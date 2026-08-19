# COMMON BRIEF — targeted independent reverification of the A-080 checkpoint

**Authority:** D-057(9) — *targeted reverification, not another round.* John authorised this
cycle on 2026-08-19. **This is NOT a new review.** Do not hunt for new findings outside your
assigned scope; if you trip over something serious anyway, report it under RESIDUALS, clearly
separated from your verdicts.

**FROZEN COMMIT — the only thing you are evaluating:**
`c8d15a76425544148d7da2f8fa0c003feb6ad2b7`

Confirm it before anything else: `git rev-parse HEAD` in your worktree must print that SHA.
If it does not, stop and say so.

## The one rule that matters most

**VERIFY THE ARGUMENT, NOT THE DEMONSTRATION.** This project's recorded, repeated failure mode
is a repair that fixes the exact case a reviewer exploited and leaves the identical hole one
line, one branch, one file or one language away. Three of the repairs you are checking were
already sent back once for exactly this. So for every item:

1. State the **general property** the repair is supposed to establish — in your own words,
   before you look at the fix.
2. Ask **where else that property must hold**, and enumerate those siblings **mechanically**
   (grep, a file listing, a symbol search) rather than from memory or from the finding text.
3. Only then check whether the repair covers them.

Re-running the original reviewer's probe and watching it pass is **not** reverification.

## What every finding-level verdict must contain

- **Exact files and invocation shapes inspected.** Real paths, real commands, copy-pasteable.
- **An observing falsification, or a pre-fix comparison, wherever practical.** Break the thing
  and confirm the test/guard *notices*. If you cannot break it, say why.
- **A paired control** that must behave the *opposite* way. A probe with no control cannot
  distinguish "the fix works" from "everything is refused now" or "nothing is measured".
- **What your evidence does and does not establish.** Be explicit about the gap.
- **A verdict: `HOLD`, `FAIL`, or `UNVERIFIABLE`.** Not "looks fine".
- **Residuals listed separately from failures.** A residual is a real limit you are recording;
  a failure is the repair not doing its job. Do not merge them.

## Four traps this project has actually paid for — check yourself against each

- **A GREEN SUITE IS NOT EVIDENCE IF ITS ASSERTIONS CANNOT OBSERVE THE NAMED DEFECT.** Before
  you trust a passing test, mutate the code it covers and confirm the test goes red.
- **A DEAD PROBE'S SILENCE READS EXACTLY LIKE A PASS.** Five dead probes shipped here in two
  days: a mutation of a value already at its maximum; a Solidity probe that did not compile; a
  run that died before reaching the code under test; a grep that matched nothing. **Ask what
  your probe MOVED before believing what its result implies.**
- **EXIT STATUS 0 IS NOT SUCCESS.** Read output. A truncated bash script exits 0.
- **A CHECK CAN BE CAUGHT BY THE WRONG CHECK.** If your tamper is rejected, prove it was
  rejected by the check you are testing and not by a neighbouring one.

## Working rules

- **Work ONLY inside your own worktree.** You may edit it freely — that is what it is for.
  **Never touch the primary repository tree**; other reviewers are reading the same SHA.
- **Never edit `scripts/test.sh` while a gate run is in flight.** It corrupts the run, and one
  such run exited 0 without printing `GATE PASSED`.
- **Write your deliverables into your assigned evidence directory** (given in your own brief).
- **NO MACHINE-SPECIFIC ABSOLUTE PATHS IN ANYTHING YOU WRITE.** Your reports get committed to
  this repository, which has a guard against exactly that. Write `<WORKTREE>/contracts/...`,
  never a real home directory path. Repository-relative paths are always fine.
- **No secrets, no session IDs, no environment dumps** in your deliverables.

## What you may NOT do

Do not sign or reopen a gate. Do not certify any public claim. Do not ratify a correction. Do
not push, publish, or rename anything. Do not commit. Do not edit the primary tree. If you
believe a decision is needed, write it down as a question for John — do not answer it.
