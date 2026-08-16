#!/usr/bin/env bash
# §7.5 Gate 5 — vendor honesty. The mechanical half of D-008, made enforceable.
#
# D-008 defines the gate in four parts:
#
#   (1) every cell of the capability matrix is documentation-only, dated, and linked to its
#       cited source;
#   (2) the "executed" and "faithfully emulated" columns of the §10.1 labeling scheme are
#       empty in v1 (per D-001);
#   (3) cells that are inference rather than quoted documentation are marked as inference;
#   (4) no claim OR LAYOUT implying empirical superiority over any named vendor appears in
#       any v1 artifact.
#
# and then says: "The empty-column condition is mechanically checkable." D-032 kept Gate 5 as
# an S2 pass condition on exactly that basis. This script is the check that sentence implies,
# and it had not been written — a gate declared mechanically checkable and never mechanised
# is an honour system with a stronger claim attached, which is worse than one without.
#
# WHAT THIS SCRIPT WILL NOT DO. Conditions (1) and (3) are judgements about whether a
# sentence fairly represents somebody else's product. The verification partition in HANDOFF
# gives public claims — "matrix, README, resume language" — autonomy NONE: John certifies
# them. So this script MEASURES those conditions and reports them as UNCERTIFIED. It never
# reports them as passed, and no agent may clear them by editing this file. That is the same
# shape as the workspace contrast guard, which reports UNMEASURED rather than a pass, and it
# exists so a green gate never silently means "an agent decided these claims were fair".
#
# Exit status is driven by the MECHANICAL conditions only. The certification section is
# printed on every run so it cannot be forgotten at the gate.

set -uo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

PROPOSAL="Sentinel_Protocol_Lab_Proposal_v0_2.md"
fail=0

# The vendors §2 and §10.1 name. Sentinel's honesty obligation is specifically about THESE
# parties, because they are the ones a reader could take a number to be a claim about.
VENDORS='Cobo|Coinbase|Circle|Privy|Safe|MetaMask|Sigil|Hypernative|Blockaid|Tenderly'

# MEASUREMENT ARTIFACTS are the files that carry numbers, evidence, or published claims. The
# rule below is that no NAMED vendor may appear in one of them.
#
# Everything else in the repository is a DELIBERATION record — the specification that
# analyses the market, the decision log that rules on it, the handoff, and the preserved
# review scratch. Those must be free to name vendors; forbidding it would make the project
# unable to record why D-001 cut executed comparisons. The exclusions are listed explicitly,
# with that reason, rather than left as a pattern nobody can audit.
#
# `docs/gate-5-vendor-audit.md` is on the list for the same reason and no other: it is the
# audit PREPARED FOR this gate, it carries no measurement of anything, and it cannot do its
# job — laying nine rows in front of John — without naming the nine parties they describe.
EXCLUDED='^(Sentinel_Protocol_Lab_Proposal_v0_2\.md|HANDOFF\.md|docs/decisions\.md|docs/session-state\.md|docs/gate-5-vendor-audit\.md|docs/review-2026-08-15/|scripts/check-vendor-honesty\.sh)'

artifacts() {
    git ls-files -- '*.md' '*.json' 'README*' | grep -Ev "$EXCLUDED"
}

echo "vendor honesty (§7.5 Gate 5, D-008) — mechanical conditions"

# --- (2) The empty-column condition -----------------------------------------
#
# D-001 cut executed vendor comparisons from v1, so no artifact may carry a comparison
# labelled anything but documentation-only. The two labels are searched for as literal
# strings, and the ONLY places they may legitimately appear are the sites that DEFINE the
# scheme. Those are declared here by exact file, because a bare "these words are banned"
# rule would fire on §10.1 itself and the fix would then be to weaken the rule.
label_hits=0
while IFS= read -r file; do
    if grep -Eiq 'executed directly|faithfully emulated' "$file"; then
        echo "  FAIL  $file labels a vendor comparison 'executed' or 'faithfully emulated'"
        echo "        D-001 cut executed comparisons from v1; §10.1's other two labels must stay empty."
        label_hits=$((label_hits + 1))
    fi
done < <(artifacts)

if [ "$label_hits" -eq 0 ]; then
    echo "  ok    no artifact claims an executed or emulated vendor comparison (D-001, D-008(2))"
else
    fail=1
fi

# The definition site must still exist. A check that passes because the scheme was deleted is
# a check measuring nothing — the same failure as a denylist whose entries cannot fire.
if ! grep -q 'Faithfully emulated from current documentation' "$PROPOSAL"; then
    echo "  FAIL  §10.1's labelling scheme is missing from $PROPOSAL — this check now proves nothing"
    fail=1
fi

