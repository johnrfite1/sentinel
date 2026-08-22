#!/usr/bin/env python3
"""Tests for the Sentinel standalone receipt verifier (D-010).

Stdlib unittest only, no third-party test runner:

    python3 verifier/test_verifier.py
    python3 -m unittest discover -s verifier -v
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import eip712  # noqa: E402
import jcs  # noqa: E402
import reasoncodes  # noqa: E402
import refusal  # noqa: E402
import verify  # noqa: E402
from keccak import keccak256, keccak256_hex  # noqa: E402
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


def trust_root(sample_dir):
    """The trust root THIS TEST asserts, as the verifying party.

    A-058 (H-1): `verify_sample` no longer certifies a domain.json it merely FOUND, in the
    bundle or beside it, because every such path belongs to whoever assembled the material.
    A test is the verifying party for the fixtures it stages, so it names the root rather than
    letting the code guess — which is the same thing `--domain` does at the CLI.

    This is NOT the old discovery rule wearing a new name: the code no longer has that rule at
    all, so nothing here can drift back into agreement with an implementation. It is one
    caller stating where its own fixture put the file.
    """
    return os.path.join(os.path.dirname(os.path.abspath(sample_dir)), "domain.json")


def _verify(sample_dir, **kwargs):
    """verify_sample with this test's asserted trust root (see `trust_root`)."""
    kwargs.setdefault("domain_path", trust_root(sample_dir))
    return verify.verify_sample(sample_dir, **kwargs)


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


def all_sample_dirs():
    return sorted(
        os.path.join(SAMPLES, name)
        for name in os.listdir(SAMPLES)
        if os.path.isdir(os.path.join(SAMPLES, name))
    )


def sample_dirs():
    """The samples presenting a §5.4 signed receipt.

    §5.5.1 (2026-08-16) split the corpus in two. A bundle presents a decision
    OR a refusal -- never both -- so the tests that walk every sample asserting
    a receipt property now walk this list, and `refusal_sample_dirs()` carries
    the other kind. The split is read from `index.json`'s `signerRefused`,
    which is fixture-harness metadata rather than protocol; the verifier makes
    the same distinction structurally, by locating a §5.5.1 record.
    """
    refused = {e["id"] for e in read_json(SAMPLES, "index.json")
               if e.get("signerRefused")}
    return [d for d in all_sample_dirs() if os.path.basename(d) not in refused]


def refusal_sample_dirs():
    """The samples presenting a §5.5.1 SignedRefusalRecord."""
    refused = {e["id"] for e in read_json(SAMPLES, "index.json")
               if e.get("signerRefused")}
    return [d for d in all_sample_dirs() if os.path.basename(d) in refused]


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

        ok, checks = _verify(target)  # must not raise
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
                ok, checks = _verify(path)
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
                self.assertEqual(
                    verify.main(["--domain", os.path.join(SAMPLES, "domain.json"),
                                 "--all", SAMPLES]), 0)
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
                        ok, _ = _verify(path, tamper=mode)
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
        # 42 -> 48 (A-049): `evidence-hash` was added, applicable to all six receipt
        # samples. It corrupts the PUBLISHED hash rather than the canonical bytes, so
        # it is the only mode that isolates "keccak256(canonical bytes) matches
        # evidence.hash" -- a named check that, until this mode existed, no mode
        # targeted. An adversarial review neutered that check and the whole suite
        # stayed green (A-048).
        # 48 -> 54 (A-055): `receipt-wrongkey` added, applicable to all six receipt samples.
        # `override-wrongkey` and `refusal-wrongkey` already existed; the PRIMARY §5.4 artifact
        # had neither, which is the single reason the receipt's binding to the DEPLOYMENT's
        # signer was asserted by nothing until a directed sweep neutered it and all 154 tests
        # still passed.
        # 54 -> 63 (A-056): four RE-SIGNING modes added, each isolating a binding that no
        # existing mode could witness. `override-nonce` mutates a signed field without
        # re-signing, so the signature check fires first and §3.3(9)'s nonce binding never
        # bites; `override-wrongkey` leaves `ownerAddress` declaring the owner, so §3.3(7)
        # never bites. Re-signing is what makes the binding the witness.
        # 63 -> 64 (A-058, H-2): `override-outsider-mints`, applicable only to
        # case-4-review, the one sample carrying an override. Both existing party modes mint
        # as the SENTINEL SIGNER and are therefore caught by §3.3(7); an ARBITRARY THIRD
        # PARTY passes every check this stage had, which is why the stage's owner-identity
        # binding was asserted by nothing until this mode existed.
        self.assertEqual(exercised, 64, "expected 64 applicable tamper cases")

    def test_evidence_tamper_breaks_the_receipt_binding(self):
        # Specifically: it must fail the receipt.evidenceHash check, not merely
        # the file comparison. Otherwise a verifier handed only a bundle and a
        # receipt would still accept.
        ok, checks = _verify(sample_dirs()[0], tamper="evidence")
        self.assertFalse(ok)
        binding = [c for c in checks if "evidenceHash binds" in c.name]
        self.assertEqual(len(binding), 1)
        self.assertFalse(binding[0].ok)

    def test_receipt_tamper_breaks_signer_recovery(self):
        ok, checks = _verify(sample_dirs()[0], tamper="receipt")
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
            ok, _ = _verify(path, domain_path=domain_path)
            self.assertFalse(ok, "a cross-chain replay was accepted")

    def test_wrong_verifying_contract_is_rejected(self):
        path = sample_dirs()[0]
        with tempfile.TemporaryDirectory() as tmp:
            domain = read_json(SAMPLES, "domain.json")
            domain["verifyingContract"] = "0x" + "11" * 20
            domain_path = os.path.join(tmp, "domain.json")
            with open(domain_path, "w") as handle:
                json.dump(domain, handle)
            ok, _ = _verify(path, domain_path=domain_path)
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
            ok, _ = _verify(sample_dirs()[0])
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
                    ok, _ = _verify(sample_dirs()[0])
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
        ok, checks = _verify(target)
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
        ok, checks = _verify(path)
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
        ok, checks = _verify(path)
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
        ok, checks = _verify(path)  # must not raise
        self.assertFalse(ok)
        self.assertTrue(any("signed receipt is present" in c.name and not c.ok
                            for c in checks))

    def test_a_receipt_without_a_signature_is_not_certified(self):
        # "refused" is not the only way to present nothing signed: dropping the
        # signature leaves a well-formed receipt body that nothing attests to.
        doc = read_json(sample_dirs()[0], "receipt.json")
        doc.pop("signature")
        path = self._refused_copy(doc)
        ok, checks = _verify(path)
        self.assertFalse(ok, "a receipt with no signature was certified")
        self.assertTrue(any("signed receipt is present" in c.name and not c.ok
                            for c in checks))

    def test_refused_but_signed_is_a_failure(self):
        # A refusal that nonetheless carries a signed receipt is contradictory
        # and must not pass.
        original = read_json(sample_dirs()[0], "receipt.json")
        original["refused"] = True
        path = self._refused_copy(original)
        ok, checks = _verify(path)
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
                        ok, checks = _verify(path, tamper=mode)
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
                    ok, checks = _verify(path, tamper="reasons-reorder")
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

        ok, checks = _verify(target)
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
        ok, checks = _verify(target)
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
        ok, checks = _verify(target)
        self.assertFalse(ok)
        grammar = [c for c in checks if "identifier matches" in c.name]
        self.assertTrue(grammar and not grammar[0].ok)


# ---------------------------------------------------------------------------
# §5.5 override authorization and the chain-binding question (D-023)
# ---------------------------------------------------------------------------

OVERRIDE_SAMPLE = os.path.join(SAMPLES, "case-4-review-failmode-review")


SPEC_5_8_ANCHOR = "### 5.8 EIP-712 Type Strings (normative)"


