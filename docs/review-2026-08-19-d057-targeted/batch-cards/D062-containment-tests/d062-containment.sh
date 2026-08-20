#!/usr/bin/env bash
# D-062 CONTAINMENT — falsification harness for the `GIT_INDEX_FILE` regression.
#
# AUTHORITY: D-062. This file is a TEST. It makes no production repair, modifies no entry
# point, and does not modify either frozen harness — `A1-tests/a1-repo-identity.sh` and
# `A2-tests/a2-env-and-supervisor.sh` stay byte-identical and their sha256 values are asserted
# in case Z below rather than taken on trust.
#
# THE ONE INVARIANT UNDER TEST
#
#   The pre-commit guard scans THE INDEX THAT IS ABOUT TO BECOME THE COMMIT, and refuses
#   rather than reporting a result it did not establish — while an arbitrary caller-supplied
#   `GIT_INDEX_FILE` still redirects nothing.
#
# THE DEFECT THIS OBSERVES. `.githooks/pre-commit` and `scripts/check-secrets.sh` each clear
# `GIT_INDEX_FILE`. Git legitimately hands a pre-commit hook a TEMPORARY index in that variable
# for two ordinary commit forms, measured on git 2.50.1 and re-measured by preflight P6 here:
#
#   git commit            (pre-staged)  ->  .git/index                      relative, harmless
#   git commit -- <path>                ->  <root>/.git/next-index-<pid>.lock   temporary
#   git commit -a                       ->  <root>/.git/index.lock              temporary
#
# In the second and third forms `.git/index` does NOT hold what is being committed. Clearing
# the pointer makes the guard read the wrong index, print `secret guard: clean`, exit 0, and
# land a credential in HEAD.
#
# HOW TO READ THE OUTPUT. Every scored line is one of
#   REQUIRED  — an assertion of the required behaviour. At the pre-repair baseline six of
#               these FAIL. That is the point; a REQUIRED line that cannot fail is worthless.
#   CONTROL   — an assertion that the probe is alive and discriminating: the paired situation
#               that must behave OPPOSITELY, or evidence that the fixture, the temporary index
#               or the invocation shape does anything at all. A failing CONTROL means the
#               harness is measuring nothing and NO conclusion may be drawn beside it.
#   OBSERVED  — a recorded fact. Asserts NOTHING and counts toward neither tally, so a fact
#               worth keeping cannot be misread as a behaviour that passed.
#
# EXIT STATUS — control failure is a DIFFERENT exit path from required-case failure.
#   0  every REQUIRED and every CONTROL held
#   1  REQUIRED failures, all CONTROLs held        (expected at the pre-repair baseline)
#   2  a CONTROL failed, or a preflight failed     (the harness is untrustworthy — fix it first)
#
# EXIT STATUS IS NOT A VALID DISCRIMINATOR ON ITS OWN and this harness never uses it as one.
# Every BLOCK assertion additionally requires the guard's own output to NAME the fixture path,
# and requires the credential to be absent from HEAD afterwards. Every REFUSE assertion
# additionally requires the absence of the `secret guard: clean` line, because a refusal and a
# clean report are the two answers that must never be confused.
#
# ISOLATION. Nothing here writes to the repository under test. Every case operates on a private
# clone under TMPDIR or on repositories this script created, and everything is removed on exit.
# `HOME` and the global / system / XDG git configuration are redirected into the scratch area
# for every scored run and their fingerprint is asserted unchanged at the end. Git configuration
# is never written into a repository this script did not create.
#
# FIXTURES. The planted credential is obviously fake: a single hex character repeated 64 times,
# ASSEMBLED AT RUN TIME rather than written as a literal, so this file carries no
# credential-shaped content into a repository guarded by check-secrets.sh.
#
# METHOD NOTES, recorded so the next author does not re-pay for them:
#   * /usr/bin/grep, never the shell's grep — the wrapper on this workstation honours
#     --ignore-files and can return a clean-looking zero. P1 plants a canary to prove it.
#   * bash 3.2: no mapfile, no associative arrays, and `"${arr[@]}"` on an EMPTY array is an
#     unbound-variable error under `set -u`.
#   * command substitution STRIPS NUL bytes, so nothing here parses NUL-delimited git output.
#   * git EXPORTS its hook environment, so the emulated hook invocation used by cases 8-11 is
#     built from what preflight P6 MEASURED git handing a real hook, not from an assumption.
#     If a future git sets a variable P6 records as unset, P6 fails rather than emulating a
#     fiction.
#   * a temporary index is built the way git builds one — `git read-tree HEAD` into a private
#     index file, then `git add` into it — and case 10/11 controls prove the result genuinely
#     carries the candidate content while the canonical index does not.

set -uo pipefail

# ---------------------------------------------------------------------------- preamble ------
# The commit this harness was authored and demonstrated against. A different SHA is not an
# error; it is recorded and warned about, because the outcomes are evidence about whatever was
# actually measured and nothing else.
DEMONSTRATED_AT="76c466fe95ef4a69a1ce86f271498e076e5343aa"
# The two production files are byte-identical at 28fa955 and at 76c466f — `git diff 28fa955 HEAD
# -- .githooks/pre-commit scripts/check-secrets.sh` is empty — so a result measured at either
# transfers to the other. Case Z re-verifies that rather than restating it.
CONTAINMENT_BASE="28fa955"

FROZEN_A1_SHA="54535b3b139ef9098753393872e39c932e25e0d861cfa14eb04e6f18c591122d"
FROZEN_A2_SHA="dd67d69a13faf43e0578c57f9681e1468ca0b721727e7f14e83c1e5859fc84a7"

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${1:-$(cd "$SELF_DIR/../../../.." && pwd)}"

