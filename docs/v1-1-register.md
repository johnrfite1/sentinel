# Sentinel — v1.1 register

**This file changes nothing. It records what should change.**

D-035 part (c) ruled that the specification passages carrying fixture-specific worked examples
are a **v1.1 correction, not a v1 re-freeze**, and ruled explicitly that removing a worked
example from §4.2 *edits the specification to serve the measurement* and **is not authorised**.
So this register exists to hold the work rather than do it. Everything here is deferred behind
a decision that is John's.

Written 2026-08-15. **Its first version said "every line number and count below was verified
against the tree that day" — and every line number in it was stale within hours**, because the
Gate 5 certification grew §2 by four lines and nothing re-checked. Found by an independent
adversarial review, 2026-08-16. That sentence was the register's own inoculation against "a
figure that was true once", and it did not work, which is the more useful finding than the
off-by-four.

**Line numbers below are therefore SECTION ANCHORS, not line numbers.** Grep the quoted heading;
do not trust an integer in a file that moves. Counts were re-verified 2026-08-16 by running the
tools, not by reading the prose.

---

## 1. The contamination passages (A-030, D-035)

The channel is real and **measured to be small**: six targeted measurement arms (G, H, J, K, L,
M), across two specification versions and two models over fourteen fixtures, compared against
E and F as the labels of record — **one label moved** (F051), and it was the one labeller E had
itself flagged. (An earlier phrasing said "six labellers" and counted the measurement arms as if
they were the whole programme. Twelve label files touch those fixtures: A–D are the first round,
superseded by E and F under D-021's owed re-label; E and F are the record; G, H, J, K, L, M are
the measurement arms. See `docs/session-state.md`.) D-035's control arm — run twice, see A-037 — moved nothing. The
passages are still defects; the bound is what says they are not urgent.

| Passage | Where (grep this, not a line number) | What it leaks |
|---|---|---|
| §4.2 Case 2 | `#### Case 2: Real Prompt Injection — Block` | Walks through F049's scenario and states the expected block |
| §5.7.1 note | `*Added 2026-08-15 (D-031)` | Names "the wrong-policy fixture then ALLOWs" — that is F025, with its answer |
| §5.7.1 body | `**Binding and activation**` through `**Evidence that did not arrive**` | **Publishes all 41 of the evaluator's reason-code identifiers** |
| D-025's text | in `decisions.md`, reachable via the spec | Is F051's and F056's case, written out |

### A correction to D-035's own supporting text, which does not touch its ruling

