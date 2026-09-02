# Sentinel — A-018 remediation register

**This file changes nothing. It records what should change.** It holds the **proposed** remediation
set reflecting build-team evidence and informal chair consultation against the four
Adversary-sustained Cycle 2 Criticals (`A-018` / `MSG-022`, session
`S-20260829-sentinel-enforcement-publication`). **Pending Smith registration and authorization.**

Written 2026-08-30. **Corrected the same day, before any of it was acted on** — see §0.

**THIS REGISTER AUTHORISES NOTHING.** It does not withdraw a Critical, ratify Cycle 2, close a
gate, resolve the publication scope, or authorise a push, a deployment, or a visibility change.
The Crucible line remains **HALTED** with all four Criticals **OPEN AT ANVIL**. Nothing in §3
becomes authorised work by appearing here.

**Nothing here is "agreed" in any ratified sense.** Where an earlier draft said "agreed between
the build team and the Crucible council" or "accepted by the council," it was describing an
**informal consultation with no ledger entry**. The chairs made no ruling and the Smith has made
none. That wording is corrected throughout.

**LINE NUMBERS BELOW ARE SECTION ANCHORS, NOT LINE NUMBERS.** This is the `v1-1-register.md`
rule and it exists because that register's line numbers were stale within hours of being written.
Grep the quoted string; do not trust an integer in a file that moves.

---

## 0. What the first version of this file got wrong

Recorded at the top, in the house pattern, because the largest error was load-bearing and a
reader who skips it will draw the wrong conclusion about urgency.

### 0.1 THE PUSHED-BRANCH CLAIM WAS FALSE

The first version said these were *"live defects and false claims in code that exists on a
pushed branch."* **That is false.** Measured 2026-08-30:

```sh
git rev-parse --short HEAD                              # a38cff9
git rev-parse --short origin/step-3/isolated-signer     # 70f4b4d
git branch -r --contains a38cff9                        # (empty — no remote ref contains it)
```

**`a38cff9` was never pushed.** The BLOCK→PASS verifier and the entire v0.3 publication surface
exist **only in the local working tree.** No recipient has ever been able to obtain them.

**This is prevention work, not incident response,** and the distinction changes the sequencing
argument in §6. The error came from carrying a stale "branch pushed" fact forward — true of
`70f4b4d`, not of `a38cff9` — without re-measuring it. That is exactly the failure the
workspace rule *"verify before you rely on a documented status"* exists to prevent, committed
in a document whose §1 is a list of unverified claims.

### 0.3 A claim was written before its work existed, and an outage left it standing — 2026-09-01

Recorded in §0 because it is the same failure as §0.1 arriving by a different mechanism.

During the D-087 build, the documentation lane wrote into `HANDOFF.md`'s 2026-09-01 block that
*"the release's cold demo now mints a BLOCK receipt per run and requires four refusals"* — and was
then killed by a rate limit before the cold-demo change existed. For the length of the outage the
entry-point document a builder reads first asserted a control that `grep -c BLOCK
ts/src/tools/cold-demo.ts` measured at **0**. The coordinator caught it on resume by measuring
rather than reading the agent's report; the lane made the claim true by implementing the work
(six serial runs, four typed refusals) rather than striking it, and reported the error itself.

**Why it is recorded rather than simply fixed:** the lane's brief was claim honesty. The defect
this project keeps finding — a statement standing in the record with no control behind it — was
produced here by *sequencing under interruption*, with no misjudgement by anyone. A process that
writes the claim in the same pass as the work has this failure available to it whenever the pass
can be cut short. **The mitigation is the one already in force for everything else: measure the
tree, never the report.**

### 0.2 Three further corrections

- **Conscience attribution.** The first version said the council's restatement "named only the
  publication policy layer." Wrong as to the Conscience, who named **both**
  `verify_publication.py` and `deployment.py` explicitly (grep `so verifier/verify_publication.py,
  verifier/deployment.py` in the session `comms.md`). Her omission was not separating their
  *consequences*, not failing to name the module.
- **"Valid under every branch."** Overstated. The §3 items are valid **only if the v0.3
  enforcement/verifier architecture is retained.** A fresh casting could remove or redefine them.
  §3 is retitled accordingly.
- **Licence claim.** The first version said `UNLICENSED` leaves recipients "no right to use,
  modify, or independently examine." The examination half is **not established** and is removed
  pending legal review. What holds: `UNLICENSED` provides **no affirmative licence grant**.

---

## 1. Verified facts

Every figure produced by running the tool on 2026-08-30 against `a38cff9`, not by reading prose.

### 1.1 The shipped publication verifier accepts a BLOCK receipt

Reproduced. Signing a deployment manifest with a freshly generated authority key and pointing the
shipped verifier at the `case-2-injection-block` bundle (receipt `verdict` = `0` = BLOCK) returns
`PASS: authenticated deployment, owner mandate, exact action, and current receipt`, exit 0. In the
same run an invented `runtimeCodeHash` was echoed back in the PASS payload, and a receipt expired
nine hours earlier was revived through `--evaluation-time`.

**Not a signature or cryptography failure.** The signatures verify correctly. What the run
demonstrates is the absence of a binding between a signed manifest and live chain state, and the
absence of a verdict check.

### 1.2 Test coverage, and where the boundary falls

| File in `release/verifier/` | Covered by the 221-test suite |
|---|---|
| `eip712.py` | Yes — imported, 73 call sites |
| `jcs.py` | Yes — imported, 39 call sites |
| `keccak.py` | Yes — `keccak256` / `keccak256_hex` imported |
| `secp256k1.py` | Yes — recovery functions imported |
| `verify_publication.py` | **No — never imported by any test** |
| `deployment.py` | **No — never imported by any test** |

The 15 apparent matches for "deployment" in the suite are the English word in comments about the
legacy `domain.json` root, not the module. **The two uncovered files are exactly the two files
`a38cff9` introduced** — verify with
`git log --diff-filter=A -- verifier/deployment.py verifier/verify_publication.py`. The commit
boundary, the coverage boundary and the post-Gate-8 boundary coincide.

`deployment.py` deserves separate emphasis: **it is where the recipient's out-of-band trust
decision enters the system.**

### 1.3 The release tree, stated as a check result and not as an absence

**No known development key was detected by these checks in the enumerated release tree.** The
guard is a denylist — grep `KNOWN_DEV_KEYS` in `scripts/assemble-enforcement-release.py`. An
earlier draft said the tree was "already clean," which asserts an absence a denylist cannot
establish, in a document that criticised `release/README.md` for exactly that.

### 1.4 What the deployment manifest signs

`sourceArchiveHash` covers only `contracts/src/**.sol` (grep `function sourceArchiveHash` in
`ts/src/tools/cold-demo.ts`). The manifest also signs `runtimeCodeHash`, `compilerMetadataHash`,
`deploymentBlockHash`, `chainId`, `vault`, `owner`, and `signer` (grep `FIELDS = frozenset` in
`verifier/deployment.py`). **Selected deployment and compiler facts are signed; the complete
recipient-executed release is not.**

### 1.5 The deployment manifest has no expiry

New finding, 2026-08-30. `deployment.py` validates `issuedAt` as a canonical decimal and **never
compares it to anything** — grep `issuedAt` in that file returns two hits, both structural. A
signed manifest is therefore valid forever, with no revocation path. This is the "manifest lacks
a clear expiration/revocation mechanism" item from the Cycle 2 handoff, now measured.

### 1.6 The candidate mechanically custodies value

Relevant to any zero-VaR product decision (§2). In `contracts/src/SentinelVault.sol`: a `payable`
constructor, `receive() external payable {}`, `function recover(address payable to, ...)`, and
`action.target.call{value: action.valueWei}(callData)`. The cold demo deploys with `10n ** 18n`
wei and `PublicationWithdrawal.t.sol` runs `vm.deal(address(vault), 1 ether)`.

### 1.7 Suite figures

`forge test --root contracts` → **105/105**. `pytest verifier/test_verifier.py` → **221/221**. The
internal record is accurate. The release ships **2 of the 105** Foundry tests and **none** of the
221.

---

## 2. What is NOT required, so it is not rediscovered as work

