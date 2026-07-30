# Gate S1 — Evidence Pack

**Status: UNSIGNED. Prepared for John; not answered, not pre-filled.**

D-002 and D-004 put gate signing with John, in a facilitated session, and the D-007…D-011
delegation explicitly excluded it. This document assembles evidence, records input received,
and asks questions. It does not record answers, and no agent may add them.

Prepared 2026-07-28. Revised the same day after two outside reviews, then again after the
D-017 independent review closed. All three found real defects — see §6 and A-022.

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

**Mutation testing — the honest numbers.** 62 deliberate defects, in `scripts/mutate.sh`,
reproducible with `./scripts/mutate.sh`. **54 caught on first attempt; 8 survived.** All 62
are caught now. The survivors are the interesting part, and they split two ways:

*Five were real coverage gaps, each since fixed:*

| Survivor | What it exposed |
|---|---|
| `M18` keystore signs a receipt naming another signer | the guard had no test at all |
| `S2` simulate as caller instead of vault | the impersonation fixture was vacuous — an Anvil dev account, so the node signed natively |
| `E7` drop the beneficiary check | 24 evaluator codes were exercised by nothing |
| `V3` drop simulation serialisation | the D-017 concurrency fix shipped with no test |
| `V4` un-normalise decoded addresses | the case-normalisation test uppercased an address with no hex letters — a no-op |
| `V5` emit unpaired surrogates again | the D-017 RFC 8785 fix shipped with no test |

*Two were defective MUTATIONS rather than gaps, and were replaced:* `R2` swapped a domain
tag for bytes that could not collide anyway; `R6` was written as a no-op. Telling those apart
from real survivors is part of the technique — a surviving mutation is a question, not a
verdict.

The first version of this pack said "all caught at last run of each batch", which implied a
clean sweep while not quite claiming it; a reviewer called that out and was right to. The
survivors are better evidence than a clean sweep would have been.

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
4. **Three times now, code has shipped whose tests could not fail.** A whole class of checks
   was untested until a mutation found it — 22 of the signer's checks (A-016), then 24 of the
   evaluator's — and then the D-017 *corrections themselves* shipped with three untestable
   fixes (A-022). Counts are as they stood when each was found; both surfaces now have
   structural exhaustiveness guards. **The pattern is the single most useful thing to weigh
   here:** a fix written confidently and a test written from the same understanding are one
   act, not two. Mutation testing has caught this every time; reading and review have not.
5. **The A-016 adversarial review is weaker evidence than it looks.** 6 of 8 skeptic
   verifications never ran (spend limit), so most findings were adjudicated by the build
   loop against the spec rather than independently.
6. **Independent review of steps 4–6 is COMPLETE** (D-017; see §7 and A-022). It found one
   S1-blocking defect, now corrected and reverified. Six further confirmed defects were also
   corrected. Steps 1–3 were reviewed earlier under A-016, whose own verifications were
   mostly cut short — that limit still stands and is unchanged by this review.
7. **The repository is pushed.** `origin` is configured and both branches are on GitHub,
   private. Authorised, but "nothing has left this machine" is no longer true, and the repo
   carries the colliding working name — now governed by the D-016 publication gate (§8),
   which is deliberately NOT an S1 condition.

## 4. Decisions — RULED by John, 2026-07-28

All four are now closed and implemented. Canonical text: `docs/decisions.md` D-012…D-015.
They are no longer questions for this session.

| Was | Ruling | Implemented as |
|---|---|---|
| A-011 | **D-012** — confirmed, plus a recorded refusal artifact | A signed `RefusalRecord` binding action + evidence hashes, domain-separated from EIP-712 so it can never be replayed as a receipt. "Refused" is now distinguishable from "never asked". |
| A-012 | **D-013** — mechanism confirmed, CLAIM narrowed | No code change. Per-process best-effort defence in depth, never a durable guarantee; the vault's nonce is the actual guarantee. Wording corrected, with a test making the honest limit observable. |
| A-018 | **D-014** — resolved: NO conformance checks in the signer | The signer decodes the calldata itself and verifies the bundle's decoded parameters match the bytes. Derivation without judgement; the mandate is never consulted. A wrong-purpose ALLOW becomes detectable by the D-010 verifier without a second evaluator. |
| A-020 | **D-015** — confirmed, and §5.2 amended | The proposal's contradicting sentence is gone, asserted mechanically by a test. Both `failureMode` configurations must appear in the demo (step 9). |

