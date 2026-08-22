# B-EVENTS — exact reproduction runbook

All mutating commands below target a private clone. Do not run `mutate.py` against the shared
repository.

```bash
SUBJECT=46b62bea748b0dcdf6c02288659a3be1bbb945ba
REPO="$(git rev-parse --show-toplevel)"
EVIDENCE="$REPO/docs/review-2026-08-19-d057-targeted/batch-cards/B-EVENTS-tests"
PROBE="$(mktemp -d)/repo"

git clone --no-hardlinks --local "$REPO" "$PROBE"
git -C "$PROBE" checkout --detach "$SUBJECT"
git -C "$PROBE" submodule update --init --recursive
git -C "$PROBE" apply --check "$EVIDENCE/TESTS.patch"
git -C "$PROBE" apply "$EVIDENCE/TESTS.patch"
```

If the clone has no installed TypeScript dependencies, provision its ignored dependency directory
from the subject repository without committing it:

```bash
ln -s "$REPO/ts/node_modules" "$PROBE/ts/node_modules"
```

## 1. Unchanged focused control

```bash
(
  cd "$PROBE/contracts"
  forge fmt --check test/SentinelVault.events.t.sol
  forge build
  forge test --match-path test/SentinelVault.events.t.sol -vv
)
```

Expected: build warning-clean; 11 passed, 0 failed.

## 2. Complete mutation run

```bash
OUT="$(mktemp -d)"
cp "$PROBE/contracts/test/SentinelVault.events.t.sol" "$OUT/SentinelVault.events.t.sol"
printf 'mutant\tkind\tbuild\ttest\tfailing_tests\n' > "$OUT/matrix.tsv"

while IFS= read -r id; do
  git -C "$PROBE" restore contracts/src/SentinelVault.sol
  cp "$OUT/SentinelVault.events.t.sol" "$PROBE/contracts/test/SentinelVault.events.t.sol"
  python3 "$EVIDENCE/mutate.py" "$PROBE" "$id"

  if forge build --root "$PROBE/contracts" > "$OUT/$id.build.txt" 2>&1; then
    build=PASS
    if forge test --root "$PROBE/contracts" \
        --match-path test/SentinelVault.events.t.sol -vv > "$OUT/$id.test.txt" 2>&1; then
      test_result=SURVIVED
    else
      test_result=CAUGHT
    fi
    failing="$(rg '^\[FAIL:' "$OUT/$id.test.txt" \
      | sed -E 's/^.*\] ([^()]*)\(.*/\1/' | sort -u | paste -sd, - || true)"
  else
    build=FAIL
    test_result=NOT_RUN
    failing=''
  fi

  kind=PRODUCTION
  [ "$id" = instrument_wrong_emitter ] && kind=CONTROL
  printf '%s\t%s\t%s\t%s\t%s\n' \
    "$id" "$kind" "$build" "$test_result" "$failing" >> "$OUT/matrix.tsv"
done < <(python3 "$EVIDENCE/mutate.py" --list)

git -C "$PROBE" restore contracts/src/SentinelVault.sol
cp "$OUT/SentinelVault.events.t.sol" "$PROBE/contracts/test/SentinelVault.events.t.sol"
rg -i 'warning' "$OUT"/*.build.txt || true
awk -F '\t' 'NR > 1 { count[$2 FS $3 FS $4]++ } END { for (key in count) print key, count[key] }' \
  "$OUT/matrix.tsv" | sort
```

Expected: `PRODUCTION PASS CAUGHT 49`, `CONTROL PASS CAUGHT 1`, and no warning output. A build
failure is reported as `NOT_RUN` and is never a behavioral catch.

## 3. Known current-suite hole and frozen-test kill

Use a second clean subject clone **without** `TESTS.patch`:

```bash
CURRENT="$(mktemp -d)/repo"
git clone --no-hardlinks --local "$REPO" "$CURRENT"
git -C "$CURRENT" checkout --detach "$SUBJECT"
git -C "$CURRENT" submodule update --init --recursive
python3 "$EVIDENCE/mutate.py" "$CURRENT" field_action_via_false
forge build --root "$CURRENT/contracts"
forge test --root "$CURRENT/contracts" -vv
git -C "$CURRENT" restore contracts/src/SentinelVault.sol
git -C "$CURRENT" apply "$EVIDENCE/TESTS.patch"
python3 "$EVIDENCE/mutate.py" "$CURRENT" field_action_via_false
forge build --root "$CURRENT/contracts"
forge test --root "$CURRENT/contracts" --match-path test/SentinelVault.events.t.sol -vv
```

Expected current-suite result: 92 passed, 0 failed. With the frozen patch, only
`test_OverrideAndActionExecuted_exactFieldsTrueRouteOrderAndVaultEmitter` fails; the automatic
success control remains green.

## 4. Durable receipt probe

On a patched clean clone with dependencies provisioned:

```bash
cp "$EVIDENCE/live-receipt-probe.ts" "$PROBE/ts/test/b-events-receipt-probe.ts"
forge build --root "$PROBE/contracts"
(
  cd "$PROBE/ts"
  ./node_modules/.bin/tsx test/b-events-receipt-probe.ts
)
```

The exact expected JSON is preserved in `logs/live-receipt.log`. The probe exits nonzero on any
status, log order/emitter/count, relay boolean, or nonce mismatch.

## 5. F7-R1 false baseline and truthful control

On a third clean subject clone without either patch applied:

```bash
NATSPEC="$(mktemp -d)/repo"
git clone --no-hardlinks --local "$REPO" "$NATSPEC"
git -C "$NATSPEC" checkout --detach "$SUBJECT"
set +e
python3 "$EVIDENCE/nat-spec-probe.py" "$NATSPEC"
baseline_exit=$?
set -e
test "$baseline_exit" -eq 1
git -C "$NATSPEC" apply --check "$EVIDENCE/NATSPEC.patch"
git -C "$NATSPEC" apply "$EVIDENCE/NATSPEC.patch"
python3 "$EVIDENCE/nat-spec-probe.py" "$NATSPEC"
git -C "$NATSPEC" diff -- contracts/src/SentinelVault.sol
```

Expected baseline: `false_claim_count=1`, `truthful_replacement_count=0`, exit 1. Expected
replacement control: `0`, `1`, exit 0. The diff must contain comment lines only.

## 6. Top-level fast-gate binding

Use a fresh subject clone with only `TESTS.patch` applied and dependencies provisioned as above:

```bash
GATE="$(mktemp -d)/repo"
git clone --no-hardlinks --local "$REPO" "$GATE"
git -C "$GATE" checkout --detach "$SUBJECT"
git -C "$GATE" submodule update --init --recursive
git -C "$GATE" apply "$EVIDENCE/TESTS.patch"
(cd "$GATE" && ./scripts/test.sh)
python3 "$EVIDENCE/mutate.py" "$GATE" field_action_via_false
(cd "$GATE" && ./scripts/test.sh)
```

Expected unchanged control: top-level `GATE PASSED`. Expected mutant: the Solidity stage names the
override event test failure and the top-level supervisor refuses completion. This card does not
run or claim the deep profile.

## 7. Repository/workspace guards after the evidence commit

```bash
(cd "$REPO" && ./scripts/check-secrets.sh)
(cd "$REPO" && ./scripts/check-review-scope.sh)
(cd "$REPO" && ./scripts/check-findings-ledger.sh)
(cd "$(dirname "$REPO")" && tools/guards/run_guards.sh "$(basename "$REPO")")
git -C "$REPO" status --short --branch
```

Read every output. Workspace guard success is ratcheted evidence (baselined findings may remain),
not a claim that the repository contains no historical machine-state debt.
