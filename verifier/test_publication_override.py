#!/usr/bin/env python3
"""Adversarial tests for the REVIEW / owner-override arm of the publication predicate.

    python3 verifier/test_publication_override.py
    python3 -m unittest discover -s verifier -v

WHY THIS FILE EXISTS
--------------------
`verifier/verify_publication.py` gained an owner-override execution arm --
`--execution-path {automatic,owner-override}`, `check_verdict()` and
`check_owner_override()` -- to close R-A018-01, whose closure condition reads:

    a non-`ALLOW` verdict fails closed; a `REVIEW` receipt passes only through an
    explicitly modelled and authenticated owner override, matching the Vault's
    `NotAllowVerdict` / `NotReviewVerdict`; and BOTH ARMS have negative tests.

`test_publication_verifier.py` covers the automatic arm. It was written against a
baseline in which the override arm did not exist, so it contains no test that
supplies `--execution-path owner-override` and no test that opens
`override.json`: the second arm shipped with **no coverage at all**, and the
final clause of R-A018-01 was therefore unmet. This file is that coverage.

D-058(1) AND A-028: WHO WROTE THIS, AND WHAT THAT BUYS
------------------------------------------------------
Written by an independent test author who is forbidden to edit
`verify_publication.py`, `deployment.py`, or `test_publication_verifier.py`. An
implementer's own tests inherit its blind spots; the point of the separation is
that the contract below is derived from the sources, not from the implementer's
reasoning about them. Nothing in the new code's comments was taken as authority.

THE SPECIFICATION, IN THE ORDER IT WAS CONSULTED
------------------------------------------------
1. `contracts/src/SentinelVault.sol::executeWithOverride` -- the on-chain truth.
   It runs `_checkAction`, then `_checkReceipt`, then rejects any verdict that is
   not `REVIEW` (`NotReviewVerdict`), then requires the override to name this
   exact review-receipt hash, action hash, mandate hash, policy hash and action
   nonce (`OverrideMismatch`), then requires a non-empty and current window
   (`InvalidValidityWindow` / `OverrideNotYetValid` / `OverrideExpired`), then
   requires the signature to recover to `owner` (`NotOwnerOverride`). The offline
   verifier must refuse everything the Vault refuses.
2. `contracts/src/types/SentinelTypes.sol` -- the nine-field §5.5 payload and its
   EIP-712 type string, and the §5.5 note that "a BLOCK receipt cannot be
   overridden at all -- that path requires a new mandate or policy."
3. `verifier/verify.py::_override_checks` -- the house pattern. The legacy
   verifier has verified overrides since D-023 and holds them to EIP-2 low-s with
   `v in {27,28}` (R-A018-16(a)), binds the authorising party to the mandate's
   principal (A-058), and refuses an override that does not target a REVIEW
   receipt. Where this file and the legacy verifier disagree about a bundle, the
   disagreement is reported, not smoothed over.
4. `docs/a018-remediation-register.md` -- R-A018-01 and R-A018-16.

HOW A BUNDLE IS STAGED, AND WHY NOT A SECOND WAY
------------------------------------------------
`Bundle` and `sign_manifest` are IMPORTED from `test_publication_verifier`, not
re-implemented. A second staging helper would be a second thing to drift, and the
A-056 lesson those helpers encode -- re-seal the whole chain, or the mutation is
caught by a stale hash and the binding it was meant to probe never bites -- has
to hold for the override too. `OverrideBundle` adds exactly one thing: a
`seal_override()` that recomputes the override's five bindings from the re-sealed
bundle and re-signs it with a chosen key, so a negative below reaches the
predicate as a perfectly authentic, internally consistent credential that is
nonetheless wrong. `TestOverrideControl` is what keeps that helper honest.

WHAT IS NOT COVERED HERE, so a green run is not read as more than it is
----------------------------------------------------------------------
`executeWithOverride` also runs `_checkAction`, and four of its checks are not
observable offline by any test: `paused`, `allowedTarget`, `allowedSelector` and
`action.actionNonce == actionNonce` are Vault storage. The first three are vault
constructor state; the fourth is R-A018-02's corrected responsibility split --
only the Vault consumes a nonce, atomically, at execution. What IS asserted is
that an override does not excuse the checks that ARE observable offline
(`TestOverrideDoesNotExcuseTheAction`), because "which paths does this check not
run on?" is the question D-052(b) turned into a required one.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import eip712  # noqa: E402
import jcs  # noqa: E402
import verify_publication  # noqa: E402
from secp256k1 import N, parse_signature, sign_digest  # noqa: E402

# Imported, never restated. See the module docstring: a second copy of the
# staging helper is a second thing to drift, and a second copy of a test key is a
# second thing for R-A018-12's guard to find.
from test_publication_verifier import (  # noqa: E402
    AUTHORITY, AUTHORITY_KEY, Bundle, NOW, OUTSIDER, OUTSIDER_KEY, OWNER,
    OWNER_KEY, PREDICATE, PublicationTestCase, SAMPLES, SIGNER, SIGNER_KEY,
    address_of, domain_of, manifest_payload, read_json, write_json,
)

AUTOMATIC = verify_publication.AUTOMATIC_PATH
OVERRIDE = verify_publication.OVERRIDE_PATH

# The one fixture in the corpus that carries a §5.5 credential. `index.json`
# records it as the REVIEW case; `fixtures/samples/*/override.json` exists
# nowhere else.
REVIEW_CASE = "case-4-review-failmode-review"
ALLOW_CASE = "case-1-allow"


class OverrideBundle(Bundle):
    """`Bundle`, plus the one thing the automatic arm never needed.

    `Bundle.seal()` rebuilds policy -> mandate -> action -> receipt and re-signs
    the mandate as the owner and the receipt as the signer. It does not touch
    `override.json`, because until this arm existed nothing read it.

    `seal_override()` completes the chain: it repoints the override's five
    bindings at the re-sealed bundle and re-signs the §5.5 payload under the same
    EIP-712 domain the predicate derives from the manifest. Without it every
    negative in this file would be refused by the override's own signature check
    before the binding under test was ever compared -- the A-056 failure mode,
    one artifact further down.
    """

    def override_doc(self):
        return read_json(self.path("override.json"))

    def graft_override(self, case=REVIEW_CASE):
        """Give a bundle that ships no §5.5 credential one to carry."""
        shutil.copy(os.path.join(SAMPLES, case, "override.json"),
                    self.path("override.json"))
        self._template = None
        return self

    def pristine_override(self):
        """A deep copy of the credential as the corpus shipped it.

        `seal_override()` starts from this rather than from whatever it wrote
        last, so a test may stage several mutations against ONE bundle without
        each one inheriting the previous one's damage. Staging a fresh bundle per
        mutation would be cleaner still and costs three secp256k1 signatures a
        time in pure Python; this is the compromise, and it is safe because every
        call rewrites `override.json` in full."""
        if getattr(self, "_template", None) is None:
            self._template = self.override_doc()
        return json.loads(json.dumps(self._template))

    def seal_override(self, mutate=None, key=None, owner_address=None,
                      declare_owner=True, malleate=False, force_v=None,
                      domain=None, post=None):
        """Rebind and re-sign `override.json`.

        `mutate` edits the payload BEFORE signing, so what reaches the predicate
        is a genuine owner authorization of the wrong thing. `post` edits the
        document AFTER signing, which is the only way to stage a value
        `eip712.parse_uint` refuses to hash at all.
        """
        key = self.owner_key if key is None else key
        doc = self.pristine_override()
        override = doc["override"]
        override["reviewReceiptHash"] = (
            "0x" + eip712.receipt_struct_hash(self.receipt).hex())
        override["actionHash"] = self.receipt["actionHash"]
        override["mandateHash"] = self.action["mandateHash"]
        override["policyHash"] = self.action["policyHash"]
        override["actionNonce"] = self.action["actionNonce"]
        if mutate:
            mutate(override)

        signature = sign_digest(
            eip712.override_digest(domain or domain_of(self.payload), override), key)
        if malleate:
            signature = malleated(signature)
        if force_v is not None:
            signature = signature[:-2] + "%02x" % force_v

        doc["override"] = override
        doc["ownerSignature"] = signature
        if not declare_owner:
            doc.pop("ownerAddress", None)
        else:
            doc["ownerAddress"] = (
                owner_address if owner_address is not None else address_of(key))
        if post:
            post(doc)
        write_json(self.path("override.json"), doc)
        return self


def malleated(signature):
    """(r, s, v) -> (r, n-s, v^1): the same authorization, reflected.

    Restated from `TestDeploymentSignatureCanonicalForm.malleate` because the
    override is a third signature the same EIP-2 argument applies to, and
    R-A018-16(a) is the register item that says applying it to some signatures
    and not others was an omission rather than a decision.
    """
    r, s, v = parse_signature(signature)
    return ("0x" + r.to_bytes(32, "big").hex()
            + (N - s).to_bytes(32, "big").hex()
            + bytes([{27: 28, 28: 27}[v]]).hex())


class OverrideTestCase(PublicationTestCase):
    """The override arm's invocation, and a live-clock staging helper.

    Everything inherited from `PublicationTestCase` -- `assert_certifies`,
    `assert_refused` and its load-bearing subject regex, `cli` -- routes through
    `_predicate`, so overriding that one method is enough to move the whole
    inherited apparatus onto the override arm.
    """

    def bundle(self, case=REVIEW_CASE, payload=None, seal=True):
        room = tempfile.mkdtemp(dir=self.root)
        b = OverrideBundle(case, room, payload=payload)
        return b.seal() if seal else b

    def _predicate(self, bundle, authority=AUTHORITY, key=AUTHORITY_KEY,
                   evaluation_time=NOW, manifest_path=None,
                   execution_path=OVERRIDE):
        return verify_publication.verify(
            bundle.dir,
            manifest_path if manifest_path else bundle.manifest_file(key),
            authority, evaluation_time=evaluation_time,
            execution_path=execution_path)

    def live_bundle(self, case=REVIEW_CASE):
        """A REVIEW bundle current at the REAL host clock.

        Every other test names an evaluation time, which puts the run in
        `MODE_DIAGNOSTIC` -- correct under R-A018-03, and unable to witness what a
        CERTIFYING override run says about itself. The fixture windows all closed
        in the past, so a certifying run has to be staged: the receipt, mandate,
        policy, action deadline and manifest are moved around `time.time()` and
        the whole chain re-sealed. The override's own window is left as the
        fixture set it, `[0, 4000000000)`, which contains any plausible now.
        """
        live = int(time.time())
        b = self.bundle(case, payload=manifest_payload(issuedAt=str(live - 60)),
                        seal=False)
        b.receipt["issuedAt"] = str(live - 60)
        b.receipt["expiresAt"] = str(live + 3600)
        b.mandate["validAfter"] = str(live - 3600)
        b.mandate["validUntil"] = str(live + 7200)
        b.policy["validAfter"] = str(live - 3600)
        b.policy["validUntil"] = str(live + 7200)
        b.action["deadline"] = str(live + 7200)
        b.seal()
        # `case-1-allow` ships no §5.5 credential and needs none: it is staged
        # live only as the automatic-arm comparison in
        # `TestTheCertifyingRunSaysWhichPathItCertified`.
        if os.path.isfile(b.path("override.json")):
            b.seal_override()
        return b


# ---------------------------------------------------------------------------
# The controls
# ---------------------------------------------------------------------------

class TestOverrideControl(OverrideTestCase):
    """Nothing below this class means anything without these.

    Every negative in this file asserts that a bundle is REFUSED. A refusal is
    evidence only if an otherwise-identical bundle is ACCEPTED, and the shipped
    fixture is the only unmodified thing in the corpus that can supply that."""

    def test_the_shipped_review_fixture_certifies_on_the_override_path(self):
        """PASSES. The positive control, and the independent check of the
        implementer's claim that `case-4-review-failmode-review`'s shipped
        `override.json` is fully valid. It is: unmodified, re-sealed only in the
        sense that `Bundle.seal()` re-signs with the same keys over the same
        values, it certifies on `--execution-path owner-override`."""
        result = self.assert_certifies(self.bundle())
        self.assertEqual(result["verdict"], "REVIEW")
        self.assertEqual(result["executionPath"], OVERRIDE)
        self.assertIn("ownerOverrideHash", result)

    def test_the_reported_override_hash_is_the_eip712_hash_struct(self):
        """PASSES. `ownerOverrideHash` must be the §5.8 `hashStruct` of the
        payload that was actually authenticated -- the same value
        `SentinelVault` computes with `T.hashOverride(auth)` and emits as
        `OverrideAuthorized.overrideHash`. Recomputed here from the file rather
        than trusted, or the field is decoration."""
        bundle = self.bundle()
        result = self.assert_certifies(bundle)
        expected = "0x" + eip712.override_hash(
            bundle.override_doc()["override"]).hex()
        self.assertEqual(result["ownerOverrideHash"], expected)

    def test_the_override_reseal_helper_reproduces_the_shipped_credential(self):
        """PASSES, and MUST keep passing. `seal_override()` with no arguments has
        to reproduce the shipped override exactly -- same nine field values, same
        hashStruct -- or every negative staged through it is probing a credential
        the corpus never contained."""
        shipped = read_json(SAMPLES, REVIEW_CASE, "override.json")["override"]
        bundle = self.bundle().seal_override()
        self.assertEqual(bundle.override_doc()["override"], shipped)
        self.assertEqual(self.assert_certifies(bundle)["ownerOverrideHash"],
                         "0x" + eip712.override_hash(shipped).hex())

    def test_the_reseal_preserves_the_receipt_hash_the_override_names(self):
        """PASSES. `override.reviewReceiptHash` is the receipt's EIP-712
        `hashStruct`, so if `Bundle.seal()` produced a different receipt than the
        corpus records, the positive control above would be passing for the wrong
        reason -- a helper agreeing with itself."""
        shipped = read_json(SAMPLES, REVIEW_CASE, "override.json")["override"]
        bundle = self.bundle()
        self.assertEqual(
            "0x" + eip712.receipt_struct_hash(bundle.receipt).hex(),
            shipped["reviewReceiptHash"])

    def test_a_certifying_override_run_exits_zero_at_the_host_clock(self):
        """PASSES. The positive control at the CLI and in `MODE_STATIC`.

        Without it, every CLI assertion below could be green because the run
        failed for an unrelated reason. This is also the only test in the file
        that witnesses the override arm producing a real certification rather
        than a `--evaluation-time` diagnostic."""
        bundle = self.live_bundle()
        completed = self.cli(bundle, extra=["--execution-path", OVERRIDE])
        self.assertEqual(completed.returncode, 0,
                         "override arm did not certify:\n" + completed.stderr)
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
        self.assertEqual(payload["mode"], verify_publication.MODE_STATIC)
        self.assertEqual(payload["executionPath"], OVERRIDE)


# ---------------------------------------------------------------------------
# The verdict gate on the override arm
# ---------------------------------------------------------------------------

class TestVerdictGatesTheOverridePath(OverrideTestCase):
    """R-A018-01, second arm. `executeWithOverride` reverts `NotReviewVerdict`
    on anything that is not REVIEW, and SentinelTypes.sol §5.5 says it in words:
    "A BLOCK receipt cannot be overridden at all -- that path requires a new
    mandate or policy."

    The sharp form of each test is a BLOCK or ALLOW receipt carrying a FULLY
    VALID owner override. If the verdict gate were missing, that bundle is
    exactly what would slip through, and a bundle with a broken override would
    not tell you so."""

    def test_a_block_receipt_with_a_valid_override_is_refused(self):
        """PASSES. §5.5 verbatim, in its strongest form: the override here is
        genuine, current, correctly bound and signed by the owner. The only thing
        wrong with the bundle is that BLOCK is not overridable."""
        bundle = self.bundle(seal=False)
        bundle.receipt["verdict"] = "0"
        bundle.seal().seal_override()
        message = self.assert_refused(bundle, r"(?i)BLOCK")
        self.assertRegex(message, r"(?i)NotReviewVerdict|not REVIEW")

    def test_every_shipped_block_fixture_is_refused_on_the_override_path(self):
        """PASSES. The corpus's real BLOCK bundles -- including
        `case-2-injection-block`, the prompt-injection case -- presented at the
        override entry point, which is the presenter's obvious next move once the
        automatic path starts reading the verdict. None of them may pass, and a
        fix keyed to one fixture must not satisfy this."""
        blocks = [e["id"] for e in read_json(SAMPLES, "index.json")
                  if e["verdict"] == "BLOCK" and not e.get("signerRefused")]
        self.assertGreaterEqual(len(blocks), 3, "expected several BLOCK fixtures")
        for case in blocks:
            with self.subTest(case=case):
                self.assert_refused(self.bundle(case, seal=False),
                                    r"(?i)verdict|BLOCK")

    def test_an_allow_receipt_with_a_valid_override_is_refused(self):
        """PASSES, and the Vault is the authority for it rather than intuition.

        An ALLOW receipt is executable -- but through `executeWithReceipt`, and
        `executeWithOverride` reverts `NotReviewVerdict` on it just as it does on
        a BLOCK. There is deliberately no third path and no path that accepts
        two verdicts, so the verifier must not accept an ALLOW here merely
        because ALLOW is "stronger" than REVIEW. The declared entry point is part
        of the claim being verified."""
        bundle = self.bundle(seal=False)
        bundle.receipt["verdict"] = "2"
        bundle.seal().seal_override()
        message = self.assert_refused(bundle, r"(?i)ALLOW")
        self.assertRegex(message, r"(?i)NotReviewVerdict|not REVIEW")

    def test_the_shipped_allow_fixture_is_refused_on_the_override_path(self):
        """PASSES. The same property with no tampering at all: the corpus's ALLOW
        bundle, presented at the wrong entry point."""
        self.assert_refused(self.bundle(ALLOW_CASE, seal=False),
                            r"(?i)verdict|ALLOW")

    def test_an_out_of_range_verdict_is_refused_on_the_override_path(self):
        """PASSES. `SentinelTypes.Verdict` has three members. A fourth value must
        fail closed on BOTH arms rather than fall through an equality test for
        REVIEW that was never written -- the same fail-closed shape §5.4 gets
        from making BLOCK the zero value."""
        for value in ("3", "7", "255"):
            with self.subTest(verdict=value):
                bundle = self.bundle(seal=False)
                bundle.receipt["verdict"] = value
                bundle.seal().seal_override()
                self.assert_refused(bundle, r"(?i)verdict")

    def test_a_review_receipt_is_refused_on_the_automatic_path(self):
        """PASSES. The mirror, asserted here rather than assumed: the two arms
        must not both accept REVIEW. `executeWithReceipt` reverts
        `NotAllowVerdict`, and the refusal must point the recipient at the arm
        that could authenticate the credential they are holding."""
        message = self.assert_refused(
            self.bundle(seal=False), r"(?i)REVIEW",
            execution_path=AUTOMATIC)
        self.assertRegex(message, r"(?i)owner-override|executeWithOverride")


# ---------------------------------------------------------------------------
# The credential has to be there, and has to be a credential
# ---------------------------------------------------------------------------

class TestOverrideCredentialIsRequired(OverrideTestCase):
    """§3.3(7)'s "separately authenticated" begins with "present". A REVIEW
    bundle with no override is the ordinary case -- the signer asked for a human
    -- and it must not certify merely because the caller typed the flag."""

    def test_a_review_receipt_with_no_override_file_is_refused(self):
        """PASSES. The flag declares which entry point the bundle is presented
        for; it does not supply the credential that entry point requires."""
        bundle = self.bundle()
        os.remove(bundle.path("override.json"))
        self.assert_refused(bundle, r"(?i)override\.json")

    def test_an_override_document_missing_either_half_is_refused(self):
        """PASSES. A §5.5 payload with no signature is an unsigned claim, and a
        signature with no payload authenticates nothing. Absence is not
        agreement -- the same rule `mandate-signature.json` already gets.

        One staged bundle, rewritten per shape: each iteration replaces
        `override.json` entirely, so nothing carries over."""
        bundle = self.bundle()
        for doc in ({}, {"override": {}}, {"ownerSignature": "0x" + "11" * 65},
                    {"override": ["not", "an", "object"],
                     "ownerSignature": "0x" + "11" * 65},
                    {"override": {}, "ownerSignature": 1234}):
            with self.subTest(shape=sorted(doc)):
                write_json(bundle.path("override.json"), doc)
                self.assert_refused(bundle, r"(?i)override")

    def test_a_duplicate_member_in_the_override_document_is_refused(self):
        """PASSES, via `jcs.parse_bytes`. An override file whose raw JSON repeats
        a member has two readings, and the one a human reads need not be the one
        that was signed over. RFC 8785 3.1 forbids it; the predicate reads the
        file through the canonicalising parser rather than `json.load`, so the
        rule reaches the third signed artifact too."""
        bundle = self.bundle()
        with open(bundle.path("override.json"), "wb") as handle:
            handle.write(b'{"override":{"a":1},"override":{"b":2},'
                         b'"ownerSignature":"0x00"}')
        with self.assertRaises(jcs.CanonicalizationError):
            self._predicate(bundle)

    def test_an_under_or_over_determined_override_payload_is_refused(self):
        """PASSES. The §5.5 struct has exactly nine fields and the EIP-712 type
        string encodes all nine. A payload carrying a tenth cannot be hashed
        under that type string, and one missing a field cannot be hashed at all;
        `eip712.struct_hash` refuses both rather than hashing what it recognises
        and ignoring the rest. Staged as a post-signing edit because a struct
        that cannot be hashed cannot be signed either.

        The two shapes here are the ones that reach the hasher.
        `reviewReceiptHash`, `actionHash`, `mandateHash`, `policyHash`,
        `actionNonce`, `issuedAt` and `expiresAt` are indexed by
        `check_owner_override` before it hashes anything, so removing one of
        those is refused earlier and less legibly -- see
        `TestOverrideRefusalsAreDiagnosed`."""
        bundle = self.bundle()
        cases = (
            ("extra field", lambda doc: doc["override"].update(surprise="1")),
            ("missing reasonHash", lambda doc: doc["override"].pop("reasonHash")),
            ("missing schemaVersion",
             lambda doc: doc["override"].pop("schemaVersion")),
        )
        for label, post in cases:
            with self.subTest(shape=label):
                bundle.seal_override(post=post)
                self.assert_refused(bundle, r"(?i)OverrideAuthorizationPayload")

    def test_every_field_of_the_override_payload_is_required(self):
        """PASSES. Field by field, because a closed nine-field set enforced only
        in aggregate would drop the first omission. This asserts only that each
        removal is REFUSED; what the recipient is told about it is the separate
        question `TestOverrideRefusalsAreDiagnosed` puts."""
        bundle = self.bundle()
        for _, name in eip712.OVERRIDE_FIELDS:
            with self.subTest(missing=name):
                bundle.seal_override(post=lambda doc, n=name: doc["override"].pop(n))
                with self.assertRaises((ValueError, KeyError)):
                    self._predicate(bundle)


# ---------------------------------------------------------------------------
# The override binds to ONE exact action
# ---------------------------------------------------------------------------

class TestOverrideBindsToOneExactAction(OverrideTestCase):
    """`executeWithOverride` reverts `OverrideMismatch` unless the override names
    this exact review receipt, action hash, mandate hash, policy hash AND action
    nonce, with the contract's own reason recorded beside it:

        Any looser binding would let one override authorize a different action.

    Every override below is a GENUINE owner signature over a payload the owner
    could have produced. Only its aim is wrong. That is the whole attack: an
    owner who authorises one exception has authorised one exception."""

    def repoint(self, field, value):
        bundle = self.bundle()
        bundle.seal_override(mutate=lambda ov: ov.__setitem__(field, value))
        return bundle

    def test_an_override_repointed_to_another_action_is_refused(self):
        """PASSES. `auth.actionHash != T.hashAction(action)` -> OverrideMismatch."""
        self.assert_refused(self.repoint("actionHash", "0x" + "11" * 32),
                            r"(?i)override\.actionHash")

    def test_an_override_repointed_to_another_mandate_is_refused(self):
        """PASSES. `auth.mandateHash != action.mandateHash` -> OverrideMismatch.
        An override minted under one mandate must not authorise an action under
        another, even for the same target and value."""
        self.assert_refused(self.repoint("mandateHash", "0x" + "22" * 32),
                            r"(?i)override\.mandateHash")

    def test_an_override_repointed_to_another_policy_is_refused(self):
        """PASSES. `auth.policyHash != action.policyHash` -> OverrideMismatch.
        Policy is the half of the intersection that carries the failure mode, so
        an override that travels across a policy change is an override of a rule
        the owner never read."""
        self.assert_refused(self.repoint("policyHash", "0x" + "33" * 32),
                            r"(?i)override\.policyHash")

    def test_an_override_repointed_to_another_nonce_is_refused(self):
        """PASSES. `auth.actionNonce != action.actionNonce` -> OverrideMismatch.
        The nonce is the whole of the Vault's replay prevention (§3.3(9)), so an
        override that does not name one is an override of every future action."""
        self.assert_refused(self.repoint("actionNonce", "1"),
                            r"(?i)override\.actionNonce")

    def test_an_override_naming_another_review_receipt_is_refused(self):
        """PASSES. `auth.reviewReceiptHash != receiptHash` -> OverrideMismatch.
        This is the binding §5.5 exists for: the payload "carries
        `reviewReceiptHash` so the vault can require the matching review
        receipt"."""
        self.assert_refused(self.repoint("reviewReceiptHash", "0x" + "44" * 32),
                            r"(?i)override\.reviewReceiptHash")

    def test_an_override_naming_a_different_receipt_of_the_same_action(self):
        """PASSES, and it is the sharp version of the previous test.

        `0x44...44` is obviously not a receipt hash. Here the override names a
        REAL, correctly-formed §5.4 receipt hash -- the receipt from a bundle
        whose action is identical in every field the override checks except the
        nonce. Every hash in the credential is a hash of something that exists,
        and it still must not authorise this receipt."""
        other = self.bundle(seal=False)
        other.action["actionNonce"] = "1"
        other.seal()
        foreign = "0x" + eip712.receipt_struct_hash(other.receipt).hex()
        bundle = self.bundle().seal_override(
            mutate=lambda ov: ov.__setitem__("reviewReceiptHash", foreign))
        self.assert_refused(bundle, r"(?i)override\.reviewReceiptHash")

    def test_a_stale_override_is_not_revived_by_the_action_moving_on(self):
        """PASSES. The composite, and the most realistic replay: the owner signed
        an override for nonce 0, the action was re-issued at nonce 1, and the old
        credential is presented alongside it unchanged. Nothing about the
        override is forged; it is simply spent."""
        bundle = self.bundle()
        stale = bundle.override_doc()
        bundle.action["actionNonce"] = "1"
        bundle.seal()
        write_json(bundle.path("override.json"), stale)
        self.assert_refused(bundle, r"(?i)override\.(reviewReceiptHash|actionHash|actionNonce)")

    def test_the_same_bundle_at_another_nonce_certifies_when_resealed(self):
        """PASSES. The control for the test above: with the override re-signed
        for nonce 1, the identical bundle certifies. Without this, the refusal
        above could be the nonce itself being rejected rather than the stale
        binding."""
        bundle = self.bundle(seal=False)
        bundle.action["actionNonce"] = "1"
        bundle.seal().seal_override()
        self.assertEqual(self.assert_certifies(bundle)["actionNonce"], "1")


