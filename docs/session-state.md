# Sentinel — Session State

Rewritten at the end of each working session. **This file, not the conversation, is the
memory.** If it disagrees with anything an agent remembers, this file wins.

Last updated: **2026-08-15** (long evening session), branch `step-3/isolated-signer`, pushed.
The repository is PRIVATE and D-016 still blocks all publication.

---

## 0. If you read nothing else, read this

**Gate S1 is SIGNED — PASS, John, 2026-07-28.** **Gate S2 is NOT signed**, is signed by John
alone in a facilitated session, and never by an agent (D-002, non-delegable).

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

### 1. Collect the D-035 measurement (launched 2026-08-15; may already be recorded)

D-035 ruled: run the control labeller over **F001, F009, F025, F049, F056** and compare with
the labels of record. If no result is recorded in `fixtures/corpus/labels/`, run it:

- Control specification: `git show 052b3af:Sentinel_Protocol_Lab_Proposal_v0_2.md` written to a
  scratch path — the spec BEFORE the §4.2 walkthrough and before every 2026-08-15 amendment.
- Model: `claude-opus-5` (same as E and F, so the spec text is the only variable).
- Brief: copy labeller K's. `fixtures/corpus/labels/labeller-K.provenance.json` records the
  exact denials. **Require the provenance attestation** — six labellers for six have produced a
  first-order finding in it, unprompted.
- Record as `labeller-<letter>-control.json` + `.provenance.json`. These are AUDIT TRAIL:
  `report.ts` reads only `labeller-E.json` and `labeller-F.json`, so adding files moves no
  published number.

**THE THRESHOLD IS DECLARED IN ADVANCE (D-035): two or more of the five moved means the channel
is systematic, the sample has stopped being a bound, and a full re-freeze plus re-label of all
50 escalates to John.** One movement is consistent with F051 being the known case. **Do not
soften this after seeing the result.**

### 2. Then part (c) of D-035 — and only as far as it goes

The offending passages are a **v1.1** correction, not a v1 re-freeze. **Do NOT edit §4.2 or
§5.7.1 to remove the worked examples** — that edits the specification to serve the measurement,
and D-035 explicitly does not authorise it. Record what should change; leave it.

### 3. Prepare Gate 5's certification for John; do not perform it

`docs/gate-5-vendor-audit.md` holds a completed source-verification pass — all nine cited pages
fetched and read 2026-08-15. Five rows hold. **Four do not:**

| Row | What the cited page does not support | Proposal (John certifies) |
|---|---|---|
| 7 Hypernative | "intent verification" appears nowhere on it | strike, or mark `(inference)` |
| 2 Coinbase; Privy | holds for Privy only; "signer" for neither | split the row |
| 5 Safe | Guards page documents Guards; 4 of 5 claims absent | re-cite, or narrow to Guards |
| 3 Circle | "agent-native execution" is a characterisation | mark `(inference)` |

**Every discrepancy overstates a COMPETITOR, never Sentinel.** Once John rules, the marker
`[§13#N read YYYY-MM-DD]` on each capability cell makes D-008(1) mechanical —
`check-vendor-honesty.sh` already counts it and reports `0 of 9`.

**An agent may not write those cells.** Prepare the diff; put it in front of him.

### 4. Run Gate S2 as a facilitated session

Pack: `docs/gate-s2-evidence.md`. Read §11 (what is NOT in evidence) and §12 (the questions)
first. **Gate 5 is NOT MET** until step 3 resolves — 0 of 9 rows are dated or linked, which is
unsatisfied rather than merely uncertified.

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

**66/66 Foundry · 380/380 TypeScript · 70/70 verifier · gate green at the deep profile.**

Run `./scripts/test.sh`; use `--gate` for evidence. Read the coverage boundary it prints — it is
ONE statement, not a log; rewrite the affected layer when a step lands, never append.

**Seven mechanical guards run in the gate:** secrets (A-007), rename (D-016), labelling-prompt
freeze (D-011a), EIP-712 type strings (D-023), §5.7.1 check coverage (D-031), vendor honesty
(§7.5 Gate 5, D-008), and — deep profile only — **the §7.1 corpus executed with its committed
views verified**. The Gate 7 canary history prints and deliberately cannot fail the gate.

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
- **Labellers:** E and F are the labels of record. G, H, J, K (and L, if recorded) are targeted
  measurement arms and are audit trail only. **A-033 as first written was wrong and is corrected
  in place** — the contamination channel moved one label (F051), measured by K.

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
- **The corpus runner picks a random port and occasionally collides.** Re-run before diagnosing.
  Concurrent runs also contend — nine spurious failures came from a mutation sweep running
  beside the suite.

**What worked:**

- **Adversarial review at a fixed commit, told to prove the work fails.** Four reviews, ~24
  material findings, several missed by the suite, the mutation harness and prior reviews. Give
  each a FROZEN tree — `git worktree add <scratch> <commit>` with `node_modules` symlinked
  works and lets you keep editing.
- **Requiring a provenance attestation from every labeller.** Six for six produced a
  first-order finding this way, unprompted: the harness-injected memory file (five times), the
  specification-as-contamination-channel, the published reason codes, `failureMode`'s undefined
  encoding, and a labeller declining an injected instruction that would have breached the
  protocol.
- **Measuring a fork instead of arguing it.** D-033's control arm settled in one run what would
  otherwise have been unfalsifiable — then produced the counterexample that corrected A-033.
- **Single-variable experiment design.** H varied only the spec text; J varied only the model.
- **Declaring the escalation threshold BEFORE seeing the result** (D-035: two movements).
- **Making a guard state what it cannot check.** `check-vendor-honesty.sh` fails on the
  mechanical conditions and reports the other two as UNCERTIFIED, never as a pass.

## 6. Environment facts

- Foundry v1.7.1 at `$HOME/.foundry/bin` — **not on the agent's non-interactive PATH**.
  `scripts/mutate.sh` and `scripts/test.sh` export it themselves.
- Node v26.3.0, viem 2.55.10. The signer runs under Node's native type stripping: erasable
  syntax only, and relative imports need the `.ts` extension.
- `.env` is gitignored and holds `ANTHROPIC_API_KEY`. The pre-commit hook blocks it.
- **Claude Opus 5 rejects `temperature`/`top_p`/`top_k` (400).**
- **After a Solidity mutation sweep, `contracts/out` holds the LAST mutant's bytecode.** Run
  `forge build --force` before emitting samples, or the artifacts are signed against a
  deliberately broken vault.
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
