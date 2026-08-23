# Gate 5 / `V3-N2` — prepared admissibility material

**Ruled 2026-08-23 at D-067.** This file remains prepared material; the ruling lives in
`docs/decisions.md`. It does not recertify Gate 5.

This file is prepared material. Nothing in it is a finding of record.
It writes into no other file. It does not revoke, reaffirm, or recertify the Gate 5
certification — D-059(1)'s own three verbs. It does not rule D-059(1)'s bar met. It does not
write a recommended verdict.

**Standing state of record after D-067:** the Gate 5 certification is untouched (none of
D-059(1)'s three verbs). The supplementary §7.2 condition's evidence bar is MET; `R2` and
`V-6` are named completeness limits on D-008(2)/(4) only. The argument below is the prepared
material that session used; it is not a recertification.

---

## Standing state of record

D-059(1), 2026-08-19, John's ruling:

- The underlying Gate 5 certification **stands** (Option A). `V3-N2` did not falsify
  D-008(1)–(4), and the guarded §7.2 property was independently measured true at that commit.
- **And the part that binds an agent:** `scripts/check-vendor-honesty.sh` **is not admissible
  as evidence** for its supplementary §7.2 condition **until repaired and independently
  reverified.**
- A guard may be broken while the property it guards is true; the property's truth does not
  restore the guard's standing as evidence.
- `V3-N2` is therefore repaired **without** the certification being revoked, reaffirmed, or
  recertified — none of the three, and an agent does none of them as part of the repair.

The signed-text half is separate and is not an agent's (D-059(1b)).

---

## What was later done to the guard, and by whom

| When | Who | What |
|---|---|---|
| A-088 (2026-08-21) | administrative checkpoint under D-066 | Authorised attempt one against the frozen A-EXTRACT contract. One of the five authorised surfaces was a repair of `scripts/check-vendor-honesty.sh`. |
| Attempt one `088f745` | implementer | Changed exactly A-088's five surfaces. The independent later record (A-089) says the sole miss was `10c`: the vendor logical-paragraph normalizer concatenated a deeper ATX heading with the following caveat paragraph. |
| Attempt two `39c7679` | implementer | One line in `scripts/check-vendor-honesty.sh`: ATX headings became paragraph boundaries without changing section extent. |
| A-089 (2026-08-21) | record of work | A verifier who authored neither implementation nor contract returned **HOLD** for that exact candidate in review-only commit `a8921a1`. The isolated clean-clone deep gate directly executed each A-EXTRACT consumer once, including the vendor-honesty banner, and ended `GATE PASSED`. |

The A-EXTRACT contract's vendor-honesty slice is heading-depth-aware §7.2 extent and the
caveat comparison, plus the §2 pinned-table control. Completeness is claimed only inside that
boundary (A-089). A-089 states it does not recertify a gate.

This stretch did not re-run the frozen A-EXTRACT vendor-honesty cases and did not re-run a
deep gate. What it did run is named below under `R2`.

---

## The argument that the bar's two conjuncts now have a measured basis

Stated as strongly as the material supports, not as a conclusion.

1. **Repaired.** D-059(1) named `V3-N2`: the guard certified §7.2 while grepping the whole
   document. The frozen A-EXTRACT instrument required heading-depth-aware extent so a deeper
   heading does not end §7.2 and a same-depth heading does; an absent or duplicate heading is
   refused; a fenced mention is not the section. Attempt two's one-line ATX-boundary change is
   the recorded product delta that closed the last REQUIRED miss (`10c`). A-089 records
   52/52 REQUIRED and 70/70 CONTROL at that candidate, with execution witnesses bound to it.
2. **Independently reverified.** A different agent, who authored neither the implementation
   nor the contract, returned HOLD at the exact candidate (A-089, review-only `a8921a1`). That
   is the independent-verification shape D-058 uses elsewhere. The isolated `--gate` run
   observed the vendor-honesty stage banner, which is the deep-profile invocation A-EXTRACT's
   own GATE-BINDING.md had left outstanding at instrument time.
3. **The property's truth is not being asked to do the work.** D-059(1) already held that the
   §7.2 caveat was independently measured present. The bar was about the *guard's* standing,
   and the later work was aimed at the guard, not at re-proving the sentence.

On this reading, a ruler who takes "repaired and independently reverified" to mean "the
named `V3-N2` extraction defect was repaired against a frozen contract and a different agent
held that contract at the exact candidate" has a measured basis for treating those two
conjuncts as done **for `V3-N2`**.

---

## The counter-argument, including `R2` as a load-bearing fact rather than a footnote

Stated as strongly as the argument above.

1. **D-059(1) is about the guard as evidence for Gate 5's supplementary §7.2 condition, not
   about A-EXTRACT's batch boundary.** A-089's HOLD is explicitly scoped to section
   extraction, exact-membership, source-uniqueness, and vendor-caveat. It says it does not
   recertify a gate. Equating that HOLD with restoring `check-vendor-honesty.sh` as Gate 5
   evidence is a jump the record does not make. D-059(1) forbids an agent from making it.
2. **`R2` is an unrepaired defect in this same script.** It is not a findings-ledger row.
   The independent A1 verifier recorded it in
   `docs/review-2026-08-19-d057-targeted/batch-cards/A1-tests/VERIFICATION.md`:
   `artifacts()` enumerates `{ git ls-files ; git ls-files --others --exclude-standard }`
   without `-z`, so under default `core.quotePath` a non-ASCII name is octal-escaped and
   `[ -f "$f" ]` is false — the path is never scanned. D-061(2) deferred it. D-062 did not
   reach it. It has never been adjudicated into `NEW-FINDINGS.tsv`.
3. **This stretch reproduced `R2` read-only**, in a disposable clone of
   `8d8820c03043844b3281d35d81578890eee1ecdf` (the V-1 instrument-HOLD commit; the script
   body was not part of the V-1 candidate). Default `core.quotePath` unset. Two untracked
   markdown files, identical except one byte in the name:
   - `git ls-files --others --exclude-standard` emitted the ASCII name unquoted and the
     non-ASCII name C-quoted / octal-escaped.
   - The same listing with `-z` emitted both names unquoted.
   - Simulating `artifacts()`'s `[ -f "$f" ]` filter: ASCII **KEPT**, quoted non-ASCII
     **DROPPED**.
   Live `scripts/check-vendor-honesty.sh` still has the un-`-z` `artifacts()` block
   (lines 198–208 as of that commit). Naming this is not carding it and is not a repair.
4. **A packet that argues a guard's evidentiary standing while omitting a live unrepaired
   defect in that guard is the shape of argument this project exists to catch.** `R2` sits
   on the same `artifacts()` enumerator every vendor-honesty file-walk uses, including the
   §7.2 comparison's report-side walk. Whether that enumerator can drop a non-ASCII path
   is a fact about the guard's completeness as evidence, not a footnote about a different
   batch.
5. **The deep-profile half of D-059(7) was itself historically overstated.** A-087's heading
   said D-059(7) was discharged; A-EXTRACT `RESULTS.md` §7 and `GATE-BINDING.md` STATUS
   recorded fast-profile binding as measured and `--gate` as not run. A-089 later ran an
   isolated deep gate and observed the consumers. Those are different moments. They do not
   convert A-089's batch HOLD into a Gate 5 evidentiary restoration.
6. **What is not established here:** that `R2` currently causes the §7.2 caveat comparison
   to pass over an unscanned report (no such planted report was used); that A-EXTRACT's
   vendor-honesty REQUIRED cases would still hold if `artifacts()` dropped a file; that any
   later commit after `39c7679` re-broke the ATX-boundary repair. This stretch did not
   re-run those cases.

On this reading, a ruler who takes D-059(1)'s bar to mean "the *guard* is admissible as
Gate 5 evidence only when it is not carrying a live fail-open in the enumerator it uses
to decide what it scanned" has a measured basis for leaving inadmissibility in place.

---

## What would change the standing state

John's ruling. The two conjuncts in D-059(1) are his to declare met or not. An agent may
not revoke, reaffirm, or recertify Gate 5 in the course of presenting this material.
`R2`, `R3`, and `R5` stay deferred and unresolved unless he directs otherwise.
