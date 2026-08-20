# A1 ATTEMPT TWO — RESULTS ON THE BRANCH TIP, BEFORE ANY PRODUCTION CHANGE

**Author:** the independent test author for Batch A1 attempt two. Under D-058(1) and D-061(4) the
test author writes tests and makes **no production repair**. Nothing in this deliverable modifies
a production file, and no repair is proposed here in code.

**Branch tip under test:** `a6848d4d00775006fc663c8380e9adf335e9ce66` — the commit that carries
the failed first implementation (`63c6906`) and the independent verification that failed it
(`32d5f34`).

Paths are repository-relative. `<scratch>` stands for this session's temporary area outside the
repository.

---

## THE DEMONSTRATION D-061(4) REQUIRES

| | |
|---|---|
| new attempt-two harness `a2-env-and-supervisor.sh` | **exit 1** |
| REQUIRED assertions failed | **21 of 45**, every one for its intended reason |
| CONTROL assertions failed | **0 of 26** |
| original harness `a1-repo-identity.sh` | **exit 0** — REQUIRED failed **0**, CONTROL failed **0** |
| original harness modified? | **no — byte-identical, hashed before and after** |

**Hashes.**

| file | sha256 |
|---|---|
| `a1-repo-identity.sh` **before** this work | `54535b3b139ef9098753393872e39c932e25e0d861cfa14eb04e6f18c591122d` |
| `a1-repo-identity.sh` **after** this work | `54535b3b139ef9098753393872e39c932e25e0d861cfa14eb04e6f18c591122d` |
| `a2-env-and-supervisor.sh` | `dd67d69a13faf43e0578c57f9681e1468ca0b721727e7f14e83c1e5859fc84a7` |

**Why the original harness passing is not a contradiction.** It is blind to both confirmed
obligations by construction — its runnable set is the twelve check scripts, `scripts/test.sh` is
static-only, and its Case 4 fixture places the copied entry points *outside every repository*
rather than *inside a shape-compatible one*. `COVERAGE.md` §1 and §5 of the attempt-one
deliverables declared both gaps in advance. A repair must leave the first harness green and turn
the second one green.

---

## GROUP A — SUPERVISOR-ROOT PROPAGATION (`12-F1`)

**Fixture.** A brand-new unrelated repository holding an **empty** `scripts/test.sh`, an **empty**
`.githooks/pre-commit`, a README, and an executable decoy for every `scripts/check-*.sh` name,
each of which drops a marker file and exits 0. Sentinel's own `scripts/test.sh` is then invoked
**by absolute path** with the caller standing inside it — no environment manipulation, no
privileged access, no unusual setup. A credential is planted in the Sentinel subject so the
secret-guard stage is a live discriminator on which tree was read.

| case | kind | result | what it measured |
|---|---|---|---|
| A0 | CONTROL | PASS | a decoy drops a marker when it is actually executed — the marker mechanism is live |
| A0b | CONTROL | PASS | the foreign fixture's two lookalike files are **empty**: shape alone, no Sentinel content |
| **A1** | **REQUIRED** | **FAIL** | **9 decoy markers, 9 decoy lines in the gate's own output** |
| **A2** | **REQUIRED** | **FAIL** | the gate's secret-guard stage did **not** read Sentinel's tree — the planted credential was not blocked |
| A3 | REQUIRED | PASS | the foreign repository's worktree and `.git/config` are byte-identical afterwards |
| A4 | CONTROL | PASS | from Sentinel's root: **0 markers**, credential blocked — the discriminator is the caller's directory |
| A4s | OBSERVED | — | both arms reach 13 stages and both exit 5; **the exit status is not a discriminator here** |
| A5f | CONTROL | PASS | the 'outside' layout is genuinely inside no repository |
| A5 | CONTROL | PASS | a copy of the gate outside every Sentinel repository refuses **before any child runs** (0 markers) |
| A6 / A6n | CONTROL | PASS | the refusal scorer accepts three invented wordings and rejects six incidental failures |

**Nine, not four.** The earlier verification planted four decoys and observed four. `test.sh`
calls **nine** `scripts/check-*.sh` children; a fixture that plants a decoy for every check-script
name catches all nine. Among them is `check-gate-immutability.sh`, whose decoy exit 0 the gate
prints as its own immutability stage passing.

**The mechanism.** `scripts/test.sh:169` validates identity with `-e` tests on two path names.
Two empty files satisfy it. That is the construction D-061(3) forbids: identity may not be
validated by the presence of filenames alone.

---

