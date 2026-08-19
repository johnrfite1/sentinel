# ADJUDICATION — Reviewer 2 adjudicating Reviewer 4 (the free lens)

**Adjudicator:** R2. I did not author these findings and had no contact with R4.
**Commit adjudicated:** `7e0ab7f1057de278c09cc803ab4ca266f53399e1`.
**Worktree used:** `_archive/sentinel-d055e-review/worktrees/w2` (mine, reused).
`<REPO>` was never written to.

**Method.** I assumed each claim wrong until I made its failure happen myself. Every count in
this document is arithmetic I performed on the tree, not arithmetic I copied from R4 or from the
coordinator's summary. Where R4 demonstrated something by mutation, I re-applied the mutation
independently **and added a control R4 did not run**, because a mutation that passes proves
nothing unless the un-mutated case fails. All mutations were reverted and the revert verified with
`cmp` against a pristine 361-file copy, never with `git checkout`.

| finding | R4 severity | my verdict | my severity |
|---|---|---|---|
| `R4-F1` | MEDIUM | **CONFIRMED** (one supporting claim overstated) | **MEDIUM** — sustained |
| `R4-F2` | LOW | **CONFIRMED** | **LOW** — sustained |
| `R4-F3` | MEDIUM | **CONFIRMED** as an INSTRUMENT defect; the transposition is **not live** | **MEDIUM** — sustained |
| `R4-F4` | MEDIUM | **CONFIRMED** | **MEDIUM** — sustained |

I raised nothing and lowered nothing. Two findings carry corrections to R4's supporting reasoning
that do not change the verdict; both are recorded below rather than absorbed.

---

# R4-F1 — §11.0 says five accepted limits remain; six do. `G-3` was dropped.

## The claim

`docs/gate-s2-evidence.md` §11.0 enumerates ten accepted limits, says A-076 fixed five, and twice
states that five remain — omitting `G-3`, which the register still carries as ACCEPTED. R4 adds
that the error originates in `decisions.md` A-076, that the same paragraph contains its own stale
number ("nine"), and that this round's COMMON-BRIEF inherited the miscount.

## What I did

I did the enumeration and the subtraction myself before reading R4's, and I tested the one
hypothesis that would refute the finding — that `G-3` was fixed and simply not listed as fixed.

```
cd _archive/sentinel-d055e-review/worktrees/w2

# The T1 verification table inside §11.0 (lines 492-843):
awk 'NR>=492 && NR<=843 && /^\| `/' docs/gate-s2-evidence.md | wc -l      -> 10
# rows: D-07, D-09(a)(b), D-10, E5, F-VAULT-4, F-VAULT-5, G-3, G-5, H-5, H-8

# The per-finding bullet list in the same section:
awk 'NR>=492 && NR<=843 && /^- \*\*`/' docs/gate-s2-evidence.md
# ten limits get a bullet, G-3 among them at line 621

# The two "what remains" statements:
sed -n '492,500p'  docs/gate-s2-evidence.md   -> "what is accepted today is FIVE: D-07, D-09(a),(b), E5, F-VAULT-4, F-VAULT-5"
sed -n '517,524p'  docs/gate-s2-evidence.md   -> "What remains accepted here is five: D-07, D-09(a),(b), E5, F-VAULT-4 and F-VAULT-5"
```

**My arithmetic, done independently:** ten entries; A-076 fixed `D-10`, `G-5`, `H-5`, `H-8`
wholly and `D-09(c)` partially. Ten minus four wholly-removed entries = **six** still accepted:
`D-07`, `D-09`(a),(b), `E5`, `F-VAULT-4`, `F-VAULT-5`, **`G-3`**.

**The refuting hypothesis, tested and rejected.** If `G-3` had been fixed, the "five" would be
right and the T1 table merely stale. It was not fixed, and it could not have been:

```
grep -n '`G-3`' docs/v1-1-register.md
#  782: | `G-3` | CONFIRMED | MEDIUM -> LOW | **ACCEPTED (D-051(b), §11.0)** · T1 basis VERIFIED and MEASURED

grep -o 'Six items only:[^*]*' docs/decisions.md
#  Six items only: `D-09(c)`, `G-5`, `D-10`, `H-5`, `H-8`, and a mechanical protection
#  against the gate script being mutated mid-run.        <- D-056(a); G-3 is not in scope