# ---------------------------------------------------------------------------
# The override is a credential the signer cannot mint
# ---------------------------------------------------------------------------

class TestOverrideAuthenticatesTheOwner(OverrideTestCase):
    """§3.3(2): the override must be "separately authenticated, unavailable to
    the agent". §3.3(7) makes it the one path where a human overrules the
    automatic decision. `executeWithOverride` enforces that with
    `digest.recover(ownerSig) != owner -> NotOwnerOverride`, against the Vault's
    own immutable `owner` -- not against anything the presenter supplies.

    The offline verifier's equivalent of "the Vault's immutable owner" is the
    deployment manifest's `owner`, which reaches it under a signature from an
    authority the CALLER named out of band. `ownerAddress` inside `override.json`
    is a SIBLING DECLARATION, outside the signed §5.5 payload -- A-058's finding
    on the legacy verifier, where an override minted by a key generated seconds
    earlier produced eleven consecutive [PASS] lines. Each test below is
    therefore run in three postures: declaring truthfully, declaring the owner's
    address falsely, and declaring nothing."""

    def setUp(self):
        super(TestOverrideAuthenticatesTheOwner, self).setUp()
        self._staged = None

    def signed_by(self, key, **kwargs):
        """One staged bundle per test method, re-signed per posture.

        `seal_override` starts from the pristine credential every call, so the
        three postures below cannot contaminate each other."""
        if self._staged is None:
            self._staged = self.bundle()
        return self._staged.seal_override(key=key, **kwargs)

    def test_an_override_minted_by_the_isolated_signer_is_refused(self):
        """PASSES. The §3.3(7) case that matters most: if the isolated signer
        could mint an override, the review verdict would be a credential the
        component it protects against can overrule. All three declaration
        postures are refused."""
        for label, kwargs in (
            ("truthful ownerAddress", {"owner_address": SIGNER}),
            ("declares the owner", {"owner_address": OWNER}),
            ("no ownerAddress", {"declare_owner": False}),
        ):
            with self.subTest(posture=label):
                self.assert_refused(self.signed_by(SIGNER_KEY, **kwargs),
                                    r"(?i)owner|signer")

    def test_the_signer_minted_guard_fires_when_owner_and_signer_coincide(self):
        """PASSES, and it is the only input that reaches
        `check_owner_override`'s explicit "recovers to the Sentinel signer"
        branch at all.

        In every ordinary deployment the owner-recovery comparison rejects a
        signer-minted override first, leaving the §3.3(7) branch behind it
        unexercised -- and an unexercised fail-closed branch is a branch nobody
        has established still works. A deployment that names ONE address as both
        owner and signer is refused by nothing else in the file: the manifest
        permits it, the mandate can be re-signed for it, and the receipt already
        names it. That is the configuration in which §3.3(7) is the last line,
        and this test is the evidence it holds."""
        payload = manifest_payload(owner=SIGNER)
        bundle = self.bundle(payload=payload, seal=False)
        bundle.mandate["principal"] = SIGNER
        bundle.owner_key = SIGNER_KEY
        bundle.seal().seal_override(key=SIGNER_KEY, owner_address=SIGNER)
        message = self.assert_refused(bundle, r"(?i)Sentinel signer")
        self.assertIn("3.3(7)", message)

    def test_an_override_minted_by_an_outsider_is_refused(self):
        """PASSES. The A-058 artifact, applied to the new arm: a perfectly valid
        signature from a key that is simply not the owner's. The declared
        `ownerAddress` is varied because it is the presenter's field -- a check
        that only compares the declaration to the manifest, without also
        comparing the RECOVERED address, would pass the middle posture."""
        for label, kwargs in (
            ("truthful ownerAddress", {"owner_address": OUTSIDER}),
            ("declares the owner", {"owner_address": OWNER}),
            ("no ownerAddress", {"declare_owner": False}),
        ):
            with self.subTest(posture=label):
                self.assert_refused(self.signed_by(OUTSIDER_KEY, **kwargs),
                                    r"(?i)owner")

    def test_the_recovered_address_is_checked_and_not_only_the_declaration(self):
        """PASSES. Stated as its own assertion because the two checks answer
        different questions and a repair could keep one. The refusal for an
        outsider signature that DECLARES the owner's address must name the
        recovered signer, not the declaration -- if it named the declaration, the
        declaration is all that was compared."""
        message = self.assert_refused(
            self.signed_by(OUTSIDER_KEY, owner_address=OWNER), r"(?i)recovered")
        self.assertIn(OUTSIDER.lower(), message.lower())

    def test_an_override_signed_under_a_foreign_domain_is_refused(self):
        """PASSES. The EIP-712 domain binds chain and vault. An override the
        owner really signed, for the same nine field values, under another
        deployment's domain separator, must not authenticate here -- otherwise a
        credential harvested from a testnet vault authorises the mainnet one.
        The Vault gets this from `_domainSeparator()` being computed from
        `block.chainid` and `address(this)`; the verifier gets it from the
        manifest."""
        for label, change in (("chainId", {"chainId": "1"}),
                              ("verifyingContract",
                               {"verifyingContract": "0x" + "11" * 20})):
            with self.subTest(field=label):
                bundle = self.bundle()
                foreign = dict(domain_of(bundle.payload), **change)
                bundle.seal_override(domain=foreign)
                self.assert_refused(bundle, r"(?i)recovered owner override")

    def test_an_override_for_a_bundle_whose_manifest_names_another_owner(self):
        """PASSES. The trust root moves, not the credential. The same shipped,
        genuine, owner-signed override is presented under a manifest naming a
        different owner; the authority signed that manifest, so nothing about it
        is forged. It must not certify, because the manifest's owner is the only
        thing standing in for the Vault's immutable `owner`."""
        bundle = self.bundle(payload=manifest_payload(owner=OUTSIDER))
        self.assert_refused(bundle, r"(?i)owner|principal")


