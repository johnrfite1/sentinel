# C-SNAPSHOT — coverage and limits

## 1. Test-to-state mapping

Every exhaustion fixture has exactly five attempt outcomes. The mock records the real JSON-RPC
requests issued by `createChainReader`, so a fixture must prove it reached its declared branches
before its error classification is considered.

| Test | Attempts by cause | Latest lookups | Pinned reads | Baseline |
|---|---|---:|---:|---|
| stable success | B5 | 2 | 11 | pass control |
| pure B1 | 5 B1 | 5 | 0 | pass control |
| pure B2 movement | 5 B2a | 10 | 55 | pass control |
| pure B2 reorg | 5 B2b | 10 | 55 | pass control |
| pure B3 | 5 B3 | 10 | 55 | **named fail** |
| B1+B3 | 2 B1 + 3 B3 | 8 | 33 | **named fail** |
| B1+B2 | 2 B1 + 2 B2a + 1 B2b | 8 | 33 | **named fail** |
| B2+B3 | 2 B2a + 1 B2b + 2 B3 | 10 | 55 | **named fail** |
| B1+B2+B3 | 2 B1 + 1 B2a + 1 B2b + 1 B3 | 8 | 33 | **named fail** |
| ordinary read failure | hashed pin, RPC read rejects | 1 before failure | not used as an exhaustion count | pass control |

The arithmetic is internal to each fixture and asserted by the test. B2 movement and reorg share
one cause category but are driven independently so a height-only implementation cannot masquerade
as complete classification.

## 2. Error oracle

The oracle checks four independent dimensions after route counts establish reachability:

- the thrown value is specifically `ChainUnstableError`;
- `pendingOnly` is true exactly for pure B1;
- the message retains the five-attempt budget; and
- three independent semantic recognizers match exactly the causes that occurred.

The pending-head recognizer accepts either the frozen “pending block with no hash” wording or a
truthful “pending head before reads” equivalent. Movement accepts moved/replaced head or
same-height reorg language. Confirmation accepts pending-confirmation or confirmation-pending
language. Mixed cases additionally reject the frozen false universal phrases.

The ordinary-error control requires a non-`ChainUnstableError` carrying the scripted RPC failure
and verifies that no confirmation lookup or snapshot retry is attempted. This proves the suite did
not make every failure satisfy the unstable-chain contract.

## 3. Mutation discrimination

The exact baseline is already collapsed in four distinct ways:

- pure B3 and B1+B3 collapse into the pure-B1 flag/message;
- B1+B2 collapses into pure B2 and omits the B1 fact;
- B2+B3 collapses into pure B2 and omits B3;
- B1+B2+B3 collapses into pure B2 and omits B1/B3.

Those produce the five intended baseline failures and no control failure. Five additional exact
mutants calibrate the remaining directions:

- B1 reclassified as movement kills the pure-B1 property assertion;
- B2 reclassified as pending kills both height-movement and reorg controls;
- B3 reclassified as movement kills the pure-B3 movement-exclusion assertion;
- swapping the two existing pure messages kills both pure message controls; and
- one generic message kills all eight exhaustion message oracles.

All five mutations typecheck. Compile/typecheck failure is not counted as a behavioral catch.

## 4. Explicit Batch D dependency

`protocol.ts`, `Refusal`, `RefusalRecord`, `attest.ts`, signer startup/status output, and the
historical A-077 sentence are outside this production boundary. C5/ADJ4 establishes that no signed
refusal detail carries the `ChainUnstableError` flag or message. Therefore this card proves the
accuracy of the reader error only; it does not claim that a signed refusal distinguishes B1/B2/B3.

Batch D owns correcting the false current `protocol.ts` statement and superseding the dated
historical claim. Batch C must neither double-own those words nor build machinery to make them
true.

## 5. Exclusions and blind spots

- Completeness is only for the two declared symbols and the enumerated scripted-node states. No
  repository-wide state-machine or RPC-completeness claim is made.
- A hashless `latest` response is driven through a scripted JSON-RPC node, as the existing suite
  already does. Reachability at any specific production provider or real Anvil is not established.
- The tests prove what requests the reader makes and how it classifies their replies. They do not
  certify an RPC provider's historical-state correctness, finality, reorg policy, or honesty.
- No retry backoff, recency policy, timeout, new reason code, signed detail, telemetry, or public
  output is required or evaluated.
- No constructor-specific implementation, exact full error sentence, new exported cause type, or
  new error property is required.
- No post-repair run, deep gate, implementation verification, D-055 assessment, signing,
  certification, ratification, publication, rename, or push is performed.
