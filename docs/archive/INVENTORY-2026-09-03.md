# Archive inventory — 2026-09-03

**This file changes nothing. It is the measured contract for the D-093(c) archive index and
pruning pass.** Measured on branch `step-3/isolated-signer` at HEAD `e73789d` (working tree clean
apart from an untracked `.claude/`). Every line number below was read from the files at that
commit; a line number is a pointer into that revision and nothing else. Nothing here is a ruling.
Where a choice would change what a live document says, it is listed under §8 as a fork for John.

The mandate this inventory serves, quoted from `docs/decisions.md` D-093 (line 523): *"Mitigant
committed post-Quench: an archive index and a pruning pass over superseded passages, changing no
mechanism." The commitment is work owed, not done.* The cold reader's cost (MSG-041) was "dense,
repetitive governance history", "numerous superseded passages", and a root README that "became
long and historically crowded". Nothing is deleted; `docs/decisions.md` does not change; no
mechanism, test, release file or the frozen packet is touched.

Three measured constraints govern every move (details in §6):

1. `scripts/check-suite-floors.sh` is **run by the gate** (`scripts/test.sh:304`) and opens
   `docs/session-state.md` by path (`check-suite-floors.sh:41`). The file must keep that name and
   must never again contain the two strings the script refuses (lines 178 and 181 of the script).
2. `scripts/check-vendor-honesty.sh` is run by the gate (`scripts/test.sh:301`) and scans every
   tracked or untracked-not-ignored text file **except** an exact-filename exclusion list
   (`check-vendor-honesty.sh:149`) that names `HANDOFF.md` and `docs/session-state.md` and would
   not cover `docs/archive/*` or `docs/ARCHIVE-INDEX.md`. `docs/session-state.md:637` names a
   vendor inside a HISTORICAL block. Moving that block verbatim into a new file fails the gate.
3. `scripts/assemble-reviewer-packet.py:220` cuts the root README at the literal heading
   `## In this repository`; that heading text is load-bearing. The packet copy it produces is
   frozen (D-091(c), D-092(b): "no packet byte moves") and the assembler is not run by the gate.

---

## 1. `docs/session-state.md` — block map (1025 lines)

Legend: **CURRENT** = true today and needed by a reader arriving now. **HISTORICAL** = a
superseded instruction, a struck sentence, a dated block about a state that has since changed,
or a corrected claim kept for the record. **DURABLE** = a method lesson or environment fact that
is neither dated status nor superseded; D-093(c)'s "superseded passages" does not reach it.

