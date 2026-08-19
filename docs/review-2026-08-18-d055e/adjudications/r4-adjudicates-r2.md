# ADJUDICATION — R4 adjudicates REVIEWER 2

**Adjudicator:** R4 (the free lens). I did not author any of R2's findings and I did not author
the code they are against.
**Commit adjudicated:** `7e0ab7f1057de278c09cc803ab4ca266f53399e1`
**Worktree used:** `<REVIEW-ROOT>/worktrees/w4`
**Method:** every claim assumed WRONG until I made its failure happen myself. I did not run any
probe from `evidence/r2/probes/`; where I needed a probe I wrote my own
(`adjudication/probes-r4/`). Baseline for the worktree was taken before this session and
re-verified after: `git diff HEAD --stat -- .` shows only the two provisioned submodule symlink
entries, and a full `cmp` against a pristine pre-review copy reports **364 files, 0 differ**.
**Nothing was repaired. Nothing in the live repository was touched.**

| id | R2 severity | my verdict | my severity |
|---|---|---|---|
| `R2-F1` | HIGH | **CONFIRMED** (mechanism) — its load-bearing severity argument **REFUTED** | **LOW** |
| `R2-F2` | MEDIUM | **REFUTED** | — |
| `R2-F3` | LOW | **CONFIRMED** | **LOW** |
| `R2-F4` | MEDIUM | **CONFIRMED** | **MEDIUM** |
| `R2-F5` | MEDIUM | **CONFIRMED** | **MEDIUM** |
| `R2-F6` | INFO | **CONFIRMED** | **INFO** |

---

## R2-F1 — the simulator's unpinned reads — **CONFIRMED, severity HIGH → LOW**

### The claim

The E3 repair pinned `readVaultState` and left the identical unpinned-read defect in
`ts/src/simulate/index.ts`: the anchor comes from an unpinned `getBlock()` and the pre-state,
execution and post-state can all be at a different block, so the receipt names a block the
effects were not measured at. R2 rates this HIGH on four supporting arguments, of which **#2 —
"the E3 check cannot detect it" — is the one that carries the severity.**

### What I did

**Step 1 — verify the code claim.** Read `ts/src/simulate/index.ts` directly.

```
sed -n '186,210p' ts/src/simulate/index.ts     # anchor = await client.getBlock()  (no args)
sed -n '349,400p' ts/src/simulate/index.ts     # readState: getBalance / readContract, no pin
grep -rn "blockNumber" ts/src/simulate/
#   ts/src/simulate/index.ts:73:    blockNumber: bigint;             <- type declaration
#   ts/src/simulate/index.ts:191:        blockNumber: anchorBlock.number,  <- writing the field
```

**R2's code reading is exactly right.** There is no `blockNumber` argument on any read in the
simulator, the anchor is taken from an unpinned `getBlock()`, and `control.snapshot()` is taken
*after* it. There is no head-confirmation loop of the kind `vault.ts:203-213` has.

**Step 2 — reproduce the straddle myself.** I wrote my own probe,
`adjudication/probes-r4/a1-straddle-then-signer.ts`. It imports the **real** `simulateAction`
from w4 and drives it with a stub client whose head advances from 10 to 11 immediately after the
anchor `getBlock()` returns. The vault's balance differs by block (5000 at block 10, 999000 at
block 11) so a read served at the wrong block is visible.

```
cd <REVIEW-ROOT>/worktrees/w4
node <REVIEW-ROOT>/adjudication/probes-r4/a1-straddle-then-signer.ts
```

```
  getBlock() -> block 10  (LATEST, unpinned)
  *** an external block arrives: head 10 -> 11 ***
  evm_snapshot at head 11
  getBalance(0x1111) served at block 11   <-- NO blockNumber pin
  ...
  anchor.blockNumber          = 10
  vault balance BEFORE        = 999000   (block 10 value is 5000)
  STRADDLE PRESENT            = true
```

**The straddle is real and I reproduced it independently.**

**Step 3 — the question R2 did not ask: what happens next?** The receipt is not issued by the
simulator. The pipeline continues into the signer, and the signer runs the E3 check
(`attest.ts:440-445`) against its own head-confirmed pinned read.

```
  evaluation.simulationBlockNumber = 10
  state.observedAtBlock            = 11
  findings                         = ["SIGNER_ANCHOR_NOT_OBSERVED"]

RESULT: the straddled simulation is REFUSED by the signer. No receipt is issued.
```

### Why this is not an accident of my stub — the general argument

Let `A` = the block the evaluator's `readVaultState` pinned, `B` = the anchor, `E` = the block the
simulator's unpinned reads were actually served at, `C` = the block the signer pinned.