# --- (4) No claim or layout implying empirical superiority -------------------
#
# Implemented as: a NAMED vendor may not appear in a measurement artifact at all.
#
# Stronger than scanning for comparative phrasing, and deliberately so. A phrase list is a
# denylist, and this project's most repeated defect is a denylist whose coverage is the
# spellings it happens to declare (A-028 F-3). More importantly D-008 forbids a LAYOUT that
# implies superiority, and layout has no vocabulary to scan for: a vendor's name in the same
# table as Sentinel's false-allow count implies the comparison whatever the prose says. §7.2's
# baseline is "representative" precisely so that no row of the ablation is about a real
# product.
vendor_hits=0
while IFS= read -r file; do
    if grep -Eq "\b($VENDORS)\b" "$file"; then
        echo "  FAIL  $file names a vendor in a measurement artifact:"
        grep -Enm3 "\b($VENDORS)\b" "$file" | sed 's/^/          /'
        vendor_hits=$((vendor_hits + 1))
    fi
done < <(artifacts)

if [ "$vendor_hits" -eq 0 ]; then
    echo "  ok    no named vendor appears in any measurement artifact (D-008(4))"
else
    echo "        A number beside a vendor's name is a claim about that vendor, whatever the"
    echo "        surrounding prose says. Rewrite to the capability class — §7.2's baseline is"
    echo "        called 'representative' for this reason."
    echo "        The exclusion list is for DELIBERATION records that carry no measurement, and"
    echo "        adding a file to it is a claim about that file. If the file reports a result,"
    echo "        excluding it is how this gate gets defeated."
    fail=1
fi

# --- §7.2's caveat must be present where the numbers are --------------------
#
# A-028 found the ablation report published its detection-contribution table without §7.2's
# own caveat anywhere in it. The caveat was added; this is what stops it being dropped again
# by a regeneration nobody reads.
#
# The expected text is EXTRACTED FROM THE SPECIFICATION, not transcribed here — the same
# shape as `check-type-strings.sh`, and for the same reason: a guard holding its own copy of
# the thing it guards can only ever confirm that copy. Whitespace is normalised on both
# sides because the caveat is a SENTENCE and the report is line-wrapped; comparing raw lines
# would fail on a rewrap, and the repair for that failure would be to weaken the guard.
norm() { tr '\n' ' ' <"$1" | tr -s ' '; }

CAVEAT="$(grep -F 'is not evidence that current vendors miss Case 3' "$PROPOSAL" | head -1 | sed 's/^ *//;s/ *$//')"
if [ -z "$CAVEAT" ]; then
    echo "  FAIL  §7.2's caveat is missing from $PROPOSAL, so there is nothing to enforce"
    fail=1
elif norm docs/ablation-report.md | grep -qF "$CAVEAT"; then
    echo "  ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it"
else
    echo "  FAIL  docs/ablation-report.md no longer carries §7.2's caveat:"
    echo "        \"$CAVEAT\""
    echo "        The report's own generator must emit it; do not paste it into the output file."
    fail=1
fi

# --- (1) and (3): the certification half, never reported as a pass ----------
#
# Parsed from the proposal rather than transcribed here, so the count cannot drift out of
# agreement with the table it describes.
echo
echo "vendor honesty — CERTIFICATION PENDING (John only; agents may not clear these)"

rows=$(awk '/^\| Category \| Examples \| Existing capability \| Consequence for Sentinel \|/{t=1;next} t&&/^\|---/{next} t&&/^\|/{n++} t&&!/^\|/{exit} END{print n+0}' "$PROPOSAL")
cited=$(awk '/^\| Category \| Examples \| Existing capability \| Consequence for Sentinel \|/{t=1;next} t&&/^\|---/{next} t&&/^\|/{if ($0 ~ /\[§13#[0-9]+ read [0-9]{4}-[0-9]{2}-[0-9]{2}\]/) n++} t&&!/^\|/{exit} END{print n+0}' "$PROPOSAL")

echo "  UNCERTIFIED  §2 capability table: $cited of $rows rows carry a per-cell source and access date"
echo "               D-008(1) requires every cell documentation-only, DATED, and LINKED to its"
echo "               cited source. §13 lists the sources; the cells do not reference them, and"
echo "               nothing records when each page was read. The marker this check counts is"
echo "               [§13#N read YYYY-MM-DD], appended to the capability cell."
echo "  UNCERTIFIED  §2 capability table: inference marking (D-008(3)) is a reading of each"
echo "               sentence against its source, which is John's certification, not a grep."
echo
echo "  These two are NOT failures of this script and NOT passes of Gate 5. They are the part"
echo "  of the gate the verification partition assigns to John: public claims, autonomy none."
echo "  docs/gate-5-vendor-audit.md holds the per-row audit prepared for that session."

echo
if [ "$fail" -ne 0 ]; then
    echo "vendor honesty: MECHANICAL CONDITIONS FAILED"
    exit 1
fi
echo "vendor honesty: mechanical conditions pass; certification pending (D-008(1),(3))"
