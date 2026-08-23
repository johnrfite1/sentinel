# Class-credit determination (Phase A) — for John's number, not a published change

Guard, ratchet, HANDOFF, session-state, and §11.0 are **untouched**. This file is the determination.

## Remeasured

`./scripts/check-class-coverage.sh` prints `ok    14 of 20 classes exercise the class they name` and exits 0. One GAP: `conflicting-block-state`. Credit loop: any ABOUT code in L3 `failing` is a hit, including UNRESOLVED.

Live class names from `fixtures/corpus/for-labelling/`:

| Class | ABOUT (from the guard) | Fixture used | L3 | ABOUT hit |
|---|---|---|---|---|
| `malformed-calldata-or-unknown-selector` | `EVAL_CALLDATA_UNDECODABLE`, `EVAL_SELECTOR_BOUND`, `EVAL_OPERATION_SUPPORTED` | F037 | REVIEW | `EVAL_CALLDATA_UNDECODABLE` UNRESOLVED only. `EVAL_SIMULATION_SUCCEEDS` PASS. |
| same | same | F036 | BLOCK | `EVAL_CALLDATA_UNDECODABLE` UNRESOLVED **and** `EVAL_SIMULATION_SUCCEEDS` VIOLATION. ABOUT hit is the UNRESOLVED. |
| `runtime-code-change-or-proxy-target` | `EVAL_TARGET_CODE_IDENTITY` | F042 | REVIEW | that code UNRESOLVED (pin mismatch, not a proxy) |
| `rpc-simulator-or-context-outage` | `EVAL_SIMULATION_UNAVAILABLE` and related UNOBSERVED/UNAVAILABLE | F045 | REVIEW | `EVAL_SIMULATION_UNAVAILABLE` UNRESOLVED |

Engine (`ts/src/evaluate/checks.ts`): undecodable calldata is `unresolved("EVAL_CALLDATA_UNDECODABLE")` (§3.3(8)). Target code-hash mismatch is `unresolved("EVAL_TARGET_CODE_IDENTITY")` (Case 4). Null simulation is `unresolved("EVAL_SIMULATION_UNAVAILABLE")`.

## Independent ruling (verbatim substance)

**CREDIT all three.** UNRESOLVED on a ran ABOUT check is credit when that is the spec-assigned outcome for the named phenomenon.

John's intuition — outage UNRESOLVED may be correct; malformed UNRESOLVED may mean the fixture never reached the decision — was **tested and rejected**. F037 simulated successfully (PASS) and still UNRESOLVED on decode. That is the class decision D-028 assigned, not a skipped one.

**Collapse: yes.** They are alike under one defensible rule:

> Credit iff an ABOUT check ran against the named phenomenon and recorded the outcome the spec assigns to that phenomenon, including UNRESOLVED when the spec assigns UNRESOLVED.

John's reversal condition ("if the reviewer finds the three classes are in fact alike under any defensible rule, the per-class approach collapses to whichever single rule that is") **fired**.

## What John still rules in Phase B

The number, and whether the guard / ratchet / maintained prose / §11.0 move to match it. Not moved here.

## Blind spots (beside the ruling)

- Malformed ABOUT lists `EVAL_SELECTOR_BOUND` and `EVAL_OPERATION_SUPPORTED`; no fixture in that class fails them.
- No fixture in runtime-code-change is an actual proxy.
- Outage sibling codes on the non-null simulation branch never fire in that class.