- `B ≤ E` — the anchor `getBlock()` precedes every read in `runSimulation`.
- `E ≤ C` — the signer runs strictly after `simulateAction` returns, and `evm_revert` restores the
  head to the snapshot point, so the signer's head-confirmed read is at or after `E`.
- E3 requires `B == C`.

`B ≤ E ≤ C` and `B == C` force `B == E == C`. **A straddle cannot coexist with a passing E3
check.** The protection is not that the anchor is derived from the reads — R2 is right that it is
not — it is that the signer's later equality check squeezes the interval shut.

### Could the signer read a different, lagging node?

This is the one configuration in which R2 would be right, so I checked it rather than assumed it.

```
grep -n "SENTINEL_RPC_URL" ts/src/tools/sample-check.ts ts/src/corpus/run.ts ts/src/tools/emit-samples.ts
#   sample-check.ts:166   SENTINEL_RPC_URL: rpcUrl,
#   corpus/run.ts:231     SENTINEL_RPC_URL: rpcUrl,
#   (emit-samples likewise)
```

**All three shipped pipelines hand the signer process the same `rpcUrl` the simulator uses.** A
divergent-head configuration is constructible only by pointing `SENTINEL_RPC_URL` at a second
node, which exists nowhere in this repository, and `SIGNER_SIMULATION_BLOCK_MISMATCH`
(`attest.ts:421-424`) independently re-checks the anchor's hash against that node.

### Verdict: CONFIRMED

The mechanism R2 describes is real, is in the code, and I reproduced it. R2 did not overstate what
it observed.

**But its argument #2 is REFUTED**: *"The E3 check cannot detect it — both halves can agree while
the effects were measured a block later"* is false for every configuration in this repository, and
the residual R2 quotes as evidence of an overclaim (A-075(c)) in fact describes precisely the
behaviour I observed: *"a caller whose simulation is one block stale is refused and must
re-simulate."* Argument #3 (the straddle also moves the execution) is true but lands in the same
refusal. Argument #1 (the anchor is consumed, unlike `observedAtBlock`) is true and is the reason
this is not INFO.

### Severity: LOW (lowered from HIGH)

The crux the coordinator asked me to decide: **the unpinned read is a real defect in the module,
and it is immaterial to what any receipt claims.** Not because the simulation snapshots and
reverts — the snapshot protects the *node*, not the *labelling* — but because a straddle makes the
anchor stale relative to the signer's head, and the E3 equality then refuses to sign. The
inconsistency is converted into a refusal, which is the correct outcome.

What remains, and why it is not INFO:

1. **Three comments claim a property the module does not locally establish.**
   `index.ts:186-188` — *"the anchor … names the state the verdict is computed against"* — is true
   of the shipped system but is not made true by anything in that file. The property is emergent
   from call ordering plus an equality check in a different component, and **neither file records
   that dependency.** Relax E3 to a recency window and the claim silently becomes false.
2. **A-075's sibling sweep genuinely missed a real unpinned-read site.** It swept for the symbol
   `readVaultState`, not for the property "a chain read must be pinned". That is the
   generalise-the-demonstration pattern, correctly identified by R2, even though the consequence
   here is contained.

A defensible case for MEDIUM exists on the strength of point 1 — an undocumented cross-component
dependency is fragile. I did not take it, because severity should track what the artifact
currently claims falsely, and no receipt at `7e0ab7f` can claim falsely by this route.

---

## R2-F2 — `SIGNER_ANCHOR_NOT_OBSERVED` "binds a label, not a simulation" — **REFUTED**

### The claim

The check compares two caller-supplied integers to the signer's head, therefore it binds a
caller-chosen label; and **two places describe it as binding the evaluator's simulation** —
`attest.ts:426-431` and A-075's residual (c). R2 scopes the finding explicitly as a *claim*
defect, which is what makes it MEDIUM rather than INFO.

### What I did

The mechanical half is not in dispute and I confirmed it: `simulationBlockNumber` and
`simulationBlockHash` are RPC parameters parsed in `protocol.ts:752-755`, the signer performs no
simulation, and `attest.ts:440-445` compares them to `state.observedAtBlock` /
`state.observedBlockHash`. All true.

The finding therefore stands or falls on whether the two cited passages overstate. I read both in
full rather than from R2's excerpt.

**A-075 residual (c), exact text from `docs/decisions.md`:**

> (c) The anchor now binds to the block the signer read; **nothing binds the EVALUATOR's
> simulation to that block except this refusal**, so a caller whose simulation is one block stale
> is refused and must re-simulate. That is the intended behaviour and it is a REAL behaviour
> change, stated here rather than left to be discovered.

