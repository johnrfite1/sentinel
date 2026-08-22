# A-FLOORS — seventh-corrected coverage and blind spots

## Covered

Prior fifth/sixth coverage, plus wrapper records whose stripped text **begins with** `{` or `}`
(not only exact `{` / `}`), six `DR-prettycomment-*` controls, and a live commented pretty-JSON
sibling. Focused green is 131 REQUIRED and 218 CONTROL, including 44/44 diagnostic-oracle
controls.

## Not covered

Unchanged shell/Markdown exclusions. Brace-less multi-name `{NAME}:` dumps without wrapper
records that begin with `{` / `}` remain the Review-3 herestring fail-closed shape.

## Interpreting green

Focused green is not repository-wide completeness and is not a gate replay. Workspace guards
remain ratcheted.
