# C-SNAPSHOT — corrected measured results

## Verdict

**HOLD for corrected test-contract readiness, pending fresh independent review.** F1 is closed by
seven exact full messages plus four adversarial oracle controls. F2 is closed by all pair
directions, all six triple first-occurrence permutations and causally discriminating rank/reset
mutants. No production implementation has been made or approved.

## 1. Frozen bytes and correction identity

| Item | Result |
|---|---|
| behavioral baseline | `1655b120a653b60ccb5b3a22583c0001d59ea7a4` |
| failed first review | `8834d9b868657fbccfe1009bf139e23dc8e06db1`; `INSTRUMENT-REVIEW-1.md` sha256 `ffad26f2c8307aa7fcf9e2c7e18dd971eace47b955132f65222bbb1c335febf0` |
| corrected `TESTS.patch` | applies cleanly; sha256 `c2a53a4707d62c3e6632405037d684216c8319dd79fdaad15da2c15de6c69de1` |
| extracted test source | 485 lines; sha256 `eea8876c38545db864df36f8d75e7a10e53b47ee730d805dc4ed984f88d6c1f7` |
| corrected mutation driver | 270 lines; sha256 `223e784d3804aad8fb7e9a12424c94d19a60418ad4905c3959bcfc707123b4f8` |
| TypeScript typecheck | exit 0 for baseline and every mutant; raw log sha256 `8fa1cf5506304e8abac55868e7f1a136c9b1dde57a3981a382da4c21ea129a6f` |
| patch/diff check | pass |

The review record is not edited. This correction changes only existing instrument/evidence files
inside this directory.

## 2. Exact corrected pre-repair focused result

The corrected patch on the unchanged behavioral baseline returns **9 pass / 13 fail** across 22
tests. Passing controls are stable success; pure B1; pure B2 height movement; pure B2 same-height
reorg; ordinary RPC/read failure; and all four oracle-negative controls.

The thirteen intended failures are pure B3, all six ordered-pair cases and all six triple
first-occurrence permutations. Request-count assertions run before classification in every route
and pass. Pure B3 fails `pendingOnly`; B1/B3 pairs fail the same live property until any B2 sets
the baseline flag false; the remaining cases fail their exact expected cause-set sentence.

Raw focused-output sha256:
`fdbb1361b1875b36e3bacf778ca063f4f8d328ff6fb39ee0a171e50cd75dd4e9`.
`logs/focused-baseline-summary.log` preserves all 22 scored names without path/timing noise.

## 3. F1 oracle-negative controls

All four controls pass by observing a named rejection:

| False candidate | Named rejection |
|---|---|
| expected B1 phrase explicitly negated | exact B1 full-message mismatch |
| otherwise B1 text with `50 attempts` | attempt budget not bound to `5 attempts` |
| exact B1+B2 text supplied for B1 | exact B1 full-message mismatch |
| mixed B1+B2 text claiming every attempt ended both ways | exact B1+B2 full-message mismatch |

Because the production route tests use the same `assertExactMessage` helper, these are live
self-tests of the actual oracle rather than prose examples.

## 4. Typecheck-clean mutation calibration

`mutation-matrix.tsv` carries exact totals and raw hashes. No typecheck failure is credited.

| Case | Pass / fail | Causal observation |
|---|---:|---|
| live baseline | 9 / 13 | B3 plus all mixed/order defects live |
| B1 → movement | 8 / 14 | pure B1 property fails incrementally |
| B2 → pending | 7 / 15 | pure B2a and B2b properties fail incrementally |
| B3 → movement | 9 / 13 | pure B3 advances to exact B3-message failure |
| pure messages swapped | 6 / 16 | pure B1/B2 exact sentences fail incrementally |
| generic message collapse | 6 / 16 | all sixteen exhaustion sentences fail |
| negated pure-B1 message | 8 / 14 | pure B1 exact sentence rejects semantic negation |
| rank-order accumulator | 14 / 8 | three reversed pairs and five non-ascending triples fail; pure/ascending pass |
| reset-on-repeat accumulator | 10 / 12 | every mixed route fails; all pure/oracle controls pass |

The rank/reset mutants contain otherwise-correct exact cause-set messages and property handling.
Their failures therefore measure the expanded F2 routes rather than the baseline collapse.

## 5. Top-level fast-gate binding

| Case | Foundry | TypeScript | Later scored consumers | Top level |
|---|---|---|---|---|
| unchanged baseline, no patch | 103/103 | 527/527 | verifier 221; samples 7; tamper 78/30 | **exit 0, GATE PASSED** |
| same baseline + corrected patch only | 103/103 | 536/549; exactly thirteen named new failures | ablation regeneration and verifier consumers remain green | **exit 5, GATE FAILED; supervisor refuses completion** |

Raw gate hashes are
`01c623750c70a15a9e900ce11f7bf813597e896c4f23ae160a97628a06f45dd9` for the unchanged control
and `67af49c9a81b3e0a6f4fc8d4803742063d856d5ec6fdc7e147760324c9518a9d` for patch-only
falsification. The patched count is the unchanged 527 plus 22 new tests: nine pass and thirteen
fail. The four negative-oracle controls are among the nine passes.

No post-implementation pass exists and none is claimed. The deep profile was not run; the
requested corrected test-contract binding is the fast gate.

## 6. Measurement hygiene

All corrected patch application, focused runs, mutations and gates ran in an isolated detached
checkout. Raw path-bearing logs remain outside the repository and are bound here by sha256.

The original contract's disclosed wrong-working-directory typecheck attempt remains excluded
historical measurement. It was not reused. Every corrected mutant used `npm --prefix ts run
typecheck`, exited 0 and then ran behaviorally.

## 7. Repository and workspace guards

With only the fourteen bounded instrument/evidence corrections staged:

- cached diff check and all fourteen payload checksums: pass;
- secret guard, worktree and staged: clean;
- review scope: pass, all 584 tracked files assigned (R1 386 / R2 46 / R3 152);
- findings ledger: pass, 23 finding IDs and ruled disposition totals unchanged;
- suite floors: pass at Foundry 92, TypeScript 527, verifier 221/7/78/30;
- vendor-honesty mechanical guard: pass, with D-008(1)/(3) still John's authority as printed; and
- workspace guards: pass, 13 machine-state findings baselined and zero new.

The workspace result is ratcheted, not a claim that the thirteen accepted findings are absent.
Sentinel has no visual/aspect/contrast stage in this non-Godot guard route.

## 8. Limits carried with the HOLD

This HOLD is only for the corrected frozen test instrument and `COVERAGE.md` boundary, and still
requires fresh independent review. It does not approve an implementation, claim the message
reaches a signed refusal, repair or own Batch D's false detail statement, add a public reason code,
reconcile floors, assess D-055, sign/reopen a gate, certify a claim, ratify or publish text,
rename, expose held D-008 questions or authorize a push.
