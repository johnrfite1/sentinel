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
cd "$(git rev-parse --show-toplevel)"
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
