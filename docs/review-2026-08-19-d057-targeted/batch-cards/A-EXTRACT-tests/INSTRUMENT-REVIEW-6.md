# A-EXTRACT — SIXTH INDEPENDENT INSTRUMENT REVIEW

# VERDICT: FAIL

The two restored Forge-library preflight branches work as claimed, the four former controls are
honestly classified as `OBSERVED`, the current fast totals reproduce, and the measured
seven-of-ten git-invocation wording is accurate under the harness's active replacement hardening.
The instrument nevertheless fails D-066's repair argument in a sibling dependency path and still
contains a control that can report `PASS` after its probe failed.

- **`F6-1` — an empty `ts/node_modules` dependency tree is scored as G1.** The gate harness
  copies that dependency after `P3-provenance`, with no absent-or-empty preflight. With both Forge
  trees complete and clean but `ts/node_modules` empty, all three gate logs show missing-package
  errors, G1 prints `REQUIRED FAIL`, the harness reports `6 of 7 REQUIRED` / `10 of 10 CONTROL`
  and selects its exit-1 branch. D-066(4) requires an incomplete dependency precondition to refuse
  before any REQUIRED or CONTROL verdict and never appear as a gate defect.
- **`F6-2` — `Z-clean` masks a failed `git status`.** Both harnesses derive `dirty` from
  `git status ... | wc -l` without requiring the pipeline to have succeeded. A clean repository
  produces `rc=0, dirty=0, PASS`; a dirty repository produces `rc=0, dirty=1, FAIL`; but a
  repository whose submodule metadata makes `git status` exit 128 produces `dirty=0` and the
  control prints `PASS` beside Git's fatal diagnostic. This is a paired, moving control with an
  unhandled error branch, not a theoretical objection.
- **`F6-3` — the governing card still publishes a current count of 49 binding assertions.**
  `CARD.md:290` says **“Fourteen CASES; forty-nine BINDING assertions”**. The current matrix has
  52 REQUIRED rows, and the same card says 52 at lines 10 and 462. This is not inside a historical
  review quotation or a superseded-measurement banner.

Any one of `F6-1` or `F6-2` is sufficient for FAIL under D-065(3). This review changes no gate,
production file, harness, evidence file, existing review, signed text, or certified material.

---

## 0. Review identity and bar

| | |
|---|---|
| Subject | branch `step-3/isolated-signer`, exact commit `bcee8084e0295316b7d4a8fcb8729471c489b6cb` |
| Threat model | D-065: faithful measurement in a **non-adversarial** environment; no new hostile caller-controlled variable is offered as a finding |
| Governing repair argument | D-066(4): an incomplete dependency precondition refuses before REQUIRED/CONTROL scoring and is never scored as a gate defect |
| Fast harness | sha256 `68dec333a34ecbc3186419ba2264af513c74058771772be24deee275f3c7e4c9` |
| Gate harness | sha256 `e4141c166353c941a479fa730dfaaaff2089dbb17df697aeffeb666271189fd3` |
| Repository writes before this record | none |
| Scratch mutation | private clones and captures outside the repository only |

I read `AGENTS.md`, `docs/repair-protocol.md`, D-065, D-066, the complete current `CARD.md`,
`COVERAGE.md`, `RESULTS.md`, `GATE-BINDING.md`, both harnesses, and
`INSTRUMENT-REVIEW-5.md`. Output, banners, tokens, diagnostics, matrices and witness rows were
read directly; exit status was never treated as a case discriminator.

## 1. Dependency preflight — two repaired branches hold; one sibling defeats the argument

### 1.1 Both restored branches discriminate before scoring

The committed tree has exactly two `contracts/lib` gitlinks:

```
forge-std             bf647bd6046f2f7da30d0c2bf435e5c76a780c1b
openzeppelin-contracts 5fd1781b1454fd1ef8e722282f86f9293cacf256
```

`a-extract-gate.sh:288-291` checks those same two names in one loop before the first REQUIRED or
CONTROL call. Each branch was driven independently in a private clone; the other sibling was
nonempty in each run.

