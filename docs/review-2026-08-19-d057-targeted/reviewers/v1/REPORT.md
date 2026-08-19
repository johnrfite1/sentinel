# V1 — targeted independent reverification of `R3-F6` and `R3-F7`

**Reviewer:** V1 (independent; authored none of the code or repairs below).
**Frozen commit evaluated:** `c8d15a76425544148d7da2f8fa0c003feb6ad2b7` — confirmed by
`git rev-parse HEAD` in the reviewer worktree before any other work.
**Baseline of the shipped suite at that commit:** `92 tests passed, 0 failed, 0 skipped`
(6 suites), from `forge test` in `contracts/`.

| Finding | Verdict |
|---|---|
| **`R3-F6`** — vault timestamp boundaries, incl. `executeWithOverride`'s `auth.expiresAt` | **HOLD** |
| **`R3-F7`** — the complete required vault event set, incl. `MandateRevoked` | **FAIL** |

`R3-F7` fails on a *different* event from the one that failed last round. `MandateRevoked`
— the specific omission that sent the repair back — is now covered thoroughly, and so are the
other five events the repair added. The failure is that the required set is larger than the
repair's six, and one member of it, `ActionExecuted`, can still be made to state something
false with the whole suite green.

All paths in this report are repository-relative or `<WORKTREE>/`-relative. Full command
transcripts are in `PROBES.md`; blind spots are in `COVERAGE.md`.

---

## Item 1 — `R3-F6`: VERDICT `HOLD`

### 1.1 The general property, stated before looking at the fix

> Wherever the vault compares the current block time to a time field carried by a credential,
> it defines a validity window. The window's last valid instant is exactly the field's value —
> the boundary is **inclusive**. Two distinct mis-statements of that rule exist at every such
> site: shifting the window one second **earlier** (refusing the instant that should still be
> accepted) and one second **later** (accepting the instant that should already be refused).
> A boundary is *pinned* only when a named regression test dies for **each** of those two
> mis-statements, at **each** site, and dies **because of that site's own check** rather than a
> neighbouring one.

Two corollaries I held myself to, because both are ways this could look pinned and not be:

* A test that only warps *past* expiry leaves `>` -> `>=` alive, and `>=` rejects the commonest
  real case — the credential used at its own deadline. One-sided pinning is half-pinning.
* A boundary test that also crosses a *different* window is killed by the wrong check, and
  proves nothing about the one it names.

### 1.2 Mechanical sibling enumeration

I did not take a count from the finding, the repair, or any document. Run from `contracts/`:

```
grep -rn "block\.timestamp\|block\.number\|\bnow\b" src/
grep -rniE "expiresat|deadline|notbefore|validfrom|validuntil|issuedat|timestamp|expiry|expires" src/
```

**Every comparison of `block.timestamp` against a credential time field in the vault — the
complete list, three entries:**

| # | Site | Comparison | Reached from |
|---|---|---|---|
| 1 | `contracts/src/SentinelVault.sol:268` (`executeWithOverride`) | `block.timestamp > auth.expiresAt` | `executeWithOverride` only |
| 2 | `contracts/src/SentinelVault.sol:306` (`_checkAction`) | `block.timestamp > action.deadline` | **both** entry points |
| 3 | `contracts/src/SentinelVault.sol:341` (`_checkReceipt`) | `block.timestamp > receipt.expiresAt` | **both** entry points |

`executeWithOverride`'s `auth.expiresAt` — the entry that survived the first repair — **is in
the list.** There is no fourth site: the greps return no other `block.timestamp` in
`contracts/src/SentinelVault.sol` outside NatSpec prose and the three `forge-lint` suppression
comments that sit immediately above these three lines.

**The named control, also enumerated rather than assumed:** the value ceiling at
`contracts/src/SentinelVault.sol:324`, `action.valueWei > maxNativeValueWei`.

**Sibling outside the vault, enumerated and ruled out on inspection:**
`contracts/src/demo/DemoPay.sol:57`, `base > uint64(block.timestamp)`. This is a `max()`
selection computing an entitlement start in the demo *target*, not a comparison the vault's
authorization decision passes through. Recorded so the list is complete, not deferred silently.

