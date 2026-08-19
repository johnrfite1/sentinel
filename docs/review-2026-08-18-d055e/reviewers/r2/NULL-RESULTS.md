# REVIEWER 2 — NULL RESULTS

What I probed and found SOUND, so the next round knows where not to look again.
Commit `7e0ab7f1057de278c09cc803ab4ca266f53399e1`. Every mutation below was applied to the
worktree, run, reverted, and the revert verified with `cmp` against a pristine copy (never with
`git checkout`). The runner is `probes/mutate.sh`.

## N1 — A-072's call-graph pinning: all THREE parts hold

Register §13.4 records `C-3` as **FIXED (A-068), pinned end to end by A-072 — the pure walk, the
tracer name, and the mapping into `SimulationResult`**. My brief asks whether all three are pinned
or only the ones the finding named. **All three are pinned**, each by a differently-named test:

| mutation | file | result |
|---|---|---|
| delete `walk(child)` from `internalCalls` (kill the recursion) | `ts/src/simulate/anvil.ts:114` | **CAUGHT** — `maps every descendant of the fetched trace into the result, not just the top level` fails with a concrete diff (the DELEGATECALL descendant is missing) |
| `tracer: "callTracer"` → `"prestateTracer"` | `ts/src/simulate/anvil.ts:96` | **CAUGHT** — `asks the node for a callTracer trace, which is the only tracer that reports calls` fails, and `the call graph PIPELINE is asserted end to end (A-072)` fails alongside it |
| `internalCalls(callTrace).map` → `(callTrace.calls ?? []).map` (top level only) | `ts/src/simulate/index.ts:261` | **CAUGHT** — `maps every descendant of the fetched trace into the result` fails |

Notably, the pure walk and the mapping are killed by *different* assertions rather than by one test
covering both, which is what makes the third pin real rather than incidental.

**Bound on this null:** these are unit-level pins over hand-built traces. Register §14 already
records that `EVAL_CALL_GRAPH_EXPECTED` is asserted by no corpus fixture and no sample, so the pins
prove the walk and the plumbing, not that a real node's trace is faithfully consumed. See
`R2-F5` for a defect in what the evaluator does with an empty result.

## N2 — the E3 anchor comparison compares BOTH fields, and the tier is pinned

| mutation | result |
|---|---|
| drop the hash half: `evaluation.simulationBlockNumber !== state.observedAtBlock \|\| evaluation.simulationBlockHash !== state.observedBlockHash` → number only (`attest.ts:440-443`) | **CAUGHT** — `compares the anchor's HASH, not only its height (D-055(c))` fails |
| retier `SIGNER_ANCHOR_NOT_OBSERVED: "CONFORMANCE"` → `"EXECUTABILITY"` (`protocol.ts:222`) | **CAUGHT** — `still signs a REVIEW on a superseded anchor, keeping Case 4 reachable (E3)` fails |

The second is the specific attack my brief names ("Is `SIGNER_ANCHOR_NOT_OBSERVED` reachable in a
way that makes Case 4 unreachable?"). It is not: the tier is CONFORMANCE, REVIEW stays reachable,
and a test fails the moment the tier moves one step stricter. The e2e test that asserts it also
asserts `SIGNER_SIMULATION_BLOCK_MISMATCH` is **absent**, so it cannot be passing because the old
check rejected the input — I checked that, because "rejected by a different check" is this
project's failure mode 7.

**Both E3 e2e tests genuinely ran in my baseline** (`baseline-test.txt:637-638`), against a real
Anvil, with `skipped 0`. They are not silently skipped in a worktree.

## N3 — the retry loop terminates, and pending heads produce no snapshot

`ts/src/signer/vault.ts:157-236`. `for (let attempt = 0; attempt < SNAPSHOT_ATTEMPTS; attempt += 1)`
with `SNAPSHOT_ATTEMPTS = 5`. Two `continue` arms, no `attempt` reassignment inside the body, no
`while`, no recursion, and an unconditional `throw new ChainUnstableError(...)` after the loop.
**There is no non-terminating path.** I read every branch looking for one; there is nothing that
resets the counter and nothing that awaits without a bound.

`head.hash === null` (a pending block) is handled before any read is issued (`:163-167`), so a
snapshot with a null `observedBlockHash` — which would make the anchor comparison compare against
nothing — cannot be returned. Asserted by `ABSENCE IS NOT AGREEMENT: a head with no hash produces
no snapshot`, which passed in my baseline. See `R2-F6` for the record-fidelity defect that remains.

## N4 — D-053(b)'s basis-keyed nonce guard: I could not find another shape

My brief asks whether a rotation cycle has a sibling. I tried four and **all four are closed**:

1. **Mandate cycle M1 → M2 → M1** — the finding's own shape. **CAUGHT** by mutation: reverting the
   key to `${chainId}:${vault}:${nonce}` (`attest.ts:179`) fails `a REVIEW reservation survives a
   cycle, not just an ALLOW one` and `an EXPIRED superseded reservation no longer holds the nonce
   after a cycle`.
2. **Policy cycle P1 → P2 → P1 with the mandate unchanged** — this looked like the promising one,
   because it puts two credentials under the *same* active mandate with no cycle required. It is
   closed at the vault: `contracts/src/SentinelVault.sol:314-315` reverts `PolicyNotActive` when
   `action.policyHash != activePolicyHash`, and `:337` requires `receipt.policyHash ==
   action.policyHash`. The old receipt dies on rotation exactly as the mandate case does, and the
   guard key carries `policyHash` so the cycle back finds the original reservation.
3. **REVIEW-then-rotate-then-ALLOW** (two live executable credentials under different bases) —
   closed by the same vault checks; the stale-basis receipt cannot execute.
4. **TTL shortening to free a nonce early** — `record()` (`attest.ts:220-224`) takes the later of
   the held and the new expiry, and only for the *same* `actionHash`; `release()` (`:248`) deletes
   only when the `actionHash` matches, under a key that now includes the basis. A failed request
   cannot cancel a sibling's reservation.

I also checked **unbounded map growth**, since basis-keying multiplies keys: `chainId` and `vault`
are fixed per attestor, `nonce` is forced to the vault's current value (`SIGNER_NONCE_MISMATCH` is
EXECUTABILITY and refuses both reserving verdicts), and the basis is the vault's current hashes —
none of the three is caller-chosen. `prune()` runs per request. At most one live entry per
(nonce, basis). **Not a growth surface.**

