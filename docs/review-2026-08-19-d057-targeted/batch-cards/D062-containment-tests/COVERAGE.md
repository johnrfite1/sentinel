# D-062 CONTAINMENT — COVERAGE STATEMENT

What `d062-containment.sh` exercises, and — the half that matters more — what it does not.
Written before any repair exists, so that a repair cannot be graded against a moving target.

**Harness sha256:** `c830d195281c0a2bae2fd62e79ce1d1402f03182bb2fbc446361c91fd89a1756`

---

## 1. WHAT IT EXERCISES

**Three invocation shapes, deliberately different instruments:**

| shape | used by | why |
|---|---|---|
| a real `git commit`, hooks live | cases 1-6 | git chooses `GIT_INDEX_FILE`; only a real commit produces the genuine hand-off, and only a real commit can land a credential in HEAD |
| `check-secrets.sh` invoked directly | case 7 and its controls | the manual path, where a caller-supplied variable must be ignored |
| the hook invoked directly with an emulated hook environment | cases 8-11 | the value of `GIT_INDEX_FILE` is the thing under test, so it has to be chosen rather than observed |

The emulation used by cases 8-11 is **built from measurement, not assumption.** Preflight `P6`
runs a probe hook through three real commit forms and records what git hands it; the emulation
then reproduces exactly that. If a future git sets `GIT_DIR`, `GIT_WORK_TREE` or
`GIT_COMMON_DIR` for hooks — this git sets none of them — `P6` fails the whole run rather than
emulating a fiction.

**Assertions are never on exit status alone.** Every BLOCK assertion additionally requires the
guard's own output to name the fixture path and requires the credential to be absent from HEAD.
Every REFUSE assertion additionally requires the absence of the `secret guard: clean` line. This
is the direct consequence of §0's *"a generic failed commit, missing file, or broken fixture is
not a caught credential"* and *"exit status 0 is not success"*.

**Control failure is a separate exit path.** Exit 1 means required cases failed with every
control holding, so each failure is attributable. Exit 2 means a control or a preflight failed
and **nothing** printed above it may be relied on.

**The credential fixture** is a single hex character repeated 64 times bound to a key-shaped
identifier, assembled at run time. Preflight `P5` proves it trips `check-secrets.sh` in **both**
modes before any case runs.

**Isolation.** Every case runs against a private clone under `TMPDIR`, or against repositories
the harness created. `HOME` and the global, system and XDG git configuration are redirected into
scratch for the whole run and asserted unchanged at the end (`Z-cfg`). Git configuration is
never written into a repository the harness did not create. The repository under test is read
only: cloned from, `rev-parse`d, and `shasum`ed.

---

## 2. PLATFORM AND VERSION BOUNDS

Measured on **git 2.50.1 (Apple Git-155)** and **bash 3.2.57(1)-release**, on `darwin`, with
`core.quotePath` and `diff.renames` at their defaults.

- **The temporary-index hand-off is git's documented hook contract, but it was measured on one
  version.** The exact spellings — `.git/index.lock` for `git commit -a`, and
  `.git/next-index-<pid>.lock` for `git commit -- <path>` — are what this git produces. A
  different git could plausibly choose a different temporary name. Cases 10 and 11 name those
  two spellings explicitly and would need extending, not rewriting, if a supported git produced
  a third.
- **`P6` is the guard against that going unnoticed**: it records the live spellings on every
  run, so a divergence appears in the evidence rather than as a silent pass.
- **One repository layout.** The subject is an ordinary clone. A **linked worktree** — where the
  index lives under `.git/worktrees/<name>/` rather than under `.git/` — is **not exercised**,
  and it is the layout most likely to break a naive location check. This is named as an
  uncovered case rather than left for a verifier to find.
- **A separate-`gitdir` checkout** (`.git` as a file) is not exercised either.
- **Concurrency is not probed.** Nothing here runs two commits at once.
- **bash 3.2 only.** The harness itself avoids `mapfile` and associative arrays, but it has not
  been run under bash 4 or 5.

---

## 3. WHERE A CASE PASSES WITHOUT DISCRIMINATING — STATED PLAINLY

This is the section a reviewer should read first.

**Cases 4, 5 and 6b pass at the pre-repair baseline for the WRONG reason.** At the baseline the
guard reads the canonical index, which for those three commit forms is empty, and prints
`secret guard: clean`. The commit is allowed because nothing was examined — not because the
temporary index was examined and found clean. Their controls (`1-tmp`, `2-tmp`) prove the
temporary index existed and differed, but nothing observable from outside distinguishes *"read
the right index and found nothing"* from *"read the wrong index and found nothing"* when the
right answer is also nothing.

