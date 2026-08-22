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
# CALLER GIT OVERRIDES ARE REMOVED ONCE, HERE, BEFORE ANY BODY-LEVEL GIT CALL (12-F2).
# Scrubbing only the identity probe left every later `git` inheriting the caller's
# environment: GIT_DIR alone made this guard report clean over a live credential, and made
# install-hooks write into a victim repository. GIT_PREFIX is included although inert on
# git 2.50.1 — an inert variable today is not a guarantee tomorrow.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
cd "$ROOT"

PROPOSAL="Sentinel_Protocol_Lab_Proposal_v0_2.md"
fail=0

# The vendors §2 and §10.1 name. Sentinel's honesty obligation is specifically about THESE
# parties, because they are the ones a reader could take a number to be a claim about.
#
# TEN SPELLINGS, AND THAT IS A REAL LIMIT RATHER THAN A COMPLETE RULE. D-008 forbids claims
# about "any named vendor"; this list is the ten §2 and §10.1 name. Fireblocks, Turnkey, Dfns,
# Anchorage and everything else pass. An independent review was right to point out that A-031
# described this construction as categorically stronger than a phrase denylist when it is a
# denylist of a different column — stronger against LAYOUT, which was the argument, and no
# stronger against an unlisted name. The honest reading: this catches the vendors the project
# has actually written about, which is the population D-008's artifacts draw from, and a new
# vendor entering an artifact is a thing a human has to notice.
#
# THE ROSTER IS THE TWO VARIABLES BELOW, AND THERE IS DELIBERATELY NO THIRD ONE (A-049). A single
# `VENDORS=` list used to live on this line, directly under the paragraph above. When the case
# split landed (A-047) it became dead — expanded nowhere — while remaining the only thing a
# reader would take to be the roster, so a maintainer adding an eleventh vendor here would have
# changed nothing and got a green gate. An independent review demonstrated exactly that with
# `Fireblocks`. It is deleted rather than kept in sync, because two lists that must agree is the
# defect this file already carries a warning about. **Add new vendors to ONE of the two lists
# below, choosing by whether the token means anything but a vendor.**

