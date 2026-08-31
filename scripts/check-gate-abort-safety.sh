#!/usr/bin/env bash
# Sentinel — gate abort-safety guard (R-A018-25).
#
# WHY. `scripts/test.sh:12` sets `set -euo pipefail`. Two of its failure branches ended in
#
#     diff <fresh> <committed> | head -20
#     fail=1
#
# Reaching either line MEANS the comparison failed, so `diff` exits 1, `pipefail` promotes that
# to the pipeline status, `set -e` aborts the body — and **`fail=1` on the next line never ran.**
# Every stage after it was silently skipped: the §7.3 ablation check and the D-010 verifier stage
# never executed on any run that reached the corpus digest branch. The only reason it surfaced at
# all is the supervisor completion-token check at the very bottom of the file, which refused the
# run for a different reason than the one that actually happened.
#
# **That is this project's own recorded failure mode — a probe that is dead and whose silence
# reads like a pass — sitting on the gate's own failure path**, which is the hardest place to
# notice it, because you only get there when something is already wrong. Nothing in this
# repository would have caught a third instance being added. This file is that check.
#
# =====================================================================================
#  WHAT THIS GUARD CATCHES — the precise list, and nothing wider.
# =====================================================================================
#
#   A1  A command from the DECLARED COMMAND LIST below, appearing as the COMMAND WORD of a
#       simple command, in a file where `set -e` is in effect, whose exit status is not
#       handled. "Not handled" means all of the following are false:
#         - it sits in the condition of `if` / `elif` / `while` / `until`
#         - its AND-OR list is prefixed with `!`
#         - its pipeline is followed by `&&` or `||` (this is what `|| true` does)
#         - it is a non-final segment of a pipeline AND `pipefail` is OFF
#         - it is the operand of a status-masking builtin (`local`, `declare`, `export`, ...)
#       Such a command aborts the script the moment it reports a difference, so every
#       statement after it — the `fail=1`, the diagnostics, the remaining stages — is dead.
#
#   A2  The same, inside a `$( )` command substitution, including one on the right-hand side
#       of a plain assignment. `v="$(printf ... | grep -oE ... | wc -l)"` aborts under
#       `pipefail` when the `grep` matches nothing, even though `wc` succeeds. **This is a
#       real, currently-live site in `scripts/test.sh` — see the CARRIED FINDINGS below.**
#
#   A3  A carried finding (an `ACCEPT` line) that has GONE AWAY is reported as STALE rather
#       than passing quietly, the same shape `check-test-vacuity.sh` and
#       `check-publication-suite-floors.sh` use. A ratchet that silently stops ratcheting is
#       the defect this file is about.
#
#  AND IT PROVES ITS OWN CLASSIFICATION RULES ON EVERY RUN. Before it looks at a real file it
#  builds a set of synthetic subjects — one per shape above, guarded and unguarded — RUNS each
#  of them under this machine's own bash, and observes whether the script actually aborted.
#  **The classifier must agree with the shell on every shape or this guard REFUSES.** If a
#  future bash changes `set -e` semantics, or the lexer regresses and stops seeing command
#  words, the controls fail and you are told, instead of getting a green line over a probe that
#  has quietly stopped being able to find anything. This is the `check-gate-immutability.sh`
#  control pattern: a probe that is no longer dangerous makes every pass after it meaningless.
#
# =====================================================================================
#  WHAT THIS GUARD DOES NOT CATCH. Read this before quoting it as coverage.
# =====================================================================================
#
#   * **A COMMAND OUTSIDE THE DECLARED LIST whose non-zero exit is also routine.** The list is
#     `diff cmp comm grep egrep fgrep` — commands whose non-zero exit is a REPORT, not an
#     error. `git diff --exit-code`, `git diff --quiet`, `pgrep`, `read`, `command -v` and a
#     bare `[ ... ]` have the same property and are NOT checked. Two widenings were measured on
#     2026-08-30 rather than argued, and both were rejected:
#       - adding `[` and `test` took the examined population from 10 sites to 107 and found
#         **zero** additional unguarded sites. A bare `[ ... ]` under `set -e` is also a
#         deliberate assert-or-die idiom, so flagging it would be an argument about style, not
#         a defect report — and under-reporting is the safe direction for such a check.
#       - adding `read`, `command` and `pgrep` took it to 117 sites and produced exactly one
#         extra finding, `scripts/check-secrets.sh`s `read -r ... <<< "..."`, which is NOT a
#         defect: a here-string always supplies a terminated line, and the next line checks the
#         field anyway. It would have imported a false positive into a file this guard may
#         not repair.
#     **Widening is a one-line edit to the DECLARATION.** The rejection is recorded here so the
#     next person does not have to redo the measurement to find out why the list is short.
#
#   * **The command word only.** `git diff --exit-code` is a `git` site, not a `diff` site, and
#     is invisible. So is any wrapper function or alias around a declared command — measured:
#     `check-secrets.sh` calls `_cs_git diff --cached`, correctly NOT counted as a `diff` site
#     because `diff` is an argument there, but a hypothetical `mydiff` wrapper that returns 1
#     routinely would be missed entirely.
#
#   * **A SITE INSIDE A SHELL FUNCTION whose callers all invoke it in a handled context.**
#     errexit is suspended for the whole dynamic extent of an `if` condition, so
#     `check() { diff a b; }` invoked only as `if check; then ..` cannot abort — and this guard
#     would report it anyway. No call-graph analysis is done. **This is a FALSE-POSITIVE class,
#     not a blind spot: it can add noise, it can never hide a site.** Measured 2026-08-30: the
#     one site reported here is at top level, so the class is stated rather than active. The
#     four handled `grep` sites in `check-secrets.sh` ARE inside functions and are correctly
#     silent for a different reason — they carry `|| true`.
#
#   * **WHETHER THE SITE IS ON A FAILURE PATH.** That is a semantic property and it is not
#     decidable; this guard does not attempt it. It reports the abort site wherever it is. That
#     is deliberate and it is not a weakening: R-A018-25s harm — every following statement
#     silently skipped — does not depend on the branch being a failure branch. It only becomes
#     hardest to notice there.
#
#   * **Whether the repair is right.** It checks that the following statements are REACHABLE.
#     It has no opinion on whether `fail=1` is the correct thing to reach, or whether the
#     diagnostic above it is accurate.
#
#   * **`set -e` toggled mid-file.** `set +e` / `set -e` regions are not modelled. A file that
#     enables errexit and then toggles it makes this guard REFUSE (exit 2) rather than analyse
#     a state it did not establish. Measured 2026-08-30: no such file exists here.
#
#   * **Legacy backtick substitutions.** Not parsed. If a backtick region contains a declared
#     command the guard REFUSES rather than reporting a region it did not analyse.
#
#   * **Process substitution `<( )` / `>( )`,** whose failure does NOT abort the parent, is not
#     modelled and would be reported as a site. Measured 2026-08-30: zero occurrences in the
#     analysed files. If one is added, this comment is the place the false positive was
#     predicted.
#
#   * **Files that never enable errexit are not analysed at all** — the abort mechanism does not
#     exist in them, which is why every other `scripts/check-*.sh` runs under `set -uo pipefail`
#     with no `-e`. The skipped list is printed. A non-errexit file SOURCED into an errexit
#     context would be wrongly skipped; nothing here does that today.
#
#   * `trap ... ERR`, `set -E`, `shopt -s inherit_errexit`, and any shell other than bash.
#
# EXIT STATUS. 0 clean · 1 findings · 2 refused / could not check. **Exit 2 is never a pass.**
# The guard refuses rather than reporting a property it did not establish: a control that
# stopped being dangerous, a classifier that disagrees with the shell, a file it could not
# lex, or a real scan that examined ZERO command sites — which would mean the probe is dead,
# the exact thing this file exists to detect.
#
# COST. Measured 2026-08-30 at under two seconds: it runs about twenty three-line synthetic
# scripts and lexes four real ones. It is wired into BOTH profiles for that reason.
#
# Usage:
#   ./scripts/check-gate-abort-safety.sh                      run and enforce
#   ./scripts/check-gate-abort-safety.sh --print-declaration   print the declaration only
set -uo pipefail

