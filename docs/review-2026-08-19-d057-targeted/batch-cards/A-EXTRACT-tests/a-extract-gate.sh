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
usage: a-extract-gate.sh <repository-path> <exact-40-hex-commit>

  <repository-path>       the Sentinel repository to clone. Required.
  <exact-40-hex-commit>   the commit whose GATE is measured, as a FULL 40-character
                          lowercase object id. Required. Nothing else is accepted.

Same grammar as a-extract.sh, for the same reason: a name has to be RESOLVED, and
resolution is the part an ambiguous ref or an injected configuration setting gets to
influence. Abbreviated ids, branches, tags, HEAD, refs/…, revision expressions and
option-shaped input are all refused at exit 2 with ZERO scored verdicts.

  a-extract-gate.sh . bb664c626d592d86391f644bf014e76f2bbf7db4

Optional environment:
  A_EXTRACT_GATE_LOGDIR    directory to copy the three gate logs and the matrix into
USAGE
}

case "${1:-}" in
    -h|--help) usage; exit 2 ;;
esac

if [ "$#" -ne 2 ]; then
    printf '\n  PREFLIGHT FAILED: an evidentiary run takes EXACTLY a repository and a full 40-hex commit.\n' >&2
    printf '  Received %s argument(s). There is no default subject, by design.\n\n' "$#" >&2
    usage
    exit 2
fi

ROOT_ARG="$1"
SUBJECT_OID="$2"
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
    # A MALFORMED VERDICT IS A FAILURE — NOT A PASS, AND NOT SILENTLY UNCOUNTED.
    #
    # This used arithmetic (`[ "$held" -eq 0 ]`) on a value that can be EMPTY when the command
    # substitution producing it died — for instance on an unbound variable under `set -u`. Empty
    # made both `-eq` and the later `-ne` error with "integer expression expected", so the case
    # printed FAIL and then the failure counter was never incremented: the run reported its
    # controls held and exited 0 beside a printed FAIL. An independent review found exactly that
    # in the sibling gate harness. **String comparison, no arithmetic, and anything that is not
    # a literal 0 is a failure.**
    case "$held" in
        0) status="PASS" ;;
        *) status="FAIL" ;;
    esac
    if [ "$kind" = "OBSERVED" ]; then status="...."; fi
    printf '  case %-10s %-8s %s  %s\n' "$case_id" "$kind" "$status" "$desc"
    MATRIX_TSV="${MATRIX_TSV}${case_id}	${kind}	${status}	${desc}
"
    if [ "$status" = "FAIL" ]; then
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
# Caller configuration injection is neutralised before the first git invocation; the keys are
# enumerated from the environment rather than assumed to stop at a small n. INSTRUMENT-LOCAL
# isolation only — it does not reopen Batch A1 and does not address A1's `R-C` residual.
_scrub_git_config_env() {
    local v
    for v in $( ( env; printf '%s\n' "${!GIT_CONFIG_@}" ) 2>/dev/null \
                | sed -n 's/^\(GIT_CONFIG_KEY_[0-9][0-9]*\)=.*/\1/p; s/^\(GIT_CONFIG_VALUE_[0-9][0-9]*\)=.*/\1/p; /^GIT_CONFIG_KEY_[0-9][0-9]*$/p; /^GIT_CONFIG_VALUE_[0-9][0-9]*$/p' \
                | sort -u ); do
        unset "$v" 2>/dev/null || true
    done
    unset GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS 2>/dev/null || true
}

# OBJECT REPLACEMENT IS NEUTRALISED BEFORE THE FIRST GIT INVOCATION.
#
# `refs/replace/<oid>` silently substitutes one object for another in `git archive`,
# `git show <oid>:<path>` and `git cat-file blob <oid>:<path>` — every command that DELIVERS
# bytes — while `git cat-file --batch-all-objects`, the command chosen for the existence check
# precisely because it does no name resolution, is the ONE command immune to it. **So the
# command that VERIFIED and the commands that MEASURED did not share resolution semantics, and
# the verification said nothing about the bytes delivered.** An independent review obtained a
# complete run of a different commit's tree with every control green.
#
# MEASURED, both doors, before this repair:
#   plain                         verifier/test_verifier.py -> 924749d5…
#   refs/replace in the repo      same path                 -> 9ebb7fa7…   (another commit's bytes)
#   caller GIT_REPLACE_REF_BASE   same path                 -> 9ebb7fa7…
#   --batch-all-objects still reported the original present: 1
#
# `GIT_NO_REPLACE_OBJECTS=1` restores 924749d5… on every one of those routes, so ONE semantics
# now governs the existence check, the archive and the blob reads alike. The base variable is
# scrubbed as well: setting it is the caller's other door into the same mechanism.
_neutralise_object_replacement() {
    unset GIT_REPLACE_REF_BASE 2>/dev/null || true
    export GIT_NO_REPLACE_OBJECTS=1
}
_neutralise_object_replacement

