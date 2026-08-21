# A-EXTRACT — FIFTH INDEPENDENT INSTRUMENT REVIEW

# VERDICT: FAIL

**Two items on D-065(3)'s own list are present in the committed instrument, and one of them is
the class this review was told to prioritise.**

- **`F5-1` — A STATED REQUIREMENT SILENTLY REMOVED, AND STILL MISSING.** The `bac7cd8 → 4f1e6a3`
  edit of `a-extract-gate.sh` deleted three preflight `die` guards and one `OBSERVED` line along
  with the ref-resolution machinery it was replacing. No commit message and no evidence file
  mentions any of the four. Two of the three guards are functionally replaced by a later
  `cp -R … || die`. **The third is not replaced by anything:** `[ -n "$(ls -A
  "$ROOT/contracts/lib/$m")" ] || die "contracts/lib/$m is empty"`. `cp -R` of an empty
  directory exits 0, so an uninitialised submodule working tree is now staged silently.
  **The mechanism is the identity block's, exactly** — a replacement region bounded by "the next
  blank line" swallowed the six adjacent lines, and the author verified the new behaviour rather
  than reading what the replacement had consumed. It was found by the audit `INSTRUMENT-REVIEW-4`
  said would be needed, and it was still there at `2d6b948`.

- **`F5-2` — FOUR CONTROLS THAT CANNOT FAIL.** In `a-extract.sh`, `1-ctl`, `5-ctl`, `8-ctl` and
  `13-ctl` are functions solely of `_p0ts` / `_p0ec` / `_p0vp`, which are assigned exactly once at
  line 723 and which the unconditional `die`s at lines 724–726 already require to satisfy exactly
  those predicates. Demonstrated: in the only state where `1-ctl` could fail, the harness refuses
  at `P6` and never prints the line. `74 of 74 CONTROL held` therefore counts four lines that are
  structurally incapable of moving.

**Both items are narrow, and this document says so plainly: neither can produce a false green.**
Everything the `2d6b948` commit message claims was verified by measurement and held, both
provenance controls discriminate when driven wrong, the malformed-verdict counter is closed in
both harnesses, and **every published figure this reviewer could reach reproduced exactly.** The
verdict rests on D-065(3) naming these two classes as in scope regardless of downstream harm —
which is the same ground on which the identity block was accepted as a defect.

---

## 0. What this review was, and the ground it stood on

Read first: `docs/decisions.md` `D-065`. **The bar is faithful measurement under a
NON-ADVERSARIAL environment.** A caller who can set arbitrary git environment variables can
equally edit the harness, so that class is out of scope; known doors are scrubbed as hardening,
explicitly not a completeness claim, and **a newly named caller-controlled variable is not by
itself a FAIL**. No time was spent hunting a fifth environment variable, and none is offered as a
finding.

| | |
|---|---|
| Subject | branch `step-3/isolated-signer`, HEAD `2d6b948622d062173c5c139760e30ea7d08e2776` |
| Files reviewed | `a-extract.sh` sha256 `2095c277…07df`, `a-extract-gate.sh` sha256 `b1d8d4d2…f296`, and `CARD.md` / `COVERAGE.md` / `RESULTS.md` / `GATE-BINDING.md` |
| Environment | git 2.50.1 (Apple Git-155); bash 3.2.57; Python 3.9.6; node v26.3.0; `/usr/bin/grep` |
| Written by this review | this file only |
| Read for change | nothing. No production file, no harness, no existing evidence file, no review record was edited |
| Repositories mutated | only ones this reviewer created under its own scratch directory |

**Hygiene observed.** Output was read, never exit status alone. Every probe carries a paired
control that moved. **No harness was edited at any point** — where a fragment of a harness had to
be driven in isolation, it was extracted verbatim with `sed` and the extraction was proved
verbatim with `grep -qF` against the committed file before use. The two long runs were started
after all reading was complete and nothing was written while they ran.

---

## 1. Per-item results

| # | Assignment | Result | Measured |
|---|---|:--:|---|
| 1 | Verify each `2d6b948` claim by measurement, with a paired control that moves | **HELD** | see §2 — all five claims reproduced; both provenance controls fail when driven wrong |
| 2 | **PRIORITY** — hunt other silent removals across the six revisions | **DEFECT** | `F5-1`: four deletions at `bac7cd8 → 4f1e6a3`, one with no replacement, none disclosed. §3 |
| 3 | Every published figure measured on the file it describes | **HELD** | 21 figures re-measured, all reproduce. One overstated completeness claim, `F5-3`. §4 |
| 4 | The counter class, both harnesses | **HELD** | six malformed shapes × 2 harnesses = 12 probes, all FAIL, all counted, exit 2. §5 |
| 5 | Controls that cannot fail | **DEFECT** | `F5-2`: 4 of 74 in `a-extract.sh`. All 10 gate controls can fail. §6 |
| 6 | Baseline reproduction, twice | **HELD** | `21 of 52` / `74 of 74`, exit 1, twice, byte-identical output. §7 |
| 7 | Re-measure the gate harness independently | **HELD** | `7 of 7` / `10 of 10`, exit 0, rc=0/5/5. §8 |

