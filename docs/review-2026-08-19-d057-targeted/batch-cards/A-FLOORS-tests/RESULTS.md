# A-FLOORS — corrected measured pre-repair results

## Verdict

**HOLD for corrected test-contract readiness, pending fresh independent Review 2.** No production
repair, post-repair pass or approval exists.

## 1. Review-1 evidence retained as historical measurement

The original author subject measured focused REQUIRED 10/53, CONTROL 28/28. Its harness and
matrix were `4782ff02…5200f` and `a704290d…47ca5`; raw output was `8a34c604…57478`.
`focused-matrix-review1.tsv` and `logs/focused-baseline-review1-summary.log` preserve those bytes.
Review 1 independently reproduced all 81 rows and returned FAIL because zero and standalone
indented assignments were absent. `INSTRUMENT-REVIEW-1.md` is unchanged.

## 2. Corrected baseline

Against exact clean subject `e3b8a76cff7a002b3211bb8f8a75f2d14b86a37e` with the corrected
harness executed externally:

```text
REQUIRED 10/71
CONTROL 65/65
PRE-REPAIR DEFECTS OBSERVED
exit=1
```

The ten required passes remain the six existing missing-definition refusals and current verifier
quartet. Newly added outcomes:

- six `Z-*` zero refusals: all fail at the current reader;
- six `ONE-*` positive-one controls: all pass;
- twelve standalone-indented refusals (`IA/IB`): all fail;
- twelve Bash trace/order witnesses (`IAW/IBW`): all pass;
- eighteen inert comment/quote/heredoc controls: all pass; and
- `P-reader-restore`: passes exact reader hash plus restored exit/output identity.

All 136 case names are unique. Raw output sha256:
`d90500cd684d245bdc79324f3562a92cabbc935b79595e65976878322ba20931`.
Matrix sha256: `f0ab8dcd63efe98bbacfc353dd0e849b6b9f91bbdccd6288fa90c80a524b63a0`.

## 3. Causal zero sibling

The digits-only zero-accepting sibling returns:

```text
REQUIRED 65/71
CONTROL 65/65
exit=1
```

Comparison against the preserved Review-1 matrix proves 81/81 old rows pass, with zero missing
names and zero old non-passes. The complete corrected matrix has 136/136 unique names. Its exact
failure set is only:

```text
Z-FOUNDRY_MIN_TESTS
Z-TS_MIN_TESTS
Z-VERIFIER_MIN_TESTS
Z-VERIFIER_MIN_SAMPLES
Z-VERIFIER_MIN_TAMPER
Z-VERIFIER_MIN_TAMPER_MODES
```

Raw sha256: `2085505bdcd6db3004b5e82cb424da45cc658bcc47caf78ce3b7a522d6275e2c`.
Matrix sha256: `2094fba903c6ad9ef7f8be4cdba1bc5dfc0bc841b7f34fc70070b6787c6bf46c`.

## 4. Exact-positive satisfying control

The sibling differing only in `[1-9][0-9]*` returns:

```text
REQUIRED 71/71
CONTROL 65/65
A_FLOORS_FOCUSED_COMPLETE
exit=0
```

Raw sha256: `34980d90b09909c698abf7e8f2c88d02e81755325d03ba61325756fef2de0d11`.
Matrix sha256: `3db1d06abbcec760aa4ce80f68aacaed7ed17df3fc998adf3c74707b86695bdb`.

## 5. Historical serial gate reliance

The gate harness is byte-unchanged, and F1/F2 add no gate-path semantic. No expensive gate was
rerun. Historical final evidence remains:

| Case | Historical result | Seconds |
|---|---|---:|
| G0 unchanged fast | CONTROL PASS | 152.670 |
| G1 wrong paragraph fast | REQUIRED FAIL, expected baseline hole | 150.318 |
| G2 unchanged isolated deep | CONTROL PASS | 286.512 |
| G3 wrong paragraph deep | REQUIRED FAIL, expected baseline hole | 289.146 |
| G4 planned 103/550 unchanged | CONTROL PASS | 153.205 |
| G5 delete B 11-test file | REQUIRED PASS, exact 92 < 103 | 145.689 |
| G6 delete C 23-test file | REQUIRED PASS, exact 527 < 550 | 143.293 |

Historical score is REQUIRED 2/4, CONTROL 3/3. Gate harness/matrix hashes are
`fb389fdd…fc39` / `0b4d9c12…c58`; the seven full raw hashes remain in unchanged tracked
`logs/gate-summary.log`. This correction does not refresh those timings or raw logs.

## 6. Measurement hygiene and limits

The corrected harness ran normal, zero-sibling and exact-positive variants in disposable clean
clones. A provisional sibling run exposed that its heredoc detector mistook the comment
`# <<< GATE BOOTSTRAP <<<` for a heredoc and failed the live-reader control; it was not counted.
After excluding full-line comments and adding `P-reader-restore`, all three final runs have every
control green. Setup/calibration failures are not verdicts under D-066(4).

Full raw focused logs remain external and are hash-bound. Prior gate raw logs remain external due
the pre-existing machine path in the rename stage. This establishes instrument discrimination,
not implementation, generic parsing/Markdown completeness, historical truth, certification,
signing, publication or D-055 closure.

## 7. Guards

With the correction confined to this directory:

- secret guard, worktree and staged modes: `clean`;
- review scope: worktree pass at 603/603 (R1 404 / R2 47 / R3 152), then staged pass at
  609/609 tracked files (R1 410 / R2 47 / R3 152);
- findings ledger: pass with 23 IDs and D-057(1) totals unchanged;
- live suite-floor reader: exit 0 at `92/527/221/7/78/30`;
- vendor-honesty mechanical guard: pass, with D-008 authority left exactly as printed; and
- workspace guard: pass with 13 pre-existing machine-state findings baselined and zero new.

A workspace pass remains ratcheted: the 13 pre-existing findings are accepted debt, not absent.
