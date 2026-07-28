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

/** Perturbations, one per declared code. Each changes exactly one dimension. */
const CASES: {code: string; expect: CheckOutcome; overrides: Overrides}[] = [
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
     overrides: {action: {mandateHash: keccak256(stringToBytes("stale"))}}},
    {code: "EVAL_MANDATE_BINDS_POLICY", expect: "VIOLATION",
     overrides: {mandate: {policyHash: keccak256(stringToBytes("unlinked"))}}},
    {code: "EVAL_TARGET_CODE_IDENTITY", expect: "UNRESOLVED",
     overrides: {state: {targetCodeHash: keccak256(stringToBytes("changed"))}}},
    {code: "EVAL_MANDATE_WINDOW", expect: "VIOLATION", overrides: {mandate: {validUntil: NOW - 1n}}},
    {code: "EVAL_POLICY_WINDOW", expect: "VIOLATION", overrides: {policy: {validUntil: NOW - 1n}}},
    {code: "EVAL_ACTION_DEADLINE", expect: "VIOLATION", overrides: {action: {deadline: NOW - 1n}}},
    {code: "EVAL_VALUE_WITHIN_MANDATE", expect: "VIOLATION",
     overrides: {mandate: {maxNativeValueWei: VALUE - 1n}}},
    {code: "EVAL_VALUE_WITHIN_POLICY", expect: "VIOLATION",
     overrides: {policy: {maxNativeValueWei: VALUE - 1n}}},
    {code: "EVAL_VALUE_WITHIN_VAULT_CAP", expect: "VIOLATION",
     overrides: {state: {maxNativeValueWei: VALUE - 1n}}},
    {code: "EVAL_POLICY_OPERATION", expect: "VIOLATION", overrides: {policy: {allowedOperation: 1n}}},
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
        it(`${c.code} → ${c.expect}`, () => {
            assert.equal(
                outcomeOf(c.overrides, c.code),
                c.expect,
                `${c.code} did not reach ${c.expect} under its own perturbation`,
            );
        });
    }
});

describe("the check table is exhaustive", () => {
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
