# Sentinel

A testnet mandate-to-effects conformance lab for agent-proposed EVM actions.

> The agent proposes. Sentinel evaluates. The isolated signer attests. SentinelVault enforces.

This project is distinct from Uppsala Security's Sentinel Protocol and from sentinel.co's Cosmos network. Those names collide; they are not affiliation. Named here because competitor overlap is a claimed property of the artifact, not because a legal conclusion has been drawn.

Sentinel is not a detector. It does not infer danger from bytecode, from a story an agent told, or from how a call “looks.” It checks whether one exact EVM call matches a human-signed mandate, against simulated effects at a recorded block, and it permits execution only of that exact attested call.

## What is cryptographically bound

Binding is to an **exact action**, not to a class of similar calls. These are the fields. A signature over them is not a signature over a similar call.

The **EIP-712 domain** binds `name` (`Sentinel`), `version` (`0.2`), `chainId`, and `verifyingContract` (the vault). A payload signed for a different chain or vault does not verify.

The **mandate** (owner-signed) binds `schemaVersion`, `mandateId`, `principal`, `vault`, `chainId`, `target`, `targetCodeHash`, `selector`, `maxNativeValueWei`, `purposeKind`, `resourceId`, `beneficiary`, `durationSeconds`, `recurringAllowed`, `validAfter`, `validUntil`, and `policyHash`.

The **policy** (hashed into the mandate and the action) binds `schemaVersion`, `policyVersion`, `vault`, `chainId`, `allowedOperation`, `allowedTargetsHash`, `allowedSelectorsHash`, `maxNativeValueWei`, `maxAllowanceIncreaseBaseUnits`, `allowedCallGraphHash`, `validAfter`, `validUntil`, and `failureMode`.

The **action** binds `schemaVersion`, `chainId`, `vault`, `actionNonce`, `target`, `valueWei`, `dataHash`, `operation`, `mandateHash`, `policyHash`, and `deadline`. Raw calldata rides beside that payload; it is not a field of the signed struct. The vault will execute that exact call, or nothing.

The **receipt** (signer-attested) binds `schemaVersion`, `decisionId`, `actionHash`, `mandateHash`, `policyHash`, `verdict` (ALLOW, BLOCK, or REVIEW), `reasonCodesHash`, `evidenceHash`, `simulationBlockNumber`, `simulationBlockHash`, `issuedAt`, `expiresAt`, and `signer`.

An optional **owner override** of a REVIEW receipt binds `schemaVersion`, `reviewReceiptHash`, `actionHash`, `mandateHash`, `policyHash`, `actionNonce`, `reasonHash`, `issuedAt`, and `expiresAt`. A BLOCK cannot be overridden.

The agent’s rationale is not among those fields. It never enters the signature.

## Who signs what

Four roles, and they are not interchangeable.

- **Agent** — not trusted. Proposes a call. Does not sign. Its story is not evidence.
- **Evaluator** — not trusted as a cryptographic authority. Decides ALLOW, BLOCK, or REVIEW by comparing the decoded call and simulated effects to the mandate. Does not sign. Its decision is a claim until the signer attests the hashes.
- **Isolated signer** — trusted for the attestation, and only for that. The only party that signs a decision receipt. Attests the verdict over those hashes. Independently decodes the calldata and refuses if the decoded parameters in the evidence do not match the bytes. It does not re-run the mandate comparison; that would be a second evaluator.
- **Vault** — trusted to refuse any call other than the attested one. Onchain. Does not sign the receipt. Does not re-prove that the simulation is still true of the chain.

The owner signs the mandate, and may sign an override for a REVIEW receipt. That is a fifth signature, not a fifth role. A BLOCK cannot be overridden; that path needs a new mandate or policy.

A Python verifier in the demonstration packet re-checks a signed receipt against a trust root the operator asserts. The bundle cannot nominate its own signer and pass.

## Why Case 3 blocks

Case 3 is the load-bearing case.

The call is mechanically valid: chain, vault, target, selector, value, and operation all match, and the simulation **succeeds**. The checks that would catch a dangerous-looking call are green.

It still BLOCKs because the **purpose is wrong**. The purchase is for a different resource than the mandate authorised. Not because the call looks dangerous. A reader who leaves thinking Sentinel is a threat detector has missed the point of the artifact.

## What a receipt proves

A verified receipt proves that the deployment’s isolated signer attested this verdict over these hashes — action, mandate, policy, evidence, reason codes — at the simulation block the receipt names, and that the signature recovers to the signer in the trust root that was asserted, not to a signer the bundle nominated for itself. Anyone with the bundle and that trust root can re-check that offline. BLOCK is a signed decision, not a missing artifact.

## What a receipt does not prove

Verifying a receipt is not verifying that the simulation was true of the chain. Effects were judged at the recorded block. The vault will bind the exact call at execution; it will not re-prove the effects.

A verified receipt does not prove that the target code is benign. A code-hash mismatch is insufficient evidence for automatic approval, not a malice label.

It does not prove that the agent was honest, or that a prompt was or was not injected. The agent’s story never enters the bound fields.

It does not prove anything about any other product.