- **A permanent versioned deployment registry is not binding.** A single immutable,
  independently authenticated deployment record satisfies the written Critical 1 condition.
- **The `AUTHENTIC_BUNDLE` / `EXECUTABLE_AT_BLOCK` / `EXECUTED` names are not binding.** The
  *semantic distinction* between static authenticity and live executability is required; the
  names are not.
- **Aggregate caps, signer epochs, minimum execution intervals and `recurringAllowed`
  enforcement are not automatic closure requirements.** They are What-Must-Be-True entries.
- **Git history rewriting is not entailed** by the fixture-key work. See R-A018-10.

**The derivative obligation that does attach.** A value-at-risk ceiling **cannot be declarative.**
If a non-zero exposure is set, something must enforce it, and the per-action ceiling demonstrably
does not — see the `@dev` header in `SentinelVault.sol` ("AGGREGATE LOSS", "EXECUTION RATE"). The
mechanisms above then return as binding *through the VaR clause*.

**On a zero-VaR product, recorded as an option and not proposed.** A product that never custodies
value would satisfy the clause mechanically. **It is not a labelling exercise, and the current
candidate contradicts it** — §1.6. The chairs' informal view is that it is a coherent product
("authorization router, not value custodian") **only if mechanically true**, which would require
at minimum: rejecting custody; requiring `valueWei == 0` or removing the native-value path; a
narrowly defined supported-action class; and bounding token, approval and administrative
authority — because **zero native value is not zero economic exposure.** A zero-value call can
still transfer tokens, grant approvals, exercise administrative authority, or change ownership
and policy. It would leave every other Critical 4 requirement untouched. **This is a product
decision and is John's.**

---

## 3. Work valid if the v0.3 enforcement/verifier architecture is retained

**Not "valid under every branch"** — a fresh casting could remove or redefine all of it. **None of
it is authorised by this register.** No item may be started without an instruction from John.

**Urgency note, corrected:** these are defects and false claims in the **local, unpushed
candidate**. There is no external exposure and no incident to respond to. See §0.1 and §6.

### R-A018-01 — Enforce the verdict `[CRITICAL 3, clause 4]`

~~`verify_publication.py` never reads `receipt["verdict"]`.~~ **Struck 2026-09-01: false of the tree since `8d47a0b`; see CLOSED below.** **Closes when** a non-`ALLOW` verdict
fails closed; a `REVIEW` receipt passes only through an explicitly modelled and authenticated
owner override, matching the Vault's `NotAllowVerdict` / `NotReviewVerdict`; and both arms have
negative tests.

**CLOSED 2026-08-30 at `8d47a0b`; closure marker added 2026-09-01** (the entry had described the
repaired defect in the present tense for two days). `check_verdict` reads the verdict, holds it to
the closed enum `{0=BLOCK, 1=REVIEW, 2=ALLOW}` and fails closed outside it rather than falling
through to an ALLOW comparison; the automatic path certifies ALLOW only; the override path
certifies REVIEW only and only alongside an authenticated `override.json`
(`check_owner_override`, examined on every path since D-083(c)); and a BLOCK receipt is refused
on both with a `FAIL:` naming `NotAllowVerdict` / `NotReviewVerdict`, matching the Vault. Observed
by `TestVerdictIsEnforced` in `verifier/test_publication_verifier.py`
(`test_a_signed_block_receipt_does_not_certify`, `test_the_shipped_block_fixture_does_not_certify`,
`test_an_out_of_range_verdict_does_not_certify`) and by the override suite. **Runnable in the
release since 2026-09-01 (D-085(f)):** the cold demo mints a BLOCK receipt per run with that run's
keys and requires four refusals — `executeWithReceipt` (`NotAllowVerdict()`), `executeWithOverride`
(`NotReviewVerdict()`), and the verifier on both `--execution-path` values.

### R-A018-02 — Remove the dead nonce check; add an authenticated-block nonce check `[CRITICAL 3, clause 4]`

~~The current check is `parse_uint("uint256", …) < 0` and **cannot fire.**~~ **CORRECTED
2026-08-30: that branch is DELETED, so this sentence is stale as a description of the tree.** Left
struck rather than removed — the closure condition below is still open, and a repair batch's own
register going stale about the code it repaired is precisely the failure §0 is about. The
implementing agent flagged it rather than editing a Crucible-facing document outside its scope,
which was the right call.

**Closes when** the dead branch is deleted ✅ **and** a certifying result checks the Vault's nonce
state **at a named, authenticated block** ❌ — the second half needs a chain and is carved out with
R-A018-04. The offline half landed: a non-certifying result now states plainly that it cannot
establish nonce freshness.

### R-A018-22 — Nothing verifies that `release/` matches source — NEW, and it is the cause of F1

The batch's most serious finding was that `release/verifier/` shipped the **pre-repair** verifier
while `MANIFEST.sha256` matched it perfectly — internally consistent, self-verifying, and wrong. A
recipient would have received a verifier that certifies the corpus's real prompt-injection BLOCK
bundle, beside a README advertising the repairs.

**The cause was mundane and will recur.** The assembler was re-run mid-batch, at a point when the
documentation repairs had landed and the verifier repairs had not. Nothing re-ran it afterwards,
and nothing anywhere would have noticed: `grep -n "release\|assemble" scripts/test.sh
.githooks/pre-commit` returns **nothing**. The release tree is a build artifact with no freshness
check, in a project whose entire discipline is mechanically-enforced guards.

**Closes when** a guard fails if `release/` is not what the assembler would currently produce —
cheap to write, since the assembler is already idempotent (a second run yields a byte-identical
`MANIFEST.sha256`).

**Note the shape.** `a38cff9` was defective because the reviewed thing and the shipped thing were
different. The repair batch reproduced that failure against itself, one level down, within hours.
That is an argument for the guard rather than for more care.

**PARTIALLY CLOSED 2026-08-30.** `scripts/check-release-sync.sh` written and proven: it assembles
into a temporary directory and compares, asserting the assembler's `OUT` still resolves to
`release/` and digesting `release/` before and after so the guard cannot mutate what it guards.
Demonstrated failing on the *original* defect — a pre-repair verifier with a regenerated matching
manifest — where manifest integrity alone passes and only the freshness pass catches it.
Companion `scripts/check-publication-suite-floors.sh` asserts "N pass AND exactly these named
reds", proven against four simultaneous mutations that left the red *count* unchanged.

### R-A018-23 — Neither new guard is wired into anything — NEW, and it is the other half of R-A018-22

`grep -n "release\|assemble" scripts/test.sh .githooks/pre-commit` still returns **nothing**.
R-A018-22's cause was *"nothing re-ran it and nothing would have noticed"*; a guard that exists but
runs in no gate closes the first half only. The guard author deliberately did not edit
`scripts/test.sh` — it is protected by `check-gate-immutability.sh`, which extracts a pinned
bootstrap from it — and supplied the two lines instead, to sit beside
`./scripts/check-suite-floors.sh || fail=1`:

```
./scripts/check-release-sync.sh || fail=1
./scripts/check-publication-suite-floors.sh || fail=1
```

**CLOSED 2026-08-30.** Both wired at `scripts/test.sh` — `check-release-sync.sh` in **both**
profiles (8.3s; placed after the Solidity stage, because the assembler reads an untracked Foundry
artifact and would otherwise `exit 2` "refused" on an unbuilt tree, and a refusal is not a check),
`check-publication-suite-floors.sh` under `--gate` only. A fast run now **prints both declarations
and any carried findings**, so it discloses what it did not check rather than being silent about a
deep-only guard. The register's own literal test — `grep -n "release\|assemble" scripts/test.sh
.githooks/pre-commit` — now returns 10 lines where it returned none.

**A premise in this entry was wrong and is corrected.** It said `scripts/test.sh` is digest-pinned
by `check-gate-immutability.sh`. **It is not.** That guard extracts the 171-line region between
`# >>> GATE BOOTSTRAP` and `# <<< GATE BOOTSTRAP` **fresh on every run** and exercises it against
synthetic subjects; no digest of `test.sh` is stored anywhere. What is protected is that region,
not the file, and the supervisor's `_gate_before`/`_gate_now` comparison is a within-run check
against mid-execution edits with no persisted baseline. The wiring went outside the protected
region, where every other guard step already lives; the bootstrap digest was identical before and
after, and `check-gate-immutability.sh` passes 10/10.

