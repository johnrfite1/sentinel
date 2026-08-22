# A-FLOORS — fresh independent seventh-corrected instrument review 8

## Verdict

**HOLD for instrument readiness.** The seventh correction closes Review 7's commented pretty-JSON
hole. Unique-subject rejection now fires when any stripped refusal record begins with ASCII `{`
or `}`, not only when a record is exactly `{` / `}`. The committed commented pretty-JSON sibling
emits Review 7's `{ // object` / `} // end` payload, fails exactly the 90 named-duplicate
REQUIRED rows, holds every CONTROL, and shares the uncorrelated matrix rather than the
satisfying control. Review 6's exact `{` / `}` wrappers, same-record inventory, compact JSON,
oneline inventory, kitchen-sink class words, extra whitespace that still strips to `{` / `}`,
and wrapper spellings that still begin with `{` or `}` after strip all behave the same way.
`VERIFIER_MIN_TAMPER` is not credited from a `VERIFIER_MIN_TAMPER_MODES` subject.

A brace-less six-line `{NAME}: duplicate executable assignment` dump fully greens. That is the
stated Review-3 herestring fail-closed exclusion in `CARD.md` §2 and §8, not a Review-6/7 JSON
hole. Fullwidth `｛` / `｝`, a zero-width space before `{`, and `// {` wrappers also fully green;
`CARD.md` claims stripped records that **begin with** ASCII `{` or `}`, and I do not FAIL on
characters or comment placement outside that grammar.

This is an instrument-readiness verdict only. It is not an implementation verdict, gate approval
or signature, certification, ratification, publication, rename, D-055 assessment, D-008 action
or push authorization.

## 1. Exact subject, scope and preservation

I reviewed exact subject `17d1a4ea9195405add208fc4c1441be811921ec0`, tree
`33a56a20594f77138679054a5d8aef246554606d`, whose sole parent is Review-7 FAIL
`0e90836057174052c13327fa5410f58a92550ad0`. HEAD was exactly that subject. Tracked `README.md`
was dirty and `assets/` was untracked in the live worktree; I did not touch, stage or commit
either. Every focused run used a disposable clean clone of `17d1a4e` as the harness source.

The parent-to-subject correction contains exactly 33 paths, all beneath this `A-FLOORS-tests/`
evidence directory: eight modified evidence/harness files, `logs/README.md`, and twenty-four
added v7 matrices/summaries, with 4,566 insertions and 242 deletions. It changes no production
byte, existing product test/script, live gate, maintained claim, decision record, signed material
or prior review. `git diff --check` on the subject is clean. Every entry in
`CHECKSUMS.sha256` verifies.

Reviews 1–7 and the concurrent Review-5 blob are byte-preserved at:

- Review 1: `d07c6358127caba142b0c95adcba6fc33cb5b8eafdbba5c8680382a32d39c82d`;
- Review 2: `978d09f669cb6c5037d0de0e903f678ea7015f394670692698305b2f821ae7ae`;
- Review 3: `27e8e8da48fe34a07c750023296c11b82d937279f65b058fe4c5d2e78523bf86`;
- Review 4: `cfdf80b4c49a5716565fae5254652174c360226e005720402aaba8fb37d28437`;
- Review 5 of record: `4d742aded60fce42d30ec49dbb4d7a443fe0f0dbfc04ab9cafcc06987c4bd6fa`;
- concurrent Review 5: `10bc8231f5d9e3f309a3bf87190d1340f60176c8fdc1644bb1bf8bd2e585dbb7`;
- Review 6: `a807603684afc76f93929d662be111e1438d7578a7be3dbcdb4d9d7ef40ac3f4`;
- Review 7: `7d4fea4c150e7c136ecb364b32dca97e76a69b94b8267b44e470bd28956dfa77`.

`a-floors-gate.py` and `gate-matrix.tsv` are byte-identical to the Review-7 parent. The current
focused harness is SHA-256
`47cb61ccef462f75131259c7af2b22c12911c86347c898653d50062bf8b717b4` (1140 lines); the unchanged
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

All twelve official matrices have 349 rows, 349 unique case names in identical order, 131
REQUIRED and 218 CONTROL, including forty-four `DR-*` rows (six each of legit / two-line /
oneline / compact JSON / pretty JSON / pretty-comment / inventory, plus the TAMPER prefix pair).
No REQUIRED case name was added or removed versus the v7 exact-positive matrix. Live floors at
this subject remain `92/527/221/7/78/30`.

