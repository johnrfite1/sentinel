#!/usr/bin/env python3
"""Frozen focused test contract for Sentinel A-FLOORS.

The harness clones the named exact commit and mutates only its private clone.
"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

BASELINE = "1a133301533e9d959dbafbbcc7ffe05e7eb78df3"
FLOORS = {
    "FOUNDRY_MIN_TESTS": 103,
    "TS_MIN_TESTS": 550,
    "VERIFIER_MIN_TESTS": 221,
    "VERIFIER_MIN_SAMPLES": 7,
    "VERIFIER_MIN_TAMPER": 78,
    "VERIFIER_MIN_TAMPER_MODES": 30,
}
B_EVENTS_SHA256 = "2a9219cc5138858b012b0bc56069490db3dd7d1963b73ccc19c28a48ce2b029e"
C_SNAPSHOT_SHA256 = "29a673560e89b639b6635661706a368454c9969a04c5d37c4f6c15229df3dd8a"

required_total = required_held = control_total = control_held = 0
rows: list[tuple[str, str, str, str]] = []


def record(kind: str, case: str, held: bool, description: str) -> None:
    global required_total, required_held, control_total, control_held
    status = "PASS" if held else "FAIL"
    print(f"  {case:<29} {kind:<8} {status:<4}  {description}")
    rows.append((case, kind, status, description))
    if kind == "REQUIRED":
        required_total += 1
        required_held += int(held)
    elif kind == "CONTROL":
        control_total += 1
        control_held += int(held)
    else:
        raise ValueError(kind)


def run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    clean = os.environ.copy()
    for name in (
        "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "GIT_PREFIX",
        "GIT_REPLACE_REF_BASE", "GIT_NO_REPLACE_OBJECTS", "GIT_TEMPLATE_DIR",
    ):
        clean.pop(name, None)
    for name in list(clean):
        if name.startswith("GIT_CONFIG_"):
            clean.pop(name, None)
    return subprocess.run(
        args, cwd=cwd, env=clean, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False,
    )


def must(args: list[str], cwd: Path, label: str) -> str:
    result = run(args, cwd)
    if result.returncode != 0:
        raise RuntimeError(f"{label}: rc={result.returncode}: {result.stdout}")
    return result.stdout


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checker(root: Path) -> subprocess.CompletedProcess[str]:
    return run(["bash", "scripts/check-suite-floors.sh"], root)


def printed_value(output: str, name: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(name)}\s+(\S.*)$", output)
    return match.group(1).strip() if match else None


def source_assignments(path: Path, name: str) -> list[tuple[int, str]]:
    token = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(name)}\s*=")
    found = []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.lstrip().startswith("#") and token.search(line):
            found.append((number, line))
    return found


def canonical_value(path: Path, name: str) -> int | None:
    found = re.findall(rf"(?m)^{re.escape(name)}=([1-9][0-9]*)$", path.read_text())
    return int(found[0]) if len(found) == 1 else None


def legacy_first_value(path: Path, name: str) -> str | None:
    found = re.findall(rf"(?m)^{re.escape(name)}=([^\n]*)$", path.read_text())
    return found[0] if found else None


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if text.count(old) != 1:
        raise RuntimeError(f"anchor count {path}:{old!r}={text.count(old)}")
    path.write_text(text.replace(old, new))


VALID_TEST_SH = """#!/usr/bin/env bash
FOUNDRY_MIN_TESTS=103
TS_MIN_TESTS=550
VERIFIER_MIN_TESTS=221
VERIFIER_MIN_SAMPLES=7
VERIFIER_MIN_TAMPER=78
VERIFIER_MIN_TAMPER_MODES=30

cat <<'COVERAGE'
GATE PASSED

COVERAGE BOUNDARY (house rule 4) — read this, not the pass count

  D-010    Current measured counts and all six floor values are printed above from
           canonical assignments; this maintained paragraph does not copy them.
           THIS PARAGRAPH READ 62/24/149 FROM 2026-08-16 UNTIL 2026-08-17.
           That dated sentence is historical evidence.
COVERAGE
"""

VALID_SESSION = """# Session-state fixture

## 3. Where the build is

**DO NOT READ A SUITE COUNT FROM THIS FILE. RUN ./scripts/test.sh AND READ ITS OUTPUT, OR
RUN ./scripts/check-suite-floors.sh.**

