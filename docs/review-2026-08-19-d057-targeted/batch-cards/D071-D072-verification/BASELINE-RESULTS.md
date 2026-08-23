# D-071 / D-072 baseline demonstration

Independent test author. **This file records FAIL at the repair parents.**
It does not score HEAD. It does not assign severity.

Harness: `d071-d072-observe.sh`. Machine: `git version 2.50.1 (Apple Git-155)`.
Matrix: `logs/matrix.tsv`.

## Subjects (remeasured)

| Role | SHA |
|---|---|
| R5 baseline | `558d001546b55bd80156bc875cf080fef0e301eb` |
| V-6/R2 baseline | `1ae684cec83c7bfdb24a8c18ffdeba87c535874f` |

Worktrees: `/tmp/sentinel-r5-base`, `/tmp/sentinel-v6-base`. Isolated clones
for plants and for UNVERIFIED. Main worktree not used as a plant site.

Harness (script rows, `--skip-toplevel`): exit 1, `req_fail=14`,
`ctl_fail=0`, `invalid=0`. R5-5 was then completed on the same
UNVERIFIED clone with the real `./scripts/test.sh --gate` instrument
(not a homemade aggregator). After that row: `req_fail=15`,
`ctl_fail=0`, `not_measured=5`, `invalid=0`. That is the expected
baseline shape: REQUIRED failures, controls held.

## Exact commands that produced UNVERIFIED

```
git clone --local --no-hardlinks /tmp/sentinel-r5-base <isolated-clone>
git -C <isolated-clone> remote get-url origin
# origin=/tmp/sentinel-r5-base   (or /private/tmp/sentinel-r5-base)
<isolated-clone>/scripts/check-rename-gate.sh
<isolated-clone>/scripts/check-rename-gate.sh --gate
```

Measured origin: local path, not a GitHub slug. Fast and `--gate` both printed
`rename gate: UNVERIFIED — could not read visibility for /tmp/sentinel-r5-base`
and exited 0. That is D-071's decisive fact, not a faked UNVERIFIED.

## Exact commands that produced each V-6 vector

Shared prelude, isolated clone of the V-6 baseline, plant then inject:

```
GIT_CONFIG_COUNT=1
GIT_CONFIG_KEY_0=core.excludesFile
GIT_CONFIG_VALUE_0=<ignore-file-listing-the-plant>
```

```
GIT_CONFIG_GLOBAL=<gitconfig whose [core] excludesFile points at that ignore file>
```

```
GIT_CONFIG_SYSTEM=<same shape of gitconfig>
```

```
GIT_CONFIG_NOSYSTEM=1
# no attacker ignore file; only hides if the real system config already excludes
```

```
unset GIT_CONFIG_COUNT GIT_CONFIG_KEY_0 GIT_CONFIG_VALUE_0
unset GIT_CONFIG_GLOBAL GIT_CONFIG_SYSTEM GIT_CONFIG_NOSYSTEM
unset XDG_CONFIG_HOME
HOME=<sandbox>
# <sandbox>/.config/git/ignore lists the plant
```

```
unset GIT_CONFIG_*
XDG_CONFIG_HOME=<sandbox-xdg>
# <sandbox-xdg>/git/ignore lists the plant
```

Unpinned control call after injection:

```
git ls-files --others --exclude-standard
```

No `-c core.excludesFile=`. No `-c core.quotePath=false`.

## R5 rows — baseline `558d001`

| Case | Control fired? | REQUIRED at baseline (FAIL expected) | Actual | Log |
|---|---|---|---|---|
| R5-1-fast-varname | yes (origin local; output UNVERIFIED, not "no remote") | FAIL | **FAIL** — UNVERIFIED line does not name `SENTINEL_RENAME_GATE_UNVERIFIED_OK`; rc=0 | `logs/r5-1-fast.log` |
| R5-2-deep-refuse | yes (same UNVERIFIED clone) | FAIL | **FAIL** — `--gate` rc=0 | `logs/r5-2-deep.log` |
| R5-3-deep-ack-disclose | yes (same clone, `SENTINEL_RENAME_GATE_UNVERIFIED_OK=1`) | FAIL | **FAIL** — rc=0 and no "acknowledged, not verified" disclosure | `logs/r5-3-ack.log` |
| R5-4-readable-clean | yes (`gh repo view johnrfite1/sentinel` → PRIVATE) | PASS (clean path was not the defect) | **PASS** — fast and `--gate` rc=0, `rename gate: clean` | `logs/r5-4-fast.log` |
| R5-5-toplevel-gate | yes (precheck UNVERIFIED, rc=0) | FAIL | **FAIL** — `GATE PASSED` present, `gate_rc=0` | `logs/r5-5-precheck.log`, `logs/r5-5-gate.log`, `logs/r5-5-gate.meta` |

### Excerpts

R5-1 / R5-2 / R5-3 (identical UNVERIFIED text; no ack variable; `--gate` ignored):

```
rename gate: UNVERIFIED — could not read visibility for /private/tmp/sentinel-r5-base (auth? network?).
  D-016 still blocks publication. Verify manually before any public action.
```

R5-4:

```
rename gate: clean (johnrfite1/sentinel is private; D-016 publication block intact)
```

R5-5 precheck, isolated clone origin `/tmp/sentinel-r5-base`, SHA `558d001`:

```
rename gate: UNVERIFIED — could not read visibility for /tmp/sentinel-r5-base (auth? network?).
```

precheck_rc=0. `./scripts/test.sh --gate` was then allowed to run to
completion on that clone. Result: **FAIL** of the REQUIRED assertion
(the hole is that the gate **passes**). See "R5-5 completion".

