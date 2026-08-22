# B-EVENTS — FIRST FRESH INDEPENDENT INSTRUMENT REVIEW

# VERDICT: HOLD

No blocking instrument defect was found. The frozen patch independently fixes the eight-event
vault ABI and its successful routes, refuses missing, wrong, reordered and extra vault events,
binds every expected event to the vault emitter, distinguishes both `viaOverride` directions,
and catches every one of its 49 warning-clean production mutants for the intended named test.
The live probe observes mined Anvil receipts rather than Foundry's reverted-frame recorder, and
the proposed NatSpec replacement states the measured EVM retention boundary precisely.

This is a **HOLD for instrument readiness only**. It is not an implementation approval, product
approval, gate signature, certification, ratification, publication, rename, D-055 assessment or
push authorization.

---

## 0. Review identity and bar

| Item | Identity |
|---|---|
| exact instrument subject | `3d8e8dd1f2d9e71df8be60983e842277a9bacb36` |
| subject tree | `91b554eb63da5641ab20206f08d92f259a7ee86a` |
| subject message | `B-EVENTS: freeze independent event test contract` |
| frozen behavioral baseline / subject parent | `46b62bea748b0dcdf6c02288659a3be1bbb945ba` |
| baseline tree | `e5d6044d048b2ba56c6c4db8d9e08ad1bc5d2788` |
| frozen test patch | sha256 `b057d64f0b01d4a4de2cb8e2ac30ba4e16d60ffc0cfcf02544b4260be893c931` |
| extracted test source | sha256 `2a9219cc5138858b012b0bc56069490db3dd7d1963b73ccc19c28a48ce2b029e` |
| NatSpec patch | sha256 `a5937bcbba3e8cd060a320a92f1251c5a6ae8e3cd5098a2a5a8370276a59c29c` |
| mutation driver | sha256 `f6816b1e94d06612d14809919333038dc41c4f56920c398c431ad6429cecb1a6` |
| frozen matrix | sha256 `92769e5dca0c84d15db71abba01bdbe4ff2e49f81180bfe034514246882a4ddd` |
| repository state at start and resumption | clean; HEAD was the exact instrument subject |

I authored neither the instrument nor any future implementation. I read the workspace rules;
D-058, D-059, D-060 and D-066; proposal §3.3(2); the R3-F7 and F7-R1 report, probes, coverage and
adjudication; every file in this instrument directory; the complete vault; the current Solidity
test inventory and event assertions; `contracts/foundry.toml`; and the complete top-level gate.
The exact parent-to-subject diff was also read, not inferred from the commit message.

## 1. Exact scope, derivation and frozen ABI

The parent-to-subject diff adds 22 files and 2,221 lines, all under this one evidence directory.
It changes no production source, existing test, script, fixture, verifier, signed record or
maintained product document. The behavioral replay baseline is therefore byte-identical to the
exact instrument subject on every executable surface.

Proposal §3.3(2) names six human operations: activation, revocation, override, pause, recovery
and signer rotation. The frozen vault splits activation into mandate and policy activation, so
those six requirements map to seven control events. D-058 separately requires the shared
execution event on both routes. Direct source enumeration confirms exactly eight vault event
declarations and exactly eight emit sites:

| Event | Route | Frozen layout |
|---|---|---|
| `MandateActivated` | `activateMandate` | one indexed `bytes32` |
| `MandateRevoked` | `revokeMandate` | one indexed `bytes32`, carrying the previous active hash |
| `PolicyActivated` | `activatePolicy` | one indexed `bytes32` |
| `SignerRotated` | `rotateSigner` | indexed previous and new addresses |
| `PausedSet` | `setPaused` | one data `bool`, driven true and false |
| `Recovered` | `recover` | indexed recipient plus data amount |
| `OverrideAuthorized` | successful retained override | two indexed hashes plus three data fields |
| `ActionExecuted` | automatic and override | two indexed fields plus decision id and route boolean |

The six owner-only functions each have one corresponding emit site. The automatic entry point
passes `false` to the shared `_consumeAndCall`; the override entry point emits
`OverrideAuthorized` after authentication, then passes `true`. No ninth vault event or alternate
vault execution route exists in the declared file/symbol boundary. `DemoPay.Purchased` and the
test relay's `Attempted` are deliberately non-vault events and are correctly excluded from the
vault census.

## 2. The frozen oracle observes what it names

