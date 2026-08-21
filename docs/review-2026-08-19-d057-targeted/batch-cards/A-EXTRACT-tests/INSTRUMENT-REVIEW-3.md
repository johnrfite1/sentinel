# A-EXTRACT — THIRD INDEPENDENT INSTRUMENT REVIEW (SUBJECT SELECTION, CONFIG ISOLATION, EXECUTION WITNESS)

**VERDICT: FAIL**

Reviewer: a third independent agent. I authored none of `a-extract.sh`, none of `a-extract-gate.sh`,
none of their cases, and none of the corrective commits. I did not write and have not edited
`INSTRUMENT-REVIEW.md` (**VERDICT FAIL**) or `INSTRUMENT-REVIEW-2.md` (**VERDICT HOLD**, residual
`R1`); both stand exactly as their authors wrote them, and nothing in this document amends either.

**Subject.** Branch `step-3/isolated-signer`, HEAD `4f1e6a3c77ab6f4a23fdeb3223dd4474c6a3af6c`.
`a-extract.sh` sha256 `ead0bf0cbda8711a742f003b77db1401df8c7df40b37b91e045c66ce57454dca`;
`a-extract-gate.sh` sha256 `105f4f6ba0fa2e60abcdd54b9f547b5a109622f17acad6ffaa2b71791f20cc14`
(both printed by the harnesses themselves, both matching `RESULTS.md`).

**Scope.** The eleven falsifications the commit claims, the assurance that nothing else moved, and
a deliberate attempt to make the instrument measure, archive or execute bytes other than the
requested object's. **I did not re-run the 52 REQUIRED cases on their merits** and this review says
nothing about whether the consumers are right.

---

## The verdict in one paragraph

**All eleven falsifications hold as stated, and they hold on measurement rather than on reading —
the grammar really is a grammar, and I proved it with a `bash -x` trace showing that a name-shaped
subject reaches `die` after exactly one git invocation, `git --version`, with no `rev-parse`, no
`show-ref` and no `cat-file` ever run. The FAIL is not on any of the eleven; it is on the charge
they were meant to discharge.** The config scrub is real and I proved my injections potent
first, including against a scrub-neutered copy of the instrument itself. The execution witness is
real and I broke it two different ways on purpose. **But the central claim of this commit —
"there is no ref-resolution step left to defeat" — is false, because the step that was deleted is
not the only one.** `git archive`, `git show <oid>:<path>` and `git cat-file blob <oid>:<path>` all
honour git's **object replacement** mechanism, which is not name resolution and was therefore
untouched by the narrowing. With `refs/replace/<subject-oid>` present in the measured repository I
obtained a **complete 126-verdict run of a different commit's tree**: `21 of 52 REQUIRED`,
**`74 of 74 CONTROL`**, exit `1`, `P3-provenance` **PASS**, all four `Z-<consumer>` controls
**PASS**, and an identity block reading `requested subject: bb664c6…` / `resolved subject:
bb664c6…`. That is the `R1` shape exactly: a full green measurement of a commit nobody named.
**And it is reachable from the caller's environment alone** — `GIT_REPLACE_REF_BASE` is not
scrubbed, so a caller who can set one variable can promote an ordinary `refs/remotes/origin/*`
namespace into a replacement namespace. Separately, **this commit introduced a regression into
`a-extract-gate.sh`**: it deleted the `_clone_head` assignment while keeping the reference, so that
harness's only subject-provenance control is now an unbound-variable error that prints `FAIL` and
**is not counted**, leaving the summary free to report `10 of 10 CONTROL held`. `GATE-BINDING.md`
records that row as `PASS`. The verdict is FAIL.

---

## Conventions, and they are load-bearing

* **A verdict is a line of output, never an exit status.** "Scored" counts output lines matching
  `^  case .*(REQUIRED|CONTROL) `. `OBSERVED` lines print `....`, assert nothing, and are not
  counted. A complete valid run scores **126** (52 REQUIRED + 74 CONTROL).
* **Every probe is stated beside a control that had to move.** For the three injection classes I
  proved potency twice: against raw `git` running the harness's own `git archive` command, and
  against a copy of the harness with only `_scrub_git_config_env` neutered.
* **The discriminator throughout is a blob hash, not a tally.** `verifier/test_verifier.py` differs
  between `bb664c6…` (**A**, sha256 `924749d5…`) and `4f1e6a3…` (**B**, sha256 `9ebb7fa7…`), and the
  harness prints that hash on the `Z-test_verifier.py` line. Where the tally cannot move, that hash
  can.
* **I mutated no repository I did not create.** Every adversarial ref, config and attribute lives in
  a private clone I made under a scratch directory. The source repository was read-only to me and to
  every harness run; verified before and after.
* Paths are written `<scratch>`. `~/Projects/Sentinel` is the harness's own sanitized output.

---

## Per-item results

