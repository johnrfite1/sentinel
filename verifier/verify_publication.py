#!/usr/bin/env python3
"""Fail-closed verifier for the Sentinel v0.3 publication bundle.

Unlike the legacy review-packet verifier, the presenter cannot choose either
the deployment identity or the receipt clock.  The caller supplies an
out-of-band deployment authority; that authority signs the deployment
manifest.  The manifest then supplies the chain, vault, owner, and signer that
all EIP-712 artifacts must match.
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import deployment
import eip712
import jcs
from keccak import keccak256
from secp256k1 import RecoveryError, recover_address


class VerificationError(ValueError):
    pass


def read_bytes(path):
    with open(path, "rb") as handle:
        return handle.read()


def read_json(path):
    return jcs.parse_bytes(read_bytes(path))


def required(sample, name):
    path = os.path.join(sample, name)
    if not os.path.isfile(path):
        raise VerificationError(f"missing required artifact {name}")
    return path


def hx(raw):
    return "0x" + raw.hex()


def eq(label, actual, expected):
    if str(actual).lower() != str(expected).lower():
        raise VerificationError(f"{label}: {actual!r} != {expected!r}")


def verify(sample, manifest_path, authority, evaluation_time=None):
    sample = os.path.abspath(sample)
    manifest = deployment.verify(read_json(manifest_path), authority)
    now = int(time.time()) if evaluation_time is None else int(evaluation_time)

    mandate = read_json(required(sample, "mandate.json"))
    policy = read_json(required(sample, "policy.json"))
    action = read_json(required(sample, "action.json"))
    receipt_doc = read_json(required(sample, "receipt.json"))
    mandate_sig = read_json(required(sample, "mandate-signature.json"))
    evidence_raw = read_bytes(required(sample, "evidence.json"))
    canonical_file = read_bytes(required(sample, "evidence.canonical.json"))
    evidence_hash_file = read_bytes(required(sample, "evidence.hash")).decode().strip().lower()
    receipt = receipt_doc.get("receipt")
    receipt_signature = receipt_doc.get("signature")
    if not isinstance(receipt, dict) or not isinstance(receipt_signature, str):
        raise VerificationError("receipt.json must carry a signed decision receipt")

    domain = {
        "name": "Sentinel",
        "version": "0.3",
        "chainId": manifest["chainId"],
        "verifyingContract": manifest["vault"],
    }

    canonical = jcs.canonicalize(jcs.parse_bytes(evidence_raw))
    if canonical != canonical_file:
        raise VerificationError("evidence canonicalization mismatch")
    evidence_hash = hx(keccak256(canonical))
    eq("evidence.hash", evidence_hash_file, evidence_hash)

    mandate_hash = hx(eip712.mandate_hash(mandate))
    policy_hash = hx(eip712.policy_hash(policy))
    action_hash = hx(eip712.action_hash(action))
    eq("action.mandateHash", action["mandateHash"], mandate_hash)
    eq("action.policyHash", action["policyHash"], policy_hash)
    eq("receipt.actionHash", receipt["actionHash"], action_hash)
    eq("receipt.mandateHash", receipt["mandateHash"], mandate_hash)
    eq("receipt.policyHash", receipt["policyHash"], policy_hash)
    eq("receipt.evidenceHash", receipt["evidenceHash"], evidence_hash)

    for label, doc in (("mandate", mandate), ("policy", policy), ("action", action)):
        eq(f"{label}.chainId", doc["chainId"], manifest["chainId"])
        eq(f"{label}.vault", doc["vault"], manifest["vault"])
    eq("mandate.principal", mandate["principal"], manifest["owner"])
    eq("mandate.signer", mandate["signer"], manifest["signer"])
    eq("receipt.signer", receipt["signer"], manifest["signer"])
    eq("mandate.policyHash", mandate["policyHash"], policy_hash)

    calldata = action.get("callData")
    if not isinstance(calldata, str):
        raise VerificationError("action.callData is required for exact-call verification")
    eq("action.dataHash", action["dataHash"], hx(keccak256(eip712.hex_to_bytes(calldata))))

    if set(mandate_sig) != {"ownerAddress", "ownerSignature"}:
        raise VerificationError("mandate-signature.json has an unexpected shape")
    eq("mandate signature owner", mandate_sig["ownerAddress"], manifest["owner"])
    try:
        mandate_owner = recover_address(
            eip712.mandate_digest(domain, mandate), mandate_sig["ownerSignature"]
        )
        receipt_signer = recover_address(
            eip712.receipt_digest(domain, receipt), receipt_signature
        )
    except (RecoveryError, eip712.EncodingError, ValueError) as exc:
        raise VerificationError(f"signature verification failed: {exc}") from exc
    eq("recovered mandate owner", mandate_owner, manifest["owner"])
    eq("recovered receipt signer", receipt_signer, manifest["signer"])

    valid_after = eip712.parse_uint("uint64", mandate["validAfter"])
    valid_until = eip712.parse_uint("uint64", mandate["validUntil"])
    issued_at = eip712.parse_uint("uint64", receipt["issuedAt"])
    expires_at = eip712.parse_uint("uint64", receipt["expiresAt"])
    deadline = eip712.parse_uint("uint64", action["deadline"])
    if not valid_after <= now < valid_until:
        raise VerificationError(f"mandate is not current at evaluationTime {now}")
    if not issued_at <= now < expires_at:
        raise VerificationError(
            f"receipt requires issuedAt <= evaluationTime < expiresAt; got {issued_at} <= {now} < {expires_at}"
        )
    if now > deadline:
        raise VerificationError("action deadline has passed")
    if eip712.parse_uint("uint256", action["actionNonce"]) < 0:
        raise VerificationError("invalid action nonce")

    return {
        "deploymentAuthority": authority.lower(),
        "deploymentBlockNumber": manifest["deploymentBlockNumber"],
        "runtimeCodeHash": manifest["runtimeCodeHash"],
        "mandateHash": mandate_hash,
        "actionHash": action_hash,
        "actionNonce": action["actionNonce"],
        "evaluationTime": str(now),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sample", help="publication evidence-bundle directory")
    parser.add_argument("--deployment-manifest", required=True)
    parser.add_argument(
        "--deployment-authority", required=True,
        help="authority address obtained independently of the publication material",
    )
    parser.add_argument("--evaluation-time", type=int, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        result = verify(
            args.sample, args.deployment_manifest, args.deployment_authority,
            evaluation_time=args.evaluation_time,
        )
    except (OSError, ValueError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: authenticated deployment, owner mandate, exact action, and current receipt")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
