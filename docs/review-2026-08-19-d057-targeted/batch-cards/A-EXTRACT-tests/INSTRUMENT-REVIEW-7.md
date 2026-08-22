# A-EXTRACT — SEVENTH INDEPENDENT INSTRUMENT REVIEW

# VERDICT: FAIL

The three sixth-review repairs hold in the states they name: each of the three copied gate
dependency trees refuses separately when absent and when empty before any REQUIRED or CONTROL
row; both `Z-clean` predicates fail closed when Git's status probe fails and still distinguish
ordinary clean from dirty repositories; and the current fast matrix is 52 REQUIRED rows. The
fast harness's two optional evidence destinations also refuse setup errors before scoring.

The instrument nevertheless has two in-scope honesty defects:

- **`F7-1` — the gate harness scores and returns success after its optional evidence destination
  fails.** `A_EXTRACT_GATE_LOGDIR` is advertised by the usage text, but it is neither validated
  nor opened before scoring. Only after all 7 REQUIRED and 10 CONTROL rows have printed does the
  harness try to create the directory and copy the logs and matrix; every failure there is
  ignored. With the destination set to a child of a regular file, the complete gate harness
  printed both the directory-creation error and the matrix-write error, then printed
  `REQUIRED : 7 of 7 held`, `CONTROL : 10 of 10 held`,
  `FAST-PROFILE GATE BINDING MEASURED`, and exited 0. This is the same operator/setup class the
  sixth repair closed for `A_EXTRACT_EVIDENCE_DIR`, left live in its gate-harness sibling. It is
  a non-adversarial, self-masking setup failure under D-065(3).
- **`F7-2` — a live result statement still publishes the superseded 49-row outcome.** The
  current `GATE-BINDING.md` §5 says the fast harness measures **28 REQUIRED failures** at
  `bb664c6`. Two complete current runs instead measured **31 failures: 21 of 52 held**. The
  historical `28 of 49` passages in `RESULTS.md` are explicitly reconciled as history; this §5
  sentence is a present-tense statement of what the harness measures now. The direct `49`
  sentence identified as `F6-3` was corrected, but this derived current figure was not. A
  current published figure that was never remeasured is expressly in scope under D-065(3).

Either finding is sufficient for FAIL. This review changes no harness, gate, production file,
operative evidence document, historical review, `TESTS.patch`, signed text, or certified
material.

---

## 0. Review identity and bar

| | |
|---|---|
| Branch | `step-3/isolated-signer` |
| Exact subject | `d64bc55df55575e98d01e7c91d4c37316b320e02` |
| Subject commit message | `A-EXTRACT: sixth-review instrument defects closed. INSTRUMENT ONLY.` |
| Parent | `a0cc67f8f66feeb2ffcabfb561b07ebdc2ef0f84` — sixth independent review, VERDICT FAIL |
| Fast harness | sha256 `9e489ee6f4adab00535d036619738cf1faa97ec8ab070d22cbf29dd3e769bc1a` |
| Gate harness | sha256 `b8290f9931b540eb8a4dd381dfd9aaa43f143792a0cbdaef3d0c73bb24b8ff50` |
| Threat model | D-065: faithful measurement in a non-adversarial environment; no newly named hostile caller variable is offered as a finding |
| Governing repair argument | D-066(4): an incomplete dependency precondition refuses before REQUIRED/CONTROL scoring and is never scored as a gate defect |
| Repository state at start | clean; HEAD and the resolved subject were the same exact object |
| Repository writes before this record | none; every mutation and capture was in a temporary clone or directory outside the repository |

The initially supplied 40-character expansion of the short subject id did not exist in this
repository. I independently resolved `d64bc55^{commit}` to the exact subject above; the task
owner then corrected the expansion to that same oid. No review work was performed against the
nonexistent string.

I read the workspace instructions, `docs/session-state.md`, `docs/repair-protocol.md`, D-065 and
D-066 in `docs/decisions.md`, the complete current `CARD.md`, `COVERAGE.md`, `RESULTS.md`,
`GATE-BINDING.md`, both harnesses, and `INSTRUMENT-REVIEW-6.md`. I inspected every line of both
harnesses and the complete subject-commit diff. Measurements below use output, matrices,
diagnostics, named stage results, supervisor outcomes, execution witnesses, and completion
tokens; exit status is never treated as a per-case discriminator.

## 1. Sixth-review repairs

### 1.1 `F6-1` — all three copied dependency trees hold, absent and empty

Each branch was driven independently in a private clone. The other two dependency paths were
non-empty in each run.

| Dependency | State | Process | REQUIRED rows | CONTROL rows | Result |
|---|---|---:|---:|---:|---|
| `contracts/lib/forge-std` | absent | 2 | 0 | 0 | named preflight refusal |
| `contracts/lib/forge-std` | empty | 2 | 0 | 0 | named preflight refusal |
| `contracts/lib/openzeppelin-contracts` | absent | 2 | 0 | 0 | named preflight refusal |
| `contracts/lib/openzeppelin-contracts` | empty | 2 | 0 | 0 | named preflight refusal |
| `ts/node_modules` | absent | 2 | 0 | 0 | named preflight refusal |
| `ts/node_modules` | empty | 2 | 0 | 0 | named preflight refusal |

