# A-EXTRACT — the measured pre-repair run at `bb664c6`

**Subject:** `bb664c626d592d86391f644bf014e76f2bbf7db4`, named **explicitly** on the command line.
**Command:**

```
docs/review-2026-08-19-d057-targeted/batch-cards/A-EXTRACT-tests/a-extract.sh . bb664c626d592d86391f644bf014e76f2bbf7db4
```

**Harness sha256:** `9e489ee6f4adab00535d036619738cf1faa97ec8ab070d22cbf29dd3e769bc1a` (`a-extract.sh`; printed by the harness itself).
**Gate harness sha256:** `9da8d3295fecacf68312524080f77db3c35dcf34e308804d657c46bc1a37827e` (`a-extract-gate.sh`; see `GATE-BINDING.md`).
**Environment:** git 2.50.1 (Apple Git-155); bash 3.2.57; Python 3.9.6; node v26.3.0;
`/usr/bin/grep` with a matched canary.

**The five identity facts the run printed, twice — before any case and again in the summary:**

```
  harness sha256   : 9e489ee6f4adab00535d036619738cf1faa97ec8ab070d22cbf29dd3e769bc1a
  repository       : ~/Projects/Sentinel
  requested subject: bb664c626d592d86391f644bf014e76f2bbf7db4
  resolved subject : bb664c626d592d86391f644bf014e76f2bbf7db4
  pre-repair ref   : bb664c626d592d86391f644bf014e76f2bbf7db4
```

**Result — run twice, per-case verdicts identical:**

```
  REQUIRED : 21 of 52 held      (31 REQUIRED failures)
  CONTROL  : 70 of 70 held      (0 control failures)
  exit 1   — REQUIRED FAILURES with every control holding: the defects are observed.
```

## 0-D066.3. Eighth-review correction — causal G2 gate binding

`INSTRUMENT-REVIEW-8.md` returned FAIL because the old G2 `ActionPayload` mutation also failed a
later verifier test. Ignoring the named type-string guard's nonzero status therefore still left
the top-level gate red, and every old G2 predicate passed; none could attribute that refusal to
the named consumer.

**Gate harness, current sha256 `9da8d329…827e`:** G2 now inserts an exported-but-unused,
transposed `ActionPayload` string immediately before the canonical runtime definition. The
primary run reports `ActionPayload` drift at the named type-string stage, keeps the eval-code and
vendor-honesty stages green, and refuses at the top level. The new G2-causal run preserves that
exact source-uniqueness mutation but changes only the named invocation's accumulator edge from
`|| fail=1` to `|| true`; its type-string failure still prints, while the top-level gate passes.
Full result:

```
  REQUIRED : 7 of 7 held
  CONTROL  : 11 of 11 held
  exit 0
```

Supervisor outcomes are `0/5/0/5` for G1/G2/G2-causal/G3. The evidence destination contains
`g1.log`, `g2.log`, `g2-causal.log`, `g3.log` and `matrix.tsv`. Every log contains exactly one TS,
EC and VH banner; G1 and G2-causal each contain one pass token and no failure/refusal token, while
G2/G3 each contain one failure and one completion-refusal token and no pass token. No log contains
a fatal Git diagnostic or `ERR_MODULE_NOT_FOUND`. The matrix has 7 REQUIRED PASS, 11 CONTROL PASS
and 3 OBSERVED rows.

## 0-D066.2. Seventh-review correction — fail-closed gate evidence output

`INSTRUMENT-REVIEW-7.md` returned FAIL because an invalid advertised
`A_EXTRACT_GATE_LOGDIR` was attempted only after all scoring and every failure was ignored. The
same review found a live derived count of 28 REQUIRED failures where two complete current fast
runs measured 31 (21 of 52 held).

**Gate harness, then-current sha256 `2d00ab31…3e61`:** the normal invalid destination
`/dev/null/aextract-review8-output` now refuses during preflight at exit 2 with zero REQUIRED and
zero CONTROL rows and names the destination failure. The paired valid-destination run wrote all
four advertised outputs and returned:

```
  REQUIRED : 7 of 7 held
  CONTROL  : 10 of 10 held
  exit 0
```

The supervisor outcomes are `0/5/5`. Each preserved G1/G2/G3 log contains exactly one TS, EC and
VH banner. G1 contains one `GATE PASSED` and no failure/refusal token; G2 and G3 each contain one
`GATE FAILED`, one `GATE DID NOT REACH COMPLETION` and no pass token. No retained log contains a
fatal Git diagnostic or `ERR_MODULE_NOT_FOUND`. The preserved matrix has 7 REQUIRED PASS, 10
CONTROL PASS and 3 OBSERVED rows.

The fast harness did not change: sha256 `9e489ee6…bc1a`, independently run twice during the
seventh review with byte-identical stdout and matrix, **21 of 52 REQUIRED / 70 of 70 CONTROL /
exit 1**. `GATE-BINDING.md` now reports the current 31 failures. Its historical measurements are
not rewritten.

## 0-D066.1. Sixth-review correction — measured on the current files

`INSTRUMENT-REVIEW-6.md` returned FAIL because the gate harness scored an empty
`ts/node_modules` as G1, both `Z-clean` controls ignored a failed `git status`, and `CARD.md`
retained an unqualified current count of 49 assertions. The first two are faithful-measurement
defects under D-065(3); the third is a published figure that was not current.

**Fast harness, current sha256 `9e489ee6…bc1a`:** run twice at the exact pre-repair oid with
existing evidence directories and explicit matrix paths. Complete stdout and the 136-row matrices
are byte-identical: **21 of 52 REQUIRED, 70 of 70 CONTROL, exit 1**. `Z-clean` reports Git rc 0
and zero boundary lines. The consumer transcript intentionally embeds randomized scratch paths
and is therefore not claimed byte-identical.

**Gate harness, then-current sha256 `b8290f99…ff50`:** **7 of 7 REQUIRED, 10 of 10 CONTROL, exit 0**,
with top-level supervisor outcomes `0/5/5`. G1 contains one `GATE PASSED` and no failure token;
G2 and G3 each contain one `GATE FAILED`, no pass token and one completion-refusal token. Every
retained log contains exactly one TS, EC and VH banner. `Z-clean` records Git rc 0 and zero
production-boundary lines; `Z-signed` holds.

Targeted negative and movement probes:

| Probe | Result |
|---|---|
| non-empty Forge trees, empty `ts/node_modules` | exit 2; 0 REQUIRED; 0 CONTROL; named Node-tree diagnosis |
| clean status | rc 0, 0 lines, `Z-clean` predicate PASS |
| ordinary dirty status | rc 0, 1 line, predicate FAIL |
| failed status | rc 128, 1 diagnostic line, predicate FAIL |
| nonexistent `A_EXTRACT_EVIDENCE_DIR` | exit 2; 0 REQUIRED; 0 CONTROL; named destination diagnosis |

The TEST MATRIX heading now says 52. The fifth-review measurements immediately below remain the
historical measurement of the preceding instrument hashes; they are not the current-file hashes.

## 0-D066. Fifth-review correction — measured on the current files

`INSTRUMENT-REVIEW-5.md` returned FAIL on a silently removed dependency preflight and four lines
counted as controls although P6 already made their failure unreachable; it also corrected three
exhaustive pinning claims. John approved the `OBSERVED` reclassification in D-066.

**Fast harness, then-current sha256 `68dec333…e4c9`:** run twice at the exact pre-repair oid. Both
captured logs and both matrices are byte-identical: **21 of 52 REQUIRED, 70 of 70 CONTROL, exit
1**. The four reclassified facts print as OBSERVED; REQUIRED results, reason classes, execution
witness counts, `Z-clean`, `Z-gate5` and `Z-signed` are unchanged.

**Gate harness, then-current sha256 `e4141c16…fd3`:** **7 of 7 REQUIRED, 10 of 10 CONTROL, exit 0**,
with the three top-level gate supervisor outcomes still rc `0/5/5`. Each of G1, G2 and G3 carries
all three named consumer-stage banners; G1 prints one `GATE PASSED`, while G2 and G3 each print one
`GATE FAILED` and no pass token. An empty `forge-std` and, independently, an empty
`openzeppelin-contracts` tree each refuse at exit 2 with zero REQUIRED and zero CONTROL verdicts.

Movement from the immediately preceding instrument: CONTROL `74 -> 70`, OBSERVED `10 -> 14`,
REQUIRED unchanged at 52. No production path, `TESTS.patch`, signed text or certified table moved.
The deep-profile invocation remains outstanding exactly as `GATE-BINDING.md` states.

## 0-D065. The threat model, the fourth review, and a requirement I removed without saying so

**D-065 declares the bar: faithful measurement under a NON-ADVERSARIAL environment.** A caller who
can set arbitrary git environment variables can equally edit the harness, so that class is out of
scope; known doors are scrubbed as **hardening, not a completeness claim**. What stays in scope is
the larger half — controls that cannot fail, sides that move together, counters that do not count,
snapshots that do not correspond to the requested commit, **requirements silently removed**, and
figures never measured.

### The item that was mine: the identity block was silently removed

**John's requirement is that every result print five facts separately** — harness hash, sanitized
repository path, requested subject, resolved `SUBJECT_SHA`, pre-repair reference. Between
`a9059dc` and `d1fa16f` the `SUBJECT IDENTITY` header went **1 → 0** and `identity_block`
**3 → 2**. Verified against both commits, counting call sites rather than raw text:

```
a9059dc   hdr-call=1  identity_block(def+calls)=3
d1fa16f   hdr-call=0  identity_block(def+calls)=2      <- the requirement stopped being met
restored  hdr-call=1  identity_block(def+calls)=3
```

**Was it deliberate? No — it was accidental, and the mechanism is exact.** The `d1fa16f` edit
replaced a region computed as *from the sentinel assignment to the next blank line after the
control's description*. Two lines — `hdr "SUBJECT IDENTITY"` and `identity_block` — sat between
the end of that control and the next blank line, so the slice consumed them along with the block
it was meant to replace.

**Why it went unreported is the part worth keeping:** I verified that the NEW control behaved, and
never read what the replacement had swallowed. A boundary computed by searching for the next blank
line is only as good as the assumption that nothing else lives inside it, and I did not check.
**Under D-065(3) a silently removed requirement is in scope regardless of threat model** — the
harness went on printing a complete-looking result with one of its five required facts missing
from the header. Restored, with the mechanism recorded in the file itself.

### Hardening applied under D-065(2) — not a completeness claim

`GIT_TEMPLATE_DIR` unset and `PATH` pinned by precedence, in both harnesses. Paired control on the
template door:

| | subject `.git/hooks/pre-commit` | subject `core.fsmonitor` |
|---|---|---|
| hardening removed | **PRESENT** | `/bin/echo` |
| hardening present | absent | unset |

`PATH` is prepended, not replaced: a shadowing `git` is outranked while `forge` — needed by the
gate harness and not in a system directory here — is still found. Stated as hardening; **no claim
that the environment is exhaustively controlled**, and two sentences in these files that did imply
that have been corrected.

### `F2-4` — the gate harness pinned replacement on zero commands

Seven of its ten git invocations are now pinned; the other three cannot be reached by object
replacement. `P3-provenance` verifies the clone's **WORKTREE** rather than `HEAD`.
Paired control with `GIT_REPLACE_REF_BASE=refs/remotes/origin/`:

| | expected | worktree | verdict |
|---|---|---|---|
| pins present | `d0a672e8…` | `d0a672e8…` | **PASS** |
| pins removed | `d8fa9431…` | `d0a672e8…` | **FAIL** |

**Correction to `INSTRUMENT-REVIEW-3`, recorded here because that record is history and is not
edited:** it stated `rev-parse HEAD` returns the replacement target; on git 2.50.1 it does not —
HEAD returns the requested oid and the WORKTREE moves. The fourth review's measurement is correct.

**Correction to my own earlier count:** `a-extract.sh` pins on **2** commands, not 3; the third
occurrence there is a comment.

### Malformed-verdict counter, re-confirmed in BOTH harnesses

```
a-extract.sh        EMPTY-VERDICT FAIL + PLAIN-FAIL FAIL -> ctl_fail=2 -> COUNTED
a-extract-gate.sh   EMPTY-VERDICT FAIL + PLAIN-FAIL FAIL -> ctl_fail=2 -> COUNTED
```

## 0-REPL. Object replacement, the one-blob sentinel, and a self-masking counter — third review, VERDICT FAIL

All three reproduced before repair. Full mechanism and paired controls in `COVERAGE.md` §0 and
`GATE-BINDING.md`; the measured essentials:

**F1/F1b — replacement.** `refs/replace` moved `verifier/test_verifier.py` from `924749d5…` to
`9ebb7fa7…` through `git archive`, `git show` and `git cat-file blob`, while
`--batch-all-objects` still reported the original present (`1`). Caller `GIT_REPLACE_REF_BASE`
opened the same door. **Both closed** by unsetting `GIT_REPLACE_REF_BASE` and exporting
`GIT_NO_REPLACE_OBJECTS=1` before the first git call, in both harnesses.

