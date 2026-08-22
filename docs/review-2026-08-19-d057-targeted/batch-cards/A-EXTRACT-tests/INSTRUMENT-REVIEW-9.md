# A-EXTRACT — NINTH INDEPENDENT INSTRUMENT REVIEW

# VERDICT: FAIL

The eighth-review causal correction behaves as intended. The new G2 fixture changes only
`ts/src/signer/eip712.ts`, adds one exported-but-unused transposed `ActionPayload` string, leaves
the canonical `ACTION_TYPE`, its runtime typehash path, the proposal, and the independent
evaluator unchanged, and produces no later suite failure. With the named type-string status edge
live, the top-level gate fails; with only that edge bypassed, the same named diagnostic remains
visible and the otherwise-identical gate passes. This discriminates the defective wiring Review 8
demonstrated.

The whole-instrument read found one different in-scope record defect:

- **`F9-1` — the current operative gate records still publish the superseded three-run cost and
  evidence shape.** The harness now runs G1, G2, G2-causal, and G3: four complete fast gates,
  four logs, and the currently stated ~240 MB scratch budget. `CARD.md`, the current correction
  sections, `RESULTS.md`, and the harness say so. But `GATE-BINDING.md`'s current STATUS row still
  says *"Three full `./scripts/test.sh` runs"*; its current isolation/cost section still says
  *"Three full fast-gate runs"* and *"roughly 180 MB"*; and `COVERAGE.md`'s current description
  still says the harness runs the fast gate *"three times"*. These are not labelled historical
  measurements. The full run retained four logs and measured the fourth arm, so the figures are
  demonstrably stale. D-065(3) keeps a published figure that does not describe what was measured
  in scope.

`F9-1` is sufficient for FAIL. The bounded correction is to update only those unqualified current
passages to the four-run/four-log current shape and current scratch budget, while leaving every
explicitly historical three-arm measurement untouched. This review makes no repair.

---

## 0. Review identity and bar

| | |
|---|---|
| Branch | `step-3/isolated-signer` |
| Exact frozen subject | `e22b81bfccbb466e46f1dd604c0f8b6ae6c840af` |
| Subject message | `A-EXTRACT: eighth-review causal gate binding repaired. INSTRUMENT ONLY.` |
| Parent | `b1109136b19aaee6306103bebd664d98b1ce2bd8` — eighth independent review, VERDICT FAIL |
| Fast harness | sha256 `9e489ee6f4adab00535d036619738cf1faa97ec8ab070d22cbf29dd3e769bc1a` |
| Gate harness | sha256 `9da8d3295fecacf68312524080f77db3c35dcf34e308804d657c46bc1a37827e` |
| Frozen test patch | sha256 `3780e63a68ba013a085937c5019a837eb02fc4dda0238c21b2bd2074a908442b` |
| Threat model | D-065: faithful measurement in a non-adversarial environment; no hostile caller-variable finding is offered |
| Repository state at start | clean; HEAD and the supplied exact subject were the same commit object |
| Repository writes before this record | none; every mutation and capture was in an isolated temporary tree outside the repository |

The correction commit changes exactly five files: `CARD.md`, `COVERAGE.md`, `RESULTS.md`,
`GATE-BINDING.md`, and `a-extract-gate.sh`. It changes no production consumer, top-level gate,
existing product test, `TESTS.patch`, proposal, ablation report, signed text, certified material,
or prior review record.

I read the workspace instructions, the authoritative session state, D-058, D-059, D-065 and
D-066, all four operative A-EXTRACT records, both complete harnesses, the complete frozen
`TESTS.patch`, and `INSTRUMENT-REVIEW-8.md`. Measurements below use raw logs, matrices, named
diagnostics, content diffs, hashes, supervisor outcomes, and completion tokens. Exit status alone
is never treated as a per-case verdict.

## 1. `F8-1` — causal gate binding now discriminates

### 1.1 The G2 source fixture is isolated from runtime behaviour

I independently rebuilt the exact mutation from the frozen harness against a fresh archive of
`bb664c626d592d86391f644bf014e76f2bbf7db4` and compared the complete trees.

- The only changed file is `ts/src/signer/eip712.ts`.
- The complete diff is one new exported constant,
  `A_EXTRACT_G2_DECOY_ACTION_TYPE`, immediately before `ACTION_TYPE`.
- The decoy contains the transposed tail
  `bytes32 policyHash,bytes32 mandateHash,uint64 deadline` exactly once.
- The decoy symbol occurs exactly once — its definition — so no runtime code imports or reads it.
- The canonical `ACTION_TYPE` definition remains byte-identical and occurs exactly once.
- `ACTION_TYPEHASH = keccak256(stringToBytes(ACTION_TYPE))`, `hashAction`, the pinned
  `ActionPayload` golden hash, and the `ActionPayload: ACTION_TYPEHASH` binding are byte-identical.
- The proposal is byte-identical, sha256 `322cd96f…4124`, and the independent evaluator's
  `ts/src/evaluate/hashes.ts` is byte-identical, sha256 `cd012a63…850`.

