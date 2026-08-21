# A-EXTRACT — INDEPENDENT INSTRUMENT RE-REVIEW (SUBJECT RESOLUTION ONLY)

**VERDICT: HOLD**

Reviewer: a second independent agent. I authored none of `a-extract.sh`, none of its cases, none
of its evidence, and none of the corrective commits. I did not write, and have not edited,
`INSTRUMENT-REVIEW.md`; its **VERDICT: FAIL** stands exactly as its author wrote it.

**Scope, deliberately narrow.** The first independent review returned FAIL on one defect — an
ambiguous refname was not refused, and `P3` could not fail. That defect was repaired at `bac7cd8`
and its evidence completed at `6f2f65f`. **This review re-verifies that repair, and the assurance
that nothing else moved. It does not re-run the contract.** Subject: the harness at `HEAD`
(`cefc135`), branch `step-3/isolated-signer`, sha256
`4ad1eb55de50ca23c23aa22c61f7b00c12514371c6e74c2c7206629ef7a7bb32`; sibling `a-extract-gate.sh`
sha256 `99c6d8d65fe08f5572c1ce63d6ad06a9742a2411a53ba5cbbbbb1e586bd5cf97`.

## The verdict in one paragraph

**The defect is closed, and I proved it rather than read it.** I reproduced the original
fail-open against raw git first, then established that the collision is refused at exit `2` with
**zero scored verdicts**, that the abbreviated-object-id-shaped branch name is refused too, that
the two mechanisms really do cover different cases (proved by ablation, not by reading the
table), that the paired control in the same colliding clone measures a matrix **case-for-case
identical** to the baseline, and that `P3` **can be made to fail on the committed harness with no
modification to it whatsoever** — which is a stronger falsification than the corrective commit
itself claims. Twenty-seven subject shapes were put through the instrument. Under stock git
configuration **not one of them measured anything while ambiguous.** The verdict is HOLD.
**One residual is open and it is not small (R1):** git's ambiguity warning has an off switch, and
mechanism 2 is the *only* detector for one ambiguity class. With that switch thrown — from the
measured repository's own `.git/config`, or from `GIT_CONFIG_COUNT` in the caller's environment,
which this harness's isolation block does not neutralize although it neutralizes five other git
variables — I obtained a complete 126-verdict run, exit `1`, **all 74 controls green**, `P3`
PASS, of a commit the caller did not name. That is the same *shape* as the defect just repaired,
reached through a *different and narrower* door. It is a residual rather than a reproduction
because it requires a non-default configuration state, not merely a ref; the defect under repair
required neither.

---

## Per-item results

| # | Item | Result | Key measurement |
|---|---|---|---|
| 1 | Branch/tag collision refused as instrument failure, **zero verdicts scored** | **HOLD** | exit `2`, `scored=0`, mechanism-1 diagnostic naming both refs; same in `a-extract-gate.sh` |
| 2 | Abbreviated-oid-shaped branch name refused; enumeration alone would miss it | **HOLD** | exit `2`, `scored=0`, mechanism-2 diagnostic; **ablation proves** enumeration alone does not refuse it |
| 3 | Paired control still measures in the same colliding clone | **HOLD** | `refs/heads/ambig` → `bb664c6…`, 126 verdicts, `21 of 52` / `74 of 74`, exit `1`; matrix identical to baseline but for `P3`'s own description |
| 4 | `P3` genuinely falsifiable | **HOLD** | `case P3 CONTROL FAIL` obtained **on the unmodified committed harness**; also FAILs under two-mechanism ablation |
| 5 | Attempt to defeat it | **PARTIAL — residual R1 open** | 27 shapes; 0 measured while ambiguous under stock git. **1 configuration state produced a full green measurement of an unnamed commit** |
| 6 | Nothing else moved | **HOLD** | `21 of 52` / `74 of 74` reproduced; 136-line matrix vs `f1c0fdd` differs only in `P0`'s hash and `P3`'s description; 114 `check` call sites, case ids and kinds identical |
| 7 | Source repository clean; no git config written | **HOLD** | `git status --porcelain` empty; `.git/config` sha256 and mtime unchanged; `.git/index`, `.git/objects` mtimes unchanged; zero tags |

