# Sentinel

Sentinel is a testnet lab that binds one exact EVM call to a human-signed mandate:

- an untrusted agent proposes a call;
- an evaluator compares the decoded call and its simulated effects at a recorded block to the
  mandate;
- an isolated signer attests the verdict in a signed receipt; and
- `SentinelVault` executes the exact attested bytes on an ALLOW receipt, executes a REVIEW
  receipt only alongside a separate owner-signed override, and reverts a BLOCK receipt at both
  entry points, altered calldata, and a replayed nonce.

What that establishes is narrow, and the tools say so themselves. The release's offline verifier
certifies only that the Vault's offline-checkable predicate accepts a bundle, and prints a
`NOT ESTABLISHED` line beside every certifying result:

- no chain is read, so deployed code identity and nonce freshness are not established;
- the clock is unauthenticated;
- the calldata arguments are never decoded by the verifier or the Vault, only by the signer's
  evaluator; and
- the Vault's native-value ceiling is per action, bounding neither aggregate loss nor token
  allowances, which no contract here caps.

Sentinel is not a detector, not a production wallet, and not a deployment: the fixtures and the
cold demo run on a local Anvil, and testnet-only is documented rather than enforced.

Status at this revision (2026-09-04): public, published under D-099 as a demonstration of the
author's engineering work; Quenched on `8dfaa27` (D-096, 2026-09-03) after the Crucible's lab
casting returned no unresolved Criticals; licensed Apache-2.0 (D-097, 2026-09-04). `docs/session-state.md` is the live status and wins over
anything written here.

Where the record lives:

- the mechanism in `contracts/` and `verifier/`;
- the limitations in the verifier's own `NOT ESTABLISHED` output, `release/README.md` and
  `docs/enforcement-release-v0.3.md`;
- the status in `docs/session-state.md`; and
- the archive — every ruling, register and review arc, kept because the history is part of what
  is evaluated — in `docs/decisions.md`, `docs/a018-remediation-register.md`,
  `docs/v1-1-register.md` and the `docs/review-*/` directories.

The map of that record, written for a reader who did not live through it, is `docs/ARCHIVE-INDEX.md`.

This project is distinct from Uppsala Security's Sentinel Protocol and from sentinel.co's Cosmos network. The names collide; there is no affiliation. It is said here so the collision is disclosed, not as a legal conclusion.

> The agent proposes. Sentinel evaluates. The isolated signer attests. SentinelVault enforces.

It does not infer danger from bytecode, from a story an agent told, or from how a call “looks.” It checks whether one exact EVM call matches a human-signed mandate, against simulated effects at a recorded block, and it permits execution only of that exact attested call.

## How this was built

This project was built with LLM agents working under one person's rulings. The standing rule is
that agents propose and the author decides: no gate is signed, no design fork resolved and no claim
about the work made by an agent. Tests were written by an author separate from the implementer
against a frozen baseline, and a third, fresh agent verified each change. The code was then put
through three cycles of adversarial review by an external four-chair council, whose findings and
the author's rulings on them are the record this repository keeps.

A few words the record uses without explaining them elsewhere:

- **Crucible** — the adversarial review protocol: four chairs, cycles, a final Quench.
- **Smith** — the author, in the protocol's terms; the only party who rules.
- **Quench** — the protocol's closing gate, where every untested assumption is accepted with a
  stated risk or the artifact does not ship.
- **D-nnn** — a numbered ruling in `docs/decisions.md`.
- **A-nnn** — a numbered finding from a review.
- **R-A018-nn** — an item in the remediation register.

## Start here: the enforcement release under `release/`

`release/` is the generated enforcement release candidate, v0.3 — produced by
`scripts/assemble-enforcement-release.py` and held byte-identical to a fresh assembly by
`scripts/check-release-sync.sh`. It is not a publication decision
or a production deployment. It carries the onchain and trust-root evidence that the historical
comprehension packet further down deliberately lacks:

- SentinelVault source, ABI, bytecode, compiler metadata, a focused adversarial test, and a
  reproducible release manifest;
