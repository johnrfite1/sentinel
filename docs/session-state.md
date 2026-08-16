# Sentinel — Session State

Rewritten at the end of each working session. **This file, not the conversation, is the
memory.** If it disagrees with anything an agent remembers, this file wins.

Last updated: **2026-08-15** (evening session), on branch `step-3/isolated-signer`
(the repository is PRIVATE and D-016 still blocks all publication).

---

## 0. If you read nothing else, read this

**Gate S1 is SIGNED — PASS, John, 2026-07-28**, scope bounded by D-018. **Gate S2 is NOT
signed**, is signed by John alone in a facilitated session, and never by an agent (D-002).

**All six items A-028 left owed are now built.** The §7.5 evidence pack is assembled at
`docs/gate-s2-evidence.md` and is UNSIGNED. Running the S2 session is the next thing, and it
is John's.

**Carry this forward, because it was the shape of every defect found in the last two
sessions:** the defects were *honesty* defects — a claim stronger than its evidence — and none
was found by the build loop's own checks. Mutation testing missed what line coverage caught;
line coverage missed what branch coverage would have caught; all three missed what an
adversarial reviewer caught. **Do not treat a green suite, a clean mutation run, or your own
re-reading as sufficient before claiming something is done.**

It happened again this session, in a smaller way and worth knowing about: two of the five
corpus mutations had been silently ERRORING since the guard they mutate was rewritten — a
mutation that cannot apply measures exactly as much as a test that cannot fail, and nothing
in the project re-runs the mutation harness after the code it mutates is repaired.

---

## 1. Read these first, in this order

1. `Sentinel_Protocol_Lab_Proposal_v0_2.md` — the spec. §14.8 and §14.9 supersede conflicting
   prose elsewhere in it. §5.7.1, §5.8 and §5.9 were added 2026-08-15 and are load-bearing.
2. `docs/decisions.md` — **canonical**. D-001…D-032 ratified; A-001…A-031 agent-flagged.
   **A-028 is the longest and most important entry**; **A-030 is an OPEN FORK for John.**
3. `docs/gate-s2-evidence.md` — the §7.5 pack, unsigned. Read §11 ("What is NOT in evidence")
   and §12 (the questions) before doing anything toward S2.
4. `HANDOFF.md` — the build brief: corridor, gates, house rules, verification partition.
5. `../AGENTS.md` — workspace rules. Binding. Not auto-loaded.
6. `../vault/Topics/AI-ML/prompting-agents-playbook.md` — the build-loop method.
7. `verifier/REPORT.md` — the D-010 independent reimplementation report. Still the single most
   useful document about where the specification is thin.

## 2. Authority — the line that matters most

**Agents propose; John decides.** Never sign a gate, ratify a decision, or resolve a product
fork. Routine engineering judgment is yours.

- **Gates S1 and S2 are signed by John**, in facilitated sessions. Prepare evidence and run
  the session; never answer or pre-fill it.
- **The five D-008 comprehension questions are held by John and must stay unseen.** Do not ask
  for them, guess them, or write substitutes. The build loop seeing them voids the check.
  Under D-032 that check is now a PRE-PUBLICATION condition, not an S2 one.
- D-007…D-011 were ruled by delegation and are revisitable on field evidence. Delegation
  covered design forks only — gate signing is not delegable.
- **A worked pattern for decision sessions:** present ONE fork at a time with verified facts,
  real options, costs, and a recommendation; record the ruling immediately, including the
  counter-argument and the condition that would reverse it.

## 3. Where the build actually is

**60/60 Foundry + 349/349 TypeScript + 70/70 verifier tests.** Run `./scripts/test.sh`; use
`--gate` for gate evidence (20,000 fuzz runs, 262,144 calls per invariant). It prints its own
coverage boundary — read all of it. That block is ONE statement, not a running log; when a
step lands, rewrite the affected layer rather than appending.

**Six mechanical guards run in the gate:** secrets (A-007), rename (D-016), labelling-prompt
freeze (D-011a), published EIP-712 type strings (D-023), §5.7.1 check coverage (D-031), and
**vendor honesty (§7.5 Gate 5, D-008)**. A seventh stage — the Gate 7 canary history — prints
and deliberately cannot fail the gate.

Done: §9 steps 1–9.

- **Steps 1–6** — typed payloads, vault, isolated signer, decoders, effect pipeline,
  conformance engine. See A-011…A-022.
- **§9 step 7** — `ts/src/propose/`, the agent-proposal seam. D-019 rules that Sentinel encodes
  calldata from the agent's typed arguments. The two-arm procedure now lives in
  `ts/src/spike/arms.ts`, shared by the spike and the canary.
- **§9 step 8** — `ts/src/corpus/`, 50 fixtures across all 20 §7.1 classes, executed against a
  real chain with per-fixture snapshot isolation. **The `malicious-retrieved-instructions`
  class is no longer vacuous** (A-028 F-5): both fixtures carry an `agentRationale`, F049's
  verbatim from the pinned recording, are transcribed through the untrusted proposal seam, and
  the run fails if any phrase of the narrative reaches a bound field, a check, a reason code,
  or the evidence bundle.
