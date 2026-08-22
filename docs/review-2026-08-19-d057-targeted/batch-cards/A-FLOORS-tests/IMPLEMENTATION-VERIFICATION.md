# A-FLOORS — independent final implementation verification

# VERDICT: HOLD

The exact implementation candidate
`dc47cdf87ce864bb39afd70d842888fa7eee7953` holds the seventh-corrected frozen
A-FLOORS contract. The candidate has one implementation attempt. No correction attempt was
needed. This is a HOLD for this exact candidate and declared three-surface inventory only; it is
not a gate signature, approval, certification, ratification, publication, rename, D-055
assessment, D-008 action or push authorization.

I authored neither the A-FLOORS instrument and reviews nor this implementation. I changed no
production source, test, instrument, prior review, gate, floor, maintained claim, decision or
signed material during verification. This standalone record is the only tracked review change.

I tried to fail the candidate on scope, floor direction, instrument bytes, frozen B/C bytes,
prior-review preservation, focused counters, CONTROL failures, gate counters, G1/G3 later-stage
masking, and the G5/G6 deletion strings. None of those attacks held.

## 1. Frozen identity, scope and patch fidelity

| Item | Independently verified identity |
|---|---|
| implementation candidate | `dc47cdf87ce864bb39afd70d842888fa7eee7953` |
| candidate parent / Review-8 HOLD | `e1d69ff1352ccfef3aa558bbfe729051b834b0d9` |
| candidate tree | `c8b138ee75350ef2682b5b5e36360d24f0ab4dec` |
| held instrument review | Review 8; review-file sha256 `c34fce8ec3a85da2056e1ade767172af98fab19ccdfd75e20bf3128713d6ea1f` |
| focused harness `a-floors.py` | 1140 lines; sha256 `47cb61ccef462f75131259c7af2b22c12911c86347c898653d50062bf8b717b4` |
| serial gate harness `a-floors-gate.py` | sha256 `fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0` |
| frozen `gate-matrix.tsv` | sha256 `0b4d9c127e7230c7266960fe073f92f9551da9a68005cb936850993d803d1c58` |

The exact parent-to-candidate diff is only:

- modified `scripts/test.sh` (floors `92 → 103` and `527 → 550`; one
  `./scripts/check-suite-floors.sh || fail=1` on the common fast/deep path before suite
  consumers; live COVERAGE D-010 figures removed, dated history preserved);
- modified `scripts/check-suite-floors.sh` (named-subject `{NAME}: <class phrase>` refusals;
  unique named-subject records rather than JSON-wrapper dumps; three enumerated publication
  paragraphs); and
- modified `docs/session-state.md` (live §3 / D-010 floor copies removed; dated history
  preserved).

No instrument, prior review, B/C test, signed pack, or other production file moves. `git diff
--check` on the candidate is clean. Live worktree dirt (`README.md`) and untracked `assets/` /
`.serena/` were present and were not touched, staged or committed. Every focused and gate
invocation used a disposable clean clone of `dc47cdf` as the harness source; that clone's
`git status --porcelain --untracked-files=no` was empty.

Candidate production hashes:

| File | blob | sha256 |
|---|---|---|
| `scripts/test.sh` | `a2551232c41f2196430d48ad445e830f77b6b342` | `ec3cfffdcb686d5ac4bd6d00793c107011bbb4b12d201710f34761f0cc4341a4` |
| `scripts/check-suite-floors.sh` | `f8df5ab4db9023b319d872249e10140b635dc152` | `95b65a02bdfc8436e4739b7e5ef90b803964236a86173ed5b8f3c6cc139f7a46` |
| `docs/session-state.md` | `b1ed90bd1d0cb0ebcec258a0c217dc35ae0dc044` | `5582e7bba69eb8455aa7de869444d17f3d6a645ca72620b7aea097125192c711` |

Parent hashes remain the Review-8 freeze: `scripts/test.sh`
`66c272b90a16b037e3fcfc6f0d9184c48f63ac32e62538be7b6cd96a93801b79`,
`scripts/check-suite-floors.sh`
`c9a334dca2ce06e78a126e15dd33ef19bd0df3b43569eb0de76ea0b1c3ac13b6`,
`docs/session-state.md` blob `b91f548389a52b75b9796d3aaa975fc6e542dedc`.

Floors were raised, not lowered. The verifier quartet is unchanged at 221/7/78/30. Parent
`scripts/test.sh` had no `check-suite-floors.sh` invocation; the candidate has exactly one.

## 2. Independent implementation reading

`scripts/test.sh` assigns `FOUNDRY_MIN_TESTS=103` and `TS_MIN_TESTS=550` once each, keeps the
existing single assignments of the four verifier floors, and invokes the reader once on the
common path (`fail=1` accumulation) before Foundry, TypeScript, verifier and deep corpus
consumers. When the reader refuses, later stages still run; `GATE PASSED` and the completion
token are withheld; the supervisor exits 5 with `GATE DID NOT REACH COMPLETION`. The deep-profile
identification line is on the success path only, after that refusal branch.