# ---------------------------------------------------------------------------
# The override's validity window
# ---------------------------------------------------------------------------

class TestOverrideWindow(OverrideTestCase):
    """`executeWithOverride` runs three separate window checks in this order:

        auth.issuedAt >= auth.expiresAt      -> InvalidValidityWindow
        block.timestamp <  auth.issuedAt     -> OverrideNotYetValid
        block.timestamp >= auth.expiresAt    -> OverrideExpired

    Three errors, not one, because they are three different owner mistakes. The
    window is half-open at both ends and both ends are asserted: an off-by-one
    here silently extends every human authorization by a second, and the whole
    point of a bounded override window is that a one-time exception does not
    become standing permission."""

    def window(self, issued, expires):
        return self.bundle().seal_override(
            mutate=lambda ov: ov.update(issuedAt=str(issued),
                                        expiresAt=str(expires)))

    def test_an_override_whose_window_has_not_opened_is_refused(self):
        """PASSES. OverrideNotYetValid. A post-dated authorization is not a
        current one, and the owner may have signed it precisely so that it is
        not yet usable."""
        self.assert_refused(self.window(NOW + 3600, NOW + 7200),
                            r"(?i)owner override requires issuedAt")

    def test_an_expired_override_is_refused(self):
        """PASSES. OverrideExpired."""
        self.assert_refused(self.window(0, NOW - 1),
                            r"(?i)owner override requires issuedAt")

    def test_the_override_window_is_half_open_at_the_top(self):
        """PASSES. `block.timestamp >= auth.expiresAt` is exclusive: AT
        `expiresAt` the override is over, not still live for one more second."""
        self.assert_refused(self.window(0, NOW),
                            r"(?i)owner override requires issuedAt")

    def test_the_override_window_is_inclusive_at_the_bottom(self):
        """PASSES. `block.timestamp < auth.issuedAt` is exclusive the other way:
        AT `issuedAt` the override is already live. Asserted as an ACCEPTANCE, so
        that a repair which fixes the top boundary by tightening both ends is
        caught."""
        self.assert_certifies(self.window(NOW, NOW + 10))

    def test_an_empty_override_window_is_refused(self):
        """PASSES. InvalidValidityWindow, reported as its own condition rather
        than folded into the currency check -- `issuedAt == expiresAt` is an
        authorization that was never valid at any instant, which is a different
        thing for a recipient to be told than "expired"."""
        message = self.assert_refused(self.window(500, 500),
                                      r"(?i)empty validity window")
        self.assertNotRegex(message, r"(?i)expired")

    def test_an_inverted_override_window_is_refused(self):
        """PASSES. The same guard from the other side."""
        self.assert_refused(self.window(NOW + 10, NOW),
                            r"(?i)empty validity window")

    def test_the_override_window_is_bounded_to_uint64(self):
        """PASSES. `issuedAt` and `expiresAt` are uint64 in the §5.5 struct, and
        a value above that ceiling cannot be what the owner signed under the
        published type string. Staged as a post-signing edit because
        `eip712.parse_uint` refuses to hash it in the first place -- that refusal
        IS the property."""
        bundle = self.bundle()
        for value in (str(2 ** 64), "0123", "-1", "0x10", ""):
            with self.subTest(expiresAt=value):
                bundle.seal_override(
                    post=lambda doc, v=value: doc["override"].update(expiresAt=v))
                with self.assertRaises((ValueError, KeyError)):
                    self._predicate(bundle)


