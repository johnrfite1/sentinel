# ATTESTATION — Reviewer 3 (onchain and corpus)

## Commit reviewed
`7e0ab7f1057de278c09cc803ab4ca266f53399e1`
("Pre-review provenance checkpoint: preserve and curate round six")

Worktree: `<REVIEW-ROOT>/worktrees/w3`, detached HEAD.
**The live repository `<REPO>` was never written to.** Every mutation,
build and test ran under the worktree path above; the only reads outside it were through the two
provisioned symlinks (`contracts/lib/*`, `ts/node_modules`), which are inputs, not outputs.

## Tools and versions
| Tool | Version |
|---|---|
| forge | 1.7.1 (commit `4072e48705af9d93e3c0f6e29e93b5e9a40caed8`, build 2026-05-08) |
| solc | 0.8.28 (via forge, `via_ir = true`, `optimizer_runs = 200`) |
| node | v26.3.0 |
| npm | 11.16.0 |
| python3 | system (macOS), used only for read-only analysis and the two gate-script blocks I read |
| git | 2.50.1 (Apple Git-155) |
| platform | darwin 25.5.0, arm64 |

Foundry profile: **default** (`fuzz.runs = 1024`, `invariant.runs = 256`, `depth = 64`).
The `gate` profile (20 000 / 2 048) was **not** used — see COVERAGE.

## Baseline, recorded BEFORE any mutation
```
$ pgrep -f sentinel-gate                  -> no match (no gate run in flight)
$ git diff HEAD --stat -- .
 contracts/lib/forge-std              | 2 +-
 contracts/lib/openzeppelin-contracts | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)
   (both entries are the provisioned symlinks — the expected provisioned state)

$ forge build --root contracts
 Compiling 34 files with Solc 0.8.28 -> Compiler run successful!

$ forge test --root contracts             -> exit 0
 Ran 5 test suites: 75 tests passed, 0 failed, 0 skipped (75 total)
   SentinelTypes.t.sol 21 · harness 3 · SentinelVault.t.sol 22 ·
   backstops 12 · invariants 17
 (baseline/forge-test.txt)

$ forge test --root contracts --match-path 'test/SentinelVault.invariants.t.sol' \
      --match-test '^invariant_'         -> exit 0, 11 tests
 (confirms the campaign selector picks exactly the eleven invariants)

$ cd ts && npm test                       -> exit 0
 tests 513 / suites 90 / pass 513 / fail 0 / cancelled 0 / skipped 0 / todo 0
 (baseline/npm-test.txt)
```

## Pristine copy used for revert verification
Taken before the first mutation, with `cp -R`, into
`<SCRATCH>/scratchpad/pristine`:
`contracts/src`, `contracts/test`, `ts/src`, `ts/test`, `fixtures`, `scripts`, `docs`, plus
`contracts/foundry.toml`, `ts/package.json`, `ts/tsconfig.json`,
`Sentinel_Protocol_Lab_Proposal_v0_2.md`.

**`git checkout -- .` was never run** — it destroys the symlinked toolchain and then reports a
clean tree. Reverts are `cp` from the pristine copy followed by `cmp`.

## Every command that mutated anything

Two files were ever written inside the worktree, one at a time, always restored before the next:

| File | Mutations applied | Harness |
|---|---|---|
| `contracts/src/SentinelVault.sol` | **53** (49 measured + 4 dead probes, all 4 re-run) | `scratchpad/probes/mutate.sh`, `marginal.sh` |
| `ts/src/evaluate/checks.ts` | **12** (12 measured, 0 dead probes) | `scratchpad/probes/tsmutate.sh` |

Every mutation was a single exact-string substitution asserted to occur exactly once, applied by
`python3`, guarded by:
1. occurrence count `== 1` (else `DEAD-PROBE pattern-count`);
2. `cmp` against pristine — the file must have MOVED (else `DEAD-PROBE source-identical`);
3. `forge build` / `npm run typecheck` must SUCCEED (else `DEAD-PROBE build-failed`, never a catch);
4. bytecode-prefix comparison (advisory `WARN` only — see DEAD-PROBES DP-6 for its limitation).

