# The repair protocol — required for every repair (D-052(b))

**Ruled by John, 2026-08-18, D-052(b): repairs must be tested against SIBLING PATHS and the
UNDERLYING ARGUMENT.** This file is the operative form of that ruling. It binds every repair
made from here on, including repairs to repairs.

**This is not a style guide. It exists because four of the last five repairs were defeated by
the same failure mode within 48 hours of being made**, each by an independent reviewer, and
each repair had been falsified by its author first. Falsifying a repair against the defect its
reviewer demonstrated is what all four did, and it is exactly what did not work.

---

## The evidence this is derived from

| Repair | Defeated by | The shape |
|---|---|---|
| **A-063** — §7.1 containment correction, certified by John | Round 6 lens 4 | Corrected four sites and recorded "a grep for the claim's other spellings found no fifth site". Two remained — `SentinelVault.sol:12-16` (the vault's own NatSpec) and `§4:238`, which the original finding had named **by line number**. The grep missed it because it says "hard constraints", not "hard caps". |
| **A-066** — socket-path fallback | Round 6 lens 7 | Fixed the construction in `corpus/run.ts`. The identical construction is in `tools/sample-check.ts` and `tools/emit-samples.ts`; both still die `connect EINVAL`. |
| **A-068** — `C-3` | Round 6 lenses 7, 9 | Pinned the pure function `internalCalls()`. Its **input** (the tracer name) and its **output** (the mapping into `SimulationResult`) both remained deletable with a green suite. |
| **A-068** — `D-06` | Round 6 lenses 3, 9 | The finding named five comparisons; the repair pinned four. The test comment calls itself "that generalisation". |
| **A-069** — `E4` | Round 6 lenses 2, 6, 7 | Built checks for the two fields the finding named, gated on `isinstance(..., dict)`, so **absence emits no check at all**. The third field — the one D-014's justification rests on — was not covered. |

The common factor: **each repair generalised the DEMONSTRATION and not the ARGUMENT.**

---

## The protocol — six steps, all required

### 1. Write the ARGUMENT before writing the code

One sentence, in the decision entry, stating the **general property** the repair establishes —
not the input that broke. If you cannot state it without naming the reviewer's specific probe,
you do not yet understand the defect.

- Demonstration: *"a `.` in a filename matches a different pin entry."*
- Argument: *"the manifest lookup must be exact-string, so no filename can match an entry that
  is not its own."*

### 2. Enumerate sibling paths — mechanically, and record the list

Before the repair is called done, produce and record:

- every other call site of the repaired function or construction (`grep`, not memory);
- every other spelling of a corrected claim — **search the meaning, not the wording**, because
  A-063's grep for "hard caps" missed "hard constraints" in a sentence the finding had cited;
- for a repaired check: **every code path it does NOT run on.** A-069's checks are absent from
  the refusal path entirely; nobody looked.

**Record the list even when it is empty.** "I checked and there are no siblings" is a claim,
and it is checkable. "No siblings were mentioned" is not.

### 3. Falsify against the ARGUMENT, by a different route than the demonstration

The regression test must fail against a mutation that violates the general property **via a
route the reviewer did not use**. A test that only fails against the reviewer's own probe
measures the reviewer's imagination, which is A-046's lesson restated one layer up.

Falsifying against the demonstration as well is fine. It is not sufficient and never was.

### 4. Prove the ABSENCE case fails rather than skips

If the repair adds a check gated on a field's presence, type, or shape, you must show that the
**absent** and **wrong-type** cases FAIL and do not silently emit nothing.

A-067 stated this exactly — *"ABSENCE IS NOT AGREEMENT… A hash commits to a document. With no
document there is nothing to certify, so this FAILS"* — and A-069, written the next day,
shipped the opposite. A skipped check whose absence produces no output line is worse than no
check, because the run still prints as clean.

### 5. Falsify through every invocation shape

If the artifact has more than one entry point, falsify through each. The trust-root repair
closed the single-bundle path and left `--all` certifying the identical hostile tree; it was
caught only by re-running the exploit through both shapes.

### 6. Record what the repair does NOT reach

State the residual in the decision entry, in the §11 "what is NOT in evidence" discipline
already used for gate packs. A repair with no stated residual is asserting completeness, and
that assertion has been wrong four times running.

---

## What this does not permit

- **A partial repair is allowed; an unstated partial repair is not.** A-068's `D-06` fix
  pinning four of five boundaries would have been fine had it said so. It said "all five" and
  called itself a generalisation.
- **Do not widen scope to satisfy the protocol.** If the sibling sweep surfaces work beyond the
  repair's scope, record it in `docs/v1-1-register.md` and raise it — do not silently absorb it.
  Scope additions go through John (house rule 7).
- **Never weaken a mechanical guard to make a repair pass** (house rule 5).

---

## Status of the mechanical half

**This protocol is currently prose, and prose is what this project has repeatedly found
insufficient.** `check-label-prompt.sh`'s own header states the standard: *"a durable project
rule gets a mechanical guard rather than prose."*

By that standard this file is incomplete, and it is recorded as incomplete rather than
presented as done. What a mechanical half would look like — a gate stage asserting that every
new decision entry claiming a repair carries a recorded sibling list and a stated residual — is
**not built, not scoped, and is John's to rule on.** It is listed in `docs/v1-1-register.md`.

**Reversal condition, from D-052(b)(a):** if remediation performed under this protocol still
produces defects at the rate the last five repairs did, the protocol has not worked and it
returns to John rather than being iterated by an agent.