| # | Lines | Date | Class | What it is / what it recorded |
|---|---|---|---|---|
| 1 | 1–4 | — | CURRENT | Title; "this file, not the conversation, is the memory". |
| 2 | 6–9 | 2026-09-03 | CURRENT | Last-updated line: Quench on `8dfaa27` answered, D-093–D-096. **Stale detail inside it:** line 8 names two handoffs (`-handoff.md`, `-2.md`); four exist (`-3.md` D-095, `-4.md` D-096). |
| 3 | 10–11 | 2026-09-02 | HISTORICAL | Struck last-updated: Cycle 3 returned, D-092 patch landed. |
| 4 | 12–13 | 2026-09-02 | HISTORICAL | Struck last-updated: `81edee1` pushed as backup (D-091(d)). |
| 5 | 14–16 | 2026-09-01 | HISTORICAL | Struck last-updated: Cycle 2 candidate in build (D-087); BLOCK→PASS fixed at `8d47a0b`. |
| 6 | 17–20 | 2026-08-29 | HISTORICAL | Struck last-updated: D-081 checkpoint; "left visible because four commits and three rulings landed under that date line". |
| 7 | 21–23 | — | CURRENT | D-055 MET (D-073) unlocks nothing; name "Sentinel" (D-074); domain string "Sentinel" (D-075); branch. |
| 8 | 24–26 | 2026-08-25 | HISTORICAL | "WORKING TREE AT THE START OF THIS STRETCH: clean at the A-109 freeze" — A-109 is the 2026-08-25 freeze; the tree has moved 20+ commits since. Lines 25–26 (count unpushed; no push authorised) are live but duplicated at 198–203. |
| 9 | 28–47 | 2026-08-25 | HISTORICAL (framing) | "READ THIS BEFORE ANYTHING ELSE", first paragraph: the Gate 8 / D-077–D-080 / A1-closed state, "the Icon line is kept". Its prohibitions survive as live facts (§1.1 below); the framing is the 2026-08-25 state. |
| 10 | 49–57 | 2026-09-01 | HISTORICAL | "CURRENT NARROW INSTRUCTION (D-087)": build one ~35-item Cycle 2 candidate. **Spent** — that candidate is `cb124fe` (line 141). |
| 11 | 59–73 | 2026-08-29 | HISTORICAL | Struck NARROW INSTRUCTION (D-081), "spent at `a38cff9`"; what the D-081 candidate contained; the v0.2 corpus refusal (A-111). |
| 12 | 75–91 | 2026-09-01 | HISTORICAL | Repair batch landed (`8d47a0b`, `5d93850`, `5c8c090`, `2318ae3`); D-085/D-086/D-087 recorded; the inventory-diff figure (54 + 4 + 4); "two Crucible lines, do not conflate them". |
| 13 | 93–110 | 2026-09-02 | HISTORICAL | Cycle 3 returned with zero sustained Criticals on `81edee1`; D-092's narrow patch (a)–(g); "patch LANDED in this commit … names no SHA" (that commit is `8dfaa27`, now the Quench artifact). |
| 14 | 112–122 | 2026-09-02 | HISTORICAL | Final Cycle 3 candidate `81edee1`, pushed as backup; D-091 forks ruled; struck "next external event". |
| 15 | 124–139 | 2026-09-02 | HISTORICAL | First Cycle 3 candidate `0bc79a8`; D-090 route (a); README rewrite; the D-092 Conscience Major 3 correction in place. |
| 16 | 141–147 | 2026-09-02 | HISTORICAL | Cycle 2 candidate `cb124fe`; D-088 exemption; pushed under D-089. |
| 17 | 149–159 | 2026-08-30 | HISTORICAL | "THE CRUCIBLE LINE IS HALTED": the four A-018/MSG-022 Criticals OPEN AT ANVIL; the register proposed; corrected 2026-09-01 (§3 items authorised piecemeal). Carries live fact §1.1-F7. |
| 18 | 161–168 | 2026-08-30 | HISTORICAL | Struck BLOCK→PASS defect (fixed `8d47a0b`); "`a38cff9` IS NOT PUSHED … origin at `70f4b4d`" — itself stale (origin is at `28b82a4` today). |
| 19 | 170–177 | 2026-08-30 | HISTORICAL | Struck scope fork → RULED D-083(a),(g): custody retained with the drain disclosed; audience technical evaluators; venue GitHub public, visibility unchanged; fresh casting `S-20260830-sentinel-conformance-lab-r1`. Carries live facts §1.1-F5/F9. |
| 20 | 179–185 | 2026-08-20 | HISTORICAL | `GIT_INDEX_FILE` fail-open fixed at `4920213` (D-062), verified `c163195`. |
| 21 | 187–196 | 2026-08-24 | HISTORICAL | `V-1` retired under D-073; the scrub-before-`rev-parse` ordering. One standing engineering constraint inside it (guarded by `scripts/check-v1-index-ordering.sh`, gate-run at `test.sh:264`). |
| 22 | 198–203 | — | CURRENT | Count unpushed with `git log origin/…..HEAD`; repository PRIVATE; publication not authorised; push only on John's explicit direction for a specific state. |
| 23 | 205–236 | 2026-08-25 | HISTORICAL | "READING ORDER FOR A FRESH INSTANCE" — routes a newcomer through D-058…D-064, the batch cards, D-066…A-111. This is the passage the index replaces. |
| 24 | 238–241 | — | CURRENT | "DO NOT QUOTE COUNTS FROM THIS FILE"; where the floors, findings and verdicts are derived. |
| 25 | 244–258 | — | CURRENT | §0 opening: S1 signed 2026-07-28, S2 signed 2026-08-16 (D-041); what S2 does not authorise; Gate 8 passed with three limits (D-080); §11's limits; six accepted limits. |
| 26 | 260–269 | 2026-08-16/19 | HISTORICAL | The steps 1–3 review (A-043 CRITICAL); "§11 is NOT empty" (`B-7`); §11.0 count corrections (A-080). |
| 27 | 271–332 | 2026-08-18/20 | DURABLE | "THE PATTERN" — the honesty-defect list a reviewer brief has to encode (13 bullets, dated additions 2026-08-18 and 2026-08-20). |
| 28 | 334–340 | 2026-08-19 | HISTORICAL | "WHERE THE PROJECT STANDS, 2026-08-19": round five adjudicated; D-051(a)/D-053(a)/D-054. |
| 29 | 342–346 | 2026-08-18 | HISTORICAL | Round six 91 findings, not clean (D-052(a)); D-055(a) replaced D-047 (D-085 later retired D-047 outright). |
| 30 | 348–355 | 2026-08-18 | HISTORICAL | A-075: D-055(d)'s four prerequisites; register §13.4 corrected; ten → six accepted limits; A-076. |
| 31 | 357–361 | 2026-08-18 | HISTORICAL | D-055(e) ran: four reviewers, scope fixed by John (D-056(d)). |
| 32 | 363–368 | 2026-08-19 | HISTORICAL | 23 findings, `R1-F1` CRITICAL in the gate; D-057; condition four NOT MET; A-077/A-078. |
| 33 | 370–373 | 2026-08-19 | HISTORICAL | A-078: 3 REPAIR-FAILS, "generalised the DEMONSTRATION and not the ARGUMENT". |
| 34 | 375–378 | 2026-08-19 | HISTORICAL | The certification gate protected (D-057(3)) — standing constraint lives in `scripts/check-gate-immutability.sh` (gate-run, `test.sh:216`). |
| 35 | 380–383 | — | CURRENT | Design forks delegated; gate signing and public-claim certification stay outside, autonomy none. |
| 36 | 387–394 | — | CURRENT | §1 "YOUR JOB: NOTHING, WITHOUT AN INSTRUCTION FROM JOHN". Heading is a link target (HANDOFF lines 82, 116, 134, 146, 176, 195, 208; README line 307). Stale hedges inside: "D-058 confirmed batches HOLD"; "packet is not name-agnostic". |
| 37 | 396–410 | 2026-09-01→03 | CURRENT | ADDENDUM table — the live status rows (listed at §1.1-F13). Measured defect: the "D-092 patch" row (line 408) repeats its own sentence ("child of `02458d2`, subject `D-092 patch …`" twice). |
| 38 | 412–428 | 2026-08-29 | HISTORICAL | "WHERE THE PROJECT IS, 2026-08-29" table: gates, review arc, remediation, A1, D-058 batches, D-055 exit, Phase B, Sessions Eight/Nine/Eleven. |
| 39 | 430–448 | 2026-08-20 | HISTORICAL | "HOW BATCH A1 ACTUALLY CLOSED": `63c6906`/`f61ecca` FAILED; D-062 exception; `c73b17a`/`4920213`/`c163195`; D-064. |
| 40 | 450–462 | 2026-08-22 | HISTORICAL | What the five D-058 batches closed (A-089, A-091, A-093, A-094, A-095). |
| 41 | 464–491 | 2026-08-25 | HISTORICAL | "WHAT IS STILL OPEN" (D-062 residuals V-1…V-10, R2/R3/R5, Gate 5 §7.2, deferred items). Item 1's prohibition is live, duplicated at 198–203. |
| 42 | 493–513 | 2026-08-25 | HISTORICAL | "WHAT IS WAITING ON JOHN": four struck/closed items; item 5 duplicates block 22. |
| 43 | 515–534 | 2026-08-25 | HISTORICAL | "WHAT IS NOT AUTHORISED": A1 reopening clauses (spent lifts), D-016-era wording; the live prohibitions are in block 22. |
| 44 | 536–551 | 2026-08-19 | DURABLE | The method that governs remediation: batch cards (D-060(1)), test-first (D-058(1)). D-085(e) added the inventory-diff method for review; not stated here. |
| 45 | 554–564 | — | CURRENT | §2 Authority: agents propose, John decides; the five D-008 questions stay unseen; the one-fork-at-a-time session pattern. |
| 46 | 566–569 | — | CURRENT | §3 heading; "DO NOT READ A SUITE COUNT FROM THIS FILE". |
| 47 | 571–612 | 2026-08-16→18 | HISTORICAL | The staleness chronicle: five corrected-count notes (507/198 vs 513/209; 75/507 vs 89/526; 160→170; 149/149; 66/66). |
| 48 | 614–615 | — | CURRENT | Run `./scripts/test.sh`; `--gate` for evidence; read the coverage boundary. |
| 49 | 617–623 | 2026-08-16 | HISTORICAL | Four counts re-measured; the verifier had no gate stage (A-045). |
| 50 | 625–650 | 2026-08-16/17 | HISTORICAL | A-046 "8/8" worthless; A-047 seven defeats; A-049 `evidence-hash` mode; A-051 sweep (41 survivors). **Line 637 names a vendor** (the case-sensitivity example) — see §6 constraint 2. |
| 51 | 652–662 | 2026-08-17 | HISTORICAL | A-048 broke A-047's headline; skipped-test floor; `expiryAfter`/`expiryBefore`; the D-045 misdescription corrected. |
| 52 | 664–674 | 2026-08-16/18 | HISTORICAL (stale) | "TEN mechanical stages guard the gate" + "two of the eight pass on something weaker". Measured today: `scripts/test.sh` invokes **17** `check-*.sh` scripts (lines 216–531). |
| 53 | 676–705 | 2026-08-16/17 | HISTORICAL | Bullets: §9 steps done; ablation 38/8/1 (guarded separately by `test.sh:882` diff against `docs/ablation-report.md`); D-010 verifier count corrections; Gate 7 canary monthly (D-036); labellers E/F of record. |
| 54 | 707–773 | 2026-08-15/16 | HISTORICAL | §4 index table of D-033…D-051 and A-029…A-069 (61 rows). An index into `docs/decisions.md`, superseded by the archive index. |
| 55 | 775–925 | 2026-08-15→18 | DURABLE | §5 Traces: dead ends (25 bullets) and what worked (11 bullets). |
| 56 | 927–952 | — | CURRENT / DURABLE | §6 Environment facts (concurrent sessions, Foundry path, Node, `.env`, model parameters, `contracts/out` after mutation, harness-injected memory). |
| 57 | 956–959 | — | CURRENT | §7 `scripts/mutate.sh` usage; "get counts by running it". |
| 58 | 961–970 | 2026-08-16 | HISTORICAL | Latest measured mutation counts (C 14/14, S 31/31); "no `spike` batch". |
| 59 | 972–1003 | 2026-08-19 | HISTORICAL (stale) | §7.1 checkers table. Measured today: it lists 9 gate-run scripts; `test.sh` invokes 17; it says `check-suite-floors.sh` is "run by hand only — NOTHING invokes them" but `test.sh:304` invokes it; six scripts are unlisted (`check-gate-abort-safety`, `check-publication-suite-floors`, `check-release-executes`, `check-release-sync`, `check-test-vacuity`, `check-v1-index-ordering`). |
| 60 | 1005–1025 | pre-2026-08-15 | DURABLE | §8 pre-existing traces (Foundry/invariant/mutation lessons). |

