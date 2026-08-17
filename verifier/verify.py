#!/usr/bin/env python3
"""Sentinel standalone receipt verifier (ratified deliverable D-010).

Independent reimplementation. Shares no canonicalization, hashing, or signing
code with the Sentinel evaluator: RFC 8785 in jcs.py, Keccak-f[1600] in
keccak.py, secp256k1 recovery in secp256k1.py, and the §5.5.1 refusal digest in
refusal.py are all written here from the published specifications. Zero
third-party dependencies; stock Python 3.8+.

A bundle presents EITHER a §5.4 SignedDecisionReceipt or a §5.5.1
SignedRefusalRecord. Both are verified; a bundle presenting neither, or
presenting an unsigned claim that the signer refused, fails -- §5.5.1: "a
verifier must treat an absent record as an unestablished refusal rather than an
established one."

    python3 verifier/verify.py fixtures/samples/case-1-allow
    python3 verifier/verify.py --tamper fixtures/samples/case-1-allow
    python3 verifier/verify.py --all fixtures/samples

Exit status is 0 only if every check passes.
"""

import argparse
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import eip712  # noqa: E402
import jcs  # noqa: E402
import reasoncodes  # noqa: E402
import refusal  # noqa: E402
from keccak import keccak256  # noqa: E402
from secp256k1 import (  # noqa: E402
    G, RecoveryError, is_low_s, parse_signature, point_mul,
    public_key_to_address, recover_address, sign_digest,
)

# §5.4 lists `verdict` with no enumeration and no encoding. The receipts carry
# it numerically. Recovered from the samples against index.json/meta.json:
#   0 = BLOCK, 1 = REVIEW, 2 = ALLOW.
# See REPORT.md F-4: the spec never states this and §4.2 lists the cases in the
# opposite order, so ALLOW=0 is an equally defensible misreading.
VERDICT_NAMES = {0: "BLOCK", 1: "REVIEW", 2: "ALLOW"}

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"


def _color(text, code):
    return f"{code}{text}{RESET}" if sys.stdout.isatty() else text


class Check:
    def __init__(self, name, ok, detail="", skipped=False):
        self.name = name
        self.ok = ok
        self.detail = detail
        self.skipped = skipped

    def render(self):
        if self.skipped:
            tag = _color("SKIP", YELLOW)
        else:
            tag = _color("PASS", GREEN) if self.ok else _color("FAIL", RED)
        line = f"  [{tag}] {self.name}"
        if self.detail:
            line += "\n" + "\n".join(
                "         " + _color(l, DIM) for l in self.detail.splitlines()
            )
        return line


def _read_bytes(path):
    with open(path, "rb") as handle:
        return handle.read()


def _read_json(path):
    return jcs.parse_bytes(_read_bytes(path))


def _norm_hex(value):
    return value.lower() if isinstance(value, str) else value


def _find_domain(sample_dir, override):
    """Locate domain.json — the TRUST ROOT — preferring the deployment's copy.

    THE PRESENTER OF A BUNDLE MUST NOT CHOOSE THE TRUST ROOT, AND UNTIL 2026-08-17 IT COULD
    (A-055). This function searched the BUNDLE directory first and the parent second. Since
    `domain.json` carries `signerAddress` — the one thing binding a receipt to the deployment's
    signer rather than to whoever signed it — a bundle that shipped its own `domain.json` chose
    what "the signer" means for itself. Demonstrated against the UNMUTATED verifier: a receipt
    re-signed with an arbitrary outsider key, with `receipt.signer` set to that key's address and
    a `domain.json` naming it, verified `=> PASS`, exit 0. Under `--all`, one hostile directory
    inside a corpus overrode the signer identity for itself and the run still printed
    `N/N verified`. No mutation was required; this was shipped behaviour.

    Now: `--domain` wins if given, then the DEPLOYMENT's copy in the parent directory, and a
    bundle-supplied copy is used only when there is no deployment copy at all — in which case
    the caller marks the trust root as presenter-supplied and FAILS the sample, because a bundle
    plus its own idea of the signer is not something that can be certified. A bundle that ships
    a copy CONTRADICTING the deployment's is an error rather than a preference.

    Returns (path, provenance, presenter_supplied).
    """
    if override:
        return override, "supplied explicitly via --domain", False
    inside = os.path.join(sample_dir, "domain.json")
    parent = os.path.join(os.path.dirname(os.path.abspath(sample_dir)), "domain.json")
    have_inside, have_parent = os.path.isfile(inside), os.path.isfile(parent)
    if have_parent and have_inside:
        try:
            identical = _read_json(parent) == _read_json(inside)
        except Exception:
            identical = False
        if not identical:
            raise ValueError(
                "the bundle ships its own domain.json and it CONTRADICTS the deployment's "
                "copy in the parent directory. The trust root is not the presenter's to "
                "choose: `signerAddress` is what binds a receipt to the deployment's signer. "
                "Remove the bundle's copy, or pass --domain to state which root you mean."
            )
        return parent, "deployment copy (parent directory); the bundle's copy is identical", False
    if have_parent:
        return parent, "deployment copy (parent directory)", False
    if have_inside:
        return inside, "PRESENTER-SUPPLIED (the bundle's own domain.json; no deployment copy found)", True
    raise FileNotFoundError(
        "domain.json not found in the sample directory or its parent; "
        "pass --domain"
    )


TAMPER_MODES = (
    "evidence", "evidence-hash", "receipt", "receipt-wrongkey", "signature",
    "reasons-substitute", "reasons-add", "reasons-remove", "reasons-reorder",
    "override-reviewreceipt", "override-nonce", "override-wrongkey",
    "override-repoint", "override-nonce-resigned", "override-signer-mints",
    "receipt-anchor-split",
    "override-otherchain",
    # §5.5.1. Every one of these leaves a *validly signed* SignedRefusalRecord
    # behind except `refusal-signature` and `refusal-strip-signature`: the
    # record is mutated and then re-signed with the published signer key, so
    # what is being tested is the binding, not the cryptography. A refusal that
    # verifies as a signature and names another action is the whole failure
    # mode §5.5.1's attributability sentence exists to close.
    "refusal-actionhash", "refusal-evidencehash", "refusal-chainid",
    "refusal-vault", "refusal-verdict", "refusal-reasonhash",
    "refusal-signature", "refusal-strip-signature", "refusal-wrongkey",
    "refusal-otherchain", "refusal-reasons-add", "refusal-reasons-remove",
)

# Modes whose mutation must NOT break verification. A pure reorder of the
# published reasonCodes list is the control case: the committed set is sorted
# before hashing, so order in the published list carries no information. If a
# reorder were rejected, this verifier would be hashing the list as given rather
# than the set, and would reject honest receipts whose producer emitted the
# codes in evaluation order.
TAMPER_MUST_STILL_VERIFY = frozenset({"reasons-reorder"})


