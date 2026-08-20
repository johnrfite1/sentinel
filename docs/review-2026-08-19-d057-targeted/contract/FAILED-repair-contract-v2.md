> # FAILED / SUPERSEDED — NOT OPERATIVE
> **This is preserved PROCESS EVIDENCE, not an instruction to anyone.**
> Repair Contract v2 was independently audited and returned **FAIL**.
> **D-060(1) abandons the global-contract method entirely.** There is no active
> repository-wide prose contract. Remediation proceeds through small, independently
> test-authored BATCH CARDS instead — see `../README.md`.
> **Do not implement anything from this document.**

---

# REPAIR CONTRACT v2 — D-058 remediation

**Authority:** D-058, D-059 (John, 2026-08-19). **Base SHA:**
`a18e6e61598a996d962798ad0353a166232d4490`.

**THIS IS THE ONE REVISION D-059(10) PERMITS.** v1 was audited independently and returned **FAIL
on 7 of 8 dimensions, 19 numbered failures**. v1 is preserved unaltered as
`REPAIR-CONTRACT-v1-superseded.md`; the audit is `CONTRACT-AUDIT.md`. **A contract revision does
not consume a batch implementation attempt.**

## Why this is a rewrite and not a patch

The auditor's closing diagnosis, which is correct and is the reason the structure changed:

> the contract's enumerations were each run with a command shaped like the site somebody already
> reported, and every one of them therefore stops where that report stopped.

v1 was organised by **reported symptom**, so each sibling list inherited the blind spot of the
report that produced it. `ENUMERATION.md`'s `cd "$(` pattern could not see the two-step
`ROOT="$(git rev-parse …)"` idiom, and missed **eight** scripts. **v2 is organised by ROOT CAUSE**,
and every enumeration below is derived from the *mechanism*, not from a reported line number.

**Bounded stopping rule (D-058(9)):** two implementation attempts per batch after its contract is
fixed; second failure of the same contract or sibling class **stops and returns to John**.

---

## 1. SINGLE OWNERSHIP — corrected (fixes F8, F9, F10)

| Item | **OWNER** | Dependency only |
|---|---|---|
| Repository-root resolution, **all 13 scripts** | **A-R1** | — |
| `check-secrets.sh` file retrieval, **both modes, 4 skip points** | **A-R2** | — |
| Markdown section extent — **all consumers incl. `verifier/`** | **A-R3** | — |
| Normative-publication uniqueness (Markdown **and** source) | **A-R4** | — |
| Identifier membership word-bounding (`C1`) | **A-R5** | — |
| Floor constants; every live floor surface; `test.sh` stale output | **A-R6** | D (control only) |
| Targeted guard + gate wiring | **A-G1** | D-F5 consumes |
| `SentinelVault.sol` events and NatSpec | **B** | — |
| `ts/src/signer/vault.ts` branch matrix | **C** | — |
| **`C5` — the signer "detail" claim** (`protocol.ts` comment + `decisions.md` A-077) | **D-F6** — **F10 fixed; it was owned by nobody in v1** | — |
| `exit-criterion-packet.md` §7 | **D-F1** | — |
| Accepted-limit derivation | **D-F2** | supplies a fact to A-G1 |
| `decode/index.ts`, `evaluate.checks.test.ts` | **D-F4** | — |

**`docs/session-state.md` is written by A-R6 (floor passages) and D-F2/D-F3 (count derivation)
— F8 fixed by naming both here.** They touch disjoint passages; **A-R6 owns every line stating a
floor value, D-F2 owns only the accepted-limit sentences.** Neither may edit the other's passage.

**`check-suite-floors.sh` is owned by A-R1 (its `cd`), A-R4 (its `head -1`) and A-R6 (its floor
semantics) — three independent routes, F9 fixed by stating all three.**

---

## 2. GATE 5 — D-059(1), unchanged from v1

Certification **STANDS**. `check-vendor-honesty.sh` is **NOT ADMISSIBLE** as evidence for its
supplementary §7.2 condition until repaired and independently reverified. **The repairer must not
revoke, reaffirm or recertify — none of the three.** The signed-text correction is **OFFERED, not
applied**, at `offered/OFFERED-S2-SIGNED-TEXT.md`, and is in **no batch**.

