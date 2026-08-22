# C-SNAPSHOT — THIRD FRESH INDEPENDENT INSTRUMENT REVIEW

# VERDICT: HOLD

The twice-corrected instrument is ready to be held fixed. The second correction closes Review
2's late-first/repeat hole by executing every length-five B1/B2/B3 category sequence through the
real reader under both declared alternating B2 mechanism polarities. The finite generator has no
missing or duplicated category sequence; the aggregate cannot turn a failed subcase into a pass;
and the otherwise-correct freeze-after-first-repeat mutant is caught only by the new aggregate
after all retained 22 tests remain green.

This is a **HOLD for frozen instrument readiness only**. It is not an implementation verdict,
product approval, gate signature, certification, ratification, publication, rename, D-055
assessment or push authorization. No production source, existing test, frozen instrument, prior
review, script, claim or signed material was edited by this review.

---

## 0. Exact identity and independence

| Item | Identity |
|---|---|
| exact twice-corrected subject | `7fa82695666b82a56319cebab24c27012fed4225` |
| subject tree | `86d2ec76f64f0d622e3b3362303f91c679e1a1f3` |
| subject title | `C-SNAPSHOT: exhaust frozen sequence matrix` |
| subject parent / Review 2 FAIL | `71cfa70b8267d5e2950af99307abf372992c008b` |
| parent tree | `c11beba94c3cdaecca578ae0028b09ed8f27d18b` |
| behavioral baseline | `1655b120a653b60ccb5b3a22583c0001d59ea7a4` |
| behavioral-baseline tree | `b2c8fb1e53d35ea40655dc83faa61f8a76dd4f78` |
| twice-corrected test patch | sha256 `b6fc3c713e97c2fdfc328516eeb42fdb4f3cc25d0648602ea654e6cf1513c9f1` |
| extracted test | 603 lines; sha256 `29a673560e89b639b6635661706a368454c9969a04c5d37c4f6c15229df3dd8a` |
| mutation/control driver | 298 lines; sha256 `f404a5ffe7d00a8d4978cd235c3c2a57c62a6e332a8d7106699db5eddd45ef2f` |
| frozen mutation matrix | sha256 `9d1d19cd29af5684287fdbe53995113cd17c5e8a9a8cc4686385637187fbedc0` |
| state at review start | clean; HEAD was the exact subject |

I authored neither the instrument, either correction nor any future Batch C implementation. I
read the workspace instructions; D-058, D-059, D-060 and D-066; proposal section 3.3(2); the R2,
V3 and adjudication evidence identified by `PROVENANCE.md`; every file in this instrument
directory; both preserved independent FAIL reviews; the complete declared production symbols in
`ts/src/signer/vault.ts`; the relevant current tests and call sites; and the top-level fast gate.
I inspected the exact parent-to-subject diff rather than relying on the maintained summaries.

## 1. Correction scope, preservation and replay

The exact parent-to-subject correction modifies **14 existing files**, with 476 insertions and
279 deletions, all beneath `C-SNAPSHOT-tests/`. It adds, deletes or renames no file. The protected
diff is empty across production, existing tests, contracts, scripts, verifier, fixtures, hooks,
proposal, decisions and signed Gate S2 material.

The prior independent reviews are byte-preserved at both the parent and subject:

- Review 1 sha256
  `ffad26f2c8307aa7fcf9e2c7e18dd971eace47b955132f65222bbb1c335febf0`; and
- Review 2 sha256
  `25e336b97194ee58f6e20c367163726a3a4e9c8b2566e86bc76ab1fbdc3b201e`.

All 15 payload entries in `CHECKSUMS.sha256` verify. The checksum file is the sixteenth directory
file and intentionally does not self-hash. The frozen source, test-tree, gate and signed-material
identities in `PROVENANCE.md` independently agree with the behavioral baseline, including
`vault.ts` sha256 `dbff956fc2fdf6698e6c94ce4261626dc40cf219b6095ff8afcda8afcadc1185`,
the pre-existing TypeScript-test tree `e29397245dadfe8c9250905d99c26c036013aacf`, gate blob
`0c6c38ed746925d52720468865ca61eb31ae7ddd`, and signed Gate S2 blob
`baab3e7809a46f22131ef2b609f30af1ed8eeada`.

