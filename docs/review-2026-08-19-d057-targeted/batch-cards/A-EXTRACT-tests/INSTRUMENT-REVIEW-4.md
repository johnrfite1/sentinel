# INSTRUMENT-REVIEW-4 — fourth independent review of the A-EXTRACT harnesses

## VERDICT: FAIL

**Subject**: `a-extract.sh` (sha256 `17d200d1…6220`) and `a-extract-gate.sh` (sha256
`9fd5790e…6e25`) as committed at `d1fa16f805c2ba9beb4c9840d0def323a9f4d375`, branch
`step-3/isolated-signer`. Both on-disk files were confirmed byte-identical to their committed blobs
before any probe was run.

**Reviewer**: fourth pass. I authored none of this and reviewed none of it before. I read
`INSTRUMENT-REVIEW.md`, `-2` and `-3` for their claims and residual lists, and I edited none of them.

---

## The verdict in one paragraph

**The three defects `INSTRUMENT-REVIEW-3` reported are genuinely closed, and I could not reopen
them.** Object replacement is neutralised on both doors in both harnesses; the widened whole-tree
provenance digest is a real detector that I made fail on demand and could not make pass over a
differing tree; the counter fix holds against every malformed verdict I could construct, in both
harnesses, in situ as well as at unit level; the eleven earlier falsifications all still hold; and the
figures are exactly what the commit claims — I independently re-measured `21 of 52` REQUIRED /
`74 of 74` CONTROL for `a-extract.sh` and **`7 of 7` REQUIRED / `10 of 10` CONTROL, exit 0** for
`a-extract-gate.sh`, both at `bb664c6…`. **The FAIL is for a fourth door of the same shape as the
third, which this commit did not close and which no control in either harness can see:
`GIT_TEMPLATE_DIR`.** It is unscrubbed caller environment. It needs no write to the measured
repository and no edit to the harness. `git init` and `git clone` both copy a caller-supplied
template's **`config` and `hooks/`** into every repository the harnesses create — which is exactly
the repository-local configuration layer that `_scrub_git_config_env`, `GIT_CONFIG_GLOBAL/SYSTEM`
and `GIT_CONFIG_NOSYSTEM` exist to keep the caller out of. **Measured, on the committed
`a-extract.sh`, against a clean private clone: an injected `core.fsmonitor` rewrote
`scripts/check-vendor-honesty.sh` inside 16 of the harness's own subject repositories; the
harness's own consumer log records those tampered bytes executing 16 times; and the run printed
`CONTROL : 74 of 74 held`, `P3-provenance` PASS, and all four execution witnesses PASS.** The same
variable puts a `post-checkout` hook into `a-extract-gate.sh`'s measured clone, where the gate then
executes whatever the hook left behind and `P3-provenance` still passes. A second, independent
finding is recorded below: the gate harness's `P3-provenance` is structurally incapable of detecting
object replacement — measured — which corrects a statement in `INSTRUMENT-REVIEW-3` and means that
control is a passenger for the very class this commit is about.

---

## Conventions, and they are load-bearing

* **Every probe has a control that must move.** Where a probe reports "inert", the mechanism was
  first shown to be potent against the same command outside the harness. Where a fix is claimed to be
  load-bearing, a **scratch copy** of the harness with that one line removed was run against the same
  repository. Those copies live under my scratch directory. **No file in this repository was modified
  by this review except this document.**
* **Output, not exit status.** Every count below is read from the printed matrix
  (`A_EXTRACT_MATRIX_OUT`) and the summary block, never inferred from `$?`.
* **My own repository.** Every adversarial ref, config, attribute and template was installed in a
  private clone I created under a scratch directory. The source repository was never modified and
  never had git configuration written into it. The one exception is item 8: the full gate-harness
  re-measurement was run against the live repository, which that harness only reads — it clones and
  copies outward, and asserts its own `Z-clean`, which passed.
