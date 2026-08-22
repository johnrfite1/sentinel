# C-SNAPSHOT — exact reproduction runbook

All mutating commands below target private clones. Do not apply `mutate.py` to the shared
repository.

```bash
SUBJECT=1655b120a653b60ccb5b3a22583c0001d59ea7a4
REPO="$(git rev-parse --show-toplevel)"
EVIDENCE="$REPO/docs/review-2026-08-19-d057-targeted/batch-cards/C-SNAPSHOT-tests"
PATCHED="$(mktemp -d)/repo"

git clone --no-hardlinks --local "$REPO" "$PATCHED"
git -C "$PATCHED" checkout --detach "$SUBJECT"
git -C "$PATCHED" submodule update --init --recursive
git -C "$PATCHED" apply --check "$EVIDENCE/TESTS.patch"
git -C "$PATCHED" apply "$EVIDENCE/TESTS.patch"
```

If the isolated clone has no dependency directory, provision a temporary untracked symlink
without committing it:

```bash
ln -s "$REPO/ts/node_modules" "$PATCHED/ts/node_modules"
```

## 1. Frozen focused pre-repair result

```bash
npm --prefix "$PATCHED/ts" run typecheck
node --test --test-concurrency=1 \
  "$PATCHED/ts/test/vault.snapshot.classification.test.ts"
```

Expected: typecheck exit 0; 22 tests, nine controls pass and the thirteen named R2-F6 tests fail.
The passing set is stable, pure B1, both pure B2 variants, ordinary RPC failure and four
oracle-negative controls. The failing status is the intended pre-repair observation, not a
post-repair success claim.

## 2. Exact baseline oracle mutations

```bash
for mutation_id in $(python3 "$EVIDENCE/mutate.py" --list); do
  git -C "$PATCHED" restore ts/src/signer/vault.ts
  python3 "$EVIDENCE/mutate.py" "$PATCHED" "$mutation_id"
  npm --prefix "$PATCHED/ts" run typecheck
  node --test --test-concurrency=1 \
    "$PATCHED/ts/test/vault.snapshot.classification.test.ts"
done
git -C "$PATCHED" restore ts/src/signer/vault.ts
```

All eight mutants must typecheck and fail their named assertions as recorded in
`mutation-matrix.tsv`. In particular, the rank accumulator must return 14/8 and reset-on-repeat
10/12 with their documented passing controls. Do not count a typecheck failure as a behavioral
catch.

## 3. Top-level fast-gate binding

Use two clean subject clones with dependencies provisioned. The first remains unpatched:

```bash
CONTROL="$(mktemp -d)/repo"
git clone --no-hardlinks --local "$REPO" "$CONTROL"
git -C "$CONTROL" checkout --detach "$SUBJECT"
git -C "$CONTROL" submodule update --init --recursive
(cd "$CONTROL" && ./scripts/test.sh)
```

Expected: Foundry 103/103, TypeScript 527/527, verifier 221/7/78/30, exit 0, `GATE PASSED`.

Apply only the frozen tests in the other clone:

```bash
git -C "$PATCHED" status --short
(cd "$PATCHED" && ./scripts/test.sh)
```

`PATCHED` already contains only the test patch plus any untracked dependency plumbing from setup;
do not reapply it. The only source/test change must be
`ts/test/vault.snapshot.classification.test.ts`. Expected pre-repair result: Foundry 103/103;
TypeScript 536/549 with only the thirteen named C-SNAPSHOT failures and all four negative-oracle
controls passing; later ablation/verifier consumers green; top-level exit 5 and supervisor
refusal. No deep profile or post-repair pass is part of this card.

## 4. Evidence integrity and guards

From the shared repository after staging only this directory:

```bash
git diff --cached --check
shasum -a 256 -c "$EVIDENCE/CHECKSUMS.sha256"
./scripts/check-secrets.sh
./scripts/check-secrets.sh --staged
./scripts/check-review-scope.sh
./scripts/check-findings-ledger.sh
./scripts/check-suite-floors.sh
./scripts/check-vendor-honesty.sh
(cd "$(dirname "$REPO")" && tools/guards/run_guards.sh "$(basename "$REPO")")
git status --short --branch
```

Read every output. Workspace guard success is ratcheted evidence; baselined findings may remain.
