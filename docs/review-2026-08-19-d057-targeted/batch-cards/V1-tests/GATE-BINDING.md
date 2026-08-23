# V-1 — D-059(7) gate binding, measured

> *"A standalone script that nothing invokes repeats the defect this work is trying to close.
> Required: invocation by the applicable fast and deep gate paths; a TOP-LEVEL falsification
> showing THE GATE fails when the targeted fact is wrong; an unchanged control showing the real
> gate passes; and an explicit statement that the guard covers only its enumerated canonical facts
> and is NOT general prose-consistency evidence."* — D-059(7)

**Harness:** `v1-gate-binding.sh`
**Subject:** isolated clones of this repository with the candidate `scripts/test.sh` and
`scripts/check-v1-index-ordering.sh` overlaid from the working tree. The live tree is not
edited. Raw logs are in `logs/`; one disclosed substitution replaces the operator's
absolute repository path with `<sentinel-root>` (the rename gate prints it when UNVERIFIED).
No credential-shaped literal is in any log.

## Fast profile — MEASURED

Three serial `./scripts/test.sh` runs (not `--gate`). Supervisor outcomes read from output,
not from a remembered number:

| Case | What was done | V-1 stage | Top-level | Supervisor rc |
|---|---|---|---|---|
| **G1** REQUIRED | unchanged candidate | `V-1 index-path ordering: ok` | `GATE PASSED` | 0 |
| **G2** REQUIRED | reverse-ordering mutant of `check-secrets.sh` only | `V-1 index-path ordering: FAIL`; CS-live FAIL; secret guard still `clean` | `GATE FAILED` then `GATE DID NOT REACH COMPLETION` | 5 |
| **G2c** CONTROL | same mutant, V-1 step changed to `\|\| true` | FAIL line still prints | `GATE PASSED` | 0 |

G2c is the causal twin: the mutant remains, the named stage still prints FAIL, and ignoring
only that stage's status lets the gate pass. So G2's red is the V-1 step, not a side effect
of mutating `check-secrets.sh` (default-mode secret guard stayed clean on G2).

Log sha256 values of the committed, redacted files are in `logs/SHA256SUMS`. The one
disclosed substitution is the operator repository absolute path → `<sentinel-root>`
in the rename-gate UNVERIFIED line; it does not appear in the V-1 stage output.

## Deep profile — invocation, not a third mutation trio

The V-1 step sits in `scripts/test.sh` in the shared prefix: after `PROFILE` is assigned and
before the Foundry step, with no `if`/`case`/`while` wrapping it. The first profile-dependent
*branch* is the later corpus/deep block. A-EXTRACT's GATE-BINDING.md recorded the same split:
fast mutations measured; deep invocation is the same shared-prefix step, and three deep
mutation runs are not required unless that control flow moves.

This document does not claim the deep profile was executed here. Independent verification
of a later candidate may run `./scripts/test.sh --gate` and capture the V-1 stage banner.

## Coverage statement (repeated because D-059(7) requires it in the binding record)

The V-1 guard covers only CS validation-refusal and HOOK commit-block under a hostile
`GIT_INDEX_FILE`, as enumerated in the guard header and in `COVERAGE.md`. It is not general
index-handling evidence, not evidence about any other script, and not a claim that a
hook-path commit is accepted after the hook's own directory check is reversed.
