# B-EVENTS — INDEPENDENT IMPLEMENTATION VERIFICATION

# VERDICT: **HOLD**

The exact implementation candidate `ff048508d9d3056bf5635233ab0df5e79ecb45d4` holds the
frozen B-EVENTS contract. The candidate is exactly the two A-090-authorized surfaces: the
unchanged frozen 343-line event test and the exact comment-only NatSpec correction. A forced
warning-clean build and the focused suite pass **11/11**. An independent rerun catches all
**49/49 warning-clean production mutants** plus the one oracle control, reproduces the known
92-test survivor and the new-test kill, and reproduces the mined Anvil receipt matrix byte for
byte. Both the ordinary fast gate and the required isolated exact-commit deep gate end in
`GATE PASSED`; the deep output directly shows the new event suite executing.

This reviewer authored neither the B-EVENTS instrument nor the implementation. **HOLD means only
that this exact candidate satisfies the frozen, bounded B-EVENTS contract.** It is not product
approval, a gate signature or reopening, certification, ratification, publication, rename or
push authority, a D-055 assessment, or a ruling on any held D-008 question.

---

## 0. Identity, authority and frozen inputs

| Item | Identity |
|---|---|
| Branch | `step-3/isolated-signer` |
| A-090 parent/checkpoint | `11b2566e6d1bffe1262007ddca914aefc02a3abf` |
| Exact candidate | `ff048508d9d3056bf5635233ab0df5e79ecb45d4` |
| Instrument subject | `3d8e8dd1f2d9e71df8be60983e842277a9bacb36` |
| Independent instrument review | `f30cfbdb0957c767c5b48022d81c95b6c9a72df5` — HOLD |
| `TESTS.patch` sha256 | `b057d64f0b01d4a4de2cb8e2ac30ba4e16d60ffc0cfcf02544b4260be893c931` |
| Extracted test source sha256 | `2a9219cc5138858b012b0bc56069490db3dd7d1963b73ccc19c28a48ce2b029e` |
| `NATSPEC.patch` sha256 | `a5937bcbba3e8cd060a320a92f1251c5a6ae8e3cd5098a2a5a8370276a59c29c` |
| Mutation driver sha256 | `f6816b1e94d06612d14809919333038dc41c4f56920c398c431ad6429cecb1a6` |
| Frozen matrix sha256 | `92769e5dca0c84d15db71abba01bdbe4ff2e49f81180bfe034514246882a4ddd` |
| Repository state at start | clean; `HEAD` was the exact candidate |
| Repository writes before this record | none |

I read the workspace rules; D-058, D-059, D-060, D-066 and A-090; every file under the frozen
B-EVENTS test directory, including `INSTRUMENT-REVIEW-1.md`; the complete candidate diff; the
vault, independent event test, current Solidity tests, Foundry configuration and top-level gate.
I verified only the declared file/symbol/route boundary, not repository-wide event completeness.

## 1. Exact two-surface implementation and patch fidelity

The complete A-090-to-candidate diff is:

| Surface | Change | Classification |
|---|---:|---|
| `contracts/test/SentinelVault.events.t.sol` | +343 / −0 | exact frozen independent test |
| `contracts/src/SentinelVault.sol` | +6 / −3 | exact frozen NatSpec replacement |

No third path changes. I replayed `TESTS.patch` and `NATSPEC.patch` onto a detached A-090 clone,
then compared both resulting files byte for byte with the candidate. Both comparisons pass.
`git diff --check` passes.

The test patch is not weakened or edited: its candidate source hash is the frozen
`2a9219cc…b029e`. The NatSpec replacement appears exactly once, the false paragraph appears zero
times, and the patch changes comment lines only. The 21 entries in `CHECKSUMS.sha256` all verify;
the frozen test contract, instruments, logs and matrix are unchanged. From the instrument subject
to the candidate, the only file added under the B-EVENTS evidence directory is the standalone
first instrument review.

### 1.1 No executable vault change

The source diff contains no event declaration, emit, route, state transition or executable line.
I also compiled the pre-NatSpec and candidate source independently and stripped Solidity's
source-dependent metadata trailer from each deployed bytecode object. Both executable bodies are
**6,278 bytes** and have sha256
`5aec4ef7842bfede4fe64a18e70c6798abf9c7a88163d8e2205558e067123ba9`. The complete bytecode
objects differ only inside their 53-byte source-dependent metadata trailers.

## 2. Event ABI, routes, fields, order and emitter

Independent source enumeration finds exactly **eight event declarations and eight emit sites**.
The compiled ABI confirms these exact fields and indexed/data locations:

| Event | Fields | Route |
|---|---|---|
| `MandateActivated` | indexed `mandateHash` | `activateMandate` |
| `MandateRevoked` | indexed previous `mandateHash` | `revokeMandate` |
| `PolicyActivated` | indexed `policyHash` | `activatePolicy` |
| `SignerRotated` | indexed `previousSigner`, indexed `newSigner` | `rotateSigner` |
| `PausedSet` | data `paused` | `setPaused`, both booleans |
| `Recovered` | indexed `to`, data `amount` | `recover` |
| `OverrideAuthorized` | indexed `actionHash`, indexed `overrideHash`; data `reviewReceiptHash`, `reasonHash`, `expiresAt` | successful retained override route |
| `ActionExecuted` | indexed `actionHash`, indexed bound `actionNonce`; data `decisionId`, `viaOverride` | shared `_consumeAndCall` |

