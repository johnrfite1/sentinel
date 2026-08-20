#!/usr/bin/env bash
# BATCH A1 — falsification harness for repository identity and fail-closed enumeration.
#
# AUTHORITY: batch card A1 (D-060(2), D-060(5)). Base SHA f68d4d804de4d3b631e25fd539deecda5409f0d7.
# This file is a TEST. It makes no production repair and modifies no entry point.
#
# THE INVARIANT UNDER TEST, from the card, both halves load-bearing:
#   A project-owned entry point operates on the Sentinel repository that CONTAINS IT, and
#   refuses rather than reporting a result it did not establish.
#
# HOW TO READ THE OUTPUT. Every line is either
#   REQUIRED  — an assertion of the card's required behaviour. At the base SHA the pre-repair
#               defects make these FAIL. That is the point; a REQUIRED line that cannot fail
#               is worthless.
#   CONTROL   — an assertion that the probe is alive and discriminating: the paired situation
#               that must behave OPPOSITELY. A failing CONTROL means the harness is measuring
#               nothing and NO conclusion may be drawn from the REQUIRED lines beside it.
#
# EXIT STATUS
#   0  every REQUIRED and every CONTROL held        (post-repair success)
#   1  REQUIRED failures, all CONTROLs held         (expected at the base SHA)
#   2  a CONTROL failed, or a preflight failed      (the harness is untrustworthy — fix it
#      before believing any line above)
#
# ISOLATION. Nothing here writes to the repository under test. Every case that stages, commits,
# installs hooks, or writes git config operates on a private clone or on a scratch repository
# this script created under TMPDIR, and everything is removed on exit. `install-hooks.sh` writes
# `core.hooksPath`; it is never pointed at a repository this script did not make.
#
# FIXTURES. The planted credentials are obviously fake: a single character repeated 64 times.
# They are assembled at run time rather than written as literals, so that this file does not
# itself carry credential-shaped content into a repository guarded by check-secrets.sh.
#
# NOT EXERCISED, stated here as well as in COVERAGE.md: scripts/test.sh and scripts/mutate.sh.
# Both drive Foundry, and the review worktree deliberately leaves contracts/lib unpopulated.
# `forge build` self-installs the submodules over the network, which is a state change a test
# author may not make at a pinned SHA. Their case-1 status is asserted STATICALLY (shebang,
# exec bit, tracked, root-resolution idiom) and their runtime behaviour is NOT in evidence.

set -uo pipefail

# ---------------------------------------------------------------------------- preamble ------
BASE_SHA="f68d4d804de4d3b631e25fd539deecda5409f0d7"

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${1:-$(cd "$SELF_DIR/../../../.." && pwd)}"

req_fail=0
ctl_fail=0
preflight_fail=0
MATRIX_TSV=""

hdr() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }
say() { printf '        %s\n' "$*"; }

# check KIND CASE HELD DESC     HELD is 0 when the asserted behaviour was observed.
# KIND is REQUIRED, CONTROL, or OBSERVED. OBSERVED asserts NOTHING and counts toward neither
# tally — it exists so that a fact worth recording cannot be misread as a behaviour that passed.
check() {
    local kind="$1" case_id="$2" held="$3" desc="$4" status
    if [ "$kind" = "OBSERVED" ]; then status="...."
    elif [ "$held" -eq 0 ]; then status="PASS"; else status="FAIL"; fi
    printf '  case %-3s %-8s %s  %s\n' "$case_id" "$kind" "$status" "$desc"
    MATRIX_TSV="${MATRIX_TSV}${case_id}	${kind}	${status}	${desc}
"
    if [ "$held" -ne 0 ] && [ "$kind" != "OBSERVED" ]; then
        if [ "$kind" = "REQUIRED" ]; then req_fail=$((req_fail + 1)); else ctl_fail=$((ctl_fail + 1)); fi
    fi
}

die() { printf '\n  PREFLIGHT FAILED: %s\n' "$1"; exit 2; }

# The 16 entry points, enumerated by the card. Split by whether this harness can execute them.
RUNNABLE="check-class-coverage check-eval-codes check-findings-ledger check-gate-immutability
check-label-integrity check-label-prompt check-rename-gate check-review-scope check-secrets
check-suite-floors check-type-strings check-vendor-honesty"
STATIC_ONLY="scripts/install-hooks.sh scripts/mutate.sh scripts/test.sh .githooks/pre-commit"

# A fake 64-hex value. Assembled, never written as a literal in this file.
fake_hex64() {
    local ch="${1:-b}" i out=""
    case "$ch" in [0-9a-fA-F]) : ;; *) echo "fake_hex64: '$ch' is not a hex digit" >&2; return 1 ;; esac
    i=0
    while [ "$i" -lt 64 ]; do out="${out}${ch}"; i=$((i + 1)); done
    printf '%s' "$out"
}
# Write a fixture whose content is credential-shaped to check-secrets.sh's KEYLIT_RE.
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
if [ "$ROOT_SHA" != "$BASE_SHA" ]; then
    say "WARNING: that is NOT the card's base SHA ($BASE_SHA)."
    say "         Outcomes below are evidence about $ROOT_SHA and nothing else."
fi

WORK="$(mktemp -d "${TMPDIR:-/tmp}/a1-repo-identity.XXXXXXXX")" || die "mktemp failed"
trap 'rm -rf "$WORK"' EXIT

# P1 — /usr/bin/grep canary. The shell's grep on this workstation is a wrapper that honours
# --ignore-files and can return a clean-looking zero. Every search below uses /usr/bin/grep,
# and this proves /usr/bin/grep finds a string that is definitely there.
printf 'A1-CANARY-STRING\n' > "$WORK/canary"
if [ "$(/usr/bin/grep -c 'A1-CANARY-STRING' "$WORK/canary" 2>/dev/null)" != "1" ]; then
    die "/usr/bin/grep did not find a planted canary — no zero result below can be trusted"
fi
say "P1 /usr/bin/grep canary found"

# P2 — an unrelated directory that is genuinely outside every repository.
PLAIN="$WORK/unrelated"
mkdir -p "$PLAIN"
if ( cd "$PLAIN" && git rev-parse --show-toplevel >/dev/null 2>&1 ); then
    die "the 'unrelated directory' is inside a git repository — case 2 would measure nothing"
