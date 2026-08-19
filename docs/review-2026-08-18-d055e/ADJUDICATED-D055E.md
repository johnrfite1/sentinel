# D-055(e) — the adjudicated list, for John

**Run 2026-08-18/19 against frozen `7e0ab7f`.** Four reviewers, four worktrees, four evidence
directories, at most two concurrent. **Every finding cross-adjudicated by a reviewer who did not
author it.** The coordinating agent adjudicated NOTHING — it authored the code behind eleven of
the twenty findings.

**Status: NOT ACTED ON.** Per D-051(c) this comes to you without remediation. Whether the round
is clean under D-055(a) is your judgement.

## 20 findings · 19 CONFIRMED · 1 REFUTED · 3 downgrades awaiting your countersignature

| id | claim | reviewer | adjudicator | verdict | severity |
|---|---|---|---|---|---|
| **R1-F1** | **the gate snapshot is reachable and corruptible mid-run; the "private file" claim is false** | R1 | R3 | **CONFIRMED** | **CRITICAL** |
| R1-F2 | scope guard prints "all assigned" after measuring nothing when its base ref fails | R1 | R3 | CONFIRMED | HIGH → **MEDIUM** ↓ |
| R1-F3 | nothing invokes the scope guard | R1 | R3 | CONFIRMED | MEDIUM → **LOW** ↓ |
| R1-F4 | register §13.6 still prescribes the rejected design | R1 | R3 | CONFIRMED | LOW |
| R1-F5 | deep run's coverage boundary says it was "this default" | R1 | R3 | CONFIRMED | LOW |
| R2-F1 | E3 pinned the signer, left the SIMULATOR unpinned | R2 | R4 | CONFIRMED (argument refuted) | HIGH → **LOW** ↓ |
| R2-F2 | anchor binds a label, not a simulation | R2 | R4 | **REFUTED** | — |
| R2-F3 | `expectedEffects` omits the vault's immutable cap | R2 | R4 | CONFIRMED | LOW |
| R2-F4 | A-074 residual cites a register entry that does not exist | R2 | R4 | CONFIRMED | MEDIUM |
| R2-F5 | call-graph absence records PASS | R2 | R4 | CONFIRMED (1 of 2 grounds) | MEDIUM |
| R2-F6 | `SIGNER_CHAIN_UNSTABLE` covers two conditions, names one | R2 | R4 | CONFIRMED | INFO |
| R3-F1 | §11's "MEASURED" G-3 reproduction names the wrong class, undercounts 3 as 2 | R3 | R1 | CONFIRMED | MEDIUM |
| R3-F2 | ablation partition check compares a hand-typed duplicate, asserts nothing | R3 | R1 | CONFIRMED | MEDIUM |
| R3-F3 | evaluator output reaches a labeller view under an innocuous name | R3 | R1 | CONFIRMED | MEDIUM |
| R3-F4 | three policy/mandate fields consulted by nothing, undisclosed | R3 | R1 | CONFIRMED | MEDIUM |
| **R3-F5** | **`D-05` fixed in TypeScript, never generalised to Solidity — policy half survives 75/75** | R3 | R1 | CONFIRMED | MEDIUM |
| **R3-F6** | **`D-06` closed the engine's ten edges, never the vault's — 6 survivors** | R3 | R1 | CONFIRMED | MEDIUM |
| **R3-F7** | **five of eight vault events can state something false with 75/75 green** | R3 | R1 | CONFIRMED | MEDIUM |
| **R3-F8** | **`D-10`'s repair pinned 2 of 9 sites, and its measured premise is FALSE (F024)** | R3 | R1 | CONFIRMED | MEDIUM |
| R4-F1 | the S2 pack says FIVE accepted limits remain; SIX do (`G-3` dropped) | R4 | R2 | CONFIRMED | MEDIUM |
| R4-F2 | round-six README omits one of its own four sanitizations | R4 | R2 | CONFIRMED | LOW |
| R4-F3 | type-string/eval-code guards certify a NAMED section while grepping the whole file | R4 | R2 | CONFIRMED (instrument defect, NOT live) | MEDIUM |
| R4-F4 | `session-state.md` §3 publishes 507/198; real figures are 513/209 | R4 | R2 | CONFIRMED | MEDIUM |

## THE ONE ITEM R1 ASKED BE PUT TO YOU AS ONE, NOT FOUR

**R3-F5, F6, F7 and F8 are four independent measurements of a single pattern: THE REPAIR
GENERALISED THE DEMONSTRATION, NOT THE ARGUMENT.** `D-05` and `D-06` fixed one language away
from the vault; `D-10`'s repair missed its own stated argument; `D-043` missed the five events
it did not name. **This is the pattern `docs/repair-protocol.md` exists to stop, measured four
times in one round, and it holed three of the coordinating agent's own repairs this session.**

## Two adjudications that CORRECTED their reviewer

- **R3 raised the stakes on R1-F1**: the corruption is **non-deterministic** — 2 of 8 real-gate
  trials completed cleanly with the edit demonstrably applied. R1 called it deterministic. **A
  certification instrument corrupted on ~¾ of attempts and silently green on the rest is worse,
  and it means one clean trial is not evidence a repair worked.**