# =====================================================================================
#  THE DECLARATION — THE ONE PLACE TO EDIT. Nothing below reads it from anywhere else.
#
#    SCAN <glob>                  files to consider (those with errexit OFF are then skipped)
#    COMMAND <name>               a command whose non-zero exit is a REPORT, not an error
#    ACCEPT <file> <cmd> <source-fragment> :: <reason>       one KNOWN site, ratcheted
#
#  AN `ACCEPT` IS KEYED ON A SOURCE FRAGMENT, NOT A LINE NUMBER. Line numbers in this
#  repository are stale within hours — it is the `v1-1-register.md` rule — and a ratchet
#  pinned to one would silently stop ratcheting on the next edit above it. The fragment must
#  appear in the flagged source line.
#
#  AN `ACCEPT` LINE IS A RATCHET, NOT A DISMISSAL. It is printed on every run, and if the site
#  it names goes away the guard reports the declaration as STALE rather than quietly passing.
#  Never add one to make a run green: say what makes the site correct, or fix the site.
# =====================================================================================
DECLARATION=$(cat <<'ABORTSAFETY'
SCAN scripts/*
SCAN .githooks/*

COMMAND diff
COMMAND cmp
COMMAND comm
COMMAND grep
COMMAND egrep
COMMAND fgrep

# --- carried findings ----------------------------------------------------------------
# NOTE FOR WHOEVER EDITS THIS BLOCK: bash 3.2 (the macOS system bash, which runs this)
# mis-parses an APOSTROPHE inside a heredoc nested in $( ), and an odd number of them makes
# the whole script a syntax error a long way further down. Write around them.
#
# ONE CARRIED SITE, MEASURED 2026-08-30, AND IT IS A THIRD INSTANCE OF R-A018-25 THAT NOBODY
# HAD FOUND. In the D-010 verifier stage of scripts/test.sh:
#
#     v_modes=<command substitution>  printf .. | grep -oE .the mutated [a-z-]+. | sed .. | sort -u | wc -l | tr -d ..
#
# The line directly above it ends in `|| true` on its `grep -c`, so the author knew. This one
# does not have it. `grep -oE` is a NON-FINAL pipeline segment and `pipefail` is on, so if the
# verifier ever stops printing `the mutated <mode>` lines — which is exactly the regression the
# tamper-mode floor below it exists to catch — the assignment fails, `set -e` aborts, and the
# `FLOOR BREACHED .. tamper modes` message that was supposed to report it never prints. Same
# shape, same failure path, same silence.
#
# CARRIED AND NOT FIXED, DELIBERATELY. R-A018-25 records that changing the gate failure
# semantics is not an agent decision and was put to John; the owner then ruled TWO specific
# lines and this third site was not among them. The one-line repair is a `|| true` on the
# substitution, after which `${v_modes:-0}` becomes 0 and the existing tamper-modes floor
# reports the breach properly instead of the run dying. **That is a ruling, not a cleanup.**
ACCEPT scripts/test.sh grep the mutated [a-z-]+ :: third R-A018-25 instance, found by this guard on its first run; grep -oE is a non-final pipefail segment inside the v_modes assignment, so a verifier that stops printing its tamper-mode lines aborts the gate instead of tripping the tamper-modes floor below it. NOT fixed here: R-A018-25 reserves gate failure semantics to John and his ruling named two other lines. Owed to him as a decision.
ABORTSAFETY
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
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX

MODE="run"
case "${1:-}" in
    "")                  MODE="run" ;;
    --print-declaration) printf '%s\n' "$DECLARATION"; exit 0 ;;
    *) echo "  FAIL  unknown argument '$1'; refusing." >&2; exit 2 ;;
esac

if ! command -v python3 >/dev/null 2>&1; then
    echo "  FAIL  python3 not found; the gate abort-safety guard refuses." >&2
    exit 2
fi

# =====================================================================================
#  THE CONTROLS. Built, RUN, and observed before any real file is looked at.
#
#  Each subject is three lines under `set -euo pipefail`: the shape, then a marker echo. If
#  the marker reaches the output the shell did NOT abort. The classifier is then run over the
#  same files and must agree, shape for shape. The pairs are deliberate — every unguarded
#  shape has a guarded twin differing only in the handling — so a classifier that reported
#  everything, or nothing, fails here rather than in six months.
# =====================================================================================
WORK="$(mktemp -d "${TMPDIR:-/tmp}/gate-abort-safety.XXXXXXXX")" || {
    echo "  FAIL  cannot create a working directory; refusing." >&2; exit 2; }
trap 'rm -rf "$WORK"' EXIT
SUBJ="$WORK/subjects"
mkdir -p "$SUBJ" || { echo "  FAIL  cannot create the subject directory; refusing." >&2; exit 2; }
printf 'left\n'  > "$SUBJ/A"
printf 'right\n' > "$SUBJ/B"

MARKER="SENTINEL_ABORT_SAFETY_REACHED_END"
OBS="$WORK/observed.txt"
: > "$OBS"

shape() {
    # shape <name>  <<'X' ...body... X
    _sh_name="$1"
    { echo '#!/usr/bin/env bash'
      echo 'set -euo pipefail'
      cat
      echo "echo $MARKER"
    } > "$SUBJ/$_sh_name.sh"
}

shape unguarded_pipe_to_head <<'X'
diff A B | head -20
X
shape guarded_pipe_to_head <<'X'
diff A B | head -20 || true
X
shape unguarded_bare <<'X'
diff A B >/dev/null
X
shape unguarded_semicolon_true <<'X'
diff A B >/dev/null; true
X
shape unguarded_subshell <<'X'
( diff A B >/dev/null )
X
shape unguarded_grep_statement <<'X'
grep -q nomatchhere A
X
shape unguarded_cmp <<'X'
cmp A B >/dev/null
X
shape unguarded_in_assignment <<'X'
v="$(printf 'zz\n' | grep -oE 'nomatchhere' | sort -u | wc -l | tr -d ' ')"
echo "v=$v"
X
shape unguarded_in_elif_body <<'X'
if false; then :; elif true; then diff A B >/dev/null; fi
X
shape guarded_if_condition <<'X'
if diff -q A B >/dev/null 2>&1; then :; else :; fi
X
shape guarded_while_condition <<'X'
while diff -q A B >/dev/null 2>&1; do break; done
X
shape guarded_negated <<'X'
! diff A B >/dev/null
X
shape guarded_and_list <<'X'
diff A B >/dev/null && echo same
X
shape guarded_in_assignment <<'X'
v="$(printf 'zz\n' | grep -c 'nomatchhere' || true)"
echo "v=$v"
X
shape guarded_local_assignment <<'X'
f() { local v="$(printf 'zz\n' | grep -oE 'nomatchhere' | wc -l)"; echo "v=$v"; }
f
X
shape not_a_command_word <<'X'
printf '%s\n' diff cmp comm grep >/dev/null
X
shape inside_a_comment <<'X'
# diff A B
:
X
shape inside_a_heredoc <<'X'
cat >/dev/null <<'INNER'
diff A B
INNER
X

for _f in "$SUBJ"/*.sh; do
    _n="$(basename "$_f" .sh)"
    _out="$( (cd "$SUBJ" && bash "$_f") 2>&1 )"
    case "$_out" in
        *"$MARKER"*) printf '%s CONTINUED\n' "$_n" >> "$OBS" ;;
        *)           printf '%s ABORTED\n'   "$_n" >> "$OBS" ;;
    esac
done

python3 - "$ROOT" "$MODE" "$DECLARATION" "$SUBJ" "$OBS" <<'PY'
import fnmatch
import os
import re
import sys

ROOT, MODE, DECLARATION, SUBJ, OBS = sys.argv[1:6]

# =====================================================================================
#  THE LEXER. Small on purpose, and it REFUSES on anything it does not model.
# =====================================================================================

OPS = [";;", "&&", "||", "|&", ">>", "<<-", "<<", "<&", ">&", ";", "|", "&", "(", ")", "\n"]
RESET_WORDS = {"if", "elif", "while", "until", "then", "else", "do", "done", "fi",
               "case", "esac", "in", "!", "time", "function", "{", "}"}
MASKING = {"local", "declare", "typeset", "export", "readonly"}


class Refuse(Exception):
    pass


class Tok(object):
    __slots__ = ("kind", "text", "line")

    def __init__(self, kind, text, line):
        self.kind, self.text, self.line = kind, text, line


def grab_sub(src, i, line):
    """src[i:] starts with '$('.  Return (inner, next_index, start_line)."""
    n = len(src)
    depth = 0
    j = i + 1
    while j < n:
        c = src[j]
        if c == "\\":
            j += 2
            continue
        if c == "'":
            k = src.find("'", j + 1)
            if k == -1:
                raise Refuse("unterminated single quote inside $( ) near line %d" % line)
            j = k + 1
            continue
        if c == '"':
            j += 1
            while j < n:
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == '"':
                    j += 1
                    break
                if src.startswith("$(", j):
                    _, j, _ = grab_sub(src, j, line)
                    continue
                j += 1
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return src[i + 2:j], j + 1, line
        j += 1
    raise Refuse("unterminated command substitution near line %d" % line)


def backtick_guard(inner, line, commands):
    for cmd in commands:
        if re.search(r"(^|[\s;|&(])" + re.escape(cmd) + r"\b", inner):
            raise Refuse(
                "line %d: a legacy backtick substitution contains `%s`. This lexer does not "
                "parse backticks and refuses rather than reporting a region it did not "
                "analyse." % (line, cmd))


def lex(src, line0, commands):
    """Return (tokens, subs) where subs is [(inner_src, start_line, token_index)]."""
    toks, subs = [], []
    i, n, line = 0, len(src), line0
    heredocs = []
    while i < n:
        c = src[i]
        if c == "\n":
            toks.append(Tok("op", "\n", line))
            i += 1
            line += 1
            while heredocs:
                delim, strip = heredocs.pop(0)
                while i < n:
                    j = src.find("\n", i)
                    if j == -1:
                        j = n
                    raw = src[i:j]
                    i = j + 1
                    line += 1
                    cand = raw.lstrip("\t") if strip else raw
                    if cand.strip() == delim:
                        break
            continue
        if c in " \t":
            i += 1
            continue
        if c == "\\" and i + 1 < n and src[i + 1] == "\n":
            i += 2
            line += 1
            continue
        if c == "#" and (i == 0 or src[i - 1] in " \t\n;&|()"):
            j = src.find("\n", i)
            i = n if j == -1 else j
            continue
        if src.startswith("<<", i) and not src.startswith("<<<", i):
            strip = src.startswith("<<-", i)
            k = i + (3 if strip else 2)
            while k < n and src[k] in " \t":
                k += 1
            m = re.match(r"""('[^']*'|"[^"]*"|[A-Za-z_][A-Za-z0-9_]*)""", src[k:])
            if m:
                heredocs.append((m.group(1).strip("'\""), strip))
                toks.append(Tok("redir", "<<", line))
                i = k + m.end()
                continue
        op = None
        for cand in OPS:
            if src.startswith(cand, i):
                op = cand
                break
        if op is not None:
            toks.append(Tok("redir" if op in (">>", "<<", "<&", ">&") else "op", op, line))
            i += len(op)
            continue
        if c in "<>":
            toks.append(Tok("redir", c, line))
            i += 1
            continue
        start, startline, buf = i, line, []
        while i < n:
            c = src[i]
            if c == "\\" and i + 1 < n:
                if src[i + 1] == "\n":
                    i += 2
                    line += 1
                    continue
                buf.append(src[i + 1])
                i += 2
                continue
            if c == "'":
                j = src.find("'", i + 1)
                if j == -1:
                    raise Refuse("unterminated single quote near line %d" % line)
                line += src.count("\n", i, j)
                buf.append(src[i:j + 1])
                i = j + 1
                continue
            if c == '"':
                i += 1
                buf.append('"')
                while i < n:
                    if src[i] == "\\" and i + 1 < n:
                        buf.append(src[i:i + 2])
                        if src[i + 1] == "\n":
                            line += 1
                        i += 2
                        continue
                    if src[i] == '"':
                        i += 1
                        buf.append('"')
                        break
                    if src.startswith("$(", i):
                        sl = line
                        inner, ni, _ = grab_sub(src, i, line)
                        line += src.count("\n", i, ni)
                        i = ni
                        subs.append((inner, sl, len(toks)))
                        buf.append("$(..)")
                        continue
                    if src[i] == "`":
                        j = src.find("`", i + 1)
                        if j == -1:
                            raise Refuse("unterminated backtick near line %d" % line)
                        backtick_guard(src[i + 1:j], line, commands)
                        line += src.count("\n", i, j)
                        buf.append("`..`")
                        i = j + 1
                        continue
                    if src[i] == "\n":
                        line += 1
                    buf.append(src[i])
                    i += 1
                continue
            if src.startswith("$(", i):
                sl = line
                inner, ni, _ = grab_sub(src, i, line)
                line += src.count("\n", i, ni)
                i = ni
                subs.append((inner, sl, len(toks)))
                buf.append("$(..)")
                continue
            if c == "`":
                j = src.find("`", i + 1)
                if j == -1:
                    raise Refuse("unterminated backtick near line %d" % line)
                backtick_guard(src[i + 1:j], line, commands)
                line += src.count("\n", i, j)
                buf.append("`..`")
                i = j + 1
                continue
            if c in " \t\n" or c in "<>":
                break
            if any(src.startswith(cand, i) for cand in OPS):
                break
            buf.append(c)
            i += 1
        text = "".join(buf)
        if not text and i == start:
            i += 1
            continue
        toks.append(Tok("word", text, startline))
    return toks, subs


ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\[[^]]*\])?\+?=")


def command_words(toks):
    """Yield (index, tok) for each token that is the command word of a simple command."""
    expect = True
    for idx, t in enumerate(toks):
        if t.kind == "redir":
            continue
        if t.kind == "op":
            expect = True
            continue
        if expect and ASSIGN.match(t.text):
            continue
        if t.text in RESET_WORDS:
            expect = True
            continue
        if expect:
            yield idx, t
            expect = False


def in_condition(toks, idx):
    depth = 0
    for t in toks[:idx]:
        if t.kind != "word":
            continue
        if t.text in ("if", "elif", "while", "until"):
            depth += 1
        elif t.text in ("then", "do"):
            depth = max(0, depth - 1)
    return depth > 0


def negated(toks, idx):
    j = idx - 1
    while j >= 0:
        t = toks[j]
        if t.kind == "redir":
            j -= 1
            continue
        if t.kind == "op":
            if t.text in ("|", "|&", "&&", "||"):
                j -= 1
                continue
            return False
        if t.text == "!":
            return True
        if t.text in RESET_WORDS:
            return False
        j -= 1
    return False


def followed_by_and_or(toks, idx):
    j = idx + 1
    while j < len(toks):
        t = toks[j]
        if t.kind == "op":
            if t.text in ("&&", "||"):
                return True
            if t.text in ("|", "|&"):
                j += 1
                continue
            return False
        j += 1
    return False


def last_in_pipeline(toks, idx):
    j = idx + 1
    while j < len(toks):
        t = toks[j]
        if t.kind == "op":
            return t.text not in ("|", "|&")
        j += 1
    return True


def statement_start(toks, idx):
    """Index of the first token of the simple command containing token idx."""
    j = idx
    while j > 0:
        p = toks[j - 1]
        if p.kind == "op" or (p.kind == "word" and p.text in RESET_WORDS):
            break
        j -= 1
    return j


def masked(toks, idx):
    return toks[statement_start(toks, idx)].text in MASKING


def handled(toks, idx, pipefail, outer):
    if outer:
        return True
    if in_condition(toks, idx) or negated(toks, idx) or followed_by_and_or(toks, idx):
        return True
    if masked(toks, idx):
        return True
    if not pipefail and not last_in_pipeline(toks, idx):
        return True
    return False


def scan(src, pipefail, commands, line0=1, outer=False, sites=None, examined=None):
    sites = [] if sites is None else sites
    examined = [] if examined is None else examined
    toks, subs = lex(src, line0, commands)
    for idx, t in command_words(toks):
        if t.text.split("/")[-1] not in commands:
            continue
        examined.append((t.line, t.text))
        if not handled(toks, idx, pipefail, outer):
            sites.append((t.line, t.text.split("/")[-1]))
    for inner, sl, tokidx in subs:
        if outer or tokidx >= len(toks):
            oh = True if outer else False
        else:
            oh = handled(toks, tokidx, pipefail, False)
        scan(inner, pipefail, commands, sl, oh, sites, examined)
    return sites, examined


def errexit_state(src):
    """(errexit_enabled_anywhere, pipefail_on, first_line, toggle_lines).

    `set +e` lines in a file that never turned errexit on are no-ops and are ignored;
    a file that turns it on and then touches it again is REFUSED by the caller, because
    modelling regions is not something this guard does.
    """
    set_e, clear_e, pf = [], [], False
    for i, raw in enumerate(src.split("\n"), 1):
        m = re.match(r"^\s*set\s+([-+]\S.*)$", raw)
        if not m:
            continue
        rest = m.group(1)
        if re.search(r"(^|\s)-[a-zA-Z]*e", rest) or "-o errexit" in rest:
            set_e.append(i)
        if re.search(r"(^|\s)\+[a-zA-Z]*e", rest) or "+o errexit" in rest:
            clear_e.append(i)
        if "pipefail" in rest and re.search(r"(^|\s)-[a-zA-Z]*o(\s|$)", rest):
            pf = True
    if not set_e:
        return False, pf, None, []
    toggles = sorted(set_e[1:] + clear_e)
    return True, pf, set_e[0], toggles


# =====================================================================================
#  THE DECLARATION, PARSED.
# =====================================================================================
scans, commands, accepts = [], [], []
for raw in DECLARATION.split("\n"):
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    kw, _, rest = line.partition(" ")
    rest = rest.strip()
    if kw == "SCAN":
        scans.append(rest)
    elif kw == "COMMAND":
        commands.append(rest)
    elif kw == "ACCEPT":
        body, _, reason = rest.partition(" :: ")
        parts = body.split(None, 2)
        if len(parts) != 3 or not reason.strip():
            print("  FAIL  malformed ACCEPT line; refusing:\n    %s" % line)
            raise SystemExit(2)
        accepts.append((parts[0], parts[1], parts[2].strip(), reason.strip()))
    else:
        print("  FAIL  unknown declaration keyword %r; refusing." % kw)
        raise SystemExit(2)

commands = set(commands)
if not commands or not scans:
    print("  FAIL  the declaration names no commands or no files; refusing.")
    raise SystemExit(2)

# =====================================================================================
#  PART 1 — THE CONTROLS.  The classifier must agree with the shell, shape for shape.
# =====================================================================================
observed = {}
for raw in open(OBS):
    parts = raw.split()
    if len(parts) == 2:
        observed[parts[0]] = parts[1]

control_bad = []
n_abort = n_cont = 0
for name in sorted(observed):
    path = os.path.join(SUBJ, name + ".sh")
    try:
        src = open(path).read()
    except IOError as exc:
        control_bad.append("%s: could not be read back (%s)" % (name, exc))
        continue
    on, pf, _, _ = errexit_state(src)
    if not on or not pf:
        control_bad.append("%s: the subject did not carry errexit+pipefail; the probe is void"
                           % name)
        continue
    try:
        sites, _ = scan(src, pf, commands)
    except Refuse as exc:
        control_bad.append("%s: the lexer refused its own control subject (%s)" % (name, exc))
        continue
    said = "ABORTED" if sites else "CONTINUED"
    if observed[name] == "ABORTED":
        n_abort += 1
    else:
        n_cont += 1
    if said != observed[name]:
        control_bad.append(
            "%s: this shell %s, the classifier said %s" % (name, observed[name], said))

if n_abort == 0:
    control_bad.append(
        "NOT ONE control subject aborted. `set -e` is not doing what this guard is about, so "
        "every pass below would be meaningless — this is the dead-probe failure mode.")
if n_cont == 0:
    control_bad.append(
        "NOT ONE control subject survived. The guarded shapes are supposed to; a classifier "
        "that flags everything is not evidence.")

if control_bad:
    print("gate abort safety: REFUSED — the controls do not hold.")
    for line in control_bad:
        print("    %s" % line)
    print()
    print("  The classifier is validated against this machine's own bash on every run. A")
    print("  disagreement means the shell's `set -e` semantics, or this lexer, is not what")
    print("  the classification rules assume. Reporting a pass on that would be fiction.")
    raise SystemExit(2)

# =====================================================================================
#  PART 2 — THE REAL SCAN.
# =====================================================================================
candidates = []
for pattern in scans:
    d = os.path.dirname(pattern) or "."
    base = os.path.basename(pattern)
    try:
        names = sorted(os.listdir(os.path.join(ROOT, d)))
    except OSError:
        continue
    for nm in names:
        rel = os.path.join(d, nm) if d != "." else nm
        full = os.path.join(ROOT, rel)
        if not os.path.isfile(full) or not fnmatch.fnmatch(nm, base):
            continue
        if rel not in candidates:
            candidates.append(rel)

analysed, skipped, findings, examined_total = [], [], [], 0
site_rows = []
refusals = []
for rel in candidates:
    full = os.path.join(ROOT, rel)
    try:
        src = open(full, "r").read()
    except (IOError, UnicodeDecodeError):
        continue
    head = src.split("\n", 1)[0]
    if not head.startswith("#!") or ("bash" not in head and "sh" not in head):
        continue
    on, pf, first, toggles = errexit_state(src)
    if not on:
        skipped.append(rel)
        continue
    if toggles:
        refusals.append("%s: errexit is enabled at line %s and `set` touches -e again at %s. "
                        "Mid-file toggling is not modelled and this guard will not analyse a "
                        "state it did not establish." % (rel, first, ", ".join(map(str, toggles))))
        continue
    try:
        sites, examined = scan(src, pf, commands)
    except Refuse as exc:
        refusals.append("%s: %s" % (rel, exc))
        continue
    analysed.append((rel, first, pf, len(examined)))
    examined_total += len(examined)
    lines = src.split("\n")
    for lineno, cmd in sites:
        text = lines[lineno - 1].strip() if 0 < lineno <= len(lines) else ""
        site_rows.append((rel, lineno, cmd, text))

if refusals:
    print("gate abort safety: REFUSED — a declared file could not be analysed.")
    for line in refusals:
        print("    %s" % line)
    raise SystemExit(2)

if not analysed:
    print("gate abort safety: REFUSED — no file with `set -e` in effect was found.")
    print("    The declaration names %s. If errexit really is off everywhere, this guard has"
          % ", ".join(scans))
    print("    nothing to protect and should be removed, not left reporting a green line.")
    raise SystemExit(2)

if examined_total == 0:
    print("gate abort safety: REFUSED — ZERO command sites were examined in %d errexit file(s)."
          % len(analysed))
    print("    The controls passed, so the classifier works; finding nothing at all in real")
    print("    source means the lexer is not seeing these files. A probe that cannot find")
    print("    anything is the failure mode this guard exists to detect.")
    raise SystemExit(2)

# --- match sites against the ratchet -------------------------------------------------
carried, hit = [], set()
unguarded = []
for rel, lineno, cmd, text in site_rows:
    key = None
    for i, (afile, acmd, frag, reason) in enumerate(accepts):
        if afile == rel and acmd == cmd and frag in text:
            key = i
            break
    if key is None:
        unguarded.append((rel, lineno, cmd, text))
    else:
        hit.add(key)
        carried.append((rel, lineno, cmd, accepts[key][3]))

for i, (afile, acmd, frag, reason) in enumerate(accepts):
    if i in hit:
        continue
    findings.append([
        "%s: carried site `%s` matching %r NO LONGER HAS A FINDING." % (afile, acmd, frag),
        "Reason on record: %s" % reason,
        "Either it was repaired — delete the ACCEPT line in the same edit — or the line moved,",
        "was renamed or deleted, in which case this ratchet has stopped watching it. A ratchet",
        "that silently stops ratcheting is the failure mode this whole file is about.",
    ])

for rel, lineno, cmd, text in unguarded:
    findings.append([
        "%s:%d [A1/A2] `%s` runs with its exit status unhandled under `set -e`." % (rel, lineno, cmd),
        "    %s" % text[:160],
        "Reaching this line with a difference to report MEANS a non-zero exit, so the shell",
        "aborts here and every statement after it — the flag, the diagnostic, the remaining",
        "stages — never runs. Handle the status: `|| true` if the following lines must run,",
        "an `if` if the result is the decision. `; true` on the next statement does NOT work",
        "and this guard proves it in its own controls.",
    ])

# =====================================================================================
#  REPORT.
# =====================================================================================
print("gate abort safety (R-A018-25 — an EXPECTED non-zero exit that kills the run before it")
print("can record the failure):")
print("  controls          %d/%d shapes agree with this machine's bash "
      "(%d abort, %d survive)" % (len(observed), len(observed), n_abort, n_cont))
for rel, first, pf, count in analysed:
    print("  %-34s errexit ON at line %-4s pipefail=%-5s %3d command site(s)"
          % (rel, first, "on" if pf else "off", count))
print("  %d file(s) analysed · %d command site(s) examined · %d unguarded · %d carried"
      % (len(analysed), examined_total, len(unguarded), len(carried)))
if skipped:
    print("  NOT ANALYSED (errexit OFF, so the abort cannot happen there): %s"
          % ", ".join(skipped))
print()
print("  CATCHES  A1 a declared command as the COMMAND WORD of a simple command, under")
print("           `set -e`, with its status unhandled — not an if/while condition, not")
print("           negated, not followed by && or ||, not masked by local/export, and not a")
print("           discarded non-final pipeline segment")
print("           A2 the same inside $( ), including the right-hand side of an assignment,")
print("           where pipefail promotes a mid-pipeline failure to the whole substitution")
print("           A3 a carried ACCEPT whose site has gone away, reported as STALE")
print("  DECLARED COMMANDS  %s — commands whose non-zero exit is a REPORT, not an error."
      % " ".join(sorted(commands)))
print("  DOES NOT CATCH  a command OUTSIDE that list with the same property. `git diff")
print("           --exit-code`, `pgrep`, `read`, `command -v` and a bare `[ .. ]` all have it.")
print("           Both widenings were measured and rejected in this file's header, with the")
print("           numbers; widening is a one-line edit to the DECLARATION. Also not caught:")
print("           a wrapper function or alias around a declared command; WHETHER THE SITE IS")
print("           ON A FAILURE PATH, which is not decidable and is not attempted; whether the")
print("           repair is the RIGHT one, as opposed to reachable; `set +e` regions and")
print("           backtick substitutions, both of which make this guard REFUSE instead;")
print("           process substitution, which would be a false positive and does not occur")
print("           here today; and any file that never turns errexit on, listed above.")
print("  KNOWN FALSE POSITIVE  a site inside a function whose callers all invoke it in a")
print("           handled context: errexit is suspended for the dynamic extent of an `if`")
print("           condition and no call-graph analysis is done here. It costs noise, never")
print("           blindness — nothing is hidden by it.")

if carried:
    print()
    print("  CARRIED FINDINGS (ratchet — declared in this script, and still present):")
    for rel, lineno, cmd, reason in carried:
        print("    %s:%d  %s" % (rel, lineno, cmd))
        print("        %s" % reason)

if findings:
    print()
    for block in findings:
        for line in block:
            print("  %s" % line)
        print()
    print("gate abort safety: %d finding(s)." % len(findings))
    print("Do not silence one with an ACCEPT line to make a run pass (AGENTS.md): an ACCEPT")
    print("must say what makes the site CORRECT, and it is printed on every run.")
    raise SystemExit(1)

print()
print("gate abort safety: clean — every declared command under `set -e` has its exit status")
print("handled, and the classifier was re-proved against this shell before saying so.")
PY
exit $?