**Totals:** 60 blocks — **42 HISTORICAL** (≈606 of 1025 lines), **14 CURRENT** (≈169 lines
including blanks), **4 DURABLE** (≈250 lines: blocks 27, 44, 55, 60).

**Ordering defect worth naming for the index:** the top-of-file blocks 10–21 run newest-first
(09-01, 08-29, 09-01, 09-02 ×4, 08-30 ×3, 08-20, 08-24) while §1's sub-sections run
oldest-first; a cold reader meets the same 2026-09-02 facts three times (blocks 13, 14, 15, 37
and 3–5) before reaching §1.

### 1.1 Live facts that must survive the move (numbered for the reviewer)

Each was read from the file at HEAD, or measured, as marked.

- **F1. Branch and remote.** `step-3/isolated-signer`; remote `origin` = `github.com/johnrfite1/sentinel`
  (measured: `git remote -v`; also `docs/publication-policy.state` `CANONICAL_REPOSITORY`). Line 23.
- **F2. Push state is measured, never quoted.** "Count what is unpushed with `git log --oneline
  origin/step-3/isolated-signer..HEAD`; do not quote a number from here" (lines 198–200).
  Measured at write time: `origin/step-3/isolated-signer` = `28b82a4`; one unpushed commit,
  `e73789d` (the Crucible debrief). That measurement is not to be copied into the live file.
- **F3. The Quench artifact.** `8dfaa275a669bd202c3fa45e36dc12cbbe261170` (A-033), the D-092 patch
  commit, child of `02458d2`, subject beginning `D-092 patch`; pushed to the PRIVATE remote as
  backup; the Quench on it is ANSWERED (D-093–D-096). Lines 6–9, 106, 409.
- **F4. Publication is NOT AUTHORISED; the repository is PRIVATE.** Backup pushes are not
  publication (D-044(a), D-089, D-091(d)); an agent pushes only on John's explicit direction for a
  specific state. Lines 198–203, 410.
- **F5. Visibility and venue.** `docs/publication-policy.state` is `PUBLICATION_STATE=HELD_PRIVATE`,
  `RIGHTS_MODE=UNDECIDED`, `SMITH_DECISION=NONE` (measured); `scripts/check-rename-gate.sh` judges
  against it. D-083(a),(g): audience = technical evaluators, venue = GitHub public, visibility
  unchanged (HELD_PRIVATE); custody RETAINED with the drain disclosed. Lines 171–177, 410.
- **F6. Licence DEFERRED (D-082(c)).** "No licence may be added or selected, and rights mode ships
  `UNDECIDED`" (`docs/decisions.md:333`). No agent may select one. Lines 9, 110, 147, 410.
- **F7. Two Crucible lines, not to be conflated.** (i) The **enforcement-publication line**
  (`S-20260829-sentinel-enforcement-publication`): HALTED, four A-018 / MSG-022 Criticals OPEN AT
  ANVIL (D-083(i)); the register is `docs/a018-remediation-register.md`. (ii) The **lab casting**
  (`S-20260830-sentinel-conformance-lab-r1`): Cycle 1's two Criticals closed at Cycle 2 on
  `cb124fe`; Cycle 2 sustained one (D-090); Cycle 3 extended by written note (D-090(c)); Cycle 3
  returned zero sustained Criticals on `81edee1` (MSG-034); D-092 patch → `8dfaa27`; Quench
  answered (D-096). Lines 88–90, 149–159, 403–404, 407–409.
- **F8. The Temper trigger.** "The first external evaluator engagement — the first time a
  named-audience human reads or runs the artifact outside the Crucible" (D-096(d),
  `docs/decisions.md:559`; rejected as triggers: the visibility decision, the licence decision,
  completion of the pruning pass). Line 409.
- **F9. The owed work.** Post-Quench under D-093(c): an archive index and a pruning pass over
  superseded passages, changing no mechanism (this pass). Also owed/John's: the licence (D-082(c));
  the visibility decision; AC8's summarising half (D-095); any further checklist item. Line 409.
- **F10. Gates.** S1 SIGNED 2026-07-28; S2 SIGNED 2026-08-16 (D-041), both by John, non-delegable
  (D-002); Gate 5 certified (D-038); Gate 8 PASSED with three limits (D-080) against the v0.2
  packet, not rerun on the v0.3 regeneration; D-055(a) MET (D-073) and unlocks nothing; D-048
  makes a clean result a precondition, never a trigger. Lines 21, 246–258, 416, 421, 426.
- **F11. What is not delegated.** Gate signing (D-002) and certification of public claims (§2
  capability table, README, résumé language — autonomy NONE); the five D-008 comprehension
  questions stay unseen (Gate 8 is pre-publication under D-032). Lines 380–383, 556–560.
- **F12. Names.** The project name is "Sentinel" (D-074); the EIP-712 domain string is `"Sentinel"`
  (D-075); no name/domain split; the reviewer packet is not name-agnostic. Lines 21–23, 38–40, 392–393.
- **F13. The addendum table's current rows** (lines 400–410), each to survive with its substance:
  Repair batch LANDED (`8d47a0b`, `5d93850`, `5c8c090`, `2318ae3`) · Lab casting Cycles 1–2 (as F7)
  · Enforcement line HALTED, four Criticals OPEN AT ANVIL (D-083(i)) · Review method: inventory
  diff (D-085(e)), 54 + 4 + 4 missing checks, D-047 retired, D-055(a) governs · Cycle 2 candidate
  `cb124fe` PUSHED (D-089) · Cycle 3 candidate `81edee1` reviewed, zero sustained Criticals,
  eighteen findings, PUSHED (D-091(d)) · D-092 patch LANDED and verified · Next: Quench answered,
  orchestrator files D-096 and closes the session; Temper trigger; owed work (F8, F9) ·
  Publication NOT AUTHORISED, licence DEFERRED, policy state (F5).
- **F14. Where the rulings live.** `docs/decisions.md` is canonical and wins (line 709); D-088…D-096
  are the Crucible-era rulings; the register's own record is `docs/a018-remediation-register.md`;
  the Quench handoffs are `docs/quench-orchestrator-handoff.md`, `-2.md`, `-3.md`, `-4.md`; the
  debrief is `docs/crucible-session-debrief-2026-09-03.md`. Lines 8, 156, 709.
- **F15. Counts are derived, not quoted.** Suite floors: `./scripts/check-suite-floors.sh`;
  findings: `./scripts/check-findings-ledger.sh`; review verdicts:
  `docs/review-2026-08-19-d057-targeted/VERDICT-LEDGER.tsv`. Lines 238–241, 568–569.
- **F16. Standing engineering constraints referenced from status.** The `GIT_INDEX_FILE` scrub
  ordering in `.githooks/pre-commit` and `scripts/check-secrets.sh` (guard: `check-v1-index-ordering.sh`);
  the gate executes an unlinked copy of itself under a supervisor (`check-gate-immutability.sh`);
  `V-3` accepted as a boundary at `scripts/check-secrets.sh` 148–152. Lines 187–196, 375–378, 421.
  These live in the scripts' own comments and in D-057(3)/D-062/D-073; the live file needs a pointer, not the paragraphs.
- **F17. One agent session at a time on this tree** (D-037) and the rest of §6 Environment facts. Lines 929–952.
  *[Correction, 2026-09-03, after review: this entry conflates two places. D-037's live text was the §4 index-table
  row at line 728; lines 929–952 carry A-037's §6 paragraphs. Both halves are live facts; the ruling was restored to
  §6 of the live file after the reviewer found the §4 table had taken it to the archive.]*
- **F18. The exit record and census of record.** `docs/review-2026-08-19-d057-targeted/d055-condition-status.md`;
  `docs/review-2026-08-19-d057-targeted/critical-high-census.md`. Lines 234–236, 421.

---

## 2. `HANDOFF.md` — block map (341 lines)

| # | Lines | Date | Class | What it is / what it recorded |
|---|---|---|---|---|
| 1 | 1–6 | 2026-07-27 | HISTORICAL | Header: "Build authorized through Gate S2" — spent 2026-08-16 (line 116 says so). |
| 2 | 8–17 | 2026-09-03 | CURRENT | Four one-line entries: D-096 (Temper trigger), D-095 (acceptance criteria), D-094 (assumptions 2/3/8), D-093 (assumptions 1/4/5; owed archive index). This is the current block. |
| 3 | 19–34 | 2026-09-02 | HISTORICAL | Cycle 3 returned; D-092 patch (a)–(g) landed "in this commit" (`8dfaa27`). |
| 4 | 36–59 | 2026-09-01/02 | HISTORICAL | Repair batch landed; two Crucible lines; D-085 reversal; final Cycle 3 candidate `81edee1` pushed (D-091(d)). |
| 5 | 61–72 | 2026-09-02 | HISTORICAL | First Cycle 3 candidate `0bc79a8`; D-090 route (a); D-092 Conscience Major 3 correction in place. |
| 6 | 74–82 | 2026-09-02 | HISTORICAL | Cycle 2 candidate `cb124fe`; D-087 scope; pushed under D-089. |
| 7 | 84–95 | 2026-08-30 | HISTORICAL | Cycle 2 HALTED; register drafted; corrected 2026-09-01. Carries live fact F7(i). |
| 8 | 97–104 | 2026-08-30 | HISTORICAL | Struck BLOCK→PASS defect; "`a38cff9` … origin at `70f4b4d`" (stale push record). |
| 9 | 106–114 | 2026-08-29 | HISTORICAL | D-081 checkpoint authorised. |
| 10 | 116 | 2026-08-16 | HISTORICAL | S2 signed; A-043; "the §14.8 ladder as John directs". |
| 11 | 118–134 | 2026-08-19 | HISTORICAL | Post-S2 review arc; A-080 correction; A-081 8 of 11 FAILED; loop PAUSED. |
| 12 | 136–147 | 2026-08-20 | HISTORICAL | Remediation loop stopped; Batch A1 FAILED twice; fail-open LIVE. |
| 13 | 149–173 | 2026-08-20 | HISTORICAL | A1 closed through the D-062 exception; `V-1` carried; A-098 correction; A-095 correction. |
| 14 | 175–181 | 2026-08-22 | HISTORICAL | D-058 batches HOLD; D-055 unruled. |
| 15 | 183–192 | 2026-08-22/24 | HISTORICAL | `V-1` guard; retired under D-073. |
| 16 | 194–205 | 2026-08-24 | HISTORICAL | D-055 MET (D-073), unlocks nothing. |
| 17 | 207–213 | 2026-08-25 | HISTORICAL | Name "Sentinel" (D-074). |
| 18 | 215–220 | 2026-08-25 | HISTORICAL | Gate 8 packet assembled (D-077). |
| 19 | 222–228 | 2026-08-25 | HISTORICAL | Packet corrected (D-078). |
| 20 | 230–234 | 2026-08-25 | HISTORICAL | D-014 annotated (D-079). |
| 21 | 236–248 | 2026-08-25 | HISTORICAL | Gate 8 PASSED with limits (D-080); four fixes (A-110). |
| 22 | 250 | 2026-07-27 | HISTORICAL | "Amended … by Opus 5 at build start: D-007…D-011". |
| 23 | 252–341 | 2026-07-27 | HISTORICAL (brief) with DURABLE parts | The original build brief: Mission (252–254), Read these (256–264), Operating corridor (266–272), Gates (274–290, with D-032/D-041 amendments at 278–280), Internal checkpoint (292–296), Kill criteria (298–303), **Verification partition (305–316)**, **House rules (318–327; rule 8 updated to D-074/D-080)**, Flagged assumptions (329–336), Known context (338–341). |

**Totals:** 23 blocks — **1 CURRENT** (block 2, ten lines), **22 HISTORICAL** (block 23 being
the original 2026-07-27 brief, itself historical as a brief because its mission "through Gate S2"
was spent on 2026-08-16).

**Durable parts inside the brief that are cited live and must remain reachable:** the
Verification partition table (lines 305–316) is cited by `docs/gate-5-vendor-audit.md` lines 3–5
("The verification partition in `HANDOFF.md` gives public claims … autonomy none") and by
`docs/session-state.md` 380–383; the House rules (318–327) are the standing fence and rule 8 was
edited 2026-08-25. Whether those two sections stay in the live `HANDOFF.md` or move with a pointer
is a fork (§8-4).

**Ordering defect:** blocks 3–9 run newest-first (09-02, 09-01, 09-02, 09-02, 08-30, 08-30,
08-29); block 10 jumps back to 08-16; blocks 11–21 then run oldest-first (08-19 → 08-25). The
reader is told "Start at `docs/session-state.md` §1" seven times (lines 82, 116, 134, 146, 176,
195, 208).

---

## 3. `README.md` — section map (309 lines)

Constraint restated: the entry region (1–46), "Start here", the verifier sections and every
measured claim are LIVE and do not change in substance. Only pointers are added.

| Lines | Section | Disposition | Reason |
|---|---|---|---|
| 1–29 | Entry: what Sentinel binds; `NOT ESTABLISHED`; not a detector; status at this revision | **keep** | Line 27 reads "Status at this revision (2026-09-02): a pre-publication candidate under external adversarial review". After D-096 the casting's checklist is complete; whether that sentence still describes the state is §8-2, not this pass's call. |
| 31–39 | Where the record lives | **keep + add one pointer** | Lines 37–39 already name "the archive" (`docs/decisions.md`, both registers, `docs/review-*/`). The natural single hook for `docs/ARCHIVE-INDEX.md`. |
| 41 | Name-collision disclosure | **keep** | Disclosure. |
| 43 | Tagline | **keep** | |
| 45 | "Sentinel is not a detector…" | **keep** | Restates 24–25; observed duplication only, no change proposed (entry region is frozen in substance). |
| 47–66 | Start here: the enforcement release | **keep** | LIVE. |
| 68–91 | Run the cold demo | **keep** | Measured claims (Node 26.3.0, Foundry 1.7.1, Python 3.9.6; the printed heading). |
| 92–136 | Verify independently | **keep** | Measured: 300 s window; exit `0`/`1`/`3`; lines 130–136 are the D-092(f) no-manifest limitation. |
| 138–166 | Two verifiers, two claims | **keep** | Measured run at lines 159–165 (`expiresAt` 1788059884); D-087(c), D-090(a), D-091(a), D-092(c),(d). |
| 168–177 | What is not established, and where it is written down | **keep** | LIVE. |
| 179–187 | Status | **trim to a pointer** | Lines 185–187 enumerate five Crucible record files and "D-088 through D-092"; measured today the record also has D-093–D-096, four Quench handoffs and the debrief — the list is one session stale. Replace the enumeration with "the Crucible record is mapped in `docs/ARCHIVE-INDEX.md`"; keep lines 181–185 (session-state authoritative; policy state; licence deferred). |
| 189–197 | `## Historical:` header paragraph | **split** | **Disclosure that survives:** lines 191–193 (what the packet is; off-chain half only) and 194–196: *"the Crucible's Cycle 2 sustained a Critical against exactly that: this file's verifier commands resolved only inside the packet, so a reader was routed to `verify.py`, which prints PASS on a BLOCK receipt."* Line 196–197 *"Nothing below is deleted; it is history, and the history is part of what is evaluated."* **Narrative that can move with a pointer:** the "first surface until 2026-09-02 … D-090(b) re-ranked it here" clause (194, 196). |
| 199–208 | Gate 8 result; v0.3 regeneration; two verifiers | **keep** | Disclosure: Gate 8 passed against the v0.2 packet and was not rerun (199–203); lines 203–208: *"the packet's older copy still prints a bare `=> PASS` on it"* — must survive. |
| 210–216 | What this packet does not contain | **keep** | Packet honesty limits (D-078, D-080). |
| 218–236 | What is cryptographically bound | **keep** | Reference body of the Gate 8 packet; its root twin was edited by D-092(a); not history in the D-093(c) sense. |
| 238–247 | Who signs what | **keep** | Line 247 carries an in-place dated correction ("corrected 2026-09-02; this sentence previously said the opposite"); a visible correction record, keep. |
| 249–257 | Why Case 3 blocks | **keep** | Line 257 carries the D-080 nonce-finding disclosure. |
| 259–261 | What a receipt proves | **keep** | |
| 263–275 | What a receipt does not prove | **keep** | Line 271 is disclosure that must survive: *"the packet's frozen copy of the verifier does not check them against a clock, so there an expired receipt still prints `=> PASS`. The repository's current `verifier/verify.py` … reports … `=> AUTHENTIC, NOT EXECUTABLE`, exit `3` (D-092(c))."* |
| 277–297 | The authenticity verifier, and what a PASS means | **keep 279–283 and 293–297; relocate most of 285–291 with a pointer** | 279–283 is the D-092(a) prose invocation (no fence may return). 285–291 is narrative: the two fenced commands, the Cycle 3 candidate making the BLOCK→PASS route copy-pasteable, three chairs failing it, D-092(a). Keep one sentence ("This section carried two fenced commands until 2026-09-02; under D-092(a) nothing here runs as written") plus a pointer. 293–297 is disclosure that must survive: `--domain` semantics; presenter-supplied domain "says nothing about signer identity"; and line 297: *"Two copies exist and they differ on this commit … `reviewer-packet/verifier/verify.py` … prints a bare `=> PASS`, and exits `0`; `verifier/verify.py` at the repository root prints `=> AUTHENTIC, NOT EXECUTABLE` … exits `3` (D-090(a)). The packet copy is the stale one; the root copy is the contract."* |
| 299–309 | In this repository | **keep + add one link** | Heading text is read literally by `scripts/assemble-reviewer-packet.py:220`; do not rename. Add "Archive index: `docs/ARCHIVE-INDEX.md`" beside the decision log and session-state links (306–307). |

