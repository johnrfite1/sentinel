// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {SentinelVault} from "../src/SentinelVault.sol";
import {SentinelTypes as T} from "../src/types/SentinelTypes.sol";

/// @dev Shared test construction for the v0.3 exhibited owner-signed mandate envelope.
abstract contract MandateTestHelper is Test {
    function _mandateEnvelope(
        SentinelVault targetVault,
        uint256 ownerPk,
        address principal,
        address authorisedSigner,
        address target,
        bytes4 selector,
        uint256 maxValue,
        bytes32 policyHash,
        bytes32 mandateId
    ) internal view returns (T.MandatePayload memory mandate, bytes memory signature) {
        mandate = T.MandatePayload({
            schemaVersion: 1,
            mandateId: mandateId,
            principal: principal,
            signer: authorisedSigner,
            vault: address(targetVault),
            chainId: block.chainid,
            target: target,
            targetCodeHash: target.codehash,
            selector: selector,
            maxNativeValueWei: maxValue,
            purposeKind: keccak256("test-purpose"),
            resourceId: keccak256("test-resource"),
            beneficiary: principal,
            durationSeconds: 1 days,
            recurringAllowed: false,
            validAfter: 0,
            validUntil: type(uint64).max,
            policyHash: policyHash
        });
        bytes32 digest = T.digest(
            T.domainSeparator(block.chainid, address(targetVault)), T.hashMandate(mandate)
        );
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(ownerPk, digest);
        signature = abi.encodePacked(r, s, v);
    }

    function _activateTestMandate(
        SentinelVault targetVault,
        uint256 ownerPk,
        address principal,
        address authorisedSigner,
        address target,
        bytes4 selector,
        uint256 maxValue,
        bytes32 policyHash,
        bytes32 mandateId
    ) internal returns (bytes32 mandateHash) {
        (T.MandatePayload memory mandate, bytes memory signature) = _mandateEnvelope(
            targetVault,
            ownerPk,
            principal,
            authorisedSigner,
            target,
            selector,
            maxValue,
            policyHash,
            mandateId
        );
        vm.startPrank(principal);
        targetVault.activatePolicy(policyHash);
        targetVault.activateMandate(mandate, signature);
        vm.stopPrank();
        return T.hashMandate(mandate);
    }
}
