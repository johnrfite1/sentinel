#!/usr/bin/env bash
# Sentinel — test vacuity guard (R-A018-24, authorised by D-083(j)).
#
# WHY. A pass-count floor cannot see a vacuous test. During the F7 repair three tests in
# `verifier/test_publication_verifier.py` were GREEN and asserting NOTHING for hours, and
# `scripts/check-publication-suite-floors.sh` was RIGHT the whole time: the pass count and the
# declared red set both matched. The tests ran under `--evaluation-time` behind
# `if completed.returncode == 0:`; that flag became a non-certifying diagnostic that exits 3,
# the guard was never taken, and the assertions inside it never executed. R-A018-08's PASS
# line had no coverage at all while every instrument in this repository reported green.
#
# That is this project's own recorded failure mode — **a probe that is dead and whose silence
# reads like a pass** — reappearing inside the instrument built to prevent it. The tests were
# found by instrumenting a full run with `sys.settrace` plus AST (`coverage` is not installed
# here), not by reading. This file is that probe promoted to a guard.
#
# =====================================================================================
#  WHAT THIS GUARD CATCHES — the precise list, and nothing wider.
# =====================================================================================
#
#   V1  A `test_*` method that unittest never invoked — not collected at all, defined on a
#       class nothing instantiates, or shadowed — or a PASSING test whose body executed not
#       one statement.
#   V2  A test that PASSED during which NO assertion executed at all.
#   V3  A test that PASSED carrying an assertion inside a block that was never entered — a
#       `for` over an empty sequence, an `if` never true. **This is the F7 shape exactly.**
#   V4  A test whose SOURCE contains no assertion anywhere (checked on the syntax tree, so it
#       holds whether the test ran or not).
#   V5  Two `def`s of the same name in one class body: the earlier is unreachable.
#   V6  An assertion whose compared arguments are ALL literal constants — `assertTrue(True)`,
#       `assertEqual(1, 1)`, `assertIn("a", "abc")`. Cannot fail by construction. **Only the
#       assert* methods listed in `LITERAL_CHECKED` below are eligible**, because only for
#       those does this file know which leading arguments are operands and which trailing one
#       is the failure message. Anything not listed is left alone — under-reporting, which is
#       the safe direction for a check whose false positives would be arguments about style.
#
# =====================================================================================
#  WHAT THIS GUARD DOES NOT CATCH. Read this before quoting it as coverage.
# =====================================================================================
#
#   * **AN ASSERTION THAT EXECUTES AND IS MERELY WEAK.** This is the important one and it is
#     not hypothetical. A repaired test's `assertIn("evaluation-time", stdout)` PASSED with
#     the flag fully suppressed, because argparse reprints the module docstring and the
#     docstring mentions the flag in prose. That assertion executed, its arguments were not
#     both literal, and it could in principle fail. **Nothing here sees it.** The instrument
#     that caught it was `scripts/mutate.sh`; reading did not catch it either, and the test
#     author's own first draft had the identical hole.
#   * An assertion computed from the same wrong source on both sides — `assertEqual(f(x), f(x))`.
#   * An assertion against a fixture or stub that has stopped representing the subject.
#   * Vacuity in a test that is RED, ERRORED or SKIPPED. Those are EXCLUDED from V1/V2/V3 and
#     the count of exclusions is printed: a failing test stops at its first failed assertion,
#     so everything after it is legitimately dead and reporting it would be noise. **A test
#     that is both deliberately red and vacuous is therefore invisible here.** That is a real
#     hole, it is stated rather than papered over, and the reds are enumerated by
#     `scripts/check-publication-suite-floors.sh` for anyone who wants to read them by hand.
#   * Anything outside the modules named in the DECLARATION below.
#   * "The assertion cannot fail" IN GENERAL. That is undecidable and this guard does not
#     pretend otherwise. V1/V2/V3 are decidable because they are questions about EXECUTION,
#     observed by tracing a real run; V4/V5/V6 are decidable because they are questions about
#     SYNTAX. Everything between those two is out of reach, and the paragraph above names the
#     concrete case that lives there.
#
# HOW IT ANSWERS THEM. One `sys.settrace` line-tracer over a real `unittest` run of each
# declared module, forked into its own process so no module can contaminate another's run,
# plus an AST pass that locates every statement and every assertion site. A statement counts
# as executed if ANY line of its source span was traced — spans, not single line numbers,
# because a multi-line call does not always report its first line.
#
# ASSERTIONS DELEGATED TO A HELPER STILL COUNT. A test whose body is `self.check_thing()`,
# where `check_thing` is a method in the same file that asserts, is not reported by V2 or V4.
# Delegation is propagated transitively through same-file helpers.
#
# `self.fail(...)` AND `raise` IN A BLOCK THAT WAS NEVER TAKEN ARE NOT FINDINGS. A guard rail
# whose only effect is to fail the test is HEALTHY when it does not fire; V3 fires only on a
# dead `assert*`. Statements inside an `except` handler are excluded for the same reason.
#
# EXIT STATUS. 0 clean · 1 findings · 2 refused / could not check. **Exit 2 is never a pass.**
# The guard refuses rather than reporting a property it did not establish: a module that
# would not import, a suite that collected nothing, or a traced run that observed no lines at
# all means the probe itself was dead, which is the thing this file exists to detect.
#
# COST. It runs three suites for real, under a line tracer. **Measured between 2m15s and 7m
# on the same machine on 2026-08-30**, the spread being entirely other work running alongside
# it; the per-module seconds are printed by every run and are the number to trust. It is wired
# into the DEEP profile (`./scripts/test.sh --gate`) for that reason, which means a vacuous
# test survives a fast run. That is a cost decision and it is stated where it can be argued
# with, not buried.
#
# Usage:
#   ./scripts/check-test-vacuity.sh                      run and enforce
#   ./scripts/check-test-vacuity.sh --print-declaration   print the declaration only

