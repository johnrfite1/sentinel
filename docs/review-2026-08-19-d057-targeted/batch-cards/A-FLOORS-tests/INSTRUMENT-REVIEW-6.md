# A-FLOORS — fresh independent fifth-corrected instrument review 6

## Verdict

**FAIL for instrument readiness.** The fifth correction closes Review 5's four frozen holes:
semicolon-joined Review-4 records, space-joined copies of those records, compact JSON that lists
every name beside a class field, and the `VERIFIER_MIN_TAMPER` / `VERIFIER_MIN_TAMPER_MODES`
prefix collision. The committed oneline and JSON siblings fail exactly the 90 named-duplicate
REQUIRED rows. The matcher still treats any newline-split record whose stripped text begins
`{NAME}:` and whose remainder contains the class word as a named-subject refusal. Pretty-printing
a JSON-like object with each constant as an unquoted key after `{` returns **131/131 REQUIRED and
200/200 CONTROL**, exit 0, and a matrix byte-identical to the satisfying exact-positive control.
That reader never names the mutated constant as the unique subject of the refusal; it emits every
name as a `{NAME}:` record whenever any duplicate exists. `CARD.md` §2 says wrapping every
constant in JSON beside the class does not satisfy the named-subject assertion. The six
`DR-json-*` rows and the live compact-JSON sibling cannot catch it: they score only the one-line
`{"names": "...", "class": "..."}` payload the author froze.

This is an instrument-readiness verdict only. It is not an implementation verdict, gate approval
or signature, certification, ratification, publication, rename, D-055 assessment, D-008 action
or push authorization.

## 1. Exact subject, scope and preservation

I reviewed exact subject `3fc2e5673bc2d10f552c5d5177c56cabac008541`, tree
`d3b174085e0de1bc2b76fce551dddfef749d6d60`, whose sole parent is Review-5 FAIL of record
`30d6257f806276a24cb6a40319b5bbb858fa9a5d` (tree `80769f8b18ab3b716bb51d40463e153a840c10e6`).
HEAD was exactly that subject and tracked-clean before this review file existed.

The parent-to-subject correction contains exactly 28 paths, all beneath this `A-FLOORS-tests/`
evidence directory: nine modified evidence/harness files, the added concurrent Review-5 blob, and
eighteen added v5 matrices/summaries, with 3,720 insertions and 176 deletions. It changes no
production byte, existing product test/script, live gate, maintained claim, decision record,
signed material or prior review. `git diff --check` passes. All 77 entries in corrected
`CHECKSUMS.sha256` verify.

Reviews 1–5 and the concurrent Review-5 blob are byte-preserved at:

- Review 1: `d07c6358127caba142b0c95adcba6fc33cb5b8eafdbba5c8680382a32d39c82d`;
- Review 2: `978d09f669cb6c5037d0de0e903f678ea7015f394670692698305b2f821ae7ae`;
- Review 3: `27e8e8da48fe34a07c750023296c11b82d937279f65b058fe4c5d2e78523bf86`;
- Review 4: `cfdf80b4c49a5716565fae5254652174c360226e005720402aaba8fb37d28437`;
- Review 5 of record: `4d742aded60fce42d30ec49dbb4d7a443fe0f0dbfc04ab9cafcc06987c4bd6fa`;
- concurrent Review 5: `10bc8231f5d9e3f309a3bf87190d1340f60176c8fdc1644bb1bf8bd2e585dbb7`,
  byte-identical to `bd0c43321e7bb2e8200513fb4e97666fccdab697`'s `INSTRUMENT-REVIEW-5.md`.

Every earlier non-v5 matrix and log summary is absent from the correction diff and verifies at
its preserved checksum. `a-floors-gate.py` and `gate-matrix.tsv` are byte-identical to the
Review-5 parent. The current focused harness is SHA-256
`3f347ecf482b7f249275dec87b70c6f94f9a3b3a329a4dd02e4db4a68742a42a` (1035 lines); the unchanged
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

