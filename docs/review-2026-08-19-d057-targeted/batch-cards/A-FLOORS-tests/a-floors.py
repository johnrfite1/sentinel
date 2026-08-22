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


def make_fixture(root: Path) -> None:
    (root / "scripts/test.sh").write_text(VALID_TEST_SH)
    (root / "scripts/test.sh").chmod(0o755)
    (root / "docs/session-state.md").write_text(VALID_SESSION)


def shell_value(script: Path, name: str) -> tuple[int, str]:
    command = f'source "$1" >/dev/null; printf "%s" "${{{name}-}}"'
    result = subprocess.run(
        ["bash", "-c", command, "_", str(script)], text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    return result.returncode, result.stdout


def source_refusal(result: subprocess.CompletedProcess[str], name: str, reason: str) -> bool:
    output = result.stdout.lower()
    return result.returncode != 0 and name.lower() in output and reason in output


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

        print("A-FLOORS focused frozen contract")
        print(f"subject={subject}")
        print(f"baseline={BASELINE}")
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
        live_reader = checker(root)
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
            replace_once(root / "scripts/test.sh", line, line + f"\n{name}=999")
            result = checker(root)
            bash_rc, bash_got = shell_value(root / "scripts/test.sh", name)
            witness = (
                bash_rc == 0 and bash_got == "999"
                and printed_value(result.stdout, name) == str(value)
                and len(source_assignments(root / "scripts/test.sh", name)) == 2
            )
            record("CONTROL", f"DAW-{name}", witness,
                   "after witness: current reader first-wins; Bash last-wins 999")
            record("REQUIRED", f"DA-{name}", source_refusal(result, name, "duplicate"),
                   "duplicate after the canonical definition refuses by name")

            make_fixture(root)
            replace_once(root / "scripts/test.sh", line, f"{name}=999\n" + line)
            result = checker(root)
            bash_rc, bash_got = shell_value(root / "scripts/test.sh", name)
            witness = (
                bash_rc == 0 and bash_got == str(value)
                and printed_value(result.stdout, name) == "999"
                and len(source_assignments(root / "scripts/test.sh", name)) == 2
            )
            record("CONTROL", f"DBW-{name}", witness,
                   f"before witness: current reader first-wins 999; Bash last-wins {value}")
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
                   "conditional/indented assignment token refuses as duplicate")

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
