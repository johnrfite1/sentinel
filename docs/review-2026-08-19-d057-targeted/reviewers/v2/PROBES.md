# V2 — PROBES

Every command run against `c8d15a76425544148d7da2f8fa0c003feb6ad2b7`, including the dead and
failed ones. `<WORKTREE>` is the V2 worktree root; `<SCRATCH>` is a session scratch directory
outside both trees. All probes were run from `<WORKTREE>` unless stated.

---

## 0. Preconditions

| # | Command | Material output |
|---|---|---|
| 0.1 | `git rev-parse HEAD` | `c8d15a76425544148d7da2f8fa0c003feb6ad2b7` — matches the frozen SHA |
| 0.2 | `git status --porcelain` | `?? ts/node_modules` only |
| 0.3 | `/usr/bin/env bash --version` | `GNU bash, version 3.2.57(1)-release (arm64-apple-darwin25)` — this is what `#!/usr/bin/env bash` resolves to, so all scripts under test ran on bash 3.2 |
| 0.4 | `git rev-parse HEAD` (re-run after last probe) | unchanged; `git status --porcelain` still only `?? ts/node_modules` |

---

## 1. DEAD AND FAILED PROBES — recorded first, because three of them silently returned "no hits"

The brief's second trap is "a dead probe's silence reads exactly like a pass". Three of my early
sweeps returned zero hits for three different mechanical reasons, and any one of them would have
produced a false HOLD on `R4-F4`.

| # | Command | What went wrong | How caught |
|---|---|---|---|
| D.1 | `grep -nE "...527..." $LIVE` | `grep` in this shell is a **function wrapping `ugrep`**, and it also passes `--ignore-files` (honours `.gitignore`). Output was a single "No such file or directory" naming the whole newline-joined list. | `type grep` |
| D.2 | `xargs -a /tmp/live.txt /usr/bin/grep ...` | BSD/macOS `xargs` has **no `-a` flag**. Errored to stderr, which I had redirected to `/dev/null`. Returned zero hits, looking exactly like "clean". | control probe C.1 below returned zero hits for a pattern that must match |
| D.3 | `/usr/bin/grep -nE "..." $L` where `L=$(cat live.txt)` | **`IFS` in this shell does not contain newline**, so the unquoted variable did not word-split into filenames. | same control |
| D.4 | `for s in ...; do timeout 90 ./scripts/$s.sh; done` | macOS has **no `timeout`**. All twelve reported `rc=127 command not found`. | read the output rather than the exit codes |
| D.5 | `mapfile -t LIVE < <(...)` in a helper script | bash 3.2 has **no `mapfile`**. | script aborted with `mapfile: command not found` |
| D.6 | `git diff --name-only ... \| cat -A` | macOS `cat` has no `-A`. | `usage: cat [-belnstuv]` |
| D.7 | **Hypothesis probe, disproved:** a tracked `docs/note[1].md` will pass `assign()` but fail `git ls-files --error-unmatch` because `[1]` is pathspec glob syntax | git matched the path **literally**; `--error-unmatch` returned 0. The predicted route into the line-198 defect does not exist. | see 3.6 |

**Controls that proved the machinery before any conclusion was drawn from a zero-hit result:**

| # | Command | Output |
|---|---|---|
| C.1 | `/usr/bin/grep -c "" <16 live files>` | a line count for each of the 16 — machinery live |
| C.2 | `<SCRATCH>/sweep.sh "Sentinel" live` | real hits + `[sweep rc=0 files=16 set=live]` |
| C.3 | `<SCRATCH>/sweep.sh --selftest` | `LIVE files: 16   FROZEN files: 52` |

---

## 2. `V3-N1` — the stub

`<SCRATCH>/stub/git` execs `/usr/bin/git` for everything except the one call selected by
`GIT_STUB_MODE`. Modes: `passthru`, `lsfiles_fail`, `lsfiles_empty`, `errorunmatch_fail`,
`toplevel_fail`, `diff_fail`.

**Stub transparency check (mandatory before trusting any refusal):**

```
$ PATH="<SCRATCH>/stub:$PATH" GIT_STUB_MODE=passthru git rev-parse HEAD
c8d15a76425544148d7da2f8fa0c003feb6ad2b7
$ /usr/bin/git rev-parse HEAD
c8d15a76425544148d7da2f8fa0c003feb6ad2b7
STUB PASSTHRU OK
```

