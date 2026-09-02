#!/usr/bin/env python3
"""Adversarial tests for the three CONTENT arms the publication predicate does not have.

    python3 verifier/test_publication_conformance.py
    python3 -m unittest discover -s verifier -v

WHY THIS FILE EXISTS
--------------------
`docs/check-inventory-diff-2026-08-31.md` diffed `verify.py` (A, 95 checks) against
`verify_publication.py` (B) and found 54 checks ABSENT with zero recorded reason. Three
of its families are ruled INTO the Cycle 2 candidate by D-087 and are this file's
subject:

  O2  the §5.6 evidence-projection arm (`verify.py::_evidence_describes_the_bundle`
      plus the anchor / verdict agreement checks in `_chain_checks`) -- the diff's
      SEVERITY-1 cell. B hashes `evidence.json` and never opens it: `normalizedAction`,
      `expectedEffects` and `anchor` have zero occurrences in B, so `evidence.json`
      replaced wholesale with `{"note": "this bundle's evidence says nothing at all"}`,
      re-canonicalised, re-hashed and re-signed, CERTIFIES. B authenticates that the
      evidence is THE bundle the signer signed over and never that it DESCRIBES THIS
      ACTION.
  O4  the reason-code arm (`verify.py::_reason_code_checks`). `receipt.reasonCodesHash`
      commits to a published list B never reads, so the codes a recipient is shown can
      be swapped freely.
  §5.7.1  the signer-attested-record conformance check
      (`verify.py::_allow_conforms_to_the_mandate`), added by D-087(b) AND NAMED
      PRECISELY -- see "THE NAME", below.

D-058(1) AND A-028: WHO WROTE THIS, AND WHAT THAT BUYS
------------------------------------------------------
Written by an independent test author, forbidden to edit any verifier module and any
existing test file, against the frozen baseline `2115c4f`. Every negative below FAILS on
that baseline BY DESIGN: it is the statement of what the predicate must do, written
before and independently of the implementation that will satisfy it. Nothing in
`verify_publication.py`'s comments was taken as authority; `verify.py`'s three functions
were read as the specification because they are the checks being ported.

THE SPECIFICATION, IN THE ORDER IT WAS CONSULTED
------------------------------------------------
1. `docs/decisions.md` D-087 -- the authorisation, and (b)'s naming rule.
2. `docs/check-inventory-diff-2026-08-31.md` §1, §3, §7 -- the eight scenarios, the
   staging warning, and where a seventh instance would hide.
3. `verify.py::_evidence_describes_the_bundle`, `_reason_code_checks`,
   `_allow_conforms_to_the_mandate`, and the anchor / verdict tail of `_chain_checks`.
4. `verifier/reasoncodes.py` -- the §5.4 grammar and the delimiter collision it documents.
5. `test_publication_verifier.py` -- `Bundle`, the signing helpers, and the house
   assertion pattern (a refusal must NAME its subject).

THE STAGING NOTE THAT DECIDED THIS FILE'S SHAPE
-----------------------------------------------
The diff's §3 says, in bold: `Bundle.seal` does not resync the §5.6 projections, and the
first run produced THREE FALSE POSITIVES from that. `Bundle.seal()` rebuilds policy ->
mandate -> action -> receipt and re-signs, but `evidence.json` is copied verbatim -- so
the moment a test moves any document (every live-clock bundle moves five), the shipped
`normalizedAction` no longer restates the action and the shipped `expectedEffects` no
longer projects the mandate, and a faithful port of A REFUSES THE CONTROL. Every
negative here would then be "refused for the reason under test" while the control is
refused for the same reason, and the file would prove nothing.

`ConformanceBundle.seal()` therefore re-seals the WHOLE chain INCLUDING the projections:
it derives `normalizedAction`, `expectedEffects` (with the §5.2 intersected ceiling),
`anchor` and `verdict` from the sealed documents exactly as A defines them, re-derives
`receipt.reasonCodesHash` from the published list, applies the ONE mutation under test
AFTER that resync, rewrites the three evidence artifacts, and re-signs the receipt over
the final `evidenceHash`. `TestConformanceControl` shows the resync is a byte-for-byte
no-op on every shipped fixture and that an unmutated re-sealed bundle still certifies
-- in-process, at the CLI, and on the override path.

THE NAME (D-087(b)), AND WHY THIS FILE ENFORCES IT
--------------------------------------------------
The §5.7.1 check compares the signer's ATTESTED DECODED RECORD -- `resourceId`,
`beneficiary`, `durationSeconds`, `recurringAllowed`, `spender`, the allowance ceiling --
against the mandate, WITHOUT decoding calldata. It catches a misconfigured-but-honest
evaluator. It honestly does not catch a lying signer, because the record it reads is the
signer's own. John ruled the check is named

    "signer-attested record conforms to mandate"

and NEVER "beneficiary verified", and that its output must say what it does not catch.
`TestTheCheckIsNamedPrecisely` pins all three on the refusal message and on the
certifying output, and every §5.7.1 negative routes through
`assert_refused_by_the_conformance_check`, which applies the same rule. The standing
pattern D-087 records -- carry the honest version, name it precisely, never let the name
claim more than the check establishes -- is the rule these assertions execute.

WHAT IS DELIBERATELY NOT TESTED HERE
------------------------------------
* CALLDATA DECODING. D-083(b) ruled the publication verifier decodes nothing, and
  D-087(b) does not reverse it. No test here reads or rewrites the argument words of
  `callData`; the permanently-red sibling test is that ruling's record and is not
  duplicated or contradicted. `test_the_certifying_output_still_discloses_that_calldata_
  is_not_decoded` pins that the port leaves the disclosure standing.
* The §5.5.1 refusal path that `_evidence_describes_the_bundle` also runs on in A.
  D-087(d) rules refusal bundles are RECOGNISED AND REFUSED, not verified.
* A's "no mandate.json to compare against" branch: B `required()`s the mandate before
  any content check can run, so the branch is unreachable here.
* A's advisory "published list is in canonical order" Check is `skipped=True` and cannot
  fail; it is carried as a CONTROL (a non-canonical, correctly committed list must still
  certify), not as a negative.
* A tolerates an individual field ABSENT from an otherwise-present `expectedEffects`
  (`if name in expected`). That tolerance is neither pinned nor forbidden here.

KNOWN BLIND SPOTS
-----------------
* Conformance binds to ALLOW only, as in A ("BLOCK and REVIEW bundles are legitimately
  nonconforming and MUST stay verifiable"). `test_a_review_bundle_with_a_nonconforming_
  record_still_certifies_by_override` pins that. Whether the OVERRIDE path should
  require conformance of the attested record is a product question this file does not
  answer -- it ports A, and says so.
* Nothing here reads a chain, so `anchor` is compared to the receipt's own block fields,
  never to a real block.
"""

