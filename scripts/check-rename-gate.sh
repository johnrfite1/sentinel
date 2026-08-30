#!/usr/bin/env bash
# Sentinel — expected-publication-state guard (D-032 / D-048 / D-074 / D-076 / D-082).
#
# THE NAME IS HISTORICAL AND IS KEPT ON PURPOSE. This started as D-016's rename gate: the
# project could not be named, so the guard's whole job was "fail if the repository has become
# public". D-074 ratified the name and lifted that block; D-076 re-scoped the citations. The
# file keeps its name because `scripts/test.sh` calls it by that name, operators know it by
# that name, and a rename would cost the history for nothing.
#
# WHAT IT IS NOW, AND WHY IT CHANGED (John's written ruling of 2026-08-30, transcribed as
# D-082(b)).
# The old guard hard-coded ONE policy — "private, always" — into its control flow. That was
# correct and it was also unmaintainable: the day publication is authorised, the only way to
# make the suite green is to DELETE the check. A guard whose retirement is the operator's
# next step is a guard that gets deleted early, by someone in a hurry, with no diff anybody
# reviews. So the policy moved OUT of the script and into a tracked artifact,
# `docs/publication-policy.state`, and the script became a guard on the DISTANCE between the
# declared state and the observed one.
#
#   WHERE THE AUTHORITY ACTUALLY SITS, because this file enforces a rule about who may decide
#   and must not misdescribe its own mandate. **The ruling is John's**, in writing, dated
#   2026-08-30: the state-aware re-scope, the tracked policy state, HELD_PRIVATE with rights
#   mode UNDECIDED as the default, the AUTHORIZED_PUBLIC preconditions, the every-remote
#   requirement, and the deep-gate rule that unreadable visibility may not be acknowledged
#   away for a public transition. **`D-082(b)` is an agent's authorised TRANSCRIPTION of that
#   ruling into the decision log — it is neither the ruling itself nor an agent decision**,
#   and D-082's own preamble says John's text governs wherever the transcription is more
#   specific. Cite D-082(b) to find the record; do not read it as the source of the authority.
#
#   RIGHTS MODE SHIPS `UNDECIDED` BECAUSE THE LICENCE IS DELIBERATELY HELD, NOT BECAUSE THE
#   FIELD IS UNFILLED (D-082(c)). John has deferred the proprietary-versus-open-source choice
#   pending a commercial check: a permissive grant on published code cannot be withdrawn, and
#   a licence protects the expression rather than the approach, so the decision is narrower
#   than it looks and is his alone. No agent may add or select a licence or resolve the rights
#   mode. `UNDECIDED` is therefore a POSITION, and the contradiction check below — which
#   refuses AUTHORIZED_PUBLIC while the rights mode is UNDECIDED — is enforcing a live hold,
#   not nagging about a blank field.
#
# WHAT DID NOT CHANGE, because the ruling was explicit that it must not:
#   * Every case the old guard failed, this one still fails. A public repository under the
#     held state is still `RENAME GATE VIOLATED`, exit 1. A deep/`--gate` run that could not
#     verify visibility still refuses unless SENTINEL_RENAME_GATE_UNVERIFIED_OK=1. Running
#     outside the Sentinel repository is still a refusal, exit 2.
#   * D-071's four-way behaviour (fast/deep x unverified/acknowledged) survives in substance,
#     with the acknowledgement now correctly restricted — see ACKNOWLEDGEMENT below.
#   * A passed gate is still not publication permission. D-048 makes a clean result a
#     PRECONDITION, never a TRIGGER, and this guard printing `held` is a clean result.
#
# THREE THINGS THE OLD GUARD GOT WRONG, all of which the ruling names:
#
#   1. IT READ `origin` AND ONLY `origin`. `git config --get remote.origin.url`, one string,
#      one lookup. A second remote — a fork, a mirror, a colleague's sandbox — added at any
#      point in the next ten years is invisible to it, and a public mirror is a publication
#      whatever it is called in `.git/config`. The census below enumerates EVERY configured
#      remote URL and pushurl and inspects all of them.
#   2. IT NEVER CHECKED WHICH REPOSITORY IT WAS JUDGING. It derived a slug from whatever
#      `origin` happened to be and reported on that. Repoint origin at some other private
#      repository and the old guard prints `clean` — truthfully, about the wrong repository.
#      `CANONICAL_REPOSITORY` in the state file pins the answer, and the guard says out loud
#      when it cannot resolve that pin.
#   3. ITS ACKNOWLEDGEMENT PATH HAD NO CEILING. `SENTINEL_RENAME_GATE_UNVERIFIED_OK=1` let a
#      deep gate pass while stating that visibility "was acknowledged, not verified". That is
#      an honest sentence and an acceptable trade while the answer is "stay private", because
#      the failure mode of a wrong acknowledgement is a check that ran late. It is NOT
#      acceptable while the state is AUTHORIZED_PUBLIC: there the acknowledgement would be
#      waving through the one measurement that decides whether an authorised publication
#      actually matches what is on the internet. Under AUTHORIZED_PUBLIC a deep gate that
#      cannot read visibility FAILS, and the acknowledgement is refused in writing.
#
# STATES AND THE DECISION TABLE. `docs/publication-policy.state` is parsed, never sourced.
#
#   PUBLICATION_STATE=HELD_PRIVATE      (the shipped state)
#     every configured GitHub remote must read PRIVATE
#       any non-PRIVATE .................................. FAIL (1)  RENAME GATE VIOLATED
#       all PRIVATE and the canonical pin resolved ....... held (0)
#       anything unreadable / unpinnable ................. UNVERIFIED
#                                                            fast: 0
#                                                            deep: 1, or 0 with the ACK
#
#   PUBLICATION_STATE=AUTHORIZED_PUBLIC (unreachable by editing one word — see below)
#     requires ALL of: a resolved RIGHTS_MODE; a SMITH_DECISION reference recorded in
#     docs/decisions.md; this state file committed; a licence file when the rights mode is
#     OPEN_SOURCE or SOURCE_AVAILABLE
#       any of those missing ............................. FAIL (1)
#       a NON-canonical GitHub remote is public .......... FAIL (1)
#       visibility unreadable, deep/--gate ............... FAIL (1), ACK REFUSED
#       visibility unreadable, fast ...................... UNVERIFIED (0)
#       canonical readable, others private ............... authorised (0)
#
#   The state file missing, unreadable, a symlink, malformed, holding an unknown or duplicate
#   key, or holding a value outside the enumerations ..... REFUSE (2)
#
# WHY AUTHORIZED_PUBLIC TAKES FOUR THINGS AND NOT ONE. The failure this guard exists to
# prevent is not a considered decision to publish; it is an unconsidered one. One word in one
# file, changed by someone who read neither the decision log nor this header, must not be
# enough. Two of the four requirements cannot be satisfied inside this file at all — the
# decision reference has to exist in `docs/decisions.md`, and the file itself has to be
# COMMITTED, so the change is in a diff before it is in effect. This is the project's
# zero-value principle applied to its own configuration: an unset, absent or damaged state
# reads as refusal, never as permission.
#
# EXIT CODES. 0 = consistent (or an accurately labelled fast UNVERIFIED). 1 = the observed
# world disagrees with the declared state, or a deep gate refuses. 2 = this guard cannot
# establish what it is judging and declines to report at all.
#
# COVERAGE, AND WHAT IS STILL NOT COVERED. This inspects configured git remotes and their
# GitHub visibility. It does not see demos, published links, package registries, portfolio or
# resume references, screenshots, or a copy of the tree someone put somewhere else. It cannot
# see a remote that is not configured. Those are review's job and are stated here so that a
# green run is not read as more than it is.
#
# NOT an S1 condition. It is a publication-state gate, checked continuously so that a
# divergence is caught the day it happens rather than at the next review.
set -uo pipefail