The complete G2 and G2-causal logs independently confirm the behavioural half: Foundry is
92 passed / 0 failed / 0 skipped; TypeScript is 527 passed / 0 failed / 0 skipped; the ablation
artifact regenerates byte-for-byte; and the independent verifier reports a clean 209-test subject
suite with all sample and tamper floors met. The only failure in G2 is the intended named
type-string stage.

### 1.2 The causal twin changes one status edge and reverses the top-level outcome

An independent tree comparison between G2 and G2-causal found exactly one changed file,
`scripts/test.sh`, with exactly one changed line:

```
-./scripts/check-type-strings.sh || fail=1
+./scripts/check-type-strings.sh || true  # A-EXTRACT G2 causal bypass
```

The transposed source fixture is byte-identical between the two arms. The four complete raw logs
and matrix measured:

| Arm | Supervisor | TS diagnostic | EC | VH | Pass token | Fail token | Completion refusal |
|---|---:|---|---|---|---:|---:|---:|
| G1 | 0 | success | success | success | 1 | 0 | 0 |
| G2 | 5 | `DRIFT in ActionPayload` | success | success | 0 | 1 | 1 |
| G2-causal | 0 | `DRIFT in ActionPayload` | success | success | 1 | 0 | 0 |
| G3 | 5 | success | success | named ablation-report failure | 0 | 1 | 1 |

Every arm contains exactly one TS, EC, and VH banner. No arm contains a fatal Git diagnostic or
`ERR_MODULE_NOT_FOUND`; no unintended suite failure appears. The matrix is 7 REQUIRED PASS,
11 CONTROL PASS, and 3 OBSERVED, with no failing row. This is the expected `0/5/0/5` outcome and
proves that G2's refusal depends on the named status edge.

This directly discriminates Review 8's defective wiring. The old proposal mutation also failed
the later `TestPublishedTypeStrings` consumer, so bypassing the named edge left the gate red. The
current unused source duplicate leaves that verifier clean, and the causal arm goes green.

`G2-named` is compatible with both sides of the fixed contract without weakening to silence or
unrelated output: it requires `ActionPayload`, forbids the success line, and requires either the
current pre-repair `DRIFT` class or duplicate/source-count vocabulary suitable for the eventual
source-uniqueness refusal. An empty message, an unrelated failure, an `ActionPayload` mention with
no reason class, or a success line cannot satisfy it. `G2-causal` repeats that named predicate and
also requires supervisor 0, both later consumers green, `GATE PASSED`, and no failure or
completion-refusal token.

## 2. Evidence destinations and prior fail-closed repairs

### 2.1 Gate evidence output covers all five current names

The complete valid-output run created five regular files: `g1.log`, `g2.log`, `g2-causal.log`,
`g3.log`, and `matrix.tsv`. Their final copies/writes are individually checked in the harness,
and every file was present and readable after exit 0.

The invalid parent `/dev/null/aextract-review9-output` returned 2 before any REQUIRED or CONTROL
row and printed one named preflight diagnosis. Each of the five output names was then driven
independently as a directory under an otherwise valid destination. Every case returned 2, emitted
zero scored rows, and named that output as not a writable regular file. The preflight therefore
covers the causal log as well as the original three logs and matrix.

### 2.2 All six dependency states refuse before scoring

Each state was driven separately with the other two dependency trees populated:

| Dependency | State | Process | REQUIRED rows | CONTROL rows |
|---|---|---:|---:|---:|
| `contracts/lib/forge-std` | absent | 2 | 0 | 0 |
| `contracts/lib/forge-std` | empty | 2 | 0 | 0 |
| `contracts/lib/openzeppelin-contracts` | absent | 2 | 0 | 0 |
| `contracts/lib/openzeppelin-contracts` | empty | 2 | 0 | 0 |
| `ts/node_modules` | absent | 2 | 0 | 0 |
| `ts/node_modules` | empty | 2 | 0 | 0 |

Every output carries the applicable named dependency diagnosis. D-066(4)'s setup/refusal
boundary holds.

### 2.3 Optional fast outputs and both `Z-clean` predicates remain fail-closed

Four fast-output states were driven independently: absent evidence directory, evidence output
colliding with a directory, absent matrix parent, and matrix target colliding with a directory.
Each returned 2 with zero REQUIRED and zero CONTROL rows and a named preflight diagnosis. Both
complete valid runs wrote the consumer transcript and matrix.

The exact `Z-clean` predicate shared by the two harnesses was driven over all three result shapes:

| State | Git rc | output/diagnostic lines | Predicate |
|---|---:|---:|:---:|
| clean | 0 | 0 | PASS |
| ordinary dirty path | 0 | 1 | FAIL |
| status error / no repository | 128 | 1 | FAIL |

The two complete fast runs and complete gate run then recorded `Z-clean CONTROL PASS` with rc 0
and zero boundary lines.

## 3. Complete fast-harness measurements

Two complete runs against the exact pre-repair object independently produced:

```
52 REQUIRED — 21 PASS, 31 FAIL
70 CONTROL  — 70 PASS, 0 FAIL
14 OBSERVED
136 total rows
process exit 1; empty stderr
```

The complete stdout is byte-identical between runs, sha256 `36fdeda0…524`; the complete matrices
are byte-identical, sha256 `af11a950…34a`. The same 31 named REQUIRED rows fail in both runs.
`P3-provenance` matches all 498 blob paths, and all execution witnesses hold: TS 26 executions,
EC 14, VH 17, verifier 8, every one carrying the exact subject blob. `Z-gate5` and `Z-signed`
hold in both runs.

## 4. Subject, scope, deletion audit, pinning, and protected material

- The exact correction scope is five files and only those five. The production/protected delta
  from parent to subject is empty across `scripts`, `ts`, `contracts`, `verifier`, `fixtures`,
  `.githooks`, the proposal, ablation report, signed pack, and `TESTS.patch`.
- The correction deletes 68 lines across the five files. Every deletion maps to the documented
  replacement of the old proposal-based G2, its three-arm descriptions/counts, its old hash and
  measurement labels, or wording made obsolete by the causal arm. No executable preflight,
  integrity control, assertion, protected-boundary statement, or case is silently removed.
- The gate harness still has ten Git invocations: seven command-pinned with
  `--no-replace-objects`; the other three are version reporting, worktree hashing, and status.
  The operative records state that measured seven-of-ten shape rather than claiming every command
  is pinned.
- `TESTS.patch` is unchanged, and `git apply --check` succeeds against a fresh archive of the
  pre-repair subject. It was not applied by this review.
- `docs/gate-s2-evidence.md` remains sha256 `833671b8…f589`.
- The live Gate 5 pin, the live §2 table digest, and the pre-repair §2 digest all remain
  `c9034750e56b8801be7cd31cce33c42caad209013a61ed7082155db33903959c`.

## 5. `F9-1` — current three-run claims are stale

The current executable and its newest records agree on four full fast-gate arms:

- `a-extract-gate.sh` says four runs and ~240 MB, executes G1, G2, G2-causal, and G3, and writes
  four logs plus the matrix;
- `CARD.md`'s deliverables table says four runs;
- `RESULTS.md` names the `0/5/0/5` outcomes and all five evidence files;
- the complete run in this review actually produced that shape.

Three unqualified current passages disagree:

1. `GATE-BINDING.md` STATUS says *"Three full `./scripts/test.sh` runs"*.
2. `GATE-BINDING.md` §6 says *"Three full fast-gate runs"* and *"roughly 180 MB"*.
3. `COVERAGE.md` §5 says the separate harness runs the top-level fast gate *"three times"*.

These are not in a superseded or historical subsection. They describe current status, current
cost, and current harness behaviour. The fourth arm is not optional bookkeeping: it is the causal
control that repairs `F8-1`. Omitting it from the current evidence/cost description understates
what must run and which log must exist, while adjacent current sections say the opposite. This is
the published-figure and requirement-consistency class D-065(3) keeps within the review bar.

The repair surface is bounded to those current prose passages. Historical three-arm results —
including the seventh-review and older measurements — remain historical evidence and must not be
rewritten.

## 6. Repository and workspace checks

After all measurements and isolated probes:

- both harnesses pass `bash -n`;
- the correction commit passes `git diff --check`;
- `check-secrets.sh`: clean;
- `check-review-scope.sh`: all 538 then-tracked files assigned; 156 remediation-surface and
  79 preservation-only files reported;
- `check-suite-floors.sh`: 92 Foundry, 527 TypeScript, 221 verifier tests, 7 samples,
  78 tamper cases, and 30 modes, read from the single source in `scripts/test.sh`;
- `check-rename-gate.sh`: private repository, D-016 publication block intact;
- workspace guards: 13 machine-state findings, all 13 baselined, 0 new; PASS by ratchet.

These checks establish scope and preservation. They do not make the stale current evidence
description true.

## 7. Limits and disposition

1. The deep `./scripts/test.sh --gate` profile remains unmeasured, exactly as the current records
   disclose. The post-repair exact-SHA verifier still owns that invocation and its three banners;
   a deep run cannot correct `F9-1`.
2. This review ran on the documented macOS/git/bash/Python/Node/Forge environment only.
3. Dependency tests cover absent and empty trees, not every malformed filesystem object.
4. Late evidence I/O failure is checked statically and the normal final writes completed; disk
   exhaustion or a permission change occurring after preflight was not induced.
5. D-065's hostile caller-variable class remains out of scope. No such variable is a finding.
6. Isolated mutations and raw captures are not committed. This file is the only repository write.
7. This verdict evaluates instrument readiness only. It does not approve or assess a production
   repair, sign or reopen a gate, certify a claim, or discharge D-059(7)'s deep-profile portion.

**FAIL.** The causal G2 repair holds, but three current operative passages still describe the
superseded three-arm harness and old scratch budget. A FAIL consumes no implementation attempt.
Nothing is signed, ratified, certified, reaffirmed, published, renamed, pushed, or implemented by
this review.