This does not describe the check as binding the evaluator's simulation. **It explicitly disclaims
exactly that**, names the refusal as the sole mechanism, and states the resulting behaviour — which
is the behaviour my F1 probe produced. This is the disclosure R2 says is missing.

**`attest.ts:426-431`:**

> The anchor must be the block the signer read the vault at — not a recent one, THE one. Every
> value checked below this line came from `state`, and `state` came from a single pinned,
> head-confirmed block; a verdict computed against any other block was computed against state the
> signer never saw.

Every sentence here is about the **signer's own vault state**. "Every value checked below this
line came from `state`" is true. Nothing in it asserts that the simulated effects were measured at
that block.

And 400 lines earlier, `attest.ts:32-42` states the boundary in the strongest available terms:

> It never decodes calldata parameters, **never simulates, never inspects effects** … *This signer
> prevents a MIS-BOUND receipt from being signed. It does not prevent a WRONG VERDICT from being
> signed.*

### Verdict: REFUTED

The mechanism R2 describes is accurate, but the finding is that two documents overstate it, and
neither does. One of the two is the project's own residual list saying precisely what R2 says it
fails to say. A finding whose entire substance is "these passages claim more than the code does"
is refuted when the passages are read in full.

### Residual worth carrying forward — not R2-F2, and not a finding of mine

R2 makes a separate observation inside this section that is factually correct and is **not** the
claim I refuted: the pipeline is a two-block composite. `vaultState` is read at block `A`
(`sample-check.ts:188`) and the anchor is taken at block `B` (`:225`); nothing requires `A == B`,
so `targetCodeIdentity.observedOnChain` in the bundle can come from an older block than the
bundle's own `anchor`. The verdict is protected — the signer independently re-reads every vault
fact at `C` — and I found no route to a wrong receipt. **I record it so it is not lost, and I am
not adjudicating it as a finding, because R2 did not file it as one.**

---

## R2-F3 — the vault's immutable cap is absent from `expectedEffects` — **CONFIRMED, LOW**

### What I did

I did not need a probe, and a static proof is stronger than one. `ts/src/evaluate/index.ts:136`:

```ts
maxNativeValueWei: minOf(mandate.maxNativeValueWei, policy.maxNativeValueWei).toString(),
```

The expression takes **two** arguments and `vaultState` is not among them, so the field
**provably cannot** reflect the vault cap for any input whatsoever — a stronger result than any
single reproduction. With mandate = policy = 1e18 and a vault cap of 2e15, the field is 1e18 and
every check passes for an action of 1e15, so the verdict is ALLOW. R2's 500× figure is arithmetic
on that expression and is correct.

`ts/src/evaluate/checks.ts:302-305` does state the rule with three constraints —
*"the binding limit is the lower of the two, plus the vault's own immutable cap, and the action
must satisfy all three"* — and `checks.ts:306-320` enforces all three.

### Verdict: CONFIRMED — with two corrections to R2's framing

1. **A mitigation R2 does not mention.** The bundle is not silent about the vault cap. `EVAL_VALUE_WITHIN_VAULT_CAP`
   is emitted as a check and `evaluate/index.ts:127-131` writes every check into `policyChecks`
   with its outcome, so the bundle records that the vault cap was checked and passed. What it
   omits is the cap's **value**, not the fact of the constraint.
2. **The "D-09(c) third route" framing overreaches.** D-09(c) was about inverting the §5.2
   intersection of mandate and policy. The vault cap sits outside §5.2's stated intersection —
   §5.2's published words are "mandate **and policy** constraints are intersected" — so this is a
   *different* question about what the field should mean, not the same argument left ungeneralised.
   R2 states this counter-reading itself, honestly, which is why it filed LOW.

### Severity: LOW (agreeing with R2)

The field is spec-conformant on the published reading and is documented as *"What the mandate
authorised"*. The defect is that a reader can take it for the ceiling that can execute, and the
engine's own comment invites that reading by calling all three "the binding limit". Whether the
field should carry the binding limit is a product question and not an agent's to settle — R2 says
so and is right. INFO would also be defensible; I kept LOW because the comment and the field
genuinely disagree.

---

## R2-F4 — A-074's residual files a gap as "recorded in the register"; it is not — **CONFIRMED, MEDIUM**

### What I did

Independently reproduced every leg.

```
cd <REVIEW-ROOT>/worktrees/w4
grep -n "decodedSelectorAndParameters" docs/v1-1-register.md   # -> line 865 ONLY
grep -n "description" docs/v1-1-register.md                    # -> 46, 258, both unrelated
grep -rn "L3-04" docs/                                         # -> docs/decisions.md:239 only
```

