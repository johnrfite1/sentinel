# V1 — PROBES: every command run, and its material output

Includes the probes that died, measured nothing, or lied. Frozen commit
`c8d15a76425544148d7da2f8fa0c003feb6ad2b7`. All commands run from `contracts/` in the reviewer
worktree unless stated. No machine-specific paths appear here by design.

---

## 0. Confirming the commit and the baseline

```
$ git rev-parse HEAD
c8d15a76425544148d7da2f8fa0c003feb6ad2b7

$ forge --version
forge Version: 1.7.1  Commit SHA: 4072e48705af9d93e3c0f6e29e93b5e9a40caed8

$ forge test
Ran 6 test suites in 9.92s: 92 tests passed, 0 failed, 0 skipped (92 total tests)
```

`git status --porcelain` in the worktree errors on the vendored forge-std submodule
(`fatal: not a git repository: contracts/lib/forge-std/...`); `--ignore-submodules=all` was used
instead. Worth recording as an instrument quirk: the bare command exits 128, and a script that
treated that as "clean" would be wrong in both directions.

---

## 1. HARNESS SELF-TESTS — run before trusting any result

A mutation harness that cannot report a survivor, or that reports a build break as a survivor,
manufactures exactly the false clean this project has paid for five times. Both were tested.

| Self-test | Mutation | Expected | Observed |
|---|---|---|---|
| `SELFTEST-NULL` | insert a comment line above `receive()` | must SURVIVE | **SURVIVED**, `92 tests passed, 0 failed` |
| `SELFTEST-POISON` | `receive() external payable { this_symbol_does_not_exist(); }` | must be COMPILE_ERROR | **COMPILE_ERROR**, `Error (7576): Undeclared identifier` |

The null test is the one that matters: it proves a `SURVIVED` verdict elsewhere in this report is
a measurement and not a broken parser. The poison test proves a failed build is not scored as a
pass.

The driver applies exactly one textual mutation at a time to
`contracts/src/SentinelVault.sol`, asserts the anchor string occurs **exactly once** before
editing (a zero-match anchor is the dead grep the COMMON-BRIEF names), runs the **full**
`forge test`, and restores the file from a byte copy in a `finally` block. Source tree confirmed
byte-identical to the frozen commit after every sweep.

---

## 2. DEAD PROBES AND INSTRUMENT FAILURES — reported because they are findings about my tools

### 2.1 A regex that reported a killed mutant as a survivor

Round 1 extracted failing test names with `^\[FAIL[^\]]*\]\s+(\S+?)\s*\(`. Foundry's actual line
for an `expectEmit` mismatch is:

```
[FAIL: Recovered param mismatch at amount: expected=1000000000000000000 [1e18], got=10000000000000000000 [1e19]] test_Recovered_statesRecipientAndAmount() (gas: 51281)
```

The `[1e18]` inside the reason closes `[^\]]*` early, the match fails, and the harness printed:

```
SURVIVED  F7-Recovered-SUBFIELD  24.7s  90 tests passed, 2 failed
```

**"SURVIVED" and "2 failed" on the same line.** Caught only because the harness records the
pass/fail tally alongside the name list and I cross-checked them. Had it recorded names only,
this review would have reported a `Recovered` hole that does not exist. Fixed by re-parsing the
saved raw outputs with `^\[FAIL[^\n]*\]\s+([A-Za-z0-9_]+)\(` (greedy to the last `]` on the
line) and by classifying on the tally rather than on the names.

### 2.2 A replacement regex that reported every passing test as failing

The round-2 pattern `\]\s+(name)\(` also matches `[PASS] test_x()`, so two genuinely-caught
mutations were annotated with all 92 test names. Harmless in direction — the CAUGHT/SURVIVED
classification came from the tally, not the names — but it would have made the report unreadable
and untrustworthy. Same fix.

### 2.3 Three mutations that never compiled

`contracts/foundry.toml` sets `deny = "warnings"`. Deleting an `emit` orphans the local or
parameter that fed it, and solc's *warning* becomes a build failure:

| Mutation | Compiler output |
|---|---|
| `F7-MandateRevoked-SUBFIELD` | `Warning (2072): Unused local variable` -> `previous` |
| `F7-ActionExecuted-SUBVIAOVERRIDE` | `Warning (5667): Unused function parameter` -> `viaOverride` |
| `F7-ActionExecuted-SUBDECISIONID` | `Warning (5667): Unused function parameter` -> `decisionId` |

**All three would have printed as `SURVIVED` under a harness that only checked whether tests
failed** — and for `SUBVIAOVERRIDE` that would have been accidentally the right answer for
entirely the wrong reason, which is worse than being wrong. Each was re-run as a `-v2` variant
that compiles clean (unnaming the orphaned parameter, or removing the orphaned local). The `-v2`
results are the ones reported.

### 2.4 `vm.recordLogs` retains logs from a reverted frame

Relevant to RESIDUAL F7-R1. See section 6.

---

## 3. R3-F6 — mechanical enumeration

```
$ grep -rn "block\.timestamp\|block\.number\|\bnow\b" src/
src/SentinelVault.sol:27:   (NatSpec prose)
src/SentinelVault.sol:36:   (NatSpec prose)
src/SentinelVault.sol:268:  if (block.timestamp > auth.expiresAt) revert OverrideExpired();
src/SentinelVault.sol:291:  (NatSpec prose)
src/SentinelVault.sol:306:  if (block.timestamp > action.deadline) revert ActionExpired();
src/SentinelVault.sol:341:  if (block.timestamp > receipt.expiresAt) revert ReceiptExpired();
src/SentinelVault.sol:358:  (NatSpec prose)
src/demo/DemoPay.sol:57:    uint64 start = base > uint64(block.timestamp) ? base : uint64(block.timestamp);

$ grep -rniE "expiresat|deadline|notbefore|validfrom|validuntil|issuedat|timestamp|expiry|expires" src/
  (adds only: the three forge-lint suppression comments; the event/struct field declarations;
   and src/types/SentinelTypes.sol's validAfter/validUntil/issuedAt fields, none of which the
   vault compares against block.timestamp anywhere)
```

Three comparison sites in the vault. The control comparison, found by the same sweep:

```
src/SentinelVault.sol:324:  if (action.valueWei > maxNativeValueWei) revert ValueOverCap();
```

---

## 4. R3-F6 — the mutation sweep

Every row: mutation applied, **full** `forge test` run, file restored.

```
CAUGHT  F6-OVR-TIGHTEN        ['test_overrideExpiry_atTheBoundaryIsStillValid']
CAUGHT  F6-OVR-LOOSEN         ['test_overrideExpiry_oneSecondPastIsRejected']
CAUGHT  F6-OVR-DELETE         ['test_expiredOverrideIsRejected', 'test_overrideExpiry_oneSecondPastIsRejected']
CAUGHT  F6-ACT-TIGHTEN        ['test_actionDeadline_atTheBoundaryIsStillValid']
CAUGHT  F6-ACT-LOOSEN         ['test_actionDeadline_oneSecondPastIsRejected']
CAUGHT  F6-ACT-DELETE         ['test_actionDeadline_oneSecondPastIsRejected', 'test_expiredActionIsRejected']
CAUGHT  F6-RCP-TIGHTEN        ['test_receiptExpiry_atTheBoundaryIsStillValid']
CAUGHT  F6-RCP-LOOSEN         ['test_receiptExpiry_oneSecondPastIsRejected']
CAUGHT  F6-RCP-DELETE         ['test_expiredReceiptIsRejected', 'test_receiptExpiry_oneSecondPastIsRejected']
CAUGHT  F6-CTL-VAL-TIGHTEN    ['test_LIMIT_nativeCeilingIsPerActionAndBoundsNoAggregate', 'test_valueCeiling_atTheCapIsAllowed']
CAUGHT  F6-CTL-VAL-LOOSEN     ['test_LIMIT_nativeCeilingIsPerActionAndBoundsNoAggregate', 'test_valueCeiling_oneWeiOverIsRejected', 'test_valueOverHardCapIsRejectedEvenWithAValidReceipt']
```

Mutation shapes (exact):

