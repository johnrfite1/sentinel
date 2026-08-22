# B-EVENTS — top-level fast-gate binding

**Subject:** `46b62bea748b0dcdf6c02288659a3be1bbb945ba`.

**Unchanged gate:** `scripts/test.sh`, sha256
`66c272b90a16b037e3fcfc6f0d9184c48f63ac32e62538be7b6cd96a93801b79`, subject blob
`0c6c38ed746925d52720468865ca61eb31ae7ddd`.

**Frozen test patch:** sha256
`b057d64f0b01d4a4de2cb8e2ac30ba4e16d60ffc0cfcf02544b4260be893c931`; extracted test source
sha256 `2a9219cc5138858b012b0bc56069490db3dd7d1963b73ccc19c28a48ce2b029e`.

The patch adds `contracts/test/SentinelVault.events.t.sol`. The existing Foundry invocation in
`scripts/test.sh` discovers `test/*.t.sol` automatically, so no gate script or product script is
edited to bind the test.

## Unchanged control

On a private detached clone of the subject with only `TESTS.patch` applied:

```text
exit=0
103 tests: 103 passed, 0 failed, 0 skipped
typescript: 527 tests (floor 527)
suite 221 (floor 221) · verdict clean · samples 7 (floor 7) · tamper 78 cases / 30 modes (floors 78/30)
GATE PASSED
```

Full raw gate-log sha256:
`cf969c64238a6c764f7d9db73aa380e7ac9f702d2898de8cf83e26723c73c20f`.

## Targeted falsification

The same clone then received only warning-clean production mutant `field_action_via_false`:

```diff
-        bool viaOverride
+        bool
...
-        emit ActionExecuted(actionHash, action.actionNonce, decisionId, viaOverride);
+        emit ActionExecuted(actionHash, action.actionNonce, decisionId, false);
```

The mutant build passed with zero warnings. The unchanged top-level fast gate returned:

```text
exit=5
[FAILURE] test_OverrideAndActionExecuted_exactFieldsTrueRouteOrderAndVaultEmitter()
103 tests: 102 passed, 1 failed, 0 skipped
typescript: 527 tests (floor 527)
suite 221 (floor 221) · verdict clean · samples 7 (floor 7) · tamper 78 cases / 30 modes (floors 78/30)
GATE FAILED
```

Full raw gate-log sha256:
`d5eac43cf78fd274bded0787ee0e91cc077ac0b3b87c622fedd4aada326c64b6`.

The automatic event test stayed green. The only Foundry failure was the named override assertion;
later TypeScript and verifier consumers remained green. The falsification therefore binds the
top-level refusal to the new event test rather than to an unrelated stage.

## Limit

This establishes the requested **fast-profile** gate binding for the exact patch and named
mutant. It does not run or discharge a deep-profile obligation. It is not evidence for any event,
route, field, or repository fact outside `COVERAGE.md`'s explicit boundary, and it is not a generic
prose-consistency guard.
