# ADJUDICATION — R3 adjudicates REVIEWER 1

**Adjudicator:** R3 (onchain and corpus reviewer of this round), acting as an independent
adjudicator. **I did not author any of R1's findings and I did not author the code they are
against.**
**Commit:** `7e0ab7f1057de278c09cc803ab4ca266f53399e1`
**Worktree used:** `_archive/sentinel-d055e-review/worktrees/w3` (my own, detached).
**The live repository `<REPO>` was never touched.**

## Method

For each finding I assumed the claim was WRONG until I had made its failure happen with a probe
I wrote myself. **I did not execute `evidence/r1/probes/probe-snapshot-reachable.sh` at any
point**, and no verdict below rests on re-running an R1 artifact. Where I read an R1 artifact it
is named as corroboration only.

My baseline on this worktree, established before this adjudication began: `forge test` 75/75,
`npm test` 513/513, `git diff HEAD --stat -- .` showing only the two provisioned submodule
symlinks. Re-verified clean after every probe below.

## Verdict summary

| finding | R1's severity | verdict | **my severity** | direction |
|---|---|---|---|---|
| **R1-F1** — the gate snapshot is reachable and corruptible mid-run | CRITICAL | **CONFIRMED** | **CRITICAL** | unchanged, and my evidence is stronger than R1's |
| **R1-F2** — `check-review-scope.sh` reports "all assigned" after measuring nothing | HIGH | **CONFIRMED** | **MEDIUM** | lowered, reasoning below |
| **R1-F3** — nothing invokes `check-review-scope.sh` | MEDIUM | **CONFIRMED (as fact)** | **LOW** | lowered, reasoning below |
| **R1-F4** — register §13.6 still says "Not built, deliberately" | LOW | **CONFIRMED** | **LOW** | unchanged |
| **R1-F5** — the coverage boundary calls a deep run "this default" | LOW | **CONFIRMED** | **LOW** | unchanged |

Two downgrades. Both carry recorded reasoning, as D-056(e) requires, and both are mine — they
are recommendations to John, not decisions.

---

# R1-F1 — CONFIRMED. Severity **CRITICAL** (unchanged).

## The claim

That `scripts/test.sh`'s bootstrap comment, `check-gate-immutability.sh`'s header, and
`docs/decisions.md` A-076(1) are all false where they say *"from the exec onward bash reads a
private file nobody has a path to, so an edit cannot corrupt the running parser AT ALL; the
failure mode is REMOVED, not detected"* — because `SENTINEL_GATE_SNAPSHOT` is exported to every
child and the snapshot path is on the process command line, so the snapshot is writable by any
descendant or sibling running as the same user.

I was asked to be especially hard on this one. Three sub-questions were put to me explicitly and
I answer each with my own measurement.

## What I did

### Step 1 — the two access routes, read from source

* `SENTINEL_GATE_SNAPSHOT="$_gate_snap" … exec bash "$_gate_snap" "$@"` (test.sh:82-85). A
  prefix assignment on `exec` places the variable in the exec'd process's **environment**, so
  every descendant inherits it. The bootstrap's own comment says so: *"But it is EXPORTED to
  every child process."*
* After the exec the argv is `bash /var/…/sentinel-gate.XXXXXXXX`. `test.sh:73-81` and A-076(e)
  both publish this in order to tell operators to use `pkill -f sentinel-gate`.
* `mktemp` creates the snapshot mode 0600 **owned by the same uid**, so same-user write is
  unrestricted. I verified writability from a sibling process (`[ -w "$snap" ]` → true, uid 501).

### Step 2 — my own synthetic probe, written from scratch, with a working control

I extracted the shipped bootstrap with my own `awk` (104 lines, 4 `SENTINEL_GATE_SNAPSHOT`
occurrences — extraction verified, not assumed), built my own subject bodies, and ran everything
under an isolated `TMPDIR`. Scripts: `scratchpad/adj/{mkbody.sh,child-env.sh,bootstrap.sh}`.

