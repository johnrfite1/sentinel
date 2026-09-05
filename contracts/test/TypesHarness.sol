// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {SentinelTypes as T} from "../src/types/SentinelTypes.sol";

/// @title TypesHarness
/// @notice Exposes the `SentinelTypes` library's pure hash functions as external calls so
///         an off-chain implementation can be differentially tested against the Solidity
///         one over a real EVM.
///
/// @dev WHY THIS EXISTS. The vault recomputes `hashAction` and `hashReceipt` on every
///      execution, so the TypeScript signer's encoding of those two is checked against
///      Solidity by every passing end-to-end test — a wrong padding or field order shows up
///      as a rejected receipt.
///
///      `hashMandate`, `hashPolicy`, and `hashOverride` get no such check for free.
///      SentinelVault stores the mandate and policy as *hashes* and never recomputes them
///      from their fields (§3.2 steps 3–4), so a TypeScript encoder could disagree with
///      Solidity on all three and every onchain test would still pass: the offchain side
///      would simply activate its own wrong hash and then match it. The disagreement would
///      surface much later, in the D-010 verifier or in an evidence bundle nobody could
///      reproduce — which is exactly the class of schema defect D-010 says is cheap to fix
///      now and expensive once the corpus has fossilised.
///
///      This contract is test-only scaffolding. It holds no state, no key material, and no
///      authority; it is deployed by the TypeScript suite and by nothing else. It is
///      deliberately NOT in `src/` — it is not part of the system under test, and putting
///      it there would enlarge the deployed surface to serve a test.
contract TypesHarness {
    function hashMandate(T.MandatePayload calldata m) external pure returns (bytes32) {
        return T.hashMandate(m);
    }

    function hashPolicy(T.PolicyPayload calldata p) external pure returns (bytes32) {
        return T.hashPolicy(p);
    }

    function hashAction(T.ActionPayload calldata a) external pure returns (bytes32) {
        return T.hashAction(a);
    }

    function hashReceipt(T.DecisionReceiptPayload calldata r) external pure returns (bytes32) {
        return T.hashReceipt(r);
    }

    function hashOverride(T.OverrideAuthorizationPayload calldata o) external pure returns (bytes32) {
        return T.hashOverride(o);
    }

    function domainSeparator(uint256 chainId, address vault) external pure returns (bytes32) {
        return T.domainSeparator(chainId, vault);
    }
}