def published_type_strings(text, anchor=SPEC_5_8_ANCHOR):
    """The §5.8 consumer, as ONE function so it can be tested against synthetic
    documents rather than only against the live proposal.

    A-EXTRACT case 13. `scripts/check-type-strings.sh` and this consumer read the
    same section of the same document and must not disagree about where it ends or
    about what to do with a duplicate. The contract this function owes, and which
    TestPublishedTypeStringsSectionExtent below asserts:

      * the section runs from `anchor` to the next heading whose depth is the SAME
        AS OR SHALLOWER THAN THE ANCHOR'S OWN -- not to a fixed heading class, and
        not to the next horizontal rule. A `#### 5.8.1` subsection is INSIDE `§5.8`;
        a `### 5.7` heading ends it; a `## 6.` heading ends it.
      * an absent anchor is REFUSED by name, not by IndexError. An uncaught
        exception is an INSTRUMENT FAILURE, not a refusal: it carries no
        statement about the section and is not stable across inputs.
      * two headings claiming the anchor are REFUSED. Taking the first is a
        tie-break, and the document's section order is not monotonic.
      * a heading QUOTED inside a fenced code block is a MENTION, not the
        anchor. `scripts/check-vendor-honesty.sh` already records this exact
        defeat against its own section-2 lookup.
      * two different publications of one type inside the section are REFUSED in
        EITHER order. Silently keeping the last is how a transposed type string
        rode through a consumer that reported success.

    REFUSAL VOCABULARY, because `a-extract.sh` case 13 requires this consumer and
    `scripts/check-type-strings.sh` to land in the SAME reason class and a class is
    read off the message. Raise `ValueError` whose text contains the section
    number AND, for the anchor cases, one of:

        anchor-unresolved    "could not isolate" / "could not find" /
                             "not found" / "absent" / "missing" /
                             "no such section"
        anchor-ambiguous     "ambiguous" / "duplicate" / "two sections" /
                             "headings claim"

    and for a repeated publication, one of "duplicate" / "twice" /
    "more than one" / "published N times". The words are alternatives, not a
    dictated sentence; what is fixed is the CLASS the message must land in.

    The body below is the behaviour AS IT STOOD at bb664c6, moved here unchanged so
    that applying this patch changes nothing on its own. The new tests fail against
    it; that is what makes them a contract rather than a description.
    """
    import re
    lines = text.splitlines()
    heading_re = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+|$)(?!#)")
    fence_re = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
    headings = []
    fence_char = None
    fence_length = 0
    for index, line in enumerate(lines):
        if fence_char is not None:
            if re.match(r"^ {0,3}" + re.escape(fence_char) +
                        r"{%d,}[ \t]*$" % fence_length, line):
                fence_char = None
                fence_length = 0
            continue
        opening = fence_re.match(line)
        if opening:
            marker = opening.group(1)
            fence_char = marker[0]
            fence_length = len(marker)
            continue
        heading = heading_re.match(line)
        if heading:
            headings.append((index, len(heading.group(1))))

    anchors = [(index, depth) for index, depth in headings
               if lines[index] == anchor]
    if not anchors:
        raise ValueError("§5.8 could not isolate section: anchor not found")
    if len(anchors) != 1:
        raise ValueError("§5.8 ambiguous section: %d headings claim the anchor" %
                         len(anchors))

    start, depth = anchors[0]
    end = len(lines)
    for index, candidate_depth in headings:
        if index > start and candidate_depth <= depth:
            end = index
            break

    out = {}
    for line in lines[start + 1:end]:
        m = re.match(r"^ {4}([A-Za-z0-9]+)\((.*)\)$", line)
        if m:
            name = m.group(1)
            if name in out:
                raise ValueError("§5.8 duplicate publication: %s published 2 times" % name)
            out[name] = line.strip()
    return out


class TestPublishedTypeStrings(unittest.TestCase):
    """§5.8 now publishes all six type strings. Check the published spec is
    sufficient -- and that it agrees with what was independently recovered."""

    def _published(self):
        spec = os.path.join(REPO, "Sentinel_Protocol_Lab_Proposal_v0_2.md")
        with open(spec, encoding="utf-8") as handle:
            text = handle.read()
        return published_type_strings(text)

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



class TestPublishedTypeStringsSectionExtent(unittest.TestCase):
    """A-EXTRACT case 13 — the §5.8 consumer agrees with the shell guard.

    Two consumers of one section that disagree about its extent, or about what a
    duplicate means, are two different claims wearing one section number. Every
    fixture here is synthetic: the live proposal is never mutated, and no test in
    this class depends on the proposal's current contents.
    """

    A = SPEC_5_8_ANCHOR
    ONE = "    AlphaPayload(uint16 schemaVersion,address vault)"
    TWO = "    BetaPayload(uint16 schemaVersion,uint256 chainId)"
    TWO_ALT = "    BetaPayload(uint256 chainId,uint16 schemaVersion)"

    def _doc(self, body):
        return "# Proposal\n\n## 5. Typed Contracts\n\n" + body + "\n"

    # -- extent ----------------------------------------------------------------

    def test_deeper_subsection_stays_inside_the_section(self):
        # `#### 5.8.1` is DEEPER than the `###` anchor, so it is part of §5.8.
        doc = self._doc("\n".join([
            self.A, "", self.ONE, "",
            "#### 5.8.1 Domain field values", "",
            self.TWO, "",
            "### 5.6 EvidenceBundle", "", "    Ignored(uint8 x)",
        ]))
        got = published_type_strings(doc)
        self.assertIn("AlphaPayload", got)
        self.assertIn("BetaPayload", got)
        self.assertNotIn("Ignored", got)

    def test_same_depth_heading_ends_the_section(self):
        doc = self._doc("\n".join([
            self.A, "", self.ONE, "",
            "### 5.6 EvidenceBundle", "", self.TWO,
        ]))
        got = published_type_strings(doc)
        self.assertIn("AlphaPayload", got)
        self.assertNotIn("BetaPayload", got)

    def test_shallower_heading_ends_the_section(self):
        doc = self._doc("\n".join([
            self.A, "", self.ONE, "",
            "## 6. AI and Context Scope", "", self.TWO,
        ]))
        got = published_type_strings(doc)
        self.assertIn("AlphaPayload", got)
        self.assertNotIn("BetaPayload", got)

    def test_horizontal_rule_does_not_end_the_section(self):
        # The shell guard's boundary is a HEADING. A rule inside the section is
        # typography, and a consumer that stops at one reads a shorter §5.8 than
        # the guard certifying §5.8 does.
        doc = self._doc("\n".join([
            self.A, "", self.ONE, "", "---", "", self.TWO, "",
            "### 5.6 EvidenceBundle",
        ]))
        got = published_type_strings(doc)
        self.assertIn("AlphaPayload", got)
        self.assertIn("BetaPayload", got)

    # -- refusals --------------------------------------------------------------

    UNRESOLVED_WORDS = ("could not isolate", "could not find", "could not locate",
                        "not found", "absent", "missing", "no such section")
    AMBIGUOUS_WORDS = ("ambiguous", "duplicate", "two sections", "headings claim")
    REPEATED_WORDS = ("duplicate", "twice", "more than one", "times")

    def _assert_class(self, message, words):
        lowered = message.lower()
        self.assertTrue(any(w in lowered for w in words),
                        "refusal %r lands in no required class %r" % (message, words))

    def test_absent_anchor_is_refused_by_name(self):
        doc = self._doc("\n".join(["### 5.6 EvidenceBundle", "", self.ONE]))
        with self.assertRaises(ValueError) as caught:
            published_type_strings(doc)
        self.assertIn("5.8", str(caught.exception))
        self._assert_class(str(caught.exception), self.UNRESOLVED_WORDS)

    def test_duplicate_anchor_is_refused(self):
        doc = self._doc("\n".join([
            self.A, "", self.ONE, "", self.TWO, "",
            "### 5.7 Supported Checks", "",
            self.A, "", self.ONE, "", self.TWO,
        ]))
        with self.assertRaises(ValueError) as caught:
            published_type_strings(doc)
        self.assertIn("5.8", str(caught.exception))
        self._assert_class(str(caught.exception), self.AMBIGUOUS_WORDS)

    def test_a_quoted_heading_is_not_the_anchor(self):
        # The real section is second; the first "heading" is inside a fenced
        # block, introduced as a rejected draft. A line-oriented anchor search
        # cannot see fences and takes the quotation.
        doc = self._doc("\n".join([
            "A format considered and rejected, quoted so the reasoning survives:",
            "", "```markdown", self.A, "", self.TWO_ALT, "```", "",
            self.A, "", self.ONE, "", self.TWO, "",
            "### 5.6 EvidenceBundle",
        ]))
        got = published_type_strings(doc)
        self.assertEqual(got.get("BetaPayload"), self.TWO.strip())

    def test_a_tilde_fenced_heading_is_not_the_anchor(self):
        # CommonMark spells a fenced code block with three or more BACKTICKS or
        # three or more TILDES. A consumer taught to ignore one and not the
        # other has generalised the demonstration and not the argument, which
        # is this project's most repeated repair defect. Its own case, not a
        # parameter of the one above, so a reader can point at it.
        doc = self._doc("\n".join([
            "A format considered and rejected, quoted so the reasoning survives:",
            "", "~~~markdown", self.A, "", self.TWO_ALT, "~~~", "",
            self.A, "", self.ONE, "", self.TWO, "",
            "### 5.6 EvidenceBundle",
        ]))
        got = published_type_strings(doc)
        self.assertEqual(got.get("BetaPayload"), self.TWO.strip())

    def test_duplicate_publication_is_refused_decoy_first(self):
        doc = self._doc("\n".join([
            self.A, "", self.ONE, "", self.TWO_ALT, "", self.TWO,
        ]))
        with self.assertRaises(ValueError) as caught:
            published_type_strings(doc)
        self.assertIn("BetaPayload", str(caught.exception))
        self._assert_class(str(caught.exception), self.REPEATED_WORDS)

    def test_duplicate_publication_is_refused_decoy_second(self):
        # The order that fails SILENTLY today: the later line simply overwrites
        # the earlier one in the dict and the consumer reports success.
        doc = self._doc("\n".join([
            self.A, "", self.ONE, "", self.TWO, "", self.TWO_ALT,
        ]))
        with self.assertRaises(ValueError) as caught:
            published_type_strings(doc)
        self.assertIn("BetaPayload", str(caught.exception))
        self._assert_class(str(caught.exception), self.REPEATED_WORDS)

    # -- controls --------------------------------------------------------------

    def test_a_well_formed_section_is_read_whole(self):
        doc = self._doc("\n".join([
            self.A, "", self.ONE, "", self.TWO, "",
            "### 5.6 EvidenceBundle",
        ]))
        got = published_type_strings(doc)
        self.assertEqual(sorted(got), ["AlphaPayload", "BetaPayload"])

    def test_the_live_proposal_still_publishes_six(self):
        # The opposite outcome for every refusal above: the real document is not
        # ambiguous, so none of these rules may fire on it.
        spec = os.path.join(REPO, "Sentinel_Protocol_Lab_Proposal_v0_2.md")
        with open(spec, encoding="utf-8") as handle:
            text = handle.read()
        self.assertEqual(len(published_type_strings(text)), 6)

class TestOverride(unittest.TestCase):
    def _doc(self):
        return read_json(OVERRIDE_SAMPLE, "override.json")

    def test_override_verifies(self):
        ok, checks = _verify(OVERRIDE_SAMPLE)
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
                ok, _ = _verify(OVERRIDE_SAMPLE, tamper=mode)
                self.assertFalse(ok, f"{mode} was WRONGLY ACCEPTED")

    def test_the_outsider_minting_mode_is_registered_structurally(self):
        # A-049's rule: a mode can be implemented and never registered, and the loop-driven
        # test above would then simply not run it. Assert membership, not behaviour.
        self.assertIn("override-outsider-mints", verify.TAMPER_MODES)

    def test_an_override_minted_by_an_arbitrary_outsider_is_rejected(self):
        """A-058 (H-2). The override stage had NO deployment-anchored owner identity.

        `ownerAddress` is a sibling declaration, not a member of the signed §5.5 payload, so
        anyone can sign the identical payload with their own key and name themselves. Against
        the REAL domain.json this produced eleven consecutive [PASS] lines and `=> PASS`,
        exit 0. Both existing party modes mint as the SENTINEL SIGNER, which §3.3(7) catches,
        so neither could ever witness this.

        Built by DERIVING from the genuine override rather than hand-assembling one, so the
        rejection cannot be an artefact of a malformed payload — the paired assertions below
        require every pre-existing check in the stage to still PASS.
        """
        from secp256k1 import sign_digest, point_mul, public_key_to_address, G
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = stage(OVERRIDE_SAMPLE, tmp)
        domain = read_json(SAMPLES, "domain.json")
        outsider = 0x00C0FFEE00C0FFEE00C0FFEE00C0FFEE00C0FFEE00C0FFEE00C0FFEE00C0FF02
        address = public_key_to_address(point_mul(outsider, G))
        doc = read_json(target, "override.json")
        payload_before = json.dumps(doc["override"], sort_keys=True)
        doc["ownerAddress"] = address
        doc["ownerSignature"] = sign_digest(
            eip712.override_digest(domain, doc["override"]), outsider)
        write_json(os.path.join(target, "override.json"), doc)
        self.assertEqual(json.dumps(read_json(target, "override.json")["override"],
                                    sort_keys=True), payload_before,
                         "the PAYLOAD must be untouched, or this tests something else")

        ok, checks = _verify(target)
        self.assertFalse(ok, "an override minted by an arbitrary outsider was certified")
        by_name = {c.name: c for c in checks}
        for name in ("override signature recovers ownerAddress",
                     "override owner is NOT the Sentinel signer (§3.3(7))",
                     "override.reviewReceiptHash == this receipt's EIP-712 hashStruct",
                     "override targets a REVIEW receipt, not a BLOCK (§5.5)"):
            self.assertTrue(by_name[name].ok,
                            f"{name} must still PASS -- every pre-existing check in this "
                            "stage does, which is precisely why the stage needed a new one")
        self.assertEqual(
            [c.name for c in checks if not c.ok],
            ["override owner is the mandate's principal (§5.1), "
             "not a self-declared address"])

    def test_the_genuine_owner_is_the_mandate_principal(self):
        # The paired positive. Without it the check above could be satisfied by a rule that
        # rejects every override, and the sample walk would be the only thing noticing.
        doc = read_json(OVERRIDE_SAMPLE, "override.json")
        mandate = read_json(OVERRIDE_SAMPLE, "mandate.json")
        self.assertEqual(doc["ownerAddress"].lower(), mandate["principal"].lower())

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
        ok, checks = _verify(OVERRIDE_SAMPLE, tamper="override-wrongkey")
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

class TestEvidenceDescribesTheBundle(unittest.TestCase):
    """A-069 (from round five's E4). §5.6's `normalizedAction` and `expectedEffects` were
    checked by NOBODY — not the signer (D-014 keeps conformance out of it) and not this
    verifier. `evidenceHash` made them tamper-evident, so nothing could change them unnoticed;
    nothing compared them to the documents they claim to describe.

    The bundles below are re-canonicalised, re-hashed, re-bound and RE-SIGNED, so every hash
    and signature check passes and only these checks can reject them. A mutation caught by a
    different check than the one it targets is worth nothing (A-055/A-056), and the first
    attempt at this test was exactly that — the un-resealed bundle failed on the canonical
    bytes.
    """

    SIGNER = 0x59C6995E998F97A5A0044966F0945389DC9E86DAE88C7A8412F4603B6B78690D

    def resealed(self, mutate, sample="case-1-allow"):
        """A bundle mutated by `mutate(evidence)` and then made wholly self-consistent."""
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = stage(os.path.join(SAMPLES, sample), tmp)
        ev = read_json(target, "evidence.json")
        mutate(ev)
        with open(os.path.join(target, "evidence.json"), "w") as h:
            json.dump(ev, h)
        canon = jcs.canonicalize(ev)
        with open(os.path.join(target, "evidence.canonical.json"), "wb") as h:
            h.write(canon)
        digest = "0x" + keccak256(canon).hex()
        with open(os.path.join(target, "evidence.hash"), "w") as h:
            h.write(digest + "\n")
        doc = read_json(target, "receipt.json")
        doc["receipt"]["evidenceHash"] = digest
        domain = read_json(SAMPLES, "domain.json")
        doc["signature"] = sign_digest(
            eip712.receipt_digest(domain, doc["receipt"]), self.SIGNER)
        write_json(os.path.join(target, "receipt.json"), doc)
        return target

    def test_the_reseal_itself_produces_a_verifying_bundle(self):
        # THE CONTROL, and without it every test below could be passing because `resealed`
        # produces malformed bundles rather than because the new checks work.
        target = self.resealed(lambda ev: None)
        ok, checks = _verify(target)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])

    def test_expectedEffects_may_not_state_what_the_mandate_does_not(self):
        target = self.resealed(
            lambda ev: ev["expectedEffects"].__setitem__("beneficiary", "0x" + "44" * 20))
        ok, checks = _verify(target)
        self.assertFalse(ok, "a bundle stated a beneficiary its own mandate does not authorise")
        self.assertEqual(
            [c.name for c in checks if not c.ok],
            ["evidence.expectedEffects projects the §5.1/§5.2 documents (ceiling intersected)"],
            "only THIS check may reject it — anything else means the bundle is malformed and "
            "the test is measuring something other than what it names")

    def test_normalizedAction_may_not_restate_a_different_action(self):
        target = self.resealed(
            lambda ev: ev["normalizedAction"].__setitem__("valueWei", "999999999999999999"))
        ok, checks = _verify(target)
        self.assertFalse(ok)
        self.assertIn("evidence.normalizedAction restates the §5.3 action it was computed for",
                      [c.name for c in checks if not c.ok])

    def test_the_bundles_callData_must_be_the_action_it_commits_to(self):
        target = self.resealed(
            lambda ev: ev["normalizedAction"].__setitem__("callData", "0xdeadbeef"))
        ok, checks = _verify(target)
        self.assertFalse(ok)
        self.assertIn("keccak256(evidence.normalizedAction.callData) == action.dataHash",
                      [c.name for c in checks if not c.ok])

    # ---- OMISSION, not contradiction (D-052(b), from round six L6-3/L2-3) --------------
    #
    # Every test above mutates a projection into saying something FALSE. A-069 gated both
    # checks on `isinstance(..., dict)` with no else-branch, so a bundle that simply OMITTED a
    # projection — or supplied one wrapped in a list — emitted NO Check at all, and the run
    # printed as clean. Contradiction cost a FAIL; omission cost nothing, which is the wrong
    # way round. This is A-067's own rule, one file over: "A hash commits to a document. With
    # no document there is nothing to certify, so this FAILS."
    #
    # Each of these was confirmed to PASS against the pre-fix verifier before the fix landed.

    def test_expectedEffects_may_not_simply_be_absent(self):
        target = self.resealed(lambda ev: ev.pop("expectedEffects"))
        ok, checks = _verify(target)
        self.assertFalse(ok, "a bundle omitting expectedEffects was certified")
        self.assertIn("evidence.expectedEffects is present and is an object (§5.6)",
                      [c.name for c in checks if not c.ok])

    def test_expectedEffects_may_not_be_a_non_object(self):
        # The list wrapper is the cheapest type evasion and it defeated the isinstance gate.
        target = self.resealed(
            lambda ev: ev.__setitem__("expectedEffects", [ev["expectedEffects"]]))
        ok, checks = _verify(target)
        self.assertFalse(ok)
        self.assertIn("evidence.expectedEffects is present and is an object (§5.6)",
                      [c.name for c in checks if not c.ok])

    def test_normalizedAction_may_not_simply_be_absent(self):
        target = self.resealed(lambda ev: ev.pop("normalizedAction"))
        ok, checks = _verify(target)
        self.assertFalse(ok, "a bundle omitting normalizedAction was certified")
        self.assertIn("evidence.normalizedAction is present and is an object (§5.6)",
                      [c.name for c in checks if not c.ok])

    def test_normalizedAction_may_not_be_a_non_object(self):
        target = self.resealed(
            lambda ev: ev.__setitem__("normalizedAction", [ev["normalizedAction"]]))
        ok, checks = _verify(target)
        self.assertFalse(ok)
        self.assertIn("evidence.normalizedAction is present and is an object (§5.6)",
                      [c.name for c in checks if not c.ok])

    # ---- THE SIBLINGS, which no reviewer reported -------------------------------------
    #
    # Found by the docs/repair-protocol.md step-2 sweep of every `isinstance`-gated block in
    # verify.py, run because the protocol requires it rather than because anyone pointed here.
    # `reasonCodes is a list` two hundred lines away already had the correct shape — it emits a
    # FAILING check on the wrong type — so the file disagreed with itself about this.

    def test_the_anchor_may_not_simply_be_absent(self):
        # A-056 added `receipt-anchor-split` because "THE ANCHOR HAD NO TEST AT ALL". Deleting
        # the anchor outright is the cheaper attack on the same binding and it verified PASS.
        target = self.resealed(lambda ev: ev.pop("anchor"))
        ok, checks = _verify(target)
        self.assertFalse(ok, "a bundle omitting its anchor was certified")
        self.assertIn("evidence.anchor is present and is an object (§5.6)",
                      [c.name for c in checks if not c.ok])

    def test_the_anchor_may_not_be_a_non_object(self):
        # Protocol step 4 requires BOTH branches of an absence-shaped gate: absent AND
        # wrong-type. The list wrapper is the cheaper of the two evasions — it needs no field
        # removed, so a reader diffing the bundle sees the anchor still "there" — and pinning
        # only the absent case would be this project's own partial-repair defect committed
        # inside the repair for it.
        target = self.resealed(lambda ev: ev.__setitem__("anchor", [ev["anchor"]]))
        ok, checks = _verify(target)
        self.assertFalse(ok, "a bundle whose anchor is not an object was certified")
        self.assertIn("evidence.anchor is present and is an object (§5.6)",
                      [c.name for c in checks if not c.ok])

    def test_the_evidence_verdict_may_not_simply_be_absent(self):
        target = self.resealed(lambda ev: ev.pop("verdict"))
        ok, checks = _verify(target)
        self.assertFalse(ok, "a bundle omitting its own verdict was certified")
        self.assertIn("evidence.verdict is present to compare against the receipt (§5.6)",
                      [c.name for c in checks if not c.ok])


