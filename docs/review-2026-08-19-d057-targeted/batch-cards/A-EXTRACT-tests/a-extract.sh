#!/usr/bin/env bash
# BATCH A-EXTRACT — falsification harness for named-scope extraction, exact membership,
# and publication/definition uniqueness.
#
# AUTHORITY: D-058(1) (test-first separation), D-058(6) (no generic prose checker; logical
# Markdown paragraphs must be normalized across hard line wraps), D-059(2) (a sibling
# enumeration identifies candidates, it does not adjudicate them), D-059(8) (section
# extraction and source uniqueness are TWO properties, not one primitive), D-060(1) (batch
# cards; completeness is claimed only inside the declared boundary).
#
# THIS FILE IS A TEST. It makes no production repair. It modifies nothing in the repository
# it is run from: every case operates on a private snapshot of the base commit, extracted
# into a scratch directory this script created and removes on exit.
#
# THE ONE INVARIANT UNDER TEST
#
#   A checker naming a section, publication, or identifier must inspect that exact scope and
#   require the exact value. It must not pass through a prefix, outside-section decoy,
#   duplicate publication, incorrect heading boundary, or first-match tie-break.
#
# THE BOUNDARY — four consumers, and only their named-scope / exact-membership / uniqueness
# blocks:
#
#   TS  scripts/check-type-strings.sh      §5.8 extraction, per-type publication uniqueness,
#                                          and the eip712.ts source-definition lookup
#   EC  scripts/check-eval-codes.sh        §5.7.1 extraction and per-code membership
#   VH  scripts/check-vendor-honesty.sh    the §7.2 caveat extraction and the ablation-report
#                                          comparison, plus the §2 pinned-table control
#   VP  verifier/test_verifier.py          TestPublishedTypeStrings — the §5.8 consumer
#
# Nothing else in those files is in scope, and no other script is touched.
#
# HOW TO READ THE OUTPUT. Every scored line is one of
#   REQUIRED  — an assertion of the required behaviour. Several of these FAIL at the
#               pre-repair base commit; that is the point of the exercise. A REQUIRED line
#               that cannot fail is worthless.
#   CONTROL   — the paired opposite outcome, or evidence that a mutation really applied.
#               A failing CONTROL means the harness is measuring nothing and NO conclusion
#               may be drawn beside it.
#   OBSERVED  — a recorded fact. Asserts nothing and counts toward neither tally.
#
# EXIT STATUS — a control failure is a DIFFERENT exit path from a required-case failure.
#   0  every REQUIRED and every CONTROL held
#   1  REQUIRED failures, all CONTROLs held      (the expected pre-repair shape)
#   2  a CONTROL failed, or a preflight failed   (the harness is untrustworthy — fix it first)
#
# EXIT STATUS IS NOT A VALID DISCRIMINATOR FOR ANY INDIVIDUAL CASE and this harness never
# uses it as one. Three of the four consumers exit 1 for every finding they have, so a
# non-zero exit says nothing about WHICH finding fired. Every assertion here is on the
# consumer's OUTPUT: the success line must be absent, and the finding must be NAMED — the
# type string, the identifier, the section, or the artifact it is about.
#
# HEADING DEPTH IS DERIVED FROM THE ANCHOR, NOT FROM A FIXED CLASS. `check-type-strings.sh`
# anchors on a `###` heading and `check-eval-codes.sh` on a `####` one, and both terminate
# their scan on `^#{1,4} `. Cases 7 and 8 exercise the SAME `####` depth against BOTH
# anchors: below a `###` anchor it is a deeper subsection that must stay INSIDE, and at a
# `####` anchor it is a same-depth heading that must END the section. A fixed class cannot
# satisfy both, which is what makes the pair the evidence rather than either one alone.
#
# METHOD NOTES, recorded so the next author does not re-pay for them:
#   * /usr/bin/grep, never the shell's grep — the wrapper on this workstation honours
#     --ignore-files and can return a clean-looking zero. Preflight P1 plants a canary.
#   * bash 3.2: no mapfile, no associative arrays, and "${arr[@]}" on an EMPTY array is an
#     unbound-variable error under `set -u`. No arrays are used here.
#   * A LINE-ORIENTED GREP IS DISALLOWED for a Markdown paragraph check (D-058(6)). Case 11
#     is that rule made into a probe: the same sentence is hard-wrapped on the proposal side
#     and on the report side, and the consumer must find it in both.
#   * Refusal vocabulary is matched as a SET OF ALTERNATIVES, never as one exact sentence.
#     A repair chooses its own wording; what it may not choose is to stay silent, to report
#     success, or to name something other than the finding.
#   * No credential-shaped fixture is needed by any case here, so none is assembled. The
#     mutations are Markdown headings, type strings and identifier tokens.

set -uo pipefail

# ---------------------------------------------------------------------------- preamble ------
# THE SUBJECT IS AN ARGUMENT, NOT A CONSTANT. THIS IS THE INSTRUMENT DEFECT JOHN FOUND, AND
# IT WAS BLOCKING.
#
# Until this correction the harness hardcoded one commit and archived THAT, whatever repository
# or HEAD it was pointed at. `P3` noticed a differing HEAD and emitted an OBSERVED warning it
# could not fail on. So after a repair the harness would have snapshotted the PRE-REPAIR tree,
# measured the PRE-REPAIR consumers, and reported `21 of 49` with every control green —
# for ever. And `CARD.md` forbids the implementer from touching the harness, so nobody
# downstream could have corrected it. **An instrument that always reports the same number is
# not a failing instrument; it is a confident wrong answer, which is this project's named
# defect class.** Found in John's review of the contract, not by this author and not by a run.
#
# THE CORRECTION, in one sentence: an evidentiary run is given a repository AND a subject
# commit, resolves the subject or REFUSES, archives the SUBJECT, and prints all five identity
# facts beside every result so a reader can tell what was measured without trusting a claim.

# The historical baseline, kept as an IMMUTABLE NAMED REFERENCE so the original measurement
# stays reproducible — `21 of 49 REQUIRED, 70 of 70 CONTROL` was measured here. It is never
# what gets archived, and no default falls back to it.
PRE_REPAIR_SHA="bb664c626d592d86391f644bf014e76f2bbf7db4"

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
    cat >&2 <<'USAGE'
usage: a-extract.sh <repository-path> <exact-40-hex-commit>

  <repository-path>       the Sentinel repository to measure. Required.
  <exact-40-hex-commit>   the commit to measure, as a FULL 40-character lowercase
                          object id. Required. Nothing else is accepted.

ACCEPTED:   ^[0-9a-f]{40}$ naming an object of type `commit` in that repository.

REJECTED, every one at exit 2 with ZERO scored verdicts:
  abbreviated object ids            bb664c6
  branch / tag / remote names       main, v1.0, origin/main
  symbolic refs                     HEAD, @
  fully qualified refs              refs/heads/main, refs/tags/v1.0
  revision expressions              HEAD~1, x^{commit}, :/text, @{u}, a..b
  option-shaped input               anything beginning with -
  uppercase hex                     BB664C6…  (git's canonical form is lowercase)
  objects that are missing, or exist but are not commits

WHY SO NARROW. A name has to be RESOLVED, and resolution is what an attacker or an
accident gets to influence — a tag shadowing a branch, a branch shadowing an
abbreviation, `core.warnAmbiguousRefs=false` silencing the warning that detected it.
An exact object id is not resolved, it is looked up. **There is no ref-resolution step
left to defeat.** Convenience refs buy this instrument nothing and cost it its only
remaining fail-open.

To reproduce the recorded pre-repair baseline:

  a-extract.sh . bb664c626d592d86391f644bf014e76f2bbf7db4

Optional environment:
  A_EXTRACT_EVIDENCE_DIR   directory to write per-case consumer output into
  A_EXTRACT_MATRIX_OUT     file to write the case matrix TSV into
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

# HOME is redirected into the scratch area further down, so the real one is captured HERE, while
# it is still the user's, purely so paths can be printed without a machine-specific prefix.
ORIG_HOME="${HOME:-}"
sanitize_path() {  # PATH -> the same path with any home prefix replaced by ~
    local q; q="$1"
    if [ -n "$ORIG_HOME" ]; then case "$q" in "$ORIG_HOME"*) q="~${q#"$ORIG_HOME"}" ;; esac; fi
    printf '%s' "$q" | sed -E 's#^/Users/[^/]+#~#; s#^/home/[^/]+#~#'
}

PROP_REL="Sentinel_Protocol_Lab_Proposal_v0_2.md"
SRC_REL="ts/src/signer/eip712.ts"
RPT_REL="docs/ablation-report.md"

# The exact anchors the four consumers name. Written here once so that a case which needs to
# duplicate, delete or shadow one cannot drift from what the consumer actually looks for.
H58="### 5.8 EIP-712 Type Strings (normative)"
H59="### 5.9 Enumerations (normative)"
H56="### 5.6 EvidenceBundle"
H571="#### 5.7.1 Check coverage (auditable; the identifiers are not normative)"
H6="## 6. AI and Context Scope"
H72="### 7.2 Fair Baselines"

CAVEAT_PHRASE='is not evidence that current vendors miss Case 3'
CAVEAT_SENTENCE='This baseline makes the demo reproducible but is not evidence that current vendors miss Case 3.'

# The Gate 5 constant this batch must leave alone (case 14). Read from the script under test
# rather than trusted from here; this is the value expected, and a mismatch is reported.
GATE5_PINNED="c9034750e56b8801be7cd31cce33c42caad209013a61ed7082155db33903959c"

req_fail=0
ctl_fail=0
MATRIX_TSV=""

hdr() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }
say() { printf '        %s\n' "$*"; }

