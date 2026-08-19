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
# below, and **this exits non-zero if any tracked file is assigned to NO reviewer.** A file
# added between now and dispatch turns this red rather than sliding into a gap. That is the
# difference between a manifest and a claim about one.
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

cd "$(git rev-parse --show-toplevel)"

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

declare -a unassigned=()
r1=0; r2=0; r3=0
while IFS= read -r f; do
    case "$(assign "$f")" in
        R1) r1=$((r1+1)) ;;
        R2) r2=$((r2+1)) ;;
        R3) r3=$((r3+1)) ;;
        *)  unassigned+=("$f") ;;
    esac
done < <(git ls-files)

total=$((r1 + r2 + r3))
echo "review scope: R1=$r1  R2=$r2  R3=$r3  (assigned $total of $(git ls-files | wc -l | tr -d ' ') tracked files)"

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
since="${SENTINEL_SCOPE_BASE:-a89c255~1}"

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
while IFS= read -r f; do
    [ -n "$f" ] || continue
    git ls-files --error-unmatch "$f" >/dev/null 2>&1 || continue   # deleted since; not in scope
    who="$(assign "$f")"
    if [ "$who" = "UNASSIGNED" ]; then
        echo "  FAIL  touched since A-070 and unassigned: $f"
        exit 1
    fi
    if preservation_only "$f"; then preserved=$((preserved+1)); else touched=$((touched+1)); fi
done < <(git diff --name-only "$since"..HEAD 2>/dev/null)
echo "  remediation surface: $touched file(s) changed since A-070, all assigned"
if [ "$preserved" -gt 0 ]; then
    echo "  preservation-only:   $preserved file(s) (round-six record; faithfully preserved with"
    echo "                       disclosed path sanitization, no behaviour)"
fi

echo "  reviewer 4 is unassigned BY DESIGN (D-056(d)) and ranges over every surface above"
