# A1 — PROBES

Every probe run while authoring the A1 tests, with its material output, **including the ones that
died, the ones that measured nothing, and the one that changed state it should not have.**

**Path convention.** `<WORKTREE>` is the A1 review worktree, `<SENTINEL>` the primary tree,
`<SCRATCH>` a session scratch directory, `<TMP>` a `mktemp -d` under `TMPDIR`. No absolute machine
path appears in this directory by design.

**Credential fixtures** are described, never pasted. Each is one line of the form
`export const signerKey = "0x<64 hex>";` where the 64 hex digits are a single hex character
repeated — obviously fake, assembled at run time, never present as a literal in any file written
here. Every fixture lived in `<TMP>` or in a throwaway clone and was removed.

---

## 0. Instrument checks, run before anything was believed

```
$ printf 'CANARY_A1_MARKER\n' > <SCRATCH>/canary.txt
$ /usr/bin/grep -c CANARY_A1_MARKER <SCRATCH>/canary.txt
1
$ grep -c CANARY_A1_MARKER <SCRATCH>/canary.txt          # the shell's wrapper
1
```

Both found the canary today, so no divergence was observed on this workstation. The harness still
uses `/usr/bin/grep` throughout: the wrapper honours `--ignore-files` and the failure it produces
is a clean-looking zero, which is unrecoverable once trusted.

```
$ env bash --version | head -1
GNU bash, version 3.2.57(1)-release (arm64-apple-darwin25)
```

The harness is therefore written to bash 3.2 (no `mapfile`, no associative arrays).

```
$ git -C <WORKTREE> rev-parse HEAD
f68d4d804de4d3b631e25fd539deecda5409f0d7
$ git -C <SENTINEL> rev-parse HEAD
f68d4d804de4d3b631e25fd539deecda5409f0d7
```

---

## 1. The boundary — 16 entry points, by file, shebang and ownership

```
$ git ls-files 'scripts/*' '.githooks/*' | wc -l
16
```

Root-resolution idiom in each (`/usr/bin/grep -nE 'rev-parse --show-toplevel|^cd |ROOT=|repo_root='`):

| entry point | line |
|---|---|
| check-class-coverage.sh | 48 `ROOT="$(git rev-parse --show-toplevel)"` · 49 `cd "$ROOT"` |
| check-eval-codes.sh | 21 `ROOT="$(git rev-parse --show-toplevel)"` |
| check-findings-ledger.sh | 22 `cd "$(git rev-parse --show-toplevel)"` |
| check-gate-immutability.sh | 43 `ROOT="$(git rev-parse --show-toplevel)"` |
| check-label-integrity.sh | 32 `ROOT=…` |
| check-label-prompt.sh | 18 `ROOT=…` |
| **check-rename-gate.sh** | **none — reads `git config --get remote.origin.url` in the caller's CWD** |
| check-review-scope.sh | 47 `cd "$(git rev-parse --show-toplevel)"` |
| **check-secrets.sh** | **none — runs `git ls-files` / `git diff --cached` in the caller's CWD** |
| check-suite-floors.sh | 13 `cd "$(git rev-parse --show-toplevel)"` |
| check-type-strings.sh | 18 `ROOT=…` |
| check-vendor-honesty.sh | 32 `ROOT=…` · 33 `cd "$ROOT"` |
| install-hooks.sh | 5 `cd "$(git rev-parse --show-toplevel)"` |
| mutate.sh | 33 `ROOT=…` |
| test.sh | 161 `cd "$(git rev-parse --show-toplevel)"` |
| .githooks/pre-commit | 4 `repo_root=$(git rev-parse --show-toplevel)` |

**Two of the sixteen resolve no root at all.** They are the two that fail open in cases 2 and 4.
This is why the card's "enumerate by file, shebang and ownership" matters: a sweep for the
`rev-parse --show-toplevel` idiom would have found 14 and missed exactly the two that misbehave
worst.

---

## 2. Case 1 — from the repository root