fi
say "P2 unrelated directory is outside every repository"

# P3 — the subject under test: an isolated clone, so no case can touch the real tree.
SUT="$WORK/sut"
git clone -q --no-hardlinks "$ROOT" "$SUT" >/dev/null 2>&1 || die "clone of the repository under test failed"
git -C "$SUT" fetch -q "$ROOT" HEAD >/dev/null 2>&1 || die "fetch of HEAD into the clone failed"
git -C "$SUT" checkout -q --detach FETCH_HEAD >/dev/null 2>&1 || die "checkout of HEAD in the clone failed"
git -C "$SUT" config user.email "a1-harness@example.invalid"
git -C "$SUT" config user.name "A1 harness"
SUT_SHA="$(git -C "$SUT" rev-parse HEAD)"
[ "$SUT_SHA" = "$ROOT_SHA" ] || die "clone is at $SUT_SHA, not $ROOT_SHA"
# Carry the real origin URL across so check-rename-gate.sh behaves as it does in the real tree.
SUT_ORIGIN="$(git -C "$ROOT" config --get remote.origin.url 2>/dev/null || true)"
if [ -n "$SUT_ORIGIN" ]; then git -C "$SUT" remote set-url origin "$SUT_ORIGIN"
else git -C "$SUT" remote remove origin >/dev/null 2>&1 || true; fi
say "P3 isolated clone of the subject at $SUT_SHA"

# P4 — the git shim. It delegates to the real git except for one named failure mode. A shim
# that did not pass through would make every case-5/6/11 result meaningless.
mkdir -p "$WORK/shim"
cat > "$WORK/shim/git" <<'SHIM'
#!/usr/bin/env bash
# A1 harness shim. One targeted git failure, everything else delegated verbatim.
case "${A1_SHIM_MODE:-none}" in
  lsfiles-fail)
    if [ "${1:-}" = "ls-files" ]; then echo "a1-shim: simulated ls-files failure" >&2; exit 3; fi ;;
  lsfiles-empty)
    if [ "${1:-}" = "ls-files" ]; then exit 0; fi ;;
  errorunmatch-fail)
    if [ "${1:-}" = "ls-files" ]; then
      for a in "$@"; do [ "$a" = "--error-unmatch" ] && exit 3; done
    fi ;;
  show-fail)
    if [ "${1:-}" = "show" ]; then echo "a1-shim: simulated show failure" >&2; exit 3; fi ;;
esac
exec "$A1_REAL_GIT" "$@"
SHIM
chmod +x "$WORK/shim/git"
export A1_REAL_GIT="$REAL_GIT"
shim_sha="$(cd "$SUT" && PATH="$WORK/shim:$PATH" A1_SHIM_MODE=none git rev-parse HEAD 2>/dev/null)"
[ "$shim_sha" = "$SUT_SHA" ] || die "the git shim does not pass through — every shimmed case would be a dead probe"
say "P4 git shim passes through when idle"

# P5 — the credential fixture must actually trip the guard. If it does not, cases 9/10/11 would
# all report clean for a reason that has nothing to do with the defect they name.
write_fixture "$SUT/a1-preflight.ts" f
if ( cd "$SUT" && ./scripts/check-secrets.sh >/dev/null 2>&1 ); then
    rm -f "$SUT/a1-preflight.ts"
    die "the planted credential fixture does NOT trip check-secrets.sh — every clean result below would be vacuous"
fi
rm -f "$SUT/a1-preflight.ts"
say "P5 the planted credential fixture trips check-secrets.sh"

# P6 — a foreign repository, created here, never one this harness did not make.
FOREIGN="$WORK/foreign"
git -c init.defaultBranch=main init -q "$FOREIGN" || die "cannot create the foreign repository"
git -C "$FOREIGN" config user.email "a1-harness@example.invalid"
git -C "$FOREIGN" config user.name "A1 harness"
mkdir -p "$FOREIGN/scripts"
printf 'a foreign repository, created by the A1 harness\n' > "$FOREIGN/README.md"
printf '#!/usr/bin/env bash\n: foreign\n' > "$FOREIGN/scripts/foreign.sh"
git -C "$FOREIGN" add -A >/dev/null
git -C "$FOREIGN" commit -qm "foreign base" >/dev/null
git -C "$FOREIGN" remote add origin "https://github.com/a1-foreign-owner/a1-foreign-repo.git"
[ "$(git -C "$FOREIGN" rev-parse --show-toplevel)" = "$(cd "$FOREIGN" && pwd -P)" ] \
  || say "note: foreign toplevel differs from its path (symlinked TMPDIR); comparisons are unaffected"
say "P6 foreign repository created (2 tracked files, a decoy remote)"

# ============================================================================ CASE 1 =========
hdr "CASE 1 (CONTROL) — invoked from Sentinel's root, normal result"

# 1a — the boundary itself, asserted rather than asserted about: 16 entry points, each
#      #!/usr/bin/env bash, executable, tracked.
ep_bad=0; ep_n=0
for f in $(cd "$SUT" && git ls-files 'scripts/*' '.githooks/*'); do
    ep_n=$((ep_n + 1))
    head -1 "$SUT/$f" | /usr/bin/grep -q '^#!/usr/bin/env bash$' || { ep_bad=1; say "not env-bash: $f"; }
    [ -x "$SUT/$f" ] || { ep_bad=1; say "not executable: $f"; }
done
[ "$ep_n" -eq 16 ] || { ep_bad=1; say "entry-point count is $ep_n, the card enumerates 16"; }
check CONTROL 1a "$ep_bad" "16 tracked entry points under scripts/ and .githooks/, all env-bash and executable"

# 1b — the twelve that can be executed here all exit 0 from the repository root.
mkdir -p "$WORK/base"
one_bad=0
for s in $RUNNABLE; do
    out="$( cd "$SUT" && "./scripts/$s.sh" 2>&1 )"; rc=$?
    printf '%s' "$out" > "$WORK/base/$s.out"
    printf '%s' "$rc"  > "$WORK/base/$s.rc"
    [ "$rc" -eq 0 ] || { one_bad=1; say "$s.sh exited $rc from the root"; }
done
check CONTROL 1b "$one_bad" "12 executable entry points exit 0 from the repository root"

