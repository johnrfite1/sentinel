# A-FLOORS — fresh independent sixth-corrected instrument review 7

## Verdict

**FAIL for instrument readiness.** The sixth correction closes Review 6's exact frozen
spellings: pretty-printed unquoted name-as-key JSON whose wrapper records are exactly `{` and
`}`, and a same-record decoy inventory after `{NAME}:`. The committed pretty-JSON and inventory
siblings fail exactly the 90 named-duplicate REQUIRED rows, hold every CONTROL, and share one
matrix distinct from the satisfying control. Exact class-phrase matching rejects a kitchen-sink
of class words. The unique-subject rule is implemented as membership of a stripped record that
is exactly `{` or `}`. Pretty-printing the same unquoted name-as-key object with comments on
those wrapper lines returns **131/131 REQUIRED and 212/212 CONTROL**, exit 0, and a matrix
byte-identical to the satisfying exact-positive control. Inner records are the Review-6 payload;
the mutated constant is still not a unique subject. `DR-prettyjson-*` never invokes the
candidate, so that live reader still greens every diagnostic-oracle row.

This is an instrument-readiness verdict only. It is not an implementation verdict, gate approval
or signature, certification, ratification, publication, rename, D-055 assessment, D-008 action
or push authorization.

## 1. Exact subject, scope and preservation

I reviewed exact subject `f0e0a9f1a12a5593e1d32aed9e207c3ab2b51fe3`, tree
`95b3e78f549537c90173d8de3c46237fe6b1672d`, whose sole parent is Review-6 FAIL
`b4553841e4d234b947c008f340dce4f6a1a28b02` (tree `2b76ab1a4f45cd6b84ecec8bce352b4f86c006d8`).
HEAD was exactly that subject and tracked-clean before this review file existed.

The parent-to-subject correction contains exactly 31 paths, all beneath this `A-FLOORS-tests/`
evidence directory: eight modified evidence/harness files, `logs/README.md`, and twenty-two added
v6 matrices/summaries, with 4,285 insertions and 306 deletions. It changes no production byte,
existing product test/script, live gate, maintained claim, decision record, signed material or
prior review. `git diff --check` passes. Every entry in corrected `CHECKSUMS.sha256` verifies.

Reviews 1–6 and the concurrent Review-5 blob are byte-preserved at:

- Review 1: `d07c6358127caba142b0c95adcba6fc33cb5b8eafdbba5c8680382a32d39c82d`;
- Review 2: `978d09f669cb6c5037d0de0e903f678ea7015f394670692698305b2f821ae7ae`;
- Review 3: `27e8e8da48fe34a07c750023296c11b82d937279f65b058fe4c5d2e78523bf86`;
- Review 4: `cfdf80b4c49a5716565fae5254652174c360226e005720402aaba8fb37d28437`;
- Review 5 of record: `4d742aded60fce42d30ec49dbb4d7a443fe0f0dbfc04ab9cafcc06987c4bd6fa`;
- concurrent Review 5: `10bc8231f5d9e3f309a3bf87190d1340f60176c8fdc1644bb1bf8bd2e585dbb7`;
- Review 6: `a807603684afc76f93929d662be111e1438d7578a7be3dbcdb4d9d7ef40ac3f4`.

Every earlier non-v6 matrix and log summary is absent from the correction diff and verifies at
its preserved checksum. `a-floors-gate.py` and `gate-matrix.tsv` are byte-identical to the
Review-6 parent. The current focused harness is SHA-256
`1c298341fb807b54fa15e1e95f4084db5b9ce4881bb52099f5499e0811b8c93c` (1116 lines); the unchanged
serial harness remains
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

No REQUIRED case name was added or removed versus the v5 exact-positive matrix. The twelve new
rows are exactly the six `DR-prettyjson-*` and six `DR-inventory-*` controls (343 unique names;
131 REQUIRED, 212 CONTROL). Live floors at this subject remain `92/527/221/7/78/30`.

