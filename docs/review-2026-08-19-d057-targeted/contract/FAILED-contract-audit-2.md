> # AUDIT OF A FAILED, SUPERSEDED CONTRACT — preserved as evidence
> The contract this audits is **not operative** (D-060(1)). The audit's FINDINGS remain
> factually valid about the tree and several are carried into the batch cards; the
> CONTRACT it audits is abandoned. **Do not implement from the contract.**

---

# CONTRACT AUDIT 2 — the repeat audit of REPAIR-CONTRACT v2

**Authority:** D-059(10). The v1 audit returned FAIL; D-059(10) buys **ONE** contract revision and
**one** repeat audit, and neither consumes a batch implementation attempt. This is that repeat
audit.

**Auditor:** independent, and a different agent from the v1 auditor. I did not draft
`REPAIR-CONTRACT.md` (v1 or v2), did not write `ENUMERATION.md`, reported none of the findings
under adjudication, authored none of the adjudications, and wrote none of the code, prose or
guards under examination. I attacked v2; I did not defend it.

**Frozen commit:** `a18e6e61598a996d962798ad0353a166232d4490`, confirmed by `git rev-parse HEAD`
in my worktree before the first probe and again after the last.

**Worktree restored.** `git diff HEAD --stat` empty; `git status --porcelain` shows only the
pre-existing untracked `ts/node_modules`. After restoration `check-eval-codes.sh` (`41/41`),
`check-type-strings.sh` (`6/6`), `check-secrets.sh` (`clean`) and `check-vendor-honesty.sh`
(mechanical conditions pass) each re-run green. Scratch probes ran in a session scratch directory
and in throwaway repositories created there; `install-hooks.sh` was never executed anywhere that
could reach a real repository's config. Nothing was repaired, signed, certified, ratified or
reaffirmed. Nothing was committed or pushed. No file outside this evidence directory was changed.

**Instrument hygiene.** Every sweep used `/usr/bin/grep`. Every loop over a word-split list was run
under `/bin/bash`, not the session shell — **this trap fired on me live**: my first pass over the
41 eval codes reported *zero* codes missing from `check-class-coverage.sh`'s map, because `zsh`
did not word-split the variable and the single multi-line "pattern" matched as an alternation.
Re-run under `bash` the true answer is **two**. Both readings are recorded rather than the
convenient one. Every document-editing probe asserts on the line it expects before the guard runs
and prints `WROTE-OK`.

