# BRIEF V3 — a refusal code that names one of two conditions, and two guards that certify a
# section they never locate

Scope: **`R2-F6`** and **`R4-F3`**.

---

## Item 1 — `R2-F6`

**Original finding (INFO):** `SIGNER_CHAIN_UNSTABLE` covers **two different conditions** and its
published record names only one.

- `ts/src/signer/vault.ts` — the head is **PENDING / not yet confirmed** (`head.hash === null`):
  the attempt `continue`s and **no reads are issued at all**.
- `ts/src/signer/vault.ts` — the head **MOVED** (or a same-height reorg): the attempt
  `continue`s and the reads are discarded.

`ts/src/signer/protocol.ts` documents the code as exactly the second: *"the vault was read
repeatedly and the chain moved each time"*. **A node returning a hashless head five times running
never moved and was never read** — so the signed D-012 refusal record commits a reason code whose
published meaning the evidence does not support. That is a record-fidelity defect in a code whose
entire justification is record fidelity.

**Why it needed a residual fix:** the repair was **pinned by nothing.** In the author's words:
*"both messages collapsed into one broken string, 526/526 green."* The suite could not observe the
defect the repair was written to fix.

**What you must establish:**

1. **The unpinned / confirmation-pending behaviour itself.** Drive the pending-head path
   (`head.hash === null`) and the head-moved path separately. Confirm each produces the behaviour
   and the message the code and its docstring now claim for it.
2. **The MESSAGE.** A reader of a refusal record must be able to tell which condition occurred.
   **Verify that the pending/unconfirmed case is not reported using language that asserts the
   chain moved, or that reads were made and disagreed.** A pending confirmation must not be
   reported as a confirmed observation.
3. **THE TESTS — this is the part that failed before.** Collapse the two messages into one, or
   swap them, and confirm a **named test fails**. If the suite stays green under that mutation,
   the repair is pinned by nothing and the verdict is `FAIL` regardless of the suite total.
   Run the mutation; do not reason about it.
4. **The CLASSIFICATION.** Check how this item's status is recorded in the maintained documents.
   **A pending or unconfirmed condition must not be reported anywhere as confirmed, fixed, or
   accepted.** This applies both to the runtime record (a pending block reported as a confirmed
   chain observation) and to the project's own status record for `R2-F6`. Check both readings.
5. **A control:** a stable chain must still produce a normal successful read, and the ordinary
   `SIGNER_VAULT_UNREACHABLE` condition must still be distinguishable from both of the above. A
   signer that had simply started refusing everything must not pass your check.

---

## Item 2 — `R4-F3`

**Original finding (MEDIUM, instrument defect):** `scripts/check-type-strings.sh` and
`scripts/check-eval-codes.sh` both **certify a NAMED SECTION** of
`Sentinel_Protocol_Lab_Proposal_v0_2.md` while **grepping the entire 84KB document.** Neither
locates a section. `check-type-strings.sh` can print
`type strings: 6/6 published in §5.8 match eip712.ts exactly` while §5.8 publishes a transposed
type string, because the matching line was found somewhere else in the file.

**YOUR SPECIFIC OBLIGATION, and it is narrower and sharper than the original finding:**

**Verify that DUPLICATE TYPE PUBLICATION *WITHIN THE SAME §5.8 SECTION* IS DETECTED — not only
duplication across separate sections.** The obvious repair to a "grepped the whole file" defect is
to bound the search to the section. That fixes cross-section confusion and can leave
**intra-section** duplication completely undetected: two copies of a type string inside §5.8, one
correct and one transposed, with the checker matching the first and reporting `6/6`.

So:

1. **Construct the intra-section case.** In your worktree, put a second, WRONG copy of a type
   string inside §5.8 alongside the correct one. Run the checker. **If it still prints a clean
   6/6, that is a FAIL.** Try both orders — wrong copy first, wrong copy second — because a
   `head -1` makes order decisive.
2. **Construct the cross-section case too**, so you can say whether the repair fixed only the
   demonstrated half.
3. **INCLUDE A LEGITIMATE NON-DUPLICATE CONTROL.** A document that legitimately mentions a type
   name once in its proper place — and any legitimate repeated *substring* that is not a real
   duplicate publication — must NOT be flagged. A checker that fails on everything is not a
   checker. Say explicitly what your control was and that it passed.
4. **Do the same reasoning for `check-eval-codes.sh`** and say whether the argument was carried
   across to it or only applied to the file the finding named. The two scripts are siblings and
   this project's recorded failure mode is fixing one and not the other.

---

## Deliverables — write these into `<EVIDENCE>/reviewers/v3/`

`REPORT.md`, `PROBES.md`, `COVERAGE.md`, per the COMMON BRIEF. Separate verdicts of
`HOLD` / `FAIL` / `UNVERIFIABLE` for `R2-F6` and for `R4-F3`. Residuals separate from failures.
