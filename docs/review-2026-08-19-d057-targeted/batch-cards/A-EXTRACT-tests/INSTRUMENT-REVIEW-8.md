# A-EXTRACT — EIGHTH INDEPENDENT INSTRUMENT REVIEW

# VERDICT: FAIL

The two seventh-review corrections hold in the states they name. A normal invalid
`A_EXTRACT_GATE_LOGDIR` now refuses at exit 2 before any REQUIRED or CONTROL row and without the
completion token; a valid newly created destination receives all three gate logs and the matrix,
with every final write checked. The current fast result is 21 of 52 REQUIRED, so the live derived
failure count is 31 rather than 28; the old 28-of-49 figures remain explicitly historical.

The complete gate run exposed a different in-scope instrument defect:

- **`F8-1` — G2 cannot establish that the gate carries the first consumer's failure.** Its
  `ActionPayload` proposal mutation makes the named type-string guard fail, but it also makes the
  later verifier suite fail independently in
  `TestPublishedTypeStrings.test_recovered_strings_match_the_published_ones`. The G2 predicates
  inspect the named guard body, the two later shell-consumer bodies, and the global `GATE FAILED`
  token; none excludes or distinguishes that second failure. In an isolated causal control I
  changed the same `scripts/test.sh` invocation from `check-type-strings.sh || fail=1` to
  `check-type-strings.sh || true`, leaving the G2 proposal mutation intact. The guard still
  printed its named `DRIFT in ActionPayload`, the eval-code and vendor-honesty consumers both
  stayed green, the later verifier test failed, and the top-level gate still printed
  `GATE FAILED` at supervisor rc 5. The current `G2-named`, `G2-gate`, `G2-unmasked`, and
  `G2-scope` predicates would all pass in that defective-wiring state. G2 therefore cannot
  observe whether the first consumer's failure was accumulated or later masked, while
  `GATE-BINDING.md` says it establishes exactly that. This is a non-discriminating REQUIRED
  probe under D-065(3), not a hostile-environment input.

`F8-1` is sufficient for FAIL. The correction is bounded: use a G2 fixture whose top-level
failure depends only on the named type-string stage, and add a causal control in which ignoring
or clearing that stage's failure makes the top-level gate pass. The instrument must also assert
that no other gate stage supplies an independent failure in that arm. This review makes no such
repair.

---

## 0. Review identity and bar

| | |
|---|---|
| Branch | `step-3/isolated-signer` |
| Exact subject | `c69c88c70c7381dd66cecd9f01398275643f5b86` |
| Subject commit message | `A-EXTRACT: seventh-review instrument defects closed. INSTRUMENT ONLY.` |
| Parent | `7fa7ecc7b55570584f369204e5c3ee8648219389` — seventh independent review, VERDICT FAIL |
| Fast harness | sha256 `9e489ee6f4adab00535d036619738cf1faa97ec8ab070d22cbf29dd3e769bc1a` |
| Gate harness | sha256 `2d00ab31fb61956f2daf4128647203a971f220b7104cdff595987cb484153e61` |
| Threat model | D-065: faithful measurement in a non-adversarial environment; no newly named hostile caller variable is offered as a finding |
| Governing repair argument | D-066(4): an incomplete dependency precondition refuses before REQUIRED/CONTROL scoring and is never scored as a gate defect |
| Repository state at start | clean; HEAD and the supplied frozen subject were the same exact object |
| Repository writes before this record | none; every mutation and capture was in an isolated temporary tree outside the repository |

The correction commit changes exactly five files: the four operative A-EXTRACT records
(`CARD.md`, `COVERAGE.md`, `RESULTS.md`, `GATE-BINDING.md`) and `a-extract-gate.sh`. No review
document, fast harness, `TESTS.patch`, production consumer, top-level gate, signed text, or
certified material changes in that commit.

I read the workspace instructions, `docs/session-state.md`, `docs/repair-protocol.md`, D-058,
D-059, D-065 and D-066 in `docs/decisions.md`, the complete current `CARD.md`, `COVERAGE.md`,
`RESULTS.md`, `GATE-BINDING.md`, both harnesses, and `INSTRUMENT-REVIEW-7.md`. I inspected the
complete correction diff and the current harness control flow. Measurements below use the
emitted matrices, raw consumer and gate logs, named diagnostics, execution witnesses, gate
tokens, and supervisor outcomes; an exit status alone is not treated as a per-case verdict.

## 1. Seventh-review corrections

### 1.1 `F7-1` — gate evidence output now refuses before scoring

With `A_EXTRACT_GATE_LOGDIR` set to a child of the regular file `/dev/null`, the gate harness
returned:

```
process                         2
REQUIRED rows                  0
CONTROL rows                   0
completion tokens              0
PREFLIGHT FAILED diagnostics   1
```