# 1c — the four that are not executed here are asserted statically and recorded as NOT RUN.
four_bad=0
for f in $STATIC_ONLY; do
    /usr/bin/grep -q 'git rev-parse --show-toplevel' "$SUT/$f" || { four_bad=1; say "$f: no root resolution found"; }
done
check CONTROL 1c "$four_bad" "install-hooks/mutate/test/pre-commit resolve a root (runtime NOT exercised; see COVERAGE.md)"

# ============================================================================ CASE 2 =========
hdr "CASE 2 (REQUIRED) — invoked from an unrelated directory, must still check Sentinel"

# The assertion is exactly the invariant: the answer must not depend on where the caller stood.
# All twelve are deterministic (verified by running each twice from the root), so byte-identical
# output is a legitimate assertion rather than a brittle one.
two_bad=0; two_open=0
for s in $RUNNABLE; do
    out="$( cd "$PLAIN" && "$SUT/scripts/$s.sh" 2>&1 )"; rc=$?
    if [ "$out" != "$(cat "$WORK/base/$s.out")" ] || [ "$rc" != "$(cat "$WORK/base/$s.rc")" ]; then
        two_bad=$((two_bad + 1))
        [ "$rc" -eq 0 ] && { two_open=$((two_open + 1)); say "FAIL-OPEN from elsewhere: $s.sh exit 0 with a different answer"; }
    fi
done
check REQUIRED 2 "$two_bad" "all 12 give the Sentinel answer from an unrelated directory ($two_bad differ, of which $two_open exit 0)"

# ============================================================================ CASE 3 =========
hdr "CASE 3 (REQUIRED) — invoked from inside a foreign git repository, must still check Sentinel"

three_bad=0; three_open=0; three_same=""
for s in $RUNNABLE; do
    out="$( cd "$FOREIGN" && "$SUT/scripts/$s.sh" 2>&1 )"; rc=$?
    printf '%s' "$out" > "$WORK/foreign-$s.out"
    if [ "$out" != "$(cat "$WORK/base/$s.out")" ] || [ "$rc" != "$(cat "$WORK/base/$s.rc")" ]; then
        three_bad=$((three_bad + 1))
        [ "$rc" -eq 0 ] && three_open=$((three_open + 1))
    else
        three_same="$three_same $s"
    fi
done
# AN IDENTICAL ANSWER IS NOT AUTOMATICALLY AGREEMENT. On a clean tree check-secrets.sh prints
# "secret guard: clean" whichever repository it read, so its sweep comparison cannot
# discriminate on its own. Case 3a is the probe that does, by planting content the Sentinel
# repository holds and the foreign one does not.
[ -n "$three_same" ] && say "same output from both places (NOT evidence of agreement):$three_same"
check REQUIRED 3 "$three_bad" "all 12 give the Sentinel answer from inside a foreign repository ($three_bad differ, of which $three_open exit 0)"

# 3a — the sharpest form. A credential is planted in the Sentinel clone; the guard is then run
#      with the caller standing in the foreign repository. The required behaviour is BLOCKED.
write_fixture "$SUT/a1-case3.ts" c
( cd "$FOREIGN" && "$SUT/scripts/check-secrets.sh" >/dev/null 2>&1 ); rc_foreign=$?
( cd "$SUT"     && ./scripts/check-secrets.sh      >/dev/null 2>&1 ); rc_home=$?
rm -f "$SUT/a1-case3.ts"
if [ "$rc_foreign" -ne 0 ]; then held=0; else held=1; fi
check REQUIRED 3a "$held" "check-secrets.sh blocks a credential in Sentinel when called from a foreign repo (exit $rc_foreign)"
if [ "$rc_home" -ne 0 ]; then held=0; else held=1; fi
check CONTROL  3a "$held" "the same credential blocks when called from Sentinel's root (exit $rc_home) — the fixture is live"

# 3b — a partition report about the wrong repository. The foreign repo has 2 tracked files.
if /usr/bin/grep -q 'assigned 2 of 2 tracked files' "$WORK/foreign-check-review-scope.out"; then held=1; else held=0; fi
check REQUIRED 3b "$held" "check-review-scope.sh does not print a partition of the FOREIGN repository"

# 3c — a visibility report about the wrong repository. Only meaningful if the root run named a
#      repository at all; otherwise the comparison could not discriminate and says so.
if /usr/bin/grep -q 'gh CLI not available' "$WORK/base/check-rename-gate.out"; then
    check CONTROL 3c 1 "check-rename-gate.sh cannot discriminate here — gh is unavailable, so 3c is UNTESTABLE, not a pass"
else
    if /usr/bin/grep -q 'a1-foreign-owner/a1-foreign-repo' "$WORK/foreign-check-rename-gate.out"; then held=1; else held=0; fi
    check REQUIRED 3c "$held" "check-rename-gate.sh does not report on the FOREIGN repository's slug"
fi

# ============================================================================ CASE 4 =========
hdr "CASE 4 (REQUIRED) — an entry point whose OWN repository cannot be established must refuse"

# WHY THIS FIXTURE REPLACED THE PREVIOUS ONE, recorded here rather than in a side document.
# The withdrawn case 4 ran the SAME command as case 2 — the in-repository entry points, called
# from a directory outside every repository — and required a non-zero exit where case 2
# requires the Sentinel answer and exit 0. What that fixture made unresolvable was only the
# CALLER's repository, which was the identity solely under the caller-current-directory
# semantics D-060(2) abolished. Under the ruled semantics the entry point derives identity from
# its OWN location, so it resolves and exit 0 is CORRECT. The two rows described one fixture
# read under two semantics; only case 2 survives. Independently adjudicated CONFIRMED-INVALID.
#
# THE PROPERTY THIS CASE NOW ASSERTS:
#   An entry point whose own containing Sentinel repository cannot be established must REFUSE
#   before performing project work.
# The fixture instantiates that premise the only way D-060(2) allows: it attacks the SCRIPT's
# own location. The entry-point layout is copied out of every repository, preserving the
# scripts/ and .githooks/ structure, and the COPIES are invoked from there with the git
# identity variables cleared. Case 2 is untouched and still requires the ORIGINALS, called
# from an unrelated directory, to check Sentinel and exit 0 — so the two cases now measure two
# different commands and can both hold. All 16 entry points are covered, not the 12 of the
# withdrawn form.
#
# A NON-ZERO EXIT IS NOT A PASS, AND THIS IS THE CRUX. At the pre-repair checkpoint most of
# these copies exit non-zero for INCIDENTAL reasons — a missing file, a `cd` that failed, a
# child that is not on PATH — and scoring those as refusals is exactly the mislabelling case
# 12b already forecloses; it would make this case vacuous. A pass requires a DEDICATED
# repository-identity refusal, and controls 4c/4d prove the scorer separates the two in both
# directions. Nothing here is scored on an implementation's literal string: 4c feeds the
# scorer refusal wordings this harness invented.
#
# ISOLATION. The copies run with HOME, the global/system/XDG git config files and PATH all
# redirected into this run's scratch area, so nothing they attempt can reach the operator's
# configuration. Expensive and network-capable children (forge, npm, node, curl, gh, …) are
# shimmed to a recorder that does no work: REACHING A SHIM IS AN INSTRUMENT FAILURE, never a
# refusal, and an entry point that reaches one cannot pass this case.

