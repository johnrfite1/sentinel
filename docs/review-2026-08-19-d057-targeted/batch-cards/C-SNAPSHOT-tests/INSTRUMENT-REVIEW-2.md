# C-SNAPSHOT — FRESH INDEPENDENT CORRECTION REVIEW

# VERDICT: FAIL

The correction closes Review 1's lexical-message finding F1 and canonical-order mutant F2 as
specified. The seven exact sentences, contextual attempt count, four live oracle controls, both
pair directions, all six triple first-occurrence orders and the published rank/reset mutants all
work and reproduce.

The corrected instrument is nevertheless not ready to be held fixed. Every mixed fixture
introduces its complete cause set before its first repeated cause. An otherwise-correct,
typecheck-clean accumulator that freezes after its first repeat therefore passes all 22 frozen
tests. It then loses a cause that first appears on attempt four or five, even though those routes
have the same claimed pair/triple first-occurrence orders and are supported by the five-attempt
production loop. Four review-only late-arrival probes kill that mutant without disturbing any of
the original 22 cases.

This is a **FAIL of corrected instrument readiness only**. It is not an implementation verdict,
product approval, gate signature, certification, ratification, publication, rename, D-055
assessment or push authorization. No production source, existing test or frozen instrument file
was edited by this review.

---

## 0. Exact review identity and correction scope

| Item | Identity |
|---|---|
| exact corrected subject | `cf67c7f8ae79dd15d241bd3ca7a69707a1c94981` |
| corrected subject tree | `5d01ade40dea9cfe531ae6f616f120a0bc2759f4` |
| subject message | `C-SNAPSHOT: correct frozen classification instrument` |
| subject parent / first-review FAIL | `8834d9b868657fbccfe1009bf139e23dc8e06db1` |
| behavioral baseline | `1655b120a653b60ccb5b3a22583c0001d59ea7a4` |
| behavioral-baseline tree | `b2c8fb1e53d35ea40655dc83faa61f8a76dd4f78` |
| corrected test patch | sha256 `c2a53a4707d62c3e6632405037d684216c8319dd79fdaad15da2c15de6c69de1` |
| extracted corrected test | 485 lines; sha256 `eea8876c38545db864df36f8d75e7a10e53b47ee730d805dc4ed984f88d6c1f7` |
| corrected mutation driver | 270 lines; sha256 `223e784d3804aad8fb7e9a12424c94d19a60418ad4905c3959bcfc707123b4f8` |
| preserved Review 1 | sha256 `ffad26f2c8307aa7fcf9e2c7e18dd971eace47b955132f65222bbb1c335febf0` |
| repository state at review start | clean; HEAD was the exact corrected subject |

I authored neither the instrument, its correction nor any future implementation. I read every
corrected file, the byte-preserved `INSTRUMENT-REVIEW-1.md`, the complete corrected patch and
mutation driver, the governing D-058/D-059/D-060/D-066 material and the same frozen production,
test, R2/V3 and adjudication sources recorded in Review 1.

The exact parent-to-subject diff modifies **14 existing files**, all under
`C-SNAPSHOT-tests/`. It adds, deletes or renames none. `INSTRUMENT-REVIEW-1.md` has no diff and
has the same sha256 at the parent and corrected subject. The protected diff is empty across
production, existing tests, scripts, contracts, verifier, hooks, proposal, decisions and signed
Gate S2 material.

All 14 entries in the corrected `CHECKSUMS.sha256` verify from the repository root. The checksum
file is not self-hashed. Independent provenance checks confirm the frozen identities in
`PROVENANCE.md`, including:

- `vault.ts` sha256 `dbff956fc2fdf6698e6c94ce4261626dc40cf219b6095ff8afcda8afcadc1185`;
- `protocol.ts` sha256 `87fc5204c561d986c04cc61eb4ae9e880db113187707f7e92e2df7a334b29b33`;
- TypeScript-test tree `e29397245dadfe8c9250905d99c26c036013aacf`;
- gate blob `0c6c38ed746925d52720468865ca61eb31ae7ddd` and file sha256
  `66c272b90a16b037e3fcfc6f0d9184c48f63ac32e62538be7b6cd96a93801b79`; and
- signed Gate S2 blob `baab3e7809a46f22131ef2b609f30af1ed8eeada` and file sha256
  `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589`.

`TESTS.patch` applies cleanly to the exact behavioral baseline, adds only
`ts/test/vault.snapshot.classification.test.ts`, and extracts to the published line count and
hash. No patch is applied in the shared subject.

## 1. Review 1 F1 is closed

The correction replaces open-ended keyword recognizers with a finite test-owned table keyed by
the canonical nonempty cause set. There are exactly seven keys:

```text
B1  B2  B3  B1+B2  B1+B3  B2+B3  B1+B2+B3
```

Each maps to one complete sentence. I read each sentence independently against the route it
names. Pure B1 and B2 are byte-compatible with the current production messages. Pure B3 names a
hashed pin followed by a hashless confirmation without calling it movement. Each mixed sentence
names exactly its cause set, avoids a pure-case universal, and is canonical across encounter
orders.