# --- Sentinel repository identity (D-060(2)) ---------------------------------
# This guard previously operated on whatever repository the caller stood in, so a
# run from elsewhere reported a clean result for the wrong tree. Identity is now
# derived from THIS FILE's own location, and every step is checked: `cd ""`
# returns 0 and does not abort even under `set -e`.
_sentinel_self="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)" || _sentinel_self=""
if [ -z "$_sentinel_self" ]; then
    echo "  FAIL  cannot resolve this script's own location; refusing." >&2; exit 2
fi
SENTINEL_ROOT="$(cd -- "$_sentinel_self" 2>/dev/null && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR git rev-parse --show-toplevel 2>/dev/null)" || SENTINEL_ROOT=""
if [ -z "$SENTINEL_ROOT" ] || [ ! -e "$SENTINEL_ROOT/scripts/test.sh" ] || [ ! -e "$SENTINEL_ROOT/.githooks/pre-commit" ]; then
    echo "  FAIL  this script is not inside the Sentinel repository; refusing." >&2; exit 2
fi
cd "$SENTINEL_ROOT" || { echo "  FAIL  cannot enter the Sentinel repository root; refusing." >&2; exit 2; }
# CALLER GIT OVERRIDES ARE REMOVED ONCE, HERE, BEFORE ANY BODY-LEVEL GIT CALL (12-F2).
# Scrubbing only the identity probe left every later `git` inheriting the caller's
# environment: GIT_DIR alone made this guard report clean over a live credential, and made
# install-hooks write into a victim repository. GIT_PREFIX is included although inert on
# git 2.50.1 — an inert variable today is not a guarantee tomorrow.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX

# --- Interface ---------------------------------------------------------------
# `--gate` is the deep profile and is what `scripts/test.sh --gate` passes; no argument is
# the fast profile and is what `scripts/test.sh` passes. UNKNOWN ARGUMENTS NOW REFUSE. The
# old parser ignored them silently, which meant a typo'd flag ran the wrong profile and
# reported success — the cheapest possible way to get a false pass out of this file.
PROFILE="fast"
for _arg in "$@"; do
    case "$_arg" in
        --gate) PROFILE="gate" ;;
        -h|--help)
            echo "usage: check-rename-gate.sh [--gate]"
            echo "  Compares the observed publication reality against the declared state in"
            echo "  docs/publication-policy.state. --gate is the deep profile."
            exit 0 ;;
        *)
            echo "  FAIL  unknown argument '$_arg'; refusing." >&2
            echo "        usage: check-rename-gate.sh [--gate]" >&2
            exit 2 ;;
    esac
done
ACK="${SENTINEL_RENAME_GATE_UNVERIFIED_OK:-}"

RED=$'\033[31m'; YEL=$'\033[33m'; RST=$'\033[0m'
[ -t 1 ] || { RED=""; YEL=""; RST=""; }

STATE_REL="docs/publication-policy.state"
COVER="Coverage: configured git remotes and their GitHub visibility. Not covered: demos, published links, package registries, portfolio or resume references, or copies of this tree held anywhere else."

note() { printf '  %s\n' "$1"; }
refuse() {
    echo "${RED}rename gate: REFUSED${RST} — $1" >&2
    echo "  An unestablished publication state is not a permitted one. ${2:-}" >&2
    exit 2
}

# --- 1. The declared state ---------------------------------------------------
# PARSED, NEVER SOURCED. `source`ing a policy file would make the policy artifact an
# execution vector: a line reading `PUBLICATION_STATE=$(curl …)` would run, and the guard
# would then report on a state that no reviewer could read out of the diff.
if [ -L "$STATE_REL" ]; then
    refuse "$STATE_REL is a symlink" "The state must be the tracked file itself, not a pointer at one."
fi
if [ ! -f "$STATE_REL" ]; then
    refuse "$STATE_REL is missing" "The canonical publication state is a required, tracked artifact; without it this guard has nothing to judge against."
fi
if [ ! -r "$STATE_REL" ]; then
    refuse "$STATE_REL is not readable"
fi

PUBLICATION_STATE=""; RIGHTS_MODE=""; SMITH_DECISION=""; CANONICAL_REPOSITORY=""
_seen_pub=0; _seen_rights=0; _seen_smith=0; _seen_repo=0
_lineno=0
while IFS= read -r _line || [ -n "$_line" ]; do
    _lineno=$((_lineno + 1))
    case "$_line" in
        *$'\r'*) refuse "$STATE_REL line $_lineno contains a carriage return" "A state file this guard cannot read byte-for-byte is not a state file it may act on." ;;
    esac
    case "$_line" in
        ''|'#'*) continue ;;
    esac
    # Deliberately strict: KEY=VALUE, uppercase key, no spaces, no quotes, no export.
    # A permissive parser is how `PUBLICATION_STATE = AUTHORIZED_PUBLIC` ends up silently
    # ignored while the operator believes it took effect.
    case "$_line" in
        [A-Z_]*=*) ;;
        *) refuse "$STATE_REL line $_lineno is not KEY=VALUE: '$_line'" ;;
    esac
    _k="${_line%%=*}"; _v="${_line#*=}"
    case "$_k" in *[!A-Z_]*) refuse "$STATE_REL line $_lineno has a malformed key '$_k'" ;; esac
    case "$_v" in *' '*|*$'\t'*|'') refuse "$STATE_REL line $_lineno has an empty or space-bearing value for $_k" ;; esac
    case "$_k" in
        PUBLICATION_STATE)    _seen_pub=$((_seen_pub + 1));       PUBLICATION_STATE="$_v" ;;
        RIGHTS_MODE)          _seen_rights=$((_seen_rights + 1)); RIGHTS_MODE="$_v" ;;
        SMITH_DECISION)       _seen_smith=$((_seen_smith + 1));   SMITH_DECISION="$_v" ;;
        CANONICAL_REPOSITORY) _seen_repo=$((_seen_repo + 1));     CANONICAL_REPOSITORY="$_v" ;;
        *) refuse "$STATE_REL line $_lineno declares an unknown key '$_k'" "An unrecognised key may be a policy this guard does not implement; it is not something to ignore." ;;
    esac
