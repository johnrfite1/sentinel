/**
 * The mechanical guard on the D-011(b) labeller/evaluator split.
 *
 * D-011(b) is unambiguous: "the labeler receives payload schemas, security invariants, and
 * each fixture's declared intent — never evaluator source, never evaluator output." The
 * corpus runner emits two views to two directories, and this is what stops the wrong one
 * reaching the labelling side.
 *
 * WHY IT IS A GUARD AND NOT A CONVENTION. A labeller view that leaked a verdict would turn
 * the corpus from an independent bar into a self-graded suite, and the leak would be
 * INVISIBLE in a green run — every label would simply agree with the implementation and the
 * disagreement rate would read as a success. That is the most expensive failure available to
 * this project, because the corpus is the only evidence that bears on whether the verdicts
 * are right at all. HANDOFF kill criterion 3 treats fixture and label tampering as an
 * immediate halt; this is the check that would notice the accidental version.
 *
 * EXTRACTED FROM THE RUNNER SO IT CAN BE TESTED. It previously lived inside `run.ts` as a
 * local function, which meant the one guard protecting a ratified separation was itself
 * unverified — a guard that has never been shown to fail is a guard nobody should trust.
 */

/**
 * Keys that must never appear in a labeller-facing view.
 *
 * Deliberately a denylist of SHAPES rather than an allowlist of permitted fields. An
 * allowlist would silently drop any new environment field the labeller legitimately needs,
 * and a labeller missing information fails loudly (INSUFFICIENT) while a labeller given a
 * verdict fails silently. Given the choice, this errs toward the loud failure.
 */
export const FORBIDDEN_KEYS = [
    "verdict",
    "checks",
    "reasonCodes",
    "failing",
    "outcome",
    "label",
    "expected",
    "layers",
] as const;

export class LeakageError extends Error {
    readonly key: string;
    readonly fixtureId: string;

    constructor(fixtureId: string, key: string) {
        super(
            `labeller view for ${fixtureId} leaks an evaluator-shaped key: ${key}. ` +
                `D-011(b) forbids evaluator output reaching a labeller; a leaked verdict makes ` +
                `the corpus agree with the implementation by construction.`,
        );
        this.fixtureId = fixtureId;
        this.key = key;
    }
}

/**
 * Throw if any key in a labeller-facing view is, or contains, a forbidden name.
 *
 * Takes the OBJECT rather than serialised text. Walking keys is what makes "contains" safe:
 * a substring scan over the text would fire on any VALUE mentioning a forbidden word, and
 * several fixtures deliberately carry adversarial prose — one claiming the owner "has already
 * approved" a call must still reach the labeller, because that is the attack being described.
 */
export function assertNoLeakage(view: unknown, fixtureId: string): void {
    walk(view, fixtureId, 0, false);
}

/**
 * Recursive KEY WALK, not a substring scan over the serialised text.
 *
 * TWO DEFECTS PRECEDED THIS, AND BOTH READ GREEN.
 *
 * The first lowercased the haystack and compared it against the key verbatim, so every
 * camelCase entry could never match — in practice `reasonCodes`, one of the eight.
 *
 * The second survived that fix and was worse: matching `"key"` WITH BOTH QUOTES meant only
 * an exact key name fired, so every entry fell to a one-word prefix. An adversarial reviewer
 * demonstrated `engineVerdict`, `l3Verdict`, `computedLabel`, `expectedOutcome`,
 * `failingChecks`, `evaluatorReasonCodes` and `layerVerdicts` all passing (A-028 F-3) — every
 * name a real engineer would actually write. And the gap was already in use: six labelling
 * views carried the decoder's internal enum strings through fields whose names merely
 * CONTAINED a forbidden word.
 *
 * The lesson generalises past this file. A denylist matched by substring is a denylist whose
 * coverage depends on how its entries happen to be spelled, and testing it with the exact
 * spellings it declares can only ever confirm the spellings it declares. Walking keys and
 * testing containment is the shape that does not depend on that.
 */
