import {spawn} from "node:child_process";
import {existsSync, mkdirSync, readFileSync, rmSync, writeFileSync} from "node:fs";
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
} from "viem";
import {privateKeyToAccount} from "viem/accounts";
import {anvil} from "viem/chains";
import {buildRegistry, decodeCall} from "../decode/index.ts";
import {evaluate} from "../evaluate/index.ts";
import {hashMandate, hashPolicy} from "../evaluate/hashes.ts";
import {simulateAction} from "../simulate/index.ts";
import {createChainReader} from "../signer/vault.ts";
import {connectSigner} from "../signer/client.ts";
import type {ActionPayload, Hex, MandatePayload, PolicyPayload} from "../signer/protocol.ts";

/**
 * Emit signed sample artifacts for the D-010 independent verifier.
 *
 * D-010 promotes a standalone receipt-verifier CLI into v1 for a reason that is engineering
 * rather than presentational: "an independent reimplementation is the strongest available
 * test of the spec's precision, and RFC 8785 edge cases, hash-domain separation, and
 * encoding ambiguity surface only when someone builds from the written schema."
 *
 * The verifier cannot be built against a description. It needs real artifacts — canonical
 * evidence bytes, their keccak, a receipt, and a signature over an EIP-712 digest — produced
 * by the real pipeline. This writes them.
 *
 * WHAT IS DELIBERATELY NOT WRITTEN HERE. No typehash constants, no domain separator, no
 * canonicalization rules. The verifier's author must derive all of those from §5 of the
 * proposal. Emitting them would hand over the very thing the exercise is meant to test, and
 * D-010's independence condition would be satisfied in letter while being void in substance.
 * The one exception is `domain.json`, which carries only the domain's *field values* (name,
 * version, chainId, verifyingContract) — a verifier cannot know the deployed vault address
 * or a local chain id by derivation, and withholding them would test clairvoyance rather
 * than the spec.
 *
 * Run:  npm --prefix ts run emit-samples
 */

const REPO = join(import.meta.dirname, "..", "..", "..");
const OUT = join(REPO, "fixtures", "samples");
const OWNER = privateKeyToAccount("0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80");
const SIGNER = privateKeyToAccount("0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d");

const RESOURCE = keccak256(stringToBytes("weather-basic-24h"));
const WRONG_RESOURCE = keccak256(stringToBytes("premium-monthly"));
const ATTACKER: Hex = "0x00000000000000000000000000000000deadbeef";
const DURATION = 86_400n;
const VALUE = 10n ** 15n;
const FAR_FUTURE = 4_000_000_000n;
const MAX_UINT256 = (1n << 256n) - 1n;

function artifact(file: string, contract: string): {abi: Abi; bytecode: Hex} {
    const path = join(REPO, "contracts", "out", file, `${contract}.json`);
    if (!existsSync(path)) throw new Error(`missing ${path}; run ./scripts/test.sh first`);
    const j = JSON.parse(readFileSync(path, "utf8")) as {abi: Abi; bytecode: {object: Hex}};
    return {abi: j.abi, bytecode: j.bytecode.object};
}

/** bigints render as decimal STRINGS, matching the evidence schema's own no-JSON-numbers rule. */
function j(value: unknown): string {
    return JSON.stringify(value, (_k, v) => (typeof v === "bigint" ? v.toString() : v), 2);
}

const anvilBin = join(process.env.HOME ?? "", ".foundry", "bin", "anvil");
const port = 8900 + Math.floor(Number(process.hrtime.bigint() % 90n));
const rpcUrl = `http://127.0.0.1:${port}`;
const node = spawn(existsSync(anvilBin) ? anvilBin : "anvil", ["--port", String(port), "--silent"], {
    stdio: "ignore",
});

const publicClient = createPublicClient({chain: anvil, transport: http(rpcUrl)});
const walletClient = createWalletClient({chain: anvil, account: OWNER, transport: http(rpcUrl)});

