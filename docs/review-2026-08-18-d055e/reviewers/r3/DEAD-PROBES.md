# DEAD-PROBES — Reviewer 3

**Every probe that measured nothing, whether or not it looked like a pass.** A probe that did
not compile, matched no lines, errored before reaching the code under test, or mutated a value
already at its limit, is listed here even when it "passed".

## Mechanical guards I built in before running anything

The vault mutation harness (`scratchpad/probes/mutate.sh`) refuses to report a result unless the
probe demonstrably moved something. It exits `9` with a `DEAD-PROBE` label, never a pass, when:

| Guard | Detects |
|---|---|
| exact-occurrence count `!= 1` before substitution | an anchor that has rotted or is ambiguous (round five's `mutate.sh` batch C failure mode) |
| `cmp` of source against the pristine copy after substitution | a substitution that changed no bytes |
| `forge build` non-zero | a mutant that does not compile — never counted as caught, because that credits the compiler for the suite's work |
| bytecode-prefix comparison before/after | a mutation the optimiser erased |

Every one of the 35 vault mutations passed all four guards. **`0` dead probes in the vault sweep.**
`mutations/log.txt` carries the per-mutation line; no line reads `DEAD-PROBE`.

## Dead probes I actually hit

### DP-1 — `upper()` on an all-digit address (avoided, not hit — recorded because it is the
trap the project itself documents)
`ts/test/evaluate.checks.test.ts:440-448` records a prior instance: upper-casing `0x2222…` is a
no-op, so a case-normalisation probe built on it changes nothing while looking like it does.
Before writing any case probe I re-used that file's `LETTERY` constant
(`0xabcdefabcdefabcdefabcdefabcdefabcdefabcd`) and asserted `upper(x) !== x` first. **No probe of
mine ran against an all-digit address.**

### DP-2 — concurrent `npm test` during the Foundry sweep (HAZARD IDENTIFIED, PROBE NOT RUN)
Six TypeScript test files read `contracts/out` (`decode.chain`, `cases.e2e`, `differential`,
`harness`, `simulate`, `propose.e2e`). Running `npm test` while the vault mutation sweep held a
MUTATED `SentinelVault.json` in `contracts/out` would have measured the TypeScript suite against
a mutant vault and produced results attributable to neither. **I serialised instead of
parallelising and did not run that probe.** This is recorded because "the run was green" would
have looked identical.

### DP-3 — no probe of mine mutated a value already at its limit
The four boundary mutations (`MB1`–`MB4`) widen a comparison by exactly one
(`x > cap` → `x > cap + 1`), and the three timestamp ones widen to `uint256` first so a
`type(uint64).max` fixture cannot silently panic instead of executing the widened branch. Each
was checked for a compile and a bytecode move before its result was believed.

## Probes that returned nothing because the thing was not there

### DP-4 — search for an assertion tying `WITHHELD` to `MANDATE_CONFORMANCE_CODES`
```
grep -rn 'WITHHELD' ts/ scripts/ docs/ --exclude-dir=node_modules
```
matched **only the three lines in `report.ts` that declare and use it**. Zero hits in `ts/test/`.
This is a null match that IS the evidence for R3-F2, not a probe that failed to fire — recorded
here so the distinction is on the record.

---

## Dead probes the harness caught DURING the run

### DP-5 — `M21-receiptSigRecover` — **DEAD PROBE, build-failed, NOT a pass**
```
M21-receiptSigRecover DEAD-PROBE build-failed
```
Commenting out `if (digest.recover(receiptSig) != signer) revert WrongSigner();` leaves
`bytes32 digest` unused, and `contracts/foundry.toml` sets `deny = "warnings"`, so solc fails
the build. **Counting that as "caught" would credit the compiler for the suite's work** — the
exact inflation `scripts/mutate.sh`'s own header warns about. The harness reports it as an
error, and it is re-run in the follow-up batch with a mutation that keeps `digest` live
(`!= signer` → `== address(0)`), so the check is genuinely measured rather than skipped.
See the follow-up rows in `mutations/log.txt` / `mutations/log2.txt`.

### DP-6 — my own bytecode guard is a PREFIX comparison and produced a false alarm
```
M23-reviewVerdict WARN bytecode-prefix-unchanged
```
My guard compares the first 80 hex characters of `SentinelVault.json`'s `bytecode.object`,
which is constructor prologue and does not move for a small body edit. **This is a defect in my
instrument, not in the probe.** It is emitted as `WARN`, never as a result, and the load-bearing
guard is the `cmp` of the source against the pristine copy plus a successful build — both of
which passed for M23. Recorded because a guard that reports a false negative is exactly the
thing this file exists to surface, and because the next reviewer should compare full runtime
bytecode, not a prefix.

### DP-7 — `M24-ovrReceiptHash` and `M30-ownerSig` — **DEAD PROBES, build-failed, re-run**
Same cause as DP-5: commenting the statement out orphans `receiptHash` / `digest`, and
`deny = "warnings"` fails the build. Re-run as `M24b` (`receiptHash == bytes32(uint256(1)) || …`,
keeping `receiptHash` live) and `M30b` (`digest.recover(ownerSig) == address(0)`). Both KILLED —
so those two checks ARE genuinely covered, and neither was silently skipped.

### DP-8 — `MEV2-mandateRevokedArg` — **DEAD PROBE, build-failed, re-run**
`emit MandateRevoked(previous);` → `emit MandateRevoked(activeMandateHash);` orphans `previous`.
Re-run as `MEV2b` with `previous & bytes32(0)`, which keeps the variable live and emits the same
zero value. **`MEV2b` SURVIVED 75/75** — so the dead probe was concealing a real survivor, which
is precisely why a build failure must never be scored as a catch.

## Final tally of dead probes

| batch | attempted | dead probes | re-run | still dead |
|---|---|---|---|---|
| vault (Foundry) | 53 | 4 (`M21`, `M24`, `M30`, `MEV2`) | 4 (`M21b`, `M24b`, `M30b`, `MEV2b`) | **0** |
| TypeScript | 12 | 0 | — | **0** |
| pure/out-of-tree probes (leakage, ablation prose, `WITHHELD`) | 15 | 0 | — | **0** |

**All four dead probes were caught by the harness's build-must-succeed guard, reported as
`DEAD-PROBE build-failed`, and re-run. One of the four (`MEV2`) was concealing a survivor.**