The reader prints one `{NAME}: <class phrase>` record per failed constant (`missing definition`,
`empty assignment`, `malformed assignment`, `numeric positive decimal required`, `duplicate
executable assignment`). It does not emit `{` / `}` wrapper records. Unique-subject rejection of
JSON-wrapped dumps is scored by the frozen harness oracle against that output; a production dump
that named every constant as the same class inside wrapper records would fail those REQUIRED
rows. The three enumerated publication checks fire on the wrapped live §3 paragraph, the wrapped
current D-010 session paragraph, and the wrapped current gate coverage paragraph, each naming
`session-state` or `coverage` plus current/maintained class and a derivation/numeric-copy reason.

`docs/session-state.md` no longer repeats live floor/count copies in the §3 stable paragraph or
the D-010 bullet. Dated history, including the 2026-08-17 correction note, is retained.

## 3. Independent focused reproduction

Commands were run against a disposable clean clone of the exact candidate. I did not copy author
`/tmp` logs or claimed matrix bytes. The focused harness was the frozen Review-8 instrument
(hash above). Variant was the default `baseline`.

Exit 0. REQUIRED **131/131**. CONTROL **218/218**. Completion token
`A_FLOORS_FOCUSED_COMPLETE`. Zero FAIL rows in the produced matrix (349 data rows plus header:
131 REQUIRED, 218 CONTROL).

Measured matrix sha256
`69825cc0e41a11cc359c66968f5920160f215d2a0c2f2b62e6c06a4dd99aeed0`
— byte-identical to the frozen exact-positive v7 matrix. Measured focused raw-log sha256
`a89ea7c1a1af463d1b62f995ba78ea6e73e74ebd1efe2e367df7da3a2e8b74e9`.

Named output was inspected, not inferred from totals: live canonical values are 103/550/221/7/78/30;
B-EVENTS and C-SNAPSHOT preservation controls pass; `W-common` observes exactly one real-gate
invocation; the four publication REQUIRED rows pass; `T-route-complete` reports 54/54.

Frozen B/C bytes at the candidate, independently hashed:

- B-EVENTS `contracts/test/SentinelVault.events.t.sol`
  `2a9219cc5138858b012b0bc56069490db3dd7d1963b73ccc19c28a48ce2b029e`
- C-SNAPSHOT `ts/test/vault.snapshot.classification.test.ts`
  `29a673560e89b639b6635661706a368454c9969a04c5d37c4f6c15229df3dd8a`

## 4. Independent seven-case serial gate

No competing live Sentinel gate was present at launch. Cases ran serially with the frozen
harness (hash unchanged vs Review 8). Timeout 1800s/case. Exit 0. REQUIRED **4/4**. CONTROL
**3/3**. Completion token `A_FLOORS_GATE_COMPLETE`.

Elapsed times are from the produced matrix, not from author evidence:

| Case | Kind | Status | Elapsed | Raw log sha256 |
|---|---|---|---:|---|
| G0-fast-unchanged | CONTROL | PASS | 316.226s | `bb61b73ad943781a705d47a383e28897e7484077e73250611e6a8a0da8e37ef3` |
| G1-fast-reader | REQUIRED | PASS | 275.296s | `e48849a85bca66390256e928484200747c3d900073f9b6e6356e6e5f8b473109` |
| G2-deep-unchanged | CONTROL | PASS | 1062.704s | `b99ae41101c4f3b9df850afc3497198c31190295a297ba4a1b8a140495dcca90` |
| G3-deep-reader | REQUIRED | PASS | 915.491s | `75fc723cce136e50ddb36b0c198e71be58d57a6b07fddf440130d141650d5743` |
| G4-raised-control | CONTROL | PASS | 243.044s | `9da0f5c3849ca6653ef275f312a4bf9678e697a531501e785defcc7e0569e7dc` |
| G5-delete-events | REQUIRED | PASS | 284.483s | `999a52f3d8348e648b529d99cfc88aaa964dfdc8c42144cdbc38021ee5736193` |
| G6-delete-snapshot | REQUIRED | PASS | 295.176s | `ffb232046638d8bba6876c3d9105fd0a8da3f1cac89768e3518ce6bf7fc5a68e` |

Produced gate-result matrix sha256
`51d4bb609efa3f2bb7319d7cf2ab8718b2ba3943f78d5016744a3856a80e441a`.
Harness-wrapper log sha256
`4e3713836f98ca1ca1db639ebc5f8e71bcdeb3f6e1a8c5dc1255e2e8ad4d75f5`.

Raw-log inspection, not inference:

- G0: `foundry: 103 tests (floor 103)`; `typescript: 550 tests (floor 550)`; suite 221/7/78/30;
  `GATE PASSED`; fast-profile footer. No `GATE DID NOT REACH COMPLETION`.