req_fail=0
ctl_fail=0
MATRIX_TSV=""

hdr() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }
say() { printf '        %s\n' "$*"; }

check() {   # KIND CASE HELD DESC   — HELD is 0 when the asserted behaviour was observed.
    local kind="$1" case_id="$2" held="$3" desc="$4" status
    if [ "$kind" = "OBSERVED" ]; then status="...."
    elif [ "$held" -eq 0 ]; then status="PASS"; else status="FAIL"; fi
    printf '  case %-6s %-8s %s  %s\n' "$case_id" "$kind" "$status" "$desc"
    MATRIX_TSV="${MATRIX_TSV}${case_id}	${kind}	${status}	${desc}
"
    if [ "$held" -ne 0 ] && [ "$kind" != "OBSERVED" ]; then
        if [ "$kind" = "REQUIRED" ]; then req_fail=$((req_fail + 1)); else ctl_fail=$((ctl_fail + 1)); fi
    fi
}

die() { printf '\n  PREFLIGHT FAILED: %s\n' "$1"; exit 2; }

# The credential fixture, assembled at run time. `signerKey` is a name check-secrets.sh rule 3b
# exists to catch; 64 repeated 'b' is not one of the allowlisted development accounts.
fake_hex64() {
    local ch="${1:-b}" i=0 out=""
    case "$ch" in [0-9a-fA-F]) : ;; *) echo "fake_hex64: '$ch' is not a hex digit" >&2; return 1 ;; esac
    while [ "$i" -lt 64 ]; do out="${out}${ch}"; i=$((i + 1)); done
    printf '%s' "$out"
}
CRED_HEX="$(fake_hex64 b)"
cred_line() { printf 'export const signerKey = "0x%s";\n' "$CRED_HEX"; }

# ---------------------------------------------------------------------------- preflight ------
hdr "preflight — refuse to run a harness that cannot fail"

[ -d "$ROOT/.git" ] || [ -f "$ROOT/.git" ] || die "no repository at the given root: $ROOT"
[ -x "$ROOT/scripts/check-secrets.sh" ] || die "root has no executable scripts/check-secrets.sh"
[ -x "$ROOT/.githooks/pre-commit" ]     || die "root has no executable .githooks/pre-commit"

command -v git >/dev/null 2>&1 || die "git not on PATH"
GIT_VERSION="$(git --version 2>/dev/null)" || die "cannot read the git version"
BASH_VERSION_LINE="$(bash --version 2>/dev/null | head -1)"
ROOT_SHA="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null)" || die "cannot read HEAD at the root"
say "git       : $GIT_VERSION"
say "bash      : $BASH_VERSION_LINE"
say "root      : repository under test is at $ROOT_SHA"
if [ "$ROOT_SHA" != "$DEMONSTRATED_AT" ]; then
    say "WARNING: that is NOT the commit this harness was demonstrated on ($DEMONSTRATED_AT)."
    say "         Outcomes below are evidence about $ROOT_SHA and nothing else."
fi

WORK="$(mktemp -d "${TMPDIR:-/tmp}/d062-containment.XXXXXXXX")" || die "mktemp failed"
trap 'rm -rf "$WORK"' EXIT

# P1 — the /usr/bin/grep canary. Every zero count below is load-bearing.
printf 'D062-CANARY-STRING\n' > "$WORK/canary"
[ "$(/usr/bin/grep -c 'D062-CANARY-STRING' "$WORK/canary" 2>/dev/null)" = "1" ] \
    || die "/usr/bin/grep did not find a planted canary — no zero result below can be trusted"
say "P1 /usr/bin/grep canary found"

# P2 — the redirected environment, established BEFORE any repository is created.
D062HOME="$WORK/home"; mkdir -p "$D062HOME/.config"
BASEENV=(HOME="$D062HOME"
         GIT_CONFIG_GLOBAL="$D062HOME/.gitconfig"
         GIT_CONFIG_SYSTEM="$D062HOME/.gitconfig-system"
         XDG_CONFIG_HOME="$D062HOME/.config"
         GIT_TERMINAL_PROMPT=0)
export HOME="$D062HOME" GIT_CONFIG_GLOBAL="$D062HOME/.gitconfig" \
       GIT_CONFIG_SYSTEM="$D062HOME/.gitconfig-system" XDG_CONFIG_HOME="$D062HOME/.config" \
       GIT_TERMINAL_PROMPT=0
opcfg_fp() {
    { cat "$D062HOME/.gitconfig"        2>/dev/null || echo ABSENT-global
      cat "$D062HOME/.gitconfig-system" 2>/dev/null || echo ABSENT-system
      find "$D062HOME/.config" -type f -exec cat {} + 2>/dev/null || echo ABSENT-xdg
      git -C "$ROOT" config --local --list 2>/dev/null || echo NO-LOCAL
    } | shasum -a 256 | cut -d' ' -f1
}
OPCFG_BEFORE="$(opcfg_fp)"
say "P2 HOME and the global/system/XDG git configuration redirected into the scratch area"

