# A-FLOORS — fresh independent fourth-corrected instrument review 5

## Verdict

**FAIL for instrument readiness.** The fourth correction closes Review 4's exact two-line
payload: the committed `uncorrelated-diagnostic-sibling` fails 90 named-duplicate REQUIRED rows
and holds every CONTROL. The common matcher still accepts the mutated name and the reason word as
uncorrelated substrings of one line. Joining Review 4's two records with `;` instead of a newline
returns **131/131 REQUIRED and 186/186 CONTROL**, exit 0, and a matrix byte-identical to the
satisfying exact-positive control. That reader never names the mutated constant as the subject of
the refusal. The twelve new `DR-*` rows cannot catch it: they score a hardcoded two-line string
inside the harness, not the candidate.

This is an instrument-readiness verdict only. It is not an implementation verdict, gate approval
or signature, certification, ratification, publication, rename, D-055 assessment, D-008 action
or push authorization.

## 1. Exact subject, scope and preservation

I reviewed exact subject `178347dbf33ab70923a6fd0278ea61c5dec5e6b6`, tree
`1b5f028aa217da5e389c28a062d43b5350c60d96`, whose sole parent is Review-4 FAIL
`0bf739b5be645abe6c8171c005a7181aaaadc5c8` (tree `2b7265c78e549ba290f0ec2c138c7bc5718b7fcf`).

The parent-to-subject correction contains exactly 23 paths, all beneath this `A-FLOORS-tests/`
evidence directory: nine modified evidence/harness files and fourteen added v4
matrices/summaries, with 2,627 insertions and 145 deletions. It changes no production byte,
existing product test/script, live gate, maintained claim, decision record, signed material or
prior review. `git diff --check` passes. All 57 entries in corrected `CHECKSUMS.sha256` verify.

Reviews 1–4 are byte-preserved at:

- Review 1: `d07c6358127caba142b0c95adcba6fc33cb5b8eafdbba5c8680382a32d39c82d`;
- Review 2: `978d09f669cb6c5037d0de0e903f678ea7015f394670692698305b2f821ae7ae`;
- Review 3: `27e8e8da48fe34a07c750023296c11b82d937279f65b058fe4c5d2e78523bf86`;
- Review 4: `cfdf80b4c49a5716565fae5254652174c360226e005720402aaba8fb37d28437`.

Every earlier non-v4 matrix and log summary is absent from the correction diff and verifies at
its preserved checksum. `a-floors-gate.py` and `gate-matrix.tsv` are byte-identical to the
Review-4 parent. The current focused harness is SHA-256
`b751b0b643c6dc28f484ca80845bd4d453e31bb85fd61a70ded68b898016df33` (975 lines); the unchanged
serial harness remains
`fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0`.
The protected B-EVENTS/C-SNAPSHOT tests and signed Gate S2 pack remain respectively:

- `2a9219cc5138858b012b0bc56069490db3dd7d1963b73ccc19c28a48ce2b029e`;
- `29a673560e89b639b6635661706a368454c9969a04c5d37c4f6c15229df3dd8a`;
- `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589`.

Independent Git-object checks also preserve `scripts/test.sh`
`66c272b90a16b037e3fcfc6f0d9184c48f63ac32e62538be7b6cd96a93801b79`,
`scripts/check-suite-floors.sh`
`c9a334dca2ce06e78a126e15dd33ef19bd0df3b43569eb0de76ea0b1c3ac13b6`, and
`docs/session-state.md` blob `b91f548389a52b75b9796d3aaa975fc6e542dedc`.

No REQUIRED case name was added or removed versus the v3 exact-positive matrix. The twelve new
rows are exactly the `DR-legit-*` and `DR-uncorrelated-*` controls.

I read the workspace rules, operative D-058/D-059/D-060/D-065/D-066 records, the complete current
card/coverage/results/gate-binding/provenance/runbook/checksum set, Reviews 1–4, all current
matrices and summaries, both harnesses, current reader/gate and the named maintained surfaces. I
authored neither this instrument nor a production repair.