| # | Falsification | Result | Key measurement |
|---|---|---|---|
| 1 | exact 40-hex commit completes normally | **HOLD** | `21 of 52 REQUIRED`, `74 of 74 CONTROL`, exit `1`, 126 scored, 1m44s |
| 2 | short SHA refused | **HOLD** | `bb664c6` → exit `2`, **scored=0**, *an ABBREVIATED object id (length 7, need exactly 40)* |
| 3 | branch/tag collision refused **because names are not accepted** | **HOLD** | refusal is grammatical, proved by trace: only `git --version` runs before `die`; identical refusal in a repo with **no refs at all** |
| 4 | fully qualified ref refused | **HOLD** | `refs/heads/main` → exit `2`, **scored=0**, *a fully qualified ref; refs are not accepted* |
| 5 | SHA-resembling branch name refused | **HOLD** | `deadbeefdeadbeef` → exit `2`, **scored=0**, *an ABBREVIATED object id (length 16…)* |
| 6 | 40-hex-named branch cannot redirect the selected **object** | **HOLD** | branch **and** tag named `bb664c6…` → `4f1e6a3…`; run measured `Z-test_verifier.py 924749d5…` (**A**), not `9ebb7fa7…` (**B**); matrix byte-identical to baseline |
| 7 | `GIT_CONFIG_COUNT` / `KEY_<n>` / `VALUE_<n>`, including large *n* | **HOLD** | `n=1` and `n=300` (payload at `KEY_299`): `21 of 52`, `74 of 74`. Potency: same injection makes raw `git archive` drop a file, and kills a scrub-neutered harness at preflight |
| 8 | `GIT_CONFIG_PARAMETERS` | **HOLD** | `21 of 52`, `74 of 74`, 126 scored. Potency: same payload drops a file from raw `git archive` |
| 9 | repository-local `core.warnAmbiguousRefs=false` | **HOLD** | set in the clone's own `.git/config` **with** the 40-hex branch and tag present: `21 of 52`, `74 of 74`, `Z-test_verifier.py 924749d5…` (**A**) |
| 10 | invalid subjects score **zero** verdicts | **HOLD** | **17** invalid shapes, every one exit `2` with **scored=0** |
| 11 | the witness proves the candidate's consumer bytes were **EXECUTED** | **HOLD** | tamper an executed non-`p0` copy only → `Z-check-type-strings.sh` **FAIL**, `73 of 74`, exit `2`; untampered → **PASS**, `74 of 74` |
| — | **Nothing else moved** | **HOLD** | 123 `check` call sites both sides; **the only case-level delta is `P3` → `P3-provenance`**; control delta **zero** |
| — | Source repository clean, no git config written | **HOLD** | before/after state byte-identical: clean tree, same 5 refs, same `.git/config` sha256, no `.git/info/attributes`, no grafts |
| — | `P3-provenance` claims no independence; no stale prose | **HOLD** | every surviving "two independent routes" string is either an explicit withdrawal or lives in the two immutable review documents |
| — | **`a-extract-gate.sh` at this commit** | **FAIL** | `P3-provenance` is an unbound-variable error: prints `FAIL`, **is not counted**, and `GATE-BINDING.md` records it as `PASS`. It is the control that would have caught the caller-env redirection on the clone path |
| — | **Attempt to defeat it** | **FAIL** | `refs/replace/<oid>` → full green measurement of a different commit; reachable from the caller's environment via `GIT_REPLACE_REF_BASE` |

---

## F1 — OBJECT SUBSTITUTION IS A RESOLUTION STEP, AND IT WAS NOT DELETED

### The claim under test

> *"Existence and type come from `git cat-file --batch-all-objects`, which enumerates the object
> database and performs NO name resolution. There is no ref-resolution step left to defeat."*

The premise is that an object id is *looked up*, not *resolved*. **That is not true of git.** Git
carries a second indirection keyed on object ids themselves — `refs/replace/<oid>` — which is
consulted by essentially every object-reading command **except** raw object-database enumeration.
So the one command chosen to establish existence is the one command immune to it, and the three
commands that actually produce the measured bytes are not.

### Measured, in a private clone, `A` = `bb664c6…` (subject), `B` = `4f1e6a3…` (a different commit)

```
$ git replace -f bb664c6…db4 4f1e6a3…af6c
$ git for-each-ref refs/replace
  refs/replace/bb664c626d592d86391f644bf014e76f2bbf7db4 -> 4f1e6a3c77ab6f4a23fdeb3223dd4474c6a3af6c

1. odb enumeration (the existence+type check): bb664c626d592d86391f644bf014e76f2bbf7db4 commit
2. git archive   -> verifier/test_verifier.py : 9ebb7fa781fc      <-- B's blob
3. git show A:verifier/test_verifier.py       : 9ebb7fa781fc      <-- B's blob
4. git cat-file blob A:scripts/check-type…    : 9bcdb5621ca7      <-- the sentinel, unchanged between A and B

   TRUTH: A = 924749d5c362   B = 9ebb7fa781fc
   with GIT_NO_REPLACE_OBJECTS=1: archive -> 924749d5c362
```

