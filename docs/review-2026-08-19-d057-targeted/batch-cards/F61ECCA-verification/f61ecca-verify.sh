#!/usr/bin/env bash
# F61ECCA verification. Disposable clones only. Never edits the live tree.
# Exploit control first, observing test second. Runtime-synthesised credentials.
set -euo pipefail

SRC="${1:-}"
LOGDIR="${2:-}"
if [ -z "$SRC" ] || [ -z "$LOGDIR" ]; then
  echo "usage: f61ecca-verify.sh <repository-path> <log-directory>" >&2
  exit 2
fi
SRC="$(cd "$SRC" && pwd -P)"
mkdir -p "$LOGDIR"
LOGDIR="$(cd "$LOGDIR" && pwd -P)"
if [ -n "$(ls -A "$LOGDIR" 2>/dev/null)" ]; then
  echo "preflight: log directory must be empty: $LOGDIR" >&2
  exit 2
fi

WORK="$(mktemp -d "${TMPDIR:-/tmp}/f61ecca.XXXXXXXX")"
trap 'rm -rf "$WORK"' EXIT

CRED="$(python3 -c 'import os; print("API_KEY=" + os.urandom(32).hex())')"
export CRED
redact() {
  python3 -c 'import sys,os; c=os.environ["CRED"]; sys.stdout.write(sys.stdin.read().replace(c,"API_KEY=<redacted>"))'
}
save_log() { redact < "$1" > "$2"; }

req_fail=0
ctl_fail=0
record() {
  local id="$1" kind="$2" held="$3" desc="$4" status
  if [ "$held" -eq 0 ]; then status="PASS"; else status="FAIL"; fi
  printf '  %-10s %-8s %s  %s\n' "$id" "$kind" "$status" "$desc"
  printf '%s\t%s\t%s\t%s\n' "$id" "$kind" "$status" "$desc" >> "$LOGDIR/matrix.tsv"
  if [ "$held" -ne 0 ]; then
    if [ "$kind" = "REQUIRED" ]; then req_fail=$((req_fail + 1)); else ctl_fail=$((ctl_fail + 1)); fi
  fi
}

run_to() {
  python3 - "$1" "$2" "${@:3}" << 'PY'
import subprocess, sys
timeout = float(sys.argv[1])
cwd = sys.argv[2]
cmd = sys.argv[3:]
try:
    r = subprocess.run(cmd, cwd=cwd, timeout=timeout)
    sys.exit(r.returncode)
except subprocess.TimeoutExpired:
    sys.exit(124)
PY
}

make_clone() {
  local dest="$WORK/$1"
  git clone -q --local --no-hardlinks "$SRC" "$dest" >/dev/null 2>&1 || return 1
  git -C "$dest" config user.email "f61ecca-card@invalid"
  git -C "$dest" config user.name "F61ECCA card"
  git -C "$dest" config commit.gpgsign false
  printf '%s' "$dest"
}

plant_identity_lookalikes() {
  mkdir -p "$1/scripts" "$1/.githooks"
  : > "$1/scripts/test.sh"
  : > "$1/.githooks/pre-commit"
}

do_mutate_c4() {
  python3 - "$1/scripts/check-secrets.sh" << 'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
t = p.read_text()
orig = t
t = t.replace("ls-files -s -z", "ls-files -s")
t = t.replace("ls-files --others --exclude-standard -z", "ls-files --others --exclude-standard")
t = t.replace("diff --cached --raw -z --diff-filter=d", "diff --cached --raw --diff-filter=d")
t = t.replace("read -r -d ''", "read -r")
t = t.replace(
    'if [ "$_rc" -ne 0 ]; then _sec_refuse "$f"; continue; fi',
    'if [ "$_rc" -ne 0 ]; then continue; fi',
)
if t == orig:
    sys.exit("c4 mutate: no substitutions landed")
p.write_text(t)
PY
}