No REQUIRED case name was added or removed versus the v4 exact-positive matrix. The fourteen new
rows are exactly the twelve `DR-oneline-*` / `DR-json-*` controls plus `DR-prefix-TAMPER` and
`DR-prefix-TAMPER-MODES` (331 unique names; 131 REQUIRED, 200 CONTROL). Live floors at this
subject remain `92/527/221/7/78/30`.

I read the workspace rules, operative D-058/D-059/D-060/D-065/D-066 records, the complete current
card/coverage/results/gate-binding/provenance/runbook/checksum set, Reviews 1–5, the concurrent
Review-5 blob, all current matrices and summaries, both harnesses, current reader/gate and the
named maintained surfaces. I authored neither this instrument nor a production repair.

## 2. Independent nine-variant reproduction

HEAD was exactly `3fc2e56` and tracked-clean. I executed the committed 1035-line harness from that
subject against a disposable clone of `3fc2e56`. All nine generated matrices were byte-identical
to their tracked v5 counterparts. Against `3fc2e56` the raw SHA-256 values differ from
`RESULTS.md` only in the printed `subject=` line; `RESULTS.md` used clone identity `30d6257`.
Substituting `30d6257f806276a24cb6a40319b5bbb858fa9a5d` for that one field reproduces every
published raw hash.

| Variant | Exit | REQUIRED | CONTROL | Raw SHA-256 (subject `3fc2e56`) | Matrix SHA-256 |
|---|---:|---:|---:|---|---|
| pre-repair baseline | 1 | 4/131 | 200/200 | `0c4b3e37db608eea9830570a1aeb4adbd69d3645479df43623796989e393d4ac` | `b7dabf0e3ea0ede2c0fdf6bca70feeafa2d911b77e55c06e8db625078f1283e0` |
| digits/zero sibling | 1 | 125/131 | 200/200 | `f62ba9bf56392e170523a6f70bc998edd45bcd86cf615658f1a5ca835e40a401` | `3eac8a9e4657f518870ce53110c23ad4f97b229e689629184dfe712d40aab62b` |
| exact Review-2 raw sibling | 2 | 83/131 | 160/200 | `dd5fb353b263669c0a2169a0c18820074f29ac6cdb4e149dc5616bfce66f88ce` | `16766991f633d81c8753cc2502475b90a9ca81b5f533aefbd90615ee7013d7c2` |
| exact Review-3 non-comment sibling | 2 | 131/131 | 152/200 | `e224f67b93ea9f1399f1e41b689b695172c99a1743a2ed620edb25373d3e3d66` | `325b2323d55acbca4da494f11c82e617317c97fbfeb8fb96fab9745f9b9cce6d` |
| expanded all-token sibling | 2 | 131/131 | 146/200 | `835be68504233b511b21abbc6701b77843772dea169a68220f16e94f2611d5cb` | `1b7d8c79585314734ee48f0ad932541fb15255e63c1eed673fd6d8c671f462d5` |
| Review-4 two-line uncorrelated sibling | 1 | 41/131 | 200/200 | `024fcb72bdc994cc5def0e4bddd6632b038d223f086b41e0f79f3b1a9fc4b3b4` | `b464ae62dcff31da51f5bd6391b7bc8c35c17e39fb540aa03a6c39162b522e2d` |
| Review-5 oneline uncorrelated sibling | 1 | 41/131 | 200/200 | `496cf0c032b26a5dc75531dabae214a95d6847fe6e99909f65cc9c91625e6211` | `b464ae62dcff31da51f5bd6391b7bc8c35c17e39fb540aa03a6c39162b522e2d` |
| compact JSON uncorrelated sibling | 1 | 41/131 | 200/200 | `22ed079f90bb21a9aa86c32a527a0af70f46ebede727a81342262c84cfe1af96` | `b464ae62dcff31da51f5bd6391b7bc8c35c17e39fb540aa03a6c39162b522e2d` |
| satisfying exact-positive control | 0 | 131/131 | 200/200 | `c30e02fcfa3ef1853cdcf26ce9a901ced5c2b2861020e8c2e3b8ec767e734bb6` | `ea972bff0f769c8acb177134d1ce5ddbcc03fcc18d89d704af2579f10d5e212a` |