set -uo pipefail

# =====================================================================================
#  THE DECLARATION — THE ONE PLACE TO EDIT. Nothing below reads it from anywhere else.
#
#    MODULE <module>                                    a test module to instrument
#    ACCEPT <module> <V-code> <Class.test_method> <reason>   one KNOWN finding, ratcheted
#
#  AN `ACCEPT` NAMES ONE CHECK ON ONE TEST, not a test. `ACCEPT ... V3 Class.test ...`
#  silences the dead-assertion finding on that test and NOTHING else — if the same test
#  later stops asserting altogether, V2 still fires. A per-test blanket would be a hole
#  shaped exactly like the defect this guard exists to find.
#
#  AN `ACCEPT` LINE IS A RATCHET, NOT A DISMISSAL. It is printed on every run, and if the
#  finding it names goes away the guard reports the declaration as STALE rather than
#  quietly passing — the same shape `check-publication-suite-floors.sh` uses for a declared
#  red that starts passing. Never add one to make a run green: say what makes the dead site
#  correct, or fix the test.
# =====================================================================================
DECLARATION=$(cat <<'VACUITY'
MODULE test_publication_verifier
MODULE test_publication_override
MODULE test_verifier

# --- carried findings ----------------------------------------------------------------
# NOTE FOR WHOEVER EDITS THIS BLOCK: bash 3.2 (the macOS system bash, which runs this)
# mis-parses an APOSTROPHE inside a heredoc nested in $( ), and an odd number of them makes
# the whole script a syntax error a hundred lines further down. Write around them. This
# cost a debugging round; it is recorded so it costs nobody a second one.
#
# Measured 2026-08-30 against the three modules above. **THE TWO PUBLICATION SUITES CARRY
# NOTHING**: every assertion in every passing test executed. Both entries below are in
# `test_verifier.py`, both were found by this guard on its first real run, and both are
# carried rather than fixed because an agent wiring guards may not edit a test file
# (D-058(1), A-028 — the test author and the module author are separate roles). **Neither
# is a dismissal: both are true statements about a real dead assertion, and both are
# printed on every run.** Anyone permitted to edit these tests should.
#
# V3. The test encodes an address, then tries two whitespace-padded spellings of it. The
# encoder REJECTS both outright, so `except EncodingError: continue` fires and the trailing
# `assertNotEqual` is never reached. Rejection IS the property holding, and the other
# assertion in that test (`assertEqual(len(word), 32)`) executes every run — so the TEST is
# not vacuous, but that ASSERTION is dead, and it would stay dead if the encoder regressed
# to accepting a padded spelling and returning a different word. The comment above it says
# the first version "nested assertNotEqual INSIDE assertRaises, where it can never
# execute". This is the second version. Closer, still not reached.
ACCEPT test_verifier V3 TestUnassertedValidation.test_pair_aligned_whitespace_cannot_collide_an_encoded_word   the encoder rejects both padded spellings so the `continue` fires and the assertion is unreachable; rejection is the property holding and the test asserts elsewhere
#
# V6. `self.assertGreater("\U0001f600", "\ufffd")  # opposite by code point` compares two
# string LITERALS. It is a true statement about how Python orders code points and cannot be
# moved by anything in `jcs`; it is a comment written as an assertion. The two assertions
# above it in the same test do the real work and are untouched by this. Carried so that the
# assertion count of that suite is not read as if this one contributed to it.
ACCEPT test_verifier V6 TestJCSStructure.test_key_sorting_is_utf16_code_units   the compared literals are a true statement about how Python orders code points, not about jcs; it is a comment written as an assertion, and the two real assertions in that test are unaffected
VACUITY
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
    "")                  MODE="run" ;;
    --print-declaration) MODE="print" ;;
    *) echo "  FAIL  unknown argument '$1'; refusing." >&2; exit 2 ;;