ISO="$WORK/iso-layout"
ISO_DECOY="$WORK/iso-decoy"
FOURSHIM="$WORK/shim4"
FOURHOME="$WORK/home4"
FOURTOUCH="$WORK/shim4.touched"
mkdir -p "$ISO" "$ISO_DECOY" "$FOURSHIM" "$FOURHOME"
: > "$FOURTOUCH"

EP_ALL="$( cd "$SUT" && git ls-files 'scripts/*' '.githooks/*' )"
for f in $EP_ALL; do
    mkdir -p "$ISO/$(dirname "$f")" "$ISO_DECOY/$(dirname "$f")"
    cp "$SUT/$f" "$ISO/$f";       chmod +x "$ISO/$f"
    cp "$SUT/$f" "$ISO_DECOY/$f"; chmod +x "$ISO_DECOY/$f"
done
# The decoy layout differs in exactly one file: a caller-provided check sitting where the hook
# would look for one. It must not run.
printf '#!/usr/bin/env bash\necho "A1-CASE4-DECOY-RAN"\nexit 0\n' > "$ISO_DECOY/scripts/check-secrets.sh"
chmod +x "$ISO_DECOY/scripts/check-secrets.sh"

for c in forge anvil cast chisel npm npx node cargo curl wget gh python3 pip3 yarn pnpm ssh nc; do
    cat > "$FOURSHIM/$c" <<SHIM4
#!/usr/bin/env bash
printf '%s %s\n' "$c" "\$*" >> "$FOURTOUCH"
echo "a1-case4 shim: '$c' was reached — INSTRUMENT FAILURE, not a refusal" >&2
exit 97
SHIM4
    chmod +x "$FOURSHIM/$c"
done

# --- the scorer -----------------------------------------------------------------------------
# A dedicated repository-identity refusal is ONE LINE carrying both a refusal verb and the
# repository-identity condition. Behavioural, not a transcription of any implementation.
is_ident_refusal() {
    printf '%s\n' "$1" \
      | /usr/bin/grep -Ei 'refus(e|ed|es|ing)|declin(e|ed|es|ing)' \
      | /usr/bin/grep -Eiq 'sentinel repositor|repository identit|identity mismatch|repository root|own location|invoking repositor|another repositor|foreign repositor|(is |was )?(not inside|outside) the sentinel|cannot (establish|determine|resolve).*(repositor|identity|location)'
}

iso_fp() { ( cd "$1" && { find . | LC_ALL=C sort
                          find . -type f -exec shasum -a 256 {} + | LC_ALL=C sort
                        } | shasum -a 256 | cut -d' ' -f1 ); }
sut_fp() { printf '%s|%s' "$(git -C "$SUT" rev-parse HEAD)" \
                          "$(git -C "$SUT" status --porcelain -z -uall | shasum -a 256 | cut -d' ' -f1)"; }
# "no git configuration was written ANYWHERE": the clone, the real tree, this run's redirected
# global/system/XDG files, and any repository that might have been conjured in the layout.
cfg_fp() {
    { git -C "$SUT"  config --local --list 2>/dev/null || true
      git -C "$ROOT" config --local --list 2>/dev/null || true
      cat "$FOURHOME/.gitconfig"        2>/dev/null || echo ABSENT-global
      cat "$FOURHOME/.gitconfig-system" 2>/dev/null || echo ABSENT-system
      find "$FOURHOME/.config" -type f -exec cat {} + 2>/dev/null || echo ABSENT-xdg
      for d in "$ISO" "$ISO_DECOY"; do [ -e "$d/.git" ] && echo "GIT-IN-$d" || echo "NO-GIT-IN-$d"; done
    } | shasum -a 256 | cut -d' ' -f1
}
run_iso() {   # $1 layout directory, $2 entry point path relative to it
    ( cd "$1" && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_COMMON_DIR -u GIT_PREFIX \
        HOME="$FOURHOME" GIT_CONFIG_GLOBAL="$FOURHOME/.gitconfig" \
        GIT_CONFIG_SYSTEM="$FOURHOME/.gitconfig-system" XDG_CONFIG_HOME="$FOURHOME/.config" \
        GIT_TERMINAL_PROMPT=0 PATH="$FOURSHIM:$PATH" "./$2" 2>&1 )
}

# 4a — the fixture instantiates the premise, or nothing below means anything.
iso_bad=0; iso_n=0
for d in "$ISO" "$ISO_DECOY"; do
    ( cd "$d" && git rev-parse --show-toplevel >/dev/null 2>&1 ) && { iso_bad=1; say "layout $d is inside a git repository — case 4 would measure nothing"; }
done
for f in $EP_ALL; do
    iso_n=$((iso_n + 1))
    cmp -s "$SUT/$f" "$ISO/$f" || { iso_bad=1; say "copy differs from the original: $f"; }
    [ -x "$ISO/$f" ] || { iso_bad=1; say "copy is not executable: $f"; }
done
[ "$iso_n" -eq 16 ] || { iso_bad=1; say "copied $iso_n entry points; the card enumerates 16"; }
check CONTROL 4a "$iso_bad" "16 byte-identical entry-point copies, structure preserved, in layouts outside every repository"

