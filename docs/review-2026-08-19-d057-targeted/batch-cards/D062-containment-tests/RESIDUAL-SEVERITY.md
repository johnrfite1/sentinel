# D-062 / A2 residuals — independent severity

This document is written by an **independent adjudicator**. The author is
**not** the D-062 verifier, **not** the implementer, and **not** a party
D-055 exit depends on.

It scores the residuals **as recorded**:

- V-1, V-2, V-3, V-4, V-5, V-7, V-8, V-9, V-10 from
  `docs/review-2026-08-19-d057-targeted/batch-cards/D062-containment-tests/VERIFICATION.md`
  §10 (lines 450–513 of that file, opened here).
- R-A, R-B, R-C, R-D, R-E, R-F from
  `docs/review-2026-08-19-d057-targeted/batch-cards/A2-tests/VERIFICATION-2.md`
  residuals section (lines 396–437 of that file, opened here).

It does **not** score whether later repairs hold, except as **measured
context** for upgrade and downgrade conditions. It does **not** score
D-055. **D-016 stands.** The five D-008 comprehension questions are
unread.

**Not rescored here:** V-6 (already High in
`docs/review-2026-08-19-d057-targeted/batch-cards/D071-D072-verification/SEVERITY.md`),
R5, R2.

Scale is the same one used in those models: **Critical / High / Medium /
Low / Info**. Instrument defects are in scope. R1-F1, the Critical that
opened this arc, was a certification-gate defect: a child or sibling
could rewrite the running parser, and the "private snapshot" claim was
false.

HEAD measured with `git rev-parse HEAD` on this machine, not copied from
a brief:

| | |
|---|---|
| HEAD | `dffe6f8a0048fc3f051e766c453537dd8d883e81` |
| git | `git version 2.50.1 (Apple Git-155)` |

Live production names at this HEAD, from the files opened below:
`.githooks/pre-commit`, `scripts/check-secrets.sh`,
`scripts/check-vendor-honesty.sh`, `scripts/test.sh`,
`scripts/check-v1-index-ordering.sh`, `scripts/check-rename-gate.sh`.

V-3 was **not** probed with a timing exploit.

---

## Summary

High / UNSCORED first.

| id | severity |
|---|---|
| **V-1** | **High** |
| **V-3** | **UNSCORED** (requires a timing probe) |
| **R-C** | **High** |
| V-10 | Medium |
| R-F | Medium |
| V-2 | Low |
| V-4 | Low |
| V-5 | Info |
| V-7 | Info |
| V-8 | Info |
| V-9 | Info |
| R-A | Info |
| R-B | Info |
| R-D | Info |
| R-E | Info |

V-6 is not in this table. It remains High on the earlier adjudication.

---

## V-1 — **High**

### The defect (as recorded)

`VERIFICATION.md` §10 V-1 (lines 455–461): `git rev-parse --git-path index`
honours `GIT_INDEX_FILE`. The directory comparison in the D-062 repair is
only meaningful because both production files clear that variable
**before** they ask git for the canonical path. At recording time, no
test in any harness would fail if that order were reversed: every card
case would still pass.

### What was measured at this HEAD

Premise still true. In a throwaway `git init` tree:

- `git rev-parse --git-path index` → `.git/index`
- `GIT_INDEX_FILE=/tmp/elsewhere.idx git rev-parse --git-path index` →
  `/tmp/elsewhere.idx`

The load-bearing order is still the live defence:

- `.githooks/pre-commit` unsets `GIT_INDEX_FILE` at line 39, then asks
  `git rev-parse --git-path index` at line 86.
- `scripts/check-secrets.sh` unsets it at line 76, then asks the same
  question at line 121.

A later guard exists. That is **context**, not closure. Session-state
still calls V-1 carried, not accepted.

`scripts/check-v1-index-ordering.sh` (header lines 1–47) observes
behaviour under a hostile exported `GIT_INDEX_FILE`, not source-text
order. It covers only CS validation-refusal and HOOK commit-block.
`scripts/test.sh` invokes it in the shared prefix at lines 227–228, so
both profiles run it. The guard's own coverage statement says a reversed
hook shifts the refusal wording onto `check-secrets.sh` and leaves HEAD
unmoved; that end-to-end accept after reversing the hook's directory
check was **not** constructed.

