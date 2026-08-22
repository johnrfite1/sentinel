# A-FLOORS — fresh independent fourth-corrected instrument review 5

## Verdict

**FAIL for instrument readiness.** The fourth correction closes Review 4's named two-line
split: `source_refusal` now requires the mutated name and reason word on one `splitlines()`
record, the twelve `DR-*` controls reject that exact inventory-plus-unrelated payload, and the
live `uncorrelated-diagnostic-sibling` fails exactly the 90 named-duplicate REQUIRED rows. The
oracle still treats any single line that contains both substrings as a named refusal. Joining
Review 4's two records with a space, or emitting the same decoy names inside a JSON object that
also carries `duplicate executable assignment`, scores **131/131 REQUIRED and 186/186 CONTROL**,
exit 0, and produces a matrix byte-identical to the satisfying exact-positive control. That
reader does not name the mutated constant as the subject of the refusal, which `CARD.md` §2
requires. The twelve new `DR-*` rows cannot catch it: they score hardcoded strings inside the
harness, not the candidate.

This is an instrument-readiness verdict only. It is not an implementation verdict, gate approval
or signature, certification, ratification, publication, rename, D-055 assessment, D-008 action
or push authorization.

## 1. Exact subject, scope and preservation

I reviewed exact subject `178347dbf33ab70923a6fd0278ea61c5dec5e6b6`, tree
`1b5f028aa217da5e389c28a062d43b5350c60d96`, whose sole parent is Review-4 FAIL
`0bf739b5be645abe6c8171c005a7181aaaadc5c8` (tree `2b7265c78e549ba290f0ec2c138c7bc5718b7fcf`).

The parent-to-subject correction contains exactly 23 paths, all beneath this
`A-FLOORS-tests/` evidence directory: nine modified evidence/harness files and fourteen added
v4 matrices/summaries, with 2,627 insertions and 145 deletions. It changes no production byte,
existing product test/script, live gate, maintained claim, decision record, signed material or
prior review. `git diff --check` passes. All 57 entries in corrected `CHECKSUMS.sha256` verify.
The working tree was clean at this subject except for the later addition of this standalone
review record.

Reviews 1–4 are byte-preserved at:

- Review 1: `d07c6358127caba142b0c95adcba6fc33cb5b8eafdbba5c8680382a32d39c82d`;
- Review 2: `978d09f669cb6c5037d0de0e903f678ea7015f394670692698305b2f821ae7ae`;
- Review 3: `27e8e8da48fe34a07c750023296c11b82d937279f65b058fe4c5d2e78523bf86`;
- Review 4: `cfdf80b4c49a5716565fae5254652174c360226e005720402aaba8fb37d28437`.

Every earlier non-v4 matrix and log summary is absent from the correction diff and verifies at
its preserved checksum. The current focused harness is SHA-256
`b751b0b643c6dc28f484ca80845bd4d453e31bb85fd61a70ded68b898016df33` (975 lines);
the unchanged serial harness remains
`fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0`.
`gate-matrix.tsv` remains
`0b4d9c127e7230c7266960fe073f92f9551da9a68005cb936850993d803d1c58`.
Independent Git-object checks also preserve `scripts/test.sh`
`66c272b90a16b037e3fcfc6f0d9184c48f63ac32e62538be7b6cd96a93801b79`,
`scripts/check-suite-floors.sh`
`c9a334dca2ce06e78a126e15dd33ef19bd0df3b43569eb0de76ea0b1c3ac13b6`, and
`docs/session-state.md` blob `b91f548389a52b75b9796d3aaa975fc6e542dedc`.
The protected B-EVENTS/C-SNAPSHOT tests and signed Gate S2 pack remain respectively:

- `2a9219cc5138858b012b0bc56069490db3dd7d1963b73ccc19c28a48ce2b029e`;
- `29a673560e89b639b6635661706a368454c9969a04c5d37c4f6c15229df3dd8a`;
- `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589`.

No v3 REQUIRED or CONTROL case was removed or relabelled: exact-positive v4 keeps all 305 prior
rows at the same kind and status and adds only the twelve `DR-*` controls (317 unique names;
131 REQUIRED, 186 CONTROL).