esac

if ! command -v python3 >/dev/null 2>&1; then
    echo "  FAIL  python3 not found; test vacuity guard refuses." >&2
    exit 2
fi

python3 - "$ROOT" "$MODE" "$DECLARATION" <<'PY'
import ast
import contextlib
import io
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT, MODE, DECLARATION = Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3]
VERIFIER = ROOT / "verifier"


def refuse(reason, *detail):
    print(f"  FAIL  test vacuity: {reason}", file=sys.stderr)
    for line in detail:
        print(f"        {line}", file=sys.stderr)
    print("  This guard did not establish that the declared suites assert anything.",
          file=sys.stderr)
    print("  Exit 2 is not a pass.", file=sys.stderr)
    raise SystemExit(2)


# The six checks, by code. An ACCEPT line may only name one of these.
CHECKS = {
    "V1": "NEVER RUN / BODY NEVER EXECUTED",
    "V2": "NO ASSERTION EXECUTED",
    "V3": "ASSERTION NEVER EXECUTED",
    "V4": "NO ASSERTION IN SOURCE",
    "V5": "SHADOWED DEFINITION",
    "V6": "ASSERTION CANNOT FAIL",
}

# =====================================================================================
#  parse the declaration
# =====================================================================================
modules, accepted = [], {}
for number, line in enumerate(DECLARATION.splitlines(), 1):
    text = line.strip()
    if not text or text.startswith("#"):
        continue
    parts = text.split(None, 2)
    kind = parts[0]
    if kind == "MODULE":
        if len(parts) < 2:
            refuse(f"declaration line {number} is malformed: {text!r}")
        modules.append(parts[1])
        accepted.setdefault(parts[1], {})
    elif kind == "ACCEPT":
        parts = text.split(None, 3)
        if len(parts) < 4:
            refuse(f"declaration line {number} is malformed: {text!r}",
                   "Expected: ACCEPT <module> <V-code> <Class.test_method> <reason>")
        code = parts[2].upper()
        if code not in CHECKS:
            refuse(f"declaration line {number} names check {code!r}, "
                   f"which is not one of {sorted(CHECKS)}.")
        rest = parts[3].split(None, 1)
        reason = rest[1].strip() if len(rest) > 1 else ""
        if not reason:
            # An ACCEPT with no reason is a dismissal wearing a ratchet's clothes.
            refuse(f"declaration line {number} accepts {code} on {rest[0]} with no reason.",
                   "Every carried finding must say what makes it correct.")
        accepted.setdefault(parts[1], {})[(code, rest[0])] = reason
    else:
        refuse(f"declaration line {number} starts with {kind!r}, not MODULE or ACCEPT.")

