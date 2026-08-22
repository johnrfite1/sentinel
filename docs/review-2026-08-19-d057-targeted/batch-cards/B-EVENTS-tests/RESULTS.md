# B-EVENTS — measured results

## Verdict

**HOLD for test-contract readiness.** The frozen independent patch discriminates the declared
event boundary, the known current-suite hole, F7-R1's false comment, live durable receipt
semantics, and top-level fast-gate binding. No production implementation has been made or
approved.

## 1. Frozen bytes and unchanged control

| Item | Result |
|---|---|
| subject | `46b62bea748b0dcdf6c02288659a3be1bbb945ba` |
| `TESTS.patch` | applies cleanly; sha256 `b057d64f0b01d4a4de2cb8e2ac30ba4e16d60ffc0cfcf02544b4260be893c931` |
| extracted `SentinelVault.events.t.sol` | sha256 `2a9219cc5138858b012b0bc56069490db3dd7d1963b73ccc19c28a48ce2b029e` |
| format check | pass |
| warning-clean build | pass |
| focused unchanged suite | **11 passed, 0 failed, 0 skipped** |

The 11 tests comprise eight exact success-route/event tests, two honest downstream-revert
rollback tests, and one explicitly labelled `vm.recordLogs` limitation calibration. The relay is
test-only scaffolding for the live receipt probe and has no production surface.

## 2. The measured pre-repair coverage hole

Warning-clean `field_action_via_false` replaces `_consumeAndCall`'s boolean parameter with an
unnamed parameter and always emits `false`.

| Suite | Result |
|---|---|
| frozen subject's current Solidity suite, without `TESTS.patch` | **92 passed, 0 failed** — mutant survives |
| frozen independent focused patch, same mutant | **10 passed, 1 failed** |

The only frozen-test failure is
`test_OverrideAndActionExecuted_exactFieldsTrueRouteOrderAndVaultEmitter`. The automatic-path
success test remains green. This reproduces R3-F7 at the current subject and demonstrates the
new assertion's marginal observation rather than relying on the historical report.

## 3. Final mutation measurement

`mutation-matrix.tsv` is the exact 51-line result (one header plus 50 cases):

```text
PRODUCTION  build PASS  behavior CAUGHT  49
CONTROL     build PASS  behavior CAUGHT   1
PRODUCTION  build FAIL                    0
PRODUCTION  SURVIVED                      0
build output containing "warning"        0
```

The production rows are:

- 8/8 required-event omissions caught;
- 18/18 meaningful field substitutions caught, including both `viaOverride` directions;
- 2/2 execution call-site route substitutions caught;
- 17/17 legal indexed/data-location substitutions caught;
- 1/1 wrong event-topic substitution caught; and
- 3/3 unexpected extra-event substitutions caught.

The separate wrong-emitter control is caught and is not counted as a production mutant. Every row
was built under `deny = "warnings"` before the behavioral test. No compile or warning failure was
credited as a catch.

## 4. Event membership, order and emitter

The frozen test's event declarations are independent of the production declarations. Every
expected event binds `address(vault)`. Successful-route recorder censuses filter by the actual
emitter and require exact topic membership/order:

- each owner control: its one named vault event only;
- automatic: `ActionExecuted` only, with `viaOverride=false`;
- override: `OverrideAuthorized` then `ActionExecuted`, with `viaOverride=true`.

This exact census was added after self-review found that `expectEmit` alone can skip unexpected
intervening logs. The three extra-event mutants demonstrate the correction. This pre-freeze
instrument repair changed no production file and consumed no implementation attempt.

## 5. Durable live-receipt matrix

The exact Anvil output was:

```json
{"directSuccess":{"status":"success","logs":["OverrideAuthorized","ActionExecuted","Purchased"],"vaultLogCount":2,"nonce":"1"},"directFailure":{"status":"reverted","logs":[],"vaultLogCount":0,"nonce":"0"},"relaySwallowsFailure":{"status":"success","logs":["Attempted"],"vaultLogCount":0,"attemptedOk":false,"nonce":"0"},"relaySuccess":{"status":"success","logs":["OverrideAuthorized","ActionExecuted","Purchased","Attempted"],"vaultLogCount":2,"attemptedOk":true,"nonce":"1"},"ancestorRevertsAfterSuccess":{"status":"reverted","logs":[],"vaultLogCount":0,"attemptedOk":null,"nonce":"0"}}
```

These are mined transaction receipts. The successful relay control proves the relay and payload
can carry the two vault events. The swallowed-failure transaction is itself successful but carries
only `Attempted(false)`; the inner vault log and nonce are absent. The ancestor-revert route first
allows a successful inner vault call and then reverts the outer frame; its receipt has zero logs
and the vault nonce remains zero.

By contrast, the labelled Foundry limitation test observes one retained reverted-frame
`OverrideAuthorized` recorder entry while the vault nonce is zero. That entry is a cheatcode
artifact and is used only to demonstrate why it is inadmissible as durable evidence.

## 6. F7-R1 comment probe and exact allowed repair

Baseline:

```text
exit 1
false_claim_count=1
truthful_replacement_count=0
```

After applying only `NATSPEC.patch`:

```text
exit 0
false_claim_count=0
truthful_replacement_count=1
git diff --check: pass
diff numstat: 6 insertions, 3 deletions in contracts/src/SentinelVault.sol
```

The patch changes comments only. It adds no log-preservation machinery. The wording is tied to the
five-route live matrix and says that a durable log requires downstream success and retention of
every enclosing frame; it does not use the ambiguous “if and only if the action executed.”

## 7. Top-level fast gate

| Case | Foundry | Later consumers | Top level |
|---|---|---|---|
| unchanged subject + `TESTS.patch` | 103/103 | TS 527/527; verifier 221; samples 7; tamper 78/30 | **exit 0, GATE PASSED** |
| same + warning-clean `field_action_via_false` | 102/103; only named override event test fails | same later consumers green | **exit 5, GATE FAILED** |

The unchanged `scripts/test.sh` automatically discovers the added `.t.sol` file. No gate change is
part of this card. Full raw gate logs are identified by hash in `GATE-BINDING.md`; tracked
summaries omit the one machine-specific path printed by the pre-existing rename guard. No deep
profile was run or claimed.

## 8. Repository and workspace guards

Run with the complete evidence directory staged:

| Guard | Result |
|---|---|
| `check-secrets.sh` default | `secret guard: clean` |
| `check-secrets.sh --staged` | `secret guard: clean` |
| `check-review-scope.sh` | 566/566 tracked files assigned; exit 0 |
| `check-findings-ledger.sh` | all D-057(1) ruled totals match; exit 0 |
| `check-suite-floors.sh` | all six canonical floors read from the sole copy; exit 0 |
| `check-vendor-honesty.sh` | mechanical conditions pass; no held D-008 question answered by this author |
| workspace `run_guards.sh Sentinel` | **13 findings, 13 baselined, 0 new; PASS** |

The workspace guard was first invoked from the project directory with a workspace-relative
project argument and correctly refused `no such directory` at exit 2 before scoring. The recorded
result is the corrected documented invocation from the workspace root. Baselined machine-state
findings remain accepted debt, not a clean-repository claim.

## 9. Limits carried with the HOLD

The HOLD is only for this test instrument and the boundary in `COVERAGE.md`. It does not approve
an implementation, assert repository-wide event completeness, re-prove the authentication or
execution system, assess D-055, sign/reopen a gate, certify a claim, ratify/publish text, rename
the project, expose held D-008 questions, or authorize a push.
