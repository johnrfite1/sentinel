# A-EXTRACT — coverage: what is exercised, and what is NOT

**Read this before treating a green A-EXTRACT run as evidence of anything.** A green result is
evidence only for what it actually exercised. Everything below is a limit of this harness,
stated so that nobody has to rediscover it from a passing line.

---

## 1. Which consumer each case reaches

`TS` = `scripts/check-type-strings.sh` · `EC` = `scripts/check-eval-codes.sh` ·
`VH` = `scripts/check-vendor-honesty.sh` · `VP` = `verifier/test_verifier.py`
(`TestPublishedTypeStrings`).

| Case | TS | EC | VH | VP |
|---|:--:|:--:|:--:|:--:|
| 1 — section absent | 1a | 1b | — | 1c, 1c-ctl |
| 2 — prefix-sharing value | 2b | 2a, 2-ctl | — | — |
| 3 — value only outside | 3b | 3a | — | — |
| 4 — decoy before the section | 4a, 4c, 4d, 4e | 4b, 4f | — | — |
| 5 — duplicate publication | 5before, 5after, 5-ctl | — | — | — |
| 6 — duplicate source definition | 6before, 6after, 6-ctl | — | — | — |
| 7 — deeper subsection stays in | 7a, 7c | 7b | — | — |
| 8 — same/shallower ends | 8a, 8b | 8c, 8d | — | — |
| 9 — prose is not a publication | 9a, 9b, 9c | — | — | — |
| 10 — §7.2 caveat + SECTION EXTENT | — | — | 10a–10h, 10-ctl | — |
| 11 — report carries the caveat | — | — | 11a–11d, 11f-*, 11g | — |
| 12 — one-character prefix | — | 12suffix, 12prefix, 12-ctl | — | — |
| 13 — the two §5.8 consumers agree by CLASS | 13a–13f (paired) | — | — | 13a–13f, 13-ctl |
| 14 — certified §2 table + pin, isolated copy | — | — | 14a, 14b, 14-fixture, 14b-mut | — |
| integrity | — | — | — | Z-*, incl. Z-gate5 and Z-signed |

**Coverage gaps inside the boundary, named rather than implied:**

- **EC is never probed for duplicate publication.** This is now a DETERMINATION, not an omission
  by default — see §7.
- **VH now HAS section-extent cases** (`10c`–`10h`), written before any extractor exists. They
  specify the extent the repair must implement rather than describing one that already does.
- **VP is probed only through `TestPublishedTypeStrings`.** No other test class in
  `test_verifier.py` is run, imported, or asserted on.
- **Case 14 no longer asserts anything about the LIVE repository as a REQUIRED case.** Its
  pass/fail pair is on an isolated snapshot; the live tree is covered by integrity control
  `Z-gate5` and by `Z-signed`. Neither is a certification, recertification or reaffirmation
  (D-059(1)).
- **The `§2` marker census, the vendor-name scan, the `§10.1` label scan and the `EVAL_CODES`
  parse execute** (they are earlier blocks of the same scripts) **but nothing is asserted about
  them.**

## 2. Version and platform bounds

Measured, not assumed, and printed by preflight `P2` on every run:

- **git 2.50.1 (Apple Git-155)** — used for `git archive` (snapshot), `git init` (subject
  identity), `git ls-files` (VH's artifact enumeration) and `git show` (the `Z-*` integrity
  controls).
- **bash 3.2.57 (arm64-apple-darwin25)** — no `mapfile`, no associative arrays, no arrays at
  all in this harness.
- **Python 3.9.6** — the `VP` consumer and `TESTS.patch` are run under it.
- **`/usr/bin/grep` (BSD)** — every search. Preflight `P1` plants a canary because the
  PATH-resolved `grep` on this workstation is a wrapper that honours `--ignore-files` and can
  return a clean-looking zero.
- **`shasum -a 256`**, **`awk`**, **`sed`**, **`tar`**, **`mktemp -d`** — BSD/macOS variants.

**Not exercised on any other platform, git, bash, awk or python.** A GNU `awk`, a `bash` 4+, or
a different `grep` may behave differently, most plausibly in `sec_sub`'s `index()` loop and in
the `^#{1,6} ` ERE used by the harness's own section reader. **Nothing here should be read as a
claim about CI, about Linux, or about a container image.**

---

## 2b. Gate binding — what `a-extract-gate.sh` does and does not show