- **R4 refuted R2-F1's argument** by following the artifact to its consumer: the straddle is
  real, but the signer's E3 equality converts it into a refusal, so no receipt is issued.

## THE EXIT QUESTION, and the adjudicators disagree with the reviewer

R4-F1 is a false count. **R2 (adjudicating) found R4's "it is in SIGNED text" lever does not
hold**: the pack was signed 2026-08-16 (D-041); §11.0's heading is dated 2026-08-18 and its
corrections are A-075/A-076 of that day. **John did not sign "five."** It is post-signature text
inside a signed document — under a header asserting "§11 … is part of what was signed", which
R2 flags as its own unscoped problem.

**R2's independent view: it should not block exit, and should not be accepted either — it should
be CORRECTED, because that costs one line and accepting it costs the criterion its meaning.**
Reading it as blocking makes C1 condition 4 satisfiable by bookkeeping rather than substance.
**The disposition is John's.**

## Three downgrades requiring John's countersignature (D-056(e))

| finding | from | to | adjudicator's reasoning |
|---|---|---|---|
| R1-F2 | HIGH | MEDIUM | load-bearing half unaffected; base ref does resolve today — **"HIGH stays defensible on the same facts"** |
| R1-F3 | MEDIUM | LOW | the manifest already says "do not trust that line — run it" |
| R2-F1 | HIGH | LOW | straddle is real but converted to a refusal by E3; comments overclaim locally |

**R3 notes R1-F2 and R1-F3 COMPOUND, and says the compound deserves attention regardless.**

---

# D-055 EXIT ASSESSMENT — **NOT MET**

Assessed against D-055(a)'s four conditions, on the closing verification run at `7e0ab7f`.

| D-055(a) condition | Met? | Evidence |
|---|---|---|
| One independent, fixed-scope post-D-052 review on the repaired apparatus | **YES** | Four reviewers, scope fixed by John at D-056(d) BEFORE the run, cross-adjudicated, all deliverables on disk |
| Passing deep gate and workspace guards | **YES** | GATE PASSED at `7e0ab7f`; 75 / 513 / 209 / 7 samples / 78 tamper over 30 modes; corpus verified file-by-file, 51 results identical; guards 0 new findings |
| **Zero unresolved confirmed Critical/High defects** | **NO** | **R1-F1 CONFIRMED CRITICAL, unrepaired** |
| Zero known false or unsupported signed/certified claims | **NOT MET** (D-057(1)) | R4-F1 is a false count, AND §11's header falsely claims its post-signature text was part of what was signed |

**EXIT IS NOT MET. TWO conditions fail, not one.**

**CONDITION 4 IS NOT MET, CORRECTED FROM "CONTESTED" BY JOHN (D-057(1)).** The adjudicator
established that the "five limits" sentence post-dates D-041's signature, and the coordinating
agent recorded that as making the condition contested. **John ruled otherwise, and the reason is
sharper than the arithmetic:** §11's header asserts that its content was part of what was
signed. That assertion is FALSE for the post-signature text it now carries. **A document that
claims retrospective signature for text added after signing is a false signed claim in its own
right, independent of whether the count inside it is right.** Post-signature text is not
retrospectively signed by the header saying so.

## The green deep gate is not reassurance here, and saying so is the point

The same run that printed `GATE PASSED` also printed **`gate immutability: 5/5`** — from the
instrument R3 confirmed is blind to the CRITICAL, using an attack it does not attempt. **A
passing gate is evidence about what the gate measures.** Under T4 that is stated rather than
left to be inferred: this run asserts the floors, the corpus provenance and the verifier suite;
it asserts nothing about whether the gate could have been corrupted while running.

## Carried and ratcheted items in this exit record (T4)

- 14 of 20 corpus classes exercise the class they name — and **R3-F1 shows §11's reproduction of
  that qualification names the wrong class and undercounts 3 as 2**.
- All four count floors are ratchets against ACCIDENT, not intent; every floor is met with
  **zero headroom** (R4's null result).
- Vendor honesty is "certified by record", not re-measured.
- Gate 6 is carried ENTIRELY by the deterministic tests; the invariant campaign's marginal
  contribution is zero — **re-confirmed by R3 on a sweep 4× wider than the certifying one, and
  found NOT understated**.

## What must happen before exit can be reassessed

1. **R1-F1 (CRITICAL)** — repaired and independently reverified by a reviewer who did not author
   the repair, or explicitly accepted by John as a documented product boundary. **An agent may
   do neither alone.** Note that the natural repair changes what the gate GUARANTEES, so under
   D-056(e) it returns to John rather than being implemented.
2. **The three downgrades** — countersigned, or restored to the reviewer's severity.
3. **R4-F1** — corrected (the adjudicator's recommendation) or ruled non-blocking.
4. The remaining 15 confirmed Medium/Low — individually adjudicated already; each now needs
   repair, or an accurately bounded acceptance decision from John.

**No gate signed. No claim certified. No publication authorised. D-016 unchanged.**
