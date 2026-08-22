# A-EXTRACT — TENTH INDEPENDENT INSTRUMENT REVIEW

# VERDICT: FAIL

The ninth-review correction closes `F9-1`'s run/log/scratch-shape defect exactly. The
parent-to-subject diff changes only `COVERAGE.md` and `GATE-BINDING.md`, and only the three
unqualified live passages Review 9 cited. They now describe four full fast-gate runs, four logs
plus the matrix, and roughly 240 MB of scratch. Explicitly historical three-arm measurements are
byte-identical to the parent.

The required full-record search found one remaining current-record defect:

- **`F10-1` — the live duration budget has two incompatible publications.** The executable
  harness and `COVERAGE.md` say four gate runs take **roughly fifteen to twenty minutes**;
  `CARD.md` and `GATE-BINDING.md` say **roughly/budget fifteen to twenty-five minutes**. These are
  all unqualified descriptions of the current harness, not dated three-arm results. The same
  current records also describe the fast harness as **about one minute** in the gate harness and
  **about two minutes** in `CARD.md` / `GATE-BINDING.md`. The correction therefore fixed the
  arm/log/scratch counts but did not leave one internally consistent current cost statement.
  Resolve the live duration figures from preserved timing evidence (or remeasure if that evidence
  is unavailable), then make the current records agree without rewriting any historical run.

`F10-1` is sufficient for FAIL under D-065(3)'s published-figure bar. It is a record defect only:
the executable bytes and Review 9's measured behavior remain intact. This review makes no repair.

---

## 0. Review identity and bar

| | |
|---|---|
| Branch | `step-3/isolated-signer` |
| Exact frozen subject | `d0164cd63da9c6f438058d8c9581613431c283fb` |
| Subject message | `A-EXTRACT: ninth-review evidence-shape figures corrected. INSTRUMENT ONLY.` |
| Parent | `18e2a5819fbcb41878e072132a6e89dce239b529` — ninth independent review, VERDICT FAIL |
| Review 9 executable subject | `e22b81bfccbb466e46f1dd604c0f8b6ae6c840af` |
| Fast harness | sha256 `9e489ee6f4adab00535d036619738cf1faa97ec8ab070d22cbf29dd3e769bc1a` |
| Gate harness | sha256 `9da8d3295fecacf68312524080f77db3c35dcf34e308804d657c46bc1a37827e` |
| Frozen test patch | sha256 `3780e63a68ba013a085937c5019a837eb02fc4dda0238c21b2bd2074a908442b` |
| Threat model | D-065: faithful measurement in a non-adversarial environment; no hostile caller-variable finding is offered |
| Repository state at start | clean; HEAD and the supplied exact subject were the same commit object |
| Repository writes before this record | none |

I read the workspace instructions; D-058, D-059, D-065 and D-066; all four operative A-EXTRACT
records; both harnesses; `TESTS.patch`; `INSTRUMENT-REVIEW-9.md`; and the exact
parent-to-subject diff. This is an instrument-readiness review only. It does not approve a
product repair, sign or reopen a gate, certify or alter a claim, ratify a decision, publish,
rename, or push.

## 1. `F9-1` is closed on the exact correction

The complete parent-to-subject diff is three replacements in two files:

1. `COVERAGE.md` §5 changes the current fast-gate invocation count from three to four.
2. `GATE-BINDING.md` STATUS replaces the three-arm summary with G1, G2, G2-causal and G3.
3. `GATE-BINDING.md` §6 changes three runs / roughly 180 MB to four runs / roughly 240 MB and
   widens its current time budget.

No other path changes. In particular, every dated or revision-labelled three-arm account remains
byte-identical: the seventh-, sixth-, fifth- and earlier review measurements were not rewritten.
A full-text search of `CARD.md`, `COVERAGE.md`, `RESULTS.md` and `GATE-BINDING.md` found no
remaining unqualified current publication of three gate arms, three gate logs, or roughly 180 MB.
The surviving three-arm references occur inside explicit historical sections and retain their
then-current hashes, `0/5/5` outcomes, three-log shape and 10-control tally.

The current arm/log/scratch shape is internally consistent:

- the executable contains four `./scripts/test.sh` invocations: G1, G2, G2-causal and G3;
- it preflights and writes `g1.log`, `g2.log`, `g2-causal.log`, `g3.log` and `matrix.tsv`;
- the current records describe four logs plus the matrix and roughly 240 MB;
- the current gate record agrees on 7 REQUIRED, 11 CONTROL, 3 OBSERVED, exit 0 and supervisor
  outcomes `0/5/0/5`;
