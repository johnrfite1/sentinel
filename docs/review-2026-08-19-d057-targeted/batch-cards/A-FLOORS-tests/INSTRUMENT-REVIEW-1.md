# A-FLOORS — fresh independent instrument review 1

## Verdict

**FAIL for instrument readiness.** The frozen contract has two independent false-green routes
inside behavior it expressly claims: it never supplies zero as a value to its positive-decimal
oracle, and its `conditional/indented` rows supply only conditional syntax. A future checker can
pass every frozen case while accepting `NAME=0`, or while refusing the tested conditional form
but accepting a standalone executable indented assignment. Neither route is an implementation
question; both are omissions in the frozen test stimulus.

This is a verdict on the test contract only. It is not an implementation verdict, gate approval
or signature, certification, ratification, publication, rename, D-055 assessment, D-008 action
or push authorization.

## 1. Frozen identity, scope and authorship separation

I reviewed exact subject `e8b4d29641c47f0099482c9a9ac5da86c9255197`, tree
`3debee282acb37a23e0a5ba8eb38368ad5736d08`, whose only parent is the declared behavioral
baseline `1a133301533e9d959dbafbbcc7ffe05e7eb78df3`. The baseline independently resolves to tree
`07cdc103133525f42b95018fabb802caa7cd8af3`, parent
`a0952264521f0f0755cb34b567877d496d8c1ec1`, timestamp
`2026-08-22T02:26:50-07:00`, and title `A-093: record C-SNAPSHOT implementation HOLD`.

The parent-to-subject diff is exactly 14 added files and 1,520 added lines, all beneath this
`A-FLOORS-tests/` directory. It changes no production byte, existing test, script, gate, floor,
maintained claim, prior evidence, decision record or signed material. `CHECKSUMS.sha256` has 13
payload entries because it does not self-hash; all 13 verified from this directory. Independent
hash and Git-object checks confirmed the provenance table, including:

| Frozen item | Git blob | sha256 |
|---|---|---|
| `scripts/test.sh` | `0c6c38ed746925d52720468865ca61eb31ae7ddd` | `66c272b90a16b037e3fcfc6f0d9184c48f63ac32e62538be7b6cd96a93801b79` |
| `scripts/check-suite-floors.sh` | `d69cc9a403719908139fdd660a126e254014d45b` | `c9a334dca2ce06e78a126e15dd33ef19bd0df3b43569eb0de76ea0b1c3ac13b6` |
| `docs/session-state.md` | `b91f548389a52b75b9796d3aaa975fc6e542dedc` | `2a2d0a4ce78cd06a8af38d80aa90f5c3eabb32968905ca18250f61e5fe54de2c` |
| frozen B-EVENTS test | `b601b0ad949a6c64b5ab53232fc00a9784e123a0` | `2a9219cc5138858b012b0bc56069490db3dd7d1963b73ccc19c28a48ce2b029e` |
| frozen C-SNAPSHOT test | `6a00cb9d674a5fe89c0e999149add7e25f7100de` | `29a673560e89b639b6635661706a368454c9969a04c5d37c4f6c15229df3dd8a` |
| signed Gate S2 pack | `baab3e7809a46f22131ef2b609f30af1ed8eeada` | `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589` |

I read the workspace instructions; the complete operative D-058, D-059, D-060 and D-066
records; all 14 evidence files; the current reader and complete gate; the three claimed live
paragraphs; the frozen B/C tests; R4-F4 evidence; `N-TESTSH-FLOORS`; and the C3 adjudication. I
authored neither this instrument nor a future Batch A implementation.

## 2. Blocking findings

### F1 — the positive-decimal language has no zero stimulus

The card says every constant must be exactly one column-zero assignment whose value is a
**positive decimal**. Its per-constant cases are exact planned value (`V`), missing (`M`), empty
(`E`), spaced spelling (`X`), the single literal `not-a-number` (`N`), direct duplicates in both
orders (`DA`/`DB`), and one conditional duplicate (`DC`). None supplies `0`.