# ---------------------------------------------------------------------------
# Signature canonical form
# ---------------------------------------------------------------------------

class TestOverrideSignatureCanonicalForm(OverrideTestCase):
    """R-A018-16(a). `verify.py` holds the override to EIP-2 low-s with
    `v in {27,28}` and records why: §5.8 gives the override the same construction
    as the receipt, so there is no basis in §5 for one rule on one and none on
    the other. The new arm routes the override through the same
    `check_signature_form` the manifest and receipt now use; these tests are what
    say so rather than assume it."""

    def test_a_malleated_override_signature_recovers_the_same_owner(self):
        """PASSES, because it is a fact about ECDSA rather than about this code.
        Recorded first so the next test cannot be read as a test of signature
        parsing: the reflected form is a DIFFERENT 65 bytes that authenticates
        identically."""
        from secp256k1 import recover_address
        bundle = self.bundle().seal_override()
        doc = bundle.override_doc()
        digest = eip712.override_digest(domain_of(bundle.payload), doc["override"])
        reflected = malleated(doc["ownerSignature"])
        self.assertNotEqual(reflected, doc["ownerSignature"])
        self.assertEqual(recover_address(digest, reflected).lower(), OWNER.lower())

    def test_a_high_s_override_signature_is_refused(self):
        """PASSES. Two byte-distinct documents carrying one owner decision means
        an override has no unique identity, and §3.3(2) requires the override to
        be LOGGED -- `OverrideAuthorized` is keyed on `overrideHash`, so an
        auditor reconciling the log against presented credentials would see one
        hash and two authorizations claiming it."""
        bundle = self.bundle().seal_override(malleate=True)
        self.assert_refused(bundle, r"(?i)low-s|canonical|EIP-2|malleab")

    def test_an_override_signature_with_v_outside_27_28_is_refused(self):
        """PASSES. `ECDSA.recover` in the Vault rejects anything else; an offline
        verifier that silently normalised 0/1 to 27/28 would certify a credential
        the Vault will not accept."""
        bundle = self.bundle()
        for v in (0, 1, 26, 29, 255):
            with self.subTest(v=v):
                bundle.seal_override(force_v=v)
                self.assert_refused(bundle, r"(?i)v=%d|v in" % v)

    def test_a_malformed_override_signature_is_refused_by_shape(self):
        """PASSES. Wrong length or non-hex must be a named refusal, not a
        `ValueError` from `bytes.fromhex` escaping with no subject."""
        bundle = self.bundle()
        for bad in ("0x" + "11" * 64, "0x" + "11" * 66, "0xzz", "0x", ""):
            with self.subTest(signature=bad):
                bundle.seal_override(
                    post=lambda doc, b=bad: doc.update(ownerSignature=b))
                self.assert_refused(bundle, r"(?i)owner override signature")


