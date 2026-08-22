# C-SNAPSHOT — twice-corrected frozen independent test contract

**Verdict: HOLD for corrected test-contract readiness only, pending fresh independent review.**
This is not implementation approval, a gate signature, certification, ratification, publication,
rename, D-055 assessment or push authorization.

**Behavioral baseline:** `1655b120a653b60ccb5b3a22583c0001d59ea7a4` (tree
`b2c8fb1e53d35ea40655dc83faa61f8a76dd4f78`). The independent test author wrote none of the
future Batch C implementation.

**Correction chain:** independent review commit
`8834d9b868657fbccfe1009bf139e23dc8e06db1` returned FAIL on lexical message matching and
canonical-only first-occurrence routes. The first bounded correction closed those findings.
Independent review commit `71cfa70b8267d5e2950af99307abf372992c008b` then returned FAIL
because the 22 named routes completed each mixed cause set before its first repeat. This second
bounded instrument correction closes that finite late-first/repeat hole. Neither correction
consumes a D-058(9) implementation attempt. `INSTRUMENT-REVIEW-1.md` and
`INSTRUMENT-REVIEW-2.md` are preserved byte-for-byte.

**Authority:** D-058(1), (8)C and (9); D-059(5)–(6); D-060(1); D-066(2)–(3).

This directory is the complete test-only deliverable. `TESTS.patch` is preserved but not applied
in this commit. No production source, existing test, `scripts/test.sh`, `protocol.ts`,
maintained claim, floor, prior evidence, review record or signed material is changed.

## 1. Declared production boundary

Completeness is claimed only for `ChainUnstableError` and
`createChainReader(...).readVaultState` in `ts/src/signer/vault.ts`, at the behavioral
baseline. The contract covers B1/B2/B3 exhaustion causes, every nonempty cause set, the retained
named order fixtures, and every length-five B1/B2/B3 category sequence under both deterministic
B2 mechanism polarities. Stable success and ordinary RPC/read failure remain controls.

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

`pendingOnly` remains `true` exactly for pure B1. Any hashed-head attempt, including B3,
makes the exhausted run non-pure and therefore `false`.

## 3. Finite exact full-message contract

The oracle accepts exactly one complete message for each nonempty cause set, and binds the runtime
component `5 attempts`.

| Cause set | Exact full message |
|---|---|
| B1 | `no finalised head after 5 attempts: every observation returned a pending block with no hash, so there was nothing to anchor to` |
| B2 | `no stable block after 5 attempts: the head moved or was replaced under each pinned read` |
| B3 | `no finalised confirmation after 5 attempts: every pinned snapshot was followed by a pending confirmation with no hash` |
| B1+B2 | `no stable block after 5 attempts: the run observed a pending head before reads and a head that moved or was replaced after pinned reads` |
| B1+B3 | `no finalised snapshot after 5 attempts: the run observed a pending head before reads and a pending confirmation with no hash after pinned reads` |
| B2+B3 | `no stable snapshot after 5 attempts: the run observed a head that moved or was replaced after pinned reads and a pending confirmation with no hash after pinned reads` |
| B1+B2+B3 | `no stable snapshot after 5 attempts: the run observed a pending head before reads, a head that moved or was replaced after pinned reads, and a pending confirmation with no hash after pinned reads` |

B1 and B2 remain byte-compatible with current pure-case tests. Four oracle-negative controls reject
negation, an unrelated `50 attempts`, an extra unobserved cause and false universal wording.

## 4. Named and exhaustive matrix

The patch contains 23 top-level tests:

- the retained 22 named tests: stable success; pure B1/B2a/B2b/B3; both directions for every pair;
  all six three-cause first-occurrence permutations; ordinary RPC failure; four oracle controls;
- one aggregate exhaustive test over all `3^5 = 243` category sequences; and
- for every sequence, two deterministic B2 polarities, for **486 real reader routes**.

In the first variant, each B2 alternates B2a/B2b starting with moved-height; the second alternates
starting with same-height reorg. Thus a single B2 is independently B2a and B2b, and repeated B2
exercises both mechanisms with both starting polarities. Every route computes and verifies exact
actual latest-lookup and pinned-read counts. Execution, route and classification failures are
aggregated so all subcases continue; the final assertion exposes four independent 486/486
traversal counters.

## 5. Frozen instruments

| File | Role |
|---|---|
| `TESTS.patch` | Adds one independent 603-line TypeScript file with 23 top-level tests and 486 exhaustive routes; sha256 `b6fc3c713e97c2fdfc328516eeb42fdb4f3cc25d0648602ea654e6cf1513c9f1`. |
| `mutate.py` | Applies ten exact typecheck-clean driver cases: eight defects plus an exact accumulator control and the late-repeat freeze mutant; sha256 `f404a5ffe7d00a8d4978cd235c3c2a57c62a6e332a8d7106699db5eddd45ef2f`. |
| `mutation-matrix.tsv` | Exact top-level totals, 486-route traversal/subcase totals and raw-output hashes. |
| `RUNBOOK.md` | Reproduction commands for isolated clones only. |

The exact accumulator control passes 23/23 and proves 486/486 traversal. The otherwise-correct
freeze-after-first-repeat mutant keeps the original 22 named tests green but fails only the
aggregate exhaustive test, with 276 discriminated subcase failures. It is the causal witness for
the Review 2 hole.

## 6. Contract the implementer receives

The implementer may apply `TESTS.patch` unchanged and make the smallest coherent change inside
the two declared `vault.ts` symbols. The tests prescribe no counter, set, flags, helper,
constructor rewrite or new exported cause object. The exported class, compatible constructor call
shapes and `pendingOnly` must remain. Frozen tests, existing tests, `protocol.ts`,
`attest.ts`, public reason vocabulary and tiers, gates, floors, maintained claims, prior evidence,
review records and signed material may not change.

## 7. Fixed success condition

Batch C implementation readiness holds only if:

- `TESTS.patch` applies unchanged and all 23 top-level tests pass, including 486/486 exhaustive
  reader routes;
- the full TypeScript suite and typecheck pass without shrinking or weakening tests;
- every typecheck-clean defect is caught at its named assertion and the exact control stays green;
- the unchanged top-level fast gate passes with the new tests included;
- protected and excluded files stay unchanged; and
- repository/workspace guards report no new finding.

No post-repair pass is claimed here; it is deferred to implementation. Per D-058(9), a future
implementation failure permits one bounded product-code correction under this same contract, not
a test edit or scope expansion.
