# A1 ATTEMPT TWO — INDEPENDENT VERIFICATION OF THE REPAIR

**Verifier:** an independent agent that wrote neither harness and neither implementation attempt,
and repaired nothing. Every probe below was built from scratch against the obligations in
`docs/decisions.md` D-061 and batch card `A1.md`. No result was taken on either harness's word;
both harnesses were run, but only after the independent probes had already produced their own
answers.

**Commit under verification:** `f61ecca55557b7912cc26fddc87127cb0f6e2ebb`
(*A-083: Batch A1 implementation attempt two*).
**Pre-repair baseline used for every discriminator:** `9091d41` — the test-contract commit,
which carries the failed first implementation. Where a probe below reports HOLD, the same probe
was run at `9091d41` and reported the defect, so the instrument is demonstrably live.

**Harnesses, hashed in the frozen worktree and untouched by the implementation commit:**

| file | sha256 | matches the declared hash |
|---|---|---|
| `A1-tests/a1-repo-identity.sh` | `54535b3b139ef9098753393872e39c932e25e0d861cfa14eb04e6f18c591122d` | yes |
| `A2-tests/a2-env-and-supervisor.sh` | `dd67d69a13faf43e0578c57f9681e1468ca0b721727e7f14e83c1e5859fc84a7` | yes |

`git diff --stat 9091d41..HEAD` touches sixteen production files and **no file under `docs/`**, so
D-061(4)'s "neither harness is the implementer's to touch" holds mechanically.

Paths are repository-relative. `<scratch>` stands for this session's temporary area outside every
repository; `<subject>` for an isolated clone of the commit under verification; `<baseline>` for an
isolated clone of `9091d41`.

---

## VERDICT: **FAIL**

Eight of the nine assigned items hold, most of them with a live pre-repair discriminator that
demonstrates the defect really was closed. Both confirmed obligations `12-F1` and `12-F2` are
closed against every probe I could build, and the `R1` enumeration repair is sound.

**Item 2 fails.** The `12-F2` repair clears `GIT_INDEX_FILE` unconditionally, and git *legitimately*
hands the pre-commit hook a **temporary index** in that variable for two ordinary commit forms.
Clearing it makes the guard read a different index from the one being committed, so
`git commit -a` and `git commit -- <path>` now print `secret guard: clean`, exit 0, and **land a
credential in HEAD**. Both were blocked at the pre-repair baseline. This is a **regression
introduced by attempt two**, it sits inside batch card A1's own symbol boundary (`git diff --cached`
in `check-secrets.sh`), and it breaks the fail-closed half of A1's invariant in the most direct way
available: a clean report over repository content the guard did not read.

Both harnesses are **green** at this commit — `a1-repo-identity.sh` exit 0 (REQUIRED 0, CONTROL 0)
and `a2-env-and-supervisor.sh` exit 0 (REQUIRED 0, CONTROL 0), and I ran both. That is not
contradicted here. The attempt-two harness injects `GIT_INDEX_FILE` pointing at a **decoy** index,
which the repair correctly ignores; it never injects the **legitimate temporary index git itself
creates**, which is the case the repair now mishandles. The tests are not overclaiming; the
implementation is wrong in a shape neither harness instruments.

---

## PER-ITEM RESULTS

| # | Item | Result |
|---|---|---|
| 1 | decoy shape-compatible repository | **HOLD** — 0 markers, Sentinel's tree read, foreign repo byte-identical |
| 2 | each git environment variable, separately and combined | **FAIL** — see below; the six declared configurations hold, the repair's own clearing of `GIT_INDEX_FILE` opens a new hole |
| 3 | foreign-repository configuration mutation | **HOLD** — whole `.git/config` byte-identical in every configuration |
| 4 | hook mismatch before caller execution | **HOLD** — decoy never ran, no commit landed |
| 5 | staged rename-with-modification and typechange | **HOLD** — destination scanned and blocked in both |
| 6 | staged-deletion control | **HOLD** — accepted, no false failure |
| 7 | copied `test.sh` identity refusal | **HOLD** — dedicated refusal, exit 5, zero shims reached |
| 8 | all 16 entry points, surviving caller-relative git operations | **HOLD** — 0 of 267 body-level calls carry a caller variable |
| 9 | gate supervisor and completion-token behaviour | **HOLD** — every preserved property independently re-falsified |

