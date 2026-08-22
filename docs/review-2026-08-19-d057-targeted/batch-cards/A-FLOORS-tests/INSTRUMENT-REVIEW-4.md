# A-FLOORS — fresh independent third-corrected instrument review 4

## Verdict

**FAIL for instrument readiness.** The third correction closes Review 3's missing inverse
fake-opener controls, but the common source-diagnostic matcher does not correlate the mutated
constant with the refusal reason. It accepts the target name anywhere in the complete output and
the reason word anywhere else. A reader that emits a benign inventory containing all six names
and reports an actual duplicate only as `UNRELATED_CONSTANT: duplicate executable assignment`
passes every one of the **305/305** frozen assertions and produces a matrix byte-identical to the
satisfying control. That reader violates `CARD.md` §2's requirement that refusals name the
constant and exact class.

This is an instrument-readiness verdict only. It is not an implementation verdict, gate approval
or signature, certification, ratification, publication, rename, D-055 assessment, D-008 action
or push authorization.

## 1. Exact subject, scope and preservation

I reviewed exact subject `fa92ff7729287b10d6e140a6955b9740248600a6`, tree
`e01f89342315611f42edd42ee6400b34ea0da56e`, whose sole parent is Review-3 FAIL
`cd12ac26fb718a9bd02971db1f09f4fe1189bba7`.

The parent-to-subject correction contains exactly 21 paths, all beneath this
`A-FLOORS-tests/` evidence directory: nine modified evidence/harness files and twelve added v3
matrices/summaries, with 2,233 insertions and 166 deletions. It changes no production byte,
existing product test/script, live gate, maintained claim, decision record, signed material or
prior review. `git diff --check` passes. All 42 entries in corrected `CHECKSUMS.sha256` verify.

Reviews 1–3 are byte-preserved at:

- Review 1: `d07c6358127caba142b0c95adcba6fc33cb5b8eafdbba5c8680382a32d39c82d`;
- Review 2: `978d09f669cb6c5037d0de0e903f678ea7015f394670692698305b2f821ae7ae`;
- Review 3: `27e8e8da48fe34a07c750023296c11b82d937279f65b058fe4c5d2e78523bf86`.

Every earlier non-v3 matrix and log summary is absent from the correction diff and verifies at
its preserved checksum. The current focused harness is SHA-256
`4bc09b9c4f835f28fcfc114a6f9b78c6bb3e102d3513eae545bdb1ad5996bb80`;
the unchanged serial harness remains
`fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0`.
The protected B-EVENTS/C-SNAPSHOT tests and signed Gate S2 pack remain respectively:

- `2a9219cc5138858b012b0bc56069490db3dd7d1963b73ccc19c28a48ce2b029e`;
- `29a673560e89b639b6635661706a368454c9969a04c5d37c4f6c15229df3dd8a`;
- `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589`.

I read the workspace rules, operative D-058/D-059/D-060/D-066 records, the complete current
card/coverage/results/gate-binding/provenance/runbook/checksum set, Reviews 1–3, all current
matrices and summaries, both harnesses, current reader/gate and the named maintained surfaces. I
authored neither this instrument nor a future Batch A implementation.

## 2. Independent six-variant reproduction

I ran the current 926-line harness externally against exact clean Review-3 commit
`cd12ac26fb718a9bd02971db1f09f4fe1189bba7`. All six generated matrices were byte-identical to
their tracked v3 counterparts; all raw and matrix hashes exactly match the publication.