**F11 fix — the carve-out v1 omitted.** D-F2 edits `docs/gate-s2-evidence.md` §11.0, which the
Gate 5 section calls a signed pack. **That is permissible and here is why, recorded so the
repairer neither edits signed text nor stops:** §11.0 carries an explicit
not-retrospectively-signed carve-out in its own text, and the D-041 signing commit `9488f27`
contains **zero** occurrences of `11.0` — it was introduced two days later at `c2fc8d2`.
**The PROTECTED phrase is a different sentence entirely (`:284`), it IS inside the signed
boundary, and it is not in any batch.** §11.0 ≠ `:284`.

---

## 3. BATCH A — organised by ROOT CAUSE

### A-R1 — repository-root resolution (fixes F1, F17, F18-part)

**Guarantee:** *A script that relocates to the repository root must establish that it reached the
intended root, and must refuse rather than operate against whatever tree it landed in.*

**ROOT CAUSE:** `cd ""` returns 0 and does not abort even under `set -euo pipefail` (verified).
**Two idioms express it and v1's enumeration saw only one:**

```
/usr/bin/grep -lE '(cd "\$\(git rev-parse --show-toplevel\)"|[A-Za-z_]+="\$\(git rev-parse --show-toplevel\)")' scripts/*.sh
```

**THIRTEEN SCRIPTS, not five.** v1 said five; falsification #4 then said six; **both were wrong
and the contradiction is F17.** The correct statement: **13 scripts carry the class; `test.sh:60`'s
`BASH_SOURCE` bootstrap is a separate, argued exemption and is not one of them.**

| Script | Idiom | Fail direction | Gate-invoked? |
|---|---|---|---|
| `check-review-scope.sh:47` | `cd "$(…)"` | closed (false diagnostic) | no |
| `check-suite-floors.sh:13` | `cd "$(…)"` | **OPEN** | no |
| `install-hooks.sh:5` | `cd "$(…)"` | **OPEN** (writes `core.hooksPath` into a foreign repo) | no |
| `check-findings-ledger.sh:22` | `cd "$(…)"` | closed | no |
| `test.sh:161` | `cd "$(…)"` | closed as measured; **carries the C6d fork** | **it IS the gate** |
| **`check-vendor-honesty.sh`** | `ROOT="$(…)"` | **OPEN — demonstrated: a complete clean certification, exit 0, standing in a two-file decoy tree** | **YES (`test.sh:209`), and it is the Gate 5 instrument** |
| `check-class-coverage.sh`, `check-eval-codes.sh`, `check-gate-immutability.sh`, `check-label-integrity.sh`, `check-label-prompt.sh`, `check-type-strings.sh`, `mutate.sh` | `ROOT="$(…)"` | **to be measured per script by the test author — not assumed** | mixed |

**Falsifications — one per script, not one for the class.** Merging them repeats the D-057(1)
grouping error: fail directions differ, and `install-hooks.sh` needs a **side-effect** assertion
(no foreign `core.hooksPath` write) that no other site needs.

**Controls:** every script run from the true root behaves exactly as at base SHA. For
`check-vendor-honesty.sh` specifically, the discriminating control is the audit's: removing one
capability row from the decoy makes it print a *lower* count and FAIL, so the probe is live.

**Success condition:** **13 scripts each carry an observing falsification and a control**;
`test.sh:60` carries a recorded exemption; **no count in this contract says five or six.**

**C6d FORK — JOHN'S, and repairing `cd ""` does not touch it.** `git rev-parse --show-toplevel`
yields the **caller's** root, not the **script's** tree, and they diverge even when git works.
**(A)** keep caller-relative semantics and document, or **(B)** adopt the `BASH_SOURCE` idiom.
**This changes what a `GATE PASSED` line asserts.** **The test author must not choose.**

### A-R2 — file retrieval in `check-secrets.sh` (fixes F2, F18-part)

**Guarantee:** *A secret scan must scan every file it reports having scanned, and must refuse when
it cannot retrieve one, while never converting a legitimate absence into a failure.*

**ROOT CAUSE (`C4`):** `core.quotePath`. A non-ASCII filename is emitted quoted and
octal-escaped, and retrieval by that token fails. **Demonstrated: two byte-identical files with a
planted 64-hex key differing only by one non-ASCII byte in the FILENAME — ASCII twin BLOCKED,
accented twin silently skipped, guard prints `clean`, exit 0.**

**FOUR skip points, TWO modes. v1 enumerated ONE — and it was in the mode the gate does not run.**