A regression test is not acceptance of the residual.

### What it reaches

If the unset/resolve order is reversed, `GIT_INDEX_FILE` defines the
"canonical" directory it is compared against. The containing-directory
test becomes vacuous. A hostile index outside `.git` can be accepted.
The pre-commit hook execs `check-secrets.sh --staged` (hook lines
122–125). That is the path that lands a credential in HEAD. Same class
as R1: a secrets-guard fail-open on a path operators actually take
(`git commit`).

Ordinary `A`/`C`/`M` adds still block while the order holds. The hole is
not currently open. Reversing two lines reopens it.

### Severity: **High**

Not Critical. The running parser is not rewritable. The private-snapshot
claim of R1-F1 is not this defect. The repair currently holds because of
the order, not because the residual was accepted.

High because a future edit that hoists the resolve — or adds a third
caller that resolves before scrubbing — reopens credential-to-HEAD, and
the residual as recorded was that nothing would fail. A-098 now fails
that specific hostile-export case. Session-state still carries V-1
unaccepted. Scoring the residual as recorded is High. The guard is a
downgrade **condition**, not a silent close.

### What would change it

- **Up to Critical** if the order is reversed at HEAD and a credential
  reaches HEAD, or if `--staged` / the hook also fail-open without that
  reversal. Neither was measured as open.
- **Down to Medium** if John accepts the residual, or if the defence
  stops depending on unset-before-resolve (git no longer honours
  `GIT_INDEX_FILE` in `--git-path index`, or canonicalisation does not
  consult git for that path). A-098 existing, by itself, is not that
  downgrade. Session-state still says carried, not accepted.

### What this is not claiming

- That the hole is currently open. The order at this HEAD is unset, then
  resolve.
- That A-098 closed V-1. It did not.
- That D-055 is met or unmet.

---

## V-3 — **UNSCORED** (requires a timing probe)

### The defect (as recorded)

`VERIFICATION.md` §10 V-3 (lines 469–472): the validate/scan window
exists twice. The hook validates then `exec`s. The guard re-validates
then reads. A same-user process can replace the file in either window.
The implementation states this bound in both files' comments. The
verifier did not manufacture a timing probe and drew no conclusion
either way.

### What was measured at this HEAD (no timing probe)

The windows are still in the source. No exploit was run.

- Hook: symlink/file checks at `.githooks/pre-commit` 114–115, then
  `exec` of `check-secrets.sh` at 122–125.
- Guard: the same checks at `scripts/check-secrets.sh` 138–139, then
  reads through `_cs_git` (153–159), which prefixes `GIT_INDEX_FILE` on
  the index census, the staged diff, and the staged blob `show`.
- Both files state the same-user bound in comments (`check-secrets.sh`
  148–152; hook comments 61–64).

Siblings of this bound scored **High** (R1, V-6) and **Critical**
(R1-F1). That is not a substitute for a probe. Whether replacement in
the window fail-opens (credential committed) or fail-closes is not
established here.

### Severity: **UNSCORED**

Requires a timing probe. This adjudicator was forbidden to run one and
will not guess High from the siblings.

### What would change it

- A probe that lands a credential in HEAD through either window, while
  the other path still looks clean, would put this in the R1 / V-6 class
  (**High**) or, if a certification token were issued over a rewritten
  parser or a false "impossible" claim, in the R1-F1 class (**Critical**).
- A probe that cannot win the race, or that only fails closed, could
  support Low / Info. That result does not exist in this file.

### What this is not claiming

- That the window is exploitable. Unprobed.
- That the window is safe. Unprobed.
- That same-user replacement is in scope for D-062. The implementation
  disclaims it. Whether that disclaimer is acceptable is not a severity
  score of an unprobed race.

---

## R-C — **High**

### The defect (as recorded)