I read the workspace rules, the complete current card/coverage/results/gate-binding/provenance/
runbook/checksum set, Reviews 1–7, the concurrent Review-5 blob, current v7 matrices and
summaries, both harnesses, current reader/gate and the named maintained surfaces. I authored
neither this instrument nor a production repair.

## 2. Independent twelve-variant reproduction

HEAD was exactly `17d1a4e`. The committed 1140-line harness refuses a dirty source worktree, so
I executed it from `/tmp` against a disposable clean clone of `17d1a4e`. All twelve generated
matrices were byte-identical to their tracked v7 counterparts. Against `17d1a4e` the raw SHA-256
values differ from `RESULTS.md` only in the printed `subject=` line; `RESULTS.md` used clone
identity `0e90836`. Substituting `0e90836057174052c13327fa5410f58a92550ad0` for that one field
reproduces every published raw hash.

| Variant | Exit | REQUIRED | CONTROL | Raw SHA-256 (subject `17d1a4e`) | Matrix SHA-256 |
|---|---:|---:|---:|---|---|
| pre-repair baseline | 1 | 4/131 | 218/218 | `61b10f29983bfec5454bdcf9d8bf9791675b807be7e36b03c73e2419af843591` | `82e0e80e849190807576ddb079795dfeb86595eb517c035ed28a848023c23684` |
| digits/zero sibling | 1 | 125/131 | 218/218 | `e7c2bdb3c3562556213ff7b1b016209eb0606701da461417459820f97b07fe19` | `fec03d43fe4cc392fe8765119d651d971e06db853ebbc676b89d4290f518ae47` |
| exact Review-2 raw sibling | 2 | 83/131 | 178/218 | `436af4d1ddb5f70f12de38e65ab1b1576e1eb6839231e25816973328ce0f277c` | `0696db2d63fc9779e7038d0e4615ad92e748ff9845e6cd2e84a539999364c7c9` |
| exact Review-3 non-comment sibling | 2 | 131/131 | 170/218 | `b1bff87a3c97df24be6744a6ddaf237c45af1936276cc8e72339e0cc50eb34ff` | `57584faa5b4a2aeb8d03db41e354ba236e11082d31d5d062daceefd3be7aa2b2` |
| expanded all-token sibling | 2 | 131/131 | 164/218 | `238a8d0dc0bb6b036b9e4de6ed7d2882e56ac8822add39e7278fdb7a341ee954` | `eb398f4b816e395c277346d4ad104f295fd62ff982da81786bc011372111407b` |
| Review-4 two-line uncorrelated sibling | 1 | 41/131 | 218/218 | `99095eb08498c7b6c5b17e19348dde5f7bb2e3948f4d1c63cd2f095a4b4af911` | `b83e49acb5a483d9507b4ae4e31edfc0f53ffd767cf3d40b0dabfca81fd30308` |
| Review-5 oneline uncorrelated sibling | 1 | 41/131 | 218/218 | `d970c81d55a898f8729a1d01422fc6c6a79be0ba1e3446e79ff3822fd1d52d5a` | `b83e49acb5a483d9507b4ae4e31edfc0f53ffd767cf3d40b0dabfca81fd30308` |
| compact JSON uncorrelated sibling | 1 | 41/131 | 218/218 | `b8e7fd54bc127b69d477b9fb1d0010a9ce22412a00c8f2d6870f1b4def4ed563` | `b83e49acb5a483d9507b4ae4e31edfc0f53ffd767cf3d40b0dabfca81fd30308` |
| Review-6 pretty JSON uncorrelated sibling | 1 | 41/131 | 218/218 | `80da5b3930d0bffccbe141a89bc2e3120b145e58ee3a1c2ec6ac02d926e724d1` | `b83e49acb5a483d9507b4ae4e31edfc0f53ffd767cf3d40b0dabfca81fd30308` |
| Review-7 commented pretty JSON sibling | 1 | 41/131 | 218/218 | `370e7eea5f38a060eee575238b984b5cfa136368728662c3323563f4e471fe2e` | `b83e49acb5a483d9507b4ae4e31edfc0f53ffd767cf3d40b0dabfca81fd30308` |
| same-record inventory uncorrelated sibling | 1 | 41/131 | 218/218 | `3986b0e7a8ef8e3954fdccf4ca9fd8f5dc0bf225f7072c49c289938ff982fcad` | `b83e49acb5a483d9507b4ae4e31edfc0f53ffd767cf3d40b0dabfca81fd30308` |
| satisfying exact-positive control | 0 | 131/131 | 218/218 | `cd6829ed3c0c8ee655f803355b3dc15898bc6ccc6a43f27fa2fcfb4ecfcbe369` | `69825cc0e41a11cc359c66968f5920160f215d2a0c2f2b62e6c06a4dd99aeed0` |

