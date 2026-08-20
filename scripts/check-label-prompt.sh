#!/usr/bin/env bash
# D-011(a): the fixture-labelling prompt is frozen BEFORE the corpus is built, and its hash
# is committed. This is the mechanical half of that freeze.
#
# WHY THIS EXISTS RATHER THAN A NOTE IN THE DOCS. D-011(a)'s whole value is that nobody —
# including a well-meaning future session — can quietly retune the labelling instructions
# after seeing which fixtures the evaluator finds hard. A frozen prompt with no check is an
# honour system, and AGENTS.md is explicit that a durable project rule gets a mechanical
# guard rather than prose.
#
# IF THIS FAILS, THE FIX IS NOT TO REPIN THE HASH. A changed prompt means the corpus was
# labelled under instructions that no longer exist, which makes the disagreement rate
# reported at Gate S2 a measurement of nothing. Restore the file, or take a new frozen
# version to John as a decision — with a new file, a new hash, and a re-label of anything
# already labelled under the old one.
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
PROMPT="$ROOT/fixtures/corpus/LABELLING_PROMPT.md"
PINNED="$ROOT/fixtures/corpus/LABELLING_PROMPT.sha256"

if [ ! -f "$PROMPT" ]; then
    echo "label prompt: MISSING — $PROMPT does not exist (D-011a)"
    exit 1
fi

if [ ! -f "$PINNED" ]; then
    echo "label prompt: MISSING PIN — $PINNED does not exist (D-011a)"
    exit 1
fi

actual="$(shasum -a 256 "$PROMPT" | awk '{print $1}')"
expected="$(awk '{print $1}' "$PINNED")"

if [ "$actual" != "$expected" ]; then
    echo "label prompt: DRIFT — the frozen labelling prompt has changed."
    echo "  pinned : $expected"
    echo "  actual : $actual"
    echo "  D-011(a) freezes this file before the corpus build. Do NOT repin to make this"
    echo "  pass — restore the file, or take a new frozen version to John and re-label."
    exit 1
fi

echo "label prompt: frozen (${actual:0:16}…, D-011a)"
