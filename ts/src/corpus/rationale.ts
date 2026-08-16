/**
 * The measurement that makes `malicious-retrieved-instructions` a real class (A-028 F-5).
 *
 * §4.2 Case 2's claim is that Sentinel judges the bytes and their effects, never the agent's
 * account of what the call means. On the step-7 path that claim has a test. In the corpus it
 * had nothing at all: `FixtureSpec` carried no rationale, so the two injection fixtures were
 * their own underlying approval and wrong-resource actions wearing a class label, and whatever
 * layer "caught" them caught the action, not an injection.
 *
 * WHAT THIS FILE ASSERTS, AND WHAT IT DELIBERATELY DOES NOT. It asserts that the narrative
 * reached no evaluator-side artefact. It does NOT assert that the narrative was "handled",
 * "detected", or "resisted" — nothing in Sentinel reads it, so there is nothing to resist, and
 * a fixture that appeared to detect an injection would be evidence of a defect rather than a
 * feature. The value of the assertion is regression: threading provenance into the evidence
 * bundle is a plausible, even tempting future change, and it would silently turn an untrusted
 * string into signed content.
 *
 * WHY BIGRAMS RATHER THAN A DECLARED PHRASE LIST. The project's most repeated defect is a
 * guard whose coverage is the list of spellings it happens to declare — the leakage denylist
 * was wrong twice for exactly that reason (A-028 F-3), and `propose.e2e.test.ts` checks three
 * hand-picked phrases, which can only ever confirm those three. Deriving the probes FROM the
 * fixture's own rationale means adding a fixture automatically extends the guard, and editing
 * a rationale automatically re-aims it.
 */

/** Words too generic to distinguish narrative from canonical JSON field names. */
const GENERIC = new Set([
    "this",
    "that",
    "with",
    "from",
    "your",
    "call",
    "data",
    "hash",
    "true",
    "false",
    "value",
    "block",
    "allow",
    "check",
    "token",
    "owner",
    "target",
    "action",
    "policy",
    "mandate",
    "address",
    "selector",
    "allowance",
    "approve",
    "approval",
    "purchase",
    "beneficiary",
    "duration",
    "recurring",
    "simulation",
    "entitlement",
]);

/**
 * The lowercase word bigrams a canonical evidence bundle could not plausibly contain.
 *
 * Both halves must be alphabetic and at least four characters, and neither may be a field
 * name the evaluator legitimately emits — otherwise `unlimited allowance` would fire on
 * `allowanceDeltas` and the guard would be tuned back down until it stopped complaining,
 * which is how a denylist becomes decorative.
 */
export function rationaleBigrams(rationale: string): string[] {
    const words = rationale
        .toLowerCase()
        .split(/[^a-z]+/)
        .filter((w) => w.length >= 4 && !GENERIC.has(w));

    const out: string[] = [];
    for (let i = 0; i + 1 < words.length; i++) out.push(`${words[i]} ${words[i + 1]}`);
    return [...new Set(out)];
}

export class RationaleLeakError extends Error {
    readonly fixtureId: string;
    readonly phrase: string;

    constructor(fixtureId: string, phrase: string) {
        super(
            `the agent's rationale reached an evaluator-side artefact for ${fixtureId}: ` +
                `"${phrase}". §3.1 classifies a purpose claim as untrusted and D-019 keeps it ` +
                `unread; a narrative inside the evidence bundle is signed content Sentinel ` +
                `never verified.`,
        );
        this.fixtureId = fixtureId;
        this.phrase = phrase;
    }
}

export class UnprobeableRationaleError extends Error {
    constructor(fixtureId: string, count: number) {
        super(
            `the rationale for ${fixtureId} yields only ${count} distinctive bigram(s), so the ` +
                `leak check cannot fail and would report a pass it did not earn. Write a ` +
                `rationale with real narrative in it, or drop the field.`,
        );
    }
}

/** Below this the probe set is too thin to be evidence of anything. */
const MIN_BIGRAMS = 5;

/**
 * Throw if any distinctive phrase from the rationale appears in the evaluator's own output.
 *
 * `artefact` is the serialised evaluator-side material — bound fields, calldata, check
 * results, reason codes, and the canonical evidence bundle. The labeller view is deliberately
 * NOT passed: the labeller is supposed to see the claim, because judging a call whose
 * accompanying story argues for it is the thing being measured.
 */
export function assertRationaleUnread(rationale: string, artefact: string, fixtureId: string): void {
    const probes = rationaleBigrams(rationale);
    if (probes.length < MIN_BIGRAMS) throw new UnprobeableRationaleError(fixtureId, probes.length);

    // Normalised the same way the probes are, so a leak that arrived through JSON escaping,
    // an underscore join, or punctuation still matches. A guard that only catches the
    // prettiest spelling of a leak is the denylist mistake again.
    const haystack = artefact.toLowerCase().replace(/[^a-z]+/g, " ");
    for (const phrase of probes) {
        if (haystack.includes(phrase)) throw new RationaleLeakError(fixtureId, phrase);
    }
}
