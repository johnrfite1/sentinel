// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.28;

/// @title DemoPay
/// @notice §4.1. Accepts test ETH for a resource purchase and writes inspectable
///         entitlement state.
///
/// @dev Two properties are load-bearing for the lab and must not be "improved" away:
///
///      1. **It makes no external calls.** That keeps the normal purchase to exactly one
///         payable CALL with no internal call graph, which is what lets §5.7's
///         "allowed call graph" check mean something. Adding a callback, a hook, or a
///         fee transfer here would silently widen the supported effect surface.
///
///      2. **Entitlement is contract state, not just an event.** §5.7 is explicit that an
///         event alone is not proof of entitlement — conformance checks the resulting
///         state. The event is supporting evidence; `entitlementExpiry` is the truth.
contract DemoPay {
    event Purchased(
        address indexed buyer,
        address indexed beneficiary,
        bytes32 indexed resourceId,
        uint64 durationSeconds,
        bool recurring,
        uint256 valueWei,
        uint64 expiry
    );

    error NoPayment();
    error ZeroBeneficiary();
    error ZeroDuration();

    /// @notice beneficiary => resourceId => unix expiry.
    mapping(address => mapping(bytes32 => uint64)) public entitlementExpiry;

    /// @notice beneficiary => resourceId => whether recurrence was enabled at purchase.
    /// @dev Stored separately from expiry because Case 3 turns on recurrence being a
    ///      *bound, inspectable* effect: a mandate that forbids recurrence must be
    ///      violable in a way the effect extractor can actually see.
    mapping(address => mapping(bytes32 => bool)) public recurringEnabled;

    function purchase(bytes32 resourceId, address beneficiary, uint64 durationSeconds, bool recurring)
        external
        payable
    {
        if (msg.value == 0) revert NoPayment();
        if (beneficiary == address(0)) revert ZeroBeneficiary();
        if (durationSeconds == 0) revert ZeroDuration();

        uint64 base = entitlementExpiry[beneficiary][resourceId];
        // Same reasoning as the vault's validity windows: this computes an entitlement
        // expiry measured in hours, so a validator nudging the timestamp by seconds moves
        // the expiry by seconds. There is no value-bearing comparison and no randomness
        // being derived. Suppressed per-line with a reason rather than by relaxing
        // `deny = "warnings"`.
        // forge-lint: disable-next-line(block-timestamp)
        uint64 start = base > uint64(block.timestamp) ? base : uint64(block.timestamp);
        uint64 expiry = start + durationSeconds;

        entitlementExpiry[beneficiary][resourceId] = expiry;
        recurringEnabled[beneficiary][resourceId] = recurring;

        emit Purchased(msg.sender, beneficiary, resourceId, durationSeconds, recurring, msg.value, expiry);
    }
}