I read the workspace rules, the complete current card/coverage/results/gate-binding/provenance/
runbook/checksum set, Reviews 1–6, the concurrent Review-5 blob, current v6 matrices and
summaries, both harnesses, current reader/gate and the named maintained surfaces. I authored
neither this instrument nor a production repair.

## 2. Independent eleven-variant reproduction

HEAD was exactly `f0e0a9f` and tracked-clean. The committed 1116-line harness refuses a dirty
source worktree, so I executed it from a disposable clean clone of `f0e0a9f` against subject
`f0e0a9f`. All eleven generated matrices were byte-identical to their tracked v6 counterparts.
Against `f0e0a9f` the raw SHA-256 values differ from `RESULTS.md` only in the printed
`subject=` line; `RESULTS.md` used clone identity `b455384`. Substituting
`b4553841e4d234b947c008f340dce4f6a1a28b02` for that one field reproduces every published raw
hash.

| Variant | Exit | REQUIRED | CONTROL | Raw SHA-256 (subject `f0e0a9f`) | Matrix SHA-256 |
|---|---:|---:|---:|---|---|
| pre-repair baseline | 1 | 4/131 | 212/212 | `3406737a7f47f77298c93b812c588e1167fc462be9f854889d959bf1ae79f52d` | `74500e901beeb34a9916ee44d7a890b2ca75370f960d41933f27fffc660dd724` |
| digits/zero sibling | 1 | 125/131 | 212/212 | `65fabcf19ded5d23253ad9fec1c54191ed6369d2d7d2a9aa2e6e6b1b7d4d8f2f` | `e3b72a952470a051d0650abf5e6b71ee441f36e191954e7f37c0e38747fc856f` |
| exact Review-2 raw sibling | 2 | 83/131 | 172/212 | `52c8636b3609f5d04035c1e70c2aada547cbeb3665c62db93743d8e47c0fb7b5` | `2ac06deb1121d39b3eb2cbdf19443a1313f2f7b21738bf217e7b3c91ce2b80cd` |
| exact Review-3 non-comment sibling | 2 | 131/131 | 164/212 | `b2ccfc11e09a6ea03063e412a5bfe7eb4aa6cdd7182d98efa41830f0197ba1f4` | `4451ccdadb92467c78811408188b4f7e7eafae3eaab593db7bb3de272b73f6dc` |
| expanded all-token sibling | 2 | 131/131 | 158/212 | `c39fcba9dd4a359cd7fe745671f1dd3a4eb22a534a0ac10fa9449d177b0c238f` | `b09209d81d4b3fe032ab1de6bb3261d608c6964e00ec501d77baa01a9c46b7c4` |
| Review-4 two-line uncorrelated sibling | 1 | 41/131 | 212/212 | `b67b4be2c0c51604fa292bc359bb1a3c11b7eec96726b0221b310f11c94bbf56` | `37329860d7787ea0ee5edda3f30bd4b7d0064353d24b175b5a6e4730ebe8e1c8` |
| Review-5 oneline uncorrelated sibling | 1 | 41/131 | 212/212 | `240fd91c88084b450bf922d587596ca01d94304fd0fdb7a8f3fb8ad3f32d1566` | `37329860d7787ea0ee5edda3f30bd4b7d0064353d24b175b5a6e4730ebe8e1c8` |
| compact JSON uncorrelated sibling | 1 | 41/131 | 212/212 | `8d16de084142b15fe69d640f1c272e922d1ff61d035a81249f5550988bfb700d` | `37329860d7787ea0ee5edda3f30bd4b7d0064353d24b175b5a6e4730ebe8e1c8` |
| Review-6 pretty JSON uncorrelated sibling | 1 | 41/131 | 212/212 | `0a517771c936f76473b7bf8ff7645f7b7a6f0db2abb3a981bab656149f7a43c2` | `37329860d7787ea0ee5edda3f30bd4b7d0064353d24b175b5a6e4730ebe8e1c8` |
| same-record inventory uncorrelated sibling | 1 | 41/131 | 212/212 | `90f0536d5577b2c705e5627f87ca9c7df4e1d508f48589795c22be004af359a0` | `37329860d7787ea0ee5edda3f30bd4b7d0064353d24b175b5a6e4730ebe8e1c8` |
| satisfying exact-positive control | 0 | 131/131 | 212/212 | `c078add3972dd705f5f1f71f21f5b3d51031e025c9f53e42ce2ee5956d302654` | `7f3ddf691b9619669ed221c94b1f0ab58e581a1db2086727772043afeadabfa1` |