**Time-like fields the vault declares but never compares** (an enumeration result, and the
reason the answer is three and not more): `MandatePayload.validAfter` / `.validUntil`,
`PolicyPayload.validAfter` / `.validUntil`, `DecisionReceiptPayload.issuedAt`,
`OverrideAuthorizationPayload.issuedAt`, and `DecisionReceiptPayload.simulationBlockNumber` /
`.simulationBlockHash`. The vault binds mandate and policy by **hash only** and never reads
their validity windows; there is no lower ("not before") bound anywhere in the contract. These
are not unpinned boundaries — they are boundaries the vault does not have. See RESIDUAL F6-R3.

### 1.3 Falsification — every site, both directions, plus deletion

Harness: a reviewer-written mutation driver kept in the session scratchpad. One textual mutation
to `contracts/src/SentinelVault.sol` at a time, **full** `forge test` after each, file restored
from a byte copy afterwards. `COMPILE_ERROR` is classified separately from `SURVIVED` so a build
break cannot read as a pass. Harness self-tests are in `PROBES.md` section 1.

| Mutation | Direction | Result | Named test that failed |
|---|---|---|---|
| `auth.expiresAt`: `>` -> `>=` | tighten | **CAUGHT** | `test_overrideExpiry_atTheBoundaryIsStillValid` — `[FAIL: OverrideExpired()]` |
| `auth.expiresAt`: `> uint256(auth.expiresAt) + 1` | loosen 1s | **CAUGHT** | `test_overrideExpiry_oneSecondPastIsRejected` |
| `auth.expiresAt`: check deleted | removed | **CAUGHT** | `test_overrideExpiry_oneSecondPastIsRejected`, `test_expiredOverrideIsRejected` |
| `action.deadline`: `>` -> `>=` | tighten | **CAUGHT** | `test_actionDeadline_atTheBoundaryIsStillValid` — `[FAIL: ActionExpired()]` |
| `action.deadline`: `+ 1` | loosen 1s | **CAUGHT** | `test_actionDeadline_oneSecondPastIsRejected` |
| `action.deadline`: check deleted | removed | **CAUGHT** | `test_actionDeadline_oneSecondPastIsRejected`, `test_expiredActionIsRejected` |
| `receipt.expiresAt`: `>` -> `>=` | tighten | **CAUGHT** | `test_receiptExpiry_atTheBoundaryIsStillValid` — `[FAIL: ReceiptExpired()]` |
| `receipt.expiresAt`: `+ 1` | loosen 1s | **CAUGHT** | `test_receiptExpiry_oneSecondPastIsRejected` |
| `receipt.expiresAt`: check deleted | removed | **CAUGHT** | `test_receiptExpiry_oneSecondPastIsRejected`, `test_expiredReceiptIsRejected` |
| **CONTROL** value ceiling: `>` -> `>=` | tighten | **CAUGHT** | `test_valueCeiling_atTheCapIsAllowed`, `test_LIMIT_nativeCeilingIsPerActionAndBoundsNoAggregate` |
| **CONTROL** value ceiling: `+ 1` | loosen 1 wei | **CAUGHT** | `test_valueCeiling_oneWeiOverIsRejected`, `test_valueOverHardCapIsRejectedEvenWithAValidReceipt`, `test_LIMIT_nativeCeilingIsPerActionAndBoundsNoAggregate` |

**Six of six timestamp mutants killed. Zero survivors.** Each of the six is killed by a
*distinct* named test; no test does double duty across two boundaries.

### 1.4 Proving the kill came from the right check (COMMON-BRIEF trap 4)

The three tighten mutants were re-run against the binding suite alone with per-test output.
Each mutant produced **exactly one** failure, the revert selector in the failure message named
**the check under test**, and the other five boundary tests stayed green:

```
TIGHTEN auth.expiresAt    -> [FAIL: OverrideExpired()] test_overrideExpiry_atTheBoundaryIsStillValid
                             (5 other boundary tests PASS)
TIGHTEN action.deadline   -> [FAIL: ActionExpired()]   test_actionDeadline_atTheBoundaryIsStillValid
                             (5 other boundary tests PASS)
TIGHTEN receipt.expiresAt -> [FAIL: ReceiptExpired()]  test_receiptExpiry_atTheBoundaryIsStillValid
                             (5 other boundary tests PASS)
```

