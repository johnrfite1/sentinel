# C-SNAPSHOT — FIRST FRESH INDEPENDENT INSTRUMENT REVIEW

# VERDICT: FAIL

The frozen instrument is not ready to be held fixed. Its route oracle is real and its published
baseline/mutation/gate measurements reproduce, but its message oracle does not establish the
semantic property the card claims. It accepts messages that explicitly deny an observed cause,
accepts false mixed-run universals outside a two-phrase blacklist, and does not bind the digit `5`
to an attempt count. Separately, every mixed fixture introduces cause categories in the same
canonical B1-before-B2-before-B3 order, so an order-dependent cause accumulator survives the
entire frozen matrix while misclassifying supported reversed orders.

This is a **FAIL of instrument readiness only**. It is not an implementation verdict, product
approval, gate signature, certification, ratification, publication, rename, D-055 assessment or
push authorization. No production source, existing test, frozen instrument, script or signed
material was edited by this review.

---

## 0. Review identity and independence

| Item | Identity |
|---|---|
| exact instrument subject | `30d1466cde0e47899740818e574a75e575d75b9d` |
| subject tree | `09c29b98b17468ba937c8c6a87094a1ea1215b71` |
| subject message | `C-SNAPSHOT: freeze independent state classification test contract` |
| frozen behavioral baseline / subject parent | `1655b120a653b60ccb5b3a22583c0001d59ea7a4` |
| baseline tree | `b2c8fb1e53d35ea40655dc83faa61f8a76dd4f78` |
| frozen test patch | sha256 `51fba356e71fe648e78e85d551b6092b649d843645dde4338f64ca6b932450df` |
| extracted test source | 329 lines; sha256 `92267b368fb24c1f466e63d7d8344d6884d00c5e96957d612047c642228652c5` |
| mutation driver | sha256 `bee4a18f56e99fca812cbeddbb3515272845b63eb73f77c99235a730ec126997` |
| frozen matrix | sha256 `9f78e5708356cd874849a175989285a3b0239755cb33104894f396abe5fd88f7` |
| state at review start | clean; HEAD was the exact instrument subject |

I authored neither this instrument nor any future Batch C implementation. I read the workspace
instructions; D-058, D-059, D-060 and D-066; proposal §3.3(2); the original R2-F6 report and R4
adjudication; the V3 brief, report, probes, coverage and targeted adjudication; C5/ADJ4; all 14
files in this instrument directory; the complete declared production symbols and ABI in
`ts/src/signer/vault.ts`; the relevant current tests and call sites; and the complete top-level
fast gate. I inspected the exact parent-to-subject diff rather than relying on the card summary.

## 1. Frozen identity, provenance and boundary

The exact parent-to-subject diff adds 14 files and 1,037 lines, all beneath
`C-SNAPSHOT-tests/`. It changes no production source, existing test, script, gate, proposal,
decision, prior evidence or signed record. The protected diff across `ts/src`, `ts/test`,
`scripts/`, the proposal and `docs/decisions.md` is empty.

All 13 payload entries in `CHECKSUMS.sha256` verify from the repository root. The checksum file
is the fourteenth file and is intentionally not self-hashed. The independently checked frozen
identities agree with `PROVENANCE.md`:

- `vault.ts` sha256 `dbff956fc2fdf6698e6c94ce4261626dc40cf219b6095ff8afcda8afcadc1185`
  and `protocol.ts` sha256
  `87fc5204c561d986c04cc61eb4ae9e880db113187707f7e92e2df7a334b29b33`;
- pre-existing TypeScript-test tree `e29397245dadfe8c9250905d99c26c036013aacf`;
- `scripts/test.sh` blob `0c6c38ed746925d52720468865ca61eb31ae7ddd`, file sha256
  `66c272b90a16b037e3fcfc6f0d9184c48f63ac32e62538be7b6cd96a93801b79`;
- signed Gate S2 blob `baab3e7809a46f22131ef2b609f30af1ed8eeada`, file sha256
  `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589`; and
