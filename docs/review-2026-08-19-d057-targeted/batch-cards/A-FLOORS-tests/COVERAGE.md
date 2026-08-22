# A-FLOORS — coverage and blind spots

## Covered

- All six named floor constants, their exact planned values and current measured values.
- Exact-one positive-decimal source shape.
- Missing, empty, whitespace-malformed and assigned non-numeric definitions for every constant.
- Direct duplicates both before and after the canonical definition, plus conditional/indented
  duplicates, for every constant.
- Current reader first-wins versus Bash last-wins in both direct orders, with conditional Bash
  execution witnesses.
- The `VERIFIER_MIN_TAMPER` prefix relationship to `VERIFIER_MIN_TAMPER_MODES`.
- Three enumerated maintained logical paragraphs, whitespace normalization across wrapping,
  named diagnostic class, and controls for dated history within the same logical paragraph.
- Common fast/deep gate-path wiring exactly once.
- Unchanged fast and isolated deep top-level controls.
- Wrong-reader-current-publication top-level falsification on fast and deep paths, including
  later successful suites/corpus and supervisor completion behavior.
- Causal deletion of the frozen eleven-test B-EVENTS file and twenty-three-test C-SNAPSHOT file
  against planned floors 103/550, with unchanged raised-floor control.
- Frozen B/C test-file byte identity.

## Not covered

- Shell spellings outside the enumerated direct, malformed and conditional assignment shapes;
  this is not a complete Bash parser claim.
- Arbitrary Markdown, arbitrary numeric prose, every paragraph in `session-state.md` or every
  heredoc paragraph in the gate. Only the three named current roles are scored.
- Whether historical statements are factually correct. They are preservation controls here.
- Non-floor counts such as corpus size 50, ablation totals, mutation totals or documentation
  dates.
- Batch D maintained-claim surfaces or any claim assigned to another batch.
- The semantic strength of B-EVENTS or C-SNAPSHOT tests. Their independent contracts own that;
  this card establishes only frozen bytes, discovery, counts and deletion sensitivity.
- Concurrency behavior of two gates. Final evidence intentionally runs serially.
- A repaired implementation, post-repair gate pass, public claim, certification or D-055 closure.

## Interpreting green

Focused green will mean the 81 frozen assertions held for the exact subject. Gate green will mean
all seven serial cases produced their named outcomes. Neither result is repository-wide
completeness. Workspace guards remain ratcheted and Sentinel's non-Godot route has no visual,
aspect or contrast evidence.
