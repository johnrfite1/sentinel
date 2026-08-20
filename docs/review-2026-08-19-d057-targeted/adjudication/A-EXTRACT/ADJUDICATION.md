# Adjudication — the three defect classes newly exposed by the A-EXTRACT test contract

**Independent adjudicator. Classification only — no repair is proposed, designed, or made.**
This instance authored no A-EXTRACT test, no harness, and no production code under review.

**Adjudicated at:** `ca49f1852aaa73c2a094597c06e16d19115254f9`, branch `step-3/isolated-signer`.
**The card's demonstrated base:** `bb664c626d592d86391f644bf014e76f2bbf7db4`.
`git diff --stat bb664c6 ca49f18 -- scripts/check-type-strings.sh scripts/check-eval-codes.sh
scripts/check-vendor-honesty.sh verifier/test_verifier.py Sentinel_Protocol_Lab_Proposal_v0_2.md
ts/src/signer/eip712.ts docs/ablation-report.md` is **empty**, so probes run at `ca49f18` speak
to the tree the card measured. Line numbers below are `ca49f18`'s.

**Authority read before deciding:** `A-081` (for `R4-F3`), `D-058(6)`, `D-058(7)`, `D-058(8)`,
`D-059(1)`, `D-059(2)`, `D-059(4)`, `D-059(8)`, `D-060`, `D-062`, `D-063`, `D-064`, `A-085`,
`A-086`; `NEW-FINDINGS.tsv`; `VERDICT-LEDGER.tsv`;
`adjudication/new-findings/ADJUDICATED-NEW-FINDINGS.md`; `adjudication/round2/ADJ3.md`;
the A-EXTRACT `CARD.md`, `COVERAGE.md` and `RESULTS.md`; `session-state.md` §0.

**What this document does NOT do, stated first.** Gate 5's signed `§2` text in
`docs/gate-s2-evidence.md` and its certified pin are not read for change, quoted for correction,
re-hashed, or proposed for amendment. No certification is revoked, reaffirmed, or recertified
(`D-059(1)`). Batch A1 is CLOSED and nothing here reopens it. Floors, vault events, signer
state, maintained-claim repairs, signed text, `D-055`, `D-016` and publication are untouched and
unrecommended. **No severity here authorises a repair; `D-058(9)`'s attempt budget is unspent.**

**Every verdict below was reproduced from the tree by this adjudicator's own probes, not read
off `RESULTS.md`.** Where a probe agrees with `RESULTS.md` that is stated; where it goes beyond
it, that is stated too, and one probe (`AX-3` case `C`) found a direction `RESULTS.md` does not
record.

---

## 1. Verdicts — one row per class

| id | Class | Classification | Severity | Boundary | Duplicates / sibling of |
|---|---|---|---|---|---|
| **AX-1** | the exact section-anchor lookup is first-match and accepts an earlier decoy heading | **CONFIRMED** | **MEDIUM** | **INSIDE** | sibling in genus of `C1`, `C2`, `R4-F3` — **covered by none of their remedies** |
| **AX-2** | the authoritative SOURCE-definition lookup does not require uniqueness | **DUPLICATE** | carried from `R4-F3`; no new severity assigned | **INSIDE** | **`R4-F3` — this IS `R4-F3`'s confirmed, unrepaired residual** |
| **AX-3** | the `§7.2` caveat comparison is line-oriented on the proposal side | **CONFIRMED** | **MEDIUM** | **INSIDE** | sibling of `V3-N2`, same line — **neither remedy covers the other** |

**Counts are derived from `ADJUDICATED.tsv`, one row per class, and are not restated here as a
second hand count (`D-057(1)`).**

**No class is REFUTED and none is OUT OF SCOPE.** All three fall inside the A-EXTRACT declared
boundary — the section-extraction, exact-membership and uniqueness blocks of
`scripts/check-type-strings.sh`, `scripts/check-eval-codes.sh`, `scripts/check-vendor-honesty.sh`
and `verifier/test_verifier.py`'s `§5.8` consumer — and nothing outside it was probed or judged.