Conventions used throughout, and they matter:

* **A verdict is a line of output, not an exit status.** "Scored verdicts" counts output lines
  matching `^  case .* (PASS|FAIL) `. `OBSERVED` lines print `....` and are not verdicts. Every
  refusal claim below is `scored=0` measured on the output, not inferred from exit `2`.
* **Every probe is paired with something that had to move.** A refusal probe that cannot be
  distinguished from a broken harness is worth nothing, so each refusal is stated beside a run in
  the *same* repository that resolved and measured.
* Paths are written `<scratch>`; runs used a redirected `HOME`, `XDG_CONFIG_HOME`,
  `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM` and `GIT_CONFIG_NOSYSTEM=1`, and no repository outside
  `<scratch>` was written to.

---

## Item 0 — the original defect, re-measured against raw git before touching the harness

I did not take the corrective commit's account of git's behaviour on trust. In a throwaway clone
I created the collision myself:

```
bb664c626d592d86391f644bf014e76f2bbf7db4 refs/heads/ambig
f1c0fddad382d34d589df3e0274e25363280abd8 refs/tags/ambig
```

```
$ git rev-parse --verify 'ambig^{commit}'
exit=0  stdout=f1c0fddad382d34d589df3e0274e25363280abd8
stderr: warning: refname 'ambig' is ambiguous.

$ git rev-parse --verify --quiet 'ambig^{commit}' 2>/dev/null      # the pre-repair form
exit=0  stdout=f1c0fddad382d34d589df3e0274e25363280abd8
(no diagnostic at all)
```

The tag is silently preferred, exit `0`. The first review's finding is correct and the premise
the repair rests on is correct. git 2.50.1, bash 3.2.57, on the same host.

---

## Item 1 — the collision is refused, and nothing is scored

**Probe.** `a-extract.sh <scratch>/clone ambig`, in the clone that carries the collision above.

```
  case P0         OBSERVED ....  harness sha256 4ad1eb55de50ca23c23aa22c61f7b00c12514371c6e74c2c7206629ef7a7bb32
  case P1         OBSERVED ....  /usr/bin/grep is used for every search; canary matched
  case P2         OBSERVED ....  git version 2.50.1 (…) ; bash 3.2.57 ; Python 3.9.6

  PREFLIGHT FAILED: subject ref 'ambig' is AMBIGUOUS in <scratch>/clone — it names 2 refs:
                       refs/tags/ambig
                       refs/heads/ambig
                     git would silently prefer one of these and warn on stderr. This harness
                     refuses instead. Name the ref in full, e.g. refs/heads/ambig.
```

**exit `2`; scored verdicts `0`.** The three lines above the refusal are `OBSERVED`, and by the
harness's own `check()` an `OBSERVED` line prints `....` and increments no counter. The refusal
sits **before** `P3`, which is the first scored line in the file, so "zero scored" is a property
of the ordering and not only of this run.

`a-extract-gate.sh <scratch>/clone2 ambig` — **exit `2`, scored `0`**, same mechanism-1
diagnostic. The sibling was read *and run*; the first review could only read it, and flagged its
finding there as unmeasured.

**The sibling's paired control was run too, end to end against the primary repository at the same
subject** — the real fast gate, three times, `forge` and both submodule trees present:

```
  case P3-subject CONTROL PASS  'bb664c626d59…db4' resolves identically by TWO independent routes
                                (rev-parse=bb664c62…, show-ref+cat-file=bb664c62…) and the clone
                                is checked out at it
  …
  REQUIRED : 7 of 7 held        CONTROL : 10 of 10 held
```

Exit `0`. `Z-clean` and `Z-signed` both PASS inside that run. The `7 of 7` / `10 of 10` figures
`GATE-BINDING.md` carries from **before** the resolution rewiring reproduce **unchanged after
it** — which is the assurance the corrective commit asked to be taken on its word.