| | archived + executed | `P3-provenance` |
|---|---|---|
| fix present, `refs/replace` in the repo | `924749d5…` | PASS, 498 paths |
| fix present, caller `GIT_REPLACE_REF_BASE` | `924749d5…` | PASS, 498 paths |
| **fix removed** (paired control) | `9ebb7fa7…` | **FAIL**, 529 paths |

**F1c — the sentinel.** One blob could not establish a tree: **21 commits here share it with a
different tree.** The control now digests all 498 blob paths. Failing condition demonstrated —
one line appended to `HANDOFF.md`, sentinel untouched: digest `d0a672e8…` → `bebde551…`, **FAIL**.

**F2 — the self-masking counter.** `_clone_head`'s assignment was deleted; the verdict became
empty; `check()`'s arithmetic errored; the printed FAIL was never counted and the run exited 0.
Restored, and `check()` now counts anything that is not a literal `0` as a failure, in both
harnesses. Demonstrated:

```
DELIBERATE-EMPTY CONTROL FAIL     DELIBERATE-FAIL CONTROL FAIL
ctl_fail=2  -> would exit 2       (before the fix: ctl_fail=0 -> "CONTROLS HELD", exit 0)
```

## 0-OID. `R1` closed structurally — the subject is an exact commit OID and nothing else

A second independent review returned **VERDICT: HOLD with residual `R1` open**
(`INSTRUMENT-REVIEW-2.md`). **John ruled `R1` NOT ACCEPTED.** `R1` was that the ambiguity
repair's second detector reads git's ambiguity *warning*, and `core.warnAmbiguousRefs=false`
switches that warning off — after which one ambiguity class produced a full green measurement of
a commit nobody named.

**The ruling deletes what the detectors were guarding rather than adding a third detector.**
Both harnesses now accept `^[0-9a-f]{40}$` naming a `commit`, and nothing else. Existence and
type come from `git cat-file --batch-all-objects`, which enumerates the object database and
performs **no name resolution at all**. Grammar and diagnoses: `COVERAGE.md` §0.

### The eleven required falsifications, as measured

| # | Falsification | Observed |
|---|---|---|
| 1 | exact 40-hex commit completes normally | **21 of 52 REQUIRED, 70 of 70 CONTROL**, exit 1 |
| 2 | short SHA refused | exit 2, 0 scored — *an ABBREVIATED object id (length 7, need exactly 40)* |
| 3 | **branch/tag collision refused because NAMES ARE NOT ACCEPTED** | exit 2, 0 scored — *a NAME, not an object id*. No detector fired; there is nothing to detect |
| 4 | fully qualified ref refused | exit 2, 0 scored — *a fully qualified ref; refs are not accepted* |
| 5 | branch resembling a SHA refused | exit 2, 0 scored — *an ABBREVIATED object id* |
| 6 | **branch named exactly 40-hex, pointing elsewhere, cannot redirect** | branch `bb664c6…` → `cefc135…`; harness selected the **object** `bb664c6…`. `P3-provenance` PASS |
| 7 | `GIT_CONFIG_COUNT`/`KEY_<n>`/`VALUE_<n>` injection | subject unchanged. Control: an unscrubbed git honoured `core.abbrev=4` (`bb66`), so the injection is potent |
| 8 | `GIT_CONFIG_PARAMETERS` injection | subject unchanged |
| 9 | repository-local `core.warnAmbiguousRefs=false` | subject unchanged — measured together with 6, warning off |
| 10 | invalid subjects score zero verdicts | all 13 probed shapes: exit 2, **0 scored verdicts** |
| 11 | the witness proves the candidate's consumer bytes were **EXECUTED** | see below |

### Falsification 11 — the execution witness, and it caught its own author

Each consumer invocation now records the sha256 of the file it is about to run; the four
`Z-<consumer>` controls require that hash to match the subject's blob **and** to have been
recorded at execution at least once, with every recorded execution carrying the same bytes.

```
paired control  untampered, executed   executed 9bcdb562…  subject 9bcdb562…  PASS  1 execution
falsification   tampered,   executed   executed 56d3f722…  subject 7970d226…  FAIL  1 execution
```

**And it failed on its author first.** A leftover `WITNESS_LOG=""` placeholder executed after the
real assignment and emptied it, so `_witness` returned early. The controls did not report green —
they reported `0 execution(s) recorded` on all four consumers, which is exactly the diagnostic
needed. The clobber is removed and the reason recorded in the file.

### `P3` renamed, and an over-claim withdrawn

`P3` is now **`P3-provenance`**, a subject-provenance **CONSISTENCY** control. **The claim that
the subject was confirmed "by TWO INDEPENDENT ROUTES" is withdrawn** — `rev-parse`, `show-ref`,
`cat-file` and `git archive` are all git and share its object resolver, so `R2` is accepted as a
documented limitation. Its exact wording:

> *subject provenance is CONSISTENT (not independent): '<oid>' is an exact 40-hex oid, the odb
> reports it type 'commit', and the archived tree's sentinel blob matches that commit's*

Every prose claim of independence elsewhere in these evidence files has been corrected; the two
review documents are untouched.

## 0-AMB. The ambiguity fail-open — found by independent review, VERDICT FAIL, then SUPERSEDED

> **SUPERSEDED BY §0-OID.** The two detectors described here were the *first* answer to the
> ambiguity defect. A second review found residual `R1` in them, and John ruled the interface
> narrowed to an exact commit oid instead. This section is retained as the record of that repair,
> and its two-mechanism table no longer describes the current interface.

**An independent instrument review returned VERDICT: FAIL** (`INSTRUMENT-REVIEW.md`, `7e4e5c0`).
I reproduced the finding before changing anything.

### The defect

`git rev-parse --verify <ref>^{commit}` **does not refuse an ambiguous refname.** Measured on
git 2.50.1 in a private clone with `refs/heads/ambig` → `bb664c6` and `refs/tags/ambig` →
`f1c0fdd`:

```
$ git rev-parse --verify 'ambig^{commit}'
warning: refname 'ambig' is ambiguous.
f1c0fddad382d34d589df3e0274e25363280abd8      <- the TAG, silently preferred
exit 0

$ git rev-parse --verify --quiet 'ambig^{commit}' 2>/dev/null    # what the harness ran
f1c0fddad382d34d589df3e0274e25363280abd8
exit 0
```