- **Independent labelling** — **labellers E and F are the labels of record.** Round 1 (A/B)
  scored a spec since amended; round 2 (C/D) was **discarded as contaminated** (A-028 F-1).
  **Labeller G (2026-08-15) is a two-fixture re-check**, not a round: it re-labelled F049 and
  F050 after the view gained the rationale field, agreed with E and F on both, and — unprompted
  — produced the finding recorded as A-030.
- **§7.2 baseline + §7.3 ablation** — `ts/src/ablation/`, report at `docs/ablation-report.md`.
  **False allows 38 / 17 / 1**; detection contribution — baseline alone 9, effect extraction
  adds 20, mandate conformance adds **17**; exact match 12 / 32 / 49 of 50; inter-labeller
  disagreement 0.0% on a freshly drawn sample. **These numbers did not move this session** —
  the corpus was re-run twice and the only diffs were chain timestamps and latency.
- **D-010 verifier** — `verifier/`, Python, zero third-party dependencies, built by an agent
  that never read `ts/`. **6/6 samples verify, 42/42 applicable tamper cases behave as
  specified, 70/70 of its own tests pass.** The sixth sample is `edge-single-reason-code`
  (A-027): nothing had pinned the single-element case of `reasonCodesHash`.
- **Gate 7's live canary** — `npm --prefix ts run canary`. First live run 2026-08-15:
  `claude-haiku-4-5`, INJECTION LANDED, **agrees with the pinned recording**. History at
  `fixtures/injection/canary-history.jsonl`; `./scripts/test.sh` prints it every run.

## 4. Decisions and findings

D-019…D-032 were ratified 2026-08-15 (see the index in `decisions.md`; D-032 split §7.5's
gates). Added since:

| | Subject |
|---|---|
| A-029 | The labeller views are not byte-reproducible — chain time flows into entitlement expiry |
| A-030 | **OPEN FORK for John** — the specification has become a contamination channel for labellers, and the frozen prompt no longer matches it |
| A-031 | The five owed items are built; three agent-made design calls recorded, one flagged reversible |

## 5. What to do next, in order

1. **Run Gate S2 as a facilitated session.** The pack is `docs/gate-s2-evidence.md`; its §12
   lists five questions, none of them an agent's call. Gate 5 is PART MET by construction —
   its two certification conditions are John's and no agent may clear them.
2. **Put A-030 to John before the next labelling round.** Every available response changes a
   ratified protocol, so it cannot be resolved in the build loop. Nothing is blocked on it
   today: the labels of record stand and G agreed with them.
3. **§9 steps 7–8 have never had an independent review.** Steps 4–6 had a full adversarial pass
   (A-022); steps 1–3's earlier review (A-016) had most of its verifications cut short by a
   spend limit, and that limit is NOT retired by the later review. This is the largest
   remaining hole in the evidence, and this session's own work is inside it.
4. **A-029, if John wants it fixed before S2.** Diagnosis and the reason it was not fixed under
   time pressure are in the entry.
5. **Gate 8 and the rename gate** are PRE-PUBLICATION (D-032, D-016), and Gate 8 additionally
   needs the dashboard D-009 holds outside S2.

**Carried and still true:** three separate times before 2026-08-15, and four times during it,
code shipped whose tests could not fail. Run `./scripts/mutate.sh` after any substantive
change, check *branch* coverage not just line coverage, and prefer an independent reviewer over
your own re-reading for anything you are about to call done.

## 6. Traces — what worked, and what was a dead end

The pre-2026-08-15 entries below the line still hold. Added since:

**Dead ends and traps — do not repeat:**

- **A mutation harness rots silently when the code it mutates is repaired.** Two of the five
  corpus mutations had anchors from a guard that was rewritten one commit earlier, and had been
  reporting "anchor not unique" ever since. The counter distinguishes errors from catches, so
  nothing false was published — but nobody looked. **Re-run the affected batch as part of any
  fix to the code it targets.**
- **A `forge test` exit code does not distinguish "the suite caught it" from "it did not
  compile".** With `deny = "warnings"`, deleting a check that leaves an unused variable breaks
  the build, and a naive harness scores that as caught — the instrument reading as maximally
  effective at the moment it is broken. Build first, report a non-compiling mutant as an error.
- **Two mutation batches must not share a letter.** `mutate.sh S` now matches both the simulate
  batch and the vault batch. Harmless but confusing; the vault batch kept `S1…S20` deliberately
  so its ids match `docs/review-2026-08-15/artifacts/sol_mutants.json`.
- **A denylist matched by substring only catches the spellings it declares.** (Carried from the
  earlier session; the leakage guard was wrong twice for this reason.) The working shape is a
  **recursive key walk using `contains`, plus a declared allowlist** — and where the two
  conflict, the allowlist wins, because a decision must overrule a heuristic.