# ---------------------------------------------------------------------------
# An override excuses the verdict and nothing else
# ---------------------------------------------------------------------------

class TestOverrideDoesNotExcuseTheAction(OverrideTestCase):
    """The question D-052(b) made mandatory: which checks does this path skip?

    `executeWithOverride` runs `_checkAction` and `_checkReceipt` FIRST, before
    it looks at the verdict or the override at all. So an owner override buys
    exactly one thing -- a REVIEW verdict becomes executable -- and buys nothing
    else. It does not widen the mandate, does not revive an expired receipt, and
    does not authorise a different call.

    That is worth asserting rather than assuming, because "the owner personally
    approved it" is the most natural place for a verifier to start skipping
    checks, and every bundle below carries a genuine, current, correctly bound
    owner override."""

    def staged(self, mutate):
        bundle = self.bundle(seal=False)
        mutate(bundle)
        bundle.seal().seal_override()
        return bundle

    def test_an_override_does_not_authorise_a_non_mandated_target(self):
        """PASSES. `_checkAction` reverts `TargetNotAllowed` before the override
        is read. The owner's override says "execute this reviewed action", not
        "execute anything"."""
        self.assert_refused(
            self.staged(lambda b: b.action.update(target="0x" + "11" * 20)),
            r"(?i)target")

    def test_an_override_does_not_lift_the_mandate_value_ceiling(self):
        """PASSES. `_checkAction` reverts `ValueOverCap`. The ceiling is in the
        owner-signed mandate; an override of a review verdict is not an
        amendment to the mandate."""
        self.assert_refused(
            self.staged(lambda b: b.action.update(
                valueWei=str(int(b.mandate["maxNativeValueWei"]) * 100000))),
            r"(?i)value|wei|ceiling|maxNative")

    def test_an_override_does_not_lift_the_policy_value_ceiling(self):
        """PASSES. Asserted separately from the mandate ceiling because they are
        two distinct limits and a repair could enforce one and not the other."""
        def mutate(b):
            ceiling = int(b.policy["maxNativeValueWei"])
            b.mandate["maxNativeValueWei"] = str(ceiling * 1000000)
            b.action["valueWei"] = str(ceiling * 100000)
        self.assert_refused(self.staged(mutate),
                            r"(?i)value|wei|ceiling|policy")

    def test_an_override_does_not_authorise_another_selector(self):
        """PASSES. `_checkAction` reverts `SelectorNotAllowed`."""
        self.assert_refused(
            self.staged(lambda b: b.action.update(
                callData="0xdeadbeef" + b.action["callData"][10:])),
            r"(?i)selector")

    def test_an_override_does_not_authorise_another_operation(self):
        """PASSES. `_checkAction` reverts `UnsupportedOperation` for anything
        that is not CALL, and DELEGATECALL has a categorically different blast
        radius."""
        self.assert_refused(
            self.staged(lambda b: b.action.update(operation="1")),
            r"(?i)operation")

    def test_an_override_does_not_revive_expired_credentials(self):
        """PASSES. `_checkReceipt` reverts `ReceiptExpired` and `_checkAction`
        reverts `MandateExpired` / `ActionExpired`, all before the override's own
        window is even parsed. A current override over a dead receipt is the
        exact shape a presenter would reach for, since the override is the one
        document the owner can re-sign at will."""
        cases = (
            ("expired receipt", lambda b: b.receipt.update(
                issuedAt=str(NOW - 1000), expiresAt=str(NOW - 1)),
             r"(?i)receipt requires issuedAt"),
            ("expired mandate", lambda b: b.mandate.update(
                validAfter="0", validUntil=str(NOW - 1)),
             r"(?i)mandate is not current"),
            ("expired policy", lambda b: b.policy.update(
                validAfter="0", validUntil=str(NOW - 1)),
             r"(?i)policy"),
            ("passed deadline", lambda b: b.action.update(deadline=str(NOW - 1)),
             r"(?i)deadline"),
        )
        for label, mutate, subject in cases:
            with self.subTest(case=label):
                self.assert_refused(self.staged(mutate), subject)

    def test_an_override_does_not_excuse_an_unapproved_receipt_signer(self):
        """PASSES. `_checkReceipt` reverts `WrongSigner`. §3.3(7) requires BOTH a
        signed REVIEW receipt from the active signer AND the owner's override --
        the override is an additional credential, never a substitute for the
        first one."""
        def mutate(b):
            b.signer_key = OUTSIDER_KEY
        self.assert_refused(self.staged(mutate), r"(?i)signer")