**No class carries a live false claim at `ca49f18`.** Measured, not assumed:
`grep -c '^### 5\.8 '` = 1, `grep -c '^#### 5\.7\.1 '` = 1, `grep -c '^### 7\.2 '` = 1 in the
proposal; the source defines each of the six type strings exactly once; and all three consumers
report success on an unmutated snapshot. **These are instrument defects, and the distinction is
recorded rather than blurred.**

---

## 2. Method, and how to re-run any probe here

Every probe ran against a private `git archive ca49f18` extraction under a scratch directory
outside the repository, re-initialised as its own git repository, with `HOME`,
`XDG_CONFIG_HOME`, `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` redirected into the scratch area
and `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE`/`GIT_COMMON_DIR`/`GIT_PREFIX` cleared. Below,
`$SNAP` is that extraction's root; nothing in the recipes depends on where it sits. `/usr/bin/grep`
was used throughout, because this machine's `grep` is a wrapper honouring `--ignore-files` whose
zero reads exactly like a clean sweep (`A-081(3)`).

**The baseline control, run first and again after every restore:**

```
$SNAP $ ./scripts/check-type-strings.sh
type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)          rc=0
$SNAP $ ./scripts/check-eval-codes.sh
eval codes: 41/41 engine checks documented in §5.7.1 (D-031)                 rc=0
$SNAP $ ./scripts/check-vendor-honesty.sh | grep caveat
  ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it
```

**Every falsification below carries its own proof-of-mutation count and its own opposite-outcome
control.** `session-state.md` §0: *a falsification probe can be dead, and its silence reads
exactly like a pass* — so each probe states what it MOVED before what it implies. The live
repository was verified clean before and after; the snapshot was verified byte-restored at the
end (`git status --porcelain` empty in both).

---

## 3. `AX-1` — the section anchor is taken first-match, and a duplicate anchor is never detected

### 3.1 The code

`scripts/check-type-strings.sh:54`

```
awk '/^### 5\.8 /{f=1;next} f && /^#{1,4} /{exit} f' "$SPEC" > "$SPEC_SECTION"
```

`scripts/check-eval-codes.sh:49` is the same shape at `/^#### 5\.7\.1 /`. Both set the flag at an
anchor match and exit at the next heading. **Neither ever asks whether a second anchor exists.**
`verifier/test_verifier.py:930` carries the same property in Python:
`text.split("### 5.8 EIP-712 Type Strings")[1]` is the segment after the FIRST occurrence.

### 3.2 Probe `AX-1/TS` — and its control first

**Control `AX-1/TS-ctl` (no duplicate anchor).** Transpose `address principal,address vault` to
`address vault,address principal` in the one indented `MandatePayload(…)` publication inside the
real `§5.8`. Proof of mutation: `'^### 5.8 '` anchors = 1, transposed publications = 1.

```
type strings: DRIFT in MandatePayload
  spec  : MandatePayload(…,bytes32 mandateId,address vault,address principal,…)
  source: MandatePayload(…,bytes32 mandateId,address principal,address vault,…)
  A published type string that disagrees with the code is a confident wrong answer:
  a wrong type string and an invalid signature are indistinguishable at the output.
rc=1
```

**The instrument moves.** The transposition alone IS reported.

