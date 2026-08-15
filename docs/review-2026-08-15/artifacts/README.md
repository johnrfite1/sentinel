# Review artifacts — 2026-08-15, commit `9059346`

Reproduction rigs and campaign data from the four independent adversarial reviews recorded as
**A-028**. Preserved here because the reviewers worked in session-scoped scratch that would
otherwise have been lost, and D-017 requires findings be attributable and reproducible rather
than taken on the reviewer's word.

**These are EVIDENCE, not part of the build.** Nothing here is wired into `scripts/test.sh`,
and `OrderingProbe.t.sol` deliberately sits outside `contracts/test/` so Foundry does not
compile it — applying it is a remediation decision that has not been taken.

| File | What it demonstrates |
|---|---|
| `attack.ts` | **F1** end to end: a two-field lie in the evidence bundle switches the D-014 attestation off, an ALLOW is signed for a wrong-resource purchase, and the wrong entitlement lands onchain. Run against a real Anvil, vault, and signer process. |
| `OrderingProbe.t.sol` | **F2**: a regression test for §3.3(9)'s "nonce consumed before the external call". Passes on `9059346`, fails under the S7 mutation that moves the increment after the call. Verified by its author. |
| `probe.mjs` | The **A-005** isolation probe — 26 method names, raw `__proto__` on the wire, an oversized line, and socket/directory permission checks. All refused; this is the rig behind the strongest thing the review confirmed. |
| `collide2.mjs` | The 4-byte selector collision search behind step 7's F1 (`fUXSEz2ajwh(bytes32)` → `0xc188528b`). |
| `mutate.py`, `sol_mutants.json`, `ts_mutants.json` | The 45-mutation campaign: 20 Solidity, 25 TypeScript, 29 survivors, 9 of 9 controls caught. |

Absolute paths in the original scripts were rewritten to repo-relative form to satisfy the
secret guard (house rule 6). **The guard was not weakened** — that rule exists precisely so a
convenience path does not become a committed dependency on one machine.
