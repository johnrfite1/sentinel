import {spawn, type ChildProcess} from "node:child_process";
import {createServer} from "node:net";
import {existsSync, mkdtempSync, readFileSync, rmSync} from "node:fs";
import {tmpdir} from "node:os";
import {join} from "node:path";
import {
    createPublicClient,
    createWalletClient,
    encodeFunctionData,
    http,
    keccak256,
    stringToBytes,
    toBytes,
    type Abi,
    type PublicClient,
    type WalletClient,
} from "viem";
import {privateKeyToAccount} from "viem/accounts";
import {anvil} from "viem/chains";
import {digest, domainSeparator, hashMandate, hashPolicy} from "../src/signer/eip712.ts";
import {decodeBySelector} from "../src/decode/index.ts";
import type {
    ActionPayload,
    Hex,
    MandatePayload,
    PolicyPayload,
} from "../src/signer/protocol.ts";

/**
 * Test harness for the isolated signer.
 *
 * Deliberately runs the REAL things: a real Anvil node, the real compiled SentinelVault,
 * and the signer as a real separate OS process reached over its real socket. There are no
 * fakes here, and that is the point of the file.
 *
 * A-005 says signer isolation must be "real, not nominal" — that "a same-process module
 * would satisfy the letter and make the public 'isolated signer' claim dishonest." A test
 * that imported the attestor and called it directly would be testing a same-process module
 * no matter what the production entry point does, and would therefore certify exactly the
 * thing A-005 warns against. So the END-TO-END tests spawn `src/signer/main.ts`, connect by
 * socket, and never import `keystore.ts`.
 *
 * Two suites deliberately do import in-process, and neither makes an isolation claim:
 * `attestor.concurrency.test.ts` needs a slow fake signer to widen a race window the socket
 * path cannot reliably hit, and `keystore.test.ts` exercises guards the attestor can never
 * reach. Both say so in their own headers. The distinction that matters is not "no test may
 * import" — it is that no test which certifies ISOLATION may import.
 *
 * The second thing this harness buys is a cross-language differential the signer cannot
 * fake: every receipt it produces is submitted to the compiled Solidity vault, which
 * recomputes `hashAction` and `hashReceipt` in Solidity and recovers the signature. If the
 * TypeScript EIP-712 encoding in `eip712.ts` is wrong in any field, in any padding, in any
 * ordering, the vault rejects it. That check runs on every green test, not on a fixture
 * someone remembered to regenerate.
 */

export const REPO_ROOT = join(import.meta.dirname, "..", "..");
const TS_DIR = join(REPO_ROOT, "ts");
const FOUNDRY_BIN = join(process.env.HOME ?? "", ".foundry", "bin");

/** Anvil's publicly-known dev accounts. Not secrets; see `.env.example`. */
export const OWNER_KEY: Hex = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80";
export const SIGNER_KEY: Hex = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d";
export const ATTACKER_KEY: Hex = "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a";

export const OWNER = privateKeyToAccount(OWNER_KEY);
export const SIGNER = privateKeyToAccount(SIGNER_KEY);
export const ATTACKER = privateKeyToAccount(ATTACKER_KEY);

// ---------------------------------------------------------------------------
// Compiled artifacts
// ---------------------------------------------------------------------------

interface Artifact {
    abi: Abi;
    bytecode: Hex;
}

export function artifact(sourceFile: string, contract: string): Artifact {
    const path = join(REPO_ROOT, "contracts", "out", sourceFile, `${contract}.json`);
    if (!existsSync(path)) {
        throw new Error(
            `missing Foundry artifact ${path}.\n` +
                `Run the Solidity build first — ./scripts/test.sh does this before the TS stage.`,
        );
    }
    const json = JSON.parse(readFileSync(path, "utf8")) as {
        abi: Abi;
        bytecode: {object: Hex};
    };
    return {abi: json.abi, bytecode: json.bytecode.object};
}

