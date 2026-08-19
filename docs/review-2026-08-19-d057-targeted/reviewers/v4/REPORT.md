# V4 — targeted independent reverification of `R2-F4` and `R3-F4`

**Frozen commit evaluated:** `c8d15a76425544148d7da2f8fa0c003feb6ad2b7`
(`git rev-parse HEAD` in the V4 worktree printed exactly that SHA; the only working-tree
difference was an untracked `ts/node_modules`).

**Verdicts**

| Finding | Verdict |
|---|---|
| `R2-F4` — the `decodedSelectorAndParameters` claim corrected where the reader is not | **FAIL** |
| `R3-F4` — the fabricated `EVAL_VAULT_*` enforcement code name | **HOLD** (one same-class residual recorded separately) |

I authored none of this material. Every probe below is paired with a control, and every
zero result is backed by a planted-string demonstration that the search instrument was live.
The full probe transcript is in `PROBES.md`; what I did and did not reach is in `COVERAGE.md`.

---

## 0. The search instrument, established BEFORE any zero result was trusted

The brief warned that on this machine `grep` is a ugrep wrapper carrying `--ignore-files`.
I confirmed that and measured the consequence rather than assuming it.

Planting `CANARY_V4_SWEEP_PROOF2` in two gitignore-matched paths (`contracts/out/canary.txt`,
`.env.canary`) and searching:

- the shell `grep` wrapper returned **exit 1, no output** — indistinguishable from a clean sweep;
- `/usr/bin/grep -rnE` (BSD grep, ignore-files not honoured) returned **both files**.

Every sweep in this report therefore runs through `/usr/bin/grep` directly, excluding only
`.git` and `node_modules`. Separately, because this repository hard-wraps prose, phrase
searches were re-run against a newline-joined copy of every file, and identifier searches
against **two** joins — space-joined (reassembles wrapped phrases) and empty-joined
(reassembles an identifier hard-wrapped mid-token). The mid-token join was not a precaution
in the abstract: a deliberately wrapped fabricated code name was invisible to the
space-joined pass and visible to the empty-joined one. Both are in `PROBES.md`.

---

## 1. `R2-F4` — **FAIL**

### 1.1 The general property, stated before looking at the fix

*No maintained, reader-facing artifact may leave a reader who encounters **that artifact**
with the false statement standing. A correction filed in a different document is not a
correction of this one.*

That is `R2-F4`'s own argument, restated. `A-078(5)` accepted it in those terms — *"the
correction was filed and the falsehood left standing, which is the original finding moved
rather than closed"* — named **two** further sites, and its commit message closed with
**"Both closed."**

### 1.2 Ground truth, measured, not read

The claim at issue is *"`decodedSelectorAndParameters` is compared to nothing / a
conformance comparison the D-010 verifier does not perform."*

The packet's own stated test, run verbatim at the frozen commit:

```
grep -c decodedSelectorAndParameters verifier/verify.py   ->  2
```

and the control that proves the instrument moves:

```
git show 9347c9d:verifier/verify.py | grep -c decodedSelectorAndParameters   ->  0
git show caad4c1:verifier/verify.py | grep -c decodedSelectorAndParameters   ->  2
```

`9347c9d` is the commit that wrote the §7 blocker text; `caad4c1` is `A-074`, which built the
comparison. So the claim was true when written and became false at `A-074`.

A grep count is a weak instrument, so I falsified behaviourally as well. Neutering
`_allow_conforms_to_the_mandate` (`verifier/verify.py:1348`) to `return []` took
`TestAllowConformsToTheMandate` from **9 passed** to **8 failed / 1 passed**, the survivor
being the BLOCK-still-verifies control that is supposed to pass in both states. The
comparison exists, is reached, and is load-bearing.

**The claim is FALSE at this commit.** The signer checks the field too
(`ts/src/signer/attest.ts:638`, `checkEvidenceDecoding`).

### 1.3 Mechanical enumeration of every site

Searched the whole tree — code comments, Solidity NatSpec, Python docstrings, shell scripts,
the proposal, `HANDOFF.md`, `README.md`, every `docs/*.md`, and the review artifacts — for
nine spellings of the meaning, not the wording: *compared to nothing*, *compared against
nothing*, *compared by nothing*, *checked by neither*, *nothing checks/compares*, *no
conformance comparison*, *does not perform*, *is not compared*, *uncompared*, plus
`grep -c decodedSelectorAndParameters` and `does the conformance comparison`.

**Four maintained, reader-facing sites carry the claim. Two are corrected. Two are not.**

