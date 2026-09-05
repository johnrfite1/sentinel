# Sentinel — Session State

Rewritten at the end of each working session. **This file, not the conversation, is the
memory.** If it disagrees with anything an agent remembers, this file wins.

Last updated: **2026-09-03 (the D-093(c) archive index and pruning pass: the stacked history that stood in this file is in `docs/archive/session-state-history.md`, verbatim, and the map is `docs/ARCHIVE-INDEX.md`; the Quench on `8dfaa27` is ANSWERED, D-093–D-096; publication is not authorised; licence DEFERRED).**
D-055 is MET (D-073). It unlocks nothing. **"Sentinel" is the project name (D-074).**
The EIP-712 domain string is also `"Sentinel"` (D-075, recorded late). There is no
name/domain split. Branch `step-3/isolated-signer`.

## Current state — 2026-09-03

**The Quench is complete, and what shipped is a private artifact.** The Quench artifact is
`8dfaa275a669bd202c3fa45e36dc12cbbe261170` (A-033) — the D-092 patch commit, child of `02458d2`,
subject beginning `D-092 patch` — pushed to the PRIVATE remote as backup, which is not
publication (D-044(a), D-089, D-091(d)). The Quench on it is ANSWERED: D-093 accepted existential
assumptions 1, 4 and 5 with stated risk on one unaided named-audience cold read (MSG-041); D-094
amended assumption 2 to the architecture (Plausible, stated risk) and accepted 3 and 8 with stated
risk, so no register assumption remains Untested; D-095 ruled the acceptance criteria (AC1, 3–7,
10 met; AC8 half met, half owed; AC9 struck; AC2 clause 1 waived for A-033 with stated risk);
D-096 found no unresolved Criticals, named the surviving pre-mortem (Catalyst C1, record density),
recorded the decision note and set the Temper trigger. The handoffs are
`docs/quench-orchestrator-handoff.md`, `-2.md`, `-3.md` and `-4.md`; the debrief is
`docs/crucible-session-debrief-2026-09-03.md`. Remote `origin` is the `CANONICAL_REPOSITORY` in
`docs/publication-policy.state`.

**Two Crucible lines; do not conflate them.**

- The **enforcement-publication line** (`S-20260829-sentinel-enforcement-publication`) is HALTED:
  its four A-018 / MSG-022 Criticals are OPEN AT ANVIL (D-083(i)). Its register is
  `docs/a018-remediation-register.md`; the register's §3 items were authorised piecemeal
  (D-082(a), D-083(j), D-085(f), D-086, D-087) and most are CLOSED with dated markers; §4 is John's.
- The **lab casting** (`S-20260830-sentinel-conformance-lab-r1`, the fresh casting D-083(g)
  required): Cycle 1's two Criticals closed at Cycle 2 on `cb124fe` (pushed as backup, D-089);
  Cycle 2 sustained one (D-090); Cycle 3 was extended by the Smith's written note (D-090(c));
  Cycle 3 returned zero sustained Criticals on `81edee1` (MSG-034; eighteen findings; pushed as
  backup, D-091(d)); the D-092 narrow patch (a)–(g) landed as `8dfaa27`, independently verified
  (`docs/cycle-3-patch-return-note.md` §5); the Quench on it is answered (D-096).

**What is and is not authorised.** Publication is **NOT AUTHORISED** and the repository is
PRIVATE: `docs/publication-policy.state` is `PUBLICATION_STATE=HELD_PRIVATE`,
`RIGHTS_MODE=OPEN_SOURCE` (Apache-2.0, D-097), `SMITH_DECISION=NONE`, and `scripts/check-rename-gate.sh` judges against
it. ~~The licence is DEFERRED (D-082(c))~~ **The licence is Apache-2.0 (D-097, 2026-09-04)**: `LICENSE` and `NOTICE` at the root, rights mode ships
~~`UNDECIDED`, and no agent may select one~~ `OPEN_SOURCE` since D-097; John selected it. D-083(a),(g) stand: audience = technical evaluators,
venue = GitHub public, visibility unchanged (HELD_PRIVATE), custody RETAINED with the drain
disclosed. No gate is signed or reopened. Gate signing (D-002) and certification of public
claims — the §2 capability table, README, résumé language — stay outside the delegation
(HANDOFF verification partition, autonomy *none*); the five D-008 comprehension questions stay
unseen, Gate 8 being pre-publication under D-032. An agent pushes only on John's explicit
direction for a specific state, PRIVATE verified first.

**Gates.** S1 SIGNED 2026-07-28; S2 SIGNED 2026-08-16 (D-041) — both by John alone, non-delegable
(D-002). Gate 5 certified (D-038). Gate 8 PASSED with three limits (D-080) against the v0.2
packet and has not been rerun against the v0.3 regeneration. D-055(a) is MET (D-073) and unlocks
nothing; D-048 makes a clean result a precondition, never a trigger. The exit record is
`docs/review-2026-08-19-d057-targeted/d055-condition-status.md`; the census of record is
`docs/review-2026-08-19-d057-targeted/critical-high-census.md`.

**Temper trigger (D-096(d)).** The first external evaluator engagement — the first time a
named-audience human reads or runs the artifact outside the Crucible. Rejected as triggers: the
visibility decision, the licence decision, and completion of the pruning pass.

