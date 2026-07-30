import type {DecodeResult} from "../decode/index.ts";
import type {SimulationResult} from "../simulate/index.ts";
import type {VaultState} from "../signer/vault.ts";
import type {
    ActionPayload,
    Hex,
    MandatePayload,
    PolicyPayload,
} from "../signer/protocol.ts";
import {hashCallData, hashMandate, hashPolicy} from "./hashes.ts";

/**
 * The deterministic conformance checks (§5.7, §9 step 6).
 *
 * THE VERDICT RULE, taken verbatim from §5.2: "Mandate and policy constraints are
 * intersected. Any failed rule blocks. Any unknown required check reviews. Automatic allow
 * requires every required check to pass."
 *
 * So every check returns one of three outcomes, and the verdict is a fold over them:
 *
 *   VIOLATION  — a rule was evaluated and failed            → BLOCK
 *   UNRESOLVED — a required check could not be evaluated    → governed by policy.failureMode
 *   PASS       — evaluated and satisfied
 *
 * A single VIOLATION blocks regardless of anything else. With no violations, any UNRESOLVED
 * yields REVIEW when `policy.failureMode` is REVIEW and BLOCK when it is FAIL_CLOSED. Only
 * an all-PASS evaluation can produce ALLOW, which is §3.3(8) — "missing or conflicting
 * state, unsupported calls, undecodable calldata, stale mandate or policy, code-identity
 * mismatch, or critical dependency failure never produces automatic allow" — expressed as
 * a fold rather than as a checklist someone can forget an item from.
 *
 * ON THE TENSION BETWEEN §5.2's PROSE AND `failureMode` (recorded as A-020): §5.2 says
 * "any unknown required check reviews", while `PolicyPayload.failureMode` exists precisely
 * to choose between FAIL_CLOSED and REVIEW for that case. Read together, the prose
 * describes the REVIEW setting and the field parameterises it; the field governs here.
 * A consequence worth stating plainly because it shapes the demo: **§4.2 Case 4 expects a
 * REVIEW receipt, so the Case 4 policy must set `failureMode = REVIEW`.** Under a
 * FAIL_CLOSED policy the identical evidence uncertainty blocks — which is a legitimate
 * configuration and a different demonstration.
 *
 * WHAT THIS FILE IS NOT. Its own test suite is not its bar. HANDOFF's verification
 * partition is explicit: the conformance engine is "cheap to run, expensive to trust — its
 * bar is the independently labeled corpus, never its own suite (self-written tests encode
 * the same misunderstanding twice)". The tests here demonstrate the mechanism and pin
 * regressions; they are not evidence that the verdicts are correct. That evidence is the
 * §9 step 8 corpus, labelled under D-011 by an agent with no implementation context.
 */

/**
 * Every code this engine can emit.
 *
 * Declared as an enumerable list, not left implicit in the `results.push` calls, so a test
 * can assert that each one is actually reachable by some case. That is the lesson from
 * A-016: the signer had 31 checks of which 22 were exercised by nothing, and mutation
 * testing could not reveal it because the mutation set was written from the same reading of
 * the code as the tests. Enumerating the declared surface is what makes coverage a
 * structural property instead of a hope. `evaluate.checks.test.ts` fails if this list and
 * the tested set diverge in either direction.
 */
