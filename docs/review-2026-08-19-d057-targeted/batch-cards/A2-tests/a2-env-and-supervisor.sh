#!/usr/bin/env bash
# BATCH A1 ATTEMPT TWO — falsification harness for supervisor-root propagation, git-environment
# isolation, and the staged rename/typechange enumeration.
#
# AUTHORITY: D-061(2) and D-061(4). This file is a TEST. It makes no production repair, modifies
# no entry point, and does NOT modify the attempt-one harness `a1-repo-identity.sh`, which is a
# separate deliverable and stays byte-identical (its sha256 is recorded in RESULTS.md).
#
# WHAT IT ASSERTS, from the confirmed obligations:
#   A  12-F1  scripts/test.sh must gate the repository established by its REAL supervisor path,
#             never a shape-compatible caller repository. Identity may NOT be validated by the
#             presence of filenames alone (D-061(3)).
#   B  12-F2  no caller-provided git environment variable may redirect any entry point's
#             body-level git operations. Exercised SEPARATELY for GIT_DIR, GIT_WORK_TREE,
#             GIT_DIR+GIT_WORK_TREE, GIT_INDEX_FILE, GIT_COMMON_DIR and GIT_PREFIX.
#   C  R1     staged rename and typechange records fall out of `--diff-filter=ACM`, so the
#             destination is never scanned. ADJUDICATED CONFIRMED — see R1-ADJUDICATION.md.
#             Entering attempt two is John's call under D-061(2); this harness supplies the
#             reproduction and the assertions, not the authorisation.
#
# HOW TO READ THE OUTPUT. Every scored line is one of
#   REQUIRED  — an assertion of the required behaviour. At this branch tip the confirmed
#               defects make several of these FAIL. That is the point; a REQUIRED line that
#               cannot fail is worthless.
#   CONTROL   — an assertion that the probe is alive and discriminating: the paired situation
#               that must behave OPPOSITELY, or the liveness evidence that the fixture, the
#               scorer or the injected variable does anything at all. A failing CONTROL means
#               the harness is measuring nothing and NO conclusion may be drawn beside it.
#   OBSERVED  — a recorded fact. Asserts NOTHING and counts toward neither tally, so that a
#               fact worth keeping cannot be misread as a behaviour that passed.
#
# EXIT STATUS
#   0  every REQUIRED and every CONTROL held
#   1  REQUIRED failures, all CONTROLs held      (expected at this branch tip)
#   2  a CONTROL failed, or a preflight failed   (the harness is untrustworthy — fix it first)
#
# ISOLATION. Nothing here writes to the repository under test. Every case operates on a private
# clone or on scratch repositories this script created under TMPDIR, and everything is removed
# on exit. Git configuration is NEVER written into a repository this script did not create; the
# operator's own global, system and XDG git configuration is redirected into the scratch area
# for every scored run and its fingerprint is asserted unchanged at the end.
#
# FIXTURES. The planted credentials are obviously fake: a single hex character repeated 64
# times, assembled at run time rather than written as a literal, so this file carries no
# credential-shaped content into a repository guarded by check-secrets.sh.
#
# METHOD NOTES THAT COST SOMETHING TO LEARN, recorded so the next author does not re-pay:
#   * /usr/bin/grep, never the shell's grep — the wrapper on this workstation honours
#     --ignore-files and can return a clean-looking zero. P1 plants a canary to prove it.
#   * `cd ""` returns 0 and does not abort even under `set -euo pipefail`.
#   * command substitution STRIPS NUL bytes, so every NUL-delimited git enumeration is read
#     from a file, never from `$(...)`.
#   * git EXPORTS git environment variables while a hook runs, so a hook's own children inherit
#     them unless the hook clears them.
#   * bash 3.2: no mapfile, no associative arrays, and `"${arr[@]}"` on an EMPTY array is an
#     unbound-variable error under `set -u` — hence the `${arr[@]+"${arr[@]}"}` spelling.
#   * `timeout` is not present on this platform; long children are bounded with a wait loop.

set -uo pipefail

# ---------------------------------------------------------------------------- preamble ------
BRANCH_TIP="a6848d4d00775006fc663c8380e9adf335e9ce66"

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
    printf '  case %-5s %-8s %s  %s\n' "$case_id" "$kind" "$status" "$desc"
    MATRIX_TSV="${MATRIX_TSV}${case_id}	${kind}	${status}	${desc}
"
    if [ "$held" -ne 0 ] && [ "$kind" != "OBSERVED" ]; then
        if [ "$kind" = "REQUIRED" ]; then req_fail=$((req_fail + 1)); else ctl_fail=$((ctl_fail + 1)); fi
    fi
}

die() { printf '\n  PREFLIGHT FAILED: %s\n' "$1"; exit 2; }

# The 16 entry points the A1 card enumerates, as repository-relative paths.
EP16="scripts/check-class-coverage.sh scripts/check-eval-codes.sh scripts/check-findings-ledger.sh
scripts/check-gate-immutability.sh scripts/check-label-integrity.sh scripts/check-label-prompt.sh
scripts/check-rename-gate.sh scripts/check-review-scope.sh scripts/check-secrets.sh
scripts/check-suite-floors.sh scripts/check-type-strings.sh scripts/check-vendor-honesty.sh
scripts/install-hooks.sh scripts/mutate.sh scripts/test.sh .githooks/pre-commit"

# The six caller-provided git environment configurations, exercised SEPARATELY (D-061(2)).
CONFIGS="none gitdir worktree both index common prefix"

fake_hex64() {
    local ch="${1:-b}" i out=""
    case "$ch" in [0-9a-fA-F]) : ;; *) echo "fake_hex64: '$ch' is not a hex digit" >&2; return 1 ;; esac
    i=0
    while [ "$i" -lt 64 ]; do out="${out}${ch}"; i=$((i + 1)); done
    printf '%s' "$out"
}
write_fixture() {   # $1 destination path, $2 fill character
    printf 'export const signerKey = "0x%s";\n' "$(fake_hex64 "$2")" > "$1"
}

# ---------------------------------------------------------------------------- preflight ------
hdr "preflight — refuse to run a harness that cannot fail"

[ -d "$ROOT/.git" ] || [ -f "$ROOT/.git" ] || die "no repository at the given root"
[ -x "$ROOT/scripts/check-secrets.sh" ] || die "root has no scripts/check-secrets.sh"

REAL_GIT="$(command -v git)" || die "git not on PATH"
ROOT_SHA="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null)" || die "cannot read HEAD"
say "repository under test is at $ROOT_SHA"
if [ "$ROOT_SHA" != "$BRANCH_TIP" ]; then
    say "WARNING: that is NOT the branch tip this harness was demonstrated on ($BRANCH_TIP)."
    say "         Outcomes below are evidence about $ROOT_SHA and nothing else."
fi

WORK="$(mktemp -d "${TMPDIR:-/tmp}/a2-env-supervisor.XXXXXXXX")" || die "mktemp failed"
trap 'rm -rf "$WORK"' EXIT

# P1 — the /usr/bin/grep canary.
printf 'A2-CANARY-STRING\n' > "$WORK/canary"
if [ "$(/usr/bin/grep -c 'A2-CANARY-STRING' "$WORK/canary" 2>/dev/null)" != "1" ]; then
    die "/usr/bin/grep did not find a planted canary — no zero result below can be trusted"
fi
say "P1 /usr/bin/grep canary found"

# P2 — the isolated subject. Every case runs against this clone, never the real tree.
SUT="$WORK/sut"
git clone -q --no-hardlinks "$ROOT" "$SUT" >/dev/null 2>&1 || die "clone of the repository under test failed"
git -C "$SUT" fetch -q "$ROOT" HEAD >/dev/null 2>&1 || die "fetch of HEAD into the clone failed"
git -C "$SUT" checkout -q --detach FETCH_HEAD >/dev/null 2>&1 || die "checkout of HEAD in the clone failed"
git -C "$SUT" config user.email "a2-harness@example.invalid"
git -C "$SUT" config user.name "A2 harness"
SUT_SHA="$(git -C "$SUT" rev-parse HEAD)"
[ "$SUT_SHA" = "$ROOT_SHA" ] || die "clone is at $SUT_SHA, not $ROOT_SHA"
SUT_ROOT="$(git -C "$SUT" rev-parse --show-toplevel)"
say "P2 isolated clone of the subject at $SUT_SHA"