# --- KNOWN-DOOR HARDENING UNDER D-065(2). THE LIST IS NOT CLAIMED COMPLETE. -----
#
# **D-065(1) sets the bar: this instrument must measure faithfully under a NON-ADVERSARIAL
# environment. A caller who can set arbitrary git environment variables can equally edit this
# file, so that class is OUT OF SCOPE and a newly named caller-controlled variable is not by
# itself a defect.** The variables handled here are handled because they are KNOWN and the cost
# is one line each — **that is hardening, not a claim that the environment is exhaustively
# controlled, and nothing here should be read as such a claim.**
#
# `GIT_TEMPLATE_DIR` earns its line: `git init` and `git clone` copy a caller-supplied template's
# `config` **and `hooks/`** into every repository this harness creates, which is precisely the
# repository-local configuration layer the `GIT_CONFIG_*` scrub exists to keep the caller out of.
# An independent review measured it rewriting a consumer in 16 subject repositories while this
# harness's own witness log recorded the tampered bytes executing 16 times and the run printed
# `CONTROL : 74 of 74 held`.
#
# `PATH` is PINNED BY PRECEDENCE, not by replacement: the system directories are prepended so
# `git`, `awk`, `sed`, `find`, `paste`, `sort`, `shasum`, `tar` and `python3` resolve there
# whatever a caller put in front of them, while the caller's remaining PATH is retained after
# them. **Stated precisely because the difference matters:** replacing PATH outright would have
# broken `forge`, which the sibling gate harness requires and which does not live in a system
# directory on this machine — so this raises the bar for shadowing a system tool and does NOT
# claim the tool search path is exhaustively controlled. `/usr/bin/grep` remains absolute, which
# is stronger than either.
_harden_known_doors() {
    unset GIT_TEMPLATE_DIR 2>/dev/null || true
    PATH="/usr/bin:/bin:/usr/sbin:/sbin:${PATH:-}"
    export PATH
}
_harden_known_doors
_scrub_git_config_env
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
    printf '  requested subject: %s\n' "$SUBJECT_OID"
    printf '  resolved subject : %s\n' "${SUBJECT_SHA:-<unresolved>}"
    printf '  pre-repair ref   : %s\n' "$PRE_REPAIR_SHA"
}
check OBSERVED P0 0 "gate harness sha256 $SELF_SHA"
check OBSERVED P1 0 "$(git --version) ; bash $(bash --version | head -1 | $GREP -o '[0-9][0-9.]*' | head -1) ; $(node --version 2>&1) ; $(python3 --version 2>&1)"

for t in git node python3; do command -v "$t" >/dev/null 2>&1 || die "$t is required"; done
command -v forge >/dev/null 2>&1 || die "forge is required — the gate's solidity stage cannot run without it"
[ -n "$ROOT" ] || die "the repository path '$ROOT_ARG' does not exist or is not a directory"
[ -d "$ROOT/.git" ] || die "$(sanitize_path "$ROOT") is not a git repository"
# THERE IS NO SUBJECT RESOLUTION STEP. Same ruling, same reason as `a-extract.sh`: a name must
# be resolved and resolution is what an ambiguous ref or an injected configuration setting gets
# to influence; an exact object id is looked up, not resolved. Measured: a branch literally named
# a 40-hex oid does NOT shadow that object, with `core.warnAmbiguousRefs` on or off.
case "$SUBJECT_OID" in
    -*) die "subject '$SUBJECT_OID' is option-shaped. The subject must be a bare 40-hex commit id." ;;
esac
if ! printf '%s' "$SUBJECT_OID" | $GREP -qE '^[0-9a-f]{40}$'; then
    die "subject '$SUBJECT_OID' is not an exact 40-character lowercase hex object id.
                     Branches, tags, HEAD, refs/…, revision expressions and abbreviated ids are
                     REFUSED — names are not accepted at all."