# P3 — the isolated subject. Every case runs against this clone, never the real tree.
SUT="$WORK/sut"
git clone -q --no-hardlinks "$ROOT" "$SUT" >/dev/null 2>&1 || die "clone of the repository under test failed"
git -C "$SUT" fetch -q "$ROOT" HEAD >/dev/null 2>&1 || die "fetch of HEAD into the clone failed"
git -C "$SUT" checkout -q --detach FETCH_HEAD >/dev/null 2>&1 || die "checkout of HEAD in the clone failed"
git -C "$SUT" config user.email "d062-harness@example.invalid"
git -C "$SUT" config user.name  "D062 harness"
git -C "$SUT" config commit.gpgsign false
[ "$(git -C "$SUT" rev-parse HEAD)" = "$ROOT_SHA" ] || die "the clone is not at $ROOT_SHA"
SUT_ROOT="$(cd "$SUT" && pwd -P)"
say "P3 isolated clone of the subject at $ROOT_SHA"

# P4 — the fixture base commit. A tracked file the cases modify, created here rather than
#      borrowed from the product tree, so no case depends on the content of a real document.
FIX="d062-fixture.txt"
printf 'a fixture file created by the D-062 containment harness\n' > "$SUT/$FIX"
git -C "$SUT" add "$FIX" >/dev/null 2>&1 || die "cannot stage the fixture"
git -C "$SUT" -c core.hooksPath=/dev/null commit -qn -m "d062 fixture base" >/dev/null 2>&1 \
    || die "cannot create the fixture base commit"
BASE="$(git -C "$SUT" rev-parse HEAD)"
git -C "$SUT" config core.hooksPath .githooks
say "P4 fixture base commit $BASE carrying $FIX"

reset_sut() {
    rm -f "$SUT/.git/index.lock" 2>/dev/null
    rm -f "$SUT"/.git/next-index-*.lock 2>/dev/null
    git -C "$SUT" reset -q --hard "$BASE" >/dev/null 2>&1
    git -C "$SUT" clean -qfd >/dev/null 2>&1
    git -C "$SUT" config core.hooksPath .githooks
}
plant()   { cred_line >> "$SUT/$FIX"; }
innocue() { printf 'an edit that carries nothing credential-shaped\n' >> "$SUT/$FIX"; }
head_has_cred() {   # 0 when the credential is in HEAD's copy of the fixture
    git -C "$SUT" show "HEAD:$FIX" 2>/dev/null | /usr/bin/grep -q "$CRED_HEX"
}
names_fixture() { printf '%s' "$1" | /usr/bin/grep -q "$FIX"; }
says_clean()    { printf '%s' "$1" | /usr/bin/grep -q 'secret guard: clean'; }

# P5 — the planted credential must actually trip the guard in BOTH modes, or every clean result
#      below is vacuous for a reason that has nothing to do with the defect under test.
reset_sut; plant; git -C "$SUT" add "$FIX" >/dev/null 2>&1
( cd "$SUT" && ./scripts/check-secrets.sh          >/dev/null 2>&1 ); p5d=$?
( cd "$SUT" && ./scripts/check-secrets.sh --staged >/dev/null 2>&1 ); p5s=$?
reset_sut
[ "$p5d" -ne 0 ] || die "the planted credential does NOT trip check-secrets.sh in default mode"
[ "$p5s" -ne 0 ] || die "the planted credential does NOT trip check-secrets.sh in --staged mode"
say "P5 the planted credential trips check-secrets.sh in both modes (default=$p5d staged=$p5s)"

# P6 — WHAT GIT ACTUALLY HANDS A HOOK, measured rather than assumed. A probe hook records its
#      environment and the two index views, then exits 1 so nothing lands. Cases 8-11 emulate a
#      hook invocation, and this is what that emulation is built from: if a future git sets a
#      variable recorded here as unset, this preflight fails rather than emulating a fiction.
PROBE="$WORK/probehooks"; mkdir -p "$PROBE"
PROBE_LOG="$WORK/probe.log"
cat > "$PROBE/pre-commit" <<'PRB'
#!/usr/bin/env bash
{
  printf 'FORM=%s\n' "${D062_FORM:-?}"
  printf 'GIT_INDEX_FILE=%s\n' "${GIT_INDEX_FILE-<unset>}"
  printf 'GIT_DIR=%s\n'        "${GIT_DIR-<unset>}"
  printf 'GIT_WORK_TREE=%s\n'  "${GIT_WORK_TREE-<unset>}"
  printf 'GIT_COMMON_DIR=%s\n' "${GIT_COMMON_DIR-<unset>}"
  printf 'GIT_PREFIX=%s\n'     "${GIT_PREFIX-<unset>}"
  printf 'PWD=%s\n'            "$PWD"
  printf 'HANDED_SET=%s\n'     "$(git diff --cached --name-only | tr '\n' ' ')"
  printf 'CANON_SET=%s\n'      "$(env -u GIT_INDEX_FILE git diff --cached --name-only | tr '\n' ' ')"
  printf 'HANDED_BLOB_HAS_CRED=%s\n' "$(git show ":${D062_FIX:-nonesuch}" 2>/dev/null | /usr/bin/grep -c "${D062_CRED:-nonesuch}")"
  printf 'END\n'
} >> "$D062_PROBE_LOG"
exit 1
PRB
chmod +x "$PROBE/pre-commit"

probe_form() {   # $1 label, rest: the git command line, run at the subject root
    local label="$1"; shift
    : > "$PROBE_LOG"
    git -C "$SUT" config core.hooksPath "$PROBE"
    ( cd "$SUT" && env D062_FORM="$label" D062_PROBE_LOG="$PROBE_LOG" D062_FIX="$FIX" \
        D062_CRED="$CRED_HEX" "$@" >/dev/null 2>&1 )
    git -C "$SUT" config core.hooksPath .githooks
}
probe_get() { /usr/bin/grep "^$1=" "$PROBE_LOG" | head -1 | sed "s/^$1=//"; }

