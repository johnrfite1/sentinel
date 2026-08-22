# A-FLOORS — seventh-corrected frozen independent test contract

**Verdict: HOLD for seventh-corrected test-contract readiness only, pending fresh independent
Review 8.** This is not implementation approval, a gate signature, certification, ratification,
publication, rename, D-055 assessment or push authorization.

**Behavioral baseline:** `1a133301533e9d959dbafbbcc7ffe05e7eb78df3` (tree
`07cdc103133525f42b95018fabb802caa7cd8af3`). Original evidence subject
`e8b4d29641c47f0099482c9a9ac5da86c9255197`; first correction
`69e4fda92401e29c0cd4c717538fc278a5e59e26`; Review-2 FAIL
`9889289cb730a7ef23b2b9d11c0e84110dce84f6`; second correction
`12a35d2c3f30c77250b3ebde0bf82c25591dce10`; Review-3 FAIL parent
`cd12ac26fb718a9bd02971db1f09f4fe1189bba7`; third correction
`fa92ff7729287b10d6e140a6955b9740248600a6`; Review-4 FAIL
`0bf739b5be645abe6c8171c005a7181aaaadc5c8`; fourth correction
`178347dbf33ab70923a6fd0278ea61c5dec5e6b6`; Review-5 FAIL of record
`30d6257f806276a24cb6a40319b5bbb858fa9a5d`; fifth correction
`3fc2e5673bc2d10f552c5d5177c56cabac008541`; Review-6 FAIL
`b4553841e4d234b947c008f340dce4f6a1a28b02`; sixth correction
`f0e0a9f1a12a5593e1d32aed9e207c3ab2b51fe3`; Review-7 FAIL
`0e90836057174052c13327fa5410f58a92550ad0`. This correction changes only this evidence
directory. Reviews 1–7 and the concurrent Review-5 blob remain byte-identical.
Seventh-corrected focused probes used the external dirty harness against a disposable clean clone
of Review-7 commit `0e90836`.

**Authority:** D-058(1), (2), (6), (8)C and (9); D-059(5), (7) and (8); D-060(1); D-066(2)–(4).
`N-TESTSH-FLOORS` remains a duplicate of `R4-F4`, not a seventh item. C3 supplies the confirmed
reader-first/Bash-last disagreement.

## 1. Declared future implementation surfaces

Completeness is claimed only for this finite inventory:

| Surface | Future obligation |
|---|---|
| `scripts/test.sh` six assignments | Raise `92 → 103` and `527 → 550`; preserve `221/7/78/30`; keep exactly one executable positive-decimal definition per name. |
| `scripts/test.sh` gate body | Invoke the targeted guard exactly once on the common fast/deep path, before suite consumers, accumulating failure so later green stages cannot mask it. |
| quoted COVERAGE D-010 paragraph | Remove hand-maintained live copies of the six facts or display only values derived from canonical assignments; preserve dated history. |
| `scripts/check-suite-floors.sh` | Apply the exact finite source/refusal and paragraph matrix in this card. |
| `docs/session-state.md` §3 stable paragraph and D-010 bullet | Remove live hand-maintained floor/count copies while preserving non-floor facts and dated history. |

There is no production `TESTS.patch`; the directly tracked harnesses are the test instrument. No
implementation, current claim or existing script is edited by this correction.

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
accepted and reported. Refusals name the constant as the **subject** of one refusal record
(`{NAME}:` then the exact class phrase). Absent → `missing definition`; empty → `empty
assignment`; spaced/non-assignment spelling → `malformed assignment`; assigned non-number or
zero → `numeric positive decimal required`; and a second executable assignment in the enumerated
direct, inline-conditional or standalone-indented forms → `duplicate executable assignment`.
Newline and semicolon are both record boundaries. Trailing commas on the class phrase are
stripped. An inventory of every constant — split across two lines, joined by `;`, wrapped as
compact JSON, pretty-printed as a `{` / `}` name-as-key object, or listed after the colon on the
same named-subject record — does not satisfy that assertion. Class-first live wording such as
`MISSING: $v is not defined` is not a named-subject refusal. Ordinary `NAME=1` and the
`VERIFIER_MIN_TAMPER`/`VERIFIER_MIN_TAMPER_MODES` prefix relationship remain controls: a
`TAMPER_MODES` subject is not a `TAMPER` refusal.

A JSON-wrapped dump whose stripped records begin with `{` or `}` and that names every constant
as the same class is not a unique-subject refusal, including when those wrapper lines carry
comments. A brace-less six-line `{NAME}: duplicate executable assignment` dump without those
wrapper records is the Review-3 herestring fail-closed shape and is not the Review-6/7 JSON
grammar.

