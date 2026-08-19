# V2 — independent reverification of `V3-N1` and `R4-F4`

**Frozen commit evaluated:** `c8d15a76425544148d7da2f8fa0c003feb6ad2b7`
(confirmed by `git rev-parse HEAD` in the V2 worktree before any probe, and re-confirmed
unchanged after the last probe).

**Verdicts**

| Item | Verdict |
|---|---|
| `V3-N1` — `scripts/check-review-scope.sh` must fail closed on `git ls-files` failure and on unexpected emptiness; diagnostic must name the correct base | **FAIL** |
| `R4-F4` — suite counts derived or single-sourced, no stale duplicate on a reader-facing sibling surface | **FAIL** |

Both failures are of the **sibling** requirement, not of the demonstrated branch. In both cases
the branch the previous reviewer exploited is now correctly repaired, and in both cases a
same-shape twin survives inside the repair's own blast radius. Residuals are listed separately
in section 3.

---

# 1. `V3-N1`

## 1.1 The general property, stated before looking at the fix

Written down before reading the repaired script, from `R1-F2`'s argument as the brief states it:

> **A coverage instrument must never report coverage it did not measure.** Concretely: every
> point at which `check-review-scope.sh` learns something from outside itself must be able to
> distinguish *"I looked and there was nothing"* from *"I failed to look"*, and must refuse in
> the second case. A number the script prints must be a number it measured.

Where that property must hold: **at every external-command call in the script**, not at the two
the finding named. That is the enumeration in 1.3.

## 1.2 Requirements 1-4: the named repair holds

All commands below were run from the V2 worktree root. `git` was shadowed by a PATH shim at
`<SCRATCH>/stub/git` which execs the real binary for every call except the one being sabotaged,
selected by `GIT_STUB_MODE`.

### Control first (COMMON-BRIEF: a probe with no control cannot distinguish fail-closed from always-fails)

```
$ ./scripts/check-review-scope.sh
review scope: R1=241  R2=46  R3=151  (assigned 438 of 438 tracked files)
  remediation surface: 48 file(s) changed since A-070's parent, all assigned
  preservation-only:   79 file(s) (round-six record; faithfully preserved with
                       disclosed path sanitization, no behaviour)
  reviewer 4 is unassigned BY DESIGN (D-056(d)) and ranges over every surface above
rc=0

$ PATH="<SCRATCH>/stub:$PATH" GIT_STUB_MODE=passthru ./scripts/check-review-scope.sh
  ... byte-identical output ...
rc=0
```

The pass-through control is load-bearing: it proves the shim itself is transparent, so any
refusal seen later is caused by the sabotage and not by the presence of a shim on `PATH`.

### Requirement 1 — `git ls-files` FAILS

```
$ PATH="<SCRATCH>/stub:$PATH" GIT_STUB_MODE=lsfiles_fail ./scripts/check-review-scope.sh
  FAIL  git ls-files failed:
    fatal: stub: ls-files refused (index unreadable)
    Refusing to report a partition measured against nothing.
rc=1
```

**HOLDS.** Refuses, names the failure, echoes git's own stderr, exits non-zero.

### Requirement 2 — `git ls-files` returns EMPTY with exit 0 (the dangerous case)

```
$ PATH="<SCRATCH>/stub:$PATH" GIT_STUB_MODE=lsfiles_empty ./scripts/check-review-scope.sh
  FAIL  git ls-files returned NO tracked files.
    A repository with nothing in it is not a repository whose every file is assigned.
rc=1
```

**HOLDS.** This is the case the brief flags as indistinguishable from success, and the script
distinguishes it. The guard is a genuine second test, not a side effect of the first: the stub
exits **0** here, so the `$? -ne 0` branch is not what caught it.

### Requirement 3 — the diagnostic names the correct base/reference

Two separate things had to be true, and both are.

**(a) The pinned constant really is what it claims.** `SCOPE_BASE_DEFAULT` is
`140c59e5aa8feab72831534886fda4048cff8fe7`, and the header calls it "the full 40-character
object name of A-070's parent".