### R-A018-25 — THE GATE ABORTS SILENTLY ON ITS OWN FAILURE PATH — NEW, and it is the worst of these

Found 2026-08-30 by the guard-wiring agent, verified independently. **A failure branch of
`scripts/test.sh` kills the gate before it can record the failure, and skips every stage after it.**

`scripts/test.sh:12` sets `set -euo pipefail`. Line 735, inside the corpus `DIGEST MISMATCH`
branch, is:

```sh
diff "$CORPUS_TMP/.../_digests.json" fixtures/corpus/.../_digests.json | head -20
fail=1
```

When the digests differ — which is the only way to reach this line — `diff` exits 1, `pipefail`
propagates it, `set -e` aborts, and **`fail=1` on the next line never runs.** The §7.3 ablation and
the D-010 verifier stages that follow never execute. The same shape is at line 831 for the
ablation-report diff.

**Why this is the worst finding of the batch.** Every other defect here was a check that did not
exist or a claim stronger than its evidence. This one is a check that *fires correctly*, prints its
diagnosis, and then destroys the run's ability to report it. It is this project's own recorded
failure mode — *a probe that is dead and whose silence reads like a pass* — **on the gate's own
failure path**, where it is hardest to notice, because you only reach it when something is already
wrong.

**The only reason it surfaced as `exit 5` rather than a silent stop is the supervisor's
completion-token check** (`scripts/test.sh:1332`, "Anything that stops the body before here … a
`set -e` abort …"). That defence was written for exactly this and it worked. It is the last line,
not the first.

**FIXED 2026-08-30 at John's ruling, D-084(a)** — `|| true` on both `diff` lines. **Verified by
evidence, not by reading:** two full deep-gate runs differing only in whether the `|| true` at
`:735` was present gave 20 stages vs 18, with `§7.3 ablation` and `D-010 receipt verifier` present
in one and **absent** in the other, `GATE FAILED` printed in one and not the other — and **the
supervisor exit status identical at 5 in both.** A caller reading exit codes alone cannot
distinguish "the gate failed and said so" from "the gate died mid-run and skipped two stages".
That row is R-A018-25 stated once.

**A THIRD INSTANCE EXISTS, IS NOT FIXED, AND IS RESERVED TO JOHN.** `scripts/test.sh:945`:
`v_modes="$(… | grep -oE 'the mutated [a-z-]+' | … )"`. `grep -oE` is a non-final pipeline segment
with `pipefail` on, so if the verifier ever stops printing those lines — **precisely the regression
the tamper-mode floor eight lines below exists to catch** — the substitution fails, `set -e`
aborts, and `FLOOR BREACHED — tamper modes` never prints. **Line `:944` directly above already ends
in `|| true`**, so the class was known and this one was missed. Carried on
`scripts/check-gate-abort-safety.sh`'s ratchet and printed every run, so it cannot go quiet.

**AND THE "EXACTLY TWO INSTANCES" FIGURE IN D-084(a) WAS WRONG — the agent's error, corrected in
`docs/decisions.md`.** `grep -cE '^\s+(diff|grep|cmp|comm)\b'` is anchored to statement start and
**structurally cannot see** a command inside `$( )` or mid-pipeline; unanchored the same file has 8
candidates. A number true only of the probe, reported as a property of the tree, inside a ruling
about a probe whose silence read like a pass.

**GUARDED 2026-08-30** by `scripts/check-gate-abort-safety.sh`, wired in both profiles. It builds
18 synthetic subjects and **runs each under this machine's bash on every invocation**, requiring
its classifier to agree shape-for-shape, so a changed shell or a regressed lexer makes it *refuse*
rather than print green. It refuses on backticks and `set +e` regions rather than analysing what it
did not establish, and records two measured widenings it rejected — with the numbers — so nobody
redoes them.

### R-A018-24 — A pass-count floor cannot see a vacuous test — NEW

The floors guard asserts pass count and the exact red set. **Neither moved during the entire F7
defect**: three tests were green and asserting nothing for hours, and both numbers were correct
throughout. This is this project's own recorded failure mode — *a probe that is dead and whose
silence reads like a pass* — reappearing in the instrument built to prevent it.

The test author found them by instrumenting a full run (`sys.settrace` + AST, since `coverage` is
not installed here) rather than by reading. That probe is at
`scratchpad/vacuity_probe.py` and **is worth promoting to a guard**: a test whose body never
executes, or whose assertion cannot fail, is invisible to every instrument this project currently
runs.

Corroborating: one repaired test's `assertIn("evaluation-time", stdout)` was *defeatable* because
argparse reprints the module docstring, which mentions the flag in prose — so it passed with the
flag fully suppressed. The test author's own first draft had the identical hole. **The mutation
pass caught it; reading did not.**

**CLOSED 2026-08-30** by `scripts/check-test-vacuity.sh`, wired under `--gate`. It catches six
decidable classes — a `test_*` never invoked; a passing test whose body executed no statement; a
passing test in which no assertion executed; an assertion in a block never entered (**the exact
shape of the F7 defect**); a test with no assertion at all; a `def` shadowed by a later `def`; and
an assertion whose compared arguments are all literal constants.

**Its limits are printed on every run, which is the point.** An assertion that executes and is
merely *weak* is invisible to it — the `assertIn("evaluation-time", …)` case above is named in the
guard's own output as a class it does **not** catch, reachable only by `scripts/mutate.sh`. Also
excluded: vacuity inside a red, errored or skipped test (a failing test legitimately stops early —
the exclusion count is printed), and "cannot fail" in general, which is undecidable. **A guard
that overstates its reach is the defect this project keeps finding; this one states what it
misses.**

**Two real dead assertions found on its first run**, both in `verifier/test_verifier.py`, both
carried on a per-check ratchet rather than fixed, because the guard's author may not edit a test
file: `TestUnassertedValidation.test_pair_aligned_whitespace_cannot_collide_an_encoded_word` (a
`continue` fires and the trailing `assertNotEqual` is unreachable — **the test's own comment
records that its first version had the same defect**), and
`TestJCSStructure.test_key_sorting_is_utf16_code_units` (`assertGreater` over two literals — a
comment written as an assertion). **Owed to someone permitted to edit tests.**

### Two smaller items left by the F7 repair

- **`verify_publication.py`'s `KNOWN RED TESTS` block is stale, and its staleness was
  load-bearing.** It records that one test "now passes, but incidentally". That parenthesis *is*
  the declaration that let a vacuous test stand. The test now passes for a real reason. The
  "77/81 expected" line above it remains accurate. A test author cannot edit that file; someone
  permitted to should. **DONE 2026-08-30 under D-083(j).** The block was rewritten: 77/81 was
  re-derived by running the suite rather than assumed; the fourth `TestDeploymentIdentityIsNotBound`
  test is now recorded as green *for a reason*, with the incidental-pass parenthesis and what it
  cost kept as the lesson rather than deleted; R-A018-17's entry is re-labelled ruled-disclosed-only
  per D-083(b); and the override suite's expected state (61/61, no deliberate reds, per D-083(c))
  is declared there too, since that file previously carried no record of its own.
- **`test_a_superseded_manifest_cannot_certify_after_signer_rotation` passes for a weaker reason
  than its name claims.** Its rotated manifest is built, self-asserted, and never presented to the
  predicate; what is actually exercised is the 90-day lifetime bound. Left alone deliberately — a
  real rotation test needs an authenticated revocation source and would go red, breaching both the
  four-deliberate-reds constraint and the floors guard's declared set. **Recorded so the name is
  not later mistaken for coverage.**

**Responsibility split, corrected:** an offline verifier **cannot consume** the on-chain nonce.
The Vault consumes it atomically at execution; the verifier can only observe it at an
authenticated block. Any offline-only mode must state it cannot establish nonce freshness and
must not print "current receipt."

### R-A018-03 — Bind executability to a trusted time source `[CRITICAL 3, clause 2]`

~~`--evaluation-time` is registered with `help=argparse.SUPPRESS`.~~ **Struck 2026-09-01: false of the tree since `8d47a0b`; see CLOSED below.** **"Non-overridable clock" is
underspecified** — the operating-system clock is also caller-controlled. **Closes when**
executability uses an **authenticated block timestamp or another explicitly trusted time
source**; injected time survives only in a non-certifying test mode that cannot produce a
certifying result; and a "refused clock override" negative test exists.

**CLOSED 2026-08-30 at `8d47a0b` on the condition as re-scoped by D-086(e); marker added
2026-09-01.** What landed: `--evaluation-time` is documented in `--help` and the module docstring
as NON-CERTIFYING TEST MODE; a run under it reports its findings and exits 3, which the module
docstring, `docs/enforcement-release-v0.3.md` and the release README all name; without the flag
the instant is the host clock, the result says so in `evaluationTimeSource`, and "a trusted time
source" is listed under `NOT ESTABLISHED` beside every certifying result. Observed by
`TestClockIsNotTheCallers` (`test_an_injected_clock_cannot_produce_a_certifying_result`,
`test_an_injected_clock_cannot_revive_an_expired_receipt`,
`test_the_clock_control_is_not_concealed_from_the_help_text`). **What did NOT land, and is not
claimed by this marker:** an authenticated block timestamp. The first clause of the closure
condition was re-scoped by John at D-086(e) — Binding Critical 2 closes by the
non-certifying-static route, *"the result stop claiming properties it did not authenticate"*, and
live RPC is NOT AUTHORISED. The module-level `deployment.verify(evaluation_time=None)` default,
held at D-083(d) and released by D-086, is the verifier implementer's item in the D-087 batch and
is not closed here.

### R-A018-04 — Bind deployment identity to live chain state `[CRITICAL 3, clause 3; CRITICAL 1]`

Neither module performs any RPC. ~~A fabricated `runtimeCodeHash` is reported as authenticated
(§1.1).~~ **Struck 2026-09-01 — false of the tree since the D-087 batch, under D-086(e).** The
value now travels inside `unverifiedAuthorityAssertions` in the result payload and appears in no
headline; the certifying line and `NOT ESTABLISHED` disclaim deployment identity, currentness and
executability on chain by name. **That is the claim corrected, not the binding built:** D-086(e)
ruled Binding Critical 2 closed by the non-certifying-static route — *"what is mandatory is that
the result stop claiming properties it did not authenticate"* — with live RPC NOT AUTHORISED.
**The three deliberate reds of `TestDeploymentIdentityIsNotBound` were REDEFINED, not closed by
chain binding:** each had asserted a chain binding, i.e. the route that is now ruled out, so each
was rewritten to observe the *claim* instead (the fabricated hash is never presented as an
authenticated fact; two contradictory manifests both authenticate statically and neither claims
deployment identity; no claim is anchored to a block and executability is stated as not
established). All three fail on `2115c4f` and are green-able under the ruling; none is a
chain-binding test any more. **Closes when** the recorded runtime code hash is compared against
live deployed bytecode or an authenticated state proof at a named block, and results distinguish
static authenticity from executability at a named block — **which remains OPEN and is not
authorised**; this item is the first `NOT ESTABLISHED` entry and stays there.

### R-A018-05 — Implement the missing predicate checks `[CRITICAL 3, clause 5]` — NEW

The first version listed negative *tests* for target, value, selector, operation, policy expiry
and code identity but **no item required implementing those checks** in the shipped predicate.
~~The verifier currently compares none of them against mandate or policy.~~ **Struck 2026-09-01: false of the tree since `8d47a0b`; see CLOSED below.** **Closes when** the
shipped predicate enforces exact target, value, selector, operation, policy validity, and code
identity where relevant.

**CLOSED 2026-08-30 at `8d47a0b` for the fields that can be compared offline; marker added
2026-09-01.** `check_exact_action` compares the action's target and selector to the mandate, its
`valueWei` to both the mandate's and the policy's ceilings, its `operation` to the policy's
`allowedOperation`, and the policy's `validAfter`/`validUntil` at the evaluation instant;
`TestExactActionIsEnforced` observes each. **Carved out, not closed here:** code identity —
authenticated as an authority assertion and compared to no chain (R-A018-04, open, first
`NOT ESTABLISHED` entry); the calldata's arguments — ruled disclosed-only (D-083(b), R-A018-17);
and the policy's hash-bound lists (`allowedTargetsHash`, `allowedSelectorsHash`,
`allowedCallGraphHash`), whose contents do not ship and are disclosed in the release README. The
four Vault-axis items the 2026-08-31 inventory diff added — `operation == CALL` enforced
unconditionally on both offline verifiers, and the three §4 hard backstops disclosed in
`NOT ESTABLISHED` — are in the D-087(a) batch and are not claimed by this marker.