**The three disclosures the brief names, located:** (a) the packet's frozen verifier prints PASS
on BLOCK — lines 194–196, 203–208, 297; (b) the note position — this is a packet fact, not a root
README fact: D-091(c)'s dated note stands and D-092(b) moved it above
`reviewer-packet/README.md:107–108`; the root README does not restate it and nothing here moves
or adds it; (c) the two copies differ — line 297 (and 271 for the clock).

**Measured:** `reviewer-packet/README.md` differs from `README.md` (`diff -q`); the packet copy
opens with a different second line ("A testnet mandate-to-effects conformance lab…"). It is the
frozen Gate 8 artefact and stays untouched.

**Line-number references into the README that exist elsewhere:** `README.md:234` appears ten
times (HANDOFF.md:23; `docs/a018-remediation-register.md:1098`;
`docs/cycle-3-patch-orchestrator-handoff.md` ×4; `docs/cycle-3-patch-return-note.md:24`; and in
`docs/decisions.md`). Today line 234 is the "Mandate, policy and evidence travel as plain JSON"
paragraph; the reference is to the deleted command and is historical by construction. No edit
to the README changes its meaning.

---

## 4. `docs/` file census (26 tracked files + 6 review directories)

Story letters refer to §5. "Filed" means the file was handed to the Crucible session as a
byte-for-byte artefact and must not move or change (§6).