# occurrences of G-3 inside the entire A-076 entry:
python3 -c "...A-076 slice..."   -> 0        (G-5 appears 3 times; G-3 zero)
```

`G-3` is outside the checkpoint D-056(a) authorised, appears nowhere in A-076, and the register
carries it as ACCEPTED with a T1-VERIFIED basis. **It is unambiguously still an accepted limit.**

**ADDENDUM 1 verified.** `decisions.md` A-076, under "RECORDS UPDATED SO NOTHING FIXED STILL READS
AS ACCEPTED", writes the same five-item list. The defect is in **two** canonical records, and it
propagated from the decision log to the signed pack.

**Propagation verified — all four locations R4 names:**

```
briefs/COMMON-BRIEF.md:51        "§11.0 is the five findings John ACCEPTED as limits"
docs/exit-criterion-packet.md:221 "The ten §11.0 accepted limits — subject to T1."
docs/session-state.md:96,165,176,205  "ten accepted limits"
```

The COMMON-BRIEF line is the operative one: it is the instrument governing **this** round, and it
tells four reviewers that the accepted-limit baseline has five members when it has six.

**ADDENDUM 2 — I reproduced the `G-3` mechanism from the corpus myself**, because R4's severity
argument rests on it:

```
# my own script over fixtures/corpus/results/F*.json — 50 fixtures, 20 classes
classes whose ONLY non-PASS outcomes are UNRESOLVED:
   conflicting-block-state              -> ['F048']
   runtime-code-change-or-proxy-target  -> ['F042', 'F043']

./scripts/check-class-coverage.sh   -> 6 carried (1 RESERVED, 4 DELEGATED, 1 GAP)
   the GAP is conflicting-block-state; runtime-code-change-or-proxy-target is NOT carried
   20 - 6 = 14 counted as covered
