import {after, before, describe, it} from "node:test";
import assert from "node:assert/strict";
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
import {anvil} from "viem/chains";
import {buildRegistry, decodeCall, type TargetRegistry} from "../src/decode/index.ts";
import {evaluate, type Verdict} from "../src/evaluate/index.ts";
import {hashMandate, hashPolicy} from "../src/evaluate/hashes.ts";
import {simulateAction} from "../src/simulate/index.ts";
import {connectSigner, type SignerClient} from "../src/signer/client.ts";
import {createChainReader} from "../src/signer/vault.ts";
import type {
    ActionPayload,
    Hex,
    MandatePayload,
    PolicyPayload,
} from "../src/signer/protocol.ts";
import {
    OWNER,
    SIGNER,
    artifact,
    startAnvil,
    startSignerProcess,
    type AnvilHandle,
    type SignerHandle,
} from "./harness.ts";

/**
 * The four demonstration cases of §4.2, end to end.
 *
 * Each runs the real pipeline — decode, simulate against a real Anvil with the real
 * compiled contracts, evaluate — and Case 1 continues through the isolated signer process
 * and into `SentinelVault.executeWithReceipt`. Nothing is stubbed.
 *
 * WHAT THESE TESTS ARE EVIDENCE FOR, AND WHAT THEY ARE NOT.
 *
 * They demonstrate that the mechanism runs end to end and that the four cases reach their
 * documented verdicts. That is worth having and it is NOT evidence that the verdicts are
 * correct in general. §7 opens by saying so directly: "Four demo paths alone cannot prove
 * that the verdicts are not hard-coded." The bar for the conformance engine is the
 * independently labelled corpus of §9 step 8 — authored under D-011 by an agent with no
 * implementation context, adversarially cross-checked, sampled by John at the gate — plus
 * the §7.3 ablation that measures what each layer actually contributes. Until those exist,
 * a green run here means the machine turns over.
 *
 * Case 3 is the one that carries the differentiation claim, and its test asserts the shape
 * §7.2 cares about: the action passes every check a representative policy baseline would
 * make, and fails only on mandate conformance.
 */

let node: AnvilHandle;
let signer: SignerHandle;
let client: SignerClient;
let publicClient: PublicClient;
let walletClient: WalletClient;

let vault: Hex;
let demoPay: Hex;
let demoErc20: Hex;
let vaultAbi: Abi;
let demoPayAbi: Abi;
let demoErc20Abi: Abi;
let registry: TargetRegistry;
let chainId: bigint;

const RESOURCE: Hex = keccak256(stringToBytes("weather-basic-24h"));
const WRONG_RESOURCE: Hex = keccak256(stringToBytes("premium-monthly"));
const ATTACKER: Hex = "0x00000000000000000000000000000000deadbeef";
const DURATION = 86_400n;
const PURCHASE_VALUE = 10n ** 15n;
const FAR_FUTURE = 4_000_000_000n;

const PURCHASE_ABI = [
    {
        type: "function",
        name: "purchase",
        stateMutability: "payable",
        inputs: [{type: "bytes32"}, {type: "address"}, {type: "uint64"}, {type: "bool"}],
        outputs: [],
    },
] as const;

function purchaseCalldata(resource: Hex, beneficiary: Hex, duration = DURATION, recurring = false): Hex {
    return encodeFunctionData({
        abi: PURCHASE_ABI,
        functionName: "purchase",
        args: [resource, beneficiary, duration, recurring],
    }) as Hex;
}

