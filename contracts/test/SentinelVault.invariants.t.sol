// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {SentinelVault} from "../src/SentinelVault.sol";
import {SentinelTypes as T} from "../src/types/SentinelTypes.sol";
import {DemoPay} from "../src/demo/DemoPay.sol";

/// @notice A target that calls straight back into the vault with a *second, independently
///         valid* receipt for the next nonce.
/// @dev This is the attack the nonce alone does not stop, and the reason the reentrancy
///      guard exists. By the time the external call is made the nonce has already been
///      bumped to N+1 — so a reentrant receipt minted for N+1 passes the nonce check.
///      Without the guard this drains twice in one transaction while every individual
///      credential check passes.
contract Reenterer {
    SentinelVault public immutable vault;
    bytes public payload;
    bool public armed;

    constructor(SentinelVault _vault) {
        vault = _vault;
    }

    function arm(bytes memory _payload) external {
        payload = _payload;
        armed = true;
    }

    // solhint-disable-next-line no-complex-fallback
    fallback() external payable {
        if (!armed) return;
        armed = false;
        (bool ok,) = address(vault).call(payload);
        // Swallowed deliberately: we want the outer call to survive so the test can assert
        // on final vault state rather than on a bubbled revert.
        ok;
    }

    receive() external payable {}
}