Every matrix has 343 rows, 343 unique case names, 131 REQUIRED and 212 CONTROL, with identical
case-name sets. Independent route recounting confirms:

- 54 `FA-*` fake-only reader controls and 54 paired `TF/FC-*` requirements form a one-to-one
  route bijection (`comment` 6, `printf`/`echo`/`assign`/`herestring` 12 each);
- all 54 paired Bash witnesses exist and pass in the satisfying candidate;
- six `HR-post-*` real-heredoc post-terminator routes exist;
- thirty-eight `DR-*` oracle rows exist (six each of legit / two-line / oneline / compact JSON /
  pretty JSON / inventory, plus the TAMPER prefix pair); and
- `T-route-complete` passes with its 54/54 description.

The zero sibling fails only the six `Z-*` rows. Exact Review 3 fails exactly 48 non-comment
`FA-*` controls. The expanded sibling fails all 54 `FA-*` controls. The Review-2 sibling retains
its 48 `TF-*` REQUIRED failures and adds 40 `FA-*` CONTROL failures. Each committed uncorrelated
sibling fails exactly the 90 named-duplicate REQUIRED rows (`DA/DB/DC/IA/IB` 30, `TF-*` 48,
`FC-comment-*` 6, `HR-post-*` 6) and holds every CONTROL. The five uncorrelated matrices are
byte-identical to each other and distinct from the satisfying control. These scopes and counters
are from the reproduced matrices, not from `RESULTS.md`.

## 3. Blocking pretty-printed JSON whose wrapper records are not exactly `{` / `}`

Named source refusals are now scored through exact class phrases, a remainder name-scan, and a
wrapper check:

```python
json_wrapped = "{" in records or "}" in records
matching = [
    remainder for subject, remainder in hits
    if subject == name and class_remainder(remainder) == phrase
]
if json_wrapped and any(
    subject != name and class_remainder(remainder) == phrase
    for subject, remainder in hits
):
    return False
```

`class_remainder` lowercases, strips, and strips a trailing comma, then requires equality with
`duplicate executable assignment`. Unique-subject rejection fires only when a stripped record is
exactly `{` or `}`. `DR-prettyjson-*` tests only Review 6's exact payload (hash
`3e6a9aa2cfedcedf1fea11682fb9252e4f6cd321dc25bcbb4cad73e66e0fbaea`). `DR-inventory-*` tests only
`{NAME}: duplicate executable assignment` plus the six names on that same record. Those rows
never invoke the candidate.

`CARD.md` §2 still says a pretty-printed `{` / `}` name-as-key object that lists every constant
as the same class is not a unique-subject refusal. The committed pretty-JSON sibling now rejects
the exact Review-6 spelling because `{` and `}` are their own records. That is not the same as
rejecting the object.

### Passing defective candidate

In `/tmp` I copied the committed 1116-line harness and changed only the pretty-JSON duplicate
emitter so the wrapper lines were `{ // object` and `} // end`. Lexer, values, wiring,
fake-opener handling and every other behavior were unchanged. Against exact subject `f0e0a9f`
that candidate returns:

```text
REQUIRED 131/131
CONTROL 212/212
A_FLOORS_FOCUSED_COMPLETE
exit=0
```

