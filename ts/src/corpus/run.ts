import {createHash} from "node:crypto";
import {spawn} from "node:child_process";
import {existsSync, mkdirSync, mkdtempSync, readFileSync, renameSync, rmSync, writeFileSync} from "node:fs";
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
} from "viem";
import {privateKeyToAccount} from "viem/accounts";
import {anvil} from "viem/chains";
import {buildRegistry, decodeCall} from "../decode/index.ts";
import {simulateAction, type SimulationResult} from "../simulate/index.ts";
import {hashMandate, hashPolicy} from "../evaluate/hashes.ts";
import {createChainReader} from "../signer/vault.ts";
import {signerSocketPath} from "../signer/socket-path.ts";
import {connectSigner} from "../signer/client.ts";
import {evaluate} from "../evaluate/index.ts";
import type {ActionPayload, Hex, MandatePayload, PolicyPayload} from "../signer/protocol.ts";
import {LAYERS, runLayer, type LayerResult} from "../ablation/layers.ts";
import type {BaselineConfig} from "../ablation/baseline.ts";
import {transcribe} from "../propose/index.ts";
import type {AgentProposal} from "../propose/schema.ts";
import {CORPUS, ATTACKER, RESOURCE, WRONG_RESOURCE, CONFORMING_VALUE, MANDATE_CEILING} from "./fixtures.ts";
import type {FixtureSpec} from "./spec.ts";
import {assertNoLeakage, assertViewShape} from "./leakage.ts";
import {verifyRationaleFixture} from "./rationale.ts";

/**
 * Execute the §7.1 corpus against a real chain and emit two separate views.
 *
 * `fixtures/corpus/for-labelling/` — what the independent labellers see. Concrete payload
 * values and the declared intent. **No verdict, no check result, no reason code, no layer
 * output.** D-011(b): "the labeler receives payload schemas, security invariants, and each
 * fixture's declared intent — never evaluator source, never evaluator output." The split is
 * enforced by construction here rather than by asking the labeller not to peek, and
 * `assertNoLeakage` fails the run if an evaluator-shaped key ever reaches that directory.
 *
 * `fixtures/corpus/results/` — the layer results for the §7.3 ablation. Written to a
 * different directory precisely so it can be handed to the ablation without ever being
 * handed to a labeller.
 *
 * ISOLATION. Each fixture runs inside its own `evm_snapshot`/`evm_revert` pair. Several
 * scenarios are sticky — pausing the vault, rotating the signer, advancing time, consuming a
 * nonce — and without isolation fixture N would silently condition fixture N+1. That is the
 * corpus equivalent of the simulation-leak defect A-019 records, and it is the kind of thing
 * that produces a plausible, entirely wrong results table.
 *
 * Run:  npm --prefix ts run corpus
 */

const REPO = join(import.meta.dirname, "..", "..", "..");

/**
 * Where the run writes. Overridable so the GATE can execute this file without touching the
 * committed artifacts.
 *
 * `scripts/test.sh` never ran the corpus, which is why `run.ts` was covered by nothing and why
 * six mutations against its wiring survived a green suite. Wiring it in naively would have the
 * gate rewrite 32 view files on every invocation — a gate that dirties the tree is a gate
 * people stop running, and it would break the mutation harness's clean-tree requirement.
 *
 * So the gate runs the corpus to a temporary directory and compares `_digests.json` against
 * the committed one. That covers this file end to end, leaves the tree clean, AND turns the
 * A-029 provenance claim into something the gate checks: the committed views are still the
 * semantic output of the current code.
 */
const OUT = process.env.SENTINEL_CORPUS_OUT ?? join(REPO, "fixtures", "corpus");
const OWNER = privateKeyToAccount("0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80");
const SIGNER = privateKeyToAccount("0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d");
const OTHER_SIGNER = privateKeyToAccount("0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a");

const DAY = 86_400n;
const FAR_FUTURE = 4_000_000_000n;
const MAX_UINT256 = (1n << 256n) - 1n;
const UNKNOWN_TARGET: Hex = "0x000000000000000000000000000000000000beef";

function artifact(file: string, contract: string): {abi: Abi; bytecode: Hex} {
    const path = join(REPO, "contracts", "out", file, `${contract}.json`);
    if (!existsSync(path)) throw new Error(`missing ${path}; run ./scripts/test.sh first`);
    const j = JSON.parse(readFileSync(path, "utf8")) as {abi: Abi; bytecode: {object: Hex}};
    return {abi: j.abi, bytecode: j.bytecode.object};
}