In a private detached clone of the exact behavioral baseline, `TESTS.patch` applies cleanly and
adds only `ts/test/vault.snapshot.classification.test.ts`. The extracted file has the published
603-line count and hash above. No part of that patch is applied in the shared subject.

## 2. Independent exhaustive derivation

I reimplemented the category enumeration independently of the frozen helper. Base-three indices
0 through 242 produce exactly **243 category sequences and 243 unique category strings**, from
`B1,B1,B1,B1,B1` through `B3,B3,B3,B3,B3`. Each of the five positions contains B1, B2 and B3
exactly 81 times. Running both declared B2 starting polarities produces **486 actual reader
executions**.

The independently derived distribution is:

| Property | Count |
|---|---:|
| one-cause executions | 6 |
| two-cause executions | 180 |
| three-cause executions | 300 |
| B1 attempts | 810 |
| B2a attempts | 405 |
| B2b attempts | 405 |
| B3 attempts | 810 |
| latest-head lookups | 4,050 |
| pinned state/code reads | 17,820 |

Each pure cause set occurs twice, each pair cause set occurs 60 times, and the triple cause set
occurs 300 times. That independently explains the live baseline's exhaustive result: its current
pure-B1 and pure-B2 messages satisfy four routes, while the other **482** routes fail the exact
cause-set oracle.

There are 454 unique concrete mechanism sequences among the 486 executions. The 32 category
sequences containing no B2 necessarily produce identical concrete sequences under the two B2
polarity labels; every one of the 211 B2-containing category pairs differs. This is not an
omission or a false publication: the card consistently claims 486 **executed reader routes**, not
486 unique mechanism strings. Both labeled executions still start and stop a real scripted node
and invoke the real reader.

The B2 mapping is also internally sound. A single B2 is B2a under one polarity and B2b under the
other. Repeated B2 alternates the two mechanisms under both starting polarities. Pure B2a/B2b and
retained mixed named tests separately bind height movement and same-height reorg to the shared B2
classification. The card explicitly excludes every arbitrary B2a/B2b arrangement; it claims
finite completeness at the B1/B2/B3 cause-category level, not mechanism-string completeness.

Because all `3^5` category strings are executed, there is no remaining first-attempt, late-first,
ordering or repetition sibling inside the declared five-attempt B1/B2/B3 domain. Longer runs,
additional categories and arbitrary B2 mechanism arrangements remain outside it, as the card
states.

## 3. Real routes, aggregation and false-pass attack

The aggregate uses the real `createChainReader(...).readVaultState` path and records its JSON-RPC
calls; it does not fabricate `ChainUnstableError` objects. For every execution, the route oracle
re-derives expected latest/read totals from the concrete B1/B2a/B2b/B3 attempt list, compares them
to the separately computed category totals, then compares both with the actual recorded calls.
Only after that does the classification oracle require exhaustion, the exact error class,
`pendingOnly`, and the full cause-set message.

I attacked the aggregate's continuation and final accounting:

- `attempted` increments before execution; an execution failure is appended and continued, so
  `observed` and later counters remain short and the final incomplete-traversal check fails;
- a route assertion failure is appended, but classification is still attempted;
- a classification failure is appended, and the next subcase still runs;
- `classificationChecked` counts attempted classifications rather than successful ones, an
  accurate name; a failed assertion remains in `failures`; and
- the final assertion requires both all four counters at 486 and zero accumulated failures.

