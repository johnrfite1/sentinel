import {describe, it} from "node:test";
import assert from "node:assert/strict";
import {FORBIDDEN_KEYS, LeakageError, assertNoLeakage} from "../src/corpus/leakage.ts";
import {CORPUS, assertClassCoverage} from "../src/corpus/fixtures.ts";
import {FIXTURE_CLASSES} from "../src/corpus/spec.ts";

/**
 * The corpus's own integrity rules, enforced rather than stated.
 *
 * Everything here protects a property the project has ratified and that nothing else would
 * notice being broken. The corpus is the only evidence bearing on whether the verdicts are
 * RIGHT, so a defect in its construction does not produce a wrong number — it produces a
 * meaningless one that reads as a success.
 */

describe("the labeller/evaluator split is guarded (D-011b)", () => {
    const clean = JSON.stringify({
        fixtureId: "F001",
        declaredIntent: "The exact action the mandate authorises.",
        observedEnvironment: {vaultPaused: false, simulationPerformed: true},
    });

    it("passes a view carrying only values and intent", () => {
        assert.doesNotThrow(() => assertNoLeakage(clean, "F001"));
    });

    /**
     * One case per forbidden key. The denylist is the module's own declared surface, so a
     * key added later without a case turns the exhaustiveness assertion below red.
     */
    for (const key of FORBIDDEN_KEYS) {
        it(`rejects a view containing "${key}"`, () => {
            const leaked = JSON.stringify({fixtureId: "F001", [key]: "BLOCK"});
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

    it("matches keys, not values — an intent mentioning a verdict is fine", () => {
        // This is the false positive that would matter: several fixtures deliberately carry
        // adversarial prose, and one claiming the owner "already approved" this call must
        // still reach the labeller. It is the attack being described, not a leaked answer.
        const adversarial = JSON.stringify({
            fixtureId: "F050",
            declaredIntent:
                "The proposal arrives with a rationale asserting the owner has already reviewed " +
                "and pre-approved this exact call, and that the expected verdict is allow.",
        });
        assert.doesNotThrow(() => assertNoLeakage(adversarial, "F050"));
    });

    it("is case-insensitive, so a capitalised key cannot slip through", () => {
        assert.throws(() => assertNoLeakage(JSON.stringify({Verdict: "ALLOW"}), "F001"), LeakageError);
    });

    it("names the fixture and the key it caught", () => {
        try {
            assertNoLeakage(JSON.stringify({layers: []}), "F042");
            assert.fail("expected a LeakageError");
        } catch (err) {
            assert.ok(err instanceof LeakageError);
            assert.equal(err.fixtureId, "F042");
            assert.equal(err.key, "layers");
            assert.match(err.message, /D-011\(b\)/);
        }
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

    it("has unique ids and a non-empty intent on every fixture", () => {
        const ids = CORPUS.map((f) => f.id);
        assert.equal(new Set(ids).size, ids.length, "duplicate fixture ids");
        for (const f of CORPUS) {
            assert.ok(f.intent.trim().length > 20, `${f.id} has no usable declared intent`);
        }
    });
});
