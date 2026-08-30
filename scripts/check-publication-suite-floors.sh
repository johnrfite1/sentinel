#!/usr/bin/env bash
# Sentinel — publication-suite floors (F6; closure evidence for R-A018-06 and R-A018-16).
#
# WHY. `scripts/check-suite-floors.sh` prints six floors and none of them covers
# `verifier/test_publication_verifier.py` or `verifier/test_publication_override.py`; the gate
# loads only `test_verifier` (grep `VERIFIER_MIN_` in `scripts/test.sh`). Those two files ARE
# the closure evidence for R-A018-06 ("test the two uncovered modules") and R-A018-16, and
# they could be deleted, weakened, or go red with no mechanical signal whatsoever. AGENTS.md,
# "Mechanically Enforced Project Rules": a durable project rule that can be checked
# mechanically gets a check, not prose.
#
# WHY A "MUST BE GREEN" FLOOR WOULD BE WRONG, AND WHY A COUNT ALONE WOULD BE TOO.
# Both files contain tests that are RED ON PURPOSE. They were written by an independent
# author who is forbidden to edit the module under test (D-058(1), A-028), so a deferred item
# cannot be marked `expectedFailure` from either side — the reds are the record of work that
# is deliberately not done, and two of them are reserved to John. Demanding green would demand
# unauthorised work. But a bare count is no better: with 77 of 81 required to pass, a NEW
# failure hides perfectly behind a red that somebody fixed, and the guard reports the same
# number for a healthy suite and a regressed one.
#
# So the assertion is **N pass AND exactly these named tests fail**. Every direction moves it:
#
#   * a new failure          -> an undeclared red, named
#   * a declared red goes green -> the declaration is stale, OR somebody did work reserved to
#                              John. The guard cannot tell those apart and does not try; it
#                              says so and stops.
#   * a red test deleted or renamed -> declared red missing from the suite
#   * a passing test deleted -> pass count below floor
#   * a test skipped         -> reported. A skip is evidence that did not run.
#
# HOW TO UPDATE IT. The declaration below is the only thing to edit, and it is the only copy.
# Adding a passing test needs no edit at all — the floor is a floor. Changing a RED line means
# asserting that a deliberate red has been closed, so say which register item authorised it.
# **R-A018-17 and R-A018-18 are reserved to John (register §3).** An agent that finds one of
# those green has found either its own unauthorised work or somebody else's, and must report
# it rather than update this block to match.
#
# Usage:
#   ./scripts/check-publication-suite-floors.sh                 run the suites and enforce
#   ./scripts/check-publication-suite-floors.sh --print-floors   print the declaration only
#
# EXIT STATUS. 0 clean · 1 findings · 2 refused / could not check. Exit 2 is never a pass.
#
# COST. It runs both suites for real — roughly 90 seconds — because a floor asserted from
# anything other than a run is the defect one layer up (see check-suite-floors.sh's header:
# "THIS PRINTS THE FLOORS, NOT THE COUNTS").

set -uo pipefail

