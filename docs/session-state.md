# Sentinel — Session State

Rewritten at the end of each working session. **This file, not the conversation, is the
memory.** If it disagrees with anything an agent remembers, this file wins.

Last updated: **2026-08-16**, end of session. Branch `step-3/isolated-signer`, **pushed**
(`f3308ea`, verified against the remote rather than trusting the push output). Working tree
clean. The repository is PRIVATE — `check-rename-gate.sh` checks this on every gate run — and
D-016 still blocks all publication. **Pushing to the private remote is backup, not publication;
do not read the push as any relaxation of D-016.**

**READING ORDER FOR A FRESH INSTANCE.** §0 for where the project stands and how it fails; §1 for
what to do, which is probably nothing without an instruction from John; then `docs/decisions.md`
for D-041 through D-044 and A-039 through A-044, which is everything from the last session.
`docs/v1-1-register.md` is the list of known outstanding work, with each item's blocker stated.
`docs/gate-s2-evidence.md` §11 is what is NOT in evidence — read it before repeating any claim
about what this project has proven.

**The suite counts in §3 are verified as of this commit. Verify them again before quoting them:
that line was wrong for most of 2026-08-16.**

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
its limits, not despite them** — 14 of 20 classes exercising the class they name, and no live
agent in CI. D-041 carries an annotation naming what became known after it was signed.

**The steps 1–3 review S2 was signed WITHOUT has since been run (D-044(b)), and §11 is now
empty.** It found A-043: **a CRITICAL, exploitable bypass — a signed ALLOW obtainable for
calldata nobody decoded, reproduced twice onchain.** Fixed, with regression tests. Read A-043
and A-044 before trusting anything about the signer.

**THE PATTERN, now the operating assumption rather than an observation.** The defects are
*honesty* defects — a claim stronger than its evidence — and **the build loop does not find
them.** Across 2026-08-15 and 2026-08-16, roughly ninety findings came from adversarial
reviewers, independent labellers, the mutation harness and an independent reimplementation.
The build loop found essentially none of its own. Specifically and repeatedly:

- **An instrument can exist and point at the wrong thing.** Guards, tests and mutations have
  shipped aimed at something other than what they name — five or more times now.
- **A repair can generalise the DEMONSTRATION rather than the ARGUMENT.** A-028 fixed the branch
  its reviewer exploited and left the identical hole two lines down. A-043 is the cost.
- **A comment can describe a vulnerability and file it as an inconvenience.** A-028's test file
  named the exact bypass state in prose and routed around it.
- **A regression test can pass against the defect it names** (A-044).
- **A published number can be true once.** This file's own headline suite counts were stale for
  most of a day while the numbers moved underneath them.

**None of that is a reason to distrust the work; it is the reason to keep pointing independent
eyes at it.** Everything above was found, fixed or recorded — and found by the process working.

**John has delegated design forks to the build loop.** Two things stay outside that
permanently, and were restated to him: **gate signing** (D-002) and **certification of public
claims** — the §2 capability table, README, resume language (HANDOFF verification partition,
autonomy *none*).

---

## 1. What the next instance should do

### FIRST: probably nothing. Read this before starting anything.

**Both of D-002's mid-build gates are signed. There is no next gate until pre-publication, and
`HANDOFF.md` records that "authorized through Gate S2" has been SPENT.** D-044(e) ruled the
session closed at a clean point with pre-publication explicitly declined.

**The next move is a PROGRAMME START, and it is John's to authorise.** If you have arrived with
no instruction from him, the correct action is to say so and stop — not to find work. The
v1.1 register exists so that "there is nothing to do" is checkable rather than a guess.

**Three things are specifically NOT authorised, and each was declined with reasons on 2026-08-16
(D-043, D-044). "S2 is signed" is not permission for any of them:**

- **§14.8 ladder rung 2** (executed vendor comparisons). Reverses D-001 and would require
  unwinding D-008(2) and the vendor-honesty guard — putting executed-comparison claims into a
  project whose entire honesty apparatus was built on their absence.
- **The 14.3 attestation stretch**, now eligible because the §7.5 gates are green.
- **The evidence dashboard as "groundwork."** It needs no ruling from John and is a Gate 8
  prerequisite, which is exactly what makes it the tempting one. Building it reverses D-043's
  "open no new front."

### If John directs PRE-PUBLICATION

This is the only remaining direction, and starting it **fires the re-label trigger** (D-043(b)).
All of the following move together:

- **Re-label all 50 fixtures** under the SAME frozen prompt — D-035 ruled the prompt is not at
  fault, so `check-label-prompt.sh` stays green and no re-freeze is involved. The cost is fresh
  labeller runs, replacing E and F as the labels of record, and re-running the §7.3 ablation.
  **Every figure in `docs/gate-s2-evidence.md` then needs re-verifying.**
- **The five corpus defects that ride with it** — see §5 below and `docs/v1-1-register.md`.
- **Gate 8** (five-minute comprehension). Needs the dashboard D-009 deferred AND John's five
  held questions. **The build loop must never see those questions; do not ask for them, guess
  them, or write substitutes** (D-008, D-032).
- **D-016's rename gate and publication lift.** The repository is PRIVATE and
  `check-rename-gate.sh` verifies that on every gate run.

### If John directs V1.1 WORK

`docs/v1-1-register.md` is the list — seven sections, each with its blocker stated. Two items do
NOT ride on the re-label and could be done alone: the **vault token cap** and **receipt epoch
binding**. Both are deferred by explicit ruling (D-042(b), D-044(c), D-044(d)) and **both were
re-put to John on 2026-08-16 and both deferrals were confirmed.** Do not reopen them without him;
"the work is available" is not new information.

### The operating rules that bind whatever you do

1. **One agent session at a time on this tree** (D-037). Sub-agents inside one session are fine
   and are how every review here is run; two sessions with write authority are not.
2. **Adversarial review is the technique that works.** Four review rounds on 2026-08-16 produced
   ~65 findings in work that had already passed a build loop, including one CRITICAL exploitable
   bypass (A-043). Freeze a tree — `git worktree add <scratch> <commit> --detach`, symlink
   `ts/node_modules` — and tell the reviewer to prove the work fails.
3. **Verify before you rely on any number or status in these docs**, including this file. It has
   been wrong repeatedly, most recently in its own headline suite counts.
4. **Run every new regression test against the PRE-FIX code and confirm it fails.** A-044: a test
   written for the backpressure defect passed against the unfixed server — it was pinning the
   author's own fix, not the defect.
5. **Never sign a gate; never certify a public claim** (D-002, and the HANDOFF verification
   partition: public claims, autonomy NONE).

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

**73/73 Foundry · 405/405 TypeScript · 146/146 verifier · 50 corpus fixtures · 7 samples ·
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
| A-042 | **The D-010 experiment run properly:** a schema-only build met a real signed refusal it had never seen. Everything §5.5.1 STATED matched first time; the envelope it omitted diverged, plus three defects in the section — all mine, all corrected. 101 → 146 tests |

## 5. Traces — what worked, and what was a dead end

**Dead ends and traps — do not repeat:**

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
