# Gate S1 — Evidence Pack

**Status: UNSIGNED. Prepared for John; not answered, not pre-filled.**

D-002 and D-004 put gate signing with John, in a facilitated session, and the D-007…D-011
delegation explicitly excluded it. This document assembles evidence, records input received,
and asks questions. It does not record answers, and no agent may add them.

Prepared 2026-07-28. Revised the same day after two outside reviews, both of which found
real defects in the first version — see §6.

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
| Replay/tamper invariants | `SentinelVault.invariants.t.sol` | deep-profile campaigns, non-vacuity tests |

**Reproduction — use the DEEP profile for gate evidence, not the fast default:**

```bash
cd ~/Projects/Sentinel && ./scripts/test.sh --gate
```

The default profile runs 16,384-call invariant campaigns, which is legitimate for the inner
loop but is not the right evidence for a security gate. `--gate` raises fuzzing to 20,000
runs and each stateful invariant to 262,144 calls. The script prints its own coverage
boundary; **read it in full** — it is organised by layer, and each layer states the limit it
cannot exceed.

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

**Mutation testing — the honest numbers.** 51 deliberate defects, in `scripts/mutate.sh`,
reproducible with `./scripts/mutate.sh`. **48 were caught on first attempt. 3 survived**,
and each survivor exposed a real gap that was then fixed:

| Survivor | What it exposed |
|---|---|
| `M18` keystore signs a receipt naming another signer | the guard had no test at all |
| `S2` simulate as caller instead of vault | the impersonation fixture was vacuous — an Anvil dev account, so the node signed natively |
| `E7` drop the beneficiary check | 24 of the evaluator's 37 codes were exercised by nothing |

All three are now caught. The first version of this pack said "all caught at last run of each
batch", which implied 51/51 while not quite claiming it; a reviewer called that out and was
right to. The 3 survivors are better evidence than a clean sweep would have been — they are
what shows the technique finds things reading does not.