In a disposable exact-baseline clone I changed all six canonical values, and nothing else, to
zero. The current reader exited 0, printed each of the following, and ended with its success
claim:

```text
FOUNDRY_MIN_TESTS          0
TS_MIN_TESTS               0
VERIFIER_MIN_TESTS         0
VERIFIER_MIN_SAMPLES       0
VERIFIER_MIN_TAMPER        0
VERIFIER_MIN_TAMPER_MODES  0
suite floors: read from scripts/test.sh, which is the only copy.
```

That current defect is expected pre-repair; the instrument defect is discrimination. A natural
repair using `^[0-9]+$` rejects the frozen `not-a-number` row and accepts every frozen planned
value, yet still accepts zero. Because no frozen case observes zero, such a repair is
observationally indistinguishable from a genuinely positive-only reader. Exact-value assertions
do not close a lexical sibling the harness never invokes.

Related source-shape probes bound the result. The current reader accepted an ordinary positive
`1`. It also accepted the literal source value `$(printf 92)`, showing why one fixed
`not-a-number` specimen is not itself a structural proof of the language. `export
FOUNDRY_MIN_TESTS=92` and `readonly FOUNDRY_MIN_TESTS=92` both failed closed as missing; those
alternative shell spellings are outside the declared parser-completeness boundary, although
their diagnostic class is not frozen. The existing empty, spaced, direct-order, conditional and
prefix cases all ran in the focused reproduction described below.

**Required bounded correction:** add a zero refusal row for each of the six constants, with the
name and a defined positive/numeric diagnostic, or replace the example-only value oracle with a
justified structurally exhaustive positive-decimal oracle. In either form, causally calibrate it
against an otherwise-conforming digits-only sibling that accepts zero; proving only that the
already-broken baseline fails is insufficient. If the broad card wording is retained rather
than narrowed to the six planned literals, ordinary positive controls should remain accepted.

### F2 — `conditional/indented` coverage exercises only conditional syntax

The card separately promises refusal of “a conditional or indented assignment token that Bash
can execute,” and `COVERAGE.md` claims “conditional/indented duplicates” for every constant.
Every `DC-*` mutation is only:

```sh
if true; then NAME=999; fi
```

There is no standalone indented assignment stimulus. In an exact-baseline clone I inserted
`    FOUNDRY_MIN_TESTS=999` after the canonical line. Bash can execute that assignment, but the
current column-zero reader exited 0, reported the canonical 92 and claimed that the file was the
only copy. A future repair that recognizes the tested `if ...; then` syntax specifically can
pass all six `DC` rows while retaining this unobserved hole.

A broad textual-token scan is not a safe correction. As a negative control I added an
assignment-shaped string inside a `printf` argument; it is not an assignment and the current
reader correctly remained green. The frozen `P-mentions` control includes constant names but no
assignment-shaped quoted, commented or heredoc prose. Thus the present oracle neither demands a
plain indented executable assignment nor prevents a repair from rejecting inert prose that
looks like one.

**Required bounded correction:** either narrow both the card and coverage claim to the tested
conditional shape, or add a direct indented executable-assignment refusal probe for each
applicable constant and placement, with Bash-state witnesses. Preserve causal controls proving
that commented, quoted and heredoc/prose `NAME=value` text is not treated as an executable
duplicate.

F1 and F2 are independent: a perfect positive-decimal predicate does not find a second
executable source definition, and a perfect duplicate recognizer does not make zero positive.

## 3. Focused reproduction and oracle audit

The frozen focused harness independently hashes to
`4782ff0211ce64c5a6fb1c82b7faf6ea3b4118eea4fe218c38648386e235200f` and its tracked matrix to
`a704290d198f14ab85db1a66149b5dd03ff3d7096ad04646f05f5c6980247ca5`.
I reran it at the exact baseline in a disposable clone and inspected all 81 rows:

```text
REQUIRED 10/53
CONTROL 28/28
PRE-REPAIR DEFECTS OBSERVED
exit=1
```

