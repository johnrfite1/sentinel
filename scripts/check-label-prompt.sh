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

ROOT="$(git rev-parse --show-toplevel)"
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