```

So `runtime-code-change-or-proxy-target` is one of the 14 counted as covered and its credit comes
entirely from `EVAL_TARGET_CODE_IDENTITY`, which is UNRESOLVED in both its fixtures. That is
`G-3`'s substance, and it is the qualification on the "14 of 20" figure that
`docs/exit-criterion-packet.md:94` lists as a boundary that must not block exit.

## What I observed that R4 got wrong

**One supporting claim is overstated and I am correcting it.** R4 writes:

> in the two documents John reads to set the exit criterion — the packet and the signed pack — the
> figure "14 of 20 classes exercise the class they name" now appears with no surviving
> qualification anywhere in either.

That is not true of the pack. `docs/gate-s2-evidence.md:795-812` carries a substantial, still-live
qualification: it breaks down the six carried classes, names `conflicting-block-state` as a ruled
GAP, states "spread over is not coverage", corrects an earlier draft with "**A DELEGATION IS NOT A
CREDIT**", and adds the separate figure "39 of 43 scoped fixtures individually fail a check their
own class is about."

What is missing is **`G-3`'s specific and distinct** qualification — that two of the classes
counted as *covered* are credited only on UNRESOLVED outcomes. §795-812 is about the six
**carried** classes; `G-3` is about the fourteen **counted**. The narrower claim survives and is
the one that matters; the sentence as R4 wrote it does not.

**The "nine" sub-claim: valid but minor.** The paragraph does say *"silently restating it as nine
would leave those citations pointing at a number that no longer appears anywhere."* Under A-076
the restatement would be five (or truly six), so "nine" is a fossil of the A-075 edit. But it sits
inside a counterfactual clause arguing why the heading keeps "TEN"; it does not assert a count of
current limits, and no reader would take "restating it as nine" to mean nine are accepted. **It
carries no independent severity.** I record it as sound and immaterial rather than let it inflate
the finding.

## An observation arising from adjudication, explicitly NOT part of R4's finding

R4 calls §11.0 "a **signed** pack section" and builds its severity partly on that. **Checked: the
pack is signed 2026-08-16 (D-041); §11.0's own heading is dated 2026-08-18 (D-051(b)) and its
corrections are A-075/A-076 of the same day. §11.0 postdates the signature by two days.** The
document's header nonetheless states: *"Signed on the state described below, including §11. …
**§11 is not a caveat attached after the fact; it is part of what was signed.**"*

So the strict position is: **John did not sign "five".** The false count is post-signature text
inside a signed document, under a header asserting that §11 is signed content. R4's strongest
severity lever — "false claim in signed text" — is the part that does not survive inspection, and
an adjudicator should say so rather than let it carry weight it has not earned.

(That the signed pack's §11 has grown after signature under a header claiming §11 *is* what was
signed is a separate question about what the signature covers. It is not R4's finding, I did not
scope it, and I am flagging rather than adjudicating it.)

## Verdict: **CONFIRMED**

The count is false, deterministic, and present in two canonical records. Both R4 addenda hold.
One supporting sentence is overstated and is corrected above; the "signed text" framing is
weaker than stated.

## Severity: **MEDIUM** — sustained. And my independent view on whether it blocks exit.

The coordinator asked for this specifically, because D-055(a) makes "zero known false or
unsupported signed/certified claims" an exit condition.

**Why not HIGH.** No code behaviour is affected. The authoritative record — register §13.4:782 —
is correct and carries `G-3` with a T1-VERIFIED, MEASURED basis, so **nothing is actually lost
from the record**; two prose summaries disagree with a correct ledger. `G-3` is itself an
adjudicated LOW. And the "signed claim" framing does not hold: §11.0 postdates the signature, so
this is a false claim in a canonical document, not a claim John certified. HIGH would require
either a product consequence or a genuinely signed false statement, and there is neither.

**Why not LOW.** Three things, and the third is decisive. (1) It is in **two** canonical records,
not one, and the second inherited it from the first — the failure mode is copying, which does not
self-correct. (2) The paragraph containing the error is *itself* an anti-staleness argument; a
count-correction paragraph that miscounts is the project's own named defect class operating on the
instrument built to prevent it. (3) **The harm is not hypothetical — it has already occurred.**
`briefs/COMMON-BRIEF.md:51` tells this round's four reviewers the baseline has five members. A
reviewer who re-derives `G-3` against that baseline reports a false positive, and a future round
has no summary carrying the acceptance forward. Demonstrated propagation into the live instrument
is what separates this from a documentation typo.

**Does it block exit?** My independent view: **it should not block, and it should not be accepted
either — it should be corrected before exit, because correcting it costs one line and accepting it
costs the exit criterion its meaning.**

The reasoning: C1 condition 4 targets *false or unsupported signed/certified claims*. This is a
false claim in a certified document's post-signature section — weaker than a signed false claim,
stronger than a stray doc error. Reading it as blocking would make the condition unsatisfiable by
bookkeeping rather than by substance, which is not what D-055(a) is for. Reading it as a
non-blocker without correcting it leaves the exit-criterion packet's own boundary table
(`:92`, "Ten findings accepted as documented limits | D-051(b), §11.0") pointing at a section that
says five, when the answer is six — three numbers across three documents, none of them right.

**That disposition is John's, not mine.** What I can state as an adjudicator is the fact:
**six limits are accepted today, `G-3` is the sixth, and three live documents say otherwise.**

---

# R4-F2 — the round-six preservation README omits one of its own four sanitizations

## The claim

`docs/d055e-scope-manifest.md` de-scopes 15 files on the grounds that the directory's README is
"the authority on which is which", and names three modified files. `EVIDENCE-MANIFEST.txt` is a
fourth — `<REPO>`-substituted and header-prefixed — and the README's fidelity table does not
disclose it.

## What I did and observed

```
A=<HOME>/Projects/_archive/sentinel-round-six-2026-08-18
R=.../worktrees/w2/docs/review-2026-08-18-round-six

diff "$A/MANIFEST-sha256.txt" "$R/EVIDENCE-MANIFEST.txt"
# 0a1,4   > 4 header lines ("# Relative SHA-256 manifest…", archive name + sha256)
# 972c976 < …-> <REPO>/ts/node_modules
#         > …-> <REPO>/ts/node_modules