# ---------------------------------------------------------------------------
# The declared entry point is part of the claim
# ---------------------------------------------------------------------------

class TestExecutionPathInterface(OverrideTestCase):
    """`--execution-path` decides which Vault function the result is a statement
    about. A recipient reading a PASS has to be able to tell which."""

    def test_an_unknown_execution_path_fails_closed(self):
        """PASSES. `verify()` is importable and is called directly by this
        suite and by anything else that embeds the predicate, so the argparse
        `choices=` list is not the only gate. An unrecognised path must refuse
        rather than fall back to the automatic arm."""
        for path in ("whatever", "", None, "AUTOMATIC", "override"):
            with self.subTest(path=path):
                self.assert_refused(self.bundle(), r"(?i)unknown execution path",
                                    execution_path=path)

    def test_the_cli_rejects_an_unknown_execution_path(self):
        """PASSES. argparse's own gate, asserted so a later refactor to a free
        string is visible."""
        completed = self.cli(self.bundle(),
                             extra=["--execution-path", "nonsense"])
        self.assertEqual(completed.returncode, 2)
        self.assertIn("invalid choice", completed.stderr)

    def test_the_execution_path_control_is_documented_in_help(self):
        """PASSES. R-A018-03's lesson generalised: a caller-facing switch that
        changes what the verifier certifies must not be concealed from `--help`.
        A recipient who cannot see that two entry points exist cannot know which
        one the result they were handed is about."""
        completed = subprocess.run(
            [sys.executable, PREDICATE, "--help"], capture_output=True, text=True)
        self.assertIn("--execution-path", completed.stdout)
        self.assertIn(OVERRIDE, completed.stdout)

    def test_the_result_payload_names_the_path_and_the_credential(self):
        """PASSES. The machine-readable half of the claim: a result produced on
        the override arm must say so and must name the §5.5 credential it
        authenticated, or two runs over the same bundle at two entry points are
        indistinguishable after the fact."""
        automatic = self.assert_certifies(self.bundle(ALLOW_CASE))
        override = self.assert_certifies(self.bundle())
        self.assertEqual(automatic["executionPath"], AUTOMATIC)
        self.assertNotIn("ownerOverrideHash", automatic)
        self.assertEqual(override["executionPath"], OVERRIDE)
        self.assertIn("ownerOverrideHash", override)

    # `case-1-allow` has to be verified on the automatic arm; the helper above
    # defaults to the override arm for everything else.
    def assert_certifies(self, bundle, **kwargs):
        if os.path.basename(bundle.dir) == ALLOW_CASE:
            kwargs.setdefault("execution_path", AUTOMATIC)
        return self._predicate(bundle, **kwargs)