# CASE. Until 2026-08-16 the scan below was `grep -Eq` — case-SENSITIVE — while the §10.1 label
# scan forty lines above is `grep -Eiq`. An adversarial review defeated it with one token: a
# markdown table row reading `| coinbase | 34 | no |` passed, and capitalising that single word
# and nothing else failed the guard. Lowercase names are idiomatic in table cells and CSV-ish
# data, so this was not even an adversarial spelling — it is how somebody would naturally type
# it (A-047).
#
# THE FIX IS NOT `-i` ON THE WHOLE LIST. `Safe` is an ordinary English word: case-insensitively
# it occurs in ELEVEN in-scope files, `docs/ablation-report.md` ("costly-but-safe") among them —
# so a blanket `-i` fires on the flagship measurement artifact on the first run, and this file's
# own header says a guard that cries wolf gets reverted rather than obeyed. The full enumeration
# is below and is stated ONCE, deliberately: this paragraph carried a second copy of it until
# 2026-08-17, the second copy was the one that was wrong, and correcting only the other was the
# "one site of two" defect for the third time in two days. So the list is split:
# NINE of the ten are matched in ANY casing. Only `Safe` is not, and the exception is measured
# rather than assumed: over this guard's own artifact set, with the same `\b` form it uses,
# case-insensitive matching hits **safe 11 files** — `docs/ablation-report.md`'s "costly-but-safe",
# `contracts/src/SentinelVault.sol`, **five** `ts/src/**`, two `ts/test/**`, `verifier/REPORT.md`
# and `verifier/refusal.py` — versus **circle 0 and sigil 0**. (This enumeration said "four
# `ts/src`" until 2026-08-17; two reviewers caught it independently, inside a claim labelled
# "measured rather than assumed". The totals and the conclusion were right; the list was not.)
VENDORS_ANYCASE='Cobo|Coinbase|Circle|Privy|MetaMask|Sigil|Hypernative|Blockaid|Tenderly'
VENDORS_EXACTCASE='Safe|SAFE'
#
# HOW THIS LIST GOT HERE, because the reasoning was wrong twice and the corrections are the
# useful part. A-047 split the roster and put THREE names in the exact-case list while its own
# comment said "two of the ten spellings are ordinary English words" — `Sigil` entered with no
# argument at all. A-048 corrected the prose but left the code, and stated the residual as
# "lower case", which was also wrong: `grep -Eq` is exact-case in BOTH directions, so `SAFE`,
# `CIRCLE` and `SIGIL` in capitals evaded too, and all-caps is this repository's own emphasis
# idiom. A-049 fixes the code: `Circle` and `Sigil` move to any-case at zero measured cost, and
# `Safe` carries its uppercase spelling explicitly.
#
# RESIDUAL, NARROWED AND STATED PRECISELY: `safe` and mixed-case oddities of it (`sAfE`) still
# pass, because "safe" is an ordinary English word that occurs eleven times in scope and a guard
# that cries wolf gets reverted rather than obeyed. That is one word in one casing family, down
# from three words in every casing but one. A vendor named in an artifact as the lower-case word
# "safe" remains something a human has to notice — the same residual this file already declares
# for the unlisted vendors above.

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
#
# `docs/review-2026-08-15/` IS NOT EXCLUDED WHOLESALE, and the correction is the point. The
# first version excluded the whole directory as "review scratch"; the same review pointed out
# that `gate-s2-hard-gates-draft.md` inside it is a superseded gate-evidence pack containing a
# false-allow table — a file that reports a result, which this script's own error message
# calls the way the gate gets defeated. Only `artifacts/` (reproduction rigs and campaign
# data) is excluded now.
# ANCHORED AT BOTH ENDS. The first version anchored `^` only, which made every entry a PREFIX
# match: `docs/decisions.md.gate-5-evidence` — an untracked file one `git add -A` from being
# published — inherited decisions.md's exemption and could carry a head-to-head false-allow
# table naming three vendors plus both banned §10.1 labels, defeating conditions (2) and (4) at
# once. Found by an independent adversarial review, 2026-08-16, with that exact file. Directory
# entries keep the prefix form deliberately; file entries now end at `$`.
EXCLUDED='^(Sentinel_Protocol_Lab_Proposal_v0_2\.md|HANDOFF\.md|docs/decisions\.md|docs/session-state\.md|docs/gate-5-vendor-audit\.md|docs/v1-1-register\.md|scripts/check-vendor-honesty\.sh)$|^docs/review-2026-08-15/artifacts/'

# CONDITION (2) HAS A DIFFERENT, MUCH NARROWER EXCLUSION LIST, and the split is the point.
#
# The list above exists because a DELIBERATION record cannot discuss the market without naming
# the parties. That argument is about condition (4) — vendor names — and about nothing else. The
# first version applied it to the §10.1 label scan too, so appending "Sentinel was **executed
# directly** against every vendor above and led on all nine rows" to the Gate 5 audit passed the
# gate. That file is the packet John rules from.
#
# Narrowed to the four files that DEMONSTRABLY need it, measured rather than assumed: the
# proposal defines the scheme in §10.1; `decisions.md` records D-001's text, which is the ruling
# that cut executed comparisons; the Gate 5 audit quotes the labels while explaining the
# condition; and this script holds the pattern. HANDOFF.md, session-state.md, v1-1-register.md,
# the S2 evidence pack and the review artifacts were all on the old list and contain neither
# label — they are now scanned.
#
# THE RESIDUAL EXPOSURE, STATED BECAUSE IT IS NOT MECHANICALLY CLOSED AND WAS RE-TESTED AFTER
# THIS REPAIR. A guard cannot tell "labelling a comparison executed" from "recording that
# executed comparisons were cut", and those are the same words. So condition (2) is unenforced
# inside those four files, one of which is the packet John rules Gate 5 from.
#
# DEMONSTRATED 2026-08-16 and still true: appending "Sentinel was executed directly against
# every vendor above" to `docs/gate-5-vendor-audit.md` passes this gate. Of the twelve exploits
# an adversarial review built against these two guards, this is the ONE that survives the fix.
# Reading that file is the only control, which is the honest description of an honour system.
EXCLUDED_LABELS='^(Sentinel_Protocol_Lab_Proposal_v0_2\.md|docs/decisions\.md|docs/gate-5-vendor-audit\.md|scripts/check-vendor-honesty\.sh)$'

