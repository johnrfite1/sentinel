import {describe, it} from "node:test";
import assert from "node:assert/strict";
import {keccak256, stringToBytes, toBytes} from "viem";
import {decodeCall, buildRegistry, type DecodeResult} from "../src/decode/index.ts";
import {EVAL_CODES, evaluate, runChecks, type CheckOutcome} from "../src/evaluate/index.ts";
import {hashCallData, hashMandate, hashPolicy} from "../src/evaluate/hashes.ts";
import type {SimulationResult} from "../src/simulate/index.ts";
import type {VaultState} from "../src/signer/vault.ts";
import type {
    ActionPayload,
    Hex,
    MandatePayload,
    PolicyPayload,
} from "../src/signer/protocol.ts";

/**
 * One case per declared conformance check.
 *
 * WHY THIS FILE EXISTS. The four demonstration cases reach their documented verdicts, and
 * that told me nothing about the other checks: 24 of the engine's 37 codes were exercised
 * by nothing, and a mutation deleting the beneficiary check left the whole suite green.
 * This is the second time the same gap has appeared — the signer had 22 of 31 uncovered
 * (A-016) — and it appeared again for the same reason, which is that demonstration cases
 * cover the paths someone thought to demonstrate.
 *
 * The durable fix is the exhaustiveness assertion at the bottom, running against
 * `EVAL_CODES`. A check added later without a case here turns this file red.
 *
 * COVERAGE BOUNDARY, unchanged and worth repeating: these prove each check FIRES on its own
 * trigger. They are not evidence that the checks are the RIGHT checks, nor that the
 * verdicts are correct — this module's own tests cannot be that, by construction. The bar
 * is the independently labelled corpus of §9 step 8.
 */

const VAULT: Hex = "0x1111111111111111111111111111111111111111";
const DEMO_PAY: Hex = "0x2222222222222222222222222222222222222222";
const DEMO_ERC20: Hex = "0x3333333333333333333333333333333333333333";
const OWNER: Hex = "0x4444444444444444444444444444444444444444";
const OTHER: Hex = "0x9999999999999999999999999999999999999999";
const RESOURCE: Hex = keccak256(stringToBytes("weather-basic-24h"));
const CODE_HASH: Hex = keccak256(stringToBytes("DemoPay runtime"));
const NOW = 1_800_000_000n;
const VALUE = 1_000n;
const DURATION = 86_400n;

const REGISTRY = buildRegistry({[DEMO_PAY]: "DemoPay", [DEMO_ERC20]: "DemoERC20"});

/** `purchase(bytes32,address,uint64,bool)` — encoded by hand so the fixture owns its bytes. */
function purchaseCalldata(
    resource: Hex = RESOURCE,
    beneficiary: Hex = OWNER,
    duration = DURATION,
    recurring = false,
): Hex {
    const w = (h: string) => h.padStart(64, "0");
    return `0xc188528b${w(resource.slice(2))}${w(beneficiary.slice(2))}${w(
        duration.toString(16),
    )}${w(recurring ? "1" : "0")}` as Hex;
}

function approveCalldata(spender: Hex = OWNER, amount = 0n): Hex {
    const w = (h: string) => h.padStart(64, "0");
    return `0x095ea7b3${w(spender.slice(2))}${w(amount.toString(16))}` as Hex;
}

interface Overrides {
    mandate?: Partial<MandatePayload>;
    policy?: Partial<PolicyPayload>;
    action?: Partial<ActionPayload>;
    state?: Partial<VaultState>;
    simulation?: Partial<SimulationResult> | null;
    callData?: Hex;
    target?: Hex;
    now?: bigint;
}

/**
 * A fully conforming evaluation, with every hash derived so one perturbation stays
 * consistent everywhere else. The baseline must produce ALLOW with zero non-PASS checks —
 * asserted below, because without that control every "the check fired" assertion could be
 * satisfied by a fixture broken in some unrelated way.
 */