check() {   # KIND CASE HELD DESC   — HELD is 0 when the asserted behaviour was observed.
    local kind case_id held desc status; kind="$1"; case_id="$2"; held="$3"; desc="$4"
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

# ---------------------------------------------------------------------------- isolation -----
# HOME, XDG and the global / system git configuration are redirected into the scratch area for
# the whole run. Nothing here writes git configuration into a repository it did not create,
# and no repository outside the scratch area is written to at all.
WORK="$(mktemp -d "${TMPDIR:-/tmp}/a-extract.XXXXXX")" || die "cannot create a scratch directory"
cleanup() { [ -n "${WORK:-}" ] && rm -rf "$WORK"; }
trap cleanup EXIT

export HOME="$WORK/home";               mkdir -p "$HOME"
export XDG_CONFIG_HOME="$WORK/xdg";     mkdir -p "$XDG_CONFIG_HOME"
export GIT_CONFIG_GLOBAL="$WORK/gitconfig-global"; : > "$GIT_CONFIG_GLOBAL"
export GIT_CONFIG_SYSTEM="$WORK/gitconfig-system"; : > "$GIT_CONFIG_SYSTEM"
export GIT_CONFIG_NOSYSTEM=1
export GIT_TERMINAL_PROMPT=0
export GIT_AUTHOR_NAME="a-extract" GIT_AUTHOR_EMAIL="a-extract@invalid"
export GIT_COMMITTER_NAME="a-extract" GIT_COMMITTER_EMAIL="a-extract@invalid"
# CALLER CONFIGURATION INJECTION IS NEUTRALISED BEFORE THE FIRST GIT INVOCATION.
#
# `GIT_CONFIG_COUNT` with `GIT_CONFIG_KEY_<n>` / `GIT_CONFIG_VALUE_<n>`, and the older
# `GIT_CONFIG_PARAMETERS`, inject configuration into every git process without touching any
# file — so a caller could set `core.warnAmbiguousRefs=false`, or point `safe.directory`,
# `core.hooksPath`, `include.path` and similar at whatever it liked, and nothing on disk would
# show it. The keys are enumerated FROM THE ENVIRONMENT rather than assumed to stop at some
# small n, because "we scrubbed the first ten" is the kind of bound that is wrong exactly once.
#
# **SCOPE, AND IT IS DELIBERATELY NARROW (John's framing, recorded here so it is not
# overstated): this is an INSTRUMENT-LOCAL isolation repair. It does not reopen Batch A1 and it
# does not claim to solve A1's repository-wide `R-C` residual.** It makes THIS harness's git
# calls unconfigurable by its caller. It says nothing about any other entry point.
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
_scrub_git_config_env
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX 2>/dev/null || true
# The private empty global/system configuration set above is RETAINED — scrubbing the injection
# variables and pinning the config files are two different defences and both are wanted.

GREP=/usr/bin/grep
WITNESS_LOG="$WORK/witness.tsv"; : > "$WITNESS_LOG"

# ---------------------------------------------------------------------------- primitives ----
# Every mutation is a whole-line operation keyed on the EXACT line text, never on a line
# number and never on a regular expression, so a fixture that has moved fails to mutate
# rather than mutating something else. Each case then proves its mutation applied.

# THE INSERTED TEXT TRAVELS THROUGH A FILE, NOT THROUGH `awk -v`.
#
# `awk -v t="line1<newline>line2"` is a hard error — "newline in string" — and the first
# version of this harness carried it. awk printed the diagnostic to stderr, the mutation did
# NOT apply, and the case beside it reported PASS against an unmutated fixture. That is the
# recorded "a falsification probe can be dead and its silence reads exactly like a pass"
# class, reproduced inside a harness written to probe for it. Every insertion is now
# multi-line-capable by construction, and every case proves its own mutation applied.
edit_at() {  # FILE MODE MATCHLINE TEXT      MODE = before | after | replace | delete
    local f mode m t tf
    f="$1"; mode="$2"; m="$3"; t="$4"
    tf="$WORK/.edit-block"
    printf '%s\n' "$t" > "$tf"
    edit_at_file "$f" "$mode" "$m" "$tf"
    rm -f "$tf"
}

edit_at_file() {  # FILE MODE MATCHLINE BLOCKFILE
    local f mode m bf
    f="$1"; mode="$2"; m="$3"; bf="$4"
    awk -v mode="$mode" -v m="$m" -v bf="$bf" '
        function emit(   line) { while ((getline line < bf) > 0) print line; close(bf) }
        $0 == m {
            if (mode == "before")  { emit(); print; next }
            if (mode == "after")   { print; emit(); next }
            if (mode == "replace") { emit(); next }
            if (mode == "delete")  { next }
        }
        { print }
    ' "$f" > "$f.a-extract.tmp" && mv "$f.a-extract.tmp" "$f"
}

# THE HARNESS'S OWN SECTION READER IS ANCHOR-DERIVED, AND THIS IS NOT DECORATION.
#
# It was written with a fixed `^#{1,6} ` terminator — the same fixed-class mistake case 7 exists
# to falsify — and control `10c-mut` failed because of it: a `#### 7.2.1` subsection planted
# INSIDE `§7.2` terminated the harness's own read of `§7.2`, so the harness reported that its
# own mutation had not applied. An instrument that carries the defect it is measuring cannot be
# believed about it. The terminator depth is now computed from the ANCHOR's own `#` run, and the
# explicit form remains available for the two places that genuinely want a different boundary.
anchor_depth() {  # HEADINGLINE -> the number of leading '#'
    printf '%s' "$1" | awk '{ n = 0; while (substr($0, n + 1, 1) == "#") n++; print n }'
}

section_of() {  # FILE ANCHORLINE [ENDRE]  -> the section body on stdout
    local f a endre d
    f="$1"; a="$2"; endre="${3:-}"
    if [ -z "$endre" ]; then
        d="$(anchor_depth "$a")"
        [ "$d" -ge 1 ] || { echo "section_of: '$a' is not a heading" >&2; return 1; }
        endre="^#{1,${d}} "
    fi
    awk -v a="$a" -v e="$endre" '$0 == a { f = 1; next } f && $0 ~ e { exit } f' "$f"
}

# COUNTING IS NORMALIZED, NOT LINE-ORIENTED (D-058(6)). Every "is the sentence there?" answer
# this harness computes for itself collapses newlines and runs of blanks first, so the harness
# cannot fall into the wrap trap it exists to probe in the consumers.
norm_count() {  # FILE PHRASE -> number of normalized occurrences
    tr '\n' ' ' < "$1" | tr -s ' ' | $GREP -o -F "$2" | wc -l | tr -d ' '
}

sec_sub() {  # FILE ANCHORLINE OLD NEW — literal substitution, in-section only, ANCHOR-DERIVED
    local f a d e
    f="$1"; a="$2"
    d="$(anchor_depth "$a")"
    [ "$d" -ge 1 ] || { echo "sec_sub: '$a' is not a heading" >&2; return 1; }
    e="^#{1,${d}} "
    awk -v a="$a" -v e="$e" -v old="$3" -v new="$4" '
        $0 == a { f = 1; print; next }
        f && $0 ~ e { f = 0 }
        f {
            out = ""; rest = $0
            while ((p = index(rest, old)) > 0) {
                out = out substr(rest, 1, p - 1) new
                rest = substr(rest, p + length(old))
            }
            $0 = out rest
        }
        { print }
    ' "$f" > "$f.a-extract.tmp" && mv "$f.a-extract.tmp" "$f"
}

# ---------------------------------------------------------------------------- subjects ------
PRISTINE_TAR="$WORK/pristine.tar"

subject() {  # TAG [git-add]  -> prints the subject root
    local tag add d
    tag="$1"; add="${2:-}"; d="$WORK/s-$tag"
    rm -rf "$d"; mkdir -p "$d"
    tar -xf "$PRISTINE_TAR" -C "$d" || return 1
    ( cd "$d" && git init -q . >/dev/null 2>&1 ) || return 1
    if [ "$add" = "add" ]; then ( cd "$d" && git add -A >/dev/null 2>&1 ) || return 1; fi
    printf '%s' "$d"
}

# EVERY CONSUMER INVOCATION IS LOGGED WHEN AN EVIDENCE DIRECTORY IS REQUESTED, keyed by the
# subject directory, which is named for the case. The verdicts below are assertions ON THIS
# OUTPUT; preserving it is what lets a later reader check the assertion rather than trust it.
_log() {  # SUBJECT CONSUMER COMMAND OUTPUT
    [ -n "${A_EXTRACT_EVIDENCE_DIR:-}" ] || return 0
    { printf '\n===== subject=%s consumer=%s\n----- command: %s\n%s\n' \
        "$(basename "$1")" "$2" "$3" "$4"
    } >> "$A_EXTRACT_EVIDENCE_DIR/consumer-output.txt"
}
# THE EXECUTION WITNESS. Every consumer invocation records the sha256 of the file it is ABOUT
# TO RUN, keyed by path, into a witness log. The `Z-<consumer>` controls then require that the
# bytes they compared against the subject's blob are bytes that were actually EXECUTED at least
# once — turning "the file we hashed is the file we ran" from an inference into a measurement.
# This is the strongest property this instrument has and it is kept deliberately.
# WITNESS_LOG is initialised in the isolation block, where WORK exists. It is deliberately NOT
# re-declared here: an earlier draft carried a `WITNESS_LOG=""` placeholder on this line, which
# executed AFTER the real assignment and silently emptied it, so `_witness` returned early and
# every Z control reported "0 execution(s) recorded". The controls caught it — which is the
# behaviour wanted from a control, including against its own author.
_witness() {  # SUBJECT RELPATH
    [ -n "$WITNESS_LOG" ] || return 0
    local h; h="$(shasum -a 256 "$1/$2" 2>/dev/null | awk '{print $1}')"
    [ -n "$h" ] || h="<unreadable>"
    printf '%s\t%s\n' "$2" "$h" >> "$WITNESS_LOG"
}
run_ts() { local o; _witness "$1" scripts/check-type-strings.sh
           o="$( cd "$1" && ./scripts/check-type-strings.sh 2>&1 )"
           _log "$1" TS "./scripts/check-type-strings.sh" "$o"; printf '%s' "$o"; }
run_ec() { local o; _witness "$1" scripts/check-eval-codes.sh
           o="$( cd "$1" && ./scripts/check-eval-codes.sh 2>&1 )"
           _log "$1" EC "./scripts/check-eval-codes.sh" "$o"; printf '%s' "$o"; }
run_vh() { local o; _witness "$1" scripts/check-vendor-honesty.sh
           o="$( cd "$1" && git add -A >/dev/null 2>&1; ./scripts/check-vendor-honesty.sh 2>&1 )"
           _log "$1" VH "./scripts/check-vendor-honesty.sh" "$o"; printf '%s' "$o"; }
run_vp() { local o; _witness "$1" verifier/test_verifier.py
           o="$( cd "$1/verifier" && python3 -m unittest test_verifier.TestPublishedTypeStrings 2>&1 )"
           _log "$1" VP "python3 -m unittest test_verifier.TestPublishedTypeStrings" "$o"; printf '%s' "$o"; }

TS_OK='published in §5.8 match eip712.ts exactly'
EC_OK='engine checks documented in §5.7.1'
VH_OK="the ablation report carries §7.2's caveat verbatim"
VP_OK_RE='^OK$'

# NO `grep -q` ON A PIPE. `printf '%s' "$big" | grep -qF …` exits grep at the first match,
# closing the pipe; `printf` then takes EPIPE and, under `set -o pipefail`, the pipeline returns
# non-zero although the needle WAS found. The sibling gate harness caught this on itself against a
# 60 KB gate log — a control reported FAIL beside a `printf: write error: Broken pipe`. Outputs
# here are small enough that it has never fired, which is exactly why it is worth removing rather
# than leaving as a latent size-dependent falsehood. `grep -c` consumes all of its input.
has()    { printf '%s' "$1" | $GREP -cF -- "$2" >/dev/null; }
has_re() { printf '%s' "$1" | $GREP -cEi -- "$2" >/dev/null; }

# A REFUSAL is: the success line is ABSENT, the finding's SUBJECT is named, and the output
# carries refusal vocabulary from a set of alternatives rather than one dictated sentence.
refuses() {  # OUTPUT SUCCESSLINE SUBJECT REASON_ALTERNATIVES
    local out ok subj why; out="$1"; ok="$2"; subj="$3"; why="$4"
    has "$out" "$ok" && return 1
    has "$out" "$subj" || return 1
    has_re "$out" "$why" || return 1
    return 0
}

DUP_WHY='duplicat|twice|two |more than one|ambigu|cannot choose|refus|conflict'
MISSING_WHY='absent|missing|does not publish|not found|no home|undocumented|not documented'
AMBIG_WHY='ambigu|duplicat|two |more than one|second|cannot choose|conflict'
UNRESOLVED_WHY='could not (isolate|find|locate)|not found|absent|missing|no such section|refus'

# ---------------------------------------------------------------------------- reason classes
# CASE 13 ASSERTS FAILURE IDENTITY, NOT AGREEMENT ON A BOOLEAN.
#
# The first version of this harness compared only "did TS succeed" against "did the verifier
# succeed". Two consumers failing for DIFFERENT reasons counted as agreement, and case
# `13b-after` passed on exactly that — the shell guard refused a duplicate publication while the
# Python consumer silently kept the LAST line and then failed a value comparison. A boolean that
# calls those two the same answer is not measuring agreement.
#
# Each consumer's output is now mapped to a REASON CLASS from one shared vocabulary, and every
# case names the class BOTH consumers must produce. The vocabulary is matched by alternatives,
# so a repair picks its own words; what it may not pick is a different class.
#
#   success               the consumer reports the section read and the values correct
#   anchor-unresolved     the named section could not be located
#   anchor-ambiguous      more than one heading claims the named section
#   duplicate-publication one type is published more than once inside the section
#   not-published         the section does not publish a required value
#   drift                 the published value and the source definition disagree
#   duplicate-definition  the source defines one type more than once
#   crash                 an uncaught exception — an INSTRUMENT FAILURE, never a refusal
#   other                 unclassifiable; always a finding, never a pass

ts_class() {  # OUTPUT -> reason class
    local o; o="$1"
    if has    "$o" "$TS_OK";                                     then printf 'success'; return; fi
    if has_re "$o" 'could not isolate';                          then printf 'anchor-unresolved'; return; fi
    if has_re "$o" 'headings? claim|two sections|duplicate (section|anchor|heading)|ambiguous (section|anchor|heading)'; then printf 'anchor-ambiguous'; return; fi
    if has_re "$o" 'publishes [0-9]+ different lines|duplicate publication'; then printf 'duplicate-publication'; return; fi
    if has_re "$o" 'defines? [a-z0-9_]* ?[0-9]* ?(different )?(times|definitions)|duplicate (source )?definition'; then printf 'duplicate-definition'; return; fi
    if has_re "$o" 'does not publish';                           then printf 'not-published'; return; fi
    if has_re "$o" 'drift in';                                   then printf 'drift'; return; fi
    printf 'other'
}

vp_class() {  # OUTPUT -> reason class
    local o; o="$1"
    if printf '%s' "$o" | $GREP -qE '^OK$';                      then printf 'success'; return; fi
    # A TRACEBACK IS AN INSTRUMENT FAILURE. `unittest` prints `ERROR` for an uncaught exception
    # and `FAIL` for an assertion, and the difference is exactly the difference between a
    # consumer that refused and a consumer that fell over.
    if has_re "$o" 'IndexError|KeyError|TypeError|AttributeError'; then printf 'crash'; return; fi
    if has_re "$o" 'ValueError|RefusalError|SectionError'; then
        if has_re "$o" 'headings? claim|two sections|duplicate (section|anchor|heading)|ambiguous'; then printf 'anchor-ambiguous'; return; fi
        if has_re "$o" 'duplicat|twice|more than one|published .* times'; then printf 'duplicate-publication'; return; fi
        if has_re "$o" 'could not (isolate|find|locate)|not found|absent|missing|no such section'; then printf 'anchor-unresolved'; return; fi
        printf 'other'; return
    fi
    if has_re "$o" 'AssertionError';                             then printf 'assertion-mismatch'; return; fi
    printf 'other'
}

# ============================================================================ preflight ======
hdr "PREFLIGHT"

# THE FIVE IDENTITY FACTS, PRINTED SEPARATELY AND BEFORE ANY MEASUREMENT. A result that does not
# say which harness, which repository, which ref, which commit, and against which historical
# reference is not evidence about anything in particular.
SELF_SHA="$(shasum -a 256 "${BASH_SOURCE[0]}" | awk '{print $1}')"
identity_block() {
    printf '  harness sha256   : %s\n' "$SELF_SHA"
    printf '  repository       : %s\n' "$(sanitize_path "${ROOT:-$ROOT_ARG}")"
    printf '  requested subject: %s\n' "$SUBJECT_OID"
    printf '  resolved subject : %s\n' "${SUBJECT_SHA:-<unresolved>}"
    printf '  pre-repair ref   : %s\n' "$PRE_REPAIR_SHA"
}
check OBSERVED P0 0 "harness sha256 $SELF_SHA"

[ -x "$GREP" ] || die "$GREP is not executable; this harness will not use a PATH-resolved grep"
printf 'a-extract-canary\n' > "$WORK/canary.txt"
[ "$($GREP -c a-extract-canary "$WORK/canary.txt")" = "1" ] || die "the /usr/bin/grep canary did not match"
check OBSERVED P1 0 "/usr/bin/grep is used for every search; canary matched"

GIT_V="$(git --version 2>/dev/null)"; BASH_V="$($GREP -o 'version [0-9.]*' <<<"$(bash --version | head -1)")"
check OBSERVED P2 0 "$GIT_V ; bash ${BASH_V#version } ; $(python3 --version 2>&1)"

[ -n "$ROOT" ] || die "the repository path '$ROOT_ARG' does not exist or is not a directory"
[ -d "$ROOT/.git" ] || die "$(sanitize_path "$ROOT") is not a git repository"

# THERE IS NO SUBJECT RESOLUTION STEP ANY MORE. THAT IS THE POINT.
#
# TWO REVIEWS AND TWO REPAIRS OF THE SAME SEAM. The first repair made the subject an argument;
# the second added two detectors for ambiguous refnames, because
# `git rev-parse --verify <ref>^{commit}` silently prefers a tag over a branch of the same name.
# An independent review then measured the residual (`R1`): the second detector reads git's
# ambiguity WARNING, and `core.warnAmbiguousRefs=false` switches that warning off — after which
# one ambiguity class produced a full green measurement of a commit nobody named.
#
# **JOHN'S RULING, AND IT CLOSES THE SEAM STRUCTURALLY RATHER THAN BY ADDING A THIRD DETECTOR:
# take an EXACT FULL COMMIT OID and nothing else.** A name must be RESOLVED, and resolution is
# the part a tag, a branch, an abbreviation or a configuration setting gets to influence. A full
# object id is not resolved, it is LOOKED UP. Delete the resolution step and there is nothing
# left for a third detector to detect.
#
# **MEASURED, because the whole argument rests on it:** with a branch literally NAMED
# `bb664c626d5…` and pointing at a different commit, `git rev-parse` and `git cat-file -t` both
# still return the OBJECT, not the branch's target — and they do so with
# `core.warnAmbiguousRefs=false` as well. A full oid is not shadowed by a ref of the same name.
# The existence-and-type check below goes further and performs NO NAME RESOLUTION AT ALL.

# --- the grammar, enforced before any git touches the subject -----------------
case "$SUBJECT_OID" in
    -*) die "subject '$SUBJECT_OID' is option-shaped. The subject must be a bare 40-hex commit id." ;;