```
$ git log -1 --format='%s' 140c59e5aa8feab72831534886fda4048cff8fe7
session-state and the round-six brief, rewritten for a fresh instance

$ git rev-list --all --children | grep ^140c59e5aa8feab72831534886fda4048cff8fe7
140c59e5aa8feab72831534886fda4048cff8fe7 a89c255d8836f6ad3056fbe50970c5f00655a592

$ git log --oneline --all --grep=A-070
a89c255 A-070: the first remediation under the D-052(b) repair protocol
```

The pinned base's only child is `a89c255`, which is A-070. The label is **correct**, and the
"full, not abbreviated, not relative" claim in the header is correct.

**(b) The printed label tracks the base actually used**, rather than being a fixed string:

```
$ SENTINEL_SCOPE_BASE=a89c255d8836f6ad3056fbe50970c5f00655a592 ./scripts/check-review-scope.sh
  remediation surface: 46 file(s) changed since a89c255d8836f6ad3056fbe50970c5f00655a592, all assigned

$ ./scripts/check-review-scope.sh                                   # control
  remediation surface: 48 file(s) changed since A-070's parent, all assigned
```

The count moved with the base (48 -> 46) *and* the label moved with it. A true count under a
false label — the LOW half of `V3-N1` — is fixed, and the control proves the label is not merely
echoing whatever it was handed.

### Requirement 4 — the ordinary run still assigns everything

Covered by the control above: `R1=241 R2=46 R3=151`, `assigned 438 of 438`, exit 0. The
partition is not vacuous and the script is not simply refusing everything.

## 1.3 Requirement 5 — the sibling sweep. **This is where it fails.**

Enumerated mechanically, not from memory:

```
$ awk '!/^[[:space:]]*#/ && /git |wc |tr |printf |sed |awk |cat |grep |cut /{printf "%4d: %s\n", NR, $0}' \
      scripts/check-review-scope.sh
```

Every external-command call whose empty or failed output could be mistaken for a clean result:

| # | Line | Call | Guarded? | Evidence |
|---|---|---|---|---|
| S1 | 47 | `cd "$(git rev-parse --show-toplevel)"` | **NO** | P4 — see residual R-1 |
| S2 | 106 | `tracked="$(git ls-files 2>&1)"` | **YES** — failure *and* emptiness | P1, P2 |
| S3 | 131 | `$(printf '%s\n' "$tracked" \| wc -l \| tr -d ' ')` | **NO** (cosmetic) | residual R-2 |
| S4 | 161 | `git rev-parse --verify --quiet "${since}^{commit}"` | **YES** | P6 |
| S5 | 168 | `scope_diff="$(git diff --name-only "$since"..HEAD 2>&1)"` | **YES** for failure; **NO** for empty | P10, P7 |
| S6 | 198 | `git ls-files --error-unmatch "$f" >/dev/null 2>&1 \|\| continue` | **NO** | **P3 — the failure** |

### S6 is the finding, alive, ninety-two lines below its own repair

Line 198 is the **third** `git ls-files` call in this script. Its non-zero exit is
unconditionally reinterpreted as the benign meaning `# deleted since; not in scope` and the file
is dropped from the remediation surface. Nothing distinguishes *"this path is not tracked"* from
*"git failed"*.

Sabotaging **only** that call — bare `git ls-files` still works, so S2's guard is satisfied and
the first half of the script is untouched:

```
$ PATH="<SCRATCH>/stub:$PATH" GIT_STUB_MODE=errorunmatch_fail ./scripts/check-review-scope.sh
review scope: R1=241  R2=46  R3=151  (assigned 438 of 438 tracked files)
  remediation surface: 0 file(s) changed since A-070's parent, all assigned
  reviewer 4 is unassigned BY DESIGN (D-056(d)) and ranges over every surface above
rc=0
```

**Paired control, same stub binary, same invocation, sabotage off:**

```
$ PATH="<SCRATCH>/stub:$PATH" GIT_STUB_MODE=passthru ./scripts/check-review-scope.sh
  remediation surface: 48 file(s) changed since A-070's parent, all assigned
```