| Probe | Process result | REQUIRED rows | CONTROL rows | Diagnosis |
|---|---:|---:|---:|---|
| empty `forge-std` | exit 2 | 0 | 0 | names `contracts/lib/forge-std` absent or empty |
| populated `forge-std`, empty `openzeppelin-contracts` | exit 2 | 0 | 0 | names `contracts/lib/openzeppelin-contracts` absent or empty |
| both merely nonempty, invalid subject | exit 2 | 0 | 0 | advances past both dependency checks and refuses the subject grammar |

The two repaired branches and their immediate sibling completeness therefore **hold**. Neither
can now be scored as G1 in the empty-tree state they claim to reject.

### 1.2 `F6-1` — the gate's Node dependency is omitted from that preflight

The same harness consumes a third dependency tree:

```
a-extract-gate.sh:342  cp -R "$ROOT/ts/node_modules" "$BASECOPY/ts/node_modules"
```

That copy occurs **after** `P3-provenance`, and `cp -R` accepts an empty directory. There is no
prior absent-or-empty check for it. This is not a hostile environment input; it is an ordinary
incomplete local dependency installation.

I built a private source clone with valid, clean submodule repositories at the exact gitlink
commits and an existing but empty `ts/node_modules`. Its own scoped `git status` returned 0 with
no output before the run. The gate harness then produced:

```
G1  REQUIRED FAIL  unchanged fast gate ... (supervisor rc=5)
G2  all three REQUIRED PASS
G3  all three REQUIRED PASS

REQUIRED : 6 of 7 held
CONTROL  : 10 of 10 held
REQUIRED FAILURES with every control holding: the gate binding is NOT established.
```

All three retained gate logs contain `ERR_MODULE_NOT_FOUND`, including missing `viem` and
`@anthropic-ai/sdk`, and each contains all three A-EXTRACT consumer banners. The populated paired
control, run from the real complete dependency tree, returned `7 of 7` / `10 of 10`, G1
supervisor rc 0, and G2/G3 rc 5/5.

The empty-Node state is therefore a dependency precondition presented as a G1 gate defect. It is
the state D-066(4) says must not exist. The card's statement that the fast harness has only the
Node dependency does not remove that same dependency from the gate harness.

## 2. Fast matrix, control audit, and `F6-2`

### 2.1 Current classification and totals reproduce twice

Two clean, sequential full runs at the exact pre-repair oid produced byte-identical stdout and
byte-identical matrices:

```
matrix rows: 136
REQUIRED:     52 total, 21 PASS, 31 FAIL
CONTROL:      70 total, 70 PASS, 0 FAIL
OBSERVED:     14 total
process:      exit 1 branch — REQUIRED failures with every control holding
```

Both runs printed the five identity facts twice, `P3-provenance` over 498 blob paths with digest
`d0a672e8e34aa7e31a2515c7f2d0c626364a1369b03a46afeb8bbb1cdb1b1669`, and these four execution
witnesses:

| Consumer | sha256 | executions |
|---|---|---:|
| `check-type-strings.sh` | `9bcdb5621ca7355cc9b57471af3bd75d9d2627549f5a717e3bf480ab9966761a` | 26 |
| `check-eval-codes.sh` | `7970d22674643fceca848a34b68119dc4957fbc7169a37f2036f4e17c8fe6123` | 14 |
| `check-vendor-honesty.sh` | `1ead2f37b474867d0f52675909ca9f0621c9fb3cf25f27c4770949afde7e157e` | 17 |
| `test_verifier.py` | `924749d5c362f209a625488b85ae1858b18ab79a7c2cf72f4bf7744e78084d89` | 8 |

`1-ctl`, `5-ctl`, `8-ctl` and `13-ctl` each appear exactly once as `OBSERVED ....`. Source
inspection confirms their former predicates are still guaranteed by P6 before those lines can
print. D-066's reclassification is honest: CONTROL moved `74 -> 70`, OBSERVED `10 -> 14`, and
REQUIRED stayed 52.

