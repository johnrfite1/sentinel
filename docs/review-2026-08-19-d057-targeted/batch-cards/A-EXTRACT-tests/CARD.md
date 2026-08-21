# BATCH CARD A-EXTRACT — named-scope extraction, exact membership, and uniqueness

**Authority:** D-058(1) (test-first separation), D-058(6) (no generic prose checker; a
line-oriented grep is DISALLOWED for a Markdown paragraph check), D-059(2) (a sibling
enumeration identifies candidates and does not adjudicate them), D-059(8) (section extraction
and source uniqueness are TWO properties, not one primitive), D-060(1) (batch cards;
completeness is asserted only inside a declared boundary).

**Pre-repair base SHA:** `bb664c626d592d86391f644bf014e76f2bbf7db4`, tree clean.
**Demonstrated at:** the same commit. **Harnesses:** `a-extract.sh` (fast, 49 binding assertions)
and `a-extract-gate.sh` (D-059(7) gate binding). Each prints its own sha256 at preflight `P0`;
both are recorded in `RESULTS.md` and `GATE-BINDING.md`.

**This revision is a CORRECTIVE update.** `e7ff655` and `ca49f18` are recorded history and are not
rewritten or amended; the first measurement they carry is preserved and reconciled with this one
in `RESULTS.md` §0.

**This card is small on purpose. It claims completeness ONLY inside the boundary below.** It is
**not** a Batch A1 attempt of any kind. **Batch A1 is CLOSED** — both ordinary attempts remain
FAILED, the D-062 containment exception closed one named regression, and **nothing here reopens
any A1 finding, residual, or harness.** The name `A-EXTRACT` is used precisely because `A2`
already identifies frozen attempt-two evidence.

**This is a test-only deliverable.** No production file is modified by this card, by its harness,
or by the commit that carries it. `TESTS.patch` is supplied as a patch file and is **NOT
applied**.

## D-065 DECLARES THE THREAT MODEL, AND A FOURTH REVIEW'S THREE ITEMS

**Four independent instrument reviews returned FAIL, FAIL, HOLD-with-residual and FAIL, and each
cycle closed one caller-controlled door while the next found another** — `GIT_CONFIG_*`, then
`refs/replace`, then `GIT_REPLACE_REF_BASE`, then `GIT_TEMPLATE_DIR`, with `PATH` named as next.
**John ruled the regress unbounded by construction and declared the bar (D-065).**

| | |
|---|---|
| **The bar** | the instrument must measure faithfully under a **NON-ADVERSARIAL** environment. A caller who can set arbitrary git environment variables **can equally edit this harness**, so that class is **out of scope** and a newly named variable is not by itself a defect |
| **Known doors** | scrubbed as **cheap hardening, one line each — NOT a completeness claim** |
| **Still in scope, the larger half** | a control that cannot fail; a comparison whose expected and actual sides move together; a counter that does not count; a snapshot that does not correspond to the requested commit under ordinary conditions; **a stated requirement silently removed**; a published figure that was never measured |

**The reviewers were not wrong — the specification was silent.** D-065(5) reverses the bar if this
harness is ever run where the caller is not the operator.

### The three items, and one of them is mine

**1 — Hardening (D-065(2), no completeness claimed).** `GIT_TEMPLATE_DIR` is unset and `PATH` is
pinned by precedence in both harnesses. The template door is real: `git init` and `git clone` copy
a caller-supplied template's `config` **and `hooks/`** into every repository the harness creates —
the very repository-local layer the `GIT_CONFIG_*` scrub exists to keep the caller out of.
**Paired control:** with hardening removed, a subject repository received the template's
`hooks/pre-commit` and `core.fsmonitor=/bin/echo`; with it present, both absent.

**2 — `F2-4`, in scope: the gate harness was structurally blind to replacement.** It pinned
`--no-replace-objects` on **zero** commands and was protected only by the accident that clone's
refspec skips `refs/replace`. **Protection by accident is not protection.** It now pins on every
command, and `P3-provenance` verifies the clone's **WORKTREE** against the subject's tree rather
than trusting what `HEAD` reports.

