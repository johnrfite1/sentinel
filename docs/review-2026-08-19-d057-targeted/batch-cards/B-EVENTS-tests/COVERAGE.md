# B-EVENTS — coverage and limits

## 1. Frozen source inventory

At `46b62bea748b0dcdf6c02288659a3be1bbb945ba`, mechanical enumeration of
`contracts/src/SentinelVault.sol` yields exactly eight event declarations and eight emit sites:

| Event | Declaration | Emit | Route |
|---|---:|---:|---|
| `MandateActivated(bytes32 indexed)` | 84 | 189 | `activateMandate` |
| `MandateRevoked(bytes32 indexed)` | 85 | 195 | `revokeMandate` |
| `PolicyActivated(bytes32 indexed)` | 86 | 200 | `activatePolicy` |
| `SignerRotated(address indexed,address indexed)` | 87 | 205 | `rotateSigner` |
| `PausedSet(bool)` | 88 | 211 | `setPaused` |
| `Recovered(address indexed,uint256)` | 89 | 216 | `recover` |
| `ActionExecuted(bytes32 indexed,uint256 indexed,bytes32,bool)` | 90 | 381 | shared `_consumeAndCall`; automatic and override |
| `OverrideAuthorized(bytes32 indexed,bytes32 indexed,bytes32,bytes32,uint64)` | 108 | 277 | `executeWithOverride` only |

The automatic call site passes `false`; the override call site passes `true`. Override emission is
after every receipt/override/signature/expiry check and before `_consumeAndCall`. `_consumeAndCall`
increments the nonce, emits `ActionExecuted`, calls the target, and reverts the whole frame on a
false call result. No alternate vault execution route or emit site exists inside the declared
file/symbol boundary.

## 2. Test-to-invariant mapping

The independent test declares its own copy of the event ABI. Expected topics and indexed/data
layout therefore do not move when a production declaration is mutated. Every `expectEmit` names
`address(vault)`. After each successful call, an exact emitter/topic census refuses missing,
wrong, reordered, or extra vault events.

| Test | Direct observation |
|---|---|
| `test_MandateActivated_exactFieldAndVaultEmitter` | exact hash; independent topic/layout; vault emitter; exactly one vault event; resulting active hash |
| `test_MandateRevoked_exactPreviousFieldAndVaultEmitter` | exact previous hash; topic/layout/emitter; exactly one; resulting zero hash |
| `test_PolicyActivated_exactFieldAndVaultEmitter` | exact hash; topic/layout/emitter; exactly one; resulting active hash |
| `test_SignerRotated_exactPreviousAndNewFieldsAndVaultEmitter` | both addresses; topic/layout/emitter; exactly one; resulting signer |
| `test_PausedSet_exactTrueAndFalseFieldsAndVaultEmitter` | both boolean directions; topic/layout/emitter and one event per call; resulting state |
| `test_Recovered_exactRecipientAndAmountFieldsAndVaultEmitter` | exact recipient/amount; topic/layout/emitter; exactly one; recipient balance |
| `test_ActionExecuted_automaticExactFieldsFalseRouteAndVaultEmitter` | action hash, bound nonce, decision id, `false`; only one vault event; successful entitlement |
| `test_OverrideAndActionExecuted_exactFieldsTrueRouteOrderAndVaultEmitter` | all five override fields; all four action fields; `true`; exact two-event order; successful entitlement and nonce |
| `test_revertedAutomaticCallRollsBackVaultNonceAndTargetState` | honest downstream revert; nonce and target state both zero |
| `test_revertedOverrideCallRollsBackAuthorizationNonceAndTargetState` | same rollback on override route |
| `test_LIMIT_recordLogsRetainsARevertedOverrideArtifact` | proves Foundry retains one reverted-frame `OverrideAuthorized` recorder entry while nonce is zero; labels that entry non-durable and does not use it as chain evidence |

## 3. Discriminating mutation matrix

All production mutants are exact source replacements. Each is built first under the subject's
`deny = "warnings"`; a failed build or any warning is classified separately and cannot count as
a behavioral catch. The final run contains **49 production mutants**, all warning-clean and all
caught, plus one expected-emitter instrument control.

### 3.1 Every required event omission (8)

