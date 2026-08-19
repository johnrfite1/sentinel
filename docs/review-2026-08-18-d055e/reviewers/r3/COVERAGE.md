# COVERAGE — Reviewer 3

What I actually ran, what I did NOT reach, and why. Written so a null is never read as coverage.

## Profile actually used

**FAST equivalent, plus targeted deep components.** I did NOT run `./scripts/test.sh --gate` end
to end. What I ran instead:

| Ran | Not run |
|---|---|
| `forge build --root contracts` (before anything) | the full `--gate` profile of `scripts/test.sh` |
| `forge test --root contracts` — full 75-test suite, ~40 times | `forge test --profile gate` (20 000 fuzz / 2 048 invariant runs) |
| `forge test --match-test '^invariant_'` — the 11-invariant campaign, ~35 times | |
| `cd ts && npm test` — 513 tests, baseline + TS mutation batch | |
| `bash scripts/check-class-coverage.sh` | the other eight gate guards |
| `npm run ablation` equivalent, via a pure out-of-tree call to `loadInputs()`+`buildReport()` | `npm --prefix ts run corpus` (see below) |

**Baseline recorded before any mutation:** forge 75/75, npm 513/513. Transcripts in
`baseline/`. Every mutation result in this report is measured against that.

## Deliberately NOT run: the corpus itself

`npm --prefix ts run corpus` rewrites `fixtures/corpus/for-labelling/` and
`fixtures/corpus/results/` **in place** unless `SENTINEL_CORPUS_OUT` is set. Those 100 files are
the artifacts the labels of record attest to. I judged the risk of destroying them in a review
worktree — and the risk of leaving a half-reverted corpus behind — to outweigh what a re-run
would have added, since every corpus question I had was answerable from the committed records.

**What that costs, stated so it is not read as coverage:**

* **I did not exercise the deep gate's `VERDICTCHECK` or `VIEWCHECK` end to end.** My brief asks
  "can you change an engine verdict and keep both artifacts byte-identical?" **I did not answer
  that question by running it.** I read both python blocks line by line and formed a view (the
  results comparison is genuine and covers `verdict`, `checks[].code`, `checks[].outcome` and
  `failing`; the two normalisations, `micros` and `\bnow \d+\b` in `detail`, are symmetric
  between fresh and committed and I found no asymmetric channel) — **but that is reading, not
  measurement, and it should be treated as a LEAD at most, not as a null result.** A reviewer
  with a disposable copy of the corpus should run it.
* I did not verify that a corpus re-run reproduces `_digests.json`.
* Anything visible only under `--gate` was out of reach for me, as it was for round five.

## Surfaces I was assigned and DID exercise

| Surface | Depth |
|---|---|
| `contracts/src/SentinelVault.sol` | **line by line, then 53 mutations attempted / 49 measured / 4 dead probes re-run**, each measured one against the 11-invariant campaign alone AND against the full suite; the 8 the campaign killed were re-run a third time with the campaign excluded |
| the deterministic + invariant Foundry suites | executed ~40 times; `invariants.t.sol` read fully (handler actions, selector registration, non-vacuity block); `backstops.t.sol` and `SentinelVault.t.sol` indexed by function and read closely around the receipt-binding and LIMIT tests |
| atomic-drain behaviour | `test_LIMIT_nativeCeilingIsPerActionAndBoundsNoAggregate` read fully with its control; §7.1's row and the NatSpec header read against the code; **probed for understatement and found none** (NULL N-4) |
| the invariant-campaign boundary | **measured independently**: see the table in REPORT.md; my figures are my own, not A-073's re-quoted |
| `ts/src/ablation/**` | all three files read fully; `report.ts` probed with three synthetic-input variants and two `WITHHELD` variants |
| `ts/src/corpus/**` | `run.ts`, `leakage.ts`, `rationale.ts` read fully; `spec.ts`/`fixtures.ts` read for structure only; leak guards probed with 8 synthetic views |
| `fixtures/corpus/**` | all 50 result records and all 50 labeller views parsed programmatically; per-field variance computed across the whole corpus |
| `G-5` | derivation re-checked against data; three residual prose branches reproduced |
| `D-10` | **12 TypeScript mutations, 0 dead probes**: the two pinned case sites and the one pinned field swap confirmed as controls (all KILLED), the seven unpinned case sites and the sibling field swap and the recurrence conjunction all swept (9 SURVIVED) |
| `D-09(c)` | **see NOT REACHED below** |
| NatSpec and §7.1 | read fully and checked against the code and the tests |

## What I did NOT reach

1. **`D-09(c)` — the intersected-ceiling regression.** My brief names it. I read register §13.5
   and §11.0's reopening, confirmed by measurement that `F006` diverges (mandate `1e18` vs policy
   `2e15`) and that it is the **only** one of 50 that does — which is the corrected premise —
   but I **did not** probe the `min`→`max` mutation on the intersection, and I did not look at
   the seven committed sample bundles or the D-010 verifier's reading of them at all. The
   verifier is R1's surface, but the *sample* side of D-09(c) is a real gap in my coverage.
2. **`contracts/test/SentinelTypes.t.sol` (386 lines) and `contracts/src/types/SentinelTypes.sol`
   (333 lines).** I read the payload structs for what they carry and confirmed
   `allowedTargetsHash` / `allowedSelectorsHash` / `purposeKind` appear only in the struct and
   the hash — but I ran **no** mutation against the typehash pinning. I took A-040's 4-way
   differential on the record, exactly as round five's vault lens did. **Two consecutive rounds
   have now declined to re-verify the same thing on the same grounds.**
3. **`contracts/src/demo/DemoPay.sol` and `DemoERC20.sol`.** Read once for the entitlement and
   allowance semantics the checks depend on. No probing.
4. **`ts/src/corpus/fixtures.ts` (570 lines) and `spec.ts`.** I derived everything about the
   fixtures from the committed *artifacts* rather than the generator. A defect in the generator
   that is faithfully reflected in the committed records is invisible to my method. `F002`'s
   misfiling question and the F026/F051 `allowedCallGraphHash` discrepancy raised by labeller K
   are both in this blind spot.
5. **The e2e vault configuration.** Round five's lens F named this as its own hole
   ("I never established what targets and selectors the shipped e2e vault actually allowlists")
   and cited A-040's ecrecover-precompile allowlist defect as unverified. **I did not close it
   either.** It is now a two-round-old unreached item on this surface.
6. **The other eight gate guards.** I ran only `check-class-coverage.sh`. `check-eval-codes.sh`,
   `check-label-integrity.sh`, `check-label-prompt.sh`, `check-type-strings.sh`,
   `check-vendor-honesty.sh`, `check-rename-gate.sh`, `check-gate-immutability.sh` and
   `check-secrets.sh` are R1's surface, but several bear on corpus artifacts that are mine.
7. **`scripts/mutate.sh` executed.** I read it and found S5's defect by reading (R3-F5). **I did
   not run it**, so I cannot say how many of its other Solidity mutants share the
   whole-statement shape that hides a half-tested conjunction. **That is the obvious next probe
   and I ran out of session before it.**
8. **No live model call.** No `.env`; the Gate 7 canary and every model-dependent arm went
   unexercised, as in every prior round.
9. **The gate profile's own honesty.** I did not check whether the COVERAGE BOUNDARY block
   printed by `scripts/test.sh` is currently true — R1's surface, and I stayed off it.