**3 — A STATED REQUIREMENT SILENTLY REMOVED, AND IT WAS MINE.** The `d1fa16f` edit deleted the
`SUBJECT IDENTITY` header and its `identity_block` call — `1 → 0` and `3 → 2` — so runs stopped
printing the five identity facts John required, **and my report of that commit did not mention
it.** Restored. **It was accidental, and the mechanism is recorded in the file rather than
excused:** the edit replaced a text region bounded by "the next blank line after the control's
description", and two lines sat inside that boundary. It went unnoticed because I verified the new
control behaved rather than reading what the replacement had swallowed. **Under D-065(3) this is
in scope regardless of threat model, and it is the class this project treats most seriously.**

## A THIRD REVIEW: OBJECT REPLACEMENT, A WEAK SENTINEL, AND A SELF-MASKING HARNESS

**VERDICT: FAIL** (`INSTRUMENT-REVIEW-3.md`; that document and the two before it are the
reviewers' records and none is edited here). **John ruled: fix all three and re-verify.** Still
instrument only; still not an implementation attempt. All three were reproduced independently
before anything was changed.

| | Finding | Repair |
|---|---|---|
| **F1 / F1b** | `refs/replace` substitutes objects in `git archive`, `git show <oid>:<path>` and `git cat-file blob <oid>:<path>` — every command that DELIVERS bytes — while `--batch-all-objects`, the existence check, is the one command immune. **The verifying and the measuring commands did not share semantics.** Reachable from the caller's environment alone; neither harness scrubbed `GIT_REPLACE_REF_BASE` or `GIT_NO_REPLACE_OBJECTS` | both scrubbed/exported before the first git call in **both** harnesses; the provenance and witness comparisons additionally pin `--no-replace-objects` on the command so they detect the hole even if the scrub were removed |
| **F1c** | `P3-provenance`'s sentinel was **one file**, and **21 commits in this repository share that blob with a different tree** | the control now compares **whole trees** — a digest over `path<TAB>blob-oid` for all 498 blob paths, plus the path list itself |
| **F2** | the `4f1e6a3` edit **deleted** `_clone_head`'s assignment while line 240 still read it; under `set -u` the verdict became empty, `check()`'s arithmetic errored, and **the printed FAIL was never counted** — the run reported controls held at rc 0, and `GATE-BINDING.md` recorded a false `PASS` | assignment restored; `check()` rewritten to string comparison with **anything not a literal `0` counted as a failure**, in **both** harnesses; the false row corrected |

**F2 is the one worth dwelling on: a harness that prints FAIL and then reports "all controls
held" is this project's named defect class, and it would have masked any future control failure,
not just this one.** It is demonstrated fixed with a deliberately failing control.

## THE SUBJECT INTERFACE IS NARROWED TO AN EXACT COMMIT OID — `R1` CLOSED STRUCTURALLY

**A second independent review returned VERDICT: HOLD with residual `R1` open**
(`INSTRUMENT-REVIEW-2.md`; that document and `INSTRUMENT-REVIEW.md` are the reviewers' records
and neither is edited here). **John ruled `R1` NOT ACCEPTED — close it before implementation.**
Still instrument and tests only; still not an implementation attempt.

**`R1`, in one sentence:** the ambiguity repair's second detector reads git's ambiguity WARNING,
and `core.warnAmbiguousRefs=false` switches that warning off — after which one ambiguity class
produced a full green measurement of a commit nobody named.

**The ruling does not add a third detector. It deletes what the detectors were guarding.**

| | |
|---|---|
| **Accepted** | `^[0-9a-f]{40}$` naming an object of type `commit` |
| **Refused**, exit 2, **zero scored verdicts** | abbreviated ids · branch / tag / remote names · `HEAD` · `refs/…` · revision expressions · option-shaped input · uppercase hex · absent objects · non-commit objects · wrong argument count |

**A name has to be RESOLVED, and resolution is the part a tag, an abbreviation or a configuration
setting gets to influence. An exact object id is looked up, not resolved. There is no
ref-resolution step left to defeat.** Existence and type are established by
`git cat-file --batch-all-objects`, which enumerates the object database and performs **no name
resolution at all**. Measured: a branch literally *named* a 40-hex oid, pointing elsewhere, does
not shadow that object — with the ambiguity warning on or off.

**Caller configuration injection is neutralised before the first git invocation** —
`GIT_CONFIG_COUNT`, every `GIT_CONFIG_KEY_<n>` / `GIT_CONFIG_VALUE_<n>` enumerated from the
environment rather than assumed to stop at a small n, and `GIT_CONFIG_PARAMETERS`. The private
empty global/system configuration is retained. **This is an INSTRUMENT-LOCAL isolation repair: it
does not reopen Batch A1 and does not claim to solve A1's repository-wide `R-C` residual.**

**`P3` is renamed `P3-provenance` and redescribed as a subject-provenance CONSISTENCY control —
not an independence proof**, accepting `R2` as a documented limitation. The claim that two git
commands are independent is withdrawn: they share git's object resolver. The full chain and what
asserts each link are in `COVERAGE.md` §0.

## A SECOND INSTRUMENT DEFECT, FOUND BY INDEPENDENT REVIEW — VERDICT FAIL, then SUPERSEDED

> **The two-detector answer described in this section was itself found wanting (`R1`) and is
> SUPERSEDED by the exact-oid grammar in the section above.** It is retained as the record of
> that repair. Where it says "two independent mechanisms", that describes the interface as it
> then stood, not as it stands now.

**An independent instrument review of the corrected harness returned VERDICT: FAIL**
(`INSTRUMENT-REVIEW.md`, committed at `7e4e5c0`; that document is the reviewer's record and is
not edited here). John ruled: fix and re-verify inside this same instrument checkpoint. **Still
an instrument correction, still not an implementation attempt.**

**The finding, reproduced independently before fixing anything.** The subject-resolution fix
rested on a false premise stated in the harness's own comment: that
`git rev-parse --verify <ref>^{commit}` refuses an ambiguous ref. **It does not.** On git 2.50.1
with a branch and a tag both named `ambig`, it returns the **tag's** commit, exit 0, with only a
warning on stderr — and the harness suppressed that warning with `--quiet` and discarded it again
with `2>/dev/null`. **A full 126-verdict measurement of the wrong commit completed on the
ordinary path with all 74 controls green and `P3` reporting PASS.**

**Three defects, all three corrected:**

1. **The ambiguity fail-open.** Now caught by **two independent mechanisms** — enumerate the refs
   the name could denote and refuse if more than one exists; and keep `rev-parse`'s stderr and
   refuse on any ambiguity warning. **Each catches a case the other misses**, measured: a branch
   named like an abbreviated object id is a single ref, so enumeration alone sees nothing, and
   only the stderr mechanism catches it. Refusal is a preflight instrument failure — exit 2,
   **zero scored verdicts**.
2. **`P3` was unfalsifiable by construction** — it re-ran the identical command and compared the
   answer to itself. It now compares two routes that can disagree, and **route B declines to
   choose when a name is ambiguous rather than tie-breaking**. Demonstrated failing.
3. **The false claim in the comment** is replaced by what `--verify` actually guarantees: one
   object name, not one ref.

Full interface and the measured mechanism table are in `COVERAGE.md` §0.

## AN INSTRUMENT DEFECT FOUND IN JOHN'S REVIEW — corrected, and NOT an implementation attempt

**John reviewed this contract and found a BLOCKING defect in the harness itself.** It is recorded
here as an instrument defect found in review. **It is not implementation attempt one and must not
be counted as one; D-058(9)'s attempt budget is unspent.**

**The defect.** `a-extract.sh` hardcoded the subject commit and built its snapshot from that
constant, whatever repository or HEAD it was handed. `P3` noticed a differing HEAD and emitted an
**OBSERVED warning it could not fail on**. The four consumer-integrity controls, the Gate 5
control and the signed-pack control all compared against the same constant.

**The consequence, which is why it was blocking.** After a repair the harness would have
extracted and measured the **PRE-REPAIR** consumers and reported **`21 of 49` for ever, with
every control green** — and this card forbids the implementer from touching the harness, so
nothing downstream could have corrected it. **A harness that cannot observe the repair it exists
to gate is a confident wrong answer**, which is this project's named defect class.
`a-extract-gate.sh` carried the same shape.

**The correction, in five parts.** `PRE_REPAIR_SHA` stays as an immutable named reference so the
original measurement remains reproducible, but is never archived. An evidentiary run takes an
explicit repository **and** an explicit subject ref; the subject is resolved with
`git rev-parse --verify --quiet "<ref>^{commit}"` and a missing, **ambiguous**, or
not-a-commit ref is a **preflight refusal**, never a fallback. The snapshot is built from
`SUBJECT_SHA`. **`P3` became a CONTROL** — later renamed `P3-provenance` and redescribed as a consistency
control, see the section above. The four consumer-integrity controls compare against `SUBJECT_SHA`; `Z-clean`,
`Z-gate5` and `Z-signed` remain about the **live tree** and are deliberately not folded in. Every
run prints five identity facts separately — harness hash, sanitized repository path, requested
ref, resolved `SUBJECT_SHA`, pre-repair reference. **The full interface is `COVERAGE.md` §0.**

**No case semantics, reason vocabulary, expected outcome, exclusion or Gate 5 material was
changed to accomplish it.** The only deliberate count movement is `P3` becoming a CONTROL where
it was an OBSERVED line, plus the fence sibling below.

## ADJUDICATION OF WHAT THIS CARD EXPOSED — settled, and fed back in

An independent adjudicator classified the three defect classes this card's first run exposed
(`adjudication/A-EXTRACT/`, committed at `3668f51`). **The classifications are settled and this
card is written to them, not around them.**

| id | Class | Verdict |
|---|---|---|
| **AX-1** | the exact section ANCHOR is taken first-match and a duplicate anchor is never detected | **CONFIRMED, MEDIUM, distinct.** The adjudicator ran `C2`'s depth-aware terminator and `C1`'s word-anchored membership against its own fixtures and **both still read the decoy**, so neither existing remedy discharges it. It reaches a third consumer, `verifier/test_verifier.py`. |
| **AX-2** | the authoritative SOURCE-definition lookup does not require uniqueness | **DUPLICATE — it IS `R4-F3`'s confirmed, unrepaired residual.** The block is byte-identical to `c8d15a7`, which `R4-F3` was verified FAIL against. **No new finding id exists for it and this card claims none.** The observation that `6before` exits non-zero for the WRONG reason is a refinement of `R4-F3`'s severity, not a second defect. |
| **AX-3** | the `§7.2` caveat comparison is line-oriented on the PROPOSAL side | **CONFIRMED, MEDIUM, sibling of `V3-N2`** — same line, and neither remedy covers the other. The adjudicator additionally demonstrated a **false-assurance** direction the first run did not record; it is now case `11g`. |

## WHAT CHANGED IN THIS REVISION, and why

The first cut of this contract had cases that returned the right verdict for the wrong reason, or
had no discriminating control at all. **Each is either repaired or removed — none is left in the
binding set on a weak assertion.** See `COVERAGE.md` §7 for the removals with their reasons.

- **`14d` removed from binding.** It compared the live repository's pin against a constant with no
  opposite outcome available, because producing one would mean editing `§2`. The PASS/FAIL pair is
  now `14a`/`14b` **on an isolated snapshot**; what remains of `14d` is an integrity control,
  `Z-gate5`.
- **`1c` no longer binds on a crash.** An uncaught `IndexError` is an instrument failure. It now
  requires a **stable named diagnostic** in the `anchor-unresolved` class, paired with `1c-ctl`.
- **Case 13 asserts a REASON CLASS per consumer.** Boolean agreement let `13b-after` pass while the
  two consumers were failing for different reasons.
- **`11f` executes the canonical generator.** The proxy over `report.ts`'s text is gone.
- **EC duplicate publication: determined NOT NORMATIVE and omitted**, with `P8` asserting the basis.
- **Vendor honesty gains section-extent cases** (`10c`–`10h`) written **before** any extractor exists.
- **Exact-anchor cases added:** a quoted heading is a mention — now in **both fence spellings**,
  `4e-btick`/`4e-tilde` (TS), `4f-btick`/`4f-tilde` (EC), `10h-btick`/`10h-tilde` (VH), each with
  its own mutation control; two exact headings must be REFUSED rather than the first selected
  (`4b`, `4c`, `4d`, `10g`, `13f`).
- **The harness's own section reader is now anchor-derived.** It had a fixed `^#{1,6} `
  terminator — the same defect case 7 exists to falsify — and control `10c-mut` failed because of
  it. An instrument carrying the defect it measures cannot be believed about it.

## THE INVARIANT — one

> **A checker naming a section, publication, or identifier must inspect that exact scope and
> require the exact value. It must not pass through a prefix, outside-section decoy, duplicate
> publication, incorrect heading boundary, or first-match tie-break.**

Two things make this a real invariant here rather than a slogan. **The proposal's section order
is not monotonic** — `§5.9` precedes `§5.8`, which precedes `§5.7` — so "the first match" is
routinely not "the real one". And **the same `####` heading depth must mean opposite things at
the two anchors**: inside `§5.8` (a `###` anchor) it is a subsection that stays IN, and at
`§5.7.1` (a `####` anchor) it is a sibling that ENDS the section. A fixed `#{1,4}` terminator
class cannot be right for both, which is why heading depth must be derived from the anchor.

## BOUNDARY — four consumers, and only three kinds of block inside them

| Tag | File | The blocks in scope |
|---|---|---|
| **TS** | `scripts/check-type-strings.sh` | the `§5.8` `awk` extraction; the per-type publication-uniqueness test (`spec_hits`); the `§5.8` publication lookup; the `eip712.ts` source-definition lookup |
| **EC** | `scripts/check-eval-codes.sh` | the `§5.7.1` `awk` extraction; the per-code membership test (`grep -q "$code"`) |
| **VH** | `scripts/check-vendor-honesty.sh` | the `§7.2` caveat extraction (`CAVEAT=…`) and its comparison against `docs/ablation-report.md`, including `norm()` |
| **VP** | `verifier/test_verifier.py` | `TestPublishedTypeStrings` — the `§5.8` consumer only |

**Fixture files the cases mutate** (never in the repository under test; only in private
snapshots): `Sentinel_Protocol_Lab_Proposal_v0_2.md`, `ts/src/signer/eip712.ts`,
`docs/ablation-report.md`.

**Explicitly OUTSIDE this boundary and untouched:** every other block of those four files —
the repository-identity preamble, the git-environment scrubbing, the vendor-name scan, the
`§10.1` label scan, the `§13` marker census, `EVAL_CODES` parsing, and every other test class in
`test_verifier.py`. Every other script. Floors, vault events, signer state, maintained-claim
repairs, signed text, D-055, D-016, publication. **`docs/gate-s2-evidence.md` is not read,
quoted, or proposed for change by this card.**

## TEST MATRIX — fourteen cases, all required

**Fourteen CASES; forty-nine BINDING assertions.** The case numbers are the brief's; the
sub-case ids below are the harness's. Every binding assertion carries a paired control, a
proof-of-mutation control, and a named failure reason. **Where a case could not be given a
discriminating control it was REMOVED from the binding set and recorded as a residual, never
left in on a weak assertion** — see the EXCLUDED table below and `COVERAGE.md` §7.

| # | Case | Consumers | Required behaviour |
|---|---|---|---|
| 1 | the named section is **ABSENT** | TS, EC, VP | **refuse, naming the section.** No result for a scope that could not be found, and no fallback to the whole document |
| 2 | the exact value is **absent but a prefix-sharing value exists** | EC, TS | **exact membership.** A token of which the required value is a proper prefix is a different token |
| 3 | the value is present **only OUTSIDE** the named section | EC, TS | the value must be reported absent, in **both directions of the file** |
| 4 | an **outside-section decoy BEFORE** the real section | TS, EC | **refuse the ambiguity**; never a first-match tie-break, and never a success report |
| 5 | **duplicate normative publication inside the section, in BOTH orders** | TS | **refuse**, naming the type. There is no correct way to choose |
| 6 | **duplicate authoritative definition in the SOURCE, in BOTH orders** | TS | **refuse**, naming the duplicate definition — not "drift", and not success |
| 7 | a **deeper subsection stays INSIDE** its parent | TS, EC | `#### 5.8.1` does not truncate `§5.8`; `##### 5.7.1.1` does not truncate `§5.7.1` |
| 8 | a **same-depth or shallower heading ENDS** the section | TS, EC | and the depth is **relative to the anchor** — see 7a/8c |
| 9 | a **prose or backticked mention is NOT a publication** | TS | the verdict is unchanged and no duplicate refusal is raised |
| 10 | the **`§7.2` caveat comes from `§7.2` itself** | VH | not from the first tree-wide match, in **both the false-fail and the false-pass direction** |
| 11 | the **generated ablation report carries the exact caveat** | VH | and the comparison is over **logical paragraphs**, on the proposal side as well as the report side |
| 12 | **a ONE-CHARACTER prefix substitution is rejected** | EC | appended or prepended; one character makes a different identifier |
| 13 | the **verifier `§5.8` consumer AGREES with the shell guard** | VP + TS | on section extent and on duplicate handling |
| 14 | **Gate 5's certified `§2` table and its pinned hash are unchanged** | VH | a control that must hold **before and after** any repair |

### What each case asserts, in the harness's own case ids

**BINDING — every one has a paired control, a distinct named failure reason, and a
proof-of-mutation control.**

- **1a / 1b** — TS and EC refuse by name. **1c** — the verifier emits a **named
  `anchor-unresolved` diagnostic** mentioning §5.8, with **no uncaught traceback**; `1c-ctl` is the
  valid-input control.
- **2a** (EC, `EVAL_POLICY_WINDOW` vs `EVAL_POLICY_WINDOW_STRICT`), **2b** (TS,
  `PolicyPayload` vs `PolicyPayloadV2`).
- **3a** (EC, code moved later in the file), **3b** (TS, publication moved to §5.6).
- **4a** correct decoy earlier in §5.9, real §5.8 transposed → must report the drift.
  **4c** two complete §5.8 sections → must refuse. **4d** the FIRST §5.8 correct, the real one
  transposed → **must not report success**. **4b** the same shape at §5.7.1.
  **4e-btick / 4e-tilde / 4f-btick / 4f-tilde** — a heading **quoted inside a fenced code block**
  is a MENTION and must not be selected as the anchor, at TS and EC, in **both CommonMark fence
  spellings**: three backticks and three tildes. **Each fence character is its own case with its
  own proof-of-mutation control** — a guard taught to ignore ``` and not `~~~` would have
  generalised the demonstration and not the argument. Deliberately not generalised further:
  indented code blocks, HTML blocks, blockquoted headings and info-string variants are NOT probed.
- **5before / 5after** — duplicate publication either side of the real line.
- **6before / 6after** — duplicate SOURCE definition either side of the real one. **This is
  `R4-F3`'s residual (AX-2), carried under its existing id.**
- **7a** `####` inside §5.8 (must stay in), **7b** `#####` inside §5.7.1 (must stay in),
  **7c** `#####` inside §5.8 — a CONTROL, because it already stays in.
- **8a** `###` inside §5.8, **8b** `##` inside §5.8, **8c** `####` inside §5.7.1,
  **8d** `###` inside §5.7.1. **8c against 7a is the anchor-derivation evidence**: the same
  `####` depth, opposite required outcomes.
- **9a** inline backticked mention, **9b** indented backticked line, **9c** CONTROL — the same
  text unbackticked IS a publication and is refused.
- **10a** decoy earlier, §7.2 intact → must report ok. **10b** decoy earlier matching the report
  while §7.2's own wording is absent from it → **must FAIL naming the report**.
  **§7.2 SECTION EXTENT, specified before any extractor exists:** **10c** a `####` subsection
  inside §7.2 does not end it; **10d** a same-depth `###` heading does; **10e** a shallower `##`
  heading does; **10f** an ABSENT §7.2 anchor is REFUSED by name; **10g** TWO exact §7.2 headings
  are REFUSED as ambiguous; **10h-btick / 10h-tilde** a §7.2 heading quoted in a fenced block is a MENTION, in both fence spellings.
- **11a** base commit; **11b** §7.2's caveat hard-wrapped → must still be located;
  **11g** the **AX-3 false-assurance** direction — the report carries only the TAIL half and the
  guard must FAIL naming it; **11c/11d** controls.
  **11f-a / 11f-b / 11f-c** — the **canonical generator is EXECUTED** (`buildReport(loadInputs())`,
  the entry point `scripts/test.sh`'s A-062 stage uses): its output is byte-identical to the
  committed report, the **regenerated** artifact carries the caveat, and VH passes **against the
  regenerated artifact**. `11f-ctl` removes the emitting statement from the generator and requires
  VH to fail naming the report.
- **12suffix / 12prefix** — `EVAL_NONCE_CURRENTX` and `XEVAL_NONCE_CURRENT`.
- **13a / 13b-before / 13b-after / 13d / 13e / 13f** — each names the **reason class BOTH
  consumers must produce**; class equality alone is not asserted, and two consumers failing for
  different reasons is a failure. Vocabulary: `success`, `anchor-unresolved`, `anchor-ambiguous`,
  `duplicate-publication`, `not-published`, `drift`, `duplicate-definition`, `crash`, `other`.
  **`crash` is never an acceptable class.**
- **14a / 14b** — the certified §2 table and its pin exercised **in an isolated copy**, both
  directions: unmodified table + pin → certified by record; mutated table + **pin left unchanged**
  → STALE. **The live pin is never updated, re-signed or touched.**

**EXCLUDED from the binding contract, each with its reason** — full statements in `COVERAGE.md` §7:

| Removed | Reason |
|---|---|
| `14d` (live-repository pin comparison) | no discriminating control is constructible without editing `§2` in the live tree, which D-059(1) forbids. Retained as integrity control `Z-gate5`. |
| EC duplicate-publication case | **§5.7.1 declares its identifiers NON-NORMATIVE.** A section that does not publish normatively cannot publish twice normatively; manufacturing the requirement would be inventing an obligation the document declines. `P8` asserts the basis so the omission expires if §5.7.1 ever becomes normative. |
| the `11f` proxy over `report.ts` text | replaced by executing the generator. A text count cannot tell an emitted sentence from a commented-out one. |
| boolean agreement in case 13 | replaced by per-consumer reason classes. |

## GATE BINDING — D-059(7), `a-extract-gate.sh`

*"A standalone script that nothing invokes repeats the defect this work is trying to close."*
A separate harness runs the **top-level fast gate** against a private clone and demonstrates three
things. `GATE-BINDING.md` carries the measured evidence.

| | Demonstration |
|---|---|
| **G1** | the **unchanged** top-level fast gate **PASSES**, and all three consumer stages are invoked by name |
| **G2** | breaking the **FIRST** consumer makes the gate fail **at its named stage** — and the two LATER consumer stages report success in the same run without clearing it |
| **G3** | breaking the **LAST** consumer does the same with the two EARLIER consumer stages green |

The three stage banners are `== published EIP-712 type strings (D-023) ==`,
`== §5.7.1 check coverage (D-031) ==` and `== vendor honesty (§7.5 Gate 5, D-008) ==`.
**Both directions are run because "a later stage cannot clear an earlier failure" and "earlier
successes cannot excuse a later failure" are two properties, and one direction shows only one.**

**Stated explicitly, as D-059(7) requires: these guards cover only their enumerated canonical
facts — six §5.8 type strings, forty-one §5.7.1 identifiers, one §7.2 sentence, one §2 table
hash. They are NOT general prose-consistency evidence.**

## CONTROLS — each case has an opposite outcome, or it proves nothing

- **Every mutation proves it applied.** Each `*-mut` control counts the fixture before and
  after — anchors present/absent, exact-token vs substring hits, decoy line number against the
  real one, publications above and below an interposed heading. A probe whose mutation silently
  failed reads exactly like a pass, and this harness has already caught that in itself: an
  `awk -v` carrying a newline errored to stderr, the mutation did not apply, and case `11b`
  reported PASS against an unmutated fixture until the `*-mut` control was added.
- **`1-ctl`, `5-ctl`, `6-ctl`, `8-ctl`, `10-ctl`, `13-ctl`** — the unmutated snapshot, where
  every consumer reports success. Nothing here is satisfiable by a checker that always fails.
- **`2-ctl`, `12-ctl`** — the identifier removed outright, where EC *does* name it missing. So
  the reporting path is live and `2a`/`12*` are about the matching rule, not about plumbing.
- **`7c` against `7a`** — the SAME insertion at a deeper heading level already passes, so `7a`
  is about depth and not about headings in general.
- **`9c` against `9a`/`9b`** — the identical text as an unbackticked literal IS refused, so
  `9a`/`9b` do not pass because the fixture is inert.
- **`11c`, `11d`** — the report's copy altered by one word FAILS, and a pure re-wrap of the
  report does not. `11b` is therefore about the **proposal** side of the comparison.
- **`14b` against `14a`** — the same snapshot, one §2 row changed and the pin left alone, makes the
  guard report STALE where it reported certified. Case 14 is a two-direction pair, not a single
  same-value comparison.
- **`P8`** — §5.7.1 still declares its identifiers non-normative. The basis for omitting an EC
  duplicate-publication case is asserted, not assumed, so the omission expires if that changes.
- **`1c-ctl`** — the same verifier consumer reports `success` and emits no diagnostic on VALID
  input, so `1c` is about the malformed path and not about the harness reaching the consumer.
- **`11f-ran` / `11f-mut` / `11f-ctl` / `11f-restore`** — the canonical generator really ran;
  deleting its emitting statement really removes the caveat from its output and really makes VH
  fail; and the generator fixture is restored so nothing downstream inherits the mutation.
- **`14-fixture` / `14b-mut`** — the snapshot's pin is the certified value, and the §2 mutation
  moved the table **while leaving the pin unchanged**, which is what makes `14b` a test of the pin
  rather than of an edit to it.
- **`Z-*`** — the four consumers are byte-identical to the base SHA at run time, the repository
  under test is unmodified when the run ends, **Gate 5's pin and §2 table are unmoved
  (`Z-gate5`)**, and **`docs/gate-s2-evidence.md` is byte-identical to the base commit
  (`Z-signed`)** — no signed document was read for change.

**A failing CONTROL exits 2 and invalidates every verdict beside it.** A failing REQUIRED with
all controls holding exits 1. **Exit status alone is never a per-case discriminator:** three of
the four consumers exit 1 for every finding they have, so every assertion here is on OUTPUT —
the success line absent, and the finding NAMED.

**Refusal wording is matched as a set of alternatives, never as one dictated sentence.** The
repair chooses its words; it may not choose silence, success, or a message about something else.

## EXCLUSIONS

- **No implementation is proposed.** Every assertion is on behaviour: what is reported, what is
  refused, what is named. Nothing asserts how a consumer extracts a section.
- **No generic prose-consistency checker is proposed or tested** (D-058(6)). Every probe is
  aimed at a named canonical fact: six type strings, forty-one identifiers, one `§7.2` sentence,
  one `§2` table hash.
- **Batch A1 is not reopened.** No A1 test, no A1 production change, no relabelling of either
  attempt.
- **Gate 5 is neither revoked, reaffirmed nor recertified** (D-059(1)). Case 14 asserts only
  that this batch leaves the certified table and its pin exactly where they were.
- **`R2` (quotePath), `R3`, `R5`** and every other deferred item stay deferred.
- One platform, one git, one python. See `COVERAGE.md` §2.

## DELIVERABLES

| File | What it is |
|---|---|
| `CARD.md` | this card — the invariant, the boundary, the matrix, the controls, the exclusions, the stopping rule |
| `a-extract.sh` | the fast harness: 49 binding assertions, 70 controls, ~2 minutes, no toolchain beyond git/bash/awk/python3/node |
| `a-extract-gate.sh` | the D-059(7) gate-binding harness: three full fast-gate runs in an isolated clone, ~10-20 minutes, needs forge and `ts/node_modules` |
| `GATE-BINDING.md` | the measured gate-binding evidence |
| `COVERAGE.md` | what is exercised, what is not, the interpretations, and **§7 — what was removed from the binding contract and why** |
| `RESULTS.md` | the measured pre-repair run at `bb664c6`, both measurements, and the per-case verdicts |
| `TESTS.patch` | the verifier-side half of the case-13 contract — **a patch file, NOT applied** |

## STOPPING RULE

**This batch STOPS at the independent test checkpoint.** The tests are demonstrated failing for
their intended pre-repair reasons with every control discriminating; the harness, this card,
`COVERAGE.md`, `RESULTS.md` and `TESTS.patch` are committed; **John reviews before any
implementation begins.**

Thereafter D-058(9): **at most two implementation attempts** against this fixed contract. **The
implementer may not modify, weaken, relocate or delete this harness or `TESTS.patch`**
(D-058(1)). If a case here is believed invalid, the implementation **STOPS** and has the
invalidity independently confirmed before anything changes. A failure in this batch does not
authorize widening another.
