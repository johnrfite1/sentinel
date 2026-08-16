# Sentinel — v1.1 register

**This file changes nothing. It records what should change.**

D-035 part (c) ruled that the specification passages carrying fixture-specific worked examples
are a **v1.1 correction, not a v1 re-freeze**, and ruled explicitly that removing a worked
example from §4.2 *edits the specification to serve the measurement* and **is not authorised**.
So this register exists to hold the work rather than do it. Everything here is deferred behind
a decision that is John's.

Written 2026-08-15. Every line number and count below was verified against the tree that day,
because this project's documented failure mode is a figure that was true once.

---

## 1. The contamination passages (A-030, D-035)

The channel is real and **measured to be small**: across six labellers, two specification
versions and two models over fourteen fixtures, **one label moved** (F051), and it was the one
labeller E had itself flagged. D-035's control arm — run twice, see A-037 — moved nothing. The
passages are still defects; the bound is what says they are not urgent.

| Passage | Where | What it leaks |
|---|---|---|
| §4.2 Case 2 | line 259 | Walks through F049's scenario and states the expected block |
| §5.7.1 note | line 516 | Names "the wrong-policy fixture then ALLOWs" — that is F025, with its answer |
| §5.7.1 body | lines 522–535 | **Publishes the evaluator's reason-code identifiers** |
| D-025's text | in `decisions.md`, reachable via the spec | Is F051's and F056's case, written out |

### A correction to D-035's own supporting text, which does not touch its ruling

