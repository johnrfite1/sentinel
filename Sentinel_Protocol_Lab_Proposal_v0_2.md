---
primary_layer: "project"
status: "active"
domains: ["ai_security", "agentic_systems", "blockchain_security", "product_design"]
project: "sentinel_protocol_lab"
summary: "Narrowed proposal for a vendor-neutral mandate-to-effects conformance lab for agent-proposed EVM actions."
depends_on:
  - "../vault/Protocol Stack/Layer 1 - Domain Protocols/L1 - AI - Agentic Security.md"
  - "../vault/Protocol Stack/Layer 1 - Domain Protocols/L1 - AI - Courtroom Verification.md"
  - "../vault/Protocol Stack/Layer 1 - Domain Protocols/L1 - AI Operations - Bounded Autonomy.md"
extracted_from: []
extracted_to: []
review_date: "2026-08-09"
ttl: "Review monthly while build and market validation are active."
exclude_from_loading: false
tags: ["project-doc", "portfolio", "artifact-hub", "ai-agents", "evm", "security", "bounded-autonomy"]
changelog:
  - "2026-07-09: Initial v0.1 proposal."
  - "2026-07-09: Reframed v0.2 around portable mandate-to-effects assertions; narrowed the MVP, corrected the market thesis, specified one enforcement substrate, and made adversarial evaluation the primary proof artifact."
  - "2026-07-27: Added Section 14 reviewer notes (Claude): independent receipt-verifier demo, predicted-vs-observed effects clarification, vendor-baseline scope reduction, mandate-fidelity limit, discovery sequencing. (Entry originally misdated 2026-07-09; corrected.)"
  - "2026-07-27: Applied John's ratified rulings — expanded §8 honest limits per 14.5 and the 14.3 claims-boundary clarification; added §14.8 recording rulings on the Section 14 ladder, gate cadence, and kill criteria. Proposal now lives in the Sentinel project repository; build launched."
  - "2026-07-27: Post-verification fixes from the independent review pass — 14.4 ruling relabeled adopted-with-modification, dispatch ruling mirrored into §14.8, depends_on paths updated for the repository location."
  - "2026-07-27: Build-start amendments D-007..D-011 (delegated rulings) added as §14.9; §8 gained the procedural-not-organizational limit on corpus labeling. §14.8 preserved unchanged."
---

# Sentinel Protocol Lab
## Portfolio MVP and Market-Discovery Proposal

Version: v0.2  
Date: July 9, 2026  
Status: Greenlight a narrowed portfolio MVP; treat commercialization as an unproven hypothesis.  
Purpose: Define an Artifact Hub flagship that demonstrates bounded AI action at an irreversible external-state boundary.

> Working-name warning: “Sentinel Protocol” is already used by blockchain-security and blockchain-network projects. Treat Sentinel as an internal codename until a domain and trademark review is completed. Rename before public launch. This is a naming-risk observation, not a legal conclusion.

---

## 1. Executive Decision

Build Sentinel, but build a much narrower system than v0.1 proposed.

Sentinel Protocol Lab is a testnet mandate-to-effects conformance lab for agent-proposed EVM actions. It binds an exact action to a human-signed mandate, evaluates deterministic policy and pinned-state execution evidence, and permits execution only through a testnet vault that enforces the result.

The project is an Artifact Hub flagship first and a startup-discovery vehicle second. It is not a wallet, custody product, generalized smart-contract auditor, token ecosystem, or production security guarantee.

The narrower differentiation hypothesis is:

> Portable typed mandate-to-effect assertions, exact cryptographic binding, and independently verifiable decision receipts may provide assurance that existing wallet controls do not provide consistently across providers.

This must be demonstrated, not assumed. Several current products already offer intent-aware delegation, calldata constraints, completion conditions, simulation, policy enforcement, and human review.

One-line description:

> Sentinel tests whether an exact agent-proposed EVM action and its supported effects conform to the mandate the user signed.

Conceptual hook:

> Wallet policy asks whether an action is permitted. Sentinel tests whether the observed action fulfills the bound mandate.

Current assessment:

| Dimension | Assessment |
|---|---:|
| Underlying need | 8/10 |
| Narrow portfolio MVP feasibility | 8.5/10 |
| Full v0.1 breadth as a solo build | 4/10 |
| Generic agent-wallet firewall differentiation | 3–4/10 |
| Portable conformance and receipt hypothesis | 6/10 pending evidence |
| Startup readiness | 3–4/10 |
| Portfolio value with rigorous evaluation | 9/10 |

---

## 2. Need, Market Reality, and First User

AI agents can now hold credentials, call tools, spend money, sign messages, and submit blockchain actions. Prompt injection, poisoned context, specification gaming, ambiguous intent, and excessive permissions can therefore become financial events rather than merely bad text.

The security question is:

> Is this exact action authorized by this owner, for this typed purpose, under this active policy, against this deployed code, at this moment?

NIST’s 2026 agent-security inquiry focuses on systems that affect external state and on least privilege, constrained environments, monitoring, and human approval. Onchain actions are a useful proving ground because they are exact, value-bearing, adversarial, and reproducible in local execution environments.

The market, however, is already active. Agent-wallet and wallet-security providers offer substantial parts of the original proposal:

| Category | Examples | Existing capability | Consequence for Sentinel |
|---|---|---|---|
| Pact-first agent authorization | Cobo Agentic Wallet | Owner-approved task pacts, scoped and revocable credentials, parameter matching, completion conditions, rolling limits, and allow/review/deny enforcement [§13#5 read 2026-08-15] [§13#6 read 2026-08-15] | Intent-aware authorization is not an empty category |
| Wallet policy infrastructure | Privy | Rules over value, network, destination, contract, and decoded calldata [§13#9 read 2026-08-15] | Generic policy-as-code is a substitute |
| Wallet policy infrastructure | Coinbase Policy Engine | Rules over value and destination [§13#7 read 2026-08-15] | Generic policy-as-code is a substitute |
| Agent payment wallets | Circle Agent Wallets | Spend limits, address controls, compliance screening, and agent-native execution (inference) [§13#8 read 2026-08-15] | Spend governance is increasingly bundled |
| Direct agent-wallet security | Sigil | ERC-4337 wallet, Guardian co-signing, deterministic rules, simulation, AI risk scoring, policies, and recovery [§13#12 read 2026-08-15] | Close overlap with the original stack |
| Smart-account controls | Safe | Guards, allowance modules, multisignature approval, recovery modules, and agent spending patterns [§13#10 read 2026-08-15] [§13#25 read 2026-08-15] [§13#26 read 2026-08-15] | Do not invent production custody |
| Wallet-native controls | MetaMask Agent Wallet | Protocol policies, simulation, threat scanning, MEV protection, and human escalation [§13#11 read 2026-08-15] | Policy plus simulation is moving into wallet UX |
| Institutional transaction guard | Hypernative Transaction Guard | Pre-sign simulation, custom policy, intent verification (inference), approval workflows, and audit records [§13#13 read 2026-08-15] [§13#27 read 2026-08-16] [§13#28 read 2026-08-16] | Direct substitute for an inline transaction guard |
| Simulation and threat APIs | Blockaid | Decoded effects, execution simulation, and known-threat detection [§13#14 read 2026-08-15] | Integrate or compare against these primitives |
| Simulation APIs | Tenderly | Decoded effects and execution simulation [§13#15 read 2026-08-15] | Integrate or compare against these primitives |
| Signing metadata | ERC-7730 | Chain/address-bound clear-signing metadata for calldata and typed messages [§13#16 read 2026-08-15] | Consume the standard; do not invent a parallel manifest without evidence of a gap |

*Certified by John at the Gate 5 session, 2026-08-16 (D-038).* Every entry in "Existing capability" is quoted or closely paraphrased from its cited source as read on the marked date; clauses marked `(inference)` are not. **The "Consequence for Sentinel" column is Sentinel's own inference throughout** — no vendor documents what its product implies for this project.

The honest market thesis is therefore:

> Sentinel may be valuable as a provider-neutral evaluation and evidence layer, but it has not yet proved a product gap beyond the strongest current wallet and transaction-guard controls.

### 2.1 First User and Buyer

Primary user:

> A security-minded agent, DeFi, or platform engineer preparing an EVM-capable workflow for mainnet using existing wallet infrastructure.

Economic buyer:

> A founder, CTO, head of engineering, or security lead accountable for release.

Likely trigger:

- Mainnet launch.
- Expansion of agent permissions.
- Prompt-injection or policy-bypass finding.
- Near miss.
- Customer diligence.
- Audit finding.

Initial offer:

> A fixed-scope agent-action security assessment plus a CI or shadow-mode regression harness.

Starting outside the live signer path reduces custody exposure and signer-path liability, provided Sentinel never handles production keys or signing authority. It also tests whether teams value recurring monitoring or only a one-time assessment.

---

## 3. System Thesis, Trust Boundary, and Invariants

The model may draft a typed mandate, but a human owner must inspect and sign it. The agent may propose an action, but it cannot authorize or execute that action through an alternate path.

The v0.2 control statement is:

> The agent proposes. Sentinel evaluates. The isolated signer attests. SentinelVault enforces.

Vendor-neutral means that the schemas, evaluator, fixtures, and receipts are provider-neutral. v0.2 implements only SentinelVault. Safe and wallet-provider adapters are post-MVP work.

### 3.1 Trust Classification

Trusted for the lab:

- One EOA owner key.
- Minimal testnet-only SentinelVault.
- Canonical schema encoders and hashes.
- Active mandate and policy state stored by the vault.
- Deterministic policy and conformance evaluator.
- Local Anvil EVM and effect extractor.
- Isolated Sentinel authorization signer.

Untrusted:

- Agent.
- Model output.
- Natural-language descriptions.
- Remote endpoints.
- Retrieved documents.
- Agent-supplied parameter or purpose claims.
- Remote RPC state until anchored and checked.

Context-only:

- Documentation.
- Audit reports.
- Source-verification status.
- Clear-signing metadata.
- AI explanations.

The signer exposes no generic sign-bytes method. It independently recomputes the canonical action hash, checks the current mandate and policy, confirms an allow verdict, and signs only the defined receipt payload.

### 3.2 Flow

1. AI drafts a typed mandate from a user instruction.
2. The owner inspects and signs the mandate payload.
3. The owner activates the mandate hash in SentinelVault.
4. The owner activates a canonical policy hash.
5. The agent proposes an exact EVM call.
6. Sentinel decodes the supported call schema.
7. Deterministic policy checks run.
8. A local Anvil fork is anchored to a recorded block hash.
9. Sentinel snapshots, executes, inspects supported pre/post effects and call traces, then reverts the snapshot.
10. The conformance engine compares mandate, policy, action, and effects.
11. Sentinel issues a signed allow, block, or review receipt.
12. SentinelVault executes only with a valid allow receipt, or with a separately signed owner override attached to a review receipt.
13. The vault consumes the action nonce before the external call.
14. The complete evidence bundle is retained offchain and its canonical hash is recorded in the receipt.

### 3.3 Security Invariants

1. Every agent-reachable execution path passes through SentinelVault.
2. Human-only activation, revocation, override, pause, recovery, and signer rotation are separately authenticated, unavailable to the agent, and logged.
3. The owner signs a typed mandate payload, not raw natural language.
4. Authorization binds the exact chain, vault, action nonce, target, native value, operation, calldata hash, mandate hash, policy hash, and deadline.
5. Any mutation to a bound field invalidates authorization.
6. The automatic path accepts only a current, unexpired allow receipt from the active signer.
7. A review path requires both the signed review receipt and a separate owner-signed OverrideAuthorization for that exact action. **A block cannot be overridden directly.** *Amended 2026-08-15 (D-026): the remedy for a block depends on what failed.* A **conformance** block — the action does not match the signed mandate — requires a new mandate or policy. An **executability** block — the vault is paused, the signer has been rotated, the action's nonce is not the vault's, the deadline has passed, or the value exceeds the vault's own hard cap — is cleared by changing the vault state or the action, and needs no new mandate. Both are non-overridable; only the remedy differs. The previous text said a block "requires a new mandate or policy" without qualification, which is true of the first kind and false of the second, and three independent labellers converged on the gap. The executability class is enumerated in §5.7 and mirrors the isolated signer's EXECUTABILITY severity tier.
8. Missing or conflicting state, unsupported calls, undecodable calldata, stale mandate or policy, code-identity mismatch, or critical dependency failure never produces automatic allow. *Clarified 2026-08-15 (D-030): this is a FLOOR, not a verdict — it rules out ALLOW and each listed condition is classified separately.* Code-identity mismatch and undecodable calldata are evidence gaps following `failureMode` (D-015, D-028); a reverting simulation is a failed rule (D-021); pause, nonce, deadline and the vault's hard cap are the EXECUTABILITY class (D-026); and **conflicting state is a failed rule and blocks** — where the operands are known and the comparison fails, nothing is unestablished, and describing a determinate contradiction as missing information would be the wrong reading. Recorded caveat: a vault reaching a self-contradictory state means something upstream already went wrong, so this is arguably a system inconsistency rather than a property of the action; see D-030 for the objection and the condition that would reopen it.
9. A single monotonically increasing action nonce stored in SentinelVault prevents receipt and override replay and is consumed before the external call.
10. Owner-only mandate revocation, policy activation, pause, recovery, and signer rotation remain outside agent authority.
11. Unsupported top-level operations and unexpected internal calls are denied or reviewed by default.
12. A receipt signature authenticates the receipt; replay prevention comes from vault nonce consumption. An evidence hash proves retained bytes have not changed, not that the evidence was complete or correct.

Required Foundry invariants:

- Every executed agent action used the active mandate, active policy, current signer, current action nonce, and valid time window.
- No action nonce executes twice.
- Mutating any bound field invalidates the credential.
- Block receipts never execute.
- Review receipts never execute without a matching owner override.
- Paused execution always fails.
- Unauthorized callers cannot activate or revoke mandates, change policy, rotate the signer, or recover funds.
- Reentrancy cannot reuse an action nonce.

---

## 4. Narrow MVP

The MVP proves one mechanism:

> An untrusted agent cannot execute a supported EVM action unless SentinelVault verifies a credential bound to the active human-signed mandate, active policy, exact call, and current action nonce.

Scope:

- One local Anvil environment as the reproducible baseline.
- Optional Base Sepolia deployment.
- One testnet-only SentinelVault with capped test funds.
- One payable DemoPay contract.
- One DemoERC20 contract used only for the approval-attack fixture.
- One top-level EVM operation type: CALL.
- Two decoded top-level call schemas: DemoPay purchase and DemoERC20 approve.
- No proxy targets on the automatic-allow path.
- One evidence dashboard.

SentinelVault is an execution harness, not a production wallet. Its hard onchain backstops bound the SHAPE of each action — supported targets and selectors, the calldata hash, the chain and vault binding, nonce ordering, and a PER-ACTION native-value ceiling — and allow the owner to pause, revoke or recover. **They do not bound aggregate loss or execution rate, and this sentence used to imply otherwise (corrected 2026-08-18, D-053(a)).** `maxNativeValueWei` is compared once per action and no cumulative or rate-limited bound exists anywhere in the contracts; and because `nonReentrant` stops nesting rather than repetition, a relayer can call `executeWithReceipt` repeatedly inside ONE transaction — measured, 100 valid receipts at exactly the cap drain a funded vault to zero atomically, with the block number and timestamp unchanged. A compromised evaluator or signer issuing sequential nonces therefore drains the vault in a single transaction, and PAUSE protects only before execution begins or between transactions. **This is an explicitly accepted v1 boundary of the testnet lab, not an open defect:** the lab limits worst-case blast radius to testnet funds, and it does not limit how fast they leave.

### 4.1 DemoPay

DemoPay accepts test ETH and exposes a purchase function with:

- Resource identifier.
- Beneficiary.
- Duration.
- Recurring flag.

It writes inspectable entitlement state, such as entitlement expiry by beneficiary and resource. It makes no external calls in v0.2.

This keeps the normal purchase to one payable CALL. DemoERC20 is separate and exists only to demonstrate approval detection.

### 4.2 Four Demonstration Cases

#### Case 1: Exact Mandate — Allow

The owner activates a mandate for one purchase of weather-basic-24h from the pinned DemoPay code hash, for the owner as beneficiary, with recurrence disabled and no more than the specified test-ETH amount.

The agent proposes the expected call. Calldata, native value, policy, and simulated entitlement state conform.

Expected result: allow receipt and execution.

#### Case 2: Real Prompt Injection — Block

A malicious service document directs the agent to call DemoERC20 approve for an attacker and maximum allowance. The agent genuinely proposes it.

Sentinel evaluates the decoded call and its simulated effects, never the agent's account of what the call means.

**Amended by D-019 (2026-08-15).** This sentence previously read "Sentinel derives the selector and parameters from calldata rather than trusting the agent's description", which was written before the proposal seam existed and does not survive contact with it. The agent under test emits typed parameter *claims* — a target, a function signature, and arguments as strings — not calldata. Under D-019 Sentinel encodes the calldata from those claims, so decoding it back recovers them by construction: that round trip is a check on Sentinel's own transcriber, not corroboration of the agent. The claim as amended is the one the mechanism actually supports, and it is the one that carries the case: the agent's `rationale` calls the attacker "the settlement relayer" and the unlimited approval "a required one-time setup before purchasing the weather-basic-24h feed", and none of it reaches a check, a reason code, a bound field, or the evidence bundle. The block comes from the decoded spender and amount against the mandate's allowance ceiling. The stronger, literal reading of the original sentence remains available at the cost of re-recording the D-007 fixtures; D-019 records why that was not taken in v1.

Expected result: deterministic block. No executable receipt exists.

#### Case 3: Mechanically Valid but Wrong Purpose — Block

Poisoned context causes the agent to request premium-monthly or enable recurrence instead of weather-basic-24h. The target and native value fit a representative basic wallet policy, and execution succeeds, but decoded parameters and simulated entitlement state violate the signed mandate.

Expected result: mandate-conformance block.

This case proves the Sentinel mechanism, not market superiority. Strong current products may express equivalent parameter or completion constraints. Incremental differentiation must be established through fair baselines and provider tests.

#### Case 4: Evidence Uncertainty — Review

The target code hash changes, the target appears to be a proxy, the anchored RPC state conflicts, or simulation is unavailable.

Sentinel does not label the target malicious. It reports insufficient evidence for automatic approval.

Expected result: review. Execution requires a separately signed exact-action owner override or a new mandate.

---

## 5. Typed Contracts, Policy, and Supported Claims

EIP-712 provides typed, domain-separated signing. SentinelVault must separately enforce nonce consumption, validity windows, active hashes, and signer identity.

Signatures are envelope fields and are excluded from the payload hashes they sign.

### 5.1 MandatePayload

    schemaVersion
    mandateId
    principal
    vault
    chainId
    target
    targetCodeHash
    selector
    maxNativeValueWei
    purposeKind
    resourceId
    beneficiary
    durationSeconds
    recurringAllowed
    validAfter
    validUntil
    policyHash

SignedMandate contains MandatePayload plus ownerSignature.

The MVP supports one EOA owner. The principal must equal the current vault owner when the mandate is activated. EIP-1271 owners are out of scope.

### 5.2 PolicyPayload

    schemaVersion
    policyVersion
    vault
    chainId
    allowedOperation
    allowedTargetsHash
    allowedSelectorsHash
    maxNativeValueWei
    maxAllowanceIncreaseBaseUnits
    allowedCallGraphHash
    validAfter
    validUntil
    failureMode

The owner activates the canonical policy hash in SentinelVault.

Mandate and policy constraints are intersected. Any failed rule blocks. Any unknown required check is governed by `failureMode`: it reviews under REVIEW and blocks under FAIL_CLOSED. Automatic allow requires every required check to pass. **A failed rule takes precedence over an unresolved check (D-029):** where both are present the verdict is BLOCK, whatever `failureMode` says. An unresolved check is an absence of information and cannot undo a positive finding — learning that something else is unknown does not make a known violation less certain.

*Amended 2026-08-15 (D-021).* A **reverting simulation is a failed rule** and therefore blocks; it is not an "unknown required check" and does not follow `failureMode`. The reasoning: a revert is a determinate observed fact — the simulation succeeded in reporting that the call does not execute — so nothing about it is unknown. The consequence is stated because it is sharp and was argued against: §3.3(7) makes a block remediable only by a new mandate or policy, so an action that reverts for a trivially correctable reason costs a new mandate rather than a corrected re-proposal.

*Amended 2026-07-28 (D-015).* This sentence previously read "Any unknown required check reviews", unconditionally, which contradicted the `failureMode` field listed above it and would have made that field nearly meaningless. The amendment records the reading the implementation follows. One consequence is worth stating here rather than leaving to be rediscovered: because §4.2 Case 4 expects a review receipt, the Case 4 policy must set `failureMode = REVIEW`; the identical evidence uncertainty blocks under FAIL_CLOSED, which is a legitimate configuration and a different demonstration.

### 5.3 ActionPayload

    schemaVersion
    chainId
    vault
    actionNonce
    target
    valueWei
    dataHash
    operation
    mandateHash
    policyHash
    deadline

The complete calldata accompanies the payload. SentinelVault recomputes dataHash.

### 5.4 DecisionReceiptPayload

    schemaVersion
    decisionId
    actionHash
    mandateHash
    policyHash
    verdict
    reasonCodesHash
    evidenceHash
    simulationBlockNumber
    simulationBlockHash
    issuedAt
    expiresAt
    signer

SignedDecisionReceipt contains DecisionReceiptPayload plus sentinelSignature.

Only an allow receipt is executable on the automatic path.

*Added 2026-08-15 (D-022).* **`reasonCodesHash` is defined as follows, because §5.4 previously named the field and nothing else, leaving it unverifiable by any independent party.**

The committed set is the **union of the evaluator's reason codes and the isolated signer's own findings** — not the evaluator's codes alone. This is the part a reader would not guess, and it is deliberate: the signer appends what it found so the receipt commits to the whole record rather than to the evaluator's half of it.

That set is de-duplicated (exact match, not case-folded), sorted in ascending byte order of the identifier, joined with a single `\n` (U+000A) between elements, encoded UTF-8, and hashed with keccak256. The empty set hashes to `keccak256("")` = `0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470`.

**A verifier hashes the `reasonCodes` array it is given, verbatim.** It does not recompute the union. The union describes how the signer *builds* the set, not what a verifier *recomputes* — and the distinction is load-bearing: a verifier that re-unions the published list with `signerFindings` would silently repair the deletion of any code that appears in both, and the deletion would go undetected. A verifier MUST additionally assert `signerFindings ⊆ reasonCodes`, which catches that deletion as a subset violation rather than repairing it.

**Identifier grammar.** Each identifier must match, **end to end**:

    [A-Za-z0-9_.:-]{1,64}

Use an anchoring construct that means end-of-input in your language — `\A…\z`, or Python's `re.fullmatch`. **Do not write `^…$`.** In Python `$` also matches immediately before a trailing newline, so `"EVAL_OK\n"` passes; in Ruby `^` and `$` are line anchors unconditionally, so `"EVIL\nINJECTED"` passes. Either admits `\n` into an identifier, and because `\n` is also the delimiter, `{"EVIL\nINJECTED"}` and `{"EVIL", "INJECTED"}` then produce the byte-identical preimage and therefore **the same `reasonCodesHash`** — one receipt committing to two different sets. The grammar is the only thing preventing that collision, so it has to hold in the implementer's language rather than in the abstract.

A verifier MUST re-validate every identifier against this grammar and **reject rather than sanitise** on failure. Enforcement at the signer's RPC boundary does not help a third party, who is outside that boundary by construction.

The receipt commits to a hash, not to the list, so **the full ordered list travels alongside the receipt** and a verifier must be given it. A signed receipt presented without its `reasonCodes` list MUST fail verification rather than skip the check: its signature and evidence can still be checked, but its stated reasons cannot, and reporting that as a pass would misdescribe what was verified.

### 5.5 OverrideAuthorizationPayload

    schemaVersion
    reviewReceiptHash
    actionHash
    mandateHash
    policyHash
    actionNonce
    reasonHash
    issuedAt
    expiresAt

SignedOverrideAuthorization contains OverrideAuthorizationPayload plus ownerSignature.

The vault accepts an override only with the matching signed review receipt. A block receipt cannot be overridden.

### 5.5.1 RefusalRecord (normative)

*Added 2026-08-16 (D-043). **This section publishes an artifact the signer has produced since D-012 and the specification had never described.** An independent verifier built from this document — which is what D-010 requires — therefore could not establish a refusal, and the D-010 CLI shipped certifying an unsigned `{"refused": true}` claim as a PASS. The implementation anticipated this precisely: the comment beside `refusalDigest` reads "the D-010 verifier will need to check these, and a refusal nobody else can verify is not evidence." It was written down in the one place the verifier is not allowed to read. **The general lesson, and the reason this correction is worth its own note: a requirement ratified in the decision log is not a requirement an implementer can build. Only the published document is.***

D-012 requires that a refusal leave a recorded artifact — otherwise "the signer refused" and "the signer was never asked" are indistinguishable, and a party presenting an evidence bundle can suppress a receipt and call it a refusal.

    schemaVersion
    chainId
    vault
    actionHash
    evidenceHash
    requestedVerdict
    reasonCodesHash
    refusedAt
    signer

`SignedRefusalRecord` contains RefusalRecord plus a signature over the digest below.

*Amended 2026-08-16, same day, after an independent implementation built from this section was pointed at a real signed refusal (A-042). **Everything this section STATED matched on the first run — the field list, the order, the domain tag, the preimage bytes, and the signature construction. What it did not state is what diverged**, which is the most useful result this section could have produced and the reason D-010 exists.*

**The envelope, which the first version left entirely unspecified.** A refusal is presented in `receipt.json` in place of a §5.4 receipt — a bundle carries a receipt **or** a refusal, never both — under the key `refusalRecord`, whose value is an object with three members:

    { "refused": true,
      "refusalRecord": { "record": <RefusalRecord>, "signature": <65-byte hex>,
                         "reasonCodes": [ <identifier>, ... ] } }

The signature member is named `signature`. **The first version of this section said "plus `signerSignature`" and named no file, key, or nesting depth; an implementer guessed three shapes and none was right.** `reasonCodes` is the ordered set `reasonCodesHash` commits to, and must be present for the same reason §5.4 carries it: without it a third party cannot recompute the hash.

**The signature is raw ECDSA over the 32-byte digest — no EIP-191 prefix, no EIP-712 domain.** Recovery yields the signer's address, and `s` must be canonical (low-s, per EIP-2) as for every other signature in this document.

**`signer` is self-declared and must not be trusted.** Anyone can mint a record naming their own key and satisfy every rule above. **A verifier MUST compare the recovered address against the deployment's known Sentinel signer** — the `signerAddress` a §5.6 bundle's domain carries — or the whole record is forgeable.

**`actionHash` DOES NOT ATTRIBUTE A REFUSAL ON ITS OWN, and this is not theoretical:** the same action can legitimately be decided twice — evaluated to ALLOW on an unpaused vault, then refused when the vault's state changed — and both artifacts then name a byte-identical `actionHash`. The shipped `refusal-vault-paused` and `case-1-allow` samples are exactly that pair. **`evidenceHash` is what binds a refusal to the bundle it accompanies, and a verifier MUST check it**; checking `actionHash` alone lets a genuine signed refusal be moved onto a different bundle.

**Correction to the injectivity argument.** The first version credited injectivity to the charsets alone. Precisely: **fixed arity** — always nine fields — is what prevents a malformed record colliding with a well-formed one, and **the charsets** are what prevent two malformed records colliding with each other. Both are load-bearing. Without the charset rules, `requestedVerdict = "BLOCK\nSMUGGLED"` with `reasonCodesHash = "H"` joins to the same preimage as `requestedVerdict = "BLOCK"` with `reasonCodesHash = "SMUGGLED\nH"`, so one signature attests to two distinct records — the same delimiter-smuggling D-022 closed for reason codes, in a second place. **A verifier MUST validate the charsets before hashing, not merely rely on the join.**

**Known limits, stated rather than left to be discovered:** a refusal carries no expiry, so it is valid indefinitely; `schemaVersion` is cross-checked against nothing; and any human-readable `refusalReason` presented alongside is **outside the signature** — a presenter may rewrite it without invalidating anything, so it is not evidence.

**This record is NOT an EIP-712 typed structure, and the difference is deliberate.** Its digest is a domain-tagged, newline-joined string preimage:

    keccak256(utf8(
        "sentinel.refusal.v0.2" ‖ "\n" ‖
        schemaVersion ‖ "\n" ‖ chainId ‖ "\n" ‖ vault ‖ "\n" ‖
        actionHash ‖ "\n" ‖ evidenceHash ‖ "\n" ‖ requestedVerdict ‖ "\n" ‖
        reasonCodesHash ‖ "\n" ‖ refusedAt ‖ "\n" ‖ signer
    ))

`schemaVersion`, `chainId` and `refusedAt` are decimal digits; `vault` and `signer` are lowercase `0x` addresses; the three hashes are lowercase `0x` 32-byte hex; `requestedVerdict` is a §5.9 verdict NAME. **Field order is part of the format.** The encoding is injective because every field is a fixed charset that cannot contain the newline delimiter — which is what makes a joined preimage safe here where it would not be for free-form text.

`reasonCodesHash` uses the same encoding as a receipt's (§5.4): identifiers sorted ascending by bytes, joined with a single `\n`, UTF-8, keccak256.

**A refusal is attributable or it is not issued.** Where a request is too malformed to name an action — a payload contradicting its own calldata — the signer emits no record rather than one it cannot honestly attribute, and a verifier must treat an absent record as an unestablished refusal rather than an established one.

### 5.9 Enumerations (normative)

*Added 2026-08-15 (D-024), because all three of these were undocumented and the document's own prose ordering implies the wrong values for the first.*

    Verdict:      BLOCK = 0,        REVIEW = 1,   ALLOW = 2
    FailureMode:  FAIL_CLOSED = 0,  REVIEW = 1
    Operation:    CALL = 0,         DELEGATECALL = 1 (unsupported),  CREATE = 2 (unsupported)

All three are `uint8` and all three are **fail-closed by construction**: the zero value is the most restrictive member, so an uninitialised, truncated, or defaulted field denies rather than permits.

> **Warning: the `Verdict` numbering is the REVERSE of the order this document presents the verdicts in.** §4.2 introduces the demonstration cases allow-first; §5.4 and §5.7 say "allow, block, or review". A reader inferring the enum from that prose ordering gets `ALLOW = 0` — precisely inverted, on the field §5.4 makes security-critical ("Only an allow receipt is executable on the automatic path"). The prose ordering is narrative, chosen so a reader meets the mechanism through the conforming case; the numbering is fail-closed. Both are deliberate and they do not agree.
>
> This inversion is worth stating explicitly because **it is the one error in §5 that fails silently in both directions.** `verdict` is a `uint8` inside the signed struct, so a reader's *interpretation* of it does not affect the encoded bytes or the digest. A verifier holding the enum backwards passes the signature check, passes the evidence hash, confirms the mandate binding — and then reports the opposite verdict. Nothing in the cryptography can surface it.

`FailureMode` governs unresolved checks (§5.2 as amended by D-015), and `Operation` is the §5.3 `operation` field and the §5.2 `allowedOperation` field. §4 fixes v1 at one supported top-level operation, CALL; the other two members exist so an unsupported operation has a defined encoding rather than an undefined one, and neither ever executes.

---

### 5.8 EIP-712 Type Strings (normative)

*Added 2026-08-15 (D-023), after an independent reimplementation established that §5 as written was not sufficient to build a verifier.*

Every payload hash named in §5 — `mandateHash`, `policyHash`, `actionHash`, `reviewReceiptHash` — is the EIP-712 `hashStruct` of the corresponding payload: `keccak256(typeHash ‖ abi.encode(fields in the order listed))`. These are **not** RFC 8785 JSON hashes; RFC 8785 applies only to the EvidenceBundle (§5.6). The document's use of the word "canonical" for both is a known source of confusion and is why this subsection exists.

They are **bare `hashStruct` values**: no `\x19\x01` prefix and no domain separator is applied. Chain and vault binding for these hashes therefore comes solely from the `chainId` and `vault` members of the payloads themselves. The full EIP-712 digest — `keccak256("\x19\x01" ‖ domainSeparator ‖ hashStruct)` — is applied only where a signature is produced.

The type strings are **normative and byte-exact**. A single differing character changes the typehash, the digest, and the recovered address.

    EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)

    MandatePayload(uint16 schemaVersion,bytes32 mandateId,address principal,address vault,uint256 chainId,address target,bytes32 targetCodeHash,bytes4 selector,uint256 maxNativeValueWei,bytes32 purposeKind,bytes32 resourceId,address beneficiary,uint64 durationSeconds,bool recurringAllowed,uint64 validAfter,uint64 validUntil,bytes32 policyHash)

    PolicyPayload(uint16 schemaVersion,uint32 policyVersion,address vault,uint256 chainId,uint8 allowedOperation,bytes32 allowedTargetsHash,bytes32 allowedSelectorsHash,uint256 maxNativeValueWei,uint256 maxAllowanceIncreaseBaseUnits,bytes32 allowedCallGraphHash,uint64 validAfter,uint64 validUntil,uint8 failureMode)

    ActionPayload(uint16 schemaVersion,uint256 chainId,address vault,uint256 actionNonce,address target,uint256 valueWei,bytes32 dataHash,uint8 operation,bytes32 mandateHash,bytes32 policyHash,uint64 deadline)

    DecisionReceiptPayload(uint16 schemaVersion,bytes32 decisionId,bytes32 actionHash,bytes32 mandateHash,bytes32 policyHash,uint8 verdict,bytes32 reasonCodesHash,bytes32 evidenceHash,uint256 simulationBlockNumber,bytes32 simulationBlockHash,uint64 issuedAt,uint64 expiresAt,address signer)

    OverrideAuthorizationPayload(uint16 schemaVersion,bytes32 reviewReceiptHash,bytes32 actionHash,bytes32 mandateHash,bytes32 policyHash,uint256 actionNonce,bytes32 reasonHash,uint64 issuedAt,uint64 expiresAt)

The domain uses no `salt`. `EIP712Domain` field values for a deployment are `name = "Sentinel"`, `version = "0.2"`, and the deployment's own `chainId` and `verifyingContract` (the SentinelVault address).

**Warnings a reimplementer needs, each of which cost the independent verifier real time:**

- **`uintN` widths do not change the encoded data.** Every `uintN` occupies one left-padded 32-byte word, so `uint16 schemaVersion` and `uint256 schemaVersion` encode identically. The width changes only the type string, and therefore the digest. **A width mismatch is indistinguishable from an invalid signature** — the verifier reports a signer mismatch and an operator reasonably concludes the receipt is forged. The widths above are not uniform: `schemaVersion` is `uint16` while `policyVersion` is `uint32`; `actionNonce` is `uint256` while `deadline` is `uint64`.
- **`bytesN` is RIGHT-padded** to 32 bytes, while `uintN` and `address` are LEFT-padded. `selector` is `bytes4`, not `bytes32` and not a string.
- **ActionPayload's accompanying `callData` is not a member of the signed struct.** It travels alongside and is bound only through `dataHash = keccak256(callData)`.
- **`signer` is a member of the DecisionReceiptPayload struct as well as the recovered address.** This is deliberate: the signature commits to the claimed signer rather than merely recovering some address, so a swapped `signer` field fails rather than quietly recovering another key.
- **`keccak256` here means the EVM's keccak256** — original Keccak with `pad10*1` domain byte `0x01` — **not** FIPS-202 SHA3-256 (`0x06`). The two produce different digests for every input and the same output length. Python's standard library ships `sha3_256` and no keccak; reaching for it produces a plausible digest that is wrong for every input.

**Known asymmetry, recorded rather than resolved.** `MandatePayload`, `PolicyPayload` and `ActionPayload` each carry `chainId` and `vault`. `DecisionReceiptPayload` and `OverrideAuthorizationPayload` carry neither. The receipt's chain and contract binding lives entirely in the EIP-712 domain separator, which is what domain separation is for — but it has an operational consequence: **a receipt is not self-describing.** A deployment must publish its domain field values alongside the SentinelVault address, and a receipt transmitted outside the lab must be accompanied by them. A verifier not told the domain cannot verify a receipt, and one that guesses will report a valid receipt as forged. The override carries chain and vault only transitively, through the `mandateHash` and `policyHash` it references; whether that is sufficient is being measured rather than assumed (D-023).

---

### 5.6 EvidenceBundle

    normalizedAction
    decodedSelectorAndParameters
    policyChecks
    expectedEffects
    observedPreState
    observedPostState
    nativeBalanceDeltas
    allowanceDeltas
    internalCallTrace
    targetCodeIdentity
    citedContextReferences
    unresolvedChecks
    aiExplanation

EvidenceBundle uses RFC 8785 JSON canonicalization and keccak256 for evidenceHash.

### 5.7 Supported Checks and Effects

Supported deterministic checks:

- Active owner, mandate, policy, and signer.
- Exact chain, vault, nonce, target, operation, value, selector, and code hash. *Qualified 2026-08-15 (D-027): the **code-hash** comparison is an EVIDENCE check, not a failed rule.* Its failure is UNRESOLVED and follows `failureMode`, per D-015 and §4.2 Case 4 — "Sentinel does not label the target malicious. It reports insufficient evidence for automatic approval." Listing it beside the exact-equality checks read against that ruling, which is what this qualifier removes. The other items in this line are equality checks whose failure is a failed rule.
- Native-value ceiling.
- DemoERC20 approval parameters and allowance ceiling.
- DemoPay resource, beneficiary, duration, and recurrence.

*Amended 2026-08-15 (D-020).* These four are compared for **equality**, not as ceilings. Only fields named `max*` — `maxNativeValueWei`, `maxAllowanceIncreaseBaseUnits` — are ceilings the action may come in under. The previous text said the fields were "checked" without stating the relation, which left open whether a purchase for less duration than the mandate authorises conforms. It does not. The reasoning is recorded because it is not the obvious one: DemoPay accepts any non-zero payment and grants exactly the duration requested, so price does not scale with duration — a shorter duration at the same price is the owner paying in full for less access, and a longer one is the owner receiving more than they authorised. Neither direction is benign.
- Mandate and receipt validity.
- Allowed top-level and internal call graph.

*Qualified 2026-08-15 (D-025).* In v1 this check enforces an **empty** call graph, which is the conforming graph for both supported schemas — neither DemoPay nor DemoERC20 makes an internal call. `PolicyPayload.allowedCallGraphHash` (§5.2) is **reserved and not yet consulted**: a policy declaring any other call graph has no effect in v1. Stated rather than left implicit because a declared-but-unenforced field is one an owner could reasonably believe they had constrained something with. The consequence for evaluation is recorded too: §7.1's unexpected-internal-call class cannot be driven to a positive case in v1, so no corpus fixture demonstrates it and the §7.3 ablation does not count it as a detection.

*Added 2026-08-15 (D-026) — the EXECUTABILITY class.* Of the checks above, these say the receipt could not be used rather than that the action violates the mandate: **vault not paused, action nonce is the vault's current nonce, action deadline not passed, and value within the vault's own hard cap.** They block, they are not overridable, and per §3.3(7) as amended their remedy is a change of vault state or of the action — never a new mandate. This mirrors the isolated signer's EXECUTABILITY severity tier (A-011, D-012), which has always drawn this line; the classification simply did not exist in the specification or the conformance engine until now. Note that the vault's hard cap is a THIRD ceiling, independent of the mandate-and-policy intersection §5.2 describes.

*Added 2026-08-15 (D-028) — undecodable calldata is an evidence gap.* Calldata that does not decode under a supported schema is an UNRESOLVED check and follows `failureMode`: it reviews under REVIEW and blocks under FAIL_CLOSED. §3.3(8) is satisfied either way, since neither produces an automatic allow. **An apparent asymmetry is worth naming so it is not read as inconsistency:** a call so malformed it carries no usable selector will usually also fail a determinate check — the selector is not on the vault's allowlist — and therefore blocks, while a call that is merely non-canonical but still executable reviews. Those are two different reasons that happen to co-occur in one fixture class, not undecodability behaving two ways. The reviewable case is real and deliberate: §4.2's override path exists precisely for an action the owner recognises and Sentinel cannot parse. Note the one place this bites hardest — trailing bytes past the declared arguments are the single case where Sentinel is stricter than the EVM, so under REVIEW an owner may override something Sentinel deliberately refused to parse.

Supported effects:

- Native balance changes.
- DemoERC20 allowance changes.
- Revert or success.
- Call trace.
- DemoPay entitlement pre/post state.
- Emitted events as supporting evidence.

An event alone is not proof of entitlement; conformance checks the resulting contract state.

#### 5.7.1 Check coverage (auditable; the identifiers are not normative)

*Added 2026-08-15 (D-031), after an independent labeller working only from this document noticed that §5.7's prose never names the mandate-to-active-policy binding, and drew the consequence itself: an evaluator built from §5.7 alone omits it, and the wrong-policy fixture then ALLOWs. Measuring the gap rather than assuming its size found **eleven** of the engine's forty-one checks with no home in the prose above, including all three binding checks §3.3(4) and §3.3(5) rest on.*

**What this list is and is not.** The prose above is normative — it says what is checked and why. This table exists so the prose can be AUDITED for completeness against a working implementation, and its identifiers are deliberately **not** normative: a reimplementer should derive behaviour from the descriptions, not transcribe names. That distinction is the whole value D-010 demonstrated — an independent implementer failing against a written schema is what reveals where the schema is thin, and a copyable identifier list would replace that signal with a transcription exercise.

`scripts/check-eval-codes.sh` fails the project gate if a check exists in the engine and not here. **It asserts COVERAGE, not correctness** — that someone declared where a check belongs, not that the description is right. That is weaker than the §5.8 type-string guard, which compares two byte-exact strings, and the difference is stated rather than glossed.

**Binding and activation** — §3.3(4), §3.3(5), §5.1:
`EVAL_CHAIN_BOUND`, `EVAL_VAULT_BOUND`, `EVAL_TARGET_BOUND`, `EVAL_SELECTOR_BOUND`, `EVAL_NONCE_CURRENT`, `EVAL_CALLDATA_BINDING` (the presented bytes hash to the action's `dataHash`), `EVAL_ACTION_BINDS_MANDATE_AND_POLICY` (the action names the hashes the vault reports active), `EVAL_MANDATE_BINDS_POLICY` (the mandate's embedded `policyHash` is the active policy), `EVAL_MANDATE_ACTIVE`, `EVAL_POLICY_ACTIVE`, `EVAL_MANDATE_PRINCIPAL_IS_OWNER`.

**Windows and deadlines:** `EVAL_MANDATE_WINDOW`, `EVAL_POLICY_WINDOW`, `EVAL_ACTION_DEADLINE`.

**Ceilings, intersected per §5.2:** `EVAL_VALUE_WITHIN_MANDATE`, `EVAL_VALUE_WITHIN_POLICY`, `EVAL_VALUE_WITHIN_VAULT_CAP` (the vault's own constructor cap — a third ceiling, outside the mandate-and-policy intersection).

**Operation and vault state:** `EVAL_OPERATION_SUPPORTED`, `EVAL_POLICY_OPERATION`, `EVAL_VAULT_NOT_PAUSED`.

**Decoded parameters against the mandate:** `EVAL_PURCHASE_RESOURCE`, `EVAL_PURCHASE_BENEFICIARY`, `EVAL_PURCHASE_DURATION`, `EVAL_PURCHASE_RECURRENCE`, `EVAL_APPROVAL_SPENDER`, `EVAL_APPROVAL_CEILING`, `EVAL_CALLDATA_UNDECODABLE` (an evidence gap per D-028).

**Simulated effects:** `EVAL_SIMULATION_SUCCEEDS` (a revert is a failed rule per D-021), `EVAL_NATIVE_DELTA_MATCHES_VALUE`, `EVAL_ALLOWANCE_EFFECT_WITHIN_CEILING`, `EVAL_ENTITLEMENT_ADVANCED`, `EVAL_ENTITLEMENT_RECURRENCE`, `EVAL_CALL_GRAPH_EXPECTED` (enforces an empty graph; `allowedCallGraphHash` is reserved per D-025), `EVAL_TARGET_CODE_IDENTITY` (an evidence gap per D-015/D-027).

**Evidence that did not arrive** — each is UNRESOLVED and travels rather than being inferred away (§3.3(8), A-019(e)): `EVAL_SIMULATION_UNAVAILABLE`, `EVAL_NATIVE_DELTA_UNOBSERVED`, `EVAL_ALLOWANCE_EFFECT_UNOBSERVED`, `EVAL_ENTITLEMENT_UNOBSERVED`, `EVAL_SIM_CALL_TRACE_UNAVAILABLE`, `EVAL_SIM_STOP_IMPERSONATION_FAILED`, `EVAL_SIM_UNRECOGNISED`.

Explicitly unsupported:

- Proxy targets on automatic allow.
- Delegatecall.
- Contract creation.
- Fallback-only calls.
- Multicall and arbitrary batching.
- DEX, Permit2, bridge, governance, and cross-chain actions.
- MEV and transaction-ordering guarantees.
- General bytecode semantics.

---

## 6. AI and Context Scope

AI is outside the executable verdict in v0.2.

AI may:

- Draft a typed mandate for owner review.
- Explain decoded parameters and supported effects.
- Cite missing or contradictory context.
- Produce a non-authoritative review memo.

AI may not:

- Activate or sign a mandate.
- Hold execution or authorization credentials.
- Change policy results.
- Create, restore, or downgrade an allow decision.
- Claim arbitrary contract safety.

The executable allow, block, or review verdict is deterministic. AI quality is evaluated separately from security detection.

A vector database is unnecessary. Use a small, versioned context pack and established ERC-7730 metadata where useful. Add RAG only if a later experiment identifies a measured failure that retrieval solves.

Document mismatch in v0.2 means a mechanically observable conflict such as wrong chain, address, selector, ABI hash, or runtime code hash. Source verification establishes correspondence between published source or build metadata and deployed bytecode; it does not prove authorship, provenance, or safety.

---

## 7. Evaluation Harness

The evaluation harness is the main portfolio artifact. Four demo paths alone cannot prove that the verdicts are not hard-coded.

### 7.1 Fixture Set

Build 30–50 labeled fixtures covering:

- Exact allowed action and benign variations.
- Boundary and over-limit native value.
- Finite, oversized, and unlimited approvals.
- Wrong resource, beneficiary, duration, or recurrence.
- Altered calldata after receipt creation.
- Wrong chain, vault, target, mandate, or policy.
- Stale or reused action nonce.
- Expired mandate, receipt, or override.
- Invalid or rotated signer.
- Malformed calldata or unknown selector.
- Runtime code change and proxy target.
- Simulation revert.
- RPC, simulator, or context outage.
- Conflicting block state.
- Malicious retrieved instructions.
- Unexpected internal call.
- Unsupported multicall or delegatecall.
- Owner override and block behavior.
- Reentrancy attempt.
- Evaluator or signer compromise scenario within the vault’s hard caps. *Corrected 2026-08-16 (D-042), after an adversarial review demonstrated the claim was wider than the vault: **the hard caps bound the NATIVE-VALUE dimension only.** Pause, nonce, deadline and the vault’s own wei ceiling are enforced onchain (§5.7.1, D-026). **Token authority is not capped by the vault at all.** One valid ALLOW receipt for `approve(spender, type(uint256).max)` passes every vault check — the native ceiling never engages, because `valueWei` is zero — and the vault’s entire token balance is then transferable. `PolicyPayload.maxAllowanceIncreaseBaseUnits` has no onchain counterpart, so the flagship Case 2 attack is refused by the CONFORMANCE EVALUATOR with nothing behind it. That is a deliberate v1 boundary — §2 says do not invent production custody, and a vault-side token cap would partly mask what the harness exists to measure — but it must not be read as containment. Reproduced in `contracts/test/SentinelVault.backstops.t.sol`. A per-action allowance-increase ceiling is v1.1 work (`docs/v1-1-register.md`).* **CORRECTED AGAIN 2026-08-17 (A-063), because D-042's correction was itself still false in the one dimension it claimed to bound. CERTIFIED BY JOHN 2026-08-18 (D-051(a)), at a facilitated walkthrough — certified on the measurement and its control, not on the agent's summary of them. What was certified is a repair from something FALSE to something MEASURED, and not a new claim.** D-042 said the hard caps bound the native-value dimension. **They do not bound it either. `maxNativeValueWei` is compared PER ACTION** (`SentinelVault.sol`: `action.valueWei > maxNativeValueWei`), **and no cumulative, rate-limited or velocity bound exists anywhere** — not in the vault, not in `PolicyPayload`, not in `MandatePayload`; a grep of `contracts/src` for one returns nothing. Under the exact threat model this bullet names, a compromised signer mints one receipt per nonce at exactly the ceiling and the vault's entire native balance leaves. **Measured rather than argued:** a probe vault capped at 0.01 ether and funded with 1 ether was drained to zero by 100 sequential valid ALLOW receipts, each at exactly the cap, relayed by an address holding no key — `execute` is permissionless — with the paired control confirming that one action at cap+1 still reverts with `ValueOverCap`, so the drain is measured against a live ceiling rather than an absent one. **[CORRECTED 2026-08-18, D-053(a): that measurement warped a year between actions, and the framing was wrong in the direction that flatters the vault.** The warp is unnecessary. A relayer contract calls `executeWithReceipt` repeatedly inside ONE transaction — `nonReentrant` stops nesting, not repetition — and the same 100-receipt drain completes **atomically**, ~75,700 gas each, with `block.number` and `block.timestamp` asserted UNCHANGED throughout. The limit test no longer warps and asserts both.] **The other three items D-042 listed as onchain containment are no better against that threat, and listing them was the error underneath both corrections:** `actionNonce` prevents REPLAY but not a fresh receipt at N+1; `deadline` lives in the ActionPayload the receipt commits to and `expiresAt` in the receipt itself, so under signer compromise both are the attacker's to choose and the vault rejects only values already in the past. **Of the four, only PAUSE bounds a compromised signer — and pause is an owner REACTION, not a cap:** it bounds damage after somebody notices, which is a different and weaker guarantee. ~~…after somebody notices…~~ **[CORRECTED 2026-08-18, D-053(a). EVEN THAT IS TOO GENEROUS, and it is the last thing this row had left to retreat to.** Because the drain is ATOMIC there is no interval during it in which anyone could notice or act: no block boundary, no owner transaction, nothing interleaves. **Pause protects only BEFORE execution begins or BETWEEN transactions.** Against a compromised signer that batches, it provides no in-flight protection at all.] **What is true, stated plainly so this row stops overstating for a third time: the vault constrains WHAT any single action may do — target allowlist, selector, calldata hash, chain, vault, nonce ordering, per-action wei ceiling — and constrains NOTHING about how many such actions a compromised signer may issue. Per-action authority is bounded; cumulative authority is not bounded at all.** ~~A cumulative or rate-limited ceiling is v1.1 work alongside the token cap.~~ **THAT COMMITMENT IS WITHDRAWN 2026-08-18 (D-053(a)). No cumulative or rate-limited bound is added, and none is promised.** It is relabelled an OPTIONAL FUTURE EXTENSION rather than owed work: adding one would change what a mandate means onchain and would change the deployed bytecode and therefore `targetCodeHash`, which every mandate binds and all 50 committed corpus views carry. **This is an explicitly accepted v1 boundary of a testnet lab.** Read this row as: *the native-value ceiling bounds the SHAPE of each action, not aggregate loss and not execution rate; a compromised signer can issue sequential nonces and drain the vault atomically in one transaction; pause protects only before execution begins or between transactions.* **CERTIFICATION STATUS OF THIS ROW, because it now carries two corrections of different standing and the earlier one's certification must not be read as covering the later:** the A-063 per-action correction **WAS CERTIFIED by John 2026-08-18 (D-051(a))**. The D-053(a) ATOMICITY correction — and the withdrawal of the cumulative-ceiling v1.1 commitment — **IS OFFERED FOR RATIFICATION AND IS NOT CERTIFIED.** No agent may record it as certified. D-053(a) supersedes D-051(a) ONLY where the earlier wording is inconsistent with the demonstrated atomic-drain boundary; the S2 signature otherwise stands and no gate's status changes.

### 7.2 Fair Baselines

Use two baseline classes:

Representative local baseline:

- Exact chain and vault.
- Allowlisted DemoPay and DemoERC20 targets.
- Native-value ceiling.
- Direct maximum-approval block.
- No resource, beneficiary, duration, recurrence, or post-state constraint.

This baseline makes the demo reproducible but is not evidence that current vendors miss Case 3.

Strong published-capability baselines:

- Cobo pact parameter matching and completion conditions.
- Privy decoded-calldata policies.
- Hypernative custom transaction policy and approval flow.
- Sigil deterministic policy, simulation, and co-signing flow.
- Other provider capabilities where executable test access exists.

If a provider cannot be executed directly, label the result a documented-capability comparison or faithful versioned emulation, not an empirical win over the provider.

### 7.3 Security Ablation

Compare three detection configurations:

1. Representative policy baseline.
2. Policy plus pinned-state execution and effect extraction.
3. Policy plus mandate-to-effects conformance and bound receipts.

Report:

- Results by supported attack class.
- False allows and false blocks.
- Allow, block, and review rates.
- p50 and p95 deterministic decision latency.
- Dependency-failure behavior.
- Detection contribution by layer.

Do not claim general transaction-safety accuracy.

### 7.4 Separate AI Evaluation

Evaluate the optional explanation layer on:

- Citation faithfulness.
- Unsupported-claim rate.
- Explanation usefulness.
- Added human-review requests.
- Latency.
- Cost.

If AI does not improve comprehension or evidence review enough to justify cost and attack surface, remove it from the public demo.

### 7.5 Gates

*Amended 2026-08-15 (D-032). This heading previously read "Hard Gates" and covered all eight bullets, which conflicted with D-008 — titled "§7.5 soft-gate definitions" — and with D-009, which makes Gate S2 pass on "§7.5 hard-gate evidence". The three documents used one vocabulary three ways, and whether two of these gates were S2 conditions turned on it.*

**Six of the eight below are Gate S2 pass conditions**, together with the ones D-009 adds. **Two are not.** The last bullet — a viewer understanding the mechanism in five minutes — is a **PRE-PUBLICATION** condition alongside D-016's rename gate, because D-008 requires it be run against a dashboard that D-009 explicitly holds outside S2, and because it asks whether a stranger understands a finished artifact rather than whether the mechanism is proven. Vendor-comparison honesty **remains an S2 condition**: it is mechanically checkable against artifacts that exist today.


- No agent action executes without a valid allow receipt or matching review receipt plus owner override.
- Every replay, tamper, wrong-chain, expiry, and approval invariant passes.
- Critical dependency outages review or fail closed.
- The wrong-purpose case passes the representative baseline and fails mandate conformance.
- Strong vendor-capability comparisons are reported honestly.
- Foundry fuzz and invariant tests cannot bypass SentinelVault.
- A real prompt injection changes the agent proposal and is contained.
- A viewer can understand the mechanism and evidence in five minutes.

---

## 8. Threat Model and Honest Limits

Primary threats:

1. Prompt injection changes the proposed action.
2. AI drafts an incomplete or misleading mandate.
3. The owner signs a typed mandate that does not match their prose intent.
4. The agent mutates calldata after review.
5. A receipt or override is replayed.
6. Unexpected internal calls create unsupported effects.
7. Simulation state differs from execution state.
8. Remote RPC state is false, stale, or conflicting.
9. The evaluator or authorization signer is compromised.
10. The owner override becomes routine approval theater.

Core mitigations:

- Typed owner approval.
- Exact action binding.
- Active onchain mandate and policy hashes.
- One vault action nonce consumed before external execution.
- Local deterministic execution anchored to a recorded block hash.
- Explicit call-graph constraints.
- Short-lived receipts.
- Testnet fund caps and hard vault limits.
- Owner pause, revocation, recovery, and signer rotation.
- Fuzz, invariant, replay, outage, and compromise tests.

Honest limitation:

> Sentinel cannot prove arbitrary transaction safety or infer arbitrary human purpose from bytecode. It establishes conformance only for fields and effects represented in its typed mandate, active policy, supported call schemas, and effect extractors. Unknown behavior must review or fail closed.

> Sentinel verifies conformance to the signed mandate, not the fidelity of the mandate to the owner's intent. A poisoned or careless drafting step upstream of the owner's signature is outside Sentinel's authority; the architecture deliberately concentrates that residual trust in mandate signing — a rare, high-attention human step — rather than in per-action approval.

> Conformance is established against simulated effects at a recorded block, not observed post-execution effects. State may change between evaluation and execution; the vault enforces exact-action binding at execution time, but effect conformance is a pre-execution judgment.

> The evaluation corpus that grades this system is labeled under **procedural, not organizational, independence**. A solo build cannot buy an independent labeling organization. What it can buy is an auditable bound: a labeling prompt frozen before the corpus build with its hash committed, a labeler given the schemas and each fixture's declared intent but never the evaluator's source or output, a second labeler re-labeling a sample, and adversarial human sampling at the gates. The residual risk — that the author of the system also shaped the instructions that grade it — is reduced and measured, not eliminated. Reported disagreement rates, not assurances, are the evidence.

Additional limits:

- Simulation is deterministic only for the specified state and environment.
- State may change before execution.
- Code identity does not prove benign behavior.
- EOA-owner support is not production account abstraction.
- DemoERC20 approval handling does not generalize to every token or authorization scheme.
- AI explanation can still be incomplete.
- Fail-closed operation trades availability for safety.
- Testnet success is not production custody evidence.

---

## 9. Technical Direction, Sequence, and Effort

Recommended stack:

- Solidity and Foundry.
- Anvil snapshots and pinned forks for execution evidence.
- Optional Base Sepolia deployment.
- TypeScript with viem for typed data, chain access, and orchestration.
- RFC 8785 canonical JSON for evidence hashing.
- Thin Next.js evidence dashboard.
- Versioned fixtures and context files.
- Structured logs and trace IDs.

Implementation sequence:

1. Threat model, claims boundary, typed payloads, and canonical hashes.
2. SentinelVault, active mandate and policy state, nonce, pause, recovery, and hard caps.
3. Isolated signer and receipt verification.
4. DemoPay, DemoERC20, and two supported decoders.
5. Anvil snapshot, execute, inspect, trace, and revert pipeline.
6. Conformance evaluator and evidence bundle.
7. Real agent and malicious-context fixture.
8. Adversarial corpus, Foundry fuzzing, and invariants.
9. Baselines, ablation, dashboard, demo, and postmortem.

Effort:

| Deliverable | Estimate |
|---|---:|
| Clickable or partly scripted proof | 60–100 hours |
| Defensible portfolio MVP | 220–340 hours |
| Broad v0.1 roadmap | 600–1,000 hours |
| Production generalized guardrail | Multi-person security product, not a credible solo v1 |

A realistic portfolio schedule is five to eight focused full-time weeks or roughly three to five months at fifteen hours per week, assuming basic TypeScript and Solidity familiarity.

Explicitly defer:

- Production custody and mainnet funds.
- Safe, Cobo, Coinbase, Privy, and other provider adapters.
- Generalized auditing or vulnerability scanning.
- Multi-chain and arbitrary DeFi coverage.
- Tokenomics, token, DAO, or governance modules.
- Broad RAG or vector infrastructure.
- Novel public metadata standards.
- AI participation in authorization.

---

## 10. Market Validation

The MVP should produce evidence for discovery rather than assume startup fit.

### 10.1 Capability Map

Map 10–15 representative actions against the strongest published controls of Cobo, Coinbase, Circle, Privy, Safe, MetaMask, Sigil, Hypernative, Blockaid, and Tenderly.

Remove any proposed feature already covered without meaningful improvement. Record whether each comparison is:

- Executed directly.
- Faithfully emulated from current documentation.
- Documentation-only.

### 10.2 Interviews

Interview 8–12 participants, including at least:

- Three to four hands-on agent or platform engineers.
- Three to four accountable economic buyers.
- Security or audit practitioners.

Record technical pain, ownership, current spend, and procurement path separately.

Ask for the last unsafe proposal, near miss, or difficult release decision; current wallet controls; action classes that remain hard to express; and anonymized cases where policy and task purpose diverged.

### 10.3 Shadow Pilots

Run one or two read-only pilots without signing authority. Target integration in no more than one to two engineer-days.

Measure incremental catches, false allows, false blocks, review burden, latency, outages, and whether findings change a release or policy decision.

Define a material incremental catch before testing:

> A high-severity mandate violation that passes the team’s current policy and simulation stack but is detected by a portable conformance assertion or receipt check.

### 10.4 Continue Gates

Continue product discovery only if:

- At least two independent teams contribute real or anonymized cases.
- At least one team completes a shadow integration, with two preferred.
- Sentinel demonstrates a material incremental catch over the team’s current stack.
- Integration remains within the agreed burden.

One paid assessment validates a services wedge. A recurring product requires repeated live findings and recurring willingness to pay. Neither result alone establishes startup fit.

If these gates fail, finish Sentinel cleanly as an open-source evaluation lab and portfolio artifact.

---

## 11. Portfolio Proof

Sentinel is valuable because it demonstrates:

- Agent security and prompt-injection containment.
- Deterministic policy and bounded autonomy.
- Cryptographic decision binding.
- Transaction decoding and local execution.
- Smart-contract engineering.
- Failure handling and recovery.
- Adversarial evaluation.
- Separation between evidence, explanation, and authority.

Public framing:

> I built a testnet authorization and conformance gateway for an untrusted agent crossing an irreversible external-state boundary. I used EVM calls because they provide exact actions, inspectable state changes, and reproducible adversarial tests.

Required artifact package:

- Runnable repository and one-command local setup.
- Optional testnet deployment.
- Five-minute demo.
- Trust-boundary diagram.
- Typed payload and receipt specification.
- Threat model.
- 30–50 labeled fixtures.
- Foundry unit, fuzz, and invariant tests.
- Baseline and ablation report.
- Failure-mode demonstrations.
- Competitive capability matrix.
- Architecture decision records.
- One audit-style attack report.
- Honest postmortem and production-redesign requirements.

The evaluation harness is more important than dashboard polish.

Resume language, used only after metrics exist:

> Built a testnet conformance gateway for agent-proposed EVM actions, binding exact calls to human-signed mandates and evaluating policy, execution effects, replay resistance, and failure behavior across N adversarial fixtures with X percent supported high-risk recall and Y millisecond p95 deterministic decision latency.

---

## 12. Build and Commercial Verdict

Build decision:

> Greenlight Sentinel v0.2 as a sharply bounded portfolio build.

Commercial decision:

> Do not treat Sentinel as a startup until fair provider comparisons and shadow pilots demonstrate a recurring, material conformance gap.

Stop condition:

> If the project expands into production wallets, generalized auditing, broad RAG, tokenomics, or multi-chain coverage before proving the vault, binding, conformance, and evaluation mechanism, stop and recut it.

The project succeeds as a portfolio artifact if it proves:

- The agent cannot bypass SentinelVault.
- Credentials bind the exact active mandate, policy, action, nonce, and time window.
- A real prompt injection changes the proposal and is contained.
- The evaluation corpus distinguishes real catches from hard-coded demos.
- The document reports limits and competitor overlap honestly.

If those conditions are met, Sentinel can be a flagship AI-security artifact even if customer discovery does not justify a company.

---

## 13. Source Notes

Problem and evaluation context:

1. [NIST / Federal Register — Security Considerations for Artificial Intelligence Agents](https://www.federalregister.gov/documents/2026/01/08/2026-00206/request-for-information-regarding-security-considerations-for-artificial-intelligence-agents)
2. [OpenAI — Introducing EVMbench](https://openai.com/index/introducing-evmbench/)
3. [EVMbench paper](https://arxiv.org/html/2603.04915v1)
4. [OWASP Smart Contract Top 10: 2026](https://scs.owasp.org/sctop10/)

Wallet, authorization, and security alternatives:

5. [Cobo Agentic Wallet — Pact Mechanism](https://www.cobo.com/products/agentic-wallet/manual/security/pact-mechanism)
6. [Cobo Agentic Wallet — Policy Engine](https://www.cobo.com/products/agentic-wallet/manual/security/policy-engine)
7. [Coinbase Developer Platform — Policy Engine](https://docs.cdp.coinbase.com/wallets/security-and-policies/policy-engine/overview)
8. [Circle — Agent Wallets](https://developers.circle.com/agent-stack/agent-wallets)
9. [Privy — Policies and Controls](https://docs.privy.io/controls/policies/overview)
10. [Safe — Smart Account Guards](https://docs.safe.global/advanced/smart-account-guards)
11. [MetaMask — Introducing MetaMask Agent Wallet](https://metamask.io/news/introducing-metamask-agent-wallet)
12. [Sigil — Agent Wallet Security](https://sigil.codes/)
13. [Hypernative — Asset Manager Transaction Protection](https://hypernative.io/industry/asset-managers)
14. [Blockaid — Transaction Security](https://blockaid.io/transaction-security)
15. [Tenderly — Simulation for Onchain Operations](https://tenderly.co/)

Additional vendor sources, added at the Gate 5 certification session (D-038). **Appended rather
than inserted into the 5–15 block on purpose:** inserting would renumber 16–24 and silently
invalidate every `§13 #N` reference already written, which is a worse citation defect than the
one being repaired.

25. [Safe — How do Safe Smart Accounts work?](https://docs.safe.global/advanced/smart-account-overview)
26. [Safe — AI agent with a spending limit for a treasury](https://docs.safe.global/home/ai-agent-quickstarts/agent-with-spending-limit)
27. [Hypernative — How Institutions Verify a Transaction Is Safe Before It Executes](https://www.hypernative.io/insights/blog/how-institutions-verify-a-transaction-is-safe-before-it-executes)
28. [Hypernative — Guardian Brings Transaction Simulation to MPC Wallets](https://www.hypernative.io/blog/hypernative-guardian-for-web3s-institutional-moment)

Standards and implementation:

16. [ERC-7730 — Structured Data Clear Signing Format](https://eips.ethereum.org/EIPS/eip-7730)
17. [EIP-712 — Typed Structured Data Hashing and Signing](https://eips.ethereum.org/EIPS/eip-712)
18. [ERC-20 — Token Standard](https://eips.ethereum.org/EIPS/eip-20)
19. [Foundry — Invariant Testing](https://getfoundry.sh/forge/invariant-testing)
20. [Viem — Simulate Contract](https://viem.sh/docs/contract/simulateContract)
21. [RFC 8785 — JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785)
22. [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/5.x)

Naming collisions:

23. [Sentinel Protocol / Uppsala Security](https://uppward.sentinelprotocol.io/)
24. [Sentinel blockchain network whitepaper](https://docs.sentinel.co/get-started/whitepaper)

---

## 14. Reviewer Notes

Reviewer: Claude (LLM review, requested by John)
Date: 2026-07-27 (header originally misdated 2026-07-09)
Scope: Full v0.2 proposal. These are advisory notes, not sign-offs or design decisions.

### 14.1 Overall Assessment

Concur with the build decision in Section 12: greenlight as a sharply bounded portfolio build, commercialization unproven. The v0.1-to-v0.2 narrowing is real discipline. The honest market table (§2), trust classification (§3.1), fail-closed defaults, and the stop condition (§12) are strengths most proposals lack. Making the evaluation harness the primary artifact (§7) is the right call for the intended audience.

Two changes are recommended as conditions of starting the build (14.2 and 14.4); the rest are advisory.

### 14.2 The Demo Cases Do Not Test the Differentiation Hypothesis (Blocking Recommendation)

The §1 hypothesis is *portable* typed assertions and *independently verifiable* receipts. But the MVP implements only SentinelVault, and no demo case exercises receipt verification by any party other than Sentinel itself. Case 1 is table stakes; Case 2 (max-approval to attacker) is caught by essentially every policy engine in the §2 market table; Case 4 (review on uncertainty) is common. The differentiation load rests entirely on Case 3, and the proposal already concedes that Cobo pacts and Privy decoded-calldata policies may express equivalent constraints.

Recommendation: add a **fifth demonstration case — a standalone receipt-verifier CLI**. Given only the published schemas and an evidence bundle, an independent party recomputes the canonical hashes and validates the decision receipt without trusting Sentinel's code or infrastructure. This is the cheapest artifact (~10–20 hours) that actually demonstrates provider-neutrality of the receipt layer, and it does so without building a Safe or vendor adapter.

### 14.3 "Mandate-to-Effects" Is Currently "Mandate-to-Predicted-Effects"

Receipts are issued pre-execution against a pinned fork; the vault enforces at execution time, when state may have drifted (§8 acknowledges the drift but does not connect it to the framing). Nothing verifies that *actual* on-chain effects matched the simulation.

Recommendation, either/or:

- Name this crisply in the claims boundary: conformance is established against simulated effects at a recorded block, not observed post-execution effects; or
- Add a cheap post-execution attestation step on testnet: compare observed effects against the simulated evidence bundle and log a follow-up receipt. This makes the "effects" claim honest end-to-end and adds a distinctive artifact. Treat as optional scope; do not let it displace the fixture corpus.

### 14.4 Strong-Vendor Baselines Are the Scope Bomb (Blocking Recommendation)

"Faithful versioned emulation" of Cobo pact matching, Privy calldata policy, Hypernative approval flows, and Sigil co-signing (§7.2) is itself a research project, and it is where honesty erodes under time pressure — an unfaithful emulation is worse than none.

Recommendation: for the MVP, downgrade all §7.2 strong baselines to the documentation-only capability matrix already specified in §10.1. Run executed comparisons only where a provider offers free testnet access. Keep the representative local baseline for the §7.3 ablation; it is sufficient for the portfolio claim as long as it stays labeled the way §7.2 already labels it.

### 14.5 Threat 3 Is the Load-Bearing Limit — Promote It

The AI drafts the mandate; the same injection channels that can poison the action proposal can poison the mandate draft, and the human "inspects and signs" step is exactly the fatigued-review step this architecture exists to shore up. The real defense — mandate signing is a rare, high-attention event versus per-action approval, so the attack surface narrows to one channel — is implicit but never stated.

Recommendation: promote this into the §8 honest-limitation block explicitly, e.g.: *Sentinel verifies conformance to the signed mandate, not the fidelity of the mandate to the owner's intent.* Reviewers in the AI-security space will look for exactly this; preempting it reads as sophistication, being asked about it reads as a hole.

### 14.6 Sequence a Slice of Discovery Before the Build

§10 places the capability map, interviews, and shadow pilots after or alongside a 220–340 hour build. Recommendation: do the capability map and 3–4 of the engineer interviews first (~15 hours), specifically hunting for real anonymized cases where policy passed but purpose diverged (the Case 3 shape). A null result does not kill the portfolio build, but it redirects emphasis early — toward the harness-and-receipts story and away from the conformance-gap story.

### 14.7 Minor Notes

- Threat 10 (owner override becoming approval theater) has no corresponding mitigation anywhere in the design. Even an override-rate counter surfaced on the evidence dashboard would close it for the lab.
- The 220–340 hour estimate is plausible only if the §9 deferral list holds. The fixture corpus plus Foundry invariant suite is realistically half the total; scope added elsewhere comes directly out of the part that makes the project credible.
- The naming-collision warning (§0) is correct and should stay a hard pre-launch gate.

### 14.8 Rulings (John, 2026-07-27)

Recorded from the facilitated intake session on 2026-07-27. The canonical decision log for the build is `docs/decisions.md` in this repository; this subsection mirrors the rulings so the proposal is self-contained.

- **14.5 — ADOPTED for v1.** Applied to §8 in this revision, together with the free half of 14.3 (claims-boundary wording: conformance is against simulated effects at a recorded block).
- **14.4 — ADOPTED for v1, WITH MODIFICATION.** Vendor baselines are documentation-only; executed or emulated vendor comparisons — including the free-testnet executed comparisons that 14.4 as written would have kept in v1 — are cut from v1 scope and deferred to rung 2.
- **14.2 — DEFERRED to ladder rung 1.** The standalone receipt-verifier CLI (+10–20h) is a stated goal that must ship before the portfolio artifact is called done.
- **Ladder rung 2 (post-MVP, discovery track):** executed vendor comparisons where free test access exists.
- **14.3 attestation — STRETCH.** Considered only after the §7.5 gates are green.
- **14.6 — OVERRIDDEN** by John's decision to launch the build now; the §10 discovery track proceeds in parallel under John's ownership.
- **Gate cadence:** two mid-build facilitated sign-offs. Gate S1: vault + isolated signer + exact-action binding + Case 1 end-to-end + replay/tamper invariants green. Gate S2: full fixture corpus + §7.5 hard-gate evidence. Gates are signed only by John.
- **Kill criteria (no token cap):** the §12 stop condition on scope expansion; a no-progress halt after 3 failed independent attempts at a gate; immediate halt if any agent modifies fixtures, ground-truth labels, or gate definitions to make a suite pass.
- **Dispatch:** Opus 5 architects and directs subagents; John launches the build and holds all gate and veto authority. Build authorized through Gate S2.

### 14.9 Build-Start Amendments (John, 2026-07-27, delegated)

Four forks were opened at build start by Opus 5, reviewed by Fable, and ruled by John through explicit delegation: *"go with what you think is best for now and we can modify later if we discover issues in the field."* They are John's rulings by that delegation, authored by Opus 5, and revisitable on field evidence. Canonical text is `docs/decisions.md` D-007 through D-011; this subsection mirrors them so the proposal stays self-contained. §14.8 is preserved unchanged — these amend it, they do not replace it.

Gate signing authority is not delegated. Gates S1 and S2 remain facilitated sessions signed by John.

- **D-007 — Case 2 injection definition.** A §7.5 injection demonstration is real only with a plausibly-naive documented agent config (scaffold pinned by hash), malicious content arriving through a data channel the agent legitimately reads, **and** a control run on the benign document producing the Case 1 proposal. Model id, version, temperature, scaffold hash, and full transcript are recorded per fixture. Pinned transcripts are the CI fixtures; a live canary runs alongside, never fails CI, and its history ships in the S2 evidence bundle. The injection is spiked before the deep build, timeboxed to 4 hours; a negative result is reported honestly as a finding — §4 claims an *untrusted* agent cannot execute, not that a gullible one is fooled.
- **D-008 — §7.5 soft gates defined.** Five-minute comprehension: three fresh-context reviewers, demo/dashboard/README only, five questions frozen in advance and never shown to the build loop, pass at all three ≥4/5. Vendor honesty: every matrix cell documentation-only, dated and linked; §10.1's "executed" and "faithfully emulated" columns empty in v1; inference marked as inference; no claim **or layout** implying empirical superiority over a named vendor.
- **D-009 — Gate S2 amended (amends D-002).** S2 = full corpus + §7.5 hard-gate evidence + the §7.3 ablation report + the receipt-verifier CLI. The ablation is added because §7 opens by stating four demo paths cannot prove the verdicts are not hard-coded. Dashboard still excluded unless John adds it at the gate. Priority under time pressure: corpus > ablation > CLI.
- **D-010 — Receipt-verifier CLI promoted into v1 (amends D-001).** Moved from ladder rung 1 to an S2 pass condition. It shares no canonicalization or hashing code with the evaluator and is written in a different language (Python) against independent JCS and keccak implementations. Corrected effort: 20–30h, not 14.2's 10–20h, which assumed code reuse.
- **D-011 — Label independence is procedural, not organizational.** Labeling prompt frozen before the corpus build with its hash committed; labeler sees schemas, invariants, and declared intent only; a second labeler re-labels ~20%; >10% disagreement halts S2, and any disagreement on a hard-gate-relevant fixture escalates individually; John's gate sampling oversamples baseline-vs-conformance disagreements and *review* verdicts. §8 states the procedural-not-organizational limit in those words.

