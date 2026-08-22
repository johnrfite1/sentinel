# A-FLOORS — fourth-corrected frozen independent test contract

**Verdict: HOLD for fourth-corrected test-contract readiness only, pending fresh independent
Review 5.** This is not implementation approval, a gate signature, certification, ratification,
publication, rename, D-055 assessment or push authorization.

**Behavioral baseline:** `1a133301533e9d959dbafbbcc7ffe05e7eb78df3` (tree
`07cdc103133525f42b95018fabb802caa7cd8af3`). Original evidence subject
`e8b4d29641c47f0099482c9a9ac5da86c9255197`; first correction
`69e4fda92401e29c0cd4c717538fc278a5e59e26`; Review-2 FAIL
`9889289cb730a7ef23b2b9d11c0e84110dce84f6`; second correction
`12a35d2c3f30c77250b3ebde0bf82c25591dce10`; Review-3 FAIL parent
`cd12ac26fb718a9bd02971db1f09f4fe1189bba7`; third correction
`fa92ff7729287b10d6e140a6955b9740248600a6`; Review-4 FAIL
`0bf739b5be645abe6c8171c005a7181aaaadc5c8`. This correction changes only this evidence
directory. All four review records remain byte-identical. Fourth-corrected focused probes used
the external dirty harness against a disposable clean clone of Review-4 commit `0bf739b`.

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
accepted and reported. Refusals name the constant and exact class on **one refusal record or
line**: absent → `missing`; empty → `empty`; spaced/non-assignment spelling → `malformed`;
assigned non-number → `numeric`; zero → `positive`; and a second executable assignment in the
enumerated direct, inline-conditional or standalone-indented forms → `duplicate`. An inventory
line that lists every constant, paired with an unrelated record that carries only the class,
does not satisfy that assertion. Ordinary `NAME=1` and the
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

For every form/constant route, an `FA-*` CONTROL first places the exact opener at the same position
without the indented duplicate. It requires reader exit 0, no refusal/duplicate diagnostic and
all six canonical values reported exactly. The existing paired route then adds indented 999: its
Bash control proves canonical then 999 actually executed, and its REQUIRED row demands a named
duplicate refusal. `T-route-complete` requires 54/54 unique fake-only controls to map one-to-one
to 54/54 paired requirements, six per spelling. The inverse plus paired sides establish that the
real assignment—not the inert opener—caused the outcome transition.

For each constant, a genuine `: <<'A_FLOOR_REAL'` body containing `NAME=888` remains inert, and
parsing must resume after the terminator so a following indented `NAME=999` is caught. The old
`IH-*` controls prove body-only inertness; six new `HR-post-*` requirements prove resumption.

This is an exact finite grammar, not general Bash parsing. Command substitution, backticks,
concatenated quote fragments, escaped-quote variants, process substitution, arbitrary redirection
syntax and delimiter expansion are outside it. Those forms were not promised by the prior card;
this correction does not widen into them.

## 4. Diagnostic-correlation oracle

Review 4 showed that a global search for the mutated name anywhere in complete output and the
reason word anywhere else accepted this exact hostile payload at 305/305:

```text
inspected constants: FOUNDRY_MIN_TESTS TS_MIN_TESTS VERIFIER_MIN_TESTS VERIFIER_MIN_SAMPLES VERIFIER_MIN_TAMPER VERIFIER_MIN_TAMPER_MODES
UNRELATED_CONSTANT: duplicate executable assignment
```

The fourth correction requires one refusal record or line to carry both the mutated constant and
the expected class. Twelve new CONTROLS pin that oracle directly:

- six `DR-legit-*` rows accept `{NAME}: duplicate executable assignment`;
- six `DR-uncorrelated-*` rows reject the Review-4 inventory-plus-unrelated payload for that name.

The embedded `uncorrelated-diagnostic-sibling` is the Review-4 candidate: the exact-positive
finite lexer, with only duplicate diagnostics rewritten to that hostile policy. It must fail
exactly the 90 named-duplicate REQUIRED rows and hold every CONTROL, including the twelve new
oracle rows.

## 5. Causal sibling calibration