- an owner-signed mandate that names the only signer the vault and isolated signer may accept;
- exclusive validity windows (`issuedAt <= evaluationTime < expiresAt`), authenticated
  chain/vault identity, exact calldata binding, and nonce consumption;
- a signed deployment manifest whose authority is supplied out of band rather than nominated by
  `domain.json`; and
- a cold Anvil demonstration that creates fresh lab authority for each run, writes no private
  keys, executes the exact authorized call, and rejects a BLOCK receipt at both Vault entry
  points and on both verifier paths, wrong authority, altered calldata, and replay.

### Run the cold demo

Prerequisites: Node with native TypeScript type stripping, Foundry (`forge` and `anvil`), and
Python 3.9+ with no third-party packages. `.nvmrc` and `.tool-versions` pin the versions the
author runs (Node 26.3.0, Python 3.9.6); `ts/package.json` declares the Node floor (24); Foundry
1.7.1 is the tested version and has no per-repository pin. From the repository root:

```sh
cd release
npm --prefix ts ci
forge build --root contracts
npm --prefix ts run cold-demo -- --output "$PWD/demo-out"
```

Give `--output` an absolute path: `npm --prefix` runs the script from `ts/`, so a relative one
lands there. The demo generates owner, isolated-signer and deployment-authority keys in memory,
deploys to a fresh Anvil, owner-signs and activates a signer-bound mandate, evaluates and signs in
the separate signer process, verifies the manifest and receipt, executes the exact call, runs
typed negative controls that each assert the specific refusal they expect, and ends by printing
the address to use next under the heading `LAB-GENERATED DEPLOYMENT AUTHORITY -- NOT PRODUCTION,
NOT A TRUST ROOT`.

### Verify what the demo wrote

[`release/README.md`](release/README.md) is the release's own first surface and the authority on
what it ships, what it does not bound, and how to verify what the demo just produced: its
"Independent verification" section carries the `verify_publication.py` invocations for
`demo-out/sample` and the BLOCK bundle beside it, the five-minute receipt lifetime, and the
exit-code contract. They are not repeated here. Two things to know before opening it. No signed deployment manifest ships anywhere in this repository: the only
one is the one the demo generates and signs with a lab authority it labels non-production, so
verifying against the address it prints is a self-consistency loop, not independent
authentication. And a recipient with Python alone — no Node, no Foundry, no Anvil — can
therefore run only the repository's `verifier/verify.py` on the checked-in fixtures, and that
tool certifies authenticity, never executability (D-092(f)).

### Two verifiers, two claims

The release ships one verifier, `verifier/verify_publication.py`, and its claim is
**executability**: would `SentinelVault` execute this bundle at the entry point it is presented
for. It refuses a BLOCK receipt, and a REVIEW receipt without an authenticated owner override,
because the Vault would refuse them. Its contract is `release/README.md`, "Two verifiers, two
claims" and "Exit codes".

The repository carries a second, older verifier at `verifier/verify.py`, which the release tree
does not ship. Its claim is **authenticity**: is this bundle genuinely what the signer produced.
It certifies nothing about execution, and its exit status says which of three things happened.
`0` means authentic and live: an ALLOW receipt, or a REVIEW receipt with a valid owner override,
inside its validity window. `3` means authentic but not executable: the hashes, signatures and
bindings hold against the named trust root, but the bundle is one the Vault refuses — a BLOCK
receipt, a REVIEW receipt with no `override.json`, a §5.5.1 refusal record, or a receipt or
override outside its validity window by the host clock, which is unauthenticated and which the
tool takes no caller-supplied instant to replace. `1` means a check failed. Under `--all`, `1`
beats `3` beats `0` (the split is ruled at D-087(c); the exit contract at D-090(a), D-091(a) and
D-092(c)). An expired receipt is still an authentic one and is counted as such. Every shipped
fixture is exit `3` today: the four BLOCK receipts and the refusal record by their verdict, the
ALLOW and overridden-REVIEW fixtures because their windows have closed. Measured on this commit
with the fixtures' own `domain.json` asserted as trust root: `case-2-injection-block` exits `3`
and is listed `NOT EXECUTABLE`; `--all` over the seven fixtures reports `7/7 sample(s) verified
as AUTHENTIC`, lists all seven `NOT EXECUTABLE`, and exits `3`. A `PASS` from this tool is
reachable only on a bundle whose window contains the moment you run it.