reset_sut; plant
probe_form "commit-a" git commit -am "probe -a"
P6_A_IDX="$(probe_get GIT_INDEX_FILE)"; P6_A_HANDED="$(probe_get HANDED_SET)"
P6_A_CANON="$(probe_get CANON_SET)";    P6_A_CRED="$(probe_get HANDED_BLOB_HAS_CRED)"
P6_A_GITDIR="$(probe_get GIT_DIR)"; P6_A_WT="$(probe_get GIT_WORK_TREE)"
P6_A_COMMON="$(probe_get GIT_COMMON_DIR)"; P6_A_PREFIX="$(probe_get GIT_PREFIX)"
P6_A_PWD="$(probe_get PWD)"

reset_sut; plant
probe_form "commit-path" git commit -m "probe -- path" -- "$FIX"
P6_P_IDX="$(probe_get GIT_INDEX_FILE)"; P6_P_HANDED="$(probe_get HANDED_SET)"
P6_P_CANON="$(probe_get CANON_SET)";    P6_P_CRED="$(probe_get HANDED_BLOB_HAS_CRED)"

reset_sut; plant; git -C "$SUT" add "$FIX" >/dev/null 2>&1
probe_form "commit-prestaged" git commit -m "probe pre-staged"
P6_S_IDX="$(probe_get GIT_INDEX_FILE)"
reset_sut

[ -n "$P6_A_IDX" ] || die "the probe hook never ran for 'git commit -a' — the mechanism preflight is dead"
say "P6 git commit -a        -> GIT_INDEX_FILE=$P6_A_IDX"
say "P6 git commit -- <path> -> GIT_INDEX_FILE=$P6_P_IDX"
say "P6 git commit           -> GIT_INDEX_FILE=$P6_S_IDX"
say "P6 hook environment: GIT_DIR=$P6_A_GITDIR GIT_WORK_TREE=$P6_A_WT GIT_COMMON_DIR=$P6_A_COMMON GIT_PREFIX=[$P6_A_PREFIX] PWD=$P6_A_PWD"
case "$P6_A_GITDIR$P6_A_WT$P6_A_COMMON" in
    "<unset><unset><unset>") : ;;
    *) die "this git sets GIT_DIR/GIT_WORK_TREE/GIT_COMMON_DIR for hooks; the cases 8-11 emulation would be a fiction" ;;
esac
# Compared after resolution: TMPDIR is commonly a symlinked path, so the literal strings differ
# while the directories are the same one.
P6_A_PWD_R="$(cd "$P6_A_PWD" 2>/dev/null && pwd -P)"
[ "$P6_A_PWD_R" = "$SUT_ROOT" ] || die "git did not run the hook at the worktree root; the emulation would be a fiction"
say "P6 the emulated hook environment matches what git was measured to hand a real hook"

# P7 — the victim repository, created here. The harness never points a variable at a repository
#      it did not make. Its single blob is written into the SUBJECT's object store so the victim
#      index is fully READABLE from the subject: otherwise case 8 would fail-closed on an
#      unreadable object and pass for a reason that has nothing to do with path validation.
VIC="$WORK/victim"
git -c init.defaultBranch=main init -q "$VIC" >/dev/null 2>&1 || die "cannot create the victim repository"
git -C "$VIC" config user.email "d062-harness@example.invalid"
git -C "$VIC" config user.name  "D062 harness"
git -C "$VIC" config commit.gpgsign false
printf 'a victim repository created by the D-062 containment harness\n' > "$VIC/VICTIM-ONLY.md"
git -C "$VIC" add -A >/dev/null 2>&1; git -C "$VIC" commit -qm "victim base" >/dev/null 2>&1
( cd "$SUT" && git hash-object -w "$VIC/VICTIM-ONLY.md" >/dev/null ) || die "cannot make the victim index readable from the subject"
vic_fp() {
    { git -C "$VIC" rev-parse HEAD 2>/dev/null || echo NO-HEAD
      cat "$VIC/.git/config" 2>/dev/null || echo NO-CONFIG
      git -C "$VIC" ls-files -s 2>/dev/null || echo NO-INDEX
      git -C "$VIC" status --porcelain 2>/dev/null || echo NO-STATUS
      find "$VIC" -type f -not -path '*/.git/*' -exec shasum -a 256 {} + 2>/dev/null | sort
    } | shasum -a 256 | cut -d' ' -f1
}
VIC_BEFORE="$(vic_fp)"
VIC_COMMITS_BEFORE="$(git -C "$VIC" rev-list --count HEAD 2>/dev/null)"
say "P7 victim repository created; fingerprint $VIC_BEFORE ($VIC_COMMITS_BEFORE commit)"

# P8 — the emulated hook invocation, and proof that it is faithful in BOTH directions. Cases
#      8-11 cannot be driven by a real `git commit`, because git chooses `GIT_INDEX_FILE` and
#      the whole point is to choose it. So the hook is invoked directly with exactly the
#      environment P6 measured. L1 and L2 below prove the emulation is neither inert nor
#      inherently broken; without them a refusal in case 8 could be an artifact of the harness.
hookrun() {   # $1 = the value handed as GIT_INDEX_FILE
    ( cd "$SUT" && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_COMMON_DIR \
        "${BASEENV[@]}" GIT_PREFIX="" GIT_INDEX_FILE="$1" ./.githooks/pre-commit 2>&1 )
}

hdr "results"

