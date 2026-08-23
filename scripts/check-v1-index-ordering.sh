#!/usr/bin/env bash
# Sentinel — V-1 index-path ordering guard.
#
# Residual V-1 (D-062 verification §10; carried, not accepted):
#   `git rev-parse --git-path index` honours GIT_INDEX_FILE. The two production sites
#   that resolve a canonical index path are therefore correct only if they scrub that
#   variable BEFORE asking git for the path.
#
# THIS GUARD OBSERVES BEHAVIOUR, NOT SOURCE TEXT. The failure signal is the guard's
# own output under a hostile exported GIT_INDEX_FILE. A comparison of line order,
# byte offsets, or grep-ordering of the scrub against the resolution is forbidden
# here: it would pass a refactor that kept line order while reopening the hole
# (reading the environment into a local before unset; a subshell that re-exports).
#
# ---------------------------------------------------------------------------
# D-059(7) COVERAGE STATEMENT
# ---------------------------------------------------------------------------
# This guard covers ONLY these enumerated facts:
#
#   CS  scripts/check-secrets.sh invoked as
#         --staged --index-file <hostile-path>
#       with GIT_INDEX_FILE exported to that same hostile path, while
#       credential-shaped content sits in the real staged index, must REFUSE at
#       validation and name the canonical index directory. It must not print
#       `secret guard: clean` and must not scan an index it did not establish.
#
#   HOOK  .githooks/pre-commit invoked by a real `git commit` with GIT_INDEX_FILE
#       exported to a hostile path outside the canonical index directory must
#       block the commit: non-zero exit, HEAD unmoved.
#
# It is NOT general evidence about:
#   - index-handling of any other script or hook
#   - GIT_DIR / GIT_WORK_TREE / GIT_COMMON_DIR
#   - untracked-file hygiene (V-6 / R-C)
#   - staged rename or typechange (R1)
#   - a hook-path commit being *accepted* after the hook's own directory check
#     is reversed — that end-to-end was not constructed. The hook unsets
#     GIT_INDEX_FILE before exec, and check-secrets.sh independently
#     re-validates --index-file against a --git-path that then no longer sees
#     the hostile export. A reversed hook therefore shifts the refusal from the
#     hook's wording to check-secrets.sh's wording; HEAD stays unmoved. That
#     shift is a CONTROL that the hook probe is live, not a REQUIRED
#     commit-accepted outcome.
#
# Invoked by both profiles of scripts/test.sh (the step sits in the shared
# prefix, before any PROFILE-dependent branch). A standalone copy that nothing
# invokes would repeat the defect this work is closing.
#
# Credential-shaped fixtures are assembled at run time (D062 pattern) and never
# written as literals. Captured output is matched, not stored.
# ---------------------------------------------------------------------------
set -uo pipefail

# --- Sentinel repository identity (D-060(2)) ---------------------------------
_sentinel_self="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)" || _sentinel_self=""
if [ -z "$_sentinel_self" ]; then
    echo "  FAIL  cannot resolve this script's own location; refusing." >&2; exit 2
fi
SENTINEL_ROOT="$(cd -- "$_sentinel_self" 2>/dev/null && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR git rev-parse --show-toplevel 2>/dev/null)" || SENTINEL_ROOT=""
if [ -z "$SENTINEL_ROOT" ] || [ ! -e "$SENTINEL_ROOT/scripts/test.sh" ] || [ ! -e "$SENTINEL_ROOT/.githooks/pre-commit" ]; then
    echo "  FAIL  this script is not inside the Sentinel repository; refusing." >&2; exit 2
fi
cd "$SENTINEL_ROOT" || { echo "  FAIL  cannot enter the Sentinel repository root; refusing." >&2; exit 2; }
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX

RED=$'\033[31m'; RST=$'\033[0m'
[ -t 1 ] || { RED=""; RST=""; }

die() { echo "${RED}V-1 index-path ordering: FAIL${RST} (preflight) — $1" >&2; exit 2; }

