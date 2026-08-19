# BRIEF V2 — a coverage instrument that reported coverage it did not measure, and a count

Scope: **`V3-N1`** and **`R4-F4`**. Neither needs Solidity. Both are about instruments and
documents telling a reader something they did not check.

---

## Item 1 — `V3-N1`

This one was found by a verifier *unasked*, while checking a different repair. The repair it
sits beside (`R1-F2`) established the general property: **a coverage instrument must never
report coverage it did not measure.** The author guarded the `git diff` path in
`scripts/check-review-scope.sh` and **left `git ls-files` in the identical unguarded shape one
block above it**. With `ls-files` failing, the script printed
`0 file(s) changed since A-070, all assigned` and exited 0 — byte-identical to the sentence
`R1-F2` was filed against.

**What you must establish, by making it happen rather than by reading the code:**

1. **Make `git ls-files` FAIL, and verify the checker fails CLOSED.** Shadow `git` on `PATH`
   with a stub that errors on `ls-files`, or otherwise force the failure. The checker must
   refuse — not print a clean-looking summary, not exit 0.
2. **Make `git ls-files` return an unexpectedly EMPTY result, and verify refusal.** Empty is
   the dangerous case: it is indistinguishable from "nothing to assign" and reads as success.
3. **Verify the diagnostic names the correct base/reference** — not a stale or misleading one.
   The message a reader gets must point at the actual comparison the script performs. If it
   names a commit or reference that is wrong, out of date, or not the one used, that is a FAIL
   even if the fail-closed behaviour is correct.
4. **A control:** an ordinary unmutated run must still succeed and still assign every tracked
   file. Without it you cannot tell fail-closed from always-fails.
5. **Sweep for siblings.** The whole point of this finding is that one guarded call sat next to
   an unguarded twin. Enumerate **every** external-command call in that script whose empty or
   failed output could be mistaken for a clean result, and say whether each is guarded.

---

## Item 2 — `R4-F4`

**Original finding:** `docs/session-state.md` §3 published `507/198` when the real figures were
`513/209`. **Why it came back FAILED:** *"I removed one copy of the suite counts and left another
eleven lines below my own claim that they were no longer duplicated."*

**What you must establish:**

1. **Suite counts are DERIVED or SINGLE-SOURCED.** Find where the authoritative numbers live and
   confirm there is exactly one source. `scripts/check-suite-floors.sh` exists for this — read
   what it actually does, and whether it reads from one place or restates numbers of its own.
2. **NO STALE DUPLICATE COUNT REMAINS ON ANY READER-FACING SIBLING SURFACE.** Sweep the
   maintained documents mechanically. Reader-facing means: would a person acting on this
   document encounter the number and believe it? `docs/session-state.md`, `HANDOFF.md`,
   `README.md`, `docs/*.md`, and the proposal are all in scope. **Preserved historical review
   artifacts under `docs/review-2026-08-1*/` are NOT** — those are frozen evidence and a number
   inside them is a record of what was said, not a live claim. State which surfaces you treated
   as which, and why.
3. **Falsify your own sweep.** Change a real floor in `scripts/test.sh` *in your worktree* and
   confirm that (a) the single-source mechanism reflects it and (b) your sweep would have caught
   a document that disagreed. A sweep that cannot fail proves nothing.
4. **A control:** a document legitimately quoting a historical count in a clearly historical
   frame must NOT be flagged. Distinguish stale-live from correctly-historical.

---

## Deliverables — write these into `<EVIDENCE>/reviewers/v2/`

- `REPORT.md` — per item: the general property, mechanical sibling enumeration, exact commands
  and invocation shapes, falsifications and their observed output, controls, what the evidence
  does and does not establish, verdict `HOLD` / `FAIL` / `UNVERIFIABLE`.
- `PROBES.md` — every command and its material output, including dead or failed probes.
- `COVERAGE.md` — what you did not reach, and why.
