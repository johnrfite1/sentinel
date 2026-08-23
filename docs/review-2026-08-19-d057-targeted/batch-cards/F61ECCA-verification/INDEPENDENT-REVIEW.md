# Independent reviews — F61ECCA card and class-credit (2026-08-23)

Neither reviewer authored the f61ecca repairs or this card. Verbatim below.

## 2b — F61ECCA verification card (agent `25f1a6eb-eb8d-484c-947c-00fb444e50a0`)

## Verdict: **HOLD**

Attacked the harness, the mutants, and the logs — not the write-up. The named holes reopen on the mutants and stay closed on the freeze. Nothing here relabels an A1 verdict.

### Per item

| Item | Verdict | Reason |
|---|---|---|
| **C4** | **HOLD** | Mutant café-only prints `secret guard: clean` while the ASCII twin is `BLOCKED`; freeze `BLOCKED probe/café-only.md` on the same runtime `API_KEY=` blob. |
| **C6a** | **HOLD** | Mutant from the decoy cwd emits `MISMATCH` at 24 vs the ruled 23 (it read the canary ledger); freeze from the same cwd reports Sentinel’s 23 and `all totals match D-057(1) as ruled`. |
| **C6b** | **HOLD** | Mutant prints decoy `FOUNDRY_MIN_TESTS 99999`; freeze from the same cwd prints Sentinel’s floors (`103` / `550` / `221` / …), not the decoy constant. |
| **C6c** | **HOLD** | Mutant writes `core.hooksPath=.githooks` into the foreign repo; freeze refuses (`invoked from` vs `this script's`) and leaves that repo’s `hooksPath` unset. |
| **C6d** | **HOLD** | Mutant fires decoy shims; freeze marker file is empty after `--- decoy markers after freeze ---`, and the freeze log is Sentinel’s own children (`gate immutability: 10/10`, then `secret guard: clean`, then V-1). |
| **R1** | **HOLD** | Mutant `--staged` rename and typechange both print `secret guard: clean`; freeze `BLOCKED` names `r1-dst.txt` (line 401) and `r1-link`. Mutant-clean is the R/T proof: D+A would have been ACM-visible and the control would have failed. |

### Severity

No FAIL, so no FAIL-severity.

**R1 — High** (first adjudication; A2 said *“No claim about severity or priority.”*). `.githooks/pre-commit` execs `check-secrets.sh --staged`. ACM drops `R` and `T`, so a credential on a rename or typechange destination is admitted to the commit. That is a secrets-guard fail-open on a path developers actually take (`git mv` + edit). Not Critical: ordinary `A`/`C`/`M` adds still block; with `diff.renames` off the same edit scores `D`+`A` and ACM sees the `A`.

### C6d `GATE PASSED`

**Honest limit, not a FAIL of the card.** `C6D_GATE=NOT_OBSERVED`. The 240s bound died during later suite work (RPC surface), after identity had already selected Sentinel. The bar is “stays on Sentinel,” which the silent shims plus live Sentinel stages observe. Completing the banner would only watch more of a suite already chosen. A hang *inside* a Sentinel child after that point is suite liveness, not C6d.

### Overall

**HOLD**

Live strings in this tree (remeasured, not taken from the reviewer): `secret guard: clean`, `BLOCKED`, `all totals match D-057(1) as ruled`, `GATE PASSED`. Live hook is `.githooks/pre-commit` invoking `scripts/check-secrets.sh`. Live C6b decoy floor in the harness logs is the distinctive `99999`. Live R1 destinations in the harness: `r1-dst.txt` / `r1-link`.

## 2c — class-credit (agent `658f093f-3499-4f6f-b719-1f47fc52d9ad`)

**Ruling: CREDIT all three. UNRESOLVED on a ran ABOUT check is credit when that is the spec-assigned outcome for the named phenomenon. The offered split is rejected.**

The credit loop treats any ABOUT code in L3 `failing` as a hit. `failing` is `outcome !== "PASS"`, so UNRESOLVED counts. That is the right predicate for these three classes.

---

**1. Per class**