do_mutate_r1() {
  python3 - "$1/scripts/check-secrets.sh" << 'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
t = p.read_text()
start = t.find('if [ "$STAGED" -eq 1 ]; then')
if start < 0:
    sys.exit("r1 mutate: staged block start not found")
end = t.find("\nelse\n", start)
if end < 0:
    sys.exit("r1 mutate: staged block else not found")
repl = '''if [ "$STAGED" -eq 1 ]; then
  if ! _cs_git diff --cached --name-only --diff-filter=ACM >"$_sec_lst" 2>"$_sec_err"; then
    echo "${RED}FAIL${RST} git diff --cached --name-only failed; refusing to report a clean scan:"
    printf '    %s\\n' "$(cat "$_sec_err")"
    _sec_cleanup; exit 1
  fi
  while IFS= read -r _p; do
    [ -z "$_p" ] && continue
    sec_files+=("$_p")
    sec_kind+=("regular")
    sec_hasidx+=("1")
  done < "$_sec_lst"
'''
p.write_text(t[:start] + repl + t[end:])
PY
}

do_mutate_cwd_identity() {
  python3 - "$1" << 'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
t = p.read_text()
needle = 'cd -- "$_sentinel_self" 2>/dev/null && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR git rev-parse --show-toplevel 2>/dev/null'
if needle not in t:
    sys.exit(f"identity mutate: root assignment not found in {p}")
t = t.replace(needle, 'git rev-parse --show-toplevel 2>/dev/null', 1)
t = t.replace(
    'if [ -n "$CALLER_ROOT" ] && [ "$CALLER_ROOT" != "$SENTINEL_ROOT" ]; then',
    'if false && [ -n "$CALLER_ROOT" ] && [ "$CALLER_ROOT" != "$SENTINEL_ROOT" ]; then',
    1,
)
p.write_text(t)
PY
}

do_mutate_c6d() {
  python3 - "$1/scripts/test.sh" << 'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
t = p.read_text()
old_root = '_gate_root="$(cd -- "$(dirname -- "$_gate_src")" 2>/dev/null && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR -u GIT_PREFIX git rev-parse --show-toplevel 2>/dev/null)" || _gate_root=""'
if old_root not in t:
    sys.exit("c6d mutate: supervisor root line not found")
t = t.replace(old_root, '_gate_root="$(git rev-parse --show-toplevel 2>/dev/null)" || _gate_root=""', 1)
old_id = '[ "$(cd -- "$(dirname -- "$_gate_src")" && pwd -P)" = "$_gate_root/scripts" ] || _gate_root=""'
if old_id not in t:
    sys.exit("c6d mutate: script-in-scripts check not found")
t = t.replace(old_id, 'true  # mutant: no script-location identity', 1)
p.write_text(t)
PY
}

write_large() {
  python3 - "$1" << 'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
p.write_text("\n".join(f"line {i} of innocuous documentation." for i in range(400)) + "\n")
PY
}

echo "F61ECCA verification"
echo "source=$SRC"
echo "logs=$LOGDIR"
echo "work=$WORK"
echo
printf 'id\tkind\tstatus\tdesc\n' > "$LOGDIR/matrix.tsv"

echo "== C4 café / ASCII =="
C4M="$(make_clone c4-mutant)"
C4F="$(make_clone c4-freeze)"
do_mutate_c4 "$C4M"

mkdir -p "$C4M/probe"
printf '%s\n' "$CRED" > "$C4M/probe/café-only.md"
( cd "$C4M" && ./scripts/check-secrets.sh ) >"$WORK/c4-mut-cafe.raw" 2>&1 || true
save_log "$WORK/c4-mut-cafe.raw" "$LOGDIR/c4-mutant-cafe.log"
if grep -q "secret guard: clean" "$WORK/c4-mut-cafe.raw"; then
  record C4-x CONTROL 0 "mutant café-only: hole live (clean)"
else
  record C4-x CONTROL 1 "mutant café-only did not print clean"
fi

