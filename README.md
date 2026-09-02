# Sentinel

Sentinel is a testnet lab that binds one exact EVM call to a human-signed mandate. An untrusted agent proposes a call; an evaluator compares the decoded call and its simulated effects at a recorded block to the mandate; an isolated signer attests the verdict in a signed receipt; and `SentinelVault` executes the exact attested bytes on an ALLOW receipt, executes a REVIEW receipt only alongside a separate owner-signed override, and reverts a BLOCK receipt at both entry points, altered calldata, and a replayed nonce. What that establishes is narrow, and the tools say so themselves: the release's offline verifier certifies only that the Vault's offline-checkable predicate accepts a bundle, and prints a `NOT ESTABLISHED` line beside every certifying result — no chain is read, so deployed code identity and nonce freshness are not established; the clock is unauthenticated; the calldata arguments are never decoded by the verifier or the Vault, only by the signer's evaluator; and the Vault's native-value ceiling is per action, bounding neither aggregate loss nor token allowances, which no contract here caps. Sentinel is not a detector, not a production wallet, and not a deployment: the fixtures and the cold demo run on a local Anvil, and testnet-only is documented rather than enforced. Status at this revision (2026-09-02): a pre-publication candidate under external adversarial review, held private, publication not authorised, licence deferred; `docs/session-state.md` is the live status and wins over anything written here. Where the record lives: the mechanism in `contracts/` and `verifier/`; the limitations in the verifier's own `NOT ESTABLISHED` output, `release/README.md` and `docs/enforcement-release-v0.3.md`; the status in `docs/session-state.md`; and the archive — every ruling, register and review arc, kept because the history is part of what is evaluated — in `docs/decisions.md`, `docs/a018-remediation-register.md`, `docs/v1-1-register.md` and the `docs/review-*/` directories.

This project is distinct from Uppsala Security's Sentinel Protocol and from sentinel.co's Cosmos network. Those names collide; they are not affiliation. Named here because competitor overlap is a claimed property of the artifact, not because a legal conclusion has been drawn.

> The agent proposes. Sentinel evaluates. The isolated signer attests. SentinelVault enforces.

Sentinel is not a detector. It does not infer danger from bytecode, from a story an agent told, or from how a call “looks.” It checks whether one exact EVM call matches a human-signed mandate, against simulated effects at a recorded block, and it permits execution only of that exact attested call.

## Start here: the enforcement release under `release/`

`release/` is the generated enforcement release candidate, v0.3. It is not a publication decision
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

`release/README.md` is the release's own first surface and is the authority on what it ships,
what it does not bound, and how to verify it. What follows is that README's runnable path,
restated here so that the repository's first surface and the release's agree.

### Run the cold demo

Prerequisites: Node with native TypeScript type stripping, Foundry (`forge` and `anvil`), and
Python 3.8+ with no third-party packages. The sequence below was run from a fresh clone of this
commit with Node 26.3.0, Foundry 1.7.1 and Python 3.9.6. From the repository root:

```sh
cd release
npm --prefix ts ci
forge build --root contracts
npm --prefix ts run cold-demo -- --output "$PWD/demo-out"
```

Give `--output` an absolute path: `npm --prefix` runs the script from `ts/`, so a relative one
lands there. The demo generates owner, isolated-signer and deployment-authority keys in memory,
deploys to a fresh Anvil, owner-signs and activates a signer-bound mandate, evaluates and signs in
the separate signer process, verifies the manifest and receipt, executes the exact call, and
runs typed negative controls that each assert the specific refusal they expect. It ends by
printing the address to use next, under the heading
`LAB-GENERATED DEPLOYMENT AUTHORITY -- NOT PRODUCTION, NOT A TRUST ROOT`. The demo signed its
own manifest with that key, so the verification below is a self-consistency loop, not an
independent authentication; a real recipient's authority arrives over a channel the publisher
does not control.

### Verify independently

Still inside `release/`, substituting the printed address:

```sh
python3 verifier/verify_publication.py demo-out/sample \
  --deployment-manifest demo-out/deployment-manifest.json \
  --deployment-authority 0xADDRESS_THE_DEMO_PRINTED
```