- the current fast record agrees on 52 REQUIRED (21 held, 31 failed), 70 CONTROL, 14 OBSERVED and
  136 total rows at the pre-repair subject.

## 2. Exact-executable reliance and its limit

Both current harnesses are byte-identical to Review 9's frozen executable subject
`e22b81bfccbb466e46f1dd604c0f8b6ae6c840af`. Their sha256 values above match both commits, and
`bash -n` passes for both.

Accordingly, I did **not** rerun either expensive harness. I rely on Review 9's independent full
measurements as exact executable evidence:

- gate: 7/7 REQUIRED, 11/11 CONTROL, 3 OBSERVED, exit 0; `0/5/0/5`; four retained logs with one
  TS, EC and VH banner each; the causal G2 twin held;
- fast: two byte-identical runs at 52 REQUIRED / 70 CONTROL / 14 OBSERVED, with 21 REQUIRED held
  and 31 failed.

That reliance establishes behavior, counts and tokens for the unchanged executable. It does not
choose between the conflicting current time estimates in `F10-1`. A new full run is not needed to
establish that two live publications disagree, and one run under one machine load would not by
itself establish a generally valid upper budget. The record correction must instead cite the
preserved timing basis or explicitly remeasure the budget it elects to publish.

## 3. `F10-1` — current cost records still disagree

The conflicting live passages are:

| Current source | Published duration |
|---|---|
| `a-extract-gate.sh` COST header | roughly 15–20 minutes for four full fast-gate runs |
| `COVERAGE.md` §2b | roughly 15–20 minutes for four full fast-gate runs |
| `CARD.md` DELIVERABLES | roughly 15–25 minutes for the gate harness |
| `GATE-BINDING.md` §6 | budget 15–25 minutes for four full fast-gate runs |

The fast-harness estimate has the same smaller inconsistency: the gate harness says
`a-extract.sh` runs in about one minute, while `CARD.md` and `GATE-BINDING.md` say about two.
These are current operator-facing cost statements. None is introduced as an older checkpoint or
as a different environment's measurement.

The correction should not guess which estimate is true, and this review does not choose one. The
actionable boundary is only the current duration publications; arm count, log count, scratch
budget, executable behavior, and every historical three-arm measurement already hold.

## 4. Scope, protected material and pinning

- The parent-to-subject delta is exactly `COVERAGE.md` and `GATE-BINDING.md`: 3 insertions and
  3 deletions. The production/protected diff is empty across `scripts`, `ts`, `contracts`,
  `verifier`, `fixtures`, `.githooks`, the proposal, ablation report, signed pack and
  `TESTS.patch`.
- `TESTS.patch` remains sha256
  `3780e63a68ba013a085937c5019a837eb02fc4dda0238c21b2bd2074a908442b`.
- `docs/gate-s2-evidence.md` remains sha256
  `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589`.
- The live Gate 5 pin, live §2 table and pre-repair §2 table all remain
  `c9034750e56b8801be7cd31cce33c42caad209013a61ed7082155db33903959c`.
- No prior review record changes. `INSTRUMENT-REVIEW-9.md` remains the independent evidence on
  which the unchanged executable measurements rely.

## 5. Focused repository and workspace checks

- both harnesses: `bash -n` PASS;
- parent-to-subject and worktree `git diff --check`: PASS;
- `check-secrets.sh`: clean;
- `check-review-scope.sh`: 539/539 tracked files assigned; 157 remediation-surface and
  79 preservation-only files reported;
- `check-suite-floors.sh`: 92 Foundry, 527 TypeScript, 221 verifier tests, 7 samples,
  78 tamper cases and 30 modes, single-sourced from `scripts/test.sh`;
- `check-findings-ledger.sh`: all ruled totals match;
- `check-rename-gate.sh`: private repository; D-016 publication block intact;
- workspace guards: 13 machine-state findings, all baselined, 0 new; PASS by ratchet.

These checks support scope and preservation. They do not resolve the conflicting live duration
figures.

## 6. Limits and disposition

1. No full fast or gate run was repeated because both executables are byte-identical to Review
   9's fully measured subject. The exact evidence relied upon is stated in §2.
2. The deep `./scripts/test.sh --gate` profile remains unmeasured, as the operative records
   disclose. The eventual exact-candidate verifier still owns that invocation and its three
   banners.
3. The duration inconsistency is documentary. It does not reverse any executable verdict, but
   it prevents a HOLD because the current operator cost is not stated consistently.
4. This verdict evaluates instrument readiness only. It does not approve implementation,
   discharge the deep-profile portion of D-059(7), or exercise any authority reserved to John.
