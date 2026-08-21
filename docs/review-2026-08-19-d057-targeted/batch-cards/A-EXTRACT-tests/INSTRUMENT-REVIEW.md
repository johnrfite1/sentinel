# A-EXTRACT — INDEPENDENT INSTRUMENT REVIEW

**VERDICT: FAIL**

Reviewer: an independent agent that authored none of `a-extract.sh`, its cases, or its
evidence. Subject of review: the harness at `f1c0fdd`, branch `step-3/isolated-signer`.
Harness sha256 `ea661affb969eb075d84ca22400a18fa3ff2ee5966fea01e5d2c48a9be720a53`
(printed by every run as `P0`, and matching the committed file).

This reviews the INSTRUMENT, not the defects it hunts.

## The verdict in one paragraph

**The blocking defect is genuinely corrected.** The subject is now an argument, the snapshot
is built from the resolved subject, and I proved — from outside the harness, using bytes only
my scratch commit could have produced — that the consumer the harness actually EXECUTES comes
from the named subject and not from a constant. Assignments 1, 2 and 4 are established.
**The verdict is FAIL on assignment 3 alone:** a genuinely ambiguous ref — a branch and a tag
of the same name — is *not* refused. The harness silently selects the tag, suppresses git's
ambiguity warning twice over, runs a complete 126-verdict measurement, exits `1` (the ordinary
"defects observed" path), and `P3` — the control promoted from OBSERVED specifically to close
this class — reports **PASS** with the words "resolves to exactly one commit". The harness's
own comment names this exact case as one it refuses. That claim is false. A silent
precedence tie-break, certified green by a control that re-asks the same question, is the
defect class this batch exists to falsify, reproduced inside the correction to it.

Severity is bounded and stated plainly below: the fail-open is not reachable in the primary
repository as it stands today (zero tags, no head/tag name collision). It is a latent
fail-open and a false self-description, not a live wrong number.

---

## Per-item results

| # | Assignment | Result | Key measurement |
|---|---|---|---|
| 1 | Baseline reproduction, stable across two runs | **HOLD** | `21 of 52 REQUIRED`, `74 of 74 CONTROL`, exit 1 — twice, matrices byte-identical; reproduced a third time from an independent clone |
| 2 | Subject provenance — snapshot, integrity control, and a moving verdict | **HOLD** | Executed consumer's sha256 `26998f75…` = my scratch blob (proved by an out-of-harness execution witness); `Z-check-eval-codes.sh` reported the same; `2a`, `12suffix`, `12prefix` moved FAIL→PASS; totals `21 → 24 of 52` |
| 3 | Fail-closed on bad subjects (5 required cases) | **FAIL** | 4 of 5 fail closed with zero scored verdicts. **Ambiguous refname fails OPEN**: exit 1, 126 scored verdicts, `P3` PASS |
| 4 | Source repository clean after every run; no git config written | **HOLD** | `git status --porcelain` empty; `.git/config` unchanged; `.git/objects` and `.git/index` mtimes predate the first run |
| — | Case-set accounting vs `0140a4f` | **HOLD** | Every movement explained; nothing unaccounted |

Supplementary confirmations (all requested explicitly), each **true**:

| Claim | Result |
|---|---|
| `PRE_REPAIR_SHA` retained as a named reference and never archived | **TRUE** |
| `Z-clean` / `Z-gate5` / `Z-signed` still about the LIVE tree, not the subject snapshot | **TRUE** — proved by a probe in which exactly those three moved |
| Every run prints harness hash, sanitized repository path, requested ref, resolved subject, pre-repair reference — separately | **TRUE for measuring runs**, with two sanitization residuals (R3, R4) |
| Case semantics, reason vocabulary, expected outcomes and exclusions unchanged | **TRUE** |

---

## Assignment 1 — baseline reproduction

**Probe.** Two runs of the committed harness against the primary repository with the subject
named explicitly, each with an isolated `HOME`, `XDG_CONFIG_HOME`, `GIT_CONFIG_GLOBAL`,
`GIT_CONFIG_SYSTEM` and `GIT_CONFIG_NOSYSTEM=1`, writing the case matrix to separate files:

```
a-extract.sh . bb664c626d592d86391f644bf014e76f2bbf7db4
```