orphan = sorted(set(accepted) - set(modules))
if orphan:
    refuse(f"declaration ACCEPTs sites in {orphan} but declares no MODULE for them.",
           "That half-written form would silently never be checked.")
if not modules:
    refuse("the declaration names no modules; there is nothing to instrument.")

if MODE == "print":
    for module in modules:
        print(f"  {module + '.py':<38} instrumented  "
              f"+ {len(accepted[module])} carried finding(s)")
    for module in modules:
        for (code, name), reason in sorted(accepted[module].items()):
            print(f"    ACCEPT {code} ({CHECKS[code]}) on {module}.{name}")
            print(f"           {reason}")
    print("test vacuity: the declaration is the block at the top of")
    print("scripts/check-test-vacuity.sh and is the only copy. Run it to enforce it.")
    raise SystemExit(0)


# =====================================================================================
#  AST analysis
# =====================================================================================
COMPOUND = (ast.If, ast.For, ast.While, ast.With, ast.Try,
            ast.AsyncFor, ast.AsyncWith)
FUNCDEF = (ast.FunctionDef, ast.AsyncFunctionDef)

# Methods whose ARGUMENTS are compared, with how many of the leading positional arguments
# are operands rather than the trailing `msg`. Only these are eligible for V6; anything not
# listed is left alone, which is the conservative direction.
LITERAL_CHECKED = {
    "assertTrue": 1, "assertFalse": 1, "assertIsNone": 1, "assertIsNotNone": 1,
    "assertEqual": 2, "assertNotEqual": 2, "assertIs": 2, "assertIsNot": 2,
    "assertIn": 2, "assertNotIn": 2, "assertGreater": 2, "assertGreaterEqual": 2,
    "assertLess": 2, "assertLessEqual": 2, "assertAlmostEqual": 2,
    "assertNotAlmostEqual": 2, "assertRegex": 2, "assertNotRegex": 2,
    "assertListEqual": 2, "assertDictEqual": 2, "assertSetEqual": 2,
    "assertTupleEqual": 2, "assertCountEqual": 2, "assertMultiLineEqual": 2,
}


def is_literal(node):
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return all(is_literal(element) for element in node.elts)
    if isinstance(node, ast.Dict):
        return all(key is not None and is_literal(key) and is_literal(value)
                   for key, value in zip(node.keys, node.values))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        return is_literal(node.operand)
    return False


def span(nodes):
    lo = min(node.lineno for node in nodes)
    hi = max(getattr(node, "end_lineno", None) or node.lineno for node in nodes)
    return lo, hi


def header(stmt):
    """The expressions a compound statement evaluates in its own right. Its BODY is made of
    separate statements and is walked separately, so a `for` whose body never ran is visible
    as dead body statements rather than as a dead `for`."""
    if isinstance(stmt, ast.If):
        return [stmt.test]
    if isinstance(stmt, (ast.For, ast.AsyncFor)):
        return [stmt.iter]
    if isinstance(stmt, ast.While):
        return [stmt.test]
    if isinstance(stmt, (ast.With, ast.AsyncWith)):
        return [item.context_expr for item in stmt.items]
    return []


def calls(node):
    """Every Call in `node`'s subtree, without descending into nested function definitions."""
    stack, found = [node], []
    while stack:
        current = stack.pop()
        if isinstance(current, ast.Call):
            found.append(current)
        for child in ast.iter_child_nodes(current):
            if isinstance(child, FUNCDEF) and child is not node:
                continue
            stack.append(child)
    return found