`omit_mandate_activated`, `omit_mandate_revoked`, `omit_policy_activated`,
`omit_signer_rotated`, `omit_paused_set`, `omit_recovered`, `omit_override_authorized`, and
`omit_action_executed` each preserve the surrounding successful behavior and remove only the
named receipt. The revoke and action omissions also remove or unname now-unused locals/parameters
so the mutants remain warning-clean.

### 3.2 Every event field (18)

| Event | Field mutant(s) |
|---|---|
| `MandateActivated` | `field_mandate_activated_hash` |
| `MandateRevoked` | `field_mandate_revoked_hash` |
| `PolicyActivated` | `field_policy_activated_hash` |
| `SignerRotated` | `field_signer_previous`, `field_signer_new` |
| `PausedSet` | `field_paused` |
| `Recovered` | `field_recovered_to`, `field_recovered_amount` |
| `OverrideAuthorized` | `field_override_action_hash`, `field_override_hash`, `field_override_receipt_hash`, `field_override_reason_hash`, `field_override_expires_at` |
| `ActionExecuted` | `field_action_hash`, `field_action_nonce`, `field_action_decision_id`, `field_action_via_false`, `field_action_via_true` |

The two `viaOverride` constants are separate because a constant false lies only on the override
route and a constant true lies only on the automatic route. Both named assertions move.

### 3.3 Routes, ABI layout, topic identity, and exact membership (23)

- Call-site truth: `route_automatic_as_override`, `route_override_as_automatic`.
- Every indexed field moved to data (10): `index_mandate`, `index_revoked`, `index_policy`,
  `index_signer_previous`, `index_signer_new`, `index_recovered_to`, `index_action_hash`,
  `index_action_nonce`, `index_override_action_hash`, `index_override_hash`.
- Every data field that can legally become the third indexed field (7): `index_paused`,
  `index_recovered_amount`, `index_action_decision_id`, `index_action_via_override`,
  `index_override_receipt_hash`, `index_override_reason_hash`, `index_override_expires_at`.
- Wrong event identity: `topic_mandate_as_policy`.
- Unexpected vault-event membership: `extra_owner_event`, `extra_automatic_override_event`,
  `extra_override_event`.

The separate `instrument_wrong_emitter` control changes the expected emitter to `DemoPay` and
must fail. It is not counted as a production mutant.

## 4. Durable receipt boundary and F7-R1

`live-receipt-probe.ts` reads mined Anvil transaction receipts, not Foundry recorder output:

| Route | Transaction | Durable receipt | Vault nonce |
|---|---|---|---:|
| direct override success | success | `OverrideAuthorized`, `ActionExecuted`, `Purchased` | 1 |
| direct downstream failure | reverted | no logs | 0 |
| relay swallows inner failure | success | `Attempted(false)` only; no vault log | 0 |
| relay success | success | `OverrideAuthorized`, `ActionExecuted`, `Purchased`, `Attempted(true)` | 1 |
| successful inner vault call, ancestor reverts | reverted | no logs | 0 |

This is why `vm.recordLogs` is not admissible durability evidence and why “if and only if the
action executed” is rejected. `NATSPEC.patch` states downstream success and retained enclosing
frames instead. `nat-spec-probe.py` fails the frozen false comment and passes the exact proposed
replacement.

## 5. Exclusions and blind spots

- Completeness is only for the frozen vault file/API and named routes. No claim is made about all
  events, contracts, scripts, indexers, or documents in the repository.
- The patch does not re-prove owner/signature authentication, reentrancy, hashing, expiry,
  allowlist, pause, cap, or replay safety. Existing suites remain the evidence for those domains.
- The live probe uses Anvil final transaction receipts. It does not test reorgs, RPC/indexer
  retention, archive-node availability, third-party decoding, or mainnet clients.
- Reverted owner-control calls are not separately driven on live receipts. EVM frame rollback is
  exercised through both override downstream/ancestor shapes; the source-order inventory shows
  no post-call owner-control success path outside the declared functions.
- The success fixtures use one nonzero hash/address/amount/value per field, except pause and
  `viaOverride`, whose two boolean values are both driven. Mutation discrimination, not input
  fuzzing, is the purpose of this card.
- No deep-profile gate was run. The requested top-level binding is the fast gate: unchanged
  control plus the known `viaOverride=false` falsification.
- No production repair, existing-test repair, signed-text change, gate reopening, certification,
  ratification, publication, rename, push, or D-055 assessment is performed.