import os
import re
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import eip712  # noqa: E402
import jcs  # noqa: E402
import reasoncodes  # noqa: E402
import verify_publication  # noqa: E402
from keccak import keccak256  # noqa: E402

# Imported, never restated (see `test_publication_override.py` for the reasoning: a
# second copy of the staging helper is a second thing to drift, and a second copy of a
# test key is a second thing for R-A018-12's guard to find).
from test_publication_verifier import (  # noqa: E402
    AUTHORITY, AUTHORITY_KEY, Bundle, NOW, PREDICATE, PublicationTestCase, SAMPLES,
    read_json, write_json,
)
# The override sibling's `seal_override()` re-points a §5.5 credential at a re-sealed
# receipt and re-signs it as the owner. Needed here because `receipt.evidenceHash` is a
# receipt FIELD: any evidence mutation on the REVIEW fixture moves the receipt's struct
# hash, and the shipped credential would then be refused for `reviewReceiptHash` -- the
# A-056 failure mode one artifact further down -- before the content check under test
# was ever reached. Imported, not restated; its own controls prove it reproduces the
# shipped credential exactly.
from test_publication_override import OverrideBundle  # noqa: E402

AUTOMATIC = verify_publication.AUTOMATIC_PATH
OVERRIDE = verify_publication.OVERRIDE_PATH

ALLOW_CASE = "case-1-allow"
REVIEW_CASE = "case-4-review-failmode-review"
BLOCK_WRONG_PURPOSE_CASE = "case-3-wrong-purpose-block"

# SentinelTypes.sol: enum Verdict { BLOCK, REVIEW, ALLOW }. Restated rather than imported
# so this file does not agree with the module under test by construction.
VERDICT_NAMES = {0: "BLOCK", 1: "REVIEW", 2: "ALLOW"}

# The §5.6 `expectedEffects` fields A copies from the mandate. `maxAllowanceIncreaseBaseUnits`
# comes from the policy and `maxNativeValueWei` is the §5.2 intersection; both are derived
# in `sync_projections`.
EXPECTED_EFFECTS_FROM_MANDATE = (
    "target", "selector", "resourceId", "beneficiary", "durationSeconds", "recurringAllowed",
)

# D-087(b), verbatim. The check's name, matched case-insensitively and nowhere else relaxed.
CHECK_NAME = "signer-attested record conforms to mandate"
CHECK_NAME_RE = re.compile(re.escape(CHECK_NAME), re.I)
# The name the ruling forbids, in the spellings a sentence would naturally produce.
FORBIDDEN_NAME_RE = re.compile(r"beneficiary\s+(?:is\s+|was\s+|has\s+been\s+)?verified", re.I)
# The ruling's own words for what the check does not establish.
LYING_SIGNER_RE = re.compile(r"lying signer", re.I)
# D-083(b), which D-087(b) does not reverse: the output must still say calldata is not decoded.
NOT_DECODED_RE = re.compile(
    r"nothing here decodes|not decoded|never decoded|decodes nothing|does not decode", re.I)

# The refusals a broken staging would produce. Every content negative asserts its refusal
# does NOT match these, so a stale hash or signature -- the A-056 failure mode -- is
# reported as a staging defect rather than mistaken for the check under test firing.
STAGING_FAULT_RE = re.compile(
    r"^evidence\.hash: |^receipt\.evidenceHash: |canonicalization mismatch|"
    r"signature verification failed|^recovered |^override\.")

OTHER_ADDRESS = "0x000000000000000000000000000000000000dead"
FABRICATED_HASH = "0x" + "fa" * 32
APPROVE_SELECTOR = "0x095ea7b3"


def word(value):
    """One ABI word: a 0x-hex address or a decimal uint, left-padded to 32 bytes."""
    if isinstance(value, str) and value.startswith("0x"):
        return value[2:].lower().rjust(64, "0")
    return "%064x" % int(value)