# 4b — the marker is a dedicated signal. If a NORMAL run already emitted it, the scorer would
#      pass anything and case 4 would prove nothing.
b4=0
for s in $RUNNABLE; do
    is_ident_refusal "$(cat "$WORK/base/$s.out")" && { b4=1; say "an identity refusal appears in a NORMAL run of $s.sh"; }
done
check CONTROL 4b "$b4" "no normal in-repository run emits an identity refusal — the marker is dedicated, not boilerplate"

# 4c/4d — the scorer itself, probed both ways with synthetic lines.
p1='  FAIL  refusing: the Sentinel repository containing this script cannot be established.'
p2='cannot determine the repository identity of this hook; declining before running anything.'
p3='guard: this file is not inside the Sentinel repository, so it refuses to report a result.'
if is_ident_refusal "$p1" && is_ident_refusal "$p2" && is_ident_refusal "$p3"; then held=0; else held=1; fi
check CONTROL 4c "$held" "the scorer accepts dedicated identity refusals in three wordings this harness invented, not one implementation's literal"
neg_bad=0
while IFS= read -r probe; do
    [ -n "$probe" ] || continue
    is_ident_refusal "$probe" && { neg_bad=1; say "scorer accepted an INCIDENTAL failure: $probe"; }
done <<'NEGPROBES'
bash: ./scripts/check-secrets.sh: No such file or directory
./scripts/test.sh: line 12: forge: command not found
fatal: not a git repository (or any of the parent directories): .git
./scripts/mutate.sh: line 33: cd: /ts: No such file or directory
a1-case4 shim: 'npm' was reached — INSTRUMENT FAILURE, not a refusal
  FAIL  git ls-files failed; refusing to report a clean scan:
findings ledger: MISSING at docs/findings-register.md — refusing to report totals from nothing.
  FAIL  git ls-files --error-unmatch failed on: .githooks/pre-commit. Refusing to treat an instrument failure as a deletion.
NEGPROBES
check CONTROL 4d "$neg_bad" "the scorer rejects missing-file, command-not-found, failed-cd, not-a-repository, shim and non-identity refusals"

# --- the case itself ------------------------------------------------------------------------
sut_before="$(sut_fp)"; cfg_before="$(cfg_fp)"
four_pass=0; four_fail=0; four_shim=0; four_incidental=0
ih_rc=""; ih_out=""; ih_cfg_held=1
for f in $EP_ALL; do
    fp0="$(iso_fp "$ISO")"; cfg0="$(cfg_fp)"; sut0="$(sut_fp)"
    t0="$(/usr/bin/grep -c '' "$FOURTOUCH")"
    out="$( run_iso "$ISO" "$f" )"; rc=$?
    printf '%s' "$out" > "$WORK/case4-$( printf '%s' "$f" | tr '/' '_' ).out"
    fp1="$(iso_fp "$ISO")"; cfg1="$(cfg_fp)"; sut1="$(sut_fp)"
    t1="$(/usr/bin/grep -c '' "$FOURTOUCH")"
    [ "$t1" = "$t0" ] || four_shim=$((four_shim + 1))
    printf '%s' "$out" | /usr/bin/grep -Eiq 'no such file or directory|command not found|permission denied|not a git repository|cannot open' \
        && four_incidental=$((four_incidental + 1))
    why=""
    [ "$rc" -eq 0 ]              && why="${why:+$why; }exited 0"
    is_ident_refusal "$out"      || why="${why:+$why; }no dedicated identity refusal"
    [ "$t1" = "$t0" ]            || why="${why:+$why; }reached a shimmed child (instrument failure)"
    [ "$fp1" = "$fp0" ]          || why="${why:+$why; }mutated the layout"
    [ "$cfg1" = "$cfg0" ]        || why="${why:+$why; }wrote git configuration"
    [ "$sut1" = "$sut0" ]        || why="${why:+$why; }mutated the Sentinel clone"
    if [ "$f" = "scripts/install-hooks.sh" ]; then
        ih_rc="$rc"; ih_out="$out"
        [ "$cfg1" = "$cfg0" ] && ih_cfg_held=0
    fi
    if [ -z "$why" ]; then four_pass=$((four_pass + 1))
    else four_fail=$((four_fail + 1)); say "NOT a refusal: $f (exit $rc) — $why"; fi
done
sut_after="$(sut_fp)"; cfg_after="$(cfg_fp)"

check REQUIRED 4 "$four_fail" "all 16 entry points refuse with a dedicated repository-identity refusal before doing any work ($four_pass of 16 refuse, $four_fail do not)"

# 4i — install-hooks.sh carries the extra obligation: NOTHING may be written to git config.
if [ -n "$ih_rc" ] && [ "$ih_rc" -ne 0 ] && is_ident_refusal "$ih_out" && [ "$ih_cfg_held" -eq 0 ]; then held=0; else held=1; fi
check REQUIRED 4i "$held" "install-hooks.sh refuses on an unestablished repository and writes NO git configuration anywhere (exit ${ih_rc:-none}, config unchanged=$( [ "$ih_cfg_held" -eq 0 ] && echo yes || echo no ))"

# 4h — .githooks/pre-commit carries its own: no caller-provided check may execute first.
out4h="$( run_iso "$ISO_DECOY" ".githooks/pre-commit" )"; rc4h=$?
printf '%s' "$out4h" > "$WORK/case4-decoy-pre-commit.out"
decoy4=no; printf '%s' "$out4h" | /usr/bin/grep -q 'A1-CASE4-DECOY-RAN' && decoy4=yes
if [ "$rc4h" -ne 0 ] && [ "$decoy4" = "no" ] && is_ident_refusal "$out4h"; then held=0; else held=1; fi
check REQUIRED 4h "$held" "the hook refuses before executing the layout's own scripts/check-secrets.sh (exit $rc4h, decoy ran: $decoy4)"

# 4e — case 4 is inert with respect to everything the later cases measure.
if [ "$sut_after" = "$sut_before" ] && [ "$cfg_after" = "$cfg_before" ]; then held=0; else held=1; fi
check CONTROL 4e "$held" "case 4 changed neither the Sentinel clone nor any git configuration — later cases still measure a clean subject"

