"""Independent authentication for Sentinel deployment identity manifests.

The verifier never learns its authority from the material being verified.  The
expected authority address is supplied out of band by the caller; this module
only verifies that address signed the exact canonical deployment payload.

Three disciplines the pre-`a38cff9` verifier kept and this module originally
dropped are enforced here (R-A018-16):

* **(a) EIP-2 low-s.**  `verify.py` holds the receipt, the refusal record and the
  owner override to low-s with `v in {27, 28}` -- grep `signature is EIP-2
  canonical` there.  The authority signature is held to the same rule, so one
  authority decision has exactly one byte-distinct valid document and any later
  revoke-or-pin-by-digest scheme is not evadable by presenting `(r, n-s, v^1)`.
* **(b) A bounded, comparable `issuedAt`.**  `_uint` now carries a ceiling, and
  `check_lifetime` compares `issuedAt` in *both* directions against a caller-
  supplied evaluation time.  A lifetime bound that only looks backwards is
  survived by post-dating.
* **(c) Honest diagnostics.**  `validate_payload` runs *outside* the `try` that
  catches signature failures, so a field error is reported as a field error.  A
  recipient told their out-of-band authority's signature failed would go and
  re-check the authority -- the one thing that was fine.

WHAT THIS MODULE STILL DOES NOT DO, so a caller does not assume otherwise:
it reaches no chain.  `runtimeCodeHash`, `deploymentBlockHash` and
`compilerMetadataHash` are authenticated as things the deployment authority
*said*; they are compared against no deployed bytecode and no state proof.  That
binding is R-A018-04 and is not implemented here.  There is also no
authenticated revocation source -- no list, no on-chain registry, no state
proof -- so `check_lifetime` is the minimum viable, offline-observable form of
revocation: a bounded manifest lifetime, not a revocation check.
"""

from typing import Dict, Optional

import jcs
from keccak import keccak256
from secp256k1 import RecoveryError, is_low_s, parse_signature, recover_address

SCHEMA = "sentinel.deployment-manifest.v1"
DIGEST_TAG = b"sentinel.deployment-manifest.v1\n"
FIELDS = frozenset({
    "schemaVersion", "chainId", "vault", "owner", "signer",
    "deploymentBlockNumber", "deploymentBlockHash", "runtimeCodeHash",
    "compilerMetadataHash", "sourceArchiveHash", "issuedAt",
})

MAX_UINT64 = 2 ** 64 - 1
MAX_UINT256 = 2 ** 256 - 1

# Per-field ceilings.  `issuedAt` and `deploymentBlockNumber` are uint64 because
# that is what every downstream time and block comparison in this repository
# uses; `chainId` is the EIP-712 domain's uint256.  Without a ceiling `issuedAt`
# accepted 10**40 -- a timestamp roughly 10**32 years hence -- and every piece of
# arithmetic downstream inherited an unbounded integer (R-A018-16(b)).
UINT_CEILINGS = {
    "chainId": MAX_UINT256,
    "deploymentBlockNumber": MAX_UINT64,
    "issuedAt": MAX_UINT64,
}

# How old a signed deployment manifest may be before it stops authenticating.
#
# The bound is a judgement call, not a derived constant, and it is recorded as
# one.  What is NOT a judgement call is that some bound must exist: without one a
# signed manifest is valid forever, so a manifest naming a signer that has since
# been rotated away keeps certifying that signer's year-old receipts, and there
# is no path by which a recipient can learn it has been superseded (register
# §1.5).  Ninety days is short enough that a rotation is visible within a
# quarter and long enough that a release does not expire mid-review.
MAX_MANIFEST_AGE_SECONDS = 90 * 24 * 3600


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


def _uint(value, label, ceiling=MAX_UINT256):
    if not isinstance(value, str) or not value.isascii() or not value.isdecimal():
        raise DeploymentManifestError(f"{label} must be a canonical decimal string")
    if value != "0" and value.startswith("0"):
        raise DeploymentManifestError(f"{label} has a leading zero")
    parsed = int(value)
    if parsed > ceiling:
        raise DeploymentManifestError(
            f"{label} is {value}, above the maximum {ceiling} this field is bounded to"
        )
    return parsed


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
    for name, ceiling in sorted(UINT_CEILINGS.items()):
        _uint(payload[name], name, ceiling)
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