---

## 2. Assignment 1 — the five claims of `2d6b948`, each measured

### 2.1 `GIT_TEMPLATE_DIR` scrubbed and `PATH` pinned by precedence, in both harnesses — HELD

`_harden_known_doors()` is byte-identical in both files (`a-extract.sh` 305–309,
`a-extract-gate.sh` 239–244) and is invoked before the first git call in each. The function was
extracted verbatim and driven with a shadowing `git` planted first on `PATH`:

```
_harden_known_doors() {
    unset GIT_TEMPLATE_DIR 2>/dev/null || true
    PATH="/usr/bin:/bin:/usr/sbin:/sbin:${PATH:-}"
    export PATH
}

--- BEFORE hardening (shadow first on PATH) ---     <- the control, and it moves
<scratch>/shadow/git
~/.foundry/bin/forge
SHADOWED-GIT
--- AFTER hardening ---
/usr/bin/git
~/.foundry/bin/forge
git version 2.50.1 (Apple Git-155)
GIT_TEMPLATE_DIR=[<unset>]
--- AFTER hardening, with GIT_TEMPLATE_DIR set by the caller ---
GIT_TEMPLATE_DIR=[<unset>]
```

The shadowing `git` is outranked, `forge` — which is not in a system directory here — is still
found, and the template variable is cleared. **Precedence, not replacement, is what the file
claims and what it does.** The gate run in §8 is the independent confirmation that the retained
tail of `PATH` really is still load-bearing: that run needed `forge` and found it.

### 2.2 The two "unconfigurable by their caller" sentences removed — HELD

```
$ git grep -n "unconfigurable" d1fa16f -- <A-EXTRACT-tests>
d1fa16f:…/COVERAGE.md:99:  … It makes these two harnesses' git calls unconfigurable by their caller, and says
d1fa16f:…/a-extract.sh:242: # calls unconfigurable by its caller. It says nothing about any other entry point.

$ git grep -n "unconfigurable" 2d6b948 -- <A-EXTRACT-tests>
(no output)
```

Exactly two, exactly where the commit says, both gone. The replacement wording in both places
states hardening rather than completeness.

### 2.3 Gate harness `--no-replace-objects` pins `0 → 7` — HELD, with a wording defect

Seven command pins at lines 296, 303, 304, 308, 321, 325, 456; an eighth occurrence at line 311
is a comment. At `d1fa16f` the count was zero. **The count of 7 is correct.** What is not correct
is the surrounding prose — see `F5-3` in §4.3.

The parallel correction for `a-extract.sh` also holds: two command pins (685, 1574), a third
occurrence at 680 being a comment.

### 2.4 `P3-provenance` verifies the clone's WORKTREE — HELD, and it genuinely fails

This is the question the assignment singled out. The control's two digest expressions and its
predicate were extracted verbatim from `a-extract-gate.sh` 321–332 and driven against a clone in
two states. **State B is the exact shape `INSTRUMENT-REVIEW-4` measured: `HEAD` still reports the
requested oid while the worktree carries another commit's tree** — produced here with
`git read-tree -u --reset`, which moves index and worktree without moving `HEAD`.

```
=== A: worktree IS the subject's tree (the paired positive) ===
  case P3-provenance CONTROL  PASS  … the clone's WORKTREE matches that commit's tree over
                                    498 tracked blob paths — expected d0a672e8e34a…, worktree d0a672e8e34a…
      [A] clone HEAD=bb664c626d592d86391f644bf014e76f2bbf7db4

=== B: HEAD still reports the subject, worktree+index carry ANOTHER commit's tree ===
  case P3-provenance CONTROL  FAIL  … over 529 tracked blob paths
                                    — expected d0a672e8e34a…, worktree d8fa94311141…
      [B] clone HEAD=bb664c626d592d86391f644bf014e76f2bbf7db4

req_fail=0 ctl_fail=1
```

**The control fires, and it fires on the worktree, with `HEAD` reporting correctly throughout.**
The predicate's `_clone_head = SUBJECT_SHA` conjunct held in both states, so the tree comparison
alone did the discriminating.

The same probe was run against `a-extract.sh`'s `P3-provenance` (lines 685–696 extracted
verbatim), with the snapshot built from a different commit and the subject argument unchanged:

```
=== A: the snapshot IS the subject's tree ===
  case P3-provenance CONTROL  PASS  … over all 498 blob paths (d0a672e8e34a…)
=== B: the snapshot is ANOTHER commit's tree ===
  case P3-provenance CONTROL  FAIL  … over all 529 blob paths (d8fa94311141…)
req_fail=0 ctl_fail=1
```

