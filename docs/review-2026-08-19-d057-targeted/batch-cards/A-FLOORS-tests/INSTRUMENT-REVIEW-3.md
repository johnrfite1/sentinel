# A-FLOORS — fresh independent second-corrected instrument review 3

## Verdict

**FAIL for instrument readiness.** The second correction closes Review 2's demonstrated
false-heredoc success route, but its paired transition rows do not establish why the reader
failed. Every fake-opener requirement includes both the inert opener and the following real
indented duplicate; the paired control proves only what Bash executed. No row requires the
reader to accept that exact fake opener when the real duplicate is absent.

A bounded sibling therefore retains Review 2's false heredoc state, which hides the real
duplicate, but fail-closes on the inert `A_FLOOR_MASK` token with the expected named `duplicate`
diagnostic. It passes all **131/131 REQUIRED and 120/120 CONTROL** rows, and its matrix is
byte-identical to the satisfying exact-positive matrix, while rejecting valid one-definition
source. This contradicts `CARD.md` §3's claim that the reader cannot satisfy the pair by rejecting
the inert token for an unrelated reason.

This is instrument readiness only. It is not an implementation verdict, gate approval or
signature, certification, ratification, publication, rename, D-055 assessment, D-008 action or
push authorization.

## 1. Exact subject, scope and preservation

I reviewed exact subject `12a35d2c3f30c77250b3ebde0bf82c25591dce10`, tree
`b75b7173793b2ea31305698d43a0d81f147e2540`, whose sole parent is Review-2 FAIL
`9889289cb730a7ef23b2b9d11c0e84110dce84f6`. The parent-to-subject correction contains 17 paths,
all beneath this evidence directory: eight modified evidence documents/harness files and nine
new v2 matrices/summaries, with 1,521 insertions and 264 deletions. There is no path outside the
declared evidence directory and no change to production, an existing script/test, a maintained
claim, signed material or a prior review.

All 29 entries in `CHECKSUMS.sha256` verify. The old matrices and non-v2 summaries are unchanged
from the Review-2 parent. The two review records are byte-preserved:

- `INSTRUMENT-REVIEW-1.md`:
  `d07c6358127caba142b0c95adcba6fc33cb5b8eafdbba5c8680382a32d39c82d`;
- `INSTRUMENT-REVIEW-2.md`:
  `978d09f669cb6c5037d0de0e903f678ea7015f394670692698305b2f821ae7ae`.

Independent Git-object and SHA-256 checks also preserve the behavioral baseline
`1a133301533e9d959dbafbbcc7ffe05e7eb78df3`, current gate/reader/session bytes, frozen B/C tests
and signed Gate S2 pack at the identities in `PROVENANCE.md`. The corrected focused harness is
`fb9577d3182cc881e4c2c4f5bca9c02d1ddf8ed04bd64d9f85e0db4d0985896d`; the unchanged serial
gate harness is `fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0`.

I read the workspace rules, operative D-058/D-059/D-060/D-066 records, all 30 current evidence
files, Reviews 1/2, both harnesses, current gate and reader, maintained live paragraph surfaces,
protected B/C tests and the cited R4-F4/C3/adjudication evidence. I authored neither this
instrument nor a future Batch A implementation.

## 2. Exact focused reproduction

I independently ran the current 859-line harness from the corrected subject against exact clean
Review-2 commit `9889289cb730a7ef23b2b9d11c0e84110dce84f6`. All four newly generated matrices were
byte-identical to their tracked v2 counterparts, and all raw and matrix hashes match the
publication:

| Variant | Exit | REQUIRED | CONTROL | Raw SHA-256 | Matrix SHA-256 |
|---|---:|---:|---:|---|---|
| pre-repair baseline | 1 | 10/131 | 120/120 | `a18333f67c4405af8b86aa7d6f4cfb9f94df380d31ae4744174cd40701f069e4` | `26039eccc906f3db9a5d8f97c7710e17fe6e007187c5503fcfd54fb16b9eaf35` |
| digits/zero sibling | 1 | 125/131 | 120/120 | `6b11d16b4d56040e78b2305b5bdc95a3be18451ee5fbb3c8899f3ff57d7f3350` | `93444b6b196518050ef16948743459112f1550ca7008a6a231cf9d42ae26ec08` |
| exact Review-2 raw sibling | 1 | 83/131 | 120/120 | `33a0b2d3b12cdb8f89b2b45b30774baee93f488797573b11033d056c5178fbc4` | `a49891dcfcfc5da17e0003a7ed1148901d7437d123e8e2b6347d4c6575babfc7` |
| corrected exact-positive control | 0 | 131/131 | 120/120 | `9044d8e72217b9bc03c023ff109b22663852c12f07d45f38bed70359efa84fd9` | `5d390a4fe8a1600d3430abb340e28e0f0f22e3389ad2f87e61636fa49a9244c1` |

The zero sibling's only failures are the exact six `Z-*` rows. The Review-2 sibling passes every
one of the 136 prior rows and fails exactly 48 required rows: 12 each in `TF-printf`, `TF-echo`,
`TF-assign` and `TF-herestring`. It passes all 120 controls, all six full-line-comment pairs and
all six real-heredoc post-terminator rows. The satisfying control completes with no non-pass row.

An independent TSV audit found 251 rows and 251 unique names in every variant: 131 REQUIRED and
120 CONTROL. The case-name set is identical across variants. Each of the nine declared fake
forms has exactly six required and six paired Bash-control rows, one per constant, giving 54/54
unique paired routes. Each matrix also has exactly six `HR-post-*` routes and one passing
`T-route-complete`. The only description differences between baseline and siblings are the
truthful observed values in the two raised `V-*` rows and the observed `W-common` invocation
count.

The exact Review-2 sibling reconstruction is faithful: its raw marker search, full-line-comment
exclusion and state transition precede `shell_code` exactly as recorded in Review 2; only the
positive value predicate differs from the deliberate zero sibling. The corrected finite sibling
handles all nine declared opener forms and genuine quoted-heredoc termination in the published
matrix. The card, coverage and results consistently exclude command substitution, backticks,
concatenated/escaped quote variants, process substitution and arbitrary redirection/delimiter
expansion; I do not treat those excluded Bash spellings as missing coverage.

## 3. Blocking causal false green

The sole `inert_opener_routes` loop always constructs this state:

```text
canonical assignment
exact inert fake opener
standalone indented NAME=999
```

It then records a CONTROL from `shell_value`/xtrace and a REQUIRED result from
`source_refusal(..., name, "duplicate")`. The control does not inspect the reader. The required
row accepts any nonzero output containing the target constant and `duplicate`; it does not
require the other constants to remain readable and cannot distinguish refusal of the inert
opener from detection of the following executable assignment.

There are 54 paired required rows and 54 paired Bash controls, but **zero reader controls that
instantiate any of the nine exact fake opener forms without the following duplicate**. `IC-*`
contains an ordinary assignment-shaped comment without `A_FLOOR_MASK`; `IQ-*` contains a quoted
assignment string without an opener; and `IH-*` is a genuine heredoc body. Those are useful prior
controls but do not observe the exact new fake-opener states.

### Passing defective sibling

I started from the exact Review-2 raw sibling with its positive predicate and retained its raw
marker-before-context transition. I added one bounded fail-closed policy: on non-comment
`A_FLOOR_MASK` syntax, emit the expected named `duplicate` diagnostic rather than accept the
inert source; for the name-free exact here-string forms, mark the definitions untrustworthy with
the same diagnostic. The raw state still masks the following executable duplicate.

The current frozen harness nevertheless reports:

```text
REQUIRED 131/131
CONTROL 120/120
A_FLOORS_FOCUSED_COMPLETE
exit=0
```

