// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

/// @title SentinelTypes
/// @notice The five typed payloads of proposal §5 and their canonical EIP-712 hashes.
///         This library is the single source of truth for what Sentinel binds. The
///         TypeScript evaluator and the independent Python verifier (D-010) both
///         reimplement these hashes from the written schema; cross-implementation
///         agreement is a build-time check, not an assumption.
///
/// @dev Two conventions carry security weight and are easy to lose in a later edit:
///
///      1. FIELD ORDER IS THE SCHEMA. An EIP-712 typehash is keccak256 of the type
///         string, and the type string encodes field order. Reordering fields — even
///         with identical names and types — silently produces a different hash and
///         invalidates every previously signed payload. `SentinelTypes.t.sol` recomputes
///         every typehash from its literal type string, so a reorder fails the suite
///         rather than passing quietly.
///
///      2. SIGNATURES ARE ENVELOPE FIELDS (§5). A signature is never part of the payload
///         it signs. `SignedMandate` is `MandatePayload + ownerSignature`, and the mandate
///         hash covers the payload only. Structs here are payloads; envelopes live at the
///         call boundary.
library SentinelTypes {
    // ---------------------------------------------------------------------
    // Enumerations
    // ---------------------------------------------------------------------

    /// @notice Top-level EVM operation. v0.2 supports CALL only (§4).
    /// @dev DELEGATECALL and CREATE are declared so an unsupported operation has a
    ///      name in traces and reason codes rather than surfacing as a bare integer.
    ///      Declaring them is not supporting them: §5.7 lists both as unsupported, and
    ///      the vault rejects any operation other than CALL.
    enum Operation {
        CALL, // 0
        DELEGATECALL, // 1 — unsupported, never executes
        CREATE // 2 — unsupported, never executes
    }

    /// @notice Deterministic verdict (§3.2 step 11).
    /// @dev BLOCK is deliberately the zero value. A zero-initialised struct, an
    ///      uninitialised storage slot, or a decode of empty bytes therefore reads as
    ///      BLOCK and never as ALLOW. This is invariant §3.3(8) — "missing or conflicting
    ///      state ... never produces automatic allow" — expressed in the type system
    ///      instead of in a runtime check that a later refactor could drop.
    enum Verdict {
        BLOCK, // 0 — fail-closed default
        REVIEW, // 1
        ALLOW // 2
    }

    /// @notice Behaviour when a required check cannot be evaluated (§5.2 failureMode).
    /// @dev FAIL_CLOSED is the zero value, for the same reason as BLOCK above.
    enum FailureMode {
        FAIL_CLOSED, // 0
        REVIEW // 1
    }

    // ---------------------------------------------------------------------
    // Payload structs (§5.1 – §5.5)
    // ---------------------------------------------------------------------

    /// @notice §5.1. What the human owner actually signs. The MVP supports one EOA
    ///         owner; `principal` must equal the vault owner at activation time.
    struct MandatePayload {
        uint16 schemaVersion;
        bytes32 mandateId;
        address principal;
        /// @notice The only isolated signer this owner-signed mandate authorises.
        /// @dev Binding the signer here makes rotation fail closed: a mandate signed for
        ///      signer A cannot become executable merely because the vault later selects B.
        address signer;
        address vault;
        uint256 chainId;
        address target;
        bytes32 targetCodeHash;
        bytes4 selector;
        uint256 maxNativeValueWei;
        bytes32 purposeKind;
        bytes32 resourceId;
        address beneficiary;
        uint64 durationSeconds;
        bool recurringAllowed;
        uint64 validAfter;
        uint64 validUntil;
        bytes32 policyHash;
    }

    /// @notice §5.2. Mandate and policy constraints are intersected; any failed rule
    ///         blocks, any unknown required check reviews.
    struct PolicyPayload {
        uint16 schemaVersion;
        uint32 policyVersion;
        address vault;
        uint256 chainId;
        uint8 allowedOperation;
        bytes32 allowedTargetsHash;
        bytes32 allowedSelectorsHash;
        uint256 maxNativeValueWei;
        uint256 maxAllowanceIncreaseBaseUnits;
        bytes32 allowedCallGraphHash;
        uint64 validAfter;
        uint64 validUntil;
        uint8 failureMode;
    }

    /// @notice §5.3. The exact action. Every field named in invariant §3.3(4) appears
    ///         here, and mutating any of them changes `actionHash` — which is what makes
    ///         invariant §3.3(5) ("any mutation to a bound field invalidates
    ///         authorization") mechanical rather than procedural.
    /// @dev The complete calldata travels alongside the payload; the vault recomputes
    ///      `dataHash` from it and never trusts a supplied digest.
    struct ActionPayload {
        uint16 schemaVersion;
        uint256 chainId;
        address vault;
        uint256 actionNonce;
        address target;
        uint256 valueWei;
        bytes32 dataHash;
        uint8 operation;
        bytes32 mandateHash;
        bytes32 policyHash;
        uint64 deadline;
    }

    /// @notice §5.4. Signed by the isolated signer (A-005). Only an ALLOW receipt is
    ///         executable on the automatic path.
    /// @dev `simulationBlockNumber` / `simulationBlockHash` record the pinned block the
    ///      verdict was computed against. Per §8 as amended, conformance is established
    ///      against simulated effects at that recorded block, not observed
    ///      post-execution effects — these two fields are what make that claim auditable
    ///      rather than rhetorical.
    struct DecisionReceiptPayload {
        uint16 schemaVersion;
        bytes32 decisionId;
        bytes32 actionHash;
        bytes32 mandateHash;
        bytes32 policyHash;
        uint8 verdict;
        bytes32 reasonCodesHash;
        bytes32 evidenceHash;
        uint256 simulationBlockNumber;
        bytes32 simulationBlockHash;
        uint64 issuedAt;
        uint64 expiresAt;
        address signer;
    }

    /// @notice §5.5. Owner override for a REVIEW receipt, bound to one exact action.
    /// @dev Carries `reviewReceiptHash` so the vault can require the matching review
    ///      receipt (invariant §3.3(7)). A BLOCK receipt cannot be overridden at all —
    ///      that path requires a new mandate or policy.
    struct OverrideAuthorizationPayload {
        uint16 schemaVersion;
        bytes32 reviewReceiptHash;
        bytes32 actionHash;
        bytes32 mandateHash;
        bytes32 policyHash;
        uint256 actionNonce;
        bytes32 reasonHash;
        uint64 issuedAt;
        uint64 expiresAt;
    }

    // ---------------------------------------------------------------------
    // Type strings and typehashes
    // ---------------------------------------------------------------------
    // Kept as literal strings beside their hashes so a reviewer can verify the pair by
    // eye and the suite can verify it by keccak. Field order must match the structs above.

    string internal constant MANDATE_TYPE =
        "MandatePayload(uint16 schemaVersion,bytes32 mandateId,address principal,address signer,address vault,uint256 chainId,address target,bytes32 targetCodeHash,bytes4 selector,uint256 maxNativeValueWei,bytes32 purposeKind,bytes32 resourceId,address beneficiary,uint64 durationSeconds,bool recurringAllowed,uint64 validAfter,uint64 validUntil,bytes32 policyHash)";

    string internal constant POLICY_TYPE =
        "PolicyPayload(uint16 schemaVersion,uint32 policyVersion,address vault,uint256 chainId,uint8 allowedOperation,bytes32 allowedTargetsHash,bytes32 allowedSelectorsHash,uint256 maxNativeValueWei,uint256 maxAllowanceIncreaseBaseUnits,bytes32 allowedCallGraphHash,uint64 validAfter,uint64 validUntil,uint8 failureMode)";

    string internal constant ACTION_TYPE =
        "ActionPayload(uint16 schemaVersion,uint256 chainId,address vault,uint256 actionNonce,address target,uint256 valueWei,bytes32 dataHash,uint8 operation,bytes32 mandateHash,bytes32 policyHash,uint64 deadline)";

    string internal constant RECEIPT_TYPE =
        "DecisionReceiptPayload(uint16 schemaVersion,bytes32 decisionId,bytes32 actionHash,bytes32 mandateHash,bytes32 policyHash,uint8 verdict,bytes32 reasonCodesHash,bytes32 evidenceHash,uint256 simulationBlockNumber,bytes32 simulationBlockHash,uint64 issuedAt,uint64 expiresAt,address signer)";

    string internal constant OVERRIDE_TYPE =
        "OverrideAuthorizationPayload(uint16 schemaVersion,bytes32 reviewReceiptHash,bytes32 actionHash,bytes32 mandateHash,bytes32 policyHash,uint256 actionNonce,bytes32 reasonHash,uint64 issuedAt,uint64 expiresAt)";

    string internal constant EIP712_DOMAIN_TYPE =
        "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)";

    bytes32 internal constant MANDATE_TYPEHASH = keccak256(bytes(MANDATE_TYPE));
    bytes32 internal constant POLICY_TYPEHASH = keccak256(bytes(POLICY_TYPE));
    bytes32 internal constant ACTION_TYPEHASH = keccak256(bytes(ACTION_TYPE));
    bytes32 internal constant RECEIPT_TYPEHASH = keccak256(bytes(RECEIPT_TYPE));
    bytes32 internal constant OVERRIDE_TYPEHASH = keccak256(bytes(OVERRIDE_TYPE));
    bytes32 internal constant EIP712_DOMAIN_TYPEHASH = keccak256(bytes(EIP712_DOMAIN_TYPE));

    string internal constant DOMAIN_NAME = "Sentinel";
    string internal constant DOMAIN_VERSION = "0.3";

    // ---------------------------------------------------------------------
    // Domain separator
    // ---------------------------------------------------------------------

    /// @notice EIP-712 domain separator, bound to chain and vault.
    /// @dev Binding `verifyingContract` to the vault is what stops a payload signed for
    ///      one vault from validating against another; binding `chainId` is the
    ///      wrong-chain fixture in §7.1. Both are also carried inside the payloads
    ///      themselves. That redundancy is deliberate: the domain protects the signature,
    ///      the payload fields let an offchain verifier that never saw the domain — the
    ///      D-010 CLI — still check chain and vault binding from the bundle alone.
    function domainSeparator(uint256 chainId, address vault) internal pure returns (bytes32) {
        return keccak256(
            abi.encode(
                EIP712_DOMAIN_TYPEHASH,
                keccak256(bytes(DOMAIN_NAME)),
                keccak256(bytes(DOMAIN_VERSION)),
                chainId,
                vault
            )
        );
    }

    /// @notice EIP-712 digest: keccak256(0x1901 ‖ domainSeparator ‖ structHash).
    function digest(bytes32 domainSep, bytes32 structHash) internal pure returns (bytes32) {
        return keccak256(abi.encodePacked(hex"1901", domainSep, structHash));
    }

    // ---------------------------------------------------------------------
    // Struct hashes
    // ---------------------------------------------------------------------
    // abi.encode zero-pads every atomic field to 32 bytes, which is exactly the EIP-712
    // encodeData rule for atomic types. Every field of every payload here is atomic
    // (no strings, bytes, arrays, or nested structs), so no member needs pre-hashing.

    function hashMandate(MandatePayload memory m) internal pure returns (bytes32) {
        return keccak256(
            abi.encode(
                MANDATE_TYPEHASH,
                m.schemaVersion,
                m.mandateId,
                m.principal,
                m.signer,
                m.vault,
                m.chainId,
                m.target,
                m.targetCodeHash,
                m.selector,
                m.maxNativeValueWei,
                m.purposeKind,
                m.resourceId,
                m.beneficiary,
                m.durationSeconds,
                m.recurringAllowed,
                m.validAfter,
                m.validUntil,
                m.policyHash
            )
        );
    }

    function hashPolicy(PolicyPayload memory p) internal pure returns (bytes32) {
        return keccak256(
            abi.encode(
                POLICY_TYPEHASH,
                p.schemaVersion,
                p.policyVersion,
                p.vault,
                p.chainId,
                p.allowedOperation,
                p.allowedTargetsHash,
                p.allowedSelectorsHash,
                p.maxNativeValueWei,
                p.maxAllowanceIncreaseBaseUnits,
                p.allowedCallGraphHash,
                p.validAfter,
                p.validUntil,
                p.failureMode
            )
        );
    }

    function hashAction(ActionPayload memory a) internal pure returns (bytes32) {
        return keccak256(
            abi.encode(
                ACTION_TYPEHASH,
                a.schemaVersion,
                a.chainId,
                a.vault,
                a.actionNonce,
                a.target,
                a.valueWei,
                a.dataHash,
                a.operation,
                a.mandateHash,
                a.policyHash,
                a.deadline
            )
        );
    }

    function hashReceipt(DecisionReceiptPayload memory r) internal pure returns (bytes32) {
        return keccak256(
            abi.encode(
                RECEIPT_TYPEHASH,
                r.schemaVersion,
                r.decisionId,
                r.actionHash,
                r.mandateHash,
                r.policyHash,
                r.verdict,
                r.reasonCodesHash,
                r.evidenceHash,
                r.simulationBlockNumber,
                r.simulationBlockHash,
                r.issuedAt,
                r.expiresAt,
                r.signer
            )
        );
    }

    function hashOverride(OverrideAuthorizationPayload memory o) internal pure returns (bytes32) {
        return keccak256(
            abi.encode(
                OVERRIDE_TYPEHASH,
                o.schemaVersion,
                o.reviewReceiptHash,
                o.actionHash,
                o.mandateHash,
                o.policyHash,
                o.actionNonce,
                o.reasonHash,
                o.issuedAt,
                o.expiresAt
            )
        );
    }
}