**Their discriminating value is therefore conditional and arrives only after a repair.** Once
cases 1 and 2 pass, cases 4 and 5 become the opposite control that stops a repair from refusing
every `-a` commit. Until then they are anti-regression only. **A harness cannot be satisfied by
something that refuses unconditionally** — that is what 4, 5, 6a and 6b buy — **and it cannot be
satisfied by something that accepts unconditionally** — that is what 1, 2, 3 and 6c buy. Neither
half is sufficient alone, and this is the pairing, not two independent facts.

**Case 6a is the one "allowed" case that discriminates at the baseline**, because a genuine
pre-staged deletion is enumerated through the canonical index the baseline actually reads.

**Case 12 passes at the baseline trivially**, because the baseline never touches the victim: it
clears the variable before anything runs. Its value is entirely post-repair, and `12-live`
exists so that "unchanged" is known to be a measurement rather than an inert comparison.

**Case 7 passes at the baseline for the RIGHT reason** — the `12-F2` scrub is doing exactly what
it was built to do — and it is included precisely so a repair cannot buy cases 1 and 2 by
re-honouring whatever `GIT_INDEX_FILE` it inherits.

---

## 4. INTERPRETATIONS THIS HARNESS COMMITS TO, THAT A REPAIR MIGHT READ DIFFERENTLY

Named here rather than buried, because the implementer may not change these tests and an
unstated reading would be an ambush.

1. **"REFUSE" in cases 8 and 9 is read as fail-closed refusal of the commit** — a non-zero exit
   with no `secret guard: clean` line — and **not** as "ignore the bad path and scan the
   canonical index anyway". The distinction is deliberate in the specification this harness was
   written against: manual invocation *ignores* a caller-supplied value, the hook *rejects* an
   unacceptable one. The hook is the component that knows it was invoked by git, so a
   `GIT_INDEX_FILE` it cannot validate means something is wrong with the invocation, and the
   fail-closed direction is the one the invariant demands. **If a repair believes this reading
   is wrong, it stops and has the invalidity independently confirmed — it does not edit these
   cases.**
2. **Case 8 does not assert any particular refusal wording**, only that the guard did not report
   clean and did not exit 0. Cases 1, 2, 3, 10 and 11 assert that the output **names the fixture
   path**, which is the finding, not a fixed message format.
3. **Case 11 uses a fixed digit string in the temporary index name**
   (`next-index-24680.lock`). Any acceptance rule matching git's next-index form will accept it.
   A rule that accepts only the *live* process's own pid would fail case 11 — that is intended:
   the hook is not the process that created the file and cannot know that pid.
4. **The internal channel between the hook and the guard is not asserted anywhere.** Cases 8-11
   invoke the hook, never the guard directly, precisely so that no implementation shape is
   baked in.

---

## 5. WHAT THIS HARNESS DOES NOT PROBE AT ALL

- **Every residual recorded in `A2-tests/VERIFICATION-2.md`** — `R-A` (`SENTINEL_GATE_REPO_ROOT`
  accepted when the gate body is entered directly), `R-B` (a symlinked or copied
  `scripts/test.sh` inside a foreign repository), `R-C` (git configuration-injection variables
  outside the cleared set, which can hide untracked content from default mode), `R-D`
  (`GIT_OBJECT_DIRECTORY` failing closed loudly), `R-E` (`GIT_PREFIX` inert and scrubbed
  inconsistently), and `R-F` (attempt one's `R2`, `R3`, `R5`, deferred by D-061(2)). **None is
  reopened by D-062 and none is measured here. Read no coverage into the silence.**
- **The other five caller git variables in combination.** `A2-tests/a2-env-and-supervisor.sh`
  owns those six configurations and is frozen; this harness asserts only that it is byte-
  identical, and adds `GIT_INDEX_FILE` coverage that harness does not have. The two are
  complementary and **both** must be run to cover the environment.
- **The other fourteen entry points.** Only `.githooks/pre-commit` and `scripts/check-secrets.sh`
  are in the D-062 boundary.
- **`check-secrets.sh`'s pattern rules.** The fixture exercises rule 3b and nothing else. No
  claim is made about the credential patterns, the placeholder suppressors, the Anvil allowlist
  or the machine-path rule.
- **Rename, copy, typechange and gitlink enumeration.** `R1`'s repair is assumed unchanged and
  is not re-verified here; the D-062 boundary forbids touching it.
- **Non-ASCII filenames**, covered by the frozen A1 harness.
- **The gate, the suite, Solidity and the corpus.** Nothing here builds or runs the product.
- **Whether the repair is minimal.** That is a verifier's judgement, not a test's.

---

## 6. HOW TO RUN IT

```
docs/review-2026-08-19-d057-targeted/batch-cards/D062-containment-tests/d062-containment.sh [ROOT]
```

`ROOT` defaults to the repository containing the harness. Set `D062_MATRIX_OUT=<path>` to write
the scored matrix as TSV. Exit 0 = everything held; 1 = required failures with all controls
holding; 2 = a control or preflight failed and the harness is untrustworthy.

**Run it against the pre-repair commit as well as the repaired one.** A required case that
passes at both is not evidence of a repair.