**Probe `AX-1/TS`.** Keep that transposition; additionally insert, immediately before
`### 5.9 Enumerations (normative)` (line 468 — *earlier in the file than `§5.8` at line 486,
because this document's section order is not monotonic*), a complete decoy section headed
`### 5.8 EIP-712 Type Strings (normative)` carrying the six **correct** publication lines.
Proof of mutation: anchors now at lines **468 and 500**; correct `MandatePayload` publications
= 1; transposed publications = 1, at line **512**, i.e. inside the real `§5.8`.

```
$SNAP $ ./scripts/check-type-strings.sh
type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)
rc=0
```

**A real transposition inside the real `§5.8` is certified as `6/6 … match … exactly`, exit 0.**
This reproduces `RESULTS.md` case `4d` independently.

### 3.3 Probe `AX-1/EC` — the same shape at `§5.7.1`

**Control `AX-1/EC-ctl`.** Rename `EVAL_ACTION_DEADLINE` out of the real `§5.7.1` with no decoy.
Proof of mutation: anchors = 1, occurrences of the token in the whole file = 0.

```
eval codes: 1 check(s) declared by the engine and absent from §5.7.1:
    EVAL_ACTION_DEADLINE
  Add them to §5.7.1 with a description. Do NOT remove them from the engine to pass.
rc=1
```

**Probe `AX-1/EC`.** Same rename, plus a complete decoy `#### 5.7.1` section carrying the
original body planted before `### 5.9`. Proof of mutation: anchors at lines **468 and 608**;
occurrences of the token inside the REAL (second) `§5.7.1` = **0**; inside the DECOY = **1**.

```
$SNAP $ ./scripts/check-eval-codes.sh
eval codes: 41/41 engine checks documented in §5.7.1 (D-031)
rc=0
```

### 3.4 Probe `AX-1/VP` — the third consumer carries it too

The verifier's own extraction expression, evaluated verbatim against the `AX-1/TS` fixture:

```
MandatePayload the verifier consumer would read:
  MandatePayload(uint16 schemaVersion,bytes32 mandateId,address principal,address vault,…
ordering: principal,vault  (the DECOY's correct copy)
```

**Three of the four declared consumers carry the defect.** `check-vendor-honesty.sh` is not
implicated here: its `§7.2` block has no anchor extraction at all, which is `V3-N2`.

### 3.5 Why this is not `C2`, and not `C1` — demonstrated, not argued

`ADJ3` established `C2` (fixed-depth `#{1,4}` terminator truncating `§5.8`) and `C1` (unanchored
`grep -q` membership) as CONFIRMED and distinct. **`AX-1` survives both of their remedies.**

**Against `C2`'s remedy — a depth-aware terminator derived from the anchor.** Run the shipped
`awk` and a depth-aware `awk` (`/^#{1,3} /`, correct for a `###` anchor) over the same `AX-1/TS`
fixture:

```
shipped awk (fixed #{1,4}) :   MandatePayload(…,address principal,address vault
DEPTH-AWARE awk (#{1,3})   :   MandatePayload(…,address principal,address vault
```

**Byte-identical, and both are the DECOY's copy.** A perfect `C2` repair reads the wrong section
just as confidently. `C2` is about where a section ENDS; `AX-1` is about which section BEGINS.

**Against `C1`'s remedy — exact, word-anchored membership.** The `AX-1/EC` fixture uses the
**exact** token with no prefix or superstring trick at all:

```
extracted section is the DECOY (36 lines); grep -qw EVAL_ACTION_DEADLINE -> FOUND
the REAL §5.7.1 contains it -> NO
```

A `C1`-repaired guard still reports `41/41`. `C1`'s input is *already* `§5.7.1` — `ADJ3` §1.6(i)
proved that scoping live — and `AX-1` attacks **which** `§5.7.1` that is.

**Against `R4-F3`.** `R4-F3` as originally confirmed was **over**-scoping: the guard read the
whole 84 KB and claimed `§5.8`. Its remedy — the `awk` scoping — is **in place and is exactly
what `AX-1` defeats**. Like `C2` under `ADJ3` §2.6(2), `AX-1` is a defect **in** that repair,
introduced by it, and it did not exist before the extraction did. `R4-F3`'s still-open residual
is `AX-2` below, on the other operand; discharging it does not touch the `§5.8` anchor.

### 3.6 The counter-argument, and why it is rejected

**The counter-argument:** *`RESULTS.md` itself says this is "the same first-match class `V3-N2`
names, at the anchor rather than at the value". First-match-take-`head -1` is one genus, it has
been filed three times already as `R4-F3`, `C1`/`C2` and `V3-N2`, and a fourth id for the same
genus is precisely the inflation this project treats as a defect.*

**Why it is rejected: sharing a genus is not sharing a mechanism, and the test that decides it is
whether the existing remedies discharge it.** I ran that test three times above and the answer
was no in every case — a depth-aware terminator, an exactly-anchored membership operator, and a
duplicate-refused SOURCE operand each leave `AX-1` producing `6/6 … match … exactly` over a real
transposition. This is the standard `ADJ3` applied to `C2` and `C1` and I am applying it
unchanged. The opposite error is the one that matters here: filing `AX-1` under an existing id
would let an implementer discharge that id in full and ship a guard that still certifies the
wrong section, with nothing in the repository recording the gap.

**A second thing `AX-1` defeats, which no existing finding covers.** `D-057(5)` added the
`spec_hits` duplicate-publication refusal at `:75–82`. Under `AX-1` that refusal never fires: the
two conflicting publications live in two different `§5.8` sections and only the first is ever
extracted, so each section publishes each type exactly once. **`AX-1` disarms a mitigation by
satisfying it.**

### 3.7 Severity — **MEDIUM**, and the reasoning both ways

**Why not LOW.**
- Both shell consumers are invoked by the product gate (`scripts/test.sh:235` and `:238`), so
  their verdicts are load-bearing rather than advisory.
- The output shape is this guard's most confident: `6/6 … published in §5.8 match eip712.ts
  exactly (D-023)` at exit 0. The guard's own header calls a published-but-drifted type string
  *"worse than an absent one"*.
- It defeats **two** separately-installed mitigations at once — `R4-F3`'s scoping and
  `D-057(5)`'s duplicate refusal.
- Three of the four declared consumers carry it, including the Python one, so the cross-consumer
  agreement the card's case 13 relies on does not catch it either.
- Nothing in the repository observes anchor ambiguity: the guards do not count anchors, and no
  test asserts there is one.

**Why not HIGH — and this is a restraint the evidence forced, not a courtesy.**
- No live false claim at `ca49f18`: one anchor each, counted mechanically.
- The fail-OPEN direction needs a **deliberate two-part construction**: a complete, well-formed
  duplicate section carrying the **correct** values, placed earlier, *plus* a divergence in the
  real section. That is not an ordinary editorial act.
- I probed the ordinary editorial act specifically, because if it fired the severity would rise.
  Inserting a fenced quotation of the heading — `` ```markdown `` / `### 5.8 EIP-712 Type Strings
  (normative)` / `` ``` `` — earlier in the file, alongside the transposition, gives:

  ```
  type strings: §5.8 does not publish EIP712Domain
  type strings: §5.8 does not publish MandatePayload
  … (six refusals) …                                                        rc=1
  ```

  **It fails CLOSED, loudly.** The cheap, conventional, review-invisible trigger that raised
  `C2` to MEDIUM has no fail-open analogue here. That bounds `AX-1` below `C2`'s trigger cost
  even though its consequence is worse, and MEDIUM is where those meet.

---

## 4. `AX-2` — the SOURCE operand takes `head -1` with no uniqueness test

### 4.1 The code, and the comment that declares the property for both operands

`scripts/check-type-strings.sh:68–84`, quoted because the exact text is load-bearing:

```
    # The spec publishes each as an indented literal line; the source as a quoted string.
    # EXACTLY ONE PUBLICATION PER TYPE, not the first of several (R4-F3 residual, D-057(5)).
    …
    spec_hits="$(grep -cE "^ {4}${name}\([^)]*\)$" "$SPEC_SECTION")"
    if [ "$spec_hits" -gt 1 ]; then
        …  Refusing to pick one. Remove the duplicate.
    fi
    spec_line="$(grep -oE "^ {4}${name}\([^)]*\)$" "$SPEC_SECTION" | head -1 | sed 's/^ *//')"
    src_line="$(grep -oE "\"${name}\([^\"]*\)\"" "$SRC" | head -1 | sed 's/^"//; s/"$//')"