// ---------------------------------------------------------------------------
// Anvil
// ---------------------------------------------------------------------------

async function freePort(): Promise<number> {
    return new Promise((resolve, reject) => {
        const server = createServer();
        server.once("error", reject);
        server.listen(0, "127.0.0.1", () => {
            const address = server.address();
            if (address === null || typeof address === "string") {
                reject(new Error("could not determine a free port"));
                return;
            }
            const {port} = address;
            server.close(() => resolve(port));
        });
    });
}

export interface AnvilHandle {
    rpcUrl: string;
    stop(): void;
}

export async function startAnvil(): Promise<AnvilHandle> {
    const port = await freePort();
    // Foundry lives at $HOME/.foundry/bin and is on John's interactive PATH via .zshenv,
    // but not in an agent's or a test runner's non-interactive shell. Resolved explicitly
    // rather than assumed (session traces, "Environment facts").
    const bin = existsSync(join(FOUNDRY_BIN, "anvil")) ? join(FOUNDRY_BIN, "anvil") : "anvil";
    const child = spawn(bin, ["--port", String(port), "--silent"], {stdio: "ignore"});

    const rpcUrl = `http://127.0.0.1:${port}`;
    const client = createPublicClient({chain: anvil, transport: http(rpcUrl)});

    const deadline = Date.now() + 20_000;
    for (;;) {
        try {
            await client.getChainId();
            break;
        } catch {
            if (Date.now() > deadline) {
                child.kill("SIGKILL");
                throw new Error(`anvil did not become ready at ${rpcUrl} within 20s`);
            }
            await sleep(50);
        }
    }

    return {
        rpcUrl,
        stop() {
            child.kill("SIGKILL");
        },
    };
}

// ---------------------------------------------------------------------------
// Deployment
// ---------------------------------------------------------------------------

export interface Stack {
    rpcUrl: string;
    chainId: bigint;
    publicClient: PublicClient;
    walletClient: WalletClient;
    vault: Hex;
    demoPay: Hex;
    demoErc20: Hex;
    vaultAbi: Abi;
    demoPayAbi: Abi;
    demoErc20Abi: Abi;
    purchaseSelector: Hex;
    approveSelector: Hex;
}

export const PURCHASE_SELECTOR: Hex = "0x00000000"; // replaced at deploy time
const MAX_NATIVE_VALUE_WEI = 10n ** 16n; // 0.01 ETH — the vault's immutable hard cap

export async function deployStack(rpcUrl: string): Promise<Stack> {
    const publicClient = createPublicClient({chain: anvil, transport: http(rpcUrl)});
    const walletClient = createWalletClient({chain: anvil, account: OWNER, transport: http(rpcUrl)});
    const chainId = BigInt(await publicClient.getChainId());

    const payArtifact = artifact("DemoPay.sol", "DemoPay");
    const erc20Artifact = artifact("DemoERC20.sol", "DemoERC20");
    const vaultArtifact = artifact("SentinelVault.sol", "SentinelVault");

    const demoPay = await deploy(publicClient, walletClient, payArtifact, []);
    const demoErc20 = await deploy(publicClient, walletClient, erc20Artifact, [
        OWNER.address,
        10n ** 24n,
    ]);

    const purchaseSelector = selectorOf(payArtifact.abi, "purchase");
    const approveSelector = selectorOf(erc20Artifact.abi, "approve");

    const vault = await deploy(
        publicClient,
        walletClient,
        vaultArtifact,
        [
            OWNER.address,
            SIGNER.address,
            MAX_NATIVE_VALUE_WEI,
            [demoPay, demoErc20],
            [purchaseSelector, approveSelector],
        ],
        // Funded so the vault can actually forward native value to DemoPay. A vault with no
        // balance turns every Case 1 run into a CallFailed and hides whatever else broke.
        10n ** 18n,
    );

    return {
        rpcUrl,
        chainId,
        publicClient,
        walletClient,
        vault,
        demoPay,
        demoErc20,
        vaultAbi: vaultArtifact.abi,
        demoPayAbi: payArtifact.abi,
        demoErc20Abi: erc20Artifact.abi,
        purchaseSelector,
        approveSelector,
    };
}

