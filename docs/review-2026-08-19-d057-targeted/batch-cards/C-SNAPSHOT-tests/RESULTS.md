# C-SNAPSHOT — twice-corrected measured results

## Verdict

**HOLD for corrected test-contract readiness, pending fresh independent review.** The second
correction preserves the exact seven-message F1 contract and retained named order fixtures, and
closes Review 2's late-first/repeat hole with a finite 486-route aggregate. No production
implementation has been made or approved.

## 1. Frozen bytes and correction identity

| Item | Result |
|---|---|
| behavioral baseline | `1655b120a653b60ccb5b3a22583c0001d59ea7a4` |
| first FAIL review | commit `8834d9b868657fbccfe1009bf139e23dc8e06db1`; file sha256 `ffad26f2c8307aa7fcf9e2c7e18dd971eace47b955132f65222bbb1c335febf0` |
| second FAIL review | commit `71cfa70b8267d5e2950af99307abf372992c008b`; file sha256 `25e336b97194ee58f6e20c367163726a3a4e9c8b2566e86bc76ab1fbdc3b201e` |
| twice-corrected `TESTS.patch` | applies cleanly; 609 lines; sha256 `b6fc3c713e97c2fdfc328516eeb42fdb4f3cc25d0648602ea654e6cf1513c9f1` |
| extracted test source | 603 lines; sha256 `29a673560e89b639b6635661706a368454c9969a04c5d37c4f6c15229df3dd8a` |
| mutation/control driver | 298 lines; sha256 `f404a5ffe7d00a8d4978cd235c3c2a57c62a6e332a8d7106699db5eddd45ef2f` |
| TypeScript typecheck | exit 0 for baseline and all ten driver cases; each raw log sha256 `8fa1cf5506304e8abac55868e7f1a136c9b1dde57a3981a382da4c21ea129a6f` |
| patch/diff check | pass |

Both review records are byte-unchanged. This correction changes only existing instrument/evidence
files inside this directory.

## 2. Focused pre-repair result and complete traversal

The patch on the unchanged baseline returns **9 pass / 14 fail across 23 top-level tests**. The
retained 22 score exactly as before: nine controls pass and thirteen named R2-F6 routes fail. The
new aggregate is the fourteenth failure.

The aggregate completes all subcases before its final assertion:

`attempted=486/486 observed=486/486 route-verified=486/486 classification-checked=486/486`

Baseline has 482 aggregated classification failures: only the two pure-B1 polarity routes and two
pure-B2 polarity routes match its current two-message model. All exact route-count checks pass.
Raw focused-output sha256:
`7066885e18c81f936137017799e7f451849cc0683afd4995d7f9bb646c2b1aba`.
The tracked focused summary preserves all 23 scored names and the exhaustive counters.

## 3. Exact message self-controls

All four oracle-negative controls pass by observing their named rejection:

| False candidate | Named rejection |
|---|---|
| expected B1 phrase explicitly negated | exact B1 full-message mismatch |
| otherwise B1 text with `50 attempts` | attempt budget not bound to `5 attempts` |
| exact B1+B2 text supplied for B1 | exact B1 full-message mismatch |
| mixed B1+B2 text claiming every attempt ended both ways | exact B1+B2 full-message mismatch |

They exercise the same `assertExactMessage` helper used by every real route.

## 4. Typecheck-clean mutation/control calibration

Every row typechecks at exit 0. Every exhaustive row reports all four traversal counters at
486/486. Compile or warning/typecheck failure is not credited.