The checks precede the first scored call, `P3-provenance`. An absent or empty copied dependency
can no longer be presented as G1. `F6-1` holds for all six required states.

### 1.2 `F6-2` — both `Z-clean` predicates fail closed and move

The fast and gate predicates were driven with their exact respective path boundaries:

| Harness predicate | Repository state | Git rc | Output/diagnostic lines | Predicate |
|---|---|---:|---:|:---:|
| fast | clean | 0 | 0 | PASS |
| fast | one dirty in-boundary path | 0 | 1 | FAIL |
| fast | status probe cannot run | 128 | 1 | FAIL |
| gate | clean | 0 | 0 | PASS |
| gate | one dirty in-boundary path | 0 | 1 | FAIL |
| gate | status probe cannot run | 128 | 1 | FAIL |

Both complete fast runs and the complete gate-harness run then reported `Z-clean CONTROL PASS`
with Git rc 0 and zero lines. The failed-probe branch no longer collapses to clean, and the
ordinary clean/dirty movement remains. `F6-2` holds.

### 1.3 `F6-3` — the direct total is 52; one derived current figure remains stale

Every explicit current total inspected in the card, coverage introduction, results correction,
deliverables table, and live matrix is 52. The complete matrix independently contains:

```
52 REQUIRED — 21 PASS, 31 FAIL
70 CONTROL  — 70 PASS, 0 FAIL
14 OBSERVED
136 total rows
```

The old 49-row measurements in `RESULTS.md` and the harness commentary are labelled historical
and reconciled with the three fence siblings that moved 49 to 52. The live statement in
`GATE-BINDING.md` §5 is different: it says what `a-extract.sh` measures now, and gives 28 failures
rather than 31. That is `F7-2` above.

## 2. Optional evidence destinations and `F7-1`

### 2.1 Fast harness — the repair holds

Four setup failures were driven. Every one returned 2 before any REQUIRED or CONTROL row:

| Destination | Failure | Scored rows |
|---|---|---:|
| `A_EXTRACT_EVIDENCE_DIR` | directory absent | 0 |
| `A_EXTRACT_EVIDENCE_DIR` | output path not writable as a file | 0 |
| `A_EXTRACT_MATRIX_OUT` | parent absent | 0 |
| `A_EXTRACT_MATRIX_OUT` | target not writable as a file | 0 |

Two later complete runs used valid existing evidence directories and explicit matrix files;
both artifacts were written successfully. The fast optional destinations do not score after a
setup failure.

### 2.2 Gate harness — the sibling remains fail-open

The usage text advertises `A_EXTRACT_GATE_LOGDIR`. Unlike the two fast destinations, the gate
harness has no preflight for it. The only handling is after G1, G2, G3, `Z-clean`, and `Z-signed`:

1. `mkdir -p` the requested path;
2. copy each log with errors redirected away;
3. write `matrix.tsv`;
4. ignore the status of every operation and proceed to the summary.

The complete isolated drive used an invalid child beneath a regular file. The observable order
was:

```
7 REQUIRED PASS and 10 CONTROL PASS rows
Z-clean PASS; Z-signed PASS
directory creation: Not a directory
matrix write: Not a directory
REQUIRED : 7 of 7 held
CONTROL  : 10 of 10 held
FAST-PROFILE GATE BINDING MEASURED
process exit 0
```

The failed destination preserved no G1/G2/G3 log or matrix at the promised location. A caller
receives a successful instrument verdict after its requested evidence capture failed. This does
not depend on a hostile environment variable: it is an advertised optional setup input given an
ordinary invalid destination, and is therefore in scope under D-065(3).

## 3. Complete measurements

### 3.1 Fast harness twice

Both runs used the exact pre-repair subject
`bb664c626d592d86391f644bf014e76f2bbf7db4`, valid evidence destinations, and explicit matrix
paths. Both returned the expected exit-1 branch with every control holding.

| Evidence | Run 1 | Run 2 |
|---|---:|---:|
| REQUIRED | 21 of 52 | 21 of 52 |
| CONTROL | 70 of 70 | 70 of 70 |
| OBSERVED | 14 | 14 |
| Matrix rows | 136 | 136 |
| Process | 1 | 1 |

Stdout was byte-identical across the two runs, sha256
`36fdeda0c59811d3a7851ec8b0d3af790931b0495c6dcb0a046c1ed193bff524`. The matrices were
byte-identical, sha256
`af11a9501a2744232556a81e04cd3a30241ca082499b1b079d1224e702ece34a`.

The execution witnesses held on both runs. The inspected run recorded:

| Consumer | Executions | Executed hash prefix |
|---|---:|---|
| `check-type-strings.sh` | 26 | `9bcdb562…` |
| `check-eval-codes.sh` | 14 | `7970d226…` |
| `check-vendor-honesty.sh` | 17 | `1ead2f37…` |
| `test_verifier.py` | 8 | `924749d5…` |