def verify_sample(sample_dir, domain_path=None, tamper=None):
    """Run every check against one sample directory. Returns (ok, [Check])."""
    checks = []
    sample_dir = os.path.abspath(sample_dir)

    # ---- load -----------------------------------------------------------
    evidence_raw = _read_bytes(os.path.join(sample_dir, "evidence.json"))
    canonical_expected = _read_bytes(os.path.join(sample_dir, "evidence.canonical.json"))
    hash_expected = _read_bytes(os.path.join(sample_dir, "evidence.hash")).decode().strip()
    # §5.5.1 publishes SignedRefusalRecord as an artifact in its own right, so a
    # bundle carrying one and no receipt.json is not malformed -- there is no
    # receipt to carry. With neither file this still raises, which is right:
    # the bundle presents nothing to verify.
    receipt_path = os.path.join(sample_dir, "receipt.json")
    if os.path.isfile(receipt_path) or not os.path.isfile(
            os.path.join(sample_dir, "refusal.json")):
        receipt_doc = _read_json(receipt_path)
    else:
        receipt_doc = {}
    domain_file, domain_provenance, domain_presenter_supplied = _find_domain(
        sample_dir, domain_path)
    domain = _read_json(domain_file)

    # THE TRUST ROOT IS NOW A NAMED CHECK RATHER THAN AN IMPLICIT ASSUMPTION (A-055).
    #
    # Every signer binding downstream is relative to `domain.signerAddress`, so where that file
    # came from is the precondition for all of them. It was previously invisible — and invisible
    # is how a presenter-supplied root certified an outsider-minted receipt with `=> PASS`. A
    # bundle whose only trust root is its own copy now FAILS: "here is a bundle and here is who
    # I say signed it" is not a certifiable claim, and answering it with PASS was the defect.
    checks.append(Check(
        "the trust root is the deployment's, not the presenter's",
        not domain_presenter_supplied,
        domain_provenance if not domain_presenter_supplied else (
            domain_provenance + " — pass --domain with the deployment's domain.json, or place "
            "it beside the bundle. A receipt can only be certified against a signer identity "
            "the presenter did not supply."),
    ))

    override_tamper = None
    refusal_tamper = None
    evidence = jcs.parse_bytes(evidence_raw)
    if tamper == "evidence":
        evidence = _tamper_json(evidence)
    elif tamper == "receipt-wrongkey":
        # THE MODE THE PRIMARY §5.4 ARTIFACT DID NOT HAVE (A-055). `override-wrongkey` and
        # `refusal-wrongkey` both existed; the RECEIPT — the artifact the whole verifier is
        # about — had neither, and that absence is the single reason the check binding a receipt
        # to the DEPLOYMENT's signer was asserted by nothing. A directed sweep neutered
        # `recovered == domain_signer` to `True` and every one of the then-154 tests passed.
        #
        # This is not a byte-flip. The receipt is re-signed by an OUTSIDER key and
        # `receipt.signer` is rewritten to that key's own address, so the bundle is entirely
        # SELF-CONSISTENT: `recovered == receipt.signer` passes, the signature is valid, nothing
        # is malformed. The only thing that can reject it is the binding to the deployment's
        # signer identity. That is the check this mode exists to make fail.
        receipt_doc = copy.deepcopy(receipt_doc)
        body = receipt_doc.get("receipt")
        if not body:
            raise NotApplicable(
                "receipt-wrongkey needs a §5.4 receipt body; this sample has none")
        outsider_addr = public_key_to_address(point_mul(_OUTSIDER_TEST_KEY, G))
        body["signer"] = outsider_addr
        receipt_doc["signature"] = sign_digest(
            eip712.receipt_digest(domain, body), _OUTSIDER_TEST_KEY)
    elif tamper == "receipt-anchor-split":
        # The receipt's anchor is `simulationBlockNumber` + `simulationBlockHash`, and the
        # SUITE HAS NO ANCHOR TEST AT ALL (A-056). Splitting the pair inside the signed body
        # and RE-SIGNING with the deployment key leaves a valid, correctly-attributed receipt
        # whose anchor names a block that is not the one the evidence was gathered at.
        receipt_doc = copy.deepcopy(receipt_doc)
        body = receipt_doc.get("receipt")
        if not body:
            raise NotApplicable(
                "receipt-anchor-split needs a §5.4 receipt body; this sample has none")
        h = body["simulationBlockHash"]
        body["simulationBlockHash"] = "0x" + ("%02x" % (int(h[2:4], 16) ^ 0xFF)) + h[4:]
        receipt_doc["signature"] = sign_digest(
            eip712.receipt_digest(domain, body), _SENTINEL_SIGNER_TEST_KEY)
    elif tamper == "evidence-hash":
        # Corrupt the PUBLISHED hash instead of the bytes, so that exactly one check
        # can catch it: "keccak256(canonical bytes) matches evidence.hash".
        #
        # WHY THIS MODE EXISTS (A-049). An adversarial review neutered that check by
        # hand -- `ok = True or evidence_hash == expected_hash` -- and all 146 tests
        # passed and all 7 samples verified. No mode mutated `evidence.hash`; the
        # field was only ever READ. The `evidence` mode above changes the canonical
        # BYTES, which other checks also notice, so it never isolated this one.
        # A named check that no mode targets is a check nothing asserts.
        #
        # THAT SENTENCE IS FALSE AS A GENERAL RULE AND IS RETIRED (A-055). It held for THIS
        # check and became load-bearing across three entries on that strength. A directed sweep
        # measured it in both directions and refuted it: of 33 checks no tamper mode ever makes
        # fail, 18 were probed and 10 were CAUGHT by the unit suite — not being targeted by a
        # mode says nothing. And of checks that DO fail under some mode, 10 were neutered and 5
        # SURVIVED, because their mode is caught by a different check failing alongside, so the
        # tamper matrix scores them covered while nothing asserts them. **That direction is the
        # dangerous one, and it means the tamper matrix is not a coverage measure. Mutation is.**
        # The mode below is still worth having; the general inference that motivated it is not.
        _h = _norm_hex(hash_expected)
        _h = _h[2:] if _h.startswith("0x") else _h
        # Flip the leading nibble to a value it cannot already hold, so the mutation
        # is guaranteed to change the string rather than depending on its content.
        hash_expected = "0x" + ("1" if _h[:1] == "0" else "0") + _h[1:]
    elif tamper == "receipt":
        receipt_doc = copy.deepcopy(receipt_doc)
        if not receipt_doc.get("receipt"):
            # A mode that mutates nothing is not a passing self-test, it is a
            # vacuous one -- and it reported PASS until a §5.5.1 refusal bundle
            # (which has no receipt body) arrived in the corpus to expose it.
            raise NotApplicable(
                "receipt needs a §5.4 receipt body; this sample has none")
        # Flip the low bit of issuedAt: still a well-typed uint64, so the
        # struct still encodes -- only the digest, and so the recovered
        # address, changes.
        body = receipt_doc["receipt"]
        body["issuedAt"] = str(int(body["issuedAt"]) ^ 1)
    elif tamper == "signature":
        receipt_doc = copy.deepcopy(receipt_doc)
        if not receipt_doc.get("signature"):
            raise NotApplicable(
                "signature needs a §5.4 receipt signature; this sample has none")
        sig = receipt_doc["signature"]
        flipped = "%02x" % (int(sig[2:4], 16) ^ 0x01)
        receipt_doc["signature"] = "0x" + flipped + sig[4:]
    elif tamper and tamper.startswith("override-"):
        if not os.path.isfile(os.path.join(sample_dir, "override.json")):
            raise NotApplicable(
                f"{tamper} needs an override.json; this sample has none"
            )
        override_tamper = tamper
    elif tamper and tamper.startswith("refusal-"):
        # Applicability cannot be decided from a filename: §5.5.1 does not say
        # which file carries the record. Decided below, once it is located.
        refusal_tamper = tamper
    elif tamper and tamper.startswith("reasons-"):
        receipt_doc, applied = _tamper_reasons(receipt_doc, tamper)
        if not applied:
            raise NotApplicable(
                f"{tamper} cannot be applied to a sample with "
                f"{len(receipt_doc.get('reasonCodes') or [])} reason code(s)"
            )
    elif tamper is not None:
        raise ValueError(f"unknown tamper mode {tamper!r}")

    # ---- 1. recanonicalize ---------------------------------------------
    try:
        canonical_actual = jcs.canonicalize(evidence)
    except jcs.CanonicalizationError as exc:
        # RFC 8785 requires termination on input it cannot canonicalize (an
        # unpaired surrogate, for one). Terminating is right; crashing out of
        # the middle of verify_sample is not. Report it as the failed check it
        # is, and stop: with no canonical bytes there is no evidenceHash, and
        # every check downstream of it would be answering nothing.
        checks.append(Check(
            "RFC 8785 recanonicalization matches evidence.canonical.json",
            False,
            f"{exc}\nthe bundle cannot be canonicalized, so evidenceHash "
            "cannot be recomputed and nothing bound to it can be checked",
        ))
        return False, checks
    ok = canonical_actual == canonical_expected
    detail = ""
    if not ok:
        detail = _byte_diff(canonical_actual, canonical_expected)
    else:
        detail = f"{len(canonical_actual)} bytes, byte-identical, no trailing newline"
        if canonical_expected.endswith(b"\n"):
            detail = f"{len(canonical_actual)} bytes, byte-identical"
    checks.append(Check("RFC 8785 recanonicalization matches evidence.canonical.json", ok, detail))

    # ---- 2. keccak256 of the canonical bytes ----------------------------
    # Hash what we recomputed, not what was handed to us: hashing the supplied
    # canonical file would let a mismatch in check 1 pass unnoticed here.
    evidence_hash = "0x" + keccak256(canonical_actual).hex()
    expected_hash = _norm_hex(hash_expected)
    if not expected_hash.startswith("0x"):
        expected_hash = "0x" + expected_hash
    ok = evidence_hash == expected_hash
    checks.append(Check(
        "keccak256(canonical bytes) matches evidence.hash",
        ok,
        f"computed {evidence_hash}" + ("" if ok else f"\nfile     {expected_hash}"),
    ))

    refused = bool(receipt_doc.get("refused"))
    receipt = receipt_doc.get("receipt")
    signature = receipt_doc.get("signature")

    # ---- 2a. §5.5.1 SignedRefusalRecord ---------------------------------
    # Located BEFORE the receipt branch, because a bundle presenting a signed
    # refusal is a different artifact from a bundle presenting nothing, and
    # only §5.5.1 tells the two apart. Locating is separate from verifying:
    # `_locate_refusal` reports how the record was presented, and every claim
    # it makes is then checked in `_refusal_checks`.
    located, locate_errors = _locate_refusal(sample_dir, receipt_doc)
    if locate_errors:
        checks.append(Check(
            "the bundle presents at most one §5.5.1 SignedRefusalRecord, in a "
            "recognisable shape",
            False, "\n".join(locate_errors)))
        return False, checks
    if refusal_tamper and not located:
        raise NotApplicable(
            f"{refusal_tamper} needs a §5.5.1 SignedRefusalRecord; this "
            "sample presents a §5.4 receipt")
    if located:
        record = located[0]
        if refusal_tamper:
            record, domain = _tamper_refusal(record, domain, refusal_tamper)
        checks.extend(_refusal_checks(
            sample_dir, record, receipt_doc, evidence, evidence_hash, domain))
        return all(c.ok for c in checks), checks

    if refused or receipt is None or signature is None:
        checks.extend(_unauthenticated_receipt_checks(
            receipt_doc, evidence, refused, receipt, signature))
        return all(c.ok for c in checks), checks

    # ---- 3. receipt binds the evidence ----------------------------------
    receipt_evidence_hash = _norm_hex(receipt.get("evidenceHash", ""))
    ok = receipt_evidence_hash == evidence_hash
    checks.append(Check(
        "receipt.evidenceHash binds the recomputed evidence",
        ok,
        "" if ok else f"receipt   {receipt_evidence_hash}\ncomputed  {evidence_hash}",
    ))

    # ---- 4. EIP-712 digest and signer recovery --------------------------
    try:
        separator = eip712.domain_separator(domain)
        struct_hash = eip712.receipt_struct_hash(receipt)
        digest = eip712.receipt_digest(domain, receipt)
        recovered = recover_address(digest, signature)
        recover_error = None
    except (eip712.EncodingError, RecoveryError, ValueError) as exc:
        separator = struct_hash = digest = None
        recovered = None
        recover_error = str(exc)

    if recover_error:
        checks.append(Check("EIP-712 digest recomputation", False, recover_error))
        checks.append(Check("signature recovers the declared signer", False, recover_error))
    else:
        checks.append(Check(
            "EIP-712 digest recomputed from §5.4 field list",
            True,
            f"domainSeparator 0x{separator.hex()}\n"
            f"structHash      0x{struct_hash.hex()}\n"
            f"digest          0x{digest.hex()}",
        ))

        declared = _norm_hex(receipt.get("signer", ""))
        ok = recovered == declared
        checks.append(Check(
            "recovered signer == receipt.signer",
            ok,
            f"recovered {recovered}" + ("" if ok else f"\ndeclared  {declared}"),
        ))

        domain_signer = _norm_hex(domain.get("signerAddress", ""))
        ok = recovered == domain_signer
        checks.append(Check(
            "recovered signer == domain.json signerAddress",
            ok,
            "" if ok else f"recovered {recovered}\ndomain    {domain_signer}",
        ))

        _, s_value, v_value = parse_signature(signature)
        checks.append(Check(
            "signature is EIP-2 canonical (low-s) and v in {27,28}",
            is_low_s(s_value) and v_value in (27, 28),
            f"v={v_value}, low-s={is_low_s(s_value)}",
        ))

    # ---- 5. verdict sanity ----------------------------------------------
    checks.append(_verdict_check(sample_dir, receipt))

    # ---- 6. the rest of the hash chain ----------------------------------
    checks.extend(_chain_checks(sample_dir, receipt, evidence, domain))

    # ---- 7. reason codes (§5.4 as amended by D-022) ----------------------
    checks.extend(_reason_code_checks(receipt_doc, receipt))

    # ---- 8. override authorization (§5.5 / §5.8, D-023) ------------------
    checks.extend(_override_checks(sample_dir, receipt, domain, override_tamper))

    return all(c.ok for c in checks), checks


