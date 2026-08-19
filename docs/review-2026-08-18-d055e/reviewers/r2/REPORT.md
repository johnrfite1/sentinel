# REVIEWER 2 — findings

**Commit reviewed:** `7e0ab7f1057de278c09cc803ab4ca266f53399e1` (detached, worktree `w2`)
**Surface:** `ts/src/signer/**`, the Solidity type mirror, `ts/src/evaluate/**`, `ts/src/decode/**`,
`ts/src/simulate/**`, `ts/src/propose/**`, `ts/src/tools/**`; A-072, D-053(b), A-074, A-075/`E3`.

**Baseline before any mutation** (raw logs `baseline-test.txt`, `baseline-typecheck.txt`):
`npm --prefix ts test` -> **513 pass / 0 fail** (after `forge build`, which the TS suite requires);
`npm --prefix ts run typecheck` -> exit 0, no output.

| id | severity | one line |
|---|---|---|
| `R2-F1` | **HIGH** | The E3 repair pinned the SIGNER's reads to one block and left the identical unpinned-read defect standing in the SIMULATOR - the component whose effects the anchor names. The anchor comes from an unpinned `getBlock()` and pins nothing; pre-state, execution and post-state can all be a different block. Three source comments assert the property the code does not have. |
| `R2-F2` | **MEDIUM** | `SIGNER_ANCHOR_NOT_OBSERVED` is not an anchor check on the simulation. It compares two caller-supplied integers to the signer's own head. A-075's residual (c) and `attest.ts:426-431` both describe it as binding the evaluator's simulation. It does not. |
| `R2-F3` | **LOW** | D-09(c)'s third route: `expectedEffects.maxNativeValueWei` records min(mandate, policy) and omits the vault's immutable cap, which the engine's own comment names as the third binding constraint. Reproduced: an **ALLOW** bundle attesting a ceiling **500x above** what can ever execute - the identical false statement and identical ratio that A-076's own docstring gives as the reason (c) had to be fixed. |
| `R2-F4` | **MEDIUM** | A-074's residual (c) says the `description` gap is "Recorded in the register". It is not: the register contains no entry for it, and the one register bullet that names `decodedSelectorAndParameters` is a stale statement A-074 itself refutes. Every review brief names the register as the authority on what is recorded, so this gap is invisible to exactly the reader it was filed for - reproduced on myself. |
| `R2-F5` | **MEDIUM** | Absence reads as agreement in the effect evaluator: with the call trace unavailable, the bundle records `EVAL_CALL_GRAPH_EXPECTED: PASS` - a positive assertion about an input that was never observed. `checks.ts`'s own comment claiming "every other effect class has an explicit UNRESOLVED counterpart" is false; the call graph has none. |
| `R2-F6` | **INFO** | `SIGNER_CHAIN_UNSTABLE` covers two conditions (head moved / head hashless) and its docstring names one. The record says "the chain moved each time" about a chain that never moved. |

---

## R2-F1 - the E3 repair pinned the signer and left the identical defect in the simulator

**Severity: HIGH.** Confidence: high (mechanically reproduced, with a control).

### The claim under attack

`ts/src/signer/vault.ts:21-42` states the E3 argument and names the defect it repaired:

> **ONE BLOCK, NOT ELEVEN (D-055(c), the E3 repair).** ... **WHAT THE PREVIOUS VERSION DID,
> because it is the defect:** ten `eth_call`s, a `getCode` and a `getBlockNumber`, all at
> "latest", each its own request, with a comment conceding they "could in principle straddle a
> block boundary" and arguing it away on the grounds that a local Anvil has no competing
> producer. Two things were wrong with that. The straddle made `observedAtBlock` a number no
> field was guaranteed to have been read at - and nothing consumed it, so the inconsistency was
> invisible. **And the environment argument is exactly the kind this project has repeatedly paid
> for: it justifies a property from the deployment rather than from the code.**

A-075 (`docs/decisions.md:241`) records the sibling sweep that was supposed to generalise it:

> **THE SIBLING SWEEP (step 2), RECORDED RATHER THAN ASSERTED.** `grep` finds six call sites of
> `readVaultState` ... **all six go through `createChainReader`, so the pin lives in one helper
> and cannot be missed at a call site.**

### What the code does

`ts/src/simulate/index.ts` - the module that produces the anchor which travels into the receipt
and into `evidence.anchor` - reads chain state exactly the way `vault.ts` calls "the defect":

- `index.ts:189` `const anchorBlock = await client.getBlock();` - **unpinned**, `latest`.
- `index.ts:356` `client.getBalance({address})` - **no `blockNumber`**, one request per watched
  address, called twice (pre and post).
- `index.ts:365`, `:381`, `:387` `client.readContract({...})` - **no `blockNumber`** on the
  allowance read and on both DemoPay state reads.

`grep -rn "blockNumber" ts/src/simulate/` returns exactly two hits and neither is a pin:

```
ts/src/simulate/index.ts:73:    blockNumber: bigint;              <- the Anchor type declaration
ts/src/simulate/index.ts:191:        blockNumber: anchorBlock.number,  <- writing the anchor field
```

**There is no `blockNumber` argument on any read in the simulator.** The sibling sweep swept for the function name
`readVaultState`, not for the property "a chain read must be pinned", so it could not see this.

The comments assert the property anyway:

- `index.ts:186-188`: *"The anchor is recorded BEFORE anything mutates, so it names the state the
  verdict is computed against (SS3.2 step 8)."*
- `index.ts:39-42`: *"These are SIMULATED effects at a recorded block ... The recorded anchor is
  what makes that claim auditable rather than rhetorical."*

### Reproduction

`probes/p1-sim-anchor-straddle.ts` (read-only; imports the worktree source, mutates nothing). A
stub `PublicClient` serves two blocks - block 10 has the vault at 5000 wei, block 11 at 999000 wei
- and advances its head **once**, immediately after the anchor `getBlock()` returns.

```
cd <REVIEW-ROOT>/worktrees/w2
node <REVIEW-ROOT>/evidence/r2/probes/p1-sim-anchor-straddle.ts
```

Observed (`probes/p1-output.txt`):

```
--- RPC trace as the simulator issued it ---
  getBlock -> block 10 (LATEST, unpinned)
  *** a block arrives: head 10 -> 11 ***
  evm_snapshot
  getBalance(0x1111) -> served at block 11  <-- NO blockNumber PIN
  getBalance(0x2222) -> served at block 11  <-- NO blockNumber PIN
  eth_sendTransaction (mines a block)
  getBalance(0x1111) -> served at block 11  <-- NO blockNumber PIN
  getBalance(0x2222) -> served at block 11  <-- NO blockNumber PIN
  evm_revert

anchor.blockNumber      = 10
anchor.blockHash        = 0xaaaa...aaaa
vault balance BEFORE    = 999000
vault balance AFTER     = 999000
reported native delta   = 0
tx was actually sent    = true

RESULT: STRADDLE. anchor says block 10; the pre-state it claims to describe was read at block 11.
```

**Control** (`probes/p1-control.ts`, `probes/p1-control-output.txt`) - identical probe with the
head left at 10: `vault balance BEFORE = 5000`, block 10's value, `RESULT: no straddle observed`.
The probe moved something; the only difference is the one interfering block.

### Why this is worse than the signer's version was

1. **The anchor is the artifact.** `observedAtBlock` was "read on every request and never
   consumed" (the E3 finding's own words) - its inconsistency was invisible because nothing used
   it. The *simulation's* anchor is used by everything: `corpus/run.ts:463`,
   `tools/sample-check.ts:280`, `tools/emit-samples.ts:482` pass `simulation.anchor` to the signer
   as `simulationBlockNumber`/`simulationBlockHash`, and `evaluate/index.ts:194-200` writes it
   into the signed evidence bundle as `anchor`. It is the number the receipt commits to.
2. **The E3 check cannot detect it.** `attest.ts:440-445` compares the *anchor* to the signer's
   observed block. Both halves can agree while the effects were measured a block later - the
   anchor is not derived from the reads, so a consistent anchor is not evidence of consistent
   reads. See `R2-F2`.