**Foundry bounding.** `contracts/lib` is unpopulated in the review worktree and `forge` cannot run
there. It bounded nothing: A1 is git and shell only, and the two entry points that drive Foundry
were reached with their expensive children shimmed to a recorder that does no work and returns 97.
Reaching a shim is recorded as an instrument fact, never scored as a result. `ts/node_modules` is
provisioned in the worktree but not in an isolated clone, so no gate run reaches completion here —
consistent with `COVERAGE.md` §2, and the reason exit status is never used below as a discriminator
for group-A-shaped probes.

---

# 2. THE FAILURE — A CLEARED `GIT_INDEX_FILE` MAKES THE HOOK READ THE WRONG INDEX

## 2-F1 — `git commit -a` and `git commit -- <path>` now admit a credential to HEAD

**Severity: high. No environment manipulation, no privileged access, no unusual setup — two of the
most ordinary commit forms there are.**

### What the repair added

`.githooks/pre-commit` (line 31) and `scripts/check-secrets.sh` (line 76) each gained

```
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
```

The hook clears it immediately before `exec "$HOOK_ROOT/scripts/check-secrets.sh" --staged`.

### What git actually supplies

Measured on git 2.50.1 by pointing `core.hooksPath` at a probe hook that dumps its environment,
in a repository I created:

| commit form | `GIT_INDEX_FILE` handed to the hook |
|---|---|
| `git commit` (pre-staged) | `.git/index` — relative, and re-resolves harmlessly after the `cd` |
| `git commit -- <path>` | `<root>/.git/next-index-<pid>.lock` — **a temporary index**, absolute |
| `git commit -a` | `<root>/.git/index.lock` — **the index that will become the commit**, absolute |

In the second and third forms `.git/index` does **not** contain what is being committed. The
temporary index does. The repair discards the pointer to it.

### Measured outcome, subject versus baseline

Fixture: `docs/ablation-report.md`, a tracked file already in the tree, with one credential-shaped
line appended in the **working tree only** — nothing staged. `core.hooksPath=.githooks`. The
planted value is an obviously fake one, assembled at run time from a single repeated hex character
and bound to an identifier of the shape the guard's own rule 3b exists to catch. Both arms used the
identical fixture.

| | `<subject>` `f61ecca` | `<baseline>` `9091d41` |
|---|---|---|
| control: an ordinary staged add of the same content | blocked, commit refused | blocked, commit refused |
| `git commit -am …` | **exit 0 · `secret guard: clean` · credential in HEAD** | exit 1 · destination named and blocked · not in HEAD |
| `git commit -m … -- <path>` | **exit 0 · `secret guard: clean` · credential in HEAD** | exit 1 · destination named and blocked · not in HEAD |

The hook's entire output on the failing run is one line: `secret guard: clean`. That is the hook's
verdict, and the commit proceeds on it.

### The cause isolated, with the R1 parser held constant

The obvious alternative explanation is the new raw-record parser. It is not that. I cloned the
subject, deleted **only** the added `unset` line from `scripts/check-secrets.sh`, left the R1 raw
parser exactly as shipped, built the temporary index by hand the way git builds it
(`git read-tree HEAD` then `git add` into a private index file), and ran the guard against it:

```
patched clone  (scrub line removed, raw parser kept) : exit 1, destination named and BLOCKED
f61ecca as shipped                                   : exit 0, "secret guard: clean"
```

One line accounts for the whole difference. The raw parser is not implicated, and item 5 below
confirms it independently.

### Why this is a contract failure and not a residual

- It is inside batch card A1's declared **symbol boundary**: the `git diff --cached` enumeration in
  `check-secrets.sh`, `--staged` mode.
- It violates A1's invariant directly — "refuses rather than reporting a result it did not
  establish". The guard reports clean over content it never read.
- It violates D-061(1)'s stated principle in the mode next door: content the repository knows about
  goes unread while a clean line is printed.
- Test matrix case 11 (`secret guard --staged mode → fail-closed`) does not hold for these two
  commit forms.
- It is a **regression**: the baseline blocks both.
- It is the same class as `12-F2` itself — an entry point's body-level git operation resolving
  against the wrong repository state because of how the caller's git environment was handled. The
  first attempt failed by honouring that environment too much; the second fails by honouring it too
  little. `GIT_INDEX_FILE` is not purely a caller-provided override; in the hook it is also git's
  own hand-off of what is being committed, exactly as `INVOKING_ROOT` is git's own hand-off of where
  the commit is happening. The hook already captures `INVOKING_ROOT` before clearing the
  environment. It does not do the equivalent for the index.

### Blast radius

