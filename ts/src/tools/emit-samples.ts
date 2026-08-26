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
import type {
    ActionPayload,
    Hex,
    MandatePayload,
    OverrideAuthorizationPayload,
    PolicyPayload,
} from "../signer/protocol.ts";
import {digest, domainSeparator, hashOverride, hashReceipt} from "../signer/eip712.ts";
import {signerSocketPath} from "../signer/socket-path.ts";

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

/** D-043 — owner pause/unpause, so a sample can be emitted against a paused vault. */
async function setPaused(next: boolean): Promise<void> {
    const h = await walletClient.writeContract({
        address: vault,
        abi: vaultArt.abi,
        functionName: "setPaused",
        args: [next],
        account: OWNER,
        chain: anvil,
    });
    await publicClient.waitForTransactionReceipt({hash: h});
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

const socketPath = signerSocketPath(REPO, `emit-${port}`, process.env.SENTINEL_EMIT_SOCKET_DIR);
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
    /**
     * Assert the signed receipt commits to exactly this many reason codes, or fail the run.
     *
     * Only set where the COUNT is the point of the sample. It is not an expected verdict and
     * not a hint: the verdict is whatever the engine produces, and no sample carries one.
     * This exists because an edge pinned by a fixture that stops exercising it is not pinned
     * at all — the single-code sample below would quietly become a two-code sample the first
     * time an unrelated signer finding started firing on it, and nothing would say so.
     */
    expectReasonCodeCount?: number;

    /**
     * Pause the vault around this sample so the signer REFUSES to attest.
     *
     * D-043. §5.5.1 publishes `RefusalRecord`, and until this sample existed no artifact in
     * the repository carried one — every `receipt.json` had `refused: false`. So the D-010
     * verifier had nothing real to check its refusal implementation against, and "the signer
     * refused" was a path the fixtures could not demonstrate.
     *
     * `SIGNER_VAULT_PAUSED` is an EXECUTABILITY finding, which refuses both ALLOW and REVIEW.
     * That is the honest trigger to pick: the action itself is perfectly conforming and the
     * refusal is about the vault's state, so the sample demonstrates a refusal WITHOUT also
     * being a bad action — which would confound the two things a reader is trying to tell
     * apart.
     */
    pauseVault?: boolean;
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
        // suspect the setting was chosen to produce the wanted result. Showing the same
        // unresolved condition under both is what answers that. The two bundles are not
        // byte-identical: the policy differs, so hashes and the anchor block move.
        id: "case-4-blocked-failmode-failclosed",
        title: "§4.2 Case 4 — same unresolved condition, failureMode = FAIL_CLOSED",
        note: "The same code-hash uncertainty — same pin, same observed hash — under the other legitimate policy setting. The two bundles are not byte-identical: the policy differs, so the policyHash, mandateHash, actionHash, evidence and anchor block all differ. That the mandate hash moves when only the policy moved is the transitive binding working.",
        target: demoPay,
        callData: purchaseCalldata(RESOURCE),
        valueWei: VALUE,
        failureMode: 0n,
        mandateOverrides: {targetCodeHash: keccak256(stringToBytes("a different code hash"))},
    },
    {
        /**
         * A-027, the owed fixture. Nothing in the corpus pinned the SINGLE-element case of
         * `reasonCodesHash`.
         *
         * §5.4 defines the preimage as the codes joined by a delimiter, with no trailing
         * one. Every shipped sample had either zero codes or two or more, so a producer that
         * emitted `code + "\n"` for a one-element set — the single most natural way to write
         * the loop wrong — hashed identically to a correct implementation on every artifact
         * a third-party verifier could obtain. The bug would be undetectable until the day a
         * real receipt carried one code.
         *
         * The scenario is Case 3's wrong-resource purchase, which fails exactly one
         * evaluator check, under its OWN mandate id. The distinct mandate is not decoration:
         * the signer's per-nonce reservation is keyed by the vault's active mandate and
         * policy, so a sample reusing Case 1's mandate picks up
         * `SIGNER_NONCE_ALREADY_ATTESTED` as a second code and stops being a single-code
         * sample — which is exactly what happened to `case-3-wrong-purpose-block` and is why
         * the gap existed.
         */
        id: "edge-single-reason-code",
        title: "§5.4 edge — a receipt committing to exactly one reason code",
        note:
            "Pins the no-trailing-delimiter edge in reasonCodesHash (A-027). A producer " +
            "appending the delimiter after a one-element set hashes identically to a correct " +
            "one on every other sample in this directory.",
        target: demoPay,
        callData: purchaseCalldata(WRONG_RESOURCE),
        valueWei: VALUE,
        failureMode: 1n,
        mandateOverrides: {mandateId: keccak256(stringToBytes("mandate:single-reason-code-edge"))},
        expectReasonCodeCount: 1,
    },
    {
        /**
         * D-043 — the first artifact in this repository carrying a §5.5.1 RefusalRecord.
         *
         * The action is CONFORMING. What makes the signer refuse is the vault's state, not
         * the request, so this sample isolates "the signer declined to attest" from "the
         * action was bad" — two things every other sample would conflate.
         */
        id: "refusal-vault-paused",
        title: "D-012/§5.5.1 — the signer refuses; vault paused",
        note:
            "A conforming purchase submitted while the vault is paused. SIGNER_VAULT_PAUSED " +
            "is EXECUTABILITY, so the signer refuses to attest and emits a signed refusal " +
            "record instead of a receipt. The only sample whose receipt.json has " +
            "refused: true, and the only artifact a third party can use to check that a " +
            "refusal is authentic and attributable rather than merely asserted.",
        target: demoPay,
        callData: purchaseCalldata(RESOURCE),
        valueWei: VALUE,
        failureMode: 1n,
        pauseVault: true,
    },
];

