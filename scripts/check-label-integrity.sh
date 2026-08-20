#!/usr/bin/env bash
# A-064: the LABELS are pinned, not just the prompt that produced them.
#
# WHY THIS EXISTS. D-011(a) freezes the labelling PROMPT and `check-label-prompt.sh` enforces
# that. Nothing enforced anything about the LABELS. Round five's corpus lens demonstrated the
# consequence: change one word in `labeller-E.json` — `"BLOCK"` to `"ALLOW"` on the flagship
# fixture — regenerate the ablation report, and the §7.3 figures move from 38/8/1 to a perfect
# score while `./scripts/test.sh` prints GATE PASSED with byte-identical stage lines. A grep of
# `scripts/*.sh` for any reference to these files returned nothing.
#
# `labeller-E.json` IS the ground truth. D-003's kill criterion 3 names "fixture ground-truth
# labels" as evaluator-tamper territory and halts on it; the instructions were guarded and the
# measurements taken under them were not.
#
# WHY EVERY ARM AND NOT JUST E AND F. E and F are the labels of record and are what the finding
# named. Every other arm is audit trail — the contamination controls, the model-diversity arm,
# the duplicate — and an audit trail that can be edited silently is not one. Fixing the
# demonstration rather than the argument is this project's most-repeated defect.
#
# THREE FAILURE MODES, because a manifest that only re-hashes what it lists can be defeated by
# adding a file (the A-054 lesson: pin by COMPLEMENT, not by enumerating the bad cases):
#   1. a pinned file's content changed,
#   2. a pinned file is missing,
#   3. a label file exists that the manifest does not pin.
#
# IF THIS FAILS, DO NOT REPIN TO MAKE IT PASS. A moved label means the corpus's ground truth
# changed, which makes every §7.3 figure a measurement of something else. Restore the file, or
# take the re-label to John as a decision — D-043(b) binds re-labelling to pre-publication and
# names the trigger.
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
DIR="$ROOT/fixtures/corpus/labels"
PIN="$DIR/LABELS.sha256"

[ -d "$DIR" ] || { echo "label integrity: MISSING — $DIR does not exist"; exit 1; }
[ -f "$PIN" ] || { echo "label integrity: MISSING PIN — $PIN does not exist"; exit 1; }

fail=0

# 1 + 2: every pinned file must exist and hash to its pin.
while read -r expected name; do
    [ -z "${name:-}" ] && continue
    f="$DIR/$name"
    if [ ! -f "$f" ]; then
        echo "label integrity: MISSING — $name is pinned but not present"
        fail=1
        continue
    fi
    actual="$(shasum -a 256 "$f" | awk '{print $1}')"
    if [ "$actual" != "$expected" ]; then
        echo "label integrity: DRIFT — $name has changed."
        echo "  pinned : $expected"
        echo "  actual : $actual"
        echo "  This is the corpus's ground truth. Do NOT repin to make this pass."
        fail=1
    fi
done < "$PIN"

# 3: no label file may exist unpinned. Without this, the check is an allowlist of files
# somebody remembered, and a new `labeller-N.json` presented as evidence would be invisible.
for f in "$DIR"/*.json; do
    [ -e "$f" ] || continue
    name="$(basename "$f")"
    if ! awk '{print $2}' "$PIN" | grep -qx "$name"; then
        echo "label integrity: UNPINNED — $name exists but is not in LABELS.sha256"
        echo "  Add it deliberately: a labelling artifact nobody pinned is not evidence."
        fail=1
    fi
done

if [ "$fail" -ne 0 ]; then
    exit 1
fi

echo "label integrity: $(grep -c . "$PIN") labelling artifact(s) pinned, none unpinned (A-064)"
