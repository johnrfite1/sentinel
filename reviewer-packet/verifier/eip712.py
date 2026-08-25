"""EIP-712 typed-data hashing for the Sentinel DecisionReceiptPayload.

Written from EIP-712 itself. §5.4 of the proposal lists the payload's field
*names* and nothing else -- no Solidity types, no struct name for the type
string, no domain type. Everything below the field-name list is a derivation
recorded in REPORT.md, not something the spec states. See REPORT.md finding F-1.
"""

import re
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


# §5.5 / §5.8. Unlike everything above, this one was NOT recovered by search --
# it is transcribed from the §5.8 published type string, which is the point of
# D-023: checking the published spec is sufficient to build from. It was, on the
# first attempt, with no search required. See REPORT.md F-2 resolution.
OVERRIDE_STRUCT_NAME = "OverrideAuthorizationPayload"
OVERRIDE_FIELDS: List[Tuple[str, str]] = [
    ("uint16", "schemaVersion"),
    ("bytes32", "reviewReceiptHash"),
    ("bytes32", "actionHash"),
    ("bytes32", "mandateHash"),
    ("bytes32", "policyHash"),
    ("uint256", "actionNonce"),
    ("bytes32", "reasonHash"),
    ("uint64", "issuedAt"),
    ("uint64", "expiresAt"),
]


class EncodingError(ValueError):
    pass


def _bits(solidity_type: str) -> int:
    return int(solidity_type[4:]) if solidity_type != "uint" else 256


# --------------------------------------------------------------------------
# Strict scalar parsing
# --------------------------------------------------------------------------
# §5 never states how a payload field is encoded *in JSON* -- see REPORT.md
# F-17. Every scalar in every shipped payload is one of exactly three shapes: a
# `0x`-prefixed even-length hex string, a canonical decimal string, or a native
# JSON `true`/`false`. This parser accepts those and nothing else.
#
# The reason is not tidiness. `mandateHash`, `policyHash` and `actionHash` are
# recomputed from these documents and compared against the receipt, so the
# document -> 32-byte-word map must be INJECTIVE or "the recomputed hash
# matches" stops pinning the document it was recomputed from. Before this,
# `"120"`, `" 120 "`, `"1_20"`, `"0120"`, `120` and `120.9` all encoded to the
# same word, and `bool` mapped every unrecognised string -- `"True"`, `"yes"`,
# `"1 "` -- to false. Six byte-distinct mandates could share one mandateHash,
# and the one an operator read was not necessarily the one the signer signed.
# Reject rather than coerce: a producer using another encoding gets a clean
# failure instead of a silent collision.
_CANONICAL_DECIMAL = re.compile(r"(?:0|[1-9][0-9]*)")
_HEX_BODY = re.compile(r"(?:[0-9a-fA-F]{2})*")


def parse_uint(solidity_type: str, value) -> int:
    """Parse a canonical decimal string into a non-negative integer."""
    if isinstance(value, bool) or not isinstance(value, str):
        raise EncodingError(
            f"{solidity_type} value must be a canonical decimal string, got "
            f"{type(value).__name__} {value!r}; a JSON number, boolean or null "
            "is refused rather than coerced"
        )
    # fullmatch, not ^...$ -- the §5.4/D-022 anchoring lesson applies here too:
    # `$` would accept a trailing newline and `"5\n"` would parse as 5.
    if not _CANONICAL_DECIMAL.fullmatch(value):
        raise EncodingError(
            f"{solidity_type} value {value!r} is not a canonical decimal "
            "string; a sign, whitespace, underscores, leading zeros, a "
            "fraction or an exponent are all refused rather than coerced"
        )
    return int(value)


def hex_to_bytes(value, label: str = "value") -> bytes:
    """Parse a strict `0x`-prefixed, even-length hex string into bytes."""
    if not isinstance(value, str):
        raise EncodingError(
            f"{label} must be a 0x-prefixed hex string, got "
            f"{type(value).__name__} {value!r}"
        )
    if not value.startswith("0x"):
        raise EncodingError(f"{label} {value!r} is missing its 0x prefix")
    if not _HEX_BODY.fullmatch(value[2:]):
        raise EncodingError(
            f"{label} {value!r} is not an even-length run of hex digits; "
            "whitespace and separators are refused rather than stripped "
            "(bytes.fromhex accepts them, so '0xde ad' and '0xdead' used to "
            "produce the same word)"
        )
    return bytes.fromhex(value[2:])


def encode_value(solidity_type: str, value) -> bytes:
    """abi.encode a single EIP-712 atomic value into one 32-byte word."""
    if solidity_type.startswith("bytes") and solidity_type[5:].isdigit():
        width = int(solidity_type[5:])
        raw = hex_to_bytes(value, f"{solidity_type} value")
        if len(raw) != width:
            raise EncodingError(
                f"{solidity_type} value is {len(raw)} bytes: {value!r}"
            )
        # bytesN is right-padded (EIP-712 / ABI), unlike uintN and address.
        return raw.ljust(32, b"\x00")
    if solidity_type == "address":
        raw = hex_to_bytes(value, "address value")
        if len(raw) != 20:
            raise EncodingError(f"address value is {len(raw)} bytes: {value!r}")
        return bytes(12) + raw
    if solidity_type == "string":
        if not isinstance(value, str):
            raise EncodingError(
                f"string value must be a JSON string, got "
                f"{type(value).__name__} {value!r}"
            )
        return keccak256(value.encode("utf-8"))
    if solidity_type == "bool":
        # Only a native JSON true/false. A string is refused: the old rule
        # (`value in (True, "true", 1, "1")`) silently read "True", "TRUE" and
        # "yes" as FALSE, which is the worst available failure for a field
        # named recurringAllowed.
        if not isinstance(value, bool):
            raise EncodingError(
                f"bool value must be a JSON true/false literal, got "
                f"{type(value).__name__} {value!r}; strings are refused rather "
                "than coerced"
            )
        return (1 if value else 0).to_bytes(32, "big")
    if solidity_type.startswith("uint"):
        number = parse_uint(solidity_type, value)
        width = _bits(solidity_type)
        if number >= 1 << width:
            raise EncodingError(
                f"value {number} does not fit in {solidity_type}"
            )
        return number.to_bytes(32, "big")
    raise EncodingError(f"unsupported EIP-712 atomic type {solidity_type!r}")


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


def override_hash(override: Dict) -> bytes:
    return struct_hash(OVERRIDE_STRUCT_NAME, OVERRIDE_FIELDS, override)


def override_digest(domain: Dict, override: Dict) -> bytes:
    """The EIP-712 digest the OWNER signs for an override authorization."""
    return keccak256(
        b"\x19\x01" + domain_separator(domain) + override_hash(override)
    )


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