### R-A018-06 — Test the two uncovered modules `[CRITICAL 3, clause 5]`

**Closes when** `verify_publication.py` and `deployment.py` have direct adversarial coverage on
the pattern in `verifier/test_verifier.py`. For `deployment.py` specifically, hostile coverage
must include **authority selection, wrong-authority refusal, canonicalization, stale deployment
records (§1.5), rotation and revocation, chain/block/code binding, and deployment
configuration** — not merely malformed JSON.

Minimum negative set for the predicate: unapproved signer, absent mandate proof, future and
expired mandate and receipt, consumed nonce, `BLOCK`, `REVIEW` without override, wrong chain,
wrong Vault, wrong target, wrong value, wrong selector, altered calldata, expired policy,
substituted deployment identity, changed target code, stale state proof, refused clock override.

### R-A018-07 — Authenticate the whole release, and bootstrap that check `[CRITICAL 1]`

The recipient's verifier, the TypeScript runtime and `package-lock.json` sit outside the
authority signature, and `MANIFEST.sha256` is itself unsigned.

**The bootstrap requirement, which the first version missed:** the complete release digest must
be verified **before executing the release's own verifier**, or a substituted verifier attests to
itself. This needs an external standard signature/digest tool or a separately bootstrapped one.

**Closes when** the authority signature binds the full release digest and the candidate commit,
and the digest check runs from outside the release.

### R-A018-08 — Correct every overstated claim `[CRITICAL 2; CRITICAL 3]`

| Location | Claim | Problem |
|---|---|---|
| `release/README.md` | "No private key or fixed private-key fixture is included" | Absence claim a denylist cannot make (§1.3) |
| `release/README.md` | "…policy, and nonce commitments" | The nonce check cannot fire; policy is hash-bound, not enforced |
| `verify_publication.py` | `PASS: … and current receipt` | Survives a caller-chosen clock and a BLOCK verdict |
| `a38cff9` commit subject | "publication-ready Sentinel enforcement" | Stronger than the contract's own `@dev` header |
| `docs/enforcement-release-v0.3.md` | "Signer rotation revokes the active mandate" | True of the *mandate*; reads as a claim about *receipts* that `SentinelVault.sol`'s own correction note contradicts |

**~~Branch-dependent, and must not be batched with the rest: the drain-boundary disclosure.~~
UNBLOCKED 2026-08-30 — the Smith ruled custody RETAINED with the boundary disclosed
reader-facing.** The hold existed because a mechanically zero-custody product would need different
wording; that option was considered and rejected. The disclosure is now in scope and was
implemented. **This register was committed before that ruling and said otherwise for several
hours** — the implementing agent hit the contradiction, flagged it rather than silently picking,
and kept the disclosure in two self-contained sections so it reverts as single hunks. Recorded
because a stale instruction that an agent obeys is worse than one it questions.

### R-A018-09 — Type the cold demo's negative controls `[CRITICAL 1]`

~~`mustReject` in `ts/src/tools/cold-demo.ts` uses a bare `catch` and scores **any** exception as
`PASS negative`.~~ **Struck 2026-09-01: false of the tree since `8d47a0b`; see CLOSED below.** **Closes when** each negative asserts its expected error selector, exit
classification and failure stage.

