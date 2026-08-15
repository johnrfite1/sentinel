"""EIP-712 typed-data hashing for the Sentinel DecisionReceiptPayload.

Written from EIP-712 itself. §5.4 of the proposal lists the payload's field
*names* and nothing else -- no Solidity types, no struct name for the type
string, no domain type. Everything below the field-name list is a derivation
recorded in REPORT.md, not something the spec states. See REPORT.md finding F-1.
"""

from typing import Dict, List, Tuple

from keccak import keccak256

# EIP-712 defines this domain type; §5 never names the subset of fields the
# Sentinel domain uses. domain.json supplies exactly name/version/chainId/
# verifyingContract, so this is the four-field variant with no salt.
DOMAIN_TYPE = (
    "EIP712Domain(string name,string version,uint256 chainId,"
    "address verifyingContract)"
)

# Field order follows §5.4's list verbatim. The Solidity types were recovered by
# search against the signed samples; see REPORT.md F-1.
RECEIPT_STRUCT_NAME = "DecisionReceiptPayload"
RECEIPT_FIELDS: List[Tuple[str, str]] = [
    ("uint16", "schemaVersion"),
    ("bytes32", "decisionId"),
    ("bytes32", "actionHash"),
    ("bytes32", "mandateHash"),
    ("bytes32", "policyHash"),
    ("uint8", "verdict"),
    ("bytes32", "reasonCodesHash"),
    ("bytes32", "evidenceHash"),
    ("uint256", "simulationBlockNumber"),
    ("bytes32", "simulationBlockHash"),
    ("uint64", "issuedAt"),
    ("uint64", "expiresAt"),
    ("address", "signer"),
]

RECEIPT_TYPE = (
    RECEIPT_STRUCT_NAME
    + "("
    + ",".join(f"{t} {n}" for t, n in RECEIPT_FIELDS)
    + ")"
)


# §5.1 / §5.2 / §5.3. Same situation as §5.4: names from the spec, types
# recovered by search against the samples. Recovering these turned the CLI from
# "checks the signature" into "checks the whole chain", so they are worth
# carrying even though nothing in §5 says the receipt's mandateHash/policyHash/
# actionHash are hashStruct values. See REPORT.md F-2.
MANDATE_STRUCT_NAME = "MandatePayload"
MANDATE_FIELDS: List[Tuple[str, str]] = [
    ("uint16", "schemaVersion"),
    ("bytes32", "mandateId"),
    ("address", "principal"),
    ("address", "vault"),
    ("uint256", "chainId"),
    ("address", "target"),
    ("bytes32", "targetCodeHash"),
    ("bytes4", "selector"),
    ("uint256", "maxNativeValueWei"),
    ("bytes32", "purposeKind"),
    ("bytes32", "resourceId"),
    ("address", "beneficiary"),
    ("uint64", "durationSeconds"),
    ("bool", "recurringAllowed"),
    ("uint64", "validAfter"),
    ("uint64", "validUntil"),
    ("bytes32", "policyHash"),
]

POLICY_STRUCT_NAME = "PolicyPayload"
POLICY_FIELDS: List[Tuple[str, str]] = [
    ("uint16", "schemaVersion"),
    ("uint32", "policyVersion"),
    ("address", "vault"),
    ("uint256", "chainId"),
    ("uint8", "allowedOperation"),
    ("bytes32", "allowedTargetsHash"),
    ("bytes32", "allowedSelectorsHash"),
    ("uint256", "maxNativeValueWei"),
    ("uint256", "maxAllowanceIncreaseBaseUnits"),
    ("bytes32", "allowedCallGraphHash"),
    ("uint64", "validAfter"),
    ("uint64", "validUntil"),
    ("uint8", "failureMode"),
]

ACTION_STRUCT_NAME = "ActionPayload"
ACTION_FIELDS: List[Tuple[str, str]] = [
    ("uint16", "schemaVersion"),
    ("uint256", "chainId"),
    ("address", "vault"),
    ("uint256", "actionNonce"),
    ("address", "target"),
    ("uint256", "valueWei"),
    ("bytes32", "dataHash"),
    ("uint8", "operation"),
    ("bytes32", "mandateHash"),
    ("bytes32", "policyHash"),
    ("uint64", "deadline"),
]


class EncodingError(ValueError):
    pass