```
ARM0  CONTROL — identical body, NO bootstrap, same in-place edit
      exit 127 · BODY COMPLETED: NO · shell corruption: YES
      -> the probe is dangerous; anything below is not passing for the wrong reason

ARM1  shipped bootstrap; a CHILD reads its inherited SENTINEL_GATE_SNAPSHOT and rewrites
      that file in place (truncate+write, same inode, 40 lines prepended)
        [child] inherited SENTINEL_GATE_SNAPSHOT=…/sentinel-gate.rMlLQuJZ
        [child] and it is WRITABLE by me
        …/sentinel-gate.rMlLQuJZ: line 4126: unexpected EOF while looking for matching `"'
      exit code: 0 · BODY COMPLETED: NO · original source UNCHANGED

ARM2  a SIBLING with SENTINEL_GATE_SNAPSHOT unset, recovering the path from `ps` alone
        [sibling] ps says the running parser is reading: …/sentinel-gate.2EMHZjn1
        …/sentinel-gate.2EMHZjn1: line 4126: unexpected EOF while looking for matching `"'
      exit code: 0 · BODY COMPLETED: NO · source-changed diagnostic: NO
```

I also swept subject sizes from 6.7 KB to 85.6 KB (9 sizes) to rule out "the file was already
fully buffered" as a confound: **every size was corrupted, every one exited 0.**

### Step 3 — the test R1 did NOT do: the REAL shipped gate, end to end

R1 established this only on a synthetic body. I attacked the real `./scripts/test.sh` in my
worktree with a sibling that knows nothing but what `ps` shows, and I verified for every trial
that the edit actually landed (same inode, size 73 660 → 74 410) before believing any result.

| trial | edit at | edit verified | exit | `GATE PASSED` | shell corruption | `GATE SOURCE CHANGED` |
|---|---|---|---|---|---|---|
| 1 | t=12 s | yes | 0 | **printed** | none | — |
| 2 | t=12 s | yes | 0 | **printed** | none | — |
| 3 | t=2 s | yes | **127** | no | `line 132: EXIT:: command not found` | **no** |
| 4 | t=20 s | yes | **127** | no | yes | **no** |
| 5 | t=30 s | yes | **127** | no | `line 304: erifier: command not found` | **no** |
| 6 | t=45 s | yes | **0** | **no** | `line 591: syntax error near unexpected token '('` | **no** |
| 7 | t=45 s | yes | **0** | **no** | `line 591: syntax error near unexpected token '('` | **no** |
| 8 | t=45 s | yes | **0** | **no** | `line 591: syntax error near unexpected token '('` | **no** |

**6 of 8 verified trials against the real gate were corrupted. Three of them produced exit 0
with no `GATE PASSED` and no diagnostic** — which is `docs/v1-1-register.md` §13.6's description
of the original A-075 incident, word for word: *"threw a syntax error, never printed GATE
PASSED, and EXITED 0 — a run that looks green to anything checking the status and is worthless."*

Note trial 5's `erifier: command not found` — bash resumed mid-token inside the word
`verifier`. That is the shifted-byte-offset failure mode itself, in the shipped gate.

## The three questions I was asked

**1. Does the exploit actually reproduce?** **Yes** — on my own synthetic subject at nine sizes
by two independent access routes, and on the real shipped gate in 6 of 8 verified trials.

**2. Does it produce exit 0 with no GATE PASSED?** **Yes.** Both synthetic arms, and real-gate
trials 6, 7 and 8. The mechanism is exactly as R1 describes: the `_gate_exit` trap re-hashes
`$SENTINEL_GATE_SOURCE` — the ORIGINAL — which genuinely did not change, so
`_gate_source_unchanged` returns true, `rc` is left at whatever the last command produced, and
no diagnostic is emitted. **The instrument built to refuse a zero exit to a compromised run
affirmatively certifies it.** I confirmed `src_diag=0` on every corrupted trial.

**3. Does `check-gate-immutability.sh` really miss it?** **Yes, and I have it doing so inside the
very run it failed to protect.** `evidence/r3/../scratchpad/adj/real-r45-19350.out`:

```
line   1-19 :  == gate immutability (D-056(b)) ==
               extracted 104 lines of bootstrap verbatim from scripts/test.sh
               1. unchanged source                     -> exit 0 and the body ran
               2a. CONTROL                             -> an unprotected script IS corrupted
               2b. the protected script under the SAME edit
                     the body ran to completion — the mid-run edit did NOT corrupt the parser
                     no syntax error or shifted-offset damage in the output
                     exit 4 — a changed source is refused a zero exit
               …
line 930    :  …/sentinel-gate.RjizIQjs: line 591: syntax error near unexpected token `('
exit        :  0        GATE PASSED: not printed        GATE SOURCE CHANGED: not printed
```

Structurally, R1's reading of the harness is exactly right and I verified it line by line:

* `grep -n edit_in_place scripts/check-gate-immutability.sh` → calls at 134 (`$CTRL`),
  150 (`$SUBJ2`), 235 (`$SUBJ6`). **All three targets are the ORIGINAL subject file. No property
  ever edits a snapshot.**
* Property 5 sets `SENTINEL_GATE_SNAPSHOT="$WORK/some-other-parents-snapshot"` (line 229) and
  `grep -n some-other-parents` shows lines 229-230 only — **the file is never created**. The
  property then edits `$SUBJ6`, the original. It asserts that a child protects *itself*; it never
  asserts that a child cannot reach the *parent's real* snapshot.

## The one thing I found that R1 did not, and it cuts against R1's framing slightly

**The corruption is non-deterministic.** Two of my eight real-gate trials (both at t=12 s)
completed normally and printed `GATE PASSED` with the edit demonstrably applied. Whether the run
is corrupted depends on where bash's parse point sits relative to the rewrite at the moment it
next refills from disk. R1's report presents the outcome as deterministic.

**This does not reduce the severity — it raises it.** A certification instrument that is
corrupted on roughly three quarters of attempts and silently green on the rest is worse than one
that fails predictably, because the clean runs are indistinguishable from real passes and there
is no artifact separating them. It also means a single negative trial is not evidence of safety,
which is worth recording for whoever verifies the repair.

## Verdict: **CONFIRMED**

## Severity: **CRITICAL** (I keep R1's severity)

Reasoning, stated because a Critical blocks exit and must be defensible:

1. **The falsified claim is unqualified and canonical.** `docs/decisions.md` A-076(1) is a signed
   record and states *"an edit cannot corrupt the running parser AT ALL; the failure mode is
   REMOVED, not detected."* The failure mode is not removed. It was relocated to a path the same
   commit published in two places.
2. **The artifact is the project's certification instrument.** Both signed gate packs are gate
   runs. A gate run that exits 0 without `GATE PASSED` is precisely the artifact §13.6 exists to
   prevent, and it is now reachable through the repair for it.
3. **The failure is silent and the guard is complicit.** Exit 0, no `GATE PASSED`, no diagnostic
   — and `check-gate-immutability.sh` printing its properties met in the same run.
4. **A-076's stated residuals do not cover it.** (a) scopes the harness to a synthetic body and to
   files other than `scripts/test.sh`; (b) covers a torn read of the source. Neither contemplates
   the snapshot being writable.
5. **It is not a re-report.** §13.6 records the original defect against `scripts/test.sh`. This is
   that the repair is incomplete while the record asserts completeness — common-brief Rule 5.

**One qualification I attach for John, because severity should not be inflated by threat-model
drift.** The attacker here is a same-uid process: a gate child stage, a concurrent agent, or the
operator's own editor. This is not a privilege boundary and it is not a remote attack. But that
is *exactly* the threat model §13.6 was written for — *"found twice in one session, both times by
the agent doing it to itself"* — so the finding lands squarely inside the model the protection
was built against, and CRITICAL is right on those terms rather than on a security-boundary
reading.

## Repair note (offered, not prescribed — I am adjudicating, not repairing)

Two shapes exist and both are John's call, not an agent's: make the snapshot unreachable
(`unset SENTINEL_GATE_SNAPSHOT` after the re-exec test, unlink the snapshot immediately after
`exec` so only the open fd survives), or make the corruption detectable (have the trap hash the
SNAPSHOT as well as the source). **The second is the design John rejected at D-056(b) and it
fails for his stated reason** — a trap living in the corrupted body may never run. The first
is the one that matches the argument the bootstrap already states. **Unlinking would also break
`pkill -f sentinel-gate`, which A-076(e) has already deferred as operational documentation, so
the two interact and that is a decision, not an implementation detail.**

---

# R1-F2 — CONFIRMED. Severity **MEDIUM** (lowered from HIGH; reasoning recorded).

## The claim

That `scripts/check-review-scope.sh`'s second half — the remediation-surface check D-056(d)
required — prints a completeness claim and exits 0 after measuring nothing, whenever its base ref
does not resolve.

## What I did

I did not use R1's probe value. I read the code, established my own baseline, then used two
failure shapes of my own choosing.

**Source, verified myself:**
```
32 : set -uo pipefail                      <- no `set -e`
109: since="${SENTINEL_SCOPE_BASE:-a89c255~1}"
137: done < <(git diff --name-only "$since"..HEAD 2>/dev/null)
138: echo "  remediation surface: $touched file(s) changed since A-070, all assigned"
```
`git diff`'s stderr is discarded at line 137 and its exit status is unreachable — it is the
right-hand side of a process substitution, so `pipefail` cannot see it and there is no `set -e`
to abort on it. `touched` is initialised to 0 at line 126. Line 138 runs unconditionally.

**Baseline (mine):**
```
review scope: R1=175  R2=46  R3=150  (assigned 371 of 371 tracked files)
  remediation surface: 37 file(s) changed since A-070, all assigned
  preservation-only:   15 file(s) (round-six record; …)
rc=0
```
Ground truth, measured separately: `git diff --name-only 'a89c255~1'..HEAD | wc -l` → **52**
(= 37 remediation + 15 preservation). The baseline is internally consistent.

**Probe A — a base object that does not exist (my value, not R1's):**
```
$ SENTINEL_SCOPE_BASE=0000000000000000000000000000000000000000 ./scripts/check-review-scope.sh
review scope: R1=175  R2=46  R3=150  (assigned 371 of 371 tracked files)
  remediation surface: 0 file(s) changed since A-070, all assigned
  reviewer 4 is unassigned BY DESIGN (D-056(d)) and ranges over every surface above
rc=0
```

**Probe B — a well-formed ref name this repository does not have:**
```
$ SENTINEL_SCOPE_BASE=refs/heads/no-such-branch ./scripts/check-review-scope.sh
  remediation surface: 0 file(s) changed since A-070, all assigned
rc=0
```

**Probe C — what the discarded stderr actually said:**
```
$ git diff --name-only 0000000000000000000000000000000000000000..HEAD
fatal: Invalid revision range 0000000000000000000000000000000000000000..HEAD
git rc=128
```

## What I observed

The mechanism is exactly as R1 states. A `fatal` from git, exit 128, is swallowed; the loop body
never runs; `touched` stays 0; and the script prints **"0 file(s) changed since A-070, all
assigned"** and exits 0. The words "all assigned" are a completeness claim discharged by zero
measurement, which is verbatim the class the common brief names: *"Absence can read as
agreement."* The `preservation-only` line silently disappearing is the only tell.

## Verdict: **CONFIRMED**

## Severity: **MEDIUM** (lowered from HIGH)

I lower it, and I record why rather than downgrading quietly — which is the T2 discipline John
applied to his own acceptance at D-056(a).

**What holds R1's case up:**
* The guard exists precisely so a completeness claim is mechanical rather than asserted, and
  `docs/d055e-scope-manifest.md:9` calls it *"the part that matters"*.
* The silent-failure shape is the project's most-repeated defect class.

**What I weighed against HIGH:**
1. **The first and load-bearing half is unaffected.** D-056(d)'s actual requirement is that every
   tracked file be assigned to exactly one reviewer. That half reads `git ls-files` with no
   suppression and prints `371 of 371`; it cannot silently degrade to a green claim (a failure
   would print `0 of 0`, which is visibly absurd). **Only the secondary remediation-surface count
   is affected**, and R1's own quotation of the header shows the header's central promise —
   *"this exits non-zero if any tracked file is assigned to NO reviewer"* — belongs to the
   unaffected half.
2. **The trigger is not present in the environment the tool is used in.** I verified
   `git rev-parse 'a89c255~1'` resolves in this detached review worktree (→ `140c59e5…`), as it
   does in the live repository, because the worktree shares the object store. R1's enumerated
   triggers — shallow clone, unfetched clone, history rewrite, abbreviated-SHA ambiguity — are
   real but none of them describes how or where this script is run.
3. **The false output contradicts the record it would be used to support.** It prints `0` where
   the scope manifest documents `37`, and drops a line the manifest also documents. A reader
   comparing the two — which is the only reason to run the script — sees the disagreement.
4. **It is a single-use dispatch instrument, not a durable gate property.** Its output is read
   once, by a person, at the moment of dispatch.

MEDIUM is where I land: a real silent-failure defect in a claim-bearing instrument, in its
secondary half, with a visible tell and a trigger that is not the operating environment.
**I am not confident enough in the gap between MEDIUM and HIGH to argue anyone out of HIGH** —
if John reads the remediation-surface half as equally load-bearing with the assignment half,
HIGH is defensible on the same facts. The fix is two characters either way (`set -e`, or capture
`git diff` to a file and test its status), so the severity call has no bearing on the cost.

---

# R1-F3 — CONFIRMED AS FACT. Severity **LOW** (lowered from MEDIUM; reasoning recorded).

## The claim

That nothing invokes `check-review-scope.sh`, so its header sentence *"A file added between now
and dispatch turns this red rather than sliding into a gap"* describes a mechanism that does not
exist.

## What I did

My own exhaustive search over the tracked tree, plus a direct reading of every invocation site:

```
$ git grep -n 'check-review-scope' -- .
docs/d055e-scope-manifest.md:9, :31, :63, :69, :78     <- prose only, five hits, one document

$ ls .githooks/ && cat .githooks/pre-commit
pre-commit  ->  exec "$repo_root/scripts/check-secrets.sh" --staged

$ grep -n 'scripts/check-' scripts/test.sh
131 check-gate-immutability.sh   134 check-secrets.sh     137 check-rename-gate.sh
140 check-label-prompt.sh        147 check-label-integrity.sh
150 check-type-strings.sh        153 check-eval-codes.sh
161 check-class-coverage.sh      167 check-vendor-honesty.sh
```

**Nine `check-*.sh` scripts are wired into the gate. `check-review-scope.sh` is not one of them,
and the only git hook runs `check-secrets.sh`.** R1's factual claim is exactly right.

## What I observed that changes the reading

`docs/d055e-scope-manifest.md:31` — the authoritative document for this partition — says:

> Current state at the provenance checkpoint, from the script's actual output: **R1=175 · R2=46 ·
> R3=150 … Do not trust that line — run `./scripts/check-review-scope.sh`.**

**The manifest explicitly instructs the reader to run it by hand and explicitly tells them not to
trust the transcribed number.** So the project does not, in its authoritative document, rely on
automatic invocation. The overstatement is confined to the script's own header, and even there
the sentence R1 quotes is ambiguous between "this script exits red" (true) and "this happens
automatically" (false).

## Verdict: **CONFIRMED (as fact)**

The fact — nothing invokes it — is established. The header sentence does oversell, in a file
whose header has already been corrected once for describing a mechanism it lacks (lines 16-21,
the overlap-detection correction). That pattern is real and worth recording.

## Severity: **LOW** (lowered from MEDIUM)

1. The authoritative manifest already discloses the manual nature *and* tells the reader the
   transcribed numbers are untrustworthy. That is the disclosure the header lacks.
2. This is a one-shot dispatch instrument. Wiring it into the gate would be wrong on its own
   terms — the partition is specific to D-055(e) and would fail forever once the round ends and
   files change. "Not in the gate" is arguably correct design here, not an omission.
3. No executable consequence and no false green: the script, when run, is correct (modulo F2).

**Where I agree with R1 and it matters:** F2 and F3 compound. The one instrument standing behind
the round's coverage claim both fails silently in its second half and is run only if somebody
remembers. Neither alone is more than MEDIUM/LOW; **together they mean "the scope was verified
mechanically" is a claim resting on one manual invocation whose secondary half cannot fail
loudly.** That compound is worth John's attention even at LOW+MEDIUM.

---

# R1-F4 — CONFIRMED. Severity **LOW** (unchanged).

## The claim

That `docs/v1-1-register.md` §13.6 still says the gate-corruption protection is *"Not built,
deliberately"* and still recommends the design John rejected.

## What I did

Read both records at the frozen commit.

**Register §13.6, verbatim, as it stands:**
> …there is a cheap mechanical one: **have the gate hash its own file at start and re-check at
> exit, failing loudly if it changed underneath itself.** Roughly four lines.
>
> **Not built, deliberately:** it is new tooling and outside D-055(d)'s four prerequisites…

**`docs/decisions.md` D-056(b), verbatim:**
> **THE GATE-MUTATION PROTECTION, AND JOHN REJECTED THE AGENT'S PROPOSED DESIGN ON ITS MERITS.**
> A-076's predecessor recorded a naive remedy — hash the script at start and re-check at the end.
> **John ruled it insufficient, with the reason: "The ending check can itself be skipped or
> corrupted when bash resumes at a shifted byte offset."**

**`docs/decisions.md` A-076(1):** *"THE GATE CAN NO LONGER BE MUTATED MID-RUN…"*

**And the register's own A-076 markers:** `grep -n 'A-076' docs/v1-1-register.md` returns lines
773, 774, 784, 786, 787 — the rows for `D-09`, `D-10`, `G-5`, `H-5`, `H-8`. **§13.6 is not among
them.** R1's account is accurate in every particular.

## Verdict: **CONFIRMED**

## Severity: **LOW** (unchanged)

A stale canonical record with no executable consequence. The register is additive by house rule
and §13.4 carries its own warning that hand-maintained status goes stale — but that warning is
attached to the adjudication table, not to §13.6, and §13.6 is not a status cell: it is a
narrative section asserting that a thing does not exist and prescribing a remedy that was ruled
insufficient two days later.

**R1's own closing observation is the sharpest thing about this finding and I endorse it:** given
R1-F1, *"the stale text is closer to the truth than the current record is."* §13.6 says no
protection exists; A-076(1) says the failure mode is removed. **Measured, neither is right — the
protection exists and the failure mode is not removed.** Whoever repairs F1 should correct §13.6
and A-076(1) in the same edit, and should not simply move §13.6 to FIXED.

---

# R1-F5 — CONFIRMED. Severity **LOW** (unchanged).

## The claim

That the `COVERAGE BOUNDARY` block — which the gate titles *"read this, not the pass count"* —
ends with a sentence that is false on exactly the deep runs that constitute gate evidence:
*"For gate evidence use the deep profile — ./scripts/test.sh --gate — not this default."*

## What I did

**I ran my own deep gate.** I did not read R1's `deep-gate-run.txt` for the verdict; I cite it
below only as corroboration after the fact.

```
$ cd <worktree w3> && forge build --root contracts && ./scripts/test.sh --gate
```

Evidence from **my** run (`scratchpad/adj/mydeep.out`, exit 0):

```
line  127 :  == solidity build + tests (profile: gate) ==      <- it IS the deep profile
line  928 :  == §7.1 corpus executed, and the committed views verified (A-029) ==
line  930 :  corpus: 50 fixtures executed; committed views verified FILE BY FILE
line  931 :    corpus verdicts: 51 result files identical to the committed set
                                                                 ^ deep-profile-only stages ran
line  939 :  GATE PASSED
line  942 :  COVERAGE BOUNDARY (house rule 4) — read this, not the pass count
last line :  For gate evidence use the deep profile — ./scripts/test.sh --gate — not this default.
```

**Source, confirming it is structural and not incidental:**
```
785: if [ "$fail" -ne 0 ]; then
786:     echo -e "\033[31mGATE FAILED\033[0m"
787:     exit 1
788: fi
790: cat <<'COVERAGE'
791: GATE PASSED
...
1141: For gate evidence use the deep profile — ./scripts/test.sh --gate — not this default.
1142: COVERAGE
```
The heredoc — `GATE PASSED` and the whole coverage boundary together — is guarded **only** on
`$fail`. `grep -n '\$PROFILE' scripts/test.sh` returns lines 190, 218 and 392 and nothing near
1141. **There is no profile guard on this block, so the sentence is emitted verbatim on every
passing run of either profile.**

## Verdict: **CONFIRMED**

Reproduced independently on my own deep run. R1's `deep-gate-run.txt` shows the same thing, which
I checked only after reaching my own result.

## Severity: **LOW** (unchanged)

No executable consequence. It is a false printed claim, and it sits in the one block the project
instructs people to read *instead of* the result — which is why it is worth reporting at all
rather than dismissing as a typo. It is false in the direction that invites a reader to discard a
valid deep run as a default one, i.e. it degrades evidence rather than inflating it.

**One thing R1 did not say and I will:** the fix is not simply a `$PROFILE` conditional. On a
FAST run the sentence is true and useful, and on a DEEP run the correct statement is the opposite
("this WAS the deep profile"). A conditional is right, but writing it is writing a new claim
about what the block asserts, which is a decision rather than a typo fix.

---

# What I could NOT establish, stated so a null is not read as coverage

1. **I did not determine the precise bash mechanism behind R1-F1's non-determinism.** I measured
   the outcome (6 of 8 real-gate trials corrupted, 2 clean, both clean ones at t=12 s) but not
   why the parse point sometimes escapes. `lsof` reported the script fd at EOF within one second
   on both corrupted and uncorrupted runs, so **fd offset is not a usable predictor and I discard
   my own early inference from it.** Anyone verifying a repair for F1 must therefore run several
   trials at several timings; a single clean run proves nothing.
2. **My first real-gate trial was very nearly a dead probe and I am recording it.** My initial
   `ps` selector (`grep -o '/[^ ]*sentinel-gate\.[A-Za-z0-9]*'`) matched a zero-length suffix and
   produced three runs reporting `snapshot vanished before edit`. Those three measured NOTHING
   and are excluded from every count above. The eight trials in the F1 table all carry a verified
   in-place edit: same inode before and after, size 73 660 → 74 410. **Had I not added that
   verification, "the gate survived" would have looked identical to "the probe never fired."**
3. **I did not adjudicate R1's NULL-RESULTS, DEAD-PROBES, COVERAGE, CRITIQUE or ATTESTATION.**
   The task named the five findings. I read `REPORT.md` in full and nothing else of R1's except
   `deep-gate-run.txt`, cited once as post-hoc corroboration.
4. **I did not assess whether R1's findings are complete for its surface.** Adjudication is
   per-claim; absence of other findings is not evidence of their absence.

# Provenance and tree state

**Tools:** bash 3.2.57(1) (arm64-apple-darwin25), forge 1.7.1 / solc 0.8.28, node v26.3.0,
python3 (system), git 2.50.1, darwin 25.5.0 arm64.

**Everything I mutated:** only files under
`<SCRATCH>/scratchpad/adj/`
and **transient gate snapshots under the system `$TMPDIR`**, which are the gate's own temporary
files. **No file in the repository was written at any point during this adjudication.** The one
repository-adjacent side effect — snapshot files left in `$TMPDIR` by corrupted runs that never
reached their cleanup trap — I removed afterwards (`ls …/sentinel-gate.*` → 0).

**Tree verified after every probe and again at the end:**
```
$ diff -r <dir> <pristine>/<dir>   for contracts/src contracts/test ts/src ts/test
                                       fixtures scripts docs
  CLEAN on all seven
$ git diff HEAD --stat -- .
  contracts/lib/forge-std | 2 +-   contracts/lib/openzeppelin-contracts | 2 +-
  (the two provisioned symlinks only — identical to my recorded baseline)
```

`./scripts/test.sh --gate` on the untouched tree at this commit: **GATE PASSED, exit 0**, with
the deep-only corpus stage reporting *"50 fixtures executed; committed views verified FILE BY
FILE"* and *"corpus verdicts: 51 result files identical to the committed set."* So every
corrupted run above was caused by my probe and nothing else, and the tree I adjudicated on is
the tree R1 reviewed.

# Note on my own standing

I am R3 in this round. **None of these five findings overlaps anything in my own report** — mine
are on `contracts/src/**`, `ts/src/corpus/**`, `ts/src/ablation/**` and `fixtures/corpus/**`;
R1's are on `scripts/**` and the canonical records. I have no finding whose standing is improved
or damaged by any verdict above.

One point of contact worth disclosing: **my own R3-F6 and R1-F1 are instances of the same named
pattern** — a repair that generalises the demonstration rather than the argument. That did not
influence any verdict here; I confirmed R1-F1 on measurement, and my two downgrades (F2, F3) cut
against, not for, that shared framing.