**CLOSED 2026-08-30 at `8d47a0b`; marker added 2026-09-01.** `mustReject` is gone.
`mustRevertWith` asserts stage = vault-execution, class = evm-revert and identity = a custom-error
selector computed locally from the signature (not read back from the ABI, so one wrong build cannot
satisfy both sides); `mustRefuseVerification` asserts stage = publication-verifier, the exit
status, no traceback, no `PASS:` on stdout, and a matched `FAIL:` line. Anything else is a
`NegativeControlFailure` and the demo fails. R-A018-15's chain-clock alignment closed the drift
that made the bare catch dangerous. **Extended 2026-09-01 under D-085(f):** four BLOCK-receipt
negatives on the same machinery — both Vault entry points, both verifier paths — with the
`NotReviewVerdict()` control deliberately presenting a zeroed override so that the selector proves
the verdict check fired before the Vault read the credential.

### R-A018-10 — Stop the demo presenting its own key as out-of-band `[CRITICAL 2]` — NEW

~~`cold-demo.ts` generates `authorityKey`, signs the manifest with it, and prints that same address
as `Deployment authority (obtain out of band)`.~~ **Struck 2026-09-01: false of the tree since `8d47a0b`; see CLOSED below.** **Closes when** lab-generated authority is
labelled unmistakably non-production and the demo does not present a self-generated address as an
out-of-band trust root.

**CLOSED 2026-08-30 at `8d47a0b`; marker added 2026-09-01.** The key is `labAuthorityKey`, named
for the caveat; the demo prints a `NOTE` before the verifier runs that the verification is a
self-consistency loop and not an independent authentication, and closes with a
`LAB-GENERATED DEPLOYMENT AUTHORITY -- NOT PRODUCTION, NOT A TRUST ROOT` block. The generated
`release/README.md` carries the same statement under "The demo generates its own deployment
authority", and `docs/enforcement-release-v0.3.md` says it once more. Git history is untouched,
per §2 and R-A018-12. The 2026-09-01 BLOCK case reuses the same per-run keys and ships no fixture,
for the reason this item records.

### R-A018-11 — Resolve the v0.2 envelope tag on v0.3 material `[CRITICAL 2]` — NEW

`release/ts/src/evaluate/index.ts` emits `schema: "sentinel.evidence.v0.2"` in the v0.3
enforcement release. **D-075 deliberately froze the schema tags**, so this is not an accidental
regression — but a recipient of a v0.3 release reading v0.2-tagged evidence has a comprehension
problem regardless of why the tag is stable. **Closes when** the divergence is either resolved or
disclosed reader-facing. **Changing a schema tag touches signature preimages and is not an
architect's call.**

### R-A018-12 — Make fixture separation structural `[CRITICAL 2]`

The guard is a denylist. The three fixed-key tools are `ts/src/tools/sample-check.ts`,
`ts/src/tools/emit-samples.ts`, `ts/src/corpus/run.ts`.

**Closes when** current tools generate ephemeral keys per run, frozen historical fixtures stay
quarantined and reproducible, and lab and production authority domains are structurally distinct.

**On history:** annotation does **not** remove old keys if full git history is publicly
distributed. The least destructive answer is a **history-free publication export**. **Do not
rewrite history** — that depends on the venue ruling in §4.

### THE PATTERN IS NOT WHAT THIS SECTION SAID — SUPERSEDED 2026-08-31 by the inventory diff

**Read `docs/check-inventory-diff-2026-08-31.md` instead of this section.** The "four faces" (and
later "six faces") framing below was a sample, not the class. Measured mechanically under D-085(e):
**54 of `verify.py`'s 95 checks are absent from the publication verifier with no recorded reason —
zero deliberate — plus 4 Vault conditions neither offline verifier enforces, plus the inverse
direction nobody had looked at: `verify.py` has no clock and certifies a receipt that expired
2026-08-28.** The class is a **scope truncation** — `a38cff9` rebuilt the surface around "would the
Vault execute this?" and dropped every check answering "does this bundle describe what it says?"
— not a list of dropped disciplines. The honest count is **54 + 4 + 4, not 6.** The section below is
kept as the record of how the shape was first seen and why one-at-a-time could never have found it.

### THE PATTERN — four faces of one omission, and it is the most useful thing this batch found

Recorded above the individual items because reading them as four separate defects loses the
finding. Every one has the same shape: **a discipline the pre-`a38cff9` verification surface had
accumulated, which the surface `a38cff9` added does not have.**

| # | The discipline | Where it lives | Where it is absent |
|---|---|---|---|
| 1 | Adversarial test coverage | every verifier module predating `a38cff9` | `verify_publication.py`, `deployment.py` — §1.2 |
| 2 | EIP-2 low-s canonical signatures | `verify.py`, receipt + refusal record | all three new signature checks — R-A018-16(a) |
| 3 | Examine an override credential whenever one is present | `verify.py::_override_checks`, called unconditionally at its check list | `check_owner_override`, gated behind the override path — R-A018-18, **CLOSED** |
| 4 | Name the artifact a refusal is about | `deployment.py` after R-A018-16(c) | the override arm, twenty lines away — R-A018-20 |

**This is not four bugs. It is one omission with four faces:** `a38cff9` rebuilt the verification
surface fresh rather than deriving it from the reviewed one, so none of the discipline three
adversarial review rounds had deposited in `verify.py` came across. The count matters — one
instance is an oversight, four is a method failure — and it is the sharpest available answer to
*why* the publication surface was defective, as against *how*.

**It belongs in the new Ingot's §1.2 framing**, which currently argues the boundary from test
coverage alone. Coverage is the symptom the count makes visible; the omission is the cause.

**Corollary for whoever finishes this batch:** stop finding these one at a time. The remaining work
is a systematic diff of `verify.py`'s check inventory against the new modules', asking of each
check "does the new surface do this, and if not, why not?" That is the same instruction the Cycle 2
handoff gave under a different name — one versioned executable predicate, shared conformance
vectors — reached from the other direction.

### R-A018-18 — An unexamined §5.5 credential rides inside a PASS — NEW

Found 2026-08-30 by the independent override test author, verified. `check_owner_override()` runs
**only** on the override path (`verify_publication.py`, gated behind `execution_path ==
OVERRIDE_PATH`). So an ALLOW bundle carrying a genuine, correctly-bound, **outsider-signed**
`override.json` certifies on the automatic path with that file never opened.

**Both other implementations refuse it.** The Vault: `executeWithReceipt` takes no override
parameter and `executeWithOverride` reverts `NotReviewVerdict` on an ALLOW receipt, so the
credential is executable at neither entry point. `verify.py`: `_override_checks` is in the
unconditional check list and refuses this exact bundle with *"override targets a REVIEW receipt,
not a BLOCK (§5.5)"* — reproduced.

This is **D-052(b) / A-059 reintroduced**: *"Nothing on this path examines the override, so
accepting it would certify a §5.5 credential that was never verified."* The finding was made once,
fixed once, and lost in the rewrite.

**Closes when** an override credential is either examined on every path or refused as a shape that
cannot be certified. **Which of the two is a scope decision and is John's** — the test author
correctly declined to pick.

**RULED AND CLOSED 2026-08-30. John took the first option at D-083(c): an override credential is
EXAMINED ON EVERY PATH**, matching `verify.py::_override_checks`. Implemented in
`verifier/verify_publication.py`: `verify()` now calls `check_owner_override` when the caller
declares the override path **or** the bundle carries an `override.json`, and that function opens
with the §5.5 pairing check — the receipt a credential authorises must be REVIEW. An ALLOW bundle
carrying an override is refused with *"override.json is present, but the receipt it authorises is
ALLOW, not REVIEW"*, naming §5.5, both Vault entry points and R-A018-18.

**Where the implementation deliberately departs from the house pattern, and why.** `_override_checks`
accumulates every check and reports them together, so its ordering carries no information; this
module refuses at the first failure, so ordering *is* the diagnosis. The §5.5 pairing check is
therefore FIRST here and last there. Authenticating first would answer an outsider-signed
credential on an ALLOW bundle with an `ownerAddress` mismatch — true, and the wrong repair to send
a recipient after, because a correct owner would not make that bundle certifiable either. That is
R-A018-16(c)'s discipline applied to a pairing rather than to a field.