class ConformanceBundle(OverrideBundle):
    """`Bundle`, plus the half of the bundle `Bundle.seal()` leaves stale.

    See the module docstring's staging note. `seal()` here takes two hooks:

      documents(b)  runs BEFORE the chain is sealed -- for a test that moves a
                    mandate, policy or action field and needs the projections to
                    FOLLOW it (the divergent-ceiling and approve-schema tests);
      evidence(b)   runs AFTER the projections are resynced -- for the one fault
                    under test, applied to `b.evidence`, `b.receipt_doc` or
                    `b.receipt` so it survives into what is signed and written.

    Both `Bundle.seal()` calls and the `seal_override()` that follows them on a bundle
    carrying a §5.5 credential are the imported helpers; nothing about the chain, the
    credential or the signatures is re-implemented here.
    """

    def __init__(self, case, root, payload=None):
        OverrideBundle.__init__(self, case, root, payload=payload)
        self.evidence = read_json(self.dir, "evidence.json")

    def sync_projections(self):
        """Derive every §5.6 projection and the reason-code commitment from the documents.

        The derivations are A's own, restated: `normalizedAction` is the §5.3 ActionPayload
        verbatim plus `callData`; `expectedEffects` is six mandate fields, one policy field,
        and the LOWER of the two native ceilings (§5.2: "Mandate and policy constraints are
        intersected"); `anchor` is the receipt's simulation block; `verdict` is the receipt's
        enum spelled out. `test_the_projection_resync_is_a_no_op_on_every_shipped_fixture`
        is what keeps this restatement honest.
        """
        normalized = {name: self.action[name] for _, name in eip712.ACTION_FIELDS}
        normalized["callData"] = self.action["callData"]
        self.evidence["normalizedAction"] = normalized

        effects = {name: self.mandate[name] for name in EXPECTED_EFFECTS_FROM_MANDATE}
        effects["maxAllowanceIncreaseBaseUnits"] = self.policy["maxAllowanceIncreaseBaseUnits"]
        effects["maxNativeValueWei"] = str(min(int(self.mandate["maxNativeValueWei"]),
                                               int(self.policy["maxNativeValueWei"])))
        self.evidence["expectedEffects"] = effects

        self.evidence["anchor"] = {
            "blockNumber": self.receipt["simulationBlockNumber"],
            "blockHash": self.receipt["simulationBlockHash"],
        }
        self.evidence["verdict"] = VERDICT_NAMES[int(self.receipt["verdict"])]
        self.receipt["reasonCodesHash"] = reasoncodes.reason_codes_hash_hex(
            self.receipt_doc["reasonCodes"])

    def publish_reason_codes(self, codes, commit=True, findings=None):
        """Set the published list; commit to it in the receipt unless told not to."""
        self.receipt_doc["reasonCodes"] = codes
        if findings is not None:
            self.receipt_doc["signerFindings"] = findings
        if commit:
            self.receipt["reasonCodesHash"] = reasoncodes.reason_codes_hash_hex(codes)
        return self

    def attested_record(self):
        return self.evidence["decodedSelectorAndParameters"]

    def write_evidence(self):
        canonical = jcs.canonicalize(self.evidence)
        write_json(self.path("evidence.json"), self.evidence)
        with open(self.path("evidence.canonical.json"), "wb") as handle:
            handle.write(canonical)
        with open(self.path("evidence.hash"), "w", encoding="ascii") as handle:
            handle.write("0x" + keccak256(canonical).hex())
        self.receipt["evidenceHash"] = "0x" + keccak256(canonical).hex()

    def seal(self, documents=None, evidence=None):
        if documents is not None:
            documents(self)
        Bundle.seal(self)                # the chain, then a first signature (discarded)
        self.sync_projections()
        if evidence is not None:
            evidence(self)
        self.write_evidence()
        Bundle.seal(self)                # re-signed over the final evidenceHash and reasonCodesHash
        if os.path.isfile(self.path("override.json")):
            self.seal_override()         # the credential re-pointed at the re-signed receipt
        return self


class ConformanceTestCase(PublicationTestCase):
    """The inherited apparatus -- `assert_refused` with its load-bearing subject regex,
    `assert_certifies`, `cli`, `live_bundle`, `certifying_run` -- all route through
    `bundle()` and `_predicate()`, so overriding those two moves the whole of it onto
    `ConformanceBundle` and lets a test name the execution path."""

    def bundle(self, case=ALLOW_CASE, payload=None, seal=True):
        room = tempfile.mkdtemp(dir=self.root)
        b = ConformanceBundle(case, room, payload=payload)
        return b.seal() if seal else b

    def staged(self, evidence=None, documents=None, case=ALLOW_CASE):
        """An internally perfect bundle whose ONLY fault is what the hooks introduce."""
        return self.bundle(case, seal=False).seal(documents=documents, evidence=evidence)

    def _predicate(self, bundle, authority=AUTHORITY, key=AUTHORITY_KEY,
                   evaluation_time=NOW, manifest_path=None, execution_path=AUTOMATIC):
        return verify_publication.verify(
            bundle.dir,
            manifest_path if manifest_path else bundle.manifest_file(key),
            authority, evaluation_time=evaluation_time, execution_path=execution_path)

    def assert_refused_for_content(self, bundle, subject, **kwargs):
        """Refused, naming `subject`, and NOT by a hash or signature check.

        The second half is the anti-false-positive guard the diff's §3 warned about: a
        bundle refused because its staging left a stale hash is not evidence that the
        content check exists."""
        message = self.assert_refused(bundle, subject, **kwargs)
        self.assertNotRegex(
            message, STAGING_FAULT_RE,
            "refused by a hash or signature check, so the staging is broken and the "
            "content check under test was never reached: " + message)
        return message

    def assert_refused_by_the_conformance_check(self, bundle, field, **kwargs):
        """A §5.7.1 refusal: names the field, carries D-087(b)'s name, never the forbidden one."""
        message = self.assert_refused_for_content(bundle, field, **kwargs)
        self.assertRegex(
            message, CHECK_NAME_RE,
            "D-087(b): the refusal must name the check %r; got: %s" % (CHECK_NAME, message))
        self.assertNotRegex(
            message, FORBIDDEN_NAME_RE,
            "D-087(b): the check is never named 'beneficiary verified': " + message)
        return message

    def approve_documents(self, spender, amount):
        """A `documents` hook that turns the fixture into a DemoERC20.approve mandate.

        The mandate's selector and the action's leading selector move together so the
        existing selector check keeps passing; the policy gets a non-zero allowance
        ceiling so "within" and "exceeds" are both reachable."""
        def hook(b):
            b.mandate["selector"] = APPROVE_SELECTOR
            b.policy["maxAllowanceIncreaseBaseUnits"] = "1000"
            b.action["callData"] = APPROVE_SELECTOR + word(spender) + word(amount)
        return hook

    def approve_record(self, spender, amount):
        """An `evidence` hook attesting a decoded DemoERC20.approve record."""
        def hook(b):
            b.evidence["decodedSelectorAndParameters"] = {
                "decoded": "true",
                "selector": APPROVE_SELECTOR,
                "schema": "DemoERC20.approve",
                "description": "DemoERC20.approve(spender=%s, amount=%s)" % (spender, amount),
                "parameters": {"spender": spender, "amount": str(amount)},
            }
        return hook


# ---------------------------------------------------------------------------
# The controls
# ---------------------------------------------------------------------------

