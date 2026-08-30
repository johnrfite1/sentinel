"""Independent authentication for Sentinel deployment identity manifests.

The verifier never learns its authority from the material being verified.  The
expected authority address is supplied out of band by the caller; this module
only verifies that address signed the exact canonical deployment payload.
"""

from typing import Dict

import jcs
from keccak import keccak256
from secp256k1 import RecoveryError, recover_address

SCHEMA = "sentinel.deployment-manifest.v1"
DIGEST_TAG = b"sentinel.deployment-manifest.v1\n"
FIELDS = frozenset({
    "schemaVersion", "chainId", "vault", "owner", "signer",
    "deploymentBlockNumber", "deploymentBlockHash", "runtimeCodeHash",
    "compilerMetadataHash", "sourceArchiveHash", "issuedAt",
})


class DeploymentManifestError(ValueError):
    pass


def _address(value, label):
    if not isinstance(value, str) or len(value) != 42 or not value.startswith("0x"):
        raise DeploymentManifestError(f"{label} must be a 20-byte 0x address")
    try:
        bytes.fromhex(value[2:])
    except ValueError as exc:
        raise DeploymentManifestError(f"{label} is not hexadecimal") from exc
    return value.lower()


def _bytes32(value, label):
    if not isinstance(value, str) or len(value) != 66 or not value.startswith("0x"):
        raise DeploymentManifestError(f"{label} must be a 32-byte 0x value")
    try:
        bytes.fromhex(value[2:])
    except ValueError as exc:
        raise DeploymentManifestError(f"{label} is not hexadecimal") from exc
    return value.lower()


def _uint(value, label):
    if not isinstance(value, str) or not value.isascii() or not value.isdecimal():
        raise DeploymentManifestError(f"{label} must be a canonical decimal string")
    if value != "0" and value.startswith("0"):
        raise DeploymentManifestError(f"{label} has a leading zero")
    return int(value)


def validate_payload(payload: Dict) -> Dict:
    if not isinstance(payload, dict):
        raise DeploymentManifestError("manifest payload must be an object")
    missing = FIELDS - set(payload)
    extra = set(payload) - FIELDS
    if missing or extra:
        raise DeploymentManifestError(
            f"manifest fields differ: missing={sorted(missing)} extra={sorted(extra)}"
        )
    if payload["schemaVersion"] != "1":
        raise DeploymentManifestError("unsupported deployment manifest schemaVersion")
    for name in ("chainId", "deploymentBlockNumber", "issuedAt"):
        _uint(payload[name], name)
    for name in ("vault", "owner", "signer"):
        _address(payload[name], name)
    for name in (
        "deploymentBlockHash", "runtimeCodeHash", "compilerMetadataHash", "sourceArchiveHash"
    ):
        _bytes32(payload[name], name)
    return payload


def digest(payload: Dict) -> bytes:
    validate_payload(payload)
    return keccak256(DIGEST_TAG + jcs.canonicalize(payload))


def verify(document: Dict, expected_authority: str) -> Dict:
    if not isinstance(document, dict) or set(document) != {"schema", "payload", "authoritySignature"}:
        raise DeploymentManifestError(
            "manifest must contain exactly schema, payload, and authoritySignature"
        )
    if document["schema"] != SCHEMA:
        raise DeploymentManifestError(f"unsupported manifest schema {document['schema']!r}")
    authority = _address(expected_authority, "out-of-band deployment authority")
    try:
        recovered = recover_address(digest(document["payload"]), document["authoritySignature"])
    except (RecoveryError, ValueError) as exc:
        raise DeploymentManifestError(f"deployment authority signature is invalid: {exc}") from exc
    if recovered != authority:
        raise DeploymentManifestError(
            f"deployment manifest recovered {recovered}, expected out-of-band authority {authority}"
        )
    return validate_payload(document["payload"])
