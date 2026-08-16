import {describe, it} from "node:test";
import assert from "node:assert/strict";
import {
    FORBIDDEN_KEYS,
    LeakageError,
    ViewShapeError,
    assertNoLeakage,
    assertViewShape,
} from "../src/corpus/leakage.ts";
import {CORPUS, assertClassCoverage} from "../src/corpus/fixtures.ts";
import {FIXTURE_CLASSES, type FixtureSpec} from "../src/corpus/spec.ts";
import {
    RationaleLeakError,
    UnprobeableRationaleError,
    assertRationaleUnread,
    rationaleBigrams,
} from "../src/corpus/rationale.ts";

/**
 * The corpus's own integrity rules, enforced rather than stated.
 *
 * Everything here protects a property the project has ratified and that nothing else would
 * notice being broken. The corpus is the only evidence bearing on whether the verdicts are
 * RIGHT, so a defect in its construction does not produce a wrong number — it produces a
 * meaningless one that reads as a success.
 */

describe("the labeller/evaluator split is guarded (D-011b)", () => {
    const clean = {
        fixtureId: "F001",
        declaredIntent: "The exact action the mandate authorises.",
        observedEnvironment: {vaultPaused: false, simulationPerformed: true},
    };

    it("passes a view carrying only values and intent", () => {
        assert.doesNotThrow(() => assertNoLeakage(clean, "F001"));
    });

    /**
     * One case per forbidden key. The denylist is the module's own declared surface, so a
     * key added later without a case turns the exhaustiveness assertion below red.
     */
    for (const key of FORBIDDEN_KEYS) {
        it(`rejects a view containing "${key}"`, () => {
            const leaked = {fixtureId: "F001", [key]: "BLOCK"};
            assert.throws(
                () => assertNoLeakage(leaked, "F001"),
                (err: unknown) => err instanceof LeakageError && err.key === key,
                `a view carrying "${key}" must not reach a labeller`,
            );
        });
    }

    it("has a case for every forbidden key", () => {
        // Structural: the loop above iterates the module's list, so this asserts the list is
        // non-empty and that nothing has quietly emptied it — a denylist of zero keys would
        // pass every view while looking like a working guard.
        assert.ok(FORBIDDEN_KEYS.length >= 8, "the denylist has shrunk");
    });

    /**
     * THE BYPASS THAT WAS LIVE. The guard matched `"key"` with both quotes, so only an exact
     * name fired and every entry fell to a one-word prefix. An adversarial reviewer
     * demonstrated all of these passing, and two of them were actually in the emitted views.
     */
    for (const key of [
        "engineVerdict",
        "l3Verdict",
        "computedLabel",
        "expectedOutcome",
        "failingChecks",
        "evaluatorReasonCodes",
        "layerVerdicts",
    ]) {
        it(`rejects the prefixed/suffixed key "${key}"`, () => {
            assert.throws(() => assertNoLeakage({fixtureId: "F001", [key]: "x"}, "F001"), LeakageError);
        });
    }

    it("walks NESTED objects and arrays, not just the top level", () => {
        assert.throws(
            () => assertNoLeakage({observedEnvironment: {deep: [{engineVerdict: "BLOCK"}]}}, "F001"),
            LeakageError,
        );
    });

    it("matches keys, not values — an intent mentioning a verdict is fine", () => {
        // This is the false positive that would matter: several fixtures deliberately carry
        // adversarial prose, and one claiming the owner "already approved" this call must
        // still reach the labeller. It is the attack being described, not a leaked answer.
        const adversarial = {
            fixtureId: "F050",
            declaredIntent:
                "The proposal arrives with a rationale asserting the owner has already reviewed " +
                "and pre-approved this exact call, and that the expected verdict is allow.",
        };
        assert.doesNotThrow(() => assertNoLeakage(adversarial, "F050"));
    });

    it("is case-insensitive, so a capitalised key cannot slip through", () => {
        assert.throws(() => assertNoLeakage({Verdict: "ALLOW"}, "F001"), LeakageError);
    });

    it("names the fixture and the key it caught", () => {
        try {
            assertNoLeakage({layers: []}, "F042");
            assert.fail("expected a LeakageError");
        } catch (err) {
            assert.ok(err instanceof LeakageError);
            assert.equal(err.fixtureId, "F042");
            assert.equal(err.key, "layers");
            assert.match(err.message, /D-011\(b\)/);
        }
    });
});