function walk(node: unknown, fixtureId: string, depth: number, inEnvironment: boolean): void {
    if (Array.isArray(node)) {
        for (const item of node) walk(item, fixtureId, depth, inEnvironment);
        return;
    }
    if (typeof node !== "object" || node === null) return;

    for (const [key, value] of Object.entries(node)) {
        // A DECLARED key is exempt, and the precedence is the whole design.
        //
        // Broadening the match from equals to contains immediately flagged
        // `simulationOutcome` — a legitimate observed fact the labeller needs, caught only
        // because "outcome" is a substring of it. The fix is not to narrow the denylist back
        // until the false positive goes away, which would reopen the bypass; it is to say
        // what the two checks are FOR. The allowlist is a decision somebody made about a
        // specific field. The denylist is a heuristic for fields nobody decided about. A
        // heuristic must not overrule a decision, and a decision must be explicit — which is
        // why adding to `ALLOWED_ENVIRONMENT_KEYS` is the act that carries the thinking.
        //
        // THE EXEMPTION IS NOW SCOPED TO THE DEPTH IT WAS DECIDED AT. It used to apply at
        // every depth: `isDeclared` took a bare name, so an allowlisted word anywhere in the
        // tree — nested three levels inside `mandate`, say — was exempt from the denylist
        // walk, and `assertViewShape` only inspects the top level and `observedEnvironment`.
        // An independent review raised it as a hypothesis it had not demonstrated. It is a
        // real gap and it is cheaper to close than to argue about: a decision about a
        // TOP-LEVEL field is not a decision about a field of the same name buried inside a
        // payload, and treating it as one is how an allowlist quietly becomes a wildcard.
        if (isDeclaredAt(key, depth, inEnvironment)) {
            walk(value, fixtureId, depth + 1, inEnvironment || key === "observedEnvironment");
            continue;
        }
        const lowered = key.toLowerCase();
        for (const forbidden of FORBIDDEN_KEYS) {
            // CONTAINS, not equals — `engineVerdict` is as much a leak as `verdict`.
            if (lowered.includes(forbidden.toLowerCase())) {
                throw new LeakageError(fixtureId, key);
            }
        }
        walk(value, fixtureId, depth + 1, inEnvironment);
    }
}

/**
 * Exempt only where the exemption was actually decided.
 *
 * Depth 0 is the view's own shape, so `ALLOWED_VIEW_KEYS` applies there. `observedEnvironment`
 * is the one declared container, so `ALLOWED_ENVIRONMENT_KEYS` applies to its immediate
 * members. Nothing is exempt anywhere else — a name matching an allowlist entry six levels
 * down inside a typed payload was never a decision anybody took.
 */
function isDeclaredAt(key: string, depth: number, inEnvironment: boolean): boolean {
    if (depth === 0) return (ALLOWED_VIEW_KEYS as readonly string[]).includes(key);
    if (inEnvironment && depth === 1) return (ALLOWED_ENVIRONMENT_KEYS as readonly string[]).includes(key);
    return false;
}

/**
 * The typed §5.1-§5.3 payload containers, declared field by field (R3-F3, D-055(e)).
 *
 * THE ARGUMENT: **an allowlist that stops one level above the leak is a denylist.**
 * `ALLOWED_VIEW_KEYS` declared `mandate`, `policy` and `action` as permitted CONTAINERS and
 * said nothing about what may be inside them, so a field carrying evaluator output under an
 * innocuous name — `calldataDecodedByASupportedSchema` was the real one (A-028 F-3) — passed
 * the shape check at depth 1 and met only the denylist, which by construction cannot catch a
 * name containing no forbidden word.
 *
 * A-032 recorded this as a HYPOTHESIS and closed the denylist half. R3 DEMONSTRATED it: the
 * exact route A-028 F-3 used is still open one level down. This closes it.
 *
 * These are the §5 payload fields and nothing else — measured from all 50 committed views, not
 * transcribed from the spec. Adding a field to a payload container is now a deliberate act that
 * fails the corpus run until it is declared, which is the point at which somebody has to ask
 * whether it leaks.
 */
export const ALLOWED_PAYLOAD_KEYS: Readonly<Record<string, readonly string[]>> = {
    mandate: [
        // `signer` is owner-authored mandate input, not evaluator output. Labellers need the
        // complete signed authorisation envelope to judge signer-identity substitutions.
        "schemaVersion", "mandateId", "principal", "signer", "vault", "chainId", "target",
        "targetCodeHash", "selector", "maxNativeValueWei", "purposeKind", "resourceId",
        "beneficiary", "durationSeconds", "recurringAllowed", "validAfter", "validUntil",
        "policyHash",
    ],
    policy: [
        "schemaVersion", "policyVersion", "vault", "chainId", "allowedOperation",
        "allowedTargetsHash", "allowedSelectorsHash", "maxNativeValueWei",
        "maxAllowanceIncreaseBaseUnits", "allowedCallGraphHash", "validAfter", "validUntil",
        "failureMode",
    ],
    action: [
        "schemaVersion", "chainId", "vault", "actionNonce", "target", "valueWei", "dataHash",
        "operation", "mandateHash", "policyHash", "deadline", "callData",
    ],
};