rm -f "$C4M/probe/café-only.md"
printf '%s\n' "$CRED" > "$C4M/probe/ascii-only.md"
( cd "$C4M" && ./scripts/check-secrets.sh ) >"$WORK/c4-mut-ascii.raw" 2>&1 || true
save_log "$WORK/c4-mut-ascii.raw" "$LOGDIR/c4-mutant-ascii.log"
if grep -q "BLOCKED" "$WORK/c4-mut-ascii.raw" && grep -q "ascii-only.md" "$WORK/c4-mut-ascii.raw"; then
  record C4-a CONTROL 0 "mutant ASCII-only: still BLOCKED (scanner not inert)"
else
  record C4-a CONTROL 1 "mutant ASCII-only was not BLOCKED"
fi

mkdir -p "$C4F/probe"
printf '%s\n' "$CRED" > "$C4F/probe/café-only.md"
( cd "$C4F" && ./scripts/check-secrets.sh ) >"$WORK/c4-frz-cafe.raw" 2>&1 || true
save_log "$WORK/c4-frz-cafe.raw" "$LOGDIR/c4-freeze-cafe.log"
if grep -q "BLOCKED" "$WORK/c4-frz-cafe.raw"; then
  record C4 REQUIRED 0 "freeze café-only: BLOCKED"
else
  record C4 REQUIRED 1 "freeze café-only was not BLOCKED"
fi
rm -f "$C4F/probe/café-only.md"
printf '%s\n' "$CRED" > "$C4F/probe/ascii-only.md"
( cd "$C4F" && ./scripts/check-secrets.sh ) >"$WORK/c4-frz-ascii.raw" 2>&1 || true
save_log "$WORK/c4-frz-ascii.raw" "$LOGDIR/c4-freeze-ascii.log"
if grep -q "BLOCKED" "$WORK/c4-frz-ascii.raw"; then
  record C4b REQUIRED 0 "freeze ASCII-only: BLOCKED"
else
  record C4b REQUIRED 1 "freeze ASCII-only was not BLOCKED"
fi

echo "== R1 staged rename + typechange =="
R1M="$(make_clone r1-mutant)"
do_mutate_r1 "$R1M"
write_large "$R1M/r1-src.txt"
git -C "$R1M" add r1-src.txt
git -C "$R1M" commit -qn -m "r1 base" >/dev/null
git -C "$R1M" mv r1-src.txt r1-dst.txt
printf '%s\n' "$CRED" >> "$R1M/r1-dst.txt"
git -C "$R1M" add r1-dst.txt
( cd "$R1M" && ./scripts/check-secrets.sh --staged ) >"$WORK/r1-mut-R.raw" 2>&1 || true
save_log "$WORK/r1-mut-R.raw" "$LOGDIR/r1-mutant-rename.log"
if grep -q "secret guard: clean" "$WORK/r1-mut-R.raw"; then
  record R1-xR CONTROL 0 "mutant staged rename: hole live (clean)"
else
  record R1-xR CONTROL 1 "mutant staged rename did not print clean"
fi

R1MT="$(make_clone r1-mutant-T)"
do_mutate_r1 "$R1MT"
ln -s /tmp/r1-none "$R1MT/r1-link"
git -C "$R1MT" add r1-link
git -C "$R1MT" commit -qn -m "r1 symlink" >/dev/null
rm -f "$R1MT/r1-link"
printf '%s\n' "$CRED" > "$R1MT/r1-link"
git -C "$R1MT" add r1-link
( cd "$R1MT" && ./scripts/check-secrets.sh --staged ) >"$WORK/r1-mut-T.raw" 2>&1 || true
save_log "$WORK/r1-mut-T.raw" "$LOGDIR/r1-mutant-typechange.log"
if grep -q "secret guard: clean" "$WORK/r1-mut-T.raw"; then
  record R1-xT CONTROL 0 "mutant staged typechange: hole live (clean)"
else
  record R1-xT CONTROL 1 "mutant staged typechange did not print clean"
fi