def _unauthenticated_receipt_checks(receipt_doc, evidence, refused, receipt,
                                    signature):
    """Neither a signed receipt nor a §5.5.1 refusal record: nothing to certify.

    §5.4 defines `SignedDecisionReceipt` as "DecisionReceiptPayload plus
    sentinelSignature". §5.5.1 (added 2026-08-16) now defines the other half --
    `SignedRefusalRecord`, "RefusalRecord plus `signerSignature`". A bundle
    reaching this function presented neither.

    `refused`, `refusalReason` and `reason` are fixture-harness fields, not
    protocol: §5.5.1 gives the refusal a *record* and a *signature*, and a bare
    boolean is neither. So a bundle whose `receipt.json` reads
    `{"refused": true}` still carries nothing an independent party can
    authenticate. "The isolated signer refused", "the signer was never asked",
    and "somebody deleted the ALLOW receipt on the way here" are the same bytes
    -- and the third is not hypothetical: the evidence bundle sitting beside it
    may record `"verdict": "ALLOW"`.

    §5.5.1 now says this in its own words, which is what turned the previous
    conservative choice (REPORT.md F-13) into a specified requirement: "a
    verifier must treat an absent record as an unestablished refusal rather
    than an established one."

    The evidence checks above still ran and are still reported; they establish
    that the bundle is internally consistent, which is a strictly weaker claim
    than "Sentinel decided this". This function refuses to let the weaker claim
    be printed as `=> PASS`.
    """
    if refused:
        stated = receipt_doc.get("refusalReason") or receipt_doc.get("reason")
        opening = "receipt.json asserts `refused: true`"
        if stated:
            opening += f", stating: {stated!r}"
    elif receipt is None:
        opening = "receipt.json carries no `receipt` body"
    else:
        opening = "receipt.json carries a receipt body but no `signature`"

    detail = [
        opening,
        "§5.4 defines SignedDecisionReceipt as DecisionReceiptPayload plus "
        "sentinelSignature; §5.5.1 defines SignedRefusalRecord as RefusalRecord "
        "plus signerSignature. This bundle presents neither, and a bare "
        "`refused` boolean is not a §5.5.1 record.",
        "§5.5.1: \"a verifier must treat an absent record as an unestablished "
        "refusal rather than an established one\".",
        "Nothing in this bundle is authenticated, so a genuine refusal, a "
        "signer that was never asked, and a deleted receipt are "
        "indistinguishable to any third party.",
    ]
    if isinstance(evidence, dict) and evidence.get("verdict") is not None:
        detail.append(
            f"the evidence bundle beside it records verdict "
            f"{evidence['verdict']!r}; presenting that as a refusal is exactly "
            "the substitution this check exists to stop."
        )

    out = [Check("a signed receipt is present to verify (§5.4), or a signed "
                 "refusal record (§5.5.1)", False, "\n".join(detail))]
    if refused and receipt is not None:
        out.append(Check(
            "refusal shape is self-consistent",
            False,
            "refused is true but a receipt body is also present; a refusal "
            "must not carry a signed receipt",
        ))
    return out


# --------------------------------------------------------------------------
# §5.5.1 SignedRefusalRecord
# --------------------------------------------------------------------------
# §5.5.1 defines the record, its field order, its charsets and its digest. It
# does NOT define how the record is carried in an evidence bundle -- no
# filename, no JSON key, no nesting. That silence is F-18.2 in REPORT.md, and
# it is resolved here by accepting the two shapes the rest of the corpus makes
# plausible, and by refusing outright when a bundle presents two records that
# disagree. Being liberal about *where* the record sits costs nothing: every
# record found is put through the identical verification, so a location this
# verifier accepts and the signer never writes to simply never occurs, while a
# location it rejects and the signer does write to fails loudly rather than
# silently. Being liberal about *what* the record contains would cost
# everything, and `refusal.canonical_fields` is correspondingly strict.
_REFUSAL_NESTED_KEYS = ("refusal", "refusalRecord", "record")
_REFUSAL_SIGNATURE_KEYS = ("signerSignature", "signature")
# Fields that may travel beside the record without being part of it. Anything
# NOT in this list, and not a §5.5.1 field, is a hard error rather than an
# ignored extra: an unrecognised sibling key may be a field its producer
# believes is signed, and §5.5.1's preimage covers exactly nine values.
_REFUSAL_ANCILLARY_KEYS = ("refused", "refusalReason", "reason", "reasonCodes",
                           "signerFindings")


def _extract_refusal(doc, source, allow_flat, signature_keys, _depth=0):
    """Pull one (record, signature) pair out of a document. -> (found, errors)."""
    if not isinstance(doc, dict):
        return None, [f"{source}: expected a JSON object, got "
                      f"{type(doc).__name__}"]

    nested = [k for k in _REFUSAL_NESTED_KEYS if isinstance(doc.get(k), dict)]
    if len(nested) > 1:
        return None, [f"{source} carries a refusal record under more than one "
                      f"key: {nested}"]
    if nested:
        inner = doc[nested[0]]
        if _depth < 2 and not any(k in inner for k in refusal.FIELD_NAMES):
            # `doc[key]` is not the record: it is another envelope carrying the
            # record and its signature. §5.5.1 specifies neither envelope, so
            # neither depth is more correct than the other -- descend rather
            # than reject, and record the ambiguity (REPORT.md F-18.2).
            return _extract_refusal(inner, f"{source} -> {nested[0]}", True,
                                    _REFUSAL_SIGNATURE_KEYS, _depth + 1)
        record = inner
    elif allow_flat and any(k in doc for k in refusal.FIELD_NAMES):
        # §5.5.1 says "SignedRefusalRecord contains RefusalRecord plus
        # signerSignature", which reads equally well as a nested object and as
        # nine fields with a signature beside them. Both are accepted.
        record = {k: doc[k] for k in refusal.FIELD_NAMES if k in doc}
        leftover = sorted(k for k in doc
                          if k not in refusal.FIELD_NAMES
                          and k not in signature_keys
                          and k not in _REFUSAL_ANCILLARY_KEYS)
        if leftover:
            return None, [
                f"{source} presents a flat RefusalRecord alongside "
                f"unrecognised key(s) {leftover}; §5.5.1's preimage commits to "
                "exactly nine fields, so these are unauthenticated and the "
                "shape is refused rather than silently narrowed"]
    else:
        return None, []

    present = [k for k in signature_keys if doc.get(k) is not None]
    values = [doc[k] for k in present]
    if len(values) > 1 and any(v != values[0] for v in values[1:]):
        return None, [f"{source} carries two different signatures, under "
                      f"{present}; §5.5.1 names exactly one, `signerSignature`"]
    return ({"source": source, "record": record, "doc": doc,
             "signature": values[0] if values else None}, [])


def _locate_refusal(sample_dir, receipt_doc):
    """Find the SignedRefusalRecord, if the bundle presents one at all."""
    located, errors = [], []

    path = os.path.join(sample_dir, "refusal.json")
    if os.path.isfile(path):
        found, errs = _extract_refusal(
            _read_json(path), "refusal.json", True, _REFUSAL_SIGNATURE_KEYS)
        errors.extend(errs)
        if found is not None:
            located.append(found)
        elif not errs:
            errors.append(
                "refusal.json is present but carries no §5.5.1 RefusalRecord, "
                "under any of the shapes this verifier recognises "
                f"({', '.join(_REFUSAL_NESTED_KEYS)}, or the nine fields flat)")

    # Only the §5.5.1 name is accepted inside receipt.json: `signature` there
    # already means the receipt's own sentinelSignature, and reading it as the
    # refusal's would let one signature be presented as attesting two different
    # documents.
    found, errs = _extract_refusal(
        receipt_doc, "receipt.json", False, ("signerSignature",))
    errors.extend(errs)
    if found is not None:
        located.append(found)

    if len(located) > 1:
        first, second = located[0], located[1]
        if (first["record"] != second["record"]
                or first["signature"] != second["signature"]):
            errors.append(
                f"the bundle presents two DIFFERENT refusal records, in "
                f"{first['source']} and {second['source']}. §5.5.1 does not "
                "say where the record lives, so a verifier cannot choose "
                "between two answers to \"what did the signer refuse\"; both "
                "are rejected.")
    return located, errors


def _refusal_label_check(sample_dir):
    """Cross-check the fixture label, the way _verdict_check does for a receipt."""
    expected = None
    meta_path = os.path.join(sample_dir, "meta.json")
    if os.path.isfile(meta_path):
        expected = _read_json(meta_path).get("signerRefused")
    if expected is None:
        index_path = os.path.join(os.path.dirname(sample_dir), "index.json")
        if os.path.isfile(index_path):
            for entry in _read_json(index_path):
                if entry.get("id") == os.path.basename(sample_dir):
                    expected = entry.get("signerRefused")
    if expected is None:
        return Check("the case label records a signer refusal", True,
                     "no meta.json/index.json to cross-check against",
                     skipped=True)
    return Check(
        "the case label records a signer refusal", expected is True,
        "" if expected is True else
        f"the case label says signerRefused: {expected!r}, but the bundle "
        "presents a §5.5.1 SignedRefusalRecord")