Its raw output hashes to
`026128b27c2b81b154dbe59c07b1cf11590ecbe0bacf447c5974c9496ff0d7e2`.
Its matrix hashes to
`7f3ddf691b9619669ed221c94b1f0ab58e581a1db2086727772043afeadabfa1`
and is byte-for-byte identical to the satisfying frozen matrix. All thirty-eight `DR-*` rows
PASS.

Against a direct `FOUNDRY_MIN_TESTS` duplicate, the hostile reader's complete diagnostic is:

```text
{ // object
  FOUNDRY_MIN_TESTS: duplicate executable assignment,
  TS_MIN_TESTS: duplicate executable assignment,
  VERIFIER_MIN_TESTS: duplicate executable assignment,
  VERIFIER_MIN_SAMPLES: duplicate executable assignment,
  VERIFIER_MIN_TAMPER: duplicate executable assignment,
  VERIFIER_MIN_TAMPER_MODES: duplicate executable assignment
} // end
```

That object hashes to
`d8b5d186035fadde9847fe0a8171695bd0ecba7f4d6b23306d03ea6de281bc01`.
The inner six records are Review 6's payload. `strip()` leaves `{ // object` and `} // end`, so
`json_wrapped` is false, and every name matches the exact class phrase with no other floor name
in its remainder. The grammatical wrapper is still a `{` / `}` name-as-key object of every
constant. The mutated constant is not distinguished from its five siblings.

### Review-6 holes that did close

The following live siblings, run as full-harness copies against `f0e0a9f` by changing only the
pretty-JSON emitter, each return 41/131 and 212/212 with matrix
`37329860d7787ea0ee5edda3f30bd4b7d0064353d24b175b5a6e4730ebe8e1c8`, matching the frozen
uncorrelated siblings rather than the satisfying control:

- Review 6's exact pretty-printed unquoted name-as-key object (committed variant; payload
  `3e6a9aa2cfedcedf1fea11682fb9252e4f6cd321dc25bcbb4cad73e66e0fbaea`);
- Review 6's same-record six-name inventory after `{NAME}:` (committed variant);
- quoted pretty JSON (`"NAME": "duplicate executable assignment"`);
- extra whitespace around `{` / `}` and around the colon, still stripping to exact `{` / `}`
  records;
- per-name `{NAME: ...}` wrappers;
- a kitchen-sink of every class phrase after `{NAME}:`.

`source_refusal(..., "VERIFIER_MIN_TAMPER", "duplicate")` remains false for
`VERIFIER_MIN_TAMPER_MODES: duplicate executable assignment` and true for a `TAMPER_MODES`
subject. The six `DR-legit-*` rows still accept `{NAME}: duplicate executable assignment`. A
JSON object that names only the mutated constant as that class still scores as a unique-subject
refusal. Those are the legitimate controls the charter kept.

### Brace-less six-line dump — stated exclusion, not blocking

A brace-less six-line `{NAME}: duplicate executable assignment` dump, with no `{` / `}` wrapper
records, also returns 131/131 and 212/212, matrix
`7f3ddf691b9619669ed221c94b1f0ab58e581a1db2086727772043afeadabfa1`. Payload SHA-256
`2e156ac2f721f2e0768bce951cb170f56d64018cc5abcb033ff2488440a5b0d8`.

`CARD.md` §2 and §8, and `COVERAGE.md`, state this as the Review-3 herestring fail-closed shape
rather than the Review-6 JSON grammar. That distinction is load-bearing: the committed Review-3
sibling scores 131/131 REQUIRED because its fail-closed diagnostic emits exactly this named-
subject dump. I accept that as a stated finite exclusion and do not treat the brace-less dump as
a blocking false green. A JSON array wrapper `[` / `]` of the same inner lines also fully
greens; I read that as the same omitted-curly-wrapper family, not as an independent blocking
hole. The blocking candidate still opens with `{` and closes with `}` around the name-as-key
object.

### Required bounded correction

