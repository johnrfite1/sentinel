#!/usr/bin/env bash
# The D-055(e) review scope manifest, asserted rather than asserted-about (D-056(d)).
#
# WHY THIS IS A SCRIPT AND NOT A TABLE IN A DOCUMENT. John's requirement was that the
# remaining tracked documents be "partitioned explicitly so the claims surface is not covered
# merely by assertion". A hand-written table IS an assertion: it claims completeness, nothing
# checks it, and this repository has now recorded three separate cases of a hand-maintained
# status table going stale while being cited as authority (register §13.4, the gate's coverage
# boundary, session-state §3).
#
# So the partition is executable. Every tracked file is matched against the reviewer patterns
# below, and **this exits non-zero if any tracked file is assigned to NO reviewer** — WHEN IT IS
# RUN.
#
# WHAT INVOKES IT, stated exactly because the previous wording did not (R1-F3, D-055(e)).
# **Nothing runs this automatically.** It is not a stage of `scripts/test.sh`, not a git hook,
# and not called by any other script. It is a DISPATCH-TIME check: run by hand before a review
# is scoped and before reviewers are provisioned, which is the only moment its answer means
# anything. The earlier header said a newly added file "turns this red rather than sliding into
# a gap", which described a mechanism that does not exist — nothing would have turned red until
# somebody typed the command.
#
# **It is deliberately NOT wired into the gate (D-057(4)).** This manifest belongs to ONE
# bounded, now-spent review; making the permanent product gate depend on a spent review's
# scope would be wiring history into the build to make a sentence true. John ruled that
# explicitly. `docs/d055e-scope-manifest.md` says "do not trust that line — run
# `./scripts/check-review-scope.sh`", and running it is the whole contract.
#
# WHAT IT DOES NOT DO, corrected 2026-08-18 because the first version of this header claimed
# it. **It does not detect OVERLAPPING patterns.** `assign()` is a `case`, and a `case` returns
# on its FIRST match: a file matching three arms is assigned by the first and the other two are
# never evaluated. So every file gets exactly one reviewer BY CONSTRUCTION — which is a real
# property and the one the partition needs — but an overlap is silently RESOLVED, not reported.
# Saying it detected double-assignment described a mechanism that is not here.
#
# NO OVERLAP DETECTOR IS BUILT, deliberately. First-match precedence is what makes the specific
# rules above the general ones work at all — `ts/src/corpus/*` must beat `ts/src/*`, and
# `docs/ablation-report.md` must beat nothing else claiming it — so overlap is the DESIGN, not
# a defect to find. A detector would flag every deliberate precedence rule as a problem. The
# ordering is the specification; read it as one.
#
# REVIEWER 4 IS DELIBERATELY ABSENT FROM THE PATTERNS. Its scope is "no assigned target, no
# preferred direction, no surface hints" (D-056(d)), so assigning it files would defeat it.
# Coverage here means R1-R3 partition the tree; R4 ranges over all of it.
set -uo pipefail

# --- Sentinel repository identity (D-060(2)) ---------------------------------
# Derived from THIS FILE's own location, never the caller's working directory, so a
# run from an unrelated directory or a foreign repository still inspects Sentinel.
# Every step is checked: `cd ""` returns 0 and does not abort even under `set -e`.
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

