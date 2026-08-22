# C-SNAPSHOT — twice-corrected coverage and limits

## 1. Retained named test-to-route mapping

Every exhaustion fixture has exactly five attempt outcomes. The mock records the real JSON-RPC
requests issued by `createChainReader`. Each named case supplies independently declared
latest/read totals; the helper checks its arithmetic against those declarations, then actual
requests, then error properties and exact message.

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

Four non-route oracle controls make the retained named total 22. These cases still preserve both
pair directions, all six triple first-occurrence permutations, repetitions and explicit B2a/B2b
routes.

## 2. Finite exhaustive late-first/repeat matrix

One additional aggregate top-level test enumerates every length-five category sequence in lexical
base-three order over `[B1, B2, B3]`: `3^5 = 243`. Each category sequence executes twice:

- polarity A maps successive B2 occurrences to B2a, B2b, B2a, …;
- polarity B maps them to B2b, B2a, B2b, ….

That is **486 real reader routes**, not fabricated error objects. A single B2 is B2a in one route
and B2b in the other. Repeated B2 alternates mechanisms under both starting polarities.

For each route, expected values are independently calculated from its five categories:

- `latest = B1 count + 2 × non-B1 count`;
- `reads = 11 × non-B1 count`;
- expected cause set is the canonical set of categories actually present.

The route helper then independently re-derives counts from the concrete B1/B2a/B2b/B3 attempt
sequence and compares actual RPC calls. Across the whole matrix this is 2,430 attempts: 810 B1
attempts, 405 B2a, 405 B2b and 810 B3; therefore 4,050 latest lookups and 17,820 pinned reads.
Cause-set coverage is six pure routes, 180 two-cause routes and 300 three-cause routes.

Execution, route and classification errors are caught per subcase and appended. The aggregate
does not fail fast. Its final assertion reports:

`attempted=486/486 observed=486/486 route-verified=486/486 classification-checked=486/486`

The exact accumulator control proves all four counters at 486/486 with zero failures. Baseline
reports the same four counters and 482 classification failures. Thus a red aggregate does not
hide an early-abort subset.

## 3. Exact error oracle

After route reachability, the oracle checks:

- the thrown value is specifically `ChainUnstableError`;
- `pendingOnly` is true exactly for pure B1;
- the message contains the exact contextual component `5 attempts`; and
- the entire message is byte-equal to the one finite sentence keyed by the expected nonempty
  canonical cause set.

The four negative controls call the actual oracle with fabricated errors and require its named
assertion to reject: negated B1, unrelated `50 attempts`, an extra cause and a mixed false
universal. The ordinary-error control requires a non-`ChainUnstableError` carrying the scripted
RPC failure and verifies one initial lookup without an unstable-snapshot retry.

## 4. Typecheck-clean discrimination

Ten driver cases plus the live baseline are measured. All typecheck with exit 0; compile or
warning/typecheck failure receives no behavioral credit.

The retained defects remain discriminated:

- B1-as-movement, B2-as-pending and B3-as-movement path substitutions;
- swapped pure messages, generic collapse and negated B1 wording;
- an otherwise-correct rank-gated accumulator; and
- an otherwise-correct reset-on-repeat accumulator.

Two second-correction witnesses are added:

- **exact accumulator CONTROL:** 23/23 top-level tests pass, exhaustive 486/486 with zero subcase
  failures;
- **freeze after first repeat:** 22/23 pass; all original named 22 remain green; only the
  exhaustive aggregate fails, with 276 classification subcases caught after full 486/486
  traversal.

The freeze mutant stops accepting new causes after the first repeated cause. The retained 22
completed their cause set before that repeat, so their green result reproduces Review 2's hole.
Late-arrival sequences in the exhaustive domain kill it causally. Rank and reset are recalibrated
to 14/9 and 10/13 because their prior named failures remain and the aggregate adds one top-level
failure.

## 5. Explicit Batch D dependency

`protocol.ts`, `Refusal`, `RefusalRecord`, `attest.ts`, signer startup/status output and
the historical A-077 sentence are outside this production boundary. C5/ADJ4 establishes that no
signed refusal detail carries the `ChainUnstableError` property or message. This card proves
reader-error accuracy only; it does not claim that a signed refusal distinguishes B1/B2/B3.

Batch D owns correcting the false current `protocol.ts` statement and superseding the dated
historical claim. Batch C must neither double-own those words nor build machinery to make them
true.

## 6. Exclusions and blind spots

- Completeness is limited to the two declared symbols and the fixed five-attempt B1/B2/B3
  exhaustion category domain. No repository-wide state-machine or RPC-completeness claim is made.
- The exhaustive matrix covers both alternating B2 mechanism polarities, not every arbitrary
  B2a/B2b arrangement. Classification is intentionally cause-category based; pure and named mixed
  controls separately bind both mechanisms.
- A hashless `latest` response is driven through a scripted JSON-RPC node. Reachability at any
  specific production provider or real Anvil is not established.
- The tests prove request routes and classification of scripted replies. They do not certify a
  provider's historical-state correctness, finality, reorg policy or honesty.
- Transport retries inside the RPC client are not counted or constrained.
- No retry backoff, recency policy, timeout, new reason code, signed detail, telemetry or public
  output is required or evaluated.
- No constructor-specific implementation, exported cause type or new error property is required.
  Exact full messages are required.
- No post-repair run, deep gate, implementation verification, D-055 assessment, signing,
  certification, ratification, publication, rename or push is performed.