Raw output SHA-256 is
`c161fcc726002ad4c831334a2b255a10004609b74e97bcf6760b29bc5d2cd481`.
Its matrix SHA-256 is
`5d390a4fe8a1600d3430abb340e28e0f0f22e3389ad2f87e61636fa49a9244c1` and is byte-for-byte
identical to the tracked satisfying-control matrix.

An independent `printf-sq` probe makes the causal error directly observable. With only the
canonical 103 and exact inert fake opener present, Bash xtrace is `[103]`, final value 103, but
the reader exits 1 and prints `FOUNDRY_MIN_TESTS: duplicate executable assignment` (while its
false heredoc state also hides later canonical definitions). Adding the real indented duplicate
changes Bash xtrace to `[103, 999]` and final value 999, but the reader returns the same target
diagnostic. Thus the passing paired row did not establish that the reader saw the state change it
names. The compact probe log is SHA-256
`f400f28ed58f591695cf12107aaf4381ca414b88f0e4c0e325614dbc2c53b76d`.

This is a false green inside the exact finite grammar, not a request for generic Bash parsing.

### Required bounded correction

Add the missing inverse half of the transition matrix: for each of the nine exact fake opener
forms and each of the six constants, instantiate the opener at the same position **without** the
following indented duplicate and require reader exit 0 with all six canonical values reported.
That is 54 fake-opener-only reader controls. Retain the existing 54 paired routes and Bash traces
to require that adding the real duplicate reverses the reader outcome for the intended cause.

Calibrate the corrected matrix against this fail-closed/raw-state sibling, not only the original
Review-2 success sibling. A satisfying control must continue to pass both the 54 new inverse
controls and the 54 paired requirements. Do not weaken the controls by accepting a generic
nonzero diagnostic or by checking Bash without checking the reader.

## 4. Other audited boundaries

The prior source/value rows still cover every constant's exact value, zero, ordinary one,
missing, empty, malformed, nonnumeric, direct duplicates in both orders, inline conditional and
standalone indented duplicates before/after with exact Bash order/final-value witnesses. The
zero, Review-2 and satisfying siblings causally distinguish their named sets. Diagnostic helpers
require the target name and class; the new finding is specifically that the paired transition
does not constrain what caused that class.

`P-reader-restore`, `W-common` and `W-positive` all pass in every corrected sibling, including the
defective one. The candidate reader hash/output restoration and one common-path invocation are
therefore preserved, but do not close the missing inverse transition.

The three logical-paragraph roles, whitespace-wrapped/unwrapped classification, dated-history
controls and live surface inventory are unchanged from Reviews 1/2 and remain coherent. Current
source, session state, gate, README, HANDOFF, proposal and register searches expose no extra live
floor publication. Dated decisions/reviews/signed packs remain preservation controls. Batch A
owns the six definitions, targeted reader, common call site and three maintained roles; Batch D
claim repair and B/C semantics remain excluded. No implementation-surface expansion is needed
to correct this instrument gap.

## 5. Gate replay limit

I did **not** run the seven-case `a-floors-gate.py` matrix. The cheap focused counterexample is
decisive, and the review coordinator directed that no approximately twenty-minute gate replay be
spent after instrument FAIL. The gate harness/matrix remain checksum-valid and byte-unchanged,
but the old 3/3 CONTROL and 2/4 REQUIRED evidence is historical reliance only, not refreshed or
independently claimed here. A top-level run cannot repair a focused oracle that gives identical
passing matrices to conforming and nonconforming readers.

## 6. Review-child guards and final boundary

The only repository change made by this reviewer is this standalone review record. Repository
secret guards, scope, findings ledger, live floor reader, vendor-honesty guard, workspace guard,
protected hashes and the exact staged diff were run before commit. Workspace success remains
ratcheted: 13 pre-existing machine-state findings are baselined, not absent, and zero are new.

**FAIL.** Add and causally calibrate the 54 inverse fake-opener controls, freeze a new exact
evidence subject and obtain another fresh independent review before any product repair. This
review does not implement a reader, change an existing instrument, sign a gate, assess D-055,
act on D-008, certify/publish a claim, rename or push.