# P3 — the redirected environment. HOME, the global/system/XDG git configuration and the
#      terminal prompt are all pointed into scratch, so nothing any case attempts can reach the
#      operator's configuration. Asserted unchanged at the end (case Z1).
A2HOME="$WORK/home"; mkdir -p "$A2HOME/.config"
BASEENV=(HOME="$A2HOME"
         GIT_CONFIG_GLOBAL="$A2HOME/.gitconfig"
         GIT_CONFIG_SYSTEM="$A2HOME/.gitconfig-system"
         XDG_CONFIG_HOME="$A2HOME/.config"
         GIT_TERMINAL_PROMPT=0)
opcfg_fp() {
    { cat "$A2HOME/.gitconfig"        2>/dev/null || echo ABSENT-global
      cat "$A2HOME/.gitconfig-system" 2>/dev/null || echo ABSENT-system
      find "$A2HOME/.config" -type f -exec cat {} + 2>/dev/null || echo ABSENT-xdg
      git -C "$ROOT" config --local --list 2>/dev/null || echo NO-LOCAL
    } | shasum -a 256 | cut -d' ' -f1
}
OPCFG_BEFORE="$(opcfg_fp)"
say "P3 global/system/XDG git configuration redirected into the scratch area"

# P4 — the child shim. Network-capable and expensive children are replaced by a recorder that
#      does no work. REACHING ONE IS AN INSTRUMENT FACT, recorded, never scored as a refusal.
SHIM="$WORK/shim"; mkdir -p "$SHIM"
SHIM_HITS="$WORK/shim.hits"; : > "$SHIM_HITS"
for c in forge anvil cast chisel npm npx cargo curl wget gh pip3 yarn pnpm ssh nc; do
    cat > "$SHIM/$c" <<SHM
#!/usr/bin/env bash
printf '%s %s\n' "$c" "\$*" >> "$SHIM_HITS"
echo "a2 shim: '$c' was reached — instrument fact, not a result" >&2
exit 97
SHM
    chmod +x "$SHIM/$c"
done
SHIMPATH="$SHIM:$PATH"
say "P4 15 expensive/network children shimmed to a recorder"

# P5 — the decoy repository the caller-provided variables point at. Created here; the harness
#      never points a variable at a repository it did not make.
DEC="$WORK/decoy"
git -c init.defaultBranch=main init -q "$DEC" || die "cannot create the decoy repository"
git -C "$DEC" config user.email "a2-harness@example.invalid"
git -C "$DEC" config user.name "A2 harness"
printf 'a decoy repository, created by the A2 harness\n' > "$DEC/DECOY-ONLY.md"
git -C "$DEC" add -A >/dev/null; git -C "$DEC" commit -qm "decoy base" >/dev/null
DEC_N="$(git -C "$DEC" ls-files | /usr/bin/grep -c '')"
SUT_N="$(git -C "$SUT" ls-files | /usr/bin/grep -c '')"
[ "$DEC_N" -lt "$SUT_N" ] || die "the decoy is not distinguishable from the subject by file count"
say "P5 decoy repository created ($DEC_N tracked file, subject has $SUT_N)"

# The configuration table. EA is filled by set_cfg; bash 3.2 has no associative arrays.
EA=()
set_cfg() {
    EA=()
    case "$1" in
        none)     : ;;
        gitdir)   EA=("GIT_DIR=$DEC/.git") ;;
        worktree) EA=("GIT_WORK_TREE=$DEC") ;;
        both)     EA=("GIT_DIR=$DEC/.git" "GIT_WORK_TREE=$DEC") ;;
        index)    EA=("GIT_INDEX_FILE=$DEC/.git/index") ;;
        common)   EA=("GIT_COMMON_DIR=$DEC/.git") ;;
        prefix)   EA=("GIT_PREFIX=a2-caller-prefix/") ;;
        *) die "unknown configuration '$1'" ;;
    esac
}
cfg_label() {
    case "$1" in
        none)     printf 'no caller variables (CONTROL)' ;;
        gitdir)   printf 'GIT_DIR only' ;;
        worktree) printf 'GIT_WORK_TREE only' ;;
        both)     printf 'GIT_DIR + GIT_WORK_TREE' ;;
        index)    printf 'GIT_INDEX_FILE only' ;;
        common)   printf 'GIT_COMMON_DIR only' ;;
        prefix)   printf 'GIT_PREFIX only' ;;
    esac
}
# Run a command inside the subject under one configuration, with the redirected environment.
run_cfg() {   # $1 configuration, rest: command and arguments
    local c="$1"; shift
    set_cfg "$c"
    ( cd "$SUT" && env "${BASEENV[@]}" ${EA[@]+"${EA[@]}"} PATH="$SHIMPATH" "$@" 2>&1 )
}

reset_sut() {
    git -C "$SUT" reset -q --hard "$SUT_SHA" >/dev/null 2>&1
    git -C "$SUT" clean -qfd >/dev/null 2>&1
    git -C "$SUT" config core.hooksPath .githooks
}

# P6 — the credential fixture must actually trip the guard, in BOTH modes, or every clean
#      result below would be vacuous for a reason that has nothing to do with the defect.
write_fixture "$SUT/a2-preflight.ts" f
git -C "$SUT" add a2-preflight.ts >/dev/null
( cd "$SUT" && ./scripts/check-secrets.sh >/dev/null 2>&1 ); p6d=$?
( cd "$SUT" && ./scripts/check-secrets.sh --staged >/dev/null 2>&1 ); p6s=$?
reset_sut
[ "$p6d" -ne 0 ] || die "the planted credential does NOT trip check-secrets.sh in default mode"
[ "$p6s" -ne 0 ] || die "the planted credential does NOT trip check-secrets.sh in --staged mode"
say "P6 the planted credential trips check-secrets.sh in both modes (default=$p6d staged=$p6s)"

# P7 — each injected configuration must actually DO something to git, or a REQUIRED line that
#      passes under it proves nothing. Measured, not assumed: some of these are inert on this
#      git and that is recorded rather than hidden.
INERT_CFGS=""
for c in $CONFIGS; do
    [ "$c" = "none" ] && continue
    top="$( run_cfg "$c" git rev-parse --show-toplevel )"
    n="$( run_cfg "$c" git ls-files | /usr/bin/grep -c '' )"
    cv="$( run_cfg "$c" git config --get a2probe.canary )"
    git -C "$DEC" config a2probe.canary DECOY-CONFIG-REACHED
    cv2="$( run_cfg "$c" git config --get a2probe.canary )"
    git -C "$DEC" config --unset a2probe.canary
    eff=""
    [ "$top" = "$SUT_ROOT" ] || eff="${eff}toplevel "
    [ "$n" = "$SUT_N" ]      || eff="${eff}file-list "
    [ -z "$cv2" ]            || eff="${eff}config "
    if [ -z "$eff" ]; then
        INERT_CFGS="$INERT_CFGS $c"
        say "P7 $c: NO observable redirection on this git — required lines under it are recorded as inert"
    else
        say "P7 $c: redirects [$eff]"
    fi
done
say "P7 inert configurations:${INERT_CFGS:- none}"

# P8 — the subject is deterministic for the two guards the outcome cases score.
( cd "$SUT" && ./scripts/check-secrets.sh >/dev/null 2>&1 ); q1=$?
( cd "$SUT" && ./scripts/check-secrets.sh >/dev/null 2>&1 ); q2=$?
[ "$q1" = "$q2" ] || die "check-secrets.sh is not deterministic on a clean subject ($q1 then $q2)"
say "P8 the clean subject gives a stable answer (exit $q1 twice)"

# ======================================================================= GROUP A =============
hdr "GROUP A (12-F1) — the gate must use the repository its REAL SUPERVISOR PATH establishes"

