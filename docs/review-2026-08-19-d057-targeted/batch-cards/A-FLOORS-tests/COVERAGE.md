# A-FLOORS — fifth-corrected coverage and blind spots

## Covered

- All six floor constants and the prior missing/empty/malformed/non-numeric/zero/positive-one
  matrix.
- Direct duplicates in both orders, inline conditionals, standalone indented duplicates before
  and after, exact Bash order/final-value witnesses, prefix discrimination and reader restoration.
- Nine exact inert fake-opener spellings across every constant: full-line comment; `printf`,
  `echo` and assignment single/double quote forms; and here-string single/double quote forms.
- Every fake-opener spelling by itself: 54/54 reader controls requiring exit 0, no refusal class
  and all six exact canonical values; each maps one-to-one to 54/54 paired requirements.
- Every fake-opener spelling immediately followed by a real indented duplicate: 54/54 unique
  paired routes, with one Bash witness and one named requirement per route.
- Genuine quoted-heredoc body inertness and six post-terminator parser-resumption routes.
- Named-subject diagnostic correlation: six `DR-legit-*` controls accepting `{NAME}: duplicate
  executable assignment`; six `DR-uncorrelated-*` controls rejecting Review 4's two-line
  inventory; six `DR-oneline-*` controls rejecting Review 5's semicolon-joined inventory; six
  `DR-json-*` controls rejecting the compact JSON inventory; and two prefix controls distinguishing
  `VERIFIER_MIN_TAMPER` from `VERIFIER_MIN_TAMPER_MODES`.
- Live Review-4 two-line, Review-5 oneline and JSON uncorrelated-diagnostic siblings, each failing
  90 named-duplicate REQUIRED rows with every CONTROL holding.
- Exact Review-2 raw-reader sibling with its original 48 required misses retained and 40 new
  fake-only control failures classified separately.
- Exact Review-3 non-comment fail-closed sibling failing 48 fake-only controls while passing every
  prior/required row, twenty-six diagnostic controls and six comment-only controls; separately
  named expanded all-token sibling failing all 54 fake-only controls.
- Corrected digits-only sibling failing exactly six zero rows; corrected exact-positive control
  passing all 331 rows.
- Three finite maintained logical paragraphs, wrap normalization, dated-history controls, exact
  common-path wiring, frozen B/C bytes and unchanged historical seven-case gate binding.

## Not covered

- Command substitution, backticks, concatenated or escaped quote variants, process substitution,
  arbitrary redirection/delimiter expansion, or other shell spellings outside the exact matrix.
  This is not a complete Bash parser claim.
- Arbitrary Markdown/numeric prose; only three named maintained roles are scored.
- Diagnostic records that place a named subject and class under some other grammar than the
  enumerated `{NAME}:` subject with newline/semicolon record boundaries; this correction closes
  the Review-5 same-record and JSON false greens, not every conceivable decoy.
- Historical factual correctness, non-floor counts, Batch D claims, B/C semantic strength,
  concurrent gates, implementation, post-repair pass, public claim or D-055 closure.

## Interpreting green

Focused green means 131 REQUIRED and 200 CONTROL assertions held for the exact subject/variant,
including 54/54 inverse, 54/54 paired routes and 26/26 diagnostic-oracle controls. Gate green
means the seven unchanged serial cases produced their named outcomes when actually replayed; this
correction did not replay them. Neither result is repository-wide completeness. Workspace guards
remain ratcheted; Sentinel's non-Godot route has no visual/aspect/contrast evidence.