- **Shown:** the unchanged top-level FAST gate passes in an isolated clone; all three consumer
  stages are invoked by their exact banners, in a known order; breaking the FIRST consumer fails
  the gate at its named stage with two later consumers green; breaking the LAST does the same
  with two earlier consumers green.
- **NOT shown:** the DEEP profile (`--gate`) is not run — it costs several minutes more per
  invocation and executes the corpus. **That the three stages are unconditional in both profiles
  is a READING of `scripts/test.sh`, not a measurement, and it is recorded here as a reading.**
- **NOT shown:** anything about whether the guards are right. The gate carries their verdict;
  `a-extract.sh` measures the verdict.
- **Explicitly, as D-059(7) requires:** these guards cover only their enumerated canonical facts
  — six §5.8 type strings, forty-one §5.7.1 identifiers, one §7.2 sentence, one §2 table hash.
  **They are NOT general prose-consistency evidence.**
- **Cost and dependencies:** three full fast-gate runs, roughly ten to fifteen minutes, ~180 MB
  of scratch per subject, and it requires `forge`, `node`, an installed `ts/node_modules` and
  both submodule working trees. If any is absent the harness **DIES (exit 2)** rather than
  skipping — a check that cannot execute must never read as one that passed.

## 3. Where exit status is NOT a valid discriminator

**Nowhere is exit status used as a per-case verdict, and here is why it could not be.**

- `check-type-strings.sh` exits `1` for *every* finding it has — an absent section, an absent
  publication, a duplicate publication, and a drift are all exit 1. Cases 1a, 2b, 3b, 5*, 6*,
  8a and 8b would be indistinguishable from one another on status.
- `check-eval-codes.sh` likewise exits `1` both for "could not isolate §5.7.1" and for "n
  checks absent".
- `check-vendor-honesty.sh` accumulates a single `fail` flag across roughly a dozen unrelated
  conditions; its exit status carries no information about the `§7.2` block specifically.
- The `VP` consumer's status distinguishes only "all tests passed" from "something failed", and
  at case 1c the failure is an **uncaught `IndexError`**. That is why case 1c no longer asserts
  *"does not report success"* — a crash satisfies that. It asserts a **named diagnostic in the
  `anchor-unresolved` class with no traceback**, which a crash fails, and `1c-how` records the
  observed shape as a fact rather than dressing it up as a refusal.
- **A `crash` is never an acceptable class.** `unittest` prints `ERROR` for an uncaught exception
  and `FAIL` for an assertion; the reason classifier keeps them apart, and case 13 requires a
  named class from both consumers rather than matching booleans.

Every REQUIRED assertion is consequently of the form: **the success line is absent, the finding's
subject is named, and the output carries refusal vocabulary.** The harness's own exit status is
used for exactly one thing — separating "a control failed, so nothing here is trustworthy"
(exit 2) from "required cases failed with every control holding" (exit 1).

---

## 4. Interpretations I commit to, which a repair might read differently

These are decisions, not measurements. **If the implementer disagrees with one, D-058(1) says it
STOPS and has the disagreement independently confirmed — it does not edit the test.**

1. **"Prefix" is read in the dangerous direction.** Case 2 and case 12 both plant a token of
   which the required value is a *proper prefix* (`EVAL_POLICY_WINDOW_STRICT`,
   `EVAL_NONCE_CURRENTX`), plus the embedded-position variant (`XEVAL_NONCE_CURRENT`). The
   other reading — the required value is absent and only a *shorter* string is present — is
   already handled correctly by both checkers and is not probed. **Cases 2 and 12 deliberately
   overlap**; 12 is the minimal one-character form the brief names, 2 is the realistic
   longer-token form.
2. **Two headings claiming one anchor is an ambiguity to REFUSE, not a duplicate to
   deduplicate** (cases 4b/4c/4d, 10g, 13f). A repair that "reads the last one" or "merges them"
   satisfies nothing here; either is the same first-match defect wearing different clothes.
3. **A heading QUOTED inside a fenced code block is a MENTION, not an anchor** (4e, 4f, 10h).
   `check-vendor-honesty.sh` already records this exact defeat against its own `§2` lookup, so
   the fixture is the project's own, not invented for this card.
4. **A horizontal rule does not end a section** (case 13d). The shell guard's boundary is a
   heading; for the two `§5.8` consumers to agree, the Python one must stop at a heading too.
   They agree on the live document only because `§5.8`'s trailing `---` happens to sit
   immediately before the next heading. **That coincidence is not a property and this case says
   so.**