**Observed output (run 1 summary, verbatim except for the sanitized path):**

```
== SUMMARY ==
  harness sha256   : ea661affb969eb075d84ca22400a18fa3ff2ee5966fea01e5d2c48a9be720a53
  repository       : ~/Projects/Sentinel
  requested ref    : bb664c626d592d86391f644bf014e76f2bbf7db4
  resolved subject : bb664c626d592d86391f644bf014e76f2bbf7db4
  pre-repair ref   : bb664c626d592d86391f644bf014e76f2bbf7db4

  REQUIRED : 21 of 52 held
  CONTROL  : 74 of 74 held

  REQUIRED FAILURES with every control holding: the defects are observed.
```

Exit status 1. Run 2 produced the same summary and a **byte-identical case matrix**
(`diff` of the two TSVs is empty). A third reproduction from a throwaway clone of the
repository, same subject ref, also produced a byte-identical matrix — so the number is a
property of the subject, not of the working copy it was read from.

**What moved.** Nothing, and that is the assertion: the same subject twice gives the same
124-verdict matrix. The control that this probe is paired against is Assignment 2's scratch
run, which *did* move — without it, "stable" would be indistinguishable from "stuck", which
is precisely the defect under repair.

---

## Assignment 2 — subject provenance (the decisive one)

### Construction

A throwaway clone (`--no-hardlinks --no-local`) of the repository was made in scratch space,
its dependency tree copied in, and a scratch commit created on a new branch. The commit
changes one consumer, `scripts/check-eval-codes.sh`, in two ways:

1. **A real behavioural change** — the membership test at the `for code in $codes` loop was
   changed from a substring match to an exact-token match:

   ```
   -    grep -q "$code" "$SPEC_SECTION" || missing="$missing $code"
   +    grep -qE "(^|[^A-Za-z0-9_])${code}([^A-Za-z0-9_]|$)" "$SPEC_SECTION" || missing="$missing $code"
   ```

2. **An out-of-harness execution witness** — three lines that append the consumer's own
   working directory and the sha256 of the file being executed to a path named by an
   environment variable, defaulting to `/dev/null`:

   ```
   printf '%s\t%s\n' "$PWD" "$(shasum -a 256 "${BASH_SOURCE[0]}" | awk '{print $1}')" \
       >> "${A_EXTRACT_WITNESS:-/dev/null}" 2>/dev/null || true
   ```

The witness file is created by me, written by the extracted consumer at execution time, and
read by me after the run. **The harness never touches it and cannot report on it.** This is
what makes the provenance finding independent of the harness's own controls.

Blob hashes of `scripts/check-eval-codes.sh`, computed by me directly from the object
database, not taken from any harness output:

| Commit | sha256 of the consumer |
|---|---|
| `bb664c6` (pre-repair) | `7970d22674643fceca848a34b68119dc4957fbc7169a37f2036f4e17c8fe6123` |
| `f1c0fdd` (current) | `7970d226…` (identical to `bb664c6`) |
| scratch commit `3aa3997` | `26998f75d9c21cedf3fd494b0d0eb1ee512c94d9d27451d1c231c35762d5c940` |

### (a) The changed bytes are present in the snapshot the harness extracted

Run: `a-extract.sh <clone> 3aa39970a99ae51af1e13ff063e1cc8c155894e0`

Witness file after the run — **14 invocations, one distinct file hash:**

```
distinct sha256 of the executed check-eval-codes.sh:
  26998f75d9c21cedf3fd494b0d0eb1ee512c94d9d27451d1c231c35762d5c940

distinct working directories:
  <tmp>/a-extract.XXXXXX/s-p0        <tmp>/a-extract.XXXXXX/s-c1b
  <tmp>/a-extract.XXXXXX/s-c2        <tmp>/a-extract.XXXXXX/s-c2c
  <tmp>/a-extract.XXXXXX/s-c3        <tmp>/a-extract.XXXXXX/s-c4b
  <tmp>/a-extract.XXXXXX/s-c4f       <tmp>/a-extract.XXXXXX/s-c4f-tilde
  <tmp>/a-extract.XXXXXX/s-c7b       <tmp>/a-extract.XXXXXX/s-c8c
  <tmp>/a-extract.XXXXXX/s-c8d       <tmp>/a-extract.XXXXXX/s-c12ctl
  <tmp>/a-extract.XXXXXX/s-c12prefix <tmp>/a-extract.XXXXXX/s-c12suffix
```