esac
if ! printf '%s' "$SUBJECT_OID" | $GREP -qE '^[0-9a-f]{40}$'; then
    # The diagnosis is ordered most-specific first, and "uppercase hex" is only claimed when the
    # string really is 40 hex characters in the wrong case — otherwise `HEAD` gets reported as
    # uppercase hex, which is true of its letters and false about what the caller did wrong.
    _why="not a 40-character lowercase hex object id (length ${#SUBJECT_OID}, need exactly 40)"
    case "$SUBJECT_OID" in
        refs/*)        _why="a fully qualified ref; refs are not accepted, only object ids" ;;
        *[~^:@]*|*..*) _why="a revision expression; expressions are not accepted, only object ids" ;;
        *)
            if printf '%s' "$SUBJECT_OID" | $GREP -qE '^[0-9a-fA-F]{40}$'; then
                _why="uppercase hex — git's canonical form is lowercase"
            elif printf '%s' "$SUBJECT_OID" | $GREP -qE '^[0-9a-f]+$'; then
                _why="an ABBREVIATED object id (length ${#SUBJECT_OID}, need exactly 40)"
            else
                _why="a NAME, not an object id — branches, tags and HEAD are not accepted"
            fi ;;
    esac
    die "subject '$SUBJECT_OID' is $_why.
                     This instrument accepts ONE input shape: ^[0-9a-f]{40}\$ naming a commit.
                     Branches, tags, HEAD, refs/…, revision expressions and abbreviated ids are
                     all REFUSED — not because a detector fired, but because names are not
                     accepted at all. Run: git rev-parse --verify <your-ref>^{commit} yourself,
                     then pass the 40-hex result."
fi

# --- existence and type, WITHOUT resolving a name -----------------------------
# `--batch-all-objects` enumerates the object database and performs no name lookup whatsoever,
# so nothing a ref, an abbreviation or a configuration setting can do reaches this check. It is
# the difference between "git told me what this name means" and "this object is present, and it
# is a commit".
_odb_type="$( cd "$ROOT" && git cat-file --batch-all-objects --batch-check='%(objectname) %(objecttype)' 2>/dev/null \
              | $GREP -m1 -E "^${SUBJECT_OID} " | awk '{print $2}' )"
if [ -z "$_odb_type" ]; then
    die "object $SUBJECT_OID is not present in $(sanitize_path "$ROOT")'s object database."
fi
if [ "$_odb_type" != "commit" ]; then
    die "object $SUBJECT_OID exists in $(sanitize_path "$ROOT") but is a '$_odb_type', not a commit."
fi

# The subject IS the argument. Nothing was resolved, so nothing can have been resolved wrongly.
SUBJECT_SHA="$SUBJECT_OID"

# THE SNAPSHOT IS BUILT FROM THE SUBJECT, NEVER FROM THE HISTORICAL BASE.
( cd "$ROOT" && git archive --format=tar "$SUBJECT_SHA" ) > "$PRISTINE_TAR" 2>/dev/null \
    || die "cannot build a snapshot of $SUBJECT_SHA"
[ -s "$PRISTINE_TAR" ] || die "the snapshot of $SUBJECT_SHA is empty"

P0="$(subject p0 add)" || die "cannot build the pristine subject"
for f in "$PROP_REL" "$SRC_REL" "$RPT_REL" scripts/check-type-strings.sh \
         scripts/check-eval-codes.sh scripts/check-vendor-honesty.sh verifier/test_verifier.py; do
    [ -f "$P0/$f" ] || die "the snapshot is missing $f"
done
check OBSERVED P4 0 "snapshot of SUBJECT_SHA $SUBJECT_SHA built; four consumers present"

# P3-provenance — A SUBJECT-PROVENANCE CONSISTENCY CONTROL. NOT AN INDEPENDENCE PROOF.
#
# **RENAMED AND REDESCRIBED ON JOHN'S RULING, accepting `R2` from the second independent review
# as a documented limitation.** Its predecessor claimed the subject was confirmed "by TWO
# INDEPENDENT ROUTES". That claim is withdrawn: `rev-parse`, `show-ref`, `cat-file` and
# `git archive` are all git, and for a subject naming no ref the two routes shared git's object
# resolver outright. **Commands that share a resolver are not independent of each other, and
# this control no longer says they are.**
#
# What it does establish, and this is the whole of it — a CONSISTENCY CHAIN, each link measured:
#   (a) the string supplied is an exact full 40-hex object id — no name was resolved;
#   (b) that exact object is present in the object database with type `commit`, established by
#       enumeration rather than by name lookup;
#   (c) the archived tree was produced from THAT oid — checked here against a sentinel blob read
#       back out of the same commit;
#   (d) the consumers actually EXECUTED carry that commit's bytes — asserted separately by the
#       four `Z-<consumer>` controls, which now require a recorded execution, not just a match;
#   (e) the source repository is unchanged by the run — asserted separately by `Z-clean`.
#
# It can fail: a mismatched sentinel blob, an absent object, a non-commit, or a subject that is
# not an exact oid all make it fail — and (a) and (b) are re-asserted here rather than assumed
# from the earlier `die`, so that a future edit removing a refusal cannot leave this silent.
# THE PROVENANCE CHECK IS OVER THE WHOLE TREE, NOT ONE FILE.
#
# It compared ONE sentinel blob. An independent review established that **21 commits already in
# this repository carry an identical `scripts/check-type-strings.sh` blob with a DIFFERENT
# tree** — measured here, not taken on trust — so every one of them would have satisfied it. A
# one-blob sentinel cannot establish that the archived tree is the subject's tree, and that is
# true independently of the replacement hole above.
#
# Both sides are reduced to one digest over `path<TAB>blob-oid` for every blob:
#   expected — `git ls-tree -r --full-tree <oid>`, filtered to blobs (gitlinks are not archived);
#   actual   — every regular file in the snapshot, hashed with `git hash-object --stdin-paths`.
# The path list is compared too, so an EXTRA file in the snapshot moves the digest as surely as
# a changed one. 498 paths at the pre-repair commit; a one-line edit to any of them moves it.
# THE EXPECTED SIDE IS PINNED WITH `--no-replace-objects` ON THE COMMAND, NOT LEFT TO THE
# ENVIRONMENT. Without this the control is self-consistent under replacement and passes: the
# paired control measured exactly that — with the scrub removed, BOTH sides moved together to the
# replaced commit's tree (529 paths, digest d8fa9431…) and the control reported PASS. Pinning the
# expected side means the control itself detects the hole rather than relying on the scrub.
_tree_expected="$( cd "$ROOT" && git --no-replace-objects ls-tree -r --full-tree "$SUBJECT_SHA" 2>/dev/null \
                   | awk '$2=="blob"{print $4"\t"$3}' | LC_ALL=C sort | shasum -a 256 | awk '{print $1}' )"
_tree_paths="$WORK/.tree-paths"; _tree_hashes="$WORK/.tree-hashes"
_tree_actual="$( cd "$P0" 2>/dev/null && \
                 find . -type f -not -path './.git/*' | sed 's|^\./||' | LC_ALL=C sort > "$_tree_paths" && \
                 git hash-object --stdin-paths < "$_tree_paths" > "$_tree_hashes" 2>/dev/null && \
                 paste "$_tree_paths" "$_tree_hashes" | shasum -a 256 | awk '{print $1}' )"
_tree_n="$($GREP -c . "$_tree_paths" 2>/dev/null || echo 0)"
check CONTROL P3-provenance "$( printf '%s' "$SUBJECT_OID" | $GREP -qE '^[0-9a-f]{40}$' && \
      [ "$_odb_type" = "commit" ] && [ -n "$_tree_expected" ] && [ -n "$_tree_actual" ] && \
      [ "$_tree_expected" = "$_tree_actual" ] && echo 0 || echo 1 )" \
      "subject provenance is CONSISTENT (not independent): '$SUBJECT_OID' is an exact 40-hex oid of odb type '${_odb_type:-<none>}', and the archived tree matches that commit's tree over all ${_tree_n} blob paths (${_tree_actual:0:12}…)"

for h in "$H58" "$H59" "$H56" "$H571" "$H6" "$H72"; do
    n="$($GREP -c -x -F -- "$h" "$P0/$PROP_REL")"
    [ "$n" = "1" ] || die "anchor is not unique in the proposal ($n occurrences): $h"
done
check OBSERVED P5 0 "all six anchor headings occur exactly once in the base proposal"

command -v python3 >/dev/null 2>&1 || die "python3 is required for the §5.8 verifier consumer"
_p0ts="$(run_ts "$P0")"; _p0ec="$(run_ec "$P0")"; _p0vp="$(run_vp "$P0")"
has "$_p0ts" "$TS_OK" || die "the base subject does not pass check-type-strings.sh: $_p0ts"
has "$_p0ec" "$EC_OK" || die "the base subject does not pass check-eval-codes.sh: $_p0ec"
has_re "$_p0vp" "$VP_OK_RE" || die "the base subject does not pass the verifier §5.8 consumer"
check OBSERVED P6 0 "the unmutated snapshot passes TS, EC and the verifier §5.8 consumer"

# P7 — THE GENERATOR SUBJECT. Case 11f runs the real ablation generator, which imports `viem`
# transitively, so it needs an installed `ts/node_modules`. The dependency tree is COPIED into a
# private subject rather than symlinked, so nothing the generator does can reach the repository
# under test. If node or the dependency tree is absent this DIES rather than skipping: the
# gate's own words for this stage are "a check that cannot execute must never read as a check
# that passed", and a silent skip beside a green line is this project's recorded defect class.
command -v node >/dev/null 2>&1 || die "node is required to execute the canonical ablation generator (case 11f)"
[ -d "$ROOT/ts/node_modules" ] || die "ts/node_modules is absent; the canonical generator cannot run (case 11f). Run 'npm --prefix ts install' first."
GEN="$(subject gen)" || die "cannot build the generator subject"
cp -R "$ROOT/ts/node_modules" "$GEN/ts/node_modules" || die "cannot stage the generator's dependency tree"
check OBSERVED P7 0 "generator subject built with a private copy of ts/node_modules ($(node --version))"

# P8 — §5.7.1's IDENTIFIERS ARE DECLARED NON-NORMATIVE, WHICH IS WHY EC HAS NO
# DUPLICATE-PUBLICATION CASE.
#
# The question was asked before the case was omitted rather than after. `§5.7.1`'s own heading
# reads "the identifiers are not normative", and its body says a reimplementer "should derive
# behaviour from the descriptions, not transcribe names". A section that does not publish
# normatively cannot publish twice normatively, so requiring uniqueness there would be
# manufacturing an obligation the document declines to take on — and D-058(6) forbids exactly
# that shape of invention. The determination is ASSERTED rather than asserted-once-and-forgotten:
# if §5.7.1 ever becomes normative this control fails and the omission is revisited.
#
# The exact-token cases (2a superstring, 12suffix, 12prefix) are retained either way; they are
# about membership, which §5.7.1 does assert, and not about uniqueness.
check CONTROL  P8 "$(has "$H571" "the identifiers are not normative" && \
      $GREP -q 'not.*normative' <<< "$(section_of "$P0/$PROP_REL" "$H571" | head -20)" && echo 0 || echo 1)" \
      "§5.7.1 still declares its identifiers NON-NORMATIVE — the basis for omitting a duplicate-publication case at EC"

# ============================================================================ case 1 =========
hdr "CASE 1 — the named section is ABSENT"
say "Required: refuse, naming the section. A checker may not report a result for a scope it"
say "could not find, and may not fall back to the whole document."

S="$(subject c1)"; edit_at "$S/$PROP_REL" delete "$H58" ""
n_after="$($GREP -c -x -F -- "$H58" "$S/$PROP_REL")"
n_before="$($GREP -c -x -F -- "$H58" "$P0/$PROP_REL")"
check CONTROL  1-mut "$([ "$n_before" = 1 ] && [ "$n_after" = 0 ] && echo 0 || echo 1)" \
      "mutation applied: the §5.8 heading is present once in the base and absent in the fixture"
o="$(run_ts "$S")"
check REQUIRED 1a "$(refuses "$o" "$TS_OK" "5.8" 'could not (isolate|find)|refus|cannot' && echo 0 || echo 1)" \
      "TS refuses when §5.8 is absent, naming the section"
# 1c REQUIRES A NAMED DIAGNOSTIC, NOT MERELY THE ABSENCE OF SUCCESS.
#
# The first version asserted only "does not report success", which an UNCAUGHT `IndexError`
# satisfies. A crash is an instrument failure, not a refusal: it carries no statement about
# §5.8, it is not stable across inputs, and a consumer that falls over is indistinguishable
# from one that was never reached. The assertion is now three-part — no traceback, a
# diagnostic that NAMES the section, and not success — so a crash FAILS it.
o="$(run_vp "$S")"
vpc="$(vp_class "$o")"
named="$(has "$o" "5.8" && echo yes || echo no)"
check REQUIRED 1c "$([ "$vpc" = "anchor-unresolved" ] && [ "$named" = yes ] && echo 0 || echo 1)" \
      "the verifier §5.8 consumer emits a NAMED anchor-unresolved diagnostic (class=$vpc, names §5.8=$named)"
check OBSERVED 1c-how 0 "verifier failure shape at this commit: $(printf '%s' "$o" | $GREP -oE '(IndexError|KeyError|ValueError|AssertionError)' | head -1 | sed 's/^$/none/')"
_p0vpc="$(vp_class "$_p0vp")"
check CONTROL  1c-ctl "$([ "$_p0vpc" = "success" ] && ! has "$_p0vp" "5.8 " && echo 0 || echo 1)" \
      "paired control: on VALID input the same consumer reports success and emits no diagnostic (class=$_p0vpc)"

S="$(subject c1b)"; edit_at "$S/$PROP_REL" delete "$H571" ""
check CONTROL  1b-mut "$([ "$($GREP -c -x -F -- "$H571" "$S/$PROP_REL")" = 0 ] && echo 0 || echo 1)" \
      "mutation applied: the §5.7.1 heading is absent from the fixture"
o="$(run_ec "$S")"
check REQUIRED 1b "$(refuses "$o" "$EC_OK" "5.7.1" 'could not (isolate|find)|refus|cannot' && echo 0 || echo 1)" \
      "EC refuses when §5.7.1 is absent, naming the section"

check CONTROL  1-ctl "$(has "$_p0ts" "$TS_OK" && has "$_p0ec" "$EC_OK" && echo 0 || echo 1)" \
      "opposite outcome: with the sections present both checkers report success"

# ============================================================================ case 2 =========
hdr "CASE 2 — the exact value is ABSENT but a value sharing its prefix is present"
say "Required: exact membership. A token of which the required value is a proper prefix is a"
say "DIFFERENT token and must not satisfy the requirement."

S="$(subject c2)"
sec_sub "$S/$PROP_REL" "$H571" 'EVAL_POLICY_WINDOW' 'EVAL_POLICY_WINDOW_STRICT'
body="$(section_of "$S/$PROP_REL" "$H571")"
exact="$(printf '%s' "$body" | $GREP -cE '\bEVAL_POLICY_WINDOW\b')"
supers="$(printf '%s' "$body" | $GREP -c 'EVAL_POLICY_WINDOW_STRICT')"
check CONTROL  2-mut "$([ "$exact" = 0 ] && [ "$supers" -ge 1 ] && echo 0 || echo 1)" \
      "mutation applied: §5.7.1 carries EVAL_POLICY_WINDOW_STRICT and no exact EVAL_POLICY_WINDOW"
o="$(run_ec "$S")"
check REQUIRED 2a "$(refuses "$o" "$EC_OK" "EVAL_POLICY_WINDOW" "$MISSING_WHY" && echo 0 || echo 1)" \
      "EC reports EVAL_POLICY_WINDOW absent although a superstring of it is documented"

S="$(subject c2b)"
sec_sub "$S/$PROP_REL" "$H58" 'PolicyPayload(' 'PolicyPayloadV2('
body="$(section_of "$S/$PROP_REL" "$H58")"
check CONTROL  2b-mut "$([ "$(printf '%s' "$body" | $GREP -cE '^ {4}PolicyPayload\(')" = 0 ] && \
      [ "$(printf '%s' "$body" | $GREP -cE '^ {4}PolicyPayloadV2\(')" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: §5.8 publishes PolicyPayloadV2 and no exact PolicyPayload"
o="$(run_ts "$S")"
check REQUIRED 2b "$(refuses "$o" "$TS_OK" "PolicyPayload" "$MISSING_WHY" && echo 0 || echo 1)" \
      "TS reports PolicyPayload not published although PolicyPayloadV2 is"

S="$(subject c2c)"
sec_sub "$S/$PROP_REL" "$H571" 'EVAL_POLICY_WINDOW' 'EVAL_UNRELATED_TOKEN'
o="$(run_ec "$S")"
check CONTROL  2-ctl "$(refuses "$o" "$EC_OK" "EVAL_POLICY_WINDOW" "$MISSING_WHY" && echo 0 || echo 1)" \
      "paired control: with the token wholly removed EC does name it missing, so the path is live"

# ============================================================================ case 3 =========
hdr "CASE 3 — the value is present ONLY OUTSIDE the named section"
say "Required: a value published elsewhere in the document does not satisfy a claim about"
say "this section, in either direction of the file."

S="$(subject c3)"
CODE_LINE="$(section_of "$S/$PROP_REL" "$H571" | $GREP -F 'EVAL_VAULT_NOT_PAUSED' | head -1)"
sec_sub "$S/$PROP_REL" "$H571" 'EVAL_VAULT_NOT_PAUSED' 'EVAL_MOVED_AWAY'
edit_at "$S/$PROP_REL" after "$H6" "Relocated for this probe: \`EVAL_VAULT_NOT_PAUSED\`."
inside="$(section_of "$S/$PROP_REL" "$H571" | $GREP -c 'EVAL_VAULT_NOT_PAUSED')"
whole="$($GREP -c 'EVAL_VAULT_NOT_PAUSED' "$S/$PROP_REL")"
check CONTROL  3-mut "$([ "$inside" = 0 ] && [ "$whole" -ge 1 ] && echo 0 || echo 1)" \
      "mutation applied: EVAL_VAULT_NOT_PAUSED is outside §5.7.1 and inside the document"
o="$(run_ec "$S")"
check REQUIRED 3a "$(refuses "$o" "$EC_OK" "EVAL_VAULT_NOT_PAUSED" "$MISSING_WHY" && echo 0 || echo 1)" \
      "EC reports the code absent from §5.7.1 although the document carries it elsewhere"

S="$(subject c3b)"
OV="$(section_of "$S/$PROP_REL" "$H58" | $GREP -E '^ {4}OverrideAuthorizationPayload\(' | head -1)"
[ -n "$OV" ] || die "cannot read the OverrideAuthorizationPayload publication from §5.8"
edit_at "$S/$PROP_REL" delete "$OV" ""
edit_at "$S/$PROP_REL" after "$H56" ""
edit_at "$S/$PROP_REL" after "$H56" "$OV"
inside="$(section_of "$S/$PROP_REL" "$H58" | $GREP -cE '^ {4}OverrideAuthorizationPayload\(')"
outside="$(section_of "$S/$PROP_REL" "$H56" | $GREP -cE '^ {4}OverrideAuthorizationPayload\(')"
check CONTROL  3b-mut "$([ "$inside" = 0 ] && [ "$outside" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: the publication moved out of §5.8 and into §5.6"
o="$(run_ts "$S")"
check REQUIRED 3b "$(refuses "$o" "$TS_OK" "OverrideAuthorizationPayload" "$MISSING_WHY" && echo 0 || echo 1)" \
      "TS reports the type string not published in §5.8 although §5.6 publishes it"

# ============================================================================ case 4 =========
hdr "CASE 4 — an outside-section DECOY placed BEFORE the real section"
say "Required: refusal, not a first-match tie-break. Section order in this document is NOT"
say "monotonic — §5.9 precedes §5.8 — so 'the first match' is not 'the real one'."

S="$(subject c4a)"
AP="$(section_of "$S/$PROP_REL" "$H58" | $GREP -E '^ {4}ActionPayload\(' | head -1)"
[ -n "$AP" ] || die "cannot read the ActionPayload publication from §5.8"
AP_BAD="$(printf '%s' "$AP" | sed 's/bytes32 mandateHash,bytes32 policyHash/bytes32 policyHash,bytes32 mandateHash/')"
[ "$AP_BAD" != "$AP" ] || die "the ActionPayload transposition did not change the line"
edit_at "$S/$PROP_REL" replace "$AP" "$AP_BAD"
edit_at "$S/$PROP_REL" after "$H59" ""
edit_at "$S/$PROP_REL" after "$H59" "$AP"
check CONTROL  4a-mut "$([ "$(section_of "$S/$PROP_REL" "$H59" | $GREP -cF "$AP")" = 1 ] && \
      [ "$(section_of "$S/$PROP_REL" "$H58" | $GREP -cF "$AP_BAD")" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: the correct line sits in §5.9 (earlier) and §5.8 carries the transposed one"
o="$(run_ts "$S")"
check REQUIRED 4a "$(refuses "$o" "$TS_OK" "ActionPayload" 'drift|differ|mismatch|does not match|disagree' && echo 0 || echo 1)" \
      "TS reads §5.8 itself and reports drift, ignoring the earlier correct decoy"

# 4c and 4d PLANT A COMPLETE DECOY SECTION, not a bare heading. A decoy heading with an
# empty body makes the guard refuse for the WRONG reason — its empty-scope check fires and
# the case reports PASS while proving nothing about first-match selection. The decoy body
# below is a VERBATIM COPY of the real section, so a first-match reader sees a section that
# looks entirely correct.
plant_decoy_section() {  # SUBJECT ANCHORLINE BEFORELINE  — copies the real section up front
    local s anchor before body
    s="$1"; anchor="$2"; before="$3"
    body="$WORK/.decoy-body"
    { printf '%s\n\n' "$anchor"
      section_of "$s/$PROP_REL" "$anchor"
      printf '\n---\n\n'
    } > "$body"
    edit_at_file "$s/$PROP_REL" before "$before" "$body"
    rm -f "$body"
}

S="$(subject c4c)"
D58="$(section_of "$S/$PROP_REL" "$H58" | $GREP -E '^ {4}EIP712Domain\(' | head -1)"
plant_decoy_section "$S" "$H58" "$H59"
n58="$($GREP -c -x -F -- "$H58" "$S/$PROP_REL")"
n_dom="$($GREP -cF "$D58" "$S/$PROP_REL")"
check CONTROL  4c-mut "$([ "$n58" = 2 ] && [ "$n_dom" = 2 ] && echo 0 || echo 1)" \
      "mutation applied: TWO complete §5.8 sections with identical bodies, the decoy first"
o="$(run_ts "$S")"
check REQUIRED 4c "$(refuses "$o" "$TS_OK" "5.8" "$DUP_WHY" && echo 0 || echo 1)" \
      "TS refuses when two headings claim the §5.8 anchor, rather than taking the first"

S="$(subject c4d)"
plant_decoy_section "$S" "$H58" "$H59"
AP_REAL="$(awk -v a="$H58" 'n==2 && $0 ~ /^ {4}ActionPayload\(/ {print; exit} $0==a{n++}' "$S/$PROP_REL")"
[ -n "$AP_REAL" ] || die "cannot read the ActionPayload publication from the second §5.8"
AP_BAD="$(printf '%s' "$AP_REAL" | sed 's/bytes32 mandateHash,bytes32 policyHash/bytes32 policyHash,bytes32 mandateHash/')"
awk -v a="$H58" -v old="$AP_REAL" -v new="$AP_BAD" '
    $0==a{n++} { if (n==2 && $0==old) { print new; next } print }' "$S/$PROP_REL" > "$S/$PROP_REL.t" \
    && mv "$S/$PROP_REL.t" "$S/$PROP_REL"
n58="$($GREP -c -x -F -- "$H58" "$S/$PROP_REL")"
first_ap="$(section_of "$S/$PROP_REL" "$H58" | $GREP -cF "$AP_REAL")"
bad_n="$($GREP -cF "$AP_BAD" "$S/$PROP_REL")"
check CONTROL  4d-mut "$([ "$n58" = 2 ] && [ "$first_ap" = 1 ] && [ "$bad_n" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: the FIRST §5.8 carries the correct ActionPayload, the REAL one the transposed"
o="$(run_ts "$S")"
check REQUIRED 4d "$(has "$o" "$TS_OK" && echo 1 || echo 0)" \
      "TS does NOT report success when an earlier duplicate §5.8 anchor hides a real drift"

S="$(subject c4b)"
plant_decoy_section "$S" "$H571" "$H59"
awk -v a="$H571" '$0==a{n++} { if (n==2) { gsub(/EVAL_TARGET_BOUND/, "EVAL_REMOVED_HERE") } print }' \
    "$S/$PROP_REL" > "$S/$PROP_REL.t" && mv "$S/$PROP_REL.t" "$S/$PROP_REL"
n571="$($GREP -c -x -F -- "$H571" "$S/$PROP_REL")"
first_has="$(section_of "$S/$PROP_REL" "$H571" | $GREP -c 'EVAL_TARGET_BOUND')"
total_has="$($GREP -c 'EVAL_TARGET_BOUND' "$S/$PROP_REL")"
check CONTROL  4b-mut "$([ "$n571" = 2 ] && [ "$first_has" -ge 1 ] && [ "$total_has" = "$first_has" ] && echo 0 || echo 1)" \
      "mutation applied: TWO complete §5.7.1 sections; only the DECOY documents EVAL_TARGET_BOUND"
o="$(run_ec "$S")"
check REQUIRED 4b "$(has "$o" "$EC_OK" && echo 1 || echo 0)" \
      "EC does NOT report full coverage when an earlier duplicate §5.7.1 anchor supplies the codes"

# --- 4e / 4f: A QUOTED HEADING IS A MENTION, NOT AN ANCHOR --------------------
#
# The exact-anchor requirement has a second half. It is not enough that a duplicate heading be
# refused; a heading QUOTED inside a fenced code block is not a heading at all, and must not be
# selected as the anchor. `check-vendor-honesty.sh` already carries this exact defeat in its own
# §2 block, recorded there by an independent review on 2026-08-16: the real certification line
# was deleted from §2 and the string planted inside a code block in §14, introduced as "a format
# we considered and rejected", and the guard reported certified. The same fixture is planted
# here against the section anchors.
# THE FENCE CHARACTER IS A PARAMETER, AND EXACTLY TWO VALUES ARE USED.
#
# CommonMark gives a fenced code block two spellings — three or more BACKTICKS, or three or more
# TILDES — and they are equally ordinary. A guard that learned to ignore ``` and not ~~~ would
# have generalised the DEMONSTRATION instead of the ARGUMENT, which is this project's most
# repeated repair defect (A-081(2)). So each fence character gets its OWN case and its OWN
# proof-of-mutation control, rather than one case with a loop nobody can point at.
#
# **DELIBERATELY NOT GENERALISED FURTHER.** Indented code blocks, HTML blocks, blockquoted
# headings and info-string variants are NOT probed. Two fence characters is the whole addition.
plant_quoted_anchor() {  # SUBJECT ANCHORLINE BODYLINE BEFORELINE [FENCE]
    local s anchor body before fence blk
    s="$1"; anchor="$2"; body="$3"; before="$4"; fence="${5:-\`\`\`}"
    case "$fence" in
        '```'|'~~~') : ;;
        *) echo "plant_quoted_anchor: unsupported fence '$fence'" >&2; return 1 ;;
    esac
    blk="$WORK/.quoted-anchor"
    { printf 'A heading format considered and rejected in 2026-08-14, quoted here so the\n'
      printf 'reasoning survives rather than being lost:\n\n'
      printf '%smarkdown\n%s\n\n%s\n%s\n\n' "$fence" "$anchor" "$body" "$fence"
    } > "$blk"
    edit_at_file "$s/$PROP_REL" before "$before" "$blk"
    rm -f "$blk"
}

S="$(subject c4e)"
D58="$(section_of "$S/$PROP_REL" "$H58" | $GREP -E '^ {4}EIP712Domain\(' | head -1)"
D58_BAD="$(printf '%s' "$D58" | sed 's/string name,string version/string version,string name/')"
plant_quoted_anchor "$S" "$H58" "$D58_BAD" "$H59"
fence="$($GREP -c -x -F '```markdown' "$S/$PROP_REL")"
real_intact="$(section_of "$P0/$PROP_REL" "$H58" | $GREP -cF "$D58")"
check CONTROL  4e-btick-mut "$([ "$fence" = 1 ] && [ "$($GREP -c -x -F -- "$H58" "$S/$PROP_REL")" = 2 ] && [ "$real_intact" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: the §5.8 heading is quoted inside a BACKTICK fence earlier in the file; the real §5.8 is untouched"
o="$(run_ts "$S")"
check REQUIRED 4e-btick "$(has "$o" "$TS_OK" && echo 0 || echo 1)" \
      "TS ignores a §5.8 heading quoted inside a BACKTICK fence and reads the real section"

S="$(subject c4e-tilde)"
D58="$(section_of "$S/$PROP_REL" "$H58" | $GREP -E '^ {4}EIP712Domain\(' | head -1)"
D58_BAD="$(printf '%s' "$D58" | sed 's/string name,string version/string version,string name/')"
plant_quoted_anchor "$S" "$H58" "$D58_BAD" "$H59" '~~~'
fence="$($GREP -c -x -F '~~~markdown' "$S/$PROP_REL")"
real_intact="$(section_of "$P0/$PROP_REL" "$H58" | $GREP -cF "$D58")"
check CONTROL  4e-tilde-mut "$([ "$fence" = 1 ] && [ "$($GREP -c -x -F '```markdown' "$S/$PROP_REL")" = 0 ] && \
      [ "$($GREP -c -x -F -- "$H58" "$S/$PROP_REL")" = 2 ] && [ "$real_intact" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: the §5.8 heading is quoted inside a TILDE fence (and no backtick fence) earlier in the file"
o="$(run_ts "$S")"
check REQUIRED 4e-tilde "$(has "$o" "$TS_OK" && echo 0 || echo 1)" \
      "TS ignores a §5.8 heading quoted inside a TILDE fence and reads the real section"

S="$(subject c4f)"
plant_quoted_anchor "$S" "$H571" '`EVAL_CHAIN_BOUND` only, in a format that was rejected.' "$H59"
check CONTROL  4f-btick-mut "$([ "$($GREP -c -x -F -- "$H571" "$S/$PROP_REL")" = 2 ] && \
      [ "$($GREP -c -x -F '```markdown' "$S/$PROP_REL")" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: the §5.7.1 heading is quoted inside a BACKTICK fence earlier in the file"
o="$(run_ec "$S")"
check REQUIRED 4f-btick "$(has "$o" "$EC_OK" && echo 0 || echo 1)" \
      "EC ignores a §5.7.1 heading quoted inside a BACKTICK fence and reads the real section"

S="$(subject c4f-tilde)"
plant_quoted_anchor "$S" "$H571" '`EVAL_CHAIN_BOUND` only, in a format that was rejected.' "$H59" '~~~'
check CONTROL  4f-tilde-mut "$([ "$($GREP -c -x -F -- "$H571" "$S/$PROP_REL")" = 2 ] && \
      [ "$($GREP -c -x -F '~~~markdown' "$S/$PROP_REL")" = 1 ] && \
      [ "$($GREP -c -x -F '```markdown' "$S/$PROP_REL")" = 0 ] && echo 0 || echo 1)" \
      "mutation applied: the §5.7.1 heading is quoted inside a TILDE fence (and no backtick fence) earlier in the file"
o="$(run_ec "$S")"
check REQUIRED 4f-tilde "$(has "$o" "$EC_OK" && echo 0 || echo 1)" \
      "EC ignores a §5.7.1 heading quoted inside a TILDE fence and reads the real section"

# ============================================================================ case 5 =========
hdr "CASE 5 — DUPLICATE normative publication inside the section, in BOTH orders"
say "Required: refuse. A section that publishes two different strings for one type has no"
say "correct answer to choose between, so choosing is the defect."

for order in before after; do
    S="$(subject "c5$order")"
    AP="$(section_of "$S/$PROP_REL" "$H58" | $GREP -E '^ {4}ActionPayload\(' | head -1)"
    AP_BAD="$(printf '%s' "$AP" | sed 's/bytes32 mandateHash,bytes32 policyHash/bytes32 policyHash,bytes32 mandateHash/')"
    edit_at "$S/$PROP_REL" "$order" "$AP" ""
    edit_at "$S/$PROP_REL" "$order" "$AP" "$AP_BAD"
    n="$(section_of "$S/$PROP_REL" "$H58" | $GREP -cE '^ {4}ActionPayload\(')"
    check CONTROL  "5$order-mut" "$([ "$n" = 2 ] && echo 0 || echo 1)" \
          "mutation applied: §5.8 publishes ActionPayload twice (decoy $order the real line)"
    o="$(run_ts "$S")"
    check REQUIRED "5$order" "$(refuses "$o" "$TS_OK" "ActionPayload" "$DUP_WHY" && echo 0 || echo 1)" \
          "TS refuses the duplicate publication with the decoy $order the real line"
done
check CONTROL  5-ctl "$(has "$_p0ts" "$TS_OK" && echo 0 || echo 1)" \
      "paired control: with one publication per type TS reports success"

# ============================================================================ case 6 =========
hdr "CASE 6 — DUPLICATE authoritative definition in the SOURCE, in BOTH orders"
say "D-059(8)(b): source uniqueness is a SECOND property, not the Markdown one. Required:"
say "refuse and name the duplicate definition — not report drift, and not report success."

SRC_ANCHOR_BEFORE="export const MANDATE_TYPE ="
SRC_ANCHOR_AFTER="export const EIP712_DOMAIN_TYPEHASH = keccak256(stringToBytes(EIP712_DOMAIN_TYPE));"
for order in before after; do
    S="$(subject "c6$order")"
    REALDEF="$($GREP -oE '"MandatePayload\([^"]*\)"' "$S/$SRC_REL" | head -1)"
    [ -n "$REALDEF" ] || die "cannot read the MandatePayload definition from $SRC_REL"
    DECOYDEF="$(printf '%s' "$REALDEF" | sed 's/address principal,address vault/address vault,address principal/')"
    [ "$DECOYDEF" != "$REALDEF" ] || die "the source transposition did not change the definition"
    if [ "$order" = before ]; then
        edit_at "$S/$SRC_REL" before "$SRC_ANCHOR_BEFORE" ""
        edit_at "$S/$SRC_REL" before "$SRC_ANCHOR_BEFORE" "const _decoyMandateType = $DECOYDEF;"
    else
        edit_at "$S/$SRC_REL" after "$SRC_ANCHOR_AFTER" "const _decoyMandateType = $DECOYDEF;"
        edit_at "$S/$SRC_REL" after "$SRC_ANCHOR_AFTER" ""
    fi
    n="$($GREP -cE '"MandatePayload\(' "$S/$SRC_REL")"
    real_ln="$($GREP -nF "$REALDEF" "$S/$SRC_REL" | head -1 | cut -d: -f1)"
    decoy_ln="$($GREP -nF "$DECOYDEF" "$S/$SRC_REL" | head -1 | cut -d: -f1)"
    if [ "$order" = before ]; then ord_ok="$([ "$decoy_ln" -lt "$real_ln" ] && echo 0 || echo 1)"
    else ord_ok="$([ "$decoy_ln" -gt "$real_ln" ] && echo 0 || echo 1)"; fi
    check CONTROL  "6$order-mut" "$([ "$n" = 2 ] && [ "$ord_ok" = 0 ] && echo 0 || echo 1)" \
          "mutation applied: two MandatePayload definitions in the source, decoy $order the real one (lines $decoy_ln/$real_ln)"
    o="$(run_ts "$S")"
    check REQUIRED "6$order" "$(refuses "$o" "$TS_OK" "MandatePayload" "$DUP_WHY" && echo 0 || echo 1)" \
          "TS refuses the duplicate SOURCE definition with the decoy $order the real one"
done
check CONTROL  6-ctl "$([ "$($GREP -cE '"MandatePayload\(' "$P0/$SRC_REL")" = 1 ] && has "$_p0ts" "$TS_OK" && echo 0 || echo 1)" \
      "paired control: the base source defines MandatePayload exactly once and TS reports success"

# ============================================================================ case 7 =========
hdr "CASE 7 — a DEEPER subsection remains INSIDE its parent section"
say "D-059(8)(a): a §5.8.1 subsection must not truncate §5.8. Depth is relative to the ANCHOR."

S="$(subject c7a)"
DOM="$(section_of "$S/$PROP_REL" "$H58" | $GREP -E '^ {4}EIP712Domain\(' | head -1)"
edit_at "$S/$PROP_REL" after "$DOM" ""
edit_at "$S/$PROP_REL" after "$DOM" "#### 5.8.1 Domain field values"
below="$(awk -v a='#### 5.8.1 Domain field values' '$0==a{f=1;next} f && /^### /{exit} f' "$S/$PROP_REL" | $GREP -cE '^ {4}[A-Za-z]+Payload\(')"
check CONTROL  7a-mut "$([ "$($GREP -c -x -F '#### 5.8.1 Domain field values' "$S/$PROP_REL")" = 1 ] && \
      [ "$below" = 5 ] && echo 0 || echo 1)" \
      "mutation applied: a #### subsection sits inside §5.8 with 5 publications below it"
o="$(run_ts "$S")"
check REQUIRED 7a "$(has "$o" "$TS_OK" && echo 0 || echo 1)" \
      "TS still matches all six: a #### subsection inside a ### anchor does NOT end the section"

S="$(subject c7c)"
DOM="$(section_of "$S/$PROP_REL" "$H58" | $GREP -E '^ {4}EIP712Domain\(' | head -1)"
edit_at "$S/$PROP_REL" after "$DOM" ""
edit_at "$S/$PROP_REL" after "$DOM" "##### 5.8.0.1 A deeper subsection still"
below="$(awk -v a='##### 5.8.0.1 A deeper subsection still' '$0==a{f=1;next} f && /^#{1,5} /{exit} f' "$S/$PROP_REL" | $GREP -cE '^ {4}[A-Za-z]+Payload\(')"
check CONTROL  7c-mut "$([ "$($GREP -c -x -F '##### 5.8.0.1 A deeper subsection still' "$S/$PROP_REL")" = 1 ] && \
      [ "$below" = 5 ] && echo 0 || echo 1)" \
      "mutation applied: a ##### heading sits inside §5.8 with 5 publications below it"
o="$(run_ts "$S")"
check CONTROL  7c "$(has "$o" "$TS_OK" && echo 0 || echo 1)" \
      "paired control: a ##### subsection inside §5.8 already does not end it — so 7a is about depth, not about headings"

S="$(subject c7b)"
edit_at "$S/$PROP_REL" after "$H571" ""
edit_at "$S/$PROP_REL" after "$H571" "##### 5.7.1.1 A deeper subsection"
o="$(run_ec "$S")"
check REQUIRED 7b "$(has "$o" "$EC_OK" && echo 0 || echo 1)" \
      "EC still documents all codes: a ##### subsection inside a #### anchor does NOT end the section"

# ============================================================================ case 8 =========
hdr "CASE 8 — a SAME-DEPTH or SHALLOWER heading ENDS the section"
say "The other half of case 7, and the half that makes the depth ANCHOR-RELATIVE: the very"
say "same #### depth must stay inside a ### anchor (7a) and must terminate a #### anchor (8c)."

S="$(subject c8a)"
DOM="$(section_of "$S/$PROP_REL" "$H58" | $GREP -E '^ {4}EIP712Domain\(' | head -1)"
edit_at "$S/$PROP_REL" after "$DOM" ""
edit_at "$S/$PROP_REL" after "$DOM" "### 5.8bis An interposed same-depth heading"
below="$(awk -v a='### 5.8bis An interposed same-depth heading' '$0==a{f=1;next} f && /^### /{exit} f' "$S/$PROP_REL" | $GREP -cE '^ {4}[A-Za-z]+Payload\(')"
check CONTROL  8a-mut "$([ "$($GREP -c -x -F '### 5.8bis An interposed same-depth heading' "$S/$PROP_REL")" = 1 ] && \
      [ "$below" = 5 ] && echo 0 || echo 1)" \
      "mutation applied: a ### heading sits inside §5.8 with 5 publications below it"
o="$(run_ts "$S")"
check REQUIRED 8a "$(refuses "$o" "$TS_OK" "MandatePayload" "$MISSING_WHY" && echo 0 || echo 1)" \
      "TS ends §5.8 at an interposed ### heading and reports the publications below it absent"

S="$(subject c8b)"
DOM="$(section_of "$S/$PROP_REL" "$H58" | $GREP -E '^ {4}EIP712Domain\(' | head -1)"
edit_at "$S/$PROP_REL" after "$DOM" ""
edit_at "$S/$PROP_REL" after "$DOM" "## 5bis A shallower heading"
below="$(awk -v a='## 5bis A shallower heading' '$0==a{f=1;next} f && /^#{1,3} /{exit} f' "$S/$PROP_REL" | $GREP -cE '^ {4}[A-Za-z]+Payload\(')"
check CONTROL  8b-mut "$([ "$($GREP -c -x -F '## 5bis A shallower heading' "$S/$PROP_REL")" = 1 ] && \
      [ "$below" = 5 ] && echo 0 || echo 1)" \
      "mutation applied: a ## heading sits inside §5.8 with 5 publications below it"
o="$(run_ts "$S")"
check REQUIRED 8b "$(refuses "$o" "$TS_OK" "MandatePayload" "$MISSING_WHY" && echo 0 || echo 1)" \
      "TS ends §5.8 at an interposed shallower ## heading"

# 8c AND 8d INTERPOSE THE HEADING PART-WAY THROUGH §5.7.1, not immediately after its anchor.
# Immediately after leaves an EMPTY section, and the guard then refuses for its empty-scope
# reason instead of naming the codes that fell outside — a PASS that proves nothing about
# where the section ended. Placed after the binding paragraph, the codes below it are the
# evidence, and the case asserts one of them BY NAME.
BIND_LINE="$(section_of "$P0/$PROP_REL" "$H571" | $GREP -F 'EVAL_CHAIN_BOUND' | head -1)"
[ -n "$BIND_LINE" ] || die "cannot locate the §5.7.1 binding paragraph"

S="$(subject c8c)"
edit_at "$S/$PROP_REL" after "$BIND_LINE" "$(printf '\n#### 5.7.2 A same-depth heading\n')"
kept="$(section_of "$S/$PROP_REL" "$H571" | $GREP -c 'EVAL_CHAIN_BOUND')"
dropped="$(section_of "$S/$PROP_REL" "$H571" | $GREP -c 'EVAL_MANDATE_WINDOW')"
check CONTROL  8c-mut "$([ "$kept" = 1 ] && [ "$dropped" = 0 ] && echo 0 || echo 1)" \
      "mutation applied: a #### heading sits mid-§5.7.1; EVAL_CHAIN_BOUND is above it and EVAL_MANDATE_WINDOW below"
o="$(run_ec "$S")"
check REQUIRED 8c "$(refuses "$o" "$EC_OK" "EVAL_MANDATE_WINDOW" "$MISSING_WHY" && echo 0 || echo 1)" \
      "EC ends §5.7.1 at an interposed #### heading — the SAME depth that must stay inside §5.8 (7a)"

S="$(subject c8d)"
edit_at "$S/$PROP_REL" after "$BIND_LINE" "$(printf '\n### 5.7bis A shallower heading\n')"
o="$(run_ec "$S")"
check REQUIRED 8d "$(refuses "$o" "$EC_OK" "EVAL_MANDATE_WINDOW" "$MISSING_WHY" && echo 0 || echo 1)" \
      "EC ends §5.7.1 at an interposed shallower ### heading"

check CONTROL  8-ctl "$(has "$_p0ts" "$TS_OK" && has "$_p0ec" "$EC_OK" && echo 0 || echo 1)" \
      "paired control: with no interposed heading both sections extend over their whole content"

# ============================================================================ case 9 =========
hdr "CASE 9 — a legitimate PROSE or BACKTICKED mention is NOT a normative publication"
say "D-059(8): legitimate prose mentions must remain CONTROLS. Required: the verdict is"
say "unchanged and no duplicate refusal is raised."

S="$(subject c9a)"
AP="$(section_of "$S/$PROP_REL" "$H58" | $GREP -E '^ {4}ActionPayload\(' | head -1)"
AP_BAD="$(printf '%s' "$AP" | sed 's/bytes32 mandateHash,bytes32 policyHash/bytes32 policyHash,bytes32 mandateHash/;s/^ *//')"
edit_at "$S/$PROP_REL" after "$AP" ""
edit_at "$S/$PROP_REL" after "$AP" "An earlier draft wrote it as \`$AP_BAD\`, which is recorded here as history and is not a publication."
check CONTROL  9a-mut "$([ "$(section_of "$S/$PROP_REL" "$H58" | $GREP -c 'recorded here as history')" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: §5.8 carries an inline backticked mention of a different ActionPayload string"
o="$(run_ts "$S")"
check REQUIRED 9a "$(has "$o" "$TS_OK" && echo 0 || echo 1)" \
      "TS still reports success: an inline backticked prose mention is not a second publication"