| # | Site | State at `c8d15a7` | Class |
|---|---|---|---|
| 1 | `docs/v1-1-register.md:928-937` (§14 bullet) | Struck, labelled *"SUPERSEDED AND FALSE SINCE A-074 — CORRECTED IN PLACE 2026-08-19"* | **corrected** |
| 2 | `docs/exit-criterion-packet.md:103` (§3b row) | Item struck; the cell carries an explicit `CORRECTION:` a reader of that row sees | **corrected** |
| 3 | `docs/exit-criterion-packet.md:211-214` (§7, **BLOCKER 1**) | **Live, present tense, unstruck, unannotated** | **UNCORRECTED** |
| 4 | `docs/decisions.md:225` (`A-070` residual (b)) | **Live, present tense, unstruck, unannotated** | **UNCORRECTED** |

### 1.4 Site 3 — the most serious, and it is in the file the repair edited

`docs/exit-criterion-packet.md` §7, *"Explicit blockers and non-blockers"*, opening
*"BLOCKERS — exit cannot be reached while these stand"*:

> 1. **The signed Gate S1 pack contains a known false claim.** `gate-s1-evidence.md:124`/`:152`
>    state the D-010 verifier "does the conformance comparison"; **it does not.** **This is not
>    an agent's to close — it changes what the product guarantees, and it sits in signed text.**
>    Under C1 condition 4 this alone blocks exit.

Three facts make this a failure rather than an oversight:

1. **It is false.** The verifier does the conformance comparison (§1.2 above, measured two ways).
2. **It is in the same file the repair edited.** `git show 8990255 --format="" -U0 --
   docs/exit-criterion-packet.md` produces exactly one hunk: `@@ -103 +103 @@`. One line
   changed; §7 sits **108 lines below it** and was not looked at. `git log -L 212,212` on that
   file shows its last touch was `9347c9d` — *before* `A-074` built the comparison. Nothing has
   revisited it since.
3. **It is the document's live status surface, not narration.** §7 tells a reader what blocks
   the exit criterion. It asserts a resolved item still blocks exit. §3b of the same file, 108
   lines above, says the claim is corrected. The document contradicts itself, and the half a
   reader consults for "what blocks exit" is the false half.

This is `R4-F4`'s shape reproduced inside the repair for `R2-F4`: *"I removed one copy … and
left another eleven lines below my own claim that the figures were no longer duplicated."*
Here it is one copy removed and another left 108 lines below, in a commit whose message says
**"Both closed."**

### 1.5 Site 4 — the originating sentence, never touched

`docs/decisions.md:225`, `A-070`'s residual (b), verbatim and unstruck:

> (b) The §5.6 projections are now required on both paths, but WHAT THEY COMPARE is unchanged:
> `decodedSelectorAndParameters` **is still compared to nothing**, which is round six's separate
> and larger finding that D-014's own justification names a conformance comparison **this
> verifier does not perform**. **That one is not fixed here and is not an agent's to close** —
> it changes what the product guarantees and it sits inside a SIGNED gate pack.

This is not a paraphrase of the falsehood. It is the **source**: register §14's struck bullet
quotes this sentence and attributes it *"(A-070)"* by name. The repair struck the quotation and
left the original. `git log -L 225,225:docs/decisions.md` shows the line unchanged since
`a89c255`, the commit that wrote it.

`docs/decisions.md` is a maintained document by this project's own settled convention, not
preserved evidence: `A-080` annotated `A-076`'s entry **in place** at line 243 on the express
ground that it was *"the second canonical record `R4-F1` named"*, and `A-078(5)` invoked the
same convention (*"per the convention §13.3 and §11.0 already use"*). By that standard the
canonical record of the sentence register §14 struck is exactly the entry that should have
been annotated, and it was the one entry nobody opened.

Both halves of the sentence are false at this commit, and its final clause is worse than the
first two: it tells a reader the item **is not fixed**, in the file the project treats as its
own memory.

### 1.6 The control — a place the claim is stated CORRECTLY, and I am not flagging it

The narrowed claim — that the human-readable **`description` sub-field** is compared to
nothing — is still TRUE, and my sweep hits it. I verified it and deliberately did not flag it:
a word-boundary grep for `description` in `ts/src/signer/attest.ts` returns nothing, and the
only `description` in `verifier/verify.py` is an `argparse` keyword at `:2261`.

Sites carrying the claim **correctly**, all left alone:

- `docs/v1-1-register.md:877` — §13.7's heading, *"The human-readable description is compared
  to nothing"*. True.
