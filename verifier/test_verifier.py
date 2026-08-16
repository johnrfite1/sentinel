#!/usr/bin/env python3
"""Tests for the Sentinel standalone receipt verifier (D-010).

Stdlib unittest only, no third-party test runner:

    python3 verifier/test_verifier.py
    python3 -m unittest discover -s verifier -v
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import eip712  # noqa: E402
import jcs  # noqa: E402
import reasoncodes  # noqa: E402
import verify  # noqa: E402
from keccak import keccak256_hex  # noqa: E402
from secp256k1 import (  # noqa: E402
    G, N, is_low_s, parse_signature, point_mul, public_key_to_address,
    recover_address, sign_digest,
)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(REPO, "fixtures", "samples")

# Anvil account #1, which domain.json names as the Sentinel signer. Its private
# key is PUBLISHED, so anyone presenting a bundle can mint a perfectly valid
# signature over whatever receipt they like. That is the position a third-party
# verifier is actually in, and it is why "the signature verified" cannot stand
# in for the bundle-internal binding checks.
SIGNER_KEY = verify._SENTINEL_SIGNER_TEST_KEY


def read_json(*parts):
    with open(os.path.join(*parts), "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


def write_json(path, doc):
    with open(path, "w", encoding="ascii") as handle:
        json.dump(doc, handle)  # ensure_ascii=True, so lone surrogates escape


def stage(case, tmp, domain=None):
    """Copy a sample directory into `tmp`, with a domain.json beside it."""
    target = os.path.join(tmp, os.path.basename(case))
    shutil.copytree(case, target)
    write_json(os.path.join(tmp, "domain.json"),
               read_json(SAMPLES, "domain.json") if domain is None else domain)
    return target


def reseal(target, domain):
    """Re-sign a staged receipt.json with the published signer key."""
    doc = read_json(target, "receipt.json")
    doc["signature"] = sign_digest(
        eip712.receipt_digest(domain, doc["receipt"]), SIGNER_KEY)
    write_json(os.path.join(target, "receipt.json"), doc)
    return doc


def sample_dirs():
    return sorted(
        os.path.join(SAMPLES, name)
        for name in os.listdir(SAMPLES)
        if os.path.isdir(os.path.join(SAMPLES, name))
    )


def expected_verdicts():
    return {e["id"]: e for e in read_json(SAMPLES, "index.json")}


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------

class TestKeccak(unittest.TestCase):
    """Keccak-256 against published vectors, so a green suite below means the
    hash is right rather than merely self-consistent."""

    # Published vectors, not values this implementation produced.
    VECTORS = [
        (b"", "0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"),
        (b"abc", "0x4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45"),
        (b"hello", "0x1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8"),
        (b"testing", "0x5f16f4c7f149ac4f9510d9cf8cf384038ad348b3bcdc01915f95de12df9d1b02"),
        (b"a" * 200, "0x96ea54061def936c4be90b518992fdc6f12f535068a256229aca54267b4d084d"),
    ]

    def test_vectors(self):
        for data, expected in self.VECTORS:
            with self.subTest(length=len(data)):
                self.assertEqual(keccak256_hex(data), expected)

    def test_rate_boundary_lengths_are_distinct(self):
        # 136 bytes is exactly one absorb block, so 135/136/137 straddle the
        # pad10*1 edge. These are regression pins on this implementation, not
        # independent vectors; the cross-implementation evidence that the
        # padding is right is that the ~6.3 kB evidence bundles hash to the
        # values the Sentinel evaluator recorded.
        digests = {keccak256_hex(bytes(n)) for n in (135, 136, 137)}
        self.assertEqual(len(digests), 3)
        self.assertEqual(
            keccak256_hex(bytes(136)),
            "0x3a5912a7c5faa06ee4fe906253e339467a9ce87d533c65be3c15cb231cdb25f9",
        )

    def test_not_sha3(self):
        import hashlib
        self.assertNotEqual(keccak256_hex(b"abc"), "0x" + hashlib.sha3_256(b"abc").hexdigest())


class TestJCSNumbers(unittest.TestCase):
    """RFC 8785 appendix B number vectors.

    None of these are exercised by the Sentinel fixtures, which carry every
    number as a JSON string (REPORT.md F-6). They are tested anyway because the
    schema does not forbid a real number appearing later.
    """

    VECTORS = [
        (0.0, "0"), (-0.0, "0"), (1.0, "1"), (-1.0, "-1"),
        (1e21, "1e+21"), (1e20, "100000000000000000000"),
        (1e-6, "0.000001"), (1e-7, "1e-7"),
        (333333333.33333329, "333333333.3333333"),
        (5e-324, "5e-324"),
        (9.999999999999997e22, "9.999999999999997e+22"),
        (1.7976931348623157e308, "1.7976931348623157e+308"),
        (-1.5, "-1.5"),
    ]

    def test_number_serialization(self):
        for value, expected in self.VECTORS:
            with self.subTest(value=value):
                self.assertEqual(jcs.serialize_number(value), expected)

    def test_nan_and_infinity_rejected(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(jcs.CanonicalizationError):
                jcs.serialize_number(bad)


class TestJCSStructure(unittest.TestCase):
    def test_key_sorting_is_utf16_code_units(self):
        # U+FFFD is one UTF-16 code unit (0xFFFD); U+1F600 is the surrogate
        # pair 0xD83D 0xDE00. So the astral character sorts FIRST in UTF-16
        # code-unit order and LAST in code-point order. An implementation that
        # sorted by code point would silently produce a different hash.
        obj = {"\ufffd": 1, "\U0001f600": 2}
        self.assertEqual(
            jcs.canonicalize(obj).decode("utf-8"),
            '{"\U0001f600":2,"\ufffd":1}',
        )
        self.assertLess("\U0001f600".encode("utf-16-be"),
                        "\ufffd".encode("utf-16-be"))
        self.assertGreater("\U0001f600", "\ufffd")  # opposite by code point

    def test_escapes(self):
        value = "\b\t\n\f\r\"\\" + "\u0000" + "\u001f" + "\u007f"
        self.assertEqual(
            jcs.canonicalize({"a": value}).decode("utf-8"),
            '{"a":"\\b\\t\\n\\f\\r\\"\\\\\\u0000\\u001f\u007f"}',
        )

    def test_non_ascii_is_literal_not_escaped(self):
        self.assertEqual(
            jcs.canonicalize({"k": "\u00e9"}), '{"k":"\u00e9"}'.encode("utf-8")
        )

    def test_no_whitespace(self):
        self.assertEqual(
            jcs.canonicalize({"b": [1.0, 2.0], "a": {}}).decode(),
            '{"a":{},"b":[1,2]}',
        )

    def test_duplicate_keys_rejected(self):
        with self.assertRaises(jcs.CanonicalizationError):
            jcs.parse('{"a":1,"a":2}')

    def test_bom_rejected(self):
        with self.assertRaises(jcs.CanonicalizationError):
            jcs.parse_bytes(b"\xef\xbb\xbf{}")

    def test_oversized_integer_rejected_not_rounded(self):
        # 2**53 + 1 is not exactly representable as a double. Silently rounding
        # it would produce a hash neither party could reproduce.
        with self.assertRaises(jcs.CanonicalizationError):
            jcs.canonicalize({"n": 2 ** 53 + 1})


class TestJCSSurrogates(unittest.TestCase):
    """RFC 8785 section 3.2.2.2 on invalid Unicode:

        "Since invalid Unicode data like 'lone surrogates' (e.g., U+DEAD) may
        lead to interoperability issues including broken signatures,
        occurrences of such data MUST cause a compliant JCS implementation to
        terminate with an appropriate error."

    Terminate with an error -- not substitute U+FFFD, not emit CESU-8, and not
    raise UnicodeEncodeError out of the middle of canonicalization, which is
    what this implementation used to do.

    Nothing in the Sentinel corpus reaches this path: every byte of every
    shipped bundle is ASCII and `aiExplanation` -- the one free-form model
    output field, and the one most likely to carry whatever a model emitted --
    is null in all six (REPORT.md F-6). These tests are its only coverage.
    """

    def test_lone_high_surrogate_in_a_value(self):
        with self.assertRaises(jcs.CanonicalizationError):
            jcs.canonicalize({"a": "\ud800"})

    def test_lone_low_surrogate_mid_string(self):
        with self.assertRaises(jcs.CanonicalizationError):
            jcs.canonicalize({"a": "before\udeadafter"})

    def test_lone_surrogate_in_an_object_key(self):
        with self.assertRaises(jcs.CanonicalizationError):
            jcs.canonicalize({"\udfff": 1})

    def test_reversed_surrogate_pair_is_two_lone_surrogates(self):
        with self.assertRaises(jcs.CanonicalizationError):
            jcs.canonicalize({"a": "\udc00\ud800"})

    def test_nested_inside_an_array(self):
        with self.assertRaises(jcs.CanonicalizationError):
            jcs.canonicalize({"a": [{"b": ["\ud800"]}]})

    def test_the_path_a_real_bundle_takes(self):
        # json.loads decodes the \ud800 escape into a lone surrogate without
        # complaint, so the bad data arrives already parsed.
        value = jcs.parse('{"a":"\\ud800"}')
        self.assertEqual(value, {"a": "\ud800"})
        with self.assertRaises(jcs.CanonicalizationError):
            jcs.canonicalize(value)

    def test_the_error_is_a_jcs_error_not_a_codec_crash(self):
        with self.assertRaises(jcs.CanonicalizationError) as ctx:
            jcs.canonicalize({"a": "\ud800"})
        self.assertNotIsInstance(ctx.exception, UnicodeEncodeError)
        self.assertIn("3.2.2.2", str(ctx.exception),
                      "the error should cite the rule it enforces")

    def test_a_valid_surrogate_pair_is_unaffected(self):
        # The control. An astral character is not invalid Unicode; it is one
        # code point that happens to need two UTF-16 code units. It must still
        # canonicalize, and literally, per section 3.2.2.2.
        self.assertEqual(jcs.canonicalize({"a": "\U0001f600"}),
                         '{"a":"\U0001f600"}'.encode("utf-8"))
        self.assertEqual(jcs.parse('{"a":"\\ud83d\\ude00"}'), {"a": "\U0001f600"})
        # And the UTF-16 key-sorting rule still sees it as a surrogate pair.
        self.assertEqual(jcs.canonicalize({"�": 1, "\U0001f600": 2}),
                         '{"\U0001f600":2,"�":1}'.encode("utf-8"))

    def test_cesu8_input_bytes_are_a_clean_error(self):
        # A surrogate encoded directly as three UTF-8 bytes: rejected at the
        # decode step, as a CanonicalizationError rather than a UnicodeDecodeError.
        with self.assertRaises(jcs.CanonicalizationError):
            jcs.parse_bytes(b'{"a":"\xed\xa0\x80"}')

    def test_non_string_object_key_is_a_clean_error(self):
        # Same family: this branch used to be unreachable because the sort key
        # called .encode() on the key first and raised AttributeError.
        with self.assertRaises(jcs.CanonicalizationError):
            jcs.canonicalize({1: "a"})

    def test_a_bundle_with_a_lone_surrogate_fails_verification(self):
        # End to end: a verification failure with a named reason, not a
        # traceback out of the middle of the run.
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = stage(os.path.join(SAMPLES, "case-1-allow"), tmp)
        bundle = read_json(target, "evidence.json")
        self.assertIsNone(bundle["aiExplanation"])
        bundle["aiExplanation"] = "the model said \ud800"
        write_json(os.path.join(target, "evidence.json"), bundle)

        ok, checks = verify.verify_sample(target)  # must not raise
        self.assertFalse(ok)
        canon = [c for c in checks if "recanonicalization" in c.name]
        self.assertTrue(canon and not canon[0].ok)
        self.assertIn("surrogate", canon[0].detail)


class TestSecp256k1(unittest.TestCase):
    def test_known_private_key_to_address(self):
        # Anvil account #0, a published test key.
        priv = 0xAC0974BEC39A17E36BA4A6B4D238FF944BACB478CBED5EFCAE784D7BF4F2FF80
        self.assertEqual(
            public_key_to_address(point_mul(priv, G)),
            "0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266",
        )

    def test_signer_key_to_address(self):
        # Anvil account #1, which domain.json names as the Sentinel signer.
        priv = 0x59C6995E998F97A5A0044966F0945389DC9E86DAE88C7A8412F4603B6B78690D
        self.assertEqual(
            public_key_to_address(point_mul(priv, G)),
            "0x70997970c51812dc3a010c7d01b50e0d17dc79c8",
        )

    def test_group_order(self):
        self.assertIsNone(point_mul(N, G))


# ---------------------------------------------------------------------------
# End-to-end against every sample
# ---------------------------------------------------------------------------

class TestSamples(unittest.TestCase):
    def test_every_sample_verifies(self):
        dirs = sample_dirs()
        # Five §4.2 demonstration samples plus `edge-single-reason-code`, added
        # 2026-08-15 for A-027: no sample committed to exactly ONE reason code,
        # so nothing pinned the no-trailing-delimiter edge of reasonCodesHash and
        # a producer emitting `code + delimiter` for a one-element set hashed
        # identically to a correct one on every artifact a third party could get.
        # The count assertion stays -- it is what would notice the sample set
        # silently shrinking -- and is raised deliberately, not deleted.
        self.assertEqual(len(dirs), 6, "expected the five §4.2 samples plus the single-reason-code edge")
        for path in dirs:
            with self.subTest(sample=os.path.basename(path)):
                ok, checks = verify.verify_sample(path)
                failures = [c.name for c in checks if not c.ok]
                self.assertTrue(ok, f"failing checks: {failures}")

    def test_canonical_bytes_are_exact(self):
        for path in sample_dirs():
            with self.subTest(sample=os.path.basename(path)):
                with open(os.path.join(path, "evidence.json"), "rb") as handle:
                    parsed = jcs.parse_bytes(handle.read())
                with open(os.path.join(path, "evidence.canonical.json"), "rb") as handle:
                    expected = handle.read()
                self.assertEqual(jcs.canonicalize(parsed), expected)
                self.assertFalse(expected.endswith(b"\n"),
                                 "fixture is documented as having no trailing newline")

    def test_canonicalization_is_idempotent(self):
        for path in sample_dirs():
            with self.subTest(sample=os.path.basename(path)):
                with open(os.path.join(path, "evidence.canonical.json"), "rb") as handle:
                    canonical = handle.read()
                self.assertEqual(jcs.canonicalize(jcs.parse_bytes(canonical)), canonical)

    def test_verdict_encoding_matches_case_labels(self):
        index = expected_verdicts()
        for path in sample_dirs():
            case = os.path.basename(path)
            with self.subTest(sample=case):
                doc = read_json(path, "receipt.json")
                if not doc.get("receipt"):
                    continue
                decoded = verify.VERDICT_NAMES[int(doc["receipt"]["verdict"])]
                self.assertEqual(decoded, index[case]["verdict"])

    def test_all_verdict_values_are_covered(self):
        seen = set()
        for path in sample_dirs():
            doc = read_json(path, "receipt.json")
            if doc.get("receipt"):
                seen.add(int(doc["receipt"]["verdict"]))
        self.assertEqual(seen, {0, 1, 2},
                         "samples must pin all three verdict encodings")

    def test_cli_exit_code_zero(self):
        with open(os.devnull, "w") as devnull:
            saved, sys.stdout = sys.stdout, devnull
            try:
                self.assertEqual(verify.main(["--all", SAMPLES]), 0)
            finally:
                sys.stdout = saved

    def test_cli_exit_code_nonzero_on_missing_sample(self):
        with open(os.devnull, "w") as devnull:
            saved, sys.stdout = sys.stdout, devnull
            try:
                self.assertEqual(verify.main([os.path.join(SAMPLES, "no-such-case")]), 1)
            finally:
                sys.stdout = saved


# ---------------------------------------------------------------------------
# Negative tests: a verifier that cannot fail is not a verifier
# ---------------------------------------------------------------------------

class TestTamper(unittest.TestCase):
    def test_every_tamper_mode_behaves_as_specified(self):
        # Most modes must be rejected. The modes in TAMPER_MUST_STILL_VERIFY
        # are controls that must NOT break verification -- see
        # TestReasonCodeTamper.test_pure_reorder_still_verifies.
        exercised = 0
        for path in sample_dirs():
            for mode in verify.TAMPER_MODES:
                with self.subTest(sample=os.path.basename(path), mode=mode):
                    try:
                        ok, _ = verify.verify_sample(path, tamper=mode)
                    except verify.NotApplicable:
                        continue  # this sample's shape cannot express the mode
                    exercised += 1
                    if mode in verify.TAMPER_MUST_STILL_VERIFY:
                        self.assertTrue(ok, f"{mode} was WRONGLY REJECTED")
                    else:
                        self.assertFalse(ok, f"{mode} was WRONGLY ACCEPTED")
        # 6 samples x 3 core modes = 18; reason-code modes 20 (case-1's empty
        # list makes 3 N/A, and edge-single-reason-code's one-element list makes
        # reorder N/A); override modes 4 (only case-4-review has one).
        #
        # Was 36 across 5 samples before `edge-single-reason-code` was added for
        # A-027. The six new cases are the point of that sample: the reason-code
        # tamper modes now run against a set of size ONE, which is the size the
        # published hash construction is most easily got wrong at.
        self.assertEqual(exercised, 42, "expected 42 applicable tamper cases")

    def test_evidence_tamper_breaks_the_receipt_binding(self):
        # Specifically: it must fail the receipt.evidenceHash check, not merely
        # the file comparison. Otherwise a verifier handed only a bundle and a
        # receipt would still accept.
        ok, checks = verify.verify_sample(sample_dirs()[0], tamper="evidence")
        self.assertFalse(ok)
        binding = [c for c in checks if "evidenceHash binds" in c.name]
        self.assertEqual(len(binding), 1)
        self.assertFalse(binding[0].ok)

    def test_receipt_tamper_breaks_signer_recovery(self):
        ok, checks = verify.verify_sample(sample_dirs()[0], tamper="receipt")
        self.assertFalse(ok)
        recovery = [c for c in checks if "recovered signer ==" in c.name]
        self.assertTrue(recovery and not all(c.ok for c in recovery))

    def test_wrong_domain_is_rejected(self):
        # A receipt for chain 31337 must not verify when replayed against
        # another chain id. This is the whole point of domain separation.
        path = sample_dirs()[0]
        with tempfile.TemporaryDirectory() as tmp:
            domain = read_json(SAMPLES, "domain.json")
            domain["chainId"] = "1"
            domain_path = os.path.join(tmp, "domain.json")
            with open(domain_path, "w") as handle:
                json.dump(domain, handle)
            ok, _ = verify.verify_sample(path, domain_path=domain_path)
            self.assertFalse(ok, "a cross-chain replay was accepted")

    def test_wrong_verifying_contract_is_rejected(self):
        path = sample_dirs()[0]
        with tempfile.TemporaryDirectory() as tmp:
            domain = read_json(SAMPLES, "domain.json")
            domain["verifyingContract"] = "0x" + "11" * 20
            domain_path = os.path.join(tmp, "domain.json")
            with open(domain_path, "w") as handle:
                json.dump(domain, handle)
            ok, _ = verify.verify_sample(path, domain_path=domain_path)
            self.assertFalse(ok)

    def test_wrong_type_string_would_not_verify(self):
        # Guards the F-1 finding: the uint widths §5 omits are load-bearing.
        # Swapping uint16 schemaVersion for uint256 changes only the type
        # string, yet the digest and therefore the recovered address change.
        original = eip712.RECEIPT_FIELDS
        try:
            eip712.RECEIPT_FIELDS = [
                ("uint256", name) if name == "schemaVersion" else (t, name)
                for t, name in original
            ]
            ok, _ = verify.verify_sample(sample_dirs()[0])
            self.assertFalse(ok, "the uint widths are apparently not load-bearing")
        finally:
            eip712.RECEIPT_FIELDS = original

    def test_all_receipt_uint_widths_are_load_bearing(self):
        # Every uintN in the type string changes the digest if widened, even
        # though the *encoded bytes* are identical (all left-padded to 32).
        # This is the F-1 trap, tested field by field.
        original = eip712.RECEIPT_FIELDS
        widened = [(t, n) for t, n in original if t.startswith("uint") and t != "uint256"]
        self.assertTrue(widened, "expected some non-uint256 fields")
        try:
            for target_type, target_name in widened:
                with self.subTest(field=target_name, was=target_type):
                    eip712.RECEIPT_FIELDS = [
                        ("uint256", n) if n == target_name else (t, n)
                        for t, n in original
                    ]
                    ok, _ = verify.verify_sample(sample_dirs()[0])
                    self.assertFalse(ok)
        finally:
            eip712.RECEIPT_FIELDS = original

    def test_mandate_hash_is_load_bearing(self):
        # Swapping in another sample's mandate must fail, or the receipt is not
        # actually bound to the mandate it claims.
        import shutil
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = os.path.join(tmp, "case-swapped")
        shutil.copytree(sample_dirs()[0], target)
        shutil.copy(os.path.join(SAMPLES, "domain.json"), tmp)
        other = os.path.join(SAMPLES, "case-4-review-failmode-review", "mandate.json")
        shutil.copy(other, os.path.join(target, "mandate.json"))
        ok, checks = verify.verify_sample(target)
        self.assertFalse(ok, "a swapped mandate was accepted")
        self.assertTrue(any("mandateHash" in c.name and not c.ok for c in checks))

    def test_unknown_receipt_field_is_rejected(self):
        with self.assertRaises(eip712.EncodingError):
            eip712.receipt_struct_hash({
                **read_json(sample_dirs()[0], "receipt.json")["receipt"],
                "surpriseField": "0x00",
            })


# ---------------------------------------------------------------------------
# Refusal shape
# ---------------------------------------------------------------------------

class TestRefusedShape(unittest.TestCase):
    """No shipped sample sets refused=true (REPORT.md F-13), so the shape is
    synthesised here rather than left untested.

    §5.4 defines `SignedDecisionReceipt` as the payload plus a signature and
    defines no refusal record at all -- the string "refus" does not occur
    anywhere in the published specification. So an unsigned refusal claim is
    not a weaker receipt, it is not a receipt: nothing about it is
    authenticated, and it cannot be certified. See REPORT.md F-13.
    """

    def _refused_copy(self, body, case=None):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = os.path.join(tmp, "case-refused")
        shutil.copytree(case or sample_dirs()[0], target)
        write_json(os.path.join(target, "receipt.json"), body)
        shutil.copy(os.path.join(SAMPLES, "domain.json"), tmp)
        return target

    def test_unsigned_refusal_is_not_certified(self):
        path = self._refused_copy({
            "refused": True,
            "refusalReason": "signer declined: evidence anchor unavailable",
            "receipt": None,
            "signature": None,
        })
        ok, checks = verify.verify_sample(path)
        self.assertFalse(ok, "an unsigned refusal claim was certified")
        failed = [c for c in checks if not c.ok]
        self.assertTrue(any("signed receipt is present" in c.name for c in failed))
        # What the tool *could* establish is still reported as established:
        # refusing to certify is not refusing to check.
        self.assertTrue(any("recanonicalization" in c.name and c.ok for c in checks))
        self.assertTrue(any("keccak256(canonical bytes)" in c.name and c.ok
                            for c in checks))

    def test_an_allow_cannot_be_presented_as_a_refusal(self):
        # The reported symptom, exactly: take a real ALLOW bundle, replace
        # receipt.json with a bare refusal claim, and the CLI used to print
        # `=> PASS` and exit 0 while evidence.json beside it said ALLOW.
        allow_case = os.path.join(SAMPLES, "case-1-allow")
        self.assertEqual(read_json(allow_case, "evidence.json")["verdict"], "ALLOW")
        path = self._refused_copy(
            {"refused": True, "refusalReason": "nothing to see here"},
            case=allow_case)
        ok, checks = verify.verify_sample(path)
        self.assertFalse(ok)
        detail = "\n".join(c.detail for c in checks if not c.ok)
        self.assertIn("ALLOW", detail,
                      "the report should name the verdict being suppressed")
        with open(os.devnull, "w") as devnull:
            saved, sys.stdout = sys.stdout, devnull
            try:
                self.assertEqual(verify.main([path]), 1, "exit status must be non-zero")
            finally:
                sys.stdout = saved

    def test_refused_with_omitted_keys_does_not_crash(self):
        path = self._refused_copy({"refused": True})
        ok, checks = verify.verify_sample(path)  # must not raise
        self.assertFalse(ok)
        self.assertTrue(any("signed receipt is present" in c.name and not c.ok
                            for c in checks))

    def test_a_receipt_without_a_signature_is_not_certified(self):
        # "refused" is not the only way to present nothing signed: dropping the
        # signature leaves a well-formed receipt body that nothing attests to.
        doc = read_json(sample_dirs()[0], "receipt.json")
        doc.pop("signature")
        path = self._refused_copy(doc)
        ok, checks = verify.verify_sample(path)
        self.assertFalse(ok, "a receipt with no signature was certified")
        self.assertTrue(any("signed receipt is present" in c.name and not c.ok
                            for c in checks))

    def test_refused_but_signed_is_a_failure(self):
        # A refusal that nonetheless carries a signed receipt is contradictory
        # and must not pass.
        original = read_json(sample_dirs()[0], "receipt.json")
        original["refused"] = True
        path = self._refused_copy(original)
        ok, checks = verify.verify_sample(path)
        self.assertFalse(ok)
        self.assertTrue(any("self-consistent" in c.name for c in checks))


class TestDerivedConstants(unittest.TestCase):
    """Pins the values REPORT.md documents as derived rather than specified, so
    that a later §5 amendment that contradicts them breaks the suite loudly."""

    def test_mandate_policy_action_type_strings(self):
        self.assertEqual(
            eip712.MANDATE_STRUCT_NAME + "(" + ",".join(
                f"{t} {n}" for t, n in eip712.MANDATE_FIELDS) + ")",
            "MandatePayload(uint16 schemaVersion,bytes32 mandateId,"
            "address principal,address vault,uint256 chainId,address target,"
            "bytes32 targetCodeHash,bytes4 selector,uint256 maxNativeValueWei,"
            "bytes32 purposeKind,bytes32 resourceId,address beneficiary,"
            "uint64 durationSeconds,bool recurringAllowed,uint64 validAfter,"
            "uint64 validUntil,bytes32 policyHash)")

    def test_receipt_type_string(self):
        self.assertEqual(
            eip712.RECEIPT_TYPE,
            "DecisionReceiptPayload(uint16 schemaVersion,bytes32 decisionId,"
            "bytes32 actionHash,bytes32 mandateHash,bytes32 policyHash,"
            "uint8 verdict,bytes32 reasonCodesHash,bytes32 evidenceHash,"
            "uint256 simulationBlockNumber,bytes32 simulationBlockHash,"
            "uint64 issuedAt,uint64 expiresAt,address signer)",
        )

    def test_domain_separator_is_stable(self):
        domain = read_json(SAMPLES, "domain.json")
        self.assertEqual(
            "0x" + eip712.domain_separator(domain).hex(),
            "0x6fdefb2adc6b65ee8595f3abb969a21492cdd583459829b295b84ed45bd7e02c",
        )

    def test_field_order_follows_section_5_4(self):
        self.assertEqual(
            [name for _, name in eip712.RECEIPT_FIELDS],
            ["schemaVersion", "decisionId", "actionHash", "mandateHash",
             "policyHash", "verdict", "reasonCodesHash", "evidenceHash",
             "simulationBlockNumber", "simulationBlockHash", "issuedAt",
             "expiresAt", "signer"],
        )

    def test_empty_reason_codes_hash_is_keccak_of_empty(self):
        # §5.4 as amended by D-022 states this explicitly; case-1 pins it.
        doc = read_json(SAMPLES, "case-1-allow", "receipt.json")
        self.assertEqual(doc["reasonCodes"], [])
        self.assertEqual(doc["receipt"]["reasonCodesHash"], keccak256_hex(b""))
        self.assertEqual(reasoncodes.reason_codes_hash_hex([]), keccak256_hex(b""))


# ---------------------------------------------------------------------------
# reasonCodesHash — §5.4 as amended by D-022 (was F-3, NOT VERIFIABLE)
# ---------------------------------------------------------------------------

class TestReasonCodes(unittest.TestCase):
    def test_every_sample_reason_codes_hash_matches(self):
        for path in sample_dirs():
            with self.subTest(sample=os.path.basename(path)):
                doc = read_json(path, "receipt.json")
                self.assertIn("reasonCodes", doc, "sample must publish reasonCodes")
                self.assertEqual(
                    reasoncodes.reason_codes_hash_hex(doc["reasonCodes"]),
                    doc["receipt"]["reasonCodesHash"],
                )

    def test_signer_findings_are_inside_the_committed_set(self):
        for path in sample_dirs():
            with self.subTest(sample=os.path.basename(path)):
                doc = read_json(path, "receipt.json")
                self.assertTrue(
                    set(doc["signerFindings"]) <= set(doc["reasonCodes"]),
                    "§5.4 defines the committed set as the union of evaluator "
                    "codes and signer findings",
                )

    def test_samples_cover_both_halves_of_the_union(self):
        # The union rule is only exercised if some sample actually carries a
        # signer finding the evaluator did not raise.
        signer_only = set()
        for path in sample_dirs():
            doc = read_json(path, "receipt.json")
            evaluator = {c for c in doc["reasonCodes"] if not c.startswith("SIGNER_")}
            signer_only |= {c for c in doc["signerFindings"] if c not in evaluator}
        self.assertTrue(signer_only, "no sample exercises the signer half of the union")

    def test_published_lists_are_already_canonical(self):
        for path in sample_dirs():
            with self.subTest(sample=os.path.basename(path)):
                doc = read_json(path, "receipt.json")
                self.assertEqual(
                    doc["reasonCodes"],
                    reasoncodes.committed_set(doc["reasonCodes"]),
                )

    def test_join_has_no_trailing_delimiter(self):
        self.assertEqual(reasoncodes.preimage(["A", "B"]), b"A\nB")
        self.assertEqual(reasoncodes.preimage(["A"]), b"A")
        self.assertEqual(reasoncodes.preimage([]), b"")

    def test_dedup_and_sort_are_applied(self):
        a = reasoncodes.reason_codes_hash_hex(["B", "A", "B"])
        b = reasoncodes.reason_codes_hash_hex(["A", "B"])
        self.assertEqual(a, b)

    def test_sort_is_byte_order_so_case_matters(self):
        # Byte order, not case-insensitive collation: uppercase sorts first.
        self.assertEqual(reasoncodes.committed_set(["a", "B"]), ["B", "a"])

    def test_invalid_identifiers_are_rejected_not_sanitised(self):
        for bad in ["EVAL OK", "EVAL/OK", "", "A" * 65, "ÉVAL", "EVAL\nOK",
                    "EVAL_OK\n", None, 7, ["EVAL_OK"]]:
            with self.subTest(bad=bad):
                with self.assertRaises(reasoncodes.ReasonCodeError):
                    reasoncodes.validate(bad)

    def test_valid_identifiers_are_accepted(self):
        for good in ["A", "EVAL_TARGET_BOUND", "a.b:c-d_e", "A" * 64, "0"]:
            with self.subTest(good=good):
                self.assertEqual(reasoncodes.validate(good), good)

    def test_trailing_newline_is_rejected_despite_the_printed_pattern(self):
        # REPORT.md F-3: the printed pattern ^[A-Za-z0-9_.:-]{1,64}$ does NOT
        # reject a trailing newline under Python's re.match, because `$` matches
        # before one. Guard that this implementation uses absolute anchors.
        import re
        self.assertIsNotNone(re.match(r"^[A-Za-z0-9_.:-]{1,64}$", "EVAL_OK\n"))
        with self.assertRaises(reasoncodes.ReasonCodeError):
            reasoncodes.validate("EVAL_OK\n")

    def test_delimiter_injection_would_collide(self):
        # Demonstrates why the grammar is load-bearing rather than cosmetic:
        # an identifier containing the delimiter makes two distinct committed
        # sets hash identically. The validator is the only thing preventing it.
        from keccak import keccak256_hex
        self.assertEqual(
            keccak256_hex("EVIL\nINJECTED".encode()),
            reasoncodes.reason_codes_hash_hex(["EVIL", "INJECTED"]),
        )
        with self.assertRaises(reasoncodes.ReasonCodeError):
            reasoncodes.validate("EVIL\nINJECTED")


class TestReasonCodeTamper(unittest.TestCase):
    REJECT_MODES = ("reasons-substitute", "reasons-add", "reasons-remove")

    def test_substitution_addition_removal_are_rejected(self):
        for path in sample_dirs():
            for mode in self.REJECT_MODES:
                with self.subTest(sample=os.path.basename(path), mode=mode):
                    try:
                        ok, checks = verify.verify_sample(path, tamper=mode)
                    except verify.NotApplicable:
                        continue  # empty reason-code list; nothing to mutate
                    self.assertFalse(ok, f"{mode} was WRONGLY ACCEPTED")
                    hashes = [c for c in checks
                              if "reasonCodesHash recomputed" in c.name]
                    self.assertEqual(len(hashes), 1)
                    self.assertFalse(hashes[0].ok)

    def test_pure_reorder_still_verifies(self):
        # The control case. The committed set is sorted before hashing, so the
        # order of the published list carries no information and must not be
        # able to fail an otherwise-good receipt.
        applied = 0
        for path in sample_dirs():
            with self.subTest(sample=os.path.basename(path)):
                try:
                    ok, checks = verify.verify_sample(path, tamper="reasons-reorder")
                except verify.NotApplicable:
                    continue
                applied += 1
                self.assertTrue(
                    ok, "a pure reorder was rejected: this verifier is hashing "
                        "the list as given, not the set")
                hashes = [c for c in checks if "reasonCodesHash recomputed" in c.name]
                self.assertTrue(hashes and hashes[0].ok)
        self.assertGreaterEqual(applied, 4, "reorder must be exercised")

    def test_removing_a_signer_finding_is_detected(self):
        # Pins the union-vs-published design choice (REPORT.md F-3). If the
        # verifier re-unioned reasonCodes with signerFindings instead of hashing
        # the published list, dropping a code that also appears in
        # signerFindings would be silently repaired and go undetected.
        import shutil
        path = os.path.join(SAMPLES, "case-4-review-failmode-review")
        doc = read_json(path, "receipt.json")
        victim = doc["signerFindings"][0]
        self.assertIn(victim, doc["reasonCodes"])
        doc["reasonCodes"] = [c for c in doc["reasonCodes"] if c != victim]

        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = os.path.join(tmp, "case-dropped")
        shutil.copytree(path, target)
        shutil.copy(os.path.join(SAMPLES, "domain.json"), tmp)
        with open(os.path.join(target, "receipt.json"), "w") as handle:
            json.dump(doc, handle)

        ok, checks = verify.verify_sample(target)
        self.assertFalse(ok, "a dropped signer finding was accepted")
        self.assertTrue(any("reasonCodesHash recomputed" in c.name and not c.ok
                            for c in checks))
        self.assertTrue(any("signerFindings" in c.name and not c.ok
                            for c in checks),
                        "the subset invariant should also have caught it")

    def test_missing_reason_codes_array_fails(self):
        import shutil
        doc = read_json(sample_dirs()[0], "receipt.json")
        doc.pop("reasonCodes", None)
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = os.path.join(tmp, "case-nolist")
        shutil.copytree(sample_dirs()[0], target)
        shutil.copy(os.path.join(SAMPLES, "domain.json"), tmp)
        with open(os.path.join(target, "receipt.json"), "w") as handle:
            json.dump(doc, handle)
        ok, checks = verify.verify_sample(target)
        self.assertFalse(ok, "a receipt with no reasonCodes list was accepted")

    def test_malformed_identifier_fails_verification(self):
        import shutil
        doc = read_json(os.path.join(SAMPLES, "case-3-wrong-purpose-block"),
                        "receipt.json")
        doc["reasonCodes"] = doc["reasonCodes"] + ["BAD CODE WITH SPACES"]
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = os.path.join(tmp, "case-badid")
        shutil.copytree(os.path.join(SAMPLES, "case-3-wrong-purpose-block"), target)
        shutil.copy(os.path.join(SAMPLES, "domain.json"), tmp)
        with open(os.path.join(target, "receipt.json"), "w") as handle:
            json.dump(doc, handle)
        ok, checks = verify.verify_sample(target)
        self.assertFalse(ok)
        grammar = [c for c in checks if "identifier matches" in c.name]
        self.assertTrue(grammar and not grammar[0].ok)


# ---------------------------------------------------------------------------
# §5.5 override authorization and the chain-binding question (D-023)
# ---------------------------------------------------------------------------

OVERRIDE_SAMPLE = os.path.join(SAMPLES, "case-4-review-failmode-review")


class TestPublishedTypeStrings(unittest.TestCase):
    """§5.8 now publishes all six type strings. Check the published spec is
    sufficient -- and that it agrees with what was independently recovered."""

    def _published(self):
        import re
        spec = os.path.join(REPO, "Sentinel_Protocol_Lab_Proposal_v0_2.md")
        with open(spec, encoding="utf-8") as handle:
            text = handle.read()
        block = text.split("### 5.8 EIP-712 Type Strings")[1].split("---")[0]
        out = {}
        for line in block.split("\n"):
            m = re.match(r"^([A-Za-z0-9]+)\((.*)\)$", line.strip())
            if m:
                out[m.group(1)] = line.strip()
        return out

    def test_all_six_are_published(self):
        self.assertEqual(len(self._published()), 6)

    def test_recovered_strings_match_the_published_ones(self):
        pub = self._published()
        def render(name, fields):
            return name + "(" + ",".join(f"{t} {n}" for t, n in fields) + ")"
        cases = {
            "EIP712Domain": eip712.DOMAIN_TYPE,
            "DecisionReceiptPayload": eip712.RECEIPT_TYPE,
            "MandatePayload": render(eip712.MANDATE_STRUCT_NAME, eip712.MANDATE_FIELDS),
            "PolicyPayload": render(eip712.POLICY_STRUCT_NAME, eip712.POLICY_FIELDS),
            "ActionPayload": render(eip712.ACTION_STRUCT_NAME, eip712.ACTION_FIELDS),
            "OverrideAuthorizationPayload": render(
                eip712.OVERRIDE_STRUCT_NAME, eip712.OVERRIDE_FIELDS),
        }
        for name, mine in cases.items():
            with self.subTest(struct=name):
                self.assertEqual(pub[name], mine)


class TestOverride(unittest.TestCase):
    def _doc(self):
        return read_json(OVERRIDE_SAMPLE, "override.json")

    def test_override_verifies(self):
        ok, checks = verify.verify_sample(OVERRIDE_SAMPLE)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])
        names = [c.name for c in checks]
        for expected in ("override signature recovers ownerAddress",
                         "override.reviewReceiptHash == this receipt's EIP-712 hashStruct",
                         "override.actionNonce == action.actionNonce"):
            self.assertIn(expected, names)

    def test_owner_is_not_the_sentinel_signer(self):
        # §3.3(7): the override must be a credential the isolated signer cannot
        # mint. If these were the same key the property would be vacuous.
        doc = self._doc()
        receipt = read_json(OVERRIDE_SAMPLE, "receipt.json")["receipt"]
        self.assertNotEqual(doc["ownerAddress"].lower(), receipt["signer"].lower())

    def test_owner_is_the_mandate_principal(self):
        doc = self._doc()
        mandate = read_json(OVERRIDE_SAMPLE, "mandate.json")
        self.assertEqual(doc["ownerAddress"].lower(), mandate["principal"].lower())

    def test_review_receipt_hash_is_the_receipt_hashstruct(self):
        doc = self._doc()
        receipt = read_json(OVERRIDE_SAMPLE, "receipt.json")["receipt"]
        self.assertEqual(
            doc["override"]["reviewReceiptHash"],
            "0x" + eip712.receipt_struct_hash(receipt).hex(),
        )

    def test_only_review_receipts_carry_an_override(self):
        # §5.5: "A block receipt cannot be overridden."
        for path in sample_dirs():
            has = os.path.isfile(os.path.join(path, "override.json"))
            verdict = verify.VERDICT_NAMES[
                int(read_json(path, "receipt.json")["receipt"]["verdict"])]
            if has:
                self.assertEqual(verdict, "REVIEW", f"{path} overrides a {verdict}")

    def test_every_override_tamper_mode_is_rejected(self):
        modes = [m for m in verify.TAMPER_MODES if m.startswith("override-")]
        self.assertGreaterEqual(len(modes), 3)
        for mode in modes:
            with self.subTest(mode=mode):
                ok, _ = verify.verify_sample(OVERRIDE_SAMPLE, tamper=mode)
                self.assertFalse(ok, f"{mode} was WRONGLY ACCEPTED")

    def test_wrongkey_signature_is_valid_but_from_the_wrong_party(self):
        # The forged signature must be well-formed -- otherwise this only tests
        # signature parsing, not signer identity.
        from secp256k1 import sign_digest, recover_address
        doc = self._doc()
        domain = read_json(SAMPLES, "domain.json")
        digest = eip712.override_digest(domain, doc["override"])
        forged = sign_digest(digest, verify._SENTINEL_SIGNER_TEST_KEY)
        recovered = recover_address(digest, forged)
        receipt = read_json(OVERRIDE_SAMPLE, "receipt.json")["receipt"]
        self.assertEqual(recovered, receipt["signer"].lower(),
                         "the forgery should recover the Sentinel signer")
        self.assertNotEqual(recovered, doc["ownerAddress"].lower())
        ok, checks = verify.verify_sample(OVERRIDE_SAMPLE, tamper="override-wrongkey")
        self.assertFalse(ok)
        self.assertTrue(any("recovers ownerAddress" in c.name and not c.ok
                            for c in checks))


class TestOverrideChainBinding(unittest.TestCase):
    """D-023: measure the §5.5 chain-binding concern rather than reasoning about it.

    OverrideAuthorizationPayload carries neither chainId nor vault. Two
    independent mechanisms are claimed to bind it anyway: the EIP-712 domain
    separator, and the chain-bound payload hashes it references.
    """

    def _parts(self, domain, mandate, policy, action, receipt):
        mh = "0x" + eip712.mandate_hash(mandate).hex()
        ph = "0x" + eip712.policy_hash(policy).hex()
        act = dict(action, mandateHash=mh, policyHash=ph)
        ah = "0x" + eip712.action_hash(act).hex()
        rec = dict(receipt, actionHash=ah, mandateHash=mh, policyHash=ph)
        return mh, ph, ah, "0x" + eip712.receipt_struct_hash(rec).hex()

    def _load(self):
        return (read_json(SAMPLES, "domain.json"),
                read_json(OVERRIDE_SAMPLE, "mandate.json"),
                read_json(OVERRIDE_SAMPLE, "policy.json"),
                read_json(OVERRIDE_SAMPLE, "action.json"),
                read_json(OVERRIDE_SAMPLE, "receipt.json")["receipt"],
                read_json(OVERRIDE_SAMPLE, "override.json"))

    def _replays(self, domain, doc):
        from secp256k1 import recover_address
        try:
            got = recover_address(eip712.override_digest(domain, doc["override"]),
                                  doc["ownerSignature"])
        except Exception:
            return False
        return got == doc["ownerAddress"].lower()

    def test_baseline_replays_on_its_own_deployment(self):
        domain, m, p, a, r, doc = self._load()
        self.assertTrue(self._replays(domain, doc))

    def test_other_chain_breaks_both_mechanisms(self):
        domain, m, p, a, r, doc = self._load()
        base = self._parts(domain, m, p, a, r)
        d2 = dict(domain, chainId="8453")
        moved = self._parts(d2, dict(m, chainId="8453"), dict(p, chainId="8453"),
                            dict(a, chainId="8453"), r)
        self.assertNotEqual(base, moved, "referenced hashes must change")
        self.assertFalse(self._replays(d2, doc), "domain separator must change")

    def test_other_vault_breaks_both_mechanisms(self):
        domain, m, p, a, r, doc = self._load()
        nv = "0x" + "11" * 20
        base = self._parts(domain, m, p, a, r)
        d2 = dict(domain, verifyingContract=nv)
        moved = self._parts(d2, dict(m, vault=nv), dict(p, vault=nv),
                            dict(a, vault=nv), r)
        self.assertNotEqual(base, moved)
        self.assertFalse(self._replays(d2, doc))

    def test_domain_separator_catches_what_the_hashes_cannot(self):
        # Changing only the domain name leaves every referenced hash identical.
        # Only the separator notices. Proves the separator does independent work.
        domain, m, p, a, r, doc = self._load()
        d2 = dict(domain, name="Sentinel2")
        self.assertEqual(self._parts(domain, m, p, a, r),
                         self._parts(d2, m, p, a, r))
        self.assertFalse(self._replays(d2, doc))

    def test_hashes_catch_what_the_domain_separator_cannot(self):
        # Substituting a different mandate on the SAME deployment leaves the
        # separator identical and the signature valid. Only the referenced
        # hashes notice. Proves the two mechanisms are genuinely independent.
        domain, m, p, a, r, doc = self._load()
        other = read_json(SAMPLES, "case-1-allow", "mandate.json")
        self.assertEqual(other["chainId"], m["chainId"])
        self.assertEqual(other["vault"].lower(), m["vault"].lower())
        self.assertNotEqual("0x" + eip712.mandate_hash(other).hex(),
                            "0x" + eip712.mandate_hash(m).hex())
        self.assertTrue(self._replays(domain, doc), "signature is unaffected")
        self.assertNotEqual(doc["override"]["mandateHash"],
                            "0x" + eip712.mandate_hash(other).hex())

    def test_receipt_is_chain_bound_transitively_despite_carrying_no_chainid(self):
        # The original F-2 worry in its sharpest form: DecisionReceiptPayload has
        # no chainId and no vault member, and reviewReceiptHash is a hash of it.
        domain, m, p, a, r, doc = self._load()
        self.assertNotIn("chainId", r)
        self.assertNotIn("vault", r)
        _, _, _, base_receipt = self._parts(domain, m, p, a, r)
        _, _, _, moved_receipt = self._parts(
            dict(domain, chainId="8453"), dict(m, chainId="8453"),
            dict(p, chainId="8453"), dict(a, chainId="8453"), r)
        self.assertNotEqual(base_receipt, moved_receipt,
                            "the receipt hashStruct must move with the chain")


# ---------------------------------------------------------------------------
# §3.3(4)/§3.3(5) chain and vault binding, established from the bundle
# ---------------------------------------------------------------------------

class TestChainAndVaultBinding(unittest.TestCase):
    """§5.8: the payload hashes are bare hashStruct values, so "Chain and vault
    binding for these hashes therefore comes solely from the `chainId` and
    `vault` members of the payloads themselves."

    domain.json is an unsigned side file supplied by whoever presents the
    bundle, and §5.8's own warning block says a receipt "is not
    self-describing" -- so the domain cannot be the authority on which
    deployment a bundle belongs to. These tests pin the checks that read the
    payload members instead.
    """

    def test_cross_payload_agreement_needs_no_domain_at_all(self):
        # §5.8's claim is about "a verifier that never saw the domain", so the
        # agreement checks must fire with no domain knowledge whatsoever.
        case = os.path.join(SAMPLES, "case-1-allow")
        mandate = read_json(case, "mandate.json")
        policy = read_json(case, "policy.json")
        action = dict(read_json(case, "action.json"), chainId="8453")
        checks = verify._binding_checks(
            [("mandate.json", mandate), ("policy.json", policy),
             ("action.json", action)], {})
        agreement = [c for c in checks if "all bind the same chainId" in c.name]
        self.assertTrue(agreement, "no cross-payload chainId check exists")
        self.assertFalse(agreement[0].ok)

    def test_cross_payload_vault_agreement_needs_no_domain_at_all(self):
        case = os.path.join(SAMPLES, "case-1-allow")
        mandate = dict(read_json(case, "mandate.json"), vault="0x" + "44" * 20)
        action = read_json(case, "action.json")
        checks = verify._binding_checks(
            [("mandate.json", mandate), ("action.json", action)], {})
        agreement = [c for c in checks if "all bind the same vault" in c.name]
        self.assertTrue(agreement)
        self.assertFalse(agreement[0].ok)

    def test_samples_pass_the_binding_checks(self):
        for path in sample_dirs():
            with self.subTest(sample=os.path.basename(path)):
                _, checks = verify.verify_sample(path)
                binding = [c for c in checks
                           if "bind the same" in c.name or "equals the presented" in c.name]
                self.assertEqual(len(binding), 4)
                self.assertTrue(all(c.ok for c in binding))

    def test_bundle_presented_under_another_deployments_domain_is_rejected(self):
        # A genuinely-signed bundle, re-presented with a domain.json naming a
        # different chain AND a different contract. The receipt is re-signed
        # with the published signer key, so every cryptographic check passes:
        # the signature is valid, it recovers receipt.signer, and it recovers
        # the address domain.json names. Only the payload members notice.
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        domain = read_json(SAMPLES, "domain.json")
        domain["chainId"] = "8453"
        domain["verifyingContract"] = "0x" + "22" * 20
        target = stage(os.path.join(SAMPLES, "case-1-allow"), tmp, domain)
        reseal(target, domain)

        ok, checks = verify.verify_sample(target)
        self.assertFalse(
            ok, "a bundle was certified against a domain naming another chain "
                "and another vault")
        for name in ("EIP-712 digest recomputed from §5.4 field list",
                     "recovered signer == receipt.signer",
                     "recovered signer == domain.json signerAddress",
                     "signature is EIP-2 canonical (low-s) and v in {27,28}"):
            found = [c for c in checks if c.name == name]
            self.assertTrue(found and found[0].ok,
                            f"{name} should still pass -- the point is that the "
                            "cryptography cannot notice this")
        self.assertEqual(
            sorted(c.name for c in checks if not c.ok),
            sorted(["every payload's chainId equals the presented domain's chainId (§5.8)",
                    "every payload's vault equals the presented domain's "
                    "verifyingContract (§5.8)"]))

    def test_mandate_naming_another_vault_than_the_action_is_rejected(self):
        # A fully self-consistent bundle whose mandate binds a different vault
        # than its action. Every hash is recomputed correctly and matches the
        # receipt; the receipt is validly signed. Nothing but the cross-payload
        # agreement check can see that two deployments are being described.
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        domain = read_json(SAMPLES, "domain.json")
        target = stage(os.path.join(SAMPLES, "case-1-allow"), tmp)

        mandate = read_json(target, "mandate.json")
        mandate["vault"] = "0x" + "33" * 20
        write_json(os.path.join(target, "mandate.json"), mandate)
        mandate_hash = "0x" + eip712.mandate_hash(mandate).hex()

        action = read_json(target, "action.json")
        action["mandateHash"] = mandate_hash
        write_json(os.path.join(target, "action.json"), action)
        action_hash = "0x" + eip712.action_hash(action).hex()

        doc = read_json(target, "receipt.json")
        doc["receipt"]["mandateHash"] = mandate_hash
        doc["receipt"]["actionHash"] = action_hash
        write_json(os.path.join(target, "receipt.json"), doc)
        reseal(target, domain)

        ok, checks = verify.verify_sample(target)
        self.assertFalse(ok, "a mandate binding a different vault than the "
                             "action it authorises was accepted")
        for name in ("recomputed mandateHash from §5.1 MandatePayload matches the receipt",
                     "recomputed actionHash from §5.3 ActionPayload matches the receipt",
                     "recovered signer == receipt.signer",
                     "action binds the same mandate and policy as the receipt"):
            found = [c for c in checks if c.name == name]
            self.assertTrue(found and found[0].ok,
                            f"{name} should still pass -- the bundle is internally "
                            "consistent, which is exactly the problem")
        self.assertIn("§5.1/§5.2/§5.3 payloads all bind the same vault (§3.3(4))",
                      [c.name for c in checks if not c.ok])

    def test_a_malformed_binding_member_fails_rather_than_being_skipped(self):
        checks = verify._binding_checks(
            [("mandate.json", {"chainId": "31337"})], {})
        self.assertEqual(len(checks), 1)
        self.assertFalse(checks[0].ok)
        self.assertIn("vault", checks[0].detail)


# ---------------------------------------------------------------------------
# Strict payload-field parsing: the recomputed hash must pin the document
# ---------------------------------------------------------------------------

class TestStrictFieldParsing(unittest.TestCase):
    """`mandateHash` and friends are recomputed from these documents and
    compared against the receipt. If several byte-distinct documents encode to
    the same 32-byte word, "the recomputed hash matches" stops being a
    statement about the document in front of the operator.

    §5 never states how a payload field is encoded in JSON at all, so what is
    accepted is a choice recorded in REPORT.md F-17, not a spec reading.
    """

    def test_only_one_spelling_of_an_integer_survives(self):
        spellings = ["86400", " 86400 ", "86400\n", "86_400", "0086400",
                     "+86400", "86400.0", 86400, 86400.0, 86400.9, True]
        accepted = []
        for spelling in spellings:
            try:
                accepted.append(eip712.encode_value("uint64", spelling))
            except eip712.EncodingError:
                continue
        self.assertEqual(len(accepted), 1,
                         "more than one spelling encodes, so equal hashes no "
                         "longer imply equal documents")
        self.assertEqual(accepted[0], (86400).to_bytes(32, "big"))

    def test_each_lossy_integer_spelling_is_named_in_its_own_error(self):
        for bad in (" 86400 ", "86_400", "0086400", "+86400", "-1", "",
                    "0x151800", "86400.0", 86400, 86400.0, 86400.9, True,
                    False, None, ["86400"]):
            with self.subTest(bad=bad):
                with self.assertRaises(eip712.EncodingError):
                    eip712.encode_value("uint64", bad)

    def test_zero_and_canonical_decimals_still_encode(self):
        for good, expected in (("0", 0), ("1", 1), ("31337", 31337),
                               ("4000000000", 4000000000)):
            with self.subTest(good=good):
                self.assertEqual(eip712.encode_value("uint256", good),
                                 expected.to_bytes(32, "big"))

    def test_bool_no_longer_reads_True_and_yes_as_false(self):
        # The old rule was `value in (True, "true", 1, "1")`, so "True",
        # "TRUE" and "yes" all encoded as FALSE -- silently, on a field called
        # recurringAllowed.
        for bad in ("True", "TRUE", "yes", "true", "false", "1", "0", 1, 0,
                    None, ""):
            with self.subTest(bad=bad):
                with self.assertRaises(eip712.EncodingError):
                    eip712.encode_value("bool", bad)
        self.assertEqual(eip712.encode_value("bool", True), (1).to_bytes(32, "big"))
        self.assertEqual(eip712.encode_value("bool", False), bytes(32))

    def test_hex_rejects_whitespace_and_a_missing_prefix(self):
        good = "0x70997970c51812dc3a010c7d01b50e0d17dc79c8"
        self.assertEqual(eip712.encode_value("address", good)[12:].hex(), good[2:])
        for bad in (good[:12] + " " + good[12:],   # bytes.fromhex used to strip it
                    good[2:],                       # no 0x prefix
                    "0X" + good[2:],                # a different document
                    good + "\n",
                    "0x" + "z" * 40,
                    7, None, True):
            with self.subTest(bad=bad):
                with self.assertRaises(eip712.EncodingError):
                    eip712.encode_value("address", bad)

    def test_mixed_case_hex_is_still_accepted(self):
        # EIP-55 casing is a checksum, not data: the same 20 bytes either way,
        # and the fixture set is internally inconsistent about it (REPORT.md
        # F-11). Rejecting it would invent a rule §5 does not have.
        lower = "0x70997970c51812dc3a010c7d01b50e0d17dc79c8"
        checksummed = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
        self.assertEqual(eip712.encode_value("address", lower),
                         eip712.encode_value("address", checksummed))

    def test_string_type_rejects_non_strings(self):
        # str(value) used to be hashed for anything non-string.
        for bad in (2, None, True, ["a"]):
            with self.subTest(bad=bad):
                with self.assertRaises(eip712.EncodingError):
                    eip712.encode_value("string", bad)

    def test_calldata_whitespace_no_longer_hashes_to_dataHash(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = stage(os.path.join(SAMPLES, "case-1-allow"), tmp)
        action = read_json(target, "action.json")
        action["callData"] = action["callData"][:10] + " " + action["callData"][10:]
        write_json(os.path.join(target, "action.json"), action)
        ok, checks = verify.verify_sample(target)
        self.assertFalse(ok, "callData with embedded whitespace still hashed "
                             "to the committed dataHash")
        data = [c for c in checks if "callData" in c.name]
        self.assertTrue(data and not data[0].ok)

    def test_two_byte_distinct_mandates_no_longer_share_one_mandateHash(self):
        # The defect in its operational form. `"durationSeconds": "86400"` and
        # `"durationSeconds": 86400` are different JSON documents that used to
        # produce the same mandateHash, so both verified against the same
        # receipt -- and §5.7 as amended by D-020 makes durationSeconds an
        # EQUALITY check against the mandate, so which document the operator is
        # reading is load-bearing.
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = stage(os.path.join(SAMPLES, "case-1-allow"), tmp)
        mandate = read_json(target, "mandate.json")
        original = dict(mandate)
        mandate["durationSeconds"] = int(mandate["durationSeconds"])
        mandate["validAfter"] = " " + mandate["validAfter"] + " "
        self.assertNotEqual(json.dumps(mandate), json.dumps(original))
        write_json(os.path.join(target, "mandate.json"), mandate)

        ok, checks = verify.verify_sample(target)
        self.assertFalse(ok, "a re-spelled mandate still recomputed the "
                             "receipt's mandateHash")
        failed = [c for c in checks if not c.ok]
        self.assertTrue(any("mandateHash" in c.name for c in failed))


# ---------------------------------------------------------------------------
# Signature canonical form: the receipt and the override, held to one rule
# ---------------------------------------------------------------------------

class TestSignatureCanonicalForm(unittest.TestCase):
    """§5 says nothing about signature encoding for EITHER signature -- not the
    r||s||v layout, not v in {27,28}, not EIP-2 low-s (REPORT.md F-10). The
    receipt's low-s check therefore comes from EIP-2, which is a rule about
    secp256k1 ECDSA rather than about receipts, and §5.8 gives the override the
    same construction: an EIP-712 digest under the same domain, signed with a
    secp256k1 key. There is no basis in §5 for one rule on one and none on the
    other, so the asymmetry was an omission rather than a decision.
    """

    def malleate(self, signature):
        """(r, s, v) -> (r, n-s, v^1): the same signature, reflected."""
        r, s, v = parse_signature(signature)
        self.assertTrue(is_low_s(s), "the fixture should start out canonical")
        return ("0x" + r.to_bytes(32, "big").hex()
                + (N - s).to_bytes(32, "big").hex()
                + bytes([{27: 28, 28: 27}[v]]).hex())

    def test_a_malleated_signature_recovers_the_same_address(self):
        # The premise. This is not a forgery and not a corruption: it is a
        # second, byte-distinct encoding of the owner's own authorization, and
        # every identity check passes on it. Only a canonical-form rule can
        # tell the two apart.
        doc = read_json(OVERRIDE_SAMPLE, "override.json")
        digest = eip712.override_digest(read_json(SAMPLES, "domain.json"),
                                        doc["override"])
        malleated = self.malleate(doc["ownerSignature"])
        self.assertNotEqual(malleated, doc["ownerSignature"])
        self.assertEqual(recover_address(digest, doc["ownerSignature"]),
                         recover_address(digest, malleated))
        self.assertEqual(recover_address(digest, malleated),
                         doc["ownerAddress"].lower())

    def test_high_s_override_signature_is_rejected(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = stage(OVERRIDE_SAMPLE, tmp)
        doc = read_json(target, "override.json")
        doc["ownerSignature"] = self.malleate(doc["ownerSignature"])
        write_json(os.path.join(target, "override.json"), doc)

        ok, checks = verify.verify_sample(target)
        self.assertFalse(ok, "a non-canonical (high-s) override signature was "
                             "accepted")
        low_s = [c for c in checks
                 if "override signature is EIP-2 canonical" in c.name]
        self.assertTrue(low_s and not low_s[0].ok)
        owner = [c for c in checks
                 if c.name == "override signature recovers ownerAddress"]
        self.assertTrue(owner and owner[0].ok,
                        "the owner check must still pass -- otherwise this "
                        "tests signature parsing, not canonical form")

    def test_the_receipt_and_the_override_are_held_to_the_same_rule(self):
        _, checks = verify.verify_sample(OVERRIDE_SAMPLE)
        canonical = [c for c in checks if "EIP-2 canonical (low-s)" in c.name]
        self.assertEqual(len(canonical), 2,
                         "both signatures in a bundle must be held to the "
                         "same canonical-form rule")
        self.assertTrue(all(c.ok for c in canonical))


if __name__ == "__main__":
    unittest.main(verbosity=2)