**Measured after the repair:** `verifier/test_publication_override.py` 61/61, with no deliberate
reds left in that file; `verifier/test_publication_verifier.py` unchanged at 77/81;
`verifier/test_verifier.py` 221/221. `scripts/check-publication-suite-floors.sh` now FAILS until
its declaration is moved to floor 61 with both R-A018-18 RED lines removed — the guard behaving
exactly as designed, since it cannot tell an authorised closure from unauthorised work.

### R-A018-19 — A certifying override run does not say it was an override — NEW

~~The override arm prints the automatic arm's PASS headline verbatim.~~ **Struck 2026-09-01: false of the tree since `8d47a0b`; see CLOSED below.** Nothing in it was false; it
omits the entire reason the run passed, so *"the machine approved this"* and *"a human was asked
and signed"* are indistinguishable outside the JSON. The result object does carry `executionPath`
and `ownerOverrideHash`.

**The Vault holds the opposite position explicitly.** It splits the two into separate functions,
sets `viaOverride: true`, and under **D-043** emits a dedicated `OverrideAuthorized` event carrying
the override hash and the owner's `reasonHash` — precisely because `viaOverride` alone was ruled
insufficient for an auditor. §3.3(2) singles out override as the thing that must be **logged**.

An R-A018-08-shaped claim defect: the headline is weaker than the evidence in the one direction
that matters for comprehension.

**CLOSED 2026-08-30 at `8d47a0b`; marker added 2026-09-01.** The override arm's headline is
`PASS (static, offline) BY AUTHENTICATED OWNER OVERRIDE, NOT AUTOMATICALLY: …`, and it says that
the signer's decision was REVIEW, that the Vault refuses that receipt at `executeWithReceipt`, and
that a separate owner-signed override naming this exact receipt, action and nonce was
authenticated and recovers to the owner rather than the signer. Both reader-facing surfaces —
the generated `release/README.md` and `docs/enforcement-release-v0.3.md` — state that a certifying
override run says so in its headline. Verified by reading `verify_publication.main` at HEAD; the
JSON's `executionPath` and `ownerOverrideHash` were already present and are unchanged. ~~No test is
cited because the implementer found none that asserts on the headline text; recorded as a blind
spot rather than claimed.~~ **Corrected 2026-09-01 by independent verification: one exists and
asserts on it —
`verifier/test_publication_override.py::TestTheCertifyingRunSaysWhichPathItCertified.test_the_certifying_headline_names_the_owner_override`.
The implementer grepped the wrong file.**

### R-A018-20 — R-A018-16(c)'s diagnosis discipline was not carried into the override arm — NEW

Both bundles are correctly *refused*; what the recipient is told is wrong. A missing override
binding escapes as a bare `KeyError` — at the CLI, `FAIL: 'reviewReceiptHash'`, naming no file, no
artifact, no §5.5. A non-canonical `issuedAt` escapes as an unattributed encoder error, though the
receipt, mandate, policy and action all carry uint64 time fields too.

`check_verdict`, added in the same batch twenty lines away, does this correctly, and
`mandate-signature.json` gets an explicit shape check while `override.json` gets none.

**A THIRD FACE, found while fixing the first two.** The item named two symptoms; there were three.
`schemaVersion`, `reasonHash` and two other fields were not indexed early, so they reached
`eip712.override_digest` from *inside* the try/except that wraps everything as a signature failure.
Measured before the fix: a missing `reasonHash` produced `owner override signature verification
failed: OverrideAuthorizationPayload is missing required field 'reasonHash'`. **That is R-A018-16(c)
verbatim, in a third location** — a field error reported as a signature error, sending a recipient
to re-check an owner signature that was fine.

So the §THE PATTERN table above undercounts: the diagnosis discipline was absent in `deployment.py`,
in the override arm's explicit checks, *and* in the override arm's implicit ones. **Three faces of
face #4.** The corollary stands and hardens — stop finding these one at a time; diff `verify.py`'s
check inventory against the new modules systematically.

**CLOSED 2026-08-30.** Fixed by deriving the closed nine-field set from `eip712.OVERRIDE_FIELDS`
rather than restating it, so it cannot drift from what is actually hashed. Both
`TestOverrideRefusalsAreDiagnosed` tests green; the override suite went 4 failures → 2, and the 2
remaining were R-A018-18 — **since ruled at D-083(c) and closed, taking that file to 61/61.**

**One stale docstring left for a test author, deliberately not edited by the implementer.** In
`verifier/test_publication_override.py`, `test_an_under_or_over_determined_override_payload_is_refused`
says its cases are refused by `eip712.struct_hash` and that `reasonHash`/`schemaVersion` "reach the
hasher". They are now refused earlier, by the new shape check. The test still passes and its claim
about *behaviour* is still true; only its account of *which code refuses* has moved. The
implementer flagged it rather than editing a frozen contract — correct under D-058(1).

### R-A018-16 — The new modules dropped three disciplines the old verifier kept — NEW

Found 2026-08-30 by the independent test author, verified. **The same structural story as §1.2: a
rule every pre-`a38cff9` surface follows, that everything `a38cff9` added skipped.**

**(a) ~~EIP-2 low-s is enforced on none of the three signatures.~~** **Struck 2026-09-01: false of the tree since `8d47a0b`; see CLOSED below.** `is_low_s` ships in the shared
`verifier/secp256k1.py` and `verify.py` applies it to the receipt *and* the refusal record — grep
`signature is EIP-2 canonical` there. `grep -n low_s verifier/verify_publication.py
verifier/deployment.py` returns **nothing**. Demonstrated: `(r, N−s, v^1)` on a manifest signature
is accepted, so one authority decision has two byte-distinct valid documents and any later
revoke-or-pin-by-digest scheme is evadable.

**(b) ~~`issuedAt` is unbounded above.~~** **Struck 2026-09-01: false of the tree since `8d47a0b`; see CLOSED below.** §1.5 records that it is never compared to now; `_uint` also
imposes no ceiling, so `"1" + "0"*40` is accepted. A lifetime bound that only looks backwards is
survived by post-dating, so both directions need asserting.

**(c) ~~Field errors are reported as signature errors.~~** **Struck 2026-09-01: false of the tree since `8d47a0b`; see CLOSED below.** `deployment.verify()` calls `digest()`,
which validates, *inside* the `try` that catches `ValueError` — so a leading zero surfaces as
`deployment authority signature is invalid: issuedAt has a leading zero`. The refusal is correct
and the diagnosis is wrong, and it sends a recipient to re-check the one thing that was fine. In a
tool whose value is unaided comprehension that is an inherited-Critical-2 concern, not cosmetics.

**Closes when** all three are corrected and the corresponding tests in
`verifier/test_publication_verifier.py` pass.

**CLOSED 2026-08-30 at `8d47a0b`; marker added 2026-09-01.** (a) `is_low_s` with `v in {27, 28}`
is held on the deployment authority signature (`deployment._check_signature_form`) and on the
mandate owner and receipt signer signatures (`verify_publication.check_signature_form`);
`TestDeploymentSignatureCanonicalForm`. (b) `UINT_CEILINGS` caps `issuedAt` at uint64 and
`check_lifetime` compares it in both directions, refusing a post-dated manifest and one older than
`MAX_MANIFEST_AGE_SECONDS` (90 days, ratified D-083(e), whose unguarded drift is recorded there);
`TestDeploymentManifestLifetime`. (c) `validate_payload` runs outside the `try` that catches
signature failures; `TestDeploymentDiagnostics.test_a_field_error_is_not_reported_as_a_signature_error`.
The override arm's third face of (c) is R-A018-20, closed separately. The absence of an
authenticated revocation source — so that `check_lifetime` is a lifetime bound and not a
revocation check — is disclosed in `deployment.py`'s docstring and, since 2026-09-01, in the
release README's limits.

### R-A018-17 — Calldata can redirect the mandated beneficiary — RULED DISCLOSED-ONLY (D-083(b))

