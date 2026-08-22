# A-FLOORS — frozen independent test contract

**Verdict: HOLD for test-contract readiness only, pending fresh independent review.** This is
not implementation approval, a gate signature, certification, ratification, publication, rename,
D-055 assessment or push authorization.

**Behavioral baseline:** `1a133301533e9d959dbafbbcc7ffe05e7eb78df3` (tree
`07cdc103133525f42b95018fabb802caa7cd8af3`). The independent test author wrote none of the
future Batch A floor implementation.

**Authority:** D-058(1), (2), (6), (8)C and (9); D-059(5), (7) and (8); D-060(1); D-066(2)–(4).
`N-TESTSH-FLOORS` is not a seventh item: its adjudicated disposition is duplicate of `R4-F4`
under D-058(2). `C3` supplies the independently confirmed reader/Bash disagreement that the
source oracle must close.

This evidence commit may add only this directory. It does not apply a production patch and does
not edit `scripts/test.sh`, `scripts/check-suite-floors.sh`, `docs/session-state.md`, an existing
test, prior evidence, a maintained claim, a decision record or signed material.

## 1. Declared future implementation surfaces

Completeness is claimed only for this finite surface inventory:

| Surface | Future obligation |
|---|---|
| `scripts/test.sh` six canonical assignments | Raise Foundry `92 → 103` and TypeScript `527 → 550`; preserve verifier `221/7/78/30`; keep exactly one executable positive-decimal definition of each. |
| `scripts/test.sh` gate body | Invoke the targeted floor-source/publication guard exactly once on the common fast/deep path, before the suite consumers, accumulating failure so later green stages cannot mask it. |
| `scripts/test.sh` quoted COVERAGE D-010 logical paragraph | Stop publishing a live hand-maintained copy of any of the six floor/count facts; derive any displayed live values from the canonical assignments. Preserve explicitly dated historical narration as history. |
| `scripts/check-suite-floors.sh` | Read all six definitions exactly, refuse missing/empty/malformed/non-numeric/duplicate assignments by constant and reason, and check only the enumerated maintained reader paragraphs below after logical-paragraph normalization. |
| `docs/session-state.md` §3 stable paragraph | Keep the current non-floor corpus/workspace facts if desired, but do not publish live hand-maintained values for any of the six floor dimensions. |
| `docs/session-state.md` §3 D-010 bullet | Replace the live stale floor/count clause with a derived/no-copy statement; preserve its explicitly dated history as history. |

There is no production test file to apply: the exact frozen instruments are the two directly
tracked Python harnesses. No `TESTS.patch` is needed or authorized.

## 2. Six-dimensional source contract

The planned canonical values are:

| Constant | Planned value | Baseline value | Baseline measured count |
|---|---:|---:|---:|
| `FOUNDRY_MIN_TESTS` | 103 | 92 | 103 |
| `TS_MIN_TESTS` | 550 | 527 | 550 |
| `VERIFIER_MIN_TESTS` | 221 | 221 | 221 |
| `VERIFIER_MIN_SAMPLES` | 7 | 7 | 7 |
| `VERIFIER_MIN_TAMPER` | 78 | 78 | 78 |
| `VERIFIER_MIN_TAMPER_MODES` | 30 | 30 | 30 |

For each name the checker must accept exactly one column-zero shell assignment whose value is a
positive decimal and must report that value. It must refuse these states distinctly:

- no assignment token: diagnostic names the constant and `missing`;
- token with empty value: names the constant and `empty`;
- whitespace around `=` / non-assignment spelling: names the constant and `malformed`;
- assigned non-number: names the constant and `numeric`;
- a second direct definition before or after the canonical one: names the constant and
  `duplicate`; and
- a conditional or indented assignment token that Bash can execute: names the constant and
  `duplicate`.

The duplicate matrix binds both directions. With a duplicate after the canonical line, the
current reader's `head -1` reports the old value while Bash enforces the last value. With a
duplicate before it, the reader reports the injected value while Bash later restores the planned
value. A conditional assignment is invisible to the reader's column-zero grep but changes Bash
state. The `VERIFIER_MIN_TAMPER`/`VERIFIER_MIN_TAMPER_MODES` prefix pair is an explicit
non-collision control.

Source uniqueness and maintained-publication truth are separate properties under D-059(8). A
single successful parse does not discharge the paragraph contract.

## 3. Finite reader-publication contract

The Markdown oracle is limited to exactly three maintained logical paragraphs and their stable
role anchors:

1. the `docs/session-state.md` §3 paragraph beginning
   `**What is stable and worth stating:`;