class TestAllowConformsToTheMandate(unittest.TestCase):
    """D-055(b): the conformance comparison D-014's architecture assigns to THIS verifier.

    D-014 rejected giving the signer conformance checks, and its stated ground -- carried into
    the SIGNED Gate S1 pack -- is that "a wrong-purpose ALLOW is detectable after the fact by
    the D-010 verifier, which does the conformance comparison". It did not: `grep -c
    decodedSelectorAndParameters verify.py` returned 0, and a wholly self-consistent
    wrong-purpose ALLOW verified `=> PASS`, exit 0.

    John ruled the architecture must hold rather than the sentence be withdrawn, so the check
    is built here. It binds ONLY to ALLOW: a BLOCK or REVIEW bundle is legitimately
    nonconforming, which is what the corpus is full of and what `case-3-wrong-purpose-block`
    exists to be. The last test in this class is that negative, and it is the one that would
    catch an over-broad repair.
    """

    # Borrowed from TestEvidenceDescribesTheBundle.resealed, which this class reuses rather
    # than duplicating: one reseal harness, so a defect in it cannot pass here and fail there.
    SIGNER = TestEvidenceDescribesTheBundle.SIGNER

    CONFORMANCE = "ALLOW: the signer-attested decoded parameters conform to the mandate (§5.7.1)"

    def _params(self, ev):
        return ev["decodedSelectorAndParameters"]["parameters"]

    def test_a_wrong_resource_under_ALLOW_is_refused(self):
        # The flagship shape: mechanically valid, wrong purpose, asserted as ALLOW.
        t = TestEvidenceDescribesTheBundle.resealed(
            self, lambda ev: self._params(ev).__setitem__("resourceId", "0x" + "ab" * 32))
        ok, checks = _verify(t)
        self.assertFalse(ok, "a wrong-purpose ALLOW was certified")
        self.assertIn(self.CONFORMANCE, [c.name for c in checks if not c.ok])

    def test_a_wrong_beneficiary_under_ALLOW_is_refused(self):
        t = TestEvidenceDescribesTheBundle.resealed(
            self, lambda ev: self._params(ev).__setitem__("beneficiary", "0x" + "44" * 20))
        ok, checks = _verify(t)
        self.assertFalse(ok)
        self.assertIn(self.CONFORMANCE, [c.name for c in checks if not c.ok])

    def test_a_widened_duration_under_ALLOW_is_refused(self):
        t = TestEvidenceDescribesTheBundle.resealed(
            self, lambda ev: self._params(ev).__setitem__("durationSeconds", "31536000"))
        ok, checks = _verify(t)
        self.assertFalse(ok)
        self.assertIn(self.CONFORMANCE, [c.name for c in checks if not c.ok])

    def test_recurrence_the_mandate_forbids_under_ALLOW_is_refused(self):
        t = TestEvidenceDescribesTheBundle.resealed(
            self, lambda ev: self._params(ev).__setitem__("recurring", True))
        ok, checks = _verify(t)
        self.assertFalse(ok)
        self.assertIn(self.CONFORMANCE, [c.name for c in checks if not c.ok])

    def test_a_selector_the_mandate_does_not_authorise_is_refused(self):
        # A route no reviewer demonstrated (protocol step 3): the parameters can agree while
        # the CALL is a different function entirely.
        t = TestEvidenceDescribesTheBundle.resealed(
            self, lambda ev: ev["decodedSelectorAndParameters"].__setitem__(
                "selector", "0x095ea7b3"))
        ok, checks = _verify(t)
        self.assertFalse(ok)
        self.assertIn("ALLOW: the decoded selector is the one the mandate authorises",
                      [c.name for c in checks if not c.ok])

    def test_an_ALLOW_whose_decoded_record_is_absent_is_refused(self):
        # Absence is not agreement: omission must cost more than contradiction, not less.
        t = TestEvidenceDescribesTheBundle.resealed(
            self, lambda ev: ev.pop("decodedSelectorAndParameters"))
        ok, checks = _verify(t)
        self.assertFalse(ok)
        self.assertIn("ALLOW: evidence carries a signer-attested decoded-parameter record",
                      [c.name for c in checks if not c.ok])

    def test_an_ALLOW_whose_parameters_are_not_an_object_is_refused(self):
        t = TestEvidenceDescribesTheBundle.resealed(
            self, lambda ev: ev["decodedSelectorAndParameters"].__setitem__(
                "parameters", [self._params(ev)]))
        ok, checks = _verify(t)
        self.assertFalse(ok)
        self.assertIn("ALLOW: the decoded record carries a parameters object",
                      [c.name for c in checks if not c.ok])

    def test_an_ALLOW_over_an_undecoded_call_is_refused(self):
        t = TestEvidenceDescribesTheBundle.resealed(
            self, lambda ev: ev["decodedSelectorAndParameters"].__setitem__("decoded", "false"))
        ok, checks = _verify(t)
        self.assertFalse(ok)
        self.assertIn("ALLOW: the calldata was decoded", [c.name for c in checks if not c.ok])

    def test_a_NONCONFORMING_BLOCK_BUNDLE_STILL_VERIFIES(self):
        # THE NEGATIVE THAT BOUNDS THE REPAIR, and the one an over-broad version fails.
        # `case-3-wrong-purpose-block` buys a resource its mandate does not authorise. That is
        # the artifact this project exists to produce, and requiring conformance of it would
        # reject the corpus. Resealed through the same harness so this is not passing because
        # the bundle was untouched.
        t = TestEvidenceDescribesTheBundle.resealed(
            self, lambda ev: None, sample="case-3-wrong-purpose-block")
        ok, checks = _verify(t)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])
        self.assertNotIn(self.CONFORMANCE, [c.name for c in checks],
                         "the conformance check must not even run on a BLOCK bundle")