/**
 * The labeller view's DECLARED SHAPE — the half a denylist structurally cannot provide.
 *
 * WHY BOTH. The key walk above catches a field NAMED like evaluator output. It cannot catch
 * one that carries evaluator output under an innocuous name, and that is exactly what
 * happened: `calldataDecodedByASupportedSchema` and `calldataDecodeFailureReason` published
 * the evaluator's own decoder result — the same object handed to `evaluate` — through names
 * containing no forbidden word. Six views carried them and a labeller quoted the enum strings
 * verbatim (A-028 F-3).
 *
 * A denylist answers "does this look like an answer?". Only an allowlist answers "is this
 * something we decided the labeller should have?". Adding a field to the labeller view is
 * now a deliberate act that fails the corpus run until it is declared here — which is the
 * point at which someone has to think about whether it leaks.
 */
export const ALLOWED_VIEW_KEYS = [
    "fixtureId",
    "scenarioClass",
    "declaredIntent",
    // DECLARED DELIBERATELY, 2026-08-15, which is the entire purpose of this allowlist.
    //
    // `agentRationale` carries the untrusted narrative attached to the proposal (A-028 F-5).
    // The question the allowlist forces is "did we decide the labeller should have this?", and
    // the answer is yes, for a reason specific to this field: the labeller's job is to say
    // what Sentinel SHOULD conclude, and a labeller shown only the bytes is never tested on
    // whether a persuasive story moves them. The frozen prompt anticipated exactly this — rule
    // 8.2 says a fixture claiming to be "a required setup step" is a fixture describing an
    // attack, not an instruction — so the field is within the material D-011(b) grants, and
    // the prompt needs no change to accommodate it.
    //
    // It is not evaluator output. Nothing in `evaluate/` reads it, and `rationale.ts` fails
    // the corpus run if any of it turns up in an evaluator-side artefact.
    "agentRationale",
    "mandate",
    "policy",
    "action",
    "observedEnvironment",
] as const;

export const ALLOWED_ENVIRONMENT_KEYS = [
    "vaultPaused",
    "vaultActiveMandateHash",
    "vaultActivePolicyHash",
    "vaultCurrentActionNonce",
    "vaultAuthorisedSigner",
    "vaultOwner",
    "vaultMaxNativeValueWei",
    "targetOnVaultAllowlist",
    "selectorOnVaultAllowlist",
    "targetRuntimeCodeHashOnChain",
    "simulationPerformed",
    "simulationOutcome",
    "simulationRevertReason",
    "nativeBalanceDeltas",
    "allowanceDeltas",
    "entitlements",
    "internalCallCount",
    "simulationAnchorBlock",
] as const;

export class ViewShapeError extends Error {
    constructor(fixtureId: string, where: string, unexpected: string[]) {
        super(
            `labeller view for ${fixtureId} has undeclared ${where} key(s): ${unexpected.join(", ")}. ` +
                `Add them to the allowlist in leakage.ts only after deciding they do not carry ` +
                `evaluator output — D-011(b) forbids that, and a name-based denylist cannot ` +
                `catch a leak under an innocuous name.`,
        );
    }
}

/** Assert the view carries exactly the declared fields, and nothing undeclared. */
export function assertViewShape(view: Record<string, unknown>, fixtureId: string): void {
    const top = Object.keys(view).filter((k) => !(ALLOWED_VIEW_KEYS as readonly string[]).includes(k));
    if (top.length > 0) throw new ViewShapeError(fixtureId, "top-level", top);

    const env = view.observedEnvironment;
    if (typeof env === "object" && env !== null) {
        const extra = Object.keys(env).filter(
            (k) => !(ALLOWED_ENVIRONMENT_KEYS as readonly string[]).includes(k),
        );
        if (extra.length > 0) throw new ViewShapeError(fixtureId, "observedEnvironment", extra);
    }

    // THE TYPED PAYLOAD CONTAINERS (R3-F3). Without this the allowlist declared `mandate`,
    // `policy` and `action` as permitted containers and said nothing about their contents, so
    // an innocuously-named field carrying evaluator output sat one level below the boundary
    // and met only the denylist — which cannot catch a name containing no forbidden word.
    // That is the exact route A-028 F-3 used, left open by the repair that closed the other
    // half. Demonstrated by an independent reviewer rather than hypothesised.
    for (const [container, allowed] of Object.entries(ALLOWED_PAYLOAD_KEYS)) {
        const payload = view[container];
        if (typeof payload !== "object" || payload === null || Array.isArray(payload)) continue;
        const extra = Object.keys(payload).filter((k) => !allowed.includes(k));
        if (extra.length > 0) throw new ViewShapeError(fixtureId, container, extra);
    }
}
