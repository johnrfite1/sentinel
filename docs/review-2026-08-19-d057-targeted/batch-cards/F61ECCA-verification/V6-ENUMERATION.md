# V-6 — git environment and config injection, enumerated before any repair

A named-list patch produced this defect. This is not another named list offered as a fix. It is an inventory of **where git is invoked**, by file, shebang and ownership, and which of git's documented configuration inputs those invocations still honour.

Git version on this machine: `git version 2.50.1 (Apple Git-155)`. Sources: `git(1)` ENVIRONMENT, `git-config(1)` ENVIRONMENT, `gitignore(5)` DESCRIPTION. Not training data.

## Documented configuration inputs (from the manuals)

From `git-config(1)` ENVIRONMENT:

- `GIT_CONFIG_COUNT` / `GIT_CONFIG_KEY_<n>` / `GIT_CONFIG_VALUE_<n>` — additional config pairs, processed when COUNT is a positive number.
- `GIT_CONFIG_GLOBAL` — replacement global config file.
- `GIT_CONFIG_SYSTEM` — replacement system config file.
- `GIT_CONFIG_NOSYSTEM` — skip the system file.
- `GIT_CONFIG` — **git-config only**. The manual: *"This variable has no effect on other Git commands."*

From `git(1)` ENVIRONMENT, also: `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM`, `GIT_CONFIG_NOSYSTEM`, plus `HOME`. `GIT_CONFIG_COUNT` is **not** in `git(1)` ENVIRONMENT. A reader of `git(1)` alone misses the COUNT triple.

From `gitignore(5)`, untracked exclusion sources, high to low:

1. command-line patterns
2. `.gitignore` in the tree
3. `$GIT_DIR/info/exclude`
4. `core.excludesFile` (default `$XDG_CONFIG_HOME/git/ignore`, else `$HOME/.config/git/ignore`)

`GIT_CONFIG_PARAMETERS` does **not** appear in this git's `git(1)` or `git-config(1)` ENVIRONMENT. Not listed as a vector.

`GIT_DIR` / `GIT_WORK_TREE` / `GIT_INDEX_FILE` / `GIT_COMMON_DIR` / `GIT_PREFIX` are the 12-F2 scrub list. They redirect the repository, not `core.excludesFile`. They are already unset in production identity blocks. They are not V-6's remaining surface. `$GIT_DIR/info/exclude` is reachable only if `GIT_DIR` still points at a writable git dir; after the 12-F2 unset, that path is the real repo's `info/exclude`, which is tracked-adjacent repository state, not caller env.

## Production scrub, today, every project-owned shell guard

After identity, each bash guard `unset`s `GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX`. None unsets `GIT_CONFIG_*`, `HOME`, or `XDG_CONFIG_HOME`. None passes `env -u GIT_CONFIG_COUNT` (or GLOBAL/SYSTEM) into later git.

Identity probes themselves use `env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR` (test.sh also `-u GIT_PREFIX`). Same gap.

## Boundary

**In:** every project-owned file under `scripts/` and `.githooks/`.
**Out:** `contracts/lib/**` (vendor). Review cards under `docs/review-*` (evidence, not production).

## Per-file inventory