- `ts/src/decode/index.ts:250` — `describe()`'s own docstring, *"never used for comparison —
  the typed fields are the truth"*. True.
- `docs/decisions.md:27` — `D-014`'s *"detectable after the fact by the D-010 verifier, which
  does the conformance comparison"*. False when written, **true now**; correctly not flagged.
- `scripts/test.sh:653` — *"198 (A-074, D-055(b): the conformance comparison D-014 assigns to
  this verifier, which did not exist)"*. Accurate past tense.

A sweep that flagged any of these would not be distinguishing false-and-live from true. Mine
distinguishes them, which is what makes the two hits above findings rather than noise.

### 1.7 Sites classified HISTORICAL, and why

- `docs/review-2026-08-18-d055e/**` (`reviewers/r2/REPORT.md`, `reviewers/r2/CRITIQUE.md`,
  `adjudications/r4-adjudicates-r2.md`), `docs/review-2026-08-18-round-six/ADJUDICATED-ROUND-SIX.md`,
  `docs/review-2026-08-17/*.json` — preserved reviewer and adjudication artifacts under
  `docs/review-2026-08-1*/`. These record what was said and must not be rewritten. Hits here
  are expected and correct.
- `docs/gate-s1-evidence.md:152-172` — the false sentence sits **inside** an explicit
  `[ANNOTATED 2026-08-18 (D-055(b)). THIS SENTENCE WAS FALSE WHEN THIS PACK WAS SIGNED, AND IS
  NOW TRUE …]` bracket, and the `returned 0` is past tense within it. A reader of that site sees
  the correction. Acceptable.
- `verifier/verify.py:1504-1510` and `verifier/test_verifier.py:1337` — docstrings using past
  tense (*"It did not … returned 0"*) to explain why the check exists. True as history.
- `docs/decisions.md:223` (`D-052(a)`) — repeats *"a conformance comparison the D-010 verifier
  does not perform"* in present tense, but as an item in the enumerated **reproduced-findings
  set of round six at frozen `140c59e`**, introduced by *"The reproduced set, because a count is
  not a finding"*. I classify it HISTORICAL on that basis, consistent with `A-080`'s own ruling
  that dated `decisions.md` entries stand as history. **This is the weakest of my
  classifications and I flag it as such** — see RESIDUAL R-3.

### 1.8 Verdict and what the evidence does not establish

**`R2-F4`: FAIL.** The repair asserted completeness ("Both closed") over a set of two when the
set is four. Both misses are of the exact class `docs/repair-protocol.md` step 2 exists to
prevent, and one of them is 108 lines from the line the repair changed.

**What this does not establish.** I did not evaluate whether `A-078`'s two *corrections* are
well-worded, only that they are present and visible at their sites. I did not search
non-English spellings, image or binary content, or git history beyond the four commits cited.
My sweep covers the meanings enumerated in §1.3; a fifth site phrased in a meaning I did not
anticipate would not appear here, and I state that rather than claim a clean sweep.

---

## 2. `R3-F4` — **HOLD**

### 2.1 The general property, stated before looking at the fix

*Every enforcement code a maintained document names must be a code the codebase actually
defines, so a reader can follow the pointer to the thing that enforces.*

### 2.2 The real code names, derived from the code and not from any document

Enumerated mechanically from the product tree:

| Real code | Defined at | Emitted at |
|---|---|---|
| `SIGNER_VAULT_TARGET_NOT_ALLOWED` | `ts/src/signer/protocol.ts:248` (code to class map, `"CONFORMANCE"`) | `ts/src/signer/attest.ts:523` — `if (!state.targetAllowed) findings.push(...)` |
| `SIGNER_VAULT_SELECTOR_NOT_ALLOWED` | `ts/src/signer/protocol.ts:250` | `ts/src/signer/attest.ts:524` — `if (!state.selectorAllowed) findings.push(...)` |

Corroborated independently of the source: `fixtures/samples/case-2-injection-block/receipt.json`
carries `SIGNER_VAULT_TARGET_NOT_ALLOWED` in a committed receipt, `ts/test/reasoncodes.test.ts:141-142`
pins both, and `scripts/mutate.sh:326-327` names the target one as a mutation site.

**The prefix is not cosmetic.** `ts/src/signer/protocol.ts:769-774` refuses a caller-supplied
`SIGNER_` prefix outright — *"reserved for the signer's own findings"* — after an adversarial
reviewer signed a receipt asserting three signer findings the signer never made. So an `EVAL_`
spelling of these two codes does not merely misspell a name: it attributes vault
target/selector enforcement to the conformance engine, which is precisely the confusion
`R3-F4`'s disclosure exists to prevent.