class TestConformanceControl(ConformanceTestCase):
    """Nothing below this class means anything without these.

    Every negative in this file asserts that a bundle is REFUSED for its content. That
    is evidence only if (1) the staging reproduces the shipped fixtures exactly, so the
    negatives probe bundles the corpus could have contained, and (2) an otherwise
    identical bundle is ACCEPTED. All PASS on the baseline and MUST keep passing."""

    def test_the_projection_resync_is_a_no_op_on_every_shipped_fixture(self):
        """PASSES. For every receipt-bearing fixture, re-sealing with the projections
        resynced reproduces the shipped `evidence.canonical.json` BYTE FOR BYTE, the
        shipped `evidence.hash`, and the shipped `reasonCodesHash`. If any fixture
        drifted from its own documents, or if `sync_projections` restated A's
        derivations wrongly, this is where it shows -- and it names the fixture."""
        # Selected from the corpus index, not from the file listing: the §5.5.1 refusal
        # fixture carries a `receipt.json` with no receipt body, and D-087(d) rules that
        # shape is RECOGNISED AND REFUSED by this verifier, never verified.
        cases = sorted(entry["id"] for entry in read_json(SAMPLES, "index.json")
                       if not entry["signerRefused"])
        self.assertGreaterEqual(len(cases), 6, "the corpus shrank: " + repr(cases))
        for case in cases:
            with self.subTest(case=case):
                b = self.bundle(case)
                with open(os.path.join(SAMPLES, case, "evidence.canonical.json"), "rb") as h:
                    shipped_canonical = h.read()
                with open(os.path.join(SAMPLES, case, "evidence.hash"), "rb") as h:
                    shipped_hash = h.read().decode().strip().lower()
                shipped_receipt = read_json(SAMPLES, case, "receipt.json")["receipt"]
                self.assertEqual(jcs.canonicalize(b.evidence), shipped_canonical,
                                 "resynced projections differ from the shipped evidence")
                with open(b.path("evidence.hash"), "rb") as h:
                    self.assertEqual(h.read().decode().strip().lower(), shipped_hash)
                self.assertEqual(b.receipt["evidenceHash"], shipped_receipt["evidenceHash"])
                self.assertEqual(b.receipt["reasonCodesHash"],
                                 shipped_receipt["reasonCodesHash"])

    def test_an_unmutated_resealed_bundle_still_certifies(self):
        """PASSES, and MUST keep passing. If a repair breaks this, every negative in
        this file has become unfalsifiable."""
        result = self.assert_certifies(self.bundle())
        self.assertEqual(result["verdict"], "ALLOW")
        self.assertEqual(result["actionHash"],
                         read_json(SAMPLES, ALLOW_CASE, "receipt.json")["receipt"]["actionHash"])

    def test_an_unmutated_resealed_review_bundle_still_certifies_by_override(self):
        """PASSES. An unmutated re-seal reproduces the shipped receipt exactly, so the
        re-pointed credential is byte-identical to the shipped one; the override path
        is reachable from this staging, which is what the override-path negatives
        rely on."""
        b = self.bundle(REVIEW_CASE)
        self.assertEqual(b.override_doc()["override"],
                         read_json(SAMPLES, REVIEW_CASE, "override.json")["override"])
        result = self.assert_certifies(b, execution_path=OVERRIDE)
        self.assertEqual(result["verdict"], "REVIEW")
        self.assertIn("ownerOverrideHash", result)

    def test_a_mutated_review_bundle_carries_a_credential_naming_its_re_signed_receipt(self):
        """PASSES. The override-path negatives change `evidence.json`, which moves
        `receipt.evidenceHash` and so the receipt's struct hash; this proves the
        credential follows it, so those negatives cannot be refused for
        `reviewReceiptHash` instead of for their content."""
        b = self.staged(evidence=lambda b: b.evidence.__setitem__("note", "probe"),
                        case=REVIEW_CASE)
        shipped = read_json(SAMPLES, REVIEW_CASE, "receipt.json")["receipt"]
        self.assertNotEqual(b.receipt["evidenceHash"], shipped["evidenceHash"])
        self.assertEqual(b.override_doc()["override"]["reviewReceiptHash"],
                         "0x" + eip712.receipt_struct_hash(b.receipt).hex())
        self.assert_certifies(b, execution_path=OVERRIDE)

    def test_a_resealed_bundle_certifies_at_the_cli_on_the_host_clock(self):
        """PASSES. The positive control for every assertion about CERTIFYING output
        below; `certifying_run` insists on exit 0 and `MODE_STATIC`, so those
        assertions cannot go green on a run that failed for another reason."""
        completed, headline, payload = self.certifying_run(ALLOW_CASE)
        self.assertTrue(headline.startswith("PASS (static, offline)"), headline)
        self.assertEqual(payload["verdict"], "ALLOW")

    def test_the_evidence_hook_reaches_the_file_the_predicate_reads(self):
        """PASSES. The negatives mutate `b.evidence` in memory; this proves the mutation
        lands in `evidence.json` on disk, that the three evidence artifacts agree with
        each other, and that the receipt was re-signed over the mutated bytes -- i.e.
        that the only thing left for the predicate to object to is the CONTENT."""
        b = self.staged(evidence=lambda b: b.evidence.__setitem__("note", "probe"))
        on_disk = read_json(b.path("evidence.json"))
        self.assertEqual(on_disk.get("note"), "probe")
        canonical = jcs.canonicalize(on_disk)
        with open(b.path("evidence.canonical.json"), "rb") as h:
            self.assertEqual(h.read(), canonical)
        self.assertEqual(read_json(b.path("receipt.json"))["receipt"]["evidenceHash"],
                         "0x" + keccak256(canonical).hex())
        # And the baseline, which reads no content, certifies it: the hash chain is intact.
        self.assert_certifies(b)

    def test_divergent_ceilings_with_the_correct_intersection_certify(self):
        """PASSES. Control for the §5.2 intersection negative: when the policy ceiling is
        tighter than the mandate's, `expectedEffects.maxNativeValueWei` projecting the
        LOWER of the two is correct and must certify. (The corpus has no divergent
        sample -- A's own comment records that -- so it is staged.)"""
        b = self.staged(documents=lambda b: b.policy.__setitem__(
            "maxNativeValueWei", "2000000000000000"))
        self.assertEqual(b.evidence["expectedEffects"]["maxNativeValueWei"], "2000000000000000")
        self.assert_certifies(b)

    def test_a_committed_non_empty_reason_code_list_certifies(self):
        """PASSES. The reason-code check is a COMPARISON against the commitment, not a
        requirement that the list be empty: a published list the receipt actually
        commits to certifies."""
        b = self.staged(evidence=lambda b: b.publish_reason_codes(
            ["EVAL_TARGET_BOUND", "EVAL_CHAIN_BOUND"]))
        self.assert_certifies(b)

    def test_a_non_canonical_but_correctly_committed_list_certifies(self):
        """PASSES. A's fourth reason-code check is ADVISORY (`skipped=True`): the hash is
        de-duplicated and sorted before hashing, so an unsorted list with a duplicate
        that commits to the right set is not a failure. Pinned so a port does not
        promote the advisory into a refusal."""
        codes = ["EVAL_TARGET_BOUND", "EVAL_CHAIN_BOUND", "EVAL_CHAIN_BOUND"]
        b = self.staged(evidence=lambda b: b.publish_reason_codes(codes))
        self.assertEqual(b.receipt["reasonCodesHash"],
                         reasoncodes.reason_codes_hash_hex(sorted(set(codes))))
        self.assert_certifies(b)

    def test_a_receipt_without_a_signer_findings_array_certifies(self):
        """PASSES. A skips the subset check when `signerFindings` is absent; absence of
        the SIGNER'S OWN findings list is tolerated, absence of `reasonCodes` is not."""
        b = self.staged(evidence=lambda b: b.receipt_doc.pop("signerFindings"))
        self.assertNotIn("signerFindings", read_json(b.path("receipt.json")))
        self.assert_certifies(b)

    def test_an_approve_record_that_conforms_certifies(self):
        """PASSES. Control for the DemoERC20.approve arm of §5.7.1: a signer-attested
        record whose spender is the mandated beneficiary and whose amount is within the
        policy's allowance ceiling conforms. A does not tie the attested schema to the
        selector; this control ports that and no more."""
        spender = read_json(SAMPLES, ALLOW_CASE, "mandate.json")["beneficiary"]
        b = self.staged(documents=self.approve_documents(spender, 1000),
                        evidence=self.approve_record(spender, 1000))
        self.assertEqual(b.mandate["selector"], APPROVE_SELECTOR)
        self.assert_certifies(b)

    def test_a_block_bundle_is_refused_for_its_verdict_not_its_conformance(self):
        """PASSES on the baseline and pins an ORDERING for the port. `case-3-wrong-purpose-
        block`'s attested record does not conform to the mandate -- that is WHY it is
        BLOCK. A binds conformance to ALLOW only, and R-A018-16(c) says a recipient must
        be told the signer said BLOCK, not that a resourceId disagrees."""
        message = self.assert_refused(self.bundle(BLOCK_WRONG_PURPOSE_CASE), r"BLOCK")
        self.assertNotRegex(message, CHECK_NAME_RE,
                            "a BLOCK bundle was refused for nonconformance, not its verdict")

    def test_a_review_bundle_with_a_nonconforming_record_still_certifies_by_override(self):
        """PASSES. A: "BLOCK and REVIEW bundles are legitimately nonconforming and MUST
        stay verifiable." A REVIEW receipt executed by an authenticated owner override
        is the owner's decision to proceed; the conformance check binds to ALLOW.
        THIS PORTS A. Whether the override path should ALSO require conformance is a
        product question, recorded in the module docstring and not decided here."""
        def nonconforming(b):
            b.attested_record()["parameters"]["beneficiary"] = OTHER_ADDRESS
        b = self.staged(evidence=nonconforming, case=REVIEW_CASE)
        self.assertEqual(b.attested_record()["parameters"]["beneficiary"], OTHER_ADDRESS)
        self.assert_certifies(b, execution_path=OVERRIDE)