D-035 records that "§5.7.1 publishes **eleven** of the evaluator's own reason-code identifiers".
**That number is wrong.** Counted directly: §5.7.1 publishes **41** — every check in the engine,
grouped under seven headings, each with a description. The "eleven" in the ratified entry is the
count from §5.7.1's own note of *checks with no home in §5.7's prose* ("eleven of the engine's
forty-one checks"), which is a different quantity that happens to sit in the same sentence.

**Consequence, stated plainly:** the contamination surface of that one subsection is roughly
four times what the decision log records. A labeller reading §5.7.1 sees the evaluator's entire
check vocabulary, not a sample of it — and labeller J cited those identifiers as `specBasis`.

**What this does NOT change:** D-035's ruling stands in full. Part (c) — v1.1 correction, not a
re-freeze — was decided on the *kind* of defect, not its size, and the measurement that bounds
it (zero movements out of five, twice) is unaffected. The entry is annotated in place rather
than rewritten, because it is John's ruling and only its supporting arithmetic was wrong.

### What amending these would cost, so the cost is not rediscovered

`scripts/check-eval-codes.sh` fails the gate if a check exists in the engine and not in §5.7.1.
**Deleting the identifier list to close the leak would break that guard**, which is the guard
D-031 added to prove §5.7's prose is complete. The two goals are in direct tension and the
resolution is a design decision, not an edit: the candidate shapes are (a) move the identifier
list out of the labeller-visible specification into an appendix the labelling protocol denies,
(b) keep it and accept a disclosed channel, (c) give labellers a redacted view of the spec.
**(c) is the largest change and the only one that also fixes §4.2.** None is chosen here.

## 2. The frozen labelling prompt says "three verdicts" and defines four

`fixtures/corpus/LABELLING_PROMPT.md` says "one of **three** verdicts" (line 20) and heads its
section "The **three** verdicts" (line 55) — then §2 instructs the labeller to answer
`INSUFFICIENT` when the material does not decide, and §7's output schema lists it as a fourth
enumerated value. Raised independently by the D-035 control arms.

This is not cosmetic: `INSUFFICIENT` is the control that makes the whole contamination
measurement interpretable — D-033's design rests on a labeller answering `INSUFFICIENT` rather
than guessing, so that "the amendment helped" is distinguishable from "the amendment decided
it". The one label that ever moved (F051) moved *to* `INSUFFICIENT`.

**Cost, per `check-label-prompt.sh`:** the file is frozen under D-011(a). Changing it means a
new file, a new hash, and a re-label of everything scored under the old one. **So this rides
with the re-label or not at all** — it is not worth a re-freeze by itself, and it has caused no
observed harm: every labeller found and used `INSUFFICIENT` regardless.

## 3. Corpus defects, all deferred for the same reason

Fixing any of these changes the view the labels of record were drawn against, so each belongs
**with** a re-label rather than before one.

**RULED 2026-08-16 (D-043): the re-label is bound to PRE-PUBLICATION with a named trigger** —
any move toward publication fires it, alongside Gate 8 and D-016's rename gate. All five defects
are fixed together and all 50 re-labelled **under the same frozen prompt**: D-035 ruled the
prompt is not at fault, so `check-label-prompt.sh` stays green and no re-freeze is involved. The
cost is fresh labeller runs, replacing E and F as the labels of record, and re-running the §7.3
ablation. **The trigger is named because pre-publication is where deferred things go quiet.**

- **F032 does not isolate policy expiry.** Its action deadline expires one second before the
  policy window, so it fails two checks in different D-026 remedy classes.
- **F026 and F051 pin different `allowedCallGraphHash` values over an identical observed call
  graph** — same target, selector, calldata, operation, and `internalCallCount` 0. At most one
  can describe what F051's intent claims. Found by labeller K with no implementation access.
- **F056 does not exercise reentrancy** (A-036) and **F051 is inert** for the neighbouring
  class, so §7.1's `reentrancy-attempt` and `unexpected-internal-call` classes are covered at
  the corpus layer by two fixtures that between them exercise neither.
- **The labelling view emits `failureMode` as `"0"`/`"1"` with no legend** (A-026(e)). The
  specification itself no longer has this gap — §5.9 (D-024) states `FAIL_CLOSED = 0,
  REVIEW = 1` — but **the fixture view a labeller reads still does not**, and every control arm
  run against the pre-§5.9 snapshot has flagged it, twice calling it their most actionable
  finding. Any re-label must fix the view first.

## 4. The highest-value item, and it is not on the list above

**A fixture's class name is a claim about what it exercises, and nothing in the corpus checks
that claim** (A-036, third instance of this defect class after A-028 F-5). The mechanical check
is describable in one sentence — *assert that each class's fixtures produce at least one failing
check the class is about* — and **is not built**.

It is the only item here that would have caught F056, F051 and the vacuous injection class
without a human noticing each one separately, and unlike everything else in this register it
does **not** ride on the re-label decision: asserting a property of the existing corpus changes
no fixture and moves no label.

**BUILT 2026-08-16 — `scripts/check-class-coverage.sh`, wired into the gate (A-038).** It
reports **14 of 20 classes exercise the class they name**. Four of the six carried are known and
reasoned; **two are new and unruled**, and they are the register's newest items:

- **`owner-override-and-block-behaviour`** — F054/F055 fail on code identity and wrong resource.
  Neither is about the override path.
- **`conflicting-block-state`** — F048 REVIEWs on simulation-unavailable and code-identity, which
  is an outage shape, not the conflicting-state shape D-030 calls a failed rule that blocks.

**RULED 2026-08-16 (D-039), and the two are not the same kind of defect:**

- **`owner-override-and-block-behaviour` — ACCEPTED DELEGATION, nothing owed.** F054/F055 declare
  `primaryEnforcement: vault-foundry-invariants` and the vault suite genuinely tests the override
  path. The declaration is accurate; the corpus layer is not where it is proved.
- **`conflicting-block-state` — A GAP, and it OWES A FIXTURE.** F048 declares
  `primaryEnforcement: conformance-engine`, claiming to be proved *here*, and is not. Nothing
  else covers it. **This is the one new v1.1 work item this session produced.**

The GAP inherits A-036's deferral — repairing F048 changes the view the labels of record were
drawn against — so the fixture rides with the re-label. What did NOT ride with it is the guard,
which is why building it first was worth doing, and the guard now carries a `status` of
DELEGATED / RESERVED / GAP so this distinction lives in the instrument rather than only here.

## 5. Owed on the vault and its evidence environment (D-042, A-040)

From the §9 steps 1–3 adversarial review. **The first two ride with the re-label; the third does
not and is the only one that could be done today.**

- **A per-action allowance-increase ceiling in the vault.** Today the vault caps native value
  only, so one valid ALLOW receipt for `approve(spender, max)` moves the entire token balance —
  the flagship Case 2 attack refused by the evaluator with nothing behind it.
  `PolicyPayload.maxAllowanceIncreaseBaseUnits` has no onchain counterpart. §7.1 is corrected and
  `test_LIMIT_vaultCapsNativeValueOnlyAndNotTokenAuthority` asserts the limit; **when the cap is
  built that test fails, and the failure is the signal to update §7.1, not to delete the test.**
- **The corpus vault configuration.** `ts/src/corpus/run.ts` and `ts/src/tools/emit-samples.ts`
  allowlist the ecrecover precompile `0x…0001` as an execution target and do NOT allowlist
  DemoERC20 — contradicting §7.2 and their own offchain baseline. **Verified to ride with the
  re-label:** `targetOnVaultAllowlist` is in the labelling view, F009's view carries `false`
  today, and labeller E's note cites "the target is off the vault allowlist" by name. Repairing
  it changes what the labellers saw. There is also no setter for the allowlists, so a
  misconfigured backstop needs a redeploy.
- **Receipt-to-signer-epoch binding.** Rotation is not revocation: a receipt from a rotated-out
  signer executes if that key is ever reinstated, and a receipt pre-minted by a standby key goes
  live the instant the owner rotates to it. **This does not touch the corpus and is not blocked
  by the re-label.** *The wrong comment is CORRECTED (2026-08-16) and both directions are now
  pinned by `test_LIMIT_reinstatingARotatedOutSignerRevivesItsOldReceipts` and
  `test_LIMIT_receiptFromAFutureSignerGoesLiveOnRotation`. Those tests assert the LIMIT — when
  epoch binding is added they fail, and the failure is the signal to update the comment and this
  entry, not to delete the tests. The binding itself is still owed.*
- ~~**Log the override authorization.**~~ **DONE 2026-08-16 (D-043).** §3.3(2) requires override
  be *logged* and it was not. `SentinelVault.OverrideAuthorized` now emits the override's own
  hash, the review receipt it names, the owner's `reasonHash` and its expiry — after
  authentication and before the call, so the log records only authorizations that passed.
  Done now rather than at v1.1 because an unmet stated invariant is a defect, not a feature.
  **Verified not to disturb the corpus:** the committed labelling views are unchanged.

## 6. ~~The specification defines no refusal record~~ — PUBLISHED 2026-08-16 (D-043)

**§5.5.1 now publishes `RefusalRecord`** — fields, order, domain tag, digest construction, and
the injectivity argument for the newline-joined preimage. It was a documentation correction, not
new design: the signer has produced this artifact since D-012.

**DONE the same day (A-042): the verifier now verifies refusals**, built by a schema-only agent
from §5.5.1 alone and measured against a real signed refusal it had never seen
(`fixtures/samples/refusal-vault-paused`, the first such artifact in the repository). Everything
§5.5.1 stated matched first time; the envelope it failed to state did not, and three further
defects in the section were found and corrected. Tests 101 → 146, 7/7 samples verify.

**What is still owed on refusals**, from that measurement: a refusal has no expiry and is valid
indefinitely; `schemaVersion` is cross-checked against nothing; and `refusalReason` sits outside
the signature, so a presenter can rewrite it — §5.5.1 now says it is not evidence, which is
honest but is a limitation rather than a resolution.

The original entry is kept below because the lesson is worth more than the fix.

---

**The highest-value item this session produced, and it was a spec item rather than a code one.**

D-012 requires that a refusal leave a recorded artifact, *"or 'the signer refused' and 'the
signer was never asked' are indistinguishable"*. **That requirement appears nowhere in the
published specification.** §5.4 defines `SignedDecisionReceipt` as payload plus signature and
stops; the word "refusal" does not occur in §5 at all. The only gesture toward it is a
parenthetical `(A-011, D-012)` in a §5.7 note, pointing at a decision record that implementers
and labellers are denied by protocol.

So an independent implementer building from the published document **cannot implement refusal
handling** — which is precisely the class of gap D-010 was promoted into v1 to surface, and it
took an agent denied the implementation to find it.

**Owed at v1.1:** a §5 payload for the signed refusal record — its fields, its type string, and
how it is authenticated — so the D-010 verifier can establish a refusal rather than refusing to
certify one. Until then the verifier's conservative behaviour is correct but is a placeholder
for a decision, not the decision.

**Do not fix this by loosening the verifier.** It currently fails closed on an unauthenticated
refusal claim, which is the right side to err on while the spec is silent.

## 7. Owed on the §2 capability table, after Gate 5's certification (D-038)

Two citations are weaker than they could be — one row cited for fewer criteria than the vendor
may document, and one still pointing at a marketing page rather than technical documentation.
Neither blocks anything; both would move accuracy in the direction that does *not* flatter
Sentinel.

**The detail is in `docs/gate-5-vendor-audit.md`, not here, and the split is not editorial:**
that file is the one artifact `check-vendor-honesty.sh` excludes from D-008(4), because it
cannot do its job without naming the parties. This register is a measurement artifact and must
stay free of vendor names. The guard caught a first draft of this very section for exactly that
reason, which is the second time it has fired on this session's own work.

**Any edit to the §2 table makes D-038's certification stale**, so these ride together with
whatever else touches that table rather than being applied one at a time.

## 8. Guard and gate defects found by adversarial review, 2026-08-16 (A-047) — RECORDED, NOT FIXED

Three independent reviewers were pointed at commits `fac9140..f65b745` and told to prove the work
fails. **John scoped the remediation:** the three severe defects were fixed (the corpus stage's
missing committed-view check, the verifier stage's missing floors, the case-sensitive vendor
scan). **Everything below is real, reproduced, and deliberately NOT fixed** — each reopens a guard
design question, and several touch rulings (D-038, D-039) that are John's.

**Read this before trusting any guard's output line.** Every item is a gap between what a guard
SAYS it protects and what it mechanically does.

### 8.1 Spec greps that are not scoped to the section they name

- **`check-type-strings.sh`** greps the whole 71 KB proposal for `^ {4}Name\(...\)$` and takes
  `head -1`. It is **not scoped to §5.8**. A decoy 4-space-indented type string earlier in the
  document satisfies the guard while §5.8 — declared "normative and byte-exact" — publishes a
  drifted one. Demonstrated with `MandatePayload`, `durationSeconds` `uint64`→`uint256`: guard
  green, and the two type hashes differ (`0xc4b5766f…` vs `0x003da56d…`). The same `head -1`
  weakness exists on the source side, so a comment above a drifted constant works too.
- **`check-eval-codes.sh`** is `grep -q "$code" "$SPEC"` — anywhere in the file, no section
  scoping, no description required, despite the output line and the failure message both naming
  §5.7.1. Demonstrated: three checks' documentation deleted from §5.7.1 and the bare identifiers
  left in an HTML comment at EOF — `41/41 engine checks documented in §5.7.1`, exit 0. The three
  included the mandate and policy validity windows. Today no eval code appears outside §5.7.1, so
  the guard is currently correct **by accident**.

### 8.2 `check-secrets.sh` — three independent evasions

- **The placeholder suppressor eats the language's own syntax.** Lines matching
  `(YOUR_|REPLACE_|EXAMPLE|PLACEHOLDER|xxx|\.\.\.)` are dropped, and `\.\.\.` matches `...` — the
  TypeScript spread operator, in a TypeScript repository. A real private key on a line containing
  `{...defaults, privateKey: "0x7c85…"}` passes; the identical line with the spread replaced by an
  explicit field is BLOCKED. The literal word `EXAMPLE` anywhere on the line does the same.
- **`ANVIL_ALLOW` is applied line-wise, not value-wise.** The whole line is discarded if a known
  Anvil key appears anywhere on it, so `KEY = "0x7c85…"; // rotated away from ac0974be…` passes —
  while the header promises "any OTHER 64-hex value bound to a key-shaped name is a finding".
- **The absolute-path scan is case-sensitive** — `(/Users/[a-z]|/home/[a-z])`. `/Users/Johnfite/…`
  passes; lowercasing the one letter fails the guard. macOS home directories derived from a full
  name are routinely capitalised.

### 8.3 `check-rename-gate.sh` — publication is reachable without tripping it

- **It reads `remote.origin.url` only.** `git remote add public … && git push public main` is the
  literal one-click publication D-016 describes, and the guard reports "publication block intact".
- **A trailing slash on the origin URL degrades to UNVERIFIED, which exits 0.**
  `https://github.com/owner/repo/` — what `git clone` with a trailing slash leaves behind — yields
  `rename gate: UNVERIFIED`, exit 0, while the identical URL without the slash correctly reports
  `RENAME GATE VIOLATED`. The guard is honest that UNVERIFIED is not a pass, but the gate is green
  and the line is indistinguishable from the "no `gh` CLI" case a reader skims past.
- **Consequence for A-046's "all eight fire":** in an environment without `gh`, or without auth,
  this guard fires on nothing and the gate is green. A-046 did not disclose that precondition.

### 8.4 `check-class-coverage.sh` — the ruled GAP can be laundered green

The guard's entire evidence base is `fixtures/corpus/results/*.json`, a **committed** artifact
that nothing regenerates-and-compares — `grep -c results scripts/test.sh` → 0. The `--gate` corpus
stage does regenerate `results/` into its temp directory and then deletes it unread. Editing
F048's committed result so it fails an on-class check makes the guard fire and **prescribe the
second step** ("Remove it from BASELINE"); doing so yields `15 of 20 classes exercise the class
they name` and `All carried classes are DELEGATED or RESERVED with a ruling. None owes a fixture.`
The D-039 GAP — the one class ruled genuinely uncovered and owing a fixture — disappears from the
report. **The fix is the same one A-047 applied to the labelling views:** compare the committed
`results/` against the freshly generated ones. **THE REASON ORIGINALLY GIVEN HERE WAS FALSE
(A-048):** it said the fix "was not applied because the corpus stage deletes that directory". It
does not, at the point that matters — `$CORPUS_TMP/results/` is fully populated when the view
check runs, and the `rm -rf` comes later in the stage. An independent reviewer measured the real
obstacle instead: fresh and committed `results/` differ in all 50 files, but after stripping
`micros` **exactly one** differs (`F033.json`, two `detail` strings embedding a chain timestamp)
and `_index.json` is byte-identical. **So the fix is two normalisations away, not structurally
blocked.** What genuinely defers it is that D-039's ruling is John's.

### 8.5 The D-010 verifier — a named check is asserted by nothing

**DONE 2026-08-17 (A-049) — see the closing note at the end of this subsection.** As found:
`ok = True or evidence_hash == expected_hash` in `verify.py` left **all 146 tests passing and
all 7 samples verifying**. No `TAMPER_MODE` corrupts `evidence.hash`; the field is only ever read.
Proven non-vacuous against a bundle with a one-nibble-corrupted hash, which the unmutated code
FAILs and the mutated code PASSes. **Owed: an `evidence.hash` tamper mode.** Three control
mutations were caught, so this is a specific hole, not a general one. A-047's floors catch a
verifier that SHRINKS; nothing catches one that silently stops checking.

**CLOSED 2026-08-17 (A-049).** The `evidence-hash` tamper mode corrupts the PUBLISHED hash
rather than the canonical bytes, which is what isolates this one check — the pre-existing
`evidence` mode changes the bytes, and other checks notice that, so it never isolated it. Three
tests, written so none can pass for the wrong reason: the mode's presence in `TAMPER_MODES` is
asserted STRUCTURALLY (a mode can be implemented and never registered — D-042), the mutated
bundle must fail ON THAT CHECK specifically rather than on any check, and the UNMUTATED bundle
must PASS that same check so the test cannot succeed by the check always failing. Verified against
the pre-fix state: the neutering that was invisible now produces 12 failures. Suite 146 → 149,
tamper cases 55 → 62, and a distinct-MODE floor (24) was added because a pair count alone can be
padded by adding samples. **What is NOT closed is the generalisation** — no mutation sweep has run
over `keccak.py`, `secp256k1.py`, `eip712.py`, `refusal.py` or `reasoncodes.py`, so this is the
only hole of its kind anybody has looked for.

Also on that stage, not fixed:
- **Arm B is subsumed by arm A.** `test_verifier.py:399` already runs
  `verify.main(["--all", SAMPLES])` and asserts exit 0, so the CLI arm detects nothing the suite
  does not. A-045 justified it as catching "a verifier that passes its own tests while rejecting
  the corpus" — a state the suite makes unreachable. It is 0.6s and it produces the sample count
  the new floor reads, so it stays; the justification was wrong, not the line.
- **`verify.py`'s module docstring documents `--tamper fixtures/samples/case-1-allow`, which
  argparse rejects** (`--tamper` takes `nargs="?"` and swallows the path as the mode).

### 8.6 `check-vendor-honesty.sh` — residuals after A-047's case fix

- **CORRECTED 2026-08-17 (A-048), and it was wrong twice over.** The residual is not "lower
  case": `grep -Eq` is exact-case in BOTH directions, so **any casing but the one declared
  spelling evades** — `SAFE`, `CIRCLE` and `SIGIL` in capitals all pass, verified, and all-caps
  is this repository's own emphasis idiom. And the justification held for only ONE of the three:
  measured over the guard's own artifact set with its own `\b` form, **safe 11 files, circle 0,
  sigil 0.** **DONE 2026-08-17 (A-049): `Circle` and `Sigil` moved to any-case, and `Safe` now
  carries its uppercase spelling explicitly.** Verified across seventeen probes — every casing of
  every listed name is caught except the one declared residual. **The dead `VENDORS` variable is
  also deleted** rather than kept in sync, since two lists that must agree is the defect this file
  already warns about. **Residual, narrowed:** `safe` and mixed-case oddities of it still pass,
  because "safe" occurs eleven times in scope as an English word and a guard that cries wolf gets
  reverted. One word in one casing family, down from three words in every casing but one.
- **The binary skip is an extension allowlist** (`*.png|*.pdf|*.zip|…`). A genuine
  `docs/gate-5-comparison.pdf` carrying a vendor table is never scanned.
- **`CAVEAT` is `head -1` over the whole proposal**, so a shorter sentence containing the key
  phrase, inserted earlier, becomes the enforced caveat. The check is also hard-coded to
  `docs/ablation-report.md`: numbers moved to a new file carry no caveat requirement.
- **The `rows`/`cited`/`badrefs` awk is not scoped to §2** (unlike `table_sha`, which is). A decoy
  capability-table header earlier in the document hijacks the D-008(1) count. Not turned into a
  violation, because `CERTIFIED_TABLE_SHA` independently pins §2's lines — the hash is doing the
  real work, not the counter.

### 8.7 The labelling-prompt freeze covers one of two channels

`check-label-prompt.sh` could not be defeated — it is the one guard whose mechanism is exactly as
strong as its claim. But D-011(a)'s stated purpose is that nobody can quietly retune the labelling
instructions, and `fixtures/corpus/labels/labeller-*.provenance.json` carry substantial per-labeller
`assignment` briefs that **nothing pins**. The project's own record (A-028 F-1) is an instance of
that unpinned channel contaminating a round. Structural, not a mechanical bypass.

## 9. The directed mutation sweep of the verifier, 2026-08-17 (A-051) — 41 survivors, 3 closed

A directed sweep applied **142 behaviour-changing mutations** across the six `verifier/` modules
that are not `verify.py`. **84 were caught; 41 survived a fully green gate** (17 further green
results were proven no-ops and are not counted). Six survivors were run through
`./scripts/test.sh` end to end — all exit 0, the D-010 stage line byte-identical to baseline.

**CLOSED under John's scoping (the three that flip a VERDICT rather than degrade a diagnostic):**
pair-aligned whitespace in `_HEX_BODY`; `strict=` unasserted at four of five `struct_hash` call
sites; over-length signatures accepted by `parse_signature`. See `TestUnassertedValidation` in
`verifier/test_verifier.py` — each test was run against its mutation and confirmed to fail, and
the `strict=` test covers all four uncovered sites rather than the one the reviewer exploited.

**THE SHAPE OF WHAT REMAINS, which matters more than the count: construction is pinned, value-level
validation is not.** Type strings, golden typehashes, domain separators, field order and `\x19\x01`
are all caught. But `encode_value` is never called with a `bytesN` type at all, the `uintN` range
check has no test, and the signature parser only ever sees exactly 65 bytes. **24 of the 41
survivors live in that asymmetry**, in `eip712.py` (11/27 caught) and `secp256k1.py` (11/26).

**Owed, grouped by what one fix would close:**

- **`encode_value` coverage for `bytesN` and out-of-range `uintN`.** Short `bytesN` values
  right-pad and collide (`bytes4 "0xc1" == bytes4 "0xc1000000"`; `bytes32 "0x"` == all-zero), and
  a `uint8` of `"300"` or a `uint16` of `"65537"` hashes cleanly — producing a digest no conformant
  Solidity signer could produce, which §5.8 warns is indistinguishable from an invalid signature.
- **Complement-based charset tests, replacing enumerated bad lists**, in `reasoncodes.py`
  (tab, CR, backslash and `+` are all accepted when added to the charset; space and newline are
  the only spellings pinned), `refusal.py` (§5.5.1's width bounds are pinned on the SHORT side
  only, so over-length `actionHash`/`signer` values and a trailing-space verdict name pass), and
  `_HEX_BODY` (now partly closed). §5.5.1's charsets are the whole of its injectivity argument.
- **A witness pair for the UTF-16 sort that distinguishes BE from LE.**
  `test_key_sorting_is_utf16_code_units` names RFC 8785 §3.2.3 correctly and then picks
  `{U+FFFD, U+1F600}`, which orders IDENTICALLY under both — and every key in every fixture is
  ASCII, for which the two are provably the same. So `utf-16-le` survives while `utf-32-be` and
  `utf-8` are caught. Direction is fail-closed, but a wrong canonical form and a tampered bundle
  are indistinguishable at the output.
- **String-escape complement tests.** `test_escapes` pins the seven required short escapes and
  nothing about what must be emitted LITERALLY, so escaping `/` or `U+00A0` survives. No fixture
  contains a single `/` or a non-ASCII byte, so the sample walk cannot see it either.
- **An ERC-191 constant pinned independently.** `test_an_eip191_signature_fails_and_says_so`
  builds its test input using `refusal.eth_signed_message_digest` — the function under test — so
  any mutation of the wrapping is applied to both sides and the test passes regardless. With a
  drifted tag the verifier reports a genuine `personal_sign` receipt as a forgery, which is the
  exact misdiagnosis the function exists to prevent.
- **The EIP-2 low-s boundary**, unasserted in both directions (`N//2 + 1` is exactly the
  reflection of `N//2`, so a malleable pair passes the named low-s check). ~2⁻²⁵⁶ to hit by
  accident — a correctness item, not an attack.
- **`reasoncodes.reason_codes_hash()` without `validate_all`** will hash a delimiter-injected set,
  reviving D-022's collision at the module API. `verify.py` validates separately so the CLI still
  fails closed; this is a defence-in-depth loss.

**Two things about the sweep's own limits, recorded because they bound the result.**
`keccak.py` came back **17/17 caught, zero survivors**, with its four green results proven no-ops
over 609 inputs — it is genuinely well covered, and `jcs.py` caught 23/33 including the `1e-6`
threshold in both directions. And **`verify.py` — 1681 lines, the file that actually decides PASS
or FAIL — was not swept.** That is now the largest measured gap in the verifier.

**A HARNESS TRAP worth more than several of the findings.** A same-SIZE mutation landing in the
same filesystem-mtime second makes CPython reuse the stale `__pycache__` bytecode, so the
"mutated" run executes clean code and the mutation reads as a no-op. Same-size mutations are the
interesting ones. Any Python mutation harness here must run with `-B` and clear `__pycache__`.

## 10. Corrections owed to §8 and elsewhere (A-051)

- **§8.6's residual, restated once more.** `safe` in lower case AND in mixed case (`SaFe`,
  `sAfE`) still evades. `A-049` claimed "every casing of every listed name is caught except
  lower-case safe" on the strength of seventeen probes, none of which was mixed-case — a bound
  generalised past its own sample, which §5's traces warn about by name.
- **The committed-view relation check is TYPE-BLIND.** `int()` normalises `"9"` and `9`, so a
  view can change its JSON schema undetected. And `expiryBefore` is the constant `"0"` in 35 of
  36 views, so the "chain-time-varying" justification never applied to it.
- **Both verifier floors are ratchets against accident, not intent.** A mode is a NAME: replacing
  a real mode with a registered no-op raised the pair count to 63 while the mode proving a
  corrupted receipt signature is rejected no longer existed, and both floors stayed green. Only
  `evidence-hash` has a structural test naming it; no other mode does.