| Line | Mode | Disposition |
|---|---|---|
| `:85` | shared | to be classified by the test author |
| `:195` | staged | empty-line guard; classify |
| `:198` | **staged** | `C4` as adjudicated. **`test.sh:176` does NOT pass `--staged`** |
| **`:201`** | **default — THE MODE THE GATE RUNS** | **`[ -f "$f" ] \|\| continue` — fail-OPEN, demonstrated over a planted key whose ASCII twin is blocked** |
| `:226`, `:231` | third loop | classify |

**F2's sting, stated so it cannot be missed: the adjudicated discriminator does NOT transfer.**
`git diff --cached --raw -z` gives status letters and blob OIDs — but the **default** mode uses
`git ls-files`, **which has no status letters.** **The default-mode repair needs its own
discriminator, and the test author must establish one rather than reuse `C4`'s.** If none exists,
that is a **DECISION FORK for John**, not an engineering choice.

**Control (D-059(3), protected):** a staged deletion must NOT cause refusal. Structurally safe in
staged mode — `--diff-filter=ACM` at `:78` drops status `D`, so it never reaches `:198`. **In
default mode this protection has not been established and must be.**

### A-R3 — Markdown section extent (fixes F3, F4, F13-part, F19)

**Guarantee:** *A guard certifying a NAMED section must derive that section's extent with an
**ANCHOR-DEPTH-RELATIVE** terminator: a heading DEEPER than the anchor lies INSIDE; a heading of
the SAME OR SHALLOWER depth ENDS it.*

**ROOT CAUSE (`C2`):** the terminator `#{1,4}` is a **fixed** depth class, independent of the
anchor. That is why the identical `awk` line is **correct** at `check-eval-codes.sh:31` (anchor
`#### 5.7.1`, depth 4) and **wrong** at `check-type-strings.sh:36` (anchor `### 5.8`, depth 3 —
over-terminates by one level).

**ALL consumers, enumerated by mechanism (v1 had two; there are at least seven, in three
languages and three tie-break styles):**

| Consumer | Anchor depth | Correct today? |
|---|---|---|
| `check-type-strings.sh:36` | 3 | **NO — over-terminates** |
| `check-eval-codes.sh:31` | 4 | **YES — and a repair MUST NOT change its behaviour** |
| `check-vendor-honesty.sh:306` (§13) | 2 | measure |
| `check-vendor-honesty.sh:351` (`sec2`, §2) | 2 | measure |
| **`check-vendor-honesty.sh:365` (`table_sha`, §2)** | 2 | **measure — THIS FEEDS THE HASH JOHN'S D-008(3) CERTIFICATION IS PINNED TO** |
| `check-vendor-honesty.sh:269` (`V3-N2`, no extraction at all) | — | **NO — whole-document** |
| **`verifier/test_verifier.py:930`** | — | **Python, `str.split("### 5.8 …")[1].split("---")[0]` — a THIRD idiom with an OPPOSITE tie-break (terminates on `---`, not a heading). Owned by nobody in v1** |

**F13 FIX — THE SUCCESS CONDITION v1 GOT BACKWARDS.** v1 required a deeper subheading to produce a
**refusal**. For `check-eval-codes.sh` a `##### 5.7.1.1` correctly stays **inside** and the guard
**correctly** exits 0. **v1 would have forced a correct guard to refuse a legitimate subsection.**
**Corrected requirement:** a deeper heading is **INSIDE** (guard unchanged); a same-or-shallower
heading **ENDS** the section. Per consumer, both directions get a falsification and a control.

**The crux control (`C2`, and it is the strongest evidence this cycle produced):** at base SHA a
duplicate under `### ` (genuinely OUTSIDE §5.8) and under `#### ` (genuinely INSIDE) produce
**byte-identical output**. **After repair they must differ.** If they still match, the repair
observes nothing.

**Also required (widening direction, which v1 never falsified):** demoting `## 6.` extends
§5.7.1's extent 35→62 lines and the guard still certifies. **Fail-open in the widening direction,
and depth-awareness alone does not close it** — a bounded extent must also be asserted.

### A-R4 — uniqueness of a normative publication (fixes F19-part)

**Guarantee, TWO substrates, deliberately not one primitive (D-059(8)):**
**(a) Markdown** — exactly one normative publication of a value inside a named section.
**(b) SOURCE FILES — no sections, no headings** — exactly one authoritative definition.

Consumers of (b): `check-type-strings.sh:66` (`src_line`, bare `head -1` over `eip712.ts`) and
`check-suite-floors.sh:15` (`get()`, `head -1` over `test.sh`).