```
$ for s in <the 12 executable checkers>; do bash "scripts/$s.sh"; done
check-class-coverage.sh    rc=0
check-eval-codes.sh        rc=0   eval codes: 41/41 engine checks documented in §5.7.1 (D-031)
check-findings-ledger.sh   rc=0
check-gate-immutability.sh rc=0
check-label-integrity.sh   rc=0   label integrity: 20 labelling artifact(s) pinned, none unpinned
check-label-prompt.sh      rc=0
check-rename-gate.sh       rc=0
check-review-scope.sh      rc=0   review scope: R1=280  R2=46  R3=151  (assigned 477 of 477 tracked files)
                                    remediation surface: 87 file(s) changed since A-070's parent, all assigned
check-secrets.sh           rc=0   secret guard: clean
check-suite-floors.sh      rc=0
check-type-strings.sh      rc=0
check-vendor-honesty.sh    rc=0
$ bash .githooks/pre-commit
secret guard: clean            rc=0
```

Determinism, because cases 2 and 3 assert byte-identical output:

```
$ for s in <the 12>; do a=$(bash "scripts/$s.sh" 2>&1); b=$(bash "scripts/$s.sh" 2>&1); …
all 12: DETERMINISTIC
```

---

## 3. Case 2 — an unrelated (non-repository) directory

```
$ ( cd <SCRATCH>/plain && git rev-parse --show-toplevel )
fatal: not a git repository (or any of the parent directories): .git   rc=128

$ ( cd <SCRATCH>/plain && bash <WORKTREE>/scripts/check-secrets.sh )
fatal: not a git repository (or any of the parent directories): .git
fatal: not a git repository (or any of the parent directories): .git
secret guard: clean
rc=0

$ ( cd <SCRATCH>/plain && bash <WORKTREE>/scripts/check-review-scope.sh )
  FAIL  git ls-files failed: … Refusing to report a partition measured against nothing.
rc=1

$ ( cd <SCRATCH>/plain && bash <WORKTREE>/scripts/check-rename-gate.sh )
rename gate: no remote configured — nothing can be public
rc=0
```

Full sweep of all 12 from the non-repository directory: **10 exit 1** (`fatal: not a git
repository` reaching the caller), **2 exit 0** with a clean summary — `check-secrets.sh` and
`check-rename-gate.sh`.

What this probe MOVED: nothing. All twelve are read-only; `git status --porcelain` in the worktree
was unchanged before and after.

---

## 4. Case 3 — inside a foreign git repository

The decoy is created by the probe, never a repository that already existed:

```
$ git -c init.defaultBranch=main init -q <SCRATCH>/decoy
$ … 2 tracked files (README.md, scripts/thing.sh), a decoy github remote …
```

```
$ ( cd <SCRATCH>/decoy && bash <WORKTREE>/scripts/check-review-scope.sh )
review scope: R1=2  R2=0  R3=0  (assigned 2 of 2 tracked files)
  FAIL  scope base '140c59e5aa8feab72831534886fda4048cff8fe7' does not resolve to a commit.
rc=1
```

The partition line is already a report about the wrong repository. Sharpened, with the documented
override pointed at the decoy's own HEAD, it becomes a **fully clean exit-0** report:

```
$ ( cd <SCRATCH>/decoy && SENTINEL_SCOPE_BASE=<decoy HEAD> bash <WORKTREE>/scripts/check-review-scope.sh )
review scope: R1=2  R2=0  R3=0  (assigned 2 of 2 tracked files)
  remediation surface: 0 file(s) changed since <decoy HEAD>, all assigned
  reviewer 4 is unassigned BY DESIGN (D-056(d)) and ranges over every surface above
rc=0
```

```
$ ( cd <SCRATCH>/decoy && bash <WORKTREE>/scripts/check-rename-gate.sh )
rename gate: UNVERIFIED — could not read visibility for a-different-owner/a-different-repo (auth? network?).
rc=0
```

The credential probe, which is the one with teeth:

```
$ <plant one fake-credential file in the Sentinel worktree>
$ ( cd <WORKTREE>       && bash <WORKTREE>/scripts/check-secrets.sh )   # control
BLOCKED planted-ascii.ts — credential-shaped content:
    1:signerKey = "0x<64 hex>"
secret guard: 1 finding(s). …                                             rc=1
$ ( cd <SCRATCH>/decoy  && bash <WORKTREE>/scripts/check-secrets.sh )   # probe
secret guard: clean                                                       rc=0
$ <remove the planted file>
```