---

## 3. `V3-N1` — probe results

### P-C1 — control, no stub at all

```
$ ./scripts/check-review-scope.sh
review scope: R1=241  R2=46  R3=151  (assigned 438 of 438 tracked files)
  remediation surface: 48 file(s) changed since A-070's parent, all assigned
  preservation-only:   79 file(s) (round-six record; faithfully preserved with
                       disclosed path sanitization, no behaviour)
  reviewer 4 is unassigned BY DESIGN (D-056(d)) and ranges over every surface above
rc=0
```

### P-C2 — control, stub on PATH in passthru mode

```
$ PATH="<SCRATCH>/stub:$PATH" GIT_STUB_MODE=passthru ./scripts/check-review-scope.sh
review scope: R1=241  R2=46  R3=151  (assigned 438 of 438 tracked files)
  remediation surface: 48 file(s) changed since A-070's parent, all assigned
  preservation-only:   79 file(s) (round-six record; faithfully preserved with
                       disclosed path sanitization, no behaviour)
  reviewer 4 is unassigned BY DESIGN (D-056(d)) and ranges over every surface above
rc=0
```

Byte-identical to P-C1. The shim is transparent.

### P1 — `git ls-files` fails (BRIEF-V2 item 1)

```
$ PATH="<SCRATCH>/stub:$PATH" GIT_STUB_MODE=lsfiles_fail ./scripts/check-review-scope.sh
  FAIL  git ls-files failed:
    fatal: stub: ls-files refused (index unreadable)
    Refusing to report a partition measured against nothing.
rc=1
```

### P2 — `git ls-files` returns empty with exit 0 (BRIEF-V2 item 2, the dangerous case)

```
$ PATH="<SCRATCH>/stub:$PATH" GIT_STUB_MODE=lsfiles_empty ./scripts/check-review-scope.sh
  FAIL  git ls-files returned NO tracked files.
    A repository with nothing in it is not a repository whose every file is assigned.
rc=1
```

Stub exit status here is **0**, so this refusal came from the `[ -z "$tracked" ]` guard and not
from the failure guard — the two guards are genuinely independent (COMMON-BRIEF trap 4).

### P3 — only `git ls-files --error-unmatch` fails (line 198) — **THE FAILURE**

```
$ PATH="<SCRATCH>/stub:$PATH" GIT_STUB_MODE=errorunmatch_fail ./scripts/check-review-scope.sh
review scope: R1=241  R2=46  R3=151  (assigned 438 of 438 tracked files)
  remediation surface: 0 file(s) changed since A-070's parent, all assigned
  reviewer 4 is unassigned BY DESIGN (D-056(d)) and ranges over every surface above
rc=0
```

Paired control, same stub, sabotage off: `remediation surface: 48 file(s) ...`

**What moved:** 48 -> 0, and the `preservation-only: 79 file(s)` line vanished. Not a dead probe.

### P4 — `git rev-parse --show-toplevel` fails (line 47)

**4a, from the repo root:**

```
$ PATH="<SCRATCH>/stub:$PATH" GIT_STUB_MODE=toplevel_fail ./scripts/check-review-scope.sh
fatal: stub: not a git repository
review scope: R1=241  R2=46  R3=151  (assigned 438 of 438 tracked files)
  remediation surface: 48 file(s) changed since A-070's parent, all assigned
  ...
```

`cd ""` is a successful no-op in bash; the run succeeds because the cwd already happened to be
correct. The only trace of the failure is a stray `fatal:` on stderr.

**4b, from `contracts/`:**

```
$ cd contracts && PATH="<SCRATCH>/stub:$PATH" GIT_STUB_MODE=toplevel_fail ../scripts/check-review-scope.sh
fatal: stub: not a git repository
review scope: R1=0  R2=0  R3=0  (assigned 0 of 13 tracked files)
  FAIL  13 tracked file(s) assigned to NO reviewer:
    foundry.toml
    lib/forge-std
    lib/openzeppelin-contracts
    src/SentinelVault.sol
    src/demo/DemoERC20.sol
rc=1
```