5. **Backticks make a mention non-normative** (cases 9a/9b). The publication form asserted is an
   unbackticked four-space-indented literal line, which is how `§5.8` publishes today.
6. **The case-13 reason-class vocabulary is a contract.** `success`, `anchor-unresolved`,
   `anchor-ambiguous`, `duplicate-publication`, `not-published`, `drift`,
   `duplicate-definition`, `crash`, `other`. **The words that map into each class are
   alternatives, not a dictated sentence** — a repair picks its own wording; what it may not pick
   is a different class. `TESTS.patch` states the same vocabulary on the verifier side so the two
   halves cannot drift.
7. **Case 14's assertion is "unchanged", not "correct".** `14a`/`14b` exercise both directions on
   a snapshot. **No certification, recertification or reaffirmation is performed** (D-059(1)), the
   live pin is never updated or re-signed, and `docs/gate-s2-evidence.md` is not read for change —
   `Z-signed` asserts it is byte-identical to the base commit.
8. **`AX-2` is `R4-F3`, not a new finding.** Cases `6before`/`6after` are carried under `R4-F3`'s
   existing id per the adjudication. The wrong-reason exit at `6before` is recorded as a
   refinement of that finding's severity, **not as a second defect** — inflating one defect into
   two is by this project's own terms a defect.
9. **`AX-3` is a sibling of `V3-N2` on the same line, not a duplicate of it.** The adjudicator
   tested the implication both ways: a `§7.2`-scoped but still line-oriented extraction fails
   `11b`, and a paragraph-normalized but unscoped extraction still reads the decoy at `10a`.

## 5. What this harness does NOT do

- **It makes no production repair, and proposes none.** Not one assertion is about how a
  consumer should be implemented.
- **It does not claim to have found every extraction site in the repository.** D-060(1): the
  boundary in `CARD.md` is the claim. Other scripts may have the same defect class; this card
  does not say they do not, and an enumeration shaped like this one would stop where this one
  stopped.
- **It does not touch the repository it is run from.** Every case works on a private `git
  archive` snapshot under `TMPDIR`; `HOME`, `XDG_CONFIG_HOME` and the global/system git
  configuration are redirected into the scratch area; the scratch area is removed on exit; and
  control `Z-clean` asserts the boundary paths are unmodified when the run ends.
- **It writes no git configuration into any repository it did not create.**
- **It assembles no credential-shaped fixture,** because no case needs one. The mutations are
  Markdown headings, type strings and identifier tokens.
- **It does not apply `TESTS.patch`.** The patch is verified to apply cleanly at the base SHA
  and is then discarded; the repository's `verifier/` tree is untouched.
- **`a-extract.sh` does not run the gate.** D-059(7)'s gate-binding obligation is discharged by a
  SEPARATE harness, `a-extract-gate.sh`, whose evidence is in `GATE-BINDING.md`. It runs the
  top-level FAST gate three times against a private clone. **The DEEP profile (`--gate`) is still
  not run** — see §2b.

---

## 6. Known weaknesses of the harness itself

- **`sec_sub` and `edit_at` key on exact line text.** If a fixture line moves or is rewrapped in
  a future proposal, the mutation silently does nothing — which is why **every falsification has
  a `*-mut` control that counts the fixture after mutating it.** This is not theoretical: the
  first version of this harness passed a multi-line string through `awk -v`, awk errored to
  stderr, the mutation did not apply, and case 11b reported PASS against an unmutated fixture.
  The `*-mut` controls exist because of that, and they caught it.
- **Case 13's reason classifier reads MESSAGES, so it is only as good as its alternatives.** A
  repair whose refusal message uses vocabulary outside the declared sets lands in `other` and
  fails the case. That is deliberate — the class is the contract — but it means a repair must read
  the vocabulary in `CARD.md` and `TESTS.patch` rather than guess it.
- **The VH cases are slow** (~4 s each, dominated by the repository-wide vendor scan the block
  under test does not need). A whole run is roughly 55 s.
- **`P3` warns rather than fails when HEAD is not the base SHA.** The outcomes are evidence
  about whatever was measured; the harness records what that was instead of refusing to run.
- **The `§2` capability-cell mutation in `14b` appends one space to a table row.** It is enough
  to move the hash, which is all case 14 needs, and it is deliberately not a semantic edit.
- **The harness's own section reader carried the defect it measures, and did so undetected until
  a control failed.** `section_of` used a fixed `^#{1,6} ` terminator; control `10c-mut` then
  reported that a mutation planted INSIDE `§7.2` had not applied, because the harness's own read
  of `§7.2` stopped at the planted `#### 7.2.1`. It is now anchor-derived, and so is `sec_sub`.
  **Recorded rather than quietly fixed**, because "the instrument carries the defect it is
  measuring" is the same class as the guards under test.
