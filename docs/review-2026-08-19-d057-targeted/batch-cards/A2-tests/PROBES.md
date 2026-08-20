# A1 ATTEMPT TWO — PROBES

Every probe below was run before the harness was written, against an isolated clone of the
branch tip in this session's scratch area. **Nothing here was written to the repository under
test.** Paths are repository-relative; `<subject>` is the isolated clone and `<scratch>` this
session's temporary area.

This file exists because this project has shipped dead probes whose silence read as a pass. Each
entry therefore records **what the probe moved** — the observable that changed when the probe was
live — and the negative results are kept, not discarded.

---

## E. THE ENVIRONMENT, MEASURED RATHER THAN ASSUMED

| fact | value |
|---|---|
| git | 2.50.1 |
| bash | 3.2.57 — no `mapfile`, no associative arrays, and `"${arr[@]}"` on an empty array is an unbound-variable error under `set -u` |
| `core.quotePath` | unset (default true) |
| `diff.renames` | unset (default true — rename detection is ON, which is what makes R1 live) |
| `timeout(1)` | **not present** on this platform; every long child in the harness is bounded with a wait loop instead |
| Foundry submodules | `contracts/lib` unpopulated; `forge` cannot build. A1 is git and shell only, so this bounds nothing except the gate's own completion — see COVERAGE.md §2 |

---

## D0. THE DEAD-PROBE CHECKS THEMSELVES

These are the probes that prove the other probes can fail. All are carried into the harness as
preflights or controls.

| id | check | moved |
|---|---|---|
| D0-1 | `/usr/bin/grep` finds a planted canary string | the shell's `grep` on this workstation is a wrapper honouring `--ignore-files` and can return a clean-looking zero; every search in the harness uses `/usr/bin/grep` and this proves it reads |
| D0-2 | the planted credential trips `check-secrets.sh` in **both** modes before any case runs | without it every "clean" result below would be vacuous for a reason unrelated to the defect |
| D0-3 | a caller decoy script drops a marker when it is actually executed | "zero markers" means nothing if a decoy cannot drop one |
| D0-4 | a caller-provided `GIT_DIR` really does redirect a git **config write** into a fresh scratch victim | the install-hooks group would otherwise pass for want of a mechanism rather than because the guard held |
| D0-5 | the git-call census scores a deliberately leaky synthetic body as a carrier and a deliberately scrubbed one as clean | a census that cannot distinguish them is measuring nothing |
| D0-6 | the identity-refusal scorer accepts three invented wordings and rejects six incidental failures | a non-zero exit is not a refusal; scoring one as a refusal is the mislabelling the A1 card forecloses |
| D0-7 | the rename fixture actually scores an `R` record | this is the exact assertion whose absence produced the earlier false negative — see R2 below |

---

## A. SUPERVISOR-ROOT PROPAGATION (12-F1)

**A1 — the foreign lookalike.** A brand-new repository containing an **empty** `scripts/test.sh`,
an **empty** `.githooks/pre-commit`, a README, and twelve executable decoys named for every
`scripts/check-*.sh`, each of which drops a marker and exits 0. Sentinel's own `scripts/test.sh`
was then invoked **by absolute path** with the caller standing inside it. No environment
manipulation, no privileged access.

```
decoy markers created            : 9
'CALLER DECOY … EXECUTED' lines in the gate's own output : 9
credential planted in the SUBJECT and blocked            : no
foreign repository worktree + .git/config                : unchanged
elapsed                                                  : 4s
```

Nine, not four: the gate calls **nine** `scripts/check-*.sh` children, and a fixture that plants
a decoy for every check-script name catches all of them. The earlier verification planted four.

**MOVED:** nine marker files that do not exist unless a caller-supplied script executed, and the
absence of a block on a credential the subject does carry.

**A2 — the control from Sentinel's own root.** The identical command, caller standing in the
subject: **0 markers, credential blocked, same 13 stage headers.** The discriminator is live and
it is the caller's directory.

