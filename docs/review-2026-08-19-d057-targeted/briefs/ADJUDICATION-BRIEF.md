# ADJUDICATION BRIEF — the six findings raised during the D-057(9) targeted reverification

**Authority:** D-058(7), John, 2026-08-19: *"The additional findings and residuals are not one
undifferentiated batch. Adjudicate each new item first and classify it as confirmed, refuted,
duplicate, historical, or a decision fork. Do not repair or accept an unadjudicated list
wholesale."*

**You are ADJUDICATING, not repairing.** Change nothing outside your evidence directory. You may
edit your own worktree freely to run probes; restore it afterwards.

**Frozen commit:** `a18e6e61598a996d962798ad0353a166232d4490`. Confirm with `git rev-parse HEAD`.

## The five classifications — pick exactly one per item

| Class | Means |
|---|---|
| **CONFIRMED** | The defect is real and live at this commit. You reproduced it. |
| **REFUTED** | The mechanism does not hold, or holds only under conditions that cannot occur. |
| **DUPLICATE** | Already covered by an existing finding or an accepted limit. Name which. |
| **HISTORICAL** | The text is a dated record of what was true then, not a current claim. |
| **DECISION FORK** | Real, but resolving it changes what the product guarantees or promises. **Not yours to resolve — state the fork and its options.** |

A finding can be CONFIRMED *and* carry a decision fork about its remedy. Say so if it does.

## What every adjudication must contain

- **The exact claim or guarantee at issue**, in your own words.
- **Its authoritative source** — the file and construct that decides the question. Code beats
  prose; a generated artifact beats the prose describing it.
- **A reproduction**, or an explicit statement that you could not reproduce it and why.
- **A paired control** that must behave the opposite way. Without one you cannot distinguish
  "the defect is real" from "everything fails" or "nothing is measured".
- **Severity as you assess it**, with reasoning. You may differ from the reporter.
- **What your evidence does and does not establish.**
- **The classification**, from the table above.

## Traps that have already fired on this commit — check yourself against each

- **This machine's `grep` is a `ugrep` wrapper honouring `--ignore-files`.** It returns exit 1
  and no output for strings BSD grep finds. **Use `/usr/bin/grep`.** A zero result from the
  wrapper reads exactly like a clean sweep.
- **The repository hard-wraps prose.** A phrase you search for may straddle a newline and match
  no line-based regex. Two real defects survived a "clean" sweep this way. Join logical
  paragraphs or read the region.
- **A naive Solidity mutation is a COMPILE ERROR, not a survivor.** Orphaning a parameter fails
  `deny = "warnings"` and reads as SURVIVED. Classify compile failures separately.
- **Foundry's `vm.recordLogs` RETAINS logs from a reverted frame.** A test written that way will
  falsely confirm that a log survives a revert. On chain it does not.
- **Ask what your probe MOVED** before believing what its result implies.

## Forbidden

Do not repair anything. Do not sign, certify, ratify, reaffirm or revoke any gate or
certification. Do not push or commit. Do not resolve a decision fork — state it.