I read the workspace rules, operative D-058/D-059/D-060/D-065/D-066 records, the complete
current card/coverage/results/gate-binding/provenance/runbook/checksum set, Reviews 1–4, all
current matrices and summaries, both harnesses, current reader/gate and the named maintained
surfaces. I authored neither this instrument nor any production repair.

## 2. Independent seven-variant reproduction

HEAD was exactly `178347d` and tracked-clean. I executed that commit's `a-floors.py` against a
disposable clone of the same subject. All seven generated matrices were byte-identical to their
tracked v4 counterparts. Independent raw hashes below are for subject `178347d`. Substituting
the author-used subject `0bf739b` into those raw logs reproduces every RESULTS.md raw hash;
the matrices do not carry the subject identity and already matched without substitution.

| Variant | Exit | REQUIRED | CONTROL | Raw SHA-256 | Matrix SHA-256 |
|---|---:|---:|---:|---|---|
| pre-repair baseline | 1 | 10/131 | 186/186 | `2b427f8759248ae1cc8095d042d77be05af1f7ef0a9b8b23d9e2c075b430534e` | `81049470ca4a7d36385bf82a231395f85b039d7b682bc89ae4108602b84396f1` |
| digits/zero sibling | 1 | 125/131 | 186/186 | `b4a944dd6e89a564f5a13a22f34fede27641dd92f2759bb71fb6d6edd5a5212b` | `9e7982aea1c4930ba4df535cf6d136c322c1d03eb1f3792217efb712d87956e3` |
| exact Review-2 raw sibling | 2 | 83/131 | 146/186 | `6b5ba3cf7fc001667aabb5fcf8681e7f05e76b6f00edfd5c4a777f5f545e92ad` | `3842c0d9e28880859b66b27d662912be190be0e9fc9b26882aa6db752399627f` |
| exact Review-3 non-comment sibling | 2 | 131/131 | 138/186 | `0c24214a723897c6bd167f95a51f99af5eb4d9b353e974bc60c87e62f71c640b` | `a258ba787faad740bf7ac98813701f261ddac73a89fcea0f6a7cf05ff77d1618` |
| expanded all-token sibling | 2 | 131/131 | 132/186 | `571fd608efbe1e5c0f5065933809a9ce1968e4252ee515fee7a6717d0128104a` | `1ff40412804a481264dd01cb0bf74164e5104e66291403ae5f06ac299128e600` |
| satisfying exact-positive control | 0 | 131/131 | 186/186 | `09fa3adce1b33f27873b0b344e314a08230ae41466dc89bee02791a7f65dde6c` | `63dbb5577a5a9d40c5f4df06367f77901305d26e858e6d16386c4118451e1ff5` |
| Review-4 uncorrelated-diagnostic sibling | 1 | 41/131 | 186/186 | `fdfddbc852b9f8b3dc39a7ee9083cb1e99eaa84562eeef2a5ecb64d72298bcaf` | `15c540c565050b427d4e97486ba34a2d7d020aede82d2aa6e61e2086820f3be9` |

Every matrix has 317 rows, 317 unique case names, 131 REQUIRED and 186 CONTROL, with identical
case-name sets. Independent route recounting confirms:

- 54 `FA-*` fake-only reader controls and 54 paired `TF/FC-*` requirements form a one-to-one
  route bijection (`comment` 6; `printf`/`echo`/`assign`/`herestring` 12 each);
- all 54 paired Bash witnesses exist and pass in the satisfying candidate;
- six `HR-post-*` real-heredoc post-terminator routes exist;
- twelve `DR-*` oracle rows exist; and
- `T-route-complete` passes with its 54/54 description.

The zero sibling fails only the six `Z-*` rows. Exact Review 3 fails exactly 48 non-comment
`FA-*` controls. The expanded sibling fails all 54 `FA-*` controls. The Review-2 sibling retains
its 48 `TF-*` REQUIRED failures and adds 40 `FA-*` CONTROL failures. The committed Review-4
uncorrelated sibling fails exactly the 90 named-duplicate REQUIRED rows (`DA/DB/DC/IA/IB` 30,
`TF-*` 48, `FC-comment-*` 6, `HR-post-*` 6) and holds every CONTROL. These scopes and counters
are from the reproduced matrices, not from RESULTS.md.