- every governing and R2/V3/adjudication source hash listed in `PROVENANCE.md`.

`TESTS.patch` applies cleanly to the exact baseline and adds only
`ts/test/vault.snapshot.classification.test.ts`. The extracted source has the published hash and
line count. Nothing from the patch is applied in this shared subject.

The declared production boundary is coherent: exported `ChainUnstableError` and
`createChainReader(...).readVaultState` in `vault.ts`. `protocol.ts`, `attest.ts`, refusal wire
types and current claims are explicitly excluded and assigned to Batch D/C5. That exclusion is
truthful: `attest.ts` reduces the error to `SIGNER_CHAIN_UNSTABLE` and discards its message and
`pendingOnly`, so this card does not pretend the diagnostic reaches a signed refusal. The
FATAL tier, public reason vocabulary and proposal §3.3(2) human-control/event requirement remain
untouched.

## 2. Independently derived routes and successful replay

Static source derivation agrees with the card. `SNAPSHOT_ATTEMPTS` is 5. A hashed attempt issues
ten pinned `eth_call`s plus one pinned `eth_getCode`; B1 issues none. Each successful or
post-read-failed hashed attempt has two latest-head lookups; B1 has one.

| State | Actual route | Reads |
|---|---|---:|
| B1 | initial `head.hash === null` | 0 |
| B2a | confirmation height differs | 11 |
| B2b | same height, confirmation hash differs | 11 |
| B3 | hashed pin and reads, then `confirm.hash === null` | 11 |
| B5 | confirmation number/hash match | 11 and a returned snapshot |

The frozen helper asserts the exact route-derived read and latest-lookup counts before it checks
classification. The stable control asserts the returned pin number/hash, exactly 11 reads and
two latest lookups. The ordinary-RPC control requires a non-`ChainUnstableError`, preserves the
scripted failure text, and confirms there is one initial lookup and no retry/confirmation. Those
controls are causally discriminating within the stated classification boundary.

In a private detached clone of the exact baseline:

- patch replay and test-source hashing passed;
- TypeScript typecheck exited 0, with raw sha256
  `8fa1cf5506304e8abac55868e7f1a136c9b1dde57a3981a382da4c21ea129a6f`;
- the focused run produced exactly **10 tests, 5 pass / 5 fail**; and
- request-count assertions completed before each of the five classification failures.

The pass/fail names match the preserved result: stable, pure B1, pure B2a, pure B2b and ordinary
failure pass; pure B3 plus B1+B3, B1+B2, B2+B3 and B1+B2+B3 fail. The first two fail at
`pendingOnly`; the other three fail at the first omitted cause recognizer.

The current API shape is also accurately inventoried. The exported constructor remains
`ChainUnstableError(attempts, pendingOnly = false)`, `pendingOnly` remains readable, the reader
uses the two-argument form and the existing fake uses the one-argument form. Full typecheck covers
both current in-repository call shapes. The frozen test observes the class, property and message
without requiring a new exported cause object or a particular constructor rewrite.

## 3. The five published mutants reproduce

I reran all five mutations independently from a restored exact `vault.ts`. Every mutation
typechecked with exit 0 and then failed behaviorally:

| Mutant | Focused result | Intended discrimination inspected |
|---|---:|---|
| B1 classified as movement | 4 pass / 6 fail | pure B1 fails `pendingOnly` |
| B2 classified as pending | 3 pass / 7 fail | pure height movement and pure reorg fail `pendingOnly` |
| B3 classified as movement | 5 pass / 5 fail | pure B3 moves past the baseline flag failure and fails movement exclusion |
| pure B1/B2 messages swapped | 2 pass / 8 fail | pure B1 and both pure B2 controls fail message classification |
| both pure messages collapsed | 2 pass / 8 fail | all eight exhaustion message checks fail |