`assertExactMessage` first requires the contextual component `5 attempts` and then requires
byte equality with the complete expected sentence. This closes the original false positives:
lexical negation, a false but keyword-complete universal, an extra cause and an unrelated `50`
cannot satisfy full equality.

The four oracle controls exercise the actual helper, not a copied approximation. They pass only
after observing their named assertion reject:

1. an expected B1 phrase placed under negation;
2. otherwise-compatible B1 text using `50 attempts`;
3. the exact B1+B2 sentence supplied for a B1-only set; and
4. a B1+B2 sentence falsely claiming every attempt ended both ways.

The fabricated errors use the existing one-argument constructor call shape. Current production
routes cover the two-argument form; full typecheck also covers the existing one-argument fake.
The exported class, `pendingOnly` property and both current call shapes remain compatible. The
instrument requires no new exported cause object or incompatible constructor rewrite.

I found no surviving negation, universal, extra-cause or numeric-context escape in the corrected
exact-message oracle. Exact messages are intentionally narrower than arbitrary truthful prose;
the card now states that limit honestly.

## 2. Corrected focused baseline and route accounting

In a private detached clone of the exact behavioral baseline, the corrected patch typechecked
with exit 0. Its typecheck log sha256 is
`8fa1cf5506304e8abac55868e7f1a136c9b1dde57a3981a382da4c21ea129a6f`.

The focused run reproduced **22 tests, 9 pass / 13 fail**:

- passing: stable; pure B1; pure B2a; pure B2b; ordinary RPC/read failure; and all four oracle
  controls;
- failing: pure B3, all six ordered pairs and all six triple first-occurrence permutations.

Every exhaustion case asserts a hard-coded expected latest/read total. The helper independently
derives totals from the attempt sequence, compares that arithmetic to the declaration, then
compares actual recorded calls to it before checking `pendingOnly` or the message. The static and
runtime totals agree: B1 contributes one latest lookup and zero reads; B2a/B2b/B3 each contribute
two latest lookups and 11 pinned reads.

Both pair directions and all six triple first-occurrence orders are present. Every applicable
mixed route containing B2 drives both B2a and B2b. Every frozen mixed route repeats at least one
cause after a category change. Pure B2a and B2b independently keep height movement and
same-height replacement distinct at the route level.

Stable success returns the exact pin number/hash after 11 reads and two latest lookups. Ordinary
read failure remains non-`ChainUnstableError`, retains its scripted message and has one initial
latest lookup with no unstable-snapshot retry. These controls are discriminating inside the
declared two-symbol classification boundary.

## 3. All eight published mutants reproduce exactly

Each corrected mutant was applied from a restored exact `vault.ts`, typechecked with exit 0 and
then run behaviorally. The measured totals and named failures match `mutation-matrix.tsv`:

| Mutant | Pass / fail | Independently inspected catch |
|---|---:|---|
| B1 as movement | 8 / 14 | pure B1 incrementally fails `pendingOnly` |
| B2 as pending | 7 / 15 | pure B2a and B2b incrementally fail `pendingOnly` |
| B3 as movement | 9 / 13 | pure B3 advances to the exact B3-message mismatch |
| pure B1/B2 messages swapped | 6 / 16 | all three current pure-message controls fail |
| generic message collapse | 6 / 16 | all 16 exhaustion messages fail |
| negated pure-B1 message | 8 / 14 | pure B1 rejects the semantically false exact sentence |
| rank-order accumulator | **14 / 8** | exactly three reversed pairs and five non-ascending triples fail |
| reset-on-repeat accumulator | **10 / 12** | exactly all 12 frozen mixed routes fail; pure/oracle controls pass |

The rank and reset mutants use otherwise-correct exact cause-set messages and property handling,
so they causally establish the improvements they name. No compile/typecheck failure or generic
harness noise is credited.

## 4. Blocking residual — every complete cause set precedes the first repeat

The expanded matrix varies first-occurrence **order**, but not the relationship between first
occurrence and repetition:

- every pair introduces both causes in attempts 1–2 and only then repeats one;
- every triple introduces all three causes in attempts 1–3 and only then repeats one; and
- therefore no frozen mixed case introduces a new cause after an earlier cause has repeated.

That leaves an order/repetition sibling alive. In scratch I constructed an otherwise-correct
accumulator with the corrected exact seven-message table and correct `pendingOnly` handling. Its
only defect is:

```text
record first occurrences until a cause repeats;
after the first repeat, freeze the cause set and ignore later newly observed causes.
```

This is typecheck-clean. Its mutated `vault.ts` sha256 is
`007d9799c9b9e271b22dd2552e82ec22d1e4e3cc295fcabd92687dc282d3236f`. Against the unchanged
corrected patch it returns **22 pass / 0 fail**, raw output sha256
`f499dbf6453859c0d4cfa5f016243582c29667e21097c87f46392d327eb42d0d`.

