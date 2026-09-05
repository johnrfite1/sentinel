// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {SentinelVault} from "../src/SentinelVault.sol";
import {SentinelTypes as T} from "../src/types/SentinelTypes.sol";
import {DemoPay} from "../src/demo/DemoPay.sol";

/// @notice Publication-focused witness for the Crucible withdrawal conditions.
/// @dev Keys are derived inside each run and never embedded in or emitted by the artifact.
contract PublicationWithdrawalTest is Test {
    SentinelVault internal vault;
    DemoPay internal target;
    address internal owner;
    address internal signer;
    uint256 internal ownerPk;
    uint256 internal signerPk;
    bytes32 internal mandateHash;
    bytes32 internal constant POLICY_HASH = keccak256("publication-policy");

    function setUp() public {
        ownerPk = _ephemeralKey("owner");
        signerPk = _ephemeralKey("signer");
        owner = vm.addr(ownerPk);
        signer = vm.addr(signerPk);
        target = new DemoPay();
        address[] memory targets = new address[](1);
        targets[0] = address(target);
        bytes4[] memory selectors = new bytes4[](1);
        selectors[0] = DemoPay.purchase.selector;
        vault = new SentinelVault(owner, signer, 0.01 ether, targets, selectors);
        vm.deal(address(vault), 1 ether);
        vm.warp(1_000_000);

        (T.MandatePayload memory mandate, bytes memory signature) = _mandate(signer);
        mandateHash = T.hashMandate(mandate);
        vm.startPrank(owner);
        vault.activatePolicy(POLICY_HASH);
        vault.activateMandate(mandate, signature);
        vm.stopPrank();
    }

    function test_exactSucceedsAlteredCalldataReplayAndWrongDomainFail() public {
        bytes memory data = abi.encodeCall(
            DemoPay.purchase, (keccak256("publication-resource"), owner, 1 hours, false)
        );
        T.ActionPayload memory action = _action(data);
        (T.DecisionReceiptPayload memory receipt, bytes memory signature) = _receipt(action);

        bytes memory altered = abi.encodeCall(
            DemoPay.purchase, (keccak256("altered-resource"), owner, 1 hours, false)
        );
        vm.expectRevert(SentinelVault.CalldataMismatch.selector);
        vault.executeWithReceipt(action, altered, receipt, signature);

        vault.executeWithReceipt(action, data, receipt, signature);
        assertEq(vault.actionNonce(), 1);

        vm.expectRevert(SentinelVault.BadNonce.selector);
        vault.executeWithReceipt(action, data, receipt, signature);

        action.actionNonce = 1;
        action.chainId += 1;
        (receipt, signature) = _receipt(action);
        vm.expectRevert(SentinelVault.WrongChain.selector);
        vault.executeWithReceipt(action, data, receipt, signature);

        action.chainId = block.chainid;
        action.vault = address(0x1234);
        (receipt, signature) = _receipt(action);
        vm.expectRevert(SentinelVault.WrongVault.selector);
        vault.executeWithReceipt(action, data, receipt, signature);
    }

    function test_absentOrWrongSignerMandateAndReceiptClockFailClosed() public {
        vm.prank(owner);
        vault.revokeMandate();
        bytes memory data = abi.encodeCall(
            DemoPay.purchase, (keccak256("publication-resource"), owner, 1 hours, false)
        );
        T.ActionPayload memory action = _action(data);
        (T.DecisionReceiptPayload memory receipt, bytes memory signature) = _receipt(action);
        vm.expectRevert(SentinelVault.MandateNotActive.selector);
        vault.executeWithReceipt(action, data, receipt, signature);

        uint256 otherPk = _ephemeralKey("other-signer");
        (T.MandatePayload memory wrong, bytes memory wrongSig) = _mandate(vm.addr(otherPk));
        vm.prank(owner);
        vm.expectRevert(SentinelVault.MandateSignerMismatch.selector);
        vault.activateMandate(wrong, wrongSig);

        (T.MandatePayload memory correct, bytes memory correctSig) = _mandate(signer);
        mandateHash = T.hashMandate(correct);
        vm.prank(owner);
        vault.activateMandate(correct, correctSig);
        action.mandateHash = mandateHash;

        (receipt, signature) = _receipt(action);
        receipt.issuedAt = uint64(block.timestamp + 1);
        signature = _sign(signerPk, T.hashReceipt(receipt));
        vm.expectRevert(SentinelVault.ReceiptNotYetValid.selector);
        vault.executeWithReceipt(action, data, receipt, signature);

        (receipt, signature) = _receipt(action);
        vm.warp(receipt.expiresAt);
        vm.expectRevert(SentinelVault.ReceiptExpired.selector);
        vault.executeWithReceipt(action, data, receipt, signature);
    }

    function _mandate(address authorisedSigner)
        internal
        view
        returns (T.MandatePayload memory mandate, bytes memory signature)
    {
        mandate = T.MandatePayload({
            schemaVersion: 1,
            mandateId: keccak256(abi.encode("publication-mandate", authorisedSigner)),
            principal: owner,
            signer: authorisedSigner,
            vault: address(vault),
            chainId: block.chainid,
            target: address(target),
            targetCodeHash: address(target).codehash,
            selector: DemoPay.purchase.selector,
            maxNativeValueWei: 0.01 ether,
            purposeKind: keccak256("purchase"),
            resourceId: keccak256("publication-resource"),
            beneficiary: owner,
            durationSeconds: 1 hours,
            recurringAllowed: false,
            validAfter: uint64(block.timestamp - 1),
            validUntil: uint64(block.timestamp + 1 days),
            policyHash: POLICY_HASH
        });
        signature = _sign(ownerPk, T.hashMandate(mandate));
    }

    function _action(bytes memory data) internal view returns (T.ActionPayload memory) {
        return T.ActionPayload({
            schemaVersion: 1,
            chainId: block.chainid,
            vault: address(vault),
            actionNonce: vault.actionNonce(),
            target: address(target),
            valueWei: 0.001 ether,
            dataHash: keccak256(data),
            operation: uint8(T.Operation.CALL),
            mandateHash: mandateHash,
            policyHash: POLICY_HASH,
            deadline: uint64(block.timestamp + 1 hours)
        });
    }

    function _receipt(T.ActionPayload memory action)
        internal
        view
        returns (T.DecisionReceiptPayload memory receipt, bytes memory signature)
    {
        receipt = T.DecisionReceiptPayload({
            schemaVersion: 1,
            decisionId: keccak256(abi.encode("publication-decision", action.actionNonce)),
            actionHash: T.hashAction(action),
            mandateHash: action.mandateHash,
            policyHash: action.policyHash,
            verdict: uint8(T.Verdict.ALLOW),
            reasonCodesHash: bytes32(0),
            evidenceHash: keccak256("publication-evidence"),
            simulationBlockNumber: block.number,
            simulationBlockHash: blockhash(block.number - 1),
            issuedAt: uint64(block.timestamp),
            expiresAt: uint64(block.timestamp + 5 minutes),
            signer: signer
        });
        signature = _sign(signerPk, T.hashReceipt(receipt));
    }

    function _sign(uint256 pk, bytes32 structHash) internal view returns (bytes memory) {
        bytes32 d = T.digest(T.domainSeparator(block.chainid, address(vault)), structHash);
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(pk, d);
        return abi.encodePacked(r, s, v);
    }

    function _ephemeralKey(string memory role) internal view returns (uint256) {
        return uint256(keccak256(abi.encode(role, address(this), block.prevrandao, gasleft())));
    }
}