class ModuleFacts:
    """Everything the AST alone can say about one test module."""

    def __init__(self, path):
        self.path = path
        self.source = path.read_text(encoding="utf-8")
        self.lines = self.source.splitlines()
        self.tree = ast.parse(self.source, filename=str(path))
        self.functions = {}          # qualname -> FunctionDef
        self.shadowed = []           # (qualname, first lineno, second lineno)
        self._collect(self.tree, "")
        self.asserting_methods = self._propagate_delegation()

    def _collect(self, node, prefix):
        seen = {}
        for item in node.body:
            if isinstance(item, ast.ClassDef):
                self._collect(item, prefix + item.name + ".")
            elif isinstance(item, FUNCDEF):
                qual = prefix + item.name
                if item.name in seen:
                    self.shadowed.append((qual, seen[item.name].lineno, item.lineno))
                seen[item.name] = item
                self.functions[qual] = item

    # -- assertion recognition ---------------------------------------------------------
    @staticmethod
    def _assert_name(call):
        if isinstance(call.func, ast.Attribute):
            name = call.func.attr
            if name.startswith("assert") or name in ("fail", "failUnless", "failIf"):
                return name
        return None

    @staticmethod
    def _self_call(call):
        if (isinstance(call.func, ast.Attribute)
                and isinstance(call.func.value, ast.Name)
                and call.func.value.id == "self"):
            return call.func.attr
        return None

    def _direct_asserts(self, fn):
        """Simple names of methods this function ASSERTS through directly."""
        names = set()
        for node in ast.walk(fn):
            if isinstance(node, ast.Assert):
                names.add("<bare assert>")
        for call in calls(fn):
            name = self._assert_name(call)
            if name and not name.startswith("fail"):
                names.add(name)
        return names

    def _propagate_delegation(self):
        """Simple method names in this file that assert, directly or through another
        same-file method. Two passes over a fixed point so a helper calling a helper
        calling an assertion still counts."""
        asserts = set()
        for qual, fn in self.functions.items():
            if self._direct_asserts(fn):
                asserts.add(qual.rsplit(".", 1)[-1])
        for _ in range(8):
            grown = set(asserts)
            for qual, fn in self.functions.items():
                simple = qual.rsplit(".", 1)[-1]
                if simple in grown:
                    continue
                for call in calls(fn):
                    target = self._self_call(call)
                    if target and target in grown:
                        grown.add(simple)
                        break
            if grown == asserts:
                break
            asserts = grown
        return asserts

    def is_assertion_site(self, nodes):
        """True if evaluating `nodes` performs an assertion — directly, or by calling a
        same-file helper that asserts. `self.fail(...)` and bare `raise` are NOT assertions
        for this purpose: a guard rail that does not fire is the healthy case."""
        for node in nodes:
            if isinstance(node, (ast.ClassDef,) + FUNCDEF):
                # A nested `def` only BINDS a name when its line runs; the assertions in its
                # body execute when it is CALLED, which is a separate statement. Counting the
                # def line as an assertion site would make a helper that is defined and never
                # called look like coverage.
                continue
            if isinstance(node, ast.Assert):
                return True
            for call in calls(node):
                name = self._assert_name(call)
                if name and not name.startswith("fail"):
                    return True
                target = self._self_call(call)
                if target and target in self.asserting_methods:
                    return True
        return False

    # -- statement walk ----------------------------------------------------------------
    def units(self, fn):
        """Yield (lo, hi, in_handler, nodes, text) for every executable unit inside `fn`:
        each leaf statement, and each compound statement's own header expressions.
        Docstrings are skipped — a docstring is a statement Python executes, and counting it
        would make a body with a docstring look alive when nothing else ran."""
        out = []

        def walk(body, in_handler):
            for stmt in body:
                if (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)
                        and isinstance(stmt.value.value, str)):
                    continue
                if isinstance(stmt, COMPOUND):
                    head = header(stmt)
                    if head:
                        lo, hi = span(head)
                        out.append((stmt.lineno, hi, in_handler, head))
                    if isinstance(stmt, ast.Try):
                        walk(stmt.body, in_handler)
                        for handler in stmt.handlers:
                            walk(handler.body, True)
                        walk(stmt.orelse, in_handler)
                        walk(stmt.finalbody, in_handler)
                    else:
                        walk(stmt.body, in_handler)
                        walk(getattr(stmt, "orelse", []), in_handler)
                elif isinstance(stmt, FUNCDEF) or isinstance(stmt, ast.ClassDef):
                    lo, hi = stmt.lineno, stmt.lineno
                    out.append((lo, hi, in_handler, [stmt]))
                else:
                    lo, hi = span([stmt])
                    out.append((lo, hi, in_handler, [stmt]))

        walk(fn.body, False)
        return out

    def literal_assertions(self, fn):
        """V6 — assertions whose compared arguments are every one a literal constant."""
        found = []
        for call in calls(fn):
            name = self._assert_name(call)
            if name not in LITERAL_CHECKED:
                continue
            arity = LITERAL_CHECKED[name]
            positional = [a for a in call.args if not isinstance(a, ast.Starred)]
            if len(positional) < arity or len(positional) != len(call.args):
                continue
            if all(is_literal(argument) for argument in positional[:arity]):
                found.append((call.lineno, name))
        return found