done < "$STATE_REL"

# DUPLICATES REFUSE RATHER THAN LAST-WINS. Two `PUBLICATION_STATE=` lines are a file whose
# meaning depends on the parser, and a reviewer reading the diff would see the one that does
# not take effect.
[ "$_seen_pub"    -eq 1 ] || refuse "$STATE_REL must declare PUBLICATION_STATE exactly once (saw $_seen_pub)"
[ "$_seen_rights" -eq 1 ] || refuse "$STATE_REL must declare RIGHTS_MODE exactly once (saw $_seen_rights)"
[ "$_seen_smith"  -eq 1 ] || refuse "$STATE_REL must declare SMITH_DECISION exactly once (saw $_seen_smith)"
[ "$_seen_repo"   -eq 1 ] || refuse "$STATE_REL must declare CANONICAL_REPOSITORY exactly once (saw $_seen_repo)"

case "$PUBLICATION_STATE" in
    HELD_PRIVATE|AUTHORIZED_PUBLIC) ;;
    *) refuse "PUBLICATION_STATE='$PUBLICATION_STATE' is not one of HELD_PRIVATE, AUTHORIZED_PUBLIC" ;;
esac
case "$RIGHTS_MODE" in
    UNDECIDED|OPEN_SOURCE|PROPRIETARY|SOURCE_AVAILABLE) ;;
    *) refuse "RIGHTS_MODE='$RIGHTS_MODE' is not one of UNDECIDED, OPEN_SOURCE, PROPRIETARY, SOURCE_AVAILABLE" ;;
esac
case "$CANONICAL_REPOSITORY" in
    */*/*/*) refuse "CANONICAL_REPOSITORY='$CANONICAL_REPOSITORY' has too many path segments; expected host/owner/name" ;;
    */*/*) ;;
    *) refuse "CANONICAL_REPOSITORY='$CANONICAL_REPOSITORY' is not of the form host/owner/name" ;;
esac
_c1="${CANONICAL_REPOSITORY%%/*}"; _crest="${CANONICAL_REPOSITORY#*/}"
_c2="${_crest%%/*}"; _c3="${_crest#*/}"
if [ -z "$_c1" ] || [ -z "$_c2" ] || [ -z "$_c3" ]; then
    refuse "CANONICAL_REPOSITORY='$CANONICAL_REPOSITORY' has an empty host, owner or name segment"
fi

echo "rename gate: declared state ${PUBLICATION_STATE} / rights ${RIGHTS_MODE} / decision ${SMITH_DECISION}"
note "canonical repository pinned to ${CANONICAL_REPOSITORY} ($STATE_REL)"

# --- 2. Is AUTHORIZED_PUBLIC actually authorised? ----------------------------
# These run BEFORE any network work, because a contradiction in the declaration is a failure
# whatever the remotes say, and an operator who mis-declared should be told so offline.
fail=0
violation() { echo "${RED}PUBLICATION STATE VIOLATION${RST} — $1"; fail=1; }

