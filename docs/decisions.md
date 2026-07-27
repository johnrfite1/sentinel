# Sentinel — Decision Log

Canonical record of decisions for the Sentinel build. Agents propose; John decides. Ratified entries are attributed to John. Agent-made calls are logged separately as flagged assumptions and are cheap to reverse. New forks get new entries; history is never rewritten.

## Ratified (John)

- **D-001 (2026-07-27) — Section 14 ladder.** v1 adopts 14.5 (mandate-fidelity limit promoted into §8; applied) and 14.4 (vendor baselines documentation-only; executed/emulated vendor comparisons cut from v1). Rung 1: 14.2 receipt-verifier CLI (+10–20h), a stated goal that must ship before the portfolio artifact is called done. Rung 2 (post-MVP, discovery track): executed vendor comparisons where free test access exists. 14.3 attestation: stretch, considered only after the §7.5 gates are green; its claims-boundary wording (conformance is against simulated effects at a recorded block) applied to §8 now.
- **D-002 (2026-07-27) — Gate cadence.** Two mid-build facilitated sign-offs. Gate S1: vault + isolated signer + exact-action binding + Case 1 end-to-end + replay/tamper invariants green. Gate S2: full fixture corpus + §7.5 hard-gate evidence. Gates are signed only by John.
- **D-003 (2026-07-27) — Kill criteria, no token cap.** The §12 stop condition on scope expansion; a no-progress halt after 3 failed independent attempts at a gate; immediate halt if any agent modifies fixtures, ground-truth labels, or gate definitions to make a suite pass.
- **D-004 (2026-07-27) — Dispatch.** Opus 5 architects and directs subagents; John launches the build and holds all gate and veto authority. Build authorized through Gate S2.

## Agent assumptions (flagged, cheap to reverse)

- **A-001 (2026-07-27) — Proposal home.** This repository (John moved the proposal from the vault on 2026-07-27). A vault pointer note is at John's discretion.
- **A-002 (2026-07-27) — Base Sepolia deferred** until the local Anvil suite is green (§4 marks the deployment optional).
- **A-003 (2026-07-27) — Anthropic API, current models,** for the untrusted agent under test and mandate drafting. Low stakes: the agent is untrusted by design.
- **A-004 (2026-07-27) — Repository local and private** until the §0 rename gate and John's publication decision.
