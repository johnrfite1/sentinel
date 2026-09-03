#!/usr/bin/env python3
"""Tests for the Sentinel standalone receipt verifier (D-010).

Stdlib unittest only, no third-party test runner:

    python3 verifier/test_verifier.py
    python3 -m unittest discover -s verifier -v
"""

import contextlib
import inspect
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
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


def live_window(now=None):
    """A receipt window that contains the host instant: opened a minute ago, an hour left.

    D-092(c) (2026-09-02). Every shipped receipt fixture expired on 2026-08-29
    (`expiresAt` 1788059884), so a test that needs `=> PASS` / exit 0 can no longer
    read it off the corpus; it MINTS a bundle whose window contains now. The margin
    on each side is large against the run time of one test and small against the
    fixtures' 300-second lifetime, so a bundle minted here is live for the whole of
    the test that minted it and would not have been live yesterday.
    """
    now = int(time.time()) if now is None else int(now)
    return now - 60, now + 3600


def rewindow(target, issued_at, expires_at, domain=None):
    """Move a staged receipt.json's validity window and re-seal it (D-092(c)).

    `issuedAt` and `expiresAt` sit inside the §5.4 struct the signature covers, so
    the receipt is re-signed with the published signer key afterwards; nothing else
    in the bundle copies the window (measured: the two timestamps occur only in
    receipt.json), so no other hash moves. ORDER MATTERS beside an override: §5.5's
    `reviewReceiptHash` is the receipt's hashStruct, which this changes, so call
    this BEFORE `_add_owner_override`, never after.
    """
    domain = read_json(SAMPLES, "domain.json") if domain is None else domain
    doc = read_json(target, "receipt.json")
    doc["receipt"]["issuedAt"] = str(int(issued_at))     # §5.4 uint64, canonical decimal
    doc["receipt"]["expiresAt"] = str(int(expires_at))
    write_json(os.path.join(target, "receipt.json"), doc)
    return reseal(target, domain)


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

    def test_cli_exit_code_over_the_shipped_corpus_is_3_not_0(self):
        # Was `test_cli_exit_code_zero`, asserting 0, from D-010 until D-090(a) made
        # that assertion the defect: four of the seven bundles are BLOCK receipts, so
        # a run over the corpus that exits 0 is a run whose exit status lies to a
        # script about a verdict the Vault refuses. The corpus is still authentic end
        # to end -- TestExitContractD090 pins the 7/7 count and the per-bundle words
        # -- and exit 0 over a corpus of ALLOW / overridden-REVIEW bundles is pinned
        # there too, so this is not "non-zero is fine".
        with open(os.devnull, "w") as devnull:
            saved, sys.stdout = sys.stdout, devnull
            try:
                self.assertEqual(
                    verify.main(["--domain", os.path.join(SAMPLES, "domain.json"),
                                 "--all", SAMPLES]), EXIT_NOT_EXECUTABLE)
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
            "address principal,address signer,address vault,uint256 chainId,address target,"
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
            "0x97f2389190b7b01c7bf3d315356436d6c1a02caa9d9890de99e31f100ff3238e",
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
        spec = os.path.join(REPO, "Sentinel_Lab_Proposal_v0_2.md")
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
                if name == "MandatePayload":
                    # The ratified v0.2 proposal is immutable historical evidence. The
                    # publication release is additive v0.3 and inserts `address signer`;
                    # it must therefore differ here rather than silently rewriting v0.2.
                    self.assertNotEqual(pub[name], mine)
                    release_doc = os.path.join(REPO, "docs", "enforcement-release-v0.3.md")
                    with open(release_doc, encoding="utf-8") as handle:
                        self.assertIn(mine, handle.read())
                else:
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
        spec = os.path.join(REPO, "Sentinel_Lab_Proposal_v0_2.md")
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

    def test_a_nonempty_corpus_still_verifies_and_is_not_reported_as_empty(self):
        # THE CONTROL John asked to preserve. Without it, "always fail" satisfies
        # every assertion below. Its JOB is unchanged: a real corpus must be
        # distinguishable from an empty one by exit status and by the count line.
        # Its VALUE changed at D-090(a): the corpus carries four BLOCK receipts, so
        # the aggregate is 3 (authentic, not executable), not 0 -- and 3 is neither
        # of the two "nothing was verified" codes this class exists to pin. The
        # rest of the D-090(a) contract is in TestExitContractD090.
        rc, out = self._run(SAMPLES)
        self.assertEqual(rc, EXIT_NOT_EXECUTABLE, out)
        self.assertNotIn(rc, (1, 2))
        self.assertIn("7/7 sample(s) verified", out)
        self.assertNotIn("NO BUNDLE DIRECTORIES FOUND", out)

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

    def test_the_cli_exits_3_on_a_signed_refusal_not_0(self):
        # Was `test_the_cli_exits_zero_on_a_signed_refusal`, asserting 0, until
        # D-091(a) made that assertion the defect: a signed refusal is AUTHENTIC and
        # there is nothing in it for SentinelVault to execute, so it takes the same
        # word and exit status as a BLOCK receipt (D-090(a)). This bundle uses the
        # `refusal.json` envelope, which the corpus sample does not, so the
        # classification is pinned on both shapes (TestExitContractD091 has the other).
        target = self.stage_refusal()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = verify.main(["--domain", trust_root(target), target])
        out = _strip_ansi(buf.getvalue())
        self.assertEqual(rc, EXIT_NOT_EXECUTABLE, out[-1500:])
        self.assertNotIn("=> PASS", out)
        self.assertIn(f"=> {NOT_EXECUTABLE_WORD}", out)
        self.assertIn("1/1 sample(s) verified", out)

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


# ---------------------------------------------------------------------------
# D-090(a): the recipient-facing exit contract
# ---------------------------------------------------------------------------

# THE WORD. D-090(a) requires "a distinct word" for a receipt that is authentic and
# that the Vault will not execute; the ruling leaves the word open, and this file
# pins it so that the implementer, the README lane and any script that greps the
# headline agree on one string. It contains AUTHENTIC because the claim `verify.py`
# makes is unchanged (D-087(c), D-088); it contains neither PASS nor FAIL because
# those are the two words a script already reads.
NOT_EXECUTABLE_WORD = "AUTHENTIC, NOT EXECUTABLE"

# THE EXIT CODES. 0 and 1 are the codes `verify.py` has always had; 2 is the code it
# already reserves for "nothing was verified" (H-8, D-056(a)). 3 is chosen for
# "authentic, not executable" to parallel verify_publication.py's three-state
# contract, where 3 is "NOT CERTIFIED, and not a refusal either ... treating 3 as
# either a pass or a failure misreads it". That sentence is exactly the property
# D-090(a) wants here: a script that treats this state as a pass submits a receipt
# the Vault refuses (the Adversary's finding), and a script that treats it as a
# failure says the signature did not hold, which is false. The two verifiers ship
# side by side, so a caller who learns one code table has learned the other.
EXIT_PASS = 0
EXIT_REFUSED = 1
EXIT_NOTHING_VERIFIED = 2
EXIT_NOT_EXECUTABLE = 3


def _strip_ansi(text):
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def _headline_blocks(out):
    """Every `=> ...` headline with its continuation lines, up to the next blank line.

    `run()` prints one headline per sample after the check list; a continuation
    line is indented and belongs to the headline above it. Returned stripped of
    colour and leading whitespace so the assertions read the words, not the layout.
    """
    blocks, current = [], None
    for line in _strip_ansi(out).splitlines():
        stripped = line.strip()
        if stripped.startswith("=>"):
            current = [stripped]
            blocks.append(current)
        elif current is not None:
            if stripped:
                current.append(stripped)
            else:
                current = None
    return ["\n".join(b) for b in blocks]