**What the probe MOVED** (the brief's dead-probe test): the remediation surface went 48 -> 0 and
the `preservation-only: 79 file(s)` line disappeared entirely. Both loops' worth of work was
skipped. The probe is not silent-and-therefore-assumed-good; it changed two observable outputs.

Set this against the script's own header at lines 96-105, which describes `V3-N1` and says the
defect was that `ls-files` failing produced

> `0 file(s) changed since A-070, all assigned`, exit 0

and calls fixing the demonstrated branch while leaving its sibling *"the exact defect this
repository has now recorded more times than any other"*. The sentence produced above is that
sentence, differing only by the `_scope_label` improvement made in the same repair. The
`git diff` twin (S5) was guarded, the bare `git ls-files` twin (S2) was guarded, and the
`git ls-files --error-unmatch` twin was not.

Additionally, S6 sits **upstream of the script's own unassigned check**: line 200's
`if [ "$who" = "UNASSIGNED" ]` is never reached for any file the `|| continue` swallows. So a
skipped file is not merely uncounted, it is unchecked.

### Honest limits on S6 — how reachable is it without a shim?

I tried to reach S6 through ordinary repository content and got two negative results and one
latent positive. These are reported as probes, not as support:

- **Quoted paths — LATENT POSITIVE.** `git diff --name-only` emits C-quoted names for paths with
  non-ASCII bytes, and `--error-unmatch` on that literal quoted string fails. Demonstrated in a
  throwaway repository with no shim: a changed, tracked file named with an accented character
  came out of `diff` as `"caf\303\251.md"` and was silently dropped. **But** the repository has
  **0** such paths today (`git ls-files | grep -c '^"'` -> `0`), and loop 1 would independently
  flag such a name as UNASSIGNED, so today this route is latent and masked.
- **Glob metacharacters — DEAD PROBE, hypothesis disproved.** I predicted a tracked
  `docs/note[1].md` would pass `assign()` but fail `--error-unmatch` as a pathspec glob. It did
  not: git matched it literally and `--error-unmatch` returned 0.
- **Submodule gitlinks — negative.** `--error-unmatch` returns 0 for both
  `contracts/lib/forge-std` and `contracts/lib/openzeppelin-contracts`.

So the demonstrated route is a PATH shim plus a latent content route. I do not think that
weakens the verdict, for two reasons. First, a PATH shim is precisely the evidentiary standard
`V3-N1` itself was established on — the script's own header records that the finding came from a
verifier who *"failed `ls-files` with a PATH shim"*. Second, the requirement in BRIEF-V2 item 5
is not "demonstrate an exploit"; it is "enumerate every external-command call whose empty or
failed output could be mistaken for a clean result, and say whether each is guarded." S6's
failed output **is** mistaken for a clean result, and it is not guarded.

## 1.4 What this evidence does and does not establish

**Establishes:** the two behaviours BRIEF-V2 items 1 and 2 demand are present and are two
independent guards; the pinned base is genuinely A-070's parent; the printed label tracks the
base actually used; the ordinary run is not vacuous; and one enumerated sibling call reproduces
the exact prohibited sentence with exit 0.

**Does not establish:** that S6 is reachable today by ordinary use — no non-shim route is live in
this repository at this commit. Does not establish anything about `check-review-scope.sh` under a
bash other than the 3.2.57 that `#!/usr/bin/env bash` resolves to here. Does not establish
anything about the correctness of the partition's *content* (which file belongs to which
reviewer), only about the instrument's honesty when its inputs fail.

## 1.5 Verdict — `V3-N1`: **FAIL**

Requirements 1, 2, 3 and 4 hold and were each falsified with a paired control. Requirement 5
fails: the sibling sweep the finding exists to force was not completed by the repair, and the
call it missed produces the finding's own signature output.

---

# 2. `R4-F4`

## 2.1 The general property, stated before looking at the fix

> **A number a reader can act on must exist in exactly one place, and that place must be the one
> the gate asserts.** Not "the number is currently correct" — correctness is what drifted five
> times. The property is *uniqueness of the copy*, because a second copy is only ever
> accidentally right.

