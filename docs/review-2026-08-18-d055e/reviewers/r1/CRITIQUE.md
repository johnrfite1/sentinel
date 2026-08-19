# REVIEWER 1 — CRITIQUE of the brief, the scope and the apparatus

The brief invites me to report that it is wrong. Four things.

---

## 1. My brief pointed me at the right file and told me the wrong thing to attack about it.

`r1.md` says of `check-gate-immutability.sh`: *"Can you defeat the snapshot? Can you make the
source-change detection miss? Can the harness pass while the property fails?"*

Those three questions are framed around **the original file** — they assume the snapshot is the
safe side and the source is the attack surface. The actual defect (R1-F1) is the inverse: the
source-change detection works perfectly, the harness's five properties all genuinely hold, and
the hole is that **the snapshot is not private**. "Can you defeat the snapshot?" turns out to
mean "can you *write to* the snapshot", and the answer is yes, trivially, because its path is
exported to every child and printed on the command line.

I found it despite the framing rather than because of it. A reviewer who took the three
questions literally would have spent the round mutating `scripts/test.sh` and reported 5/5
confirmed. **The brief's framing reproduces the designer's imagination, which is the thing the
common brief warns about in its own opening paragraph.**

## 2. The apparatus advertises the defect and the round did not notice.

`docs/decisions.md` A-076(e) records — as *operational documentation, explicitly deferred as
not a correctness defect* — that after the exec the process is
`bash /tmp/sentinel-gate.XXXXXXXX --gate`, and instructs reviewers to use `pkill -f
sentinel-gate`. Common brief Rule 6 carries the same instruction to all four of us.

**That instruction is the exploit.** It tells every reviewer, in writing, that the running
parser's file path is readable from `ps`. It was reviewed, discussed, corrected once for
incompleteness, argued about at the level of "does any consumer grep for the gate by name", and
carried into four briefs — and nobody asked what else knowing that path lets you do. The
project spent its attention on whether the *rename* broke a consumer and never on what the
*disclosure* enables.

This is worth recording as a process observation, not just a finding: the deferral note and the
falsified property are three lines apart in the same file, and they contradict each other.

## 3. "Prove the work fails" is in tension with the deliverables contract, and the contract should win louder than it does.

The contract is at the top of the common brief and is emphatic, and it is right. But the
incentive it creates is unstated: a reviewer optimising for "prove the work fails" will spend
its last hour on a sixth finding rather than on writing COVERAGE.md honestly. Round six's
failure was not a shortage of findings — it was seven reviewers with nothing on disk.

Concretely: **the most useful thing in my evidence directory is probably COVERAGE.md item 1**
(that I never exercised `fixtures/samples/**`, on a surface the brief says has broken in four
consecutive rounds inside the previous round's repairs), and nothing in the brief's incentive
structure rewards me for saying so. I would suggest the next round ask for the coverage
statement *first*, as a plan, and then again at the end as a result.

## 4. Scope arithmetic: R1's surface is too large to review at the depth the brief demands.

R1 owns 175 of 371 tracked files — **47% of the repository, and more than R2 and R3 individually**
(46 and 150). That includes ~4,000 lines of shell guards, a 2,358-line verifier with a
3,168-line test file, both signed gate packs, `decisions.md`, `session-state.md`, `HANDOFF.md`,
the register, the repair protocol, the round-six record, *and* Gate 7's spike and fixtures —
plus a mandatory ~50-minute deep gate run.

The brief then says "prefer depth over breadth", which for a surface this size means most of it
is guaranteed to go unexamined. I chose depth and got one Critical; the cost is documented in
COVERAGE.md and it is large. **The partition is executable and verified (that is
`check-review-scope.sh`'s real achievement) but it is not balanced**, and a partition that
assigns half the tree to one reviewer produces a coverage claim whose weakest arm is the one
nobody sized.

Note that `check-review-scope.sh` prints `R1=175 R2=46 R3=150` on every run. **The imbalance is
in the guard's own output and is not commented on anywhere.** That is a number nobody read —
which is, precisely, this project's recurring defect class, occurring in the instrument built
to prevent it.

## 5. Smaller: Rule 5's "worse than recorded" test is doing a lot of work and is not operationalised.

Rule 5 says re-reporting a recorded item is not a finding, but showing it is worse than recorded
is. R1-F1 sits exactly on that line: register §13.6 records the original defect,
A-076 records the repair, and my finding is that the repair is partial and the record asserts
completeness. I judged it a finding. But the rule gives no test for the case where the *record*
is the thing that changed — and since A-076's claim ("a private file nobody has a path to") is
the sentence I falsified, an adjudicator could equally frame this as "a documentation defect".
It is not: the exit-0 behaviour is live. Flagging the ambiguity so the adjudication is
deliberate rather than incidental.