for (;;) {
    try {
        await publicClient.getChainId();
        break;
    } catch {
        await new Promise((r) => setTimeout(r, 50));
    }
}
const chainId = BigInt(await publicClient.getChainId());

async function deploy(art: {abi: Abi; bytecode: Hex}, args: unknown[], value = 0n): Promise<Hex> {
    const hash = await walletClient.deployContract({
        abi: art.abi,
        bytecode: art.bytecode,
        args: args as never,
        account: OWNER,
        chain: anvil,
        value,
    });
    return (await publicClient.waitForTransactionReceipt({hash})).contractAddress!.toLowerCase() as Hex;
}

const payArt = artifact("DemoPay.sol", "DemoPay");
const ercArt = artifact("DemoERC20.sol", "DemoERC20");
const vaultArt = artifact("SentinelVault.sol", "SentinelVault");

const demoPay = await deploy(payArt, []);
const vault = await deploy(
    vaultArt,
    [
        OWNER.address,
        SIGNER.address,
        10n ** 16n,
        [demoPay, "0x0000000000000000000000000000000000000001"],
        ["0xc188528b", "0x095ea7b3"],
    ],
    10n ** 18n,
);
const demoErc20 = await deploy(ercArt, [vault, 10n ** 24n]);
const registry = buildRegistry({[demoPay]: "DemoPay", [demoErc20]: "DemoERC20"});

const code = await publicClient.getCode({address: demoPay});

function buildPolicy(failureMode: bigint): PolicyPayload {
    return {
        schemaVersion: 1n,
        policyVersion: 1n,
        vault,
        chainId,
        allowedOperation: 0n,
        allowedTargetsHash: keccak256(stringToBytes("targets")),
        allowedSelectorsHash: keccak256(stringToBytes("selectors")),
        maxNativeValueWei: 10n ** 16n,
        maxAllowanceIncreaseBaseUnits: 0n,
        allowedCallGraphHash: keccak256(stringToBytes("DemoPay.purchase:no-internal-calls")),
        validAfter: 0n,
        validUntil: FAR_FUTURE,
        failureMode,
    };
}

function buildMandate(policy: PolicyPayload, overrides: Partial<MandatePayload> = {}): MandatePayload {
    return {
        schemaVersion: 1n,
        mandateId: keccak256(stringToBytes("mandate:samples")),
        principal: OWNER.address.toLowerCase() as Hex,
        vault,
        chainId,
        target: demoPay,
        targetCodeHash: keccak256(toBytes(code ?? "0x")),
        selector: "0xc188528b",
        maxNativeValueWei: 10n ** 16n,
        purposeKind: keccak256(stringToBytes("data-service-purchase")),
        resourceId: RESOURCE,
        beneficiary: OWNER.address.toLowerCase() as Hex,
        durationSeconds: DURATION,
        recurringAllowed: false,
        validAfter: 0n,
        validUntil: FAR_FUTURE,
        policyHash: hashPolicy(policy),
        ...overrides,
    };
}

async function activate(mandate: MandatePayload, policy: PolicyPayload): Promise<void> {
    for (const [fn, arg] of [
        ["activateMandate", hashMandate(mandate)],
        ["activatePolicy", hashPolicy(policy)],
    ] as const) {
        const h = await walletClient.writeContract({
            address: vault,
            abi: vaultArt.abi,
            functionName: fn,
            args: [arg],
            account: OWNER,
            chain: anvil,
        });
        await publicClient.waitForTransactionReceipt({hash: h});
    }
}

const socketPath = join(REPO, ".sentinel", `emit-${port}.sock`);
const signerProc = spawn(process.execPath, [join(REPO, "ts", "src", "signer", "main.ts")], {
    cwd: join(REPO, "ts"),
    stdio: ["ignore", "ignore", "ignore"],
    env: {
        ...process.env,
        SENTINEL_RPC_URL: rpcUrl,
        SENTINEL_VAULT_ADDRESS: vault,
        SENTINEL_SIGNER_SOCKET: socketPath,
        SENTINEL_SIGNER_KEY: "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
    },
});
for (let i = 0; i < 200 && !existsSync(socketPath); i++) await new Promise((r) => setTimeout(r, 25));
const signerClient = await connectSigner(socketPath);