describe("the view's declared shape is enforced (A-028 F-3)", () => {
    /**
     * The half the denylist cannot do. `calldataDecodedByASupportedSchema` and
     * `calldataDecodeFailureReason` leaked the evaluator's decoder output under names
     * containing no forbidden word — no name-based check could ever have caught them.
     */
    it("rejects an undeclared top-level key", () => {
        assert.throws(() => assertViewShape({fixtureId: "F001", somethingNew: 1}, "F001"), ViewShapeError);
    });

    it("rejects the exact fields that leaked, by shape rather than by name", () => {
        for (const key of ["calldataDecodedByASupportedSchema", "calldataDecodeFailureReason"]) {
            // Proof they are invisible to the denylist...
            assert.doesNotThrow(() => assertNoLeakage({[key]: "x"}, "F001"));
            // ...and caught by the allowlist.
            assert.throws(
                () => assertViewShape({fixtureId: "F001", observedEnvironment: {[key]: "x"}}, "F001"),
                ViewShapeError,
            );
        }
    });

    it("accepts the real emitted shape", () => {
        assert.doesNotThrow(() =>
            assertViewShape(
                {fixtureId: "F001", scenarioClass: "x", declaredIntent: "y", mandate: {}, policy: {},
                 action: {}, observedEnvironment: {vaultPaused: false, simulationPerformed: true}},
                "F001",
            ),
        );
    });
});

describe("no fixture carries a verdict", () => {
    /**
     * THE RULE THE CORPUS RESTS ON, made mechanical.
     *
     * `spec.ts` states it in prose: no fixture carries a verdict, an expectation, or a hint;
     * `intent` describes what was set up, never what should happen. Prose is what a future
     * edit ignores. If an `expected` field ever appears here the corpus stops being an
     * independent bar and becomes the implementers' opinion written twice — which is exactly
     * what D-006 and D-011 exist to prevent, and what HANDOFF kill criterion 3 treats as an
     * immediate halt.
     */
    it("has no verdict-shaped key on any fixture spec", () => {
        const forbidden = ["expected", "verdict", "label", "answer", "truth", "outcome"];
        for (const fixture of CORPUS) {
            for (const key of Object.keys(fixture)) {
                assert.equal(
                    forbidden.includes(key.toLowerCase()),
                    false,
                    `fixture ${fixture.id} carries "${key}" — the corpus must not hold its own answers`,
                );
            }
        }
    });

    it("has no fixture whose intent states an expected outcome", () => {
        // A softer version of the same rule: `intent` is prose, so it can smuggle an answer
        // that no key check would catch. This looks for the phrasings that would.
        const tells = [
            "should allow",
            "should block",
            "should review",
            "expected result",
            "expected verdict",
            "must allow",
            "must block",
        ];
        for (const fixture of CORPUS) {
            const intent = fixture.intent.toLowerCase();
            for (const tell of tells) {
                assert.equal(
                    intent.includes(tell),
                    false,
                    `fixture ${fixture.id}'s intent states an outcome ("${tell}") — it must describe the setup only`,
                );
            }
        }
    });
});

