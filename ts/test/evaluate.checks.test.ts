import {describe, it} from "node:test";
import assert from "node:assert/strict";
import {getAddress, keccak256, stringToBytes, toBytes} from "viem";
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
        observedBlockHash: keccak256(stringToBytes("block 100")),
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

    // A-072: THE OTHER SIX EDGES. A-068's comment above says "`<=` could become `<` on all
    // five" and then pins FOUR — `EVAL_APPROVAL_CEILING`, the fifth `D-06` named by line, got
    // no row. A mechanical sweep of every comparison in `checks.ts` (8 sites, 10 edges) found
    // that four more were unpinned as well: A-064 split the two window checks by BOUND but gave
    // each bound only a VIOLATION row, which pins the DIRECTION and not the EDGE.
    //
    // Measured before these rows existed, each with the pinned deadline edge as a control that
    // correctly failed: all six mutations below left this file at `pass 96 / fail 0`.
    //
    // The harm is the same one A-068 states for itself, and it is not hypothetical: a value or
    // a timestamp EXACTLY at a declared limit is the commonest real case and the one a mandate
    // author would believe they had authorised. Every one of these flips it to a refusal.
    {code: "EVAL_MANDATE_WINDOW", expect: "PASS", overrides: {mandate: {validAfter: NOW}},
     note: "LOWER edge: now EXACTLY at validAfter — the first instant of force"},
    {code: "EVAL_MANDATE_WINDOW", expect: "PASS", overrides: {mandate: {validUntil: NOW}},
     note: "UPPER edge: now EXACTLY at validUntil — the last instant of force"},
    {code: "EVAL_POLICY_WINDOW", expect: "PASS", overrides: {policy: {validAfter: NOW}},
     note: "LOWER edge: now EXACTLY at validAfter"},
    {code: "EVAL_POLICY_WINDOW", expect: "PASS", overrides: {policy: {validUntil: NOW}},
     note: "UPPER edge: now EXACTLY at validUntil"},
    {code: "EVAL_APPROVAL_CEILING", expect: "PASS",
     overrides: {target: DEMO_ERC20, callData: approveCalldata(OWNER, 5n),
                 mandate: {target: DEMO_ERC20, selector: "0x095ea7b3"},
                 policy: {maxAllowanceIncreaseBaseUnits: 5n}},
     note: "D-06's FIFTH comparison, named by line and left unpinned by A-068"},
    {code: "EVAL_ALLOWANCE_EFFECT_WITHIN_CEILING", expect: "PASS",
     overrides: {policy: {maxAllowanceIncreaseBaseUnits: 5n},
                 simulation: {allowanceDeltas: [{token: DEMO_ERC20, owner: VAULT,
                     spender: OTHER, before: 0n, after: 5n, delta: 5n}]}},
     note: "resulting allowance EXACTLY at the ceiling"},
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

describe("an unavailable call trace does not record a PASS (R2-F5)", () => {
    /**
     * R2-F5, D-055(e), CONFIRMED at MEDIUM. Repaired under D-057(4).
     *
     * THE ARGUMENT: **an empty list of observed internal calls means "none were seen", which
     * is the same value whether none occurred or nothing looked.** With the tracer
     * unavailable, `internalCalls` is `[]` and the check recorded a POSITIVE
     * `EVAL_CALL_GRAPH_EXPECTED: PASS` — signed into the receipt as though §3.3(11)'s defence
     * had been evaluated — on a run where it never was.
     *
     * The verdict was always protected; the RECORD was not. Both are asserted here, because
     * fixing the record while silently changing the verdict would be a different defect.
     */
    it("records UNRESOLVED, not PASS, when the trace is unavailable", () => {
        assert.equal(
            outcomeOf({simulation: {callTrace: null, internalCalls: [],
                                    unresolvedChecks: ["SIM_CALL_TRACE_UNAVAILABLE"]}},
                      "EVAL_CALL_GRAPH_EXPECTED"),
            "UNRESOLVED",
        );
    });

    it("still PASSes when the trace IS available and the graph is genuinely empty", () => {
        // The control. Without it, "always UNRESOLVED" satisfies the row above and the check
        // stops detecting anything.
        assert.equal(outcomeOf({}, "EVAL_CALL_GRAPH_EXPECTED"), "PASS");
    });

    it("still VIOLATES on a real unexpected internal call", () => {
        // The second control: the check must keep doing its actual job.
        assert.equal(
            outcomeOf({simulation: {internalCalls: [{from: VAULT, to: OTHER, type: "CALL"}]}},
                      "EVAL_CALL_GRAPH_EXPECTED"),
            "VIOLATION",
        );
    });
});

