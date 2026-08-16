# Sentinel — Session State

Rewritten at the end of each working session. **This file, not the conversation, is the
memory.** If it disagrees with anything an agent remembers, this file wins.

Last updated: **2026-08-16**, branch `step-3/isolated-signer`, **pushed** (`1a27a36`, verified
against the remote rather than trusting the push output). The repository is PRIVATE — the rename
gate checks this on every run — and D-016 still blocks all publication. **Pushing to the private
remote is backup, not publication; do not read the push as any relaxation of D-016.**

---

## 0. If you read nothing else, read this

**Gate S1 is SIGNED — PASS, John, 2026-07-28. GATE S2 IS SIGNED — PASS, John, 2026-08-16
(D-041).** Both by John alone at facilitated sessions, never by an agent (D-002, non-delegable).
**D-002's two mid-build gates are now both behind the project.**

**What S2 does NOT authorise, stated first because a signed gate is the moment scope creeps.**
D-016 still blocks all publication and the repository is PRIVATE. Gate 8 (five-minute
comprehension) is PRE-PUBLICATION under D-032 — it needs the dashboard D-009 deferred and John's
five held questions, which the build loop must never see. Certification of public claims is
still autonomy NONE. **S2 was signed on the state in `docs/gate-s2-evidence.md` §11 INCLUDING
its limits, not despite them** — 14 of 20 classes exercising the class they name, no live agent
in CI, steps 1–3's review still cut short by an un-retired spend limit.

**All six items A-028 left owed are built.** Then four independent adversarial reviews and six
independent labellers were pointed at that work, and they found **two blockers and roughly
twenty further defects — most in work done the same day, several in the remediations
themselves.** All are remediated or recorded. Read A-032 and A-033 before trusting anything
here.

**The pattern, now observed often enough to be the operating assumption:** the defects are
*honesty* defects — a claim stronger than its evidence — and the build loop does not find them.
It found none of them. Reviewers, labellers and the mutation harness did. **Three separate
times this session a guard, a test or a mutation existed and was pointed at the wrong thing.**
The instrument existing is not the instrument working.

**John has delegated design forks to the build loop.** Two things stay outside that
permanently, and were restated to him: **gate signing** (D-002) and **certification of public
claims** — the §2 capability table, README, resume language (HANDOFF verification partition,
autonomy *none*).

---

## 1. What the next instance should do, in order

### 1. ~~Collect the D-035 measurement~~ — DONE, 2026-08-15. Result below.

**Labeller L: 5 of 5 agree with the labels of record. ZERO movements, against a declared
threshold of two.** D-035 part (c) stands; no escalation is owed and no re-freeze happens.
Recorded in `fixtures/corpus/labels/labeller-L-control.json` and its provenance file.

**The programme as a whole: E and F are the labels of record; SIX targeted measurement arms
(G, H, J, K, L, M) were compared against them, across two specification versions, two models and
fourteen fixtures — ONE label moved (F051), and it was the one labeller E had itself flagged.**
That is the bound D-035 asked for, and it holds.

**"Six independent labellers" was the wrong count and is corrected.** Twelve label files touch
those fourteen fixtures: **A–D are the FIRST labelling round, E and F are the labels of record,
and G, H, J, K, L, M are the six targeted measurement arms.**

**A–D are not unexplained — an earlier draft of this entry said they were, and that was my error
rather than a gap in the record.** `decisions.md` documents them: A and B produced the project's
sole inter-labeller disagreement (A read F002 REVIEW, B read it BLOCK), which is what put D-021
to John; C and D drove D-026 and D-027. **D-021 then owed a re-label of A's four wrong REVIEW
labels by fresh labellers — and E and F are that re-label**, verified: E labels F002 BLOCK,
citing D-021 by name. The owed work was done. Say A–D are superseded, not that nobody knows what
they are; **the lesson is that "the record does not establish this" is a claim needing the same
verification as any other, and I published it without grepping the decision log.**

**REPLICATED, BY ACCIDENT — labeller M, a second control arm over the same five fixtures.** Two
Claude Code sessions were open on this repository at once and both ran D-035's control. The
arms were blind to each other and agree completely: **E, L and M give the same label on all
five, and L and M even match on confidence — both `medium` on F025 and `high` on the other
four, both marking F025's governing rule as inferred rather than stated.** Ten control
observations, zero movements. The result is stronger than D-035 required, and **it was not
designed — do not write it up as planned replication.** See A-037 for the incident, which is a
finding in its own right and the more important half.

