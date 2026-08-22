# A-FLOORS — measured pre-repair results

## Verdict

**HOLD for test-contract readiness, pending fresh independent review.** The baseline product is
supposed to fail the required repair assertions. Controls establish the instrument remains live.
No production repair has been made or approved.

## 1. Focused baseline

Against exact baseline `1a133301533e9d959dbafbbcc7ffe05e7eb78df3`:

```text
REQUIRED 10/53
CONTROL 28/28
PRE-REPAIR DEFECTS OBSERVED
exit=1
```

The ten required baseline satisfactions are the already-current verifier quartet
`221/7/78/30` and all six missing-definition refusals. Every intended open defect remains
observable:

- stale Foundry and TypeScript canonical values (`92`, `527` rather than `103`, `550`);
- empty, malformed and non-numeric definitions are not distinctly refused for all six names;
- duplicate-before, duplicate-after and conditional duplicates are not refused;
- both duplicate orders prove reader first-wins against Bash last-wins;
- wrapped/unwrapped live §3 publication, current D-010 session publication and current D-010
  coverage publication are not rejected; and
- `scripts/test.sh` contains zero common-path invocations of the targeted checker.

All 28 controls pass. They include frozen B/C hashes, unchanged reader execution, exact valid
six-source acceptance, prefix discrimination, twelve direct-order witnesses, six conditional
Bash witnesses, wrap equivalence, dated numbers inside enumerated logical paragraphs,
constant-name mentions, unrelated numbers and a positive wiring witness against frozen candidate
text.

Final raw focused log sha256:
`8a34c604d0a9ce814a55715a1f1775fcb9f01eff76a90b7ad4d33174c7d57478`.
Complete path-free matrix sha256:
`a704290d198f14ab85db1a66149b5dd03ff3d7096ad04646f05f5c6980247ca5`.

## 2. Serial top-level gate baseline

No final case overlapped another gate. Each case used an independent exact-commit clone.

| Case | Result | Seconds | Exact baseline observation |
|---|---|---:|---|
| G0 unchanged fast | CONTROL PASS | 152.670 | 103 Foundry / 550 TypeScript / verifier 221, samples 7, tamper 78/30; `GATE PASSED` |
| G1 wrong current paragraph, fast | REQUIRED FAIL | 150.318 | identical measured success and `GATE PASSED`; current gate does not invoke the reader guard |
| G2 unchanged deep | CONTROL PASS | 286.512 | same counts; 50 corpus fixtures and committed views file-by-file; deep profile; `GATE PASSED` |
| G3 wrong current paragraph, deep | REQUIRED FAIL | 289.146 | identical deep success including corpus/views and `GATE PASSED`; deep path has the same wiring hole |
| G4 raised 103/550, unchanged suites | CONTROL PASS | 153.205 | Foundry 103 floor 103; TypeScript 550 floor 550; verifier green; `GATE PASSED` |
| G5 raised floors + delete B-EVENTS file | REQUIRED PASS | 145.689 | Foundry 92 floor 103 breach; TypeScript/verifier green; `GATE FAILED`; no completion |
| G6 raised floors + delete C-SNAPSHOT file | REQUIRED PASS | 143.293 | Foundry green; TypeScript 527 floor 550 breach; verifier green; `GATE FAILED`; no completion |

Final score:

```text
REQUIRED 2/4
CONTROL 3/3
PRE-REPAIR GATE DEFECTS OBSERVED
exit=1
```

The two required failures are the intended fast/deep reader-wiring holes. The two required passes
prove the planned floors catch exactly the B/C deletion deltas. Full raw-log hashes:

| Case | sha256 |
|---|---|
| G0 | `27fa0430af50e662f2fee339057cd824703d8cc964e8bdc9b5d1447977a07ee0` |
| G1 | `691748637047827f629fb65f131777774131f4958a54af77bbf87382ac37260f` |
| G2 | `ebb9d73577f6e4888ac8b2579883c7aa46bf9cc06e1803748c37a6b495a81275` |
| G3 | `9c0321dcccdd7477b0ba487f8fbdeb0c541d121f09978b0a588b874639265d20` |
| G4 | `79b14aa7537ec233ae2b60f61fcb1e390ff19ae7a589042cdffd82a2f2cb4edf` |
| G5 | `42e061acabb661a3d34d94abaf8227f455ad7ad6c0d2b574e886473d991f5fdc` |
| G6 | `954940da794f0afe6b4d014f34aaf5861f88325f2563cc35f08565791e3577c6` |

Harness raw log sha256:
`c4a41ddc58b73c7c23932556a37c7c955968298553fcbbd94314c550c01a6cb2`.
Path-free gate matrix sha256:
`0b4d9c127e7230c7266960fe073f92f9551da9a68005cb936850993d803d1c58`.

## 3. Excluded setup/calibration runs

- One preliminary deep run overlapped another gate and was cancelled immediately. Its only
  durable result is `gate: cancelled; the body was stopped with it.` It is neither gate evidence
  nor timing evidence.
- One preliminary fast run overlapped that setup interval. Although it returned green, it is not
  used as final evidence or timing.
- The first serial-wrapper launch stopped before a case because the temporary harness lacked its
  executable bit. No gate ran; this is setup failure, not a verdict.
- The next calibration completed a green unchanged fast gate but the wrapper expected verifier
  `verdict PASS` while the actual exact word is `verdict clean`. That control failure invalidated
  the wrapper run; the active next case was cancelled. The oracle was corrected and all seven
  final cases rerun from the beginning.

These exclusions implement D-066(4): incomplete dependency/precondition states never contribute
a REQUIRED or CONTROL verdict.

## 4. Repository and workspace guards

With only this new evidence directory present:

- secret guard, worktree and staged modes: `clean`;
- review scope: pass before staging at 588/588 (R1 389 / R2 47 / R3 152), then pass with
  this directory staged at 602/602 (R1 403 / R2 47 / R3 152);
- findings ledger: pass, 23 IDs and D-057(1) totals unchanged;
- suite-floor reader: exit 0 and exact baseline `92/527/221/7/78/30`;
- vendor-honesty mechanical guard: pass, while D-008(1)/(3) remain John's authority exactly as
  printed; and
- workspace guards: pass with 13 pre-existing machine-state findings baselined and zero new.

A green workspace guard is ratcheted evidence: it permits the 13 pre-existing Sentinel
machine-state findings and does not claim those findings are absent.

## 5. Limits

The baseline gate logs contain a machine-specific repository path in the pre-existing rename
stage. Full logs therefore remain outside the repository and are bound by sha256; tracked logs
preserve the exact scored lines only. This evidence does not establish a repaired pass, generic
shell parsing, generic Markdown consistency, correctness of historical records, a signed/public
claim, or any fact outside the card boundary.