describe("binding comparisons are case- and field-pinned (D-10)", () => {
    /**
     * D-10, adjudicated CONFIRMED and accepted as a limit at LOW — **re-classified MEDIUM for
     * part (c) by John (D-056(a)) rather than left at LOW through an undocumented downgrade,
     * which is D-055's T2 applied to his own earlier acceptance.** Closed here.
     *
     * THE EVIDENCE STANDARD IS UNUSUAL AND JOHN STATED IT EXPLICITLY: *"The implementation is
     * currently correct, so the evidence here is that each mutation survived before the new
     * tests and is killed afterward — not that the clean implementation previously failed."*
     * All three mutations below passed the full 510-test suite before these tests existed.
     *
     * THE ARGUMENT: **a binding comparison must be pinned to the FIELD it names and to the
     * VALUE it names, independently of how the corpus happens to spell either.** The corpus is
     * single-case throughout — measured: 9 distinct addresses across all 50 fixtures, zero
     * non-lowercase occurrences — and ~~every fixture sets `principal === beneficiary`~~ **— FALSE, and `F024` is the counterexample (R3-F8). The corpus DOES distinguish them.** So the
     * corpus cannot distinguish a normalised comparison from an unnormalised one, nor the
     * beneficiary from the principal, and neither could anything else in the suite.
     *
     * WHY MIXED CASE IS NOT A CONTRIVANCE. EIP-55 checksummed addresses are mixed case by
     * construction and are what an LLM-produced proposal routinely contains — this
     * repository's own injection fixtures carry them, and `attest.ts` already had to be
     * repaired for exactly this reason once.
     */

    /**
     * Two different "same value, different spelling" transforms, because addresses and raw
     * hex are not interchangeable here.
     *
     * `upper` is for NON-ADDRESS hex — bytes32 and selectors — where any case is valid.
     *
     * `checksum` is for ADDRESSES. Upper-casing an address produces a string viem REJECTS as
     * failing EIP-55, so a probe built on it fails for the wrong reason and proves nothing
     * about case handling. The realistic mixed-case address IS the checksummed one, which is
     * what an EIP-55 wallet and an LLM-produced proposal both emit — and it is what `attest.ts`
     * had to be repaired for once already.
     */
    const upper = (a: Hex): Hex => ("0x" + a.slice(2).toUpperCase()) as Hex;
    const checksum = (a: Hex): Hex => getAddress(a) as Hex;

    /**
     * An address containing hex LETTERS, because the repository's own constants do not.
     *
     * `DEMO_PAY` is `0x2222…` — all digits — so upper-casing it is a no-op and a probe built
     * on it changes nothing while looking like it does. The first version of this test did
     * exactly that and asserted a difference that was not there; it failed loudly only because
     * the "did the probe move anything" guard below was written first. Keeping that guard.
     */
    const LETTERY: Hex = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd";

    it("matches a mixed-case TARGET against the mandate (mutation: drop normalisation)", () => {
        // The action names the target upper-cased, the mandate lower-cased. Same address, so
        // `EVAL_TARGET_BOUND` must PASS.
        assert.notEqual(upper(LETTERY), LETTERY, "the probe must actually change the spelling");
        assert.equal(
            outcomeOf(
                {action: {target: checksum(LETTERY)}, mandate: {target: LETTERY}},
                "EVAL_TARGET_BOUND",
            ),
            "PASS",
        );
    });

    it("matches a mixed-case SELECTOR against the mandate (mutation: drop normalisation)", () => {
        // The decoded selector comes from the calldata bytes and is lower case; the mandate
        // names the same selector upper-cased.
        const SEL: Hex = "0xc188528b";
        assert.notEqual(upper(SEL), SEL, "the probe must actually change the spelling");
        assert.equal(
            outcomeOf({mandate: {selector: upper(SEL)}}, "EVAL_SELECTOR_BOUND"),
            "PASS",
        );
    });

    /**
     * ALL NINE CASE-NORMALISATION SITES (R3-F8, D-055(e), CONFIRMED).
     *
     * The A-076 repair pinned **2 of 9** and recorded a premise that is FALSE: *"every fixture
     * sets `principal === beneficiary`"*. **`F024` is the counterexample** — principal
     * `0x0000…` against beneficiary `0xf39f…` — so the corpus DOES distinguish the two fields,
     * and a repair reasoning from "it cannot" was reasoning from a measurement nobody made.
     * That is `D-09(c)`'s refuted-basis defect, committed inside the fix for it.
     *
     * Each row upper-cases ONE side of ONE comparison. Same value, different spelling, so the
     * check must still PASS; a mutant dropping `.toLowerCase()` on either side fails the row
     * that names it.
     */
    const CASE_SITES: {code: string; note: string; overrides: Overrides}[] = [
        {code: "EVAL_MANDATE_PRINCIPAL_IS_OWNER", note: "principal vs vault owner",
         overrides: {mandate: {principal: checksum(LETTERY)}, state: {owner: LETTERY}}},
        {code: "EVAL_VAULT_BOUND", note: "action vault vs mandate vault",
         overrides: {action: {vault: checksum(LETTERY)}, mandate: {vault: LETTERY}}},
        {code: "EVAL_TARGET_BOUND", note: "action target vs mandate target",
         overrides: {action: {target: checksum(LETTERY)}, mandate: {target: LETTERY}}},
        {code: "EVAL_TARGET_CODE_IDENTITY", note: "mandate code hash vs observed code hash",
         // BOTH sides stated: the fixture derives `state.targetCodeHash` from the mandate, so
         // overriding only the mandate made both sides the SAME uppercase string and the probe
         // measured nothing. Caught by the mutation sweep, not by the test passing.
         overrides: {mandate: {targetCodeHash: upper(CODE_HASH)}, state: {targetCodeHash: CODE_HASH}}},
        {code: "EVAL_SELECTOR_BOUND", note: "decoded selector vs mandate selector",
         overrides: {mandate: {selector: upper("0xc188528b" as Hex)}}},
        {code: "EVAL_PURCHASE_RESOURCE", note: "decoded resource vs mandate resource",
         overrides: {mandate: {resourceId: upper(RESOURCE)}}},
        {code: "EVAL_PURCHASE_BENEFICIARY", note: "decoded beneficiary vs mandate beneficiary",
         // LETTERY, not OWNER: `OWNER` is 0x4444… — all digits — so checksumming it is a no-op
         // and the probe changed nothing. Three rows had this defect and all three survived
         // their mutation until the sweep exposed them.
         overrides: {callData: purchaseCalldata(RESOURCE, LETTERY),
                     mandate: {beneficiary: checksum(LETTERY)}}},
    ];

    // THE PROBE MUST MOVE SOMETHING. Four of these rows originally used all-digit constants
    // (`OWNER` is 0x4444…, `VAULT` is 0x1111…) where upper-casing and checksumming are both
    // no-ops, so the row passed while testing nothing and its mutant survived. This guard is
    // asserted per row rather than trusted.
    assert.notEqual(upper(CODE_HASH), CODE_HASH, "upper() must change a bytes32");
    assert.notEqual(checksum(LETTERY), LETTERY, "checksum() must change a letter-bearing address");

    for (const c of CASE_SITES) {
        it(`matches mixed case: ${c.note}`, () => {
            assert.equal(outcomeOf(c.overrides, c.code), "PASS",
                `${c.code} must be insensitive to how the same value is spelled`);
        });
    }

    it("matches a mixed-case approval spender against the mandate beneficiary", () => {
        assert.notEqual(checksum(LETTERY), LETTERY, "the probe must change the spelling");
        assert.equal(
            outcomeOf({target: DEMO_ERC20, callData: approveCalldata(LETTERY, 0n),
                       mandate: {target: DEMO_ERC20, selector: "0x095ea7b3" as Hex,
                                 beneficiary: checksum(LETTERY)}},
                      "EVAL_APPROVAL_SPENDER"),
            "PASS",
        );
    });

    it("matches a mixed-case native-delta address against the action vault", () => {
        // The ninth site: the observed balance delta is matched to the vault by address.
        // `action.vault` must be the letter-bearing address too, or both sides are 0x1111…
        // and the row proves nothing.
        assert.equal(
            outcomeOf({action: {vault: LETTERY}, mandate: {vault: LETTERY},
                       simulation: {nativeBalanceDeltas: [
                {address: checksum(LETTERY), before: 1000n, after: 0n, delta: -1000n}]}},
                      "EVAL_NATIVE_DELTA_MATCHES_VALUE"),
            "PASS",
        );
    });

    it("compares the PURCHASE beneficiary to the beneficiary, not the principal (R3-F8)", () => {
        // THE SECOND FIELD SWAP, thirty lines above the one A-076 fixed and left standing.
        // F024 is the corpus counterexample that makes it observable at all.
        const m = {principal: OWNER, beneficiary: OTHER};
        assert.equal(
            outcomeOf({callData: purchaseCalldata(RESOURCE, OTHER), mandate: m, state: {owner: OWNER}},
                      "EVAL_PURCHASE_BENEFICIARY"),
            "PASS",
            "a purchase for the mandate's beneficiary must conform",
        );
        assert.equal(
            outcomeOf({callData: purchaseCalldata(RESOURCE, OWNER), mandate: m, state: {owner: OWNER}},
                      "EVAL_PURCHASE_BENEFICIARY"),
            "VIOLATION",
            "a purchase for the PRINCIPAL, who is not the beneficiary, must not conform",
        );
    });

    it("compares the approval spender to the BENEFICIARY, not the principal (D-10(c))", () => {
        // The substantive half, and the one the adjudicator raised to MEDIUM. Every corpus
        // fixture sets principal === beneficiary, so `mandate.beneficiary` could be swapped
        // for `mandate.principal` with the whole suite green — the check would then be
        // enforcing the wrong field while still reporting EVAL_APPROVAL_SPENDER.
        //
        // Here they DIFFER, which is what makes the swap observable: an approval to the
        // beneficiary conforms, and an approval to the principal does not.
        const approvalMandate = {
            target: DEMO_ERC20,
            selector: "0x095ea7b3" as Hex,
            principal: OWNER,
            beneficiary: OTHER,
        };
        assert.equal(
            outcomeOf(
                {target: DEMO_ERC20, callData: approveCalldata(OTHER, 0n), mandate: approvalMandate,
                 state: {owner: OWNER}},
                "EVAL_APPROVAL_SPENDER",
            ),
            "PASS",
            "an approval to the mandate's beneficiary must conform",
        );
        // The paired negative. Without it, a check that always PASSes satisfies the row above.
        assert.equal(
            outcomeOf(
                {target: DEMO_ERC20, callData: approveCalldata(OWNER, 0n), mandate: approvalMandate,
                 state: {owner: OWNER}},
                "EVAL_APPROVAL_SPENDER",
            ),
            "VIOLATION",
            "an approval to the PRINCIPAL, who is not the beneficiary, must not conform",
        );
    });
});

