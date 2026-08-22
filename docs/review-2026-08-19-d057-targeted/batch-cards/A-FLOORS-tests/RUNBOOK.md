# A-FLOORS — reproduction runbook

All commands below start from a clean Sentinel repository whose exact subject exists locally.
The harnesses refuse tracked source changes before scoring. `ts/node_modules` and both Solidity
submodules must be provisioned; an incomplete setup is exit 2 and is not a verdict.

## 1. Verify exact baseline identity

```bash
git rev-parse HEAD
git status --porcelain --untracked-files=no
git submodule status
test -d ts/node_modules
```

Behavioral baseline is `1a133301533e9d959dbafbbcc7ffe05e7eb78df3`; the corrected pre-repair
focused evidence was driven against clean Review-1 commit
`e3b8a76cff7a002b3211bb8f8a75f2d14b86a37e` by the corrected external harness.

## 2. Focused contract

```bash
evidence=docs/review-2026-08-19-d057-targeted/batch-cards/A-FLOORS-tests
subject="$(git rev-parse HEAD)"
matrix_out="$(mktemp)"
A_FLOORS_MATRIX="$matrix_out" \
  "$evidence/a-floors.py" "$(pwd -P)" "$subject"
focused_rc=$?
shasum -a 256 "$matrix_out"
printf 'focused_rc=%s\n' "$focused_rc"
```

At the frozen pre-repair subject, expected verdict is exit 1, REQUIRED 10/71, CONTROL 65/65.
Exit 2 is an
invalid instrument/setup state and must not be reported as a product verdict.

## 3. Causal sibling and satisfying control

Use the same clean source/subject and a fresh output path for each:

```bash
A_FLOORS_VARIANT=digits-zero-sibling A_FLOORS_MATRIX="$zero_matrix" \
  "$evidence/a-floors.py" "$(pwd -P)" "$subject"
zero_rc=$?

A_FLOORS_VARIANT=exact-positive-control A_FLOORS_MATRIX="$positive_matrix" \
  "$evidence/a-floors.py" "$(pwd -P)" "$subject"
positive_rc=$?
```

The zero sibling must return REQUIRED 65/71 and CONTROL 65/65, with exactly six `Z-*` failures.
Compare its matrix by case name to `focused-matrix-review1.tsv`: all 81 old rows must be present
and PASS. The exact-positive control must return 71/71, 65/65 and completion.

## 4. Serial top-level gate contract

First confirm no competing Sentinel gate is running. Use a new empty log directory. The harness
runs seven gates synchronously and must not be launched in parallel with any other final gate:

```bash
evidence=docs/review-2026-08-19-d057-targeted/batch-cards/A-FLOORS-tests
subject="$(git rev-parse HEAD)"
gate_logs="$(mktemp -d)"
"$evidence/a-floors-gate.py" "$(pwd -P)" "$subject" "$gate_logs"
gate_rc=$?
shasum -a 256 "$gate_logs"/*.raw.log "$gate_logs/matrix.tsv"
printf 'gate_rc=%s\n' "$gate_rc"
```

Historical baseline expectation is exit 1, REQUIRED 2/4, CONTROL 3/3. The cases execute in this fixed order:
unchanged fast, wrong-reader fast, unchanged deep, wrong-reader deep, raised-floor control,
B-EVENTS deletion, C-SNAPSHOT deletion.

The harness timeout, clone failure, missing dependency, dirty tracked source or non-empty log
directory is exit 2 before final scoring. Do not convert it to HOLD/FAIL. Review-1 F1/F2 did not
change this harness; do not present a rerun-free correction as refreshed gate/timing evidence.

## 5. Inspect material output

For every raw gate log read, rather than infer:

```bash
rg -n 'foundry:|typescript:|FLOOR BREACHED|suite 221|corpus: 50 fixtures|GATE PASSED|GATE FAILED|GATE DID NOT REACH|This IS the deep profile' "$gate_logs"/*.raw.log
```

G1/G3 are green at the pre-repair baseline and therefore fail their required assertions. After a
conforming repair they must name the reader-publication defect, show later success, and fail
closed. G5/G6 must keep their exact 92/527 deletion deltas.

## 6. Repository and workspace guards

```bash
./scripts/check-secrets.sh --worktree
./scripts/check-secrets.sh --staged
./scripts/check-review-scope.sh
./scripts/check-findings-ledger.sh
./scripts/check-suite-floors.sh
./scripts/check-vendor-honesty.sh
../tools/guards/run_guards.sh .
```

Read all output. The workspace guard's pass is ratcheted; it reports 13 pre-existing baselined
machine-state findings and must report zero new.

## 7. Post-repair fixed target

A conforming implementation subject must return focused REQUIRED 71/71 and CONTROL 65/65, then
gate REQUIRED 4/4 and CONTROL 3/3 with the same frozen harness hashes. Re-run repository/workspace
guards and obtain a different independent verifier at that exact subject. Do not edit the
instruments to fit the implementation.