```

The comment names both operands and declares one property. The refusal is implemented for one.

### 4.2 Probes, both orders, with the control

**Control `AX-2-ctl`** — pristine source, one definition per type: `6/6 … exactly`, rc=0.

**`AX-2-after`** — a second, transposed `"MandatePayload(…)"` definition inserted AFTER the real
one. Proof of mutation: definitions = 2, correct-order = 1, transposed = 1.

```
$SNAP $ ./scripts/check-type-strings.sh
type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)
rc=0
```

**A silent false pass.** The specification and the source now disagree about what the signer
hashes, and the guard certifies agreement.

**`AX-2-before`** — the same decoy inserted BEFORE the real definition. Proof of mutation:
definitions = 2, transposed at line 105, real at line 106.

```
type strings: DRIFT in MandatePayload
  spec  : MandatePayload(…,address principal,address vault,…)
  source: MandatePayload(…,address vault,address principal,…)
rc=1
```

**Non-zero, for the wrong reason.** The finding is a duplicate definition; the guard reports
drift and points the reader at the specification. Per `session-state.md` §0 — *a check can be
caught by the wrong check* — a generic non-zero exit is not a caught defect. **This refines
`R4-F3`; it does not add a second one.**

### 4.3 **Is this the same class as `R4-F3`? YES — plainly, and it is `R4-F3` itself**

This is the question the task singles out, so here is the evidence that decided it rather than a
characterisation.

**(a) `A-081`'s own words for `R4-F3` describe this and nothing else.**

> `R4-F3`: the duplicate refusal was added to the SPEC operand and not to the SOURCE operand one
> line below, under a comment declaring the property for both; the assigned intra-section
> obligation itself HOLDS.

`spec_hits` at `:75–82`; `src_line` at `:84` — **one line below** `spec_line`; the comment at
`:68–69` declaring the property **for both**. Every clause matches the code I probed.

**(b) `ADJ3` §2.6(3) names the same line as `R4-F3`'s residual, by file and offset.**

> That residual is the **source** operand at `:66` — a bare `head -1` over
> `ts/src/signer/eip712.ts` with neither scoping nor duplicate refusal.

`:66` is that line's number at `c8d15a7`, the SHA `ADJ3` worked from. It is `:84` at `ca49f18`
only because the repository-identity preamble grew. **Verified byte-identical, not assumed:**

```
$ git show c8d15a7:scripts/check-type-strings.sh | sed -n '66p' | shasum -a 256
fa6d2c48daa869dea0e4e447236de02dea4371957fc997004d979452bd9fef9e
$ sed -n '84p' scripts/check-type-strings.sh | shasum -a 256
fa6d2c48daa869dea0e4e447236de02dea4371957fc997004d979452bd9fef9e

