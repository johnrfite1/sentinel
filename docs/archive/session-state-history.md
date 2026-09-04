# Session-state history (archived 2026-09-03)

This file holds the dated status blocks moved out of `docs/session-state.md` on 2026-09-03 under D-093(c), verbatim — nothing was edited in the move, struck passages stay struck — ordered newest first by each block's own date (ties in original line order), each under a heading giving its original line range in that file at `e73789d`. One historical block did not move: the 2026-08-16/17 A-046…A-051 block stays at the tail of the live file under a guard constraint (`scripts/check-vendor-honesty.sh` exempts the live file by name and would scan this one). The map is `docs/ARCHIVE-INDEX.md`.

---

### 2026-09-03 — `docs/session-state.md` lines 6–9 at `e73789d`

[The header's Last-updated line as it stood before this pass. Line 8 names two Quench handoffs; four exist — `-3.md` (D-095) and `-4.md` (D-096). Not corrected here; the live header now names all four.]

Last updated: **2026-09-03 (D-093–D-096: the Quench on `8dfaa27` is ANSWERED — every register assumption disposed — 1, 4, 5 accepted on one
unaided cold read, MSG-041; 2 amended to the architecture, Plausible; 3 and 8 accepted; handoffs at
`docs/quench-orchestrator-handoff.md` and `-2.md`; the Quench artifact is
`8dfaa27`, pushed as backup; publication is not authorised; licence DEFERRED).**

### 2026-09-02 — `docs/session-state.md` lines 10–11 at `e73789d`

~~Last updated: 2026-09-02 (Cycle 3 returned on `81edee1` with zero sustained Criticals; D-092 recorded;
the D-092 narrow patch has LANDED in this commit, verified, named by parent and subject below; publication is not authorised).~~ — superseded.

### 2026-09-02 — `docs/session-state.md` lines 12–13 at `e73789d`

~~Last updated: 2026-09-02 (the final Cycle 3 candidate is `81edee1`, PUSHED to the PRIVATE remote as
backup under D-091(d); D-090 and D-091 recorded; publication is not authorised).~~ — superseded.

### 2026-09-02 — `docs/session-state.md` lines 93–110 at `e73789d`

[Cut from the `>` blockquote headed "READ THIS BEFORE ANYTHING ELSE" that stood at lines 28–196; the `>` prefix is original.]

> **2026-09-02 (Cycle 3 returned) — ZERO SUSTAINED CRITICALS ON `81edee1`; D-092 RULES A NARROW
> PATCH BEFORE THE QUENCH; THE PATCH HAS LANDED IN THIS COMMIT.** The Adversary measured both clauses of its
> withdrawal condition and reported HOLDS; it raised no provisional Critical, so the ledger closed
> with zero sustained Criticals (MSG-034). Subtractor, Catalyst and Conscience reported FAIL on
> `README.md:234` — a fenced command running the frozen packet verifier on a BLOCK bundle,
> `=> PASS` / exit `0` — graded a Major residue by the Adversary. Eighteen findings in all. D-092
> rules a narrow patch, (a)–(g), before the Quench: the Historical section keeps no runnable
> command; the packet note moves above the packet's commands; `verify.py` gains a host-clock
> executability classification; `[PASS]`-line and `--tamper` wording; the no-manifest limitation
> stated in the README; and the Conscience Major 3 / Major 5 corrections to this file, `HANDOFF.md`
> and the README's entry paragraph. D-092 also binds two build-team errors: a candidate's status
> documents land in the SAME commit as its code, and nothing in the README's Historical section may
> be copy-pasteable. **Patch status: LANDED in this commit and independently verified — D-092(c), (d), (e) HOLD under two fresh verifiers (`docs/cycle-3-patch-return-note.md` §5); suite 252 → 278, fast gate PASSED at floor 278; sync and execution guards clean.
> The patch commit is the child of `02458d2` on `step-3/isolated-signer`, subject beginning `D-092 patch`; measure it with `git log --oneline 02458d2..HEAD`. This block is IN that commit, which is why it names no SHA.** Then fresh agents reproduce every chair's
> failing command on the new SHA, a short return note maps each finding to its change, and the
> Smith takes the Quench decision on that SHA without a further cycle (D-092(g)). No push,
> publication, visibility change, gate signature or Critical withdrawal is authorised by D-092;
> licence DEFERRED (D-082(c)).

### 2026-09-02 — `docs/session-state.md` lines 112–122 at `e73789d`

[Cut from the `>` blockquote headed "READ THIS BEFORE ANYTHING ELSE" that stood at lines 28–196; the `>` prefix is original.]

> **2026-09-02 (earlier; superseded as latest by the block above) — THE FINAL CYCLE 3 CANDIDATE IS `81edee1a770648345401ea782b4928c382d3602f`, PUSHED AS BACKUP (D-091(d)).**
> John ruled the three forks below (D-091): §5.5.1 refusal records EXTENDED into the contract —
> `verify.py` now reports a signed refusal record as `=> AUTHENTIC, NOT EXECUTABLE`, exit 3, built
> test-first in a second lane (`TestExitContractD091`, 13 tests, suite 239 → 252, floor raised) and
> verified by a third independent agent (HOLDS; vacuity checked empirically, 10/14 red against the
> old code); the `[PASS]` diagnostic lines STAND, disclosed; the packet note STANDS. `--all
> fixtures/samples` lists five NOT EXECUTABLE bundles (at `81edee1`; seven since D-092(c)). Gate PASSED at floor 252; guards clean.
> Return note `docs/cycle-3-return-note.md` names `81edee1` as the candidate to file. Orchestrator
> brief drafted for John's review at `docs/cycle-3-orchestrator-brief.md`. ~~**Next external
> event: the orchestrator files D-090 as the SMITH DECISION and Cycle 3 runs on `81edee1`.**~~
> **Happened — Cycle 3 ran and returned; see the block above and D-092.**

### 2026-09-02 — `docs/session-state.md` lines 124–139 at `e73789d`

[Cut from the `>` blockquote headed "READ THIS BEFORE ANYTHING ELSE" that stood at lines 28–196; the `>` prefix is original.]

> **2026-09-02 (later) — THE FIRST CYCLE 3 CANDIDATE WAS `0bc79a8373ec26398702b47430da48134e7cbfe6`** (superseded by `81edee1` above).
> Cycle 2 closed both Cycle 1 Criticals and sustained one new one — the first surface routed to
> `verify.py`, which returned PASS/exit 0 on BLOCK (D-090). Route (a) taken: `verify.py` now
> reports BLOCK or un-overridden REVIEW as `=> AUTHENTIC, NOT EXECUTABLE`, exit 3 (the `gpgv`
> model), test-first (`TestExitContractD090`, 18 tests, 221 → 239); root README rewritten with the
> entry-point paragraph at the top and ~~every pre-Historical command through
> `verify_publication.py`~~ (**corrected 2026-09-02 under D-092, Conscience Major 3:** every fenced *verifier*
> command before the Historical section is `verify_publication.py`; one inline measured `verify.py`
> example remains under "Two verifiers, two claims" and exits 3; after D-092(a) the Historical
> section carries no runnable command); the D-010 walk requires exit 3. Fast gate PASSED; 239 · 104/105 · 61 ·
> 53; sync and execution guards clean. Independently verified, both clauses HOLD (29 commands);
> three stale passages asserting the old behaviour found and fixed, one of them the shipped
> `verify_publication.py` docstring, one a dated additive note in the Gate 8 packet's README
> (reversible). Return note `docs/cycle-3-return-note.md`; register §8. **Forks for John:** §5.5.1
> refusal records still PASS/0 on `verify.py`; per-check `[PASS]` lines; the packet note. **Not
> pushed — a push is John's, for this named SHA, after verifying PRIVATE.** Withdraws nothing.

### 2026-09-02 — `docs/session-state.md` lines 141–147 at `e73789d`

[Cut from the `>` blockquote headed "READ THIS BEFORE ANYTHING ELSE" that stood at lines 28–196; the `>` prefix is original.]

> **2026-09-02 — THE CYCLE 2 CANDIDATE IS `cb124feaad6b925f683b0739de53970e1700e146`.** Built under
> D-086/D-087 with test-first separation; fast gate PASSED; 104/105 · 61/61 · 53/53 · 221/221 ·
> 557/557 · 105/105; every guard clean including the new `check-release-executes.sh`. Return
> package for the council at `docs/cycle-2-return-package.md`. F-2 ruled exempt (D-088). ~~Nothing
> pushed~~ **PUSHED 2026-09-02 at John's explicit direction (D-089) to the PRIVATE remote — backup,
> not publication (D-044(a)); visibility verified PRIVATE before the push.** Repo PRIVATE; licence
> DEFERRED. The lab casting's Cycle 2 is the next external event.

### 2026-09-01 — `docs/session-state.md` lines 14–16 at `e73789d`

~~Last updated: 2026-09-01 (the Cycle 2 candidate is IN BUILD under D-087; D-085 and D-086
recorded; the BLOCK→PASS defect named below is FIXED at `8d47a0b`; publication is not
authorised).~~ — superseded.

### 2026-09-01 — `docs/session-state.md` lines 49–57 at `e73789d`

[Cut from the `>` blockquote headed "READ THIS BEFORE ANYTHING ELSE" that stood at lines 28–196; the `>` prefix is original.]

> **CURRENT NARROW INSTRUCTION (2026-09-01, D-087 and the Smith's build instruction that
> followed it):** build ONE Cycle 2 candidate of ~35 items — the §5.6 evidence-projection arm,
> the reason-code arm, the four Vault-axis items, §5.7.1 conformance named "signer-attested
> record conforms to mandate", the A/B semantic split stated on both verifiers, the §5.5.1
> refusal arm recognised and refused, release packaging per D-085(f), and the 2026-08-30
> round's confirmed findings — for the chairs to review as one SHA. Test authors and
> implementers work in separate lanes; `release/` is assembled ONCE at the end by the
> coordinator, never mid-batch (that is how a pre-repair verifier shipped last time). No
> commit, push, gate signature, Critical withdrawal or publication is authorised by it.

### 2026-09-01 — `docs/session-state.md` lines 75–91 at `e73789d`

[Cut from the `>` blockquote headed "READ THIS BEFORE ANYTHING ELSE" that stood at lines 28–196; the `>` prefix is original.]

> **2026-09-01 — THE REPAIR BATCH LANDED, D-085/D-086/D-087 ARE RECORDED, AND THE CYCLE 2
> CANDIDATE IS IN BUILD.** Four commits since the block below was written: `8d47a0b` (the
> publication-surface repairs and the state-aware publication gate — the BLOCK→PASS defect is
> fixed there), `5d93850` (R-A018-18/23/24 closed under D-083; guards wired), `5c8c090` and
> `2318ae3` (the gate's silent-abort defect, D-084). Then three rulings: **D-085** reversed
> D-083(h) — D-047 is retired, D-055(a) governs, the agent's error is recorded — and replaced
> one-at-a-time finding with a systematic inventory diff, which measured the class at
> **54 + 4 + 4 missing checks, not 6** (`docs/check-inventory-diff-2026-08-31.md`); **D-086**
> fired D-083(d)'s release condition, so the fail-open `deployment.verify(evaluation_time=None)`
> default is FIXED-not-marked and the lab casting's Binding Critical 2 closes by the
> non-certifying-static route, with Binding Critical 1 already closed at `5d93850` and needing
> demonstration; **D-087** scoped the next candidate to ~35 items and ruled §5.7.1 (port the
> attested-record comparison, named precisely), the A/B split (stated on both verifiers;
> ~~`verify.py` discloses it has no clock~~ — amended D-092(c): it classifies against the unauthenticated host clock), and the §5.5.1 arm (recognise and refuse). **Two
> Crucible lines, do not conflate them:** the enforcement-publication line's four A-018
> Criticals are still OPEN AT ANVIL (D-083(i)); the lab casting is HALTED pending the new SHA.
> The block below is struck where it is now false and otherwise stands.

### 2026-09-01 — `docs/session-state.md` lines 396, 398 and 408 at `e73789d`

[Three lines of the ADDENDUM 2026-09-01 table, which itself stays in the live file, as they stood before this pass: the heading and intro line, which referred to the 2026-08-29 table now archived above, and the D-092 patch row, whose bold clause was written twice. The live lines were edited to remove the dangling reference and the repetition; the originals are here.]

### ADDENDUM 2026-09-01 — what has moved since the table below was written
The table below is the 2026-08-29 record and is left as written. Since then:
| D-092 patch | **LANDED, verified** — narrow, (a)–(g), before the Quench; the child of `02458d2`, subject `D-092 patch …`. Code and status documents land in ONE commit. **child of `02458d2`, subject `D-092 patch …`; LANDED and verified.** No code change is claimed landed |

### 2026-08-30 — `docs/session-state.md` lines 149–159 at `e73789d`

[Cut from the `>` blockquote headed "READ THIS BEFORE ANYTHING ELSE" that stood at lines 28–196; the `>` prefix is original.]

> **2026-08-30 — THE CRUCIBLE LINE IS HALTED; A REMEDIATION SET IS PROPOSED, ~~NOT AGREED AND NOT
> STARTED~~.** **Corrected 2026-09-01: it was not agreed as a register, but its §3 items were
> authorised one by one (D-082(a), D-083(j), D-085(f), D-086, D-087) and most are now CLOSED
> with dated markers; §4 is still John's.** All four Cycle 2 Criticals were Adversary-SUSTAINED at `A-018` / `MSG-022` and remain
> **OPEN AT ANVIL**. A build-team response and reply were drafted and the chairs consulted
> informally. **That consultation made no ledger entry, no repository change, and no ruling.
> Nothing is "agreed" or "accepted" in any ratified sense**, and an earlier version of this block
> said otherwise. The proposal lives at **`docs/a018-remediation-register.md`** — read it before
> touching the publication surface. It authorises nothing; its §3 items are valid **only if the
> v0.3 enforcement/verifier architecture is retained** and still need an instruction, and its §4
> items are blocked on John.

### 2026-08-30 — `docs/session-state.md` lines 161–168 at `e73789d`

[Cut from the `>` blockquote headed "READ THIS BEFORE ANYTHING ELSE" that stood at lines 28–196; the `>` prefix is original.]

> ~~**THE DEFECT: the shipped `verify_publication.py` prints PASS and exits 0 for a receipt whose
> verdict is BLOCK**~~ (register §1.1, reproduced 2026-08-30) — **FIXED at `8d47a0b` the same
> day; struck, not deleted, because the push-status record that follows is still true.** **IT IS NOT PUSHED.** `a38cff9`
> exists only in the local working tree; `origin/step-3/isolated-signer` is at `70f4b4d` and no
> remote ref contains it. An earlier version of this block inherited a "pushed branch" claim that
> was false — prevention work, not incident response. **Four build-team claims were wrong and are
> corrected in the register's §0** (the push status, the Conscience attribution, "valid under
> every branch", and the licence wording), plus the two earlier self-corrections now at §1.2–§1.3.

### 2026-08-30 — `docs/session-state.md` lines 170–177 at `e73789d`

[Cut from the `>` blockquote headed "READ THIS BEFORE ANYTHING ELSE" that stood at lines 28–196; the `>` prefix is original.]

> ~~**The publication scope fork is unresolved, and its constitutional precondition has not been
> ruled:**~~ **RULED 2026-08-30 at D-083(a) and D-083(g):** the candidate is the `a38cff9`
> lineage repaired, custody RETAINED with the drain disclosed, audience = technical evaluators,
> venue = GitHub public (visibility unchanged, HELD_PRIVATE), and the lab branch REQUIRES A FRESH
> CASTING — the chairs' informal reading is that an Override-in-Writing can authorise proceeding
> despite unresolved Criticals but **does not rewrite the Ingot's acceptance or kill conditions**,
> and John ruled that reading rather than merely leaning on it. That casting is
> `S-20260830-sentinel-conformance-lab-r1`.

### 2026-08-29 — `docs/session-state.md` lines 17–20 at `e73789d`

~~Last updated: 2026-08-29 (Crucible Cycle 2 implementation checkpoint authorised / D-081;
candidate implementation verified and awaiting its authorised local commit; publication is not
authorised).~~ — superseded; left visible because four commits and three rulings landed under
that date line before it was corrected.

### 2026-08-29 — `docs/session-state.md` lines 59–73 at `e73789d`

[Cut from the `>` blockquote headed "READ THIS BEFORE ANYTHING ELSE" that stood at lines 28–196; the `>` prefix is original.]

> ~~**CURRENT NARROW INSTRUCTION (D-081):**~~ **spent at `a38cff9` (2026-08-29); kept for the
> record of what that candidate was.** Implement the three Crucible withdrawal conditions,
> create one local Sentinel commit, and record its immutable SHA in the Crucible session ledger.
> This instruction does not ratify Cycle 2, withdraw any Critical, authorize publication, change
> repository visibility, or authorize a push. The candidate adds SentinelVault enforcement,
> owner-signed signer authorization, exclusive clock checks, an out-of-band authenticated signed
> deployment manifest, a key-free generated release, and a cold exact-call/mismatch/replay demo.
> The fast canonical gate passes. The v0.3 corpus runner executes all 50 fixtures, but the deep
> provenance comparison correctly refuses the historical v0.2 corpus: adding the signed `signer`
> field changes all 50 labeller views and F035 moves from evaluator ALLOW to BLOCK. Those frozen
> labels were not silently regenerated or repinned; any v0.3 relabelling/ruling remains outside
> this implementation instruction and belongs to the Cycle 2 decision process (A-111).
> The private comprehension samples and generated reviewer packet were regenerated on the v0.3
> mandate/domain schema, remain fixed-key private fixtures, and are excluded from `release/`.
> D-080's Gate 8 result belongs to their predecessor v0.2 packet; no Gate 8 rerun is claimed.

### 2026-08-29 — `docs/session-state.md` lines 412–428 at `e73789d`

[The 2026-08-29 table that the ADDENDUM 2026-09-01 in the live file extended.]

### WHERE THE PROJECT IS, 2026-08-29

| | |
|---|---|
| Gates | **S1 SIGNED** 2026-07-28 · **S2 SIGNED** 2026-08-16, both by John (D-002 non-delegable) |
| Review arc | **COMPLETE.** Rounds five and six adjudicated; D-055(e) ran four reviewers, 23 findings, one CRITICAL in the gate itself; D-057 ruled every one |
| Remediation | **A-081 reverified 11 items — 3 held, 8 FAILED.** The convergence reset (D-058/059/060) replaced the method with batch cards. **Batch A1's two ordinary attempts BOTH FAILED and stay failed** |
| Batch A1 | **CLOSED — through the D-062 containment exception, NOT on the merits of either attempt.** One named regression repaired and independently verified HOLD. **Neither ordinary attempt is relabelled successful (D-061(4)).** |
| Confirmed D-058 batches | **HOLD**, each inside its card: A-EXTRACT (A-089), B-EVENTS (A-091), C-SNAPSHOT (A-093), A-FLOORS (A-094), D-CLAIMS (A-095) |
| D-055 exit | **MET (D-073, Session Six).** Unlocks nothing. D-048: a clean result is a PRECONDITION, never a trigger. Census of record: `critical-high-census.md`. Exit record: `d055-condition-status.md`. V-3 accepted as a documented boundary at `scripts/check-secrets.sh` 148–152. D-067 D-008(2)/(4) limits HISTORICAL. Gate 5 not recertified. |
| 2026-08-23 Phase B | **ACCEPTED.** Frozen at A-101. D-069–D-072 recorded. A-100 dispositions both frozen-harness control failures. D-067 §7.2 sentence untouched; D-008(2)/(4) limits now HISTORICAL at D-073 |
| 2026-08-24 record stretch | **FROZEN at A-104.** D-073 recorded. Census and dossier are the exit record. Isolated verified-origin `--gate` is after that freeze, out of tree |
| 2026-08-25 Session Eight | **Name ratified "Sentinel" (D-074).** D-016 naming block lifts. Domain-string ruling recorded (D-075). Rename-gate re-scoped Option A (D-076). **Gate 8 packet assembled (D-077); the run is not started** |
| 2026-08-25 Session Nine | **Packet corrected (D-078)** from a cold pre-read (not Gate 8). Case 2 pull fixed; honest limits stated; handoff zip is four artifacts. **D-014 annotated (D-079)** — phrase clarified, ruling and behaviour unchanged. **The run is still not started** |
| 2026-08-25 Session Eleven | **Gate 8 PASSED (D-080), with three limits recorded beside the result.** Four findings ruled FIX. The packet and record corrections are frozen at A-110; signed bundles were not regenerated. |
| Next | **Nothing without John's next instruction.** No publication, preparation toward it, visibility change, public URL, push, gate signature, Gate 8 rerun, or request for the held questions. |
| Publication | **NOT AUTHORISED.** D-055 MET and Gate 8 PASS are D-048 preconditions, never triggers. D-016's naming block has lifted. Publication remains a fresh decision John has not taken. |

### 2026-08-25 — `docs/session-state.md` lines 24–26 at `e73789d`

**WORKING TREE AT THE START OF THIS STRETCH:** clean at the A-109 freeze.
Count what is unpushed with `git log --oneline origin/step-3/isolated-signer..HEAD`;
no push is authorised. `.serena/` remains gitignored.

### 2026-08-25 — `docs/session-state.md` lines 28–47 at `e73789d`

[Cut from the `>` blockquote headed "READ THIS BEFORE ANYTHING ELSE" that stood at lines 28–196; the `>` prefix is original.] [This is the blockquote's opening paragraph, the 2026-08-25 framing; its prohibitions are restated in the live file's current block.]

> ## READ THIS BEFORE ANYTHING ELSE
>
> **YOUR JOB IS NOTHING WITHOUT AN INSTRUCTION FROM JOHN.** D-055 is MET (D-073).
> **A MET D-055 unlocks nothing.** D-048 makes a clean result a PRECONDITION, never
> a trigger. **D-016's naming block has lifted (D-074). That is not publication
> permission.** Gate 8 passed under D-080 with three limits recorded beside the result:
> the questions mirror README headings; the dashboard was read as source, not rendered;
> and reviewers read verifier source. Passing removes a named pre-publication condition
> and authorises nothing. The private packet at `reviewer-packet/` is assembled for a
> private handoff (D-077), corrected (D-078), and carries D-080's four finding fixes.
> D-014's summarising phrase is annotated (D-079), not rewritten. The packet carries the EIP-712 domain name as a signature
> preimage and renders it under **Cryptographically bound** on every case screen;
> calling it "name-agnostic" was **false** — John's recording error, Session Eight,
> not a discovery. No gate is signed or reopened. Do not publish, change repository
> visibility, post a demo, or prepare any of it. A1 is closed:
> **no A1 reopening and no further A1 production change is authorised.** The
> 2026-08-23 lift of the "no further A1 test" clause remains **spent** at the
> F61ECCA card freeze. The D-058 confirmed batches independently HOLD.
> **The Icon line in `README.md` is kept.** Report the state
> below and wait.

### 2026-08-25 — `docs/session-state.md` lines 205–236 at `e73789d`

[The reading order this passage gave is replaced by `docs/ARCHIVE-INDEX.md`.]

**READING ORDER FOR A FRESH INSTANCE.**

1. **§1 below** — what happened, what is open, what is not yours to do.
2. **§0 below** — how this project fails. The most reused page in the repository.
3. **`docs/decisions.md`: D-058, D-059, D-060, D-061.** The convergence reset. **D-060(1)
   ABANDONED the global repair-contract method; D-061(4) closes Batch A1 with no third
   attempt.** D-055(a) remains the governing exit criterion and D-048 still makes a clean
   result a PRECONDITION for pre-publication, never a trigger.
4. **`docs/review-2026-08-19-d057-targeted/README.md`** — the evidence directory's own map. It
   explains why there is no active global contract and what a batch card is.
5. **`.../batch-cards/A2-tests/VERIFICATION-2.md`** — why Batch A1 failed. Read it before
   proposing anything about the entry points.
6. **`docs/decisions.md`: D-062, D-063, D-064**, then
   **`.../batch-cards/D062-containment-tests/`** — the containment exception that closed the one
   named regression. `CARD.md` is the contract, `VERIFICATION.md` is the independent verdict and
   **§10 is the authoritative residual list**, and `IMPLEMENTATION.md` is the implementer's own
   claim rather than evidence. **D-063 withdrew standing force authorization: any forced removal
   now needs new, exact approval after every stated precondition holds.**
7. **`docs/decisions.md`: D-066, D-067, D-068, D-069, D-070, D-071, D-072, D-073, then A-089, A-091, A-093, A-094, A-095, A-096,
   A-097, A-098, A-099, A-100, A-101, A-102, A-103, A-104, D-074, D-075, A-105, D-076, A-106,
   D-077, A-107, D-078, A-108, D-079, A-109, D-080, A-110, D-081, A-111.** D-073 records that D-055 is MET
   and that it unlocks nothing. D-067's D-008(2)/(4) completeness limits are HISTORICAL as of
   D-073; the §7.2 admissibility sentence is untouched. Gate 5 is not recertified. A-104
   froze the exit record. D-076 re-scopes the visibility gate and amends D-071's citation
   only. D-077 retitles the live gate heading and assembles the Gate 8 packet. D-078 corrects
   that packet from a cold pre-read. D-079 annotates D-014's summarising phrase without
   rewriting D-014. D-080 records the Gate 8 pass with all three limits and orders four fixes;
   A-110 records those fixes and the freeze. Publication remains a fresh decision John has not taken.
   **Do not treat MET as publication, rename, a gate signature, or a follow-on plan.**
   The exit record is
   `docs/review-2026-08-19-d057-targeted/d055-condition-status.md`. The census of record is
   `docs/review-2026-08-19-d057-targeted/critical-high-census.md`.

### 2026-08-25 — `docs/session-state.md` lines 464–491 at `e73789d`

### WHAT IS STILL OPEN, AND NONE OF IT IS THIS INSTANCE'S TO CLOSE

1. **Publication, any preparation toward it, any Gate 8 rerun, and any gate signature or reopening.**
   D-055 MET and the D-080 Gate 8 pass start none of these. D-016's naming block has lifted
   (D-074). The packet is assembled (D-077), corrected (D-078), and carries D-080's finding fixes.
   D-014 is annotated (D-079). The five D-008 comprehension questions stay unseen.
   `scripts/check-rename-gate.sh` is re-scoped under D-076 (visibility still PRIVATE; citation is now D-032 / D-048 / D-074). That is not publication permission.
2. **RESIDUALS FROM THE D-062 VERIFICATION — scored, not all repaired.**
   **`V-1` is retired under D-073** (A-098 verified repair) and remains load-bearing as
   stated in the header. **`V-3` is accepted as a documented boundary** at
   `scripts/check-secrets.sh` 148–152. **`R-C` is retired under D-073** (D-072 pin;
   coverage explicit in the census). **`V-2` through `V-10` otherwise** — read them in
   `docs/review-2026-08-19-d057-targeted/batch-cards/D062-containment-tests/VERIFICATION.md` §10
   and `RESIDUAL-SEVERITY.md`. Copying their prose into this file is how this file has
   drifted before.
3. **RESIDUALS AFTER THE 2026-08-23 SESSION AND PHASE B.** `R3` is **DISPOSITIONED** as a
   permanent recorded limit; the frozen A1 harness is untouched (D-068(6)). `R5` is
   **repaired** as D-071 option C. `R2` and `V-6` are **closed at the D-072 pin**; the
   D-067 D-008(2)/(4) completeness limits are **HISTORICAL as of D-073**. D-067's §7.2
   admissibility sentence is untouched.
4. **Gate 5 supplementary §7.2 condition.** D-067 records that D-059(1)'s bar is **MET for that
   condition only**: `check-vendor-honesty.sh` is restored as admissible evidence for §7.2.
   **The Gate 5 certification is not revoked, reaffirmed, or recertified.** The D-008(2)/(4)
   limits no longer load-bear those scans. They never load-bore §7.2 (fixed paths, no
   `artifacts()`). An agent may not recertify the gate.
5. **Deferred items stay deferred** (disposition, D-059(2)): `exit-criterion-packet.md` §7;
   `NEW-FINDINGS.tsv` annotations; sanitization-manifest rows; harness-pin disposition;
   the three volunteered items. **Do not work them.**

### 2026-08-25 — `docs/session-state.md` lines 493–513 at `e73789d`

### WHAT IS WAITING ON JOHN — all of it is his

1. ~~**The `GIT_INDEX_FILE` fail-open.**~~ **CLOSED** under the D-062 exception — repaired at
   `4920213`, independently verified HOLD at `c163195`, accepted by John. **`V-1` is retired
   under D-073** (A-098 verified repair); the ordering remains load-bearing as stated in the
   header.
2. ~~**Whether Batch A1 is recarded.**~~ **RULED: it is not.** A1's closure is accepted and
   **no A1 reopening and no further A1 production change is authorised.** The 2026-08-22 lift
   of the "no further A1 test" clause was **spent** at the Phase 1 freeze that added the V-1
   behavioural guard; it is not standing permission.
3. ~~**Phase B of the 2026-08-23 stretch.**~~ **ACCEPTED, frozen at A-101.** D-069, D-070,
   D-071, D-072 recorded. **A-102 froze the post-B dossier refresh. A-103 froze the
   close-out stretch. A-104 froze the D-073 record.** The D-067 D-008(2)/(4) limits are
   HISTORICAL as of D-073.
4. ~~**The push.**~~ John pushed D-074 through D-078 himself. That backup authorisation is
   spent. Count anything outstanding with `git log --oneline origin/step-3/isolated-signer..HEAD`;
   **do not quote a number from this file.** An agent pushes only on John's explicit direction
   for a specific later state. The repository is still PRIVATE: backup is not publication.
5. **Publication, any preparation toward it, any Gate 8 rerun, any gate signature or reopening,
   and any follow-on stretch.** D-055 is **MET** and Gate 8 **PASSED with limits** under D-080.
   Those are preconditions, not triggers. Publication remains a fresh decision John has not taken.

### 2026-08-25 — `docs/session-state.md` lines 515–534 at `e73789d`

### WHAT IS NOT AUTHORISED, and none of it has changed

- **NO A1 REOPENING OF ANY KIND** — no third implementation attempt (D-061(4)), and no
  further A1 production change. The 2026-08-22 lift of the "no further A1 test" clause was
  **spent** at the Phase 1 freeze that added the V-1 behavioural guard. The 2026-08-23 lift
  of the same clause was **spent** at the F61ECCA card freeze (A-099). Neither is standing
  permission.
- **No follow-on because D-055 is MET.** No publication path, visibility change, public demo,
  push, v1.1 plan, or stretch unless John starts it. The private packet at `reviewer-packet/`
  is assembled for a private handoff (D-077), corrected (D-078), and carries D-080's finding
  fixes; it is not published. Gate 8 passed with its limits and may not be rerun without a new
  ruling. D-079 annotates a dated phrase; it is not a product change. No gate signed or reopened, no public claim certified, no
  correction ratified.
  A MET D-055 certifies nothing.
- **Publication is not authorised.** Gate 8 passed with limits under D-080; D-048 makes clean
  results preconditions, never triggers. The repository is PRIVATE. `scripts/check-rename-gate.sh`
  still checks origin visibility (D-076 Option A); D-071's substance is unchanged.
- **No preparation toward publication.** D-074's naming-block lift and D-080's pass are not triggers.
- **The five D-008 comprehension questions stay unseen.**
- **No push** without John's explicit direction for a specific state.

### 2026-08-24 — `docs/session-state.md` lines 187–196 at `e73789d`

[Cut from the `>` blockquote headed "READ THIS BEFORE ANYTHING ELSE" that stood at lines 28–196; the `>` prefix is original.]

> **`V-1` IS RETIRED UNDER D-073 via verified repair — A-098's behavioural guard,
> independent HOLD — and the ordering is still the thing to know.** `git rev-parse
> --git-path index` **honours `GIT_INDEX_FILE`.** The repair is therefore correct
> **only because both files scrub that variable BEFORE asking git for the canonical
> index path** (`.githooks/pre-commit` 39→86, `scripts/check-secrets.sh` 76→121).
> A-098 observes the hostile-export hole and is bound to both gate profiles.
> Reversing the ordering still reopens the hole; the guard is required to fail.
> **A MET D-055 does not make this paragraph optional.** `V-3` is John's explicit
> acceptance of the same-user TOCTOU already declared at `scripts/check-secrets.sh`
> 148–152, not a probe and not a repair.

### 2026-08-22 — `docs/session-state.md` lines 450–462 at `e73789d`

### WHAT THE CONFIRMED BATCHES CLOSED, AND WHAT THEY DID NOT

Each HOLD is completeness inside a declared boundary, not repository-wide closure.

1. **A-EXTRACT (A-089)** — section extraction, exact-membership, source-uniqueness, vendor-caveat.
2. **B-EVENTS (A-091)** — vault event evidence on both routes and truthful F7-R1 NatSpec.
3. **C-SNAPSHOT (A-093)** — signer snapshot-exhaustion classification.
4. **A-FLOORS (A-094)** — six suite floors, named-subject reader, one common gate invocation.
5. **D-CLAIMS (A-095)** — five comment / unsigned-prose surfaces. No signed-pack edit, no
   `RefusalRecord.detail`, no public reason-code split.

**A-081's eight FAILED items were the inventory those batches were built from.** Do not re-list
them as unrepaired current work. Do not treat the HOLDs as repository-wide closure.

### 2026-08-20 — `docs/session-state.md` lines 179–185 at `e73789d`

[Cut from the `>` blockquote headed "READ THIS BEFORE ANYTHING ELSE" that stood at lines 28–196; the `>` prefix is original.]

> **THE `GIT_INDEX_FILE` FAIL-OPEN IS FIXED — the warning that stood here is withdrawn.**
> It was real: clearing the variable made the pre-commit guard read `.git/index` while git was
> committing from a temporary index, so `git commit -am` and `git commit -- <path>` landed a
> credential in HEAD. **Repaired at `4920213` under D-062, independently verified HOLD at
> `c163195`, and confirmed live in this repository — both forms now block with the finding named
> and HEAD unmoved, while a benign `-am` still lands.** `git add` + `git commit` remains a
> perfectly good habit; it is no longer a workaround for a live defect.

### 2026-08-20 — `docs/session-state.md` lines 430–448 at `e73789d`

### HOW BATCH A1 ACTUALLY CLOSED — the record, stated so it cannot be rounded up

**Both ordinary implementation attempts FAILED** — `63c6906` and `f61ecca`, each independently
verified FAIL. **D-061(4) permitted no third, and none was made.** John then authorised **one
surgical containment exception (D-062) for the `GIT_INDEX_FILE` regression only** — explicitly not
a third general attempt, and reopening no other A1 finding or residual. That exception was run
test-first with the roles separate: independent test contract at **`c73b17a`** demonstrated
failing (7 REQUIRED, 0 CONTROL failures); the two-file repair at **`4920213`**; independent
verification by a third agent at **`c163195`** returned **HOLD**.

**A1 IS THEREFORE CLOSED THROUGH THE EXCEPTION, NOT ON THE MERITS OF EITHER ORDINARY ATTEMPT.**
Do not compress that into "A1 passed". It did not.

**Two A2 assertions were EXPRESSLY SUPERSEDED, never silently treated as passing.** The frozen
attempt-two harness fails exactly `B3-index` and `B4` against the repair, with **zero control
failures on two runs**, and **D-064 rules them superseded for the hook path only** — A2 is not
modified, not re-scoped, not relabelled. **The verifier independently confirmed exactly two
assertions moved and no third, so D-064's reversal condition did not fire; the rest of A2 remained
stable.**

### 2026-08-19 — `docs/session-state.md` lines 260–269 at `e73789d`

**The steps 1–3 review S2 was signed WITHOUT has since been run (D-044(b)).** It found A-043:
**a CRITICAL, exploitable bypass — a signed ALLOW obtainable for calldata nobody decoded,
reproduced twice onchain.** Fixed, with regression tests. Read A-043 and A-044 before trusting
anything about the signer. **`gate-s2-evidence.md` §11 is NOT empty** — this file once claimed it
was, twenty-two lines after telling a fresh instance to read it (`B-7`). It carries the pack's
stated limits plus **§11.0: findings John has ACCEPTED as limits rather than fixed — ten when
D-051(b) accepted them, and SIX today** (`D-07`, `D-09`(a),(b), `E5`, `F-VAULT-4`, `F-VAULT-5`,
`G-3`), five having been FIXED by A-076. **Read the derivation in §11.0; do not re-count by hand
and do not quote a count from here.** §11.0 twice mis-stated the remainder as five by dropping
`G-3` (`R4-F1`, CONFIRMED; corrected A-080).

### 2026-08-19 — `docs/session-state.md` lines 334–340 at `e73789d`

**WHERE THE PROJECT STANDS, 2026-08-19.** Round five (51 findings, 2 CRITICAL) is fully
adjudicated and remediated: three live security defects fixed, nine MEDIUMs fixed, ten accepted
as documented limits, two design forks with John. §7.1's containment claim — wrong twice — is
corrected, measured, asserted by a test, and **certified by John** (D-051(a)). Both corrections
are ratified and certified (D-054): the D-053(a) atomic-drain correction to §7.1, superseding
D-051(a) ONLY where the earlier wording is inconsistent with the atomic-drain boundary, and the
A-073 Gate 6 correction. **The S2 signature otherwise stands and no gate's status changes.**

### 2026-08-19 — `docs/session-state.md` lines 363–368 at `e73789d`

**IT RETURNED 23 FINDINGS: 22 CONFIRMED, ONE REFUTED — INCLUDING A CRITICAL IN THE
CERTIFICATION GATE ITSELF (`R1-F1`).** John ruled on all of them (D-057), countersigned three
independently reasoned severity downgrades, accepted three bounded limitations subject to T1
basis verification, and **ruled D-055's condition four NOT MET** — because `gate-s2-evidence.md`
§11's header claims post-signature text was signed. **A-077 repaired everything he ruled REPAIR;
A-078 was the independent targeted reverification of those repairs.**

### 2026-08-19 — `docs/session-state.md` lines 370–373 at `e73789d`

**A-078 IS THE ENTRY WORTH READING, BECAUSE IT IS WHERE MY OWN REPAIRS WERE DEFEATED.**
15 REPAIR-HOLDS, **3 REPAIR-FAILS**, 3 LIMIT-BASIS-CONFIRMED, and one new finding — every failure
the same shape: **the repair generalised the DEMONSTRATION and not the ARGUMENT.** All four were
then corrected and re-verified. See §1.

### 2026-08-19 — `docs/session-state.md` lines 375–378 at `e73789d`

**THE CERTIFICATION GATE IS NOW PROTECTED (D-057(3)).** `scripts/test.sh` executes an anonymous,
unlinked, read-only copy of itself under an external completion supervisor. Ten falsification
cases assert it, including an unprotected control that must be corrupted first. §1 says what you
must not undo.

### 2026-08-19 — `docs/session-state.md` lines 974–991 at `e73789d`

[§7.1's intro paragraph and its checker tables as they stood; the heading stays in the live file above a re-measured table.]

**Verified by reading `scripts/test.sh`, not by assuming.** The first draft of this table
asserted that none of these was wired into the gate; three of them are. That is the defect class
in §0 — a claim about an instrument, stronger than the check behind it — committed in the
section that lists the instruments.

**Run by the gate** (`scripts/test.sh`, both profiles; a failure fails the gate):
`check-gate-immutability.sh` · `check-secrets.sh` · `check-rename-gate.sh` ·
`check-label-prompt.sh` · `check-label-integrity.sh` · `check-type-strings.sh` ·
`check-eval-codes.sh` · `check-class-coverage.sh` · `check-vendor-honesty.sh`.

**Run by hand only — NOTHING invokes them** (each prints its own verdict and exits non-zero on
failure):

| Script | Asserts | Why it is not in the gate |
|---|---|---|
| `check-suite-floors.sh` | prints the floors read from `scripts/test.sh`, the only copy | it is a reporting aid; the floors themselves are asserted by the gate |
| `check-findings-ledger.sh` | derives every D-055(e) total from `FINDINGS-LEDGER.tsv` and asserts D-057(1)'s eight figures | bookkeeping for one spent review |
| `check-review-scope.sh` | every tracked file is assigned to R1/R2/R3; **fails closed** on an unresolvable base or a failing/empty `git ls-files` | **D-057(4): John ruled explicitly that the permanent product gate must not be made to depend on a spent review's scope** |

### 2026-08-18 — `docs/session-state.md` lines 342–346 at `e73789d`

**ROUND SIX THEN RAN AND RETURNED 91 FINDINGS, AND JOHN RULED IT NOT CLEAN (D-052(a)).** The loop
was paused (D-052(b)) to recut both the repair protocol and the terminating condition. **BOTH ARE
NOW DONE:** `docs/repair-protocol.md` binds every repair, and **D-055(a) has REPLACED D-047's
terminating condition** with a bounded, risk-based one. **There is no open-ended review loop any
more.**

### 2026-08-18 — `docs/session-state.md` lines 348–355 at `e73789d`

**A-075 (2026-08-18) FINISHED D-055(d)'S FOUR PREREQUISITES.** `E3` is BUILT — the signer's reads
are pinned to one block and the receipt's anchor bound to it, so an ALLOW anchored to a superseded
block is now refused where pre-fix it was SIGNED. Register §13.4's status column is corrected —
**22 of its 24 rows were wrong**, not the ~17 estimated. The ten limits accepted at that time
were T1-verified (**six remain accepted today** — see §11.0):
**eight bases held, `D-09(c)`'s was REFUTED, `G-5`'s was narrower than it read, `D-10` carried a
T2 severity discrepancy, and `H-5`/`H-8` were accepted with NO recorded reasoning at all.** Those
five were then closed by **A-076**, together with the gate-mutation protection.

### 2026-08-18 — `docs/session-state.md` lines 357–361 at `e73789d`

**THEN THE ONE BOUNDED REVIEW D-055(a) CALLS FOR ACTUALLY RAN (D-055(e), 2026-08-18).** Four
reviewers, scope fixed by John in advance (D-056(d)), each in its own worktree with its own
persistent evidence directory, at most two concurrent, every deliverable written to disk before
the reviewer was counted complete — **which closes round six's provenance gap, where reports
existed only in conversation.**

### 2026-08-18 — `docs/session-state.md` lines 571–612 at `e73789d`

This line published `507/507 TypeScript · 198/198 verifier` while the gate's own floors were
**513** and **209** — and it quoted `TS_MIN_TESTS=507` where the constant was 513, so a
maintainer reconciling the two would have LOWERED a floor, the one action `scripts/test.sh`
repeatedly forbids. **The figures are no longer duplicated here.** The gate constants are the
only copy, and `scripts/check-suite-floors.sh` prints them from the script itself, so this file
cannot drift from them again. That is the mechanical binding John required rather than a fifth
hand-correction of a line whose own text already said it "has been wrong four times".

**What is stable and worth stating: 50 corpus fixtures · workspace guards 0 NEW findings with
13 pre-existing baselined — it PASSES ON RATCHETED DEBT, which is not the same as clean.**
Values for the six floor dimensions are deliberately not repeated here; the checker derives
them from scripts/test.sh.
**AND SINCE A-075 THE FOUNDRY AND TYPESCRIPT FIGURES ARE FLOORS THIS GATE ASSERTS, which they
had never been before** — ratcheted in the same edit as the suites, and falsified (a shrunk suite
breaches; a `vm.skip`/`skip`/`todo` test is caught by a separate branch because the floor alone
does NOT see it; an absent report fails closed). So the sentence below — "there are still NO
floors on the Foundry or TypeScript counts" — **is no longer true and is struck.**

**THE FLOOR VALUES ARE DELIBERATELY NOT REPRINTED HERE.** This passage previously quoted
`FOUNDRY_MIN_TESTS=75, TS_MIN_TESTS=507` in present tense while the constants were 89 and 526 —
**eleven lines below its own claim that the figures are no longer duplicated in this file.** The
D-057(5) verifier found it and correctly ruled `R4-F4` REPAIR-FAILS: I had removed one copy and
left another in the same section. **Run `./scripts/check-suite-floors.sh`**, which reads them
from `scripts/test.sh`, the only copy.
*(Measured 2026-08-18 on the A-075 working tree by running `./scripts/test.sh` and reading its
output, not by copying this line. Post-D-052 arc: A-070 moved 180→188 verifier, A-072 the 189th, **A-074 189→198**;
A-072 moved 481→489 TypeScript and D-053 489→494. `VERIFIER_MIN_TESTS` was ratcheted in the SAME
edit as the suite every time. **VERIFY BEFORE QUOTING — this line has been wrong four times.**
~~there are still NO floors on the Foundry or TypeScript counts, which is item 4 of §1~~
**— CLOSED BY A-075: all three suites now have count floors.** The instruction to verify before
quoting still stands and always will; a floor stops a suite shrinking silently, it does not make
this line true.)*
*(A-059 moved 160→170 / 77→78 / 29→30; A-061 moved 405→407 TypeScript and 170→173 verifier;
A-063 moved 73→74 Foundry; A-064 moved 74→75 Foundry and 407→409 TypeScript;
A-067 moved 409→426 TypeScript and 173→176 verifier.
Every gate FLOOR was ratcheted in the SAME edit as the suite it bounds, which is the rule this
line exists to enforce and the rule it has broken three times.)*
*(Read `149/149` and omitted the tamper figures entirely until 2026-08-17 — stale for the third
time, in the file that opens by declaring itself the memory. The verifier moved 146 → 149 → 154 →
158 → 160 in two days and this line tracked none of it.)* *(This line read 66/66 and 70/70 for
most of 2026-08-16 while all three numbers moved underneath it — in the file that opens by
declaring itself the memory. Update it in the same edit that changes a suite, not later.)*

### 2026-08-18 — `docs/session-state.md` lines 664–674 at `e73789d`

**TEN mechanical stages guard the gate** *(eight until A-064 added labelling-artifact pinning — the labels of record were guarded by nothing while the prompt that produced them was hash-frozen — and A-062 then added the §7.3 ablation-report provenance stage; COUNT THEM IN `scripts/test.sh` before quoting this number, because this line has been wrong three times)***:** secrets (A-007), publication visibility (D-032/D-048), labelling-prompt
freeze (D-011a), EIP-712 type strings (D-023), §5.7.1 check coverage (D-031), **corpus class
coverage (A-036, new 2026-08-16)**, vendor honesty (§7.5 Gate 5, D-008), and — deep profile
only — **the §7.1 corpus executed with its committed views verified**. The Gate 7 canary history
prints and deliberately cannot fail the gate.

**Two of the eight pass on something weaker than a pass, and both say so on every run.** Vendor
honesty now reports D-008(1) as MET and (3) as **certified by record** (D-038) — it checks that a
named certification exists in §2 and that §2 still hashes to the table John certified, and states
that it cannot check the certification is *right*. Class coverage passes on a RATCHET: **14 of 20 classes exercise the class they name** (credit iff an ABOUT check ran against the named phenomenon and recorded the outcome the spec assigns to it, UNRESOLVED included); six are carried, one of them a GAP, and a green line
means only that no NEW class went vacuous. Read their output, not their exit status.

### 2026-08-17 — `docs/session-state.md` lines 652–662 at `e73789d`

**A-048 (2026-08-17) then broke A-047's own headline.** A second review round — thinner briefs,
three reviewers — found the verifier floor counted tests that never ran (`@unittest.skip`,
`@unittest.expectedFailure` over a real RFC 8785 violation, and a `setUp` monkeypatch giving
`OK (skipped=146)`: every assertion disabled, floor satisfied), and that the new committed-view
check exempted `expiryAfter`/`expiryBefore` — a CONFORMANCE INPUT feeding
`EVAL_ENTITLEMENT_ADVANCED` in 36 of 50 views, not the "timestamp fields" three documents called
them. **Both fixed and falsified against clean baselines.** Worst item: A-047's annotation to the
signed S2 pack claimed §11 had made the overclaim, when §11 said the opposite and was RIGHT
("git history, not re-execution"); that misdescription reached a facilitated ratification
(D-045). Corrected in place under John's ruling that repairing a false statement inside an
annotation is not itself a new annotation.

### 2026-08-17 — `docs/session-state.md` lines 676–705 at `e73789d`

- **§9 steps 1–9 done.** Steps 4–6 reviewed under A-022; steps 1–3 under A-016 (whose
  verifications were mostly cut short by a spend limit — that limit is NOT retired); **steps
  7–8 reviewed for the first time this session**, ten findings, all remediated.
- **Ablation:** false allows **38 / 8 / 1**; contribution — baseline alone 9, effect extraction
  29, **mandate conformance 8**; exact match 12 / 41 / 49. **D-034 gave the partition a
  criterion** (L3-only = compares the call or its effects to the mandate's PURPOSE fields) and
  the figure fell from 17 to 8. The 8 are exactly the wrong-purpose class. The report emits the
  split as a CHECK — its second row must be empty.
- **D-010 verifier:** Current measured counts and floor values are printed by the gate and by
  scripts/check-suite-floors.sh; this maintained paragraph carries no numeric copy.
  *(CORRECTED 2026-08-17, round five `B-4`/`B-1`: this line read `7/7, 62/62,
  24 modes, 149/149` — a fourth staleness in this file, seventy-nine lines below a §3 headline
  that already said 160 and 77/29. **The identical stale trio is STILL PRINTED BY THE GATE
  ITSELF** in `scripts/test.sh`'s COVERAGE BOUNDARY, where it is labelled "ALL THREE FIGURES ARE
  FLOORS THIS RUN ASSERTS" beside floors of 160/7/77/29 — five of eight round-five lenses found
  it independently. That one is CODE and is NOT fixed: it is unscoped remediation awaiting John,
  register §13.)* *This line read `6/6, 42/42, 70/70` until
  2026-08-16, forty-six lines below the headline in §3 that already said 146/146 and 7 samples —
  i.e. this file contradicted itself, in the file that opens by declaring itself the memory. It
  was **not** fixed by A-045, whose decision entry and commit message both claim "both layers are
  corrected"; exactly one was. Found by an independent reviewer, not by the author who edited this
  file twice in the same session.*
- **Gate 7 canary:** built, run live once, agrees with the pinned recording. D-036 sets the
  cadence at **monthly**; a DRIFT row is a finding about the model, never a build failure.
- **Labellers:** E and F are the labels of record. G, H, J, K, **L and M** are targeted
  measurement arms and are audit trail only. **A-033 as first written was wrong and is corrected
  in place** — the contamination channel moved one label (F051), measured by K. **L and M are
  the same D-035 control arm run twice by two concurrent sessions (A-037); M is the duplicate,
  re-designated, and its provenance says so. They agree with E and with each other on all five
  labels and on confidence.** Next arm is N.

### 2026-08-16 — `docs/session-state.md` lines 617–623 at `e73789d`

**All four counts above were re-measured 2026-08-16 (late session) and all four held.** The
verifier's 146 was measured by running it — which until that moment was the ONLY way it could be
measured, because **no profile of the gate ran the verifier and nothing in `scripts/` invoked
it** (A-045). Its numbers were quoted on this line beside Foundry's and TypeScript's as though a
green gate covered them; it did not, and a verifier regression could not have failed the gate.
It is now a stage in `scripts/test.sh`, in both profiles, and both of its arms were falsified
against the real script before that was claimed.

### 2026-08-16 — `docs/session-state.md` lines 707–773 at `e73789d`

[The §4 index table into `docs/decisions.md`; the live §4 keeps the heading and a pointer.]

## 4. Decisions and findings — 2026-08-15 and 2026-08-16

**The canonical record is `docs/decisions.md`, and it is the one that wins.** This table is an
index, ordered roughly as things happened. Every entry below has a full entry there with its
reasoning, its rejected options, and where stated the condition that would reverse it.

| | Subject |
|---|---|
| D-033 | Measure A-030's contamination channel; add model diversity |
| D-034 | The §7.3 partition gets a criterion; mandate conformance 17 → 8 |
| D-035 | **Resolves A-034** — measure five fixtures, then treat the PASSAGES as the v1.1 defect. Escalation threshold declared: 2+ movements → full re-freeze |
| D-036 | Canary monthly; D-009 order confirmed; A-029 accepted as bounded |
| A-029 | Views not byte-reproducible — now bounded by normalised digests |
| A-030 | The specification is a contamination channel for labellers |
| A-031 | The five owed items built; three agent-made calls, one flagged reversible |
| A-032 | Three adversarial reviews: two blockers, fourteen others |
| A-033 | D-033 executed — **corrected**: the channel moved one label |
| A-034 | Agent call not to re-freeze — **TRIGGERED, superseded by D-035** |
| A-036 | Two fixtures do not exercise the class they name; no check asserts they do |
| A-037 | **Two sessions ran the same measurement and one overwrote the other's committed evidence.** Caught by luck, not by any guard |
| A-038 | A-036's check **built** and in the gate: 14/20 classes exercise the class they name; two new vacuous classes found |
| D-037 | **One agent session at a time on this tree.** Resolves A-037 |
| D-038 | **GATE 5 CERTIFIED.** Seven rulings; §2 rewritten; 11/11 cited; stale on any §2 edit |
| D-039 | The two A-038 classes ruled apart: override is an accepted **delegation**, conflicting-block-state is a **GAP owing a fixture** |
| A-039 | **Two adversarial reviews, 25 findings.** Both new guards were defeatable; several claims exceeded their evidence. 11 of 12 exploits now caught, 1 documented residual |
| D-040 | Closes A-039: **F002 stays** (it earns its place by blocking), the class map widens to §7.1's four hard caps, condition (2)'s residual accepted as documented |
| D-041 | **GATE S2 SIGNED — PASS, John, 2026-08-16.** Signed on §11's limits, not despite them. Steps 1–3's limit recorded not retired; dashboard stays outside S2; 14/20 does not flip a gate |
| A-040 | The steps 1–3 review S2 was signed WITHOUT. **The encoding held; the two layers built on it did not.** Vault caps native value only; the invariant campaign killed nothing the fast tests did; the D-010 verifier certified a forged refusal |
| D-042 | **S2 stands, annotated.** §7.1's containment claim corrected (cap → v1.1); the campaign gets its two missing arms; the verifier is repaired by an agent that has not read the implementation |
| A-041 | Verifier repaired, 70 → 101 tests, both exploits now fail closed. **Its best output is a spec finding: §5 defined no refusal record at all**, so D-012's requirement was unbuildable from the published document |
| D-043 | **CONSOLIDATE — no new front, no ladder rung.** Re-label bound to pre-publication with a named trigger; §5.5.1 RefusalRecord published; override event added; Anvil keys re-baselined |
| A-044 | The six remaining step-3 findings, ruled and fixed: backpressure bounded nothing, the signer's namespace was caller-writable, `evidenceHash` non-injective, two refusal paths left no artifact. Anchor recency **recorded as a limit** |
| A-043 | **CRITICAL, fixed.** A signed ALLOW was obtainable for calldata nobody decoded, and executed onchain twice in reproduction. A-028's repair covered one of two branches; **11 tests were passing through the hole** |
| D-044 | **Session close.** Pushed; one last review of §9 step 3 (A-016's 6 unadjudicated skeptics); both capability deferrals CONFIRMED; **pre-publication NOT started** |
| D-045 | S2 pack annotated for A-042 and A-047, **with a stopping rule** |
| D-046 | Round two authorised; reading declared before results |
| D-047 | ~~The review loop terminates on a CLEAN ROUND~~ **SUPERSEDED by D-055(a), 2026-08-18.** Its anti-gaming and non-amendability spirit carries into T1–T4 |
| D-048 | **Pre-publication sequences AFTER the loop.** A clean round is a precondition, not a trigger |
| A-045 | The D-010 verifier was an S2 deliverable **no gate ran** |
| A-046 | All eight guards falsified — headline later shown worthless (see A-047) |
| A-047 | **Three reviewers: 7 guard defeats.** A-046's "8/8" refuted; corpus provenance never checked |
| A-048 | **Round two broke A-047's fixes**, incl. one John had ratified. Floor counted tests that never ran |
| A-049 | `evidence-hash` mode; vendor roster de-duplicated; casing residual narrowed |
| A-050 | Round three launched; reading declared first; **taxonomy later proved incomplete** |
| A-051 | **41 surviving mutations** across six verifier modules. My brief omitted `jcs.py` |
| A-052 | **The secret guard let a real private key through** — `...` and `EXAMPLE` suppressed the line |
| A-053 | The `verify.py` sweep commissioned; reviewer invited to criticise the brief |
| A-054 | Charsets pinned by COMPLEMENT rather than by bad list |
| A-055 | **`verify.py`: 14 survivors + TWO LIVE certification defects.** Presenter chose the trust root |
| A-056 | Override cluster, the anchor, and **the corpus-vs-verifier category error** |
| A-057 | Round five commissioned; the reading declared before results; eight lenses, whole tree |
| A-058 | **ROUND FIVE: NOT CLEAN. 51 findings, 2 CRITICAL, the same repair defect three times. D-048(b) fired** |
| D-049 | John: **the loop continues and "full breadth" gets defined**; remediation scoped to the three LIVE defects |
| A-059 | The three live defects fixed. **The first draft of the first fix shipped the very defect it was fixing** |
| A-060 | ~~DRAFT~~ **RATIFIED by D-050(1)** — the nine-surface definition of "full breadth" |
| D-050 | John's six walkthrough rulings: **A-060 ratified**, cluster C only, leads → round six, reports committed, push, kill the leaks |
| A-061 | Cluster C built: the signer's prototype-chain verdict check and the verifier's array-precedence hole |
| A-062 | The coverage boundary audited WHOLE — four false statements, two reported by nobody; G-2 closed with a provenance gate stage |
| A-063 | **F-VAULT-1: D-042's correction was itself false.** Four sites repaired, a limit test added, **claim UNCERTIFIED — awaits John** |
| A-064 | **Cluster B closed:** labels pinned (9th guard), corpus VERDICTS compared, both window lower bounds exercised, the invariant arm's registration asserted |
| A-065 | Two verified leads: the env template that never shipped, and a suite figure counted twice |
| A-066 | **The deep profile can now be run from a worktree** — D-050(1)'s condition was unmeetable when it was ratified |
| A-067 | **21 of 24 leads CONFIRMED** by four independent adjudicators. `D-08` raised to HIGH and fixed; `H-4` fixed; 19 recorded |
| D-051 | John's four walkthrough rulings: **§7.1 CERTIFIED**, fix MEDIUM / accept LOW, round six after the fixes, probes preserved |
| A-068 | Seven MEDIUMs fixed; ~~`E3` and `E4` returned to John as design forks~~ **`E3` was ALREADY ruled a declared limit by John at A-044(f) 2026-08-16; A-068 re-opened it without citing that. NOW RULED FIXED (D-055).** `E4`'s signer half stays unbuilt (D-014) |
| A-069 | E4's verifier half built — and the fixture gap it found matters more than the check |
| A-042 | **The D-010 experiment run properly:** a schema-only build met a real signed refusal it had never seen. Everything §5.5.1 STATED matched first time; the envelope it omitted diverged, plus three defects in the section — all mine, all corrected. 101 → 146 tests |

### 2026-08-16 — `docs/session-state.md` lines 961–970 at `e73789d`

Latest measured: **batch C 14/14 caught**, **batch S 31/31 caught**, 0 survived, 0 failed to
apply. Three qualifications belong with that number: it is **not** comparable to A-028's "29 of
45 survived", because these tests were written for these mutants; **four anchors had to be
re-aimed** after the code they target was rewritten, twice in one day; and **C12 survived its
first run**, catching a test that passed for a reason other than the one it named — which three
independent reviews and a green suite had missed.

**There is no `spike` batch.** `ts/src/spike/**` is excluded from `tsconfig`, and its two live
defects this session were found by reading, not by tooling. `canary.test.ts` now covers the
verdict logic; the arms themselves need a model and are untested.
