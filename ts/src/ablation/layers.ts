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
/**
 * The mandate-to-effects checks: what L3 has and L2 does not.
 *
 * THE CRITERION, ratified as D-034 and stated here because the previous version of this set
 * did not have one and drifted twice for that reason:
 *
 *   A code belongs here if, and only if, it compares the CALL or its SIMULATED EFFECTS
 *   against the mandate's PURPOSE fields — resource, beneficiary, duration, recurrence, and
 *   the post-state those imply. Everything else goes to L2: whether a valid mandate exists,
 *   whether the signed payload is intact, whether the target's code identity can be
 *   confirmed, and every ceiling or allowlist.
 *
 * That is §7.2's own sentence, and nothing more: "No resource, beneficiary, duration,
 * recurrence, or post-state constraint." L2 is defined as the full engine with the
 * mandate-to-effects checks removed — so L2 HAS the mandate. It simply never asks what the
 * mandate was FOR. An arm holding a mandate can perfectly well check that the mandate is
 * active, in window, bound to the active policy, and names the owner as principal; withholding
 * those from it modelled no product and inflated the contribution figure with work that has
 * nothing to do with purpose.
 *
 * WHAT THIS COST, AND WHY IT WAS PAID. Applying the criterion moved NINE codes to L2 and cut
 * the headline "added by mandate conformance" roughly in half. The number that survives is the
 * one §4.2 Case 3 actually claims. A smaller figure that withstands reading is worth more than
 * a larger one that does not, and the larger one had already produced two findings: A-028
 * caught `EVAL_CALLDATA_BINDING` counted as mandate conformance when it is signed-payload
 * integrity, and an independent review then caught F023 doing the same thing through
 * `EVAL_ACTION_BINDS_MANDATE_AND_POLICY`. Patching the instances left the category error in
 * place; the criterion is what stops a third.
 *
 * Listed explicitly rather than derived by prefix, because a prefix rule would silently absorb
 * any future code and quietly change what the ablation measures.
 */
export const MANDATE_CONFORMANCE_CODES: ReadonlySet<string> = new Set([
    // The four §7.2 names, compared against the decoded call.
    "EVAL_PURCHASE_RESOURCE",
    "EVAL_PURCHASE_BENEFICIARY",
    "EVAL_PURCHASE_DURATION",
    "EVAL_PURCHASE_RECURRENCE",
    // The post-state those imply, read back out of the simulation.
    "EVAL_ENTITLEMENT_ADVANCED",
    "EVAL_ENTITLEMENT_RECURRENCE",
    "EVAL_ENTITLEMENT_UNOBSERVED",
    // The approval schema's analogue of `beneficiary`: WHO the allowance is granted to,
    // compared against the mandate rather than against an allowlist.
    "EVAL_APPROVAL_SPENDER",
    //
    // MOVED TO L2 BY D-034, each for the reason the criterion gives:
    //   EVAL_TARGET_BOUND, EVAL_SELECTOR_BOUND   — mandate IDENTITY, not purpose
    //   EVAL_VALUE_WITHIN_MANDATE                — a ceiling; §7.2 grants the baseline one
    //   EVAL_TARGET_CODE_IDENTITY                — an evidence check (D-015, D-027)
    //   EVAL_ACTION_BINDS_MANDATE_AND_POLICY     — signed-payload integrity (the A-028 shape)
    //   EVAL_MANDATE_BINDS_POLICY                — binding, not purpose
    //   EVAL_MANDATE_ACTIVE, _WINDOW, _PRINCIPAL_IS_OWNER — mandate VALIDITY
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
        // L2 CARRIES THE POLICY ALLOWLIST, and omitting it made the ladder NON-MONOTONE.
        //
        // `MANDATE_CONFORMANCE_CODES` removes EVAL_TARGET_BOUND and EVAL_SELECTOR_BOUND —
        // correctly, since both ask "is this the MANDATE's target/selector", which §7.2
        // withholds. But they are the engine's ONLY target and selector constraints, so L2
        // was left with none at all while the strictly weaker L1 has an allowlist §7.2
        // grants it explicitly. F056 was the demonstration: L1 BLOCK, L2 REVIEW, L3 BLOCK.
        // Every product in the class L2 models has a target allowlist, so "added by L3" was
        // being measured against an arm blind to a capability the baseline has.
        //
        // Fixed by giving L2 the baseline's allowlist checks alongside the filtered engine
        // ones. L2 is now a superset of L1's capability, which is what a ladder means.
        const allowlist = runBaseline({...input, simulation: null}, baselineConfig).filter(
            (c) => c.code === "BASE_TARGET_ALLOWLISTED" || c.code === "BASE_SELECTOR_ALLOWLISTED",
        );
        checks = [
            ...allowlist,
            ...runChecks(input).filter((c) => !MANDATE_CONFORMANCE_CODES.has(c.code)),
        ];
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