function fixture(o: Overrides = {}) {
    const policy: PolicyPayload = {
        schemaVersion: 1n,
        policyVersion: 1n,
        vault: VAULT,
        chainId: 31337n,
        allowedOperation: 0n,
        allowedTargetsHash: keccak256(stringToBytes("targets")),
        allowedSelectorsHash: keccak256(stringToBytes("selectors")),
        maxNativeValueWei: 10n ** 18n,
        maxAllowanceIncreaseBaseUnits: 0n,
        allowedCallGraphHash: keccak256(stringToBytes("graph")),
        validAfter: 0n,
        validUntil: NOW + 100_000n,
        failureMode: 1n,
        ...o.policy,
    };
    const policyHash = hashPolicy(policy);

    const mandate: MandatePayload = {
        schemaVersion: 1n,
        mandateId: keccak256(stringToBytes("mandate")),
        principal: OWNER,
        vault: VAULT,
        chainId: 31337n,
        target: DEMO_PAY,
        targetCodeHash: CODE_HASH,
        selector: "0xc188528b",
        maxNativeValueWei: 10n ** 18n,
        purposeKind: keccak256(stringToBytes("purpose")),
        resourceId: RESOURCE,
        beneficiary: OWNER,
        durationSeconds: DURATION,
        recurringAllowed: false,
        validAfter: 0n,
        validUntil: NOW + 100_000n,
        policyHash,
        ...o.mandate,
    };
    const mandateHash = hashMandate(mandate);

    const callData = o.callData ?? purchaseCalldata();
    const target = o.target ?? DEMO_PAY;

    const vaultState: VaultState = {
        owner: OWNER,
        signer: OTHER,
        activeMandateHash: mandateHash,
        activePolicyHash: policyHash,
        actionNonce: 0n,
        paused: false,
        maxNativeValueWei: 10n ** 18n,
        targetAllowed: true,
        selectorAllowed: true,
        domainSeparator: keccak256(stringToBytes("domain")),
        targetCodeHash: mandate.targetCodeHash,
        observedAtBlock: 100n,
        ...o.state,
    };

    const action: ActionPayload = {
        schemaVersion: 1n,
        chainId: mandate.chainId,
        vault: VAULT,
        actionNonce: vaultState.actionNonce,
        target,
        valueWei: VALUE,
        dataHash: hashCallData(callData),
        operation: 0n,
        mandateHash: vaultState.activeMandateHash,
        policyHash: vaultState.activePolicyHash,
        deadline: NOW + 10_000n,
        ...o.action,
    };

    const decode: DecodeResult = decodeCall({target, callData, registry: REGISTRY});

    const baseSimulation: SimulationResult = {
        anchor: {blockNumber: 100n, blockHash: keccak256(stringToBytes("block"))},
        outcome: {status: "success", revertReason: null},
        gasUsed: 50_000n,
        nativeBalanceDeltas: [
            {address: VAULT, before: 10n ** 18n, after: 10n ** 18n - VALUE, delta: -VALUE},
            {address: target, before: 0n, after: VALUE, delta: VALUE},
        ],
        allowanceDeltas: [],
        entitlements: [
            {
                contract: target,
                beneficiary: OWNER,
                resourceId: RESOURCE,
                expiryBefore: 0n,
                expiryAfter: NOW + DURATION,
                recurringBefore: false,
                recurringAfter: false,
            },
        ],
        events: [],
        callTrace: null,
        internalCalls: [],
        unresolvedChecks: [],
    };

    const simulation =
        o.simulation === null ? null : {...baseSimulation, ...(o.simulation ?? {})};

    return {
        mandate,
        policy,
        action,
        callData,
        decode,
        simulation,
        vaultState,
        now: o.now ?? NOW,
    };
}