* TIGHTEN: `block.timestamp > X` -> `block.timestamp >= X`
* LOOSEN: `block.timestamp > X` -> `block.timestamp > uint256(X) + 1`
* DELETE: the whole `if (...) revert ...;` line replaced by `// deleted`
* CONTROL TIGHTEN / LOOSEN: the same two shapes on `action.valueWei > maxNativeValueWei`

### 4.1 Attribution check — the kill came from the right check

Each TIGHTEN mutant re-run against the binding suite alone:

```
$ forge test --match-path 'test/SentinelVault.binding.t.sol'

########## TIGHTEN auth.expiresAt ##########
[PASS] test_actionDeadline_atTheBoundaryIsStillValid()
[PASS] test_actionDeadline_oneSecondPastIsRejected()
[FAIL: OverrideExpired()] test_overrideExpiry_atTheBoundaryIsStillValid()
[PASS] test_overrideExpiry_oneSecondPastIsRejected()
[PASS] test_receiptExpiry_atTheBoundaryIsStillValid()
[PASS] test_receiptExpiry_oneSecondPastIsRejected()

########## TIGHTEN action.deadline ##########
[FAIL: ActionExpired()] test_actionDeadline_atTheBoundaryIsStillValid()
[PASS] the other five boundary tests

########## TIGHTEN receipt.expiresAt ##########
[FAIL: ReceiptExpired()] test_receiptExpiry_atTheBoundaryIsStillValid()
[PASS] the other five boundary tests
```

Exactly one failure per mutant, and the revert selector names the mutated check. No boundary
test is killed by a neighbouring window.

---

## 5. R3-F7 — mechanical enumeration and the mutation sweep

```
$ grep -rn "^\s*event " src/
src/SentinelVault.sol:84:  event MandateActivated(bytes32 indexed mandateHash);
src/SentinelVault.sol:85:  event MandateRevoked(bytes32 indexed mandateHash);
src/SentinelVault.sol:86:  event PolicyActivated(bytes32 indexed policyHash);
src/SentinelVault.sol:87:  event SignerRotated(address indexed previousSigner, address indexed newSigner);
src/SentinelVault.sol:88:  event PausedSet(bool paused);
src/SentinelVault.sol:89:  event Recovered(address indexed to, uint256 amount);
src/SentinelVault.sol:90:  event ActionExecuted(bytes32 indexed actionHash, uint256 indexed actionNonce, bytes32 decisionId, bool viaOverride);
src/SentinelVault.sol:108: event OverrideAuthorized(bytes32 indexed actionHash, bytes32 indexed overrideHash, bytes32 reviewReceiptHash, bytes32 reasonHash, uint64 expiresAt);
src/demo/DemoPay.sol:19:   event Purchased(...)              [demo target, out of the vault's event set]

$ grep -n "emit " src/SentinelVault.sol
189 MandateActivated   195 MandateRevoked   200 PolicyActivated   205 SignerRotated
211 PausedSet          216 Recovered        277 OverrideAuthorized  381 ActionExecuted
```

Eight events, eight emit sites, six state-changing `onlyOwner` functions all emitting: a
one-to-one map with no unlogged owner operation.

```
$ grep -rn "expectEmit" test/
test/SentinelVault.binding.t.sol:336  (true,true,false,false, address(vault))   SignerRotated
test/SentinelVault.binding.t.sol:344  (false,false,false,true, address(vault))  PausedSet(true)
test/SentinelVault.binding.t.sol:350  (false,false,false,true, address(vault))  PausedSet(false)
test/SentinelVault.binding.t.sol:359  (true,false,false,false, address(vault))  MandateActivated
test/SentinelVault.binding.t.sol:368  (true,false,false,false, address(vault))  PolicyActivated
test/SentinelVault.binding.t.sol:385  (true,false,false,false, address(vault))  MandateRevoked
test/SentinelVault.binding.t.sol:396  (true,false,false,true,  address(vault))  Recovered
test/SentinelVault.backstops.t.sol:474 (true,true,false,true,  address(vault))  ActionExecuted (automatic path only)
test/SentinelVault.backstops.t.sol:483 (true,false,false,true, address(vault))  Recovered
test/SentinelVault.backstops.t.sol:757 (true,true,true,true)   [no emitter]     OverrideAuthorized
```

