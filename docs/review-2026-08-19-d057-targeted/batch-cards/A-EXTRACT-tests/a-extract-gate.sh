#!/usr/bin/env bash
# A-EXTRACT — GATE BINDING (D-059(7)).
#
# AUTHORITY: D-059(7). *"A standalone script that nothing invokes repeats the defect this work
# is trying to close. Required: invocation by the applicable fast and deep gate paths; a
# TOP-LEVEL falsification showing THE GATE fails when the targeted fact is wrong; an unchanged
# control showing the real gate passes; and an explicit statement that the guard covers only its
# enumerated canonical facts and is NOT general prose-consistency evidence."*
#
# THIS FILE IS A TEST. It makes no production repair and modifies nothing in the repository it
# is run from. The top-level gate is executed against a PRIVATE CLONE under TMPDIR; the live
# gate, the live proposal and every certified document are read-only inputs to `git clone` and
# to two `cp -R` operations, and nothing is written back.
#
# WHAT IT DEMONSTRATES — three things, and the third is the one that is usually assumed
#
#   G1  the UNCHANGED top-level fast gate PASSES in the isolated copy.
#   G2  a targeted A-EXTRACT guard failure makes the TOP-LEVEL gate FAIL at its NAMED STAGE.
#   G3  that failure CANNOT BE MASKED by another consumer succeeding — demonstrated from BOTH
#       ends of the stage order, because "a later stage cannot clear an earlier failure" and
#       "an earlier success cannot excuse a later failure" are two different properties and
#       only one of them is obvious from reading `fail=1`.
#
# THE THREE CONSUMER STAGES, by the exact banner `scripts/test.sh` prints:
#
#   == published EIP-712 type strings (D-023) ==        scripts/check-type-strings.sh
#   == §5.7.1 check coverage (D-031) ==                 scripts/check-eval-codes.sh
#   == vendor honesty (§7.5 Gate 5, D-008) ==           scripts/check-vendor-honesty.sh
#
# G2 breaks the FIRST of the three, so two consumer stages report success AFTER the failure.
# G3 breaks the LAST of the three, so two consumer stages report success BEFORE it. In both
# runs the gate must still refuse.
#
# WHAT THIS DOES **NOT** SHOW, said here rather than left to be assumed:
#
#   * It exercises the FAST profile only. `--gate` (deep) is not run — it costs several minutes
#     more per invocation and runs the corpus. The three consumer stages are unconditional in
#     both profiles, which is a reading of `scripts/test.sh` and not a measurement, and it is
#     recorded as a reading in COVERAGE.md.
#   * It says nothing about whether the guards are RIGHT. It shows the gate carries their
#     verdict. The guards' own correctness is what `a-extract.sh` measures.
#   * The A-EXTRACT guards cover only their enumerated canonical facts — six §5.8 type strings,
#     forty-one §5.7.1 identifiers, one §7.2 sentence, one §2 table hash. **They are NOT general
#     prose-consistency evidence** (D-058(6), D-059(7)).
#
# RUN THIS ALONE. `scripts/test.sh`'s TypeScript stage starts a real signer process over a real
# socket. Run concurrently with another heavy job, one of its RPC-surface tests can fail on
# timing and the suite then hangs with the signer still alive — observed once during authorship,
# recorded in GATE-BINDING.md rather than quietly re-run. A baseline that can fail for an
# unrelated reason is worthless as a control, so give this harness the machine.
#
# COST. Three full fast-gate runs. Budget roughly ten to fifteen minutes and a 180 MB scratch
# copy per subject. This is deliberately NOT part of `a-extract.sh`, which runs in about a
# minute and needs no toolchain beyond git, bash, awk, python3 and node.
#
# EXIT STATUS — the same three-way convention as `a-extract.sh`:
#   0  every REQUIRED and every CONTROL held
#   1  REQUIRED failures, all CONTROLs held
#   2  a CONTROL failed, or a preflight failed — the harness is untrustworthy
#
# Exit status of the GATE ITSELF is never used as a per-case discriminator. `scripts/test.sh`
# runs under a completion-token supervisor whose failure codes are its own; every assertion here
# is on the gate's OUTPUT — which stage banner appeared, what the guard printed beneath it, and
# whether `GATE PASSED` or `GATE FAILED` was emitted.

set -uo pipefail