## 3. Blocking diagnostic-correlation false green

Review 4's two-line payload is now rejected by the frozen matcher, and the live two-line sibling
does not go fully green. The remaining helper is still:

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

Name and reason need only co-occur as substrings of one `splitlines()` record. They need not
be a refusal of that constant. `DR-uncorrelated-*` tests a synthetic two-line string, not
candidate output. `DR-legit-*` scores the hardcoded string `{NAME}: duplicate executable
assignment`. Those twelve rows therefore cannot fail for a defective reader. The only live
candidate bound to Review 4's grammar is `uncorrelated-diagnostic-sibling`. No frozen row
rejects a one-line concatenation of the same two records, or another one-line grammar that
lists every constant beside the class.

`CARD.md` §2 still requires refusals to name the constant and exact class on one refusal record
or line, and says an inventory of every constant paired with an unrelated class record does not
satisfy that assertion. `COVERAGE.md`'s disclosure that other same-line grammars are "not
covered" does not retire that requirement or move it out of D-065.

### Passing defective candidates

In a throwaway copy of the committed 975-line harness I added only two diagnostic modes to the
existing exact-positive finite lexer (`[1-9][0-9]*`, finite opener handling, named missing/empty/
malformed/numeric messages unchanged). Duplicate emission became either:

1. one line: Review 4's inventory plus `UNRELATED_CONSTANT: duplicate executable assignment`;
2. one JSON object whose `inspected` array lists all six names and whose `class` member is
   `duplicate executable assignment`.

Against exact subject `178347d` both return:

```text
REQUIRED 131/131
CONTROL 186/186
A_FLOORS_FOCUSED_COMPLETE
exit=0
```

Both matrices hash to
`63dbb5577a5a9d40c5f4df06367f77901305d26e858e6d16386c4118451e1ff5`
and are byte-for-byte identical to the satisfying frozen matrix. All twelve `DR-*` rows PASS.
Raw hashes:

- oneline sibling: `71ae4d1d48de9a43ee2d66147a2fff155bdf85e9edaa9166d9a140473ccbb9de`;
- JSON sibling: `bec8c8d3d1e0ac3e5d0db4372bc449cf64ba83f916dfb5c18ae6211cc7803c67`.

A direct `FOUNDRY_MIN_TESTS` duplicate under the oneline policy emits exactly:

```text
inspected constants: FOUNDRY_MIN_TESTS TS_MIN_TESTS VERIFIER_MIN_TESTS VERIFIER_MIN_SAMPLES VERIFIER_MIN_TAMPER VERIFIER_MIN_TAMPER_MODES UNRELATED_CONSTANT: duplicate executable assignment
```

That output hashes to
`518a78edb86ab2332eb47b70ddea9cf11f04c2ef49b5226893df0d97ad4a6eab`.
The JSON sibling's corresponding record hashes to
`40a7c7771c2111886e5291b7b8c267c7c7f41648b4ab9f5f7cfcf575f1a8ab44`.
Each contains every target and the reason on one line, so every duplicate `source_refusal` row
accepts it. The grammatical subject of the refusal is still `UNRELATED_CONSTANT` (or a JSON
`class` field), not the mutated constant. The committed two-line reconstruction still hashes to
Review 4's `4c216970238c6774a7ef3e9067cf26f0c417d47575421761636a9c23ddd6f37a` and is rejected.
The unchanged satisfying reader emits:

```text
FOUNDRY_MIN_TESTS: duplicate executable assignment
```

with SHA-256
`2d5fc18357191f989e580636199ba0d28e5c21095baf89aae60e7c2d62f4ac74`.
A matcher that requires the field before `:` to be exactly the mutated name rejects both hostile
payloads and the Review-4 split, and accepts this control.

This is inside the stated finite diagnostic-correlation contract, not a request for generic
Bash parsing and not a caller-controlled git-environment attack. It is the Review-4 defect
class with a different record separator.

