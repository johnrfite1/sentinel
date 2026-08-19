# ADJUDICATION — targeted reverification of the A-080 checkpoint

**This file is ADJUDICATOR SYNTHESIS. It is not reviewer-authored.** Every reviewer deliverable
is preserved unaltered under `reviewers/`; the briefs they were issued are under `briefs/`.
Where this file and a reviewer report differ, the reviewer report is the record of what that
reviewer found and this file is the record of what was made of it.

**Frozen commit reviewed:** `c8d15a76425544148d7da2f8fa0c003feb6ad2b7` (A-080).
**Authority:** D-057(9) — targeted reverification, not another round. No new review was opened.
**Reviewers:** five, none of whom authored any repair under review; at most two concurrent.

## Result

| # | Item | Reviewer | Verdict | Independently re-checked by the adjudicator |
|---|---|---|---|---|
| 1 | `R3-F6` — vault timestamp boundaries | V1 | **HOLD** | not re-run; enumeration and per-mutant test names accepted |
| 2 | `R3-F7` — required vault event set | V1 | **FAIL** | **YES** — mutant survives, control caught |
| 3 | `R4-F4` — suite counts single-sourced | V2 | **FAIL** | **YES** — read the duplicated constants |
| 4 | `V3-N1` — scope checker fails closed | V2 | **FAIL** | **YES** — read the unguarded call site |
| 5 | `R2-F6` — chain-unstable condition/record | V3 | **FAIL** | **YES** — mutant survives, control caught |
| 6 | `R4-F3` — type-string section scoping | V3 | **FAIL** | **YES** — read both operands |
| 7 | `R2-F4` — false claim at every reader-facing site | V4 | **FAIL** | **YES** — read §7, ran the packet's own test |
| 8 | `R3-F4` — real `SIGNER_*` enforcement codes | V4 | **HOLD** | spot-checked; fictitious names survive only in A-078's own marked quotation |
| 9 | A-080(2) — accepted-limit count is six | V5 | **FAIL** | **YES** — read §13.4, confirmed the derivation |
| 10 | A-080(3) — rejected hash design | V5 | **HOLD** | not re-run; harness passed with its unprotected control corrupted |
| 11 | A-080(1) — truthful handoff | V5 | **FAIL** | **YES** — read both stale sites |

**8 FAIL · 3 HOLD.**

## The three that hold, stated first so they are not lost in the failures

- **`R3-F6` holds decisively.** V1 enumerated the vault's timestamp comparisons mechanically
  rather than from the finding, found exactly three, confirmed `executeWithOverride`'s
  `auth.expiresAt` is among them, and killed six mutants — tighten and loosen at each site —
  **each by a distinct named test**, with the revert selector naming the mutated check. That last
  step is what rules out "caught by the wrong check", which is the trap the first repair hit.
- **`R3-F4` holds.** The fabricated `EVAL_VAULT_*` names occur exactly once each in the entire
  tree, both inside A-078's own paragraph headed "A FALSE CODE NAME I INVENTED" — the acceptable
  historical category. V4 derived the real codes from the code and diffed 105 defined against 55
  named to find the orphans, which is the right shape of check.
- **A-080(3) holds.** §13.6 reads unambiguously cold; the adopted design matches the code; the
  threat-model residual is faithful to A-077(b) and to the mechanism.

## What the eight failures have in common

**Every one is the project's own recorded pattern: the repair generalised the DEMONSTRATION and
not the ARGUMENT.** That is not a characterisation added here — it is what the evidence shows,
item by item:

- **`R3-F7`** pinned the six events it scoped and left `ActionExecuted.viaOverride` asserted on
  the automatic path and by nothing on the override path. A vault logging every override as "not
  an override" passes 92/92.
- **`R2-F6`** pinned the branch the ORIGINAL finding named and left unpinned the branch the FIRST
  REVERIFICATION caused to be added. The same defect, two levels down, inside its own repair.
- **`R4-F3`** added the duplicate refusal to the SPEC operand and not to the SOURCE operand one
  line below, under a comment declaring the property for both.
- **`R4-F4`** removed the Foundry and TypeScript figures and left the verifier's three, five
  lines under the claim that the figures were no longer duplicated — the third iteration of one
  defect.
- **`R2-F4`** corrected §3b of a file and left §7 of the SAME file asserting the opposite, under
  a commit message reading "Both closed".
- **`V3-N1`** guarded two of three `git ls-files` call sites in the script whose whole subject is
  an unguarded call site.
- **A-080(2)** left a derivation that computes to five and an unstruck sentence saying five, while
  correcting a different sentence saying five.
- **A-080(1)** left two stale count sites, both invisible to a line-based sweep.

**Two of the eight are the adjudicator's own work from earlier the same day.** They are listed
with the others and were found the same way.

## Method failures recorded rather than discarded

Four instrument defects fired during this review and were caught only by controls. They are
recorded because a review that reports only its findings hides how nearly it missed them.

- **A line-based sweep cannot see a hard-wrapped claim.** Three separate reviewers hit this, and
  it is why A-080(2) and A-080(1) each left an uncorrected copy: the phrases straddle a newline.
  **Any future doc-consistency guard must join wrapped lines or it ships dead.**
- **This machine's `grep` is a `ugrep` wrapper honouring `--ignore-files`**, returning exit 1 and
  zero output for strings BSD `grep` finds. A zero result from it reads exactly like a clean
  sweep. V4 caught it with planted canaries and moved every sweep to `/usr/bin/grep`.
- **A naive Solidity mutation is a COMPILE ERROR, not a survivor.** Hardcoding `viaOverride`
  orphans the parameter and fails `deny = "warnings"`. Without a separate `COMPILE_ERROR` class
  it reads as SURVIVED. V1 classified it; the adjudicator hit the same trap and was saved by
  V1's warning.
- **Worktree provisioning self-reported healthy while broken.** See `PROVISIONING-NOTE.md`.

## What this review did NOT establish

- `R3-F6` and A-080(3) were accepted on their reviewers' evidence and not independently re-run.
- No item here speaks to whether Sentinel DECIDES correctly. This is a review of repairs to
  claims and instruments.
- A passing deep gate remains evidence about the run that produced it, not proof the gate cannot
  be corrupted — A-077(b)'s same-user environment-token residual is carried, not closed.