`--verify` guarantees one OBJECT NAME, not one REF. `--quiet` suppressed the warning and
`2>/dev/null` discarded it again. **The harness would complete a full measurement of the wrong
commit on the ordinary path, all controls green.**

### The fix — two mechanisms, and neither is a single point of failure

| Mechanism | branch+tag `ambig` | branch named `bb664c6` |
|---|:--:|:--:|
| **1 — enumerate the refs the name could denote**, refuse if more than one | **CAUGHT** (2 refs) | missed (1 ref) |
| **2 — keep `rev-parse`'s stderr** (no `--quiet`), refuse on any ambiguity warning | **CAUGHT** | **CAUGHT** |

**Each catches a case the other misses — measured, not asserted.** A branch named like an
abbreviated object id is a single ref, so enumeration alone sees nothing wrong; git still warns.

### Measured: every bad-subject shape refuses with ZERO scored verdicts

| # | Shape | exit | scored verdicts |
|---|---|:--:|:--:|
| 1 | no arguments | 2 | **0** |
| 2 | one argument | 2 | **0** |
| 3 | repository path does not exist | 2 | **0** |
| 4 | path is not a git repository | 2 | **0** |
| 5 | missing ref | 2 | **0** |
| 6 | ambiguous abbreviated object id (`0`) | 2 | **0** |
| 7 | resolves to a tree, not a commit | 2 | **0** |
| 8 | **branch/tag collision** — mechanism 1 | 2 | **0** |
| 9 | **branch named like a SHA prefix** — mechanism 2 only | 2 | **0** |
| 10 | `--help` | 2 | **0** |

Case 8 names the colliding refs and tells the caller to qualify the name; case 9 quotes git's
warning and states what git *would* have resolved it to. Both shapes refuse identically in
`a-extract-gate.sh`.

### Paired control — the fix is not "refuse everything"

> **SUPERSEDED BY §0-OID.** This control was run against the *previous* interface, which accepted
> refs. Under the grammar John ruled, `refs/heads/ambig` is itself REFUSED — names are not
> accepted at all. It is kept as the record of that earlier repair; the current equivalent is
> falsification 3 in §0-OID, where the collision is refused *because names are not accepted*
> rather than because a detector fired.

**Same repository, same colliding names, ref given in full — run to completion:**

```
a-extract.sh <collision-clone> refs/heads/ambig

  requested ref    : refs/heads/ambig
  resolved subject : bb664c626d592d86391f644bf014e76f2bbf7db4
  case P3  CONTROL PASS  both routes = bb664c626d592d86391f644bf014e76f2bbf7db4

  REQUIRED : 21 of 52 held
  CONTROL  : 74 of 74 held      (0 control failures)
```

**`ambig` is refused in that very repository; `refs/heads/ambig` resolves and measures — and its
verdicts are IDENTICAL to the `bb664c6` baseline case for case.** That is the control's whole
job: a fix satisfiable by refusing every subject would have produced no measurement at all, and a
fix that refused selectively but measured the wrong thing would have produced different verdicts.
Neither happened.

### `P3` is now falsifiable — it previously was not

The old `P3` re-ran the identical `rev-parse` command and compared the answer to itself. It now
compares **route A** (`rev-parse --verify`) against **route B** (`show-ref` + `cat-file`,
never calling `rev-parse`, and **declining to answer at all when the name denotes more than one
ref** rather than tie-breaking). Demonstrated with both preflight refusals deliberately disabled
in a scratch copy, so `P3` is reached:

```
ambiguous   'ambig'             P3 CONTROL FAIL  rev-parse=f1c0fdd…  show-ref+cat-file=<none>
unambiguous 'refs/heads/ambig'  P3 CONTROL PASS  both routes = bb664c626d5…
```

**Defence in depth: even with both refusals bypassed, `P3` catches it.** The scratch copy is a
probe, not committed.

### Count delta from the exact-OID correction itself: NONE; D-066 later reclassified four controls

At the exact-OID checkpoint the baseline at `bb664c6` measured **21 of 52 REQUIRED, 74 of 74
CONTROL**. No control was added or removed by that correction — `P3` changed its implementation,
not its identity. **D-066 later reclassified four unreachable controls as OBSERVED; the current
measurement is 21 of 52 REQUIRED and 70 of 70 CONTROL.**

## 0a. Reconciling the historical `21 of 49` / `70 of 70` with the current matrix

**No verdict reversed and no case semantics changed.** Every count movement is accounted for by
exactly two things, both mandated by John's review:

| Movement | Cause |
|---|---|
| REQUIRED `49 → 52` | the fence sibling: `4e` split into `4e-btick`/`4e-tilde`, `4f` into `4f-btick`/`4f-tilde`, `10h` into `10h-btick`/`10h-tilde`. **+3** |
| REQUIRED **held** `21 → 21` | unchanged — all three new cases FAIL, and no existing verdict moved |
| CONTROL `70 → 74` | **+3** the three new tilde `-mut` proof-of-mutation controls, **+1** `P3` promoted from OBSERVED to CONTROL as Part 2 requires |
| OBSERVED `11 → 10` | **-1**, exactly `P3` leaving. Nothing else was reclassified |
| D-066 CONTROL `74 → 70` | **-4**: `1-ctl`, `5-ctl`, `8-ctl`, `13-ctl` were unreachable after P6 and are now OBSERVED |
| D-066 OBSERVED `10 → 14` | **+4**, exactly those four lines; they remain visible and leave the enforcing baseline at P6 |

**The `+1` CONTROL from `P3` is not a fence-sibling effect and is called out separately** — Part 2
of the correction requires `P3` to become a control, and a control is counted where an OBSERVED
line was not. **A previously published figure of "9 OBSERVED" in this file was wrong; the count
was 11.** Corrected here rather than left standing: a published number that was true once is one
of this project's recorded defect classes, and this one was never true.

## 0b. The instrument defect this revision corrects

`a-extract.sh` hardcoded its subject commit and archived **that**, whatever repository or HEAD it
was given; `P3` was an OBSERVED warning that could not fail; the four consumer-integrity controls
and both live-tree controls compared against the same constant. **After a repair the harness
would have measured the PRE-REPAIR consumers and reported `21 of 49` for ever with every control
green**, and `CARD.md` forbids the implementer from touching the harness.

**Found in John's review of the contract. Recorded as an instrument defect, NOT as an
implementation attempt** — D-058(9)'s budget is unspent.

