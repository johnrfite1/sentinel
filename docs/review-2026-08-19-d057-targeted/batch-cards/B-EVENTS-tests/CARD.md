# B-EVENTS — frozen independent test contract

**Verdict: HOLD for test-contract readiness only.** This is not a product approval, gate
signature, certification, ratification, implementation authorization, or publication.

**Frozen subject:** `46b62bea748b0dcdf6c02288659a3be1bbb945ba` (tree
`e5d6044d048b2ba56c6c4db8d9e08ad1bc5d2788`). The subject was clean when authorship began.
The independent test author wrote none of the forthcoming Batch B implementation.

**Authority:** D-058(1), (5), (8)B and (9); D-059(9); D-060(1); D-066(2)–(3). The actual product
guarantee is proposal §3.3(2): human-only activation, revocation, override, pause, recovery and
signer rotation are separately authenticated, unavailable to the agent, and logged.

This directory is the complete test-only deliverable. `TESTS.patch` and `NATSPEC.patch` are
preserved proposals and are not applied in this commit. No production code, existing product
test, `scripts/test.sh`, maintained claim, signed material, prior evidence, or gate record is
changed.

## 1. Declared boundary

Completeness is claimed only for:

- the eight event declarations and eight emit sites in the frozen
  `contracts/src/SentinelVault.sol`;
- the six owner-control functions, the automatic execution path, the override execution path,
  and `_consumeAndCall` in that file;
- the exact event fields, indexed/data layout, vault emitter, per-route event membership and
  order described below;
- durable receipt/state behavior for successful, downstream-reverted, swallowed-inner-revert,
  and ancestor-reverted override transactions; and
- the false F7-R1 comment immediately before `OverrideAuthorized`.

This is not a repository-wide event-completeness claim. Exclusions are in `COVERAGE.md`.

## 2. Independently derived required set

The proposal names six human operations. The current vault API splits activation into mandate and
policy activation, so the API exposes seven human-control events. D-058 separately requires both
execution routes and truthful `viaOverride`, adding the shared execution event.

| Required vault event | Successful route(s) | Frozen truth |
|---|---|---|
| `MandateActivated` | `activateMandate` | activated mandate hash |
| `MandateRevoked` | `revokeMandate` | previous active mandate hash |
| `PolicyActivated` | `activatePolicy` | activated policy hash |
| `SignerRotated` | `rotateSigner` | previous and new signer |
| `PausedSet` | `setPaused(true/false)` | new pause state |
| `Recovered` | `recover` | actual recipient and amount |
| `OverrideAuthorized` | successful retained override only | exact authenticated owner authorization consumed by that successful transaction |
| `ActionExecuted` | automatic and override | exact action hash, bound pre-increment nonce and decision id; `false` automatic, `true` override |

No ninth vault event exists in the frozen declaration or emit inventory. `DemoPay.Purchased` and
the probe-only relay's `Attempted` are non-vault events and are not members of this set.

## 3. Frozen instruments

| File | Role |
|---|---|
| `TESTS.patch` | Adds one independent Solidity test file with 11 unchanged controls, frozen local event declarations, exact emitter/topic censuses, field assertions, both execution routes, success state controls, rollback controls, and one explicitly labelled Foundry-recorder limitation test. It also contains the test-only relay used by the live probe. |
| `mutate.py` | Applies one exact warning-clean mutant to a caller-supplied isolated checkout. Forty-nine production mutants cover all eight omissions, every event field, both boolean directions and call-site routes, every indexed/data location, wrong event topic, and unexpected extra events. One separate test-oracle control changes the expected emitter. |
| `live-receipt-probe.ts` | Runs five transactions on live Anvil receipts: direct success, direct downstream failure, swallowed downstream failure, relayed success, and ancestor revert after a successful inner vault call. |
| `NATSPEC.patch` | The only allowed F7-R1 production repair: six truthful comment lines; no executable change. |
| `nat-spec-probe.py` | Fails the false baseline wording and passes only the exact truthful replacement. |

The executable commands and hashes are frozen in `RUNBOOK.md` and `CHECKSUMS.sha256`.

## 4. Contract the implementer receives

The smallest admissible Batch B implementation is:

1. apply `TESTS.patch` without weakening, deleting, or editing the independent test;
2. replace only the false F7-R1 comment using exact `NATSPEC.patch`; and
3. make no event machinery change unless the fixed tests expose a contradiction on the exact
   implementation candidate.

The exact truthful replacement is:

```solidity
        // §3.3(2)'s "logged": emitted after every override-authentication check passes and
        // before the external call. A durable OverrideAuthorized log exists only if the
        // downstream call succeeds and every enclosing call frame commits. Any revert of
        // this frame or an ancestor discards the log and nonce update. The event therefore
        // records an override authorization consumed by a successful, retained vault
        // execution; it does not record a failed or merely attempted override. (D-043, F7-R1)
```

This wording intentionally rejects “if and only if the action executed.” That phrase is
ambiguous when an inner call succeeds and an ancestor later reverts. The replacement instead
states the EVM retention conditions measured by the live receipt matrix.

## 5. Fixed success condition

The contract is satisfied only if all of the following hold on the implementation candidate:

- `TESTS.patch` applies without editing and its focused suite passes;
- all eight event declarations, indexed/data layouts, exact fields and emit routes remain true;
- each owner-control success route emits exactly its one named vault event;
- automatic success emits exactly `ActionExecuted(..., false)` from the vault;
- override success emits exactly `OverrideAuthorized` then `ActionExecuted(..., true)` from the
  vault, with all fields exact;
- downstream or ancestor revert retains no vault log or nonce state in the transaction receipt;
- the false comment is absent and the exact replacement is present once;
- the unchanged top-level fast gate passes and the known `viaOverride=false` mutant makes that
  same gate fail at the Solidity stage; and
- repository/workspace guards show no new finding.

Compile errors and warnings are instrument failures, not behavioral catches. Any invalid frozen
test stops implementation for independent confirmation. Per D-058(9), a failed implementation
gets at most one bounded correction under this same contract; it does not authorize test repair or
scope expansion.
