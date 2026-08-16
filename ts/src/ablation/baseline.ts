import type {Hex} from "../signer/protocol.ts";
import type {ConformanceInput, CheckResult, Verdict} from "../evaluate/checks.ts";
import {MAX_UINT256} from "../decode/index.ts";

/**
 * §7.2 — the representative local baseline, as its own implementation.
 *
 * WHY THIS IS NOT A FILTER OVER THE EVALUATOR'S CHECK CODES. The obvious cheap construction
 * is to run the real evaluator and drop the codes a baseline would not have. That would be
 * wrong in a way that flatters Sentinel: the evaluator's `EVAL_TARGET_BOUND` asks "does the
 * target equal the MANDATE's target", while a policy baseline asks "is the target on the
 * ALLOWLIST" — and §7.2's baseline explicitly allowlists both DemoPay *and* DemoERC20. A
 * filtered evaluator would therefore report the baseline catching Case 2 on target binding,
 * which a real policy engine of this class would not do. The semantics differ, so the
 * implementation is separate.
 *
 * BUILD IT AS STRONG AS IT FAIRLY GOES. §7 exists to test whether Sentinel's verdicts are
 * anything more than hard-coding, and a weak baseline manufactures a difference rather than
 * measuring one. So this baseline decodes calldata — policy engines that write rules over
 * decoded calldata are real and shipping, and §2's capability table is where the market is
 * described — enforces a native-value ceiling, and blocks unlimited approvals outright. It is
 * given every capability §7.2 lists and no less.
 *
 * NO VENDOR IS NAMED IN THIS FILE, and the omission is deliberate rather than incidental.
 * This module IS the arm the ablation's headline compares against; a vendor's name in its
 * header would make every figure in `docs/ablation-report.md` read as a claim about that
 * product, which is exactly the LAYOUT D-008(4) forbids. One was here until 2026-08-15, in
 * this paragraph, and it survived because `check-vendor-honesty.sh` only scanned markdown.
 *
 * WHAT §7.2 WITHHOLDS FROM IT, VERBATIM: "No resource, beneficiary, duration, recurrence, or
 * post-state constraint." Those are the mandate-to-effects layer, and withholding them is
 * the whole content of the comparison.
 *
 * THE CLAIM THIS SUPPORTS, AND THE ONE IT DOES NOT. §7.2 is explicit: "This baseline makes
 * the demo reproducible but is not evidence that current vendors miss Case 3." Nothing
 * produced by this file may be reported as an empirical result about any named vendor.
 * D-001 cut executed vendor comparisons from v1 entirely, and D-008's vendor-honesty gate
 * makes the layout of such a claim as forbidden as the claim itself.
 */

/** What a representative wallet policy of this class is configured with. */
export interface BaselineConfig {
    chainId: bigint;
    vault: Hex;
    /** §7.2: "Allowlisted DemoPay and DemoERC20 targets." */
    allowedTargets: readonly Hex[];
    allowedSelectors: readonly Hex[];
    maxNativeValueWei: bigint;
    /**
     * §7.2: "Direct maximum-approval block."
     *
     * Read as the rule these products actually ship: block the unlimited sentinel. It is
     * deliberately NOT a general allowance ceiling — that is `maxAllowanceIncreaseBaseUnits`,
     * a policy-layer quantity, and granting it to the baseline would be inventing a
     * capability §7.2 does not list.
     */
    blockUnlimitedApproval: boolean;
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

/** The baseline's own code namespace, so its results can never be confused with the engine's. */
export const BASELINE_CODES = [
    "BASE_CHAIN_BOUND",
    "BASE_VAULT_BOUND",
    "BASE_TARGET_ALLOWLISTED",
    "BASE_SELECTOR_ALLOWLISTED",
    "BASE_VALUE_CEILING",
    "BASE_UNLIMITED_APPROVAL",
    "BASE_CALLDATA_UNDECODABLE",
] as const;

export type BaselineCode = (typeof BASELINE_CODES)[number];

export function runBaseline(input: ConformanceInput, config: BaselineConfig): CheckResult[] {
    const {action, decode} = input;
    const results: CheckResult[] = [];

    results.push(
        action.chainId === config.chainId
            ? pass("BASE_CHAIN_BOUND")
            : violation("BASE_CHAIN_BOUND", `action chain ${action.chainId} is not ${config.chainId}`),
    );

    results.push(
        action.vault.toLowerCase() === config.vault.toLowerCase()
            ? pass("BASE_VAULT_BOUND")
            : violation("BASE_VAULT_BOUND", `action vault ${action.vault} is not ${config.vault}`),
    );

    const target = action.target.toLowerCase();
    results.push(
        config.allowedTargets.some((t) => t.toLowerCase() === target)
            ? pass("BASE_TARGET_ALLOWLISTED")
            : violation("BASE_TARGET_ALLOWLISTED", `${action.target} is not on the allowlist`),
    );

    const selector = input.callData.slice(0, 10).toLowerCase();
    results.push(
        config.allowedSelectors.some((s) => s.toLowerCase() === selector)
            ? pass("BASE_SELECTOR_ALLOWLISTED")
            : violation("BASE_SELECTOR_ALLOWLISTED", `${selector} is not on the allowlist`),
    );

    results.push(
        action.valueWei <= config.maxNativeValueWei
            ? pass("BASE_VALUE_CEILING")
            : violation(
                  "BASE_VALUE_CEILING",
                  `${action.valueWei} wei exceeds ceiling ${config.maxNativeValueWei}`,
              ),
    );

    // Undecodable calldata is UNRESOLVED rather than a violation: a policy engine that
    // cannot read the call has not established that the call is bad, only that it cannot
    // tell. Scoring it as a block would credit the baseline with a detection it did not make.
    if (!decode.ok) {
        results.push(
            unresolved("BASE_CALLDATA_UNDECODABLE", `${decode.code}: the baseline cannot read this call`),
        );
        return results;
    }

    if (config.blockUnlimitedApproval && decode.decoded.schema === "DemoERC20.approve") {
        results.push(
            decode.decoded.amount === MAX_UINT256
                ? violation("BASE_UNLIMITED_APPROVAL", "unlimited approval is blocked outright")
                : pass("BASE_UNLIMITED_APPROVAL", `finite approval of ${decode.decoded.amount}`),
        );
    }

    return results;
}

/**
 * The baseline's verdict fold.
 *
 * Two verdicts, not three. A policy engine of this class allows or blocks; "review" is a
 * Sentinel concept tied to the owner-override path (§3.3(7)), and giving the baseline a
 * review verdict would hand it a mechanism §7.2 does not describe. An unresolved check
 * therefore has to resolve one way, and it resolves to ALLOW — which is not generosity but
 * accuracy: a wallet policy that cannot decode a call does not hold the transaction for a
 * human, it applies the rules it could evaluate. That choice is what makes
 * `BASE_CALLDATA_UNDECODABLE` count as a FALSE ALLOW in the ablation when the ground truth
 * says block, and counting it honestly is the point.
 */
export function baselineVerdict(results: CheckResult[]): Verdict {
    return results.some((r) => r.outcome === "VIOLATION") ? "BLOCK" : "ALLOW";
}