Independent route recounting confirms:

- 54 `FA-*` fake-only reader controls and 54 paired `TF/FC-*` requirements form a one-to-one
  route bijection; `T-route-complete` passes with its 54/54 description;
- all 54 paired Bash witnesses exist and pass in the satisfying candidate;
- six `HR-post-*` real-heredoc post-terminator routes exist;
- forty-four `DR-*` oracle rows exist and all PASS in baseline, exact-positive, and every
  uncorrelated sibling.

The zero sibling fails only the six `Z-*` rows. Exact Review 3 fails exactly 48 non-comment
`FA-*` controls. The expanded sibling fails all 54 `FA-*` controls. The Review-2 sibling retains
its 48 `TF-*` REQUIRED failures and adds 40 `FA-*` CONTROL failures. Each committed uncorrelated
sibling fails exactly the 90 named-duplicate REQUIRED rows (`DA/DB/DC/IA/IB` 30, `TF-*` 48,
`FC-comment-*` 6, `HR-post-*` 6) and holds every CONTROL. The six uncorrelated matrices are
byte-identical to each other and distinct from the satisfying control. These scopes and counters
are from the reproduced matrices, not from `RESULTS.md`.

## 3. Attacks against the claimed begin-with `{` / `}` grammar

Named source refusals are scored through exact class phrases, a remainder name-scan, and a
wrapper check:

```python
json_wrapped = any(record.startswith("{") or record.startswith("}") for record in records)
```

`refusal_records` splits on newlines and `;`, then `strip()`. `class_remainder` lowercases,
strips, and strips a trailing comma, then requires equality with
`duplicate executable assignment`. Unique-subject rejection fires when any stripped record
begins with `{` or `}` and another floor name carries the same class phrase. `DR-prettycomment-*`
tests Review 7's exact payload; the live `uncorrelated-pretty-json-comment-sibling` binds that
emitter to the candidate.

Attack harnesses were copies of the 1140-line instrument with only the diagnostic emitter
changed, run as full focused variants against the same clean `17d1a4e` clone. Synthetic
`source_refusal` evaluation against the same payloads agreed with every live matrix.

### 3.1 CARD-stated wrappers — rejected, not a green

Live sibling against a direct `FOUNDRY_MIN_TESTS` duplicate emits:

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

Payload SHA-256 `d8b5d186035fadde9847fe0a8171695bd0ecba7f4d6b23306d03ea6de281bc01`.
`source_refusal` is false for every floor name. The committed commented sibling returns
41/131 and 218/218, matrix
`b83e49acb5a483d9507b4ae4e31edfc0f53ffd767cf3d40b0dabfca81fd30308`.

Review 6's exact pretty-printed unquoted name-as-key object (wrappers exactly `{` / `}`) hashes
to `3e6a9aa2cfedcedf1fea11682fb9252e4f6cd321dc25bcbb4cad73e66e0fbaea`. The committed pretty-JSON
sibling returns the same 41/131, 218/218, and uncorrelated matrix.

The following live copies, changing only wrapper spelling, each return 41/131 and 218/218 with
that same uncorrelated matrix, not the satisfying control:

| Wrapper spelling | Payload SHA-256 |
|---|---|
| `{/*` / `} /*` | `7bc9a1a7dc2d204d15f5b31ab63d5ca033f2c4ef4d969031927037c92fc4ef3b` |
| `{ #` / `} #` | `df910d5d96d9e18f2c454b6eb3675a5c251391d6e3263aa26fbf103e514ec3cb` |
| `{ //` / `} //` | `10bce7206f9aaf51b11b45ebf5de370c18d779251693c5e617295b5cda2d6823` |
| `{\t` / `}\t` | `82e97cc604980a4e950cf9302b9d6cffd130f1e940d5f013c8d427600232a0bd` |
| `{` / `} /*` | `2b34a9596a2d71305feefb9961d6a119e088dbbd05fd2414c7132439fa483943` |
| `{` / `} //` | `c5f307f04d185df63c20eb2b5c694e620b2f84fc28fc5ce954f71071c9c63bbd` |
| `{FOO` / `}` | `a9fb0d39df1b2b8483d6cc7a44955437eff90f1d6ee38312e8b40767d57d9e21` |
| `{ // object,` / `} // end,` | `5a3c33a0e179f5b813ae447e40549f86be76200b03114d80c8400b613e5b17f9` |
| extra whitespace still stripping to `{` / `}` | `99a1da50fa087dfe3d00b97a003f1fdc97f8c04e803feae13f38fca78cfc622f` |

Same-record inventory after `{NAME}:` (committed sibling) and two kitchen-sink remainders that
are not the exact class phrase (`missing definition empty assignment malformed assignment
numeric positive decimal required duplicate`, and `duplicate missing empty malformed numeric
positive decimal assignment executable`) each return 41/131 and 218/218 with the uncorrelated
matrix.

A named-subject line that itself begins with `{`:

```text
{FOUNDRY_MIN_TESTS: duplicate executable assignment
```

Payload SHA-256 `0c099bb85350eb9ed853c5a99d746d52a6ddfb94be3de742a5e73cd57d5976a4`.
`named_subject_hits` does not match `^FOUNDRY_MIN_TESTS\s*:`, so the line is not credited.
Printing that spelling for all six names is the same: 41/131 and 218/218, uncorrelated matrix.
That is fail-closed, not a false green.

Compact JSON and the Review-4/5 two-line and oneline inventories are the committed siblings
above: 41/131 and 218/218.

`source_refusal(..., "VERIFIER_MIN_TAMPER", "duplicate")` is false for
`VERIFIER_MIN_TAMPER_MODES: duplicate executable assignment` and true for a `TAMPER_MODES`
subject. The six `DR-legit-*` rows still accept `{NAME}: duplicate executable assignment`.

### 3.2 Brace-less six-line dump — stated exclusion, accepted

A finite-lexer sibling whose duplicate emitter prints only:

```text
FOUNDRY_MIN_TESTS: duplicate executable assignment
TS_MIN_TESTS: duplicate executable assignment
VERIFIER_MIN_TESTS: duplicate executable assignment
VERIFIER_MIN_SAMPLES: duplicate executable assignment
VERIFIER_MIN_TAMPER: duplicate executable assignment
VERIFIER_MIN_TAMPER_MODES: duplicate executable assignment
```

returns **131/131 REQUIRED and 218/218 CONTROL**, exit 0, matrix
`69825cc0e41a11cc359c66968f5920160f215d2a0c2f2b62e6c06a4dd99aeed0`
byte-identical to the satisfying control. Payload SHA-256
`2e156ac2f721f2e0768bce951cb170f56d64018cc5abcb033ff2488440a5b0d8`.

No stripped record begins with `{` or `}`. `CARD.md` §2 and §8, and `COVERAGE.md`, state this as
the Review-3 herestring fail-closed shape rather than the Review-6/7 JSON grammar. The committed
Review-3 sibling scores 131/131 REQUIRED because its fail-closed diagnostic emits named-subject
`{NAME}: duplicate executable assignment` lines without those wrappers. I accept that as a
stated finite exclusion and do not treat the brace-less dump as a blocking false green.

### 3.3 Spellings outside the stated ASCII begin-with grammar — classified, not FAIL

Three live finite-lexer siblings fully green 131/131 and 218/218 with the satisfying matrix
`69825cc0e41a11cc359c66968f5920160f215d2a0c2f2b62e6c06a4dd99aeed0`. After `strip()`, their
wrapper records do **not** begin with ASCII `{` or `}`:

| Spelling | Payload SHA-256 | Why it is outside CARD |
|---|---|---|
| fullwidth `｛` / `｝` | `b70bd9706be4992f37f6fd1ed92de99cfa84f2f9174c7202ddaf497ce62a7dbb` | CARD's `{` / `}` are U+007B / U+007D |
| zero-width space then `{` / `}` | `a654ae9c13c1317368832aa29da81dcddb94663aa4b23777265f23438b0f1304` | `strip()` leaves U+200B; the record does not begin with `{` |
| `// {` / `// }` | `2957ff0f95e3e6a6c34da123cf4f052a8cc7cc543751515aab540d3d480ad9de` | comment precedes the brace; the record begins with `/` |

