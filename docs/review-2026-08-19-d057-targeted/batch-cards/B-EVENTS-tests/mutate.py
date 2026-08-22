#!/usr/bin/env python3
"""Apply one exact B-EVENTS mutant to an isolated Sentinel checkout."""

from pathlib import Path
import sys


SOURCE = Path("contracts/src/SentinelVault.sol")
TEST = Path("contracts/test/SentinelVault.events.t.sol")


def one(old: str, new: str, path: Path = SOURCE):
    return (path, old, new)


MUTANTS = {
    # One warning-clean omission for every required vault event.
    "omit_mandate_activated": one("        emit MandateActivated(mandateHash);\n", ""),
    "omit_mandate_revoked": one(
        "        bytes32 previous = activeMandateHash;\n"
        "        activeMandateHash = bytes32(0);\n"
        "        emit MandateRevoked(previous);\n",
        "        activeMandateHash = bytes32(0);\n",
    ),
    "omit_policy_activated": one("        emit PolicyActivated(policyHash);\n", ""),
    "omit_signer_rotated": one("        emit SignerRotated(signer, newSigner);\n", ""),
    "omit_paused_set": one("        emit PausedSet(value);\n", ""),
    "omit_recovered": one("        emit Recovered(to, amount);\n", ""),
    "omit_override_authorized": one(
        "        emit OverrideAuthorized(\n"
        "            auth.actionHash, overrideHash, auth.reviewReceiptHash, auth.reasonHash, auth.expiresAt\n"
        "        );\n",
        "",
    ),
    "omit_action_executed": one(
        "        bytes32 decisionId,\n"
        "        bool viaOverride\n"
        "    ) internal returns (bytes memory) {\n"
        "        bytes32 actionHash = T.hashAction(action);\n"
        "        actionNonce += 1;\n\n"
        "        emit ActionExecuted(actionHash, action.actionNonce, decisionId, viaOverride);\n",
        "        bytes32,\n"
        "        bool\n"
        "    ) internal returns (bytes memory) {\n"
        "        actionNonce += 1;\n",
    ),
    # Every event field gets a discriminating value substitution.
    "field_mandate_activated_hash": one(
        "        emit MandateActivated(mandateHash);\n",
        "        emit MandateActivated(bytes32(0));\n",
    ),
    "field_mandate_revoked_hash": one(
        "        bytes32 previous = activeMandateHash;\n"
        "        activeMandateHash = bytes32(0);\n"
        "        emit MandateRevoked(previous);\n",
        "        activeMandateHash = bytes32(0);\n"
        "        emit MandateRevoked(bytes32(0));\n",
    ),
    "field_policy_activated_hash": one(
        "        emit PolicyActivated(policyHash);\n",
        "        emit PolicyActivated(bytes32(0));\n",
    ),
    "field_signer_previous": one(
        "        emit SignerRotated(signer, newSigner);\n",
        "        emit SignerRotated(newSigner, newSigner);\n",
    ),
    "field_signer_new": one(
        "        emit SignerRotated(signer, newSigner);\n",
        "        emit SignerRotated(signer, signer);\n",
    ),
    "field_paused": one("        emit PausedSet(value);\n", "        emit PausedSet(!value);\n"),
    "field_recovered_to": one(
        "        emit Recovered(to, amount);\n",
        "        emit Recovered(payable(address(this)), amount);\n",
    ),
    "field_recovered_amount": one(
        "        emit Recovered(to, amount);\n",
        "        emit Recovered(to, address(this).balance);\n",
    ),
    "field_override_action_hash": one(
        "            auth.actionHash, overrideHash, auth.reviewReceiptHash, auth.reasonHash, auth.expiresAt\n",
        "            bytes32(0), overrideHash, auth.reviewReceiptHash, auth.reasonHash, auth.expiresAt\n",
    ),
    "field_override_hash": one(
        "            auth.actionHash, overrideHash, auth.reviewReceiptHash, auth.reasonHash, auth.expiresAt\n",
        "            auth.actionHash, bytes32(0), auth.reviewReceiptHash, auth.reasonHash, auth.expiresAt\n",
    ),
    "field_override_receipt_hash": one(
        "            auth.actionHash, overrideHash, auth.reviewReceiptHash, auth.reasonHash, auth.expiresAt\n",
        "            auth.actionHash, overrideHash, bytes32(0), auth.reasonHash, auth.expiresAt\n",
    ),
    "field_override_reason_hash": one(
        "            auth.actionHash, overrideHash, auth.reviewReceiptHash, auth.reasonHash, auth.expiresAt\n",
        "            auth.actionHash, overrideHash, auth.reviewReceiptHash, bytes32(0), auth.expiresAt\n",
    ),
    "field_override_expires_at": one(
        "            auth.actionHash, overrideHash, auth.reviewReceiptHash, auth.reasonHash, auth.expiresAt\n",
        "            auth.actionHash, overrideHash, auth.reviewReceiptHash, auth.reasonHash, uint64(0)\n",
    ),
    "field_action_hash": one(
        "        bytes32 actionHash = T.hashAction(action);\n",
        "        bytes32 actionHash = bytes32(0);\n",
    ),
    "field_action_nonce": one(
        "        emit ActionExecuted(actionHash, action.actionNonce, decisionId, viaOverride);\n",
        "        emit ActionExecuted(actionHash, actionNonce, decisionId, viaOverride);\n",
    ),
    "field_action_decision_id": one(
        "        bytes32 decisionId,\n"
        "        bool viaOverride\n"
        "    ) internal returns (bytes memory) {\n"
        "        bytes32 actionHash = T.hashAction(action);\n"
        "        actionNonce += 1;\n\n"
        "        emit ActionExecuted(actionHash, action.actionNonce, decisionId, viaOverride);\n",
        "        bytes32,\n"
        "        bool viaOverride\n"
        "    ) internal returns (bytes memory) {\n"
        "        bytes32 actionHash = T.hashAction(action);\n"
        "        actionNonce += 1;\n\n"
        "        emit ActionExecuted(actionHash, action.actionNonce, bytes32(0), viaOverride);\n",
    ),
    "field_action_via_false": one(
        "        bytes32 decisionId,\n"
        "        bool viaOverride\n"
        "    ) internal returns (bytes memory) {\n"
        "        bytes32 actionHash = T.hashAction(action);\n"
        "        actionNonce += 1;\n\n"
        "        emit ActionExecuted(actionHash, action.actionNonce, decisionId, viaOverride);\n",
        "        bytes32 decisionId,\n"
        "        bool\n"
        "    ) internal returns (bytes memory) {\n"
        "        bytes32 actionHash = T.hashAction(action);\n"
        "        actionNonce += 1;\n\n"
        "        emit ActionExecuted(actionHash, action.actionNonce, decisionId, false);\n",
    ),
    "field_action_via_true": one(
        "        bytes32 decisionId,\n"
        "        bool viaOverride\n"
        "    ) internal returns (bytes memory) {\n"
        "        bytes32 actionHash = T.hashAction(action);\n"
        "        actionNonce += 1;\n\n"
        "        emit ActionExecuted(actionHash, action.actionNonce, decisionId, viaOverride);\n",
        "        bytes32 decisionId,\n"
        "        bool\n"
        "    ) internal returns (bytes memory) {\n"
        "        bytes32 actionHash = T.hashAction(action);\n"
        "        actionNonce += 1;\n\n"
        "        emit ActionExecuted(actionHash, action.actionNonce, decisionId, true);\n",
    ),
    # Call-site route discrimination, independently of the central boolean variants.
    "route_automatic_as_override": one(
        "        return _consumeAndCall(action, callData, receipt.decisionId, false);\n",
        "        return _consumeAndCall(action, callData, receipt.decisionId, true);\n",
    ),
    "route_override_as_automatic": one(
        "        return _consumeAndCall(action, callData, receipt.decisionId, true);\n",
        "        return _consumeAndCall(action, callData, receipt.decisionId, false);\n",
    ),
    # Exact per-route vault-log censuses reject extra events as well as missing ones.
    "extra_owner_event": one(
        "        emit MandateActivated(mandateHash);\n",
        "        emit MandateActivated(mandateHash);\n"
        "        emit PolicyActivated(mandateHash);\n",
    ),
    "extra_automatic_override_event": one(
        "        return _consumeAndCall(action, callData, receipt.decisionId, false);\n",
        "        emit OverrideAuthorized(T.hashAction(action), bytes32(0), bytes32(0), bytes32(0), 0);\n"
        "        return _consumeAndCall(action, callData, receipt.decisionId, false);\n",
    ),
    "extra_override_event": one(
        "        emit OverrideAuthorized(\n"
        "            auth.actionHash, overrideHash, auth.reviewReceiptHash, auth.reasonHash, auth.expiresAt\n"
        "        );\n",
        "        emit OverrideAuthorized(\n"
        "            auth.actionHash, overrideHash, auth.reviewReceiptHash, auth.reasonHash, auth.expiresAt\n"
        "        );\n"
        "        emit OverrideAuthorized(\n"
        "            auth.actionHash, overrideHash, auth.reviewReceiptHash, auth.reasonHash, auth.expiresAt\n"
        "        );\n",
    ),
    # Independent test declarations freeze every indexed/data location used by the API.
    "index_mandate": one(
        "    event MandateActivated(bytes32 indexed mandateHash);\n",
        "    event MandateActivated(bytes32 mandateHash);\n",
    ),
    "index_revoked": one(
        "    event MandateRevoked(bytes32 indexed mandateHash);\n",
        "    event MandateRevoked(bytes32 mandateHash);\n",
    ),
    "index_policy": one(
        "    event PolicyActivated(bytes32 indexed policyHash);\n",
        "    event PolicyActivated(bytes32 policyHash);\n",
    ),
    "index_signer_previous": one(
        "    event SignerRotated(address indexed previousSigner, address indexed newSigner);\n",
        "    event SignerRotated(address previousSigner, address indexed newSigner);\n",
    ),
    "index_signer_new": one(
        "    event SignerRotated(address indexed previousSigner, address indexed newSigner);\n",
        "    event SignerRotated(address indexed previousSigner, address newSigner);\n",
    ),
    "index_recovered_to": one(
        "    event Recovered(address indexed to, uint256 amount);\n",
        "    event Recovered(address to, uint256 amount);\n",
    ),
    "index_action_hash": one(
        "        bytes32 indexed actionHash, uint256 indexed actionNonce, bytes32 decisionId, bool viaOverride\n",
        "        bytes32 actionHash, uint256 indexed actionNonce, bytes32 decisionId, bool viaOverride\n",
    ),
    "index_action_nonce": one(
        "        bytes32 indexed actionHash, uint256 indexed actionNonce, bytes32 decisionId, bool viaOverride\n",
        "        bytes32 indexed actionHash, uint256 actionNonce, bytes32 decisionId, bool viaOverride\n",
    ),
    "index_override_action_hash": one(
        "        bytes32 indexed actionHash,\n        bytes32 indexed overrideHash,\n",
        "        bytes32 actionHash,\n        bytes32 indexed overrideHash,\n",
    ),
    "index_override_hash": one(
        "        bytes32 indexed actionHash,\n        bytes32 indexed overrideHash,\n",
        "        bytes32 indexed actionHash,\n        bytes32 overrideHash,\n",
    ),
    "index_paused": one(
        "    event PausedSet(bool paused);\n",
        "    event PausedSet(bool indexed paused);\n",
    ),
    "index_recovered_amount": one(
        "    event Recovered(address indexed to, uint256 amount);\n",
        "    event Recovered(address indexed to, uint256 indexed amount);\n",
    ),
    "index_action_decision_id": one(
        "        bytes32 indexed actionHash, uint256 indexed actionNonce, bytes32 decisionId, bool viaOverride\n",
        "        bytes32 indexed actionHash, uint256 indexed actionNonce, bytes32 indexed decisionId, bool viaOverride\n",
    ),
    "index_action_via_override": one(
        "        bytes32 indexed actionHash, uint256 indexed actionNonce, bytes32 decisionId, bool viaOverride\n",
        "        bytes32 indexed actionHash, uint256 indexed actionNonce, bytes32 decisionId, bool indexed viaOverride\n",
    ),
    "index_override_receipt_hash": one(
        "        bytes32 reviewReceiptHash,\n",
        "        bytes32 indexed reviewReceiptHash,\n",
    ),
    "index_override_reason_hash": one(
        "        bytes32 reasonHash,\n",
        "        bytes32 indexed reasonHash,\n",
    ),
    "index_override_expires_at": one(
        "        uint64 expiresAt\n",
        "        uint64 indexed expiresAt\n",
    ),
    # Event-name discrimination and emitter binding instrument controls.
    "topic_mandate_as_policy": one(
        "        emit MandateActivated(mandateHash);\n",
        "        emit PolicyActivated(mandateHash);\n",
    ),
    "instrument_wrong_emitter": one(
        "        vm.expectEmit(true, false, false, false, address(vault));\n"
        "        emit MandateActivated(MANDATE_HASH);\n",
        "        vm.expectEmit(true, false, false, false, address(demoPay));\n"
        "        emit MandateActivated(MANDATE_HASH);\n",
        TEST,
    ),
}

def main() -> None:
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        print("\n".join(MUTANTS))
        return
    if len(sys.argv) != 3:
        raise SystemExit("usage: mutate.py CHECKOUT MUTANT | mutate.py --list")
    root = Path(sys.argv[1]).resolve()
    name = sys.argv[2]
    try:
        relative, old, new = MUTANTS[name]
    except KeyError as error:
        raise SystemExit(f"unknown mutant: {name}") from error
    path = root / relative
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{name}: expected one exact source anchor, found {count} in {relative}")
    path.write_text(text.replace(old, new, 1))
    print(f"{name}\t{relative}")


if __name__ == "__main__":
    main()
