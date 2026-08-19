# R4 — PROVENANCE ATTESTATION

## Commit reviewed

```
7e0ab7f1057de278c09cc803ab4ca266f53399e1
Pre-review provenance checkpoint: preserve and curate round six
```

Verified with `git rev-parse HEAD` in the worktree at the start and at the end of the review.

- **Worktree:** `<REVIEW-ROOT>/worktrees/w4` (detached)
- **Evidence directory:** `<REVIEW-ROOT>/evidence/r4`
- **The live repository `<REPO>` was never written to.** It was read
  only indirectly, through the provisioned symlinks (`contracts/lib/*`, `ts/node_modules`), which
  I did not replace or modify.
- **Read outside the worktree, never written:**
  `<HOME>/Projects/_archive/sentinel-round-six-2026-08-18/**` (the round-six raw
  archive) and the briefs under `…/sentinel-d055e-review/briefs/`. All access was `ls`, `cat`,
  `cmp`, `diff`, `find`, `stat`, `shasum -c`. Nothing in the archive was created, modified or
  deleted; `PRESERVATION.txt`'s "source NOT modified and NOT deleted" still holds after my run.
- I did **not** read the r1/r2/r3 briefs, to keep the free lens uncontaminated. I did read
  `REVIEW-STATE.md`, which is shared round state, and it is why I avoided the wave-1 leads.

## Environment and tool versions

| | |
|---|---|
| Platform | macOS 26.5.2 (`25F84`), arm64 |
| Harness shell | **zsh** (see DEAD-PROBES — this caused 3 of my 4 dead probes) |
| Script shell | GNU bash 3.2.57(1)-release (arm64-apple-darwin25) |
| git | 2.50.1 (Apple Git-155) |
| forge | 1.7.1 (`4072e48705af9d93e3c0f6e29e93b5e9a40caed8`), Solc 0.8.28 |
| node | v26.3.0 |
| python3 | 3.9.6 |
| shasum | BSD, `-a 256` |

## Baseline, recorded BEFORE any mutation

```
$ git diff HEAD --stat -- .
 contracts/lib/forge-std              | 2 +-
 contracts/lib/openzeppelin-contracts | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)
```

Those two entries are the provisioned submodule symlinks and are the expected starting state, not
my changes. **This is unchanged at the end of the review.** Symlinks confirmed intact at both
ends (`contracts/lib/forge-std`, `contracts/lib/openzeppelin-contracts`, `ts/node_modules` — 3
symlinks, all resolving into the live repo).

`forge build --root contracts` was run before any Foundry or corpus work, per the brief:
"Compiling 34 files with Solc 0.8.28 … Compiler run successful!"

## Pristine copy used for revert verification

Taken before the first mutation, with `rsync -a`, excluding `node_modules` and `lib`:

```
<SCRATCH>/scratchpad/pristine
```

Contents: `scripts/`, `verifier/`, `docs/`, `fixtures/`, `ts/src/`, `ts/test/`, `contracts/src/`,
`contracts/test/`, plus `contracts/foundry.toml`, `ts/package.json`, `ts/tsconfig.json`,
`HANDOFF.md`, `README.md`, `Sentinel_Protocol_Lab_Proposal_v0_2.md` — **364 files.**

## EVERY command that mutated anything

**Exactly one file was ever modified: `Sentinel_Protocol_Lab_Proposal_v0_2.md`.** It was mutated
three times, each time via a `python3` heredoc, each time restored from the pristine copy and
each restore verified with `cmp` before the next probe.

| # | Mutation | Purpose | Restored + `cmp` verified |
|---|---|---|---|
| 1 | Removed the only §5.7.1 mention of `EVAL_MANDATE_PRINCIPAL_IS_OWNER`; added a mention inside `## 6. AI and Context Scope` | R4-F3 demo 1 | ✅ |
| 2 | Moved the `EIP712Domain` type-string literal out of §5.8 into §6 | R4-F3 (scope check) | ✅ |
| 3 | Transposed `string name`/`string version` in the `EIP712Domain` line §5.8 publishes; inserted a correct copy earlier, in §5.9 | R4-F3 demo 2 | ✅ |

