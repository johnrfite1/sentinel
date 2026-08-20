# A1 — RESULTS

**Base SHA:** `f68d4d804de4d3b631e25fd539deecda5409f0d7`, confirmed with `git rev-parse HEAD` in the
A1 worktree and again in the primary tree. Both are at that commit.

**Harness:** `a1-repo-identity.sh` (added by `TESTS.patch`). Two consecutive runs, and a third run
from a freshly-patched clone with no argument, were **byte-identical**.

**Aggregate at this SHA:** `REQUIRED failed 18 · CONTROL failed 0 · harness exit 1.`

The harness exits `2` if any control fails, so *no* required line below can be read as evidence
unless the control tally is zero. It is zero.

---

## The 13 cases

| # | Case | Required | Observed at this SHA | Verdict |
|---|---|---|---|---|
| 1 | invoked from Sentinel's root | normal result | 16/16 entry points are tracked, `#!/usr/bin/env bash`, executable; 12/12 executable checkers exit 0 from the root; 4 asserted statically only | **PASSES-AS-CONTROL** |
| 2 | invoked from an unrelated directory | still checks Sentinel | **12 of 12 give a different answer.** 10 fail closed by accident (missing files); **2 exit 0 with a clean-looking summary** — `check-secrets.sh` (`secret guard: clean`) and `check-rename-gate.sh` (`no remote configured — nothing can be public`) | **FAILS-AS-INTENDED** |
| 3 | invoked from inside a foreign git repository | still checks Sentinel | **11 of 12 give a different answer**; `check-review-scope.sh` prints a partition **of the foreign repository** and, with `SENTINEL_SCOPE_BASE` set, exits **0** with a fully clean report about it. `check-secrets.sh` returns `clean` for the wrong repository while the Sentinel tree that contains it holds a planted credential (case 3a) | **FAILS-AS-INTENDED** |
| 4 | repository identity unresolved | refuse | **2 of 12 exit 0** with a result they did not establish; 10 refuse | **FAILS-AS-INTENDED** |
| 5 | a git command exits non-zero | refuse | `check-secrets.sh` default mode prints `secret guard: clean`, exit 0, when `git ls-files` exits 3 (5a). `check-review-scope.sh`'s `--error-unmatch` call (`:198`, `V3-N1`) turns a true remediation surface of **87** into **0**, `all assigned`, exit 0 (5b/5c) | **FAILS-AS-INTENDED** |
| 6 | a git command succeeds with **empty** output | refuse | `check-secrets.sh` prints `secret guard: clean`, exit 0 | **FAILS-AS-INTENDED** |
| 7 | a genuine **staged deletion** | accept — protected control (D-059(3)) | guard exit 0, hook exit 0, commit lands. `--diff-filter=ACM` never enumerates the deleted path, so nothing is skipped and nothing needs to be | **PASSES-AS-CONTROL** |
| 8 | ASCII filename carrying a planted credential | blocked | blocked in **both** modes (default exit 1, `--staged` exit 1) | **PASSES-AS-CONTROL** |
| 9 | **non-ASCII** filename, byte-identical credential | blocked (`C4`) | **clean, exit 0, in both modes** — untracked, tracked, and staged | **FAILS-AS-INTENDED** |
| 10 | secret guard **default** mode | fail-closed | a tracked path is enumerated, the index still holds the credential, the working-tree copy is gone → `[ -f "$f" ] \|\| continue` skips it → `secret guard: clean`, exit 0 | **FAILS-AS-INTENDED** |
| 11 | secret guard **`--staged`** mode | fail-closed | `git show ":$f"` made to fail → `\|\| continue` skips every staged file → `secret guard: clean`, exit 0 | **FAILS-AS-INTENDED** |
| 12 | `install-hooks.sh` against a **foreign** repository | refuse; never write `core.hooksPath` | **`core.hooksPath=.githooks` is written into the foreign repository.** Its non-zero exit is a downstream `chmod` failure that happens *after* the write, not a refusal | **FAILS-AS-INTENDED** |
| 13 | pre-commit hook, repository-identity **mismatch** | refuse | the hook resolves `repo_root` from the **caller's** repository and `exec`s that repository's `scripts/check-secrets.sh`. With a decoy guard present the decoy **ran**, the commit **succeeded**, and the credential **landed in the foreign repository's HEAD** | **FAILS-AS-INTENDED** |