if [ "$PUBLICATION_STATE" = "AUTHORIZED_PUBLIC" ]; then
    if [ "$RIGHTS_MODE" = "UNDECIDED" ]; then
        violation "AUTHORIZED_PUBLIC with RIGHTS_MODE=UNDECIDED is a contradiction."
        note "Publication of a work whose terms of use nobody has chosen is not an authorised"
        note "publication. Resolve RIGHTS_MODE to OPEN_SOURCE, PROPRIETARY or SOURCE_AVAILABLE,"
        note "by the owner's decision and not by an agent's."
    fi
    # A reference, and a reference that exists. `NONE` and the usual placeholders are the
    # spellings an operator reaches for when filling a field they have no answer for.
    case "$SMITH_DECISION" in
        NONE|none|TBD|TODO|PENDING|N/A|NA|XXX|-)
            violation "AUTHORIZED_PUBLIC with SMITH_DECISION='$SMITH_DECISION' — no decision is referenced."
            note "The state may only be AUTHORIZED_PUBLIC with an explicit recorded decision reference." ;;
        D-[0-9][0-9][0-9]|S-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-*)
            if [ ! -f docs/decisions.md ]; then
                violation "cannot verify SMITH_DECISION='$SMITH_DECISION': docs/decisions.md is missing."
            elif ! grep -Fq -- "$SMITH_DECISION" docs/decisions.md; then
                violation "SMITH_DECISION='$SMITH_DECISION' does not appear in docs/decisions.md."
                note "A reference to a ruling nobody wrote down is not a ruling. Record the decision"
                note "in the canonical log first; that is the owner's act, not an agent's."
            else
                note "smith decision ${SMITH_DECISION} found in docs/decisions.md"
            fi ;;
        *)
            violation "SMITH_DECISION='$SMITH_DECISION' is not a recognised reference shape (D-NNN or S-YYYYMMDD-...)." ;;
    esac
    # The declaration must be COMMITTED. An uncommitted or untracked state file is a local
    # opinion; it has been through no diff and no review, and it is precisely the artifact
    # someone edits in a hurry.
    if ! git ls-files --error-unmatch -- "$STATE_REL" >/dev/null 2>&1; then
        violation "$STATE_REL is not tracked; AUTHORIZED_PUBLIC requires a committed state."
    elif ! git rev-parse --verify -q HEAD >/dev/null 2>&1; then
        violation "cannot resolve HEAD; AUTHORIZED_PUBLIC requires a committed state this guard can read."
    elif ! git show "HEAD:$STATE_REL" 2>/dev/null | cmp -s - "$STATE_REL"; then
        violation "$STATE_REL differs from its committed content at HEAD."
        note "An authorisation that exists only in the working tree has been reviewed by nobody."
    fi
    # A declared rights mode that implies distribution terms needs the terms to exist. This
    # checks for the FILE and deliberately does not read, judge, or suggest its contents:
    # choosing a licence is the owner's decision and is explicitly deferred.
    case "$RIGHTS_MODE" in
        OPEN_SOURCE|SOURCE_AVAILABLE)
            _lic=""
            for _cand in LICENSE LICENSE.md LICENSE.txt LICENCE LICENCE.md LICENCE.txt COPYING COPYING.md; do
                if [ -f "$_cand" ]; then _lic="$_cand"; break; fi
            done
            if [ -z "$_lic" ]; then
                violation "RIGHTS_MODE=$RIGHTS_MODE but no licence file exists at the repository root."
                note "The rights mode asserts distribution terms; the terms have to be in the tree."
            else
                note "licence file present: $_lic"
            fi ;;
    esac
fi

# --- 3. The remote census ----------------------------------------------------
# EVERY configured remote, fetch URL and pushurl, not `origin` and not `.url` alone. A
# pushurl is where a `git push` actually lands, so a guard reading only `.url` reports on a
# destination nothing is sent to.
if ! command -v git >/dev/null 2>&1; then
    refuse "git is not available"
fi

RM_URL=(); RM_NAME=(); RM_KIND=(); RM_SLUG=(); RM_VIS=()

_rg_lower() { printf '%s' "$1" | tr '[:upper:]' '[:lower:]'; }