I inspected all 70 current CONTROL predicates. The four structurally unreachable controls are no
longer counted. The previously recorded redundancies remain (`10-ctl` repeats REQUIRED `11a`, and
the gate's `G2-scope`/`G3-scope` are sub-conjunctions of their REQUIRED siblings), but they can
fail and are not the same defect as an unreachable control.

### 2.2 `F6-2` — a probe error becomes `Z-clean PASS`

The fast and gate harnesses use the same shape (`a-extract.sh:1586`,
`a-extract-gate.sh:460`):

```
dirty="$(cd "$ROOT" && git status --porcelain -- <boundary> | wc -l | tr -d ' ')"
check CONTROL Z-clean "$([ "$dirty" = "0" ] && echo 0 || echo 1)" ...
```

The assignment's status is ignored. An exact isolated drive of this expression produced:

| Repository state | `git status` pipeline rc | `dirty` | Printed predicate |
|---|---:|---:|---|
| clean | 0 | 0 | PASS |
| one dirty path under `scripts/` | 0 | 1 | FAIL |
| broken submodule gitdir; Git prints `fatal: not a git repository` | 128 | 0 | **PASS** |

The control genuinely moves on a normal dirty path, so it is not dead. Its failure-to-execute
branch is nevertheless self-masking: no status output is counted as zero changed paths. The
failure was also observed end-to-end in the first dependency scratch run: the fatal diagnostic
printed immediately before `case Z-clean CONTROL PASS`, and the summary still reported all ten
controls held. This is inside D-065(3): the control's own probe failed under a non-adversarial
repository state and the counter still certified it.

## 3. Replacement pinning and wording — HELD

Static enumeration of actual command sites in `a-extract-gate.sh` gives exactly ten git
invocations.

| Kind | Lines / commands |
|---|---|
| pinned, 7 | 304 `cat-file`; 311 `clone`; 312 `checkout`; 316 `rev-parse`; 329 `ls-tree`; 333 `ls-files`; 464 `show` |
| not command-pinned, 3 | 278 `--version`; 335 `hash-object --stdin-paths`; 460 `status --porcelain` |

An independent replacement-base probe moved the subject tree from
`592186a834c803fc2654677579f7c9ffa15f60a4` to
`6bc2b507a04d89ad94b1facd403646e319783901`; `--no-replace-objects` restored the first tree.
The full `ls-tree` digest likewise moved under replacement and returned under the pin. This is the
paired control proving replacement was potent.

For the three unpinned invocations:

- `git --version` was identical with replacement enabled or disabled;
- `git hash-object HANDOFF.md` was identical in all three states;
- `git status` **is** replacement-sensitive in isolation (0 rows became 2), but the harness's
  earlier exported `GIT_NO_REPLACE_OBJECTS=1` restored it to 0. Thus this third command is safe
  because of the active process-wide hardening, not because `status` is inherently immune.

The live operative wording in `CARD.md`, `COVERAGE.md`, `RESULTS.md` and `GATE-BINDING.md` now
says seven of ten invocations are pinned and the other three cannot be reached by replacement.
The old exhaustive phrases remain only as quoted historical findings inside
`INSTRUMENT-REVIEW-5.md`, which this review does not rewrite. The measured claim therefore holds,
with the `status` qualification above.

## 4. Deletion audit and `F6-3`

The `989f315 -> bcee808` corrective commit changes only D-066 plus the four operative evidence
files and two harnesses. The gate harness has eight additions and **zero deletions**. The fast
harness has eight additions and eight deletions: exactly the four two-line `check CONTROL`
statements replaced by four two-line `check OBSERVED` statements. Every deleted evidence line is
accounted for by the hash/count refresh, the four reclassification descriptions, or replacement
of the three exhaustive pinning phrases. I found **no other silently removed requirement** in the
commit's deletion set.

The current requirements audit did find one count that the correction missed. `CARD.md:290`
still says 49 binding assertions in the present-tense TEST MATRIX introduction, while the current
matrix and two other lines in that card say 52. Historical `49` and `74` measurements elsewhere
are retained with supersession/reconciliation context; this card sentence is not.

## 5. Full gate run — measured, logs read

The full `a-extract-gate.sh` harness ran alone against the complete local dependencies and exact
pre-repair oid. Its matrix contains 20 rows:

```
REQUIRED : 7 of 7 held
CONTROL  : 10 of 10 held
OBSERVED : 3
process  : exit 0
```

The three supervisor outcomes are 0/5/5. Each retained G1/G2/G3 log contains exactly one copy of
each named TS, EC and VH stage banner. G1 contains exactly one `GATE PASSED` and no fail token;
G2 and G3 each contain exactly one `GATE FAILED`, no pass token, and one
`GATE DID NOT REACH COMPLETION`. No fatal, missing-file, broken-pipe, unbound-variable or syntax
diagnostic appears in the normal harness log or any of the three gate logs.

This re-establishes the published fast-profile gate figures and is the populated control for
`F6-1`. It does not erase the fact that an incomplete dependency turns G1 red instead of refusing
preflight.

## 6. Integrity and untouched scope

The corrective commit changes only these seven files: `docs/decisions.md`, the four operative
A-EXTRACT Markdown files, and the two harnesses. Blob equality across `bcee808^ -> bcee808`
independently confirms all of the following untouched:

- production/fixture consumers: the proposal, `ts/src/signer/eip712.ts`,
  `docs/ablation-report.md`, the three production guards, and `verifier/test_verifier.py`;
- `TESTS.patch` — sha256
  `3780e63a68ba013a085937c5019a837eb02fc4dda0238c21b2bd2074a908442b`, and
  `git apply --check` still succeeds against a private `bb664c6` extraction;
- all five historical instrument-review records, including `INSTRUMENT-REVIEW-5.md`;
- signed text: `docs/gate-s2-evidence.md` sha256
  `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589`, identical now and at
  `bb664c6`;
- Gate 5 material: the live pin, live §2 table and `bb664c6` §2 table independently hash to
  `c9034750e56b8801be7cd31cce33c42caad209013a61ed7082155db33903959c`.

Both clean fast runs also printed `Z-clean`, `Z-gate5` and `Z-signed` PASS, and the normal gate run
printed `Z-clean` and `Z-signed` PASS without diagnostics. Those controls are corroboration; the
blob and direct hash comparisons above are the independent evidence.

## 7. Residuals and limitations

1. **Deep-profile invocation remains unmeasured.** This review ran the complete gate-binding
   harness (three fast gates), not a separate `./scripts/test.sh --gate`. D-059(7) remains partly
   discharged exactly as `GATE-BINDING.md` says.
2. **The 31 pre-repair REQUIRED failures were not semantically re-adjudicated one by one.** Their
   identities, outputs, controls, reason classes and totals were inspected across two identical
   runs; this review is of the instrument, not a new adjudication of the consumers.
3. **D-065's hostile caller-variable class remains out of scope.** No new environment door is a
   finding here. The replacement probe tests the published structural claim, not a hostile-caller
   threat model.
4. **The first attempted fast capture was discarded.** I supplied a non-existing
   `A_EXTRACT_EVIDENCE_DIR`; `_log` does not create it and printed missing-file diagnostics while
   the summary still completed. Two later runs used existing directories and were diagnostic-free.
   This is recorded as an operator/setup limitation, not used as evidence for the verdict.
5. Scratch logs and mutation repositories are temporary local evidence and are not committed.

## 8. Disposition

**FAIL.** `F6-1` violates the exact general repair argument John recorded in D-066(4), and
`F6-2` is a self-masking control under D-065(3). `F6-3` is an additional current evidence-count
defect. No gate is signed, reopened, certified, reaffirmed or closed by this review. A FAIL
consumes no implementation attempt, and Batch A1 remains closed.
