# Quench — third handoff to the orchestrator: the acceptance-criteria item

**From the Smith.** Session `S-20260830-sentinel-conformance-lab-r1`, Step 6, in reply to the orchestrator's
drafted recommendation on the acceptance-criteria item. The Quench artifact is unchanged:
`8dfaa275a669bd202c3fa45e36dc12cbbe261170` (A-033).

## The Smith's ruling, to send in his own words

> AC1, AC3, AC4, AC5, AC6, AC7 and AC10: met. AC8: met on its entry-point half; the summarising half is
> owed under D-093(c), not met. AC9: struck; licence deferred. AC2: clauses 2–4 met — BLOCK and
> un-overridden REVIEW fail closed on both verifiers, no certifying result takes a caller-chosen clock,
> nonce freshness is declared not established rather than asserted. Clause 1, one unified executable
> predicate, is consciously waived for A-033: the artifact intentionally separates authenticity, offline
> certification and live execution (D-087(c); Assumption 2 amended at D-094(a)). Residual risk: no shared
> conformance corpus covers all three implementations; parity rests on the 39-cell matrix, three cycles of
> chair reproduction and the exit-contract tests; unification remains deferred. This completes the
> acceptance-criteria item only and authorises no publication.

## The Smith Decision to file (D-095, verbatim from `docs/decisions.md`)

- **D-095 (2026-09-03) — THE QUENCH'S ACCEPTANCE-CRITERIA ITEM: AC1, AC3–AC7 AND AC10 MET; AC8 MET ON ITS ENTRY-POINT HALF WITH THE SUMMARISING HALF OWED; AC9 STRUCK, LICENCE DEFERRED; AC2 CLAUSES 2–4 MET AND CLAUSE 1 CONSCIOUSLY WAIVED FOR A-033. Ruled by John, 2026-09-03, on the orchestrator's drafted recommendation, restated as the Smith's own ruling with two corrections the agent proposed. The agent RECORDS this and makes none of it.**

**MET, on measured evidence.** **AC1** — `README.md:1` states a testnet lab, not a production wallet or deployment (Adversary, Cycle 3). **AC3** — both shipped verifier modules carry direct adversarial coverage; reproduced by the chairs at Cycle 2 and not contradicted since. **AC4** — no usable fixture key detected by the stated checks, every lab authority labelled `NOT PRODUCTION, NOT A TRUST ROOT`, absence stated as check results (D-084). **AC5** — one unaided named-audience read (MSG-041) showed the identity distinction, what a PASS establishes and does not, and what real value would require; on a model proxy, with the risk stated at D-093. **AC6** — every un-struck headline claim in the README, the release document, the release README and both verifiers' success strings was run and matched by the Cycle 3 patch's independent verifier. **AC7** — the per-action ceiling, the single-transaction drain and the pause gap are on the first surface and were retained by the cold reader. **AC10** — audience named, venue recorded (D-083(a)), artifact shaped for it.

**AC8 — MET ON ONE HALF, THE OTHER OWED.** The entry point is stated and was found. The decision material is *signposted* by the archive map; it is not yet *summarised*, and the cold reader named its density as a confidence cost. The summarising half is the work owed under D-093(c) — an archive index and a pruning pass over superseded passages — and is recorded here as owed, not met.

**AC9 — STRUCK; LICENCE DEFERRED (D-082(c)).**

**AC2 — CLAUSES 2–4 MET; CLAUSE 1 CONSCIOUSLY WAIVED FOR A-033.** AC2 has four clauses. Met on this artifact: BLOCK and un-overridden REVIEW fail closed on both verifiers (D-083(c), D-090(a)); no certifying result takes a caller-chosen clock (D-086(e), D-092(c)); nonce state is declared not established by the publication verifier's `NOT ESTABLISHED` line rather than asserted. **Unmet and waived:** "one versioned executable predicate" — the artifact intentionally separates authenticity, offline certification and live execution (D-087(c)), and Assumption 2 was amended to say so (D-094(a)). **Residual risk, stated:** no shared conformance corpus covers all three implementations; parity rests on the 39-cell matrix, the chairs' reproductions across three cycles, and the exit-contract tests; unification remains deferred. **Rejected — waive AC2 whole** (waives three clauses that hold); **decline the waiver and hold** (the Quench could not complete on this artifact).

**KILL CRITERION 1, NOTED.** "The verifier can certify any receipt SentinelVault would refuse." The current verifiers cannot. The frozen v0.2 packet's verifier, from its own directory, still prints a bare PASS on a BLOCK; that residue is disclosed and ruled at D-091(c), D-092(a)–(b) and D-094(c), and is not a certification by the artifact's verifier.

**WHAT THIS ENTRY DOES NOT DO.** It completes one Quench checklist item. It authorises no publication, deployment, push or visibility change; the repository remains PRIVATE; **the licence remains DEFERRED under D-082(c).** The orchestrator's draft was a pre-fill the runbook does not permit it to solicit; the Smith answered in his own ruling.

## Not decided here

The remaining Quench items — no unresolved Criticals; a surviving pre-mortem; the one-line decision note —
and the Temper trigger are answered by the Smith directly. Publication, deployment, push, visibility and
licence are separate rulings and are not taken; the repository remains PRIVATE and the licence DEFERRED.
