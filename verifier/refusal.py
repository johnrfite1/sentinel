"""SignedRefusalRecord, per §5.5.1 (normative; added to the spec 2026-08-16).

§5.5.1 is the first place the published specification describes a refusal at
all. Before it, `{"refused": true}` was a claim nobody outside the signer could
check, and this verifier's only honest answer was to fail closed (REPORT.md
F-13). That answer is now replaceable with an actual verification -- but only
for the parts §5.5.1 pins down. Everything this module decides that §5.5.1 does
not state is marked CHOICE and written up in REPORT.md F-18.

What §5.5.1 states, and this module implements verbatim:

    keccak256(utf8(
        "sentinel.refusal.v0.2" | "\\n" |
        schemaVersion | "\\n" | chainId | "\\n" | vault | "\\n" |
        actionHash | "\\n" | evidenceHash | "\\n" | requestedVerdict | "\\n" |
        reasonCodesHash | "\\n" | refusedAt | "\\n" | signer
    ))

Ten segments, nine delimiters, no trailing newline, no EIP-712 anywhere. The
charsets are §5.5.1's own: `schemaVersion`, `chainId` and `refusedAt` are
decimal digits; `vault` and `signer` are lowercase `0x` addresses; the three
hashes are lowercase `0x` 32-byte hex; `requestedVerdict` is a §5.9 verdict
NAME.

**The charsets are load-bearing, not cosmetic.** §5.5.1's injectivity argument
is "every field is a fixed charset that cannot contain the newline delimiter".
That is an argument about a *validated* record. A verifier that skips the
validation and joins whatever it was handed loses injectivity outright: a
`requestedVerdict` of "BLOCK\\n0\\n0x...", with the following fields shifted
along, produces the same joined preimage -- and therefore the same digest, and
the same signature -- as a differently-populated record. One signature, two
refusals. This is the D-022 reason-code collision in a new place, and the fix is
the same one: validate with absolute anchors, and reject rather than sanitise.

**Field values go into the preimage verbatim.** They are not re-canonicalized
first. "31337" and "031337" are both "decimal digits" per §5.5.1, they are
different byte strings, and they therefore hash differently -- which is safe
(two digests, not one), where normalising them to a single form in the verifier
and not in the signer would not be. See `NONCANONICAL_DECIMAL` for how a
non-canonical decimal is surfaced without being either accepted silently or
rejected against the spec's own wording.
"""

import re
from typing import Dict, List, Tuple

from keccak import keccak256

# §5.5.1, byte-exact. Not a version number to be liberalised: a differing
# character changes the digest and therefore the recovered address, exactly as
# §5.8 warns for the EIP-712 type strings.
DOMAIN_TAG = "sentinel.refusal.v0.2"

DELIMITER = "\n"

# §5.9 verdict NAMES. §5.5.1 says `requestedVerdict` is a NAME, not the uint8 --
# so "2" is not a legal value here even though §5.9 numbers ALLOW as 2.
VERDICT_NAMES = ("BLOCK", "REVIEW", "ALLOW")

DECIMAL, ADDRESS, HASH32, VERDICT = "decimal", "address", "hash32", "verdict"

# §5.5.1's field list, in §5.5.1's order. "Field order is part of the format."
FIELDS: List[Tuple[str, str]] = [
    ("schemaVersion", DECIMAL),
    ("chainId", DECIMAL),
    ("vault", ADDRESS),
    ("actionHash", HASH32),
    ("evidenceHash", HASH32),
    ("requestedVerdict", VERDICT),
    ("reasonCodesHash", HASH32),
    ("refusedAt", DECIMAL),
    ("signer", ADDRESS),
]

FIELD_NAMES = tuple(name for name, _ in FIELDS)

# Compiled without `^`/`$` and applied with fullmatch, for the reason §5.4/D-022
# spells out at length: in Python `$` also matches before a trailing newline, so
# `^[0-9]+$` accepts "5\n" -- an identifier containing the delimiter the pattern
# exists to exclude, which is precisely how the injectivity argument dies.
_PATTERNS = {
    DECIMAL: re.compile(r"[0-9]+"),
    ADDRESS: re.compile(r"0x[0-9a-f]{40}"),
    HASH32: re.compile(r"0x[0-9a-f]{64}"),
}

_DESCRIPTIONS = {
    DECIMAL: "decimal digits ([0-9]+, matched end to end)",
    ADDRESS: "a lowercase 0x address (0x[0-9a-f]{40})",
    HASH32: "lowercase 0x 32-byte hex (0x[0-9a-f]{64})",
    VERDICT: "a §5.9 verdict NAME, one of " + ", ".join(VERDICT_NAMES),
}

# CHOICE (REPORT.md F-18.3). §5.5.1 says "decimal digits" and stops, so "007" is
# a conforming schemaVersion. Because the field enters the preimage verbatim,
# a leading zero produces a *different* digest rather than a colliding one, so
# it is not a soundness problem and rejecting it would invent a rule §5.5.1 does
# not state. It is surfaced as an advisory instead.
_CANONICAL_DECIMAL = re.compile(r"(?:0|[1-9][0-9]*)")