L raised a new finding, recorded as **A-036: F056 does not exercise reentrancy at all** —
`internalCallCount` 0, target with empty bytecode, exact-target failing long before the call
graph is reached. With F051 inert for the neighbouring class, §7.1's `reentrancy-attempt` and
`unexpected-internal-call` classes are covered at the corpus layer by two fixtures that between
them exercise neither. Deferred with D-035 (repairing them changes the labelled views), and it
is the THIRD instance of this defect class after A-028 F-5. **A mechanical check is possible —
assert each class's fixtures produce at least one failing check the class is about — and is not
built. That is the highest-value corpus work outstanding.**

### 1b. If the measurement ever needs re-running (it should not)

D-035 ruled: run the control labeller over **F001, F009, F025, F049, F056** and compare with
the labels of record. If no result is recorded in `fixtures/corpus/labels/`, run it:

- Control specification: `git show 052b3af:Sentinel_Protocol_Lab_Proposal_v0_2.md` written to a
  scratch path — the spec BEFORE the §4.2 walkthrough and before every 2026-08-15 amendment.
- Model: `claude-opus-5` (same as E and F, so the spec text is the only variable).
- Brief: copy labeller K's. `fixtures/corpus/labels/labeller-K.provenance.json` records the
  exact denials. **Require the provenance attestation** — eight labellers for eight have produced
  a first-order finding in it, unprompted.
- Record as `labeller-<letter>-control.json` + `.provenance.json`. These are AUDIT TRAIL:
  `report.ts` reads only `labeller-E.json` and `labeller-F.json`, so adding files moves no
  published number.

**THE THRESHOLD IS DECLARED IN ADVANCE (D-035): two or more of the five moved means the channel
is systematic, the sample has stopped being a bound, and a full re-freeze plus re-label of all
50 escalates to John.** One movement is consistent with F051 being the known case. **Do not
soften this after seeing the result.**

### 2. ~~Then part (c) of D-035~~ — DONE, 2026-08-15. `docs/v1-1-register.md`

The offending passages are a **v1.1** correction, not a v1 re-freeze. **Do NOT edit §4.2 or
§5.7.1 to remove the worked examples** — that edits the specification to serve the measurement,
and D-035 explicitly does not authorise it. Recorded, not changed.

Three things in that register a reader should not have to find for themselves:

- **D-035's "§5.7.1 publishes eleven reason-code identifiers" is wrong — it publishes 41.** The
  eleven is §5.7.1's count of checks missing from §5.7's prose. The ruling is unaffected; the
  entry is annotated in place, not rewritten, because it is John's.
- **Closing that leak fights `check-eval-codes.sh`**, which fails the gate if a check exists in
  the engine and not in §5.7.1. Deleting the list to protect labellers breaks the guard that
  proves the prose is complete. That tension is a design fork, not an edit.
- ~~One item does NOT ride on the re-label and could be built now~~ — **BUILT 2026-08-16,
  `scripts/check-class-coverage.sh`, in the gate. It found two more vacuous classes (A-038),
  both awaiting John.** See §3 and A-038.

### 3. ~~Prepare Gate 5's certification for John~~ — **CERTIFIED 2026-08-16 (D-038)**

**Gate 5 is MET.** John ruled all seven forks at a facilitated session; §2 is rewritten to match.
`check-vendor-honesty.sh` reports **11 of 11 rows cited** and D-008(3) **certified by record**,
naming D-038 — it checks that a named certification exists and says on every run that it cannot
check the certification is right. Rows 2 and 8 split; Circle and Hypernative marked
`(inference)`; Safe re-cited rather than narrowed; §13 gained #25–#28.

**The certification goes stale on ANY edit to the §2 table** — the guard prints that where the
certification prints. **Owed at v1.1:** Coinbase was left at two documented criteria without the
re-cite lookup that rescued Safe, and Tenderly stays on a marketing page the audit called thin.
Both would improve accuracy in the direction that does not flatter Sentinel.

<details><summary>The original preparation note (superseded)</summary>