The diagnosis names the destination creation failure. Only the two OBSERVED identity/tool lines
precede it. Validation is before `P3-provenance`, the first scored row.

The paired full run supplied a valid path that did not yet exist. The harness created it and
preserved four regular files: `g1.log`, `g2.log`, `g3.log`, and `matrix.tsv`. Its matrix contains
7 REQUIRED PASS, 10 CONTROL PASS, 3 OBSERVED, and no failing row; the process returned 0 with no
stderr. Each raw log contains exactly one TS, EC, and VH banner. Token counts were:

| Arm | Supervisor | `GATE PASSED` | `GATE FAILED` | completion refusal |
|---|---:|---:|---:|---:|
| G1 unchanged | 0 | 1 | 0 | 0 |
| G2 first consumer broken | 5 | 0 | 1 | 1 |
| G3 last consumer broken | 5 | 0 | 1 | 1 |

No retained log contains a fatal Git diagnostic or `ERR_MODULE_NOT_FOUND`. The checked late
copies and matrix write completed. `F7-1` holds for the normal invalid and valid setup states.

### 1.2 `F7-2` — the current derived count is 31

Two complete current fast runs independently measured:

```
52 REQUIRED — 21 PASS, 31 FAIL
70 CONTROL  — 70 PASS, 0 FAIL
14 OBSERVED
136 total rows
process exit 1 on both runs
```

Complete stdout is byte-identical across the two runs, sha256
`36fdeda0c59811d3a7851ec8b0d3af790931b0495c6dcb0a046c1ed193bff524`. The matrices are also
byte-identical, sha256
`af11a9501a2744232556a81e04cd3a30241ca082499b1b079d1224e702ece34a`. Both stderr captures are
empty. The current operative records say 31 where they state the live result. Their 28-of-49
passages are labelled and reconciled historical measurements rather than rewritten. `F7-2`
holds.

## 2. Prior critical repairs

### 2.1 All six absent/empty dependency states refuse before scoring

Each dependency state was driven separately in an isolated repository, with the other two trees
non-empty:

| Dependency | State | Process | REQUIRED | CONTROL | Diagnosis |
|---|---|---:|---:|---:|---|
| `contracts/lib/forge-std` | absent | 2 | 0 | 0 | names absent-or-empty Forge tree |
| `contracts/lib/forge-std` | empty | 2 | 0 | 0 | names absent-or-empty Forge tree |
| `contracts/lib/openzeppelin-contracts` | absent | 2 | 0 | 0 | names absent-or-empty Forge tree |
| `contracts/lib/openzeppelin-contracts` | empty | 2 | 0 | 0 | names absent-or-empty Forge tree |
| `ts/node_modules` | absent | 2 | 0 | 0 | names absent-or-empty Node tree |
| `ts/node_modules` | empty | 2 | 0 | 0 | names absent-or-empty Node tree |

No incomplete copied dependency can reach G1 or be scored as a gate failure.

### 2.2 Both `Z-clean` predicates fail closed

The exact fast and gate predicates were driven over their respective path boundaries:

| Harness predicate | Repository state | Git rc | output/diagnostic lines | Predicate |
|---|---|---:|---:|:---:|
| fast | clean | 0 | 0 | PASS |
| fast | dirty | 0 | 1 | FAIL |
| fast | status error | 128 | 1 | FAIL |
| gate | clean | 0 | 0 | PASS |
| gate | dirty | 0 | 1 | FAIL |
| gate | status error | 128 | 1 | FAIL |

Both complete fast runs and the complete gate run then reported `Z-clean CONTROL PASS` with Git
rc 0 and zero boundary lines.

### 2.3 Optional fast-output setup fails closed

Four separately driven states — absent evidence directory, evidence target colliding with a
directory, absent matrix parent, and matrix target colliding with a directory — each returned 2
with one named preflight failure and zero REQUIRED/CONTROL rows. Both valid complete runs wrote
their evidence transcript and matrix successfully.

### 2.4 Subject, provenance, counting, integrity, and protected boundaries

- Both harnesses accept only a lowercase exact 40-hex commit object and establish object presence
  and type before selecting it. The two complete fast runs archived the requested
  `bb664c626d592d86391f644bf014e76f2bbf7db4`; `P3-provenance` matched its complete 498-blob tree.
- The fast execution witnesses held twice: type strings 26 executions, eval codes 14, vendor
  honesty 17, verifier 8, all at the subject blobs. `Z-gate5` and `Z-signed` held.
- The complete gate run's clone worktree matched the same requested subject over 498 tracked blob
  paths. `P3-provenance`, `Z-clean`, and `Z-signed` all passed.