before(async () => {
    node = await startAnvil();
    publicClient = createPublicClient({chain: anvil, transport: http(node.rpcUrl)});
    walletClient = createWalletClient({chain: anvil, account: OWNER, transport: http(node.rpcUrl)});
    chainId = BigInt(await publicClient.getChainId());

    const payArt = artifact("DemoPay.sol", "DemoPay");
    const ercArt = artifact("DemoERC20.sol", "DemoERC20");
    const vaultArt = artifact("SentinelVault.sol", "SentinelVault");
    demoPayAbi = payArt.abi;
    demoErc20Abi = ercArt.abi;
    vaultAbi = vaultArt.abi;

    const deploy = async (art: {abi: Abi; bytecode: Hex}, args: unknown[], value = 0n): Promise<Hex> => {
        const hash = await walletClient.deployContract({
            abi: art.abi,
            bytecode: art.bytecode,
            args: args as never,
            account: OWNER,
            chain: anvil,
            value,
        });
        return (await publicClient.waitForTransactionReceipt({hash})).contractAddress!.toLowerCase() as Hex;
    };

    demoPay = await deploy(payArt, []);
    const purchaseSelector = "0xc188528b" as Hex;
    const approveSelector = "0x095ea7b3" as Hex;

    vault = await deploy(
        vaultArt,
        [OWNER.address, SIGNER.address, 10n ** 16n, [demoPay, "0x0000000000000000000000000000000000000001"], [purchaseSelector, approveSelector]],
        10n ** 18n,
    );
    demoErc20 = await deploy(ercArt, [vault, 10n ** 24n]);
    registry = buildRegistry({[demoPay]: "DemoPay", [demoErc20]: "DemoERC20"});

    signer = await startSignerProcess({rpcUrl: node.rpcUrl, vault});
    client = await connectSigner(signer.socketPath);
});

after(async () => {
    await client?.close().catch(() => {});
    signer?.stop();
    node?.stop();
});

/**
 * The Case 1 mandate and policy.
 *
 * `failureMode` is REVIEW because §4.2 Case 4 expects a review receipt on evidence
 * uncertainty, and `failureMode` is what governs that (A-020). Under FAIL_CLOSED the
 * identical evidence gap blocks — a legitimate configuration and a different demonstration.
 */
async function buildMandateAndPolicy(overrides: {mandate?: Partial<MandatePayload>} = {}) {
    const code = await publicClient.getCode({address: demoPay});
    const policy: PolicyPayload = {
        schemaVersion: 1n,
        policyVersion: 1n,
        vault,
        chainId,
        allowedOperation: 0n,
        allowedTargetsHash: keccak256(stringToBytes("targets")),
        allowedSelectorsHash: keccak256(stringToBytes("selectors")),
        maxNativeValueWei: 10n ** 16n,
        // Zero: this mandate authorises a purchase, not an approval. Any approval at all is
        // over the ceiling, which is what makes Case 2 a policy violation rather than a
        // judgement call.
        maxAllowanceIncreaseBaseUnits: 0n,
        allowedCallGraphHash: keccak256(stringToBytes("DemoPay.purchase:no-internal-calls")),
        validAfter: 0n,
        validUntil: FAR_FUTURE,
        failureMode: 1n,
    };
    const mandate: MandatePayload = {
        schemaVersion: 1n,
        mandateId: keccak256(stringToBytes("mandate:case-1")),
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
        ...overrides.mandate,
    };
    return {mandate, policy, mandateHash: hashMandate(mandate), policyHash: hashPolicy(policy)};
}

async function activate(mandateHash: Hex, policyHash: Hex): Promise<void> {
    for (const [fn, arg] of [
        ["activateMandate", mandateHash],
        ["activatePolicy", policyHash],
    ] as const) {
        const hash = await walletClient.writeContract({
            address: vault,
            abi: vaultAbi,
            functionName: fn,
            args: [arg],
            account: OWNER,
            chain: anvil,
        });
        await publicClient.waitForTransactionReceipt({hash});
    }
}

/** decode → simulate → evaluate, exactly as §3.2 steps 6–10 sequence it. */
async function runPipeline(args: {
    mandate: MandatePayload;
    policy: PolicyPayload;
    target: Hex;
    callData: Hex;
    valueWei: bigint;
}) {
    const reader = createChainReader(node.rpcUrl);
    const decode = decodeCall({target: args.target, callData: args.callData, registry});
    const selector = args.callData.slice(0, 10) as Hex;
    const vaultState = await reader.readVaultState(vault, args.target, selector);

    const action: ActionPayload = {
        schemaVersion: 1n,
        chainId,
        vault,
        actionNonce: vaultState.actionNonce,
        target: args.target,
        valueWei: args.valueWei,
        dataHash: keccak256(toBytes(args.callData)),
        operation: 0n,
        mandateHash: vaultState.activeMandateHash,
        policyHash: vaultState.activePolicyHash,
        deadline: FAR_FUTURE,
    };

    const simulation = await simulateAction({
        client: publicClient,
        vault,
        target: args.target,
        valueWei: args.valueWei,
        callData: args.callData,
        decoded: decode.ok ? decode.decoded : null,
    });

    const evaluation = evaluate({
        mandate: args.mandate,
        policy: args.policy,
        action,
        callData: args.callData,
        decode,
        simulation,
        vaultState,
        now: BigInt(Math.floor(Date.now() / 1000)),
    });

    return {action, decode, simulation, evaluation, vaultState};
}