D-035 records that "§5.7.1 publishes **eleven** of the evaluator's own reason-code identifiers".
**That number is wrong.** Counted directly: §5.7.1 publishes **41** — every check in the engine,
grouped under seven headings, each with a description. The "eleven" in the ratified entry is the
count from §5.7.1's own note of *checks with no home in §5.7's prose* ("eleven of the engine's
forty-one checks"), which is a different quantity that happens to sit in the same sentence.

**Consequence, stated plainly:** the contamination surface of that one subsection is roughly
four times what the decision log records. A labeller reading §5.7.1 sees the evaluator's entire
check vocabulary, not a sample of it — and labeller J cited those identifiers as `specBasis`.

**What this does NOT change:** D-035's ruling stands in full. Part (c) — v1.1 correction, not a
re-freeze — was decided on the *kind* of defect, not its size, and the measurement that bounds
it (zero movements out of five, twice) is unaffected. The entry is annotated in place rather
than rewritten, because it is John's ruling and only its supporting arithmetic was wrong.

### What amending these would cost, so the cost is not rediscovered

`scripts/check-eval-codes.sh` fails the gate if a check exists in the engine and not in §5.7.1.
**Deleting the identifier list to close the leak would break that guard**, which is the guard
D-031 added to prove §5.7's prose is complete. The two goals are in direct tension and the
resolution is a design decision, not an edit: the candidate shapes are (a) move the identifier
list out of the labeller-visible specification into an appendix the labelling protocol denies,
(b) keep it and accept a disclosed channel, (c) give labellers a redacted view of the spec.
**(c) is the largest change and the only one that also fixes §4.2.** None is chosen here.

## 2. The frozen labelling prompt says "three verdicts" and defines four

`fixtures/corpus/LABELLING_PROMPT.md` says "one of **three** verdicts" (line 20) and heads its
section "The **three** verdicts" (line 55) — then §2 instructs the labeller to answer
`INSUFFICIENT` when the material does not decide, and §7's output schema lists it as a fourth
enumerated value. Raised independently by the D-035 control arms.

This is not cosmetic: `INSUFFICIENT` is the control that makes the whole contamination
measurement interpretable — D-033's design rests on a labeller answering `INSUFFICIENT` rather
than guessing, so that "the amendment helped" is distinguishable from "the amendment decided
it". The one label that ever moved (F051) moved *to* `INSUFFICIENT`.

**Cost, per `check-label-prompt.sh`:** the file is frozen under D-011(a). Changing it means a
new file, a new hash, and a re-label of everything scored under the old one. **So this rides
with the re-label or not at all** — it is not worth a re-freeze by itself, and it has caused no
observed harm: every labeller found and used `INSUFFICIENT` regardless.

## 3. Corpus defects, all deferred for the same reason

Fixing any of these changes the view the labels of record were drawn against, so each belongs
**with** a re-label rather than before one.

- **F032 does not isolate policy expiry.** Its action deadline expires one second before the
  policy window, so it fails two checks in different D-026 remedy classes.
- **F026 and F051 pin different `allowedCallGraphHash` values over an identical observed call
  graph** — same target, selector, calldata, operation, and `internalCallCount` 0. At most one
  can describe what F051's intent claims. Found by labeller K with no implementation access.
- **F056 does not exercise reentrancy** (A-036) and **F051 is inert** for the neighbouring
  class, so §7.1's `reentrancy-attempt` and `unexpected-internal-call` classes are covered at
  the corpus layer by two fixtures that between them exercise neither.
- **The labelling view emits `failureMode` as `"0"`/`"1"` with no legend** (A-026(e)). The
  specification itself no longer has this gap — §5.9 (D-024) states `FAIL_CLOSED = 0,
  REVIEW = 1` — but **the fixture view a labeller reads still does not**, and every control arm
  run against the pre-§5.9 snapshot has flagged it, twice calling it their most actionable
  finding. Any re-label must fix the view first.

## 4. The highest-value item, and it is not on the list above

**A fixture's class name is a claim about what it exercises, and nothing in the corpus checks
that claim** (A-036, third instance of this defect class after A-028 F-5). The mechanical check
is describable in one sentence — *assert that each class's fixtures produce at least one failing
check the class is about* — and **is not built**.

It is the only item here that would have caught F056, F051 and the vacuous injection class
without a human noticing each one separately, and unlike everything else in this register it
does **not** ride on the re-label decision: asserting a property of the existing corpus changes
no fixture and moves no label.

**BUILT 2026-08-16 — `scripts/check-class-coverage.sh`, wired into the gate (A-038).** It
reports **14 of 20 classes exercise the class they name**. Four of the six carried are known and
reasoned; **two are new and unruled**, and they are the register's newest items:

- **`owner-override-and-block-behaviour`** — F054/F055 fail on code identity and wrong resource.
  Neither is about the override path.
- **`conflicting-block-state`** — F048 REVIEWs on simulation-unavailable and code-identity, which
  is an outage shape, not the conflicting-state shape D-030 calls a failed rule that blocks.

**RULED 2026-08-16 (D-039), and the two are not the same kind of defect:**

- **`owner-override-and-block-behaviour` — ACCEPTED DELEGATION, nothing owed.** F054/F055 declare
  `primaryEnforcement: vault-foundry-invariants` and the vault suite genuinely tests the override
  path. The declaration is accurate; the corpus layer is not where it is proved.
- **`conflicting-block-state` — A GAP, and it OWES A FIXTURE.** F048 declares
  `primaryEnforcement: conformance-engine`, claiming to be proved *here*, and is not. Nothing
  else covers it. **This is the one new v1.1 work item this session produced.**

The GAP inherits A-036's deferral — repairing F048 changes the view the labels of record were
drawn against — so the fixture rides with the re-label. What did NOT ride with it is the guard,
which is why building it first was worth doing, and the guard now carries a `status` of
DELEGATED / RESERVED / GAP so this distinction lives in the instrument rather than only here.

## 5. Owed on the §2 capability table, after Gate 5's certification (D-038)

Two citations are weaker than they could be — one row cited for fewer criteria than the vendor
may document, and one still pointing at a marketing page rather than technical documentation.
Neither blocks anything; both would move accuracy in the direction that does *not* flatter
Sentinel.

**The detail is in `docs/gate-5-vendor-audit.md`, not here, and the split is not editorial:**
that file is the one artifact `check-vendor-honesty.sh` excludes from D-008(4), because it
cannot do its job without naming the parties. This register is a measurement artifact and must
stay free of vendor names. The guard caught a first draft of this very section for exactly that
reason, which is the second time it has fired on this session's own work.

**Any edit to the §2 table makes D-038's certification stale**, so these ride together with
whatever else touches that table rather than being applied one at a time.