## GROUP B — GIT-ENVIRONMENT ISOLATION (`12-F2`)

Six configurations, exercised **separately**, each proven to redirect something before being
trusted (preflight P7): `GIT_DIR`, `GIT_WORK_TREE`, `GIT_DIR`+`GIT_WORK_TREE`, `GIT_INDEX_FILE`,
`GIT_COMMON_DIR`, `GIT_PREFIX`. **`GIT_PREFIX` redirects nothing observable on git 2.50.1** and
its lines are marked inert in the harness output rather than counted as coverage.

### B1 — `check-secrets.sh`, credential planted and staged in the SUBJECT

| configuration | default mode | `--staged` mode |
|---|---|---|
| none (CONTROL) | blocked | blocked |
| `GIT_DIR` | blocked | **FAIL — `secret guard: clean`, exit 0** |
| `GIT_WORK_TREE` | blocked | blocked |
| `GIT_DIR`+`GIT_WORK_TREE` | **FAIL — clean, exit 0** | **FAIL — clean, exit 0** |
| `GIT_INDEX_FILE` | blocked | **FAIL — refusal, not a block** |
| `GIT_COMMON_DIR` | blocked | **FAIL — refusal, not a block** |
| `GIT_PREFIX` (inert) | blocked | blocked |

Two rows print a **clean report over unread Sentinel content**, which is the worst shape of the
defect and is raised as its own OBSERVED line. Three more fail closed but do not do their job.

**A trap for the repair, recorded so nobody is credited for it.** Several default-mode rows block
*incidentally*: once the tracked enumeration is redirected, Sentinel's own files fall into
`git ls-files --others`, and the untracked sweep added in round six reads them from the working
tree. The tracked enumeration still read the wrong repository.

### B2 — `install-hooks.sh`, one **fresh** victim repository per configuration

The whole `.git/config` file is hashed, not just `core.hooksPath`.

| configuration | victim `core.hooksPath` | victim `.git/config` | exit |
|---|---|---|---|
| `GIT_DIR` | **FAIL — written `.githooks`** | **mutated** | 0 |
| `GIT_COMMON_DIR` | **FAIL — written `.githooks`** | **mutated** | 0 |
| `GIT_WORK_TREE`, `GIT_DIR`+`GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_PREFIX` | unset | unchanged | 2 / 2 / 0 / 0 |

**`GIT_COMMON_DIR` is a second, independent route to the same mutation and is not in the
verifier's record.** Both routes end in exit 0 and a success message, into a repository the script
does not own — D-060(2)'s explicit prohibition.

Controls: a caller-provided `GIT_DIR` demonstrably redirects a git **config write** into a fresh
scratch repository (so B2 is not passing for want of a mechanism), and with no variables
`install-hooks.sh` against Sentinel still succeeds.

### B3 — the pre-commit hook

Invoked in the **matching** repository with hook-shaped variables present, as a wrapper, a CI step
or `git filter-branch` supplies them, with a credential staged in the subject:

| configuration | result |
|---|---|
| none (CONTROL) | blocked |
| `GIT_DIR` | **FAIL — `secret guard: clean`, exit 0 over a live staged credential** |
| `GIT_WORK_TREE`, `GIT_DIR`+`GIT_WORK_TREE` | refusal on identity mismatch (fail-closed, accepted) |
| `GIT_INDEX_FILE`, `GIT_COMMON_DIR` | **FAIL — neither blocked nor a dedicated refusal** |
| `GIT_PREFIX` (inert) | blocked |

`B3b` PASSES and must stay passing: on a genuine identity mismatch the hook still refuses
**before** executing the caller's own `scripts/check-secrets.sh`, and the decoy never runs.
`B3c` PASSES: a matching repository still commits benign content and still blocks a credential
through a real `git commit`.

### B4 — the census across all sixteen entry points

A recording `git` on `PATH` writes one line per invocation naming which caller-provided variables
were present, then delegates to the real git verbatim, so this is today's behaviour and not a
simulation. The injected values are the **subject's own** paths, so every entry point runs
normally and the census sees all of its calls rather than only the ones before it fails.

```
238 git invocations recorded across 16 of 16 entry points
  8 entry points carry caller-provided variables into a BODY-LEVEL git call:
      check-rename-gate.sh   check-review-scope.sh   check-secrets.sh
      check-vendor-honesty.sh  install-hooks.sh  mutate.sh  test.sh  .githooks/pre-commit
209 body-level calls carried GIT_DIR and its four siblings
  1 body-level call carried only GIT_PREFIX, which is inert on this git
  0 entry points made no git call at all
```