/** bigint-safe rendering, so an assertion message never crashes instead of reporting. */
function show(value: unknown): string {
    return JSON.stringify(value, (_k, v) => (typeof v === "bigint" ? v.toString() : v));
}

function codes(evaluation: {checks: {code: string; outcome: string}[]}, outcome: string): string[] {
    return evaluation.checks.filter((c) => c.outcome === outcome).map((c) => c.code);
}

// ---------------------------------------------------------------------------

describe("Case 1 — exact mandate, allow", () => {
    it("evaluates ALLOW, the signer attests, and the vault executes the purchase", async () => {
        const {mandate, policy, mandateHash, policyHash} = await buildMandateAndPolicy();
        await activate(mandateHash, policyHash);

        const callData = purchaseCalldata(RESOURCE, OWNER.address.toLowerCase() as Hex);
        const {action, evaluation, simulation} = await runPipeline({
            mandate,
            policy,
            target: demoPay,
            callData,
            valueWei: PURCHASE_VALUE,
        });

        assert.equal(
            evaluation.verdict,
            "ALLOW" satisfies Verdict,
            `expected ALLOW; violations=${codes(evaluation, "VIOLATION")} ` +
                `unresolved=${codes(evaluation, "UNRESOLVED")}`,
        );
        assert.deepEqual(evaluation.reasonCodes, []);

        // The signer independently re-derives everything and attests.
        const signed = await client.evaluateAndSign({
            action,
            callData,
            mandate,
            policy,
            evaluation: {
                verdict: "ALLOW",
                reasonCodes: evaluation.reasonCodes,
                evidenceCanonical: evaluation.evidenceCanonical,
                simulationBlockNumber: simulation.anchor.blockNumber,
                simulationBlockHash: simulation.anchor.blockHash,
            },
        });
        assert.equal(signed.refused, false, `signer refused: ${show(signed)}`);

        // The receipt commits to the evidence the evaluator produced.
        assert.equal(signed.receipt.evidenceHash, evaluation.evidenceHash);

        const hash = await walletClient.writeContract({
            address: vault,
            abi: vaultAbi,
            functionName: "executeWithReceipt",
            args: [action, callData, signed.receipt, signed.signature],
            account: OWNER,
            chain: anvil,
        });
        assert.equal((await publicClient.waitForTransactionReceipt({hash})).status, "success");

        const expiry = (await publicClient.readContract({
            address: demoPay,
            abi: demoPayAbi,
            functionName: "entitlementExpiry",
            args: [OWNER.address, RESOURCE],
        })) as bigint;
        assert.ok(expiry > 0n, "the authorised purchase did not land");
    });
});