function j(value: unknown): string {
    return JSON.stringify(value, (_k, v) => (typeof v === "bigint" ? v.toString() : v), 2);
}

/**
 * A digest of a labeller view with the RUN-VARYING fields normalised out (A-029).
 *
 * THE PROBLEM THIS SOLVES, AND THE ONE IT DELIBERATELY DOES NOT. Re-running the corpus
 * rewrites 32 of 50 view files with no source change, because entitlement expiry is derived
 * from the simulated block's timestamp and Anvil starts at the wall clock. So "the labellers
 * were given these files" is supported by commit history and cannot be re-derived by anyone
 * re-running the pipeline — which is a weak footing for the only evidence bearing on whether
 * the verdicts are right.
 *
 * The tempting fix is to pin chain time. It was not taken. Anvil's later blocks follow the
 * real clock whatever the genesis is, so pinning gets *nearly* deterministic rather than
 * deterministic; and forcing every block's timestamp risks the failure this file already
 * records, where passing `Date.now()` instead of chain time silently made three time-window
 * fixtures vacuous. A fix that quietly neuters a time fixture is worse than a documented
 * irreproducibility.
 *
 * So the irreproducibility is BOUNDED instead. The digest covers the whole view except the
 * timestamps that cannot help but move, and `_digests.json` is committed. A re-run that
 * changes nothing semantic produces an EMPTY git diff on that file; a re-run that changes a
 * value a labeller reasons about does not. The provenance claim becomes "these views are
 * semantically the ones that were labelled", which is checkable, rather than "these are the
 * bytes", which is not.
 *
 * The normalised fields are listed here rather than pattern-matched, so adding one is a
 * deliberate act — the same reason `ALLOWED_VIEW_KEYS` is a list.
 */
const RUN_VARYING_FIELDS = ["expiryBefore", "expiryAfter"] as const;

function normalisedDigest(view: unknown): string {
    const canonical = JSON.stringify(view, (key, value) => {
        if ((RUN_VARYING_FIELDS as readonly string[]).includes(key)) return "<run-varying>";
        return typeof value === "bigint" ? value.toString() : value;
    });
    return createHash("sha256").update(canonical).digest("hex").slice(0, 32);
}

const anvilBin = join(process.env.HOME ?? "", ".foundry", "bin", "anvil");
const port = 9100 + Math.floor(Number(process.hrtime.bigint() % 90n));
const rpcUrl = `http://127.0.0.1:${port}`;
const node = spawn(existsSync(anvilBin) ? anvilBin : "anvil", ["--port", String(port), "--silent"], {
    stdio: "ignore",
});

const publicClient: PublicClient = createPublicClient({chain: anvil, transport: http(rpcUrl)});
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
        MANDATE_CEILING,
        [demoPay, "0x0000000000000000000000000000000000000001"],
        ["0xc188528b", "0x095ea7b3"],
    ],
    10n ** 18n,
);
const demoErc20 = await deploy(ercArt, [vault, 10n ** 24n]);
const registry = buildRegistry({[demoPay]: "DemoPay", [demoErc20]: "DemoERC20"});
const baseCode = await publicClient.getCode({address: demoPay});

/** §7.2's representative baseline, configured once. Allowlists BOTH demo targets, per §7.2. */
const baselineConfig: BaselineConfig = {
    chainId,
    vault,
    allowedTargets: [demoPay, demoErc20],
    allowedSelectors: ["0xc188528b", "0x095ea7b3"],
    maxNativeValueWei: MANDATE_CEILING,
    blockUnlimitedApproval: true,
};

