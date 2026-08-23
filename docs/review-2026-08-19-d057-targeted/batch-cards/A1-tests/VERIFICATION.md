# A1 — INDEPENDENT VERIFICATION OF THE REPAIR

**Verifier:** an independent agent that wrote neither `a1-repo-identity.sh` nor the implementation
under it, and repaired nothing. Every probe below was built from scratch against the card's stated
requirements; no result was taken on the harness's word.

**Commit under verification:** `63c6906f538ee7e0c8cb54a80cb6b59bfeb3db21`
(*A-082: Batch A1 first implementation attempt*).
**Base SHA for pre-repair discrimination:** `f68d4d804de4d3b631e25fd539deecda5409f0d7`.
**Harness under verification (unmodified, hash checked in both trees):**
`a1-repo-identity.sh`, `sha256 54535b3b139ef9098753393872e39c932e25e0d861cfa14eb04e6f18c591122d`.

Paths are repository-relative. `<scratch>` stands for this session's temporary area outside the
repository; `<sentinel>` for the isolated clone of the subject.

---

## VERDICT: **FAIL**

Twelve of the thirteen required items hold, several of them convincingly. **Item 12 fails**, and it
fails on the card's own invariant rather than on a technicality: **caller-relative git operation
survived the repair in two demonstrated forms.** One of them needs no environment manipulation at
all and ends with Sentinel's own gate executing scripts belonging to a stranger's repository.

The committed harness is **green at this SHA** — I ran it: `REQUIRED failed: 0`,
`CONTROL failed: 0`, exit `0`. That is not contradicted by this document. Both failures below sit
inside blind spots the test author **declared in advance** in `COVERAGE.md` §1 and §5. The tests
are not overclaiming; the **implementation** is incomplete relative to the invariant, and the
harness is structurally unable to see it.

Nothing here is a regression. Both failures are pre-existing shapes the repair did not reach.

---

## PER-ITEM RESULTS

| # | Item | Result |
|---|---|---|
| 1 | non-ASCII credential filenames blocked in both modes, ASCII twin as control | **HOLD** |
| 2 | absent regular tracked file ⇒ index blob scanned | **HOLD** (but see R5) |
| 3 | genuine staged deletion still accepted | **HOLD** |
| 4 | V3-N1 refusal, count correct **and** exit non-zero | **HOLD** |
| 5 | unrelated directory / foreign repository still read Sentinel | **HOLD** (12 of 16) |
| 6 | `install-hooks.sh` makes no foreign-repository mutation | **HOLD** for the required fixture; broken under 12-F2 |
| 7 | pre-commit refuses before any decoy executes | **HOLD** |
| 8 | unchanged normal controls from Sentinel's root | **HOLD** |
| 9 | corrected Case 4 fails only on unresolved own-repository identity | **HOLD** (scorer weakness R3) |
| 10 | Case 2 succeeds from Case 4's caller directory | **HOLD** |
| 11 | `test.sh` refuses before doing work when copied out; exits 5 | **HOLD** |
| 12 | no caller-relative git operation survived the repair | **FAIL — two demonstrated** |
| 13 | no foreign repository configuration or files changed | **HOLD** |

**Foundry:** `contracts/lib` is unpopulated and `forge` cannot run. It bounded nothing. No Solidity
is involved in A1, and every probe below is git and shell only. The one place it could have mattered
— `test.sh` and `mutate.sh` at runtime — I reached by shimming the expensive children
(`forge anvil cast chisel npm npx node cargo curl wget gh python3 pip3 yarn pnpm ssh nc`) to a
recorder that does no work and returns 97, and by counting shim hits so that reaching one is scored
as an instrument failure rather than a result.

---

## 1. NON-ASCII CREDENTIAL FILENAMES — HOLD

Fixture built independently: two files in the clone whose contents are one identical line carrying a
64-hex value bound to a key-shaped identifier, under the names `probe/ascii-twin.md` and
`probe/café-twin.md`. Byte-identity of the *contents* verified with `cmp` (not by construction):

```
cmp probe/ascii-twin.md probe/café-twin.md   ->  BYTE-IDENTICAL
```

The names differ by exactly two bytes (`e` versus `\303\251`, confirmed with `od -c`), and the C4
precondition reproduces on this machine — `core.quotePath` is at its default:

```
git ls-files probe      ->  probe/ascii-twin.md
                            "probe/caf\303\251-twin.md"
git ls-files -z probe   ->  probe/ascii-twin.md
                            probe/café-twin.md
```