Every matrix has 331 rows, 331 unique case names, 131 REQUIRED and 200 CONTROL, with identical
case-name sets. Independent route recounting confirms:

- 54 `FA-*` fake-only reader controls and 54 paired `TF/FC-*` requirements form a one-to-one
  route bijection (`comment` 6, `printf`/`echo`/`assign`/`herestring` 12 each);
- all 54 paired Bash witnesses exist and pass in the satisfying candidate;
- six `HR-post-*` real-heredoc post-terminator routes exist;
- twenty-six `DR-*` oracle rows exist; and
- `T-route-complete` passes with its 54/54 description.

The zero sibling fails only the six `Z-*` rows. Exact Review 3 fails exactly 48 non-comment
`FA-*` controls. The expanded sibling fails all 54 `FA-*` controls. The Review-2 sibling retains
its 48 `TF-*` REQUIRED failures and adds 40 `FA-*` CONTROL failures. Each committed uncorrelated
sibling fails exactly the 90 named-duplicate REQUIRED rows (`DA/DB/DC/IA/IB` 30, `TF-*` 48,
`FC-comment-*` 6, `HR-post-*` 6) and holds every CONTROL. The three uncorrelated matrices are
byte-identical to each other and distinct from the satisfying control. These scopes and counters
are from the reproduced matrices, not from `RESULTS.md`.

## 3. Blocking pretty-printed named-key JSON false green

Named source refusals are now scored through:

```python
def refusal_records(output: str) -> list[str]:
    records: list[str] = []
    for line in output.splitlines():
        for part in line.split(";"):
            text = part.strip()
            if text:
                records.append(text)
    return records

def source_refusal(result, name, reason):
    if result.returncode == 0:
        return False
    name_l = name.lower()
    reason_l = reason.lower()
    subject = re.compile(rf"^{re.escape(name)}\s*:", re.IGNORECASE)
    for record in refusal_records(result.stdout):
        match = subject.match(record)
        if match is None:
            continue
        head = record[: match.end() - 1].strip()
        if head.lower() != name_l:
            continue
        if reason_l in record[match.end():].lower():
            return True
    return False
```

Newline and semicolon are the only record boundaries. A record satisfies a name if it begins
`{NAME}:` and the class word is a substring after the colon. Compact JSON, space-joined Review-4
bytes, and semicolon-joined Review-4 bytes no longer match, because those records begin
`inspected constants:` / `{"names":` / `{` rather than `{NAME}:`. `DR-json-*` tests only that
compact inventory object. `DR-oneline-*` tests only the semicolon-joined string. Those rows never
invoke the candidate.

`CARD.md` §2 still requires refusals to name the constant as the subject of one refusal record
and says an inventory of every constant wrapped in JSON beside a class word does not satisfy that
assertion. `COVERAGE.md`'s disclosure that other grammars are "not covered" does not retire the
JSON claim the card already made, and it does not bind a live candidate for a pretty-printed
name-as-key object.

### Passing defective candidate

In `/tmp` I copied the committed 1035-line harness and changed only the uncorrelated-oneline
duplicate emitter to pretty-print an unquoted name-as-key object. Lexer, values, wiring,
fake-opener handling and every other behavior were unchanged. Against exact subject `3fc2e56`
that candidate returns:

```text
REQUIRED 131/131
CONTROL 200/200
A_FLOORS_FOCUSED_COMPLETE
exit=0
```