| Variant | Exit | REQUIRED | CONTROL | Raw SHA-256 | Matrix SHA-256 |
|---|---:|---:|---:|---|---|
| pre-repair baseline | 1 | 10/131 | 174/174 | `cb2e9e89edc3d032483a5241df06d7d0fcae499de49c85acd3f40d763061d7f4` | `98a3f66489827f8632be5b32395d2e02841fc456099f5f179e213eeda71f95ca` |
| digits/zero sibling | 1 | 125/131 | 174/174 | `d9f08c88bed66e38b6789114fd4a20d7da104d5c2d138097e7ec6d935c67f47e` | `bbeaaf8a18d4ee08e9990b339ea3e5f426d19c3198adcfb9ae6ca9c27761c3e1` |
| exact Review-2 raw sibling | 2 | 83/131 | 134/174 | `65e1cf30e3c123a5485741e8544d3da6e45a6225d8ee73827046628bb85a778d` | `9456409625b1f49570c34580adbe1c0b7fc45d834965cfdeb3710d80aae97ecf` |
| exact Review-3 non-comment sibling | 2 | 131/131 | 126/174 | `b7950c4b1e4ca075ca6a32e525f5e1ea108f6c205cd6f862c378871e3eea101e` | `feb1ede79e3cff8ca38d34e1a747116daeac73589c982fa12be1781c2347f2f4` |
| expanded all-token sibling | 2 | 131/131 | 120/174 | `6e9daec8628d84707d1f7b1485fd85d1f6ca4eb29e7bb26071329f83e020ef2f` | `c9f40f79b8acac473701a1c17d2d928a93905369bbe3c41734c29afbaa4f5101` |
| satisfying exact-positive control | 0 | 131/131 | 174/174 | `a3a1c390ab03a53d19596d473fcbdfc3b38852d5775a3f7a1edc6ee45685bf16` | `15e53549138fb45d19c8b89d8f2dd676abdeb576aa735b195c20218e858bfe2d` |

Every matrix has 305 rows, 305 unique case names, 131 REQUIRED and 174 CONTROL, with identical
case-name sets. Independent route recounting confirms:

- 54 `FA-*` fake-only reader controls and 54 paired `TF/FC-*` requirements form a one-to-one
  route bijection;
- `comment`, `printf-sq`, `printf-dq`, `echo-sq`, `echo-dq`, `assign-sq`, `assign-dq`,
  `herestring-sq` and `herestring-dq` each occur exactly six times on each side;
- all 54 paired Bash witnesses exist and pass in the satisfying candidate;
- six `HR-post-*` real-heredoc post-terminator routes exist; and
- `T-route-complete` passes with its 54/54 description.

The zero sibling fails only the six `Z-*` rows. Exact Review 3 passes all 251 prior rows and six
comment-only controls, then fails the exact 48 non-comment `FA-*` controls. The expanded sibling
also rejects the six comments and fails all 54 `FA-*` controls. The Review-2 sibling retains its
48 `TF-*` REQUIRED failures and adds 40 `FA-*` CONTROL failures. These scopes and counters are
exact, not inferred from the summaries.

## 3. Blocking diagnostic-correlation false green

Every named source refusal is scored through this common helper:

```python
def source_refusal(result, name, reason):
    output = result.stdout.lower()
    return result.returncode != 0 and name.lower() in output and reason in output
```

The name and reason need not occur in the same emitted refusal record or line. No other frozen
row correlates them. The fake-only oracle's clean-output exclusions are useful but do not apply
to required refusal output, and the paragraph diagnostic helper uses a different line-correlated
predicate.

### Passing defective candidate

In a disposable exact Review-3 clone I installed the satisfying finite positive reader, then
made only this diagnostic-policy change:

1. every invocation emits one benign `inspected constants:` line listing all six names;
2. an actual duplicate emits only `UNRELATED_CONSTANT: duplicate executable assignment`.

The duplicate detector, finite fake-opener handling, values, wiring and every other behavior are
unchanged. The frozen harness nevertheless returns:

```text
REQUIRED 131/131
CONTROL 174/174
A_FLOORS_FOCUSED_COMPLETE
exit=0
```

Its raw output hashes to
`917e67ca19581a72b102cd911bd0970b490264e801a52ebd9398f1f710bab362`.
Its matrix hashes to
`15e53549138fb45d19c8b89d8f2dd676abdeb576aa735b195c20218e858bfe2d`
and is byte-for-byte identical to the satisfying frozen matrix.

Against a direct `FOUNDRY_MIN_TESTS` duplicate, the hostile reader's complete output is exactly:

```text
inspected constants: FOUNDRY_MIN_TESTS TS_MIN_TESTS VERIFIER_MIN_TESTS VERIFIER_MIN_SAMPLES VERIFIER_MIN_TAMPER VERIFIER_MIN_TAMPER_MODES
UNRELATED_CONSTANT: duplicate executable assignment
```

That output hashes to
`4c216970238c6774a7ef3e9067cf26f0c417d47575421761636a9c23ddd6f37a`.
It contains the target and reason globally, so every duplicate `source_refusal` row accepts it;
there is no line or refusal record correlating them. By contrast, the unchanged satisfying
reader emits the legitimate control:

```text
FOUNDRY_MIN_TESTS: duplicate executable assignment
```

