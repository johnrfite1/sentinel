# Independent review brief — V-1 instrument readiness

You authored none of this work. Return **HOLD** or **FAIL** for instrument readiness.
Do not repair. Do not grade generously. Prove the instrument fails its own bar if you can.

## Subject

Working tree of this repository, specifically:

- `scripts/check-v1-index-ordering.sh`
- the V-1 step in `scripts/test.sh`
- `docs/review-2026-08-19-d057-targeted/batch-cards/V1-tests/`

## What the instrument claims to observe

Behaviour under a hostile exported `GIT_INDEX_FILE`, not source-text order. See
`EXPLOIT-CONTROL.md` and the guard header. A grep of line order is a FAIL.

## What you must attack

1. Does every REQUIRED case fail for the reason it names when the hole is open, and pass
   when it is not? Run the guard. Apply the reverse-ordering mutant yourself in a
   disposable copy and watch the guard's own behaviour.
2. Is the CS mutant control live? If the mutant still refuses, the instrument is measuring
   nothing.
3. Credential-shaped content: is any 64-hex assignment literal present in a tracked file
   this work adds? It must not be.
4. D-059(7): is the guard invoked by `scripts/test.sh` in the shared prefix? Is there a
   top-level falsification showing the *gate* fails when ordering is reversed, and an
   unchanged control showing the real gate passes? Read `v1-gate-binding.sh` and its logs
   if present; if the logs are absent, say so rather than inferring a pass.
5. The coverage statement: does it honestly exclude the hook commit-accepted outcome that
   could not be constructed?
6. Would a refactor that keeps scrub-before-resolve by a different mechanism (local copy
   of the environment, subshell re-export) still be observed as a hole if it reopened one?
   If the failure signal is line order, FAIL.

## Verdict

One word first: **HOLD** or **FAIL**. Then evidence. Do not recommend a product repair.
This is instrument readiness only.