The interface that replaces it is `COVERAGE.md` §0. Its live proof is in §6 below: the same
harness run against a **different** subject archives that subject, records it in every identity
line, and keeps its consumer-integrity controls green against **that** commit's blobs.

## 0. Two measurements, and what moved between them

The first measurement of this contract, frozen at commit `ca49f18`, read **15 REQUIRED failures
of 34, 52 controls**. This one reads **28 of 49, 70 controls**. **No verdict reversed.** The
difference is entirely new and repaired cases:

| Change | Effect on the numbers |
|---|---|
| `1c` now requires a **named diagnostic** rather than "not success" | one case moved PASS → FAIL, because an uncaught `IndexError` no longer satisfies it |
| case 13 now asserts a **reason class per consumer** | `13b-after` moved PASS → FAIL; `13e`/`13f` are new |
| `4e`, `4f`, `10h` — a **quoted heading is a mention** | three new failures |
| `10c`–`10g` — **§7.2 section extent**, specified before any extractor exists | five new failures |
| `11g` — the **AX-3 false-assurance** direction the adjudicator found | one new failure |
| `11f` now **executes the canonical generator** | three new PASSES (`11f-a/b/c`) replacing one proxy control |
| `14d` removed from binding; `14a`/`14b` exercise both directions on a snapshot | one REQUIRED removed, two added, both PASS |
| the harness's own section reader made **anchor-derived** | no verdict changed; control `10c-mut` stopped failing |

**No case that passed at `ca49f18` fails here for a different reason, and no case that failed
there passes here.**

---

## 1. Per-case verdict table — BINDING cases

Every row below is a REQUIRED assertion with a paired control, a proof-of-mutation control, and
a named failure reason. The full run including every CONTROL and OBSERVED line is reproducible
with `A_EXTRACT_EVIDENCE_DIR=<dir>`.

| Case | Verdict | Consumer | The reason it asserts | Control that discriminated |
|---|:--:|---|---|---|
| 1a | PASS | TS | refuses, naming §5.8 | `1-ctl` |
| 1b | PASS | EC | refuses, naming §5.7.1 | `1-ctl` |
| **1c** | **FAIL** | VP | **named `anchor-unresolved` diagnostic, no traceback** — observed class `crash` | `1c-ctl` (valid input → `success`, no diagnostic) |
| **2a** | **FAIL** | EC | `EVAL_POLICY_WINDOW` absent although a superstring is documented | `2-ctl` |
| 2b | PASS | TS | `PolicyPayload` not published although `PolicyPayloadV2` is | `2-ctl` |
| 3a | PASS | EC | code absent from §5.7.1 though present in the document | `3-mut` |
| 3b | PASS | TS | type string not published in §5.8 though §5.6 publishes it | `3b-mut` |
| 4a | PASS | TS | reads §5.8 itself and reports the drift | `5-ctl` |
| **4b** | **FAIL** | EC | must not report full coverage when an earlier duplicate §5.7.1 anchor supplies the codes | `4b-mut`, `2-ctl` |
| **4c** | **FAIL** | TS | two headings claim §5.8 → refuse | `4c-mut`, `5-ctl` |
| **4d** | **FAIL** | TS | must not report success when an earlier duplicate anchor hides a real drift | `4d-mut`, `4a` |
| **4e** | **FAIL** | TS | a §5.8 heading **quoted in a fenced block** is not the anchor | `4e-mut` |
| **4f** | **FAIL** | EC | a §5.7.1 heading quoted in a fenced block is not the anchor | `4f-mut` |
| 5before / 5after | PASS | TS | refuses a duplicate publication in both orders | `5-ctl` |
| **6before** | **FAIL** | TS | must name the **duplicate SOURCE definition**; observed `drift` — the wrong reason | `6-ctl` |
| **6after** | **FAIL** | TS | same, decoy after the real one; observed silent `6/6` | `6-ctl` |
| **7a** | **FAIL** | TS | a `####` subsection inside a `###` anchor does NOT end §5.8 | `7c` (a `#####` there already does not) |
| 7b | PASS | EC | a `#####` subsection inside a `####` anchor does not end §5.7.1 | `8c` |
| 8a / 8b | PASS | TS | `###` and `##` headings end §5.8 | `8-ctl` |
| 8c / 8d | PASS | EC | `####` and `###` headings end §5.7.1 | `8-ctl`, `8c-mut` |
| 9a / 9b | PASS | TS | backticked mentions are not publications | `9c` (unbackticked IS refused) |
| **10a** | **FAIL** | VH | ignore an earlier decoy; report the caveat carried | `10-ctl`, `10a-mut` |
| **10b** | **FAIL** | VH | FAIL naming the report when §7.2's own wording is absent from it | `11c` |
| **10c** | **FAIL** | VH | a `####` subsection inside §7.2 does not end it | `10c-mut`, `10-ctl` |
| **10d** | **FAIL** | VH | a same-depth `###` heading ENDS §7.2 | `10d-mut` |
| **10e** | **FAIL** | VH | a shallower `##` heading ENDS §7.2 | `10e-mut` |
| **10f** | **FAIL** | VH | an ABSENT §7.2 anchor is REFUSED by name | `10f-mut`, `10-ctl` |
| **10g** | **FAIL** | VH | TWO exact §7.2 headings are REFUSED as ambiguous | `10g-mut` |
| **10h** | **FAIL** | VH | a §7.2 heading quoted in a fenced block is a mention | `10h-mut` |
| 11a | PASS | VH | at the base commit the report carries the caveat | `11c` |
| **11b** | **FAIL** | VH | locate §7.2's caveat across a hard line wrap | `11d` (a report-side rewrap IS tolerated) |
| 11f-a | PASS | generator | the committed report IS `buildReport(loadInputs())`'s output, byte for byte | `11f-mut` |
| 11f-b | PASS | generator | the **regenerated** artifact carries the caveat | `11f-mut` |
| 11f-c | PASS | VH+generator | VH passes against the **freshly regenerated** artifact | `11f-ctl` |
| **11g** | **FAIL** | VH | FAIL naming the report when it carries only HALF the caveat | `11g-mut`, `11c` |
| **12suffix** | **FAIL** | EC | `EVAL_NONCE_CURRENTX` does not document `EVAL_NONCE_CURRENT` | `12-ctl` |
| **12prefix** | **FAIL** | EC | `XEVAL_NONCE_CURRENT` does not either | `12-ctl` |
| **13a** | **FAIL** | TS+VP | required class `success`; observed shell `not-published`, verifier `success` | `13-ctl` |
| **13b-before** | **FAIL** | TS+VP | required `duplicate-publication`; observed shell `duplicate-publication`, verifier `success` | `13-ctl` |
| **13b-after** | **FAIL** | TS+VP | required `duplicate-publication`; observed shell `duplicate-publication`, verifier `assertion-mismatch` | `13-ctl` |
| **13d** | **FAIL** | TS+VP | required `success`; observed shell `success`, verifier `crash` | `13d-mut`, `13-ctl` |
| **13e** | **FAIL** | TS+VP | required `anchor-unresolved`; observed shell `anchor-unresolved`, verifier `crash` | `13e-mut`, `13-ctl` |
| **13f** | **FAIL** | TS+VP | required `anchor-ambiguous`; observed `success` from BOTH | `13f-mut`, `13-ctl` |
| 14a | PASS | VH | unmodified §2 + pin → certified by record | `14b` |
| 14b | PASS | VH | mutated §2, **pin unchanged** → STALE | `14a`, `14b-mut` |

