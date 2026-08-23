# C6d completing probe

## What was asked

The last stretch stopped the C6d probe before a completing `GATE PASSED` from a decoy cwd was observed. Complete it, or say plainly why it cannot be completed.

## What was run

Freeze clone of HEAD. Invoke the clone's `scripts/test.sh` **by absolute path** with cwd a foreign git repository that contains instrumented `scripts/*` shims. Identity, if it holds, cds into the clone and runs Sentinel's own children. Identity, if it fails, cds into the decoy and the shims fire.

Wait bound: 240 seconds (Python `subprocess` timeout; macOS has no `timeout(1)`). Completing `GATE PASSED` from decoy cwd is informational. A timeout is not a CONTROL failure.

## Mutant (exploit control)

Supervisor root assignment replaced with `git rev-parse --show-toplevel` from cwd. Script-in-`scripts/` check replaced with `true`.

From the decoy cwd the mutant fired decoy shims (marker file non-empty). CONTROL PASS. The mutant body still printed Sentinel step banners — those banners are in `test.sh` itself — then invoked decoy children. Later stages in the decoy have no `contracts/` tree; that is expected once identity has already failed.

## Freeze (observing test)

No decoy shim fired (marker file empty). Sentinel stages started from the decoy cwd: gate-immutability completed its ten probes, then `secret guard: clean`, then V-1, then the rename gate. Identity held.

`GATE PASSED` was **not** observed before the wait bound. The freeze log ends during later suite stages, not on the completion line.

## Why the completing gate was not observed

The freeze identity path runs the real suite. The wait bound is enough to see that decoy shims do not fire and that Sentinel stages start. It is not enough, on this machine, to wait out Foundry + TypeScript + verifier to the completion banner. Extending the wait would observe more of a suite the identity check has already selected. It would not add a new fact about C6d's hole.

Stated plainly: **the completing `GATE PASSED` from decoy cwd was not observed. The identity claim was observed: decoy shims silent, Sentinel stages live.**

## Blind spot

A hang *inside* a Sentinel child after identity has held would also fail to print `GATE PASSED`. That is a suite-liveness question, not C6d. This probe does not distinguish them past the wait bound.
