# BRIEF V5 — the three documentation corrections made in the frozen commit itself

Scope: the **A-080 checkpoint** — the commit you are standing on. Its author corrected three
documentation defects and recorded the work as `A-080` in `docs/decisions.md`. **You are checking
whether those corrections are true, complete, and unambiguous.** The author is not available to
you and you should not try to reconstruct their reasoning; check the tree.

`git show --stat HEAD` shows you exactly what the checkpoint touched.

---

## Item 1 — the accepted-limit count is consistently SIX

`docs/gate-s2-evidence.md` §11.0 recorded a set of findings John ACCEPTED as documented limits
rather than fixing. It has carried **three mutually inconsistent counts** of that one set: a
heading saying TEN, a derived correction saying SIX, an unstruck sentence saying FIVE, and a
stale "nine" in the rationale.

**What you must establish:**

1. **There is exactly ONE authoritative, derived count and it is SIX.** Read the derivation.
   Check the arithmetic yourself against the underlying record — `docs/v1-1-register.md` §13.4 is
   the status table, and it is the source that was right when both prose ledgers were wrong.
   **Derive the number independently; do not accept it because the document asserts it.**
2. **No live statement of FIVE or a stale NINE survives unstruck** on any reader-facing surface.
   Sweep mechanically. Preserved reviewer/adjudication artifacts under
   `docs/review-2026-08-1*/` are frozen evidence and must NOT be rewritten — report them as such.
3. **The sibling surfaces agree.** `docs/exit-criterion-packet.md`, `docs/session-state.md` and
   `docs/decisions.md` all carried copies. Check each.
4. **A control:** confirm that a legitimately historical statement of "ten" — a document
   correctly recording what was true on its own date — is still present and is NOT being
   reported as an error. The correction must not have flattened history.

---

## Item 2 — the rejected hash/recheck design is unmistakably rejected

`docs/v1-1-register.md` §13.6 concerns a gate script that can be corrupted mid-run. A four-line
design — *"have the gate hash its own file at start and re-check at exit"* — was **rejected by
John on its merits before it was built**, on the reasoning that the ending check can itself be
skipped or corrupted when bash resumes at a shifted byte offset. The section nevertheless left
that prescription reading as a live recommendation, and its warning pointed at the wrong text.

**What you must establish:**

1. **Read §13.6 cold, as a fresh engineer would.** Would you come away thinking the hash/recheck
   design is something to build, or something rejected? **If there is any ambiguity, say so —
   that is the entire defect.**
2. **The warning points unambiguously at the rejected design**, not at some other struck text
   beside it.
3. **The ADOPTED design is preserved and still legible:** copy, open read-only, unlink, execute
   as `/dev/fd/N`, an external supervisor requiring a completion token, and exit 0 alone not
   being success.
4. **Its recorded threat-model residual is present and accurate** — specifically that a
   **same-user actor able to read the executing body's environment can forge the completion
   token**, and that the nonce defends against corruption rather than against environment access.
   **Verify this against the code and against `A-077`'s own residual text**, not just that some
   sentence about it exists.
5. **Check the guard's own header** (`scripts/test.sh` and
   `scripts/check-gate-immutability.sh`) for the same ambiguity. If the register is clear and the
   script header still recommends the rejected design, the defect survives.

---

## Item 3 — `docs/session-state.md` is a truthful current handoff

This file opens by declaring itself the project's memory and says it wins over anything an agent
remembers. Its previous version claimed that **every repair had been independently reverified**
and that **there was no agent work outstanding.** Both were false.

**The true sequence, which you should verify against `git log` and the commit messages rather
than against the file:**

- the bounded review completed;
- the CRITICAL repair was independently reverified at `497d1ce`;
- `R3-F6`, `R3-F7` and `R4-F4` FAILED that reverification;
- `V3-N1` and further residuals were found;
- corrections for all of those were made in `8990255`, **after** the verifiers had finished;
- **those post-verifier corrections have not been independently reverified**;
- targeted independent reverification therefore remains outstanding.

**What you must establish:**

1. **Every one of those points is stated plainly** — not implied, not buried, not hedged.
2. **The blanket claims are GONE.** Grep for any surviving assertion that every repair was
   reverified or that no agent work remains.
3. **Push status is accurate and dated.** The branch was synchronized to the private remote
   through `254db64`; work after that is to remain local. Verify the file says so, and says it as
   a **dated checkpoint fact** rather than a standing claim.
4. **No hard-coded ahead/behind count is presented as a standing fact** anywhere in the file —
   those go stale on the next commit, which is a defect this file has committed repeatedly.
5. **Counts point at the canonical derived source rather than being duplicated.** Check that
   suite counts are not restated in the file.
6. **A CONTROL, and this is the important one: read the file as a fresh instance with no context
   and write down what you would conclude the project's state is.** If what you conclude is more
   complete, more finished, or more verified than the true sequence above, the handoff is still
   overclaiming and the verdict is `FAIL`.

---

## Deliverables — write these into `<EVIDENCE>/reviewers/v5/`

`REPORT.md`, `PROBES.md`, `COVERAGE.md`, per the COMMON BRIEF. **Three separate verdicts** of
`HOLD` / `FAIL` / `UNVERIFIABLE` — one for the count, one for the rejected design, one for the
handoff. Residuals separate from failures.
