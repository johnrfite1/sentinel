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
        # 5 samples x 3 core modes = 15; reason-code modes 17 (case-1's empty
        # list makes 3 N/A); override modes 4 (only case-4-review has one).
        self.assertEqual(exercised, 36, "expected 36 applicable tamper cases")

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
