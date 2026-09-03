# Quench — second handoff to the orchestrator: assumptions 2, 3 and 8

**From the Smith.** Session `S-20260830-sentinel-conformance-lab-r1`, Step 6, in reply to the orchestrator's
walk of the remaining Untested assumptions (after MSG-042). The Quench artifact is unchanged:
`8dfaa275a669bd202c3fa45e36dc12cbbe261170` (A-033). Verbatim from `docs/decisions.md`.

## The Smith Decision to file (D-094)

- **D-094 (2026-09-03) — THE REMAINING UNTESTED ASSUMPTIONS: 2 IS AMENDED TO MATCH THE ARCHITECTURE AND MOVES TO PLAUSIBLE WITH STATED RISK; 3 AND 8 ARE ACCEPTED WITH STATED RISK. Ruled by John, 2026-09-03, in reply to the orchestrator's Quench walk (MSG-042 onward), in a facilitated walkthrough with the agent's recommendations stated and taken. The agent RECORDS these and makes none of them.**

**(a) ASSUMPTION 2 — AMENDED; STATUS PLAUSIBLE, WITH STATED RISK.** The register's text — *"The offline verifier and SentinelVault answer the same question, so a verifier PASS means the Vault would execute"* — is measured false by design, because the artifact separates authenticity, offline executability and live execution (D-087(c)). It is amended to: **"A PASS from `verify_publication.py` means SentinelVault's offline-checkable action predicate accepts the bundle at the named entry point; `verify.py` certifies authenticity only and never exits 0 for an offline-checkable case the Vault refuses; live execution additionally depends on state neither verifier reads — nonce, pause, and the mandate's and policy's state at the block."** Status: **Plausible, not Verified.** Evidence: the 39-cell override parity matrix (`docs/check-inventory-diff-2026-08-31.md`), three cycles of chair reproduction, the D-090(a)/D-091(a)/D-092(c) exit contract. **Stated risk:** "No shared conformance corpus has been run through all three implementations, so parity rests on the matrix and the chairs' spot checks; unification into one versioned predicate remains deferred (D-087(c))." **Rejected — waive as written** (leaves a false sentence in the register for the audience to read as a claim); **hold for unification** (the Quench cannot complete on this artifact).

**(b) ASSUMPTION 3 — ACCEPTED WITH STATED RISK.** *A public repository for evaluators is not deployed where value is at risk.* Not Existential. **Stated risk:** "Documented, not enforced. Risk: someone deploys the contracts with real value despite the README. Mitigant: no mainnet configuration ships, the demo runs on a local Anvil only, the per-action ceiling and the disclosed drain and token-authority limits are stated on the first surface, and the repository is held private with the licence deferred." **Rejected — waive without a mitigant; hold for a chain-id guard** (a mechanism change, not a narrow patch).

**(c) ASSUMPTION 8 — ACCEPTED WITH STATED RISK.** *v0.2 corpus and v0.3 semantics can coexist without misrepresenting either.* Not Existential. **Stated risk:** "The v0.2 packet is a frozen historical artifact (D-080) and its verifier predates the exit contract. Risk: a recipient handed the packet directory alone runs its `verify.py` on a BLOCK bundle and reads PASS. Mitigant: the packet README's dated note precedes its commands (D-092(b)), the root README describes the packet in prose only (D-092(a)), and the release tree ships no `verify.py` at all." **Rejected — waive; regenerate the packet first** (reverses D-092(b) and makes the packet no longer the artifact Gate 8 reviewed).

**WHAT THIS ENTRY DOES NOT DO.** With D-093 it disposes of every Untested assumption in the register; it does not answer the Quench's other checklist items, which the Smith answers directly to the orchestrator. It authorises no publication, deployment, push or visibility change; the repository remains PRIVATE; **the licence remains DEFERRED under D-082(c).**

## Register effect requested

- Assumption 2: text replaced by the amended statement above; `Untested — MEASURED FALSE / Existential` →
  `Plausible with stated risk (D-094(a)) / Existential`.
- Assumption 3: `Untested` → `Accepted with stated risk (D-094(b))`.
- Assumption 8: `Untested` → `Accepted with stated risk (D-094(c))`.
- No other Status or Existential changes. With D-093, no assumption remains `Untested`.

## Not decided here

The remaining Quench checklist items (acceptance criteria met or waived — note AC2 is not met and needs a
conscious waiver; no unresolved Criticals; a surviving pre-mortem; the one-line decision note) and the Temper
trigger are answered by the Smith directly. Publication, deployment, push, visibility and licence are separate
rulings and are not taken; the repository remains PRIVATE and the licence DEFERRED (D-082(c)).