## 2.2 Requirement 1 — is there exactly one source?

The authoritative numbers are six shell constants in `scripts/test.sh`:

```
$ grep -nE "^(FOUNDRY_MIN_TESTS|TS_MIN_TESTS|VERIFIER_MIN_TESTS|VERIFIER_MIN_SAMPLES|VERIFIER_MIN_TAMPER|VERIFIER_MIN_TAMPER_MODES)=" scripts/test.sh
234:FOUNDRY_MIN_TESTS=92
235:TS_MIN_TESTS=527
658:VERIFIER_MIN_TESTS=209
659:VERIFIER_MIN_SAMPLES=7
660:VERIFIER_MIN_TAMPER=78
673:VERIFIER_MIN_TAMPER_MODES=30
```

`scripts/check-suite-floors.sh` genuinely **derives**: it greps those six names out of
`scripts/test.sh`, restates no number of its own, and fails if any is unreadable. Read in full;
its `get()` is `grep -E "^$1=" "$GATE" | head -1 | cut -d= -f2`. Its header is also honest about
a distinction the rest of the repository blurs — *"THIS PRINTS THE FLOORS, NOT THE COUNTS...
reporting a floor as a measurement is the defect one layer up."* That is the right instrument.

**But it is not the only copy.** `docs/session-state.md` section 3 restates three of the six, in
the present tense, in the same section that twice says it does not:

```
340: **DO NOT READ A SUITE COUNT FROM THIS FILE. RUN `./scripts/test.sh` AND READ ITS OUTPUT, OR RUN
341: `./scripts/check-suite-floors.sh` (R4-F4, D-055(e), CONFIRMED).**
...
346: repeatedly forbids. **The figures are no longer duplicated here.** The gate constants are the
347: only copy, and `scripts/check-suite-floors.sh` prints them from the script itself, so this file
348: cannot drift from them again.
...
351: **What is stable and worth stating: 50 corpus fixtures · 7 samples · 78 tamper cases over 30
352: modes · workspace guards 0 NEW findings with 13 pre-existing baselined — it PASSES ON RATCHETED
353: DEBT, which is not the same as clean.**
...
360: **THE FLOOR VALUES ARE DELIBERATELY NOT REPRINTED HERE.** This passage previously quoted
361: `FOUNDRY_MIN_TESTS=75, TS_MIN_TESTS=507` in present tense while the constants were 89 and 526 —
362: **eleven lines below its own claim that the figures are no longer duplicated in this file.**
```

`7` is `VERIFIER_MIN_SAMPLES`. `78` is `VERIFIER_MIN_TAMPER`. `30` is
`VERIFIER_MIN_TAMPER_MODES`. All three are floor values, all three are among the six that
`check-suite-floors.sh` prints as *"the only copy"*, and all three are reprinted **five lines
below** the claim that the figures are no longer duplicated here and **nine lines above** the
claim that the floor values are deliberately not reprinted here.

The previous iteration of this repair left `FOUNDRY_MIN_TESTS`/`TS_MIN_TESTS` eleven lines below
its own claim. This iteration removed those two and left the verifier's three, five lines below
the same claim. It is the same defect, one constant-group over.

Three further points sharpen it rather than soften it:

- Line 340 forbids the reader from doing exactly what lines 351-352 invite: the verifier's
  sample/tamper/mode figures **are** suite counts — `scripts/test.sh` prints them on one line as
  `suite ... · samples ... · tamper ... cases / ... modes`.
- They are introduced as *"What is stable and worth stating"* — a present-tense liveness claim,
  the strongest possible framing for a reader to act on. This is the brief's own test for
  reader-facing: a person acting on this document encounters the number and believes it.
- They are **floors presented as measurements**, which is the precise error
  `check-suite-floors.sh`'s own header warns against, in the document that names that script as
  the authority.