# THE FIXTURE. A brand-new unrelated repository that satisfies the structural test the body
# performs today — an EMPTY scripts/test.sh and an EMPTY .githooks/pre-commit — plus a decoy
# for every check script name, each of which drops a marker and exits 0. No environment
# manipulation, no privileged access, no unusual setup: the gate is simply invoked by absolute
# path with the caller standing inside it.
FSUP="$WORK/foreign-super"; MARK="$WORK/markers"; mkdir -p "$MARK"
git -c init.defaultBranch=main init -q "$FSUP" || die "cannot create the foreign supervisor fixture"
git -C "$FSUP" config user.email "a2-harness@example.invalid"
git -C "$FSUP" config user.name "A2 harness"
mkdir -p "$FSUP/scripts" "$FSUP/.githooks"
: > "$FSUP/scripts/test.sh"
: > "$FSUP/.githooks/pre-commit"
printf 'a foreign repository created by the A2 harness\n' > "$FSUP/README.md"
DECOY_NAMES="class-coverage eval-codes findings-ledger gate-immutability label-integrity
label-prompt rename-gate review-scope secrets suite-floors type-strings vendor-honesty"
for n in $DECOY_NAMES; do
    cat > "$FSUP/scripts/check-$n.sh" <<DEC_EOF
#!/usr/bin/env bash
: > "$MARK/$n"
echo "A2-CALLER-DECOY check-$n EXECUTED"
exit 0
DEC_EOF
    chmod +x "$FSUP/scripts/check-$n.sh"
done
git -C "$FSUP" add -A >/dev/null; git -C "$FSUP" commit -qm "foreign lookalike" >/dev/null

fs_fp() { ( cd "$FSUP" && { find . | LC_ALL=C sort
                            find . -type f -exec shasum -a 256 {} + | LC_ALL=C sort
                          } | shasum -a 256 | cut -d' ' -f1 ); }