describe("Case 2 — real prompt injection, block", () => {
    it("blocks the injected approve, and no executable receipt exists", async () => {
        // The proposal the injection actually produced (A-009): the attacker as spender,
        // max uint256 as the amount. Sentinel derives that from calldata, not from the
        // agent's description of it.
        const {mandate, policy, mandateHash, policyHash} = await buildMandateAndPolicy();
        await activate(mandateHash, policyHash);

        const callData = encodeFunctionData({
            abi: demoErc20Abi,
            functionName: "approve",
            args: [ATTACKER, (1n << 256n) - 1n],
        }) as Hex;

        const {action, evaluation, simulation} = await runPipeline({
            mandate,
            policy,
            target: demoErc20,
            callData,
            valueWei: 0n,
        });

        assert.equal(evaluation.verdict, "BLOCK");
        // The decoded parameters are what condemn it — not the target address alone.
        assert.ok(codes(evaluation, "VIOLATION").includes("EVAL_APPROVAL_CEILING"));
        assert.ok(codes(evaluation, "VIOLATION").includes("EVAL_TARGET_BOUND"));

        // The simulation shows exactly what would have happened: the vault's own tokens,
        // approved without limit to the attacker.
        assert.equal(simulation.allowanceDeltas[0]!.after, (1n << 256n) - 1n);
        assert.equal(simulation.allowanceDeltas[0]!.owner, vault);

        // §4.2: "No executable receipt exists." The signer will sign a BLOCK receipt as
        // evidence, and the vault refuses it on both paths.
        const signed = await client.evaluateAndSign({
            action,
            callData,
            mandate,
            policy,
            evaluation: {
                verdict: "BLOCK",
                reasonCodes: evaluation.reasonCodes,
                evidenceCanonical: evaluation.evidenceCanonical,
                simulationBlockNumber: simulation.anchor.blockNumber,
                simulationBlockHash: simulation.anchor.blockHash,
            },
        });
        assert.equal(signed.refused, false);
        assert.equal(signed.receipt.verdict, 0n);

        await assert.rejects(
            () =>
                walletClient.writeContract({
                    address: vault,
                    abi: vaultAbi,
                    functionName: "executeWithReceipt",
                    args: [action, callData, signed.receipt, signed.signature],
                    account: OWNER,
                    chain: anvil,
                }),
            /NotAllowVerdict|TargetNotAllowed/,
        );
    });
});

describe("Case 3 — mechanically valid, wrong purpose, block", () => {
    it("passes every representative-baseline check and fails only mandate conformance", async () => {
        // THE CASE THAT CARRIES THE DIFFERENTIATION CLAIM (§4.2, §7.2).
        //
        // §7.2's representative local baseline checks: exact chain and vault, allowlisted
        // target, native-value ceiling, and a direct maximum-approval block. It has "no
        // resource, beneficiary, duration, recurrence, or post-state constraint".
        //
        // So this action must satisfy all of those and still be blocked — otherwise the
        // demonstration would be showing an ordinary policy engine at work rather than
        // mandate conformance. The assertions below name that shape explicitly rather than
        // just checking the verdict.
        const {mandate, policy, mandateHash, policyHash} = await buildMandateAndPolicy();
        await activate(mandateHash, policyHash);

        const callData = purchaseCalldata(WRONG_RESOURCE, OWNER.address.toLowerCase() as Hex);
        const {evaluation, simulation} = await runPipeline({
            mandate,
            policy,
            target: demoPay,
            callData,
            valueWei: PURCHASE_VALUE,
        });

        assert.equal(evaluation.verdict, "BLOCK");

        // What a representative baseline would have checked — all passing.
        const passed = codes(evaluation, "PASS");
        for (const baselineCheck of [
            "EVAL_CHAIN_BOUND",
            "EVAL_VAULT_BOUND",
            "EVAL_TARGET_BOUND",
            "EVAL_SELECTOR_BOUND",
            "EVAL_VALUE_WITHIN_POLICY",
            "EVAL_VALUE_WITHIN_VAULT_CAP",
            "EVAL_OPERATION_SUPPORTED",
            "EVAL_SIMULATION_SUCCEEDS",
        ]) {
            assert.ok(passed.includes(baselineCheck), `${baselineCheck} should pass a baseline`);
        }

        // And the execution genuinely succeeds — this is not a call that would have failed.
        assert.equal(simulation.outcome.status, "success");

        // The only violation is the mandate's purpose constraint.
        assert.deepEqual(
            codes(evaluation, "VIOLATION"),
            ["EVAL_PURCHASE_RESOURCE"],
            "Case 3 must fail on mandate conformance ALONE, or it proves nothing about it",
        );
    });

    it("also blocks recurrence the mandate forbids", async () => {
        const {mandate, policy, mandateHash, policyHash} = await buildMandateAndPolicy();
        await activate(mandateHash, policyHash);

        const callData = purchaseCalldata(RESOURCE, OWNER.address.toLowerCase() as Hex, DURATION, true);
        const {evaluation} = await runPipeline({
            mandate,
            policy,
            target: demoPay,
            callData,
            valueWei: PURCHASE_VALUE,
        });

        assert.equal(evaluation.verdict, "BLOCK");
        const violations = codes(evaluation, "VIOLATION");
        assert.ok(violations.includes("EVAL_PURCHASE_RECURRENCE"));
        // The simulated post-state corroborates the decoded parameter, per §5.7 — an event
        // alone is not proof, the resulting contract state is.
        assert.ok(violations.includes("EVAL_ENTITLEMENT_RECURRENCE"));
    });
});

