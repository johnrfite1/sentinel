# REPORT — Reviewer 3 (onchain and corpus)

Commit reviewed: `7e0ab7f1057de278c09cc803ab4ca266f53399e1`
Worktree: `_archive/sentinel-d055e-review/worktrees/w3` (detached). Live repo never touched.
Baseline (mine, run before any mutation): forge 75/75 pass, `npm test` 513/513 pass.
See `ATTESTATION.md` for versions and the exact baseline transcript.

## Findings at a glance

| id | severity | one line | reproduced |
|---|---|---|---|
| **R3-F1** | MEDIUM | The signed S2 pack's "MEASURED" reproduction of `G-3` names a class that is credited on nothing and undercounts the real set by half — and my own brief repeats the refuted figure | yes |
| **R3-F2** | MEDIUM | The ablation report's "CHECK ON THE PARTITION" compares two hand-maintained copies of one list; its DRIFT message diagnoses a set the probe never touched | yes |
| **R3-F3** | MEDIUM | Evaluator output reaches a labeller view under an innocuous name one level below where the allowlist reaches — A-032's hypothesis, now demonstrated | yes |
| **R3-F4** | MEDIUM | Three signed payload fields are consulted by nothing; only one carries the disclosure D-025 exists to require | yes |
| **R3-F5** | MEDIUM | The vault's §3.3(5) receipt binding is half-tested: deleting the POLICY half leaves 75/75 green, and `mutate.sh`'s S5 reports it CAUGHT | yes |
| **R3-F6** | MEDIUM | All three of the vault's timestamp comparisons are unpinned in BOTH directions; the value ceiling is pinned in both | yes |
| **R3-F7** | MEDIUM | Five of the vault's eight events can be made to state something false with 75/75 green — exactly the five D-043 did not touch | yes |
| **R3-F8** | MEDIUM | The D-10 repair pinned 2 of 9 case comparisons and 1 of 2 field swaps; the identical swap 30 lines above still survives, and the repair's MEASURED premise is false | yes |

