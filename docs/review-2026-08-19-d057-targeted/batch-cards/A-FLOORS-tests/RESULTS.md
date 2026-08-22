# A-FLOORS — fourth-corrected measured pre-repair results

## Verdict

**HOLD for fourth-corrected test-contract readiness, pending fresh independent Review 5.** No
production repair, post-repair pass, approval or gate replay exists.

## 1. Frozen history and correction identity

The original subject and first three corrections remain historical evidence. Review 4 reproduced
the third correction and returned FAIL in exact review-only commit
`0bf739b5be645abe6c8171c005a7181aaaadc5c8`. All four `INSTRUMENT-REVIEW-*.md` files and every
earlier matrix/log summary are byte-preserved.

The fourth-corrected harness is 975 lines, sha256
`b751b0b643c6dc28f484ca80845bd4d453e31bb85fd61a70ded68b898016df33`. Every final run below
used that external harness against a disposable clean clone at exact Review-4 commit `0bf739b`.

## 2. Fourth-corrected baseline

```text
REQUIRED 10/131
CONTROL 186/186
PRE-REPAIR DEFECTS OBSERVED
exit=1
```

The current reader passes all 54 fake-only acceptance controls and all twelve diagnostic-oracle
controls. `T-route-complete` proves 54/54 unique fake-only routes map one-to-one to 54/54 paired
requirements, with six of each exact form and no missing constant. All 317 case names are unique.
The ten held REQUIRED rows remain the four live verifier-floor canonical values and the six
`M-*` missing-definition refusals already named on one line by the baseline reader.

Raw/matrix sha256:
`33a241ca6c9dffec52b9f0a8d9fe2a741ac6c02675ba01444f6f1b2ce6524192` /
`81049470ca4a7d36385bf82a231395f85b039d7b682bc89ae4108602b84396f1`.

## 3. Diagnostic-correlation oracle

Review 4's hostile payload listed every constant on an `inspected constants:` line and emitted
only `UNRELATED_CONSTANT: duplicate executable assignment` for an actual duplicate. Against the
third-corrected oracle that payload scored 305/305.

The fourth-corrected oracle requires the mutated name and expected class on one refusal record
or line. Direct controls:

- `DR-legit-*` (6): `{NAME}: duplicate executable assignment` with nonzero status is accepted;
- `DR-uncorrelated-*` (6): the exact Review-4 split payload is rejected for that name.

The embedded `uncorrelated-diagnostic-sibling` is the Review-4 candidate on the satisfying finite
lexer. It returns:

```text
REQUIRED 41/131
CONTROL 186/186
PRE-REPAIR DEFECTS OBSERVED
exit=1
```

The 90 REQUIRED failures are exactly the named-duplicate rows: `DA/DB/DC/IA/IB` (30), `TF-*`
(48), `FC-comment-*` (6) and `HR-post-*` (6). Missing/empty/malformed/numeric/zero, paragraph,
wiring and canonical-value rows remain PASS. Every CONTROL holds, including the twelve oracle
rows and all 54 fake-only routes. This is a product-style REQUIRED miss of a defective diagnostic
policy, not an instrument/setup invalidation.

Raw/matrix sha256:
`6c6bc07ca9b59bb9214dcaa865cc6c9926e4addd54bad906bc0ad9691a1c908b` /
`15c540c565050b427d4e97486ba34a2d7d020aede82d2aa6e61e2086820f3be9`.

## 4. Exact Review-3 sibling

The faithfully reconstructed Review-3 sibling retains raw marker-before-context state and
fail-closes on non-comment `A_FLOOR_MASK` syntax. It returns:

```text
REQUIRED 131/131
CONTROL 138/186
INSTRUMENT INVALID: control failure
exit=2
```

All 305 prior v3 rows keep their previous status. The twelve diagnostic controls pass. It still
fails exactly 48 new controls: 12 each `FA-printf`, `FA-echo`, `FA-assign` and `FA-herestring`.
This is the exact Review-3 scope, not rounded to 54. 126/174 plus 12 passing diagnostic controls
is 138/186.

Raw/matrix sha256:
`634c0b999268a453923f1868ba46cd3e1a3a79064dc01af3653bf8f0711f9f68` /
`a258ba787faad740bf7ac98813701f261ddac73a89fcea0f6a7cf05ff77d1618`.