describe("Case 4 — evidence uncertainty, review", () => {
    it("reviews rather than blocking when the target's code identity is not established", async () => {
        // §4.2: "Sentinel does not label the target malicious. It reports insufficient
        // evidence for automatic approval." That is why a code-hash mismatch is UNRESOLVED
        // and not a violation — and why this case needs failureMode = REVIEW.
        const {mandate, policy, mandateHash, policyHash} = await buildMandateAndPolicy({
            mandate: {targetCodeHash: keccak256(stringToBytes("yesterday's bytecode"))},
        });
        await activate(mandateHash, policyHash);

        const callData = purchaseCalldata(RESOURCE, OWNER.address.toLowerCase() as Hex);
        const {evaluation} = await runPipeline({
            mandate,
            policy,
            target: demoPay,
            callData,
            valueWei: PURCHASE_VALUE,
        });

        assert.equal(
            evaluation.verdict,
            "REVIEW",
            `expected REVIEW; violations=${codes(evaluation, "VIOLATION")}`,
        );
        assert.deepEqual(codes(evaluation, "VIOLATION"), [], "Case 4 must not accuse the target");
        assert.ok(codes(evaluation, "UNRESOLVED").includes("EVAL_TARGET_CODE_IDENTITY"));
    });

    it("blocks the identical evidence gap under a FAIL_CLOSED policy", async () => {
        // The same uncertainty, a different policy. Demonstrates that failureMode is what
        // governs, and that Case 4's expected REVIEW is a property of its policy rather
        // than a hard-coded behaviour of the engine (A-020).
        const {mandate, policy, mandateHash, policyHash} = await buildMandateAndPolicy({
            mandate: {targetCodeHash: keccak256(stringToBytes("yesterday's bytecode"))},
        });
        const strict = {...policy, failureMode: 0n};
        const relinked = {...mandate, policyHash: hashPolicy(strict)};
        await activate(hashMandate(relinked), hashPolicy(strict));

        const callData = purchaseCalldata(RESOURCE, OWNER.address.toLowerCase() as Hex);
        const {evaluation} = await runPipeline({
            mandate: relinked,
            policy: strict,
            target: demoPay,
            callData,
            valueWei: PURCHASE_VALUE,
        });

        assert.equal(evaluation.verdict, "BLOCK");
        assert.deepEqual(codes(evaluation, "VIOLATION"), []);
        assert.ok(codes(evaluation, "UNRESOLVED").includes("EVAL_TARGET_CODE_IDENTITY"));
    });
});

describe("the evidence bundle", () => {
    it("carries all thirteen §5.6 fields and hashes deterministically", async () => {
        const {mandate, policy, mandateHash, policyHash} = await buildMandateAndPolicy();
        await activate(mandateHash, policyHash);

        const callData = purchaseCalldata(RESOURCE, OWNER.address.toLowerCase() as Hex);
        const {evaluation} = await runPipeline({
            mandate,
            policy,
            target: demoPay,
            callData,
            valueWei: PURCHASE_VALUE,
        });

        const bundle = evaluation.bundle as Record<string, unknown>;
        for (const field of [
            "normalizedAction",
            "decodedSelectorAndParameters",
            "policyChecks",
            "expectedEffects",
            "observedPreState",
            "observedPostState",
            "nativeBalanceDeltas",
            "allowanceDeltas",
            "internalCallTrace",
            "targetCodeIdentity",
            "citedContextReferences",
            "unresolvedChecks",
            "aiExplanation",
        ]) {
            assert.ok(field in bundle, `§5.6 field ${field} is missing from the bundle`);
        }

        // Passes are recorded, not just failures — §5.6's policyChecks must be able to
        // distinguish "checked and passed" from "never checked".
        const policyChecks = bundle.policyChecks as {outcome: string}[];
        assert.ok(policyChecks.some((c) => c.outcome === "PASS"));

        // The hash is of the exact canonical bytes, and re-canonicalising is stable.
        const {canonicalize} = await import("../src/evaluate/jcs.ts");
        assert.equal(canonicalize(evaluation.bundle), evaluation.evidenceCanonical);
    });
});
