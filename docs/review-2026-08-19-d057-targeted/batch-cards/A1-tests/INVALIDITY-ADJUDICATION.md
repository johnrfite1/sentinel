# A1 — INDEPENDENT ADJUDICATION OF TWO INVALIDITY CLAIMS

**Adjudicator:** an independent agent that wrote neither `a1-repo-identity.sh` nor the
implementation under it. **Standing rule applied:** D-058(1) / D-060(5) — an implementer may not
modify, weaken, relocate or delete an independent test; an invalidity claim stops work and must be
independently confirmed before anything is replaced. This document is that confirmation step, and
it was written to try to REFUTE both claims.

**The harness was not edited.** `shasum -a 256` of
`docs/review-2026-08-19-d057-targeted/batch-cards/A1-tests/a1-repo-identity.sh` is
`7be56445cc0510c03753011e21d2cea949e766a42545603289f889579145b82d` in the primary tree and the
same in the implementation worktree, before and after this adjudication. Nothing in the repository
was repaired, and the implementation worktree is at `70bf654` with no working-tree modification.

---

## VERDICTS

| Claim | Verdict |
|---|---|
| **1 — case 4 (line 290) contradicts case 2 (line 232)** | **CONFIRMED-INVALID.** Case 4's REQUIRED line *and* its CONTROL cannot hold together with case 2's REQUIRED line. **Case 2 is the correct one; case 4 is the defective one.** |
| **2 — case 5c is unsatisfiable with case 5b** | **REFUTED.** An implementation that satisfies both was written and run against the unmodified harness: `5b PASS`, `5c PASS (true=101, observed=101)`, every case-5 and case-6 control intact. |

The most valuable outcome first: **Claim 2 is wrong, and the implementer should build the design
described in §2.4.** Claim 1 is right, and §1.6 says what a corrected case 4 has to do instead.

---

## METHOD

Four implementations were placed under the **byte-identical, unmodified** harness. Each run is the
harness's own verdict, not mine. Variants B, C and D live only in throwaway clones under the
session scratch area; none of them was ever written into the repository or the worktree.

| Variant | What is under the harness | Harness exit |
|---|---|---|
| **A** | the committed first implementation attempt, worktree `HEAD` = `70bf654` | 2 |
| **B** | A + "refuse when the CALLER's directory lies in no repository" — the maximal attempt to satisfy case 4 | 1 |
| **C** | A + the case-5 repair described in §2.4 | 2 |
| **D** | A + a discriminator on the stdout *target* — the only mechanism that can tell line 232 from line 290 | 2 |

A supplementary probe, `replicate24.sh`, reproduces the harness's case-1b → case-2 → case-3 →
case-4 sequence verbatim and fingerprints the subject tree and the environment at both measurement
points.

---

## 1. CLAIM 1 — case 4 versus case 2: **CONFIRMED-INVALID**

### 1.1 The two lines, exactly

```
232|     out="$( cd "$PLAIN" && "$SUT/scripts/$s.sh" 2>&1 )"; rc=$?          # case 2 (REQUIRED)
290|     ( cd "$PLAIN" && "$SUT/scripts/$s.sh" >/dev/null 2>&1 ); rc=$?      # case 4 (REQUIRED)
```

Same subject, same loop variable, same `PLAIN`, same absence of any shim or environment override.
The **only** difference is where the two standard streams point: a command-substitution pipe at
232, `/dev/null` at 290.

### 1.2 The derivation

- Line 215, `CONTROL 1b`, requires all 12 runnable entry points to **exit 0** from the repository
  root. Those exit codes are what lines 210–212 store in `$WORK/base/$s.rc`.
- Lines 233–238, `REQUIRED 2`, require output **and** exit code from `PLAIN` to equal the stored
  base values. Combined with 1b: **`rc == 0` for all 12 from `PLAIN`.**
- Lines 288–294, `REQUIRED 4`, require `four_open == 0`, i.e. **`rc != 0` for all 12 from
  `PLAIN`.**