- G1: `session-state current publication is a numeric copy and must derive`; later Foundry,
  TypeScript and verifier stages still print the successful measured counts; `GATE FAILED`;
  `GATE DID NOT REACH COMPLETION`; **no** `GATE PASSED`. A later green stage does not mask the
  reader refusal.
- G2: same successful counts as G0; `corpus: 50 fixtures executed; committed views verified FILE BY FILE`;
  `GATE PASSED`; `This IS the deep profile (--gate)`.
- G3: the same named session-state refusal as G1; later Foundry/TypeScript/verifier success;
  corpus 50/file-by-file; `GATE FAILED`; `GATE DID NOT REACH COMPLETION`; **no** `GATE PASSED`;
  **no** `This IS the deep profile (--gate)`. Later green stages, including the deep corpus,
  do not restore completion.
- G4: `foundry: 103 tests (floor 103)` and `typescript: 550 tests (floor 550)`; `GATE PASSED`.
- G5: exact string `FLOOR BREACHED — foundry tests: 92, floor 103.`; later
  `typescript: 550 tests (floor 550)` and suite 221/7/78/30; fail-closed.
- G6: `foundry: 103 tests (floor 103)`; exact string
  `FLOOR BREACHED — typescript tests: 527, floor 550.`; suite 221/7/78/30; fail-closed.

## 5. Protected boundaries and guards

Reviews 1–8 and the concurrent Review-5 blob are byte-preserved at the Review-8 values:

- Review 1: `d07c6358127caba142b0c95adcba6fc33cb5b8eafdbba5c8680382a32d39c82d`
- Review 2: `978d09f669cb6c5037d0de0e903f678ea7015f394670692698305b2f821ae7ae`
- Review 3: `27e8e8da48fe34a07c750023296c11b82d937279f65b058fe4c5d2e78523bf86`
- Review 4: `cfdf80b4c49a5716565fae5254652174c360226e005720402aaba8fb37d28437`
- Review 5 of record: `4d742aded60fce42d30ec49dbb4d7a443fe0f0dbfc04ab9cafcc06987c4bd6fa`
- concurrent Review 5: `10bc8231f5d9e3f309a3bf87190d1340f60176c8fdc1644bb1bf8bd2e585dbb7`
- Review 6: `a807603684afc76f93929d662be111e1438d7578a7be3dbcdb4d9d7ef40ac3f4`
- Review 7: `7d4fea4c150e7c136ecb364b32dca97e76a69b94b8267b44e470bd28956dfa77`
- Review 8: `c34fce8ec3a85da2056e1ade767172af98fab19ccdfd75e20bf3128713d6ea1f`

`a-floors.py`, `a-floors-gate.py`, `gate-matrix.tsv`, `CARD.md`, `RUNBOOK.md` and
`GATE-BINDING.md` are byte-identical to the Review-8 parent. I did not rewrite any of them.

Repository checks from Sentinel root, output-read:

- secret guards: worktree and staged both `clean` (worktree emitted two `sed: RE error:
  illegal byte sequence` lines from untracked binary assets and still reported clean);
- review scope: R1 516 / R2 47 / R3 152 and **715/715** before staging this record;
  R1 517 / R2 47 / R3 152 and **716/716** after staging;
- findings ledger: pass; 23 IDs and all D-057(1) totals unchanged;
- suite-floor reader: exit 0 at **103/550/221/7/78/30**;
- vendor-honesty mechanical guard: pass without exercising agent authority over public claims;
- workspace guard: pass with **13 machine-state findings baselined and 0 new**;
- `git diff --check` on the candidate: clean.

Workspace success remains ratcheted; it does not erase the 13 pre-existing findings.

## 6. Limits carried with this HOLD

- Coverage is finite to the 131 REQUIRED / 218 CONTROL focused rows and the seven serial
  fast/deep gate cases. It is not general Bash parsing, general prose-consistency evidence, or
  repository-wide count completeness.
- Unique-subject rejection of JSON-wrapped dumps is the frozen harness oracle. The production
  reader satisfies it by emitting unique named-subject records. Brace-less six-line dumps remain
  the stated Review-3 herestring exclusion from CARD §2 and §8; fullwidth / zero-width /
  comment-before-brace wrappers remain the Review-8 classified-outside-CARD spellings. This HOLD
  does not reopen those instrument boundaries.
- Dated history in `docs/session-state.md` still contains present-tense wording about a stale
  trio in the gate coverage block. That text is inside the preserved correction note, not a live
  floor copy. Focused `P-history` is a CONTROL and passed.
- This HOLD does not assess D-055, D-008 public-claim certification, Batch D maintained claims,
  publication, rename, or push. Gate S1/S2 signatures are untouched.

**HOLD** for exact candidate `dc47cdf87ce864bb39afd70d842888fa7eee7953` within the frozen
A-FLOORS boundary.
