#!/usr/bin/env bash
# V-1 D-059(7) gate binding. Runs in isolated clones. Never edits the live tree.
#
# G1  unchanged candidate — the real gate must pass
# G2  reverse-ordering mutant of check-secrets.sh — the gate must fail at the V-1 stage
# G2c causal twin: same mutant, but `check-v1-index-ordering.sh || fail=1` becomes `|| true`
#     — the V-1 FAIL line still prints and the otherwise-identical gate must pass, proving
#     the V-1 step (not a side effect of mutating check-secrets.sh) is what turned G2 red
#
# Deep-profile invocation is the same shared-prefix step; mutation reruns under --gate are
# not required unless that control flow moves. See COVERAGE.md.
set -uo pipefail

SRC="${1:?usage: v1-gate-binding.sh <repository-path> <log-directory>}"
LOGDIR="${2:?usage: v1-gate-binding.sh <repository-path> <log-directory>}"
SRC="$(cd "$SRC" && pwd -P)"
mkdir -p "$LOGDIR"
LOGDIR="$(cd "$LOGDIR" && pwd -P)"

if [ -n "$(ls -A "$LOGDIR" 2>/dev/null)" ]; then
    echo "preflight: log directory must be empty: $LOGDIR" >&2
    exit 2
fi

[ -x "$SRC/scripts/check-v1-index-ordering.sh" ] || { echo "preflight: candidate guard missing" >&2; exit 2; }
/usr/bin/grep -q 'check-v1-index-ordering.sh' "$SRC/scripts/test.sh" \
    || { echo "preflight: test.sh does not invoke the V-1 guard" >&2; exit 2; }

WORK="$(mktemp -d "${TMPDIR:-/tmp}/v1-gate-bind.XXXXXXXX")" || exit 2
trap 'rm -rf "$WORK"' EXIT

req_fail=0
ctl_fail=0
record() {
    local kind="$1" id="$2" held="$3" desc="$4" status
    if [ "$held" -eq 0 ]; then status="PASS"; else status="FAIL"; fi
    printf '  %-6s %-8s %s  %s\n' "$id" "$kind" "$status" "$desc"
    printf '%s\t%s\t%s\t%s\n' "$id" "$kind" "$status" "$desc" >> "$LOGDIR/matrix.tsv"
    if [ "$held" -ne 0 ]; then
        if [ "$kind" = "REQUIRED" ]; then req_fail=$((req_fail + 1)); else ctl_fail=$((ctl_fail + 1)); fi
    fi
}

prepare() {
    local label="$1"
    local root="$WORK/$label"
    git clone -q --local --no-hardlinks "$SRC" "$root" >/dev/null 2>&1 || return 1
    # Overlay working-tree candidate files so this harness can run before they are committed.
    cp "$SRC/scripts/check-v1-index-ordering.sh" "$root/scripts/check-v1-index-ordering.sh"
    cp "$SRC/scripts/test.sh" "$root/scripts/test.sh"
    chmod +x "$root/scripts/check-v1-index-ordering.sh" "$root/scripts/test.sh"
    if [ -d "$SRC/ts/node_modules" ] && [ ! -e "$root/ts/node_modules" ]; then
        ln -s "$SRC/ts/node_modules" "$root/ts/node_modules"
    fi
    git -C "$root" -c protocol.file.allow=always submodule update --init --recursive >/dev/null 2>&1 || true
    printf '%s' "$root"
}

mutate_cs() {
    python3 - "$1/scripts/check-secrets.sh" << 'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
lines = p.read_text().splitlines(keepends=True)
unset_idxs = [i for i, l in enumerate(lines)
              if l.strip() == "unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX"]
resolve_idxs = [i for i, l in enumerate(lines)
                if "git rev-parse --git-path index" in l and not l.lstrip().startswith("#")]
if len(unset_idxs) != 1 or len(resolve_idxs) != 1:
    sys.exit("mutate: expected one unset and one --git-path index assignment")
ui, ri = unset_idxs[0], resolve_idxs[0]
if ui >= ri:
    sys.exit("mutate: already reversed")
unset_line = lines.pop(ui)
ri -= 1
lines.insert(ri + 1, unset_line)
p.write_text("".join(lines))
PY
}

ignore_v1_step() {
    python3 - "$1/scripts/test.sh" << 'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
text = p.read_text()
old = "./scripts/check-v1-index-ordering.sh || fail=1"
new = "./scripts/check-v1-index-ordering.sh || true"
if text.count(old) != 1:
    sys.exit(f"ignore-v1: expected one invocation, found {text.count(old)}")
p.write_text(text.replace(old, new, 1))
PY
}