`VERIFICATION-2.md` lines 416–423: `GIT_CONFIG_COUNT` with
`GIT_CONFIG_KEY_0=core.excludesFile` makes default-mode `check-secrets.sh`
print `secret guard: clean` over an untracked credential-bearing file
that it blocks with no variables set. Pre-existing. Outside the cleared
set. Arguably the declared `--exclude-standard` scope reached by another
route. Recorded as the nearest sibling the clearing does not reach.

This is the same injection family as V-6 (already High, not rescored).
R-C is the A2 recording of one vector of that hole, scored on its own
because V-10 points here.

### What it reaches

`scripts/check-secrets.sh` **default mode** (untracked census).
`scripts/test.sh` line 219 invokes `./scripts/check-secrets.sh` with no
`--staged`. That step runs in the shared prefix, so both fast and
`--gate` take it. A hidden untracked plant yields a clean secret-guard
line and does not set `fail`.

`--staged` / commit-time is a different path. R-C as recorded is default
mode.

### Measured context: the D-072 pin **does** cover this vector

Throwaway `git init`. Plant `plant.env`. Attacker ignore file `*.env`.
Environment:

```
GIT_CONFIG_COUNT=1
GIT_CONFIG_KEY_0=core.excludesFile
GIT_CONFIG_VALUE_0=<that ignore file>
```

(The residual's prose named COUNT/KEY; git's protocol also needs
`GIT_CONFIG_VALUE_0`. That is the injection that hides.)

| invocation | `plant.env` listed? |
|---|---|
| `git ls-files --others --exclude-standard` | **no** — injection hides |
| `git -c core.excludesFile= -c core.quotePath=false ls-files --others --exclude-standard` | **yes** — pin overrides |

At this HEAD the enumerating call in default-mode secrets is
`scripts/check-secrets.sh` line 281:

```
git -c core.excludesFile= -c core.quotePath=false ls-files --others --exclude-standard -z
```

`scripts/check-vendor-honesty.sh` `artifacts()` lines 200–201 uses the
same `-c core.excludesFile=` pin (without `-z`; that is R2, not
rescored).

The pin is command-line `-c` on the enumerating git. It overrides this
COUNT injection. It is **not** a silent close of the residual as
recorded. V-6 was scored High as the pre-repair defect. R-C is that
residual at A2.

### Severity: **High**

Same class as V-6 / R1: a secrets-related instrument fail-open on a path
people actually take (default-mode census inside the gate runner), while
another path (`--staged`) still holds. HOME's default ignore is the V-6
write-up; COUNT injection is what A2 actually recorded. One High, not a
second Critical.

Not Critical: staged/commit-time still blocks when the plant is visible.
An untracked secret hidden this way does not enter history through this
hole.

### What would change it

- **Up to Critical** if `--staged` / the hook also honoured
  `core.excludesFile` and admitted a credential to the index. Not
  measured as open.
- **Down to Medium** if default-mode secrets were not a gate stage.
  They are (`test.sh` 219). The pin covering COUNT is a **repair-hold
  condition**, not this downgrade. This file does not certify that the
  pin holds in production beyond the scratch measurement above.

### What this is not claiming

- That the pin is accepted closure of R-C or V-6. V-6 remains High on
  the earlier document; R-C remains High as recorded.
- That `GIT_CONFIG_PARAMETERS` was this residual. A side measurement of
  that spelling produced empty listings in the scratch tree and is not
  used here.
- That R2 (unquoted `artifacts()` drop of non-ASCII names) is rescored.

---

## V-10 — **Medium**

### The defect (as recorded)

`VERIFICATION.md` §10 V-10 (lines 511–513): A2 residuals R-A through R-F
were not probed beyond the two incidental reproductions at V-5 and V-6.
D-062 reopens none of them. Read no coverage into the silence.

### What it reaches

The D-062 **HOLD** verification's completeness, not a production
fail-open of its own. The verifier labelled the gap instead of claiming
those residuals closed. That is the opposite of R1-F1's false
certification claim.

The pointed-to set includes **R-C (High as scored here)**. Silence over
a High-class secrets census hole is a real completeness miss for anyone
who treats D-062 HOLD as covering A2.

### Severity: **Medium**

Instrument completeness. Honest labelling keeps it off High. The
content of the silence includes a High, which keeps it off Low / Info.