### 2.3 The maintained documentation names the real codes

Both places that describe this enforcement now name `SIGNER_*`, and both record the error
rather than quietly overwriting it:

- `ts/src/signer/protocol.ts:369-373` — *"`SIGNER_VAULT_TARGET_NOT_ALLOWED` and
  `SIGNER_VAULT_SELECTOR_NOT_ALLOWED` — the `SIGNER_` prefix is the real one. This comment first
  cited an `EVAL_` spelling that exists nowhere in the codebase…"*
- `docs/gate-s2-evidence.md:632` — same two codes, same parenthetical.

`docs/decisions.md:245` (`A-077`) describes the disclosure without citing any code name, so
there is nothing to correct there.

### 2.4 No fictitious `EVAL_VAULT_*` survives in live maintained prose

Whole-tree sweep with the wrap-tolerant instrument. Distinct `EVAL_VAULT_*` names anywhere:
`EVAL_VAULT_BOUND`, `EVAL_VAULT_NOT_PAUSED` (both real, defined in
`ts/src/evaluate/checks.ts`), `EVAL_VAULT_TARGET_NOT_ALLOWED`, `EVAL_VAULT_SELECTOR_NOT_ALLOWED`.

The two fictitious names occur **exactly once each in the entire tree**, both on
`docs/decisions.md:246`, inside `A-078`'s own paragraph headed **"A FALSE CODE NAME I
INVENTED"**, which continues *"spellings that exist nowhere in the codebase; the real codes are
`SIGNER_`-prefixed."*

**Classification: acceptable historical quotation.** It is not a citation of the code as real —
it is the record of the error, in the sentence that names it as an error. Removing it would
delete the disclosure. No other occurrence exists in any file, wrapped or unwrapped.

One further hit, also acceptable: `docs/session-state.md:18` writes *"a fabricated
`EVAL_VAULT_*` code name"* — a glob, explicitly labelled fabricated.

### 2.5 The class sweep — every code the codebase defines, diffed against every code the docs name

Two independent diffs, both in `PROBES.md`.

**Diff A** — codebase (everything outside `docs/`) vs. maintained documents (top-level
`docs/*.md`, `HANDOFF.md`, `README.md`, the proposal, `verifier/REPORT.md`,
`fixtures/corpus/LABELLING_PROMPT.md`; `docs/review-2026-08-1*/` excluded as preserved
evidence). **105 codes defined, 55 named, 3 orphans** — the two above plus the
`EVAL_VAULT_*` glob. All accounted for.

**Diff B** — the same question with the self-vouching loophole closed. Diff A would let a
fabricated name invented **in a code comment** vouch for itself, because the comment lives in
the codebase. Diff B therefore counts a code as real only if it appears in a **non-comment**
line of product material. **102 real, 109 named anywhere, 7 gaps.** Three are truncated
globs or a deliberately-fabricated attacker payload inside preserved
`docs/review-2026-08-17/*.json` artifacts; three are the `EVAL_VAULT_*` items above. **The
seventh is new — see RESIDUAL R-4.**

### 2.6 Controls

- **Would my method have caught the original?** Reintroducing
  `EVAL_VAULT_TARGET_NOT_ALLOWED` into `docs/gate-s2-evidence.md` made Diff A report it against
  that file; reverting removed it. Reintroducing both fictitious names into the
  `ts/src/signer/protocol.ts` comment they were removed from made Diff B report it against that
  file. A mid-token-wrapped fabrication (`EVAL_VAULT_` + newline + `SELECTOR_MISSPELLED`) was
  **missed** by the space-join pass and **caught** by the empty-join pass — which is why both
  are run.
- **Does my method flag legitimate codes?** No. 102 real codes, zero flagged, including both
  `SIGNER_VAULT_*` codes and the real `EVAL_VAULT_BOUND` / `EVAL_VAULT_NOT_PAUSED`.

### 2.7 Verdict and what the evidence does not establish

**`R3-F4`: HOLD.** The real codes are what the code defines, the maintained documentation names
them, and the fabrication survives only inside the sentence that identifies it as a fabrication.

**What this does not establish.** I verified that the cited codes **exist** and are emitted on
the target/selector branches. I did **not** verify that the four fields are inert — that is the
measurement half of `R3-F4` and it is outside this brief's scope. I also did not check
identifier families other than `EVAL_`, `SIGNER_` and `DECODE_`, or codes cited only inside
`docs/review-2026-08-1*/`, which are preserved evidence.

