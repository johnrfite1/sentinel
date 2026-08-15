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

ROOT="$(git rev-parse --show-toplevel)"
SPEC="$ROOT/Sentinel_Protocol_Lab_Proposal_v0_2.md"
SRC="$ROOT/ts/src/signer/eip712.ts"

fail=0
checked=0

for name in EIP712Domain MandatePayload PolicyPayload ActionPayload \
            DecisionReceiptPayload OverrideAuthorizationPayload; do
    # The spec publishes each as an indented literal line; the source as a quoted string.
    spec_line="$(grep -oE "^ {4}${name}\([^)]*\)$" "$SPEC" | head -1 | sed 's/^ *//')"
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