# =====================================================================================
#  the instrumented run — one forked child per module, so no module contaminates another
# =====================================================================================
def instrument(module, source):
    """Run `module`'s suite under a line tracer. Returns executed line numbers and the
    outcome of every test, keyed by the qualname of the function that DEFINES it (so a test
    method inherited by three subclasses resolves to one function)."""
    target = str(source)
    executed = set()

    def tracer(frame, event, arg):
        if frame.f_code.co_filename == target:
            if event == "line":
                executed.add(frame.f_lineno)
            return tracer
        return None

    sys.path.insert(0, str(VERIFIER))
    os.chdir(ROOT)
    imported = __import__(module)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(imported)
    if loader.errors:
        return {"refuse": f"{module}.py could not be COLLECTED — the suite is broken.",
                "detail": [line for error in loader.errors
                           for line in str(error).splitlines()[:4]]}

    collected = []

    def flatten(node):
        for item in node:
            if isinstance(item, unittest.TestSuite):
                flatten(item)
            else:
                collected.append(item)

    flatten(suite)
    if not collected:
        return {"refuse": f"{module}.py collected ZERO tests.",
                "detail": ["A guard that instruments an empty suite reports a clean run",
                           "about nothing. That is the dead-probe failure mode itself."]}

    # test id -> defining qualname, resolved through the class the method is DEFINED on.
    defining = {}
    for test in collected:
        method = getattr(type(test), test._testMethodName, None)
        function = getattr(method, "__func__", method)
        code = getattr(function, "__code__", None)
        if code is None or code.co_filename != target:
            continue
        defining[test.id()] = function.__qualname__

    result = unittest.TestResult()
    started = time.time()
    sink = io.StringIO()
    sys.settrace(tracer)
    try:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            suite.run(result)
    finally:
        sys.settrace(None)
    elapsed = time.time() - started

    if not executed:
        return {"refuse": f"{module}.py: the tracer observed ZERO lines in {source.name}.",
                "detail": ["The suite ran but nothing in the file was traced, so every",
                           "'never executed' answer below would be trivially yes.",
                           "The probe is dead; the guard refuses rather than report a pass."]}

    not_passing = {}
    for label, group in (("FAILED", result.failures), ("ERRORED", result.errors)):
        for test, _ in group:
            not_passing.setdefault(test.id(), label)
    for test, _ in result.skipped:
        not_passing.setdefault(test.id(), "SKIPPED")
    for test, _ in getattr(result, "expectedFailures", []):
        not_passing.setdefault(test.id(), "EXPECTED-FAILURE")
    for test in getattr(result, "unexpectedSuccesses", []):
        not_passing.setdefault(test.id(), "UNEXPECTED-SUCCESS")

    # Worst outcome wins: if ANY invocation of a function did not pass, the function is
    # excluded from the execution-based checks. Conservative on purpose — see the header.
    outcome = {}
    for test_id, qual in defining.items():
        state = not_passing.get(test_id)
        if state:
            outcome.setdefault(qual, state)
    ran = sorted({qual for qual in defining.values()})

    return {
        "executed": sorted(executed),
        "ran": ran,
        "excluded": outcome,
        "total": len(collected),
        "attributed": len(defining),
        "elapsed": elapsed,
    }