**Both sides do not move together.** The expected side is derived only from `$ROOT` +
`SUBJECT_SHA`; the actual side only from the snapshot or clone. Two of the four published digest
figures — `d0a672e8…` / 498 paths and `d8fa9431…` / 529 paths — are reproduced here as a
by-product, and they match `COVERAGE.md`'s table exactly.

### 2.5 The identity block restored, the removal accidental — HELD

Counted by call sites, as the evidence file specifies:

```
                     a-extract.sh              a-extract-gate.sh
a9059dc   hdr-call=1  identity_block=3         hdr-call=1  identity_block=3
d1fa16f   hdr-call=0  identity_block=2   <-    hdr-call=1  identity_block=3
2d6b948   hdr-call=1  identity_block=3         hdr-call=1  identity_block=3
```

Reproduces the published `1 → 0` and `3 → 2` exactly. The gate harness never lost its block. A
live run prints the five facts twice (`grep -c "harness sha256   :" run1.txt` → `2`), matching
`RESULTS.md`. The "accidental, mechanism recorded" account is consistent with the diff — **and
§3 shows the same mechanism operated once before, in the other file, and was not caught.**

---

## 3. `F5-1` — Assignment 2, the priority: a silent removal that is still present

### 3.1 Method

Both harnesses were reconstructed at all six revisions
(`0140a4f → f1c0fdd → bac7cd8 → 4f1e6a3 → d1fa16f → 2d6b948`) and every deletion was accounted
for on three axes:

1. **the scored-case set** — every `check REQUIRED|CONTROL|OBSERVED <id>` call site, diffed as a
   set across the five transitions;
2. **every deleted non-comment line** — 212 in `a-extract.sh`, 127 in `a-extract-gate.sh`,
   read individually;
3. **every deleted comment line carrying requirement language** (`must`, `require`, `never`,
   `John`, `D-0…`, `forbid`, `refus`).

Case-set movement, all five transitions, both files:

```
a-extract.sh   0140a4f→f1c0fdd  +3 REQUIRED (4e,4f,10h -> btick/tilde pairs), +4 CONTROL
                                (3 tilde -mut, +1 P3 promoted), -1 OBSERVED (P3 leaving)
               f1c0fdd→bac7cd8  no change
               bac7cd8→4f1e6a3  P3 renamed P3-provenance
               4f1e6a3→d1fa16f  no change
               d1fa16f→2d6b948  no change
gate           0140a4f→f1c0fdd  +1 CONTROL P3-subject
               f1c0fdd→bac7cd8  no change
               bac7cd8→4f1e6a3  P3-subject renamed P3-provenance;  -1 OBSERVED P2   <-- undisclosed
               4f1e6a3→d1fa16f  no change
               d1fa16f→2d6b948  no change
```

Every movement except the last-named is documented in the commit that made it, and the
`49 → 52` / `70 → 74` / `11 → 10` reconciliation table in `RESULTS.md` §0a matches this
independent recount line for line.

### 3.2 The finding

`a-extract-gate.sh` at `bac7cd8`, lines 276–287, with the deleted region marked:

```
276  if [ -z "$SUBJECT_SHA" ]; then
277      die "cannot resolve subject ref '$SUBJECT_REF' to exactly one commit in …
278                       git said: ${_rev_err:-(no diagnostic)}
279                       Missing, ambiguous, or not-a-commit is a REFUSAL here, never a fallback."
280  fi
281  [ -d "$ROOT/ts/node_modules" ] || die "ts/node_modules is absent; …"          <-- deleted
282  for m in forge-std openzeppelin-contracts; do                                 <-- deleted
283      [ -d "$ROOT/contracts/lib/$m" ] || die "submodule working tree … absent"  <-- deleted
284      [ -n "$(ls -A "$ROOT/contracts/lib/$m" 2>/dev/null)" ] || die "… is empty" <-- deleted
285  done                                                                          <-- deleted
286  check OBSERVED P2 0 "toolchain present: git, node, python3, forge; …"         <-- deleted
287                                                                                <-- the next blank line
```

**There is no blank line between the `fi` at 280 and the guards.** The next blank line is at 287.
A replacement region computed as "the ref-resolution block up to the next blank line" consumes
281–286 — *the identical mechanism recorded for the identity block, one file over and two
revisions earlier.*

`4f1e6a3`'s commit message states three rulings and eleven falsifications and names none of these
four lines. Neither does `CARD.md`, `COVERAGE.md`, `RESULTS.md` or `GATE-BINDING.md`, at that
revision or since. All four are still absent at `2d6b948`.

### 3.3 What survived, and what did not

| deleted line | replaced by | still enforced? |
|---|---|:--:|
| `[ -d "$ROOT/ts/node_modules" ] \|\| die` | line 334 `cp -R … \|\| die "cannot stage node_modules"` | **yes**, differently worded |
| `[ -d "$ROOT/contracts/lib/$m" ] \|\| die` | line 337 `cp -R … \|\| die "cannot stage contracts/lib/$m"` | **yes**, differently worded |
| `[ -n "$(ls -A …)" ] \|\| die "… is empty"` | **nothing** | **NO** |
| `check OBSERVED P2 0 "toolchain present …"` | — | n/a: `OBSERVED` asserts nothing; the underlying `command -v` `die`s survive at 280–281 |