# --- The partition. FIRST MATCH WINS, so more specific rules come first and the ordering is
#     load-bearing. Moving an arm changes assignments silently; nothing detects that but review.
#     The seams these deliberate overlaps create are named in docs/d055e-scope-manifest.md. ---
#
# R1 certification and instruments: scripts, gate/guard behaviour, the D-010 verifier and its
#    samples, and the cross-cutting canonical records (both signed packs, decisions,
#    session-state, HANDOFF, README).
# R2 authorization and effect pipeline: signer, the Solidity type mirror, evaluate, decode,
#    simulate, propose, tools — and the proposal sections those surfaces own.
# R3 onchain and corpus: contracts and the Foundry suites, corpus, ablation, fixtures/corpus.
assign() {
    case "$1" in
        scripts/*)                                   echo R1 ;;
        verifier/*|fixtures/samples/*)               echo R1 ;;
        docs/gate-s1-evidence.md|docs/gate-s2-evidence.md) echo R1 ;;
        docs/decisions.md|docs/session-state.md)     echo R1 ;;
        HANDOFF.md|README.md)                        echo R1 ;;
        docs/repair-protocol.md|docs/exit-criterion-packet.md|docs/v1-1-register.md) echo R1 ;;
        docs/gate-5-vendor-audit.md|docs/round-six-brief.md) echo R1 ;;
        # This manifest itself. R1, because it is a CLAIM about coverage and whether a claim
        # matches its evidence is R1's subject — and because a manifest nobody reviews is the
        # same shape as the status tables this script exists to replace. It was caught by this
        # script on its first run after being written, which is the intended behaviour.
        docs/d055e-scope-manifest.md)                echo R1 ;;
        docs/review-*)                               echo R1 ;;
        .githooks/*|.gitignore|.gitmodules|.env.example) echo R1 ;;
        # Gate 7 / D-019: the injection spike, the canary, and the recorded runs they read.
        # R1 because Gate 7 IS a gate and D-007's rule about it is an INSTRUMENT rule -- "an
        # unobserved canary is not evidence" -- which is R1's subject. `ts/src/propose` and
        # `ts/src/corpus` also read these fixtures, so this is a genuine seam rather than a
        # tidy boundary; it is assigned here deliberately and named as a seam in the manifest
        # so the reviewers on either side know the other exists.
        ts/src/spike/*|ts/test/canary.test.ts)       echo R1 ;;
        fixtures/injection/*|fixtures/d019-revisit/*) echo R1 ;;

        contracts/test/*|contracts/src/*|contracts/foundry.toml|contracts/*) echo R3 ;;
        ts/src/corpus/*|ts/src/ablation/*)           echo R3 ;;
        ts/test/corpus.test.ts|ts/test/ablation.test.ts) echo R3 ;;
        fixtures/corpus/*)                           echo R3 ;;
        docs/ablation-report.md)                     echo R3 ;;

        ts/src/*|ts/test/*|ts/*)                     echo R2 ;;
        Sentinel_Protocol_Lab_Proposal_v0_2.md)      echo R2 ;;
        *)                                           echo UNASSIGNED ;;
    esac
}

# THE SIBLING OF R1-F2, AND IT WAS MISSED BY R1-F2's OWN REPAIR (V3-N1, D-057(5)).
#
# R1-F2's argument is "a coverage instrument must never report coverage it did not measure".
# That repair guarded the `git diff` path and left this one — `git ls-files` in the identical
# unguarded process-substitution shape, one block above it. A verifier failed `ls-files` with a
# PATH shim and got `assigned 0 of 0 tracked files` plus, byte-identical to the sentence R1-F2
# was filed against, `0 file(s) changed since A-070, all assigned`, exit 0.
#
# **Fixing the branch a reviewer demonstrated and leaving its sibling is the exact defect this
# repository has now recorded more times than any other**, committed inside the repair for it.
# NUL-DELIMITED so a filename carrying a newline, a quote or a non-ASCII byte cannot be split,
# nor octal-escaped by core.quotePath into a token nothing can open (Batch A1 case 9). A temp
# file rather than $(...) because command substitution STRIPS NUL bytes, and rather than
# mapfile because this runs under bash 3.2 where mapfile does not exist.
_scope_out="$(mktemp "${TMPDIR:-/tmp}/sentinel-scope.XXXXXXXX")"
_scope_err="$(mktemp "${TMPDIR:-/tmp}/sentinel-scope-err.XXXXXXXX")"
if ! git ls-files -z >"$_scope_out" 2>"$_scope_err"; then
    echo "  FAIL  git ls-files failed:"
    printf '    %s\n' "$(cat "$_scope_err")"
    echo "    Refusing to report a partition measured against nothing."
    rm -f "$_scope_out" "$_scope_err"; exit 1
fi
tracked_files=()
while IFS= read -r -d '' _f; do tracked_files+=("$_f"); done < "$_scope_out"
rm -f "$_scope_out" "$_scope_err"
if [ "${#tracked_files[@]}" -eq 0 ]; then
    echo "  FAIL  git ls-files returned NO tracked files."
    echo "    A repository with nothing in it is not a repository whose every file is assigned."
    exit 1
fi

declare -a unassigned=()
r1=0; r2=0; r3=0
while IFS= read -r f; do
    case "$(assign "$f")" in
        R1) r1=$((r1+1)) ;;
        R2) r2=$((r2+1)) ;;
        R3) r3=$((r3+1)) ;;
        *)  unassigned+=("$f") ;;
    esac
done < <(printf '%s\n' "${tracked_files[@]}")

total=$((r1 + r2 + r3))
echo "review scope: R1=$r1  R2=$r2  R3=$r3  (assigned $total of ${#tracked_files[@]} tracked files)"

if [ ${#unassigned[@]} -ne 0 ]; then
    echo "  FAIL  ${#unassigned[@]} tracked file(s) assigned to NO reviewer:"
    printf '    %s\n' "${unassigned[@]}"
    echo "  The claims surface is covered by this partition or it is not covered. Assign them."
    exit 1
fi

# --- The other half of D-056(d): every file touched since A-070 must be assigned. ---
#
# Stated separately because "every tracked file is assigned" is satisfiable by a partition that
# nobody checked against the actual remediation, and the remediation is what has not been
# independently reviewed at all.
# R1-F2 (D-055(e), CONFIRMED; HIGH -> MEDIUM countersigned by John at D-057(2)).
#
# THE ARGUMENT: **a coverage instrument must never report coverage it did not measure.** This
# block printed "0 file(s) changed since A-070, all assigned" and exited 0 whenever the base ref
# failed to resolve — `git diff`'s stderr was discarded and its exit status was unreachable
# through process substitution, so measuring NOTHING was indistinguishable from measuring a
# clean tree. Absence read as agreement, in the one instrument standing behind this review's
# coverage claim.
#
# A FULL IMMUTABLE BASE, not an abbreviated one. `a89c255~1` was both abbreviated (ambiguous as
# the repository grows) and relative (`~1` silently re-resolves if history is rewritten). This
# is the full 40-character object name of A-070's parent, pinned.
SCOPE_BASE_DEFAULT="140c59e5aa8feab72831534886fda4048cff8fe7"
since="${SENTINEL_SCOPE_BASE:-$SCOPE_BASE_DEFAULT}"

# FAIL CLOSED, in two separate ways, because they are two separate failures.
if ! git rev-parse --verify --quiet "${since}^{commit}" >/dev/null; then
    echo "  FAIL  scope base '$since' does not resolve to a commit."
    echo "    Refusing to print a remediation surface measured against nothing. A base that"
    echo "    cannot be resolved is not an empty diff."
    exit 1
fi

_diff_out="$(mktemp "${TMPDIR:-/tmp}/sentinel-diff.XXXXXXXX")"
_diff_err="$(mktemp "${TMPDIR:-/tmp}/sentinel-diff-err.XXXXXXXX")"
if ! git diff -z --name-only "$since"..HEAD >"$_diff_out" 2>"$_diff_err"; then
    echo "  FAIL  git diff against '$since' failed:"
    printf '    %s\n' "$(cat "$_diff_err")"
    rm -f "$_diff_out" "$_diff_err"; exit 1
fi
scope_files=()
while IFS= read -r -d '' _f; do scope_files+=("$_f"); done < "$_diff_out"
rm -f "$_diff_out" "$_diff_err"

# PRESERVATION IS NOT REMEDIATION, and conflating them would overstate what needs reviewing.
# The round-six record is historical evidence, faithfully preserved with disclosed path
# sanitization: it changes no behaviour and repairs nothing. Counting its files in "the
# remediation surface" would inflate that number with documents nobody is being asked to
# review as work. NOT all of them are byte-identical -- the common brief and the two reviewer
# indexes had machine paths sanitized, each disclosed in that directory's README -- so
# "verbatim" would be the wrong word for the set as a whole. Both are still ASSIGNED --
# they are in R1's scope and R1 should read them -- they are just counted apart.
preservation_only() {
    case "$1" in
        docs/review-2026-08-18-round-six/*) return 0 ;;
        # The D-055(e) record. Preservation for the same reason: it is the review's own
        # evidence, sanitized only for paths, and it repairs nothing. Its FINDINGS-LEDGER.tsv
        # is data the checker in scripts/check-findings-ledger.sh reads, not behaviour.
        docs/review-2026-08-18-d055e/*) return 0 ;;
        *) return 1 ;;
    esac
}

touched=0
preserved=0
_um_failed=0
_um_last=""
while IFS= read -r f; do
    [ -n "$f" ] || continue
    # V3-N1. This read `... || continue`, converting EVERY git failure mode into "deleted
    # since; not in scope" — upstream of the UNASSIGNED check below, so a swallowed file was
    # UNCHECKED, not merely uncounted. With ls-files failing it printed "0 file(s) changed
    # ... all assigned", exit 0. AN INSTRUMENT FAILURE IS NOT A DELETION: --error-unmatch
    # exits 1 when the path is genuinely absent from the index, and 128 when git itself failed.
    if _um_err="$(git ls-files --error-unmatch -- "$f" 2>&1 >/dev/null)"; then
        _um_rc=0
    else
        _um_rc=$?
    fi
    if [ "$_um_rc" -eq 1 ]; then
        continue                                  # genuinely not in the index: deleted since
    elif [ "$_um_rc" -ne 0 ]; then
        # THE INSTRUMENT FAILED, WHICH IS NOT A DELETION. Refuse — but do not refuse by
        # discarding a measurement that IS established: the tracked enumeration above
        # succeeded, so membership is answerable without this call. Fall back to it, finish
        # the walk, report the surface, and THEN refuse naming the failed instrument. A
        # refusal that also destroys a sound count teaches a reader nothing about which of
        # the two went wrong.
        _um_failed=1
        _um_last="$_um_err"
        _present=0
        _j=0
        while [ "$_j" -lt "${#tracked_files[@]}" ]; do
            if [ "${tracked_files[$_j]}" = "$f" ]; then _present=1; break; fi
            _j=$((_j + 1))
        done
        [ "$_present" -eq 1 ] || continue
    fi
    who="$(assign "$f")"
    if [ "$who" = "UNASSIGNED" ]; then
        echo "  FAIL  touched since A-070 and unassigned: $f"
        exit 1
    fi
    if preservation_only "$f"; then preserved=$((preserved+1)); else touched=$((touched+1)); fi
done < <(printf '%s\n' ${scope_files[@]+"${scope_files[@]}"})
# NAME THE BASE ACTUALLY USED, not a fixed label. The line said "since A-070" whatever
# `SENTINEL_SCOPE_BASE` was set to, so an override produced a true count under a false label
# (V3-N1, LOW).
_scope_label="A-070's parent"
[ "$since" = "$SCOPE_BASE_DEFAULT" ] || _scope_label="$since"
echo "  remediation surface: $touched file(s) changed since $_scope_label, all assigned"
if [ "$preserved" -gt 0 ]; then
    echo "  preservation-only:   $preserved file(s) (round-six record; faithfully preserved with"
    echo "                       disclosed path sanitization, no behaviour)"
fi

echo "  reviewer 4 is unassigned BY DESIGN (D-056(d)) and ranges over every surface above"

if [ "$_um_failed" -ne 0 ]; then
    echo "  FAIL  git ls-files --error-unmatch failed during the scope walk."
    printf '    %s\n' "$_um_last"
    echo "    The surface above is measured from the enumeration that DID succeed."
    echo "    Refusing anyway: an instrument failure is not a deletion (V3-N1)."
    exit 1
fi