def instrument_isolated(module, source):
    handle, path = tempfile.mkstemp(prefix="sentinel-vacuity-")
    os.close(handle)
    pid = os.fork()
    if pid == 0:                                       # ---- child ----
        payload = {"refuse": f"{module}: the instrumented child produced nothing."}
        try:
            payload = instrument(module, source)
        except BaseException as error:                                  # noqa: BLE001
            payload = {"refuse": f"{module}: instrumenting raised "
                                 f"{type(error).__name__}", "detail": [str(error)[:400]]}
        finally:
            try:
                with open(path, "w") as fh:
                    json.dump(payload, fh)
            except BaseException:                                       # noqa: BLE001
                pass
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(0)
    os.waitpid(pid, 0)                                 # ---- parent ----
    try:
        with open(path) as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        data = {"refuse": f"{module}: the instrumented child died without reporting.",
                "detail": ["A crashed probe is not a clean suite."]}
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
    return data


# =====================================================================================
#  run and judge
# =====================================================================================
findings = []
summary = []
carried = []
counted = 0


def finding(text, *detail):
    global counted
    counted += 1
    findings.append(text)
    findings.extend(f"    {line}" for line in detail)


for module in modules:
    source = VERIFIER / f"{module}.py"
    if not source.is_file():
        refuse(f"verifier/{module}.py is missing.",
               "The declaration names it; a guard cannot instrument a file that is not",
               "there, and reporting the other modules as clean would answer a question",
               "nobody asked.")

    facts = ModuleFacts(source)
    data = instrument_isolated(module, source)
    if "refuse" in data:
        refuse(data["refuse"], *data.get("detail", []))

    executed = set(data["executed"])
    excluded = data["excluded"]
    ran = set(data["ran"])
    accept_here = dict(accepted[module])
    hit_accepts = set()

    def alive(lo, hi):
        return any(line in executed for line in range(lo, hi + 1))

    tests = {qual: fn for qual, fn in facts.functions.items()
             if qual.rsplit(".", 1)[-1].startswith("test") and "." in qual}

    v1 = v2 = v3 = v4 = v6 = 0
    for qual in sorted(tests):
        fn = tests[qual]
        units = facts.units(fn)
        assertion_units = [(lo, hi, in_handler, nodes) for lo, hi, in_handler, nodes in units
                           if facts.is_assertion_site(nodes)]

        def report(code, text, *detail):
            if (code, qual) in accept_here:
                hit_accepts.add((code, qual))
                return
            finding(f"{module}.py [{code} {CHECKS[code]}] {qual}", text, *detail)

        # --- V4: syntax only, so it holds whether the test ran or not -------------------
        if not assertion_units:
            report("V4",
                   f"line {fn.lineno}: the body contains no assert*, no bare assert, and no",
                   "call to a same-file helper that asserts. A test that cannot fail is a",
                   "name in a pass count, not evidence.")

        # --- V6: syntax only ------------------------------------------------------------
        for lineno, name in facts.literal_assertions(fn):
            report("V6",
                   f"line {lineno}: {name}(...) compares only literal constants.",
                   "Its truth is fixed at parse time; nothing under test can move it.")

        # --- execution-based checks, on PASSING tests only ------------------------------
        if qual not in ran:
            report("V1",
                   f"line {fn.lineno}: unittest collected no test that resolves to this",
                   "definition. It is shadowed, renamed out of discovery, or defined on a",
                   "class nothing instantiates — either way it asserts nothing, ever.")
            continue
        if qual in excluded:
            continue

        body_units = [(lo, hi) for lo, hi, _, _ in units]
        if body_units and not any(alive(lo, hi) for lo, hi in body_units):
            report("V1",
                   f"line {fn.lineno}: the test is reported as PASSING and not one statement",
                   "of its body was traced.")
            continue

        live_assertions = [u for u in assertion_units if alive(u[0], u[1])]
        if assertion_units and not live_assertions:
            report("V2",
                   f"line {fn.lineno}: the test PASSED and none of its "
                   f"{len(assertion_units)} assertion site(s) ran.",
                   "This is the F7 shape: green, and asserting nothing.")
            continue

        dead = [u for u in assertion_units
                if not alive(u[0], u[1]) and not u[2]]
        if dead:
            detail = [f"line {lo}: {facts.lines[lo - 1].strip()[:100]}" for lo, _, _, _ in dead]
            report("V3",
                   f"line {fn.lineno}: the test PASSED, but {len(dead)} assertion(s) sit in a",
                   "block that was never entered — a loop over an empty sequence, or a",
                   "condition never true:",
                   *detail)

    # --- V5: module-level, syntax only --------------------------------------------------
    for qual, first, second in facts.shadowed:
        if ("V5", qual) in accept_here:
            hit_accepts.add(("V5", qual))
            continue
        finding(f"{module}.py [V5 {CHECKS['V5']}] {qual}",
                f"defined at line {first} and again at line {second}.",
                "Python keeps only the last one. The earlier definition never runs and",
                "cannot fail, whatever it contains.")

    stale = sorted(set(accept_here) - hit_accepts)
    for code, name in stale:
        finding(f"{module}.py: carried {code} on {name} NO LONGER HAS A FINDING.",
                f"Reason on record: {accept_here[(code, name)]}",
                "Either the test was repaired — in which case delete the ACCEPT line in the",
                "same edit — or it was deleted, renamed, or turned red, in which case this",
                "guard has stopped watching it. A ratchet that silently stops ratcheting is",
                "the failure mode this whole file is about.")
    for code, name in sorted(hit_accepts):
        carried.append(f"    {code}  {module}.{name}")
        carried.append(f"        {accept_here[(code, name)]}")

    summary.append(
        f"  {module + '.py':<38} {data['attributed']:>3}/{data['total']} tests traced · "
        f"{len(tests):>3} test defs · {len(excluded)} red/skipped and EXCLUDED · "
        f"{data['elapsed']:.0f}s"
    )