# A0 — the decoys are live. If a decoy cannot drop a marker, "zero markers" means nothing.
rm -f "$MARK"/*
"$FSUP/scripts/check-secrets.sh" >/dev/null 2>&1
a0="$(ls -1 "$MARK" 2>/dev/null | /usr/bin/grep -c '')"
if [ "$a0" -eq 1 ]; then held=0; else held=1; fi
check CONTROL A0 "$held" "a caller decoy drops a marker when it is actually executed ($a0 marker(s)) — the marker mechanism is live"

# A0b — the fixture really is a git repository that satisfies the two-path structural test.
if [ -e "$FSUP/scripts/test.sh" ] && [ -e "$FSUP/.githooks/pre-commit" ] \
   && [ ! -s "$FSUP/scripts/test.sh" ] && [ ! -s "$FSUP/.githooks/pre-commit" ] \
   && ( cd "$FSUP" && git rev-parse --show-toplevel >/dev/null 2>&1 ); then held=0; else held=1; fi
check CONTROL A0b "$held" "the foreign fixture is a repository whose two lookalike files are EMPTY — shape alone, no Sentinel content"

# The gate runs. A credential is planted in the SUBJECT, so the secret-guard stage is a live
# discriminator: whichever tree the gate read, the answer says so out loud.
gate_run() {   # $1 label, $2 caller directory, $3 path to the gate to invoke
    rm -f "$MARK"/*; : > "$SHIM_HITS"
    local f0 f1 c0 c1
    f0="$(fs_fp)"; c0="$(shasum -a 256 "$FSUP/.git/config" | cut -d' ' -f1)"
    gate_out="$( cd "$2" && env "${BASEENV[@]}" PATH="$SHIMPATH" "$3" 2>&1 )"; gate_rc=$?
    f1="$(fs_fp)"; c1="$(shasum -a 256 "$FSUP/.git/config" | cut -d' ' -f1)"
    printf '%s' "$gate_out" > "$WORK/gate-$1.out"
    gate_markers="$(ls -1 "$MARK" 2>/dev/null | /usr/bin/grep -c '')"
    gate_decoy="$(/usr/bin/grep -c 'A2-CALLER-DECOY' "$WORK/gate-$1.out")"
    gate_blocked="$(/usr/bin/grep -c 'BLOCKED a2-supervisor-cred' "$WORK/gate-$1.out")"
    gate_shims="$(/usr/bin/grep -c '' "$SHIM_HITS")"
    gate_fs_same=1; [ "$f0" = "$f1" ] && [ "$c0" = "$c1" ] && gate_fs_same=0
}

reset_sut
write_fixture "$SUT/a2-supervisor-cred.ts" 9

hdr "GROUP A — the gate invoked by absolute path from inside the foreign lookalike"
gate_run foreign "$FSUP" "$SUT/scripts/test.sh"
A_markers="$gate_markers"; A_decoy="$gate_decoy"; A_blocked="$gate_blocked"
A_fs="$gate_fs_same"; A_rc="$gate_rc"; A_shims="$gate_shims"
say "exit=$A_rc  decoy markers=$A_markers  decoy stdout lines=$A_decoy  subject credential blocked=$A_blocked"

if [ "$A_markers" -eq 0 ] && [ "$A_decoy" -eq 0 ]; then held=0; else held=1; fi
check REQUIRED A1 "$held" "ZERO caller decoys execute ($A_markers marker(s), $A_decoy decoy line(s) in the gate's own output)"
if [ "$A_blocked" -ge 1 ]; then held=0; else held=1; fi
check REQUIRED A2 "$held" "the gate's secret-guard stage read SENTINEL's tree — the credential planted in the subject is blocked ($A_blocked)"
check REQUIRED A3 "$A_fs" "the foreign repository is unchanged — worktree fingerprint and .git/config both byte-identical"

hdr "GROUP A (CONTROL) — the same gate invoked ordinarily from Sentinel's own root"
gate_run sentinel "$SUT" "$SUT/scripts/test.sh"
B_markers="$gate_markers"; B_blocked="$gate_blocked"; B_rc="$gate_rc"
say "exit=$B_rc  decoy markers=$B_markers  subject credential blocked=$B_blocked  shim hits=$gate_shims"
if [ "$B_markers" -eq 0 ] && [ "$B_blocked" -ge 1 ]; then held=0; else held=1; fi
check CONTROL A4 "$held" "from Sentinel's root the gate runs SENTINEL's children and blocks the planted credential ($B_markers markers, blocked=$B_blocked) — the discriminator is live"
stages_f="$(/usr/bin/grep -c '== ' "$WORK/gate-foreign.out")"
stages_s="$(/usr/bin/grep -c '== ' "$WORK/gate-sentinel.out")"
check OBSERVED A4s 0 "both invocations reach the same stage count (foreign=$stages_f, Sentinel=$stages_s) and both exit $A_rc/$B_rc — THE EXIT STATUS IS NOT A DISCRIMINATOR HERE (see COVERAGE.md §2: no completing gate run is available in this worktree)"

hdr "GROUP A (CONTROL) — a COPY of the gate outside every Sentinel repository"
# The copy is placed with its scripts/ structure preserved, beside caller decoys, in a directory
# inside NO repository. The refusal must come BEFORE any child executes.
OUTS="$WORK/outside/scripts"; mkdir -p "$OUTS"
cp "$SUT/scripts/test.sh" "$OUTS/test.sh"; chmod +x "$OUTS/test.sh"
mkdir -p "$WORK/outside/.githooks"; : > "$WORK/outside/.githooks/pre-commit"
for n in $DECOY_NAMES; do
    cat > "$OUTS/check-$n.sh" <<DEC_EOF2
#!/usr/bin/env bash
: > "$MARK/$n"
echo "A2-CALLER-DECOY check-$n EXECUTED"
exit 0
DEC_EOF2
    chmod +x "$OUTS/check-$n.sh"
done
if ( cd "$WORK/outside" && git rev-parse --show-toplevel >/dev/null 2>&1 ); then
    check CONTROL A5f 1 "the 'outside' layout is inside a git repository — control A5 would measure nothing"
else
    check CONTROL A5f 0 "the 'outside' layout is inside no git repository — the premise is instantiated"
fi
rm -f "$MARK"/*; : > "$SHIM_HITS"
out5="$( cd "$WORK/outside" && env "${BASEENV[@]}" PATH="$SHIMPATH" ./scripts/test.sh 2>&1 )"; rc5=$?
printf '%s' "$out5" > "$WORK/gate-outside.out"
m5="$(ls -1 "$MARK" 2>/dev/null | /usr/bin/grep -c '')"
# A dedicated identity refusal: a refusal verb AND a repository-identity condition, on one line.
is_ident_refusal() {
    printf '%s\n' "$1" \
      | /usr/bin/grep -Ei 'refus(e|ed|es|ing)|declin(e|ed|es|ing)' \
      | /usr/bin/grep -Eiq 'sentinel repositor|repository identit|identity mismatch|repository root|own location|invoking repositor|another repositor|foreign repositor|(is |was )?(not inside|outside) the sentinel|cannot (establish|determine|resolve).*(repositor|identity|location)'
}
if [ "$rc5" -ne 0 ] && [ "$m5" -eq 0 ] && is_ident_refusal "$out5"; then held=0; else held=1; fi
check CONTROL A5 "$held" "a copy of the gate outside every Sentinel repository emits a dedicated identity refusal BEFORE any child runs (exit $rc5, $m5 markers)"

# A6 — the scorer used by A5, probed both ways with lines this harness invented, so no
#      implementation's literal wording is what makes A5 pass.
p1='  FAIL  refusing: the Sentinel repository containing this gate cannot be established.'
p2='cannot determine the repository identity of this gate; declining before running anything.'
p3='guard: this file is not inside the Sentinel repository, so it refuses to report a result.'
if is_ident_refusal "$p1" && is_ident_refusal "$p2" && is_ident_refusal "$p3"; then held=0; else held=1; fi
check CONTROL A6 "$held" "the refusal scorer accepts three invented wordings, not one implementation's literal"
neg=0
while IFS= read -r probe; do
    [ -n "$probe" ] || continue
    is_ident_refusal "$probe" && { neg=1; say "scorer accepted an INCIDENTAL failure: $probe"; }
done <<'NEGPROBES'
bash: ./scripts/check-secrets.sh: No such file or directory
./scripts/test.sh: line 12: forge: command not found
fatal: not a git repository (or any of the parent directories): .git
a2 shim: 'npm' was reached — instrument fact, not a result
findings ledger: MISSING at docs/findings-register.md — refusing to report totals from nothing.
  FAIL  git ls-files failed; refusing to report a clean scan:
NEGPROBES
check CONTROL A6n "$neg" "the refusal scorer rejects missing-file, command-not-found, not-a-repository, shim and non-identity refusals"

reset_sut

# ======================================================================= GROUP B1 ============
hdr "GROUP B1 (12-F2) — check-secrets.sh with the caller's git environment pointed at a decoy"

# The credential is planted in the SENTINEL subject and staged there. The variables point at the
# decoy, which does not contain it. A clean report is therefore a report about content the guard
# never read.
b1_run() {   # $1 configuration
    reset_sut
    write_fixture "$SUT/a2-live-cred.ts" b
    git -C "$SUT" add a2-live-cred.ts >/dev/null
    b1_def="$( run_cfg "$1" ./scripts/check-secrets.sh )"; b1_def_rc=$?
    b1_stg="$( run_cfg "$1" ./scripts/check-secrets.sh --staged )"; b1_stg_rc=$?
    reset_sut
}
for c in $CONFIGS; do
    b1_run "$c"
    lbl="$(cfg_label "$c")"
    dblk=0; printf '%s' "$b1_def" | /usr/bin/grep -q 'BLOCKED a2-live-cred.ts' && dblk=1
    sblk=0; printf '%s' "$b1_stg" | /usr/bin/grep -q 'BLOCKED a2-live-cred.ts' && sblk=1
    dcln=0; printf '%s' "$b1_def" | /usr/bin/grep -q 'secret guard: clean' && dcln=1
    scln=0; printf '%s' "$b1_stg" | /usr/bin/grep -q 'secret guard: clean' && scln=1
    if [ "$c" = "none" ]; then
        if [ "$dblk" -eq 1 ] && [ "$sblk" -eq 1 ]; then held=0; else held=1; fi
        check CONTROL "B1-$c" "$held" "$lbl: the planted credential IS blocked in both modes (default exit $b1_def_rc, staged exit $b1_stg_rc) — the fixture is live"
        continue
    fi
    if [ "$dblk" -eq 1 ]; then held=0; else held=1; fi
    check REQUIRED "B1d-$c" "$held" "$lbl: DEFAULT mode still blocks the credential in Sentinel (exit $b1_def_rc, clean-report=$dcln)"
    if [ "$sblk" -eq 1 ]; then held=0; else held=1; fi
    check REQUIRED "B1s-$c" "$held" "$lbl: --staged mode still blocks the credential in Sentinel (exit $b1_stg_rc, clean-report=$scln)"
    if [ "$dcln" -eq 1 ] || [ "$scln" -eq 1 ]; then
        check OBSERVED "B1c-$c" 0 "$lbl: A CLEAN REPORT WAS PRINTED OVER UNREAD SENTINEL CONTENT (default=$dcln staged=$scln) — the worst shape of this defect"
    fi
    case " $INERT_CFGS " in *" $c "*)
        check OBSERVED "B1i-$c" 0 "$lbl: P7 measured NO observable redirection on this git — the two lines above are inert here, not coverage" ;;
    esac
done

# ======================================================================= GROUP B2 ============
hdr "GROUP B2 (12-F2) — install-hooks.sh against a VICTIM repository, one fresh victim each"

for c in $CONFIGS; do
    [ "$c" = "none" ] && continue
    V="$WORK/victim-$c"
    git -c init.defaultBranch=main init -q "$V"
    git -C "$V" config user.email "a2-harness@example.invalid"
    git -C "$V" config user.name "A2 harness"
    printf 'a victim repository, created by the A2 harness\n' > "$V/README.md"
    git -C "$V" add -A >/dev/null; git -C "$V" commit -qm "victim base" >/dev/null
    # The variables must point at THIS victim, not at the shared decoy.
    case "$c" in
        gitdir)   VE=("GIT_DIR=$V/.git") ;;
        worktree) VE=("GIT_WORK_TREE=$V") ;;
        both)     VE=("GIT_DIR=$V/.git" "GIT_WORK_TREE=$V") ;;
        index)    VE=("GIT_INDEX_FILE=$V/.git/index") ;;
        common)   VE=("GIT_COMMON_DIR=$V/.git") ;;
        prefix)   VE=("GIT_PREFIX=a2-caller-prefix/") ;;
    esac
    vcfg0="$(shasum -a 256 "$V/.git/config" | cut -d' ' -f1)"
    vtree0="$( cd "$V" && find . -path ./.git -prune -o -type f -print | LC_ALL=C sort | shasum -a 256 | cut -d' ' -f1 )"
    git -C "$SUT" config --unset core.hooksPath >/dev/null 2>&1
    out="$( cd "$SUT" && env "${BASEENV[@]}" "${VE[@]}" PATH="$SHIMPATH" ./scripts/install-hooks.sh 2>&1 )"; rc=$?
    vcfg1="$(shasum -a 256 "$V/.git/config" | cut -d' ' -f1)"
    vtree1="$( cd "$V" && find . -path ./.git -prune -o -type f -print | LC_ALL=C sort | shasum -a 256 | cut -d' ' -f1 )"
    vhp="$(git -C "$V" config --local --get core.hooksPath 2>/dev/null || printf 'UNSET')"
    shp="$(git -C "$SUT" config --local --get core.hooksPath 2>/dev/null || printf 'UNSET')"
    lbl="$(cfg_label "$c")"
    if [ "$vcfg0" = "$vcfg1" ] && [ "$vtree0" = "$vtree1" ] && [ "$vhp" = "UNSET" ]; then held=0; else held=1; fi
    check REQUIRED "B2-$c" "$held" "$lbl: the victim's WHOLE .git/config is byte-identical and core.hooksPath stays unset (victim=$vhp, exit $rc)"
    if [ "$rc" -ne 0 ] || [ "$shp" = ".githooks" ]; then held=0; else held=1; fi
    check REQUIRED "B2o-$c" "$held" "$lbl: install-hooks.sh either REFUSED or configured SENTINEL ONLY (exit $rc, Sentinel core.hooksPath=$shp)"
    if [ "$vcfg0" != "$vcfg1" ]; then
        check OBSERVED "B2m-$c" 0 "$lbl: *** THE VICTIM'S CONFIGURATION WAS MUTATED *** (exit $rc) — D-060(2)'s explicit prohibition"
    fi
    rm -rf "$V"
done

# B2 controls. The mechanism must be live in both directions: a fresh victim's configuration
# CAN be written through the variable, and install-hooks against Sentinel still succeeds.
VP="$WORK/victim-proof"
git -c init.defaultBranch=main init -q "$VP"
git -C "$VP" config user.email "a2-harness@example.invalid"; git -C "$VP" config user.name "A2 harness"
printf 'proof victim\n' > "$VP/README.md"; git -C "$VP" add -A >/dev/null; git -C "$VP" commit -qm base >/dev/null
( cd "$SUT" && env "${BASEENV[@]}" GIT_DIR="$VP/.git" git config a2probe.canary REACHED >/dev/null 2>&1 )
vpc="$(git -C "$VP" config --local --get a2probe.canary 2>/dev/null || printf 'UNSET')"
if [ "$vpc" = "REACHED" ]; then held=0; else held=1; fi
check CONTROL B2p "$held" "a caller-provided GIT_DIR really does redirect a git CONFIG WRITE into a victim (canary=$vpc) — B2 is not passing for want of a mechanism"
rm -rf "$VP"

git -C "$SUT" config --unset core.hooksPath >/dev/null 2>&1
out="$( cd "$SUT" && env "${BASEENV[@]}" PATH="$SHIMPATH" ./scripts/install-hooks.sh 2>&1 )"; rc=$?
shp="$(git -C "$SUT" config --local --get core.hooksPath 2>/dev/null || printf 'UNSET')"
if [ "$rc" -eq 0 ] && [ "$shp" = ".githooks" ]; then held=0; else held=1; fi
check CONTROL B2n "$held" "with no caller variables install-hooks.sh against Sentinel still succeeds and sets core.hooksPath (exit $rc, $shp)"
git -C "$SUT" config core.hooksPath .githooks

# ======================================================================= GROUP B3 ============
hdr "GROUP B3 (12-F2) — the pre-commit hook: capture the invoker, then clear before executing"

# B3a — the MATCHING repository, with hook-shaped variables present as a wrapper, a CI step or
#       `git filter-branch` supplies them. The hook's identity comparison matches, so it
#       proceeds — and its child must scan SENTINEL's staged content, not the decoy's.
for c in $CONFIGS; do
    reset_sut
    write_fixture "$SUT/a2-hook-cred.ts" 7
    git -C "$SUT" add a2-hook-cred.ts >/dev/null
    out="$( run_cfg "$c" ./.githooks/pre-commit )"; rc=$?
    lbl="$(cfg_label "$c")"
    blk=0; printf '%s' "$out" | /usr/bin/grep -q 'BLOCKED a2-hook-cred.ts' && blk=1
    cln=0; printf '%s' "$out" | /usr/bin/grep -q 'secret guard: clean' && cln=1
    ref=0; is_ident_refusal "$out" && ref=1
    if [ "$c" = "none" ]; then
        if [ "$blk" -eq 1 ] && [ "$rc" -ne 0 ]; then held=0; else held=1; fi
        check CONTROL "B3-$c" "$held" "$lbl: the hook blocks a staged credential in the matching repository (exit $rc) — the fixture is live"
        continue
    fi
    # Blocked is the required outcome; a dedicated identity refusal is also fail-closed and is
    # accepted, because refusing to act on an environment it cannot trust is not a defect.
    if [ "$blk" -eq 1 ] || { [ "$ref" -eq 1 ] && [ "$rc" -ne 0 ]; }; then held=0; else held=1; fi
    check REQUIRED "B3-$c" "$held" "$lbl: the hook blocks the staged credential or refuses (exit $rc, blocked=$blk refusal=$ref clean-report=$cln)"
    if [ "$cln" -eq 1 ] && [ "$rc" -eq 0 ]; then
        check OBSERVED "B3c-$c" 0 "$lbl: *** THE HOOK REPORTED CLEAN AND EXITED 0 OVER A LIVE STAGED CREDENTIAL ***"
    fi
done
reset_sut

# B3b — the MISMATCH, with a caller-provided script sitting where the hook would look for one.
#       The refusal must be taken before that script can run. (This shape holds at this SHA;
#       it is asserted so a repair cannot lose it.)
FH="$WORK/foreign-hook"
git -c init.defaultBranch=main init -q "$FH"
git -C "$FH" config user.email "a2-harness@example.invalid"; git -C "$FH" config user.name "A2 harness"
printf 'foreign\n' > "$FH/README.md"; git -C "$FH" add -A >/dev/null; git -C "$FH" commit -qm base >/dev/null
git -C "$FH" config core.hooksPath "$SUT/.githooks"
mkdir -p "$FH/scripts"
cat > "$FH/scripts/check-secrets.sh" <<HDEC
#!/usr/bin/env bash
: > "$MARK/hook-decoy"
echo "A2-HOOK-DECOY-RAN"
exit 0
HDEC
chmod +x "$FH/scripts/check-secrets.sh"
write_fixture "$FH/leak.ts" 1
git -C "$FH" add -A >/dev/null
rm -f "$MARK"/*
out="$( cd "$FH" && env "${BASEENV[@]}" PATH="$SHIMPATH" git commit -m "a2 B3b" 2>&1 )"; rc=$?
ncom="$(git -C "$FH" log --oneline | /usr/bin/grep -c '')"
dran=0; [ -e "$MARK/hook-decoy" ] && dran=1
if [ "$rc" -ne 0 ] && [ "$ncom" -eq 1 ] && [ "$dran" -eq 0 ] && is_ident_refusal "$out"; then held=0; else held=1; fi
check REQUIRED B3b "$held" "on an identity mismatch the hook refuses BEFORE executing the caller's own check script (exit $rc, decoy ran=$dran, commits=$ncom)"

# B3c — the matching-repository control, through a real commit rather than a direct invocation.
reset_sut
printf 'an ordinary note\n' > "$SUT/a2-benign.txt"
git -C "$SUT" add a2-benign.txt >/dev/null
( cd "$SUT" && env "${BASEENV[@]}" PATH="$SHIMPATH" git commit -qm "a2 benign" >/dev/null 2>&1 ); rc_ok=$?
write_fixture "$SUT/a2-commit-cred.ts" 3
git -C "$SUT" add a2-commit-cred.ts >/dev/null
( cd "$SUT" && env "${BASEENV[@]}" PATH="$SHIMPATH" git commit -qm "a2 leak" >/dev/null 2>&1 ); rc_leak=$?
if [ "$rc_ok" -eq 0 ] && [ "$rc_leak" -ne 0 ]; then held=0; else held=1; fi
check CONTROL B3c "$held" "a matching repository still commits benign content (exit $rc_ok) and still BLOCKS a credential through the hook (exit $rc_leak)"
reset_sut

# ======================================================================= GROUP B4 ============
hdr "GROUP B4 (12-F2) — census: does ANY caller-provided git environment survive into a body-level git call?"

# THE CENSUS IS MEASURED, NOT READ OUT OF THE SOURCE. A recording `git` on PATH writes one line
# per invocation naming which caller-provided variables were present in its environment, then
# delegates to the real git VERBATIM, so the run is today's behaviour and not a simulation.
#
# The values injected here are the SUBJECT'S OWN paths. That is deliberate: semantically inert
# values keep every entry point running normally, so the census sees ALL of its body-level git
# calls instead of only the ones before it fails. What is being asserted is that the variables
# are GONE by then, not what they would have done.
CENSUS="$WORK/census.tsv"; : > "$CENSUS"
GSHIM="$WORK/gshim"; mkdir -p "$GSHIM"
cat > "$GSHIM/git" <<'GS'
#!/usr/bin/env bash
carried=""
[ -n "${GIT_DIR:-}" ]        && carried="${carried}GIT_DIR "
[ -n "${GIT_WORK_TREE:-}" ]  && carried="${carried}GIT_WORK_TREE "
[ -n "${GIT_INDEX_FILE:-}" ] && carried="${carried}GIT_INDEX_FILE "
[ -n "${GIT_COMMON_DIR:-}" ] && carried="${carried}GIT_COMMON_DIR "
[ -n "${GIT_PREFIX:-}" ]     && carried="${carried}GIT_PREFIX "
printf '%s\t%s\t%s\n' "${A2_EP:-unknown}" "${carried:--}" "$*" >> "$A2_CENSUS"
exec "$A2_REAL_GIT" "$@"
GS
chmod +x "$GSHIM/git"
export A2_REAL_GIT="$REAL_GIT"

# The scorer. A carrier is any recorded call that had at least one variable present. Reading the
# CALLER's context is a legitimate identity input — the hook needs it to know where the commit is
# happening — so `rev-parse --show-toplevel` carriers are recorded separately and never scored.
# Everything else is a body-level operation and must be clean.
census_work_carriers() {   # $1 entry-point tag
    awk -F'\t' -v ep="$1" '$1==ep && $2!="-" && $3!="rev-parse --show-toplevel"' "$CENSUS" | /usr/bin/grep -c ''
}
census_ident_carriers() {
    awk -F'\t' -v ep="$1" '$1==ep && $2!="-" && $3=="rev-parse --show-toplevel"' "$CENSUS" | /usr/bin/grep -c ''
}
census_total() { awk -F'\t' -v ep="$1" '$1==ep' "$CENSUS" | /usr/bin/grep -c ''; }

# B4s — the scorer, probed both ways with two synthetic entry points this harness wrote. One
#       leaks by construction and one scrubs by construction; if the census cannot tell them
#       apart it is measuring nothing.
mkdir -p "$WORK/synth"
cat > "$WORK/synth/leaky.sh" <<'SY1'
#!/usr/bin/env bash
git ls-files >/dev/null 2>&1
SY1
cat > "$WORK/synth/clean.sh" <<'SY2'
#!/usr/bin/env bash
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
git ls-files >/dev/null 2>&1
SY2
chmod +x "$WORK/synth/leaky.sh" "$WORK/synth/clean.sh"
CENSUS_ENV=(GIT_DIR="$SUT/.git" GIT_WORK_TREE="$SUT_ROOT"
            GIT_INDEX_FILE="$SUT/.git/index" GIT_COMMON_DIR="$SUT/.git"
            GIT_PREFIX=a2-caller-prefix/)
( cd "$SUT" && env "${BASEENV[@]}" "${CENSUS_ENV[@]}" A2_CENSUS="$CENSUS" A2_EP="synth-leaky" \
    PATH="$GSHIM:$SHIMPATH" "$WORK/synth/leaky.sh" >/dev/null 2>&1 )
( cd "$SUT" && env "${BASEENV[@]}" "${CENSUS_ENV[@]}" A2_CENSUS="$CENSUS" A2_EP="synth-clean" \
    PATH="$GSHIM:$SHIMPATH" "$WORK/synth/clean.sh" >/dev/null 2>&1 )
sl="$(census_work_carriers synth-leaky)"; sc="$(census_work_carriers synth-clean)"
if [ "$sl" -ge 1 ] && [ "$sc" -eq 0 ]; then held=0; else held=1; fi
check CONTROL B4s "$held" "the census scores a deliberately leaky body as a carrier ($sl) and a deliberately scrubbed one as clean ($sc) — it can fail, and it can pass"

# The sweep. Every one of the sixteen entry points, run from Sentinel's own root.
# mutate.sh needs a filter that matches nothing, and the hook needs staged content to act on.
census_carry=0; census_eps=""; census_ran=0
for ep in $EP16; do
    reset_sut
    args=()
    case "$ep" in
        scripts/mutate.sh) args=("a2-no-such-mutation-filter") ;;
        .githooks/pre-commit)
            printf 'an ordinary staged note\n' > "$SUT/a2-census-note.txt"
            git -C "$SUT" add a2-census-note.txt >/dev/null ;;
    esac
    tag="$(printf '%s' "$ep" | tr '/' '_')"
    ( cd "$SUT" && env "${BASEENV[@]}" "${CENSUS_ENV[@]}" A2_CENSUS="$CENSUS" A2_EP="$tag" \
        PATH="$GSHIM:$SHIMPATH" "./$ep" ${args[@]+"${args[@]}"} >/dev/null 2>&1 )
    n="$(census_work_carriers "$tag")"; i="$(census_ident_carriers "$tag")"; t="$(census_total "$tag")"
    census_ran=$((census_ran + 1))
    [ "$t" -gt 0 ] && say "$(printf '%-34s' "$ep") git calls=$t  body-level carriers=$n  identity-probe carriers=$i"
    if [ "$n" -gt 0 ]; then census_carry=$((census_carry + 1)); census_eps="$census_eps $ep"; fi
done
reset_sut
check REQUIRED B4 "$census_carry" "no caller-provided git environment survives into a body-level git call in ANY of the 16 entry points ($census_carry entry point(s) carry:${census_eps:- none})"
zero_call=""
for ep in $EP16; do
    tag="$(printf '%s' "$ep" | tr '/' '_')"
    [ "$(census_total "$tag")" -eq 0 ] && zero_call="$zero_call $ep"
done
check OBSERVED B4z 0 "entry points that made NO git call at all under the census, so B4 says nothing about them:${zero_call:- none}"
check OBSERVED B4n 0 "$census_ran of 16 entry points were executed for the census; $(/usr/bin/grep -c '' "$CENSUS") git invocations recorded in total"
# The exemption must not hide anything. `rev-parse --show-toplevel` carriers are not scored,
# so what they carried is printed instead — a variable that is inert on this git is still an
# unscrubbed variable, and the next git may not agree that it is inert.
idvars="$(awk -F'\t' '$3=="rev-parse --show-toplevel" && $2!="-" {print $2}' "$CENSUS" | LC_ALL=C sort -u | tr '\n' '|')"
check OBSERVED B4v 0 "variables present on the EXEMPT identity-probe calls: [${idvars:-none}] — the entry points scrub GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE/GIT_COMMON_DIR there and do NOT scrub GIT_PREFIX"
# And the breakdown, so the count above is not read as bigger than it is: a call carrying only
# the inert GIT_PREFIX is a different fact from one carrying GIT_DIR.
full_n="$(awk -F'\t' '$2!="-" && $3!="rev-parse --show-toplevel" && $2 ~ /GIT_DIR/' "$CENSUS" | /usr/bin/grep -c '')"
pfx_n="$(awk -F'\t' '$2!="-" && $3!="rev-parse --show-toplevel" && $2 !~ /GIT_DIR/ && $2 !~ /GIT_WORK_TREE/ && $2 !~ /GIT_INDEX_FILE/ && $2 !~ /GIT_COMMON_DIR/' "$CENSUS" | /usr/bin/grep -c '')"
check OBSERVED B4b 0 "body-level carrier breakdown: $full_n call(s) carried GIT_DIR and its siblings; $pfx_n carried GIT_PREFIX alone, which P7 measured inert on this git"

# ======================================================================= GROUP B5 ============
hdr "GROUP B5 (12-F2) — mutate.sh's dirty-tree refusal must not be defeatable from the caller"

# mutate.sh refuses to run against a dirty ts/src or contracts/src because a mutation cannot
# otherwise be told from work in progress. That refusal is computed by a body-level `git status`,
# so it is exactly the shape 12-F2 names.
DIRTY="$(git -C "$SUT" ls-files ts/src | head -1)"
[ -n "$DIRTY" ] || die "no tracked file under ts/src to dirty — B5 would measure nothing"
b5_run() {   # $1 configuration ; sets b5_out / b5_rc
    reset_sut
    printf '// a2 harness dirt\n' >> "$SUT/$DIRTY"
    b5_out="$( run_cfg "$1" ./scripts/mutate.sh a2-no-such-mutation-filter )"; b5_rc=$?
    reset_sut
}
for c in $CONFIGS; do
    b5_run "$c"
    lbl="$(cfg_label "$c")"
    ref=0; printf '%s' "$b5_out" | /usr/bin/grep -qi 'REFUSING' && ref=1
    if [ "$c" = "none" ]; then
        if [ "$ref" -eq 1 ]; then held=0; else held=1; fi
        check CONTROL "B5-$c" "$held" "$lbl: mutate.sh refuses against a dirty ts/src (exit $b5_rc) — the fixture is live"
        continue
    fi
    if [ "$ref" -eq 1 ]; then held=0; else held=1; fi
    check REQUIRED "B5-$c" "$held" "$lbl: the dirty-tree refusal still fires (exit $b5_rc, refusal printed=$ref)"
done
# The opposite control: on a CLEAN tree the refusal must NOT fire, or B5 would be satisfied by a
# script that refuses unconditionally.
reset_sut
b5c="$( run_cfg none ./scripts/mutate.sh a2-no-such-mutation-filter )"
ref=0; printf '%s' "$b5c" | /usr/bin/grep -qi 'REFUSING: ts/src' && ref=1
check CONTROL B5clean "$ref" "on a CLEAN tree mutate.sh does NOT print the dirty-tree refusal — it is conditional, not unconditional"
reset_sut

# ======================================================================= GROUP C =============
hdr "GROUP C (R1) — staged rename and typechange: the destination must be scanned"

# ADJUDICATION FIRST. R1-ADJUDICATION.md classifies this CONFIRMED on the evidence the C0
# controls below reproduce inside this run. The fixture is deliberately LARGE: a prior probe
# reported a negative result because its fixture was small enough that appending the credential
# dropped similarity below the rename threshold and git scored D+A instead of R.
c_bigfile() {   # $1 destination path
    local i=0
    : > "$1"
    while [ "$i" -lt 400 ]; do
        printf 'line %s of an ordinary document, long enough for the pair to score a rename\n' "$i" >> "$1"
        i=$((i + 1))
    done
}
raw_records() {   # prints the staged raw records one per line, NULs turned into tabs
    ( cd "$SUT" && git diff --cached --raw -z > "$WORK/raw.z" 2>/dev/null )
    tr '\0' '\n' < "$WORK/raw.z"
}

# C0 — the rename fixture, and the control that it really scores R.
reset_sut
mkdir -p "$SUT/a2c"
c_bigfile "$SUT/a2c/doc.md"
git -C "$SUT" add a2c/doc.md >/dev/null
git -C "$SUT" commit -qm "a2 group C fixture" >/dev/null 2>&1
git -C "$SUT" mv a2c/doc.md a2c/doc-renamed.md
printf 'export const signerKey = "0x%s";\n' "$(fake_hex64 d)" >> "$SUT/a2c/doc-renamed.md"
git -C "$SUT" add -A a2c >/dev/null
( cd "$SUT" && git diff --cached --raw -z > "$WORK/rawC0.z" 2>/dev/null )
rstat=0; tr '\0' '\n' < "$WORK/rawC0.z" | /usr/bin/grep -Eq '^:[0-7]{6} [0-7]{6} [0-9a-f]+ [0-9a-f]+ R[0-9]*$' && rstat=1
check CONTROL C0 "$( [ "$rstat" -eq 1 ] && echo 0 || echo 1 )" "the staged pair actually scores a RENAME record in the raw enumeration (R present=$rstat) — the fixture is the one a prior probe failed to build"
out="$( cd "$SUT" && env "${BASEENV[@]}" PATH="$SHIMPATH" ./scripts/check-secrets.sh --staged 2>&1 )"; rc=$?
blk=0; printf '%s' "$out" | /usr/bin/grep -q 'BLOCKED a2c/doc-renamed.md' && blk=1
if [ "$blk" -eq 1 ] && [ "$rc" -ne 0 ]; then held=0; else held=1; fi
check REQUIRED C1 "$held" "--staged scans the rename DESTINATION and blocks it (exit $rc, destination named=$blk)"
# C1b — through the hook, which is where the exposure actually reaches HEAD.
( cd "$SUT" && env "${BASEENV[@]}" PATH="$SHIMPATH" git commit -qm "a2 C1b" >/dev/null 2>&1 ); rcc=$?
ncom="$(git -C "$SUT" log --oneline | /usr/bin/grep -c '')"
inhead=0
git -C "$SUT" show "HEAD:a2c/doc-renamed.md" 2>/dev/null | /usr/bin/grep -q 'signerKey' && inhead=1
if [ "$rcc" -ne 0 ] && [ "$inhead" -eq 0 ]; then held=0; else held=1; fi
check REQUIRED C1b "$held" "the hook stops the commit and the credential does NOT reach HEAD (commit exit $rcc, credential in HEAD=$inhead)"

# C2 — a rename whose destination is EXECUTABLE. Parsing by the NEW MODE is what the requirement
#      names; an executable destination is still a regular file and must still be scanned.
reset_sut
mkdir -p "$SUT/a2c"
c_bigfile "$SUT/a2c/doc2.md"
git -C "$SUT" add a2c/doc2.md >/dev/null; git -C "$SUT" commit -qm "a2 C2 fixture" >/dev/null 2>&1
git -C "$SUT" mv a2c/doc2.md a2c/doc2-renamed.md
printf 'export const signerKey = "0x%s";\n' "$(fake_hex64 a)" >> "$SUT/a2c/doc2-renamed.md"
chmod +x "$SUT/a2c/doc2-renamed.md"
git -C "$SUT" add -A a2c >/dev/null
( cd "$SUT" && git diff --cached --raw -z > "$WORK/rawC2.z" 2>/dev/null )
newmode="$(tr '\0' '\n' < "$WORK/rawC2.z" | /usr/bin/grep -E '^:[0-7]{6} [0-7]{6}' | head -1 | awk '{print $2}')"
if [ "$newmode" = "100755" ]; then held=0; else held=1; fi
check CONTROL C2f "$held" "the executable-rename fixture really carries NEW MODE 100755 in its raw record (observed '$newmode')"
out="$( cd "$SUT" && env "${BASEENV[@]}" PATH="$SHIMPATH" ./scripts/check-secrets.sh --staged 2>&1 )"; rc=$?
blk=0; printf '%s' "$out" | /usr/bin/grep -q 'BLOCKED a2c/doc2-renamed.md' && blk=1
if [ "$blk" -eq 1 ]; then held=0; else held=1; fi
check REQUIRED C2 "$held" "a rename destination with new mode 100755 is scanned and blocked (exit $rc, named=$blk)"

# C3 — a staged TYPECHANGE: a tracked symlink replaced by a credential-bearing regular file.
reset_sut
mkdir -p "$SUT/a2c"
( cd "$SUT/a2c" && ln -s ../HANDOFF.md link.md )
git -C "$SUT" add a2c/link.md >/dev/null; git -C "$SUT" commit -qm "a2 C3 fixture" >/dev/null 2>&1
rm -f "$SUT/a2c/link.md"
printf 'export const apiKey = "0x%s";\n' "$(fake_hex64 e)" > "$SUT/a2c/link.md"
git -C "$SUT" add a2c/link.md >/dev/null
( cd "$SUT" && git diff --cached --raw -z > "$WORK/rawC3.z" 2>/dev/null )
tstat=0; tr '\0' '\n' < "$WORK/rawC3.z" | /usr/bin/grep -Eq '^:120000 100644 [0-9a-f]+ [0-9a-f]+ T$' && tstat=1
check CONTROL C3f "$( [ "$tstat" -eq 1 ] && echo 0 || echo 1 )" "the typechange fixture really scores a T record from mode 120000 to 100644 (T present=$tstat)"
out="$( cd "$SUT" && env "${BASEENV[@]}" PATH="$SHIMPATH" ./scripts/check-secrets.sh --staged 2>&1 )"; rc=$?
blk=0; printf '%s' "$out" | /usr/bin/grep -q 'BLOCKED a2c/link.md' && blk=1
if [ "$blk" -eq 1 ]; then held=0; else held=1; fi
check REQUIRED C3 "$held" "a staged typechange whose destination is a regular file is scanned and blocked (exit $rc, named=$blk)"

# C4 — an ordinary staged ADD carrying the same bytes. If this were not blocked the whole group
#      would be measuring the pattern, not the enumeration.
reset_sut
write_fixture "$SUT/a2c-add.ts" 8
git -C "$SUT" add a2c-add.ts >/dev/null
out="$( cd "$SUT" && env "${BASEENV[@]}" PATH="$SHIMPATH" ./scripts/check-secrets.sh --staged 2>&1 )"; rc=$?
blk=0; printf '%s' "$out" | /usr/bin/grep -q 'BLOCKED a2c-add.ts' && blk=1
if [ "$blk" -eq 1 ]; then held=0; else held=1; fi
check CONTROL C4 "$held" "an ordinary staged ADD carrying the identical bytes IS blocked (exit $rc) — the discriminator is the STATUS LETTER, not the pattern"

# C5 — a genuine staged DELETION must still be accepted. D-059(3) forecloses the false failure,
#      and a repair that widened the filter carelessly would break exactly this.
reset_sut
git -C "$SUT" rm -q HANDOFF.md
out="$( cd "$SUT" && env "${BASEENV[@]}" PATH="$SHIMPATH" ./scripts/check-secrets.sh --staged 2>&1 )"; rc=$?
if [ "$rc" -eq 0 ]; then held=0; else held=1; fi
check CONTROL C5 "$held" "a genuine staged DELETION is still accepted, exit $rc (protected control, D-059(3))"

# C5b — a staged deletion of a file that DID carry a credential is still a deletion, not a find.
reset_sut
write_fixture "$SUT/a2c-doomed.ts" 5
git -C "$SUT" add a2c-doomed.ts >/dev/null
git -C "$SUT" commit -qm "a2 C5b fixture" --no-verify >/dev/null 2>&1
git -C "$SUT" rm -q a2c-doomed.ts
out="$( cd "$SUT" && env "${BASEENV[@]}" PATH="$SHIMPATH" ./scripts/check-secrets.sh --staged 2>&1 )"; rc=$?
if [ "$rc" -eq 0 ]; then held=0; else held=1; fi
check CONTROL C5b "$held" "deleting a credential-bearing tracked file is a DELETION and is accepted, exit $rc — removing content is not a finding"

# C6 — a new GITLINK may be treated as a gitlink. It is not a regular file and skipping it is
#      legitimate; what the requirement forbids is skipping a regular-file destination.
reset_sut
git -C "$SUT" update-index --add --cacheinfo "160000,$SUT_SHA,a2c-submodule" >/dev/null 2>&1
( cd "$SUT" && git diff --cached --raw -z > "$WORK/rawC6.z" 2>/dev/null )
glink=0; tr '\0' '\n' < "$WORK/rawC6.z" | /usr/bin/grep -Eq '^:000000 160000 ' && glink=1
check CONTROL C6f "$( [ "$glink" -eq 1 ] && echo 0 || echo 1 )" "the gitlink fixture really carries new mode 160000 in its raw record (present=$glink)"
out="$( cd "$SUT" && env "${BASEENV[@]}" PATH="$SHIMPATH" ./scripts/check-secrets.sh --staged 2>&1 )"; rc=$?
if [ "$rc" -eq 0 ]; then held=0; else held=1; fi
check CONTROL C6 "$held" "a newly staged gitlink is not a false failure, exit $rc (protected control)"

# C7 — a staged COPY. Under this git's defaults a copy surfaces as A and is already scanned;
#      under a repository whose diff.renames is set to copies it surfaces as C. Both must be
#      scanned, and C is asserted here because a repair that enumerates by raw status has to
#      keep it.
reset_sut
git -C "$SUT" config diff.renames copies
mkdir -p "$SUT/a2c"
c_bigfile "$SUT/a2c/src.md"
git -C "$SUT" add a2c/src.md >/dev/null; git -C "$SUT" commit -qm "a2 C7 fixture" >/dev/null 2>&1
cp "$SUT/a2c/src.md" "$SUT/a2c/copy.md"
printf 'export const signerKey = "0x%s";\n' "$(fake_hex64 c)" >> "$SUT/a2c/copy.md"
printf 'one more line in the source\n' >> "$SUT/a2c/src.md"
git -C "$SUT" add -A a2c >/dev/null
( cd "$SUT" && git diff --cached --raw -z > "$WORK/rawC7.z" 2>/dev/null )
cstat=0; tr '\0' '\n' < "$WORK/rawC7.z" | /usr/bin/grep -Eq '^:[0-7]{6} [0-7]{6} [0-9a-f]+ [0-9a-f]+ C[0-9]*$' && cstat=1
check OBSERVED C7f 0 "the copy fixture scores a C record under diff.renames=copies (present=$cstat) — under this git's DEFAULT configuration the same change surfaces as A"
out="$( cd "$SUT" && env "${BASEENV[@]}" PATH="$SHIMPATH" ./scripts/check-secrets.sh --staged 2>&1 )"; rc=$?
blk=0; printf '%s' "$out" | /usr/bin/grep -q 'BLOCKED a2c/copy.md' && blk=1
if [ "$blk" -eq 1 ]; then held=0; else held=1; fi
check CONTROL C7 "$held" "a staged COPY destination is scanned and blocked (exit $rc, named=$blk) — already true today and a repair must not lose it"
git -C "$SUT" config --unset diff.renames
reset_sut

# C8 — the raw enumeration a repair would have to parse, recorded as evidence rather than
#      asserted: rename and copy records carry TWO pathnames, so one pathname per record is
#      an assumption that silently drops destinations.
mkdir -p "$SUT/a2c"
c_bigfile "$SUT/a2c/two.md"
git -C "$SUT" add a2c/two.md >/dev/null; git -C "$SUT" commit -qm "a2 C8 fixture" >/dev/null 2>&1
git -C "$SUT" mv a2c/two.md a2c/two-renamed.md
printf 'one more line\n' >> "$SUT/a2c/two-renamed.md"
git -C "$SUT" add -A a2c >/dev/null
( cd "$SUT" && git diff --cached --raw -z > "$WORK/rawC8.z" 2>/dev/null )
nfields="$(tr '\0' '\n' < "$WORK/rawC8.z" | /usr/bin/grep -c '')"
check OBSERVED C8 0 "one staged rename produces $nfields NUL-delimited fields: the record, the SOURCE and the DESTINATION — not one pathname per record"
check OBSERVED C8b 0 "the excluded statuses at this SHA are the ones outside --diff-filter=ACM: R (rename) and T (typechange); A, C and M are enumerated"
reset_sut

# ======================================================================= closing =============
hdr "CLOSING CONTROLS"

OPCFG_AFTER="$(opcfg_fp)"
if [ "$OPCFG_BEFORE" = "$OPCFG_AFTER" ]; then held=0; else held=1; fi
check CONTROL Z1 "$held" "no git configuration was written to the redirected global/system/XDG files or to the repository under test"

sut_clean=1
[ -z "$(git -C "$SUT" status --porcelain -uall)" ] && [ "$(git -C "$SUT" rev-parse HEAD)" = "$SUT_SHA" ] && sut_clean=0
check CONTROL Z2 "$sut_clean" "the subject clone is back at $SUT_SHA with no modification — every case measured a clean subject"

check OBSERVED Z3 0 "instrumentation: $(/usr/bin/grep -c '' "$SHIM_HITS") shimmed-child hit(s) recorded across the run; reaching one is an instrument fact, never a result"

# ======================================================================= summary =============
hdr "A2 SUMMARY"
printf '  repository under test : %s\n' "$ROOT_SHA"
printf '  REQUIRED failed       : %d\n' "$req_fail"
printf '  CONTROL  failed       : %d   (must be 0, or nothing above is evidence)\n' "$ctl_fail"
if [ -n "${A2_MATRIX_OUT:-}" ]; then printf '%s' "$MATRIX_TSV" > "$A2_MATRIX_OUT"; printf '  matrix written        : %s\n' "$A2_MATRIX_OUT"; fi
if [ -n "${A2_CENSUS_OUT:-}" ]; then cp "$CENSUS" "$A2_CENSUS_OUT"; printf '  census written        : %s\n' "$A2_CENSUS_OUT"; fi
if [ "$ctl_fail" -ne 0 ]; then
    printf '\n  A CONTROL FAILED. This harness is not measuring what it claims. Do not read the\n'
    printf '  REQUIRED lines as evidence until the control is restored.\n'
    exit 2
fi
if [ "$req_fail" -ne 0 ]; then
    printf '\n  %d required assertion(s) failed with every control intact — the confirmed A1\n' "$req_fail"
    printf '  attempt-two obligations are present and observable at this SHA.\n'
    exit 1
fi
printf '\n  every required assertion and every control held.\n'
exit 0