# THE SUBJECT IS AN ARGUMENT, NOT A CONSTANT — the same instrument defect John found in
# `a-extract.sh`, in the same shape here: this script cloned and then checked out a HARDCODED
# commit, so it would have gone on measuring the pre-repair gate against a repaired tree.
# The historical baseline is kept as an immutable named reference and is never what gets
# checked out.
PRE_REPAIR_SHA="bb664c626d592d86391f644bf014e76f2bbf7db4"

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
    cat >&2 <<'USAGE'
usage: a-extract-gate.sh <repository-path> <subject-ref>

  <repository-path>  the Sentinel repository to clone. Required.
  <subject-ref>      the commit whose GATE is to be measured. Required.

There is NO DEFAULT SUBJECT. Omitting it is a preflight failure, not a fallback to the
historical base.

To reproduce the recorded baseline:

  a-extract-gate.sh . bb664c626d592d86391f644bf014e76f2bbf7db4

Optional environment:
  A_EXTRACT_GATE_LOGDIR    directory to copy the three gate logs and the matrix into
USAGE
}

case "${1:-}" in
    -h|--help) usage; exit 2 ;;
esac

if [ "$#" -lt 2 ]; then
    printf '\n  PREFLIGHT FAILED: an evidentiary run requires BOTH a repository and a subject ref.\n' >&2
    printf '  Received %s argument(s). There is no default subject, by design.\n\n' "$#" >&2
    usage
    exit 2
fi

ROOT_ARG="$1"
SUBJECT_REF="$2"
ROOT="$(cd -- "$ROOT_ARG" 2>/dev/null && pwd -P)" || ROOT=""

ORIG_HOME="${HOME:-}"
sanitize_path() {
    local q; q="$1"
    if [ -n "$ORIG_HOME" ]; then case "$q" in "$ORIG_HOME"*) q="~${q#"$ORIG_HOME"}" ;; esac; fi
    printf '%s' "$q" | sed -E 's#^/Users/[^/]+#~#; s#^/home/[^/]+#~#'
}

PROP_REL="Sentinel_Protocol_Lab_Proposal_v0_2.md"

STAGE_TS="== published EIP-712 type strings (D-023) =="
STAGE_EC="== §5.7.1 check coverage (D-031) =="
STAGE_VH="== vendor honesty (§7.5 Gate 5, D-008) =="

OK_TS="type strings: 6/6 published in §5.8 match eip712.ts exactly"
OK_EC="engine checks documented in §5.7.1"
OK_VH="the ablation report carries §7.2's caveat verbatim"

req_fail=0
ctl_fail=0
MATRIX_TSV=""

hdr() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }
say() { printf '        %s\n' "$*"; }

check() {
    local kind case_id held desc status
    kind="$1"; case_id="$2"; held="$3"; desc="$4"
    if [ "$kind" = "OBSERVED" ]; then status="...."
    elif [ "$held" -eq 0 ]; then status="PASS"; else status="FAIL"; fi
    printf '  case %-10s %-8s %s  %s\n' "$case_id" "$kind" "$status" "$desc"
    MATRIX_TSV="${MATRIX_TSV}${case_id}	${kind}	${status}	${desc}
"
    if [ "$held" -ne 0 ] && [ "$kind" != "OBSERVED" ]; then
        if [ "$kind" = "REQUIRED" ]; then req_fail=$((req_fail + 1)); else ctl_fail=$((ctl_fail + 1)); fi
    fi
}

die() { printf '\n  PREFLIGHT FAILED: %s\n' "$1"; exit 2; }

GREP=/usr/bin/grep

WORK="$(mktemp -d "${TMPDIR:-/tmp}/a-extract-gate.XXXXXX")" || die "cannot create a scratch directory"
cleanup() { [ -n "${WORK:-}" ] && rm -rf "$WORK"; }
trap cleanup EXIT

export HOME="$WORK/home";           mkdir -p "$HOME"
export XDG_CONFIG_HOME="$WORK/xdg"; mkdir -p "$XDG_CONFIG_HOME"
export GIT_CONFIG_GLOBAL="$WORK/gitconfig-global"; : > "$GIT_CONFIG_GLOBAL"
export GIT_CONFIG_SYSTEM="$WORK/gitconfig-system"; : > "$GIT_CONFIG_SYSTEM"
export GIT_CONFIG_NOSYSTEM=1
export GIT_TERMINAL_PROMPT=0
export GIT_AUTHOR_NAME="a-extract" GIT_AUTHOR_EMAIL="a-extract@invalid"
export GIT_COMMITTER_NAME="a-extract" GIT_COMMITTER_EMAIL="a-extract@invalid"
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX 2>/dev/null || true

