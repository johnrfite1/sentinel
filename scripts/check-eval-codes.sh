#!/usr/bin/env bash
# D-031: every check the conformance engine declares must appear in §5.7.1 of the proposal.
#
# WHY. An independent labeller working only from the specification noticed that §5.7's prose
# never names the mandate-to-active-policy binding, and drew the consequence itself: an
# evaluator built from §5.7 alone omits it, and the wrong-policy fixture then ALLOWs. The
# omission fails OPEN. Measuring rather than assuming found eleven such checks, including all
# three binding checks §3.3(4) and §3.3(5) rest on.
#
# WHAT THIS ASSERTS, AND WHAT IT DOES NOT. Coverage, not correctness — that someone declared
# where a check belongs, not that the description is right. That is weaker than
# check-type-strings.sh, which compares two byte-exact strings, and the weakness is stated in
# §5.7.1 rather than glossed. It still beats prose nobody checks: this is the third time a
# spec-versus-implementation drift has been found by someone outside the build loop, and a
# guard is the only thing that stops a fourth.
#
# If this fails, add the check to §5.7.1 with a description — do not delete it from the
# engine to make the guard pass.
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

# SCOPED TO §5.7.1, THE SECTION THIS GUARD NAMES (R4-F3, D-055(e), CONFIRMED).
#
# Same defect as check-type-strings.sh: this grepped the WHOLE 84 KB document while printing
# "documented in §5.7.1", so a check documented only in §6 — or anywhere else — was certified
# as documented in a section that never mentioned it. Demonstrated by a reviewer.
SPEC_SECTION="$(mktemp)"
trap 'rm -f "$SPEC_SECTION"' EXIT
awk '/^#### 5\.7\.1 /{f=1;next} f && /^#{1,4} /{exit} f' "$SPEC" > "$SPEC_SECTION"
if [ ! -s "$SPEC_SECTION" ]; then
    echo "eval codes: COULD NOT ISOLATE §5.7.1 from the proposal."
    echo "  Refusing to report coverage against a section this guard could not find."
    exit 1
fi
CHECKS="$ROOT/ts/src/evaluate/checks.ts"

# The declared surface, taken from the engine's own EVAL_CODES array.
codes="$(sed -n '/^export const EVAL_CODES = \[/,/^\] as const;/p' "$CHECKS" \
    | grep -oE '"EVAL_[A-Z0-9_]+"' | tr -d '"' | sort -u)"

if [ -z "$codes" ]; then
    echo "eval codes: could not read EVAL_CODES from ${CHECKS#"$ROOT"/}"
    exit 1
fi

missing=""
total=0
for code in $codes; do
    total=$((total + 1))
    grep -q "$code" "$SPEC_SECTION" || missing="$missing $code"
done

if [ -n "$missing" ]; then
    n=$(echo $missing | wc -w | tr -d ' ')
    echo "eval codes: ${n} check(s) declared by the engine and absent from §5.7.1:"
    for c in $missing; do echo "    $c"; done
    echo "  Add them to §5.7.1 with a description. Do NOT remove them from the engine to pass."
    exit 1
fi

echo "eval codes: ${total}/${total} engine checks documented in §5.7.1 (D-031)"