async function deploy(
    publicClient: PublicClient,
    walletClient: WalletClient,
    art: Artifact,
    args: unknown[],
    value = 0n,
): Promise<Hex> {
    const hash = await walletClient.deployContract({
        abi: art.abi,
        bytecode: art.bytecode,
        args: args as never,
        account: OWNER,
        chain: anvil,
        value,
    });
    const receipt = await publicClient.waitForTransactionReceipt({hash});
    if (receipt.contractAddress === null || receipt.contractAddress === undefined) {
        throw new Error("deployment produced no contract address");
    }
    return receipt.contractAddress.toLowerCase() as Hex;
}

function selectorOf(abi: Abi, name: string): Hex {
    const entry = abi.find((e) => e.type === "function" && e.name === name);
    if (entry === undefined || entry.type !== "function") throw new Error(`no function ${name} in abi`);
    const signature = `${name}(${entry.inputs.map((i) => i.type).join(",")})`;
    return keccak256(stringToBytes(signature)).slice(0, 10) as Hex;
}

// ---------------------------------------------------------------------------
// The signer, as a separate OS process
// ---------------------------------------------------------------------------

export interface SignerHandle {
    socketPath: string;
    stop(): void;
    stderr(): string;
}

export async function startSignerProcess(options: {
    rpcUrl: string;
    vault: Hex;
    privateKey?: Hex;
}): Promise<SignerHandle> {
    const dir = mkdtempSync(join(tmpdir(), "sentinel-signer-"));
    const socketPath = join(dir, "signer.sock");

    const child: ChildProcess = spawn(process.execPath, [join(TS_DIR, "src", "signer", "main.ts")], {
        cwd: TS_DIR,
        stdio: ["ignore", "pipe", "pipe"],
        env: {
            ...process.env,
            SENTINEL_RPC_URL: options.rpcUrl,
            SENTINEL_VAULT_ADDRESS: options.vault,
            SENTINEL_SIGNER_SOCKET: socketPath,
            SENTINEL_SIGNER_KEY: options.privateKey ?? SIGNER_KEY,
        },
    });

    let stderrText = "";
    let stdoutText = "";
    child.stderr?.setEncoding("utf8");
    child.stderr?.on("data", (c: string) => (stderrText += c));
    child.stdout?.setEncoding("utf8");
    child.stdout?.on("data", (c: string) => (stdoutText += c));

    const deadline = Date.now() + 20_000;
    while (!existsSync(socketPath)) {
        if (child.exitCode !== null || Date.now() > deadline) {
            throw new Error(
                `signer process did not create ${socketPath}.\n` +
                    `exit=${child.exitCode}\nstdout:\n${stdoutText}\nstderr:\n${stderrText}`,
            );
        }
        await sleep(25);
    }

    return {
        socketPath,
        stop() {
            child.kill("SIGKILL");
            rmSync(dir, {recursive: true, force: true});
        },
        stderr() {
            return stderrText;
        },
    };
}

// ---------------------------------------------------------------------------
// Case 1 fixtures (§4.2)
// ---------------------------------------------------------------------------

export const RESOURCE_ID = keccak256(stringToBytes("weather-basic-24h"));
export const PURPOSE_KIND = keccak256(stringToBytes("data-service-purchase"));
export const DURATION_SECONDS = 86_400n;
export const PURCHASE_VALUE_WEI = 10n ** 15n; // 0.001 ETH, inside every cap
const FAR_FUTURE = 4_000_000_000n;

export interface Case1 {
    mandate: MandatePayload;
    policy: PolicyPayload;
    action: ActionPayload;
    callData: Hex;
    mandateHash: Hex;
    policyHash: Hex;
}

