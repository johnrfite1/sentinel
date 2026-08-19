# REVIEWER 1 — PROVENANCE ATTESTATION

## Commit reviewed

```
7e0ab7f1057de278c09cc803ab4ca266f53399e1
```

Verified at the start and again at the end with `git rev-parse HEAD` in
`<REVIEW-ROOT>/worktrees/w1` (detached worktree,
`gitdir: <REPO>/.git/worktrees/w1`).

**The three files my findings rest on, hashed at the commit reviewed:**

```
c8f6ceb177fe9d589853a330110dcf9cb9a9443f418126e1d5ca732bc8d1f773  scripts/test.sh
b89f35ed7239a5aac320a89a768c0ef686a4d6c6d8b0950aeb8d51fc8967e0ed  scripts/check-gate-immutability.sh
4f1c4ab2d186ec5e6caf2eea5fe7b6d47531843cef629cdba3dd90e763cd7c2e  scripts/check-review-scope.sh
```

## Tools and versions

| Tool | Version |
|---|---|
| forge | 1.7.1 (commit `4072e48705af9d93e3c0f6e29e93b5e9a40caed8`, build 2026-05-08) |
| node | v26.3.0 |
| npm | 11.16.0 |
| python3 | 3.9.6 |
| bash | 3.2.57(1)-release, arm64-apple-darwin25 |
| git | 2.50.1 (Apple Git-155) |
| OS | Darwin 25.5.0 (macOS, arm64) |

## Baseline, recorded BEFORE any probe

```
$ git diff HEAD --stat -- .
 contracts/lib/forge-std              | 2 +-
 contracts/lib/openzeppelin-contracts | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)
```

Those two entries are the provisioned symlinks to the main repository and are the expected
starting state, not drift. `pgrep -f sentinel-gate` returned nothing — no gate was in flight
when I started.

## Every command that mutated anything

**No file tracked at `7e0ab7f` was modified, created or deleted by me at any point.** I made no
edits to the worktree. The complete set of state changes:

1. **`forge build --root contracts`** and the gate's own build — created the gitignored build
   artifacts `contracts/out` (2.9 MB) and `contracts/cache` (20 KB) inside the worktree. These
   are compiler output, are excluded by `.gitignore`, and are required for the gate to run.
   **Left in place**, since deleting them would only force the next reviewer to rebuild.
2. **`./scripts/test.sh --gate`** — the required deep profile. Creates and removes its own
   snapshot under `$TMPDIR`; spawns Anvil; writes and removes temporary TAP and forge-JSON
   files. All self-cleaning; verified no `sentinel-gate.*` file was added by my run.
3. **`probes/probe-snapshot-reachable.sh`** — wrote **only** inside my evidence directory, under
   `evidence/r1/probes/run.XwF61u/`, with `TMPDIR` overridden to a directory inside that path so
   it could not touch the real `$TMPDIR` or any live gate. It edits only synthetic scripts it
   created itself.
4. **`TMPDIR=<isolated> ./scripts/check-gate-immutability.sh`** — ran the shipped guard
   unmodified, with `TMPDIR` pointed at `evidence/r1/probes/tmpiso.ucFRJj`.
5. **`SENTINEL_SCOPE_BASE=… ./scripts/check-review-scope.sh`** — environment variable only, read-only script.

**Nothing outside the worktree's gitignored build output and my own evidence directory was
written.** I did not touch `<REPO>` at any point. I did not delete
the six pre-existing leaked `sentinel-gate.*` files in the user's `$TMPDIR`; I read one of them
to identify it and left all six in place, since they are evidence and are not mine to remove.

## Revert confirmation

`git checkout -- .` was **NOT** used, per common brief Rule 2 — it destroys the symlinked
toolchain and then reports clean.

Final state, verified with `git diff HEAD --stat -- .` (Rule 2's prescribed check, since bare
`git status` exits 128 in these worktrees):

```
 contracts/lib/forge-std              | 2 +-
 contracts/lib/openzeppelin-contracts | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)
```

**Byte-identical to the baseline.** Symlinks confirmed intact and still pointing at the main
repository:

```
contracts/lib/forge-std              -> <REPO>/contracts/lib/forge-std
contracts/lib/openzeppelin-contracts -> <REPO>/contracts/lib/openzeppelin-contracts
ts/node_modules                      -> <REPO>/ts/node_modules
```

`git ls-files --others --exclude-standard -- .` returns only `ts/node_modules` (the provisioned
symlink), i.e. no stray untracked files. HEAD still `7e0ab7f1057de278c09cc803ab4ca266f53399e1`.

## Deep-profile attestation (the condition of this round)

Run from the frozen worktree at exactly `7e0ab7f`. Complete output recorded at
`evidence/r1/deep-gate-run.txt`, 1298 lines, with the wrapper's own timestamps and exit codes.

**Read, not statused:**
- profile confirmed: `== solidity build + tests (profile: gate) ==` (line 134)
- `GATE PASSED` present (line 946)
- `forge build exit: 0`; `GATE EXIT CODE: 0` (line 1297)
- no `GATE FAILED`, no `FLOOR BREACHED`, no `GATE SOURCE CHANGED`, no `SUITE NOT CLEAN`

The failure mode the brief warned of — exit 0 with no `GATE PASSED` — did not occur here.

## Evidence files

| File | Lines |
|---|---|
| `REPORT.md` | 335 |
| `NULL-RESULTS.md` | 160 |
| `DEAD-PROBES.md` | 62 |
| `COVERAGE.md` | 70 |
| `CRITIQUE.md` | 83 |
| `ATTESTATION.md` | this file |
| `deep-gate-run.txt` | 1298 (raw deep-profile output) |
| `probe-snapshot-reachable.out` | raw output, R1-F1 |
| `probe-harness-leak.out` | raw output, N2 |
| `probes/probe-snapshot-reachable.sh` | the R1-F1 probe, re-runnable |

## Declaration

Every finding in `REPORT.md` was reproduced by me on this machine at this commit. No finding is
reported on suspicion; there are no leads. The two probes that measured nothing are in
`DEAD-PROBES.md`, including the one where my own hypothesis was wrong. What I did not reach is
in `COVERAGE.md`, and it is roughly 60% of my assigned surface.

*Reviewer 1, D-055(e), 2026-08-19.*