/**
 * Emit a SUBSET, leaving every other sample directory untouched.
 *
 * D-043. Adding the refusal sample must not rewrite the six that already exist: their
 * evidence embeds a simulation anchor, so a regeneration on a fresh Anvil produces different
 * block hashes and therefore different receipts — churn indistinguishable, in a diff, from a
 * real change to what the samples attest. The D-010 verifier's fixtures are those files.
 *
 *   SENTINEL_SAMPLES_ONLY=refusal-vault-paused npm --prefix ts run emit-samples
 *
 * Unset, every sample is emitted, which is still the right thing after a schema change.
 */
const ONLY = (process.env.SENTINEL_SAMPLES_ONLY ?? "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
const SELECTED = ONLY.length ? SAMPLES.filter((s) => ONLY.includes(s.id)) : SAMPLES;

if (ONLY.length && SELECTED.length !== ONLY.length) {
    const missing = ONLY.filter((id) => !SAMPLES.some((s) => s.id === id));
    throw new Error(`SENTINEL_SAMPLES_ONLY names unknown sample(s): ${missing.join(", ")}`);
}

// WIPE ONLY ON A FULL EMIT. The wipe exists so a removed sample cannot linger as a stale
// directory nobody regenerates — correct when every sample is being rewritten, and destructive
// when one is. D-043's first subset run deleted the other six sample directories and wrote one;
// they were committed, so `git checkout` restored them, and the working tree was the only thing
// at risk. THE SUBSET PATH MUST NOT TOUCH WHAT IT IS NOT REGENERATING.
if (SELECTED.length === SAMPLES.length) {
    rmSync(OUT, {recursive: true, force: true});
}
mkdirSync(OUT, {recursive: true});

const index: unknown[] = [];


for (const spec of SELECTED) {
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

    // D-043 — pause BETWEEN evaluation and attestation, and the ordering is the whole point.
    //
    // A first attempt paused before evaluating, and the sample's own guard caught it: the
    // EVALUATOR then returns BLOCK (EVAL_VAULT_NOT_PAUSED fails), the signer is asked to
    // attest a BLOCK, and attesting a block is perfectly legitimate — so no refusal was
    // produced. EXECUTABILITY refuses ALLOW and REVIEW, not BLOCK.
    //
    // Pausing here instead models the real situation the signer's independent recomputation
    // exists for (§3.1, A-005): the evaluator saw a conforming action against an unpaused
    // vault, the vault's state CHANGED underneath it, and the signer — which reads chain
    // state itself rather than trusting the request — refuses to attest an ALLOW that is no
    // longer executable. That is a better demonstration than a paused-throughout sample
    // would have been, and it was arrived at by the guard rejecting the easy version.
    if (spec.pauseVault) await setPaused(true);

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

    // Checked against the SIGNED set — the union the receipt actually commits to — not the
    // evaluator's codes, because the union is what `reasonCodesHash` is computed over and
    // therefore the only count that pins anything.
    if (spec.expectReasonCodeCount !== undefined) {
        const committed = signed.refused ? [] : signed.reasonCodes;
        if (committed.length !== spec.expectReasonCodeCount) {
            throw new Error(
                `${spec.id} was written to commit to exactly ${spec.expectReasonCodeCount} reason ` +
                    `code(s) and commits to ${committed.length}: [${committed.join(", ")}]. The ` +
                    `edge this sample exists to pin is no longer pinned — fix the sample, not ` +
                    `the assertion.`,
            );
        }
    }

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

    // §5.5 — the owner's exact-action override, emitted for any REVIEW receipt.
    //
    // D-023(b). Before this, OverrideAuthorizationPayload was the one §5 payload nothing had
    // ever verified: no sample exercised it, so the D-010 verifier could neither recover its
    // type string nor test its binding, and its observation that the override carries neither
    // `chainId` nor `vault` stayed a reasoned concern rather than a measurement.
    //
    // NOTE WHO SIGNS THIS. The OWNER, not the Sentinel signer. §3.3(7) requires a credential
    // the isolated signer cannot mint, and it cannot — the keystore signs receipts and
    // nothing else. A sample in which the signer produced this would misrepresent the
    // security property the override exists to carry.
    if (!signed.refused && evaluation.verdict === "REVIEW") {
        const auth: OverrideAuthorizationPayload = {
            schemaVersion: 1n,
            reviewReceiptHash: hashReceipt(signed.receipt),
            actionHash: signed.actionHash,
            mandateHash: action.mandateHash,
            policyHash: action.policyHash,
            actionNonce: action.actionNonce,
            reasonHash: keccak256(stringToBytes("owner accepts the code-identity risk")),
            issuedAt: 0n,
            expiresAt: FAR_FUTURE,
        };
        const ownerSignature = await OWNER.sign({
            hash: digest(domainSeparator(chainId, vault), hashOverride(auth)),
        });
        writeFileSync(
            join(dir, "override.json"),
            j({
                note:
                    "§5.5 OverrideAuthorizationPayload, signed by the OWNER (not the Sentinel " +
                    "signer). Verifies against the same EIP-712 domain as the receipt; its " +
                    "chain and vault binding is transitive, through the mandateHash and " +
                    "policyHash it references.",
                override: auth,
                ownerSignature,
                ownerAddress: OWNER.address,
            }),
        );
    }

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

    // Leave the chain as we found it, so sample order cannot change sample content.
    if (spec.pauseVault) await setPaused(false);

    // A sample that exists to carry a refusal and does not carry one is worse than no
    // sample: it would sit in the directory looking like coverage. Fail the run instead.
    if (spec.pauseVault && !signed.refused) {
        throw new Error(
            `${spec.id} was written to demonstrate a signer REFUSAL and the signer attested ` +
                `instead. Either the refusal trigger has moved or the vault was not paused at ` +
                `attestation time — fix the sample, not the assertion.`,
        );
    }
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
// On a subset run, MERGE into the existing index rather than replacing it — otherwise the
// index would claim the repository holds one sample when it holds seven. Entries are keyed by
// id, so a re-emitted sample updates in place and ordering follows SAMPLES.
const indexPath = join(OUT, "index.json");
let merged = index;
if (SELECTED.length !== SAMPLES.length && existsSync(indexPath)) {
    const prior = JSON.parse(readFileSync(indexPath, "utf8")) as {id: string}[];
    const fresh = new Map(index.map((e) => [(e as {id: string}).id, e]));
    const kept = prior.filter((e) => !fresh.has(e.id));
    const order = new Map(SAMPLES.map((s, i) => [s.id, i]));
    merged = [...kept, ...index].sort(
        (a, b) =>
            (order.get((a as {id: string}).id) ?? 0) - (order.get((b as {id: string}).id) ?? 0),
    );
}
writeFileSync(indexPath, j(merged));

console.log(
    `\nwrote ${SELECTED.length} of ${SAMPLES.length} sample(s) to ./fixtures/samples` +
        (SELECTED.length === SAMPLES.length ? "" : ` (subset: ${SELECTED.map((s) => s.id).join(", ")})`),
);

await signerClient.close().catch(() => {});
signerProc.kill("SIGTERM");
node.kill("SIGTERM");
process.exit(0);