The substring matcher has a second, non-full-green weakness: a line
`VERIFIER_MIN_TAMPER_MODES: duplicate executable assignment` satisfies
`source_refusal(..., "VERIFIER_MIN_TAMPER", "duplicate")` because the shorter name is a prefix
of the longer one. That candidate cannot green the other four constants; it is recorded as
residual matcher shape, not a second independent FAIL.

### Required bounded correction

Require the mutated constant to be the named subject of the refusal record, not merely
co-present with the class token on any one line. Decoy inventory or JSON payloads that list
every name alongside an unrelated class must fail. Do not calibrate only to Review 4's exact
two-line bytes or to `splitlines()` as the sole record boundary. Calibrate against the two
full-green candidates above as well as Review 4's two-line split. Keep a paired legitimate
`{NAME}: duplicate executable assignment` control. Bind each rejected grammar to a live
candidate sibling, not only to a synthetic matcher string. Close the
`VERIFIER_MIN_TAMPER` / `VERIFIER_MIN_TAMPER_MODES` prefix collision in the same subject
match. This states the observable requirement and does not prescribe production or harness
structure.

## 4. Other audited boundaries

The committed Review-4 two-line sibling does what the author claims: 41/131 and 186/186, failing
exactly those 90 duplicate rows. Inverse fake-opener controls, real-heredoc resumption,
positive/zero, missing/empty/malformed/non-numeric, duplicate order, conditional and standalone
indented rows, `W-common`/`W-positive`/`P-reader-restore`, paragraph wrap, dated-history and
finite three-role inventory all reproduced on the seven frozen variants. No REQUIRED row was
silently removed. Published matrix hashes and, after the one-field subject substitution,
published raw hashes were independently measured. Explicit shell exclusions remain as stated;
this review does not widen them.

The finite implementation inventory remains the six `scripts/test.sh` definitions, one common
fast/deep guard call, the targeted reader and three named current publication roles. Historical
decisions/reviews/signed packs remain controls. B/C behavior is used only for protected bytes
and count deltas; Batch D claim ownership is not duplicated or expanded.

## 5. Gate replay

I did **not** launch the seven-case `a-floors-gate.py` replay. The task made that expensive run
conditional on the cheap focused attacks holding; the 317/317 oneline and JSON candidates are a
decisive FAIL. The preserved gate harness/matrix remain checksum-valid, but no historical gate
outcome is represented here as freshly rerun or independently refreshed.

Direct diagnostic capture used a fixture file and a `check-suite-floors.sh`-shaped reader only.
I did not source `scripts/test.sh` and did not start a gate.

## 6. Limits and final boundary

This review establishes the exact frozen row counts, sibling discrimination, closure of Review
4's two-line payload, and two passing one-line diagnostic-correlation counterexamples. It does
not establish general Bash parsing, general prose consistency, implementation correctness, a
fresh fast/deep gate outcome, historical factual truth, certification, signing, publication or
D-055 closure. It does not alter or adjudicate Gate S2, signed material, Batch D surfaces or
held D-008 questions.

**FAIL.** Close the same-record uncorrelated-name hole, not only the newline-separated Review-4
bytes, freeze a new exact evidence subject and obtain another fresh independent review before
any product repair.

## 7. Review-child guards

The only repository change made by this reviewer is this standalone review record. Attack
harnesses, matrices and reader transcripts stayed outside the repository. Before commit:

- secret guards: worktree and staged modes both `clean`;
- review scope: R1 447 / R2 47 / R3 152 and 646/646 before staging; R1 448 / R2 47 /
  R3 152 and 647/647 after staging;
- findings ledger: pass, 23 IDs and all D-057(1) totals unchanged;
- unchanged live floor reader: exit 0 at `92/527/221/7/78/30`;
- vendor-honesty mechanical guard: pass without exercising agent authority over public claims;
- workspace guard: pass with 13 pre-existing machine-state findings baselined and zero new;
- process audit: no scratch-path shell/gate body, Forge, Anvil, Sentinel Node or npm test
  process was started; diagnostic capture used a fixture file only;
- staged scope: exactly this added record, with `git diff --cached --check` passing; and
- protected B/C and signed-pack hashes: unchanged as recorded in section 1.

Workspace success remains ratcheted; it does not erase the 13 pre-existing findings.