# ============================================================================ case 1 =========
# `git commit -am` with a planted credential must be BLOCKED.
reset_sut; plant
C1_PROBE_OK=1
probe_form "case1" git commit -am "case 1"
[ "$(probe_get HANDED_SET)" = "$FIX " ] && [ "$(probe_get CANON_SET)" = "" ] \
    && [ "$(probe_get HANDED_BLOB_HAS_CRED)" = "1" ] && C1_PROBE_OK=0
check CONTROL 1-tmp "$C1_PROBE_OK" \
    "the temporary index git hands the hook for -a CARRIES the candidate credential, and the canonical index does not"
reset_sut; plant
C1_OUT="$( cd "$SUT" && git commit -am "case 1" 2>&1 )"; C1_RC=$?
C1_HELD=1
if [ "$C1_RC" -ne 0 ] && names_fixture "$C1_OUT" && ! says_clean "$C1_OUT" && ! head_has_cred; then C1_HELD=0; fi
check REQUIRED 1 "$C1_HELD" \
    "git commit -am with a planted credential is BLOCKED, the guard NAMES $FIX, and nothing lands in HEAD"
check OBSERVED 1 0 "exit=$C1_RC  first line: $(printf '%s' "$C1_OUT" | head -1)"
reset_sut

# ============================================================================ case 2 =========
# `git commit -- <path>` with a planted credential must be BLOCKED.
reset_sut; plant
C2_PROBE_OK=1
probe_form "case2" git commit -m "case 2" -- "$FIX"
[ "$(probe_get HANDED_SET)" = "$FIX " ] && [ "$(probe_get CANON_SET)" = "" ] \
    && [ "$(probe_get HANDED_BLOB_HAS_CRED)" = "1" ] && C2_PROBE_OK=0
check CONTROL 2-tmp "$C2_PROBE_OK" \
    "the temporary index git hands the hook for -- <path> CARRIES the candidate credential, and the canonical index does not"
reset_sut; plant
C2_OUT="$( cd "$SUT" && git commit -m "case 2" -- "$FIX" 2>&1 )"; C2_RC=$?
C2_HELD=1
if [ "$C2_RC" -ne 0 ] && names_fixture "$C2_OUT" && ! says_clean "$C2_OUT" && ! head_has_cred; then C2_HELD=0; fi
check REQUIRED 2 "$C2_HELD" \
    "git commit -m ... -- <path> with a planted credential is BLOCKED, the guard NAMES $FIX, and nothing lands in HEAD"
check OBSERVED 2 0 "exit=$C2_RC  first line: $(printf '%s' "$C2_OUT" | head -1)"
reset_sut

# ============================================================================ case 3 =========
# Ordinary `git add` then commit must REMAIN blocked. This is the positive control that proves
# the planted credential is detectable at all through the hook path.
reset_sut; plant; git -C "$SUT" add "$FIX" >/dev/null 2>&1
C3_OUT="$( cd "$SUT" && git commit -m "case 3" 2>&1 )"; C3_RC=$?
C3_HELD=1
if [ "$C3_RC" -ne 0 ] && names_fixture "$C3_OUT" && ! says_clean "$C3_OUT" && ! head_has_cred; then C3_HELD=0; fi
check REQUIRED 3 "$C3_HELD" \
    "git add + git commit with a planted credential REMAINS blocked, named, and out of HEAD"
check OBSERVED 3 0 "exit=$C3_RC  first line: $(printf '%s' "$C3_OUT" | head -1)"
reset_sut

# ============================================================================ case 4 =========
# A clean `git commit -am` must remain ALLOWED. Its opposite control is case 1: a repair that
# refuses every -a commit fails here, a repair that accepts every -a commit fails there.
reset_sut; innocue
C4_OUT="$( cd "$SUT" && git commit -am "case 4" 2>&1 )"; C4_RC=$?
C4_NEW="$(git -C "$SUT" rev-parse HEAD)"
C4_HELD=1
if [ "$C4_RC" -eq 0 ] && says_clean "$C4_OUT" && [ "$C4_NEW" != "$BASE" ] \
   && git -C "$SUT" show "HEAD:$FIX" 2>/dev/null | /usr/bin/grep -q 'carries nothing credential-shaped'; then C4_HELD=0; fi
check REQUIRED 4 "$C4_HELD" \
    "a clean git commit -am is ALLOWED, reports clean, and the intended content reaches HEAD"
check OBSERVED 4 0 "exit=$C4_RC  HEAD advanced to $(printf '%s' "$C4_NEW" | cut -c1-7)"
reset_sut

# ============================================================================ case 5 =========
# A clean path-limited commit must remain ALLOWED. Opposite control: case 2.
reset_sut; innocue
C5_OUT="$( cd "$SUT" && git commit -m "case 5" -- "$FIX" 2>&1 )"; C5_RC=$?
C5_NEW="$(git -C "$SUT" rev-parse HEAD)"
C5_HELD=1
if [ "$C5_RC" -eq 0 ] && says_clean "$C5_OUT" && [ "$C5_NEW" != "$BASE" ] \
   && git -C "$SUT" show "HEAD:$FIX" 2>/dev/null | /usr/bin/grep -q 'carries nothing credential-shaped'; then C5_HELD=0; fi
check REQUIRED 5 "$C5_HELD" \
    "a clean path-limited commit is ALLOWED, reports clean, and the intended content reaches HEAD"
check OBSERVED 5 0 "exit=$C5_RC  HEAD advanced to $(printf '%s' "$C5_NEW" | cut -c1-7)"
reset_sut