class TestExitContractD090(unittest.TestCase):
    """D-090(a), written before any implementer touched verify.py (D-058(1)).

    THE DEFECT, sustained by the Crucible Adversary at Cycle 2: `verify.py` printed
    `=> PASS: AUTHENTIC` and `1/1 sample(s) verified as AUTHENTIC`, exit 0, for a
    BLOCK receipt and for a REVIEW receipt with no override -- verdicts SentinelVault
    refuses at both entry points and verify_publication.py refuses. The disclosure
    printed beside it does not repair that: "disclaimers do not make those predicates
    equivalent", and `gpg --verify`'s exit 0 is explicitly not the script-facing
    claim, which is why `gpgv` exists.

    THE RULED CONTRACT. `verify.py` keeps certifying AUTHENTICITY -- D-088's exemption
    from `operation == CALL` stands, there is still no clock and no window check --
    but it no longer emits a recipient-facing PASS or exit 0 for a BLOCK receipt or an
    un-overridden REVIEW receipt. ALLOW, and REVIEW with a valid owner override, keep
    PASS / exit 0. Refusals keep FAIL / exit 1.

    WHERE THE CLASSIFICATION LIVES. `verify_sample()` returns `(ok, checks)` and `ok`
    is authenticity: every in-process test in this file consumes it that way, and so
    does the tamper self-test, whose "correctly still verified" on a BLOCK sample
    under `reasons-reorder` would become WRONGLY REJECTED if `ok` started meaning
    executability. So `ok` stays authenticity (pinned below), and the word and the
    exit code are the reporting layer's -- `run()` and `main()` -- which is the
    surface the Adversary struck.

    THE AGGREGATE. `--all` and a multi-bundle positional run are one invocation
    shape each, and this file has twice found a repair that closed the single-bundle
    path and left the other open (H-8; A-058's `--all` branch). The rule is the same
    for both: 1 if any bundle was refused, else 3 if any bundle is authentic-not-
    executable, else 0. The shipped corpus carries four such bundles by design, so
    `--all fixtures/samples` exits 3 -- and the gate's D-010 stage, which today
    treats any non-zero status as a failure, must learn that (see the report that
    accompanies this class; scripts/test.sh is not this file's to edit).

    D-091(a) (2026-09-02) EXTENDED THIS CONTRACT to the §5.5.1 refusal record, which
    this class had left on the PASS side: "Refusals keep FAIL / exit 1" above means
    REFUSED bundles -- a check that did not hold -- not a signed refusal record, which
    is authentic and carries nothing to execute. The corpus therefore lists FIVE
    NOT EXECUTABLE bundles, not four; the aggregate test below was rewritten to say
    so, and TestExitContractD091 pins the refusal record's own contract.

    D-092(c) (2026-09-02) AMENDED "there is still no clock and no window check"
    above: verify.py now compares the receipt's window (and the override's) to the
    HOST clock and reports an authentic bundle outside it as NOT EXECUTABLE, exit 3.
    Every shipped receipt fixture expired on 2026-08-29, so the positive controls in
    this class -- the ALLOW and overridden-REVIEW PASS / exit 0 cases -- could no
    longer read PASS off the corpus. They were rewritten to MINT a live bundle
    (`live_window`, `rewindow`) and the corpus aggregate below now counts SEVEN
    NOT EXECUTABLE and zero PASS. TestExitContractD092 pins the window contract
    itself; the tests here keep pinning the verdict/override contract, on live bundles.
    """

    BLOCK_SAMPLE = os.path.join(SAMPLES, "case-2-injection-block")
    ALLOW_SAMPLE = os.path.join(SAMPLES, "case-1-allow")
    DOMAIN = os.path.join(SAMPLES, "domain.json")

    # -- helpers -----------------------------------------------------------------

    def _cli(self, *args):
        """verify.main() in-process, stdout and stderr captured. Returns (rc, text)."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = verify.main(list(args))
        return rc, _strip_ansi(buf.getvalue())

    def _proc(self, *args):
        """The process exit status a script actually reads."""
        proc = subprocess.run(
            [sys.executable, os.path.join(REPO, "verifier", "verify.py"), *args],
            capture_output=True, text=True)
        return proc.returncode, _strip_ansi(proc.stdout + proc.stderr)

    def _tmp(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        return tmp

    def _staged(self, sample):
        """A copy of a shipped sample under a fresh parent, domain.json beside it."""
        return stage(os.path.join(SAMPLES, sample), self._tmp())

    def _staged_with_verdict(self, verdict_num, verdict_name, source="case-1-allow"):
        """`source` re-labelled to `verdict_name` and made wholly self-consistent.

        The directory keeps the source's NAME, so a classifier reading the label off
        the path rather than the signed receipt is caught. evidence.verdict, the
        receipt's verdict enum and meta.json's label all move together, the evidence
        is re-canonicalised and re-hashed, and the receipt is re-signed with the
        published signer key -- the same steps as TestEvidenceDescribesTheBundle's
        harness, so every hash and signature check passes and only the verdict
        differs from the shipped ALLOW.
        """
        target = self._staged(source)
        ev = read_json(target, "evidence.json")
        ev["verdict"] = verdict_name
        with open(os.path.join(target, "evidence.json"), "w") as h:
            json.dump(ev, h)
        canon = jcs.canonicalize(ev)
        with open(os.path.join(target, "evidence.canonical.json"), "wb") as h:
            h.write(canon)
        digest = "0x" + keccak256(canon).hex()
        with open(os.path.join(target, "evidence.hash"), "w") as h:
            h.write(digest + "\n")
        meta = read_json(target, "meta.json")
        meta["verdict"] = verdict_name
        write_json(os.path.join(target, "meta.json"), meta)
        doc = read_json(target, "receipt.json")
        doc["receipt"]["evidenceHash"] = digest
        doc["receipt"]["verdict"] = str(verdict_num)   # §5.4 uint8, canonical decimal string
        doc["signature"] = sign_digest(
            eip712.receipt_digest(read_json(SAMPLES, "domain.json"), doc["receipt"]),
            SIGNER_KEY)
        write_json(os.path.join(target, "receipt.json"), doc)
        return target

    def _add_owner_override(self, target):
        """A §5.5 override for `target`'s receipt, signed by the mandate principal.

        Derived from the shipped override rather than hand-built, for the reason
        TestVerifierPropertiesNotCorpusProperties gives: a hand-built payload can
        fail to hash for reasons that have nothing to do with the property under
        test.
        """
        body = read_json(target, "receipt.json")["receipt"]
        template = read_json(OVERRIDE_SAMPLE, "override.json")["override"]
        override = dict(template)
        override["reviewReceiptHash"] = "0x" + eip712.receipt_struct_hash(body).hex()
        for field in ("actionHash", "mandateHash", "policyHash"):
            override[field] = body[field]
        override["actionNonce"] = str(read_json(target, "action.json")["actionNonce"])
        domain = read_json(SAMPLES, "domain.json")
        key = verify._OWNER_TEST_KEY
        write_json(os.path.join(target, "override.json"), {
            "override": override,
            "ownerSignature": sign_digest(eip712.override_digest(domain, override), key),
            "ownerAddress": public_key_to_address(point_mul(key, G)),
        })

    @staticmethod
    def _corrupt_hex(value):
        # Flip one nibble inside the s component. r stays a curve point and s stays
        # low, so the signature is well-formed and recovers to the WRONG address: the
        # refusal comes from the recovery check itself, not from a shape check
        # noticing a malformed signature (A-056: a mutation caught by a different
        # check than the one it targets is worth nothing).
        i = 2 + 64 + 24
        return value[:i] + ("0" if value[i] != "0" else "1") + value[i + 1:]

    def _corrupt_receipt_signature(self, target):
        doc = read_json(target, "receipt.json")
        doc["signature"] = self._corrupt_hex(doc["signature"])
        write_json(os.path.join(target, "receipt.json"), doc)

    def _corrupt_override_signature(self, target):
        doc = read_json(target, "override.json")
        doc["ownerSignature"] = self._corrupt_hex(doc["ownerSignature"])
        write_json(os.path.join(target, "override.json"), doc)

    def _assert_not_executable(self, rc, out, verdict_word, extra_words=()):
        """The whole of the new contract, for one bundle."""
        self.assertEqual(rc, EXIT_NOT_EXECUTABLE,
                         f"an authentic {verdict_word} receipt must exit "
                         f"{EXIT_NOT_EXECUTABLE}, got {rc}")
        blocks = _headline_blocks(out)
        self.assertEqual(len(blocks), 1, f"expected one headline, got {blocks!r}")
        head = blocks[0]
        self.assertTrue(head.startswith(f"=> {NOT_EXECUTABLE_WORD}"),
                        f"the headline word must be {NOT_EXECUTABLE_WORD!r}; got {head!r}")
        self.assertNotIn("PASS", head.splitlines()[0],
                         "the recipient-facing word must not contain PASS")
        self.assertNotIn("FAIL", head.splitlines()[0],
                         "an authentic bundle is not a refusal; the word must not say FAIL")
        self.assertIn("AUTHENTIC", head, "the output must still state the bundle is authentic")
        for word in (verdict_word,) + tuple(extra_words):
            self.assertIn(word, head, f"the headline must name {word!r}: {head!r}")
        self.assertNotIn("=> PASS", out, "no `=> PASS` anywhere in the run")
        self.assertNotIn("=> FAIL", out, "no `=> FAIL` anywhere in the run")
        # The count line is the authentic count -- the bundle IS authentic -- and the
        # text after it must carry the state, so `tail -1` does not read "1/1 verified".
        self.assertIn("1/1 sample(s) verified", out)
        after_summary = out[out.index("1/1 sample(s) verified"):]
        self.assertIn("NOT EXECUTABLE", after_summary,
                      "the summary must say the bundle is not executable")

    def _assert_pass(self, rc, out):
        self.assertEqual(rc, EXIT_PASS, out)
        blocks = _headline_blocks(out)
        self.assertEqual(len(blocks), 1, blocks)
        self.assertTrue(blocks[0].startswith("=> PASS: AUTHENTIC"), blocks[0])
        self.assertNotIn(NOT_EXECUTABLE_WORD, out)
        self.assertNotIn("NOT EXECUTABLE", out)
        self.assertIn("1/1 sample(s) verified", out)

    def _assert_refused(self, rc, out):
        self.assertEqual(rc, EXIT_REFUSED, out)
        blocks = _headline_blocks(out)
        self.assertEqual(len(blocks), 1, blocks)
        self.assertTrue(blocks[0].startswith("=> FAIL"), blocks[0])
        self.assertNotIn(NOT_EXECUTABLE_WORD, out,
                         "a refusal must not be reported as authentic-not-executable")
        self.assertIn("0/1 sample(s) verified", out)
        self.assertIn("FAILED:", out)

    # -- 1. BLOCK -----------------------------------------------------------------

    def test_every_shipped_BLOCK_fixture_is_AUTHENTIC_NOT_EXECUTABLE_and_exits_3(self):
        index = expected_verdicts()
        blocks = [d for d in sample_dirs() if index[os.path.basename(d)]["verdict"] == "BLOCK"]
        self.assertEqual(len(blocks), 4, "the corpus ships four BLOCK receipts")
        for path in blocks:
            with self.subTest(sample=os.path.basename(path)):
                rc, out = self._cli("--domain", self.DOMAIN, path)
                self._assert_not_executable(rc, out, "BLOCK")

    def test_the_process_exit_status_a_script_reads_is_3_for_the_shipped_BLOCK_receipt(self):
        # Through the interpreter, not `main()`: this is the status the Adversary
        # quoted and the one `sys.exit(main())` has to deliver.
        rc, out = self._proc("--domain", self.DOMAIN, self.BLOCK_SAMPLE)
        self._assert_not_executable(rc, out, "BLOCK")

    def test_a_staged_BLOCK_built_from_the_ALLOW_bundle_is_classified_by_its_signed_verdict(self):
        # Same bytes as case-1-allow, same directory NAME as case-1-allow; only the
        # signed verdict, the evidence's copy of it and the case label say BLOCK.
        target = self._staged_with_verdict(0, "BLOCK")
        ok, checks = _verify(target)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])   # the control
        rc, out = self._cli("--domain", trust_root(target), target)
        self._assert_not_executable(rc, out, "BLOCK")

    def test_a_resealed_copy_of_a_shipped_BLOCK_fixture_gets_the_same_contract(self):
        target = self._staged("case-2-injection-block")
        reseal(target, read_json(SAMPLES, "domain.json"))
        rc, out = self._cli("--domain", trust_root(target), target)
        self._assert_not_executable(rc, out, "BLOCK")

    # -- 2. REVIEW with no override -------------------------------------------------

    def test_the_shipped_REVIEW_fixture_with_its_override_removed_is_NOT_EXECUTABLE_exit_3(self):
        target = self._staged("case-4-review-failmode-review")
        os.remove(os.path.join(target, "override.json"))
        ok, checks = _verify(target)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])   # authentic without it
        rc, out = self._cli("--domain", trust_root(target), target)
        # The cure is an owner override, so the headline names it (R-A018-16(c)).
        self._assert_not_executable(rc, out, "REVIEW", extra_words=("override",))

    def test_a_staged_REVIEW_built_from_ALLOW_is_exit_3_without_an_override_and_exit_0_with_one(self):
        # THE PAIR THAT ISOLATES THE OVERRIDE: one bundle, one file added, and the
        # exit status moves from 3 to 0. Nothing else about the bundle changes.
        target = self._staged_with_verdict(1, "REVIEW")
        # D-092(c): the source fixture is expired, so the window is moved to contain
        # now BEFORE the override is derived (the override binds the receipt's
        # hashStruct). With that done, the override is again the only thing that moves.
        rewindow(target, *live_window())
        rc, out = self._cli("--domain", trust_root(target), target)
        self._assert_not_executable(rc, out, "REVIEW", extra_words=("override",))
        self._add_owner_override(target)
        rc, out = self._cli("--domain", trust_root(target), target)
        self._assert_pass(rc, out)

    # -- 3 and 4. the positive controls ---------------------------------------------
    # Rewritten under D-092(c): the shipped ALLOW and overridden-REVIEW fixtures are
    # expired and now exit 3 (pinned in TestExitContractD092), so PASS is read off a
    # bundle minted live. The shipped override's own window (0 .. 4000000000) is
    # live; only the receipt's had closed.

    def test_a_REVIEW_receipt_with_a_valid_owner_override_keeps_PASS_and_exit_0(self):
        target = self._staged_with_verdict(1, "REVIEW")
        rewindow(target, *live_window())
        self._add_owner_override(target)
        rc, out = self._cli("--domain", trust_root(target), target)
        self._assert_pass(rc, out)
        self.assertIn("override targets a REVIEW receipt", out,
                      "the override checks must have run for this PASS to mean anything")

    def test_an_ALLOW_receipt_keeps_PASS_and_exit_0(self):
        target = self._staged("case-1-allow")
        rewindow(target, *live_window())
        rc, out = self._cli("--domain", trust_root(target), target)
        self._assert_pass(rc, out)
        rc, out = self._proc("--domain", trust_root(target), target)
        self._assert_pass(rc, out)

    # -- 5. refusals stay FAIL / 1 --------------------------------------------------

    def test_a_tampered_signature_on_a_BLOCK_receipt_is_a_refusal_exit_1_not_3(self):
        # PRECEDENCE. A BLOCK receipt whose signature does not recover is not an
        # authentic-not-executable receipt; it is not authentic. 1 must win over 3,
        # or the new code becomes a place for a forged BLOCK to hide.
        target = self._staged("case-2-injection-block")
        self._corrupt_receipt_signature(target)
        rc, out = self._cli("--domain", trust_root(target), target)
        self._assert_refused(rc, out)
        self.assertIn("[FAIL] recovered signer == receipt.signer", out)

    def test_a_tampered_signature_on_an_ALLOW_receipt_is_still_exit_1(self):
        target = self._staged("case-1-allow")
        self._corrupt_receipt_signature(target)
        rc, out = self._cli("--domain", trust_root(target), target)
        self._assert_refused(rc, out)

    def test_a_REVIEW_whose_override_does_not_recover_is_a_refusal_exit_1_not_3(self):
        # "REVIEW with no override" is state 3; "REVIEW with a bad override" is a
        # refusal. They must not share a code: the first is cured by asking the
        # owner, the second is a credential that did not authenticate.
        target = self._staged("case-4-review-failmode-review")
        self._corrupt_override_signature(target)
        rc, out = self._cli("--domain", trust_root(target), target)
        self._assert_refused(rc, out)
        self.assertIn("[FAIL] override signature recovers ownerAddress", out)

    def test_the_four_states_are_distinguishable_by_exit_status_alone(self):
        # A script reads nothing else. Each state through the interpreter, output
        # deliberately ignored, and the four codes must be pairwise distinct.
        tampered = self._staged("case-1-allow")
        self._corrupt_receipt_signature(tampered)
        live = self._staged("case-1-allow")          # D-092(c): the shipped one is expired
        rewindow(live, *live_window())
        empty = self._tmp()
        codes = {
            "ALLOW": self._proc("--domain", trust_root(live), live)[0],
            "BLOCK": self._proc("--domain", self.DOMAIN, self.BLOCK_SAMPLE)[0],
            "tampered": self._proc("--domain", trust_root(tampered), tampered)[0],
            "nothing verified": self._proc("--domain", self.DOMAIN, "--all", empty)[0],
        }
        self.assertEqual(codes, {"ALLOW": EXIT_PASS, "BLOCK": EXIT_NOT_EXECUTABLE,
                                 "tampered": EXIT_REFUSED,
                                 "nothing verified": EXIT_NOTHING_VERIFIED})
        self.assertEqual(len(set(codes.values())), 4, codes)

    # -- the API pin ---------------------------------------------------------------

    def test_verify_sample_still_answers_authenticity_for_a_BLOCK_receipt(self):
        # The library call is what every in-process test here consumes, and what the
        # tamper self-test's "correctly still verified" reads. A BLOCK receipt is
        # authentic, so `ok` is True; the reporting layer owns the word and the code.
        ok, checks = _verify(self.BLOCK_SAMPLE)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])
        self.assertFalse(any("EXECUTABLE" in c.name.upper() for c in checks),
                         "no check named for executability may join the authenticity list "
                         "(D-088: verify.py carries no executability condition)")

    def test_the_tamper_self_test_on_a_BLOCK_sample_is_untouched(self):
        # The gate's second arm. `--tamper` replaces the PASS/FAIL headline with the
        # self-test verdict, and a BLOCK sample under `reasons-reorder` must still be
        # "correctly still verified". If the classification were pushed below the
        # tamper branch this exits non-zero and the gate's tamper floor breaks.
        rc, out = self._cli("--domain", self.DOMAIN, "--tamper", "all", self.BLOCK_SAMPLE)
        self.assertEqual(rc, EXIT_PASS, out)
        # D-092(e) rewrote the summary sentence (TestExitContractD092 pins its counts);
        # what this test keeps is that the run summarises 1/1 and never says NOT EXECUTABLE.
        self.assertRegex(out, r"(?m)^1/1 sample\(s\) ")
        self.assertNotIn(NOT_EXECUTABLE_WORD, out)

    # -- 6. the aggregate ------------------------------------------------------------

    # D-091(a): the §5.5.1 refusal record moved from the PASSING list to this one. It
    # was the seventh "PASS" until John ruled it reports as a BLOCK receipt does.
    # D-092(c): the last two moved too -- the ALLOW and the overridden REVIEW are
    # authentic and EXPIRED, and the corpus now carries nothing that PASSES. The
    # positive control for the aggregate is minted live, below.
    NOT_EXECUTABLE_IN_CORPUS = ("case-2-injection-block", "case-3-wrong-purpose-block",
                                "case-4-blocked-failmode-failclosed", "edge-single-reason-code",
                                "refusal-vault-paused",
                                "case-1-allow", "case-4-review-failmode-review")
    PASSING_IN_CORPUS = ()

    def _lines_naming(self, out, needle):
        return [l for l in out.splitlines() if needle in l]

    def test_all_over_the_shipped_corpus_exits_3_and_still_counts_7_of_7_authentic(self):
        # WHAT THE GATE RUNS, verbatim: scripts/test.sh's D-010 stage. Four of the
        # seven bundles are BLOCK by design, a fifth is a §5.5.1 refusal record
        # (D-091(a)), and the remaining two expired on 2026-08-29 (D-092(c)); none is
        # refused, so the aggregate is 3. The count line keeps the `N/M sample(s)
        # verified` form -- the gate's sed reads it against VERIFIER_MIN_SAMPLES --
        # and N is the AUTHENTIC count, because that is the claim the phrase makes
        # and all seven are authentic.
        rc, out = self._proc("--domain", self.DOMAIN, "--all", SAMPLES)
        self.assertEqual(rc, EXIT_NOT_EXECUTABLE, out[-2000:])
        self.assertRegex(out, r"(?m)^7/7 sample\(s\) verified")
        self.assertNotIn("FAILED:", out, "nothing in the corpus is refused")
        self.assertNotIn("=> FAIL", out)
        summary_at = out.index("7/7 sample(s) verified")
        after = out[summary_at:]
        self.assertEqual(len(self.NOT_EXECUTABLE_IN_CORPUS), 7)
        for name in self.NOT_EXECUTABLE_IN_CORPUS:
            path = os.path.join(SAMPLES, name)
            named = self._lines_naming(after, path)
            self.assertTrue(named and all("NOT EXECUTABLE" in l for l in named),
                            f"{name} must be listed after the summary as NOT EXECUTABLE, "
                            f"as a refused bundle is listed as FAILED; got {named!r}")
        for name in self.PASSING_IN_CORPUS:
            path = os.path.join(SAMPLES, name)
            self.assertFalse(self._lines_naming(after, path),
                             f"{name} PASSES and must not be listed after the summary")
        heads = _headline_blocks(out)
        self.assertEqual(len(heads), 7)
        # 4 -> 5 at D-091(a) (the refusal record), 5 -> 7 at D-092(c) (the two expired).
        self.assertEqual(sum(h.startswith(f"=> {NOT_EXECUTABLE_WORD}") for h in heads), 7)
        self.assertEqual(sum(h.startswith("=> PASS: AUTHENTIC") for h in heads), 0)
        self.assertNotIn("=> PASS", out, "nothing in the shipped corpus PASSES any more")

    def test_all_over_a_corpus_of_executable_shaped_bundles_exits_0(self):
        # The control for the test above: a corpus of live ALLOW and overridden-REVIEW
        # bundles is a plain PASS. Without this, "always 3" satisfies the shipped-corpus
        # test. Minted, not copied (D-092(c)): a copy of the shipped pair is expired.
        tmp = self._tmp()
        allow = stage(self.ALLOW_SAMPLE, tmp)
        rewindow(allow, *live_window())
        review = self._staged_with_verdict(1, "REVIEW")
        rewindow(review, *live_window())
        self._add_owner_override(review)
        shutil.move(review, os.path.join(tmp, "case-4-review-minted-live"))
        rc, out = self._proc("--domain", os.path.join(tmp, "domain.json"), "--all", tmp)
        self.assertEqual(rc, EXIT_PASS, out[-2000:])
        self.assertRegex(out, r"(?m)^2/2 sample\(s\) verified")
        self.assertNotIn("NOT EXECUTABLE", out)
        self.assertEqual(sum(h.startswith("=> PASS: AUTHENTIC") for h in _headline_blocks(out)), 2)

    def test_all_with_one_refused_bundle_exits_1_whatever_else_is_there(self):
        # 1 beats 3 beats 0 in the aggregate as in the single case: a corpus with a
        # forged receipt in it is refused, and the forged one is named as FAILED.
        tmp = self._tmp()
        for name in ("case-1-allow", "case-2-injection-block", "case-3-wrong-purpose-block"):
            shutil.copytree(os.path.join(SAMPLES, name), os.path.join(tmp, name))
        forged = os.path.join(tmp, "case-2-injection-block")
        self._corrupt_receipt_signature(forged)
        rc, out = self._proc("--domain", self.DOMAIN, "--all", tmp)
        self.assertEqual(rc, EXIT_REFUSED, out[-2000:])
        self.assertRegex(out, r"(?m)^2/3 sample\(s\) verified")
        self.assertTrue(any("FAILED" in l for l in self._lines_naming(out, forged)),
                        "the forged bundle must be listed as FAILED")

    def test_several_positional_bundles_follow_the_same_aggregate_rule_as_all(self):
        # `verify.py a b` is the other multi-bundle shape, and the one a first draft
        # of the `--all` rule would miss. The ALLOW is minted live (D-092(c)): with the
        # shipped, expired one both bundles would be 3 on their own and "3 beats 0"
        # would be measured by nothing.
        live = self._staged("case-1-allow")
        rewindow(live, *live_window())
        rc, out = self._cli("--domain", self.DOMAIN, live, self.BLOCK_SAMPLE)
        self.assertEqual(rc, EXIT_NOT_EXECUTABLE, out[-1500:])
        self.assertIn("2/2 sample(s) verified", out)
        self.assertEqual(sum(h.startswith("=> PASS: AUTHENTIC") for h in _headline_blocks(out)), 1)
        forged = self._staged("case-1-allow")
        self._corrupt_receipt_signature(forged)
        rc, out = self._cli("--domain", self.DOMAIN, self.BLOCK_SAMPLE, forged)
        self.assertEqual(rc, EXIT_REFUSED, out[-1500:])
        self.assertIn("1/2 sample(s) verified", out)


class TestExitContractD091(unittest.TestCase):
    """D-091(a), written before any implementer touched verify.py (D-058(1)).

    THE GAP D-090(a) LEFT. `verify.py` printed `=> PASS: AUTHENTIC` and exited 0 on
    `fixtures/samples/refusal-vault-paused`, measured at 0bc79a8 on 2026-09-02. A
    §5.5.1 SignedRefusalRecord is a signed refusal TO ISSUE a receipt: it is
    authentic -- digest, signature, signer identity and every binding hold against
    the named trust root -- and there is nothing in it for SentinelVault to execute,
    which is why verify_publication.py refuses it (D-087(d)). That is exactly the
    shape D-090(a) took the PASS word away from: a bundle that is genuinely the
    signer's and that the Vault will not run. The refusal record was left on the
    PASS side of that ruling only because it carries no verdict for `_not_executable`
    to read.

    THE RULED CONTRACT. An authentic refusal record reports the way an authentic
    BLOCK receipt does: headline `=> AUTHENTIC, NOT EXECUTABLE: ...`, exit status 3,
    `NOT EXECUTABLE: <path>` after the summary, and the summary counting it as
    AUTHENTIC. The headline must say what the bundle IS -- a §5.5.1 refusal record --
    and not borrow the BLOCK sentence: a refusal record has no signed verdict, so
    "the signed verdict is BLOCK" would be a false diagnostic of the H-5 kind. The
    exact wording is the implementer's; this class pins the prefix and the two words
    `refusal` and `§5.5.1`.

    WHAT DOES NOT MOVE. `verify_sample()` still answers authenticity (D-090(a)'s
    API pin, re-pinned here for the refusal record). A tampered refusal record is a
    refusal, `=> FAIL` / exit 1 -- 1 beats 3 beats 0, single bundle and aggregate
    alike. A refusal record with an `override.json` beside it is already refused
    (D-052(b): an unexamined §5.5 credential riding with a refusal) and stays
    refused; it must not become NOT EXECUTABLE, because a refused bundle is not an
    authentic one. The `--tamper` self-test is untouched: `refusal-*` modes are
    "correctly rejected", the receipt-only modes are N/A, and the run exits 0.

    THE AGGREGATE. `--all fixtures/samples` now lists FIVE bundles as NOT EXECUTABLE
    -- the four BLOCK receipts and the refusal record -- and still exits 3 with
    `7/7 sample(s) verified as AUTHENTIC`. TestExitContractD090's corpus test was
    rewritten to five; this class pins the refusal record's line by name, and the
    two multi-bundle shapes (positional and `--all`) each with the refusal record in
    them, because this file has twice found a repair that closed one invocation
    shape and left the other open.
    """

    REFUSAL_SAMPLE = os.path.join(SAMPLES, "refusal-vault-paused")
    ALLOW_SAMPLE = os.path.join(SAMPLES, "case-1-allow")
    BLOCK_SAMPLE = os.path.join(SAMPLES, "case-2-injection-block")
    DOMAIN = os.path.join(SAMPLES, "domain.json")

    # The check a corrupted refusal signature must fail on, verbatim from verify.py.
    # Named so that the refusal comes from the recovery check itself (A-056), not
    # from a shape check noticing a malformed signature.
    REFUSAL_RECOVERY_CHECK = "the signature recovers the record's declared signer"
    # D-052(b)'s check, verbatim, for the stray-override case.
    REFUSAL_OVERRIDE_CHECK = "a §5.5.1 refusal bundle carries no §5.5 owner override"

    # -- helpers (the D-090 class's, by reference, so the two classes cannot drift) --

    _cli = TestExitContractD090._cli
    _proc = TestExitContractD090._proc
    _tmp = TestExitContractD090._tmp
    _staged = TestExitContractD090._staged
    _corrupt_hex = staticmethod(TestExitContractD090._corrupt_hex)
    _corrupt_receipt_signature = TestExitContractD090._corrupt_receipt_signature
    _lines_naming = TestExitContractD090._lines_naming

    def _corrupt_refusal_signature(self, target):
        # The corpus envelope: receipt.json -> refusalRecord -> {record, signature,
        # reasonCodes}. Same nibble-flip as the receipt case: well-formed, low-s,
        # recovers to the WRONG address.
        doc = read_json(target, "receipt.json")
        envelope = doc["refusalRecord"]
        envelope["signature"] = self._corrupt_hex(envelope["signature"])
        write_json(os.path.join(target, "receipt.json"), doc)

    def _assert_refusal_not_executable(self, rc, out, count="1/1"):
        """The whole of the D-091(a) contract for one refusal record."""
        self.assertEqual(rc, EXIT_NOT_EXECUTABLE,
                         f"an authentic §5.5.1 refusal record must exit "
                         f"{EXIT_NOT_EXECUTABLE}, got {rc}")
        blocks = _headline_blocks(out)
        self.assertEqual(len(blocks), 1, f"expected one headline, got {blocks!r}")
        head = blocks[0]
        first = head.splitlines()[0]
        self.assertTrue(head.startswith(f"=> {NOT_EXECUTABLE_WORD}"),
                        f"the headline word must be {NOT_EXECUTABLE_WORD!r}; got {head!r}")
        self.assertNotIn("PASS", first, "the recipient-facing word must not contain PASS")
        self.assertNotIn("FAIL", first,
                         "an authentic refusal record is not a refused bundle; no FAIL")
        self.assertIn("AUTHENTIC", head, "the output must still state the record is authentic")
        # What it IS. The implementer words the reason; it must name the artifact.
        # "refusal record", not the bare word: the D-090(a) continuation line already
        # says "neither a certification nor a refusal", so "refusal" alone is vacuous.
        self.assertIn("refusal record", head.lower(),
                      f"the headline must say this is a refusal record: {head!r}")
        self.assertIn("§5.5.1", head,
                      f"the headline must cite §5.5.1, as the BLOCK headline cites §5.5: {head!r}")
        # What it is NOT. A refusal record carries no signed verdict, so the BLOCK
        # and REVIEW sentences from D-090(a) would be false diagnostics here (H-5).
        for borrowed in ("the signed verdict is BLOCK", "the signed verdict is REVIEW"):
            self.assertNotIn(borrowed, head,
                             "a refusal record must not be reported with a receipt's verdict")
        self.assertNotIn("=> PASS", out, "no `=> PASS` anywhere in the run")
        self.assertNotIn("=> FAIL", out, "no `=> FAIL` anywhere in the run")
        # The count line is the AUTHENTIC count -- the record IS authentic -- and the
        # text after it must carry the state, so `tail -1` does not read "verified".
        summary = f"{count} sample(s) verified"
        self.assertIn(summary, out)
        after_summary = out[out.index(summary):]
        self.assertIn("NOT EXECUTABLE", after_summary,
                      "the summary must say the record is not executable")
        self.assertNotIn("FAILED:", after_summary, "nothing here is refused")

    def _assert_refused(self, rc, out, count="0/1"):
        self.assertEqual(rc, EXIT_REFUSED, out[-1500:])
        blocks = _headline_blocks(out)
        self.assertEqual(len(blocks), 1, blocks)
        self.assertTrue(blocks[0].startswith("=> FAIL"), blocks[0])
        self.assertNotIn(NOT_EXECUTABLE_WORD, out,
                         "a refused bundle must not be reported as authentic-not-executable")
        self.assertNotIn("NOT EXECUTABLE", out)
        self.assertIn(f"{count} sample(s) verified", out)
        self.assertIn("FAILED:", out)

    # -- 1. the single refusal record --------------------------------------------------

    def test_every_shipped_refusal_record_is_AUTHENTIC_NOT_EXECUTABLE_and_exits_3(self):
        # THE DEFECT, measured: `=> PASS: AUTHENTIC`, exit 0, at 0bc79a8.
        dirs = refusal_sample_dirs()
        self.assertTrue(dirs, "§5.5.1 is untested by any artifact again")
        self.assertIn(self.REFUSAL_SAMPLE, dirs)
        for path in dirs:
            with self.subTest(sample=os.path.basename(path)):
                ok, checks = _verify(path)
                self.assertTrue(ok, [c.name for c in checks if not c.ok])   # the control
                rc, out = self._cli("--domain", self.DOMAIN, path)
                self._assert_refusal_not_executable(rc, out)
                self.assertTrue(
                    self._lines_naming(out[out.index("1/1 sample(s) verified"):], path),
                    "the NOT EXECUTABLE line after the summary must name the bundle's path")

    def test_the_process_exit_status_a_script_reads_is_3_for_the_shipped_refusal_record(self):
        # Through the interpreter, not `main()`: the status `sys.exit(main())` delivers.
        rc, out = self._proc("--domain", self.DOMAIN, self.REFUSAL_SAMPLE)
        self._assert_refusal_not_executable(rc, out)

    def test_a_staged_copy_of_the_refusal_record_under_another_parent_gets_the_same_contract(self):
        # Same bytes, fresh parent, the test asserting its own trust root: the
        # classification must read the bundle, not the corpus path.
        target = self._staged("refusal-vault-paused")
        rc, out = self._cli("--domain", trust_root(target), target)
        self._assert_refusal_not_executable(rc, out)

    def test_a_refusal_record_and_a_BLOCK_receipt_share_exit_3_and_the_headline_tells_them_apart(self):
        # The ruling puts both on 3. A script reads only the status, so the two are
        # deliberately NOT distinguishable there; a reader is, by the headline, which
        # names the artifact in each case and must not describe one as the other.
        rc_r, out_r = self._proc("--domain", self.DOMAIN, self.REFUSAL_SAMPLE)
        rc_b, out_b = self._proc("--domain", self.DOMAIN, self.BLOCK_SAMPLE)
        self.assertEqual((rc_r, rc_b), (EXIT_NOT_EXECUTABLE, EXIT_NOT_EXECUTABLE))
        head_r = _headline_blocks(out_r)[0]
        head_b = _headline_blocks(out_b)[0]
        self.assertIn("refusal record", head_r.lower())
        self.assertIn("§5.5.1", head_r)
        # The BLOCK headline says "neither a certification nor a refusal" already, so
        # the bare word cannot separate them; the artifact name and the section can.
        self.assertNotIn("refusal record", head_b.lower(),
                         "the BLOCK headline must not have been rewritten to describe a refusal record")
        self.assertNotIn("§5.5.1", head_b)
        self.assertIn("the signed verdict is BLOCK", head_b,
                      "the D-090(a) BLOCK headline is unchanged by D-091(a)")
        self.assertNotIn("the signed verdict is BLOCK", head_r)

    def test_run_classifies_the_refusal_record_as_authentic_and_not_executable(self):
        # The seam D-090(a) chose: run() returns (ok, checks, executable), with `ok`
        # still authenticity and `executable` the reporting layer's classification.
        # For a refusal record that is (True, ..., False).
        with contextlib.redirect_stdout(io.StringIO()):
            ok, checks, executable = verify.run(self.REFUSAL_SAMPLE, self.DOMAIN, quiet=True)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])
        self.assertFalse(executable, "run() must classify an authentic refusal record as "
                                     "not executable, as it does a BLOCK receipt")

    # -- 2. the aggregate --------------------------------------------------------------

    def test_all_over_the_shipped_corpus_lists_seven_NOT_EXECUTABLE_including_the_refusal_record(self):
        # WHAT THE GATE RUNS. Four BLOCK receipts plus the refusal record were five
        # lines at D-091(a); D-092(c) added the two expired receipts, so SEVEN lines,
        # exit 3, 7/7 authentic. README.md and scripts/test.sh say "five" today and
        # will need to say seven (reported, not edited, by this lane). Was
        # `..._lists_five_...` until D-092(c).
        rc, out = self._proc("--domain", self.DOMAIN, "--all", SAMPLES)
        self.assertEqual(rc, EXIT_NOT_EXECUTABLE, out[-2000:])
        self.assertRegex(out, r"(?m)^7/7 sample\(s\) verified")
        self.assertNotIn("FAILED:", out)
        after = out[out.index("7/7 sample(s) verified"):]
        listed = [l for l in after.splitlines() if l.strip().startswith("NOT EXECUTABLE:")]
        self.assertEqual(len(listed), 7, f"seven NOT EXECUTABLE lines, got {listed!r}")
        named = self._lines_naming(after, self.REFUSAL_SAMPLE)
        self.assertTrue(named and all("NOT EXECUTABLE" in l for l in named),
                        f"the refusal record must be listed as NOT EXECUTABLE; got {named!r}")
        heads = _headline_blocks(out)
        self.assertEqual(len(heads), 7)
        self.assertEqual(sum(h.startswith(f"=> {NOT_EXECUTABLE_WORD}") for h in heads), 7)
        self.assertEqual(sum(h.startswith("=> PASS: AUTHENTIC") for h in heads), 0)

    def test_all_over_a_corpus_of_only_the_refusal_record_exits_3(self):
        # The `--all` discovery path with nothing but the refusal record in it: the
        # classification must apply on this path as on the positional one.
        tmp = self._tmp()
        shutil.copytree(self.REFUSAL_SAMPLE, os.path.join(tmp, "refusal-vault-paused"))
        rc, out = self._proc("--domain", self.DOMAIN, "--all", tmp)
        self._assert_refusal_not_executable(rc, out)

    def test_the_refusal_record_beside_an_ALLOW_bundle_exits_3_in_either_order(self):
        # Positional multi-bundle: 3 beats 0, whichever bundle comes first, and only
        # the refusal record is listed after the summary. The ALLOW is minted live
        # (D-092(c)): the shipped one is expired and would be listed too.
        live = self._staged("case-1-allow")
        rewindow(live, *live_window())
        for order in ((self.REFUSAL_SAMPLE, live), (live, self.REFUSAL_SAMPLE)):
            with self.subTest(order=[os.path.basename(p) for p in order]):
                rc, out = self._cli("--domain", self.DOMAIN, *order)
                self.assertEqual(rc, EXIT_NOT_EXECUTABLE, out[-1500:])
                self.assertIn("2/2 sample(s) verified", out)
                after = out[out.index("2/2 sample(s) verified"):]
                self.assertTrue(self._lines_naming(after, self.REFUSAL_SAMPLE))
                self.assertFalse(self._lines_naming(after, live),
                                 "the live ALLOW bundle PASSES and is not listed after the summary")
                heads = _headline_blocks(out)
                self.assertEqual(sum(h.startswith("=> PASS: AUTHENTIC") for h in heads), 1)
                self.assertEqual(sum(h.startswith(f"=> {NOT_EXECUTABLE_WORD}") for h in heads), 1)

    def test_the_refusal_record_beside_a_tampered_bundle_exits_1_not_3(self):
        # 1 beats 3: a forged receipt anywhere in the run is a refusal of the run,
        # and the forged bundle -- not the refusal record -- is the one named FAILED.
        forged = self._staged("case-1-allow")
        self._corrupt_receipt_signature(forged)
        rc, out = self._cli("--domain", self.DOMAIN, self.REFUSAL_SAMPLE, forged)
        self.assertEqual(rc, EXIT_REFUSED, out[-1500:])
        self.assertIn("1/2 sample(s) verified", out)
        after = out[out.index("1/2 sample(s) verified"):]
        self.assertTrue(any("FAILED" in l for l in self._lines_naming(after, forged)))
        self.assertFalse(any("FAILED" in l for l in self._lines_naming(after, self.REFUSAL_SAMPLE)),
                         "the authentic refusal record must not be listed as FAILED")

    # -- 3. refusals of the refusal record stay FAIL / 1 --------------------------------

    def test_a_tampered_signature_on_the_refusal_record_is_a_refusal_exit_1_not_3(self):
        # PRECEDENCE, single bundle. A refusal record whose signature does not
        # recover is not an authentic-not-executable record; it is not authentic.
        # 1 must win over 3, or the new branch becomes a place for a forged
        # refusal to hide -- the same argument D-090(a) made for a forged BLOCK.
        target = self._staged("refusal-vault-paused")
        self._corrupt_refusal_signature(target)
        ok, _checks = _verify(target)
        self.assertFalse(ok, "the control: the corrupted record must not verify")
        rc, out = self._cli("--domain", trust_root(target), target)
        self._assert_refused(rc, out)
        self.assertIn(f"[FAIL] {self.REFUSAL_RECOVERY_CHECK}", out)

    def test_a_refusal_record_with_a_stray_override_beside_it_is_refused_not_NOT_EXECUTABLE(self):
        # MEASURED at 0bc79a8, before this ruling: verify.py already refuses this
        # bundle -- `=> FAIL`, exit 1, on D-052(b)'s check -- because an unexamined
        # §5.5 credential riding beside a refusal is not a certifiable shape. The
        # analogous BLOCK bundle with a foreign override.json is also refused, on the
        # override binding checks (pinned below as the control). D-091(a) must not
        # move either into the new state: 1 beats 3, and a refused bundle is not an
        # authentic one whatever else is in the directory.
        target = self._staged("refusal-vault-paused")
        shutil.copy(os.path.join(OVERRIDE_SAMPLE, "override.json"),
                    os.path.join(target, "override.json"))
        rc, out = self._cli("--domain", trust_root(target), target)
        self._assert_refused(rc, out)
        self.assertIn(f"[FAIL] {self.REFUSAL_OVERRIDE_CHECK}", out)
        # The control: the same foreign override beside a BLOCK receipt.
        block = self._staged("case-2-injection-block")
        shutil.copy(os.path.join(OVERRIDE_SAMPLE, "override.json"),
                    os.path.join(block, "override.json"))
        rc, out = self._cli("--domain", trust_root(block), block)
        self._assert_refused(rc, out)
        self.assertIn("[FAIL] override targets a REVIEW receipt, not a BLOCK (§5.5)", out)

    # -- 4. what does not move ----------------------------------------------------------

    def test_verify_sample_still_answers_authenticity_for_the_refusal_record(self):
        # The library call every in-process test consumes, and what the tamper
        # self-test's "correctly rejected" reads. A refusal record is authentic, so
        # `ok` is True; the reporting layer owns the word and the code (D-090(a)).
        ok, checks = _verify(self.REFUSAL_SAMPLE)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])
        self.assertFalse(any("EXECUTABLE" in c.name.upper() for c in checks),
                         "no check named for executability may join the authenticity list "
                         "(D-088: verify.py carries no executability condition)")

    def test_the_tamper_self_test_on_the_refusal_sample_is_untouched(self):
        # MEASURED at 0bc79a8 and pinned unchanged: `--tamper all` exits 0 with every
        # refusal-* mode "correctly rejected"; a receipt-only mode is N/A and exits 0;
        # a reason-code mode is N/A on a sample with zero reason codes and exits 0.
        # `--tamper` replaces the headline with the self-test verdict, so the
        # NOT EXECUTABLE word must never appear on this arm.
        rc, out = self._cli("--domain", self.DOMAIN, "--tamper", "all", self.REFUSAL_SAMPLE)
        self.assertEqual(rc, EXIT_PASS, out[-2000:])
        # D-092(e) rewrote the summary sentence (TestExitContractD092 pins its counts).
        self.assertRegex(out, r"(?m)^1/1 sample\(s\) ")
        self.assertIn("correctly rejected the mutated refusal-signature", out)
        self.assertNotIn("WRONGLY", out)
        self.assertNotIn(NOT_EXECUTABLE_WORD, out)
        self.assertNotIn("NOT EXECUTABLE", out)
        for mode in ("signature", "reasons-reorder"):
            with self.subTest(mode=mode):
                rc, out = self._cli("--domain", self.DOMAIN, "--tamper", mode,
                                    self.REFUSAL_SAMPLE)
                self.assertEqual(rc, EXIT_PASS, out[-2000:])
                self.assertIn("=> N/A", out)
                self.assertNotIn(NOT_EXECUTABLE_WORD, out)
                self.assertNotIn("=> PASS", out)
                self.assertNotIn("=> FAIL", out)


class TestExitContractD092(unittest.TestCase):
    """D-092(c), (d), (e), written before any implementer touched verify.py (D-058(1)).

    THE DEFECT (c), measured at 02458d2 on 2026-09-02. `verify.py` reads no clock.
    `fixtures/samples/case-1-allow` and `case-4-review-failmode-review` both carry
    `issuedAt` 1788059584 / `expiresAt` 1788059884 -- a window that closed on
    2026-08-29 -- and `verify.py --domain fixtures/samples/domain.json <bundle>`
    printed `=> PASS: AUTHENTIC`, exit 0, on each. SentinelVault (`SentinelVault.sol`
    ~:393-397) refuses both on the window, and so does verify_publication.py
    (`issuedAt <= evaluationTime < expiresAt`, host clock). D-090(a) took the PASS
    word away from a bundle the Vault refuses on its VERDICT; this is the one
    remaining offline-checkable refusal it still exited 0 for.

    THE RULED CONTRACT (c). `verify.py` compares the receipt's validity window --
    and the override's, when an override.json is present (§5.5's payload carries
    `issuedAt` / `expiresAt`; measured on the shipped override) -- to the HOST clock,
    with exactly the publication verifier's predicate: `issuedAt <= now < expiresAt`.
    An authentic bundle whose window does not contain the host instant is
    `=> AUTHENTIC, NOT EXECUTABLE: ...`, exit 3, `NOT EXECUTABLE: <path>` after the
    summary, counted authentic; the headline NAMES THE WINDOW and states that the
    host clock is unauthenticated. Not-yet-valid is the same class as expired.
    Precedence: 1 beats 3 beats 0 as before, and within 3 a BLOCK, an un-overridden
    REVIEW or a refusal record keeps its D-090(a)/D-091(a) headline over the window.
    A LIVE ALLOW, or a LIVE REVIEW with a LIVE override, keeps `=> PASS` / exit 0.

    WHAT DOES NOT MOVE. The authenticity certification: `verify_sample()` still
    returns authenticity, an expired receipt is still an authentic one, the tamper
    self-test on an expired fixture still exits 0. NO CALLER-SUPPLIED INSTANT: the
    host clock is the only clock, so no flag, environment variable or library
    parameter can restore exit 0 on an expired receipt (the publication verifier's
    `--evaluation-time` is a non-certifying diagnostic mode; this tool gets none).
    The "no clock" / "evaluates no validity window" sentences in the output are now
    false and must go; what replaces them must disclose the host clock as
    unauthenticated.

    HOW A PASS IS TESTED NOW. No shipped receipt is live, so every test that needs
    exit 0 MINTS a bundle: a staged copy re-windowed around the host instant and
    re-signed with the published signer key (`live_window`, `rewindow`), and for
    REVIEW an override derived from the shipped one with its own window set and
    re-signed by the mandate principal. The pair "minted live -> PASS / 0, same
    bundle re-windowed into the past -> 3" isolates the window as the only thing
    that moved.

    THE AGGREGATE. `--all fixtures/samples` lists SEVEN NOT EXECUTABLE bundles --
    four BLOCK, one refusal record, two expired -- still `7/7 sample(s) verified as
    AUTHENTIC`, exit 3, and nothing in the shipped corpus PASSES any more.

    (d) TWO WORDING PINS on the refusal-record path (`refusal-vault-paused`): the
    per-check line `[PASS] ALLOW: the signer-attested decoded parameters conform to
    the mandate (§5.7.1)` labels ALLOW as the REQUESTED verdict -- a refusal record
    attests no verdict, and a bare `[PASS] ALLOW:` on a refusal reads as one -- and
    the continuation under the refusal headline reads `neither a certification nor
    a rejection` (a refusal record IS a refusal; "nor a refusal" contradicts the
    line above it). The BLOCK path may keep its wording.

    (e) `--tamper` SUMMARY HONESTY. `--tamper all` on `case-2-injection-block` ran
    10 applicable modes and skipped 20 as N/A (14 / 16 on the refusal sample) and
    summarised "behaved as expected under every tamper mode". The summary now states
    the applicable count and the N/A count as numbers that match the per-mode lines
    actually printed, and says `self-test`; exit 0 stays (a self-test contract,
    stated in `--help`).
    """

    ALLOW_SAMPLE = os.path.join(SAMPLES, "case-1-allow")
    REVIEW_SAMPLE = os.path.join(SAMPLES, "case-4-review-failmode-review")
    BLOCK_SAMPLE = os.path.join(SAMPLES, "case-2-injection-block")
    REFUSAL_SAMPLE = os.path.join(SAMPLES, "refusal-vault-paused")
    DOMAIN = os.path.join(SAMPLES, "domain.json")

    # Measured on the shipped ALLOW and overridden-REVIEW fixtures; asserted by the
    # premise test below rather than assumed, so a regenerated corpus is noticed.
    SHIPPED_WINDOW = (1788059584, 1788059884)
    DAY = 86400

    # The claims the old output made and the new one may not (case-insensitive).
    OLD_CLAIMS = ("no clock", "evaluates no validity window", "evaluate no validity window")
    CLOCK_DISCLOSURE = re.compile(r"unauthenticated|not (?:an )?authenticated")

    # D-092(d): the §5.7.1 conformance check, minus its `ALLOW:` label.
    CONFORMANCE_TAIL = "the signer-attested decoded parameters conform to the mandate (§5.7.1)"

    # "and similar": every spelling of a caller-supplied instant this lane could think
    # of. argparse rejects an unknown option with status 2 and names it.
    INSTANT_FLAGS = ("--evaluation-time", "--evaluation_time", "--now", "--at", "--time",
                     "--clock", "--epoch", "--instant", "--as-of")
    INSTANT_ENV = ("SENTINEL_EVALUATION_TIME", "SENTINEL_NOW", "EVALUATION_TIME",
                   "VERIFY_NOW", "SOURCE_DATE_EPOCH")
    INSTANT_PARAM = re.compile(r"time|now|instant|clock|epoch|evaluat", re.IGNORECASE)

    # -- helpers (the D-090 / D-091 classes', by reference, so the three cannot drift) --

    _cli = TestExitContractD090._cli
    _proc = TestExitContractD090._proc
    _tmp = TestExitContractD090._tmp
    _staged = TestExitContractD090._staged
    _staged_with_verdict = TestExitContractD090._staged_with_verdict
    _add_owner_override = TestExitContractD090._add_owner_override
    _corrupt_hex = staticmethod(TestExitContractD090._corrupt_hex)
    _corrupt_receipt_signature = TestExitContractD090._corrupt_receipt_signature
    _corrupt_override_signature = TestExitContractD090._corrupt_override_signature
    _lines_naming = TestExitContractD090._lines_naming
    _assert_pass = TestExitContractD090._assert_pass
    _assert_refused = TestExitContractD090._assert_refused
    _assert_refusal_not_executable = TestExitContractD091._assert_refusal_not_executable

    @staticmethod
    def _now():
        return int(time.time())

    @staticmethod
    def _receipt_window(target):
        body = read_json(target, "receipt.json")["receipt"]
        return int(body["issuedAt"]), int(body["expiresAt"])

    @staticmethod
    def _override_window(target):
        body = read_json(target, "override.json")["override"]
        return int(body["issuedAt"]), int(body["expiresAt"])

    def _minted(self, verdict=None, window=None, source="case-1-allow"):
        """A staged copy of `source`, optionally re-verdicted, re-windowed and re-sealed.

        `verdict` is `(num, name)` as `_staged_with_verdict` takes it; `window` is
        `(issuedAt, expiresAt)` and defaults to one containing the host instant.
        """
        target = (self._staged(source) if verdict is None
                  else self._staged_with_verdict(*verdict, source=source))
        rewindow(target, *(live_window() if window is None else window))
        return target

    def _add_windowed_override(self, target, window):
        """The D-090 owner override, with its §5.5 window set to `window` and re-signed."""
        self._add_owner_override(target)
        doc = read_json(target, "override.json")
        doc["override"]["issuedAt"] = str(int(window[0]))
        doc["override"]["expiresAt"] = str(int(window[1]))
        doc["ownerSignature"] = sign_digest(
            eip712.override_digest(read_json(SAMPLES, "domain.json"), doc["override"]),
            verify._OWNER_TEST_KEY)
        write_json(os.path.join(target, "override.json"), doc)

    def _assert_clock_disclosed(self, out, where="the output"):
        low = out.lower()
        for claim in self.OLD_CLAIMS:
            self.assertNotIn(claim, low,
                             f"{where} still claims {claim!r}; under D-092(c) the tool reads "
                             "the host clock, so that sentence is false")
        self.assertIn("host clock", low, f"{where} must say which clock it read")
        self.assertRegex(low, self.CLOCK_DISCLOSURE,
                         f"{where} must disclose the host clock as unauthenticated")

    def _assert_window_not_executable(self, rc, out, window, extra_words=(), forbidden=()):
        """The whole of the D-092(c) contract for one authentic bundle outside its window."""
        self.assertEqual(rc, EXIT_NOT_EXECUTABLE,
                         f"an authentic bundle outside its window must exit "
                         f"{EXIT_NOT_EXECUTABLE}, got {rc}")
        blocks = _headline_blocks(out)
        self.assertEqual(len(blocks), 1, f"expected one headline, got {blocks!r}")
        head = blocks[0]
        first = head.splitlines()[0]
        self.assertTrue(head.startswith(f"=> {NOT_EXECUTABLE_WORD}"),
                        f"the headline word must be {NOT_EXECUTABLE_WORD!r}; got {head!r}")
        self.assertNotIn("PASS", first, "the recipient-facing word must not contain PASS")
        self.assertNotIn("FAIL", first, "an authentic bundle is not a refusal; no FAIL")
        self.assertIn("AUTHENTIC", head, "the output must still state the bundle is authentic")
        # NAMES THE WINDOW: both endpoints, as the uint64 decimal strings the receipt
        # carries and the publication verifier prints (`got {issuedAt} <= {now} < {expiresAt}`).
        for endpoint in window:
            self.assertIn(str(endpoint), head,
                          f"the headline must name the window that failed ({window}): {head!r}")
        self.assertIn("window", head.lower(), f"the headline must say it is the window: {head!r}")
        self._assert_clock_disclosed(head, "the headline")
        for word in extra_words:
            self.assertIn(word, head, f"the headline must say {word!r}: {head!r}")
        # H-5: a false diagnostic is worse than none. An expired ALLOW is not a BLOCK,
        # and an expired REVIEW beside its override does not "carry no override.json".
        for phrase in ("the signed verdict is BLOCK", "carries no override.json") + tuple(forbidden):
            self.assertNotIn(phrase, head,
                             f"the headline borrows a sentence that is false here: {phrase!r}")
        self.assertNotIn("=> PASS", out, "no `=> PASS` anywhere in the run")
        self.assertNotIn("=> FAIL", out, "no `=> FAIL` anywhere in the run")
        self.assertIn("1/1 sample(s) verified", out, "the count is the AUTHENTIC count")
        after_summary = out[out.index("1/1 sample(s) verified"):]
        self.assertIn("NOT EXECUTABLE", after_summary,
                      "the summary must say the bundle is not executable")
        self.assertNotIn("FAILED:", after_summary, "nothing here is refused")
        self._assert_clock_disclosed(out, "the run's output")

    # -- 0. the premise, measured ------------------------------------------------------

    def test_the_shipped_receipt_fixtures_are_expired_and_the_shipped_override_is_live(self):
        # If the corpus is ever regenerated with live receipts, every "shipped fixture
        # exits 3" test below would fail for the wrong reason; this names the reason.
        now = self._now()
        for path in sample_dirs():
            with self.subTest(sample=os.path.basename(path)):
                issued, expires = self._receipt_window(path)
                self.assertLess(issued, expires)
                self.assertLessEqual(expires, now, f"{path} is not expired at {now}")
        for path in (self.ALLOW_SAMPLE, self.REVIEW_SAMPLE):
            self.assertEqual(self._receipt_window(path), self.SHIPPED_WINDOW)
        issued, expires = self._override_window(self.REVIEW_SAMPLE)
        self.assertTrue(issued <= now < expires,
                        "the shipped override's own window is live; only the receipt's closed")
        self.assertIn("issuedAt", read_json(self.REVIEW_SAMPLE, "override.json")["override"],
                      "§5.5's payload carries a window, so the override's is checked too")

    # -- 1. the shipped, expired fixtures ------------------------------------------------

    def test_the_shipped_ALLOW_fixture_is_AUTHENTIC_NOT_EXECUTABLE_and_exits_3(self):
        # THE DEFECT, measured: `=> PASS: AUTHENTIC`, exit 0, at 02458d2.
        ok, checks = _verify(self.ALLOW_SAMPLE)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])   # the control: authentic
        rc, out = self._cli("--domain", self.DOMAIN, self.ALLOW_SAMPLE)
        self._assert_window_not_executable(rc, out, self.SHIPPED_WINDOW,
                                           forbidden=("the signed verdict is REVIEW",))
        self.assertTrue(self._lines_naming(out[out.index("1/1 sample(s) verified"):],
                                           self.ALLOW_SAMPLE),
                        "the NOT EXECUTABLE line after the summary must name the bundle's path")

    def test_the_process_exit_status_a_script_reads_is_3_for_the_shipped_ALLOW_fixture(self):
        # Through the interpreter, not `main()`: the status `sys.exit(main())` delivers.
        rc, out = self._proc("--domain", self.DOMAIN, self.ALLOW_SAMPLE)
        self._assert_window_not_executable(rc, out, self.SHIPPED_WINDOW)

    def test_the_shipped_overridden_REVIEW_fixture_is_exit_3_on_the_receipt_window_not_the_override(self):
        # The override's window (0 .. 4000000000) contains now; the receipt's does not.
        # So the headline names the RECEIPT's window, and must not say the bundle
        # carries no override -- it carries a valid, live one, and the override checks
        # must still have run.
        rc, out = self._cli("--domain", self.DOMAIN, self.REVIEW_SAMPLE)
        self._assert_window_not_executable(rc, out, self.SHIPPED_WINDOW,
                                           forbidden=("the signed verdict is REVIEW",))
        self.assertIn("override targets a REVIEW receipt", out,
                      "the override checks still run on an expired REVIEW receipt")
        self.assertNotIn("4000000000", _headline_blocks(out)[0],
                         "the override's window is live and is not the reason")

    # -- 2. the pair that isolates the window ---------------------------------------------

    def test_a_live_ALLOW_keeps_PASS_and_exit_0_and_the_same_bundle_expired_exits_3(self):
        target = self._minted()
        rc, out = self._cli("--domain", trust_root(target), target)
        self._assert_pass(rc, out)
        self._assert_clock_disclosed(out, "the PASS output")
        rc, out = self._proc("--domain", trust_root(target), target)
        self._assert_pass(rc, out)
        # One bundle, two timestamps moved, nothing else: 0 -> 3.
        now = self._now()
        closed = (now - 2 * 3600, now - 3600)
        rewindow(target, *closed)
        ok, checks = _verify(target)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])   # still authentic
        rc, out = self._cli("--domain", trust_root(target), target)
        self._assert_window_not_executable(rc, out, closed)
        rc, out = self._proc("--domain", trust_root(target), target)
        self._assert_window_not_executable(rc, out, closed)

    def test_a_receipt_not_yet_valid_is_the_same_class_as_an_expired_one(self):
        now = self._now()
        future = (now + self.DAY, now + 2 * self.DAY)
        target = self._minted(window=future)
        ok, checks = _verify(target)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])
        rc, out = self._cli("--domain", trust_root(target), target)
        self._assert_window_not_executable(rc, out, future)

    def test_the_window_is_issuedAt_inclusive_and_expiresAt_exclusive_like_the_publication_verifier(self):
        # `issuedAt <= now < expiresAt`, verbatim from verify_publication.py. The host
        # instant only moves forward, so an instant read BEFORE the run bounds it:
        # issuedAt == t0 is inside (t0 <= now), expiresAt == t0 is outside (now < t0 fails).
        t0 = self._now()
        at_issue = self._minted(window=(t0, t0 + self.DAY))
        rc, out = self._cli("--domain", trust_root(at_issue), at_issue)
        self._assert_pass(rc, out)
        at_expiry = self._minted(window=(t0 - self.DAY, t0))
        rc, out = self._cli("--domain", trust_root(at_expiry), at_expiry)
        self._assert_window_not_executable(rc, out, (t0 - self.DAY, t0))

    # -- 3. REVIEW: the receipt's window and the override's ---------------------------------

    def test_a_live_REVIEW_with_a_live_override_is_PASS_and_without_one_is_exit_3_naming_the_override(self):
        target = self._minted(verdict=(1, "REVIEW"))
        rc, out = self._cli("--domain", trust_root(target), target)
        # Live but un-overridden: D-090(a)'s headline, not the window's.
        self.assertEqual(rc, EXIT_NOT_EXECUTABLE, out[-1500:])
        head = _headline_blocks(out)[0]
        self.assertIn("the signed verdict is REVIEW", head)
        self.assertIn("override", head)
        self._add_windowed_override(target, live_window())
        rc, out = self._cli("--domain", trust_root(target), target)
        self._assert_pass(rc, out)
        self.assertIn("override targets a REVIEW receipt", out)
        rc, out = self._proc("--domain", trust_root(target), target)
        self._assert_pass(rc, out)

    def test_a_live_REVIEW_whose_override_window_has_closed_exits_3_naming_the_override_window(self):
        now = self._now()
        for label, window in (("closed", (now - 2 * 3600, now - 3600)),
                              ("not yet open", (now + self.DAY, now + 2 * self.DAY))):
            with self.subTest(override_window=label):
                target = self._minted(verdict=(1, "REVIEW"))
                self._add_windowed_override(target, window)
                ok, checks = _verify(target)
                self.assertTrue(ok, [c.name for c in checks if not c.ok])   # authentic
                rc, out = self._cli("--domain", trust_root(target), target)
                self._assert_window_not_executable(rc, out, window, extra_words=("override",),
                                                   forbidden=("the signed verdict is REVIEW",))
                # The receipt's own window is live and is not the reason.
                issued, expires = self._receipt_window(target)
                self.assertTrue(issued <= self._now() < expires)

    def test_an_expired_REVIEW_with_a_live_override_is_exit_3_on_the_receipt_window(self):
        now = self._now()
        closed = (now - 2 * 3600, now - 3600)
        target = self._minted(verdict=(1, "REVIEW"), window=closed)
        self._add_windowed_override(target, live_window())
        rc, out = self._cli("--domain", trust_root(target), target)
        self._assert_window_not_executable(rc, out, closed,
                                           forbidden=("the signed verdict is REVIEW",))
        self.assertIn("override targets a REVIEW receipt", out)

    # -- 4. precedence inside exit 3, and 1 over 3 ---------------------------------------------

    def test_a_BLOCK_verdict_takes_precedence_over_the_window_in_the_headline(self):
        # The shipped BLOCK is expired AND a BLOCK; the lead sentence is the BLOCK one.
        # A BLOCK minted live is 3 for the verdict alone, with the same lead: the
        # window is not what demotes a BLOCK.
        for label, target in (("shipped, expired", self.BLOCK_SAMPLE),
                              ("minted, live", self._minted(verdict=(0, "BLOCK")))):
            with self.subTest(block=label):
                rc, out = self._cli("--domain", trust_root(target) if label.startswith("minted")
                                    else self.DOMAIN, target)
                self.assertEqual(rc, EXIT_NOT_EXECUTABLE, out[-1500:])
                first = _headline_blocks(out)[0].splitlines()[0]
                self.assertTrue(
                    first.startswith(f"=> {NOT_EXECUTABLE_WORD}: the signed verdict is BLOCK"),
                    f"the BLOCK sentence leads, whatever the window says: {first!r}")
                self._assert_clock_disclosed(out, "the run's output")

    def test_an_un_overridden_REVIEW_takes_precedence_over_the_window_in_the_headline(self):
        # Expired AND un-overridden: the cure the headline names is still the override
        # (R-A018-16(c)); the window is the second thing wrong, not the first.
        target = self._staged("case-4-review-failmode-review")
        os.remove(os.path.join(target, "override.json"))
        self.assertLess(self._receipt_window(target)[1], self._now())
        rc, out = self._cli("--domain", trust_root(target), target)
        self.assertEqual(rc, EXIT_NOT_EXECUTABLE, out[-1500:])
        head = _headline_blocks(out)[0]
        first = head.splitlines()[0]
        self.assertTrue(
            first.startswith(f"=> {NOT_EXECUTABLE_WORD}: the signed verdict is REVIEW"),
            f"the REVIEW sentence leads, whatever the window says: {first!r}")
        self.assertIn("override", head)

    def test_the_refusal_record_headline_is_unchanged_by_the_window_rule(self):
        # A §5.5.1 record carries an issuedAt and no expiresAt: there is no receipt
        # window to compare, and D-091(a)'s headline stands word for word in its lead.
        rc, out = self._cli("--domain", self.DOMAIN, self.REFUSAL_SAMPLE)
        self._assert_refusal_not_executable(rc, out)
        first = _headline_blocks(out)[0].splitlines()[0]
        self.assertTrue(first.startswith(f"=> {NOT_EXECUTABLE_WORD}: this is a §5.5.1 refusal record"),
                        first)
        for word in ("expired", "window", "1788059584"):
            self.assertNotIn(word, first, "a refusal record has no window to have missed")
        self._assert_clock_disclosed(out, "the run's output")

    def test_a_refusal_of_any_check_beats_the_window_exit_1_not_3(self):
        # 1 beats 3: an expired bundle whose signature does not recover is a refusal,
        # not an authentic-not-executable one, on the receipt and on the override.
        expired_allow = self._staged("case-1-allow")
        self._corrupt_receipt_signature(expired_allow)
        rc, out = self._cli("--domain", trust_root(expired_allow), expired_allow)
        self._assert_refused(rc, out)
        self.assertNotIn("NOT EXECUTABLE", out)
        expired_review = self._staged("case-4-review-failmode-review")
        self._corrupt_override_signature(expired_review)
        rc, out = self._cli("--domain", trust_root(expired_review), expired_review)
        self._assert_refused(rc, out)
        self.assertNotIn("NOT EXECUTABLE", out)
        # And a live bundle that is refused is refused: the window earns nothing.
        live = self._minted()
        self._corrupt_receipt_signature(live)
        rc, out = self._cli("--domain", trust_root(live), live)
        self._assert_refused(rc, out)

    # -- 5. no caller-supplied instant -------------------------------------------------------

    def test_no_flag_supplies_the_instant(self):
        # The one flag that would restore exit 0 on an expired receipt. argparse
        # rejects an unknown option with status 2 -- pinned as "rejected", not merely
        # "does not exit 0", so that a future `--evaluation-time` that is parsed and
        # ignored is also caught (it would exit 3 and pass a weaker assertion).
        inside = str(self.SHIPPED_WINDOW[0] + 1)
        for flag in self.INSTANT_FLAGS:
            with self.subTest(flag=flag):
                rc, out = self._proc(flag, inside, "--domain", self.DOMAIN, self.ALLOW_SAMPLE)
                self.assertEqual(rc, 2, f"{flag} must be rejected by the parser: {out[-800:]}")
                self.assertIn("unrecognized arguments", out)
                self.assertNotIn("=> PASS", out)
                rc, out = self._proc(f"{flag}={inside}", "--domain", self.DOMAIN, self.ALLOW_SAMPLE)
                self.assertEqual(rc, 2, out[-800:])
        rc, out = self._proc("--help")
        self.assertEqual(rc, 0)
        self.assertNotRegex(out.lower(), r"evaluation[- _]time",
                            "--help must not advertise a caller-supplied instant")

    def test_no_environment_variable_supplies_the_instant(self):
        inside = str(self.SHIPPED_WINDOW[0] + 1)
        for name in self.INSTANT_ENV:
            with self.subTest(env=name):
                env = dict(os.environ)
                env[name] = inside
                proc = subprocess.run(
                    [sys.executable, os.path.join(REPO, "verifier", "verify.py"),
                     "--domain", self.DOMAIN, self.ALLOW_SAMPLE],
                    capture_output=True, text=True, env=env)
                out = _strip_ansi(proc.stdout + proc.stderr)
                self._assert_window_not_executable(proc.returncode, out, self.SHIPPED_WINDOW)

    def test_no_library_entry_point_takes_an_instant(self):
        # `verify_sample`, `run` and `main` are the seams a caller reaches. None may
        # grow a parameter that names an instant; the clock is read inside.
        for func in (verify.verify_sample, verify.run, verify.main):
            with self.subTest(func=func.__name__):
                params = list(inspect.signature(func).parameters)
                offending = [p for p in params if self.INSTANT_PARAM.search(p)]
                self.assertEqual(offending, [],
                                 f"{func.__name__} takes a caller-supplied instant: {params}")

    # -- 6. the claims the output makes ---------------------------------------------------------

    def test_the_output_no_longer_claims_no_clock_and_discloses_the_host_clock(self):
        # Every headline path and the summary line, plus --help (the module docstring,
        # which is the epilog and today says "THIS TOOL EVALUATES NO VALIDITY WINDOW.
        # It has no clock.").
        live = self._minted()
        runs = {
            "expired ALLOW": self._cli("--domain", self.DOMAIN, self.ALLOW_SAMPLE),
            "expired overridden REVIEW": self._cli("--domain", self.DOMAIN, self.REVIEW_SAMPLE),
            "BLOCK": self._cli("--domain", self.DOMAIN, self.BLOCK_SAMPLE),
            "refusal record": self._cli("--domain", self.DOMAIN, self.REFUSAL_SAMPLE),
            "live ALLOW (PASS)": self._cli("--domain", trust_root(live), live),
            "--all over the corpus": self._proc("--domain", self.DOMAIN, "--all", SAMPLES),
        }
        for label, (_rc, out) in runs.items():
            with self.subTest(run=label):
                self._assert_clock_disclosed(out, f"the {label} output")
                summary = [l for l in out.splitlines() if re.match(r"^\d+/\d+ sample\(s\) verified", l)]
                self.assertEqual(len(summary), 1, summary)
                self._assert_clock_disclosed(summary[0], f"the {label} summary line")
        rc, out = self._proc("--help")
        self.assertEqual(rc, 0)
        low = out.lower()
        for claim in self.OLD_CLAIMS:
            self.assertNotIn(claim, low, f"--help still claims {claim!r}")
        self.assertNotIn("evaluates no validity window", low)
        self.assertIn("host clock", low, "--help must say the tool reads the host clock")

    # -- 7. what does not move ------------------------------------------------------------------

    def test_verify_sample_still_answers_authenticity_for_an_expired_receipt(self):
        # The library call every in-process test consumes, and what the tamper
        # self-test's "correctly still verified" reads. An expired receipt is
        # authentic, so `ok` is True, and the window is NOT an authenticity check:
        # no check named for it may join the list.
        for path in (self.ALLOW_SAMPLE, self.REVIEW_SAMPLE):
            with self.subTest(sample=os.path.basename(path)):
                ok, checks = _verify(path)
                self.assertTrue(ok, [c.name for c in checks if not c.ok])
                names = [c.name.lower() for c in checks]
                self.assertFalse(any("executable" in n or "host clock" in n or "expired" in n
                                     for n in names),
                                 f"the window classification is the reporting layer's, not "
                                 f"verify_sample()'s: {names}")
        # The seam D-090(a) chose: run() returns (ok, checks, executable).
        with contextlib.redirect_stdout(io.StringIO()):
            ok, checks, executable = verify.run(self.ALLOW_SAMPLE, self.DOMAIN, quiet=True)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])
        self.assertFalse(executable, "run() must classify an expired receipt as not executable")
        live = self._minted()
        with contextlib.redirect_stdout(io.StringIO()):
            ok, checks, executable = verify.run(live, trust_root(live), quiet=True)
        self.assertTrue(ok, [c.name for c in checks if not c.ok])
        self.assertTrue(executable, "run() must classify a live ALLOW as executable-shaped")

    def test_the_tamper_self_test_on_the_expired_fixtures_still_exits_0(self):
        # The gate's second arm runs `--all fixtures/samples --tamper all` and takes
        # any non-zero status as a failure. If the window check were pushed into
        # verify_sample(), `reasons-reorder` on the expired ALLOW would be WRONGLY
        # REJECTED and the gate would break.
        for path in (self.ALLOW_SAMPLE, self.REVIEW_SAMPLE):
            with self.subTest(sample=os.path.basename(path)):
                rc, out = self._cli("--domain", self.DOMAIN, "--tamper", "all", path)
                self.assertEqual(rc, EXIT_PASS, out[-2000:])
                self.assertIn("tamper self-test PASS", out)
                self.assertNotIn("WRONGLY", out)
                self.assertNotIn(NOT_EXECUTABLE_WORD, out)
                self.assertNotIn("NOT EXECUTABLE", out)
                if path == self.REVIEW_SAMPLE:
                    # The must-still-verify mode. case-1-allow commits to zero reason
                    # codes, so `reasons-reorder` is N/A there; case-4 commits to two,
                    # and an expired receipt under a pure reorder must still verify.
                    self.assertIn("correctly still verified", out)
        # The gate's own command: every shipped BLOCK is expired too, and each must
        # still be "correctly still verified" under a reorder.
        rc, out = self._cli("--domain", self.DOMAIN, "--all", SAMPLES, "--tamper", "all")
        self.assertEqual(rc, EXIT_PASS, out[-2000:])
        self.assertIn("correctly still verified", out)
        self.assertNotIn("WRONGLY", out)
        self.assertRegex(out, r"(?m)^7/7 sample\(s\) ")

    # -- 8. the aggregate --------------------------------------------------------------------------

    def test_all_over_the_shipped_corpus_lists_seven_NOT_EXECUTABLE_four_BLOCK_one_refusal_two_expired(self):
        # WHAT THE GATE RUNS. README.md, scripts/test.sh and docs say "five" today and
        # will need to say seven (reported, not edited, by this lane).
        rc, out = self._proc("--domain", self.DOMAIN, "--all", SAMPLES)
        self.assertEqual(rc, EXIT_NOT_EXECUTABLE, out[-2000:])
        self.assertRegex(out, r"(?m)^7/7 sample\(s\) verified")
        self.assertNotIn("FAILED:", out)
        self.assertNotIn("=> PASS", out)
        after = out[out.index("7/7 sample(s) verified"):]
        listed = [l for l in after.splitlines() if l.strip().startswith("NOT EXECUTABLE:")]
        self.assertEqual(len(listed), 7, f"seven NOT EXECUTABLE lines, got {listed!r}")
        for path in (self.ALLOW_SAMPLE, self.REVIEW_SAMPLE):
            named = self._lines_naming(after, path)
            self.assertTrue(named and all("NOT EXECUTABLE" in l for l in named),
                            f"{path} is expired and must be listed; got {named!r}")
        heads = _headline_blocks(out)
        self.assertEqual(len(heads), 7)
        self.assertTrue(all(h.startswith(f"=> {NOT_EXECUTABLE_WORD}") for h in heads))
        firsts = [h.splitlines()[0] for h in heads]
        self.assertEqual(sum("the signed verdict is BLOCK" in f for f in firsts), 4)
        self.assertEqual(sum("refusal record" in f.lower() for f in firsts), 1)
        window_heads = [h for h in heads
                        if "the signed verdict is BLOCK" not in h.splitlines()[0]
                        and "refusal record" not in h.splitlines()[0].lower()]
        self.assertEqual(len(window_heads), 2)
        for h in window_heads:
            for endpoint in self.SHIPPED_WINDOW:
                self.assertIn(str(endpoint), h)

    def test_a_live_ALLOW_beside_an_expired_one_exits_3_and_only_the_expired_one_is_listed(self):
        # 3 beats 0, positional in both orders and under --all; the live bundle PASSES
        # and is not listed after the summary.
        live = self._minted()
        for order in ((live, self.ALLOW_SAMPLE), (self.ALLOW_SAMPLE, live)):
            with self.subTest(order=[os.path.basename(p) for p in order]):
                rc, out = self._cli("--domain", self.DOMAIN, *order)
                self.assertEqual(rc, EXIT_NOT_EXECUTABLE, out[-1500:])
                self.assertIn("2/2 sample(s) verified", out)
                after = out[out.index("2/2 sample(s) verified"):]
                self.assertTrue(self._lines_naming(after, self.ALLOW_SAMPLE))
                self.assertFalse(self._lines_naming(after, live))
                heads = _headline_blocks(out)
                self.assertEqual(sum(h.startswith("=> PASS: AUTHENTIC") for h in heads), 1)
                self.assertEqual(sum(h.startswith(f"=> {NOT_EXECUTABLE_WORD}") for h in heads), 1)
        tmp = self._tmp()
        shutil.copytree(live, os.path.join(tmp, "minted-live"))
        shutil.copytree(self.ALLOW_SAMPLE, os.path.join(tmp, "case-1-allow"))
        rc, out = self._proc("--domain", self.DOMAIN, "--all", tmp)
        self.assertEqual(rc, EXIT_NOT_EXECUTABLE, out[-1500:])
        self.assertRegex(out, r"(?m)^2/2 sample\(s\) verified")
        after = out[out.index("2/2 sample(s) verified"):]
        self.assertTrue(self._lines_naming(after, os.path.join(tmp, "case-1-allow")))
        self.assertFalse(self._lines_naming(after, os.path.join(tmp, "minted-live")))

    def test_an_expired_bundle_beside_a_refused_one_exits_1(self):
        tmp = self._tmp()
        shutil.copytree(self.ALLOW_SAMPLE, os.path.join(tmp, "case-1-allow"))
        forged = os.path.join(tmp, "forged")
        shutil.copytree(self.ALLOW_SAMPLE, forged)
        self._corrupt_receipt_signature(forged)
        rc, out = self._proc("--domain", self.DOMAIN, "--all", tmp)
        self.assertEqual(rc, EXIT_REFUSED, out[-1500:])
        self.assertRegex(out, r"(?m)^1/2 sample\(s\) verified")
        self.assertTrue(any("FAILED" in l for l in self._lines_naming(out, forged)))

    # -- 9. D-092(d): two wording pins on the refusal-record path -------------------------------

    def test_the_refusal_bundle_labels_ALLOW_as_the_requested_verdict_on_the_conformance_line(self):
        # Measured at 02458d2: `[PASS] ALLOW: the signer-attested decoded parameters
        # conform to the mandate (§5.7.1)` on a bundle in which the signer attested no
        # verdict at all. The check itself stays (the requested verdict's parameters are
        # still compared); its label says whose verdict ALLOW is.
        rc, out = self._cli("--domain", self.DOMAIN, self.REFUSAL_SAMPLE)
        self.assertEqual(rc, EXIT_NOT_EXECUTABLE, out[-1500:])
        lines = [l for l in out.splitlines() if self.CONFORMANCE_TAIL in l]
        self.assertEqual(len(lines), 1, f"the §5.7.1 conformance line must still print once: {lines!r}")
        self.assertIn("[PASS]", lines[0], "the check still holds on this bundle")
        self.assertIn("requested", lines[0].lower(),
                      f"ALLOW must be labelled as the REQUESTED verdict: {lines[0]!r}")
        bare = [l for l in out.splitlines() if re.match(r"^\s*\[PASS\] ALLOW:", l)]
        self.assertEqual(bare, [], f"no bare `[PASS] ALLOW:` on a refusal record: {bare!r}")

    def test_the_refusal_record_continuation_reads_neither_a_certification_nor_a_rejection(self):
        # Measured at 02458d2: "Exit status 3: neither a certification nor a refusal."
        # under a headline that says the bundle IS the signer's refusal.
        rc, out = self._cli("--domain", self.DOMAIN, self.REFUSAL_SAMPLE)
        self.assertEqual(rc, EXIT_NOT_EXECUTABLE, out[-1500:])
        head = _headline_blocks(out)[0]
        self.assertIn("neither a certification nor a rejection", head, head)
        self.assertNotIn("nor a refusal", head,
                         "a refusal record is a refusal; the continuation may not deny it")
        # The BLOCK path is not held to this by the ruling; pinned only as "still exit 3".
        rc, _out = self._cli("--domain", self.DOMAIN, self.BLOCK_SAMPLE)
        self.assertEqual(rc, EXIT_NOT_EXECUTABLE)

    # -- 10. D-092(e): --tamper summary honesty ---------------------------------------------------

    # Measured at 02458d2 with `grep -c`: per-mode lines actually printed.
    TAMPER_COUNTS = {"case-2-injection-block": (10, 20), "refusal-vault-paused": (14, 16)}

    def test_the_tamper_summary_states_applicable_and_NA_counts_that_match_the_lines_printed(self):
        self.assertEqual(sum(self.TAMPER_COUNTS["case-2-injection-block"]), len(verify.TAMPER_MODES))
        self.assertEqual(sum(self.TAMPER_COUNTS["refusal-vault-paused"]), len(verify.TAMPER_MODES))
        for name, (want_applicable, want_na) in self.TAMPER_COUNTS.items():
            with self.subTest(sample=name):
                rc, out = self._cli("--domain", self.DOMAIN, "--tamper", "all",
                                    os.path.join(SAMPLES, name))
                self.assertEqual(rc, EXIT_PASS, out[-2000:])          # (e): exit 0 stays
                applicable = [l for l in out.splitlines() if "=> tamper self-test" in l]
                na = [l for l in out.splitlines() if l.strip().startswith("=> N/A")]
                self.assertEqual((len(applicable), len(na)), (want_applicable, want_na),
                                 "the per-mode lines are the measurement the summary must match")
                self.assertTrue(all("PASS" in l for l in applicable), applicable)
                self.assertNotIn("WRONGLY", out)
                summary = [l for l in out.splitlines() if re.match(r"^1/1 sample\(s\)", l)]
                self.assertEqual(len(summary), 1, f"one run summary line: {summary!r}")
                line = summary[0]
                self.assertIn("self-test", line, f"the run headline must say self-test: {line!r}")
                numbers = {int(n) for n in re.findall(r"\b\d+\b", line[len("1/1"):])}
                self.assertIn(want_applicable, numbers,
                              f"the summary must state the applicable count {want_applicable}: {line!r}")
                self.assertIn(want_na, numbers,
                              f"the summary must state the N/A count {want_na}: {line!r}")
                self.assertNotIn("every tamper mode", line,
                                 f"{want_na} modes did not run; the summary may not say every: {line!r}")
                self.assertNotIn(NOT_EXECUTABLE_WORD, out)
                self.assertNotIn("=> PASS", out)
                self.assertNotIn("=> FAIL", out)


def _norm(a):
    return a.lower().replace("0x", "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