What this probe MOVED: one untracked file in the worktree for the duration, removed immediately;
`git status --porcelain` verified clean afterwards. The decoy repository is scratch.

---

## 5. Cases 5 and 6 — a git shim

A `git` wrapper first on `PATH`, delegating to the real `git` except for one named failure. Its
pass-through is asserted before use (harness preflight P4), because a shim that did not pass
through would make every shimmed result meaningless.

```
$ PATH=<shim>:$PATH A1_SHIM_MODE=none git rev-parse --short HEAD
f68d4d8                                    # pass-through confirmed
```

```
# CASE 5 — ls-files exits 3
$ … A1_SHIM_MODE=lsfiles-fail bash scripts/check-secrets.sh
a1-shim: simulated ls-files failure
a1-shim: simulated ls-files failure
secret guard: clean                        rc=0     <-- fail-open
$ … A1_SHIM_MODE=lsfiles-fail bash scripts/check-review-scope.sh
  FAIL  git ls-files failed: … Refusing to report a partition measured against nothing.
                                           rc=1     <-- guarded sibling refuses (control)

# CASE 6 — ls-files exits 0 with no output
$ … A1_SHIM_MODE=lsfiles-empty bash scripts/check-secrets.sh
secret guard: clean                        rc=0     <-- fail-open
$ … A1_SHIM_MODE=lsfiles-empty bash scripts/check-review-scope.sh
  FAIL  git ls-files returned NO tracked files. …
                                           rc=1     <-- guarded sibling refuses (control)
```

The `V3-N1` route, which leaves the guarded branch above untouched by failing only
`--error-unmatch`:

```
$ bash scripts/check-review-scope.sh                                   # unmutated
review scope: R1=280  R2=46  R3=151  (assigned 477 of 477 tracked files)
  remediation surface: 87 file(s) changed since A-070's parent, all assigned    rc=0
$ … A1_SHIM_MODE=errorunmatch-fail bash scripts/check-review-scope.sh  # mutated
review scope: R1=280  R2=46  R3=151  (assigned 477 of 477 tracked files)
  remediation surface: 0 file(s) changed since A-070's parent, all assigned     rc=0
```

**87 → 0, `all assigned`, exit 0.** Byte-for-byte the sentence R1-F2 was filed against.

---

## 6. Case 7 — a genuine staged deletion

Run in a throwaway clone, so nothing here touched a real repository.

```
$ git rm -q HANDOFF.md
$ git diff --cached --name-status
D	HANDOFF.md
$ git diff --cached --name-only --diff-filter=ACM | wc -l
0                                       # the deletion is never enumerated at all
$ bash scripts/check-secrets.sh --staged
secret guard: clean                     rc=0
$ bash .githooks/pre-commit
secret guard: clean                     rc=0
$ git commit -m "…"
COMMIT SUCCEEDED
```

The `ACM` filter is why this is safe today, and it is why "refuse on any git failure" would break
it: such a repair would have to enumerate deletions before it could refuse on them.

---

## 7. Cases 8 and 9

```
$ cmp -s a1probe-ascii.ts 'a1probe-café.ts' && echo YES
YES                                     # byte-identical
$ shasum a1probe-ascii.ts 'a1probe-café.ts'
e2ddd524…  a1probe-ascii.ts
e2ddd524…  a1probe-café.ts

# STAGED
$ git add a1probe-ascii.ts ; git diff --cached --name-only --diff-filter=ACM
a1probe-ascii.ts
$ bash scripts/check-secrets.sh --staged
BLOCKED a1probe-ascii.ts — credential-shaped content: …                 rc=1

$ git add 'a1probe-café.ts' ; git diff --cached --name-only --diff-filter=ACM
"a1probe-caf\303\251.ts"
$ git diff --cached --raw -z | tr '\0' '\n'
:000000 100644 0000000 a83f376 A
a1probe-café.ts
$ bash scripts/check-secrets.sh --staged
secret guard: clean                                                     rc=0

# DEFAULT, untracked
$ git ls-files --others --exclude-standard | /usr/bin/grep a1probe
a1probe-ascii.ts
"a1probe-caf\303\251.ts"
$ git ls-files --others --exclude-standard -z | tr '\0' '\n' | /usr/bin/grep a1probe
a1probe-ascii.ts
a1probe-café.ts
   only ASCII present  -> rc=1 (BLOCKED)
   only accented present -> rc=0 (clean)

# DEFAULT, tracked — identical asymmetry
$ git ls-files | /usr/bin/grep a1probe
a1probe-ascii.ts
"a1probe-caf\303\251.ts"
```

