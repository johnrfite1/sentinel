#!/usr/bin/env python3
"""Frozen focused test contract for Sentinel D-CLAIMS.

Clones the named exact commit and mutates only that private clone.
"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

BASELINE = "1e7761be051422ad8091b203df375ddcfb7d1208"
S1_SHA256 = "25dcefcade99e9e45be0c482f3dc5141f4d25335a920fabe1012303c7d7caf68"
S2_PREFIX_SHA256 = "470ec1de8ee696a2875334a7873e8e02504ea27d10676cb1a0018668097ba02f"
CHECKER_SHA256 = "95b65a02bdfc8436e4739b7e5ef90b803964236a86173ed5b8f3c6cc139f7a46"
B_EVENTS_SHA256 = "2a9219cc5138858b012b0bc56069490db3dd7d1963b73ccc19c28a48ce2b029e"
C_SNAPSHOT_SHA256 = "29a673560e89b639b6635661706a368454c9969a04c5d37c4f6c15229df3dd8a"
S2_PREFIX_MARK = "## 11. What is NOT in evidence"
BLOCKER1_START = "1. **The signed Gate S1 pack"
BLOCKER1_END = "2. **`E3` is an open fork"
D6_FALSE = "so the refusal detail now distinguishes them"
D6_TRUTH = (
    "The signed RefusalRecord has no detail field; SIGNER_CHAIN_UNSTABLE remains "
    "one public code for both (a) and (b). Distinguishing text exists only on "
    "ChainUnstableError, which attest.ts does not put on the wire."
)
D4B_NEITHER = "NEITHER the signer nor the verifier"
D4B_OPEN = "Both are open (v1.1 register)"
D4B_TRUTH_A = "The D-010 verifier compares those fields to the presented action and mandate"
D4B_TRUTH_B = (
    "Register E4 is VERIFIER HALF BUILT · SIGNER HALF DELIBERATELY NOT BUILT, "
    "not an open defect."
)
D1_FALSE = "; it does not."
D1_TRUTH = "FALSE SINCE A-074; THE COMPARISON IS BUILT"
D2_FALSE = "Ten minus the five fixed leaves six"
D2_TRUTH = "Ten minus four wholly-removed entries is six"
VARIANTS = {
    "baseline",
    "fix-d6",
    "fix-all",
    "break-s1",
    "break-s2-prefix",
    "break-floors",
    "break-bevents",
    "break-d014",
}

required_total = required_held = control_total = control_held = 0
rows: list[tuple[str, str, str, str]] = []


def record(kind: str, case: str, held: bool, description: str) -> None:
    global required_total, required_held, control_total, control_held
    status = "PASS" if held else "FAIL"
    print(f"  {case:<22} {kind:<8} {status:<4}  {description}")
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


def wrap_norm(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def comment_norm(text: str) -> str:
    return wrap_norm(re.sub(r"(?m)^\s*\*", " ", text))


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if text.count(old) != 1:
        raise RuntimeError(f"anchor count {path}:{old!r}={text.count(old)}")
    path.write_text(text.replace(old, new, 1))


def region(text: str, start: str, end: str) -> str:
    i = text.index(start)
    j = text.index(end, i)
    return text[i:j]


def s2_prefix_digest(text: str) -> str:
    return hashlib.sha256(text[: text.index(S2_PREFIX_MARK)].encode()).hexdigest()


def refusal_record_has_detail(src: str) -> bool:
    body = region(src, "export interface RefusalRecord {", "export interface Refusal {")
    return re.search(r"\bdetail\s*[?:]", body) is not None


D6_OLD = (
    "**A record naming one cause for two conditions is the\n"
    "     * shape this project keeps paying for**, so the refusal detail now distinguishes them."
)
D6_NEW = (
    "**A record naming one cause for two conditions is the\n"
    "     * shape this project keeps paying for.** "
    + D6_TRUTH
)
D4A_OLD = "`EVAL_ACTION_TARGET_MATCHES_MANDATE` must PASS."
D4A_NEW = "`EVAL_TARGET_BOUND` must PASS."
D4B_OLD = (
    " * bundle also carries `normalizedAction` and `expectedEffects`, and those are checked by\n"
    " * NEITHER the signer nor the verifier — the receipt's `evidenceHash` commits to them, so they\n"
    " * are tamper-evident, but nothing compares them to the action and the mandate they purport to\n"
    " * describe. A bundle can therefore state expected effects that its own action does not imply\n"
    " * and still verify.\n"
    " *\n"
    " * Whether the SIGNER should compare them is a D-014 question and not an agent's to answer:\n"
    " * D-014 deliberately kept conformance out of the signer. Whether the VERIFIER should is\n"
    " * cheaper and needs no ruling — it already loads all three documents. Both are open (v1.1\n"
    " * register); this comment states the gap rather than leaving the sentence above to imply it\n"
    " * is closed.\n"
)
D4B_NEW = (
    " * bundle also carries `normalizedAction` and `expectedEffects`. The D-010 verifier compares\n"
    " * those fields to the presented action and mandate (`_evidence_describes_the_bundle`). The\n"
    " * signer still does not.\n"
    " *\n"
    " * Whether the SIGNER should compare them is a D-014 question and not an agent's to answer:\n"
    " * D-014 deliberately kept conformance out of the signer. Register E4 is VERIFIER HALF BUILT\n"
    " * · SIGNER HALF DELIBERATELY NOT BUILT, not an open defect.\n"
)
D1_OLD = 'does the conformance comparison"; it does not.'
D1_NEW = (
    'does the conformance comparison"; ~~it does not.~~ **'
    + D1_TRUTH
    + " (`grep -c decodedSelectorAndParameters verifier/verify.py` = 2). "
    "The signed S1 pack's original sentence is historical signed text and is not "
    "an agent's to rewrite. This item is not a current exit blocker.**"
)
D2_OLD = "Ten minus the five\nfixed leaves six, not five."
D2_NEW = (
    "Four entries were wholly removed (`D-10`, `G-5`, `H-5`, `H-8`); `D-09` is in "
    "both the fixed and accepted sets. Ten minus four wholly-removed entries is six, not five."
)


def apply_d6(root: Path) -> None:
    replace_once(root / "ts/src/signer/protocol.ts", D6_OLD, D6_NEW)


def apply_all(root: Path) -> None:
    apply_d6(root)
    replace_once(root / "ts/test/evaluate.checks.test.ts", D4A_OLD, D4A_NEW)
    replace_once(root / "ts/src/decode/index.ts", D4B_OLD, D4B_NEW)
    replace_once(root / "docs/exit-criterion-packet.md", D1_OLD, D1_NEW)
    replace_once(root / "docs/gate-s2-evidence.md", D2_OLD, D2_NEW)


def score(root: Path) -> None:
    protocol = (root / "ts/src/signer/protocol.ts").read_text()
    protocol_n = comment_norm(protocol)
    decode = (root / "ts/src/decode/index.ts").read_text()
    decode_n = comment_norm(decode)
    checks = (root / "ts/test/evaluate.checks.test.ts").read_text()
    packet = (root / "docs/exit-criterion-packet.md").read_text()
    packet_n = wrap_norm(packet)
    blocker = wrap_norm(region(packet, BLOCKER1_START, BLOCKER1_END))
    s2 = (root / "docs/gate-s2-evidence.md").read_text()
    s2_n = wrap_norm(s2)
    s1 = root / "docs/gate-s1-evidence.md"
    register = wrap_norm((root / "docs/v1-1-register.md").read_text())
    session = wrap_norm((root / "docs/session-state.md").read_text())
    decisions = (root / "docs/decisions.md").read_text()
    handoff = wrap_norm((root / "HANDOFF.md").read_text())
    test_sh = (root / "scripts/test.sh").read_text()
    scripts = {p.name for p in (root / "scripts").glob("check-*.sh")}
    adj2 = wrap_norm((root / "docs/review-2026-08-19-d057-targeted/adjudication/new-findings/ADJ2.md").read_text())
    v3 = wrap_norm((root / "docs/review-2026-08-19-d057-targeted/reviewers/v3/REPORT.md").read_text())

    record("REQUIRED", "R-D6-absent", D6_FALSE not in protocol_n, "protocol.ts lacks the false detail claim")
    record("REQUIRED", "R-D6-truth", D6_TRUTH in protocol_n, "protocol.ts carries D6_TRUTH")
    record("REQUIRED", "R-D4a-absent", "EVAL_ACTION_TARGET_MATCHES_MANDATE" not in checks, "evaluate.checks.test.ts lacks the fictitious code")
    record("REQUIRED", "R-D4b-neither", D4B_NEITHER not in decode_n, "decode/index.ts lacks NEITHER signer nor verifier")
    record("REQUIRED", "R-D4b-open", D4B_OPEN not in decode_n, "decode/index.ts lacks Both are open")
    record("REQUIRED", "R-D4b-truth", D4B_TRUTH_A in decode_n and D4B_TRUTH_B in decode_n, "decode/index.ts carries both D4B_TRUTH fragments")
    record("REQUIRED", "R-D1-absent", D1_FALSE not in blocker, "packet BLOCKER 1 lacks unstruck ; it does not.")
    record("REQUIRED", "R-D1-truth", D1_TRUTH in blocker, "packet BLOCKER 1 carries D1_TRUTH")
    record("REQUIRED", "R-D2-absent", D2_FALSE not in s2_n, "gate-s2 §11.0 lacks Ten minus the five")
    record("REQUIRED", "R-D2-truth", D2_TRUTH in s2_n, "gate-s2 §11.0 carries Ten minus four wholly-removed")

    record("CONTROL", "C-D6-a", "(a) the head MOVED" in protocol_n, "(a) chain-moved condition remains")
    record("CONTROL", "C-D6-b", "(b) the head had NO HASH" in protocol_n, "(b) pending-head condition remains")
    record("CONTROL", "C-D6-no-detail", not refusal_record_has_detail(protocol), "RefusalRecord has no detail field")
    record("CONTROL", "C-D6-fatal", 'SIGNER_CHAIN_UNSTABLE: "FATAL"' in protocol, "SIGNER_CHAIN_UNSTABLE stays FATAL")
    record("CONTROL", "C-D6-d057", "D-057(4)" in protocol, "D-057(4) remains in the NatSpec")
    record("CONTROL", "C-D4a-real", "EVAL_TARGET_BOUND" in checks, "evaluate.checks.test.ts still asserts EVAL_TARGET_BOUND")
    record("CONTROL", "C-D4b-d014", "D-014 deliberately kept conformance out of the signer" in decode_n, "D-014 signer exclusion remains")
    record("CONTROL", "C-E4-register", "SIGNER HALF DELIBERATELY NOT BUILT" in register, "register E4 signer half remains deliberately unbuilt")
    record("CONTROL", "C-D1-3b", "FALSE SINCE A-074; CORRECTED 2026-08-19" in packet_n, "packet §3b already-corrected row remains")
    record("CONTROL", "C-D1-s1", digest(s1) == S1_SHA256, "signed gate-s1-evidence.md bytes unchanged")
    record("CONTROL", "C-D2-prefix", s2_prefix_digest(s2) == S2_PREFIX_SHA256, "gate-s2 bytes before §11 unchanged")
    record("CONTROL", "C-D2-six", "WHAT IS ACCEPTED TODAY IS SIX" in s2_n and "`G-3`" in s2_n, "accepted set still names six including G-3")
    record("CONTROL", "C-D2-struck", "FIVE OF THESE TEN ARE NO LONGER ACCEPTED LIMITS" in s2_n, "struck five-of-ten sentence remains")
    record("CONTROL", "C-D2-packet-ten", "The ten §11.0 accepted limits" in packet_n, "packet NON-BLOCKER historical ten remains")
    record("CONTROL", "C-session-ten", "ten accepted as documented limits" in session, "dated round-five ten remains in session-state")
    record("CONTROL", "C-A077", "**A-077 (2026-08-19)" in decisions, "A-077 heading is not rewritten away")
    record("CONTROL", "C-A080", '~~"COMPLETE THROUGH REVERIFICATION"~~' in handoff, "HANDOFF A-080 strike remains")
    record("CONTROL", "C-13-7", "the `description` SUB-FIELD is compared to nothing" in register, "register §13.7 true description claim remains")
    record("CONTROL", "C-floors", bool(re.search(r"(?m)^FOUNDRY_MIN_TESTS=103$", test_sh) and re.search(r"(?m)^TS_MIN_TESTS=550$", test_sh)), "live floors remain 103/550")
    record("CONTROL", "C-checker", digest(root / "scripts/check-suite-floors.sh") == CHECKER_SHA256, "A-FLOORS checker bytes unchanged")
    record("CONTROL", "C-B-EVENTS", digest(root / "contracts/test/SentinelVault.events.t.sol") == B_EVENTS_SHA256, "B-EVENTS test bytes unchanged")
    record("CONTROL", "C-C-SNAPSHOT", digest(root / "ts/test/vault.snapshot.classification.test.ts") == C_SNAPSHOT_SHA256, "C-SNAPSHOT test bytes unchanged")
    record("CONTROL", "C-no-second-checker", "check-claims.sh" not in scripts and "check-prose.sh" not in scripts and "check-suite-floors.sh" in scripts, "no second claim/floor checker")
    record("CONTROL", "C-no-gate-wire", "d-claims" not in test_sh, "test.sh does not invoke d-claims")
    record("CONTROL", "C-hist-adj2", D4B_OPEN in adj2, "historical ADJ2 quote of Both are open remains")
    record("CONTROL", "C-hist-v3", D6_FALSE in v3, "historical v3 quote of the detail claim remains")


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("usage: d-claims.py <source-repository> [exact-commit]", file=sys.stderr)
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
    variant = os.environ.get("D_CLAIMS_VARIANT", "baseline")
    if variant not in VARIANTS:
        print("preflight: unknown D_CLAIMS_VARIANT", file=sys.stderr)
        return 2
    matrix_path = os.environ.get("D_CLAIMS_MATRIX")
    self_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(f"D-CLAIMS focused harness sha256 {self_sha}")
    print(f"subject {subject} variant {variant}")
    with tempfile.TemporaryDirectory(prefix="d-claims.") as temp:
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
        if variant == "fix-d6":
            apply_d6(root)
        elif variant == "fix-all":
            apply_all(root)
        elif variant == "break-s1":
            path = root / "docs/gate-s1-evidence.md"
            path.write_text(path.read_text() + "\n")
        elif variant == "break-s2-prefix":
            path = root / "docs/gate-s2-evidence.md"
            text = path.read_text()
            mark = S2_PREFIX_MARK
            path.write_text(text.replace(mark, " \n" + mark, 1))
        elif variant == "break-floors":
            replace_once(root / "scripts/test.sh", "FOUNDRY_MIN_TESTS=103", "FOUNDRY_MIN_TESTS=92")
        elif variant == "break-bevents":
            path = root / "contracts/test/SentinelVault.events.t.sol"
            path.write_text(path.read_text() + "\n")
        elif variant == "break-d014":
            replace_once(
                root / "ts/src/decode/index.ts",
                "D-014 deliberately kept conformance out of the signer.",
                "conformance remains out of the signer.",
            )
        score(root)
    print(
        f"REQUIRED {required_held}/{required_total}  "
        f"CONTROL {control_held}/{control_total}"
    )
    if matrix_path:
        dest = Path(matrix_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        body = "case\tkind\tstatus\tdescription\n" + "".join(
            f"{case}\t{kind}\t{status}\t{description}\n"
            for case, kind, status, description in rows
        )
        dest.write_text(body)
        print(f"matrix sha256 {hashlib.sha256(dest.read_bytes()).hexdigest()}")
    complete = (
        required_total == 10
        and required_held == required_total
        and control_total > 0
        and control_held == control_total
    )
    if complete:
        print("D_CLAIMS_FOCUSED_COMPLETE")
        return 0
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"preflight: {exc}", file=sys.stderr)
        raise SystemExit(2)