def _refusal_checks(sample_dir, located, receipt_doc, evidence, evidence_hash,
                    domain):
    """Verify a §5.5.1 SignedRefusalRecord end to end.

    The order matters. Shape and charset first, because §5.5.1's injectivity
    argument -- and therefore the meaning of the digest -- is conditional on
    them. Then the digest and the signature, which establish *who said it*.
    Then the bindings, which establish *what they said it about*: a refusal
    that recovers the Sentinel signer and names another action is a genuine
    refusal of something else, and certifying it here would be the same
    substitution F-13 was about, merely with a valid signature attached.
    """
    out = []
    record = located["record"]
    signature = located["signature"]
    source = located["source"]

    # ---- 0. a refusal excludes a receipt, and vice versa -----------------
    receipt = receipt_doc.get("receipt")
    if receipt is not None or receipt_doc.get("signature") is not None:
        out.append(Check(
            "the bundle presents a decision OR a refusal, not both", False,
            f"a §5.5.1 SignedRefusalRecord in {source} sits beside a §5.4 "
            "receipt body. The isolated signer either signed a decision or "
            "declined to; a bundle asserting both describes no coherent event, "
            "and a verifier certifying it would be certifying whichever half "
            "the reader happens to look at."))
    if "refused" in receipt_doc and not receipt_doc["refused"]:
        out.append(Check(
            "the bundle's `refused` flag agrees with the refusal record", False,
            f"receipt.json says refused: {receipt_doc['refused']!r} while "
            f"{source} presents a signed refusal record"))
    out.append(_refusal_label_check(sample_dir))

    # ---- 1. shape and charsets (§5.5.1) ---------------------------------
    shape_name = ("RefusalRecord carries exactly the nine §5.5.1 fields, each "
                  "inside its stated charset")
    try:
        fields = refusal.canonical_fields(record)
    except refusal.RefusalError as exc:
        out.append(Check(shape_name, False, str(exc)))
        return out
    out.append(Check(
        shape_name, True,
        f"9 field(s) validated with absolute anchors\n"
        f"presented in {source}"))

    loose = refusal.noncanonical_decimals(record)
    if loose:
        out.append(Check(
            "the record's decimal fields are in canonical form", True,
            f"{loose} carry leading zeros. §5.5.1 says only \"decimal "
            "digits\", and the field enters the preimage verbatim, so this "
            "produces a different digest rather than a colliding one and is "
            "advisory. It is surfaced because two spellings of one chainId is "
            "a place two implementations diverge silently.",
            skipped=True))

    # ---- 2. the record is signed at all ---------------------------------
    if not isinstance(signature, str) or not signature:
        out.append(Check(
            "the refusal record is signed (§5.5.1 SignedRefusalRecord)", False,
            f"{source} carries a RefusalRecord with no `signerSignature`. "
            "§5.5.1 defines the verifiable artifact as SignedRefusalRecord = "
            "RefusalRecord plus signerSignature; an unsigned record is a claim "
            "about the signer rather than a claim by it, and \"a refusal is "
            "attributable or it is not issued\"."))
        return out

    # ---- 3. the §5.5.1 digest -------------------------------------------
    digest = refusal.digest(record)
    out.append(Check(
        "§5.5.1 digest recomputed from the domain-tagged newline-joined "
        "preimage", True,
        f"preimage  {refusal.render_preimage(record)}\n"
        f"digest    0x{digest.hex()}\n"
        "10 segments, 9 delimiters, no trailing newline; not EIP-712, so no "
        "\\x19\\x01 and no domain separator"))

    # ---- 4. who signed it ------------------------------------------------
    try:
        recovered = recover_address(digest, signature)
        recover_error = None
    except (RecoveryError, ValueError) as exc:
        recovered, recover_error = None, str(exc)

    declared = fields["signer"]
    if recover_error:
        out.append(Check("the signature recovers the record's declared signer",
                         False, recover_error))
        return out

    ok = recovered == declared
    detail = f"recovered {recovered}"
    if not ok:
        detail = (f"recovered {recovered}\ndeclared  {declared}\n"
                  + _refusal_signature_diagnosis(record, signature, declared))
    out.append(Check("the signature recovers the record's declared signer", ok,
                     detail))

    # §5.5.1 puts `signer` inside the preimage, so the signature commits to the
    # claimed signer -- but a self-declared signer is not an identity. Anyone
    # can mint a record naming their own key and sign it, and every check above
    # passes. What makes it a *Sentinel* refusal is that the key is Sentinel's,
    # and §5.5.1 never says where a verifier learns that. domain.json is the
    # only place this bundle names it (REPORT.md F-9, F-18.4).
    domain_signer = _norm_hex(domain.get("signerAddress", ""))
    out.append(Check(
        "the recovered signer is the deployment's Sentinel signer",
        recovered == domain_signer,
        "" if recovered == domain_signer else
        f"recovered {recovered}\ndomain    {domain_signer}\n"
        "a refusal signed by any other key is somebody else's refusal; §5.5.1 "
        "does not say where a verifier learns the signer's identity, so this "
        "check reads domain.json, exactly as the receipt path does"))

    _, s_value, v_value = parse_signature(signature)
    out.append(Check(
        "refusal signature is EIP-2 canonical (low-s) and v in {27,28}",
        is_low_s(s_value) and v_value in (27, 28),
        f"v={v_value}, low-s={is_low_s(s_value)}"))

    # ---- 5. what it is a refusal OF (§5.5.1 attributability) -------------
    out.extend(_refusal_binding_checks(
        sample_dir, fields, evidence, evidence_hash, domain))

    # ---- 6. reason codes, §5.5.1 deferring to §5.4 -----------------------
    out.extend(_refusal_reason_code_checks(located, receipt_doc, fields))

    # ---- 7. the stated reason is not authenticated -----------------------
    doc = located.get("doc") or {}
    stated = (doc.get("refusalReason") or doc.get("reason")
              or receipt_doc.get("refusalReason") or receipt_doc.get("reason"))
    if stated is not None:
        out.append(Check(
            "the free-text refusal reason is NOT covered by the signature",
            True,
            f"{stated!r} is not a §5.5.1 field, so nothing commits to it and a "
            "presenter may rewrite it without breaking anything above. The "
            "authenticated statement of reasons is reasonCodesHash.",
            skipped=True))
    return out


def _refusal_signature_diagnosis(record, signature, declared):
    """Name the near-misses when recovery fails. See REPORT.md F-18.1.

    §5.5.1 gives a digest and never says how a signature over it is produced.
    This verifier recovers over the digest directly. If a producer instead
    reached for a wallet library's `signMessage`, the signature is over an
    EIP-191 wrapping and the only symptom is a signer mismatch -- which reads
    as a forgery. §5.8 warns about exactly this class of failure for the type
    strings ("a width mismatch is indistinguishable from an invalid
    signature"). The check still FAILS; this only stops the failure being a
    mystery.
    """
    try:
        digest = refusal.digest(record)
        candidates = (
            ("EIP-191 personal_sign over the §5.5.1 digest",
             refusal.eth_signed_message_digest(digest)),
            ("EIP-191 personal_sign over the §5.5.1 preimage STRING",
             refusal.eth_signed_message_digest(refusal.preimage(record))),
        )
        for label, alternative in candidates:
            try:
                if recover_address(alternative, signature) == declared:
                    return (
                        f"NOTE: this signature DOES recover {declared} under "
                        f"{label}.\n§5.5.1 states the digest and does not state "
                        "how it is signed; this verifier signs and recovers "
                        "over the digest itself. One of the two "
                        "implementations is wrong and §5.5.1 does not say "
                        "which. See REPORT.md F-18.1.")
            except (RecoveryError, ValueError):
                continue
    except (refusal.RefusalError, ValueError):
        return ""
    return ("the signature does not recover the declared signer under the "
            "§5.5.1 digest, nor under either EIP-191 wrapping of it")