Restore command used each time (**never `git checkout -- .`**):

```
cp "$PRIS/Sentinel_Protocol_Lab_Proposal_v0_2.md" Sentinel_Protocol_Lab_Proposal_v0_2.md
cmp Sentinel_Protocol_Lab_Proposal_v0_2.md "$PRIS/Sentinel_Protocol_Lab_Proposal_v0_2.md"
```

Each mutation was confirmed to have **moved the input** before its guard result was believed
(`grep -c` on the mutated region / `grep -n` on the moved line), per COMMON-BRIEF rule 4.

## Non-mutating commands that wrote to disk

All outside the worktree or into gitignored build output; none altered a tracked file.

- `forge build`, `forge test --json` → `contracts/out/`, `contracts/cache/` (gitignored build
  artifacts), and `/tmp/r4-forge.json`, `/tmp/r4-forge.err`
- `npm test` → `/tmp/r4-ts.tap`, `/tmp/r4-ts.log`; started and stopped local anvil instances via
  the test harness
- `python3 verifier/verify.py … --tamper all` → tampering is in-memory; no fixture changed (see
  final verification)
- `sed -n … > /tmp/sec5711.txt`
- The six deliverables in `evidence/r4/`

**No network calls were made.** In particular I did not run the Gate 7 canary live — only
`--report`, which the source documents as making no API call, and which I confirmed by reading
`ts/src/spike/canary.ts:105-136` before running it.

## Final verification — the worktree is reverted

```
$ # full cmp of every pristine file against the worktree
$ compared 364 files; 0 differ

$ git diff HEAD --stat -- .
 contracts/lib/forge-std              | 2 +-
 contracts/lib/openzeppelin-contracts | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)

$ git status --porcelain -- scripts ts/src ts/test contracts/src contracts/test verifier docs fixtures
   (empty)

$ ls -l contracts/lib/ ts/node_modules | grep -c '^l'
3
```

**364 of 364 files byte-identical to the pre-review state. `git diff HEAD --stat` is identical to
the baseline. The toolchain symlinks are intact.** Verification is by `cmp` against the pristine
copy, not by git, exactly as the brief requires — and the symlink count is reported alongside
because a revert that verifies clean while the toolchain is gone is the failure mode the brief
names.

## Concurrency discipline

Checked for an in-flight gate with `pgrep -f sentinel-gate` (**not** `pgrep -f scripts/test.sh`,
which no longer matches since A-076). I did not run the deep or fast gate: R1 owns the
exact-commit deep gate and had completed it. One background job (the TypeScript suite) ran at a
time; `forge test` was run only after it finished, deliberately, to avoid round six's
concurrency-induced false results.

## Deliverables

All six are on disk in `evidence/r4/`: `REPORT.md`, `NULL-RESULTS.md`, `DEAD-PROBES.md`,
`COVERAGE.md`, `CRITIQUE.md`, `ATTESTATION.md`.

## Findings summary

| ID | Severity | One line |
|---|---|---|
| R4-F1 | **MEDIUM** | Signed §11.0 (and `decisions.md` A-076) say five accepted limits remain; six do — `G-3` dropped from both ledgers |
| R4-F2 | **LOW** | Round-six preservation README omits one of its own four sanitizations, in the document designated the authority on that |
| R4-F3 | **MEDIUM** | Two gate guards certify a *section* while grepping the whole document; `check-type-strings.sh` passes while §5.8 publishes a transposed type string |
| R4-F4 | **MEDIUM** | `session-state.md` §3 stale for the fifth time: publishes 507/198, tree measures 513/209, and misquotes `TS_MIN_TESTS` downward |

0 Critical · 0 High · 3 Medium · 1 Low · 0 Info. Three leads, labelled as leads, in COVERAGE.md.

Severities are mine, assigned independently, and not softened. I adjudicate none of them.