# ---------------------------------------------------------------------------
# DEFECTS FOUND IN THE NEW ARM
# ---------------------------------------------------------------------------

class TestTheCertifyingRunSaysWhichPathItCertified(OverrideTestCase):
    """R-A018-08 -- claims match behaviour. EXTENSION: the register's table does
    not carry this row, because the sentence in question was written for the
    automatic arm only.

    The override arm reuses the automatic arm's PASS line verbatim. A certifying
    override run prints:

        PASS (static, offline): the deployment manifest authenticates under the
        out-of-band authority; the mandate is the owner's; the signer's decision
        is REVIEW; and the action matches the mandate and policy.

    Nothing in that sentence is false. What it omits is the entire reason the run
    passed: that a SEPARATE owner override was presented and authenticated, and
    that the Vault will refuse this bundle at `executeWithReceipt`. The same
    sentence with one word changed is printed for an ordinary ALLOW, so the two
    outcomes a reader most needs to tell apart -- "the machine approved this" and
    "the machine asked for a human and a human signed" -- are reported
    identically outside the JSON.

    §3.3(2) singles out override as the thing that must be LOGGED, and D-043
    added `OverrideAuthorized` on-chain for exactly this reason: "an auditor
    reconstructing history from the log could see THAT an override happened and
    never which owner authorization permitted it". The offline verifier's
    headline is the same artifact for a recipient who reads one line."""

    def test_the_certifying_headline_names_the_owner_override(self):
        """FAILS -- EXTENSION (R-A018-08 shape, register row not present).

        Contract: if a run certifies on the override arm, its human-readable
        headline must say an owner override was authenticated. The JSON payload
        already carries `executionPath` and `ownerOverrideHash`; this is about
        the line a recipient actually reads."""
        completed = self.cli(self.live_bundle(),
                             extra=["--execution-path", OVERRIDE])
        self.assertEqual(completed.returncode, 0,
                         "positive control broken:\n" + completed.stderr)
        headline = completed.stdout.splitlines()[0]
        self.assertRegex(
            headline, r"(?i)override",
            "a certifying override run's headline does not mention the owner "
            "override that is the only reason it passed: " + repr(headline))

    def test_the_certifying_headline_does_not_read_as_an_automatic_pass(self):
        """FAILS -- EXTENSION, the same defect from the recipient's side.

        The headline for a REVIEW-plus-override run and the headline for an
        ordinary ALLOW run must not differ only in the verdict word. A reader
        skimming a release packet cannot be expected to notice that "REVIEW"
        where they expected "ALLOW" means a human signed an exception."""
        review = self.cli(self.live_bundle(),
                          extra=["--execution-path", OVERRIDE])
        allow = self.cli(self.live_bundle(ALLOW_CASE))
        self.assertEqual(review.returncode, 0, review.stderr)
        self.assertEqual(allow.returncode, 0, allow.stderr)
        review_line = review.stdout.splitlines()[0].replace("REVIEW", "@")
        allow_line = allow.stdout.splitlines()[0].replace("ALLOW", "@")
        self.assertNotEqual(
            review_line, allow_line,
            "an owner-override certification and an automatic certification "
            "print the same headline modulo the verdict word")