## What is not established, and where that is written down

The verifier's `NOT ESTABLISHED` line is the first place to read, because it travels with every
certifying result. `release/README.md`, "What this release does not bound", states the value
boundary — the per-action native-value ceiling, the atomic drain that `pause` cannot interrupt,
and the token-allowance ceiling that sits in the signed policy type and is read by no contract.
`docs/enforcement-release-v0.3.md` carries the same boundary with its rulings, the signer
rotation that does not revoke outstanding receipts, and the reason a v0.3 release emits evidence
tagged v0.2. None of those is an open defect; each is a ruled limit, recorded beside the test
that asserts it.

## Status

`docs/session-state.md` is rewritten at the end of each session and declares itself
authoritative over anything an agent or a reader remembers. `docs/publication-policy.state` is
the machine-checked publication state (`AUTHORIZED_PUBLIC` under D-099, rights `OPEN_SOURCE`);
`scripts/check-rename-gate.sh` refuses if the repository's visibility stops matching it. The licence is
Apache-2.0 (D-097): `LICENSE` and `NOTICE` at the root. The Crucible review record is in `docs/cycle-2-orchestrator-brief.md`, `docs/cycle-2-return-package.md`,
`docs/cycle-3-orchestrator-brief.md`, `docs/cycle-3-return-note.md`, `docs/cycle-3-patch-return-note.md`
and the four Quench handoffs `docs/quench-orchestrator-handoff.md`, `-2.md`, `-3.md` and `-4.md`;
the rulings that followed are D-088 through D-096 in `docs/decisions.md`. The whole record is
mapped in `docs/ARCHIVE-INDEX.md`.

## Historical: the v0.2 comprehension packet reviewed at Gate 8 (`reviewer-packet/`)

`reviewer-packet/` is the frozen v0.2 comprehension packet that passed Gate 8 under D-080: five
fixed-key bundles, a static dashboard and an older copy of the authenticity verifier, no Vault. Its
own `verifier/verify.py` predates the exit contract and prints a bare `=> PASS`, exit `0`, on a
BLOCK receipt that the repository's `verifier/verify.py` reports `AUTHENTIC, NOT EXECUTABLE`, exit
`3`; the packet's README carries a dated note saying so before its commands. D-090(b) re-ranked it
below the release. Its history is in `docs/archive/readme-historical-section-2026-09-04.md`.

## In this repository

These links are for people working in the repository. They are not part of a standalone reading of this file.

- **Spec:** [Sentinel_Lab_Proposal_v0_2.md](Sentinel_Lab_Proposal_v0_2.md) — §14.8 records the intake rulings, §14.9 the build-start amendments
- **Enforcement release v0.3:** [docs/enforcement-release-v0.3.md](docs/enforcement-release-v0.3.md) and the generated [release/README.md](release/README.md)
- **Build handoff:** [HANDOFF.md](HANDOFF.md)
- **Decision log:** [docs/decisions.md](docs/decisions.md)
- **Archive index:** [docs/ARCHIVE-INDEX.md](docs/ARCHIVE-INDEX.md) — the map of the record for a reader who did not live through it
- **Operating record (agent-facing; its top block is the live status):** [docs/session-state.md](docs/session-state.md)
- **Registers:** [docs/a018-remediation-register.md](docs/a018-remediation-register.md), [docs/v1-1-register.md](docs/v1-1-register.md)
- **Icon:** [assets/icon.png](assets/icon.png) — standard mark (nested chamber, cyan alignment line)

## Licence

Apache License, Version 2.0 — see `LICENSE` and `NOTICE` at the repository root (D-097, 2026-09-04).
Vendored dependencies under `contracts/lib/` carry their own notices. A licence is a grant of rights
over this code; the publication decision is D-099.