contract SentinelVaultReentrancyTest is Test {
    SentinelVault internal vault;
    Reenterer internal reenterer;

    uint256 internal constant OWNER_PK = 0xA11CE;
    uint256 internal constant SIGNER_PK = 0x519E4;
    address internal owner;
    address internal signerAddr;

    bytes32 internal constant MANDATE_HASH = keccak256("mandate-1");
    bytes32 internal constant POLICY_HASH = keccak256("policy-1");
    bytes4 internal constant SEL = bytes4(keccak256("anything()"));

    function setUp() public {
        owner = vm.addr(OWNER_PK);
        signerAddr = vm.addr(SIGNER_PK);

        // The reenterer needs the vault address, and the vault needs the reenterer
        // allowlisted. Predict the reenterer's address so both can be satisfied.
        address predicted = vm.computeCreateAddress(address(this), vm.getNonce(address(this)) + 1);
        address[] memory targets = new address[](1);
        targets[0] = predicted;
        bytes4[] memory selectors = new bytes4[](1);
        selectors[0] = SEL;

        vault = new SentinelVault(owner, signerAddr, 1 ether, targets, selectors);
        reenterer = new Reenterer(vault);
        assertEq(address(reenterer), predicted, "address prediction failed; test is not exercising reentrancy");

        vm.deal(address(vault), 10 ether);
        vm.startPrank(owner);
        vault.activateMandate(MANDATE_HASH);
        vault.activatePolicy(POLICY_HASH);
        vm.stopPrank();
        vm.warp(1_000_000);
    }

    function _bundle(uint256 nonce, bytes memory data)
        internal
        view
        returns (T.ActionPayload memory a, T.DecisionReceiptPayload memory r, bytes memory sig)
    {
        a = T.ActionPayload({
            schemaVersion: 1,
            chainId: block.chainid,
            vault: address(vault),
            actionNonce: nonce,
            target: address(reenterer),
            valueWei: 0.1 ether,
            dataHash: keccak256(data),
            operation: uint8(T.Operation.CALL),
            mandateHash: MANDATE_HASH,
            policyHash: POLICY_HASH,
            deadline: uint64(block.timestamp + 1 hours)
        });
        r = T.DecisionReceiptPayload({
            schemaVersion: 1,
            decisionId: keccak256(abi.encode("decision", nonce)),
            actionHash: T.hashAction(a),
            mandateHash: MANDATE_HASH,
            policyHash: POLICY_HASH,
            verdict: uint8(T.Verdict.ALLOW),
            reasonCodesHash: bytes32(0),
            evidenceHash: bytes32(0),
            simulationBlockNumber: block.number,
            simulationBlockHash: bytes32(0),
            issuedAt: uint64(block.timestamp),
            expiresAt: uint64(block.timestamp + 10 minutes),
            signer: signerAddr
        });
        bytes32 digest = T.digest(T.domainSeparator(block.chainid, address(vault)), T.hashReceipt(r));
        (uint8 v, bytes32 rr, bytes32 ss) = vm.sign(SIGNER_PK, digest);
        sig = abi.encodePacked(rr, ss, v);
    }

    function test_reentrantSecondReceiptCannotExecuteInTheSameTransaction() public {
        bytes memory data = abi.encodePacked(SEL);

        (T.ActionPayload memory a0, T.DecisionReceiptPayload memory r0, bytes memory s0) = _bundle(0, data);
        (T.ActionPayload memory a1, T.DecisionReceiptPayload memory r1, bytes memory s1) = _bundle(1, data);

        // Arm the target to re-enter with the *next* nonce's fully valid credential.
        reenterer.arm(abi.encodeCall(SentinelVault.executeWithReceipt, (a1, data, r1, s1)));

        uint256 balanceBefore = address(vault).balance;
        vault.executeWithReceipt(a0, data, r0, s0);

        assertEq(vault.actionNonce(), 1, "exactly one nonce may be consumed per transaction");
        assertEq(
            balanceBefore - address(vault).balance, 0.1 ether, "exactly one transfer may leave the vault"
        );
    }

    // -----------------------------------------------------------------
    // The override path, and the door between the two paths
    // -----------------------------------------------------------------
    //
    // FOUND BY AN INDEPENDENT REVIEW, 2026-08-15, and it is the second time the SAME
    // blind spot has produced a finding. `nonReentrant` can be deleted from
    // `executeWithOverride` and all 60 tests still pass, because the only reentrancy
    // test drove `executeWithReceipt` and the only allowlisted target the invariant
    // campaign has is DemoPay — which makes no outbound call, so the campaign
    // STRUCTURALLY cannot generate a callback at any depth or profile. Adding four
    // override actions to the handler did not fix that and was never going to.
    //
    // The reviewer demonstrated a double-spend on two shapes. Both are tested below.
    // The second is the one worth staring at: `_entered` is shared, so the door is not
    // "the override path re-entering itself" but ANY execution path re-entering ANY
    // other. A per-path guard would have looked equally correct and been wrong.

    function _reviewBundle(uint256 nonce, bytes memory data)
        internal
        view
        returns (
            T.ActionPayload memory a,
            T.DecisionReceiptPayload memory r,
            bytes memory sig,
            T.OverrideAuthorizationPayload memory auth,
            bytes memory ownerSig
        )
    {
        (a, r, sig) = _bundle(nonce, data);
        r.verdict = uint8(T.Verdict.REVIEW);
        bytes32 digest = T.digest(T.domainSeparator(block.chainid, address(vault)), T.hashReceipt(r));
        (uint8 v, bytes32 rr, bytes32 ss) = vm.sign(SIGNER_PK, digest);
        sig = abi.encodePacked(rr, ss, v);

        auth = T.OverrideAuthorizationPayload({
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
        bytes32 od = T.digest(T.domainSeparator(block.chainid, address(vault)), T.hashOverride(auth));
        (uint8 ov, bytes32 orr, bytes32 oss) = vm.sign(OWNER_PK, od);
        ownerSig = abi.encodePacked(orr, oss, ov);
    }

    function test_reentrantOverrideCannotExecuteInTheSameTransaction() public {
        bytes memory data = abi.encodePacked(SEL);
        (
            T.ActionPayload memory a0,
            T.DecisionReceiptPayload memory r0,
            bytes memory s0,
            T.OverrideAuthorizationPayload memory auth0,
            bytes memory o0
        ) = _reviewBundle(0, data);
        (
            T.ActionPayload memory a1,
            T.DecisionReceiptPayload memory r1,
            bytes memory s1,
            T.OverrideAuthorizationPayload memory auth1,
            bytes memory o1
        ) = _reviewBundle(1, data);

        reenterer.arm(
            abi.encodeCall(SentinelVault.executeWithOverride, (a1, data, r1, s1, auth1, o1))
        );

        uint256 balanceBefore = address(vault).balance;
        vault.executeWithOverride(a0, data, r0, s0, auth0, o0);

        assertEq(vault.actionNonce(), 1, "exactly one nonce may be consumed per transaction");
        assertEq(balanceBefore - address(vault).balance, 0.1 ether, "exactly one transfer may leave");
    }

    /// @notice The cross-path door: an ALLOW receipt executing, and the target re-entering
    ///         through the OVERRIDE path with an independently valid credential.
    function test_anAllowExecutionCannotBeReenteredThroughTheOverridePath() public {
        bytes memory data = abi.encodePacked(SEL);
        (T.ActionPayload memory a0, T.DecisionReceiptPayload memory r0, bytes memory s0) = _bundle(0, data);
        (
            T.ActionPayload memory a1,
            T.DecisionReceiptPayload memory r1,
            bytes memory s1,
            T.OverrideAuthorizationPayload memory auth1,
            bytes memory o1
        ) = _reviewBundle(1, data);

        reenterer.arm(
            abi.encodeCall(SentinelVault.executeWithOverride, (a1, data, r1, s1, auth1, o1))
        );

        uint256 balanceBefore = address(vault).balance;
        vault.executeWithReceipt(a0, data, r0, s0);

        assertEq(vault.actionNonce(), 1, "the override path re-entered an allow execution");
        assertEq(balanceBefore - address(vault).balance, 0.1 ether, "two transfers left the vault");
    }
}

/// @notice Handler for the stateful invariant campaign.
///
/// @dev DESIGN NOTE — why validity is the default path.
///
///      The first version of this handler randomized every dimension at once (verdict,
///      nonce, calldata, pause, signer) inside a single `tryExecute`. Valid bundles were
///      then a coincidence requiring five independent dice to land together, and across
///      a 64-call run they essentially never did: the campaign made 16,384 calls and
///      executed ZERO actions, while every invariant reported PASS. The `afterInvariant`
///      non-vacuity guard is what surfaced that.
///
///      The fix is to give the fuzzer a `executeValid` action that always builds a
///      correct bundle, and to put each adversarial case in its own action. The fuzzer
///      then explores orderings and interleavings — which is what stateful invariant
///      testing is actually for — instead of spending its budget rediscovering how to
///      construct a valid signature.
///
///      Signer rotation cycles between two keys the handler holds, so rotation stays
///      exercised without starving the campaign of signable receipts.
contract VaultHandler is Test {
    SentinelVault public immutable vault;
    DemoPay public immutable demoPay;
    uint256 internal immutable signerPkA;
    uint256 internal immutable signerPkB;
    uint256 internal currentSignerPk;
    address public immutable owner;
    /// @dev Needed because the override path requires an OWNER signature, not an owner
    ///      `prank`. §3.3(7)'s "separately authenticated" is a signature over a typed
    ///      payload; a handler that could only prank would be unable to reach the path at all.
    uint256 internal immutable ownerPk;

    bytes32 public constant MANDATE_HASH = keccak256("mandate-1");
    bytes32 public constant POLICY_HASH = keccak256("policy-1");

    // --- Ghost state ---
    uint256 public successfulExecutions;
    uint256 public rejectedAttempts;
    bool public everExecutedWhilePaused;
    bool public everExecutedNonAllowVerdict;
    bool public everExecutedTampered;
    mapping(bytes32 => uint256) public executionsPerActionHash;
    bytes32[] public executedActionHashes;

    // --- Ghost state for the override path (§3.3(7)) ---
    //
    // SEPARATE GHOSTS ON PURPOSE. A REVIEW verdict executing through an owner override is
    // CORRECT, so folding override executions into `everExecutedNonAllowVerdict` would make
    // the automatic-path invariant fire on legitimate behaviour — and the temptation would
    // then be to loosen that invariant, which is the wrong repair. Each path gets its own
    // ghost and its own invariant.
    uint256 public overrideExecutions;
    bool public everExecutedNonReviewViaOverride;
    bool public everExecutedForgedOverride;
    bool public everExecutedMismatchedOverride;

    // --- Ghost state added 2026-08-16 (D-042), after an adversarial review MEASURED that this
    //     campaign had zero marginal killing power ---
    //
    // 31 mutations of the vault's own checks: 31/31 caught by the deterministic suite, and
    // 31/31 STILL caught with this entire campaign disabled. Five survived all invariants,
    // and two of those were invisible for the same reason — the handler could not construct
    // the input that would expose them:
    //
    //   * `actionNonce != current` weakened to `< current`, i.e. the vault honours receipts
    //     for arbitrary FUTURE nonces. Every action here submitted either the current nonce
    //     (executeValid, executeNonAllow, the override arms) or a stale one (executeReplay
    //     bounds to [0, current-1]). Nothing ever offered a future nonce, so the hole could
    //     not be seen — and `invariant_nonceEqualsSuccessfulExecutions` still held, because a
    //     mutated vault still advances the nonce by exactly one per execution.
    //   * a failed external call reported as success. DemoPay could not fail in this campaign:
    //     `_data` bounds duration to [1, 30 days], derives a non-zero beneficiary, and
    //     `_bundle` bounds value to [1, 0.01 ether] — so all three of DemoPay's revert
    //     conditions were unreachable by construction.
    //
    // THE LESSON, WHICH GENERALISES BEYOND THESE TWO: a stateful campaign's coverage is
    // bounded by what its handler can BUILD, not by how many calls it makes. 262,144 calls
    // that never construct a future nonce prove nothing about future nonces.
    bool public everExecutedFutureNonce;
    bool public everExecutedKnownFailingCall;
    uint256 public futureNonceAttempts;
    uint256 public failingCallAttempts;

    constructor(
        SentinelVault _vault,
        DemoPay _demoPay,
        uint256 _signerPkA,
        uint256 _signerPkB,
        address _owner,
        uint256 _ownerPk
    ) {
        vault = _vault;
        demoPay = _demoPay;
        signerPkA = _signerPkA;
        signerPkB = _signerPkB;
        currentSignerPk = _signerPkA;
        owner = _owner;
        ownerPk = _ownerPk;
    }

    function executedCount() external view returns (uint256) {
        return executedActionHashes.length;
    }

    function _data(uint256 seed) internal pure returns (bytes memory) {
        return abi.encodeCall(
            DemoPay.purchase,
            (
                keccak256(abi.encode(seed)),
                address(uint160(uint256(keccak256(abi.encode(seed, "b"))))),
                uint64(bound(seed, 1, 30 days)),
                seed % 2 == 0
            )
        );
    }

    function _bundle(uint256 seed, uint256 nonce, T.Verdict verdict, bytes memory data)
        internal
        view
        returns (T.ActionPayload memory a, T.DecisionReceiptPayload memory r, bytes memory sig)
    {
        a = T.ActionPayload({
            schemaVersion: 1,
            chainId: block.chainid,
            vault: address(vault),
            actionNonce: nonce,
            target: address(demoPay),
            valueWei: bound(seed, 1, 0.01 ether),
            dataHash: keccak256(data),
            operation: uint8(T.Operation.CALL),
            mandateHash: MANDATE_HASH,
            policyHash: POLICY_HASH,
            deadline: uint64(block.timestamp + 1 hours)
        });
        r = T.DecisionReceiptPayload({
            schemaVersion: 1,
            decisionId: keccak256(abi.encode(seed, "d")),
            actionHash: T.hashAction(a),
            mandateHash: MANDATE_HASH,
            policyHash: POLICY_HASH,
            verdict: uint8(verdict),
            reasonCodesHash: bytes32(0),
            evidenceHash: bytes32(0),
            simulationBlockNumber: block.number,
            simulationBlockHash: bytes32(0),
            issuedAt: uint64(block.timestamp),
            expiresAt: uint64(block.timestamp + 30 minutes),
            signer: vault.signer()
        });
        bytes32 digest = T.digest(T.domainSeparator(block.chainid, address(vault)), T.hashReceipt(r));
        (uint8 v, bytes32 rr, bytes32 ss) = vm.sign(currentSignerPk, digest);
        sig = abi.encodePacked(rr, ss, v);
    }

    function _record(bytes32 actionHash, bool wasPaused, T.Verdict verdict, bool tampered) internal {
        successfulExecutions++;
        executionsPerActionHash[actionHash]++;
        executedActionHashes.push(actionHash);
        if (wasPaused) everExecutedWhilePaused = true;
        if (verdict != T.Verdict.ALLOW) everExecutedNonAllowVerdict = true;
        if (tampered) everExecutedTampered = true;
    }

    /// @notice The productive path: a correct ALLOW bundle at the current nonce.
    function executeValid(uint256 seed) external {
        bytes memory data = _data(seed);
        (T.ActionPayload memory a, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _bundle(seed, vault.actionNonce(), T.Verdict.ALLOW, data);
        bool wasPaused = vault.paused();
        try vault.executeWithReceipt(a, data, r, sig) {
            _record(T.hashAction(a), wasPaused, T.Verdict.ALLOW, false);
        } catch {
            rejectedAttempts++;
        }
    }

    /// @notice FUTURE nonce: a correctly signed bundle pinned to a nonce the vault has not
    ///         reached yet. §3.3(9) makes the nonce a single monotonically increasing counter,
    ///         so "not yet" must be refused exactly as firmly as "already used" — a vault that
    ///         accepts N+k lets a signer pre-authorise actions out of order and lets a holder
    ///         choose when they land. `executeReplay` covers the stale direction; this covers
    ///         the other one, and until D-042 nothing did.
    function executeFutureNonce(uint256 seed) external {
        uint256 future = vault.actionNonce() + bound(seed, 1, 1000);
        bytes memory data = _data(seed);
        (T.ActionPayload memory a, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _bundle(seed, future, T.Verdict.ALLOW, data);
        futureNonceAttempts++;
        bool wasPaused = vault.paused();
        try vault.executeWithReceipt(a, data, r, sig) {
            everExecutedFutureNonce = true;
            _record(T.hashAction(a), wasPaused, T.Verdict.ALLOW, false);
        } catch {
            rejectedAttempts++;
        }
    }

    /// @notice A call the TARGET will reject. Everything the vault checks is valid — signature,
    ///         nonce, binding, caps — and DemoPay reverts on `durationSeconds == 0`. §5.7 and
    ///         D-021 treat a revert as a determinate observed failure, so the vault must not
    ///         report it as a successful execution. Nothing in this campaign could previously
    ///         build a call that fails at the callee.
    function executeFailingCall(uint256 seed) external {
        bytes memory data = abi.encodeCall(
            DemoPay.purchase,
            (
                keccak256(abi.encode(seed, "fail")),
                address(uint160(uint256(keccak256(abi.encode(seed, "fb"))))),
                uint64(0), // DemoPay.ZeroDuration
                false
            )
        );
        (T.ActionPayload memory a, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _bundle(seed, vault.actionNonce(), T.Verdict.ALLOW, data);
        failingCallAttempts++;
        bool wasPaused = vault.paused();
        try vault.executeWithReceipt(a, data, r, sig) {
            everExecutedKnownFailingCall = true;
            _record(T.hashAction(a), wasPaused, T.Verdict.ALLOW, false);
        } catch {
            rejectedAttempts++;
        }
    }

    /// @notice Replay: re-submit a bundle pinned to an already-consumed nonce.
    function executeReplay(uint256 seed) external {
        uint256 current = vault.actionNonce();
        if (current == 0) return;
        bytes memory data = _data(seed);
        (T.ActionPayload memory a, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _bundle(seed, bound(seed, 0, current - 1), T.Verdict.ALLOW, data);
        bool wasPaused = vault.paused();
        try vault.executeWithReceipt(a, data, r, sig) {
            _record(T.hashAction(a), wasPaused, T.Verdict.ALLOW, true);
        } catch {
            rejectedAttempts++;
        }
    }

    /// @notice A signed BLOCK or REVIEW receipt on the automatic path. Must never execute.
    function executeNonAllow(uint256 seed, bool review) external {
        bytes memory data = _data(seed);
        T.Verdict verdict = review ? T.Verdict.REVIEW : T.Verdict.BLOCK;
        (T.ActionPayload memory a, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _bundle(seed, vault.actionNonce(), verdict, data);
        bool wasPaused = vault.paused();
        try vault.executeWithReceipt(a, data, r, sig) {
            _record(T.hashAction(a), wasPaused, verdict, false);
        } catch {
            rejectedAttempts++;
        }
    }

    /// @notice Calldata swapped after the receipt was signed (§7.1 altered-calldata case).
    function executeTamperedCalldata(uint256 seed) external {
        bytes memory data = _data(seed);
        (T.ActionPayload memory a, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _bundle(seed, vault.actionNonce(), T.Verdict.ALLOW, data);
        bytes memory swapped = _data(seed + 1);
        bool wasPaused = vault.paused();
        try vault.executeWithReceipt(a, swapped, r, sig) {
            _record(T.hashAction(a), wasPaused, T.Verdict.ALLOW, true);
        } catch {
            rejectedAttempts++;
        }
    }

    /// @notice A receipt signed by a key that is not the active signer.
    function executeForgedSignature(uint256 seed) external {
        bytes memory data = _data(seed);
        (T.ActionPayload memory a, T.DecisionReceiptPayload memory r,) =
            _bundle(seed, vault.actionNonce(), T.Verdict.ALLOW, data);
        bytes32 digest = T.digest(T.domainSeparator(block.chainid, address(vault)), T.hashReceipt(r));
        (uint8 v, bytes32 rr, bytes32 ss) = vm.sign(uint256(keccak256(abi.encode(seed, "forge"))), digest);
        bool wasPaused = vault.paused();
        try vault.executeWithReceipt(a, data, r, abi.encodePacked(rr, ss, v)) {
            _record(T.hashAction(a), wasPaused, T.Verdict.ALLOW, true);
        } catch {
            rejectedAttempts++;
        }
    }

    // -----------------------------------------------------------------
    // The override path (§3.3(7)) — absent from this campaign until A-028
    // -----------------------------------------------------------------
    //
    // A-028: "`executeWithOverride` is absent from the invariant campaign's handler set
    // although §3.3 names its property." The whole second execution path — the one that can
    // move funds on a REVIEW verdict — was exercised only by deterministic tests, so nothing
    // explored it interleaved with pauses, rotations, replays and time warps. It also meant
    // the nonce invariant had never seen a nonce consumed by an override.

    function _overrideFor(T.ActionPayload memory a, T.DecisionReceiptPayload memory r, uint256 seed)
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
            reasonHash: keccak256(abi.encode(seed, "reason")),
            issuedAt: uint64(block.timestamp),
            expiresAt: uint64(block.timestamp + 30 minutes)
        });
    }

    function _signOverride(uint256 pk, T.OverrideAuthorizationPayload memory auth)
        internal
        view
        returns (bytes memory)
    {
        bytes32 digest = T.digest(T.domainSeparator(block.chainid, address(vault)), T.hashOverride(auth));
        (uint8 v, bytes32 rr, bytes32 ss) = vm.sign(pk, digest);
        return abi.encodePacked(rr, ss, v);
    }

    /// @notice The productive override path: a REVIEW receipt plus the owner's signature.
    function executeValidOverride(uint256 seed) external {
        bytes memory data = _data(seed);
        (T.ActionPayload memory a, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _bundle(seed, vault.actionNonce(), T.Verdict.REVIEW, data);
        T.OverrideAuthorizationPayload memory auth = _overrideFor(a, r, seed);
        bool wasPaused = vault.paused();
        try vault.executeWithOverride(a, data, r, sig, auth, _signOverride(ownerPk, auth)) {
            overrideExecutions++;
            _record(T.hashAction(a), wasPaused, T.Verdict.ALLOW, false);
        } catch {
            rejectedAttempts++;
        }
    }

    /// @notice An ALLOW or BLOCK receipt pushed through the override path. §3.3(7) makes a
    ///         block unoverridable, and an allow has no business here either.
    function executeOverrideOnNonReview(uint256 seed, bool allowVerdict) external {
        bytes memory data = _data(seed);
        T.Verdict verdict = allowVerdict ? T.Verdict.ALLOW : T.Verdict.BLOCK;
        (T.ActionPayload memory a, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _bundle(seed, vault.actionNonce(), verdict, data);
        T.OverrideAuthorizationPayload memory auth = _overrideFor(a, r, seed);
        bool wasPaused = vault.paused();
        try vault.executeWithOverride(a, data, r, sig, auth, _signOverride(ownerPk, auth)) {
            everExecutedNonReviewViaOverride = true;
            overrideExecutions++;
            _record(T.hashAction(a), wasPaused, verdict, true);
        } catch {
            rejectedAttempts++;
        }
    }

    /// @notice The override signed by the EVALUATOR's key rather than the owner's. A
    ///         compromised signer must not be able to manufacture both halves of §3.3(7).
    function executeOverrideWithForgedOwnerSig(uint256 seed) external {
        bytes memory data = _data(seed);
        (T.ActionPayload memory a, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _bundle(seed, vault.actionNonce(), T.Verdict.REVIEW, data);
        T.OverrideAuthorizationPayload memory auth = _overrideFor(a, r, seed);
        bool wasPaused = vault.paused();
        try vault.executeWithOverride(a, data, r, sig, auth, _signOverride(currentSignerPk, auth)) {
            everExecutedForgedOverride = true;
            overrideExecutions++;
            _record(T.hashAction(a), wasPaused, T.Verdict.REVIEW, true);
        } catch {
            rejectedAttempts++;
        }
    }

    /// @notice A validly owner-signed override that names a DIFFERENT action. This is the
    ///         one that matters most: the owner really did consent to something, just not
    ///         to this.
    function executeOverrideForAnotherAction(uint256 seed) external {
        bytes memory data = _data(seed);
        (T.ActionPayload memory a, T.DecisionReceiptPayload memory r, bytes memory sig) =
            _bundle(seed, vault.actionNonce(), T.Verdict.REVIEW, data);
        T.OverrideAuthorizationPayload memory auth = _overrideFor(a, r, seed);
        auth.actionHash = keccak256(abi.encode(seed, "a different action entirely"));
        bool wasPaused = vault.paused();
        try vault.executeWithOverride(a, data, r, sig, auth, _signOverride(ownerPk, auth)) {
            everExecutedMismatchedOverride = true;
            overrideExecutions++;
            _record(T.hashAction(a), wasPaused, T.Verdict.REVIEW, true);
        } catch {
            rejectedAttempts++;
        }
    }

    function togglePause(bool value) external {
        vm.prank(owner);
        vault.setPaused(value);
    }

    /// @dev Rotates between two keys the handler holds, so rotation is exercised without
    ///      leaving the campaign unable to sign anything.
    function rotateSigner(bool toB) external {
        uint256 next = toB ? signerPkB : signerPkA;
        vm.prank(owner);
        vault.rotateSigner(vm.addr(next));
        currentSignerPk = next;
    }

    function warp(uint256 seconds_) external {
        vm.warp(block.timestamp + bound(seconds_, 1, 5 minutes));
    }
}

/// @title SentinelVault stateful invariants
/// @notice The §7.5 gate: "Foundry fuzz and invariant tests cannot bypass SentinelVault."
contract SentinelVaultInvariantTest is Test {
    SentinelVault internal vault;
    DemoPay internal demoPay;
    VaultHandler internal handler;

    uint256 internal constant OWNER_PK = 0xA11CE;
    uint256 internal constant SIGNER_PK = 0x519E4;
    uint256 internal constant SIGNER_PK_B = 0x519E5;

    function setUp() public {
        address owner = vm.addr(OWNER_PK);
        demoPay = new DemoPay();

        address[] memory targets = new address[](1);
        targets[0] = address(demoPay);
        bytes4[] memory selectors = new bytes4[](1);
        selectors[0] = DemoPay.purchase.selector;

        vault = new SentinelVault(owner, vm.addr(SIGNER_PK), 0.01 ether, targets, selectors);
        vm.deal(address(vault), 100 ether);

        vm.startPrank(owner);
        vault.activateMandate(handlerMandate());
        vault.activatePolicy(handlerPolicy());
        vm.stopPrank();
        vm.warp(1_000_000);

        handler = new VaultHandler(vault, demoPay, SIGNER_PK, SIGNER_PK_B, owner, OWNER_PK);
        targetContract(address(handler));
        // Explicit selector list. Without it the runner also fuzzes inherited
        // forge-std helpers on the handler, which crowd out the actions we care about.
        // REGISTERING A HANDLER ACTION IS A SEPARATE STEP FROM WRITING ONE, and forgetting it
        // is silent. D-042's two arms were written, their non-vacuity test passed (it calls
        // them directly), the whole suite went green — and the future-nonce mutation still
        // survived, because the fuzzer was never told these selectors existed. The new
        // invariants were pointing at nothing. Caught only by re-running the mutation rather
        // than trusting the green suite. If you add an action below, add its selector here and
        // then re-run the mutation it was written for.
        bytes4[] memory sel = new bytes4[](14);
        sel[0] = VaultHandler.executeValid.selector;
        sel[1] = VaultHandler.executeReplay.selector;
        sel[2] = VaultHandler.executeNonAllow.selector;
        sel[3] = VaultHandler.executeTamperedCalldata.selector;
        sel[4] = VaultHandler.executeForgedSignature.selector;
        sel[5] = VaultHandler.togglePause.selector;
        sel[6] = VaultHandler.rotateSigner.selector;
        sel[7] = VaultHandler.warp.selector;
        // The override path, added after A-028 found the entire second execution path
        // missing from this campaign.
        sel[8] = VaultHandler.executeValidOverride.selector;
        sel[9] = VaultHandler.executeOverrideOnNonReview.selector;
        sel[10] = VaultHandler.executeOverrideWithForgedOwnerSig.selector;
        sel[11] = VaultHandler.executeOverrideForAnotherAction.selector;
        // D-042, after a review measured this campaign killing nothing the deterministic tests
        // did not. These two are the inputs it could not previously construct.
        sel[12] = VaultHandler.executeFutureNonce.selector;
        sel[13] = VaultHandler.executeFailingCall.selector;
        targetSelector(FuzzSelector({addr: address(handler), selectors: sel}));
    }

    function handlerMandate() internal pure returns (bytes32) {
        return keccak256("mandate-1");
    }

    function handlerPolicy() internal pure returns (bytes32) {
        return keccak256("policy-1");
    }

    /// @notice NON-VACUITY GUARDS.
    ///
    /// @dev These are ordinary tests, deliberately NOT invariants or an `afterInvariant`
    ///      hook. That distinction cost a debugging cycle and is worth stating:
    ///
    ///      Non-vacuity is a property of the *campaign*, not of any reachable state. An
    ///      `afterInvariant` assertion on "at least one action executed" looks right and
    ///      cannot work, because Foundry shrinks a failing sequence to its minimum — and
    ///      any one-call sequence trivially has zero executions, so the guard fails
    ///      forever once shrinking engages, regardless of the vault.
    ///
    ///      The risk it was guarding against is real and was caught here: an earlier
    ///      handler produced 16,384 calls and zero executions while every invariant below
    ///      reported PASS. So the guard stays — as deterministic tests that prove the
    ///      handler's valid path really executes and its adversarial paths really get
    ///      rejected. If either breaks, these go red and the invariants stop being
    ///      evidence for nothing.

    function test_nonVacuity_validPathActuallyExecutes() public {
        handler.executeValid(1);
        handler.executeValid(2);
        handler.executeValid(3);
        assertEq(handler.successfulExecutions(), 3, "handler's valid path cannot execute");
        assertEq(vault.actionNonce(), 3, "nonce did not advance with executions");
        assertEq(handler.rejectedAttempts(), 0);
    }

    function test_nonVacuity_adversarialPathsAreReachedAndRejected() public {
        handler.executeValid(1); // gives executeReplay a consumed nonce to aim at

        uint256 before = handler.successfulExecutions();
        handler.executeReplay(1);
        handler.executeNonAllow(2, false);
        handler.executeNonAllow(3, true);
        handler.executeTamperedCalldata(4);
        handler.executeForgedSignature(5);

        assertEq(handler.successfulExecutions(), before, "an adversarial path executed");
        assertEq(handler.rejectedAttempts(), 5, "an adversarial path was not actually attempted");
        assertFalse(handler.everExecutedTampered());
        assertFalse(handler.everExecutedNonAllowVerdict());
    }

    /// @notice The same non-vacuity discipline applied to the override path.
    ///
    /// @dev Worth stating why this is not optional. Three of the four new handler actions can
    ///      only ever be rejected, so if the productive one silently stopped working the
    ///      campaign would still report every override invariant PASS — while proving nothing
    ///      about a path that moves funds. That is the 16,384-calls-zero-executions failure
    ///      recorded above, and it would recur here first.
    function test_nonVacuity_overridePathExecutesAndItsAdversarialArmsDoNot() public {
        handler.executeValidOverride(11);
        assertEq(handler.overrideExecutions(), 1, "the override path cannot execute at all");
        assertEq(vault.actionNonce(), 1, "an override execution did not consume a nonce");

        handler.executeOverrideOnNonReview(12, true); // ALLOW receipt
        handler.executeOverrideOnNonReview(13, false); // BLOCK receipt — §3.3(7) forbids
        handler.executeOverrideWithForgedOwnerSig(14);
        handler.executeOverrideForAnotherAction(15);

        assertEq(handler.overrideExecutions(), 1, "an adversarial override executed");
        assertFalse(handler.everExecutedNonReviewViaOverride());
        assertFalse(handler.everExecutedForgedOverride());
        assertFalse(handler.everExecutedMismatchedOverride());
        assertEq(vault.actionNonce(), 1, "a rejected override consumed a nonce");
    }

    /// @notice The two arms added by D-042 really construct their inputs and really get
    ///         rejected — without this, the new invariants would pass vacuously in exactly
    ///         the way the campaign they were added to already failed once.
    function test_nonVacuity_futureNonceAndFailingCallArmsAreReachable() public {
        handler.executeFutureNonce(21);
        assertEq(handler.futureNonceAttempts(), 1, "the future-nonce arm did not build an action");
        assertFalse(handler.everExecutedFutureNonce(), "a future nonce executed");
        assertEq(vault.actionNonce(), 0, "a rejected future-nonce action consumed a nonce");

        handler.executeFailingCall(22);
        assertEq(handler.failingCallAttempts(), 1, "the failing-call arm did not build an action");
        assertFalse(handler.everExecutedKnownFailingCall(), "a reverting call counted as an execution");
        assertEq(vault.actionNonce(), 0, "a reverted call consumed a nonce");

        // The arms must reject for the RIGHT reason. A future-nonce action that failed for an
        // unrelated cause, or a "failing" call the callee actually accepted, would leave both
        // new invariants green while testing nothing — the F051 shape, one layer down.
        assertEq(handler.rejectedAttempts(), 2, "an arm was not actually attempted");
        handler.executeValid(23);
        assertEq(vault.actionNonce(), 1, "the valid path stopped working");
    }

    /// @notice Proves the paused and rotated states the campaign relies on are reachable.
    function test_nonVacuity_ownerControlsAreReachable() public {
        handler.togglePause(true);
        assertTrue(vault.paused());
        handler.executeValid(9);
        assertEq(handler.successfulExecutions(), 0, "executed while paused");

        handler.togglePause(false);
        handler.rotateSigner(true);
        handler.executeValid(10);
        assertEq(handler.successfulExecutions(), 1, "rotation left the campaign unable to sign");
    }

    /// @notice Invariant §3.3(9). The nonce is the sole replay defence, so it must advance
    ///         exactly once per execution — never skipping, never repeating.
    function invariant_nonceEqualsSuccessfulExecutions() public view {
        assertEq(vault.actionNonce(), handler.successfulExecutions());
    }

    /// @notice §3.3(9): the nonce is a single monotonically increasing counter, so a receipt
    ///         for a nonce the vault has not reached must be refused exactly as firmly as one
    ///         for a nonce already consumed.
    ///
    /// @dev ADDED D-042, and it is the invariant this campaign most needed. Weakening the
    ///      vault's `!=` to `<` — accepting arbitrary future nonces — survived all ten prior
    ///      invariants across 262,144 calls, because no handler action ever offered one.
    ///      `invariant_nonceEqualsSuccessfulExecutions` cannot catch it: a mutated vault still
    ///      advances the nonce by one per execution, so the count stays consistent while the
    ///      authorization model is broken.
    function invariant_futureNonceNeverExecutes() public view {
        assertFalse(
            handler.everExecutedFutureNonce(),
            "a receipt pinned to an unreached nonce executed - future-nonce authorization"
        );
    }

    /// @notice A call the target rejects must never be recorded as a successful execution.
    ///
    /// @dev ADDED D-042. "Failed external call reported as success" also survived every prior
    ///      invariant, for a different reason: DemoPay could not be made to fail by the old
    ///      handler at all — duration was bounded away from zero, the beneficiary was derived
    ///      non-zero, and value was bounded above zero, which are exactly its three revert
    ///      conditions. The blind spot was in what the handler could BUILD, not in the
    ///      assertions.
    function invariant_failedCallNeverCountsAsExecution() public view {
        assertFalse(
            handler.everExecutedKnownFailingCall(),
            "an action whose callee reverted was recorded as a successful execution"
        );
    }

    /// @notice No action hash executes twice, across the whole campaign.
    function invariant_noActionHashExecutesTwice() public view {
        uint256 n = handler.executedCount();
        for (uint256 i = 0; i < n; i++) {
            assertEq(handler.executionsPerActionHash(handler.executedActionHashes(i)), 1);
        }
    }

    function invariant_pausedNeverExecutes() public view {
        assertFalse(handler.everExecutedWhilePaused());
    }

    /// @notice No replayed, calldata-swapped, or forged-signature attempt ever executes.
    function invariant_tamperedAttemptsNeverExecute() public view {
        assertFalse(handler.everExecutedTampered());
    }

    /// @notice Invariant §3.3(6): only an ALLOW receipt executes on the automatic path.
    ///         Block and review verdicts must never get through it.
    function invariant_onlyAllowVerdictsExecuteOnTheAutomaticPath() public view {
        assertFalse(handler.everExecutedNonAllowVerdict());
    }

    /// @notice §3.3(7) on the override path: only a REVIEW verdict is overridable. A BLOCK
    ///         "requires a new mandate or policy; it cannot be overridden directly."
    function invariant_onlyReviewVerdictsExecuteOnTheOverridePath() public view {
        assertFalse(handler.everExecutedNonReviewViaOverride());
    }

    /// @notice §3.3(7)'s "separately authenticated": the override is the HUMAN's half, so a
    ///         signature from the evaluator's own key must never satisfy it. This is the
    ///         property that keeps a compromised signer from authoring both halves.
    function invariant_overrideRequiresTheOwnersOwnSignature() public view {
        assertFalse(handler.everExecutedForgedOverride());
    }

    /// @notice An override authorises ONE exact action. A genuine owner signature over a
    ///         different action must not execute this one.
    function invariant_overrideMustNameTheExactAction() public view {
        assertFalse(handler.everExecutedMismatchedOverride());
    }

    /// @notice The owner's authority is never reachable through the execution path,
    ///         however many actions run.
    function invariant_ownerAndCapsAreImmutableFromExecution() public view {
        assertEq(vault.owner(), vm.addr(OWNER_PK));
        assertEq(vault.maxNativeValueWei(), 0.01 ether);
    }
}