$ git show c8d15a7:scripts/check-type-strings.sh | sed -n '48,66p' | shasum -a 256
3d30996c36b7f287726501526e4a6a343a56b9d4a5f9d464f976e7a3479d32e6
$ sed -n '66,84p' scripts/check-type-strings.sh | shasum -a 256
3d30996c36b7f287726501526e4a6a343a56b9d4a5f9d464f976e7a3479d32e6
```

**The entire block `R4-F3` was verified FAIL against is byte-identical at `ca49f18`.**

**(c) `VERDICT-LEDGER.tsv` already carries it as a confirmed, adjudicator-reproduced failure.**

```
R4-F3	V3	FAIL	reproduced	repair
```

**(d) `D-058(8)`'s Batch A already assigns exactly this repair:** *"`R4-F3` BOTH operands and
every exact-section extraction sibling"*. **BOTH operands** is this obligation, by name.

**Verdict: DUPLICATE of `R4-F3`.** No new id is created and no new severity is assigned; the
obligation already exists, is already confirmed FAIL, and is already owned by Batch A. **What
A-EXTRACT contributes here is a demonstrated falsifying test for an obligation that previously
had a prose description — which is what `D-058(1)` asks a test author to produce, and is not a
second defect.** Recording it as one would inflate one defect into two, and by this project's
own terms that is itself a defect.

### 4.4 The counter-argument, and why it is rejected

**The counter-argument:** *A-EXTRACT establishes something `R4-F3` never did — that `6before`
exits non-zero for the WRONG reason, naming DRIFT where the defect is a duplicate definition. A
wrong diagnosis is a distinct property from a missing refusal, and `ADJ3` itself split `C2` off
`R4-F3` on a comparably fine distinction.*

**Why it is rejected.** `ADJ3` split `C2` off on a test it stated and met: *discharging `R4-F3`'s
named residual does not fix `C2`*. Run that same test here and it fails immediately — adding the
duplicate refusal to the SOURCE operand removes the misdiagnosis **as a side effect of the same
one-line change**, because the misdiagnosis exists only in the window between "two definitions
present" and "no refusal raised". There is no repair that discharges `R4-F3` and leaves the
misdiagnosis standing. That is the definition of one defect, not two. The misdiagnosis is
evidence about `R4-F3`'s severity and about why exit status is not a discriminator — both worth
recording, neither a second finding.

---

## 5. `AX-3` — the `§7.2` caveat is compared line-by-line on the proposal side

### 5.1 The code

`scripts/check-vendor-honesty.sh:285–298`

```
norm() { tr '\n' ' ' <"$1" | tr -s ' '; }