**The ALLOW bundle expires 300 seconds after the demo signed it.** The isolated signer issues
receipts with a five-minute lifetime, and the verifier evaluates that window against the host
clock. Run within five minutes: exit `0` and a headline beginning `PASS (static, offline):`,
followed by a `CLAIM:` line stating which claim this tool makes and a `NOT ESTABLISHED by this
run:` line naming what it did not check. Run later: exit `1` and `FAIL: receipt requires
issuedAt <= evaluationTime < expiresAt; got …`. The second is expiry, not rejection — the bytes
are the same, and a verifier with a window is doing what it should. Re-run the demo for a fresh
bundle.

The BLOCK bundle the demo wrote beside it does not go stale the same way. The verdict is checked
before the windows, so `demo-out/sample-block` is refused however long you wait, on either path:

```sh
python3 verifier/verify_publication.py demo-out/sample-block \
  --deployment-manifest demo-out/deployment-manifest.json \
  --deployment-authority 0xADDRESS_THE_DEMO_PRINTED
# exit 1 — FAIL: receipt.verdict is BLOCK (0), not ALLOW: …
python3 verifier/verify_publication.py demo-out/sample-block \
  --deployment-manifest demo-out/deployment-manifest.json \
  --deployment-authority 0xADDRESS_THE_DEMO_PRINTED \
  --execution-path owner-override
# exit 1 — FAIL: receipt.verdict is BLOCK (0), not REVIEW: …
```

Exit codes: `0` certifying, `1` refused with a `FAIL:` line on stderr, and `3` — not certified
and not a refusal — only under `--evaluation-time`. A script that treats any non-zero status as
a failure, or any non-`1` status as a pass, misreads the third.

### Two verifiers, two claims

The release ships one verifier, `verifier/verify_publication.py`, and its claim is
**executability**: would `SentinelVault` execute this bundle at the entry point it is presented
for. It refuses a BLOCK receipt, and a REVIEW receipt without an authenticated owner override,
because the Vault would refuse them. Its certifying output carries its own `CLAIM:` line:

> CLAIM: this tool certifies EXECUTABILITY, statically and offline -- that SentinelVault's offline-checkable action predicate accepts this bundle at the entry point named above. It is not the authenticity verifier: verify.py certifies AUTHENTICITY, that the bundle is genuinely what the signer produced, and reports a BLOCK receipt, a REVIEW receipt with no override, or a §5.5.1 refusal record -- all of which this tool refuses -- as AUTHENTIC, NOT EXECUTABLE with exit status 3, not as a PASS (D-090(a), D-091(a)).

The repository carries that second, older verifier at `verifier/verify.py`, which the release
tree does not ship. Its claim is **authenticity**: is this bundle genuinely what the signer
produced. It evaluates no validity window and certifies nothing about execution. Under
D-090(a) and D-091(a), landed 2026-09-02, it no longer exits `0` for anything the Vault would
not execute: a BLOCK receipt, a REVIEW receipt with no `override.json`, or a §5.5.1 refusal
record (a signed refusal to issue a receipt at all) prints `=> AUTHENTIC, NOT EXECUTABLE: …` and
exits `3` — neither a certification nor a rejection — while ALLOW, and REVIEW with a valid owner
override, keep `=> PASS: AUTHENTIC` and exit `0`, and a bundle that fails a check keeps `=> FAIL`
and exit `1`. Under `--all`, `1` beats `3` beats `0`. Measured on this commit:
`python3 verifier/verify.py --domain fixtures/samples/domain.json fixtures/samples/case-2-injection-block`
exits `3` and lists `NOT EXECUTABLE: fixtures/samples/case-2-injection-block`; `--all
fixtures/samples` reports `7/7 sample(s) verified as AUTHENTIC`, lists five `NOT EXECUTABLE`
bundles (four BLOCK receipts and the refusal record), and exits `3`. The split is ruled at D-087(c) and stated in
`docs/enforcement-release-v0.3.md`, "Two verifiers, two claims".

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
the machine-checked publication state (`HELD_PRIVATE`, rights `UNDECIDED`); `scripts/check-rename-gate.sh`
refuses if the repository's visibility stops matching it. The licence is deliberately deferred
(D-082(c)) and no agent may select one. The Crucible review record is in
`docs/cycle-2-orchestrator-brief.md` and `docs/cycle-2-return-package.md`; the rulings that
followed are D-088 through D-090 in `docs/decisions.md`.

