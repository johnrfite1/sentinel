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
| 1 — section absent | 1a | 1b | — | 1c |
| 2 — prefix-sharing value | 2b | 2a, 2-ctl | — | — |
| 3 — value only outside | 3b | 3a | — | — |
| 4 — decoy before the section | 4a, 4c, 4d | 4b | — | — |
| 5 — duplicate publication | 5before, 5after, 5-ctl | — | — | — |
| 6 — duplicate source definition | 6before, 6after, 6-ctl | — | — | — |
| 7 — deeper subsection stays in | 7a, 7c | 7b | — | — |
| 8 — same/shallower ends | 8a, 8b | 8c, 8d | — | — |
| 9 — prose is not a publication | 9a, 9b, 9c | — | — | — |
| 10 — §7.2 caveat from §7.2 | — | — | 10a, 10b, 10-ctl | — |
| 11 — report carries the caveat | — | — | 11a–11f | — |
| 12 — one-character prefix | — | 12suffix, 12prefix, 12-ctl | — | — |
| 13 — the two §5.8 consumers agree | 13a, 13d (paired) | — | — | 13a, 13b-*, 13d, 13-ctl |
| 14 — Gate 5 controls | — | — | 14a–14c | — |

**Coverage gaps inside the boundary, named rather than implied:**

- **EC is never probed for duplicate publication (case 5's shape).** `§5.7.1`'s own heading says
  "the identifiers are not normative", so a code named twice there is not obviously a defect and
  I decline to invent one. **This is an interpretation, not a measurement** — see §4.
- **VH is never probed for section EXTENT.** Its `§7.2` block does not extract a section at all;
  it greps the whole proposal. Case 10 is therefore about *where the sentence came from*, not
  about where `§7.2` ends. A repair that gives VH a real section extractor will need extent
  cases of its own, and this card does not supply them.
- **VP is probed only through `TestPublishedTypeStrings`.** No other test class in
  `test_verifier.py` is run, imported, or asserted on.
- **Case 14 is a control everywhere and a REQUIRED assertion only at `14d`.** It proves this
  batch left Gate 5 alone. It says nothing about whether Gate 5 is right — D-008(1) and (3) are
  John's, and no hash speaks to them.
- **The `§2` `[§13#N read YYYY-MM-DD]` marker census, the vendor-name scan, the `§10.1` label
  scan and the `EVAL_CODES` parse are executed** (they are earlier blocks of the same scripts)
  **but nothing is asserted about them.** They appear in the captured output only as context.

---

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
  at case 1c the failure is an **uncaught `IndexError`**, not a named assertion. Case 1c
  therefore asserts *"does not report success"* — the weakest honest form — and `1c-how` records
  the refusal shape as an OBSERVED fact rather than dressing it up as a clean refusal.

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
   deduplicate** (cases 4b/4c/4d). A repair that "reads the last one" or "merges them" satisfies
   nothing here, and I regard either as the same first-match defect wearing different clothes.
3. **A horizontal rule does not end a section** (case 13d). The shell guard's boundary is a
   heading; for the two `§5.8` consumers to agree, the Python one must stop at a heading too.
   Today they agree on the live document only because `§5.8`'s trailing `---` happens to sit
   immediately before the next heading. **That coincidence is not a property and this case says
   so.**
4. **Backticks make a mention non-normative** (cases 9a/9b). The publication form asserted is an
   unbackticked four-space-indented literal line, which is how `§5.8` publishes today. A repair
   that adopts fenced code blocks instead would need this case revisited — through the
   stop-and-confirm route, not by editing it.
5. **`§5.7.1` identifiers are declared non-normative, so EC gets no duplicate-publication
   case.** See §1.
6. **Case 14's assertion is "unchanged", not "correct".** `14d` compares the live repository's
   pinned constant and computed `§2` hash against the value D-038 certified. **It is not a
   certification, a recertification, or a reaffirmation** (D-059(1)).
7. **"The generated report carries the caveat" is measured on the committed report plus the
   generator source, not by running the generator** (cases 11a, 11e, 11f). `npm --prefix ts run
   ablation` is not executed: it needs a toolchain this harness does not assume, and a
   regeneration would rewrite a tracked artifact. **11f is a proxy** — the generator contains
   both halves of the sentence — and a proxy is what it is called here.

---

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
- **It does not run the fast gate, the deep gate, or `scripts/test.sh`.** D-059(7) requires a
  targeted guard to be bound to the real gate — that obligation belongs to the *repair*, and
  this card records it as owed rather than pretending to have discharged it.

---

## 6. Known weaknesses of the harness itself

- **`sec_sub` and `edit_at` key on exact line text.** If a fixture line moves or is rewrapped in
  a future proposal, the mutation silently does nothing — which is why **every falsification has
  a `*-mut` control that counts the fixture after mutating it.** This is not theoretical: the
  first version of this harness passed a multi-line string through `awk -v`, awk errored to
  stderr, the mutation did not apply, and case 11b reported PASS against an unmutated fixture.
  The `*-mut` controls exist because of that, and they caught it.
- **Case 13's `agree()` compares only success/failure, not the reason.** Two consumers that both
  fail for different reasons count as agreeing. `TESTS.patch` carries the finer-grained
  verifier-side contract; the shell-side reason is asserted separately by the other cases.
- **The VH cases are slow** (~4 s each, dominated by the repository-wide vendor scan the block
  under test does not need). A whole run is roughly 55 s.
- **`P3` warns rather than fails when HEAD is not the base SHA.** The outcomes are evidence
  about whatever was measured; the harness records what that was instead of refusing to run.
- **The `§2` capability-cell mutation in `14c` appends one space to a table row.** It is enough
  to move the hash, which is all case 14 needs, and it is deliberately not a semantic edit.
- **`14d` has no control in the LIVE repository, and cannot have one.** Its paired opposite
  outcome (`14c`) is measured on the snapshot, because proving the pin is live in the live tree
  would mean editing `§2` there. **Stated rather than implied:** `14d` is a same-value
  comparison against a constant recorded in this card, and the evidence that the comparison can
  fail at all lives one directory away, in the snapshot.