| File | Lines | Class | Story | One line |
|---|---|---|---|---|
| `a018-remediation-register.md` | 1131 | LIVE (Crucible-facing register) | F, G | The A-018 remediation register; "authorises nothing"; §3 items closed with dated markers, §4 John's; D-093 records the owed work "in the register". |
| `ablation-report.md` | 212 | LIVE (generated; guarded) | B | §7.3 ablation output; `test.sh:882` diffs it against a regeneration; `check-vendor-honesty.sh:326` extracts its §7.2 caveat. |
| `check-inventory-diff-2026-08-31.md` | 221 | HISTORICAL (analysis of record) | G | D-085(e) inventory diff at `8146937`: 54 + 4 + 4 missing checks. |
| `crucible-session-debrief-2026-09-03.md` | 91 | Filed (Smith's debrief, "to be filed verbatim") | G | The session debrief, MSG-001…MSG-043. |
| `cycle-2-orchestrator-brief.md` | 147 | Filed | G | Cycle 2 instructions; candidate `cb124fe`. |
| `cycle-2-return-package.md` | 189 | Filed | G | Cycle 2 return package for the council. |
| `cycle-3-orchestrator-brief.md` | 178 | Filed | G | Cycle 3 instructions; candidate `81edee1`. |
| `cycle-3-patch-orchestrator-handoff.md` | 165 | Filed | G | The D-092 patch handoff: SHA, D-092 verbatim, return note verbatim. |
| `cycle-3-patch-return-note.md` | 98 | Filed | G | Maps Cycle 3's eighteen findings to the patch. |
| `cycle-3-return-note.md` | 149 | Filed | G | Cycle 3 return note on `81edee1`. |
| `d055e-scope-manifest.md` | 129 | HISTORICAL (instrument manifest) | C | Scope of the D-055(e) review, fixed by D-056(d); pairs with `scripts/check-review-scope.sh`. |
| `decisions.md` | 561 | LIVE — the record itself | all | D-001…D-096 and A-027…A-111 (106 A-entries); read by `check-rename-gate.sh`. **Does not change.** |
| `enforcement-release-v0.3.md` | 280 | LIVE (normative; guarded) | F | v0.3 type strings and release rulings; `SPEC_V03` for `check-type-strings.sh:40` and `check-eval-codes.sh:43`. |
| `exit-criterion-packet.md` | 238 | HISTORICAL | C | The measured packet that preceded D-055; "PREPARED, NOT DECIDED". |
| `gate-5-vendor-audit.md` | 502 | HISTORICAL (certified table's audit) | B | Gate 5 §2 audit for D-038; excluded from vendor scans by name. |
| `gate-s1-evidence.md` | 323 | HISTORICAL (signed pack) | A | Gate S1, SIGNED PASS 2026-07-28. |
| `gate-s2-evidence.md` | 986 | HISTORICAL (signed pack; §11 load-bearing) | B, C | Gate S2, SIGNED PASS 2026-08-16 (D-041); §11/§11.0 accepted limits; D-069 annotation. |
| `publication-policy.state` | 70 | LIVE (machine-read) | H | `HELD_PRIVATE` / `UNDECIDED` / `NONE`; judged by `check-rename-gate.sh`. |
| `quench-orchestrator-handoff.md` | 30 | Filed | G | D-093 handoff. |
| `quench-orchestrator-handoff-2.md` | 32 | Filed | G | D-094 handoff. |
| `quench-orchestrator-handoff-3.md` | 39 | Filed | G | D-095 handoff. |
| `quench-orchestrator-handoff-4.md` | 43 | Filed | G | D-096 handoff; Temper trigger. |
| `repair-protocol.md` | 110 | LIVE (binding method, D-052(b)) | C, D | Required for every repair. |
| `round-six-brief.md` | 91 | HISTORICAL | C | Round six brief, "prepared and NOT RUN" (it then ran 2026-08-18). |
| `session-state.md` | 1025 | LIVE (status) | all | Mapped in §1; read by `check-suite-floors.sh`. |
| `v1-1-register.md` | 949 | HISTORICAL register (deferred work) | B, C | The v1.1 register behind the re-label decision; §8 mutation survivors; cited by `scripts/test.sh:673`. |
| `review-2026-08-15/` | dir | HISTORICAL evidence | B | `artifacts/` (promoted into `mutate.sh`) and the superseded §7.5 draft. |
| `review-2026-08-16/` | dir | HISTORICAL evidence | B | Attack probes for A-040 and A-043. |
| `review-2026-08-17/` | dir | HISTORICAL evidence | C | Round five, eight lens reports at `8234aba`. |
| `review-2026-08-18-d055e/` | dir | HISTORICAL evidence (guarded) | C | D-055(e) at `7e0ab7f`; `FINDINGS-LEDGER.tsv` read by `check-findings-ledger.sh:41`. |
| `review-2026-08-18-round-six/` | dir | HISTORICAL evidence | C | Round six at `140c59e`. |
| `review-2026-08-19-d057-targeted/` | dir | HISTORICAL evidence; carries the D-055 exit record | D, E | Batch cards, `VERDICT-LEDGER.tsv`, `d055-condition-status.md`, `critical-high-census.md`. |

Counts: 26 tracked files (25 `.md` + 1 `.state`), of which LIVE 7 (`a018-remediation-register`,
`ablation-report`, `decisions`, `enforcement-release-v0.3`, `publication-policy.state`,
`repair-protocol`, `session-state`), Filed 11 (six `cycle-*`, four `quench-*`, the debrief),
HISTORICAL 8; plus 6 review directories, all historical evidence.

---

## 5. The decision log's stories (the index's spine)

Grouped from `grep -n "^- \*\*D-" docs/decisions.md` (96 headings, lines 13–551). The ranges are
by decision number; the log's physical order is not monotonic (D-044…D-032 sit at lines 85–129,
newest-first, then D-045 onward oldest-first from line 181).

**A. Intake and the build gates** — D-001…D-018 (2026-07-27/28). Settled the §14 ladder, the two
mid-build gates and their non-delegable signing (D-002, D-004), kill criteria (D-003), the four
delegated forks (D-007…D-011), signer refusal semantics and no conformance checks in the signer
(D-012…D-015), the naming block (D-016), and what "end-to-end" meant for S1 (D-017, D-018); S1
signed 2026-07-28. Carried by: `HANDOFF.md` (the brief, lines 252–341), `docs/gate-s1-evidence.md`,
`Sentinel_Lab_Proposal_v0_2.md` §14.8–14.9.

**B. Specification clarifications, labelling, Gate 5 and Gate S2** — D-019…D-042 (2026-08-15/16).
Settled calldata origin, equality of purpose fields, reverting simulation, `reasonCodesHash`,
published type strings and enumerations (D-019…D-031); split §7.5 into six S2 conditions and two
pre-publication conditions (D-032); measured the contamination channel and declared the re-freeze
threshold (D-033…D-036); one session at a time (D-037); Gate 5 certified (D-038); S2 SIGNED on §11's
limits (D-041), annotated for A-043 (D-042). Carried by: `docs/gate-s2-evidence.md`,
`docs/gate-5-vendor-audit.md`, `docs/ablation-report.md`, `docs/review-2026-08-15/`,
`docs/review-2026-08-16/`, session-state §4 (lines 707–773).

**C. The post-S2 review loop and its terminating condition** — D-043…D-057 (2026-08-16→19).
Settled CONSOLIDATE (D-043), the session close and both capability deferrals (D-044), the
stopping rules (D-045, D-046), the loop's terminating condition (D-047, later superseded by
D-055(a) and retired by D-085), sequencing before pre-publication (D-048), rounds five and six
(D-049…D-052), the atomic-drain boundary (D-053, D-054), the exit criterion C1 + T1–T4 (D-055),
the bounded D-055(e) review and John's rulings on its 23 findings (D-056, D-057). Carried by:
`docs/review-2026-08-17/`, `docs/review-2026-08-18-round-six/`, `docs/review-2026-08-18-d055e/`,
`docs/repair-protocol.md`, `docs/exit-criterion-packet.md`, `docs/round-six-brief.md`,
`docs/d055e-scope-manifest.md`, `docs/v1-1-register.md`.