## Historical: the v0.2 comprehension packet reviewed at Gate 8 (`reviewer-packet/`)

Everything from here to "In this repository" describes the private comprehension packet under
`reviewer-packet/`: five fixed-key decision bundles, a static dashboard, and a copy of the
authenticity verifier. It is the off-chain half only, and it was the lab's first surface until
2026-09-02, when the Crucible's Cycle 2 sustained a Critical against exactly that: this file's
verifier commands resolved only inside the packet, so a reader was routed to `verify.py`, which
prints PASS on a BLOCK receipt. D-090(b) re-ranked it here. Nothing below is deleted; it is
history, and the history is part of what is evaluated.

Gate 8 (five-minute comprehension) passed under D-080 against the predecessor v0.2 packet. The
packet was then regenerated on the v0.3 mandate/domain schema while retaining the
`sentinel.evidence.v0.2` evidence-envelope tag; Gate 8 has not been rerun against that
regeneration, and D-080's recorded qualitative limits remain historical evidence, not the v0.3
release trust model. `reviewer-packet/verifier/verify.py` is the **authenticity** verifier
(D-010): it establishes that a bundle is genuinely what the named signer produced. **It does not
certify executability** — the repository's `verifier/verify.py` reports a BLOCK receipt as
`AUTHENTIC, NOT EXECUTABLE` with exit `3` (D-090(a)), the packet's older copy still prints a bare
`=> PASS` on it, and the verifier that answers whether the Vault would execute a bundle is the
release's `verify_publication.py`, above.

### What this packet does not contain

This packet is the off-chain half. SentinelVault is not in it — no source, no ABI, no tests — so “the vault will execute that exact call, or nothing” is a **design claim here, not a demonstrated one**. The fixtures were produced on chain 31337, a local devnet, using the standard local development accounts. Nothing here is a deployment.

The verifier source also ships the published local test keys for the fixture signer and owner. Anyone holding this packet can mint new receipts and owner overrides that verify against the presenter-supplied `bundles/domain.json`. These signatures demonstrate the payload format, hashing, and signature recovery — **not custody of either signing key**.

The packet also cannot demonstrate its own headline trust-root property. See the verifier section below.

### What is cryptographically bound

Binding is to an **exact action**, not to a class of similar calls. These are the fields. A signature over them is not a signature over a similar call.

The **EIP-712 domain** binds `name` (`Sentinel`), `version` (`0.3`), `chainId`, and `verifyingContract` (the vault). A payload signed for a different chain or vault does not verify.

The **mandate** (owner-signed) binds `schemaVersion`, `mandateId`, `principal`, `signer`, `vault`, `chainId`, `target`, `targetCodeHash`, `selector`, `maxNativeValueWei`, `purposeKind`, `resourceId`, `beneficiary`, `durationSeconds`, `recurringAllowed`, `validAfter`, `validUntil`, and `policyHash`.

The **policy** (hashed into the mandate and the action) binds `schemaVersion`, `policyVersion`, `vault`, `chainId`, `allowedOperation`, `allowedTargetsHash`, `allowedSelectorsHash`, `maxNativeValueWei`, `maxAllowanceIncreaseBaseUnits`, `allowedCallGraphHash`, `validAfter`, `validUntil`, and `failureMode`. `failureMode` decides what an UNRESOLVED check becomes: `0` = FAIL_CLOSED (BLOCK), `1` = REVIEW. It is pre-declared in the policy, not the evaluator’s discretion at decision time.

The **action** binds `schemaVersion`, `chainId`, `vault`, `actionNonce`, `target`, `valueWei`, `dataHash`, `operation`, `mandateHash`, `policyHash`, and `deadline`. Raw calldata rides beside that payload; it is not a field of the signed struct.