run_fast_gate() {
    local root="$1" log="$2"
    # Do not redirect HOME: the gate needs foundry on the operator PATH.
    (
        cd "$root" || exit 2
        unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX SENTINEL_GATE_TOKEN SENTINEL_GATE_REPO_ROOT
        ./scripts/test.sh
    ) >"$log" 2>&1
    echo $? > "${log}.rc"
}

echo "V-1 D-059(7) gate binding"
echo "source=$SRC"
echo "logs=$LOGDIR"

# G1 unchanged
echo
echo "== G1 unchanged fast gate =="
G1="$(prepare g1)" || { echo "clone G1 failed" >&2; exit 2; }
run_fast_gate "$G1" "$LOGDIR/g1.raw.log"
G1_RC="$(cat "$LOGDIR/g1.raw.log.rc")"
if /usr/bin/grep -q "GATE PASSED" "$LOGDIR/g1.raw.log" \
   && ! /usr/bin/grep -q "GATE FAILED" "$LOGDIR/g1.raw.log" \
   && /usr/bin/grep -q "V-1 index-path ordering: ok" "$LOGDIR/g1.raw.log" \
   && [ "$G1_RC" = "0" ]; then
    record REQUIRED G1 0 "unchanged fast gate passes; V-1 stage ok"
else
    record REQUIRED G1 1 "unchanged fast gate did not pass with V-1 ok (rc=$G1_RC)"
fi

# G2 mutant CS
echo
echo "== G2 reverse-ordering mutant of check-secrets.sh =="
G2="$(prepare g2)" || { echo "clone G2 failed" >&2; exit 2; }
mutate_cs "$G2" || { echo "mutate G2 failed" >&2; exit 2; }
run_fast_gate "$G2" "$LOGDIR/g2.raw.log"
G2_RC="$(cat "$LOGDIR/g2.raw.log.rc")"
if /usr/bin/grep -q "V-1 index-path ordering: FAIL" "$LOGDIR/g2.raw.log" \
   && /usr/bin/grep -q "GATE FAILED" "$LOGDIR/g2.raw.log" \
   && ! /usr/bin/grep -q "GATE PASSED" "$LOGDIR/g2.raw.log" \
   && [ "$G2_RC" != "0" ]; then
    record REQUIRED G2 0 "mutated check-secrets.sh makes the gate fail at the V-1 stage"
else
    record REQUIRED G2 1 "mutant did not fail the gate at the V-1 stage (rc=$G2_RC)"
fi

# G2-causal
echo
echo "== G2c causal twin: mutant plus V-1 step ignored =="
G2C="$(prepare g2c)" || { echo "clone G2c failed" >&2; exit 2; }
mutate_cs "$G2C" || { echo "mutate G2c failed" >&2; exit 2; }
ignore_v1_step "$G2C" || { echo "ignore-v1 G2c failed" >&2; exit 2; }
run_fast_gate "$G2C" "$LOGDIR/g2c.raw.log"
G2C_RC="$(cat "$LOGDIR/g2c.raw.log.rc")"
if /usr/bin/grep -q "V-1 index-path ordering: FAIL" "$LOGDIR/g2c.raw.log" \
   && /usr/bin/grep -q "GATE PASSED" "$LOGDIR/g2c.raw.log" \
   && [ "$G2C_RC" = "0" ]; then
    record CONTROL G2c 0 "same mutant with V-1 step ignored: FAIL still prints, gate passes"
else
    record CONTROL G2c 1 "causal twin did not isolate the V-1 step (rc=$G2C_RC)"
fi

echo
printf '  REQUIRED failures: %s\n' "$req_fail"
printf '  CONTROL  failures: %s\n' "$ctl_fail"
echo
echo "Stated explicitly, as D-059(7) requires: the V-1 guard covers only its enumerated"
echo "CS validation-refusal and HOOK commit-block facts. It is not general index-handling"
echo "evidence and is not evidence about any other script."

if [ "$ctl_fail" -ne 0 ]; then
    echo "CONTROL FAILURE — the harness is untrustworthy."
    exit 2
fi
if [ "$req_fail" -ne 0 ]; then
    echo "REQUIRED FAILURES with controls holding."
    exit 1
fi
echo "D-059(7) fast-profile gate binding held."
exit 0
