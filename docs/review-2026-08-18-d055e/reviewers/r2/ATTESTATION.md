# REVIEWER 2 — ATTESTATION

## Commit reviewed

```
$ cd <REVIEW-ROOT>/worktrees/w2 && git rev-parse HEAD
7e0ab7f1057de278c09cc803ab4ca266f53399e1
```

Detached HEAD, worktree `_archive/sentinel-d055e-review/worktrees/w2`. **The live repository
`<REPO>` was never written to.** Read access to it occurred only
through the provisioned symlinks (`ts/node_modules`, `contracts/lib/*`), which I did not modify.

## Environment and tool versions

```
macOS 26.5.2 / Darwin 25.5.0
node   v26.3.0
npm    11.16.0
forge Version: 1.7.1
Commit SHA: 4072e48705af9d93e3c0f6e29e93b5e9a40caed8
Build Timestamp: 2026-05-08T07:54:31.470926000Z (1778226871)
Python 3.9.6   (probe scaffolding only)
solc   0.8.28 (as selected by foundry.toml)
```

## Concurrency note

At the moment I started, `pgrep -f sentinel-gate` returned pid **69845** (`bash
<TMP> --gate`, 11 seconds elapsed) — another reviewer's deep
gate. I did not start a gate run. All of my measurements are FAST profile and were taken in my own
worktree with my own process's exit status.

## Baseline, taken BEFORE any mutation

```
$ cd <REVIEW-ROOT>/worktrees/w2/contracts && forge build
Compiling 34 files with Solc 0.8.28
Solc 0.8.28 finished in 20.28s
Compiler run successful!            -> exit 0

$ cd <REVIEW-ROOT>/worktrees/w2 && npm --prefix ts test           # log: baseline-test.txt
ℹ tests 513
ℹ suites 90
ℹ pass 513
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 55700.974584
EXIT=0

$ cd <REVIEW-ROOT>/worktrees/w2 && npm --prefix ts run typecheck  # log: baseline-typecheck.txt
> tsc --noEmit
EXIT=0
```

The first attempt at that baseline FAILED (exit 1, 4 tests) because `contracts/out/` did not
exist. That dead probe is recorded in full in `DEAD-PROBES.md` DP-1, because a mutation run
against that state would have looked like a caught mutation.

## Everything that mutated anything

Eight source mutations. Each was applied by `probes/mutate.sh`, which (a) backs up the file, (b)
applies a `perl -0pi -e` substitution, (c) **aborts with `DEAD PROBE: mutation changed nothing`
if the mutated file still `cmp`s equal to pristine**, (d) prints the diff against pristine, (e)
runs the tests, (f) restores from the backup, (g) `cmp`s the restored file against pristine and
prints `REVERT VERIFIED`. All eight printed `REVERT VERIFIED`.

| # | file | mutation | outcome |
|---|---|---|---|
| M1 | `ts/src/simulate/anvil.ts` | delete `walk(child);` from `internalCalls` | caught |
| M2 | `ts/src/simulate/anvil.ts` | `tracer: "callTracer"` → `"prestateTracer"` | caught |
| M3 | `ts/src/simulate/index.ts` | `internalCalls(callTrace).map` → `(callTrace.calls ?? []).map` | caught |
| M4 | `ts/src/signer/protocol.ts` | `SIGNER_ANCHOR_NOT_OBSERVED: "CONFORMANCE"` → `"EXECUTABILITY"` | caught |
| M5 | `ts/src/signer/attest.ts` | drop the hash half of the anchor comparison | caught |
| M6 | `ts/src/signer/attest.ts` | nonce-guard key → `\`${chainId}:${vault}:${nonce}\`` (revert D-053(b)) | caught |
| M7 | `ts/src/signer/attest.ts` | delete the A-043 `requestedVerdict === "ALLOW"` guard | caught |
| M8 | (M1 re-run after the DP-2 runner fix) | as M1 | caught |

No other file in the worktree was written by me. The four probe scripts
(`probes/p1-*.ts`, `p2-*.ts`, `p2b-*.ts`, `p3-*.ts`) live in the **evidence** directory, not
the worktree, and import the worktree source read-only.

## Revert verification — by `cmp`, not by git

```
$ P=<scratchpad>/pristine-w2      # 361 files: ts/src, ts/test, scripts, contracts/src,
                                   # contracts/test, docs, verifier, fixtures, ts/package.json,
                                   # ts/tsconfig.json — copied BEFORE the first mutation
$ cd $P && find . -type f | while read -r f; do
      cmp -s "$P/$f" "<REVIEW-ROOT>/worktrees/w2/$f" || echo "DIFFERS: $f"; done
(no output)
```

**Zero differing files.** The symlinked toolchain is intact and was never replaced:

```
ts/node_modules                     -> <REPO>/ts/node_modules
contracts/lib/forge-std             -> <REPO>/contracts/lib/forge-std
contracts/lib/openzeppelin-contracts-> <REPO>/contracts/lib/openzeppelin-contracts
```

**I did not run `git checkout -- .` at any point**, and I did not run bare `git status`.
`git diff HEAD --stat -- .` reports:

```
 contracts/lib/forge-std              | 2 +-
 contracts/lib/openzeppelin-contracts | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)
```

**This output is identical to the one I recorded before touching anything** — it is the provisioned
symlinks standing in for submodules, not a residue of my work. It is why my revert check is `cmp`
and not git.

## Post-revert re-verification

```
$ cd <REVIEW-ROOT>/worktrees/w2 && npm --prefix ts test           # log: post-revert-test.txt
ℹ tests 513
ℹ pass 513
ℹ fail 0
EXIT=0

$ cd <REVIEW-ROOT>/worktrees/w2 && npm --prefix ts run typecheck  # log: post-revert-typecheck.txt
EXIT=0
```

**Identical to the baseline.** The tree is in the state I received it.

## What I left behind in the worktree, deliberately

- `contracts/out/` — Foundry build artifacts produced by `forge build`. Gitignored, not a source
  file, and **required for `npm --prefix ts test` to run at all**. Removing it would leave the
  next reader with the DP-1 failure. Recorded rather than removed; see `CRITIQUE.md` §6.

Nothing else. `git ls-files --others --exclude-standard` reports only `ts/node_modules` (the
provisioned symlink).

## Evidence files

```
REPORT.md  NULL-RESULTS.md  DEAD-PROBES.md  COVERAGE.md  CRITIQUE.md  ATTESTATION.md
baseline-test.txt  baseline-typecheck.txt  post-revert-test.txt  post-revert-typecheck.txt
probes/mutate.sh
probes/p1-sim-anchor-straddle.ts  probes/p1-output.txt
probes/p1-control.ts              probes/p1-control-output.txt
probes/p2-ceiling-third-route.ts  probes/p2b-ceiling-allow.ts
probes/p3-callgraph-absence.ts
probes/node_modules -> <REPO>/ts/node_modules   (probe resolution only)
```

Every finding in `REPORT.md` is reproducible from this directory against the frozen commit. No
finding rests on a run I did not print the totals of.