Measured, on directories this reviewer created:

```
--- the deleted guard, applied to an EMPTY dir ---
  [ -d ]            -> TRUE  (the absence guard would NOT fire)
  [ -n ls -A ]      -> FALSE (the DELETED emptiness guard WOULD have fired)
--- what replaced it ---
  cp -R of an EMPTY dir -> exit 0, so "|| die" does NOT fire
  files staged: 0
--- and it is a gitlink in the tree, so the clone has nothing of its own ---
160000 commit bf647bd6…  contracts/lib/forge-std
160000 commit 5fd1781b…  contracts/lib/openzeppelin-contracts
```

Both dependency trees are gitlinks, so the private clone contains empty directories at those
paths and the staged copy from `$ROOT` is their only content. Line 336 then `rm -rf`s the clone's
own directory before copying. **An uninitialised submodule working tree in `$ROOT` is therefore
staged as an empty directory with no diagnostic.**

### 3.4 Severity, stated so the verdict can be judged rather than assumed

The consequence is **not** a false green. With an empty submodule tree the solidity stage cannot
build, `G1` — a REQUIRED case — fails, and the run reports *"REQUIRED FAILURES with every control
holding: the gate binding is NOT established"* at exit 1. Nothing is claimed that is untrue.

What is lost is the *diagnosis*: a preflight refusal at exit 2 with zero scored verdicts, arriving
in under a second, has become a REQUIRED failure arriving after three full gate runs and pointing
at the gate rather than at the operator's tree. That matters here for a specific reason the file
itself states: `G1` exists *"[without it] `G2` and `G3` would be satisfiable by a gate that fails
on this machine for an unrelated reason"* — and in this scenario `G2-gate` and `G3-gate` do pass,
for an unrelated reason, with `G1` the only line that moves.

**It is in scope because D-065(3) names it, not because of what it could cause.** The identity
block produced no false number either.

### 3.5 Everything else in the deletion audit is accounted for

Every other deletion across the six revisions maps to a stated change: the hardcoded `BASE_SHA`
and the defaulted `ROOT` (`f1c0fdd`); `4e`/`4f`/`10h` splitting into backtick/tilde siblings
(`f1c0fdd`); the whole ref-resolution apparatus — `_ref_candidates`, `_matching_refs`,
`_peel_to_commit`, `_independent_subject_sha`, the two ambiguity detectors, `SUBJECT_REF` —
(`4f1e6a3` Ruling 1); the four bare `run_*` one-liners, replaced by the witness-recording versions
(`4f1e6a3`); the "TWO INDEPENDENT ROUTES" claim (`4f1e6a3` Ruling 3); the arithmetic in `check()`
(`d1fa16f`); the one-blob sentinel (`d1fa16f`); `hdr "SUBJECT IDENTITY"` + `identity_block`
(`d1fa16f`, the known removal, restored at `2d6b948`). `d1fa16f → 2d6b948` deletes **no**
non-comment line from either harness. The four review records were each touched by exactly one
commit and none has been edited.

---

## 4. Assignment 3 — every published figure, measured on the file it describes

### 4.1 Reproduced exactly