# ---------------------------------------------------------------------------
# O2 -- the §5.6 evidence-projection arm. Severity 1.
# ---------------------------------------------------------------------------

class TestEvidenceDescribesTheBundle(ConformanceTestCase):
    """`verify.py::_evidence_describes_the_bundle` and the anchor / verdict tail of
    `_chain_checks`, ported. Every bundle below is re-canonicalised, re-hashed and
    RE-SIGNED, so the hash chain is perfect and only a content check can refuse it.
    All FAIL on the baseline: B never opens `evidence.json`."""

    def test_evidence_replaced_wholesale_with_an_empty_object_is_refused(self):
        """FAILS on baseline -- the diff's worst cell (§3 #1). The artifact a recipient
        actually READS, the dashboard's entire content, replaced with a note saying
        nothing, and B prints `PASS (static, offline) ... the signer's decision is
        ALLOW`. Absence is not agreement (A-067, D-052(b))."""
        b = self.staged(evidence=lambda b: setattr(
            b, "evidence", {"note": "this bundle's evidence says nothing at all"}))
        self.assertEqual(read_json(b.path("evidence.json")),
                         {"note": "this bundle's evidence says nothing at all"})
        self.assert_refused_for_content(
            b, r"normalizedAction|expectedEffects|anchor|verdict|5\.6")

    def test_evidence_that_is_not_an_object_is_refused(self):
        """FAILS on baseline. A's first branch: a top-level array canonicalises and
        hashes perfectly well and describes nothing."""
        b = self.staged(evidence=lambda b: setattr(b, "evidence", ["nothing"]))
        self.assert_refused_for_content(b, r"evidence")

    def test_normalized_action_naming_a_different_target_is_refused(self):
        """FAILS on baseline (§3 #2). `normalizedAction` is the §5.3 action restated;
        a restatement that names another contract describes a call this bundle does
        not carry."""
        b = self.staged(evidence=lambda b: b.evidence["normalizedAction"].__setitem__(
            "target", OTHER_ADDRESS))
        self.assert_refused_for_content(b, r"normalizedAction[\s\S]*target")

    def test_an_absent_normalized_action_is_refused(self):
        """FAILS on baseline. Omission must cost more than a contradiction, not less
        (D-052(b)): deleting the projection is the cheapest evasion."""
        b = self.staged(evidence=lambda b: b.evidence.pop("normalizedAction"))
        self.assert_refused_for_content(b, r"normalizedAction")

    def test_a_normalized_action_that_is_not_an_object_is_refused(self):
        """FAILS on baseline. A-069's original gate was `isinstance(..., dict)` with no
        else-branch, so wrapping the projection in a one-element list emitted no Check."""
        b = self.staged(evidence=lambda b: b.evidence.__setitem__(
            "normalizedAction", [b.evidence["normalizedAction"]]))
        self.assert_refused_for_content(b, r"normalizedAction")

    def test_normalized_calldata_whose_bytes_do_not_hash_to_data_hash_is_refused(self):
        """FAILS on baseline. Every §5.3 field of `normalizedAction` agrees, including
        `dataHash` -- only `callData` differs. Without the keccak comparison the
        evidence could agree field by field while the BYTES it was computed over were
        something else entirely."""
        def swap_calldata(b):
            original = b.evidence["normalizedAction"]["callData"]
            b.evidence["normalizedAction"]["callData"] = original[:-2] + (
                "00" if original[-2:] != "00" else "01")
        b = self.staged(evidence=swap_calldata)
        self.assertEqual(b.evidence["normalizedAction"]["dataHash"], b.action["dataHash"])
        self.assert_refused_for_content(b, r"callData|dataHash")

    def test_an_evidence_verdict_of_block_beside_an_allow_receipt_is_refused(self):
        """FAILS on baseline (§3 #3). The dashboard says BLOCK; the signed receipt says
        ALLOW; B certifies the receipt and never reads the dashboard."""
        b = self.staged(evidence=lambda b: b.evidence.__setitem__("verdict", "BLOCK"))
        self.assert_refused_for_content(b, r"verdict")

    def test_an_absent_evidence_verdict_is_refused(self):
        """FAILS on baseline. A's sibling-of-L6-3: `"verdict" in evidence` with no
        else-branch meant a bundle that omits its own verdict was never compared."""
        b = self.staged(evidence=lambda b: b.evidence.pop("verdict"))
        self.assert_refused_for_content(b, r"verdict")

    def test_an_evidence_verdict_of_allow_beside_a_review_receipt_is_refused_by_override(self):
        """FAILS on baseline. The same disagreement on the path where B certifies a
        non-ALLOW receipt: a REVIEW bundle whose dashboard tells the owner ALLOW."""
        b = self.staged(evidence=lambda b: b.evidence.__setitem__("verdict", "ALLOW"),
                        case=REVIEW_CASE)
        self.assert_refused_for_content(b, r"verdict", execution_path=OVERRIDE)

    def test_an_anchor_naming_a_fabricated_block_is_refused(self):
        """FAILS on baseline (§3 #4). The receipt's `simulationBlockNumber` /
        `simulationBlockHash` are signed; the evidence's `anchor` is what a reader is
        shown. A-056: the anchor had no test at all."""
        b = self.staged(evidence=lambda b: b.evidence.__setitem__(
            "anchor", {"blockNumber": "99999999", "blockHash": FABRICATED_HASH}))
        self.assert_refused_for_content(b, r"anchor")

    def test_an_absent_anchor_is_refused(self):
        """FAILS on baseline. Deleting the anchor outright is the cheaper attack on the
        same binding, and A found it verified `=> PASS` until the D-052(b) sweep."""
        b = self.staged(evidence=lambda b: b.evidence.pop("anchor"))
        self.assert_refused_for_content(b, r"anchor")

    def test_expected_effects_misprojecting_the_native_ceiling_is_refused(self):
        """FAILS on baseline (§3 #7). `expectedEffects.maxNativeValueWei` ten times the
        ceiling either signed document states."""
        b = self.staged(evidence=lambda b: b.evidence["expectedEffects"].__setitem__(
            "maxNativeValueWei", "100000000000000000"))
        self.assert_refused_for_content(b, r"expectedEffects[\s\S]*maxNativeValueWei")

    def test_expected_effects_naming_another_beneficiary_is_refused(self):
        """FAILS on baseline. Seven of `expectedEffects`' fields are copied from the
        mandate; a copy that disagrees with the signed mandate is not a projection."""
        b = self.staged(evidence=lambda b: b.evidence["expectedEffects"].__setitem__(
            "beneficiary", OTHER_ADDRESS))
        self.assert_refused_for_content(b, r"expectedEffects[\s\S]*beneficiary")

    def test_expected_effects_misprojecting_the_allowance_ceiling_is_refused(self):
        """FAILS on baseline. The one field of `expectedEffects` copied from the POLICY."""
        b = self.staged(evidence=lambda b: b.evidence["expectedEffects"].__setitem__(
            "maxAllowanceIncreaseBaseUnits", "1"))
        self.assert_refused_for_content(
            b, r"expectedEffects[\s\S]*maxAllowanceIncreaseBaseUnits")

    def test_an_absent_expected_effects_is_refused(self):
        """FAILS on baseline. The same omission-is-cheapest argument as
        `normalizedAction`."""
        b = self.staged(evidence=lambda b: b.evidence.pop("expectedEffects"))
        self.assert_refused_for_content(b, r"expectedEffects")

    def test_expected_effects_stating_the_mandate_ceiling_where_the_policy_is_tighter_is_refused(self):
        """FAILS on baseline. §5.2: constraints are INTERSECTED, so the binding native
        ceiling is the lower of the two. Compared against the mandate alone the check
        would be wrong the first time they diverge -- and this is the first time."""
        b = self.staged(
            documents=lambda b: b.policy.__setitem__("maxNativeValueWei", "2000000000000000"),
            evidence=lambda b: b.evidence["expectedEffects"].__setitem__(
                "maxNativeValueWei", b.mandate["maxNativeValueWei"]))
        self.assertEqual(b.evidence["expectedEffects"]["maxNativeValueWei"],
                         "10000000000000000")
        self.assert_refused_for_content(b, r"maxNativeValueWei")