def _refusal_binding_checks(sample_dir, fields, evidence, evidence_hash, domain):
    """The bindings that make a refusal attributable to THIS bundle.

    §5.5.1: "A refusal is attributable or it is not issued... a verifier must
    treat an absent record as an unestablished refusal rather than an
    established one." A record that is present but names another action, or
    another evidence bundle, or another deployment, is the same problem wearing
    a signature: the signer refused *something*, and this bundle is not it.

    Note what the record does and does not carry. It carries `chainId` and
    `vault` outright -- which the DecisionReceiptPayload does not, and which
    §5.8 records as a "known asymmetry". It does NOT carry `mandateHash` or
    `policyHash`; those are reached transitively, through `actionHash`, because
    the §5.3 ActionPayload has both as members. That transitivity is only
    available to a verifier holding action.json, which is why its absence is
    treated as a failure here rather than a skip.
    """
    out = []

    def load(name):
        path = os.path.join(sample_dir, name)
        return _read_json(path) if os.path.isfile(path) else None

    mandate, policy, action = load("mandate.json"), load("policy.json"), load("action.json")

    ok = fields["evidenceHash"] == evidence_hash
    out.append(Check(
        "refusal.evidenceHash binds the recomputed evidence", ok,
        "" if ok else f"record    {fields['evidenceHash']}\n"
                      f"computed  {evidence_hash}"))

    out.extend(_binding_checks(
        [(name, doc) for name, doc in
         (("mandate.json", mandate), ("policy.json", policy),
          ("action.json", action)) if doc is not None],
        domain))

    if action is None:
        out.append(Check(
            "refusal.actionHash binds the §5.3 action payload", False,
            "the bundle carries no action.json, so the action this refusal "
            "names cannot be exhibited. §5.5.1: \"A refusal is attributable or "
            "it is not issued\" -- a record whose actionHash matches nothing "
            "in front of the verifier is attributable to the signer but not to "
            "this bundle, and it is also the only route by which the refusal "
            "reaches the mandate and the policy at all (neither is a §5.5.1 "
            "field). Treated as a failure rather than a skip: see REPORT.md "
            "F-18.5."))
        return out

    out.append(_payload_hash_check(
        action, eip712.action_hash, "actionHash", "§5.3 ActionPayload",
        fields["actionHash"], "the refusal record"))
    out.append(_payload_hash_check(
        mandate, eip712.mandate_hash, "mandateHash", "§5.1 MandatePayload",
        action.get("mandateHash"), "action.json"))
    out.append(_payload_hash_check(
        policy, eip712.policy_hash, "policyHash", "§5.2 PolicyPayload",
        action.get("policyHash"), "action.json"))
    calldata = _calldata_check(action)
    if calldata is not None:
        out.append(calldata)
    if mandate is not None:
        out.append(Check(
            "mandate.policyHash == action.policyHash",
            _norm_hex(mandate.get("policyHash", ""))
            == _norm_hex(action.get("policyHash", ""))))

    # The record's OWN chain and vault members. §5.5.1's digest is tagged with
    # a constant string and nothing else -- no chainId, no verifyingContract --
    # so unlike the receipt there is no domain separator doing this work. These
    # two members are the entire chain-and-vault binding of a refusal, and they
    # only bind if somebody reads them. That is F-14's lesson, arriving in a
    # new place.
    try:
        record_chain = eip712.parse_uint("uint256", fields["chainId"])
        action_chain = eip712.parse_uint("uint256", action["chainId"])
        chain_ok = record_chain == action_chain
    except (KeyError, eip712.EncodingError):
        record_chain = None
        chain_ok = False
    out.append(Check(
        "refusal.chainId == the action payload's chainId", chain_ok,
        "" if chain_ok else f"record {fields['chainId']!r}, action "
                            f"{action.get('chainId')!r}"))
    vault_ok = fields["vault"] == _norm_hex(action.get("vault", ""))
    out.append(Check(
        "refusal.vault == the action payload's vault", vault_ok,
        "" if vault_ok else f"record {fields['vault']}\naction {action.get('vault')}"))

    try:
        domain_chain = eip712.parse_uint("uint256", domain["chainId"])
        domain_vault = "0x" + eip712.hex_to_bytes(
            domain["verifyingContract"], "verifyingContract").hex()
        ok = record_chain == domain_chain and fields["vault"] == domain_vault
        detail = "" if ok else (
            f"record chainId {fields['chainId']} vault {fields['vault']}\n"
            f"domain chainId {domain['chainId']} verifyingContract "
            f"{domain_vault}\n"
            "§5.5.1's digest carries no domain separator, so these two members "
            "are the whole of a refusal's deployment binding")
    except (KeyError, TypeError, eip712.EncodingError) as exc:
        ok, detail = False, str(exc)
    out.append(Check(
        "refusal.chainId/vault match the presented deployment (§5.5.1)",
        ok, detail))

    # requestedVerdict: the verdict the signer was asked to attest, and which
    # it declined to. §5.5.1 does not require it to agree with anything, but
    # the evidence bundle beside it records the evaluator's verdict, and the
    # receipt path already holds that field to the same standard.
    if isinstance(evidence, dict) and evidence.get("verdict") is not None:
        ok = evidence["verdict"] == fields["requestedVerdict"]
        out.append(Check(
            "refusal.requestedVerdict agrees with the evidence bundle's verdict",
            ok,
            "" if ok else
            f"record says {fields['requestedVerdict']}, evidence records "
            f"{evidence['verdict']!r}. §5.5.1 does not state that these must "
            "agree; this verifier requires it, because the requested verdict "
            "is by construction the one the evaluator produced and the signer "
            "declined to sign. See REPORT.md F-18.6."))
    else:
        out.append(Check(
            "refusal.requestedVerdict agrees with the evidence bundle's verdict",
            True, "the evidence bundle records no verdict", skipped=True))
    return out


def _refusal_reason_code_checks(located, receipt_doc, fields):
    """§5.5.1: "reasonCodesHash uses the same encoding as a receipt's (§5.4)".

    §5.4's surrounding requirements come with it, because they are properties
    of the commitment rather than of the receipt: the identifier grammar must
    be re-validated and rejected rather than sanitised, the full list must
    travel alongside because the record commits to a hash and not to the list,
    and signerFindings must be a subset rather than re-unioned.
    """
    out = []
    source = located.get("doc") or {}
    published = source.get("reasonCodes")
    if published is None:
        published = receipt_doc.get("reasonCodes")

    # RESOLVED INDEPENDENTLY OF `published`, WHICH IS THE FIX (A-055). These two keys do not
    # have to live in the same object, and IN THE SHIPPED CORPUS THEY DO NOT:
    # `refusal-vault-paused/receipt.json` puts `reasonCodes` inside `refusalRecord` and
    # `signerFindings` at the TOP LEVEL. The old code only consulted `receipt_doc` for findings
    # when `published` was missing — so on the one refusal artifact in the repository `findings`
    # resolved to None, the subset invariant was SKIPPED, and the verifier printed "the bundle
    # carries no `signerFindings` array" about a bundle that carries one. Adding an uncommitted
    # reason code to that array verified `=> PASS`, exit 0, against the unmutated verifier.
    # `test_signer_findings_must_be_a_subset` co-locates both keys in one envelope, so it never
    # exercised the corpus's own shape while its docstring claimed both were covered.
    findings = source.get("signerFindings")
    if findings is None:
        findings = receipt_doc.get("signerFindings")

    if published is None:
        out.append(Check(
            "refusal.reasonCodesHash recomputed from the published reason codes",
            False,
            "the bundle carries no `reasonCodes` array beside the refusal "
            "record. §5.5.1 gives reasonCodesHash the same encoding as §5.4's, "
            "and §5.4 requires the full ordered list to travel alongside; "
            "without it the commitment cannot be checked, and reporting the "
            "refusal as verified would misdescribe what was verified."))
        return out
    if not isinstance(published, list):
        out.append(Check("reasonCodes is a list", False,
                         f"got {type(published).__name__}"))
        return out

    try:
        reasoncodes.validate_all(published)
        if findings is not None:
            reasoncodes.validate_all(findings)
        out.append(Check(
            "every reason-code identifier matches ^[A-Za-z0-9_.:-]{1,64}$",
            True,
            f"{len(published)} identifier(s) validated with absolute anchors"))
    except reasoncodes.ReasonCodeError as exc:
        out.append(Check(
            "every reason-code identifier matches ^[A-Za-z0-9_.:-]{1,64}$",
            False, str(exc)))
        return out

    computed = reasoncodes.reason_codes_hash_hex(published)
    ok = computed == fields["reasonCodesHash"]
    out.append(Check(
        "refusal.reasonCodesHash recomputed from the published reason codes",
        ok,
        f"{len(reasoncodes.committed_set(published))} code(s) committed" if ok
        else f"computed {computed}\nrecord   {fields['reasonCodesHash']}"))

    if findings is None:
        out.append(Check("signerFindings ⊆ reasonCodes", True,
                         "no `signerFindings` array in the refusal record or at the top "
                         "level of receipt.json — checked both (A-055)",
                         skipped=True))
    else:
        missing = sorted(set(findings) - set(published))
        out.append(Check(
            "signerFindings ⊆ the committed reason-code set", not missing,
            "" if not missing else
            f"signer findings absent from reasonCodes: {missing}"))
    return out


def _binding_checks(payloads, domain):
    """§3.3(4)/§3.3(5) chain and vault binding, established from the bundle.

    §5.8: the payload hashes are bare `hashStruct` values -- "no `\\x19\\x01`
    prefix and no domain separator is applied. Chain and vault binding for
    these hashes therefore comes solely from the `chainId` and `vault` members
    of the payloads themselves."

    That sentence is only true if somebody reads those members. Nothing else in
    this file does: `domain.json` is an unsigned side file supplied by whoever
    presents the bundle, and the §5.8 warning block records that a receipt "is
    not self-describing", so the domain cannot be the authority on which chain
    and which vault a bundle belongs to. These are the checks that do not
    depend on it -- the cross-payload agreement is establishable from the
    bundle alone, per §3.3(4) ("Authorization binds the exact chain, vault,
    ...") and §3.3(5) ("Any mutation to a bound field invalidates
    authorization").

    The last two also tie the presented domain back to the signed payloads, so
    a genuinely-signed bundle cannot be re-presented under a domain naming
    another deployment. §5.8 fixes `verifyingContract` as "the SentinelVault
    address", which is the same address §5.1-§5.3 call `vault`.
    """
    if not payloads:
        return [Check("§3.3(4) chain and vault binding", True,
                      "no §5.1-§5.3 payload file in this sample", skipped=True)]

    chains, vaults, errors = {}, {}, []
    for label, doc in payloads:
        for name in ("chainId", "vault"):
            try:
                raw = doc[name]
            except (KeyError, TypeError):
                errors.append(f"{label}: missing required member {name!r}")
                continue
            try:
                if name == "chainId":
                    chains[label] = eip712.parse_uint("uint256", raw)
                else:
                    vaults[label] = "0x" + eip712.hex_to_bytes(raw, name).hex()
            except eip712.EncodingError as exc:
                errors.append(f"{label}.{name}: {exc}")
    if errors:
        return [Check(
            "every §5.1-§5.3 payload carries a well-formed chainId and vault",
            False, "\n".join(errors))]

    out = []
    for name, values in (("chainId", chains), ("vault", vaults)):
        distinct = sorted({str(v) for v in values.values()})
        ok = len(distinct) == 1
        out.append(Check(
            f"§5.1/§5.2/§5.3 payloads all bind the same {name} (§3.3(4))",
            ok,
            f"{len(values)} payload(s) agree on {distinct[0]}" if ok else
            "payloads disagree, so no single deployment is bound:\n"
            + "\n".join(f"  {label}: {values[label]}"
                        for label in sorted(values))))

    try:
        domain_chain = eip712.parse_uint("uint256", domain["chainId"])
        domain_vault = "0x" + eip712.hex_to_bytes(
            domain["verifyingContract"], "verifyingContract").hex()
    except (KeyError, TypeError, eip712.EncodingError) as exc:
        out.append(Check(
            "the presented domain carries a well-formed chainId and "
            "verifyingContract", False, str(exc)))
        return out

    for name, values, expected, domain_field in (
        ("chainId", chains, domain_chain, "chainId"),
        ("vault", vaults, domain_vault, "verifyingContract"),
    ):
        bad = {label: v for label, v in values.items() if v != expected}
        out.append(Check(
            f"every payload's {name} equals the presented domain's "
            f"{domain_field} (§5.8)",
            not bad,
            f"both say {expected}" if not bad else
            f"the domain this bundle was presented with names "
            f"{domain_field} {expected}, but the signed payloads bind:\n"
            + "\n".join(f"  {label}: {bad[label]}" for label in sorted(bad))
            + "\n§5.8: chain and vault binding for the payload hashes comes "
              "solely from these members, so the bundle and the domain "
              "describe different deployments."))
    return out