CAVEAT="$(grep -F 'is not evidence that current vendors miss Case 3' "$PROPOSAL" | head -1 | sed …)"
if [ -z "$CAVEAT" ]; then
    echo "  FAIL  §7.2's caveat is missing from $PROPOSAL, so there is nothing to enforce"
elif norm docs/ablation-report.md | grep -qF "$CAVEAT"; then
    echo "  ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it"
```

`norm()` is applied to the ablation report and **not** to the proposal. The proposal side is a
line-oriented `grep -F` over a Markdown paragraph.

### 5.2 Probe `AX-3/A` — the false-failure direction

Hard-wrap `§7.2`'s caveat so the anchor phrase straddles the break — a pure reflow, no wording
change. Proof of mutation: **line-oriented hits in the proposal = 0; paragraph-normalized hits
= 1.**

```
$SNAP $ ./scripts/check-vendor-honesty.sh
  FAIL  §7.2's caveat is missing from Sentinel_Protocol_Lab_Proposal_v0_2.md,
        so there is nothing to enforce
```

**The sentence is present and the guard announces it does not exist.** Reproduces `RESULTS.md`
case `11b`.

### 5.3 Control `AX-3/ctl-report` — the defect is located on the proposal side

Restore the proposal; re-wrap the **report's** copy of the same sentence instead. Proof of
mutation: the report's line breaks moved.

```
  ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it
```

**Tolerated — because `norm()` covers that side.** The asymmetry is the defect, exactly.

### 5.4 Probe `AX-3/C` — **the false-assurance direction, which `RESULTS.md` does not record**

`RESULTS.md` demonstrates only the false-failure direction. I probed the other one, because
`D-059(1)` turns on whether this guard can produce a false assurance.

Wrap `§7.2`'s caveat **before** the anchor phrase, so line 1 is
`This baseline makes the demo reproducible but` and line 2 is
`is not evidence that current vendors miss Case 3.` — `CAVEAT` is then the tail half only. Then
delete the first half from the ablation report, leaving only the tail. Proof of mutation: the
report no longer carries `This baseline makes the demo reproducible` (paragraph-normalized count
**0**); it does still carry the tail (count **1**).

```
$SNAP $ ./scripts/check-vendor-honesty.sh
  ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it