class TestAnUnexaminedOverrideCredentialIsNotCertifiable(OverrideTestCase):
    """EXTENSION -- not in register §1, and the same defect D-052(b) already
    repaired one module over.

    `check_owner_override()` is called ONLY when `execution_path` is
    `owner-override`. On the automatic arm the predicate never opens
    `override.json`, so an ALLOW bundle can carry a signed §5.5 authorization
    minted by an arbitrary key and the run prints PASS with that credential
    unexamined.

    `verify.py` rules that shape uncertifiable and says why, at the site:

        override.json is present beside a signed refusal record. A refusal and an
        authorization in one bundle is not a certifiable claim -- §0 refuses the
        same shape for a receipt. Nothing on this path examines the override, so
        accepting it would certify a §5.5 credential that was never verified.

    and its `_override_checks` runs on EVERY bundle that carries the file,
    including this one -- measured: the legacy verifier refuses an ALLOW bundle
    with an override grafted onto it, on `override targets a REVIEW receipt, not
    a BLOCK (§5.5)`.

    The Vault agrees that the credential is not executable: `executeWithReceipt`
    takes no override parameter and `executeWithOverride` reverts
    `NotReviewVerdict` on an ALLOW receipt. So the bundle presents an
    authorization that no Vault entry point will accept, and the publication
    verifier certifies it without comment."""

    def allow_bundle_carrying_an_override(self, key):
        bundle = self.bundle(ALLOW_CASE, seal=False)
        bundle.seal().graft_override().seal_override(
            key=key, owner_address=address_of(key))
        return bundle

    def test_an_allow_bundle_carrying_an_outsider_override_is_refused(self):
        """FAILS -- EXTENSION.

        The credential here is real: a genuine secp256k1 signature over a §5.5
        payload correctly bound to THIS bundle's receipt, action, mandate, policy
        and nonce -- minted by a key that is not the owner's. Presented on the
        automatic arm it is never opened, and the bundle certifies.

        Contract: either the override is examined on every path that certifies a
        bundle, or a bundle carrying an override the declared path cannot use is
        refused as not-a-certifiable-claim. Which of the two is a scope decision
        and is not a test author's call; that neither happens is the defect."""
        bundle = self.allow_bundle_carrying_an_override(OUTSIDER_KEY)
        self.assert_refused(bundle, r"(?i)override",
                            execution_path=AUTOMATIC)

    def test_the_owner_signed_case_is_refused_too_or_examined(self):
        """FAILS -- EXTENSION, the narrower half.

        Even when the override is the OWNER's, it is bound to a REVIEW that this
        bundle does not contain, and §5.5 says an override targets a review
        receipt. An ALLOW bundle carrying one is either a packaging error or a
        substitution attempt; certifying it silently is neither reading it nor
        refusing it."""
        bundle = self.allow_bundle_carrying_an_override(OWNER_KEY)
        self.assert_refused(bundle, r"(?i)override",
                            execution_path=AUTOMATIC)


class TestOverrideRefusalsAreDiagnosed(OverrideTestCase):
    """R-A018-16(c) -- "a field error is reported as a field error". EXTENSION
    for this arm: the register item was written about `deployment.py`, and the
    same discipline was not carried into `check_owner_override`.

    Both tests below concern a bundle that IS correctly refused. What is wrong is
    what the recipient is told. In a tool whose entire value is telling an
    unaided reader what went wrong, a refusal that names neither the file nor the
    field is an inherited-Critical-2 concern, and `check_verdict` -- added in the
    same batch, twenty lines away -- already does it right:

        receipt.verdict '...' is not a canonical uint8: ...
    """

    def test_a_structurally_incomplete_override_names_the_override(self):
        """FAILS -- EXTENSION.

        `check_owner_override` indexes `override["reviewReceiptHash"]` directly
        after checking only that `override` is a dict, so an override payload
        missing its bindings escapes as a bare `KeyError`. Measured at the CLI:

            FAIL: 'reviewReceiptHash'

        That is fail-closed -- `main()` catches `KeyError` and exits 1 -- and it
        is all it is. The recipient is not told which file, which artifact, or
        that a §5.5 override was even involved. The sibling artifact
        `mandate-signature.json` gets an explicit shape check ("has an unexpected
        shape"); `override.json` gets none."""
        bundle = self.bundle()
        write_json(bundle.path("override.json"),
                   {"override": {"schemaVersion": "1"},
                    "ownerSignature": "0x" + "11" * 65})
        self.assert_refused(bundle, r"(?i)override")

    def test_a_non_canonical_override_time_field_names_the_override(self):
        """FAILS -- EXTENSION.

        `check_owner_override` calls `eip712.parse_uint` on `issuedAt` and
        `expiresAt` outside any try/except, so the refusal is the encoder's:

            FAIL: uint64 value '0123' is not a canonical decimal string; ...

        Correct, and unattributed. Nothing in it says the value came from the
        owner override rather than from the receipt, the mandate, the policy or
        the action -- every one of which also carries uint64 time fields."""
        bundle = self.bundle().seal_override(
            post=lambda doc: doc["override"].update(issuedAt="0123"))
        self.assert_refused(bundle, r"(?i)override")


# ---------------------------------------------------------------------------
# Coverage bookkeeping
# ---------------------------------------------------------------------------

class TestTheOverrideArmIsNowCovered(unittest.TestCase):
    """R-A018-01's final clause turned into something that fails if it regresses.

    Before this file, `grep -l "execution.path\\|override" verifier/test_*.py`
    matched `test_verifier.py` (the legacy arm) and `test_publication_verifier.py`
    (only in prose, describing what a REVIEW receipt would need). Nothing
    supplied `--execution-path owner-override` to the publication predicate and
    nothing opened its `override.json`."""

    def test_the_override_arm_entry_points_exist_as_named(self):
        """The contract's vocabulary, pinned. If `check_owner_override` is
        renamed or the path constants change, the tests above would start
        passing vacuously against a different function."""
        self.assertTrue(callable(verify_publication.check_owner_override))
        self.assertTrue(callable(verify_publication.check_verdict))
        self.assertEqual(verify_publication.OVERRIDE_PATH, "owner-override")
        self.assertEqual(verify_publication.AUTOMATIC_PATH, "automatic")

    def test_the_sibling_suite_still_does_not_exercise_the_override_arm(self):
        """NOT A TRIPWIRE, and the measurement R-A018-01's final clause rests on.

        The sibling suite names the override path only in prose and in one
        `assertFalse(os.path.exists(... "override.json"))` -- it asserts the file
        is ABSENT and never reads one. It never passes `execution_path` to the
        predicate, so every one of its 81 tests runs on the automatic arm and the
        second arm shipped uncovered. If this fails because someone added real
        override coverage there, that is a good change and this bookkeeping test
        is the thing that should go."""
        with open(os.path.join(os.path.dirname(PREDICATE),
                               "test_publication_verifier.py"),
                  encoding="utf-8") as handle:
            source = handle.read()
        self.assertNotIn("execution_path", source)
        self.assertNotIn("--execution-path", source)
        self.assertNotIn('read_json(bundle.path("override.json"))', source)

    def test_the_review_fixture_is_the_only_corpus_bundle_with_a_credential(self):
        """Records the coverage boundary. Every override negative in this file is
        staged from one fixture, because it is the only one that ships a §5.5
        credential. A second REVIEW fixture would be worth having."""
        with_override = [
            name for name in sorted(os.listdir(SAMPLES))
            if os.path.isfile(os.path.join(SAMPLES, name, "override.json"))]
        self.assertEqual(with_override, [REVIEW_CASE])


if __name__ == "__main__":
    unittest.main(verbosity=2)