wc -l  ->  archive 972 lines, committed 976 lines
```

The README's fidelity table (lines 33-38) discloses fidelity for five files explicitly —
*"byte-identical"*, *"one line sanitized: an absolute repository path became `<REPO>`. Nothing
else changed"*, *"worktree paths sanitized"* — and then:

```
| `EVIDENCE-MANIFEST.txt` | relative paths + SHA-256 for all 971 preserved files |
```

No modification disclosed, in a table whose every other row discloses one. And the scope manifest
(lines 39-42) says *"`COMMON-BRIEF.md` and the two reviewer indexes had machine-specific paths
replaced, **each disclosed there**"* — three, not four.

**R4's carried note also checks out.** The README's provenance table gives
`Raw manifest | sha256 51894dd4…`; I hashed both files:

```
51894dd424c26b03784011f0772ba605dbab346eab6b528856bd003d3e69f87d   archive MANIFEST-sha256.txt
234503ed7f76053747a990f57c4449ffb81ea1cf3bddc38f3fb1b4edee7f9560   committed EVIDENCE-MANIFEST.txt
```

The row is labelled "Raw manifest" and is therefore correct, exactly as R4 said. A reader
verifying the *committed* file against it gets a mismatch with no explanation in the directory.

## Verdict: **CONFIRMED**

Deterministic, reproduced by `diff` and `shasum` against the source archive.

## Severity: **LOW** — sustained

I considered raising to MEDIUM and decided against it. The substitution is the project's own
disclosed convention applied consistently; no hash changed and no content was lost (R4 reports
971/971 hashes verified, and the two file hashes I checked independently are consistent with
that). Nothing downstream is misled about the evidence itself.

I also considered lowering to INFO and decided against it. It is a false statement of
*completeness* in the document another document explicitly nominates as the authority on that
exact question, and it is the stated basis on which 15 files were excluded from review. The
exclusion rests on marginally more than was established. LOW is the right place for that.

---

# R4-F3 — two gate guards certify a named SECTION while grepping the whole document

## The claim

`check-eval-codes.sh` and `check-type-strings.sh` print certifications naming §5.7.1 and §5.8 but
grep the entire 84KB proposal. Because section order is non-monotonic (§5.9 precedes §5.8),
`head -1` can select an occurrence from another section, and R4 demonstrated the guard printing
`6/6 published in §5.8 match eip712.ts exactly` while §5.8 publishes a transposed `EIP712Domain`.

## What I did

**First, the mechanism, read from the scripts:**

```
check-eval-codes.sh:38    grep -q "$code" "$SPEC" || missing="$missing $code"
check-type-strings.sh:29  spec_line="$(grep -oE "^ {4}${name}\([^)]*\)$" "$SPEC" | head -1 | ...)"
```

`$SPEC` is the whole proposal in both. Neither locates a section. The section number appears only
in the prose and in the printed line. Confirmed.

**Second, the non-monotonic order — verified, and it is real:**

```
grep -n "^### 5\." Sentinel_Protocol_Lab_Proposal_v0_2.md
  415: ### 5.5.1 RefusalRecord
  468: ### 5.9 Enumerations (normative)      <- §5.9 …
  486: ### 5.8 EIP-712 Type Strings          <- … precedes §5.8
  522: ### 5.6 EvidenceBundle
  540: ### 5.7 Supported Checks and Effects
```

**Third — and this is the part R4 did not do — I ran the CONTROL.** A mutation that passes proves
nothing unless the un-mutated form fails; without the control, "the guard passed" is compatible
with "the guard passes on everything".

```
CONTROL C1 — transpose §5.8's EIP712Domain, add NO decoy:
  ./scripts/check-type-strings.sh
  -> type strings: DRIFT in EIP712Domain
     spec  : EIP712Domain(string version,string name,…)
     source: EIP712Domain(string name,string version,…)
     exit=1                                     <- the guard DOES catch plain drift
```

**Fourth, R4's demonstration 2, re-applied by me:** keep the transposed §5.8 line, insert a
*correct* copy inside §5.9 at line 475.

```
grep -nE "^ {4}EIP712Domain\(" …
  475:    EIP712Domain(string name,string version,…)      <- §5.9 (468-486), correct decoy
  497:    EIP712Domain(string version,string name,…)      <- §5.8 (487-522), WRONG

./scripts/check-type-strings.sh
  -> type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)
     exit=0
```

**Reproduced exactly.** And the consequence is real: I computed both typehashes with viem —

```
correct     keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)")
            = 0x8b73c3c6…
transposed  = 0x4723509f…                       different
```

so an independent implementer building from §5.8 would produce signatures that never recover.

**Fifth, demonstration 1, with its own control:**

```
D1 — remove EVAL_MANDATE_PRINCIPAL_IS_OWNER from §5.7.1 (line 580), add a mention in "## 6. AI and Context Scope":
  occurrences inside §5.7.1 (571-606): 0        <- probe MOVED something
  occurrences in the file: 1, at line 609 (inside §6)
  ./scripts/check-eval-codes.sh -> eval codes: 41/41 engine checks documented in §5.7.1 (D-031)  exit=0

