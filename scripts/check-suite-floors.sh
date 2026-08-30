#!/usr/bin/env bash
# Print the gate's suite floors FROM THE GATE (R4-F4, D-055(e), D-058).
#
# WHY. `docs/session-state.md` §3 kept a hand-maintained copy of the suite counts and drifted
# from the gate's constants five times — most recently publishing 507/198 while the floors were
# 513/209, which would have led a maintainer to LOWER a floor. John's ruling: remove the
# duplication or mechanically bind it. The duplication is removed; this is the binding.
#
# THIS PRINTS THE FLOORS, NOT THE COUNTS. A floor is what the gate asserts; the count is what a
# run measures. They are equal today and that is not guaranteed tomorrow — run the gate for the
# counts. Stating this because reporting a floor as a measurement is the defect one layer up.
#
# Refusals name the constant as the subject of one record (`{NAME}: <class phrase>`). Live
# floor copies in the three enumerated current paragraphs are refused; dated history is not.
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
# CALLER GIT OVERRIDES ARE REMOVED ONCE, HERE, BEFORE ANY BODY-LEVEL GIT CALL (12-F2).
# Scrubbing only the identity probe left every later `git` inheriting the caller's
# environment: GIT_DIR alone made this guard report clean over a live credential, and made
# install-hooks write into a victim repository. GIT_PREFIX is included although inert on
# git 2.50.1 — an inert variable today is not a guarantee tomorrow.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 not found; suite-floor reader refuses." >&2
    exit 2
fi

python3 - "$SENTINEL_ROOT/scripts/test.sh" "$SENTINEL_ROOT/docs/session-state.md" <<'PY'
import re
import sys

gate_path, session_path = sys.argv[1:]
gate = open(gate_path).read()
session = open(session_path).read()
names = (
    "FOUNDRY_MIN_TESTS", "TS_MIN_TESTS", "VERIFIER_MIN_TESTS",
    "VERIFIER_MIN_SAMPLES", "VERIFIER_MIN_TAMPER", "VERIFIER_MIN_TAMPER_MODES",
)
VALUE_PATTERN = r"[1-9][0-9]*"


def shell_code(line):
    out = []
    quote = None
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
            if quote is None:
                out.append(char)
            continue
        if char == "\\":
            escaped = True
            continue
        if quote is not None:
            if char == quote:
                quote = None
            continue
        if char in "'\"":
            quote = char
            continue
        if char == "#" and (index == 0 or line[index - 1].isspace()):
            break
        out.append(char)
    return "".join(out)


def heredoc_opener(raw):
    # Finite lexer: unquoted/quoted delimiter forms only. Operators inside ordinary
    # quotes and here-strings are ignored. This is not a general Bash parser.
    index = 0
    quote = None
    while index < len(raw):
        char = raw[index]
        if quote is not None:
            if quote == '"' and char == "\\" and index + 1 < len(raw):
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue
        if char == "\\" and index + 1 < len(raw):
            index += 2
            continue
        if char in "'\"":
            quote = char
            index += 1
            continue
        if char == "#" and (index == 0 or raw[index - 1].isspace()):
            return None
        if raw.startswith("<<<", index):
            index += 3
            continue
        if not raw.startswith("<<", index):
            index += 1
            continue
        cursor = index + 2
        if cursor < len(raw) and raw[cursor] == "-":
            cursor += 1
        while cursor < len(raw) and raw[cursor].isspace():
            cursor += 1
        delimiter_quote = None
        if cursor < len(raw) and raw[cursor] in "'\"":
            delimiter_quote = raw[cursor]
            cursor += 1
        match = re.match(r"[A-Za-z_][A-Za-z0-9_]*", raw[cursor:])
        if not match:
            index += 2
            continue
        delimiter = match.group(0)
        cursor += len(delimiter)
        if delimiter_quote is not None:
            if cursor >= len(raw) or raw[cursor] != delimiter_quote:
                index += 2
                continue
        return delimiter
    return None


tokens = {name: [] for name in names}
heredoc = None
for number, raw in enumerate(gate.splitlines(), 1):
    if heredoc is not None:
        if raw.strip() == heredoc:
            heredoc = None
        continue
    marker = heredoc_opener(raw)
    if marker is not None:
        heredoc = marker
    code = shell_code(raw)
    for name in names:
        if not re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}\s*=", code):
            continue
        direct = re.fullmatch(rf"{re.escape(name)}=(.*)", code)
        tokens[name].append((number, direct.group(1) if direct else None))

failed = False
values = {}
for name in names:
    found = tokens[name]
    if not found:
        print(f"{name}: missing definition")
        failed = True
        continue
    if len(found) > 1:
        print(f"{name}: duplicate executable assignment")
        failed = True
        continue
    value = found[0][1]
    if value is None:
        print(f"{name}: malformed assignment")
        failed = True
    elif value == "":
        print(f"{name}: empty assignment")
        failed = True
    elif not re.fullmatch(VALUE_PATTERN, value):
        print(f"{name}: numeric positive decimal required")
        failed = True
    else:
        values[name] = value

normal_session = re.sub(r"\s+", " ", session)
normal_gate = re.sub(r"\s+", " ", gate)
if "What is stable and worth stating: current floors are Foundry" in normal_session:
    print("session-state current publication is a numeric copy and must derive")
    failed = True
if "D-010 verifier:** 7 samples" in normal_session:
    print("session-state maintained publication is a numeric copy and must derive")
    failed = True
if "D-010 The current verifier has" in normal_gate:
    print("coverage current publication is a numeric copy and must derive")
    failed = True

if failed:
    sys.exit(1)
for name in names:
    print(f"  {name:<26} {values[name]}")
print("suite floors: read from scripts/test.sh, which is the only copy.")
PY
_floors_rc=$?

# --- ADDITIVE (F6). NOTHING ABOVE THIS LINE IS CHANGED. ----------------------
# The six floors above are the ones scripts/test.sh declares, and they cover
# `test_verifier` only. `verifier/test_publication_verifier.py` and
# `verifier/test_publication_override.py` — the closure evidence for R-A018-06 and
# R-A018-16 — had no floor at all, so this listing was silently incomplete: a reader
# checking "which suites are floored?" got six answers and no hint of the two missing.
#
# Their floor cannot be a `VERIFIER_MIN_` integer, because both files contain tests that
# are RED ON PURPOSE and a pass-count alone lets a new failure hide behind a fixed one. It
# is a pass count PLUS a named red set, and it lives in
# `scripts/check-publication-suite-floors.sh` — which is the only copy, exactly as
# scripts/test.sh is the only copy of the six above. This call PRINTS it; that script
# ENFORCES it, and running it here would put a 90-second suite run inside a printer.
#
# THIS CANNOT MASK A FAILURE ABOVE. `_floors_rc` is captured before this line and the only
# assignment after it raises the status to 1. A guard that swallowed its own earlier
# failure to report a later success would be the defect this repository keeps catching.
"$SENTINEL_ROOT/scripts/check-publication-suite-floors.sh" --print-floors || _floors_rc=1

exit "$_floors_rc"