Fails closed, but the diagnostic is false — those files *are* assigned, under their real
repo-relative paths.

**4c, control — same subdirectory, no stub:**

```
$ cd contracts && ../scripts/check-review-scope.sh
review scope: R1=241  R2=46  R3=151  (assigned 438 of 438 tracked files)
rc=0
```

### P5 — the base label

```
$ SENTINEL_SCOPE_BASE=a89c255d8836f6ad3056fbe50970c5f00655a592 ./scripts/check-review-scope.sh
  remediation surface: 46 file(s) changed since a89c255d8836f6ad3056fbe50970c5f00655a592, all assigned

$ ./scripts/check-review-scope.sh                       # control
  remediation surface: 48 file(s) changed since A-070's parent, all assigned
```

### P5b — is the pinned default really A-070's parent?

```
$ git log -1 --format='%H%n  subject: %s' 140c59e5aa8feab72831534886fda4048cff8fe7
140c59e5aa8feab72831534886fda4048cff8fe7
  subject: session-state and the round-six brief, rewritten for a fresh instance

$ git rev-list --all --children | grep ^140c59e5aa8feab72831534886fda4048cff8fe7
140c59e5aa8feab72831534886fda4048cff8fe7 a89c255d8836f6ad3056fbe50970c5f00655a592

$ git log --oneline --all --grep=A-070
8990255 A-078: the D-057(5) reverification — three of my repairs returned as failed
7e0ab7f Pre-review provenance checkpoint: preserve and curate round six
f3c1820 Pre-review administration: scope manifest, and the deferred process-name residual
a89c255 A-070: the first remediation under the D-052(b) repair protocol
```

Sole child of the pinned base is `a89c255` = A-070. Label correct.

### P6 — unresolvable base

```
$ SENTINEL_SCOPE_BASE=deadbeefdeadbeefdeadbeefdeadbeefdeadbeef ./scripts/check-review-scope.sh
review scope: R1=241  R2=46  R3=151  (assigned 438 of 438 tracked files)
  FAIL  scope base 'deadbeefdeadbeefdeadbeefdeadbeefdeadbeef' does not resolve to a commit.
    Refusing to print a remediation surface measured against nothing. A base that
    cannot be resolved is not an empty diff.
rc=1
```

### P7 — base resolves, diff legitimately empty

```
$ SENTINEL_SCOPE_BASE=HEAD ./scripts/check-review-scope.sh
review scope: R1=241  R2=46  R3=151  (assigned 438 of 438 tracked files)
  remediation surface: 0 file(s) changed since HEAD, all assigned
rc=0
```

Correct behaviour (a real measurement of a real empty diff, correctly labelled), recorded as
residual R-3 only because it prints the same sentence as the defect.

### P10 — `git diff` fails (line 168 guard)

```
$ PATH="<SCRATCH>/stub:$PATH" GIT_STUB_MODE=diff_fail ./scripts/check-review-scope.sh
review scope: R1=241  R2=46  R3=151  (assigned 438 of 438 tracked files)
  FAIL  git diff against '140c59e5aa8feab72831534886fda4048cff8fe7' failed:
    fatal: stub: diff refused
rc=1
```

### 3.6 — non-shim reachability of the line-198 defect

**Quoted paths, in a throwaway repo, no shim (LATENT POSITIVE):**

```
$ git diff --name-only HEAD~1..HEAD | while IFS= read -r f; do
    git ls-files --error-unmatch "$f" >/dev/null 2>&1 && echo "OK      : $f" || echo "SKIPPED : $f"
  done
SKIPPED : "caf\303\251.md"   <-- silently dropped from the surface
OK      : plain.md
```

**Glob metacharacters (DEAD PROBE — hypothesis disproved):**

```
$ git ls-files --error-unmatch 'docs/note[1].md'
docs/note[1].md          # exit 0 — git matched literally, no defect via this route
```

**Submodule gitlinks (negative):**

```
$ git ls-files --error-unmatch contracts/lib/forge-std           -> rc=0  OK
$ git ls-files --error-unmatch contracts/lib/openzeppelin-contracts -> rc=0  OK
```

**Is the quoted-path route live in this repository today?**

```
$ git ls-files | grep -c '^"'
0
```