function outcomeOf(o: Overrides, code: string): CheckOutcome | "ABSENT" {
    const results = runChecks(fixture(o));
    return results.find((r) => r.code === code)?.outcome ?? "ABSENT";
}

/**
 * Perturbations, at least one per declared code. Each changes exactly one dimension.
 *
 * `note` distinguishes rows that share a code. Added for the window checks (A-064): each of
 * those compares TWO bounds and only the upper one was ever perturbed, so `now >= validAfter`
 * could be deleted from either check with the whole suite green. A row per BOUND, not per code.
 */
const CASES: {code: string; expect: CheckOutcome; overrides: Overrides; note?: string}[] = [
    {code: "EVAL_MANDATE_ACTIVE", expect: "VIOLATION",
     overrides: {state: {activeMandateHash: keccak256(stringToBytes("other"))}}},
    {code: "EVAL_POLICY_ACTIVE", expect: "VIOLATION",
     overrides: {state: {activePolicyHash: keccak256(stringToBytes("other"))}}},
    {code: "EVAL_MANDATE_PRINCIPAL_IS_OWNER", expect: "VIOLATION", overrides: {state: {owner: OTHER}}},
    {code: "EVAL_VAULT_NOT_PAUSED", expect: "VIOLATION", overrides: {state: {paused: true}}},
    {code: "EVAL_CHAIN_BOUND", expect: "VIOLATION", overrides: {action: {chainId: 999n}}},
    {code: "EVAL_VAULT_BOUND", expect: "VIOLATION", overrides: {action: {vault: OTHER}}},
    {code: "EVAL_NONCE_CURRENT", expect: "VIOLATION", overrides: {action: {actionNonce: 7n}}},
    {code: "EVAL_TARGET_BOUND", expect: "VIOLATION", overrides: {mandate: {target: OTHER}}},
    {code: "EVAL_OPERATION_SUPPORTED", expect: "VIOLATION", overrides: {action: {operation: 1n}}},
    {code: "EVAL_CALLDATA_BINDING", expect: "VIOLATION",
     overrides: {action: {dataHash: keccak256(stringToBytes("lie"))}}},
    {code: "EVAL_ACTION_BINDS_MANDATE_AND_POLICY", expect: "VIOLATION",
     overrides: {action: {mandateHash: keccak256(stringToBytes("stale"))}},
     note: "mandate half of the conjunction"},
    {code: "EVAL_ACTION_BINDS_MANDATE_AND_POLICY", expect: "VIOLATION",
     overrides: {action: {policyHash: keccak256(stringToBytes("unbound"))}},
     note: "POLICY half — deletable with the whole suite green before A-068"},
    {code: "EVAL_MANDATE_BINDS_POLICY", expect: "VIOLATION",
     overrides: {mandate: {policyHash: keccak256(stringToBytes("unlinked"))}}},
    {code: "EVAL_TARGET_CODE_IDENTITY", expect: "UNRESOLVED",
     overrides: {state: {targetCodeHash: keccak256(stringToBytes("changed"))}}},
    {code: "EVAL_MANDATE_WINDOW", expect: "VIOLATION", overrides: {mandate: {validUntil: NOW - 1n}},
     note: "upper bound: validUntil in the past"},
    {code: "EVAL_MANDATE_WINDOW", expect: "VIOLATION", overrides: {mandate: {validAfter: NOW + 1n}},
     note: "LOWER bound: validAfter in the future — a mandate signed but not yet in force"},
    {code: "EVAL_POLICY_WINDOW", expect: "VIOLATION", overrides: {policy: {validUntil: NOW - 1n}},
     note: "upper bound: validUntil in the past"},
    {code: "EVAL_POLICY_WINDOW", expect: "VIOLATION", overrides: {policy: {validAfter: NOW + 1n}},
     note: "LOWER bound: validAfter in the future — no coverage anywhere before A-064"},
    {code: "EVAL_ACTION_DEADLINE", expect: "VIOLATION", overrides: {action: {deadline: NOW - 1n}}},
    {code: "EVAL_VALUE_WITHIN_MANDATE", expect: "VIOLATION",
     overrides: {mandate: {maxNativeValueWei: VALUE - 1n}}},
    {code: "EVAL_VALUE_WITHIN_POLICY", expect: "VIOLATION",
     overrides: {policy: {maxNativeValueWei: VALUE - 1n}}},
    {code: "EVAL_VALUE_WITHIN_VAULT_CAP", expect: "VIOLATION",
     overrides: {state: {maxNativeValueWei: VALUE - 1n}}},
    {code: "EVAL_POLICY_OPERATION", expect: "VIOLATION", overrides: {policy: {allowedOperation: 1n}}},

    // A-068: AT the boundary, not one step outside it.
    //
    // Every ceiling and deadline row above perturbs the limit until it is VIOLATED, which pins
    // the comparison's direction and not its edge: `<=` could become `<` on all five and
    // nothing failed, so a value EXACTLY at a ceiling — the commonest real case, and the one a
    // mandate author would think they had authorised — would have been refused. Same shape as
    // the window bounds A-064 split by BOUND; this is that generalisation applied to the
    // conjunction's other side, the upper limits it left alone.
    {code: "EVAL_VALUE_WITHIN_MANDATE", expect: "PASS",
     overrides: {mandate: {maxNativeValueWei: VALUE}}, note: "value EXACTLY at the ceiling"},
    {code: "EVAL_VALUE_WITHIN_POLICY", expect: "PASS",
     overrides: {policy: {maxNativeValueWei: VALUE}}, note: "value EXACTLY at the ceiling"},
    {code: "EVAL_VALUE_WITHIN_VAULT_CAP", expect: "PASS",
     overrides: {state: {maxNativeValueWei: VALUE}}, note: "value EXACTLY at the vault cap"},
    {code: "EVAL_ACTION_DEADLINE", expect: "PASS",
     overrides: {action: {deadline: NOW}}, note: "now EXACTLY at the deadline"},
    {code: "EVAL_CALLDATA_UNDECODABLE", expect: "UNRESOLVED",
     overrides: {callData: "0xdeadbeef" as Hex}},
    {code: "EVAL_SELECTOR_BOUND", expect: "VIOLATION", overrides: {mandate: {selector: "0x095ea7b3"}}},
    {code: "EVAL_PURCHASE_RESOURCE", expect: "VIOLATION",
     overrides: {callData: purchaseCalldata(keccak256(stringToBytes("premium-monthly")))}},
    {code: "EVAL_PURCHASE_BENEFICIARY", expect: "VIOLATION",
     overrides: {callData: purchaseCalldata(RESOURCE, OTHER)}},
    {code: "EVAL_PURCHASE_DURATION", expect: "VIOLATION",
     overrides: {callData: purchaseCalldata(RESOURCE, OWNER, 60n)}},
    {code: "EVAL_PURCHASE_RECURRENCE", expect: "VIOLATION",
     overrides: {callData: purchaseCalldata(RESOURCE, OWNER, DURATION, true)}},
    {code: "EVAL_APPROVAL_CEILING", expect: "VIOLATION",
     overrides: {target: DEMO_ERC20, callData: approveCalldata(OWNER, 1n),
                 mandate: {target: DEMO_ERC20, selector: "0x095ea7b3"}}},
    {code: "EVAL_APPROVAL_SPENDER", expect: "VIOLATION",
     overrides: {target: DEMO_ERC20, callData: approveCalldata(OTHER, 0n),
                 mandate: {target: DEMO_ERC20, selector: "0x095ea7b3"}}},
    {code: "EVAL_SIMULATION_UNAVAILABLE", expect: "UNRESOLVED", overrides: {simulation: null}},
    {code: "EVAL_SIMULATION_SUCCEEDS", expect: "VIOLATION",
     overrides: {simulation: {outcome: {status: "revert", revertReason: "ZeroDuration"}}}},
    {code: "EVAL_CALL_GRAPH_EXPECTED", expect: "VIOLATION",
     overrides: {simulation: {internalCalls: [{from: DEMO_PAY, to: OTHER, type: "CALL"}]}}},
    {code: "EVAL_SIM_CALL_TRACE_UNAVAILABLE", expect: "UNRESOLVED",
     overrides: {simulation: {unresolvedChecks: ["SIM_CALL_TRACE_UNAVAILABLE"]}}},
    {code: "EVAL_NATIVE_DELTA_UNOBSERVED", expect: "UNRESOLVED",
     overrides: {simulation: {nativeBalanceDeltas: []}}},
    {code: "EVAL_NATIVE_DELTA_MATCHES_VALUE", expect: "VIOLATION",
     overrides: {simulation: {nativeBalanceDeltas: [
         {address: VAULT, before: 10n ** 18n, after: 10n ** 18n - 1n, delta: -1n}]}}},
    {code: "EVAL_ENTITLEMENT_UNOBSERVED", expect: "UNRESOLVED",
     overrides: {simulation: {entitlements: []}}},
    {code: "EVAL_ENTITLEMENT_ADVANCED", expect: "VIOLATION",
     overrides: {simulation: {entitlements: [{contract: DEMO_PAY, beneficiary: OWNER,
         resourceId: RESOURCE, expiryBefore: 5n, expiryAfter: 5n,
         recurringBefore: false, recurringAfter: false}]}}},
    {code: "EVAL_ENTITLEMENT_RECURRENCE", expect: "VIOLATION",
     overrides: {simulation: {entitlements: [{contract: DEMO_PAY, beneficiary: OWNER,
         resourceId: RESOURCE, expiryBefore: 0n, expiryAfter: NOW + DURATION,
         recurringBefore: false, recurringAfter: true}]}}},
    {code: "EVAL_SIM_STOP_IMPERSONATION_FAILED", expect: "UNRESOLVED",
     overrides: {simulation: {unresolvedChecks: ["SIM_STOP_IMPERSONATION_FAILED"]}}},
    {code: "EVAL_SIM_UNRECOGNISED", expect: "UNRESOLVED",
     overrides: {simulation: {unresolvedChecks: ["SIM_SOMETHING_NEW"]}}},
    {code: "EVAL_ALLOWANCE_EFFECT_UNOBSERVED", expect: "UNRESOLVED",
     overrides: {target: DEMO_ERC20, callData: approveCalldata(OWNER, 0n),
                 mandate: {target: DEMO_ERC20, selector: "0x095ea7b3"},
                 simulation: {allowanceDeltas: []}}},
    {code: "EVAL_ALLOWANCE_EFFECT_WITHIN_CEILING", expect: "VIOLATION",
     overrides: {simulation: {allowanceDeltas: [{token: DEMO_ERC20, owner: VAULT,
         spender: OTHER, before: 0n, after: 5n, delta: 5n}]}}},
];