Require that wrapping every constant as a pretty-printed `{` / `}` name-as-key object of the
same class does not satisfy the named-constant assertion, including when the wrapper lines carry
comments or other non-whitespace so they are not exact one-character `{` / `}` records. Do not
calibrate only to Review 6's exact payload. Bind that rejected grammar to a live candidate
sibling, not only to a synthetic matcher string. Keep the paired legitimate
`{NAME}: duplicate executable assignment` control, and keep the stated Review-3 brace-less
exclusion if that sibling must remain 131/131 REQUIRED. This states the observable requirement
and does not prescribe production or harness structure.

## 4. Other audited boundaries

The committed Review-4 two-line, Review-5 oneline, compact-JSON, Review-6 pretty-JSON and
same-record-inventory siblings do what the author claims: 41/131 and 212/212, failing exactly
those 90 duplicate rows. Inverse fake-opener controls, real-heredoc resumption, positive/zero,
missing/empty/malformed/non-numeric, duplicate order, conditional and standalone indented rows,
`W-common`/`W-positive`/`P-reader-restore`, paragraph wrap, dated-history and finite three-role
inventory all reproduced on the eleven frozen variants. No REQUIRED row was silently removed.
Published matrix hashes and, after the one-field subject substitution, published raw hashes were
independently measured. Explicit shell exclusions remain as stated; this review does not widen
them except to refuse the pretty-printed `{` / `}` object the card already named.

The finite implementation inventory remains the six `scripts/test.sh` definitions, one common
fast/deep guard call, the targeted reader and three named current publication roles. Historical
decisions/reviews/signed packs remain controls. B/C behavior is used only for protected bytes and
count deltas; Batch D claim ownership is not duplicated or expanded.

## 5. Gate replay

I did **not** launch the seven-case `a-floors-gate.py` replay. The task forbade that expensive
run. The preserved gate harness/matrix remain checksum-valid, but no historical gate outcome is
represented here as freshly rerun or independently refreshed.

Direct diagnostic capture used a fixture-shaped reader transcript only. I did not source
`scripts/test.sh` and did not start a gate.

## 6. Limits and final boundary

This review establishes the exact frozen row counts, sibling discrimination, closure of Review
6's exact pretty-JSON and same-record-inventory spellings, acceptance of the stated Review-3
brace-less exclusion, and one passing pretty-printed `{` / `}` name-as-key counterexample whose
wrapper records are not exact `{` / `}`. It does not establish general Bash parsing, general
prose consistency, implementation correctness, a fresh fast/deep gate outcome, historical
factual truth, certification, signing, publication or D-055 closure. It does not alter or
adjudicate Gate S2, signed material, Batch D surfaces or held D-008 questions.

**FAIL.** Close the pretty-printed `{` / `}` name-as-key object even when the wrapper lines are
not exact one-character `{` / `}` records, not only the exact Review-6 payload the author froze.
Freeze a new exact evidence subject and obtain another fresh independent review before any
product repair.

## 7. Review-child guards

The only repository change made by this reviewer is this standalone review record. Attack
harnesses, matrices and reader transcripts stayed in `/tmp`. Before commit:

- secret guards: worktree and staged modes both `clean`;
- review scope: R1 490 / R2 47 / R3 152 and 689/689 before staging; R1 491 / R2 47 /
  R3 152 and 690/690 after staging;
- findings ledger: pass, 23 IDs and all D-057(1) totals unchanged;
- unchanged live floor reader: exit 0 at `92/527/221/7/78/30`;
- vendor-honesty mechanical guard: pass without exercising agent authority over public claims;
- workspace guard: pass with 13 pre-existing machine-state findings baselined and zero new;
- process audit: no scratch-path shell/gate body, Forge, Anvil, Sentinel Node or npm test
  process was started; diagnostic capture used a fixture transcript only;
- staged scope: exactly this added record, with `git diff --cached --check` passing; and
- protected B/C and signed-pack hashes: unchanged as recorded in section 1.

Workspace success remains ratcheted; it does not erase the 13 pre-existing findings.
