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
import verify  # noqa: E402
from keccak import keccak256_hex  # noqa: E402
from secp256k1 import G, N, point_mul, public_key_to_address  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(REPO, "fixtures", "samples")


def read_json(*parts):
    with open(os.path.join(*parts), "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


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
    number as a JSON string (REPORT.md F-4). They are tested anyway because the
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
        self.assertEqual(len(dirs), 5, "expected the five §4.2 demonstration samples")
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
    def test_every_tamper_mode_is_rejected(self):
        for path in sample_dirs():
            for mode in verify.TAMPER_MODES:
                with self.subTest(sample=os.path.basename(path), mode=mode):
                    ok, _ = verify.verify_sample(path, tamper=mode)
                    self.assertFalse(ok, f"{mode} tamper was WRONGLY ACCEPTED")

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
        original = eip712.RECEIPT_TYPE
        try:
            eip712.RECEIPT_TYPE = original.replace(
                "uint16 schemaVersion", "uint256 schemaVersion"
            )
            ok, _ = verify.verify_sample(sample_dirs()[0])
            self.assertFalse(ok, "the type string is apparently not load-bearing")
        finally:
            eip712.RECEIPT_TYPE = original

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
    """No shipped sample sets refused=true (REPORT.md F-7), so the shape is
    synthesised here rather than left untested."""

    def _refused_copy(self, body):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        target = os.path.join(tmp, "case-refused")
        shutil.copytree(sample_dirs()[0], target)
        with open(os.path.join(target, "receipt.json"), "w") as handle:
            json.dump(body, handle)
        shutil.copy(os.path.join(SAMPLES, "domain.json"), tmp)
        return target

    def test_refused_receipt_still_verifies_evidence(self):
        path = self._refused_copy({
            "refused": True,
            "refusalReason": "signer declined: evidence anchor unavailable",
            "receipt": None,
            "signature": None,
        })
        ok, checks = verify.verify_sample(path)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])
        skipped = [c.name for c in checks if c.skipped]
        self.assertEqual(len(skipped), 2, "receipt-bound checks should be skipped")
        self.assertTrue(any("recanonicalization" in c.name and c.ok for c in checks))

    def test_refused_with_omitted_keys_does_not_crash(self):
        path = self._refused_copy({"refused": True})
        ok, _ = verify.verify_sample(path)
        self.assertTrue(ok)

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
        # case-1 has no reason codes and its reasonCodesHash is keccak256(""),
        # which REPORT.md F-6 flags as an unstated convention.
        doc = read_json(SAMPLES, "case-1-allow", "receipt.json")
        self.assertEqual(doc["receipt"]["reasonCodesHash"], keccak256_hex(b""))


if __name__ == "__main__":
    unittest.main(verbosity=2)
