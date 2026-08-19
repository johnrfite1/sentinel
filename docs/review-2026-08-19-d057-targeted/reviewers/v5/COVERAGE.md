# V5 — COVERAGE

What this review looked at, what it did not, and where its evidence stops.

Frozen commit: `c8d15a76425544148d7da2f8fa0c003feb6ad2b7`, confirmed with `git rev-parse HEAD`
before any other command. Scope: the three documentation corrections made **in that commit
itself** (recorded as `A-080`). Per the COMMON BRIEF this is targeted reverification, not a new
review; anything found outside scope is filed as a residual in `REPORT.md`.

---

## 1. The general property each item must establish

Stated before looking at the fix, as the COMMON BRIEF requires.

| Item | The general property |
|---|---|
| 1 | **Every reader-facing surface that states how many findings are currently accepted as limits states the same number, and that number is derivable from the underlying record.** Not "the one sentence a reviewer quoted is fixed". |
| 2 | **Nowhere in the tree does the hash-at-start/recheck-at-exit design read as something to build**, and the design that replaced it is preserved with its limits intact. |
| 3 | **A fresh instance reading only `docs/session-state.md` forms a picture of the project no more finished, complete or verified than the tree actually is** — including its numbers. |

## 2. Siblings enumerated MECHANICALLY, not from memory

| Item | How siblings were enumerated | Result |
|---|---|---|
| 1 | `ls docs/*.md` (11 reader-facing docs) + `ls -d docs/review-*` (5 frozen dirs) + repo-root `.md`; then three wrap-tolerant regex sweeps over the whole tree | 6 reader-facing surfaces carry a count; 23 hits under `docs/review-…/` correctly untouched |
| 2 | One wrap-tolerant sweep for the design's wording over the whole tree, all file types | 6 reader-facing surfaces + 3 frozen review artifacts + 2 scripts |
| 3 | `command grep -n "^## \|^### " docs/session-state.md` (18 sections); `git show HEAD -U0` hunk headers to establish which regions A-080 actually touched | A-080 touched lines 6–259 only; §3 (l.338–477) untouched |

## 3. Controls paired with every probe

A probe with no control cannot distinguish "the fix works" from "nothing is measured".

| Probe | Paired control | Control behaved oppositely? |
|---|---|---|
| Count sweeps return few hits | Planted canary string, found by both grep paths (P0.3) | YES |
| Line-based sweeps | Planted a line-straddling phrase; line grep returned 0, wrap-tolerant found it (P0.4) | YES |
| §13.4 yields SIX | Mutated `G-3`'s status; count moved 6→5; restored (P1.2) | YES |
| No count in `HANDOFF.md`/`README.md` | Same regex over `docs/` returned 12 hits (P1.9) | YES |
| No live rejected-design recommendation | Planted the sentence in a scratch dir; sweep found it (P2.7) | YES |
| Gate protection is real | `check-gate-immutability.sh` probe 2a: unprotected subject **was** corrupted, exit 127 (P2.6) | YES |
| "ten accepted" corrections complete | The near-identical phrase in `exit-criterion-packet.md` **was** struck (P3.4) | YES |
| §3's figures are wrong | "50 corpus fixtures" checked and found **correct** (P3.8) | YES |
| Handoff overclaims | Cold read by a context-free instance (P3.9) | YES — it under-claimed |

## 4. Falsifications actually performed

- **Mutated `docs/v1-1-register.md` §13.4** (`G-3` ACCEPTED → FIXED) and confirmed my count moved
  6 → 5, then restored and confirmed `git diff` clean. My instrument observes the source.
- **Ran `scripts/check-gate-immutability.sh`** and read its output rather than its status. Its
  own unprotected control was corrupted (exit 127), so its 10/10 is not vacuous. Probe 5
  independently demonstrated the completion-token refusal (exit 5).
- **Ran `scripts/check-suite-floors.sh`** to obtain the gate's real floor constants rather than
  trusting any document's statement of them. This is what exposed the Item 3 defect.
- **Ran a genuinely context-free cold read** of `docs/session-state.md` in a separate instance
  with no repository access, no brief, and no knowledge of this review.

## 5. What was NOT done, and why

- **The deep gate was not run.** Out of scope: A-080 is documentation-only and changes no suite
  or guard behaviour, which `git show --stat HEAD` confirms (6 files, all `.md`). The fast gate
  was not run either — the COMMON BRIEF forbids editing `scripts/test.sh` during a run and
  nothing in scope required a full gate.
- **The environment-read token-forgery residual was not exploited.** Confirming it would mean
  reading another process's environment; the mechanism was verified by reading the code that
  passes `SENTINEL_GATE_TOKEN` into the body, which is sufficient to confirm the residual is
  accurately *stated*. It remains an open, declared residual — not something this review closed.
- **Correctness of the accepted limits themselves was not re-adjudicated.** Only the arithmetic
  and the consistency of the count across surfaces. Whether SIX findings *should* be accepted is
  John's, decided at D-051(b).
- **`docs/review-…/` artifacts were read but never evaluated as defects.** They are frozen
  evidence; `git show --stat HEAD` confirms none was touched.
- **No verdict is offered on whether A-080 closes A-078(b), D-055 condition 4, or any gate.**
  Not an agent's call.

## 6. What the evidence does and does not establish

**Establishes:**
- The accepted-limit count SIX is **correct**, derived independently two ways (§13.4 status
  column; §11.0's ten-entry roster minus the four entries A-076 fully removed).
- The rejected gate design cannot be mistaken for a live recommendation in the register or in
  either script header, and the design that replaced it is real, is implemented as described,
  and is falsified by a guard with a working unprotected control.
- The A-077(b) threat-model residual in §13.6 is faithful to A-077's own text and to the code.
- `docs/session-state.md`'s narrative of the review/reverification sequence is accurate against
  `git log`, its blanket claims are gone, and its push status matches the actual remote ref.
- Three gate floor constants are duplicated in `docs/session-state.md` §3, and a fourth
  statement there asserts four floors of which three are **stale**.

**Does NOT establish:**
- That no fifth surface anywhere states a count in a phrasing my regexes did not anticipate. The
  sweeps are wrap-tolerant and controlled, but they are regex, not comprehension. I read §11.0,
  §13.4, §13.6 and `docs/session-state.md` in full; I did not read `docs/decisions.md` in full
  (it is a single-line-per-entry ledger of ~250 very long lines) — I searched it exhaustively
  and read every hit's surrounding paragraph.
- That the six accepted limits are individually still accurately described. Out of scope.
- That the gate cannot be corrupted. The guard proves specific properties on synthetic bodies;
  the environment-read residual is open by design.
- Anything about whether the corrections in `8990255` are themselves sound — that is the wider
  targeted reverification this cycle exists to perform, and it is other reviewers' scope.

## 7. Blind spots I am aware of

- **I am one reader.** The Item 2 cold-read verdict is a judgement about how text lands. I
  mitigated it by reading §13.6 before reading the commit message, but I cannot un-know the
  brief's framing that a defect was alleged there.
- **The cold-read control ran on one instance.** A second cold reader might weight the file
  differently. Its conclusion was strongly consistent with the tree, which is the outcome that
  matters, but n=1.
- **Line numbers cited are for this frozen commit only** and will drift on the next edit.