def _payload_hash_check(doc, fn, field, label, declared, against):
    """Recompute one §5.1-§5.3 hashStruct and compare it to a declared value.

    Shared by the receipt path and the §5.5.1 refusal path. The refusal record
    names only `actionHash`, so the mandate and policy hashes are compared
    against the action payload's members instead -- which is the same chain,
    walked one link further out.
    """
    if doc is None:
        return Check(f"recomputed {field} from {label}", True,
                     "payload file not present in this sample", skipped=True)
    try:
        computed = "0x" + fn(doc).hex()
    except eip712.EncodingError as exc:
        return Check(f"recomputed {field} from {label}", False, str(exc))
    expected = _norm_hex(declared) if isinstance(declared, str) else declared
    ok = computed == expected
    return Check(
        f"recomputed {field} from {label} matches {against}", ok,
        "" if ok else f"computed {computed}\ndeclared {expected}")


def _calldata_check(action):
    """calldata -> dataHash, the one place the raw call is bound.

    Parsed strictly: bytes.fromhex silently ignores embedded whitespace, so
    "0xc188 528b..." and "0xc188528b..." used to hash identically and dataHash
    stopped pinning the presented bytes.
    """
    if not action or "callData" not in action:
        return None
    try:
        raw = eip712.hex_to_bytes(action["callData"], "action.callData")
    except eip712.EncodingError as exc:
        return Check("keccak256(callData) matches action.dataHash", False,
                     str(exc))
    computed = "0x" + keccak256(raw).hex()
    ok = computed == _norm_hex(action.get("dataHash", ""))
    return Check("keccak256(callData) matches action.dataHash", ok,
                 "" if ok else
                 f"computed {computed}\naction   {action.get('dataHash')}")


def _chain_checks(sample_dir, receipt, evidence, domain):
    """Recompute every other hash the receipt commits to.

    §5 does not say these are EIP-712 hashStruct values; that was recovered by
    search (REPORT.md F-2). Without these, a receipt could be correctly signed
    over the *wrong* mandate and still pass every other check in this file.
    """
    out = []

    def load(name):
        path = os.path.join(sample_dir, name)
        return _read_json(path) if os.path.isfile(path) else None

    mandate, policy, action = load("mandate.json"), load("policy.json"), load("action.json")

    # §3.3(4)/§3.3(5) chain and vault binding, from the payload members §5.8
    # says the binding lives in. Runs first: if the bundle does not name one
    # deployment, every hash recomputation below is answering the wrong
    # question.
    out.extend(_binding_checks(
        [(name, doc) for name, doc in
         (("mandate.json", mandate), ("policy.json", policy), ("action.json", action))
         if doc is not None],
        domain,
    ))

    for doc, fn, field, label in (
        (mandate, eip712.mandate_hash, "mandateHash", "§5.1 MandatePayload"),
        (policy, eip712.policy_hash, "policyHash", "§5.2 PolicyPayload"),
        (action, eip712.action_hash, "actionHash", "§5.3 ActionPayload"),
    ):
        out.append(_payload_hash_check(doc, fn, field, label,
                                       receipt.get(field), "the receipt"))

    calldata = _calldata_check(action)
    if calldata is not None:
        out.append(calldata)

    # Cross-references that §5 lists as fields but never requires to agree.
    if mandate and policy:
        out.append(Check(
            "mandate.policyHash == receipt.policyHash",
            _norm_hex(mandate.get("policyHash", "")) == _norm_hex(receipt.get("policyHash", "")),
        ))
    if action:
        out.append(Check(
            "action binds the same mandate and policy as the receipt",
            _norm_hex(action.get("mandateHash", "")) == _norm_hex(receipt.get("mandateHash", ""))
            and _norm_hex(action.get("policyHash", "")) == _norm_hex(receipt.get("policyHash", "")),
        ))

    # Evidence-bundle fields §5.6 does not list, and never requires to agree
    # with the receipt (REPORT.md F-5). Checked anyway: if they can disagree,
    # the dashboard and the receipt can tell an operator different stories.
    anchor = evidence.get("anchor") if isinstance(evidence, dict) else None
    if isinstance(anchor, dict):
        ok = (str(anchor.get("blockNumber")) == str(receipt.get("simulationBlockNumber"))
              and _norm_hex(anchor.get("blockHash", "")) == _norm_hex(receipt.get("simulationBlockHash", "")))
        out.append(Check(
            "evidence.anchor matches the receipt's simulation block",
            ok,
            "" if ok else f"anchor  {anchor}\nreceipt {receipt.get('simulationBlockNumber')} "
                          f"{receipt.get('simulationBlockHash')}",
        ))
    if isinstance(evidence, dict) and "verdict" in evidence:
        expected = VERDICT_NAMES.get(int(receipt["verdict"]))
        ok = evidence["verdict"] == expected
        out.append(Check(
            "evidence.verdict agrees with the receipt's verdict enum",
            ok,
            "" if ok else f"evidence says {evidence['verdict']}, receipt decodes to {expected}",
        ))

    return out


def _override_checks(sample_dir, receipt, domain, tamper=None):
    """§5.5 OverrideAuthorizationPayload, using the §5.8 published type string.

    Only runs when the sample carries an override.json. §5.5: "The vault accepts
    an override only with the matching signed review receipt. A block receipt
    cannot be overridden."
    """
    path = os.path.join(sample_dir, "override.json")
    if not os.path.isfile(path):
        return []
    doc = _read_json(path)
    out = []
    if tamper:
        doc, domain = _tamper_override(doc, domain, tamper)
    override = doc.get("override")
    signature = doc.get("ownerSignature")
    owner = _norm_hex(doc.get("ownerAddress", ""))
    if not override or not signature:
        return [Check("override.json is well formed", False,
                      "missing `override` or `ownerSignature`")]

    # 1. Signature: recompute the digest and recover the owner.
    try:
        struct = eip712.override_hash(override)
        digest = eip712.override_digest(domain, override)
        recovered = recover_address(digest, signature)
        err = None
    except (eip712.EncodingError, RecoveryError, ValueError) as exc:
        struct = digest = recovered = None
        err = str(exc)

    if err:
        out.append(Check("override EIP-712 digest recomputed from §5.8", False, err))
        return out

    out.append(Check(
        "override EIP-712 digest recomputed from the §5.8 type string", True,
        f"hashStruct 0x{struct.hex()}\ndigest     0x{digest.hex()}",
    ))
    ok = recovered == owner
    out.append(Check("override signature recovers ownerAddress", ok,
                     f"recovered {recovered}" + ("" if ok else f"\ndeclared  {owner}")))

    # Same rule as the receipt's signature, applied for the same reason.
    #
    # §5 says nothing about signature encoding for EITHER signature -- not the
    # 65-byte r||s||v layout, not v in {27,28}, not EIP-2 low-s (REPORT.md
    # F-10). The low-s rule on the receipt therefore comes from EIP-2, not from
    # this specification, and EIP-2 is not about receipts: it is about
    # secp256k1 ECDSA. §5.8 gives the override the same construction as the
    # receipt -- an EIP-712 digest under the same domain, signed with a
    # secp256k1 key -- so there is no basis anywhere in §5 for holding one to a
    # canonical-form rule and not the other. The asymmetry was an omission.
    #
    # What it let through: (r, n-s, v^1) recovers the SAME address as (r, s, v),
    # so an override could be handed on with a second, byte-distinct signature
    # that verifies identically. §3.3(9) puts replay prevention in the vault's
    # nonce rather than in the credential's bytes, so this is not a replay --
    # but a verifier that reports two different documents as the same valid
    # override is describing them wrongly, and any consumer keyed on signature
    # bytes sees two authorizations where the owner produced one.
    _, s_value, v_value = parse_signature(signature)
    out.append(Check(
        "override signature is EIP-2 canonical (low-s) and v in {27,28}",
        is_low_s(s_value) and v_value in (27, 28),
        f"v={v_value}, low-s={is_low_s(s_value)}",
    ))

    # 2. §3.3(7): the override is a credential the isolated signer cannot mint.
    #    If the owner were the Sentinel signer, an override would be forgeable by
    #    the very component the review verdict is protecting against.
    signer = _norm_hex(receipt.get("signer", ""))
    out.append(Check(
        "override owner is NOT the Sentinel signer (§3.3(7))",
        recovered != signer,
        f"owner {recovered}\nsigner {signer}" if recovered == signer else "",
    ))

    # 3. Bindings.
    receipt_struct = "0x" + eip712.receipt_struct_hash(receipt).hex()
    ok = _norm_hex(override.get("reviewReceiptHash", "")) == receipt_struct
    out.append(Check(
        "override.reviewReceiptHash == this receipt's EIP-712 hashStruct", ok,
        "" if ok else f"override {override.get('reviewReceiptHash')}\n"
                      f"receipt  {receipt_struct}",
    ))
    for field in ("actionHash", "mandateHash", "policyHash"):
        ok = _norm_hex(override.get(field, "")) == _norm_hex(receipt.get(field, ""))
        out.append(Check(f"override.{field} == receipt.{field}", ok))

    action_path = os.path.join(sample_dir, "action.json")
    if os.path.isfile(action_path):
        action = _read_json(action_path)
        ok = str(override.get("actionNonce")) == str(action.get("actionNonce"))
        out.append(Check(
            "override.actionNonce == action.actionNonce", ok,
            "" if ok else f"override {override.get('actionNonce')}, "
                          f"action {action.get('actionNonce')}"))

    # 4. §5.5: "A block receipt cannot be overridden."
    verdict = VERDICT_NAMES.get(int(receipt["verdict"]))
    out.append(Check(
        "override targets a REVIEW receipt, not a BLOCK (§5.5)",
        verdict == "REVIEW",
        "" if verdict == "REVIEW" else
        f"receipt verdict is {verdict}; §5.5 says a block receipt cannot be "
        "overridden",
    ))
    return out