2. the current §3 list item beginning `- **D-010 verifier:`; and
3. the quoted `scripts/test.sh` COVERAGE paragraph beginning `  D-010`.

It normalizes runs of whitespace across hard wraps before classification. The same synthetic live
publication is tested wrapped and unwrapped and must receive the same diagnostic class. A reader
refusal must be non-zero and include the surface (`session-state` or `coverage`), a current-time
word (`live`, `current` or `maintained`), and a derivation/publication reason (`duplicate`,
`publication`, `numeric copy`, `must derive` or `derived`). A generic error or a line-oriented
grep failure is not accepted.

The valid fixture deliberately leaves dated numeric history inside both D-010 logical paragraphs.
That fixture must pass. Constant-name mentions with no values and unrelated issue/observation
numbers outside the three paragraphs also pass. These controls prevent the targeted oracle from
becoming a generic prose-consistency or generic number scan.

The contract does not freeze exact future prose beyond the three role anchors and diagnostic
class. The implementation may choose derived display or no live numeric copy. If it displays a
live floor/count, the value must be derived from the six canonical assignments rather than typed
again.

## 4. Gate wiring contract

`a-floors-gate.py` creates an independent exact-commit clone per case and executes every case
synchronously. It never overlaps two gates.

| Case | Kind | Frozen obligation |
|---|---|---|
| G0 | control | unchanged fast gate completes and measures `103/550/221/7/78/30` |
| G1 | required | one wrong wrapped §3 current paragraph produces a named reader refusal; Foundry, TypeScript and verifier still succeed; no `GATE PASSED`; supervisor exits 5 with missing-completion diagnostic |
| G2 | control | unchanged deep gate alone completes, identifies `--gate`, executes the 50-fixture corpus and verifies committed views |
| G3 | required | the same wrong paragraph is rejected on the deep path; later suites and the 50-fixture committed-view stage still succeed; no completion token |
| G4 | control | only raising the floors to 103/550 leaves the frozen B/C suites green and completes |
| G5 | required | after raising floors, deleting the eleven-test B-EVENTS file reports exactly `92 < 103`, later consumers remain green, and top level refuses completion |
| G6 | required | after raising floors, deleting the twenty-three-test C-SNAPSHOT file reports exactly `527 < 550`, later consumers remain green, and top level refuses completion |

G5 and G6 are the causal preservation rationale. B-EVENTS added exactly eleven currently passing
Foundry tests; C-SNAPSHOT added exactly twenty-three currently passing TypeScript tests. D-058's
no-weakening rule plus planned floors preserve those frozen additions. The verifier quartet did
not move and remains exactly at its existing floors.

## 5. Frozen instruments and success condition

| File | Role |
|---|---|
| `a-floors.py` | 53 required assertions and 28 controls over six definitions, shell/read order, finite paragraph publication and common-path source wiring. |
| `a-floors-gate.py` | Seven serial independent-clone top-level cases: four required and three controls, including fast and isolated deep paths. |
| `focused-matrix.tsv` | Complete baseline focused score by case. |
| `gate-matrix.tsv` | Complete baseline gate score and non-overlapping elapsed time by case. |
| `RUNBOOK.md` | Exact reproduction order and setup/verdict separation. |

A future implementation is contract-ready only if:

- focused is `53/53 REQUIRED`, `28/28 CONTROL`, with the frozen B/C bytes unchanged;
- gate binding is `4/4 REQUIRED`, `3/3 CONTROL` from serial non-overlapping runs;
- the top-level failure logs show the named defect and later successful consumers, while the
  supervisor refuses completion;
- protected, excluded, prior and signed files remain unchanged; and
- repository and workspace guards report no new finding.

No post-repair pass is claimed here. Per D-058(9), a later implementation failure permits one
bounded product correction under this frozen contract; it does not authorize changing the tests,
lowering a floor or widening the surfaces.

## 6. Explicit exclusions and cross-ownership limits

- Historical/dated reviews, decisions, signed packs, prior gate logs and A-090–A-093 are evidence
  controls, not maintained live publications to rewrite.
- The corpus size `50`, ablation counts and other non-floor statistics are outside this card.
- Batch D owns its maintained-claim repairs. This card must not edit, verify or double-own any
  Batch D surface merely because it contains a number or count.
- Event behavior/NatSpec and snapshot classification are closed B/C implementation boundaries.
  This card only preserves their frozen test files and resulting suite counts.
- No repository-wide prose consistency, count completeness, shell-parser completeness or
  publication correctness claim is made beyond the enumerated definitions, mutations and three
  logical paragraphs.