- Dynamic matrix counts, rather than source-text estimates, produced 52/70/14 for fast and
  7/10/3 for gate. No printed FAIL is omitted from either matrix. The four D-066 lines remain
  OBSERVED rather than inflating CONTROL.
- `TESTS.patch` is unchanged from the frozen test checkpoint, sha256
  `3780e63a68ba013a085937c5019a837eb02fc4dda0238c21b2bd2074a908442b`, and `git apply --check`
  succeeds against an isolated extraction of the pre-repair subject. It was not applied by this
  review.
- `docs/gate-s2-evidence.md` remains sha256
  `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589`. The proposal, three
  production guards, `scripts/test.sh`, `verifier/test_verifier.py`, `ts/src/signer/eip712.ts`,
  ablation report, `TESTS.patch`, and signed pack are byte-identical between the correction
  commit and its parent.

## 3. `F8-1` — G2 is satisfied by a gate that ignores the named failure

### 3.1 The confound in the unmodified complete run

The G2 fixture changes the normative `ActionPayload` publication. That is consumed twice by the
real gate:

1. `scripts/check-type-strings.sh` prints `DRIFT in ActionPayload` at its named stage and exits
   non-zero.
2. Later, the verifier suite reads the same proposal and compares the published value with its
   independently recovered `ActionPayload`. It reports
   `FAIL: test_recovered_strings_match_the_published_ones` for `struct='ActionPayload'`.

The current G2 assertions at `a-extract-gate.sh:435-442` check only:

- the named guard body has the DRIFT and lacks its success line;
- the eval-code and vendor-honesty bodies have their success lines; and
- the global log has `GATE FAILED` and lacks `GATE PASSED`.

They neither require the rest of the gate to be clean nor establish which non-zero stage left the
final `fail` accumulator set.

### 3.2 Causal control

In a private clone at the pre-repair subject, I applied exactly two probe mutations:

1. the harness's own G2 `ActionPayload` transposition; and
2. `scripts/test.sh`'s named invocation changed from
   `./scripts/check-type-strings.sh || fail=1` to
   `./scripts/check-type-strings.sh || true`.

The second mutation is the defective gate wiring G2 is supposed to exclude: the named guard runs
and prints its failure, but its status cannot set the top-level accumulator. The observed result:

```
named type-string DRIFT                  1
eval-code success                         1
vendor-honesty success                    1
later verifier ActionPayload failure      1
GATE PASSED                               0
GATE FAILED                               1
supervisor process                        5
```

Those values satisfy every current G2 predicate. The gate fails because the later verifier suite
sets `fail=1`, not because the named guard's status is carried. Thus the probe cannot distinguish
the intended gate from the defective one and cannot support the current statements that the
first consumer's failure survives later consumer success or that the gate carries that verdict.

G1 still demonstrates baseline invocation and the guard's success output. G3 remains a valid
last-consumer direction in this run: its raw log contains the intended vendor-honesty failure and
no separate verifier or toolchain failure. Neither repairs G2's missing causal discrimination.

## 4. Repository and workspace checks

All checks below ran after the complete measurements:

- both harnesses pass `bash -n`;
- the correction commit passes `git diff --check`;
- `check-secrets.sh`: clean;
- `check-review-scope.sh`: 537 of 537 tracked files assigned; 155 remediation-surface files and
  79 preservation-only files reported;
- `check-suite-floors.sh`: 92 Foundry, 527 TypeScript, 221 verifier tests, 7 samples, 78 tamper
  cases, 30 modes, all read from the single source in `scripts/test.sh`;
- `check-rename-gate.sh`: private repository, D-016 publication block intact;
- workspace guards: 13 machine-state findings, all 13 baselined, 0 new; PASS by ratchet.

These checks do not cure `F8-1`; they establish that the review and its isolated probes did not
move a protected or unrelated surface.

## 5. Limits and disposition

1. The deep `./scripts/test.sh --gate` profile remains unmeasured, exactly as the operative
   records disclose. A deep run cannot repair a non-discriminating fast mutation and was not
   needed to establish this FAIL.
2. Dependency probes cover the required absent and empty states, not every malformed filesystem
   object type.
3. D-065's hostile caller-variable class remains out of scope. No such variable is a finding.
4. The causal mutant and all captures were isolated and are not committed.
5. This review evaluates instrument readiness only. It does not assess or approve a production
   implementation, and it does not discharge D-059(7)'s outstanding deep-profile portion.

**FAIL.** `F8-1` lets the gate-binding instrument report every G2 predicate PASS when the named
guard's failure is explicitly ignored by the top-level gate. That is the control-cannot-observe
class D-065(3) keeps in scope. A FAIL consumes no implementation attempt. Nothing is signed,
ratified, certified, reaffirmed, published, renamed, pushed, or implemented by this review.