class TestAbsenceIsNotAgreement(unittest.TestCase):
    """A-067 (from round five's H-4). A payload-hash MISMATCH became a PASS when the
    contradicting file was DELETED.

    `_payload_hash_check` and `_binding_checks` both returned `ok=True, skipped=True` when the
    payload was absent, so `rm action.json` flipped exit 1 to exit 0 on a bundle whose receipt
    committed to a different action. **This is the same structural defect A-041 already named
    in the S2 pack** — "SKIP counted as ok=True in the aggregate, so 'was not checked' summed
    as 'passed'" — fixed there for the refusal envelope and left standing on the receipt path.

    Both branches are pinned here, because fixing only the one a reviewer exploited is this
    project's most-repeated defect.
    """

    def staged(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        return tmp, stage(os.path.join(SAMPLES, "case-1-allow"), tmp)

    def test_the_intact_bundle_still_verifies(self):
        # The control. Without it, a rule that fails every bundle satisfies everything below.
        _, target = self.staged()
        ok, _ = _verify(target)
        self.assertTrue(ok)

    def test_deleting_a_contradicting_payload_does_not_turn_FAIL_into_PASS(self):
        # The finding in its exact shape: swap in another case's action, observe the mismatch,
        # then delete the file that produced it.
        _, target = self.staged()
        shutil.copy(os.path.join(SAMPLES, "case-3-wrong-purpose-block", "action.json"),
                    os.path.join(target, "action.json"))
        # The two branches name the check slightly differently — "…ActionPayload matches the
        # receipt" when the payload is present, "…ActionPayload" when it is absent — so both
        # are matched by prefix rather than by loosening the assertion to a substring of
        # something vaguer.
        def failed_action_hash(checks):
            return [c.name for c in checks
                    if not c.ok and c.name.startswith("recomputed actionHash from §5.3")]

        ok, checks = _verify(target)
        self.assertFalse(ok, "the swapped action must be caught")
        self.assertTrue(failed_action_hash(checks), [c.name for c in checks if not c.ok])

        os.remove(os.path.join(target, "action.json"))
        ok, checks = _verify(target)
        self.assertFalse(
            ok, "deleting the contradicting payload turned a FAILING bundle into a PASS")
        self.assertTrue(failed_action_hash(checks), [c.name for c in checks if not c.ok])

    def test_stripping_every_payload_does_not_verify(self):
        # The sibling branch: with no payloads at all, §3.3(4) asserted nothing and said so
        # with ok=True, so a receipt bound to no chain and no vault certified.
        _, target = self.staged()
        for name in ("action.json", "mandate.json", "policy.json"):
            os.remove(os.path.join(target, name))
        ok, checks = _verify(target)
        self.assertFalse(ok, "a receipt bound to nothing presented was certified")
        self.assertIn("§3.3(4) chain and vault binding",
                      [c.name for c in checks if not c.ok])


class TestAllOverZeroBundles(unittest.TestCase):
    """H-8 (round five), closed under D-056(a).

    THE ARGUMENT: **"verified nothing" must never be reported as "verified
    everything".** `--all` discovers its own work, so zero discovered bundles used
    to print `0/0 sample(s) verified` and exit 0 -- and in a gate that reads exit
    status, an empty corpus was indistinguishable from a passing one.

    THE WHOLE DISCOVERY SURFACE IS SWEPT, not the one shape a reviewer tried: an
    empty directory, a directory holding only files, and a path that cannot be
    enumerated at all. The last previously died with a bare traceback -- nonzero,
    but for the wrong reason and with no usable diagnostic.

    `subprocess` rather than calling `main()` in-process, deliberately: the defect
    is about the EXIT STATUS a caller observes, and asserting on a return value
    inside this process would not exercise what the gate actually reads.
    """

    def _run(self, *args):
        proc = subprocess.run(
            [sys.executable, os.path.join(REPO, "verifier", "verify.py"),
             "--domain", os.path.join(SAMPLES, "domain.json"), "--all", *args],
            capture_output=True, text=True)
        return proc.returncode, proc.stdout + proc.stderr

    def test_a_nonempty_corpus_still_verifies_and_exits_zero(self):
        # THE CONTROL John asked to preserve. Without it, "always fail" satisfies
        # every assertion below.
        rc, out = self._run(SAMPLES)
        self.assertEqual(rc, 0, out)
        self.assertIn("7/7 sample(s) verified", out)

    def test_an_empty_directory_exits_nonzero(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        rc, out = self._run(tmp)
        self.assertNotEqual(rc, 0, "zero discovered bundles must not read as success")
        self.assertIn("NO BUNDLE DIRECTORIES FOUND", out)
        self.assertNotIn("0/0 sample(s) verified", out)

    def test_a_directory_of_non_bundle_files_exits_nonzero(self):
        # The sibling shape. A corpus whose generation wrote files but no bundle
        # directories is the realistic version of this, and it discovers zero
        # targets exactly as an empty directory does.
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        for name in ("readme.txt", "index.json", "domain.json"):
            with open(os.path.join(tmp, name), "w") as fh:
                fh.write("{}")
        rc, out = self._run(tmp)
        self.assertNotEqual(rc, 0)
        self.assertIn("NO BUNDLE DIRECTORIES FOUND", out)

    def test_an_unenumerable_path_gives_a_diagnostic_not_a_traceback(self):
        rc, out = self._run(os.path.join(tempfile.gettempdir(), "sentinel-no-such-dir-xyz"))
        self.assertNotEqual(rc, 0)
        self.assertIn("cannot enumerate", out)
        self.assertNotIn("Traceback", out,
                         "a missing path is a user error, not an internal fault")

    def test_a_file_named_under_all_is_reported_rather_than_crashing(self):
        # `--all path/to/file.json` is a plausible typo and is not enumerable.
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        path = os.path.join(tmp, "not-a-directory.json")
        with open(path, "w") as fh:
            fh.write("{}")
        rc, out = self._run(path)
        self.assertNotEqual(rc, 0)
        self.assertIn("cannot enumerate", out)
        self.assertNotIn("Traceback", out)

    def test_one_empty_root_among_several_is_still_reported(self):
        # The case an aggregate "did we find ANY targets" check would pass: a real
        # corpus plus an empty directory. The empty one contributed nothing and
        # saying so is the whole point.
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        rc, out = self._run(SAMPLES, tmp)
        self.assertNotEqual(rc, 0)
        self.assertIn("NO BUNDLE DIRECTORIES FOUND", out)
        self.assertIn(tmp, out)


class TestCaseLabelDiagnosticIsTrue(unittest.TestCase):
    """H-5 (round five), closed under D-056(a).

    THE ARGUMENT: **a diagnostic must describe the bundle it is about.** Both label
    cross-checks collapsed two different situations into one sentence -- "no
    meta.json/index.json to cross-check against" -- which is true when no metadata
    exists and FALSE when metadata exists but is silent about the field. The
    second is the case that occurs, so the verifier printed a false statement
    about a bundle that carries a meta.json.

    Three states are now told apart: metadata absent (skip, honestly), metadata
    present but silent (FAIL -- absence is not agreement, A-067), and usable
    metadata (the real cross-check).

    BOTH PATHS ARE PINNED. The receipt path reads `verdict` and the refusal path
    reads `signerRefused` through the same helper. The identical construction
    appeared twice, and repairing one occurrence while its sibling stands is the
    A-066 defect this repository has already paid for.
    """

    def staged_receipt(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        return stage(os.path.join(SAMPLES, "case-1-allow"), tmp)

    def staged_refusal(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        return stage(os.path.join(SAMPLES, "refusal-vault-paused"), tmp)

    @staticmethod
    def _detail(checks, needle):
        for c in checks:
            if needle in c.name:
                return c
        return None

    def test_intact_bundles_still_verify(self):
        # The control, for both paths. Without it a rule that fails everything
        # satisfies every assertion below.
        ok, _ = _verify(self.staged_receipt())
        self.assertTrue(ok)
        ok, _ = _verify(self.staged_refusal())
        self.assertTrue(ok)

    def test_genuinely_absent_metadata_is_still_skipped_and_still_says_so(self):
        # THE PRESERVED CONTROL John asked for by name. A bundle carrying no case
        # label at all is a legitimate shape: there is nothing to cross-check, the
        # check is skipped, and the original sentence is the TRUE one here.
        target = self.staged_receipt()
        os.remove(os.path.join(target, "meta.json"))
        index = os.path.join(os.path.dirname(target), "index.json")
        if os.path.isfile(index):
            os.remove(index)
        ok, checks = _verify(target)
        self.assertTrue(ok, "an unlabelled bundle must still verify")
        c = self._detail(checks, "decodes to")
        self.assertIsNotNone(c)
        self.assertTrue(c.skipped)
        self.assertIn("no meta.json/index.json", c.detail)

    def test_receipt_path_metadata_present_but_silent_is_not_reported_as_absent(self):
        # THE FALSE DIAGNOSTIC, in its exact shape. meta.json exists and carries no
        # `verdict`; index.json is removed so nothing else supplies it. Pre-fix this
        # printed "no meta.json/index.json to cross-check against" -- about a
        # directory containing a meta.json -- and PASSED.
        target = self.staged_receipt()
        meta = read_json(target, "meta.json")
        del meta["verdict"]
        write_json(os.path.join(target, "meta.json"), meta)
        index = os.path.join(os.path.dirname(target), "index.json")
        if os.path.isfile(index):
            os.remove(index)
        ok, checks = _verify(target)
        c = self._detail(checks, "decodes to")
        self.assertIsNotNone(c)
        self.assertNotIn(
            "no meta.json/index.json", c.detail,
            "the bundle HAS a meta.json; saying otherwise is the false diagnostic")
        self.assertIn("meta.json", c.detail)
        self.assertIn("verdict", c.detail)
        self.assertFalse(ok, "an uncheckable label must not pass silently")

    def test_refusal_path_metadata_present_but_silent_is_not_reported_as_absent(self):
        # The sibling. Same construction, different field, and it was equally wrong.
        target = self.staged_refusal()
        meta = read_json(target, "meta.json")
        del meta["signerRefused"]
        write_json(os.path.join(target, "meta.json"), meta)
        index = os.path.join(os.path.dirname(target), "index.json")
        if os.path.isfile(index):
            os.remove(index)
        ok, checks = _verify(target)
        c = self._detail(checks, "records a signer refusal")
        self.assertIsNotNone(c)
        self.assertNotIn("no meta.json/index.json", c.detail)
        self.assertIn("signerRefused", c.detail)
        self.assertFalse(ok)

    def test_a_usable_label_still_performs_the_real_cross_check(self):
        # The third state. Without this, "always fail when the field is missing"
        # would satisfy the rows above while the actual comparison rotted.
        target = self.staged_receipt()
        meta = read_json(target, "meta.json")
        meta["verdict"] = "BLOCK"          # the receipt decodes to ALLOW
        write_json(os.path.join(target, "meta.json"), meta)
        ok, checks = _verify(target)
        self.assertFalse(ok)
        c = self._detail(checks, "matching the case label")
        self.assertIsNotNone(c)
        self.assertIn("case label says BLOCK", c.detail)


class TestTheTrustRootMustBeAsserted(unittest.TestCase):
    """A-058 (H-1): no path inside the presented material can establish provenance.

    The 2026-08-17 repair searched the parent directory first and called what it found there
    "the deployment's copy". A presenter who ships `tree/domain.json` beside `tree/bundle/`
    supplies that file, so an outsider-signed receipt verified `=> PASS`, exit 0. These tests
    are written against the ARGUMENT rather than that demonstration, so BOTH invocation shapes
    are pinned -- the first draft of the repair closed the single-bundle path and left `--all`
    certifying the identical tree.
    """

    def hostile_tree(self):
        """A tree whose receipt is signed by an OUTSIDER key, presented with its own root.

        Everything is self-consistent: `receipt.signer` is inside the signed body and names
        the outsider, and the domain.json beside the bundle names it too. Only the question
        of WHERE that domain.json came from can reject this.
        """
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = os.path.join(tmp, "bundle")
        shutil.copytree(os.path.join(SAMPLES, "case-1-allow"), target)
        outsider = 0x00C0FFEE00C0FFEE00C0FFEE00C0FFEE00C0FFEE00C0FFEE00C0FFEE00C0FF01
        address = public_key_to_address(point_mul(outsider, G))
        domain = dict(read_json(SAMPLES, "domain.json"), signerAddress=address)
        write_json(os.path.join(tmp, "domain.json"), domain)
        doc = read_json(target, "receipt.json")
        doc["receipt"]["signer"] = address
        doc["signature"] = sign_digest(
            eip712.receipt_digest(domain, doc["receipt"]), outsider)
        write_json(os.path.join(target, "receipt.json"), doc)
        return tmp, target, address

    def test_the_outsider_tree_is_internally_consistent(self):
        # Without this the rejections below could be passing because the bundle is MALFORMED,
        # which would make every other test in this class worthless -- the A-056 rule that a
        # mode caught by a different check than the one it targets is worth nothing.
        #
        # So: assert the outsider's own root DELIBERATELY, and the tree verifies end to end.
        # That is not a defect. `--domain` means "I, the verifying party, state that this is
        # the deployment's signer", and a tool cannot stop someone asserting a false root on
        # purpose. The defect was reaching that same PASS with nobody having asserted anything.
        _, target, _ = self.hostile_tree()
        ok, checks = _verify(target)          # trust_root() names the attacker's own copy
        self.assertTrue(ok, "the outsider tree must be internally consistent, or the "
                            "rejections below prove nothing about provenance")
        by_name = {c.name: c for c in checks}
        for name in ("recovered signer == receipt.signer",
                     "recovered signer == domain.json signerAddress"):
            self.assertTrue(by_name[name].ok)

    def test_a_root_found_beside_the_bundle_cannot_certify(self):
        _, target, _ = self.hostile_tree()
        ok, checks = verify.verify_sample(target)          # nothing asserted
        self.assertFalse(ok, "an outsider-signed receipt was certified against a domain.json "
                             "the presenter supplied one directory up")
        failed = [c for c in checks if not c.ok]
        self.assertEqual([c.name for c in failed],
                         ["the trust root was ASSERTED by the verifying party, "
                          "not found in the material"])

    def test_a_root_found_inside_the_bundle_cannot_certify(self):
        tmp, target, address = self.hostile_tree()
        shutil.move(os.path.join(tmp, "domain.json"),
                    os.path.join(target, "domain.json"))
        ok, _ = verify.verify_sample(target)
        self.assertFalse(ok)

    def test_the_cli_refuses_to_certify_a_single_bundle_with_no_asserted_root(self):
        _, target, _ = self.hostile_tree()
        with open(os.devnull, "w") as devnull:
            saved, sys.stdout = sys.stdout, devnull
            try:
                self.assertEqual(verify.main([target]), 1)
            finally:
                sys.stdout = saved

    def test_the_cli_refuses_under_all_too(self):
        # THE BRANCH THE FIRST DRAFT OF THIS REPAIR LEFT OPEN. It treated the directory named
        # under `--all` as the caller's assertion; when the presenter hands you the tree, the
        # directory you name IS the presenter's, and `--all` printed `1/1 sample(s) verified`
        # on the identical hostile tree the single-bundle path had just started rejecting.
        tmp, _, _ = self.hostile_tree()
        with open(os.devnull, "w") as devnull:
            saved, sys.stdout = sys.stdout, devnull
            try:
                self.assertEqual(verify.main(["--all", tmp]), 1)
            finally:
                sys.stdout = saved

    def test_an_asserted_root_certifies_and_a_wrong_asserted_root_does_not(self):
        # `--domain` is an ASSERTION, so pointing it at the deployment's real root must still
        # certify the real samples -- otherwise this repair is just a guard that cries wolf.
        real = os.path.join(SAMPLES, "domain.json")
        ok, _ = verify.verify_sample(os.path.join(SAMPLES, "case-1-allow"), domain_path=real)
        self.assertTrue(ok)
        _, target, _ = self.hostile_tree()
        ok, checks = verify.verify_sample(target, domain_path=real)
        self.assertFalse(ok, "the outsider bundle was certified against the DEPLOYMENT's root")
        self.assertIn("recovered signer == domain.json signerAddress",
                      [c.name for c in checks if not c.ok])

    def test_a_bundle_copy_contradicting_the_asserted_root_is_an_error(self):
        tmp, target, _ = self.hostile_tree()
        shutil.copy(os.path.join(tmp, "domain.json"), os.path.join(target, "domain.json"))
        with self.assertRaises(ValueError):
            verify.verify_sample(target, domain_path=os.path.join(SAMPLES, "domain.json"))


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
                _, checks = _verify(path)
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

        ok, checks = _verify(target)
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

        ok, checks = _verify(target)
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
        ok, checks = _verify(target)
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

        ok, checks = _verify(target)
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

        ok, checks = _verify(target)
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
        _, checks = _verify(OVERRIDE_SAMPLE)
        canonical = [c for c in checks if "EIP-2 canonical (low-s)" in c.name]
        self.assertEqual(len(canonical), 2,
                         "both signatures in a bundle must be held to the "
                         "same canonical-form rule")
        self.assertTrue(all(c.ok for c in canonical))


# ---------------------------------------------------------------------------
# §5.5.1 SignedRefusalRecord
# ---------------------------------------------------------------------------

# A key that is neither the Sentinel signer nor the owner.
OUTSIDER_KEY = verify._OUTSIDER_TEST_KEY


def address_of(key):
    return public_key_to_address(point_mul(key, G))


def build_refusal_record(case_dir, key=SIGNER_KEY, **overrides):
    """A §5.5.1 RefusalRecord for a sample, built from §5.5.1's field list.

    Every value comes from the bundle itself or from §5.5.1's charset rules --
    nothing is copied from a shipped refusal artifact. The point of D-010 is
    that this is possible.
    """
    action = read_json(case_dir, "action.json")
    with open(os.path.join(case_dir, "evidence.hash"), "rb") as handle:
        evidence_hash = handle.read().decode().strip().lower()
    record = {
        "schemaVersion": action["schemaVersion"],
        "chainId": action["chainId"],
        "vault": action["vault"].lower(),
        "actionHash": "0x" + eip712.action_hash(action).hex(),
        "evidenceHash": evidence_hash,
        "requestedVerdict": read_json(case_dir, "evidence.json")["verdict"],
        "reasonCodesHash": reasoncodes.reason_codes_hash_hex(
            read_json(case_dir, "receipt.json").get("reasonCodes") or []),
        "refusedAt": "1786916613",
        "signer": address_of(key),
    }
    record.update(overrides)
    return record


class TestRefusalDigest(unittest.TestCase):
    """§5.5.1's digest, pinned against the specification's own words.

    §5.5.1 prints the preimage explicitly, so unlike §5.4's EIP-712 digest
    (REPORT.md F-1, recovered by brute-force search) nothing here is a
    reconstruction. These tests exist to keep it that way.
    """

    RECORD = {
        "schemaVersion": "1",
        "chainId": "31337",
        "vault": "0xe7f1725e7734ce288f8367e1bb143e90bb3f0512",
        "actionHash": "0x" + "11" * 32,
        "evidenceHash": "0x" + "22" * 32,
        "requestedVerdict": "BLOCK",
        "reasonCodesHash": "0x" + "33" * 32,
        "refusedAt": "1786916613",
        "signer": "0x70997970c51812dc3a010c7d01b50e0d17dc79c8",
    }

    def hand_built(self):
        # Transcribed from §5.5.1, one concatenation per printed line.
        r = self.RECORD
        return (
            "sentinel.refusal.v0.2" + "\n"
            + r["schemaVersion"] + "\n" + r["chainId"] + "\n" + r["vault"] + "\n"
            + r["actionHash"] + "\n" + r["evidenceHash"] + "\n"
            + r["requestedVerdict"] + "\n"
            + r["reasonCodesHash"] + "\n" + r["refusedAt"] + "\n" + r["signer"]
        ).encode("utf-8")

    def test_preimage_is_the_section_5_5_1_string(self):
        self.assertEqual(refusal.preimage(self.RECORD), self.hand_built())

    def test_digest_is_keccak_of_that_string(self):
        self.assertEqual(refusal.digest_hex(self.RECORD),
                         keccak256_hex(self.hand_built()))

    def test_digest_is_pinned(self):
        # A literal, so a later refactor that changes the construction breaks
        # loudly instead of staying self-consistent.
        self.assertEqual(
            refusal.digest_hex(self.RECORD),
            "0x6805267dae6fdd49207cb4d935ebfbda542d26264e141290db3ad5e5ca492baa")

    def test_no_trailing_delimiter(self):
        # The §5.4 edge-single-reason-code fixture exists because a producer
        # appending the delimiter hashes identically on every other sample. The
        # same keystroke is available here.
        self.assertFalse(refusal.preimage(self.RECORD).endswith(b"\n"))
        self.assertEqual(refusal.preimage(self.RECORD).count(b"\n"), 9)
        self.assertEqual(len(refusal.preimage(self.RECORD).split(b"\n")), 10)

    def test_domain_tag_is_byte_exact(self):
        self.assertEqual(refusal.DOMAIN_TAG, "sentinel.refusal.v0.2")
        self.assertTrue(refusal.preimage(self.RECORD)
                        .startswith(b"sentinel.refusal.v0.2\n"))

    def test_a_different_domain_tag_is_a_different_digest(self):
        saved = refusal.DOMAIN_TAG
        try:
            refusal.DOMAIN_TAG = "sentinel.refusal.v0.3"
            self.assertNotEqual(refusal.digest_hex(self.RECORD),
                                keccak256_hex(self.hand_built()))
        finally:
            refusal.DOMAIN_TAG = saved

    def test_field_order_follows_section_5_5_1(self):
        self.assertEqual(
            list(refusal.FIELD_NAMES),
            ["schemaVersion", "chainId", "vault", "actionHash", "evidenceHash",
             "requestedVerdict", "reasonCodesHash", "refusedAt", "signer"])

    def test_field_order_is_part_of_the_format(self):
        # §5.5.1 says so in bold. Two records differing only by which of two
        # same-charset values sits in which slot must not share a digest.
        swapped = dict(self.RECORD,
                       actionHash=self.RECORD["evidenceHash"],
                       evidenceHash=self.RECORD["actionHash"])
        self.assertNotEqual(refusal.digest_hex(swapped),
                            refusal.digest_hex(self.RECORD))

    def test_it_is_not_an_eip712_digest(self):
        # §5.5.1: "This record is NOT an EIP-712 typed structure."
        self.assertNotIn(b"\x19\x01", refusal.preimage(self.RECORD)[:2])
        domain = read_json(SAMPLES, "domain.json")
        separator = eip712.domain_separator(domain)
        self.assertNotEqual(
            refusal.digest(self.RECORD),
            keccak256(b"\x19\x01" + separator + refusal.digest(self.RECORD)))


class TestRefusalCharsets(unittest.TestCase):
    """§5.5.1's charsets are the whole of its injectivity argument."""

    def record(self, **overrides):
        return dict(TestRefusalDigest.RECORD, **overrides)

    def test_the_good_record_validates(self):
        self.assertEqual(len(refusal.canonical_fields(self.record())), 9)

    def test_rejected_values(self):
        cases = {
            "decimal with a sign": {"chainId": "+31337"},
            "decimal with whitespace": {"chainId": " 31337"},
            "decimal with a trailing newline": {"chainId": "31337\n"},
            "decimal as a JSON number": {"chainId": 31337},
            "decimal that is empty": {"refusedAt": ""},
            "hex chainId": {"chainId": "0x7a69"},
            "checksummed vault": {
                "vault": "0xE7f1725E7734CE288F8367e1Bb143E90bb3F0512"},
            "uppercase hash": {"actionHash": "0x" + "AB" * 32},
            "hash missing its 0x": {"evidenceHash": "11" * 32},
            "hash of the wrong width": {"evidenceHash": "0x" + "11" * 31},
            "address of the wrong width": {"signer": "0x" + "11" * 19},
            "verdict as its §5.9 number": {"requestedVerdict": "2"},
            "verdict in lower case": {"requestedVerdict": "block"},
            "verdict that is not one": {"requestedVerdict": "REFUSE"},
            "verdict as a JSON null": {"requestedVerdict": None},
            "boolean in a string slot": {"schemaVersion": True},
        }
        for label, override in cases.items():
            with self.subTest(case=label):
                with self.assertRaises(refusal.RefusalError):
                    refusal.canonical_fields(self.record(**override))

    def test_a_missing_field_cannot_be_defaulted(self):
        for name in refusal.FIELD_NAMES:
            with self.subTest(field=name):
                short = self.record()
                del short[name]
                with self.assertRaises(refusal.RefusalError):
                    refusal.canonical_fields(short)

    def test_an_extra_field_is_refused_rather_than_ignored(self):
        # The preimage commits to exactly nine values, so a tenth is
        # unauthenticated data a reader would reasonably assume is signed.
        with self.assertRaises(refusal.RefusalError):
            refusal.canonical_fields(self.record(expiresAt="1786916913"))

    def test_the_charsets_are_what_makes_the_encoding_injective(self):
        # §5.5.1: "The encoding is injective because every field is a fixed
        # charset that cannot contain the newline delimiter." Two DIFFERENT
        # nine-field records, each with one delimiter smuggled into a value,
        # join to the same bytes -- so one signature would attest to both.
        base = self.record()
        a = dict(base, requestedVerdict="BLOCK\nSMUGGLED",
                 reasonCodesHash="0x" + "33" * 32)
        b = dict(base, requestedVerdict="BLOCK",
                 reasonCodesHash="SMUGGLED\n0x" + "33" * 32)
        joined = lambda r: "\n".join(  # noqa: E731 - a two-line helper
            [refusal.DOMAIN_TAG] + [r[n] for n in refusal.FIELD_NAMES])
        self.assertNotEqual(a, b)
        self.assertEqual(joined(a), joined(b),
                         "the premise: without the charsets these collide")
        for label, record in (("a", a), ("b", b)):
            with self.subTest(record=label):
                with self.assertRaises(refusal.RefusalError):
                    refusal.canonical_fields(record)

    def test_leading_zeros_are_advisory_not_a_collision(self):
        # §5.5.1 says "decimal digits" and no more, so "031337" conforms. It
        # enters the preimage verbatim, so it produces a DIFFERENT digest
        # rather than a colliding one -- which is why it is surfaced rather
        # than rejected. See REPORT.md F-18.3.
        loose = self.record(chainId="031337")
        self.assertEqual(len(refusal.canonical_fields(loose)), 9)
        self.assertNotEqual(refusal.digest_hex(loose),
                            refusal.digest_hex(self.record()))
        self.assertEqual(refusal.noncanonical_decimals(loose), ["chainId"])
        self.assertEqual(refusal.noncanonical_decimals(self.record()), [])


class TestRefusalBundle(unittest.TestCase):
    """End-to-end bundles, every one of them synthesised from §5.5.1.

    The staged bundles use `refusal.json` with the record nested one level;
    `refusal-vault-paused` in the corpus uses a different envelope again. Both
    are covered, because §5.5.1 specifies neither (REPORT.md F-18.2).
    """

    CASE = os.path.join(SAMPLES, "case-1-allow")

    def stage_refusal(self, key=SIGNER_KEY, sign=True, doc=None, receipt=None,
                      meta_refused=True, case=None, **overrides):
        case = case or self.CASE
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = stage(case, tmp)
        source = read_json(case, "receipt.json")
        record = build_refusal_record(case, key=key, **overrides)
        envelope = {
            "refusal": record,
            "reasonCodes": source.get("reasonCodes") or [],
            "signerFindings": source.get("signerFindings") or [],
        }
        if sign:
            try:
                envelope["signerSignature"] = sign_digest(
                    refusal.digest(record), key)
            except refusal.RefusalError:
                # A record this malformed cannot be digested, so it cannot be
                # signed either. Attach a well-formed but meaningless
                # signature: the shape check runs first and must reject the
                # bundle before anything looks at the signature at all.
                envelope["signerSignature"] = "0x" + "11" * 64 + "1b"
        if doc is not None:
            envelope.update(doc)
        write_json(os.path.join(target, "refusal.json"), envelope)
        write_json(os.path.join(target, "receipt.json"),
                   {"refused": True} if receipt is None else receipt)
        meta = read_json(case, "meta.json")
        meta["signerRefused"] = meta_refused
        write_json(os.path.join(target, "meta.json"), meta)
        return target

    def run_sample(self, target):
        return _verify(target)

    def assertFailsOn(self, checks, fragment):
        failed = [c.name for c in checks if not c.ok]
        self.assertTrue(any(fragment in name for name in failed),
                        f"expected a failure naming {fragment!r}; failures "
                        f"were {failed}")

    # -- the happy path ---------------------------------------------------

    def test_a_properly_signed_refusal_verifies(self):
        ok, checks = self.run_sample(self.stage_refusal())
        self.assertTrue(ok, [c.name for c in checks if not c.ok])
        names = [c.name for c in checks]
        for expected in (
            "the signature recovers the record's declared signer",
            "the recovered signer is the deployment's Sentinel signer",
            "refusal.evidenceHash binds the recomputed evidence",
            "recomputed actionHash from §5.3 ActionPayload matches the "
            "refusal record",
            "refusal.chainId/vault match the presented deployment (§5.5.1)",
            "refusal.reasonCodesHash recomputed from the published reason codes",
        ):
            self.assertIn(expected, names)

    def test_the_cli_exits_zero_on_a_signed_refusal(self):
        target = self.stage_refusal()
        with open(os.devnull, "w") as devnull:
            saved, sys.stdout = sys.stdout, devnull
            try:
                self.assertEqual(
                    verify.main(["--domain", trust_root(target), target]), 0)
            finally:
                sys.stdout = saved

    def test_the_flat_envelope_verifies_identically(self):
        # §5.5.1: "SignedRefusalRecord contains RefusalRecord plus
        # signerSignature" reads equally well flat or nested, and specifies
        # neither. Both must reach the same verdict or the envelope silently
        # decides verification.
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = stage(self.CASE, tmp)
        record = build_refusal_record(self.CASE)
        flat = dict(record)
        flat["signerSignature"] = sign_digest(refusal.digest(record), SIGNER_KEY)
        flat["reasonCodes"] = []
        write_json(os.path.join(target, "refusal.json"), flat)
        write_json(os.path.join(target, "receipt.json"), {"refused": True})
        meta = read_json(self.CASE, "meta.json")
        meta["signerRefused"] = True
        write_json(os.path.join(target, "meta.json"), meta)
        ok, checks = self.run_sample(target)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])

    def test_the_record_may_travel_inside_receipt_json(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = stage(self.CASE, tmp)
        record = build_refusal_record(self.CASE)
        write_json(os.path.join(target, "receipt.json"), {
            "refused": True,
            "refusalRecord": record,
            "signerSignature": sign_digest(refusal.digest(record), SIGNER_KEY),
            "reasonCodes": [],
        })
        meta = read_json(self.CASE, "meta.json")
        meta["signerRefused"] = True
        write_json(os.path.join(target, "meta.json"), meta)
        ok, checks = self.run_sample(target)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])

    # -- unsigned, absent, contradictory ----------------------------------

    def test_an_unsigned_record_is_not_certified(self):
        ok, checks = self.run_sample(self.stage_refusal(sign=False))
        self.assertFalse(ok, "an unsigned refusal record was certified")
        self.assertFailsOn(checks, "the refusal record is signed")

    def test_an_absent_record_is_an_unestablished_refusal(self):
        # §5.5.1: "a verifier must treat an absent record as an unestablished
        # refusal rather than an established one." This is the F-13 behaviour,
        # now with a specification behind it instead of a judgement call.
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = stage(self.CASE, tmp)
        write_json(os.path.join(target, "receipt.json"),
                   {"refused": True, "refusalReason": "signer declined"})
        ok, checks = self.run_sample(target)
        self.assertFalse(ok)
        self.assertFailsOn(checks, "a signed receipt is present to verify")

    def test_a_refusal_beside_a_signed_receipt_fails(self):
        ok, checks = self.run_sample(
            self.stage_refusal(receipt=read_json(self.CASE, "receipt.json")))
        self.assertFalse(ok)
        self.assertFailsOn(checks, "a decision OR a refusal, not both")

    def test_a_refusal_with_refused_false_fails(self):
        ok, checks = self.run_sample(
            self.stage_refusal(receipt={"refused": False}))
        self.assertFalse(ok)
        self.assertFailsOn(checks, "`refused` flag agrees")

    def test_a_refusal_the_case_label_denies_fails(self):
        ok, checks = self.run_sample(self.stage_refusal(meta_refused=False))
        self.assertFalse(ok)
        self.assertFailsOn(checks, "the case label records a signer refusal")

    def test_two_disagreeing_records_are_both_rejected(self):
        target = self.stage_refusal()
        other = build_refusal_record(self.CASE, refusedAt="1786916999")
        write_json(os.path.join(target, "receipt.json"), {
            "refused": True,
            "refusalRecord": other,
            "signerSignature": sign_digest(refusal.digest(other), SIGNER_KEY),
        })
        ok, checks = self.run_sample(target)
        self.assertFalse(ok)
        self.assertFailsOn(checks, "at most one §5.5.1 SignedRefusalRecord")

    # -- malformed --------------------------------------------------------

    def test_malformed_records_fail(self):
        cases = {
            "missing a field": {"drop": "refusedAt"},
            "extra field": {"expiresAt": "1786916913"},
            "checksummed signer": {
                "signer": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"},
            "verdict as a number": {"requestedVerdict": "2"},
            "hash of the wrong width": {"evidenceHash": "0x" + "11" * 31},
            "delimiter smuggled into a value": {
                "requestedVerdict": "ALLOW\nSMUGGLED"},
        }
        for label, override in cases.items():
            with self.subTest(case=label):
                drop = override.pop("drop", None)
                target = self.stage_refusal(**override)
                if drop:
                    doc = read_json(target, "refusal.json")
                    del doc["refusal"][drop]
                    write_json(os.path.join(target, "refusal.json"), doc)
                ok, checks = self.run_sample(target)
                self.assertFalse(ok, f"{label} was accepted")
                self.assertFailsOn(checks, "exactly the nine §5.5.1 fields")

    def test_a_corrupt_signature_fails(self):
        target = self.stage_refusal()
        doc = read_json(target, "refusal.json")
        sig = doc["signerSignature"]
        doc["signerSignature"] = ("0x%02x" % (int(sig[2:4], 16) ^ 1)) + sig[4:]
        write_json(os.path.join(target, "refusal.json"), doc)
        ok, checks = self.run_sample(target)
        self.assertFalse(ok)

    def test_a_high_s_signature_is_rejected(self):
        target = self.stage_refusal()
        doc = read_json(target, "refusal.json")
        r, s, v = parse_signature(doc["signerSignature"])
        self.assertTrue(is_low_s(s))
        doc["signerSignature"] = ("0x" + r.to_bytes(32, "big").hex()
                                  + (N - s).to_bytes(32, "big").hex()
                                  + bytes([{27: 28, 28: 27}[v]]).hex())
        write_json(os.path.join(target, "refusal.json"), doc)
        ok, checks = self.run_sample(target)
        self.assertFalse(ok, "a malleated refusal signature was accepted")
        self.assertFailsOn(checks, "refusal signature is EIP-2 canonical")
        signer = [c for c in checks
                  if c.name == "the signature recovers the record's declared "
                               "signer"]
        self.assertTrue(signer and signer[0].ok,
                        "the identity check must still pass, or this tests "
                        "signature parsing rather than canonical form")

    # -- wrong signer -----------------------------------------------------

    def test_a_self_consistent_outsider_refusal_fails(self):
        # The attack the record cannot catch on its own: an outsider mints a
        # RefusalRecord naming their OWN key as `signer` and signs it. Digest,
        # recovery and every binding are correct. Only "is this Sentinel's
        # key?" rejects it.
        target = self.stage_refusal(key=OUTSIDER_KEY)
        ok, checks = self.run_sample(target)
        self.assertFalse(ok, "anyone could mint a refusal")
        recovered = [c for c in checks
                     if c.name == "the signature recovers the record's "
                                  "declared signer"]
        self.assertTrue(recovered and recovered[0].ok,
                        "the forgery is internally consistent by construction")
        self.assertFailsOn(checks, "deployment's Sentinel signer")

    def test_a_swapped_signer_field_fails(self):
        # Signed correctly, then `signer` rewritten. §5.5.1 puts signer inside
        # the preimage, so the digest moves and recovery lands elsewhere.
        target = self.stage_refusal()
        doc = read_json(target, "refusal.json")
        doc["refusal"]["signer"] = address_of(OUTSIDER_KEY)
        write_json(os.path.join(target, "refusal.json"), doc)
        ok, checks = self.run_sample(target)
        self.assertFalse(ok)
        self.assertFailsOn(checks, "recovers the record's declared signer")

    def test_an_eip191_signature_fails_and_says_so(self):
        # §5.5.1 states the digest and never states how it is signed. A
        # producer reaching for a wallet library's signMessage lands here, and
        # the only symptom is a signer mismatch. REPORT.md F-18.1.
        target = self.stage_refusal(sign=False)
        doc = read_json(target, "refusal.json")
        digest = refusal.digest(doc["refusal"])
        doc["signerSignature"] = sign_digest(
            refusal.eth_signed_message_digest(digest), SIGNER_KEY)
        write_json(os.path.join(target, "refusal.json"), doc)
        ok, checks = self.run_sample(target)
        self.assertFalse(ok, "an EIP-191 signature must not be accepted "
                             "silently either")
        detail = "\n".join(c.detail for c in checks if not c.ok)
        self.assertIn("EIP-191", detail,
                      "the failure must name the near-miss, or a construction "
                      "disagreement reads as a forgery")

    # -- mis-bound --------------------------------------------------------

    def test_misbound_records_fail_despite_valid_signatures(self):
        other = os.path.join(SAMPLES, "edge-single-reason-code")
        other_action = "0x" + eip712.action_hash(
            read_json(other, "action.json")).hex()
        with open(os.path.join(other, "evidence.hash"), "rb") as handle:
            other_evidence = handle.read().decode().strip().lower()
        cases = {
            "another action": ({"actionHash": other_action},
                               "recomputed actionHash"),
            "another evidence bundle": ({"evidenceHash": other_evidence},
                                        "evidenceHash binds"),
            "another chain": ({"chainId": "8453"}, "chainId"),
            "another vault": ({"vault": "0x" + "11" * 20}, "vault"),
            "another requested verdict": ({"requestedVerdict": "BLOCK"},
                                          "requestedVerdict"),
            "another reason set": ({"reasonCodesHash": "0x" + "44" * 32},
                                   "reasonCodesHash"),
        }
        for label, (override, fragment) in cases.items():
            with self.subTest(case=label):
                target = self.stage_refusal(**override)
                ok, checks = self.run_sample(target)
                self.assertFalse(ok, f"a refusal bound to {label} was accepted")
                self.assertFailsOn(checks, fragment)

    def test_a_signed_refusal_cannot_be_lifted_to_another_deployment(self):
        # §5.5.1's digest carries no domain separator -- the tag is a constant.
        # The record's own chainId/vault members are the entire deployment
        # binding, and they only bind if a verifier reads them (F-14's lesson).
        target = self.stage_refusal()
        elsewhere = dict(read_json(SAMPLES, "domain.json"), chainId="8453")
        write_json(os.path.join(os.path.dirname(target), "domain.json"),
                   elsewhere)
        ok, checks = self.run_sample(target)
        self.assertFalse(ok, "a refusal was accepted on another chain")

    def test_the_reason_code_list_must_travel_alongside(self):
        # §5.5.1 gives reasonCodesHash §5.4's encoding, and §5.4 requires the
        # list to travel with the commitment.
        target = self.stage_refusal(case=os.path.join(
            SAMPLES, "edge-single-reason-code"))
        doc = read_json(target, "refusal.json")
        del doc["reasonCodes"]
        write_json(os.path.join(target, "refusal.json"), doc)
        ok, checks = self.run_sample(target)
        self.assertFalse(ok)
        self.assertFailsOn(checks, "reasonCodesHash recomputed")

    def test_substituting_the_reason_code_list_fails(self):
        target = self.stage_refusal(case=os.path.join(
            SAMPLES, "edge-single-reason-code"))
        doc = read_json(target, "refusal.json")
        doc["reasonCodes"] = ["EVAL_SOMETHING_ELSE"]
        write_json(os.path.join(target, "refusal.json"), doc)
        ok, checks = self.run_sample(target)
        self.assertFalse(ok)
        self.assertFailsOn(checks, "reasonCodesHash recomputed")

    def test_signer_findings_must_be_a_subset(self):
        target = self.stage_refusal()
        doc = read_json(target, "refusal.json")
        doc["signerFindings"] = ["SIGNER_INVENTED_FINDING"]
        write_json(os.path.join(target, "refusal.json"), doc)
        ok, checks = self.run_sample(target)
        self.assertFalse(ok)
        self.assertFailsOn(checks, "signerFindings")

    def test_a_shadowing_array_in_the_envelope_cannot_hide_the_top_level_one(self):
        """A-061 (from A-058, H-3). A-055's repair resolved the two locations by PRECEDENCE.

        Absent is not the same as trustworthy. `refusal-vault-paused` — the repository's only
        refusal artifact — puts `reasonCodes` in the envelope and `signerFindings` at the TOP
        LEVEL, so adding `"signerFindings": []` to the envelope shadowed the array actually in
        use and the subset invariant passed over an empty set. Reproduced against the
        unmutated verifier: an uncommitted reason code verified `=> PASS`, exit 0.

        Written against the CORPUS'S OWN SHAPE, which is the specific thing the pre-existing
        subset test could not do — it co-locates both keys in one envelope, so it never
        exercised the split layout while its docstring claimed both were covered.
        """
        target = self.stage_refusal_corpus_shape()
        doc = read_json(target, "receipt.json")
        self.assertIsNotNone(doc.get("signerFindings"),
                             "this fixture must carry findings at the TOP LEVEL, or the test "
                             "is not exercising the shape the defect lived in")
        doc["signerFindings"] = list(doc["signerFindings"]) + ["SIGNER_UNCOMMITTED_CODE"]
        doc["refusalRecord"]["signerFindings"] = []          # the single shadowing key
        write_json(os.path.join(target, "receipt.json"), doc)
        ok, checks = _verify(target)
        self.assertFalse(ok, "an uncommitted reason code was hidden by a shadowing array")
        self.assertIn("`signerFindings` is published once, not twice with different contents",
                      [c.name for c in checks if not c.ok])

    def test_the_same_hole_in_reason_codes_is_closed_too(self):
        # The ARGUMENT, not the demonstration: the identical precedence applied to
        # `reasonCodes`, so the list a reader sees could differ entirely from the list that
        # was hashed. Fixing only the array the reviewer exploited would be this project's
        # most-repeated defect.
        target = self.stage_refusal_corpus_shape()
        doc = read_json(target, "receipt.json")
        doc["reasonCodes"] = ["EVAL_NO_INJECTION_DETECTED", "EVAL_PURPOSE_CONFORMS"]
        write_json(os.path.join(target, "receipt.json"), doc)
        ok, checks = _verify(target)
        self.assertFalse(ok)
        self.assertIn("`reasonCodes` is published once, not twice with different contents",
                      [c.name for c in checks if not c.ok])

    def test_the_unmodified_corpus_refusal_still_verifies(self):
        # The paired positive. Without it, a rule that rejects every refusal satisfies both
        # tests above, and the split layout the corpus actually ships would be the casualty.
        target = self.stage_refusal_corpus_shape()
        ok, checks = _verify(target)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])
        self.assertTrue(next(c for c in checks
                             if c.name == "signerFindings ⊆ the committed reason-code set").ok)

    def stage_refusal_corpus_shape(self):
        """The shipped refusal bundle, copied verbatim: reasonCodes in the envelope,
        signerFindings at the top level. Deliberately NOT the co-located envelope the other
        refusal tests build."""
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        return stage(os.path.join(SAMPLES, "refusal-vault-paused"), tmp)

    def test_the_refusal_corpus_bundle_verifies_as_committed(self):
        # THE PAIRED CONTROL for the test below. Without it that test could be passing because
        # `stage_refusal_corpus_shape` produces a broken bundle rather than because the new
        # check works — the failure mode A-056 named when a constructed override raised inside
        # `struct_hash` and the test "passed" for an unrelated reason.
        target = self.stage_refusal_corpus_shape()
        ok, checks = self.run_sample(target)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])

    def test_a_refusal_bundle_carrying_an_owner_override_is_refused(self):
        # D-052(b), from round six L6-2. A defect of ORDER: `verify_sample` calls
        # `_refusal_checks` and RETURNS, while `_override_checks` sits below that return — so
        # `override.json` was never opened on this path and an override minted by an arbitrary
        # outsider key rode along inside a bundle this verifier printed `=> PASS` over. The
        # SAME artifact is correctly rejected on the receipt path by A-059's owner-identity
        # check, and the verifier's own `--tamper all` arm printed six consecutive
        # `WRONGLY ACCEPTED` lines for the override modes on the very bundle the certifying arm
        # passed.
        #
        # It is REFUSED rather than checked: §0 of `_refusal_checks` already rejects a bundle
        # presenting a decision and a refusal together, on the ground that certifying it would
        # certify whichever half the reader looked at. An override is an authorization, so a
        # refusal carrying one is that same shape.
        target = self.stage_refusal_corpus_shape()
        shutil.copy(os.path.join(OVERRIDE_SAMPLE, "override.json"),
                    os.path.join(target, "override.json"))
        ok, checks = self.run_sample(target)
        self.assertFalse(ok, "a refusal bundle carrying an unexamined §5.5 override verified")
        self.assertFailsOn(checks, "refusal bundle carries no")

    def test_a_refusal_with_no_action_payload_fails(self):
        # §5.5.1: "A refusal is attributable or it is not issued." The record
        # names no mandate and no policy; actionHash is the only route to
        # either, and it is only walkable with the action payload in hand.
        target = self.stage_refusal()
        os.remove(os.path.join(target, "action.json"))
        ok, checks = self.run_sample(target)
        self.assertFalse(ok)
        self.assertFailsOn(checks, "refusal.actionHash binds")