class RefusalError(ValueError):
    pass


def validate_field(name: str, kind: str, value) -> str:
    """Validate one §5.5.1 field. Fails; never sanitises, never coerces."""
    if isinstance(value, bool) or not isinstance(value, str):
        raise RefusalError(
            f"RefusalRecord.{name} must be a JSON string; got "
            f"{type(value).__name__} {value!r}. §5.5.1's preimage is a string "
            "join, so a JSON number or boolean has no defined spelling in it "
            "and is refused rather than stringified."
        )
    if kind == VERDICT:
        if value not in VERDICT_NAMES:
            raise RefusalError(
                f"RefusalRecord.requestedVerdict {value!r} is not "
                f"{_DESCRIPTIONS[VERDICT]}"
            )
        return value
    if _PATTERNS[kind].fullmatch(value) is None:
        raise RefusalError(
            f"RefusalRecord.{name} {value!r} is not {_DESCRIPTIONS[kind]}; "
            "refusing to normalise. §5.5.1's injectivity argument holds only "
            "for records whose fields are inside their stated charsets."
        )
    return value


def canonical_fields(record) -> Dict[str, str]:
    """Validate a RefusalRecord and return its nine fields in §5.5.1 order.

    Strict in both directions. A missing field cannot be defaulted -- §5.5.1
    gives no defaults and a defaulted field would be a field the signer never
    committed to. An *extra* field is refused for the mirror-image reason and it
    is the more dangerous of the two: the preimage covers exactly nine values,
    so anything else in the record object is uncommitted data that a reader will
    reasonably assume the signature covers. `eip712.struct_hash` refuses an
    over-populated struct for the same reason; this is that rule applied here.
    """
    if not isinstance(record, dict):
        raise RefusalError(
            f"RefusalRecord must be a JSON object, got {type(record).__name__}"
        )
    missing = [name for name in FIELD_NAMES if name not in record]
    if missing:
        raise RefusalError(
            f"RefusalRecord is missing §5.5.1 field(s): {missing}. "
            f"The object presented carries: {sorted(record)}. "
            "§5.5.1 defines the record's nine fields and their order but not "
            "the envelope that carries them, so a mismatch here is as likely "
            "to be a disagreement about the envelope as a malformed record "
            "(REPORT.md F-18.2)."
        )
    extra = sorted(k for k in record if k not in FIELD_NAMES)
    if extra:
        raise RefusalError(
            f"RefusalRecord carries fields not in its §5.5.1 list: {extra}. "
            "The §5.5.1 preimage commits to exactly nine values, so these are "
            "unauthenticated; refusing to hash an under-determined record."
        )
    return {name: validate_field(name, kind, record[name])
            for name, kind in FIELDS}


def noncanonical_decimals(record) -> List[str]:
    """Decimal fields with a leading zero. Advisory; see the CHOICE note above."""
    return [name for name, kind in FIELDS
            if kind == DECIMAL and isinstance(record.get(name), str)
            and _PATTERNS[DECIMAL].fullmatch(record[name])
            and not _CANONICAL_DECIMAL.fullmatch(record[name])]


def preimage(record) -> bytes:
    """The exact §5.5.1 byte string: tag, then nine fields, joined with \\n."""
    fields = canonical_fields(record)
    segments = [DOMAIN_TAG] + [fields[name] for name in FIELD_NAMES]
    return DELIMITER.join(segments).encode("utf-8")


def digest(record) -> bytes:
    """keccak256 of the §5.5.1 preimage. NOT an EIP-712 digest -- §5.5.1 is
    explicit that this record is not a typed structure, so there is no
    `\\x19\\x01`, no domain separator and no typehash anywhere in it."""
    return keccak256(preimage(record))


def digest_hex(record) -> str:
    return "0x" + digest(record).hex()


def render_preimage(record) -> str:
    """The preimage with its delimiters shown, for a check's detail block."""
    return preimage(record).decode("utf-8").replace("\n", "\\n")


def eth_signed_message_digest(payload: bytes) -> bytes:
    """EIP-191 `personal_sign` wrapping. DIAGNOSTIC ONLY -- see F-18.1.

    §5.5.1 names a digest and never says how a signature over it is produced.
    This verifier signs and recovers over the digest directly, which is what
    §5.5.1's words say and what the receipt path does with its EIP-712 digest.
    A producer reaching for a wallet library's `signMessage` instead would
    produce a signature over this wrapping and nothing else would look wrong.
    That divergence is invisible without a name, so when the normative recovery
    fails, the verifier tries this and reports it -- and still FAILS.
    """
    return keccak256(
        b"\x19Ethereum Signed Message:\n"
        + str(len(payload)).encode("ascii")
        + payload
    )