**D. The convergence reset, batch cards and Batch A1** — D-058…D-066 (2026-08-19→21). Settled
test-first remediation (D-058), the Gate 5 option and the repair-contract corrections (D-059),
abandonment of the global repair contract (D-060), A1 attempt two and no third (D-061), the one
`GIT_INDEX_FILE` containment exception (D-062), withdrawal of standing force authorisation (D-063),
B3/B4 superseded for the hook path (D-064), the A-EXTRACT threat model (D-065), delegation of the
remaining work (D-066). Carried by: `docs/review-2026-08-19-d057-targeted/` (README, `batch-cards/`,
`VERDICT-LEDGER.tsv`), session-state §1 blocks 39–43.

**E. D-055 met, the name, and Gate 8** — D-067…D-080 (2026-08-23→25). Settled the Gate 5 §7.2
condition (D-067), six forks (D-068), the §11 annotation (D-069), 14 of 20 (D-070), R5 and V-6
(D-071, D-072), D-055(a) MET and unlocking nothing (D-073), the name "Sentinel" (D-074), the domain
string (D-075), the rename-gate re-scope (D-076), the Gate 8 packet assembled and corrected
(D-077, D-078), D-014 annotated (D-079), Gate 8 PASSED with three limits (D-080). Carried by:
`docs/review-2026-08-19-d057-targeted/d055-condition-status.md` and `critical-high-census.md`,
`reviewer-packet/` (frozen), README `## Historical:` (lines 189–297).