CONTROL C2 — remove it from the file entirely:
  ./scripts/check-eval-codes.sh -> 1 check(s) declared by the engine and absent from §5.7.1  exit=1
```

Both guards therefore measure **presence anywhere in the document**, and certify **presence in a
named section**.

**Revert:** restored from a backup taken before the first mutation; `cmp` against the pristine
copy clean; both guards re-run green afterwards; full 361-file `cmp` sweep clean.

## Is the transposition LIVE, or only demonstrated? — the coordinator's question, answered precisely

**Only demonstrated. It is NOT live at `7e0ab7f`.** I established this directly rather than
taking R4's word:

```
grep -nE "^ {4}(EIP712Domain|MandatePayload|PolicyPayload|ActionPayload|DecisionReceiptPayload|OverrideAuthorizationPayload)\(" …
  496, 498, 500, 502, 504, 506      — all six, and ONLY six occurrences in the whole file
§5.8 spans 486-521, so all six literals are inside §5.8 and there are no duplicates anywhere.
```

With no duplicate occurrence, `head -1` currently selects the §5.8 line for every one of the six,
so the printed claim is **true today**. Producing the defeat required me to make *two* edits — the
transposition *and* an inserted decoy earlier in the file. Likewise for §5.7.1: all 41 codes are
genuinely in 571-606 at this commit.

**Therefore this is an INSTRUMENT defect, not a live false claim.** Nothing is currently
mis-published. What is defective is that the guard's passing tells you less than its output says,
and the gap is invisible from the output.

R4 stated this distinction correctly and unprompted, and assigned severity on the instrument-defect
basis. I note that in R4's favour: it would have been easy to present the mutated output as a live
defect.

## Verdict: **CONFIRMED** (as an instrument defect)

## Severity: **MEDIUM** — sustained

**Why not HIGH.** The artifact is correct at this commit. §5.8 and §5.7.1 both genuinely publish
what they claim, the six type strings additionally agree across the four implementations that
carry them, and the guard does catch plain drift (my control C1). A HIGH would assert a live
defect and there is none.

**Why not LOW.** A guard that **passes while the property it names is violated** is this
repository's most expensive recorded failure mode — the secret guard that passed a real private
key was HIGH, three times. The property here protects §5.8, which exists specifically because an
independent reimplementation established §5 was not buildable without it, and the guard's own
header says a drifted published type string "is worse than an absent one: it is a confident, wrong
answer that an implementer has no way to detect". The guard is the only mechanical thing standing
behind that, and I made it certify a wrong string in under a minute. The two printed lines are
read as section-scoped evidence by `docs/gate-s2-evidence.md`.

**One correction to R4's smaller observations, which I checked:** R4 says
`check-eval-codes.sh` prints `${total}/${total}` so the ratio is an identity. **Confirmed** —
`scripts/check-eval-codes.sh:49`. That is a real cosmetic-honesty point and R4 was right to
record it below the finding rather than as one.

---

# R4-F4 — `session-state.md` §3 publishes 507/198 where the tree measures 513/209

## The claim

§3, the designated session entry point, publishes stale TypeScript and verifier counts and quotes
`TS_MIN_TESTS=507` where the gate constant is 513.

## What I did — every figure measured by me, not read

```
# What §3 publishes (docs/session-state.md:353-354, :359-360):
  "75/75 Foundry · 507/507 TypeScript · 198/198 verifier · 78 tamper cases over 30 modes …"
  "`FOUNDRY_MIN_TESTS=75`, `TS_MIN_TESTS=507`"

# TypeScript — my own reviewer baseline at this exact commit (evidence/r2/baseline-test.txt):
  ℹ tests 513 / pass 513 / fail 0 / skipped 0 / todo 0

# Verifier — run by me just now:
  cd verifier && python3 test_verifier.py   ->  Ran 209 tests in 54.948s   OK

# The gate's own constants:
  scripts/test.sh:187  FOUNDRY_MIN_TESTS=75
  scripts/test.sh:188  TS_MIN_TESTS=513
  scripts/test.sh:611  VERIFIER_MIN_TESTS=209