**What this probe moved.** Nothing yet — see item 3, which is the run that had to move and did.

---

## Item 2 — the abbreviated-oid-shaped branch name, and the asymmetry tested rather than believed

**Construction.** `refs/heads/bb664c6` → `f1c0fdd…`. One ref, and a name that is also a valid
abbreviation of a different commit.

**Raw git, and the enumeration done by hand:**

```
$ git rev-parse --verify 'bb664c6^{commit}'
exit=0 -> f1c0fddad382d34d589df3e0274e25363280abd8
stderr: warning: refname 'bb664c6' is ambiguous.

candidates that exist, in gitrevisions order:
  refs/heads/bb664c6            <- and nothing else
```

So enumeration sees **one** ref. The harness nonetheless refuses:

```
  PREFLIGHT FAILED: subject ref 'bb664c6' is AMBIGUOUS in <scratch>/clone.
                     git said: warning: refname 'bb664c6' is ambiguous.
                     git resolved it anyway, to f1c0fddad382d34d589df3e0274e25363280abd8, by its own precedence
                     order. This harness refuses rather than inherit that choice.
```

**exit `2`; scored `0`.** The diagnostic differs in wording from item 1's, which is itself the
evidence that a *different* mechanism fired.

**The asymmetry, proved by ablation rather than by the table.** I made scratch copies of the
committed harness with one mechanism deleted from each, and ran them in the same clone.

| harness copy | subject | outcome |
|---|---|---|
| mechanism 2 deleted | `ambig` | refused, `scored=0` — enumeration catches the collision |
| mechanism 1 deleted | `ambig` | refused, `scored=0` — stderr catches the collision |
| **mechanism 2 deleted** | **`bb664c6`** | **NOT refused.** Reached `P3`, which reported **PASS** (`rev-parse=f1c0fdd…`, `show-ref+cat-file=f1c0fdd…`), and went on to the snapshot |
| both deleted | `ambig` | `case P3 CONTROL FAIL  rev-parse=f1c0fdd…, show-ref+cat-file=<none>` |
| **both deleted** | **`bb664c6`** | **`case P3 CONTROL PASS`** — no third detector exists for this class |

Row 3 is the claim under test and it holds: enumeration alone does not catch it. Row 5 is **not**
in the repair's documentation and is the seed of residual R1 below: for this ambiguity class,
`P3` is not a backstop, so mechanism 2 is not merely *a* detector, it is the *only* one.

---

## Item 3 — the paired control still measures, and measures the same thing

**Probe.** `a-extract.sh <scratch>/clone refs/heads/ambig` — the fully-qualified name, in the
identical clone that still holds the collision, with `ts/node_modules` copied in so the generator
case can run.

```
== SUMMARY ==
  harness sha256   : 4ad1eb55de50ca23c23aa22c61f7b00c12514371c6e74c2c7206629ef7a7bb32
  requested ref    : refs/heads/ambig
  resolved subject : bb664c626d592d86391f644bf014e76f2bbf7db4
  pre-repair ref   : bb664c626d592d86391f644bf014e76f2bbf7db4

  REQUIRED : 21 of 52 held
  CONTROL  : 74 of 74 held
```

```
  case P3         CONTROL  PASS  'refs/heads/ambig' resolves to the same commit by TWO independent
                                 routes — rev-parse=bb664c62…, show-ref+cat-file=bb664c62…
```

Exit `1`. **126 scored verdicts.** This is the control that had to move, and it moved: the fix is
not "refuse everything".

**Stronger than the tally.** I extracted every `case` line from this run and from the primary
baseline run and diffed them. **136 lines each; exactly one differs**, and it is `P3` echoing the
ref name it was given:

```
< case P3 CONTROL PASS 'refs/heads/ambig' … rev-parse=bb664c62… show-ref+cat-file=bb664c62…
> case P3 CONTROL PASS 'bb664c626d59…db4'  … rev-parse=bb664c62… show-ref+cat-file=bb664c62…
```

Every other case id, kind, status and description is byte-identical. A fix that refused
selectively but measured the wrong thing would have produced a different matrix here.