Line 1 is why the harness admits the subject. Lines 2 and 3 are why it measures the wrong one **and
why nothing detects it**: `Z-<consumer>` compares the archive against `git show "$SUBJECT_SHA:$f"`,
and *both sides follow the replacement*, so they agree. Line 4 is why `P3-provenance` does not fire:
its sentinel is a single file, `scripts/check-type-strings.sh`, which is byte-identical in A and B.

### The full run

```
== SUBJECT IDENTITY ==
  requested subject: bb664c626d592d86391f644bf014e76f2bbf7db4
  resolved subject : bb664c626d592d86391f644bf014e76f2bbf7db4

  case P3-provenance CONTROL  PASS  subject provenance is CONSISTENT (not independent): 'bb664c6…db4'
        is an exact 40-hex oid, the odb reports it type 'commit', and the archived tree's sentinel
        blob matches that commit's
  case Z-check-type-strings.sh   CONTROL  PASS  … 9bcdb562… — 26 execution(s) recorded
  case Z-check-eval-codes.sh     CONTROL  PASS  … 7970d226… — 14 execution(s) recorded
  case Z-check-vendor-honesty.sh CONTROL  PASS  … 1ead2f37… — 17 execution(s) recorded
  case Z-test_verifier.py        CONTROL  PASS  … 9ebb7fa7… —  8 execution(s) recorded
  case Z-clean    CONTROL  PASS
  REQUIRED : 21 of 52 held
  CONTROL  : 74 of 74 held
  exit 1 — REQUIRED FAILURES with every control holding: the defects are observed.
```

The scored matrix is **verdict-for-verdict identical** to the true `bb664c6…` baseline *and* to a
run whose subject really is `4f1e6a3…`. **The only trace anywhere in 126 verdicts is
`Z-test_verifier.py 9ebb7fa7…` where the truth is `924749d5…`** — a hash the reader must already
know to notice, on a control line that says `PASS`.

### The sentinel is not a defence, and its escape hatch is not narrow

`P3-provenance` fires only when the replacement's `scripts/check-type-strings.sh` differs from the
subject's. Measured against this repository's own history:

```
sentinel blob 2c8abb076d55d0803611d7d80724267dd355a194
196 commits reachable from all refs
 21 commits carry the IDENTICAL sentinel blob
 20 of those have a DIFFERENT tree
```

**Twenty commits already in this repository can be substituted for `bb664c6…` with
`P3-provenance` still reporting PASS.** No craft is required; `4f1e6a3` — the commit under review —
is one of them, which is how I found it.

### F1b — and it is reachable from the CALLER'S ENVIRONMENT ALONE

This matters because Ruling 2's claim is *"caller configuration injection is neutralised before the
first git invocation"*, and the `R1` threat model John rejected was exactly a caller-set variable.
`GIT_REPLACE_REF_BASE` relocates the replacement namespace. **Neither harness mentions it**
(`grep -c 'GIT_REPLACE_REF_BASE\|GIT_NO_REPLACE_OBJECTS'` → `0` in both files), and neither sets
`GIT_NO_REPLACE_OBJECTS`.

Measured in a clone carrying **no `refs/replace` at all** — only an ordinary remote-tracking ref
named the subject oid, which is precisely what a `fetch` from a remote carrying such a branch
creates, and precisely the ref shape falsification 6 already treats as a realistic hazard:

```
  refs/remotes/origin/bb664c626d592d86391f644bf014e76f2bbf7db4 -> 4f1e6a3…af6c
  refs/replace present? 0

  archive verifier/test_verifier.py WITHOUT the env : 924749d5c362      <-- A, correct
  archive verifier/test_verifier.py WITH    the env : 9ebb7fa781fc      <-- B, wrong
  odb enumeration WITH the env                      : bb664c6…db4 commit
  sentinel cat-file blob WITH the env               : 9bcdb5621ca7      <-- still matches
        env = GIT_REPLACE_REF_BASE=refs/remotes/origin/
```

And the full harness, in that same clone, with that one variable set:

```
== SUBJECT IDENTITY ==
  requested subject: bb664c626d592d86391f644bf014e76f2bbf7db4
  resolved subject : bb664c626d592d86391f644bf014e76f2bbf7db4

  case P3-provenance             CONTROL  PASS
  case Z-check-type-strings.sh   CONTROL  PASS  … 9bcdb562… — 26 execution(s) recorded
  case Z-check-eval-codes.sh     CONTROL  PASS  … 7970d226… — 14 execution(s) recorded
  case Z-check-vendor-honesty.sh CONTROL  PASS  … 1ead2f37… — 17 execution(s) recorded
  case Z-test_verifier.py        CONTROL  PASS  … 9ebb7fa7… —  8 execution(s) recorded   <-- B
  case Z-clean                   CONTROL  PASS
  REQUIRED : 21 of 52 held      CONTROL : 74 of 74 held      exit 1
```