- Lines 295–296, `CONTROL 4`, require `four_closed > 0`, i.e. at least one `rc != 0`.

`rc == 0 for all` and `rc != 0 for all` are the same measurement of the same command. Case 4's
CONTROL is the weaker half of the same contradiction: it needs one refusal that case 2 forbids.

The escape "print Sentinel's answer byte-identically **and** exit non-zero" is closed by CONTROL
1b: line 233 compares `rc` as well as `out`, and 1b pins the base `rc` at 0. Making the root run
exit non-zero to match would fail 1b, and a failing CONTROL sets harness exit 2, under which no
REQUIRED line is evidence at all (lines 507–511).

### 1.3 Evidence — the two measurement points are the same state

`replicate24.sh` ran the harness's case-1b, case-2, case-3 (including the 3a plant-and-remove) and
case-4 blocks in order against worktree `HEAD`, fingerprinting between them:

```
FINGERPRINT at the case-2 point : e3b0c44298fc1c14      (git status --porcelain -z -uall | shasum)
ENV        at the case-2 point : 6a613af53bec3036
FINGERPRINT at the case-4 point : e3b0c44298fc1c14
ENV        at the case-4 point : 6a613af53bec3036
identical rc at both measurement points: 12 of 12   (differing: 0)
```

**Establishes:** the subject tree (tracked, staged and untracked) and the environment are
byte-identical at both points, so case 3 leaves nothing behind that could legitimately change an
answer, and the two lines measure one deterministic quantity.
**Does not establish:** anything about implementations that are deliberately non-deterministic or
that inspect their own file descriptors — see §1.5.

### 1.4 Evidence — the paired variants

| Line | Variant A (`HEAD`) | Variant B |
|---|---|---|
| `case 1b CONTROL` | PASS | PASS |
| `case 2 REQUIRED` | **PASS** — 0 differ | **FAIL** — 12 differ, 0 exit 0 |
| `case 3 REQUIRED` | PASS — 0 differ | PASS — 0 differ |
| `case 4 REQUIRED` | **FAIL** — 12 of 12 exit 0 | **PASS** — 0 of 12 exit 0 |
| `case 4 CONTROL` | **FAIL** — 0 of 12 refuse | **PASS** — 12 of 12 refuse |

Variant B is the maximal attempt: it refuses only when the **caller's** directory lies in no
repository at all, so a caller standing in a foreign repository is still allowed through and
**case 3 stays green**. The tension is therefore isolated to exactly case 2 versus case 4 — it is
not a general "identity" problem, and it is not case 3's doing.

Read together: case 2 passing forces case 4 and its control to fail; case 4 and its control
passing forces case 2 to fail. Both directions were measured, by the harness, against real
implementations.

### 1.5 The one mechanism that satisfies both, and why the harness itself rejects it

The two invocations differ in exactly one observable, and that observable *is* readable from inside
a script (`[ -c /dev/stdout ]` is false for a pipe, true for `/dev/null`). Variant D keys refusal on
it. The harness's verdict:

```
case 2   REQUIRED PASS   all 12 give the Sentinel answer from an unrelated directory (0 differ)
case 3   REQUIRED PASS   all 12 give the Sentinel answer from inside a foreign repository
case 4   REQUIRED PASS   no entry point reports a result with identity unresolved (0 of 12 exit 0)
case 4   CONTROL  PASS   12 of 12 do refuse
case 7   CONTROL  FAIL   staged deletion accepted: guard=2 hook=2 commit=1
case 13c CONTROL  FAIL   a matching repository with hooks installed still commits (exit 1)
CONTROL failed : 2   -> harness exit 2
```

Case 7 is the **protected control** the card takes from D-059(3), and line 344 invokes
`./scripts/check-secrets.sh --staged >/dev/null 2>&1` while line 347 requires that exit to be `0`.
Line 491's commit control does the same through the hook. A script that refuses because its stdout
is `/dev/null` must fail both. So the single mechanism capable of satisfying cases 2 and 4 together
is foreclosed by the harness's own protected control, and the run ends at exit 2 where nothing
above is evidence.