[ -x "$SENTINEL_ROOT/scripts/check-secrets.sh" ] || die "scripts/check-secrets.sh is not executable"
[ -x "$SENTINEL_ROOT/.githooks/pre-commit" ]     || die ".githooks/pre-commit is not executable"
command -v git >/dev/null 2>&1 || die "git is not on PATH"
command -v python3 >/dev/null 2>&1 || die "python3 is not on PATH"

# The credential fixture, assembled at run time. `signerKey` is a name
# check-secrets.sh rule 3b exists to catch; 64 repeated 'b' is not an
# allowlisted development account. Same pattern as D062-containment-tests.
fake_hex64() {
    local ch="${1:-b}" i=0 out=""
    case "$ch" in [0-9a-fA-F]) : ;; *) echo "fake_hex64: not a hex digit" >&2; return 1 ;; esac
    while [ "$i" -lt 64 ]; do out="${out}${ch}"; i=$((i + 1)); done
    printf '%s' "$out"
}
CRED_HEX="$(fake_hex64 b)"
cred_line() { printf 'export const signerKey = "0x%s";\n' "$CRED_HEX"; }

# Reverse-ordering mutant: move the body-level GIT_* unset to immediately AFTER
# the `git rev-parse --git-path index` assignment. This is the V-1 hole. Applied
# only to a disposable copy.
mutate_reverse_ordering() {
    python3 - "$1" << 'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
lines = p.read_text().splitlines(keepends=True)
unset_idxs = [i for i, l in enumerate(lines)
              if l.strip() == "unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX"]
resolve_idxs = [i for i, l in enumerate(lines)
                if "git rev-parse --git-path index" in l and not l.lstrip().startswith("#")]
if len(unset_idxs) != 1 or len(resolve_idxs) != 1:
    sys.exit("mutate: expected one unset and one --git-path index assignment")
ui, ri = unset_idxs[0], resolve_idxs[0]
if ui >= ri:
    sys.exit("mutate: unset is not before --git-path index (already reversed, or unexpected shape)")
unset_line = lines.pop(ui)
ri -= 1
lines.insert(ri + 1, unset_line)
p.write_text("".join(lines))
PY
}

WORK="$(mktemp -d "${TMPDIR:-/tmp}/sentinel-v1.XXXXXXXX")" || die "mktemp failed"
trap 'rm -rf "$WORK"' EXIT

# P1 — /usr/bin/grep canary. The wrapper on this workstation honours --ignore-files.
printf 'V1-CANARY-STRING\n' > "$WORK/canary"
[ "$(/usr/bin/grep -c 'V1-CANARY-STRING' "$WORK/canary" 2>/dev/null)" = "1" ] \
    || die "/usr/bin/grep did not find a planted canary — no match below can be trusted"

# Isolated git configuration. Never write into the operator's HOME or global config.
V1HOME="$WORK/home"
mkdir -p "$V1HOME/.config"
export HOME="$V1HOME"
export GIT_CONFIG_GLOBAL="$V1HOME/.gitconfig"
export GIT_CONFIG_SYSTEM="$V1HOME/.gitconfig-system"
export XDG_CONFIG_HOME="$V1HOME/.config"
export GIT_TERMINAL_PROMPT=0
unset GIT_INDEX_FILE GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_PREFIX || true
# V-6: pin enumeration-sensitive keys at the call site. COUNT still applies on top of
# GLOBAL/SYSTEM; command-line -c outranks every config source. Not a denylist.
git_pinned() { git -c core.excludesFile= -c core.quotePath=false "$@"; }

# Isolated subject. Clone the committed tree, then overlay the WORKING-TREE bytes of
# the two production files so an uncommitted reversal is what this guard sees —
# the same bytes the rest of this gate run is about to execute.
SUT="$WORK/sut"
git_pinned clone -q --local --no-hardlinks "$SENTINEL_ROOT" "$SUT" >/dev/null 2>&1 \
    || die "clone of the repository under test failed"
cp "$SENTINEL_ROOT/scripts/check-secrets.sh" "$SUT/scripts/check-secrets.sh" \
    || die "cannot overlay working-tree check-secrets.sh"