**Evidence bound, stated where it bites.** `contracts/lib/forge-std` and the other submodule
directories are **empty** in this worktree, so `forge build`/`forge test` cannot run and the
Foundry artifacts the TypeScript suite loads do not exist. **I did not re-run Batch B's Solidity
mutants or the full TypeScript suite.** I did run the one TypeScript file that binds `EVAL_CODES`
(`121/121` at base SHA, and `121/121` again under A-R5's falsification). Batch B's and Batch C's
core evidence is therefore carried on the v1 auditor's measured record, which v2 cites; I neither
confirm nor dispute it, and I say so at the point it matters.

---

## VERDICT: **FAIL**

| # | Dimension | v1 | **v2** |
|---|---|---|---|
| 1 | Sibling-list completeness | FAIL | **FAIL** |
| 2 | Unadjudicated items entering scope | HOLD | **FAIL** |
| 3 | Duplicate ownership across batches | FAIL | **FAIL** |
| 4 | Historical material treated as live (and the converse) | FAIL | **FAIL** |
| 5 | Whether every proposed test observes its named defect | FAIL | **FAIL** |
| 6 | Whether every mechanical guard is invoked by the actual gate | FAIL | **HOLD** |
| 7 | Count and terminology consistency within the contract | FAIL | **FAIL** |
| 8 | Shared primitives stretched across different guarantees | FAIL | **HOLD** |

**F1..F19 tally: 12 FIXED · 5 PARTIALLY FIXED · 2 NOT FIXED.**

**v2 is a real improvement and it is not sufficient.** Its two hardest calls are right and I
verified both by measurement: the F13 inversion (a deeper heading belongs INSIDE; v1 would have
forced a correct guard to refuse) and the separation of identifier membership into A-R5, whose
falsification I reproduced surviving at base SHA with both of its controls discriminating. The
A-P1/A-P2a splits are genuine. What fails is the same thing that failed in v1, one layer further
out: **the rewrite was organised by root cause but its enumerations were still run with
spelling-shaped commands over the directories somebody already reported**, and two obligations
were lost in the restructuring — one of them `V3-N1`, the confirmed finding D-058(8) names first.

---

# PART 1 — the nineteen failures

| # | v1 failure | v2 | One-line evidence |
|---|---|---|---|
| F1 | git-root class is 13 not 5 | **PARTIAL** | 13 correct **for `scripts/*.sh`**; the class by mechanism is **14** — `.githooks/pre-commit:4` is invisible to both halves of v2's regex and to its glob |
| F2 | `check-secrets.sh` four skip points; gate's mode | **PARTIAL** | mode analysis right; the skip-point table omits the rule-1 basename match and the rule-4 retrieval, and mislabels one row's mode |
| F3 | third §5.8 consumer in `verifier/` unowned | **FIXED** | in A-R3's table, owner named, opposite tie-break stated |
| F4 | four more extractions in the vendor guard | **PARTIAL** | 3 of 4 groups added; the §2 row-scan group dropped — **demonstrated fail-open below** |
| F5 | false completeness claim between the two D-F2 sites | **NOT FIXED** | `docs/gate-s2-evidence.md:527-529` appears **nowhere** in v2; the paragraph labelled "F5 fix" resolves a different subject |
| F6 | single-sourcing claim restated outside every batch | **FIXED** | A-R6 names it (citation off by two lines) |
| F7 | two live "no floors exist" surfaces | **PARTIAL** | named without locations, and dispositioned **both** inside A-R6 and outside every batch |
| F8 | `session-state.md` written by two batches | **PARTIAL** | boundary stated, but the owners are given as "A-R6 and D-F2/D-F3" and D-F3 is REMOVED |
| F9 | `check-suite-floors.sh` row hid one route | **FIXED** | three routes stated (A-R1 `cd`, A-R4 `head -1`, A-R6 floors) |
| F10 | `C5` owned by nobody | **FIXED** | D-F6 created and owns both sites |
| F11 | Batch D edits a file Gate 5 calls off-limits | **FIXED** | carve-out recorded; git facts verified |
| F12 | D-F2's third site is deliberately-preserved material | **FIXED** | default editing foreclosed, disposition required (wrong line cited) |
| F13 | **A-P2a observed nothing; item (c) demanded the wrong answer** | **FIXED** | **verified in both directions by probe — see below** |
| F14 | controls labelled as falsifications | **FIXED** | §7 table plus a governing rule |
| F15 | A-G1 left its own counter-example standing | **FIXED** | "wire it or record an argued exemption" |
| F16 | A-G1 did not require the live gate-runs table to follow | **FIXED** | A-G1(6) |
| F17 | "six `cd`-bearing scripts" vs "FIVE distinct scripts" | **FIXED** | 13 stated consistently; table has 13 rows (a **new** count contradiction appears elsewhere — dimension 7) |
| F18 | A-P1 stretched across three root causes | **NOT FIXED** | split done, but the third strand — **`V3-N1` itself** — now has **no owning section** |
| F19 | A-P2a stretched across three properties | **FIXED** | A-R3 / A-R4 / A-R5, widening obligation added |

## F13 — verified FIXED, by probe, in both directions

This was the item I was told to attack hardest. v2 claims it split identifier membership into A-R5
and inverted the depth requirement. Both claims hold.

**Direction 1 — a deeper heading must stay INSIDE and the guard must be unchanged.** Inserting
`##### 5.7.1.1 Grouping notes` inside §5.7.1 (anchor `#### 5.7.1`, depth 4):

```
extent = 36 lines
eval codes: 41/41 engine checks documented in §5.7.1 (D-031)      EXIT=0
```

**v1's success condition would have required a refusal here, and that would have been wrong.**
v2's corrected requirement matches the measured correct behaviour.

**Direction 2 — a same-or-shallower heading must END the section.** Both spellings terminate:

| Inserted heading | Depth vs anchor | extent | Result |
|---|---|---|---|
| `#### 5.7.1.1 …` | same | 19 lines | exit **1**, names 7 absent codes |
| `### 5.7.2 …` | shallower | 19 lines | exit **1**, names 7 absent codes |

**A-R5's falsification genuinely observes the prefix defect.** Renaming
`EVAL_SIM_STOP_IMPERSONATION_FAILED` → `…_FAILE` across `ts/src/evaluate/checks.ts` (2 sites) and
`ts/test/evaluate.checks.test.ts` (1 site), spec untouched:

```
occurrences of the truncated name in the proposal, word-bounded : 0
scripts/check-eval-codes.sh      -> eval codes: 41/41 …            EXIT=0      SURVIVES
scripts/check-class-coverage.sh  -> pass on the ratchet            EXIT=0      SURVIVES
ts/test/evaluate.checks.test.ts  -> tests 121  pass 121  fail 0                SURVIVES
```

**Both controls discriminate.** The non-prefix `…_FAILEX`, one character different and the same
length, is caught: `eval codes: 1 check(s) declared by the engine and absent from §5.7.1`, exit
**1**. The same truncating rename applied to `EVAL_ACTION_DEADLINE` is caught by the second
instrument: `corpus class coverage: FAILED`, exit **1**.

**A-R5's scope note is accurate.** Derived under `/bin/bash` (see instrument hygiene), exactly
**2 of 41** codes are absent from `check-class-coverage.sh`'s map —
`EVAL_NATIVE_DELTA_MATCHES_VALUE` and `EVAL_SIM_STOP_IMPERSONATION_FAILED` — and A-R5's
falsification sits at that intersection deliberately.

**A-R3's crux control also reproduces.** At base SHA, a second differing `MandatePayload` line
placed under a `#### ` heading (genuinely INSIDE §5.8) and under a `### ` heading (genuinely
OUTSIDE it) produce **byte-identical** guard output — same extent (22), same sentence, same exit
0. `cmp` reports no difference. And the widening figure v2 states is right: demoting `## 6.` to
bold prose extends §5.7.1's extent **35 → 62** lines with the guard still printing `41/41`, exit
0. (ADJ3 §1.6 records 64 for this; **62 is the correct figure** and v2 has it.)

## F5 — NOT FIXED, and it is the failure mode this audit exists to catch

The v1 audit's F5 is a **live false sentence in the repository**, `docs/gate-s2-evidence.md:527-529`:

> **The two citations it names are corrected in the same checkpoint** (`docs/exit-criterion-packet.md` §3, `docs/session-state.md`). Corrected 2026-08-19 (A-080).

It is still false. `docs/exit-criterion-packet.md` §3 was corrected; `docs/session-state.md:162-163`
still reads *"ten accepted as documented limits"* — **and v2 agrees it is uncorrected**, because
D-F2 lists that very copy as a repair site. So the sentence asserting the sweep is complete sits
three lines above a site v2 enumerates, and v2 gives it no disposition: the token `527` occurs
twice in v2 and both are TypeScript test counts.

What v2 offers instead, inside D-F1:

> **F5 fix: v1 asserted completeness between its two sites; the enumeration is re-derived here and claims only what the paragraph-normalized sweep covered.**

That is a statement about the **contract's own** completeness claim, attached to a different item
(`R2-F4`). **The failure is named and a different one is resolved.** A contract that does this is
worse than one that omits the item, because the row reads as handled.

## F18 — NOT FIXED: `V3-N1` has no owner in v2

`V3-N1` — the scope checker's unguarded `git ls-files --error-unmatch "$f" … || continue` at
`scripts/check-review-scope.sh:198` — is one of the **eight** D-058(8) confirmed repair
obligations (adjudicated **FAIL**, `ADJUDICATED-D057-TARGETED.md` row 4) and the **first** item
D-058(8)A names for Batch A.

Measured over v2:

```
occurrences of the string V3-N1 in REPAIR-CONTRACT.md        : 0     (v1: 5)
occurrences of check-review-scope in REPAIR-CONTRACT.md      : 2     (v1: 4)
  :92   `check-review-scope.sh:47`  -> A-R1's git-root table (a DIFFERENT defect)
  :315  `check-review-scope.sh:106` -> §7's controls table
  :320  `(:198)` -> §7's controls table, "TRUE FALSIFICATION — survives" — bare, no file named
```

§1's single-ownership table has seven Batch A rows: root resolution; `check-secrets.sh` retrieval;
Markdown section extent; normative-publication uniqueness; identifier membership; floor constants;
guard-and-gate wiring. **None of them reaches a swallowed exit status in the scope checker.**
A-R1's guarantee is explicitly about relocating to a repository root. A-R2's is explicitly scoped
to `check-secrets.sh`. So v2 splits A-P1 into two primitives and drops one of its three strands on
the floor: the site survives only as one row of a table about *labelling*, with a falsification
attached to no obligation and no success condition.

v1's own §8.1 predicted this shape precisely — it recommended splitting off the file-list
primitive *and* "carry the side-effect obligation … into A-P1's success condition **rather than
leaving it in a table**". v2 carried the side-effect obligation and left `V3-N1` in a table.

**Compounding it, D-059(2) ordered a disposition that v2 deleted.** John: *"the
`printf "$tracked" | wc -l` site gets an explicit disposition — either established as safely
downstream of the non-empty check, or given its own observing test. **Do not leave it in the
inventory without disposition.**"* v1 carried that disposition (an argued exemption, `:84`).
**v2 contains zero occurrences of `wc -l`.** A ruling-mandated disposition was lost in the rewrite.

---

# PART 2 — v2 audited afresh on the eight dimensions

## 1. SIBLING-LIST COMPLETENESS — **FAIL**

I re-derived all three of v2's headline numbers independently. **13 and 7 are wrong; the "four
skip points" table does not contain four skip points.**

### 1.1 FAILURE — the root-resolution class is **fourteen** sites, and the missed one is the
pre-commit hook

v2 runs its enumeration as

```
/usr/bin/grep -lE '(cd "\$\(git rev-parse --show-toplevel\)"|[A-Za-z_]+="\$\(git rev-parse --show-toplevel\)")' scripts/*.sh
```

which returns 13. That command is **still shaped like the spellings already reported** — it
enumerates two literal quoted forms — and it is **still scoped to `scripts/*.sh`**. Swept by
mechanism instead, over every tracked file:

```
/usr/bin/grep -nE '\$\(git rev-parse --show-toplevel\)'   (tracked, excluding docs/)
  .githooks/pre-commit:4   repo_root=$(git rev-parse --show-toplevel)     <- UNQUOTED assignment
  …the 13 in scripts/…
```

`.githooks/pre-commit:4` is invisible to v2 **twice over**: the assignment is unquoted, so neither
alternative in the regex matches it (confirmed: the regex applied to the file returns exit 1); and
the file is not under `scripts/`. It then does exactly what A-R1's guarantee describes — resolves a
root and executes a script from the tree it resolved:

```
exec "$repo_root/scripts/check-secrets.sh" --staged
```

**Fail direction, measured** in throwaway repositories with a shimmed `git`:

| Case | Result |
|---|---|
| control, real `git`, from the repo | the target script runs with the right cwd, exit 0 |
| `rev-parse --show-toplevel` exits 128 | aborts, **exit 128** — fail-CLOSED |
| `rev-parse --show-toplevel` returns empty, exit 0 | `/scripts/check-secrets.sh: No such file or directory`, **exit 1** — fail-CLOSED |

Fail-closed lowers the severity of the site; it does not repair the enumeration. v2's own table
carries two fail-CLOSED members (`check-review-scope.sh:47`, `check-findings-ledger.sh:22`), so
"closed" is not v2's criterion for inclusion. And this member is not incidental: it is the
**installed pre-commit hook**, the only route by which `check-secrets.sh --staged` — A-R2's own
subject — is ever invoked, and the artifact that `install-hooks.sh` (A-R1's demonstrated
fail-OPEN member) points `core.hooksPath` at. It sits at the junction of the two sections that
name it in neither.

**Fix.** Sweep `git rev-parse --show-toplevel` in **any** substitution across **all tracked
files**, not two spellings across one directory. Route `.githooks/pre-commit:4` through A-R1 or
record an argued exemption. Correct the count and correct the claim in `ENUMERATION.md` that v2's
commands "match the *mechanism*".

### 1.2 FAILURE — A-R2's skip-point table contains neither four skip points nor the right ones

v2: *"FOUR skip points, TWO modes. v1 enumerated ONE."* Its table lists **five rows and six line
numbers**: `:85`, `:195`, `:198`, `:201`, `:226`, `:231`.

ADJ4 §C4.6 — the adjudication v2 is implementing — states the four as: *"the default-mode
`[ -f "$f" ] || continue`, rule 4's `git show`/`[ -f ]` pair at `:229`, and **rule 1's `basename`
case match**"*, plus the reported `:198`. Read against the file:

| Line | What it actually is | In v2's table? |
|---|---|---|
| `:85` | empty-line guard, rule-1 loop | yes ("shared") |
| **`:86` / `:88`** | **rule 1's `basename` case match — one of ADJ4's four** | **NO** |
| `:195` | empty-line guard, rule-3 loop — **shared**, above the mode branch at `:197` | yes, **mislabelled "staged"** |
| `:196` / `:227` | self-exclusion skips | no |
| `:198` | staged `git show … \|\| continue` (`C4`) | yes |
| `:201` | default `[ -f ] \|\| continue` — the gate's mode | yes |
| `:226` | empty-line guard, rule-4 loop | yes ("third loop") |
| **`:229`** | **rule 4's `body=$(git show … \|\| true)` — does not skip; scans an EMPTY body** | **NO** |
| `:231` | default `[ -f ] \|\| continue`, rule-4 loop | yes |

So v2 replaced two of ADJ4's four mechanisms with three benign empty-line guards.

**The omission of `:86`/`:88` is not theoretical — I demonstrated the bypass.** In a throwaway
repository, two byte-identical files each carrying a planted 64-hex key, differing only by one
non-ASCII byte in the **filename**, both tracked:

```
git ls-files
  .env.local
  ".env.locale\\xcc\\x81"                     <- C-quoted token

both present:            BLOCKED .env.local — env files are never committed (A-007).
                         BLOCKED .env.local — credential-shaped content: …
                         secret guard: 2 finding(s)                              EXIT=1
ASCII twin removed:      secret guard: clean                                     EXIT=0
```

The ASCII control fires at **both** rule 1 and rule 3, so the instrument is live in both. With only
the odd-named file present, a tracked env file carrying a planted key produces `clean`, exit 0.
**A-R2's guarantee — "must scan every file it reports having scanned" — is violated at a line the
table does not contain**, and `:229` violates it by a third mechanism (`|| true` yields an empty
body, so the file is *counted as scanned* rather than skipped) that also is not in the table.

### 1.3 FAILURE — A-R3 drops the §2 row-scan extent, and I demonstrated its fail-open

v2: *"ALL consumers, enumerated by mechanism (v1 had two; there are at least seven …)"*. Its table
adds `check-vendor-honesty.sh:306`, `:351`, `:365` — three of the four groups v1's F4 named — and
**drops `:297`, `:298`, `:308`**, the §2 capability-table row scans. Those are extent derivations
over a named region with their own terminator (`t&&!/^\|/{exit}` — the first line not starting with
a pipe), and that terminator **disagrees with the terminator `:365` uses over the same region**.

Probe: insert **one blank line** into the middle of the §2 capability table (after data row 8),
changing nothing else.

| | baseline | after one blank line |
|---|---|---|
| row-scan report | `ok    §2 capability table: 11 of 11 rows carry a marker resolving to a §13 entry` | `ok    §2 capability table: **8 of 8** rows carry a marker …` |
| certified-table SHA | `ok … certified by record` | `ok … certified by record` — **unchanged** |
| exit | 0 | **0** |

The whole diff between the two runs is that one line. **Three rows silently stop being checked for
the per-cell dated-and-linked marker D-008(1)'s mechanical half rests on; the guard's own text
promises "A row added later without [the marker] in its capability cell FAILS this gate. The count
is a ratchet" — and the ratchet silently ratchets DOWN with no diagnostic and no exit-code
change.** The SHA pin does not catch it because a blank line contributes nothing to the hash, which
is computed over an extent derived with a different terminator.

This is A-R3's property exactly — one named region, two extents, silently divergent, one of them
feeding the certification. v2 flags `:365` as *"THIS FEEDS THE HASH JOHN'S D-008(3) CERTIFICATION
IS PINNED TO"* and then leaves out the sibling extent that disagrees with it.

**One thing I checked and found harmless, recorded so it is not later assumed:** re-deriving §2's
extent under an anchor-depth-relative rule would **not** move `CERTIFIED_TABLE_SHA`, because the
only heading between `## 2.` and `## 3.` is `### 2.1` (depth 3, deeper than the depth-2 anchor) and
therefore stays inside under both rules. A-R3 can be implemented at `:365` without disturbing the
pin.

### 1.4 Residual — a fourth extraction idiom, undispositioned

`scripts/check-gate-immutability.sh:53` extracts a named region from `scripts/test.sh` with a
**paired-sentinel** terminator (`/^# >>> GATE BOOTSTRAP/` … `/^# <<< GATE BOOTSTRAP/`), which
prints to EOF if the closing sentinel is removed. It is fail-closed (the extracted text is hashed
against a pin), and v1 did not name it either. But A-R3 claims *three* tie-break styles and *all*
consumers; this is a fourth style. One line of argued exemption, or a row.

## 2. UNADJUDICATED ITEMS ENTERING SCOPE — **FAIL**

Most of v2 is careful here, and better than v1 in one respect: `check-vendor-honesty.sh:352`, which
v1 admitted to a batch carrying an instruction to *measure* rather than a classification, is moved
out to §8's recorded residuals with no disposition claimed. That is the right treatment.

**FAILURE — the F7 pair is simultaneously inside a batch and reserved for John.** A-R6's live-surface
list ends:

> **two live surfaces asserting the Foundry/TypeScript floors do not exist (F7), which are false since A-075 and have no disposition in v1 — the test author enumerates and dispositions them.**

§8, "OUTSIDE EVERY BATCH — returns to John", item 5:

> **Whether the "no floors exist" claims (F7) are repaired now or adjudicated as new findings.**

Both sites are live and unstruck, verified: `docs/v1-1-register.md:911-916` (*"NO GATE FLOOR EXISTS
ON THE FOUNDRY OR TYPESCRIPT SUITE COUNTS … neither count is read, compared or asserted … Not fixed
here"*, present tense) and `docs/exit-criterion-packet.md:105` (the §3b UNRESOLVED row). Neither is
adjudicated anywhere. D-058(7) and D-059(4) both require classification **before** an item enters a
batch. v2 puts them in A-R6's enumeration for the test author to disposition **and** reserves the
same question for John. An implementer cannot satisfy both sentences, and under the reading that
A-R6 owns them, an unadjudicated item has entered Batch A.

**Fix.** Pick one. If they return to John, strike them from A-R6's live-surface list and say A-R6's
enumeration deliberately excludes them. If they enter A-R6, they must be adjudicated first, and §8
item 5 must go.

## 3. DUPLICATE OWNERSHIP ACROSS BATCHES — **FAIL**

The dependency markings are right and better than v1's: `D-F3` removed, `D-F5` as claim-side use
only, `check-suite-floors.sh`'s three routes stated (F9), `session-state.md`'s A/D boundary stated
with a non-interference rule (F8), `C5` given an owner (F10).

### 3.1 FAILURE — an adjudicated obligation with no owner

`V3-N1`. Full evidence at F18 above. v1's §3.3 failed the same dimension for the same reason
(`C5` CONFIRMED, owned by nobody); v2 fixed that instance and created a worse one, because `V3-N1`
is not a new finding — it is one of the eight D-058(8) obligations and the first item D-058(8)A
lists.

### 3.2 FAILURE — `docs/exit-criterion-packet.md` is written by Batch A and Batch D

- **D-F1** owns `docs/exit-criterion-packet.md:211` (§7), and names **§3b's corrected copy** among
  the three controls that must stay unflagged. §3b's corrected row is `:103`.
- **A-R6**, under the F7 sentence, reaches `docs/exit-criterion-packet.md:105` — **the next row of
  the same §3b table.**

Two batches, one file, one table, adjacent rows, and no carve-out. That is F8's shape recurring in
a different file. D-059(5) is written per file *and* per factual repair. Under the other reading of
the F7 sentence (§8 item 5 — outside every batch) the collision disappears and A-R6's live-surface
enumeration is instead wrong. Either way it must change.

### 3.3 FAILURE — §1 names a removed item as a co-owner

> **`docs/session-state.md` is written by A-R6 (floor passages) and D-F2/D-F3 (count derivation) — F8 fixed by naming both here.**

§6: **"D-F3 — REMOVED (D-059(5)); Batch A owns the floor passages."** So §1 names three owners,
calls them "both", and one of the three does not exist. The substantive boundary A-R6 vs D-F2 is
stated correctly; the sentence carrying it is not.

### 3.4 Residual — an intra-batch collision with no boundary rule

`docs/session-state.md:774` is claimed twice inside Batch A: by **A-R6** (*"the table row restating
the single-sourcing claim"*) and by **A-G1(6)** (the *"which scripts the gate runs"* table, which
must be updated when wiring changes — and `:774` is the row for the very script A-G1(5) may wire).
Same batch, so D-059(5) is not breached, but v2 wrote an explicit non-interference rule for A-R6 vs
D-F2 and none for this.

## 4. HISTORICAL MATERIAL TREATED AS LIVE, AND THE CONVERSE — **FAIL**

The repository-facing half is handled well and I could not break it: no dated `decisions.md` entry
is scheduled for rewrite anywhere in v2; A-077 takes a supersession note per D-059(6); D-F1
re-derives to ONE live site rather than forcing two; A-R6 lists its historical controls
(`round-six-brief.md:28` under its own verify-it-yourself heading, `verifier/REPORT.md`'s dated
figures, dated `decisions.md` entries); F12's trap — that D-F2's third site is material a source
**deliberately** preserved — is named and default editing is foreclosed.

**FAILURE — v2 makes a document it labels *superseded* the operative specification for two of the
four batches.**

§4: *"**Unchanged from v1** and verified live by the auditor"*. §5: *"**Unchanged** and verified
live by the auditor"*. §1's opening: *"v1 is preserved unaltered as
`REPAIR-CONTRACT-v1-superseded.md`"* — i.e. as the audited artifact, the historical record of what
failed 7 of 8 dimensions.

The consequence is concrete, not formal, and it is wider than Batches B and C. Counted:

```
occurrences of "success condition" in REPAIR-CONTRACT-v1-superseded.md : 6   (A-P1, A-P2a,
                                                       A-F1, Batch B, Batch C, + one restatement)
occurrences of "success condition" in REPAIR-CONTRACT.md               : 3
  :108  A-R1's — the only one that states an obligation
  :170  prose about v1's F13 error
  :201  prose about v1's A-P2a
```

**v2 states exactly ONE success condition, A-R1's.** A-R2, A-R3, A-R4, A-R5, A-R6, A-G1, Batch B,
Batch C and every D-F item have none. v2 restates no guarantee, no authoritative-source statement
and no event/emit table for Batch B, and no branch matrix for Batch C. v1 has all of them. So
either those obligations live in a document v2 calls superseded, or they do not exist — and
D-058(1) requires a **precommitted specification** that the repairer implements against and **may
not weaken**. A specification with one success condition out of nine sub-items cannot discharge
that role, whichever way the ambiguity is read.

And the two documents **disagree**. v1's Batch B item 3 reads *"For each of the other seven events:
delete the emit; substitute a field value; substitute a different event. Each must fail a named
test"*, with the success condition *"every one of the eight events fails a named test under
omission and under field substitution"*. v2's §7 reclassifies that item — *"Batch B item 3 (parts)
| falsification | **mixed — split per event**"* — because six of the seven already pass. An
implementer told Batch B is "unchanged from v1" implements the uncorrected list; an implementer
reading §7 implements a different one. **A precommitted specification the repairer "may not weaken"
(D-058(1)) cannot be split across a live document and a superseded one that contradict each other.**

**Fix.** Either restate Batches B and C in full inside v2 with their success conditions, or state
explicitly and prominently that `REPAIR-CONTRACT-v1-superseded.md` §§ "BATCH B" and "BATCH C" are
**incorporated as operative annexes**, list every point at which v2 §7 overrides them, and stop
calling the file superseded without qualification.

## 5. WHETHER EVERY PROPOSED TEST OBSERVES ITS NAMED DEFECT — **FAIL**

**Verified sound, by me, at base SHA:** A-R5's falsification (survives: `41/41` exit 0,
class-coverage exit 0, `121/121`) with **both** controls discriminating (`…_FAILEX` exit 1;
`EVAL_ACTION_DEADLINE` truncation caught by class-coverage, exit 1); A-R3's crux control
(byte-identical output for opposite ground truths, `cmp` clean); A-R3's widening figure (35 → 62,
`41/41`, exit 0); F13's corrected requirement in **both** directions; A-R6's four stale COVERAGE
figures (`180` at `scripts/test.sh:981`, `160/7/77/29` at `:984`, and its own false sentence *"They
are corrected here"* at `:986`), `docs/session-state.md:470`'s stale trio, and §3 at ~`:365`;
D-F1's site (`docs/exit-criterion-packet.md:211`, §7 BLOCKER 1); A-R2's mode fact
(`scripts/test.sh:176` invokes the secret guard with **no** flag); A-R1's gate fact
(`scripts/test.sh:209` invokes the vendor guard; nine guards at `:173`-`:209`, no profile
conditional); D-F2's arithmetic (five named as repaired, one of them partial, so four wholly
removed, ten minus four is six). **Batch B's and Batch C's mutants I could not run — see the
evidence bound.**