**Paired control — same repository, same subject, the variable simply absent:**

```
  case Z-test_verifier.py        CONTROL  PASS  … 924749d5… —  8 execution(s) recorded   <-- A
  REQUIRED : 21 of 52 held      CONTROL : 74 of 74 held      exit 1

  matrix diff (case, verdict) between the two runs:
  IDENTICAL VERDICTS — nothing in the scored output moved
```

**One caller-set environment variable silently swapped which commit was measured, and not one of
the 126 verdicts moved.** That is the `R1` shape, in the class Ruling 2 says is neutralised.

### Bounded, then unbounded again: what reaches the gate harness

Measured, not assumed. `a-extract-gate.sh` builds its subject with
`git clone --no-hardlinks --local` and then `git checkout <oid>`, and a local clone does not copy
`refs/replace`. From a source clone carrying the replacement:

```
  replace refs in the clone                 : 0
  clone HEAD after checkout of bb664c6…db4  : bb664c626d592d86391f644bf014e76f2bbf7db4
  worktree verifier/test_verifier.py        : 924749d5c362      <-- A, the truth
```

So a bare `refs/replace/<oid>` in the source does not reach the gate harness. **But that is a fact
about `git clone`'s default refspec, not a defence the harness authored — and `GIT_REPLACE_REF_BASE`
walks straight past it,** because a clone *does* copy `refs/heads/*` into `refs/remotes/origin/*`
and `refs/tags/*` verbatim. Measured, in a gate-style clone of a source carrying a 40-hex branch and
tag:

```
  refs/remotes/origin/bb664c626d592d86391f644bf014e76f2bbf7db4 -> 4f1e6a3…af6c
  refs/tags/bb664c626d592d86391f644bf014e76f2bbf7db4           -> 4f1e6a3…af6c
  refs/replace present? 0

  git checkout <oid>                            -> worktree test_verifier.py 924749d5c362  (A)
  GIT_REPLACE_REF_BASE=refs/remotes/origin/ \
      git checkout <oid>                        -> HEAD 4f1e6a3…af6c
                                                   worktree test_verifier.py 9ebb7fa781fc  (B)
```

**`git rev-parse HEAD` in that clone returns `4f1e6a3…`, not the subject** — which is precisely the
comparison `_clone_head = "$SUBJECT_SHA"` was written to make. **F2 disabled the one control that
would have caught F1b on the gate path.** The two findings are not independent: the regression
removed the detector for the fail-open.

### What would close it

Not my call to make, and I make none — but the measurement above records that
`GIT_NO_REPLACE_OBJECTS=1` restored `924749d5c362` in every probe I ran, and that it is one export
in the same isolation block that already exports seven other git variables.

### Age

**F1 is not new at this commit.** `git rev-parse` returns an oid unchanged under replacement, and
`git archive` followed the replacement in every git command the previous harness used, so the prior
revision had the same hole. What is new is the *claim* that the seam is now structurally closed.
**I did not re-run the `1517120` harness under a replace ref**; that statement is read from the code
paths, not measured.

---

## F2 — THE GATE HARNESS'S ONLY PROVENANCE CONTROL IS DEAD, AND THE TALLY SWALLOWS IT

This one **is** a regression introduced by `4f1e6a3`. The rewrite of the `P3-subject` →
`P3-provenance` block deleted the line that produces `_clone_head` and kept the line that reads it:

```
@@ 1517120 -> 4f1e6a3, a-extract-gate.sh
-_clone_head="$(cd "$BASECOPY" && git rev-parse HEAD 2>/dev/null)" || _clone_head=""
-check CONTROL P3-subject "$([ "$_clone_head" = "$SUBJECT_SHA" ] && …
+check CONTROL P3-provenance "$([ "$_clone_head" = "$SUBJECT_SHA" ] && …
```

`a-extract-gate.sh` runs under `set -u`. Live, against the real repository at the real subject:

```
a-extract-gate.sh: line 240: _clone_head: unbound variable
a-extract-gate.sh: line 140: [: : integer expression expected
  case P3-provenance CONTROL  FAIL  subject provenance is CONSISTENT (not independent): …
a-extract-gate.sh: line 144: [: : integer expression expected
```

Line 140 is `elif [ "$held" -eq 0 ]` and line 144 is `if [ "$held" -ne 0 ] && …`. The first error is
why the line prints `FAIL`; **the second is why `ctl_fail` is never incremented.** Replayed with the
harness's own `check()` verbatim:

```
  case P3-provenance CONTROL  FAIL  provenance
  after: ctl_fail=0
  CONTROL : 1 of 1 held
  script rc=0
```