`P3-provenance` matched the complete 498-blob archived tree to the requested commit with digest
`d0a672e8e34a…`. `Z-gate5`, `Z-signed`, and all four consumer witnesses held. I found no
additional dead or self-masking scored predicate in the complete 70-control matrix.

### 3.2 Full gate-binding harness, run alone

The complete current gate harness ran alone, also at the exact pre-repair subject. Its harness
logic completed all three top-level fast gates before the `F7-1` destination failure:

| Arm | Supervisor outcome | Named result read from harness output |
|---|---:|---|
| G1 unchanged | 0 | one passing unchanged gate; TS, EC, and VH present in order and green |
| G2 first consumer broken | 5 | named TS failure; two later consumers green; top-level gate refused |
| G3 last consumer broken | 5 | named VH failure; two earlier consumers green; top-level gate refused |

All 7 REQUIRED and 10 CONTROL predicates held. `P3-provenance` matched HEAD and the clone's
498-path worktree to the requested oid. `Z-clean` recorded Git rc 0 with zero lines, and
`Z-signed` held. The wrapper output and its success/failure/completion statements were read; the
process exit alone was not used as evidence. The run then demonstrated `F7-1` and exited 0.

The separate deep-profile invocation `./scripts/test.sh --gate` remains unmeasured, exactly as
`GATE-BINDING.md` states. This review does not convert the static control-flow argument into a
measured deep run.

## 4. Subject, provenance, replacement, and counting audit

- Both harnesses accept only an exact lowercase 40-hex object id and establish existence/type by
  object-database enumeration before assigning the subject. Invalid shapes are preflight
  refusals, not scored cases.
- The fast snapshot is archived from `SUBJECT_SHA`, not the historical constant. Its whole-tree
  control and four execution witnesses held in both complete runs.
- The gate clone checked out the supplied oid and compared its worktree against the subject's
  full tree. The complete gate run held that control over 498 tracked blob paths.
- The replacement wording is bounded rather than exhaustive: the fast harness has two
  command-local `--no-replace-objects` pins; the gate harness has seven of ten, with the other
  three relying on the active process-wide hardening or being outside object delivery. No new
  caller-controlled environment door is treated as a finding under D-065.
- Dynamic counting came from the emitted matrices, not source greps. The malformed-verdict
  string comparison counts anything other than literal `0` as a failure in both harnesses. No
  printed FAIL was omitted from either complete matrix.
- The four D-066 lines remain `OBSERVED`, not CONTROL. P6 is the enforcing preflight for their
  facts. Current counts are therefore 70 CONTROL and 14 OBSERVED, as ruled.

## 5. Deletions, hashes, protected surfaces, and scope

The subject commit changes exactly six files: the four operative A-EXTRACT evidence documents
and the two harnesses. Its 21 deleted lines are accounted for by the Node-sibling correction,
current hash/result refreshes, replacement of the stale 49-row card sentence, the optional-fast-
destination usage wording, and replacement of each old `Z-clean` pipeline. I found no other
silently removed requirement in the subject diff.

Direct checks:

- `a-extract.sh` sha256 `9e489ee6…bc1a` and `a-extract-gate.sh` sha256 `b8290f99…ff50`
  match the current operative documents and both harnesses' own printed identities.
- `TESTS.patch` is unchanged from the parent, sha256
  `3780e63a68ba013a085937c5019a837eb02fc4dda0238c21b2bd2074a908442b`, and
  `git apply --check` succeeds against a private extraction of `bb664c6`. It was not applied.
- `INSTRUMENT-REVIEW-6.md` is byte-identical between parent and subject.
- `docs/gate-s2-evidence.md` is byte-identical at parent, subject, and pre-repair base, sha256
  `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589`.
- The live Gate 5 pin, the subject's §2 table, and the pre-repair §2 table all equal
  `c9034750e56b8801be7cd31cce33c42caad209013a61ed7082155db33903959c`.
- The proposal, all three production guards, `verifier/test_verifier.py`,
  `ts/src/signer/eip712.ts`, `docs/ablation-report.md`, and `scripts/test.sh` are byte-identical
  between the subject and its parent. No production, fixture, gate, signed, certified, or Gate 5
  surface moved in the reviewed repair commit.

## 6. Residuals and disposition

1. The deep `--gate` profile remains a documented static reading rather than a measured run.
2. Dependency preflight drives covered the requested absent and empty states. Other malformed
   filesystem object types were not added to the contract by this review.
3. D-065's hostile caller-variable class remains out of scope. No such variable is a finding.
4. Temporary clones and captures remain outside the repository and are not committed.

**FAIL.** `F7-1` permits an advertised evidence-capture setup failure to accompany a complete
green result and exit 0. `F7-2` is a live stale result figure under the exact defect class
D-065(3) retains. A FAIL consumes no implementation attempt. Nothing is signed, approved,
ratified, certified, reaffirmed, published, renamed, pushed, or implemented by this review.