**The counter-argument, stated fairly, and why I reject it.** One can read "the figures" and "the
floor values" in section 3 as scoped to the Foundry/TypeScript/verifier-test counts that `R4-F4`
originally named, in which case 7/78/30 are a different category and the section is compliant. I
reject it because the remediation instrument the section itself designates as the authority
enumerates all six constants, and because the section's own opening sentence scopes the
prohibition to "a suite count", which these are. Reasonable people could differ on severity; the
factual claim — that a present-tense, unbound second copy of three gate floor constants sits
inside the section asserting there is none — is not in dispute and is demonstrated below.

## 2.3 Requirement 3 — falsifying my own sweep

A sweep that cannot fail proves nothing, so I made the source move and checked that the document
did not follow.

**Mutation** (in the V2 worktree only, `scripts/test.sh` backed up first, no gate run in flight):
`VERIFIER_MIN_TAMPER=78` -> `VERIFIER_MIN_TAMPER=80`.

**(a) Does the single-source mechanism reflect it?**

```
$ ./scripts/check-suite-floors.sh
  VERIFIER_MIN_TAMPER        80
suite floors: read from scripts/test.sh, which is the only copy.
```

Yes — `check-suite-floors.sh` is genuinely derived, not a restatement. This is the half of the
repair that works.

**(b) Would my sweep catch a document that disagreed?** My sweep reads the floors *from*
`check-suite-floors.sh` rather than hardcoding them, so it re-targets automatically:

```
== tamper   (source says 80) ==
docs/session-state.md:351:78 tamper cases        <-- live surface, present tense, now WRONG
docs/decisions.md:219:78 tamper cases            <-- dated A-0NN entry, historical
```

Yes. The sweep flags `docs/session-state.md:351`, and it flags it *because the source moved*,
which is exactly what will happen the next time a verifier floor is ratcheted.

**(c) Does anything in the repository catch it?** No. With the floor at 80 and
`docs/session-state.md` still saying 78, all twelve guards pass:

```
check-class-coverage rc=0    check-eval-codes rc=0       check-findings-ledger rc=0
check-gate-immutability rc=0 check-label-integrity rc=0  check-label-prompt rc=0
check-rename-gate rc=0       check-review-scope rc=0     check-secrets rc=0
check-suite-floors rc=0      check-type-strings rc=0     check-vendor-honesty rc=0
```

And `check-suite-floors.sh` is invoked by **nothing**: it is not a stage of `scripts/test.sh` and
no script calls it. Its only references are three prose mentions in `docs/session-state.md` and
one in `docs/decisions.md`. So the "mechanical binding John required" binds the *reader who
chooses to run it*; it does not bind the document. Single-sourcing here is prose discipline with
a convenience reader attached, and prose discipline is what failed five times.

**Revert confirmed:** `git diff --stat -- scripts/test.sh` and
`git status --porcelain -- scripts/test.sh` both empty afterwards; `VERIFIER_MIN_TAMPER=78`
restored.

## 2.4 Requirement 2 — the mechanical sweep, and which surfaces I treated as which

68 tracked `.md` files. Split by the brief's rule:

- **FROZEN, out of scope — 52 files** under `docs/review-2026-08-1*/`. Preserved review evidence;
  a number inside is a record of what was said. Not swept for staleness.
- **LIVE, in scope — 16 files.** Swept.

| Live surface | Contains a suite figure? | Treated as | Why |
|---|---|---|---|
| `README.md` | no | — | verified clean |
| `HANDOFF.md` | no | — | verified clean; "suite" appears only as prose |
| `Sentinel_Protocol_Lab_Proposal_v0_2.md` | no | — | only `D-010 verifier` false positives |
| `docs/repair-protocol.md` | no | — | clean |
| `docs/d055e-scope-manifest.md` | no | — | clean |
| `docs/exit-criterion-packet.md` | no | — | clean |
| `docs/gate-5-vendor-audit.md` | no | — | clean |
| `fixtures/corpus/LABELLING_PROMPT.md` | no | — | clean |
| `docs/ablation-report.md` | ablation table only | out of finding scope | not suite counts |
| `docs/gate-s1-evidence.md` (`43/43 Foundry`) | yes | **historical** | signed gate pack, held immutable by `check-gate-immutability.sh`; a figure in it is the record at S1 signing |
| `docs/gate-s2-evidence.md` (`66/66 Foundry`) | yes | **historical** | same |
| `docs/decisions.md` (many; latest `Suite 92 Foundry / 527 TypeScript / 209 verifier`) | yes | **historical** | dated append-only `A-0NN (date)` entries, each recording state at that action |
| `docs/v1-1-register.md` (`Suite 146 -> 149`, `over 29 modes`) | yes | **historical** | register entries citing past transitions in past tense |
| `verifier/REPORT.md` (`5 samples`, `39 tests`, ...) | yes | **historical** | a dated changelog table of the verifier's own growth |
| `docs/round-six-brief.md` (`75/75 · 481/481 · 180/180 · 7 samples · 78 tamper cases over 30 modes`) | yes | **historical — CONTROL** | see 2.5 |
| `docs/session-state.md` section 3 | yes | **MIXED — see below** | the defect |

