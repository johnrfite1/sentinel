# A-FLOORS — corrected frozen independent test contract

**Verdict: HOLD for corrected test-contract readiness only, pending fresh independent Review 2.**
This is not implementation approval, a gate signature, certification, ratification, publication,
rename, D-055 assessment or push authorization.

**Behavioral baseline:** `1a133301533e9d959dbafbbcc7ffe05e7eb78df3` (tree
`07cdc103133525f42b95018fabb802caa7cd8af3`). **Original evidence subject:**
`e8b4d29641c47f0099482c9a9ac5da86c9255197`. Independent review-only commit
`e3b8a76cff7a002b3211bb8f8a75f2d14b86a37e` returned FAIL on two focused stimuli: zero and
standalone indented assignments. This bounded correction changes only this evidence directory.
`INSTRUMENT-REVIEW-1.md` remains byte-identical at sha256
`d07c6358127caba142b0c95adcba6fc33cb5b8eafdbba5c8680382a32d39c82d`.

**Authority:** D-058(1), (2), (6), (8)C and (9); D-059(5), (7) and (8); D-060(1); D-066(2)–(4).
`N-TESTSH-FLOORS` remains a duplicate of `R4-F4`, not a seventh item. C3 supplies the confirmed
reader-first/Bash-last disagreement.

## 1. Declared future implementation surfaces

Completeness is claimed only for this finite inventory:

| Surface | Future obligation |
|---|---|
| `scripts/test.sh` six assignments | Raise `92 → 103` and `527 → 550`; preserve `221/7/78/30`; keep exactly one executable positive-decimal definition per name. |
| `scripts/test.sh` gate body | Invoke the targeted guard exactly once on the common fast/deep path, before suite consumers, accumulating failure so later green stages cannot mask it. |
| quoted COVERAGE D-010 paragraph | Remove hand-maintained live copies of the six facts or display only values derived from canonical assignments; preserve dated history as history. |
| `scripts/check-suite-floors.sh` | Parse all six definitions, apply the exact source/refusal matrix below, and inspect only the three enumerated maintained logical paragraphs. |
| `docs/session-state.md` §3 stable paragraph and D-010 bullet | Remove live hand-maintained floor/count copies while preserving non-floor facts and explicitly dated history. |

There is no production `TESTS.patch`: the directly tracked harnesses are the exact test
instrument. No implementation, current claim or existing script is edited in this correction.

## 2. Six-dimensional value and source contract

| Constant | Planned | Baseline | Measured |
|---|---:|---:|---:|
| `FOUNDRY_MIN_TESTS` | 103 | 92 | 103 |
| `TS_MIN_TESTS` | 550 | 527 | 550 |
| `VERIFIER_MIN_TESTS` | 221 | 221 | 221 |
| `VERIFIER_MIN_SAMPLES` | 7 | 7 | 7 |
| `VERIFIER_MIN_TAMPER` | 78 | 78 | 78 |
| `VERIFIER_MIN_TAMPER_MODES` | 30 | 30 | 30 |

For every name, exactly one executable column-zero assignment with a positive decimal value is
accepted and reported. Refusals must name the constant and exact class:

- absent token → `missing`;
- empty direct value → `empty`;
- whitespace around `=` / non-assignment spelling → `malformed`;
- assigned non-number → `numeric`;
- assigned zero → `positive`; and
- any second executable assignment in the enumerated direct, inline-conditional or standalone
  indented forms → `duplicate`.

An ordinary `NAME=1` control passes for all six constants. The
`VERIFIER_MIN_TAMPER`/`VERIFIER_MIN_TAMPER_MODES` prefix pair remains a non-collision control.

### Executable duplicate matrix

The direct duplicate cases remain in both orders. Their witnesses now observe the legacy
column-zero first-line projection independently from the repaired checker, and compare it with
Bash's final last-wins value; they no longer require a refusing checker to print a value.

Inline conditionals remain their own `DC/DCW` cases. They are not described as indentation.

Standalone indented duplicates have two required placements for every constant:

| Placement | Bash trace | Final Bash value | Why required |
|---|---|---:|---|
| after canonical | planned, then 999 | 999 | the indented assignment actually shadows the floor |
| before canonical | 999, then planned | planned | the extra executable source still exists even though the canonical line later restores the value |

`bash --noprofile --norc -x` must show those exact two assignments in the stated order. A final
value alone cannot prove the before mutation executed. Each placement has a separate CONTROL
witness and REQUIRED named refusal.

For every name, three inert assignment-shaped siblings must remain accepted with the planned Bash
value: an indented comment, a single-quoted `printf` argument, and a body line inside a quoted
heredoc. These 18 controls prevent a broad indentation/token regex from satisfying the contract.

## 3. Causal F1 sibling and satisfying control

The focused harness has two synthetic, test-only variants. Both use the same complete 136-row
matrix and change no shared repository file:

- `digits-zero-sibling` recognizes digits with `[0-9]+`, correctly handles every other frozen
  source/reader/wiring case, and accepts zero. It passes all 81 Review-1 rows, all new F2 rows and
  all 65 controls, but fails exactly the six new `Z-*` rows: REQUIRED 65/71, CONTROL 65/65.
- `exact-positive-control` differs only in using `[1-9][0-9]*`. It passes REQUIRED 71/71 and
  CONTROL 65/65.

Thus zero is causally discriminated from every old stimulus. The satisfying control proves the
new matrix is achievable rather than a permanent red condition. These embedded siblings are
test calibration, not prescribed production structure.

`P-reader-restore` hashes the candidate reader before fixture mutation, restores the untouched
candidate gate/session bytes after all fixture cases, reruns the reader, and requires identical
exit/output and reader hash. Fixture transformation cannot silently substitute a different live
candidate behavior.

## 4. Finite reader-publication contract

The Markdown oracle remains limited to three logical paragraphs:

1. `docs/session-state.md` §3 `**What is stable and worth stating:`;
2. its current `- **D-010 verifier:` list item; and
3. the quoted gate COVERAGE paragraph beginning `  D-010`.

Whitespace is normalized across wraps. Refusal must name the surface, a current-time class and a
publication/derivation reason. Wrapped and unwrapped versions must agree. Dated numeric history
inside the same logical paragraph, constant names without values, and unrelated numbers outside
these roles remain passing controls. This is not a generic prose or number scanner.

## 5. Gate binding and frozen instruments

The seven-case serial gate harness is byte-unchanged at sha256
`fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0`; its matrix is unchanged at
`0b4d9c127e7230c7266960fe073f92f9551da9a68005cb936850993d803d1c58`. F1/F2 alter only focused
source stimuli, not gate semantics, so the expensive gates were not rerun. The prior non-overlap
measurements are retained as historical reliance, not refreshed timing evidence.

| File | Role |
|---|---|
| `a-floors.py` | corrected 71 REQUIRED / 65 CONTROL focused instrument and two causal variants |
| `focused-matrix.tsv` | corrected baseline 136-row score |
| `focused-matrix-review1.tsv` | byte-preserved 81-row Review-1 baseline matrix |
| `zero-sibling-matrix.tsv` | causal zero-accepting sibling score |
| `exact-positive-matrix.tsv` | satisfying exact-positive control score |
| `a-floors-gate.py`, `gate-matrix.tsv` | byte-unchanged seven serial fast/deep cases |
| `RUNBOOK.md` | exact reproduction and setup/verdict rules |

A future implementation is contract-ready only if focused is 71/71 and 65/65, gate binding is
4/4 and 3/3 under the unchanged harness, frozen B/C/protected bytes hold, and repository/workspace
guards report no new finding. A future implementation failure permits only D-058(9)'s bounded
product correction, not a test rewrite or lower floor.

## 6. Exclusions

Historical/dated reviews, decisions, signed packs, prior gate logs and A-090–A-093 remain
controls. Corpus/ablation/mutation counts and Batch D claims are excluded. B/C semantics remain
owned by their closed contracts; only frozen bytes/count deltas are preserved here. No generic
Bash-parser, repository-wide prose/count completeness, historical-truth or publication claim is
made.
