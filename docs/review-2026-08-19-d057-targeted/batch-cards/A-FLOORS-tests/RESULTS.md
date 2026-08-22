# A-FLOORS — fifth-corrected measured pre-repair results

## Verdict

**HOLD for fifth-corrected test-contract readiness, pending fresh independent Review 6.** No
production repair, post-repair pass, approval or gate replay exists.

## 1. Frozen history and correction identity

The original subject and first four corrections remain historical evidence. Review 5 reproduced
the fourth correction and returned FAIL in exact review-only commit
`30d6257f806276a24cb6a40319b5bbb858fa9a5d`. A concurrent independent FAIL at
`bd0c43321e7bb2e8200513fb4e97666fccdab697` named the same hole; its exact blob is preserved as
`INSTRUMENT-REVIEW-5-concurrent.md`. Reviews 1–5 and that concurrent blob, and every earlier
matrix/log summary, are byte-preserved.

The fifth-corrected harness is 1035 lines, sha256
`3f347ecf482b7f249275dec87b70c6f94f9a3b3a329a4dd02e4db4a68742a42a`. Every final run below
used that external harness against a disposable clean clone at exact Review-5 commit `30d6257`.

## 2. Fifth-corrected baseline

```text
REQUIRED 4/131
CONTROL 200/200
PRE-REPAIR DEFECTS OBSERVED
exit=1
```

The current reader passes all 54 fake-only acceptance controls and all twenty-six
diagnostic-oracle controls. `T-route-complete` proves 54/54 unique fake-only routes map one-to-one
to 54/54 paired requirements, with six of each exact form and no missing constant. All 331 case
names are unique. The four held REQUIRED rows are the four live verifier-floor canonical values.
The six `M-*` rows no longer pass: class-first `MISSING: $v is not defined` does not name the
constant as the refusal subject.

Raw/matrix sha256:
`242d0098cbf8045ce52e80c12f376581d2c3e01ac1ae11b1316ba093aa80f217` /
`b7dabf0e3ea0ede2c0fdf6bca70feeafa2d911b77e55c06e8db625078f1283e0`.

## 3. Diagnostic-correlation oracle

Review 5's hostile payload joined Review 4's two records with `;`:

```text
inspected constants: FOUNDRY_MIN_TESTS TS_MIN_TESTS VERIFIER_MIN_TESTS VERIFIER_MIN_SAMPLES VERIFIER_MIN_TAMPER VERIFIER_MIN_TAMPER_MODES; UNRELATED_CONSTANT: duplicate executable assignment
```

Against the fourth-corrected same-line matcher that payload scored 317/317 with a matrix
byte-identical to the satisfying control.

The fifth-corrected oracle requires `{NAME}:` as the named subject and treats newline and
semicolon as record boundaries. Direct controls:

- `DR-legit-*` (6): `{NAME}: duplicate executable assignment` with nonzero status is accepted;
- `DR-uncorrelated-*` (6): the exact Review-4 split payload is rejected for that name;
- `DR-oneline-*` (6): the Review-5 semicolon-joined payload is rejected for that name;
- `DR-json-*` (6): the compact JSON inventory-plus-class payload is rejected for that name;
- `DR-prefix-TAMPER` / `DR-prefix-TAMPER-MODES`: a `VERIFIER_MIN_TAMPER_MODES` subject is not a
  `TAMPER` refusal and remains a `TAMPER_MODES` refusal.

The three embedded uncorrelated siblings are the Review-4 two-line, Review-5 oneline and JSON
candidates on the satisfying finite lexer. Each returns:

```text
REQUIRED 41/131
CONTROL 200/200
PRE-REPAIR DEFECTS OBSERVED
exit=1
```

The 90 REQUIRED failures are exactly the named-duplicate rows: `DA/DB/DC/IA/IB` (30), `TF-*`
(48), `FC-comment-*` (6) and `HR-post-*` (6). Missing/empty/malformed/numeric/zero, paragraph,
wiring and canonical-value rows remain PASS. Every CONTROL holds, including the twenty-six oracle
rows and all 54 fake-only routes. The three siblings produced one shared matrix, distinct from
the satisfying control. This is a product-style REQUIRED miss of a defective diagnostic policy,
not an instrument/setup invalidation.

| Sibling | Raw SHA-256 | Matrix SHA-256 |
|---|---|---|
| two-line | `8b24e85949063a041aced443937329d1bfca8d9a7499a4191f0d4b8a5152f36b` | `b464ae62dcff31da51f5bd6391b7bc8c35c17e39fb540aa03a6c39162b522e2d` |
| oneline | `99edf1dc6d2789cd30c57ad16460fa391f70c86b5d2c58fc6560c86ef2f2de5a` | `b464ae62dcff31da51f5bd6391b7bc8c35c17e39fb540aa03a6c39162b522e2d` |
| JSON | `1598e55137f9a5a49e2b5ffde0339d74d5aa84f0295384cc8006fe8ebb5942e6` | `b464ae62dcff31da51f5bd6391b7bc8c35c17e39fb540aa03a6c39162b522e2d` |

## 4. Exact Review-3 sibling

