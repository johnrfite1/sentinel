# A-EXTRACT — TWELFTH INDEPENDENT INSTRUMENT REVIEW

# VERDICT: HOLD

The exact eleventh-review correction closes `F11-1`. It changes one maintained sentence in
`COVERAGE.md` from the unqualified roughly-55-second whole-run claim to the measured current
figure: **103 seconds, with an operator budget of about two minutes**. No other file changes.
The adjacent estimate of roughly four seconds per vendor-honesty case remains compatible: the
unchanged harness has 17 `run_vh` call sites, matching Review 9's execution witness, so that
estimate accounts for roughly 68 of the measured 103 seconds and leaves roughly 35 seconds for
the other consumers, mutations and harness overhead.

A search of all four operative records and both harnesses finds one current cost basis:

- fast instrument: measured **103 seconds**, budget **about two minutes**;
- four-arm gate instrument: measured **8m50s, 8m51s and 9m57s**, budget **10–15 minutes**;
- gate scratch: **roughly 240 MB per subject**.

No unqualified current 55-second, one-minute, 15–20-minute or 15–25-minute publication remains.
The old figures that remain in prior reviews are their dated findings and were not edited. Both
harnesses are unchanged from Review 11, and their executable-line reliance on Review 9's full
measurements still holds. I therefore did not repeat either expensive instrument run.

**HOLD means the A-EXTRACT instrument is ready for the next authorised process step.** It is not
approval of a product repair, sign-off, gate reopening, certification, reaffirmation,
ratification, publication, rename, push, or discharge of the still-unmeasured deep-profile
invocation.

---

## 0. Review identity and bar

| | |
|---|---|
| Branch | `step-3/isolated-signer` |
| Exact frozen subject | `4fe512ee5e42ea991889044b406792495b4c88a9` |
| Subject message | `A-EXTRACT: eleventh-review fast duration corrected. INSTRUMENT ONLY.` |
| Parent | `1de678a73b5740458029d2a3df03357d07ab3706` — eleventh independent review, VERDICT FAIL |
| Review 9 executable subject | `e22b81bfccbb466e46f1dd604c0f8b6ae6c840af` |
| Fast harness | sha256 `9e489ee6f4adab00535d036619738cf1faa97ec8ab070d22cbf29dd3e769bc1a` |
| Gate harness | sha256 `da8c15794f4a597bb0ab766f73e50dac87fd4edea62b22d533e4eef313acc4b1` |
| Frozen test patch | sha256 `3780e63a68ba013a085937c5019a837eb02fc4dda0238c21b2bd2074a908442b` |
| Threat model | D-065: faithful measurement in a non-adversarial environment; no hostile caller-variable finding is offered |
| Repository state at start | clean; HEAD and the supplied exact subject were the same commit object |
| Repository writes before this record | none |

I read the workspace instructions; D-058, D-059, D-065 and D-066; the four operative A-EXTRACT
records; both harnesses; `TESTS.patch`; `INSTRUMENT-REVIEW-11.md`; and the exact
parent-to-subject diff. This review is limited to instrument readiness under those authorities.

## 1. Exact correction and historical preservation

The parent-to-subject diff is one file, one insertion and one deletion:

```diff
-  under test does not need). A whole run is roughly 55 s.
+  under test does not need). The current whole run measured 103 seconds; budget about two minutes.
```

`git diff --name-status 4fe512e^ 4fe512e` names only `COVERAGE.md`. The sentence remains in the
same current “Known weaknesses” bullet and now agrees with the operative cost basis rather than
being disguised as history. No prior review record, historical measurement, product source,
consumer guard, verifier source, fixture, hook, signed pack, proposal, ablation report,
`TESTS.patch`, or harness changes in this correction.

This is the correct treatment under D-058(8)D: repair the maintained current statement while
leaving dated review evidence intact. In particular, Reviews 10 and 11 still state the old
15–20/15–25-minute, one-minute and 55-second figures because those documents record the defects
they found. They are not current operator instructions.

## 2. Current duration audit

I searched `CARD.md`, `COVERAGE.md`, `RESULTS.md`, `GATE-BINDING.md`, `a-extract.sh` and
`a-extract-gate.sh` for timing, cost and budget vocabulary, including the known stale forms and
broader unit-bearing statements.

| Current publication | Fast instrument | Gate instrument | Scratch |
|---|---|---|---|
| `CARD.md` deliverables | 103 seconds / budget ~2 minutes | 8m50s–9m57s / budget 10–15 minutes | gate dependency described |
| `COVERAGE.md` §2b and known weaknesses | 103 seconds / budget about two minutes; VH ~4 s each | 8m50s, 8m51s, 9m57s / budget 10–15 minutes | ~240 MB |
| `GATE-BINDING.md` §6 | 103 seconds / budget about two minutes | 8m50s, 8m51s, 9m57s / budget 10–15 minutes | roughly 240 MB |
| `a-extract-gate.sh` COST comment | 103 seconds / budget about two minutes | 8m50s, 8m51s, 9m57s / budget ten to fifteen minutes | 240 MB |

`RESULTS.md` publishes the current hashes and results but no competing current duration. The
fast harness itself publishes no duration estimate. The only “several minutes” wording is the
explicitly unmeasured incremental cost of the deep profile, not a competing figure for either
instrument.

### 2.1 The roughly-four-seconds-per-VH-case sentence is compatible