### What would change it

- **Up to High** if a D-062 HOLD, gate pack, or session-state were
  treated as having closed R-A…R-F. This file does not find that claim
  in the residual itself.
- **Down to Low** if every pointed-to residual were Info. They are not.
  R-C is High.

### What this is not claiming

- That D-062 HOLD is wrong. Completeness of probing is a different
  question from the seven demonstrated failures the HOLD addresses.
- Scores for R-A…R-F. Those are below.

---

## R-F — **Medium**

### The defect (as recorded)

`VERIFICATION-2.md` lines 435–437: attempt one's residuals R2, R3, and
R5 were not probed. They are deferred by D-061(2). `check-rename-gate.sh`
was observed exiting 0 while printing `UNVERIFIED`, which is R5 still
live. Nothing was done about it. Nothing should be read into the
silence.

### What it reaches

A2 verification completeness over deferred items. The live observation
was R5: UNVERIFIED and exit 0. **R5 is not rescored here** (already High
in the D-071 adjudication). R-F is the completeness/silence claim, plus
that observation as recorded.

### Measured context (not a rescore of R5)

At this HEAD `scripts/check-rename-gate.sh` still exits 0 on UNVERIFIED
in the fast profile (lines 67–71). Deep/`--gate` exits 1 unless
`SENTINEL_RENAME_GATE_UNVERIFIED_OK=1` (lines 56–66). That is D-071
option C, context only.

### Severity: **Medium**

Honest recording of deferred items, including an observed-live High-class
rename-gate path. Not a second High for R5. Not Info: they saw UNVERIFIED
exit 0 during other probes and left it in the silence.

### What would change it

- **Up to High** if this residual were used to treat R5 as closed by A2.
- **Down to Low** if R5 had not been observed live and the remainder were
  only unread deferred notes. The observation is in the recorded text.

### What this is not claiming

- A new severity for R5 or R2.

---

## V-2 — **Low**

### The defect (as recorded)

`VERIFICATION.md` §10 V-2 (lines 463–467): a hardlink into the canonical
index directory is accepted. `-L` is false for a hardlink, so a hardlink
to a foreign index passes validation. It failed **safe** in the
verification — the guard scanned the linked bytes and blocked the
credential. Creating it requires write access to `.git`, which is the
same-user boundary the implementation disclaims.

### Measured at this HEAD

`.githooks/pre-commit` 114–115 and `scripts/check-secrets.sh` 138–139:
`[ ! -L ... ]` then `[ -f ... ]`. Scratch hardlink: bash `[ -L ]` status
1, `[ -f ]` status 0. Still accepted by that pair.

### Severity: **Low**

The symlink check's intent is incomplete. Measured outcome was fail-safe.
Same-user write to `.git`. Not a secrets fail-open on an operator commit
path.

### What would change it

- **Up to High** if the hardlink made the guard scan different bytes from
  the index git commits (fail-open). The recorded probe was fail-safe.
- **Down to Info** if same-user `.git` writes are ruled out of scope
  without remainder. That ruling is not this score.

---

## V-4 — **Low**

### The defect (as recorded)

`VERIFICATION.md` §10 V-4 (lines 474–478): `--index-file` is now a
reachable interface on `check-secrets.sh`. Re-validation confines it to
the repository's own canonical index directory, and it is refused without
`--staged`. A caller who can write into `.git` can direct the guard at an
index of their own authorship. Outside the hook that changes only what
the guard **reports**, never what git commits.

### Measured at this HEAD

Parser: `scripts/check-secrets.sh` 80–98 (`--index-file` at 90–95).
Re-validation: 104–141. Hook is the production passer (122–123). The only
invocation outside the hook named by the residual, still true at this
HEAD: `scripts/test.sh` 219, no arguments.

### Severity: **Low**

New surface, contained by re-validation, reports-only outside the hook,
same-user `.git` write.

### What would change it

- **Up to High** if a caller who cannot write `.git` can still point the
  guard at a foreign index, or if `--index-file` changes what git
  commits. Not measured.
- **Down to Info** if the flag were unreachable except from the hook and
  the hook's validation were the only copy. The script remains directly
  invocable.

