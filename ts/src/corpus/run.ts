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
    type PublicClient,
} from "viem";
import {privateKeyToAccount} from "viem/accounts";
import {anvil} from "viem/chains";
import {buildRegistry, decodeCall} from "../decode/index.ts";
import {simulateAction, type SimulationResult} from "../simulate/index.ts";
import {hashMandate, hashPolicy} from "../evaluate/hashes.ts";
import {createChainReader} from "../signer/vault.ts";
import {connectSigner} from "../signer/client.ts";
import {evaluate} from "../evaluate/index.ts";
import type {ActionPayload, Hex, MandatePayload, PolicyPayload} from "../signer/protocol.ts";
import {LAYERS, runLayer, type LayerResult} from "../ablation/layers.ts";
import type {BaselineConfig} from "../ablation/baseline.ts";
import {CORPUS, ATTACKER, RESOURCE, WRONG_RESOURCE, CONFORMING_VALUE, MANDATE_CEILING} from "./fixtures.ts";
import type {FixtureSpec} from "./spec.ts";
import {assertNoLeakage} from "./leakage.ts";

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
const OUT = join(REPO, "fixtures", "corpus");
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

const socketPath = join(REPO, ".sentinel", `corpus-${port}.sock`);
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

rmSync(OUT + "/for-labelling", {recursive: true, force: true});
rmSync(OUT + "/results", {recursive: true, force: true});
mkdirSync(join(OUT, "for-labelling"), {recursive: true});
mkdirSync(join(OUT, "results"), {recursive: true});

const outcomes: RunOutcome[] = [];

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

        // --- the labeller's view: values and intent, nothing derived ---------
        const labellerView = {
            fixtureId: spec.id,
            scenarioClass: spec.class,
            declaredIntent: spec.intent,
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
                calldataDecodedByASupportedSchema: decode.ok,
                calldataDecodeFailureReason: decode.ok ? null : decode.code,
            },
        };
        const labellerJson = j(labellerView);
        assertNoLeakage(labellerJson, spec.id);
        writeFileSync(join(OUT, "for-labelling", `${spec.id}.json`), labellerJson);

        writeFileSync(
            join(OUT, "results", `${spec.id}.json`),
            j({
                fixtureId: spec.id,
                class: spec.class,
                intent: spec.intent,
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
    join(OUT, "results", "_index.json"),
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

await signerClient.close().catch(() => {});
signerProc.kill("SIGTERM");
node.kill("SIGTERM");
process.exit(0);
