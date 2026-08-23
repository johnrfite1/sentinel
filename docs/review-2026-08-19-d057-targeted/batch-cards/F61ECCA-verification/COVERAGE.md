# F61ECCA coverage

| Item | Hole claimed at f61ecca | Exploit control | Observing test | Blind spot |
|---|---|---|---|---|
| C4 | Non-ASCII path quoted under `core.quotePath`; `[ -f ]` / `|| continue` skipped it | Café-only mutant prints clean; ASCII-only mutant is BLOCKED | Freeze BLOCKED on both | Default mode untracked. Tracked non-ASCII with absent working-tree copy is a sibling, not this case. |
| R1 | `--name-only --diff-filter=ACM` dropped staged rename and typechange | Mutant clean on staged R and staged T carrying a synthesised assignment | Freeze BLOCKED, destination named | Copy (`C`) was already inside ACM; not re-probed. |
| C6a | `check-findings-ledger.sh` took the caller's git top-level | Mutant reads a decoy ledger and MISMATCHes | Freeze from the same cwd still matches Sentinel | Does not claim every git override is scrubbed (that is V-6). |
| C6b | `check-suite-floors.sh` same identity hole | Mutant prints a distinctive decoy floor | Freeze prints Sentinel's floors | Same limit as C6a. |
| C6c | `install-hooks.sh` wrote `core.hooksPath` into a foreign repository | Mutant sets `core.hooksPath` on a foreign scratch repo | Freeze refuses; foreign repo unchanged | Sentinel's own hooksPath is not the measurement. |
| C6d | `test.sh` established root from cwd; decoy lookalikes ran | Mutant from decoy cwd fires decoy shims | Freeze from decoy cwd does not fire decoy shims; Sentinel stages start | Full `GATE PASSED` from decoy cwd is attempted; if not waited out, `C6d-PROBE.md` says so. |

Severity is the independent reviewer's, not the implementer's.