`rev-parse --show-toplevel` calls that carry caller variables are **exempt** — reading the
caller's context is a legitimate identity input — and what they carried is printed instead, so the
exemption hides nothing. It shows that the entry points' identity probes scrub `GIT_DIR`,
`GIT_WORK_TREE`, `GIT_INDEX_FILE` and `GIT_COMMON_DIR` and do **not** scrub `GIT_PREFIX`.

Control B4s: the census scores a deliberately leaky synthetic body as a carrier and a
deliberately scrubbed one as clean. It can fail, and it can pass.

### B5 — `mutate.sh`'s dirty-tree refusal

`mutate.sh` refuses to run against a dirty `ts/src` or `contracts/src`, because a mutation cannot
otherwise be told from work in progress. That refusal is a body-level `git status`.

| configuration | refusal fires? |
|---|---|
| none (CONTROL) | yes |
| `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_PREFIX` | yes |
| `GIT_DIR`+`GIT_WORK_TREE` | **FAIL — no** |
| `GIT_COMMON_DIR` | **FAIL — no** (`fatal: bad object HEAD`, empty status, run proceeds) |

Opposite control B5clean: on a clean tree the refusal does **not** fire, so the assertion is not
satisfiable by a script that refuses unconditionally.

---

## GROUP C — STAGED RENAME AND TYPECHANGE (`R1`)

Adjudicated **CONFIRMED** in `R1-ADJUDICATION.md`. Whether it is worked is John's call under
D-061(2); this group supplies the reproduction and the assertions.

| case | kind | result |
|---|---|---|
| C0 | CONTROL | PASS — the staged pair really scores a rename record. *This is the assertion whose absence produced the earlier false negative.* |
| **C1** | **REQUIRED** | **FAIL** — the rename destination is not scanned: clean, exit 0 |
| **C1b** | **REQUIRED** | **FAIL** — the commit succeeds through the hook and **the credential reaches HEAD** |
| C2f | CONTROL | PASS — the executable-rename fixture really carries new mode `100755` |
| **C2** | **REQUIRED** | **FAIL** — an executable rename destination is not scanned |
| C3f | CONTROL | PASS — the typechange fixture really scores a `T` record from `120000` to `100644` |
| **C3** | **REQUIRED** | **FAIL** — the typechange destination is not scanned |
| C4 | CONTROL | PASS — an ordinary staged ADD of the identical bytes **is** blocked: the discriminator is the status letter, not the pattern |
| C5 / C5b | CONTROL | PASS — genuine staged deletions are still accepted (D-059(3) is not foreclosed) |
| C6f / C6 | CONTROL | PASS — a newly staged gitlink carries new mode `160000` and is not a false failure |
| C7f / C7 | OBSERVED / CONTROL | a staged **copy** scores `C`, which is **inside** `--diff-filter=ACM`, and is already blocked. Copy is a regression risk for the repair, not a live defect |
| C8 / C8b | OBSERVED | one staged rename produces **three** NUL-delimited fields — record, source and destination — so one pathname per record is an assumption that drops destinations. The excluded statuses at this SHA are `R` and `T` |

---

## CLOSING CONTROLS

| case | result |
|---|---|
| Z1 | PASS — no git configuration was written to the redirected global/system/XDG files or to the repository under test |
| Z2 | PASS — the subject clone ends at the branch tip with no modification, so every case measured a clean subject |
| Z3 | OBSERVED — 7 shimmed-child hits recorded; reaching a shim is an instrument fact, never a result |

**Isolation.** Every case ran against a private clone or against repositories the harness created
under `TMPDIR`, all removed on exit. Git configuration was never written into a repository the
harness did not create. The repository under test was read and never written. The operator's own
global, system and XDG git configuration was redirected into scratch for every scored run and
asserted unchanged.

---

## WHAT THESE RESULTS DO NOT ESTABLISH

The full list is in `COVERAGE.md`. The three that matter most for reading the table above:

1. **The gate cannot complete in this worktree** (`contracts/lib` unpopulated, no `node_modules`
   in an isolated clone, and provisioning either is a network state change a test author may not
   make). Both group A arms exit 5. The exit status is not a discriminator; the decoy markers and
   the secret-guard stage's tree are.
2. **`GIT_PREFIX` is inert on this git**, so its four REQUIRED lines are not coverage.
3. **The census exempts `rev-parse --show-toplevel`**, so an implementation that derived its
   working root from a caller-carried answer would need groups A, B1, B2 and B3 — which assert
   outcomes — to catch it. The census supplements those and does not replace them.
