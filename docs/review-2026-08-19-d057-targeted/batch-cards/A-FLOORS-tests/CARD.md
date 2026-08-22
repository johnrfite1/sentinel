# A-FLOORS — second-corrected frozen independent test contract

**Verdict: HOLD for second-corrected test-contract readiness only, pending fresh independent
Review 3.** This is not implementation approval, a gate signature, certification, ratification,
publication, rename, D-055 assessment or push authorization.

**Behavioral baseline:** `1a133301533e9d959dbafbbcc7ffe05e7eb78df3` (tree
`07cdc103133525f42b95018fabb802caa7cd8af3`). Original evidence subject
`e8b4d29641c47f0099482c9a9ac5da86c9255197`; first correction
`69e4fda92401e29c0cd4c717538fc278a5e59e26`; Review-2 FAIL parent
`9889289cb730a7ef23b2b9d11c0e84110dce84f6`. This correction changes only this evidence
directory. Both review records remain byte-identical.

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
accepted and reported. Refusals name the constant and exact class: absent → `missing`; empty →
`empty`; spaced/non-assignment spelling → `malformed`; assigned non-number → `numeric`; zero →
`positive`; and a second executable assignment in the enumerated direct, inline-conditional or
standalone-indented forms → `duplicate`. Ordinary `NAME=1` and the
`VERIFIER_MIN_TAMPER`/`VERIFIER_MIN_TAMPER_MODES` prefix relationship remain controls.

Direct duplicates remain in both orders with independent legacy-first and Bash-last witnesses.
Inline conditionals remain separate `DC/DCW` rows. Standalone indented before/after rows require
`bash --noprofile --norc -x` to show exact order and actual final value. Existing `IC/IQ/IH`
controls retain inert comment, quoted string and genuine quoted-heredoc body behavior.

## 3. Finite fake-opener transition grammar

The Review-2 correction adds exactly these nine inert opener spellings, each immediately followed
by a standalone indented `NAME=999` and executed for all six constants:

| ID | Exact finite spelling class | Review-2 raw-reader target? |
|---|---|---|
| `comment` | full-line indented `# <<'A_FLOOR_MASK' NAME=888` | no; boundary requirement |
| `printf-sq` | `printf` with a single-quoted fake-opener argument | yes |
| `printf-dq` | `printf` with a double-quoted fake-opener argument | yes |
| `echo-sq` | `echo` with a single-quoted fake-opener token | yes |
| `echo-dq` | `echo` with a double-quoted fake-opener token | yes |
| `assign-sq` | single-quoted assignment value containing a fake opener | yes |
| `assign-dq` | double-quoted assignment value containing a fake opener | yes |
| `herestring-sq` | `: <<< 'A_FLOOR_MASK'` | yes |
| `herestring-dq` | `: <<< "A_FLOOR_MASK"` | yes |

Thus `T-route-complete` requires 54/54 unique paired routes, six per spelling. Every pair has a
separate Bash witness proving the fake opener was inert and the canonical then indented-999
assignments actually executed. A REQUIRED row additionally demands a named duplicate refusal;
the reader cannot satisfy it by rejecting an inert token for an unrelated reason.

For each constant, a genuine `: <<'A_FLOOR_REAL'` body containing `NAME=888` remains inert, and
parsing must resume after the terminator so a following indented `NAME=999` is caught. The old
`IH-*` controls prove body-only inertness; six new `HR-post-*` requirements prove resumption.

This is an exact finite grammar, not general Bash parsing. Command substitution, backticks,
concatenated quote fragments, escaped-quote variants, process substitution, arbitrary redirection
syntax and delimiter expansion are outside it. Those forms were not promised by the prior card;
this correction does not widen into them.

## 4. Causal sibling calibration

All current variants execute the same 251 uniquely named rows: 131 REQUIRED and 120 CONTROL.

- `digits-zero-sibling` uses the corrected finite opener lexer but accepts `[0-9]+`. It passes all
  transition and prior rows and fails exactly six `Z-*` rows: 125/131, 120/120.
- `flawed-heredoc-sibling` reconstructs Review 2's raw-text marker search before quote/context
  classification with a positive predicate. It passes all 136 prior rows, all controls, all six
  full-line-comment pairs and all six genuine-heredoc post rows, but fails exactly the 48 target
  rows (`printf`, `echo`, quoted assignment and here-string; single/double × six): 83/131,
  120/120.
- `exact-positive-control` uses `[1-9][0-9]*` and the finite lexer. It passes 131/131 and 120/120.

The satisfying control proves the matrix is achievable. These embedded candidates calibrate
observable behavior; they do not prescribe production structure. `P-reader-restore` continues to
require unchanged candidate-reader bytes plus identical restored exit/output after fixtures.

## 5. Finite reader-publication contract

The Markdown oracle remains limited to three whitespace-normalized logical paragraphs: the
`docs/session-state.md` §3 stable paragraph, its current D-010 bullet, and the quoted gate COVERAGE
D-010 paragraph. Refusal names the surface, current-time class and publication/derivation reason.
Wrapped/unwrapped forms agree. Dated history in the same paragraph, constant names without values
and unrelated numbers outside these roles remain controls. This is not a generic prose scan.

## 6. Gate binding and frozen instruments

The seven-case serial gate harness remains byte-identical at
`fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0`; `gate-matrix.tsv` remains
`0b4d9c127e7230c7266960fe073f92f9551da9a68005cb936850993d803d1c58`. The second correction
changes only focused parser-state stimuli, so no expensive gate was rerun. Earlier serial results
remain historical design reliance, not refreshed execution/timing evidence.

| File | Role |
|---|---|
| `a-floors.py` | second-corrected 131 REQUIRED / 120 CONTROL instrument and three variants |
| `*-matrix-v2.tsv` | current baseline, zero, flawed-reader and satisfying-control matrices |
| matrices/logs without `v2` | preserved Review-1/Review-2 historical evidence |
| `a-floors-gate.py`, `gate-matrix.tsv` | byte-unchanged seven serial fast/deep cases |
| `RUNBOOK.md` | reproduction and setup/verdict rules |

A future implementation is contract-ready only if focused is 131/131 and 120/120, unchanged gate
binding is 4/4 and 3/3 when replayed for implementation verification, frozen B/C/protected bytes
hold, and repository/workspace guards report no new finding. A product failure permits only
D-058(9)'s bounded product correction, not a test rewrite or lower floor.

## 7. Exclusions

Historical reviews, decisions, signed packs, prior gate logs and A-090–A-093 remain controls.
Corpus/ablation/mutation counts and Batch D claims are excluded. B/C semantics remain owned by
their closed contracts; only frozen bytes/count deltas are preserved here. No generic Bash parser,
repository-wide prose/count completeness, historical truth or publication claim is made.
