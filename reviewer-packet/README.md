# Sentinel

A testnet mandate-to-effects conformance lab for agent-proposed EVM actions.

> The agent proposes. Sentinel evaluates. The isolated signer attests. SentinelVault enforces.

This project is distinct from Uppsala Security's Sentinel Protocol and from sentinel.co's Cosmos network. Those names collide; they are not affiliation. Named here because competitor overlap is a claimed property of the artifact, not because a legal conclusion has been drawn.

Sentinel is not a detector. It does not infer danger from bytecode, from a story an agent told, or from how a call “looks.” It checks whether one exact EVM call matches a human-signed mandate, against simulated effects at a recorded block, and it permits execution only of that exact attested call.

## What this packet does not contain

This packet is the off-chain half. SentinelVault is not in it — no source, no ABI, no tests — so “the vault will execute that exact call, or nothing” is a **design claim here, not a demonstrated one**. The fixtures were produced on chain 31337, a local devnet, using the standard local development accounts. Nothing here is a deployment.

The packet also cannot demonstrate its own headline trust-root property. See the verifier section below.

## What is cryptographically bound

Binding is to an **exact action**, not to a class of similar calls. These are the fields. A signature over them is not a signature over a similar call.

The **EIP-712 domain** binds `name` (`Sentinel`), `version` (`0.2`), `chainId`, and `verifyingContract` (the vault). A payload signed for a different chain or vault does not verify.

The **mandate** (owner-signed) binds `schemaVersion`, `mandateId`, `principal`, `vault`, `chainId`, `target`, `targetCodeHash`, `selector`, `maxNativeValueWei`, `purposeKind`, `resourceId`, `beneficiary`, `durationSeconds`, `recurringAllowed`, `validAfter`, `validUntil`, and `policyHash`.

The **policy** (hashed into the mandate and the action) binds `schemaVersion`, `policyVersion`, `vault`, `chainId`, `allowedOperation`, `allowedTargetsHash`, `allowedSelectorsHash`, `maxNativeValueWei`, `maxAllowanceIncreaseBaseUnits`, `allowedCallGraphHash`, `validAfter`, `validUntil`, and `failureMode`. `failureMode` decides what an UNRESOLVED check becomes: `0` = FAIL_CLOSED (BLOCK), `1` = REVIEW. It is pre-declared in the policy, not the evaluator’s discretion at decision time.

The **action** binds `schemaVersion`, `chainId`, `vault`, `actionNonce`, `target`, `valueWei`, `dataHash`, `operation`, `mandateHash`, `policyHash`, and `deadline`. Raw calldata rides beside that payload; it is not a field of the signed struct.

The **receipt** (signer-attested) binds `schemaVersion`, `decisionId`, `actionHash`, `mandateHash`, `policyHash`, `verdict` (a `uint8`: `0` = BLOCK, `1` = REVIEW, `2` = ALLOW), `reasonCodesHash`, `evidenceHash`, `simulationBlockNumber`, `simulationBlockHash`, `issuedAt`, `expiresAt`, and `signer`. The numbering is fail-closed: zero denies. It is the reverse of the order a reader meets the words ALLOW, BLOCK, REVIEW in the demonstration. Reason codes name the check that produced an adverse outcome, not the outcome. `EVAL_ALLOWANCE_EFFECT_WITHIN_CEILING` in a BLOCK receipt means that check failed; the outcome itself lives in the evidence.

An optional **owner override** of a REVIEW receipt binds `schemaVersion`, `reviewReceiptHash`, `actionHash`, `mandateHash`, `policyHash`, `actionNonce`, `reasonHash`, `issuedAt`, and `expiresAt`. A BLOCK cannot be overridden.

Mandate, policy and evidence travel as plain JSON and are committed by hash; the receipt binds those hashes. The owner’s signature over the mandate is **not exhibited in this packet** — only the signer’s receipt signature and the owner’s override signature are present and re-checked.

The agent’s rationale is not among those fields. It never enters the signature.

## Who signs what

Four roles, and they are not interchangeable.

