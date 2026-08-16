// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {ECDSA} from "openzeppelin-contracts/contracts/utils/cryptography/ECDSA.sol";
import {SentinelTypes as T} from "./types/SentinelTypes.sol";

/// @title SentinelVault
/// @notice The enforcement substrate of §4: "An untrusted agent cannot execute a supported
///         EVM action unless SentinelVault verifies a credential bound to the active
///         human-signed mandate, active policy, exact call, and current action nonce."
///
/// @dev THIS IS AN EXECUTION HARNESS, NOT A PRODUCTION WALLET (§4). Its hard onchain
///      backstops cap native value, restrict targets and selectors, enforce the active
///      signer and nonce, and let the owner pause or recover. A compromised evaluator or
///      signer can still authorize a malicious action within those caps — the lab bounds
///      worst-case blast radius to testnet funds, it does not eliminate it.
///
/// @dev WHY `execute` IS PERMISSIONLESS. Authorization rides on the receipt, not on
///      `msg.sender`. Anyone may relay a valid allow receipt, and that is safe precisely
///      because the receipt binds the exact action and the nonce is consumed on use —
///      a relayer can only cause what the owner already authorized, exactly once.
///      Gating on a designated agent address would add a second, weaker credential and
///      invite the mistake of trusting it. The credential is the receipt. (§3.3(1) is
///      satisfied by there being no other execution path, not by caller checks.)
contract SentinelVault {
    using ECDSA for bytes32;

    // ---------------------------------------------------------------------
    // Errors
    // ---------------------------------------------------------------------

    error NotOwner();
    error Paused();
    error WrongChain();
    error WrongVault();
    error BadNonce();
    error ActionExpired();
    error ReceiptExpired();
    error OverrideExpired();
    error MandateNotActive();
    error PolicyNotActive();
    error UnsupportedOperation();
    error CalldataMismatch();
    error ValueOverCap();
    error TargetNotAllowed();
    error SelectorNotAllowed();
    error ReceiptActionMismatch();
    error ReceiptBindingMismatch();
    error NotAllowVerdict();
    error NotReviewVerdict();
    error WrongSigner();
    error OverrideMismatch();
    error NotOwnerOverride();
    error Reentrancy();
    error CallFailed(bytes returnData);
    error CalldataTooShort();
    error ZeroAddress();

    // ---------------------------------------------------------------------
    // Events
    // ---------------------------------------------------------------------

    event MandateActivated(bytes32 indexed mandateHash);
    event MandateRevoked(bytes32 indexed mandateHash);
    event PolicyActivated(bytes32 indexed policyHash);
    event SignerRotated(address indexed previousSigner, address indexed newSigner);
    event PausedSet(bool paused);
    event Recovered(address indexed to, uint256 amount);
    event ActionExecuted(
        bytes32 indexed actionHash, uint256 indexed actionNonce, bytes32 decisionId, bool viaOverride
    );

    /// @notice The owner authorization an override executed under.
    ///
    /// @dev ADDED 2026-08-16 (D-043). §3.3(2) requires that override be "separately
    ///      authenticated, unavailable to the agent, and LOGGED". The first two were enforced;
    ///      the third was not. `ActionExecuted` carried only `viaOverride: true` and the
    ///      RECEIPT's `decisionId` — so an auditor reconstructing history from the log could
    ///      see THAT an override happened and never which owner authorization permitted it,
    ///      or what the owner's recorded reason was. Every other item in §3.3(2) already had
    ///      a dedicated event; override was the omission. Found by adversarial review (A-040).
    ///
    ///      `reasonHash` is the owner's justification, and it is the field that makes this
    ///      more than bookkeeping: §3.3(7) makes a review override the one path where a human
    ///      overrules the automatic decision, and an override with no recorded reason is
    ///      exactly the event a hostile reader would ask about first.
    event OverrideAuthorized(
        bytes32 indexed actionHash,
        bytes32 indexed overrideHash,
        bytes32 reviewReceiptHash,
        bytes32 reasonHash,
        uint64 expiresAt
    );

    // ---------------------------------------------------------------------
    // State
    // ---------------------------------------------------------------------

    address public owner;

    /// @notice The isolated signer's address (A-005). The signing key lives in a separate
    ///         OS process that exposes no generic sign-bytes method (§3.1).
    address public signer;

    bytes32 public activeMandateHash;
    bytes32 public activePolicyHash;

    /// @notice Invariant §3.3(9): a single monotonically increasing nonce, consumed
    ///         *before* the external call. This is the whole of replay prevention —
    ///         a receipt signature authenticates a receipt, it does not make it
    ///         single-use (§3.3(12)).
    uint256 public actionNonce;

    bool public paused;

    // --- Hard backstops (§4). Immutable or owner-only; never agent-reachable. ---

    uint256 public immutable maxNativeValueWei;
    mapping(address => bool) public allowedTarget;
    mapping(bytes4 => bool) public allowedSelector;

    /// @dev Reentrancy guard. The nonce bump alone already defeats reuse of the *same*
    ///      credential, but a target that calls back into `execute` with a *different*
    ///      valid receipt would otherwise nest. Invariant §3.3(8) says unexpected
    ///      internal calls never produce an automatic allow; refusing to re-enter at all
    ///      is the strongest form of that at this layer.
    uint256 private _entered;

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    modifier nonReentrant() {
        if (_entered == 1) revert Reentrancy();
        _entered = 1;
        _;
        _entered = 0;
    }

    constructor(
        address _owner,
        address _signer,
        uint256 _maxNativeValueWei,
        address[] memory targets,
        bytes4[] memory selectors
    ) payable {
        if (_owner == address(0) || _signer == address(0)) revert ZeroAddress();
        owner = _owner;
        signer = _signer;
        maxNativeValueWei = _maxNativeValueWei;
        for (uint256 i = 0; i < targets.length; i++) {
            allowedTarget[targets[i]] = true;
        }
        for (uint256 i = 0; i < selectors.length; i++) {
            allowedSelector[selectors[i]] = true;
        }
    }

    receive() external payable {}

    // ---------------------------------------------------------------------
    // Owner-only controls (§3.3(2), §3.3(10)) — never reachable by the agent
    // ---------------------------------------------------------------------

    function activateMandate(bytes32 mandateHash) external onlyOwner {
        activeMandateHash = mandateHash;
        emit MandateActivated(mandateHash);
    }

    function revokeMandate() external onlyOwner {
        bytes32 previous = activeMandateHash;
        activeMandateHash = bytes32(0);
        emit MandateRevoked(previous);
    }

    function activatePolicy(bytes32 policyHash) external onlyOwner {
        activePolicyHash = policyHash;
        emit PolicyActivated(policyHash);
    }

    function rotateSigner(address newSigner) external onlyOwner {
        if (newSigner == address(0)) revert ZeroAddress();
        emit SignerRotated(signer, newSigner);
        signer = newSigner;
    }

    function setPaused(bool value) external onlyOwner {
        paused = value;
        emit PausedSet(value);
    }

    function recover(address payable to, uint256 amount) external onlyOwner {
        if (to == address(0)) revert ZeroAddress();
        emit Recovered(to, amount);
        (bool ok, bytes memory ret) = to.call{value: amount}("");
        if (!ok) revert CallFailed(ret);
    }

    // ---------------------------------------------------------------------
    // Execution
    // ---------------------------------------------------------------------

    /// @notice The automatic path. Requires a current, unexpired ALLOW receipt from the
    ///         active signer, bound to this exact action (§3.3(6)).
    function executeWithReceipt(
        T.ActionPayload calldata action,
        bytes calldata callData,
        T.DecisionReceiptPayload calldata receipt,
        bytes calldata receiptSig
    ) external nonReentrant returns (bytes memory) {
        _checkAction(action, callData);
        _checkReceipt(action, receipt, receiptSig);

        if (receipt.verdict != uint8(T.Verdict.ALLOW)) revert NotAllowVerdict();

        return _consumeAndCall(action, callData, receipt.decisionId, false);
    }

    /// @notice The review path (§3.3(7)). Requires BOTH a signed REVIEW receipt AND a
    ///         separate owner-signed override naming that exact review receipt and action.
    /// @dev A BLOCK receipt can never reach here — the verdict check rejects anything that
    ///      is not REVIEW, and `executeWithReceipt` rejects anything that is not ALLOW.
    ///      There is deliberately no third path.
    function executeWithOverride(
        T.ActionPayload calldata action,
        bytes calldata callData,
        T.DecisionReceiptPayload calldata receipt,
        bytes calldata receiptSig,
        T.OverrideAuthorizationPayload calldata auth,
        bytes calldata ownerSig
    ) external nonReentrant returns (bytes memory) {
        _checkAction(action, callData);
        bytes32 receiptHash = _checkReceipt(action, receipt, receiptSig);

        if (receipt.verdict != uint8(T.Verdict.REVIEW)) revert NotReviewVerdict();

        // The override must name this exact review receipt, this exact action, and this
        // exact nonce. Any looser binding would let one override authorize a different action.
        if (
            auth.reviewReceiptHash != receiptHash || auth.actionHash != T.hashAction(action)
                || auth.mandateHash != action.mandateHash || auth.policyHash != action.policyHash
                || auth.actionNonce != action.actionNonce
        ) revert OverrideMismatch();

        // forge-lint: disable-next-line(block-timestamp)
        if (block.timestamp > auth.expiresAt) revert OverrideExpired();

        bytes32 overrideHash = T.hashOverride(auth);
        bytes32 digest = T.digest(_domainSeparator(), overrideHash);
        if (digest.recover(ownerSig) != owner) revert NotOwnerOverride();

        // §3.3(2)'s "logged", emitted AFTER authentication and BEFORE the call — so the log
        // records only authorizations that actually passed, and records them even if the
        // external call then reverts the transaction away. (D-043)
        emit OverrideAuthorized(
            auth.actionHash, overrideHash, auth.reviewReceiptHash, auth.reasonHash, auth.expiresAt
        );

        return _consumeAndCall(action, callData, receipt.decisionId, true);
    }

    // ---------------------------------------------------------------------
    // Internal checks
    // ---------------------------------------------------------------------

    /// @dev Every field named in invariant §3.3(4) is checked here. Mutating any of them
    ///      changes `actionHash`, which then fails the receipt binding in `_checkReceipt` —
    ///      that pair is invariant §3.3(5).
    /// @dev NOTE ON `block.timestamp` (forge-lint block-timestamp, suppressed below).
    ///      The lint warns that validators can nudge the timestamp. That is true and
    ///      irrelevant here: these are *validity windows*, not a randomness source and not
    ///      a value-bearing comparison. The manipulable range is seconds; mandate, receipt,
    ///      override, and action windows are set in minutes or longer, and the failure mode
    ///      of a few seconds' drift is a credential expiring marginally early or late —
    ///      never an unauthorized execution, because expiry is only ever an additional
    ///      reason to reject. Suppressed per-line with this reason rather than by relaxing
    ///      `deny = "warnings"`, so the next genuine timestamp misuse still fails the build.
    function _checkAction(T.ActionPayload calldata action, bytes calldata callData) internal view {
        if (paused) revert Paused();
        if (action.chainId != block.chainid) revert WrongChain();
        if (action.vault != address(this)) revert WrongVault();
        if (action.actionNonce != actionNonce) revert BadNonce();
        // forge-lint: disable-next-line(block-timestamp)
        if (block.timestamp > action.deadline) revert ActionExpired();

        // Missing state never produces an automatic allow (§3.3(8)). A zero active hash
        // means "no mandate activated", and the zero check must come first — otherwise a
        // caller supplying mandateHash == 0 would match an uninitialised vault.
        if (activeMandateHash == bytes32(0) || action.mandateHash != activeMandateHash) {
            revert MandateNotActive();
        }
        if (activePolicyHash == bytes32(0) || action.policyHash != activePolicyHash) {
            revert PolicyNotActive();
        }

        if (action.operation != uint8(T.Operation.CALL)) revert UnsupportedOperation();

        // The vault recomputes the digest from the bytes it will actually pass on; it never
        // trusts a supplied dataHash (§5.3).
        if (keccak256(callData) != action.dataHash) revert CalldataMismatch();

        if (action.valueWei > maxNativeValueWei) revert ValueOverCap();
        if (!allowedTarget[action.target]) revert TargetNotAllowed();

        if (callData.length < 4) revert CalldataTooShort();
        if (!allowedSelector[bytes4(callData[:4])]) revert SelectorNotAllowed();
    }

    function _checkReceipt(
        T.ActionPayload calldata action,
        T.DecisionReceiptPayload calldata receipt,
        bytes calldata receiptSig
    ) internal view returns (bytes32 receiptHash) {
        if (receipt.actionHash != T.hashAction(action)) revert ReceiptActionMismatch();
        if (receipt.mandateHash != action.mandateHash || receipt.policyHash != action.policyHash) {
            revert ReceiptBindingMismatch();
        }
        // forge-lint: disable-next-line(block-timestamp)
        if (block.timestamp > receipt.expiresAt) revert ReceiptExpired();

        // Both halves matter: the receipt must *name* the active signer, and must actually
        // be *signed* by it. Checking only the named field would accept an unsigned claim;
        // checking only the recovered address would accept a receipt signed by the active
        // key that names somebody else.
        //
        // CORRECTED 2026-08-16 (A-040). This comment previously claimed the named-signer
        // check stops "a stale receipt naming a rotated-out signer if that key were later
        // reinstated". IT DOES NOT, and an adversarial review demonstrated it: with both
        // halves present, rotate A -> B (the old receipt correctly dies), then rotate B -> A,
        // and the same receipt executes. The mirror case also holds — a receipt pre-minted by
        // a standby key is rejected until the owner rotates to that key, and goes live the
        // instant they do.
        //
        // THE REAL PROPERTY, STATED SO IT CANNOT DRIFT AGAIN: nothing here binds a receipt to
        // the EPOCH in which its signer was active. Rotation is not revocation. Both checks
        // are point-in-time comparisons against whoever `signer` is right now. Receipt
        // currency comes from `expiresAt` and from the action nonce, not from rotation.
        // Epoch binding is v1.1 work (docs/v1-1-register.md); the tests below pin the
        // behaviour as it actually is.
        if (receipt.signer != signer) revert WrongSigner();

        receiptHash = T.hashReceipt(receipt);
        bytes32 digest = T.digest(_domainSeparator(), receiptHash);
        if (digest.recover(receiptSig) != signer) revert WrongSigner();
    }

    /// @dev Nonce is consumed BEFORE the external call (§3.2 step 13, §3.3(9)). Ordering is
    ///      the point: bumping after the call would leave the credential live for the
    ///      duration of a reentrant callback.
    function _consumeAndCall(
        T.ActionPayload calldata action,
        bytes calldata callData,
        bytes32 decisionId,
        bool viaOverride
    ) internal returns (bytes memory) {
        bytes32 actionHash = T.hashAction(action);
        actionNonce += 1;

        emit ActionExecuted(actionHash, action.actionNonce, decisionId, viaOverride);

        (bool ok, bytes memory ret) = action.target.call{value: action.valueWei}(callData);
        if (!ok) revert CallFailed(ret);
        return ret;
    }

    function _domainSeparator() internal view returns (bytes32) {
        return T.domainSeparator(block.chainid, address(this));
    }

    /// @notice Exposed so offchain tooling and the independent verifier (D-010) can check
    ///         they derive the same domain the vault enforces.
    function domainSeparator() external view returns (bytes32) {
        return _domainSeparator();
    }
}