export const EVAL_CODES = [
    "EVAL_ACTION_BINDS_MANDATE_AND_POLICY",
    "EVAL_ACTION_DEADLINE",
    "EVAL_ALLOWANCE_EFFECT_UNOBSERVED",
    "EVAL_ALLOWANCE_EFFECT_WITHIN_CEILING",
    "EVAL_APPROVAL_CEILING",
    "EVAL_APPROVAL_SPENDER",
    "EVAL_CALLDATA_BINDING",
    "EVAL_CALLDATA_UNDECODABLE",
    "EVAL_CALL_GRAPH_EXPECTED",
    "EVAL_CHAIN_BOUND",
    "EVAL_ENTITLEMENT_ADVANCED",
    "EVAL_ENTITLEMENT_RECURRENCE",
    "EVAL_ENTITLEMENT_UNOBSERVED",
    "EVAL_MANDATE_ACTIVE",
    "EVAL_MANDATE_BINDS_POLICY",
    "EVAL_MANDATE_PRINCIPAL_IS_OWNER",
    "EVAL_MANDATE_WINDOW",
    "EVAL_NATIVE_DELTA_MATCHES_VALUE",
    "EVAL_NATIVE_DELTA_UNOBSERVED",
    "EVAL_NONCE_CURRENT",
    "EVAL_OPERATION_SUPPORTED",
    "EVAL_POLICY_ACTIVE",
    "EVAL_POLICY_OPERATION",
    "EVAL_POLICY_WINDOW",
    "EVAL_PURCHASE_BENEFICIARY",
    "EVAL_PURCHASE_DURATION",
    "EVAL_PURCHASE_RECURRENCE",
    "EVAL_PURCHASE_RESOURCE",
    "EVAL_SELECTOR_BOUND",
    "EVAL_SIM_CALL_TRACE_UNAVAILABLE",
    "EVAL_SIM_STOP_IMPERSONATION_FAILED",
    "EVAL_SIM_UNRECOGNISED",
    "EVAL_SIMULATION_SUCCEEDS",
    "EVAL_SIMULATION_UNAVAILABLE",
    "EVAL_TARGET_BOUND",
    "EVAL_TARGET_CODE_IDENTITY",
    "EVAL_VALUE_WITHIN_MANDATE",
    "EVAL_VALUE_WITHIN_POLICY",
    "EVAL_VALUE_WITHIN_VAULT_CAP",
    "EVAL_VAULT_BOUND",
    "EVAL_VAULT_NOT_PAUSED",
] as const;

export type EvalCode = (typeof EVAL_CODES)[number];

export type CheckOutcome = "PASS" | "VIOLATION" | "UNRESOLVED";

export interface CheckResult {
    /** Stable reason code. Appears in the receipt's `reasonCodesHash` when not PASS. */
    code: string;
    outcome: CheckOutcome;
    detail: string;
}

export type Verdict = "ALLOW" | "REVIEW" | "BLOCK";

/**
 * Pipeline `unresolvedChecks` codes, mapped to declared evaluator codes.
 *
 * Explicit so every code the engine can emit appears in `EVAL_CODES` and is therefore
 * covered by the exhaustiveness test.
 */
const SIM_CODE_MAP: Record<string, string> = {
    SIM_CALL_TRACE_UNAVAILABLE: "EVAL_SIM_CALL_TRACE_UNAVAILABLE",
    SIM_STOP_IMPERSONATION_FAILED: "EVAL_SIM_STOP_IMPERSONATION_FAILED",
};

/** §5.2 FailureMode: 0 = FAIL_CLOSED, 1 = REVIEW. */
const FAILURE_MODE_REVIEW = 1n;
const OPERATION_CALL = 0n;

export interface ConformanceInput {
    mandate: MandatePayload;
    policy: PolicyPayload;
    action: ActionPayload;
    callData: Hex;
    decode: DecodeResult;
    simulation: SimulationResult | null;
    vaultState: VaultState;
    now: bigint;
}

const pass = (code: string, detail = ""): CheckResult => ({code, outcome: "PASS", detail});
const violation = (code: string, detail: string): CheckResult => ({
    code,
    outcome: "VIOLATION",
    detail,
});
const unresolved = (code: string, detail: string): CheckResult => ({
    code,
    outcome: "UNRESOLVED",
    detail,
});

/** `assert`-style helper: PASS when the condition holds, VIOLATION otherwise. */
function require_(condition: boolean, code: string, detail: string): CheckResult {
    return condition ? pass(code) : violation(code, detail);
}

/**
 * Run every supported deterministic check (§5.7).
 *
 * Returns ALL results, passes included, because the evidence bundle records what was
 * checked and not merely what failed — a bundle that lists only failures cannot distinguish
 * "this check passed" from "this check was never run", and §5.6's `policyChecks` is meant
 * to answer exactly that.
 */