```
$ git config --get core.quotePath
(unset — default true)
```

---

## 8. Case 10 — default-mode fail-closed, by a route that is not case 9

```
$ <commit a fake-credential file>            ; bash scripts/check-secrets.sh   -> rc=1 BLOCKED
$ rm -f a1probe-idx.ts                       # removed from the tree, NOT staged
$ git ls-files | /usr/bin/grep -c a1probe-idx
1                                            # still enumerated
$ git show ":a1probe-idx.ts" | /usr/bin/grep -c signerKey
1                                            # the index still holds the credential
$ git ls-files --deleted
a1probe-idx.ts                               # and git can say exactly why it is absent
$ bash scripts/check-secrets.sh
secret guard: clean                          rc=0
```

Census used for the default-mode discriminator question:

```
$ git ls-files -s | awk '{print $1}' | sort | uniq -c
 461 100644
  16 100755
   2 160000
$ git ls-files -s contracts/lib
160000 bf647bd6… 0	contracts/lib/forge-std
160000 5fd1781b… 0	contracts/lib/openzeppelin-contracts
$ git ls-files -z | while IFS= read -r -d '' f; do [ -f "$f" ] || echo "NOT-A-REGULAR-FILE: $f"; done
NOT-A-REGULAR-FILE: contracts/lib/forge-std
NOT-A-REGULAR-FILE: contracts/lib/openzeppelin-contracts
```

---

## 9. Case 11 — staged-mode fail-closed

```
$ <stage a fake-credential file>
$ bash scripts/check-secrets.sh --staged                       rc=1  BLOCKED   (control)
$ … A1_SHIM_MODE=show-fail bash scripts/check-secrets.sh --staged
secret guard: clean                                            rc=0            (fail-open)
```

---

## 10. Case 12 — install-hooks.sh against a foreign repository

Target is a repository this probe created, one command earlier. `install-hooks.sh` writes
`core.hooksPath`, so this is the probe that most needed that discipline.

```
$ git -c init.defaultBranch=main init -q <SCRATCH>/foreign12 …
$ git -C <SCRATCH>/foreign12 config --local --get core.hooksPath
(unset)
$ ( cd <SCRATCH>/foreign12 && bash <WORKTREE>/scripts/install-hooks.sh )
chmod: .githooks/*: No such file or directory
chmod: scripts/*.sh: No such file or directory
rc=1
$ git -C <SCRATCH>/foreign12 config --local --get core.hooksPath
.githooks                                <-- WRITTEN, and it persists
```

Control, against an isolated clone of Sentinel at the base SHA:

```
$ ( cd <clone> && bash scripts/install-hooks.sh )
hooks installed: core.hooksPath=.githooks    rc=0
```

Verified after every probe: `git -C <SENTINEL> config --local --get core.hooksPath` still returns
`.githooks`, its pre-existing value, and was never written by this work.

---

## 11. Case 13 — pre-commit under an identity mismatch

```
$ git -C <SCRATCH>/foreign13 config core.hooksPath <WORKTREE>/.githooks

# 13a — the foreign repository has no scripts/check-secrets.sh
$ ( cd <SCRATCH>/foreign13 && git commit -m 13a )
<WORKTREE>/.githooks/pre-commit: line 5: <SCRATCH>/foreign13/scripts/check-secrets.sh: No such file or directory
   commit blocked — by an exec failure against a path in the WRONG repository, not by a refusal

# 13b — the foreign repository supplies its own scripts/check-secrets.sh
$ ( cd <SCRATCH>/foreign13 && git commit -m 13b-again )
A1-DECOY-GUARD-RAN
[main 29c58cd] 13b-again
 1 file changed, 1 insertion(+)
$ git -C <SCRATCH>/foreign13 show HEAD:leak2.ts | /usr/bin/grep -c signerKey
1                                        <-- the credential landed
```