Verification: 6 dedicated mutations against the two code rulings, all caught. Two earlier
survivors in that batch were defective *mutations* rather than coverage gaps, and were
replaced — one of them exposed a real gap in the refusal digest, now tested.

## 5. How the rulings were reached — the arguments, retained

Kept on the record because the reasoning matters more than the outcome, and because D-014's
losing branch is the one a future reader is most likely to want to reopen. The two reviewers
agreed on A-011, A-012 and A-020 and **disagreed on A-018**; John ruled for reviewer 1.

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
- **The mutation count itself was wrong.** This pack first said 51 defects / 48 caught. The
  count came from `grep -c '^run_mutation'`, which also matched the function *definition*
  line; the true figure is **50 / 47**. Found only because John asked whether the document
  reflected the changes, and the promoted harness reported "50 skipped" on its first real
  run — which is also the first time the promoted copy had been executed rather than merely
  syntax-checked. Recorded rather than quietly amended, because a document arguing for its
  own rigour miscounting its own headline number is the exact failure §7.5 exists to catch,
  and because the lesson is concrete: a number cited as evidence must come from running the
  thing, not from grepping it.

## 7. S1 conditions still open

**D-017 — independent adversarial review of §9 steps 4–6. COMPLETE. Full detail: A-022.**

| D-017 condition | How it was met |
|---|---|
| fresh-context, adversarial | 4 independent lenses, no build context |
| fixed commit | `4b25e5d`; all 4 lenses confirmed `git rev-parse HEAD` before reviewing |
| actual implementation and tests, not the summary | reviewers read and RAN the code; instructed not to grade this pack |
| material findings independently adjudicated | **12 filed, 12 adjudicated.** First pass capped at 6 (my sizing error); a second pass closed the gap |
| confirmed defects corrected and reverified | 1 blocking + 6 non-blocking corrected; 6 regression mutations, all caught; deep profile green |

**Outcome: 1 blocking defect, 6 confirmed non-blocking, 4 refuted.** The blocking one — filed
by two lenses, reproduced by two adjudicators — was the D-014 evidence bind comparing two
different predicates, which made the signer refuse TRUTHFUL bundles fatally for exactly the
target-substitution and wrong-operation shapes injection produces. It contradicted D-014's own
boundary sentence. Corrected, with tests built from real evaluator bundles rather than the
tautological stub that hid it.

**Reverification found three of six regression mutations surviving on the first attempt** —
all three real gaps in the corrections, since fixed and re-caught. That is worth weighing: it
is the third time in this build that a confidently-written fix and a test written from the
same understanding both failed to bite.

## 8. Not an S1 condition — the pre-publication rename gate (D-016)

Recorded here so it is not mistaken for something S1 waits on. **The naming collision is not
accepted.** "Sentinel" stays a private working codename, and repository visibility changes,
public demos, published links, and portfolio or résumé references are blocked until John
approves a replacement following domain and trademark/collision review. S1 may be signed
while this remains open; the two are independent. Enforced mechanically by
`scripts/check-rename-gate.sh`, which fails the project gate if the repository becomes
public — because a rule like this is violated by one click months later, by someone who
never read the decision log.

## 9. Questions for the facilitated session

Left blank deliberately.

1. Does the evidence in §2 satisfy each D-002 condition, condition by condition?
2. **Does constructed-action Case 1 satisfy S1**, with real-agent wiring belonging to step 7
   and S2? Both reviewers asked for this to be recorded explicitly rather than left to the
   word "end-to-end".
3. Sample check: pick any two of the four demonstration cases and have the build loop walk
   the actual evidence, rather than accepting the summary above.

*(A-011, A-012, A-018 and A-020 were questions here until 2026-07-28; they are ruled as
D-012…D-015 and §4 records the outcomes. The rename gate and the independent review were
also questions here; John ruled them as D-016 and D-017 — the first is not an S1 condition,
the second is.)*

## 10. Sign-off

**Not to be completed by any agent.**

```
Gate S1 outcome:        [ PASS / PASS WITH CONDITIONS / FAIL ]
Conditions, if any:
Signed:                                        Date:
```
