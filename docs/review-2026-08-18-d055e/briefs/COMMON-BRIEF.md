# D-055(e) — the bounded post-repair review. COMMON BRIEF.

**This is ONE bounded review with a defined exit, not round seven of an open-ended loop.**
Four reviewers. Its scope was fixed by John BEFORE it ran (D-056(d), satisfying D-055's T3).

**Frozen commit: `7e0ab7f1057de278c09cc803ab4ca266f53399e1`.** Your worktree is detached at it.

## Your job

**Prove the work fails.** Not "confirm a check fires on the input it was designed for" — that
measures the designer's imagination. A previous round reported "8/8 guards caught, 0 defeated";
an independent reviewer told to DEFEAT a guard produced seven confirmed defeats within hours.

**You are invited to report that your own brief is wrong.** If your assigned surface is the
wrong place to look, or this brief mis-states what is there, that is a finding.

## THE DELIVERABLES CONTRACT — read this before you start work, not after

**EVERY ONE OF THESE MUST BE A FILE ON DISK IN YOUR EVIDENCE DIRECTORY BEFORE YOU ARE
COMPLETE.** This is not paperwork. **In round six, seven of nine reviewers left no report,
coverage statement or attestation on disk. Their findings survive only as one adjudicator's
second-hand summary, and that is now a permanent, unrecoverable provenance gap in the record
this project rests on.** You are the fix for that.

Write these, with these exact filenames, in your evidence directory:

| File | Contents |
|---|---|
| `REPORT.md` | Every finding: id, severity, the claim, the reproduction (exact commands), what you observed, and your confidence. One section per finding. |
| `NULL-RESULTS.md` | What you probed and found SOUND. A null result is evidence and it is how the next round knows where not to look again. |
| `DEAD-PROBES.md` | **Every probe that measured nothing** — did not compile, matched no lines, errored before reaching the code, or mutated a value that was already at its limit. **Five such probes in one 48-hour window looked exactly like passes.** If you had none, say so explicitly. |
| `COVERAGE.md` | What you actually ran, what you did NOT reach, and why. A surface you were assigned and did not exercise must be named here. |
| `CRITIQUE.md` | What is wrong with this brief, this scope, or this apparatus. |
| `ATTESTATION.md` | Commit you reviewed, tools and versions, every command that mutated anything, and confirmation your worktree is reverted. |

**A finding with no reproduction is a lead, not a finding — label it so.**

## Rules

1. **Work ONLY inside your own worktree.** Never touch the live repository.
2. **Revert every mutation.** Keep a pristine copy and `cmp` against it. **Do NOT revert with
   `git checkout -- .`: it DESTROYS the symlinked toolchain and then reports a clean tree,
   and a cached `forge build` still exits 0 — a revert that verifies clean while the toolchain
   is gone.** `git status` with no pathspec EXITS 128 in these worktrees (submodules are
   symlinks), which silently truncates `&&` chains; use `git diff HEAD --stat -- .`.
3. **Run your own baseline FIRST**, before mutating anything, and record it. A finding measured
   against an unknown starting state is not a finding.
4. **Check that your probe MOVED something** before believing what its silence implies.
5. **Re-reporting a recorded item is not a finding — but showing a recorded item is WORSE than
   recorded IS one.** The register `docs/v1-1-register.md` §13.4 is the list of what is already
   known; `docs/gate-s2-evidence.md` §11.0 is the five findings John ACCEPTED as limits.
6. To check whether another gate run is in flight use `pgrep -f sentinel-gate` — **not**
   `pgrep -f scripts/test.sh`, which no longer matches since the gate execs a snapshot.

## What this project's defects actually look like

They are **honesty** defects — a claim stronger than its evidence — and the build loop does not
find them. Specifically and repeatedly:

- **An instrument can exist and point at the wrong thing.** Guards, tests and mutations have
  shipped aimed at something other than what they name, five or more times.
- **A repair can generalise the DEMONSTRATION rather than the ARGUMENT** — fixing the branch a
  reviewer exploited and leaving the identical hole two lines down.
- **A regression test can pass against the defect it names.**
- **A published number can be true once.**
- **A test can pass against no protection at all.** A harness written *this week* to prove the
  gate cannot be corrupted mid-run used an edit shape that is harmless, and reported 4/4 against
  a completely unprotected script.
- **Absence can read as agreement.** A check that emits nothing when a field is missing is worse
  than no check, because the run still prints clean.

## Severity

Assign it yourself; you are the independent party. Critical / High / Medium / Low / Info.
**Do not soften.** Every finding is independently adjudicated afterwards by a reviewer who is
not you, and an unadjudicated Critical or High blocks exit — it is PENDING, never "unconfirmed".