# TRACKED **AND** UNTRACKED-BUT-NOT-IGNORED, and the second half is not belt-and-braces.
#
# The first version scanned `git ls-files` alone, which meant a brand-new artifact was
# invisible until the commit that added it — so the check passed while the file was being
# written, and HEAD went red immediately afterwards. That happened on this script's own first
# use: `docs/gate-s2-evidence.md` quoted the two §10.1 label strings, passed while untracked,
# and failed the moment it was committed. A guard that only inspects what is already published
# reports on the past.
#
# The cost is that an unignored scratch file in the working tree can fail the gate. That is
# the right side to err on for a check about publication honesty: an untracked file in this
# tree is one `git add -A` away from being published.
#
# THE FILE SET IS EVERY TEXT ARTIFACT, NOT JUST MARKDOWN AND JSON.
#
# The first version globbed '*.md' '*.json' 'README*' and an independent review named three
# things it therefore could not see, each of which carries numbers or is itself S2 evidence:
# `scripts/test.sh`'s coverage-boundary heredoc (printed on every gate run, carrying the
# false-allow figures), `fixtures/injection/canary-history.jsonl` (which `.json` does not
# match, and which D-007 requires IN the evidence bundle), and the verifier's Python. A guard
# whose scope is a file extension is a guard somebody routes around by choosing a file.
#
# BINARY SKIPPING IS BY PATH, NOT BY CONTENT. `grep -Iq .` treats any file containing a NUL as
# binary, so appending one NUL byte to a markdown file removed it from this scan entirely while
# leaving it perfectly readable — demonstrated by an independent review, 2026-08-16. The test is
# now an extension allowlist for the formats that carry binary data in this repository; anything
# else is scanned as text whatever bytes it holds.
artifacts() {
    local excl="${1:-$EXCLUDED}"
    {
        git ls-files
        git ls-files --others --exclude-standard
    } | sort -u | grep -Ev "$excl" | while IFS= read -r f; do
        case "$f" in
            *.png|*.jpg|*.jpeg|*.gif|*.pdf|*.zip|*.gz|*.wasm|*.ico) continue ;;
        esac
        [ -f "$f" ] && printf '%s\n' "$f"
    done
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
done < <(artifacts "$EXCLUDED_LABELS")

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
    if grep -Eiq "\b($VENDORS_ANYCASE)\b" "$file" || grep -Eq "\b($VENDORS_EXACTCASE)\b" "$file"; then
        echo "  FAIL  $file names a vendor in a measurement artifact:"
        { grep -Einm3 "\b($VENDORS_ANYCASE)\b" "$file"
          grep -Enm3  "\b($VENDORS_EXACTCASE)\b" "$file"; } | sort -t: -k1,1n | head -3 | sed 's/^/          /'
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
# The expected text is EXTRACTED FROM §7.2, not transcribed here — the same shape as
# `check-type-strings.sh`, and for the same reason: a guard holding its own copy of the thing
# it guards can only ever confirm that copy. Both sides are split into logical paragraphs,
# then whitespace-normalised within each paragraph. That tolerates hard wraps without letting
# a tail fragment of the caveat stand in for the whole paragraph.
VH_SECTION="$(mktemp)"
VH_PROPOSAL_PARAS="$(mktemp)"
VH_REPORT_PARAS="$(mktemp)"
trap 'rm -f "$VH_SECTION" "$VH_PROPOSAL_PARAS" "$VH_REPORT_PARAS"' EXIT