---

## 3. RESIDUALS — recorded, and kept separate from the two verdicts above

None of these is a verdict. R-1 and R-2 are limits on `R2-F4`'s corrections; R-3 is a
classification I want John to see rather than inherit; R-4 and R-5 are same-class defects I
tripped over and am reporting rather than absorbing.

**R-1. `docs/exit-criterion-packet.md:103`'s correction is visible but strikes inconsistently.**
The left cell is struck; the two false sentences in the right cell (*"It does not"*, *"This is a
known false claim in signed text and is UNFIXED"*) are **not** struck — they are followed by a
bolded `CORRECTION:` clause. A reader of the row does see the correction, so the site passes my
criterion, but the discipline differs from register §14's strike-and-supersede in the same
repair.

**R-2. `docs/decisions.md:239` (`A-074` residual (c)) still reads *"Recorded in the register,
not fixed here."*** This is the exact sentence `R2-F4` was filed against. It is **not** a live
falsehood at this commit — `A-077` made it true by writing register §13.7 — so I did not flag
it. But it carries no marker that it was false when written, and the entry that was the
finding's target is the one entry with no annotation. Whether that matters is a
record-honesty question for John, not a defect I am asserting.

**R-3. My HISTORICAL classification of `docs/decisions.md:223` (`D-052(a)`) is the one I am
least sure of.** It states *"a conformance comparison the D-010 verifier does not perform"* in
the present tense. I classified it historical because it is an item in the enumerated
reproduced-findings set of round six at a named frozen commit. A reader could reasonably read it
as a standing claim. **Question for John, not for me to answer:** does the annotate-in-place
convention reach a ruling's enumeration of what a spent review reproduced?

**R-4 (NEW, same class as `R3-F4`, LOW). A second fictitious code name, in maintained material.**
`ts/test/evaluate.checks.test.ts:502` reads:

```
// The action names the target upper-cased, the mandate lower-cased. Same address, so
// `EVAL_ACTION_TARGET_MATCHES_MANDATE` must PASS.
```

`EVAL_ACTION_TARGET_MATCHES_MANDATE` **exists nowhere else in the tree** — that comment is its
only occurrence. The assertion three lines below uses the real code, `EVAL_TARGET_BOUND`. This is
`R3-F4`'s class — *a document names a code that does not exist* — in a live maintained file, and
it was introduced by the same remediation cycle. It is a test comment, not an evidence claim, so
I record it as LOW rather than as a failure of the `R3-F4` repair.

**R-5 (NEW, same class as `R2-F4`, out of assigned scope). A false claim standing in the code's
own comment, for finding `E4`.** `ts/src/decode/index.ts:190-193` asserts that
`normalizedAction` and `expectedEffects` *"are checked by NEITHER the signer nor the verifier."*
The verifier half is built: `verifier/verify.py:1434` `_evidence_describes_the_bundle` checks
both (`:1462-1491`, `:1523-1571`) and is reached from `:911` and `:1629`. The register itself
records this at `docs/v1-1-register.md:777` — *"VERIFIER HALF BUILT (A-069…)"* — while the
comment stands. **This is the `A-063` shape verbatim** (the correction filed in the register, the
falsehood left in the source's own comment) for a different finding. Not in my scope; recorded
so it is not lost.

**R-6. The `R3-F4` class has no mechanical guard, and I proved it rather than inferred it.**
`scripts/check-eval-codes.sh` is code-to-spec directional and covers only the `EVAL_CODES` array.
It reported `41/41 … documented in §5.7.1`, exit 0, **with `EVAL_VAULT_TARGET_NOT_ALLOWED`
injected into `docs/gate-s2-evidence.md`**, and again with both fictitious names reintroduced
into `ts/src/signer/protocol.ts`. The control proves the guard is alive rather than dead:
renaming one real code inside proposal §5.7.1 made it fail with exit 1 and name the missing
code. So the guard works and is simply blind to this direction. `R3-F4`'s repair is prose, and
prose is what this project has repeatedly found insufficient. **Building such a guard is a scope
decision and is John's, not mine.**

---

## 4. What I did NOT do

I did not sign or reopen a gate, certify any claim, ratify a correction, commit, push, rename,
or edit the primary tree outside this directory. All probes ran in the V4 worktree, every
mutation was reverted, and `git status --porcelain` there shows only the untracked
`ts/node_modules`. Two questions above (R-3, R-6) are written as questions for John and are
deliberately left unanswered.