All current variants execute the same 317 uniquely named rows: 131 REQUIRED and 186 CONTROL.

- `digits-zero-sibling` uses the corrected finite opener lexer but accepts `[0-9]+`. It passes all
  transition, prior and diagnostic-oracle rows and fails exactly six `Z-*` rows: 125/131, 186/186.
- `flawed-heredoc-sibling` reconstructs Review 2's raw-text marker search before quote/context
  classification. Its earlier 83/131 REQUIRED outcome remains intact; inverse controls expose 40
  additional false reader states; the twelve diagnostic controls pass, so current calibration is
  83/131 and 146/186.
- `review3-failclosed-sibling` exactly preserves Review 3's non-comment policy. It passes all 251
  prior rows, every REQUIRED assertion, the twelve diagnostic controls and six comment-only
  controls, then fails exactly 48 non-comment `FA-*` rows: 131/131, 138/186.
- `all-token-failclosed-sibling` is separately named expanded calibration, not the exact Review-3
  candidate. It passes all prior rows/REQUIRED assertions and the twelve diagnostic controls but
  rejects comments too, failing all 54 `FA-*` rows: 131/131, 132/186.
- `uncorrelated-diagnostic-sibling` is the Review-4 hostile diagnostic policy on the satisfying
  lexer. It passes every CONTROL and fails exactly 90 named-duplicate REQUIRED rows: 41/131,
  186/186, exit 1.
- `exact-positive-control` uses `[1-9][0-9]*` and the finite lexer with named same-record
  diagnostics. It passes 131/131 and 186/186.

The baseline/current reader also passes all 54 fake-only controls and all twelve diagnostic
controls. Control failures in deliberate siblings return exit 2 by harness design: they establish
that the candidate is inadmissible, not a product verdict. The satisfying control proves the
matrix is achievable. These embedded candidates calibrate observable behavior; they do not
prescribe production structure. `P-reader-restore` continues to require unchanged candidate-reader
bytes plus identical restored exit/output after fixtures.

## 6. Finite reader-publication contract

The Markdown oracle remains limited to three whitespace-normalized logical paragraphs: the
`docs/session-state.md` §3 stable paragraph, its current D-010 bullet, and the quoted gate COVERAGE
D-010 paragraph. Refusal names the surface, current-time class and publication/derivation reason.
Wrapped/unwrapped forms agree. Dated history in the same paragraph, constant names without values
and unrelated numbers outside these roles remain controls. This is not a generic prose scan.

## 7. Gate binding and frozen instruments

The seven-case serial gate harness remains byte-identical at
`fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0`; `gate-matrix.tsv` remains
`0b4d9c127e7230c7266960fe073f92f9551da9a68005cb936850993d803d1c58`. The fourth correction
changes only focused diagnostic-correlation stimuli, so no expensive gate was rerun. Earlier serial
results remain historical design reliance, not refreshed execution/timing evidence.

| File | Role |
|---|---|
| `a-floors.py` | fourth-corrected 131 REQUIRED / 186 CONTROL instrument and six calibration/control variants |
| `*-matrix-v4.tsv` | current seven-variant baseline/calibration matrices |
| matrices/logs without `v4` | preserved earlier historical evidence |
| `a-floors-gate.py`, `gate-matrix.tsv` | byte-unchanged seven serial fast/deep cases |
| `RUNBOOK.md` | reproduction and setup/verdict rules |

A future implementation is contract-ready only if focused is 131/131 and 186/186, unchanged gate
binding is 4/4 and 3/3 when replayed for implementation verification, frozen B/C/protected bytes
hold, and repository/workspace guards report no new finding. A product failure permits only
D-058(9)'s bounded product correction, not a test rewrite or lower floor.

## 8. Exclusions

Historical reviews, decisions, signed packs, prior gate logs and A-090–A-093 remain controls.
Corpus/ablation/mutation counts and Batch D claims are excluded. B/C semantics remain owned by
their closed contracts; only frozen bytes/count deltas are preserved here. No generic Bash parser,
repository-wide prose/count completeness, historical truth or publication claim is made.