- **A name-based guard cannot catch a semantic leak.** Only the shape allowlist catches a field
  that carries evaluator output under an innocuous name.
- **A `for` loop whose body `continue`s on every element is a test that cannot fail.**
- **Do not summarise ratified decisions for an independent labeller**, and **do not reuse a
  sample across labelling rounds**.
- **A mutation named for a hole is not a mutation that tests it.** Check that it reaches the
  code it names.
- **The corpus runner picks a random port and occasionally collides.** Re-run before diagnosing.

**What worked:**

- **Adversarial review with a fixed commit, told to prove the work fails.** Four lenses found
  eight material defects in one pass, including one live security defect the entire test suite,
  mutation harness, and two prior reviews had missed.
- **Asking an independent agent for a provenance attestation.** It has now produced a
  first-order finding twice, from two different labellers, both unprompted: the harness-injected
  memory file (E), and the specification-as-contamination-channel finding (G, A-030). **Ask for
  it every time.**
- **Deriving a guard's probes from the data it guards.** `rationale.ts` builds its probe set
  from the fixture's own rationale as word bigrams, so adding a fixture extends the guard and
  editing one re-aims it. A hand-written phrase list can only ever confirm the phrases it lists.
- **Making a guard state what it cannot check.** `check-vendor-honesty.sh` fails on the
  mechanical conditions and prints the other two as UNCERTIFIED, never as a pass. A gate that
  reports a pass for a condition no machine evaluated is worse than no gate.
- **Implementing a spec amendment from the amended text, via the party that found the gap.**
- **Measuring a rejected option instead of arguing about it.**

---

*Entries below this line predate 2026-08-15 and are unchanged.*

## 7. Pre-existing traces

- **Do not make non-vacuity an `afterInvariant` hook.** Foundry shrinks a failing sequence to
  its minimum, and any one-call sequence has zero executions by construction. Non-vacuity lives
  in `test_nonVacuity_*` deterministic tests.
- **Do not randomize every dimension inside one invariant handler action.** 16,384 calls, zero
  executions, all invariants PASS. Make validity its own action.
- **`forge` caches invariant failures in `contracts/cache/invariant/`.** `rm -rf cache/invariant`
  before trusting any invariant debugging.
- **A `// forge-lint: disable-next-line(...)` directive must be the line immediately before the
  code.**
- **`Promise.all([f(await g()), f(await h())])` is NOT concurrent.**
- **A socket-level test cannot observe the signer's reserve-versus-sign ordering.** It is
  observable only in-process with a deliberately slow signer.
- **Do not measure mutation results by parsing the `node:test` reporter.** Use exit status, and
  assert the mutation actually applied.
- **`scripts/check-secrets.sh` scans TRACKED files.** Use `--staged` after `git add`. The same
  is true of `check-vendor-honesty.sh`: an uncommitted artifact is not scanned.
- **Do not run an adversarial review while still editing the tree.** Freeze, then review.
- **A mutation set written by the implementer probes only the checks the implementer already
  thought about.** Enumerate the code's own declared surface and assert exhaustiveness
  structurally.

**Environment facts:**

- Foundry v1.7.1 at `$HOME/.foundry/bin` — **not on the agent's non-interactive PATH**; export
  it explicitly. `scripts/mutate.sh` now does this itself.
- Node v26.3.0, npm 11.16.0, viem 2.55.10. The signer runs under Node's native type stripping,
  which requires erasable syntax only: no enums, no namespaces, no constructor parameter
  properties, and relative imports must carry the `.ts` extension.
- `.env` exists, is gitignored, holds `ANTHROPIC_API_KEY`. The pre-commit hook blocks it.
- **Claude Opus 5 rejects `temperature`/`top_p`/`top_k` (400)** and has thinking on by default.
- **A full `contracts` rebuild is `forge build --force`.** After a Solidity mutation sweep,
  `contracts/out` holds the LAST mutant's bytecode — rebuild before emitting samples, or the
  artifacts are signed against a deliberately broken vault.

## 8. Verification tooling

`scripts/mutate.sh` — deliberate defects across signer, decoders, pipeline, evaluator, the
D-012/D-014 rulings, the D-017 corrections, the step-7 transcriber (batch `P`), the ablation
layers (batch `B`), the corpus guards (batch `C`), and **the vault (batch `S`, Solidity)**. Run
`./scripts/mutate.sh` for all or `./scripts/mutate.sh C` for one batch. **Get the count by
running it, not by grepping.** A full sweep now takes well over an hour and is not wired into
`test.sh`.

Latest measured results: **batch C 11/11 caught**, **batch S 26/26 caught** (20 vault + 6
simulate), 0 survived, 0 failed to apply. The vault batch's numbers are **not** comparable to
A-028's "29 of 45 survived" — the tests that kill these mutants were written for them.