Every declared event has at least one assertion. `ActionExecuted` has exactly one, on the
automatic path.

### 5.1 Sweep results

```
CAUGHT     F7-MandateActivated-OMIT             ['test_MandateActivated_statesTheActivatedHash']
CAUGHT     F7-MandateActivated-SUBFIELD         ['test_MandateActivated_statesTheActivatedHash']
CAUGHT     F7-MandateActivated-SUBEVENT         ['test_MandateActivated_statesTheActivatedHash']
CAUGHT     F7-MandateRevoked-OMIT               ['test_MandateRevoked_statesTheRevokedHash']
CAUGHT     F7-MandateRevoked-SUBFIELD-v2        ['test_MandateRevoked_statesTheRevokedHash']        (91 passed, 1 failed)
CAUGHT     F7-MandateRevoked-SUBEVENT           ['test_MandateRevoked_statesTheRevokedHash']
CAUGHT     F7-PolicyActivated-OMIT              ['test_PolicyActivated_statesTheActivatedHash']
CAUGHT     F7-PolicyActivated-SUBFIELD          ['test_PolicyActivated_statesTheActivatedHash']
CAUGHT     F7-SignerRotated-OMIT                ['test_SignerRotated_statesBothEpochsTruthfully']
CAUGHT     F7-SignerRotated-SUBFIELD            ['test_SignerRotated_statesBothEpochsTruthfully']
CAUGHT     F7-PausedSet-OMIT                    ['test_PausedSet_statesTheNewStateTruthfully']
CAUGHT     F7-PausedSet-SUBFIELD                ['test_PausedSet_statesTheNewStateTruthfully']
CAUGHT     F7-Recovered-OMIT                    ['test_Recovered_statesRecipientAndAmount','test_recoverEventReportsTheAmountItActuallyMoved']
CAUGHT     F7-Recovered-SUBFIELD-v2             ['test_Recovered_statesRecipientAndAmount','test_recoverEventReportsTheAmountItActuallyMoved']  (90 passed, 2 failed)
CAUGHT     F7-OverrideAuthorized-OMIT           ['test_overrideAuthorizationIsLogged']
CAUGHT     F7-OverrideAuthorized-SUBREASON      ['test_overrideAuthorizationIsLogged']
CAUGHT     F7-OverrideAuthorized-SUBEXPIRY      ['test_overrideAuthorizationIsLogged']
CAUGHT     F7-ActionExecuted-OMIT               ['test_executionEventReportsTheBoundNonceAndTheActualAmount']
CAUGHT     F7-ActionExecuted-SUBNONCE           ['test_executionEventReportsTheBoundNonceAndTheActualAmount']
CAUGHT     F7-ActionExecuted-SUBDECISIONID-v2   ['test_executionEventReportsTheBoundNonceAndTheActualAmount']  (91 passed, 1 failed)
SURVIVED   F7-ActionExecuted-SUBVIAOVERRIDE-v2  92 tests passed, 0 failed        <-- THE FAILURE
```

### 5.2 The surviving mutant, in full

```
-        bytes32 decisionId,
-        bool viaOverride
+        bytes32 decisionId,
+        bool
     ) internal returns (bytes memory) {
         bytes32 actionHash = T.hashAction(action);
         actionNonce += 1;

-        emit ActionExecuted(actionHash, action.actionNonce, decisionId, viaOverride);
+        emit ActionExecuted(actionHash, action.actionNonce, decisionId, false);
```

```
$ forge test --no-match-path 'test/V1Probe.t.sol'
Ran 6 test suites in 11.41s: 92 tests passed, 0 failed, 0 skipped (92 total tests)
```

**Paired control — the mirror mutation IS caught.** `executeWithReceipt` made to pass `true`:

```
-        return _consumeAndCall(action, callData, receipt.decisionId, false);
+        return _consumeAndCall(action, callData, receipt.decisionId, true);

91 tests passed, 1 failed
  -> test_executionEventReportsTheBoundNonceAndTheActualAmount
```

