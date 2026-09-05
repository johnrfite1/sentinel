// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

import {ERC20} from "openzeppelin-contracts/contracts/token/ERC20/ERC20.sol";

/// @title DemoERC20
/// @notice §4. Exists for exactly one reason: to demonstrate approval detection in the
///         Case 2 prompt-injection fixture. It is not part of the normal purchase path.
///
/// @dev Deliberately a stock OpenZeppelin ERC20 with nothing added. The Case 2 fixture's
///      credibility depends on `approve` having ordinary, unsurprising semantics — a
///      hand-rolled or "hardened" token would make the demonstrated attack a property of
///      our token rather than of ERC20 approvals generally, which is the opposite of the
///      point. §8 already limits the claim: DemoERC20 approval handling does not
///      generalize to every token or authorization scheme.
contract DemoERC20 is ERC20 {
    constructor(address initialHolder, uint256 initialSupply) ERC20("Demo Billing Token", "DEMO") {
        _mint(initialHolder, initialSupply);
    }
}