It is worth saying plainly that this mechanism is not a candidate on the merits either. It makes
refusal depend on how the caller redirected output — caller-dependence of the crudest kind, which
is exactly what D-060(2) removes — and it would refuse in ordinary use whenever anyone runs a guard
with its output discarded. It is named here only to close the last hole.

### 1.6 Root cause, and what a corrected case 4 must do

Case 4's premise is never instantiated by its fixture. Under D-060(2), *"identity derives from
`BASH_SOURCE` or the hook's own location"* and *"a check invoked from another directory still
checks Sentinel"*. In both case 2 and case 4 the script being run is
`"$SUT/scripts/$s.sh"` — a file that lives **inside** an intact Sentinel clone. Its identity is
therefore **resolved**, not unresolved. What the `PLAIN` fixture makes unresolvable is the
*caller's* repository, which was the identity only under the caller-current-directory semantics
D-060(2) abolished. Rows 2 and 4 of the card's matrix describe **the same fixture read under two
different semantics**, and only row 2 survives D-060(2).

A valid case 4 must attack the **script's own** location. A proposed `4'` was measured:

```
copy scripts/*.sh into a directory that is outside every git repository, then run the copies
```

| | REQUIRED 4' (`0 of 12 may exit 0`) | CONTROL 4' (`>0 must refuse`) | coexists with case 2? |
|---|---|---|---|
| at worktree `HEAD` | **0 of 12 exit 0** — holds | **12 of 12 refuse** — holds | yes: the in-place scripts called from the *same* directory still give 12 of 12 exit 0 |
| at base SHA `f68d4d804de4d3b631e25fd539deecda5409f0d7` | **2 of 12 exit 0** — fails, as a pre-repair line must | **10 of 12 refuse** — holds | — |

The two that fail open at the base SHA are `check-rename-gate.sh` and `check-secrets.sh` — the same
pair the current case 4 names at the base SHA, so the corrected case loses none of the original's
discriminating power. It simply survives the repair instead of contradicting it.

**Two cautions for whoever writes the replacement:**

1. At the base SHA the 10 "refusals" above are **accidental** — missing-file errors from a script
   that stayed in the caller's directory — not identity refusals. A corrected case 4 that scores a
   non-zero exit as a pass repeats the mislabelling `RESULTS.md` already records twice under "two
   labelling corrections". It should assert the *refusal message or a distinct exit status*, the
   way case 12b already asserts that a non-zero exit was a refusal and not a downstream failure.
2. Other instantiations of the same premise are available and would broaden the case rather than
   replace it: a copy placed inside the **foreign** repository (identity resolves, but to the wrong
   repository), and invocation through a symlink whose real directory is outside every repository.
   Whether to include them is a scope call, not an adjudication call.

Case 4's header and description strings (lines 286, 291, 294, 296) would need rewording as well:
"repository identity unresolved" currently describes the caller's state.

---

## 2. CLAIM 2 — case 5c versus case 5b: **REFUTED**

### 2.1 The two lines, exactly

```
308| out="$( cd "$SUT" && PATH="$WORK/shim:$PATH" A1_SHIM_MODE=errorunmatch-fail ./scripts/check-review-scope.sh 2>&1 )"; rc=$?
310| check REQUIRED 5b ... "check-review-scope.sh refuses when 'git ls-files --error-unmatch' fails (exit $rc)"
311| true_n="$(... 'remediation surface: [0-9]+' "$WORK/base/check-review-scope.out" ...)"
312| shim_n="$(printf '%s' "$out" | ... 'remediation surface: [0-9]+' ...)"
314| check REQUIRED 5c ... "the remediation count survives that failure (true=${true_n:-none}, observed=${shim_n:-none})"
```

Both read the **same single run** captured at line 308. There is no second invocation, so the
count must be present in the output of the run that also exits non-zero.

### 2.2 What the shim actually breaks — and what it does not

Harness lines 152–155 fail a `git ls-files` invocation **only when `--error-unmatch` appears among
its arguments**; line 159 `exec`s the real git for everything else. So under this shim
`git ls-files -z` still works, and `git diff -z --name-only` still works. Both of those are what
`scripts/check-review-scope.sh` already uses to enumerate the tracked set and the scope diff, and
both succeed.

**That is the whole refutation: the count is establishable under this shim.** It is only the
per-file index probe that fails.

### 2.3 The implementer's observation is correct about the current code

At worktree `HEAD`, under the shim:

```
review scope: R1=286  R2=46  R3=151  (assigned 483 of 483 tracked files)
  FAIL  git ls-files --error-unmatch failed on: .githooks/pre-commit
    Refusing to treat an instrument failure as a deletion.
exit=1
```

The refusal fires on the first file of the walk, so the `remediation surface:` line is never
reached: `5b PASS`, `5c FAIL (true=101, observed=none)`. That is a fact about **this**
implementation, not about the test.

### 2.4 The implementation that satisfies both — Variant C

About twenty lines in `scripts/check-review-scope.sh`, all inside the scope walk:

1. The tracked enumeration at the top of the script (`git ls-files -z`) has already run, and the
   script already **refuses outright** when it fails or returns empty — that is what controls 5d
   and 6 measure. So when the walk begins, index membership is an **established** fact that does
   not depend on `--error-unmatch` at all. Materialise it once into a temporary list.
2. `--error-unmatch` exit `1` keeps its present meaning: the path is genuinely absent from the
   index, so it was deleted since the base and is skipped. Unchanged.
3. Any other non-zero exit is an **instrument failure**. Record it (first occurrence, with git's
   own stderr), then fall back to membership in the enumeration that *did* succeed and carry on
   counting. Nothing is guessed and nothing is skipped silently.
4. Print the `remediation surface:` line as usual — it is now backed by two commands that both
   succeeded.
5. **Then refuse:** emit a `FAIL` naming the failed instrument and exit non-zero.

Observed output under the shim:

```
review scope: R1=286  R2=46  R3=151  (assigned 483 of 483 tracked files)
  remediation surface: 101 file(s) changed since A-070's parent, all assigned
  preservation-only:   79 file(s) (round-six record; ...)
  FAIL  a git command failed during the scope walk: git ls-files --error-unmatch failed on
        '.githooks/pre-commit' (exit 3)
    The count printed above is established -- it comes from the tracked enumeration, which
    succeeded -- but an instrument failed, so this run is NOT a clean scope check and is refused.
exit=1
```

The unmodified harness's verdict on Variant C:

```
case 1b  CONTROL  PASS   12 executable entry points exit 0 from the repository root
case 2   REQUIRED PASS   0 differ
case 3   REQUIRED PASS   0 differ
case 5a  REQUIRED PASS
case 5b  REQUIRED PASS   check-review-scope.sh refuses when 'git ls-files --error-unmatch' fails (exit 1)
case 5c  REQUIRED PASS   the remediation count survives that failure (true=101, observed=101)
case 5d  CONTROL  PASS   the GUARDED ls-files branch does refuse on the same shim (exit 1)
case 5e  CONTROL  PASS   an unmutated run ... measures a non-empty remediation surface (101)
case 6   REQUIRED PASS   /  case 6 CONTROL PASS
REQUIRED failed : 1      <- case 4 only, i.e. Claim 1
```

Cases 7, 8, 9, 10, 11, 12, 12b, 13, 13a-r, 13b and every remaining control were unaffected. **5b
and 5c hold simultaneously with all controls intact.**

### 2.5 Does printing the count violate the invariant?

No. The invariant forbids *"reporting a result it did not establish"*. Under this shim the count is
established — the scope diff and the tracked enumeration both succeeded — so printing it reports a
fact, and the run still refuses: non-zero exit, with the FAIL immediately under the number. The
prohibited shape is the opposite one, and it is the one the base SHA exhibits: a **zero** printed
as though it were a measurement, with exit 0.

One honest wrinkle, offered as a note and not as a blocker: the printed line still ends
"all assigned", which is true of the set that was counted but reads as a clean verdict. A repairer
may prefer to reword it under an instrument failure. That is cosmetic — `5c`'s extraction at line
312 keys only on `remediation surface: [0-9]+`.

### 2.6 The residual, recorded rather than absorbed

`5b` can only be satisfied by an implementation that **actually issues**
`git ls-files --error-unmatch`; the shim has nothing to break otherwise. A repairer who removed
that call entirely and derived membership from the tracked enumeration alone — a defensible
simplification — would make the shim inert, exit 0, and fail `5b`. So `5b` pins a mechanism as well
as a behaviour.

That is a constraint on the repair, not an invalidity: a correct implementation satisfying both
lines exists and is demonstrated above, and it keeps `--error-unmatch` for exactly the reason
D-060 cares about — it is the per-file index probe whose `|| continue` was `V3-N1`. Flagged for
John as a note on the test's shape, not as a claim against it.

---

## 3. WHAT THIS EVIDENCE DOES AND DOES NOT ESTABLISH

**Establishes.**

- Case 2 and case 4 measure one deterministic quantity in one state, verified by fingerprint, and
  demand opposite values of it. Both directions were realised against the real harness (Variants A
  and B).
- The single observable that distinguishes the two invocations is the stdout target; keying on it
  satisfies both REQUIRED lines and is rejected by protected control 7 and by control 13c
  (Variant D, harness exit 2).
- Case 5b and case 5c are jointly satisfiable by an implementation that establishes the count from
  the commands that succeeded, prints it, and then refuses (Variant C, harness exit 2 with case 4
  as the only remaining REQUIRED failure).
- A corrected case 4 built on the script's own location is satisfiable at `HEAD`, discriminating at
  the base SHA, and compatible with case 2.

**Does not establish.**

- Claim 1 is not a formal proof over all possible programs. It is an exhaustive argument over the
  **observable** difference between the two invocations — there is exactly one, and it is
  foreclosed — plus two realised counterexamples. A program that is deliberately non-deterministic,
  or that writes hidden state into the caller's directory on one run to change the next, is not
  covered and is not a correct implementation of anything.
- Variant C is a **demonstration of satisfiability**, not a recommended final wording, and it was
  never applied to the repository or the worktree. Its wording, and the §2.5 note, are the
  implementer's and John's to settle.
- All four harness runs are against worktree `HEAD` `70bf654`, **not** the card's base SHA; the
  harness prints that warning itself. The base-SHA figures quoted in §1.6 come from a separate
  detached checkout of `f68d4d804de4d3b631e25fd539deecda5409f0d7`.
- `scripts/test.sh` and `scripts/mutate.sh` were not run here either, for the reason `COVERAGE.md`
  §1 gives. Nothing above is evidence about them.
- Nothing here adjudicates any other REQUIRED line. Cases 1, 3, 5a, 6, 7–13 were observed only as
  they fell out of these runs.

---

## 4. REPRODUCTION

From the implementation worktree, with repository-relative paths:

```
bash docs/review-2026-08-19-d057-targeted/batch-cards/A1-tests/a1-repo-identity.sh
```

For the variants, the harness takes the repository under test as `$1`, so each variant is a
throwaway clone with the change committed in it:

```
git clone -q --no-hardlinks <worktree> <scratch>/vX
git -C <scratch>/vX fetch -q <worktree> HEAD && git -C <scratch>/vX checkout -q --detach FETCH_HEAD
#   ... apply the variant, git commit ...
bash docs/review-2026-08-19-d057-targeted/batch-cards/A1-tests/a1-repo-identity.sh <scratch>/vX
```

Variant SHAs, for the record: **B** `7e62ca4`, **C** `f36f0ec`, **D** `0e6667a`, all children of
`70bf654` and all in scratch clones only. Every search in the probes used `/usr/bin/grep`.

## 5. RESTORATION

The implementation worktree is as it was found: `HEAD` `70bf654`, `git status --short` reporting
only the pre-existing untracked `ts/node_modules`, and `git diff` empty. The harness file is
unchanged in both trees, verified by hash. No production file was edited anywhere.