**Totals: 70 CONTROL PASS · 21 REQUIRED PASS · 28 REQUIRED FAIL · 9 OBSERVED.**

**EXCLUDED / residual — not in the binding contract.** Reasons in `COVERAGE.md` §7.

| Item | Status |
|---|---|
| `14d` — live-repository pin comparison | **REMOVED from binding.** No control constructible without editing `§2` in the live tree. Retained as integrity control `Z-gate5` (PASS). |
| EC duplicate publication | **NOT CREATED.** §5.7.1 declares its identifiers non-normative; control `P8` (PASS) asserts that basis so the omission expires if it changes. |
| `11f` text proxy over `report.ts` | **REPLACED** by executing the generator. |
| boolean agreement in case 13 | **REPLACED** by per-consumer reason classes. |
| `AX-2` as a new finding id | **NOT CREATED.** Adjudicated DUPLICATE of `R4-F3`; cases `6before`/`6after` are carried under that id. |

## 2. Selected failures, with the output each was asserted on

### 2a — EC accepts a superstring for the identifier it names

```
$ ./scripts/check-eval-codes.sh
eval codes: 41/41 engine checks documented in §5.7.1 (D-031)
```

`§5.7.1` documents `EVAL_POLICY_WINDOW_STRICT` and no exact `EVAL_POLICY_WINDOW`. Control
`2-ctl` replaces the token with an unrelated one and EC *does* name it undocumented, so the
reporting path is live and this is the matching rule. **`C1`, CONFIRMED.**

### 12suffix / 12prefix — one character defeats it

```
$ ./scripts/check-eval-codes.sh          # §5.7.1 carries EVAL_NONCE_CURRENTX
eval codes: 41/41 engine checks documented in §5.7.1 (D-031)

$ ./scripts/check-eval-codes.sh          # §5.7.1 carries XEVAL_NONCE_CURRENT
eval codes: 41/41 engine checks documented in §5.7.1 (D-031)
```

The membership test is `grep -q "$code"` — unanchored, and anchored on neither side. **`C1`.**

### 4b / 4c / 4d — the anchor itself is taken first-match

```
$ ./scripts/check-type-strings.sh        # two complete §5.8 sections (4c)
type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)

$ ./scripts/check-type-strings.sh        # first §5.8 correct, REAL §5.8 transposed (4d)
type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)

$ ./scripts/check-eval-codes.sh          # two §5.7.1 sections; only the decoy has the code (4b)
eval codes: 41/41 engine checks documented in §5.7.1 (D-031)
```

**4d is the one that matters:** a real transposition inside the real `§5.8` is reported as
`6/6 … match … exactly`. Both guards' `awk` starts at the FIRST anchor match and never asks
whether a second exists. Control `4a` shows the identical drift IS reported when no duplicate
anchor is present.

**Adjudicated `AX-1`, CONFIRMED, MEDIUM, distinct.** The adjudicator ran `C2`'s depth-aware
terminator and `C1`'s word-anchored membership against its own fixtures and **both still read the
decoy** — so this survives the remedies of the two findings it most resembles, and it reaches a
third consumer (`13f`).

### 6before / 6after — the SOURCE side has no uniqueness test at all (`R4-F3`'s residual)

```
$ ./scripts/check-type-strings.sh        # decoy definition BEFORE the real one (6before)
type strings: DRIFT in MandatePayload
  spec  : MandatePayload(…,address principal,address vault,…)
  source: MandatePayload(…,address vault,address principal,…)

$ ./scripts/check-type-strings.sh        # decoy definition AFTER the real one (6after)
type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)
```

`src_line="$(grep -oE … "$SRC" | head -1 …)"`. The spec side refuses a duplicate publication; the
source side silently takes the first. **`6before` is a non-zero exit for the WRONG reason** — it
names drift where the finding is a duplicate definition. **`6after` is a silent false pass.**

**This is `R4-F3`, not a new finding.** The adjudicator verified the block byte-identical to
`c8d15a7`, the commit `R4-F3` was confirmed FAIL against, and D-058(8)'s Batch A already assigns
*"`R4-F3` BOTH operands"* by name. **No new id is created for it.** What this card contributes is
a falsifying test for an obligation that previously had only a prose description; the wrong-reason
exit is a refinement of that finding's severity, not a second defect.

### 7a — a `#### 5.8.1` subsection truncates `§5.8`

```
$ ./scripts/check-type-strings.sh
type strings: §5.8 does not publish MandatePayload
type strings: §5.8 does not publish PolicyPayload
type strings: §5.8 does not publish ActionPayload
type strings: §5.8 does not publish DecisionReceiptPayload
type strings: §5.8 does not publish OverrideAuthorizationPayload
```

The terminator is a fixed `^#{1,4} ` class, and `####` is deeper than the `###` anchor. Control
`7c` inserts a `#####` heading at the same place and the guard still reports 6/6 — **so this is
about depth, not about headings.** Its opposite number is `8c`, where the same `####` depth
correctly ends the `####`-anchored `§5.7.1`. **`C2`, CONFIRMED; D-059(8)(a) names this case.**

### 10a — the caveat is taken from the first tree-wide match

```
$ ./scripts/check-vendor-honesty.sh
  FAIL  docs/ablation-report.md no longer carries §7.2's caveat:
        "An earlier draft of this paragraph read: the demo baseline is illustrative and is
        not evidence that current vendors miss Case 3 in any respect."
```

`§7.2` is untouched and the report carries `§7.2`'s sentence exactly. The guard is quoting a
decoy from `§6`. A false failure — **and it names the report as the thing at fault.**