# ---------------------------------------------------------------------------
# O4 -- the reason-code arm. Severity 4; bites hardest on the override path.
# ---------------------------------------------------------------------------

class TestReasonCodesAreRead(ConformanceTestCase):
    """`verify.py::_reason_code_checks`, ported. `receipt.reasonCodesHash` is signed;
    the `reasonCodes` list beside it is what a recipient is shown. All FAIL on the
    baseline: `reasonCodes`, `reasonCodesHash` and `signerFindings` have zero
    occurrences in B."""

    def test_published_codes_the_receipt_never_committed_to_are_refused(self):
        """FAILS on baseline (§3 #6). The receipt commits to the EMPTY set --
        keccak256("") -- and the recipient is shown two codes."""
        b = self.staged(evidence=lambda b: b.publish_reason_codes(
            ["EVAL_TARGET_BOUND", "EVAL_CHAIN_BOUND"], commit=False))
        self.assertEqual(b.receipt["reasonCodesHash"], reasoncodes.reason_codes_hash_hex([]))
        self.assert_refused_for_content(b, r"reasonCodesHash")

    def test_a_receipt_committing_to_codes_it_does_not_publish_is_refused(self):
        """FAILS on baseline. The reverse swap: the signed hash commits to a code and the
        published list is empty, so the recipient is shown a clean slate the signer
        never certified."""
        def hide(b):
            b.receipt_doc["reasonCodes"] = []
            b.receipt["reasonCodesHash"] = reasoncodes.reason_codes_hash_hex(
                ["EVAL_TARGET_BOUND"])
        b = self.staged(evidence=hide)
        self.assert_refused_for_content(b, r"reasonCodesHash")

    def test_a_swapped_list_is_refused_on_the_override_path(self):
        """FAILS on baseline. The REVIEW fixture commits to two codes; a third is shown.
        This is the path on which B certifies a non-ALLOW receipt, so it is where a
        swapped explanation reaches an owner deciding whether to override."""
        shipped = read_json(SAMPLES, REVIEW_CASE, "receipt.json")["reasonCodes"]
        b = self.staged(evidence=lambda b: b.publish_reason_codes(
            shipped + ["EVAL_NONCE_CURRENT"], commit=False), case=REVIEW_CASE)
        self.assert_refused_for_content(b, r"reasonCodesHash", execution_path=OVERRIDE)

    def test_an_absent_reason_code_list_is_refused(self):
        """FAILS on baseline. §5.4: "the full ordered list travels alongside the receipt
        and a verifier must be given it." Not being given it is a failure for a signed
        receipt, not a reason to pass quietly."""
        b = self.staged(evidence=lambda b: b.receipt_doc.pop("reasonCodes"))
        self.assertNotIn("reasonCodes", read_json(b.path("receipt.json")))
        self.assert_refused_for_content(b, r"reasonCodes")

    def test_a_reason_code_list_that_is_not_a_list_is_refused(self):
        """FAILS on baseline. A string where the array belongs."""
        b = self.staged(evidence=lambda b: b.receipt_doc.__setitem__(
            "reasonCodes", "EVAL_TARGET_BOUND"))
        self.assert_refused_for_content(b, r"reasonCodes")

    def test_an_identifier_carrying_the_delimiter_is_refused(self):
        """FAILS on baseline. `reasoncodes.py`'s documented collision: {"EVIL\\nINJECTED"}
        joins to the same preimage as {"EVIL", "INJECTED"}, so the receipt below commits
        -- correctly, byte for byte -- to a set the published list does not spell. Only
        the grammar check, applied with absolute anchors, can refuse it."""
        def collide(b):
            b.receipt_doc["reasonCodes"] = ["EVIL\nINJECTED"]
            b.receipt["reasonCodesHash"] = reasoncodes.reason_codes_hash_hex(
                ["EVIL", "INJECTED"])
        b = self.staged(evidence=collide)
        self.assert_refused_for_content(b, r"reason.code|identifier")

    def test_an_identifier_over_sixty_four_characters_is_refused(self):
        """FAILS on baseline. The §5.4 pattern bounds an identifier at 64; the hash below
        is the naive keccak of the joined form, so only the grammar can refuse it."""
        too_long = "A" * 65
        def commit_naively(b):
            b.receipt_doc["reasonCodes"] = [too_long]
            b.receipt["reasonCodesHash"] = "0x" + keccak256(too_long.encode()).hex()
        b = self.staged(evidence=commit_naively)
        self.assert_refused_for_content(b, r"reason.code|identifier")

    def test_a_signer_finding_outside_the_committed_set_is_refused(self):
        """FAILS on baseline. §5.4 defines the committed set as the UNION of the
        evaluator's codes and the signer's findings; a finding absent from
        `reasonCodes` means the receipt commits to the evaluator's half only."""
        b = self.staged(evidence=lambda b: b.publish_reason_codes(
            [], findings=["SIGNER_TARGET_CODEHASH_MISMATCH"]))
        self.assertEqual(b.receipt["reasonCodesHash"], reasoncodes.reason_codes_hash_hex([]))
        self.assert_refused_for_content(b, r"signerFindings")


