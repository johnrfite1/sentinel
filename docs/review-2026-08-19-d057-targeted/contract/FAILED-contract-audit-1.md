> # AUDIT OF A FAILED, SUPERSEDED CONTRACT — preserved as evidence
> The contract this audits is **not operative** (D-060(1)). The audit's FINDINGS remain
> factually valid about the tree and several are carried into the batch cards; the
> CONTRACT it audits is abandoned. **Do not implement from the contract.**

---

# CONTRACT AUDIT — the independent pre-precommitment audit required by D-059(10)

**Authority:** D-059(10) — *"An independent contract audit before precommitment, and it is not an
implementation attempt. One auditor, no implementation, no edits outside its evidence directory."*
**A FAIL buys ONE contract revision and a repeat audit, and does NOT consume a batch
implementation attempt.**

**Auditor:** independent. I did not draft `REPAIR-CONTRACT.md` or `ENUMERATION.md`, did not report
any finding under adjudication, did not author any adjudication, and wrote none of the code, prose
or guards under examination. I attacked the contract; I did not defend it.

**Frozen commit:** `a18e6e61598a996d962798ad0353a166232d4490`, confirmed by `git rev-parse HEAD`
in my worktree before the first probe and again after the last.

**Worktree restored.** `git diff HEAD --stat` empty; `git status --porcelain` shows only the
pre-existing untracked `ts/node_modules`. After restoration `check-type-strings.sh` (`6/6`),
`check-eval-codes.sh` (`41/41`), `check-suite-floors.sh` (all six floors), `check-vendor-honesty.sh`
(mechanical conditions pass), `check-secrets.sh` (clean) and `check-class-coverage.sh` (pass on the
ratchet) each re-run green. Nothing was repaired, signed, certified, ratified or reaffirmed.
Nothing was committed or pushed. No file outside this evidence directory was left changed.

**Instrument hygiene.** Every sweep used `/usr/bin/grep`. Every shell loop over a word-split list
was run under `/bin/bash`, not the session shell — **this trap fired on me live**: `zsh` does not
word-split an unquoted variable, so my first per-code occurrence count over §5.7.1 iterated ONCE
over the whole blob and reported "all 41 codes appear twice". Re-run under `bash` the true answer
is "each of the 41 appears exactly once". A zero, a one and a forty-one from the wrong shell all
read like measurements. Both readings are recorded rather than the convenient one. Probes that
edit a document assert on the line they expect before the guard is run.

**Standing evidence.** I ran `forge test` (92 tests, 0 failures) and the TypeScript suite
(527/527) at base SHA and under four mutations. I did not run `scripts/test.sh` end to end, the
verifier suite, or the deep profile.

---

## VERDICT: **FAIL**

| # | Dimension | Verdict |
|---|---|---|
| 1 | Sibling-list completeness | **FAIL** |
| 2 | Unadjudicated items entering scope | **HOLD** (one residual) |
| 3 | Duplicate ownership across batches | **FAIL** |
| 4 | Historical material treated as live (and the converse) | **FAIL** |
| 5 | Whether every proposed test observes its named defect | **FAIL** |
| 6 | Whether every mechanical guard is invoked by the actual gate | **FAIL** |
| 7 | Count and terminology consistency within the contract | **FAIL** |
| 8 | Shared primitives stretched across different guarantees | **FAIL** |

**The contract is strong where it was attacked before and weak in the same direction each time it
was not.** Its citations are accurate to the line almost everywhere (§7 below lists what I checked
and found right). Its Batch B and Batch C falsifications are live and I reproduced both with their
discriminating controls. What fails is the sweep: **every enumeration in the contract was run with
a command shaped like the site somebody already reported**, so each one stops exactly where the
reported instance stopped. That is the project's own recorded defect, committed inside the document
written to prevent it.

---

## 1. SIBLING-LIST COMPLETENESS — **FAIL**

### 1.1 FAILURE — the git-root class is **thirteen of fifteen scripts**, not five