def check_lifetime(payload: Dict, evaluation_time,
                   max_age_seconds: int = MAX_MANIFEST_AGE_SECONDS) -> int:
    """Compare `issuedAt` to `evaluation_time` in both directions.

    Both directions, because they are different attacks.  Backwards: a superseded
    manifest naming a rotated-away signer stays valid forever and keeps that
    signer's old receipts certifying.  Forwards: a post-dated manifest survives
    any purely backward-looking lifetime bound, so a manifest can be minted now
    and held until its window opens.
    """
    issued_at = _uint(payload["issuedAt"], "issuedAt", MAX_UINT64)
    now = int(evaluation_time)
    if issued_at > now:
        raise DeploymentManifestError(
            f"deployment manifest issuedAt {issued_at} is in the future at evaluation time "
            f"{now}: a post-dated manifest is not yet valid"
        )
    age = now - issued_at
    if age > max_age_seconds:
        raise DeploymentManifestError(
            f"deployment manifest is stale: issuedAt {issued_at} is {age}s before evaluation "
            f"time {now}, past the {max_age_seconds}s maximum manifest age. A manifest that "
            f"never expires cannot be superseded by a signer rotation nor withdrawn by a "
            f"revocation, so an old manifest would keep certifying an old signer's receipts"
        )
    return issued_at


def _check_signature_form(signature) -> None:
    """EIP-2 canonical form, before anything is recovered from the signature.

    `(r, n-s, v^1)` recovers the same address as `(r, s, v)`, so without this a
    single authority decision has two byte-distinct valid documents and the
    manifest has no unique identity to revoke or pin by.
    """
    if not isinstance(signature, str):
        raise DeploymentManifestError("authoritySignature must be a 0x-prefixed string")
    try:
        _, s_value, v_value = parse_signature(signature)
    except (RecoveryError, ValueError) as exc:
        raise DeploymentManifestError(
            f"deployment authority signature is malformed: {exc}"
        ) from exc
    if v_value not in (27, 28):
        raise DeploymentManifestError(
            f"deployment authority signature has v={v_value}; EIP-712 signatures carry "
            f"v in {{27, 28}}"
        )
    if not is_low_s(s_value):
        raise DeploymentManifestError(
            "deployment authority signature is not EIP-2 canonical (high-s). The reflected "
            "form (r, n-s, v^1) recovers the same authority, so the manifest would be "
            "malleable: one authority decision, two byte-distinct documents, and no unique "
            "identity for a later revoke-or-pin-by-digest scheme to name"
        )


def verify(document: Dict, expected_authority: str,
           evaluation_time: Optional[int] = None) -> Dict:
    """Authenticate a signed deployment manifest against an out-of-band authority.

    `evaluation_time` is the instant the manifest's lifetime is judged at.  When
    it is `None` no lifetime comparison is made, because there is nothing to
    compare against: this module has no clock it trusts, and inventing one from
    `time.time()` would make a *fixed* manifest start failing purely with the
    passage of wall-clock time in the caller's process.  `verify_publication.py`
    -- the only caller in this repository -- always supplies one.
    """
    if not isinstance(document, dict) or set(document) != {"schema", "payload", "authoritySignature"}:
        raise DeploymentManifestError(
            "manifest must contain exactly schema, payload, and authoritySignature"
        )
    if document["schema"] != SCHEMA:
        raise DeploymentManifestError(f"unsupported manifest schema {document['schema']!r}")
    authority = _address(expected_authority, "out-of-band deployment authority")

    # R-A018-16(c): validation happens HERE, outside the try below.  It used to
    # happen inside it, by way of `digest()`, so a leading zero in `issuedAt` was
    # reported to the recipient as "deployment authority signature is invalid".
    payload = validate_payload(document["payload"])
    manifest_digest = keccak256(DIGEST_TAG + jcs.canonicalize(payload))

    _check_signature_form(document["authoritySignature"])
    try:
        recovered = recover_address(manifest_digest, document["authoritySignature"])
    except (RecoveryError, ValueError) as exc:
        raise DeploymentManifestError(f"deployment authority signature is invalid: {exc}") from exc
    if recovered != authority:
        raise DeploymentManifestError(
            f"deployment manifest recovered {recovered}, expected out-of-band authority {authority}"
        )
    if evaluation_time is not None:
        check_lifetime(payload, evaluation_time)
    return payload