class TestRefusalSampleInCorpus(unittest.TestCase):
    """The corpus gained a §5.5.1 refusal sample on 2026-08-16.

    Nothing in this verifier was tuned to it: the record's field list, order,
    charsets, digest and signature construction were implemented from §5.5.1
    and matched on the first run. The one thing that did NOT match is the one
    thing §5.5.1 does not specify -- the envelope carrying the record. See
    REPORT.md F-18.2.
    """

    def test_the_corpus_carries_at_least_one_refusal_sample(self):
        self.assertTrue(refusal_sample_dirs(),
                        "§5.5.1 is untested by any artifact again")

    def test_every_refusal_sample_verifies(self):
        for path in refusal_sample_dirs():
            with self.subTest(sample=os.path.basename(path)):
                ok, checks = _verify(path)
                self.assertTrue(ok, [c.name for c in checks if not c.ok])

    def test_every_refusal_sample_is_actually_verified_not_skipped(self):
        # A pass made of skips is what F-13 was. Name the checks that must
        # have genuinely run.
        for path in refusal_sample_dirs():
            with self.subTest(sample=os.path.basename(path)):
                _, checks = _verify(path)
                ran = {c.name for c in checks if c.ok and not c.skipped}
                for expected in (
                    "the signature recovers the record's declared signer",
                    "the recovered signer is the deployment's Sentinel signer",
                    "refusal.evidenceHash binds the recomputed evidence",
                    "recomputed actionHash from §5.3 ActionPayload matches "
                    "the refusal record",
                    "refusal.reasonCodesHash recomputed from the published "
                    "reason codes",
                ):
                    self.assertIn(expected, ran)

    def test_no_refusal_sample_presents_a_signed_receipt(self):
        for path in refusal_sample_dirs():
            with self.subTest(sample=os.path.basename(path)):
                doc = read_json(path, "receipt.json")
                self.assertIsNone(doc.get("receipt"))
                self.assertIsNone(doc.get("signature"))

    def test_every_refusal_tamper_mode_is_rejected(self):
        modes = [m for m in verify.TAMPER_MODES if m.startswith("refusal-")]
        self.assertGreaterEqual(len(modes), 10)
        for path in refusal_sample_dirs():
            for mode in modes:
                with self.subTest(sample=os.path.basename(path), mode=mode):
                    try:
                        ok, _ = _verify(path, tamper=mode)
                    except verify.NotApplicable:
                        continue
                    self.assertFalse(ok, f"{mode} was WRONGLY ACCEPTED")

    def test_a_refusal_and_a_receipt_for_the_SAME_action_both_exist(self):
        # The corpus happens to contain the sharpest available adversarial
        # pair: a signed ALLOW receipt and a signed refusal naming the SAME
        # actionHash, differing only in their evidence. So actionHash alone
        # cannot tell a verifier which bundle a refusal belongs to.
        refusal_case = os.path.join(SAMPLES, "refusal-vault-paused")
        allow_case = os.path.join(SAMPLES, "case-1-allow")
        if not os.path.isdir(refusal_case):
            self.skipTest("no refusal-vault-paused sample in this corpus")
        self.assertEqual(
            eip712.action_hash(read_json(refusal_case, "action.json")),
            eip712.action_hash(read_json(allow_case, "action.json")),
            "the premise of this test no longer holds")

    def test_a_refusal_cannot_be_moved_onto_a_same_action_bundle(self):
        # Move the genuine, untouched, validly-signed refusal onto the ALLOW
        # bundle for the same action. Its actionHash matches. Only the evidence
        # binding says no -- which is why both bindings are checked.
        refusal_case = os.path.join(SAMPLES, "refusal-vault-paused")
        allow_case = os.path.join(SAMPLES, "case-1-allow")
        if not os.path.isdir(refusal_case):
            self.skipTest("no refusal-vault-paused sample in this corpus")
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = stage(allow_case, tmp)
        for name in ("receipt.json", "meta.json"):
            shutil.copy(os.path.join(refusal_case, name),
                        os.path.join(target, name))
        ok, checks = _verify(target)
        self.assertFalse(ok, "a signed refusal was moved onto another bundle")
        failed = [c.name for c in checks if not c.ok]
        self.assertIn("refusal.evidenceHash binds the recomputed evidence",
                      failed)
        action_bound = [c for c in checks if "recomputed actionHash" in c.name]
        self.assertTrue(action_bound and action_bound[0].ok,
                        "the action binding must still pass, or this tests "
                        "something other than what it claims to")

    def test_refusal_tamper_modes_are_not_applicable_to_receipt_samples(self):
        for path in sample_dirs():
            with self.subTest(sample=os.path.basename(path)):
                with self.assertRaises(verify.NotApplicable):
                    _verify(path, tamper="refusal-actionhash")