The B3 total staying 5/5 is not a dead mutant: its pure-B3 assertion changes from the baseline
`pendingOnly` mismatch to the intended movement-classification mismatch. No compile failure,
typecheck failure or generic harness error is credited. B2a and B2b are independently driven in
their pure cases and both appear in every applicable frozen mixed family.

These measurements validate the card's recorded mutant table. They do not cure the independent
oracle defects below because none of the five mutants attacks negation, unlisted universal
wording, numeric-context substitution or first-occurrence order.

## 4. Blocking finding F1 — lexical presence is not semantic truth

The card requires the message to “semantically name all and only” observed causes and says its
oracle accepts equivalent **truthful** wording. The frozen helper instead lowers the message and
uses three unanchored positive regexes:

```text
pending (block with no hash | head ... before ... read)
head moved | head ... replaced | same-height reorg
pending confirmation | confirmation ... pending
```

It compares only those lexical booleans to the expected cause set. There is no negation handling,
no independently fixed grammar and no structured cause value. For mixed runs it rejects only the
two literal fragments `every observation` and `under each pinned read`.

I appended review-only tests in the private clone, leaving the frozen instrument unchanged. All
three probes typechecked and passed the helper itself:

1. a positive control demonstrated that at least one alternate truthful phrase for each cause is
   accepted (`pending head ... before ... read`, `same-height reorg`, and
   `confirmation ... pending`);
2. the helper accepted `No pending block with no hash was observed`, `The head moved did not
   occur`, and `No pending confirmation occurred` for the corresponding expected pure causes;
   each sentence denies the fact the oracle records as present; and
3. for a mixed B1+B2 cause set it accepted `All five attempts had a pending head before the read
   and the head moved after the read`. B1 and B2 are mutually exclusive attempt endings, so this
   universal is false, but it contains neither blacklisted phrase.

The review-probe suite reported all three probe tests passing; its raw output sha256 is
`4e62ee5b75e7f7e32f278f99e5be5bdb442011e3e3cb92d22ac061a86f071aa1`. Thus a future
implementation can
classify the routes correctly enough to set `pendingOnly`, emit a materially false explanation,
and satisfy the frozen semantic oracle. Route counts do not help: they prove the fixture reached
the causes, not that prose containing their keywords asserts them truthfully.

The attempt-budget check has the same false-positive shape. `new RegExp(String(5))` accepts the
digit anywhere, including `50`; it does not require “5 attempts” or otherwise bind the value to
the exhausted retry budget.

This is blocking, not a preference for exact prose. R2-F6 is a record-fidelity obligation, and
the fixed contract explicitly makes truthful cause aggregation its observable success
condition. An oracle that accepts the opposite assertion does not observe that condition.

## 5. Blocking finding F2 — one canonical first-occurrence order

The four frozen mixed fixtures do contain repeated causes and exercise each cause family, but
their **first appearances** are always in ascending canonical order:

```text
B1+B3       B1, B3, B1, B3, B3
B1+B2       B1, B2a, B1, B2b, B2a
B2+B3       B2a, B3, B2b, B3, B2a
B1+B2+B3    B1, B2a, B3, B2b, B1
```

I evaluated an intentionally defective accumulator that records a newly encountered cause only
when its rank is not lower than the highest rank previously seen (B1 < B2 < B3). It reports the
correct cause sets for all four frozen mixed fixtures. The later repeated lower-ranked causes do
not expose it because those causes were already recorded before the higher rank appeared.

The same accumulator omits B1 for B3→B1, omits B1 for B2→B1, and omits B2 for B3→B2. All are
ordinary orderings the five-attempt loop accepts; no production branch constrains causes to the
frozen canonical order. Therefore an order-sensitive “repair” can satisfy every frozen case yet
violate the card's unqualified rule that the error aggregates all and only causes actually
observed.

`COVERAGE.md` says completeness is limited to the enumerated scripted-node states, but `CARD.md`
and the fixed success condition make the cause-aggregation property general inside the two-symbol
state-machine boundary and call the branch classifier exhaustive. Restricting evidence to one
ordering per set cannot support that stronger claim. This is the exact generalise-the-argument,
not-one-demonstration problem D-058's explicit branch-matrix requirement is meant to prevent.

