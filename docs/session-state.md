# Sentinel — Session State

Rewritten at the end of each working session. **This file, not the conversation, is the
memory.** If it disagrees with anything an agent remembers, this file wins.

Last updated: **2026-08-15**, at commit `216c570` on branch `step-3/isolated-signer`
(pushed; the repository is PRIVATE and D-016 still blocks all publication).

---

## 0. If you read nothing else, read this

**Gate S1 is SIGNED — PASS, John, 2026-07-28**, scope bounded by D-018. Gate S2 is NOT signed
and is signed by John alone, in a facilitated session, never by an agent (D-002).

**Four independent adversarial reviews ran on 2026-08-15 at commit `9059346` and found real
defects, most of them in work done that same day.** The full record is **A-028** in
`docs/decisions.md` — read it before building on anything here. Headline: one LIVE code defect
inside Gate S1's signed scope (since fixed), a test that could not fail, a contaminated
labelling round, a leakage guard bypassed by any prefixed key with a live leak already through
it, and several overstated numbers in the ablation report.

**All of the above are now remediated except the items listed in §5.** The suite is green and
the numbers in this file are post-remediation.

**The pattern worth carrying forward, because it recurred four times in one session:** every
one of those defects was an *honesty* defect — a claim stronger than its evidence — and none
was found by the build loop's own checks. Mutation testing missed what line coverage caught;
line coverage missed what branch coverage would have caught; all three missed what an
adversarial reviewer caught. **Do not treat a green suite, a clean mutation run, or your own
re-reading as sufficient before claiming something is done.**

---

## 1. Read these first, in this order

1. `Sentinel_Protocol_Lab_Proposal_v0_2.md` — the spec. §14.8 and §14.9 supersede conflicting
   prose elsewhere in it. §5.7.1, §5.8 and §5.9 were added 2026-08-15 and are load-bearing.
2. `docs/decisions.md` — **canonical**. D-001…D-032 ratified; A-001…A-028 agent-flagged.
   **A-028 is the longest and most important entry in the file.**
3. `HANDOFF.md` — the build brief: corridor, gates, house rules, verification partition.
4. `../AGENTS.md` — workspace rules. Binding. Not auto-loaded.
5. `../vault/Topics/AI-ML/prompting-agents-playbook.md` — the build-loop method.
6. `verifier/REPORT.md` — the D-010 independent reimplementation report. Still the single most
   useful document about where the specification is thin.

## 2. Authority — the line that matters most

**Agents propose; John decides.** Never sign a gate, ratify a decision, or resolve a product
fork. Routine engineering judgment is yours.

- **Gates S1 and S2 are signed by John**, in facilitated sessions. Prepare evidence and run
  the session; never answer or pre-fill it.
- **The five D-008 comprehension questions are held by John and must stay unseen.** Do not ask
  for them, guess them, or write substitutes. The build loop seeing them voids the check.
- D-007…D-011 were ruled by delegation and are revisitable on field evidence. Delegation
  covered design forks only — gate signing is not delegable.
- **A worked pattern for decision sessions**, used throughout 2026-08-15 and worth repeating:
  present ONE fork at a time with verified facts, real options, costs, and a recommendation;
  record the ruling immediately, including the counter-argument and the condition that would
  reverse it. Twelve decisions (D-020…D-032) were taken this way in one session.

## 3. Where the build actually is

**43/43 Foundry + 341/341 TypeScript.** Run `./scripts/test.sh`; use `--gate` for gate evidence
(20,000 fuzz runs, 262,144 calls per invariant). It prints its own coverage boundary — read all
of it. That block is ONE statement, not a running log; when a step lands, rewrite the affected
layer rather than appending.

**Five mechanical guards now run in the gate:** secrets (A-007), rename (D-016), labelling-prompt
freeze (D-011a), published EIP-712 type strings (D-023), and §5.7.1 check coverage (D-031).

Done: §9 steps 1–8 and most of 9.

- **Steps 1–6** — typed payloads, vault, isolated signer, decoders, effect pipeline,
  conformance engine. See the prior entries A-011…A-022.
- **§9 step 7** — `ts/src/propose/`, the agent-proposal seam. D-019 rules that Sentinel encodes
  calldata from the agent's typed arguments. `propose.e2e.test.ts` drives both arms of the
  pinned `claude-haiku-4-5` recording through to the vault.
- **§9 step 8** — `ts/src/corpus/`, 50 fixtures across all 20 §7.1 classes, executed against a
  real chain with per-fixture snapshot isolation.
- **Independent labelling** — **labellers E and F are the labels of record.** Round 1 (A/B)
  scored a spec since amended; round 2 (C/D) was **discarded as contaminated** (A-028 F-1). All
  four earlier files are retained as audit trail. E and F carry provenance attestations.
- **§7.2 baseline + §7.3 ablation** — `ts/src/ablation/`, report at `docs/ablation-report.md`.
  Post-remediation: **false allows 38 / 17 / 1**; detection contribution — baseline alone 9,
  effect extraction adds 20, mandate conformance adds **17**; exact match 12 / 32 / 49 of 50;
  inter-labeller disagreement 0.0% on a freshly drawn sample.