check OBSERVED 4s 0 "instrumentation: $four_shim of 16 reached a shimmed child, $four_incidental of 16 printed an incidental error (neither can score as a refusal)"
check OBSERVED 4x 0 "case 2 and case 4 differ only in WHERE THE SCRIPT LIVES: originals inside Sentinel, called from elsewhere, must answer; copies outside every repository must refuse"

# ============================================================================ CASE 5 =========
hdr "CASE 5 (REQUIRED) — a git command exits non-zero, must refuse"

# 5a — check-secrets.sh default mode. `git ls-files` fails; the file list collapses to empty.
( cd "$SUT" && PATH="$WORK/shim:$PATH" A1_SHIM_MODE=lsfiles-fail ./scripts/check-secrets.sh >/dev/null 2>&1 ); rc=$?
if [ "$rc" -ne 0 ]; then held=0; else held=1; fi
check REQUIRED 5a "$held" "check-secrets.sh refuses when git ls-files exits non-zero (exit $rc)"

# 5b — check-review-scope.sh, the V3-N1 route: `git ls-files --error-unmatch` fails while plain
#      `git ls-files` still works, so the guarded branch above is not entered at all.
out="$( cd "$SUT" && PATH="$WORK/shim:$PATH" A1_SHIM_MODE=errorunmatch-fail ./scripts/check-review-scope.sh 2>&1 )"; rc=$?
if [ "$rc" -ne 0 ]; then held=0; else held=1; fi
check REQUIRED 5b "$held" "check-review-scope.sh refuses when 'git ls-files --error-unmatch' fails (exit $rc)"
true_n="$(/usr/bin/grep -oE 'remediation surface: [0-9]+' "$WORK/base/check-review-scope.out" | /usr/bin/grep -oE '[0-9]+')"
shim_n="$(printf '%s' "$out" | /usr/bin/grep -oE 'remediation surface: [0-9]+' | /usr/bin/grep -oE '[0-9]+')"
if [ "${shim_n:-none}" = "${true_n:-none}" ]; then held=0; else held=1; fi
check REQUIRED 5c "$held" "the remediation count survives that failure (true=${true_n:-none}, observed=${shim_n:-none})"

# CONTROLS for case 5. The guarded sibling branch refuses on the same shim, and an unmutated
# run still measures the whole tree. Without both, 5a/5b would prove nothing about the shim.
( cd "$SUT" && PATH="$WORK/shim:$PATH" A1_SHIM_MODE=lsfiles-fail ./scripts/check-review-scope.sh >/dev/null 2>&1 ); rc=$?
if [ "$rc" -ne 0 ]; then held=0; else held=1; fi
check CONTROL 5d "$held" "check-review-scope.sh's GUARDED ls-files branch does refuse on the same shim (exit $rc) — the shim is live"
if [ -n "${true_n:-}" ] && [ "${true_n:-0}" -gt 0 ]; then held=0; else held=1; fi
check CONTROL 5e "$held" "an unmutated run assigns every tracked file and measures a non-empty remediation surface (${true_n:-none})"

# ============================================================================ CASE 6 =========
hdr "CASE 6 (REQUIRED) — a git command succeeds with EMPTY output, must refuse"

( cd "$SUT" && PATH="$WORK/shim:$PATH" A1_SHIM_MODE=lsfiles-empty ./scripts/check-secrets.sh >/dev/null 2>&1 ); rc=$?
if [ "$rc" -ne 0 ]; then held=0; else held=1; fi
check REQUIRED 6 "$held" "check-secrets.sh refuses when git ls-files succeeds with no output (exit $rc)"
( cd "$SUT" && PATH="$WORK/shim:$PATH" A1_SHIM_MODE=lsfiles-empty ./scripts/check-review-scope.sh >/dev/null 2>&1 ); rc=$?
if [ "$rc" -ne 0 ]; then held=0; else held=1; fi
check CONTROL 6 "$held" "check-review-scope.sh's guarded branch does refuse on an empty enumeration (exit $rc)"

# ============================================================================ CASE 7 =========
hdr "CASE 7 (PROTECTED CONTROL) — a genuine staged deletion must NOT be refused (D-059(3))"

# Hooks are installed in the clone first, so this exercises the real commit path and doubles as
# case 12's control. install-hooks.sh writes core.hooksPath; the target is this harness's clone.
inst_out="$( cd "$SUT" && ./scripts/install-hooks.sh 2>&1 )"; inst_rc=$?
if [ "$inst_rc" -eq 0 ] && [ "$(git -C "$SUT" config --local --get core.hooksPath)" = ".githooks" ]; then held=0; else held=1; fi
check CONTROL 12c "$held" "install-hooks.sh against Sentinel still succeeds and sets core.hooksPath (exit $inst_rc)"

git -C "$SUT" rm -q HANDOFF.md
( cd "$SUT" && ./scripts/check-secrets.sh --staged >/dev/null 2>&1 ); rc_guard=$?
( cd "$SUT" && ./.githooks/pre-commit           >/dev/null 2>&1 ); rc_hook=$?
( cd "$SUT" && git commit -qm "a1 case 7: a genuine staged deletion" >/dev/null 2>&1 ); rc_commit=$?
if [ "$rc_guard" -eq 0 ] && [ "$rc_hook" -eq 0 ] && [ "$rc_commit" -eq 0 ]; then held=0; else held=1; fi
check CONTROL 7 "$held" "staged deletion accepted: guard=$rc_guard hook=$rc_hook commit=$rc_commit (a blanket 'any git failure refuses' would break this)"
git -C "$SUT" reset -q --hard "$SUT_SHA"; git -C "$SUT" clean -qfd

# ============================================================================ CASES 8 / 9 ====
hdr "CASES 8 & 9 — the same credential bytes under an ASCII and a non-ASCII filename"

ASCII_NAME="a1-case8-ascii.ts"
UTF8_NAME="$(printf 'a1-case9-caf\303\251.ts')"
write_fixture "$SUT/$ASCII_NAME" 8
write_fixture "$SUT/$UTF8_NAME"  8
if cmp -s "$SUT/$ASCII_NAME" "$SUT/$UTF8_NAME"; then held=0; else held=1; fi
check CONTROL 89 "$held" "the two fixtures are byte-identical — only the FILENAME differs, which is the whole discriminator"