fi
_odb_type="$( cd "$ROOT" && git --no-replace-objects cat-file --batch-all-objects --batch-check='%(objectname) %(objecttype)' 2>/dev/null \
              | $GREP -m1 -E "^${SUBJECT_OID} " | awk '{print $2}' )"
[ -n "$_odb_type" ] || die "object $SUBJECT_OID is not present in $(sanitize_path "$ROOT")'s object database."
[ "$_odb_type" = "commit" ] || die "object $SUBJECT_OID exists but is a '$_odb_type', not a commit."
SUBJECT_SHA="$SUBJECT_OID"

BASECOPY="$WORK/gate-base"
git --no-replace-objects clone -q --no-hardlinks --local "$ROOT" "$BASECOPY" 2>/dev/null || die "cannot clone the repository"
( cd "$BASECOPY" && git --no-replace-objects checkout -q "$SUBJECT_SHA" ) || die "cannot check out $SUBJECT_SHA in the clone"
# A SUBJECT-PROVENANCE CONSISTENCY CONTROL — NOT an independence proof. The claim that two git
# commands are independent is withdrawn (R2): they share git's object resolver. What is asserted
# is that the clone is standing on the exact oid that was supplied.
_clone_head="$( cd "$BASECOPY" && git --no-replace-objects rev-parse HEAD 2>/dev/null )" || _clone_head=""
# THE CONTROL VERIFIES THE WORKTREE, NOT MERELY WHAT `HEAD` SAYS — `F2-4`.
#
# This harness pinned `--no-replace-objects` on ZERO commands and was protected only by the
# accident that clone's default refspec does not fetch `refs/replace`. **Protection by accident
# is not protection.** An independent review measured `GIT_REPLACE_REF_BASE=refs/remotes/origin/`
# giving the clone a worktree of another commit's tree — 533 tracked paths against 500 — while
# `rev-parse HEAD` still returned the requested oid, so a HEAD-only control passed.
#
# **A CORRECTION TO `INSTRUMENT-REVIEW-3` FOR THE RECORD, made here because that document is
# history and is not edited:** it recorded `rev-parse HEAD` returning the replacement target. On
# git 2.50.1 it does not — HEAD returns the requested oid and it is the WORKTREE that moves. The
# fourth review's measurement is the correct one, and it is why this control now compares trees.
_gate_tree_expected="$( cd "$ROOT" && git --no-replace-objects ls-tree -r --full-tree "$SUBJECT_SHA" 2>/dev/null \
        | awk '$2=="blob"{print $4"\t"$3}' | LC_ALL=C sort | shasum -a 256 | awk '{print $1}' )"
_gate_paths="$WORK/.gate-paths"; _gate_hashes="$WORK/.gate-hashes"
_gate_tree_actual="$( cd "$BASECOPY" 2>/dev/null && \
        git --no-replace-objects ls-files -s 2>/dev/null | awk '$1!="160000"{sub(/^[^\t]*\t/,""); print}' \
          | LC_ALL=C sort > "$_gate_paths" && \
        git hash-object --stdin-paths < "$_gate_paths" > "$_gate_hashes" 2>/dev/null && \
        paste "$_gate_paths" "$_gate_hashes" | shasum -a 256 | awk '{print $1}' )"
_gate_n="$($GREP -c . "$_gate_paths" 2>/dev/null || echo 0)"
check CONTROL P3-provenance "$([ "$_clone_head" = "$SUBJECT_SHA" ] && [ "${#SUBJECT_SHA}" = "40" ] && \
      [ "$_odb_type" = "commit" ] && [ -n "$_gate_tree_expected" ] && [ -n "$_gate_tree_actual" ] && \
      [ "$_gate_tree_expected" = "$_gate_tree_actual" ] && echo 0 || echo 1)" \
      "subject provenance is CONSISTENT (not independent): '$SUBJECT_OID' is an exact 40-hex oid of type '${_odb_type:-<none>}', HEAD is at it, and the clone's WORKTREE matches that commit's tree over ${_gate_n} tracked blob paths — expected ${_gate_tree_expected:0:12}…, worktree ${_gate_tree_actual:0:12}…"
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
s2_base="$(cd "$ROOT" && git --no-replace-objects show "$PRE_REPAIR_SHA:docs/gate-s2-evidence.md" | shasum -a 256 | awk '{print $1}')"
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