| guard | mode | ASCII twin | non-ASCII twin | exit |
|---|---|---|---|---|
| repaired | `--staged` | BLOCKED | **BLOCKED** | 1 |
| repaired | default | BLOCKED | **BLOCKED** | 1 |
| base SHA | `--staged` | BLOCKED | *clean* | 1 |
| base SHA | default | BLOCKED | *clean* | 1 |

The base-SHA rows are the discriminator and they behave oppositely, so the asymmetry the card names
as "the discriminator" is real and is closed at HEAD in **both** modes.

## 2. ABSENT TRACKED FILE ⇒ INDEX BLOB SCANNED — HOLD

Planted a credential-bearing file, committed it, deleted the working-tree copy, and confirmed the
deletion was **not** staged (`git status --porcelain` shows ` D`, `git diff --cached --name-only`
is empty). Default mode:

```
repaired guard : exit 1   BLOCKED probe/committed-cred.md
base SHA guard : exit 0   secret guard: clean
```

The index blob is read and the file is blocked. The discriminator is live.

## 3. GENUINE STAGED DELETION STILL ACCEPTED — HOLD

`git rm` of a benign tracked file (`docs/ablation-report.md`), staged as ` D `:

```
check-secrets.sh --staged   -> exit 0, "secret guard: clean"
check-secrets.sh (default)  -> exit 0, "secret guard: clean"
git commit through the hook -> exit 0, commit created, file deleted
```

No false failure. D-059(3) is not foreclosed by the repair.

## 4. V3-N1 — HOLD, BOTH HALVES

My own `git` shim on `PATH`, passing everything through except a selectable sabotage of
`--error-unmatch`. Baseline from Sentinel's root: `remediation surface: 105 file(s)`.

| shim mode | exit | surface printed | refusal line |
|---|---|---|---|
| inert passthrough (control) | 0 | 105 | — |
| `--error-unmatch` exits 128 | **1** | **105** | present |
| `--error-unmatch` exits 2 | **1** | **105** | present |
| `--error-unmatch` exits 1 (genuine absence) | 0 | 0 | absent — correct |
| base SHA, `--error-unmatch` exits 128 | **0** | **0** — *"all assigned"* | absent |

Both halves confirmed: **the count is correct (105 = baseline, not a discarded measurement) and the
exit is non-zero.** The exit-1 row proves the repair still distinguishes a genuine "deleted since"
from an instrument failure rather than blanket-refusing. The base-SHA row is the V3-N1 fail-open
reproduced verbatim.

## 5. UNRELATED DIRECTORY AND FOREIGN REPOSITORY — HOLD (12 OF 16)

A foreign repository was built holding two tracked files, one of them credential-bearing, so any
caller-relative read would be loud. All twelve executable check scripts, run from a directory inside
no repository and from inside that foreign repository, produced **byte-identical output and exit
status** to the run from Sentinel's root. A separate sweep confirmed no run mentioned the foreign
content. The foreign repository's `.git/config` and worktree hashed identically before and after.

**This item is 12 of 16 by construction, and that is where item 12's first failure lives.**
`scripts/test.sh` is not in the twelve — see below.

## 6. `install-hooks.sh` AGAINST A FOREIGN REPOSITORY — HOLD FOR THE REQUIRED FIXTURE

`core.hooksPath` read before and after in a scratch repository I created:

```
BEFORE: core.hooksPath = <unset>
  FAIL  refusing to install Sentinel hooks into another repository.
        Nothing was written. Run it from Sentinel if that is what you meant.       exit 2
AFTER : core.hooksPath = <unset>
  .git/config sha256 unchanged : YES
  worktree hash unchanged      : YES
```

The refusal is a dedicated refusal taken before any write, not a downstream `chmod` failure.
Controls: from Sentinel's own root it still succeeds; from a directory in no repository it succeeds
and configures Sentinel. **This guarantee does not survive 12-F2.**

## 7. PRE-COMMIT REFUSES BEFORE ANY DECOY EXECUTES — HOLD

Foreign repository with `core.hooksPath` pointed at Sentinel's `.githooks`, a credential staged, and
its own `scripts/check-secrets.sh` replaced by a decoy whose only job is to `touch` a marker file:

```
commit -> exit 1
  FAIL  pre-commit: repository identity mismatch; refusing before running anything.
  DECOY MARKER present after commit? NO-DECOY-NEVER-RAN
  decoy stdout in output?            NO
  credential landed in foreign HEAD? NO-NO-COMMIT
```

