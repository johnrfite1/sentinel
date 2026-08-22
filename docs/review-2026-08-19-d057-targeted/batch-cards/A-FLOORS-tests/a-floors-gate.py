#!/usr/bin/env python3
"""Serial top-level gate contract for Sentinel A-FLOORS.

Every case gets a private exact-commit clone. Cases run synchronously: this harness
never overlaps one gate with another.
"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
import tempfile
import time
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
B_EVENTS = "contracts/test/SentinelVault.events.t.sol"
C_SNAPSHOT = "ts/test/vault.snapshot.classification.test.ts"

rows: list[tuple[str, str, str, str, str]] = []
required_total = required_held = control_total = control_held = 0


def clean_env() -> dict[str, str]:
    env = os.environ.copy()
    for name in (
        "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "GIT_PREFIX",
        "GIT_REPLACE_REF_BASE", "GIT_NO_REPLACE_OBJECTS", "GIT_TEMPLATE_DIR",
        "SENTINEL_GATE_TOKEN", "SENTINEL_GATE_REPO_ROOT",
    ):
        env.pop(name, None)
    for name in list(env):
        if name.startswith("GIT_CONFIG_"):
            env.pop(name, None)
    return env


def run(args: list[str], cwd: Path, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args, cwd=cwd, env=clean_env(), text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, timeout=timeout, check=False,
    )


def must(args: list[str], cwd: Path, label: str) -> str:
    result = run(args, cwd)
    if result.returncode != 0:
        raise RuntimeError(f"{label}: rc={result.returncode}: {result.stdout}")
    return result.stdout


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(kind: str, case: str, held: bool, elapsed: float, description: str) -> None:
    global required_total, required_held, control_total, control_held
    status = "PASS" if held else "FAIL"
    print(f"  {case:<20} {kind:<8} {status:<4} {elapsed:7.1f}s  {description}", flush=True)
    rows.append((case, kind, status, f"{elapsed:.3f}", description))
    if kind == "REQUIRED":
        required_total += 1
        required_held += int(held)
    elif kind == "CONTROL":
        control_total += 1
        control_held += int(held)
    else:
        raise ValueError(kind)


def set_planned_floors(root: Path) -> None:
    path = root / "scripts/test.sh"
    text = path.read_text()
    for name, value in FLOORS.items():
        pattern = rf"(?m)^{re.escape(name)}=[^\n]*$"
        found = re.findall(pattern, text)
        if len(found) != 1:
            raise RuntimeError(f"planned-floor anchor {name}: {len(found)}")
        text = re.sub(pattern, f"{name}={value}", text)
    path.write_text(text)


def replace_current_floor_paragraph(root: Path) -> None:
    path = root / "docs/session-state.md"
    text = path.read_text()
    pieces = re.split(r"(\n[ \t]*\n)", text)
    indexes = [
        i for i, piece in enumerate(pieces)
        if piece.lstrip().startswith("**What is stable and worth stating:")
    ]
    if len(indexes) != 1:
        raise RuntimeError(f"current paragraph anchor count={len(indexes)}")
    pieces[indexes[0]] = (
        "**What is stable and worth stating: current floors are Foundry 104, TypeScript\n"
        "550, verifier 221, samples 7, tamper 78, and modes 30.**"
    )
    path.write_text("".join(pieces))


def named_reader_refusal(output: str) -> bool:
    lower = output.lower()
    matching = [line for line in lower.splitlines() if "session-state" in line]
    return any(
        ("live" in line or "current" in line or "maintained" in line)
        and (
            "duplicate" in line or "publication" in line or "numeric copy" in line
            or "must derive" in line or "derived" in line
        )
        for line in matching
    )


def measured_success(output: str) -> bool:
    return (
        re.search(r"(?m)^\s*foundry: 103 tests \(floor [0-9]+\)$", output) is not None
        and re.search(r"(?m)^\s*typescript: 550 tests \(floor [0-9]+\)$", output) is not None
        and re.search(
            r"(?m)^\s*suite 221 \(floor [0-9]+\) · verdict clean · samples 7 "
            r"\(floor [0-9]+\) · tamper 78 cases / 30 modes \(floors [0-9]+/[0-9]+\)$",
            output,
        ) is not None
    )


def completed(result: subprocess.CompletedProcess[str], deep: bool = False) -> bool:
    return (
        result.returncode == 0
        and "GATE PASSED" in result.stdout
        and "GATE DID NOT REACH COMPLETION" not in result.stdout
        and measured_success(result.stdout)
        and (not deep or "This IS the deep profile (--gate)" in result.stdout)
    )


def failed_closed(result: subprocess.CompletedProcess[str]) -> bool:
    return (
        result.returncode == 5
        and "GATE PASSED" not in result.stdout
        and "GATE DID NOT REACH COMPLETION" in result.stdout
    )


def prepare(source: Path, subject: str, parent: Path, label: str) -> Path:
    root = parent / label
    cloned = run(["git", "clone", "--no-hardlinks", "--local", str(source), str(root)], source)
    if cloned.returncode != 0:
        raise RuntimeError(f"{label} clone: {cloned.stdout}")
    must(["git", "checkout", "--detach", subject], root, f"{label} checkout")
    submodules = run(
        ["git", "-c", "protocol.file.allow=always", "submodule", "update", "--init", "--recursive"],
        root, timeout=300,
    )
    if submodules.returncode != 0:
        raise RuntimeError(f"{label} submodules: {submodules.stdout}")
    source_modules = source / "ts/node_modules"
    target_modules = root / "ts/node_modules"
    if not source_modules.is_dir():
        raise RuntimeError("source ts/node_modules is absent")
    if not target_modules.exists():
        target_modules.symlink_to(source_modules, target_is_directory=True)
    if must(["git", "rev-parse", "HEAD"], root, f"{label} identity").strip() != subject:
        raise RuntimeError(f"{label} identity mismatch")
    if must(
        ["git", "status", "--porcelain", "--untracked-files=no"], root,
        f"{label} clean status",
    ):
        raise RuntimeError(f"{label} clone has tracked changes before mutation")
    return root


def exact_diff(root: Path, names: set[str]) -> bool:
    observed = set(filter(None, must(["git", "diff", "--name-only"], root, "diff names").splitlines()))
    return observed == names


def gate(root: Path, log_dir: Path, case: str, deep: bool = False) -> tuple[subprocess.CompletedProcess[str], float]:
    args = ["./scripts/test.sh"] + (["--gate"] if deep else [])
    started = time.monotonic()
    result = run(args, root, timeout=1800)
    elapsed = time.monotonic() - started
    (log_dir / f"{case}.raw.log").write_text(result.stdout)
    return result, elapsed


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: a-floors-gate.py <source-repository> <exact-commit> <log-directory>", file=sys.stderr)
        return 2
    source = Path(sys.argv[1]).resolve()
    subject = sys.argv[2]
    log_dir = Path(sys.argv[3]).resolve()
    if not re.fullmatch(r"[0-9a-f]{40}", subject):
        print("preflight: exact lowercase 40-hex commit required", file=sys.stderr)
        return 2
    if must(["git", "cat-file", "-t", subject], source, "subject type").strip() != "commit":
        print("preflight: subject is not a commit", file=sys.stderr)
        return 2
    if must(["git", "status", "--porcelain", "--untracked-files=no"], source, "source status"):
        print("preflight: source has tracked changes", file=sys.stderr)
        return 2
    for command in ("bash", "git", "forge", "npm", "python3"):
        probe = run(["command", "-v", command], source) if command == "command" else None
        if subprocess.run(["bash", "-lc", f"command -v {command}"], stdout=subprocess.DEVNULL).returncode != 0:
            print(f"preflight: command unavailable: {command}", file=sys.stderr)
            return 2
    log_dir.mkdir(parents=True, exist_ok=True)
    if any(log_dir.iterdir()):
        print("preflight: log directory must be empty", file=sys.stderr)
        return 2

    print("A-FLOORS serial top-level gate contract", flush=True)
    print(f"subject={subject}", flush=True)
    print(f"baseline={BASELINE}", flush=True)
    print(f"harness_sha256={digest(Path(__file__))}", flush=True)
    print("execution=serial; each case has an independent exact-commit clone", flush=True)

    try:
        with tempfile.TemporaryDirectory(prefix="a-floors-gates.") as temp_name:
            temp = Path(temp_name)

            root = prepare(source, subject, temp, "g0-fast-unchanged")
            result, elapsed = gate(root, log_dir, "G0-fast-unchanged")
            record("CONTROL", "G0-fast-unchanged", completed(result), elapsed,
                   "unchanged fast gate completes with measured 103/550/221/7/78/30")

            root = prepare(source, subject, temp, "g1-fast-reader")
            replace_current_floor_paragraph(root)
            diff_ok = exact_diff(root, {"docs/session-state.md"})
            result, elapsed = gate(root, log_dir, "G1-fast-reader")
            held = (
                diff_ok and failed_closed(result) and named_reader_refusal(result.stdout)
                and measured_success(result.stdout)
            )
            record("REQUIRED", "G1-fast-reader", held, elapsed,
                   "wrong current publication is named; later green stages cannot mask refusal")

            root = prepare(source, subject, temp, "g2-deep-unchanged")
            result, elapsed = gate(root, log_dir, "G2-deep-unchanged", deep=True)
            record("CONTROL", "G2-deep-unchanged", completed(result, deep=True), elapsed,
                   "unchanged deep gate alone completes and identifies the deep profile")

            root = prepare(source, subject, temp, "g3-deep-reader")
            replace_current_floor_paragraph(root)
            diff_ok = exact_diff(root, {"docs/session-state.md"})
            result, elapsed = gate(root, log_dir, "G3-deep-reader", deep=True)
            held = (
                diff_ok and failed_closed(result) and named_reader_refusal(result.stdout)
                and measured_success(result.stdout)
                and "This IS the deep profile (--gate)" not in result.stdout
                and "corpus: 50 fixtures executed; committed views verified FILE BY FILE" in result.stdout
            )
            record("REQUIRED", "G3-deep-reader", held, elapsed,
                   "deep path names the same defect, later stages run, completion remains absent")

            root = prepare(source, subject, temp, "g4-raised-control")
            set_planned_floors(root)
            diff_ok = exact_diff(root, {"scripts/test.sh"}) or exact_diff(root, set())
            result, elapsed = gate(root, log_dir, "G4-raised-control")
            planned_lines = (
                "foundry: 103 tests (floor 103)" in result.stdout
                and "typescript: 550 tests (floor 550)" in result.stdout
            )
            record("CONTROL", "G4-raised-control", diff_ok and completed(result) and planned_lines,
                   elapsed, "planned 103/550 floors preserve the unchanged frozen B/C suites")

            root = prepare(source, subject, temp, "g5-delete-events")
            set_planned_floors(root)
            (root / B_EVENTS).unlink()
            diff_ok = exact_diff(root, {"scripts/test.sh", B_EVENTS}) or exact_diff(root, {B_EVENTS})
            result, elapsed = gate(root, log_dir, "G5-delete-events")
            held = (
                diff_ok and failed_closed(result)
                and "FLOOR BREACHED — foundry tests: 92, floor 103" in result.stdout
                and "typescript: 550 tests (floor 550)" in result.stdout
                and re.search(r"(?m)^\s*suite 221 .* samples 7 .* tamper 78 cases / 30 modes", result.stdout)
                is not None
            )
            record("REQUIRED", "G5-delete-events", held, elapsed,
                   "deleting the frozen eleven-test file breaches only the 103 Foundry floor")

            root = prepare(source, subject, temp, "g6-delete-snapshot")
            set_planned_floors(root)
            (root / C_SNAPSHOT).unlink()
            diff_ok = exact_diff(root, {"scripts/test.sh", C_SNAPSHOT}) or exact_diff(root, {C_SNAPSHOT})
            result, elapsed = gate(root, log_dir, "G6-delete-snapshot")
            held = (
                diff_ok and failed_closed(result)
                and "foundry: 103 tests (floor 103)" in result.stdout
                and "FLOOR BREACHED — typescript tests: 527, floor 550" in result.stdout
                and re.search(r"(?m)^\s*suite 221 .* samples 7 .* tamper 78 cases / 30 modes", result.stdout)
                is not None
            )
            record("REQUIRED", "G6-delete-snapshot", held, elapsed,
                   "deleting the frozen twenty-three-test file breaches only the 550 TypeScript floor")
    except (RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"INSTRUMENT SETUP FAILURE: {exc}", file=sys.stderr)
        return 2

    (log_dir / "matrix.tsv").write_text(
        "case\tkind\tstatus\telapsed_seconds\tdescription\n"
        + "".join("\t".join(row) + "\n" for row in rows)
    )
    print("\nA-FLOORS gate summary")
    print(f"REQUIRED {required_held}/{required_total}")
    print(f"CONTROL {control_held}/{control_total}")
    if control_held != control_total:
        print("INSTRUMENT INVALID: control failure")
        return 2
    if required_held != required_total:
        print("PRE-REPAIR GATE DEFECTS OBSERVED")
        return 1
    print("A_FLOORS_GATE_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