// THE SOCKET PATH IS BOUNDED BY THE OS, NOT BY US (A-066).
//
// A unix socket path must fit macOS's 104-byte `sun_path`, and `REPO/.sentinel/corpus-N.sock`
// does not when REPO is a review worktree: 129 bytes from the paths this project actually uses,
// so `npm run corpus` — and therefore `./scripts/test.sh --gate` — aborted with `connect
// EINVAL` before evaluating a single fixture. **Round five discovered this the expensive way:
// all eight of its reviewers ran the FAST profile, none of them knew it, and one measured it
// only after its own findings were written** (A-058, D-12).
//
// That is now more than an inconvenience. D-050(1) ratified A-060, which requires at least one
// reviewer per round to be able to run the DEEP profile — so without this, round six cannot
// satisfy its own definition of breadth.
//
// The fallback triggers on LENGTH rather than on being-in-a-worktree, because the thing that
// breaks is the byte count and nothing else. In the live tree the path is short and unchanged,
// so the default behaviour and the committed evidence are untouched.
//
// THE FALLBACK GETS ITS OWN PRIVATE DIRECTORY, and the first version of this fix did not — it
// put the socket directly in `tmpdir()` and died with `EPERM: chmod '/var/folders/.../T'`.
// `startSignerServer` deliberately chmods the socket's PARENT to 0700, because unix-socket
// permissions are checked at connect time and a 0700 parent closes that window however the
// socket was created (itself an adversarial-review finding). Pointing the signer at a shared
// system directory asks it to lock down a directory it does not own. `mkdtempSync` gives it a
// fresh private one, so the hardening still applies to a directory that is ours.
// MOVED TO A SHARED HELPER 2026-08-18 (D-052(b), round six L7-3). The logic above was correct
// and lived HERE ONLY, while `tools/sample-check.ts` and `tools/emit-samples.ts` carried the
// identical raw construction and still died `connect EINVAL` from a worktree. One
// implementation, three callers — see `../signer/socket-path.ts` for the reasoning that used
// to sit in this comment.
const socketPath = signerSocketPath(REPO, `corpus-${port}`,
                                    process.env.SENTINEL_CORPUS_SOCKET_DIR);
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

/** The baseline conforming mandate/policy, used only by `executeConforming`. */
const conformingPolicy: PolicyPayload = {
    schemaVersion: 1n,
    policyVersion: 1n,
    vault,
    chainId,
    allowedOperation: 0n,
    allowedTargetsHash: keccak256(stringToBytes("targets")),
    allowedSelectorsHash: keccak256(stringToBytes("selectors")),
    maxNativeValueWei: MANDATE_CEILING,
    maxAllowanceIncreaseBaseUnits: 0n,
    allowedCallGraphHash: keccak256(stringToBytes("DemoPay.purchase:no-internal-calls")),
    validAfter: 0n,
    validUntil: FAR_FUTURE,
    failureMode: 1n,
};
const conformingMandate: MandatePayload = {
    schemaVersion: 1n,
    mandateId: keccak256(stringToBytes("mandate:corpus-nonce-consumer")),
    principal: OWNER.address.toLowerCase() as Hex,
    vault,
    chainId,
    target: demoPay,
    targetCodeHash: keccak256(toBytes(baseCode ?? "0x")),
    selector: "0xc188528b",
    maxNativeValueWei: MANDATE_CEILING,
    purposeKind: keccak256(stringToBytes("data-service-purchase")),
    resourceId: RESOURCE,
    beneficiary: OWNER.address.toLowerCase() as Hex,
    durationSeconds: DAY,
    recurringAllowed: false,
    validAfter: 0n,
    validUntil: 3_000_000_000n,
    policyHash: hashPolicy(conformingPolicy),
};

async function rpc(method: string, params: unknown[]): Promise<unknown> {
    const res = await fetch(rpcUrl, {
        method: "POST",
        headers: {"content-type": "application/json"},
        body: JSON.stringify({jsonrpc: "2.0", id: 1, method, params}),
    });
    return ((await res.json()) as {result?: unknown}).result;
}

function targetAddress(name: FixtureSpec["target"]): Hex {
    return name === "demoPay" ? demoPay : name === "demoErc20" ? demoErc20 : UNKNOWN_TARGET;
}

function buildCallData(spec: FixtureSpec): Hex {
    const c = spec.call;
    if (c.kind === "raw") return c.hex;
    if (c.kind === "approve") {
        return encodeFunctionData({
            abi: ercArt.abi,
            functionName: "approve",
            args: [c.spender === "attacker" ? ATTACKER : c.spender, c.amount === "max" ? MAX_UINT256 : c.amount],
        }) as Hex;
    }
    const resource = c.resource === "wrong" ? WRONG_RESOURCE : (c.resource ?? RESOURCE);
    const beneficiary =
        c.beneficiary === "attacker" ? ATTACKER : (c.beneficiary ?? (OWNER.address.toLowerCase() as Hex));
    return encodeFunctionData({
        abi: payArt.abi,
        functionName: "purchase",
        args: [resource, beneficiary, c.durationSeconds ?? DAY, c.recurring ?? false],
    }) as Hex;
}