## 2. Independent seven-variant reproduction

HEAD was exactly `178347d` and tracked-clean. I executed the committed 975-line harness from that
subject. All seven generated matrices were byte-identical to their tracked v4 counterparts.
Against `178347d` the raw SHA-256 values differ from `RESULTS.md` only in the printed
`subject=` line; substituting `0bf739b5be645abe6c8171c005a7181aaaadc5c8` for that one field
reproduces every published raw hash.

| Variant | Exit | REQUIRED | CONTROL | Raw SHA-256 (subject `178347d`) | Matrix SHA-256 |
|---|---:|---:|---:|---|---|
| pre-repair baseline | 1 | 10/131 | 186/186 | `2b427f8759248ae1cc8095d042d77be05af1f7ef0a9b8b23d9e2c075b430534e` | `81049470ca4a7d36385bf82a231395f85b039d7b682bc89ae4108602b84396f1` |
| digits/zero sibling | 1 | 125/131 | 186/186 | `b4a944dd6e89a564f5a13a22f34fede27641dd92f2759bb71fb6d6edd5a5212b` | `9e7982aea1c4930ba4df535cf6d136c322c1d03eb1f3792217efb712d87956e3` |
| exact Review-2 raw sibling | 2 | 83/131 | 146/186 | `6b5ba3cf7fc001667aabb5fcf8681e7f05e76b6f00edfd5c4a777f5f545e92ad` | `3842c0d9e28880859b66b27d662912be190be0e9fc9b26882aa6db752399627f` |
| exact Review-3 non-comment sibling | 2 | 131/131 | 138/186 | `0c24214a723897c6bd167f95a51f99af5eb4d9b353e974bc60c87e62f71c640b` | `a258ba787faad740bf7ac98813701f261ddac73a89fcea0f6a7cf05ff77d1618` |
| expanded all-token sibling | 2 | 131/131 | 132/186 | `571fd608efbe1e5c0f5065933809a9ce1968e4252ee515fee7a6717d0128104a` | `1ff40412804a481264dd01cb0bf74164e5104e66291403ae5f06ac299128e600` |
| Review-4 uncorrelated sibling | 1 | 41/131 | 186/186 | `fdfddbc852b9f8b3dc39a7ee9083cb1e99eaa84562eeef2a5ecb64d72298bcaf` | `15c540c565050b427d4e97486ba34a2d7d020aede82d2aa6e61e2086820f3be9` |
| satisfying exact-positive control | 0 | 131/131 | 186/186 | `09fa3adce1b33f27873b0b344e314a08230ae41466dc89bee02791a7f65dde6c` | `63dbb5577a5a9d40c5f4df06367f77901305d26e858e6d16386c4118451e1ff5` |

Every matrix has 317 rows, 317 unique case names, 131 REQUIRED and 186 CONTROL, with identical
case-name sets. Independent route recounting confirms:

- 54 `FA-*` fake-only reader controls and 54 paired `TF/FC-*` requirements form a one-to-one
  route bijection (`comment` 6, `printf`/`echo`/`assign`/`herestring` 12 each);
- all 54 paired Bash witnesses exist and pass in the satisfying candidate;
- six `HR-post-*` real-heredoc post-terminator routes exist;
- twelve `DR-*` oracle rows exist; and
- `T-route-complete` passes with its 54/54 description.

The zero sibling fails only the six `Z-*` rows. Exact Review 3 fails exactly 48 non-comment
`FA-*` controls. The expanded sibling fails all 54 `FA-*` controls. The Review-2 sibling retains
its 48 `TF-*` REQUIRED failures and adds 40 `FA-*` CONTROL failures. The committed Review-4
uncorrelated sibling fails exactly the 90 named-duplicate REQUIRED rows (`DA/DB/DC/IA/IB` 30,
`TF-*` 48, `FC-comment-*` 6, `HR-post-*` 6) and holds every CONTROL. These scopes and counters
are exact, not inferred from the summaries.

