// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {SentinelVault} from "../src/SentinelVault.sol";
import {SentinelTypes as T} from "../src/types/SentinelTypes.sol";
import {DemoPay} from "../src/demo/DemoPay.sol";

/// @notice Observes the vault's `actionNonce` DURING the external call.
///
/// @dev This is the only guard-independent way to see §3.3(9)'s ordering. From outside the
///      transaction the nonce reads 1 whether it was bumped before or after the call, and the
///      reentrancy guard rejects a callback for a reason that has nothing to do with the
///      nonce — so a suite can be fully green while the two defences it presents as
///      independent are tested by the same test. Reading the nonce from inside the callee is
///      the observation that separates them.
contract NonceObserver {
    SentinelVault public immutable vault;
    uint256 public nonceDuringCall = type(uint256).max;

    constructor(SentinelVault v) {
        vault = v;
    }

    fallback() external payable {
        nonceDuringCall = vault.actionNonce();
    }

    receive() external payable {
        nonceDuringCall = vault.actionNonce();
    }
}

/// @title SentinelVault — the backstops nothing else exercised
/// @notice Written to close the Solidity half of the A-028 coverage debt.
///
/// @dev WHY A SECOND FILE RATHER THAN MORE CASES IN `SentinelVault.t.sol`. Every test here
///      exists because a specific deliberate defect SURVIVED a fully green 43-test Foundry
///      run. That provenance is the point: these are not tests someone thought of while
///      reading the contract — they are the ones the contract's own author demonstrably did
///      not think of, and a reader deciding how much to trust the suite should be able to see
///      which is which. Each test names the mutation it kills.
///
/// @dev COVERAGE BOUNDARY. Same as the sibling suite: this proves the vault ENFORCES a
///      receipt, never that the receipt carried a correct verdict.
contract SentinelVaultBackstopsTest is Test {
    SentinelVault internal vault;
    DemoPay internal demoPay;

    uint256 internal constant OWNER_PK = 0xA11CE;
    uint256 internal constant SIGNER_PK = 0x519E4;

    address internal owner;
    address internal signerAddr;

    uint256 internal constant MAX_VALUE = 0.01 ether;
    bytes32 internal constant RESOURCE = keccak256("weather-basic-24h");
    bytes32 internal constant MANDATE_HASH = keccak256("mandate-1");
    bytes32 internal constant POLICY_HASH = keccak256("policy-1");

    bytes4 internal constant PURCHASE_SEL = DemoPay.purchase.selector;

    function setUp() public {
        owner = vm.addr(OWNER_PK);
        signerAddr = vm.addr(SIGNER_PK);
        demoPay = new DemoPay();

        address[] memory targets = new address[](1);
        targets[0] = address(demoPay);
        bytes4[] memory selectors = new bytes4[](1);
        selectors[0] = PURCHASE_SEL;

        vault = new SentinelVault(owner, signerAddr, MAX_VALUE, targets, selectors);
        vm.deal(address(vault), 10 ether);

        vm.startPrank(owner);
        vault.activateMandate(MANDATE_HASH);
        vault.activatePolicy(POLICY_HASH);
        vm.stopPrank();

        vm.warp(1_000_000);
    }

    // =================================================================
    // Fixture builders — same shapes as the sibling suite
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

    function _sign(uint256 pk, bytes32 structHash) internal view returns (bytes memory) {
        bytes32 digest = T.digest(T.domainSeparator(block.chainid, address(vault)), structHash);
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(pk, digest);
        return abi.encodePacked(r, s, v);
    }

    // =================================================================
    // §3.3(9) ordering — the two defences, told apart
    // =================================================================

    /// @notice Kills S7 ("consume the nonce AFTER the external call").
    ///
    /// @dev A-028's sharpest coverage finding: §3.3(9) says the nonce is consumed before the
    ///      external call, the contract's own comment says ordering "is the point", and
    ///      nothing verified it. The reentrancy guard masks it — move the increment after the
    ///      call and every one of the 43 tests still passed, because the only test that could
    ///      have noticed re-enters and is rejected by `nonReentrant` first. Two defences
    ///      presented as independent were being tested by one.
    ///
    ///      Adapted from `docs/review-2026-08-15/artifacts/OrderingProbe.t.sol`, written and
    ///      verified by the reviewer who found the gap.
    function test_nonceIsConsumedBeforeTheExternalCall() public {
        // A vault whose single allowlisted target is the observer, so the executed call
        // lands in a contract that can read the vault back.
        address predicted = vm.computeCreateAddress(address(this), vm.getNonce(address(this)) + 1);
        address[] memory targets = new address[](1);
        targets[0] = predicted;
        bytes4 sel = bytes4(keccak256("anything()"));
        bytes4[] memory selectors = new bytes4[](1);
        selectors[0] = sel;

        SentinelVault probeVault = new SentinelVault(owner, signerAddr, 1 ether, targets, selectors);
        NonceObserver obs = new NonceObserver(probeVault);
        require(address(obs) == predicted, "address prediction failed");

        vm.deal(address(probeVault), 10 ether);
        vm.startPrank(owner);
        probeVault.activateMandate(MANDATE_HASH);
        probeVault.activatePolicy(POLICY_HASH);
        vm.stopPrank();

        bytes memory data = abi.encodePacked(sel);
        T.ActionPayload memory a = T.ActionPayload({
            schemaVersion: 1,
            chainId: block.chainid,
            vault: address(probeVault),
            actionNonce: 0,
            target: address(obs),
            valueWei: 0.1 ether,
            dataHash: keccak256(data),
            operation: uint8(T.Operation.CALL),
            mandateHash: MANDATE_HASH,
            policyHash: POLICY_HASH,
            deadline: uint64(block.timestamp + 1 hours)
        });
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);

        bytes32 digest = T.digest(T.domainSeparator(block.chainid, address(probeVault)), T.hashReceipt(r));
        (uint8 v, bytes32 rr, bytes32 ss) = vm.sign(SIGNER_PK, digest);
        probeVault.executeWithReceipt(a, data, r, abi.encodePacked(rr, ss, v));

        assertEq(obs.nonceDuringCall(), 1, "the nonce was NOT consumed before the external call");
        assertEq(probeVault.actionNonce(), 1);
    }

    // =================================================================
    // Hard backstops that only fire when everything else is valid
    // =================================================================

    /// @notice Kills S1 ("delete the WrongVault check").
    ///
    /// @dev The sibling suite tampers with every bound field EXCEPT `vault`, and the gap is
    ///      invisible from the outside: deleting the check still leaves the transaction
    ///      reverting, just on the receipt binding two checks later. Only asserting the exact
    ///      error tells the two apart — which is why this asserts the selector rather than
    ///      merely that the call failed.
    function test_actionNamingADifferentVaultIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        a.vault = address(0xBEEF);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        vm.expectRevert(SentinelVault.WrongVault.selector);
        vault.executeWithReceipt(a, data, r, sig);
        assertEq(vault.actionNonce(), 0);
    }

    /// @notice Kills S3 ("delete the SelectorNotAllowed check").
    ///
    /// @dev The vault's selector allowlist is a §4 hard backstop — the layer that still holds
    ///      when the evaluator and signer are both compromised — and nothing exercised it. The
    ///      receipt here is entirely valid: correct signer, correct binding, allowlisted
    ///      target. Only the four leading bytes are off the list.
    function test_selectorOffTheVaultAllowlistIsRejected() public {
        bytes memory data = abi.encodeWithSelector(bytes4(keccak256("notOnTheList(uint256)")), uint256(1));
        T.ActionPayload memory a = _action(data);
        a.dataHash = keccak256(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        vm.expectRevert(SentinelVault.SelectorNotAllowed.selector);
        vault.executeWithReceipt(a, data, r, sig);
        assertEq(vault.actionNonce(), 0);
    }

    /// @notice Kills S2 ("delete the CalldataTooShort check").
    ///
    /// @dev Without the length check, `bytes4(callData[:4])` reverts on the slice instead —
    ///      so the transaction still fails and a test that only asserted "it reverts" would
    ///      pass either way. The named error is the difference between a deliberate refusal
    ///      and an out-of-bounds accident.
    function test_calldataShorterThanASelectorIsRejected() public {
        bytes memory data = hex"c188";
        T.ActionPayload memory a = _action(data);
        a.dataHash = keccak256(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        vm.expectRevert(SentinelVault.CalldataTooShort.selector);
        vault.executeWithReceipt(a, data, r, sig);
        assertEq(vault.actionNonce(), 0);
    }

    /// @notice Kills S18 ("drop the dataHash recompute and trust the supplied digest").
    ///
    /// @dev §5.3 says the vault recomputes the digest from the bytes it will actually pass
    ///      on. The bound `dataHash` here names OTHER bytes and the receipt is signed over
    ///      that action, so every binding check agrees with itself — the only thing standing
    ///      between the signed intent and different executed bytes is the recompute. Deleting
    ///      it executes the supplied calldata under a receipt that committed to something
    ///      else, which is §3.3(5) failing silently.
    function test_dataHashIsRecomputedFromTheBytesActuallyPassedOn() public {
        bytes memory executed = _callData();
        bytes memory committed = abi.encodeCall(DemoPay.purchase, (RESOURCE, owner, 48 hours, false));

        T.ActionPayload memory a = _action(executed);
        a.dataHash = keccak256(committed);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        vm.expectRevert(SentinelVault.CalldataMismatch.selector);
        vault.executeWithReceipt(a, executed, r, sig);
        assertEq(vault.actionNonce(), 0);
    }

    /// @notice Kills S5 ("delete the ReceiptBindingMismatch check").
    ///
    /// @dev The receipt names this exact action — `actionHash` matches — but claims a
    ///      different mandate. Without the binding check a signer could issue one receipt
    ///      whose stated authority is a mandate the action was never evaluated against, and
    ///      the vault would accept it because every other field lines up.
    function test_receiptClaimingADifferentMandateIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        r.mandateHash = keccak256("a mandate this action was never evaluated against");
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        vm.expectRevert(SentinelVault.ReceiptBindingMismatch.selector);
        vault.executeWithReceipt(a, data, r, sig);
        assertEq(vault.actionNonce(), 0);
    }

    /// @notice Kills S17 ("drop the zero-hash guard on activePolicyHash").
    ///
    /// @dev The sibling suite's uninitialised-vault test stops at the MANDATE guard, because
    ///      that check runs first and both hashes are zero there. The policy guard therefore
    ///      had no test at all. This vault has a mandate active and no policy, so an action
    ///      supplying `policyHash == 0` would match an uninitialised slot exactly — the
    ///      §3.3(8) fail-closed default, one layer down.
    function test_zeroPolicyHashDoesNotMatchAnUnsetPolicy() public {
        address[] memory targets = new address[](1);
        targets[0] = address(demoPay);
        bytes4[] memory selectors = new bytes4[](1);
        selectors[0] = PURCHASE_SEL;
        SentinelVault fresh = new SentinelVault(owner, signerAddr, MAX_VALUE, targets, selectors);
        vm.deal(address(fresh), 1 ether);

        vm.prank(owner);
        fresh.activateMandate(MANDATE_HASH);

        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        a.vault = address(fresh);
        a.policyHash = bytes32(0);

        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        bytes32 digest = T.digest(T.domainSeparator(block.chainid, address(fresh)), T.hashReceipt(r));
        (uint8 v, bytes32 rr, bytes32 ss) = vm.sign(SIGNER_PK, digest);

        vm.expectRevert(SentinelVault.PolicyNotActive.selector);
        fresh.executeWithReceipt(a, data, r, abi.encodePacked(rr, ss, v));
    }

    // =================================================================
    // The override path — §3.3(7)
    // =================================================================

    /// @notice Kills S14 ("drop actionNonce from the override binding").
    ///
    /// @dev The override names a nonce so it authorises ONE execution at one point in the
    ///      sequence. Drop that field from the comparison and an override issued for nonce N
    ///      still satisfies the check at nonce N+1 — the owner's one-time consent becomes
    ///      reusable for as long as the review receipt lives.
    function test_overrideNamingADifferentNonceIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.REVIEW);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        T.OverrideAuthorizationPayload memory auth = _override(a, r);
        auth.actionNonce = a.actionNonce + 1;
        bytes memory ownerSig = _sign(OWNER_PK, T.hashOverride(auth));

        vm.expectRevert(SentinelVault.OverrideMismatch.selector);
        vault.executeWithOverride(a, data, r, sig, auth, ownerSig);
        assertEq(vault.actionNonce(), 0);
    }

    /// @notice Kills S15 ("drop mandate/policy from the override binding").
    ///
    /// @dev Same shape, different field: the override must name the authority the action was
    ///      evaluated under, or an owner who accepted a residual risk under one mandate has
    ///      unknowingly accepted it under another.
    function test_overrideNamingADifferentMandateIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.REVIEW);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        T.OverrideAuthorizationPayload memory auth = _override(a, r);
        auth.mandateHash = keccak256("some other mandate");
        bytes memory ownerSig = _sign(OWNER_PK, T.hashOverride(auth));

        vm.expectRevert(SentinelVault.OverrideMismatch.selector);
        vault.executeWithOverride(a, data, r, sig, auth, ownerSig);

        auth = _override(a, r);
        auth.policyHash = keccak256("some other policy");
        ownerSig = _sign(OWNER_PK, T.hashOverride(auth));

        vm.expectRevert(SentinelVault.OverrideMismatch.selector);
        vault.executeWithOverride(a, data, r, sig, auth, ownerSig);
        assertEq(vault.actionNonce(), 0);
    }

    /// @notice Kills S6 ("delete the OverrideExpired check").
    ///
    /// @dev The override window has to be separable from the receipt's, or the test only
    ///      proves the receipt expired. The review receipt here lives two hours and the
    ///      override ten minutes, so at +11 minutes exactly one of them has lapsed.
    function test_expiredOverrideIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        a.deadline = uint64(block.timestamp + 3 hours);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.REVIEW);
        r.expiresAt = uint64(block.timestamp + 2 hours);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        T.OverrideAuthorizationPayload memory auth = _override(a, r);
        bytes memory ownerSig = _sign(OWNER_PK, T.hashOverride(auth));

        vm.warp(block.timestamp + 11 minutes);
        vm.expectRevert(SentinelVault.OverrideExpired.selector);
        vault.executeWithOverride(a, data, r, sig, auth, ownerSig);
        assertEq(vault.actionNonce(), 0);
    }

    // =================================================================
    // Zero-address guards
    // =================================================================

    /// @notice Kills S10, S11 and S12 — the three `ZeroAddress` guards, none of which had a
    ///         test. Cheap to write, and the reason they are worth writing is that each one
    ///         bricks the vault in a different unrecoverable way: no owner means no controls
    ///         at all, a zero signer means no receipt can ever verify, and a recovery to the
    ///         zero address burns the balance the guard exists to rescue.
    function test_constructorRejectsAZeroOwnerOrSigner() public {
        address[] memory targets = new address[](0);
        bytes4[] memory selectors = new bytes4[](0);

        vm.expectRevert(SentinelVault.ZeroAddress.selector);
        new SentinelVault(address(0), signerAddr, MAX_VALUE, targets, selectors);

        vm.expectRevert(SentinelVault.ZeroAddress.selector);
        new SentinelVault(owner, address(0), MAX_VALUE, targets, selectors);
    }

    function test_rotateSignerRejectsTheZeroAddress() public {
        vm.prank(owner);
        vm.expectRevert(SentinelVault.ZeroAddress.selector);
        vault.rotateSigner(address(0));

        assertEq(vault.signer(), signerAddr, "a refused rotation must leave the signer intact");
    }

    function test_recoverRejectsTheZeroAddress() public {
        vm.prank(owner);
        vm.expectRevert(SentinelVault.ZeroAddress.selector);
        vault.recover(payable(address(0)), 1 ether);

        assertEq(address(vault).balance, 10 ether, "a refused recovery must move nothing");
    }
}
