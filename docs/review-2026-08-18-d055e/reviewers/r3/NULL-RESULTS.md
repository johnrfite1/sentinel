# NULL-RESULTS — Reviewer 3

What I probed and found SOUND. Recorded so the next round knows where not to look again.

## N-1 — `docs/ablation-report.md` regenerates BYTE-IDENTICALLY from the committed inputs

`G-2` (round five, MEDIUM, "the report is not the output of its own generator — the latency
column is arithmetically impossible from the committed results") **is fixed and stays fixed.**

```bash
node <scratchpad>/probes/regen-ablation.ts /tmp/regen.md    # calls loadInputs()+buildReport()
diff docs/ablation-report.md /tmp/regen.md                  # -> no output
```
Zero-byte diff. The committed report is exactly what `buildReport(loadInputs())` produces on the
committed `fixtures/corpus/results/` and `labels/labeller-{E,F}.json`. Every column — verdicts,
false-allow counts, contribution, latency percentiles, class table — re-derives.

## N-2 — the G-5 repair's DERIVED sentences are correct today, on real data

The two sets A-076 made derivable are right on the committed corpus:

| Derived from | Value in the committed report | Independently recomputed |
|---|---|---|
| `results.length` | 50 fixtures | 50 result files, 50 `_index.json` entries |
| `class === "unexpected-internal-call"` | `F051` is INERT | exactly `F051` |
| `primaryEnforcement !== "conformance-engine"` | `F028, F029, F035, F054, F055, F056` | identical six; `F057` is `conformance-engine` and correctly absent |

**`F057` is no longer wrongly named**, which was the substance of the G-5 repair. Confirmed.

## N-3 — the hardcoded prose claims I could check against data are TRUE

`evidence/r3/data/ablation-prose-claims.txt`.

| Hardcoded claim in `report.ts` | Measured |
|---|---|
| "`EVAL_CALL_GRAPH_EXPECTED` is never non-PASS anywhere in the corpus" | **holds** — 0 non-PASS occurrences across 50 fixtures × 3 layers |
| "two demo contracts and two call schemas" | **holds** — `DemoPay.purchase`, `DemoERC20.approve` (plus undecodable, which is not a schema) |
| "exactly as it blocks `F009` and `F012`" (analogues of F049/F050) | **holds** — F049 and F009 share an identical L3 failing set; F050 and F012 both fail on `EVAL_PURCHASE_RESOURCE` alone |
| "the sample … contained no conforming fixture and no fixture whose primary defect is an evidence gap" | **holds** — all 10 sampled fixtures are labelled BLOCK by E; **0** carry an ALLOW label; **0** have UNRESOLVED as their only non-PASS outcome |
| "with n=10 the only attainable rates are multiples of 10%" | **holds** for the committed sample (n=10 exactly); the multiple is DERIVED, only the "10.0%" instance is a literal |

The inter-labeller figure re-derives: `|E ∩ F| = 10`, `0` disagreements, `0.0%`.

## N-4 — the vault's two LIMIT tests are honest, and both carry their controls

* `test_LIMIT_vaultCapsNativeValueOnlyAndNotTokenAuthority` — asserts a limit (unlimited
  allowance granted through one valid receipt) and pins it with the nonce assertion.
* `test_LIMIT_nativeCeilingIsPerActionAndBoundsNoAggregate` — **has the control the pattern
  requires**: one action at `cap + 1` must still revert `ValueOverCap` before the 100-action
  drain runs, so the drain is measured against a LIVE ceiling and not an absent one. The
  `vm.warp` is genuinely gone and `block.number` / `block.timestamp` are asserted UNCHANGED
  across all 100 executions, which is the D-053(a) correction actually implemented rather than
  described.
* Both carry a "if this ever fails, update §7.1 — do not delete the test" instruction, which is
  the right shape for a limit test.

**I found no way in which the ATOMIC-DRAIN boundary is understated.** The §7.1 row, the NatSpec
header (`SentinelVault.sol:12-37`) and the test agree with each other and with the code, and the
row has been retreated to the position the code actually supports ("per-action authority is
bounded; cumulative authority is not bounded at all"). Probed for overstatement in the
containment direction and found none.

## N-5 — the corpus class-coverage guard's OWN self-checks fire

I read the seven self-guards in `check-class-coverage.sh` (baseline status enum, baseline key
must exist in the map, map codes must exist in the engine, missing/extra/duplicate result files,
class disagreement between the two directories) and confirmed each is reachable code with a
`fail = 1`. The guard's stated limits are stated honestly, including the one mutation it admits
survived (re-pointing `altered-calldata-after-receipt` at a check F018 already fails).
**The defect I found is not in the guard — it is in the DOCUMENT that reports what the guard
measures.** See R3-F1.

## N-6 — the leak denylist still works at depth

`assertNoLeakage`'s key walk fires on a forbidden substring at any depth, including inside an
array member two levels down (probe P4: `observedEnvironment.entitlements[0].engineFailingCodes`
→ `LeakageError`). The A-028 F-3 substring/quoting defects are genuinely closed. The residual
gap (R3-F3) is the ALLOWLIST's reach, not the denylist's.

## N-7 — the invariant campaign's marginal contribution is ZERO, measured independently on a sweep 2.8× wider than the one it was certified on

`A-073` measured it and `D-054(b)` certified it. My brief lists it as an accepted boundary I may
report only if UNDERSTATED. **It is not understated. I reproduce it, and I extend the basis.**

`F-VAULT-3` (round five) swept **twelve** vault checks and found all twelve unreachable by the
campaign. I swept **41 mutations** (34 in the first pass + 7 follow-ups; 3 dead probes re-run in
a variable-preserving shape), each against the 11-invariant campaign alone
(`forge test --match-test '^invariant_'`) and against the full suite.

| | count |
|---|---|
| mutations measured | 41 |
| dead probes (build-failed, re-run) | 3 |
| killed by the campaign | 8 |
| survived the campaign | 33 |
| **of the 8 the campaign killed, also killed by the deterministic tests alone** | **8 of 8** |

The marginal run is `forge test --no-match-test '^invariant_'` — the whole suite with **only**
the eleven invariant functions excluded, so `invariants.t.sol`'s own deterministic tests
(reentrancy, non-vacuity, selector registration) still run. Every one came back KILLED:

```
M01-paused          deterministic-only=KILLED
M04-nonce           deterministic-only=KILLED
M11-datahash        deterministic-only=KILLED
M22-allowVerdict    deterministic-only=KILLED
M23-reviewVerdict   deterministic-only=KILLED
M25-ovrActionHash   deterministic-only=KILLED
M21b-receiptSigRecover / M30b-ownerSig — see mutations/marginal.txt
```

**Marginal contribution of the stateful campaign over 41 mutations: 0.** The recorded position
is correct and my sweep is a wider basis for it than the one it was certified on.

**One refinement worth recording, because the recorded wording is narrower than the behaviour.**
F-VAULT-3's claim is that the campaign *"cannot construct a violation of ANY of the vault's
twelve action- and receipt-validation checks"* — true of those twelve. It is NOT true that the
campaign kills nothing: it killed 8 of my 41. The precise statement is **"the campaign kills a
strict subset of what the deterministic tests kill"**, which is a stronger and more durable claim
than "it cannot reach these twelve", because it does not depend on which checks were swept.

## N-8 — the D-043 override log IS properly asserted

Three mutations against `emit OverrideAuthorized(...)` — deleting it, zeroing `reasonHash`, and
inverting `viaOverride` on `ActionExecuted` — were all KILLED by the full suite
(`M35`, `M36`, `M37`). The §3.3(2) "logged" repair A-043 made is real and tested. (The other
five vault events are not — see R3-F7.)

## N-9 — `ts/src/corpus/rationale.ts` is sound and states its own limits accurately

The containment guard derives its probes FROM each fixture's own rationale (so adding a fixture
extends the guard), pairs adjacent words BEFORE filtering (so a probe that cannot fire cannot be
constructed), asserts that invariant in code (`assertProbesLive`), and enforces a floor on LIVE
probes rather than on probes (`MIN_BIGRAMS`, after a constructed rationale reached six dead
probes and passed a verbatim leak). It names its own uncloseable hole in the file — a
`rationaleHash` shares no bytes with its preimage, so no scan can find it — and claims absence
of THESE FORMS rather than absence of the rationale. **I found nothing to add and nothing
overstated.**
