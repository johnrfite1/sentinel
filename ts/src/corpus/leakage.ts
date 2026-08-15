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
 * Throw if a serialised view contains any forbidden key.
 *
 * Takes the already-serialised JSON text rather than the object, because the runner's
 * serialiser is what handles bigints and the check must see exactly the bytes that will be
 * written — checking the object and writing the text would be two different things.
 *
 * Matches on `"key"` with the quotes, so a VALUE containing the word is not a false positive:
 * a fixture whose declared intent says "the owner has already approved this" must pass, and
 * one whose environment carries a `verdict` field must not.
 */
export function assertNoLeakage(serialisedView: string, fixtureId: string): void {
    const haystack = serialisedView.toLowerCase();
    for (const key of FORBIDDEN_KEYS) {
        // BOTH sides lowercased. The version this was extracted from lowercased only the
        // haystack and compared it against the key verbatim, so every camelCase entry in the
        // list — `reasonCodes` was the only one — could never match anything. The guard
        // reported clean on a view carrying reason codes, and nothing would have revealed
        // that: a denylist entry that cannot fire is indistinguishable from one that never
        // needed to. Found by writing one test per declared key rather than one test.
        if (haystack.includes(`"${key.toLowerCase()}"`)) {
            throw new LeakageError(fixtureId, key);
        }
    }
}