print("test vacuity (R-A018-24 — a pass count cannot see a test that asserts nothing):")
for line in summary:
    print(line)
print()
print("  CATCHES  V1 a test never run, or a passing test whose body executed no statement")
print("           V2 a passing test in which NO assertion executed")
print("           V3 a passing test whose assertion sits in a block never entered")
print("           V4 a test whose source contains no assertion at all")
print("           V5 a def shadowed by a later def of the same name in the same class")
print("           V6 an assertion whose compared arguments are all literal constants")
print("  DOES NOT CATCH  an assertion that EXECUTES and is merely weak. `assertIn(")
print("           \"evaluation-time\", stdout)` passed with the flag fully suppressed because")
print("           argparse reprints the module docstring, which mentions it in prose. Only")
print("           scripts/mutate.sh finds that class; reading did not, and neither does this.")
print("           Also not caught: vacuity inside a RED or SKIPPED test (excluded above),")
print("           an assertion computed from the same wrong source on both sides, and")
print("           \"cannot fail\" IN GENERAL, which is undecidable.")
if carried:
    print()
    print("  CARRIED FINDINGS (ratchet — declared in this script, and still present):")
    for line in carried:
        print(line)

if findings:
    print()
    for line in findings:
        print(line)
    print()
    print(f"test vacuity: {counted} finding(s).")
    print("Do not silence one with an ACCEPT line to make a run pass (AGENTS.md): an ACCEPT")
    print("must say what makes the dead site CORRECT, and it is printed on every run.")
    raise SystemExit(1)

print()
print("test vacuity: clean — every passing test in the declared modules executed at least one")
print("assertion, and no assertion sat in a block that was never entered.")
PY
exit $?