**What is stable and worth stating: 50 corpus fixtures.** Values for the six floor dimensions
are deliberately not repeated here; the checker derives them from scripts/test.sh.

- **D-010 verifier:** Current measured counts and floor values are printed by the gate and by
  scripts/check-suite-floors.sh; this maintained paragraph carries no numeric copy.
  *(From 2026-08-16 until 2026-08-17 this line read 7/7, 62/62, 24 modes, and 149/149.
  This is a dated historical control, not a current publication.)*

## 4. Historical controls

On 2026-08-18 the old floor constants were 75/513/209/7/78/30. This paragraph is explicitly
dated and outside the enumerated current paragraphs.
"""

SIBLING_TEMPLATE = r'''#!/usr/bin/env bash
set -uo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)" || exit 2
python3 - "$ROOT/scripts/test.sh" "$ROOT/docs/session-state.md" <<'PY'
import re, sys

gate_path, session_path = sys.argv[1:]
gate = open(gate_path).read()
session = open(session_path).read()
names = (
    "FOUNDRY_MIN_TESTS", "TS_MIN_TESTS", "VERIFIER_MIN_TESTS",
    "VERIFIER_MIN_SAMPLES", "VERIFIER_MIN_TAMPER", "VERIFIER_MIN_TAMPER_MODES",
)
VALUE_PATTERN = r"__VALUE_PATTERN__"
MARKER_MODE = "__MARKER_MODE__"
FAILCLOSE_MODE = "__FAILCLOSE_MODE__"
DIAGNOSTIC_MODE = "__DIAGNOSTIC_MODE__"

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
    if MARKER_MODE == "raw":
        if raw.lstrip().startswith("#"):
            return None
        marker = re.search(
            r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1", raw
        )
        return marker.group(2) if marker else None
    # This finite lexer recognizes only the card's exact unquoted/quoted delimiter forms.
    # It ignores operators inside ordinary single/double quotes and ignores here-strings.
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
forced_duplicates = set()
heredoc = None
for number, raw in enumerate(gate.splitlines(), 1):
    if heredoc is not None:
        if raw.strip() == heredoc:
            heredoc = None
        continue
    if "A_FLOOR_MASK" in raw:
        is_comment = raw.lstrip().startswith("#")
        if FAILCLOSE_MODE == "all" or (FAILCLOSE_MODE == "non-comment" and not is_comment):
            named = {
                name for name in names
                if re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}\s*=", raw)
            }
            forced_duplicates.update(named or names)
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
if DIAGNOSTIC_MODE == "uncorrelated":
    print("inspected constants: " + " ".join(names))

def emit_duplicate(target):
    if DIAGNOSTIC_MODE == "uncorrelated":
        print("UNRELATED_CONSTANT: duplicate executable assignment")
    else:
        print(f"{target}: duplicate executable assignment")

for name in names:
    if name in forced_duplicates:
        emit_duplicate(name)
        failed = True
for name in names:
    found = tokens[name]
    if not found:
        print(f"{name}: missing definition")
        failed = True
        continue
    if len(found) > 1:
        emit_duplicate(name)
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
print("suite floors: read from scripts/test.sh, which is the only executable source.")
PY
'''


def install_sibling(
    root: Path, value_pattern: str, marker_mode: str, failclose_mode: str = "none",
    diagnostic_mode: str = "named",
) -> None:
    gate = root / "scripts/test.sh"
    text = gate.read_text()
    for name, value in FLOORS.items():
        pattern = rf"(?m)^{re.escape(name)}=[^\n]*$"
        if len(re.findall(pattern, text)) != 1:
            raise RuntimeError(f"sibling floor anchor {name}")
        text = re.sub(pattern, f"{name}={value}", text)
    anchor = 'step() { printf \'\\n\\033[1m== %s ==\\033[0m\\n\' "$1"; }\n'
    if text.count(anchor) != 1:
        raise RuntimeError("sibling gate wiring anchor")
    gate.write_text(text.replace(
        anchor,
        anchor + "\n./scripts/check-suite-floors.sh || fail=1\n",
    ))
    reader = root / "scripts/check-suite-floors.sh"
    sibling = SIBLING_TEMPLATE
    if (
        sibling.count("__VALUE_PATTERN__") != 1
        or sibling.count("__MARKER_MODE__") != 1
        or sibling.count("__FAILCLOSE_MODE__") != 1
        or sibling.count("__DIAGNOSTIC_MODE__") != 1
    ):
        raise RuntimeError("sibling template anchors")
    reader.write_text(
        sibling.replace("__VALUE_PATTERN__", value_pattern)
        .replace("__MARKER_MODE__", marker_mode)
        .replace("__FAILCLOSE_MODE__", failclose_mode)
        .replace("__DIAGNOSTIC_MODE__", diagnostic_mode)
    )
    reader.chmod(0o755)


def install_zero_accepting_sibling(root: Path) -> None:
    install_sibling(root, r"[0-9]+", "finite")


def install_flawed_heredoc_sibling(root: Path) -> None:
    install_sibling(root, r"[1-9][0-9]*", "raw")


def install_review3_failclosed_sibling(root: Path) -> None:
    install_sibling(root, r"[1-9][0-9]*", "raw", "non-comment")


def install_all_token_failclosed_sibling(root: Path) -> None:
    install_sibling(root, r"[1-9][0-9]*", "raw", "all")


def install_exact_positive_control(root: Path) -> None:
    install_sibling(root, r"[1-9][0-9]*", "finite")


def install_uncorrelated_diagnostic_sibling(root: Path) -> None:
    install_sibling(root, r"[1-9][0-9]*", "finite", diagnostic_mode="uncorrelated")


def make_fixture(root: Path) -> None:
    (root / "scripts/test.sh").write_text(VALID_TEST_SH)
    (root / "scripts/test.sh").chmod(0o755)
    (root / "docs/session-state.md").write_text(VALID_SESSION)


def inert_opener_routes(name: str) -> list[tuple[str, str, bool]]:
    """Exact finite fake-opener spellings; bool marks Review-2-vulnerable routes."""
    return [
        ("comment", f"    # <<'A_FLOOR_MASK' {name}=888", False),
        ("printf-sq", f"printf '%s\\n' '<<\"A_FLOOR_MASK\" {name}=888' >/dev/null", True),
        ("printf-dq", f"printf '%s\\n' \"<<'A_FLOOR_MASK' {name}=888\" >/dev/null", True),
        ("echo-sq", f"echo '<<\"A_FLOOR_MASK\" {name}=888' >/dev/null", True),
        ("echo-dq", f"echo \"<<'A_FLOOR_MASK' {name}=888\" >/dev/null", True),
        ("assign-sq", f"a_floor_note='<<\"A_FLOOR_MASK\" {name}=888'", True),
        ("assign-dq", f"a_floor_note=\"<<'A_FLOOR_MASK' {name}=888\"", True),
        ("herestring-sq", ": <<< 'A_FLOOR_MASK'", True),
        ("herestring-dq", ': <<< "A_FLOOR_MASK"', True),
    ]


def shell_value(script: Path, name: str) -> tuple[int, str]:
    command = f'source "$1" >/dev/null; printf "%s" "${{{name}-}}"'
    result = subprocess.run(
        ["bash", "-c", command, "_", str(script)], text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    return result.returncode, result.stdout


def shell_assignment_trace(script: Path, name: str) -> tuple[int, list[str]]:
    result = subprocess.run(
        [
            "bash", "--noprofile", "--norc", "-x", "-c",
            'source "$1" >/dev/null; printf "done"', "_", str(script),
        ],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    values = re.findall(rf"(?m)^\++ {re.escape(name)}=([^\s]*)$", result.stdout)
    return result.returncode, values


def synthetic_result(output: str, rc: int = 1) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=rc, stdout=output, stderr="")


def source_refusal(result: subprocess.CompletedProcess[str], name: str, reason: str) -> bool:
    if result.returncode == 0:
        return False
    name_l = name.lower()
    reason_l = reason.lower()
    for line in result.stdout.splitlines():
        low = line.lower()
        if name_l in low and reason_l in low:
            return True
    return False


def reader_accepts_all_values(result: subprocess.CompletedProcess[str]) -> bool:
    output = result.stdout.lower()
    refusal_markers = (
        "duplicate", "missing definition", "malformed assignment",
        "empty assignment", "numeric positive decimal required", "must derive", "numeric copy",
        "refus",
    )
    return (
        result.returncode == 0
        and not any(marker in output for marker in refusal_markers)
        and all(printed_value(result.stdout, name) == str(value) for name, value in FLOORS.items())
    )


def reader_refusal(result: subprocess.CompletedProcess[str], surface: str) -> bool:
    output = result.stdout.lower()
    return (
        result.returncode != 0
        and surface in output
        and ("live" in output or "current" in output or "maintained" in output)
        and (
            "duplicate" in output
            or "publication" in output
            or "numeric copy" in output
            or "must derive" in output
            or "derived" in output
        )
    )


def logical_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def wiring_count(value: str) -> int:
    return len(re.findall(
        r"(?m)^\s*\./scripts/check-suite-floors\.sh(?:\s|$)", value
    ))


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("usage: a-floors.py <source-repository> [exact-commit]", file=sys.stderr)
        return 2
    source = Path(sys.argv[1]).resolve()
    subject = sys.argv[2] if len(sys.argv) == 3 else must(
        ["git", "rev-parse", "HEAD"], source, "resolve subject"
    ).strip()
    if not re.fullmatch(r"[0-9a-f]{40}", subject):
        print("preflight: exact lowercase 40-hex commit required", file=sys.stderr)
        return 2
    if must(["git", "cat-file", "-t", subject], source, "subject type").strip() != "commit":
        print("preflight: subject is not a commit", file=sys.stderr)
        return 2
    status = must(
        ["git", "status", "--porcelain", "--untracked-files=no"], source,
        "source worktree status",
    )
    if status:
        print("preflight: source worktree has tracked changes", file=sys.stderr)
        return 2

    matrix_path = os.environ.get("A_FLOORS_MATRIX")
    variant = os.environ.get("A_FLOORS_VARIANT", "baseline")
    if variant not in (
        "baseline", "digits-zero-sibling", "flawed-heredoc-sibling",
        "review3-failclosed-sibling", "all-token-failclosed-sibling",
        "exact-positive-control", "uncorrelated-diagnostic-sibling",
    ):
        print("preflight: unknown A_FLOORS_VARIANT", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="a-floors.") as temp:
        root = Path(temp) / "subject"
        cloned = run(["git", "clone", "--no-hardlinks", "--local", str(source), str(root)], source)
        if cloned.returncode != 0:
            print("preflight: clone failed: " + cloned.stdout, file=sys.stderr)
            return 2
        checked = run(["git", "checkout", "--detach", subject], root)
        if checked.returncode != 0:
            print("preflight: checkout failed: " + checked.stdout, file=sys.stderr)
            return 2
        if must(["git", "rev-parse", "HEAD"], root, "identity").strip() != subject:
            print("preflight: clone identity mismatch", file=sys.stderr)
            return 2
        if variant == "digits-zero-sibling":
            install_zero_accepting_sibling(root)
        elif variant == "flawed-heredoc-sibling":
            install_flawed_heredoc_sibling(root)
        elif variant == "review3-failclosed-sibling":
            install_review3_failclosed_sibling(root)
        elif variant == "all-token-failclosed-sibling":
            install_all_token_failclosed_sibling(root)
        elif variant == "exact-positive-control":
            install_exact_positive_control(root)
        elif variant == "uncorrelated-diagnostic-sibling":
            install_uncorrelated_diagnostic_sibling(root)

        print("A-FLOORS focused frozen contract")
        print(f"subject={subject}")
        print(f"baseline={BASELINE}")
        print(f"variant={variant}")
        print(f"harness_sha256={digest(Path(__file__))}")

        print("\n== frozen B/C preservation controls ==")
        record(
            "CONTROL", "P-B-EVENTS",
            digest(root / "contracts/test/SentinelVault.events.t.sol") == B_EVENTS_SHA256,
            "frozen eleven-test B-EVENTS implementation bytes",
        )
        record(
            "CONTROL", "P-C-SNAPSHOT",
            digest(root / "ts/test/vault.snapshot.classification.test.ts") == C_SNAPSHOT_SHA256,
            "frozen twenty-three-test C-SNAPSHOT implementation bytes",
        )

        print("\n== live canonical values ==")
        actual_gate = root / "scripts/test.sh"
        actual_gate_text = actual_gate.read_text()
        actual_session = root / "docs/session-state.md"
        actual_session_text = actual_session.read_text()
        actual_reader_hash = digest(root / "scripts/check-suite-floors.sh")
        live_reader = checker(root)
        if live_reader.returncode != 0:
            print("  live-reader diagnostic: " + live_reader.stdout.strip().replace("\n", " | "))
        record("CONTROL", "V-reader-alive", live_reader.returncode == 0,
               "unchanged baseline reader executes successfully")
        for name, expected in FLOORS.items():
            got = canonical_value(actual_gate, name)
            record("REQUIRED", f"V-{name}", got == expected,
                   f"canonical value {expected}; observed {got!r}")

        print("\n== synthetic exact-source matrix ==")
        make_fixture(root)
        valid = checker(root)
        values_ok = all(printed_value(valid.stdout, name) == str(value)
                        for name, value in FLOORS.items())
        record("CONTROL", "S-valid", valid.returncode == 0 and values_ok,
               "six exact positive-decimal definitions are accepted and reported")
        record(
            "CONTROL", "S-prefix",
            len(source_assignments(root / "scripts/test.sh", "VERIFIER_MIN_TAMPER")) == 1,
            "TAMPER does not consume the legitimate TAMPER_MODES sibling",
        )

        print("\n== diagnostic-correlation oracle ==")
        hostile_output = (
            "inspected constants: " + " ".join(FLOORS) + "\n"
            "UNRELATED_CONSTANT: duplicate executable assignment\n"
        )
        for name in FLOORS:
            legit = synthetic_result(f"{name}: duplicate executable assignment\n")
            record(
                "CONTROL", f"DR-legit-{name}",
                source_refusal(legit, name, "duplicate"),
                "same-record named duplicate diagnostic satisfies the oracle",
            )
            hostile = synthetic_result(hostile_output)
            record(
                "CONTROL", f"DR-uncorrelated-{name}",
                not source_refusal(hostile, name, "duplicate"),
                "inventory plus unrelated duplicate record does not name this constant",
            )

        fake_only_routes: list[tuple[str, str]] = []
        paired_routes: list[tuple[str, str]] = []
        for name, value in FLOORS.items():
            line = f"{name}={value}"

            make_fixture(root)
            replace_once(root / "scripts/test.sh", line + "\n", "")
            result = checker(root)
            record("REQUIRED", f"M-{name}", source_refusal(result, name, "missing"),
                   "missing definition refuses by constant and reason")

            make_fixture(root)
            replace_once(root / "scripts/test.sh", line, f"{name}=")
            result = checker(root)
            record("REQUIRED", f"E-{name}", source_refusal(result, name, "empty"),
                   "empty definition refuses distinctly")

            make_fixture(root)
            replace_once(root / "scripts/test.sh", line, f"{name} = {value}")
            result = checker(root)
            record("REQUIRED", f"X-{name}", source_refusal(result, name, "malformed"),
                   "malformed assignment refuses by constant and reason")

            make_fixture(root)
            replace_once(root / "scripts/test.sh", line, f"{name}=not-a-number")
            result = checker(root)
            record("REQUIRED", f"N-{name}", source_refusal(result, name, "numeric"),
                   "assigned non-numeric value refuses by constant and reason")

            make_fixture(root)
            replace_once(root / "scripts/test.sh", line, f"{name}=0")
            result = checker(root)
            record("REQUIRED", f"Z-{name}", source_refusal(result, name, "positive"),
                   "zero refuses by constant and positive-decimal reason")

            make_fixture(root)
            replace_once(root / "scripts/test.sh", line, f"{name}=1")
            result = checker(root)
            record(
                "CONTROL", f"ONE-{name}",
                result.returncode == 0 and printed_value(result.stdout, name) == "1",
                "ordinary positive decimal one remains accepted and reported",
            )

            make_fixture(root)
            replace_once(root / "scripts/test.sh", line, line + f"\n{name}=999")
            result = checker(root)
            bash_rc, bash_got = shell_value(root / "scripts/test.sh", name)
            witness = (
                bash_rc == 0 and bash_got == "999"
                and legacy_first_value(root / "scripts/test.sh", name) == str(value)
                and len(source_assignments(root / "scripts/test.sh", name)) == 2
            )
            record("CONTROL", f"DAW-{name}", witness,
                   "after witness: legacy first-line projection differs from Bash last-wins 999")
            record("REQUIRED", f"DA-{name}", source_refusal(result, name, "duplicate"),
                   "duplicate after the canonical definition refuses by name")

            make_fixture(root)
            replace_once(root / "scripts/test.sh", line, f"{name}=999\n" + line)
            result = checker(root)
            bash_rc, bash_got = shell_value(root / "scripts/test.sh", name)
            witness = (
                bash_rc == 0 and bash_got == str(value)
                and legacy_first_value(root / "scripts/test.sh", name) == "999"
                and len(source_assignments(root / "scripts/test.sh", name)) == 2
            )
            record("CONTROL", f"DBW-{name}", witness,
                   f"before witness: legacy first-line projection 999 differs from Bash {value}")
            record("REQUIRED", f"DB-{name}", source_refusal(result, name, "duplicate"),
                   "duplicate before the canonical definition refuses by name")

            make_fixture(root)
            replace_once(root / "scripts/test.sh", line, line + f"\nif true; then {name}=999; fi")
            result = checker(root)
            bash_rc, bash_got = shell_value(root / "scripts/test.sh", name)
            witness = (
                bash_rc == 0 and bash_got == "999"
                and len(source_assignments(root / "scripts/test.sh", name)) == 2
            )
            record("CONTROL", f"DCW-{name}", witness,
                   "conditional duplicate executes and shadows the canonical value")
            record("REQUIRED", f"DC-{name}", source_refusal(result, name, "duplicate"),
                   "inline conditional assignment token refuses as duplicate")

            make_fixture(root)
            replace_once(root / "scripts/test.sh", line, line + f"\n    {name}=999")
            result = checker(root)
            bash_rc, bash_got = shell_value(root / "scripts/test.sh", name)
            trace_rc, trace = shell_assignment_trace(root / "scripts/test.sh", name)
            witness = (
                bash_rc == 0 and bash_got == "999" and trace_rc == 0
                and trace == [str(value), "999"]
            )
            record("CONTROL", f"IAW-{name}", witness,
                   "indented-after executes after canonical and Bash last-wins 999")
            record("REQUIRED", f"IA-{name}", source_refusal(result, name, "duplicate"),
                   "standalone indented duplicate after canonical refuses by name")

            make_fixture(root)
            replace_once(root / "scripts/test.sh", line, f"    {name}=999\n" + line)
            result = checker(root)
            bash_rc, bash_got = shell_value(root / "scripts/test.sh", name)
            trace_rc, trace = shell_assignment_trace(root / "scripts/test.sh", name)
            witness = (
                bash_rc == 0 and bash_got == str(value) and trace_rc == 0
                and trace == ["999", str(value)]
            )
            record("CONTROL", f"IBW-{name}", witness,
                   f"indented-before executes first; canonical later restores {value}")
            record("REQUIRED", f"IB-{name}", source_refusal(result, name, "duplicate"),
                   "standalone indented duplicate before canonical refuses by name")

            make_fixture(root)
            replace_once(root / "scripts/test.sh", line, line + f"\n    # {name}=999")
            result = checker(root)
            bash_rc, bash_got = shell_value(root / "scripts/test.sh", name)
            record(
                "CONTROL", f"IC-{name}",
                result.returncode == 0 and bash_rc == 0 and bash_got == str(value)
                and printed_value(result.stdout, name) == str(value),
                "indented commented assignment-shaped text is inert and accepted",
            )

            make_fixture(root)
            replace_once(
                root / "scripts/test.sh", line,
                line + f"\nprintf '%s\\n' '{name}=999' >/dev/null",
            )
            result = checker(root)
            bash_rc, bash_got = shell_value(root / "scripts/test.sh", name)
            record(
                "CONTROL", f"IQ-{name}",
                result.returncode == 0 and bash_rc == 0 and bash_got == str(value)
                and printed_value(result.stdout, name) == str(value),
                "quoted assignment-shaped string is inert and accepted",
            )

            make_fixture(root)
            replace_once(
                root / "scripts/test.sh", line,
                line + f"\n: <<'A_FLOOR_INERT'\n{name}=999\nA_FLOOR_INERT",
            )
            result = checker(root)
            bash_rc, bash_got = shell_value(root / "scripts/test.sh", name)
            record(
                "CONTROL", f"IH-{name}",
                result.returncode == 0 and bash_rc == 0 and bash_got == str(value)
                and printed_value(result.stdout, name) == str(value),
                "quoted-heredoc assignment-shaped body is inert and accepted",
            )

            for opener_id, opener, vulnerable in inert_opener_routes(name):
                make_fixture(root)
                replace_once(
                    root / "scripts/test.sh", line,
                    line + f"\n{opener}",
                )
                fake_only = checker(root)
                record(
                    "CONTROL", f"FA-{opener_id}-{name}",
                    reader_accepts_all_values(fake_only),
                    f"{opener_id} alone is accepted with all six canonical values reported",
                )
                fake_only_routes.append((opener_id, name))

                make_fixture(root)
                replace_once(
                    root / "scripts/test.sh", line,
                    line + f"\n{opener}\n    {name}=999",
                )
                result = checker(root)
                bash_rc, bash_got = shell_value(root / "scripts/test.sh", name)
                trace_rc, trace = shell_assignment_trace(root / "scripts/test.sh", name)
                witness = (
                    bash_rc == 0 and bash_got == "999" and trace_rc == 0
                    and trace == [str(value), "999"]
                )
                prefix = "TF" if vulnerable else "FC"
                record(
                    "CONTROL", f"{prefix}W-{opener_id}-{name}", witness,
                    f"{opener_id} token is inert; Bash executes canonical then indented 999",
                )
                record(
                    "REQUIRED", f"{prefix}-{opener_id}-{name}",
                    witness and source_refusal(result, name, "duplicate"),
                    f"{opener_id} fake opener cannot mask following executable duplicate",
                )
                paired_routes.append((opener_id, name))

            make_fixture(root)
            replace_once(
                root / "scripts/test.sh", line,
                line + f"\n: <<'A_FLOOR_REAL'\n{name}=888\nA_FLOOR_REAL\n    {name}=999",
            )
            result = checker(root)
            bash_rc, bash_got = shell_value(root / "scripts/test.sh", name)
            trace_rc, trace = shell_assignment_trace(root / "scripts/test.sh", name)
            real_post_witness = (
                bash_rc == 0 and bash_got == "999" and trace_rc == 0
                and trace == [str(value), "999"]
            )
            record(
                "REQUIRED", f"HR-post-{name}",
                real_post_witness and source_refusal(result, name, "duplicate"),
                "real heredoc body is inert and parsing resumes for post-terminator duplicate",
            )

        expected_routes = {
            (opener_id, name)
            for name in FLOORS
            for opener_id, _opener, _vulnerable in inert_opener_routes(name)
        }
        route_counts = {
            opener_id: sum(route_id == opener_id for route_id, _name in paired_routes)
            for opener_id, _opener, _vulnerable in inert_opener_routes(next(iter(FLOORS)))
        }
        record(
            "CONTROL", "T-route-complete",
            len(fake_only_routes) == 54
            and len(set(fake_only_routes)) == 54
            and set(fake_only_routes) == expected_routes
            and len(paired_routes) == 54
            and len(set(paired_routes)) == 54
            and set(paired_routes) == expected_routes
            and set(fake_only_routes) == set(paired_routes)
            and all(count == 6 for count in route_counts.values()),
            "54/54 fake-only controls map one-to-one to 54/54 paired requirements",
        )

        print("\n== enumerated logical-paragraph matrix ==")
        make_fixture(root)
        result = checker(root)
        record("CONTROL", "P-history", result.returncode == 0,
               "dated numbers inside both enumerated D-010 logical paragraphs remain controls")

        replace_once(
            root / "docs/session-state.md",
            "**What is stable and worth stating: 50 corpus fixtures.** Values for the six floor dimensions\n"
            "are deliberately not repeated here; the checker derives them from scripts/test.sh.",
            "**What is stable and worth stating: current floors are Foundry 104, TypeScript\n"
            "550, verifier 221, samples 7, tamper 78, and modes 30.**",
        )
        result = checker(root)
        record("REQUIRED", "P-session-stable", reader_refusal(result, "session-state"),
               "wrapped live §3 floor paragraph refuses with named reader diagnostic")

        wrapped = (
            "**What is stable and worth stating: current floors are Foundry 104, TypeScript\n"
            "550, verifier 221, samples 7, tamper 78, and modes 30.**"
        )
        unwrapped = (
            "**What is stable and worth stating: current floors are Foundry 104, TypeScript "
            "550, verifier 221, samples 7, tamper 78, and modes 30.**"
        )
        record("CONTROL", "P-wrap-witness", logical_text(wrapped) == logical_text(unwrapped),
               "wrapped and unwrapped mutations normalize to one logical paragraph")
        make_fixture(root)
        replace_once(
            root / "docs/session-state.md",
            "**What is stable and worth stating: 50 corpus fixtures.** Values for the six floor dimensions\n"
            "are deliberately not repeated here; the checker derives them from scripts/test.sh.",
            unwrapped,
        )
        result = checker(root)
        record("REQUIRED", "P-session-stable-flat", reader_refusal(result, "session-state"),
               "equivalent unwrapped live §3 paragraph receives the same diagnostic class")

        make_fixture(root)
        replace_once(
            root / "docs/session-state.md",
            "- **D-010 verifier:** Current measured counts and floor values are printed by the gate and by\n"
            "  scripts/check-suite-floors.sh; this maintained paragraph carries no numeric copy.",
            "- **D-010 verifier:** 7 samples, 78 tamper cases over 30 modes, and\n"
            "  220 verifier tests are the current floors.",
        )
        result = checker(root)
        record("REQUIRED", "P-session-d010", reader_refusal(result, "session-state"),
               "wrapped current D-010 paragraph refuses with named reader diagnostic")

        make_fixture(root)
        replace_once(
            root / "scripts/test.sh",
            "  D-010    Current measured counts and all six floor values are printed above from\n"
            "           canonical assignments; this maintained paragraph does not copy them.",
            "  D-010    The current verifier has 220 tests, 7 samples, 78 tamper cases over\n"
            "           30 modes; all are floors this run asserts.",
        )
        result = checker(root)
        record("REQUIRED", "P-coverage-d010", reader_refusal(result, "coverage"),
               "wrapped current gate coverage paragraph refuses with named reader diagnostic")

        make_fixture(root)
        insert = (
            "\nThe identifiers FOUNDRY_MIN_TESTS, TS_MIN_TESTS, VERIFIER_MIN_TESTS, "
            "VERIFIER_MIN_SAMPLES, VERIFIER_MIN_TAMPER and VERIFIER_MIN_TAMPER_MODES "
            "are derived; this sentence publishes no value.\n"
        )
        replace_once(root / "docs/session-state.md", "\n## 4. Historical controls\n",
                     insert + "\n## 4. Historical controls\n")
        result = checker(root)
        record("CONTROL", "P-name-mentions", result.returncode == 0,
               "constant-name mentions without values are legitimate")

        make_fixture(root)
        insert = "\nIssue 103 closed after 550 observations; these are not suite facts.\n"
        replace_once(root / "docs/session-state.md", "\n## 4. Historical controls\n",
                     insert + "\n## 4. Historical controls\n")
        result = checker(root)
        record("CONTROL", "P-unrelated", result.returncode == 0,
               "unrelated numbers outside enumerated floor paragraphs remain controls")

        print("\n== real-gate wiring source ==")
        invocation_count = wiring_count(actual_gate_text)
        record("REQUIRED", "W-common", invocation_count == 1,
               f"one real-gate targeted-guard invocation; observed {invocation_count}")
        wired_witness = actual_gate_text + "\n./scripts/check-suite-floors.sh || fail=1\n"
        record(
            "CONTROL", "W-positive",
            actual_gate.read_text() != actual_gate_text
            and wiring_count(wired_witness) == invocation_count + 1,
            "frozen candidate text survives fixtures and one direct invocation increments the oracle",
        )
        actual_gate.write_text(actual_gate_text)
        actual_session.write_text(actual_session_text)
        restored_reader = checker(root)
        record(
            "CONTROL", "P-reader-restore",
            digest(root / "scripts/check-suite-floors.sh") == actual_reader_hash
            and restored_reader.returncode == live_reader.returncode
            and restored_reader.stdout == live_reader.stdout,
            "fixture transforms leave candidate reader bytes and restored behavior identical",
        )

    if matrix_path:
        matrix = Path(matrix_path)
        matrix.parent.mkdir(parents=True, exist_ok=True)
        matrix.write_text(
            "case\tkind\tstatus\tdescription\n"
            + "".join("\t".join(row) + "\n" for row in rows)
        )

    print("\nA-FLOORS focused summary")
    print(f"REQUIRED {required_held}/{required_total}")
    print(f"CONTROL {control_held}/{control_total}")
    if control_held != control_total:
        print("INSTRUMENT INVALID: control failure")
        return 2
    if required_held != required_total:
        print("PRE-REPAIR DEFECTS OBSERVED")
        return 1
    print("A_FLOORS_FOCUSED_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