describe("the conforming baseline", () => {
    it("produces ALLOW with every check passing", () => {
        const result = evaluate(fixture());
        assert.equal(
            result.verdict,
            "ALLOW",
            `baseline must conform; non-passing: ${JSON.stringify(
                result.checks.filter((c) => c.outcome !== "PASS"),
            )}`,
        );
        assert.deepEqual(result.reasonCodes, []);
    });
});

describe("every conformance check fires on its own trigger", () => {
    for (const c of CASES) {
        it(`${c.code} → ${c.expect}${c.note ? ` (${c.note})` : ""}`, () => {
            assert.equal(
                outcomeOf(c.overrides, c.code),
                c.expect,
                `${c.code} did not reach ${c.expect} under its own perturbation`,
            );
        });
    }
});

describe("the receipt STATES the reason it was reached for", () => {
    /**
     * A-068. The table above asserts each check's OUTCOME. Nothing asserted that the outcome
     * reaches the receipt, and `failingCodes` — the one function that carries it there — could
     * be narrowed from `outcome !== "PASS"` to `outcome === "VIOLATION"` with all 426 tests
     * green. Every UNRESOLVED code then vanished from `reasonCodes`, so a REVIEW receipt was
     * issued that stated NO reason, and its `reasonCodesHash` committed to the empty list.
     *
     * The receipt is the product. A verdict whose stated reasons are empty is the failure this
     * project's §5.4 reason codes exist to prevent, and it was reachable by deleting three
     * characters.
     *
     * Asserted for every non-PASS row rather than for Case 4 alone, because pinning the one
     * shape a reviewer exploited is this project's most-repeated defect.
     */
    for (const c of CASES.filter((x) => x.expect !== "PASS")) {
        it(`${c.code} appears in reasonCodes${c.note ? ` (${c.note})` : ""}`, () => {
            const result = evaluate(fixture(c.overrides));
            assert.ok(
                result.reasonCodes.includes(c.code),
                `${c.code} was ${c.expect} but the receipt's reasonCodes are ` +
                    `${JSON.stringify(result.reasonCodes)} — a verdict that does not state ` +
                    "the reason it was reached for",
            );
        });
    }

    it("a conforming baseline states no reasons at all", () => {
        // The paired positive: without it, `reasonCodes = every code` satisfies every row above.
        assert.deepEqual(evaluate(fixture()).reasonCodes, []);
    });
});

