# BRIEF V4 — a false claim corrected where the reader is not, and a fabricated code name

Scope: **`R2-F4`** and **`R3-F4`**. Both are about what a READER encounters, not about what a
correction note says happened.

---

## Item 1 — `R2-F4`

**Original finding (MEDIUM):** a residual filed the `description` gap as *"recorded in the
register"* when the register **had no such entry**.

**Why it needed a further fix, in the author's words:** *"`R2-F4`'s correction was filed where the
reader is not, leaving the falsehood standing in two other places."*

**THIS IS THE WHOLE ASSIGNMENT: check EVERY reader-facing location where the claim appears, not
only the correction note.** A correction that exists in one document while the false sentence
stands in three others has not corrected anything — it has added a fourth document.

**What you must establish:**

1. **Enumerate mechanically every place the claim appears.** Grep the maintained tree for the
   claim and its *other spellings*. This project has been bitten specifically by a sweep that
   found four sites and missed a fifth: an entry once recorded *"a grep for the claim's other
   spellings found no fifth site"* while two remained, one of them a contract's own NatSpec
   comment. **Search code comments, Solidity NatSpec, Python docstrings, the proposal, and the
   docs — not just `docs/*.md`.**
2. **At each site, verify the false statement is removed, struck, or explicitly superseded** in a
   way a reader encountering *that site* would see. A correction elsewhere does not count.
3. **Distinguish live claims from preserved historical evidence.** Frozen reviewer and
   adjudication artifacts under `docs/review-2026-08-1*/` record what was said and must NOT be
   rewritten. State which sites you classified which way and on what basis.
4. **A control:** identify at least one place where the claim is stated CORRECTLY and confirm you
   are not flagging it. Your sweep must distinguish false-and-live from true.

---

## Item 2 — `R3-F4`

`R3-F4` is a CONFIRMED MEDIUM that John disposed of as an **ACCEPTED LIMIT**, not a repair: three
signed policy/mandate fields are consulted by nothing, and D-057(6) directs that every inert field
be named, the already-disclosed distinguished from the newly disclosed, and any implication that
an implementation consults them removed.

**Your scope is the documentation-accuracy half of it, and it is specific:**

The author invented a code name that **does not exist anywhere in the codebase** —
`EVAL_VAULT_TARGET_NOT_ALLOWED` (and its selector twin) — and it propagated into maintained
evidence documents. **The real enforcement codes are `SIGNER_`-prefixed.**

**What you must establish:**

1. **Derive the REAL enforcement code names from the code**, not from any document. Find where
   the vault's target/selector enforcement codes are actually defined and list their true names.
2. **Verify the maintained documentation now names those real `SIGNER_*` codes** everywhere it
   describes this enforcement.
3. **Confirm NO fictitious `EVAL_VAULT_*` name survives outside clearly historical quoted
   evidence.** Grep the whole tree. A surviving instance inside a preserved reviewer artifact,
   or inside an explicitly-marked historical quotation showing what the error WAS, is acceptable
   and should be reported as such — a surviving instance in live maintained prose is a `FAIL`.
   **State which category each hit falls into and why.**
4. **Sweep for the same class of defect.** The finding is "a document names a code that does not
   exist". Check the maintained evidence documents for OTHER `EVAL_*` or `SIGNER_*` code names
   that have no definition in the codebase. Enumerate the codes the code actually defines and
   diff that against the codes the documents name. **A cited code nobody can follow is a claim
   nobody can check.**
5. **A control:** confirm your method does not flag legitimately-named real codes, and that it
   would have caught the original `EVAL_VAULT_TARGET_NOT_ALLOWED` had it still been present —
   demonstrate that by reintroducing it in your worktree and showing your sweep finds it.

---

## Deliverables — write these into `<EVIDENCE>/reviewers/v4/`

`REPORT.md`, `PROBES.md`, `COVERAGE.md`, per the COMMON BRIEF. Separate verdicts of
`HOLD` / `FAIL` / `UNVERIFIABLE` for `R2-F4` and for `R3-F4`. Residuals separate from failures.
