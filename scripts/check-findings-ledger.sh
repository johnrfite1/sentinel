#!/usr/bin/env bash
# The D-055(e) findings arithmetic, DERIVED rather than hand-counted (D-057(1)).
#
# WHY THIS EXISTS. The first exit assessment reported "20 findings". There are 23 finding IDs.
# The error came from grouping R3-F5..F8 into one line and then counting lines — a hand count
# of a table that had already been silently transformed. John caught it and ruled that every
# total must be derived or mechanically checked from a canonical one-row-per-finding ledger,
# and that no second hand-counted summary may be introduced.
#
# So this script is the ONLY place the numbers come from. `docs/review-2026-08-18-d055e/`
# quotes them and points here; if a document and this script disagree, this script is right
# and the document is a defect.
#
# THE DISTINCTION THE ERROR TURNED ON, and it is the reason the vocabulary is now fixed:
#   FINDING          — one investigated defect, one row in the ledger. There are 23.
#   DISPOSITION ITEM — one decision John has to make. R3-F5..F8 share one repair pattern and
#                      may be decided together, so they collapse to ONE disposition item.
# **They are four findings and four regression obligations regardless.** Grouping is a
# convenience for deciding, never a reduction in what must be verified.
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
LEDGER="docs/review-2026-08-18-d055e/FINDINGS-LEDGER.tsv"

if [ ! -s "$LEDGER" ]; then
    echo "findings ledger: MISSING at $LEDGER — refusing to report totals from nothing."
    exit 1
fi

# FAIL CLOSED on a malformed ledger. A row count is only meaningful if every row parsed;
# silently skipping a bad line would under-count, which is the defect this file exists for.
malformed=0
while IFS=$'\t' read -r id rev adj verdict rsev asev cluster disp; do
    case "$id" in ''|'#'*) continue ;; esac
    if [ -z "$rev" ] || [ -z "$adj" ] || [ -z "$verdict" ] || [ -z "$disp" ]; then
        echo "  MALFORMED ROW: $id"
        malformed=$((malformed + 1))
    fi
done < "$LEDGER"
if [ "$malformed" -ne 0 ]; then
    echo "findings ledger: $malformed malformed row(s); totals not reported."
    exit 1
fi

rows() { grep -v '^#' "$LEDGER" | grep -v '^[[:space:]]*$'; }

total=$(rows | wc -l | tr -d ' ')
confirmed=$(rows | awk -F'\t' '$4=="CONFIRMED"' | wc -l | tr -d ' ')
refuted=$(rows | awk -F'\t' '$4=="REFUTED"' | wc -l | tr -d ' ')
critical=$(rows | awk -F'\t' '$4=="CONFIRMED" && $6=="CRITICAL"' | wc -l | tr -d ' ')
high=$(rows | awk -F'\t' '$4=="CONFIRMED" && $6=="HIGH"' | wc -l | tr -d ' ')
downgrades=$(rows | awk -F'\t' '$4=="CONFIRMED" && $5!=$6' | wc -l | tr -d ' ')
clustered=$(rows | awk -F'\t' '$7=="REPAIR-PATTERN"' | wc -l | tr -d ' ')
accepted=$(rows | awk -F'\t' '$8=="ACCEPTED-LIMIT"' | wc -l | tr -d ' ')
repair=$(rows | awk -F'\t' '$8=="REPAIR"' | wc -l | tr -d ' ')

# Disposition items: every finding, with the REPAIR-PATTERN cluster collapsed to one.
#
# TOTAL and CONFIRMED are DIFFERENT NUMBERS and the first version of this script conflated
# them — it computed the confirmed figure and asserted it against both of John's, and this
# check failed on its own first run. The refuted finding still occupies a disposition slot
# (somebody had to decide it was refuted), so total counts it and confirmed does not.
disposition_total=$((total - clustered + 1))
disposition=$((confirmed - clustered + 1))
# "Other" = confirmed, excluding the Critical, the three downgrades, and R4-F1.
other=$(rows | awk -F'\t' '$4=="CONFIRMED" && $6!="CRITICAL" && $5==$6 && $1!="R4-F1"' | wc -l | tr -d ' ')
other_items=$((other - clustered + 1))

echo "findings ledger (derived from $LEDGER, one row per finding):"
echo "  finding IDs                  : $total   ($confirmed confirmed, $refuted refuted)"
echo "  confirmed CRITICAL / HIGH    : $critical / $high"
echo "  severity downgrades          : $downgrades  (countersigned by John, D-057(2))"
echo "  REPAIR-PATTERN cluster       : $clustered findings = 1 disposition item, $clustered regression obligations"
echo "  disposition items            : $disposition_total total ($disposition confirmed)"
echo "  other confirmed findings     : $other   (excl. Critical, $downgrades downgrades, R4-F1)"
echo "  other disposition items      : $other_items   (same set, cluster grouped)"
echo "  dispositions                 : $repair repair · $accepted accepted-limit · $refuted no-action"

fail=0
expect() {
    if [ "$2" != "$3" ]; then echo "  MISMATCH: $1 is $2, John's ruling says $3"; fail=1; fi
}
# D-057(1)'s figures, asserted against the derivation so the ledger cannot drift from the ruling.
expect "finding IDs"             "$total"        23
expect "confirmed"               "$confirmed"    22
expect "refuted"                 "$refuted"      1
expect "disposition items total" "$disposition_total" 20
expect "disposition confirmed"   "$disposition"  19
expect "other confirmed"         "$other"        17
expect "other disposition items" "$other_items"  14
expect "cluster size"            "$clustered"    4

if [ "$fail" -ne 0 ]; then
    echo "findings ledger: DERIVED TOTALS DISAGREE WITH THE RECORDED RULING."
    exit 1
fi
echo "  all totals match D-057(1) as ruled"