S="$(subject c9b)"
AP="$(section_of "$S/$PROP_REL" "$H58" | $GREP -E '^ {4}ActionPayload\(' | head -1)"
AP_BAD="$(printf '%s' "$AP" | sed 's/bytes32 mandateHash,bytes32 policyHash/bytes32 policyHash,bytes32 mandateHash/;s/^ *//')"
edit_at "$S/$PROP_REL" after "$AP" ""
edit_at "$S/$PROP_REL" after "$AP" "    \`$AP_BAD\`"
check CONTROL  9b-mut "$([ "$(section_of "$S/$PROP_REL" "$H58" | $GREP -cE '^ {4}`ActionPayload\(')" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: §5.8 carries an indented BACKTICKED ActionPayload line beside the real publication"
o="$(run_ts "$S")"
check REQUIRED 9b "$(has "$o" "$TS_OK" && echo 0 || echo 1)" \
      "TS still reports success: an indented BACKTICKED line is not a normative publication"

S="$(subject c9c)"
AP="$(section_of "$S/$PROP_REL" "$H58" | $GREP -E '^ {4}ActionPayload\(' | head -1)"
AP_BAD="$(printf '%s' "$AP" | sed 's/bytes32 mandateHash,bytes32 policyHash/bytes32 policyHash,bytes32 mandateHash/')"
edit_at "$S/$PROP_REL" after "$AP" ""
edit_at "$S/$PROP_REL" after "$AP" "$AP_BAD"
o="$(run_ts "$S")"
check CONTROL  9c "$(refuses "$o" "$TS_OK" "ActionPayload" "$DUP_WHY" && echo 0 || echo 1)" \
      "paired control: the SAME text as an unbackticked indented literal IS a publication and is refused"