## V-6 rows — baseline `1ae684c`

Every COUNT / GLOBAL / SYSTEM / HOME / XDG row: potency control PASS
(unpinned listing showed the plant; consumer blocked it when visible),
exploit control PASS (unpinned listing omitted the plant after injection),
REQUIRED **FAIL** (baseline consumer missed the plant, rc=0).

| Case | Control fired? | Actual |
|---|---|---|
| V6-COUNT-secrets | yes | **FAIL** — `secret guard: clean` |
| V6-COUNT-vendor | yes | **FAIL** — mechanical conditions pass; plant not named |
| V6-GLOBAL-secrets | yes | **FAIL** |
| V6-GLOBAL-vendor | yes | **FAIL** |
| V6-SYSTEM-secrets | yes | **FAIL** |
| V6-SYSTEM-vendor | yes | **FAIL** |
| V6-NOSYSTEM-secrets | **no** — `GIT_CONFIG_NOSYSTEM=1` did not hide the plant | **NOT_MEASURED** (not counted) |
| V6-NOSYSTEM-vendor | **no** — same | **NOT_MEASURED** (not counted) |
| V6-HOME-secrets | yes | **FAIL** |
| V6-HOME-vendor | yes | **FAIL** |
| V6-XDG-secrets | yes | **FAIL** |
| V6-XDG-vendor | yes | **FAIL** |

COUNT secrets excerpt:

- ls-before: `scratch-d072-secret.env`
- ls-after: empty
- potency: `BLOCKED scratch-d072-secret.env — credential-shaped content`
- observe: `secret guard: clean`

Vendor observe excerpt (plant hidden, scanner reports clean):

```
  ok    no artifact claims an executed or emulated vendor comparison
  ok    no named vendor appears in any measurement artifact
vendor honesty: mechanical conditions pass
```

## R2 — baseline `1ae684c`

| Case | Control fired? | Actual | Log |
|---|---|---|---|
| R2-vendor | yes — unquoted listing octal-escapes café (`"caf\303\251-d072.md"`); `[ -f ]` false; ASCII sibling usable; ASCII-only plant blocked | **FAIL** — café-only plant, vendor-honesty clean | `logs/r2-unquoted.ls.txt`, `logs/r2-vendor.log` |
| R2-secrets | `-z` listing still contains the raw café path | **NOT_MEASURED** — R2 not claimed against secrets | `logs/r2-z.ls.bin` |

Unquoted listing:

```
cafe-d072.md
"caf\303\251-d072.md"
```

## Rows not counted

- V6-NOSYSTEM-secrets, V6-NOSYSTEM-vendor — exploit control did not hide.
- R2-secrets — `-z` did not drop the path.
- No REQUIRED row PASSed at a baseline where FAIL was required. No test
  was judged invalid. No replacement was made.

## R5-5 completion

Instrument: `./scripts/test.sh --gate` on `/tmp/d071-gate-unverified`
(origin `/tmp/sentinel-r5-base`, HEAD `558d001546b55bd80156bc875cf080fef0e301eb`).
Allowed to finish. Not killed early. Not replaced by a script-only
rename-gate result.

**Control (fired):** immediately before the gate, the same clone's
`scripts/check-rename-gate.sh --gate` printed UNVERIFIED and exited 0
(`logs/r5-5-precheck.log`).

```
rename gate: UNVERIFIED — could not read visibility for /tmp/sentinel-r5-base (auth? network?).
  D-016 still blocks publication. Verify manually before any public action.
```

**First attempt (not the observation):** without `ts/node_modules`, the
body printed `GATE FAILED` and the supervisor printed
`GATE DID NOT REACH COMPLETION`. Elapsed ~838s.
Log: `logs/r5-5-gate-incomplete-no-node-modules.log`. That run cannot
show the hole (the hole is `GATE PASSED`). It is kept only as the
reason `npm --prefix ts ci` was run **in the clone**.

**Completing run (the observation):** `npm --prefix ts ci` in that
clone only (`ts/package-lock.json` at the R5 parent matched HEAD by
shasum). Then:

```
(cd /tmp/d071-gate-unverified && /usr/bin/time -p ./scripts/test.sh --gate)
```

Measured output (`logs/r5-5-gate.log`):

- line 68: `rename gate: UNVERIFIED — could not read visibility for /tmp/sentinel-r5-base (auth? network?).`
- later stages still ran (labelling freeze, foundry, typescript 550, corpus, D-010)
- line 1054: standalone `GATE PASSED`
- `gate_rc=0`
- `real 1269.37`

REQUIRED assertion: no `GATE PASSED`, non-zero exit.
**Actual: FAIL** (`GATE PASSED` present, exit 0) at the R5 parent.

Exact UNVERIFIED-producing commands for this row:

```
git worktree add /tmp/sentinel-r5-base --detach 558d001546b55bd80156bc875cf080fef0e301eb
git clone --local --no-hardlinks /tmp/sentinel-r5-base /tmp/d071-gate-unverified
git -C /tmp/d071-gate-unverified remote get-url origin
# /tmp/sentinel-r5-base
git -C /tmp/d071-gate-unverified rev-parse HEAD
# 558d001546b55bd80156bc875cf080fef0e301eb
/tmp/d071-gate-unverified/scripts/check-rename-gate.sh --gate
npm --prefix ts ci   # inside /tmp/d071-gate-unverified only
(cd /tmp/d071-gate-unverified && ./scripts/test.sh --gate)
```
