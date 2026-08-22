# A-FLOORS — second-corrected coverage and blind spots

## Covered

- All six floor constants and the prior missing/empty/malformed/non-numeric/zero/positive-one
  matrix.
- Direct duplicates in both orders, inline conditionals, standalone indented duplicates before
  and after, exact Bash order/final-value witnesses, prefix discrimination and reader restoration.
- Nine exact inert fake-opener spellings across every constant: full-line comment; `printf`,
  `echo` and assignment single/double quote forms; and here-string single/double quote forms.
- Every fake-opener spelling immediately followed by a real indented duplicate: 54/54 unique
  routes, with one Bash witness and one named requirement per route.
- Genuine quoted-heredoc body inertness and six post-terminator parser-resumption routes.
- Exact Review-2 raw-reader sibling: all 136 prior rows pass, then exactly 48 vulnerable transition
  rows fail while comment and genuine-heredoc boundary rows pass.
- Corrected digits-only sibling failing exactly six zero rows; corrected exact-positive control
  passing all 251 rows.
- Three finite maintained logical paragraphs, wrap normalization, dated-history controls, exact
  common-path wiring, frozen B/C bytes and unchanged historical seven-case gate binding.

## Not covered

- Command substitution, backticks, concatenated or escaped quote variants, process substitution,
  arbitrary redirection/delimiter expansion, or other shell spellings outside the exact matrix.
  This is not a complete Bash parser claim.
- Arbitrary Markdown/numeric prose; only three named maintained roles are scored.
- Historical factual correctness, non-floor counts, Batch D claims, B/C semantic strength,
  concurrent gates, implementation, post-repair pass, public claim or D-055 closure.

## Interpreting green

Focused green means 131 REQUIRED and 120 CONTROL assertions held for the exact subject/variant,
including 54/54 paired routes. Gate green means the seven unchanged serial cases produced their
named outcomes when actually replayed; this correction did not replay them. Neither result is
repository-wide completeness. Workspace guards remain ratcheted; Sentinel's non-Godot route has
no visual/aspect/contrast evidence.