The **receipt** (signer-attested) binds `schemaVersion`, `decisionId`, `actionHash`, `mandateHash`, `policyHash`, `verdict` (a `uint8`: `0` = BLOCK, `1` = REVIEW, `2` = ALLOW), `reasonCodesHash`, `evidenceHash`, `simulationBlockNumber`, `simulationBlockHash`, `issuedAt`, `expiresAt`, and `signer`. The numbering is fail-closed: zero denies. It is the reverse of the order a reader meets the words ALLOW, BLOCK, REVIEW in the demonstration. Reason codes name the check that produced an adverse outcome, not the outcome. `EVAL_ALLOWANCE_EFFECT_WITHIN_CEILING` in a BLOCK receipt means that check failed; the outcome itself lives in the evidence.

An optional **owner override** of a REVIEW receipt binds `schemaVersion`, `reviewReceiptHash`, `actionHash`, `mandateHash`, `policyHash`, `actionNonce`, `reasonHash`, `issuedAt`, and `expiresAt`. A BLOCK cannot be overridden.

Mandate, policy and evidence travel as plain JSON and are committed by hash; the receipt binds those hashes. Each decision bundle now exhibits the owner’s signature over its signer-bound mandate as `mandate-signature.json`, alongside the signer’s receipt signature and, for REVIEW, the owner’s override signature. These are fixed-key private fixtures for format inspection, not production identity evidence; the key-free release uses fresh per-run lab authority and an independently authenticated deployment manifest.

The agent’s rationale is not among those fields. It never enters the signature.

### Who signs what

Four roles, and they are not interchangeable.

- **Agent** — not trusted. Proposes a call. Does not sign. Its story is not evidence.
- **Evaluator** — not trusted as a cryptographic authority. Decides ALLOW, BLOCK, or REVIEW by comparing the decoded call and simulated effects to the mandate. Does not sign. Its decision is a claim until the signer attests the hashes.
- **Isolated signer** — trusted for the attestation, and only for that. The only party that signs a decision receipt. Independently decodes the calldata from the bytes and re-checks the structural bindings it can establish that way — target, selector, target code hash, vault allow-list, nonce — recording any mismatch as a signer finding in the receipt. It does not re-run the **purpose** comparison — resource, beneficiary, duration, recurrence — that would be a second evaluator. A signer finding is a note in a signed receipt, not a refusal: the signer refuses to attest at all only when the calldata cannot be decoded to the parameters the evidence claims. No bundle in this packet exercises that path.
- **Vault** — trusted, in the design, to refuse any call other than the attested one. Onchain. Does not sign the receipt. Does not re-prove that the simulation is still true of the chain. **Not present in this packet.**

The owner signs the mandate, and may sign an override for a REVIEW receipt. That is a fifth signature, not a fifth role. A BLOCK cannot be overridden; that path needs a new mandate or policy. This packet exhibits the override signature where a REVIEW bundle carries one, and — corrected 2026-09-02; this sentence previously said the opposite, and had been false since the v0.3 regeneration added `mandate-signature.json` to every bundle — it exhibits the mandate’s owner signature too.

### Why Case 3 blocks

Case 3 is the load-bearing case.

The call is mechanically valid: chain, vault, target, selector, value, and operation all match, and the simulation **succeeds**. The checks that would catch a dangerous-looking call are green.

It still BLOCKs because the **purpose is wrong**. The purchase is for a different resource than the mandate authorised. Not because the call looks dangerous. A reader who leaves thinking Sentinel is a threat detector has missed the point of the artifact.

Case 2 — an infinite approval to an attacker address on an uncommitted contract — is the memorable screen, and it is the weak evidence: it trips independent checks several of which a commodity allowance guard also trips. Case 3 trips exactly one **evaluator policy check**: `EVAL_PURCHASE_RESOURCE` is a VIOLATION because a human pre-committed to a purpose. Its signed receipt also commits to `SIGNER_NONCE_ALREADY_ATTESTED`, a signer finding produced because the packet's fixtures reuse action nonce 0 under the same live authorisation basis. That finding is a note in the receipt, not the ground of the BLOCK. Removing it would require regenerating the signed fixture, which this record does not authorise. If you are choosing which case to remember, it is Case 3.

### What a receipt proves