# ============================================================================ case 10 ========
hdr "CASE 10 — §7.2's caveat is extracted FROM §7.2, not from the first tree-wide match"
say "V3-N2. Required: the sentence enforced against the ablation report is the one §7.2"
say "itself words, whatever else in the document contains the same phrase."

S="$(subject c10a add)"
edit_at "$S/$PROP_REL" after "$H6" ""
edit_at "$S/$PROP_REL" after "$H6" "An earlier draft of this paragraph read: the demo baseline is illustrative and $CAVEAT_PHRASE in any respect."
first_ln="$($GREP -nF "$CAVEAT_PHRASE" "$S/$PROP_REL" | head -1 | cut -d: -f1)"
sec_ln="$($GREP -n -x -F -- "$H72" "$S/$PROP_REL" | cut -d: -f1)"
in72="$(section_of "$S/$PROP_REL" "$H72" | $GREP -cF "$CAVEAT_SENTENCE")"
check CONTROL  10a-mut "$([ "$first_ln" -lt "$sec_ln" ] && [ "$in72" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: a decoy carrying the phrase sits at line $first_ln, before §7.2 at line $sec_ln, which still words it exactly"
o="$(run_vh "$S")"
check REQUIRED 10a "$(has "$o" "$VH_OK" && echo 0 || echo 1)" \
      "VH reports the report carries §7.2's caveat, ignoring an earlier decoy elsewhere in the document"

