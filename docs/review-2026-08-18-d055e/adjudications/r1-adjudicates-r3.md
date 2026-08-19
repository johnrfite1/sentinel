# ADJUDICATION — Reviewer 1 adjudicating Reviewer 3

**Adjudicator:** R1 (certification and instruments). I did not author these findings and R3's
surface — `contracts/**`, `ts/src/corpus/**`, `ts/src/ablation/**`, `fixtures/corpus/**` — was
not mine to review.

**Commit:** `7e0ab7f1057de278c09cc803ab4ca266f53399e1`, worktree `w1`, detached.
**Baseline re-established before adjudicating:** `forge build --root contracts` clean;
`forge test --root contracts` = **75 passed, 0 failed, 0 skipped**; unmutated corpus re-run
compared with the gate's own VERDICTCHECK = **51 result files identical to the committed set**.

**Independence.** I wrote my own Solidity mutation harness
(`evidence/r1/adj/solmutate.sh`) and my own TypeScript harness (`evidence/r1/adj/tsmutate.sh`)
from scratch. I did **not** execute R3's `scratchpad/probes/mutate.sh` or `tsmutate.sh` at any
point. My anchors are my own, and for R3-F7 my **controls are different from R3's** (R3 used
`OverrideAuthorized` deletion/argument-zeroing and the `ActionExecuted` flag; I used the
`ActionExecuted` flag and `Recovered`'s amount) so the controls are not a shared assumption.
Every mutation restored and verified byte-identical by `cmp`; final `git diff HEAD --stat -- .`
shows only the two provisioned submodule symlinks.

**Verdict summary**