| Figure | Where published | Measured here |
|---|---|---|
| `a-extract.sh` sha256 `2095c277…07df` | `RESULTS.md` | `shasum -a 256` of the committed file, and the run printed it itself |
| `a-extract-gate.sh` sha256 `b1d8d4d2…f296` | `GATE-BINDING.md`, `RESULTS.md` | same, and the gate run printed it |
| `21 of 52` REQUIRED / `74 of 74` CONTROL, exit 1 | `RESULTS.md`, `CARD.md` | §7 — twice, byte-identical |
| `7 of 7` / `10 of 10`, exit 0, rc = 0/5/5 | `GATE-BINDING.md` ×3 sections | §8 |
| 498 blob paths, digest `d0a672e8…` | harness comment, `RESULTS.md`, `COVERAGE.md` | §2.4, both harnesses agree |
| 529 paths, digest `d8fa9431…` (the other tree) | `COVERAGE.md` table | §2.4 |
| witness executions 26 / 14 / 17 / 8 | commit `4f1e6a3`, `RESULTS.md` | run 1, all four `Z-` lines |
| consumer blobs `9bcdb562…`, `7970d226…`, `1ead2f37…`, `924749d5…` | `RESULTS.md` §4 | run 1, all four `Z-` lines |
| identity block `1 → 0`, `3 → 2`, restored `1`/`3` | `RESULTS.md` §0-D065 | §2.5 |
| `9fd5790e…` was `d1fa16f`'s own gate sha | implied by the `2d6b948` diff | confirmed by hashing each revision |
| `af66a45e…` is the `f1c0fdd` gate revision | `GATE-BINDING.md` | confirmed by hashing each revision |
| REQUIRED `49→52`, CONTROL `70→74`, OBSERVED `11→10` | `RESULTS.md` §0a | independent recount of call sites, §3.1 |
| "a published figure of 9 OBSERVED was wrong; it was 11" | `RESULTS.md` §0a | recount confirms 11 at `0140a4f` |
| `TESTS.patch` applies cleanly | `RESULTS.md` §5 | `git apply --check` on a scratch extraction of `bb664c6` — clean |
| the two pre-existing tests still pass after the patch | `RESULTS.md` §5 | `Ran 2 tests … OK` |
| `TestPublishedTypeStringsSectionExtent`: 12 tests, 10 expected FAIL = **9 failures + 1 error**, 2 controls pass | `RESULTS.md` §5 | `Ran 12 tests … FAILED (failures=9, errors=1)`; the two passing are exactly `test_a_well_formed_section_is_read_whole` and `test_the_live_proposal_still_publishes_six` |
| both classes together: 14 tests, 10 expected failures | `RESULTS.md` §5 | `Ran 14 tests … FAILED (failures=9, errors=1)` |
| both fence tests fail, each its own test | `RESULTS.md` §5 | `test_a_quoted_heading_is_not_the_anchor … FAIL`, `test_a_tilde_fenced_heading_is_not_the_anchor … FAIL` |
| six §5.8 type strings, forty-one §5.7.1 identifiers | `GATE-BINDING.md`, `COVERAGE.md` | gate log: `type strings: 6/6 …`, `eval codes: 41/41 …` |
| gate matrix 7 REQUIRED / 10 CONTROL / 3 OBSERVED | `GATE-BINDING.md` | `matrix.tsv` from this reviewer's own run |

### 4.2 Reproduced, with a drift note

**"21 commits already in this repository carry an identical `scripts/check-type-strings.sh` blob
with a DIFFERENT tree"** (`COVERAGE.md`, `RESULTS.md`). Measured over `git rev-list`:

```
tip = a9059dc (HEAD when d1fa16f was being written)   -> 21     <- reproduces the published figure
tip = d1fa16f                                          -> 22
tip = 2d6b948 (today)                                  -> 25
```

**The figure was measured and is correct as of when it was taken.** It is a count over history
and grows with every commit, so it is stale by four today. Not a defect; recorded because the
number will keep moving and a later reader should not be surprised by it.

### 4.3 `F5-3` — one figure's surrounding prose overstates, in the shape D-065(2) forbids

Three files describe the new pinning as complete:

- `GATE-BINDING.md`: *"`--no-replace-objects` pinned on **all 7** git commands (it was **0**)"*
- `COVERAGE.md`: *"It now pins on **every command it runs**"*
- `CARD.md`: *"It now pins on **every command**"*

Measured — `a-extract-gate.sh` issues **ten** git invocations, of which **seven** are pinned:

```
pinned  (7): 296 cat-file · 303 clone · 304 checkout · 308 rev-parse · 321 ls-tree ·
             325 ls-files · 456 show
unpinned(3): 278 git --version · 327 git hash-object --stdin-paths · 452 git status --porcelain
```

**The count 7 is right; "all", "every command it runs" and "every command" are not.** The
consequence is nil — `hash-object --stdin-paths` performs no object lookup and cannot be reached
by replacement, `--version` touches no object, and `git status` is covered by the exported
`GIT_NO_REPLACE_OBJECTS=1` — so this is a wording defect, not a measurement defect.

It is reported because it is **the same completeness-claim shape D-065(2) forbids**, appearing in
the same three documents whose `2d6b948` revision deleted two sentences for exactly that reason,
and because this commit was otherwise scrupulous about it (it volunteered the correction
"`a-extract.sh` pins on 2 commands, not 3 — the third occurrence there is a comment"). The
accurate sentence is *"seven of the ten git invocations are pinned; the other three cannot be
reached by object replacement."*

### 4.4 Figures I could not re-measure, and why

- **`RESULTS.md` §6 run 3 — `24 of 52`** at a one-consumer-changed private clone
  (`32f8d4cd…`, blob `b4ca2c4f…`). The clone was throwaway and the commit does not exist here.
  The claim is internally consistent (the three exact-token cases named are the three that would
  move) but is **not independently reproduced by this review**.
- **The `GIT_TEMPLATE_DIR` figures** — *"16 subject repositories … executing 16 times … `74 of 74`
  held"*. Inherited from `INSTRUMENT-REVIEW-4` and attributed there. Out of scope under D-065(1);
  not re-measured.
- **The `hooks/pre-commit` + `core.fsmonitor=/bin/echo` paired-control table** (`COVERAGE.md`).
  Same class; requires removing the hardening from the harness to reproduce, which this review
  would not do. Not re-measured.
- **`RESULTS.md` §0a's `28 of 34, 52 controls` / `28 of 49, 70 controls`** — figures for harness
  revisions two and three generations back. Not re-measured; they are presented as history and
  are marked as such.