`--staged` mode is invoked from exactly one place, `.githooks/pre-commit:42`, and `pre-commit` is
the only hook in `.githooks/`. So the exposure is the commit path and only the commit path. The
gate's default-mode run would still catch the content on a later run — after it had already reached
HEAD, which is the same severity language `R1-ADJUDICATION.md` used for the defect this attempt was
authorised to close.

### What a repair would have to satisfy — stated as behaviour, not as an implementation

1. A credential in a file being committed by `git commit -a` is blocked, and the commit refused.
2. The same for `git commit -- <path>`.
3. The existing pre-staged path keeps behaving exactly as it does today.
4. A caller-provided `GIT_INDEX_FILE` pointing at an unrelated repository's index still cannot make
   the guard measure that repository — the `B1`/`B3` rows below must stay passing, and they must
   keep passing **for the reason they pass today** rather than incidentally.
5. Whatever distinguishes (1)–(2) from (4) is established by the hook, which is the only component
   that knows it was invoked by git, and passed to the guard explicitly — the way the
   supervisor-established root is passed to the gate body under D-061(3). A guard that simply
   re-honours whatever `GIT_INDEX_FILE` it inherits reopens `12-F2`.

Which route to take is an engineering choice. **Whether A1 is reopened at all is John's call**, and
under D-061(2) the default is that it is not.

---

## 1. DECOY SHAPE-COMPATIBLE REPOSITORY — HOLD

Built from scratch: a fresh repository holding an **empty** `scripts/test.sh`, an **empty**
`.githooks/pre-commit`, a README, and an executable decoy for **all fourteen** `scripts/*` names —
every `check-*.sh`, plus `install-hooks.sh` and `mutate.sh` — each of which drops a marker file,
prints a line naming itself, and exits 0. A credential was planted and committed in `<subject>` so
the secret-guard stage is a live discriminator on which tree was read. Sentinel's own
`scripts/test.sh` was then invoked **by absolute path** with the caller standing inside the foreign
repository, with no variables set.

| | from inside the foreign repository | from `<subject>`'s own root (control) | `<baseline>` from inside the foreign repository |
|---|---|---|---|
| decoy marker files created | **0** | **0** | **9** |
| decoy lines in the gate's output | **0** | **0** | **9** |
| planted credential blocked | **yes** | yes | **no** |
| stages reached | 13 | 13 | 13 |
| exit | 5 | 5 | 5 |

The stage-name sequence from the foreign repository is **byte-identical** to the sequence from
Sentinel's own root. Exit status is 5 in all three arms and is not a discriminator, exactly as
`COVERAGE.md` §2 declares; the markers and the credential are.

The foreign repository's whole-worktree fingerprint and its **entire** `.git/config` hash are
identical before and after, and `git status` there is empty afterwards.

Liveness control: a decoy invoked directly does drop its marker.

## 3. FOREIGN-REPOSITORY CONFIGURATION MUTATION — HOLD

`install-hooks.sh` run against a **fresh victim repository per configuration**, hashing the victim's
**whole** `.git/config` and its whole worktree before and after, in two caller positions.

**Caller standing inside the victim:** every configuration refuses (exit 2) except the
`GIT_DIR=<victim>` + `GIT_WORK_TREE=<subject>` shape, which correctly configures Sentinel and leaves
the victim untouched.

**Caller standing in Sentinel — the shape that actually reproduced the first attempt's defect:**

| configuration | `<baseline>` victim config | `<subject>` victim config | `<subject>` outcome |
|---|---|---|---|
| none | unchanged | unchanged | Sentinel configured, exit 0 |
| `GIT_DIR` | **MUTATED, exit 0** | **unchanged** | Sentinel configured, exit 0 |
| `GIT_WORK_TREE` | unchanged | unchanged | refusal, exit 2 |
| `GIT_DIR`+`GIT_WORK_TREE` | unchanged | unchanged | refusal, exit 2 |
| `GIT_INDEX_FILE` | unchanged | unchanged | Sentinel configured, exit 0 |
| `GIT_COMMON_DIR` | **MUTATED, exit 0** | **unchanged** | Sentinel configured, exit 0 |
| `GIT_PREFIX` | unchanged | unchanged | Sentinel configured, exit 0 |

Two independent baseline routes wrote `core.hooksPath` into a victim while Sentinel's own stayed
unset; both are closed, and in the closed rows Sentinel — and only Sentinel — is configured.