# ============================================================================ case 6 =========
# A genuine staged deletion must remain ALLOWED and must never become a false failure
# (D-059(3), D-061(1)). Both arrival routes are exercised: pre-staged, and through the
# temporary index. CONTROL 6c is the opposite: a deletion in the same commit as a credential
# must NOT be waved through because a deletion is present.
reset_sut
git -C "$SUT" rm -q "$FIX" >/dev/null 2>&1
C6A_OUT="$( cd "$SUT" && git commit -m "case 6a" 2>&1 )"; C6A_RC=$?
C6A_HELD=1
if [ "$C6A_RC" -eq 0 ] && says_clean "$C6A_OUT" && ! git -C "$SUT" cat-file -e "HEAD:$FIX" 2>/dev/null; then C6A_HELD=0; fi
check REQUIRED 6a "$C6A_HELD" "a PRE-STAGED genuine deletion is ALLOWED and is not a false failure"
reset_sut
rm -f "$SUT/$FIX"
C6B_OUT="$( cd "$SUT" && git commit -am "case 6b" 2>&1 )"; C6B_RC=$?
C6B_HELD=1
if [ "$C6B_RC" -eq 0 ] && says_clean "$C6B_OUT" && ! git -C "$SUT" cat-file -e "HEAD:$FIX" 2>/dev/null; then C6B_HELD=0; fi
check REQUIRED 6b "$C6B_HELD" "a deletion arriving through the TEMPORARY index (git commit -am) is ALLOWED"
reset_sut
OTHER="d062-second.txt"
printf 'a second fixture file\n' > "$SUT/$OTHER"
git -C "$SUT" add "$OTHER" >/dev/null 2>&1
git -C "$SUT" -c core.hooksPath=/dev/null commit -qn -m "second fixture" >/dev/null 2>&1
BASE2="$(git -C "$SUT" rev-parse HEAD)"
git -C "$SUT" rm -q "$OTHER" >/dev/null 2>&1
plant; git -C "$SUT" add "$FIX" >/dev/null 2>&1
C6C_OUT="$( cd "$SUT" && git commit -m "case 6c" 2>&1 )"; C6C_RC=$?
C6C_HELD=1
if [ "$C6C_RC" -ne 0 ] && names_fixture "$C6C_OUT" && ! says_clean "$C6C_OUT"; then C6C_HELD=0; fi
check CONTROL 6c "$C6C_HELD" \
    "a deletion staged ALONGSIDE a credential is still BLOCKED — the deletion path does not blanket-accept"
git -C "$SUT" reset -q --hard "$BASE" >/dev/null 2>&1; git -C "$SUT" clean -qfd >/dev/null 2>&1
reset_sut

# ============================================================================ case 7 =========
# 12-F2 ANTI-REGRESSION. A caller-supplied GIT_INDEX_FILE pointing at a CLEAN decoy index must
# not stop `check-secrets.sh --staged` scanning Sentinel's canonical index. The decoy is built
# inside the subject's own object store so that honouring it would read CLEAN rather than
# fail-closed on an unreadable object — otherwise the case would pass for the wrong reason.
reset_sut
DECOY="$WORK/decoy.idx"; rm -f "$DECOY"
( cd "$SUT" && GIT_INDEX_FILE="$DECOY" git read-tree HEAD ) || die "cannot build the clean decoy index"
plant; git -C "$SUT" add "$FIX" >/dev/null 2>&1
D_SET="$( cd "$SUT" && GIT_INDEX_FILE="$DECOY" git diff --cached --name-only 2>&1 | tr '\n' ' ' )"
N_SET="$( cd "$SUT" && git diff --cached --name-only 2>&1 | tr '\n' ' ' )"
C7_POTENT=1
[ "$D_SET" = "" ] && [ "$N_SET" = "$FIX " ] && C7_POTENT=0
check CONTROL 7-decoy "$C7_POTENT" \
    "the decoy index is POTENT and CLEAN — honouring it yields an empty staged set while the canonical set holds $FIX"
C7_OUT="$( cd "$SUT" && env "${BASEENV[@]}" GIT_INDEX_FILE="$DECOY" ./scripts/check-secrets.sh --staged 2>&1 )"; C7_RC=$?
C7_HELD=1
if [ "$C7_RC" -ne 0 ] && names_fixture "$C7_OUT" && ! says_clean "$C7_OUT"; then C7_HELD=0; fi
check REQUIRED 7 "$C7_HELD" \
    "check-secrets.sh --staged with a malicious caller GIT_INDEX_FILE still scans the CANONICAL index and names $FIX"
C7B_OUT="$( cd "$SUT" && env "${BASEENV[@]}" ./scripts/check-secrets.sh --staged 2>&1 )"; C7B_RC=$?
C7B_HELD=1
[ "$C7B_RC" -ne 0 ] && names_fixture "$C7B_OUT" && C7B_HELD=0
check CONTROL 7-nov "$C7B_HELD" "the same invocation with NO caller variable blocks — the fixture is live on this path"
C7C_OUT="$( cd "$SUT" && env "${BASEENV[@]}" GIT_INDEX_FILE="$DECOY" ./scripts/check-secrets.sh 2>&1 )"; C7C_RC=$?
C7C_HELD=1
[ "$C7C_RC" -ne 0 ] && names_fixture "$C7C_OUT" && C7C_HELD=0
check CONTROL 7-def "$C7C_HELD" "DEFAULT mode with the same malicious caller GIT_INDEX_FILE also still scans Sentinel"
reset_sut