R1F="$(make_clone r1-freeze)"
write_large "$R1F/r1-src.txt"
git -C "$R1F" add r1-src.txt
git -C "$R1F" commit -qn -m "r1 base" >/dev/null
git -C "$R1F" mv r1-src.txt r1-dst.txt
printf '%s\n' "$CRED" >> "$R1F/r1-dst.txt"
git -C "$R1F" add r1-dst.txt
( cd "$R1F" && ./scripts/check-secrets.sh --staged ) >"$WORK/r1-frz-R.raw" 2>&1 || true
save_log "$WORK/r1-frz-R.raw" "$LOGDIR/r1-freeze-rename.log"
if grep -q "BLOCKED" "$WORK/r1-frz-R.raw" && grep -q "r1-dst.txt" "$WORK/r1-frz-R.raw"; then
  record R1-R REQUIRED 0 "freeze staged rename: BLOCKED, destination named"
else
  record R1-R REQUIRED 1 "freeze staged rename was not BLOCKED with dest named"
fi

R1FT="$(make_clone r1-freeze-T)"
ln -s /tmp/r1-none "$R1FT/r1-link"
git -C "$R1FT" add r1-link
git -C "$R1FT" commit -qn -m "r1 symlink" >/dev/null
rm -f "$R1FT/r1-link"
printf '%s\n' "$CRED" > "$R1FT/r1-link"
git -C "$R1FT" add r1-link
( cd "$R1FT" && ./scripts/check-secrets.sh --staged ) >"$WORK/r1-frz-T.raw" 2>&1 || true
save_log "$WORK/r1-frz-T.raw" "$LOGDIR/r1-freeze-typechange.log"
if grep -q "BLOCKED" "$WORK/r1-frz-T.raw" && grep -q "r1-link" "$WORK/r1-frz-T.raw"; then
  record R1-T REQUIRED 0 "freeze staged typechange: BLOCKED, destination named"
else
  record R1-T REQUIRED 1 "freeze staged typechange was not BLOCKED with dest named"
fi

echo "== C6a findings ledger identity =="
C6AM="$(make_clone c6a-mutant)"
C6AF="$(make_clone c6a-freeze)"
do_mutate_cwd_identity "$C6AM/scripts/check-findings-ledger.sh"
DECOY_A="$WORK/decoy-a"
mkdir -p "$DECOY_A/docs/review-2026-08-18-d055e"
git -C "$DECOY_A" init -q
git -C "$DECOY_A" config user.email "decoy@invalid"
git -C "$DECOY_A" config user.name "decoy"
plant_identity_lookalikes "$DECOY_A"
cp "$SRC/docs/review-2026-08-18-d055e/FINDINGS-LEDGER.tsv" \
   "$DECOY_A/docs/review-2026-08-18-d055e/FINDINGS-LEDGER.tsv"
printf 'X-CANARY\tr\ta\tCONFIRMED\tHIGH\tHIGH\t-\tREPAIR\n' \
  >> "$DECOY_A/docs/review-2026-08-18-d055e/FINDINGS-LEDGER.tsv"

( cd "$DECOY_A" && "$C6AM/scripts/check-findings-ledger.sh" ) >"$WORK/c6a-mut.raw" 2>&1 || true
save_log "$WORK/c6a-mut.raw" "$LOGDIR/c6a-mutant.log"
if grep -q "MISMATCH" "$WORK/c6a-mut.raw"; then
  record C6a-x CONTROL 0 "mutant from decoy cwd: read decoy ledger (MISMATCH)"
else
  record C6a-x CONTROL 1 "mutant from decoy cwd did not MISMATCH on decoy ledger"
fi

( cd "$DECOY_A" && "$C6AF/scripts/check-findings-ledger.sh" ) >"$WORK/c6a-frz.raw" 2>&1 || true
save_log "$WORK/c6a-frz.raw" "$LOGDIR/c6a-freeze.log"
if grep -q "all totals match D-057(1) as ruled" "$WORK/c6a-frz.raw"; then
  record C6a REQUIRED 0 "freeze from decoy cwd: still matches Sentinel ledger"