| Case | Pass / fail | Exhaustive classification failures | Raw test sha256 |
|---|---:|---:|---|
| live baseline | 9 / 14 | 482 | `7066885e18c81f936137017799e7f451849cc0683afd4995d7f9bb646c2b1aba` |
| B1 → movement | 8 / 15 | 484 | `03e1288c015c355cbc819708ac0828107aa819bfc90b44c9548d372995f9ae10` |
| B2 → pending | 7 / 16 | 484 | `87029b2aad40f122d3b9e43f4133a16a58e13002948e5608a0d7c1d81ea22f2e` |
| B3 → movement | 9 / 14 | 482 | `ca6611df8f8f27f90ef77cbd872d5f01b3045f23bc5cba6d9f95644365345515` |
| pure messages swapped | 6 / 17 | 486 | `cab81045528bfc15d613f7a50ddd2c3cdb4141fbdff99bdb1402e13f72e30782` |
| generic message collapse | 6 / 17 | 486 | `acf545d496ee8c061dae2ffefddb00dbda15b0dcf8e605a873d58c75489657b8` |
| negated pure B1 | 8 / 15 | 484 | `35172dfd8854623b0b8fe7b053ac6471d5a99647617548915373b7e2ddb9acad` |
| exact accumulator CONTROL | **23 / 0** | **0** | `c6bdcb3a7941cef848b3851c552ce8e235065893b3a08cc5ec18926b58173478` |
| rank-order accumulator | 14 / 9 | 340 | `30c73652bce17cea93400fce26dd331259a09d60663cf057b4298909a2444f19` |
| reset-on-repeat accumulator | 10 / 13 | 360 | `c2153e3e4c366170c0e03016f723e41c8b9be4e77137551eb0d8495b63ecea2d` |
| freeze-after-first-repeat | **22 / 1** | **276** | `b7e96cfae4ca4e9054601b7dca32d023d5d344095d1ad9f21d2ae0de43b67027` |

The exact control establishes a compatible satisfying implementation shape. The freeze mutant
keeps every original named test green and is caught only by the exhaustive aggregate, so its
failure is causal evidence for late arrival after repetition, not generic rejection. Rank/reset
retain their prior named discriminations and gain the aggregate top-level failure.

## 5. Top-level fast-gate binding

| Case | Foundry | TypeScript | Later scored consumers | Top level |
|---|---|---|---|---|
| unchanged baseline, no patch | 103/103 | 527/527 | verifier 221; samples 7; tamper 78/30 | **exit 0, GATE PASSED** |
| same baseline + corrected patch only | 103/103 | 536/550; exactly fourteen new failures | ablation regeneration and verifier consumers remain green | **exit 5, GATE FAILED; supervisor refuses completion** |

The fourteen failures are the retained thirteen named R2-F6 failures plus the exhaustive
aggregate. Its failure output still reports 486/486 for attempted, observed, route-verified and
classification-checked. Raw gate hashes are
`28e15ef7c8de62ec4a517af2940c7a2e721a5485f48a702692a31a24c5afb67a` for the unchanged
control and
`b17e2eedf201fb3af688b77b9be987dc8c32fd504a44766b63215ebc53d40931` for patch-only
falsification. The patched count is 527 existing plus 23 new: nine pass and fourteen fail.

No post-implementation pass exists. The deep profile was not run; the requested contract binding
is the fast gate.

## 6. Measurement hygiene

All patch application, focused runs, mutations and gates ran in an isolated detached checkout.
Raw path-bearing logs remain outside the repository and are bound here by sha256. Every driver
case used `npm --prefix ts run typecheck`, exited 0 and then ran behaviorally. The original
contract's disclosed wrong-working-directory attempt remains excluded historical measurement.

## 7. Repository and workspace guards

With only bounded C-SNAPSHOT instrument/evidence corrections staged:

- cached diff check and every payload checksum: pass;
- secret guard, worktree and staged: clean;
- review scope: pass, all 585 tracked files assigned (R1 387 / R2 46 / R3 152);
- findings ledger: pass, 23 finding IDs and ruled disposition totals unchanged;
- suite floors: pass at Foundry 92, TypeScript 527 and verifier 221/7/78/30;
- vendor-honesty mechanical guard: pass, with D-008(1)/(3) still John's authority as printed; and
- workspace guards: pass, 13 machine-state findings baselined and zero new.

The workspace result is ratcheted, not a claim that accepted findings are absent. Sentinel has no
visual/aspect/contrast stage in this non-Godot guard route.

## 8. Limits carried with the HOLD

This HOLD is only for the twice-corrected frozen test instrument and declared coverage boundary,
and still requires fresh independent review. It does not approve implementation, claim the
message reaches a signed refusal, repair or own Batch D's false detail statement, add a public
reason code, reconcile floors, assess D-055, sign/reopen a gate, certify a claim, ratify or
publish text, rename, expose held D-008 questions or authorize a push.