class TestEvidenceHashTamper(unittest.TestCase):
    """A-049. `evidence-hash` exists because a check nothing targets is a check
    nothing asserts: the review that found this neutered
    `keccak256(canonical bytes) matches evidence.hash` by hand and every one of the
    then-146 tests still passed, because no tamper mode mutated the published hash.
    """

    def test_the_mode_is_declared(self):
        # Structural, not behavioural. A mode can be implemented and never
        # registered -- this repository's most-repeated defect (D-042) -- and the
        # loop-driven tests below would then simply not run it.
        self.assertIn("evidence-hash", verify.TAMPER_MODES)

    def test_it_is_applicable_to_every_receipt_sample_and_is_rejected(self):
        for path in sample_dirs():
            with self.subTest(sample=os.path.basename(path)):
                ok, checks = _verify(path, tamper="evidence-hash")
                self.assertFalse(
                    ok, "a corrupted evidence.hash must not verify")
                named = [c for c in checks
                         if "matches evidence.hash" in c.name]
                self.assertTrue(
                    named, "the evidence.hash check must be among the checks run")
                self.assertFalse(
                    named[0].ok,
                    "the failure must come from the evidence.hash check itself, "
                    "not from some other check noticing the mutation")

    def test_the_unmutated_sample_passes_that_same_check(self):
        # Without this the test above could pass because the check ALWAYS fails.
        for path in sample_dirs():
            with self.subTest(sample=os.path.basename(path)):
                _, checks = _verify(path)
                named = [c for c in checks if "matches evidence.hash" in c.name]
                self.assertTrue(named)
                self.assertTrue(named[0].ok)