So the gate harness at this commit prints a control FAIL, reports `CONTROL : 10 of 10 held`, and
does **not** take its own exit-2 "the harness is untrustworthy" path. `a-extract-gate.sh` has exactly
10 CONTROL call sites, one of which is this one. **`GATE-BINDING.md` line 128 records the row as
`P3-provenance … CONTROL | PASS`, which the code at this commit cannot produce.**

The one thing that control asserts — *the clone is standing on the oid that was supplied* — is
therefore asserted by nothing. The clone is still `git checkout`ed at `$SUBJECT_SHA` with a `die` on
failure, so this is a dead control rather than a demonstrated wrong measurement; but a dead control
whose failure is invisible to the tally is this project's named defect class, and it is the class
both prior reviews were convened over.

**I could not re-measure `7 of 7` / `10 of 10`.** `GATE-BINDING.md` already says those figures
predate the narrowing; they still do. Three full fast-gate runs need the machine to themselves for
ten to fifteen minutes, and HEAD carries the deliberately red `cefc135`, so `G1` would fail for a
reason that is not a finding. I captured the preflight only, which is where F2 lives.

---

## The eleven, as I measured them

### 1 — an exact 40-hex commit completes normally

```
a-extract.sh . bb664c626d592d86391f644bf014e76f2bbf7db4
  REQUIRED : 21 of 52 held
  CONTROL  : 74 of 74 held
  exit 1        126 scored lines        1m44s
  Z-check-type-strings.sh 9bcdb562… 26 exec   Z-check-eval-codes.sh 7970d226… 14 exec
  Z-check-vendor-honesty.sh 1ead2f37… 17 exec Z-test_verifier.py 924749d5…  8 exec
```

Paired control that must move: the same repository at subject `4f1e6a3…` prints
`Z-test_verifier.py 9ebb7fa7…`. **The subject is honoured; the harness is not hardcoded.** Note
honestly that the *tally* does not move between those two subjects — `21 of 52` / `74 of 74` both
ways — so the tally is not a discriminator for which commit was measured. The consumer blob hash is.

### 2, 4, 5, 10 — the grammar refusals

Seventeen invalid shapes, each `exit 2` with **scored=0**:

| subject | diagnosis |
|---|---|
| *(1 arg)*, *(3 args)* | *an evidentiary run takes EXACTLY a repository and a full 40-hex commit* |
| `bb664c6` | *an ABBREVIATED object id (length 7, need exactly 40)* |
| `deadbeefdeadbeef` | *an ABBREVIATED object id (length 16, need exactly 40)* |
| 39-hex, 41-hex | *an ABBREVIATED object id (length 39 / 41, need exactly 40)* |
| `main`, `HEAD` | *a NAME, not an object id — branches, tags and HEAD are not accepted* |
| `refs/heads/main` | *a fully qualified ref; refs are not accepted, only object ids* |
| `@`, `HEAD~1`, `<oid>^{commit}` | *a revision expression; expressions are not accepted* |
| `BB664C6…` (uppercase) | *uppercase hex — git's canonical form is lowercase* |
| `--help-me` | *option-shaped* |
| `0000…0001` | *not present in ~/Projects/Sentinel's object database* |
| a blob oid, a tree oid | *exists … but is a 'blob' / 'tree', not a commit* |

**`a-extract-gate.sh` was measured separately and carries the same grammar.** Eleven shapes —
one argument, three arguments, `bb664c6`, `main`, `refs/heads/main`, `HEAD`, `HEAD~1`, uppercase
hex, `--nope`, an absent oid, a blob oid — **every one exit `2` with scored=0.** Its diagnosis is a
single sentence rather than `a-extract.sh`'s ladder (*"is not an exact 40-character lowercase hex
object id"*), which is a difference in helpfulness, not in behaviour.

### 3 — the refusal is GRAMMATICAL, not a detector firing

Two independent demonstrations, because "the message says grammar" is not evidence that grammar is
what ran.

**(a) Trace.** `bash -x a-extract.sh <repo> main` — every git invocation in the whole trace:

```
  111:++ git --version
```

That is the version banner printed by `P2`. **No `rev-parse`, no `show-ref`, no `cat-file`, no
`for-each-ref` — nothing looked at a ref, an object, or the collision.** The same trace for a
grammatically valid subject reaches:

```
  139:++ git cat-file --batch-all-objects '--batch-check=%(objectname) %(objecttype)'
```

so the instrument *does* consult git the moment the grammar is satisfied. The refusal precedes it.

**(b) Ablation.** A directory whose `.git` is an empty folder — no objects, no refs, no config, no
collision possible:

```
  <repo> main   -> PREFLIGHT FAILED: subject 'main' is a NAME, not an object id …
  <repo> bb66…  -> PREFLIGHT FAILED: object bb664c6…db4 is not present in …'s object database.
```