**Publication prep, Phase 1 (2026-09-04) — DONE in this commit.** The full history was scanned
(gitleaks, 322 commits: no secret; the hits were a contract address under a `token` key and
Anvil's published dev key, allow-listed with reasons in `.gitleaks.toml`). Root README trimmed 322
→ 178 lines: the Historical section is a stub over `docs/archive/readme-historical-section-2026-09-04.md`,
the restated runnable path is a pointer to `release/README.md`, the dense verifier paragraph is
one pass. Added `SECURITY.md`, `CONTRIBUTING.md`, `.github/workflows/gate.yml` (the fast gate in
CI), `.nvmrc`/`.tool-versions`/`engines` (R-A018-13), `release/demo-out/` ignored and skipped by
the sync guard (R-A018-27), `.claude/` and `.pytest_cache/` ignored. **Phase 2 is John's
decisions** (default branch, the reviewer packet, the agent-facing status docs, the enforcement
casting's record, GitHub settings); **Phase 3 is the flip**, in the order: ruling → policy file
`AUTHORIZED_PUBLIC` with the ruling's number, committed and pushed → visibility → a gate run.

**Owed work.** Under D-093(c), post-Quench: an archive index and a pruning pass over superseded
passages, changing no mechanism — carried out in the working tree of 2026-09-03
(`docs/ARCHIVE-INDEX.md`, `docs/archive/session-state-history.md`,
`docs/archive/handoff-history.md`; the commit is John's). John's own: ~~the licence (D-082(c))~~ (ruled Apache-2.0 at D-097, 2026-09-04); the
visibility decision; AC8's summarising half (D-095); any further checklist item, the Temper
trigger among them.

**Standing engineering constraints referenced from here** live in the scripts' own comments and
in D-057(3), D-062 and D-073, not in this file: the `GIT_INDEX_FILE` scrub-before-`rev-parse`
ordering in `.githooks/pre-commit` and `scripts/check-secrets.sh` (guard
`scripts/check-v1-index-ordering.sh`, gate-run); the gate executing an anonymous, unlinked,
read-only copy of itself under a supervisor (`scripts/check-gate-immutability.sh`, gate-run);
`V-3` accepted as a documented product boundary at `scripts/check-secrets.sh` 148–152.

**Where the rulings live, and where the history went.** `docs/decisions.md` is canonical and
wins; D-088…D-096 are the Crucible-era rulings. Every dated block that stood in this file before
2026-09-03 is in `docs/archive/session-state-history.md`, verbatim, newest first; the map of the
whole record — stories, files, what is live and what is filed — is `docs/ARCHIVE-INDEX.md`.
Reading order for a fresh instance: §1 below, then `docs/ARCHIVE-INDEX.md`, then
`docs/decisions.md` from D-093.

**Count what is unpushed with `git log --oneline origin/step-3/isolated-signer..HEAD`; do not
quote a number from here** — this file has published a stale one before, including one line
below its own instruction not to. The repository is PRIVATE and **publication is not authorised.**
Gate 8 passed with limits (D-080); D-048 makes that a precondition, never a trigger. D-016's
naming block has lifted (D-074); neither fact is publication permission. Pushing to the private remote is backup, never publication, and **an
agent pushes only on John's explicit direction for a specific state.**

**DO NOT QUOTE COUNTS FROM THIS FILE.** Suite floors: `./scripts/check-suite-floors.sh`.
Findings: `./scripts/check-findings-ledger.sh`. Review verdicts:
`docs/review-2026-08-19-d057-targeted/VERDICT-LEDGER.tsv`. This file has published stale
numbers repeatedly and been caught by independent verifiers doing it.


## 0. If you read nothing else, read this

**Gate S1 is SIGNED — PASS, John, 2026-07-28. GATE S2 IS SIGNED — PASS, John, 2026-08-16
(D-041).** Both by John alone at facilitated sessions, never by an agent (D-002, non-delegable).
**D-002's two mid-build gates are now both behind the project.**

**What S2 does NOT authorise, stated first because a signed gate is the moment scope creeps.**
D-016's naming block has lifted (D-074) and the repository is still PRIVATE. **Publication
is not authorised.** Gate 8 (five-minute comprehension) passed under D-080, with the three
limits in that entry recorded beside the result. The five held questions remain unseen by the
build loop. A passed pre-publication condition is not a publication decision.
Certification of public claims is still autonomy NONE. **S2 was signed on the state in
`docs/gate-s2-evidence.md` §11 INCLUDING
its limits, not despite them** — 14 of 20 classes exercising the class they name (credit iff an ABOUT check ran against the named phenomenon and recorded the outcome the spec assigns to it, UNRESOLVED included), and no live
agent in CI. D-041 carries an annotation naming what became known after it was signed.

**THE PATTERN, now the operating assumption rather than an observation. THIS IS THE PARAGRAPH A
REVIEWER BRIEF HAS TO ENCODE.** The defects are *honesty* defects — a claim stronger than its
evidence — and **the build loop does not find them.** Across 2026-08-15 to 2026-08-18, roughly
one hundred and forty findings came from adversarial reviewers, independent adjudicators,
independent labellers, the mutation harness and an independent reimplementation. The build loop
found essentially none of its own. Specifically and repeatedly:

- **An instrument can exist and point at the wrong thing.** Guards, tests and mutations have
  shipped aimed at something other than what they name — five or more times now.
- **A repair can generalise the DEMONSTRATION rather than the ARGUMENT.** A-028 fixed the branch
  its reviewer exploited and left the identical hole two lines down. A-043 is the cost.
- **A comment can describe a vulnerability and file it as an inconvenience.** A-028's test file
  named the exact bypass state in prose and routed around it.
- **A regression test can pass against the defect it names** (A-044).
- **A published number can be true once.** This file's own headline suite counts were stale for
  most of a day; its guard count has been wrong three times; and a suite figure was counted twice
  across two consecutive decision entries (`B-5`).
- **A FALSIFICATION PROBE CAN BE DEAD, AND ITS SILENCE READS EXACTLY LIKE A PASS.** Five were, on
  2026-08-17/18 alone: a mutation of a value already at the maximum so no percentile moved; a
  Solidity probe that did not compile and printed no PASS/FAIL line; two corpus runs that died on
  a missing build artifact long before reaching the code under test; and a grep pattern that
  matched nothing. **Ask what your probe MOVED before believing what its result implies.**
- **A CHECK CAN BE CAUGHT BY THE WRONG CHECK.** A tamper that fails on the canonical bytes tells
  you nothing about the check you were testing. Make the bundle wholly self-consistent — re-hash,
  re-bind, RE-SIGN — so only the check under test can reject it.
- **A HARNESS CAN REPORT A CLEAN SWEEP AGAINST NO PROTECTION AT ALL.** The first gate-immutability
  harness printed `4/4` against a script with the protection entirely absent: it mutated by `mv`,
  which renames a new inode and leaves the already-open original untouched. **Every falsification
  harness now needs an UNPROTECTED CONTROL that MUST be corrupted** — if the control survives, the
  harness is measuring nothing. Added `2026-08-18`.
- **EXIT STATUS 0 IS NOT SUCCESS.** Editing `scripts/test.sh` mid-run truncated the body: no
  syntax error surfaced to the caller, no `GATE PASSED` was printed, and bash **exited 0**. Read
  the OUTPUT, never the status. The gate now refuses a run that does not emit its completion
  token — because the status alone was never evidence.
- **A PROBE CAN BE DEAD BECAUSE OF THE DATA IT WAS AIMED AT.** Four checksum probes were inert
  because `OWNER` (`0x4444…`) and `VAULT` (`0x1111…`) are all-digit addresses, where changing the
  case changes nothing. The tests passed; they tested nothing. **Pick fixture values that can
  actually move under the mutation you intend.**

- **A REPAIR CAN OPEN A NEW HOLE WHILE CLOSING THE OLD ONE, AND IN THE OPPOSITE DIRECTION.**
  Batch A1 attempt one let the caller's git environment redirect every entry point. Attempt two
  scrubbed it — including `GIT_INDEX_FILE`, which git legitimately uses to hand the pre-commit
  hook a temporary index. **Too much deference, then too little, both fail-open.** Added
  `2026-08-20`.
- **A TEST CAN BE INVALID, AND TWO FAILING TESTS HIDE IT.** A1's original case 4 demanded a
  non-zero exit from the same command line case 2 demanded exit 0 from. Both failed at the
  pre-repair baseline, so the contradiction was invisible until an implementation made one pass.
  **A contradiction between two REQUIRED assertions is only visible once something starts
  passing.** Added `2026-08-20`.
- **AN ENUMERATION SHAPED LIKE A REPORTED SITE STOPS WHERE THAT REPORT STOPPED.** Two
  repository-wide contracts failed audit for this. A `cd "$(` pattern could not see the
  two-step `ROOT="$(git rev-parse …)"` idiom and missed eight scripts; the corrected sweep then
  missed a ninth outside its glob. **Enumerate by file, shebang and ownership — never by
  searching for one known idiom.** Added `2026-08-20`.
- **A GUARD CAN BE BROKEN WHILE THE PROPERTY IT GUARDS IS TRUE.** `V3-N2` broke
  `check-vendor-honesty.sh`'s §7.2 extraction, and the caveat it checks for is nevertheless
  present exactly once. **The property's truth does not restore the guard's standing as
  evidence** — D-059(1) holds the certification and rules the guard inadmissible until repaired.
  Added `2026-08-20`.

**None of that is a reason to distrust the work; it is the reason to keep pointing independent
eyes at it.** Everything above was found, fixed or recorded — and found by the process working.

**John has delegated design forks to the build loop.** Two things stay outside that
permanently, and were restated to him: **gate signing** (D-002) and **certification of public
claims** — the §2 capability table, README, resume language (HANDOFF verification partition,
autonomy *none*).

---

## 1. What the next instance should do

### YOUR JOB: NOTHING, WITHOUT AN INSTRUCTION FROM JOHN. Say so and stop.

The D-058 confirmed batches HOLD inside their declared boundaries. **D-055 is MET (D-073)
and unlocks nothing.** The name is "Sentinel" (D-074). The private packet at
`reviewer-packet/` is not name-agnostic. If you arrived with no instruction, report the
state below and wait.

### ADDENDUM 2026-09-01 — what has moved since the 2026-08-29 table (now archived) was written

The 2026-08-29 table this addendum extended is in `docs/archive/session-state-history.md`, as written. Since then:

| | |
|---|---|
| Repair batch | **LANDED** — `8d47a0b`, `5d93850`, `5c8c090`, `2318ae3` (2026-08-30). The BLOCK→PASS publication verifier is fixed; R-A018-18/23/24 closed under D-083; the release-sync, suite-floor, vacuity and gate-abort guards are wired; the register's §3 carries dated CLOSED markers |
| Lab casting, Cycles 1–2 | Cycle 1's two Criticals **closed at Cycle 2** (chairs reproduced both on `cb124fe`). Cycle 2 **sustained one**: first surface → `verify.py` PASS/0 on BLOCK (D-090). Cap of 2 reached; **Cycle 3 extended by the Smith's written note D-090(c)** |
| Enforcement line | **Unchanged: HALTED, four A-018 Criticals OPEN AT ANVIL** (D-083(i)) |
| Review method | **Inventory diff replaces one-at-a-time finding** (D-085(e)). Measured class: 54 + 4 + 4 missing checks, not 6. D-047 is retired; D-055(a) governs (D-085(a)) |
| Cycle 2 candidate | **LANDED `cb124fe`**, PUSHED to the PRIVATE remote as backup (D-089) |
| Cycle 3 candidate | **`81edee1` REVIEWED — Cycle 3 returned 2026-09-02: zero sustained Criticals (Adversary HOLDS); Subtractor, Catalyst and Conscience FAIL on `README.md:234`; eighteen findings.** `0bc79a8` closed the condition as written (verified, both clauses HOLD); `81edee1` added D-091(a) refusal records (verified, HOLDS) and was PUSHED as backup (D-091(d)). Return note `docs/cycle-3-return-note.md`; result and rulings at D-092 |
| D-092 patch | **LANDED, verified** — narrow, (a)–(g), before the Quench; the child of `02458d2`, subject `D-092 patch …`. Code and status documents land in ONE commit. No code change is claimed landed |
| Next | ~~As written on 2026-09-02.~~ **Superseded 2026-09-03 — see the Current state block at the top of this file, which is the authority.** The Quench is answered and D-096 is filed; the archive index and pruning pass owed under D-093(c) were carried out on 2026-09-03. What remains is John's: the licence (D-082(c)), the visibility decision, and the Temper at the first external evaluator engagement. **No gate signature, no publication** |
| Publication | **NOT AUTHORISED.** Unchanged. ~~Licence DEFERRED (D-082(c))~~ Licence Apache-2.0 (D-097); `docs/publication-policy.state` is HELD_PRIVATE / ~~UNDECIDED~~ OPEN_SOURCE (D-097) / NONE |

### THE METHOD THAT NOW GOVERNS REMEDIATION (D-060(1))

**There is no repository-wide prose contract.** Two were written; both failed independent audit.
The diagnosis, and it is the reason the method was replaced rather than iterated: *every
enumeration was run with a command shaped like a site somebody had already reported, so each
stopped where that report stopped.* Remediation now proceeds through **small batch cards** —
one invariant, an explicit file/symbol boundary, a test matrix, controls, exclusions — and
**completeness is assessed INSIDE the declared boundary**, never by claiming every repository
sibling has been found. Entry points are enumerated **by file, shebang and ownership**, never by
searching for a known idiom.

**Test-first is not optional (D-058(1)).** An independent test author writes the observing tests
and demonstrates them failing BEFORE any production change; the implementer may not modify,
weaken, relocate or delete an independent test; **if a test is invalid, work stops and the
invalidity is independently confirmed before anything is replaced** — that happened once already
and the replacement was authorised only after adjudication.


## 2. Authority

**Agents propose; John decides.** Routine engineering judgment is yours; John has delegated
design forks. Never sign a gate, never certify a public claim.

- **The five D-008 comprehension questions are held by John and must stay unseen.** Do not ask
  for them, guess them, or write substitutes. Gate 8 is PRE-PUBLICATION under D-032, not S2.
- **A worked pattern for decision sessions**, used for D-033…D-036: present ONE fork at a time
  with verified facts, real options, costs, and a recommendation; record the ruling immediately
  with the counter-argument and the condition that would reverse it. **When a reversal condition
  later fires, say so and hand the decision back** — A-034 did exactly that.

## 3. Where the build is

**DO NOT READ A SUITE COUNT FROM THIS FILE. RUN `./scripts/test.sh` AND READ ITS OUTPUT, OR RUN
`./scripts/check-suite-floors.sh` (R4-F4, D-055(e), CONFIRMED).**

The gate's stages are whatever `scripts/test.sh` invokes; the measured list, gate-run and
hand-run, is §7.1 below. The staleness chronicle that stood here — the corrected-count notes,
the A-045 and A-048 review records and the "TEN mechanical stages" paragraph — is in
`docs/archive/session-state-history.md`; the A-046…A-051 block is retained at the tail of this
file under a guard constraint.

Run `./scripts/test.sh`; use `--gate` for evidence. Read the coverage boundary it prints — it is
ONE statement, not a log; rewrite the affected layer when a step lands, never append.

## 4. Decisions and findings — 2026-08-15 and 2026-08-16

**The canonical record is `docs/decisions.md`, and it is the one that wins.** The index table of
D-033…D-051 and A-029…A-069 that stood here is in `docs/archive/session-state-history.md`; the
map of the whole record, by story, is `docs/ARCHIVE-INDEX.md`.

## 5. Traces — what worked, and what was a dead end

**Dead ends and traps — do not repeat:**

- **A CHECK THAT ALWAYS FIRES LOOKS EXACTLY LIKE ONE THAT CATCHES EVERYTHING.** A-051: the first
  verdict check used BSD `sed` with `\|` alternation, which basic regex does not support, so it
  matched nothing and failed on EVERY run including a clean tree. All three defeat probes duly
  came back "caught, exit 1" — which is what a working fix looks like. **Caught only by running
  the BASELINE first on an untouched tree.** This is the twin of the vacuous probe and it is the
  more seductive one, because every falsification appears to succeed.
- **A TEST THAT ASSERTS A PROPERTY OF THE CORPUS CANNOT CATCH A VERIFIER THAT ACCEPTS WHAT THE
  CORPUS HAPPENS NOT TO CONTAIN.** A-056: `test_only_review_receipts_carry_an_override` asserts
  no fixture overrides a BLOCK receipt — true, worth knowing, and completely silent on whether
  the verifier would accept one. §5.5's check was changed to `verdict in ("REVIEW","BLOCK")` and
  every test passed. Three checks survived on this confusion. **A fixture property says what the
  repository CONTAINS; a verifier property says what the code ACCEPTS.**
- **RE-SIGNING IS WHAT MAKES A BINDING THE WITNESS.** A-056: `override-nonce` bumps a SIGNED
  field and leaves the old signature, so the signature check fires first and §3.3(9)'s nonce
  binding never bites. `override-wrongkey` leaves `ownerAddress` declaring the owner, so §3.3(7)
  never bites. A tamper mode that is caught by a *different* check than the one it targets is
  worth nothing, and the tamper matrix will score that check as covered.
- **THE TAMPER MATRIX IS NOT A COVERAGE MEASURE; MUTATION IS.** A-055 measured both directions
  and refuted "a check no mode targets is a check nothing asserts" — an inference that had been
  load-bearing across three entries. Of 33 checks no mode makes fail, 18 probed → **10 CAUGHT**.
  Of checks that DO fail under some mode, 10 neutered → **5 SURVIVED**.
- **`__pycache__` MASKS SAME-SIZE MUTATIONS.** A same-length edit landing in the same
  filesystem-mtime second makes CPython reuse stale bytecode, so the mutated run executes clean
  code and reads as a no-op — **and same-size mutations are the interesting ones.** Run `python3
  -B` and clear `__pycache__` between variants.
- **A REVIEW BRIEF IS AN INSTRUMENT AND NOTHING CHECKS IT.** Twice in two rounds the brief was
  the defect: A-051's named five modules when there were six, omitting the one holding two of
  that round's best findings; A-055's was scoped to `Check(...)` mutations and would have missed
  the one live defect that needs no mutation. **Invite the reviewer to report that the brief is
  wrong** — that is what surfaced the second one.

- **A FALSIFICATION PROBE CAN ITSELF BE THE DEAD INSTRUMENT, AND ITS SILENCE READS AS A PASS.**
  A-045: to prove the new verifier stage could turn the gate red, I appended a deliberately
  failing test to `verifier/test_verifier.py` and ran the gate. **It printed GATE PASSED.** The
  correct reading was not "the wiring is broken" — it was that `unittest.main(verbosity=2)` is
  the last statement in that file, so a class appended *after* it is defined only after
  `sys.exit()` has already fired and **never runs at all**. The probe tested nothing; the test
  count stayed at 146 and I had not looked. Had I injected the probe and seen GATE FAILED for
  some unrelated reason, or skipped the probe entirely on the grounds that `|| fail=1` is
  obvious, the stage would have shipped with its wiring unproven either way. **Check that the
  probe MOVED SOMETHING — the count, the output — before you believe what its result implies.**
  Injected before the `__main__` block it ran (147 tests) and the gate went red correctly.
  **A-046 then measured the rate: FOUR of about twelve probes across the eight-guard
  falsification were vacuous, and every single time the GUARD was right and the PROBE was
  wrong** — a `sed` anchor absent from the file, a code injected outside the array the guard
  actually reads, prose where the guard searches for two literal labels, and a caveat probed
  against text the guard normalises for line-wrapping before comparing. **Each one produced a
  green guard that reads exactly like "this guard does not fire."** Assert that the edit
  applied and read the diff, every time; in this technique the probe is the unreliable half.
- **A REGRESSION TEST CAN PASS AGAINST THE DEFECT IT NAMES.** A-044: the first backpressure
  test I wrote pinned the deadlock my own repair could introduce, not the unbounded dispatch it
  was written for — it passed against the unfixed server. **Always run a new regression test
  against the PRE-FIX code and confirm it fails.** If it does not, it is testing your fix, not
  the defect.
- **A REPAIR CAN GENERALISE THE DEMONSTRATION INSTEAD OF THE ARGUMENT.** A-028 F1 fixed the
  branch its reviewer exploited and left the identical hole in the sibling branch two lines
  down, though the justification it wrote covered both. A second reviewer walked through the
  other half a year of commits later (A-043). **When you fix a defect, ask what the ARGUMENT
  covers, not what the reproduction touched.**
- **A COMMENT THAT DESCRIBES A VULNERABILITY AND CALLS IT A FIXTURE HAZARD.** A-028's test file
  says an unsupported selector means "the signer's own decode fails too, so bundle and signer
  honestly agree and nothing fires" — and routes around it to avoid a test passing for the
  wrong reason. That sentence IS the bypass, written down and filed as an inconvenience.
- **Fixtures chosen as "arbitrary bytes" are never arbitrary.** Eleven tests used an undecodable
  selector because they needed *some* calldata for tests about other things, and every one was
  passing through A-043's hole. They went red the moment it closed, which is the only reason
  the blast radius was visible. Use `decodablePurchaseCallData()`; say so explicitly when a
  test is genuinely about undecodable bytes.
- **A guard, a test or a mutation can exist and point at the wrong thing.** Three times this
  session: mutation anchors rotted when the code they targeted was rewritten (twice in one
  day); a leak guard built probes by pairing FILTERED words, so 10 of 17 could never match and
  the injection payload could pass; a canary matched `ATTACKER.slice(2,10)` — the address's HIGH
  bytes, all zeros — so every approval to `address(0)` was logged as an approval to the
  attacker. **Re-run the batch whose target you just edited.**
- **A negative test case can be the one input that cannot expose the bug.** The canary's
  negative was `0x1111…1111`, the only address containing no run of eight zeros.
- **Unit-testing a guard does not test that anything CALLS it.** Six of ten mutations against
  the injection wiring survived because every test drove the pure function and none drove the
  pipeline. Where behaviour cannot be reached, assert the STRUCTURE that produces it — read the
  caller's source, require the call site — and say in the test why.
- **A fall-through is a claim.** `verdictOf` had no treatment-arm validity check, so an arm that
  proposed *nothing* fell through to "RESISTED — the model still proposed the purchase".
- **A description a ruling rests on must describe the code.** D-034 quoted L2's doc comment as
  what decided the criterion, and L2 was carrying two checks from a different implementation.
- **Do not generalise a bound from a sample without sweeping the whole set for
  counterexamples.** A-033 claimed the channel "moved no label" from nine fixtures; the
  counterexample (F051) was already on disk, in a label's own note.
- **Measure the claim you just wrote.** The seeded gate profile is *nearly* reproducible, not
  reproducible — outcomes and call counts match, revert tallies differ by one on two of ten
  invariants. Caught before it reached a document.
- **A denylist matched by substring only catches the spellings it declares**; a name-based guard
  cannot catch a semantic leak; an allowlist exemption must be scoped to the DEPTH it was
  decided at.
- **Do not summarise ratified decisions for a labeller**, and do not reuse a sample across
  rounds.
- **A HANDLER ACTION MUST BE REGISTERED AS WELL AS WRITTEN, and forgetting it is silent.**
  D-042's two invariant arms were written, their non-vacuity test passed — it calls them
  directly — and the whole suite went green, while the mutation they were written for still
  survived, because `targetSelector` had not been told the new selectors existed. **The
  invariants existed and pointed at nothing.** Caught only by re-running the mutation instead of
  trusting the green suite. This is the project's most-repeated defect appearing *inside the fix
  for a finding about the same defect*.
- **A stateful campaign's coverage is bounded by what its handler can BUILD, not by its call
  count.** 262,144 calls that never construct a future nonce prove nothing about future nonces.
  Before D-042 the campaign killed nothing the 56 deterministic tests did not.
- **A clean `git status` is a statement about one instant, not a lock.** A-037: a second session
  committed between this session's check and its write, and the write silently clobbered it.
  The collision was caught only because both sessions picked the same letter. **Nothing in the
  repository can detect a second writer** — every guard here validates content, and content
  cannot tell you who produced it.
- **The corpus runner picks a random port and occasionally collides.** Re-run before diagnosing.
  Concurrent runs also contend — nine spurious failures came from a mutation sweep running
  beside the suite.

**What worked:**

- **Building an independent implementation from the SPEC ALONE and measuring it against a real
  artifact it had never seen** (A-042). Keep the two halves apart, and **declare what each
  outcome means before either finishes** — agreement means the spec is precise enough to build
  from, divergence is a spec gap. It resolved as divergence and named the exact clause. **The
  spec text was four days old and mine; the independent side found what I could not, because I
  could not un-know the implementation.** This is the only technique here that tests a
  DOCUMENT rather than code.
- **Writing a fixture's own falsification guard into the tool that emits it.** The refusal
  sample's spec carried "if the signer did not refuse, fail the run" — and it fired on the first
  attempt, catching that pausing before evaluation produces a BLOCK the signer will happily
  attest. A sample that exists to demonstrate X and silently does not is worse than no sample.
- **Adversarial review at a fixed commit, told to prove the work fails.** Four reviews, ~24
  material findings, several missed by the suite, the mutation harness and prior reviews. Give
  each a FROZEN tree — `git worktree add <scratch> <commit>` with `node_modules` symlinked
  works and lets you keep editing.
- **Requiring a provenance attestation from every labeller.** **Eight for eight** produced a
  first-order finding this way, unprompted: the harness-injected memory file (repeatedly), the
  specification-as-contamination-channel, the published reason codes, `failureMode`'s undefined
  encoding, the F026/F051 call-graph-hash contradiction, F056 not exercising reentrancy, and a
  labeller declining an injected instruction that would have breached the protocol.
- **Adversarial review of a GUARD, not just of code.** Two reviewers at a frozen commit produced
  twenty-five findings against two guards and the documents citing them — including that the
  certification check grepped the whole proposal while the comment beside it congratulated the
  author for having just fixed that exact defect in the function above. **Knowing about a defect
  class is not protection from it.**
- **Measuring a fork instead of arguing it.** D-033's control arm settled in one run what would
  otherwise have been unfalsifiable — then produced the counterexample that corrected A-033.
- **Single-variable experiment design.** H varied only the spec text; J varied only the model.
- **Declaring the escalation threshold BEFORE seeing the result** (D-035: two movements).
- **Making a guard state what it cannot check.** `check-vendor-honesty.sh` fails on the
  mechanical conditions and reports the other two as UNCERTIFIED, never as a pass.

## 6. Environment facts

- **One agent session at a time on this tree (D-037, resolving A-037).** The ruling is live; the
  paragraph below is why it exists.
- **MORE THAN ONE AGENT SESSION CAN BE OPEN ON THIS TREE, AND NOTHING STOPS THEM COLLIDING.**
  It happened (A-037): two sessions ran D-035's control arm minutes apart and one overwrote a
  file the other had just committed. **`git status` clean and a directory listing are only true
  for the instant they run** — re-check immediately before writing, and prefer creating a file
  under a name nobody else could pick. Every guard in this repository checks the CONTENT of the
  tree and none can see a second writer.
- Foundry v1.7.1 at `$HOME/.foundry/bin` — **not on the agent's non-interactive PATH**.
  `scripts/mutate.sh` and `scripts/test.sh` export it themselves.
- Node v26.3.0, viem 2.55.10. The signer runs under Node's native type stripping: erasable
  syntax only, and relative imports need the `.ts` extension.
- `.env` is gitignored and holds `ANTHROPIC_API_KEY`. The pre-commit hook blocks it.
- **Claude Opus 5 rejects `temperature`/`top_p`/`top_k` (400).**
- **After ANY Solidity mutation — `scripts/mutate.sh` or a hand-rolled `sed` — `contracts/out`
  holds the LAST mutant's bytecode.** Run `forge build --force` before emitting samples, or the
  artifacts are signed against a deliberately broken vault. **THE SYMPTOM IS MISLEADING AND COST
  A DETOUR ON 2026-08-16: the gate reports `corpus: DIGEST MISMATCH — the committed labeller
  views are NOT what this code now produces`,** which reads as "your change moved the labelling
  views" — the re-label trigger — when the source is clean and only the build artifacts are
  stale. Check `git diff contracts/src` FIRST; if it is empty, force-rebuild before believing
  the mismatch.
- **The harness injects the workspace `CLAUDE.md` and John's `MEMORY.md` into every subagent.**
  Five labellers reported it; one declined an instruction inside it that would have breached the
  labelling protocol. This cannot be fixed from the repository — assume every labeller starts
  partly oriented, and keep asking for the attestation that surfaces it.

## 7. Verification tooling

`scripts/mutate.sh` — batches across signer, decoders, pipeline, evaluator, the D-012/D-014
rulings, the D-017 corrections, the step-7 transcriber (`P`), the ablation layers (`B`), the
corpus guards (`C`), and the vault (`S`, Solidity). Run `./scripts/mutate.sh C` for one batch or
`./scripts/mutate.sh C12` for one mutation. **Get counts by running it, not by grepping.**

### 7.1 The checkers, and which of them the gate actually runs (added 2026-08-19)

**Verified by reading `scripts/test.sh`, not by assuming — re-measured 2026-09-03 with
`grep -n "check-.*\.sh" scripts/test.sh`.** The table this section carried from 2026-08-19 listed
nine gate-run scripts and called `check-suite-floors.sh` hand-run; it is in
`docs/archive/session-state-history.md`. Today `scripts/test.sh` invokes sixteen distinct
`check-*.sh` scripts over seventeen invocation lines (`check-rename-gate.sh` is called on two
lines, `--gate` under the gate profile and plain otherwise); two more exist under `scripts/` and
nothing invokes them. That is the defect class in §0 — a claim about an instrument, stronger than
the check behind it — so count them in the script before quoting this paragraph.

**Run by the gate, both profiles** (a failure fails the gate; line numbers are `scripts/test.sh`
at `e73789d`):

| Script | `test.sh` line | Asserts |
|---|---|---|
| `check-gate-immutability.sh` | 216 | the gate executes an unlinked copy of itself; ten properties including an unprotected CONTROL that must be corrupted (D-057(3)) |
| `check-gate-abort-safety.sh` | 252 | gate abort safety (R-A018-25, D-084) |
| `check-secrets.sh` | 255 | secret guard (A-007) |
| `check-v1-index-ordering.sh` | 264 | `GIT_INDEX_FILE` is scrubbed before `git rev-parse --git-path index` (V-1, D-059(7)) |
| `check-rename-gate.sh` | 268 (`--gate`), 270 | publication visibility against `docs/publication-policy.state` (D-032/D-048/D-076) |
| `check-label-prompt.sh` | 274 | labelling-prompt freeze (D-011a) |
| `check-label-integrity.sh` | 281 | labelling artifacts pinned (A-064) |
| `check-type-strings.sh` | 284 | published EIP-712 type strings (D-023), scoped to §5.8 by section extraction |
| `check-eval-codes.sh` | 287 | §5.7.1 check coverage (D-031), scoped by section extraction |
| `check-class-coverage.sh` | 295 | corpus class coverage, on a RATCHET (A-036) — read its output |
| `check-vendor-honesty.sh` | 301 | §7.5 Gate 5 mechanical conditions (D-008); reports (1) and (3) as John's, never as a pass |
| `check-suite-floors.sh` | 304 | prints the floors read from `scripts/test.sh`, the only copy, and refuses a numeric copy in this file (R4-F4, D-058) |
| `check-release-sync.sh` | 510 | `release/` matches the assembler's output (R-A018-22) |
| `check-release-executes.sh` | 531 | the shipped verifier is executed, not only digested |

**Run by the gate, `--gate` profile only** (a cost decision, stated in the script; a fast run
prints what it did not check):

| Script | `test.sh` line | Asserts |
|---|---|---|
| `check-publication-suite-floors.sh` | 337 | publication-suite floors (R-A018-06/16 closure evidence, D-083(j)) |
| `check-test-vacuity.sh` | 340 | a PASSING test whose assertion never executed (R-A018-24) |

**Run by hand only — NOTHING invokes them** (each prints its own verdict and exits non-zero on
failure):

| Script | Asserts | Why it is not in the gate |
|---|---|---|
| `check-findings-ledger.sh` | derives every D-055(e) total from `FINDINGS-LEDGER.tsv` and asserts D-057(1)'s eight figures | bookkeeping for one spent review |
| `check-review-scope.sh` | every tracked file is assigned to R1/R2/R3; **fails closed** on an unresolvable base or a failing/empty `git ls-files` | **D-057(4): John ruled explicitly that the permanent product gate must not be made to depend on a spent review's scope.** Measured 2026-09-03: it already fails, with tracked files assigned to no reviewer; `docs/ARCHIVE-INDEX.md` and `docs/archive/*` lengthen that list, and extending its partition is a `scripts/` change outside the pruning pass |

Of the gate's own, two are worth knowing the shape of: **`check-gate-immutability.sh` asserts 10
properties including an unprotected CONTROL that must be corrupted** — if the control survives,
the harness is measuring nothing (§0). **`check-type-strings.sh` and `check-eval-codes.sh` scope
themselves to §5.8 and §5.7.1 by section extraction and fail closed if the section cannot be
isolated**, rather than grepping the whole proposal and reporting whatever they find.

**`FINDINGS-LEDGER.tsv` is the canonical one-row-per-finding record.** John ruled that grouped
counts must be labelled **"disposition items", never "findings"** — 23 finding IDs (22 confirmed,
1 refuted) are 20 disposition items (19 confirmed) when `R3-F5`–`R3-F8` are grouped as one
remediation cluster. **They remain four findings and four regression obligations.** Do not
hand-count; run the checker.

## History retained here (guard constraint)

The 2026-08-16/17 block below is historical and would have moved to
`docs/archive/session-state-history.md` with the rest, but `scripts/check-vendor-honesty.sh`
scans every tracked or untracked-not-ignored file and exempts seven paths by exact name
(`scripts/check-vendor-honesty.sh` line 151 — this file, `HANDOFF.md`, `docs/decisions.md`,
`docs/gate-5-vendor-audit.md`, `docs/v1-1-register.md`, `Sentinel_Lab_Proposal_v0_2.md`, and the
guard itself); `docs/archive/` is not among them, and the block quotes a vendor name in two casings as
A-047's case-sensitivity example; it stays here, unedited, so that no guard is changed and
nothing moves through one.

**A-046 falsified all eight guards and reported "8/8 caught, 0 defeated". THAT HEADLINE WAS
WORTHLESS AND A-047 IS THE CORRECTION.** An independent reviewer, told to defeat a guard rather
than to confirm one, produced **seven confirmed defeats within hours** — every one a violation of
a guard's own stated purpose that the guard does not catch. A-046 stated the bound ("each guard
fires on the violation it was pointed at; it says nothing about violations nobody imagined") and
that bound turned out to be the entire story, not a footnote. **Falsifying an instrument against
the violation you designed it for measures your imagination, not the instrument.** The technique
is still worth running — it is cheap and it caught real things — but its output is a floor, and
reporting a floor as a headline is the honesty defect this project exists to study.
**Fixed under A-047 (John scoped it):** the corpus stage never hashed the committed view files at
all, so tampering one passed while the gate printed "committed views semantically current" — the
provenance claim the corpus rests on; and the vendor scan was case-sensitive while the label scan
beside it was not, so `| coinbase |` passed and `| Coinbase |` failed. **Recorded, not fixed:** the
unscoped spec greps, three secrets-guard holes, the rename gate's second-remote and trailing-slash
gaps, the class-coverage laundering route through committed `results/`, and — **omitted from this
list until 2026-08-17, though A-047's own entry calls it "A GENUINE HOLE THAT REMAINS" — that A
GREEN SUITE IS NOT A CORRECT VERIFIER:** neutering the `evidenceHash` check by hand left all
146 tests passing and all 7 samples verifying, because no tamper mode corrupted `evidence.hash`.
**CLOSED 2026-08-17 (A-049): the `evidence-hash` mode mutates the PUBLISHED hash rather than the
canonical bytes, so it isolates that one check, and the same neutering now produces 12 failures.**
The generalisation is NOT closed — **A DIRECTED SWEEP HAS NOW RUN (A-051)** over the SIX other modules — the count in this
sentence read *five* and omitted `jcs.py`, an error that reached three documents and the sweep's
own brief. 142 mutations applied, **41 survived a green gate**; three verdict-flippers are closed
and the rest are in the register. `verify.py` — 1681 lines, the file that decides the verdict —
remains unswept, and that is now the largest MEASURED gap rather than an assumed one.
See `docs/v1-1-register.md` §8.

---

*Entries below predate 2026-08-15 and are unchanged.*

## 8. Pre-existing traces

- **Do not make non-vacuity an `afterInvariant` hook.** Foundry shrinks to a minimal sequence,
  and any one-call sequence has zero executions by construction.
- **Do not randomize every dimension inside one invariant handler action.** 16,384 calls, zero
  executions, all invariants PASS.
- **`forge` caches invariant failures in `contracts/cache/invariant/`.**
- **A `// forge-lint: disable-next-line(...)` directive must be the line immediately before the
  code.**
- **`Promise.all([f(await g()), f(await h())])` is NOT concurrent.**
- **A socket-level test cannot observe the signer's reserve-versus-sign ordering.**
- **Do not measure mutation results by parsing the `node:test` reporter.** Use exit status.
- **`check-secrets.sh` scans TRACKED files** (`--staged` after `git add`);
  `check-vendor-honesty.sh` scans tracked AND untracked-but-not-ignored.
- **Do not run an adversarial review while still editing the tree.** Freeze, then review.
- **A mutation set written by the implementer probes only the checks the implementer already
  thought about** — and inherits its author's blind spots even when the author is a reviewer.