```

**The report has lost half of the caveat, and the guard certifies it `verbatim, as §7.2 words
it`.** The clause "as §7.2 words it" is false in a second, independent way: not only was the
sentence not located in `§7.2`, only one line of it was ever compared.

### 5.5 Is this a live violation of `D-058(6)`? — yes as a defect; the ruling binds the remedy

`D-058(6)`: *"any Markdown check MUST normalize logical paragraphs across hard line wraps; A
LINE-ORIENTED GREP IS DISALLOWED for this purpose."*

**The defect is live and reproduced.** `AX-3/A` and `AX-3/C` are line-oriented `grep`s over a
Markdown paragraph, failing in both directions, in the block `D-058(6)` was written about — the
ruling's stated cause is `A-081(3)`, where three reviewers hit the wrap trap and two real defects
survived a sweep that reported clean.

**One honest qualification, made rather than blurred.** The block dates from `885b4da`
(2026-08-15); `D-058(6)` was ruled 2026-08-19 at `f68d4d8`. Code written four days before a
ruling is not defiance of it, and I do not characterise it that way. What the ruling does is
**bind the remedy**: `D-058(8)`'s Batch A already owns this block through `V3-N2`, and
`D-058(6)` forecloses any repair of it that leaves a line-oriented comparison in place. That is
the operative consequence, and it does not depend on the semantics of "violation".

### 5.6 Relation to `V3-N2` — **sibling on the same line; neither remedy covers the other**

`V3-N2` as confirmed is the **scoping** half. `D-060(4)`'s ratified correction states it exactly:
*"the contemporaneous guard searched the whole proposal and took its first matching phrase rather
than locating §7.2"*. `AX-3` is the **line-orientation** half. Both live on `:287`. I tested the
implication in both directions rather than asserting independence.

**Does `V3-N2`'s remedy fix `AX-3`? No.** On the `AX-3/A` fixture:

```
a §7.2-SCOPED but still LINE-ORIENTED extraction finds :  0
a §7.2-SCOPED and PARAGRAPH-NORMALIZED extraction finds:  1
```

**Does `AX-3`'s remedy fix `V3-N2`? No.** I reproduced `V3-N2` first, to have ground truth: plant
a decoy sentence carrying the anchor phrase under `## 6.`, leaving `§7.2` and the report correct.
Proof of mutation: anchor-phrase lines at **609** and **677**, with the `§7.2` heading at **665**.

```
$SNAP $ ./scripts/check-vendor-honesty.sh
  FAIL  docs/ablation-report.md no longer carries §7.2's caveat:
        "An earlier draft of this paragraph read: the demo baseline is illustrative and is
        not evidence that current vendors miss Case 3."
```

Then, on that same fixture, a paragraph-normalizing extraction that is still unscoped:

```
first paragraph-normalized match over the WHOLE document:
  'An earlier draft of this paragraph read: the demo baseline is illustrative and i...'
total matching paragraphs: 2
```

**Still the decoy.** Normalizing without scoping leaves `V3-N2` intact.

**Two independent properties on one line — the shape `D-059(8)` insists on keeping apart.** So:
**CONFIRMED**, sibling of `V3-N2`, distinct obligation.

### 5.7 The counter-argument, and why it is rejected

**The counter-argument:** *Same file, same line, same remedy vehicle. Any competent repair of
`V3-N2` rewrites `:287` wholesale — extract `§7.2`, normalize it to logical paragraphs, locate
the caveat — and fixes both in one edit. A second finding for a defect that cannot survive the
first one's repair is bookkeeping, not adjudication.*