# NO `grep -q` HERE, AND THE REASON IS A CONTROL FAILURE THIS HARNESS CAUGHT ON ITSELF.
#
# `printf '%s' "$big" | grep -qF "$needle"` exits grep the instant it matches, closing the pipe;
# `printf` then takes EPIPE, and under `set -o pipefail` the whole pipeline returns non-zero even
# though the needle WAS found. A gate log is ~60 KB, so this fired here where it never could in
# `a-extract.sh` — control `G1-stages` reported FAIL beside a `printf: write error: Broken pipe`
# on a run whose gate had plainly printed all three banners. **The control did its job: it exited
# 2 and refused to let anything beside it be believed.** `grep -c` consumes all of its input, so
# no signal is delivered and the exit status means what it says.
has()    { printf '%s' "$1" | $GREP -cF -- "$2" >/dev/null; }
has_re() { printf '%s' "$1" | $GREP -cE -- "$2" >/dev/null; }

# The banner and everything printed under it, up to the next banner. This is what makes
# "fails AT THE NAMED STAGE" a measurement rather than "the gate failed and this stage exists".
stage_body() {  # LOGFILE BANNER
    awk -v b="$2" '$0 == b { f = 1; next } f && /^== / { exit } f' "$1"
}

# ============================================================================ preflight ======
hdr "PREFLIGHT"

SELF_SHA="$(shasum -a 256 "${BASH_SOURCE[0]}" | awk '{print $1}')"
identity_block() {
    printf '  harness sha256   : %s\n' "$SELF_SHA"
    printf '  repository       : %s\n' "$(sanitize_path "${ROOT:-$ROOT_ARG}")"
    printf '  requested ref    : %s\n' "$SUBJECT_REF"
    printf '  resolved subject : %s\n' "${SUBJECT_SHA:-<unresolved>}"
    printf '  pre-repair ref   : %s\n' "$PRE_REPAIR_SHA"
}
check OBSERVED P0 0 "gate harness sha256 $SELF_SHA"
check OBSERVED P1 0 "$(git --version) ; bash $(bash --version | head -1 | $GREP -o '[0-9][0-9.]*' | head -1) ; $(node --version 2>&1) ; $(python3 --version 2>&1)"

for t in git node python3; do command -v "$t" >/dev/null 2>&1 || die "$t is required"; done
command -v forge >/dev/null 2>&1 || die "forge is required — the gate's solidity stage cannot run without it"
[ -n "$ROOT" ] || die "the repository path '$ROOT_ARG' does not exist or is not a directory"
[ -d "$ROOT/.git" ] || die "$(sanitize_path "$ROOT") is not a git repository"
# SUBJECT RESOLUTION IS FAIL-CLOSED, AND `--verify` IS **NOT** WHAT MAKES IT SO.
#
# Same correction as `a-extract.sh`, for the same measured reason: on git 2.50.1
# `git rev-parse --verify 'ambig^{commit}'` with a branch AND a tag named `ambig` returns the
# TAG's commit, exit 0, warning on stderr. `--verify` guarantees one OBJECT NAME, not one REF.
# `--quiet` then suppressed the warning and `2>/dev/null` discarded it.
#
# TWO INDEPENDENT MECHANISMS, each catching a case the other misses:
#   1. ENUMERATION — count the refs the name could denote (catches branch+tag).
#   2. STDERR — no `--quiet`, keep stderr, refuse on any ambiguity warning (catches a branch
#      named like an abbreviated object id, which enumeration alone sees as a single ref).
_ref_candidates() {
    printf '%s\n' "$1" "refs/$1" "refs/tags/$1" "refs/heads/$1" "refs/remotes/$1" "refs/remotes/$1/HEAD"
}
_matching_refs() {
    local c
    while IFS= read -r c; do
        [ -n "$c" ] || continue
        if ( cd "$ROOT" && git show-ref --verify --quiet -- "$c" 2>/dev/null ); then printf '%s\n' "$c"; fi
    done <<CANDIDATES
$(_ref_candidates "$1")
CANDIDATES
}
_peel_to_commit() {
    local oid t i
    oid="$1"; i=0
    while [ "$i" -lt 8 ]; do
        t="$( cd "$ROOT" && git cat-file -t "$oid" 2>/dev/null )" || return 1
        case "$t" in
            commit) printf '%s' "$oid"; return 0 ;;
            tag)    oid="$( cd "$ROOT" && git cat-file tag "$oid" 2>/dev/null | awk '/^object /{print $2; exit}' )"
                    [ -n "$oid" ] || return 1 ;;
            *)      return 1 ;;
        esac
        i=$((i + 1))
    done
    return 1
}
_independent_subject_sha() {  # never calls rev-parse; declines to choose when ambiguous
    local hits n oid
    hits="$(_matching_refs "$SUBJECT_REF")"
    n="$(printf '%s' "$hits" | $GREP -c . )" || n=0
    if [ "$n" = "1" ]; then
        oid="$( cd "$ROOT" && git show-ref --verify -- "$hits" 2>/dev/null | awk '{print $1; exit}' )"
    elif [ "$n" = "0" ]; then
        oid="$( cd "$ROOT" && printf '%s\n' "$SUBJECT_REF" | git cat-file --batch-check 2>/dev/null \
                 | awk '$2 != "missing" && $2 != "ambiguous" {print $1; exit}' )"
    else
        return 1
    fi
    [ -n "$oid" ] || return 1
    _peel_to_commit "$oid"
}