A-074's residual (c) at `docs/decisions.md:239` reads, verbatim:

> (c) `evidence.decodedSelectorAndParameters.description` … is still compared to nothing; round
> six's `L3-04` showed it can state the opposite of the parameters beside it. **Recorded in the
> register, not fixed here.**

**There is no register entry for it.** Confirmed.

### The second leg — the one register bullet that names the field is now false in both halves

Register line 865: *"the field D-014's justification actually rests on **is checked by neither the
signer nor the verifier**."* I tested both halves against the tree:

- **Signer:** `ts/src/signer/attest.ts:630-650` — `checkEvidenceDecoding` reads
  `.decodedSelectorAndParameters` (`:638`) and compares it against its own `decodeBySelector`
  result (`:645`), invoked from `attest.ts:370`. **The signer checks it.**
- **Verifier:** `grep -c decodedSelectorAndParameters verifier/verify.py` returns **2** (it
  returned 0 when A-074 was written, which A-074 gives as its own reason for existing).
  `_evidence_describes_the_bundle` is defined at `verify.py:1434` and called from `:911` and
  `:1629`. **The verifier checks it.**

Both halves false. R2's reading is correct.

### Verdict: CONFIRMED

### Severity: MEDIUM (agreeing with R2)

The consequence is mechanical and R2 demonstrated it on itself, which I find persuasive rather
than rhetorical: COMMON-BRIEF rule 5 names `v1-1-register.md` §13.4 and `gate-s2-evidence.md`
§11.0 as the authorities on what is already recorded. A reviewer checking those for the
`description` gap finds nothing, and a reviewer who instead finds the `decisions.md` line will
trust "Recorded in the register" and stop looking. A-075 corrected §13.4's status column two
entries later, as a named pre-review prerequisite; **§14 was not swept in that pass**, and §14 is
where the stale bullet lives.

Not High: the underlying `description` gap is genuinely recorded *somewhere* (A-074(c) itself),
nothing about the product's behaviour is misstated to a user, and no signed pack carries it. Not
Low: a residual list exists precisely to say what a repair did not reach, this one files itself as
recorded when it is not, and the register — which the exit-criterion packet already lists as a
prerequisite that is NOT MET — carries a live false statement about the same field.

**This finding and my own R4-F1/R4-F4 are the same defect in three different tables.** I note the
convergence for the coordinator: three independent surfaces, all hand-maintained status prose,
all stale, none derived.

---

## R2-F5 — `EVAL_CALL_GRAPH_EXPECTED` passes on a trace that was never obtained — **CONFIRMED, MEDIUM**

### What I did

Traced the path in source rather than re-running R2's probe.

- `ts/src/simulate/index.ts:252-273` — on a trace-fetch failure, `subcalls` stays `[]` and
  `SIM_CALL_TRACE_UNAVAILABLE` is pushed. The `txHash === null` branch (`:271-273`) does the same.
  The comment at `:266-270` states the rule: *"a missing trace is missing evidence, and missing
  evidence must reach the evaluator rather than be inferred as 'no internal calls'."*
- `ts/src/evaluate/checks.ts:411-417` — the check is
  `require_(simulation.internalCalls.length === 0, "EVAL_CALL_GRAPH_EXPECTED", …)`.
  `require_` is `condition ? pass : violation`. **There is no third arm.** An unobserved trace and
  an observed-empty trace both yield `PASS`.
- `grep -n "UNOBSERVED" ts/src/evaluate/checks.ts` → `EVAL_ALLOWANCE_EFFECT_UNOBSERVED`,
  `EVAL_ENTITLEMENT_UNOBSERVED`, `EVAL_NATIVE_DELTA_UNOBSERVED`. **No call-graph member.**
- `evaluate/index.ts:127-131` writes every check into the bundle's `policyChecks`, so the `PASS`
  reaches the signed evidence bundle.

The inference `simulate/index.ts` says must not be made is made one layer up. **Confirmed.**

### The mitigation, which R2 states honestly and which I verified

`checks.ts:150-153` maps `SIM_CALL_TRACE_UNAVAILABLE` → `EVAL_SIM_CALL_TRACE_UNAVAILABLE`, and
`verdictOf` (`checks.ts:513-519`) returns `BLOCK` on any VIOLATION and `REVIEW`/`BLOCK` on any
UNRESOLVED, reaching `ALLOW` only when nothing is unresolved. Every branch that leaves `subcalls`
empty without an observed trace also pushes the unresolved code. **There is no route from this to
an ALLOW, and R2 does not claim one.**

### One correction to R2's second ground

