# F61ECCA verification — RESULTS

Run against disposable clones of HEAD. Live tree not mutated.
Credential-shaped values synthesised at run time (`API_KEY=` + 32 random bytes);
logs redacted. Exploit control before observing test.

Harness: `f61ecca-verify.sh`. Logs: `logs/`.

## Matrix

| id | kind | status | what was observed |
|---|---|---|---|
| C4-x | CONTROL | PASS | mutant café-only: `secret guard: clean` |
| C4-a | CONTROL | PASS | mutant ASCII-only: `BLOCKED`, `ascii-only.md` named |
| C4 | REQUIRED | PASS | freeze café-only: `BLOCKED` |
| C4b | REQUIRED | PASS | freeze ASCII-only: `BLOCKED` |
| R1-xR | CONTROL | PASS | mutant staged rename: `secret guard: clean` |
| R1-xT | CONTROL | PASS | mutant staged typechange: `secret guard: clean` |
| R1-R | REQUIRED | PASS | freeze staged rename: `BLOCKED`, destination `r1-dst.txt` named |
| R1-T | REQUIRED | PASS | freeze staged typechange: `BLOCKED`, destination `r1-link` named |
| C6a-x | CONTROL | PASS | mutant from decoy cwd: `MISMATCH` (read decoy ledger) |
| C6a | REQUIRED | PASS | freeze from same cwd: `all totals match D-057(1) as ruled` |
| C6b-x | CONTROL | PASS | mutant from decoy cwd: printed distinctive decoy floor `99999` |
| C6b | REQUIRED | PASS | freeze from same cwd: distinctive floor absent |
| C6c-x | CONTROL | PASS | mutant wrote `core.hooksPath=.githooks` into the foreign repo |
| C6c | REQUIRED | PASS | freeze refused; foreign `core.hooksPath` unset |
| C6d-x | CONTROL | PASS | mutant `test.sh` from decoy cwd fired decoy shim(s) |
| C6d-shim | REQUIRED | PASS | freeze from decoy cwd fired no decoy shim |
| C6d-start | REQUIRED | PASS | freeze from decoy cwd: Sentinel stages actually started |

Harness exit 0. REQUIRED failures: 0. CONTROL failures: 0.

## C6d completing probe

`GATE PASSED` from decoy cwd: **not observed** (wait bound expired after Sentinel stages had already started). Informational. See `C6d-PROBE.md`. Not scored as a control failure.

## What this does not establish

- A1 verdicts. None relabelled.
- Severity. T2 puts that with the independent reviewer. R1's own adjudication says *"No claim about severity or priority."*
- D-055. No condition flipped.
- Completeness of git-environment injection (that is V-6's enumeration).
- That a named-list scrub would be enough (it is what produced V-6).
