# C-SNAPSHOT — corrected coverage and limits

## 1. Test-to-route mapping

Every exhaustion fixture has exactly five attempt outcomes. The mock records the real JSON-RPC
requests issued by `createChainReader`. Each case supplies independently declared latest/read
totals; the helper first checks its own arithmetic against those declarations, then checks actual
requests, and only then considers error properties or messages.

| Test | Exact attempt sequence | Latest | Reads | Baseline |
|---|---|---:|---:|---|
| stable | B5 | 2 | 11 | pass control |
| pure B1 | B1 B1 B1 B1 B1 | 5 | 0 | pass control |
| pure B2a | B2a B2a B2a B2a B2a | 10 | 55 | pass control |
| pure B2b | B2b B2b B2b B2b B2b | 10 | 55 | pass control |
| pure B3 | B3 B3 B3 B3 B3 | 10 | 55 | **named fail** |
| B1→B2 | B1 B2a B1 B2b B2a | 8 | 33 | **named fail** |
| B2→B1 | B2a B1 B2b B1 B2a | 8 | 33 | **named fail** |
| B1→B3 | B1 B3 B1 B3 B3 | 8 | 33 | **named fail** |
| B3→B1 | B3 B1 B3 B1 B3 | 8 | 33 | **named fail** |
| B2→B3 | B2a B3 B2b B3 B2a | 10 | 55 | **named fail** |
| B3→B2 | B3 B2a B3 B2b B3 | 10 | 55 | **named fail** |
| B1→B2→B3 | B1 B2a B3 B2b B1 | 8 | 33 | **named fail** |
| B1→B3→B2 | B1 B3 B2a B1 B2b | 8 | 33 | **named fail** |
| B2→B1→B3 | B2a B1 B3 B1 B2b | 8 | 33 | **named fail** |
| B2→B3→B1 | B2a B3 B1 B2b B1 | 8 | 33 | **named fail** |
| B3→B1→B2 | B3 B1 B2a B1 B2b | 8 | 33 | **named fail** |
| B3→B2→B1 | B3 B2a B1 B1 B2b | 8 | 33 | **named fail** |
| ordinary read failure | hashed pin, first RPC read rejects | 1 before failure | not an exhaustion count | pass control |

Four non-route oracle controls make 22 tests total. B2a and B2b are pure controls and both occur
in every applicable mixed route. Every mixed route repeats at least one already-seen cause after
another cause has appeared, so a set cleared or narrowed on repetition cannot survive.

## 2. Exact error oracle

After route reachability, the oracle checks:

- the thrown value is specifically `ChainUnstableError`;
- `pendingOnly` is true exactly for pure B1;
- the message contains the exact contextual component `5 attempts`; and
- the entire message is byte-equal to the one finite sentence keyed by the expected nonempty
  canonical cause set.

This intentionally gives up open-ended wording equivalence. Natural-language regex presence
cannot prove that a phrase asserts rather than negates a fact, and a blacklist cannot enumerate
false universals. The exact seven-sentence grammar is the smaller truthful contract.

The four negative controls call the actual oracle with fabricated errors and require its named
assertion to reject:

1. `no pending block ... was observed` when B1 occurred;
2. an otherwise pure-B1 sentence using `50 attempts`;
3. the exact B1+B2 sentence when only B1 occurred; and
4. a B1+B2 sentence claiming every attempt ended both ways.

The ordinary-error control requires a non-`ChainUnstableError` carrying the scripted RPC failure
and verifies one initial lookup with no confirmation lookup or unstable-snapshot retry. Transport
retries inside the RPC client are not counted or constrained. This prevents the suite from making
every failure satisfy the unstable-chain contract.

## 3. Order, repetition and mutation discrimination

All pair first-occurrence directions and all six three-cause permutations are driven. Cause-set
messages are canonical and therefore intentionally independent of encounter order.

The corrected exact matrix contains eight typecheck-clean mutants:

- B1 reclassified as movement: pure B1 property control fails incrementally;
- B2 reclassified as pending: both height-movement and reorg controls fail incrementally;
- B3 reclassified as movement: pure B3 advances beyond its baseline property failure and fails
  the exact B3 sentence;
- pure B1/B2 messages swapped: all three pure message controls fail incrementally;
- messages collapsed to generic: all sixteen exhaustion sentences fail;
- pure B1 message negated while retaining its keywords and `5 attempts`: the exact B1 control
  fails incrementally;
- an otherwise-correct rank-gated accumulator: three reversed pairs and five non-ascending
  triples fail, while every pure and ascending-order case passes; and
- an otherwise-correct accumulator that clears on a repeated cause after mixing: all twelve
  mixed routes fail, while every pure and oracle-negative control passes.

All eight mutations typecheck. Compile or warning/typecheck failure is not counted as a catch.
The last two mutants causally isolate F2 and repeat loss rather than receiving credit for the
baseline's already-known message collapse.

## 4. Explicit Batch D dependency

`protocol.ts`, `Refusal`, `RefusalRecord`, `attest.ts`, signer startup/status output and the
historical A-077 sentence are outside this production boundary. C5/ADJ4 establishes that no
signed refusal detail carries the `ChainUnstableError` property or message. Therefore this card
proves reader-error accuracy only; it does not claim that a signed refusal distinguishes B1/B2/B3.

Batch D owns correcting the false current `protocol.ts` statement and superseding the dated
historical claim. Batch C must neither double-own those words nor build machinery to make them
true.

## 5. Exclusions and blind spots

- Completeness is only for the two declared symbols and the enumerated branch/category order
  space. No repository-wide state-machine or RPC-completeness claim is made.
- Five attempts limit the concrete repetition sequences. The rank and reset mutants discriminate
  the two supported accumulation hazards; this is not an exhaustive proof against arbitrary
  malicious accumulator algorithms.
- A hashless `latest` response is driven through a scripted JSON-RPC node. Reachability at any
  specific production provider or real Anvil is not established.
- The tests prove request routes and classification of scripted replies. They do not certify a
  provider's historical-state correctness, finality, reorg policy or honesty.
- No retry backoff, recency policy, timeout, new reason code, signed detail, telemetry or public
  output is required or evaluated.
- No constructor-specific implementation, new exported cause type or new error property is
  required. Exact full messages are required.
- No post-repair run, deep gate, implementation verification, D-055 assessment, signing,
  certification, ratification, publication, rename or push is performed.