else
  record C6a REQUIRED 1 "freeze from decoy cwd did not match Sentinel ledger"
fi

echo "== C6b suite floors identity =="
C6BM="$(make_clone c6b-mutant)"
C6BF="$(make_clone c6b-freeze)"
do_mutate_cwd_identity "$C6BM/scripts/check-suite-floors.sh"
DECOY_B="$WORK/decoy-b"
mkdir -p "$DECOY_B/scripts" "$DECOY_B/docs"
git -C "$DECOY_B" init -q
plant_identity_lookalikes "$DECOY_B"
printf '%s\n' \
  'FOUNDRY_MIN_TESTS=99999' \
  'TS_MIN_TESTS=1' \
  'VERIFIER_MIN_TESTS=1' \
  'VERIFIER_MIN_SAMPLES=1' \
  'VERIFIER_MIN_TAMPER=1' \
  'VERIFIER_MIN_TAMPER_MODES=1' \
  > "$DECOY_B/scripts/test.sh"
printf '%s\n' '# decoy session-state, no live floor copies' > "$DECOY_B/docs/session-state.md"

( cd "$DECOY_B" && "$C6BM/scripts/check-suite-floors.sh" ) >"$WORK/c6b-mut.raw" 2>&1 || true
save_log "$WORK/c6b-mut.raw" "$LOGDIR/c6b-mutant.log"
if grep -q "99999" "$WORK/c6b-mut.raw"; then
  record C6b-x CONTROL 0 "mutant from decoy cwd: printed distinctive decoy floor"
else
  record C6b-x CONTROL 1 "mutant from decoy cwd did not print decoy floor"
fi

( cd "$DECOY_B" && "$C6BF/scripts/check-suite-floors.sh" ) >"$WORK/c6b-frz.raw" 2>&1 || true
save_log "$WORK/c6b-frz.raw" "$LOGDIR/c6b-freeze.log"
if grep -q "99999" "$WORK/c6b-frz.raw"; then
  record C6b REQUIRED 1 "freeze from decoy cwd printed decoy floor (identity failed)"
else
  record C6b REQUIRED 0 "freeze from decoy cwd did not print decoy floor"
fi

echo "== C6c install-hooks foreign repo =="
C6CM="$(make_clone c6c-mutant)"
C6CF="$(make_clone c6c-freeze)"
do_mutate_cwd_identity "$C6CM/scripts/install-hooks.sh"
FOREIGN="$WORK/foreign"
mkdir -p "$FOREIGN"
git -C "$FOREIGN" init -q
plant_identity_lookalikes "$FOREIGN"

( cd "$FOREIGN" && "$C6CM/scripts/install-hooks.sh" ) >"$WORK/c6c-mut.raw" 2>&1 || true
save_log "$WORK/c6c-mut.raw" "$LOGDIR/c6c-mutant.log"
FHOOK="$(git -C "$FOREIGN" config --get core.hooksPath || true)"
if [ -n "$FHOOK" ]; then
  record C6c-x CONTROL 0 "mutant wrote core.hooksPath into the foreign repo ($FHOOK)"
else
  record C6c-x CONTROL 1 "mutant did not write core.hooksPath into the foreign repo"
fi
git -C "$FOREIGN" config --unset-all core.hooksPath 2>/dev/null || true

( cd "$FOREIGN" && "$C6CF/scripts/install-hooks.sh" ) >"$WORK/c6c-frz.raw" 2>&1 || true
save_log "$WORK/c6c-frz.raw" "$LOGDIR/c6c-freeze.log"
FHOOK2="$(git -C "$FOREIGN" config --get core.hooksPath || true)"
if [ -z "$FHOOK2" ] && grep -qi "refus" "$WORK/c6c-frz.raw"; then
  record C6c REQUIRED 0 "freeze refused; foreign repo unchanged"
else
  record C6c REQUIRED 1 "freeze did not refuse, or foreign repo was written (hooksPath=$FHOOK2)"