- **`grep -q` on a pipe was a latent size-dependent falsehood, found by a control and removed.**
  `printf '%s' "$big" | grep -qF …` exits grep at the first match; `printf` takes `EPIPE`; under
  `set -o pipefail` the pipeline returns non-zero **although the needle was found**. It never
  fired in `a-extract.sh`, whose consumer outputs are a few hundred bytes — it fired in the gate
  harness against a 60 KB log, where control `G1-stages` reported FAIL beside a visible
  `printf: write error: Broken pipe`. Both harnesses now use `grep -c`. **Recorded rather than
  quietly fixed**, because "the probe was wrong in a way that only shows up on bigger inputs" is
  the same shape as the defects under test.
- **The gate harness's G1 baseline depends on this machine's toolchain.** `forge`, `node` and an
  installed `ts/node_modules` are copied into the clone from the live tree. That is a disclosed
  dependency: the gate under test is the committed one, the environment is this workstation's.
- **`a-extract-gate.sh` asserts on the gate's OUTPUT, never on its exit status.**
  `scripts/test.sh` runs under a completion-token supervisor with its own codes; the observed
  supervisor code appears in each case description as a fact and in no assertion.

## 7. Removed from the binding contract — each with its reason

**Leaving a non-discriminating case in the binding set is worse than removing it, because a case
that cannot fail for its intended reason still reads like coverage.** Four were removed or
replaced.

1. **`14d` — the live-repository pin comparison. REMOVED from binding; retained as integrity
   control `Z-gate5`.**
   *Reason:* no discriminating control is constructible. Proving the pin is live in the live tree
   means editing `§2` there, which D-059(1) forbids and this batch will not do. The PASS/FAIL
   pair now lives at `14a`/`14b` on an isolated snapshot, where both directions are exercised and
   `14b-mut` proves the pin was left unchanged while the table moved.
   *What is lost:* nothing that was ever evidence — `14d` could only confirm two values were equal.

2. **The EC duplicate-publication case — NOT CREATED, on a determination made before the
   omission rather than after.**
   *Reason:* `§5.7.1`'s own heading reads *"the identifiers are not normative"*, and its body says
   a reimplementer *"should derive behaviour from the descriptions, not transcribe names"*. **A
   section that does not publish normatively cannot publish twice normatively.** Requiring
   uniqueness there would manufacture an obligation the document explicitly declines.
   *How the determination is kept honest:* control **`P8`** asserts §5.7.1 still declares its
   identifiers non-normative. If that changes, `P8` fails, the harness exits 2, and the omission
   is revisited rather than inherited.
   *What is retained either way:* every exact-token case — `2a` (superstring), `12suffix`
   (appended character), `12prefix` (prepended character), with controls `2-ctl` and `12-ctl`.
   Those are about MEMBERSHIP, which §5.7.1 does assert.

3. **The `11f` proxy over `ts/src/ablation/report.ts`'s text — REPLACED by executing the
   canonical generator.**
   *Reason:* a text count cannot tell an emitted sentence from a commented-out one, and says
   nothing about the artifact a regeneration would produce. `11f-a`/`11f-b`/`11f-c` now run
   `buildReport(loadInputs())` — the entry point `scripts/test.sh`'s A-062 stage uses — and assert
   on its OUTPUT; `11f-ctl` deletes the emitting statement and requires the caveat to vanish from
   the regenerated artifact and VH to fail naming the report.
   *Residual, stated:* `npm --prefix ts run ablation` (which writes the tracked file) is not
   invoked; the same `buildReport(loadInputs())` is called into the scratch area instead, so no
   tracked artifact is rewritten. `11f-a` asserts the generated bytes are byte-identical to the
   committed report, which is what makes the two equivalent here.

4. **Boolean agreement in case 13 — REPLACED by per-consumer reason classes.**
   *Reason:* two consumers failing for different reasons counted as agreement. `13b-after` passed
   on exactly that: the shell guard refused a duplicate publication while the Python consumer
   silently kept the LAST line and then failed a value comparison. Under classes it now fails,
   correctly, with `shell='duplicate-publication', verifier='assertion-mismatch'` printed in its
   own verdict line.

**Nothing else was removed.** Every assertion that held at the first measurement is retained
unchanged and still holds.