Its raw output hashes to
`95c501253267f15755d6f952965944ca4762d691c8fd4b2e425a6cc70fc43f6f`.
Its matrix hashes to
`ea972bff0f769c8acb177134d1ce5ddbcc03fcc18d89d704af2579f10d5e212a`
and is byte-for-byte identical to the satisfying frozen matrix. All twenty-six `DR-*` rows PASS.

Against a direct `FOUNDRY_MIN_TESTS` duplicate, the hostile reader's complete diagnostic is:

```text
{
  FOUNDRY_MIN_TESTS: duplicate executable assignment,
  TS_MIN_TESTS: duplicate executable assignment,
  VERIFIER_MIN_TESTS: duplicate executable assignment,
  VERIFIER_MIN_SAMPLES: duplicate executable assignment,
  VERIFIER_MIN_TAMPER: duplicate executable assignment,
  VERIFIER_MIN_TAMPER_MODES: duplicate executable assignment
}
```

That object hashes to
`3e6a9aa2cfedcedf1fea11682fb9252e4f6cd321dc25bcbb4cad73e66e0fbaea`.
`splitlines()` plus `strip()` turns every name into a `{NAME}:` record, so every duplicate
`source_refusal` row accepts it. The grammatical wrapper is still a JSON-like object of every
constant. The mutated constant is not distinguished from its five siblings.

Quoted pretty JSON (`"FOUNDRY_MIN_TESTS": "duplicate executable assignment"`) and compact
name-as-key / `{NAME:` wrappers still fail the 90 duplicate rows (41/131, 200/200, matrix
`b464ae62dcff31da51f5bd6391b7bc8c35c17e39fb540aa03a6c39162b522e2d`). The hole is specifically
pretty-printed NAME-after-`{` records under the card's own newline boundary.

### Confirming siblings

A reader that prints `{NAME}: duplicate executable assignment` plus the six-name inventory on the
same record after the colon likewise returns 131/131 and 200/200, matrix
`ea972bff0f769c8acb177134d1ce5ddbcc03fcc18d89d704af2579f10d5e212a`. Direct `FOUNDRY_MIN_TESTS`
output hashes to
`ce8456f5e8416459972e6174fdc43be3f68316f46158cfc4c7664017962c921e`.
`CARD.md` §2 says an inventory of every constant does not satisfy the named-subject assertion;
this record still carries that inventory after the colon. A kitchen-sink of every reason word
after `{NAME}:` also fully greens; class matching remains substring presence.

These are inside the stated finite diagnostic-correlation contract, not a request for generic
Bash parsing. Pretty-printed NAME-after-`{` is a JSON variant Review 5 required attacking.
Same-record inventory after `{NAME}:` is the decoy-after-colon candidate that charter also named.
Neither grammar has a `DR-*` row or a live sibling.

### Review-5 holes that did close

The following hostile candidates, run as full-harness siblings against `3fc2e56`, each return
41/131 and 200/200 with matrix
`b464ae62dcff31da51f5bd6391b7bc8c35c17e39fb540aa03a6c39162b522e2d`, matching the frozen
uncorrelated siblings rather than the satisfying control:

- space-joined Review-4 payload (no semicolon); payload SHA-256
  `518a78edb86ab2332eb47b70ddea9cf11f04c2ef49b5226893df0d97ad4a6eab`;
- comma-joined and pipe-joined copies of those two records;
- compact JSON inventory-plus-class, quoted pretty JSON, compact name-as-key JSON, and compact
  `{NAME:` wrappers;
- a kitchen-sink line that lists every constant and every reason word without a `{NAME}:` subject.

`source_refusal(..., "VERIFIER_MIN_TAMPER", "duplicate")` is false for
`VERIFIER_MIN_TAMPER_MODES: duplicate executable assignment` and true for a `TAMPER` subject.
The prefix collision is closed. The committed two-line, oneline and compact-JSON siblings do what
the author claims.

### Required bounded correction