with SHA-256
`2d5fc18357191f989e580636199ba0d28e5c21095baf89aae60e7c2d62f4ac74`.
A direct same-record search rejects the hostile output and accepts this control.

This is inside the stated finite contract, not a request for generic diagnostic parsing.

### Required bounded correction

Add a causal diagnostic-correlation probe: a single emitted refusal record or line must
correlate the mutated target constant and expected reason class. Decoy occurrences of the name
elsewhere in output must not satisfy that assertion. Retain a paired legitimate named-diagnostic
control so the strengthened oracle does not reject the intended output. Calibrate the corrected
contract against the passing hostile candidate above. This states the observable requirement and
does not prescribe production or harness structure.

## 4. Other audited boundaries

The opposite-side opener design itself now discriminates its named routes: each fake-only case
requires exit 0, no refusal-class marker and all six exact canonical values; adding the real
indented assignment requires exact Bash `[planned, 999]` plus final 999 and a refusal. Real
heredoc bodies remain inert and their post-terminator assignments are visible. Comment-only and
comment-plus-real routes are separately present. The new finding is solely that the refusal's
target and class are not correlated.

The positive/zero, missing/empty/malformed/non-numeric, duplicate order, conditional and
standalone indented rows reproduce with their witnesses. `W-common`, `W-positive` and
`P-reader-restore` pass in all conforming/calibration siblings; restoration still compares both
reader bytes and live output. The paragraph wrap witness, wrapped/unwrapped current-role rows,
dated-history controls and finite three-role inventory remain unchanged. Explicit shell
exclusions are consistently stated in the card and coverage record; this review does not widen
them.

The finite implementation inventory remains the six `scripts/test.sh` definitions, one common
fast/deep guard call, the targeted reader and three named current publication roles. Historical
decisions/reviews/signed packs remain controls. B/C behavior is used only for protected bytes and
count deltas; Batch D claim ownership is not duplicated or expanded.

## 5. Gate replay and aborted setup disclosure

I did **not** launch the seven-case `a-floors-gate.py` replay. The task made that expensive run
conditional on the cheap focused attacks holding; the 305/305 hostile candidate is a decisive
FAIL. The preserved gate harness/matrix remain checksum-valid, but no historical gate outcome is
represented here as freshly rerun or independently refreshed.

During direct diagnostic capture I mistakenly attempted to obtain a Bash state witness by
sourcing a scratch clone's full `scripts/test.sh`. That started one unintended scratch fast gate.
I detected and terminated its exact supervisor/body/process chain after approximately 22 seconds,
then confirmed no scratch-path shell, gate body, Forge, Anvil, Sentinel Node or npm test process
remained. The partial run did not complete. **All of its output, timing and possible intermediate
state are excluded from this review's evidence and verdict.** The diagnostic outputs above come
from direct reader invocations, not that aborted gate.

## 6. Limits and final boundary

This review establishes the exact frozen row counts, sibling discrimination and one passing
diagnostic-correlation counterexample. It does not establish general Bash parsing, general prose
consistency, implementation correctness, a fresh fast/deep gate outcome, historical factual
truth, certification, signing, publication or D-055 closure. It does not alter or adjudicate
Gate S2, signed material, Batch D surfaces or held D-008 questions.

**FAIL.** Correct and causally calibrate the diagnostic-correlation oracle, freeze a new exact
evidence subject and obtain another fresh independent review before any product repair.

## 7. Review-child guards

The only repository change made by this reviewer is this standalone review record. Before
commit:

- secret guards: worktree and staged modes both `clean`;
- review scope: R1 432 / R2 47 / R3 152 and 631/631 before staging; R1 433 / R2 47 /
  R3 152 and 632/632 after staging;
- findings ledger: pass, 23 IDs and all D-057(1) totals unchanged;
- unchanged live floor reader: exit 0 at `92/527/221/7/78/30`;
- vendor-honesty mechanical guard: pass without exercising agent authority over public claims;
- workspace guard: pass with 13 pre-existing machine-state findings baselined and zero new;
- process audit after the aborted scratch run: no scratch-path shell/gate body, Forge, Anvil,
  Sentinel Node or npm test process remained;
- staged scope: exactly this added record, with `git diff --cached --check` passing; and
- protected B/C and signed-pack hashes: unchanged as recorded in section 1.

Workspace success remains ratcheted; it does not erase the 13 pre-existing findings.