`docs/session-state.md` section 3 is deliberately split rather than classified whole:

- Lines 343-344, `507/507 TypeScript · 198/198 verifier ... floors were 513 and 209` —
  **historical, correctly framed, NOT flagged.** This is the section narrating the original
  `R4-F4` defect in the past tense. Flagging it would be the false positive the brief warns
  against.
- Lines 351-352, `7 samples · 78 tamper cases over 30 modes` — **live, present tense, FLAGGED.**

**No stale *disagreeing* live duplicate exists at this commit** — 7/78/30 currently match. So
BRIEF-V2 requirement 2, read strictly as "no *stale* duplicate", passes today. Requirement 1,
"exactly one source", fails.

## 2.5 Requirement 4 — the control

The control must be a document quoting a historical count in a clearly historical frame that must
**not** be flagged. `docs/round-six-brief.md:26-31`:

```
## Baseline at the time of writing — VERIFY IT YOURSELF BEFORE RELYING ON IT

Deep gate green: **75/75 Foundry · 481/481 TypeScript · 180/180 verifier · 7 samples · 78 tamper
cases over 30 modes · 50 corpus fixtures ...**
This line has been wrong before; `./scripts/test.sh --gate` is the authority, not this sentence.
```

This control is stronger than it looks, and it is why I am confident the sweep is discriminating
rather than merely number-hunting: **every one of `75`, `481`, `180` is stale** against `92`,
`527`, `209` — this document disagrees with the source far more than the flagged one does, and it
is still correct. It is time-scoped ("at the time of writing"), it names the authority, and it
pre-emptively disclaims itself. A sweep that flagged this would be useless.

The paired discrimination is therefore:

| | agrees with source | disagrees with source |
|---|---|---|
| **present-tense live claim** | `session-state.md:351` — **FLAGGED** (the defect: right today, unbound tomorrow) | — |
| **explicitly historical frame** | — | `round-six-brief.md:28` — **NOT FLAGGED** (correct) |

The flagged item is the one that agrees; the unflagged one is the one that disagrees. The sweep
is keyed on framing, not on arithmetic, which is the only way it can be right about both.

## 2.6 What this evidence does and does not establish

**Establishes:** `check-suite-floors.sh` is a genuine derivation from a single source and moves
when that source moves; the Foundry/TypeScript/verifier-test counts are no longer duplicated on
any live surface; three verifier floor constants **are** duplicated in present tense on the one
document the finding was filed against; the duplicate is unbound (proved by mutation); and no
guard in the repository binds any document to the floors.

**Does not establish:** that the duplicate is currently *wrong* — it is currently right. Does not
establish that the full gate enforces the mutated floor — I did not run `scripts/test.sh --gate`
(see COVERAGE.md). Does not establish that my line-based sweep is complete; it demonstrably is
not (see residual R-4).

## 2.7 Verdict — `R4-F4`: **FAIL**

The mechanical half is real and works. The property it is supposed to serve — one copy — is not
established: three of the six floor constants have a second, hand-maintained, present-tense copy
inside the very section that asserts, twice, that no such copy exists. That is the same sentence
shape the repair was returned for, one constant-group away, and my mutation shows nothing
propagates and nothing complains.

---

# 3. Residuals — real limits recorded, NOT failures