# 8 — ASCII twin, both modes. This is a control: it is blocked today and must stay blocked.
rm -f "$SUT/$UTF8_NAME"
( cd "$SUT" && ./scripts/check-secrets.sh >/dev/null 2>&1 ); rc8d=$?
git -C "$SUT" add "$ASCII_NAME" >/dev/null
( cd "$SUT" && ./scripts/check-secrets.sh --staged >/dev/null 2>&1 ); rc8s=$?
git -C "$SUT" reset -q
if [ "$rc8d" -ne 0 ] && [ "$rc8s" -ne 0 ]; then held=0; else held=1; fi
check CONTROL 8 "$held" "ASCII filename is BLOCKED in both modes (default=$rc8d staged=$rc8s)"
rm -f "$SUT/$ASCII_NAME"

# 9 — the accented twin, both modes. Required: blocked. Root cause is core.quotePath.
write_fixture "$SUT/$UTF8_NAME" 8
( cd "$SUT" && ./scripts/check-secrets.sh >/dev/null 2>&1 ); rc9d=$?
git -C "$SUT" add "$UTF8_NAME" >/dev/null
( cd "$SUT" && ./scripts/check-secrets.sh --staged >/dev/null 2>&1 ); rc9s=$?
if [ "$rc9d" -ne 0 ] && [ "$rc9s" -ne 0 ]; then held=0; else held=1; fi
check REQUIRED 9 "$held" "non-ASCII filename is BLOCKED in both modes (default=$rc9d staged=$rc9s)"

# The mechanism, printed as evidence rather than asserted: what each enumeration actually emits.
say "enumeration as check-secrets.sh sees it (quoted):"
say "  ls-files      -> $( cd "$SUT" && git ls-files | /usr/bin/grep case9 )"
say "  diff --cached -> $( cd "$SUT" && git diff --cached --name-only --diff-filter=ACM | /usr/bin/grep case9 )"
say "the same paths with quoting removed (candidate discriminators, NOT applied here):"
say "  ls-files -z          -> $( cd "$SUT" && git ls-files -z | tr '\0' '\n' | /usr/bin/grep case9 )"
say "  diff --cached --raw -z -> $( cd "$SUT" && git diff --cached --raw -z | tr '\0' '\n' | /usr/bin/grep -A0 case9 )"
git -C "$SUT" reset -q; rm -f "$SUT/$UTF8_NAME"

# ============================================================================ CASE 10 ========
hdr "CASE 10 (REQUIRED) — secret guard DEFAULT mode, fail-closed"

# A route distinct from case 9, as the repair protocol requires: the path is enumerated, the
# index holds the credential, and the working-tree copy is absent. `[ -f "$f" ] || continue`
# skips it, and the run prints clean. This is the mode scripts/test.sh:176 invokes.
IDX_NAME="a1-case10-index.ts"
write_fixture "$SUT/$IDX_NAME" a
git -C "$SUT" add "$IDX_NAME" >/dev/null
git -C "$SUT" commit -qm "a1 case 10 fixture" >/dev/null 2>&1
( cd "$SUT" && ./scripts/check-secrets.sh >/dev/null 2>&1 ); rc_present=$?
if [ "$rc_present" -ne 0 ]; then held=0; else held=1; fi
check CONTROL 10 "$held" "the same file, present in the working tree, IS blocked in default mode (exit $rc_present)"
rm -f "$SUT/$IDX_NAME"
( cd "$SUT" && ./scripts/check-secrets.sh >/dev/null 2>&1 ); rc_absent=$?
if [ "$rc_absent" -ne 0 ]; then held=0; else held=1; fi
check REQUIRED 10 "$held" "default mode refuses when a tracked path it enumerated cannot be read (exit $rc_absent)"

# Evidence for the default-mode discriminator question the card raises. Observations only.
say "default-mode discriminator evidence (observed, not applied):"
say "  git ls-files --deleted names it            -> $( cd "$SUT" && git ls-files --deleted | /usr/bin/grep case10 )"
say "  git show \":path\" still yields the content  -> $( cd "$SUT" && git show ":$IDX_NAME" | /usr/bin/grep -c signerKey ) matching line(s)"
say "  index mode-bit census (160000 = gitlink, legitimately not a file):"
( cd "$SUT" && git ls-files -s | awk '{print $1}' | sort | uniq -c | sed 's/^/            /' )
git -C "$SUT" reset -q --hard "$SUT_SHA"; git -C "$SUT" clean -qfd
git -C "$SUT" config core.hooksPath .githooks

# ============================================================================ CASE 11 ========
hdr "CASE 11 (REQUIRED) — secret guard --staged mode, fail-closed"

STG_NAME="a1-case11-staged.ts"
write_fixture "$SUT/$STG_NAME" e
git -C "$SUT" add "$STG_NAME" >/dev/null
( cd "$SUT" && ./scripts/check-secrets.sh --staged >/dev/null 2>&1 ); rc_plain=$?
if [ "$rc_plain" -ne 0 ]; then held=0; else held=1; fi
check CONTROL 11 "$held" "unshimmed, the staged credential IS blocked (exit $rc_plain)"
( cd "$SUT" && PATH="$WORK/shim:$PATH" A1_SHIM_MODE=show-fail ./scripts/check-secrets.sh --staged >/dev/null 2>&1 ); rc_show=$?
if [ "$rc_show" -ne 0 ]; then held=0; else held=1; fi
check REQUIRED 11 "$held" "staged mode refuses when 'git show :path' fails instead of skipping the file (exit $rc_show)"
git -C "$SUT" reset -q --hard "$SUT_SHA"; git -C "$SUT" clean -qfd
git -C "$SUT" config core.hooksPath .githooks

# ============================================================================ CASE 12 ========
hdr "CASE 12 (REQUIRED) — install-hooks.sh against a FOREIGN repository"