normalize_paragraphs() {
    awk '
        function flush_paragraph() {
            if (paragraph != "") {
                gsub(/[[:space:]]+/, " ", paragraph)
                sub(/^ /, "", paragraph)
                sub(/ $/, "", paragraph)
                print paragraph
                paragraph = ""
            }
        }
        /^[[:space:]]*$/ { flush_paragraph(); next }
        {
            line = $0
            gsub(/[[:space:]]+/, " ", line)
            sub(/^ /, "", line)
            sub(/ $/, "", line)
            paragraph = (paragraph == "" ? line : paragraph " " line)
        }
        END { flush_paragraph() }
    ' "$1"
}

CAVEAT_PHRASE='is not evidence that current vendors miss Case 3'
CAVEAT=""
if python3 "$ROOT/scripts/extract-markdown-section.py" "$PROPOSAL" \
        '### 7.2 Fair Baselines' > "$VH_SECTION"; then
    normalize_paragraphs "$VH_SECTION" > "$VH_PROPOSAL_PARAS"
    normalize_paragraphs docs/ablation-report.md > "$VH_REPORT_PARAS"
    caveat_hits="$(grep -cF "$CAVEAT_PHRASE" "$VH_PROPOSAL_PARAS")"
    if [ "$caveat_hits" -eq 1 ]; then
        CAVEAT="$(grep -F "$CAVEAT_PHRASE" "$VH_PROPOSAL_PARAS")"
    elif [ "$caveat_hits" -eq 0 ]; then
        echo "  FAIL  §7.2's caveat is missing from $PROPOSAL, so there is nothing to enforce"
        fail=1
    else
        echo "  FAIL  §7.2's caveat is ambiguous: ${caveat_hits} logical paragraphs carry its identifying phrase"
        fail=1
    fi
else
    fail=1
fi

if [ -n "$CAVEAT" ]; then
    if grep -qF "$CAVEAT" "$VH_REPORT_PARAS"; then
        echo "  ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it"
    else
        echo "  FAIL  docs/ablation-report.md no longer carries §7.2's caveat:"
        echo "        \"$CAVEAT\""
        echo "        The report's own generator must emit it; do not paste it into the output file."
        fail=1
    fi
fi

# --- (1) and (3): the certification half, never reported as a pass ----------
#
# Parsed from the proposal rather than transcribed here, so the count cannot drift out of
# agreement with the table it describes.
echo
echo "vendor honesty — D-008(1) and (3): John's to certify; agents may not clear these"

# THE MARKER IS COUNTED IN THE CAPABILITY CELL, NOT ANYWHERE IN THE ROW.
#
# The first version tested `$0` while its own message said "appended to the capability cell", so
# a marker sitting in "Consequence for Sentinel" would have counted. Nothing exploited it — the
# count was 0 of 9 for the guard's whole life before certification — but a guard whose message
# and whose test disagree is this project's most repeated defect, and it was recorded in the
# Gate 5 packet as owed. Field 4 under `-F'|'` is the capability cell: a leading empty field
# precedes Category(2), Examples(3), Existing capability(4), Consequence(5).
rows=$(awk -F'|' '/^\| Category \| Examples \| Existing capability \| Consequence for Sentinel \|/{t=1;next} t&&/^\|---/{next} t&&/^\|/{n++} t&&!/^\|/{exit} END{print n+0}' "$PROPOSAL")
cited=$(awk -F'|' '/^\| Category \| Examples \| Existing capability \| Consequence for Sentinel \|/{t=1;next} t&&/^\|---/{next} t&&/^\|/{if ($4 ~ /\[§13#[0-9]+ read [0-9]{4}-[0-9]{2}-[0-9]{2}\]/) n++} t&&!/^\|/{exit} END{print n+0}' "$PROPOSAL")