The live baseline supplies a strong continuation falsification: **482 classification subcases
fail**, yet its final diagnostic reports
`attempted=486/486 observed=486/486 route-verified=486/486 classification-checked=486/486`.
Thus it does not stop at the first red route. The exact accumulator control's green result also
proves all four counters reached 486: any incomplete counter would append a final failure. Constant
preflights refuse a drift away from 243 categories or 486 executions. A hung reader could stall
the test rather than false-pass it; timeout policy is explicitly outside this card.

## 4. Exact message and API contract

The retained oracle has exactly seven keys, one for every nonempty subset of B1/B2/B3. It requires
the contextual `5 attempts` component and byte equality with the complete canonical sentence.
The four live negative controls reject lexical negation, `50 attempts`, an extra unobserved cause
and a mixed false universal through the same helper used by real routes.

An equivalent but noncanonical truthful sentence does **not** satisfy this oracle. That is now an
intentional and accurately disclosed exact-message ABI, not Review 1's claim that an open-ended
lexical recognizer accepted arbitrary truthful wording. The exact accumulator control proves all
seven required sentences can be produced by an otherwise-compatible implementation.

The control preserves the exported class, readable `pendingOnly`, current one- and two-argument
constructor calls, and adds only an optional internal third argument in the mutant implementation.
The instrument itself does not prescribe that constructor technique, a counter, a set, flags or
a new exported cause object. It requires `pendingOnly === true` only for pure B1 and leaves current
call sites type-compatible.

## 5. Focused baseline and complete typecheck-clean calibration

The freshly extracted patch typechecks at exit 0. The focused baseline then reproduces **23
top-level tests, 9 pass / 14 fail**. The retained 22 remain 9/13: stable success, pure B1, pure
B2a, pure B2b, ordinary failure and four oracle controls pass; pure B3, all six ordered pairs and
all six triple permutations fail. The aggregate is the fourteenth failure, with all counters at
486 and 482 classification failures.

I restored the exact `vault.ts` before every driver case. All ten driver cases typechecked at exit
0 with no diagnostic; the common raw typecheck log sha256 is
`8fa1cf5506304e8abac55868e7f1a136c9b1dde57a3981a382da4c21ea129a6f`. Behavioral totals match
the frozen matrix exactly:

| Case | Pass / fail | Exhaustive failures | Fresh raw log sha256 |
|---|---:|---:|---|
| live baseline | 9 / 14 | 482 | `e6efabce986289142f59fcb13ad075ee0f314e618fdb2307b6b520b14f3949eb` |
| B1 as movement | 8 / 15 | 484 | `36de18291d1a171ed74fc2d1ffef755b505131c146e5dbc1ee6cf981e9db19cf` |
| B2 as pending | 7 / 16 | 484 | `8b90afda623300c594e8a458a014de0ac4050f77f8ff62cb3227b006ea551aef` |
| B3 as movement | 9 / 14 | 482 | `fdf656c3e2a1e2d5562ade279956979af9b0e4aa57a9bb6bffe1ea7923b5b8b6` |
| pure messages swapped | 6 / 17 | 486 | `e84f4a26c6ec7949f31cc63478b5c50a6cf6e2400e9ca4c22e9edf0f5a0e2c8f` |
| generic message collapse | 6 / 17 | 486 | `c4c2c6c474df18a7cce48991a48873b9ca16487e5c6b9283ccbd826fa9aa1c39` |
| negated pure B1 | 8 / 15 | 484 | `ad277be7a0b4096740c38b3730d27232847e3f962baf1bc71d59a69d79e71bfe` |
| exact accumulator CONTROL | **23 / 0** | **0** | `cce5e632e6c56cb169d581d5e1f7fb3e573be38cf56907bda30593a4ea4c7ba4` |
| rank-order accumulator | 14 / 9 | 340 | `f09229e4595aa1e95a858e5c1f67720b74c2db7fd7b701bdbec0f24449094768` |
| reset-on-repeat accumulator | 10 / 13 | 360 | `6beb6241e74e3ad5ddbf8fba4e60c1e105da67e5ac2c430069501fb7cceff6dc` |
| freeze-after-first-repeat | **22 / 1** | **276** | `c9aea71306b34159d3253d01acc1b1c7159855fd11b7cd0e7d8c22d528429923` |

