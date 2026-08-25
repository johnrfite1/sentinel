"""reasonCodesHash, per §5.4 as amended by D-022.

Construction, from the amended text:

    The committed set is the union of the evaluator's reason codes and the
    isolated signer's own findings. That set is de-duplicated, sorted in
    ascending byte order of the identifier, joined with a single "\\n" (U+000A)
    between elements, encoded UTF-8, and hashed with keccak256. The empty set
    hashes to keccak256("").

Two implementation notes that the amended text does not make explicit, both
recorded in REPORT.md F-3:

1. The union is a *production* rule describing how the signer built the set.
   The verifier is handed the already-unioned `reasonCodes` array, so it hashes
   that array and checks `signerFindings` is a subset of it as a separate
   invariant. Re-unioning the two published arrays instead would make the
   removal of any code that also appears in `signerFindings` undetectable,
   because the union would silently restore it.

2. The stated pattern must be matched with absolute anchors. `^...$` as written
   does not exclude the delimiter in every language (see `validate`).
"""

import re
from typing import Iterable, List, Sequence

from keccak import keccak256

DELIMITER = "\n"

# §5.4: ^[A-Za-z0-9_.:-]{1,64}$
#
# Deliberately compiled WITHOUT the `^`/`$` anchors the spec prints, and applied
# with fullmatch. In Python, re.match(r"^...$", "EVAL_OK\n") returns a match --
# `$` matches before a trailing newline -- so the spec's literal pattern admits
# an identifier ending in the very delimiter the pattern exists to exclude. In
# Ruby it is worse: `^`/`$` are line anchors unconditionally, so "EVIL\nINJECTED"
# matches, and {"EVIL\nINJECTED"} then hashes identically to {"EVIL",
# "INJECTED"} -- a collision between two distinct committed sets.
REASON_CODE_RE = re.compile(r"[A-Za-z0-9_.:-]{1,64}")


class ReasonCodeError(ValueError):
    pass


def validate(identifier) -> str:
    """Validate one reason-code identifier. Fails; never sanitises."""
    if not isinstance(identifier, str):
        raise ReasonCodeError(
            f"reason code must be a string, got {type(identifier).__name__}: "
            f"{identifier!r}"
        )
    if REASON_CODE_RE.fullmatch(identifier) is None:
        raise ReasonCodeError(
            f"reason code {identifier!r} does not match "
            r"^[A-Za-z0-9_.:-]{1,64}$ (matched with absolute anchors); "
            "refusing to sanitise"
        )
    return identifier


def validate_all(identifiers: Iterable) -> List[str]:
    return [validate(i) for i in identifiers]


def committed_set(reason_codes: Sequence) -> List[str]:
    """De-duplicate and sort by ascending byte order of the identifier.

    The pattern restricts identifiers to ASCII, so byte order, UTF-8 byte order
    and Python's code-point ordering all coincide. Sorting the encoded bytes
    anyway, so the code states the rule the spec states rather than relying on
    that coincidence holding if the pattern is ever widened.
    """
    validate_all(reason_codes)
    return sorted(set(reason_codes), key=lambda c: c.encode("utf-8"))


def preimage(reason_codes: Sequence) -> bytes:
    return DELIMITER.join(committed_set(reason_codes)).encode("utf-8")


def reason_codes_hash(reason_codes: Sequence) -> bytes:
    """keccak256 of the canonical joined form. The empty set gives keccak256("")."""
    return keccak256(preimage(reason_codes))


def reason_codes_hash_hex(reason_codes: Sequence) -> str:
    return "0x" + reason_codes_hash(reason_codes).hex()