`TESTS.patch` applies cleanly to both the baseline and the exact review subject and adds only
`contracts/test/SentinelVault.events.t.sol`. The extracted file passes `forge fmt --check`, builds
under `deny = "warnings"`, and runs **11 passed, 0 failed, 0 skipped**.

The event ABI is copied independently into the test, so a production indexed/data mutation does
not move the expected declaration. Each `vm.expectEmit` has the correct topic/data flags and
names `address(vault)`. The expected test-contract event is emitted before `vm.recordLogs`, so it
does not contaminate the actual census.

After every successful route, `_assertExactVaultTopics` filters on the actual vault address and
checks topic zero at every position, rejects an event after the expected list is exhausted, and
requires the final count to match. Consequently `expectEmit` cannot silently skip an unexpected
intervening vault event:

- each owner control permits exactly its one named vault event;
- automatic execution permits exactly `ActionExecuted(..., false)`;
- override execution permits exactly `OverrideAuthorized` followed by
  `ActionExecuted(..., true)`; and
- target and relay events remain visible in the receipt probes but are outside the explicitly
  bounded vault-event set.

The success controls also assert resulting mandate, policy, signer, pause, recipient balance,
nonce and entitlement state. The two downstream-revert tests assert nonce and target-state
rollback. The labelled LIMIT test does not call recorder output durable; it demonstrates the
opposite trap by observing one reverted-frame `OverrideAuthorized` artifact beside a zero nonce.

## 3. Complete mutation reproduction

I reran the complete harness in an isolated clone at the frozen behavioral baseline. The output
matrix is byte-identical to `mutation-matrix.tsv` and has the same sha256
`92769e5d…a4ddd`:

```text
PRODUCTION  build PASS  behavior CAUGHT  49
CONTROL     build PASS  behavior CAUGHT   1
PRODUCTION  build FAIL                    0
PRODUCTION  SURVIVED                      0
build output containing "warning"        0
```

The 49 production rows comprise 8/8 event omissions, 18/18 meaningful field substitutions,
2/2 call-site route substitutions, 17/17 legal indexed/data moves, 1/1 topic substitution and
3/3 unexpected-extra-event substitutions. Both boolean constants are separate mutants: forced
false is killed only on the override success route and forced true only on the automatic route.

Representative raw outputs were inspected rather than accepting the matrix labels. They show:

- the signer-previous and recovery-amount mutants fail with the exact mismatched values;
- the two boolean and two call-site-route directions fail in their corresponding named route;
- the extra override event fails the exact topic/order census (and the recorder LIMIT changes
  from one artifact to two);
- the indexed/data mutation fails the affected `ActionExecuted` tests;
- the mandate-to-policy topic substitution names the wrong event; and
- the separate expected-emitter control reports an emitter mismatch in the mandate test.

`omit_override_authorized` also makes the LIMIT calibration fail because the retained artifact
count changes from one to zero, but the actual success-route test independently fails in the same
run. It is therefore not credited solely through the calibration test. No row is a compile,
warning or generic harness-noise catch.

## 4. The current-suite hole and marginal frozen-test kill

I independently applied the warning-clean `field_action_via_false` mutant without the frozen
patch. The complete current Solidity suite remained **92 passed, 0 failed**. After applying the
unchanged patch, the focused result was **10 passed, 1 failed**: only
`test_OverrideAndActionExecuted_exactFieldsTrueRouteOrderAndVaultEmitter` failed, while the
automatic event test and all other focused tests stayed green. This reproduces R3-F7 at the
current baseline and establishes the new test's marginal observation.

## 5. Durable receipts and precise F7-R1 correction

The unmodified live probe was rebuilt against the frozen patch and rerun on Anvil. Its stdout is
byte-identical to the preserved `logs/live-receipt.log` (sha256 `9824847e…51671c4`):

- direct override success: `OverrideAuthorized`, `ActionExecuted`, `Purchased`; two vault logs;
  nonce one;
- direct downstream failure: reverted receipt, no logs, no vault logs, nonce zero;
- swallowed inner failure: successful receipt with only `Attempted(false)`, no vault logs,
  nonce zero;
- relayed success: the two ordered vault events, `Purchased`, then `Attempted(true)`; nonce one;
- successful inner vault call followed by ancestor revert: reverted receipt, no logs, nonce zero.

I independently strengthened the last observation in scratch with Anvil's transaction call trace.
The root relay frame reports `execution reverted`; its vault child has no error and returns
success; the vault's downstream `DemoPay` child also has no error. Thus the zero-log ancestor
receipt is not a failed-inner-call false positive: a successful inner vault execution occurred
and was erased only by the enclosing revert.

