// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {SentinelVault} from "../src/SentinelVault.sol";
import {SentinelTypes as T} from "../src/types/SentinelTypes.sol";
import {DemoPay} from "../src/demo/DemoPay.sol";
import {MandateTestHelper} from "./MandateTestHelper.sol";

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
contract SentinelVaultBackstopsTest is MandateTestHelper {
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
        bytes32 probeMandateHash = _activateTestMandate(
            probeVault, OWNER_PK, owner, signerAddr, address(obs), sel, 1 ether,
            POLICY_HASH, keccak256("probe-mandate")
        );

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
            mandateHash: probeMandateHash,
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
    /// @dev The sibling suite tampers with every bound field EXCEPT `vault`.
    ///
    ///      CORRECTION, 2026-08-15. This comment previously claimed that deleting the check
    ///      "still leaves the transaction reverting, just on the receipt binding two checks
    ///      later", and that only the exact selector tells the two apart. An independent
    ///      review measured it: the transaction SUCCEEDS. The receipt here is built from the
    ///      already-tampered action, so `receipt.actionHash` agrees with it and nothing
    ///      downstream objects — a vault executing an action that names a different vault.
    ///      The reviewer also found that only 2 of this file's 13 tests actually need the
    ///      selector rather than a bare `vm.expectRevert()`. The tests are right; the
    ///      justification was wrong, and it was the kind of wrong that sounds more rigorous
    ///      than the truth. Asserting the selector is still worth doing — it pins WHICH
    ///      refusal fired — but it is not what makes this test bite.
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

        bytes32 freshMandateHash = _activateTestMandate(
            fresh, OWNER_PK, owner, signerAddr, address(demoPay), PURCHASE_SEL, MAX_VALUE,
            POLICY_HASH, keccak256("fresh-mandate")
        );
        vm.prank(owner);
        fresh.activatePolicy(bytes32(0));

        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        a.vault = address(fresh);
        a.mandateHash = freshMandateHash;
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

    /// @notice The override binds to ONE EXACT REVIEW RECEIPT, and until an independent
    ///         review found it, nothing tested that term.
    ///
    /// @dev Dropping `auth.reviewReceiptHash != receiptHash` from the comparison survived all
    ///      60 tests. The other four terms are all functions of the ACTION, so they cannot
    ///      distinguish two decisions about the same action — and two such decisions are
    ///      ordinary: an evaluator that re-runs produces a second REVIEW receipt with a
    ///      different `decisionId`, `evidenceHash`, `reasonCodesHash` and expiry. Without this
    ///      term the owner's consent to ONE decision record silently authorises any of them,
    ///      including one issued later on different evidence. The contract's own comment at
    ///      `executeWithOverride` claims exactly this property.
    function test_overrideCannotBeReusedForADifferentReviewReceipt() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);

        // Two independently valid REVIEW receipts for the SAME action, differing only in the
        // decision they record — which is what an evaluator re-run produces.
        T.DecisionReceiptPayload memory first = _receipt(a, T.Verdict.REVIEW);
        T.DecisionReceiptPayload memory second = _receipt(a, T.Verdict.REVIEW);
        second.decisionId = keccak256("decision-2");
        second.evidenceHash = keccak256("different evidence");
        second.reasonCodesHash = keccak256("different reasons");
        second.expiresAt = uint64(block.timestamp + 20 minutes);
        bytes memory secondSig = _sign(SIGNER_PK, T.hashReceipt(second));

        // The owner signs an override naming the FIRST receipt only.
        T.OverrideAuthorizationPayload memory auth = _override(a, first);
        bytes memory ownerSig = _sign(OWNER_PK, T.hashOverride(auth));

        vm.expectRevert(SentinelVault.OverrideMismatch.selector);
        vault.executeWithOverride(a, data, second, secondSig, auth, ownerSig);
        assertEq(vault.actionNonce(), 0);
    }

    /// @notice A failed external call must revert the whole execution, not consume a nonce and
    ///         report success.
    ///
    /// @dev `CallFailed` was asserted by no test in the suite. Deleting the `if (!ok) revert`
    ///      survived all 60: the vault would consume the nonce, emit `ActionExecuted`, and
    ///      return the revert data as if it were a return value — a receipt in the log for an
    ///      action that did not happen, and the nonce spent so it cannot be retried.
    ///
    ///      The failure is produced honestly, by starving the vault of the native value the
    ///      action moves, rather than by a target written to revert.
    function test_aFailedExternalCallRevertsRatherThanConsumingTheNonce() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        vm.deal(address(vault), 0);

        vm.expectRevert();
        vault.executeWithReceipt(a, data, r, sig);
        assertEq(vault.actionNonce(), 0, "a failed call must not consume the nonce");
    }

    /// @notice The execution event reports the nonce the action was BOUND to, not the
    ///         post-increment value.
    ///
    /// @dev No test in the Solidity suite asserted any event at all, so two mutations
    ///      survived: emitting `actionNonce` (already incremented) instead of
    ///      `action.actionNonce`, and `recover` moving the whole balance while the event says
    ///      `amount`. The log is what an auditor reconstructs the history from; an event that
    ///      lies is a receipt that lies.
    function test_executionEventReportsTheBoundNonceAndTheActualAmount() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        vm.expectEmit(true, true, false, true, address(vault));
        emit SentinelVault.ActionExecuted(T.hashAction(a), a.actionNonce, r.decisionId, false);
        vault.executeWithReceipt(a, data, r, sig);
    }

    function test_recoverEventReportsTheAmountItActuallyMoved() public {
        address payable to = payable(address(0xD00D));
        uint256 amount = 1 ether;

        vm.expectEmit(true, false, false, true, address(vault));
        emit SentinelVault.Recovered(to, amount);
        vm.prank(owner);
        vault.recover(to, amount);

        assertEq(to.balance, amount, "the event's amount is not what moved");
        assertEq(address(vault).balance, 9 ether, "recover moved more than it reported");
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

    /// @notice THE VAULT PLACES NO LIMIT ON ERC20 AUTHORITY. This test asserts the LIMIT, not
    ///         a protection, and it is here so the limit cannot regress into an assumption.
    ///
    /// @dev Found by an independent adversarial review, 2026-08-16, and recorded as D-042.
    ///      §7.1 listed "evaluator or signer compromise scenario within the vault's hard caps"
    ///      and §5.7.1/D-026 calls the vault's ceiling "a THIRD ceiling, independent of the
    ///      mandate-and-policy intersection" — neither said the ceiling is NATIVE-VALUE ONLY.
    ///
    ///      One valid ALLOW receipt for `approve(spender, type(uint256).max)` passes every
    ///      onchain check: pause, chain, vault, nonce, deadline, mandate, policy, operation,
    ///      dataHash, target allowlist, selector allowlist. The wei ceiling never engages
    ///      because `valueWei` is zero. `PolicyPayload.maxAllowanceIncreaseBaseUnits` exists
    ///      precisely because unlimited approval is the flagship Case 2 attack, and the vault
    ///      has no counterpart — so that attack is refused by the CONFORMANCE EVALUATOR with
    ///      nothing behind it.
    ///
    ///      This is a deliberate v1 boundary (§2: do not invent production custody; a
    ///      vault-side token cap would partly mask what the harness measures), NOT a defect
    ///      to fix quietly. If a per-action allowance ceiling is ever added, this test should
    ///      fail — and that failure is the signal to update §7.1 and the v1.1 register, not to
    ///      delete the test.
    function test_LIMIT_vaultCapsNativeValueOnlyAndNotTokenAuthority() public {
        TokenStub token = new TokenStub();
        address[] memory targets = new address[](1);
        targets[0] = address(token);
        bytes4[] memory selectors = new bytes4[](1);
        selectors[0] = TokenStub.approve.selector;

        SentinelVault v = new SentinelVault(owner, signerAddr, MAX_VALUE, targets, selectors);
        bytes32 tokenMandateHash = _activateTestMandate(
            v, OWNER_PK, owner, signerAddr, address(token), TokenStub.approve.selector,
            MAX_VALUE, POLICY_HASH, keccak256("token-mandate")
        );

        address attacker = address(0xBAD);
        bytes memory data = abi.encodeCall(TokenStub.approve, (attacker, type(uint256).max));

        T.ActionPayload memory a = T.ActionPayload({
            schemaVersion: 1,
            chainId: block.chainid,
            vault: address(v),
            actionNonce: v.actionNonce(),
            target: address(token),
            valueWei: 0, // the wei ceiling is never consulted
            dataHash: keccak256(data),
            operation: uint8(T.Operation.CALL),
            mandateHash: tokenMandateHash,
            policyHash: POLICY_HASH,
            deadline: uint64(block.timestamp + 1 hours)
        });
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        bytes memory sig = _signFor(v, SIGNER_PK, T.hashReceipt(r));

        vm.prank(attacker); // execution is permissionless; the receipt is the authority
        v.executeWithReceipt(a, data, r, sig);

        assertEq(
            token.allowance(address(v), attacker),
            type(uint256).max,
            "REGRESSION or REPAIR: the vault now constrains token authority - see D-042"
        );
        assertEq(v.actionNonce(), 1, "one nonce consumed for unlimited token authority");
    }

    /// @notice THE NATIVE CEILING IS PER-ACTION AND BOUNDS NOTHING IN AGGREGATE. Like the
    ///         test above, this asserts a LIMIT rather than a protection, so the limit cannot
    ///         regress into an assumption.
    ///
    /// @dev Found by round five's vault lens, 2026-08-17, recorded as A-063. D-042 corrected
    ///      §7.1 to say the hard caps "bound the NATIVE-VALUE dimension only". **They do not
    ///      bound it either.** `maxNativeValueWei` is compared once per action, and no
    ///      cumulative, rate-limited or velocity bound exists anywhere in `contracts/src`.
    ///
    ///      So the correction to a claim that overstated containment ITSELF overstated
    ///      containment, in the one dimension it had just narrowed to. That is why this test
    ///      exists rather than a sentence: the previous two attempts at this row were prose.
    ///
    ///      Under the threat model §7.1 names — evaluator or signer compromise — the attacker
    ///      mints one receipt per nonce at exactly the ceiling. `execute` is permissionless, so
    ///      the relayer needs no key. Only PAUSE bounds this, and pause is an owner REACTION,
    ///      not a cap.
    ///
    ///      If a cumulative or rate-limited ceiling is ever added, this test should fail — and
    ///      that failure is the signal to update §7.1 and the v1.1 register, not to delete it.
    function test_LIMIT_nativeCeilingIsPerActionAndBoundsNoAggregate() public {
        uint256 cap = 0.01 ether;
        address[] memory targets = new address[](1);
        targets[0] = address(demoPay);
        bytes4[] memory selectors = new bytes4[](1);
        selectors[0] = PURCHASE_SEL;

        SentinelVault v = new SentinelVault(owner, signerAddr, cap, targets, selectors);
        bytes32 aggregateMandateHash = _activateTestMandate(
            v, OWNER_PK, owner, signerAddr, address(demoPay), PURCHASE_SEL, cap,
            POLICY_HASH, keccak256("aggregate-mandate")
        );
        vm.deal(address(v), 100 * cap);

        // CONTROL FIRST. One action ABOVE the cap is still refused. Without it the drain below
        // could be passing because the ceiling is ABSENT rather than because it is PER-ACTION,
        // and the test would assert nothing (A-051: a check that always fires looks exactly
        // like one that catches everything).
        {
            bytes memory data = _purchaseFor(0);
            T.ActionPayload memory a = _actionOn(v, cap + 1, data);
            a.mandateHash = aggregateMandateHash;
            T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
            bytes memory sig = _signFor(v, SIGNER_PK, T.hashReceipt(r));
            vm.prank(address(0xDEAD));
            vm.expectRevert(SentinelVault.ValueOverCap.selector);
            v.executeWithReceipt(a, data, r, sig);
        }

        // Now 100 actions at EXACTLY the cap. Every one is a valid ALLOW, the ceiling engages
        // on all of them, and it refuses none.
        //
        // THE `vm.warp` IS GONE, AND ITS ABSENCE IS THE POINT (D-053(a), round six lens 4).
        // This loop used to advance the clock by 365 days between executions, so a reader took
        // away "100 actions spread over a century" and the §7.1 row's "pause bounds damage
        // AFTER SOMEBODY NOTICES" read as a real window. It is not one. Nothing here needs
        // time to pass: the block number and timestamp are asserted UNCHANGED across all 100
        // executions below, so no owner transaction — pause included — can interleave.
        //
        // Measured on this fixture: ~75,700 gas per action, so a 30M block holds roughly 396
        // of them. The drain is bounded by the block gas limit, not by anything the vault does.
        uint256 blockNumberBefore = block.number;
        uint256 timestampBefore = block.timestamp;
        for (uint256 i = 0; i < 100; i++) {
            bytes memory data = _purchaseFor(i + 1);
            T.ActionPayload memory a = _actionOn(v, cap, data);
            a.mandateHash = aggregateMandateHash;
            T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
            bytes memory sig = _signFor(v, SIGNER_PK, T.hashReceipt(r));
            vm.prank(address(0xDEAD)); // no key needed: execution is permissionless
            v.executeWithReceipt(a, data, r, sig);
        }

        assertEq(
            block.number,
            blockNumberBefore,
            "REGRESSION: the drain now crosses a block boundary, so pause could interleave"
        );
        assertEq(
            block.timestamp,
            timestampBefore,
            "REGRESSION: time passes during the drain; 7.1 after-somebody-notices would need revisiting"
        );
        assertEq(v.actionNonce(), 100, "100 nonces consumed and not one action refused");
        assertEq(
            address(v).balance,
            0,
            "REGRESSION or REPAIR: the vault now bounds CUMULATIVE native value - see A-063"
        );
    }

    function _purchaseFor(uint256 i) internal view returns (bytes memory) {
        return abi.encodeCall(DemoPay.purchase, (keccak256(abi.encode(i)), owner, 24 hours, false));
    }

    function _actionOn(SentinelVault v, uint256 valueWei, bytes memory data)
        internal
        view
        returns (T.ActionPayload memory a)
    {
        a = T.ActionPayload({
            schemaVersion: 1,
            chainId: block.chainid,
            vault: address(v),
            actionNonce: v.actionNonce(),
            target: address(demoPay),
            valueWei: valueWei,
            dataHash: keccak256(data),
            operation: uint8(T.Operation.CALL),
            mandateHash: MANDATE_HASH,
            policyHash: POLICY_HASH,
            // `type(uint64).max`, and that is the point rather than a convenience. `deadline`
            // lives in the ActionPayload the receipt commits to, so under the compromise this
            // test models it is the ATTACKER's to choose, and the vault rejects only values
            // already in the past. D-042 listed `deadline` as onchain containment; it bounds
            // a careless signer, not a compromised one.
            deadline: type(uint64).max
        });
    }

    /// @notice §3.3(2) requires override be LOGGED, and until D-043 it was not.
    ///
    /// @dev Asserts the authorization is identifiable from the log alone — the override's own
    ///      hash, the review receipt it names, the owner's reasonHash, and its expiry. Before
    ///      this, `ActionExecuted` carried only `viaOverride` and the RECEIPT's decisionId, so
    ///      an auditor could see that an override happened and never which one.
    function test_overrideAuthorizationIsLogged() public {
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.REVIEW);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        T.OverrideAuthorizationPayload memory auth = T.OverrideAuthorizationPayload({
            schemaVersion: 1,
            reviewReceiptHash: T.hashReceipt(r),
            actionHash: T.hashAction(a),
            mandateHash: a.mandateHash,
            policyHash: a.policyHash,
            actionNonce: a.actionNonce,
            reasonHash: keccak256("owner: verified with the counterparty out of band"),
            issuedAt: uint64(block.timestamp),
            expiresAt: uint64(block.timestamp + 30 minutes)
        });
        bytes memory ownerSig = _sign(OWNER_PK, T.hashOverride(auth));

        vm.expectEmit(true, true, true, true);
        emit SentinelVault.OverrideAuthorized(
            auth.actionHash,
            T.hashOverride(auth),
            auth.reviewReceiptHash,
            auth.reasonHash,
            auth.expiresAt
        );
        vault.executeWithOverride(a, data, r, sig, auth, ownerSig);

        assertEq(vault.actionNonce(), 1, "the override did not execute");
    }

    /// @notice Rotation revokes the signer-bound mandate, so reinstating an old signer does
    ///         not revive receipts issued under the prior mandate epoch.
    function test_reinstatingARotatedOutSignerDoesNotReviveOldReceipts() public {
        address signerB = vm.addr(0xB0B);
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        bytes memory sig = _sign(SIGNER_PK, T.hashReceipt(r));

        // Rotate away: the receipt correctly dies.
        vm.prank(owner);
        vault.rotateSigner(signerB);
        vm.expectRevert(SentinelVault.MandateNotActive.selector);
        vault.executeWithReceipt(a, data, r, sig);

        // Rotate back: the old mandate is still revoked and the receipt remains dead.
        vm.prank(owner);
        vault.rotateSigner(signerAddr);
        vm.expectRevert(SentinelVault.MandateNotActive.selector);
        vault.executeWithReceipt(a, data, r, sig);

        assertEq(vault.actionNonce(), 0, "a prior mandate epoch was revived by signer rotation");
    }

    /// @notice A receipt pre-minted by a standby key cannot go live through rotation because
    ///         the owner must sign and activate a new mandate naming that signer.
    function test_receiptFromAFutureSignerDoesNotGoLiveOnRotation() public {
        uint256 pkB = 0xB0B;
        address signerB = vm.addr(pkB);
        bytes memory data = _callData();
        T.ActionPayload memory a = _action(data);

        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW);
        r.signer = signerB; // named and signed by a key that is not active yet
        bytes memory sig = _sign(pkB, T.hashReceipt(r));

        vm.expectRevert(SentinelVault.WrongSigner.selector);
        vault.executeWithReceipt(a, data, r, sig);

        vm.prank(owner);
        vault.rotateSigner(signerB);
        vm.expectRevert(SentinelVault.MandateNotActive.selector);
        vault.executeWithReceipt(a, data, r, sig);

        assertEq(vault.actionNonce(), 0, "a pre-minted receipt activated without a new mandate");
    }

    /// @dev `_sign` is bound to the suite's own vault; this variant signs for another.
    function _signFor(SentinelVault v, uint256 pk, bytes32 structHash)
        internal
        view
        returns (bytes memory)
    {
        bytes32 digest = T.digest(T.domainSeparator(block.chainid, address(v)), structHash);
        (uint8 vv, bytes32 rr, bytes32 ss) = vm.sign(pk, digest);
        return abi.encodePacked(rr, ss, vv);
    }
}

/// @notice Minimal ERC20 approve/allowance surface. Deliberately not DemoERC20: this test is
///         about the VAULT's indifference to token semantics, so the token should be the
///         smallest thing that can record an allowance.
contract TokenStub {
    mapping(address => mapping(address => uint256)) public allowance;

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }
}