# --------------------------------------------------------------- emulated-hook liveness -----
# L1 and L2 belong to cases 8-11 and are scored before them: if the emulation is inert or
# broken, nothing measured in 8-11 means anything.
reset_sut
L1_OUT="$(hookrun ".git/index")"; L1_RC=$?
L1_HELD=1
[ "$L1_RC" -eq 0 ] && says_clean "$L1_OUT" && L1_HELD=0
check CONTROL 8-L1 "$L1_HELD" "the emulated hook invocation with the CANONICAL index and nothing staged exits 0 and reports clean"
reset_sut; plant; git -C "$SUT" add "$FIX" >/dev/null 2>&1
L2_OUT="$(hookrun ".git/index")"; L2_RC=$?
L2_HELD=1
[ "$L2_RC" -ne 0 ] && names_fixture "$L2_OUT" && ! says_clean "$L2_OUT" && L2_HELD=0
check CONTROL 8-L2 "$L2_HELD" "the same emulated invocation BLOCKS a credential staged in the canonical index — the emulation is not inert"
reset_sut

# ============================================================================ case 8 =========
# A hook-supplied GIT_INDEX_FILE OUTSIDE the invoking repository's index directory must be
# REFUSED. Both wrong answers — honouring it, and silently ignoring it — produce exit 0 and
# `secret guard: clean` here, because the victim index and the canonical index are both clean.
# So the discriminator is the ABSENCE of the clean line together with a non-zero exit, never
# the exit status alone.
reset_sut
C8_PREVIEW="$( cd "$SUT" && GIT_INDEX_FILE="$VIC/.git/index" git diff --cached --raw --diff-filter=d 2>&1 | head -2 | tr '\n' '|' )"
C8_READABLE=1
printf '%s' "$C8_PREVIEW" | /usr/bin/grep -q 'VICTIM-ONLY.md' && C8_READABLE=0
check CONTROL 8-read "$C8_READABLE" \
    "the victim index is READABLE from the subject and reads CLEAN — a refusal here cannot be an unreadable-object artifact"
C8_OUT="$(hookrun "$VIC/.git/index")"; C8_RC=$?
C8_HELD=1
if [ "$C8_RC" -ne 0 ] && ! says_clean "$C8_OUT"; then C8_HELD=0; fi
check REQUIRED 8 "$C8_HELD" \
    "the hook REFUSES a GIT_INDEX_FILE outside the invoking repository's index directory (non-zero AND no clean report)"
check OBSERVED 8 0 "exit=$C8_RC  first line: $(printf '%s' "$C8_OUT" | head -1)"
reset_sut

# ============================================================================ case 9 =========
# A symlinked temporary index, and a nonexistent one, must both be REFUSED.
reset_sut
OUTSIDE="$WORK/outside.idx"; rm -f "$OUTSIDE"
( cd "$SUT" && GIT_INDEX_FILE="$OUTSIDE" git read-tree HEAD ) || die "cannot build the outside index for case 9a"
ln -sf "$OUTSIDE" "$SUT/.git/index.lock"
C9A_LINK=1
[ -L "$SUT/.git/index.lock" ] && C9A_LINK=0
check CONTROL 9-sym "$C9A_LINK" "the planted .git/index.lock really is a SYMLINK at scan time"
C9A_OUT="$(hookrun "$SUT/.git/index.lock")"; C9A_RC=$?
C9A_HELD=1
if [ "$C9A_RC" -ne 0 ] && ! says_clean "$C9A_OUT"; then C9A_HELD=0; fi
check REQUIRED 9a "$C9A_HELD" "the hook REFUSES a SYMLINKED temporary index (non-zero AND no clean report)"
check OBSERVED 9a 0 "exit=$C9A_RC  first line: $(printf '%s' "$C9A_OUT" | head -1)"
rm -f "$SUT/.git/index.lock"
reset_sut
MISSING="$SUT/.git/next-index-99999.lock"
C9B_ABSENT=1
[ ! -e "$MISSING" ] && C9B_ABSENT=0
check CONTROL 9-abs "$C9B_ABSENT" "the nonexistent temporary index really is absent at scan time"
C9B_OUT="$(hookrun "$MISSING")"; C9B_RC=$?
C9B_HELD=1
if [ "$C9B_RC" -ne 0 ] && ! says_clean "$C9B_OUT"; then C9B_HELD=0; fi
check REQUIRED 9b "$C9B_HELD" "the hook REFUSES a NONEXISTENT temporary index (non-zero AND no clean report)"
check OBSERVED 9b 0 "exit=$C9B_RC  first line: $(printf '%s' "$C9B_OUT" | head -1)"
reset_sut

# ======================================================================= cases 10 and 11 =====
# A VALID temporary index must be SCANNED. Built the way git builds one, with the canonical
# index left clean so that reading the wrong index is visible as a clean report.
scan_valid_temp() {   # $1 = basename under .git, $2 = case id, $3 = description
    local base="$1" cid="$2" desc="$3" T out rc held tset cset cred
    reset_sut
    T="$SUT/.git/$base"
    plant
    ( cd "$SUT" && GIT_INDEX_FILE="$T" git read-tree HEAD && GIT_INDEX_FILE="$T" git add "$FIX" ) \
        || die "cannot build the temporary index $base"
    tset="$( cd "$SUT" && GIT_INDEX_FILE="$T" git diff --cached --name-only 2>&1 | tr '\n' ' ' )"
    cset="$( cd "$SUT" && git diff --cached --name-only 2>&1 | tr '\n' ' ' )"
    cred="$( cd "$SUT" && GIT_INDEX_FILE="$T" git show ":$FIX" 2>/dev/null | /usr/bin/grep -c "$CRED_HEX" )"
    held=1
    if [ "$tset" = "$FIX " ] && [ "$cset" = "" ] && [ "$cred" = "1" ] && [ -f "$T" ] && [ ! -L "$T" ]; then held=0; fi
    check CONTROL "$cid-tmp" "$held" \
        "the planted $base is a regular file, CARRIES the credential, and the canonical index is empty"
    out="$(hookrun "$T")"; rc=$?
    held=1
    if [ "$rc" -ne 0 ] && names_fixture "$out" && ! says_clean "$out"; then held=0; fi
    check REQUIRED "$cid" "$held" "$desc"
    check OBSERVED "$cid" 0 "exit=$rc  first line: $(printf '%s' "$out" | head -1)"
    rm -f "$T"
    reset_sut
}
scan_valid_temp "index.lock" 10 \
    "the hook SCANS a valid .git/index.lock and BLOCKS the credential it carries, naming $FIX"