**F. The enforcement release, its Crucible casting halted at the Anvil, and the publication
posture** — D-081…D-084 (2026-08-29/30). Settled the Cycle 2 enforcement checkpoint (`a38cff9`,
D-081); the four A-018 / MSG-022 Criticals sustained and the line HALTED; token-authority
disclosure, the state-aware publication guard and the deferred licence (D-082); product identity,
scope, the fresh casting, D-047's reach and the halted line (D-083); the gate's silent-abort fix
(D-084). Carried by: `docs/a018-remediation-register.md`, `docs/enforcement-release-v0.3.md`,
`docs/publication-policy.state`, `release/` (generated).

**G. The lab casting: Cycles 1–3, the patch and the Quench** — D-085…D-096 (2026-08-31→09-03).
Settled D-047 retired / D-055(a) governs and the inventory-diff method (D-085); the fail-open clock
fixed (D-086); the ~35-item Cycle 2 candidate (D-087); the `verify.py` exemption (D-088); push as
backup (D-089); Cycle 2's result, route (a) and Cycle 3 by written note (D-090); the three forks
and `81edee1` pushed (D-091); Cycle 3 zero Criticals and the narrow patch → `8dfaa27` (D-092); the
Quench: assumptions 1/4/5 (D-093), 2/3/8 (D-094), acceptance criteria (D-095), no unresolved
Criticals, the surviving pre-mortem, the decision note and the Temper trigger (D-096). Carried by:
`docs/check-inventory-diff-2026-08-31.md`, the six `docs/cycle-*` files, the four
`docs/quench-orchestrator-handoff*.md`, `docs/crucible-session-debrief-2026-09-03.md`.

**H. Licence, venue, audience — the publication posture across arcs** (cross-cutting). D-016
(block) → D-074 (naming lifts, publication stays blocked); D-032/D-048 (Gate 8 pre-publication;
clean results are preconditions, never triggers); D-082(c) (licence deferred); D-083(a),(g)
(audience technical evaluators, venue GitHub public, visibility unchanged, custody retained);
D-089/D-091(d) (backup push is not publication); D-096(d) (the Temper trigger, and what was
rejected as one). Carried by: `docs/publication-policy.state`, README "Status" (179–187),
session-state block 22.

Eight stories. A, B, C, D, E are complete arcs; F is halted; G is closed by the Quench; H is open.

---

## 6. What must NOT move