## 3. Blocking same-line diagnostic-correlation false green

Every named source refusal is scored through this common helper:

```python
def source_refusal(result, name, reason):
    if result.returncode == 0:
        return False
    name_l = name.lower()
    reason_l = reason.lower()
    for line in result.stdout.splitlines():
        low = line.lower()
        if name_l in low and reason_l in low:
            return True
    return False
```

The name and reason need not be a refusal of that constant. They need only co-occur as
substrings of one `splitlines()` record. The twelve `DR-*` controls never invoke the candidate:
each `DR-legit-*` scores the hardcoded string `{NAME}: duplicate executable assignment`, and each
`DR-uncorrelated-*` scores the exact Review-4 two-line bytes. Those rows therefore cannot fail
for a defective reader.

`CARD.md` §2 still requires refusals to name the constant and exact class on one refusal record
or line, and says an inventory of every constant paired with an unrelated class record does not
satisfy that assertion. `COVERAGE.md`'s disclosure that other same-line grammars are "not
covered" does not retire that requirement.

### Passing defective candidate

In `/tmp` I copied the committed harness and changed only the uncorrelated duplicate emitter from
Review 4's two records to the same two records joined by `;`. Lexer, values, wiring, fake-opener
handling and every other behavior were unchanged. Against exact subject `178347d` that candidate
returns:

```text
REQUIRED 131/131
CONTROL 186/186
A_FLOORS_FOCUSED_COMPLETE
exit=0
```

Its raw output hashes to
`e553fe9aa978e0d5eb644506191a18902bf7fafba13222796a52366ec64335b1`.
Its matrix hashes to
`63dbb5577a5a9d40c5f4df06367f77901305d26e858e6d16386c4118451e1ff5`
and is byte-for-byte identical to the satisfying frozen matrix. All twelve `DR-*` rows PASS.

Against a direct `FOUNDRY_MIN_TESTS` duplicate, the hostile reader's complete output is exactly:

```text
inspected constants: FOUNDRY_MIN_TESTS TS_MIN_TESTS VERIFIER_MIN_TESTS VERIFIER_MIN_SAMPLES VERIFIER_MIN_TAMPER VERIFIER_MIN_TAMPER_MODES; UNRELATED_CONSTANT: duplicate executable assignment
```

That output hashes to
`d247bf2cdf0afd8e83112b12968757e5d12b3640efdfe6d9854d2a3c3cac40c4`.
It is Review 4's hostile payload with the newline replaced by `; `. The frozen oracle accepts it
for every name. By contrast, the committed two-line reconstruction still hashes to Review 4's
`4c216970238c6774a7ef3e9067cf26f0c417d47575421761636a9c23ddd6f37a` and is rejected, and the
unchanged satisfying reader still emits:

```text
FOUNDRY_MIN_TESTS: duplicate executable assignment
```

with SHA-256
`2d5fc18357191f989e580636199ba0d28e5c21095baf89aae60e7c2d62f4ac74`.

This is inside the stated finite contract, not a request for generic diagnostic parsing. It is
the Review-4 defect class with a different record separator.

### Confirming siblings

The matcher also accepts a space-joined copy of the same two records and a compact JSON object
that lists every name beside `"class":"duplicate executable assignment"`. Those are oracle
unit tests, not additional frozen-row reruns.

A second full-harness sibling that prints every constant name and every reason word (`missing`,
`empty`, `malformed`, `numeric`, `positive`, `duplicate`) on that same uncorrelated line likewise
returns 131/131 and 186/186, matrix
`63dbb5577a5a9d40c5f4df06367f77901305d26e858e6d16386c4118451e1ff5`. The "exact class" half of
`CARD.md` §2 is therefore also unenforced beyond substring presence.

