# A-EXTRACT — the measured pre-repair run at `bb664c6`

**Base SHA:** `bb664c626d592d86391f644bf014e76f2bbf7db4`, tree clean at the time of measurement.
**Harness sha256:** `8031e73284ef68d84d48347aa8c411d2e44a625f93e4ef035d55df660910519d`
(`a-extract.sh`; the harness prints this itself at preflight case `P0`).
**Environment, printed by preflight `P2`:** git 2.50.1 (Apple Git-155); bash 3.2.57; Python
3.9.6; `/usr/bin/grep` with a matched canary.

**Command:**

```
docs/review-2026-08-19-d057-targeted/batch-cards/A-EXTRACT-tests/a-extract.sh
```

**Result — run twice, case-line output byte-identical between runs:**

```
  REQUIRED : 19 of 34 held      (15 REQUIRED failures)
  CONTROL  : 46 of 46 held      (0 control failures)
  exit 1   — REQUIRED FAILURES with every control holding: the defects are observed.
```

**The exit path matters.** Exit 1 is "required cases failed, controls all held". Exit 2 would
mean a control failed and no verdict beside it could be relied on. **Every control held on both
runs**, so the fifteen failures below are findings about the tree, not about the instrument.

---

## 1. Per-case verdict table

`R` = REQUIRED, `C` = CONTROL, `O` = OBSERVED. "Control discriminated" answers: did the paired
opposite outcome actually behave oppositely?

| Case | Kind | Verdict | Consumer | Control discriminated |
|---|:--:|:--:|---|---|
| P0–P6 | O | recorded | — | preflight; `P6` proves the unmutated snapshot passes all three runnable consumers |
| 1-mut | C | PASS | — | heading present once in base, absent in fixture |
| **1a** | R | **PASS** | TS | yes — `1-ctl` reports 6/6 with the section present |
| **1c** | R | **PASS** | VP | yes — `13-ctl` |
| 1c-how | O | recorded | VP | refusal shape is an uncaught `IndexError` |
| 1b-mut | C | PASS | — | |
| **1b** | R | **PASS** | EC | yes — `1-ctl` |
| 1-ctl | C | PASS | TS+EC | the opposite outcome |
| 2-mut | C | PASS | — | 0 exact-token hits, 1 superstring hit |
| **2a** | R | **FAIL** | EC | yes — `2-ctl` names it missing when wholly removed |
| 2b-mut | C | PASS | — | |
| **2b** | R | **PASS** | TS | yes — `2-ctl` |
| 2-ctl | C | PASS | EC | the reporting path is live |
| 3-mut | C | PASS | — | absent inside §5.7.1, present in the document |
| **3a** | R | **PASS** | EC | yes — `1-ctl` |
| 3b-mut | C | PASS | — | moved out of §5.8 into §5.6 |
| **3b** | R | **PASS** | TS | yes — `5-ctl` |
| 4a-mut | C | PASS | — | correct line in §5.9, transposed line in §5.8 |
| **4a** | R | **PASS** | TS | yes — `5-ctl` |
| 4c-mut | C | PASS | — | two complete §5.8 sections |
| **4c** | R | **FAIL** | TS | yes — `5-ctl` |
| 4d-mut | C | PASS | — | first §5.8 correct, real §5.8 transposed |
| **4d** | R | **FAIL** | TS | yes — `4a` shows the same drift IS reported without a decoy anchor |
| 4b-mut | C | PASS | — | only the decoy §5.7.1 documents the code |
| **4b** | R | **FAIL** | EC | yes — `2-ctl`, `3a` |
| 5before-mut / 5after-mut | C | PASS | — | two publications, either order |
| **5before**, **5after** | R | **PASS** | TS | yes — `5-ctl` |
| 5-ctl | C | PASS | TS | the opposite outcome |
| 6before-mut / 6after-mut | C | PASS | — | two definitions, line numbers reported |
| **6before** | R | **FAIL** | TS | yes — `6-ctl` |
| **6after** | R | **FAIL** | TS | yes — `6-ctl` |
| 6-ctl | C | PASS | TS | one definition, success reported |
| 7a-mut | C | PASS | — | 5 publications below the interposed `####` |
| **7a** | R | **FAIL** | TS | yes — `7c` (a `#####` at the same place does NOT truncate) |
| 7c | C | PASS | TS | the depth-paired control |
| **7b** | R | **PASS** | EC | yes — `8c` (a `####` at §5.7.1 DOES end it) |
| 8a-mut … | C | PASS | — | see `8c-mut` |
| **8a**, **8b** | R | **PASS** | TS | yes — `8-ctl` |
| 8c-mut | C | PASS | — | `EVAL_CHAIN_BOUND` above, `EVAL_MANDATE_WINDOW` below |
| **8c**, **8d** | R | **PASS** | EC | yes — `8-ctl` |
| 8-ctl | C | PASS | TS+EC | the opposite outcome |
| 9a-mut | C | PASS | — | the backticked mention is present |
| **9a**, **9b** | R | **PASS** | TS | yes — `9c` refuses the SAME text unbackticked |
| 9c | C | PASS | TS | the opposite outcome |
| 10a-mut | C | PASS | — | decoy at line 608, §7.2 at line 665 |
| **10a** | R | **FAIL** | VH | yes — `10-ctl` reports ok without the decoy |
| 10b-mut | C | PASS | — | §7.2 reworded, report does not carry the new wording |
| **10b** | R | **FAIL** | VH | yes — `11c` FAILs when the report's copy is altered |
| 10-ctl | C | PASS | VH | the opposite outcome |
| **11a** | R | **PASS** | VH | yes — `11c` |
| 11b-mut | C | PASS | — | 0 line-oriented hits, 1 normalized hit |
| **11b** | R | **FAIL** | VH | yes — `11d` (a report-side re-wrap IS tolerated) |
| 11c-mut, 11c | C | PASS | VH | the report-side opposite outcome |
| 11d-mut, 11d | C | PASS | VH | the report-side re-wrap control |
| 11e | O | recorded | — | generator emits the caveat in two halves, 1 + 1 |
| 11f | C | PASS | — | the caveat is generated, not hand-pasted |
| 12suffix-mut, 12prefix-mut | C | PASS | — | 0 exact-token hits, 1 substring hit |
| **12suffix**, **12prefix** | R | **FAIL** | EC | yes — `12-ctl` names it undocumented when replaced by an unrelated token |
| 12-ctl | C | PASS | EC | the opposite outcome |
| **13a** | R | **FAIL** | VP vs TS | yes — `13-ctl` |
| **13b-before** | R | **FAIL** | VP | yes — `13-ctl` |
| **13b-after** | R | **PASS** | VP | yes — `13-ctl` |
| **13d** | R | **FAIL** | VP vs TS | yes — `13-ctl` |
| 13-ctl | C | PASS | VP+TS | both succeed unmutated, so agreement is not vacuous |
| 13-patch | O | recorded | — | the verifier-side half is `TESTS.patch`, NOT applied |
| 14a, 14b, 14c-mut, 14c | C | PASS | VH | `14c` proves the pin is live |
| **14d** | R | **PASS** | — | the live repository still carries the certified value |
| Z-* (5) | C | PASS | — | four consumers byte-identical to `bb664c6`; boundary unmodified |

