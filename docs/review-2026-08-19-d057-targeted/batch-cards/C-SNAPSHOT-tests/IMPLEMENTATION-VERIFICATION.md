# C-SNAPSHOT — independent final implementation verification

# VERDICT: HOLD

The exact implementation candidate
`317702e5ba32db680d31f6be8b52ec631555e422` holds the twice-corrected frozen
C-SNAPSHOT contract. The candidate has one implementation attempt. No correction attempt was
needed. This is a HOLD for this exact candidate and declared two-symbol boundary only; it is not
a gate signature, approval, certification, ratification, publication, rename, D-055 assessment or
push authorization.

I authored neither the C-SNAPSHOT instrument and test patch nor this implementation. I changed no
production source, test, instrument, prior review, gate, floor, maintained claim, decision or
signed material during verification. This standalone record is the only tracked review change.

## 1. Frozen identity, scope and patch fidelity

| Item | Independently verified identity |
|---|---|
| implementation candidate | `317702e5ba32db680d31f6be8b52ec631555e422` |
| candidate parent / A-092 | `0aa60625bd50d4e848500a113c52170343563ef5` |
| candidate tree | `d5fb8206715a0c340430019da49eee492f9689da` |
| frozen `TESTS.patch` | sha256 `b6fc3c713e97c2fdfc328516eeb42fdb4f3cc25d0648602ea654e6cf1513c9f1` |
| added test source | 603 lines; sha256 `29a673560e89b639b6635661706a368454c9969a04c5d37c4f6c15229df3dd8a` |
| held instrument review | `c06833d5c0755f91f59de6f445f9c28c7086330a`; review-file sha256 `68fc0d6b5aaa510b22c37fe57a08110a8db62fbeb45e5c8f08248d99601e8f22` |

The exact parent-to-candidate diff is only:

- modified `ts/src/signer/vault.ts`, with every changed line inside exported
  `ChainUnstableError` or `createChainReader(...).readVaultState`; and
- added `ts/test/vault.snapshot.classification.test.ts`.

In a detached clone of the exact parent, `git apply --check TESTS.patch` and `git apply
TESTS.patch` passed. `cmp` against the candidate's added test returned equal and the extracted
file reproduced the frozen source hash above. `git diff --check` passed. There is no third
candidate surface.

## 2. Independent implementation reading

The implementation uses a three-bit cause mask: B1 pending head before reads is `1`, B2 moved
height or same-height replacement after pinned reads is `2`, and B3 hashless confirmation after
pinned reads is `4`. Each exhaustion branch ORs its bit into one method-local mask. The mask is
never reset, toggled or frozen, so order, repetition and first-arrival position cannot discard an
earlier or later cause. Both B2 mechanisms share only B2. Every attempt either records B1/B2/B3,
returns a stable snapshot, or propagates a read/RPC exception, so five normal exhausted attempts
cannot reach the constructor with an empty mask.

`ChainUnstableError.messageFor` maps masks 1 through 7 to the seven frozen complete sentences.
`pendingOnly` is true exactly for mask 1. Direct probes of the exported constructor confirmed
byte-compatible current calls:

- `new ChainUnstableError(5)` and `(5, false)` retain the pure-B2 message and
  `pendingOnly === false`;
- `(5, true)` retains the pure-B1 message and `pendingOnly === true`; and
- the class name, `Error` inheritance and `ChainUnstableError` identity remain intact.

The stable snapshot's read/return block is unchanged. A rejected pinned read still escapes the
`Promise.all` immediately and is not converted to chain instability. The focused stable and
ordinary-error controls, the pre-existing vault-anchor tests, the complete TypeScript suite and
both top-level gates corroborate those static boundaries.

## 3. Focused and frozen calibration results

Commands run against the exact candidate:

```text
npm --prefix ts run typecheck
node --test --test-concurrency=1 ts/test/vault.snapshot.classification.test.ts
```

Typecheck exited 0 with no diagnostic. The focused suite passed **23/23**. Its exhaustive test
completed the real-reader matrix named **486/486**, with all 23 top-level names green, including
stable success, pure B1, B2a, B2b and B3, all ordered pairs and triples, ordinary RPC propagation
and four negative-message controls.

I also replayed the complete frozen driver independently against its exact behavioral source and
freshly extracted test. Every row typechecked at exit 0 and completed all four exhaustive counters
at 486/486. The measured totals matched the frozen matrix exactly:

| Frozen row | Pass / fail | Exhaustive classification failures |
|---|---:|---:|
| live baseline | 9 / 14 | 482 |
| B1 classified as movement | 8 / 15 | 484 |
| B2 classified as pending | 7 / 16 | 484 |
| B3 classified as movement | 9 / 14 | 482 |
| pure messages swapped | 6 / 17 | 486 |
| generic message collapse | 6 / 17 | 486 |
| negated pure B1 | 8 / 15 | 484 |
| exact accumulator control | **23 / 0** | **0** |
| rank-order accumulator | 14 / 9 | 340 |
| reset-on-repeat accumulator | 10 / 13 | 360 |
| freeze after first repeat | **22 / 1** | **276** |

Named output was inspected, not inferred from totals: the three path mutations incrementally
failed their corresponding pure routes; the message mutations failed exact-message assertions;
rank failed the reversed-order fixtures; reset failed the repeated mixed fixtures; and freeze
left all original 22 names green and failed only the exhaustive aggregate.

## 4. Fresh candidate-specific attacks

I mutated the actual candidate only in a private detached scratch clone. Each attack was a
minimal TypeScript-clean defect, restored before the next. Every typecheck exited 0, every test
run traversed all four 486/486 counters, and every defect was rejected behaviorally:

