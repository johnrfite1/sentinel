#!/usr/bin/env bash
# Print the gate's suite floors FROM THE GATE (R4-F4, D-055(e)).
#
# WHY. `docs/session-state.md` §3 kept a hand-maintained copy of the suite counts and drifted
# from the gate's constants five times — most recently publishing 507/198 while the floors were
# 513/209, which would have led a maintainer to LOWER a floor. John's ruling: remove the
# duplication or mechanically bind it. The duplication is removed; this is the binding.
#
# THIS PRINTS THE FLOORS, NOT THE COUNTS. A floor is what the gate asserts; the count is what a
# run measures. They are equal today and that is not guaranteed tomorrow — run the gate for the
# counts. Stating this because reporting a floor as a measurement is the defect one layer up.
set -uo pipefail
# --- Sentinel repository identity (D-060(2)) ---------------------------------
# Derived from THIS FILE's own location, never the caller's working directory, so a
# run from an unrelated directory or a foreign repository still inspects Sentinel.
# Every step is checked: `cd ""` returns 0 and does not abort even under `set -e`.
_sentinel_self="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)" || _sentinel_self=""
if [ -z "$_sentinel_self" ]; then
    echo "  FAIL  cannot resolve this script's own location; refusing." >&2; exit 2
fi
SENTINEL_ROOT="$(cd -- "$_sentinel_self" 2>/dev/null && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR git rev-parse --show-toplevel 2>/dev/null)" || SENTINEL_ROOT=""
if [ -z "$SENTINEL_ROOT" ] || [ ! -e "$SENTINEL_ROOT/scripts/test.sh" ] || [ ! -e "$SENTINEL_ROOT/.githooks/pre-commit" ]; then
    echo "  FAIL  this script is not inside the Sentinel repository; refusing." >&2; exit 2
fi
cd "$SENTINEL_ROOT" || { echo "  FAIL  cannot enter the Sentinel repository root; refusing." >&2; exit 2; }
GATE=scripts/test.sh
get() { grep -E "^$1=" "$GATE" | head -1 | cut -d= -f2; }
missing=0
for v in FOUNDRY_MIN_TESTS TS_MIN_TESTS VERIFIER_MIN_TESTS VERIFIER_MIN_SAMPLES \
         VERIFIER_MIN_TAMPER VERIFIER_MIN_TAMPER_MODES; do
    val="$(get "$v")"
    if [ -z "$val" ]; then echo "  MISSING: $v is not defined in $GATE"; missing=1
    else printf "  %-26s %s\n" "$v" "$val"; fi
done
[ "$missing" -eq 0 ] || { echo "suite floors: a floor the gate asserts could not be read."; exit 1; }
echo "suite floors: read from $GATE, which is the only copy."