| id | R3 severity | my verdict | my severity |
|---|---|---|---|
| R3-F1 | MEDIUM | **CONFIRMED** | MEDIUM |
| R3-F2 | MEDIUM | **CONFIRMED** | MEDIUM |
| R3-F3 | MEDIUM | **CONFIRMED** (structure verified; R3's synthetic run not re-executed) | MEDIUM |
| R3-F4 | MEDIUM | **CONFIRMED** | MEDIUM |
| R3-F5 | MEDIUM | **CONFIRMED** | MEDIUM |
| R3-F6 | MEDIUM | **CONFIRMED** | MEDIUM |
| R3-F7 | MEDIUM | **CONFIRMED** | MEDIUM — argued at length below; I decline to raise, and say why |
| R3-F8 | MEDIUM | **CONFIRMED, with one sub-claim MATERIALLY WEAKENED and R3's LEAD RESOLVED** | MEDIUM |

**No finding refuted. No severity changed.** R3's uniform MEDIUM was tested per-finding rather
than accepted, and it survives — but not because the findings are interchangeable. The
reasoning differs finding by finding and is given in each section. **The one correction I make
is to R3-F8(b), where I ran the probe R3 labelled a LEAD and it comes out against R3's
framing.**

---

## R3-F1 — the signed S2 pack's "MEASURED" G-3 reproduction

**Claim.** `docs/gate-s2-evidence.md` §11 and `docs/v1-1-register.md` §13.4 both state that
"exactly two classes are credited only on UNRESOLVED outcomes — `conflicting-block-state` and
`runtime-code-change-or-proxy-target`". R3 says the real number is three, and that
`conflicting-block-state` is not one of them — it is credited on *nothing*, being the guard's
one ruled GAP.

**What I did.** Ran `bash scripts/check-class-coverage.sh`. Then extracted the guard's own
`ABOUT` map (and its `CONFORMING` sentinel) directly out of `scripts/check-class-coverage.sh`
into `evidence/r1/adj/about.js` and recomputed credit from the 51 committed result files in
`fixtures/corpus/results/` with node, walking every `{code, outcome}` pair and counting a class
credited when a mapped code is non-PASS on a fixture of that class.

**A dead probe on my side, disclosed.** My first attempt extracted the map with a Python regex
and returned **0 classes**, which would have printed "credited on nothing: []" — a clean-looking
null from a probe that measured nothing. I caught it because the class count was zero rather
than twenty. The corrected extraction is the one above.

**What I observed.**

```
guard output:  ok    14 of 20 classes exercise the class they name
               GAP       conflicting-block-state   [D-039]
               1 GAP: conflicting-block-state

my recomputation (16 classes carry a non-empty code map):
  credited ONLY on UNRESOLVED (3): malformed-calldata-or-unknown-selector,
                                   runtime-code-change-or-proxy-target,
                                   rpc-simulator-or-context-outage
  credited on NOTHING (3):         conflicting-block-state,
                                   unexpected-internal-call,
                                   reentrancy-attempt
```

R3's table is reproduced exactly: three classes UNRESOLVED-only, and the class the signed pack
names is in the *other* bucket. **The same script, in the same run, prints
`1 GAP: conflicting-block-state` while the signed pack says that class is credited on
UNRESOLVED.** The two artifacts contradict each other at the frozen commit, five repairs
(A-070…A-076) after the sentence was written.

**Verdict: CONFIRMED.**

**Severity: MEDIUM** (agreeing with R3). Reasoning: this is a false claim, labelled MEASURED,
inside a **signed** gate deliverable and repeated in the register and in R3's own dispatch
brief — which is the shape my brief says has produced HIGHs before. I considered High and
declined, because the G-3 acceptance it supports (MEDIUM → LOW, on the ground that the security
framing is refuted by the outcome taxonomy) **does not turn on whether the number is two or
three**: 11-of-20 versus 14-of-20 does not flip the ruling, and the class-coverage guard prints
the GAP honestly on every run. It is a MEDIUM at the top of its band, and it is the one I would
fix first because fixing it costs a sentence.

**Duplication handled correctly by R3.** R3 disclosed *before* the claim that round six lens 5
already reported the count half (`ADJUDICATED-ROUND-SIX.md:378`), and confirmed that item is in
neither register §13.4 nor §11.0 — the two lists the common brief defines as "already recorded".
Under Rule 5 the naming error is novel and the whole is reportable. I agree with that handling
and note it as a model of the disclosure the rule wants.

---

## R3-F2 — the ablation report's "CHECK ON THE PARTITION"

**Claim.** `docs/ablation-report.md` publishes a table it calls a **CHECK ON THE PARTITION**,
asserting that a non-empty second row would mean "a code has drifted into the mandate-conformance
set". R3 says the check compares two hand-maintained copies of one list and therefore cannot
detect that drift.

**What I did.** Read `ts/src/ablation/report.ts` imports and set definition; read
`MANDATE_CONFORMANCE_CODES` in `ts/src/ablation/layers.ts`; compared the two sets by executing
the real exported set against the report's literal.

**What I observed.**

```
ts/src/ablation/report.ts:3  import {LAYERS, LAYER_DESCRIPTIONS, type LayerName} from "./layers.ts";
   -> MANDATE_CONFORMANCE_CODES is NOT imported.
ts/src/ablation/report.ts:377  const WITHHELD = new Set([ ...8 literals... ]);

layers.ts MANDATE_CONFORMANCE_CODES size 8; report.ts WITHHELD size 8
in layers not report: []      in report not layers: []
```

The two sets agree **today**, and nothing binds them. `runLayer` partitions L2 using
`MANDATE_CONFORMANCE_CODES`; the report's "check" partitions using its own `WITHHELD`. The
second row is empty because the report is comparing its copy of the list against itself. If
`layers.ts` gained or lost a code, the report's stated drift detector is the one thing that
would not notice.

**Verdict: CONFIRMED.**

**Severity: MEDIUM** (agreeing). It is a false claim in a generated Gate S2 deliverable, and the
instrument-points-at-the-wrong-thing shape the common brief names. I note one genuine mitigation
R3 did not credit: the gate byte-compares the regenerated ablation report against the committed
one, so a real change to `layers.ts` **would** move the report's contribution table and fail the
gate — just not via the mechanism the report's own prose advertises. That mitigation is why I do
not raise it; the false sentence is why I do not lower it.

---

## R3-F3 — the D-011(b) leak guards

**Claim.** The A-032 repair closed the denylist half (`isDeclaredAt`) and left the allowlist half
(`assertViewShape`) reaching only the top level and `observedEnvironment`; the route A-028 F-3
actually used — an *innocuous* key name, which a denylist cannot see — is still open one level
below where the allowlist looks.

**What I did.** Read `ts/src/corpus/leakage.ts` structurally. I did **not** re-execute R3's four
synthetic views and two controls.

**What I observed.** `assertViewShape` (leakage.ts:218) inspects `view` at depth 0 against
`ALLOWED_VIEW_KEYS`, then inspects `view.observedEnvironment` (line 222) and nothing else. The
depth-tracking walk that *does* descend (line 117, carrying `inEnvironment`) belongs to the
denylist path. The file's own comment at line 111 states the gap in terms:
*"`assertViewShape` only inspects the top level and `observedEnvironment`."* The structural basis
of R3's claim is therefore present in the shipped code and acknowledged by it.

**Verdict: CONFIRMED**, with the scope of my confirmation stated: I verified the **structure**
that makes the leak possible and that A-032 recorded this as an *undemonstrated hypothesis*.
I did not independently re-run R3's demonstration, so the step from "structurally reachable" to
"demonstrated on synthetic views" rests on R3's artifacts (`evidence/r3/probes/`), not on mine.
An adjudicator wanting that step independently confirmed should re-run it; I flag this as the
one place in this adjudication where I am relying on R3's execution.

**Severity: MEDIUM** (agreeing). This guard protects the corpus's ground truth — labeller
independence is the basis of every §7 figure — and A-032 explicitly deferred it as "no live path
was constructed". R3 constructs one. It is not higher because the leak is a *possibility in the
guard*, not an observed contamination of any committed view.

---

## R3-F4 — three signed payload fields consulted by nothing

**Claim.** `purposeKind`, `allowedTargetsHash`, `allowedSelectorsHash` and `allowedCallGraphHash`
appear only as type strings, hashStruct operands, wire validation and fixture construction —
never in a comparison — and only one carries the D-025 disclosure.

**What I did.** Grepped every occurrence across `ts/src`, `verifier/*.py` and `contracts/src`,
then ran the decisive negative check against the three files that would have to consult them.

**What I observed.**

```
occurrences of purposeKind|allowedTargetsHash|allowedSelectorsHash|allowedCallGraphHash in:
  ts/src/evaluate/checks.ts        0
  verifier/verify.py               0
  contracts/src/SentinelVault.sol  0
```

Zero in the evaluator, zero in the independent D-010 verifier, zero in the vault. Every hit
elsewhere is an EIP-712 type string, a `word.bytes32()` encoding operand, a `protocol.ts` wire
validator, or fixture construction — exactly as R3 characterised it. These fields are signed
and hash-committed, and no implementation on any of the three layers reads them.

**Verdict: CONFIRMED.**

**Severity: MEDIUM** (agreeing). A field inside a signed payload that nothing consults means the
signature attests something no layer checks — and D-025 exists precisely to require that be
disclosed. Two of the three are undisclosed. It is not higher because nothing is *wrong*: the
fields are inert rather than misleading, and inertness in a lab is a documentation debt rather
than a security one.

---

## R3-F5 — the §3.3(5) receipt binding, half-tested

**Claim.** `receipt.mandateHash != action.mandateHash || receipt.policyHash != action.policyHash`
is one check with two halves; deleting the POLICY half leaves 75/75 green while deleting the
MANDATE half is killed by exactly one test; and `scripts/mutate.sh`'s S5 deletes the whole
conjunction, so it reports CAUGHT and masks the gap.

**What I did.** Wrote my own harness and ran probe and control with my own anchors.

**What I observed.**

```
A1-PROBE-deletePolicyHalf     SURVIVED  (75 passed, 0 failed, 0 skipped)
A2-CONTROL-deleteMandateHalf  KILLED    (74 passed, 1 failed)
   [FAIL: next call did not revert as expected] test_receiptClaimingADifferentMandateIsRejected()
both restored: byte-identical
```

Same statement, same error selector, one half covered and one not. I then read
`scripts/mutate.sh:849` and confirmed S5's anchor is the **entire** two-line conjunction plus its
`revert`, and that `grep -n policyHash scripts/mutate.sh` finds no mutant perturbing the policy
half alone. I also confirmed the sole covering test
(`SentinelVault.backstops.t.sol:308`) perturbs only `r.mandateHash`.

**Verdict: CONFIRMED**, reproduced independently with my own control.

**Severity: MEDIUM** (agreeing, and I considered R3's own argument for High). The deciding
question the coordinator set is whether this changes what the product **guarantees** or only what
a test would catch. In the shipped tree the check is **correct** — both halves are enforced — so
no guarantee is currently broken. What fails is the instrument, twice over: the suite does not
pin half the check, and the project's own mutation harness reports that half covered. That is a
serious instrument defect and a genuinely un-generalised repair of `D-05` (fixed in
`ts/src/evaluate/checks.ts` under A-068, never carried to the Solidity twin), but it is not a
live vulnerability. MEDIUM is right and I decline to raise it.

---

## R3-F6 — the vault's timestamp comparisons, unpinned both ways

**Claim.** All three `block.timestamp >` comparisons are unpinned in both directions; the value
ceiling is pinned in both; six survivors, two killed controls.

**What I did.** Ran all eight mutations myself. Widening used `uint256(x) + 1` to avoid the
`type(uint64).max` overflow trap R3 documents in its DEAD-PROBES.

**What I observed.**

```
B1-deadlineWiden           SURVIVED   N1-deadlineNarrow          SURVIVED
B2-rcptExpWiden            SURVIVED   N2-rcptExpNarrow           SURVIVED
B3-ovrExpWiden             SURVIVED   N3-ovrExpNarrow            SURVIVED
B4-CONTROL-valueWiden      KILLED     N4-CONTROL-valueNarrow     KILLED
  B4 kills: test_LIMIT_nativeCeilingIsPerActionAndBoundsNoAggregate,
            test_valueOverHardCapIsRejectedEvenWithAValidReceipt
  N4 kills: test_LIMIT_nativeCeilingIsPerActionAndBoundsNoAggregate  [FAIL: ValueOverCap()]
all eight restored: byte-identical
```

R3's table reproduces exactly, including which tests fire on the controls. The split is clean:
one of the vault's four limit comparisons has an at-boundary assertion and three do not. The
three expiry tests that exist each warp far past the window (+11 min against a 10-min receipt,
+31 min against a +30-min deadline), so they prove "an hour late is rejected" and never
"one second late is rejected" or "exactly at the limit is still accepted".

**Verdict: CONFIRMED.**

**Severity: MEDIUM** (agreeing). Same reasoning as F5, and R3 states it correctly itself: *"the
finding is the instrument, not the second."* A one-second window drift is not an exploit and the
NatSpec's argument about manipulable ranges is sound. What matters is that these three edges can
be changed to `>=`, to `<`, or to `+ 3600` with a green gate. That is a MEDIUM instrument gap,
and it is the same `D-06` repair not generalised from the engine to the vault.

---

## R3-F7 — five of eight events can state something false

**The coordinator asked specifically for my independent view on whether this is worth more or
less than MEDIUM. It is worth MEDIUM, and here is the reasoning rather than the label.**

**Claim.** Five of the vault's eight events are asserted by nothing and can each be made to log
something the transaction did not do, with 75/75 green; the three that are asserted are exactly
the three D-043 touched. Sharpest: `SignerRotated` logging the new signer as the previous one.

**What I did.** Enumerated the events, the emit sites and every `expectEmit` in
`contracts/test/`. Then ran five probes and **two controls of my own choosing** — deliberately
different from R3's, so the control is not a shared assumption.

**What I observed.**

```
declarations: 8 events.  expectEmit calls: 3  -> ActionExecuted, Recovered, OverrideAuthorized

E1-signerRotatedOrderSwap   SURVIVED (75/75)   <- logs SignerRotated(new, new)
E2-mandateActivatedZero     SURVIVED (75/75)
E3-policyActivatedZero      SURVIVED (75/75)
E4-pausedSetInverted        SURVIVED (75/75)   <- logs PausedSet(!value)
E5-mandateRevokedZero       SURVIVED (75/75)

E6-CONTROL-actionExecutedFlag  KILLED  [FAIL: Purchased != expected ActionExecuted]
                                        test_executionEventReportsTheBoundNonceAndTheActualAmount
E7-CONTROL-recoveredAmount     KILLED  [FAIL: Recovered param mismatch at amount:
                                        expected=1e18, got=0] test_recoverEventReportsTheAmountItActuallyMoved
all restored: byte-identical
```

The 5/3 split is exact and holds against controls I picked independently. `E1` is confirmed as
the sharp one: `rotateSigner` emits *before* assigning, so moving the assignment two lines up
makes every rotation log `SignerRotated(newSigner, newSigner)` — an innocuous-looking reorder
that erases the outgoing key from the only onchain record of it.

**Verdict: CONFIRMED.**

**Severity: MEDIUM — and this is the finding where I most seriously considered both directions.**

*The case for raising to High.* Sentinel's product is not the vault's enforcement; it is
**conformance evidence**. §3.3(2) makes "LOGGED" a requirement, not a nicety. The events are the
only onchain artifact an auditor could reconstruct history from, and R3 is right that
`SignerRotated` is load-bearing for two accepted LIMIT tests whose whole subject is rotation
history ("rotation is not revocation"). If the audit log is a *product guarantee*, a log that can
lie about which key was authoritative is closer to a High.

*The case for lowering to Low.* Events gate nothing. No funds move differently, no verdict
changes, no receipt validates that would not have. "A test does not assert X" is the weakest
class of finding, and five of these are owner-only administrative events on a testnet lab.

*Why MEDIUM.* The deciding fact is that **in the shipped tree all eight events are correct.**
Nothing currently lies, no committed artifact is wrong, and no consumer exists in this repository
that reads any of these events — I checked. So the live product guarantee is intact and what
fails is, again, the instrument. That places it in the same band as F5 and F6 rather than above
them. But it is the **strongest** MEDIUM of the three, and for a reason worth recording: F5 and
F6 protect defence-in-depth, whereas F7's subject is the evidentiary surface the project exists
to produce. If John's view is that the onchain log is a product guarantee rather than a test
gap, this is the one of the eight I would expect him to raise, and I would not argue.

**One distinction R3 did not draw, offered to the repair.** The five are not equally worth
fixing. `E1` (SignerRotated) and `E4` (PausedSet inverted) are the two where a wrong value would
mislead an off-chain reader who had no other source — rotation history exists nowhere else, and
an inverted pause flag is what a monitor would key on. `E2`/`E3`/`E5` log hashes that are also
readable from contract state at any time. If only part of this is repaired, repair those two.

---

## R3-F8 — the D-10 repair

This is the finding I changed something about. **CONFIRMED overall, one sub-claim materially
weakened, and R3's LEAD resolved against R3's framing.**

### (c) the false MEASURED premise — CONFIRMED, and it is the sharpest part

The coordinator asked me to check this rather than trust either party. `ts/test/evaluate.checks.test.ts:426-428`
reads, verbatim at the frozen commit:

> The corpus is single-case throughout — measured: 9 distinct addresses across all 50 fixtures,
> zero non-lowercase occurrences — **and every fixture sets `principal === beneficiary`**. So the
> corpus cannot distinguish a normalised comparison from an unnormalised one, **nor the
> beneficiary from the principal**, and neither could anything else in the suite.

Swept all committed labeller views myself:

```
fixtures scanned: 51 (50 fixtures + _digests.json)
principal != beneficiary: 1
   F024  principal   0x00000000000000000000000000000000deadbeef
         beneficiary 0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266
         callData    0xc188528b...   (DemoPay.purchase — it DOES reach EVAL_PURCHASE_BENEFICIARY)
fixtures/corpus/results/F024.json:
   {"code": "EVAL_PURCHASE_BENEFICIARY", "outcome": "PASS", "detail": ""}
```

**The measured premise is false**, and the conclusion it supports — "the corpus cannot
distinguish the beneficiary from the principal" — is false as stated. It is true only of
`EVAL_APPROVAL_SPENDER`. **CONFIRMED.**

### (a) the case-normalisation sites — CONFIRMED on a sample, not re-derived in full

I ran one probe and one control rather than all nine:

```
T06-PROBE-approvalSpenderCase   unit=SURVIVED   (the check D-10(c) was raised to MEDIUM about)
C08-CONTROL-targetBoundCase     unit=KILLED
```

The shape holds: `EVAL_APPROVAL_SPENDER` is pinned for its FIELD and not for its CASE, while
`EVAL_TARGET_BOUND` is pinned for both. **I did not re-derive all nine sites**; R3's count of
7 survivors / 2 controls rests on its own transcripts (`evidence/r3/ts-mutations/`), not on mine.
CONFIRMED as to the pattern and as to T06 specifically.

### (b) the surviving field swap — CONFIRMED as to the unit suite, WEAKENED as to consequence

```
T11-PROBE-purchaseBeneficiaryFieldSwap   unit=SURVIVED  (513-test suite green)
C10-CONTROL-approvalSpenderFieldSwap     unit=KILLED    (D-10(c)'s own test)
```

Same substitution, same two fields, thirty lines apart, one covered and one not. Confirmed.

**Then I ran the probe R3 declined to run.** R3 wrote: *"LEAD, not a finding — I did not run the
corpus."* I ran it.

*First attempt was a DEAD PROBE and I am recording it.* I compared regenerated result files with
`diff -q` and got "50 result files moved" — including at baseline, because result files carry
per-check `micros` timings. That comparison measured nothing. I discarded it and extracted the
gate's own `VERDICTCHECK` comparator verbatim from `scripts/test.sh` into
`evidence/r1/adj/verdictcheck.py`, which strips `micros` and normalises the embedded wall clock.

*Validated against baseline first:*

```
unmutated corpus + VERDICTCHECK ->  corpus verdicts: 51 result files identical   (rc=0)
```

*Then under T11:*

```
T11 + corpus + VERDICTCHECK  ->  1 result file(s) MOVED: F024.json    (rc=1)
  committed: {"code":"EVAL_PURCHASE_BENEFICIARY","outcome":"PASS","detail":""}
  mutated  : {"code":"EVAL_PURCHASE_BENEFICIARY","outcome":"VIOLATION", ...}
```

**The deep gate catches T11.** Exactly one file moves, and it is F024 — precisely the fixture
whose existence the repair's comment denies. `scripts/test.sh:392` gates this stage on
`[ "$PROFILE" = "gate" ]`, so the **fast** profile is blind to it and the **deep** profile is not.

This cuts both ways and I am reporting both. It **weakens** R3's implicit framing that the field
swap is unprotected — the gate that produces gate evidence does catch it. It **sharpens** R3-F8(c),
because the repair's author wrote that the corpus could not distinguish beneficiary from
principal, and had that been checked, the corpus would have been found to catch exactly this
mutation. The false premise did not merely misdescribe the corpus; it hid an existing protection
from the person designing around its absence.

*(A detail worth passing to the repair: under T11 the diagnostic string still interpolates
`mandate.beneficiary` while the comparison uses `mandate.principal`, so F024's VIOLATION detail
prints the same address twice — "beneficiary 0xf39f…, mandate authorises 0xf39f…". A reader
would be told a value violates itself.)*

### (d) the recurrence half — NOT VERIFIED BY ME

R3 reports `T12-recurrenceMandateHalf` surviving on the ground that `recurringAllowed` is `false`
in all 50 views. **I did not run it and did not check the field.** That sub-claim is **UNPROVEN
by this adjudication** and rests on R3's transcript. It should not be counted as independently
confirmed.

### Verdict and severity

**Verdict: CONFIRMED**, with (b) weakened as described and (d) unproven by me.

**Severity: MEDIUM** (agreeing). (c) is a false measured claim inside a repair's own
justification for work John personally re-classified to MEDIUM at D-056(a) — that alone earns
MEDIUM. (a) is a real and un-generalised gap: the case comparisons are invisible to the corpus
too, because the corpus is all-lowercase, so those survive *everything*, which is the part of
this finding with the least protection behind it. (b) is the weakest limb now that the deep gate
is shown to catch it. I do not raise to High because, once again, the shipped implementation is
correct — `checks.ts` compares the right fields with the right normalisation today.

---

## Adjudicator's notes

**1. R3's uniform MEDIUM is defensible, and I tested it rather than accepted it.** I looked for
a reason to move each of the eight and found none. The flatness is not laziness: every one of
these findings has the same underlying shape — *the shipped behaviour is correct and the
instrument that would catch a regression is absent or mis-aimed* — and that shape genuinely lands
in one band. R3 said so explicitly in its own severity note, and the evidence bears it out.

**2. The cross-cutting pattern R3 claims is real and I confirmed it independently.** F5 is `D-05`
one language away. F6 is `D-06` one language away. F8 is `D-10`'s own repair not reaching its own
stated argument. F7 is `D-043` not reaching the five events it did not name. **Four independent
measurements of "the repair generalised the demonstration, not the argument"**, which is the
failure mode the common brief names. That pattern is worth more than any single MEDIUM in this
set, and I would put it to John as one item rather than four.

**3. R3's evidence discipline is the best-documented I have seen in this round.** Every mutation
carries a control, the controls fire, dead probes are recorded rather than buried (the
`type(uint64).max` overflow and the `MEV2` build failure), the partial duplicate in F1 is
disclosed *before* the claim, and the one inference it could not execute is labelled a LEAD and
left as one — which is exactly the discipline that let me resolve it cleanly. I found no
overstatement anywhere in the report.

**4. What I did not adjudicate.** R3's NULL-RESULTS, DEAD-PROBES, COVERAGE and CRITIQUE were read
for context but not independently verified. R3-F3's synthetic demonstration and R3-F8(a)'s full
nine-site sweep and (d) rest on R3's transcripts. Those are named above so no one reads this
adjudication as covering them.

## Provenance

Harnesses written for this adjudication, all re-runnable, in
`<REVIEW-ROOT>/evidence/r1/adj/`:
`solmutate.sh`, `tsmutate.sh`, `verdictcheck.py`, `about.js`, plus per-mutation transcripts
(`*.test.txt`, `*.npmtest.txt`, `*.build.txt`) and the summaries `F6-summary.txt`,
`F7-summary.txt`, `F8-summary.txt`, `baseline-corpus.txt`.

**Mutations applied: 17** (2 for F5, 8 for F6, 7 for F7) in `contracts/src/SentinelVault.sol`,
plus 5 in `ts/src/evaluate/checks.ts` (4 via harness, 1 for the corpus run). Every one restored
and verified with `cmp`. No repairs made. No file in
`<REPO>` was read, written or executed.

**Final worktree state:**

```
$ git diff HEAD --stat -- .
 contracts/lib/forge-std              | 2 +-
 contracts/lib/openzeppelin-contracts | 2 +-
$ git rev-parse HEAD
7e0ab7f1057de278c09cc803ab4ca266f53399e1
contracts/src/SentinelVault.sol  CLEAN
ts/src/evaluate/checks.ts        CLEAN
```

*R1 adjudicating R3, D-055(e), 2026-08-19.*