- **D-010 verifier** — `verifier/`, Python, zero third-party dependencies, built by an agent
  that never read `ts/`. 5/5 samples verify, all tamper modes rejected, 70 tests. It now checks
  `reasonCodesHash` and the §5.5 override, and it **retired its own chain-binding concern on
  evidence** after constructing the cross-deployment case.

## 4. Decisions taken 2026-08-15 (D-019…D-032)

Read them in `docs/decisions.md`; this is an index, not a substitute.

| | Subject |
|---|---|
| D-019 | Sentinel encodes calldata from the agent's typed args; §4.2 Case 2 amended |
| D-020 | Mandate purpose fields compare for EQUALITY, not as ceilings |
| D-021 | A reverting simulation is a FAILED RULE and blocks |
| D-022 | `reasonCodesHash` defined in §5.4; verifier extended to check it |
| D-023 | EIP-712 type strings published in §5.8 and guarded; override sample added |
| D-024 | Verdict/FailureMode/Operation enums documented in §5.9, with the inversion warned |
| D-025 | `allowedCallGraphHash` is RESERVED in v1 and not consulted |
| D-026 | The EXECUTABILITY class added; §3.3(7)'s remedy clause narrowed |
| D-027 | §5.7's code-hash line aligned with D-015 (evidence check, not failed rule) |
| D-028 | Undecodable calldata is an evidence gap; the asymmetry named not removed |
| D-029 | A failed rule takes precedence over an unresolved check |
| D-030 | "Conflicting state" is a failed rule — **with John's caveat recorded** |
| D-031 | §5.7.1 documents all 41 checks; `check-eval-codes.sh` guards coverage |
| D-032 | §7.5 split: six gates are S2 conditions, Gate 8 is PRE-PUBLICATION |

**A-023…A-028** are the agent-flagged findings from the same day, including the D-019 revisit
measurement, the corpus construction findings, and the four-review record.

## 5. What to do next, in order

1. **The vacuous `malicious-retrieved-instructions` class (A-028 F-5).** `FixtureSpec` has no
   field for an agent rationale, so F049 and F050 are byte-identical to F009 and F012 apart
   from mandate identity — the adversarial text reaches the labeller and never reaches the
   pipeline. Currently DISCLOSED in the ablation report but not fixed. Fixing it means adding
   a rationale field to the fixture format and carrying it into the run. **Note this changes
   the labeller view's declared shape**, so `ALLOWED_VIEW_KEYS` in `ts/src/corpus/leakage.ts`
   must be updated deliberately — that guard exists precisely to make the change conscious.
2. **The Solidity mutation gap.** `scripts/mutate.sh` is TypeScript-only, and A-028's F2, F5
   and F6 all live in that gap — §3.3(9)'s "nonce consumed before the external call" is
   verified by nothing, the vault's `allowedSelector` backstop and `WrongVault` check are
   uncovered, and `executeWithOverride` is absent from the invariant campaign's handler set.
   **A ready-made regression test for the ordering property is already written and verified**
   at `docs/review-2026-08-15/artifacts/OrderingProbe.t.sol` — it passes on HEAD and fails
   under the S7 mutation. It sits outside `contracts/test/` deliberately so Foundry does not
   compile it; moving it in is the remediation decision.
3. **Gate 5's missing vendor-honesty check (D-032 keeps this an S2 condition).** D-008 says the
   empty-column condition "is mechanically checkable" and no check exists. Write
   `scripts/check-vendor-honesty.sh` and wire it into the gate beside the others. Also owed: an
   audit of §2's capability table against D-008's conditions — every cell documentation-only,
   dated, linked to its source, inference marked as inference.
4. **Gate 7's live canary.** D-007 requires one live run alongside the pinned transcripts,
   never failing CI, with its run history in the S2 evidence bundle — "an unobserved canary is
   not evidence." Not built. Nothing in the suite calls a model.
5. **A single-reason-code sample fixture (A-027).** No sample has exactly one reason code, so
   nothing pins the no-trailing-delimiter edge in `reasonCodesHash`; a producer emitting
   `code + "\n"` for a single-element set would pass every shipped fixture.
6. **Assemble the §7.5 pack and run Gate S2 as a facilitated session.** A draft of the pack
   exists at `docs/review-2026-08-15/gate-s2-hard-gates-draft.md` — **it predates D-032 and
   still treats Gate 8 as an S2 condition, so it needs updating before use.**

**Carried and still true:** three separate times before this session, and four times during it,
code shipped whose tests could not fail. Run `./scripts/mutate.sh` after any substantive change,
check *branch* coverage not just line coverage, and prefer an independent reviewer over your own
re-reading for anything you are about to call done.

## 6. Traces — what worked, and what was a dead end

The pre-2026-08-15 entries below the line still hold. Added this session:

**Dead ends and traps — do not repeat:**

- **A denylist matched by substring only catches the spellings it declares.** The leakage guard
  was fixed twice and was wrong both times: first it lowercased the haystack but not the needle
  (so `reasonCodes` never fired), then it matched `"key"` with both quotes (so `engineVerdict`
  and every other prefixed name passed). Testing it with the exact names it declares can only
  ever confirm those names. The working shape is a **recursive key walk using `contains`, plus
  a declared allowlist** — and where the two conflict, the allowlist wins, because a decision
  must overrule a heuristic.
- **A name-based guard cannot catch a semantic leak.** `calldataDecodedByASupportedSchema`
  carried the evaluator's decoder output under a name containing no forbidden word. Only the
  shape allowlist catches that class.
- **A `for` loop whose body `continue`s on every element is a test that cannot fail.** Measured:
  0 of 7. It read as a limit assertion and asserted nothing.
- **Do not summarise ratified decisions for an independent labeller.** The C/D round was
  contaminated because the brief quoted D-025, which was derived by reading the evaluator.
  Give labellers the specification and deny `docs/` — including `decisions.md`.
- **Do not reuse a sample across labelling rounds.** Round 2 reused round 1's ten fixture ids,
  so its disagreement rate re-measured a question already settled between the rounds. Draw a
  fresh sample with a salted hash.
- **A mutation named for a hole is not a mutation that tests it.** `V2` was named "treat
  decoded:false as a blanket escape hatch" and mutated a different branch, reporting caught
  while the hatch sat open. Check that a mutation actually reaches the code it names.
- **The corpus runner picks a random port and occasionally collides.** A failed run is usually
  transient; re-run before diagnosing.

**What worked:**

- **Adversarial review with a fixed commit, told to prove the work fails.** Four lenses found
  eight material defects in one pass, including one live security defect the entire test suite,
  mutation harness, and two prior reviews had missed. Every one of the four also reported what
  it attacked and could NOT break, which is what makes the positive findings trustworthy.
- **Asking a reviewer to settle its own concern with evidence rather than argument.** The D-010
  verifier raised the §5.5 chain-binding worry, then constructed the cross-deployment case and
  **retired its own concern**, showing the two binding mechanisms are independent rather than
  redundant. A retired concern is as valuable as a confirmed one.
- **Requiring provenance attestation from labellers.** Labeller E disclosed, unprompted, that
  it had seen two filenames in `labels/` and that the harness injects a workspace memory file —
  neither of which it had to volunteer, and the second of which nobody had considered.
- **Implementing a spec amendment from the amended text, via the party that found the gap.**
  The verifier built `reasonCodesHash` from the new §5.4 and immediately found three defects in
  the wording — including a published regex that admits a hash collision in Python and Ruby.
  **Documentation written to close a finding is itself unreviewed work.**
- **Measuring a rejected option instead of arguing about it.** D-019's rejected branch was
  re-tested on John's direction (A-023); 4 of 4 proposals across two models produced undecodable
  calldata, settling it more firmly than the original reasoning had.

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
- **`scripts/check-secrets.sh` scans TRACKED files.** Use `--staged` after `git add`.
- **Do not run an adversarial review while still editing the tree.** Freeze, then review.
- **A mutation set written by the implementer probes only the checks the implementer already
  thought about.** Enumerate the code's own declared surface and assert exhaustiveness
  structurally.

**Environment facts:**

- Foundry v1.7.1 at `$HOME/.foundry/bin` — **not on the agent's non-interactive PATH**; export
  it explicitly.
- Node v26.3.0, npm 11.16.0, viem 2.55.10. The signer runs under Node's native type stripping,
  which requires erasable syntax only: no enums, no namespaces, no constructor parameter
  properties, and relative imports must carry the `.ts` extension.
- `.env` exists, is gitignored, holds `ANTHROPIC_API_KEY`. The pre-commit hook blocks it.
- **Claude Opus 5 rejects `temperature`/`top_p`/`top_k` (400)** and has thinking on by default.

## 8. Verification tooling

`scripts/mutate.sh` — deliberate defects across signer, decoders, pipeline, evaluator, the
D-012/D-014 rulings, the D-017 corrections, the step-7 transcriber (batch `P`), the ablation
layers (batch `B`), and the corpus guards (batch `C`). Run `./scripts/mutate.sh` for all or
`./scripts/mutate.sh E` for one batch. **Get the count by running it, not by grepping.** A full
sweep takes ~30 minutes and is not wired into `test.sh`.

**It is TypeScript-only.** There is no Solidity mutation harness, and A-028 measured 20 of its
own Solidity mutations surviving a green suite. That is item 2 in §5.

**Standing warning:** the harness once left `ts/src` empty by restoring with
`rm -rf src; cp -R backup src` and being killed mid-restore. It now touches one file at a time
and traps TERM. **A repair tool must never have a window in which the thing it repairs does not
exist**, and uncommitted work is the only work that cannot be recovered — commit first.