Identical grammatical refusal with nothing to detect, and a *different* failure mode once the
grammar passes. A detector cannot produce that pair.

### 6 — a 40-hex-named branch cannot redirect the selected object

Constructed in a private clone: **both** `refs/heads/bb664c6…db4` **and** `refs/tags/bb664c6…db4`
pointing at `4f1e6a3…`, with `core.warnAmbiguousRefs=false` and `advice.objectNameWarning=false` set
in that clone's own `.git/config` so git's warning — the detector `R1` was about — is off. Raw git
first:

```
git rev-parse bb664c6…db4   -> bb664c626d592d86391f644bf014e76f2bbf7db4   (the OBJECT)
git show-ref  bb664c6…db4   -> 4f1e6a3…af6c refs/heads/…   4f1e6a3…af6c refs/tags/…
A tree 592186a8…   B tree 23494ac2…
git archive bb664c6…db4 -> verifier/test_verifier.py 924749d5c362        (A, not B)
```

Then the full harness in that clone:

```
  requested subject: bb664c626d592d86391f644bf014e76f2bbf7db4
  resolved subject : bb664c626d592d86391f644bf014e76f2bbf7db4
  case Z-test_verifier.py CONTROL PASS  … 924749d5… — 8 execution(s) recorded
  REQUIRED : 21 of 52 held      CONTROL : 74 of 74 held      exit 1
  matrix vs baseline: IDENTICAL, including every description string
```

**The object was used, not the ref's target** — `924749d5…`, not `9ebb7fa7…`. This is the exact
falsification the commit claims, and it is the reason F1 is a separate mechanism rather than a
restatement of this one: a *ref named like an oid* cannot redirect, a *replacement keyed on that oid*
can.

### 7, 8 — config injection, with potency proved first

An injection that changes nothing proves nothing, so the payload is one that demonstrably changes
what `git archive` produces: `core.attributesFile` pointing at a file containing
`verifier/test_verifier.py export-ignore`.

**Potency against raw git**, using the harness's own archive command in the same repository:

```
  baseline archive contains verifier/test_verifier.py           : 1
  with GIT_CONFIG_COUNT=1  KEY_0=core.attributesFile            : 0
  with GIT_CONFIG_COUNT=300 payload at KEY_299 (all keys set)   : 0
  with GIT_CONFIG_PARAMETERS="'core.attributesFile=…'"          : 0
```

**Potency against this instrument**, using a copy of `a-extract.sh` with exactly one line changed —
the `_scrub_git_config_env` invocation replaced by `:`:

```
  scrub-neutered + injection : exit 2, scored=0
        PREFLIGHT FAILED: the snapshot is missing verifier/test_verifier.py
  scrub-neutered, no injection (paired control) : 21 of 52, 74 of 74, exit 1, 126 scored
```

**The real harness under the same injections:**

| injection | result |
|---|---|
| `GIT_CONFIG_COUNT=1` | `21 of 52`, `74 of 74`, exit 1, 126 scored |
| `GIT_CONFIG_COUNT=300`, payload at `KEY_299` | `21 of 52`, `74 of 74`, exit 1, 126 scored |
| `GIT_CONFIG_PARAMETERS` | `21 of 52`, `74 of 74`, exit 1, 126 scored |

The enumeration really is an enumeration: it is driven from `env` output rather than a fixed bound,
and `n=300` is neutralised as completely as `n=1`.

### 9 — repository-local `core.warnAmbiguousRefs=false`

Set in the private clone's own `.git/config` — `core.warnAmbiguousRefs=false` **and**
`advice.objectNameWarning=false`, which is what actually silences the 40-hex warning on git
2.50.1 — with the branch **and** the tag named `bb664c6…db4` still pointing at `4f1e6a3…`. Raw
`git rev-parse bb664c6…db4` printed the bare oid with no warning at all: the detector `R1` was
about is off.

```
  REQUIRED : 21 of 52 held      CONTROL : 74 of 74 held      exit 1      126 scored
  case Z-test_verifier.py CONTROL PASS  … 924749d5… — 8 execution(s) recorded
```

`924749d5…` is **A**. **The warning being off changes nothing, because nothing reads it any more.**
`R1` as written by the second review is closed.

### 11 — the execution witness

Two tampers, each on a copy of the harness with **one** inserted line inside `subject()`, immediately
after the tar extraction. Nothing else differs, and the production harness is untouched.

| probe | what it breaks | result |
|---|---|---|
| **paired control** — untampered | nothing | `Z-check-type-strings.sh` **PASS** `9bcdb562…`, 26 executions; `74 of 74`; exit 1 |
| **T1** — append a byte to `p0`'s `scripts/check-type-strings.sh` | the bytes compared against the subject's blob | `Z-check-type-strings.sh` **FAIL** `fcf00f78…` (blob is `9bcdb562…`), **and** `P3-provenance` **FAIL**; `72 of 74`; **exit 2** |
| **T2** — append a byte to case `c1`'s copy only, leaving `p0` intact | **only the EXECUTED bytes**; the compared file still matches the blob | `Z-check-type-strings.sh` **FAIL** while printing the *correct* hash `9bcdb562…`; the other three `Z` controls PASS; `73 of 74`; **exit 2** |

