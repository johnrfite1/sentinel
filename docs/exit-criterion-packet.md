# Replacing D-047 — the measured packet

**PREPARED, NOT DECIDED.** D-047 is explicit that only John changes the terminating condition,
and D-052(b) restates it: *"the bounded exit criterion is JOHN'S TO SET — an agent may prepare
measured input for that decision and may not author, adopt or infer the criterion."* Nothing in
this file is adopted. No round seven is started by it.

Every figure below is measured or cited to where it was measured. Where a number is an agent's
classification rather than an independent adjudication, it says so.

---

## 1. Defect rates by severity — rounds 1 to 6

| Round | Date | Shape | Findings | CRIT | HIGH | MED | LOW/INFO |
|---|---|---|---|---:|---:|---:|---:|
| 1 (A-046/A-047) | 08-16 | 8 guards falsified, then 3 reviewers told to DEFEAT a guard | 7 confirmed defeats + 2 fixed, rest recorded | 0 | ≥2 | — | — |
| 2 (A-048) | 08-17 | 3 reviewers, thinner briefs | 3 headline + follow-ons | 0 | 2 | 1 | — |
| 3 (A-051/A-052) | 08-17 | directed mutation sweep, 6 modules | 142 mutations → **41 survived a green gate**; 3 verdict-flippers; 1 live key-guard hole | 0 | ≥4 | — | 38 latent |
| 4 (A-055/A-056) | 08-17 | 1 directed reviewer, `verify.py` (1,830 lines) | **2 LIVE certification defects** + 14 latent survivors | 0 | 2 live | 14 | — |
| 5 (A-057/A-058) | 08-17 | **8 reviewers, whole tree** | **51** | **2** | 11 | 22 | 16 |
| 6 (this round) | 08-18 | **9 reviewers, 9 ratified surfaces** | **91** | 0 | **18** | 44 | 29 |

**Round 5 severities are independently adjudicated** (four adjudicators; 21 of 24 unconfirmed
leads confirmed, 3 returned REFUTED / ALREADY-CLOSED / UNPROVEN).
**Round 6 severities are REVIEWER-ASSIGNED and only partly adjudicated.** I reproduced ~14
myself. **Any exit rule that keys on severity must say who assigns it — see §4, attack 2.**

### By class (round 6, the only round with a full class breakdown)

| Class | Count | Note |
|---|---:|---|
| instrument-defect | ~31 | guards/tests/mutations aimed at something other than what they name |
| false-claim | ~24 | a claim stronger than its evidence — **the dominant class in every round** |
| code-defect | ~17 | includes every live certification defect |
| doc-error | ~13 | stale counts, dead citations |
| spec-gap / environment | ~6 | |

### By surface (round 6)

| Surface | Findings | HIGH |
|---|---:|---:|
| claims (documents, comments, printed output) | 18 | 2 |
| `verifier/**` | 10 | 4 |
| `ts/src/evaluate` + `decode` | 13 | 1 |
| `contracts/src` + invariants | 11 | 2 |
| `scripts/**` | 10 | 3 |
| `ts/src/simulate|propose|tools` | 10 | 2 |
| free lens | 7 | 2 |
| `ts/src/signer` | 6 | 2 |
| corpus / ablation / fixtures | 6 | 0 |

**The two facts that matter for setting a threshold.** (i) `verifier/**` has produced a **live
certification defect in four consecutive rounds**, every time inside the previous round's
repairs. (ii) The **claims** surface is the largest single source of findings and produced two
HIGHs that sit inside SIGNED packs.

---

## 2. Cost and time per round

Round 6 is the only round with per-reviewer instrumentation.

| | Measured |
|---|---|
| Reviewers | 9 |
| Agent time, summed | **~8.1 hours** |
| Wall-clock (concurrent) | **~80 minutes** |
| Subagent tokens | **~2.93 M** |
| Adjudication (agent, sequential) | ~2 hours |
| Remediation under D-052(b) | ~5 hours, 6 commits |

Per-reviewer range: 35–80 min, 216k–440k tokens. **Concurrency cost is real and measured:** nine
reviewers drove load average above 100, three recorded probes that flaked to a false CAUGHT and
reversed on re-run, and one lost a probe mid-mutation to a timeout that left a 0-byte log beside
an "exit 0" notification. **A single-reviewer round removes that entire failure class.**

Rounds 1–4 were not instrumented. Their shape (1–3 reviewers) implies roughly 1/3 to 1/9 of
round 6's cost.

---

## 3. Accepted product boundaries — these must NOT block exit

Each is a decided boundary, not an open defect. Listed so an exit rule cannot be read as
requiring their removal.

