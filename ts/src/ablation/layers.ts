import type {CheckResult, ConformanceInput, Verdict} from "../evaluate/checks.ts";
import {runChecks, verdictOf} from "../evaluate/checks.ts";
import {runBaseline, baselineVerdict, type BaselineConfig} from "./baseline.ts";

/**
 * §7.3 — the three detection configurations.
 *
 * §7 opens by saying why this exists: "Four demo paths alone cannot prove that the verdicts
 * are not hard-coded." The ablation is what turns the corpus into an argument — it measures
 * what each layer actually contributes rather than asserting that the whole stack is needed.
 *
 *   L1  representative policy baseline                              (§7.2)
 *   L2  policy + pinned-state execution and effect extraction
 *   L3  policy + mandate-to-effects conformance and bound receipts  (the full engine)
 *
 * L2 IS THE ONE THAT MATTERS, and it is the one an implementer is most tempted to skip.
 * Without it the ablation compares "cheap policy" against "everything we built" and cannot
 * say which half did the work. L2 answers a real question: how much of Sentinel's advantage
 * comes merely from EXECUTING the call and looking at the effects — which is a capability
 * several products have — versus from comparing those effects to a signed mandate, which is
 * the claim §4.2 Case 3 rests on.
 *
 * L2 IS BUILT BY SUBTRACTION FROM THE REAL ENGINE, and L1 is not. That asymmetry is
 * deliberate. L2 is genuinely "the same engine minus the mandate-purpose checks", so
 * subtraction models it faithfully. L1 has different semantics — an allowlist is not a
 * mandate binding — so subtraction would misrepresent it, and `baseline.ts` implements it
 * separately for that reason.
 */

/**
 * The mandate-to-effects checks: what L3 has and L2 does not.
 *
 * These are the codes that compare the decoded call and its simulated effects against the
 * SIGNED MANDATE's purpose fields — resource, beneficiary, duration, recurrence — plus the
 * mandate-derived bindings and ceilings. §7.2 names exactly this set as what the baseline
 * lacks: "No resource, beneficiary, duration, recurrence, or post-state constraint."
 *
 * Listed explicitly rather than derived by prefix, because a prefix rule would silently
 * absorb any future code and quietly change what the ablation measures.
 */
export const MANDATE_CONFORMANCE_CODES: ReadonlySet<string> = new Set([
    "EVAL_PURCHASE_RESOURCE",
    "EVAL_PURCHASE_BENEFICIARY",
    "EVAL_PURCHASE_DURATION",
    "EVAL_PURCHASE_RECURRENCE",
    "EVAL_ENTITLEMENT_ADVANCED",
    "EVAL_ENTITLEMENT_RECURRENCE",
    "EVAL_ENTITLEMENT_UNOBSERVED",
    "EVAL_APPROVAL_SPENDER",
    "EVAL_TARGET_BOUND",
    "EVAL_SELECTOR_BOUND",
    "EVAL_VALUE_WITHIN_MANDATE",
    "EVAL_TARGET_CODE_IDENTITY",
    "EVAL_ACTION_BINDS_MANDATE_AND_POLICY",
    "EVAL_MANDATE_BINDS_POLICY",
    "EVAL_MANDATE_ACTIVE",
    "EVAL_MANDATE_WINDOW",
    "EVAL_MANDATE_PRINCIPAL_IS_OWNER",
    "EVAL_CALLDATA_BINDING",
]);

export type LayerName = "L1_baseline" | "L2_policy_plus_effects" | "L3_full_conformance";

export interface LayerResult {
    layer: LayerName;
    verdict: Verdict;
    checks: CheckResult[];
    failing: string[];
    /** Wall-clock microseconds for the deterministic decision, excluding simulation I/O. */
    micros: number;
}

function failingOf(checks: CheckResult[]): string[] {
    return checks
        .filter((c) => c.outcome !== "PASS")
        .map((c) => c.code)
        .sort();
}

/**
 * Run one layer against one already-simulated fixture.
 *
 * The simulation is performed ONCE by the caller and shared across layers. Two reasons, and
 * the second is the load-bearing one: re-simulating per layer would triple the corpus run
 * time, and — because L1 does not simulate at all — timing each layer's own simulation would
 * make the latency comparison measure Anvil rather than the decision. §7.3 asks for
 * "deterministic decision latency", so that is what is timed: the checks and the fold.
 */
export function runLayer(
    layer: LayerName,
    input: ConformanceInput,
    baselineConfig: BaselineConfig,
): LayerResult {
    const started = process.hrtime.bigint();

    let verdict: Verdict;
    let checks: CheckResult[];

    if (layer === "L1_baseline") {
        // L1 never consults the simulation, so it is given an input with none. Passing the
        // real one and trusting the implementation not to look would be an honour system.
        checks = runBaseline({...input, simulation: null}, baselineConfig);
        verdict = baselineVerdict(checks);
    } else if (layer === "L2_policy_plus_effects") {
        checks = runChecks(input).filter((c) => !MANDATE_CONFORMANCE_CODES.has(c.code));
        verdict = verdictOf(checks, input.policy);
    } else {
        checks = runChecks(input);
        verdict = verdictOf(checks, input.policy);
    }

    const micros = Number(process.hrtime.bigint() - started) / 1000;
    return {layer, verdict, checks, failing: failingOf(checks), micros};
}

export const LAYERS: readonly LayerName[] = [
    "L1_baseline",
    "L2_policy_plus_effects",
    "L3_full_conformance",
];

export const LAYER_DESCRIPTIONS: Record<LayerName, string> = {
    L1_baseline:
        "Representative policy baseline (§7.2): exact chain and vault, allowlisted targets and " +
        "selectors, native-value ceiling, direct maximum-approval block. No resource, " +
        "beneficiary, duration, recurrence, or post-state constraint. Separate implementation, " +
        "two verdicts (allow/block), no simulation.",
    L2_policy_plus_effects:
        "Policy plus pinned-state execution and effect extraction: the full engine with the " +
        "mandate-to-effects conformance checks removed. Sees simulated effects — balance and " +
        "allowance deltas, revert, call trace — but never compares them to the signed mandate's " +
        "purpose fields.",
    L3_full_conformance:
        "Policy plus mandate-to-effects conformance and bound receipts: the full engine, " +
        "unmodified.",
};
