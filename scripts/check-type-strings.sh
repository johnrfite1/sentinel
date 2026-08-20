#!/usr/bin/env bash
# D-023: §5.8 of the proposal publishes the EIP-712 type strings verbatim. This checks that
# what the spec publishes is byte-identical to what the signer actually hashes.
#
# WHY THIS GUARD AND NOT A ONE-OFF CHECK. §5.8 exists because an independent reimplementation
# established that §5 was not buildable without these strings. A PUBLISHED type string that
# has drifted from the code is worse than an absent one: it is a confident, wrong answer that
# an implementer has no way to detect, because a wrong type string and an invalid signature
# are indistinguishable at the output. The repository already pins golden typehashes beside
# independently transcribed type strings for exactly this reason (A-013); this extends the
# same technique across the spec/code boundary.
#
# If this fails, work out which side is wrong before touching either. Changing the spec to
# match a drifted implementation, or vice versa, without deciding which is correct is how a
# schema quietly changes meaning.
set -uo pipefail

# --- Sentinel repository identity (D-060(2)) ---------------------------------
# Derived from THIS FILE's own location, never the caller's working directory, so a
# run from an unrelated directory or a foreign repository still inspects Sentinel.
# Every step is checked: `cd ""` returns 0 and does not abort even under `set -e`.
_sentinel_self="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)" || _sentinel_self=""
if [ -z "$_sentinel_self" ]; then
    echo "  FAIL  cannot resolve this script's own location; refusing." >&2; exit 2
fi
ROOT="$(cd -- "$_sentinel_self" 2>/dev/null && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR git rev-parse --show-toplevel 2>/dev/null)" || ROOT=""
if [ -z "$ROOT" ] || [ ! -e "$ROOT/scripts/test.sh" ] || [ ! -e "$ROOT/.githooks/pre-commit" ]; then
    echo "  FAIL  this script is not inside the Sentinel repository; refusing." >&2; exit 2
fi
cd "$ROOT" || { echo "  FAIL  cannot enter the Sentinel repository root; refusing." >&2; exit 2; }
SPEC="$ROOT/Sentinel_Protocol_Lab_Proposal_v0_2.md"

# SCOPED TO §5.8, THE SECTION THIS GUARD NAMES (R4-F3, D-055(e), CONFIRMED).
#
# THE ARGUMENT: **a guard that says "published in §5.8" must read §5.8.** This searched the
# whole 84 KB document and took `head -1`. Because the file's section order is NOT monotonic
# (§5.9 precedes §5.8), an earlier matching line anywhere above §5.8 wins — so a reviewer
# demonstrated the guard printing "6/6 published in §5.8 match eip712.ts exactly" while §5.8
# published a transposed `EIP712Domain` whose typehash differs. The guard's own header calls
# that outcome "worse than an absent one".
#
# NOT CURRENTLY LIVE: each type string occurs exactly once today, inside §5.8, so the guard has
# been reading the right lines. It took two edits — the transposition plus a decoy earlier in
# the file — to produce the defeat. This is an instrument defect, not a live false claim, and
# the distinction is recorded rather than blurred.
SPEC_SECTION="$(mktemp)"
trap 'rm -f "$SPEC_SECTION"' EXIT
awk '/^### 5\.8 /{f=1;next} f && /^#{1,4} /{exit} f' "$SPEC" > "$SPEC_SECTION"
if [ ! -s "$SPEC_SECTION" ]; then
    echo "type strings: COULD NOT ISOLATE §5.8 from the proposal."
    echo "  Refusing to certify a section this guard could not find — an empty scope would"
    echo "  make every comparison vacuously fail, or worse, pass against nothing."
    exit 1
fi
SRC="$ROOT/ts/src/signer/eip712.ts"

fail=0
checked=0

for name in EIP712Domain MandatePayload PolicyPayload ActionPayload \
            DecisionReceiptPayload OverrideAuthorizationPayload; do
    # The spec publishes each as an indented literal line; the source as a quoted string.
    # EXACTLY ONE PUBLICATION PER TYPE, not the first of several (R4-F3 residual, D-057(5)).
    #
    # Scoping to §5.8 closed the cross-section decoy. It did NOT close a decoy placed INSIDE
    # §5.8 above the real line, because `head -1` still silently picks a winner. A section that
    # publishes two different strings for one type is itself the defect — there is no correct
    # way to choose between them — so this refuses rather than choosing.
    spec_hits="$(grep -cE "^ {4}${name}\([^)]*\)$" "$SPEC_SECTION")"
    if [ "$spec_hits" -gt 1 ]; then
        echo "type strings: §5.8 publishes ${spec_hits} different lines for ${name}."
        echo "  A section cannot publish a type string twice and have both be normative."
        echo "  Refusing to pick one. Remove the duplicate."
        fail=1
        continue
    fi
    spec_line="$(grep -oE "^ {4}${name}\([^)]*\)$" "$SPEC_SECTION" | head -1 | sed 's/^ *//')"
    src_line="$(grep -oE "\"${name}\([^\"]*\)\"" "$SRC" | head -1 | sed 's/^"//; s/"$//')"

    if [ -z "$spec_line" ]; then
        echo "type strings: §5.8 does not publish ${name}"
        fail=1
        continue
    fi
    if [ -z "$src_line" ]; then
        echo "type strings: ${name} not found in ts/src/signer/eip712.ts"
        fail=1
        continue
    fi
    if [ "$spec_line" != "$src_line" ]; then
        echo "type strings: DRIFT in ${name}"
        echo "  spec  : $spec_line"
        echo "  source: $src_line"
        fail=1
        continue
    fi
    checked=$((checked + 1))
done

if [ "$fail" -ne 0 ]; then
    echo "  A published type string that disagrees with the code is a confident wrong answer:"
    echo "  a wrong type string and an invalid signature are indistinguishable at the output."
    exit 1
fi

echo "type strings: ${checked}/6 published in §5.8 match eip712.ts exactly (D-023)"