F12="$WORK/foreign-install"
git -c init.defaultBranch=main init -q "$F12"
git -C "$F12" config user.email "a1-harness@example.invalid"
git -C "$F12" config user.name "A1 harness"
printf 'foreign\n' > "$F12/README.md"; git -C "$F12" add -A >/dev/null; git -C "$F12" commit -qm base >/dev/null
before="$(git -C "$F12" config --local --get core.hooksPath || true)"
( cd "$F12" && "$SUT/scripts/install-hooks.sh" >/dev/null 2>&1 ); rc12=$?
after="$(git -C "$F12" config --local --get core.hooksPath || true)"
if [ -z "$after" ]; then held=0; else held=1; fi
check REQUIRED 12 "$held" "core.hooksPath is NOT written into a repository that does not own the script (before='$before' after='$after')"
# A non-zero exit is NOT a refusal here. At the base SHA install-hooks.sh writes core.hooksPath
# FIRST and then exits non-zero only because `chmod .githooks/* scripts/*.sh` finds nothing in
# the foreign tree. Scoring that as a pass is precisely the mislabelling the card forecloses,
# so 12b asserts a refusal that happened BEFORE any state was written.
if [ "$rc12" -ne 0 ] && [ -z "$after" ]; then held=0; else held=1; fi
check REQUIRED 12b "$held" "the non-zero exit is a refusal taken BEFORE any write, not a downstream chmod failure (exit $rc12, wrote='$after')"
# case 12's control (install against Sentinel succeeds) was asserted above as 12c.

# ============================================================================ CASE 13 ========
hdr "CASE 13 (REQUIRED) — pre-commit hook under a repository-identity MISMATCH"

# The mismatch is the state case 12 produces: a foreign repository whose core.hooksPath points
# at Sentinel's tracked .githooks. The hook then resolves repo_root from the CALLER's repository.
F13="$WORK/foreign-hook"
git -c init.defaultBranch=main init -q "$F13"
git -C "$F13" config user.email "a1-harness@example.invalid"
git -C "$F13" config user.name "A1 harness"
printf 'foreign\n' > "$F13/README.md"; git -C "$F13" add -A >/dev/null; git -C "$F13" commit -qm base >/dev/null
git -C "$F13" config core.hooksPath "$SUT/.githooks"

# 13a — the foreign repository supplies NO scripts/check-secrets.sh.
write_fixture "$F13/leak-a.ts" 1
git -C "$F13" add leak-a.ts >/dev/null
out13a="$( cd "$F13" && git commit -m "a1 13a" 2>&1 )"; rc13a=$?
n13a="$(git -C "$F13" log --oneline | /usr/bin/grep -c '')"
if [ "$rc13a" -ne 0 ] && [ "$n13a" -eq 1 ]; then held_block=0; else held_block=1; fi
check OBSERVED 13a "$held_block" "with no guard in the foreign tree the commit is stopped (exit $rc13a, commits=$n13a) — recorded, and asserted by 13a-r below"
if printf '%s' "$out13a" | /usr/bin/grep -q 'No such file or directory'; then held=1; else held=0; fi
check REQUIRED 13a-r "$held" "the stop is a refusal, not an exec failure against a path in the calling repository"

# 13b — the foreign repository supplies its OWN scripts/check-secrets.sh. Sentinel's hook runs
#       it. This is the identity failure with teeth: a foreign script executes and the
#       credential lands.
mkdir -p "$F13/scripts"
printf '#!/usr/bin/env bash\necho "A1-DECOY-GUARD-RAN"\nexit 0\n' > "$F13/scripts/check-secrets.sh"
chmod +x "$F13/scripts/check-secrets.sh"
git -C "$F13" add -A >/dev/null
out13b="$( cd "$F13" && git commit -m "a1 13b" 2>&1 )"; rc13b=$?
n13b="$(git -C "$F13" log --oneline | /usr/bin/grep -c '')"
decoy_ran=no; printf '%s' "$out13b" | /usr/bin/grep -q 'A1-DECOY-GUARD-RAN' && decoy_ran=yes
if [ "$decoy_ran" = "yes" ]; then decoy_held=1; else decoy_held=0; fi
if [ "$rc13b" -ne 0 ] && [ "$n13b" -eq 1 ]; then held=0; else held=1; fi
check REQUIRED 13 "$held" "the hook refuses on an identity mismatch (exit $rc13b, commits=$n13b, credential landed=$( [ "$n13b" -gt 1 ] && echo yes || echo no ))"
check REQUIRED 13b "$decoy_held" "the hook does not execute the FOREIGN repository's scripts/check-secrets.sh (decoy ran: $decoy_ran)"

# 13c/13d — the controls. A matching repository must still commit, and must still block.
printf 'a1 control note\n' > "$SUT/a1-case13-control.txt"
git -C "$SUT" add a1-case13-control.txt >/dev/null
( cd "$SUT" && git commit -qm "a1 case 13 control" >/dev/null 2>&1 ); rc13c=$?
if [ "$rc13c" -eq 0 ]; then held=0; else held=1; fi
check CONTROL 13c "$held" "a matching repository with hooks installed still commits (exit $rc13c)"
write_fixture "$SUT/a1-case13-leak.ts" 3
git -C "$SUT" add a1-case13-leak.ts >/dev/null
( cd "$SUT" && git commit -qm "a1 case 13 leak" >/dev/null 2>&1 ); rc13d=$?
if [ "$rc13d" -ne 0 ]; then held=0; else held=1; fi
check CONTROL 13d "$held" "a matching repository still BLOCKS an ASCII credential through the hook (exit $rc13d)"
git -C "$SUT" reset -q --hard "$SUT_SHA"; git -C "$SUT" clean -qfd

# ============================================================================ summary ========
hdr "A1 SUMMARY"
printf '  repository under test : %s\n' "$ROOT_SHA"
printf '  REQUIRED failed       : %d   (pre-repair defects observed)\n' "$req_fail"
printf '  CONTROL  failed       : %d   (must be 0, or nothing above is evidence)\n' "$ctl_fail"
if [ -n "${A1_MATRIX_OUT:-}" ]; then printf '%s' "$MATRIX_TSV" > "$A1_MATRIX_OUT"; printf '  matrix written        : %s\n' "$A1_MATRIX_OUT"; fi
if [ "$ctl_fail" -ne 0 ]; then
    printf '\n  A CONTROL FAILED. This harness is not measuring what it claims. Do not read the\n'
    printf '  REQUIRED lines as evidence until the control is restored.\n'
    exit 2
fi
if [ "$req_fail" -ne 0 ]; then
    printf '\n  %d required assertion(s) failed with every control intact — the A1 defects are\n' "$req_fail"
    printf '  present and observable at this SHA.\n'
    exit 1
fi
printf '\n  every required assertion and every control held.\n'
exit 0
