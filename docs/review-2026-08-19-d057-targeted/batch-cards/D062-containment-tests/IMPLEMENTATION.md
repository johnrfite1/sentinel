# D-062 CONTAINMENT — THE IMPLEMENTATION, AND WHAT IT IS AND IS NOT

**Author:** the implementing agent. **NOT independent evidence.** The independent test contract
is `d062-containment.sh` / `CARD.md` / `COVERAGE.md` / `RESULTS.md`, written by a different
agent before any production change; the independent verification is dispatched separately under
D-062(4). This file records what was changed and what was measured, so a verifier has a stated
claim to attack rather than a diff to reverse-engineer.

**Authority:** D-062 — one surgical containment exception, for the `GIT_INDEX_FILE` regression
only. **Batch A1 remains recorded as FAILED under D-061(4). Neither attempt is relabelled
successful, and no other A1 finding or residual is reopened.**

## FILES CHANGED — two, and the card permits no others

| file | change |
|---|---|
| `.githooks/pre-commit` | capture the hook-provided `GIT_INDEX_FILE` before the scrub; validate it; pass the validated path explicitly |
| `scripts/check-secrets.sh` | a narrow internal `--index-file` input, re-validated, applied per-command to the three index reads |

Nothing else. `git diff --numstat` over the production change is 83/0 and 84/4.

## WHAT THE REPAIR DOES

**The hook.** `GIT_INDEX_FILE` is captured alongside `INVOKING_ROOT`, before the existing scrub —
both are git's own hand-off and both are read before anything can be redirected. The capture is
then validated, and **only after invoking-root equality already holds**, so "this worktree" below
means a repository whose identity is established rather than asserted:

- the canonical index is asked of git as `git rev-parse --git-path index`, **not** assumed to be
  `$root/.git/index` — correct for a linked worktree and a separate-`gitdir` checkout, neither of
  which the harness exercises;
- the candidate's **directory** is resolved physically, which collapses `..` and symlinked
  components before comparison, so traversal and directory symlinks are closed in one step;
- the basename must be the canonical index, `index.lock`, or `next-index-<digits>.lock`;
- `-L` is tested **before** `-f`, because `-f` follows a symlink and a link into the canonical
  directory would otherwise pass both tests while the scanned bytes lived elsewhere;
- anything else refuses, exit 2, with a dedicated diagnostic and no clean line.

The validated path is passed as an **argument**. It is never re-exported.

**The guard.** `--index-file` is re-validated with the same rule rather than trusted from the
hook, because this script is reachable directly and a check that exists only in the caller is a
check this script cannot claim. The value reaches git through `_cs_git`, which sets
`GIT_INDEX_FILE` as a **per-command prefix** on exactly **three call sites — the index census, the
staged raw enumeration, and the staged blob read — which execute as FOUR invocations**, because
`_sec_content` is called once by the credential scan and once by the machine-path scan, so the
staged blob read runs twice per scanned path. Every other git call in both modes still runs
against the canonical index.
*(Corrected in place, closure maintenance. This passage read "exactly three calls", which counted
call SITES and stated them as invocations — `V-9` in `VERIFICATION.md`, raised by the independent
verifier. The scoping claim it supports is unchanged and was independently confirmed; the count
was imprecise, and in this project an imprecise count in an evidence file is the defect class, not
a rounding error.)*

## WHAT IT DELIBERATELY DOES NOT DO

- **The scrub is unchanged.** A caller-supplied `GIT_INDEX_FILE` still redirects nothing. Manual
  `--staged` and manual default mode both ignore it and scan Sentinel's canonical index — the
  harness asserts this at case 7 and controls `7-nov` / `7-def`, and it is the `12-F2`
  anti-regression that attempt one failed.
- **The pid is not checked.** Git's next-index form carries the *committing* git's pid, not the
  hook's, so the **form** is accepted and the containing-directory test is what makes that safe.
- **Default-mode index-blob behaviour (D-061), raw NUL parsing, rename/copy destination handling,
  mode and gitlink handling, and the staged-deletion control are untouched.**

## THE PROTECTION BOUNDARY, STATED RATHER THAN IMPLIED

This defends against **accidental and environmental** redirection — an inherited or mistaken
`GIT_INDEX_FILE`, a stale value, a path pointing at another repository. **It is NOT a defence
against a hostile process running as the same user**, which can replace git's temporary index
between validation and scan, and which can equally well edit the hook. Stated in both files' own
comments as well as here.

## MEASURED

All numbers below were read from the tools' **output**, never from an exit status.

| check | result |
|---|---|
| `bash -n`, both changed files and all 16 entry points | 0 syntax failures |
| **containment harness ×2**, repair | **12/12 REQUIRED pass · 0 CONTROL failures** (baseline: 7 REQUIRED failures) |
| **A1 frozen harness ×2**, repair | 0 REQUIRED · 0 CONTROL failures — identical to its pre-repair control |
| **A2 frozen harness ×2**, repair | **2 REQUIRED failures · 0 CONTROL failures** — see below |
| gate immutability | 10/10, unprotected control corrupted |
| secrets · review-scope · vendor-honesty · findings-ledger · rename-gate · suite-floors | all pass |
| frozen harness hashes after every run | A1 `54535b3b…122d`, A2 `dd67d69a…84a7`, D062 `c830d195…1756` — all unchanged |

**The pre-repair baseline was measured in the primary tree and the repair in an isolated clone,
because the harness clones `ROOT` at HEAD and never reads the working tree.** An uncommitted
repair is therefore invisible to it — the first run against the working tree reproduced the
baseline exactly, and that is the trap this note exists to record.

## THE TWO A2 FAILURES — RULED, NOT WAVED AWAY

**D-064 rules `B3-index` and `B4` SUPERSEDED by D-062, for the hook path only. A2 is not
modified, not re-scoped and not relabelled; it fails these two assertions on this branch, and
every citation of it must say so.**

- **`B4`** counts any git call with a variable **present** and cannot distinguish an inherited
  caller value from a validated one the hook re-supplied. Reading a specific index *requires*
  `GIT_INDEX_FILE`; there is no index flag on `git ls-files`, `git diff --cached` or `git show`.
  **Standalone `check-secrets.sh` still scores 0 carriers**, which is the manual-invocation half
  of D-062 holding.
- **`B3-index`** is a vocabulary gap, not a behaviour gap: exit 2, no clean line, no credential
  admitted — what D-062(7) requires and what case 8 of this card REQUIRES — but A2's
  `is_ident_refusal` matches identity wording and this refusal is about the **index**.
  **Rewording the refusal to satisfy that matcher was rejected**: it would relabel an index
  refusal as an identity refusal to pass a test, which is this project's own recorded defect
  class.

**D-064 carries the reversal condition: if any THIRD A2 assertion is found to have moved, the
supersession does not cover it and the repair returns to John.**

## WHAT THIS IMPLEMENTATION DOES NOT ESTABLISH

- **One platform, one git** — git 2.50.1, bash 3.2, defaults. The temporary-index hand-off is
  git's documented hook contract but was measured on one version.
- **No linked worktree, no separate-`gitdir` checkout, no concurrency, no interactive commit
  forms** were exercised. `--git-path` is *believed* correct for the first two and is *not
  measured*; that is a claim a verifier should attack rather than accept.
- **Every `A2-tests/VERIFICATION-2.md` residual (`R-A`…`R-F`) is untouched and unprobed.** None
  is reopened by D-062. Read no coverage into the silence.
- **Whether the repair is minimal** is a verifier's judgement, not the implementer's.