Found 2026-08-30 by the independent test author. With target, selector, value and operation left
exactly as mandated, swapping only the beneficiary word inside `callData` produces a fully
authentic, internally consistent bundle that **certifies under a banner reading "exact action."**

**Neither downstream check catches it.** The verifier compares `dataHash` to the bytes supplied and
never decodes them; the Vault binds `keccak256(callData)` and target/selector/value but likewise
never decodes. Only the isolated signer's evaluator checks the decoded beneficiary
(`EVAL_PURCHASE_BENEFICIARY`). So beneficiary binding rests entirely on the signer behaving
correctly, with no independent check anywhere downstream — which is precisely the assumption the
Vault exists to avoid having to make.

**Deliberately NOT folded into R-A018-05.** Enforcing it means decoding calldata against the
mandated selector inside the verifier, which is new capability and a scope decision. It may also be
the correct reading that this is by design — the signer decodes semantics, the Vault binds bytes.
**Recorded for John. The build team must not resolve it.**

**RULED 2026-08-30 — DISCLOSED-ONLY, NO ENFORCEMENT (D-083(b)).** The signer's evaluator decodes
semantics; the Vault binds bytes; the verifier now says plainly that it decodes nothing. This is a
RULING, not a deferral: there is no pending decision behind it and no queued v1.1 item.
`TestExactActionIsEnforced.test_calldata_redirecting_the_mandated_beneficiary_is_refused` is
therefore **permanently red by ruling**, and every place that declares or explains that red now
says "ruled disclosed-only at D-083(b)" rather than "reserved to John".

