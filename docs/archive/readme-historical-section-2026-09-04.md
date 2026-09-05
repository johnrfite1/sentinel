# README historical section: the v0.2 comprehension packet reviewed at Gate 8 (archived 2026-09-04)

This file is the "Historical: the v0.2 comprehension packet reviewed at Gate 8 (`reviewer-packet/`)" section of the root `README.md`, lines 194–302 at `3b69fa0`, moved here verbatim on 2026-09-04 when the README was shortened for publication prep; nothing was edited in the move, and the README keeps a short stub in its place. The map is `docs/ARCHIVE-INDEX.md`.

---

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

It does not prove the receipt is still valid. Receipts carry `issuedAt` / `expiresAt` — a 300-second window in these fixtures — and the packet's frozen copy of the verifier does not check them against a clock, so there an expired receipt still prints `=> PASS`. The repository's current `verifier/verify.py` does compare the window to the unauthenticated host clock and reports an expired receipt as `=> AUTHENTIC, NOT EXECUTABLE`, exit `3` (D-092(c)).

It does not prove anything about any other product.

It does not prove signer identity unless the `--domain` file came from a deployment record the verifying party already trusts. See below.

### The authenticity verifier, and what a PASS in this packet means

`verify.py` re-checks a signed receipt against a trust root the verifying party asserts. The
packet's invocation, described rather than given: from the repository root, run the packet's own
copy of the verifier (the `verify.py` under `reviewer-packet/verifier/`) with its `--domain`
option pointing at the packet's `bundles/domain.json` and the ALLOW bundle,
`bundles/case-1-allow`, as the positional argument. No command is given here to copy.

This section carried two fenced commands until 2026-09-02. Before that date they read
`verifier/verify.py … bundles/case-1-allow`, a path that resolves only inside
`reviewer-packet/`, so they did not run from the root; the Cycle 3 candidate corrected the paths,
which made the second of them — the packet verifier on the BLOCK bundle, printing `=> PASS` and
exiting `0` — copy-pasteable for the first time, and three Crucible chairs failed the candidate
on that line. Under D-092(a) the BLOCK command is deleted and the surviving ALLOW command is
rendered as the prose above, so that nothing in this Historical section runs as written.

`--domain` must name the deployment’s own `domain.json`, taken from the deployment record. Without it, a `domain.json` found inside or beside the bundle is loaded for diagnostics but can never carry a PASS — a presenter must not choose what “the signer” means.

The `bundles/domain.json` shipped here is presenter-supplied, which is why the invocation described above names it explicitly. Passing it will print PASS, and that PASS certifies the hashing and the signature recovery but **says nothing about signer identity**. This packet ships no out-of-band deployment record, so as delivered it cannot demonstrate the trust-root property it is proudest of.

Without `--domain` the tool reports diagnostics and does not PASS. A BLOCK receipt still verifies as authentic: BLOCK is a signed decision, not a missing artifact, and this verifier certifies that the decision is authentic, not that it is executable. Do not expect exit `0` from the current tool for that, though. Two copies exist and they differ on this commit, measured on Case 3: `reviewer-packet/verifier/verify.py` — the copy the invocation described above uses — predates D-087(c) and D-090(a), prints a bare `=> PASS`, and exits `0`; `verifier/verify.py` at the repository root prints `=> AUTHENTIC, NOT EXECUTABLE: the signed verdict is BLOCK …`, counts it in `1/1 sample(s) verified as AUTHENTIC`, lists it as `NOT EXECUTABLE: reviewer-packet/bundles/case-3-wrong-purpose-block`, and exits `3` (D-090(a)). The packet copy is the stale one; the root copy is the contract.