A verified receipt proves that the deployment’s isolated signer attested this verdict over these hashes — action, mandate, policy, evidence, reason codes — at the simulation block the receipt names, and that the signature recovers to the signer in the trust root that was asserted, not to a signer the bundle nominated for itself. Anyone with the bundle and that trust root can re-check that offline. BLOCK is a signed decision, not a missing artifact.

### What a receipt does not prove

Verifying a receipt is not verifying that the simulation was true of the chain. Effects were judged at the recorded block. The vault is designed to bind the exact call at execution; it will not re-prove the effects. In this packet that enforcement is not demonstrated.

A verified receipt does not prove that the target code is benign. A code-hash mismatch is insufficient evidence for automatic approval, not a malice label.

It does not prove that the agent was honest, or that a prompt was or was not injected. The agent’s story never enters the bound fields.

It does not prove the receipt is still valid. Receipts carry `issuedAt` / `expiresAt` — a 300-second window in these fixtures — and the authenticity verifier does not check them against a clock. An expired receipt still verifies.

It does not prove anything about any other product.

It does not prove signer identity unless the `--domain` file came from a deployment record the verifying party already trusts. See below.

### The authenticity verifier, and what a PASS in this packet means

`verify.py` re-checks a signed receipt against a trust root the verifying party asserts. From
the repository root:

```
python3 reviewer-packet/verifier/verify.py --domain reviewer-packet/bundles/domain.json reviewer-packet/bundles/case-1-allow
python3 reviewer-packet/verifier/verify.py --domain reviewer-packet/bundles/domain.json reviewer-packet/bundles/case-3-wrong-purpose-block
```

Until 2026-09-02 these two lines read `verifier/verify.py … bundles/case-1-allow`, a path that
resolves only inside `reviewer-packet/`; they are corrected to resolve from the root so that
they run as written from a fresh clone.

`--domain` must name the deployment’s own `domain.json`, taken from the deployment record. Without it, a `domain.json` found inside or beside the bundle is loaded for diagnostics but can never carry a PASS — a presenter must not choose what “the signer” means.

The `bundles/domain.json` shipped here is presenter-supplied, which is why the commands above name it explicitly. Passing it will print PASS, and that PASS certifies the hashing and the signature recovery but **says nothing about signer identity**. This packet ships no out-of-band deployment record, so as delivered it cannot demonstrate the trust-root property it is proudest of.

Without `--domain` the tool reports diagnostics and does not PASS. A BLOCK receipt still verifies as authentic: BLOCK is a signed decision, not a missing artifact, and this verifier certifies that the decision is authentic, not that it is executable. Do not expect exit `0` from the current tool for that, though. Two copies exist and they differ on this commit, measured on Case 3: `reviewer-packet/verifier/verify.py` — the copy the two commands above invoke — predates D-087(c) and D-090(a), prints a bare `=> PASS`, and exits `0`; `verifier/verify.py` at the repository root prints `=> AUTHENTIC, NOT EXECUTABLE: the signed verdict is BLOCK …`, counts it in `1/1 sample(s) verified as AUTHENTIC`, lists it as `NOT EXECUTABLE: reviewer-packet/bundles/case-3-wrong-purpose-block`, and exits `3` (D-090(a)). The packet copy is the stale one; the root copy is the contract.

## In this repository

These links are for people working in the repository. They are not part of a standalone reading of this file.

- **Spec:** [Sentinel_Lab_Proposal_v0_2.md](Sentinel_Lab_Proposal_v0_2.md) — §14.8 records the intake rulings, §14.9 the build-start amendments
- **Enforcement release v0.3:** [docs/enforcement-release-v0.3.md](docs/enforcement-release-v0.3.md) and the generated [release/README.md](release/README.md)
- **Build handoff:** [HANDOFF.md](HANDOFF.md)
- **Decision log:** [docs/decisions.md](docs/decisions.md)
- **Session state (read first when resuming):** [docs/session-state.md](docs/session-state.md)
- **Registers:** [docs/a018-remediation-register.md](docs/a018-remediation-register.md), [docs/v1-1-register.md](docs/v1-1-register.md)
- **Icon:** [assets/icon.png](assets/icon.png) — standard mark (nested chamber, cyan alignment line)