**Names that must still resolve, all measured (each reached `P3` and passed it):**
`refs/heads/ambig` → `bb664c62…`; `refs/tags/ambig` → `f1c0fdd…`; an **annotated** tag `annot` →
peeled to `bb664c62…` by the `cat-file` route; a lightweight tag `light` → `f1c0fdd…`;
`origin/HEAD`, a symbolic remote ref → `cefc135…`; `origin/main` → `6fa1ba8…`; a symbolic ref
`refs/symtest` and its short form `symtest` → `bb664c62…`; the ordinary branch name
`step-3/isolated-signer` → `cefc135…`.

---

## Item 4 — `P3` is falsifiable, and I did not need to modify the harness to show it

The corrective commit demonstrates `P3` failing only *"with both refusals disabled in a scratch
probe copy"*. That is a weaker demonstration than the control deserves, because a control that
can only be made to fail in a doctored copy of the instrument is hard to distinguish from one
that cannot fail at all. **A stronger one exists, and it is this:**

**Construction — no edit to any harness file.** A branch whose name is a *full* 40-hex object id,
pointing somewhere else: `refs/heads/bb664c626d592d86391f644bf014e76f2bbf7db4` → `f1c0fdd…`. git
resolves the *object* for a 40-hex name and the *ref* is what `show-ref` reports, so the two
routes genuinely disagree. Silence git's warning so the run reaches `P3`
(`core.warnAmbiguousRefs=false`), and:

```
  case P3         CONTROL  FAIL  'bb664c626d592d86391f644bf014e76f2bbf7db4' resolves to the same
                                 commit by TWO independent routes — rev-parse=bb664c626d59…db4,
                                 show-ref+cat-file=f1c0fddad38…abd8
```

**`P3` FAILS on the committed harness, at its committed sha256, against a repository I built and
did not otherwise touch.** Route B is doing real work: it reported the ref while route A reported
the object.

Second, independent falsification (harness ablated, as the commit describes) — reproduced:

```
  case P3         CONTROL  FAIL  'ambig' … rev-parse=f1c0fdd…, show-ref+cat-file=<none>
```

Route B declines to answer rather than tie-breaking, exactly as claimed.

**Where `P3` is weaker than "two independent routes" sounds.** When the name matches **no** ref —
which is the *ordinary* case, since the documented invocation names a 40-hex commit — route B
falls back to `git cat-file --batch-check`, and that re-enters the same object-name resolver
`rev-parse` uses. I measured `cat-file --batch-check` emitting git's ambiguity warning itself, so
it is not literally the same command, but it is not an independent route either. For the baseline
invocation `a-extract.sh . bb664c6…db4`, `P3` is closer to a consistency check than to a
cross-check. That is worth saying plainly, because "unfalsifiable by construction" is the finding
being repaired. It is a real weakening, not a defect: `P3` is genuinely falsifiable in the
ref-denoting cases, which is where resolution ambiguity lives.

---

## Item 5 — the attempt to defeat it

### Every subject shape put through the instrument, under stock git configuration