cp "$SENTINEL_ROOT/.githooks/pre-commit" "$SUT/.githooks/pre-commit" \
    || die "cannot overlay working-tree pre-commit"
chmod +x "$SUT/scripts/check-secrets.sh" "$SUT/.githooks/pre-commit"
git_pinned -C "$SUT" config user.email "v1-guard@example.invalid"
git_pinned -C "$SUT" config user.name  "V1 guard"
git_pinned -C "$SUT" config commit.gpgsign false
git_pinned -C "$SUT" config core.hooksPath .githooks

FIX="v1-guard-fixture.txt"
printf 'v1 guard fixture\n' > "$SUT/$FIX"
git_pinned -C "$SUT" add -- "$FIX" >/dev/null 2>&1 || die "cannot stage the fixture"
git_pinned -C "$SUT" -c core.hooksPath=/dev/null commit -qn -m "v1 guard fixture base" \
    || die "cannot create the fixture base commit"
BASE="$(git_pinned -C "$SUT" rev-parse HEAD)" || die "cannot read fixture base"

ATTACK_DIR="$WORK/attacker"
mkdir -p "$ATTACK_DIR"
ATTACK_INDEX="$ATTACK_DIR/index"

# P2 — the V-1 premise itself: --git-path index honours GIT_INDEX_FILE on this git.
GIT_INDEX_FILE="$ATTACK_INDEX" git_pinned -C "$SUT" read-tree HEAD >/dev/null 2>&1 \
    || die "cannot build an attacker-controlled index"
unset GIT_INDEX_FILE
canon_plain="$(cd "$SUT" && git_pinned rev-parse --git-path index 2>/dev/null)" || canon_plain=""
canon_hostile="$(cd "$SUT" && GIT_INDEX_FILE="$ATTACK_INDEX" git_pinned rev-parse --git-path index 2>/dev/null)" || canon_hostile=""
[ -n "$canon_plain" ] || die "cannot resolve --git-path index with GIT_INDEX_FILE unset"
[ -n "$canon_hostile" ] || die "cannot resolve --git-path index with GIT_INDEX_FILE set"
[ "$canon_plain" != "$canon_hostile" ] \
    || die "this git does not honour GIT_INDEX_FILE in --git-path index; the probe cannot move"
[ "$canon_hostile" = "$ATTACK_INDEX" ] \
    || die "--git-path index with GIT_INDEX_FILE set did not return the hostile path"

req_fail=0
ctl_fail=0
note() { printf '  %s\n' "$1"; }

record() {
    # KIND ID HELD DESC   — HELD is 0 when the asserted behaviour was observed.
    local kind="$1" id="$2" held="$3" desc="$4" status
    if [ "$held" -eq 0 ]; then status="PASS"; else status="FAIL"; fi
    printf '  %-6s %-10s %s  %s\n' "$id" "$kind" "$status" "$desc"
    if [ "$held" -ne 0 ]; then
        if [ "$kind" = "REQUIRED" ]; then req_fail=$((req_fail + 1)); else ctl_fail=$((ctl_fail + 1)); fi
    fi
}

reset_sut() {
    unset GIT_INDEX_FILE GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_PREFIX || true
    rm -f "$SUT/.git/index.lock" 2>/dev/null
    rm -f "$SUT"/.git/next-index-*.lock 2>/dev/null
    git_pinned -C "$SUT" reset -q --hard "$BASE" >/dev/null 2>&1 || die "reset --hard failed"
    git_pinned -C "$SUT" clean -qfd >/dev/null 2>&1
    git_pinned -C "$SUT" config core.hooksPath .githooks
    # Overlay live bytes again: reset restored HEAD copies.
    cp "$SENTINEL_ROOT/scripts/check-secrets.sh" "$SUT/scripts/check-secrets.sh"
    cp "$SENTINEL_ROOT/.githooks/pre-commit" "$SUT/.githooks/pre-commit"
    chmod +x "$SUT/scripts/check-secrets.sh" "$SUT/.githooks/pre-commit"
}