Direct duplicates remain in both orders with independent legacy-first and Bash-last witnesses.
Inline conditionals remain separate `DC/DCW` rows. Standalone indented before/after rows require
`bash --noprofile --norc -x` to show exact order and actual final value. Existing `IC/IQ/IH`
controls retain inert comment, quoted string and genuine quoted-heredoc body behavior.

## 3. Finite fake-opener transition grammar

Unchanged from the fifth correction: nine inert opener spellings, 54/54 fake-only controls,
54/54 paired requirements, six `HR-post-*` resumption routes. This is not general Bash parsing.

## 4. Diagnostic-correlation oracle

Review 6 showed that pretty-printed unquoted name-as-key JSON still scored 343/343 against the
fifth-corrected matcher:

```text
{
  FOUNDRY_MIN_TESTS: duplicate executable assignment,
  TS_MIN_TESTS: duplicate executable assignment,
  VERIFIER_MIN_TESTS: duplicate executable assignment,
  VERIFIER_MIN_SAMPLES: duplicate executable assignment,
  VERIFIER_MIN_TAMPER: duplicate executable assignment,
  VERIFIER_MIN_TAMPER_MODES: duplicate executable assignment
}
```

`splitlines()` plus `strip()` turned every inner line into a `{NAME}:` record. A same-record
inventory after a legitimate `{NAME}:` subject, and a kitchen-sink of every class word after the
colon, also fully greened.

The seventh correction treats a record as a JSON wrapper when its stripped text begins with `{`
or `}`, not only when it is exactly `{` / `}`. Direct controls add six `DR-prettycomment-*`
rows rejecting Review 7's `{ // object` / `} // end` payload. Six live uncorrelated siblings
bind the rejected grammars, including `uncorrelated-pretty-json-comment-sibling`. Each must fail
exactly the 90 named-duplicate REQUIRED rows and hold every CONTROL, including the forty-four
diagnostic-oracle rows.

## 5. Causal sibling calibration

All current variants execute the same 349 uniquely named rows: 131 REQUIRED and 218 CONTROL.

- `digits-zero-sibling`: 125/131, 218/218 (exactly six `Z-*`).
- `flawed-heredoc-sibling`: 83/131, 178/218 (48 `TF-*` plus 40 `FA-*`; 44 diagnostic controls pass).
- `review3-failclosed-sibling`: 131/131, 170/218 (exactly 48 non-comment `FA-*`).
- `all-token-failclosed-sibling`: 131/131, 164/218 (all 54 `FA-*`).
- six uncorrelated siblings (two-line, oneline, compact JSON, pretty JSON, commented pretty JSON,
  same-record inventory): each 41/131, 218/218, exit 1, failing exactly the 90 named-duplicate
  rows. Their matrices are byte-identical to each other and distinct from the satisfying control.
- `exact-positive-control`: 131/131, 218/218.

The baseline/current reader passes all 54 fake-only controls and all forty-four diagnostic
controls. Held REQUIRED rows remain the four already-correct verifier floors: 4/131, 218/218.
Control failures in deliberate siblings return exit 2. These embedded candidates calibrate
observable behavior; they do not prescribe production structure.

## 6. Finite reader-publication contract

Unchanged: three whitespace-normalized logical paragraphs; dated history and unrelated numbers
remain controls.

## 7. Gate binding and frozen instruments

The seven-case serial gate harness remains byte-identical at
`fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0`; `gate-matrix.tsv` remains
`0b4d9c127e7230c7266960fe073f92f9551da9a68005cb936850993d803d1c58`. The seventh correction
changes only focused diagnostic-correlation stimuli, so no expensive gate was rerun.

| File | Role |
|---|---|
| `a-floors.py` | seventh-corrected 131 REQUIRED / 218 CONTROL instrument and eleven calibration/control variants |
| `*-matrix-v7.tsv` | current twelve-variant baseline/calibration matrices |
| matrices/logs without `v7` | preserved earlier historical evidence |
| `a-floors-gate.py`, `gate-matrix.tsv` | byte-unchanged seven serial fast/deep cases |
| `RUNBOOK.md` | reproduction and setup/verdict rules |

A future implementation is contract-ready only if focused is 131/131 and 218/218, unchanged gate
binding is 4/4 and 3/3 when replayed for implementation verification, frozen B/C/protected bytes
hold, and repository/workspace guards report no new finding. A product failure permits only
D-058(9)'s bounded product correction, not a test rewrite or lower floor.

## 8. Exclusions

Historical reviews, decisions, signed packs, prior gate logs and A-090–A-093 remain controls.
Corpus/ablation/mutation counts and Batch D claims are excluded. Brace-less multi-name dumps
without `{` / `}` wrapper records are the Review-3 herestring fail-closed shape, not the
Review-6 JSON grammar. No generic Bash parser, repository-wide prose/count completeness,
historical truth or publication claim is made.