* **`HOME`, `XDG_CONFIG_HOME`, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM`, `GIT_CONFIG_NOSYSTEM=1`**
  redirected for every scored run and every probe.
* Machine-specific absolute paths are written `<scratch>` / `<repo>`.
* Environment: git `2.50.1`, bash `3.2.57`, node `v26.3.0`, python `3.9.6`.

---

## Per-item results

| # | Item | Result |
|---|---|---|
| 1 | Replacement, both doors, and the control itself | **HELD for `a-extract.sh`** — the expected side really is pinned, and the control really is a detector, proved with two paired copies. **FAILS for `a-extract-gate.sh`** — its `P3-provenance` cannot detect this class at all (`F2-4`) |
| 2 | Pin asymmetry, 2 vs 0 | **CONFIRMED, and the count in my charge is one too high**: `a-extract.sh` pins `--no-replace-objects` on **2** commands, not 3 — the third occurrence is a comment. `a-extract-gate.sh` pins **0**. It is protected by the environment export, plus the accident that `git clone`'s default refspec does not carry `refs/replace/*` — *incidentally*, with no detector behind either |
| 3 | Whole-tree provenance digest | **HELD.** Made to FAIL over a differing tree by two independent routes; PASSES untouched; **I could not make it pass over a differing tree.** Three uncovered surfaces recorded as residuals, all inert at this subject |
| 4 | The counter fix as a class | **HELD in both harnesses.** 13 of 15 malformed verdicts → FAIL **and counted**; only a literal `0` passes. Reproduced **in situ** in both harnesses, not only at unit level |
| 5 | The eleven previous falsifications | **ALL HELD.** 15 refusal inputs, every one exit 2 with **zero scored verdicts**; the 40-hex branch cannot redirect; config injection inert with potency proved first; the witness still discriminates |
| 6 | Residuals `R3-3`, `R4-3`, `R5-3` | `R3-3` **narrowed** (a redirected odb cannot substitute bytes — measured); `R4-3` **half closed** (file-dropping now detected; symmetric conversion still uncovered); `R5-3` **open, reproduced verbatim** |
| 7 | Nothing else moved | **ONE unaccounted movement**: `hdr "SUBJECT IDENTITY"` and its `identity_block` call were deleted from `a-extract.sh`. Everything else is exactly as claimed, verified by running the previous revision's harness side by side: case ids, kinds and statuses byte-identical, **control delta zero** |
| 8 | Gate harness re-measured at `bb664c6` | **RE-MEASURED BY ME: `7 of 7` REQUIRED, `10 of 10` CONTROL, exit 0.** The author's figures reproduce |

---

## `F1-4` — `GIT_TEMPLATE_DIR`: THE CALLER STILL OWNS THE CONFIG OF EVERY REPOSITORY THE HARNESSES CREATE, AND THROUGH IT THE BYTES THAT RUN

### Where the isolation claim stops

The isolation block says *"Caller configuration injection is neutralised before the first git
invocation; the keys are enumerated from the environment rather than assumed to stop at a small n."*
It enumerates `GIT_CONFIG_KEY_*` / `GIT_CONFIG_VALUE_*`, unsets `GIT_CONFIG_COUNT` and
`GIT_CONFIG_PARAMETERS`, redirects `GIT_CONFIG_GLOBAL` / `GIT_CONFIG_SYSTEM` to empty files, sets
`GIT_CONFIG_NOSYSTEM=1`, and unsets `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_COMMON_DIR`,
`GIT_PREFIX` and `GIT_REPLACE_REF_BASE`. That is the complete list; I checked it line by line in both
files.

**Both harnesses then create repositories, and creating a repository is a configuration entry point.**
`a-extract.sh` runs `git init` for every subject (`subject()` — P0, the generator subject and every
mutant). `a-extract-gate.sh` runs `git clone` for `BASECOPY`. `GIT_TEMPLATE_DIR` appears **nowhere in
either harness.**

### Measured — both creation paths copy the caller's template, config included

```
git init  : template config copied?  user.name=injected-by-template   core.fsmonitor=/bin/echo
            hooks/post-checkout installed: 1
git clone : template config copied?  filter.x.clean = tr a-z A-Z
            hooks/post-checkout installed: 1
```

Repository-local config is the one layer the isolation block does not reach, and it does not need to
outrank anything — it is simply read. `core.fsmonitor`, `filter.*.clean/smudge`, `core.hooksPath`,
`core.attributesfile` and `core.autocrlf` are all reachable this way.

### Measured — a full scored `a-extract.sh` run executing tampered bytes with every control green

The committed harness, unmodified, against my clean private clone, subject `bb664c6…`. The only
difference from the baseline run is one exported variable pointing at a template whose `config`
carries `core.fsmonitor = <script>`. The script leaves `s-p0` alone and rewrites
`scripts/check-vendor-honesty.sh` in the other subjects, inserting a line that prints a marker, so
the *harness's own* consumer log becomes the evidence that tampered bytes ran.

```
  REQUIRED : 21 of 52 held
  CONTROL  : 74 of 74 held
  rc = 1

  subjects tampered by the injected fsmonitor          : 16
  "REVIEW4-EXECUTED-TAMPERED-BYTES" occurrences in the
  harness's own consumer-output.txt                    : 16

  P3-provenance                CONTROL  PASS
  Z-check-type-strings.sh      CONTROL  PASS
  Z-check-eval-codes.sh        CONTROL  PASS
  Z-check-vendor-honesty.sh    CONTROL  PASS
  Z-test_verifier.py           CONTROL  PASS
  Z-clean / Z-gate5 / Z-signed CONTROL  PASS
```

**Sixteen consumer executions ran bytes that are not in the requested commit, and the instrument
reported that every one of its seventy-four controls held.** The injected line was a harmless `echo`
precisely so the run would stay legible; nothing about the mechanism limits it to that.

### The witness is a partial detector, and what decides it is timing

The first version of this payload fired at subject-creation time — inside `subject()`'s `git add -A`,
**before** `_witness` records the file's hash. That run was **caught**:

```
  CONTROL  : 73 of 74 held      rc = 2
  FAIL  Z-check-vendor-honesty.sh   (distinct witness hashes = 2)
```

Moving the payload one index-refresh later — into `run_vh`'s own `git add -A`, which happens **after**
`_witness` has recorded the hash and **before** the script runs — produced the fully green run above.
So the execution witness, which the harness rightly calls its strongest property, does catch this
class **when the tamper lands before the witness call**, and cannot when it lands after. That is a
real credit to the design and a precise statement of its limit; it is not a defence that can be
relied on, because the attacker chooses the moment.

### Measured — the gate harness's clone, tampered, with `P3-provenance` PASS

`a-extract-gate.sh` lines 272–280 reproduced verbatim on a miniature repository (`clone
--no-hardlinks --local`, then `checkout -q <oid>`, then `rev-parse HEAD`), with a template
`post-checkout` hook that rewrites a tracked file once the subject is checked out:

```
=== gate-harness sequence WITHOUT the template ===
  checkout ok
  clone HEAD (== _clone_head): af06958a…82bc6
  payload.txt in the measured worktree: ORIGINAL

=== same sequence WITH caller GIT_TEMPLATE_DIR ===
  checkout ok
  clone HEAD (== _clone_head): af06958a…82bc6
  payload.txt in the measured worktree: TAMPERED PAYLOAD
  true bytes at the subject:            ORIGINAL
  injected local config: injected
  P3-provenance would compute: _clone_head='af06958a…82bc6' vs SUBJECT_SHA='af06958a…82bc6'
```

The clone is checked out at the requested oid, its `HEAD` says so, and the bytes the gate then
executes are not that commit's. `P3-provenance` is that harness's only provenance control, it compares
`_clone_head` to `SUBJECT_SHA`, and both sides are correct here — so it passes. There is no tree
digest, no witness and no cleanliness assertion over `BASECOPY` anywhere in that harness; the run
would print `CONTROL : 10 of 10 held`. `git clone` runs `post-checkout` for its own initial checkout
as well as for the harness's explicit one, so a careless payload dirties the worktree and makes the
harness's `checkout` fail into `die … exit 2` — **that is luck, and the demonstration above is the
one `if` it takes to avoid it.**

### Why this is a FAIL and not a residual

It is the same reachability class the project already ruled a FAIL at `INSTRUMENT-REVIEW-3`'s `F1b`:
**caller environment alone, no repository write, no harness edit, every control green.** It defeats an
isolation property this harness spends code claiming. And it is not only adversarial —
`GIT_TEMPLATE_DIR` is a variable people really do export in a shell profile to get their own hook
templates, so an ordinary environment can put hooks and config into the measured repositories with
nothing in the output saying so.

The fair counter-argument is that a caller who can set the environment can often do more, and that at
some point the threat model has to stop — `R7-4` names the outer edge. **Where that line falls is
John's to draw, not mine.** What I can say is that this door is *inside* the line the harness itself
drew: it scrubs `GIT_REPLACE_REF_BASE` and the whole `GIT_CONFIG_*` family for exactly this reason,
and `GIT_TEMPLATE_DIR` reaches the same destination by a route the scrub does not cover.

---

## `F2-4` — THE GATE HARNESS'S PROVENANCE CONTROL CANNOT SEE THE CLASS THIS COMMIT CLOSED

Separate from `F1-4`; it would stand without it.

`a-extract.sh`'s repair has two layers: the environment scrub, **and** a control whose expected side is
pinned on the command so the control itself detects the hole. `a-extract-gate.sh` received only the
first. Its `P3-provenance` is:

```
_clone_head="$( cd "$BASECOPY" && git rev-parse HEAD 2>/dev/null )" || _clone_head=""
check CONTROL P3-provenance "$([ "$_clone_head" = "$SUBJECT_SHA" ] && [ "${#SUBJECT_SHA}" = "40" ] && \
      [ "$_odb_type" = "commit" ] && echo 0 || echo 1)"
```

**Neither side of that comparison can be moved by object replacement — which is exactly why it cannot
detect object replacement.** Measured on the harness's exact checkout form, in a clone of a source
carrying a branch literally named the subject oid (`git clone` copies `refs/heads/*` to
`refs/remotes/origin/*` verbatim — `INSTRUMENT-REVIEW-3`'s `F1b` route):

```
  caller base, NOT neutralised : HEAD=bb664c626d59  test_verifier.py=9ebb7fa781fc  tracked=533
  caller base, NEUTRALISED     : HEAD=bb664c626d59  test_verifier.py=924749d5c362  tracked=500
  no replacement at all        : HEAD=bb664c626d59  test_verifier.py=924749d5c362  tracked=500
```

`HEAD` stays at the requested subject in all three rows. The worktree is another commit's tree in the
first — 533 tracked paths instead of 500 — and `_clone_head == SUBJECT_SHA` holds there, so
`P3-provenance` **passes**. `INSTRUMENT-REVIEW-3` recorded that `git rev-parse HEAD` in that clone
returns the replacement target; on git `2.50.1` with the harness's exact `git checkout -q "$SUBJECT_SHA"`
it does not. **The control is blinder than the third review believed, so restoring `_clone_head` —
which was correct and necessary — restored a control that was never able to catch this.**

What protects the gate harness today is one line plus one accident of `git clone`'s default refspec.
That is enough to keep the door shut now. It is not enough to make the harness report when the door is
open, which is the standard `a-extract.sh` was held to and met.

---

## Item 1 — replacement, both doors, and the control itself (`a-extract.sh`: HELD)

**Potency first**, in my clone, with `refs/replace/bb664c6… -> d1fa16f…` and the same mapping copied
under `refs/myreplace/`:

```
archive entries, replacement live          : 610       ls-tree blobs, replacement live      : 531
archive entries, GIT_NO_REPLACE_OBJECTS=1  : 574       ls-tree blobs, --no-replace-objects  : 498
caller GIT_REPLACE_REF_BASE, unpinned      : 531       caller base, pinned on the command   : 498
```

**Then the committed harness**, same repository:

| run | door | `P3-provenance` | paths | REQUIRED | CONTROL | rc |
|---|---|---|---|---|---|---|
| baseline | none | PASS `d0a672e8e34a…` | 498 | 21 of 52 | 74 of 74 | 1 |
| A2 | `refs/replace` in the repository | PASS `d0a672e8e34a…` | 498 | 21 of 52 | 74 of 74 | 1 |
| A3 | caller `GIT_REPLACE_REF_BASE` | PASS `d0a672e8e34a…` | 498 | 21 of 52 | 74 of 74 | 1 |

All three matrices byte-identical (`sha256 1195c3e6…fa64`). A fourth run combining both replacement
doors with `GIT_CONFIG_*` and `GIT_CONFIG_PARAMETERS` injection and repository-local
`core.warnAmbiguousRefs=false` produced the same byte-identical matrix.

**Detector or passenger?** Two scratch copies, one line different each:

| copy | change | `P3-provenance` | paths | CONTROL | rc |
|---|---|---|---|---|---|
| `p1` | env scrub removed, pins kept | **FAIL** `32be7e969237…` | **531** | 72 of 74 | 2 |
| `p2` | env scrub **and** the `ls-tree` pin removed | **PASS** `32be7e969237…` | **531** | 73 of 74 | 2 |

`p1` proves the control detects. `p2` reproduces the author's stated measurement exactly: with the
expected side unpinned, **both sides move together and the control passes over another commit's
tree.** The pin is load-bearing, and the author's account of why is correct.

`p2` also shows something worth keeping: the only other control that moved in either row is
`Z-test_verifier.py`, and it is the **only one of the four witnesses that could** — the other three
consumer scripts are byte-identical between `bb664c6…` and `d1fa16f…`, so three witnesses stayed green
over a wholly substituted tree. The witness column would have caught 1 of 4. **The whole-tree digest
is what carries this load**, which is the case for having widened it.

**Other comparisons whose two sides could co-move.** I enumerated every scored comparison in
`a-extract.sh`. `Z-gate5` anchors all three of its hashes to a hardcoded constant
(`GATE5_PINNED=c9034750…`), so a moved side mismatches the constant and fails closed. `Z-signed`
compares a live-tree `shasum` against `git show "$PRE_REPAIR_SHA:…"` with **no on-command pin** — its
live side is not movable by replacement, so it is protected by the environment export alone. Same
asymmetry as the gate harness, smaller surface; `R4-4`.

---

## Item 3 — the whole-tree provenance digest

**It fails when the archived tree differs.** Two routes, neither of which edits the harness:

* **Object replacement with the scrub removed** (`p1`): 531 paths, `32be7e969237…`, FAIL, exit 2.
* **`.git/info/attributes` with `README.md export-ignore`** — `INSTRUMENT-REVIEW-3`'s `R4-3`, the
  vector that previously dropped files from the archive of the exact requested oid unnoticed. Potency:
  `574 -> 566` archive entries. Harness:

```
case P3-provenance CONTROL  FAIL  … the archived tree matches that commit's tree over all
                                   491 blob paths (dc88c71433a7…)
  CONTROL : 73 of 74 held      rc = 2
```

**It passes when the tree is left alone**: 498 paths, `d0a672e8e34a…`, on every clean run.

**I could not make it pass over a differing tree.** What I tried and what each turned into:

* **Extra or missing paths** — the path list is inside the digest; both directions move it.
* **`export-subst`** — changes content, so `hash-object` yields a different oid; detected.
* **Empty directories** — git does not track them; nothing to cover.
* **Gitlinks** — excluded from the expected side by design and not archived; there are **2** at the
  subject. Not bytes the archive delivers. `R2-4`.
* **Symlinks** — `find . -type f` omits them while `ls-tree` lists them as blobs, so a symlink in the
  tree fails the control **closed**. There are **0** symlinks at the subject (mode census: 479 ×
  `100644`, 19 × `100755`, 2 × `160000`). `R1-4`.
* **Executable-bit-only change** — `awk '$2=="blob"{print $4"\t"$3}'` drops the mode column and
  `hash-object` never sees a mode, so **a mode-only difference is invisible to the digest.** 19 of the
  498 blobs at the subject are `100755`. I found no route that makes `git archive` emit a mode the
  tree does not record, so this is a gap in the claim rather than an exploit. `R1-4`.
* **Attribute-driven conversion that round-trips** — the one genuinely uncovered class. Measured
  synthetically: with `* text eol=crlf` in force, `git archive` writes CRLF into the extracted file
  while `git hash-object` cleans it straight back to **the identical blob oid** (`c0d0fb45…` on both
  sides). Both sides move together; the control passes over a snapshot whose bytes are not the
  commit's. Reaching it needs attributes visible to **both** `git archive` in the source and
  `git hash-object` in `$P0`: the subject's own tree (**no `.gitattributes` at `bb664c6…`** — checked),
  the system attributes file (`git var GIT_ATTR_SYSTEM` = `/etc/gitattributes`, **absent here**, and
  root-owned if created), or caller-injected repository config — which is `F1-4`. `GIT_ATTR_NOSYSTEM`
  is still unset and `git hash-object` still runs without `--no-filters`. `R3-4`.

---

## Item 4 — the counter fix, as a class

**Unit level, both harnesses**, `check()` lifted verbatim (`a-extract.sh` 188–210,
`a-extract-gate.sh` 136–159) with the real counters and the real summary arithmetic:

| verdict | `a-extract.sh` | `a-extract-gate.sh` | counted |
|---|---|---|---|
| `""` (empty) | FAIL | FAIL | yes |
| `" "` (space) | FAIL | FAIL | yes |
| tab | FAIL | FAIL | yes |
| `00` | FAIL | FAIL | yes |
| `-0` | FAIL | FAIL | yes |
| `0x0` | FAIL | FAIL | yes |
| `+0` | FAIL | FAIL | yes |
| `0\n0` (multi-line) | FAIL | FAIL | yes |
| `*` (glob-shaped) | FAIL | FAIL | yes |
| `zero` | FAIL | FAIL | yes |
| 64 zero characters | FAIL | FAIL | yes |
| unbound variable in the subshell under `set -u` | FAIL | FAIL | yes |
| `expr 1 / 0` (errored substitution) | FAIL | FAIL | yes |
| `0` | PASS | PASS | — |
| `$(printf '0\n')` | PASS | PASS | — |

13 of 15 fail, every failure is counted, and both harnesses then report `WOULD EXIT 2`. `case`/string
comparison cannot itself error, so "a value that makes the comparison error" has no representative
left — which is the point of the fix.

**In situ, `a-extract.sh`**, reproducing the original `F2` *shape* rather than a synthetic verdict: a
scratch copy with the `_tree_expected` assignment deleted while the control still reads it.

```
paired/f2.sh: line 658: _tree_expected: unbound variable
  case P3-provenance CONTROL  FAIL  …
  CONTROL : 73 of 74 held      rc = 2
```

The exact defect that produced a false PASS at `4f1e6a3` now prints FAIL, is counted, and exits 2.

**In situ, `a-extract-gate.sh`**, four deliberate verdicts injected into a scratch copy truncated after
preflight (the full harness costs a quarter hour per run; the counter and summary block are verbatim):

```
  case P3-provenance CONTROL  PASS  …
  case DELIB-EMPTY CONTROL  FAIL  deliberately empty verdict (F2 shape)
  case DELIB-FAIL  CONTROL  FAIL  deliberately failing verdict
  case DELIB-00    CONTROL  FAIL  deliberately malformed verdict 00
  case DELIB-REQ   REQUIRED FAIL  deliberately empty REQUIRED verdict
  REQUIRED : 0 of 1 held
  CONTROL  : 1 of 4 held
  CONTROL FAILURE — the harness is untrustworthy…      rc = 2
```

That run also confirms the restored `_clone_head`: `P3-provenance` is **evaluated and passes** rather
than dying uncounted.

**Call-site audit.** Every scored `check` call site in both harnesses passes `held` as either a quoted
command substitution or a literal integer. There is no site where a failure could kill the main shell
instead of scoring, which is the remaining shape of this class.

---

## Item 5 — the eleven previous falsifications

**Exact 40-hex completes**: the baseline above — `21 of 52` / `74 of 74`, rc 1.

**Refusals — 15 inputs, every one `rc=2` with ZERO scored (`REQUIRED`/`CONTROL`) verdicts printed:**

| input | rc | scored | reason given |
|---|---|---|---|
| `bb664c6` | 2 | 0 | ABBREVIATED object id (length 7, need exactly 40) |
| `step-3/isolated-signer` | 2 | 0 | is a NAME, not an object id |
| `HEAD` | 2 | 0 | is a NAME, not an object id |
| `refs/heads/bb664c6…db4` | 2 | 0 | fully qualified ref |
| `HEAD~1` | 2 | 0 | revision expression |
| `bb664c6…db4^{commit}` | 2 | 0 | revision expression |
| `--help` | 2 | 0 | option-shaped |
| `-n` | 2 | 0 | option-shaped |
| `BB664C6…DB4` | 2 | 0 | uppercase hex |
| `000…001` | 2 | 0 | not present in the object database |
| a blob oid | 2 | 0 | exists but is a `blob`, not a commit |
| a tree oid | 2 | 0 | exists but is a `tree`, not a commit |
| 39 hex | 2 | 0 | ABBREVIATED object id |
| 41 hex | 2 | 0 | ABBREVIATED object id |
| `""` | 2 | 0 | is a NAME, not an object id |

The refusal is grammatical, not a detector firing — the diagnosis is produced by the `^[0-9a-f]{40}$`
test before any git command touches the subject. Two diagnostics are imprecise: a 41-character input
is called "ABBREVIATED", and the empty string is called "a NAME". `R5-4`.

**A 40-hex-named branch cannot redirect.** A branch literally named `bb664c626d5…db4` and pointing at
`d1fa16f…` was present for the combined-injection run; the harness measured the **object** (498 paths,
`d0a672e8e34a…`) and produced a matrix byte-identical to the baseline.

**Config injection is inert, with potency proved first.** Potency, against the very `git archive` the
harness runs, using `core.attributesfile` pointed at a file carrying two `export-ignore` lines:

```
plain                  : 574 archive entries
GIT_CONFIG_*           : 566
GIT_CONFIG_PARAMETERS  : 566
```

With both of those set, **plus** repository-local `core.warnAmbiguousRefs=false`, **plus**
`GIT_REPLACE_REF_BASE=refs/heads/` (which would have turned the 40-hex branch into a replacement),
**plus** the `refs/replace` ref: matrix **byte-identical to the baseline**, `74 of 74`,
`P3-provenance` PASS at 498 paths.

**The witness still proves executed bytes.** The baseline records 26 / 14 / 17 / 8 executions of the
four consumers, all carrying the pinned hash; under the `p1` substitution `Z-test_verifier.py` moved
to FAIL, and under the first `F1-4` payload `Z-check-vendor-honesty.sh` moved to FAIL. Its two limits
are stated above: it is per-file, and it depends on the tamper landing before `_witness` runs.

---

## Item 6 — the residuals `INSTRUMENT-REVIEW-3` left open

**`R3-3` — the object database is not pinned to the named repository. NARROWED, still open.**
`GIT_OBJECT_DIRECTORY` and `GIT_ALTERNATE_OBJECT_DIRECTORIES` are still unscrubbed. I tested the worse
possibility the third review did not: a loose object file whose *name does not match its content*,
served from a redirected odb.

```
cat-file -t <oid>   -> commit                     (served; that read path does not verify)
cat-file -p <oid>   -> the OTHER commit's content
ls-tree <oid>       -> error: hash mismatch … / fatal: not a tree object
archive <oid>       -> fatal, empty output
```

Every path that *parses* an object verifies its hash, so `git archive` fails hard and the harness dies
at `cannot build a snapshot of …`, exit 2, zero scored verdicts. **A redirected odb can make objects
absent, or make the run die; it cannot make the harness deliver different bytes.** The residual stands
exactly as the third review framed it — the second identity fact, *"present in **this** repository"*,
is still not established — and no worse.

**`R4-3` — the archive is not pinned to the commit's own attributes. HALF CLOSED.** The file-dropping
half is now detected (item 3: 491 paths, FAIL, exit 2). What remains is the round-trip conversion
class of `R3-4`, which the widened digest cannot see because both of its sides move together.
`GIT_ATTR_NOSYSTEM` is still unset; `git hash-object` still runs without `--no-filters`.

**`R5-3` — a `Z-<consumer>` FAIL line states the opposite of why it failed. OPEN, reproduced
verbatim, twice, from two different failure causes.** From the `p1` matrix (object replacement):

```
FAIL  Z-test_verifier.py         EXECUTED bytes are SUBJECT_SHA's: test_verifier.py 9ebb7fa7…
                                 — 8 execution(s) recorded, all carrying that hash
```

and from the first `F1-4` payload (tampering caught by the witness):

```
FAIL  Z-check-vendor-honesty.sh  EXECUTED bytes are SUBJECT_SHA's: check-vendor-honesty.sh 1ead2f37…
                                 — 17 execution(s) recorded, all carrying that hash
```

Each line asserts what its own verdict denies, and in the first the hash printed is the substituted
commit's, not the subject's. Unchanged at this commit. In a project whose stated hygiene is "read the
output, not the exit status", this is the one output line that punishes the reader who does.

---

## Item 7 — nothing else moved

I ran the **previous revision's harness** (`a9059dc`) against the same clean repository and diffed the
two matrices.

* **Case ids, kinds and statuses: byte-identical.** `21 of 52` REQUIRED and `74 of 74` CONTROL from
  both revisions. **The control delta is zero, as claimed** — measured, not read.
* **Exactly two description strings differ**: `P0` (the harness's own sha256, necessarily) and
  `P3-provenance` (the widened claim). Nothing else.
* **Static case-set diff** of every `check` call site, both harnesses, `a9059dc` vs `d1fa16f`:
  identical.
* **Full non-comment code delta** is the four changes the commit describes — `check()`,
  `_neutralise_object_replacement`, the `P3-provenance` rewrite, the `git show` pin — **plus one the
  commit does not mention**:

```
-hdr "SUBJECT IDENTITY"
-identity_block
```

  `a-extract.sh` no longer prints its `== SUBJECT IDENTITY ==` section (previous revision's run: 1
  occurrence; this one: 0). The identity facts still appear once, under `SUMMARY`.
  `a-extract-gate.sh` still prints both. Nothing scored moves, and it reads like collateral of the
  hunk that rewrote the provenance check rather than a decision — but the two harnesses' output shapes
  now differ, and an unmentioned deletion in a commit whose subject is instrument integrity should be
  named. `R6-4`.

---

## Item 8 — the gate harness, re-measured

I re-measured it myself, twice, against the live repository at
`bb664c626d592d86391f644bf014e76f2bbf7db4`, on an otherwise idle machine.

**Clean run — the author's figures reproduce exactly:**

```
  case P0  OBSERVED  gate harness sha256 9fd5790e9d445d2104251ab08a7e682e1ee315837e0903b9588f82fad9676e25
  case P3-provenance   CONTROL  PASS
  case G1              REQUIRED PASS   (supervisor rc=0)
  G1-stages / G1-order / G1-green      CONTROL PASS
  G2-named / G2-gate / G2-unmasked     REQUIRED PASS      G2-mut / G2-scope  CONTROL PASS
  G3-named / G3-gate / G3-unmasked     REQUIRED PASS      G3-mut / G3-scope  CONTROL PASS
  Z-clean / Z-signed                   CONTROL PASS

  REQUIRED : 7 of 7 held
  CONTROL  : 10 of 10 held
  rc = 0
```

**And a first run that failed, for a reason that is mine and not the harness's** — recorded because
the harness's design deserves the credit. I first ran it with `TMPDIR` set to my scratch directory,
whose path is 104 characters. The isolated-signer suite binds a unix domain socket under `TMPDIR`,
and macOS caps `sun_path` at ~104 bytes:

```
  Error: listen EINVAL: invalid argument …/sentinel-signer-XXXXXX/signer.sock
  case G1  REQUIRED FAIL  (supervisor rc=5)
  REQUIRED : 6 of 7 held      CONTROL : 10 of 10 held
```

All three A-EXTRACT consumer stages were green in that run and `G2`/`G3` still "passed" — because a
gate failing for an unrelated reason also prints `GATE FAILED`. **`G1` is the control of record for
exactly that, its own header says so, and it did its job**: it refused the run and made the
environmental failure visible instead of letting `G2`/`G3` be satisfied by an accident. Re-run under
the machine's default `TMPDIR`, everything passes. Nothing here is a finding against the harness; it
is a note for whoever runs it next, and a data point that one of its controls earns its place.

---

## Residuals

**`R1-4` — the tree digest covers neither file modes nor symlinks.** The expected side drops the mode
column; the actual side is `find -type f`. A mode-only difference is invisible; a symlink in the tree
fails the control closed. At the subject: 19 of 498 blobs are `100755`, 0 are symlinks. No route found
that makes `git archive` emit a mode the tree does not record. Inert here — but the control's own
description says *"matches that commit's tree"*, and a tree includes modes.

**`R2-4` — gitlinks are outside every provenance claim, and the gate stages them from the live
worktree.** The digest filters to `blob`. `a-extract-gate.sh` copies `contracts/lib/forge-std` and
`contracts/lib/openzeppelin-contracts` out of `$ROOT`'s **live** working tree into the measured clone,
and nothing asserts that what it copied is what the subject's gitlink records. Measured today: the
subject and HEAD record the same two gitlinks (`bf647bd6…`, `5fd1781b…`) and the live checkouts match
both, so this is inert — but it is an unasserted input to a measurement whose whole point is *which*
bytes ran. `ts/node_modules` is the same shape and is at least stated in `P7`.

**`R3-4` — attribute-driven conversion round-trips through the digest.** Measured synthetically:
`archive` writes CRLF, `hash-object` cleans it back to the same blob oid, both sides move together,
the control passes over bytes that are not the commit's. Needs attributes visible to both sides: the
subject's own tree (none at `bb664c6…`), `/etc/gitattributes` (absent, root-only), or caller-injected
repository config (`F1-4`).

**`R4-4` — `Z-signed` and `Z-gate5` read the historical base through unpinned `git show`.** Protected
by the environment export alone. `Z-gate5` anchors to a hardcoded constant and fails closed;
`Z-signed` compares a live `shasum` against `git show "$PRE_REPAIR_SHA:…"`, so defeating it would need
the replacement to reproduce a modified live file exactly. Low reach; listed because it is the same
asymmetry as `F2-4`.

**`R5-4` — two refusal diagnostics misdescribe their input.** A 41-character subject is reported as
"ABBREVIATED"; the empty string is reported as "a NAME". Both refuse correctly with zero scored
verdicts. Same family as `R5-3`.

**`R6-4` — `a-extract.sh` silently lost its `SUBJECT IDENTITY` section.** Item 7.

**`R7-4` — `PATH` is not pinned, while `grep` is.** The harness resolves `/usr/bin/grep` absolutely
and says it *"will not use a PATH-resolved grep"*, then resolves `git`, `python3`, `node`, `awk`,
`sed`, `shasum`, `find`, `tar`, `paste`, `sort`, `cut`, `wc`, `tr`, `mktemp` and `cp` through `PATH`.
The `grep` pin buys very little on its own. Not new at this commit, and I did not weaponise it; it is
the outer boundary of the caller-environment threat model the last three reviews have been working
inside, and it deserves an explicit disposition rather than an inconsistency.

**Carried and unchanged**: `R2` from `INSTRUMENT-REVIEW-2` (two git commands are not independent —
accepted and documented), plus `R3-3` and `R5-3` above.

### Fail-closed, checked and confirmed

* **Mislabeled loose object in a redirected odb** — `git archive` fatal, `die`, exit 2, scored 0.
* **`GIT_TEMPLATE_DIR` payload that fires before the execution witness** — caught by
  `Z-check-vendor-honesty.sh`; 73 of 74, exit 2.
* **`GIT_TEMPLATE_DIR` hook that dirties the worktree before the harness's own `checkout`** — the
  `checkout` fails and the gate harness dies at exit 2. Luck, not a defence.
* **`git init` template supplying a `clean` filter or `text` attributes** — moves the *actual* side of
  the digest only; `P3-provenance` fails closed.
* **`GIT_REPLACE_REF_BASE` = `refs/heads/`, `refs/myreplace/`, `refs/replace/`** — all inert against
  the committed harness; matrices byte-identical.
* **Malformed verdicts of every shape I could construct** — all counted (item 4).

---

## What this review does NOT establish

* **Nothing about the 52 REQUIRED cases on their merits**, the four consumers, or whether the measured
  defects are the right defects. That is the batch's ground, not mine.
* **Nothing about the DEEP (`--gate`) profile.** Item 8 is the fast profile, as that harness says of
  itself.
* **No claim that the `F1-4` payload could change a REQUIRED verdict undetected.** I injected a
  harmless `echo` deliberately, so the tally stayed at `21 of 52`. What is measured is that arbitrary
  content reached executing consumer scripts with every control green; what a verdict-changing payload
  would do to the REQUIRED column, I did not measure.
* **Nothing about how any of these environment variables would come to be set here.** I set them. I
  established that the instrument does not survive `GIT_TEMPLATE_DIR` and does not report it; I
  established no likelihood.
* **Nothing about the previous revisions under these vectors.** `GIT_TEMPLATE_DIR` is not new at this
  commit — it has been open the whole time — but I measured only the committed harnesses at `d1fa16f`.
* **No claim of exhaustiveness.** I probed the vectors in my charge plus `GIT_TEMPLATE_DIR`, the
  attributes stack, the odb family, modes, symlinks and gitlinks. One fell open. **This is the fourth
  review and the fourth finding; "no doors remain" is not a claim any of these four reviews has been
  able to support, and the right inference from that record is about the size of git's environment
  surface, not about the author** — three of the four fixes so far have held under adversarial
  re-testing, including all three from the last round.
* **Nothing is signed, certified, ratified or accepted here.** Whether `F1-4` and `F2-4` are accepted,
  where the caller-environment line is drawn, and what if anything is done, is John's.

---

*Every adversarial ref, config, attribute and template was installed in a private clone created by
this review under a scratch directory; the source repository was never modified and never had git
configuration written into it. Scored runs and probes ran under a redirected `HOME`,
`XDG_CONFIG_HOME`, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM` and `GIT_CONFIG_NOSYSTEM=1`. The only
file this review changed in the repository is this document.*