---

## V-5 — **Info**

### The defect (as recorded)

`VERIFICATION.md` §10 V-5 (lines 480–482): `GIT_PREFIX` still reaches
`check-secrets.sh`'s identity probe. One carrier. The `env -u` list
omits it. Identical at the baseline, pre-existing, inert on this git,
already recorded as A2 residual R-E.

### Measured at this HEAD

`scripts/check-secrets.sh` line 66: `env -u GIT_DIR -u GIT_WORK_TREE -u
GIT_INDEX_FILE -u GIT_COMMON_DIR` — no `GIT_PREFIX`. Line 76 unsets
`GIT_PREFIX` after the probe. Scratch: `GIT_PREFIX=victim` does not
change `git rev-parse --show-toplevel` or `git ls-files` on git 2.50.1.

### Severity: **Info**

Inert, pre-existing, identical at baseline. Same fact as R-E.

### What would change it

- **Up to High** if `GIT_PREFIX` redirected identity or the file list on
  a git this project runs. It did not on 2.50.1.

---

## V-7 — **Info**

### The defect (as recorded)

`VERIFICATION.md` §10 V-7 (lines 490–494): `--staged` is now recognised
anywhere in the argument list; unknown arguments are still ignored. The
only invocation of `check-secrets.sh` outside the hook is
`scripts/test.sh:219`, which passes no arguments.

### Measured at this HEAD

Parser loop: `scripts/check-secrets.sh` 80–98; `--staged` is a
non-positional `case` arm; `*) ;;` still ignores unknowns. `test.sh` 219
is still `./scripts/check-secrets.sh || fail=1`.

### Severity: **Info**

Behaviour change with no live extra-hook caller. Undocumented in the
implementation note; not a fail-open.

### What would change it

- **Up to Medium** if a live caller started passing flags whose meaning
  changed because `--staged` is no longer `$1`-only.

---

## V-8 — **Info**

### The defect (as recorded)

`VERIFICATION.md` §10 V-8 (lines 496–501): a relative `GIT_INDEX_FILE` is
resolved against `INVOKING_ROOT`, not the process CWD. Git resolves a
relative `GIT_INDEX_FILE` against the CWD. They diverge only for a
hand-invocation of the hook from a subdirectory. Measured as scanning
**more**, not less. Unreachable through git (hooks run at worktree top).

### Measured at this HEAD

`.githooks/pre-commit` `_d062_dir_of` lines 65–70: relative paths are
prefixed with the supplied base (`INVOKING_ROOT` at the candidate call,
line 94). Scratch: from `sub/`, `GIT_INDEX_FILE=rel.idx git rev-parse
--git-path index` printed `../rel.idx` (CWD-relative). Git's rule is
still CWD.

### Severity: **Info**

Hand-invoke only. Fail direction is scan-more. Unreachable through git.

### What would change it

- **Up to High** if the divergence scanned **less** than git, or if git
  invoked the hook from a subdirectory with a relative `GIT_INDEX_FILE`.
  Not measured.

---

## V-9 — **Info**

### The defect (as recorded)

`VERIFICATION.md` §10 V-9 (lines 503–509): `IMPLEMENTATION.md` said
`GIT_INDEX_FILE` is set "as a per-command prefix on exactly three calls".
There are exactly three **call sites**; the staged blob read executes
twice per scanned path. Measured count on a one-file run is four
invocations.

### Measured at this HEAD

`_cs_git` call sites in `scripts/check-secrets.sh`: line 193 (`ls-files
-s -z`), line 231 (`diff --cached --raw`), line 306 (`show` inside
`_sec_content`). `_sec_content` is invoked at lines 445 and 475. Three
sites, four invocations on a one-file staged run.

`IMPLEMENTATION.md` lines 44–53 now distinguish sites from invocations
and record the verifier's V-9 correction. That is later wording repair,
not a behaviour change. Residual as recorded remains a wording
imprecision.

### Severity: **Info**

Not a behaviour defect. Context: the implementation note was later
corrected in place.

### What would change it

- **Up to Medium** if the wording were still load-bearing evidence for a
  "exactly three invocations" safety claim. The current note no longer
  says that.