- **`RESULTS.md` §6 run 2** used subject `HEAD`, which the current grammar refuses. It is
  **correctly banner-marked** *"PARTLY SUPERSEDED BY §0-OID"* with the reason named. Good
  practice, recorded as such.

---

## 5. Assignment 4 — the counter class, both harnesses

`check()` was extracted verbatim from each committed harness (`sed -n '/^check() {/,/^}/p'`), the
extraction proved verbatim with `grep -qF` against the source, then driven with each malformed
shape. The summary tally and exit logic were likewise copied verbatim.

```
########## a-extract.sh ##########                    ########## a-extract-gate.sh ##########
  case EMPTY      CONTROL  FAIL                         case EMPTY      CONTROL  FAIL
  case WHITESPACE CONTROL  FAIL                         case WHITESPACE CONTROL  FAIL
  case DOUBLEZERO CONTROL  FAIL   (value "00")          case DOUBLEZERO CONTROL  FAIL
  case MINUSZERO  CONTROL  FAIL   (value "-0")          case MINUSZERO  CONTROL  FAIL
  case MULTILINE  CONTROL  FAIL   (value "0\n1")        case MULTILINE  CONTROL  FAIL
  case ERRORWORD  CONTROL  FAIL   (value "abc")         case ERRORWORD  CONTROL  FAIL
  case ZEROTRAIL  CONTROL  FAIL   (value "0 ")          case ZEROTRAIL  CONTROL  FAIL
  case REQEMPTY   REQUIRED FAIL                         case REQEMPTY   REQUIRED FAIL
  case GOODZERO   CONTROL  PASS   <- paired control     case GOODZERO   CONTROL  PASS
  case OBS        OBSERVED ....                         case OBS        OBSERVED ....

req_fail=1 ctl_fail=7                                 req_fail=1 ctl_fail=7
  REQUIRED : 0 of 1 held                                REQUIRED : 0 of 1 held
  CONTROL  : 1 of 8 held                                CONTROL  : 1 of 8 held
  -> CONTROL FAILURE path, exit 2                       -> CONTROL FAILURE path, exit 2
```

**Every malformed shape counts, the tallies move, and the run takes the exit-2 path in both
harnesses.** The paired control — a literal `0` — is the only value that passes, so the probe is
not merely rejecting everything. `"0 "` with a trailing space is worth naming: it fails, which is
correct, and it is a shape the old arithmetic form would have *accepted*. `OBSERVED` with an empty
verdict prints `....` and counts toward neither tally, which is the documented convention.

One residual: `check` called with fewer than four arguments would expand an unset `$4` under
`set -u` and abort the shell mid-run. The output is then visibly truncated with no `SUMMARY`, so
it cannot read as a pass — noted, not counted as a defect.

---

## 6. `F5-2` — Assignment 5: controls that cannot fail

### 6.1 `a-extract-gate.sh` — all ten can fail

| Control | Can it fail? | Note |
|---|:--:|---|
| `P3-provenance` | **yes** | demonstrated in §2.4 |
| `G1-stages`, `G1-green` | yes | read the G1 log for banners and success lines |
| `G1-order` | yes | absent banner makes the `-lt` comparison error, which the `&&` chain turns into `1` |
| `G2-mut`, `G3-mut` | yes | the python mutator's `assert` exit status plus a re-read of the mutated file |
| `G2-scope`, `G3-scope` | yes, but redundant | each is a strict sub-conjunction of the REQUIRED `*-unmasked` case beside it, so it cannot fail without that REQUIRED case failing too. It still fires; it is simply not independent of the case it polices |
| `Z-clean`, `Z-signed` | yes | live-tree comparisons |

### 6.2 `a-extract.sh` — four of seventy-four cannot fail

`_p0ts`, `_p0ec` and `_p0vp` are assigned **exactly once**, at line 723, and never reassigned:

```
723  _p0ts="$(run_ts "$P0")"; _p0ec="$(run_ec "$P0")"; _p0vp="$(run_vp "$P0")"
724  has    "$_p0ts" "$TS_OK"   || die "the base subject does not pass check-type-strings.sh: …"
725  has    "$_p0ec" "$EC_OK"   || die "the base subject does not pass check-eval-codes.sh: …"
726  has_re "$_p0vp" "$VP_OK_RE"|| die "the base subject does not pass the verifier §5.8 consumer"
```

Every later control built only from those three variables is therefore true whenever the run
reaches it:

| Control | Line | Predicate | Status |
|---|---|---|---|
| `1-ctl` | 795 | `has $_p0ts $TS_OK && has $_p0ec $EC_OK` | **cannot fail** — both conjuncts are line 724/725 |
| `5-ctl` | 1036 | `has $_p0ts $TS_OK` | **cannot fail** — line 724 |
| `8-ctl` | 1161 | `has $_p0ts $TS_OK && has $_p0ec $EC_OK` | **cannot fail** — identical to `1-ctl` |
| `13-ctl` | 1535 | `ts_class($_p0ts)=="success" && vp_class($_p0vp)=="success"` | **cannot fail** — those classes are `TS_OK` and `^OK$`, i.e. lines 724/726 |
| `1c-ctl` | 785 | `vp_class($_p0vp)=="success" && ! has $_p0vp "5.8 "` | first conjunct guaranteed; second can in principle move |
| `6-ctl` | 1070 | `grep -cE '"MandatePayload\(' == 1 && has $_p0ts $TS_OK` | first conjunct reads the subject and can move; second guaranteed |