Every executed copy — including the preflight base subject `s-p0` — carried the scratch
commit's bytes, and every subject directory lies inside the harness's own private scratch
area, not in the clone and not in the primary repository. This is direct evidence about what
was extracted and run, not a restatement of a harness claim.

### (b) The consumer-integrity control compares against the scratch commit

```
case Z-check-eval-codes.sh CONTROL  PASS  the consumer under test is byte-identical to
  SUBJECT_SHA 3aa39970a99ae51af1e13ff063e1cc8c155894e0: check-eval-codes.sh 26998f75…
```

`26998f75…` is the value I computed independently in the table above. It is **not**
`7970d226…`, which is what `bb664c6` would have produced and what the pre-repair instrument
did produce. The other three `Z-<consumer>` controls likewise named `SUBJECT_SHA
3aa3997…`.

### (c) A verdict actually moved

```
REQUIRED : 24 of 52 held      (baseline: 21 of 52)
CONTROL  : 74 of 74 held
```

Matrix diff against the baseline — **exactly three rows, nothing else:**

```
2a         REQUIRED  FAIL  ->  PASS
12suffix   REQUIRED  FAIL  ->  PASS
12prefix   REQUIRED  FAIL  ->  PASS
```

These are precisely the three exact-membership cases the scratch change repairs. A
subject-selection mechanism that resolved correctly but still measured the old bytes would
have printed `21 of 52` here.

### The control that had to move — and did

The strongest single discriminator: **the same repository, the same live working tree**
(the clone still had the scratch commit checked out), only the subject ref changed.

```
a-extract.sh <clone> bb664c626d592d86391f644bf014e76f2bbf7db4

  requested ref    : bb664c626d592d86391f644bf014e76f2bbf7db4
  resolved subject : bb664c626d592d86391f644bf014e76f2bbf7db4
  REQUIRED : 21 of 52 held
  CONTROL  : 74 of 74 held

case Z-check-eval-codes.sh CONTROL PASS ... check-eval-codes.sh 7970d226…
witness file: 0 lines
```

Zero witness lines: the pre-repair consumer has no witness code, so *nothing* was executed
from the live tree. The matrix is byte-identical to the primary-repository baseline. **The
subject ref — not the live tree, not `HEAD`, not a constant — selects what is measured.**

### The original defect, reproduced live for contrast

The `0140a4f` harness was run against the same clone, whose `HEAD` was the scratch commit:

```
case P3  OBSERVED ....  WARNING: HEAD is 3aa39970a99ae51af1e13ff063e1cc8c155894e0,
                        not the demonstrated base bb664c626d592d86391f644bf014e76f2bbf7db4

  REQUIRED : 21 of 49 held
  CONTROL  : 70 of 70 held
```

The pre-repair instrument, pointed at a repaired tree, reported the pre-repair number with
all seventy controls green and an OBSERVED line that could not fail. That is the defect,
demonstrated, on the same repository where the corrected instrument reports `24 of 52`.

---

## Assignment 3 — fail-closed on bad subjects — **FAIL**

Verdict counting below is on OUTPUT, not exit status: a run "measured nothing" only if it
emitted zero lines carrying a `PASS` or `FAIL` case status. `OBSERVED` preflight lines print
`....` and are not verdicts.

| Bad subject | Exit | Scored verdicts emitted | Fail-closed? |
|---|---|---|---|
| no arguments at all | 2 | 0 | yes |
| one argument (repository only) | 2 | 0 | yes |
| invalid ref (`definitely-not-a-ref-xyz`) | 2 | 0 | yes |
| missing repository (path does not exist) | 2 | 0 | yes |
| path that is not a git repository | 2 | 0 | yes |
| ref resolving to a tree, not a commit | 2 | 0 | yes |
| ambiguous **abbreviated object name** (3 hex chars matching two commits) | 2 | 0 | yes |
| **ambiguous refname (branch and tag of the same name)** | **1** | **126** | **NO** |