### 5.1 FAILURE — three demonstrated defects have no proposed test, because their sites are not enumerated

Each is measured above and each survives everything v2 proposes: the rule-1 basename skip
(§1.2), rule 4's empty-body retrieval at `:229` (§1.2), and the §2 row-scan extent (§1.3). The
third is the sharpest: it is a **fail-open in a gate-invoked guard whose subject is a signed
certification**, produced by a one-line edit, with no diagnostic and no exit-code change — the same
category the v1 audit used to fail dimension 1, in the same file, one section over.

### 5.2 FAILURE — `V3-N1`'s falsification is attached to no obligation

§7's row `| git ls-files --error-unmatch fails (:198) | falsification | TRUE FALSIFICATION —
survives |` is the only place the site appears. There is a probe and there is no guarantee, no
success condition and no owning section for it to observe a repair against (F18).

### 5.3 Residual — two obligations demand falsifications where v2's own rule says there are none

§7's governing rule: *"a probe that already produces the desired behaviour at base SHA is a
CONTROL. Only a probe that passes at base SHA and must fail after repair is a falsification."*
Against that:

- **A-R1's success condition** is *"13 scripts each carry an observing falsification and a
  control"*, while its own table marks `check-review-scope.sh:47` and `check-findings-ledger.sh:22`
  fail-**closed** and seven more "to be measured". For a closed site the desired behaviour already
  occurs; ADJ4 §C6.8 shows a falsification is still constructible (it must refuse *at the `cd`*,
  not downstream at `expect`), but v2 never says so, so the requirement is satisfiable by
  relabelling.
- **A-R3** requires *"Per consumer, both directions get a falsification and a control"*, and the
  same table's `check-eval-codes.sh` row reads *"**YES — and a repair MUST NOT change its
  behaviour**"*. Both directions are already correct there; neither can be a falsification.

## 6. WHETHER EVERY MECHANICAL GUARD IS INVOKED BY THE ACTUAL GATE — **HOLD**

v1's two failures are closed. A-G1(5) requires the standing counter-example to be wired **or** given
an argued exemption (F15); A-G1(6) requires `docs/session-state.md`'s live gate-runs table to move
in the same change (F16). Verified against the tree: `scripts/test.sh:173-209` invokes nine guards
with no profile conditional; `check-suite-floors.sh`, `check-findings-ledger.sh` and
`check-review-scope.sh` are invoked by nothing; the §7.1 table at `docs/session-state.md:764-776`
says exactly that and would become false the moment A-G1(5) wires anything.

**Residuals, recorded not blocking.**
- The word *"applicable"* survives in A-G1(1). v1's §6.3 asked for its deletion because there is no
  profile conditional for it to select; keeping it leaves the requirement satisfiable by declaring
  a path inapplicable.
- A-R1 now repairs `check-findings-ledger.sh` and `check-review-scope.sh`, which are also invoked
  by nothing. A-G1(5) names only `check-suite-floors.sh`. Their exemptions exist in the repository
  (`docs/session-state.md:775-776`, the second citing D-057(4)); A-G1 should point at them so the
  rule is not read as applying to one script by accident.
- The targeted guard's **enumerated canonical facts** are still not enumerated anywhere. v1 had the
  same gap, so this is not a regression, but A-G1(4) requires the guard to state a scope it has not
  been given.

## 7. COUNT AND TERMINOLOGY CONSISTENCY WITHIN v2 — **FAIL**

All checks below were run paragraph-normalized (blank-line split, whitespace collapsed), because
the repository hard-wraps prose.

1. **"FOUR skip points" over a table of five rows and six line numbers** (§1.2), none of which is
   the basename match ADJ4 counted among its four.
2. **A NEW five-vs-six.** §5: *"**Five states** (B0 init, B1 before-reads, B2 head-moved, B3
   confirmation-pending, B4 exhaustion, B5 success)"* — five asserted, **six named, in the same
   sentence**. v1 carried the same "five states" wording but at least tabulated its six rows and
   gave a success condition scoped to *"every state B1–B4"*; v2 dropped both, so the number is now
   the only guidance an implementer has.
3. **A-R1's success condition is self-falsifying.** *"no count in this contract says five or six"*
   — while A-R6 says *"across **all six** constants"*, D-F2 says *"ten minus four is **six**"*, and
   §5 says *"**Five** states"*. The intent (the git-root class) is inferable; a success condition
   that must be inferred is the shape D-059(2) was written to prevent. Scope the sentence.
4. **§1 names `D-F3` as a co-owner of `docs/session-state.md`; §6 says D-F3 is REMOVED** (§3.3).
5. **A-R3 says "ALL consumers" and "at least seven" in the same sentence.** Those cannot both hold,
   and §1.3 shows which one gives.
6. **A recorded residual is used as an operative pointer.** §8(6) records *"four citation
   offsets"* as residuals with *"no disposition claimed"* — and D-F2 then cites *"the third copy at
   `session-state.md:152`"*, which is **one of those four offsets**. `:152` is the tail of an
   unrelated bullet about exit status; the phrase D-F2 owns is at `:162-163`. v2 also introduces a
   new offset: A-R6 cites *"`session-state.md:772`'s table row restating the single-sourcing
   claim"*; `:772` is the table's header row and the claim is at `:774`.
7. **A bare line number is used for two different files with two different findings.** `:198` is
   `check-secrets.sh:198` (`C4`) in A-R2's table and `check-review-scope.sh:198` (`V3-N1`) in §7's
   table, the latter with no file named. ADJ4 §C4.7 warned in terms: *"a coincidence of line
   numbers is not identity."*

## 8. SHARED PRIMITIVES STRETCHED ACROSS DIFFERENT GUARANTEES — **HOLD**

The splits v1 asked for were made and they are real: A-P1 → **A-R1** (root resolution) + **A-R2**
(retrieval, with its own guarantee, its own discriminator problem, and the explicit statement that
`C4`'s discriminator does not transfer to a list built from `git ls-files`); A-P2a → **A-R3**
(extent, including the widening obligation v1 asked for) + **A-R4** (uniqueness, two substrates
kept apart per D-059(8)) + **A-R5** (membership, which is the split that makes `C1` observable).
`install-hooks.sh`'s side-effect obligation is carried into A-R1's falsification rule; the C6d fork
is routed to §8 and the test author is forbidden to choose. I tried to break the A-R3 split against
the certified table hash and **could not** — see §1.3's closing note.

**Residual — A-R3's guarantee sentence does not reach its own consumer set.** It reads *"A guard
certifying a NAMED section must derive that section's extent with an ANCHOR-DEPTH-RELATIVE
terminator"*. Three of its seven rows are not that: `check-vendor-honesty.sh:269` has **no
extraction at all** (whole-document comparison; the obligation is to scope it, which the sentence
does not express); `:351`/`:365` fail by **widening under renumbering**, carried in a separate
paragraph rather than in the guarantee; and `verifier/test_verifier.py:930` is a **test, not a
guard**, so the guarantee as worded does not bind it — which is precisely the question v1's F3 fix
asked v2 to answer (*"route it through the extent rule or record why a test may use a weaker one
while a guard may not"*) and v2 answers neither way.

**Residual — A-R4(a) has no enumerated consumers.** Consumers are listed for (b) only
(`check-type-strings.sh:66`, `check-suite-floors.sh:15`). The Markdown half names none, so its
control (*"a legitimate backticked prose mention … is not a second publication"*) has no site list
to be run against.

---

## WHAT MUST CHANGE — the failures

| # | Failure | Where |
|---|---|---|
| G1 | `V3-N1` — one of the eight confirmed obligations — has **no owning section, guarantee or success condition** in v2 | Part 1 F18, §3.1 |
| G2 | D-059(2)'s ordered disposition of the `printf … \| wc -l` site is **deleted**; v2 contains no occurrence of it | Part 1 F18 |
| G3 | The root-resolution class is **fourteen** sites; `.githooks/pre-commit:4` is invisible to v2's regex and to its glob | §1.1 |
| G4 | A-R2's table omits two of ADJ4's four skip points (`:86`/`:88`, `:229`), adds three benign guards, mislabels `:195`'s mode, and says "FOUR" over six line numbers | §1.2, §7(1) |
| G5 | A-R3 drops `check-vendor-honesty.sh:297`/`:298`/`:308`; **demonstrated fail-open** — one blank line silently reduces the D-008(1) row check from 11 to 8 with no diagnostic and no exit change | §1.3 |
| G6 | F5's live false sentence (`docs/gate-s2-evidence.md:527-529`) has **no disposition**; the paragraph labelled "F5 fix" resolves a different subject | Part 1 F5 |
| G7 | The F7 pair is inside A-R6 **and** returned to John, and is unadjudicated either way | §2 |
| G8 | `docs/exit-criterion-packet.md` §3b is written by Batch A (`:105`) and Batch D (`:103` control, `:211` repair) | §3.2 |
| G9 | **v2 states ONE success condition (A-R1's) where v1 stated six**; Batches B and C additionally have no guarantee, no source statement and no matrix, and their operative text is a document v2 calls superseded, which §7 contradicts | §4 |
| G10 | Internal count/terminology contradictions: "Five states" naming six; "no count says five or six" against three of v2's own counts; `D-F3` named as a live owner; "ALL consumers"/"at least seven"; a recorded citation-offset residual used as D-F2's operative pointer; `:198` used bare for two different files | §7 |

## RESIDUALS — recorded, not blocking

`check-gate-immutability.sh:53`'s paired-sentinel extraction, undispositioned (§1.4); the word
*"applicable"* in A-G1(1), which v1 already asked to be deleted (§6); `check-findings-ledger.sh`
and `check-review-scope.sh` repaired-but-uninvoked with their exemptions un-cited in A-G1 (§6); the
targeted guard's canonical-fact list still unenumerated (§6); A-R1's and A-R3's falsification
demands at already-correct sites, against §7's own rule (§5.3); A-R3's guarantee not reaching
`:269`, the widening pair, or a test (§8); A-R4(a) with no enumerated consumers (§8);
`session-state.md:774` claimed by A-R6 and A-G1(6) with no boundary rule (§3.4);
`check-label-integrity.sh:63` and `check-vendor-honesty.sh:352`, which v2 correctly moved to §8.

**NOT REOPENED, deliberately.** Gate 5's status; the C6d fork; the `F7-R1` wording, which D-059(9)
assigns to the Batch B test author; whether the F7 claims are repaired or adjudicated (that is the
fork — what fails is that v2 asserts both answers); the eight D-058(8) obligations themselves,
which are ruled.

## WHAT THIS AUDIT ESTABLISHES AND WHAT IT DOES NOT

**Establishes.** That F13 is genuinely fixed, by probing the requirement in both directions and by
reproducing A-R5's falsification surviving at base SHA with two discriminating controls and the
2-of-41 scope note re-derived under `bash`; that A-R3's crux control and its 35 → 62 widening figure
reproduce as stated; that the root-resolution class is fourteen sites, by mechanism sweep, with the
fourteenth's fail direction measured in both failure modes; that `check-secrets.sh`'s rule-1
basename skip is defeated by one non-ASCII byte in a filename, with an ASCII control that fires at
two rules; that one blank line inside the §2 capability table silently reduces the D-008(1) row
check from 11 to 8 while the certification hash and the exit code both stay put; that `V3-N1` and
D-059(2)'s `wc -l` disposition are absent from v2, by count against v1; that F5's sentence is still
false and unaddressed; and that v2 carries one success condition where v1 carried six, by count.

**Does not establish.** Whether any newly-enumerated site is reachable in practice — I measured
mechanism and fail direction, not likelihood. Whether Batch B's and Batch C's mutants still behave
as v2 reports: the submodule directories are empty in this worktree, `forge build` cannot run, and
the TypeScript suite loads Foundry artifacts that do not exist, so I ran only the single test file
that binds `EVAL_CODES`. I did not run `scripts/test.sh`, the verifier suite, the deep profile or
the corpus. I did not re-audit the eight D-058(8) obligations for whether they are real — they are
ruled. I did not read the reviewer reports before probing; I read v2, `ENUMERATION.md`, the v1
audit, the four adjudications and D-058/D-059, and started from the tree rather than from anyone's
account of it.

**The one line I would keep if only one survived:** v2 fixed the failures it could see and repeated
the failure that produced them — its enumerations are still spelling-shaped commands over the
directory somebody already reported, which is how the pre-commit hook, two secret-scan skip points
and three capability-table extractions stayed invisible — and in restructuring it lost `V3-N1`, the
confirmed finding this batch was named after.