scan_valid_temp "next-index-24680.lock" 11 \
    "the hook SCANS a valid .git/next-index-<pid>.lock and BLOCKS the credential it carries, naming $FIX"

# ============================================================================ case 12 ========
# Nothing in any refusal case may touch the victim repository's configuration or files.
VIC_AFTER="$(vic_fp)"
VIC_COMMITS_AFTER="$(git -C "$VIC" rev-list --count HEAD 2>/dev/null)"
C12_HELD=1
[ "$VIC_AFTER" = "$VIC_BEFORE" ] && [ "$VIC_COMMITS_AFTER" = "$VIC_COMMITS_BEFORE" ] && C12_HELD=0
check REQUIRED 12 "$C12_HELD" \
    "the victim repository's HEAD, configuration, index and files are byte-identical after every refusal case"
check OBSERVED 12 0 "victim fingerprint before=$VIC_BEFORE after=$VIC_AFTER"
# The opposite control: the fingerprint must be able to MOVE, or case 12 asserts nothing.
printf 'a mutation made only to prove the victim fingerprint is live\n' >> "$VIC/VICTIM-ONLY.md"
VIC_MOVED="$(vic_fp)"
C12M_HELD=1
[ "$VIC_MOVED" != "$VIC_BEFORE" ] && C12M_HELD=0
check CONTROL 12-live "$C12M_HELD" "the victim fingerprint MOVES under a deliberate change — case 12 is not vacuous"
git -C "$VIC" checkout -q -- VICTIM-ONLY.md 2>/dev/null

# ============================================================================ case Z =========
# Harness hygiene. This author touched no production file and neither frozen harness; that is
# asserted here rather than claimed in prose.
hdr "hygiene"
Z_A1="$(shasum -a 256 "$ROOT/docs/review-2026-08-19-d057-targeted/batch-cards/A1-tests/a1-repo-identity.sh" 2>/dev/null | cut -d' ' -f1)"
Z_A2="$(shasum -a 256 "$ROOT/docs/review-2026-08-19-d057-targeted/batch-cards/A2-tests/a2-env-and-supervisor.sh" 2>/dev/null | cut -d' ' -f1)"
ZA_HELD=1; [ "$Z_A1" = "$FROZEN_A1_SHA" ] && [ "$Z_A2" = "$FROZEN_A2_SHA" ] && ZA_HELD=0
check CONTROL Z-frozen "$ZA_HELD" "both frozen harnesses are byte-identical to their declared sha256 values"
Z_DIFF="$(git -C "$ROOT" diff --stat "$CONTAINMENT_BASE" HEAD -- .githooks/pre-commit scripts/check-secrets.sh 2>/dev/null | wc -c | tr -d ' ')"
check OBSERVED Z-base 0 "git diff $CONTAINMENT_BASE..HEAD over the two production files is $Z_DIFF bytes (0 means the result transfers to $CONTAINMENT_BASE)"
check OBSERVED Z-prod 0 "pre-commit sha256 $(shasum -a 256 "$ROOT/.githooks/pre-commit" | cut -d' ' -f1)"
check OBSERVED Z-prod 0 "check-secrets sha256 $(shasum -a 256 "$ROOT/scripts/check-secrets.sh" | cut -d' ' -f1)"
Z_CFG=1; [ "$(opcfg_fp)" = "$OPCFG_BEFORE" ] && Z_CFG=0
check CONTROL Z-cfg "$Z_CFG" "the redirected global/system/XDG git configuration is unchanged by this run"
Z_TREE="$(git -C "$ROOT" status --porcelain -- .githooks scripts | wc -l | tr -d ' ')"
check OBSERVED Z-tree 0 "the repository under test has $Z_TREE modified path(s) under .githooks/ and scripts/"

# ---------------------------------------------------------------------------- summary -------
hdr "summary"
printf '  git      : %s\n' "$GIT_VERSION"
printf '  bash     : %s\n' "$BASH_VERSION_LINE"
printf '  measured : %s\n' "$ROOT_SHA"
printf '  REQUIRED failures : %s\n' "$req_fail"
printf '  CONTROL  failures : %s\n' "$ctl_fail"
if [ -n "${D062_MATRIX_OUT:-}" ]; then printf '%s' "$MATRIX_TSV" > "$D062_MATRIX_OUT"; fi
if [ "$ctl_fail" -gt 0 ]; then
    printf '\n  \033[1mHARNESS UNTRUSTWORTHY\033[0m — %s control(s) failed. No verdict above may be relied on.\n' "$ctl_fail"
    exit 2
fi
if [ "$req_fail" -gt 0 ]; then
    printf '\n  \033[1mREQUIRED FAILURES: %s\033[0m — every control held, so each failure is attributable.\n' "$req_fail"
    exit 1
fi
printf '\n  \033[1mALL REQUIRED CASES AND ALL CONTROLS HELD.\033[0m\n'
exit 0