**8 findings, all MEDIUM, all reproduced. 0 Critical, 0 High, 0 Low, 0 Info. 0 leads promoted to
findings** — the one unexecuted inference (R3-F8's deep-gate consequence) is labelled LEAD in place.

**Severity note, stated rather than buried.** I considered High for R3-F5 and R3-F7 and settled on
MEDIUM for both, for the same reason: each is a check or a log that is *correct in the tree* and
*asserted by nothing*, so the live behaviour is sound and what fails is the instrument. The
argument for raising either is given inside its section. I have not softened anything to fit a
distribution; the flatness is what the evidence produced.

**The pattern across R3-F3, R3-F5, R3-F6, R3-F7 and R3-F8 is one pattern.** Five of my eight
findings are the SAME already-adjudicated defect (`D-05`, `D-06`, `D-10`, `A-028 F-3`, `D-043`)
surviving one file, one language, or one nesting level away from where a reviewer demonstrated it.
The common brief names this shape; this report is eight independent measurements of it.

## The vault mutation sweep, in full

**53 mutations attempted** against `contracts/src/SentinelVault.sol`: **4 dead probes**
(build-failed under `deny = "warnings"` — never scored as catches, all 4 re-run in a
variable-preserving shape) and **49 measured**. Each measured mutation ran twice — against the
11-invariant campaign alone (`--match-test '^invariant_'`) and against the full 75-test suite.

| result | count | ids |
|---|---|---|
| killed by the full suite | 37 | — |
| **SURVIVED the full suite** | **12** | `M18` · `MB2` `MB3` `MB4` · `MN1` `MN2` `MN3` · `M38` `MEV1` `MEV2b` `MEV3` `MEV4` |
| killed by the invariant campaign | 8 | `M01` `M04` `M11` `M22` `M23` `M25` `M21b` `M30b` |
| **of those 8, also killed with the campaign EXCLUDED** (`--no-match-test '^invariant_'`) | **8 of 8** | marginal contribution of the campaign: **zero** |

The twelve survivors are three distinct defects:

* **1** — the half-tested §3.3(5) receipt binding (`M18`) → **R3-F5**
* **6** — three time comparisons × two directions (`MB2`–`MB4` widen, `MN1`–`MN3` narrow) → **R3-F6**
* **5** — five unasserted events (`M38`, `MEV1`, `MEV2b`, `MEV3`, `MEV4`) → **R3-F7**

**Controls in the same batches that DID fire**, so "survived" is not the harness's constant:
`MB1` and `MN4` (the value ceiling, both directions), `M17` (the other half of the same
conjunction as `M18`), `M35`/`M36`/`M37` (the three D-043 events), `M21b`/`M24b`/`M30b` (the
re-run dead probes), and 30 more.

**TypeScript sweep:** 12 mutations against `ts/src/evaluate/checks.ts`, **0 dead probes**,
**9 survivors and 3 controls killed** → **R3-F8**.

---

## R3-F1 — The signed S2 pack's "MEASURED" reproduction of G-3 names the wrong classes and undercounts them by half — and the D-055(e) reviewer brief propagates the refuted figure

**Severity: MEDIUM**  (false-claim / instrument-defect, inside a SIGNED gate deliverable)
**Confidence: HIGH — reproduced from the committed artifacts with the guard's own map.**

### PARTIAL DUPLICATE, DISCLOSED BEFORE THE CLAIM

I reached this independently and only afterwards found that **round six lens 5 already reported
the count half of it**: `docs/review-2026-08-18-round-six/ADJUDICATED-ROUND-SIX.md:378` —
*"`G-3` is worse than recorded — three classes are credited only by UNRESOLVED, not two … Strict
reading: 11 of 20, not 14 of 20."* My independent measurement reproduces both numbers exactly
(11 = 10 VIOLATION-credited + 1 CONFORMING). That item is **NOT in register §13.4 and NOT in
§11.0**, the two lists the common brief names as "already recorded", so I report it rather than
drop it — but I am not claiming the count as novel.

**What IS novel, and what makes this worse than round six recorded it:**
1. The S2 pack does not merely undercount — it **names the wrong class**. `conflicting-block-state`
   is credited on NOTHING; it is the guard's single ruled `GAP`, printed as such on every run.
   Round six's summary does not say this.
2. The refuted figure is **still in the signed pack and the register at the frozen commit**, five
   repairs (A-070…A-076) later.
3. **My own D-055(e) brief repeats it** — `briefs/r3.md`: *"two classes are credited only on
   UNRESOLVED outcomes."* The scope document that fixed this review's targets carries a figure a
   previous round had already measured false, which means the final bounded review was pointed at
   the surface with a known-refuted number in hand. See `CRITIQUE.md`.

### The claim under test

`docs/gate-s2-evidence.md` §11, the row verifying `G-3`'s accepted basis, states:

> **HOLDS, and the mechanism is now MEASURED rather than asserted.** `failingCodes` is
> `outcome !== "PASS"`, so UNRESOLVED counts as failing; walking all 50 committed results,
> **exactly two classes are credited only on UNRESOLVED outcomes — `conflicting-block-state`
> and `runtime-code-change-or-proxy-target`** — which is the finding's claim reproduced
> independently.

`docs/v1-1-register.md` §13.4 repeats it: *"T1 basis VERIFIED and MEASURED — exactly two
classes are credited only on UNRESOLVED."* My own reviewer brief (`briefs/r3.md`) repeats it a
third time: *"two classes are credited only on UNRESOLVED outcomes."*

### What is actually true

**Three classes are credited only on UNRESOLVED outcomes, and `conflicting-block-state` is not
one of them — it is credited on NOTHING, because it is the guard's one ruled `GAP`.**

| Class | ABOUT map (from `scripts/check-class-coverage.sh`) | mapped codes actually non-PASS at L3 | credited? |
|---|---|---|---|
| `malformed-calldata-or-unknown-selector` | `EVAL_CALLDATA_UNDECODABLE`, `EVAL_SELECTOR_BOUND`, `EVAL_OPERATION_SUPPORTED` | F036/F037/F038/F040 `EVAL_CALLDATA_UNDECODABLE=UNRESOLVED` only | **credited, UNRESOLVED only** |
| `rpc-simulator-or-context-outage` | 6 outage codes | F045/F046/F047 `EVAL_SIMULATION_UNAVAILABLE=UNRESOLVED` only | **credited, UNRESOLVED only** |
| `runtime-code-change-or-proxy-target` | `EVAL_TARGET_CODE_IDENTITY` | F042/F043 `EVAL_TARGET_CODE_IDENTITY=UNRESOLVED` | **credited, UNRESOLVED only** |
| `conflicting-block-state` | `EVAL_MANDATE_PRINCIPAL_IS_OWNER` | **none** — F048's only non-PASS codes are `EVAL_TARGET_CODE_IDENTITY` and `EVAL_SIMULATION_UNAVAILABLE`, neither of which is in its map | **NOT credited — it is the ruled GAP** |

The guard itself prints `1 GAP: conflicting-block-state` on every run. So the sentence in the
signed pack says a class is credited-on-UNRESOLVED when the same script, in the same run,
prints that it is not credited at all.

### Reproduction (exact)

```bash
cd <worktree>
bash scripts/check-class-coverage.sh | grep -E '^  ok|GAP:'
#   ok    14 of 20 classes exercise the class they name
#   1 GAP: conflicting-block-state

node -e '
const fs=require("fs");
for (const id of ["F048","F042","F043","F036","F037","F038","F040","F045","F046","F047"]) {
  const r=JSON.parse(fs.readFileSync("fixtures/corpus/results/"+id+".json","utf8"));
  const L3=r.layers.find(l=>l.layer==="L3_full_conformance");
  console.log(id, r.class, "verdict="+L3.verdict,
    L3.checks.filter(c=>c.outcome!=="PASS").map(c=>c.code+"="+c.outcome).join(" "));
}'
```

Observed (verbatim):

```
F048 conflicting-block-state              verdict=REVIEW EVAL_TARGET_CODE_IDENTITY=UNRESOLVED EVAL_SIMULATION_UNAVAILABLE=UNRESOLVED
F042 runtime-code-change-or-proxy-target  verdict=REVIEW EVAL_TARGET_CODE_IDENTITY=UNRESOLVED
F043 runtime-code-change-or-proxy-target  verdict=BLOCK  EVAL_TARGET_CODE_IDENTITY=UNRESOLVED
F036 malformed-calldata-or-unknown-selector verdict=BLOCK  EVAL_CALLDATA_UNDECODABLE=UNRESOLVED EVAL_SIMULATION_SUCCEEDS=VIOLATION
F037 malformed-calldata-or-unknown-selector verdict=REVIEW EVAL_CALLDATA_UNDECODABLE=UNRESOLVED
F038 malformed-calldata-or-unknown-selector verdict=BLOCK  EVAL_CALLDATA_UNDECODABLE=UNRESOLVED EVAL_SIMULATION_SUCCEEDS=VIOLATION
F040 malformed-calldata-or-unknown-selector verdict=BLOCK  EVAL_CALLDATA_UNDECODABLE=UNRESOLVED EVAL_SIMULATION_SUCCEEDS=VIOLATION
F045 rpc-simulator-or-context-outage      verdict=REVIEW EVAL_SIMULATION_UNAVAILABLE=UNRESOLVED
F046 rpc-simulator-or-context-outage      verdict=BLOCK  EVAL_PURCHASE_RESOURCE=VIOLATION EVAL_SIMULATION_UNAVAILABLE=UNRESOLVED
F047 rpc-simulator-or-context-outage      verdict=BLOCK  EVAL_SIMULATION_UNAVAILABLE=UNRESOLVED
```

Note F036/F038/F040's `EVAL_SIMULATION_SUCCEEDS=VIOLATION` is **not in that class's map**, so it
does not credit the class; and F046's `EVAL_PURCHASE_RESOURCE=VIOLATION` is not in the outage
class's map either. Both were checked against the map rather than against the raw `failing` list.

Full per-class computation: `evidence/r3/data/class-credit.txt`.

### Why this is a finding and not a re-report

`G-3` is recorded and ACCEPTED (D-051(b), §11.0) — re-reporting it would not be a finding. What
is new is that **the item is worse than recorded, and its recorded basis is false in both
directions**: it undercounts (2 vs 3) and it misidentifies (it names the one class the same
guard reports as an uncovered GAP). The common brief states that showing a recorded item is
worse than recorded IS a finding, and my directed brief states it twice for exactly this reason.

### Why it matters beyond arithmetic

1. **The acceptance rests on the wrong scope.** G-3 was downgraded MEDIUM → LOW and accepted on
   a measurement presented as independent reproduction. The true set is 50% larger and includes
   `malformed-calldata-or-unknown-selector` — a class whose §7.1 name explicitly claims *unknown
   selector* coverage while `EVAL_SELECTOR_BOUND` is **never** a VIOLATION anywhere in the
   corpus. That class is credited entirely on "the engine could not decode the bytes", which is
   an evidence gap, not a demonstration that selector binding is enforced.
2. **The naming error inverts the guard's own taxonomy.** `conflicting-block-state` is
   `status: GAP` — the strongest not-covered label the script has, meaning *owed a fixture*.
   Recording it instead as a credited-but-weakly class makes the ratchet look one class
   healthier and one GAP softer than it is.
3. **It is a third repetition of the same figure across three artifacts** (S2 pack, register,
   reviewer brief) with nothing mechanical asserting it — the "a published number can be true
   once" shape, except this one was never true.

### Recommended reclassification, offered not decided

State the derived figure from the guard rather than in prose, or have
`check-class-coverage.sh` print the credit OUTCOME alongside the credit, so the sentence cannot
disagree with the run. That is the same repair G-5 already received one directory away.

---

## R3-F2 — The ablation report's "CHECK ON THE PARTITION" is not one: it compares two hand-maintained copies of the same list, and its DRIFT diagnosis names a set the probe never touched

**Severity: MEDIUM** (false-claim in a generated Gate S2 deliverable / instrument pointed at the wrong thing)
**Confidence: HIGH — reproduced in both directions with a pure, out-of-tree probe.**
**Not recorded.** `G-5` covers the `50` literal and the `F035`/`F051` caveats; nothing in
register §13.4, §14 or §11.0 mentions `WITHHELD`.

### The claim under test

`ts/src/ablation/report.ts:394-408` emits, into `docs/ablation-report.md`:

> This splits the fixtures L3 adds by whether they turn on one of those fields — **derived from
> each fixture's failing set, not asserted** — so the table below is a **CHECK ON THE PARTITION**
> rather than a description of it. The second row must be empty. **If it ever is not, a code has
> drifted into the mandate-conformance set that does not belong there** …

### What it actually compares

The partition is `MANDATE_CONFORMANCE_CODES`, exported from `ts/src/ablation/layers.ts` and used
by `runLayer` to build L2 (`runChecks(input).filter((c) => !MANDATE_CONFORMANCE_CODES.has(c.code))`).

The "check" is computed against `WITHHELD` — a second, inline, hand-typed `new Set([...])` in
`report.ts:377-386` holding the same eight strings. **`report.ts` does not import
`MANDATE_CONFORMANCE_CODES`, and nothing anywhere asserts the two agree:**

```
$ grep -rn 'WITHHELD' ts/ scripts/ docs/ --exclude-dir=node_modules
ts/src/ablation/report.ts:377    const WITHHELD = new Set([
ts/src/ablation/report.ts:390    const onWithheld = ...
ts/src/ablation/report.ts:391    const onOther   = ...
```
Zero hits in `ts/test/`. (`ablation.test.ts` does guard `MANDATE_CONFORMANCE_CODES` — a prefix
criterion and nine named exclusions — which is precisely why the duplicate is the weak copy.)

### Reproduction

Pure probe, **no worktree mutation**: `report.ts` is copied out of tree, its one relative import
rewritten to an absolute path, `WITHHELD` varied, and `buildReport()` called on the real
`loadInputs()` of the committed corpus.

```bash
P=<scratchpad>/probes ; W=<worktree>
sed 's#from "./layers.ts"#from "'"$W"'/ts/src/ablation/layers.ts"#' \
    "$W/ts/src/ablation/report.ts" > "$P/report-copy.ts"
sed 's#^        "EVAL_PURCHASE_RESOURCE",$##'                "$P/report-copy.ts" > "$P/report-dropRes.ts"
sed 's#^        "EVAL_APPROVAL_SPENDER",$#&\n        "EVAL_MANDATE_ACTIVE",#' \
                                                             "$P/report-copy.ts" > "$P/report-addMandateActive.ts"
cd "$W/ts" && node "$P/withheld-probe.ts"
```

Observed (verbatim — `evidence/r3/data/withheld-partition-probe.txt`):

```
CONTROL (WITHHELD as committed):
- Turns on a §7.2-withheld field: **8** — F012, F013, F014, F015, F016, F046, F050, F055
- Turns on another mandate-derived check: **0** — none, as the criterion requires

VARIANT A — EVAL_PURCHASE_RESOURCE removed from WITHHELD ONLY
            (MANDATE_CONFORMANCE_CODES untouched, so the PARTITION is unchanged):
- Turns on a §7.2-withheld field: **4** — F013, F014, F015, F016
- Turns on another mandate-derived check: **4** — F012, F046, F050, F055 **← DRIFT**

VARIANT B — EVAL_MANDATE_ACTIVE (mandate VALIDITY, which D-034 puts in L2) added to WITHHELD:
- Turns on a §7.2-withheld field: **8** — F012, F013, F014, F015, F016, F046, F050, F055
- Turns on another mandate-derived check: **0** — none, as the criterion requires
```

### What the two variants establish

* **Variant A — it fires on the COPY, and its diagnosis is false.** The partition
  (`MANDATE_CONFORMANCE_CODES`) is byte-identical to the committed one; the committed corpus
  results are byte-identical; only the duplicate list moved. The report nonetheless prints
  `**← DRIFT**` and tells the reader *"a code has drifted into the mandate-conformance set that
  does not belong there"* — about a set the probe never touched.
* **Variant B — it does not test D-034's criterion at all.** `EVAL_MANDATE_ACTIVE` is the
  canonical example of what D-034 assigns to L2 ("mandate VALIDITY, not purpose"), and
  `ablation.test.ts` names it explicitly in *"does not readmit anything D-034 moved to L2"*.
  Adding it to `WITHHELD` changes nothing: the row accepts any SUPERSET of the codes that
  actually drove the L3-only detections.

So the row is a consistency check between two copies of one list, one of which is guarded by
tests and one of which is guarded by nothing. It can catch a **one-sided** edit to
`MANDATE_CONFORMANCE_CODES` (and only after a corpus re-run moves `results/`), it **false-alarms
with a wrong diagnosis** on a one-sided edit to `WITHHELD`, and it is **blind to the two-sided
edit** — which is the edit anybody applying the criterion would actually make, because the
criterion is stated in both files.

### Why it matters

1. `docs/ablation-report.md` is a Gate S2 pass condition (D-009). The sentence
   *"a CHECK ON THE PARTITION rather than a description of it"* is a claim stronger than its
   evidence, in the exact document the gate rests on, describing an instrument aimed at
   something other than what it names.
2. It is the **third** copy of D-034's criterion — the prose in `layers.ts`, the guarded set in
   `layers.ts`, and the unguarded duplicate in `report.ts`. The register's own house rule for
   this repository is that duplication is its demonstrated failure mode.
3. The repair is one line: `import {MANDATE_CONFORMANCE_CODES} from "./layers.ts"` and use it,
   or assert set-equality in `ablation.test.ts`. Either makes the printed sentence true.
   **Offered, not decided** — changing what the report asserts is not an agent's call.

---

## R3-F3 — The D-011(b) leak guards let evaluator output reach a labeller view under an innocuous name one level below where the allowlist reaches. The A-032 hypothesis is now DEMONSTRATED, and the half that was repaired is not the half that A-028 F-3 actually used

**Severity: MEDIUM** (instrument-defect on the guard protecting the corpus's ground truth)
**Confidence: HIGH — four synthetic views, two controls, run against the exported guards themselves.**

### Standing of the prior record — stated before the claim

`docs/decisions.md:132` (A-032) records this as an **undemonstrated hypothesis**:

> **Two hypotheses the reviews raised and did not demonstrate, recorded so they are not lost.**
> (a) `leakage.ts`'s `isDeclared` is depth-blind and `assertViewShape` checks only the top level
> and `observedEnvironment`, so an allowlisted key name nested inside `mandate`, `policy` or
> `action` would bypass both — pre-existing, and **no live path was constructed, since all three
> are typed payloads.**

`ts/src/corpus/leakage.ts:108-115` then records the repair, and presents the gap as closed:

> **THE EXEMPTION IS NOW SCOPED TO THE DEPTH IT WAS DECIDED AT.** … An independent review
> raised it as a hypothesis it had not demonstrated. **It is a real gap and it is cheaper to
> close than to argue about** …

**The repair closed the DENYLIST half (`isDeclaredAt`) and did not touch the ALLOWLIST half
(`assertViewShape`).** And the route it closed — an *allowlisted* name nested in a payload — is
not the route the real incident used. **A-028 F-3's actual leak was an INNOCUOUS name**
(`calldataDecodedByASupportedSchema`, `calldataDecodeFailureReason`), which the denylist cannot
see by construction and which only the shape allowlist stops. That route is still open one level
below where `assertViewShape` looks.

### Reproduction

Pure probe against the two exported guards; **nothing in the worktree is modified**.

```bash
cd <worktree>/ts && node <scratchpad>/probes/leakage-probe.ts
```

Observed (verbatim — `evidence/r3/data/leakage-probe.txt`):

```
CONTROLS — the shapes the guards were built for
C1  top-level  engineVerdict: 'BLOCK'                    noLeakage THREW   viewShape THREW   (blocked)
C2  observedEnvironment.l3Verdict: 'BLOCK'               noLeakage THREW   viewShape THREW   (blocked)
C3  observedEnvironment.calldataDecodedByASupportedSchema
       (A-028 F-3's REAL field, innocuous name, depth 1) noLeakage PASSED  viewShape THREW   (blocked)
C4  action.verdict: 'BLOCK'  (forbidden WORD, depth 1)   noLeakage THREW   viewShape PASSED  (blocked)

PROBES — innocuous name, one level below where the allowlist reaches
P1  action.priorAssessment = 'BLOCK: EVAL_PURCHASE_RESOURCE'
                                                         noLeakage PASSED  viewShape PASSED  <<< LEAK
P2  mandate.engineNote = 'the engine blocks this on resource'
                                                         noLeakage PASSED  viewShape PASSED  <<< LEAK
P3  observedEnvironment.entitlements[0].priorAssessment = 'BLOCK'
                                                         noLeakage PASSED  viewShape PASSED  <<< LEAK
P4  observedEnvironment.entitlements[0].engineFailingCodes = ['EVAL_PURCHASE_RESOURCE']
                                                         noLeakage THREW   viewShape PASSED  (blocked)
```

### What each row establishes

* **C3 is the control that makes this a finding rather than a restatement.** It shows the
  allowlist genuinely closes A-028 F-3's route **at `observedEnvironment` depth 1** — so the
  guard works exactly where it was aimed.
* **P3 is the same shape one level deeper, inside the one container the shape guard is pointed
  at**, and it passes both. `assertViewShape` inspects `Object.keys(view)` and
  `Object.keys(view.observedEnvironment)` and stops; array members and nested objects are never
  shape-checked.
* **P1 and P2** show the same for `action` and `mandate` — the containers A-032 named — using an
  innocuous name rather than an allowlisted one, which is why the depth fix does not reach them.
* **P4 is the second control**: `engineFailingCodes` contains `failing`, so the denylist still
  works at depth. The gap is precisely *innocuous name × below the allowlist's reach*, which is
  the exact intersection A-028 F-3 occupied.

### Why it matters

`leakage.ts`'s own header states the stake: *"A labeller view that leaked a verdict would turn
the corpus from an independent bar into a self-graded suite, and the leak would be INVISIBLE in
a green run … this is the check that would notice the accidental version."* An accidental
version — a debugging field left in `run.ts` inside an entitlement record, or a note attached to
`action` — is not noticed. Nor would the deep gate notice: the committed views would be
regenerated with the field present, so the file-by-file VIEWCHECK and `_digests.json` would both
agree with the leaked artifacts.

### What this finding does NOT claim

No such field exists in the committed views today. I checked: the current views pass both guards,
and `assertViewShape` would reject any new **top-level or `observedEnvironment`-immediate** field.
This is a live hole in a guard, not a live leak.

### Repair, offered not decided

Recurse `assertViewShape` with a declared shape per container, or — cheaper — apply the
allowlist at every depth inside `observedEnvironment` and reject undeclared keys inside `action`,
`mandate` and `policy` against their payload types. **Either changes what the corpus guarantees
about its own ground truth, so it is John's call, not an agent's.**

---

## R3-F4 — Three signed payload fields are consulted by nothing, and only one of them carries the disclosure D-025 exists to require

**Severity: MEDIUM** (spec-gap; a declared-but-unenforced constraint in a SIGNED §5 payload)
**Confidence: HIGH — exhaustive grep over engine, vault and verifier; no mutation needed.**
**Not recorded** anywhere in `docs/` (grep below).

### The standard the project set for itself

`Sentinel_Protocol_Lab_Proposal_v0_2.md:554`, D-025, about `PolicyPayload.allowedCallGraphHash`:

> `PolicyPayload.allowedCallGraphHash` (§5.2) is **reserved and not yet consulted**: a policy
> declaring any other call graph has no effect in v1. **Stated rather than left implicit because
> a declared-but-unenforced field is one an owner could reasonably believe they had constrained
> something with.**

§5.7.1 repeats it inline: *"`EVAL_CALL_GRAPH_EXPECTED` (enforces an empty graph;
`allowedCallGraphHash` is reserved per D-025)"*.

### Two more policy fields and one mandate field are in exactly that position, undisclosed

| Field | §5 status | Read by the engine? | the vault? | the D-010 verifier? | disclosed as reserved? |
|---|---|---|---|---|---|
| `PolicyPayload.allowedCallGraphHash` | listed §5.2 | no | no (hash only) | no (type list only) | **YES — D-025** |
| `PolicyPayload.allowedTargetsHash` | listed §5.2 | **no** | no (hash only) | no (type list only) | **NO** |
| `PolicyPayload.allowedSelectorsHash` | listed §5.2 | **no** | no (hash only) | no (type list only) | **NO** |
| `MandatePayload.purposeKind` | listed §5.1 | **no** | no (hash only) | no (type list only) | **NO** |

### Reproduction

```bash
# every policy field the conformance engine actually consults
grep -o 'policy\.[a-zA-Z]*' ts/src/evaluate/checks.ts | sort -u
#   policy.allowedOperation
#   policy.failureMode
#   policy.maxAllowanceIncreaseBaseUnits
#   policy.maxNativeValueWei
#   policy.validAfter
#   policy.validUntil
#   -> 6 of PolicyPayload's 13 fields; allowedTargetsHash, allowedSelectorsHash and
#      allowedCallGraphHash are absent

grep -o 'mandate\.[a-zA-Z]*' ts/src/evaluate/checks.ts | sort -u
#   -> 14 fields; purposeKind is absent

# every other occurrence in the repository is a TYPE STRING or a STRUCT HASH, never a comparison
grep -rn 'allowedTargetsHash\|allowedSelectorsHash' ts/src/ verifier/ contracts/src/
#   ts/src/signer/eip712.ts      : type string + word.bytes32() encoding
#   ts/src/evaluate/hashes.ts    : type string + hashStruct operand
#   ts/src/signer/protocol.ts    : field type + wire validation only
#   ts/src/corpus/run.ts, tools/*: fixture CONSTRUCTION
#   contracts/src/types/...      : struct member + hashStruct operand
#   verifier/eip712.py           : type tuple only
#   -> zero comparisons anywhere

grep -n 'purposeKind' Sentinel_Protocol_Lab_Proposal_v0_2.md
#   308:    purposeKind          <- the ONLY occurrence: a bare name in the §5.1 field list

# and nothing in docs/ records any of the three
grep -rn 'allowedTargetsHash\|allowedSelectorsHash' docs/     # -> no matches
grep -rn 'purposeKind' docs/                                  # -> no matches
```

### Why this is not merely tidy-up

1. **The two policy fields read as the policy's allowlist, and there is none.** The vault has its
   own `allowedTarget` / `allowedSelector` mappings, fixed in the constructor and unrelated to
   these hashes. An owner who narrows the POLICY's target set and re-activates it changes
   nothing at all. That is verbatim the situation D-025's sentence describes.
2. **The corpus's own fixtures show the fields are not even populated meaningfully.**
   `ts/src/corpus/run.ts:247,561` sets them to `keccak256(stringToBytes("targets"))` and
   `keccak256(stringToBytes("selectors"))` — the hash of the ASCII words, not of any address or
   selector list. All 50 committed views carry those two constants (see
   `evidence/r3/data/corpus-variance.txt`: both fields have exactly one distinct value across
   the corpus). Nothing anywhere derives or checks them, so no fixture could reveal it.
3. **`purposeKind` is the mandate's PURPOSE field and the product's central claim is purpose
   conformance.** §4.2 Case 3 is "the action can be mechanically valid and still buy the wrong
   thing"; the mandate carries a field literally named `purposeKind`; no check reads it. The
   purpose semantics are carried entirely by `resourceId`, `beneficiary`, `durationSeconds` and
   `recurringAllowed`. That may well be the right design — **but §5.1 gives `purposeKind` no
   prose at all, so a reimplementer working from the specification (which is the whole D-010
   experiment) has nothing telling them it is inert.** D-010 has already produced two findings of
   exactly this shape (§5.5.1's refusal record, §5.2's intersection rule); this is a third
   waiting to happen.
4. **§5.7.1's check-coverage guard cannot catch it.** `scripts/check-eval-codes.sh` fails when a
   check exists in the ENGINE and not in the document. It has no arm in the other direction — a
   PAYLOAD FIELD that exists in the document and is enforced by no check. The instrument is
   one-directional and the document says so ("It asserts COVERAGE, not correctness"), but the
   direction it omits is the one this finding lives in.

### What I am NOT claiming

I am not claiming the fields must be enforced in v1. Reserving them may be entirely correct.
**The finding is the missing disclosure**, measured against the standard D-025 set in this same
document for the identical situation one field away. Whether to disclose, enforce, or remove is
a change to what the product guarantees and is John's, not an agent's.

---

## R3-F5 — The vault's §3.3(5) receipt binding folds two conditions into one check and only the MANDATE half is tested. Deleting the POLICY half leaves Foundry 75/75 green — and `scripts/mutate.sh`'s own S5 reports the check CAUGHT

**Severity: MEDIUM** (surviving mutation against a vault security check; instrument-defect in the
project's own mutation harness; an un-generalised repair of the identical defect)
**Confidence: HIGH — reproduced with its control; the sibling half is killed by exactly one test.**
**Not recorded.** The identical defect in the TypeScript engine is `D-05`, adjudicated CONFIRMED
and **FIXED (A-068)**. The Solidity twin was not touched.

### The check

`contracts/src/SentinelVault.sol:336-339`:

```solidity
if (receipt.actionHash != T.hashAction(action)) revert ReceiptActionMismatch();
if (receipt.mandateHash != action.mandateHash || receipt.policyHash != action.policyHash) {
    revert ReceiptBindingMismatch();
}
```

`_checkAction`'s docstring names this pair as **invariant §3.3(5)**.

### Reproduction

Harness: `scratchpad/probes/mutate.sh` (exact-occurrence anchor, `cmp` against pristine,
build-must-succeed, bytecode-must-move — see DEAD-PROBES). Baseline before both: 75/75 pass.

```bash
# M17 — delete the MANDATE half, keep the policy half   (CONTROL)
'receipt.mandateHash != action.mandateHash || receipt.policyHash != action.policyHash'
  ->  'receipt.policyHash != action.policyHash'

# M18 — delete the POLICY half, keep the mandate half   (PROBE)
'receipt.mandateHash != action.mandateHash || receipt.policyHash != action.policyHash'
  ->  'receipt.mandateHash != action.mandateHash'

forge test --root contracts
```

Observed:

```
M17  [FAIL: next call did not revert as expected] test_receiptClaimingADifferentMandateIsRejected()
     Ran 5 test suites: 74 tests passed, 1 failed, 0 skipped (75 total tests)      -> KILLED

M18  Ran 5 test suites: 75 tests passed, 0 failed, 0 skipped (75 total tests)      -> SURVIVED
```

Raw: `evidence/r3/mutations/M17-receiptMandateHalf.full.txt`,
`evidence/r3/mutations/M18-receiptPolicyHalf.full.txt`, and `mutations/log.txt`.

The control is what makes this a finding rather than an observation about a weak suite: the
**same conjunction, same statement, same error selector** — one half has a dedicated test, the
other has none. `grep -rn 'ReceiptBindingMismatch' contracts/` returns the declaration, the
`revert`, and **one** test (`test_receiptClaimingADifferentMandateIsRejected`, backstops:308),
whose only perturbation is `r.mandateHash = keccak256("a mandate this action was never
evaluated against")`.

### The project's own mutation harness reports this check covered

`scripts/mutate.sh:849`:

```
run_sol_mutation "S5  vault: delete the ReceiptBindingMismatch check" \
    "contracts/src/SentinelVault.sol" \
    '        if (receipt.mandateHash != action.mandateHash || receipt.policyHash != action.policyHash) {
            revert ReceiptBindingMismatch();
        }
' \
    ''
```

**S5 deletes the WHOLE conjunction.** The mandate-half test then fires, S5 reports CAUGHT, and
the harness has no mutant that perturbs the policy half alone. This is the common brief's
"an instrument can exist and point at the wrong thing", inside the instrument built to measure
exactly this.

### It is an un-generalised repair of the identical finding

`D-05` — *"EVAL_ACTION_BINDS_MANDATE_AND_POLICY folds two conditions under one code and only the
mandate half is exercised; the policy half can be deleted undetected"* — was adjudicated
CONFIRMED at MEDIUM and register §13.4 records **"FIXED (A-068) — a check row per HALF of the
conjunction"**. That repair was applied to `ts/src/evaluate/checks.ts`. The Solidity conjunction
carrying the same §3.3(5) invariant, with the same shape and the same mandate/policy pairing, was
left as it was. **Same defect, same argument, one directory away.**

### What the surviving mutant actually permits

The vault would accept a signed receipt whose `policyHash` names a policy the action was never
bound to. `receipt.actionHash` still pins the action (and `action.policyHash` still has to equal
`activePolicyHash`), so this is not a path to executing under an inactive policy — it is the loss
of the receipt's own attestation that it was evaluated against the policy the action names. That
is defence-in-depth rather than the last line, which is why I assign MEDIUM rather than High.
**The argument for High, stated so the adjudicator can weigh it:** the receipt is the credential
§3.3(6) rests on, `_checkAction`'s docstring cites this exact pair as invariant §3.3(5), and the
S2 pack's Gate 6 evidence rests on the deterministic Foundry suite alone (A-073/D-054(b) measured
the invariant campaign's marginal contribution at zero) — so nothing else is behind it.

### Repair, offered not decided

Split the conjunction into two `if`s with two errors (mirroring `MandateNotActive` /
`PolicyNotActive` two functions up, which ARE separate), add the sibling test, and add a
`mutate.sh` mutant per half. Changing the error surface changes the vault's ABI, so it is not an
agent's call.

---

## R3-F6 — All three of the vault's timestamp comparisons are unpinned by one second; the value ceiling is not. D-06's repair was applied to the TypeScript engine and never to the Solidity vault

**Severity: MEDIUM** (three surviving mutations against §5.7 validity windows; an
un-generalised repair of an already-adjudicated finding)
**Confidence: HIGH — three survivors and a killed control, all from the same harness.**
**Not recorded for the vault.** `D-06` is the identical finding for `ts/src/evaluate/**`,
adjudicated CONFIRMED at MEDIUM and **FIXED (A-068 pinned four of five; A-072 "closed all ten
comparison edges")**. Register §14 records the residual as being about which ceiling is
*correct*, not about the vault's edges — which were never swept.

### The three comparisons

```solidity
_checkAction   : if (block.timestamp > action.deadline)  revert ActionExpired();
_checkReceipt  : if (block.timestamp > receipt.expiresAt) revert ReceiptExpired();
executeWithOverride
               : if (block.timestamp > auth.expiresAt)   revert OverrideExpired();
```

### Reproduction

Widen each by exactly one second, casting to `uint256` first so a `type(uint64).max` fixture
cannot panic instead of reaching the widened branch (see DEAD-PROBES DP-3):

```
MB2  block.timestamp > action.deadline     ->  block.timestamp > uint256(action.deadline) + 1
MB3  block.timestamp > receipt.expiresAt   ->  block.timestamp > uint256(receipt.expiresAt) + 1
MB4  block.timestamp > auth.expiresAt      ->  block.timestamp > uint256(auth.expiresAt) + 1
MB1  action.valueWei > maxNativeValueWei   ->  action.valueWei > maxNativeValueWei + 1   (CONTROL)
```

Observed (`mutations/log.txt`, full outputs at `mutations/MB*.full.txt`):

```
MB1-valuecapOffByOne        campaign=SURVIVED  full=KILLED     <- the control fires
MB2-deadlineOffByOne        campaign=SURVIVED  full=SURVIVED
MB3-receiptExpiryOffByOne   campaign=SURVIVED  full=SURVIVED
MB4-ovrExpiryOffByOne       campaign=SURVIVED  full=SURVIVED
```

**The control is what makes this a finding.** The value ceiling's off-by-one is caught; all
three time windows' are not. The suite therefore has an at-boundary assertion for one of the
vault's four limit comparisons and none for the other three.

### Why the three expiry tests do not catch it

They exist, and each warps far past its window rather than to `limit + 1`:

| Test | window | warp |
|---|---|---|
| `test_expiredReceiptIsRejected` (`SentinelVault.t.sol:423`) | receipt lives 10 min | `+11 minutes` |
| `test_expiredActionIsRejected` (`SentinelVault.t.sol:432`) | deadline `+30 minutes` | `+31 minutes` |
| `test_expiredOverrideIsRejected` (`backstops.t.sol:497`) | override lives 10 min | `+11 minutes` |

Each proves "an hour past expiry is rejected". None proves "one second past expiry is rejected",
and none proves "exactly at expiry is still accepted". A-072's whole argument for the engine was
that these are different assertions and the second is the one that drifts.

### The pattern, stated because it is the third instance in this report

`D-06` for the engine, `D-05` for the engine (see R3-F5), and A-028 F-3's leak allowlist (see
R3-F3) were each repaired **on the surface the reviewer demonstrated** and not on the identical
structure one language, one file, or one nesting level away. R3-F5 and R3-F6 are both *the same
already-adjudicated finding, in Solidity*. The common brief names this shape — *"a repair can
generalise the DEMONSTRATION rather than the ARGUMENT"* — and this is a measured instance of it
across two independent findings in one contract.

### Practical impact, stated plainly and not inflated

A one-second-late expiry is not an exploit; `_checkAction`'s own NatSpec argues correctly that
these are validity windows whose manipulable range is seconds and whose failure mode is a
credential expiring marginally early or late. **The finding is the instrument, not the second.**
A comparison edge no test can move is one that can be edited to `>=`, to `<`, or to `+ 3600`
with a green gate, and the suite would report the vault sound throughout.

### The other direction, now measured: UNPINNED BOTH WAYS

Narrowing (`>` → `>=`, i.e. **reject** a credential that is exactly AT its limit) was run as
`MN1`–`MN3`, with the value ceiling as the control again:

```
MN1-deadlineNarrow            campaign=SURVIVED  full=SURVIVED
MN2-receiptExpiryNarrow       campaign=SURVIVED  full=SURVIVED
MN3-ovrExpiryNarrow           campaign=SURVIVED  full=SURVIVED
MN4-valuecapNarrow-CONTROL    campaign=SURVIVED  full=KILLED       <- the control fires
```

**So all three timestamp comparisons are unpinned in BOTH directions and the value ceiling is
pinned in both.** Eight mutations, two controls, one clean split:

| comparison | widen by 1s / 1 wei | narrow to `>=` |
|---|---|---|
| `action.deadline` | **SURVIVED** | **SURVIVED** |
| `receipt.expiresAt` | **SURVIVED** | **SURVIVED** |
| `auth.expiresAt` | **SURVIVED** | **SURVIVED** |
| `maxNativeValueWei` (control) | KILLED | KILLED |

`MN4` is killed by `test_LIMIT_nativeCeilingIsPerActionAndBoundsNoAggregate`, which executes 100
actions at *exactly* the cap — the at-boundary assertion the three time windows do not have.
"Unpinned in both directions" is verbatim `D-10`'s and `D-06`'s wording for the same defect one
language away.

---

## R3-F7 — FIVE of the vault's eight events can be made to state something FALSE with the suite 75/75 green. §3.3(2)'s "logged" requirement is asserted for the three events D-043 touched and for none of the five it did not

**Severity: MEDIUM** (four surviving mutations against the onchain audit log; the same
"fields read by no assertion and can be made to state the opposite" shape as `D-09`)
**Confidence: HIGH — four survivors and three killed controls in the same batch.**
**Not recorded.**

### The claim under test

`SentinelVault.sol:96-107`, the D-043 comment introducing `OverrideAuthorized`:

> §3.3(2) requires that override be "separately authenticated, unavailable to the agent, and
> LOGGED". The first two were enforced; the third was not. … **Every other item in §3.3(2)
> already had a dedicated event; override was the omission.**

That sentence is true about **declaration** and it reads as a statement about **coverage**.
Measured: the other events exist and none of them is asserted anywhere.

```
$ grep -rn 'expectEmit' contracts/test/*.sol
backstops.t.sol:474   -> ActionExecuted
backstops.t.sol:483   -> Recovered
backstops.t.sol:757   -> OverrideAuthorized
```
Three `expectEmit` calls for eight events. `grep -rn 'SignerRotated' contracts/src contracts/test
scripts/ ts/` returns **the declaration and the `emit`, and nothing else.**

### Reproduction

Each mutation makes one event report something the transaction did not do. Full suite after each:

```
M38-signerRotatedEventOrder    swap `signer = newSigner;` above the emit, so
                               SignerRotated(previousSigner, newSigner) logs the NEW
                               signer as the PREVIOUS one                     -> SURVIVED (75/75)
MEV1-mandateActivatedArg       emit MandateActivated(bytes32(0))              -> SURVIVED (75/75)
MEV3-policyActivatedArg        emit PolicyActivated(bytes32(0))               -> SURVIVED (75/75)
MEV4-pausedSetArg              emit PausedSet(!value)                         -> SURVIVED (75/75)
MEV2b-mandateRevokedArg        emit MandateRevoked(previous & bytes32(0)), so the
                               revoked mandate's hash is logged as zero          -> SURVIVED (75/75)

CONTROLS, same batch, same harness:
M35-overrideEventDeleted       delete `emit OverrideAuthorized(...)`          -> KILLED
M36-overrideEventReasonHash    emit OverrideAuthorized(..., bytes32(0), ...)  -> KILLED
M37-actionExecutedViaOverride  emit ActionExecuted(..., !viaOverride)         -> KILLED
```

Raw: `mutations/M38-*.full.txt`, `mutations/MEV{1,3,4}-*.full.txt`, `mutations/M3{5,6,7}-*.full.txt`.
(`MEV2-mandateRevokedArg` in its first shape was a **DEAD PROBE — build-failed**: `previous`
becomes unused under `deny = "warnings"`. It is NOT counted as a pass; it was re-run as `MEV2b`
in a variable-preserving shape (`previous & bytes32(0)`) and **survived 75/75**. See
DEAD-PROBES.)

**All five events D-043 did not touch are unasserted; all three it did touch are asserted.
Five of eight can be made to state something false; three of eight cannot.** The split is exact.

### Why M38 is the sharp one

`SignerRotated(previousSigner, newSigner)` is the vault's only onchain record of **which key was
authoritative when**. The vault has two accepted LIMIT tests that turn entirely on rotation
history — `test_LIMIT_reinstatingARotatedOutSignerRevivesItsOldReceipts` and
`test_LIMIT_receiptFromAFutureSignerGoesLiveOnRotation` — and `_checkReceipt`'s own corrected
comment states the property they pin: *"nothing here binds a receipt to the EPOCH in which its
signer was active. Rotation is not revocation."* **The onchain log is therefore the only artifact
from which an auditor could reconstruct the epochs**, and its `previousSigner` argument is
asserted by nothing. Two lines reordered — a plausible, innocent-looking edit — and every
rotation logs `SignerRotated(newSigner, newSigner)` with a green gate.

### Why this is not "the tests are thin"

`M35`/`M36`/`M37` are the paired controls, and they fire. The suite **does** assert event
arguments where somebody decided to. The finding is that the decision was made once, for the
event a reviewer had just complained about, and the identical argument — *"an override with no
recorded reason is exactly the event a hostile reader would ask about first"* — applies verbatim
to a pause that logs the wrong state, a mandate activation and a mandate REVOCATION that both log
the zero hash, and a signer rotation that erases the outgoing key. **This is the third measured instance in this report of a
repair applied to the demonstration and not to the argument** (with R3-F5 and R3-F6).

### Repair, offered not decided

Add an `expectEmit` per owner control, and a `mutate.sh` mutant per event argument. Cheap; it
changes no behaviour and no ABI, so unlike R3-F5's split it is not a product change — but adding
gate-asserted claims is still a decision about what the pack certifies.

---

## R3-F8 — The D-10 repair pinned 2 of the 9 case comparisons and 1 of the 2 field swaps. The identical field swap 30 lines above the one it fixed still survives — and the repair's own MEASURED premise is false

**Severity: MEDIUM** (nine surviving mutations against binding comparisons; a false measured
claim in the repair's justification; `D-10(c)` re-classified MEDIUM by John at D-056(a))
**Confidence: HIGH — nine survivors, three killed controls, one counterexample from the
committed corpus.**
**`D-10` is recorded and marked FIXED (A-076).** This reports that **the repair did not reach
the argument it states**, which is a different claim from re-reporting D-10.

### The repair's own stated argument

`ts/test/evaluate.checks.test.ts:424-429`:

> **THE ARGUMENT: a binding comparison must be pinned to the FIELD it names and to the VALUE it
> names, independently of how the corpus happens to spell either.** The corpus is single-case
> throughout — measured: 9 distinct addresses across all 50 fixtures, zero non-lowercase
> occurrences — and **every fixture sets `principal === beneficiary`**. So the corpus cannot
> distinguish a normalised comparison from an unnormalised one, **nor the beneficiary from the
> principal**, and neither could anything else in the suite.

### (a) Seven of the nine case-normalisation sites are unpinned

`ts/src/evaluate/checks.ts` performs nine `.toLowerCase()` comparisons. The D-10 tests pin two.
I dropped the normalisation at each of the nine — `x.toLowerCase() === y.toLowerCase()` →
`x === y` — and ran the full 513-test suite each time. Baseline: 513/513, exit 0.

```
T01-case-principalIsOwner       checks.ts:217  EVAL_MANDATE_PRINCIPAL_IS_OWNER  -> SURVIVED
T02-case-vaultBound             checks.ts:228  EVAL_VAULT_BOUND                 -> SURVIVED
T03-case-targetCodeIdentity     checks.ts:278  EVAL_TARGET_CODE_IDENTITY        -> SURVIVED
T04-case-purchaseResource       checks.ts:353  EVAL_PURCHASE_RESOURCE           -> SURVIVED
T05-case-purchaseBeneficiary    checks.ts:358  EVAL_PURCHASE_BENEFICIARY        -> SURVIVED
T06-case-approvalSpender        checks.ts:388  EVAL_APPROVAL_SPENDER            -> SURVIVED
T07-case-nativeDeltaAddress     checks.ts:438  native-delta address match       -> SURVIVED

C08-case-targetBound-CONTROL    checks.ts:238  EVAL_TARGET_BOUND                -> KILLED
C09-case-selectorBound-CONTROL  checks.ts:337  EVAL_SELECTOR_BOUND              -> KILLED
```

`T06` deserves its own line: **`EVAL_APPROVAL_SPENDER` — the check D-10(c) was raised to MEDIUM
about — is pinned for its FIELD and not for its CASE.** The repair added one test to that
check and pinned one of the two properties its own argument names.

### (b) The identical field swap 30 lines above the one D-10(c) fixed still survives

```
C10-field-approvalSpender-CONTROL  checks.ts:388
    decoded.spender.toLowerCase() === mandate.beneficiary.toLowerCase()
 -> decoded.spender.toLowerCase() === mandate.principal.toLowerCase()      -> KILLED  (D-10(c)'s test)

T11-field-purchaseBeneficiary     checks.ts:358
    decoded.beneficiary.toLowerCase() === mandate.beneficiary.toLowerCase()
 -> decoded.beneficiary.toLowerCase() === mandate.principal.toLowerCase()  -> SURVIVED (513/513)
```

Same substitution, same two fields, same file, thirty lines apart. One has a dedicated test; the
other has none.

### (c) The repair's MEASURED premise is false, and its counterexample is the fixture that refutes its conclusion

**"every fixture sets `principal === beneficiary`" is false.** Measured over all 50 committed
labeller views:

```
FIXTURES WHERE mandate.principal != mandate.beneficiary: 1
   F024  wrong-chain-vault-target-mandate-policy
         principal   0x00000000000000000000000000000000deadbeef
         beneficiary 0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266
         callData    0xc188528b   (DemoPay.purchase — it DOES reach EVAL_PURCHASE_BENEFICIARY)
```
`fixtures/corpus/results/F024.json` records
`{"code": "EVAL_PURCHASE_BENEFICIARY", "outcome": "PASS"}`, so under `T11`'s swap it becomes
VIOLATION and F024's committed result record moves.

**The conclusion the premise supports — "the corpus cannot distinguish … the beneficiary from
the principal" — is therefore false as stated.** It is true only of `EVAL_APPROVAL_SPENDER`
(all four approve-schema fixtures set `principal === beneficiary`), and false of
`EVAL_PURCHASE_BENEFICIARY`, which is the check the surviving mutant `T11` lives in.

**LEAD, not a finding — labelled because I did not execute it.** It follows that the deep gate's
`VERDICTCHECK` *would* catch `T11` (F024's result file would move) while `npm test` does not.
**I did not run the corpus** (see COVERAGE) and I am not reporting that as measured. What IS
measured is that `T11` survives the 513-test suite, and that the corpus contains the fixture
whose existence the repair's comment denies.

### (d) A mandate half the corpus can never exercise

```
T12-recurrenceMandateHalf   checks.ts:368
    !decoded.recurring || mandate.recurringAllowed  ->  !decoded.recurring       -> SURVIVED
```
`mandate.recurringAllowed` is `false` in **all 50** committed views
(`evidence/r3/data/corpus-variance.txt`), so the disjunct is never the deciding one and the
whole "the mandate permits recurrence" half of `EVAL_PURCHASE_RECURRENCE` can be deleted with
the suite and the corpus both green. This is `D-05`'s half-a-conjunction shape a third time
(the first two: R3-F5 in the vault, `D-05` itself in the engine).

### Reproduction

`scratchpad/probes/tsmutate.sh` — exact-occurrence anchor, `cmp` against pristine, **`npm run
typecheck` must pass before the suite runs** (a mutant that does not compile is an ERROR, never
a catch), then `npm test`. Per-mutation transcripts: `evidence/r3/ts-mutations/T*.npmtest.txt`.
Summary: `evidence/r3/ts-mutations/log.txt`. Zero dead probes in this batch.

### Repair, offered not decided

The mechanical answer is a table-driven test over every binding comparison in `checks.ts` — one
row per (check, field, spelling) — rather than three hand-written tests for the three instances a
reviewer named. That is the same "assert the STRUCTURE that produces the behaviour" move A-064
made for the fuzz-handler registration, and it is the only shape that does not need a fourth
reviewer to find the fourth instance. **And the false sentence in the comment should be corrected
in place rather than deleted** — F024 is the counterexample and it is worth recording that the
corpus is less blind than the repair believed.