CARD §4 requires rejection when stripped records **begin with** `{` or `}`, including comments
**on** those wrapper lines (`{ // object`). It does not claim fullwidth braces, prefixed
invisible characters, or comment-before-brace lines. I do not FAIL the instrument on them.

### Required bounded correction

None for the stated ASCII begin-with grammar. Review 7's `{ // object` / `} // end` payload is
bound to a live sibling, and every tested wrapper that still begins with `{` or `}` after strip
fails the 90 named-duplicate REQUIRED rows.

## 4. Other audited boundaries

The committed Review-4 two-line, Review-5 oneline, compact-JSON, Review-6 pretty-JSON,
Review-7 commented pretty-JSON and same-record-inventory siblings do what the author claims:
41/131 and 218/218, failing exactly those 90 duplicate rows. Inverse fake-opener controls,
real-heredoc resumption, positive/zero, missing/empty/malformed/non-numeric, duplicate order,
conditional and standalone indented rows, `W-common`/`W-positive`/`P-reader-restore`, paragraph
wrap, dated-history and finite three-role inventory all reproduced on the twelve frozen
variants. No REQUIRED row was silently removed. Published matrix hashes and, after the
one-field subject substitution, published raw hashes were independently measured.

The finite implementation inventory remains the six `scripts/test.sh` definitions, one common
fast/deep guard call, the targeted reader and three named current publication roles. Historical
decisions/reviews/signed packs remain controls. B/C behavior is used only for protected bytes and
count deltas; Batch D claim ownership is not duplicated or expanded. Production
`scripts/check-suite-floors.sh` still prints `MISSING:` at the pre-repair subject; that is the
defect the card is supposed to observe, not an instrument FAIL.

## 5. Gate replay

I did **not** launch the seven-case `a-floors-gate.py` replay. The task forbade that expensive
run. The preserved gate harness/matrix remain checksum-valid, but no historical gate outcome is
represented here as freshly rerun or independently refreshed.

Direct diagnostic capture used a fixture-shaped reader transcript only. I did not source
`scripts/test.sh` as a gate and did not start a gate.

## 6. Limits and final boundary

This review establishes the exact frozen row counts, sibling discrimination, closure of Review
7's commented pretty-JSON spelling and of other ASCII `{` / `}` wrappers that still begin with
those characters after strip, acceptance of the stated Review-3 brace-less exclusion, and
classification of fullwidth / zero-width / comment-before-brace greens as outside CARD's
begin-with grammar. It does not establish general Bash parsing, general prose consistency,
implementation correctness, a fresh fast/deep gate outcome, historical factual truth,
certification, signing, publication or D-055 closure. It does not alter or adjudicate Gate S2,
signed material, Batch D surfaces or held D-008 questions.

**HOLD.** The seventh-corrected instrument is ready for a later product repair against this
exact evidence subject. That repair, and any gate replay, are outside this review.

## 7. Review-child guards

The only repository change made by this reviewer is this standalone review record. Attack
harnesses, matrices and reader transcripts stayed in `/tmp`. Before commit:

- secret guards: worktree and staged modes both `clean` (worktree emitted two `sed: RE error:
  illegal byte sequence` lines from untracked binary assets and still reported clean);
- review scope: R1 515 / R2 47 / R3 152 and 714/714 before staging; R1 516 / R2 47 /
  R3 152 and 715/715 after staging;
- findings ledger: pass, 23 IDs and all D-057(1) totals unchanged;
- unchanged live floor reader: exit 0 at `92/527/221/7/78/30`;
- vendor-honesty mechanical guard: pass without exercising agent authority over public claims;
- workspace guard: pass with 13 pre-existing machine-state findings baselined and zero new;
- process audit: no scratch-path shell/gate body, Forge, Anvil, Sentinel Node or npm test
  process was started; diagnostic capture used a fixture transcript only; `a-floors-gate.py`
  was not launched;
- staged scope: exactly this added record, with `git diff --cached --check` passing; and
- protected B/C and signed-pack hashes: unchanged as recorded in section 1.

Workspace success remains ratcheted; it does not erase the 13 pre-existing findings.