`NATSPEC.patch` applies cleanly and changes only comment lines: 6 insertions and 3 deletions.
The frozen baseline probe reports `false_claim_count=1`, `truthful_replacement_count=0`, exit 1;
after the patch it reports `0`, `1`, exit 0. The replacement is accurate:

- emission is after all override authentication checks and before the external call;
- a durable log requires downstream success and every enclosing frame to commit;
- a revert of the vault frame or an ancestor discards both log and nonce update; and
- the event records an authorization consumed in a successful retained execution, not a failed
  or merely attempted override.

It correctly avoids the ambiguous phrase “if and only if the action executed” and adds no
machinery intended to preserve logs across a revert.

## 6. Top-level fast-gate causal binding

I reran both cases serially in an isolated clone of the **exact instrument subject**, with only
the frozen test patch applied before the control.

| Case | Foundry | Later consumers | Top level |
|---|---|---|---|
| unchanged | 103/103, zero failed/skipped | TypeScript 527; verifier 221, samples 7, tamper 78/30 | exit 0; `GATE PASSED` |
| then `field_action_via_false` | 102/103; exactly the named override event test fails | same later consumers green | exit 5; `GATE FAILED` |

The independent raw logs are sha256 `9c4ebdbb…32aad` for the control and
`58c0ca26…e30b` for the mutant. The mutant was separately built first with exit zero and no
warning output. The only Foundry failure says `Purchased != expected ActionExecuted`; the
automatic event test remains successful. This causally binds the top-level refusal to the added
override-route assertion rather than a later or unrelated stage.

The current top-level output still says `foundry: 103 tests (floor 92)`. This review therefore
does **not** claim that the gate's count floor independently pins the new file against deletion.
Instrument preservation comes from the frozen patch and D-058's no-weakening rule; live floor
ownership is outside this card's declared boundary. That limit does not undo the measured causal
binding above.

## 7. Provenance, protected boundaries and checks

- All 21 entries in `CHECKSUMS.sha256` verify. The checksum file is the twenty-second frozen
  instrument file and is intentionally not self-hashed.
- The baseline vault sha256, Solidity-test tree, `scripts/test.sh` blob, `foundry.toml` blob,
  signed Gate S2 blob and every governing-document hash in `PROVENANCE.md` independently match.
- The exact parent-to-subject protected diff is empty across production, existing tests,
  scripts, TypeScript, verifier, fixtures, hooks and `docs/gate-s2-evidence.md`.
- The signed Gate S2 file remains sha256
  `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589`.
- Neither patch is applied in the shared subject. No prior evidence or signed text changed.
- Parent-to-subject and review diffs pass `git diff --check`.
- Repository guards report secrets clean in default and staged modes; review scope
  `R1=370, R2=46, R3=151`, **567/567** tracked files assigned; all ruled finding totals
  matching; all six suite-floor facts single-sourced; and the private rename block intact.
- Workspace guards report 13 machine-state findings, all baselined, zero new; PASS by ratchet.

## 8. Limits and disposition

1. Completeness is only for the frozen `SentinelVault.sol` event declarations, emit sites and
   named routes. It is not repository-wide event or documentation completeness.
2. The test does not re-prove owner/signature authentication, hashing, reentrancy, time windows,
   allowlists, caps or replay safety. Existing suites remain the evidence for those domains.
3. Anvil receipts and one call trace establish the named EVM retention shapes; they do not test
   reorgs, third-party indexers, archive retention or mainnet-client diversity.
4. The fast gate, not the deep profile, is the requested and measured top-level binding. No deep
   result is claimed.
5. One initial reviewer live-probe invocation used a relative Forge root from the wrong directory;
   it compiled nothing and aborted on a missing artifact before any probe transaction. It is
   excluded. The corrected root-level build and byte-identical receipt rerun are the evidence.
6. A remote submodule fetch failed during exact-subject gate-clone provisioning. The clone used
   locally present dependencies at the two exact pinned submodule SHAs via the supported symlink
   layout; the pinned Foundry remappings and successful full gate are the boundary of reliance.

**HOLD.** The instrument is ready to be held fixed for Batch B implementation under D-058. A
future implementer may apply, but not weaken or edit, `TESTS.patch`, and may make only the exact
comment correction in `NATSPEC.patch` unless the frozen tests expose a contradiction. This review
implements or repairs nothing and exercises none of John's permanent authority boundaries.