Liveness control, measured rather than assumed: a caller-provided `GIT_DIR`, and separately a
caller-provided `GIT_COMMON_DIR`, each redirects a `git -C <sentinel> config` **write** into a fresh
scratch repository. So item 3 is not passing for want of a mechanism.

No git configuration was written into any repository this session did not create. The operator's
global setting is still unset and both real trees still carry `core.hooksPath=.githooks`.

## 4. HOOK MISMATCH BEFORE CALLER EXECUTION — HOLD

A foreign repository with `core.hooksPath` pointed at `<subject>/.githooks`, its own
`scripts/check-secrets.sh` replaced by a decoy whose only job is to drop a marker and exit 0, and a
credential staged:

```
git commit  ->  exit 1
  FAIL  pre-commit: repository identity mismatch; refusing before running anything.
  decoy marker after the commit attempt : NO-DECOY-NEVER-RAN
  decoy output in the commit's output   : none
  commits in the foreign repository     : unchanged
  credential in the foreign HEAD        : no
  foreign .git/config                   : byte-identical
```

Control: the same decoy invoked directly does drop its marker.

## 5. STAGED RENAME-WITH-MODIFICATION AND TYPECHANGE — HOLD

Every fixture asserted to be the record it claims to be **before** the guard was run, which is the
assertion whose absence produced the earlier false negative.

| fixture | raw record actually scored | `<subject>` | `<baseline>` |
|---|---|---|---|
| rename of a 200+ line tracked document, credential appended to the destination | `R099` | **blocked, exit 1** | clean, exit 0 |
| the same through a real `git commit` | — | **refused; not in HEAD** | **committed; credential in HEAD** |
| rename whose destination is executable | new mode `100755`, `R099` | **blocked** | clean |
| typechange, symlink replaced by a regular file | `:120000 100644 … T` | **blocked** | clean |
| ordinary staged add of the identical bytes (control) | `A` | blocked | blocked |

Sizing was load-bearing and was checked: the old `--diff-filter=ACM` enumeration returns **zero**
paths for the rename fixture, confirming the record really is excluded rather than split into
delete-plus-add.

Three further properties, none of which the assigned items required but all of which the repair
could have broken:

- **Field pairing across a mixed staged set.** A single staging containing a deletion, a rename
  (`R100`/`R099`), an add and a typechange is parsed correctly: with the credential on the add only
  the add is named; with it on the rename destination as well, both are named and the deletion
  produces no false failure. One pathname per record would have mis-paired everything after the
  rename.
- **Copy.** A staged copy surfaces as `A` under this git's default configuration and as `C099` when
  copy detection is forced; blocked either way.
- **Non-ASCII names.** The attempt-one `C4` asymmetry has not regressed: byte-identical
  credential-bearing files under an ASCII name and an accented name are both blocked, in both modes.

## 6. STAGED-DELETION CONTROL — HOLD

A genuine `git rm` of a benign tracked file scores `D`, and `--staged` mode reports clean, exits 0,
and the commit succeeds through the hook. Identical at the baseline. D-059(3) is not foreclosed —
the widened enumeration excludes deletions only, and it does exclude them.

A newly staged gitlink (new mode `160000`) is likewise not a false failure: exit 0, no findings.

## 7. COPIED `test.sh` IDENTITY REFUSAL — HOLD

`scripts/test.sh` copied to a directory outside every repository — the premise asserted, not
assumed, with `git rev-parse` there reporting no repository — and invoked with shims on `PATH` for
seventeen expensive children, each of which drops a marker if it is reached:

```
exit = 5
  FAIL  the gate body received no supervisor-established repository root; refusing.
  GATE DID NOT REACH COMPLETION
  The body exited 2 without emitting its completion token.

  shims reached      : 0
  stages run         : 0
```

Both halves are visible: the body refuses on its own terms before any child, and the supervisor then
fails closed because no completion token arrived. Liveness control: the same shim directory on a
real gate run is reached four times, so a zero here means the shims were not reached rather than
that the mechanism is dead.

The refusal wording changed from attempt one's. It is still a dedicated identity refusal and it
still satisfies the attempt-one Case 4 scorer, which the harness run confirms.

## 8. ALL 16 ENTRY POINTS — HOLD

**Static.** All sixteen — fourteen `scripts/*.sh`, `scripts/test.sh` and `.githooks/pre-commit` —
carry the clearing line. No entry point invokes git by absolute path or through a variable, so a
`PATH` recorder sees every invocation. Exactly **two** git calls in the whole set sit before their
file's clearing line and deliberately use the caller's environment:

- `install-hooks.sh:23` — `CALLER_ROOT`, compared against the script's own root and then discarded.
- `.githooks/pre-commit:27` — `INVOKING_ROOT`, captured **before** the clearing line, compared, then
  discarded.

Both are legitimate identity inputs and neither is used to address any repository.

**Dynamic.** A recording `git` on `PATH` that logs which caller-provided variables are present and
then delegates to the real git verbatim. All sixteen entry points executed with all six variables
set to the subject's own paths, so every entry point runs normally and the census sees all of its
calls rather than only the ones before it fails:

```
267 git invocations recorded across 16 of 16 entry points
  0 body-level calls carried any caller-provided git variable
  0 entry points made no git call at all
```

The identity probes are exempt and what they carried is printed instead: twelve of the sixteen
scrub four of the five variables there and leave `GIT_PREFIX` present; `test.sh` and the hook scrub
all five. `GIT_PREFIX` is inert on this git — independently confirmed below — so this is a
consistency observation, not a finding.

Outcome assertions beside the census, because a census only sees hygiene:

- `check-review-scope.sh`: under five configurations the output is **byte-identical** to the
  no-variable control. At the baseline three of those five produce different output.
- `check-vendor-honesty.sh`: byte-identical under all five.
- `mutate.sh`'s dirty-tree refusal fires under all seven configurations; at the baseline two of them
  defeat it. Opposite control: on a clean tree the refusal does not fire, so the assertion is not
  satisfiable by a script that refuses unconditionally.

## 9. GATE SUPERVISOR AND COMPLETION-TOKEN BEHAVIOUR — HOLD

The bootstrap changed intentionally under D-061(3). Every preserved property was re-falsified with
probes built from a bootstrap **I extracted myself** from `scripts/test.sh`, not from the project's
harness.

| property | evidence |
|---|---|
| unprotected control is still corrupted | my own unprotected subject under an in-place shifting edit: exit 127, no completion, shell-level damage — **the probe is dangerous** |
| mid-run source edit cannot corrupt the body | the protected subject under the identical edit: body ran to completion, no syntax damage, supervisor exit 4 |
| read-only snapshot | from inside the body, writing the descriptor gives permission denied and `ftruncate` gives invalid argument |
| unlinked before execution | `${BASH_SOURCE[0]}` is `/dev/fd/9`; `ps` exposes no snapshot pathname; no temp file survives the run |
| exit 0 is not success | a body that skips the completion protocol and exits 0 is refused with exit 5 and the dedicated diagnostic |
| no environment leak to children | a grandchild of a real gate run sees **no** `SENTINEL_*` variable at all — the body clears both the token and the new root variable before any stage |

**Forging `SENTINEL_GATE_REPO_ROOT`.** A victim repository was built with nine decoy check scripts
and the variable pointed at it:

| invocation | victim decoys executed | Sentinel's tree read |
|---|---|---|
| ordinary `./scripts/test.sh` with the variable set | **0** | yes |
| ordinary invocation with the variable **and** a forged token | **0** | yes |
| Sentinel's gate by absolute path, caller inside the victim, variable set | **0** | yes |

The supervisor's `unset SENTINEL_GATE_REPO_ROOT` defeats all three. D-061(3)'s "with any
caller-supplied value cleared" is satisfied. One residual about direct body entry is recorded below.

The project's own immutability harness reports 10/10, and its control 2a — the unprotected subject
that must be corrupted or everything after it is meaningless — is genuinely corrupted. I confirmed
that independently rather than reading it off the harness.

---

## RESIDUALS — separate from the failure above

**R-A — `SENTINEL_GATE_REPO_ROOT` is accepted from the environment once the body is entered
directly.** `SENTINEL_GATE_TOKEN=… SENTINEL_GATE_REPO_ROOT=<victim> bash /dev/fd/N N<scripts/test.sh`
runs the body against the victim and executes its scripts. The only barrier is the structural
"`BASH_SOURCE` is `/dev/fd/*`" test, which a caller can satisfy directly. This is **not reachable by
any ordinary invocation shape** — all three above are defeated — it grants nothing over feeding the
same bytes to bash by hand, and it is the pre-existing property the bootstrap's own comment already
states about the token. Recorded so the silence is not read as coverage, not as a defect.