**malformed-calldata-or-unknown-selector — CREDIT.**
D-028 assigns undecodable calldata to UNRESOLVED (evidence gap, follows `failureMode`), not to a failed rule. F037 reached that decision: decode returned `DECODE_LENGTH_MISMATCH`, `EVAL_CALLDATA_UNDECODABLE` is UNRESOLVED, `EVAL_SIMULATION_SUCCEEDS` is PASS, L3 is REVIEW. UNRESOLVED here is the class decision, not a skipped one. The “decisive refusal expected” reading is the competing view D-028 rejected. F036 also ran `EVAL_CALLDATA_UNDECODABLE` (`DECODE_UNKNOWN_SELECTOR`); its BLOCK is from non-ABOUT `EVAL_SIMULATION_SUCCEEDS` VIOLATION.

**runtime-code-change-or-proxy-target — CREDIT.**
Case 4 / D-027 assign pin mismatch to UNRESOLVED: the engine compared hashes, they differed, and it recorded that the target’s behaviour is no longer established. F042 isolates that check (simulation PASS, L3 REVIEW). That is a completed decision, not an abort. Ambiguity is only about phenomenon quality: F042/F043 are a lying pin, not a live mutation or a proxy.

**rpc-simulator-or-context-outage — CREDIT.**
`EVAL_SIMULATION_UNAVAILABLE` exists to record a null simulation as UNRESOLVED. F045 has `simulated: false`, that check UNRESOLVED, L3 REVIEW. The named outage occurred and the ABOUT check ran.

---

**2. Alike?**

**Yes.** One defensible rule covers all three: credit iff an ABOUT check ran against the named phenomenon and recorded the outcome the spec assigns to that phenomenon, including UNRESOLVED when the spec assigns UNRESOLVED.

They are **not** alike under the offered split (outage yes, malformed no, runtime ambiguous). That split fails the evidence: D-028 and Case 4/D-027 assign UNRESOLVED to the first two as well. Treating UNRESOLVED as “never reached the decision” is true of a skipped check, not of these three, which ran and returned their assigned outcome.

---

**3. Fixture that did not reach the decision**

None of F036, F037, F042, F045 skipped the ABOUT check that credited the class.

F036 and F037 never emit `EVAL_SELECTOR_BOUND` at all: that check lives in the `decode.ok` branch and is gated off. That is a skipped **sibling ABOUT code**, not a skipped class decision. Unknown selector is decided on the decode path (`DECODE_UNKNOWN_SELECTOR` → `EVAL_CALLDATA_UNDECODABLE`), which F036 did reach.

---

**4. Blind spots**

- **malformed:** `EVAL_SELECTOR_BOUND` never appears in F036/F037/F038/F040. No fixture in the class is “decoded but not the mandate’s selector.” `EVAL_OPERATION_SUPPORTED` is PASS on all of them (CALL); it is ABOUT this class in the map and is never failed here.
- **runtime:** No proxy. No live bytecode change in this class (F048 actually mutates code and is filed as `conflicting-block-state`, a GAP). F043 is the same pin lie under FAIL_CLOSED.
- **outage:** Null simulation pushes only `EVAL_SIMULATION_UNAVAILABLE`. `EVAL_NATIVE_DELTA_UNOBSERVED`, `EVAL_ALLOWANCE_EFFECT_UNOBSERVED`, `EVAL_ENTITLEMENT_UNOBSERVED`, `EVAL_SIM_CALL_TRACE_UNAVAILABLE`, and `EVAL_SIM_UNRECOGNISED` are never failed by a fixture in this class (they sit on the non-null simulation branch).

Published count: not addressed. No files edited.

Live class names (fixtures, remeasured): `malformed-calldata-or-unknown-selector`, `runtime-code-change-or-proxy-target`, `rpc-simulator-or-context-outage`. Guard ABOUT map (remeasured from `scripts/check-class-coverage.sh`): malformed → `EVAL_CALLDATA_UNDECODABLE`, `EVAL_SELECTOR_BOUND`, `EVAL_OPERATION_SUPPORTED`; runtime → `EVAL_TARGET_CODE_IDENTITY`; outage → `EVAL_SIMULATION_UNAVAILABLE` and sibling UNOBSERVED/UNAVAILABLE codes. Published count not changed.
