// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {SentinelVault} from "../src/SentinelVault.sol";
import {SentinelTypes as T} from "../src/types/SentinelTypes.sol";
import {DemoPay} from "../src/demo/DemoPay.sol";
import {MandateTestHelper} from "./MandateTestHelper.sol";

/// @title SentinelVault — the halves nothing asserted (R3-F5, R3-F6, R3-F7)
///
/// @dev WHY THIS FILE EXISTS. The D-055(e) review found three vault surfaces where the shipped
///      behaviour is CORRECT and the instrument that would catch a regression is absent. All
///      three are the same shape as defects already fixed elsewhere, surviving one language or
///      one field away from where a reviewer demonstrated them:
///
///        R3-F5  deleting the POLICY half of the §3.3(5) receipt binding left Foundry 75/75
///               GREEN, while deleting the mandate half was killed by one test. This is `D-05`
///               — one code folding two conditions with only one witness — FIXED in TypeScript
///               and never generalised to Solidity. `scripts/mutate.sh`'s S5 deletes BOTH halves
///               at once and therefore reports CAUGHT, masking it.
///        R3-F6  all three of the vault's `block.timestamp` comparisons were unpinned in BOTH
///               directions (6 surviving mutants), while the value ceiling is pinned in both.
///               **The first version of this file pinned TWO of the three and said "every".
///               `executeWithOverride`'s `auth.expiresAt` was found still surviving by an
///               independent verifier (D-057(5)) and is pinned below.**
///               This is `D-06` — a boundary pinned only from outside — closed for the engine's
///               ten comparison edges and never carried to the vault's.
///        R3-F7  five of the vault's eight events could be made to state something false with
///               75/75 green: exactly the five D-043 did not touch.
///               **The first version of this file asserted the WRONG five — it included
///               `Recovered`, already covered by D-043, and omitted `MandateRevoked`, which
///               nothing anywhere asserted. Both are covered below.**
///
///      COVERAGE BOUNDARY. Every test here asserts an INSTRUMENT, not a behaviour change. The
///      vault was correct before this file and is correct after it; what changes is that a
///      regression now fails. Nothing here is evidence that a verdict is right.
contract SentinelVaultBindingTest is MandateTestHelper {
    SentinelVault internal vault;
    DemoPay internal demoPay;

    uint256 internal constant OWNER_PK = 0xA11CE;
    uint256 internal constant SIGNER_PK = 0x519E4;

    address internal owner;
    address internal signerAddr;

    uint256 internal constant MAX_VALUE = 0.01 ether;
    bytes32 internal constant RESOURCE = keccak256("weather-basic-24h");
    bytes32 internal MANDATE_HASH;
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

        MANDATE_HASH = _activateTestMandate(
            vault, OWNER_PK, owner, signerAddr, address(demoPay), PURCHASE_SEL, MAX_VALUE,
            POLICY_HASH, keccak256("mandate-1")
        );

        vm.warp(1_000_000);
    }

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

    function _signedReceipt(T.ActionPayload memory a)
        internal
        view
        returns (T.DecisionReceiptPayload memory r, bytes memory sig)
    {
        r = _receipt(a, T.Verdict.ALLOW);
        sig = _sign(SIGNER_PK, T.hashReceipt(r));
    }

    // =====================================================================
    // R3-F5 — the §3.3(5) receipt binding has TWO halves and only one was asserted
    // =====================================================================

    /// @dev THE ARGUMENT: **a receipt authorises an action only if it is bound to BOTH the
    ///      mandate and the policy that action names.** `_checkReceipt` tests them in one
    ///      `if` with an `||`, so a mutant deleting either half must be killed by a test that
    ///      names that half. Only the mandate half was.
    ///
    ///      The mutation this kills: dropping `receipt.policyHash != action.policyHash` from
    ///      the conjunction. Measured to survive all 75 Foundry tests before this test existed.
    function test_receiptBoundToPolicy_mismatchIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        (T.DecisionReceiptPayload memory r, ) = _signedReceipt(a);

        // Only the POLICY half is wrong. The mandate half still matches, so a vault that
        // checks only the mandate would accept this.
        r.policyHash = keccak256("a different policy");
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        vm.expectRevert(SentinelVault.ReceiptBindingMismatch.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    /// @dev The mandate half, kept as the paired control. Without it a vault that checked
    ///      only the policy would satisfy the test above.
    function test_receiptBoundToMandate_mismatchIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        (T.DecisionReceiptPayload memory r, ) = _signedReceipt(a);

        r.mandateHash = keccak256("a different mandate");
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        vm.expectRevert(SentinelVault.ReceiptBindingMismatch.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    /// @dev The positive control: a correctly bound receipt still executes. Without it,
    ///      "revert on everything" satisfies both rows above.
    function test_correctlyBoundReceiptStillExecutes() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        (T.DecisionReceiptPayload memory r, bytes memory sig) = _signedReceipt(a);
        vault.executeWithReceipt(a, data, r, sig);
        assertEq(vault.actionNonce(), 1);
    }

    // =====================================================================
    // R3-F6 — every timestamp boundary, pinned in BOTH directions
    // =====================================================================

    /// @dev THE ARGUMENT: **a deadline is inclusive — an action at exactly its deadline is
    ///      still authorised — so `>` and `>=` are different rules and the boundary must be
    ///      pinned from both sides.** Pinning only "one second past" leaves `>` → `>=` alive,
    ///      which REJECTS the commonest real case: the value exactly at the limit.

    /// @dev ONE DIMENSION AT A TIME, and the first draft of these two got it wrong. The default
    ///      receipt expires 10 minutes out while the action deadline is an hour out, so warping
    ///      to the deadline crossed BOTH boundaries and the test failed on `ReceiptExpired` —
    ///      rejected by a different check than the one under test, which is this project's
    ///      failure mode 7. The receipt's expiry is pushed past the deadline so only the
    ///      deadline is in question.
    function test_actionDeadline_atTheBoundaryIsStillValid() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        r.expiresAt = uint64(uint256(a.deadline) + 1 hours);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        vm.warp(a.deadline); // exactly AT the deadline
        vault.executeWithReceipt(a, data, r, sig);
        assertEq(vault.actionNonce(), 1);
    }

    function test_actionDeadline_oneSecondPastIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        r.expiresAt = uint64(uint256(a.deadline) + 1 hours);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        vm.warp(uint256(a.deadline) + 1);
        vm.expectRevert(SentinelVault.ActionExpired.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    function test_receiptExpiry_atTheBoundaryIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        (T.DecisionReceiptPayload memory r, bytes memory sig) = _signedReceipt(a);

        vm.warp(r.expiresAt); // exactly AT expiry
        vm.expectRevert(SentinelVault.ReceiptExpired.selector);
        vault.executeWithReceipt(a, data, r, sig);
        assertEq(vault.actionNonce(), 0);
    }

    function test_receiptExpiry_oneSecondPastIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        (T.DecisionReceiptPayload memory r, bytes memory sig) = _signedReceipt(a);

        vm.warp(uint256(r.expiresAt) + 1);
        vm.expectRevert(SentinelVault.ReceiptExpired.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    /// @dev THE THIRD TIMESTAMP BOUNDARY — `executeWithOverride`'s `auth.expiresAt`.
    ///
    ///      **THIS WAS MISSED BY THE FIRST VERSION OF THIS FILE, WHICH CLAIMED "every timestamp
    ///      boundary" AND "all three" WHILE PINNING TWO.** An independent verifier re-derived
    ///      from R3-F6's own mutant set instead of from this file's description of it and found
    ///      `auth.expiresAt` surviving in BOTH directions with 89/89 green. It is the override
    ///      path — the second route by which funds move, on a REVIEW verdict — so it is the
    ///      boundary least covered and most consequential.
    ///
    ///      That is the same defect this file exists to close, committed inside the closing of
    ///      it: the repair generalised the demonstration and not the argument.
    function test_overrideExpiry_atTheBoundaryIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.REVIEW);
        r.expiresAt = uint64(block.timestamp + 2 hours);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));
        T.OverrideAuthorizationPayload memory auth = _override(a, r);
        bytes memory ownerSig = _sign(OWNER_PK, T.hashOverride(auth));

        vm.warp(auth.expiresAt); // exactly AT the override's expiry
        vm.expectRevert(SentinelVault.OverrideExpired.selector);
        vault.executeWithOverride(a, data, r, sig, auth, ownerSig);
        assertEq(vault.actionNonce(), 0);
    }

    function test_overrideExpiry_oneSecondPastIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.REVIEW);
        r.expiresAt = uint64(block.timestamp + 2 hours);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));
        T.OverrideAuthorizationPayload memory auth = _override(a, r);
        bytes memory ownerSig = _sign(OWNER_PK, T.hashOverride(auth));

        vm.warp(uint256(auth.expiresAt) + 1);
        vm.expectRevert(SentinelVault.OverrideExpired.selector);
        vault.executeWithOverride(a, data, r, sig, auth, ownerSig);
    }

    /// @dev The value ceiling, pinned in both directions ALREADY, kept here as the control
    ///      R3-F6 names: it is the comparison that was correctly pinned, so if these two ever
    ///      fail the harness itself is wrong rather than the boundary.
    function test_valueCeiling_atTheCapIsAllowed() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        a.valueWei = MAX_VALUE; // exactly at the immutable cap
        (T.DecisionReceiptPayload memory r, bytes memory sig) = _signedReceipt(a);
        vault.executeWithReceipt(a, data, r, sig);
        assertEq(vault.actionNonce(), 1);
    }

    function test_valueCeiling_oneWeiOverIsRejected() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        a.valueWei = MAX_VALUE + 1;
        (T.DecisionReceiptPayload memory r, bytes memory sig) = _signedReceipt(a);
        vm.expectRevert(SentinelVault.ValueOverCap.selector);
        vault.executeWithReceipt(a, data, r, sig);
    }

    // =====================================================================
    // R3-F7 — the five events that could state something false
    // =====================================================================

    /// @dev THE ARGUMENT: **an event is the only onchain record of what happened, so a test
    ///      that an event FIRED is not a test that it is TRUE.** D-043 pinned three of eight;
    ///      the other five could carry any values with the suite green. `SignerRotated` is the
    ///      sharpest — rotation history exists nowhere else in state, so a wrong `previousSigner`
    ///      erases the only record of signer epochs — and `PausedSet` is second, because a
    ///      monitor keys on it.
    ///
    ///      SIX are asserted below, not five: the five D-043 left untouched
    ///      (`SignerRotated`, `PausedSet`, `MandateActivated`, `PolicyActivated`,
    ///      `MandateRevoked`) plus `Recovered`, which D-043 already covers and which is kept
    ///      as a second, independent witness rather than removed.

    function test_SignerRotated_statesBothEpochsTruthfully() public {
        address newSigner = vm.addr(0xC0FFEE);
        address before_ = vault.signer();
        vm.expectEmit(true, true, false, false, address(vault));
        emit SentinelVault.SignerRotated(before_, newSigner);
        vm.prank(owner);
        vault.rotateSigner(newSigner);
        assertEq(vault.signer(), newSigner);
    }

    function test_PausedSet_statesTheNewStateTruthfully() public {
        vm.expectEmit(false, false, false, true, address(vault));
        emit SentinelVault.PausedSet(true);
        vm.prank(owner);
        vault.setPaused(true);
        assertTrue(vault.paused());

        vm.expectEmit(false, false, false, true, address(vault));
        emit SentinelVault.PausedSet(false);
        vm.prank(owner);
        vault.setPaused(false);
        assertFalse(vault.paused());
    }

    function test_MandateActivated_statesTheActivatedHash() public {
        (T.MandatePayload memory mandate, bytes memory signature) = _mandateEnvelope(
            vault, OWNER_PK, owner, signerAddr, address(demoPay), DemoPay.purchase.selector,
            MAX_VALUE, POLICY_HASH, keccak256("mandate-2")
        );
        bytes32 h = T.hashMandate(mandate);
        vm.expectEmit(true, false, false, false, address(vault));
        emit SentinelVault.MandateActivated(h);
        vm.prank(owner);
        vault.activateMandate(mandate, signature);
        assertEq(vault.activeMandateHash(), h);
    }

    function test_PolicyActivated_statesTheActivatedHash() public {
        bytes32 h = keccak256("policy-2");
        vm.expectEmit(true, false, false, false, address(vault));
        emit SentinelVault.PolicyActivated(h);
        vm.prank(owner);
        vault.activatePolicy(h);
        assertEq(vault.activePolicyHash(), h);
    }

    /// @dev `MandateRevoked` — THE EVENT THE FIRST VERSION OF THIS FILE MISSED WHILE CLAIMING
    ///      "All five are asserted". It picked `Recovered`, which D-043 had ALREADY covered
    ///      (`test_recoverEventReportsTheAmountItActuallyMoved` in the backstops suite), and
    ///      left `MandateRevoked` — a genuine survivor in the adjudication — asserted by
    ///      NOTHING anywhere in the repository. Every revocation could log the zero hash
    ///      instead of the mandate it revoked, 89/89 green.
    ///
    ///      Rotation and revocation history exist nowhere else in state, which is why these two
    ///      matter more than the hashes readable from storage.
    function test_MandateRevoked_statesTheRevokedHash() public {
        vm.expectEmit(true, false, false, false, address(vault));
        emit SentinelVault.MandateRevoked(MANDATE_HASH);
        vm.prank(owner);
        vault.revokeMandate();
        assertEq(vault.activeMandateHash(), bytes32(0));
    }

    function test_Recovered_statesRecipientAndAmount() public {
        address payable to = payable(vm.addr(0xD00D));
        uint256 amount = 1 ether;
        uint256 balanceBefore = to.balance;
        vm.expectEmit(true, false, false, true, address(vault));
        emit SentinelVault.Recovered(to, amount);
        vm.prank(owner);
        vault.recover(to, amount);
        assertEq(to.balance, balanceBefore + amount);
    }
}