**Totals:** 46 CONTROL PASS · 19 REQUIRED PASS · **15 REQUIRED FAIL** · 10 OBSERVED.

---

## 2. The fifteen failures, with the output each was asserted on

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
whether a second exists. This is the same first-match class `V3-N2` names, at the anchor rather
than at the value, and it is **not** in `NEW-FINDINGS.tsv` — it is new here. Control `4a` shows
the identical drift IS reported when no duplicate anchor is present.

### 6before / 6after — the SOURCE side has no uniqueness test at all

```
$ ./scripts/check-type-strings.sh        # decoy definition BEFORE the real one (6before)
type strings: DRIFT in MandatePayload
  spec  : MandatePayload(…,address principal,address vault,…)
  source: MandatePayload(…,address vault,address principal,…)

$ ./scripts/check-type-strings.sh        # decoy definition AFTER the real one (6after)
type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)
```

`src_line="$(grep -oE … "$SRC" | head -1 …)"`. The spec side refuses a duplicate publication;
the source side silently takes the first. **`6before` is a non-zero exit for the WRONG reason** —
it names drift where the finding is a duplicate definition, which is exactly why a generic
non-zero exit is not a caught defect. **`6after` is a silent false pass.** This is D-059(8)(b),
and it is **not** in `NEW-FINDINGS.tsv`.

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

### 13a / 13b-before / 13d — the two `§5.8` consumers disagree

| Fixture | `check-type-strings.sh` | `verifier` §5.8 consumer |
|---|---|---|
| `#### 5.8.1` inside §5.8 (13a) | fails — section truncated | **OK** |
| duplicate publication, decoy first (13b-before) | refuses | **OK** — dict keeps the last, which is the real line |
| duplicate publication, decoy second (13b-after) | refuses | fails — dict keeps the decoy |
| `---` inside §5.8 (13d) | 6/6, unaffected | **fails** — `split("---")[0]` truncates |

The Python consumer's extent is `text.split("### 5.8 EIP-712 Type Strings")[1].split("---")[0]`
— a first-match anchor and a horizontal-rule boundary — and its duplicate handling is a dict
assignment, so **the later line silently wins.** `13b-after` passes only because the decoy
happened to be last; the same defect passes and fails depending on fixture order, which is what
makes `13b-before` a real finding rather than a wording quibble.

---

## 3. Cases that already hold — real findings about the tree

**Nineteen REQUIRED assertions passed pre-repair, and that is information, not filler.**

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
- **Gate 5's certified `§2` table and its pinned hash are untouched** (14a–14d).

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
`TestPublishedTypeStringsSectionExtent` to `verifier/test_verifier.py`. Verified against a
throwaway `bb664c6` extraction:

- `git apply --check` — **applies cleanly at `bb664c6`.**
- With it applied to a scratch copy: `TestPublishedTypeStrings` (the two pre-existing tests)
  still **pass**, so the patch changes no behaviour on its own.
- `TestPublishedTypeStringsSectionExtent`: **10 tests, 8 fail** (7 failures + 1 error) and the
  **2 controls pass** — `test_a_well_formed_section_is_read_whole` and
  `test_the_live_proposal_still_publishes_six`.

**The patch is not applied to the repository.** `verifier/` is untouched by this batch.
