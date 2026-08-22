# A-EXTRACT — INDEPENDENT IMPLEMENTATION VERIFICATION

# VERDICT: **HOLD**

The exact implementation candidate `39c7679e7de8136596306c567c8dd3327aca5a25`
holds the frozen A-EXTRACT contract. The immutable fast instrument reports **52/52 REQUIRED**
and **70/70 CONTROL**. Its attempt-one remeasurement reports **51/52 REQUIRED** and **70/70
CONTROL**, with only `10c` failing, and the attempt-two delta is the one line needed to stop a
deeper Markdown heading from being concatenated into the vendor-honesty paragraph stream. The
ordinary fast gate and the required isolated clean-clone deep gate both end in `GATE PASSED`;
the deep run directly executed all three named A-EXTRACT consumers.

This reviewer authored neither the implementation nor the frozen test contract. **HOLD means
only that this exact candidate satisfies the fixed A-EXTRACT contract and the required deep gate
was measured.** It is not product approval, sign-off, certification, ratification, publication,
rename authority, push authority, or a ruling on any held D-008 question.

---

## 0. Identity, authority and immutable inputs

| | |
|---|---|
| Branch | `step-3/isolated-signer` |
| A-088 checkpoint | `76d90586d99d4e5bd224230ba24a948dc2d6dc36` |
| Attempt one | `088f7456fe30665ac9b4038f0deb8f46c0f59631` |
| Exact candidate / attempt two | `39c7679e7de8136596306c567c8dd3327aca5a25` |
| Fast instrument sha256 | `9e489ee6f4adab00535d036619738cf1faa97ec8ab070d22cbf29dd3e769bc1a` |
| Gate instrument sha256 | `da8c15794f4a597bb0ab766f73e50dac87fd4edea62b22d533e4eef313acc4b1` |
| Frozen `TESTS.patch` sha256 | `3780e63a68ba013a085937c5019a837eb02fc4dda0238c21b2bd2074a908442b` |
| Threat model | D-065 faithful measurement in a non-adversarial environment |
| Repository state at start | clean; `HEAD` was the exact candidate |
| Repository writes before this record | none |

I read the workspace instructions; D-058, D-059, D-065, D-066 and A-088; the complete
`CARD.md`, `COVERAGE.md`, `RESULTS.md`, `GATE-BINDING.md`, `TESTS.patch` and
`INSTRUMENT-REVIEW-12.md`; both immutable instruments; all candidate implementation lines; and
the relevant ordinary gate and guard code. The verification bar is the fixed contract in those
records, not a general claim about every Markdown dialect or hostile execution environment.

## 1. Exact scope and two-attempt provenance

From A-088 through the candidate, exactly five allowed implementation surfaces change:

| File | Candidate role |
|---|---|
| `scripts/extract-markdown-section.py` | new shared section extractor for the three shell guards |
| `scripts/check-type-strings.sh` | consumes the shared extractor and applies the §5.8 publication rules |
| `scripts/check-eval-codes.sh` | consumes the shared extractor for §5.7.1 exact-token membership |
| `scripts/check-vendor-honesty.sh` | consumes the shared extractor and normalizes logical paragraphs |
| `verifier/test_verifier.py` | independently implements the verifier-side §5.8 parser |

The A-088-to-candidate diff is 226 insertions and 31 deletions across those five files. No
harness, `TESTS.patch`, suite floor, `scripts/test.sh`, signed evidence, proposal, ablation report,
generator, decision record or prior review changes in that interval.

Attempt one adds the helper and changes the four consumers. Remeasuring that exact commit with
the immutable fast instrument gives **51/52 REQUIRED, 70/70 CONTROL**. The sole REQUIRED miss is
`10c`: a deeper `####` heading inside §7.2 was not treated as a logical-paragraph separator, so
the caveat beneath it was concatenated with the heading text and no longer matched the report.

Attempt two changes exactly one line in `scripts/check-vendor-honesty.sh`:

```awk
/^#{1,6}[[:space:]]/ { flush_paragraph(); next }
```

That line makes headings paragraph boundaries for logical-paragraph normalization without
changing the section extractor's same-or-higher-level section boundary. No third implementation
attempt exists.

## 2. Independent implementation inspection

I inspected every changed implementation line and the immediate call sites.

- All three shell guards invoke `scripts/extract-markdown-section.py`; repository search finds
  no fourth production consumer.