setup_cs() {
    reset_sut
    unset GIT_INDEX_FILE
    rm -f "$ATTACK_INDEX"
    GIT_INDEX_FILE="$ATTACK_INDEX" git_pinned -C "$SUT" read-tree HEAD >/dev/null 2>&1 \
        || die "cannot rebuild attacker index"
    unset GIT_INDEX_FILE
    cred_line >> "$SUT/$FIX"
    git_pinned -C "$SUT" add -- "$FIX" >/dev/null 2>&1 || die "cannot stage the credential-shaped fixture"
    git_pinned -C "$SUT" show ":$FIX" 2>/dev/null | /usr/bin/grep -q "$CRED_HEX" \
        || die "real staged blob does not carry the runtime credential — probe would be vacuous"
    if GIT_INDEX_FILE="$ATTACK_INDEX" git_pinned -C "$SUT" show ":$FIX" 2>/dev/null | /usr/bin/grep -q "$CRED_HEX"; then
        die "attacker index also carries the credential — setup is not discriminating"
    fi
}

run_cs() {
    local tag="$1"
    unset GIT_INDEX_FILE
    (
        cd "$SUT" || exit 2
        export GIT_INDEX_FILE="$ATTACK_INDEX"
        set +e
        ./scripts/check-secrets.sh --staged --index-file "$ATTACK_INDEX" \
            >"$WORK/${tag}.out" 2>"$WORK/${tag}.err"
        echo $? > "$WORK/${tag}.rc"
    )
    unset GIT_INDEX_FILE
}

cs_refused_at_validation() {
    local tag="$1"
    /usr/bin/grep -q "canonical index directory" "$WORK/${tag}.out" "$WORK/${tag}.err"
}

cs_accepted_clean() {
    local tag="$1"
    local rc
    rc="$(cat "$WORK/${tag}.rc")"
    [ "$rc" = "0" ] && /usr/bin/grep -q "secret guard: clean" "$WORK/${tag}.out" "$WORK/${tag}.err"
}

setup_hook() {
    reset_sut
    unset GIT_INDEX_FILE
    cred_line >> "$SUT/$FIX"
    git_pinned -C "$SUT" add -- "$FIX" >/dev/null 2>&1 || die "cannot stage the credential-shaped fixture for the hook"
    printf 'benign attacker-index content\n' > "$SUT/v1-benign.txt"
    rm -f "$ATTACK_INDEX"
    GIT_INDEX_FILE="$ATTACK_INDEX" git_pinned -C "$SUT" read-tree HEAD >/dev/null 2>&1 \
        || die "cannot rebuild attacker index for the hook"
    GIT_INDEX_FILE="$ATTACK_INDEX" git_pinned -C "$SUT" add -- "v1-benign.txt" >/dev/null 2>&1 \
        || die "cannot stage a benign path into the attacker index"
    unset GIT_INDEX_FILE
}

run_hook_commit() {
    local tag="$1"
    unset GIT_INDEX_FILE
    git_pinned -C "$SUT" rev-parse HEAD > "$WORK/${tag}.head_before"
    (
        cd "$SUT" || exit 2
        export GIT_INDEX_FILE="$ATTACK_INDEX"
        set +e
        git_pinned commit -m "v1-guard $tag" >"$WORK/${tag}.out" 2>"$WORK/${tag}.err"
        echo $? > "$WORK/${tag}.rc"
    )
    unset GIT_INDEX_FILE
    git_pinned -C "$SUT" rev-parse HEAD > "$WORK/${tag}.head_after"
}

head_unmoved() {
    local tag="$1"
    cmp -s "$WORK/${tag}.head_before" "$WORK/${tag}.head_after"
}

hook_refused_own_validation() {
    local tag="$1"
    /usr/bin/grep -q "the index git handed this hook is not acceptable" "$WORK/${tag}.out" "$WORK/${tag}.err"
}

secrets_refused_index_file() {
    local tag="$1"
    /usr/bin/grep -q -- "--index-file is not acceptable" "$WORK/${tag}.out" "$WORK/${tag}.err"
}