# ---------------------------------------------------------------------------
# §5.7.1 -- the signer-attested record conforms to the mandate. D-087(b).
# ---------------------------------------------------------------------------

class TestSignerAttestedRecordConformsToMandate(ConformanceTestCase):
    """`verify.py::_allow_conforms_to_the_mandate`, ported. The record compared is the
    signer's own `decodedSelectorAndParameters`; NOTHING here decodes `callData`
    (D-083(b)). Every refusal below must carry D-087(b)'s name for the check and never
    the forbidden one -- `assert_refused_by_the_conformance_check` enforces that on
    each. All FAIL on the baseline: `decodedSelectorAndParameters` has zero occurrences
    in B."""

    def mutate_parameter(self, name, value):
        def hook(b):
            b.attested_record()["parameters"][name] = value
        return hook

    def test_an_attested_beneficiary_that_is_not_the_mandated_one_is_refused(self):
        """FAILS on baseline (§3 #5). The signer honestly reports that it decoded a
        beneficiary the mandate does not name, and said ALLOW anyway: the
        misconfigured-but-honest evaluator this check exists to catch."""
        b = self.staged(evidence=self.mutate_parameter("beneficiary", OTHER_ADDRESS))
        self.assert_refused_by_the_conformance_check(b, r"beneficiary")

    def test_an_attested_resource_that_is_not_the_mandated_one_is_refused(self):
        """FAILS on baseline. EVAL_PURCHASE_RESOURCE, from the verifier's side."""
        b = self.staged(evidence=self.mutate_parameter("resourceId", FABRICATED_HASH))
        self.assert_refused_by_the_conformance_check(b, r"resourceId")

    def test_an_attested_duration_that_is_not_the_mandated_one_is_refused(self):
        """FAILS on baseline. EVAL_PURCHASE_DURATION, from the verifier's side."""
        b = self.staged(evidence=self.mutate_parameter("durationSeconds", "172800"))
        self.assert_refused_by_the_conformance_check(b, r"durationSeconds")

    def test_an_attested_recurrence_the_mandate_forbids_is_refused(self):
        """FAILS on baseline. EVAL_PURCHASE_RECURRENCE: `recurring` requested while
        `mandate.recurringAllowed` is false."""
        b = self.staged(evidence=self.mutate_parameter("recurring", True))
        self.assertFalse(b.mandate["recurringAllowed"])
        self.assert_refused_by_the_conformance_check(b, r"recurr")

    def test_an_attested_selector_that_is_not_the_mandated_one_is_refused(self):
        """FAILS on baseline. The attested record claims to have decoded a different
        function than the mandate authorises."""
        b = self.staged(evidence=lambda b: b.attested_record().__setitem__(
            "selector", APPROVE_SELECTOR))
        self.assert_refused_by_the_conformance_check(b, r"selector")

    def test_a_record_attesting_that_the_call_was_not_decoded_is_refused(self):
        """FAILS on baseline. `decoded: "false"` under ALLOW: an undecoded call cannot
        be ALLOWed, and an ALLOW nobody can check is not an ALLOW anybody should
        certify."""
        b = self.staged(evidence=lambda b: b.attested_record().__setitem__(
            "decoded", "false"))
        self.assert_refused_by_the_conformance_check(b, r"decoded")

    def test_an_absent_attested_record_under_allow_is_refused(self):
        """FAILS on baseline. ABSENCE IS NOT AGREEMENT: an ALLOW with no decoded record
        to compare offers nothing to certify."""
        b = self.staged(evidence=lambda b: b.evidence.pop("decodedSelectorAndParameters"))
        self.assert_refused_by_the_conformance_check(b, r"decodedSelectorAndParameters")

    def test_a_record_without_a_parameters_object_is_refused(self):
        """FAILS on baseline. The record is present and says nothing comparable."""
        b = self.staged(evidence=lambda b: b.attested_record().pop("parameters"))
        self.assert_refused_by_the_conformance_check(b, r"parameters")

    def test_a_record_of_a_schema_the_verifier_cannot_evaluate_is_refused(self):
        """FAILS on baseline. An ALLOW whose schema this verifier cannot check
        conformance for is an ALLOW it cannot certify."""
        b = self.staged(evidence=lambda b: b.attested_record().__setitem__(
            "schema", "DemoVault.withdrawEverything"))
        self.assert_refused_by_the_conformance_check(b, r"schema")

    def test_an_approve_spender_that_is_not_the_mandated_beneficiary_is_refused(self):
        """FAILS on baseline. EVAL_APPROVAL_SPENDER: the approve arm's beneficiary is
        the spender. Staged against the control that certifies with the right one."""
        beneficiary = read_json(SAMPLES, ALLOW_CASE, "mandate.json")["beneficiary"]
        b = self.staged(documents=self.approve_documents(beneficiary, 1000),
                        evidence=self.approve_record(OTHER_ADDRESS, 1000))
        self.assert_refused_by_the_conformance_check(b, r"spender")

    def test_an_approve_amount_exceeding_the_policy_allowance_ceiling_is_refused(self):
        """FAILS on baseline. EVAL_APPROVAL_CEILING: the amount is compared to
        `policy.maxAllowanceIncreaseBaseUnits`, the one §5.7.1 field that comes from the
        policy rather than the mandate."""
        beneficiary = read_json(SAMPLES, ALLOW_CASE, "mandate.json")["beneficiary"]
        b = self.staged(documents=self.approve_documents(beneficiary, 1001),
                        evidence=self.approve_record(beneficiary, 1001))
        message = self.assert_refused_by_the_conformance_check(b, r"amount|ceiling|allowance")
        self.assertNotRegex(message, r"spender", "refused for the spender, which was right")