# =====================================================================================
#  THE DECLARATION — THE ONE PLACE TO EDIT. Nothing below reads floors from anywhere else.
#
#    FLOOR <module>  <minimum number of tests that must PASS>
#    RED   <module>  <Class.test_method>   <register item — why it is red>
#
#  Measured 2026-08-30 by running both files.
# =====================================================================================
DECLARATION=$(cat <<'FLOORS'
# --- verifier/test_publication_verifier.py — 81 tests, 77 green, 4 red on purpose. ----
#     The four are recorded in the `KNOWN RED TESTS IN THE FROZEN CONTRACT` block at the
#     top of verifier/verify_publication.py; this is that record made executable.
#     81/81 would mean somebody implemented work that is not authorised.
FLOOR test_publication_verifier 77
RED   test_publication_verifier TestDeploymentIdentityIsNotBound.test_a_fabricated_runtime_code_hash_is_echoed_as_authenticated   R-A018-04 deferred: needs live chain state, no chain is named yet
RED   test_publication_verifier TestDeploymentIdentityIsNotBound.test_two_contradictory_manifests_cannot_both_certify             R-A018-04 deferred: needs live chain state, no chain is named yet
RED   test_publication_verifier TestDeploymentIdentityIsNotBound.test_the_result_names_the_block_its_claims_are_true_at           R-A018-04 deferred: needs live chain state, no chain is named yet
RED   test_publication_verifier TestExactActionIsEnforced.test_calldata_redirecting_the_mandated_beneficiary_is_refused           R-A018-17 RESERVED TO JOHN: decoding calldata is new capability and a scope ruling

# --- verifier/test_publication_override.py — 61 tests, 59 green, 2 red on purpose. ----
#     R-A018-18 asks whether an override credential should be examined on every path or
#     refused as an uncertifiable shape. The register says in terms: "Which of the two is a
#     scope decision and is John's." Neither test may be turned green by an agent.
#
#     THIS FILE HAD FOUR REDS EARLIER ON 2026-08-30. The other two were
#     TestOverrideRefusalsAreDiagnosed.test_a_structurally_incomplete_override_names_the_override
#     and .test_a_non_canonical_override_time_field_names_the_override (R-A018-20), and they
#     are green as of the shape-check and named-window repairs in check_owner_override().
#     Recorded here rather than deleted: if either goes red again, the repair regressed, and
#     the guard will name it as an undeclared red rather than leave you guessing.
FLOOR test_publication_override 59
RED   test_publication_override TestAnUnexaminedOverrideCredentialIsNotCertifiable.test_an_allow_bundle_carrying_an_outsider_override_is_refused   R-A018-18 RESERVED TO JOHN: scope decision
RED   test_publication_override TestAnUnexaminedOverrideCredentialIsNotCertifiable.test_the_owner_signed_case_is_refused_too_or_examined           R-A018-18 RESERVED TO JOHN: scope decision
FLOORS
)
# =====================================================================================
#  END OF THE DECLARATION.
# =====================================================================================

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

MODE="run"
case "${1:-}" in
    "")             MODE="run" ;;
    --print-floors) MODE="print" ;;
    *) echo "  FAIL  unknown argument '$1'; refusing." >&2; exit 2 ;;
esac

if ! command -v python3 >/dev/null 2>&1; then
    echo "  FAIL  python3 not found; publication-suite floor guard refuses." >&2
    exit 2
fi

python3 - "$ROOT" "$MODE" "$DECLARATION" <<'PY'
import io
import contextlib
import os
import sys
import time
import unittest
from pathlib import Path

ROOT, MODE, DECLARATION = Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3]
VERIFIER = ROOT / "verifier"

# --- parse the declaration ------------------------------------------------------------
floors, expected_red, order = {}, {}, []
for number, line in enumerate(DECLARATION.splitlines(), 1):
    text = line.strip()
    if not text or text.startswith("#"):
        continue
    parts = text.split(None, 2)
    kind = parts[0]
    if kind == "FLOOR":
        if len(parts) != 3 or not parts[2].split()[0].isdigit():
            print(f"  FAIL  declaration line {number} is malformed: {text!r}", file=sys.stderr)
            raise SystemExit(2)
        module, value = parts[1], int(parts[2].split()[0])
        floors[module] = value
        expected_red.setdefault(module, {})
        order.append(module)
    elif kind == "RED":
        if len(parts) < 3:
            print(f"  FAIL  declaration line {number} is malformed: {text!r}", file=sys.stderr)
            raise SystemExit(2)
        rest = parts[2].split(None, 1)
        module = parts[1]
        expected_red.setdefault(module, {})[rest[0]] = rest[1].strip() if len(rest) > 1 else ""
    else:
        print(f"  FAIL  declaration line {number} starts with {kind!r}, not FLOOR or RED.",
              file=sys.stderr)
        raise SystemExit(2)

undeclared = sorted(set(expected_red) - set(floors))
if undeclared:
    # A RED line for a module with no FLOOR line is a half-written declaration, and it would
    # silently never be run. Refuse rather than check part of what was asked for.
    print(f"  FAIL  declaration names RED tests for {undeclared} but no FLOOR for them.",
          file=sys.stderr)
    raise SystemExit(2)

if MODE == "print":
    for module in order:
        print(f"  {module + '.py':<38} {floors[module]:>4} pass  "
              f"+ {len(expected_red[module])} declared red")
    print("publication-suite floors: read from scripts/check-publication-suite-floors.sh,")
    print("which is the only copy. Run it to enforce them; this only prints them.")
    raise SystemExit(0)

# --- run ------------------------------------------------------------------------------
sys.path.insert(0, str(VERIFIER))
os.chdir(ROOT)

findings = []
summary = []


def finding(text, *detail):
    findings.append(text)
    findings.extend(f"    {line}" for line in detail)