The seven closed cases each print a named diagnostic, for example:

```
  PREFLIGHT FAILED: an evidentiary run requires BOTH a repository and a subject ref.
  Received 0 argument(s). There is no default subject, by design.

  PREFLIGHT FAILED: cannot resolve subject ref 'definitely-not-a-ref-xyz' to exactly one
    commit in <repo>.
    git said: fatal: Needed a single revision
    A ref that is missing, ambiguous, or not a commit is a REFUSAL here, never a fallback.
```

### The fail-open, in full

**Construction.** In the throwaway clone, a branch and a tag of the same name were created
pointing at *different* commits — the genuinely ambiguous case, not an invalid ref wearing a
different hat:

```
bb664c626d592d86391f644bf014e76f2bbf7db4 refs/heads/ambig
f1c0fddad382d34d589df3e0274e25363280abd8 refs/tags/ambig
```

**What git actually does** (measured, not assumed):

```
$ git rev-parse --verify "ambig^{commit}"
f1c0fddad382d34d589df3e0274e25363280abd8
exit 0
stderr: warning: refname 'ambig' is ambiguous.

$ git rev-parse --verify --quiet "ambig^{commit}"     # the form the harness uses
f1c0fddad382d34d589df3e0274e25363280abd8
exit 0
(no warning at all)
```

`--verify` refuses an ambiguous *abbreviated object name* — I confirmed that separately, and
that path is closed. It does **not** refuse an ambiguous *refname*; it warns and applies
`refs/tags/` precedence. `--quiet` suppresses the warning, and the harness additionally
discards stderr with `2>/dev/null`, so the diagnostic is destroyed twice before anyone could
read it.

**What the harness did:**

```
== SUMMARY ==
  requested ref    : ambig
  resolved subject : f1c0fddad382d34d589df3e0274e25363280abd8
  pre-repair ref   : bb664c626d592d86391f644bf014e76f2bbf7db4

  REQUIRED : 21 of 52 held
  CONTROL  : 74 of 74 held

  REQUIRED FAILURES with every control holding: the defects are observed.
```

Exit status **1** — the ordinary, expected-shape exit. 126 scored verdicts emitted. All 74
controls green. **A reader is given a complete, confident, fully-controlled measurement of a
commit they did not choose, and nothing in the output says so.**

**The promoted control certifies it:**

```
case P3  CONTROL  PASS  the requested ref 'ambig' resolves to exactly one commit and that
                        commit is the recorded SUBJECT_SHA f1c0fddad382d34d589df3e0274e25363280abd8
```

**Why `P3` cannot catch this.** Its predicate is:

```
_subject_recheck="$(cd "$ROOT" && git rev-parse --verify --quiet "${SUBJECT_REF}^{commit}" 2>/dev/null)" || _subject_recheck=""
check CONTROL P3 "$([ -n "$SUBJECT_SHA" ] && [ "$_subject_recheck" = "$SUBJECT_SHA" ] && \
      [ "${#SUBJECT_SHA}" = "40" ] && echo 0 || echo 1)" ...
```

`-n "$SUBJECT_SHA"` is guaranteed by the `die` immediately above it. `${#SUBJECT_SHA} = 40`
is guaranteed by `rev-parse`'s output format. The remaining conjunct re-runs the **identical
command** and compares the answer to itself. A deterministic wrong answer is self-consistent,
so `P3` ratifies it. Outside a concurrent ref update between two adjacent `git` calls, `P3`
has no falsifying input at all — and I have the empirical demonstration above that it passes
on the one condition its own comment says it exists to close.

**The harness's comment is false about its own behaviour.** Immediately above the resolution
block it reads: `--verify` refuses an ambiguous ref — "an abbreviated SHA matching two
objects, a branch and a tag of the same name — instead of silently choosing one", and adds
that a first-match tie-break in this instrument "would be indefensible". The first clause is
true; the second is not; and the harness does silently choose one.

**The sibling carries the same mechanism.** `a-extract-gate.sh` resolves its subject with the
same `git rev-parse --verify --quiet "${SUBJECT_REF}^{commit}" 2>/dev/null` and pairs it with
`P3-subject`, a control of the same self-comparing shape. The sibling was not run in this
review; the finding there is by reading, and is flagged rather than measured.