# ---------------------------------------------------------------------------
# D-087(b): the name, on every surface a recipient reads.
# ---------------------------------------------------------------------------

class TestTheCheckIsNamedPrecisely(ConformanceTestCase):
    """D-087(b): "The check is named 'signer-attested record conforms to mandate' and
    never 'beneficiary verified.' It catches a misconfigured-but-honest evaluator; it
    honestly does not catch a lying signer, and its output must say so." The standing
    pattern: never let the name claim more than the check establishes."""

    def test_the_refusal_names_the_check_precisely_and_never_beneficiary_verified(self):
        """FAILS on baseline. The refusal a recipient reads must say WHICH check refused
        it, by the ruled name, and must not describe what it did as verifying the
        beneficiary -- a claim that would be true only if the signer were honest."""
        def hook(b):
            b.attested_record()["parameters"]["beneficiary"] = OTHER_ADDRESS
        message = self.assert_refused(self.staged(evidence=hook), r"beneficiary")
        self.assertRegex(message, CHECK_NAME_RE,
                         "the refusal does not name %r" % CHECK_NAME)
        self.assertNotRegex(message, FORBIDDEN_NAME_RE)

    def test_the_certifying_output_names_the_check_precisely_and_never_beneficiary_verified(self):
        """FAILS on baseline. What a certifying run SAYS it compared must include this
        check by its ruled name -- R-A018-08's discipline, that the PASS line enumerates
        what was compared -- and must never call it 'beneficiary verified'."""
        completed, headline, payload = self.certifying_run(ALLOW_CASE)
        self.assertRegex(completed.stdout, CHECK_NAME_RE,
                         "certifying output does not name %r:\n%s" % (CHECK_NAME,
                                                                      completed.stdout))
        self.assertNotRegex(completed.stdout, FORBIDDEN_NAME_RE)

    def test_the_certifying_output_states_it_does_not_catch_a_lying_signer(self):
        """FAILS on baseline. The record compared is the signer's own attestation. A
        signer that lies about what it decoded passes this check, and the ruling
        requires the output to say so in as many words."""
        completed, headline, payload = self.certifying_run(ALLOW_CASE)
        self.assertRegex(
            completed.stdout, LYING_SIGNER_RE,
            "certifying output does not disclose that the check does not catch a lying "
            "signer:\n" + completed.stdout)

    def test_the_certifying_output_still_discloses_that_calldata_is_not_decoded(self):
        """PASSES on baseline and MUST keep passing after the port. D-087(b) addresses
        the gap D-083(b) measured; it does not reverse D-083(b). A port that reads the
        attested record must not start claiming, or stop disclaiming, decoding."""
        completed, headline, payload = self.certifying_run(ALLOW_CASE)
        self.assertRegex(completed.stdout, NOT_DECODED_RE)
        self.assertTrue(any("decod" in entry for entry in payload["notEstablished"]),
                        "notEstablished no longer mentions decoding: "
                        + repr(payload["notEstablished"]))

    def test_the_help_text_never_says_beneficiary_verified(self):
        """PASSES on baseline. The interface surface: argparse reprints the module
        docstring, so a docstring that adopts the forbidden name would surface here."""
        completed = subprocess.run([sys.executable, PREDICATE, "--help"],
                                   capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotRegex(completed.stdout, FORBIDDEN_NAME_RE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
