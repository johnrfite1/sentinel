"""RFC 8785 JSON Canonicalization Scheme, written from the RFC.

Independent of any JCS library and of the Sentinel evaluator. Produces bytes,
not str, because byte-exactness is the whole point.

Implemented rules (RFC 8785 sections 3.2.1 - 3.2.4):
  * No insignificant whitespace anywhere.
  * Object members sorted by key, comparing UTF-16 code units, ascending.
  * Strings serialised per ECMAScript JSON.stringify: the short escapes
    \\b \\t \\n \\f \\r \\" \\\\ , \\u00xx for remaining C0 controls, and every
    other code point emitted literally as UTF-8.
  * Numbers serialised per ECMAScript Number::toString on the IEEE-754 double,
    with RFC 8785's requirement that the shortest round-tripping form is used.
  * Output encoded as UTF-8.
"""

import json
from decimal import Decimal
from typing import Any


class CanonicalizationError(ValueError):
    pass


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def _reject_duplicate_keys(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise CanonicalizationError(
                f"duplicate object member {key!r}: RFC 8785 input must not "
                "contain duplicate keys (see RFC 8785 section 3.1)"
            )
        seen[key] = value
    return seen


def parse(text: str) -> Any:
    """Parse JSON text, rejecting duplicate object members."""
    return json.loads(text, object_pairs_hook=_reject_duplicate_keys)


def parse_bytes(raw: bytes) -> Any:
    # RFC 8785 input is UTF-8. Reject a BOM explicitly rather than silently
    # tolerating it, since it would change the hash.
    if raw.startswith(b"\xef\xbb\xbf"):
        raise CanonicalizationError("input begins with a UTF-8 BOM")
    return parse(raw.decode("utf-8"))


# --------------------------------------------------------------------------
# Number serialisation (ECMAScript Number::toString, ECMA-262 section 6.1.6.1.20)
# --------------------------------------------------------------------------

def serialize_number(value: float) -> str:
    if value != value or value in (float("inf"), float("-inf")):
        raise CanonicalizationError("NaN and Infinity are not valid JSON numbers")

    if value == 0:
        return "0"  # covers -0.0, which JCS serialises as "0"

    sign = "-" if value < 0 else ""
    value = abs(value)

    # repr() of a Python float is the shortest string that round-trips, which is
    # exactly the digit string ECMAScript's algorithm selects.
    dec = Decimal(repr(value)).normalize()
    sign_, digits, exponent = dec.as_tuple()
    digits = "".join(str(d) for d in digits)

    # Strip trailing zeros so k is minimal, as the spec's "k is as small as
    # possible" clause requires.
    while len(digits) > 1 and digits.endswith("0"):
        digits = digits[:-1]
        exponent += 1

    k = len(digits)
    n = k + exponent  # value == 0.digits * 10**n

    if k <= n <= 21:
        return sign + digits + "0" * (n - k)
    if 0 < n <= 21:
        return sign + digits[:n] + "." + digits[n:]
    if -6 < n <= 0:
        return sign + "0." + "0" * (-n) + digits
    # Exponential notation.
    exp = n - 1
    exp_sign = "+" if exp >= 0 else "-"
    mantissa = digits[0] if k == 1 else digits[0] + "." + digits[1:]
    return sign + mantissa + "e" + exp_sign + str(abs(exp))


# --------------------------------------------------------------------------
# String serialisation
# --------------------------------------------------------------------------

_SHORT_ESCAPES = {
    0x08: "\\b",
    0x09: "\\t",
    0x0A: "\\n",
    0x0C: "\\f",
    0x0D: "\\r",
    0x22: '\\"',
    0x5C: "\\\\",
}


def serialize_string(value: str) -> str:
    out = ['"']
    for char in value:
        cp = ord(char)
        escape = _SHORT_ESCAPES.get(cp)
        if escape is not None:
            out.append(escape)
        elif cp < 0x20:
            out.append("\\u%04x" % cp)
        else:
            out.append(char)
    out.append('"')
    return "".join(out)


def _sort_key(key: str) -> bytes:
    """Sort key giving lexicographic order over UTF-16 code units.

    Comparing the UTF-16BE encoding bytewise is equivalent to comparing the
    code-unit sequences numerically, which is what RFC 8785 section 3.2.3
    requires. This differs from comparing Unicode code points for anything
    above U+FFFF: surrogate pairs (0xD800..0xDFFF) sort below U+E000..U+FFFF.
    """
    return key.encode("utf-16-be", errors="surrogatepass")


# --------------------------------------------------------------------------
# Top-level
# --------------------------------------------------------------------------

def _serialize(value: Any, out: list) -> None:
    if value is None:
        out.append("null")
    elif value is True:
        out.append("true")
    elif value is False:
        out.append("false")
    elif isinstance(value, str):
        out.append(serialize_string(value))
    elif isinstance(value, int):
        # A JSON number that Python parsed as int. RFC 8785 requires IEEE-754
        # double treatment, so anything outside the exactly-representable range
        # is a canonicalization hazard rather than something to silently round.
        if abs(value) > 2 ** 53 - 1:
            raise CanonicalizationError(
                f"integer {value} exceeds the IEEE-754 exactly-representable "
                "range; RFC 8785 section 3.2.2.3 cannot canonicalize it without "
                "loss (encode it as a JSON string instead)"
            )
        out.append(serialize_number(float(value)))
    elif isinstance(value, float):
        out.append(serialize_number(value))
    elif isinstance(value, list):
        out.append("[")
        for i, item in enumerate(value):
            if i:
                out.append(",")
            _serialize(item, out)
        out.append("]")
    elif isinstance(value, dict):
        out.append("{")
        for i, key in enumerate(sorted(value.keys(), key=_sort_key)):
            if not isinstance(key, str):
                raise CanonicalizationError("object keys must be strings")
            if i:
                out.append(",")
            out.append(serialize_string(key))
            out.append(":")
            _serialize(value[key], out)
        out.append("}")
    else:
        raise CanonicalizationError(f"unsupported JSON value type {type(value)!r}")


def canonicalize(value: Any) -> bytes:
    """Canonicalize an already-parsed JSON value to RFC 8785 UTF-8 bytes."""
    out: list = []
    _serialize(value, out)
    return "".join(out).encode("utf-8")


def canonicalize_text(text: str) -> bytes:
    return canonicalize(parse(text))