No. The route is latent.

### 3.7 — sibling enumeration

```
$ awk '!/^[[:space:]]*#/ && /git |wc |tr |printf |sed |awk |cat |grep |cut /{printf "%4d: %s\n", NR, $0}' \
      scripts/check-review-scope.sh
  47: cd "$(git rev-parse --show-toplevel)"
 106: tracked="$(git ls-files 2>&1)"
 108:     echo "  FAIL  git ls-files failed:"
 109:     printf '    %s\n' "$tracked"
 114:     echo "  FAIL  git ls-files returned NO tracked files."
 131: echo "review scope: ... (assigned $total of $(printf '%s\n' "$tracked" | wc -l | tr -d ' ') tracked files)"
 135:     printf '    %s\n' "${unassigned[@]}"
 161: if ! git rev-parse --verify --quiet "${since}^{commit}" >/dev/null; then
 168: scope_diff="$(git diff --name-only "$since"..HEAD 2>&1)"
 170:     echo "  FAIL  git diff against '$since' failed:"
 171:     printf '    %s\n' "$scope_diff"
 198:     git ls-files --error-unmatch "$f" >/dev/null 2>&1 || continue   # deleted since; not in scope
 214:     echo "                       disclosed path sanitization, no behaviour)"
```

---

## 4. `R4-F4` — probe results

### 4.1 The single source

```
$ grep -nE "^(FOUNDRY_MIN_TESTS|TS_MIN_TESTS|VERIFIER_MIN_TESTS|VERIFIER_MIN_SAMPLES|VERIFIER_MIN_TAMPER|VERIFIER_MIN_TAMPER_MODES)=" scripts/test.sh
234:FOUNDRY_MIN_TESTS=92
235:TS_MIN_TESTS=527
658:VERIFIER_MIN_TESTS=209
659:VERIFIER_MIN_SAMPLES=7
660:VERIFIER_MIN_TAMPER=78
673:VERIFIER_MIN_TAMPER_MODES=30

$ grep -nE "^[A-Z_]+MIN[A-Z_]*=" scripts/test.sh
(the same six lines, no duplicate definitions)

$ ./scripts/check-suite-floors.sh
  FOUNDRY_MIN_TESTS          92
  TS_MIN_TESTS               527
  VERIFIER_MIN_TESTS         209
  VERIFIER_MIN_SAMPLES       7
  VERIFIER_MIN_TAMPER        78
  VERIFIER_MIN_TAMPER_MODES  30
suite floors: read from scripts/test.sh, which is the only copy.
```

### 4.2 Who invokes the floor reader?

```
$ git ls-files | while read f; do grep -q "check-suite-floors" "$f" && echo "HIT: $f"; done
HIT: docs/decisions.md        (line 247, prose)
HIT: docs/session-state.md    (lines 77, 221, 228, prose)

$ grep -n "check-suite-floors" scripts/test.sh
NOT WIRED into scripts/test.sh
```

Nothing executes it.

### 4.3 Surface classification

```
$ git ls-files '*.md' | wc -l                                    -> 68
$ git ls-files '*.md' | grep -vc '^docs/review-2026-08-1'        -> 16   (LIVE, swept)
$ git ls-files '*.md' | grep  -c '^docs/review-2026-08-1'        -> 52   (FROZEN, excluded by rule)
```

### 4.4 The sweep (reads floors from the source, hardcodes nothing)

`<SCRATCH>/floorsweep.sh` — material hits, unmutated:

```
SOURCE OF TRUTH (scripts/test.sh via check-suite-floors.sh):
  foundry=92 ts=527 verifier=209 samples=7 tamper=78 modes=30

== samples  (source says 7) ==
docs/session-state.md:351:7 samples          <-- present tense, live
docs/round-six-brief.md:28:7 samples         <-- historical frame (control)
docs/decisions.md:{87,178,180,181,184,195,197}   <-- dated entries
docs/gate-s2-evidence.md:795  docs/v1-1-register.md:{190,348}  verifier/REPORT.md:1212

== tamper   (source says 78) ==
docs/session-state.md:351:78 tamper cases    <-- present tense, live
docs/decisions.md:219:78 tamper cases        <-- dated entry
docs/decisions.md:{178,180,195}  docs/session-state.md:456  verifier/REPORT.md:{1173,1210}

== foundry  (source says 92) ==
docs/decisions.md:246:92 Foundry             <-- newest decision entry (residual R-6)
docs/round-six-brief.md:28:75/75 Foundry     <-- stale but historically framed (control)
docs/gate-s1-evidence.md:21:43/43 Foundry    docs/gate-s2-evidence.md:942:66/66 Foundry

== ts       (source says 527) ==
docs/decisions.md:246:527 TypeScript         <-- newest decision entry
docs/session-state.md:343:507/507 TypeScript <-- narrating the original defect, past tense (control)
docs/round-six-brief.md:28:481/481 TypeScript

== verifier (source says 209) ==
docs/decisions.md:{243,245,246}:209 verifier
docs/session-state.md:343:198/198 verifier   <-- narrating the original defect (control)
docs/round-six-brief.md:28:180/180 verifier
```

**Sweep limitation, recorded as residual R-4:** the `30 modes` duplicate at
`docs/session-state.md:351-352` is split across a hard wrap (`...over 30` / `modes ...`) and
matched **no** regex. It was found by reading lines 339-362 directly.

### 4.5 Falsification — mutate a real floor

```
$ cp scripts/test.sh <SCRATCH>/test.sh.orig
$ sed -i '' 's/^VERIFIER_MIN_TAMPER=78$/VERIFIER_MIN_TAMPER=80/' scripts/test.sh
$ grep -n "^VERIFIER_MIN_TAMPER=" scripts/test.sh
660:VERIFIER_MIN_TAMPER=80

(a) $ ./scripts/check-suite-floors.sh
      VERIFIER_MIN_TAMPER        80          <-- single source reflects it

(b) $ <SCRATCH>/floorsweep.sh
    == tamper   (source says 80) ==
    docs/session-state.md:351:78 tamper cases    <-- live doc now DISAGREES; sweep catches it
```

### 4.6 Does any guard catch the disagreement? (floor still mutated to 80)

```
check-class-coverage       rc=0 | corpus class coverage: pass on the ratchet; carried classes listed above
check-eval-codes           rc=0 | eval codes: 41/41 engine checks documented in §5.7.1 (D-031)
check-findings-ledger      rc=0 |   all totals match D-057(1) as ruled
check-gate-immutability    rc=0 |   · a subject invoked by a running gate still protects itself
check-label-integrity      rc=0 | label integrity: 20 labelling artifact(s) pinned, none unpinned (A-064)
check-label-prompt         rc=0 | label prompt: frozen (02145d7b4f83d8c8…, D-011a)
check-rename-gate          rc=0 | rename gate: clean (johnrfite1/sentinel is private; D-016 …)
check-review-scope         rc=0 |   reviewer 4 is unassigned BY DESIGN (D-056(d)) …
check-secrets              rc=0 | secret guard: clean
check-suite-floors         rc=0 | suite floors: read from scripts/test.sh, which is the only copy.
check-type-strings         rc=0 | type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)
check-vendor-honesty       rc=0 | vendor honesty: mechanical conditions pass; D-008(1) met …
```

Twelve green with a document disagreeing with the source it claims to be bound to.

### 4.7 Revert and control

```
$ cp <SCRATCH>/test.sh.orig scripts/test.sh
$ git diff --stat -- scripts/test.sh          (empty)
$ git status --porcelain -- scripts/test.sh   (empty)
$ grep -n "^VERIFIER_MIN_TAMPER=" scripts/test.sh
660:VERIFIER_MIN_TAMPER=78
$ ./scripts/check-suite-floors.sh | grep TAMPER
  VERIFIER_MIN_TAMPER        78
  VERIFIER_MIN_TAMPER_MODES  30
```

### 4.8 Direct read of the defect site

```
$ sed -n '339,362p' docs/session-state.md
```

Full text quoted in REPORT.md 2.2. The operative lines are 346-347 ("The figures are no longer
duplicated here. The gate constants are the only copy"), 351-352 ("What is stable and worth
stating: 50 corpus fixtures · 7 samples · 78 tamper cases over 30 modes ..."), and 360 ("THE
FLOOR VALUES ARE DELIBERATELY NOT REPRINTED HERE").