/**
 * Rebuild a rationale-carrying fixture as the agent proposal it claims to be (A-028 F-5).
 *
 * The `malicious-retrieved-instructions` class describes something an AGENT did — it read a
 * poisoned document and proposed a call with a story attached. A fixture that only ever exists
 * as calldata this file encoded is not that scenario, which is why the class was vacuous.
 *
 * So the fixture is driven through `propose/`, the untrusted seam a live proposal takes, and
 * the runner then requires the transcriber's bytes to equal the ones built here. That equality
 * is the load-bearing part: it says the narrative changed nothing about the call, measured
 * against an encoder that had the narrative in hand, rather than asserted because no data path
 * existed. If the two ever disagree the corpus run fails, because then this fixture and the
 * scenario it names would have come apart.
 */
function proposalFor(spec: FixtureSpec, target: Hex, valueWei: bigint): AgentProposal {
    const rationale = spec.agentRationale!;
    const c = spec.call;

    if (c.kind === "raw") {
        // Reachable only by editing a fixture, and a loud stop is the right answer: raw
        // calldata is authored precisely for the classes a transcriber cannot emit (the
        // step-7 coverage boundary says so), so a raw fixture claiming an agent rationale is
        // a scenario contradicting itself.
        throw new Error(
            `${spec.id} declares an agentRationale but authors raw calldata. Raw fixtures exist ` +
                `for shapes no proposal can produce, so the two cannot both be true.`,
        );
    }

    if (c.kind === "approve") {
        return {
            target,
            value_wei: valueWei.toString(),
            function_signature: "approve(address,uint256)",
            args: [
                c.spender === "attacker" ? ATTACKER : c.spender,
                (c.amount === "max" ? MAX_UINT256 : c.amount).toString(),
            ],
            rationale,
        };
    }

    return {
        target,
        value_wei: valueWei.toString(),
        function_signature: "purchase(bytes32,address,uint64,bool)",
        args: [
            c.resource === "wrong" ? WRONG_RESOURCE : (c.resource ?? RESOURCE),
            c.beneficiary === "attacker" ? ATTACKER : (c.beneficiary ?? (OWNER.address.toLowerCase() as Hex)),
            (c.durationSeconds ?? DAY).toString(),
            (c.recurring ?? false) ? "true" : "false",
        ],
        rationale,
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

async function ownerCall(fn: string, args: unknown[]): Promise<void> {
    const h = await walletClient.writeContract({
        address: vault,
        abi: vaultArt.abi,
        functionName: fn,
        args: args as never,
        account: OWNER,
        chain: anvil,
    });
    await publicClient.waitForTransactionReceipt({hash: h});
}

/**
 * Run one genuinely conforming action all the way through to onchain state.
 *
 * Used only to reach a state — a consumed nonce — that cannot be reached honestly any other
 * way. It is the same pipeline the corpus measures, so if this helper stops working the
 * corpus run fails loudly rather than quietly labelling a state it never established.
 */
async function executeConforming(): Promise<void> {
    // Activates its OWN mandate and policy first. The caller activates the fixture's
    // afterwards. Without this the vault would have the fixture's mandate active while this
    // helper presented a different one, the action would fail its mandate binding, and the
    // helper would throw instead of consuming a nonce.
    await activate(conformingMandate, conformingPolicy);

    const callData = encodeFunctionData({
        abi: payArt.abi,
        functionName: "purchase",
        args: [RESOURCE, OWNER.address, DAY, false],
    }) as Hex;

    const reader = createChainReader(rpcUrl);
    const vaultState = await reader.readVaultState(vault, demoPay, "0xc188528b");
    const action: ActionPayload = {
        schemaVersion: 1n,
        chainId,
        vault,
        actionNonce: vaultState.actionNonce,
        target: demoPay,
        valueWei: CONFORMING_VALUE,
        dataHash: keccak256(toBytes(callData)),
        operation: 0n,
        mandateHash: vaultState.activeMandateHash,
        policyHash: vaultState.activePolicyHash,
        deadline: FAR_FUTURE,
    };

    const decode = decodeCall({target: demoPay, callData, registry});
    const simulation = await simulateAction({
        client: publicClient,
        vault,
        target: demoPay,
        valueWei: CONFORMING_VALUE,
        callData,
        decoded: decode.ok ? decode.decoded : null,
    });
    const latest = await publicClient.getBlock();
    const evaluation = evaluate({
        mandate: conformingMandate,
        policy: conformingPolicy,
        action,
        callData,
        decode,
        simulation,
        vaultState,
        now: latest.timestamp,
    });
    if (evaluation.verdict !== "ALLOW") {
        throw new Error(`nonce-consuming action did not evaluate ALLOW: ${evaluation.reasonCodes.join(",")}`);
    }

    const signed = await signerClient.evaluateAndSign({
        action,
        callData,
        mandate: conformingMandate,
        policy: conformingPolicy,
        evaluation: {
            verdict: "ALLOW",
            reasonCodes: evaluation.reasonCodes,
            evidenceCanonical: evaluation.evidenceCanonical,
            simulationBlockNumber: simulation.anchor.blockNumber,
            simulationBlockHash: simulation.anchor.blockHash,
        },
    });
    if (signed.refused) throw new Error(`signer refused the nonce-consuming action`);

    const h = await walletClient.writeContract({
        address: vault,
        abi: vaultArt.abi,
        functionName: "executeWithReceipt",
        args: [action, callData, signed.receipt, signed.signature],
        account: OWNER,
        chain: anvil,
    });
    const r = await publicClient.waitForTransactionReceipt({hash: h});
    if (r.status !== "success") throw new Error("nonce-consuming execution reverted");
}

interface RunOutcome {
    id: string;
    class: string;
    layers: LayerResult[];
    decodeOk: boolean;
    decodeCode: string | null;
    simulated: boolean;
}

/**
 * WRITE TO A STAGING DIRECTORY AND MOVE IT INTO PLACE AT THE END.
 *
 * This used to `rmSync` the two output directories before the first fixture ran. Combined with
 * A-029 — the views are not byte-reproducible — a run that threw at fixture 30 left the
 * artifacts the labels of record attest to DELETED and only 29 regenerated, with no way to
 * restore them except git. An independent review pointed out that this repository already uses
 * the temp-then-move shape elsewhere for exactly this reason, and that the mutation harness
 * learned the same lesson the hard way: a tool must never have a window in which the thing it
 * replaces does not exist.
 */
const STAGE = mkdtempSync(join(tmpdir(), "sentinel-corpus-"));
mkdirSync(join(STAGE, "for-labelling"), {recursive: true});
mkdirSync(join(STAGE, "results"), {recursive: true});

function publish(): void {
    rmSync(OUT + "/for-labelling", {recursive: true, force: true});
    rmSync(OUT + "/results", {recursive: true, force: true});
    mkdirSync(OUT, {recursive: true});
    renameSync(join(STAGE, "for-labelling"), join(OUT, "for-labelling"));
    renameSync(join(STAGE, "results"), join(OUT, "results"));
    rmSync(STAGE, {recursive: true, force: true});
}

/**
 * Kill the two child processes on ANY exit path.
 *
 * The same review threw at `connectSigner` and had to `pkill` an orphaned Anvil and signer by
 * hand. Nothing here killed them off the happy path.
 */
let cleanedUp = false;
function cleanup(): void {
    if (cleanedUp) return;
    cleanedUp = true;
    try {
        signerProc.kill("SIGTERM");
    } catch {
        /* already gone */
    }
    try {
        node.kill("SIGTERM");
    } catch {
        /* already gone */
    }
}
process.on("exit", cleanup);
for (const sig of ["SIGINT", "SIGTERM"] as const) {
    process.on(sig, () => {
        cleanup();
        process.exit(1);
    });
}
process.on("uncaughtException", (err) => {
    console.error("corpus run failed; committed artifacts left untouched:", err);
    cleanup();
    process.exit(1);
});

const outcomes: RunOutcome[] = [];
const digests: Record<string, string> = {};

for (const spec of CORPUS) {
    const snapshot = await rpc("evm_snapshot", []);

    try {
        const policy: PolicyPayload = {
            schemaVersion: 1n,
            policyVersion: 1n,
            vault,
            chainId,
            allowedOperation: 0n,
            allowedTargetsHash: keccak256(stringToBytes("targets")),
            allowedSelectorsHash: keccak256(stringToBytes("selectors")),
            maxNativeValueWei: MANDATE_CEILING,
            maxAllowanceIncreaseBaseUnits: 0n,
            allowedCallGraphHash: keccak256(stringToBytes("DemoPay.purchase:no-internal-calls")),
            validAfter: 0n,
            validUntil: FAR_FUTURE,
            failureMode: 1n,
            ...spec.policy,
        };
        const mandate: MandatePayload = {
            schemaVersion: 1n,
            mandateId: keccak256(stringToBytes(`mandate:${spec.id}`)),
            principal: OWNER.address.toLowerCase() as Hex,
            vault,
            chainId,
            target: demoPay,
            targetCodeHash: keccak256(toBytes(baseCode ?? "0x")),
            selector: "0xc188528b",
            maxNativeValueWei: MANDATE_CEILING,
            purposeKind: keccak256(stringToBytes("data-service-purchase")),
            resourceId: RESOURCE,
            beneficiary: OWNER.address.toLowerCase() as Hex,
            durationSeconds: DAY,
            recurringAllowed: false,
            validAfter: 0n,
            validUntil: 3_000_000_000n,
            policyHash: hashPolicy(policy),
            ...spec.mandate,
        };

        const env = spec.env ?? {};

        // A REAL prior execution, not a storage poke, and BEFORE the fixture's own mandate
        // is activated. The first version wrote slot 0 with `anvil_setStorageAt` and hoped
        // that was the nonce — a guess about storage layout that would have silently stopped
        // being true on any field reordering, faking the one thing the fixture is about.
        // This consumes the nonce the way the vault itself consumes it (§3.3(9)), so an
        // action re-presented at the consumed value is a real replay.
        if (env.consumeNonceFirst) await executeConforming();

        await activate(mandate, policy);
        const target = targetAddress(spec.target);
        let callData = buildCallData(spec);
        const valueWei = spec.valueWei ?? CONFORMING_VALUE;

        // The transcription is performed here, before any environment manipulation, so a
        // failure names the transcription rather than a later mutation of the calldata. The
        // CHECKING lives in `verifyRationaleFixture` and is called once, below, after the
        // artefacts exist — one call site, structurally asserted by `corpus.test.ts`.
        const transcribedProposal =
            spec.agentRationale === undefined ? null : transcribe(proposalFor(spec, target, valueWei));

        if (env.starveVault) await rpc("anvil_setBalance", [vault, "0x0"]);
        if (env.changeTargetCode) await rpc("anvil_setCode", [demoPay, "0x6001600155"]);
        if (env.advancePastMandateWindow) await rpc("evm_setNextBlockTimestamp", [Number(3_000_000_001n)]);
        if (env.advancePastPolicyWindow) {
            await rpc("evm_setNextBlockTimestamp", [Number(4_000_000_001n)]);
        }
        if (env.advancePastMandateWindow || env.advancePastPolicyWindow) await rpc("evm_mine", []);
        if (env.pauseVault) await ownerCall("setPaused", [true]);
        if (env.rotateSigner) await ownerCall("rotateSigner", [OTHER_SIGNER.address]);
        const reader = createChainReader(rpcUrl);
        const selector = (callData.length >= 10 ? callData.slice(0, 10) : "0x00000000") as Hex;
        const vaultState = await reader.readVaultState(vault, target, selector);

        let action: ActionPayload = {
            schemaVersion: 1n,
            chainId,
            vault,
            actionNonce: vaultState.actionNonce,
            target,
            valueWei,
            dataHash: keccak256(toBytes(callData)),
            operation: 0n,
            mandateHash: vaultState.activeMandateHash,
            policyHash: vaultState.activePolicyHash,
            deadline: FAR_FUTURE,
            ...spec.action,
        };

        // Superseding AFTER the action is bound is the whole point of the class, and the
        // evaluator must then read the vault AGAIN — otherwise both the action and the
        // evaluator's view of "active" come from the same pre-supersede snapshot, they agree
        // trivially, and the fixture measures nothing. The real scenario is three points in
        // time: the action is bound at T, the owner supersedes at T+1, evaluation happens at
        // T+2 against what the vault says then.
        //
        // The first version activated the replacement BEFORE reading vault state, so the
        // action picked up the replacement's hash and pointed at the CURRENT mandate — the
        // fixture's declared intent said "superseded" while its data said otherwise, and an
        // independent labeller caught the contradiction by comparing the two. Ordering is
        // the entire content of this scenario.
        if (env.supersedeMandate) {
            await ownerCall("activateMandate", [keccak256(stringToBytes("a replacement mandate"))]);
        }
        if (env.supersedePolicy) {
            await ownerCall("activatePolicy", [keccak256(stringToBytes("a replacement policy"))]);
        }

        // Applied AFTER the dataHash was computed, which is the whole point of the class.
        if (env.tamperCalldataAfterBinding) {
            callData = buildCallData({...spec, call: {kind: "purchase", resource: "wrong"}});
        }

        // Re-read after any owner action that changes what the vault reports as active.
        const evalVaultState =
            env.supersedeMandate || env.supersedePolicy
                ? await reader.readVaultState(vault, target, selector)
                : vaultState;

        const decode = decodeCall({target, callData, registry});

        let simulation: SimulationResult | null = null;
        if (!env.simulationUnavailable) {
            try {
                simulation = await simulateAction({
                    client: publicClient,
                    vault,
                    target,
                    valueWei,
                    callData,
                    decoded: decode.ok ? decode.decoded : null,
                });
            } catch {
                // A genuine simulation failure is itself a corpus outcome (§3.3(8)), not an
                // error to abort on. It reaches the engine as an absent simulation.
                simulation = null;
            }
        }

        // `now` comes from the CHAIN, not the wall clock.
        //
        // The first version passed `Date.now()`, which made every time-window fixture
        // vacuous: advancing chain time past a mandate's validUntil changed nothing the
        // evaluator could see, so F031 and F032 reported ALLOW for an expired mandate and
        // an expired policy. Nothing in the run looked wrong — three fixtures simply
        // measured nothing. Chain time is also the correct reading on its own terms: the
        // evaluator reasons about state at a recorded block, and the block carries the
        // timestamp that state was true at.
        const latest = await publicClient.getBlock();
        const input = {
            mandate,
            policy,
            action,
            callData,
            decode,
            simulation,
            vaultState: evalVaultState,
            now: latest.timestamp,
        };

        const layers = LAYERS.map((l) => runLayer(l, input, baselineConfig));

        // --- the rationale reached nothing, MEASURED (A-028 F-5) -------------
        //
        // Scans the bound fields, the executed bytes, every layer's checks and reason codes,
        // and the canonical evidence bundle. `evaluate` is called once more here rather than
        // reusing a layer result because the bundle is the artefact that gets SIGNED, and it
        // is the one place a leak would become content the signer attests to.
        if (spec.agentRationale !== undefined) {
            const evaluation = evaluate(input);
            const p = transcribedProposal?.ok === true ? transcribedProposal.proposal : null;
            verifyRationaleFixture({
                fixtureId: spec.id,
                rationale: spec.agentRationale,
                encodedTarget: target,
                encodedValueWei: valueWei,
                encodedCallData: callData,
                transcribed: {
                    ok: transcribedProposal?.ok === true,
                    code: transcribedProposal?.ok === false ? transcribedProposal.code : undefined,
                    detail: transcribedProposal?.ok === false ? transcribedProposal.detail : undefined,
                    target: p?.target,
                    valueWei: p?.valueWei,
                    callData: p?.callData,
                },
                artefact: j({
                    action: {...action, callData},
                    layers,
                    reasonCodes: evaluation.reasonCodes,
                    evidenceCanonical: evaluation.evidenceCanonical,
                }),
            });
        }

        // --- the labeller's view: values and intent, nothing derived ---------
        const labellerView = {
            fixtureId: spec.id,
            scenarioClass: spec.class,
            declaredIntent: spec.intent,
            // Present only on the fixtures that carry one, so 48 views do not gain a null
            // field describing a thing that did not happen to them.
            ...(spec.agentRationale === undefined ? {} : {agentRationale: spec.agentRationale}),
            mandate,
            policy,
            action: {...action, callData},
            observedEnvironment: {
                vaultPaused: evalVaultState.paused,
                vaultActiveMandateHash: evalVaultState.activeMandateHash,
                vaultActivePolicyHash: evalVaultState.activePolicyHash,
                vaultCurrentActionNonce: evalVaultState.actionNonce,
                vaultAuthorisedSigner: evalVaultState.signer,
                vaultOwner: evalVaultState.owner,
                vaultMaxNativeValueWei: evalVaultState.maxNativeValueWei,
                targetOnVaultAllowlist: evalVaultState.targetAllowed,
                selectorOnVaultAllowlist: evalVaultState.selectorAllowed,
                targetRuntimeCodeHashOnChain: evalVaultState.targetCodeHash,
                simulationPerformed: simulation !== null,
                simulationOutcome: simulation === null ? null : simulation.outcome.status,
                simulationRevertReason: simulation === null ? null : simulation.outcome.revertReason,
                nativeBalanceDeltas:
                    simulation?.nativeBalanceDeltas.map((d) => ({address: d.address, delta: d.delta})) ?? null,
                allowanceDeltas:
                    simulation?.allowanceDeltas.map((d) => ({
                        token: d.token,
                        owner: d.owner,
                        spender: d.spender,
                        before: d.before,
                        after: d.after,
                    })) ?? null,
                entitlements:
                    simulation?.entitlements.map((e) => ({
                        contract: e.contract,
                        beneficiary: e.beneficiary,
                        resourceId: e.resourceId,
                        expiryBefore: e.expiryBefore,
                        expiryAfter: e.expiryAfter,
                        recurringBefore: e.recurringBefore,
                        recurringAfter: e.recurringAfter,
                    })) ?? null,
                internalCallCount: simulation?.internalCalls.length ?? null,
                simulationAnchorBlock: simulation?.anchor.blockNumber ?? null,
                // REMOVED (A-028 F-3): `calldataDecodedByASupportedSchema` and
                // `calldataDecodeFailureReason` published the EVALUATOR'S OWN DECODER OUTPUT
                // to the labeller — the same `decode` object handed to `evaluate` below,
                // including its internal enum strings. Six views carried them and labeller C
                // quoted the codes verbatim; `decode.ok === false` was a perfect predictor of
                // "not ALLOW" across the corpus. D-011(b) forbids exactly this, and the guard
                // missed it because the field NAMES merely contained forbidden words rather
                // than equalling them.
                //
                // The labeller does not need them. The calldata itself is published in full
                // (`action.callData`), and §5.7's supported schemas are in the specification,
                // so a labeller can determine decodability by reading the bytes against the
                // spec — which is the independent reasoning the corpus is supposed to measure,
                // rather than being handed the implementation's answer.
            },
        };
        assertNoLeakage(labellerView, spec.id);
        assertViewShape(labellerView as unknown as Record<string, unknown>, spec.id);
        writeFileSync(join(STAGE, "for-labelling", `${spec.id}.json`), j(labellerView));
        digests[spec.id] = normalisedDigest(labellerView);

        writeFileSync(
            join(STAGE, "results", `${spec.id}.json`),
            j({
                fixtureId: spec.id,
                class: spec.class,
                intent: spec.intent,
                // Recorded on the RESULTS side so the ablation can state which fixtures
                // actually carried an injection rather than describing the class from its
                // name — which is what produced the overclaim A-028 F-5 found.
                agentRationale: spec.agentRationale ?? null,
                primaryEnforcement: spec.primaryEnforcement ?? "conformance-engine",
                decode: decode.ok ? {ok: true, schema: decode.decoded.schema} : {ok: false, code: decode.code},
                simulated: simulation !== null,
                layers,
            }),
        );

        outcomes.push({
            id: spec.id,
            class: spec.class,
            layers,
            decodeOk: decode.ok,
            decodeCode: decode.ok ? null : decode.code,
            simulated: simulation !== null,
        });

        const v = layers.map((l) => `${l.layer.slice(0, 2)}=${l.verdict.padEnd(6)}`).join(" ");
        console.log(`${spec.id}  ${v}  ${spec.class}`);
    } finally {
        await rpc("evm_revert", [snapshot]);
    }
}

writeFileSync(
    join(STAGE, "for-labelling", "_digests.json"),
    j({
        note:
            "sha256/128 of each labeller view with the run-varying timestamp fields normalised " +
            "out (A-029). A corpus re-run that changes nothing a labeller reasons about leaves " +
            "this file byte-identical, so `git diff` on it is the signal. The view FILES " +
            "themselves are not byte-reproducible and are not meant to be.",
        normalisedFields: RUN_VARYING_FIELDS,
        digests,
    }),
);

writeFileSync(
    join(STAGE, "results", "_index.json"),
    j(
        outcomes.map((o) => ({
            id: o.id,
            class: o.class,
            verdicts: Object.fromEntries(o.layers.map((l) => [l.layer, l.verdict])),
        })),
    ),
);

console.log(`\n${outcomes.length} fixtures executed`);
for (const layer of LAYERS) {
    const counts: Record<string, number> = {ALLOW: 0, BLOCK: 0, REVIEW: 0};
    for (const o of outcomes) {
        const verdict = o.layers.find((l) => l.layer === layer)!.verdict;
        counts[verdict] = (counts[verdict] ?? 0) + 1;
    }
    console.log(`  ${layer.padEnd(24)} allow=${counts.ALLOW} block=${counts.BLOCK} review=${counts.REVIEW}`);
}

publish();

await signerClient.close().catch(() => {});
cleanup();
process.exit(0);
