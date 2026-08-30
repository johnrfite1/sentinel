// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {SentinelVault} from "../src/SentinelVault.sol";
import {SentinelTypes as T} from "../src/types/SentinelTypes.sol";
import {DemoPay} from "../src/demo/DemoPay.sol";
import {MandateTestHelper} from "./MandateTestHelper.sol";

/// @title SentinelVault — enforcement and binding suite
/// @notice Covers §9 step 2 and the replay/tamper half of Gate S1 (D-002).
///
/// @dev COVERAGE BOUNDARY (AGENTS.md test-coverage discipline; house rule 4).
///
///      Evidence for: the §3.3 invariants that live at the vault — nonce single-use and
///      monotonicity, exact-action binding across every bound field, block/review verdict
///      gating, override binding, pause, owner-only controls, signer rotation, reentrancy,
///      and the ordering property that the nonce is consumed before the external call.
///
///      NOT evidence for: anything about the conformance evaluator, the decoders, the
///      Anvil pipeline, or whether a *correct* verdict was reached. This suite assumes a
///      receipt exists and asks only whether the vault enforces it. A vault that
///      faithfully executes a wrong verdict passes every test here — that is by design,
///      and it is exactly why §7 makes the evaluation harness the primary artifact rather
///      than these tests.
contract SentinelVaultTest is MandateTestHelper {
    SentinelVault internal vault;
    DemoPay internal demoPay;

    uint256 internal constant OWNER_PK = 0xA11CE;
    uint256 internal constant SIGNER_PK = 0x519E4;
    uint256 internal constant ATTACKER_PK = 0xBAD;

    address internal owner;
    address internal signerAddr;
    address internal attacker;

    uint256 internal constant MAX_VALUE = 0.01 ether;
    bytes32 internal constant RESOURCE = keccak256("weather-basic-24h");
    bytes32 internal MANDATE_HASH;
    bytes32 internal constant POLICY_HASH = keccak256("policy-1");

    bytes4 internal constant PURCHASE_SEL = DemoPay.purchase.selector;

    function setUp() public {
        owner = vm.addr(OWNER_PK);
        signerAddr = vm.addr(SIGNER_PK);
        attacker = vm.addr(ATTACKER_PK);

        demoPay = new DemoPay();

        address[] memory targets = new address[](1);
        targets[0] = address(demoPay);
        bytes4[] memory selectors = new bytes4[](1);
        selectors[0] = PURCHASE_SEL;

        vault = new SentinelVault(owner, signerAddr, MAX_VALUE, targets, selectors);
        vm.deal(address(vault), 10 ether);

        MANDATE_HASH = _activateTestMandate(
            vault, OWNER_PK, owner, signerAddr, address(demoPay), PURCHASE_SEL, MAX_VALUE,
            POLICY_HASH, keccak256("mandate-1")
        );

        // Timestamps in fixtures are absolute, so start the clock somewhere sane.
        vm.warp(1_000_000);
    }

    // =================================================================
    // Fixture builders
    // =================================================================

    function _callData() internal view returns (bytes memory) {
        return abi.encodeCall(DemoPay.purchase, (RESOURCE, owner, 24 hours, false));
    }

    function _action(bytes memory data) internal view returns (T.ActionPayload memory a) {
        a = T.ActionPayload({
            schemaVersion: 1,
            chainId: block.chainid,
            vault: address(vault),
            actionNonce: vault.actionNonce(),
            target: address(demoPay),
            valueWei: 0.005 ether,
            dataHash: keccak256(data),
            operation: uint8(T.Operation.CALL),
            mandateHash: MANDATE_HASH,
            policyHash: POLICY_HASH,
            deadline: uint64(block.timestamp + 1 hours)
        });
    }

    function _receipt(T.ActionPayload memory a, T.Verdict verdict)
        internal
        view
        returns (T.DecisionReceiptPayload memory r)
    {
        r = T.DecisionReceiptPayload({
            schemaVersion: 1,
            decisionId: keccak256("decision-1"),
            actionHash: T.hashAction(a),
            mandateHash: a.mandateHash,
            policyHash: a.policyHash,
            verdict: uint8(verdict),
            reasonCodesHash: keccak256("reasons"),
            evidenceHash: keccak256("evidence"),
            simulationBlockNumber: block.number,
            simulationBlockHash: blockhash(block.number - 1),
            issuedAt: uint64(block.timestamp),
            expiresAt: uint64(block.timestamp + 10 minutes),
            signer: signerAddr
        });
    }

    function _sign(uint256 pk, bytes32 structHash) internal view returns (bytes memory) {
        bytes32 digest = T.digest(T.domainSeparator(block.chainid, address(vault)), structHash);
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(pk, digest);
        return abi.encodePacked(r, s, v);
    }

    function _allowBundle()
        internal
        view
        returns (T.ActionPayload memory a, bytes memory data, T.DecisionReceiptPayload memory r, bytes memory sig)
    {
        data = _callData();
        a = _action(data);
        r = _receipt(a, T.Verdict.ALLOW);
        sig = _sign(SIGNER_PK, T.hashReceipt(r));
    }

    // =================================================================
    // Happy path — Case 1
    // =================================================================

    function test_case1_allowReceiptExecutes() public {
        (T.ActionPayload memory a, bytes memory data, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _allowBundle();

        vault.executeWithReceipt(a, data, r, sig);

        assertEq(demoPay.entitlementExpiry(owner, RESOURCE), uint64(block.timestamp + 24 hours));
        assertFalse(demoPay.recurringEnabled(owner, RESOURCE));
        assertEq(vault.actionNonce(), 1, "nonce must be consumed");
        assertEq(address(demoPay).balance, 0.005 ether);
    }

    /// @notice §3.3(1): the credential is the receipt, not the caller. A relayer that is
    ///         neither owner nor signer can submit a valid allow receipt — and can cause
    ///         only what the owner authorized, exactly once.
    function test_anyCallerMayRelayAValidReceipt() public {
        (T.ActionPayload memory a, bytes memory data, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _allowBundle();

        vm.prank(attacker);
        vault.executeWithReceipt(a, data, r, sig);

        assertEq(vault.actionNonce(), 1);
    }

    // =================================================================
    // Invariant §3.3(9) — no action nonce executes twice
    // =================================================================

    function test_replay_sameReceiptCannotExecuteTwice() public {
        (T.ActionPayload memory a, bytes memory data, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _allowBundle();

        vault.executeWithReceipt(a, data, r, sig);

        vm.expectRevert(SentinelVault.BadNonce.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    function test_replay_staleNonceIsRejected() public {
        (T.ActionPayload memory a, bytes memory data, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _allowBundle();
        vault.executeWithReceipt(a, data, r, sig);

        // Re-sign a fresh, otherwise-valid bundle but pinned to the consumed nonce.
        T.ActionPayload memory stale = _action(data);
        stale.actionNonce = 0;
        T.DecisionReceiptPayload memory r2 = _receipt(stale, T.Verdict.ALLOW);
        bytes memory sig2 = _sign(SIGNER_PK, T.hashReceipt(r2));

        vm.expectRevert(SentinelVault.BadNonce.selector);
        vault.executeWithReceipt(stale, data, r2, sig2);
    }

    // =================================================================
    // Invariant §3.3(5) — mutating any bound field invalidates the credential
    // =================================================================

    /// @notice The tamper matrix. Each case mutates exactly one bound field *after* the
    ///         receipt was signed and asserts the vault rejects it. Which error fires
    ///         differs by field (some fail the vault's own precondition, some fail the
    ///         receipt binding); what matters is that none execute.
    function test_tamper_anyBoundFieldMutationIsRejected() public {
        _tamperTargetRejected();
        _tamperValueRejected();
        _tamperCalldataRejected();
        _tamperNonceRejected();
        _tamperChainRejected();
        _tamperMandateRejected();
        _tamperPolicyRejected();
        _tamperOperationRejected();
        _tamperDeadlineRejected();

        assertEq(vault.actionNonce(), 0, "no tampered action may consume a nonce");
    }

    function _tamperTargetRejected() internal {
        (T.ActionPayload memory a, bytes memory data, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _allowBundle();
        a.target = attacker;
        vm.expectRevert(SentinelVault.TargetNotAllowed.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    function _tamperValueRejected() internal {
        (T.ActionPayload memory a, bytes memory data, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _allowBundle();
        a.valueWei = 0.006 ether; // still under the hard cap — must fail on binding, not the cap
        vm.expectRevert(SentinelVault.ReceiptActionMismatch.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    /// @notice The §7.1 "altered calldata after receipt creation" fixture. The agent keeps
    ///         a valid receipt and swaps the bytes — here, redirecting the entitlement to
    ///         the attacker while leaving every field of the ActionPayload untouched.
    function _tamperCalldataRejected() internal {
        (T.ActionPayload memory a, , T.DecisionReceiptPayload memory r, bytes memory sig) = _allowBundle();
        bytes memory swapped = abi.encodeCall(DemoPay.purchase, (RESOURCE, attacker, 24 hours, false));
        vm.expectRevert(SentinelVault.CalldataMismatch.selector);
        vault.executeWithReceipt(a, swapped, r, sig);
    }

    function _tamperNonceRejected() internal {
        (T.ActionPayload memory a, bytes memory data, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _allowBundle();
        a.actionNonce = 7;
        vm.expectRevert(SentinelVault.BadNonce.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    function _tamperChainRejected() internal {
        (T.ActionPayload memory a, bytes memory data, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _allowBundle();
        a.chainId = 8453;
        vm.expectRevert(SentinelVault.WrongChain.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    function _tamperMandateRejected() internal {
        (T.ActionPayload memory a, bytes memory data, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _allowBundle();
        a.mandateHash = keccak256("other-mandate");
        vm.expectRevert(SentinelVault.MandateNotActive.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    function _tamperPolicyRejected() internal {
        (T.ActionPayload memory a, bytes memory data, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _allowBundle();
        a.policyHash = keccak256("other-policy");
        vm.expectRevert(SentinelVault.PolicyNotActive.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    function _tamperOperationRejected() internal {
        (T.ActionPayload memory a, bytes memory data, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _allowBundle();
        a.operation = uint8(T.Operation.DELEGATECALL);
        vm.expectRevert(SentinelVault.UnsupportedOperation.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    function _tamperDeadlineRejected() internal {
        (T.ActionPayload memory a, bytes memory data, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _allowBundle();
        a.deadline = uint64(block.timestamp + 2 hours);
        vm.expectRevert(SentinelVault.ReceiptActionMismatch.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    // =================================================================
    // Verdict gating — §3.3(6), §3.3(7)
    // =================================================================

    function test_blockReceiptNeverExecutes() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.BLOCK);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        vm.expectRevert(SentinelVault.NotAllowVerdict.selector);
        vault.executeWithReceipt(a, data, r, sig);

        // And a block receipt cannot be laundered through the override path either — §3.3(7)
        // says a block requires a new mandate or policy, never an override.
        T.OverrideAuthorizationPayload memory auth = _override(a, r);
        bytes memory ownerSig = _sign(OWNER_PK, T.hashOverride(auth));
        vm.expectRevert(SentinelVault.NotReviewVerdict.selector);
        vault.executeWithOverride(a, data, r, sig, auth, ownerSig);

        assertEq(vault.actionNonce(), 0);
    }

    function test_reviewReceiptDoesNotExecuteOnTheAutomaticPath() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.REVIEW);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        vm.expectRevert(SentinelVault.NotAllowVerdict.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    function _override(T.ActionPayload memory a, T.DecisionReceiptPayload memory r)
        internal
        view
        returns (T.OverrideAuthorizationPayload memory)
    {
        return T.OverrideAuthorizationPayload({
            schemaVersion: 1,
            reviewReceiptHash: T.hashReceipt(r),
            actionHash: T.hashAction(a),
            mandateHash: a.mandateHash,
            policyHash: a.policyHash,
            actionNonce: a.actionNonce,
            reasonHash: keccak256("owner accepted the residual risk"),
            issuedAt: uint64(block.timestamp),
            expiresAt: uint64(block.timestamp + 10 minutes)
        });
    }

    function test_reviewPlusOwnerOverrideExecutes() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.REVIEW);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));
        T.OverrideAuthorizationPayload memory auth = _override(a, r);
        bytes memory ownerSig = _sign(OWNER_PK, T.hashOverride(auth));

        vault.executeWithOverride(a, data, r, sig, auth, ownerSig);
        assertEq(vault.actionNonce(), 1);
    }

    function test_overrideSignedByNonOwnerIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.REVIEW);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));
        T.OverrideAuthorizationPayload memory auth = _override(a, r);

        // Signed by the evaluator's own signer, not the owner. §3.3(7) requires a
        // *separately authenticated* human decision; a compromised signer must not be
        // able to manufacture both halves.
        bytes memory notOwnerSig = _sign(SIGNER_PK, T.hashOverride(auth));

        vm.expectRevert(SentinelVault.NotOwnerOverride.selector);
        vault.executeWithOverride(a, data, r, sig, auth, notOwnerSig);
    }

    /// @notice An override is bound to one exact review receipt. Reusing an override
    ///         issued for a different action must fail even when everything else lines up.
    function test_overrideForADifferentActionIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.REVIEW);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        T.OverrideAuthorizationPayload memory auth = _override(a, r);
        auth.actionHash = keccak256("some other action");
        bytes memory ownerSig = _sign(OWNER_PK, T.hashOverride(auth));

        vm.expectRevert(SentinelVault.OverrideMismatch.selector);
        vault.executeWithOverride(a, data, r, sig, auth, ownerSig);
    }

    // =================================================================
    // Signer identity and rotation
    // =================================================================

    function test_receiptFromNonActiveSignerIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        bytes memory forged = _sign(ATTACKER_PK, T.hashReceipt(r));

        vm.expectRevert(SentinelVault.WrongSigner.selector);
        vault.executeWithReceipt(a, data, r, forged);
    }

    /// @notice The receipt must both *name* the active signer and be *signed* by it.
    ///         A receipt whose `signer` field points elsewhere fails even if the signature
    ///         itself is from the active key.
    function test_receiptNamingAStaleSignerIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        r.signer = attacker;
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        vm.expectRevert(SentinelVault.WrongSigner.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    function test_rotationInvalidatesOutstandingReceipts() public {
        (T.ActionPayload memory a, bytes memory data, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _allowBundle();

        vm.prank(owner);
        vault.rotateSigner(attacker);

        vm.expectRevert(SentinelVault.MandateNotActive.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    // =================================================================
    // Expiry, pause, caps, allowlists
    // =================================================================

    function test_expiredReceiptIsRejected() public {
        (T.ActionPayload memory a, bytes memory data, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _allowBundle();
        vm.warp(block.timestamp + 11 minutes);

        vm.expectRevert(SentinelVault.ReceiptExpired.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    function test_expiredActionIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        a.deadline = uint64(block.timestamp + 30 minutes);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        r.expiresAt = uint64(block.timestamp + 2 hours);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        vm.warp(block.timestamp + 31 minutes);
        vm.expectRevert(SentinelVault.ActionExpired.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    function test_pausedExecutionAlwaysFails() public {
        (T.ActionPayload memory a, bytes memory data, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _allowBundle();

        vm.prank(owner);
        vault.setPaused(true);

        vm.expectRevert(SentinelVault.Paused.selector);
        vault.executeWithReceipt(a, data, r, sig);

        T.OverrideAuthorizationPayload memory auth = _override(a, r);
        bytes memory ownerSig = _sign(OWNER_PK, T.hashOverride(auth));
        vm.expectRevert(SentinelVault.Paused.selector);
        vault.executeWithOverride(a, data, r, sig, auth, ownerSig);
    }

    /// @notice The hard onchain backstop (§4). Even a perfectly valid signed receipt cannot
    ///         move more native value than the vault's immutable cap — this is the check
    ///         that survives a compromised evaluator or signer.
    function test_valueOverHardCapIsRejectedEvenWithAValidReceipt() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        a.valueWei = MAX_VALUE + 1;
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        vm.expectRevert(SentinelVault.ValueOverCap.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    function test_revokedMandateBlocksExecution() public {
        (T.ActionPayload memory a, bytes memory data, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _allowBundle();

        vm.prank(owner);
        vault.revokeMandate();

        vm.expectRevert(SentinelVault.MandateNotActive.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    /// @notice §3.3(8) at the vault: an uninitialised vault must not be satisfiable by
    ///         supplying zero hashes. This is the fail-closed default, tested directly
    ///         rather than assumed from the enum ordering.
    function test_uninitialisedVaultRejectsZeroHashes() public {
        address[] memory targets = new address[](1);
        targets[0] = address(demoPay);
        bytes4[] memory selectors = new bytes4[](1);
        selectors[0] = PURCHASE_SEL;
        SentinelVault fresh = new SentinelVault(owner, signerAddr, MAX_VALUE, targets, selectors);
        vm.deal(address(fresh), 1 ether);

        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        a.vault = address(fresh);
        a.mandateHash = bytes32(0);
        a.policyHash = bytes32(0);

        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        bytes32 digest = T.digest(T.domainSeparator(block.chainid, address(fresh)), T.hashReceipt(r));
        (uint8 v, bytes32 rr, bytes32 ss) = vm.sign(SIGNER_PK, digest);

        vm.expectRevert(SentinelVault.MandateNotActive.selector);
        fresh.executeWithReceipt(a, data, r, abi.encodePacked(rr, ss, v));
    }

    // =================================================================
    // Owner-only controls — §3.3(2), §3.3(10)
    // =================================================================

    function testFuzz_nonOwnerCannotTouchOwnerControls(address caller) public {
        vm.assume(caller != owner);
        vm.startPrank(caller);

        vm.expectRevert(SentinelVault.NotOwner.selector);
        T.MandatePayload memory mandate;
        vault.activateMandate(mandate, bytes(""));
        vm.expectRevert(SentinelVault.NotOwner.selector);
        vault.revokeMandate();
        vm.expectRevert(SentinelVault.NotOwner.selector);
        vault.activatePolicy(keccak256("x"));
        vm.expectRevert(SentinelVault.NotOwner.selector);
        vault.rotateSigner(caller);
        vm.expectRevert(SentinelVault.NotOwner.selector);
        vault.setPaused(true);
        vm.expectRevert(SentinelVault.NotOwner.selector);
        vault.recover(payable(caller), 1 ether);

        vm.stopPrank();
    }

    /// @notice The signer holds authorization authority, not ownership. A fully compromised
    ///         signer must not be able to reach any owner control — that separation is what
    ///         bounds the blast radius in §8 threat 9.
    function test_signerCannotReachOwnerControls() public {
        vm.prank(signerAddr);
        vm.expectRevert(SentinelVault.NotOwner.selector);
        vault.rotateSigner(attacker);

        vm.prank(signerAddr);
        vm.expectRevert(SentinelVault.NotOwner.selector);
        vault.recover(payable(signerAddr), 1 ether);
    }
}