def _reason_code_checks(receipt_doc, receipt):
    """§5.4 as amended by D-022. Was NOT VERIFIABLE before the amendment."""
    out = []
    published = receipt_doc.get("reasonCodes")
    findings = receipt_doc.get("signerFindings")

    if published is None:
        # §5.4: "the full ordered list travels alongside the receipt and a
        # verifier must be given it." Not being given it is a verification
        # failure for a signed receipt, not a reason to pass quietly.
        out.append(Check(
            "reasonCodesHash recomputed from the published reason codes",
            False,
            "receipt.json carries no `reasonCodes` array. §5.4 requires the "
            "list to travel alongside the receipt; without it the "
            "reasonCodesHash commitment cannot be checked.",
        ))
        return out
    if not isinstance(published, list):
        out.append(Check("reasonCodes is a list", False,
                         f"got {type(published).__name__}"))
        return out

    # 1. Identifier grammar. Fail rather than sanitise.
    try:
        reasoncodes.validate_all(published)
        if findings is not None:
            reasoncodes.validate_all(findings)
        out.append(Check(
            "every reason-code identifier matches ^[A-Za-z0-9_.:-]{1,64}$",
            True,
            f"{len(published)} identifier(s) validated with absolute anchors",
        ))
    except reasoncodes.ReasonCodeError as exc:
        out.append(Check(
            "every reason-code identifier matches ^[A-Za-z0-9_.:-]{1,64}$",
            False, str(exc)))
        return out

    # 2. The commitment itself.
    computed = reasoncodes.reason_codes_hash_hex(published)
    declared = _norm_hex(receipt.get("reasonCodesHash", ""))
    ok = computed == declared
    canonical = reasoncodes.committed_set(published)
    detail = f"{len(canonical)} code(s) committed"
    if not ok:
        detail = f"computed {computed}\nreceipt  {declared}"
    out.append(Check(
        "reasonCodesHash recomputed from the published reason codes",
        ok, detail))

    # 3. signerFindings must be inside the committed set. §5.4 says the set is
    #    the union of the evaluator's codes and the signer's findings, so a
    #    finding outside `reasonCodes` means the two are not in fact unioned --
    #    and the receipt would be committing to the evaluator's half only.
    if findings is None:
        out.append(Check("signerFindings ⊆ reasonCodes", True,
                         "receipt.json carries no `signerFindings` array",
                         skipped=True))
    else:
        missing = sorted(set(findings) - set(published))
        out.append(Check(
            "signerFindings ⊆ the committed reason-code set",
            not missing,
            "" if not missing else
            f"signer findings absent from reasonCodes: {missing}\n"
            "§5.4 defines the committed set as the union of the evaluator's "
            "codes and the signer's findings, so this receipt does not commit "
            "to the signer's own findings.",
        ))

    # 4. Advisory: the published list should already be in canonical form.
    #    The hash is order- and duplicate-insensitive by construction, so this
    #    cannot be a failure -- but a drifting producer is worth surfacing.
    if published != canonical:
        reason = ("contains duplicates" if len(set(published)) != len(published)
                  else "is not in ascending byte order")
        out.append(Check(
            "published reasonCodes list is already in canonical order",
            True,
            f"the list {reason}; the hash is unaffected because the set is "
            "de-duplicated and sorted before hashing, so this is advisory only",
            skipped=True,
        ))
    return out


def _verdict_check(sample_dir, receipt):
    try:
        verdict_num = int(receipt["verdict"])
    except (KeyError, TypeError, ValueError):
        return Check("verdict decodes to a known enum member", False,
                     f"verdict is {receipt.get('verdict')!r}")
    name = VERDICT_NAMES.get(verdict_num)
    if name is None:
        return Check("verdict decodes to a known enum member", False,
                     f"verdict {verdict_num} is outside 0..2")

    expected = None
    meta_path = os.path.join(sample_dir, "meta.json")
    if os.path.isfile(meta_path):
        expected = _read_json(meta_path).get("verdict")
    if expected is None:
        index_path = os.path.join(os.path.dirname(sample_dir), "index.json")
        if os.path.isfile(index_path):
            for entry in _read_json(index_path):
                if entry.get("id") == os.path.basename(sample_dir):
                    expected = entry.get("verdict")
    if expected is None:
        return Check(f"verdict {verdict_num} decodes to {name}", True,
                     "no meta.json/index.json to cross-check against", skipped=True)
    ok = expected == name
    return Check(
        f"verdict {verdict_num} decodes to {name}, matching the case label",
        ok,
        "" if ok else f"case label says {expected}, receipt decodes to {name}",
    )


# Anvil account #1 -- the Sentinel signer's key, which is a *published* test key
# and deliberately not the owner's. Used by the override-wrongkey tamper mode to
# forge a perfectly valid signature from the wrong party. This is the §3.3(7)
# attack in its exact form: the isolated signer attempting to mint the owner
# credential that overrides its own review verdict.
_SENTINEL_SIGNER_TEST_KEY = (
    0x59C6995E998F97A5A0044966F0945389DC9E86DAE88C7A8412F4603B6B78690D
)


def _tamper_override(doc, domain, mode):
    """Mutate the override, or the deployment it is presented against."""
    doc = copy.deepcopy(doc)
    override = doc.get("override") or {}
    if mode == "override-reviewreceipt":
        # Point the authorization at a different review receipt.
        h = override["reviewReceiptHash"]
        override["reviewReceiptHash"] = "0x" + ("%02x" % (int(h[2:4], 16) ^ 0x01)) + h[4:]
    elif mode == "override-nonce":
        # Replay the same authorization at the next action nonce.
        override["actionNonce"] = str(int(override["actionNonce"]) + 1)
    elif mode == "override-wrongkey":
        # A *valid* signature over the *unmodified* payload, from the Sentinel
        # signer instead of the owner. Nothing is malformed; only the party is
        # wrong. A byte-flip cannot test this.
        digest = eip712.override_digest(domain, override)
        doc["ownerSignature"] = sign_digest(digest, _SENTINEL_SIGNER_TEST_KEY)
    elif mode == "override-repoint":
        # Repoint all three cross-artifact bindings and RE-SIGN as the owner, so the
        # authorization is genuine and only `override.X == receipt.X` can reject it. No
        # pre-existing mode touched these fields at all (A-056).
        for field in ("actionHash", "mandateHash", "policyHash"):
            h = override[field]
            override[field] = "0x" + ("%02x" % (int(h[2:4], 16) ^ 0xFF)) + h[4:]
        doc["ownerSignature"] = sign_digest(
            eip712.override_digest(domain, override), _OWNER_TEST_KEY)
    elif mode == "override-nonce-resigned":
        # `override-nonce` above bumps the nonce and leaves the old signature, so the
        # signature check fires and §3.3(9)'s nonce binding is never the witness. This
        # re-signs, isolating the binding.
        override["actionNonce"] = str(int(override["actionNonce"]) + 1)
        doc["ownerSignature"] = sign_digest(
            eip712.override_digest(domain, override), _OWNER_TEST_KEY)
    elif mode == "override-signer-mints":
        # §3.3(7) IN ITS EXACT FORM: the isolated signer mints the owner's credential.
        # `override-wrongkey` signs as the Sentinel signer but leaves `ownerAddress`
        # declaring the owner, so the recovery check catches it and §3.3(7) never bites.
        # Here the declared owner IS the Sentinel signer, so the bundle is self-consistent
        # and only §3.3(7) can reject it.
        doc["ownerAddress"] = public_key_to_address(
            point_mul(_SENTINEL_SIGNER_TEST_KEY, G))
        doc["ownerSignature"] = sign_digest(
            eip712.override_digest(domain, override), _SENTINEL_SIGNER_TEST_KEY)
    elif mode == "override-otherchain":
        # Lift the untouched, genuinely-signed override to another deployment.
        domain = dict(domain)
        domain["chainId"] = "8453"
    else:
        raise ValueError(f"unknown override tamper mode {mode!r}")
    return doc, domain


# A key that is NOT the Sentinel signer and NOT the owner. Used by
# refusal-wrongkey to mint a refusal that is entirely self-consistent -- valid
# signature, matching declared signer, correct bindings -- and simply not
# Sentinel's. Nothing internal to the record can catch it, which is the point.
# The OWNER's key -- Anvil account #0, the publicly documented dev account whose address
# `fixtures/samples/.../override.json` declares as `ownerAddress`. Used by the modes below to
# produce overrides that are VALIDLY OWNER-SIGNED and wrong in exactly one binding, which is
# the only way those bindings can be the witness: `override-nonce` mutates a signed field
# WITHOUT re-signing, so the signature check catches it first and the nonce binding never bites
# (A-056). This key ships in Anvil's own startup banner; it is a fixture, not a credential.
_OWNER_TEST_KEY = (
    0xAC0974BEC39A17E36BA4A6B4D238FF944BACB478CBED5EFCAE784D7BF4F2FF80
)