Require that wrapping every constant as a pretty-printed `{NAME}:` / JSON-like key, or carrying a
decoy inventory of the six names on the same record as a named-subject class word, does not
satisfy the named-constant assertion. Do not calibrate only to compact `{"names":..., "class":...}`
or to semicolon-joined Review-4 bytes. Bind each rejected JSON and same-record-inventory grammar
to a live candidate sibling, not only to a synthetic matcher string. Keep a paired legitimate
`{NAME}: duplicate executable assignment` control. This states the observable requirement and
does not prescribe production or harness structure.

## 4. Other audited boundaries

The committed Review-4 two-line, Review-5 oneline and compact-JSON siblings do what the author
claims: 41/131 and 200/200, failing exactly those 90 duplicate rows. Inverse fake-opener
controls, real-heredoc resumption, positive/zero, missing/empty/malformed/non-numeric, duplicate
order, conditional and standalone indented rows, `W-common`/`W-positive`/`P-reader-restore`,
paragraph wrap, dated-history and finite three-role inventory all reproduced on the nine frozen
variants. No REQUIRED row was silently removed. Published matrix hashes and, after the one-field
subject substitution, published raw hashes were independently measured. Explicit shell exclusions
remain as stated; this review does not widen them.

The finite implementation inventory remains the six `scripts/test.sh` definitions, one common
fast/deep guard call, the targeted reader and three named current publication roles. Historical
decisions/reviews/signed packs remain controls. B/C behavior is used only for protected bytes and
count deltas; Batch D claim ownership is not duplicated or expanded.

## 5. Gate replay

I did **not** launch the seven-case `a-floors-gate.py` replay. The task made that expensive run
conditional on the cheap focused attacks holding; the 331/331 pretty-printed name-as-key
candidate is a decisive FAIL. The preserved gate harness/matrix remain checksum-valid, but no
historical gate outcome is represented here as freshly rerun or independently refreshed.

Direct diagnostic capture used a fixture file and a `check-suite-floors.sh`-shaped reader only.
I did not source `scripts/test.sh` and did not start a gate.

## 6. Limits and final boundary

This review establishes the exact frozen row counts, sibling discrimination, closure of Review
5's semicolon/space/compact-JSON/prefix holes, and one passing pretty-printed JSON-like
counterexample plus two confirming same-record decoys. It does not establish general Bash
parsing, general prose consistency, implementation correctness, a fresh fast/deep gate outcome,
historical factual truth, certification, signing, publication or D-055 closure. It does not alter
or adjudicate Gate S2, signed material, Batch D surfaces or held D-008 questions.

**FAIL.** Close the pretty-printed NAME-after-`{` JSON hole, and the same-record decoy inventory
after `{NAME}:`, not only the compact JSON and semicolon-joined bytes the author froze. Freeze a
new exact evidence subject and obtain another fresh independent review before any product repair.

## 7. Review-child guards

The only repository change made by this reviewer is this standalone review record. Attack
harnesses, matrices and reader transcripts stayed in `/tmp`. Before commit:

- secret guards: worktree and staged modes both `clean`;
- review scope: R1 467 / R2 47 / R3 152 and 666/666 before staging; R1 468 / R2 47 /
  R3 152 and 667/667 after staging;
- findings ledger: pass, 23 IDs and all D-057(1) totals unchanged;
- unchanged live floor reader: exit 0 at `92/527/221/7/78/30`;
- vendor-honesty mechanical guard: pass without exercising agent authority over public claims;
- workspace guard: pass with 13 pre-existing machine-state findings baselined and zero new;
- process audit: no scratch-path shell/gate body, Forge, Anvil, Sentinel Node or npm test
  process was started; diagnostic capture used a fixture file only;
- staged scope: exactly this added record, with `git diff --cached --check` passing; and
- protected B/C and signed-pack hashes: unchanged as recorded in section 1.

Workspace success remains ratcheted; it does not erase the 13 pre-existing findings.
