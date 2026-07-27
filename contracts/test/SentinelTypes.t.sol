// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

import {Test} from "forge-std/Test.sol";
import {SentinelTypes as T} from "../src/types/SentinelTypes.sol";

/// @title SentinelTypes canonical-hash suite
/// @notice Covers §9 step 1: typed payloads and canonical hashes.
///
/// @dev WHAT THIS SUITE IS EVIDENCE FOR, AND WHAT IT IS NOT (AGENTS.md test-coverage
///      discipline; house rule 4).
///
///      Evidence for: the five §5 payload schemas hash deterministically; each typehash
///      matches an independently transcribed type string AND a pinned golden digest;
///      mutating any single bound field changes the payload hash (invariant §3.3(5));
///      the domain separator binds chain and vault; fail-closed enum defaults hold.
///
///      NOT evidence for: anything about signatures, recovery, replay, or the vault —
///      none of that exists yet. Steps 2 and 3 of §9 own those, and the replay/tamper
///      invariants Gate S1 requires are not in this file.
contract SentinelTypesTest is Test {
    // -----------------------------------------------------------------
    // Golden typehashes.
    // -----------------------------------------------------------------
    // Computed out-of-band with `cast keccak` and pinned here. Their purpose is to fail
    // loudly on a schema edit. A test that only compared the library constant against a
    // string re-derived in the same file would still pass if someone edited both — these
    // literals are the tripwire that a schema change must be deliberate, because updating
    // them is a conscious act that shows up in review as a changed hash.
    //
    // If one of these fails, do NOT update the constant to make it green. A changed
    // typehash invalidates every previously signed payload and every pinned fixture.
    bytes32 constant GOLD_MANDATE = 0xc4b5766f52cd5eee3830dfe849c18b2cdc58d3d698d5c59e3a90c6dbe9d86799;
    bytes32 constant GOLD_POLICY = 0xaa588a03b15fff97a72f063b7627ed7a61f2d76c4ca795da0607375d06a7f2a8;
    bytes32 constant GOLD_ACTION = 0x47787d5c4effb836c1e32339e527f5d91ae6e221e945eaf5c549614b02a60cff;
    bytes32 constant GOLD_RECEIPT = 0xbbdf70ecc28b4e3c3e229f3b2bfdebbd4a9960d1302f588d52b09717ef5db797;
    bytes32 constant GOLD_OVERRIDE = 0x2257b6461a2c5c9477706f5afea11a1e3df3dbe16cb5c9a2b2150311e3cc4fea;

    /// @dev The canonical EIP-712 domain typehash, identical across every EIP-712
    ///      implementation in the ecosystem. Matching it is an external cross-check that
    ///      our domain string has no stray whitespace or field-order drift.
    bytes32 constant GOLD_DOMAIN = 0x8b73c3c69bb8fe3d512ecc4cf759cc79239f7b179b0ffacaa9a75d522b39400f;

    // Deterministic stand-in addresses for hashing fixtures. No key material; these are
    // labels, not accounts. Real addresses arrive with the vault in §9 step 2.
    address constant OWNER = address(0xA11CE);
    address constant VAULT = address(0x7A017);
    address constant DEMOPAY = address(0xDEB0);
    address constant SIGNER = address(0x519E4);

    // =================================================================
    // Typehash integrity
    // =================================================================

    function test_typehashes_matchGoldenDigests() public pure {
        assertEq(T.MANDATE_TYPEHASH, GOLD_MANDATE, "MandatePayload schema changed");
        assertEq(T.POLICY_TYPEHASH, GOLD_POLICY, "PolicyPayload schema changed");
        assertEq(T.ACTION_TYPEHASH, GOLD_ACTION, "ActionPayload schema changed");
        assertEq(T.RECEIPT_TYPEHASH, GOLD_RECEIPT, "DecisionReceiptPayload schema changed");
        assertEq(T.OVERRIDE_TYPEHASH, GOLD_OVERRIDE, "OverrideAuthorizationPayload schema changed");
        assertEq(T.EIP712_DOMAIN_TYPEHASH, GOLD_DOMAIN, "EIP712Domain string is non-canonical");
    }

    /// @notice Independent transcription: the type strings are re-typed here from §5 and
    ///         must hash to the same values. Catches a typo in the library's literal that
    ///         a golden-only check would notice but not localise.
    function test_typehashes_matchIndependentTranscription() public pure {
        assertEq(
            keccak256(
                "MandatePayload(uint16 schemaVersion,bytes32 mandateId,address principal,address vault,uint256 chainId,address target,bytes32 targetCodeHash,bytes4 selector,uint256 maxNativeValueWei,bytes32 purposeKind,bytes32 resourceId,address beneficiary,uint64 durationSeconds,bool recurringAllowed,uint64 validAfter,uint64 validUntil,bytes32 policyHash)"
            ),
            T.MANDATE_TYPEHASH
        );
        assertEq(
            keccak256(
                "PolicyPayload(uint16 schemaVersion,uint32 policyVersion,address vault,uint256 chainId,uint8 allowedOperation,bytes32 allowedTargetsHash,bytes32 allowedSelectorsHash,uint256 maxNativeValueWei,uint256 maxAllowanceIncreaseBaseUnits,bytes32 allowedCallGraphHash,uint64 validAfter,uint64 validUntil,uint8 failureMode)"
            ),
            T.POLICY_TYPEHASH
        );
        assertEq(
            keccak256(
                "ActionPayload(uint16 schemaVersion,uint256 chainId,address vault,uint256 actionNonce,address target,uint256 valueWei,bytes32 dataHash,uint8 operation,bytes32 mandateHash,bytes32 policyHash,uint64 deadline)"
            ),
            T.ACTION_TYPEHASH
        );
        assertEq(
            keccak256(
                "DecisionReceiptPayload(uint16 schemaVersion,bytes32 decisionId,bytes32 actionHash,bytes32 mandateHash,bytes32 policyHash,uint8 verdict,bytes32 reasonCodesHash,bytes32 evidenceHash,uint256 simulationBlockNumber,bytes32 simulationBlockHash,uint64 issuedAt,uint64 expiresAt,address signer)"
            ),
            T.RECEIPT_TYPEHASH
        );
        assertEq(
            keccak256(
                "OverrideAuthorizationPayload(uint16 schemaVersion,bytes32 reviewReceiptHash,bytes32 actionHash,bytes32 mandateHash,bytes32 policyHash,uint256 actionNonce,bytes32 reasonHash,uint64 issuedAt,uint64 expiresAt)"
            ),
            T.OVERRIDE_TYPEHASH
        );
    }

    /// @notice §5: "Signatures are envelope fields and are excluded from the payload
    ///         hashes they sign." Enforced structurally — no payload type string may
    ///         mention a signature member.
    function test_noPayloadTypeStringContainsASignatureField() public pure {
        assertFalse(_contains(T.MANDATE_TYPE, "ignature"), "mandate type leaks a signature field");
        assertFalse(_contains(T.POLICY_TYPE, "ignature"), "policy type leaks a signature field");
        assertFalse(_contains(T.ACTION_TYPE, "ignature"), "action type leaks a signature field");
        assertFalse(_contains(T.RECEIPT_TYPE, "ignature"), "receipt type leaks a signature field");
        assertFalse(_contains(T.OVERRIDE_TYPE, "ignature"), "override type leaks a signature field");
    }

    // =================================================================
    // Fail-closed defaults
    // =================================================================

    /// @notice Invariant §3.3(8) in the type system: a zero value is never an allow.
    function test_zeroValuedEnumsAreFailClosed() public pure {
        assertEq(uint8(T.Verdict.BLOCK), 0, "BLOCK must be the zero verdict");
        assertEq(uint8(T.FailureMode.FAIL_CLOSED), 0, "FAIL_CLOSED must be the zero failure mode");
        assertEq(uint8(T.Operation.CALL), 0, "CALL must be the zero operation");

        // A zero-initialised receipt decodes as BLOCK, not ALLOW.
        T.DecisionReceiptPayload memory empty;
        assertEq(empty.verdict, uint8(T.Verdict.BLOCK), "empty receipt must read as BLOCK");
        assertTrue(empty.verdict != uint8(T.Verdict.ALLOW), "empty receipt must never read as ALLOW");
    }

    // =================================================================
    // Domain separation
    // =================================================================

    function test_domainSeparator_bindsChainAndVault() public pure {
        address vaultA = address(0xA11CE);
        address vaultB = address(0xB0B);

        bytes32 base = T.domainSeparator(31337, vaultA);
        assertTrue(base != T.domainSeparator(8453, vaultA), "chainId must change the domain");
        assertTrue(base != T.domainSeparator(31337, vaultB), "vault must change the domain");
        assertEq(base, T.domainSeparator(31337, vaultA), "domain must be deterministic");
    }

    function testFuzz_domainSeparator_isInjectiveOverChainAndVault(
        uint256 chainA,
        uint256 chainB,
        address vaultA,
        address vaultB
    ) public pure {
        vm.assume(chainA != chainB || vaultA != vaultB);
        assertTrue(
            T.domainSeparator(chainA, vaultA) != T.domainSeparator(chainB, vaultB),
            "distinct (chain, vault) must produce distinct domains"
        );
    }

    function test_digest_isEip712Framed() public pure {
        bytes32 sep = T.domainSeparator(31337, address(0xA11CE));
        bytes32 structHash = keccak256("arbitrary");
        assertEq(
            T.digest(sep, structHash),
            keccak256(abi.encodePacked(hex"1901", sep, structHash)),
            "digest must be keccak(0x1901 || domain || struct)"
        );
    }

    // =================================================================
    // Invariant §3.3(5): mutating a bound field invalidates the binding
    // =================================================================

    /// @notice Every field named in invariant §3.3(4) must change `actionHash` when
    ///         mutated. This is the mechanical form of "any mutation to a bound field
    ///         invalidates authorization" — at the hashing layer. The vault-level and
    ///         signature-level halves of that invariant belong to §9 steps 2–3 and are
    ///         deliberately not claimed here.
    function testFuzz_actionHash_changesOnAnyBoundFieldMutation(uint8 fieldIndex) public pure {
        fieldIndex = uint8(bound(fieldIndex, 0, 10));

        T.ActionPayload memory a = _sampleAction();
        bytes32 before = T.hashAction(a);

        // `unchecked` is deliberate. The fixtures use type(uint64).max for "no expiry",
        // which is realistic, and this test only needs each mutation to yield a DIFFERENT
        // value — wrapping max to 0 satisfies that. Checked arithmetic here would make the
        // test revert on its own most realistic fixture, which is what the fuzzer found.
        unchecked {
            if (fieldIndex == 0) a.schemaVersion += 1;
            else if (fieldIndex == 1) a.chainId += 1;
            else if (fieldIndex == 2) a.vault = address(uint160(a.vault) + 1);
            else if (fieldIndex == 3) a.actionNonce += 1;
            else if (fieldIndex == 4) a.target = address(uint160(a.target) + 1);
            else if (fieldIndex == 5) a.valueWei += 1;
            else if (fieldIndex == 6) a.dataHash = keccak256(abi.encode(a.dataHash));
            else if (fieldIndex == 7) a.operation += 1;
            else if (fieldIndex == 8) a.mandateHash = keccak256(abi.encode(a.mandateHash));
            else if (fieldIndex == 9) a.policyHash = keccak256(abi.encode(a.policyHash));
            else a.deadline += 1;
        }

        assertTrue(T.hashAction(a) != before, "a bound field mutation must change actionHash");
    }

    function testFuzz_mandateHash_changesOnAnyBoundFieldMutation(uint8 fieldIndex) public pure {
        fieldIndex = uint8(bound(fieldIndex, 0, 16));

        T.MandatePayload memory m = _sampleMandate();
        bytes32 before = T.hashMandate(m);

        // See the note in the action variant above for why this is unchecked.
        unchecked {
            if (fieldIndex == 0) m.schemaVersion += 1;
            else if (fieldIndex == 1) m.mandateId = keccak256(abi.encode(m.mandateId));
            else if (fieldIndex == 2) m.principal = address(uint160(m.principal) + 1);
            else if (fieldIndex == 3) m.vault = address(uint160(m.vault) + 1);
            else if (fieldIndex == 4) m.chainId += 1;
            else if (fieldIndex == 5) m.target = address(uint160(m.target) + 1);
            else if (fieldIndex == 6) m.targetCodeHash = keccak256(abi.encode(m.targetCodeHash));
            else if (fieldIndex == 7) m.selector = bytes4(uint32(m.selector) + 1);
            else if (fieldIndex == 8) m.maxNativeValueWei += 1;
            else if (fieldIndex == 9) m.purposeKind = keccak256(abi.encode(m.purposeKind));
            else if (fieldIndex == 10) m.resourceId = keccak256(abi.encode(m.resourceId));
            else if (fieldIndex == 11) m.beneficiary = address(uint160(m.beneficiary) + 1);
            else if (fieldIndex == 12) m.durationSeconds += 1;
            else if (fieldIndex == 13) m.recurringAllowed = !m.recurringAllowed;
            else if (fieldIndex == 14) m.validAfter += 1;
            else if (fieldIndex == 15) m.validUntil += 1;
            else m.policyHash = keccak256(abi.encode(m.policyHash));
        }

        assertTrue(T.hashMandate(m) != before, "a bound field mutation must change mandateHash");
    }

    /// @notice The Case 3 shape at the hashing layer: `recurringAllowed` and `resourceId`
    ///         are exactly the fields a basic wallet policy does not express, and they
    ///         must be inside the signed hash or mandate conformance has nothing to bind.
    function test_mandateHash_bindsPurposeFieldsAPolicyEngineWouldMiss() public pure {
        T.MandatePayload memory basic = _sampleMandate();

        T.MandatePayload memory recurring = _sampleMandate();
        recurring.recurringAllowed = true;

        T.MandatePayload memory premium = _sampleMandate();
        premium.resourceId = keccak256("premium-monthly");

        assertTrue(T.hashMandate(basic) != T.hashMandate(recurring), "recurrence must be bound");
        assertTrue(T.hashMandate(basic) != T.hashMandate(premium), "resourceId must be bound");
    }

    // =================================================================
    // Determinism
    // =================================================================

    function test_allHashesAreDeterministic() public pure {
        assertEq(T.hashMandate(_sampleMandate()), T.hashMandate(_sampleMandate()));
        assertEq(T.hashPolicy(_samplePolicy()), T.hashPolicy(_samplePolicy()));
        assertEq(T.hashAction(_sampleAction()), T.hashAction(_sampleAction()));
        assertEq(T.hashReceipt(_sampleReceipt()), T.hashReceipt(_sampleReceipt()));
        assertEq(T.hashOverride(_sampleOverride()), T.hashOverride(_sampleOverride()));
    }

    /// @notice Distinct payload types must not collide even when structurally similar.
    ///         Typehash prefixing is what guarantees this; the test proves the prefixing
    ///         is actually in effect rather than assumed.
    function test_distinctPayloadTypesDoNotCollide() public pure {
        bytes32[5] memory hashes = [
            T.hashMandate(_sampleMandate()),
            T.hashPolicy(_samplePolicy()),
            T.hashAction(_sampleAction()),
            T.hashReceipt(_sampleReceipt()),
            T.hashOverride(_sampleOverride())
        ];
        for (uint256 i = 0; i < hashes.length; i++) {
            for (uint256 j = i + 1; j < hashes.length; j++) {
                assertTrue(hashes[i] != hashes[j], "payload hashes must not collide across types");
            }
        }
    }

    // =================================================================
    // Fixtures
    // =================================================================
    // The Case 1 shape from §4.2: one purchase of weather-basic-24h, owner as
    // beneficiary, recurrence disabled.

    function _sampleMandate() internal pure returns (T.MandatePayload memory m) {
        m = T.MandatePayload({
            schemaVersion: 1,
            mandateId: keccak256("mandate-1"),
            principal: OWNER,
            vault: VAULT,
            chainId: 31337,
            target: DEMOPAY,
            targetCodeHash: keccak256("DemoPay-runtime"),
            selector: bytes4(keccak256("purchase(bytes32,address,uint64,bool)")),
            maxNativeValueWei: 0.01 ether,
            purposeKind: keccak256("purchase"),
            resourceId: keccak256("weather-basic-24h"),
            beneficiary: OWNER,
            durationSeconds: 24 hours,
            recurringAllowed: false,
            validAfter: 0,
            validUntil: type(uint64).max,
            policyHash: keccak256("policy-1")
        });
    }

    function _samplePolicy() internal pure returns (T.PolicyPayload memory) {
        return T.PolicyPayload({
            schemaVersion: 1,
            policyVersion: 1,
            vault: VAULT,
            chainId: 31337,
            allowedOperation: uint8(T.Operation.CALL),
            allowedTargetsHash: keccak256("targets"),
            allowedSelectorsHash: keccak256("selectors"),
            maxNativeValueWei: 0.01 ether,
            maxAllowanceIncreaseBaseUnits: 0,
            allowedCallGraphHash: keccak256("callgraph"),
            validAfter: 0,
            validUntil: type(uint64).max,
            failureMode: uint8(T.FailureMode.FAIL_CLOSED)
        });
    }

    function _sampleAction() internal pure returns (T.ActionPayload memory) {
        return T.ActionPayload({
            schemaVersion: 1,
            chainId: 31337,
            vault: VAULT,
            actionNonce: 0,
            target: DEMOPAY,
            valueWei: 0.005 ether,
            dataHash: keccak256("calldata"),
            operation: uint8(T.Operation.CALL),
            mandateHash: keccak256("mandate-1"),
            policyHash: keccak256("policy-1"),
            deadline: type(uint64).max
        });
    }

    function _sampleReceipt() internal pure returns (T.DecisionReceiptPayload memory) {
        return T.DecisionReceiptPayload({
            schemaVersion: 1,
            decisionId: keccak256("decision-1"),
            actionHash: keccak256("action-1"),
            mandateHash: keccak256("mandate-1"),
            policyHash: keccak256("policy-1"),
            verdict: uint8(T.Verdict.ALLOW),
            reasonCodesHash: keccak256("reasons"),
            evidenceHash: keccak256("evidence"),
            simulationBlockNumber: 12345,
            simulationBlockHash: keccak256("blockhash"),
            issuedAt: 1000,
            expiresAt: 2000,
            signer: SIGNER
        });
    }

    function _sampleOverride() internal pure returns (T.OverrideAuthorizationPayload memory) {
        return T.OverrideAuthorizationPayload({
            schemaVersion: 1,
            reviewReceiptHash: keccak256("review-receipt-1"),
            actionHash: keccak256("action-1"),
            mandateHash: keccak256("mandate-1"),
            policyHash: keccak256("policy-1"),
            actionNonce: 0,
            reasonHash: keccak256("reason"),
            issuedAt: 1000,
            expiresAt: 2000
        });
    }

    function _contains(string memory haystack, string memory needle) internal pure returns (bool) {
        bytes memory h = bytes(haystack);
        bytes memory n = bytes(needle);
        if (n.length == 0 || n.length > h.length) return false;
        for (uint256 i = 0; i <= h.length - n.length; i++) {
            bool ok = true;
            for (uint256 j = 0; j < n.length; j++) {
                if (h[i + j] != n[j]) {
                    ok = false;
                    break;
                }
            }
            if (ok) return true;
        }
        return false;
    }
}
