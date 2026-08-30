# Enforcement release v0.3

This is an additive publication profile. It does not rewrite or supersede the
historical v0.2 proposal as a record of what was ratified at that time.

## EIP-712 type strings (normative)

The v0.3 mandate binds the isolated signer explicitly. Its canonical type is:

    MandatePayload(uint16 schemaVersion,bytes32 mandateId,address principal,address signer,address vault,uint256 chainId,address target,bytes32 targetCodeHash,bytes4 selector,uint256 maxNativeValueWei,bytes32 purposeKind,bytes32 resourceId,address beneficiary,uint64 durationSeconds,bool recurringAllowed,uint64 validAfter,uint64 validUntil,bytes32 policyHash)

The EIP-712 domain is `Sentinel` version `0.3`. The owner signs the mandate
digest before activation. The Vault checks the owner signature, signer, chain,
vault, active policy, validity window, target, selector, and native-value limit,
then stores that authenticated enforcement state. The isolated signer checks
the mandate's runtime code hash before automatic ALLOW; a mismatch can produce
only a REVIEW, whose execution additionally requires the owner's separately
signed exact-action override. This preserves the established Case 4 recovery
path without letting the isolated signer waive code identity. Signer rotation
revokes the active mandate; it never transfers mandate authority.

Receipt, override, mandate, and policy validity use a closed lower bound and an
open upper bound: `issuedAt/validAfter <= evaluationTime < expiresAt/validUntil`.
The action deadline remains inclusive.

Publication identity comes only from
`sentinel.deployment-manifest.v1`, signed by an authority whose address the
verifying party obtains out of band. A bundled `domain.json` is never a trust
root. The manifest binds chain, Vault, owner, signer, deployment block and hash,
runtime code hash, compiler metadata hash, and source archive hash.

The generated [release tree](../release/README.md) contains source, ABI,
bytecode, compiler metadata, a focused adversarial contract test, the runtime,
the independent verifier, and the ephemeral-key cold demo. Assembling it does
not authorize publication, deployment, or push.

## Evaluator check coverage (additive)

The v0.2 §5.7.1 inventory remains the historical baseline. v0.3 adds
`EVAL_MANDATE_SIGNER_ACTIVE`: the signer named by the owner-signed mandate must equal the
Vault's currently active isolated signer. A mismatch is a violation and never produces an
automatic allow. The strict publication verifier independently recovers the owner mandate
signature and the receipt signer signature against the authenticated deployment manifest.