- **R-1 (`V3-N1`, MEDIUM).** `scripts/check-review-scope.sh:47`,
  `cd "$(git rev-parse --show-toplevel)"`, is unguarded. When the substitution is empty, bash
  treats `cd ""` as a successful no-op and the script silently proceeds against the current
  directory. Run from `contracts/` with `rev-parse --show-toplevel` failing, it exits 1 but with a
  **false diagnostic**: `13 tracked file(s) assigned to NO reviewer: foundry.toml, lib/forge-std,
  src/SentinelVault.sol ...`. Those files *are* assigned — as `contracts/foundry.toml` etc. A
  maintainer acting on that message would add wrong arms to the partition, which is the "reader is
  led to the wrong corrective action" shape `R4-F4` was filed for. It fails closed, so this is a
  residual and not part of the verdict. Run from the repo root the same failure is invisible and
  the run succeeds by luck.
- **R-2 (`V3-N1`, LOW).** Line 131's `printf ... | wc -l | tr -d ' '` is an unchecked pipeline
  inside a command substitution. Failure would render `assigned 438 of  tracked files`. Cosmetic
  only: the authoritative counts come from the loop, not this pipeline.
- **R-3 (`V3-N1`, LOW / by design).** Line 168's `git diff` is guarded against failure but not
  against an unexpectedly empty result. `SENTINEL_SCOPE_BASE=HEAD` yields
  `0 file(s) changed since HEAD, all assigned`, exit 0. I do **not** count this as a defect: the
  diff genuinely is empty, the measurement is real, and the `_scope_label` fix means the reader is
  told the base was `HEAD`. Recorded because it is the one place where the same sentence is
  legitimately printed, which makes it a poor sentence to rely on as a distress signal.
- **R-4 (`R4-F4`, MEDIUM — method limit).** My sweep is line-based and this repository hard-wraps
  prose. `docs/session-state.md:351` ends `...78 tamper cases over 30` and line 352 begins `modes`,
  so **the `30 modes` duplicate was invisible to every regex I ran** and I found it by reading. The
  same wrap hides `78 tamper` in `docs/round-six-brief.md:28`. Any future mechanical guard binding
  documents to floors must join wrapped lines before matching, or it will ship as a dead probe.
- **R-5 (`R4-F4`, LOW).** `50 corpus fixtures` is likewise duplicated between
  `docs/session-state.md:351`, `docs/round-six-brief.md:28` and several hardcoded strings in
  `scripts/test.sh` (`echo "corpus: 50 fixtures executed..."`, and comments at lines 478, 539, 679,
  929). It is not one of the six floor constants, so it is outside the finding as scoped, but it is
  the same shape and there are more copies of it than of anything `R4-F4` addressed.
- **R-6 (`R4-F4`, LOW).** `docs/decisions.md:246` (the newest entry, `A-078`) carries
  `Suite 92 Foundry / 527 TypeScript / 209 verifier`. I classified `decisions.md` as a historical
  append-only log and did not flag it. Recording it because the *newest* entry in a decision log is
  the one a resuming reader is most likely to read as current state, and it is a hand-typed copy
  bound to nothing. This is a judgement call and John may want to rule on it rather than have a
  reviewer settle it.

# 4. New concerns outside my scope (reported per COMMON-BRIEF, not part of any verdict)

- **N-1.** `scripts/check-gate-immutability.sh` returned rc=0 while `scripts/test.sh` was modified
  in the working tree. I did not investigate what that guard's subject actually is, and it may be
  entirely correct — it is recorded only so someone whose scope covers it can confirm.

# 5. Questions for John — not answered here

1. Does the `R4-F4` property cover all six floor constants that `check-suite-floors.sh` prints, or
   only the three suite-test counts the finding originally named? My FAIL rests on the former
   reading. Under the latter reading `R4-F4` would be HOLD with R-6 outstanding. This changes what
   the repair owes and is a scope ruling, not an engineering judgement.
2. Should `docs/decisions.md` entries be exempt as historical record, or should decision entries
   stop restating suite counts altogether (R-6)?