_ref_hits="$(_matching_refs "$SUBJECT_REF")"
_ref_n="$(printf '%s' "$_ref_hits" | $GREP -c . )" || _ref_n=0
if [ "$_ref_n" -gt 1 ]; then
    die "subject ref '$SUBJECT_REF' is AMBIGUOUS in $(sanitize_path "$ROOT") — it names ${_ref_n} refs:
$(printf '%s\n' "$_ref_hits" | sed 's/^/                       /')
                     git would silently prefer one and warn on stderr. This harness refuses."
fi

_rev_err_file="$WORK/.rev-parse-stderr"
SUBJECT_SHA="$( cd "$ROOT" && git rev-parse --verify "${SUBJECT_REF}^{commit}" 2>"$_rev_err_file" )" || SUBJECT_SHA=""
_rev_err="$(head -3 "$_rev_err_file" 2>/dev/null)"
rm -f "$_rev_err_file"

if printf '%s' "$_rev_err" | $GREP -qi 'ambiguous'; then
    die "subject ref '$SUBJECT_REF' is AMBIGUOUS in $(sanitize_path "$ROOT").
                     git said: ${_rev_err}
                     git resolved it anyway, to ${SUBJECT_SHA:-<none>}, by its own precedence
                     order. This harness refuses rather than inherit that choice."
fi

if [ -z "$SUBJECT_SHA" ]; then
    die "cannot resolve subject ref '$SUBJECT_REF' to exactly one commit in $(sanitize_path "$ROOT").
                     git said: ${_rev_err:-(no diagnostic)}
                     Missing, ambiguous, or not-a-commit is a REFUSAL here, never a fallback."
fi
[ -d "$ROOT/ts/node_modules" ] || die "ts/node_modules is absent; the gate's TypeScript stage cannot run"
for m in forge-std openzeppelin-contracts; do
    [ -d "$ROOT/contracts/lib/$m" ] || die "submodule working tree contracts/lib/$m is absent"
    [ -n "$(ls -A "$ROOT/contracts/lib/$m" 2>/dev/null)" ] || die "contracts/lib/$m is empty"
done
check OBSERVED P2 0 "toolchain present: git, node, python3, forge; node_modules and both submodule trees staged"

# THE ISOLATED COPY IS A CLONE, NOT AN ARCHIVE. `git archive` drops history, and several gate
# stages resolve refs. A clone at the base SHA plus the two ignored dependency trees is the
# smallest faithful subject. Nothing is written back to $ROOT.
BASECOPY="$WORK/gate-base"
git clone -q --no-hardlinks --local "$ROOT" "$BASECOPY" 2>/dev/null || die "cannot clone the repository"
( cd "$BASECOPY" && git checkout -q "$SUBJECT_SHA" ) || die "cannot check out $SUBJECT_SHA in the clone"
# P3 IS A CONTROL: the clone is standing on the commit the caller NAMED, not on whatever the
# source repository happened to have checked out and not on a constant compiled into this file.
_clone_head="$(cd "$BASECOPY" && git rev-parse HEAD 2>/dev/null)" || _clone_head=""
SUBJECT_SHA_INDEP="$(_independent_subject_sha)" || SUBJECT_SHA_INDEP=""
check CONTROL P3-subject "$([ "$_clone_head" = "$SUBJECT_SHA" ] && [ "${#SUBJECT_SHA}" = "40" ] && \
      [ -n "$SUBJECT_SHA_INDEP" ] && [ "$SUBJECT_SHA_INDEP" = "$SUBJECT_SHA" ] && echo 0 || echo 1)" \
      "'$SUBJECT_REF' resolves identically by TWO independent routes (rev-parse=${SUBJECT_SHA:-<none>}, show-ref+cat-file=${SUBJECT_SHA_INDEP:-<none>}) and the clone is checked out at it"