**Reachability today.** The primary repository has **zero tags** and no head/tag name
collision, so no run against it as it stands can hit this. The fail-open is latent, and it
becomes live the moment a release tag shares a name with a branch — which is a normal thing
for a repository to do.

---

## Assignment 4 — repository cleanliness

**Primary repository, after every run in this review** (two baseline runs plus every failure
probe, all pointed at it or reading from it):

```
$ git status --porcelain
(empty)
```

No git configuration was written into it:

- `.git/config` modification time is unchanged and predates this session by weeks.
- `git config --local --list` is identical to the listing taken before the first run: the
  same 18 keys, no additions.
- `.git/objects` and `.git/index` modification times **predate my first harness run by several
  minutes**, so the harness wrote no objects and touched no index.

**Throwaway clone**, after the scratch-subject run and after every failure probe:
`git status --porcelain` empty.

The harness redirects `HOME`, `XDG_CONFIG_HOME`, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM`,
sets `GIT_CONFIG_NOSYSTEM=1` and unsets the `GIT_DIR` family for its own run; I additionally
redirected all of them from outside for every scored run, so neither the harness's isolation
nor mine is the sole thing being relied on.

**Caveat on `Z-clean`.** It counts `git status --porcelain` only over
`Sentinel_Protocol_Lab_Proposal_v0_2.md`, `ts/src/signer/eip712.ts`, `docs/ablation-report.md`,
`scripts` and `verifier`. It is a boundary-scoped assertion, not a whole-repository one, and
it is a *state* check rather than a *delta* check — it fails on dirt that was there before the
run started. The whole-repository verification above is mine, not its.

---

## Live-tree scope of `Z-clean`, `Z-gate5`, `Z-signed`

**Probe.** The clone's live working tree was dirtied in three places — all uncommitted, so
the subject commit was untouched: a byte appended to `scripts/check-type-strings.sh`, a byte
appended to `docs/gate-s2-evidence.md`, and one `§2` capability-table row given a trailing
space in `Sentinel_Protocol_Lab_Proposal_v0_2.md`. The harness was then run with the **clean**
scratch commit as subject.

**Observed:**

```
case Z-check-type-strings.sh   CONTROL  PASS  ... byte-identical to SUBJECT_SHA 3aa3997…: 9bcdb562…
case Z-check-eval-codes.sh     CONTROL  PASS  ... byte-identical to SUBJECT_SHA 3aa3997…: 26998f75…
case Z-check-vendor-honesty.sh CONTROL  PASS  ... byte-identical to SUBJECT_SHA 3aa3997…: 1ead2f37…
case Z-test_verifier.py        CONTROL  PASS  ... byte-identical to SUBJECT_SHA 3aa3997…: 924749d5…
case Z-clean    CONTROL  FAIL  ... (2 changed path(s) in the boundary)
case Z-gate5    CONTROL  FAIL  Gate 5 untouched IN THE LIVE TREE ...
case Z-signed   CONTROL  FAIL  docs/gate-s2-evidence.md IN THE LIVE TREE ...