# Prints "host/owner/name" and returns 0 for a network URL whose target this guard can name;
# returns 1 for a local path, a file:// URL, or anything it cannot parse. Returning 1 is NOT
# "safe" — it means unverifiable, and unverifiable is handled as UNVERIFIED below.
_rg_normalise() {
    local u="$1" rest="" host="" path=""
    case "$u" in
        file://*) return 1 ;;
        *://*)
            rest="${u#*://}"
            # Strip userinfo only when the `@` really is userinfo — i.e. before the first
            # `/`. `${rest#*@}` alone would eat a path that happens to contain an `@`.
            case "${rest%%/*}" in *@*) rest="${rest#*@}" ;; esac
            host="${rest%%/*}"
            host="${host%%:*}"
            case "$rest" in */*) path="${rest#*/}" ;; *) return 1 ;; esac ;;
        *@*:*)
            rest="${u#*@}"
            host="${rest%%:*}"
            path="${rest#*:}" ;;
        *) return 1 ;;
    esac
    [ -n "$host" ] || return 1
    while :; do case "$path" in */) path="${path%/}" ;; *) break ;; esac; done
    path="${path#/}"
    path="${path%.git}"
    while :; do case "$path" in */) path="${path%/}" ;; *) break ;; esac; done
    [ -n "$path" ] || return 1
    printf '%s/%s' "$(_rg_lower "$host")" "$path"
}

_rg_seen_url() {
    local q="$1" i=0
    while [ "$i" -lt "${#RM_URL[@]}" ]; do
        [ "${RM_URL[$i]}" = "$q" ] && return 0
        i=$((i + 1))
    done
    return 1
}

_census_tmp="$(mktemp "${TMPDIR:-/tmp}/sentinel-remotes.XXXXXXXX")" || refuse "cannot create a temporary file for the remote census"
_census_err="$(mktemp "${TMPDIR:-/tmp}/sentinel-remerr.XXXXXXXX")" || refuse "cannot create a temporary file for the remote census"
trap 'rm -f "$_census_tmp" "$_census_err"' EXIT

# `--get-regexp` exits 1 when nothing matches, which is a legitimate zero-remote repository.
# Any OTHER non-zero status is a git failure and must not be read as "no remotes" — that is
# the enumeration-that-succeeds-with-no-output failure mode this project keeps finding.
git config --get-regexp '^remote\.[^.]+\.(url|pushurl)$' >"$_census_tmp" 2>"$_census_err"
_census_rc=$?
if [ "$_census_rc" -ne 0 ] && [ "$_census_rc" -ne 1 ]; then
    refuse "git config could not enumerate remotes (exit $_census_rc): $(tr '\n' ' ' <"$_census_err")"
fi
if [ "$_census_rc" -eq 1 ] && [ -s "$_census_err" ]; then
    refuse "git config reported an error while enumerating remotes: $(tr '\n' ' ' <"$_census_err")"
fi

