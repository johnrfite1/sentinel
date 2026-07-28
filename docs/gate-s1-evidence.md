# Gate S1 — Evidence Pack

**Status: UNSIGNED. Prepared for John; not answered, not pre-filled.**

D-002 and D-004 put gate signing with John, in a facilitated session, and the D-007…D-011
delegation explicitly excluded it. This document assembles evidence and asks questions. It
does not record answers, and no agent may add them.

Prepared: 2026-07-28, at commit `453469d` on branch `step-3/isolated-signer`.

---

## 1. What Gate S1 requires (D-002)

> Gate S1: vault + isolated signer + exact-action binding + Case 1 end-to-end + replay/tamper
> invariants green.

| Condition | Where it lives | Evidence |
|---|---|---|
| Vault | `contracts/src/SentinelVault.sol` | 43/43 Foundry: unit, stateful invariants, reentrancy |
| Isolated signer | `ts/src/signer/` (8 modules) | separate OS process, 0600 socket, two methods |
| Exact-action binding | `SentinelTypes.sol` + `_checkAction` | field-level mutation tests; 3-way EIP-712 differential |
| Case 1 end-to-end | `ts/test/cases.e2e.test.ts` | decode → simulate → evaluate → sign → vault executes |
| Replay/tamper invariants | `SentinelVault.invariants.t.sol` | 16,384-call campaigns, non-vacuity tests |

**One-command reproduction:**

```bash
cd ~/Projects/Sentinel && ./scripts/test.sh
```

Current result: **43 Foundry + 204 TypeScript tests green.** The script prints its own
coverage boundary; the second half of that output matters more than the first.

## 2. What the evidence actually shows

- **Case 1** runs the real pipeline end to end and the purchase lands onchain. The receipt's
  `evidenceHash` equals the hash of the bytes the evaluator produced.
- **Case 2** (the injected `approve(attacker, max)`) blocks on decoded parameters, and the
  simulation shows the vault's own tokens would have been approved without limit.
- **Case 3** blocks on mandate conformance **while every representative-baseline check
  passes and the execution genuinely succeeds**. The test asserts the violation list is
  exactly `[EVAL_PURCHASE_RESOURCE]` — if that list ever grows, the case has stopped
  demonstrating mandate conformance.
- **Case 4** reviews without recording a single violation, and the same evidence gap under a
  FAIL_CLOSED policy blocks — so the engine is visibly not hard-coding the outcome.
- **Three independent EIP-712 implementations** (Solidity, signer hand-rolled, evaluator via
  viem) agree on generated payloads, and the independence itself is asserted.
- **Mutation testing**: 50 deliberate defects introduced across signer, decoders, pipeline
  and evaluator; all caught at last run of each batch.

## 3. What it does NOT show — read before signing

1. **The verdicts are not proven correct.** §7's own opening: "Four demo paths alone cannot
   prove that the verdicts are not hard-coded." The conformance engine's own suite cannot
   supply that proof — self-written tests encode the same misunderstanding twice. The bar is
   the §9 step 8 corpus under D-011 plus the §7.3 ablation. **Neither exists yet.** Both are
   Gate S2 conditions.
2. **Case 1 is not driven by a real agent.** The action is constructed by the test. The
   D-007 spike proved an agent *proposal* flips under injection (A-009), but the proposal
   and the pipeline have not yet been wired together.
3. **Effects are simulated, not observed.** §8 as amended by D-001: conformance is against
   simulated effects at a recorded block.
4. **Twice now, a whole class of checks was untested until a mutation found it** — 22 of 31
   in the signer (A-016), 24 of 37 in the evaluator. Both are fixed and both now have
   structural exhaustiveness guards. The pattern is worth weighing when judging how much the
   green suite means.
5. **The A-016 adversarial review is weaker evidence than it looks.** 6 of 8 skeptic
   verifications never ran (spend limit), so most findings were adjudicated by the build
   loop against the spec rather than independently.
6. **No independent review of steps 4–6.** Only step 3 has had an adversarial pass.

## 4. Decisions the build loop made that are John's to confirm or reverse

Each is recorded in `docs/decisions.md` with its reasoning and is cheap to reverse now.

| Ref | The call | Why it may want reversing |
|---|---|---|
| A-011 | Signer refuses rather than downgrading; three severity tiers | Decides what artifacts exist in the S2 evidence bundle |
| A-012 | One live executable attestation per (chain, vault, nonce) | Adds a guarantee the spec does not require |
| A-018 | **Open fork, unresolved:** should the signer check decoded parameters? | Would close Case 3 at the signer layer; contradicts A-011's boundary |
| A-020 | `failureMode` governs unresolved checks, overriding §5.2's prose | Spec interpretation, not engineering |

## 5. Questions for the facilitated session

Left blank deliberately.

1. Does the evidence in §2 satisfy each D-002 condition, condition by condition?
2. Are the limits in §3 acceptable as the state of the build at S1, given that items 1 and 2
   are S2 conditions rather than S1 ones?
3. A-011 — confirm or reverse?
4. A-012 — confirm or reverse?
5. A-018 — how should this be resolved before step 6 hardens?
6. A-020 — is the reading right?
7. Sample check: pick any two of the four demonstration cases and have the build loop walk
   the actual evidence, rather than accepting the summary above.

## 6. Sign-off

**Not to be completed by any agent.**

```
Gate S1 outcome:        [ PASS / PASS WITH CONDITIONS / FAIL ]
Conditions, if any:
Signed:                                        Date:
```