The marker never appears. Control: a matching repository with the same hook still commits (exit 0).

## 8. UNCHANGED NORMAL CONTROLS — HOLD

All twelve executable check scripts exit 0 from Sentinel's root with their expected first lines.
`install-hooks.sh` exits 0. The hook admits a benign commit and blocks a credential-bearing one.
`test.sh` refuses only where it should (item 11). Nothing normal regressed.

## 9. THE CORRECTED CASE 4 FAILS ONLY ON IDENTITY — HOLD

I rebuilt the fixture independently: all 16 entry points copied out of every repository with the
`scripts/` and `.githooks/` structure preserved, invoked with `HOME`, the global/system/XDG git
config files and `PATH` redirected into scratch, the git identity variables cleared, and the
expensive children shimmed.

Message census across all 16 outputs — the only thing any of them printed:

```
  14  this script is not inside the Sentinel repository; refusing.
   1  pre-commit: this hook is not inside the Sentinel repository; refusing.
   1  the gate was invoked outside the Sentinel repository; refusing.
   0  incidental lines (no such file, command not found, permission denied,
      not a git repository, cannot open)
   0  of 16 reached a shimmed child
```

Every entry point exits non-zero (15 exit 2, `test.sh` exits 5). **It does not pass for a wrong
reason**: no PATH shim was reached, no incidental error was produced, and no failed `cd` occurred.
The refusal comes from the identity block and from nowhere else. I attempted the wrong-reason routes
listed in the brief and none of them is what fires.

One weakness in the *scorer*, not in the implementation, is recorded as R3.

## 10. CASE 2 FROM CASE 4'S CALLER DIRECTORY — HOLD

Running the **originals** (inside Sentinel) from the **identical** directory the corrected Case 4
uses as its caller — the isolated layout itself — all twelve produce byte-identical output and exit
status to the run from Sentinel's root. Case 2 and Case 4 therefore differ only in *where the script
lives*, which is exactly what the adjudication said a valid Case 4 must achieve. The old
contradiction is genuinely gone.

## 11. `test.sh` COPIED OUTSIDE THE REPOSITORY — HOLD, AND IT EXITS 5

```
exit = 5
  FAIL  the gate was invoked outside the Sentinel repository; refusing.
        Run it as ./scripts/test.sh from a Sentinel worktree.
  GATE DID NOT REACH COMPLETION
  The body exited 2 without emitting its completion token.

  shimmed child reached?  NO
  any suite stage run?    NO
```

Both halves are visible: the **body** refuses on its own terms (exit 2, before any stage) and the
D-057(3) **supervisor** then fails closed because no completion token arrived, yielding 5. No work
was done first.

## 13. NO FOREIGN REPOSITORY CHANGED — HOLD

Ten scratch repositories were created during this verification. `core.hooksPath` and the local
config line count were read at the end of every probe:

```
foreign  fr2  decoy  third  mimic  mimic2  envtest  super  vh   ->  core.hooksPath <unset>
fr3                                                            ->  set BY THIS PROBE, deliberately,
                                                                   as the case-13 attack setup
```

No Sentinel entry point mutated any of them, **except** under 12-F2, where the mutation is the
finding. The operator's own configuration was not touched: the real repository and the review
worktree both still carry `core.hooksPath=.githooks`, and the global setting is still unset.

---

# 12. THE FAILURE — CALLER-RELATIVE GIT OPERATION SURVIVED

## 12-F1 — `scripts/test.sh` runs the CALLER's repository, and executes its scripts

**Severity: high. Needs no environment manipulation, no privileged access, and no unusual setup.**

`scripts/test.sh:168` derives identity from the caller and only the caller:

```
SENTINEL_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || SENTINEL_ROOT=""
if [ -z "$SENTINEL_ROOT" ] || [ ! -e "$SENTINEL_ROOT/scripts/test.sh" ] || [ ! -e "$SENTINEL_ROOT/.githooks/pre-commit" ]; then
```

The accompanying comment states the body "validates the repository it is standing in and REFUSES
rather than gating a tree it cannot establish is Sentinel." **The validation does not establish
Sentinel identity.** It is an existence test for two path names, which any repository can satisfy
with two empty files.