`docs/gate-5-vendor-audit.md` holds a completed source-verification pass — all nine cited pages
fetched and read 2026-08-15 — and, appended to the same file, **the certification packet: every
proposed change as literal replacement text, ready for a ruling session.** It is in that file
and not its own because a new vendor-naming file would fail `check-vendor-honesty.sh` on
D-008(4), and excluding it would be a claim about the file the script warns against.

**The earlier count in this file was wrong and is corrected.** It read "five rows hold, four do
not". Row 8 is two products in one sentence: Blockaid holds, **Tenderly does not**. Four rows
hold as written (1, 4, 6, 9), one holds by half (8), and **five need a ruling:**

| Row | Status after the packet's lookups | What John rules |
|---|---|---|
| 7 Hypernative | **UNRESOLVED.** "intent verification" is on no cited page, and the re-cite lookup returned a self-contradicting read — not evidence | strike / mark `(inference)` / re-cite after a verified read |
| 2 Coinbase; Privy | holds for Privy only; "signer" for neither | split the row (text drafted) |
| 5 Safe | **recoverable** — all four missing claims documented on two Safe pages §13 does not yet cite | re-cite (text drafted; adds §13 #25, #26) |
| 8 Tenderly half | "known-threat detection" unsupported on the landing page AND the alert docs | split the row (text drafted) |
| 3 Circle | "agent-native execution" is a characterisation | mark `(inference)` (text drafted) |

Plus two policy questions the packet states: the marker format, and whether inference is marked
per-cell or by one declaration over the "Consequence for Sentinel" column (recommended).

**Every discrepancy overstates a COMPETITOR, never Sentinel** — and note that the cheap fix for
Safe (narrow the row to Guards) would have made a competitor look weaker on a citation error of
ours. The packet takes the other road. Once John rules, the marker `[§13#N read YYYY-MM-DD]` on
each capability cell makes D-008(1) mechanical — `check-vendor-honesty.sh` counts it and reports
`0 of 9` today, `10 of 11` after application, with Row 7 the honest shortfall.

**A guard defect recorded in the packet, to fix AFTER the rulings:** the script says the marker
is counted "appended to the capability cell" but its awk tests the whole row line. The tightened
version has to match the layout John rules for, so it is sequenced behind him.

**An agent may not write those cells.** The diff is prepared; put it in front of him.

</details>

### 4. ~~Run Gate S2 as a facilitated session~~ — **SIGNED, PASS, John, 2026-08-16 (D-041)**

Pack: `docs/gate-s2-evidence.md`, now marked SIGNED with the four rulings recorded in §12. Gate 5
was the blocker and was certified the same day (D-038): 0 of 9 rows dated became 11 of 11.

**Three decision points were put BEFORE the signature, in that order deliberately** — steps 1–3's
un-retired spend limit (recorded as a limit, not retired), the evidence dashboard (stays outside
S2), and whether 14-of-20 class coverage flips a gate (it does not; traced gate by gate). Nothing
capable of changing the verdict was raised after the signing.

**The next instance's job is NOT to find the next gate.** There isn't one until pre-publication.
What is owed is v1.1 work, §5 below, and it is bounded by the re-label decision.

**D-043 set the direction: CONSOLIDATE.** Work the v1.1 register down; open no new front. §14.8's
ladder is available — rung 2 (executed vendor comparisons) and the 14.3 attestation stretch are
both eligible now — **and both were declined.** Rung 2 in particular reverses D-001 and would
require unwinding D-008(2) and the vendor-honesty guard, putting executed-comparison claims into
a project whose whole honesty apparatus was built on their absence. **Do not start either without
John saying so; "S2 is signed" is not that permission.**

**The one unblocked piece of real work outstanding:** now that §5.5.1 publishes `RefusalRecord`,
a fresh **schema-only** agent can implement refusal VERIFICATION in the D-010 verifier, which
currently fails closed. Brief it exactly as A-041's was — allowlist `verifier/**` and the
proposal, deny `ts/**` and `contracts/**` — or the independence that makes the verifier evidence
is spent for nothing.

### 5. Deferred to v1.1, riding on the re-label decision (D-035)

- **F032 does not isolate policy expiry.** Its action deadline expires one second before the
  policy window, so it fails on two checks in different D-026 remedy classes.
- **F026 and F051 pin different `allowedCallGraphHash` values over an IDENTICAL observed call
  graph.** At most one can describe what F051's intent claims. Found by labeller K with no
  implementation access.

Fixing either changes the view the labels of record were drawn against. **Do not fix them
without a re-label.**

---

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

**73/73 Foundry · 380/380 TypeScript · 146/146 verifier · 50 corpus fixtures · 7 samples ·
gate green at the deep profile · workspace guards OK.** *(This line read 66/66 and 70/70 for
most of 2026-08-16 while all three numbers moved underneath it — in the file that opens by
declaring itself the memory. Update it in the same edit that changes a suite, not later.)*

Run `./scripts/test.sh`; use `--gate` for evidence. Read the coverage boundary it prints — it is
ONE statement, not a log; rewrite the affected layer when a step lands, never append.

**Eight mechanical guards run in the gate:** secrets (A-007), rename (D-016), labelling-prompt
freeze (D-011a), EIP-712 type strings (D-023), §5.7.1 check coverage (D-031), **corpus class
coverage (A-036, new 2026-08-16)**, vendor honesty (§7.5 Gate 5, D-008), and — deep profile
only — **the §7.1 corpus executed with its committed views verified**. The Gate 7 canary history
prints and deliberately cannot fail the gate.

**Two of the eight pass on something weaker than a pass, and both say so on every run.** Vendor
honesty now reports D-008(1) as MET and (3) as **certified by record** (D-038) — it checks that a
named certification exists in §2 and that §2 still hashes to the table John certified, and states
that it cannot check the certification is *right*. Class coverage passes on a RATCHET: **14 of 20
classes exercise the class they name**, six are carried, one of them a GAP, and a green line
means only that no NEW class went vacuous. Read their output, not their exit status.

- **§9 steps 1–9 done.** Steps 4–6 reviewed under A-022; steps 1–3 under A-016 (whose
  verifications were mostly cut short by a spend limit — that limit is NOT retired); **steps
  7–8 reviewed for the first time this session**, ten findings, all remediated.
- **Ablation:** false allows **38 / 8 / 1**; contribution — baseline alone 9, effect extraction
  29, **mandate conformance 8**; exact match 12 / 41 / 49. **D-034 gave the partition a
  criterion** (L3-only = compares the call or its effects to the mandate's PURPOSE fields) and
  the figure fell from 17 to 8. The 8 are exactly the wrong-purpose class. The report emits the
  split as a CHECK — its second row must be empty.
- **D-010 verifier:** 6/6 samples, 42/42 tamper cases, 70/70 tests.
- **Gate 7 canary:** built, run live once, agrees with the pinned recording. D-036 sets the
  cadence at **monthly**; a DRIFT row is a finding about the model, never a build failure.
- **Labellers:** E and F are the labels of record. G, H, J, K, **L and M** are targeted
  measurement arms and are audit trail only. **A-033 as first written was wrong and is corrected
  in place** — the contamination channel moved one label (F051), measured by K. **L and M are
  the same D-035 control arm run twice by two concurrent sessions (A-037); M is the duplicate,
  re-designated, and its provenance says so. They agree with E and with each other on all five
  labels and on confidence.** Next arm is N.

## 4. Decisions and findings from this session

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
| A-042 | **The D-010 experiment run properly:** a schema-only build met a real signed refusal it had never seen. Everything §5.5.1 STATED matched first time; the envelope it omitted diverged, plus three defects in the section — all mine, all corrected. 101 → 146 tests |

## 5. Traces — what worked, and what was a dead end

**Dead ends and traps — do not repeat:**

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

Latest measured: **batch C 14/14 caught**, **batch S 31/31 caught**, 0 survived, 0 failed to
apply. Three qualifications belong with that number: it is **not** comparable to A-028's "29 of
45 survived", because these tests were written for these mutants; **four anchors had to be
re-aimed** after the code they target was rewritten, twice in one day; and **C12 survived its
first run**, catching a test that passed for a reason other than the one it named — which three
independent reviews and a green suite had missed.

**There is no `spike` batch.** `ts/src/spike/**` is excluded from `tsconfig`, and its two live
defects this session were found by reading, not by tooling. `canary.test.ts` now covers the
verdict logic; the arms themselves need a model and are untested.

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