This is what closes the specific hazard the repair's own NatSpec records having hit on its first
draft — warping to the action deadline while the receipt expired 50 minutes earlier, so the test
died on `ReceiptExpired` and measured nothing about the deadline. It does not happen now.

### 1.5 Paired controls that must behave the opposite way

The brief requires a value *comfortably inside* the window still to be accepted, so that a vault
which had simply started refusing everything cannot pass. Three layers, all satisfied:

1. The three `_atTheBoundaryIsStillValid` tests are **positive-execution** tests that assert
   `actionNonce == 1`. A refuse-everything vault fails all three.
2. The value-ceiling pair is the control `R3-F6` itself names, pinned in both directions.
3. I added my own mid-window controls, because "at the boundary" is not "comfortably inside":
   `test_probe_control_midWindowStillExecutesOnTheAutomaticPath` and
   `test_probe_control_midWindowStillExecutesOnTheOverridePath` execute five minutes into a
   ten-minute window on **each** entry point. Both **PASS** at the frozen commit.

### 1.6 What this evidence does and does not establish

**Establishes.** All three of the vault's timestamp comparisons — `auth.expiresAt` included —
are inclusive-at-the-boundary, are pinned in both directions and against deletion by six
distinct named tests, and each kill is attributable to the intended check. Both entry points by
which funds move are covered. The suite is not passing vacuously: a comment-only null mutation
leaves it 92/92, so the harness can report a survivor and did not.

**Does not establish.** (a) That the boundaries are *correct policy*, only that they are
*pinned* — these tests assert an instrument, exactly as the file's own coverage note says.
(b) Anything about the TypeScript engine's ten comparison edges; I did not look at `ts/`.
(c) That a boundary added on *one path only* in future would be noticed — see RESIDUAL F6-R1,
which I measured rather than assumed. (d) Anything about the `gate` profile; all runs here are
the default unseeded profile.

### Verdict — `R3-F6`: **HOLD**

---

## Item 2 — `R3-F7`: VERDICT `FAIL`

### 2.1 The general property, stated before looking at the fix

> Every state change the specification requires to be *logged* must emit an event whose fields
> truthfully describe **that** change. The suite must therefore fail in three separate ways: if
> the event is **absent**; if the event is the **wrong event**; and if any field the event
> carries **says something other than what happened** — and it must do so on **every code path
> that can produce that event**, not merely the one a test happens to drive.

The last clause is the one that decides this item.

### 2.2 The required event set, derived from the guarantee

The guarantee is section 3.3(2) of `Sentinel_Protocol_Lab_Proposal_v0_2.md`:

> *"Human-only **activation, revocation, override, pause, recovery, and signer rotation** are
> separately authenticated, unavailable to the agent, and **logged**."*

Mechanical enumeration, run from `contracts/`:

```
grep -rn "^\s*event " src/                    # 8 events declared on SentinelVault
grep -n  "emit " src/SentinelVault.sol        # 8 emit sites, one per event
grep -rn "expectEmit" test/
grep -rn "emit SentinelVault\." test/
```

Eight events are declared and each is emitted exactly once. Every one of the six state-changing
`onlyOwner` functions emits. Mapping the guarantee onto them:

| section 3.3(2) operation | Event(s) that carry the record |
|---|---|
| activation (mandate) | `MandateActivated` |
| activation (policy) | `PolicyActivated` |
| **revocation** | **`MandateRevoked`** |
| **override** | `OverrideAuthorized` **and** `ActionExecuted.viaOverride` |
| pause | `PausedSet` |
| recovery | `Recovered` |
| signer rotation | `SignerRotated` |
| execution record (3.3(9); the field D-043's own entry names) | `ActionExecuted` |

**The required set is all eight declared events.** `ActionExecuted` is in it on the project's
own reading, not mine: D-043's decision entry states the override defect as *"`ActionExecuted`
records only `viaOverride` and the receipt's `decisionId`"*, and the vault's NatSpec at
`contracts/src/SentinelVault.sol:98` repeats it. `viaOverride` is the only onchain marker
distinguishing an override execution from an automatic one.

No required operation lacks an event. The constructor emits nothing, which is correct — it
performs none of the six operations, and the initial signer and both allowlists are public
state (see `COVERAGE.md`).

### 2.3 `MandateRevoked` — explicitly covered, and the evidence

**Stating it in as many words: `MandateRevoked` is covered, and covered well.** It is asserted
by `test_MandateRevoked_statesTheRevokedHash` in
`contracts/test/SentinelVault.binding.t.sol:384`, which uses
`vm.expectEmit(true, false, false, false, address(vault))` — topic 0 (the event signature) is
always checked by `expectEmit`, and topic 1 is the revoked hash, the event's only argument. All
three mutation classes are killed by that one named test:

| Mutation to `revokeMandate` | Result | Named test |
|---|---|---|
| **OMISSION** — `emit MandateRevoked(previous)` deleted (with its orphaned local) | **CAUGHT** | `test_MandateRevoked_statesTheRevokedHash` |
| **SUBSTITUTION, field** — logs the POST state (`bytes32(0)`) instead of the hash revoked | **CAUGHT** | `test_MandateRevoked_statesTheRevokedHash` |
| **SUBSTITUTION, event** — `emit MandateActivated(previous)` instead | **CAUGHT** | `test_MandateRevoked_statesTheRevokedHash` |

The event-swap kill also establishes, empirically rather than from documentation, that
`vm.expectEmit` checks topic 0 — which is what makes every other SUBEVENT row below meaningful.

### 2.4 Falsification across the whole required set

| Event | OMISSION | SUBSTITUTION (field) | SUBSTITUTION (event) | Killed by |
|---|---|---|---|---|
| `MandateActivated` | CAUGHT | CAUGHT (`bytes32(0)`) | CAUGHT (-> `PolicyActivated`) | `test_MandateActivated_statesTheActivatedHash` |
| `MandateRevoked` | CAUGHT | CAUGHT (post-state) | CAUGHT (-> `MandateActivated`) | `test_MandateRevoked_statesTheRevokedHash` |
| `PolicyActivated` | CAUGHT | CAUGHT (`bytes32(0)`) | not run (see COVERAGE) | `test_PolicyActivated_statesTheActivatedHash` |
| `SignerRotated` | CAUGHT | CAUGHT (`previousSigner` := `newSigner`) | not run | `test_SignerRotated_statesBothEpochsTruthfully` |
| `PausedSet` | CAUGHT | CAUGHT (`!value`) | not run | `test_PausedSet_statesTheNewStateTruthfully` |
| `Recovered` | CAUGHT | CAUGHT (whole balance, not the amount moved) | not run | `test_Recovered_statesRecipientAndAmount` **and** `test_recoverEventReportsTheAmountItActuallyMoved` |
| `OverrideAuthorized` | CAUGHT | CAUGHT (`reasonHash` := 0) **and** CAUGHT (`expiresAt` := 0) | not run | `test_overrideAuthorizationIsLogged` |
| **`ActionExecuted`** | CAUGHT | CAUGHT (`actionNonce` post-increment); CAUGHT (`decisionId` := 0); **SURVIVED (`viaOverride`)** | not run | see 2.5 |

**Control that a correct emission still passes:** the unmutated suite is 92/92, and every
event assertion above is a positive test that requires the *right* event with the *right*
fields to be emitted — a vault emitting nothing, or emitting the wrong event, fails all of them.

### 2.5 The failure

**Mutation `F7-ActionExecuted-SUBVIAOVERRIDE-v2`**, applied to
`contracts/src/SentinelVault.sol:381`:

```
- emit ActionExecuted(actionHash, action.actionNonce, decisionId, viaOverride);
+ emit ActionExecuted(actionHash, action.actionNonce, decisionId, false);
```

(the `viaOverride` parameter is left unnamed so the build stays warning-clean under
`deny = "warnings"`).

**Result: `92 tests passed, 0 failed`.** The full shipped suite is green while the vault's
execution log denies that **any** override has **ever** happened.

`OverrideAuthorized` still fires, so an auditor can see that an authorization was signed — but
`ActionExecuted`, the record of what the vault actually *did*, now says every execution took
the automatic path. Section 3.3(2) requires override to be logged; under this mutation the only
event that states which path executed states it falsely, on every single override, undetected.

**Why the shipped suite cannot see it.** `ActionExecuted` is asserted in exactly one place,
`test_executionEventReportsTheBoundNonceAndTheActualAmount`
(`contracts/test/SentinelVault.backstops.t.sol:474`), which drives `executeWithReceipt` and
expects `viaOverride == false`. The mutation changes nothing on that path. **No test anywhere
in the repository asserts `ActionExecuted` on the override path.** This is the finding's own
shape — a defect surviving one branch away from where it was demonstrated — recurring inside
the file written to close it.

**The paired control, which is what makes this a real hole and not a mis-measurement.** The
mirror mutation — `executeWithReceipt` passing `true` instead of `false`, so the automatic path
is misreported — **is** caught, by that same test:

```
F6-RESID-EXEC-VIAOVERRIDE-SWAP   91 tests passed, 1 failed
  -> test_executionEventReportsTheBoundNonceAndTheActualAmount
```

One direction of the same field is instrumented and the other is not. That asymmetry is the
evidence; it cannot be explained by "the mutation was inert".

**And it is cheaply observable.** A five-line assertion I wrote as an independent instrument,
`test_probe_actionExecutedSaysViaOverrideTrueOnTheOverridePath` in
`<WORKTREE>/contracts/test/V1Probe.t.sol` (source in `PROBES.md` section 5), **passes** at the
frozen commit and **fails** under the mutation:

```
shipped suite + mutation : 92 passed, 0 failed
probe         + mutation : [FAIL: Purchased != expected ActionExecuted]
                           test_probe_actionExecutedSaysViaOverrideTrueOnTheOverridePath
```

### 2.6 Scoping the verdict precisely — what is and is not wrong

This matters, because the fair reading of the repair is narrower than the verdict.

* **The six events the repair itself added are fully pinned**, in both classes, each by a named
  test. `MandateRevoked` — the omission that failed reverification — is among the strongest.
  Nothing the second correction claims for its own six is overstated.
* **What fails is the completeness of the required set.** The repair inherits the framing in
  `contracts/test/SentinelVault.binding.t.sol:28-32` — *"five of the vault's eight events could
  be made to state something false ... exactly the five D-043 did not touch"* — which asserts
  that D-043's three are already safe. **That sentence is false at the frozen commit**, and this
  is the second time a count in this same file has been wrong in the same way. `R3-F7`'s brief
  requires the set to be derived *"not from the finding, not from the repair, and not from any
  prose count"*, and requires OMISSION **and** SUBSTITUTION detection **for each** member.
  `ActionExecuted` is a member and does not have it.

**A judgement call I am flagging rather than making:** whether this is scored as `R3-F7` not yet
closed, or as `R3-F7` closed with a newly-opened defect against D-043's `ActionExecuted`
coverage, is a scoping decision. I am recording it as `FAIL` because the brief's stated bar is
per-event over the *complete* set, and I do not have authority to narrow that bar. **The
question for John:** does `R3-F7` close on the six events its repair scoped, with the
`ActionExecuted.viaOverride` gap raised as a separate item, or does it stay open until the
required set is covered end to end? I have not answered it.

### 2.7 What this evidence does and does not establish

**Establishes.** Seven of the eight required events cannot be omitted, cannot be swapped for
another event, and cannot carry a wrong value in any asserted field without a named test dying.
`MandateRevoked` is among them, verified by three independent mutations. The eighth,
`ActionExecuted`, is instrumented on the automatic path and **not** on the override path, and
one specific field substitution there survives the full suite.

**Does not establish.** (a) That the events are the *right* events for the guarantee beyond the
mapping in 2.2 — that mapping is my reading of the specification text, not a measured fact.
(b) That every field of every event is asserted; I verified the `expectEmit` flag combinations
and measured up to two field substitutions per multi-field event, not all of them
(`COVERAGE.md`). (c) Anything about offchain consumers of these logs, the D-010 verifier
included.

### Verdict — `R3-F7`: **FAIL**

---

## RESIDUALS

Kept deliberately separate from the verdicts. None of these is a claim that a repair failed.

**F6-R1 — the shared-function assumption is load-bearing and untested.** `action.deadline` and
`receipt.expiresAt` are pinned only through `executeWithReceipt`. I inserted a *path-specific*
one-second-tighter deadline check into `executeWithOverride` alone, and separately a
path-specific receipt-expiry check:

```
F6-RESID-OVR-OWN-DEADLINE         92 tests passed, 0 failed
F6-RESID-OVR-OWN-RECEIPT-EXPIRY   92 tests passed, 0 failed
```

Both invisible. At the frozen commit this is harmless — the checks live in `_checkAction` and
`_checkReceipt`, which both entry points call, so every mutation to them *is* caught. It is
recorded because the repair protocol's step 5 asks for falsification through every invocation
shape, and here two of three boundaries are falsified through one shape only. The day either
check is specialised per path, nothing notices.

**F6-R2 — no invariant arm covers a time window.** Section 3.3's *"Required Foundry invariants"*
list opens with *"Every executed agent action used the active mandate, active policy, current
signer, current action nonce, **and valid time window**."* Enumerating
`contracts/test/SentinelVault.invariants.t.sol` gives eleven `invariant_*` functions and none is
about time, although `VaultHandler` does expose a `warp` action the fuzzer drives. All boundary
coverage is unit tests. Not in scope for `R3-F6`; recorded because it is adjacent and mechanical.

**F6-R3 — the absent boundaries are not pinned as absent.** The vault enforces no lower time
bound and never reads `MandatePayload.validUntil`, `PolicyPayload.validUntil`, or either
`issuedAt`. This repository elsewhere pins exactly this kind of deliberate limit with a
`test_LIMIT_*` test — `test_LIMIT_reinstatingARotatedOutSignerRevivesItsOldReceipts`,
`test_LIMIT_vaultCapsNativeValueOnlyAndNotTokenAuthority` — and there is no such test for
onchain time. A future contributor adding a well-meant `validUntil` check would break no test.

**F7-R1 — a false claim in the vault's own NatSpec about the logging guarantee.** At
`contracts/src/SentinelVault.sol:274-276`:

> *"emitted AFTER authentication and BEFORE the call — so the log records only authorizations
> that actually passed, **and records them even if the external call then reverts the
> transaction away**."*

The emphasised half is false onchain. `_consumeAndCall` ends
`if (!ok) revert CallFailed(ret);`, which propagates out of `executeWithOverride` and reverts
the **whole transaction**; a reverted transaction's logs are discarded with its state.
Demonstrated by `test_probe_failedExternalCallOnTheOverridePathRevertsEverything`, which starves
the vault exactly as `test_aFailedExternalCallRevertsRatherThanConsumingTheNonce` does, and
observes `actionNonce == 0` afterwards — the state moved back, so nothing that transaction wrote
reached the chain.

**This one has a trap attached, and it is probably how the sentence came to be written.**
Foundry's `vm.recordLogs` **keeps** logs emitted inside the reverted frame. My probe
`test_probe_whatForgeRecordsForTheRevertedOverride` prints
`OverrideAuthorized entries the recorder kept: 1`. A test written with that cheatcode would
appear to confirm the claim. It is a harness artefact, not chain behaviour.

This is a documentation defect in a sentence about the section 3.3(2) *"logged"* requirement, of
the same family as A-063. **It is not a defect in the repair under review**, and I am not
proposing a wording — that is John's to rule on.

**F7-R2 — one event assertion does not bind the emitter.**
`contracts/test/SentinelVault.backstops.t.sol:757` uses `vm.expectEmit(true, true, true, true)`
with no address argument, so it does not check that `OverrideAuthorized` came from the vault
rather than from the demo target. Every other `expectEmit` in the suite passes
`address(vault)`. Low severity — no other contract in the tree declares that event — but it is
an inconsistency in an assertion that is otherwise the strongest of the eight.

---

## Attestations

* I authored none of the code, tests, or repairs evaluated here.
* I worked only inside my own worktree at `c8d15a76425544148d7da2f8fa0c003feb6ad2b7`; the
  primary tree was read for briefs and docs only, and written only in this evidence directory.
* `contracts/src` and `contracts/test` are byte-identical to the frozen commit at the end of
  this review; the only untracked addition in the worktree is my own probe file
  `<WORKTREE>/contracts/test/V1Probe.t.sol`, which is **not** a proposed repair.
* I have signed nothing, ratified nothing, and answered no question that is John's.