Per-mutation commands and results:
`evidence/r3/mutations/log.txt`, `marginal.txt`, `driver*.txt`, and one
`<id>.full.txt` / `<id>.invariants.txt` / `<id>.deterministic.txt` per mutation.
`evidence/r3/ts-mutations/log.txt` and one `<id>.npmtest.txt` per TypeScript mutation.

Drivers: `scratchpad/probes/{drive.sh,drive2.sh,drive3.sh,drive4.sh,drive5.sh,tsdrive.sh}`.

**Probes that mutated NOTHING in the worktree** (pure, out-of-tree, listed for completeness):
`regen-ablation.ts`, `g5-residue.ts`, `leakage-probe.ts`, `withheld-probe.ts`, and the
`report-copy/report-dropRes/report-addMandateActive` variants — all written to the scratchpad,
importing the worktree's modules read-only.

**Nothing outside those two files was written.** In particular `fixtures/corpus/**` was never
regenerated: `npm --prefix ts run corpus` was **not run** (it rewrites the committed artifacts in
place unless `SENTINEL_CORPUS_OUT` is set — see COVERAGE and CRITIQUE C-4).

## Revert verification — `cmp`/`diff -r` against the pristine copy, NOT git

```
$ cmp contracts/src/SentinelVault.sol  <pristine>/contracts/src/SentinelVault.sol   -> IDENTICAL
$ cmp ts/src/evaluate/checks.ts        <pristine>/ts/src/evaluate/checks.ts         -> IDENTICAL
$ cmp ts/src/ablation/report.ts        <pristine>/ts/src/ablation/report.ts         -> IDENTICAL
$ cmp ts/src/corpus/leakage.ts         <pristine>/ts/src/corpus/leakage.ts          -> IDENTICAL

$ diff -r <dir> <pristine>/<dir>   for contracts/src contracts/test ts/src ts/test
                                       fixtures scripts docs
  CLEAN  contracts/src
  CLEAN  contracts/test
  CLEAN  ts/src
  CLEAN  ts/test
  CLEAN  fixtures
  CLEAN  scripts
  CLEAN  docs
```

Toolchain intact (this is the check `git checkout -- .` would have silently broken):
```
contracts/lib/forge-std              -> <REPO>/contracts/lib/forge-std
contracts/lib/openzeppelin-contracts -> <REPO>/contracts/lib/openzeppelin-contracts
ts/node_modules                      -> <REPO>/ts/node_modules
```

Tracked tree, submodule-safe form (`git status` with no pathspec exits 128 here, as the brief warns):
```
$ git diff HEAD --stat -- .
 contracts/lib/forge-std              | 2 +-
 contracts/lib/openzeppelin-contracts | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)      <- IDENTICAL to the baseline above

$ git ls-files --others --exclude-standard
 ts/node_modules                                       <- the provisioned symlink; nothing else
```

## Post-revert re-baseline — both suites back to the recorded starting state
```
$ forge build --root contracts   -> Compiler run successful!
$ forge test --root contracts    -> exit 0
 Ran 5 test suites in 8.59s: 75 tests passed, 0 failed, 0 skipped (75 total tests)
 (baseline/forge-test-FINAL.txt)

$ cd ts && npm test              -> exit 0
 tests 513 / pass 513 / fail 0
 (baseline/npm-test-FINAL.txt)
```

**The worktree is reverted. Confirmed by `cmp` and `diff -r` against a pristine out-of-tree copy,
by the unchanged `git diff HEAD --stat`, by the three toolchain symlinks still resolving, and by
both suites returning exactly their recorded baseline counts.**

## Independence

I was given no other reviewer's findings and read none of `evidence/r1`, `evidence/r2` or
`evidence/r4`. Where a finding of mine overlaps prior recorded work I found it independently and
say so in the finding itself before making the claim — R3-F1 (round six lens 5, partial
duplicate), R3-F3 (A-032's undemonstrated hypothesis), R3-F5/R3-F6/R3-F8 (the Solidity or
un-repaired half of `D-05` / `D-06` / `D-10`).

## Probes preserved on disk

Register §13.2 records that a falsification living only in a scratchpad *"dies with this session"*
and that this has already cost the project twice. **Every probe behind every finding here is
copied to `evidence/r3/probes/`**, with a README mapping each script to the findings it produced
and marking which four are pure (no worktree mutation at all). They are re-runnable against the
frozen commit by re-pointing two path variables.