| # | Subject ref | Construction | Outcome | Scored |
|---|---|---|---|:--:|
| 1 | `ambig` | branch **and** tag, different commits | refused (mech 1) | 0 |
| 2 | `bb664c6` | branch named like an abbreviated oid | refused (mech 2) | 0 |
| 3 | `bb664c6…db4` | branch named like a **full** oid | refused (mech 2) | 0 |
| 4 | `HEAD` | with `refs/heads/HEAD` also present | refused (mech 1: `HEAD` + `refs/heads/HEAD`) | 0 |
| 5 | `ORIG_HEAD` | pseudo-ref **and** `refs/heads/ORIG_HEAD` | refused (mech 1) | 0 |
| 6 | `MYREF` | `.git/MYREF` **and** `refs/heads/MYREF` | refused (mech 1) | 0 |
| 7 | `origin/main` | remote-tracking **and** a local branch of that name | refused (mech 1) | 0 |
| 8 | `HEAD@{0}` | reflog syntax over an ambiguous `HEAD` | refused (mech 2) | 0 |
| 9 | `dangle` | symbolic ref to a nonexistent ref | refused (`ignoring dangling symref`) | 0 |
| 10 | `AMBIG` | case-mismatched name, refs packed | refused (`Needed a single revision`) | 0 |
| 11 | `-dash` | branch whose name begins with `-` | refused; **no argument injection** — git's own `fatal:` is quoted back | 0 |
| 12 | *(empty string)* | — | refused | 0 |
| 13 | `--all` | an option in ref position | refused | 0 |
| 14 | `:/A-EXTRACT` | commit-message search syntax | refused | 0 |
| 15–27 | `refs/heads/ambig`, `refs/tags/ambig`, `annot`, `light`, `origin/HEAD`, `symtest`, `refs/symtest`, `féé`, `a%b`, `x{y}`, `a#b`, `a@b`, `step-3/isolated-signer` | unambiguous names, incl. unicode and `% { } # @` | **resolved and measured**, `P3` PASS both routes | ≥1 |

**Under stock git configuration I could not construct a subject ref that measured anything while
ambiguous, and could not construct one that selected a commit other than the one it denotes.**
Cases 4–6 are worth flagging as a positive finding: `git show-ref --verify` accepts pseudo-refs
(`HEAD`, `ORIG_HEAD`, `FETCH_HEAD`, and a hand-written `.git/MYREF` — all measured), so
enumeration covers gitrevisions' first rule, which is the rule I expected the candidate list to
have missed.

### R1 — the one that fails open, stated in full

**Mechanism 2 reads git's warning. git's warning can be turned off. For one ambiguity class
mechanism 2 is the only detector, and `P3` is not a backstop for it (item 2, row 5).**

Two doors, measured separately:

| Vector | Result |
|---|---|
| `core.warnAmbiguousRefs=false` in the **measured repository's** `.git/config` | **silences mechanism 2** — repo-local config is not overridable by the caller |
| `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.warnAmbiguousRefs GIT_CONFIG_VALUE_0=false` in the **caller's environment** | **silences mechanism 2** — the isolation block redirects `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM`, `HOME`, `XDG_CONFIG_HOME` and unsets `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE`/`GIT_COMMON_DIR`/`GIT_PREFIX`, but not these |
| the same setting in the caller's **global** git config | **defeated** — the harness's own redirection neutralizes it. Measured: still refused |

With the second door open and `refs/heads/bb664c6` → `f1c0fdd…` present, the harness ran to
completion:

```
== SUMMARY ==
  requested ref    : bb664c6
  resolved subject : f1c0fddad382d34d589df3e0274e25363280abd8
  pre-repair ref   : bb664c626d592d86391f644bf014e76f2bbf7db4

  REQUIRED : 21 of 52 held
  CONTROL  : 74 of 74 held
  REQUIRED FAILURES with every control holding: the defects are observed.

  case P3  CONTROL  PASS  'bb664c6' resolves to the same commit by TWO independent routes —
                          rev-parse=f1c0fdd…, show-ref+cat-file=f1c0fdd…
```

Exit `1`. **126 scored verdicts of a commit the caller did not name, every control green, and
`P3` affirming there is no ambiguity.** `a-extract-gate.sh` behaves the same way: under the same
env vector it passed resolution on `bb664c6` and stopped later, for an unrelated missing
dependency.

**How much this is worth, stated honestly and in both directions.**

* *Against severity.* It requires a git configuration state that is not the default and is not
  the state of this repository. The branch/tag collision — the defect actually under repair — is
  refused by enumeration alone and is therefore **immune to both doors**; I verified that
  (`ambig` still refused with warnings silenced by each vector). And the identity block does
  print the true 40-hex resolved subject, twice.
* *For severity.* `COVERAGE.md` states *"Neither is a single point of failure, and that is
  measured rather than asserted."* For the abbreviated-oid class that is **not so**: mechanism 1
  misses it by design, `P3` passes it, so mechanism 2 stands alone — and it stands on a
  configurable warning. The claim is true as *"each catches a case the other misses"* and false
  as *"no class has a single detector"*, and those read alike.