cp -R "$ROOT/ts/node_modules" "$BASECOPY/ts/node_modules" || die "cannot stage node_modules"
for m in forge-std openzeppelin-contracts; do
    rm -rf "$BASECOPY/contracts/lib/$m"
    cp -R "$ROOT/contracts/lib/$m" "$BASECOPY/contracts/lib/$m" || die "cannot stage contracts/lib/$m"
done
check OBSERVED P3 0 "isolated clone built at SUBJECT_SHA $SUBJECT_SHA with both dependency trees"
hdr "SUBJECT IDENTITY"
identity_block

# ============================================================================ G1 =============
hdr "G1 — the UNCHANGED top-level fast gate PASSES"
say "The opposite outcome for everything below. Without it, G2 and G3 would be satisfiable by a"
say "gate that fails on this machine for an unrelated reason."

G1LOG="$WORK/g1.log"
( cd "$BASECOPY" && ./scripts/test.sh ) > "$G1LOG" 2>&1
g1_rc=$?
sed -i '' 's/\x1b\[[0-9;]*m//g' "$G1LOG" 2>/dev/null || sed -i 's/\x1b\[[0-9;]*m//g' "$G1LOG" 2>/dev/null
g1="$(cat "$G1LOG")"

check REQUIRED G1 "$(has "$g1" "GATE PASSED" && ! has "$g1" "GATE FAILED" && echo 0 || echo 1)" \
      "the unchanged fast gate prints GATE PASSED and no GATE FAILED (supervisor rc=$g1_rc)"
check CONTROL  G1-stages "$(has "$g1" "$STAGE_TS" && has "$g1" "$STAGE_EC" && has "$g1" "$STAGE_VH" && echo 0 || echo 1)" \
      "all three A-EXTRACT consumer stages are INVOKED BY THE GATE, by name (D-059(7))"
check CONTROL  G1-order "$([ "$($GREP -n -F -- "$STAGE_TS" "$G1LOG" | cut -d: -f1)" -lt "$($GREP -n -F -- "$STAGE_EC" "$G1LOG" | cut -d: -f1)" ] && \
      [ "$($GREP -n -F -- "$STAGE_EC" "$G1LOG" | cut -d: -f1)" -lt "$($GREP -n -F -- "$STAGE_VH" "$G1LOG" | cut -d: -f1)" ] && echo 0 || echo 1)" \
      "stage order is type-strings, then eval-codes, then vendor-honesty — which is what makes G2 and G3 opposite ends"
check CONTROL  G1-green "$(has "$(stage_body "$G1LOG" "$STAGE_TS")" "$OK_TS" && \
      has "$(stage_body "$G1LOG" "$STAGE_EC")" "$OK_EC" && \
      has "$(stage_body "$G1LOG" "$STAGE_VH")" "$OK_VH" && echo 0 || echo 1)" \
      "on the unchanged copy each of the three stages reports its own success line"

# ============================================================================ G2 =============
hdr "G2 — a §5.8 guard failure fails the gate at its NAMED STAGE, and two LATER consumers cannot mask it"
say "The FIRST of the three consumer stages is broken. Everything the gate does afterwards —"
say "including two A-EXTRACT consumer stages that report success — must not clear the failure."

G2COPY="$WORK/gate-g2"
cp -R "$BASECOPY" "$G2COPY" || die "cannot build the G2 subject"
python3 - "$G2COPY/$PROP_REL" <<'PY'
import sys
path = sys.argv[1]
lines = open(path, encoding="utf-8").read().split("\n")
hits = 0
for i, line in enumerate(lines):
    if line.startswith("    ActionPayload(") and "bytes32 mandateHash,bytes32 policyHash" in line:
        lines[i] = line.replace("bytes32 mandateHash,bytes32 policyHash",
                                "bytes32 policyHash,bytes32 mandateHash")
        hits += 1