`10-ctl` (1231) uses `_p0vh`, which has **no** preceding `die`, so it is a genuine control — but
it is the same expression as REQUIRED case `11a` (1324), so the two are one assertion counted
twice rather than a case and an independent control.

**Demonstrated rather than argued.** A clone of this repository was made under scratch, the §5.8
`ActionPayload` publication transposed there, committed **in the clone only**, and the committed
harness pointed at that commit:

```
  case P5         OBSERVED ....  all six anchor headings occur exactly once in the base proposal

  PREFLIGHT FAILED: the base subject does not pass check-type-strings.sh: type strings:
                    DRIFT in ActionPayload
  spec  : ActionPayload(… bytes32 policyHash,bytes32 mandateHash,uint64 deadline)
  source: ActionPayload(… bytes32 mandateHash,bytes32 policyHash,uint64 deadline)
  exit 2

1-ctl printed in the P6-die run  : 0
1-ctl printed in the healthy run : 1     <- the paired control, and it moves
  case 1-ctl      CONTROL  PASS  opposite outcome: with the sections present both checkers report success
```

**The only state in which `1-ctl` could fail is one the harness refuses before reaching it.** The
substance is enforced — by a stricter response, `die` at exit 2 with zero scored verdicts — so
nothing false is produced. What is produced is a headline `74 of 74 CONTROL held` in which four
lines were never at risk. D-065(3) names this class first.

### 6.3 One more control worth naming, below the finding line

`P8` (754) begins `has "$H571" "the identifiers are not normative"`. `H571` is a string constant
declared at line 171 of the same file, so that conjunct compares a literal against a substring of
itself and is always true. The second conjunct does read §5.7.1's body out of the subject and can
move, so `P8` as a whole is falsifiable. Recorded as a residual, not a finding.

---

## 7. Assignment 6 — baseline reproduction at `bb664c6`, twice

```
$ a-extract.sh . bb664c626d592d86391f644bf014e76f2bbf7db4

  harness sha256   : 2095c27732e05e40d3f574eddfb7a61ef1ed86c0913f6ba1b016ae9c264507df
  repository       : ~/Projects/Sentinel
  requested subject: bb664c626d592d86391f644bf014e76f2bbf7db4
  resolved subject : bb664c626d592d86391f644bf014e76f2bbf7db4
  pre-repair ref   : bb664c626d592d86391f644bf014e76f2bbf7db4

  REQUIRED : 21 of 52 held
  CONTROL  : 74 of 74 held
  exit 1   — REQUIRED FAILURES with every control holding: the defects are observed.
```

**Run twice; `diff` of the two captured outputs is empty.** Wall time ≈ 1 m 43 s each. The five
identity facts print twice per run.

Case set, reason vocabulary, expected outcomes and exclusions versus `64d9897`: **unchanged.**
The scored-case-id set is byte-identical across `4f1e6a3 → d1fa16f → 2d6b948`, and
`d1fa16f → 2d6b948` deletes no non-comment line from `a-extract.sh` at all — its 54 additions and
2 deletions are the hardening block, the restored identity call, and comments. **Delta: zero.**

`P3-provenance` reports 498 blob paths, digest `d0a672e8e34a…`; all four `Z-` consumer controls
report their `bb664c6` blobs with 26 / 14 / 17 / 8 recorded executions; `Z-clean` reports 0
changed paths; `Z-gate5` and `Z-signed` hold.

---

## 8. Assignment 7 — the gate harness, re-measured by this reviewer

Run in full, alone, ~30 minutes, three complete fast-gate runs against a private clone:

```
  case P3-provenance CONTROL  PASS  … the clone's WORKTREE matches that commit's tree over
                                    498 tracked blob paths — expected d0a672e8e34a…, worktree d0a672e8e34a…
  case G1         REQUIRED PASS  unchanged fast gate prints GATE PASSED (supervisor rc=0)
  case G1-stages  CONTROL  PASS      case G1-order  CONTROL PASS      case G1-green CONTROL PASS
  case G2-mut     CONTROL  PASS
  case G2-named   REQUIRED PASS      case G2-gate   REQUIRED PASS (rc=5)   case G2-unmasked REQUIRED PASS
  case G2-scope   CONTROL  PASS
  case G3-mut     CONTROL  PASS
  case G3-named   REQUIRED PASS      case G3-gate   REQUIRED PASS (rc=5)   case G3-unmasked REQUIRED PASS
  case G3-scope   CONTROL  PASS
  case Z-clean    CONTROL  PASS      case Z-signed  CONTROL PASS

  harness sha256   : b1d8d4d287d67045cb892e048788edcbbb171b07ea4ce36c2ddfdec24680f296
  REQUIRED : 7 of 7 held
  CONTROL  : 10 of 10 held
  exit 0
```