# D-008(1) has a mechanical half — dated and linked — and this script may report that half as
# MET when it is met. It may not report the judgement half, which is the next block.
# THE MARKER'S SHAPE IS NOT ITS LINKAGE. D-008(1) says "dated AND LINKED to its cited source",
# and the first version checked only that `[§13#N read YYYY-MM-DD]` matched — so `[§13#997 read
# 1999-01-01]` counted as a citation though §13 has no entry 997. Two independent reviews found
# this separately on 2026-08-16. Every N is now resolved against §13's actual entry numbers.
declared=$(awk '/^## 13\. Source Notes/{t=1;next} t&&/^## 14\./{exit} t&&/^[0-9]+\. \[/{sub(/\..*/,"");print}' "$PROPOSAL" | sort -un)
badrefs=""
for n in $(awk -F'|' '/^\| Category \| Examples \| Existing capability \| Consequence for Sentinel \|/{t=1;next} t&&/^\|---/{next} t&&/^\|/{print $4} t&&!/^\|/{exit}' "$PROPOSAL" \
           | grep -oE '§13#[0-9]+' | grep -oE '[0-9]+' | sort -un); do
    printf '%s\n' "$declared" | grep -qx "$n" || badrefs="$badrefs $n"
done
if [ -n "$badrefs" ]; then
    echo "  FAIL  §2 cites §13 entries that do not exist:$badrefs"
    echo "        D-008(1) requires the cell be LINKED to its cited source. A well-formed marker"
    echo "        pointing at nothing is a citation in shape only. Add the source to §13."
    fail=1
fi

if [ "$cited" -eq "$rows" ] && [ "$rows" -gt 0 ]; then
    echo "  ok    §2 capability table: $cited of $rows rows carry a marker resolving to a §13 entry"
    echo "        D-008(1)'s mechanical half: dated, and linked to a source that exists. A row"
    echo "        added later without [§13#N read YYYY-MM-DD] in its capability cell FAILS this"
    echo "        gate, as does one citing an entry §13 does not have. The count is a ratchet."
else
    echo "  FAIL  §2 capability table: only $cited of $rows rows carry a per-cell source and date"
    echo "        D-008(1) requires every cell documentation-only, DATED, and LINKED to its cited"
    echo "        source. The marker this check counts is [§13#N read YYYY-MM-DD], in the"
    echo "        CAPABILITY cell. Cite the row; do not delete it to make the count agree."
    fail=1
fi

# CONDITION (3) IS REPORTED BY RECORD, NEVER BY THIS SCRIPT'S OWN JUDGEMENT.
#
# Whether a sentence fairly describes somebody else's product is John's under the verification
# partition. What is mechanical is whether a NAMED certification exists in the document. So this
# looks for the certification line §2 carries and reports the decision id it names. It does not
# and cannot check that the certification is correct.
# SCOPED TO §2, AND THE FIRST VERSION WAS NOT.
#
# It grepped the whole 71 KB proposal, so the one line at the gate saying a human certified the
# public claims could be satisfied by a quotation, an example, or a fenced code block anywhere
# in the file. An independent review demonstrated it on 2026-08-16 by deleting the real
# certification from §2 and planting the string inside a code block in §14 introduced as "a
# format we considered and rejected" — with a 1999 date and a decision id that does not exist.
# The guard reported certified.
#
# THIS IS THE SAME DEFECT AS THE `$0`-VERSUS-FIELD-4 BUG FIXED TWENTY LINES ABOVE, committed in
# the same session, by the same author, while writing a comment congratulating itself for
# catching it. That is worth leaving in the file: the pattern is not rare and knowing about it
# is not protection.
sec2=$(awk '/^## 2\. Need, Market Reality, and First User/{t=1} t&&/^## 3\./{exit} t' "$PROPOSAL")
certline=$(printf '%s\n' "$sec2" | grep -oE '^\*Certified by John at the Gate 5 session, [0-9]{4}-[0-9]{2}-[0-9]{2} \(D-[0-9]+\)\.\*' | head -1)
# THE EXPIRY IS NOW AN INSTRUMENT, NOT A SENTENCE.
#
# D-038 declares the certification stale on ANY edit to the §2 table, and the first version
# enforced that by PRINTING it — which is a warning, not a detection. A review pointed out that
# `check-label-prompt.sh` had the enforcement pattern one file over. This pins the hash of the
# table John actually certified: the rows plus the certification line, ignoring surrounding
# prose. Edit a capability cell and the certification stops being reported, whatever the
# sentence in §2 still says.
#
# TO RE-CERTIFY: John rules on the changed table, then this constant is updated in the same
# commit that changes §2. An agent updating it without a ruling is forging a certification.
CERTIFIED_TABLE_SHA="c9034750e56b8801be7cd31cce33c42caad209013a61ed7082155db33903959c"
table_sha=$(awk '/^## 2\. Need, Market Reality, and First User/{t=1} t&&/^## 3\./{exit} t&&/^\|/{print} t&&/^\*Certified by John/{print}' "$PROPOSAL" | shasum -a 256 | awk '{print $1}')