The guard's declared limits (per-process, forgotten on restart, invisible across two processes
sharing a key) are stated in `attest.ts:83-146` and are honest. I did not attack them because they
are declared, not because they are false.

## N5 — the A-043 CRITICAL guard is in the right place

`checkEvidenceDecoding`'s `if (requestedVerdict === "ALLOW") return ["SIGNER_EVIDENCE_DECODING_MISMATCH"]`
(`attest.ts:689`) sits at the top of the `claimed.decoded === "false"` branch, above the
`TARGET_BINDING_FAILURES` sub-branch. Deleting it is **CAUGHT** by two tests —
`refuses an ALLOW when BOTH sides fail to decode (DECODE_LENGTH_MISMATCH)` and
`(DECODE_UNSUPPORTED_SELECTOR)` — which is the branch-independence the A-043 write-up claims. The
placement is the argument-level one, not the demonstration-level one.

## N6 — the D-014 `checkEvidenceDecoding` boundary is honestly stated, and the code draws it there

My brief asks whether the boundary ("compares parameters GIVEN THE SELECTOR; does not check the
selector belongs at the target") is honestly stated everywhere and is where the code actually draws
it. **Yes, on both counts.** It is stated at `attest.ts:367-368`, at `attest.ts:647-664`, and at
`decode/index.ts:203-210`; A-074's residual (b) restates it for the verifier. The code draws it
there: `decodeBySelector` (`decode/index.ts:212-243`) takes no `target` and no `registry`
parameter, so target binding is not merely skipped, it is structurally unavailable to the signer.
It is a separate entry point rather than a flag on `decodeCall`, with the reason written down.

Absence handling inside the function is sound in every shape I could construct:
non-JSON, JSON `null`, a JSON array, a top-level scalar, a missing
`decodedSelectorAndParameters`, a non-object claim, `decoded` as a boolean rather than the string
`"true"`, a missing `parameters`, and a `parameters` object missing an expected key all produce a
FATAL `SIGNER_EVIDENCE_DECODING_ABSENT` or `_MISMATCH`. I traced each by reading
`attest.ts:636-763`; none returns `[]`.

## N7 — the evidence bundle's `anchor` cannot silently disagree with the receipt

I expected to find the E3 hole re-openable through `evidence.anchor`, which the signer never reads.
It is closed on the verification path: `verifier/verify.py:1659-1660` requires
`anchor.blockNumber == receipt.simulationBlockNumber` and `_norm_hex(anchor.blockHash) ==
_norm_hex(receipt.simulationBlockHash)`. A-056 added the `receipt-anchor-split` tamper mode for
exactly this. **Sound as a post-hoc check, and I am not reporting it.** What is *not* closed is
that both sides of that comparison are written by the same caller and neither is derived from the
simulation — that is `R2-F2`, and it is a different claim.

## N8 — the reason-code namespace and the wire parser

Spot-checked, all sound at this commit: `SIGNER_`-prefixed caller codes are rejected at the
boundary (`protocol.ts:731-736`, the A-044 repair); `Object.hasOwn(VERDICT, verdict)` rather than
`in` (`:706`, the A-061/E1 repair); both `uint256` policy fields are inside `bounded()`
(`:644-653`, the A-068/E2 repair); odd-length hex is rejected (`:565`); lone surrogates are
rejected (`:544-549`). I re-read each against the defect it names rather than trusting the comment,
and each comment matches the code. **These are recorded fixes and I confirmed them rather than
re-reporting them.**

## N9 — the simulation leak invariant

`runSimulation`'s revert is in a `finally` and a failed revert throws `SimulationLeakError` rather
than logging (`simulate/index.ts:314-325`). The serialisation queue (`:160-171`) swallows rejection
on the chain only, so one failed simulation does not reject the next caller's turn while still
rejecting to its own caller. I read this looking for a path that returns without reverting and
found none — the only `return` is inside the `try`, so the `finally` always runs. **Sound.** Its
declared cross-process limit is stated in the docstring and is honest.