S="$(subject c10b add)"
NEW72='This baseline makes the demo reproducible but, stated exactly, is not evidence that current vendors miss Case 3 at all.'
edit_at "$S/$PROP_REL" replace "$CAVEAT_SENTENCE" "$NEW72"
edit_at "$S/$PROP_REL" after "$H6" ""
edit_at "$S/$PROP_REL" after "$H6" "$CAVEAT_SENTENCE"
in72="$(section_of "$S/$PROP_REL" "$H72" | $GREP -cF "$NEW72")"
rpt="$(norm_count "$S/$RPT_REL" "$NEW72")"
check CONTROL  10b-mut "$([ "$in72" = 1 ] && [ "$rpt" = 0 ] && echo 0 || echo 1)" \
      "mutation applied: §7.2 now words the caveat differently and the report does NOT carry that wording"
o="$(run_vh "$S")"
check REQUIRED 10b "$(refuses "$o" "$VH_OK" "ablation-report.md" 'no longer|missing|absent|does not carry|fail' && echo 0 || echo 1)" \
      "VH FAILS naming the report when §7.2's own wording is absent from it, despite an earlier decoy that matches"

_p0vh="$(run_vh "$P0")"
check CONTROL  10-ctl "$(has "$_p0vh" "$VH_OK" && echo 0 || echo 1)" \
      "paired control: unmutated, VH reports the report carries §7.2's caveat"

# --- 10c … 10h: §7.2 SECTION EXTENT, SPECIFIED BEFORE ANY EXTRACTOR EXISTS ----
#
# This block has no section extractor at all today: it greps the whole 84 KB document. These
# six cases state what its extent must be BEFORE one is introduced, so the repair is written
# against a specification rather than the specification being written around the repair. Every
# one of them is heading-depth-relative to the §7.2 ANCHOR (`###`), never to a fixed class.
#
# Each is discriminating at this commit for a stated reason, not by accident: 10c plants a decoy
# so that a whole-document search cannot pass it; 10d, 10e, 10f and 10g move or duplicate the
# anchor so that a whole-document search reports a caveat §7.2 does not carry.
VH_REFUSE_WHY='7\.2|section'
VH_MISSING_WHY='no longer|missing|absent|does not carry|could not (isolate|find|locate)|refus|fail'

S="$(subject c10c add)"
edit_at "$S/$PROP_REL" before "$CAVEAT_SENTENCE" "$(printf '#### 7.2.1 A deeper subsection\n')"
edit_at "$S/$PROP_REL" after "$H6" ""
edit_at "$S/$PROP_REL" after "$H6" "An earlier draft of this paragraph read: the demo baseline is illustrative and $CAVEAT_PHRASE in any respect."
in72="$(section_of "$S/$PROP_REL" "$H72" | $GREP -cF "$CAVEAT_SENTENCE")"
first_ln="$($GREP -nF "$CAVEAT_PHRASE" "$S/$PROP_REL" | head -1 | cut -d: -f1)"
sec_ln="$($GREP -n -x -F -- "$H72" "$S/$PROP_REL" | cut -d: -f1)"
check CONTROL  10c-mut "$([ "$in72" = 1 ] && [ "$first_ln" -lt "$sec_ln" ] && \
      [ "$($GREP -c -x -F '#### 7.2.1 A deeper subsection' "$S/$PROP_REL")" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: a #### subsection precedes §7.2's caveat INSIDE §7.2, and a decoy sits earlier in the file"
o="$(run_vh "$S")"
check REQUIRED 10c "$(has "$o" "$VH_OK" && echo 0 || echo 1)" \
      "a #### subsection inside §7.2 does NOT end it — the caveat below it is still §7.2's"

S="$(subject c10d add)"
edit_at "$S/$PROP_REL" delete "$CAVEAT_SENTENCE" ""
edit_at "$S/$PROP_REL" after "### 7.3 Security Ablation" "$(printf '\n%s\n' "$CAVEAT_SENTENCE")"
in72="$(section_of "$S/$PROP_REL" "$H72" | $GREP -cF "$CAVEAT_SENTENCE")"
in73="$(section_of "$S/$PROP_REL" "### 7.3 Security Ablation" | $GREP -cF "$CAVEAT_SENTENCE")"
check CONTROL  10d-mut "$([ "$in72" = 0 ] && [ "$in73" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: the caveat left §7.2 and now sits below the same-depth ### 7.3 heading"
o="$(run_vh "$S")"
check REQUIRED 10d "$(refuses "$o" "$VH_OK" "7.2" "$VH_MISSING_WHY" && echo 0 || echo 1)" \
      "a same-depth ### heading ENDS §7.2 — a caveat below it is not §7.2's and must be refused"

S="$(subject c10e add)"
edit_at "$S/$PROP_REL" before "$CAVEAT_SENTENCE" "$(printf '## 7bis A shallower heading\n')"
in72="$(section_of "$S/$PROP_REL" "$H72" | $GREP -cF "$CAVEAT_SENTENCE")"
check CONTROL  10e-mut "$([ "$in72" = 0 ] && [ "$($GREP -c -x -F '## 7bis A shallower heading' "$S/$PROP_REL")" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: a shallower ## heading now separates §7.2 from the caveat"
o="$(run_vh "$S")"
check REQUIRED 10e "$(refuses "$o" "$VH_OK" "7.2" "$VH_MISSING_WHY" && echo 0 || echo 1)" \
      "a shallower ## heading ENDS §7.2 likewise"

S="$(subject c10f add)"
edit_at "$S/$PROP_REL" delete "$H72" ""
check CONTROL  10f-mut "$([ "$($GREP -c -x -F -- "$H72" "$S/$PROP_REL")" = 0 ] && \
      [ "$($GREP -cF "$CAVEAT_SENTENCE" "$S/$PROP_REL")" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: the §7.2 heading is absent while its former text remains in the document"
o="$(run_vh "$S")"
check REQUIRED 10f "$(refuses "$o" "$VH_OK" "7.2" "$VH_MISSING_WHY" && echo 0 || echo 1)" \
      "an ABSENT §7.2 anchor is REFUSED by name — never a fallback to a whole-document search"