| File | Shebang | Ownership | Git invocations after identity | Honour GIT_CONFIG_* / HOME / XDG? | Lists untracked via `--exclude-standard`? |
|---|---|---|---|---|---|
| `scripts/check-secrets.sh` | `#!/usr/bin/env bash` | project secret guard | `_cs_git ls-files -s -z`; `git ls-files --others --exclude-standard -z`; `_cs_git diff --cached --raw -z`; `git show`; `git rev-parse --git-path index` (staged-index validation) | yes, all of them. `_cs_git` only injects `GIT_INDEX_FILE` when `--index-file` is set; it does not scrub CONFIG_* | **yes — default mode** |
| `.githooks/pre-commit` | `#!/usr/bin/env bash` | project hook | identity `git rev-parse`; `git rev-parse --git-path index`; `exec` of `check-secrets.sh --staged` | yes. Captures `GIT_INDEX_FILE` then unsets the 12-F2 five. Does not unset CONFIG_* | no (asks check-secrets `--staged`) |
| `scripts/check-vendor-honesty.sh` | `#!/usr/bin/env bash` | project Gate 5 | `artifacts()`: `git ls-files` then `git ls-files --others --exclude-standard` (**no `-z`** — that is R2) | yes | **yes — D-008(2) and D-008(4) scans** |
| `scripts/check-rename-gate.sh` | `#!/usr/bin/env bash` | project D-016 | `git config --get remote.origin.url`; then `gh` | yes, for the `git config` read | no |
| `scripts/install-hooks.sh` | `#!/usr/bin/env bash` | project | `git rev-parse` for CALLER_ROOT (before unset — inherits caller GIT_DIR); after unset, `git -C "$SENTINEL_ROOT" config core.hooksPath .githooks` | yes, the config write honours CONFIG_* on the Sentinel repo | no |
| `scripts/test.sh` | `#!/usr/bin/env bash` | project gate | supervisor: `git rev-parse --show-toplevel` with 12-F2 `-u`. Body unsets 12-F2 then runs children. No direct ls-files | children inherit remaining env | no |
| `scripts/check-findings-ledger.sh` | `#!/usr/bin/env bash` | project | none after identity; reads a path | n/a after identity | no |
| `scripts/check-suite-floors.sh` | `#!/usr/bin/env bash` | project | none after identity; reads `test.sh` and `session-state.md` | n/a | no |
| `scripts/check-class-coverage.sh` | `#!/usr/bin/env bash` | project | none after identity; reads fixtures | n/a | no |
| `scripts/check-eval-codes.sh` | `#!/usr/bin/env bash` | project | none after identity | n/a | no |
| `scripts/check-type-strings.sh` | `#!/usr/bin/env bash` | project | none after identity | n/a | no |
| `scripts/check-label-prompt.sh` | `#!/usr/bin/env bash` | project | none after identity | n/a | no |
| `scripts/check-label-integrity.sh` | `#!/usr/bin/env bash` | project | none after identity | n/a | no |
| `scripts/check-gate-immutability.sh` | `#!/usr/bin/env bash` | project | synthetic subjects; no `--others --exclude-standard` | later git, if any, would honour CONFIG_* | no |
| `scripts/check-review-scope.sh` | `#!/usr/bin/env bash` | project, not a test.sh stage | `git ls-files -z`; `git diff -z --name-only`; `git ls-files --error-unmatch` | yes | **no** — tracked / diff only |
| `scripts/mutate.sh` | `#!/usr/bin/env bash` | project | `git status --porcelain -- ts/src contracts/src` | yes | porcelain can hide untracked via excludes, but the check is "dirty tracked sources" |
| `scripts/check-v1-index-ordering.sh` | `#!/usr/bin/env bash` | project V-1 guard | **sets** `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` (and `HOME`) to isolate its clone. Then `git clone`, `git -C` config/add/commit | Redirecting GLOBAL/SYSTEM does **not** scrub `GIT_CONFIG_COUNT`. COUNT still applies on top | its clone's untracked scan is its own fixture, not a production untracked census |
| `scripts/extract-markdown-section.py` | `#!/usr/bin/env python3` | project | none | n/a | n/a |

## Reachable hide-untracked vectors (against `--others --exclude-standard`)

These do not require `GIT_DIR`:

1. **COUNT triple** → `core.excludesFile` pointing at a caller-controlled ignore file. Demonstrated against the secret guard (default mode) and against Gate 5's `artifacts()`.
2. **`GIT_CONFIG_GLOBAL`** pointing at a config that sets `core.excludesFile` or `status.showUntrackedFiles`. No COUNT required.
3. **`GIT_CONFIG_SYSTEM`** / **`GIT_CONFIG_NOSYSTEM`** — same class: replace or skip the system file. A system file that sets `excludesFile` is replaced; NOSYSTEM only helps if the *system* file was the one doing the excluding, so it is the weaker sibling.
4. **`HOME` / `XDG_CONFIG_HOME`** with no `GIT_CONFIG_*` at all — default ignore file `$XDG_CONFIG_HOME/git/ignore` or `$HOME/.config/git/ignore` (`gitignore(5)`). Caller-controlled HOME is enough.

Not counted as a remaining env vector: `GIT_CONFIG` (git-config command only). Not counted: `GIT_DIR/info/exclude` once `GIT_DIR` is unset (that is the real repo's exclude file). Not counted: in-tree `.gitignore` (tracked content, not caller env).

## Who is load-bearing for V-6

The two production consumers of `git ls-files --others --exclude-standard` are:

- `scripts/check-secrets.sh` default mode (untracked credential census)
- `scripts/check-vendor-honesty.sh` `artifacts()` (D-008(2) label scan and D-008(4) vendor-name scan)

Staged / `--staged` secret-guard still reads the index and is not this hole. Identity-only guards do not list untracked files. `check-review-scope.sh` lists tracked files with `-z`.

## What a named-list patch would miss

`check-v1-index-ordering.sh` already sets GLOBAL/SYSTEM and still inherits COUNT. An unset-list that names GLOBAL and SYSTEM and forgets COUNT is the same shape as 12-F2 forgetting CONFIG_*. `HOME` / `XDG_CONFIG_HOME` are not git-named at all. A repair that only extends the unset list re-creates the defect.

No repair is proposed here.