| Boundary | Ruling |
|---|---|
| Aggregate native value unbounded; the drain is **atomic** | **D-053(a), certified D-054(a)** |
| Token authority uncapped by the vault | D-042; per-action allowance ceiling remains v1.1 |
| Nonce guard is per-process, best-effort | D-013, restated D-053(b) |
| Invariant campaign adds no measurable assurance | **D-054(b)** |
| 14 of 20 corpus classes exercise the class they name (credit iff an ABOUT check ran against the named phenomenon and recorded the outcome the spec assigns to it, UNRESOLVED included) | ratchet, printed every run |
| ~~Ten~~ **SIX** findings accepted as documented limits — `D-07`, `D-09`(a),(b), `E5`, `F-VAULT-4`, `F-VAULT-5`, `G-3` | D-051(b) accepted ten; **A-076 FIXED five**, and the remainder was mis-stated as five until `R4-F1` (D-055(e)) found `G-3` dropped. **Derived at `docs/gate-s2-evidence.md` §11.0 — do not re-count by hand.** Corrected 2026-08-19 (A-080) |
| E4's signer half deliberately not built | D-014 |
| Verdict correctness in general; no live agent in CI | §11 |

## 3b. UNRESOLVED — these are defects, not boundaries

| Item | Why it is not a boundary |
|---|---|
| ~~**`decodedSelectorAndParameters` is compared to nothing**~~ **— FALSE SINCE A-074; CORRECTED 2026-08-19 (`R2-F4`, D-055(e))** | **`docs/gate-s1-evidence.md:124` and `:152` — a SIGNED pack — say the D-010 verifier "does the conformance comparison". It does not: `grep -c decodedSelectorAndParameters verifier/verify.py` = **0**. This is a known false claim in signed text and is UNFIXED.** **CORRECTION: A-074 BUILT the comparison — the grep now returns 2, not 0 — and the signer checks the field too. This row was true when written and is not true now. What remains is the `description` sub-field only, recorded at `docs/v1-1-register.md` §13.7.** |
| **`E3` — anchor recency** | An OPEN DESIGN FORK John holds, not a ruled boundary. Until ruled it is unresolved. |
| No gate floor on Foundry/TypeScript counts | round 6 `L8-14`; a shrinking suite is invisible to the gate |
| Register §13 status column stale for ~17 of 24 rows | the file reviewers are told to trust |
| §11.0 truncated adjudicator reasoning; no adjudicator report committed | the basis for ten acceptances is not readable |

---

## 4. Backtest — what each candidate would have produced on rounds 1–6

**C1 — John's primary candidate.** *One independent, fixed-scope post-D-052 review using the
repaired apparatus; passing deep gate and workspace guards; zero unresolved confirmed
Critical/High defects; zero known false or unsupported signed/certified claims. Medium/Low may
remain only when individually adjudicated, accurately documented as limits, and reflected in
affected claims.*

| Round | C1 verdict | Binding condition |
|---|---|---|
| 1 | **NO EXIT** | false claim: the gate printed "committed views semantically current" while hashing nothing |
| 2 | **NO EXIT** | false claim inside the SIGNED S2 annotation, which reached a facilitated ratification |
| 3 | **NO EXIT** | HIGH: the secret guard passed a real private key |
| 4 | **NO EXIT** | 2 LIVE certification defects |
| 5 | **NO EXIT** | 2 CRITICAL, 11 HIGH |
| 6 | **NO EXIT** | 18 HIGH incl. live certification defects; apparatus was broken |

**C1 correctly blocks exit on all six, including every round containing a live certification
defect. It passes the test John set.**

### Candidates that FAIL the backtest — reject