Demonstration. A brand-new unrelated repository was created containing nothing but an empty
`scripts/test.sh`, an empty `.githooks/pre-commit`, and four executable decoys named
`scripts/check-gate-immutability.sh`, `scripts/check-secrets.sh`, `scripts/check-rename-gate.sh` and
`scripts/check-label-prompt.sh`, each of which `touch`es a marker and exits 0. Then **Sentinel's own**
`scripts/test.sh` was invoked from inside it, by absolute path, with no variables set:

```
== gate immutability (D-056(b)) ==
CALLER DECOY check-gate-immutability EXECUTED by Sentinel's gate
== secret guard (A-007) ==
CALLER DECOY check-secrets EXECUTED by Sentinel's gate
== rename gate (D-016) ==
CALLER DECOY check-rename-gate EXECUTED by Sentinel's gate
== labelling-prompt freeze (D-011a) ==
CALLER DECOY check-label-prompt EXECUTED by Sentinel's gate

decoy marker files created: 4
```

**This is the same defect the pre-commit repair closed, still open in the gate.** The hook now
refuses before executing a caller-provided `scripts/check-secrets.sh` (item 7, verified). `test.sh`
executes four of them, prints Sentinel's own stage headers over the results, and treats the decoy
gate-immutability check's exit 0 as the immutability check passing.

Both halves of the invariant fail: the entry point operates on a repository that does not contain
it, and it reports Sentinel-shaped stage results it did not establish.

**Why the harness cannot see it.** `a1-repo-identity.sh:74` defines `RUNNABLE` as the twelve check
scripts; `test.sh` is in `STATIC_ONLY`. Cases 2 and 3 — the two cases that would catch this — loop
over `RUNNABLE` only. Case 4 does exercise `test.sh`, but its fixture places the copy **outside every
repository**, where `git rev-parse` fails and the refusal fires correctly. The one fixture that would
catch it — a *foreign repository* that satisfies the two-path structural test — is in no case.
`COVERAGE.md` §1 declares this gap honestly and in advance.

**Unambiguous fix.** `test.sh`'s body must establish identity, not shape. The supervisor half of the
bootstrap *does* have a real path (`_gate_src` at `test.sh:59` is built from `BASH_SOURCE`), so the
resolved Sentinel root can be computed there and passed to the body — through the environment
alongside the existing token, or on `argv` — and the body must then require its `git rev-parse`
answer to **equal** that value rather than merely look like a repository. Do not widen the structural
test with more path names; any list of path names is satisfiable by a decoy.

## 12-F2 — every body-level `git` call still inherits the caller's exported git environment

**Severity: medium. Needs `GIT_DIR` (and for the worst case `GIT_WORK_TREE`) exported.**

The identity block of all fourteen `scripts/*.sh` and the hook resolves the root with

```
env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR git rev-parse --show-toplevel
```

so the author demonstrably knew these variables override directory context. **The scrub is applied
to the identity probe and to nothing else.** After `cd "$ROOT"`, every working `git` call runs with
the variables still exported. A per-file census of git invocations outside comments:

| file | body-level git calls after the identity block | scrubbed? |
|---|---|---|
| `check-review-scope.sh` | `ls-files -z`; `rev-parse --verify`; `diff -z --name-only`; `ls-files --error-unmatch` | no |
| `check-secrets.sh` | `ls-files -s -z`; `diff --cached -z`; `ls-files --others`; `show ":$pth"` ×2 | no |
| `check-vendor-honesty.sh` | `ls-files`; `ls-files --others --exclude-standard` | no |
| `check-rename-gate.sh` | `config --get remote.origin.url` | no |
| `mutate.sh` | `status --porcelain -- ts/src contracts/src` | no |
| `install-hooks.sh` | `rev-parse --show-toplevel` (caller); `git -C "$SENTINEL_ROOT" config` | no |
| `.githooks/pre-commit` | `rev-parse --show-toplevel` (caller) | no |
| the other nine | none | — |

Demonstrated consequences, all measured:

**(a) The credential guard reports clean over a live credential.** A credential-bearing file was
placed in the Sentinel clone. Same command, same directory, one variable pair added:

```
./scripts/check-secrets.sh                            -> exit 1  BLOCKED SENTINEL-LIVE-CREDENTIAL.md
GIT_DIR=<decoy>/.git GIT_WORK_TREE=<decoy> ./scripts/check-secrets.sh
                                                      -> exit 0  "secret guard: clean"
```

**(b) The vendor-honesty guard certifies the wrong tree.** Under the same variables it prints its
whole mechanical-conditions block, every row `ok`, exit 0 — measured against the decoy repository,
which contains one file. This is evidence used for Gate 5.