**By the brief:** `docs/decisions.md` (the record itself); `docs/a018-remediation-register.md`;
the six `docs/cycle-*` and four `docs/quench-*` files and `docs/crucible-session-debrief-2026-09-03.md`
(filed with the Crucible byte-for-byte); `reviewer-packet/**` (frozen Gate 8 artefact; D-091(c),
D-092(b)); `release/**` (generated; `check-release-sync.sh` refuses a tree that differs from the
assembler's output).

**Read by a script or guard (measured by grep of `scripts/`, non-comment lines):**

| Path | Reader | Gate-run? | What the reader needs |
|---|---|---|---|
| `docs/session-state.md` | `check-suite-floors.sh:41` (opens it; refuses if it contains "What is stable and worth stating: current floors are Foundry" or "D-010 verifier:** 7 samples", lines 178 and 181) | **yes**, `test.sh:304` | File exists at this path; neither string reappears. |
| `README.md` | `assemble-reviewer-packet.py:337–346` (reads; cuts at `## In this repository`) | no (hand-run; output is the frozen packet — **do not run it**) | The heading text, verbatim. |
| `docs/ablation-report.md` | `test.sh:882,890` (diff vs regeneration); `check-vendor-honesty.sh:326,345` (§7.2 caveat) | yes | Unchanged. |
| `docs/enforcement-release-v0.3.md` | `check-type-strings.sh:40`, `check-eval-codes.sh:43` (`SPEC_V03`) | yes | Unchanged. |
| `docs/publication-policy.state` | `check-rename-gate.sh:162` | yes | Unchanged. |
| `docs/decisions.md` | `check-rename-gate.sh:266–273` (existence; `SMITH_DECISION` grep) | yes | Unchanged. |
| `docs/review-2026-08-18-d055e/FINDINGS-LEDGER.tsv` | `check-findings-ledger.sh:41` | no (hand-run) | Unchanged. |
| `HANDOFF.md`, `docs/session-state.md`, `docs/decisions.md`, `docs/gate-5-vendor-audit.md`, `docs/v1-1-register.md`, `docs/review-2026-08-15/artifacts/` | `check-vendor-honesty.sh:149` `EXCLUDED` (exact filenames exempt from the vendor-name scan); `:175` `EXCLUDED_LABELS` | yes, `test.sh:301` | See constraint below. |
| `docs/gate-s1-evidence.md`, `docs/gate-s2-evidence.md`, `docs/decisions.md`, `docs/session-state.md`, `HANDOFF.md`, `README.md`, `docs/repair-protocol.md`, `docs/exit-criterion-packet.md`, `docs/v1-1-register.md`, `docs/gate-5-vendor-audit.md`, `docs/round-six-brief.md`, `docs/d055e-scope-manifest.md`, `docs/review-*`, `docs/ablation-report.md` | `check-review-scope.sh:79–118` partition | no (hand-run only, D-057(4)) | Measured today: it already FAILS, exit 1, "444 tracked file(s) assigned to NO reviewer" — 15 of them under `docs/` (the register, the inventory diff, the debrief, all `cycle-*`/`quench-*`, `enforcement-release-v0.3.md`, `publication-policy.state`), the rest `release/**`. New `docs/archive/*` files join that list; the verdict class does not change. Adding an arm is a `scripts/` edit, outside this pass. |
| `release/README.md` | written by `assemble-enforcement-release.py:489` from a constant | — | Not derived from the root README. |

**Constraint 2 in detail (vendor-name scan).** `check-vendor-honesty.sh:98–99` defines nine
any-case vendor names and two exact-case ones; lines 261–265 fail the gate if any appears,
word-bounded, in any scanned file. `docs/session-state.md` is exempt by exact filename;
`docs/archive/session-state-history.md` would not be. Measured: exactly one hit in the three live
documents — `docs/session-state.md:637`, inside HISTORICAL block 50 (A-047's case-sensitivity
example, quoting a vendor name in two table cells). `HANDOFF.md` and `README.md`: zero hits; zero
exact-case hits; zero §10.1 label phrases (the grep at line 228 of the script) in any of the three. The
options are §8-1; none is chosen here. Note that this inventory file is itself scanned (it is
untracked and not ignored — `.gitignore` does not cover `docs/archive/`), which is why it names
the line and not the word.

**Section headings that are link targets and must survive in the live files:**
`docs/session-state.md` "§1" (HANDOFF ×7, README:307), "§0" (line 208), "§3" (`check-suite-floors.sh:4`,
`test.sh:346,397,812` comments), "§5" (`docs/v1-1-register.md`), "§7.1"; README `## In this repository`
(script-read); README "Two verifiers, two claims" (heading at README:138; cited at README:166,
`docs/session-state.md:132`, and mirrored by `docs/enforcement-release-v0.3.md:180`); "What this
release does not bound" lives in `release/README.md`, not here.

**Line-number references into the live files that exist elsewhere and are already stale
(measured):** `session-state.md:240`, `:573`, `:623`, `:3` and `HANDOFF.md:42`, `:93` (in
`docs/decisions.md` and `docs/v1-1-register.md`) — today those lines are unrelated text. They are
records of what a reviewer saw at a past commit; no move makes them less accurate.

---

## 7. Proposed target layout (nothing below is written by this inventory)

**`docs/ARCHIVE-INDEX.md` (new, ~150 lines).** The map for a reader who did not live through it:
(1) a five-line orientation — what Sentinel is, where the mechanism is, where status is, the one
sentence on why the history is kept ("part of what is evaluated", README:37–39, D-093); (2) the
eight stories of §5, each with its decision range, one sentence, and its two or three carrying
documents; (3) a table of every `docs/` file and review directory from §4 with its class; (4) the
list of standing constraints and where each is guarded (F16, §6); (5) pointers to the two history
files below and to the archive inventory. It carries no status of its own and no numbers that a
script derives.

**`docs/archive/session-state-history.md` (new).** The HISTORICAL blocks of §1 moved verbatim,
each under its own dated heading, in chronological order (oldest first), with the block's original
line range at HEAD `e73789d` noted beside it so the reviewer can diff. Blocks 3–6, 8–21, 23, 26,
28–34, 38–43, 47, 49–54, 58, 59. Block 50's line 637 is subject to §8-1 before it moves. Struck
text stays struck.

**`docs/archive/handoff-history.md` (new).** HANDOFF blocks 3–21 moved verbatim, chronological,
with original line ranges. Blocks 1, 22 and 23 (the original brief) are §8-4.

**What remains in `docs/session-state.md` (~420 lines):** the header (blocks 1–2, with line 8
corrected to name all four handoffs); a rewritten single **current block** on top carrying F1–F18
in that order, then the addendum table (block 37, its duplicated sentence de-duplicated) and one
pointer line: "History: `docs/archive/session-state-history.md`; the map: `docs/ARCHIVE-INDEX.md`";
block 22 and 24 (push/count discipline); §0 blocks 25, 27 (the pattern list) and 35; §1 blocks 36
and 44; §2; §3 blocks 46 and 48 plus a two-line replacement for blocks 52/59 that says "the gate's
stages are whatever `scripts/test.sh` invokes; read it" (with the six unlisted scripts named once);
§5, §6, §7 block 57, §8. The reading order (block 23) is replaced by three lines: §1 here → the
index → `docs/decisions.md` from D-093.

**What remains in `HANDOFF.md` (~110 lines, or ~200 under §8-4 option b):** the header rewritten
to say what the file now is (the build brief of 2026-07-27, ratified, with a current status
pointer); the current block (block 2) plus one pointer line to `docs/archive/handoff-history.md`
and the index; then either the Verification partition and House rules only (option a) or the whole
original brief (option b).

**What remains in `README.md` (~300 lines):** everything, with three edits: the pointer added at
lines 31–39; the Status paragraph's file enumeration (185–187) replaced by the index pointer; lines
285–291 reduced to one sentence plus a pointer. Every disclosure quoted in §3 stays.

---

## 8. Forks for John (agents propose; nothing here is decided)

1. **Session-state line 637 (block 50) and the vendor-name scan.** (a) Leave block 50 in
   `docs/session-state.md` as a dated historical tail, so nothing moves through the guard;
   (b) move it and replace the two quoted cells with the capability class ("a vendor name in two
   casings") — a wording change inside a historical record; (c) add `docs/archive/` to
   `check-vendor-honesty.sh:149` — a `scripts/` edit the guard's own text calls "a claim about
   that file", outside this pass's scope. No recommendation is implied by the order.
2. **README line 27.** "Status at this revision (2026-09-02): a pre-publication candidate under
   external adversarial review" — after D-096 the casting's checklist is complete and the Temper
   trigger is set. The entry region is frozen in substance by the brief; whether this sentence is
   still true is John's to say.
3. **The durable lessons (blocks 27, 44, 55, 60 — ≈250 lines).** They are not "superseded
   passages" and this inventory leaves them in `docs/session-state.md`. The cold reader's
   "dense" cost may still weigh on them; a separate live file (`docs/traces.md`) is possible and
   is not proposed here.
4. **HANDOFF's original brief (block 23).** (a) Keep only the Verification partition (305–316)
   and House rules (318–327) live and move the rest to `docs/archive/handoff-history.md`;
   (b) keep the whole brief in place under a heading that says it is the 2026-07-27 brief.
   Both keep the two cited sections reachable at their current path.
5. **`check-review-scope.sh` arms for `docs/archive/*` and `docs/ARCHIVE-INDEX.md`.** The guard
   already fails on 444 unassigned files and is hand-run only; whether to extend its partition is
   a `scripts/` change and not part of the pruning pass.