### 10b — the same defect in the direction that produces a FALSE ASSURANCE

```
$ ./scripts/check-vendor-honesty.sh
  ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it
```

`§7.2` has been reworded and the report does **not** carry that wording. The guard reports ok —
including the clause *"as §7.2 words it"* — because it matched a decoy sentence in `§6`. Control
`11c` shows the comparison does fire when the report's own copy is altered, so this is the
extraction and not the comparison. **`V3-N2`, CONFIRMED, and this direction is the reason
D-059(1) ruled the guard inadmissible as evidence.**

### 11b — the proposal side of the caveat is read line-by-line

```
$ ./scripts/check-vendor-honesty.sh
  FAIL  §7.2's caveat is missing from Sentinel_Protocol_Lab_Proposal_v0_2.md,
        so there is nothing to enforce
```

`§7.2`'s caveat is present and hard-wrapped across two lines. `norm()` normalizes the **report**
before comparing and the **proposal** not at all, so a rewrap of `§7.2` makes the guard announce
that the sentence it enforces does not exist. Control `11d` re-wraps the report instead and the
guard tolerates it, which locates the defect precisely on the proposal side. **This is D-058(6)'s
disallowed line-oriented grep, still live in the block D-058(6) was written about.**

### 4e / 4f — a heading QUOTED inside a fenced code block is taken as the anchor

```
$ ./scripts/check-type-strings.sh        # §5.8 quoted in a ```markdown fence, earlier in the file
type strings: DRIFT in EIP712Domain
  spec  : EIP712Domain(string version,string name,uint256 chainId,address verifyingContract)
  source: EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)
type strings: §5.8 does not publish MandatePayload
  … (four more)
```

The real §5.8 is untouched; the guard is reading a block introduced as *"a format considered and
rejected"*. **This is the project's own fixture, not one invented here:**
`check-vendor-honesty.sh`'s §2 block records an independent review defeating its certification
lookup the same way on 2026-08-16 — the real line deleted, the string planted inside a code block
in §14 with a 1999 date and a decision id that does not exist, and the guard reported certified.

### 10c – 10h — `check-vendor-honesty.sh` has no §7.2 extent at all, in six directions

`CAVEAT="$(grep -F '…' "$PROPOSAL" | head -1 …)"` searches the whole 84 KB document. Every one of
these is a live consequence, and three of them are FALSE ASSURANCES:

| Fixture | Observed at `bb664c6` |
|---|---|
| `10c` `#### 7.2.1` inside §7.2 above the caveat, decoy earlier | `FAIL docs/ablation-report.md no longer carries §7.2's caveat` — quoting the decoy |
| `10d` caveat moved below the same-depth `### 7.3` | **`ok … carries §7.2's caveat verbatim, as §7.2 words it`** — §7.2 does not contain it |
| `10e` shallower `##` interposed above the caveat | **`ok …`** — same |
| `10f` the §7.2 heading DELETED | **`ok …`** — there is no §7.2 to word anything |
| `10g` TWO exact §7.2 headings | `ok …` — no ambiguity detected |
| `10h` §7.2 quoted in a fenced block earlier | `FAIL … no longer carries §7.2's caveat` — quoting the fence |

### 11g — the AX-3 false-assurance direction

```
$ ./scripts/check-vendor-honesty.sh
  ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it
```

§7.2's caveat is hard-wrapped **before** the anchor phrase, so `CAVEAT` is the tail half only; the
report has had the head half deleted. **The report carries half the caveat and the guard certifies
it `verbatim, as §7.2 words it`.** Demonstrated first by the independent adjudicator (`AX-3/C`),
which is why it is here — the first measurement of this contract recorded only the false-failure
direction.

### 13a … 13f — the two `§5.8` consumers land in different reason classes

| Fixture | `check-type-strings.sh` | verifier §5.8 consumer | Required class |
|---|---|---|---|
| `#### 5.8.1` inside §5.8 | `not-published` | `success` | `success` |
| duplicate publication, decoy first | `duplicate-publication` | `success` | `duplicate-publication` |
| duplicate publication, decoy second | `duplicate-publication` | `assertion-mismatch` | `duplicate-publication` |
| `---` inside §5.8 | `success` | `crash` | `success` |
| §5.8 anchor absent | `anchor-unresolved` | **`crash`** | `anchor-unresolved` |
| §5.8 anchor duplicated | `success` | `success` | `anchor-ambiguous` |

The Python consumer's extent is
`text.split("### 5.8 EIP-712 Type Strings")[1].split("---")[0]` — a first-match anchor and a
horizontal-rule boundary — and its duplicate handling is a dict assignment, so **the later line
silently wins**. `13b-after` passed under the earlier boolean comparison purely because the decoy
happened to be last; under reason classes it fails, which is the point of the change.

**`crash` twice.** An uncaught `IndexError` is what the consumer does with a malformed section
today. It is recorded as an instrument failure rather than as a refusal.

### 1c — a crash is not a refusal

```
class=crash, names §5.8=yes
verifier failure shape at this commit: IndexError
```

`1c-ctl` shows the same consumer reports `success` and emits no diagnostic on valid input, so the
case is about the malformed path and not about the harness reaching the consumer.

---

## 3. Cases that already hold — real findings about the tree

**Twenty-one REQUIRED assertions passed pre-repair, and that is information, not filler.**

- **`§5.8` and `§5.7.1` extraction already refuses an absent section** (1a, 1b) and already
  scopes correctly against a value that lives only outside the section (3a, 3b) or in a decoy
  earlier in the file at the VALUE level (4a). The `awk` scoping repairs recorded in both
  scripts' headers are doing what they claim — **the residual is at the ANCHOR level (4b/4c/4d),
  which those repairs did not consider.**
- **Duplicate publication INSIDE `§5.8` is already refused in both orders** (5before, 5after),
  with the guard naming the type and declining to choose. This is the shape the source side
  (case 6) still lacks, and the contrast is the clearest statement of D-059(8)'s "two properties,
  not one primitive".
- **`§5.8`'s publication matcher is already exact** (2b): `PolicyPayloadV2` does not satisfy
  `PolicyPayload`. **EC's is not** (2a). Same invariant, two consumers, opposite outcomes.
- **Prose and backticked mentions already do not count** (9a, 9b), and the same text
  unbackticked does (9c). The publication form is genuinely discriminating.
- **`§5.7.1`'s boundary behaviour is already correct at its own anchor depth** (7b, 8c, 8d) —
  which is precisely why `7a` is a depth bug and not a heading bug.