**Why it is rejected.** The premise is an assumption about how an implementer will choose to
repair, and `§5.6` above shows the narrow repair — scope to `§7.2`, keep the `grep -F` — is
available, sufficient to discharge `V3-N2` as it is worded in `A-081` and `D-060(4)`, and leaves
`AX-3` fully live. This project's recorded failure mode is precisely *the repair generalised the
demonstration, not the argument* (`A-081(2)`), with `R2-F6` and `R4-F3` as second iterations of
one defect and `R4-F4` a third. Filing `AX-3` under `V3-N2` would rest the outcome on an
implementer voluntarily doing more than the finding asks. `ADJ3`'s formula fits and I am reusing
it: **same remedy vehicle, different obligation.**

### 5.8 Severity — **MEDIUM**, and the reasoning both ways

**Why not LOW.**
- The trigger is the single most ordinary editorial act there is: reflowing one paragraph. Many
  editors do it unprompted. `A-081(3)` records this exact trap firing on three reviewers.
- It fails in **both** directions — a false failure that blames the report or the proposal, and
  a demonstrated false assurance (`AX-3/C`).
- The false assurance is worded `verbatim, as §7.2 words it`, which is a stronger claim than the
  block can support even when it passes correctly.
- The block sits in a `§7.5` Gate 5 supplementary condition and the guard runs in the product
  gate (`scripts/test.sh:252`).

**Why not HIGH.**
- No live false claim at `ca49f18`: the caveat occupies one line, the report carries it, the
  baseline control reports `ok`.
- `D-059(1)` already rules this guard **INADMISSIBLE as evidence** for its supplementary `§7.2`
  condition until repaired and independently reverified. Nothing currently rests on it, which
  caps the present harm — **and that ruling is John's; it is cited here, not reopened.**
- The false-assurance direction needs **two** conditions, not one: the proposal reflowed *and*
  the report losing the half that is no longer compared. By the standard `ADJ3` applied to `C2`,
  a two-condition fail-open with no live false claim is MEDIUM.

---

## 6. What I could not reproduce, named plainly

**Nothing assigned to me failed to reproduce.** All three classes reproduced at `ca49f18`, in
both directions where two directions exist, with every control discriminating. Limits on that
statement, stated rather than left implicit:

- **I did not run `a-extract.sh`.** Every result above is from probes I built, per the
  instruction to classify from the tree rather than from a report. **The consequence is that this
  document does not independently verify the harness's other eleven cases, its 52 controls, or
  its `15 REQUIRED FAIL` total** — those remain the test author's evidence, uncorroborated here.
- **`AX-1/VP` evaluated the verifier consumer's own extraction expression verbatim
  (`verifier/test_verifier.py:930`) rather than executing the test suite.** It establishes what
  the consumer would read; it does not establish which assertion in `TestPublishedTypeStrings`
  fires or how. That narrower claim is what `§3.4` makes.
- **`RESULTS.md` cases `13a`, `13b-before`, `13b-after` and `13d`** — the verifier-side duplicate
  handling and horizontal-rule boundary — were outside my three assigned classes and were not
  probed. They are neither confirmed nor doubted here.
- **One severity input is single-platform.** All probes ran on one platform, one `git`, one
  `python3`, one `awk`, one `bash`. `COVERAGE.md` §2 declares the same limit for the harness.

## 7. Integrity of this adjudication

- **The repository under adjudication was not mutated.** Every fixture was built in a private
  `git archive` extraction outside the repository. `git status --porcelain` in the working
  repository shows only a pre-existing untracked directory under
  `batch-cards/D062-containment-tests/`, which is not mine and which I did not read, write, or
  remove.
- **The snapshot was restored byte-for-byte** after the last probe (`git status --porcelain`
  empty), and the three consumers report their baseline success lines again.
- **No production file, no test, no harness and no existing evidence file was changed by this
  work.** The only files this adjudicator writes are this document and `ADJUDICATED.tsv` beside
  it.
- **`docs/gate-s2-evidence.md` was not opened for change.** Gate 5's certified `§2` table and its
  pinned hash are untouched, unquoted for correction, and unproposed for amendment.
- **`D-058(9)`'s attempt budget is unspent.** Nothing here is a repair, and nothing here
  authorises one to begin.