for module in order:
    source = VERIFIER / f"{module}.py"
    if not source.is_file():
        finding(f"{module}.py IS MISSING from verifier/.",
                "This file is the closure evidence for R-A018-06 / R-A018-16. Its absence is",
                "the exact failure this floor exists to make impossible; it is not a pass.")
        continue

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(module)
    if loader.errors:
        finding(f"{module}.py could not be COLLECTED — the suite is broken, not merely red.",
                *[line for error in loader.errors for line in str(error).splitlines()[:4]])
        continue

    collected = []

    def walk(node):
        for item in node:
            if isinstance(item, unittest.TestSuite):
                walk(item)
            else:
                collected.append(item)

    walk(suite)

    def short(test_id):
        return test_id[len(module) + 1:] if test_id.startswith(module + ".") else test_id

    ids = {short(test.id()) for test in collected}
    result = unittest.TestResult()
    started = time.time()
    # The suites print their own progress and shell out to the verifier; the guard's output
    # is a verdict, so their chatter is captured and only surfaced through the findings.
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        suite.run(result)
    elapsed = time.time() - started

    red = {short(test.id()) for test, _ in result.failures}
    errored = {short(test.id()) for test, _ in result.errors}
    # The one-line reason, kept for the findings below. A guard that says "this test is red"
    # and not why sends the reader back to run the suite by hand, which is the step the guard
    # was supposed to save.
    why = {short(test.id()): trace.strip().splitlines()[-1][:200]
           for test, trace in list(result.failures) + list(result.errors)}
    skipped = {short(test.id()) for test, _ in result.skipped}
    unexpected = {short(test.id()) for test in result.unexpectedSuccesses}
    passing = len(collected) - len(red | errored | skipped | unexpected)
    declared = set(expected_red[module])

    summary.append(
        f"  {module + '.py':<38} {passing:>3}/{len(collected)} pass (floor {floors[module]}) · "
        f"{len(red | errored)} red (declared {len(declared)}) · {elapsed:.0f}s"
    )

    if errored:
        # An ERROR is a crash, never a deliberate red: the declared reds are assertion
        # failures about behaviour that was not implemented, not exceptions escaping a test.
        finding(f"{module}.py: {len(errored)} test(s) ERRORED. An error is never an expected red.",
                *sorted(errored))
    if skipped:
        finding(f"{module}.py: {len(skipped)} test(s) SKIPPED. A skipped test is evidence that "
                f"did not run.", *sorted(skipped))
    if unexpected:
        finding(f"{module}.py: {len(unexpected)} unexpected success(es).", *sorted(unexpected))

    new_red = sorted((red | errored) - declared)
    if new_red:
        detail = []
        for name in new_red:
            detail.append(name)
            detail.append(f"  {why.get(name, '(no detail)')}")
        finding(f"{module}.py: {len(new_red)} UNDECLARED RED test(s) — a regression, or work "
                f"that moved without the declaration moving.", *detail)

    for name in sorted(declared - (red | errored)):
        if name not in ids:
            finding(f"{module}.py: declared red test is MISSING from the suite: {name}",
                    f"Reason on record: {expected_red[module][name]}",
                    "Deleting or renaming a deliberate red erases the record of work that is",
                    "deliberately not done. Restore it, or move the declaration with it.")
        else:
            finding(f"{module}.py: declared red test now PASSES: {name}",
                    f"Reason on record: {expected_red[module][name]}",
                    "Either the declaration is stale, or somebody implemented work that is not",
                    "authorised. This guard cannot tell those apart. If the reason above says",
                    "RESERVED TO JOHN, report it — do not edit the declaration to match.")

    if passing < floors[module]:
        finding(f"{module}.py: {passing} passing, below the floor of {floors[module]}.",
                "Tests were deleted, disabled, or turned red. A floor is a floor: adding tests",
                "never trips it, so this is a subtraction.")

print("publication-suite floors (F6 — R-A018-06, R-A018-16 closure evidence):")
for line in summary:
    print(line)

if findings:
    print()
    for line in findings:
        print(line)
    print()
    print(f"publication-suite floors: {sum(1 for f in findings if not f.startswith('    '))} "
          f"finding(s). Do not weaken this floor to make a run pass (AGENTS.md).")
    print("The declaration is the block at the top of this script and is the only copy.")
    raise SystemExit(1)

print("publication-suite floors: clean — pass counts at or above floor, and the red set is "
      "exactly what is declared.")
PY
exit $?