| Candidate mutation | Pass / fail | Aggregate failures | Causal observation |
|---|---:|---:|---|
| drop B1 collection | 11 / 12 | 422 | pure B1 and B1-mixed routes fail |
| drop B2 collection | 10 / 13 | 422 | both pure B2 mechanisms and B2-mixed routes fail |
| drop B3 collection | 11 / 12 | 422 | pure B3 and B3-mixed routes fail |
| swap the B2/B3 mask bits | 15 / 8 | 124 | pure B2a, B2b and B3 plus affected mixes fail |
| swap the B1+B3 and B2+B3 message cases | 18 / 5 | 120 | exactly the affected pair names and aggregate fail |
| assign B1 instead of ORing it | 16 / 7 | 260 | late B1 resets prior causes; triple names and aggregate fail |
| XOR every cause bit on repetition | 10 / 13 | 360 | repeated mixed routes and aggregate fail |
| freeze the mask after its first repeated cause | **22 / 1** | **276** | only exhaustive late-first-arrival coverage fails |

These attacks cover dropped B1/B2/B3 collection, swapped masks and messages, order-dependent
reset, repeat toggling and the prior late-first/freeze sibling on the candidate's actual bit-mask
shape. I found no surviving plausible minimal sibling inside the declared finite domain.

## 5. Ordinary and isolated deep gates

The ordinary `./scripts/test.sh` was rerun at the exact shared candidate and returned exit 0:

```text
foundry: 103 tests (floor 92)
C-SNAPSHOT exhaustive branch classification: 23/23, exhaustive name 486/486
typescript: 550 tests (floor 527)
suite 221 (floor 221) · samples 7 (floor 7) · tamper 78/30 (floors 78/30)
GATE PASSED
```

The captured clean-rerun log has sha256
`5cc6172129eed93ca44d1944ba5a7b61c23e2e1713afe5d2b26e8fe85aafdc11`.

For the required final evidence I created a no-hardlink, detached clone at the exact candidate,
set the canonical repository origin expected by the rename guard, staged `forge-std` at
`bf647bd6046f2f7da30d0c2bf435e5c76a780c1b` and OpenZeppelin at
`5fd1781b1454fd1ef8e722282f86f9293cacf256`, copied the existing ignored TypeScript dependency
tree, confirmed the root clean and confirmed no other gate process was present. Alone in that
clone, `./scripts/test.sh --gate` returned exit 0. Direct body inspection found:

```text
foundry: 103/103 (floor 92)
C-SNAPSHOT: 23/23; exhaustive real-reader route name 486/486
typescript: 550/550 (floor 527)
corpus: 50 fixtures; committed views verified file by file
corpus results: 51 files identical to the committed set
ablation report: byte-identical regeneration
verifier: 221; samples 7; tamper 78 cases / 30 modes
GATE PASSED
```

The isolated clone remained clean after the run and still resolved the exact candidate, tree and
parent. The preserved deep log has sha256
`962881e18952c97215d5a1543ad86e9e4b3f73a1b42cea92e2c053875ef626c5`.

### Setup disclosures

The first ordinary-gate capture executed the complete gate body and printed `GATE PASSED`, but my
outer zsh wrapper then tried to assign the shell's read-only `status` variable. I did not count
that wrapper result; I corrected the wrapper and reran the complete ordinary gate cleanly to the
exit-0 result above. During isolated setup, a dependency symlink appeared as an untracked entry;
it was removed and replaced with an ignored copied dependency tree before the deep gate began.
No deep-gate result was taken from an unclean clone.

## 6. Protected boundaries and guards

The parent-to-candidate protected diff is empty for the frozen instrument and reviews, existing
tests, `protocol.ts`, `attest.ts`, signer server/main, `ts/package.json`, `scripts/test.sh`, the
proposal, decisions, both signed gate packs and prior evidence. Relevant retained hashes are:

- `protocol.ts` `87fc5204…`, `attest.ts` `fb8d90a3…`;
- `scripts/test.sh` `66c272b9…`, `ts/package.json` `a22d252c…`;
- proposal `322cd96f…`, signed Gate S1 `25dcefca…`, signed Gate S2 `833671b8…`.

This preserves the one public `SIGNER_CHAIN_UNSTABLE` code and FATAL tier. The known false current
`protocol.ts` sentence claiming a refusal detail distinguishes the conditions is unchanged and
remains exclusively Batch D-owned; this HOLD does not repair it or claim the reader message
reaches a signed refusal. All fifteen frozen instrument checksums passed.

Repository checks passed: working and staged secret guards; review scope **587/587** assigned
(R1 388 / R2 47 / R3 152; 205 remediation files assigned); findings ledger totals; all six
single-sourced floor values; vendor mechanical checks; diff checks; and clean status. The
workspace guard passed with **13 machine-state findings baselined and 0 new**. That is ratcheted
evidence, not a claim that the accepted findings are absent.

## 7. Limits carried with this HOLD

- Coverage is finite to the five-attempt B1/B2/B3 category domain and the two declared symbols.
  The exhaustive matrix alternates B2a/B2b under both starting polarities; it does not enumerate
  every arbitrary B2 mechanism string.
- The reader routes use a scripted local JSON-RPC node. They do not establish provider honesty,
  historical-state correctness, finality or reorg policy, or reachability of a hashless latest
  response on a particular production provider.
- Transport retries, retry backoff, timeouts, recency policy, telemetry and new public reason
  vocabulary are outside this contract.
- The TypeScript floor remains **527 while 550 execute**, and the Foundry floor remains **92 while
  103 execute**. Those floor reconciliations are Batch A-owned and are not hidden closure here.
- Batch D's maintained-claim repair remains open. D-055 and every other unfinished batch are not
  assessed by this review.

**HOLD** for exact candidate `317702e5ba32db680d31f6be8b52ec631555e422` within the frozen
C-SNAPSHOT boundary.