describe("the evidence bundle records the INTERSECTED ceiling (D-09(c))", () => {
    /**
     * D-09(c), reopened 2026-08-18 and closed here (D-056(a)).
     *
     * THE ARGUMENT: **`expectedEffects.maxNativeValueWei` is what the bundle CLAIMS was
     * authorised, and §5.2 says "mandate and policy constraints are intersected" — so it must
     * be the LOWER of the two ceilings whichever side is lower, not whichever side the code
     * happens to name.**
     *
     * WHY THIS WAS ABLE TO GO MISSING. `evaluate/index.ts`'s `minOf` could be inverted to a
     * max and the entire suite stayed green: measured, 507/507 passing with the intersection
     * reversed. Neither committed corpus artifact catches it either — the labeller views omit
     * `expectedEffects` by construction, and the result files do not carry it — so the deep
     * gate's byte-for-byte comparisons are blind to it too. The field was read by nothing.
     *
     * THE CONSEQUENCE IS A FALSE STATEMENT IN THE PRODUCT, not a cosmetic one. Under the
     * inversion a bundle whose policy caps spending at 2e15 would attest that 1e18 was
     * authorised — five hundred times the real limit — and the D-010 verifier compares
     * `expectedEffects` to exactly this value.
     *
     * BOTH DIRECTIONS ARE ASSERTED, and that is what makes the test more than a restatement
     * of `minOf`. A test pinning only "mandate lower" passes against `return a` — the argument
     * needs the binding side to change places while the answer stays the lower one.
     *
     * NO CORPUS FIXTURE IS ADDED OR RELABELLED (D-056(a)). `F006` already supplies the
     * divergent case at the corpus level — mandate 1e18 against policy 2e15, verified by
     * walking all 50 committed fixtures: exactly one diverges. What was missing is an
     * assertion, not a fixture.
     */
    const LOW = 2n * 10n ** 15n;
    const HIGH = 10n ** 18n;

    /**
     * Read the value out of the CANONICAL BYTES rather than the in-memory bundle.
     *
     * Deliberate: `evidenceCanonical` is what `evidenceHash` commits to, what the signer
     * attests, and what the D-010 verifier parses. Asserting the object would leave a
     * serialisation that dropped or reshaped the field undetected.
     */
    const ceilingOf = (r: ReturnType<typeof evaluate>): unknown =>
        (JSON.parse(r.evidenceCanonical) as {expectedEffects: {maxNativeValueWei: unknown}})
            .expectedEffects.maxNativeValueWei;

    it("takes the POLICY ceiling when the policy is the tighter of the two (F006's shape)", () => {
        assert.equal(ceilingOf(evaluate(fixture({
            mandate: {maxNativeValueWei: HIGH},
            policy: {maxNativeValueWei: LOW},
        }))), LOW.toString());
    });

    it("takes the MANDATE ceiling when the mandate is the tighter of the two", () => {
        // The mirror. Without it, `maxNativeValueWei: policy.maxNativeValueWei` — a plausible
        // wrong implementation that ignores the mandate entirely — passes the row above.
        assert.equal(ceilingOf(evaluate(fixture({
            mandate: {maxNativeValueWei: LOW},
            policy: {maxNativeValueWei: HIGH},
        }))), LOW.toString());
    });

    it("reports the shared value when the two agree, which is the 49-of-50 corpus case", () => {
        assert.equal(ceilingOf(evaluate(fixture({
            mandate: {maxNativeValueWei: HIGH},
            policy: {maxNativeValueWei: HIGH},
        }))), HIGH.toString());
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
