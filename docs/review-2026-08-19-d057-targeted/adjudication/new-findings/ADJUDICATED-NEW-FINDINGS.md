# Adjudicated new-findings table — D-058(7)

**Adjudicator synthesis.** The two adjudicators' own deliverables are `ADJ1.md` and `ADJ2.md`,
unaltered. Both worked from frozen `a18e6e61598a996d962798ad0353a166232d4490`, in separate
worktrees, neither having reported the findings they judged.

| # | Finding | Class | Severity | Disposition |
|---|---|---|---|---|
| 1 | `V3-N2` — `check-vendor-honesty.sh` certifies §7.2 while grepping the whole document | **CONFIRMED** | MEDIUM (unchanged) | **Batch A**, consumer of primitive A-P2. **Gate 5 status fork returns to John** |
| 2 | `F7-R1` — vault NatSpec claims the `OverrideAuthorized` log survives a revert | **CONFIRMED** | LOW as risk | **Batch B (B-F1)**. Remedy foreclosed to truthful NatSpec by D-058(5) |
| 3 | `N-TESTSH-FLOORS` — stale floors in `scripts/test.sh`'s COVERAGE block | **DUPLICATE** of `R4-F4` under D-058(2) | — | Repaired **inside A-F1**, not as a separate item |
| 4 | `N-SCOPE-CD` — unguarded `cd "$(git rev-parse --show-toplevel)"` | **CONFIRMED**, distinct from `V3-N1` | **LOW** (down from MEDIUM) | **Batch A**, consumer of primitive A-P1 |
| 5 | `N-EVAL-ACTION-TARGET` — fictitious `EVAL_ACTION_TARGET_MATCHES_MANDATE` | **CONFIRMED**, cosmetic | LOW | **Batch D (D-F4)** |
| 6 | `N-DECODE-E4` — "checked by NEITHER the signer nor the verifier" | **CONFIRMED IN PART** | MEDIUM | **Batch D (D-F4)**. The signer half is TRUE and deliberate |

**Nothing was refused, nothing was accepted wholesale, and no item entered a batch unadjudicated
— which is what D-058(7) requires.**

## Why two severities moved

- **`N-SCOPE-CD` MEDIUM → LOW.** The adjudicator swept all 61 tracked directories under
  sabotage: **fail-closed at 60 of 61, fail-open nowhere.** It never produces `V3-N1`'s
  prohibited "all assigned, exit 0" shape. What survives is a FALSE diagnostic (13 files named
  unassigned that are assigned), which is a real defect at a lower grade.
- **`N-TESTSH-FLOORS` → DUPLICATE.** D-058(2) rules `R4-F4` covers all six constants, which
  absorbs this by construction. `A-081`'s own `R4-F4` record already names "stale floors printed
  by `scripts/test.sh` itself".

## Corrections the adjudication made to earlier reviewer claims

Recorded because a reviewer's number is not automatically right either.

- **V5's "stale trio" in `test.sh` is FOUR stale figures across two sentences** — `180` at
  `:980-981` plus `160/77/29` at `:984` — and the block duplicates four of the six constants.
- **V2's stated conclusion that "no stale disagreeing live duplicate exists at this commit" is
  FALSE.** `docs/session-state.md:470` carries one, ~79 lines below the passage V2 did flag.
- **The claim that the two vault execution branches differ in revert-survival is wrong.** Both
  funnel into `_consumeAndCall`. They differ in event count, `viaOverride`, ordering and
  authentication strength — not in what survives a revert.

## THE GATE 5 STATUS FORK — D-058(4), returned to John, not resolved

**No certification was revoked, reaffirmed, or changed.**

**What `V3-N2` does NOT falsify:** the adjudicator measured the guarded property independently
of the guard and **it is TRUE at this commit** — the anchor phrase occurs exactly once tree-wide,
inside §7.2 (lines 663–686), and the ablation report carries that exact wording (its copy is
emitted by a generator literal in `ts/src/ablation/report.ts`). *(Independently re-verified by the
coordinator.)* The broken block enforces an **unnumbered supplementary condition** — the A-028
caveat — **not any of D-008(1)–(4)**. D-008(1) rests on a separate §2-anchored `awk` with §13
resolution **plus** the human per-row source-verification pass and D-038's seven rulings; (2) and
(4) are correctly-unscoped whole-file scans; (3) is John's certification plus a §2 SHA-256 pin.

**The fork, not exclusive, and not an agent's:**

- **(A)** The certification stands; the remedy is scoping the extraction to §7.2 (keeping
  report-side wrap normalisation) plus correcting two prose sites. **Precedent: A-039 repaired
  the identical defect in this same file without reopening a gate.**
- **(B)** The phrase *"extracted from §7.2 itself"* is a false statement about an enforcement
  mechanism, and it sits inside `docs/gate-s2-evidence.md` — **a SIGNED pack held immutable by a
  guard.** Whatever rule governs a false claim in signed text applies here.
