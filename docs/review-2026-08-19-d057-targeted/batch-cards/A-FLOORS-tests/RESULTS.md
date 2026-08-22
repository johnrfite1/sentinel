# A-FLOORS — third-corrected measured pre-repair results

## Verdict

**HOLD for third-corrected test-contract readiness, pending fresh independent Review 4.** No
production repair, post-repair pass, approval or gate replay exists.

## 1. Frozen history and correction identity

The original subject and first two corrections remain historical evidence. Review 3 reproduced
the second correction and returned FAIL in exact review-only commit
`cd12ac26fb718a9bd02971db1f09f4fe1189bba7`. All three `INSTRUMENT-REVIEW-*.md` files and every
earlier matrix/log summary are byte-preserved.

The third-corrected harness is 926 lines, sha256
`4bc09b9c4f835f28fcfc114a6f9b78c6bb3e102d3513eae545bdb1ad5996bb80`. Every final run below
used that external harness against a disposable clean clone at exact Review-3 commit.

## 2. Third-corrected baseline

```text
REQUIRED 10/131
CONTROL 174/174
PRE-REPAIR DEFECTS OBSERVED
exit=1
```

The current reader passes all 54 new fake-only acceptance controls. `T-route-complete` proves
54/54 unique fake-only routes map one-to-one to 54/54 paired requirements, with six of each exact
form and no missing constant. All 305 case names are unique.

Raw/matrix sha256:
`cb2e9e89edc3d032483a5241df06d7d0fcae499de49c85acd3f40d763061d7f4` /
`98a3f66489827f8632be5b32395d2e02841fc456099f5f179e213eeda71f95ca`.

## 3. Opposite-side reader oracle

Each existing paired route now has a same-position `FA-*` control containing its exact fake opener
without indented 999. It requires all of:

- checker exit 0;
- no duplicate, missing, malformed, empty, numeric, derivation or refusal diagnostic; and
- exact reporting of all six canonical values.

Adding the indented 999 then leaves the opener identical, produces exact Bash trace
`[planned, 999]`, final value 999, and requires the named duplicate refusal. The reader therefore
cannot satisfy the pair by rejecting the inert token itself.

## 4. Exact Review-3 sibling

The faithfully reconstructed Review-3 sibling retains raw marker-before-context state and
fail-closes on non-comment `A_FLOOR_MASK` syntax. It returns:

```text
REQUIRED 131/131
CONTROL 126/174
INSTRUMENT INVALID: control failure
exit=2
```

All 251 prior rows remain PASS. It passes all required rows and the six full-line-comment-only
controls, but fails exactly 48 new controls: 12 each `FA-printf`, `FA-echo`, `FA-assign` and
`FA-herestring`. This is the exact Review-3 scope, not rounded to 54.

Raw/matrix sha256:
`b7950c4b1e4ca075ca6a32e525f5e1ea108f6c205cd6f862c378871e3eea101e` /
`feb1ede79e3cff8ca38d34e1a747116daeac73589c982fa12be1781c2347f2f4`.

## 5. Expanded all-token sibling

A separately named candidate extends the fail-closed policy to comments. It is not described as
the exact Review-3 sibling. It passes all 251 prior rows and all 131 REQUIRED assertions but fails
all 54 new fake-only controls, including six comments:

```text
REQUIRED 131/131
CONTROL 120/174
INSTRUMENT INVALID: control failure
exit=2
```

Failure families are comment 6, and `printf`/`echo`/assignment/here-string 12 each. Raw/matrix
sha256:
`6e9daec8628d84707d1f7b1485fd85d1f6ca4eb29e7bb26071329f83e020ef2f` /
`c9f40f79b8acac473701a1c17d2d928a93905369bbe3c41734c29afbaa4f5101`.

Both exit-2 results are deliberate-candidate calibration: the frozen instrument correctly rejects
control-breaking readers. They are not product/setup verdicts.

## 6. Earlier causal siblings under the inverse matrix

The corrected digits-only reader remains causal:

```text
REQUIRED 125/131
CONTROL 174/174
exit=1
```

Its only failures are the six `Z-*` rows. Raw/matrix sha256:
`d9f08c88bed66e38b6789114fd4a20d7da104d5c2d138097e7ec6d935c67f47e` /
`bbeaaf8a18d4ee08e9990b339ea3e5f426d19c3198adcfb9ae6ca9c27761c3e1`.

The exact Review-2 raw reader truthfully retains its earlier 83/131 REQUIRED and 120/120 prior
CONTROL result. Of the 54 new controls it passes 14 (six comments plus eight last-constant cases)
and fails 40 (eight vulnerable forms × five non-last constants), so its current total is:

```text
REQUIRED 83/131
CONTROL 134/174
INSTRUMENT INVALID: control failure
exit=2
```

Its failure set is the prior 48 `TF-*` requirements plus 40 `FA-*` controls. Raw/matrix sha256:
`65e1cf30e3c123a5485741e8544d3da6e45a6225d8ee73827046628bb85a778d` /
`9456409625b1f49570c34580adbe1c0b7fc45d834965cfdeb3710d80aae97ecf`.

## 7. Satisfying control

The corrected finite exact-positive reader returns:

```text
REQUIRED 131/131
CONTROL 174/174
A_FLOORS_FOCUSED_COMPLETE
exit=0
```

All 251 prior and 54 added rows pass. Raw/matrix sha256:
`a3a1c390ab03a53d19596d473fcbdfc3b38852d5775a3f7a1edc6ee45685bf16` /
`15e53549138fb45d19c8b89d8f2dd676abdeb576aa735b195c20218e858bfe2d`.

## 8. Historical serial gate reliance

The gate harness/matrix remain byte-identical at
`fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0` /
`0b4d9c127e7230c7266960fe073f92f9551da9a68005cb936850993d803d1c58`. The third correction adds
only focused reader controls, so no expensive gate was rerun. Prior serial scores/raw hashes/timing
remain historical design reliance in unchanged `logs/gate-summary.log`, not refreshed evidence.

## 9. Limits

Full focused raw logs remain external and hash-bound. This establishes only the exact finite
grammar in `CARD.md`, not command substitution, escaped/concatenated quoting, arbitrary
redirection, general Bash parsing, generic Markdown consistency, historical truth,
implementation, certification, signing, publication or D-055 closure.

## 10. Guards

Before staging, repository guards all exited 0: worktree secret scan, review scope
(`R1=420`, `R2=47`, `R3=152`; 619/619 then-tracked files assigned), findings ledger (23 IDs;
totals match D-057), live suite-floor reader (`92/527/221/7/78/30`) and vendor-honesty mechanical
conditions. With all 12 new v3 matrix/summary files staged, the staged secret scan was clean and
review scope again exited 0 (`R1=432`, `R2=47`, `R3=152`; 631/631 tracked files assigned). The
workspace guard exited 0 with 13 machine-state findings, all 13 baselined and zero new. Workspace
success remains ratcheted: pre-existing findings are not absent.