The new raw output hash is exactly the published
`8a34c604d0a9ce814a55715a1f1775fcb9f01eff76a90b7ad4d33174c7d57478`.
The 81 unique matrix cases independently recount as 43 REQUIRED failures, 10 REQUIRED passes and
28 CONTROL passes. The ten passes are the four already-current verifier values and six expected
missing-definition refusals. The two blocking omissions above are not among the 81 rows.

The wiring witnesses are live rather than constant outcomes. At the baseline, `W-common` fails
because the exact candidate has zero targeted-guard invocations while `W-positive` passes. In a
disposable candidate containing exactly one direct invocation, `W-common` changed to PASS and
reported one; `W-positive` remained PASS. Code inspection also proves `W-positive` cannot always
pass: its first conjunct is false when candidate gate text equals the fixture text. The harness
captures `actual_gate_text` before any `make_fixture()` call, so later fixture mutation does not
silently replace the candidate being scored.

The Markdown classifier normalizes all whitespace before matching role anchors. I independently
unwrapped the current paragraphs and confirmed the finite live inventory is exactly the §3
stable paragraph, the §3 D-010 bullet, and the quoted gate D-010 paragraph named by the card.
The wrapped/unwrapped required rows have the same diagnostic expectation. The valid fixture
retains dated numeric history within those same paragraphs; `P-history`, constant-name mentions
without values, and unrelated numbers outside the roles all pass. Searches of README, HANDOFF,
the proposal, the current register, session state and gate found no additional operative sibling
floor publication outside those three roles. Dated decisions, reviews, signed packs and prior
gate narration remain historical controls and must not be swept or rewritten.

The six canonical source definitions, targeted reader, common gate call site, and three live
publication roles form a coherent Batch A implementation surface. B/C behavior stays excluded
except for frozen test bytes and their measured count deltas. D-059 assigns other maintained
claim repair to Batch D; this instrument does not double-own it. I found no missing live sibling
surface that would justify widening Batch A.

## 4. Top-level gate evidence and reliance limit

I read the complete 328-line serial harness, tracked seven-row matrix, results, gate-binding
record and path-free summaries. The harness and matrix independently hash to
`fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0` and
`0b4d9c127e7230c7266960fe073f92f9551da9a68005cb936850993d803d1c58`.
The tracked matrix contains seven unique serial cases and recounts to REQUIRED 2/4 and CONTROL
3/3, with the published elapsed times. Static inspection confirms one exact-commit clone per
case, synchronous execution, separate fast/deep current-publication falsifications, a raised
103/550 control, and the isolated eleven-test B and twenty-three-test C deletion cases. Its
success predicates inspect named counts, later-stage markers, completion/refusal tokens and the
expected floor breach rather than relying only on process status.

I did **not** spend another approximately twenty minutes rerunning the seven top-level cases
after F1 furnished a decisive in-contract counterexample. The external full raw logs named by
their published hashes were not present for independent reinspection; only the tracked matrices
and summaries were available. Therefore this review neither independently refreshes their
timings nor elevates the author's behavioral evidence. The preserved serial evidence remains
relevant to the gate design, but it cannot cure an untested focused-oracle route and is not a
basis for the FAIL verdict.

## 5. Guards and boundaries

The final review child was checked with the repository secret guard in worktree and staged
modes, review-scope partition, findings ledger, unchanged floor reader, vendor-honesty guard and
workspace guards. The workspace result remains ratcheted: 13 pre-existing Sentinel
machine-state findings are baselined and zero are new. No production, instrument, prior evidence,
protected B/C test or signed-pack byte changed. No test patch exists or was applied.

## 6. Verdict boundary

**FAIL.** Correct F1 and F2 in the test contract, preserve their causal controls, freeze a new
exact evidence subject, and obtain another fresh independent instrument review. Do not repair
the product under this deficient frozen oracle. This review makes no statement about a future
implementation, historical factual correctness, generic Bash parsing, generic Markdown
consistency, gate signing or D-055 closure.