---

## R-A — **Info**

### The defect (as recorded)

`VERIFICATION-2.md` lines 398–404: `SENTINEL_GATE_REPO_ROOT` is accepted
from the environment once the body is entered directly via
`bash /dev/fd/N`. The only barrier is the structural `BASH_SOURCE` is
`/dev/fd/*` test, which a caller can satisfy directly. Not reachable by
ordinary invocation. Grants nothing over feeding the same bytes to bash
by hand.

### Measured at this HEAD

`scripts/test.sh`: supervisor unsets a caller-supplied
`SENTINEL_GATE_REPO_ROOT` at line 69, then passes its own value at line
135. Body accepts it at 192–197. Entry condition: lines 56–58 require
`SENTINEL_GATE_TOKEN` **and** `BASH_SOURCE` matching `/dev/fd/*`.

### Severity: **Info**

As recorded: not ordinary invocation; no extra grant over hand-fed
bytes.

### What would change it

- **Up to High** if an ordinary `./scripts/test.sh` invocation honoured a
  caller `SENTINEL_GATE_REPO_ROOT`. The supervisor unsets it first.

---

## R-B — **Info**

### The defect (as recorded)

`VERIFICATION-2.md` lines 406–414: a symlink named `scripts/test.sh`
inside a foreign repository points the gate at that repository.
`_gate_src` is built from `BASH_SOURCE[0]` and `pwd` on its **directory**,
which does not resolve a symlinked final component. A copy behaves
identically and is correct. Both require the caller to install a file at
that path in their own repository. Neither captures a run the caller
believed was a Sentinel run.

### Measured at this HEAD

`scripts/test.sh` line 60: `_gate_src="$(cd "$(dirname
"${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"` — directory
`pwd`, not `pwd -P` on the file, final component unresolved. Line 79 uses
`pwd -P` on the derived root, which does not fix a symlinked
`test.sh` basename.

### Severity: **Info**

As recorded. Copy is the same effect and is the correct ownership rule.

### What would change it

- **Up to High** if a foreign repository could capture a run the caller
  believed was Sentinel **without** installing a file at
  `scripts/test.sh` in the tree they launched. Not this residual.

---

## R-D — **Info**

### The defect (as recorded)

`VERIFICATION-2.md` lines 425–428: `GIT_OBJECT_DIRECTORY` fails closed,
and loudly. `--staged` refuses on every enumerated path rather than
skipping any. Correct direction. Not a defect.

### Severity: **Info**

Fail-closed observation. Not a fail-open.

### What would change it

- **Up to High** if `GIT_OBJECT_DIRECTORY` caused skipped paths and a
  clean line. The residual recorded the opposite.

---

## R-E — **Info**

### The defect (as recorded)

`VERIFICATION-2.md` lines 430–433: `GIT_PREFIX` remains inert and is
scrubbed inconsistently. Independently confirmed inert on git 2.50.1.
Twelve identity probes leave it present; `test.sh` and the hook remove
it.

### Measured at this HEAD

Same inertness as V-5. Hook unsets at `.githooks/pre-commit` 39.
`check-secrets.sh` identity `env -u` omits it (line 66); body unset
includes it (line 76). `test.sh` body unsets it at 204.

### Severity: **Info**

Same fact as V-5. Inert on the measured git. Inconsistent scrub.

### What would change it

- Same upgrade as V-5: if `GIT_PREFIX` becomes live on a git this
  project runs.

---

## Boundary

- **D-055** is not scored. High is the class that criterion names for
  unresolved confirmed defects. Whether that condition is met is John's,
  at a facilitated session.
- **D-016** stands. No publication, rename, or push.
- **D-067** is not rewritten. V-6 remains the named completeness limit
  already scored High; it is not rescored here.
- V-1 remains carried, not accepted. A-098 is measured context.
- No follow-on plan. No gate signature, reopen, or annotation.
- Five D-008 comprehension questions unread.
- Working tree at adjudication: `M README.md`, untracked `.serena/` and
  `assets/` (from `git status --short`). Those paths are not part of
  this file's claims.