- The helper scans ATX headings outside both backtick and tilde fenced code blocks, requires one
  exact anchor, and ends the section only at a following heading of the same or higher level.
- `verifier/test_verifier.py` neither imports nor refers to that helper. Its section and fence
  handling is an independent Python implementation, while its classification remains local to
  the verifier consumer.
- The type-string guard separately checks section-anchor uniqueness, normative publication
  uniqueness and authoritative source-definition uniqueness. These are not collapsed into one
  count.
- The eval-code guard compares exact identifier tokens inside §5.7.1 rather than substrings or
  whole-document mentions.
- The vendor-honesty guard extracts the named sections, compares normalized logical paragraphs,
  preserves the generated-report check, and leaves the Gate 5 certification boundary intact.
- `bash -n` passes for all three shell guards. Python compilation passes for the helper and
  verifier. The candidate diff passes `git diff --check`.

The Gate 5 table independently hashes to the unchanged live pin
`c9034750e56b8801be7cd31cce33c42caad209013a61ed7082155db33903959c`.
That measurement confirms byte identity only; it does not re-certify the table.

## 3. Immutable fast instrument

I ran the frozen executable directly against each exact commit, with its matrix, run log,
consumer transcript and execution witness directed to a temporary external evidence directory:

```sh
A_EXTRACT_EVIDENCE_DIR="$evidence" \
A_EXTRACT_MATRIX_OUT="$evidence/matrix.tsv" \
docs/review-2026-08-19-d057-targeted/batch-cards/A-EXTRACT-tests/a-extract.sh \
    . <exact-commit>
```

| Subject | REQUIRED | CONTROL | OBSERVED | Result |
|---|---:|---:|---:|---|
| `088f7456fe30665ac9b4038f0deb8f46c0f59631` | 51/52 | 70/70 | 14 | only `10c` FAIL |
| `39c7679e7de8136596306c567c8dd3327aca5a25` | **52/52** | **70/70** | 14 | every scored case held |

The candidate matrix contains 136 unique case IDs and no scored non-pass. Preflight archived all
541 subject blobs and matched the exact candidate tree. Execution witnesses show that every
observed consumer execution used the candidate bytes: type-string guard 26 executions, eval-code
guard 14, vendor-honesty guard 17 and verifier 8. `Z-clean`, `Z-gate5` and `Z-signed` all pass.

The consumer transcript includes Python tracebacks from deliberately malformed negative
fixtures. Those are expected evidence, not silently ignored runtime errors: each affected scored
case checks the required failure class and diagnostic. The instrument's own run log and final
summary are clean.

## 4. Focused and adversarial probes

Focused verifier tests:

```sh
python3 -m unittest -v \
  verifier.test_verifier.TestPublishedTypeStrings \
  verifier.test_verifier.TestPublishedTypeStringsSectionExtent
```

Result: **14/14 PASS**.

The three live consumers also pass directly:

```sh
./scripts/check-type-strings.sh
./scripts/check-eval-codes.sh
./scripts/check-vendor-honesty.sh
```

I then built an independent synthetic document in external scratch and invoked the helper and
verifier parser separately. The probe established all of the following:

- apparent anchors inside a four-backtick fence and a three-tilde fence are ignored;
- deeper headings and a horizontal rule stay within the selected section;
- a following same-depth heading ends it;
- missing and duplicate anchors refuse distinctly;
- a duplicate normative type publication refuses; and
- the independent verifier parser agrees on the selected section without importing the helper.

Result: **PASS**. The probe wrote nothing to the repository.

## 5. Ordinary fast and required isolated deep gate

The ordinary fast profile at the candidate:

```sh
./scripts/test.sh
```

Result: `GATE PASSED`; Foundry **92/92**, TypeScript **527/527**, verifier suite **221**,
samples **7**, tamper **78 cases / 30 modes**. Each of the three A-EXTRACT consumer stages is
green. As documented, this profile skips the corpus and committed-view checks.

For the required deep run, I created an isolated no-hardlink clone, detached it at the exact
candidate, and locally staged dependency working trees at the repository's pinned commits:

- `forge-std` `bf647bd6046f2f7da30d0c2bf435e5c76a780c1b`;
- OpenZeppelin Contracts `5fd1781b1454fd1ef8e722282f86f9293cacf256`;
- the already installed JavaScript dependency tree copied into the isolated clone.