T2 is the one that matters: it is the tamper a pure file-versus-blob comparison cannot see. Only the
witness's *"every recorded execution carried the same hash"* clause can catch it, and it did.

---

## Nothing else moved

Accounting is against `1517120`, as required, and is complete: every executable-line difference
falls into one of four buckets and I enumerated them all.

| measurement | `1517120` | `4f1e6a3` |
|---|---|---|
| `check()` call sites in `a-extract.sh` | 123 | 123 |
| case ids and kinds | — | **identical but for `CONTROL P3` → `CONTROL P3-provenance`** |
| REQUIRED / CONTROL call sites in `a-extract-gate.sh` | 7 / 10 | 7 / 10 |
| reason vocabulary (`DUP_WHY`, `MISSING_WHY`, `AMBIG_WHY`, `UNRESOLVED_WHY`) | — | identical |
| success lines (`TS_OK`, `EC_OK`, `VH_OK`, `VP_OK_RE`) | — | identical |
| anchors `H58 H59 H56 H571 H6 H72`, `CAVEAT_*`, `GATE5_PINNED`, the three `*_REL` paths | — | identical |
| `ts_class()` / `vp_class()` reason mapping | — | identical, line for line |
| `pair()` expected classes (4 sites) | — | identical |
| `P8` exclusion basis (§5.7.1 non-normative) | — | identical |
| `COVERAGE.md` case-table rows | 14 | 14, identical |
| `COVERAGE.md` exclusions section | — | identical |

**The four buckets, and nothing outside them:** (i) usage text and `-lt 2` → `-ne 2`;
(ii) `SUBJECT_REF` → `SUBJECT_OID` and the identity label; (iii) deletion of the ref-resolution
machinery (`_ref_candidates`, `_matching_refs`, `_peel_to_commit`, `_independent_subject_sha`, the
`rev-parse --verify` call and both ambiguity detectors), replaced by the grammar gate and the
`--batch-all-objects` existence/type lookup; (iv) `_scrub_git_config_env`, `WITNESS_LOG`/`_witness`
plus one call in each of the four `run_*`, `P3` → `P3-provenance`, and the strengthened `Z-*`.

**Control delta is ZERO, as the author claims** — `P3` was renamed, not added or removed, and the
witness strengthened the four existing `Z` controls rather than adding new ones. Baseline reproduces
exactly: **`21 of 52 REQUIRED`, `74 of 74 CONTROL`.**

### `P3-provenance` does not claim independence

`grep -ni independent` over both harnesses returns only: the history of `R1`/`R2`, the explicit
withdrawal, and the control's own wording *"subject provenance is CONSISTENT (not independent)"*.
Every surviving `two independent routes` string in the batch card is either an explicit withdrawal
(`COVERAGE.md` §"`P3-provenance` — a CONSISTENCY control, not an independence proof";
`RESULTS.md` §"`P3` renamed, and an over-claim withdrawn") or lives inside `INSTRUMENT-REVIEW-2.md`,
which is history and correctly untouched. **No stale independence claim survives in the harness or
the maintained evidence.**

### The source repository

`git status --porcelain`, `git for-each-ref`, the sha256 of `.git/config`, the contents of
`.git/info` and the absence of `grafts`/`shallow` were captured before the first probe and again
after the last. **The two captures differ by exactly one line: the untracked
`INSTRUMENT-REVIEW-3.md` I am writing.** No git configuration was written into the source
repository by any harness run or by me; `.git/info` still contains only `exclude`; the five refs
are unchanged. Every adversarial ref, config value and attributes file lives in a clone I created.
`Z-clean` reported `0 changed path(s)` on all ten full runs.

---

## Residuals

**`R1-3` — object replacement redirects the measurement, and the caller can reach it.** F1 above.
Full green measurement of a commit nobody named, `P3-provenance` PASS, `74 of 74`. **Unaccepted;
this is the FAIL.**

**`R2-3` — the gate harness's provenance control is dead and uncounted, and the evidence file
records it as PASS.** F2 above. **Unaccepted; this is the second FAIL.**

**`R3-3` — the object database is not pinned to the named repository.** `GIT_OBJECT_DIRECTORY` and
`GIT_ALTERNATE_OBJECT_DIRECTORIES` are not scrubbed (the isolation block unsets `GIT_DIR`,
`GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_COMMON_DIR`, `GIT_PREFIX` and the `GIT_CONFIG_*` family, and
stops there). Measured: an **empty** repository enumerates `0` objects, and with
`GIT_ALTERNATE_OBJECT_DIRECTORIES` pointed elsewhere it enumerates `3208`, reports
`bb664c6…db4 commit`, and archives that commit's tree. This **cannot change which commit is
measured** — object ids are content-addressed — so it is a residual, not the FAIL. What it falsifies
is the second identity fact: *"this object is present in **this repository's** object database"* is
not established, and `P3-provenance` link (b) inherits that.