3. **The straddle also moves the EXECUTION.** `control.snapshot()` (`index.ts:203`) is taken
   *after* the anchor read. A block arriving in that window means the snapshot, the impersonated
   send and the whole simulated execution run on top of a block the anchor does not name. The
   receipt then says "simulated at block N" about an execution that happened on block N+1's state
   - precisely the SS8/D-001 claims boundary the file's own header says the anchor makes
   "auditable rather than rhetorical".
4. **The environment argument is the only thing holding it up**, and `vault.ts` rules it out by
   name. The serialisation queue (`index.ts:160-171`) is per-process and its own docstring
   concedes "Two processes simulating against one node still collide... Run one simulator per
   chain." The straddle needs only one competing block from any source - the owner's
   `setPaused`/rotate transactions the e2e rig itself issues, a relayer, a second process, or any
   chain with a real block cadence.

### What I did NOT establish

I did not produce the straddle against a live Anvil. It needs a block to land inside a window of a
few milliseconds and forcing that reliably needs an interleaving harness I did not build. **The
mechanism is proved at the code level and the consequence is proved by the stub; the field
probability on a quiescent single-process local Anvil is low.** That is exactly the reasoning
`vault.ts` refuses to accept for the signer, which is why I report it at the same severity rather
than discount it.

---

## R2-F2 - `SIGNER_ANCHOR_NOT_OBSERVED` binds two caller-supplied integers, not the simulation

**Severity: MEDIUM.** Confidence: high (read of the code, corroborated by the pipeline call sites).

### The claim under attack

`ts/src/signer/attest.ts:426-431`:

> **THE E3 REPAIR (D-055(c)).** The anchor must be the block the signer read the vault at - not a
> recent one, THE one. **Every value checked below this line came from `state`, and `state` came
> from a single pinned, head-confirmed block; a verdict computed against any other block was
> computed against state the signer never saw**, and saying otherwise is what the receipt would be
> doing.

A-075's residual (c), `docs/decisions.md:241`:

> (c) The anchor now binds to the block the signer read; **nothing binds the EVALUATOR's
> simulation to that block except this refusal**, so a caller whose simulation is one block stale
> is refused and must re-simulate.

### What the code does

`attest.ts:440-445` is the whole check:

```ts
if (
    evaluation.simulationBlockNumber !== state.observedAtBlock ||
    evaluation.simulationBlockHash !== state.observedBlockHash
) {
    findings.push("SIGNER_ANCHOR_NOT_OBSERVED");
}
```

`evaluation.simulationBlockNumber` and `evaluation.simulationBlockHash` are two RPC parameters
(`protocol.ts:752-755`), *asserted by the caller*. Nothing in the signer derives them from, or ties
them to, the simulation. The signer performs no simulation, receives no simulation, and cannot
recompute one - it receives `evidenceCanonical` as an opaque string.

The property the check establishes is: *the two integers the caller put in the `evaluation` object
equal the block the signer read.* It is **not**: *the effects the verdict rests on were measured at
the block the signer read.* The second is what both quoted passages say. The refusal does not
"bind the evaluator's simulation"; it binds a caller-chosen label.