The root clone was clean immediately before the run. I ran, alone:

```sh
./scripts/test.sh --gate
```

Result: **`GATE PASSED`**. The captured output directly contains each required banner exactly
once:

```text
== published EIP-712 type strings (D-023) ==
== §5.7.1 check coverage (D-031) ==
== vendor honesty (§7.5 Gate 5, D-008) ==
```

The deep run also reports Foundry **92/92**, TypeScript **527/527**, corpus **50 fixtures** with
committed views verified file by file, **51 result files identical**, verifier suite **221**,
samples **7**, and tamper **78 cases / 30 modes**. The isolated root worktree remained clean
afterward.

Two earlier scratch setups are deliberately excluded from this evidence: one copied submodule
pointer files rather than staging dependency repositories and was stopped before completion;
another setup aborted before running because a shell-local variable used a reserved zsh name.
Neither produced a scored gate result. The successful run above used a newly constructed third
clone and completed normally.

## 6. Repository, workspace and protected-boundary checks

The following live checks pass at the candidate:

- `./scripts/check-secrets.sh`: clean;
- `./scripts/check-review-scope.sh`: 543/543 then-current files assigned before this record;
  after staging this standalone record, 544/544 assigned (`R1=347`, `R2=46`, `R3=151`);
- `./scripts/check-suite-floors.sh`: 92 / 527 / 221 / 7 / 78 / 30, with `scripts/test.sh` the
  sole copy;
- `./scripts/check-findings-ledger.sh`: D-057 figures agree;
- `./scripts/check-rename-gate.sh`: private and clean;
- `git diff --check`: clean;
- workspace `tools/guards/run_guards.sh Sentinel`: PASS with **13 baselined findings and 0 new**.

The workspace guard is ratcheted: that last PASS does not mean zero findings. The 13 baseline
items remain accepted debt, not newly approved practice.

Direct A-088-to-candidate hash/diff checks show these protected surfaces byte-identical:

| Protected surface | sha256 at A-088 and candidate |
|---|---|
| `Sentinel_Protocol_Lab_Proposal_v0_2.md` | `322cd96fa7daf9840c34f6bf6cc0abd9b1d31a83ccfd5e9babb0f575e20c4124` |
| `docs/ablation-report.md` | `dbcd35e103942d2d16431ec79078e23e7bfeac78de5712e53acf9b0bd81317c0` |
| `docs/gate-s1-evidence.md` | `25dcefcade99e9e45be0c482f3dc5141f4d25335a920fabe1012303c7d7caf68` |
| `docs/gate-s2-evidence.md` | `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589` |
| `scripts/test.sh` | `66c272b90a16b037e3fcfc6f0d9184c48f63ac32e62538be7b6cd96a93801b79` |
| `ts/src/ablation/report.ts` | `dc30b345ae44d1358d07e189f20003012bf7f0c308b9b1c893e795de0de3ce85` |

The two instrument and `TESTS.patch` hashes are recorded in §0. No signed or certified text,
gate material, proposal, report, generator, gate runner or suite floor moved.

## 7. Bounds and remaining uncertainty

This HOLD is deliberately narrower than “a complete Markdown parser”:

- The contract was measured on the documented single platform and toolchain family.
- Per `CARD.md`, indented code blocks, HTML blocks, blockquotes and additional fence-info-string
  variants are outside the probed grammar. No claim is made for them.
- The independent verifier equality arm covers the fixed reason classes in the contract; it is
  not a proof that every future shell and verifier diagnostic taxonomy will stay identical.
- The fast ordinary gate does not exercise the corpus or committed views; the isolated deep gate
  above does.
- No deep mutation run was required: A-088 changes neither `scripts/test.sh` nor its control flow.
  The immutable fast instrument supplies the causal mutation evidence for the consumer repairs;
  the deep run establishes real `--gate` invocation and composition.
- The workspace guard is a baseline ratchet, and its green result must not be read as clearing the
  13 recorded findings.
- D-065 bounds these results to faithful execution. This review makes no hostile-environment or
  compromised-harness claim.

Within those stated bounds, I found no contract failure, scope escape, protected-boundary change,
or unmeasured required gate invocation. **The exact verdict for
`39c7679e7de8136596306c567c8dd3327aca5a25` is HOLD.**