The automatic path is instrumented; the override path is not. The asymmetry rules out "the
mutation was inert".

### 5.3 The five-line instrument that does observe it

`<WORKTREE>/contracts/test/V1Probe.t.sol` (reviewer-written, **not** a proposed repair):

```solidity
function test_probe_actionExecutedSaysViaOverrideTrueOnTheOverridePath() public {
    (bytes memory data, T.ActionPayload memory a, T.DecisionReceiptPayload memory r,
     bytes memory sig, T.OverrideAuthorizationPayload memory auth, bytes memory ownerSig)
        = _reviewSet();

    vm.expectEmit(true, true, false, true, address(vault));
    emit SentinelVault.ActionExecuted(T.hashAction(a), a.actionNonce, r.decisionId, true);
    vault.executeWithOverride(a, data, r, sig, auth, ownerSig);
}
```

```
unmutated: [PASS] test_probe_actionExecutedSaysViaOverrideTrueOnTheOverridePath (gas: 136537)
mutated:   [FAIL: Purchased != expected ActionExecuted]
           test_probe_actionExecutedSaysViaOverrideTrueOnTheOverridePath (gas: 155919)
```

(The reported mismatch names `Purchased` because, with `ActionExecuted` no longer matching, the
next log in the transaction is the demo target's. The test fails, which is the point.)

---

## 6. Residual probes

```
SURVIVED  F6-RESID-OVR-OWN-DEADLINE        92 tests passed, 0 failed
SURVIVED  F6-RESID-OVR-OWN-RECEIPT-EXPIRY  92 tests passed, 0 failed
```

Shape (inserted into `executeWithOverride` only, immediately after `_checkReceipt`):

```solidity
// forge-lint: disable-next-line(block-timestamp)
if (block.timestamp >= action.deadline) revert ActionExpired();      // probe 1
if (block.timestamp >= receipt.expiresAt) revert ReceiptExpired();   // probe 2
```

Neither is noticed. See RESIDUAL F6-R1 — this is a coverage statement about invocation shapes,
not a defect at the frozen commit.

### 6.1 The NatSpec log-survival claim (RESIDUAL F7-R1)

```
[PASS] test_probe_failedExternalCallOnTheOverridePathRevertsEverything
```

Starves the vault (`vm.deal(address(vault), 0)`), submits a fully valid REVIEW receipt plus a
valid owner override, and observes `vm.expectRevert()` followed by `actionNonce == 0`. The whole
transaction reverted, so no log it wrote reaches the chain — contradicting *"records them even
if the external call then reverts the transaction away"* at
`contracts/src/SentinelVault.sol:274-276`.

Paired positive control, so this is not "everything reverts now":

```
[PASS] test_probe_control_fundedOverrideDoesProduceTheLog
       (recordLogs count of OverrideAuthorized == 1, actionNonce == 1)
```

**The instrument trap.** The same scenario under `vm.recordLogs`:

```
[PASS] test_probe_whatForgeRecordsForTheRevertedOverride
Logs:
  OverrideAuthorized entries the recorder kept: 1
  total log entries the recorder kept: 2
```

Foundry keeps logs emitted inside a reverted frame. Anyone testing the NatSpec claim with
`recordLogs` would see it "confirmed". It is a harness artefact; the chain-level fact is the
state rollback above.

---

## 7. R3-F6 controls

```
[PASS] test_probe_control_midWindowStillExecutesOnTheAutomaticPath   (gas: 114047)
[PASS] test_probe_control_midWindowStillExecutesOnTheOverridePath    (gas: 134188)
```

Five minutes into a ten-minute window, on each entry point, both execute and bump the nonce. A
vault that had started refusing everything fails both.

---

## 8. Final state

```
$ git status --porcelain --ignore-submodules=all
?? contracts/test/V1Probe.t.sol
?? ts/node_modules

$ forge test --no-match-path 'test/V1Probe.t.sol'
Ran 6 test suites: 92 tests passed, 0 failed, 0 skipped (92 total tests)
```

`contracts/src` and `contracts/test` are byte-identical to the frozen commit. The only addition
is the reviewer probe file, which lives in the reviewer worktree and is not proposed for the
repository.