`ENUMERATION.md` derives A-P1's site list with `/usr/bin/grep -nE 'cd "\$\(' scripts/*.sh
verifier/*.py`. That command can only see the ONE-STEP spelling. Eight further scripts use the
TWO-STEP spelling and are invisible to it:

```
/usr/bin/grep -nE 'ROOT="\$\(git rev-parse --show-toplevel\)"' scripts/*.sh
  scripts/check-class-coverage.sh:48      -> cd "$ROOT"          (:49)
  scripts/check-eval-codes.sh:21          -> "$ROOT/…"           (:22, :37)
  scripts/check-gate-immutability.sh:43   -> "$ROOT/scripts/test.sh"
  scripts/check-label-integrity.sh:32     -> "$ROOT/fixtures/…"
  scripts/check-label-prompt.sh:18        -> "$ROOT/fixtures/…"
  scripts/check-type-strings.sh:18        -> "$ROOT/…"           (:19, :43)
  scripts/check-vendor-honesty.sh:32      -> cd "$ROOT"          (:33)
  scripts/mutate.sh:33                    -> "$ROOT/…", cd "$ROOT" (:41)
```

The contract's **"THE ARITHMETIC, STATED SO IT CANNOT DRIFT (D-059(2)): FIVE distinct scripts carry
the defective git-root pattern"** is false for the guarantee A-P1 actually states. `cd "$ROOT"`
where `ROOT=""` is byte-for-byte the same silent no-op as `cd "$(…)"`; the contract's own probe
(`cd ""` returns 0 and does not abort under `set -euo pipefail`) applies unchanged.

**And one of the eight fails OPEN, is invoked by the gate, and is the Gate 5 evidence instrument.**

`scripts/check-vendor-honesty.sh` is run at `scripts/test.sh:209`. Probe: a decoy directory
containing only a copy of the proposal and `docs/ablation-report.md`, `git init`-ed, with a `PATH`
shim failing only `git rev-parse --show-toplevel` (the natural condition — standing outside any
work tree — reproduces it without a shim). The guard was invoked by absolute path from the
project worktree:

```
fatal: not a git repository (shim)
vendor honesty (§7.5 Gate 5, D-008) — mechanical conditions
  ok    no artifact claims an … vendor comparison (D-001, D-008(2))
  ok    no named vendor appears in any measurement artifact (D-008(4))
  ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it
  ok    §2 capability table: 11 of 11 rows carry a marker resolving to a §13 entry
  ok    §2 capability table: inference marking (D-008(3)) certified by record
vendor honesty: mechanical conditions pass; D-008(1) met and (3) certified by record
EXIT=0
```

A complete Gate 5 certification, exit 0, measured against a **two-file tree that contains no
measurement artifacts at all** — so conditions (2) and (4) passed vacuously.

**Proof it read the decoy and not the project (the discriminator, not an inference):** delete one
capability-table row from the DECOY's proposal only and re-run.

| Run | cwd | Output | Exit |
|---|---|---|---|
| A | decoy, one row removed | `10 of 10 rows` … `FAIL §2 capability table: the certification is STALE` … `MECHANICAL CONDITIONS FAILED` | **1** |
| B — CONTROL, same shim | project worktree root | `11 of 11 rows` … certified by record | **0** |

The count moved with the decoy. This is `C6b` (`check-suite-floors.sh:13`) in a gate-invoked guard
whose subject is a signed certification, and it is not in the contract.

**`scripts/check-class-coverage.sh:48-49`** is the same shape (also gate-invoked, `:203`). Measured
from the same decoy it fails CLOSED (exit 1, `corpus class coverage: FAILED`) — but only because
the decoy lacked `ts/`; a complete second checkout would pass it about the wrong tree. The five
`"$ROOT/…"`-prefix guards fail CLOSED and loudly, each with a refusal naming the section
(measured: `type strings: COULD NOT ISOLATE §5.8`, `eval codes: COULD NOT ISOLATE §5.7.1`,
`gate immutability: COULD NOT EXTRACT the bootstrap`, `label prompt: MISSING`, `label integrity:
MISSING`, all exit 1).

**Fix.** Enumerate the class by the guarantee, not by the spelling: sweep
`git rev-parse --show-toplevel` in any substitution. Route all thirteen through A-P1 or record an
argued exemption for each. Add a fail-OPEN falsification for `check-vendor-honesty.sh` and
`check-class-coverage.sh`, and note that `check-vendor-honesty.sh` is already a Batch A file
(A-P2a) — a repairer implementing the contract exactly would fix its `:269` and leave its `:32-33`
fail-open standing, with the contract's success condition met.

### 1.2 FAILURE — `check-secrets.sh` has four skip points; the contract names one, and it is in the mode the gate does not run

ADJ4 §C4.6 established that `:198` is "one of four skip points sharing a single root cause (path
quoting)". Verified:

```
scripts/check-secrets.sh:86,:88   basename case match (rule 1, secret-bearing filenames)
scripts/check-secrets.sh:198      git show ":$f" … || continue     (STAGED mode, rules 3/3b)
scripts/check-secrets.sh:201      [ -f "$f" ] || continue          (DEFAULT mode, rules 3/3b)
scripts/check-secrets.sh:229,:231 git show / [ -f ] pair           (rule 4)
```

The single-ownership table and A-P1's table name **`scripts/check-secrets.sh:198` only**, and
falsification #6 reads *"`check-secrets.sh --staged` must REFUSE"*. **`scripts/test.sh:176` invokes
`./scripts/check-secrets.sh` with no flag — the DEFAULT mode**, whose skip point is `:201` and
whose file list is built at `:80-82` from `git ls-files` plus `git ls-files --others
--exclude-standard`, not from `git diff --cached`.

Probe, in a scratch repository outside the project, two files with byte-identical content carrying
one planted 64-hex value, differing only by one byte in the filename:

```
git ls-files
  ts/src/zzprobe-ascii.ts
  "ts/src/zzprobe-caf\303\251.ts"          <- quoted token

DEFAULT mode, both present:      BLOCKED ts/src/zzprobe-ascii.ts — credential-shaped content
                                 secret guard: 1 finding(s)
DEFAULT mode, only the non-ASCII: secret guard: clean
                                 (the key is retrievable from that file)
```

The ASCII control behaves oppositely, so the instrument is live. **The gate's own invocation mode
fails open and the contract does not enumerate the site or falsify the mode.**

This also breaks the repair ADJ4 prescribed: `git diff --cached --raw -z` fixes the STAGED list
only. The default list needs `git ls-files -z`, and the "status `D` ⇒ legitimate skip" argument —
which is what makes John's D-059(3) discrimination requirement satisfiable — **does not exist for
`git ls-files`**, which has no status letters. The contract states the discriminator as though one
answer covers both modes. It does not.

### 1.3 FAILURE — a third §5.8 section-extraction consumer, outside `scripts/`, owned by nobody

`ENUMERATION.md`'s A-P2 sweep is `/usr/bin/grep -nE 'head -1|head -n *1' scripts/*.sh`. It cannot
reach `verifier/` or `ts/`. There is a live one in `verifier/`:

```
verifier/test_verifier.py:927-930
    spec = os.path.join(REPO, "Sentinel_Protocol_Lab_Proposal_v0_2.md")
    block = text.split("### 5.8 EIP-712 Type Strings")[1].split("---")[0]
```

It builds a dict keyed by struct name, so a duplicate publication inside §5.8 is resolved
**LAST-wins, silently**, where `check-type-strings.sh:65`'s `head -1` resolves it **FIRST-wins**.
Two live instruments over the same section, with opposite silent tie-breaks, neither refusing, and
a third extent rule (terminate at the first `---`, not at a heading of any depth). Its
`test_all_six_are_published` asserts `len(dict) == 6`, which a duplicate cannot move.

`ts/test/rulings.test.ts:350` also reads the proposal, but by whole-file regex with no section
claim — not a member of the class.

**Fix.** Enumerate section-extraction consumers by what they DO, across `scripts/`, `verifier/` and
`ts/`, not by `head -1` in `scripts/*.sh`. Give this site a disposition: either route it through
the A-P2a extent rule or record why a test may use a weaker one while a guard may not.

### 1.4 FAILURE — four more section extractions inside a file Batch A already owns

A-P2a's consumer table lists `check-vendor-honesty.sh:269` and `:352`. The file has four more:

```
scripts/check-vendor-honesty.sh:297,:298,:308   §2 capability-table row scans
scripts/check-vendor-honesty.sh:306             §13 extent: /^## 13\./ … /^## 14\./{exit}
scripts/check-vendor-honesty.sh:351             §2 extent: /^## 2\. …/ … /^## 3\./{exit}   <- feeds :352
scripts/check-vendor-honesty.sh:365             §2 extent again -> the CERTIFIED table SHA
```

`:351` and `:365` use a **literal next-heading terminator**, which is depth-aware in neither
direction. It cannot be truncated by a deeper subheading (good) but it **widens without limit if
`## 3.` is renumbered or demoted** — the same widening `C1` demonstrated for `check-eval-codes.sh`,
and `:352`'s `head -1` and `:365`'s certified-table hash are both computed over that extent. A-P2a
declares the depth-aware rule and then leaves the two extractions that carry the D-008(3)
certification unenumerated.

### 1.5 FAILURE — a false claim sitting BETWEEN the two D-F2 sites the contract does enumerate

D-F2 enumerates the derivation and the `l.548` sentence. Both are in `docs/gate-s2-evidence.md`
§11.0. Between them:

```
docs/gate-s2-evidence.md:527-529
  **The two citations it names are corrected in the same checkpoint**
  (`docs/exit-criterion-packet.md` §3, `docs/session-state.md`). Corrected 2026-08-19 (A-080).
```

`docs/exit-criterion-packet.md:95` was corrected (it reads struck-*Ten* then **SIX**).
`docs/session-state.md:162-163` was **not** — it still reads *"ten accepted as documented limits"*,
which is the very site D-F2 lists as its "third uncorrected copy". So the sentence asserting the
sweep is complete is false, and it is three lines from a site the contract enumerates. This is
`R2-F4`'s shape exactly: corrected §3b and left §7 of the same file.

### 1.6 FAILURE — the single-sourcing universal claim is restated outside §3, unowned

`docs/session-state.md:774`, inside §7.1 (`:757-779`), not §3 (`:352-491`):

```
| `check-suite-floors.sh` | prints the floors read from `scripts/test.sh`, the only copy | … |
```

A-F1 owns "`session-state.md` §3 passages". `:361` and `:379` are in §3 and are covered. `:774` is
not, and no batch owns it. **ADJ3 §3.4 named this exact line** and it did not reach the contract's
inventory. `C3` proves the claim is unverified by its own instrument; leaving one copy of it
outside every batch reproduces `R4-F4`'s history precisely.

### 1.7 FAILURE — two live surfaces state that the floors Batch A owns do not exist

Neither is in A-F1's "Reader-facing occurrences" table and neither carries a disposition:

- `docs/v1-1-register.md:911-916` — **"NO GATE FLOOR EXISTS ON THE FOUNDRY OR TYPESCRIPT SUITE
  COUNTS"** … *"neither count is read, compared or asserted"* … *"Not fixed here"*. Unstruck,
  present tense.
- `docs/exit-criterion-packet.md:105` — the §3b **UNRESOLVED** table: *"No gate floor on
  Foundry/TypeScript counts | round 6 `L8-14`; a shrinking suite is invisible to the gate"*.
  Unstruck.

Both are false at this commit: `scripts/test.sh:234-235` define `FOUNDRY_MIN_TESTS=92` and
`TS_MIN_TESTS=527`, and `docs/session-state.md:368-370` says so in bold. The packet row sits in the
same table whose FIRST row the contract nominates as one of D-F1's three controls.

Whether these are repaired is a scope question — they are a false claim about the EXISTENCE of a
floor, not a duplicated value, so `R4-F4` does not obviously reach them and D-058(7) says a new
item is adjudicated before it enters a batch. **Leaving them out of the enumeration is not a scope
question.** D-059(2) already ruled the analogous case: *"Do not leave it in the inventory without
disposition."*

### 1.8 Residual — one member of the `|| continue` class with no disposition

`ENUMERATION.md`'s Batch A sweep `\|\| *(continue|true|:)\b` finds
`scripts/check-label-integrity.sh:63` (`[ -e "$f" ] || continue`). It is the standard
glob-no-match idiom and is benign. It should still carry the one-line argued exemption the `wc -l`
site was given, or the claim that the class was enumerated is weaker than it reads.

---

## 2. UNADJUDICATED ITEMS ENTERING SCOPE — **HOLD**

I traced every item that enters a batch to an independent classification: the six in
`ADJUDICATED-NEW-FINDINGS.md`; `C1`, `C2`, `C3` in `ADJ3.md`; `C4`, `C5`, `C6a`–`C6d` and the
`test.sh:60` exemption in `ADJ4.md`. **I found nothing in a batch that has not been independently
classified**, and the contract is scrupulous about labelling each row with its adjudication and its
severity movement. This dimension holds.

**One residual.** `scripts/check-vendor-honesty.sh:352` enters A-P2a's consumer table carrying
*"already section-scoped — verify duplicate behaviour"*. That is an instruction to measure, not a
classification, so the row is in a batch on the strength of the enumeration that surfaced it —
which is the shape D-059(4) forbids. Either measure it and classify it, or state it as an
enumerated-not-adjudicated row that enters no obligation.

**And see §3.3:** the converse failure is real — `C5` is adjudicated CONFIRMED and enters **no**
batch at all.

---

## 3. DUPLICATE OWNERSHIP ACROSS BATCHES — **FAIL**

No item is implemented twice; the dependency markings (`D-F3` removed, `D-F5` as claim-side use,
`D` as control on A-F1) are correct and are what D-059(5) asked for. The table nevertheless fails,
because it is **incomplete in three places, and one of them is a file two batches write.**

### 3.1 FAILURE — `docs/session-state.md` is written by A and by D; the table lists only A

- Batch A (A-F1) owns "§3 passages" — measured, §3 is `:352-491`, so `:365` and `:470` are in it.
- Batch D (D-F2) is told to correct the "third uncorrected copy" — measured, that is `:162-163`,
  inside §0 (`:94-213`).

`docs/session-state.md` therefore has two owning batches. The table's row reads
`**All six floor constants; every live floor occurrence; session-state.md §3 passages; …** | A
(A-F1)` and there is no Batch D row for the file. D-059(5) is written per file *and* per factual
repair, and D-058(1) forbids two writers against one worktree. A repairer reading the table
concludes Batch D touches no part of this file. **Add an explicit `docs/session-state.md` §0
(~`:162`) row under D, or move the fact to A.**

### 3.2 FAILURE — `check-suite-floors.sh`'s row hides one of its two independent defects

The table reads `scripts/check-suite-floors.sh | **A** (A-P2b + A-F1)`. A-P1's own sibling table
enumerates `scripts/check-suite-floors.sh:13`, and falsification #4 covers it. ADJ4 §C6.4 states
the point directly: *"Two independent routes to the same false sentence. They need separate
observing tests."* The ownership row names one route. Make it `A-P1 + A-P2b + A-F1`.

### 3.3 FAILURE — `C5` is CONFIRMED and has no owner

The contract mentions it once, in Batch C's *"Outside the evidence"*: *"`protocol.ts:115` and
A-077's 'the detail now distinguishes them' are unsupported. **That is a Batch D claim item, not a
Batch C code change**, unless adjudication rules otherwise."* Adjudication has ruled — ADJ4 §C5.6:
Claim A true, **Claim B false**, CONFIRMED, LOW, with the minimum repair named (*"strike the two
false sentences rather than build a field"*) and demonstrated by a probe showing the two conditions
produce byte-identical signed refusals with a control that moves both the reason code and the
`reasonCodesHash`.

It appears in no `D-F` item and in no ownership row. The `docs/decisions.md` A-077(2) half is
historical under D-058(8)D and is not rewritten; **the live half, `ts/src/signer/protocol.ts:115`,
is a source comment in the wire contract and needs an owner or an explicit, recorded deferral.**

---

## 4. HISTORICAL MATERIAL TREATED AS LIVE — **FAIL**

**No dated `docs/decisions.md` entry is scheduled for edit anywhere in the contract.** I checked
each: `:223` is D-052 and `:225` is A-070, exactly as cited, both classed HISTORICAL, and D-F1's
re-enumeration under D-059(6) correctly arrives at ONE live site rather than forcing the answer to
remain two. That part is right.

### 4.1 FAILURE — Batch D schedules two edits inside a file the contract elsewhere declares off-limits

The GATE 5 section rules: *"The phrase 'extracted from §7.2 itself' is a false statement about an
enforcement mechanism, inside `docs/gate-s2-evidence.md` — **a SIGNED pack** … It is prepared as
OFFERED / NOT-CERTIFIED and returned to John. **It is not in Batch A, B, C or D.**"*

D-F2's two repair sites are `docs/gate-s2-evidence.md:513` and `:548` — the same file — and D-F2
names neither the file nor a signature status. `l.548` is cited with no file at all.

**As it happens the edits are permissible, and the contract does not say so.** §11.0 opens with an
explicit carve-out at `:494-505`:

> *"Gate S2 was signed by John on 2026-08-16 (D-041). Everything in this §11.0 subsection post-dates
> that signature … John's signature of 2026-08-16 does NOT cover it. … This text is authorised at
> D-057; it is not retrospectively signed by anything."*

And the protected phrase is at `:284`, well outside that carve-out. So the contract is
substantively right and procedurally silent, and a repairer implementing it faces a direct
contradiction between two of its own sections: it either edits a file the contract calls a signed
pack, or it stops. **Fix: name the file, cite the `:494-505` carve-out as the authority for
touching §11.0, and state that `:284` is the only signed-text site and stays OFFERED-only.**

### 4.2 FAILURE — the converse: D-F2's "third uncorrected copy" is material the source deliberately preserved, and the contract does not say which side it falls on

The site is `docs/session-state.md:162-163`, *"ten accepted as documented limits"*. The
authoritative document records a decision to keep exactly that quotation alive:

> `docs/gate-s2-evidence.md:519-521` — *"The heading keeps its original number and this correction
> sits beside it rather than replacing it, because 'ten accepted limits' is quoted in
> `docs/exit-criterion-packet.md` §3 and in `docs/session-state.md`, and silently restating it as
> six would leave those citations pointing at a number that no longer appears anywhere."*

D-F2's own control says *"legitimately historical statements of 'ten' must remain intact and
unflagged."* The contract lists this site as a defect to correct and offers no way to tell it from
its own control. The packet's §3 shows the intended treatment — annotate in place, `~~Ten~~ **SIX**`
— and the contract should say so rather than leaving "third uncorrected copy" to be read as
"replace the number".

### 4.3 Residual — the `verifier/REPORT.md` historical classification, stated precisely

The contract classifies it HISTORICAL because *"each figure carries its own 'Results after X
(date)'"*. Verified: true of every figure line (`:1173`, `:1176`, `:1182`, `:1186`, `:1197`,
`:1212`). Two narrative sentences inside those dated blocks restate counts without their own date
(`~:1203`, `~:1221` — *"The 101 tests from the previous round all still pass"*). They are anchored
by the block they sit in. Recorded so the classification is not later read as unqualified.

---

## 5. WHETHER EVERY PROPOSED TEST OBSERVES ITS NAMED DEFECT — **FAIL**

### 5.1 Verified SOUND — I ran these

| Falsification | Measured at base SHA | Verdict |
|---|---|---|
| **B-1** `emit ActionExecuted(…, (viaOverride && false))` | compiles under `deny = "warnings"`; **92 tests passed, 0 failed — SURVIVES** | observes its defect |
| **B-2** `(viaOverride \|\| true)` — the asymmetry control | **91 passed, 1 failed — caught** | control discriminates |
| **C** restore `pendingOnly = false` at `ts/src/signer/vault.ts:228` (B3) | **527/527 — SURVIVES** | observes its defect |
| **C** the same mutation at `:182` (B1) — the control | **526/527 — caught** | control discriminates, B3 probe is live |
| **A-P1 #3** shim only `git ls-files --error-unmatch` to fail | `assigned 463 of 463 tracked files`, `0 file(s) changed since A-070's parent, all assigned`, exit 0 — **SURVIVES** | observes `V3-N1` |

Batch B's and Batch C's cores are real and their controls discriminate. Batch C's branch matrix is
accurate to the line (`:173`, `:179/:182`, `:223/:228`, `:230/:232`, `:236`, `:256`). Batch B's
enumeration is exact: eight declared events, eight emit sites at `:189/:195/:200/:205/:211/:216/
:277/:381`, `_consumeAndCall` reached at `:238` (`false`) and `:281` (`true`).

### 5.2 FAILURE — A-P2a's falsification set observes NOTHING at `check-eval-codes.sh`, and one item demands the wrong answer

The single-ownership table assigns `scripts/check-eval-codes.sh` to **A (A-P2a)**. A-P2a's
falsification list is *"for EVERY consumer — (a) plant a duplicate publication inside the named
section, in both orders; (b) plant the value outside the named section only; (c) truncate the
section with a deeper subheading; (d) make the section absent entirely"*, and its success condition
is *"each falsification produces a refusal naming the section and the reason"*. Measured, all four,
at base SHA:

| Item | Edit | Result | Observes a defect? |
|---|---|---|---|
| (a) | duplicate a code's row inside §5.7.1 | `eval codes: 41/41 … (D-031)` **exit 0** | **No** — a presence test is indifferent to duplication |
| (b) | remove the code from §5.7.1, describe it under `## 6.` | exit **1**, names the code | **No** — already correct |
| (c) | insert `##### 5.7.1.1` inside §5.7.1 | `41/41` **exit 0** | **No — and this is the RIGHT answer.** The anchor is `#### 5.7.1`, depth 4; a `#####` child belongs inside. A-P2a's success condition would force the repaired guard to REFUSE a legitimate subsection |
| (d) | rename the anchor heading | exit **1**, *"COULD NOT ISOLATE §5.7.1"* | **No** — already correct (`:32`'s `[ ! -s ]`) |

**Meanwhile the defect the contract's own table describes for this consumer survives all four.**
`C1`, reproduced: rename `EVAL_SIM_STOP_IMPERSONATION_FAILED` to `…_FAILE` (one character dropped)
across `ts/src/evaluate/checks.ts` and `ts/test/evaluate.checks.test.ts`, spec untouched —

```
occurrences of the truncated name in the proposal: 0
scripts/check-eval-codes.sh     -> eval codes: 41/41 engine checks documented in §5.7.1   EXIT=0
scripts/check-class-coverage.sh -> corpus class coverage: pass on the ratchet             EXIT=0
CONTROL, non-prefix rename …_FAILEX -> EXIT=1, names the code
```

**An implementer who satisfies A-P2a exactly — a shared depth-aware extraction primitive plus
duplicate refusal — leaves `C1` fully live, prints `41/41`, and meets the contract's stated success
condition.** This is the single failure mode D-058 exists to close, present in the contract written
to close it.

ADJ3 §1.7 says so in terms: *"A presence test makes no choice among candidates … Adding duplicate
refusal to this guard would not touch C1"*, and §1.10 gives the remedy: *"an anchored membership
test"*. That remedy appears nowhere in A-P2a's guarantee, falsifications or success condition.

**And the widening direction is named in the table with no falsification and no remedy.** Measured:
demoting the `## 6. AI and Context Scope` heading to bold prose extends §5.7.1's awk extent from
**35 to 62 lines** and the guard still prints `41/41`, exit 0. **A depth-aware terminator does not
close this** — after the demotion there is no heading of any depth left to terminate at. A-P2a's
stated guarantee is insufficient for a defect its own table lists.

**Fix.** Split A-P2a (see §8.2) and give the membership-anchoring property its own falsification (a
strict-prefix truncating rename) and its own control (a non-prefix rename, which is caught today).
Give the widening direction a separate obligation — pinning the expected terminator, or a
section-extent ratchet — because extent-narrowing and extent-widening have different remedies.

### 5.3 FAILURE — two of A-P1's six numbered falsifications cannot fail before the fix

The list is headed *"Pre-repair falsification (must be shown to fail before the fix)"* and the
success condition reads *"all SIX numbered falsifications refuse"*. Items 1 and 2 target
`scripts/check-review-scope.sh:106`, which is **already guarded at `:108` and `:114`** — the
contract's own table says so on the row above. Measured with `PATH` shims:

```
#1  bare `git ls-files` exits non-zero
    ->  FAIL  git ls-files failed: … Refusing to report a partition measured against nothing.
#2  bare `git ls-files` returns empty, exit 0
    ->  FAIL  git ls-files returned NO tracked files. …
```

Both already refuse. They are **paired controls**, not falsifications, and D-058(1) requires the
independent test author to *demonstrate each observes the pre-repair defect* — a demonstration that
does not exist to be made for these two.

The same mislabelling reaches two more places. **Falsification #4** (*"run each … from a
non-repository directory → must REFUSE"*) already passes for `check-findings-ledger.sh` (ADJ4:
exit 1) and for `test.sh` (ADJ4: exit 5, `GATE DID NOT REACH COMPLETION`). **Batch B item 3** (*"for
each of the other seven events … Each must fail a named test"*) already passes for the six events
`R3-F7`'s repair pinned.

**Fix.** Do for these lists what A-P2a and A-F1 already do elsewhere: separate FALSIFICATIONS
(observe a live defect at base SHA) from CONTROLS (must keep passing). The counts in the success
conditions must then be stated over the falsification half only.

### 5.4 FAILURE — falsification #6 exercises the mode the gate does not run

See §1.2. It must be run in BOTH modes, and the default mode needs a different discriminator
argument from the staged one.

### 5.5 For completeness — A-P2a at `check-type-strings.sh` behaves the same way

Measured, so the pattern is not an artefact of one consumer: (a) duplicate inside §5.8 with no
subheading → **exit 1** (the D-057(5) duplicate refusal, already correct — a control); (c) the same
duplicate under `#### 5.8.1` → **`6/6` exit 0, SURVIVES** (`C2`). So each consumer has at most ONE
live falsification among the four, in a different position, and `check-eval-codes.sh` has none.

---

## 6. WHETHER EVERY MECHANICAL GUARD IS INVOKED BY THE ACTUAL GATE — **FAIL**

Verified: `scripts/test.sh:173-209` invokes nine guards — `check-gate-immutability`,
`check-secrets`, `check-rename-gate`, `check-label-prompt`, `check-label-integrity`,
`check-type-strings`, `check-eval-codes`, `check-class-coverage`, `check-vendor-honesty` —
with **no profile conditional**, so both profiles run all nine. `check-suite-floors.sh`,
`check-findings-ledger.sh` and `check-review-scope.sh` are invoked by nothing.

### 6.1 FAILURE — A-G1 names the standing instance of the defect and does not require it closed

A-G1 opens: *"'A standalone script that nothing invokes repeats the defect this work is trying to
close.' `check-suite-floors.sh` is that defect today."* Its four numbered requirements then bind
only *"the targeted mechanical guard"* Batch A creates. **After Batch A, `check-suite-floors.sh`
will have been repaired twice — A-P1 at `:13`, A-P2b at `:15` — and will still be invoked by
nothing.** The contract diagnoses the condition and leaves it standing.

This is not a matter an implementer may settle, and that is exactly why the contract must speak to
it: `docs/session-state.md:774` records a REASON it is out of the gate (*"it is a reporting aid;
the floors themselves are asserted by the gate"*), and `:776` records **D-057(4)** — John's explicit
ruling that the permanent product gate must not depend on a spent review's scope — as the reason
`check-review-scope.sh` is out. **Either require the wiring, or record the argued exemption and
strike "is that defect today" as the operative characterisation.**

### 6.2 FAILURE — A-G1 requires no update to the live claim its own work falsifies

`docs/session-state.md` §7.1 (`:757-779`) is a maintained reader-facing table headed *"The
checkers, and which of them the gate actually runs (added 2026-08-19)"*, listing the nine by name
under *"Run by the gate (`scripts/test.sh`, both profiles)"* and three under *"Run by hand only —
NOTHING invokes them"*. **Wiring a tenth guard makes that table false.** §7.1 is outside §3, so
A-F1 does not own it and no batch does.

The section's own header says the defect it was written to correct was *"a claim about an
instrument, stronger than the check behind it — committed in the section that lists the
instruments."* Batch A would recommit it.

### 6.3 Residual — "applicable" is a discretion the contract does not otherwise grant

A-G1(1) reads *"Invoked by the **applicable** fast AND deep gate paths"*. There is no profile
conditional in the guard block for "applicable" to select. Delete the word, or the requirement is
satisfiable by asserting the fast path is not applicable — which is the shape of loophole the rest
of this contract is careful to close.

### 6.4 Residual — an unrecorded dependency between A-P1 and the immutability guard

`scripts/test.sh:60` sits **inside** the `# >>> GATE BOOTSTRAP` block (`:14-159`, extracted at
`scripts/check-gate-immutability.sh:53`); `scripts/test.sh:161` sits just outside it. So the `C6d`
fork's option (B) is implementable at `:161` without disturbing guarded text, and any repair that
reached `:60` would alter it. Worth recording so an implementer does not discover it by failing the
gate it is repairing.

---

## 7. COUNT AND TERMINOLOGY CONSISTENCY WITHIN THE CONTRACT — **FAIL**

### 7.1 FAILURE — the corrected arithmetic is contradicted three paragraphs below itself

> *"**THE ARITHMETIC, STATED SO IT CANNOT DRIFT (D-059(2)): FIVE distinct scripts carry the
> defective git-root pattern** … **Five defective scripts, six textual occurrences — different
> counts, used separately throughout this contract.**"*

and then, in the same subsection:

> *"4. Run **each of the six** `cd`-bearing scripts from a non-repository directory → must
> REFUSE."*

There are **five** such scripts; `scripts/test.sh` holds two of the six occurrences, one of which
is the exempted bootstrap that is not a `cd`-bearing site at all. A new arithmetic error, in the
passage written to prevent one, in the sentence that carries the obligation. (And per §1.1 both
numbers are wrong for the guarantee A-P1 states: the class is thirteen scripts.)

### 7.2 Residual — four citations that point a repairer at the wrong text

| Contract says | Measured |
|---|---|
| `180` at `scripts/test.sh:980-981` | the figure is at `:981-982` |
| `docs/session-state.md` (~`l.152`) | the phrase is at `:162-163`; `:152` is an unrelated bullet about dead probes |
| `contracts/src/SentinelVault.sol:275-276` | the sentence spans `:273-275` |
| D-F2's *"l.548"* | no file named; it is `docs/gate-s2-evidence.md:548` |

### 7.3 What I checked and found CORRECT, so the revision stays targeted

The six floor constants and their values (`scripts/test.sh:234`, `:235`, `:658`, `:659`, `:660`,
`:673` = 92 / 527 / 209 / 7 / 78 / 30, confirmed against `check-suite-floors.sh`'s own output);
`docs/decisions.md:223` = D-052 and `:225` = A-070; `docs/v1-1-register.md:877` = §13.7's heading,
`:773` = the `D-09` row that carries the both-sets fact, `:176` states only the true half;
`docs/exit-criterion-packet.md:101` (the struck §3b row) and `:211` (§7 BLOCKER 1); the
`round-six-brief.md:26` control heading *"Baseline at the time of writing — VERIFY IT YOURSELF
BEFORE RELYING ON IT"* above the `:28` figure; `docs/session-state.md:360`'s *"The figures are no
longer duplicated here"* five lines above the `:365` live figures, and the stale `:470` line
(`7` right, `77`/`29`/`160` stale against 78/30/209 — three of four, as stated); the COVERAGE
heredoc bounds `:839-1190` with `92`, `527` and `209` absent from it and `160/7/77/29` at `:984`;
`scripts/test.sh:797` as the printing site; twelve `check-*.sh` scripts and exactly twelve scripts
using `set -uo pipefail` against three using `set -e`; the scope checker's `:47`, `:106`, `:131`,
`:161`, `:168`, `:198`; `check-suite-floors.sh:13`, `:15`, `:24`; `check-type-strings.sh:36`,
`:65`, `:66`; `check-vendor-honesty.sh:269`, `:352`; `ts/test/evaluate.checks.test.ts:502`;
`ts/src/decode/index.ts:190-195`; `verifier/verify.py:1434` reached from `:911` and `:1629`; and
`ENUMERATION.md`'s Batch A, B and C commands, which reproduce as written. Every code in `EVAL_CODES`
occurs exactly once inside the 35-line §5.7.1 extract (41 of 41), so A-P2a's item (a) is at least
coherent for that consumer even though it observes nothing.

---

## 8. SHARED PRIMITIVES STRETCHED ACROSS DIFFERENT GUARANTEES — **FAIL**

### 8.1 FAILURE — A-P1 spans three root causes with three different repairs and one stated guarantee

A-P1's guarantee is *"A guard must never convert a failed or empty result from an external command
into a statement about what it measured."* Its consumers do not share it:

1. **An empty or failed command SUBSTITUTION feeding `cd`** — the git-root sites. Repair: refuse
   when the substitution is empty or the command failed. **This is the primitive**, and it genuinely
   covers all thirteen sites once they are enumerated.
2. **A swallowed EXIT STATUS** — `check-review-scope.sh:198`'s `|| continue`. Repair: stop reading a
   nonzero status as a classification. Adjacent; the same helper can express it.
3. **`check-secrets.sh` — not a failed command at all.** `git diff --cached --name-only` and
   `git ls-files` **succeed**; they emit a `core.quotePath` C-quoted token that `git show ":$f"`
   cannot resolve. ADJ4's own conclusion is that the discriminator *"must come from the file-list
   construction (`-z`, and the status letter from `--raw`), not from interpreting `git show`'s
   failure."* **A fail-closed command primitive cannot express "build the list with `-z`."** This is
   the A-P2a/A-P2b situation exactly — a guarantee whose semantics describe one substrate carrying
   another — and it needs its own sub-item.
4. **`install-hooks.sh:5` needs a SIDE-EFFECT assertion** (no foreign repository's `core.hooksPath`
   written) that no other consumer needs. The C6 table records this; A-P1's guarantee and success
   condition do not carry it.
5. **`test.sh:161` carries an unresolved decision fork whose option (B) REPLACES the construct**
   rather than guarding it, so that site may not consume the primitive at all.

**Fix.** Split off **A-P1b — a retrievable file list**: *"a guard's file list must be constructed so
that every path it names can be retrieved, and a retrieval failure over a path the list asserts
exists is an instrument failure."* Give it its own falsifications in **both** invocation modes, its
own controls (the staged-deletion control, which `--diff-filter=ACM` already excludes, **and a
default-mode control, for which no equivalent exclusion argument exists**), and its own note that
`git ls-files` carries no status letter, so ADJ4's status-`D` discriminator does not transfer.
Carry the side-effect obligation for `install-hooks.sh` into A-P1's success condition rather than
leaving it in a table.

### 8.2 FAILURE — the A-P2a / A-P2b split was right and A-P2a is still overstretched

A-P2a is *"exactly one normative publication inside a named Markdown section"*, with a
heading-depth-aware extent. Its consumer set contains three different properties and two different
extraction idioms:

| Consumer | Extraction | Property actually at issue |
|---|---|---|
| `check-type-strings.sh:36,:65` | heading-anchored `#{1,4}`, anchor depth 3 | extent (`C2`) + refuse-rather-than-choose |
| `check-eval-codes.sh:31,:52` | heading-anchored `#{1,4}`, anchor depth 4 | **membership anchoring** (`C1`) + extent WIDENING — neither is a uniqueness property |
| `check-vendor-honesty.sh:269` | **no extraction at all** — whole-document `grep -F` | scope the comparison to §7.2 (`V3-N2`) |
| `check-vendor-honesty.sh:351,:365` | literal next-heading terminator | extent widening under renumbering |
| `verifier/test_verifier.py:930` | `split("---")` | extent + silent LAST-wins tie-break |

*"The primitive is shared rather than duplicated per script"* is stated as a success condition. Over
this set it is a requirement to force three properties through one interface, and §5.2 shows the
cost: the shared primitive, correctly implemented, closes nothing at `check-eval-codes.sh`.

**Recommended split, on the same principle John applied to A-P2a/A-P2b:**

- **A-P2a-i — SECTION EXTENT.** Terminate at the first heading of depth **≤ the anchor's own
  depth**, parameterised by the anchor. Plus an explicit obligation for the WIDENING direction: the
  terminator's existence must be asserted, not assumed, because demoting or renumbering it extends
  the extent with no heading left to stop at (measured: 35 → 62 lines at §5.7.1).
- **A-P2a-ii — UNIQUENESS WITHIN THE EXTENT.** Refuse rather than choose. Applies where a duplicate
  is meaningful (`check-type-strings.sh`, `check-vendor-honesty.sh:352`); does **not** apply to a
  presence test, and the contract should say so rather than leaving item (a) to be run against a
  consumer it cannot move.
- **A-P2a-iii — ANCHORED MEMBERSHIP.** Word-boundary or exact match, for `check-eval-codes.sh:52`.
  Falsification: a strict-prefix truncating rename. Control: the non-prefix rename, which is caught
  today.

---

## 9. WHAT MUST CHANGE, AND WHAT IS RECORDED ONLY

**FAILURES — the contract may not be precommitted with these standing.**

| # | Failure | Where |
|---|---|---|
| F1 | The git-root class is thirteen scripts, not five; `check-vendor-honesty.sh` fails OPEN, gate-invoked, demonstrated | §1.1, §7.1 |
| F2 | `check-secrets.sh` has four skip points; one enumerated, and in the mode the gate does not run | §1.2, §5.4 |
| F3 | A third §5.8 extraction consumer in `verifier/`, unowned, opposite tie-break | §1.3 |
| F4 | Four more section extractions in `check-vendor-honesty.sh`, including the two feeding the certified table hash | §1.4 |
| F5 | A false completeness claim between the two D-F2 sites the contract does enumerate | §1.5 |
| F6 | The single-sourcing universal claim restated at `session-state.md:774`, outside every batch | §1.6 |
| F7 | Two live surfaces state the Foundry/TypeScript floors do not exist; not enumerated, no disposition | §1.7 |
| F8 | `docs/session-state.md` written by two batches; the ownership table lists one | §3.1 |
| F9 | `check-suite-floors.sh`'s ownership row omits A-P1, hiding one of its two independent routes | §3.2 |
| F10 | `C5` adjudicated CONFIRMED and owned by no batch | §3.3 |
| F11 | Batch D edits a file the GATE 5 section declares off-limits, without the §11.0 carve-out that permits it | §4.1 |
| F12 | D-F2's third site is material the source deliberately preserved; no disposition distinguishing it from D-F2's own control | §4.2 |
| F13 | **A-P2a observes nothing at `check-eval-codes.sh`, and its item (c) demands a refusal that would be wrong** | §5.2 |
| F14 | Two of A-P1's six falsifications, plus parts of #4 and Batch B item 3, are controls labelled as falsifications | §5.3 |
| F15 | A-G1 does not require the standing instance of its own defect to be closed or exempted | §6.1 |
| F16 | A-G1 does not require §7.1's live "which the gate runs" table to follow its own change | §6.2 |
| F17 | "each of the six `cd`-bearing scripts" contradicts "FIVE distinct scripts" | §7.1 |
| F18 | A-P1 stretched across three root causes; the `check-secrets.sh` repair is not expressible by the primitive | §8.1 |
| F19 | A-P2a stretched across three properties and two extraction idioms | §8.2 |

**RESIDUALS — worth recording, not blocking.**

`check-label-integrity.sh:63` undispositioned (§1.8); `check-vendor-honesty.sh:352` enters A-P2a
with an instruction to measure rather than a classification (§2); two undated narrative count
sentences inside dated blocks in `verifier/REPORT.md` (§4.3); the word "applicable" in A-G1(1)
(§6.3); the `test.sh:60`-inside-the-bootstrap dependency (§6.4); four citation offsets (§7.2).

**NOT REOPENED, and deliberately so.** Gate 5's status; the C6d remedy fork; whether the
no-gate-floor claims are repaired now or adjudicated as new findings; the wording candidate for
`F7-R1` (D-059(9) assigns its verification to the Batch B test author); the `--diff-filter=ACM`
staged-rename observation ADJ4 raised and did not adjudicate. Each is John's or a later stage's.

---

## 10. WHAT THIS AUDIT ESTABLISHES AND WHAT IT DOES NOT

**Establishes.** That the git-root class is thirteen scripts, by re-derivation, with a gate-invoked
fail-open demonstrated and discriminated against a control that moved with the decoy tree; that
`check-secrets.sh` fails open in the gate's own invocation mode, with an oppositely-behaving ASCII
control; that A-P2a's four falsifications produce, at base SHA, no refusal at
`check-eval-codes.sh` while `C1` survives them all and its non-prefix control is caught; that
A-P1's items 1 and 2 already refuse; that Batch B's and Batch C's falsifications are live and their
controls discriminate, by running them; that the contract's line-level citations are accurate
except at four places; and that D-F2's sites are permissible under a carve-out the contract does
not record.

**Does not establish.** Whether any of the newly-enumerated sites is reachable in practice — I
measured mechanism and fail direction, not likelihood. Whether the repairs, once respecified, are
correct: that is the test author's and the verifier's, and this audit deliberately proposes no
implementation. I did not run `scripts/test.sh`, the verifier suite, the deep profile, or the
corpus. I did not re-audit any of the eight D-058(8) confirmed obligations for whether they are
real — they are ruled, and re-litigating them is not this audit's job. I did not read the reviewer
reports before probing; I read the contract, `ENUMERATION.md`, the three adjudications and the two
governing rulings, and started from the tree rather than from anyone's account of it.

**The one thing I would say if only one line survived:** the contract's enumerations were each run
with a command shaped like the site somebody already reported, and every one of them therefore
stops where that report stopped. That is `V3-N1`'s lesson, and this document is where it has to be
applied next.