```

| figure | §3 says | I measured | |
|---|---|---|---|
| TypeScript | 507/507 | **513** | mismatch |
| verifier | 198/198 | **209** | mismatch |
| `TS_MIN_TESTS` | `507` | **`513`** at `test.sh:188` | mismatch |
| Foundry | 75/75 | `FOUNDRY_MIN_TESTS=75` — consistent; I did not run `forge test` | no discrepancy claimed |

**The drift is exactly the A-076 delta.** `decisions.md` A-076 records *"Suite 75 Foundry / **513**
TypeScript / **209** verifier; every floor ratcheted in the same edit as its suite"* — 507+6 and
198+11. §3 still reflects A-075's figures. A-076 enumerated the records it updated (§11.0's
heading, register §13.4) and `session-state.md` §3 is not among them.

**The section's own warnings, verified in place:**

```
docs/session-state.md:367  "**VERIFY BEFORE QUOTING — this line has been wrong four times.**"
docs/session-state.md:386  "All four counts above were re-measured 2026-08-16 (late session) and all four held."
```

**The forbidden-direction point, verified.** `scripts/test.sh:177` — *"RAISE A FLOOR IN THE SAME
EDIT AS THE SUITE IT BOUNDS. NEVER LOWER ONE TO MAKE A RUN PASS."* — and `:605` repeats it. R4
wrote "three separate places"; **I find two** (`grep -n -i "never lower|lower one" scripts/test.sh`
returns lines 177 and 605). A minor overcount that does not affect the point: a maintainer
reconciling `test.sh` against §3 would lower `TS_MIN_TESTS` from 513 to 507 and silently reopen the
six-test hole A-076 closed, in the exact direction the script twice forbids.

**Not disclosed as a known limit — checked.** `docs/exit-criterion-packet.md` §3b lists the
register's stale status column and does **not** list `session-state.md` §3; §6's prerequisite table
likewise. `docs/d055e-scope-manifest.md` names §3 only in the past tense as one of three tables that
*have* gone stale historically. **This instance is new and undisclosed.**

## Verdict: **CONFIRMED**

Every figure independently measured at `7e0ab7f`. R4's "three places" is two; nothing else in the
finding required correction.

## Severity: **MEDIUM** — sustained

**Why not LOW.** Three things. (1) It misquotes a gate floor constant in the one direction the
gate script twice forbids, and the misquote is in the document this project designates as its
memory — the reconciliation error it invites is a real six-test regression hole. (2) §3 is the
standing entry point: the project instruction is to start every session at `session-state.md`, and
the exit-criterion method is comparing measured state to recorded state, so a stale recorded state
corrupts the comparison at its source. (3) The line carries "this line has been wrong four times"
and "all four counts were re-measured and all four held" — a published number that was true once,
verbatim the project's own named defect class, in the sentence that exists to prevent it.

**Why not HIGH.** No code behaviour is affected. The gate carries the *correct* floors (513/209)
and would still catch a shrinking suite, so the enforcement is sound and only the description is
wrong. The accurate figures are one file away in `decisions.md` A-076. HIGH would require the
enforcement itself to be degraded and it is not.

---

# Adjudicator's provenance

**Mutations I made, all in worktree `w2`, all to one file:**
`Sentinel_Protocol_Lab_Proposal_v0_2.md` — four successive edits (control C1, demo D2, demo D1,
control C2), each applied from a backup taken before the first.

**Revert:** restored from that backup and verified with
`cmp "$PRISTINE/Sentinel_Protocol_Lab_Proposal_v0_2.md" "$W/Sentinel_Protocol_Lab_Proposal_v0_2.md"`
→ clean. Then a full sweep, `cmp` on all **361** files of the pristine copy → **zero DIFFERS**.
Both guards re-run green afterwards. `git diff HEAD --stat -- .` shows only the two provisioned
submodule symlink entries, which are present at baseline and are not mine. **`git checkout` was
never run and bare `git status` was never run.**

**Nothing was repaired.** No finding was fixed, no document edited, no live repository touched.

**What I did not do:** I did not run `forge test` (Foundry count taken from the constant, and no
Foundry discrepancy was claimed); I did not re-verify R4's 971/971 manifest hash sweep beyond the
two file-level hashes above; I did not read R4's `NULL-RESULTS.md`, `DEAD-PROBES.md`, `COVERAGE.md`
or `CRITIQUE.md` — only `REPORT.md`, so that my verification of each claim started from the tree
rather than from R4's account of what else it had checked.