S="$(subject c10g add)"
edit_at "$S/$PROP_REL" before "$H6" "$(printf '%s\n\nA decoy section claiming the same anchor.\n\n---\n' "$H72")"
check CONTROL  10g-mut "$([ "$($GREP -c -x -F -- "$H72" "$S/$PROP_REL")" = 2 ] && echo 0 || echo 1)" \
      "mutation applied: TWO exact §7.2 headings, the decoy first"
o="$(run_vh "$S")"
check REQUIRED 10g "$(refuses "$o" "$VH_OK" "7.2" "$AMBIG_WHY" && echo 0 || echo 1)" \
      "TWO exact §7.2 headings are REFUSED as ambiguous — the checker must not select the first"

S="$(subject c10h add)"
plant_quoted_anchor "$S" "$H72" 'This baseline is illustrative and is not evidence that current vendors miss Case 3 at all.' "$H6"
check CONTROL  10h-btick-mut "$([ "$($GREP -c -x -F -- "$H72" "$S/$PROP_REL")" = 2 ] && \
      [ "$($GREP -c -x -F '```markdown' "$S/$PROP_REL")" = 1 ] && \
      [ "$(section_of "$P0/$PROP_REL" "$H72" | $GREP -cF "$CAVEAT_SENTENCE")" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: the §7.2 heading is quoted inside a BACKTICK fence earlier; the real §7.2 is untouched"
o="$(run_vh "$S")"
check REQUIRED 10h-btick "$(has "$o" "$VH_OK" && echo 0 || echo 1)" \
      "a §7.2 heading quoted inside a BACKTICK fence is a MENTION, not the anchor"

S="$(subject c10h-tilde add)"
plant_quoted_anchor "$S" "$H72" 'This baseline is illustrative and is not evidence that current vendors miss Case 3 at all.' "$H6" '~~~'
check CONTROL  10h-tilde-mut "$([ "$($GREP -c -x -F -- "$H72" "$S/$PROP_REL")" = 2 ] && \
      [ "$($GREP -c -x -F '~~~markdown' "$S/$PROP_REL")" = 1 ] && \
      [ "$($GREP -c -x -F '```markdown' "$S/$PROP_REL")" = 0 ] && \
      [ "$(section_of "$P0/$PROP_REL" "$H72" | $GREP -cF "$CAVEAT_SENTENCE")" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: the §7.2 heading is quoted inside a TILDE fence (and no backtick fence) earlier; the real §7.2 is untouched"
o="$(run_vh "$S")"
check REQUIRED 10h-tilde "$(has "$o" "$VH_OK" && echo 0 || echo 1)" \
      "a §7.2 heading quoted inside a TILDE fence is a MENTION, not the anchor"

# ============================================================================ case 11 ========
hdr "CASE 11 — the generated ablation report still carries the EXACT required caveat"
say "D-058(6): the comparison is over LOGICAL PARAGRAPHS. A hard line wrap on either side is"
say "not a change to the text, and a line-oriented grep is disallowed for this purpose."

check REQUIRED 11a "$(has "$_p0vh" "$VH_OK" && echo 0 || echo 1)" \
      "at the base commit the report carries §7.2's caveat verbatim"

S="$(subject c11b add)"
edit_at "$S/$PROP_REL" replace "$CAVEAT_SENTENCE" \
    "This baseline makes the demo reproducible but is not evidence that current
vendors miss Case 3."
raw="$($GREP -cF "$CAVEAT_PHRASE" "$S/$PROP_REL")"
nrm="$(norm_count "$S/$PROP_REL" "$CAVEAT_PHRASE")"
check CONTROL  11b-mut "$([ "$raw" = 0 ] && [ "$nrm" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: §7.2's caveat is hard-wrapped — 0 line-oriented hits, 1 normalized hit"
o="$(run_vh "$S")"
check REQUIRED 11b "$(has "$o" "$VH_OK" && echo 0 || echo 1)" \
      "VH still locates §7.2's caveat across a hard line wrap and confirms the report carries it"

S="$(subject c11c add)"
sed 's/evidence that current vendors miss Case 3\./evidence that current providers miss Case 3./' \
    "$S/$RPT_REL" > "$S/$RPT_REL.t" && mv "$S/$RPT_REL.t" "$S/$RPT_REL"
check CONTROL  11c-mut "$([ "$(norm_count "$S/$RPT_REL" "$CAVEAT_PHRASE")" = 0 ] && echo 0 || echo 1)" \
      "mutation applied: the report's copy of the caveat differs by one word"
o="$(run_vh "$S")"
check CONTROL  11c "$(refuses "$o" "$VH_OK" "ablation-report.md" 'no longer|missing|absent|does not carry|fail' && echo 0 || echo 1)" \
      "paired control: VH does FAIL naming the report when the report's copy is altered"

S="$(subject c11d add)"
awk '{ if ($0 ~ /^\*\*§7\.2.s own caveat, verbatim:\*\*/) { print "**§7.2'"'"'s own caveat, verbatim:** *\"This baseline makes the demo"; skip=1; next } if (skip) { print "reproducible but is not evidence that current vendors"; print "miss Case 3.\"* The L1 arm is a local reimplementation of the"; skip=0; next } print }' \
    "$S/$RPT_REL" > "$S/$RPT_REL.t" && mv "$S/$RPT_REL.t" "$S/$RPT_REL"
raw="$($GREP -cF "$CAVEAT_PHRASE" "$S/$RPT_REL")"
nrm="$(norm_count "$S/$RPT_REL" "$CAVEAT_PHRASE")"
check CONTROL  11d-mut "$([ "$raw" = 0 ] && [ "$nrm" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: the report is re-wrapped at a different column — 0 line hits, 1 normalized hit"
o="$(run_vh "$S")"
check CONTROL  11d "$(has "$o" "$VH_OK" && echo 0 || echo 1)" \
      "paired control: a re-wrap of the report alone is tolerated, so 11b is about the PROPOSAL side"

# --- 11e / 11f: THE CANONICAL GENERATOR IS EXECUTED, NOT PARAPHRASED ----------
#
# The first version of this case counted the caveat's two halves in `ts/src/ablation/report.ts`
# and called that "the caveat comes from the generator". That is a proxy over source text: it
# cannot tell an emitted sentence from a commented-out one, and it says nothing about the
# artifact a regeneration would actually produce. The generator is now RUN — the same entry
# point `scripts/test.sh` uses at its `§7.3 ablation report is the output of its generator
# (A-062)` stage, `buildReport(loadInputs())` — and the assertions are on its OUTPUT.
#
# The generated artifact is never written into the repository under test. It is produced into
# the scratch area and compared there.
GEN_OUT="$WORK/regen-report.md"
gen_report() {  # SUBJECT OUTFILE -> 0 when the generator ran
    local sub out prog
    sub="$1"; out="$2"; prog="$WORK/.gen.mjs"
    { printf "const {loadInputs, buildReport} = await import('%s/ts/src/ablation/report.ts');\n" "$sub"
      printf "const fs = await import('node:fs');\n"
      printf "fs.writeFileSync('%s', buildReport(loadInputs()));\n" "$out"
    } > "$prog"
    rm -f "$out"
    ( cd "$sub" && node "$prog" >/dev/null 2>&1 ) && [ -s "$out" ]
}

if gen_report "$GEN" "$GEN_OUT"; then
    check CONTROL  11f-ran 0 "the canonical generator executed on the committed inputs"
    check REQUIRED 11f-a "$(cmp -s "$GEN_OUT" "$GEN/$RPT_REL" && echo 0 || echo 1)" \
          "the committed ablation report IS this generator's output on the committed inputs, byte for byte"
    check REQUIRED 11f-b "$([ "$(norm_count "$GEN_OUT" "$CAVEAT_PHRASE")" -ge 1 ] && echo 0 || echo 1)" \
          "the REGENERATED artifact carries §7.2's caveat — so the caveat is generated, not pasted"
    S="$(subject c11fc add)"
    cp "$GEN_OUT" "$S/$RPT_REL"
    o="$(run_vh "$S")"
    check REQUIRED 11f-c "$(has "$o" "$VH_OK" && echo 0 || echo 1)" \
          "VH passes against the FRESHLY REGENERATED artifact, not merely against the committed bytes"

    # The paired opposite outcome, and the proof this probe is alive: delete the emitting
    # statement from the generator, regenerate, and the caveat must be gone from the output and
    # the guard must fail naming the report.
    cp "$GEN/ts/src/ablation/report.ts" "$WORK/.report.ts.orig"
    awk '!/This baseline makes the demo reproducible but is not/' "$GEN/ts/src/ablation/report.ts" \
        > "$GEN/ts/src/ablation/report.ts.t" && mv "$GEN/ts/src/ablation/report.ts.t" "$GEN/ts/src/ablation/report.ts"
    emit_after="$($GREP -c 'This baseline makes the demo reproducible but is not' "$GEN/ts/src/ablation/report.ts")"
    GEN_OUT_MUT="$WORK/regen-report-mut.md"
    if gen_report "$GEN" "$GEN_OUT_MUT"; then
        gen_caveat="$(norm_count "$GEN_OUT_MUT" "$CAVEAT_PHRASE")"
        check CONTROL  11f-mut "$([ "$emit_after" = 0 ] && [ "$gen_caveat" = 0 ] && echo 0 || echo 1)" \
              "mutation applied: the emitting statement is gone from the generator and the caveat is absent from its output"
        S="$(subject c11fd add)"
        cp "$GEN_OUT_MUT" "$S/$RPT_REL"
        o="$(run_vh "$S")"
        check CONTROL  11f-ctl "$(refuses "$o" "$VH_OK" "ablation-report.md" 'no longer|missing|absent|does not carry|fail' && echo 0 || echo 1)" \
              "paired control: a generator that stops emitting the caveat makes VH FAIL naming the report"
    else
        check CONTROL  11f-mut 1 "the mutated generator did not run — this probe is dead and proves nothing"
    fi
    cp "$WORK/.report.ts.orig" "$GEN/ts/src/ablation/report.ts"
    check CONTROL  11f-restore "$([ "$($GREP -c 'This baseline makes the demo reproducible but is not' "$GEN/ts/src/ablation/report.ts")" = 1 ] && echo 0 || echo 1)" \
          "the generator fixture is restored, so nothing downstream inherits the mutation"
else
    check CONTROL  11f-ran 1 "THE CANONICAL GENERATOR DID NOT RUN — a check that cannot execute must never read as one that passed"
fi

check OBSERVED 11e 0 "generator entry point: buildReport(loadInputs()) from ts/src/ablation/report.ts — the same one scripts/test.sh's A-062 stage uses"

# --- 11g: the AX-3 FALSE-ASSURANCE direction, demonstrated by the adjudicator --
#
# RESULTS.md at ca49f18 recorded only the false-FAILURE direction of the wrap trap. The
# independent adjudicator demonstrated the other one, and it is the direction D-059(1) turns on:
# wrap §7.2's caveat BEFORE the anchor phrase so the extracted sentence is only the TAIL, then
# delete the head half from the report. The report has lost half the caveat and the guard
# certifies it "verbatim, as §7.2 words it".
S="$(subject c11g add)"
edit_at "$S/$PROP_REL" replace "$CAVEAT_SENTENCE" \
    "This baseline makes the demo reproducible but
is not evidence that current vendors miss Case 3."
python3 - "$S/$RPT_REL" <<'PY_11G'
import sys
path = sys.argv[1]
text = open(path, encoding="utf-8").read()
old = '*"This baseline makes the demo reproducible but is not\nevidence that current vendors miss Case 3."*'
new = '*"...is not\nevidence that current vendors miss Case 3."*'
assert old in text, "the report fixture moved; 11g cannot be planted"
open(path, "w", encoding="utf-8").write(text.replace(old, new))
PY_11G
prop_head="$(norm_count "$S/$PROP_REL" 'This baseline makes the demo reproducible but is not evidence')"
rpt_head="$(norm_count "$S/$RPT_REL" 'This baseline makes the demo reproducible')"
rpt_tail="$(norm_count "$S/$RPT_REL" "$CAVEAT_PHRASE")"
check CONTROL  11g-mut "$([ "$prop_head" = 1 ] && [ "$rpt_head" = 0 ] && [ "$rpt_tail" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: §7.2 still words the whole caveat; the report carries only its tail (head=$rpt_head, tail=$rpt_tail)"
o="$(run_vh "$S")"
check REQUIRED 11g "$(refuses "$o" "$VH_OK" "ablation-report.md" 'no longer|missing|absent|does not carry|fail' && echo 0 || echo 1)" \
      "VH FAILS naming the report when the report carries only HALF of §7.2's caveat"

# ============================================================================ case 12 ========
hdr "CASE 12 — EC rejects a ONE-CHARACTER prefix substitution"
say "C1. Required: exact-token membership. One appended or prepended character makes a"
say "DIFFERENT identifier, and an unanchored substring search cannot tell them apart."

for variant in suffix prefix; do
    S="$(subject "c12$variant")"
    if [ "$variant" = suffix ]; then repl="EVAL_NONCE_CURRENTX"; else repl="XEVAL_NONCE_CURRENT"; fi
    sec_sub "$S/$PROP_REL" "$H571" 'EVAL_NONCE_CURRENT' "$repl"
    body="$(section_of "$S/$PROP_REL" "$H571")"
    exact="$(printf '%s' "$body" | $GREP -cE '(^|[^A-Za-z0-9_])EVAL_NONCE_CURRENT([^A-Za-z0-9_]|$)')"
    sub="$(printf '%s' "$body" | $GREP -c 'EVAL_NONCE_CURRENT')"
    check CONTROL  "12$variant-mut" "$([ "$exact" = 0 ] && [ "$sub" = 1 ] && echo 0 || echo 1)" \
          "mutation applied: §5.7.1 carries $repl — 0 exact-token hits, 1 substring hit"
    o="$(run_ec "$S")"
    check REQUIRED "12$variant" "$(refuses "$o" "$EC_OK" "EVAL_NONCE_CURRENT" "$MISSING_WHY" && echo 0 || echo 1)" \
          "EC reports EVAL_NONCE_CURRENT undocumented when §5.7.1 carries only $repl"
done