REQUIRED : 24 of 52 held
CONTROL  : 71 of 74 held
```

Exit status 2 (the control-failure path). The matrix diff against the clean scratch run is
**exactly those three rows and nothing else**, and the execution witness still reported the
subject's bytes, not the live tree's.

This discriminates both directions at once: the three live-tree controls are live and
falsifiable and are about the live tree; the four `Z-<consumer>` controls are about the
subject and are indifferent to live-tree dirt; and the measured `24 of 52` did not move,
because the measurement is on the snapshot. **The live-tree protection did not silently
become subject-scoped.**

## `PRE_REPAIR_SHA` is never archived

Every use in the file:

- the constant's definition;
- the `pre-repair ref` line of the identity block;
- `Z-gate5`'s `base_tbl`, hashing the `§2` table at that commit;
- `Z-signed`'s `s2_base`, hashing `docs/gate-s2-evidence.md` at that commit.

There is exactly one `git archive` in the file and its argument is `"$SUBJECT_SHA"`. The
execution witness in Assignment 2 confirms this empirically: when the subject was the scratch
commit, no byte of `bb664c6`'s consumer was executed.

## The five identity facts

Printed twice per measuring run — once under `== SUBJECT IDENTITY ==` before any case, once
under `== SUMMARY ==` — as five separately labelled lines: harness sha256, repository,
requested ref, resolved subject, pre-repair ref. Confirmed present in every measuring run in
this review, including the ambiguous one (where they are the only place the substituted
subject is visible, and even there the *requested* ref and the *resolved* subject differ on
screen without any line calling that out).

---

## Case-set accounting vs `0140a4f`

The author's claim: `4e`/`4f`/`10h` each split into `-btick` + `-tilde` (+3 REQUIRED), +3
tilde mutation controls, and `P3` promoted OBSERVED → CONTROL (+1 CONTROL, −1 OBSERVED).

**Verified empirically**, by running the `0140a4f` harness and diffing the two runtime case
matrices rather than by reading the diff:

| | `0140a4f` | `f1c0fdd` | Δ |
|---|---|---|---|
| REQUIRED | 49 | 52 | +3 |
| CONTROL | 70 | 74 | +4 |
| OBSERVED | 11 | 10 | −1 |

Runtime case-id set difference — **complete, no other movement:**

```
10h        REQUIRED  ->  10h-btick      REQUIRED  +  10h-tilde      REQUIRED
10h-mut    CONTROL   ->  10h-btick-mut  CONTROL   +  10h-tilde-mut  CONTROL
4e         REQUIRED  ->  4e-btick       REQUIRED  +  4e-tilde       REQUIRED
4e-mut     CONTROL   ->  4e-btick-mut   CONTROL   +  4e-tilde-mut   CONTROL
4f         REQUIRED  ->  4f-btick       REQUIRED  +  4f-tilde       REQUIRED
4f-mut     CONTROL   ->  4f-btick-mut   CONTROL   +  4f-tilde-mut   CONTROL
P3         OBSERVED  ->  P3             CONTROL
```

That is the author's accounting exactly. Nothing was added, removed, renamed or
re-classified beyond it.

**Semantics unchanged, checked four further ways:**

1. **All 124 case ids common to both versions produce identical verdicts** at `bb664c6`. The
   only status change among common ids is `P3`, from `....` to `PASS`, which is the accounted
   promotion.
2. The reason vocabulary and success-line constants are byte-identical: `DUP_WHY`,
   `MISSING_WHY`, `AMBIG_WHY`, `UNRESOLVED_WHY`, `TS_OK`, `EC_OK`, `VH_OK`, `VP_OK_RE`,
   `CAVEAT_PHRASE`, `CAVEAT_SENTENCE`, `GATE5_PINNED`.
3. The classifier and primitive function bodies are byte-identical: `ts_class`, `vp_class`,
   `refuses`, `has`, `has_re`, `section_of`, `anchor_depth`, `norm_count`, `sec_sub`,
   `edit_at`, `edit_at_file`, `subject`. The loop drivers behind the variable-id cases
   (`for order in before after`, `for variant in suffix prefix`, the `13*` set and the `Z-*`
   consumer loop) are unchanged in both membership and order.
4. `plant_quoted_anchor` gained an optional fifth `FENCE` argument that **defaults to
   backticks**, so each `-btick` case is the old case invoked identically, with the old
   mutation control and the old assertion. The `-tilde` sibling is purely additive.
5. The `P8` exclusion — `§5.7.1` declaring its identifiers non-normative, the stated basis for
   omitting a duplicate-publication case at EC — is present and unchanged in both versions.

---

## Residuals

**R1 — Ambiguous refname fails open.** The finding above. Not reachable in the primary
repository today (zero tags). `git rev-parse --verify` does not refuse a head/tag name
collision; `--quiet` plus `2>/dev/null` destroys the warning that would have revealed it. The
same mechanism is in `a-extract-gate.sh`.

**R2 — `P3` is effectively unfalsifiable.** It compares a `git rev-parse` result against a
second run of the same command; its other two conjuncts are guaranteed by the code preceding
it. By the harness's own standard — "a REQUIRED line that cannot fail is worthless", and
every probe needs a control that must move — `P3` is a control with no falsifying input
outside a concurrent-ref-update race, and it demonstrably passes on the case it was promoted
to close.

**R3 — The missing-repository diagnostic is not sanitized.** `PREFLIGHT FAILED: the
repository path '<raw argument>' does not exist` prints `$ROOT_ARG` verbatim, with no
`sanitize_path`. A home-prefixed nonexistent path therefore prints the account name into
output that may be pasted into evidence. The adjacent "is not a git repository" diagnostic
*does* sanitize — the two are inconsistent.

**R4 — Sanitization only covers home-prefixed paths.** A repository outside the home
directory prints in full in the identity block. Correct as designed, but "sanitized form" is
a weaker guarantee than it sounds.

**R5 — Preflight failures print only `P0`, not the identity block.** A refused run reports
the harness hash but not the repository, requested ref or pre-repair reference. Defensible
(a refused run measured nothing) but it means "every run prints the five facts" is true only
of measuring runs.

**R6 — `Z-clean` is boundary-scoped and state-shaped.** It inspects five paths, not the whole
repository, and fails on pre-existing dirt rather than on dirt this run created. It does not,
on its own, establish that a run changed nothing anywhere.

**R7 — Exit status does not distinguish a substituted subject.** The ambiguous run exited `1`,
the same status as a legitimate measurement with defects observed. Consistent with the
harness's own stated position that exit status is not a discriminator, but worth stating: the
only signal was in the identity block, and only to a reader who already knew the requested ref
was ambiguous.

**R8 — `ts/node_modules` bound (confirmed, correct behaviour).** With the dependency tree
absent, the run dies at `P7` with exit 2, having emitted one control (`P3`) and no case
verdicts: `ts/node_modules is absent; the canonical generator cannot run (case 11f)`. This
is a refusal, not a silent skip, and it is right — but it bounds where the harness can be run
at all. An isolated clone must have the dependency tree staged into it before it can be
measured, which is what I did.

---

## What this review does NOT establish

- **Nothing about the consumers.** Whether the 31 failing REQUIRED cases name real defects in
  `check-type-strings.sh`, `check-eval-codes.sh`, `check-vendor-honesty.sh` or
  `test_verifier.py` was not examined. This review is about whether the instrument can
  measure, not about what it measured.
- **The sibling gate harness was not run.** `a-extract-gate.sh` was read, not exercised. The
  ambiguity finding there is by inspection of an identical code path, and should be confirmed
  by running it before being treated as measured.
- **Execution provenance was proved for one consumer, not four.** The witness rides in
  `check-eval-codes.sh`. For the other three, provenance rests on the `Z-<consumer>` controls'
  reported hashes matching hashes I computed independently from the object database — strong,
  but one inferential step weaker than the witness.
- **The scratch change is a probe, not a proposed repair.** It exists to move a verdict. Its
  correctness as a fix for the exact-membership defect was not reviewed, and it lives only in
  a throwaway clone.
- **No race conditions were probed.** `P3`'s one theoretical falsifying input — a ref updated
  between two adjacent `git rev-parse` calls — was not constructed.
- **Behaviour against a repository lacking `PRE_REPAIR_SHA` was not run.** By reading,
  `Z-gate5` and `Z-signed` would fail there and force exit 2, which is fail-closed rather than
  fail-open; that is reasoned, not measured. A shallow clone or a fresh worktree without the
  historical commit is the untested case.
- **One platform, one toolchain.** All runs used git 2.50.1, bash 3.2.57 and Python 3.9.6 on a
  single machine. `git rev-parse --verify`'s ambiguity behaviour is version-dependent in
  principle; R1 was measured on this version only.
- **Case 11f's generator was executed but not audited.** That it ran, and that its controls
  held, says nothing about whether the generator itself is correct.

---

## Recommendation (proposed, not decided)

The blocking defect is fixed and the evidence for that is strong. R1 and R2 are what stand
between this instrument and a HOLD. The narrow correction would be to resolve the subject in a
way that refuses a refname collision rather than inheriting `refs/tags/` precedence, to stop
discarding git's ambiguity warning, and to give `P3` a falsifying input that is not a second
copy of its own answer. Whether to make that correction now, defer it as a bounded latent
issue given the repository has no tags, or accept it with the false comment corrected, is
John's call, not this reviewer's.