describe("the injection class carries a real injection (A-028 F-5)", () => {
    const INJECTION_CLASS = "malicious-retrieved-instructions";
    const injections = CORPUS.filter((f) => f.class === INJECTION_CLASS);

    /**
     * THE DEFECT THIS CLASS EXISTS TO NOT REPEAT.
     *
     * `malicious-retrieved-instructions` shipped with no rationale field anywhere in the
     * fixture format, so its two fixtures were an unlimited approval and a wrong-resource
     * purchase with a class label attached — byte-identical to F009 and F012 apart from
     * mandate identity. The corpus counted them, the ablation scored them, and the only thing
     * standing between that and a published "the injection was contained" claim was a
     * reviewer reading the fixture format.
     */
    it("gives every fixture in the class an agent rationale", () => {
        assert.ok(injections.length > 0, "the §7.1 injection class has no fixtures at all");
        for (const f of injections) {
            assert.ok(
                (f.agentRationale ?? "").trim().length > 40,
                `${f.id} is in the ${INJECTION_CLASS} class but carries no agent rationale, which ` +
                    `makes it its underlying action wearing a class label (A-028 F-5)`,
            );
        }
    });

    it("keeps every rationale-carrying fixture transcribable from a proposal", () => {
        // A raw-calldata fixture cannot be produced by an agent — that is why raw exists — so
        // a raw fixture claiming an agent rationale describes a scenario that cannot happen.
        // The runner throws on this; the corpus should never reach it.
        for (const f of CORPUS) {
            if (f.agentRationale === undefined) continue;
            assert.notEqual(
                f.call.kind,
                "raw",
                `${f.id} claims an agent rationale but authors raw calldata`,
            );
        }
    });

    it("derives enough distinctive probes from each rationale to be able to fail", () => {
        for (const f of injections) {
            const probes = rationaleBigrams(f.agentRationale ?? "");
            assert.ok(probes.length >= 5, `${f.id}: only ${probes.length} probes`);
        }
    });

    /**
     * The guard shown FIRING, not merely passing. Every previous version of this project's
     * guards passed on the real data and would have passed on anything.
     */
    it("catches a rationale that reached the evidence bundle", () => {
        const rationale = CORPUS.find((f) => f.id === "F049")!.agentRationale!;
        const leaked = JSON.stringify({evidenceCanonical: `{"agentClaim":"${rationale}"}`});
        assert.throws(() => assertRationaleUnread(rationale, leaked, "F049"), RationaleLeakError);
    });

    it("catches a leak that arrived through underscores or punctuation", () => {
        const rationale = CORPUS.find((f) => f.id === "F049")!.agentRationale!;
        const mangled = JSON.stringify({note: "granted_the_settlement_relayer_an_unlimited_allowance"});
        assert.throws(() => assertRationaleUnread(rationale, mangled, "F049"), RationaleLeakError);
    });

    it("passes an artefact that is genuinely canonical evaluator output", () => {
        const rationale = CORPUS.find((f) => f.id === "F049")!.agentRationale!;
        const clean = JSON.stringify({
            reasonCodes: ["EVAL_APPROVAL_SPENDER", "EVAL_TARGET_BOUND", "EVAL_SELECTOR_BOUND"],
            evidenceCanonical:
                '{"allowanceDeltas":[{"spender":"0x00000000000000000000000000000000deadbeef",' +
                '"before":"0","after":"115792089237316195423570985008687907853269984665640564039457584007913129639935"}]}',
        });
        assert.doesNotThrow(() => assertRationaleUnread(rationale, clean, "F049"));
    });

    /**
     * A guard that cannot fail must say so rather than report a pass. This is the fourth
     * occurrence of that failure mode in the project (A-028), so it is checked directly.
     */
    it("refuses a rationale too thin to probe with", () => {
        assert.throws(
            () => assertRationaleUnread("approve this", "{}", "FXXX"),
            UnprobeableRationaleError,
        );
    });

    it("does not count evaluator field names as distinctive narrative", () => {
        // `unlimited allowance` reads as narrative but `allowance` is an evidence-bundle field
        // name, so the bigram is dropped rather than the guard being retuned later when it
        // false-positives on real output.
        assert.equal(rationaleBigrams("an unlimited allowance increase").includes("unlimited allowance"), false);
    });
});

describe("corpus shape", () => {
    it("covers every §7.1 class", () => {
        assert.doesNotThrow(assertClassCoverage);
        const covered = new Set(CORPUS.map((f) => f.class));
        assert.deepEqual([...FIXTURE_CLASSES].filter((c) => !covered.has(c)), []);
    });

    it("stays inside §7.1's ratified 30-50 range", () => {
        assert.ok(
            CORPUS.length >= 30 && CORPUS.length <= 50,
            `§7.1 asks for 30-50 fixtures; the corpus holds ${CORPUS.length}`,
        );
    });

    /**
     * The guards must be shown to FIRE, not merely to pass on a valid corpus. Mutations that
     * disabled the size bound and the class check both survived until these existed: the real
     * corpus satisfies them, so removing the check changed nothing observable.
     */
    it("rejects a corpus missing a §7.1 class", () => {
        const short = CORPUS.filter((f) => f.class !== "reentrancy-attempt");
        assert.throws(() => assertClassCoverage(short as FixtureSpec[]), /classes with no fixture/);
    });

    it("rejects a corpus outside the ratified 30-50 range", () => {
        // The checks run in order — class coverage, then duplicate ids, then size — so each
        // violation has to be isolated or it trips an earlier check and the test passes for
        // the wrong reason. One fixture per class covers every class with only 20 entries.
        const onePerClass = FIXTURE_CLASSES.map((c) => CORPUS.find((f) => f.class === c)!);
        assert.throws(() => assertClassCoverage(onePerClass as FixtureSpec[]), /30-50 fixtures/);

        const doubled = [...CORPUS, ...CORPUS.map((f) => ({...f, id: f.id + "b"}))];
        assert.throws(() => assertClassCoverage(doubled as FixtureSpec[]), /30-50 fixtures/);
    });

    it("rejects a corpus with duplicate ids", () => {
        // Same size, same class coverage, one id repeated.
        const dupe = CORPUS.map((f, i) => (i === CORPUS.length - 1 ? {...f, id: CORPUS[0]!.id} : f));
        assert.throws(() => assertClassCoverage(dupe as FixtureSpec[]), /duplicate fixture ids/);
    });

    it("has unique ids and a non-empty intent on every fixture", () => {
        const ids = CORPUS.map((f) => f.id);
        assert.equal(new Set(ids).size, ids.length, "duplicate fixture ids");
        for (const f of CORPUS) {
            assert.ok(f.intent.trim().length > 20, `${f.id} has no usable declared intent`);
        }
    });
});