## 5. Expanded all-token sibling

A separately named candidate extends the fail-closed policy to comments. It is not described as
the exact Review-3 sibling. It passes all 305 prior rows, all 131 REQUIRED assertions and the
twelve diagnostic controls, then fails all 54 fake-only controls, including six comments:

```text
REQUIRED 131/131
CONTROL 132/186
INSTRUMENT INVALID: control failure
exit=2
```

Failure families are comment 6, and `printf`/`echo`/assignment/here-string 12 each. 120/174 plus
12 passing diagnostic controls is 132/186. Raw/matrix sha256:
`b4dd45521ede35165a532725a4c4a1573905898dac516c200f96fdb63ff0be1a` /
`1ff40412804a481264dd01cb0bf74164e5104e66291403ae5f06ac299128e600`.

Both exit-2 results are deliberate-candidate calibration: the frozen instrument correctly rejects
control-breaking readers. They are not product/setup verdicts.

## 6. Earlier causal siblings under the inverse matrix

The corrected digits-only reader remains causal:

```text
REQUIRED 125/131
CONTROL 186/186
exit=1
```

Its only failures are the six `Z-*` rows. Raw/matrix sha256:
`351350c6583f2101e34ce822c1a922a477676080dcf3d1d489293af204ef548e` /
`9e7982aea1c4930ba4df535cf6d136c322c1d03eb1f3792217efb712d87956e3`.

The exact Review-2 raw reader truthfully retains its earlier 83/131 REQUIRED result. Of the 54
fake-only controls it passes 14 (six comments plus eight last-constant cases) and fails 40
(eight vulnerable forms × five non-last constants). The twelve diagnostic controls pass, so its
current total is:

```text
REQUIRED 83/131
CONTROL 146/186
INSTRUMENT INVALID: control failure
exit=2
```

Its failure set is the prior 48 `TF-*` requirements plus 40 `FA-*` controls. Raw/matrix sha256:
`2314126ce6cc5ffae241f76825ea377a327c99dfa51f6cf5c4b38ed67378973e` /
`3842c0d9e28880859b66b27d662912be190be0e9fc9b26882aa6db752399627f`.

## 7. Satisfying control

The corrected finite exact-positive reader returns:

```text
REQUIRED 131/131
CONTROL 186/186
A_FLOORS_FOCUSED_COMPLETE
exit=0
```

All 305 prior v3 rows and all 12 diagnostic-oracle rows pass. Raw/matrix sha256:
`d8d3a9b9f5c1c63c16bca04131b1c17d755a72da2a99794aafd980d0bbe7c809` /
`63dbb5577a5a9d40c5f4df06367f77901305d26e858e6d16386c4118451e1ff5`.

## 8. Historical serial gate reliance

The gate harness/matrix remain byte-identical at
`fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0` /
`0b4d9c127e7230c7266960fe073f92f9551da9a68005cb936850993d803d1c58`. The fourth correction adds
only focused diagnostic-correlation controls, so no expensive gate was rerun. Prior serial
scores/raw hashes/timing remain historical design reliance in unchanged `logs/gate-summary.log`,
not refreshed evidence.

## 9. Limits

Full focused raw logs remain external and hash-bound. This establishes only the exact finite
grammar and same-record diagnostic correlation in `CARD.md`, not command substitution,
escaped/concatenated quoting, arbitrary redirection, general Bash parsing, generic Markdown
consistency, historical truth, implementation, certification, signing, publication or D-055
closure.

## 10. Guards

Before staging, repository guards all exited 0: worktree secret scan, review scope
(`R1=433`, `R2=47`, `R3=152`; 632/632 then-tracked files assigned), findings ledger (23 IDs;
totals match D-057), live suite-floor reader (`92/527/221/7/78/30`) and vendor-honesty mechanical
conditions. With the 14 new v4 matrix/summary files staged, the staged secret scan was clean and
review scope again exited 0 (`R1=447`, `R2=47`, `R3=152`; 646/646 tracked files assigned). The
workspace guard exited 0 with 13 machine-state findings, all 13 baselined and zero new. Workspace
success remains ratcheted: pre-existing findings are not absent.
