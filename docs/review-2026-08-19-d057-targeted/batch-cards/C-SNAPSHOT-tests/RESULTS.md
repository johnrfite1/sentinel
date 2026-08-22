# C-SNAPSHOT — measured results

## Verdict

**HOLD for test-contract readiness.** The independent patch discriminates the frozen B1/B2/B3
branch/exhaustion matrix, reproduces every live R2-F6 classification hole at a named assertion,
preserves stable/pure-existing/ordinary-failure controls, and is bound to the unchanged fast gate.
No production implementation has been made or approved.

## 1. Frozen bytes

| Item | Result |
|---|---|
| subject | `1655b120a653b60ccb5b3a22583c0001d59ea7a4` |
| `TESTS.patch` | applies cleanly; sha256 `51fba356e71fe648e78e85d551b6092b649d843645dde4338f64ca6b932450df` |
| extracted test source | 329 lines; sha256 `92267b368fb24c1f466e63d7d8344d6884d00c5e96957d612047c642228652c5` |
| TypeScript typecheck | exit 0; raw log sha256 `8fa1cf5506304e8abac55868e7f1a136c9b1dde57a3981a382da4c21ea129a6f` |
| test diff check | pass |

## 2. Exact pre-repair focused result

The frozen patch on the unchanged subject returns **5 pass / 5 fail**:

```text
PASS CONTROL stable success returns the hashed pin after exactly eleven pinned reads
PASS CONTROL pure B1: pending head is rejected before reads and named accurately
PASS CONTROL pure B2 movement: advanced height after reads is named accurately
PASS CONTROL pure B2 reorg: same-height replacement after reads is named accurately
FAIL R2-F6 pure B3: pending confirmation is neither pre-read pending nor movement
FAIL R2-F6 mixed B1+B3: names pre-read pending and pending confirmation only
FAIL R2-F6 mixed B1+B2: names pending-before-read and changed-after-read without universals
FAIL R2-F6 mixed B2+B3: names changed head and pending confirmation without conflation
FAIL R2-F6 mixed B1+B2+B3: names all and only causes actually exhausted
PASS CONTROL ordinary RPC/read failure is not reclassified as chain instability
```

Raw focused-output sha256:
`de9d70a0c592227dd562787829b182c3b564bba69348b324f46a38be3ee3f00d`.
The raw path-bearing output remains outside the repository; `logs/focused-baseline-summary.log`
preserves the exact scored lines without timing or path noise.

The first two failures stop at the `pendingOnly` assertion: a B3 attempt began with a hashed head
and issued reads, so it is not pure pre-read pending. The other three stop at their first omitted
cause recognizer. Every fixture's request-count assertions ran before classification and passed.

## 3. Mutation calibration

`mutation-matrix.tsv` contains one live baseline-collapse row plus five exact mutations. All five
typecheck; all five are caught behaviorally. No typecheck failure is credited.

| Direction | Incremental observation beyond the five live failures |
|---|---|
| B1 → movement | pure B1 fails `pendingOnly` semantics |
| B2 → pending | pure height movement and pure reorg fail `pendingOnly` semantics |
| B3 → movement | pure B3 fails specifically because movement was named |
| pure messages swapped | pure B1 and both B2 controls fail their message recognizers |
| messages collapsed to generic | all eight exhaustion message oracles fail |

The B3 mutation has the same 5/5 total as baseline but a different named assertion: baseline pure
B3 fails `pendingOnly=true`; the mutant passes that property and then fails
`movement classification mismatch`. This proves the mutation moved the intended observation.

## 4. Top-level fast-gate binding

| Case | Foundry | TypeScript | Later scored consumers | Top level |
|---|---|---|---|---|
| unchanged subject, no patch | 103/103 | 527/527 | verifier 221; samples 7; tamper 78/30 | **exit 0, GATE PASSED** |
| same subject + `TESTS.patch` only | 103/103 | 532/537; exactly five named new failures | ablation regeneration and verifier consumers remain green | **exit 5, GATE FAILED; supervisor refuses completion** |

No post-repair pass exists yet and none is claimed. The deep profile was not run; the requested
test-contract binding is the fast gate.

## 5. Development exclusions

One early mutation command ran `npm run typecheck` from the repository root, which has no
`package.json`; npm exited before testing production. That run measured nothing and contributes no
catch. It was rerun correctly with `npm --prefix ts run typecheck`. Only the final hashes and
matrix above support the verdict.

## 6. Repository and workspace guards

With only this evidence directory staged:

- cached diff check and all thirteen payload checksums: pass;
- secret guard, worktree and staged: clean;
- review scope: pass, all 583 tracked files assigned (R1 385 / R2 46 / R3 152);
- findings ledger: pass, 23 finding IDs and ruled disposition totals unchanged;
- suite floors: pass at Foundry 92, TypeScript 527, verifier 221/7/78/30;
- vendor-honesty mechanical guard: pass, with D-008(1)/(3) still John's authority as printed; and
- workspace guards: pass, 13 machine-state findings baselined and zero new.

The workspace result is ratcheted, not a claim that the thirteen accepted findings are absent.
Sentinel has no visual/aspect/contrast stage in this non-Godot guard route.

## 7. Limits carried with the HOLD

This HOLD is only for the frozen test instrument and `COVERAGE.md` boundary. It does not approve
an implementation, claim the message reaches a signed refusal, repair or own Batch D's false
detail statement, add a public reason code, reconcile floors, assess D-055, sign/reopen a gate,
certify a claim, ratify or publish text, rename, expose held D-008 questions, or authorize a push.