(Separately: the very first sweep reported 14/14 surviving. That was a broken harness
parsing the test reporter's output, not a suite result. It is counted neither way.)

## 3. What it does NOT show — read before signing

1. **The verdicts are not proven correct.** §7's own opening: "Four demo paths alone cannot
   prove that the verdicts are not hard-coded." The conformance engine's own suite cannot
   supply that proof — self-written tests encode the same misunderstanding twice. The bar is
   the §9 step 8 corpus under D-011 plus the §7.3 ablation. **Neither exists yet.** Both are
   Gate S2 conditions.
2. **Case 1 is not agent-to-chain end-to-end.** The action is constructed by the test. The
   D-007 spike proved an agent *proposal* flips under injection (A-009), but the proposal
   and the pipeline have not yet been wired together. Both reviewers flagged the ambiguity in
   the word "end-to-end"; see question 2.
3. **Effects are simulated, not observed.** §8 as amended by D-001: conformance is against
   simulated effects at a recorded block.
4. **Twice now, a whole class of checks was untested until a mutation found it** — 22 of 31
   in the signer (A-016), 24 of 37 in the evaluator. Both are fixed and both now have
   structural exhaustiveness guards. The pattern is worth weighing when judging how much the
   green suite means.
5. **The A-016 adversarial review is weaker evidence than it looks.** 6 of 8 skeptic
   verifications never ran (spend limit), so most findings were adjudicated by the build
   loop against the spec rather than independently.
6. **No independent review of steps 4–6.** Only step 3 has had an adversarial pass. This
   conflicts with the project's own independent-grader principle; see question 3.
7. **The repository is pushed.** `origin` is configured and both branches are on GitHub,
   private. Authorised, but "nothing has left this machine" is no longer true, and the repo
   carries the colliding working name. See question 8.

## 4. Decisions the build loop made that are John's to confirm or reverse

Each is recorded in `docs/decisions.md` with its reasoning and is cheap to reverse now.

| Ref | The call |
|---|---|
| A-011 | Signer refuses rather than downgrading; three severity tiers |
| A-012 | One live executable attestation per (chain, vault, nonce) |
| A-018 | **Open fork:** should the signer check decoded parameters? |
| A-020 | `failureMode` governs unresolved checks, overriding §5.2's prose |

## 5. Input received — recommendations, NOT answers

Recorded so the session has the arguments in front of it. **These are input to John's
decision, not the decision.** The two outside reviewers agree on A-011, A-012 and A-020 and
**disagree on A-018**, which is the one genuine fork.

| Ref | Reviewer 1 | Reviewer 2 | Build loop's own view |
|---|---|---|---|
| A-011 | Confirm; add a recorded refusal artifact so "refused" and "never asked" are distinguishable | Confirm; keep refusal diagnostics separate from a signed receipt | Agree with both. The refusal-artifact gap is real and cheap; without it S2 cannot prove the signer ever saw the request |
| A-012 | Confirm the mechanism, but describe it as defence-in-depth, never as a durable guarantee | Confirm with narrower wording; per-process safeguard, or back it with durable single-writer state | Agree. The in-process limit is already in A-012; the wording is what needs constraining, not the code |
| A-018 | **No.** Two implementations of one policy that must agree is a liability. Instead have the signer bind its own decoding into the evidence it hashes — accountability without a second evaluator | **Yes.** A narrow signer-local decoder for resource, beneficiary, duration, recurrence; leave simulated-effect conformance in the evaluator | **Reviewer 1, and it is not close.** Reasoning below |
| A-020 | Confirm; ensure both `failureMode` configurations appear in the demo, not only the tests | Confirm, then amend the proposal so §5.2's prose no longer contradicts `failureMode` | Agree with both, and the spec amendment matters more — leaving the contradiction in place guarantees a future reader re-derives this fork |

**On A-018, the build loop's reasoning.** Reviewer 2's concern is legitimate and the artifact
that proves it is uncomfortable: `signer.e2e.test.ts` deliberately demonstrates the signer
signing and executing the wrong resource. But Reviewer 1 identifies the cost that outweighs
it — a signer checking four fields of many cannot honestly be described as independently
checking conformance, and it still could not re-derive simulated effects without re-running
the simulation. That is an invitation to overclaim precisely where §7.5's honesty gate bites.
Reviewer 1's alternative is strictly better than either branch of the original fork: the
signer **decodes the calldata itself and binds its own decoding into the receipt**, deriving
without judging. A wrong-purpose ALLOW then becomes detectable after the fact by the D-010
verifier, with no second evaluator and no two-implementations-must-agree problem. Decoding is
a pure function of bytes already differentially tested against the EVM, so sharing the
decoder is not the concern that sharing hashing would be.

## 6. What the outside reviews found in this pack

Recorded because a pack arguing for its own rigour should show its own corrections.

- The state file claimed the repo was unpushed with no remote. **False as written** for
  several commits; the push was authorised but the record was never updated. Corrected in
  A-004 and session-state §5.
- The gate script's coverage boundary **contradicted itself three ways** — claiming steps 5
  and 6 did not exist, that Case 3 was undetectable, and that Case 3 was detectable. It had
  grown by accretion. Rewritten as one statement organised by layer.
- session-state listed steps 5–9 as not started, eleven lines after documenting 5 and 6 as
  done. Corrected.
- "all caught at last run of each batch" was doing evasive work. Replaced with first-pass
  numbers and the three survivors named.
- The mutation harness was scratch material, so its numbers were not reproducible from the
  repository. Promoted to `scripts/mutate.sh`.

## 7. Questions for the facilitated session

Left blank deliberately.

1. Does the evidence in §2 satisfy each D-002 condition, condition by condition?
2. **Does constructed-action Case 1 satisfy S1**, with real-agent wiring belonging to step 7
   and S2? Both reviewers asked for this to be recorded explicitly rather than left to the
   word "end-to-end".
3. **Independent adversarial review of steps 4–6** — an S1 condition, or a named condition
   due before S2?
4. A-011 — confirm or reverse? Add the refusal artifact?
5. A-012 — confirm the mechanism with narrowed wording?
6. A-018 — how resolved? (See §5; the reviewers disagree.)
7. A-020 — confirm the reading, and amend §5.2's prose to match?
8. The rename gate: close it before visibility ever flips, or accept the collision?
9. Sample check: pick any two of the four demonstration cases and have the build loop walk
   the actual evidence, rather than accepting the summary above.

## 8. Sign-off

**Not to be completed by any agent.**

```
Gate S1 outcome:        [ PASS / PASS WITH CONDITIONS / FAIL ]
Conditions, if any:
Signed:                                        Date:
```