describe("the check table is exhaustive", () => {
    /**
     * WHAT THIS GUARD PROVES, STATED HONESTLY AFTER A D-017 REVIEWER NARROWED IT.
     *
     * It proves every declared code FIRES on some constructed input — that the check surface
     * is covered and a new code cannot arrive untested. It does NOT prove every code is
     * reachable through the COMPOSED pipeline, because the fixtures here hand-build
     * `SimulationResult` values and can therefore express states the real `simulateAction`
     * never returns. Several codes are in that category: the pipeline always populates
     * `nativeBalanceDeltas` for the watched set, so `EVAL_NATIVE_DELTA_UNOBSERVED` cannot
     * arise from it, and the same reasoning applies to the other `*_UNOBSERVED` codes.
     *
     * Those checks are still worth having — they are the fail-closed response to a caller
     * that supplies a degraded simulation, which is exactly what a future non-Anvil backend
     * or a partial-evidence path would do. But "covered" here means the surface, not
     * end-to-end reachability, and conflating the two would overclaim. Measuring which checks
     * a real corpus actually exercises is §7.3 ablation work, at S2.
     */
    it("has a case for every declared EVAL_ code", () => {
        // The structural guard. A check added without a case here fails this test rather
        // than joining the 24 an adversarial mutation had to find.
        const declared: string[] = [...EVAL_CODES].sort();
        const tested = [...new Set(CASES.map((c) => c.code))].sort();
        assert.deepEqual(
            declared.filter((c) => !tested.includes(c)),
            [],
            "conformance checks declared but never triggered by any test",
        );
        assert.deepEqual(
            tested.filter((c) => !declared.includes(c)),
            [],
            "tests reference conformance checks that no longer exist",
        );
    });

    it("declares every code the engine can actually emit", () => {
        // The other direction: a code emitted but not declared would escape EVAL_CODES and
        // therefore escape the exhaustiveness check above.
        const emitted = new Set<string>();
        for (const c of [{overrides: {}}, ...CASES]) {
            for (const r of runChecks(fixture(c.overrides))) emitted.add(r.code);
        }
        const declaredSet = new Set<string>(EVAL_CODES);
        const undeclared = [...emitted].filter((c) => !declaredSet.has(c));
        assert.deepEqual(undeclared, [], "codes emitted but missing from EVAL_CODES");
    });
});