**Two fixes, neither of which I have made** (nothing outside my own deliverable was written):

1. One line in the isolation block closes the environment door: `unset GIT_CONFIG_COUNT` (and any
   `GIT_CONFIG_KEY_*` / `GIT_CONFIG_VALUE_*`) beside the `GIT_DIR` unset that is already there.
2. A configuration-independent detector for the class closes the other: when enumeration finds
   exactly one ref, refuse if the name is *also* a resolvable object id — or promote the
   route-A/route-B disagreement into the refusal rather than only into `P3`.

Both are decisions about the instrument's contract, so they are proposed here and not taken.

---

## Item 6 — nothing else moved

**Baseline, re-measured at `HEAD`'s harness against the primary repository, subject
`bb664c626d592d86391f644bf014e76f2bbf7db4`:**

```
  REQUIRED : 21 of 52 held
  CONTROL  : 74 of 74 held
```

Exit `1`. **126 scored verdicts** (52 REQUIRED + 74 CONTROL) across 136 `case` lines.

**Case set, reason vocabulary, expected outcomes and exclusions versus `f1c0fdd` — measured, not
read.** I extracted `f1c0fdd`'s harness from the object database (sha256 `ea661aff…`, matching
what the first review recorded) and ran it against the same repository and the same subject, then
diffed the two 136-line matrices. **Two lines differ, both by design:**

```
< case P0 OBSERVED .... harness sha256 ea661aff…            (the old harness's own hash)
> case P0 OBSERVED .... harness sha256 4ad1eb55…

< case P3 CONTROL PASS  the requested ref '…' resolves to exactly one commit and that commit is
                        the recorded SUBJECT_SHA …
> case P3 CONTROL PASS  '…' resolves to the same commit by TWO independent routes —
                        rev-parse=…, show-ref+cat-file=…
```

Same id, same kind, same status; only `P3`'s description changed. Corroborating reads:

* `diff` of the two harness files touches **only** lines 434–459 → 434–563, the subject-resolution
  and `P3` region. No case body is inside that range.
* 114 `check` call sites in each file; the extracted `(case-id, kind)` lists are **identical**.
* `TESTS.patch` is byte-identical to `f1c0fdd`; `INSTRUMENT-REVIEW.md` is byte-identical to
  `7e4e5c0`.
* `bac7cd8` + `6f2f65f` touch only files under `A-EXTRACT-tests/`. The only production files
  changed between `f1c0fdd` and `HEAD` are `scripts/test.sh` and `verifier/test_verifier.py`, and
  both belong to `cefc135`.
* The sibling's figures reproduce after its rewiring: `7 of 7` REQUIRED, `10 of 10` CONTROL,
  exit `0` — the numbers `GATE-BINDING.md` carries from before the correction, which it flagged
  as measured beforehand rather than re-measured.
* `CARD.md` / `COVERAGE.md` / `GATE-BINDING.md` changes describe the correction and the new
  diagnostics; no case, reason string, expected outcome or exclusion is added, removed or
  reworded. The one over-statement in them is R1 above.

**The deliberately red `HEAD`.** `cefc135` applies `TESTS.patch` and ratchets the verifier floor,
so the verifier suite and the fast gate fail by design. That is stated in the record, it is not a
finding of mine, and it does not bear on subject selection: the harness measures a snapshot of
the *subject* commit, and both my baseline and the paired control name `bb664c6…`, which predates
it.

---

## Item 7 — the source repository is clean, and no git config was written into it

Recorded before the first run and re-checked after every run in this review, including two full
matrix runs and a `a-extract-gate.sh` invocation against the primary repository:

| Observable | Before | After |
|---|---|---|
| `git status --porcelain` | 0 lines | 0 lines |
| `.git/config` sha256 | `7fab4730…f809e96` | `7fab4730…f809e96` |
| `.git/config` mtime | `1785413271` | `1785413271` |
| `.git/index` mtime | `1787273711` | `1787273711` |
| `.git/objects` mtime | `1787273712` | `1787273712` |
| tags | 0 | 0 |

