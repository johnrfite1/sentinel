// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {SentinelVault} from "../src/SentinelVault.sol";
import {SentinelTypes as T} from "../src/types/SentinelTypes.sol";

/// Observes the vault's actionNonce DURING the external call. This is the direct,
/// guard-independent observation of §3.3(9)'s "consumed before the external call".
contract Observer {
    SentinelVault public immutable vault;
    uint256 public nonceDuringCall = type(uint256).max;

    constructor(SentinelVault v) { vault = v; }

    fallback() external payable { nonceDuringCall = vault.actionNonce(); }
    receive() external payable { nonceDuringCall = vault.actionNonce(); }
}

contract OrderingProbe is Test {
    SentinelVault vault;
    Observer obs;
    uint256 constant OWNER_PK = 0xA11CE;
    uint256 constant SIGNER_PK = 0x519E4;
    bytes32 constant MH = keccak256("mandate-1");
    bytes32 constant PH = keccak256("policy-1");
    bytes4 constant SEL = bytes4(keccak256("anything()"));

    function setUp() public {
        address predicted = vm.computeCreateAddress(address(this), vm.getNonce(address(this)) + 1);
        address[] memory t = new address[](1); t[0] = predicted;
        bytes4[] memory s = new bytes4[](1); s[0] = SEL;
        vault = new SentinelVault(vm.addr(OWNER_PK), vm.addr(SIGNER_PK), 1 ether, t, s);
        obs = new Observer(vault);
        require(address(obs) == predicted, "prediction failed");
        vm.deal(address(vault), 10 ether);
        vm.startPrank(vm.addr(OWNER_PK));
        vault.activateMandate(MH); vault.activatePolicy(PH);
        vm.stopPrank();
        vm.warp(1_000_000);
    }

    function test_nonceIsConsumedBeforeTheExternalCall() public {
        bytes memory data = abi.encodePacked(SEL);
        T.ActionPayload memory a = T.ActionPayload({
            schemaVersion: 1, chainId: block.chainid, vault: address(vault), actionNonce: 0,
            target: address(obs), valueWei: 0.1 ether, dataHash: keccak256(data),
            operation: 0, mandateHash: MH, policyHash: PH, deadline: uint64(block.timestamp + 1 hours)
        });
        T.DecisionReceiptPayload memory r = T.DecisionReceiptPayload({
            schemaVersion: 1, decisionId: keccak256("d"), actionHash: T.hashAction(a),
            mandateHash: MH, policyHash: PH, verdict: 2, reasonCodesHash: bytes32(0),
            evidenceHash: bytes32(0), simulationBlockNumber: block.number, simulationBlockHash: bytes32(0),
            issuedAt: uint64(block.timestamp), expiresAt: uint64(block.timestamp + 10 minutes),
            signer: vm.addr(SIGNER_PK)
        });
        bytes32 d = T.digest(T.domainSeparator(block.chainid, address(vault)), T.hashReceipt(r));
        (uint8 v, bytes32 rr, bytes32 ss) = vm.sign(SIGNER_PK, d);
        vault.executeWithReceipt(a, data, r, abi.encodePacked(rr, ss, v));

        assertEq(obs.nonceDuringCall(), 1, "the nonce was NOT consumed before the external call");
    }
}