interface SampleSpec {
    id: string;
    title: string;
    note: string;
    target: Hex;
    callData: Hex;
    valueWei: bigint;
    failureMode: bigint;
    mandateOverrides?: Partial<MandatePayload>;
}

function purchaseCalldata(resource: Hex, duration = DURATION, recurring = false): Hex {
    return encodeFunctionData({
        abi: payArt.abi,
        functionName: "purchase",
        args: [resource, OWNER.address, duration, recurring],
    }) as Hex;
}

const SAMPLES: SampleSpec[] = [
    {
        id: "case-1-allow",
        title: "§4.2 Case 1 — exact mandate, allow",
        note: "The conforming purchase. Every required check passes; the receipt is executable.",
        target: demoPay,
        callData: purchaseCalldata(RESOURCE),
        valueWei: VALUE,
        failureMode: 1n,
    },
    {
        id: "case-2-injection-block",
        title: "§4.2 Case 2 — real prompt injection, block",
        note: "The approval the recorded injection produced: attacker as spender, max uint256.",
        target: demoErc20,
        callData: encodeFunctionData({
            abi: ercArt.abi,
            functionName: "approve",
            args: [ATTACKER, MAX_UINT256],
        }) as Hex,
        valueWei: 0n,
        failureMode: 1n,
    },
    {
        id: "case-3-wrong-purpose-block",
        title: "§4.2 Case 3 — mechanically valid, wrong purpose",
        note: "Passes every representative-baseline check; fails only mandate conformance.",
        target: demoPay,
        callData: purchaseCalldata(WRONG_RESOURCE),
        valueWei: VALUE,
        failureMode: 1n,
    },
    {
        id: "case-4-review-failmode-review",
        title: "§4.2 Case 4 — evidence uncertainty, failureMode = REVIEW",
        note: "Target code hash does not match the mandate's pin. Unresolved, not violated.",
        target: demoPay,
        callData: purchaseCalldata(RESOURCE),
        valueWei: VALUE,
        failureMode: 1n,
        mandateOverrides: {targetCodeHash: keccak256(stringToBytes("a different code hash"))},
    },
    {
        // D-015(b): both failureMode settings must appear in the demo, not only in the tests,
        // because Case 4's outcome turns on a policy setting and a reviewer will reasonably
        // suspect the setting was chosen to produce the wanted result. Showing the identical
        // evidence under both is what answers that.
        id: "case-4-blocked-failmode-failclosed",
        title: "§4.2 Case 4 — identical evidence, failureMode = FAIL_CLOSED",
        note: "The same code-hash uncertainty under the other legitimate policy setting.",
        target: demoPay,
        callData: purchaseCalldata(RESOURCE),
        valueWei: VALUE,
        failureMode: 0n,
        mandateOverrides: {targetCodeHash: keccak256(stringToBytes("a different code hash"))},
    },
];

rmSync(OUT, {recursive: true, force: true});
mkdirSync(OUT, {recursive: true});

const index: unknown[] = [];