The faithfully reconstructed Review-3 sibling retains raw marker-before-context state and
fail-closes on non-comment `A_FLOOR_MASK` syntax. It returns:

```text
REQUIRED 131/131
CONTROL 152/200
INSTRUMENT INVALID: control failure
exit=2
```

All 305 prior v3 rows keep their previous status except the intended 48 non-comment `FA-*`
controls. The twenty-six diagnostic controls pass. It still fails exactly those 48 new controls:
12 each `FA-printf`, `FA-echo`, `FA-assign` and `FA-herestring`. This is the exact Review-3
scope, not rounded to 54. 126/174 plus 26 passing diagnostic controls is 152/200.

Raw/matrix sha256:
`49ff71ac22da4683fc90d77366749078b2d4c9f19a03733749e557f413c5c17f` /
`325b2323d55acbca4da494f11c82e617317c97fbfeb8fb96fab9745f9b9cce6d`.

## 5. Expanded all-token sibling

A separately named candidate extends the fail-closed policy to comments. It is not described as
the exact Review-3 sibling. It passes all 305 prior rows, all 131 REQUIRED assertions and the
twenty-six diagnostic controls, then fails all 54 fake-only controls, including six comments:

```text
REQUIRED 131/131
CONTROL 146/200
INSTRUMENT INVALID: control failure
exit=2
```

Failure families are comment 6, and `printf`/`echo`/assignment/here-string 12 each. 120/174 plus
26 passing diagnostic controls is 146/200. Raw/matrix sha256:
`104e3b732562ce4acf9f5a326ef69c60cc86f3b3cdb9598e392f89912a0fc21a` /
`1b7d8c79585314734ee48f0ad932541fb15255e63c1eed673fd6d8c671f462d5`.

Both exit-2 results are deliberate-candidate calibration: the frozen instrument correctly rejects
control-breaking readers. They are not product/setup verdicts.

## 6. Earlier causal siblings under the inverse matrix

The corrected digits-only reader remains causal:

```text
REQUIRED 125/131
CONTROL 200/200
exit=1
```

Its only failures are the six `Z-*` rows. Raw/matrix sha256:
`7748cc056b7adcfff77a24a1ad0aa9abd1008a7edf759d2df1c7845b334fc84b` /
`3eac8a9e4657f518870ce53110c23ad4f97b229e689629184dfe712d40aab62b`.

The exact Review-2 raw reader truthfully retains its earlier 83/131 REQUIRED result. Of the 54
fake-only controls it passes 14 (six comments plus eight last-constant cases) and fails 40
(eight vulnerable forms × five non-last constants). The twenty-six diagnostic controls pass, so
its current total is:

```text
REQUIRED 83/131
CONTROL 160/200
INSTRUMENT INVALID: control failure
exit=2
```

Its failure set is the prior 48 `TF-*` requirements plus 40 `FA-*` controls. Raw/matrix sha256:
`c388f7404f15c515289f1c25c1c6c2e47f2f3198e48ee999ad7c987f9f64e798` /
`16766991f633d81c8753cc2502475b90a9ca81b5f533aefbd90615ee7013d7c2`.

## 7. Satisfying control

The corrected finite exact-positive reader returns:

```text
REQUIRED 131/131
CONTROL 200/200
A_FLOORS_FOCUSED_COMPLETE
exit=0
```

All 305 prior v3 rows and all 26 diagnostic-oracle rows pass. Raw/matrix sha256:
`c362678e42aa26d67ad1206cff5b5077cae6969c375f751417c02dc374278adc` /
`ea972bff0f769c8acb177134d1ce5ddbcc03fcc18d89d704af2579f10d5e212a`.

## 8. Historical serial gate reliance

The gate harness/matrix remain byte-identical at
`fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0` /
`0b4d9c127e7230c7266960fe073f92f9551da9a68005cb936850993d803d1c58`. The fifth correction adds
only focused diagnostic-correlation controls, so no expensive gate was rerun. Prior serial
scores/raw hashes/timing remain historical design reliance in unchanged `logs/gate-summary.log`,
not refreshed evidence.

## 9. Limits

Full focused raw logs remain external and hash-bound. This establishes only the exact finite
grammar and named-subject diagnostic correlation in `CARD.md`, not command substitution,
escaped/concatenated quoting, arbitrary redirection, general Bash parsing, generic Markdown
consistency, historical truth, implementation, certification, signing, publication or D-055
closure.

## 10. Guards

Before staging, repository guards all exited 0: worktree secret scan, review scope
(`R1=448`, `R2=47`, `R3=152`; 647/647 then-tracked files assigned), findings ledger (23 IDs;
totals match D-057), live suite-floor reader (`92/527/221/7/78/30`) and vendor-honesty mechanical
conditions. With the new v5 matrix/summary files and concurrent Review-5 record staged, the
staged secret scan was clean and review scope again exited 0 (`R1=467`, `R2=47`, `R3=152`;
666/666 tracked files assigned). The workspace guard exited 0 with 13 machine-state findings,
all 13 baselined and zero new. Workspace success remains ratcheted: pre-existing findings are
not absent.