assert hits == 1, "expected exactly one ActionPayload publication, found %d" % hits
open(path, "w", encoding="utf-8").write("\n".join(lines))
PY
g2_mut=$?
check CONTROL  G2-mut "$([ "$g2_mut" = 0 ] && \
      [ "$($GREP -c '^    ActionPayload(uint16 schemaVersion,uint256 chainId,address vault,uint256 actionNonce,address target,uint256 valueWei,bytes32 dataHash,uint8 operation,bytes32 policyHash,bytes32 mandateHash' "$G2COPY/$PROP_REL")" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: §5.8 publishes a transposed ActionPayload; nothing else in the subject changed"

G2LOG="$WORK/g2.log"
( cd "$G2COPY" && ./scripts/test.sh ) > "$G2LOG" 2>&1
g2_rc=$?
sed -i '' 's/\x1b\[[0-9;]*m//g' "$G2LOG" 2>/dev/null || sed -i 's/\x1b\[[0-9;]*m//g' "$G2LOG" 2>/dev/null
g2="$(cat "$G2LOG")"
g2_ts="$(stage_body "$G2LOG" "$STAGE_TS")"
g2_ec="$(stage_body "$G2LOG" "$STAGE_EC")"
g2_vh="$(stage_body "$G2LOG" "$STAGE_VH")"

check REQUIRED G2-named "$(has_re "$g2_ts" 'DRIFT in ActionPayload' && ! has "$g2_ts" "$OK_TS" && echo 0 || echo 1)" \
      "the failure appears UNDER the named stage banner and names the type string, not merely somewhere in the log"
check REQUIRED G2-gate "$(has "$g2" "GATE FAILED" && ! has "$g2" "GATE PASSED" && echo 0 || echo 1)" \
      "the TOP-LEVEL gate prints GATE FAILED and never GATE PASSED (supervisor rc=$g2_rc)"
check REQUIRED G2-unmasked "$(has "$g2_ec" "$OK_EC" && has "$g2_vh" "$OK_VH" && has "$g2" "GATE FAILED" && echo 0 || echo 1)" \
      "NOT MASKED: the two LATER consumer stages both report success in this same run and the gate still fails"
check CONTROL  G2-scope "$(has "$g2_ec" "$OK_EC" && has "$g2_vh" "$OK_VH" && echo 0 || echo 1)" \
      "the mutation is targeted — it moved the §5.8 stage and left the other two consumers green"

# ============================================================================ G3 =============
hdr "G3 — a §7.2 guard failure fails the gate at ITS named stage, with two EARLIER consumers green"
say "The LAST of the three is broken instead. 'A later stage cannot clear an earlier failure'"
say "and 'earlier successes cannot excuse a later failure' are two properties, and a single"
say "direction demonstrates only one of them."

G3COPY="$WORK/gate-g3"
cp -R "$BASECOPY" "$G3COPY" || die "cannot build the G3 subject"
python3 - "$G3COPY/$PROP_REL" <<'PY'
import sys
path = sys.argv[1]
text = open(path, encoding="utf-8").read()
old = "This baseline makes the demo reproducible but is not evidence that current vendors miss Case 3."
new = ("This baseline makes the demo reproducible but, stated exactly, "
       "is not evidence that current vendors miss Case 3 at all.")
assert text.count(old) == 1, "expected exactly one §7.2 caveat, found %d" % text.count(old)
open(path, "w", encoding="utf-8").write(text.replace(old, new))
PY
g3_mut=$?
check CONTROL  G3-mut "$([ "$g3_mut" = 0 ] && \
      [ "$($GREP -c 'stated exactly' "$G3COPY/$PROP_REL")" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: §7.2 words its caveat differently; docs/ablation-report.md is untouched"

G3LOG="$WORK/g3.log"
( cd "$G3COPY" && ./scripts/test.sh ) > "$G3LOG" 2>&1
g3_rc=$?
sed -i '' 's/\x1b\[[0-9;]*m//g' "$G3LOG" 2>/dev/null || sed -i 's/\x1b\[[0-9;]*m//g' "$G3LOG" 2>/dev/null
g3="$(cat "$G3LOG")"
g3_ts="$(stage_body "$G3LOG" "$STAGE_TS")"
g3_ec="$(stage_body "$G3LOG" "$STAGE_EC")"
g3_vh="$(stage_body "$G3LOG" "$STAGE_VH")"