/**
 * The Case 1 "exact mandate — allow" scenario: one purchase of weather-basic-24h from the
 * pinned DemoPay code hash, for the owner as beneficiary, recurrence disabled, inside the
 * value ceiling.
 *
 * `overrides` exists so a negative test can perturb exactly one dimension and leave the
 * rest identical. Randomising several at once is how the invariant suite previously ended
 * up with 16,384 calls and zero executions (session traces, "Dead ends").
 */
export async function buildCase1(
    stack: Stack,
    overrides: {
        mandate?: Partial<MandatePayload>;
        policy?: Partial<PolicyPayload>;
        action?: Partial<ActionPayload>;
        callDataArgs?: {resourceId?: Hex; beneficiary?: Hex; duration?: bigint; recurring?: boolean};
    } = {},
): Promise<Case1> {
    const code = await stack.publicClient.getCode({address: stack.demoPay});
    const targetCodeHash = keccak256(toBytes(code ?? "0x"));

    const callData = encodeFunctionData({
        abi: stack.demoPayAbi,
        functionName: "purchase",
        args: [
            overrides.callDataArgs?.resourceId ?? RESOURCE_ID,
            overrides.callDataArgs?.beneficiary ?? OWNER.address,
            overrides.callDataArgs?.duration ?? DURATION_SECONDS,
            overrides.callDataArgs?.recurring ?? false,
        ],
    }) as Hex;

    const policy: PolicyPayload = {
        schemaVersion: 1n,
        policyVersion: 1n,
        vault: stack.vault,
        chainId: stack.chainId,
        allowedOperation: 0n,
        allowedTargetsHash: keccak256(stringToBytes(`${stack.demoPay},${stack.demoErc20}`)),
        allowedSelectorsHash: keccak256(
            stringToBytes(`${stack.purchaseSelector},${stack.approveSelector}`),
        ),
        maxNativeValueWei: 10n ** 16n,
        maxAllowanceIncreaseBaseUnits: 0n,
        allowedCallGraphHash: keccak256(stringToBytes("DemoPay.purchase:no-internal-calls")),
        validAfter: 0n,
        validUntil: FAR_FUTURE,
        failureMode: 0n,
        ...overrides.policy,
    };
    const policyHash = hashPolicy(policy);

    const mandate: MandatePayload = {
        schemaVersion: 1n,
        mandateId: keccak256(stringToBytes("mandate:case-1")),
        principal: OWNER.address.toLowerCase() as Hex,
        signer: SIGNER.address.toLowerCase() as Hex,
        vault: stack.vault,
        chainId: stack.chainId,
        target: stack.demoPay,
        targetCodeHash,
        selector: stack.purchaseSelector,
        maxNativeValueWei: 10n ** 16n,
        purposeKind: PURPOSE_KIND,
        resourceId: RESOURCE_ID,
        beneficiary: OWNER.address.toLowerCase() as Hex,
        durationSeconds: DURATION_SECONDS,
        recurringAllowed: false,
        validAfter: 0n,
        validUntil: FAR_FUTURE,
        policyHash,
        ...overrides.mandate,
    };
    const mandateHash = hashMandate(mandate);

    const nonce = (await stack.publicClient.readContract({
        address: stack.vault,
        abi: stack.vaultAbi,
        functionName: "actionNonce",
    })) as bigint;

    const action: ActionPayload = {
        schemaVersion: 1n,
        chainId: stack.chainId,
        vault: stack.vault,
        actionNonce: nonce,
        target: stack.demoPay,
        valueWei: PURCHASE_VALUE_WEI,
        dataHash: keccak256(toBytes(callData)),
        operation: 0n,
        mandateHash,
        policyHash,
        deadline: FAR_FUTURE,
        ...overrides.action,
    };

    return {mandate, policy, action, callData, mandateHash, policyHash};
}