if [ -n "$certline" ] && [ "$table_sha" = "$CERTIFIED_TABLE_SHA" ]; then
    echo "  ok    §2 capability table: inference marking (D-008(3)) certified by record —"
    echo "        ${certline}"
    echo "        The table hashes to the one certified. THIS SCRIPT DID NOT AND CANNOT CHECK"
    echo "        THAT THE CERTIFICATION IS RIGHT — it checks that a named certification exists"
    echo "        in §2 and that §2 has not changed since. Whether a sentence fairly describes"
    echo "        somebody else's product is John's, and no hash speaks to it."
elif [ -n "$certline" ]; then
    echo "  FAIL  §2 capability table: the certification is STALE. D-038 certified a table that"
    echo "        hashed to ${CERTIFIED_TABLE_SHA%%????????????????????????????????????????????????????????}…; §2 now hashes to ${table_sha%%????????????????????????????????????????????????????????}…"
    echo "        The certification line is still present and no longer describes this table."
    echo "        Gate 5 is NOT MET until John rules on the change. Updating the pinned hash"
    echo "        without a ruling forges a certification — it is not a repair."
    fail=1
elif [ -n "$CERTIFIED_TABLE_SHA" ]; then
    # A pinned hash is this repository asserting that a certification HAPPENED. If the line is
    # then absent from §2, that is not "not yet certified" — it is a certification that was
    # removed, and letting it report as merely uncertified would turn a MET gate back into an
    # open one silently. Found while re-testing the §2-scoping repair: the scoping worked, and
    # the removal path underneath it did not fail.
    echo "  FAIL  §2 capability table: a certification is pinned (D-038) but §2 carries no"
    echo "        certification line. Gate 5 was MET and is not now."
    echo "        A line elsewhere in the proposal does not count — quotations, examples and"
    echo "        code blocks were accepted until 2026-08-16, and are not."
    fail=1
else
    echo "  UNCERTIFIED  §2 capability table: inference marking (D-008(3)) is a reading of each"
    echo "               sentence against its source, which is John's certification, not a grep."
    echo "               No certification line found in §2."
fi
echo
echo "  Neither line above is this script deciding a public claim. The verification partition"
echo "  gives those to John: public claims, autonomy none. docs/gate-5-vendor-audit.md holds the"
echo "  per-row audit and the certification packet the Gate 5 session ruled from."

echo
if [ "$fail" -ne 0 ]; then
    echo "vendor honesty: MECHANICAL CONDITIONS FAILED"
    exit 1
fi
echo "vendor honesty: mechanical conditions pass; D-008(1) met and (3) certified by record"