I then added four review-only routes without changing that mutant:

| Probe | Five attempt endings | Declared latest / reads |
|---|---|---:|
| B1→B2, B2 late | B1 B1 B1 B2a B2b | 7 / 22 |
| B2→B1, B1 late | B2a B2b B2a B1 B1 | 8 / 33 |
| B1→B2→B3, B3 at attempt 4 | B1 B1 B2a B3 B2b | 8 / 33 |
| B1→B2→B3, B3 at attempt 5 | B1 B2a B2b B1 B3 | 8 / 33 |

The original 22 remain green and exactly these four probes fail: **22 pass / 4 fail**, raw output
sha256 `a29f6f338de7c1fe5fea18a9305e9b4d929abcb6b0df48aeefca382af46d1088`.
Each failure is the expected exact cause-set message mismatch after the frozen accumulator omits
the late cause; route declarations and actual call totals pass first.

This is inside, not outside, the claimed boundary. Each probe uses the same B1/B2/B3 branches,
five-attempt budget, nonempty cause sets and first-occurrence order classes the card claims. The
production loop permits every sequence. `COVERAGE.md` truthfully says its concrete sequences are
not an exhaustive proof against arbitrary malicious algorithms, but the survivor is the direct
uncovered interaction between the correction's two named dimensions: order and repetition. It
violates the fixed success rule that the error aggregate all causes observed across all five
attempts.

The published reset mutant does not catch this sibling. It clears a complete mixed set when a
repeat occurs, so the current “complete set before repeat” fixtures kill it. The survivor freezes
that already-complete set and is therefore invisible until a new cause arrives after the repeat.

## 5. Fresh fast-gate causal pair

I ran both cases serially in the same isolated exact-baseline clone, restoring production bytes
and removing only the corrected test file for the control:

| Case | Foundry | TypeScript | Later consumers | Top level |
|---|---:|---:|---|---|
| unchanged baseline | 103/103 | 527/527 | ablation byte-identical; verifier 221, samples 7, tamper 78/30 | exit 0; `GATE PASSED` |
| exact corrected patch only | 103/103 | 536/549; exactly 13 named C failures | same later consumers green; four oracle controls pass | exit 5; `GATE FAILED`, supervisor refusal |

The independent raw hashes are
`9b74b947a50d87d298bc03dc1a4b3bbc8422faed882dee515a9305e72b75b0f8` for the control and
`2d620463fc0261377a5e1d987534a588142db73b113bbbaf7ff46c697c3d8d44` for the corrected
patch-only falsification. I inspected the body stages, not only supervisor status. The pair
confirms automatic test discovery and top-level fast-profile refusal. It does not cure the
surviving mutant and is not deep-profile or post-implementation evidence.

## 6. Scope boundaries and guards

The Batch D exclusion remains precise. `protocol.ts`, refusal types, `attest.ts`, maintained
claims and signed refusal surfaces are unchanged and outside Batch C. The reader error message is
not claimed to reach a signed refusal. No new reason code, tier, detail field, timeout, backoff,
recency policy or telemetry is introduced.

Before adding this review file, repository guards reported:

- secrets clean;
- review scope `R1=386, R2=46, R3=152`, all **584/584** tracked files assigned;
- all 23 finding IDs and ruled disposition totals matching;
- all six suite-floor facts single-sourced from the gate; and
- vendor-honesty mechanical checks passing, while explicitly leaving D-008(1)/(3) in John's
  authority.

Workspace guards report 13 machine-state findings, all baselined and zero new. That is a
ratcheted PASS, not a claim that the accepted debt is absent. Sentinel is non-Godot, so this guard
route has no visual/aspect/contrast stage.

The review does not claim provider honesty, real-provider reachability of hashless `latest`,
historical-state correctness, finality policy, completeness beyond the declared two symbols, a
new suite floor, a deep-gate result or any post-implementation result.

## 7. Bounded correction required

F1's exact-message correction and the existing pair/triple order cases may be preserved. The
remaining instrument correction is narrow:

1. Add cause-arrival-after-repeat coverage. The strongest bounded option is to enumerate the
   finite `3^5 = 243` B1/B2/B3 category sequences for the fixed five-attempt budget in one
   parameterized matrix, while retaining separate B2a/B2b mechanism controls and alternating
   B2a/B2b where a category sequence contains multiple B2 outcomes. A smaller acceptable matrix
   must at least cover late first occurrences after earlier repeats for both directions of every
   pair and every triple order, including first arrival at attempts four and five.
2. Add the typecheck-clean freeze-after-first-repeat mutant above. It must be caught by the new
   late-arrival cases while the existing 22 controls remain green.
3. Update patch/source hashes, focused totals, mutation matrix, checksums and gate summaries, then
   obtain a fresh independent correction review. Do not modify Review 1 or this review.

**FAIL.** The correction materially improves the instrument and closes Review 1's exact findings,
but its first-occurrence-order completeness claim still overreaches the concrete sequence matrix.
No implementation attempt is authorized or consumed by this review.