**A3 — a copy of the gate outside every repository.** The gate copied out with its `scripts/`
structure preserved, beside the same decoys, into a directory inside no repository: a dedicated
identity refusal, **0 markers**, non-zero exit. Refusal before children, as required.

**A4 — what the body actually validates.** `scripts/test.sh:169` tests `-e` on two path names.
Two empty files satisfy it. This is why D-061(3) says identity may not be validated by the
presence of filenames alone: any repository can produce two empty files.

---

## B. GIT-ENVIRONMENT ISOLATION (12-F2)

### B0 — A FALSE READING, AND HOW IT WAS CAUGHT

The first pass at this matrix appeared **non-deterministic**: `GIT_DIR`+`GIT_WORK_TREE` printed a
clean report in one run and an enumeration failure in the next, from the same tree. The cause was
not the subject. The probe was being driven from an interactive `zsh`, where an unquoted variable
holding two `VAR=VAL` words does **not** word-split, so `env` received one variable whose value
contained a space — a `GIT_DIR` pointing at a path that does not exist. The "flake" was the
instrument.

Re-run under `bash`, every row is stable and repeats. **Recorded because a matrix that looks
flaky is usually a harness bug, and treating it as flakiness would have buried a real finding.**
The harness is `#!/usr/bin/env bash` and builds every environment as an array.

### B1 — DOES EACH VARIABLE DO ANYTHING? (the liveness question, asked first)

Measured from the subject's root, comparing against the subject's own answers (488 tracked files;
toplevel = the subject):

| configuration | redirects |
|---|---|
| `GIT_DIR` | the file list, and **config reads and writes** |
| `GIT_WORK_TREE` | the reported toplevel |
| `GIT_DIR` + `GIT_WORK_TREE` | toplevel, file list and config |
| `GIT_INDEX_FILE` | the file list |
| `GIT_COMMON_DIR` | **config reads and writes** |
| `GIT_PREFIX` | **nothing observable on this git** |

`GIT_PREFIX` is inert here. It is still exercised, and every required line under it is marked
inert in the harness output rather than counted as coverage — silence is not evidence.

`GIT_COMMON_DIR` redirecting **config** is not in the verifier's record and matters: it is a
second, independent route to the same install-hooks mutation.

### B2 — THE CREDENTIAL GUARD

Credential planted in the **subject** and staged there; variables pointed at a one-file decoy that
does not contain it.

| configuration | default mode | `--staged` mode |
|---|---|---|
| none (control) | BLOCKED | BLOCKED |
| `GIT_DIR` | BLOCKED | **clean, exit 0** |
| `GIT_WORK_TREE` | BLOCKED | BLOCKED |
| `GIT_DIR`+`GIT_WORK_TREE` | **clean, exit 0** | **clean, exit 0** |
| `GIT_INDEX_FILE` | BLOCKED (see note) | refusal |
| `GIT_COMMON_DIR` | BLOCKED | refusal |
| `GIT_PREFIX` | BLOCKED | BLOCKED |

**Note, and it is a trap for the repair.** Several default-mode rows block for an *incidental*
reason: when the tracked enumeration is redirected, the subject's own files fall into
`git ls-files --others`, so the untracked sweep added in round six reads them from the working
tree and catches the credential anyway. The tracked enumeration still read the wrong repository.
A repair must not be credited for these rows — which is why the harness records the
clean-report flag on every line and flags the clean-over-unread-content rows separately.

### B3 — `install-hooks.sh`, one fresh victim per configuration

`core.hooksPath` before and after, plus a sha256 of the **whole** `.git/config` file:

| configuration | victim `core.hooksPath` | victim config | exit |
|---|---|---|---|
| `GIT_DIR` | **`.githooks` — written** | **mutated** | 0 |
| `GIT_COMMON_DIR` | **`.githooks` — written** | **mutated** | 0 |
| the others | unset | unchanged | varies |

Two independent routes, both ending in `exit 0` and a success message, into a repository the
script does not own. This is D-060(2)'s explicit prohibition.

