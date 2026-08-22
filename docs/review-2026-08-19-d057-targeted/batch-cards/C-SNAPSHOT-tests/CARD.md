# C-SNAPSHOT — corrected frozen independent test contract

**Verdict: HOLD for corrected test-contract readiness only, pending fresh independent review.**
This is not implementation approval, a gate signature, certification, ratification, publication,
rename, D-055 assessment or push authorization.

**Behavioral baseline:** `1655b120a653b60ccb5b3a22583c0001d59ea7a4` (tree
`b2c8fb1e53d35ea40655dc83faa61f8a76dd4f78`). The independent test author wrote none of the
future Batch C implementation.

**Correction basis:** first independent review
`8834d9b868657fbccfe1009bf139e23dc8e06db1` returned instrument-readiness FAIL with F1
(lexical message oracle) and F2 (canonical-only first-occurrence order). This is the one bounded
instrument correction required by that review and consumes no D-058(9) implementation attempt.
`INSTRUMENT-REVIEW-1.md` is preserved byte-unchanged.

**Authority:** D-058(1), (8)C and (9); D-059(5)–(6); D-060(1); D-066(2)–(3).

This directory is the complete test-only deliverable. `TESTS.patch` is preserved but not applied
in this commit. No production source, existing test, `scripts/test.sh`, `protocol.ts`, maintained
claim, floor, prior evidence, review record or signed material is changed.

## 1. Declared production boundary

Completeness is claimed only for `ChainUnstableError` and
`createChainReader(...).readVaultState` in `ts/src/signer/vault.ts`, at the behavioral baseline.
The contract covers B1/B2/B3 exhaustion causes, every nonempty cause set, both first-occurrence
orders for each pair, all six first-occurrence orders for three causes, stable success and
ordinary RPC/read failure.

The false `ts/src/signer/protocol.ts` claim that a signed refusal “detail” distinguishes chain
conditions is an explicit **excluded dependency owned by Batch D / D-F6 / C5**. There is no such
wire field. Batch C must not edit it, invent a signed detail, or split
`SIGNER_CHAIN_UNSTABLE` into new public reason codes. Its current FATAL tier and remedy remain.

## 2. Independently derived branches

`SNAPSHOT_ATTEMPTS` is five and each successful pin drives eleven state/code reads.

| State | End condition | Reads in that attempt | Required fact |
|---|---|---:|---|
| B0 | initialization | 0 | no cause has yet been observed |
| B1 | `head.hash === null` before reads | 0 | pending head before reads; no movement/read claim |
| B2a | confirmation height differs | 11 | head moved after pinned reads |
| B2b | height equal, confirmation hash differs | 11 | same-height reorg after pinned reads |
| B3 | hashed head + reads + `confirm.hash === null` | 11 | pending confirmation after pinned reads; not movement |
| B4 | five attempts exhausted | sum of attempts | exact message for the complete observed cause set |
| B5 | confirmation height/hash match | 11 | return the exact hashed pin and snapshot |

`pendingOnly` remains `true` exactly for pure B1. Any hashed-head attempt, including B3, makes the
exhausted run non-pure and therefore `false`.

## 3. Finite exact full-message contract

The corrected oracle accepts exactly one complete message for each nonempty cause set. It does not
attempt to infer semantic truth from keyword presence. `${SNAPSHOT_ATTEMPTS}` below is the runtime
constant and must appear as the exact component `${SNAPSHOT_ATTEMPTS} attempts`.

| Cause set | Exact full message |
|---|---|
| B1 | `no finalised head after 5 attempts: every observation returned a pending block with no hash, so there was nothing to anchor to` |
| B2 | `no stable block after 5 attempts: the head moved or was replaced under each pinned read` |
| B3 | `no finalised confirmation after 5 attempts: every pinned snapshot was followed by a pending confirmation with no hash` |
| B1+B2 | `no stable block after 5 attempts: the run observed a pending head before reads and a head that moved or was replaced after pinned reads` |
| B1+B3 | `no finalised snapshot after 5 attempts: the run observed a pending head before reads and a pending confirmation with no hash after pinned reads` |
| B2+B3 | `no stable snapshot after 5 attempts: the run observed a head that moved or was replaced after pinned reads and a pending confirmation with no hash after pinned reads` |
| B1+B2+B3 | `no stable snapshot after 5 attempts: the run observed a pending head before reads, a head that moved or was replaced after pinned reads, and a pending confirmation with no hash after pinned reads` |

The B1 and B2 messages are byte-compatible with the current implementation and its existing pure
tests. The four explicit oracle-negative controls prove the helper rejects: a negated expected
cause, `50 attempts`, a message adding an unobserved cause, and false universal wording for a
mixed run.

## 4. Exhaustive order and repetition matrix

The patch contains 22 tests:

- one stable-success control;
- pure B1, pure B2a, pure B2b and pure B3;
- B1→B2 and B2→B1, B1→B3 and B3→B1, B2→B3 and B3→B2;
- all six first-occurrence permutations of B1/B2/B3;
- one ordinary RPC/read-failure control; and
- four oracle-negative controls.

Every five-attempt route declares its exact latest-lookup and pinned-read totals independently of
the helper's arithmetic. Every mixed route repeats causes after an order change. Every mixed route
containing B2 drives both moved-height B2a and same-height-reorg B2b. This catches rank-gated,
reset-on-repeat and drop-on-later-cause accumulators instead of generalising from one canonical
ordering.

## 5. Frozen instruments

| File | Role |
|---|---|
| `TESTS.patch` | Adds one independent 485-line TypeScript file with the 22 cases above; sha256 `c2a53a4707d62c3e6632405037d684216c8319dd79fdaad15da2c15de6c69de1`. |
| `mutate.py` | Applies eight exact typecheck-clean baseline oracle mutations, including negation, rank-order and reset-on-repeat; sha256 `223e784d3804aad8fb7e9a12424c94d19a60418ad4905c3959bcfc707123b4f8`. |
| `mutation-matrix.tsv` | Exact final totals, intended named catches and raw-output hashes. |
| `RUNBOOK.md` | Reproduction commands for isolated clones only. |

The behavioral baseline remains the live collapse mutant for B3 and every mixed cause set. The
otherwise-correct rank and reset accumulator mutants establish that the expanded routes, rather
than generic baseline rejection, observe F2 and repetition loss causally.

## 6. Contract the implementer receives

The implementer may:

1. apply `TESTS.patch` unchanged; and
2. make the smallest coherent change inside the two declared `vault.ts` symbols that satisfies
   the finite message and order-independent accumulation contract.

The tests prescribe no counter, set, flags, helper, constructor rewrite or new exported cause
object. The implementer must preserve the exported class, compatible current constructor call
shapes and `pendingOnly`. The implementer may not edit the frozen test, any existing test,
`protocol.ts`, `attest.ts`, public reason vocabulary or tiers, `scripts/test.sh`, floors,
maintained claims, prior evidence, review record or signed material.

## 7. Fixed success condition

Batch C implementation readiness holds only if:

- `TESTS.patch` applies unchanged and all 22 new tests pass;
- the full TypeScript suite and typecheck pass without shrinking or weakening tests;
- all eight typecheck-clean mutants are caught at their named assertion;
- the unchanged top-level fast gate passes with the new tests included;
- protected and excluded files stay unchanged; and
- repository/workspace guards report no new finding.

No post-repair pass is claimed here; it is deferred to implementation. Per D-058(9), a future
implementation failure permits one bounded product-code correction under this same contract, not
a test edit or scope expansion.