The automatic call site passes `false`. The override route emits `OverrideAuthorized` after all
authentication checks, then calls `_consumeAndCall(..., true)`. `_consumeAndCall` increments the
nonce, emits `ActionExecuted`, performs the target call and reverts the frame when that call
fails. No ninth vault event, alternate execution route or alternate emit site exists inside the
declared boundary.

The test's expected event declarations are independent of the production ABI. Every
`expectEmit` names `address(vault)`, and each successful route performs a vault-emitter/topic
census. Thus each owner control permits exactly its one event; automatic execution permits only
`ActionExecuted(..., false)`; and override execution requires exactly `OverrideAuthorized` then
`ActionExecuted(..., true)`. Target and relay events are correctly excluded from the vault-only
census.

## 3. Focused suite and exact NatSpec probe

I ran:

```sh
forge fmt --check test/SentinelVault.events.t.sol
forge build --force
forge test --match-path test/SentinelVault.events.t.sol -vv
```

Solc 0.8.28 compiled 36 files successfully with no warning. Result: **11 passed, 0 failed, 0
skipped**. The eleven comprise eight success/event tests, two rollback tests and the explicitly
named Foundry recorder LIMIT calibration.

The exact frozen NatSpec probe gives:

| Source | false paragraph | truthful replacement | Exit |
|---|---:|---:|---:|
| A-090 baseline | 1 | 0 | 1 |
| candidate | 0 | 1 | 0 |

The replacement accurately says that a durable `OverrideAuthorized` log requires downstream
success and commitment of every enclosing frame; it does not promise machinery to retain logs
through a revert.

## 4. Complete immutable mutation matrix

I reran `mutate.py` from the frozen bytes in an isolated detached candidate clone. Before each
row, the vault and event test were restored to exact candidate bytes. Every mutant was built
under the warning-denying Foundry configuration before the focused test was scored.

```text
PRODUCTION  build PASS  behavior CAUGHT  49
CONTROL     build PASS  behavior CAUGHT   1
PRODUCTION  build FAIL                    0
PRODUCTION  SURVIVED                      0
build output containing "warning"        0
```

The generated 51-line matrix has unique IDs, sha256 `92769e5d…a4ddd`, and is byte-identical to
the frozen `mutation-matrix.tsv`. The production rows comprise all 8 event omissions, all 18
meaningful field substitutions, both call-site routes, all 17 legal indexed/data moves, the
wrong-topic substitution and all 3 extra-event substitutions. The wrong-emitter oracle control
is caught separately and is not counted as a production mutant.

I inspected representative raw witnesses from every class. Among them, forced `false` fails only
the override-route event test; forced `true` fails only the automatic-route event test; each
call-site substitution fails its corresponding named route; an action-nonce layout move fails
both execution tests; extra override emission fails the exact order/membership census; the
mandate-to-policy topic substitution names the mandate test; and the wrong-emitter control names
the same test. No behavioral catch is credited to compilation, warnings or generic harness
failure.

## 5. Known old-suite survivor and marginal new-test kill

In isolated scratch I removed only the new event test, applied the exact warning-clean
`field_action_via_false` mutant, forced a build and ran the full pre-existing Solidity suite.
Result: **92 passed, 0 failed** — the mutant survives.

With the exact frozen event test restored against that mutant, the event suite gives **10 passed,
1 failed**. The sole failure is
`test_OverrideAndActionExecuted_exactFieldsTrueRouteOrderAndVaultEmitter`; the automatic-path
control remains green. The full 49+1 rerun independently produces the same named kill. This
establishes the new test's marginal observation rather than crediting an existing assertion.

## 6. Mined receipts versus the Foundry recorder LIMIT

I copied the frozen live probe into the detached candidate clone, rebuilt it and ran it against
Anvil. Its output is byte-identical to the preserved `logs/live-receipt.log`:

| Route | Receipt | Durable logs | Vault nonce |
|---|---|---|---:|
| direct override success | success | `OverrideAuthorized`, `ActionExecuted`, `Purchased` | 1 |
| direct downstream failure | reverted | none | 0 |
| relay swallows inner failure | success | `Attempted(false)` only; no vault event | 0 |
| relayed success | success | `OverrideAuthorized`, `ActionExecuted`, `Purchased`, `Attempted(true)` | 1 |
| successful inner vault call, ancestor reverts | reverted | none | 0 |

These are mined transaction receipts. Separately, the focused Foundry LIMIT test passes while
asserting that `vm.recordLogs` retains one reverted-frame `OverrideAuthorized` artifact beside a
zero vault nonce. That cheatcode artifact is calibration evidence about the recorder and is not
treated as a durable receipt log.

## 7. Fast gate and required isolated deep gate

I ran the unchanged fast profile in the detached exact-candidate clone:

```sh
./scripts/test.sh
```

Result: **`GATE PASSED`**. The output directly names
`test/SentinelVault.events.t.sol:SentinelVaultEventsTest` and all eleven event tests, then reports
Foundry **103/103**, TypeScript **527/527**, verifier suite **221**, samples **7**, and tamper **78
cases / 30 modes**. As documented, the fast profile does not execute the corpus or verify
committed views.

For the required deep run I used an isolated no-hardlink clone detached at the exact candidate,
with dependency working trees locally staged at the pinned commits:

- `forge-std` `bf647bd6046f2f7da30d0c2bf435e5c76a780c1b`;
- OpenZeppelin Contracts `5fd1781b1454fd1ef8e722282f86f9293cacf256`;
- the installed JavaScript dependency tree copied into the clone.

The clone was clean immediately before the run. I ran, alone:

```sh
./scripts/test.sh --gate
```

Result: **`GATE PASSED`**. The preserved output directly shows the new event test contract and all
eleven named event tests executing successfully inside Foundry **103/103**. It also reports the
gate-profile stateful campaign at 2,048 runs, TypeScript **527/527**, corpus **50 fixtures**,
committed views verified file by file, **51 result files identical**, verifier suite **221**,
samples **7**, and tamper **78 cases / 30 modes**. The clone remained clean after completion.

### 7.1 The 92-versus-103 floor is a limit, not closure

Both real gate outputs say:

```text
foundry: 103 tests (floor 92)
```

The event suite executes and the frozen mutation evidence binds its behavior, but the canonical
Foundry floor does not independently pin the new file against deletion. Under D-059(5), floor
ownership remains Batch A's. This B-EVENTS HOLD records the discrepancy and does **not** claim to
close, repair or reassign it.

## 8. Repository, protected-boundary and workspace checks

All outputs were read, not inferred from exit status:

- `check-secrets.sh`, default and staged: clean;
- `check-review-scope.sh`: 568/568 files before this record; after staging it, 569/569 assigned
  (`R1=371`, `R2=46`, `R3=152`);
- `check-findings-ledger.sh`: all D-057 ruled totals match;
- `check-suite-floors.sh`: the sole `scripts/test.sh` copy reports 92 / 527 / 221 / 7 / 78 / 30;
- `check-vendor-honesty.sh`: mechanical conditions pass; this review answers no held question;
- `check-rename-gate.sh`: private and clean;
- workspace `tools/guards/run_guards.sh Sentinel`: PASS with **13 baselined findings, 0 new**;
- candidate and protected diffs: `git diff --check` passes; repository clean.

The workspace guard is a ratchet. Its green result does not clear the 13 baselined findings.

Protected candidate hashes include:

| Surface | sha256 |
|---|---|
| `Sentinel_Protocol_Lab_Proposal_v0_2.md` | `322cd96fa7daf9840c34f6bf6cc0abd9b1d31a83ccfd5e9babb0f575e20c4124` |
| `docs/gate-s1-evidence.md` | `25dcefcade99e9e45be0c482f3dc5141f4d25335a920fabe1012303c7d7caf68` |
| `docs/gate-s2-evidence.md` | `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589` |
| `scripts/test.sh` | `66c272b90a16b037e3fcfc6f0d9184c48f63ac32e62538be7b6cd96a93801b79` |

The A-090-to-candidate diff is empty across every existing test, script, TypeScript/verifier
surface, fixture, hook, proposal and signed gate record. No signed or certified boundary, gate
runner or suite floor moved.

## 9. Exclusions, setup disclosures and remaining uncertainty

- Completeness is confined to the exact vault file, eight declarations, eight emit sites and
  named routes. It is not a repository-wide or indexer-wide event claim.
- The new suite does not re-prove authentication, hashing, reentrancy, time windows, allowlists,
  caps or replay safety. Existing suites remain the evidence for those domains.
- Anvil receipts do not cover reorgs, archive retention, third-party indexers or mainnet-client
  diversity.
- The success fixtures use one nonzero value for most fields; pause and `viaOverride` drive both
  booleans. Mutation discrimination, not input fuzzing, is the card's purpose.
- Foundry's reverted-frame recorder output remains explicitly inadmissible as durable evidence.
- The canonical Foundry floor is 92 while 103 tests execute. This is the Batch A-owned limit in
  §7.1, not a hidden B-EVENTS success claim.
- One initial ABI query emitted Forge's human-readable table into `jq`; parsing refused before
  producing a result. The corrected read-only query used `forge inspect ... --json` and is the
  ABI evidence above.
- One combined old-suite/new-suite scratch command yielded control while its second arm was still
  compiling. That partial arm was not scored, and a subsequent clean-source 11/11 run is also
  excluded. The completed 92/92 old-suite arm and the independent full matrix's exact
  `field_action_via_false` raw output supply the scored survivor and 10/11 kill evidence.

Within those stated bounds, I found no contract failure, warning catch, survivor, scope escape,
protected-boundary movement or unmeasured required deep invocation. **The exact verdict for
`ff048508d9d3056bf5635233ab0df5e79ecb45d4` is HOLD.**