export function runChecks(input: ConformanceInput): CheckResult[] {
    const {mandate, policy, action, callData, decode, simulation, vaultState, now} = input;
    const results: CheckResult[] = [];

    // --- §5.7: active owner, mandate, policy, signer -----------------------
    const mandateHash = hashMandate(mandate);
    const policyHash = hashPolicy(policy);

    results.push(
        require_(
            vaultState.activeMandateHash !== `0x${"00".repeat(32)}` &&
                mandateHash === vaultState.activeMandateHash,
            "EVAL_MANDATE_ACTIVE",
            `presented mandate ${mandateHash} is not the vault's active ${vaultState.activeMandateHash}`,
        ),
        require_(
            vaultState.activePolicyHash !== `0x${"00".repeat(32)}` &&
                policyHash === vaultState.activePolicyHash,
            "EVAL_POLICY_ACTIVE",
            `presented policy ${policyHash} is not the vault's active ${vaultState.activePolicyHash}`,
        ),
        require_(
            mandate.principal.toLowerCase() === vaultState.owner.toLowerCase(),
            "EVAL_MANDATE_PRINCIPAL_IS_OWNER",
            `mandate principal ${mandate.principal} is not vault owner ${vaultState.owner}`,
        ),
        require_(!vaultState.paused, "EVAL_VAULT_NOT_PAUSED", "the vault is paused"),
    );

    // --- §5.7: exact chain, vault, nonce, target, operation, value, selector, code hash ---
    results.push(
        require_(action.chainId === mandate.chainId, "EVAL_CHAIN_BOUND", "action/mandate chain differ"),
        require_(
            action.vault.toLowerCase() === mandate.vault.toLowerCase(),
            "EVAL_VAULT_BOUND",
            "action/mandate vault differ",
        ),
        require_(
            action.actionNonce === vaultState.actionNonce,
            "EVAL_NONCE_CURRENT",
            `action nonce ${action.actionNonce} is not the vault's ${vaultState.actionNonce}`,
        ),
        require_(
            action.target.toLowerCase() === mandate.target.toLowerCase(),
            "EVAL_TARGET_BOUND",
            `action target ${action.target} is not the mandate's ${mandate.target}`,
        ),
        require_(
            action.operation === OPERATION_CALL,
            "EVAL_OPERATION_SUPPORTED",
            `operation ${action.operation} is not CALL`,
        ),
        require_(
            hashCallData(callData) === action.dataHash,
            "EVAL_CALLDATA_BINDING",
            "action.dataHash does not match the calldata",
        ),
        require_(
            action.mandateHash === mandateHash && action.policyHash === policyHash,
            "EVAL_ACTION_BINDS_MANDATE_AND_POLICY",
            "action does not bind the presented mandate and policy",
        ),
        require_(
            mandate.policyHash === policyHash,
            "EVAL_MANDATE_BINDS_POLICY",
            "the mandate names a different policy",
        ),
    );

    // Code identity (§5.7, §3.3(8)) — UNRESOLVED on mismatch, deliberately NOT a violation.
    //
    // §4.2 Case 4 is explicit about why: "The target code hash changes... Sentinel does not
    // label the target malicious. It reports insufficient evidence for automatic approval.
    // Expected result: review." A changed code hash means Sentinel no longer knows what the
    // target does, which is an evidence gap rather than a proven breach of the mandate.
    // Classifying it as a violation would hard-block Case 4 and, worse, would state
    // something about the target that Sentinel has not established.
    //
    // §3.3(8) agrees by listing code-identity mismatch among the conditions that never
    // produce an *automatic allow* — a bar UNRESOLVED already clears — rather than among
    // conditions that must block outright. Under a FAIL_CLOSED policy it still blocks; that
    // is the policy author's choice, not the engine's verdict.
    results.push(
        mandate.targetCodeHash.toLowerCase() === vaultState.targetCodeHash.toLowerCase()
            ? pass("EVAL_TARGET_CODE_IDENTITY")
            : unresolved(
                  "EVAL_TARGET_CODE_IDENTITY",
                  `target code hash ${vaultState.targetCodeHash} is not the pinned ` +
                      `${mandate.targetCodeHash}; the target's behaviour is no longer established`,
              ),
    );

    // --- §5.7: validity windows -------------------------------------------
    results.push(
        require_(
            now >= mandate.validAfter && now <= mandate.validUntil,
            "EVAL_MANDATE_WINDOW",
            `now ${now} is outside the mandate window`,
        ),
        require_(
            now >= policy.validAfter && now <= policy.validUntil,
            "EVAL_POLICY_WINDOW",
            `now ${now} is outside the policy window`,
        ),
        require_(now <= action.deadline, "EVAL_ACTION_DEADLINE", "the action deadline has passed"),
    );

    // --- §5.7: native-value ceiling, intersected (§5.2) --------------------
    // "Mandate and policy constraints are intersected" — the binding limit is the lower of
    // the two, plus the vault's own immutable cap, and the action must satisfy all three.
    results.push(
        require_(
            action.valueWei <= mandate.maxNativeValueWei,
            "EVAL_VALUE_WITHIN_MANDATE",
            `value ${action.valueWei} exceeds mandate ceiling ${mandate.maxNativeValueWei}`,
        ),
        require_(
            action.valueWei <= policy.maxNativeValueWei,
            "EVAL_VALUE_WITHIN_POLICY",
            `value ${action.valueWei} exceeds policy ceiling ${policy.maxNativeValueWei}`,
        ),
        require_(
            action.valueWei <= vaultState.maxNativeValueWei,
            "EVAL_VALUE_WITHIN_VAULT_CAP",
            `value ${action.valueWei} exceeds the vault's immutable cap`,
        ),
        require_(
            policy.allowedOperation === action.operation,
            "EVAL_POLICY_OPERATION",
            "the policy does not allow this operation",
        ),
    );

    // --- §3.3(8): undecodable calldata never produces an automatic allow ---
    if (!decode.ok) {
        results.push(
            unresolved("EVAL_CALLDATA_UNDECODABLE", `${decode.code}: ${decode.detail}`),
        );
    } else {
        const decoded = decode.decoded;
        results.push(
            require_(
                decode.selector.toLowerCase() === mandate.selector.toLowerCase(),
                "EVAL_SELECTOR_BOUND",
                `selector ${decode.selector} is not the mandate's ${mandate.selector}`,
            ),
        );

        // --- §5.7: DemoPay resource, beneficiary, duration, recurrence -----
        //
        // THIS IS CASE 3. The action can be mechanically valid — right target, right
        // selector, value inside every ceiling, execution succeeds — and still buy the wrong
        // thing. Nothing above catches that; these four checks are the whole difference
        // between a policy engine and a mandate-conformance engine, and they are the reason
        // §7.3's ablation exists to measure what each layer contributes.
        if (decoded.schema === "DemoPay.purchase") {
            results.push(
                require_(
                    decoded.resourceId.toLowerCase() === mandate.resourceId.toLowerCase(),
                    "EVAL_PURCHASE_RESOURCE",
                    `purchases ${decoded.resourceId}, mandate authorises ${mandate.resourceId}`,
                ),
                require_(
                    decoded.beneficiary.toLowerCase() === mandate.beneficiary.toLowerCase(),
                    "EVAL_PURCHASE_BENEFICIARY",
                    `beneficiary ${decoded.beneficiary}, mandate authorises ${mandate.beneficiary}`,
                ),
                require_(
                    decoded.durationSeconds === mandate.durationSeconds,
                    "EVAL_PURCHASE_DURATION",
                    `duration ${decoded.durationSeconds}, mandate authorises ${mandate.durationSeconds}`,
                ),
                require_(
                    !decoded.recurring || mandate.recurringAllowed,
                    "EVAL_PURCHASE_RECURRENCE",
                    "recurrence requested but the mandate forbids it",
                ),
            );
        }

        // --- §5.7: DemoERC20 approval parameters and allowance ceiling -----
        if (decoded.schema === "DemoERC20.approve") {
            // An approval is never the Case 1 purchase shape. It is in scope only because
            // §4 keeps DemoERC20 for the injection fixture, so it can conform to a mandate
            // that actually authorises an approval — and violates one that does not.
            results.push(
                require_(
                    decoded.amount <= policy.maxAllowanceIncreaseBaseUnits,
                    "EVAL_APPROVAL_CEILING",
                    `approves ${decoded.amount}, policy ceiling is ` +
                        `${policy.maxAllowanceIncreaseBaseUnits}`,
                ),
                require_(
                    decoded.spender.toLowerCase() === mandate.beneficiary.toLowerCase(),
                    "EVAL_APPROVAL_SPENDER",
                    `spender ${decoded.spender} is not the mandate's beneficiary`,
                ),
            );
        }
    }

    // --- §5.7: effects, from the simulation --------------------------------
    if (simulation === null) {
        // §3.3(8): critical dependency failure. Never an automatic allow.
        results.push(unresolved("EVAL_SIMULATION_UNAVAILABLE", "no simulation was produced"));
    } else {
        results.push(
            require_(
                simulation.outcome.status === "success",
                "EVAL_SIMULATION_SUCCEEDS",
                `simulated execution reverted: ${simulation.outcome.revertReason ?? "no reason"}`,
            ),
        );

        // Unexpected internal calls (§3.3(11)). DemoPay makes no external calls, so the
        // conforming call graph is empty.
        results.push(
            require_(
                simulation.internalCalls.length === 0,
                "EVAL_CALL_GRAPH_EXPECTED",
                `${simulation.internalCalls.length} unexpected internal call(s)`,
            ),
        );

        // Every unresolved check from the pipeline travels into the verdict rather than
        // being summarised away.
        //
        // Mapped EXPLICITLY rather than by string concatenation. A dynamically built
        // `EVAL_${code}` escapes `EVAL_CODES`, and therefore escapes the exhaustiveness test
        // that exists to stop checks going untested — which is exactly the hole that let 24
        // of these codes ship uncovered. An unrecognised pipeline code still travels, under
        // a declared catch-all, so nothing is silently dropped either.
        for (const code of simulation.unresolvedChecks) {
            const mapped = SIM_CODE_MAP[code];
            results.push(
                mapped === undefined
                    ? unresolved("EVAL_SIM_UNRECOGNISED", `the effect pipeline reported ${code}`)
                    : unresolved(mapped, "the effect pipeline could not establish this"),
            );
        }

        // Native value actually moved, and only by what was authorised.
        const vaultDelta = simulation.nativeBalanceDeltas.find(
            (d) => d.address.toLowerCase() === action.vault.toLowerCase(),
        );
        if (vaultDelta === undefined) {
            results.push(unresolved("EVAL_NATIVE_DELTA_UNOBSERVED", "no vault balance delta observed"));
        } else if (simulation.outcome.status === "success") {
            results.push(
                require_(
                    vaultDelta.delta === -action.valueWei,
                    "EVAL_NATIVE_DELTA_MATCHES_VALUE",
                    `vault balance moved ${vaultDelta.delta}, action authorised -${action.valueWei}`,
                ),
            );
        }

        // Simulated entitlement state must match what the mandate authorised (§5.7: "an
        // event alone is not proof of entitlement; conformance checks the resulting state").
        if (decode.ok && decode.decoded.schema === "DemoPay.purchase") {
            const ent = simulation.entitlements[0];
            if (ent === undefined) {
                results.push(
                    unresolved("EVAL_ENTITLEMENT_UNOBSERVED", "no entitlement state was inspected"),
                );
            } else if (simulation.outcome.status === "success") {
                results.push(
                    require_(
                        ent.expiryAfter > ent.expiryBefore,
                        "EVAL_ENTITLEMENT_ADVANCED",
                        "the purchase did not advance the entitlement",
                    ),
                    require_(
                        !ent.recurringAfter || mandate.recurringAllowed,
                        "EVAL_ENTITLEMENT_RECURRENCE",
                        "resulting state enables recurrence the mandate forbids",
                    ),
                );
            }
        }

        // Allowance ceiling as an EFFECT, not merely as a decoded parameter. §7.1 lists
        // "finite, oversized, and unlimited approvals" as distinct classes, and the observed
        // post-state is what a receipt can honestly claim.
        const allowance = simulation.allowanceDeltas[0];
        // An approve action whose allowance effect was never observed must NOT reach ALLOW on
        // silence. Every other effect class has an explicit UNRESOLVED counterpart
        // (EVAL_NATIVE_DELTA_UNOBSERVED, EVAL_ENTITLEMENT_UNOBSERVED); this one had none, so a
        // missing measurement simply emitted no check at all — §3.3(8) says missing state never
        // produces an automatic allow, and an absent check is exactly missing state.
        if (
            allowance === undefined &&
            decode.ok &&
            decode.decoded.schema === "DemoERC20.approve" &&
            simulation.outcome.status === "success"
        ) {
            results.push(
                unresolved("EVAL_ALLOWANCE_EFFECT_UNOBSERVED", "no allowance delta was inspected"),
            );
        }
        if (allowance !== undefined && simulation.outcome.status === "success") {
            results.push(
                require_(
                    allowance.after <= policy.maxAllowanceIncreaseBaseUnits,
                    "EVAL_ALLOWANCE_EFFECT_WITHIN_CEILING",
                    `resulting allowance ${allowance.after} exceeds ceiling ` +
                        `${policy.maxAllowanceIncreaseBaseUnits}`,
                ),
            );
        }
    }

    return results;
}

/**
 * §5.2's fold. A single VIOLATION blocks; otherwise UNRESOLVED is governed by failureMode.
 */
export function verdictOf(results: CheckResult[], policy: PolicyPayload): Verdict {
    if (results.some((r) => r.outcome === "VIOLATION")) return "BLOCK";
    if (results.some((r) => r.outcome === "UNRESOLVED")) {
        return policy.failureMode === FAILURE_MODE_REVIEW ? "REVIEW" : "BLOCK";
    }
    return "ALLOW";
}

/** The codes that go into the receipt: everything that did not pass. */
export function failingCodes(results: CheckResult[]): string[] {
    return [...new Set(results.filter((r) => r.outcome !== "PASS").map((r) => r.code))].sort();
}

export {hashAction, hashMandate, hashPolicy} from "./hashes.ts";