**Controls:** a legitimate backticked prose **mention** inside a section is **not** a second
publication and must not be flagged — this control passes today and must keep passing.

### A-R5 — identifier membership must be word-bounded (fixes F13)

**SEPARATED FROM SECTION EXTRACTION ENTIRELY, because it is not a section problem.** This is the
audit's defining finding: **`C1` survives all four of v1's A-P2a falsifications**, so an
implementer satisfying v1 exactly would have left `C1` live with the success condition met.

**Guarantee:** *A guard asserting that an identifier is documented must match it WORD-BOUNDED, so
a strict prefix of a documented identifier is not certified as documented.*

**Falsification:** rename `EVAL_SIM_STOP_IMPERSONATION_FAILED` → `…_FAILE` consistently across
engine and test — a code occurring **zero** times in the proposal. At base SHA:
`check-eval-codes.sh 41/41 exit 0`, class-coverage exit 0, TS 121/121.
**Control:** the non-prefix `…_FAILEX` **is** caught (exit 1), and the same truncation on
`EVAL_ACTION_DEADLINE` **is** caught by class-coverage — both instruments are live.
**Scope note:** only **2 of 41** codes sit outside class-coverage's map; that is the unprotected
set and the repair must state it.

### A-R6 — floor constants (fixes F6, F7, and carries the ordering constraint)

**Guarantee (D-059(2)):** *floors are single-sourced across **all six** constants; reader-facing
prose does not duplicate live values; where displayed, values are derived mechanically.*

**ORDERING CONSTRAINT — `C3` FIRST.** `C3` **breaks A-R6's own falsification method**: `head -1`
is first-wins while bash is last-wins, so with a shadowed duplicate **mutating one copy moves
nothing**, and a test author would read that stillness as proof the surfaces are bound. **Repair
`C3` before authoring A-R6's falsification.** (Verified: duplicate-after → reader 78 / enforced
999; duplicate-before → reader 999 / enforced 78; single definition → agree.)

**Live surfaces (paragraph-normalized; a line-oriented grep is DISALLOWED here per D-058(6)):**
`session-state.md` §3 (~`:365`); `session-state.md:470`; `scripts/test.sh`'s COVERAGE heredoc
(**four** stale figures — `180`, `160`, `77`, `29` — across two sentences, and its own sentence
*"They are corrected here"* is false); **`session-state.md:772`'s table row restating the
single-sourcing claim (F6 — outside every batch in v1)**; and **two live surfaces asserting the
Foundry/TypeScript floors do not exist (F7), which are false since A-075 and have no disposition
in v1 — the test author enumerates and dispositions them.**

**Historical controls that must NOT be flagged:** `round-six-brief.md:28` under its own
"VERIFY IT YOURSELF" heading; `verifier/REPORT.md`'s dated "Results after X" figures; dated
`decisions.md` entries.

### A-G1 — gate wiring (fixes F15, F16)

**D-059(7):** *"A standalone script that nothing invokes repeats the defect this work is trying to
close."*

1. **Invoked by the applicable fast AND deep gate paths**, named in `scripts/test.sh`.
2. **A TOP-LEVEL falsification: the GATE fails** — its output carries the failure and the run does
   **not** print its completion token. Not merely the standalone script failing.
3. **An unchanged control: the real gate still passes**, emitting `GATE PASSED` and its token.
4. **An explicit scope statement** in output and header: covers only its enumerated canonical
   facts; **is NOT general prose-consistency evidence.**
5. **F15 FIX — close the standing instance of this very defect.** `check-suite-floors.sh` is today
   exactly the thing (1) forbids: invoked by **no** script. **Either wire it or record an argued
   exemption. v1 required the rule and left its own live counter-example standing.**
6. **F16 FIX —** `session-state.md`'s live "which scripts the gate runs" table (~`:772`) must be
   updated in the same change, or it becomes false the moment wiring changes.

---

## 4. BATCH B — vault event evidence

Unchanged from v1 and **verified live by the auditor**: `(viaOverride && false)` → **92/92
SURVIVES**; control `(viaOverride || true)` → **91/92 caught**. Eight events, eight emit sites, two
entry points; `ActionExecuted` the only path-discriminating field, reached at `:238` (`false`) and
`:281` (`true`).

**Compiling mutants only (D-058(8)B).** A compile failure, a `deny = "warnings"` failure, or a log
retained only by `vm.recordLogs` is **not** a caught behavioural mutation.