def _bits(solidity_type: str) -> int:
    return int(solidity_type[4:]) if solidity_type != "uint" else 256


def encode_value(solidity_type: str, value) -> bytes:
    """abi.encode a single EIP-712 atomic value into one 32-byte word."""
    if solidity_type.startswith("bytes") and solidity_type[5:].isdigit():
        width = int(solidity_type[5:])
        raw = bytes.fromhex(_strip0x(value))
        if len(raw) != width:
            raise EncodingError(
                f"{solidity_type} value is {len(raw)} bytes: {value!r}"
            )
        # bytesN is right-padded (EIP-712 / ABI), unlike uintN and address.
        return raw.ljust(32, b"\x00")
    if solidity_type == "address":
        raw = bytes.fromhex(_strip0x(value))
        if len(raw) != 20:
            raise EncodingError(f"address value is {len(raw)} bytes: {value!r}")
        return bytes(12) + raw
    if solidity_type == "string":
        text = value if isinstance(value, str) else str(value)
        return keccak256(text.encode("utf-8"))
    if solidity_type == "bool":
        return (1 if value in (True, "true", 1, "1") else 0).to_bytes(32, "big")
    if solidity_type.startswith("uint"):
        number = int(value)  # sample payloads carry every integer as a string
        if number < 0:
            raise EncodingError(f"{solidity_type} value is negative: {value!r}")
        width = _bits(solidity_type)
        if number >= 1 << width:
            raise EncodingError(
                f"value {number} does not fit in {solidity_type}"
            )
        return number.to_bytes(32, "big")
    raise EncodingError(f"unsupported EIP-712 atomic type {solidity_type!r}")


def _strip0x(value: str) -> str:
    if not isinstance(value, str):
        raise EncodingError(f"expected a hex string, got {type(value).__name__}")
    return value[2:] if value.startswith(("0x", "0X")) else value


def type_hash(type_string: str) -> bytes:
    return keccak256(type_string.encode("utf-8"))


def domain_separator(domain: Dict) -> bytes:
    return keccak256(
        type_hash(DOMAIN_TYPE)
        + encode_value("string", domain["name"])
        + encode_value("string", domain["version"])
        + encode_value("uint256", domain["chainId"])
        + encode_value("address", domain["verifyingContract"])
    )


def struct_hash(struct_name: str, fields: List[Tuple[str, str]], payload: Dict,
                strict: bool = True, ignore: Tuple[str, ...] = ()) -> bytes:
    """EIP-712 hashStruct: keccak256(typeHash || abi.encode(field values))."""
    type_string = struct_name + "(" + ",".join(f"{t} {n}" for t, n in fields) + ")"
    parts = [type_hash(type_string)]
    for solidity_type, name in fields:
        if name not in payload:
            raise EncodingError(f"{struct_name} is missing required field {name!r}")
        parts.append(encode_value(solidity_type, payload[name]))
    if strict:
        known = {n for _, n in fields} | set(ignore)
        extra = [k for k in payload if k not in known]
        if extra:
            raise EncodingError(
                f"{struct_name} carries fields not in its §5 payload list: "
                f"{sorted(extra)}; refusing to hash an under-determined struct"
            )
    return keccak256(b"".join(parts))


def receipt_struct_hash(receipt: Dict) -> bytes:
    return struct_hash(RECEIPT_STRUCT_NAME, RECEIPT_FIELDS, receipt)


def mandate_hash(mandate: Dict) -> bytes:
    return struct_hash(MANDATE_STRUCT_NAME, MANDATE_FIELDS, mandate)


def policy_hash(policy: Dict) -> bytes:
    return struct_hash(POLICY_STRUCT_NAME, POLICY_FIELDS, policy)


def action_hash(action: Dict) -> bytes:
    # §5.3: "The complete calldata accompanies the payload." It rides alongside
    # the struct rather than inside it, so callData is excluded from the hash
    # and committed to indirectly through dataHash.
    return struct_hash(ACTION_STRUCT_NAME, ACTION_FIELDS, action,
                       ignore=("callData",))


def receipt_digest(domain: Dict, receipt: Dict) -> bytes:
    """The EIP-712 digest that the Sentinel signer signs."""
    return keccak256(
        b"\x19\x01" + domain_separator(domain) + receipt_struct_hash(receipt)
    )