check REQUIRED G3-named "$(has_re "$g3_vh" "FAIL +docs/ablation-report.md" && ! has "$g3_vh" "$OK_VH" && echo 0 || echo 1)" \
      "the failure appears UNDER the vendor-honesty banner and names the artifact"
check REQUIRED G3-gate "$(has "$g3" "GATE FAILED" && ! has "$g3" "GATE PASSED" && echo 0 || echo 1)" \
      "the TOP-LEVEL gate prints GATE FAILED and never GATE PASSED (supervisor rc=$g3_rc)"
check REQUIRED G3-unmasked "$(has "$g3_ts" "$OK_TS" && has "$g3_ec" "$OK_EC" && has "$g3" "GATE FAILED" && echo 0 || echo 1)" \
      "NOT MASKED: the two EARLIER consumer stages both report success and the gate still fails"
check CONTROL  G3-scope "$(has "$g3_ts" "$OK_TS" && has "$g3_ec" "$OK_EC" && echo 0 || echo 1)" \
      "the mutation is targeted — it moved the vendor-honesty stage and left the other two consumers green"

# ============================================================================ integrity =====
hdr "INTEGRITY"
dirty="$(cd "$ROOT" && git status --porcelain -- "$PROP_REL" scripts ts contracts verifier fixtures .githooks | wc -l | tr -d ' ')"
check CONTROL Z-clean "$([ "$dirty" = "0" ] && echo 0 || echo 1)" \
      "the repository under test was not modified by this run ($dirty changed path(s) in the production boundary)"
s2_now="$(shasum -a 256 "$ROOT/docs/gate-s2-evidence.md" | awk '{print $1}')"
s2_base="$(cd "$ROOT" && git show "$PRE_REPAIR_SHA:docs/gate-s2-evidence.md" | shasum -a 256 | awk '{print $1}')"
check CONTROL Z-signed "$([ "$s2_now" = "$s2_base" ] && echo 0 || echo 1)" \
      "docs/gate-s2-evidence.md IN THE LIVE TREE is byte-identical to PRE_REPAIR_SHA — no signed document was read for change"

if [ -n "${A_EXTRACT_GATE_LOGDIR:-}" ]; then
    mkdir -p "$A_EXTRACT_GATE_LOGDIR"
    for n in g1 g2 g3; do cp "$WORK/$n.log" "$A_EXTRACT_GATE_LOGDIR/$n.log" 2>/dev/null; done
    printf '%s' "$MATRIX_TSV" > "$A_EXTRACT_GATE_LOGDIR/matrix.tsv"
fi

hdr "SUMMARY"
identity_block
echo
req_total="$(printf '%s' "$MATRIX_TSV" | awk -F'\t' '$2=="REQUIRED"' | wc -l | tr -d ' ')"
ctl_total="$(printf '%s' "$MATRIX_TSV" | awk -F'\t' '$2=="CONTROL"'  | wc -l | tr -d ' ')"
printf '  REQUIRED : %s of %s held\n' "$((req_total - req_fail))" "$req_total"
printf '  CONTROL  : %s of %s held\n' "$((ctl_total - ctl_fail))" "$ctl_total"
echo
if [ "$ctl_fail" -ne 0 ]; then
    echo "  CONTROL FAILURE — the harness is untrustworthy; no verdict beside a failing control holds."
    exit 2
fi
if [ "$req_fail" -ne 0 ]; then
    echo "  REQUIRED FAILURES with every control holding: the gate binding is NOT established."
    exit 1
fi
echo "  FAST-PROFILE GATE BINDING MEASURED: the gate passes unchanged, fails at the named stage"
echo "  when a targeted A-EXTRACT fact is wrong, and that failure survives other consumers"
echo "  succeeding both before and after it."
echo
echo "  D-059(7) IS NOT FULLY DISCHARGED BY THIS RUN. The DEEP profile (--gate) was not"
echo "  invoked; its coverage rests on static control-flow evidence only. The independent"
echo "  post-repair verification must run ./scripts/test.sh --gate at the exact candidate SHA"
echo "  and capture the three stage banners. See GATE-BINDING.md STATUS."
exit 0