**`7 of 7` / `10 of 10` / exit 0 / rc = 0, 5, 5 — reproduced independently, not inherited.** The
figures in `GATE-BINDING.md`'s three sections agree with this run. The harness's own closing
disclaimer — that the deep profile was not invoked and D-059(7) is therefore not fully discharged
— printed as published.

HEAD's deliberate redness is not treated as a finding: `cefc135` applied `TESTS.patch` and
ratcheted the floor 209 → 221, so the verifier suite and the fast gate fail at HEAD by design, and
`bb664c6` is the correct subject for `G1`.

---

## 9. Residuals

| id | Residual | Class |
|---|---|---|
| `R5-a` | `G2-scope` / `G3-scope` are strict sub-conjunctions of the REQUIRED `*-unmasked` cases beside them; `10-ctl` is the same expression as REQUIRED `11a`. Falsifiable, but not independent of what they police | instrument, minor |
| `R5-b` | `P8`'s first conjunct compares a harness constant against a substring of itself | instrument, minor |
| `R5-c` | The "21 commits share this blob with a different tree" figure is a count over history; correct when taken, now 25 | figure drift |
| `R5-d` | `RESULTS.md` §6 run 3 (`24 of 52`) rests on a throwaway clone that no longer exists; not independently reproducible | evidence |
| `R5-e` | The gate harness's actual-side path list comes from the clone's **index** (`ls-files`), not from the worktree, so an untracked file in the clone would not move the digest. Cannot arise from `clone`+`checkout` under ordinary conditions | limitation |
| `R5-f` | `git hash-object --stdin-paths` applies configured clean filters by default. Correct behaviour — it is how git computed the blob — but it means a `.gitattributes` clean filter *inside the subject tree* participates in the provenance digest on the actual side only. No `.gitattributes` filter exists in the subject; recorded as a boundary of the control | limitation |
| `R5-g` | **D-065(2) residual, out of scope by ruling.** No environment door was hunted and none is offered. The two harnesses' `PATH` pin is by precedence and the retained tail is load-bearing (`forge`), so the tool search path is not exhaustively controlled — as the files now correctly say. Under D-065(1) this is not a defect; under D-065(5) it would have to be re-taken if the caller ever stops being the operator | out of scope |
| `R5-h` | `check` invoked with fewer than four arguments aborts the shell under `set -u`. Output is then visibly truncated with no `SUMMARY`, so it cannot read as a pass | instrument, minor |

---

## 10. What this review does NOT establish

1. **It says nothing about whether the four consumers are right.** It reviews the instrument.
2. **It does not re-derive the 31 REQUIRED failures.** It confirms the count reproduces and the
   controls hold; it did not re-argue each case's semantics.
3. **It did not run the deep gate profile.** `D-059(7)` remains partly undischarged exactly as
   `GATE-BINDING.md` STATUS says.
4. **It did not reproduce the `GIT_TEMPLATE_DIR` or `PATH`-shadowing paired-control tables as
   published** — doing so requires removing hardening from the committed harness, which this
   review would not do. The mechanism was verified on an extracted fragment instead.
5. **It did not reproduce `RESULTS.md` §6 run 3**, and says so in §4.4 rather than inheriting it.
6. **It did not audit the evidence files' deletions across all six revisions** with the rigour
   applied to the harnesses; assignment 2 scoped that audit to the harnesses. The `2d6b948`
   evidence deletions were checked and are all accounted for, and the four review records are
   confirmed untouched since creation.
7. **It cannot discriminate whether `F5-1` was accidental or deliberate.** The line adjacency in
   §3.2 is consistent with the same blank-line-bounded replacement that took the identity block,
   and nothing suggests intent — but this reviewer has no access to the edit that made it and does
   not claim to know.
8. **It establishes nothing about Sentinel's production guards, Batch A1's `R-C` residual, or
   `D-055`.** Nothing here is a sign-off, a ratification, or a gate.

---

## 11. What would close `F5-1` and `F5-2`

Offered as scope, not as a decision — John's to rule on.

- **`F5-1`:** restore an emptiness refusal for both dependency trees at gate preflight (one line
  each), and record the removal and its restoration in the evidence, as the identity block's was.
  The deletion is history and should not be edited out of `4f1e6a3`.
- **`F5-2`:** either give the four controls an input that the `P6` `die` does not already
  guarantee, or reclassify them as `OBSERVED` and let the control tally fall to 70 — the tally
  should count lines that can move.
- **`F5-3`:** replace "all 7" / "every command" with the measured statement in §4.3.

**None of this is signed, certified, ratified, published or renamed. Batch A1 stays closed and
D-055 remains NOT MET.**