- **Agent** — not trusted. Proposes a call. Does not sign. Its story is not evidence.
- **Evaluator** — not trusted as a cryptographic authority. Decides ALLOW, BLOCK, or REVIEW by comparing the decoded call and simulated effects to the mandate. Does not sign. Its decision is a claim until the signer attests the hashes.
- **Isolated signer** — trusted for the attestation, and only for that. The only party that signs a decision receipt. Independently decodes the calldata from the bytes and re-checks the structural bindings it can establish that way — target, selector, target code hash, vault allow-list, nonce — recording any mismatch as a signer finding in the receipt. It does not re-run the **purpose** comparison — resource, beneficiary, duration, recurrence — that would be a second evaluator. A signer finding is a note in a signed receipt, not a refusal: the signer refuses to attest at all only when the calldata cannot be decoded to the parameters the evidence claims. No bundle in this packet exercises that path.
- **Vault** — trusted, in the design, to refuse any call other than the attested one. Onchain. Does not sign the receipt. Does not re-prove that the simulation is still true of the chain. **Not present in this packet.**

The owner signs the mandate, and may sign an override for a REVIEW receipt. That is a fifth signature, not a fifth role. A BLOCK cannot be overridden; that path needs a new mandate or policy. This packet exhibits the override signature where a REVIEW bundle carries one. It does not exhibit the mandate’s owner signature.

## Why Case 3 blocks

Case 3 is the load-bearing case.

The call is mechanically valid: chain, vault, target, selector, value, and operation all match, and the simulation **succeeds**. The checks that would catch a dangerous-looking call are green.

It still BLOCKs because the **purpose is wrong**. The purchase is for a different resource than the mandate authorised. Not because the call looks dangerous. A reader who leaves thinking Sentinel is a threat detector has missed the point of the artifact.

Case 2 — an infinite approval to an attacker address on an uncommitted contract — is the memorable screen, and it is the weak evidence: it trips independent checks several of which a commodity allowance guard also trips. Case 3 trips exactly one, and only because a human pre-committed to a purpose. If you are choosing which case to remember, it is Case 3.

## What a receipt proves

A verified receipt proves that the deployment’s isolated signer attested this verdict over these hashes — action, mandate, policy, evidence, reason codes — at the simulation block the receipt names, and that the signature recovers to the signer in the trust root that was asserted, not to a signer the bundle nominated for itself. Anyone with the bundle and that trust root can re-check that offline. BLOCK is a signed decision, not a missing artifact.

## What a receipt does not prove

Verifying a receipt is not verifying that the simulation was true of the chain. Effects were judged at the recorded block. The vault is designed to bind the exact call at execution; it will not re-prove the effects. In this packet that enforcement is not demonstrated.

A verified receipt does not prove that the target code is benign. A code-hash mismatch is insufficient evidence for automatic approval, not a malice label.

It does not prove that the agent was honest, or that a prompt was or was not injected. The agent’s story never enters the bound fields.

It does not prove the receipt is still valid. Receipts carry `issuedAt` / `expiresAt` — a 300-second window in these fixtures — and the offline verifier does not check them against a clock. An expired receipt still verifies.

It does not prove anything about any other product.

It does not prove signer identity unless the `--domain` file came from a deployment record the verifying party already trusts. See below.

## The verifier, and what a PASS in this packet means

A Python verifier re-checks a signed receipt against a trust root the verifying party asserts:

```
python3 verifier/verify.py --domain <deployment-domain.json> bundles/case-1-allow
python3 verifier/verify.py --domain <deployment-domain.json> bundles/case-3-wrong-purpose-block
```

`--domain` must name the deployment’s own `domain.json`, taken from the deployment record. Without it, a `domain.json` found inside or beside the bundle is loaded for diagnostics but can never carry a PASS — a presenter must not choose what “the signer” means.

The `bundles/domain.json` shipped here is presenter-supplied. Passing it will print PASS, and that PASS certifies the hashing and the signature recovery but **says nothing about signer identity**. This packet ships no out-of-band deployment record, so as delivered it cannot demonstrate the trust-root property it is proudest of.

Without `--domain` the tool reports diagnostics and does not PASS. A BLOCK receipt should still verify: BLOCK is a signed decision, not a missing artifact.