**MOVED:** a config key that does not exist in a freshly created repository unless something
wrote it, and a whole-file hash that changes with it.

### B4 — THE HOOK

Invoked in the **matching** repository with hook-shaped variables present, as a wrapper, a CI
step or `git filter-branch` supplies them; a credential staged in the subject:

- `GIT_DIR` at the decoy: **`secret guard: clean`, exit 0** — the hook's identity comparison
  matches, it execs the guard, and the guard reads the decoy's staged set, which is empty.
- `GIT_WORK_TREE` / both: the hook refuses on an identity mismatch (fail-closed; accepted).
- `GIT_INDEX_FILE` / `GIT_COMMON_DIR`: refusal from the guard (fail-closed; accepted).
- `GIT_PREFIX`: blocked (correct).

Git **exports** git environment variables while a hook runs, which is why the invoking repository
has to be captured *before* they are cleared and why they have to be cleared *before* the guard
is executed.

### B5 — `mutate.sh`

`mutate.sh` refuses to run against a dirty `ts/src` or `contracts/src`. That refusal is computed
by a body-level `git status`, so it is the same shape. With `ts/src` genuinely dirty:

- no variables: refuses (control).
- `GIT_DIR`+`GIT_WORK_TREE`: **the refusal does not fire** — it proceeds.
- `GIT_COMMON_DIR`: `fatal: bad object HEAD`, empty status, **the refusal does not fire**.
- `GIT_DIR` alone, `GIT_INDEX_FILE`, `GIT_WORK_TREE`, `GIT_PREFIX`: refuses (for the wrong
  reason in the `GIT_DIR` case — everything looks untracked — but fail-closed).

**Opposite control:** on a clean tree the refusal does **not** fire, so the assertion is not
satisfied by a script that refuses unconditionally.

---

## C. THE STAGED RENAME AND TYPECHANGE (R1)

### R2 — WHY THE EARLIER NEGATIVE RESULT DOES NOT REPRODUCE

`PROBES.md` D2 in the attempt-one deliverables reported that "rename detection is not applied
here, so the new path surfaces as `A`". Rebuilt at two sizes:

| fixture | raw record | `--diff-filter=ACM` | `--staged` |
|---|---|---|---|
| small file, credential appended | `D` + `A` | names the added path | **BLOCKED** |
| 400-line file, credential appended | `R099`, source and destination | **empty** | **clean, exit 0** |

The earlier probe measured its own fixture, not the guard. Appending a credential to a short file
drops similarity below git's rename threshold and splits the change. **The harness therefore
asserts that the record actually scored `R` as a control**, so this cannot recur silently.

### R3 — THE FULL SHAPE

- rename destination carrying a credential: clean, exit 0, `git commit` succeeds, the credential
  is in HEAD.
- typechange (`120000` → `100644`) with a credential in the destination: clean, exit 0.
- staged copy (`C`): **blocked** — `C` is inside `ACM`.
- ordinary staged add: blocked. Genuine staged deletion: accepted. New gitlink: accepted.
- **default** mode still blocks the rename destination, because the working-tree copy is present.
  The exposure is the `--staged` path, and therefore the hook.

Full adjudication in `R1-ADJUDICATION.md`.

---

## N. NEGATIVE AND INERT RESULTS, KEPT

- `GIT_PREFIX` redirects nothing observable on git 2.50.1. Kept, exercised, and marked inert.
- The staged **copy** is not part of the bypass. The brief listed copy among the records to fix;
  measurement says `C` is already enumerated. It is carried as a regression control instead.
- `GIT_DIR` alone does **not** defeat `mutate.sh`'s dirty-tree refusal — it defeats it only in
  combination with `GIT_WORK_TREE`, or alone via `GIT_COMMON_DIR`. Recorded so a repair is not
  measured against a rule that was never true.
- The gate's **exit status** is not a discriminator for group A: both the foreign-caller run and
  the Sentinel-root run exit 5 in this worktree, for the environment reason in COVERAGE.md §2.
  The discriminators are the decoy markers and which tree the secret-guard stage read.