The current `a-extract.sh` contains 17 `run_vh` call sites on the healthy dependency path:
the cached baseline plus the section-extent, wrapping, generator, half-caveat and Gate 5
directions. Review 9 independently observed 17 executions in the witness transcript. At the
published approximate four seconds each, those calls account for about 68 seconds. The measured
whole run is 103 seconds, leaving about 35 seconds for TypeScript/eval/verifier consumers,
snapshot construction, mutations, generator work, hashing and cleanup. The component estimate
therefore neither exceeds nor conflicts with the whole-run measurement.

This is only a compatibility check. I did not time each VH invocation independently, and the
word “roughly” remains material.

## 3. Harness identity and exact reliance

Both current harness hashes reproduce the values published in the operative records:

| Harness | Current full-file sha256 | Review 9 fully measured full-file sha256 | Executable comparison |
|---|---|---|---|
| `a-extract.sh` | `9e489ee6…bc1a` | `9e489ee6…bc1a` | full file byte-identical; normalized executable stream `5e146f96…aac` at both |
| `a-extract-gate.sh` | `da8c1579…c4b1` | `9da8d329…827e` | only the COST comment differs; normalized executable stream `d1fc4a06…ebe` at both |

The normalized comparison removes only blank lines and lines whose first nonblank character is
`#`; the complete diff confirms that only the COST comment text changed, as Review 11 records.
Both harnesses pass `bash -n`.

Review 9's full behavioural evidence therefore remains applicable to the unchanged executable
lines:

- fast, two byte-identical runs: 21/52 REQUIRED held, 70/70 CONTROL held, exit 1 at the
  pre-repair subject;
- gate: 7/7 REQUIRED and 11/11 CONTROL held, supervisor `0/5/0/5`, four logs, three named
  consumer banners per log and the G2 causal twin holding.

I did not rerun either expensive harness. This reliance covers executable behaviour and the
recorded pre-repair shape only. It does not independently reacquire the duration measurements,
does not extend them to a different workstation, and does not measure the deep profile.

## 4. Counts, hashes and protected boundaries

The operative current figures agree:

- fast matrix: 136 rows — 52 REQUIRED (21 PASS, 31 FAIL), 70 CONTROL PASS, 14 OBSERVED;
- gate matrix: 7 REQUIRED PASS, 11 CONTROL PASS, 3 OBSERVED;
- gate evidence: supervisor `0/5/0/5`, four logs plus `matrix.tsv`, with G1 and G2-causal
  passing and G2/G3 refusing at the named stages.

Older 49/52, 70/74, 9/10/11-control, three-arm and then-current harness-hash figures remain only
inside explicitly historical correction sections. They are not presented as the current result.

Boundary checks:

- the parent-to-subject diff is empty across `scripts`, `ts`, `contracts`, `verifier`,
  `fixtures`, `.githooks`, the proposal, ablation report, signed pack and `TESTS.patch`;
- `TESTS.patch` remains sha256
  `3780e63a68ba013a085937c5019a837eb02fc4dda0238c21b2bd2074a908442b`;
- `docs/gate-s2-evidence.md` remains sha256
  `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589`;
- the live Gate 5 pin, live §2 table and pre-repair §2 table all remain
  `c9034750e56b8801be7cd31cce33c42caad209013a61ed7082155db33903959c`.

No protected, signed or certified boundary moved, and this review makes no statement that
re-signs, reopens, reaffirms or recertifies one.

## 5. Checks run and output read

- parent-to-subject and worktree `git diff --check`: PASS;
- both A-EXTRACT harnesses `bash -n`: PASS;
- canonical current consumer guards: type strings 6/6, eval codes 41/41, vendor-honesty
  mechanical conditions pass; the guard itself preserves the human-certification boundary;
- `check-secrets.sh`: clean;
- `check-review-scope.sh`: 541/541 subject files assigned; 159 remediation-surface and 79
  preservation-only files reported;
- `check-suite-floors.sh`: 92 Foundry, 527 TypeScript, 221 verifier tests, 7 samples, 78 tamper
  cases and 30 modes, single-sourced from `scripts/test.sh`;
- `check-findings-ledger.sh`: all D-057(1) ruled totals match;
- `check-rename-gate.sh`: repository private; D-016 publication block intact;
- workspace guards: 13 machine-state findings, all baselined, 0 new; PASS by ratchet.

These checks establish scope, preservation and current guard health. They are not substitutes
for the omitted expensive harness runs.

## 6. Limits and disposition

1. No full fast or gate harness was rerun. The executable equivalence and exact reliance are
   stated in §3.
2. I did not independently reopen the temporary timing captures. Review 11 inspected them and
   recorded their basenames, timestamps, content shapes and hashes; this review verifies that
   `F11-1` now agrees with that preserved basis. Those external artifacts are not durable
   repository evidence and may disappear.
3. The ~4-second VH statement was checked for arithmetic and execution-count compatibility, not
   independently benchmarked per invocation.
4. The deep `./scripts/test.sh --gate` profile remains unmeasured. The eventual exact-candidate
   verifier still owns that invocation and its three banners; this HOLD does not discharge it.
5. D-065's non-adversarial-environment bar remains in force, including its reversal condition.
6. This HOLD evaluates instrument readiness only. It spends no implementation attempt and
   exercises none of John's reserved authority.

**HOLD.** `F11-1` is closed at exact subject
`4fe512ee5e42ea991889044b406792495b4c88a9`; current durations, counts and hashes are internally
consistent; both harnesses retain the executable behaviour previously measured; and no protected
boundary moved. Nothing is signed, approved, ratified, certified, reaffirmed, published, renamed,
pushed, repaired in production, or implemented by this review.