Every red aggregate reports all four counters at 486. I inspected named outcomes, not only totals:
B1 and B2 mutants incrementally fail the correct pure controls; B3 reaches its intended exact-B3
message failure; swap, generic and negation mutants fail the named message assertions; rank retains
its eight prior named order failures; reset retains its twelve prior named repetition failures.
The freeze mutant leaves every original named test green and fails **only** the aggregate, so the
new catch is causal rather than compile noise or generic rejection. Independent combinatorics
also derive exactly 210 passing and 276 failing freeze routes.

Fresh raw hashes differ from the card's preserved raw hashes because timings and isolated paths
are nondeterministic. The scored names, totals, counters and intended assertions agree exactly.

## 6. Fresh top-level fast-gate causal pair

I ran the control and falsification serially in separate private clones of the exact behavioral
baseline and inspected stage output as well as supervisor status.

| Case | Foundry | TypeScript | Later scored consumers | Top level |
|---|---:|---:|---|---|
| unchanged exact baseline | 103/103 | 527/527 | ablation byte-identical; verifier 221, samples 7, tamper 78/30 | exit 0; `GATE PASSED` |
| same baseline + `TESTS.patch` only | 103/103 | 536/550; exactly 14 C-SNAPSHOT failures | same later consumers green | exit 5; `GATE FAILED`; supervisor refuses completion |

The patch-only aggregate again reports all four counters at 486 and 482 classification failures.
The fourteen failures are precisely the retained thirteen named R2-F6 failures plus the new
aggregate. The fresh raw gate-log hashes are
`176bbe0b2ae7f614c22703dd04fd9d3f83edb1775a9a92ec12ebe0e025c09da6` for the control and
`007e6ad63a0f7bc396c7a1d4de1c5966288ee5ffb69d640e8af5a1f4671813a1` for patch-only
falsification. This establishes automatic discovery and top-level causal binding for the fast
profile. No deep-profile or post-implementation pass is claimed or required for this review.

## 7. Boundaries, guards and limits

The Batch D exclusion remains exact. `protocol.ts`, `attest.ts`, refusal wire types, maintained
claims and signed surfaces are unchanged. This instrument establishes reader-error route and
message accuracy only; it does not claim that a signed refusal carries the diagnostic. It adds no
reason code, tier, detail field, timeout, backoff, recency policy, telemetry or provider policy.

After staging only this review file, final repository checks reported:

- diff/checksum and protected-boundary checks clean;
- secrets clean in working-tree and staged modes;
- review scope R1=388, R2=46, R3=152, all **586/586** tracked files assigned and all 203 changed
  remediation files assigned;
- all 23 finding IDs and ruled disposition totals matching;
- all six suite-floor values read from the single gate source; and
- vendor-honesty mechanical conditions passing, with its output expressly leaving D-008(1)/(3)
  to John.

Workspace guards pass with 13 machine-state findings baselined and zero new. This is ratcheted
evidence, not a claim that accepted debt is absent. Sentinel is non-Godot, so this guard route has
no visual/aspect/contrast stage.

The review does not claim real-provider reachability of hashless `latest`, provider honesty,
historical-state correctness, finality or reorg policy, transport retry behavior, completeness
beyond the two declared symbols and finite category domain, a reconciled suite floor, deep-gate
coverage or a post-implementation result.

## 8. Verdict

**HOLD.** Review 1's exact-message defect and Review 2's late-first/repeat sibling are closed in
the frozen instrument. Exact identity, finite enumeration, real-route accounting, aggregation,
all eleven warning-clean calibration cases, fast-gate causal binding and protected boundaries
hold at subject `7fa82695666b82a56319cebab24c27012fed4225`.

This HOLD fixes only the C-SNAPSHOT test-contract readiness determination. The review performs no
implementation and exercises none of the permanent authorities reserved by D-066(3).