class TestUnassertedValidation(unittest.TestCase):
    """A-051. Three named properties whose only witness could not fail.

    A directed mutation sweep over the verifier's six non-`verify.py` modules applied
    142 behaviour-changing mutations and 41 survived a fully green gate. These three
    are the ones that flip a VERDICT rather than degrade a diagnostic: with each
    mutation in place the verifier CERTIFIES something it should reject, and every
    existing test still passed. The tests below are the missing witnesses.
    """

    # ---- S-1: pair-aligned whitespace in a hex value -------------------------
    #
    # `hex_to_bytes`'s own comment says why this matters: "bytes.fromhex accepts
    # them, so '0xde ad' and '0xdead' used to produce the same word." The guard test
    # inserted ONE space mid-string -- which breaks hex-pair alignment and is
    # therefore rejected by any pair-quantified pattern, including a widened one. So
    # widening `_HEX_BODY` to `[0-9a-fA-F ]{2}` survived, and two byte-distinct
    # MandatePayloads then shared one mandateHash while the gate stayed green.
    def test_hex_rejects_whitespace_on_an_EVEN_boundary(self):
        good = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
        for label, bad in (
                ("two trailing spaces", good + "  "),
                ("two leading spaces", "0x  " + good[2:]),
                ("a space pair at an even offset", good[:12] + "  " + good[12:]),
        ):
            with self.subTest(case=label):
                with self.assertRaises(eip712.EncodingError):
                    eip712.hex_to_bytes(bad, 20)

    def test_pair_aligned_whitespace_cannot_collide_an_encoded_word(self):
        # The property the test above protects, asserted at the encoder rather than the
        # parser. Written the second time: the first version nested assertNotEqual
        # INSIDE assertRaises, where it can never execute — a test shaped so that its
        # own assertion is unreachable, which is the defect this whole class is about.
        good = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
        word = eip712.encode_value("address", good)
        self.assertEqual(len(word), 32)
        for bad in (good + "  ", good[:12] + "  " + good[12:]):
            with self.subTest(bad=bad):
                try:
                    other = eip712.encode_value("address", bad)
                except eip712.EncodingError:
                    continue          # rejected outright: the property holds
                self.assertNotEqual(
                    other, word,
                    "an accepted alternate spelling encoded to the same word")

    # ---- S-2: strict= is asserted at one of five call sites ------------------
    #
    # `struct_hash`'s error text is "refusing to hash an under-determined struct",
    # and `refusal.canonical_fields` cites it as the rule it copies. Only the RECEIPT
    # site had a test. `strict=False` on any of the other four left an unauthenticated
    # field riding inside a document the verifier stamps PASS -- "approvedBy",
    # "note": "cleared by legal" -- with the gate green.
    def test_every_payload_struct_refuses_an_extra_field(self):
        d = sample_dirs()[0]
        cases = (
            ("mandate", eip712.mandate_hash, read_json(d, "mandate.json")),
            ("policy", eip712.policy_hash, read_json(d, "policy.json")),
            ("action", eip712.action_hash, read_json(d, "action.json")),
            ("receipt", eip712.receipt_struct_hash,
             read_json(d, "receipt.json")["receipt"]),
        )
        for name, fn, doc in cases:
            with self.subTest(struct=name):
                fn(doc)  # the unmutated document must still hash, or this proves nothing
                with self.assertRaises(eip712.EncodingError):
                    fn({**doc, "approvedBy": "0x00"})

    def test_the_override_struct_refuses_an_extra_field(self):
        for path in sample_dirs():
            override = os.path.join(path, "override.json")
            if not os.path.isfile(override):
                continue
            doc = read_json(path, "override.json")
            doc = doc.get("override", doc)
            eip712.override_hash(doc)
            with self.assertRaises(eip712.EncodingError):
                eip712.override_hash({**doc, "grantedBy": "0x00"})
            return
        self.fail("no override sample found; this test would assert nothing")

    # ---- S-3: signature length ----------------------------------------------
    #
    # `parse_signature` was only ever handed exactly 65 bytes. Relaxing `!= 65` to
    # `< 65` let arbitrary trailing bytes ride on a signature, so unboundedly many
    # byte-distinct signatures certify one receipt -- defeating anything downstream
    # that dedups or replay-protects on signature bytes.
    def test_an_over_length_signature_is_rejected(self):
        good = "0x" + "11" * 32 + "22" * 32 + "1b"
        parse_signature(good)  # 65 bytes must still parse
        for suffix in ("deadbeef", "00", "11" * 40):
            with self.subTest(extra=suffix[:8]):
                with self.assertRaises(Exception):
                    parse_signature(good + suffix)