**THE COST, RECORDED WITH THE RULING RATHER THAN ARGUED AWAY:** ~~beneficiary binding rests entirely
on the isolated signer behaving correctly, with **no independent downstream check** — which is the
assumption the Vault exists so as not to have to make.~~ **Corrected 2026-09-01, twice over.** First,
the 2026-08-31 CORRECTION TO D-083(b) in `docs/decisions.md` measured that `verify.py` DOES re-check
the beneficiary — `_allow_conforms_to_the_mandate` compares the signer's *attested decoded record*
against the mandate for `resourceId`, `beneficiary`, `durationSeconds`, `recurringAllowed`,
`spender` and the allowance ceiling, without decoding calldata — so "no independent downstream
check" was the fourth measured claim the agent supplied at a moment of decision that did not hold.
Second, the D-087 batch ported that check into the publication verifier under the name
**"signer-attested record conforms to mandate"** (`CONFORMANCE_CHECK_NAME`,
`verifier/verify_publication.py`, D-087(b)). The honest statement of the cost is therefore: the
verifier checks the signer's *record* against the mandate, not the *bytes*, so it catches a
misconfigured-but-honest evaluator and not a lying signer; no downstream consumer decodes
calldata, and by ruling none will. The ruling itself is unchanged. ~~The disclosure that carries it
is the fourth `NOT_ESTABLISHED` entry~~ **It is the seventh `NOT_ESTABLISHED` entry at HEAD (the
list grew to eight in this batch; the eighth is the attested-record check's own limit)** in
`verifier/verify_publication.py`, printed beside every certifying result, plus the same statement
in the module docstring and in `check_exact_action`.

### R-A018-14 — The policy commits to a token-allowance ceiling the Vault never enforces — NEW

Found 2026-08-30 by the implementing agent, verified independently. `maxAllowanceIncreaseBaseUnits`
is a field of the signed `PolicyPayload` — it is in the struct at
`contracts/src/types/SentinelTypes.sol`, in the EIP-712 type string, and inside the policy hash —
**but `grep -n allowance contracts/src/SentinelVault.sol` returns nothing.** The Vault never reads
it. One ALLOW receipt for `approve(spender, max)` on an allowlisted target hands over an entire
token balance within a policy that appears to cap exactly that.

**Why this is worse than an ordinary undisclosed limit, and why it belongs to inherited Critical 2
rather than to the backlog:** a reader who sees `maxAllowanceIncreaseBaseUnits` in the signed
policy type can reasonably conclude an allowance ceiling is enforced. The schema itself is the
misleading surface. That is a comprehension defect, not only a capability gap.

It is ratified and deferred — D-042(b), D-051(a), v1.1 — and asserted by
`test_LIMIT_vaultCapsNativeValueOnlyAndNotTokenAuthority` in
`contracts/test/SentinelVault.backstops.t.sol`. **Nothing about it is disclosed reader-facing**,
and the R-A018-08 disclosure just landed covers only the native-value half of the same class.

**Also load-bearing on a ruling already taken.** The custody decision rejected a zero-VaR product
on the grounds that *zero native value is not zero economic exposure*. This is that exposure,
concretely, in the shipped schema.

**CLOSED 2026-08-30 as a disclosure-only repair, under D-082(a).** Disclosed reader-facing in both
the v0.3 doc and the generated README, alongside the drain boundary and in the same voice.

**Two corrections to this entry's own earlier wording, both measured:**

- **It was never undisclosed *internally*.** `Sentinel_Lab_Proposal_v0_2.md` §7.1 states it at
  length (4 occurrences of the field name). The true gap was narrower and is what the disclosure
  now says: **neither §7.1 nor the pinning test travels with a release**, so a recipient meets the
  ceiling in the signed policy type and nothing that ships tells them it is unenforced.
- **The cap is not merely "out of scope" — it is a ratified commitment, deferred.**
  `docs/v1-1-register.md` §5 owes "a per-action allowance-increase ceiling in the vault" by name.
  A draft line saying "no cap is promised" was removed before it shipped, because it would have
  contradicted that commitment. **D-053(a) withdrew the cumulative/rate ceiling, not the token
  cap.** Building it in this batch remains unauthorised and would be a scope upgrade under the new
  Ingot's kill criterion 4 — but the reason is sequencing, not that nothing is owed.

### R-A018-15 — The cold demo's positive control is intermittently a false negative — NEW

Reported 2026-08-30 by the implementing agent. **~~NOT yet independently reproduced~~ —
INDEPENDENTLY REPRODUCED the same day; that caveat is lifted.** The demo's *positive* execution
reverts `ReceiptNotYetValid()` because Anvil advances block timestamps per block while the
receipt's `issuedAt` is wall-clock (`ts/src/tools/cold-demo.ts`, `BigInt(Math.floor(Date.now() /
1000))`), so a slow run leaves chain time behind. Confirmed pre-existing: the same line is in
`git show HEAD:ts/src/tools/cold-demo.ts`.

**~~Measured rate: between 1-in-6 and 1-in-3.~~ BOTH THE MECHANISM AND THE RATE ABOVE ARE WRONG.
Corrected 2026-08-30 by direct instrumentation.**

**The mechanism is not what this register said.** It is not that "Anvil advances block timestamps
per block". Measured on anvil 1.7.1: anvil stamps each mined block with the current wall-clock
second and that value then **stands still** until the next block. `pending` tracks the wall clock;
`latest` does not. viem builds a local-account transaction with `eth_fillTransaction`, which anvil
evaluates against the **`latest`** environment — so the receipt's time check is applied against the
frozen mandate-activation timestamp while the transaction is still being built, before anything is
sent. **That makes it a clean predicate, not a race**: if the signer crosses a one-second boundary
between the activation block and stamping `issuedAt`, `latest.timestamp < issuedAt` and it reverts,
and waiting cannot rescue it because `latest` never advances on its own.

**The rate was far worse than recorded.** Replaying the pre-fix `eth_fillTransaction` across 12
instrumented serial runs: **8 of 12 would have reverted**, every one with `0x118a0502` =
`ReceiptNotYetValid()`, at a drift of exactly one second. The earlier 1-in-6 and 1-in-3 figures
were sampling a one-second boundary crossing, not a rate.

**CLOSED 2026-08-30.** `cold-demo.ts` now derives every window it authors from the chain
(`getBlock({blockTag: "latest"}).timestamp`) rather than `Date.now()`, and a new
`alignChainClockTo()` mines one block at `max(latest+1, receipt.issuedAt)` before any Vault call,
asserting the result covers `issuedAt`. Deterministic by construction rather than a widened race —
no retry, no sleep, and deliberately **no widened validity window**, which would have weakened the
very window under test. The receipt's `issuedAt` stays the isolated signer's own wall clock,
correctly: that process is under test and takes no clock injection, so the demo moves the chain to
the receipt rather than the reverse. The run prints the drift it corrected.

**21 clean runs**, two batches of 10 plus one manual, all exit 0 with 4/4 controls. Ten of those
carried the one-second drift that reverts pre-fix. **Verification blind spot, stated by the
implementer:** all runs are one idle machine, anvil 1.7.1, viem 2.55.10. The alignment forces the
relationship rather than assuming it, so it does not depend on either version's clock behaviour —
but the measured *rate* does.

**Half of R-A018-09's closure condition is already met as a side effect:** the drift now fails
loudly with a non-zero exit instead of silently changing which branch the demo exercises. The other
half — aligning demo time to chain time — is not.

**Severity is release-level, not cosmetic:** the release README makes the cold demo the recipient's
first action, so a fraction of first-run recipients meet an uncaught stack trace.

**A withdrawn finding, recorded so nobody re-chases it.** The same reviewer initially reported two
TypeScript-suite anomalies (`propose.e2e.test.ts`, `signer.e2e.test.ts`) as possible instances of
the same clock mechanism. **Both were its own concurrency artefacts** — it had a background and a
foreground `npm test` running at once — and it withdrew them after re-measuring serially on an idle
machine: `signer.e2e.test.ts` 6/6, and every completed full run 557/557. **The TypeScript suite is
not implicated. Do not go looking.**

### R-A018-26 — R-A018-15's mechanism also lives in the e2e suite, and the demo fix did not reach it — NEW

Found 2026-09-01 when a fast-gate run failed on ONE TypeScript test — `ts/test/cases.e2e.test.ts:278`
*"Case 1 — exact mandate, allow › evaluates ALLOW, the signer attests, and the vault executes the
purchase"* — with `Error: ReceiptNotYetValid()`. **Same mechanism as R-A018-15:** line 260 stamps
`now: BigInt(Math.floor(Date.now() / 1000))` from the wall clock, while anvil stamps `latest` once
per block and it stands still, so a one-second boundary crossing between activation and signing
leaves `latest.timestamp < issuedAt` and the Vault reverts. R-A018-15 closed this in
`ts/src/tools/cold-demo.ts` by deriving windows from the chain and mining an alignment block. **The
e2e suite was not touched by that fix and is not in the D-087(a) batch scope.**

**Measured:** the failing file 3/3 clean serially; the full suite 557/557 on re-run; the batch's
diff touches neither `ts/test/` nor `ts/src/signer/` (`git diff --stat 2115c4f -- ts/src/signer/
ts/test/` is empty). Pre-existing and intermittent. The 2026-08-30 adversarial reviewer saw this
exact test flake at `8d47a0b` and withdrew it as its own concurrency artifact; **it was not an
artifact.**

**Closes when** `cases.e2e.test.ts` (and any sibling e2e test stamping `now` from `Date.now()`)
aligns the chain clock the way the demo does. **Not fixed in this batch, deliberately** — it is
a test-file change outside the ruled scope, and the candidate is at its declared state.

### R-A018-21 — The TypeScript suite can hang indefinitely rather than fail — NEW, low confidence

Observed 2026-08-30 while diagnosing the above. `node --test` is invoked with `--test-timeout=0`, so
a stalled test never times out: under contention one run hung on `test/signer.e2e.test.ts` for 80+
minutes with no output and no exit. **The reviewer caused that contention itself, so this is weak
evidence about normal operation** and is recorded at low confidence. It is worth knowing anyway —
a suite that hangs forever rather than failing is the shape of thing that strands CI, and this
project's own recorded failure modes include "a probe that is dead and whose silence reads like a
pass."

**Why it matters more than a flake normally would.** It is direct evidence for R-A018-09: under the
bare `catch` that R-A018-09 replaced, the same clock drift landing one step earlier would have
printed `PASS negative: altered calldata` — a green line from a harness failure that proves nothing
about enforcement. The demo could have been reporting successful negative controls it never ran.

**Closes when** demo time is aligned to chain time deterministically rather than by wall clock, and
a run that drifts fails loudly instead of silently changing which branch it exercises.

### R-A018-13 — Pin the recipient's toolchain — *Acceptance Criterion 5, NOT an A-018 requirement*

Reclassified. Solidity is already exact (`pragma solidity 0.8.28`); Node, Python, Foundry and
Anvil are unpinned. Useful reproducibility work, but **it does not appear in any A-018 withdrawal
condition** and must not be presented as closure work.

---

## 4. Blocked on a ruling that is John's — DO NOT START

- **THE CONSTITUTIONAL QUESTION, AND IT COMES FIRST.** The chairs' informal reading: an
  Override-in-Writing **can** authorize proceeding despite unresolved Criticals, but **does not
  rewrite the Ingot's acceptance or kill conditions.** So a lab product cannot be described as
  satisfying the present finished-enforcement Ingot merely because the Criticals were overridden.
  The clean lab path is **a fresh casting** with new acceptance and kill criteria; the other
  instrument is an Override explicitly recording that publication proceeds **while this Ingot
  remains unsatisfied**, which the chairs consider materially less clean. **Not formally ruled.
  No branch can be costed until it is.**
- **Product identity:** value-custody product versus mechanically non-custodial authorization
  router (§2, §1.6).
- **Named audience, venue, publication surface, and production chain.**
- **Whether the published artifact is the release tree, the public repository, or both** — and
  therefore whether a history-free export is needed. R-A018-12 stops at current tools until ruled.
- **Economic value at risk across native value, tokens, approvals and administrative authority** —
  not native value alone.
- **Owner, signer and deployment-authority custody**, and the independently controlled channel by
  which an authority fingerprint reaches a recipient.
- **Monitoring, incident, security-reporting, support and end-of-support posture.**
- **Licence.** All four contract sources carry `SPDX-License-Identifier: UNLICENSED`, which is not
  the SPDX `Unlicense` identifier, and there is **no `LICENSE` file**. It provides **no
  affirmative licence grant**. Any broader claim awaits legal review (§0.2).
- **The unaided named-audience comprehension test, without source access** — Critical 2's own
  falsifier. It cannot be run by the build team and is listed here so it is not lost.
- **Commissioning the persistent deployment and the independent security review.**
- **The v0.3 corpus relabelling**, still owed under **Acceptance Criterion 7**. Grep `the deep
  provenance comparison correctly refuses` in `docs/session-state.md`.

**A caution the build team owes against itself.** Its response to A-018 estimated the branches at
"roughly a week against several months." **Withdrawn** — no work breakdown, and it compared a
branch whose reachability is unknown against one whose scope is unset.

---

## 5. Requirements that survive outside A-018

Recorded because closing the four withdrawal conditions does not close Cycle 2. Still live:
the named-audience test, a clean publication profile, deep-profile resolution, licensing,
supportability and independent review — **unless the Smith changes the Ingot.**

---

## 6. The open sequencing question, stated without a recommendation the build team may not make

The chairs split three ways on whether to repair before the scope decision:

- **Catalyst and Conscience:** authorize the branch-independent defect repairs now.
- **Adversary:** decide the constitutional question first; the defect batch may be separately
  authorized without deciding the product.
- **Subtractor:** because the defective candidate is local-only and each change creates a new
  SHA, settle scope first and build one replacement candidate.

**The §0.1 correction bears directly on this split.** The build team's own argument for immediate
repair rested on the claim that the defects were on a pushed branch. **They are not.** Whatever
weight that urgency carried should be withdrawn from the Catalyst/Conscience position and
returned to Subtractor's.

**`a38cff9` cannot be repaired and remain the reviewed exact candidate.** Every fix produces a new
SHA requiring fresh exact-commit review, which is an argument for batching whatever is authorized
into **one** replacement candidate rather than trickling it.

---

## 7. Protocol gap, recorded for the Crucible rather than for the builders

The §5 `From` enum has seven values and none is the build team, so a halted line whose closure
conditions are all build work has no defined channel for the builder to answer on. The Conscience
recommends a non-seat `BUILDER` / `RESPONDENT` artifact path in a future protocol revision.
