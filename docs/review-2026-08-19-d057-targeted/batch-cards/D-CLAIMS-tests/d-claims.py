#!/usr/bin/env python3
"""Frozen focused test contract for Sentinel D-CLAIMS.

Clones the named exact commit and mutates only that private clone.
First correction closes INSTRUMENT-REVIEW-1.md; second closes INSTRUMENT-REVIEW-2.md.
Neither review is edited.
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
D1_BLOCKS = "this alone blocks exit"
D1_TRUTH = "FALSE SINCE A-074; THE COMPARISON IS BUILT"
D2_FALSE = "Ten minus the five fixed leaves six"
D2_FIVE = "FIVE OF THESE TEN ARE NO LONGER ACCEPTED LIMITS"
D2_TRUTH = (
    "Four entries were wholly removed (`D-10`, `G-5`, `H-5`, `H-8`); `D-09` is in "
    "both the fixed and accepted sets. Ten minus four wholly-removed entries is six, not five."
)
D2_D09 = "`D-09` is in both the fixed and accepted sets"
PACKET_TEN = "The ten §11.0 accepted limits"
PACKET_SIX = "The six §11.0 accepted limits"
FROZEN_REASON_CODES = frozenset({
    "SIGNER_DATAHASH_MISMATCH",
    "SIGNER_WRONG_VAULT",
    "SIGNER_WRONG_CHAIN",
    "SIGNER_VAULT_UNREACHABLE",
    "SIGNER_CHAIN_UNSTABLE",
    "SIGNER_DOMAIN_SEPARATOR_MISMATCH",
    "SIGNER_CALLDATA_TOO_SHORT",
    "SIGNER_EVIDENCE_DECODING_MISMATCH",
    "SIGNER_EVIDENCE_DECODING_ABSENT",
    "SIGNER_NOT_ACTIVE_SIGNER",
    "SIGNER_NONCE_MISMATCH",
    "SIGNER_VAULT_PAUSED",
    "SIGNER_ACTION_EXPIRED",
    "SIGNER_NONCE_ALREADY_ATTESTED",
    "SIGNER_MANDATE_NOT_ACTIVE",
    "SIGNER_POLICY_NOT_ACTIVE",
    "SIGNER_ACTION_BINDING_STALE",
    "SIGNER_MANDATE_TARGET_MISMATCH",
    "SIGNER_MANDATE_SELECTOR_MISMATCH",
    "SIGNER_MANDATE_VALUE_EXCEEDED",
    "SIGNER_MANDATE_WINDOW",
    "SIGNER_MANDATE_PRINCIPAL_MISMATCH",
    "SIGNER_MANDATE_POLICY_LINK_MISMATCH",
    "SIGNER_MANDATE_SCOPE_MISMATCH",
    "SIGNER_TARGET_CODEHASH_MISMATCH",
    "SIGNER_SIMULATION_BLOCK_MISMATCH",
    "SIGNER_ANCHOR_NOT_OBSERVED",
    "SIGNER_POLICY_SCOPE_MISMATCH",
    "SIGNER_POLICY_OPERATION_MISMATCH",
    "SIGNER_POLICY_VALUE_EXCEEDED",
    "SIGNER_POLICY_WINDOW",
    "SIGNER_UNSUPPORTED_OPERATION",
    "SIGNER_VAULT_VALUE_CAP_EXCEEDED",
    "SIGNER_VAULT_TARGET_NOT_ALLOWED",
    "SIGNER_VAULT_SELECTOR_NOT_ALLOWED",
})
REQUIRED_N = 14
VARIANTS = {
    "baseline",
    "fix-d6",
    "fix-all",
    "break-s1",
    "break-s2-prefix",
    "break-floors",
    "break-bevents",
    "break-d014",
    "break-reason-split",
    "break-reason-quoted",
    "break-reason-space",
    "break-reason-comment",
    "break-reason-newline",
    "break-live-strike",
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


def phrase_is_live(norm: str, phrase: str) -> bool:
    """True when `phrase` is human-readable in wrap-normalized Markdown.

    A closed `~~…~~` span may keep the words for drift. The phrase is live if any
    occurrence has at least one unstruck character (interior `exi~~t~~`, split
    `~~this alone ~~blocks exit`), or if a `~~` span is left unclosed.
    """
    chars: list[tuple[str, bool]] = []
    i = 0
    struck = False
    while i < len(norm):
        if norm.startswith("~~", i):
            struck = not struck
            i += 2
            continue
        chars.append((norm[i], struck))
        i += 1
    unclosed = struck
    text = "".join(ch for ch, _ in chars)
    start = 0
    plen = len(phrase)
    while True:
        found = text.find(phrase, start)
        if found < 0:
            return False
        span = chars[found:found + plen]
        if unclosed or not all(flag for _, flag in span):
            return True
        start = found + 1


def _skip_ws_comments(body: str, i: int) -> int:
    n = len(body)
    while i < n:
        ch = body[i]
        if ch in " \t\n\r":
            i += 1
            continue
        if body.startswith("//", i):
            nl = body.find("\n", i)
            i = n if nl < 0 else nl + 1
            continue
        if body.startswith("/*", i):
            end = body.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue
        break
    return i


def _read_quoted(body: str, i: int) -> tuple[str, int]:
    quote = body[i]
    i += 1
    start = i
    n = len(body)
    while i < n and body[i] != quote:
        i += 2 if body[i] == "\\" else 1
    return body[start:i], (i + 1 if i < n else i)


def reason_object_keys(body: str) -> frozenset[str]:
    """Finite REASON_SEVERITY key grammar, not a TypeScript parser.

    Keys: unquoted IDENT, "IDENT" / 'IDENT', or ["IDENT"] / ['IDENT'].
    Whitespace and // or /* */ comments may sit between the key and `:`.
    IDENT scored here is [A-Z][A-Z0-9_]*.
    """
    keys: list[str] = []
    i = 0
    n = len(body)
    ident = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    scored = re.compile(r"[A-Z][A-Z0-9_]*")
    while True:
        i = _skip_ws_comments(body, i)
        if i >= n or body[i] == "}":
            break
        key: str | None = None
        if body[i] in "\"'":
            key, i = _read_quoted(body, i)
        elif body[i] == "[":
            i += 1
            i = _skip_ws_comments(body, i)
            if i < n and body[i] in "\"'":
                key, i = _read_quoted(body, i)
            i = _skip_ws_comments(body, i)
            if i < n and body[i] == "]":
                i += 1
        else:
            match = ident.match(body, i)
            if match:
                key = match.group(0)
                i = match.end()
            else:
                i += 1
                continue
        i = _skip_ws_comments(body, i)
        if i >= n or body[i] != ":":
            continue
        i += 1
        if key and scored.fullmatch(key):
            keys.append(key)
        i = _skip_ws_comments(body, i)
        if i < n and body[i] in "\"'":
            _, i = _read_quoted(body, i)
        else:
            match = ident.match(body, i)
            if match:
                i = match.end()
        i = _skip_ws_comments(body, i)
        if i < n and body[i] == ",":
            i += 1
    return frozenset(keys)


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


def reason_codes(src: str) -> frozenset[str]:
    start = src.index("export const REASON_SEVERITY = {")
    end = src.index("} as const satisfies Record<string, Severity>;", start)
    inner = src[src.index("{", start) + 1:end]
    return reason_object_keys(inner)


def insert_reason_after_unstable(root: Path, entry: str) -> None:
    replace_once(
        root / "ts/src/signer/protocol.ts",
        '    SIGNER_CHAIN_UNSTABLE: "FATAL",\n',
        '    SIGNER_CHAIN_UNSTABLE: "FATAL",\n' + entry,
    )


def apply_live_strike(root: Path) -> None:
    """Review 2: interior/split ~~ spans that leave the watched claim readable."""
    apply_all(root)
    replace_once(
        root / "docs/exit-criterion-packet.md",
        "~~Under C1 condition 4 this alone blocks exit.~~",
        "Under C1 condition 4 this alone blocks exi~~t~~.",
    )
    replace_once(
        root / "docs/gate-s2-evidence.md",
        D2_FIVE_NEW,
        D2_FIVE_OLD.replace("FIVE OF THESE TEN", "FI~~V~~E OF THESE TEN", 1),
    )
    replace_once(
        root / "docs/exit-criterion-packet.md",
        PACKET_SIX_NEW,
        PACKET_SIX_NEW + "\n- The t~~e~~n §11.0 accepted limits — subject to **T1**.",
    )


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
D1_OLD = (
    'does the conformance comparison"; it does not. **This is not an\n'
    "   agent's to close — it changes what the product guarantees, and it sits in signed text.**\n"
    "   Under C1 condition 4 this alone blocks exit."
)
D1_NEW = (
    'does the conformance comparison"; ~~it does not.~~ **'
    + D1_TRUTH
    + " (`grep -c decodedSelectorAndParameters verifier/verify.py` = 2). "
    "The signed S1 pack's original sentence is historical signed text and is not "
    "an agent's to rewrite. This item is not a current exit blocker.** "
    "~~Under C1 condition 4 this alone blocks exit.~~"
)
D2_OLD = "Ten minus the five\nfixed leaves six, not five."
D2_NEW = D2_TRUTH
D2_FIVE_OLD = (
    "**FIVE OF THESE TEN ARE NO LONGER ACCEPTED LIMITS — THEY ARE FIXED (A-076, 2026-08-18, under\n"
    "D-056(a)). `D-09(c)`, `D-10`, `G-5`, `H-5` and `H-8` were repaired at John's direction in the\n"
    "bounded pre-review stabilization checkpoint.**"
)
D2_FIVE_NEW = "~~" + D2_FIVE_OLD + "~~"
PACKET_TEN_OLD = "- The ten §11.0 accepted limits — subject to **T1**."
PACKET_SIX_NEW = "- The six §11.0 accepted limits — subject to **T1**."


def apply_d6(root: Path) -> None:
    replace_once(root / "ts/src/signer/protocol.ts", D6_OLD, D6_NEW)


def apply_all(root: Path) -> None:
    apply_d6(root)
    replace_once(root / "ts/test/evaluate.checks.test.ts", D4A_OLD, D4A_NEW)
    replace_once(root / "ts/src/decode/index.ts", D4B_OLD, D4B_NEW)
    replace_once(root / "docs/exit-criterion-packet.md", D1_OLD, D1_NEW)
    replace_once(root / "docs/exit-criterion-packet.md", PACKET_TEN_OLD, PACKET_SIX_NEW)
    replace_once(root / "docs/gate-s2-evidence.md", D2_OLD, D2_NEW)
    replace_once(root / "docs/gate-s2-evidence.md", D2_FIVE_OLD, D2_FIVE_NEW)


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

    record("REQUIRED", "R-D6-absent", not phrase_is_live(protocol_n, D6_FALSE), "protocol.ts has no live false detail claim")
    record("REQUIRED", "R-D6-truth", D6_TRUTH in protocol_n, "protocol.ts carries D6_TRUTH")
    record("REQUIRED", "R-D4a-absent", "EVAL_ACTION_TARGET_MATCHES_MANDATE" not in checks, "evaluate.checks.test.ts lacks the fictitious code")
    record("REQUIRED", "R-D4b-neither", not phrase_is_live(decode_n, D4B_NEITHER), "decode/index.ts has no live NEITHER signer nor verifier")
    record("REQUIRED", "R-D4b-open", not phrase_is_live(decode_n, D4B_OPEN), "decode/index.ts has no live Both are open")
    record("REQUIRED", "R-D4b-truth", D4B_TRUTH_A in decode_n and D4B_TRUTH_B in decode_n, "decode/index.ts carries both D4B_TRUTH fragments")
    record("REQUIRED", "R-D1-absent", not phrase_is_live(blocker, "it does not."), "BLOCKER 1 has no live it does not.")
    record("REQUIRED", "R-D1-blocks", not phrase_is_live(blocker, D1_BLOCKS), "BLOCKER 1 has no live this alone blocks exit")
    record("REQUIRED", "R-D1-truth", D1_TRUTH in blocker, "packet BLOCKER 1 carries D1_TRUTH")
    record("REQUIRED", "R-D1-ten", not phrase_is_live(packet_n, PACKET_TEN), "packet has no live The ten §11.0 accepted limits")
    record("REQUIRED", "R-D1-six", PACKET_SIX in packet_n, "packet carries The six §11.0 accepted limits")
    record("REQUIRED", "R-D2-absent", not phrase_is_live(s2_n, D2_FALSE), "gate-s2 has no live Ten minus the five")
    record("REQUIRED", "R-D2-five", not phrase_is_live(s2_n, D2_FIVE), "gate-s2 has no live FIVE OF THESE TEN heading")
    record("REQUIRED", "R-D2-truth", D2_TRUTH in s2_n and D2_D09 in s2_n, "gate-s2 carries full D2_TRUTH including D-09 in both sets")

    record("CONTROL", "C-D6-a", "(a) the head MOVED" in protocol_n, "(a) chain-moved condition remains")
    record("CONTROL", "C-D6-b", "(b) the head had NO HASH" in protocol_n, "(b) pending-head condition remains")
    record("CONTROL", "C-D6-no-detail", not refusal_record_has_detail(protocol), "RefusalRecord has no detail field")
    record("CONTROL", "C-D6-fatal", 'SIGNER_CHAIN_UNSTABLE: "FATAL"' in protocol, "SIGNER_CHAIN_UNSTABLE stays FATAL")
    record("CONTROL", "C-D6-codes", reason_codes(protocol) == FROZEN_REASON_CODES, "public ReasonCode set is unchanged")
    record("CONTROL", "C-D6-d057", "D-057(4)" in protocol, "D-057(4) remains in the NatSpec")
    record("CONTROL", "C-D4a-real", "EVAL_TARGET_BOUND" in checks, "evaluate.checks.test.ts still asserts EVAL_TARGET_BOUND")
    record("CONTROL", "C-D4b-d014", "D-014 deliberately kept conformance out of the signer" in decode_n, "D-014 signer exclusion remains")
    record("CONTROL", "C-E4-register", "SIGNER HALF DELIBERATELY NOT BUILT" in register, "register E4 signer half remains deliberately unbuilt")
    record("CONTROL", "C-D1-3b", "FALSE SINCE A-074; CORRECTED 2026-08-19" in packet_n, "packet §3b already-corrected row remains")
    record("CONTROL", "C-D1-s1", digest(s1) == S1_SHA256, "signed gate-s1-evidence.md bytes unchanged")
    record("CONTROL", "C-D2-prefix", s2_prefix_digest(s2) == S2_PREFIX_SHA256, "gate-s2 bytes before §11 unchanged")
    record("CONTROL", "C-D2-six", "WHAT IS ACCEPTED TODAY IS SIX" in s2_n and "`G-3`" in s2_n, "accepted set still names six including G-3")
    record("CONTROL", "C-D2-superseded", "THAT SENTENCE IS FALSE AND IS SUPERSEDED" in s2_n, "§11.0 R4-F1 superseded record remains")
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
            path.write_text(text.replace(S2_PREFIX_MARK, " \n" + S2_PREFIX_MARK, 1))
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
        elif variant == "break-reason-split":
            insert_reason_after_unstable(
                root, '    SIGNER_CHAIN_PENDING_HEAD: "FATAL",\n',
            )
        elif variant == "break-reason-quoted":
            insert_reason_after_unstable(
                root, '    "SIGNER_CHAIN_PENDING_HEAD": "FATAL",\n',
            )
        elif variant == "break-reason-space":
            insert_reason_after_unstable(
                root, '    SIGNER_CHAIN_PENDING_HEAD : "FATAL",\n',
            )
        elif variant == "break-reason-comment":
            insert_reason_after_unstable(
                root, '    SIGNER_CHAIN_PENDING_HEAD /*split*/: "FATAL",\n',
            )
        elif variant == "break-reason-newline":
            insert_reason_after_unstable(
                root, '    SIGNER_CHAIN_PENDING_HEAD\n    : "FATAL",\n',
            )
        elif variant == "break-live-strike":
            apply_live_strike(root)
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
        required_total == REQUIRED_N
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