fi

echo "== C6d test.sh decoy probe =="
C6DM="$(make_clone c6d-mutant)"
C6DF="$(make_clone c6d-freeze)"
do_mutate_c6d "$C6DM"

DECOY_D="$WORK/decoy-d"
mkdir -p "$DECOY_D"
git -C "$DECOY_D" init -q
plant_identity_lookalikes "$DECOY_D"
MARK="$WORK/decoy-fired.mark"
: > "$MARK"
for s in check-gate-immutability.sh check-secrets.sh check-findings-ledger.sh \
         check-suite-floors.sh check-vendor-honesty.sh check-rename-gate.sh \
         check-v1-index-ordering.sh check-class-coverage.sh check-eval-codes.sh \
         check-type-strings.sh check-label-integrity.sh check-label-prompt.sh \
         check-review-scope.sh install-hooks.sh mutate.sh test.sh; do
  printf '#!/usr/bin/env bash\necho "%s" >> "%s"\nexit 0\n' "$s" "$MARK" > "$DECOY_D/scripts/$s"
  chmod +x "$DECOY_D/scripts/$s"
done

: > "$MARK"
run_to 25 "$DECOY_D" "$C6DM/scripts/test.sh" >"$WORK/c6d-mut.raw" 2>&1 || true
save_log "$WORK/c6d-mut.raw" "$LOGDIR/c6d-mutant.log"
if [ -s "$MARK" ]; then
  record C6d-x CONTROL 0 "mutant test.sh from decoy cwd fired decoy shim(s)"
else
  record C6d-x CONTROL 1 "mutant test.sh from decoy cwd did not fire any decoy shim"
fi
{
  echo "--- decoy markers after mutant ---"
  cat "$MARK"
} >> "$LOGDIR/c6d-mutant.log"

: > "$MARK"
if [ -d "$SRC/ts/node_modules" ] && [ ! -e "$C6DF/ts/node_modules" ]; then
  ln -s "$SRC/ts/node_modules" "$C6DF/ts/node_modules"
fi
run_to 240 "$DECOY_D" "$C6DF/scripts/test.sh" >"$WORK/c6d-frz.raw" 2>&1 || true
save_log "$WORK/c6d-frz.raw" "$LOGDIR/c6d-freeze.log"
{
  echo "--- decoy markers after freeze ---"
  cat "$MARK"
} >> "$LOGDIR/c6d-freeze.log"
if [ -s "$MARK" ]; then
  record C6d-shim REQUIRED 1 "freeze test.sh from decoy cwd fired decoy shim(s)"
else
  record C6d-shim REQUIRED 0 "freeze test.sh from decoy cwd fired no decoy shim"
fi
if grep -Eq "secret guard:|gate immutability|GATE PASSED" "$WORK/c6d-frz.raw"; then
  record C6d-start REQUIRED 0 "freeze from decoy cwd: Sentinel stages actually started"
else
  record C6d-start REQUIRED 1 "freeze from decoy cwd: Sentinel stages did not start"
fi
if grep -q "GATE PASSED" "$WORK/c6d-frz.raw"; then
  echo "C6D_GATE=PASSED" > "$LOGDIR/c6d-gate.status"
else
  echo "C6D_GATE=NOT_OBSERVED" > "$LOGDIR/c6d-gate.status"
fi

echo
printf '  REQUIRED failures: %s\n' "$req_fail"
printf '  CONTROL  failures: %s\n' "$ctl_fail"
echo "$req_fail" > "$LOGDIR/required_fail.count"
echo "$ctl_fail" > "$LOGDIR/control_fail.count"
if [ "$ctl_fail" -ne 0 ]; then
  echo "CONTROL FAILURE — an exploit control did not demonstrate the hole."
  exit 2
fi
if [ "$req_fail" -ne 0 ]; then
  echo "REQUIRED FAILURES with controls holding."
  exit 1
fi
echo "F61ECCA verification: required items held."
exit 0