## 6. Fresh top-level fast-gate causal pair

I ran the unchanged control and the frozen patched baseline serially in the same isolated clone
of the exact behavioral baseline, restoring all production bytes between cases. Only the new test
file differed.

| Case | Foundry | TypeScript | Later consumers | Top level |
|---|---:|---:|---|---|
| unchanged control | 103/103 | 527/527 | ablation byte-identical; verifier 221, samples 7, tamper 78/30 | exit 0; `GATE PASSED` |
| exact `TESTS.patch` only | 103/103 | 532/537; exactly the five named C tests fail | same later consumers green | exit 5; `GATE FAILED`, supervisor refuses completion |

The independent raw gate hashes are
`f965c079002ba483741580431a47d11041c7f29b1d2f8f1b1aeb78d0637b7994` for the control and
`37dd3c0dcd82e851473855183e409c5107863515c20b1b45ee107549bb6813ab` for the patched
falsification. They differ from the preserved raw hashes because
paths and timings differ; the scored stage results are identical. I inspected the body output,
not only exit status. The top-level gate therefore is genuinely bound to the new automatically
discovered test file. This establishes fast-profile causal binding only; no deep or post-repair
pass is claimed or required for this review.

## 7. Guards, preserved scope and limits

Before this review file was added, repository guards reported:

- secrets clean;
- review scope `R1=385, R2=46, R3=152`, all **583/583** tracked files assigned;
- all 23 finding IDs and ruled disposition totals matching;
- all six suite-floor facts read from the one gate source; and
- vendor-honesty mechanical conditions passing, with D-008(1)/(3) explicitly remaining John's
  authority as printed.

Workspace guards reported 13 machine-state findings, all baselined and zero new. That is a
ratcheted PASS, not a claim that the accepted debt is absent. Sentinel is non-Godot, so there is
no visual/aspect/contrast stage in this guard route.

The review does not claim RPC-provider honesty, real-provider reachability of hashless `latest`,
historical-state correctness, finality policy, telemetry, retry backoff, recency, timeout, a new
public reason code, a signed detail, or completeness outside the two declared symbols. Stable
success controls classification continuity; it is not a fresh proof of every `VaultState` field.
Fast gate evidence is not deep-profile evidence.

## 8. Bounded correction required

One instrument correction is sufficient and consumes no implementation attempt:

1. Replace the free-form positive-regex oracle with a finite, independently reviewed message
   contract keyed by the exact cause set. The smallest robust option is one exact canonical full
   message per non-empty cause set (or a finite allowlist of exact complete sentences), while
   keeping the current class and `pendingOnly` API. Do not try to repair semantic truth with a
   larger blacklist.
2. Bind the attempt budget as an exact message component such as `5 attempts`, and add explicit
   rejection controls for negated cause phrases, unrelated digits such as `50`, extra causes and
   false universal wording.
3. Add mixed fixtures whose first-occurrence order covers both directions for every pair and all
   six orders of B1/B2/B3, retaining exact read/latest counts and including B2a/B2b across the
   matrix. Include repetitions after order changes so a reset/drop accumulator is observed.
4. Add a typecheck-clean negated-message mutant and an order-dependent accumulator mutant. Each
   must be killed by its intended named assertion, not by compile/typecheck or unrelated noise.
5. Re-run the focused baseline, every mutant, checksum/provenance checks and the unchanged/patched
   fast-gate causal pair; update the frozen counts and summaries exactly.

**FAIL.** The existing route and mutant evidence may be reused where its bytes remain unchanged,
but the message oracle and ordered mixed matrix must be corrected and freshly reviewed before the
Batch C implementation contract can be held fixed. Nothing in this verdict authorizes an
implementation or crosses the permanent authority boundaries in D-066(3).