Sentinel's tracked hook executed a script belonging to a repository it does not own, and the
commit it was guarding succeeded.

---

## DEAD, FAILED AND NON-DISCRIMINATING PROBES — recorded, not discarded

**D1 — `forge build` populated the submodules. This probe MOVED state and had to be reverted.**
Checking whether case 1 could be exercised for `test.sh` and `mutate.sh`, I ran `forge build` in
`contracts/`. Foundry does not fail on missing dependencies; it **self-installs them over the
network**, cloning `forge-std` and `openzeppelin-contracts` into `contracts/lib` and leaving
` M contracts/lib/forge-std` in `git status`. Reverted by removing the two `.git` directories the
clone created and the `out`/`cache` directories; `git status --porcelain` returned to
`?? ts/node_modules` alone. **Recorded because the probe's own side effect is the finding**: at a
pinned SHA in a review worktree, the cheap-looking availability check is a state change. `test.sh`
and `mutate.sh` are not exercised at runtime as a result.

**D2 — the staged-rename route does not evade the guard. Negative result.** `--diff-filter=ACM`
excludes `R`, so a rename looked like an enumeration gap. It is not, in this invocation:

```
$ git mv a1probe-orig.ts a1probe-renamed.ts ; <append a fake credential> ; git add …
$ git diff --cached --name-status
D	a1probe-orig.ts
A	a1probe-renamed.ts
$ bash scripts/check-secrets.sh --staged
BLOCKED a1probe-renamed.ts — credential-shaped content:  …   rc=1
```

Rename detection is not applied here, so the new path surfaces as `A` and **is** scanned. No test
was written for it. Recorded so nobody re-derives it, and flagged in COVERAGE.md as
configuration-sensitive rather than proven safe.

**D3 — the harness's first run failed its own preflight, correctly.** The fixture generator was
called with a fill character that is not a hex digit, so the "credential" was not
credential-shaped and `check-secrets.sh` passed it. Preflight P5 — *the planted fixture must trip
the guard* — caught it and refused to run:

```
PREFLIGHT FAILED: the planted credential fixture does NOT trip check-secrets.sh —
                  every clean result below would be vacuous
```

Without that preflight, cases 9, 10 and 11 would all have reported `clean` and all three would
have been read as the defect. **This is the dead-probe failure mode reproducing itself inside the
test author's own instrument**, and it is the reason the generator now rejects a non-hex fill
character and the preflight is a hard stop.

**D4 — two of my own assertions were mislabelled as passes and are corrected.** Detailed in
RESULTS.md: `install-hooks.sh`'s incidental `chmod` failure was scored as a refusal, and case 13b's
flag was inverted so an executed decoy scored PASS.

**D5 — case 3's sweep does not discriminate for `check-secrets.sh`, and the harness says so.** On a
clean tree the guard prints `secret guard: clean` whichever repository it read, so its
foreign-repository output is byte-identical to its root output. The harness prints
`same output from both places (NOT evidence of agreement): check-secrets` and carries the real
discrimination in case 3a, which plants content only the Sentinel tree holds. An earlier draft
would have counted that identity as a pass.

**D6 — `PIPESTATUS` is unset in this session's interactive shell (zsh).** Several early probes read
`rc=` as empty. Re-run under `bash` with the subject's status captured directly. No conclusion was
drawn from an empty status.

---

## Isolation statement

- Everything that stages, commits, installs hooks or writes git config ran in a repository created
  by these probes (`git init` under scratch/`TMPDIR`) or in a `git clone --no-hardlinks` of the
  worktree. `install-hooks.sh` was never pointed at `<SENTINEL>` or `<WORKTREE>`.
- `<SENTINEL>`'s `core.hooksPath` was read before and after and is unchanged at `.githooks`.
- `<WORKTREE>` `git status --porcelain` at the end: `?? ts/node_modules` only, i.e. provisioning.
- The harness removes its `mktemp -d` on exit; `ls -d "$TMPDIR"/a1-repo-identity.*` finds nothing.