**R-B — a symlink named `scripts/test.sh` inside a foreign repository points the gate at that
repository.** `_gate_src` is built from `BASH_SOURCE[0]` and `pwd -P` on its **directory**, which
does not resolve a symlinked final component, so the established root is the foreign one and the
foreign repository's nine check scripts execute. A plain **copy** of `test.sh` at the same path
behaves identically, and a copy is unarguably correct — a copied entry point belongs to the tree that
contains it. The two cases are indistinguishable in effect, both require the caller to install a
file at that path in their own repository, and neither lets a foreign repository capture a run the
caller believed was a Sentinel run. Classified residual rather than a `12-F1` failure for that
reason; a repair that wants to close it would resolve the final component too.

**R-C — configuration injection is outside the cleared set and can hide untracked content.**
`GIT_CONFIG_COUNT` with `GIT_CONFIG_KEY_0=core.excludesFile` makes default mode print
`secret guard: clean` over an untracked credential-bearing file that it blocks with no variables set.
The cleared list covers five variables; git's configuration-injection variables are not among them.
**This is pre-existing — the baseline behaves identically — and it is arguably the declared
`--exclude-standard` scope decision reached by another route**, since a tracked ignore rule can
already do the same thing by design. It is outside the six configurations D-061(2) and the test
contract enumerate. Recorded as the nearest sibling the clearing does not reach.

**R-D — `GIT_OBJECT_DIRECTORY` fails closed, and loudly.** Pointed at an unrelated object store,
`--staged` mode refuses on every enumerated path rather than skipping any. That is the correct
direction, but it means the refusal count scales with the tree. Noted only so the shape is not
mistaken for the failure above; it is not a defect.

**R-E — `GIT_PREFIX` remains inert and is scrubbed inconsistently.** Independently confirmed inert on
git 2.50.1: it redirects neither the toplevel, nor the file list, nor a configuration write. Twelve
identity probes leave it present, `test.sh` and the hook remove it. Harmless today, and the
implementation says so in its own comment.

**R-F — attempt one's residuals `R2`, `R3` and `R5` were not probed.** They are DEFERRED by D-061(2).
`check-rename-gate.sh` was observed exiting 0 while printing `UNVERIFIED` during other probes, which
is `R5` still live; nothing was done about it and nothing should be read into the silence.

---

## WHAT THIS VERIFICATION DOES NOT ESTABLISH

- **No Solidity, and no completing gate run.** `contracts/lib` is unpopulated in the review worktree
  and an isolated clone has no `ts/node_modules`, so every gate run here ends at the supervisor's
  completion refusal whichever repository it gated. What `test.sh` and `mutate.sh` do *after* a
  successful identity resolution is not in evidence.
- **`mutate.sh` was exercised for identity and for its dirty-tree refusal only**, never for mutation
  behaviour.
- **The twelve check scripts' internal correctness** is untouched, exactly as the card excludes it.
- **One platform, one git.** git 2.50.1, bash 3.2, `core.quotePath` and `diff.renames` at their
  defaults. The failure above, `R1` and `12-F2` are all configuration-sensitive and all were measured
  at the defaults. The `GIT_INDEX_FILE` hand-off is git's documented hook contract rather than a
  local quirk, but it was measured on one version.
- **Concurrency** was not probed, and neither was a real linked-worktree layout — the subject is a
  clone, and `GIT_COMMON_DIR` was exercised as an injected variable.
- **Interactive commit forms** (`git commit -p`, `git commit --interactive`) were not driven; they
  use the same temporary-index mechanism as the two forms that were, so they are likely affected,
  and "likely" is the correct word because they were not measured.

## PROBE HYGIENE

Every probe ran against a private clone of the frozen commit under `<scratch>`, against a private
clone of the baseline commit, or against repositories created for the purpose under `<scratch>` and
removed afterwards. `HOME`, the global, system and XDG git configuration files and `PATH` were
redirected into the scratch area for every scored run. Git configuration was never written into a
repository this session did not create; the operator's global configuration is still unset and both
real trees still carry `core.hooksPath=.githooks` and are unmodified. The review worktree ends at
`f61ecca55557b7912cc26fddc87127cb0f6e2ebb` with no tracked modification. The primary repository was
read only, and written only to place this file.

---

**Verdict restated: FAIL on item 2.** Items 1 and 3–9 hold, most of them with a live pre-repair
discriminator proving the defect really was closed, and the two confirmed obligations `12-F1` and
`12-F2` are closed against every probe I could build. The repair is real work and the great majority
of it is sound. What it does not satisfy is the fail-closed half of A1's own invariant, in the one
component that stands between a credential and HEAD, through a line the repair itself added.
