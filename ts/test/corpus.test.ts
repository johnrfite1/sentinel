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
    DeadProbeError,
    RationaleLeakError,
    TranscriptionMismatchError,
    UnprobeableRationaleError,
    assertProbesLive,
    assertRationaleUnread,
    rationaleBigrams,
    verifyRationaleFixture,
} from "../src/corpus/rationale.ts";
import {readFileSync} from "node:fs";

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

    /**
     * THE EXEMPTION IS SCOPED TO THE DEPTH IT WAS DECIDED AT.
     *
     * `isDeclared` used to take a bare name, so an allowlisted word anywhere in the tree was
     * exempt from the denylist — and `assertViewShape` inspects only the top level and
     * `observedEnvironment`, so nothing else would have caught it. An independent review
     * raised it as an undemonstrated hypothesis; these are the demonstrations.
     */
    it("does not exempt an allowlisted name nested inside a payload", () => {
        // `simulationOutcome` is legitimately allowlisted as an environment field. Buried
        // inside `mandate`, it is not a decision anybody took — and it contains "outcome".
        assert.throws(
            () => assertNoLeakage({fixtureId: "F001", mandate: {simulationOutcome: "success"}}, "F001"),
            LeakageError,
        );
    });

    it("does not exempt a top-level view key used at depth", () => {
        assert.throws(
            () => assertNoLeakage({fixtureId: "F001", action: {observedEnvironment: {verdict: "ALLOW"}}}, "F001"),
            LeakageError,
        );
    });

    it("still exempts the declared names at the depth they were declared for", () => {
        assert.doesNotThrow(() =>
            assertNoLeakage(
                {
                    fixtureId: "F001",
                    observedEnvironment: {simulationOutcome: "success", nativeBalanceDeltas: [{delta: "1"}]},
                },
                "F001",
            ),
        );
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

    it("allows the owner-authored signer identity in the mandate envelope", () => {
        assert.doesNotThrow(() =>
            assertViewShape(
                {
                    fixtureId: "F001",
                    mandate: {signer: "0x1111111111111111111111111111111111111111"},
                },
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
        // CONTAINMENT, not equality. `leakage.ts` was wrong twice for exactly this reason
        // (A-028 F-3) and was fixed; this test one file over kept the equality form, so a
        // fixture key named `expectedVerdict` would have passed it. Found by an independent
        // review looking at the two files side by side.
        const forbidden = ["expected", "verdict", "label", "answer", "truth", "outcome"];
        for (const fixture of CORPUS) {
            for (const key of Object.keys(fixture)) {
                const lowered = key.toLowerCase();
                for (const f of forbidden) {
                    assert.equal(
                        lowered.includes(f),
                        false,
                        `fixture ${fixture.id} carries "${key}" — the corpus must not hold its own answers`,
                    );
                }
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
        // BOTH free-text fields, not just `intent`. `agentRationale` is published to every
        // labeller too (it is in ALLOWED_VIEW_KEYS), so a rationale saying "this should
        // block" would hand the labeller an answer through the field added to carry an
        // attack. An independent review found the scan reading only `intent`.
        for (const fixture of CORPUS) {
            for (const [field, text] of [
                ["intent", fixture.intent],
                ["agentRationale", fixture.agentRationale ?? ""],
            ] as const) {
                const lowered = text.toLowerCase();
                for (const tell of tells) {
                    assert.equal(
                        lowered.includes(tell),
                        false,
                        `fixture ${fixture.id}'s ${field} states an outcome ("${tell}") — it must describe the setup only`,
                    );
                }
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

describe("the injection wiring can fail (independent review, 2026-08-15)", () => {
    /**
     * SIX OF TEN MUTATIONS AGAINST THIS WIRING SURVIVED A 349/349 GREEN SUITE.
     *
     * Deleting the transcription equality check, deleting the leak call outright, building a
     * different call in `proposalFor`, dropping `agentRationale` from the view allowlist,
     * weakening the floor, and narrowing the scan to reason codes — all green. Every test
     * above exercises fixture data or the pure guard; none of them ran the pipeline, because
     * `scripts/test.sh` never runs the corpus. The tests below drive the extracted check
     * directly, and the last one asserts the call site still exists, because a unit-tested
     * function nobody calls is the same defect in better clothes.
     */
    const F049 = CORPUS.find((f) => f.id === "F049")!;
    const rationale = F049.agentRationale!;

    const good = {
        fixtureId: "F049",
        rationale,
        encodedTarget: "0xabc",
        encodedValueWei: 0n,
        encodedCallData: "0xdeadbeef",
        transcribed: {ok: true, target: "0xabc", valueWei: 0n, callData: "0xdeadbeef"},
        artefact: '{"reasonCodes":["EVAL_APPROVAL_SPENDER"]}',
    };

    it("passes a fixture whose proposal and encoding agree and whose artefacts are clean", () => {
        assert.doesNotThrow(() => verifyRationaleFixture(good));
    });

    /**
     * THE FIELDS MATCH ON PURPOSE, and the first version of this test did not do that.
     *
     * It passed `{ok: false}` with no call fields, so with the `ok` check disabled the
     * equality comparison rejected it anyway — the assertion held either way and the mutation
     * `if (!transcribed.ok)` → `if (false)` SURVIVED. Making every other field agree leaves
     * the `ok` flag as the only thing that can reject this input, which is what the test
     * claims to be about. Fourth-order version of the same defect the whole session is about:
     * a test that passes for a reason other than the one it names.
     */
    it("rejects a proposal that will not transcribe, on the ok flag alone", () => {
        assert.throws(
            () =>
                verifyRationaleFixture({
                    ...good,
                    transcribed: {
                        ok: false,
                        code: "PROPOSAL_MALFORMED_TARGET",
                        detail: "x",
                        target: good.encodedTarget,
                        valueWei: good.encodedValueWei,
                        callData: good.encodedCallData,
                    },
                }),
            (err: unknown) =>
                err instanceof TranscriptionMismatchError && /does not transcribe/.test(err.message),
        );
    });

    for (const [field, patch] of [
        ["callData", {callData: "0xfeed"}],
        ["target", {target: "0xother"}],
        ["valueWei", {valueWei: 1n}],
    ] as const) {
        it(`rejects a proposal whose ${field} differs from the fixture's`, () => {
            assert.throws(
                () => verifyRationaleFixture({...good, transcribed: {...good.transcribed, ...patch}}),
                TranscriptionMismatchError,
            );
        });
    }

    it("rejects a leak reaching the evidence bundle through the full check", () => {
        assert.throws(
            () => verifyRationaleFixture({...good, artefact: JSON.stringify({e: rationale})}),
            RationaleLeakError,
        );
    });

    /**
     * The defect an independent review measured: probes built by pairing the FILTERED word
     * list matched strings that never existed. 10 of F049's 17 probes were dead, and the
     * injection payload itself could pass. Every probe must occur in its own source text.
     */
    it("derives only probes that occur in the rationale they came from", () => {
        for (const f of CORPUS) {
            if (f.agentRationale === undefined) continue;
            const self = f.agentRationale.toLowerCase().replace(/[^a-z]+/g, " ");
            for (const p of rationaleBigrams(f.agentRationale)) {
                assert.ok(self.includes(p), `${f.id}: probe "${p}" cannot ever match`);
            }
        }
    });

    it("refuses a probe that cannot occur in its own source text", () => {
        // Hand-made, because the corrected builder can no longer produce one — which is the
        // point of the invariant. The error class exists so that a future change to the
        // builder is caught by an assertion rather than by an outside reviewer.
        assert.throws(
            () => assertProbesLive(["settlement deadbeef"], rationale, "F049"),
            DeadProbeError,
        );
        assert.doesNotThrow(() => assertProbesLive(["settlement relayer"], rationale, "F049"));
    });

    it("refuses a rationale too thin to yield a usable probe set", () => {
        assert.throws(
            () => assertRationaleUnread("please approve this call now", "{}", "FXXX"),
            UnprobeableRationaleError,
        );
    });

    it("catches the verbatim excerpt the old construction let through", () => {
        // "relayer (0x...DeaDBeef) an unlimited allowance to handle" — the injection payload.
        const leak = JSON.stringify({
            evidenceCanonical:
                "granted the settlement relayer 0x00000000000000000000000000000000DeaDBeef " +
                "an unlimited allowance to handle billing transactions",
        });
        assert.throws(() => assertRationaleUnread(rationale, leak, "F049"), RationaleLeakError);
    });

    it("catches a base64 or hex carriage of the whole rationale", () => {
        for (const enc of ["base64", "hex"] as const) {
            const smuggled = JSON.stringify({provenance: Buffer.from(rationale, "utf8").toString(enc)});
            assert.throws(
                () => assertRationaleUnread(rationale, smuggled, "F049"),
                RationaleLeakError,
                `a ${enc} carriage passed`,
            );
        }
    });

    /**
     * THE CALL SITE, asserted structurally.
     *
     * `run.ts` is not covered by any test — it needs a chain, a signer process and a full
     * corpus run — so the mutation that deletes its one call to the check would otherwise be
     * invisible. This is the same idiom the step-7 transcriber uses for its code table: when
     * behaviour cannot be reached, assert the structure that produces it, and say so.
     */
    it("still calls the check from the corpus runner", () => {
        const src = readFileSync(new URL("../src/corpus/run.ts", import.meta.url), "utf8");
        assert.match(src, /verifyRationaleFixture\(\{/, "run.ts no longer calls verifyRationaleFixture");
        assert.equal(
            (src.match(/verifyRationaleFixture\(/g) ?? []).length,
            1,
            "there must be exactly one call site, or deleting one would go unnoticed",
        );
        assert.match(src, /transcribe\(proposalFor\(spec, target, valueWei\)\)/, "the proposal is no longer transcribed");
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