class TestCharsetsByComplement(unittest.TestCase):
    """A-054. Charsets pinned by their COMPLEMENT rather than by a bad list.

    The mutation sweep (A-051) found both of these charsets widenable without any
    test noticing: adding tab, CR, backslash or `+` to the reason-code class was
    accepted, and §5.5.1's width bounds were pinned on the SHORT side only, so
    over-length hashes and addresses passed. The existing tests enumerate a handful
    of bad inputs -- which pins those spellings and nothing else. These walk the
    character space and assert the accept/reject PARTITION, so any widening of the
    class fails regardless of which character was added.

    §5.5.1's charsets are the whole of its injectivity argument, which is why the
    complement is the thing worth asserting rather than a sample of it.
    """

    # The declared classes, transcribed from the modules' own patterns. Transcribed
    # deliberately rather than imported: a test that reuses the pattern under test
    # cannot detect the pattern changing. That is the ERC-191 defect this sweep also
    # found, and it is avoided here on purpose.
    REASON_CODE_CHARS = set(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.:-")
    LOWER_HEX = set("0123456789abcdef")

    def _probe_space(self):
        # ASCII in full, plus a few non-ASCII that have bitten this project before.
        return [chr(c) for c in range(0x00, 0x80)] + ["É", " ", " ", "😀"]

    def test_reason_code_charset_is_exactly_the_declared_class(self):
        accepted, rejected = set(), set()
        for ch in self._probe_space():
            identifier = "EVAL" + ch + "OK"
            try:
                reasoncodes.validate(identifier)
                accepted.add(ch)
            except Exception:
                rejected.add(ch)
        expected = {ch for ch in self._probe_space() if ch in self.REASON_CODE_CHARS}
        self.assertEqual(
            accepted, expected,
            "the accepted character set drifted from [A-Za-z0-9_.:-]; "
            "unexpectedly accepted: %r; unexpectedly rejected: %r"
            % (sorted(accepted - expected), sorted(expected - accepted)))
        # Non-vacuity: the probe must actually exercise both sides.
        self.assertTrue(accepted and rejected)

    def test_reason_code_length_bound_is_pinned_on_BOTH_sides(self):
        reasoncodes.validate("A")
        reasoncodes.validate("A" * 64)
        for bad in ("", "A" * 65, "A" * 200):
            with self.subTest(length=len(bad)):
                with self.assertRaises(Exception):
                    reasoncodes.validate(bad)

    def test_refusal_hash_and_address_widths_are_pinned_on_BOTH_sides(self):
        # The sweep widened {64} to {64,} and {40} to {40,} and nothing failed:
        # over-length values were accepted. Short values were already covered.
        good32 = "0x" + "ab" * 32
        good20 = "0x" + "ab" * 20
        cases = (
            ("hash32", refusal.HASH32, good32, 64),
            ("address", refusal.ADDRESS, good20, 40),
        )
        for name, kind, good, width in cases:
            with self.subTest(kind=name):
                refusal.validate_field(name, kind, good)     # exact width must pass
                for bad in ("0x" + "a" * (width - 2),        # short
                            "0x" + "a" * (width + 2),        # LONG -- the unpinned side
                            "0x" + "a" * (width * 2),
                            good + " ",                      # trailing space
                            good.upper().replace("0X", "0x")):  # uppercase hex
                    with self.assertRaises(Exception, msg="accepted %r" % bad):
                        refusal.validate_field(name, kind, bad)

    def test_refusal_verdict_names_admit_no_padding_or_case_variation(self):
        for good in refusal.VERDICT_NAMES:
            refusal.validate_field("requestedVerdict", refusal.VERDICT, good)
        for bad in ("BLOCK ", " BLOCK", "block", "Block", "BLOCK\n", "BLOCKED", ""):
            with self.subTest(value=repr(bad)):
                with self.assertRaises(Exception):
                    refusal.validate_field("requestedVerdict", refusal.VERDICT, bad)


class TestVerifierPropertiesNotCorpusProperties(unittest.TestCase):
    """A-056. THE CATEGORY ERROR THIS CLASS EXISTS TO NAME.

    A directed sweep of `verify.py` found 14 named checks that nothing asserted, and
    three of them survived on one confusion: **a test that asserts a property of the
    CORPUS cannot catch a verifier that accepts what the corpus happens not to
    contain.** `test_only_review_receipts_carry_an_override` asserts that no fixture
    overrides a BLOCK receipt -- true, and worth knowing, and completely silent on
    whether the verifier would accept one. The sweep changed §5.5's check to
    `verdict in ("REVIEW", "BLOCK")` and every test still passed.

    The distinction is not pedantic and it is easy to get wrong in either direction:
    a fixture property says what the repository CONTAINS, a verifier property says
    what the code ACCEPTS. Only the second is a check on the verifier. Where a
    fixture property is worth asserting, assert it -- and do not let it stand in for
    the other one.
    """

    def _owner_key(self):
        return verify._OWNER_TEST_KEY

    def test_a_block_receipt_cannot_be_overridden_even_with_a_valid_owner_signature(self):
        # §5.5. Built rather than found: no fixture contains this, which is exactly why
        # the corpus-property test could not see it.
        block = None
        for path in sample_dirs():
            doc = read_json(path, "receipt.json")
            body = doc.get("receipt") or {}
            if str(body.get("verdict")) in ("0", "BLOCK"):
                block = (path, doc, body)
                break
        self.assertIsNotNone(block, "no BLOCK sample; this test would assert nothing")
        path, doc, body = block

        domain = read_json(os.path.dirname(path.rstrip("/")), "domain.json")
        # DERIVED from the genuine override rather than hand-built. A hand-built payload
        # can fail to hash for reasons that have nothing to do with §5.5, and a test that
        # errors for the wrong reason is the defect this class is about.
        template = None
        for other in sample_dirs():
            if os.path.isfile(os.path.join(other, "override.json")):
                template = read_json(other, "override.json")["override"]
                break
        self.assertIsNotNone(template, "no override template; this test would assert nothing")
        override = dict(template)
        override["reviewReceiptHash"] = "0x" + eip712.receipt_struct_hash(body).hex()
        for field in ("actionHash", "mandateHash", "policyHash"):
            override[field] = body[field]
        override["actionNonce"] = str(read_json(path, "action.json")["actionNonce"])
        sig = sign_digest(eip712.override_digest(domain, override), self._owner_key())
        owner = public_key_to_address(point_mul(self._owner_key(), G))

        with tempfile.TemporaryDirectory() as tmp:
            dest = os.path.join(tmp, "bundle")
            shutil.copytree(path, dest)
            with open(os.path.join(dest, "override.json"), "w") as fh:
                json.dump({"override": override, "ownerSignature": sig,
                           "ownerAddress": owner}, fh, indent=2)
            ok, checks = _verify(
                dest, domain_path=os.path.join(os.path.dirname(path.rstrip("/")),
                                               "domain.json"))

        self.assertFalse(ok, "a BLOCK receipt must not be overridable")
        named = [c for c in checks if "REVIEW receipt" in c.name]
        self.assertTrue(named, "§5.5's REVIEW-receipt check must be among those run")
        self.assertFalse(
            named[0].ok,
            "the rejection must come from §5.5's own check, not from some other "
            "check noticing the constructed bundle")

    def test_the_override_signature_itself_was_valid(self):
        # Without this, the test above could pass because the override was malformed
        # rather than because §5.5 rejected it -- which would make it another test
        # that cannot fail for the reason it names.
        for path in sample_dirs():
            override_path = os.path.join(path, "override.json")
            if not os.path.isfile(override_path):
                continue
            doc = read_json(path, "override.json")
            domain = read_json(os.path.dirname(path.rstrip("/")), "domain.json")
            recovered = recover_address(
                eip712.override_digest(domain, doc["override"]), doc["ownerSignature"])
            self.assertEqual(_norm(recovered), _norm(doc["ownerAddress"]))
            return
        self.fail("no override sample found; this test would assert nothing")


def _norm(a):
    return a.lower().replace("0x", "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