_OUTSIDER_TEST_KEY = (
    0x00000000000000000000000000000000000000000000000000000000000f00d1
)


def _tamper_refusal(located, domain, mode):
    """Mutate a §5.5.1 SignedRefusalRecord, then RE-SIGN it.

    Every mode but `refusal-signature` and `refusal-strip-signature` leaves a
    cryptographically perfect SignedRefusalRecord behind. That is deliberate: a
    verifier that only checks the signature accepts all of them, and §5.5.1's
    "a refusal is attributable or it is not issued" is precisely the
    requirement a valid signature does not satisfy on its own.
    """
    located = copy.deepcopy(located)
    record = located["record"]

    def flip(value):
        return "0x" + ("%02x" % (int(value[2:4], 16) ^ 0x01)) + value[4:]

    resign = True
    if mode == "refusal-actionhash":
        record["actionHash"] = flip(record["actionHash"])
    elif mode == "refusal-evidencehash":
        record["evidenceHash"] = flip(record["evidenceHash"])
    elif mode == "refusal-chainid":
        record["chainId"] = "8453"
    elif mode == "refusal-vault":
        record["vault"] = "0x" + "11" * 20
    elif mode == "refusal-verdict":
        record["requestedVerdict"] = next(
            v for v in refusal.VERDICT_NAMES if v != record["requestedVerdict"])
    elif mode == "refusal-reasonhash":
        record["reasonCodesHash"] = flip(record["reasonCodesHash"])
    elif mode == "refusal-signature":
        located["signature"] = flip(located["signature"])
        resign = False
    elif mode == "refusal-strip-signature":
        located["signature"] = None
        resign = False
    elif mode == "refusal-wrongkey":
        # A whole refusal minted by an outsider: the record declares the
        # outsider's own address as `signer`, so it is internally consistent
        # and only domain.json's signerAddress can reject it.
        outsider = public_key_to_address(point_mul(_OUTSIDER_TEST_KEY, G))
        record["signer"] = outsider
    elif mode == "refusal-otherchain":
        # The untouched, genuinely-signed refusal, presented as belonging to a
        # different deployment.
        domain = dict(domain)
        domain["chainId"] = "8453"
        resign = False
    elif mode in ("refusal-reasons-add", "refusal-reasons-remove"):
        # The record and its signature are untouched. Only the reason-code list
        # travelling alongside is edited -- the §5.4/D-022 substitution, which
        # §5.5.1 inherits by giving reasonCodesHash the same encoding.
        doc = located.get("doc") or {}
        codes = doc.get("reasonCodes")
        if not isinstance(codes, list):
            raise NotApplicable(
                f"{mode} needs a reasonCodes list beside the refusal record")
        if mode == "refusal-reasons-add":
            doc["reasonCodes"] = codes + ["EVAL_FABRICATED_EXTRA_CODE"]
        else:
            if not codes:
                raise NotApplicable(
                    f"{mode} cannot be applied to an empty reasonCodes list")
            doc["reasonCodes"] = codes[1:]
        resign = False
    else:
        raise ValueError(f"unknown refusal tamper mode {mode!r}")

    if resign:
        key = (_OUTSIDER_TEST_KEY if mode == "refusal-wrongkey"
               else _SENTINEL_SIGNER_TEST_KEY)
        located["signature"] = sign_digest(refusal.digest(record), key)
    return located, domain


class NotApplicable(Exception):
    """A tamper mode that this sample's shape cannot express."""


def _tamper_reasons(receipt_doc, mode):
    """Mutate the published reasonCodes list. Returns (doc, applied).

    The receipt body -- and therefore the committed reasonCodesHash and the
    signature -- is left untouched. Only the list travelling alongside is
    changed, which is exactly the substitution an attacker would attempt.
    """
    doc = copy.deepcopy(receipt_doc)
    codes = doc.get("reasonCodes")
    if not isinstance(codes, list):
        return doc, False

    if mode == "reasons-add":
        # Always applicable, including to an empty list.
        doc["reasonCodes"] = codes + ["EVAL_FABRICATED_EXTRA_CODE"]
        return doc, True
    if mode == "reasons-remove":
        if not codes:
            return doc, False
        doc["reasonCodes"] = codes[1:]
        return doc, True
    if mode == "reasons-substitute":
        if not codes:
            return doc, False
        # Swap one identifier for a different, still well-formed one, keeping
        # the list length identical.
        doc["reasonCodes"] = ["EVAL_SUBSTITUTED_CODE"] + codes[1:]
        return doc, True
    if mode == "reasons-reorder":
        # Needs at least two distinct codes for a reversal to change anything.
        if len(set(codes)) < 2:
            return doc, False
        doc["reasonCodes"] = list(reversed(codes))
        return doc, True
    raise ValueError(f"unknown reason-code tamper mode {mode!r}")


def _tamper_json(evidence):
    """Mutate exactly one byte-equivalent of the evidence, in place-ish.

    A verifier that cannot fail is not a verifier. This flips a single character
    deep inside a nested string so that neither the JSON shape nor the key set
    changes -- only the canonical bytes.
    """
    mutated = copy.deepcopy(evidence)

    def walk(node):
        if isinstance(node, dict):
            for key in sorted(node):
                if walk_value(node, key):
                    return True
            return False
        if isinstance(node, list):
            for index in range(len(node)):
                if walk_value(node, index):
                    return True
        return False

    def walk_value(container, key):
        value = container[key]
        if isinstance(value, str) and value:
            last = value[-1]
            replacement = "0" if last != "0" else "1"
            container[key] = value[:-1] + replacement
            return True
        return walk(value)

    if not walk(mutated):
        raise RuntimeError("no string leaf found to tamper with")
    return mutated


def _byte_diff(actual, expected):
    limit = min(len(actual), len(expected))
    for i in range(limit):
        if actual[i] != expected[i]:
            lo, hi = max(0, i - 40), min(limit, i + 40)
            return (
                f"first difference at byte {i} "
                f"(lengths {len(actual)} vs {len(expected)})\n"
                f"computed ...{actual[lo:hi]!r}...\n"
                f"expected ...{expected[lo:hi]!r}..."
            )
    return f"one is a prefix of the other: lengths {len(actual)} vs {len(expected)}"


def run(sample_dir, domain_path=None, tamper=None, quiet=False, verbose=True):
    label = os.path.basename(os.path.abspath(sample_dir))
    try:
        ok, checks = verify_sample(sample_dir, domain_path, tamper)
    except NotApplicable as exc:
        if not quiet:
            print(f"{label} {_color('[tamper: ' + tamper + ']', YELLOW)}")
            print(f"  => {_color('N/A', YELLOW)}: {exc}\n")
        return True, []
    except Exception as exc:  # noqa: BLE001 - a crash is a verification failure
        if not quiet:
            print(f"{label}: {_color('ERROR', RED)} {type(exc).__name__}: {exc}")
        return False, [Check("verification ran to completion", False, str(exc))]

    if not quiet:
        suffix = f" {_color('[tamper: ' + tamper + ']', YELLOW)}" if tamper else ""
        print(f"{label}{suffix}")
        if verbose:
            for check in checks:
                print(check.render())
    if tamper:
        must_verify = tamper in TAMPER_MUST_STILL_VERIFY
        as_expected = ok if must_verify else not ok
        if not quiet:
            outcome = _color("PASS", GREEN) if as_expected else _color("FAIL", RED)
            if must_verify:
                verdict = ("correctly still verified" if ok
                           else "WRONGLY REJECTED")
                note = (" (order in the published list must not matter)")
            else:
                verdict = "correctly rejected" if not ok else "WRONGLY ACCEPTED"
                note = ""
            print(f"  => tamper self-test {outcome}: {verdict} "
                  f"the mutated {tamper}{note}\n")
        return as_expected, checks

    if not quiet:
        print(f"  => {_color('PASS', GREEN) if ok else _color('FAIL', RED)}\n")
    return ok, checks


def run_tamper_suite(sample_dir, domain_path=None, quiet=False, verbose=False):
    """Every tamper mode must produce its expected outcome."""
    results = []
    for mode in TAMPER_MODES:
        as_expected, _ = run(sample_dir, domain_path, tamper=mode,
                             quiet=quiet, verbose=verbose)
        results.append(as_expected)
    return all(results)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Verify a Sentinel decision receipt end to end.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("sample", nargs="+", help="sample directory (or, with --all, its parent)")
    parser.add_argument("--domain", help="path to domain.json (default: sample dir, then parent)")
    parser.add_argument("--tamper", nargs="?", const="all", choices=("all",) + TAMPER_MODES,
                        help="self-test: mutate the artifact and require verification to FAIL "
                             "(default 'all' runs every mode)")
    parser.add_argument("--all", action="store_true",
                        help="treat each argument as a directory of sample directories")
    parser.add_argument("--print-types", action="store_true",
                        help="print the derived EIP-712 type strings and exit")
    args = parser.parse_args(argv)

    if args.print_types:
        print("domain type:", eip712.DOMAIN_TYPE)
        print("struct type:", eip712.RECEIPT_TYPE)
        return 0

    targets = []
    for path in args.sample:
        if args.all:
            targets.extend(
                os.path.join(path, entry)
                for entry in sorted(os.listdir(path))
                if os.path.isdir(os.path.join(path, entry))
            )
        else:
            targets.append(path)

    if args.tamper == "all":
        oks = [run_tamper_suite(t, args.domain, verbose=False) for t in targets]
    else:
        oks = [run(t, args.domain, args.tamper)[0] for t in targets]
    failed = [t for t, ok in zip(targets, oks) if not ok]
    passed = len(oks) - len(failed)
    print(f"{passed}/{len(oks)} sample(s) "
          f"{'behaved as expected under every tamper mode' if args.tamper else 'verified'}")
    for target in failed:
        print(f"  {_color('FAILED', RED)}: {target}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