The D-010 verifier closes one half (`verifier/verify.py:1659-1660` requires `evidence.anchor` to
equal the receipt's `simulationBlockNumber`/`simulationBlockHash`), so the *bundle* cannot disagree
with the *receipt*. But both are written by the same caller, so agreeing costs the caller nothing;
and the verifier is a post-hoc offline artifact while the vault executes on the receipt alone.

### Reproduction

A read of the code plus the pipeline's own call sites:

```
cd <REVIEW-ROOT>/worktrees/w2
grep -n "simulationBlockNumber" ts/src/signer/attest.ts ts/src/signer/protocol.ts
grep -n "simulateAction\|readVaultState\|evaluate(\|evaluateAndSign" ts/src/corpus/run.ts ts/src/tools/*.ts
```

Observed - all three production call sites have the same shape, and it is a **two-block composite**:

```
tools/sample-check.ts:188  readVaultState(...)                     <- block A (pinned, E3-repaired)
tools/sample-check.ts:225  simulateAction(...)                     <- block B (unpinned, see R2-F1)
tools/sample-check.ts:242  evaluate({vaultState, simulation, ...}) <- mixes A and B
tools/sample-check.ts:271  evaluateAndSign(...)                    <- signer reads C, requires B == C
```

`corpus/run.ts:415/431/440/454` and `tools/emit-samples.ts:422/439/447/473` are identical.
**Nothing anywhere requires A == B.** The bundle's `targetCodeIdentity.observedOnChain`
(`evaluate/index.ts:183`) is block A's value, printed inside a bundle whose `anchor` field
(`:194-200`) names block B. The E3 check pins only the B==C edge.

The verdict itself is largely protected, because the signer independently re-checks every
vault-state fact at block C - that is what the isolated signer is for, and it works. **What is not
protected, and what the anchor is actually about, is the simulated effects.** No component
re-establishes those at block C, and per `R2-F1` the anchor does not even establish them at block B.

### Honest scoping

- This is **not** `E4` re-reported. `E4` names `normalizedAction` and `expectedEffects` as the
  bundle fields checked by neither the signer nor the verifier; `anchor` *is* checked by the
  verifier. The finding here is that the check is between two caller-written fields.
- It is **not** the accepted D-014 boundary ("this signer prevents a MIS-BOUND receipt ... it does
  not prevent a WRONG VERDICT", `attest.ts:41-42`). That boundary is honest and I do not dispute
  it. What I dispute is that `attest.ts:426-431` and A-075 residual (c) describe the check as
  establishing something on the *other* side of that boundary.
- The defect is therefore primarily a **claim** defect, which is why it is MEDIUM rather than
  HIGH: the mechanism is the declared architecture, and what is wrong is that two places state the
  mechanism achieves more than it does - including the residual list whose entire purpose is to
  say what a repair did *not* reach.

---

## R2-F3 - D-09(c)'s third route: the vault's immutable cap is not in the intersected ceiling

**Severity: LOW.** Confidence: high (reproduced, ALLOW verdict, 500x overstatement).

### The claim under attack

`ts/test/evaluate.checks.test.ts:510-536`, the A-076 regression added this week:

> **THE ARGUMENT: `expectedEffects.maxNativeValueWei` is what the bundle CLAIMS was authorised,
> and SS5.2 says "mandate and policy constraints are intersected" - so it must be the LOWER of the
> two ceilings** ... **THE CONSEQUENCE IS A FALSE STATEMENT IN THE PRODUCT, not a cosmetic one.
> Under the inversion a bundle whose policy caps spending at 2e15 would attest that 1e18 was
> authorised - five hundred times the real limit.**

Register SS13.4 records `D-09` as **FIXED (A-076)** - "(c)'s intersected-ceiling regression added;
the min->max mutation survived pre-test and is killed post-test".

### What the code does

`ts/src/evaluate/index.ts:136`:

```ts
maxNativeValueWei: minOf(mandate.maxNativeValueWei, policy.maxNativeValueWei).toString(),
```

Two ceilings. `ts/src/evaluate/checks.ts:302-305`, in the same repository, states the rule with
three:

> `--- SS5.7: native-value ceiling, intersected (SS5.2) ---`
> "Mandate and policy constraints are intersected" - **the binding limit is the lower of the two,
> plus the vault's own immutable cap, and the action must satisfy all three.**

and enforces all three (`EVAL_VALUE_WITHIN_MANDATE`, `EVAL_VALUE_WITHIN_POLICY`,
`EVAL_VALUE_WITHIN_VAULT_CAP`, `checks.ts:306-320`). The signer re-checks all three
(`attest.ts:481`, `:505`, `:520`). Only the *bundle* records two.

The A-076 test asserts both directions of min(mandate, policy) and a tie. It never varies the vault
cap, so the third constraint is outside the property it pins.

### Reproduction

`probes/p2b-ceiling-allow.ts` (read-only, in-process, no mutation):

```
cd <REVIEW-ROOT>/evidence/r2/probes
node p2b-ceiling-allow.ts
```

Mandate `1e18`, policy `1e18`, **vault immutable cap `2e15`**, action value `1e15` (under the cap,
so every check passes):

```
mandate.maxNativeValueWei        = 1000000000000000000
policy.maxNativeValueWei         = 1000000000000000000
vaultState.maxNativeValueWei     = 2000000000000000   <-- the binding limit

bundle expectedEffects.maxNativeValueWei = 1000000000000000000
ratio bundle-claim : real limit          = 500x

EVAL_VALUE_WITHIN_VAULT_CAP      = PASS -
verdict                          = ALLOW

RESULT: the bundle attests a ceiling ABOVE the one that can ever execute.
```

`probes/p2-ceiling-third-route.ts` is the same construction with the value *above* the cap: the
verdict becomes `BLOCK` on `EVAL_VALUE_WITHIN_VAULT_CAP` while `expectedEffects` still attests
`1e18`.

### Why this is a finding and not a re-report

- The **outcome is the one A-076's own docstring gives as the reason (c) had to be fixed**: a
  bundle attesting `1e18` when the real limit is `2e15`, the same 500x ratio, on an **ALLOW**.
- The repair closed the route the finding *demonstrated* (invert `minOf`) and not the property it
  *argued*. This is the failure mode `docs/repair-protocol.md` and the E3 write-up both name.
- Nothing in `docs/` mentions the vault cap in this context: `grep -rn "immutable cap" docs/*.md`
  returns **no matches**.
- A defensible counter-reading exists and I state it rather than hide it: SS5.2's published words
  are "mandate **and policy** constraints are intersected", so the field is literally
  spec-conformant, and the vault cap is a hard backstop rather than an authorisation. That is why
  this is **LOW**. Whether the field should carry the binding limit or keep the SS5.2 reading is a
  product question and not an agent's to settle.

---

## R2-F4 - A-074's residual files the `description` gap as "recorded in the register"; the register has no such entry

**Severity: MEDIUM.** Confidence: high (reproduced on myself - I wrote this up as a fresh finding
before checking `decisions.md`).

### The claim under attack

`docs/decisions.md:239`, A-074's residual (c) - A-074 is explicitly on my assigned surface:

> (c) `evidence.decodedSelectorAndParameters.description` - the human-readable line SS7.5's Gate 8
> will be graded on - is still compared to nothing; round six's `L3-04` showed it can state the
> opposite of the parameters beside it. **Recorded in the register, not fixed here.**

### What is actually in the register

```
cd <REVIEW-ROOT>/worktrees/w2
grep -n "description" docs/v1-1-register.md
#   46: "grouped under seven headings, each with a description"   <- unrelated
#  258: "no description required, despite the output line ..."    <- unrelated
grep -rn "L3-04" docs/
#   docs/decisions.md:239   <- the A-074 entry itself, and nowhere else
grep -n "decodedSelectorAndParameters" docs/v1-1-register.md
#  865: one bullet, quoted below
```

**There is no register entry for the `description` gap.** The residual points at a record that
does not exist.

The single register bullet that names the field is register SS14 line 865, and it is a live false
statement:

> - **`decodedSelectorAndParameters` is still compared to nothing** (A-070). The SS5.6 projections
>   now run on both paths and fail on absence, but the field D-014's justification actually rests
>   on **is checked by neither the signer nor the verifier.** This is the larger finding, it sits
>   inside the SIGNED Gate S1 pack, and it is not an agent's to close.

Both halves are wrong at this commit:

- *"checked by ... [not] the signer"* - the signer has checked it since D-014.
  `attest.ts:729-763` compares `selector`, `schema` and every field of `parameters` against its
  own `decodeBySelector` result. This half was false when the bullet was written.
- *"checked by ... [not] the verifier"* - **A-074, recorded two entries later in the same day's
  log, built exactly that comparison** (`_evidence_describes_the_bundle`). This half became false
  the same day and the bullet was not updated.

A-075 corrected SS13.4's status column two entries after that, as a named pre-review prerequisite,
"because every review brief names this table as the authority on what is already recorded". **SS14
is the register's other status surface and it was not swept in that pass.**

### Why this is a finding and not pedantry

The consequence is mechanical and I demonstrated it on myself. Rule 5 of the common brief tells
every reviewer that `docs/v1-1-register.md` SS13.4 and `docs/gate-s2-evidence.md` SS11.0 are the
list of what is already recorded. A reviewer who checks those two authorities for the
`description` gap finds **nothing**, and correctly concludes it is unreported. **I wrote it up as
a fresh finding and only demoted it after reading a 5,000-word `decisions.md` entry that no rule
directs a reviewer to search.** A residual that files itself as recorded, in a document reviewers
are not pointed at, is functionally an unrecorded residual with a claim of recording attached -
which is the shape `docs/repair-protocol.md` step 6 exists to prevent.

It also inverts the direction A-075 says matters: a stale `open` "invites a re-report", and a
stale "recorded" invites the opposite - a reviewer who *does* find the `decisions.md` line will
trust it and stop looking, exactly as I nearly did.

### The underlying gap, stated once so it is not lost

For completeness, since the item itself is genuinely recorded *somewhere*: `evaluate/index.ts:117`
emits `description: describeCall(decode.decoded)` inside `decodedSelectorAndParameters`;
`grep -n "description" ts/src/signer/attest.ts` returns **no matches**; and
`ts/src/decode/index.ts:245-251` says the field "Exists for ... the SS7.5 five-minute comprehension
gate, where a reviewer has to see what the agent actually proposed without reading hex." The set
of fields the signer attests and the set a human at the ratified gate reads are disjoint. **That
part is A-074(c) and is not my finding.** My finding is that the register does not carry it.

---

## R2-F5 - absence reads as agreement: `EVAL_CALL_GRAPH_EXPECTED` PASSes on a trace that was never obtained

**Severity: MEDIUM.** Confidence: high (reproduced).

### The claim under attack

`ts/src/simulate/index.ts:266-270`, on the trace-fetch failure path:

> SS3.3(8): a missing trace is missing evidence, and **missing evidence must reach the evaluator
> rather than be inferred as "no internal calls".**

and `ts/src/evaluate/checks.ts:480-484`, the repair that added `EVAL_ALLOWANCE_EFFECT_UNOBSERVED`:

> An approve action whose allowance effect was never observed must NOT reach ALLOW on silence.
> **Every other effect class has an explicit UNRESOLVED counterpart** (`EVAL_NATIVE_DELTA_UNOBSERVED`,
> `EVAL_ENTITLEMENT_UNOBSERVED`); this one had none, so a missing measurement simply emitted no
> check at all - SS3.3(8) says missing state never produces an automatic allow, and an absent check
> is exactly missing state.

### What the code does

`simulate/index.ts:252-273` sets `subcalls = []` and pushes `SIM_CALL_TRACE_UNAVAILABLE` when the
trace cannot be fetched. One layer up, `checks.ts:411-417`:

```ts
results.push(
    require_(
        simulation.internalCalls.length === 0,
        "EVAL_CALL_GRAPH_EXPECTED",
        `${simulation.internalCalls.length} unexpected internal call(s)`,
    ),
);
```

`require_` is `condition ? pass(code) : violation(code, detail)`. **There is no third arm.** An
empty `internalCalls` that means "nothing was observed" and an empty one that means "an observed
trace had no subcalls" produce the identical `PASS`. The inference `simulate/index.ts` says must
not be made is made here.

And the quoted comment is **false**: `EVAL_CALL_GRAPH_EXPECTED` has **no** `*_UNOBSERVED`
counterpart. `grep -n "UNOBSERVED" ts/src/evaluate/checks.ts` returns three -
`EVAL_ALLOWANCE_EFFECT_UNOBSERVED`, `EVAL_NATIVE_DELTA_UNOBSERVED`, `EVAL_ENTITLEMENT_UNOBSERVED`
- and no call-graph member. The repair generalised from the allowance to nothing.

### Reproduction

`probes/p3-callgraph-absence.ts` (read-only, in-process). The simulation is the degraded shape the
real pipeline produces on a trace failure:

```
cd <REVIEW-ROOT>/evidence/r2/probes
node p3-callgraph-absence.ts
```

```
simulation.callTrace            = null   (debug_traceTransaction failed)
simulation.internalCalls        = []     (nothing was observed, not 'nothing happened')
simulation.unresolvedChecks     = [SIM_CALL_TRACE_UNAVAILABLE]

EVAL_CALL_GRAPH_EXPECTED        = PASS ""
EVAL_SIM_CALL_TRACE_UNAVAILABLE = UNRESOLVED
verdict                         = REVIEW

bundle policyChecks row: {"code":"EVAL_CALL_GRAPH_EXPECTED","detail":"","outcome":"PASS"}
bundle unresolvedChecks: ["EVAL_SIM_CALL_TRACE_UNAVAILABLE"]

RESULT: the bundle records PASS for a check whose input was never observed.
```

### The bound, stated plainly

**The verdict is protected.** `SIM_CALL_TRACE_UNAVAILABLE` maps to
`EVAL_SIM_CALL_TRACE_UNAVAILABLE` (`checks.ts:150-153`), which is UNRESOLVED, so `verdictOf` can
only return REVIEW or BLOCK. There is no route from this to an ALLOW through the pipeline, and I
looked for one: every branch in `simulate/index.ts` that leaves `subcalls` empty without an
observed trace also pushes the unresolved code (`:254`, `:266-270`, `:271-273`). **I am not
claiming an authorization bypass.**

What is defective is the **record**, and the record is the product. `evaluate/index.ts:24-28`
states the purpose of emitting passes at all:

> a record listing only failures cannot distinguish a check that passed from one that never ran.
> That distinction is the whole subject of SS7.3's ablation.

The bundle here does exactly what that sentence says the field exists to prevent. It is worse than
the "emits nothing" case the common brief names, because it emits a positive PASS. And this is the
one check the register already records as least-evidenced (SS14: "`EVAL_CALL_GRAPH_EXPECTED` is
asserted by no CORPUS fixture and no SAMPLE ... the gate remains blind to it at every profile") -
so the check with the least external evidence is also the one that can affirmatively claim to have
passed on none.

**MEDIUM** rather than LOW because two things are wrong at once: a reproducible
absence-as-agreement in the signed evidence bundle, and a comment asserting the general property
("every other effect class has an explicit UNRESOLVED counterpart") that is false about the very
class it omits. A downgrade to LOW on the bounded-consequence argument would be defensible with
recorded reasoning; I am not making it for the adjudicator.

---

## R2-F6 - `SIGNER_CHAIN_UNSTABLE` covers two conditions and its record names one

**Severity: INFO.** Confidence: high.

`ts/src/signer/vault.ts:157-236`. The retry loop **terminates**: `for (let attempt = 0; attempt <
SNAPSHOT_ATTEMPTS; attempt += 1)` with `SNAPSHOT_ATTEMPTS = 5`, two `continue` paths, then an
unconditional `throw new ChainUnstableError(SNAPSHOT_ATTEMPTS)`. There is no unbounded path - I
probed for one and found none (see `NULL-RESULTS.md`).

Two different conditions consume the same budget and produce the same code:

- `vault.ts:163-167` - `head.hash === null` (a pending block): `continue`, **no reads issued**.
- `vault.ts:206-213` - the head moved, or a same-height reorg: `continue`, reads discarded.

`protocol.ts:100-113` documents `SIGNER_CHAIN_UNSTABLE` as exactly one of them:

> The chain would not hold still long enough for the signer to observe one block. ... "the vault
> was read repeatedly and the chain moved each time" ... **filing the second as the first would put
> a claim in the refusal record that the evidence does not support.**

A node returning a hashless head five times running never moved and was never read. The signed
D-012 refusal record then commits a reason code whose published meaning is "the chain moved each
time" about a chain that did not move - the same substitution that docstring exists to forbid, one
level in. There is also no backoff between attempts; that is a throughput note, not a defect.

**INFO, not higher**, because both conditions correctly refuse everything (FATAL) and no verdict
changes. It is a record-fidelity defect in a code whose whole justification is record fidelity.