| Candidate | Fails where | Why |
|---|---|---|
| **"Zero CRITICAL only"** | **Round 6** | Round 6 had **no CRITICAL** — its live certification defects (an unexamined §5.5 override certified `=> PASS`; absence-is-agreement) were HIGH. This rule **would have permitted exit with a live certification defect standing.** **This is the single strongest argument for Critical/High rather than Critical-only.** |
| **Budget/time-boxed** ("stop after N reviewer-hours") | Rounds 3, 4 | Would have exited mid-loop with 41 surviving mutations and, one round later, two live certification defects. |
| **"Two consecutive documentation-only rounds"** (D-047's own reversal) | Round 6 | Round 6 was not documentation-only, so it never fires; as an exit rule it is unreachable on this evidence. |
| **"Zero findings of any severity"** | all six | Excluded by John, and correctly: it is D-047's unbounded condition renamed. |

### Attacks on C1 — five, with tightenings

C1 survives the backtest. It does not survive adversarial reading unmodified.

1. **"Confirmed" by whom?** §11.0 accepted ten findings, and one acceptance (`D-09(c)`) rested on
   the premise "no corpus fixture has divergent ceilings" — **which F006 refutes.** An adjudication
   can be accurate in form and false in basis.
   **T1: each accepted limit's stated factual basis must be independently verified, and the
   verification recorded beside it.**
2. **Severity is assignable by the party exit depends on.** Round 6's severities are
   reviewer-assigned; round 5's adjudicators moved two MEDIUM→LOW.
   **T2: for exit purposes, severity is assigned by the independent reviewer/adjudicator, and any
   downgrade is recorded with reasoning and countersigned by John.**
3. **"Fixed-scope" does not say who fixes it.** D-047's anti-gaming clause exists because a round
   scoped narrowly enough comes back clean.
   **T3: scope fixed by John BEFORE the review, covering at minimum the nine D-050(1) surfaces
   PLUS every surface touched by D-052 remediation.**
4. **"Passing deep gate" is not coverage.** The gate passes on ratchets — 14/20 classes carried,
   vendor honesty "certified by record".
   **T4: the exit record states the gate's carried and ratcheted items explicitly, so a green gate
   is not read as coverage it does not have.**
5. **"Known" false claims.** Unknown ones are what the loop finds. Not closable — this is the
   residual the independent review exists to reduce, and it should be stated rather than papered
   over. **No tightening; record as the accepted residual of any bounded rule.**

---

## 5. Fixed scope and budget of the final independent post-repair review

Offered as a concrete proposal for John to set, not as a decision.

**Scope — the surfaces with a measured prior, not an even sweep:**

1. **`verifier/**`** — a live certification defect in four consecutive rounds, always in the
   previous round's repairs. **A-070's repairs are the newest and are self-authored.**
2. **The D-052(b) remediation itself** — A-070…A-073, D-053. Four of the five repairs *preceding*
   these were defeated within 48 hours. These have not been independently reviewed at all.
3. **The claims surface** — largest source, and it produced two HIGHs inside signed packs.
4. **`ts/src/signer/**`** — carries the project's only CRITICAL to date.

**Budget:** 4 reviewers, ~1.6 M tokens, ~3 agent-hours, ~45 min wall clock — roughly **55% of
round 6**. Run **serially or at most two at a time**: round 6's concurrency produced three
false CAUGHTs and one lost probe, and a smaller round removes that class entirely.

**Deliverables per reviewer, unchanged from round 6 because they worked:** findings with
reproductions, null results, **dead probes**, a coverage statement, a brief critique, and a
provenance attestation.

**Then adjudicate.** Round 6 showed why: reviewers were accurate (21/24 later confirmed) *and*
wrong often enough that three verdicts came back REFUTED, ALREADY-CLOSED, UNPROVEN.

---

## 6. Apparatus and evidence prerequisites — all currently MET except one

| Prerequisite | Status |
|---|---|
| Deep gate passes from a **symlinked review worktree** | **MET** (A-071) — verified, `GATE PASSED`, views verified file-by-file |
| Remappings pinned so bytecode is provisioning-independent | **MET** (A-071) |
| Each reviewer its own evidence directory | MET (round 5 `D-11`) |
| `sample-check` / `emit-samples` runnable from a worktree | **MET** (A-071) |
| Worktree hazards documented (`ln -sfn`, `git status` 128, `git checkout` destroying links) | MET |
| Repair protocol binding on any repair the round produces | MET (A-070) |
| **Register §13 status column accurate** | **NOT MET** — stale for ~17 of 24 rows, and it is the file reviewers are told to trust so a re-report is not mistaken for a finding |

---

## 7. Explicit blockers and non-blockers

**BLOCKERS — exit cannot be reached while these stand:**

1. **The signed Gate S1 pack contains a known false claim.** `gate-s1-evidence.md:124`/`:152`
   state the D-010 verifier "does the conformance comparison"; ~~it does not.~~ **FALSE SINCE A-074; THE COMPARISON IS BUILT (`grep -c decodedSelectorAndParameters verifier/verify.py` = 2). The signed S1 pack's original sentence is historical signed text and is not an agent's to rewrite. This item is not a current exit blocker.** ~~Under C1 condition 4 this alone blocks exit.~~
2. **`E3` is an open fork, not a boundary.** It needs a ruling to become either.
3. **Register §13's status column** must be corrected before a review that depends on it.

**NON-BLOCKERS — must not be read as blocking:**

- Every item in §3 (accepted boundaries, all ruled).
- The six §11.0 accepted limits — subject to **T1**.
- The gate's carried/ratcheted items — subject to **T4**.
- Round 6's own non-cleanliness. D-052(a) already ruled it cannot be the qualifying round; it
  does not have to be re-run.

---

## 8. What is being asked

**A decision on the exit criterion.** The options as I read them:

- **C1 as written** — passes the backtest, and is exposed to attacks 1–4.
- **C1 + T1…T4** — same rule, four tightenings, each traceable to a defect this project actually
  shipped. **This is what I would recommend if asked, and the recommendation is not a decision.**
- **C1 with a different severity threshold** — the backtest says Critical-only is unsafe;
  Critical/High is the lowest threshold that blocks every prior round.
- **Something else entirely** — the measurements above are the input, whatever the shape.

**Not asked, and not started:** round seven. It does not begin until the criterion exists and
the blockers in §7 are resolved.
