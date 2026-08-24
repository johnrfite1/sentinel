# Critical / High census — assembled, not ruled

**Prepared material. Not a D-055 verdict. Not a recommendation.** Assembling the
clause that would retire each item is not applying that clause. John rules.

Independent residual scores for V-1–V-5, V-7–V-10 and R-A–R-F live in
`docs/review-2026-08-19-d057-targeted/batch-cards/D062-containment-tests/RESIDUAL-SEVERITY.md`.
That adjudicator was not the D-062 verifier and did not implement a repair. V-6, R5,
and R2 were not rescored there.

D-055(a): a confirmed High ceases to block only through **verified repair**, or
through **John's explicit acceptance as a documented product boundary**. An
agent may take neither on its own.

| ID | Severity | D-055(a) clause that would retire it | Standing at this assembly |
|---|---|---|---|
| `R1-F1` | Critical | Verified repair | Independent HOLD (A-078). Certification-gate corruption; John ruled REPAIR (D-057(3)). Not reopened. |
| `R1` | High | Verified repair | F61ECCA independent HOLD. First severity High. Exploit control live; freeze blocked rename and typechange destinations. Not acceptance as a product boundary. |
| `R5` | High | Verified repair | Pre-repair High (`SEVERITY.md`). D-071 option C. Independent HOLD on the card (`VERIFICATION.md`). D-067 not lifted. |
| `V-6` | High | Verified repair | Pre-repair High (`SEVERITY.md`). D-072 pin at enumerating call sites. Independent HOLD on the card. D-067 not lifted. |
| `V-1` | High | **None applied.** Returned to John. | Independent residual score High. Unset-before-resolve remains load-bearing. A-098 is a behavioural guard, not acceptance. Session-state still carries V-1 unaccepted. **Not repaired in this stretch.** |
| `R-C` | High | **None applied.** Returned to John. | Independent residual score High as recorded (A2: `GIT_CONFIG_COUNT` + `core.excludesFile` hiding untracked plants from default-mode secrets). Same injection family as V-6. The D-072 pin was measured to override that COUNT vector in scratch; the adjudicator scored the residual as recorded and did not treat the pin as silent closure. **Not repaired in this stretch.** |
| `V-3` | **UNSCORED** | **None applied.** Returned to John. | Validate/scan window exists twice. Scoring without a timing probe would be a guess. Siblings scored High / Critical; that is not a substitute for a probe. Pending under John's clarification until scored. |

No other item from the 3a set scored Critical or High.

**What this file does not do.** It does not rule condition 3. It does not accept
V-1 or R-C as product boundaries. It does not lift D-067. It does not probe V-3.