/** Exhibits the full owner-signed mandate envelope after activating its linked policy. */
export async function activate(stack: Stack, mandate: MandatePayload, policyHash: Hex): Promise<void> {
    const policyTx = await stack.walletClient.writeContract({
        address: stack.vault,
        abi: stack.vaultAbi,
        functionName: "activatePolicy",
        args: [policyHash],
        account: OWNER,
        chain: anvil,
    });
    await stack.publicClient.waitForTransactionReceipt({hash: policyTx});

    const ownerSignature = await OWNER.sign({
        hash: digest(domainSeparator(stack.chainId, stack.vault), hashMandate(mandate)),
    });
    const mandateTx = await stack.walletClient.writeContract({
        address: stack.vault,
        abi: stack.vaultAbi,
        functionName: "activateMandate",
        args: [mandate, ownerSignature],
        account: OWNER,
        chain: anvil,
    });
    await stack.publicClient.waitForTransactionReceipt({hash: mandateTx});
}

/**
 * A minimal stand-in for the §5.6 evidence bundle.
 *
 * It MUST carry a `decodedSelectorAndParameters` block that matches the calldata, because
 * D-014 makes the signer decode the bytes itself and refuse a bundle whose decoding claim
 * disagrees. A stub without one is refused as `SIGNER_EVIDENCE_DECODING_ABSENT` — which is
 * the intended behaviour, since an optional attestation would be worthless.
 *
 * Derived here with the same `decodeBySelector` the signer uses, so the positive path is
 * trivially consistent. That is fine: the assertion that matters is the deliberate MISMATCH
 * test, which constructs a wrong block by hand.
 */
export function evidenceStub(note: string, callData: Hex): string {
    const decoded = decodeBySelector(callData);
    return JSON.stringify({
        note,
        schema: "sentinel.evidence.stub.v0",
        decodedSelectorAndParameters: decoded.ok
            ? {
                  decoded: "true",
                  selector: decoded.selector,
                  schema: decoded.decoded.schema,
                  parameters:
                      decoded.decoded.schema === "DemoPay.purchase"
                          ? {
                                resourceId: decoded.decoded.resourceId,
                                beneficiary: decoded.decoded.beneficiary,
                                durationSeconds: decoded.decoded.durationSeconds.toString(),
                                recurring: decoded.decoded.recurring,
                            }
                          : {
                                spender: decoded.decoded.spender,
                                amount: decoded.decoded.amount.toString(),
                            },
              }
            : {decoded: "false", selector: decoded.selector ?? "", failureCode: decoded.code},
    });
}

/**
 * Calldata the signer's own `decodeBySelector` CAN read — a well-formed DemoPay.purchase.
 *
 * A-043. Unit fixtures used to reach for an arbitrary unsupported selector (`0xdeadbeef…`,
 * `0xa1b2c3d4…`) whenever they needed "some calldata" for a test about something else — the
 * nonce guard, the reason-code table, fail-closed behaviour. That was load-bearing in a way
 * nobody intended: an undecodable selector made the signer's own decode fail, the evidence
 * stub then honestly reported `decoded:"false"`, and the signer returned NO finding for an
 * ALLOW. **Eleven tests were therefore passing through the exact hole this review found**, and
 * they went red the moment it was closed — which is the only reason the blast radius was
 * visible at all.
 *
 * `seed` varies the resourceId so callers can build distinct-but-decodable actions, which is
 * what the nonce-guard tests actually need. Prefer this over an arbitrary selector in any test
 * that is not specifically ABOUT undecodable calldata.
 */
export function decodablePurchaseCallData(seed = "fixture"): Hex {
    const w = (h: string) => h.replace(/^0x/, "").padStart(64, "0");
    return `0xc188528b${w(keccak256(stringToBytes(seed)))}${w(
        "f39fd6e51aad88f6f4ce6ab8827279cfffb92266",
    )}${w((86_400n).toString(16))}${w("0")}` as Hex;
}

export function sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
}
