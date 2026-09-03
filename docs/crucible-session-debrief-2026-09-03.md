# Session debrief — `S-20260830-sentinel-conformance-lab-r1`

**From the Smith**, in answer to the orchestrator's closing request. Drafted by the build team's
coordinating agent from the ledger (MSG-001 to MSG-043) and the build team's own register; the Smith
edits and sends. Written to be filed verbatim.

## 1. What worked

**Withdrawal conditions written as predicates.** Every sustained Critical carried a condition a machine
could check, and every one was closed by measurement and reproduced independently by the chairs — the
override-in-a-PASS at Cycle 2, the fail-open clock at Cycle 2, the first-surface route at Cycle 3. The
rule that the owning chair judges its own condition made "closed" unambiguous.

**Test-first separation held under pressure.** Four times — the Cycle 2 batch, D-090(a), D-091(a),
D-092(c) — an independent author wrote a red suite against a frozen baseline before any implementer
touched the code, implementers refused to edit frozen contracts when a test blocked them, and a third
agent checked vacuity empirically (10 of 14, 18 of 26 new tests red against the old code). No test that
claimed to observe a new contract passed against the old one.

**Fresh-context verification found what the build loop could not.** Every cycle, an agent with no
build context walking every mention of the changed tool found surfaces the lane had missed: the
shipped docstring printing under `--help`, the release-tree README paragraph, the enforcement document's
consequences table, a second clock read on the PASS path. The chairs did the same to the build team:
Conscience proved the previous README's commands did not run and that the Cycle 3 lane had made the
route to PASS on a BLOCK copy-pasteable for the first time. Re-measuring rather than reading, as the
build team's own brief asked, is what caught it.

**The bounded exception.** The cap of two cycles plus one written-note extension (D-090(c)) cost a day
and returned zero sustained Criticals. The exception was narrow, recorded before the prompt, and did
not become a loop.

**The cold read as a Quench instrument.** Three files, three minutes, a locked book, a frozen
questionnaire delivered only after the read — and it produced usable evidence in both directions: the
identity distinction and the economic boundaries retained; the density of the record named as the cost.
"A mixture, weighted toward rigor" was the honest reading and the Smith could accept it with a stated
risk rather than pretend to a verified one.

**The ledger and the artifact never disagreed.** Every Smith decision was written in the artifact's own
decision log, filed verbatim, and checked byte-for-byte. The build team's return notes mapped each
finding to a disposition and asked for nothing.

## 2. What failed or leaked

**On the build team's side, in order of cost.**

- The Cycle 3 README lane turned two non-runnable packet commands into a fenced, runnable route to
  `=> PASS` / exit 0 on a BLOCK receipt. Its brief said every claim must map to output it ran; it did not
  say what must *not* be runnable, and the coordinator did not read the Historical section after the lane
  returned. Three Critical alarms.
- The candidate's status documents were re-pointed in the commit *after* the candidate, so the file the
  README calls authoritative contradicted the tool the README told the reader to run. Now a rule: a
  candidate's status documents land in its own commit, named by parent and subject.
- A contract change was declared landed while four surfaces still described the old contract, twice.
  A change is not landed until a fresh agent has walked every mention.
- Earlier in the line: a documentation claim written before its code existed and left standing by a
  rate-limit kill; four measured numbers supplied at moments of decision that were wrong. All in the
  register.

**On the protocol's side.**

- The orchestrator pre-filled a Quench item — a drafted recommendation on the acceptance criteria with
  "do you accept this ruling as drafted?" — which the runbook forbids. The Smith restated it as his own
  ruling with corrections, and the corrections mattered: the draft waived three AC2 clauses that hold.
- The 3–1 split on the carried withdrawal condition was resolved by routing, not by ruling. The owner
  said HOLDS; three chairs said FAILS on one line; the routing contract counted only the owner. The
  outcome was right because the Smith chose a patch anyway, but nothing in the protocol asked him to.
- The §5 `From` enum has no seat for the build team. Three artifacts were filed outside it.
- The raw `staging/` archive is absent and cannot be reconstructed, by the orchestrator's own report.
- The workspace guard was red on 228 unbaselined findings for the whole session. A guard that is always
  red is a guard nobody reads; the build team learned the same lesson in another form when a guard that
  compared but never executed passed a verifier that could not import.
- Transport: three of four Cycle 3 chairs needed retransmission; one return carries a visibly truncated
  final word.
- The named-audience test was one model proxy, not a human. Recorded as such in every acceptance.

## 3. The one change to the Crucible

**When the owning chair withdraws a carried Critical and any other chair reports the same withdrawal
condition as failing, route the split to the Smith as a named decision before the Anvil disposition.**
Not a Cycle, not an override — a single ruling: which reading of the condition governs, on what
evidence. Today that split falls silently to the owner and the dissents become advisory findings. This
session got the right answer by the Smith's choice; the protocol should ask the question instead of
relying on him to volunteer it.

If a second change were allowed: a `BUILD TEAM` value in the §5 `From` enum, so the respondent to a
halted line has a channel that is not a workaround.

---

*The Temper is owed at the first external evaluator engagement. Publication, visibility and the licence
remain undecided; the artifact is SHIPPED PRIVATE.*