**`R4-3` — the archive is not pinned to the commit's own attributes.** `git archive` honours
`$ROOT/.git/info/attributes`, which is repository-local state no environment scrub can reach, and
the harnesses do not set `GIT_ATTR_NOSYSTEM`. Measured: `verifier/test_verifier.py export-ignore` in
`.git/info/attributes` drops the file from the archive of the exact requested oid. The seven paths
the harness existence-checks after extraction catch that particular file; **nothing checks the rest
of the tree.** The system-level attributes file on this machine carries no `export-ignore` /
`export-subst`, so this vector is inert here today.

**`R5-3` — a `Z-<consumer>` FAIL line states the opposite of why it failed.** The description
string is built before the verdict and always reads *"N execution(s) recorded, all carrying that
hash"*. Under tamper T2 the line printed exactly that beside `FAIL`, while the actual reason was
that the executions did **not** all carry that hash. Cosmetic, but this project's stated hygiene is
"read the output, not the exit status", and this particular output line misdirects the reader who
does. Minor; recorded rather than argued.

**Carried from `INSTRUMENT-REVIEW-2` and not re-opened:** `R2` (commands sharing git's object
resolver are not independent) is accepted and documented by this commit and I agree with the
disposition. The original `R1` (`core.warnAmbiguousRefs=false`) is **closed** on my measurement:
falsifications 3, 6 and 9 hold with that switch thrown.

### Fail-closed, checked and confirmed

* **Incomplete tree.** A clone with one blob object deleted: `git archive` exits 255 (having written
  a partial tar), the harness's `||` catches the subshell status → `PREFLIGHT FAILED: cannot build a
  snapshot of …`, exit 2, **scored=0**.
* **Grafts.** `.git/info/grafts` rewrote parentage (`git log --format=%P` returned the graft target)
  but the archived tree was unchanged: `924749d5c362`. Not a redirection vector.
* **Packed objects.** After `git gc --aggressive` (`count: 0`, `in-pack: 3183`) the enumeration still
  reports `bb664c6…db4 commit`.
* **`core.abbrev`.** Inert against an exact 40-hex subject — `rev-parse` under `core.abbrev=4` still
  returns the full oid. It remains a valid *potency* demonstration and nothing more.
* **Symlinked root.** Resolved with `pwd -P`; the identity block names the real path.
* **`.git` as a file** (linked worktree / submodule): refused, *"is not a git repository"*. A
  usability limit, not a fail-open.
* **Regex injection through the subject.** The subject is interpolated into `grep -E "^${SUBJECT_OID} "`
  only after `^[0-9a-f]{40}$` has been enforced.

---

## What this review does NOT establish

* **Nothing about the 52 REQUIRED cases on their merits**, the four consumers, or whether the
  measured defects are the right defects. That is `INSTRUMENT-REVIEW.md`'s and the batch's ground,
  not mine.
* **Nothing about `a-extract-gate.sh` beyond its preflight.** `7 of 7` / `10 of 10` were **not**
  re-measured — `GATE-BINDING.md` already says they predate this narrowing, and they still do. I ran
  that harness only far enough to reach `SUBJECT IDENTITY` and killed it before `G1`. **`G1`, `G2`,
  `G3` and the `Z-*` rows of that harness are unverified by me at this commit**, and the summary
  line `CONTROL : 10 of 10 held` under a printed `P3-provenance FAIL` is inferred from the harness's
  own `check()` replayed verbatim, not observed in a completed run.
* **Nothing about how a replace ref or a 40-hex remote-tracking ref would come to exist here.** I
  created them. I did not establish a likelihood, only that the instrument does not survive them and
  does not report them.
* **No measurement of the previous harness under a replace ref.** F1's "not new" claim is read from
  the code paths at `1517120`, not measured.
* **No claim of exhaustiveness.** I probed the vectors named in my charge plus `GIT_REPLACE_REF_BASE`
  and the attributes stack. Two of them fell open. I did not enumerate git's remaining environment
  surface, and the fact that this review found a second door after two prior reviews is itself
  evidence that "no doors remain" is not a claim measurement can support.
* **Nothing is signed, certified, ratified or accepted here.** This is a review document. Whether
  `R1-3` and `R2-3` are accepted, and what if anything is done about them, is John's.

---

*Probes, raw output and matrices were produced under a redirected `HOME`, `XDG_CONFIG_HOME`,
`GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM`; every repository carrying an adversarial ref, config or
attribute was created by this review under a scratch directory and none of them is the source
repository.*