**(c) `install-hooks.sh` writes into a foreign repository and calls it success.** The repair's
protection is `git -C "$SENTINEL_ROOT" config core.hooksPath .githooks` — and `git -C` is exactly
what `GIT_DIR` overrides. With `GIT_WORK_TREE` pointed at the Sentinel clone, the caller's repository
*reports* as Sentinel's root, so the identity comparison matches:

```
VICTIM core.hooksPath BEFORE = <unset>
  cd <sentinel> && GIT_DIR=<victim>/.git GIT_WORK_TREE=<sentinel> ./scripts/install-hooks.sh
  -> exit 0   "hooks installed: core.hooksPath=.githooks"
VICTIM core.hooksPath AFTER  = .githooks      *** FOREIGN REPOSITORY MUTATED ***
SENTINEL core.hooksPath      = <unset>        *** the one repository it should have written ***
```

This is the exact prohibition in D-060(2) — "must never install Sentinel hooks into a foreign one" —
violated with a success message and exit 0.

**Honest bounding of the trigger, measured rather than assumed.** On git 2.50.1 here, ordinary hook
execution does **not** export `GIT_DIR`; it exports `GIT_INDEX_FILE=.git/index`, which is *relative*
and therefore re-resolves benignly after the `cd` to Sentinel's root. `git submodule foreach` exports
`GIT_DIR=.git`, also relative and also benign. The variables arrive **absolute** — and therefore
dangerous — under `git filter-branch`, and under any wrapper, CI step, container entrypoint or shell
that exports them explicitly. So this is not reachable by simply committing; it is reachable by a
wrapper, and it is trivially reachable by anyone who wants it.

`COVERAGE.md` §5 lists "`git worktree` / `GIT_DIR` / `GIT_WORK_TREE` identity confusion" as not
probed. It is not probed, and there is something there.

**Unambiguous fix.** Neutralise the inherited environment once, immediately after the identity block
in every entry point, rather than per call — `unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE
GIT_COMMON_DIR GIT_PREFIX` after `cd "$ROOT"` succeeds. The hook is the one place that must keep
reading the caller's context to compute `INVOKING_ROOT`, so it should capture that value first and
unset afterwards, before `exec`. `git -C` is not a substitute and must not be relied on again.

---

## RESIDUALS — separate from the failures above

**R1 — staged renames and typechanges fall out of `--diff-filter=ACM`, and a credential reaches
HEAD through the hook.** Inside the card's declared **symbol** boundary (`git diff --cached` in
`check-secrets.sh`, line 138). Pre-existing; the base SHA has the same filter. Not a regression, and
**not** named by any of the thirteen cases.

`docs/ablation-report.md` was renamed with one credential-bearing line appended and staged:

```
git diff --cached --raw          -> :100644 100644 ... R099  docs/ablation-report.md  docs/ablation-report-renamed.md
git diff --cached -z --name-only --diff-filter=ACM   -> (empty)
./scripts/check-secrets.sh --staged                  -> exit 0  "secret guard: clean"
git commit                                           -> exit 0  "secret guard: clean"
   credential now in HEAD.
```

Default mode still blocks it, because the working-tree copy is present — so the exposure is the
`--staged` path and therefore the hook. A staged **typechange** (symlink replaced by a
credential-bearing regular file, status `T`) behaves identically: excluded, clean, exit 0.

`COVERAGE.md` §5 flags renames as configuration-sensitive rather than proven safe, which was the
right call. `PROBES.md` D2's negative result — "rename detection is not applied here, so the new
path surfaces as `A`" — **does not reproduce**: D2's fixture was small enough that appending the
credential dropped similarity below the rename threshold and split the change into `D`+`A`. On a
realistic file it scores `R099` and is excluded. The suggested repair is to enumerate with
`--diff-filter=d` (exclude deletions only) rather than allow-listing `ACM`, so an unrecognised status
letter fails toward being scanned instead of toward being skipped — but this is a scope call for
John, since it is a new defect surface rather than an A1 case.

**R2 — the C4 defect is still live in `check-vendor-honesty.sh`.** Its `artifacts()` enumeration
(lines 191–201) is `{ git ls-files ; git ls-files --others --exclude-standard } | sort -u | … |
[ -f "$f" ]`. Neither call uses `-z`, so `core.quotePath` octal-escapes a non-ASCII name and the
`[ -f ]` test is false. Reproduced:

```
files on disk: ascii.md  café.md
  KEPT    ascii.md
  DROPPED "caf\303\251.md"   <- never scanned
```

`check-vendor-honesty.sh` is one of the sixteen declared entry points but is outside the card's
**symbol** boundary, which names only `check-review-scope.sh` and `check-secrets.sh`. So this is
correctly out of A1's scope — recorded because the guard is already INADMISSIBLE as evidence for
its supplementary §7.2 condition under D-059(1), and a repair of it should carry the `-z`
enumeration across rather than re-derive it.

**R3 — the corrected Case 4 scorer accepts one wrong reason it should reject.** `is_ident_refusal`
requires a refusal verb plus one of a list of conditions, and that list includes `repository root`.
The implementation's **failed-`cd`** message —

```
  FAIL  cannot enter the Sentinel repository root; refusing.
```

— matches. My adversarial probe of the scorer accepted it while correctly rejecting all nine other
lines I fed it (missing file, command not found, `fatal: not a git repository`, a shim report, a
generic failed `cd`, a bare `refusing.`, and three genuine non-identity refusals the scripts really
print). The brief named "not on a failed cd" as a wrong reason to check for; **at this SHA that
branch never fires**, so Case 4 does not currently pass for it, and item 9 holds. But a future
implementation whose only refusal is a failed `cd` would pass Case 4. Narrowing `repository root` to
something like `(inside|outside|identity of) the .* repository root` would close it. This is a
weakness in a test, not in the repair.

> **DISPOSITION — John, 2026-08-23.** Item 9's HOLD in this file rests on a scorer its own
> author flagged as weak (the paragraph above). Do not take that HOLD at full strength. R3 is a
> permanent recorded limit. The frozen A1 harness is not touched. Reversal: if item 9's
> verdict is ever load-bearing for a decision, the scorer weakness must be resolved before
> that decision, not after.

**R4 — an open fork was resolved by the implementer and attributed to a ruling that does not contain
it.** `check-secrets.sh:186–189` reads:

```
# D-060's ruling: absent working-tree copy, index blob present -> scan the INDEX BLOB.
```

`COVERAGE.md` §4 states that exact question is "a narrower fork still open and John's", offering (a)
scan the index blob and (b) treat it as a legitimate deletion. The implementation chose (a). D-060's
entry in `docs/decisions.md` contains **zero** occurrences of the word "index" — I counted. The
behaviour item 2 verifies is therefore correct-as-built but **not** ruled, and the comment asserting
otherwise should be corrected whichever way John decides. Flagging rather than resolving.

**R5 — `check-rename-gate.sh` exits 0 on `UNVERIFIED`.** From Sentinel's root it printed
`rename gate: UNVERIFIED — could not read visibility for <slug> (auth? network?)` and exited **0**.
That is a fact it did not establish, reported without refusing. `COVERAGE.md` §3 already raises the
adjacent no-remote shape and correctly rules it a D-016 question rather than an A1 one. Recorded for
the same reason: so the silence is not read as coverage.

---

## WHAT THIS VERIFICATION DOES NOT ESTABLISH

- **No Solidity was exercised.** `contracts/lib` is unpopulated and `forge` cannot run. A1 needs
  none, and the two entry points that drive Foundry were reached with shimmed children, so what
  `test.sh` and `mutate.sh` do *after* a successful identity resolution is out of evidence here.
- **`mutate.sh` was exercised for identity only**, not for mutation behaviour.
- **One platform, one git.** git 2.50.1, bash 3.2, `core.quotePath` and `diff.renames` at their
  defaults. R1 and 12-F2 are both sensitive to configuration and both were measured at the defaults.
- **The twelve check scripts' internal correctness** is untouched by this document, exactly as the
  card excludes it.
- **Concurrency** was not probed.

## PROBE HYGIENE

Every probe ran against a private clone of the frozen commit under `<scratch>`, or against scratch
repositories created for the purpose and deleted afterwards. The review worktree was left at
`63c6906…` with no tracked modification. The primary repository was read only, and written only to
place this file.

---

**Verdict restated: FAIL on item 12.** Items 1–11 and 13 hold, and items 1, 2, 4, 7, 9, 10 and 11
hold with live pre-repair discriminators showing the defect really was closed. The repair is real
work and most of it is sound. What it does not yet satisfy is the invariant's own first sentence, in
the one entry point that runs everything else.