while IFS= read -r _rec; do
    [ -n "$_rec" ] || continue
    _key="${_rec%% *}"; _url="${_rec#* }"
    [ "$_key" = "$_rec" ] && continue        # a key with no value; nothing to inspect
    [ -n "$_url" ] || continue
    _rg_seen_url "$_url" && continue
    _nm="${_key#remote.}"; _nm="${_nm%.url}"; _nm="${_nm%.pushurl}"
    if _slug="$(_rg_normalise "$_url")"; then
        case "$_slug" in
            github.com/*/*/*) _kind="foreign" ;;   # more segments than owner/name
            github.com/*/*)   _kind="github" ;;
            *)                _kind="foreign" ;;
        esac
    else
        _slug=""; _kind="local"
    fi
    RM_URL+=("$_url"); RM_NAME+=("$_nm"); RM_KIND+=("$_kind"); RM_SLUG+=("$_slug"); RM_VIS+=("")
done < "$_census_tmp"
rm -f "$_census_tmp" "$_census_err"; trap - EXIT

note "remote census: ${#RM_URL[@]} configured remote URL(s)"

# --- 4. Visibility, per GitHub remote ----------------------------------------
unverified_reasons=""
add_unverified() { unverified_reasons="${unverified_reasons}${unverified_reasons:+$'\n'}    - $1"; }

_has_gh=0
command -v gh >/dev/null 2>&1 && _has_gh=1

_i=0
while [ "$_i" -lt "${#RM_URL[@]}" ]; do
    _nm="${RM_NAME[$_i]}"; _url="${RM_URL[$_i]}"; _kind="${RM_KIND[$_i]}"; _slug="${RM_SLUG[$_i]}"
    case "$_kind" in
        github)
            if [ "$_has_gh" -ne 1 ]; then
                RM_VIS[$_i]="UNREADABLE"
                add_unverified "$_nm ($_slug): gh CLI not available, visibility not read"
            else
                _owner_repo="${_slug#github.com/}"
                _v="$(gh repo view "$_owner_repo" --json visibility --jq .visibility 2>/dev/null || true)"
                case "$_v" in
                    PRIVATE|PUBLIC|INTERNAL) RM_VIS[$_i]="$_v" ;;
                    *)  RM_VIS[$_i]="UNREADABLE"
                        add_unverified "$_nm ($_slug): visibility could not be read (auth? network? repository gone?)" ;;
                esac
            fi ;;
        foreign)
            RM_VIS[$_i]="UNREADABLE"
            add_unverified "$_nm ($_slug): not a GitHub repository this guard can query; visibility unknown" ;;
        local)
            RM_VIS[$_i]="LOCAL"
            add_unverified "$_nm ($_url): local or unparseable remote; nothing to query" ;;
    esac
    note "remote $_nm -> ${_slug:-$_url} [${RM_KIND[$_i]}] visibility=${RM_VIS[$_i]}"
    _i=$((_i + 1))
done

if [ "${#RM_URL[@]}" -eq 0 ]; then
    add_unverified "no remote is configured, so the canonical repository cannot be confirmed from this tree"
fi

# --- 5. The canonical pin ----------------------------------------------------
# "Judging the repository it thinks it is" is a claim this guard must be able to SUPPORT, not
# assume. If no configured remote resolves to CANONICAL_REPOSITORY, every visibility answer
# above is about some other repository and the result is UNVERIFIED, not clean.
_canon_lc="$(_rg_lower "$CANONICAL_REPOSITORY")"
CANON_IDX=-1
_i=0
while [ "$_i" -lt "${#RM_URL[@]}" ]; do
    if [ -n "${RM_SLUG[$_i]}" ] && [ "$(_rg_lower "${RM_SLUG[$_i]}")" = "$_canon_lc" ]; then
        CANON_IDX=$_i; break
    fi
    _i=$((_i + 1))
done
if [ "$CANON_IDX" -ge 0 ]; then
    note "canonical pin resolved: remote '${RM_NAME[$CANON_IDX]}' is ${CANONICAL_REPOSITORY}"
elif [ "${#RM_URL[@]}" -gt 0 ]; then
    add_unverified "no configured remote resolves to the pinned canonical repository ${CANONICAL_REPOSITORY}"
fi

# --- 6. Verdict --------------------------------------------------------------
# Declaration failures are reported first and never suppressed by a network result: an
# operator who mis-declared needs to hear that even on an offline run.

# Held state: any non-PRIVATE GitHub remote is the violation this guard was built for.
if [ "$PUBLICATION_STATE" = "HELD_PRIVATE" ]; then
    _i=0
    while [ "$_i" -lt "${#RM_URL[@]}" ]; do
        case "${RM_VIS[$_i]}" in
            PUBLIC|INTERNAL)
                echo "${RED}RENAME GATE VIOLATED${RST} — ${RM_SLUG[$_i]} is ${RM_VIS[$_i]} (remote '${RM_NAME[$_i]}')."
                echo "  The declared state is HELD_PRIVATE. Publication is not authorised; Gate 8 passed with"
                echo "  limits, and D-048 makes that a precondition rather than a trigger (D-080)."
                echo "  Make the repository private again, or obtain an authorised state change — in that order."
                fail=1 ;;
        esac
        _i=$((_i + 1))
    done
fi

# Authorised state: the authorisation covers the CANONICAL repository. Any other GitHub
# remote is a publication surface nobody ruled on.
if [ "$PUBLICATION_STATE" = "AUTHORIZED_PUBLIC" ]; then
    _i=0
    while [ "$_i" -lt "${#RM_URL[@]}" ]; do
        if [ "$_i" -ne "$CANON_IDX" ]; then
            case "${RM_VIS[$_i]}" in
                PUBLIC|INTERNAL)
                    echo "${RED}PUBLICATION STATE VIOLATION${RST} — ${RM_SLUG[$_i]} is ${RM_VIS[$_i]} (remote '${RM_NAME[$_i]}')."
                    echo "  AUTHORIZED_PUBLIC authorises ${CANONICAL_REPOSITORY} and nothing else. A second public"
                    echo "  remote is a publication surface no decision covers."
                    fail=1 ;;
            esac
        fi
        _i=$((_i + 1))
    done
    if [ "$CANON_IDX" -lt 0 ]; then
        violation "AUTHORIZED_PUBLIC but no configured remote is ${CANONICAL_REPOSITORY}."
        note "The authorisation names a repository this tree is not connected to."
    fi
fi

if [ "$fail" -ne 0 ]; then
    echo
    echo "${RED}rename gate: FAILED.${RST} Do not weaken this guard to make a run pass (AGENTS.md)."
    echo "  ${COVER}"
    exit 1
fi

# UNVERIFIED. Never printed as a pass, in either profile.
if [ -n "$unverified_reasons" ]; then
    if [ "$PUBLICATION_STATE" = "AUTHORIZED_PUBLIC" ] && [ "$PROFILE" = "gate" ]; then
        # THE ACKNOWLEDGEMENT CEILING. Stated in full because the operator reading this is
        # the one holding the env var and needs to be told it was seen and refused.
        echo "${RED}rename gate: FAILED${RST} — visibility could not be verified for an AUTHORIZED_PUBLIC state in a deep gate:"
        printf '%s\n' "$unverified_reasons"
        if [ "$ACK" = "1" ]; then
            echo "  SENTINEL_RENAME_GATE_UNVERIFIED_OK=1 IS SET AND IS REFUSED HERE. The acknowledgement"
            echo "  covers a held-private state, where a missed check means a check that ran late. It does"
            echo "  not cover a public transition, where it would wave through the one measurement that"
            echo "  says whether the authorisation matches what is actually on the internet."
        fi
        echo "  Restore a readable visibility check (gh auth, network) and re-run the deep gate."
        echo "  ${COVER}"
        exit 1
    fi
    if [ "$PROFILE" = "gate" ]; then
        if [ "$ACK" = "1" ]; then
            echo "${YEL}rename gate: UNVERIFIED${RST} (SENTINEL_RENAME_GATE_UNVERIFIED_OK=1) — declared ${PUBLICATION_STATE}:"
            printf '%s\n' "$unverified_reasons"
            echo "  This --gate run ACKNOWLEDGES the visibility check was not verified; it was acknowledged, not verified private."
            echo "  Publication is not authorised; Gate 8 passed with limits, and D-048 makes that a precondition rather than a trigger (D-080). ${COVER}"
            exit 0
        fi
        echo "${YEL}rename gate: UNVERIFIED${RST} (deep/--gate refuses unless SENTINEL_RENAME_GATE_UNVERIFIED_OK=1) — declared ${PUBLICATION_STATE}:"
        printf '%s\n' "$unverified_reasons"
        echo "  Publication is not authorised; Gate 8 passed with limits, and D-048 makes that a precondition rather than a trigger (D-080). Deep profile requires acknowledgement or a readable visibility check."
        echo "  ${COVER}"
        exit 1
    fi
    # The fast profile is reachable under BOTH declared states, so this line must not assert
    # one of them. Printing "publication is not authorised" under a declared AUTHORIZED_PUBLIC
    # would be the guard contradicting the artifact it just read.
    echo "${YEL}rename gate: UNVERIFIED${RST} (SENTINEL_RENAME_GATE_UNVERIFIED_OK=1 acknowledges in --gate) — declared ${PUBLICATION_STATE}:"
    printf '%s\n' "$unverified_reasons"
    if [ "$PUBLICATION_STATE" = "AUTHORIZED_PUBLIC" ]; then
        echo "  Fast profile: this is NOT a pass, and the deep gate will REFUSE this result — an"
        echo "  AUTHORIZED_PUBLIC state may not be gated on an unread visibility check. Verify by hand."
    else
        echo "  Fast profile: this is NOT a pass. Publication is not authorised; Gate 8 passed with limits, and D-048 makes that a precondition rather than a trigger (D-080). Verify by hand before any public action."
    fi
    echo "  ${COVER}"
    exit 0
fi

if [ "$PUBLICATION_STATE" = "AUTHORIZED_PUBLIC" ]; then
    echo "rename gate: authorised (${CANONICAL_REPOSITORY} is ${RM_VIS[$CANON_IDX]}; rights ${RIGHTS_MODE}; decision ${SMITH_DECISION})"
    echo "  Every other configured GitHub remote reads PRIVATE. ${COVER}"
    exit 0
fi

echo "rename gate: held (${CANONICAL_REPOSITORY} and every configured GitHub remote are private)"
echo "  Publication is not authorised; Gate 8 passed with limits under D-080, and D-048 makes a clean"
echo "  result a precondition rather than a trigger. ${COVER}"
exit 0