**`F7-R1` wording — NOT ACCEPTED, and v1's candidate was rejected on evidence.** *"if and only if
the action executed"* is **false in the "if" direction**: the vault frame can complete, the
external call succeed, and **an outer frame revert** — the action executed, the transaction is
discarded, no event. **D-059(9) assigns verification to the Batch B test author**, who checks any
candidate against every successful and reverted route. Three facts the repair must preserve:
`OverrideAuthorized` records an override **consumed in a successful transaction**; a reverted
transaction exposes **no durable vault event**; `vm.recordLogs` output from reverted frames is
**not on-chain evidence**.

## 5. BATCH C — signer state machine

Unchanged and **verified live by the auditor**: B3 mutation → **527/527 SURVIVES**; B1 control →
**526/527 caught**. Five states (B0 init, B1 before-reads, B2 head-moved, B3
confirmation-pending, B4 exhaustion, B5 success), **including the mixed combinations across five
attempts**, where a single boolean makes the reported condition wrong for the attempts that
issued reads.

## 6. BATCH D — maintained claims

- **D-F1 — `R2-F4`. ONE live site** (re-enumerated under D-059(6), not forced to two):
  `exit-criterion-packet.md:211` §7. **Three controls must stay unflagged:** §3b's corrected copy,
  §13.7's narrowed-and-**true** `description` claim, and the dated historical entries.
  **F5 fix: v1 asserted completeness between its two sites; the enumeration is re-derived here and
  claims only what the paragraph-normalized sweep covered.**
- **D-F2 — the accepted-limit derivation.** `D-09` is in **both** sets — (c) fixed, (a),(b)
  accepted — so wholly-removed entries are **four**, and ten minus four is six. Repairs: the
  derivation that computes to five; `:548`'s false "FIVE OF THESE TEN"; the third copy at
  `session-state.md:152`. **F12 fix: the third site is material a source deliberately preserved —
  the test author states a disposition distinguishing it from D-F2's own historical control rather
  than editing it by default.**
- **D-F3 — REMOVED** (D-059(5)); Batch A owns the floor passages.
- **D-F4 — `N-EVAL-ACTION-TARGET`** (comment-only, cosmetic) and **`N-DECODE-E4`**: *"nor the
  verifier"* FALSE; ***"NEITHER the signer" TRUE and DELIBERATE (D-014) — MUST NOT be
  "repaired"***; *"Both are open"* FALSE.
- **D-F6 — `C5`, NEW OWNER (F10 fix; owned by nobody in v1).** Two runs differing only in the
  condition produce **byte-identical signed refusals**; a grep for "detail" returns **only the two
  comment lines making the claim**. The **code** claim is true; the **detail** claim is false.
  Sites: the `protocol.ts` comment and A-077's entry — **the latter is a dated historical entry
  and takes a supersession note, not a rewrite (D-059(6)).**
- **D-F5 — claim-side USE of the A-G1 guard. Batch D builds no checker.**

## 7. FALSIFICATIONS vs CONTROLS (fixes F14)

v1 labelled as "falsifications" several probes that **already refuse at base SHA** — they are
**controls**, and calling them falsifications would let an implementer claim a pass for behaviour
that never changed. Corrected:

| Probe | v1 called it | It actually is |
|---|---|---|
| `git ls-files` fails (`check-review-scope.sh:106`) | falsification | **CONTROL — already refuses** |
| `git ls-files` empty (`:114`) | falsification | **CONTROL — already refuses** |
| Section absent, `check-eval-codes.sh` | falsification | **CONTROL — already exits 1** |
| Code only under `## 6.` | falsification | **CONTROL — already exits 1** |
| Batch B item 3 (parts) | falsification | **mixed — split per event** |
| `git ls-files --error-unmatch` fails (`:198`) | falsification | **TRUE FALSIFICATION — survives** |

**Rule for the test author: a probe that already produces the desired behaviour at base SHA is a
CONTROL. Only a probe that passes at base SHA and must fail after repair is a falsification.**

## 8. OUTSIDE EVERY BATCH — returns to John

1. **The C6d fork** — caller-relative vs script-relative root semantics.
2. **The OFFERED signed-text correction** at `:284`.
3. **Gate 5's status** — held, not reopened.
4. **The default-mode secrets discriminator**, if none proves to exist.
5. **Whether the "no floors exist" claims (F7) are repaired now or adjudicated as new findings.**
6. **`check-label-integrity.sh:63`**, `check-vendor-honesty.sh:352`, and four citation offsets —
   recorded residuals, no disposition claimed.