for (const spec of SAMPLES) {
    const policy = buildPolicy(spec.failureMode);
    const mandate = buildMandate(policy, spec.mandateOverrides);
    await activate(mandate, policy);

    const reader = createChainReader(rpcUrl);
    const selector = spec.callData.slice(0, 10) as Hex;
    const vaultState = await reader.readVaultState(vault, spec.target, selector);

    const action: ActionPayload = {
        schemaVersion: 1n,
        chainId,
        vault,
        actionNonce: vaultState.actionNonce,
        target: spec.target,
        valueWei: spec.valueWei,
        dataHash: keccak256(toBytes(spec.callData)),
        operation: 0n,
        mandateHash: vaultState.activeMandateHash,
        policyHash: vaultState.activePolicyHash,
        deadline: FAR_FUTURE,
    };

    const decode = decodeCall({target: spec.target, callData: spec.callData, registry});
    const simulation = await simulateAction({
        client: publicClient,
        vault,
        target: spec.target,
        valueWei: spec.valueWei,
        callData: spec.callData,
        decoded: decode.ok ? decode.decoded : null,
    });
    const evaluation = evaluate({
        mandate,
        policy,
        action,
        callData: spec.callData,
        decode,
        simulation,
        vaultState,
        now: BigInt(Math.floor(Date.now() / 1000)),
    });

    const signed = await signerClient.evaluateAndSign({
        action,
        callData: spec.callData,
        mandate,
        policy,
        evaluation: {
            verdict: evaluation.verdict,
            reasonCodes: evaluation.reasonCodes,
            evidenceCanonical: evaluation.evidenceCanonical,
            simulationBlockNumber: simulation.anchor.blockNumber,
            simulationBlockHash: simulation.anchor.blockHash,
        },
    });

    const dir = join(OUT, spec.id);
    mkdirSync(dir, {recursive: true});

    writeFileSync(join(dir, "mandate.json"), j(mandate));
    writeFileSync(join(dir, "policy.json"), j(policy));
    writeFileSync(join(dir, "action.json"), j({...action, callData: spec.callData}));
    writeFileSync(join(dir, "evidence.json"), j(evaluation.bundle));
    // The exact bytes whose keccak256 the receipt commits to. No trailing newline: a byte
    // added here is a different hash, and the verifier must reproduce these bytes exactly.
    writeFileSync(join(dir, "evidence.canonical.json"), evaluation.evidenceCanonical);
    writeFileSync(join(dir, "evidence.hash"), evaluation.evidenceHash);

    const receiptOut = signed.refused
        ? signed
        : {
              refused: false,
              receipt: signed.receipt,
              signature: signed.signature,
              // The exact ordered set `reasonCodesHash` commits to — the evaluator's codes
              // UNIONED with the signer's own findings. Omitting it was a fixture bug that
              // cost the D-010 verifier a BLOCKER finding: it correctly guessed the encoding
              // and could not match, because it was hashing the evaluator's codes alone
              // while the receipt commits to the union. Without this field a receipt's
              // reason codes are genuinely unverifiable by a third party.
              reasonCodes: signed.reasonCodes,
              signerFindings: signed.signerFindings,
          };
    writeFileSync(join(dir, "receipt.json"), j(receiptOut));

    writeFileSync(
        join(dir, "meta.json"),
        j({
            id: spec.id,
            title: spec.title,
            note: spec.note,
            verdict: evaluation.verdict,
            reasonCodes: evaluation.reasonCodes,
            failureMode: spec.failureMode === 1n ? "REVIEW" : "FAIL_CLOSED",
            signerRefused: signed.refused,
        }),
    );

    index.push({
        id: spec.id,
        title: spec.title,
        verdict: evaluation.verdict,
        signerRefused: signed.refused,
    });

    console.log(
        `${spec.id.padEnd(38)} ${String(evaluation.verdict).padEnd(7)} ` +
            `refused=${String(signed.refused).padEnd(5)} codes=${evaluation.reasonCodes.join(",") || "-"}`,
    );
}

writeFileSync(
    join(OUT, "domain.json"),
    j({
        note:
            "EIP-712 domain FIELD VALUES only. The domain type string, its typehash, and the " +
            "separator construction are §5's to derive — deriving them is the point of D-010.",
        name: "Sentinel",
        version: "0.2",
        chainId,
        verifyingContract: vault,
        signerAddress: SIGNER.address,
    }),
);
writeFileSync(join(OUT, "index.json"), j(index));

console.log(`\nwrote ${SAMPLES.length} samples to ./fixtures/samples`);

await signerClient.close().catch(() => {});
signerProc.kill("SIGTERM");
node.kill("SIGTERM");
process.exit(0);
