# A-FLOORS — sixth-corrected measured pre-repair results

## Verdict

**HOLD for sixth-corrected test-contract readiness, pending fresh independent Review 7.** No
production repair, post-repair pass, approval or gate replay exists.

## 1. Frozen history and correction identity

The original subject and first five corrections remain historical evidence. Review 6 reproduced
the fifth correction and returned FAIL in exact review-only commit
`b4553841e4d234b947c008f340dce4f6a1a28b02`. Reviews 1–6 and the concurrent Review-5 blob, and
every earlier matrix/log summary, are byte-preserved.

The sixth-corrected harness is 1116 lines, sha256
`1c298341fb807b54fa15e1e95f4084db5b9ce4881bb52099f5499e0811b8c93c`. Every final run below
used that external harness against a disposable clean clone at exact Review-6 commit `b455384`.

## 2. Sixth-corrected baseline

```text
REQUIRED 4/131
CONTROL 212/212
PRE-REPAIR DEFECTS OBSERVED
exit=1
```

The current reader passes all 54 fake-only acceptance controls and all thirty-eight
diagnostic-oracle controls. `T-route-complete` proves 54/54 unique fake-only routes map one-to-one
to 54/54 paired requirements. All 343 case names are unique. The four held REQUIRED rows are the
four live verifier-floor canonical values.

Raw/matrix sha256:
`690067abeb4c0a984319cb439e9b6c82d488c03f4787377832090296b68dbd5a` /
`74500e901beeb34a9916ee44d7a890b2ca75370f960d41933f27fffc660dd724`.

## 3. Diagnostic-correlation oracle

Review 6's pretty-printed name-as-key JSON listed every constant as `{NAME}: duplicate
executable assignment` inside `{` / `}` wrapper records. Against the fifth-corrected matcher
that payload scored 343/343 with a matrix byte-identical to the satisfying control.

The sixth-corrected oracle requires the exact class phrase, rejects other floor names after the
colon, and requires a unique named subject when `{` or `}` is its own record. Direct controls are
the thirty-eight `DR-*` rows in `CARD.md` §4.

Five embedded uncorrelated siblings (two-line, oneline, compact JSON, pretty JSON, same-record
inventory) each return:

```text
REQUIRED 41/131
CONTROL 212/212
PRE-REPAIR DEFECTS OBSERVED
exit=1
```

The 90 REQUIRED failures are exactly the named-duplicate rows: `DA/DB/DC/IA/IB` (30), `TF-*`
(48), `FC-comment-*` (6) and `HR-post-*` (6). The five siblings produced one shared matrix,
distinct from the satisfying control.

| Sibling | Raw SHA-256 | Matrix SHA-256 |
|---|---|---|
| two-line | `8e21ab9742fc728e107fa45d5015c504233604b9a0278ab99ee115c028b19887` | `37329860d7787ea0ee5edda3f30bd4b7d0064353d24b175b5a6e4730ebe8e1c8` |
| oneline | `b394de40bbb2c2df2a0b13d1347726e466768c4fe2010dc011ffa3836a7db411` | `37329860d7787ea0ee5edda3f30bd4b7d0064353d24b175b5a6e4730ebe8e1c8` |
| compact JSON | `e7e5510f0e03b39a39cf201a0bb8a053925e2abbb8e3298bd8c24238d7ae1203` | `37329860d7787ea0ee5edda3f30bd4b7d0064353d24b175b5a6e4730ebe8e1c8` |
| pretty JSON | `da9cce34ea8ad7a5fa1b7bd70df126b37ca7dea68e63d7bdea32f090d7f401d1` | `37329860d7787ea0ee5edda3f30bd4b7d0064353d24b175b5a6e4730ebe8e1c8` |
| same-record inventory | `68255068263525ceeb1a56af9e9ad43255ca1c3f0f51e9ab5c301d2f20bec5d4` | `37329860d7787ea0ee5edda3f30bd4b7d0064353d24b175b5a6e4730ebe8e1c8` |

## 4. Exact Review-3 sibling

```text
REQUIRED 131/131
CONTROL 164/212
INSTRUMENT INVALID: control failure
exit=2
```

It fails exactly 48 non-comment `FA-*` controls. 126/174 plus 38 passing diagnostic controls is
164/212. Raw/matrix sha256:
`77799ddd97b0a9d919c57bc8be4ec3d1966b8559b7479b86e754ccb6f86c960d` /
`4451ccdadb92467c78811408188b4f7e7eafae3eaab593db7bb3de272b73f6dc`.

## 5. Expanded all-token sibling

```text
REQUIRED 131/131
CONTROL 158/212
INSTRUMENT INVALID: control failure
exit=2
```

It fails all 54 fake-only controls. 120/174 plus 38 passing diagnostic controls is 158/212.
Raw/matrix sha256:
`304917e7340589d3c0c25693c3582848c4fdf3d2694c5d0fea60e882662da195` /
`b09209d81d4b3fe032ab1de6bb3261d608c6964e00ec501d77baa01a9c46b7c4`.

## 6. Earlier causal siblings under the inverse matrix

Digits-only:

```text
REQUIRED 125/131
CONTROL 212/212
exit=1
```

Raw/matrix sha256:
`0cf9f8a49c2704fcb0812f18f323b46ace6829a1eba103efa8901eb5273e3fa6` /
`e3b72a952470a051d0650abf5e6b71ee441f36e191954e7f37c0e38747fc856f`.

Review-2 raw:

```text
REQUIRED 83/131
CONTROL 172/212
INSTRUMENT INVALID: control failure
exit=2
```

Raw/matrix sha256:
`dc5b987e22ead342ecb0b6c3be82f52e41efd0a2e0c15c125c047bd3b5f73bf9` /
`2ac06deb1121d39b3eb2cbdf19443a1313f2f7b21738bf217e7b3c91ce2b80cd`.

## 7. Satisfying control

```text
REQUIRED 131/131
CONTROL 212/212
A_FLOORS_FOCUSED_COMPLETE
exit=0
```

Raw/matrix sha256:
`2ff602c7c33c58681d9b8fa7789d14622ed971634084469c9679efd364517175` /
`7f3ddf691b9619669ed221c94b1f0ab58e581a1db2086727772043afeadabfa1`.

## 8. Historical serial gate reliance

The gate harness/matrix remain byte-identical at
`fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0` /
`0b4d9c127e7230c7266960fe073f92f9551da9a68005cb936850993d803d1c58`. No expensive gate was
rerun.

## 9. Limits

This establishes only the exact finite grammar and named-subject diagnostic correlation in
`CARD.md`, including Review 6's pretty-printed JSON and same-record inventory holes. It is not
implementation, certification, signing, publication or D-055 closure.

## 10. Guards

Before staging, repository guards all exited 0: worktree secret scan, review scope
(`R1=468`, `R2=47`, `R3=152`; 667/667 then-tracked files assigned), findings ledger (23 IDs;
totals match D-057), live suite-floor reader (`92/527/221/7/78/30`) and vendor-honesty mechanical
conditions. With the new v6 matrix/summary files staged, the staged secret scan was clean and
review scope again exited 0 (`R1=490`, `R2=47`, `R3=152`; 689/689 tracked files assigned). The
workspace guard exited 0 with 13 machine-state findings, all 13 baselined and zero new.
Workspace success remains ratcheted: pre-existing findings are not absent.