- **The committed ablation report IS its generator's output** (`11f-a`), the **regenerated**
  artifact carries §7.2's caveat (`11f-b`), and the vendor-honesty comparison passes against the
  regenerated artifact rather than only against the committed bytes (`11f-c`). Deleting the
  emitting statement from the generator removes the caveat and fails the guard (`11f-ctl`), so
  none of the three is vacuous.
- **Gate 5's certified `§2` table and its pinned hash are untouched**, and the pin is proven LIVE
  rather than assumed: `14a` reports certified on the unmodified snapshot and `14b` reports STALE
  after one row moves with the pin left unchanged (`Z-gate5`, `Z-signed`).

---

## 4. Provenance and integrity

- Every case ran against a private `git archive bb664c6` snapshot under `TMPDIR`, with `HOME`,
  `XDG_CONFIG_HOME` and the global/system git configuration redirected into the scratch area.
- Controls `Z-check-type-strings.sh`, `Z-check-eval-codes.sh`, `Z-check-vendor-honesty.sh` and
  `Z-test_verifier.py` assert each consumer under test is byte-identical to its `bb664c6` blob:
  `9bcdb562…`, `7970d226…`, `1ead2f37…`, `924749d5…`.
- Control `Z-clean` asserts **0 changed paths** in the boundary of the repository under test
  when the run ends.
- The full per-case consumer output is reproducible by re-running with
  `A_EXTRACT_EVIDENCE_DIR=<dir>`; the excerpts in §2 are quoted from that capture.

## 5. `TESTS.patch` — measured, and NOT applied

`TESTS.patch` adds `published_type_strings()` (carrying the current behaviour unchanged) plus
`TestPublishedTypeStringsSectionExtent` to `verifier/test_verifier.py`, and states the reason-class
vocabulary case 13 requires so the shell and Python halves cannot drift. **This revision added
exactly one test — the tilde-fence twin of the existing backtick-fence test — and modified no
existing assertion.**

Verified against a throwaway extraction of `bb664c6`:

- `git apply --check` — **applies cleanly.**
- Applied to a scratch copy, `TestPublishedTypeStrings` (the two pre-existing tests) still
  **pass**, so the patch changes no behaviour on its own.
- **`TestPublishedTypeStringsSectionExtent` now carries 12 tests, of which 10 are expected to
  FAIL** (9 failures + 1 error) and **2 are controls that pass** —
  `test_a_well_formed_section_is_read_whole` and `test_the_live_proposal_still_publishes_six`.
- Running both classes together: **14 tests, 10 expected failures.**
- The two fence tests, `test_a_quoted_heading_is_not_the_anchor` and
  `test_a_tilde_fenced_heading_is_not_the_anchor`, both fail — each is its own test rather than a
  parameter of the other, so a reader can point at the one that moved.

**The patch is not applied.** `verifier/` is untouched by this batch.

## 6. Live proof that the subject correction works

> **PARTLY SUPERSEDED BY §0-OID.** Run 2 below used `HEAD`, which the current grammar REFUSES.
> Runs 1 and 3 used exact 40-hex oids and remain valid as written.

Three historical runs of the same pre-D-066 harness file, differing only in the subject argument.
Their `74 of 74` figures are preserved as measured history; the current harness is remeasured in
§0-D066 at `70 of 70`.

| # | requested ref | resolved subject | REQUIRED held | CONTROL |
|---|---|---|---|---|
| 1 | `bb664c626d592d86391f644bf014e76f2bbf7db4` | `bb664c626d592d86391f644bf014e76f2bbf7db4` | **21 of 52** | 74 of 74 |
| 2 | `HEAD` | `2579bcb03c9bd16291316a08febe98c43a62baa7` | **21 of 52** | 74 of 74 |
| 3 | a private clone with **one consumer changed** | `32f8d4cd9be76f424413ec51b12bb43b74c0b4e0` | **24 of 52** | 74 of 74 |

**Run 2** shows the resolved subject and every identity line follow the ref that was asked for.
The verdicts are identical to run 1 — correctly, because the four consumers are byte-identical at
both commits — so on its own it proves the subject is *recorded*, not that a change would be
*seen*.

**Run 3 is the falsification of the defect.** A private clone of this repository was checked out
at the pre-repair commit, **one line** of `scripts/check-eval-codes.sh` was changed there from an
unanchored `grep -q "$code"` to a word-anchored `grep -qE "(^|[^A-Za-z0-9_])${code}([^A-Za-z0-9_]|$)"`,
and that was committed **in the clone only**. Running the harness against that commit:

```
  case 2a         REQUIRED  FAIL → PASS
  case 12suffix   REQUIRED  FAIL → PASS
  case 12prefix   REQUIRED  FAIL → PASS
  REQUIRED : 24 of 52 held      (was 21 of 52)
  CONTROL  : 74 of 74 held      (unchanged)
  case Z-check-eval-codes.sh  CONTROL PASS  byte-identical to SUBJECT_SHA 32f8d4cd…: b4ca2c4f…
```

**Exactly the three exact-token membership cases moved, and nothing else.** The integrity control
reports the subject's blob — `b4ca2c4f…`, not the pre-repair `7970d226…`.

**Under the instrument as it stood before this correction, all three would have stayed FAIL and
the control would have printed `7970d226…`**, because the snapshot came from a constant. That is
the defect, demonstrated rather than described.

**This is a FIXTURE, not a production repair.** It lives in a throwaway clone under `TMPDIR`; the
Sentinel repository is untouched, and `Z-clean` in every run above asserts so. The one-line
change is not proposed as the repair — the implementer owns that, against this contract.

**A fourth observation, recorded because it is the harness behaving correctly:** the first attempt
at run 3 **refused at preflight** — the fresh clone had no `ts/node_modules`, so the canonical
generator (case `11f`) could not run, and `P7` died with exit 2 rather than skipping. *A check
that cannot execute must never read as a check that passed.*

## 7. Gate binding — D-059(7), PARTLY discharged

Measured separately by `a-extract-gate.sh`: **fast-profile gate binding is MEASURED** — 7 of 7
REQUIRED and 11 of 11 CONTROL held on the corrected revision. **The deep profile (`--gate`) was NOT run**; its coverage rests
on static control-flow evidence only, and **D-059(7) is therefore NOT yet fully discharged.**
What the eventual independent post-repair verification must do to close it — run the deep profile
at the exact candidate SHA and capture the three stage banners, with three deep mutation runs
*not* required unless the control flow differs — is stated in **`GATE-BINDING.md` STATUS**.