The harness redirects `HOME`, `XDG_CONFIG_HOME`, `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` into
its own scratch directory and sets `GIT_CONFIG_NOSYSTEM=1`. Every colliding ref I created lives
in clones under `<scratch>` that I made and will delete; **no ref, tag or configuration key was
written into the repository under review.** The one configuration change in this review
(`core.warnAmbiguousRefs=false`, R1) was made in my own clone and never in the source repository.

---

## Residuals

* **R1 — mechanism 2 has an off switch, and for one ambiguity class it is the only detector.**
  Open. Stated in full above with both doors, both fixes, and the measured 126-verdict run that
  it produces. This is the only finding in this review that could change a verdict.
* **R2 — `P3`'s independence is partial.** For a subject that denotes no ref — which is the
  documented, ordinary invocation — route B falls back to `cat-file --batch-check`, which shares
  git's object-name resolver with route A. `P3` is a genuine cross-check for ref-denoting
  subjects and closer to a self-consistency check for object-id subjects. Not a defect; a limit
  on what a green `P3` licenses you to say.
* **R3 — most of item 5's shapes were run in a clone without `ts/node_modules`.** Those runs stop
  at `P7` with exit `2` after `P3` has printed, so what they establish is the resolution outcome
  and `P3`'s verdict — which is exactly what those probes are for — and not a full matrix. Three
  runs did produce a complete 126-verdict matrix: the primary baseline, the paired control, and
  R1's fail-open demonstration.
* **R4 — path sanitization.** `sanitize_path` rewrites a home-directory prefix only; a repository
  outside `$HOME` prints its absolute path in the summary. Visible in every clone-based run
  above. The first review recorded sanitization residuals; this one persists.
* **R5 — the sibling was measured on the FAST profile only.** `a-extract-gate.sh` ran end to end
  (`7 of 7` / `10 of 10`, exit `0`), so its resolution wiring, `P3-subject`, and its `G1`/`G2`/`G3`
  demonstrations are measured here, not read. The deep profile (`--gate`) was not invoked — the
  harness says so itself in its own summary, and that statement is unchanged by this review.

---

## What this review does NOT establish

* **It does not re-run the contract.** I did not re-verify subject provenance, the snapshot's
  bytes, the consumer-integrity controls, the live-tree scope of `Z-clean`/`Z-gate5`/`Z-signed`,
  or any of the 52 REQUIRED cases on their merits. `INSTRUMENT-REVIEW.md` establishes those and
  is unaffected by this document.
* **It does not say the case set is right.** It says the case set did not *change*. Whether 21 of
  52 is the correct number for `bb664c6…` is a question about the contract, not the instrument.
* **It does not certify `a-extract-gate.sh` on the deep profile.** Its ambiguity refusals were
  measured (exit `2`, `scored=0`, four shapes), and one full fast-profile run completed at
  `bb664c6…`. `./scripts/test.sh --gate` was not invoked, and `D-059(7)` is not discharged by
  anything here — the harness's own summary says so and I am repeating it, not overriding it.
* **It says nothing about `HEAD` being red.** `cefc135` makes the verifier suite and the fast
  gate fail by design. I ran neither at `HEAD`, and neither bears on subject selection.
* **It does not establish behaviour on any git other than 2.50.1.** Mechanism 2 matches the
  string `ambiguous` in git's stderr. A git that words its warning differently, or is localized,
  would silence it exactly as R1's configuration does. I did not test another git.
* **It does not prove the absence of a defeating subject ref** — only that twenty-six shapes,
  chosen to cover gitrevisions' precedence rules, pseudo-refs, symbolic refs, annotated tags,
  remote-tracking collisions, case folding, packed and loose refs, option-shaped and
  extended-syntax names, did not defeat it.
* **It does not decide anything.** The verdict is HOLD and R1 is open. Whether R1 is acceptable
  as it stands, fixed in the instrument, or bounded by a stated precondition, is not a reviewer's
  call.