R2 calls the comment at `checks.ts:481-482` — *"Every other effect class has an explicit UNRESOLVED
counterpart"* — false. That depends on whether the call graph is an "effect class". The three
quantities `readState` measures pre/post are native balance, allowance and entitlement, and each
does have an UNOBSERVED counterpart; the call graph comes from the trace, not from `readState`.
**On the narrow reading the comment is true, and R2's second ground is UNPROVEN.** I record this
rather than let it ride, because the finding does not need it.

### Verdict: CONFIRMED — on ground (a) alone

### Severity: MEDIUM (agreeing with R2, on the narrowed basis)

The verdict is protected, so this is not an authorization defect. But the signed evidence bundle
contains a positive `PASS` for a check whose input was never observed, and `evaluate/index.ts:24-28`
states the reason passes are emitted at all: *"a record listing only failures cannot distinguish a
check that passed from one that never ran."* The bundle does exactly what that sentence exists to
prevent. COMMON-BRIEF names "absence reads as agreement" as a defect class and calls a check that
emits nothing worse than no check; this one emits a positive assertion, which is worse again. It
is also, per register §14, the check with the least external evidence — asserted by no corpus
fixture and no sample.

LOW would be defensible purely on bounded consequence. I am not taking it: the artifact is signed,
the misstatement is affirmative rather than silent, and it is read by the D-010 verifier.

---

## R2-F6 — `SIGNER_CHAIN_UNSTABLE` covers two conditions, its record names one — **CONFIRMED, INFO**

### What I did

Read `ts/src/signer/vault.ts:157-236` and `ts/src/signer/protocol.ts:100-113`.

Two distinct `continue` paths consume the same `SNAPSHOT_ATTEMPTS = 5` budget and terminate in the
same unconditional `throw new ChainUnstableError(SNAPSHOT_ATTEMPTS)`:

- `vault.ts:163-167` — `head.hash === null`, a pending block. **`continue` before any read is
  issued.**
- `vault.ts:206-213` — the confirm read shows the head moved or a same-height reorg. Reads issued
  and discarded.

`protocol.ts:100-113` glosses the code as *"the vault was read repeatedly and the chain moved each
time"*, and the same docstring warns that filing one fact as another *"would put a claim in the
refusal record that the evidence does not support. That substitution is the honesty defect this
project exists to study."* On the pending-block path no read is issued and the chain need not have
moved, so the gloss does not describe it.

I also independently checked R2's claim that the loop terminates: the `for` is bounded by
`SNAPSHOT_ATTEMPTS`, both `continue`s are inside it, and the `throw` is unconditional after it.
**No unbounded path.** R2 reported the same and was right to check.

### Verdict: CONFIRMED

### Severity: INFO (agreeing with R2)

The docstring's *primary* definition — *"The chain would not hold still long enough for the signer
to observe one block"* — covers the pending-block case accurately; only the contrastive gloss is
narrower than the code. No behaviour is wrong, no artifact is misstated, and the refusal is
correct in both cases. LOW would be defensible given the docstring names the exact hazard it then
commits, but the imprecision is confined to one clause of one comment.

---

## Adjudicator's notes

**On R2's quality.** Five of six findings survive independent reproduction, and R2's own scoping
was consistently honest: it stated the bound on F5 ("I am not claiming an authorization bypass"),
gave the counter-reading against its own F3, and disclosed on F1 exactly what it had not
established ("I did not produce the straddle against a live Anvil"). That disclosure is what let
me find the gap in F1 quickly rather than having to distrust the whole section. **The one refutation
(F2) is a reading error, not a fabrication** — the mechanism R2 describes is real, it simply is not
overclaimed anywhere.

**On the F1 severity change.** I lowered HIGH → LOW on evidence R2 could have obtained and did not:
the pipeline continues past the simulator, and the next component refuses the straddle. R2 asserted
the opposite ("the E3 check cannot detect it") without testing it. That is the single load-bearing
error in its report, and it is worth recording as a technique note: **a finding about an
intermediate artifact must follow the artifact to its consumer before its severity is set.**

**Unadjudicated by me:** nothing. All six findings have a verdict. No finding of R2's remains
PENDING on my account.

**Provenance.** My probe is at `adjudication/probes-r4/a1-straddle-then-signer.ts` and is
read-only — it imports w4's source and mutates no file. Post-adjudication the w4 worktree is
unchanged: `git diff HEAD --stat -- .` shows only the two provisioned submodule symlink entries,
and the three toolchain symlinks (`contracts/lib/forge-std`,
`contracts/lib/openzeppelin-contracts`, `ts/node_modules`) are intact.
