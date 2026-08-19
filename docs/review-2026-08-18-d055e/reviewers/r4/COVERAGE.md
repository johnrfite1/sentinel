# R4 — COVERAGE — what I actually ran, and what I did not reach

Commit `7e0ab7f`. I am the **free lens**: `docs/d055e-scope-manifest.md` states R4 is absent from
`check-review-scope.sh`'s patterns deliberately and "ranges over all of it". So I have **no
assigned surface to have skipped** — but that makes an honest statement of what I actually
exercised more important, not less, because "ranges over all of it" is not a coverage claim and
must not be read as one.

## Where I chose to look, and why

My selection rule was the r4 brief's own suggestion: **the things nobody has been assigned to
distrust are the things everyone assumes.** I looked for load-bearing claims that were either
(a) explicitly de-scoped from review, (b) designated as authority by another document, or
(c) numeric and cheap to falsify by measurement.

1. **The round-six preservation record** — chosen because `docs/d055e-scope-manifest.md`
   *explicitly excludes* those 15 files from the remediation surface on the strength of their
   fidelity being already disclosed, and because round six is the round the exit criterion was
   backtested against. Nobody is assigned to it by construction.
2. **The accepted-limits ledger (§11.0)** — chosen because COMMON-BRIEF rule 5 tells every
   reviewer to treat it as the baseline of what is already known. A baseline nobody audits.
3. **The two smallest gate guards** — chosen because prior rounds hammered the large ones
   (`check-secrets`, `check-vendor-honesty`, `check-class-coverage`, `check-gate-immutability`)
   and because "absence reads as agreement" lives in short scripts.
4. **Every published count** — chosen because "a published number can be true once" is on the
   project's own list of its defect shapes, and because counts are falsifiable in one command.

## Actually executed

| | Ran | Result |
|---|---|---|
| `forge build --root contracts` | yes | 34 files, Solc 0.8.28, successful |
| `forge test --json` (contracts) | yes | **75 tests, 75 passed** |
| `npm test` (ts, TAP) | yes | **513 tests, 513 pass, 0 fail, 0 skipped, 0 todo** |
| `python3 verifier/test_verifier.py` | yes | **Ran 209 tests, OK** (49.7s) |
| `verify.py --all fixtures/samples` | yes | **7/7 sample(s) verified** |
| `verify.py --all … --tamper all` | yes | **78 tamper self-test PASS**, 7/7 behaved as expected |
| `scripts/check-eval-codes.sh` | yes | 41/41 · **mutated twice**, see R4-F3 |
| `scripts/check-type-strings.sh` | yes | 6/6 · **mutated twice**, see R4-F3 |
| `scripts/check-class-coverage.sh` | yes | pass on ratchet; 6 carried, 1 GAP |
| `shasum -c` over round-six archive | yes | **971/971 OK** |
| `cmp` on 11 preserved round-six files | yes | 10 identical, 1 one-line disclosed diff |
| Corpus class/outcome walk (50 fixtures) | yes | reproduced the `G-3` mechanism independently |
| Full-tree `cmp` vs pristine, post-mutation | yes | **364 files, 0 differ** |

## NOT run, and why

- **The deep gate (`./scripts/test.sh --gate`).** Deliberately not run. REVIEW-STATE assigns the
  deep gate at exactly `7e0ab7f` to R1, and R1 has completed it. Running a second concurrent gate
  is the round-five `D-11` failure and the round-six concurrency failure in one. I checked for a
  gate in flight with `pgrep -f sentinel-gate` (the correct pattern per the manifest), not with
  `pgrep -f scripts/test.sh`.
- **The fast gate.** Same reason. I ran the individual stages I needed directly instead.
- **`scripts/mutate.sh`** (131 mutations, ~30 min per full sweep). I **read** it closely and
  enumerated its targets — that produced the observation in "leads" below — but I did not run a
  sweep. Cost, and the concurrency cap.
- **`scripts/check-secrets.sh`, `check-vendor-honesty.sh`, `check-gate-immutability.sh`,
  `check-label-integrity.sh`, `check-label-prompt.sh`, `check-rename-gate.sh`.** Read
  `check-label-integrity.sh`, `check-label-prompt.sh` and `check-rename-gate.sh` in full and
  found nothing I could falsify in the time; did **not** audit the three large ones. They are
  R1's surface and have a heavy prior-round history.
- **`verifier/verify.py` (120 KB) internals.** Ran its suite and both sample walks; did not read
  or attack the implementation. R1's surface, and it has had four consecutive rounds of directed
  attention.
- **`contracts/src/SentinelVault.sol` semantics, the invariant campaign, the corpus/ablation
  generators.** R3's surface, and R3 was dispatched in the same wave as me. I touched the corpus
  **results** only as read-only data to reproduce `G-3`.
- **`ts/src/signer`, `evaluate`, `decode`, `simulate`, `propose` behaviour.** R2's surface. I read
  `ts/src/evaluate/hashes.ts` and `ts/test/differential.test.ts` as a *seam* question (three
  independent EIP-712 implementations, one guard covering two of them) and recorded the result as
  NULL-RESULTS N3/N6; I did not attack the evaluator.
- **Gate 7 / prompt injection.** Read `canary.ts`'s report path and `fixtures/injection/`;
  confirmed the canary has exactly one recorded run (2026-08-16, `claude-haiku-4-5`, agrees with
  its pinned fixture). **I made no live API call.** I did not exercise the injection path.
- **`docs/gate-5-vendor-audit.md` (34 KB) and Gate 5.** Not opened. This is the largest single
  document I did not reach and I flag it as my biggest gap.
- **`HANDOFF.md`, `README.md`, `docs/gate-s1-evidence.md`, most of `decisions.md` (434 KB).**
  Searched, not read. `decisions.md` I read only at `:243` (A-076) and `:53` (D-026 citation).

## Leads — NOT findings, not reproduced

Recorded so they are not lost, and labelled so they are not counted.

- **LEAD-1: `ts/src/evaluate/hashes.ts` has zero mutation coverage.** `scripts/mutate.sh` carries
  131 mutations; `src/signer/eip712.ts` gets 3 and `src/evaluate/hashes.ts` gets **none**, though
  it is one of the three implementations A-013 requires to be independent and is imported by the
  corpus runner, `sample-check`, `emit-samples` and five test files. I did **not** demonstrate a
  surviving mutant there — `differential.test.ts` holds all three implementations against
  Solidity over 4 seeds plus a boundary case, and would plausibly catch a value-order swap. Worth
  one directed mutation next round; I did not run it.
- **LEAD-2: `mutate.sh`'s TypeScript arm has no compile/lint separation.** Its Solidity arm was
  repaired specifically so a mutant that fails to build is reported `ERROR (not a measurement)`
  rather than `caught`, with a comment explaining that crediting the compiler to the suite
  "would inflate exactly the number the gate evidence cites". The TypeScript arm two lines down
  has no equivalent branch. In practice `npm test` does not typecheck (Node strips types), so
  the exposure is limited to mutants that produce a *syntax* error, and I did not construct one.
  This is the shape the repair protocol calls generalising the demonstration rather than the
  argument, but I have **not** demonstrated a live consequence and it is a lead only.
- **LEAD-3: `check-label-integrity.sh`'s unpinned-file sweep is `"$DIR"/*.json` only** — not
  recursive, and not extension-agnostic. A label artifact in a subdirectory or with another
  extension would be invisible to failure mode 3. No such file exists today.