**Controls: 11 asserted, 11 held.** 1a, 1b, 1c, 3a-control, 4-control, 5d, 5e, 6-control,
7, 8, 89, 10-control, 11-control, 12c, 13c, 13d.

---

## Cases 8 vs 9 — the discriminator, stated as evidence

Both fixtures are written by the same function with the same fill character and are verified
**byte-identical** by `cmp -s` inside the harness (control `89`, PASS). Content, mode and staged
blob are the same. **Only the filename differs**: one is ASCII, one carries `é` as the two bytes
`\303\251`.

| | ASCII twin (case 8) | non-ASCII twin (case 9) |
|---|---|---|
| default mode, untracked | **BLOCKED**, exit 1 | clean, exit 0 |
| default mode, tracked | **BLOCKED**, exit 1 | clean, exit 0 |
| `--staged` mode | **BLOCKED**, exit 1 | clean, exit 0 |

The mechanism, captured by the harness rather than inferred:

```
enumeration as check-secrets.sh sees it (quoted):
  ls-files      -> "a1-case9-caf\303\251.ts"
  diff --cached -> "a1-case9-caf\303\251.ts"
the same paths with quoting removed:
  ls-files -z            -> a1-case9-café.ts
  diff --cached --raw -z -> a1-case9-café.ts
```

`core.quotePath` is unset in every repository probed, i.e. at its default of true. The quoted
string is not a path that exists, so `[ -f "$f" ]` is false in default mode and
`git show ":$f"` fails in staged mode, and both skip points are `|| continue`. **The asymmetry is
real and it is the filename, not the content.** A guard that blocked both twins would prove
nothing; this one blocks exactly one.

---

## Secret guard: does a **default-mode** discriminator exist?

**Yes — one exists, and the harness prints the evidence rather than applying it.** The adjudicated
staged-mode discriminator (`git diff --cached --raw -z`, status letter plus blob OID) does not
transfer, exactly as the card says: default mode uses `git ls-files` and there are no status
letters. What default mode *does* have is a three-part substitute, all of it observed:

1. **Quoting** — `git ls-files -z` and `git ls-files --others --exclude-standard -z` emit the raw
   path. Observed above: the accented name comes out unquoted and openable. This is `C4`'s root
   cause in default mode, and `-z` removes it.
2. **Legitimately-not-a-file** — `git ls-files -s -z` carries the mode bit. Census of this index:
   `460 × 100644`, `16 × 100755`, `2 × 160000`. The two `160000` entries are the Foundry gitlinks
   `contracts/lib/forge-std` and `contracts/lib/openzeppelin-contracts`, which are tracked paths
   that are correctly not regular files. Any repair that refuses on "enumerated but not a regular
   file" without consulting the mode bit will refuse on those two and break case 1.
3. **Legitimately-absent** — `git ls-files --deleted -z` names exactly the paths the index holds
   and the working tree does not. In case 10 it named the planted file, and `git show ":$f"` still
   produced its content.

**What is NOT mine to settle, and is recorded as a fork rather than answered:** whether an
index-vs-worktree deletion in default mode should be *read from the index* (`git show ":$f"`, which
would scan content the working tree no longer shows) or *skipped as legitimate* (matching case 7's
protection of a genuine deletion). Both are defensible; they differ in what the guard is for. That
is a product question. **John's, per the card.**

---

## Two labelling corrections made during authoring, recorded because they are the audit failure mode

1. My first harness scored `install-hooks.sh`'s foreign-repository exit status **1** as
   *"refuses rather than proceeding"* — **PASS**. It is not a refusal. `core.hooksPath` had already
   been written; the non-zero status comes from the `chmod` that follows. Corrected: case 12b now
   requires a non-zero exit **with nothing written**, and it FAILS.
2. My first harness inverted the flag for case 13b, so *"the decoy guard ran"* scored **PASS**.
   Corrected; it FAILS.

Both were the mistake the card names — a probe that already behaves incorrectly being written up as
a pass. They are recorded here rather than quietly fixed.