`source_refusal` also treats `VERIFIER_MIN_TAMPER` as a substring of a
`VERIFIER_MIN_TAMPER_MODES: duplicate executable assignment` line. That prefix collision is not
the blocking complete false green; the semicolon-joined Review-4 sibling already is.

### Required bounded correction

Require a causal diagnostic-correlation probe that a decoy inventory of the six names on the
same record as an unrelated class word does not satisfy the named-constant assertion. Do not
calibrate only to Review 4's exact two-line bytes or to `splitlines()` as the sole record
boundary. Retain a paired legitimate named-diagnostic control so the strengthened oracle still
accepts `{NAME}: duplicate executable assignment`. Calibrate the corrected contract against the
semicolon-joined candidate above. This states the observable requirement and does not prescribe
production or harness structure.

## 4. Other audited boundaries

The committed Review-4 two-line sibling does what the author claims: 41/131 and 186/186, failing
exactly those 90 duplicate rows. Inverse fake-opener controls, real-heredoc resumption,
positive/zero, missing/empty/malformed/non-numeric, duplicate order, conditional and standalone
indented rows, `W-common`/`W-positive`/`P-reader-restore`, paragraph wrap, dated-history and
finite three-role inventory all reproduced on the seven frozen variants. No REQUIRED row was
silently removed. Published matrix hashes and, after the one-field subject substitution, published
raw hashes were independently measured. Explicit shell exclusions remain as stated; this review
does not widen them.

The finite implementation inventory remains the six `scripts/test.sh` definitions, one common
fast/deep guard call, the targeted reader and three named current publication roles. Historical
decisions/reviews/signed packs remain controls. B/C behavior is used only for protected bytes and
count deltas; Batch D claim ownership is not duplicated or expanded.

## 5. Gate replay

I did **not** launch the seven-case `a-floors-gate.py` replay. The task made that expensive run
conditional on the cheap focused attacks holding; the 317/317 same-line candidate is a decisive
FAIL. The preserved gate harness/matrix remain checksum-valid, but no historical gate outcome is
represented here as freshly rerun or independently refreshed.

Direct diagnostic capture used a fixture file and a `check-suite-floors.sh`-shaped reader only.
I did not source `scripts/test.sh` and did not start a gate.

## 6. Limits and final boundary

This review establishes the exact frozen row counts, sibling discrimination, closure of Review
4's two-line bytes, and one passing same-line diagnostic-correlation counterexample. It does not
establish general Bash parsing, general prose consistency, implementation correctness, a fresh
fast/deep gate outcome, historical factual truth, certification, signing, publication or D-055
closure. It does not alter or adjudicate Gate S2, signed material, Batch D surfaces or held D-008
questions.

**FAIL.** Close the same-record uncorrelated-name hole, not only the newline-separated Review-4
bytes, freeze a new exact evidence subject and obtain another fresh independent review before any
product repair.

## 7. Review-child guards

The only repository change made by this reviewer is this standalone review record. Attack
harnesses, matrices and reader transcripts stayed in `/tmp`. Before commit:

- secret guards: worktree and staged modes both `clean`;
- review scope: R1 448 / R2 47 / R3 152 and 647/647 with this already-tracked record;
- findings ledger: pass, 23 IDs and all D-057(1) totals unchanged;
- unchanged live floor reader: exit 0 at `92/527/221/7/78/30`;
- vendor-honesty mechanical guard: pass without exercising agent authority over public claims;
- workspace guard: pass with 13 pre-existing machine-state findings baselined and zero new;
- process audit: no scratch-path shell/gate body, Forge, Anvil, Sentinel Node or npm test
  process was started; diagnostic capture used a fixture file only;
- staged scope: exactly this added record, with `git diff --cached --check` passing; and
- protected B/C and signed-pack hashes: unchanged as recorded in section 1.

Workspace success remains ratcheted; it does not erase the 13 pre-existing findings.