S="$(subject c12ctl)"
sec_sub "$S/$PROP_REL" "$H571" 'EVAL_NONCE_CURRENT' 'EVAL_SOMETHING_ELSE'
o="$(run_ec "$S")"
check CONTROL  12-ctl "$(refuses "$o" "$EC_OK" "EVAL_NONCE_CURRENT" "$MISSING_WHY" && echo 0 || echo 1)" \
      "paired control: with the token replaced by an unrelated one EC does name it undocumented"

# ============================================================================ case 13 ========
hdr "CASE 13 — the two §5.8 consumers produce the SAME REASON CLASS"
say "Two consumers of one section that disagree about its extent, or that fail for different"
say "reasons, are two different claims wearing one section number. Required: on each fixture"
say "both consumers land in the SAME named class — not merely the same success/failure bit."

pair() {  # SUBJECT EXPECTED_CLASS CASEID DESC   — asserts BOTH consumers reach EXPECTED_CLASS
    local s exp id desc tc vc
    s="$1"; exp="$2"; id="$3"; desc="$4"
    tc="$(ts_class "$(run_ts "$s")")"
    vc="$(vp_class "$(run_vp "$s")")"
    check REQUIRED "$id" "$([ "$tc" = "$exp" ] && [ "$vc" = "$exp" ] && echo 0 || echo 1)" \
          "$desc — required class '$exp'; shell='$tc', verifier='$vc'"
}

S="$(subject c13a)"
DOM="$(section_of "$S/$PROP_REL" "$H58" | $GREP -E '^ {4}EIP712Domain\(' | head -1)"
edit_at "$S/$PROP_REL" after "$DOM" ""
edit_at "$S/$PROP_REL" after "$DOM" "#### 5.8.1 Domain field values"
check CONTROL  13a-mut "$([ "$($GREP -c -x -F '#### 5.8.1 Domain field values' "$S/$PROP_REL")" = 1 ] && echo 0 || echo 1)" \
      "mutation applied: the #### subsection is present inside §5.8"
pair "$S" success 13a "a deeper #### subsection inside §5.8 truncates nothing"

for order in before after; do
    S="$(subject "c13b$order")"
    AP="$(section_of "$S/$PROP_REL" "$H58" | $GREP -E '^ {4}ActionPayload\(' | head -1)"
    AP_BAD="$(printf '%s' "$AP" | sed 's/bytes32 mandateHash,bytes32 policyHash/bytes32 policyHash,bytes32 mandateHash/')"
    edit_at "$S/$PROP_REL" "$order" "$AP" ""
    edit_at "$S/$PROP_REL" "$order" "$AP" "$AP_BAD"
    n="$(section_of "$S/$PROP_REL" "$H58" | $GREP -cE '^ {4}ActionPayload\(')"
    check CONTROL  "13b-$order-mut" "$([ "$n" = 2 ] && echo 0 || echo 1)" \
          "mutation applied: §5.8 publishes ActionPayload twice (decoy $order the real line)"
    pair "$S" duplicate-publication "13b-$order" "a duplicate publication with the decoy $order the real line"
done

S="$(subject c13d)"
DOM="$(section_of "$S/$PROP_REL" "$H58" | $GREP -E '^ {4}EIP712Domain\(' | head -1)"
edit_at "$S/$PROP_REL" after "$DOM" ""
edit_at "$S/$PROP_REL" after "$DOM" "---"
rules_now="$(section_of "$S/$PROP_REL" "$H58" | $GREP -c -x -- '---')"
rules_base="$(section_of "$P0/$PROP_REL" "$H58" | $GREP -c -x -- '---')"
check CONTROL  13d-mut "$([ "$rules_now" = "$((rules_base + 1))" ] && echo 0 || echo 1)" \
      "mutation applied: §5.8 now carries $rules_now horizontal rules where the base carries $rules_base"
pair "$S" success 13d "a horizontal rule inside §5.8 is typography, not a section boundary"

S="$(subject c13e)"
edit_at "$S/$PROP_REL" delete "$H58" ""
check CONTROL  13e-mut "$([ "$($GREP -c -x -F -- "$H58" "$S/$PROP_REL")" = 0 ] && echo 0 || echo 1)" \
      "mutation applied: the §5.8 anchor is absent"
pair "$S" anchor-unresolved 13e "an absent §5.8 anchor is unresolved for BOTH consumers, and by the same name"

S="$(subject c13f)"
plant_decoy_section "$S" "$H58" "$H59"
check CONTROL  13f-mut "$([ "$($GREP -c -x -F -- "$H58" "$S/$PROP_REL")" = 2 ] && echo 0 || echo 1)" \
      "mutation applied: two headings claim the §5.8 anchor"
pair "$S" anchor-ambiguous 13f "a duplicated §5.8 anchor is ambiguous for BOTH consumers"

_p0tc="$(ts_class "$_p0ts")"; _p0vc="$(vp_class "$_p0vp")"
check CONTROL  13-ctl "$([ "$_p0tc" = "success" ] && [ "$_p0vc" = "success" ] && echo 0 || echo 1)" \
      "paired control: unmutated, both consumers are class 'success' — so class equality above is not vacuous"

check OBSERVED 13-patch 0 "the verifier-side contract for these classes is TESTS.patch, supplied and NOT applied"

# ============================================================================ case 14 ========
hdr "CASE 14 — the certified §2 table and its pin, exercised in an ISOLATED COPY"
say "D-059(1): the certification stands and is neither revoked, reaffirmed nor recertified by"
say "this batch. The live pin is never updated, re-signed or touched, and no signed document is"
say "read for change. Both directions are exercised on a private snapshot instead."

check CONTROL  14-fixture "$([ "$($GREP -oE 'CERTIFIED_TABLE_SHA="[0-9a-f]{64}"' "$P0/scripts/check-vendor-honesty.sh" | head -1 | sed 's/.*="//;s/"//')" = "$GATE5_PINNED" ] && echo 0 || echo 1)" \
      "fixture sanity: the snapshot's pinned §2 hash is the value D-038 certified"

check REQUIRED 14a "$(has "$_p0vh" "certified by record" && ! has "$_p0vh" "STALE" && echo 0 || echo 1)" \
      "PASS direction: on the unmodified snapshot the pin matches and VH reports the §2 table certified by record"

S="$(subject c14b add)"
row="$(awk '/^## 2\. Need, Market Reality, and First User/{t=1} t&&/^## 3\./{exit} t&&/^\| /{n++; if(n==3){print; exit}}' "$S/$PROP_REL")"
[ -n "$row" ] || die "cannot read a §2 capability table row"
edit_at "$S/$PROP_REL" replace "$row" "$(printf '%s' "$row" | sed 's/|$/ |/')"
pin_after="$($GREP -oE 'CERTIFIED_TABLE_SHA="[0-9a-f]{64}"' "$S/scripts/check-vendor-honesty.sh" | head -1 | sed 's/.*="//;s/"//')"
check CONTROL  14b-mut "$([ "$($GREP -c -x -F -- "$row" "$S/$PROP_REL")" = 0 ] && [ "$pin_after" = "$GATE5_PINNED" ] && echo 0 || echo 1)" \
      "mutation applied: one §2 row differs from the certified text and THE PIN IS LEFT UNCHANGED"
o="$(run_vh "$S")"
check REQUIRED 14b "$(has "$o" "STALE" && ! has "$o" "certified by record" && echo 0 || echo 1)" \
      "FAIL direction: a §2 mutation with the pin unchanged makes VH report the certification STALE"

# ============================================================================ integrity =====
hdr "HARNESS INTEGRITY"
# THESE FOUR ARE ABOUT THE SUBJECT, and after the correction they say so. Comparing the snapshot
# against a hardcoded historical commit was the mechanism by which a repaired consumer would have
# been reported as pre-repair with the control still green.
# THESE FOUR ARE THE EXECUTION WITNESS, and they now assert three things rather than one: the
# snapshot's consumer matches the SUBJECT's blob, that exact hash was RECORDED AT EXECUTION at
# least once, and every recorded execution of that consumer carried the same bytes. A control
# that only compared two files on disk would leave "and it was the file we ran" as an inference.
for f in scripts/check-type-strings.sh scripts/check-eval-codes.sh scripts/check-vendor-honesty.sh verifier/test_verifier.py; do
    a="$(shasum -a 256 "$P0/$f" | awk '{print $1}')"
    b="$(cd "$ROOT" && git --no-replace-objects show "$SUBJECT_SHA:$f" | shasum -a 256 | awk '{print $1}')"
    execs="$(awk -F'\t' -v k="$f" '$1==k{n++} END{print n+0}' "$WITNESS_LOG" 2>/dev/null)"
    distinct="$(awk -F'\t' -v k="$f" '$1==k{print $2}' "$WITNESS_LOG" 2>/dev/null | sort -u | wc -l | tr -d ' ')"
    matched="$(awk -F'\t' -v k="$f" -v h="$a" '$1==k && $2==h{n++} END{print n+0}' "$WITNESS_LOG" 2>/dev/null)"
    check CONTROL "Z-${f##*/}" "$([ "$a" = "$b" ] && [ "$execs" -ge 1 ] && [ "$distinct" = "1" ] && \
          [ "$matched" = "$execs" ] && echo 0 || echo 1)" \
          "EXECUTED bytes are SUBJECT_SHA's: ${f##*/} ${a%%????????????????????????????????????????????????????????}… — ${execs} execution(s) recorded, all carrying that hash"
done
# THE NEXT THREE CONTROLS ARE ABOUT THE LIVE WORKING TREE, NOT ABOUT THE SUBJECT, and they are
# deliberately NOT folded into the Z-consumer comparison above. "the snapshot matches the commit
# I asked for" and "this run changed nothing in the repository it read" are different claims, and
# a single merged control would let either one carry the other.
dirty="$(cd "$ROOT" && git status --porcelain -- "$PROP_REL" "$SRC_REL" "$RPT_REL" scripts verifier | wc -l | tr -d ' ')"
check CONTROL Z-clean "$([ "$dirty" = "0" ] && echo 0 || echo 1)" \
      "the repository under test was not modified by this run ($dirty changed path(s) in the boundary)"

# GATE 5 IS AN INTEGRITY CONTROL, NOT A FALSIFICATION. The earlier `14d` compared the live
# repository's pin and §2 hash against a constant with NO opposite outcome available — proving
# the pin is live in the live tree would mean editing §2 there, which D-059(1) forbids. It is
# therefore no longer a REQUIRED case; the pass/fail pair lives at 14a/14b on the snapshot, and
# what remains here is the same shape as the other Z-* controls: the thing this batch promised
# not to touch is byte-identical to its base blob.
live_pin="$($GREP -oE 'CERTIFIED_TABLE_SHA="[0-9a-f]{64}"' "$ROOT/scripts/check-vendor-honesty.sh" | head -1 | sed 's/.*="//;s/"//')"
live_tbl="$(awk '/^## 2\. Need, Market Reality, and First User/{t=1} t&&/^## 3\./{exit} t&&/^\|/{print} t&&/^\*Certified by John/{print}' "$ROOT/$PROP_REL" | shasum -a 256 | awk '{print $1}')"
base_tbl="$(cd "$ROOT" && git show "$PRE_REPAIR_SHA:$PROP_REL" | awk '/^## 2\. Need, Market Reality, and First User/{t=1} t&&/^## 3\./{exit} t&&/^\|/{print} t&&/^\*Certified by John/{print}' | shasum -a 256 | awk '{print $1}')"
check CONTROL Z-gate5 "$([ "$live_pin" = "$GATE5_PINNED" ] && [ "$live_tbl" = "$GATE5_PINNED" ] && [ "$base_tbl" = "$GATE5_PINNED" ] && echo 0 || echo 1)" \
      "Gate 5 untouched IN THE LIVE TREE: the live pin, the live §2 table and the §2 table at PRE_REPAIR_SHA all hash to the certified value"

# THE SIGNED PACK IS NOT READ FOR CHANGE AND IS ASSERTED UNMOVED. D-059(1b) and D-060(4):
# `docs/gate-s2-evidence.md` carries signed text and a ratified correction. This batch does not
# edit it, quote it for correction, or re-hash it — and says so mechanically rather than in prose.
s2_now="$(shasum -a 256 "$ROOT/docs/gate-s2-evidence.md" | awk '{print $1}')"
s2_base="$(cd "$ROOT" && git show "$PRE_REPAIR_SHA:docs/gate-s2-evidence.md" | shasum -a 256 | awk '{print $1}')"
check CONTROL Z-signed "$([ "$s2_now" = "$s2_base" ] && echo 0 || echo 1)" \
      "docs/gate-s2-evidence.md IN THE LIVE TREE is byte-identical to PRE_REPAIR_SHA (${s2_now%%????????????????????????????????????????????????????????}…)"

# ============================================================================ summary ========
hdr "SUMMARY"
identity_block
echo
printf '%s' "$MATRIX_TSV" > "$WORK/matrix.tsv"
if [ -n "${A_EXTRACT_MATRIX_OUT:-}" ]; then cp "$WORK/matrix.tsv" "$A_EXTRACT_MATRIX_OUT"; fi
req_total="$(printf '%s' "$MATRIX_TSV" | awk -F'\t' '$2=="REQUIRED"' | wc -l | tr -d ' ')"
ctl_total="$(printf '%s' "$MATRIX_TSV" | awk -F'\t' '$2=="CONTROL"'  | wc -l | tr -d ' ')"
printf '  REQUIRED : %s of %s held\n' "$((req_total - req_fail))" "$req_total"
printf '  CONTROL  : %s of %s held\n' "$((ctl_total - ctl_fail))" "$ctl_total"
echo
if [ "$ctl_fail" -ne 0 ]; then
    echo "  CONTROL FAILURE — the harness is untrustworthy and no verdict beside a failing"
    echo "  control may be relied on. Fix the harness before reading the REQUIRED column."
    exit 2
fi
if [ "$req_fail" -ne 0 ]; then
    echo "  REQUIRED FAILURES with every control holding: the defects are observed."
    exit 1
fi
echo "  Every REQUIRED and every CONTROL held."
exit 0
