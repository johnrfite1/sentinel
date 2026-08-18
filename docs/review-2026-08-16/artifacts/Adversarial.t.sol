// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {SentinelVault} from "../src/SentinelVault.sol";
import {SentinelTypes as T} from "../src/types/SentinelTypes.sol";
import {DemoPay} from "../src/demo/DemoPay.sol";
import {DemoERC20} from "../src/demo/DemoERC20.sol";
import {IERC20} from "openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";

/// A target with a payable fallback that swallows anything. Stands in for any allowlisted
/// contract that does not revert on an unknown selector.
contract Sink {
    uint256 public calls;
    bytes public lastData;

    fallback() external payable {
        calls++;
        lastData = msg.data;
    }

    receive() external payable {
        calls++;
    }
}

contract AdversarialTest is Test {
    uint256 internal constant OWNER_PK = 0xA11CE;
    uint256 internal constant SIGNER_PK = 0x519E4;
    uint256 internal constant SIGNER_PK_B = 0x519E5;
    uint256 internal constant ATTACKER_PK = 0xBAD;

    address internal owner;
    address internal signerAddr;
    address internal signerB;
    address internal attacker;

    bytes32 internal constant MANDATE_HASH = keccak256("mandate-1");
    bytes32 internal constant POLICY_HASH = keccak256("policy-1");

    function setUp() public {
        owner = vm.addr(OWNER_PK);
        signerAddr = vm.addr(SIGNER_PK);
        signerB = vm.addr(SIGNER_PK_B);
        attacker = vm.addr(ATTACKER_PK);
        vm.warp(1_000_000);
    }

    function _mkVault(uint256 cap, address[] memory targets, bytes4[] memory sels)
        internal
        returns (SentinelVault v)
    {
        v = new SentinelVault(owner, signerAddr, cap, targets, sels);
        vm.startPrank(owner);
        v.activateMandate(MANDATE_HASH);
        v.activatePolicy(POLICY_HASH);
        vm.stopPrank();
    }

    function _action(SentinelVault v, address target, uint256 value, bytes memory data)
        internal
        view
        returns (T.ActionPayload memory a)
    {
        a = T.ActionPayload({
            schemaVersion: 1,
            chainId: block.chainid,
            vault: address(v),
            actionNonce: v.actionNonce(),
            target: target,
            valueWei: value,
            dataHash: keccak256(data),
            operation: uint8(T.Operation.CALL),
            mandateHash: MANDATE_HASH,
            policyHash: POLICY_HASH,
            deadline: uint64(block.timestamp + 1 hours)
        });
    }

    function _receipt(T.ActionPayload memory a, T.Verdict verdict, address namedSigner)
        internal
        view
        returns (T.DecisionReceiptPayload memory r)
    {
        r = T.DecisionReceiptPayload({
            schemaVersion: 1,
            decisionId: keccak256(abi.encode("d", a.actionNonce, a.target, a.valueWei)),
            actionHash: T.hashAction(a),
            mandateHash: a.mandateHash,
            policyHash: a.policyHash,
            verdict: uint8(verdict),
            reasonCodesHash: bytes32(0),
            evidenceHash: bytes32(0),
            simulationBlockNumber: block.number,
            simulationBlockHash: bytes32(0),
            issuedAt: uint64(block.timestamp),
            expiresAt: uint64(block.timestamp + 10 minutes),
            signer: namedSigner
        });
    }

    function _sign(SentinelVault v, uint256 pk, bytes32 structHash) internal pure returns (bytes memory) {
        bytes32 d = T.digest(T.domainSeparator(31337, address(v)), structHash);
        (uint8 vv, bytes32 r, bytes32 s) = vm.sign(pk, d);
        return abi.encodePacked(r, s, vv);
    }

    // =====================================================================
    // F-1  Unlimited ERC20 approval passes EVERY vault backstop.
    //      Config is exactly ts/test/harness.ts deployStack(): targets
    //      {DemoPay, DemoERC20}, selectors {purchase, approve}.
    // =====================================================================
    function test_ATK_unlimitedApprovalPassesEveryVaultBackstop() public {
        DemoPay pay = new DemoPay();
        DemoERC20 tok = new DemoERC20(address(this), 10 ** 24);

        address[] memory targets = new address[](2);
        targets[0] = address(pay);
        targets[1] = address(tok);
        bytes4[] memory sels = new bytes4[](2);
        sels[0] = DemoPay.purchase.selector;
        sels[1] = IERC20.approve.selector;

        SentinelVault v = _mkVault(0.01 ether, targets, sels);
        // The vault holds the tokens (this is exactly ts/src/corpus/run.ts's minting choice:
        // `deploy(ercArt, [vault, 10n ** 24n])`).
        tok.transfer(address(v), 10 ** 24);
        assertEq(tok.balanceOf(address(v)), 10 ** 24);

        // ONE action. valueWei = 0, so the native cap is not even engaged.
        bytes memory data = abi.encodeCall(IERC20.approve, (attacker, type(uint256).max));
        T.ActionPayload memory a = _action(v, address(tok), 0, data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW, signerAddr);
        bytes memory sig = _sign(v, SIGNER_PK, T.hashReceipt(r));

        vm.prank(attacker); // permissionless relay
        v.executeWithReceipt(a, data, r, sig);

        assertEq(tok.allowance(address(v), attacker), type(uint256).max, "vault approved unlimited spend");

        vm.prank(attacker);
        tok.transferFrom(address(v), attacker, 10 ** 24);
        assertEq(tok.balanceOf(attacker), 10 ** 24, "entire token balance drained");
        assertEq(tok.balanceOf(address(v)), 0);
        assertEq(v.actionNonce(), 1, "one nonce, total loss");
    }

    // =====================================================================
    // F-2  The corpus/emit-samples vault allowlists 0x...01 (ecrecover
    //      precompile) as an execution target. A call there succeeds, burns
    //      the native value, and the vault logs ActionExecuted.
    // =====================================================================
    function test_ATK_precompileTargetBurnsValueAndReportsSuccess() public {
        DemoPay pay = new DemoPay();
        address placeholder = address(0x0000000000000000000000000000000000000001);

        address[] memory targets = new address[](2);
        targets[0] = address(pay);
        targets[1] = placeholder; // <-- ts/src/corpus/run.ts:175, ts/src/tools/emit-samples.ts:123
        bytes4[] memory sels = new bytes4[](2);
        sels[0] = bytes4(0xc188528b); // purchase
        sels[1] = bytes4(0x095ea7b3); // approve

        SentinelVault v = _mkVault(0.01 ether, targets, sels);
        vm.deal(address(v), 1 ether);

        bytes memory data = abi.encodeWithSelector(bytes4(0x095ea7b3), attacker, type(uint256).max);
        T.ActionPayload memory a = _action(v, placeholder, 0.01 ether, data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW, signerAddr);
        bytes memory sig = _sign(v, SIGNER_PK, T.hashReceipt(r));

        uint256 before = address(v).balance;
        vm.prank(attacker);
        v.executeWithReceipt(a, data, r, sig);

        assertEq(before - address(v).balance, 0.01 ether, "native value left the vault");
        assertEq(placeholder.balance, 0.01 ether, "and is stranded at the precompile");
        assertEq(v.actionNonce(), 1, "vault reported a successful execution");
    }

    // =====================================================================
    // F-3  The allowlists are a CROSS PRODUCT, not a set of (target,selector)
    //      pairs. A selector allowlisted for one target is accepted for any
    //      other allowlisted target.
    // =====================================================================
    function test_ATK_selectorAllowlistIsACrossProductNotPairs() public {
        DemoPay pay = new DemoPay();
        Sink sink = new Sink();

        address[] memory targets = new address[](2);
        targets[0] = address(pay);
        targets[1] = address(sink);
        bytes4[] memory sels = new bytes4[](2);
        sels[0] = DemoPay.purchase.selector; // intended ONLY for DemoPay
        sels[1] = IERC20.approve.selector; // intended ONLY for the token

        SentinelVault v = _mkVault(0.01 ether, targets, sels);
        vm.deal(address(v), 1 ether);

        // DemoPay's selector, aimed at a completely different allowlisted contract.
        bytes memory data = abi.encodeCall(DemoPay.purchase, (keccak256("r"), attacker, 1 days, true));
        T.ActionPayload memory a = _action(v, address(sink), 0.01 ether, data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW, signerAddr);
        bytes memory sig = _sign(v, SIGNER_PK, T.hashReceipt(r));

        v.executeWithReceipt(a, data, r, sig);

        assertEq(sink.calls(), 1, "vault routed DemoPay's selector into a different target");
        assertEq(address(sink).balance, 0.01 ether);
    }

    // =====================================================================
    // F-4  A code-less target makes the selector allowlist decorative: the
    //      call always succeeds and the calldata is never executed.
    // =====================================================================
    function test_ATK_codelessTargetAlwaysSucceeds() public {
        address eoa = address(0xE0A);
        address[] memory targets = new address[](1);
        targets[0] = eoa;
        bytes4[] memory sels = new bytes4[](1);
        sels[0] = DemoPay.purchase.selector;

        SentinelVault v = _mkVault(0.01 ether, targets, sels);
        vm.deal(address(v), 1 ether);
        assertEq(eoa.code.length, 0);

        bytes memory data = abi.encodeCall(DemoPay.purchase, (keccak256("r"), attacker, 1 days, true));
        T.ActionPayload memory a = _action(v, eoa, 0.01 ether, data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW, signerAddr);
        bytes memory sig = _sign(v, SIGNER_PK, T.hashReceipt(r));

        v.executeWithReceipt(a, data, r, sig);
        assertEq(eoa.balance, 0.01 ether, "value moved; no code ran; ActionExecuted logged");
    }

    // =====================================================================
    // F-5  Signer rotation is NOT revocation. Rotating away and back revives
    //      every outstanding receipt from the old key. The contract comment
    //      claims the named-signer check prevents exactly this.
    // =====================================================================
    function test_ATK_signerReinstatementRevivesOldReceipts() public {
        DemoPay pay = new DemoPay();
        address[] memory targets = new address[](1);
        targets[0] = address(pay);
        bytes4[] memory sels = new bytes4[](1);
        sels[0] = DemoPay.purchase.selector;

        SentinelVault v = _mkVault(0.01 ether, targets, sels);
        vm.deal(address(v), 1 ether);

        bytes memory data = abi.encodeCall(DemoPay.purchase, (keccak256("r"), attacker, 1 days, true));
        T.ActionPayload memory a = _action(v, address(pay), 0.01 ether, data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW, signerAddr);
        bytes memory sig = _sign(v, SIGNER_PK, T.hashReceipt(r));

        // Owner detects a signer compromise and rotates away. Receipt is dead.
        vm.prank(owner);
        v.rotateSigner(signerB);
        vm.expectRevert(SentinelVault.WrongSigner.selector);
        v.executeWithReceipt(a, data, r, sig);

        // Later the owner rotates back to the original address (re-provisioned key,
        // rollback of a bad rotation, or an operator mistake).
        vm.prank(owner);
        v.rotateSigner(signerAddr);

        // The receipt the owner already treated as revoked executes.
        v.executeWithReceipt(a, data, r, sig);
        assertEq(v.actionNonce(), 1, "a receipt revoked by rotation executed after re-rotation");
    }

    // =====================================================================
    // F-6  A receipt pre-signed by a key that is NOT yet the signer becomes
    //      live the moment the owner rotates to it. Nothing binds a receipt
    //      to the epoch in which its signer was active.
    // =====================================================================
    function test_ATK_preSignedReceiptFromFutureSignerGoesLiveOnRotation() public {
        DemoPay pay = new DemoPay();
        address[] memory targets = new address[](1);
        targets[0] = address(pay);
        bytes4[] memory sels = new bytes4[](1);
        sels[0] = DemoPay.purchase.selector;

        SentinelVault v = _mkVault(0.01 ether, targets, sels);
        vm.deal(address(v), 1 ether);

        bytes memory data = abi.encodeCall(DemoPay.purchase, (keccak256("r"), attacker, 1 days, true));
        T.ActionPayload memory a = _action(v, address(pay), 0.01 ether, data);
        // Minted by key B while A is still the active signer.
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW, signerB);
        bytes memory sig = _sign(v, SIGNER_PK_B, T.hashReceipt(r));

        vm.expectRevert(SentinelVault.WrongSigner.selector);
        v.executeWithReceipt(a, data, r, sig);

        vm.prank(owner);
        v.rotateSigner(signerB);

        v.executeWithReceipt(a, data, r, sig);
        assertEq(v.actionNonce(), 1, "a pre-rotation receipt executed after rotation");
    }

    // =====================================================================
    // F-7  Pause is not revocation. Un-pausing revives every outstanding
    //      receipt whose window is still open.
    // =====================================================================
    function test_ATK_unpauseRevivesOutstandingReceipts() public {
        DemoPay pay = new DemoPay();
        address[] memory targets = new address[](1);
        targets[0] = address(pay);
        bytes4[] memory sels = new bytes4[](1);
        sels[0] = DemoPay.purchase.selector;

        SentinelVault v = _mkVault(0.01 ether, targets, sels);
        vm.deal(address(v), 1 ether);

        bytes memory data = abi.encodeCall(DemoPay.purchase, (keccak256("r"), attacker, 1 days, true));
        T.ActionPayload memory a = _action(v, address(pay), 0.01 ether, data);
        T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW, signerAddr);
        bytes memory sig = _sign(v, SIGNER_PK, T.hashReceipt(r));

        vm.prank(owner);
        v.setPaused(true);
        vm.expectRevert(SentinelVault.Paused.selector);
        v.executeWithReceipt(a, data, r, sig);

        vm.prank(owner);
        v.setPaused(false);
        v.executeWithReceipt(a, data, r, sig);
        assertEq(v.actionNonce(), 1, "the receipt survived the pause");
    }

    // =====================================================================
    // F-8  The native cap is PER ACTION with no cumulative or rate limit.
    //      N capped actions drain the vault completely.
    // =====================================================================
    function test_ATK_perActionCapHasNoCumulativeLimit() public {
        DemoPay pay = new DemoPay();
        address[] memory targets = new address[](1);
        targets[0] = address(pay);
        bytes4[] memory sels = new bytes4[](1);
        sels[0] = DemoPay.purchase.selector;

        SentinelVault v = _mkVault(0.01 ether, targets, sels);
        vm.deal(address(v), 1 ether);

        for (uint256 i = 0; i < 100; i++) {
            bytes memory data =
                abi.encodeCall(DemoPay.purchase, (keccak256(abi.encode(i)), attacker, 1 days, true));
            T.ActionPayload memory a = _action(v, address(pay), 0.01 ether, data);
            T.DecisionReceiptPayload memory r = _receipt(a, T.Verdict.ALLOW, signerAddr);
            bytes memory sig = _sign(v, SIGNER_PK, T.hashReceipt(r));
            v.executeWithReceipt(a, data, r, sig);
        }
        assertEq(address(v).balance, 0, "entire native balance drained through the hard cap");
        assertEq(v.actionNonce(), 100);
    }
}