# --------------------------------------------------------------------------- cases
note "observing working-tree scripts/check-secrets.sh and .githooks/pre-commit"
note "under a hostile GIT_INDEX_FILE pointing outside the canonical index directory"

# REQUIRED CS: live check-secrets.sh refuses.
setup_cs
run_cs live-cs
if cs_refused_at_validation live-cs; then
    record REQUIRED CS-live 0 "live check-secrets.sh refuses --index-file outside the canonical directory"
else
    record REQUIRED CS-live 1 "live check-secrets.sh did not refuse at validation (hole open, or unexpected output)"
fi

# CONTROL CS: the reverse-ordering mutant on a copy MUST open the hole, or this
# instrument is measuring nothing. If the live file is already reversed, the
# mutator cannot apply; the live CS run then IS the probe, and must have opened
# the hole — otherwise we would be scoring a dead instrument as a production miss.
setup_cs
if mutate_reverse_ordering "$SUT/scripts/check-secrets.sh" 2>"$WORK/mutate-cs.err"; then
    run_cs mutant-cs
    if cs_accepted_clean mutant-cs; then
        record CONTROL CS-mutant 0 "reversed check-secrets.sh accepts and prints secret guard: clean (probe is live)"
    else
        record CONTROL CS-mutant 1 "reversed check-secrets.sh did not accept — the probe did not move"
    fi
elif cs_accepted_clean live-cs; then
    record CONTROL CS-mutant 0 "live check-secrets.sh is already reversed; hole observed on CS-live"
else
    record CONTROL CS-mutant 1 "could not apply the CS mutant and live CS still refuses — probe cannot move"
fi

# REQUIRED HOOK: live pre-commit blocks a real commit, HEAD unmoved.
setup_hook
run_hook_commit live-hook
live_hook_held=1
if head_unmoved live-hook && [ "$(cat "$WORK/live-hook.rc")" != "0" ] && hook_refused_own_validation live-hook; then
    live_hook_held=0
fi
record REQUIRED HOOK-live "$live_hook_held" \
    "live pre-commit blocks git commit under hostile GIT_INDEX_FILE; HEAD unmoved; hook names its own validation"

# CONTROL HOOK: reversing the hook's own ordering bypasses the hook's directory
# check (refusal moves to check-secrets.sh) but does not accept the commit.
# That is the constructed depth of the hook hole, not a commit-accepted exploit.
setup_hook
if mutate_reverse_ordering "$SUT/.githooks/pre-commit" 2>"$WORK/mutate-hook.err"; then
    run_hook_commit mutant-hook
    hook_ctl=1
    if head_unmoved mutant-hook \
       && [ "$(cat "$WORK/mutant-hook.rc")" != "0" ] \
       && secrets_refused_index_file mutant-hook \
       && ! hook_refused_own_validation mutant-hook; then
        hook_ctl=0
    fi
    record CONTROL HOOK-mutant "$hook_ctl" \
        "reversed pre-commit no longer emits its own index refusal; check-secrets.sh still refuses; HEAD unmoved"
elif ! hook_refused_own_validation live-hook; then
    record CONTROL HOOK-mutant 0 "live pre-commit is already reversed; hook's own validation was already absent"
else
    record CONTROL HOOK-mutant 1 "could not apply the hook mutant and live hook still emits its own refusal — probe cannot move"
fi

# Restore nothing: the subject lives in $WORK and is deleted on exit.

echo
if [ "$ctl_fail" -ne 0 ]; then
    echo "${RED}V-1 index-path ordering: FAIL${RST} — a CONTROL failed; the instrument is untrustworthy."
    echo "  No REQUIRED verdict beside a failing control may be relied on."
    exit 2
fi
if [ "$req_fail" -ne 0 ]; then
    echo "${RED}V-1 index-path ordering: FAIL${RST} — live files do not hold the enumerated behaviour."
    exit 1
fi
echo "V-1 index-path ordering: ok"
echo "  Covers only CS validation-refusal and HOOK commit-block under a hostile"
echo "  GIT_INDEX_FILE, as enumerated in this file's header. Not general index-handling evidence."
exit 0
