#!/usr/bin/env bash
# The gate's supervisor + unlinked-body design, falsified (D-057(3), A-077).
#
# WHAT IS BEING PROTECTED. `scripts/test.sh` was twice corrupted mid-run by an in-place rewrite
# while bash was reading it. Bash reads a script incrementally BY BYTE OFFSET, so an insertion
# shifts everything after it and the shell resumes mid-token. The worst artifact it produced was
# a syntax error, no `GATE PASSED`, and **exit 0**.
#
# TWO PREVIOUS DESIGNS FAILED AND BOTH ARE RECORDED, because each will be proposed again:
#   1. Hash at start, re-check at end — rejected by John before it was built. The ending check
#      lives in the mutable body and is the code an edit makes unreachable.
#   2. Copy to a temp file and `exec` into it (A-076). It claimed the snapshot was "a private
#      file nobody has a path to". FALSE: the path was exported to every child in
#      `SENTINEL_GATE_SNAPSHOT` and visible to any same-user sibling in `ps`. **R1/R3 rewrote
#      the running snapshot through BOTH routes — 6 of 8 real-gate trials corrupted, three of
#      them exit 0 with no GATE PASSED — while the in-body trap certified "source unchanged".**
#
# THIS FILE ALSO FAILED ONCE, AND THAT IS WHY IT NOW CARRIES CONTROLS. Its first version edited
# the original with `mv`, which renames a NEW inode and leaves the running shell on the old one.
# **That test passes against a script with no protection whatsoever** — measured from 442 bytes
# to 1.5 MB. It reported 4/4 with the protection removed. Every dangerous probe below therefore
# runs against an UNPROTECTED CONTROL first: if the control is not corrupted, the probe has
# stopped being dangerous and every pass after it is meaningless.
#
# THE ARGUMENT NOW BEING FALSIFIED, in the shape D-057(3) requires:
#
#   1. After bootstrap the body has NO writable filesystem pathname reachable by a child or a
#      same-user sibling.
#   2. No writable backing path is exported in the environment or exposed in `ps`.
#   3. A supervisor OUTSIDE the body refuses success unless the body reaches explicit
#      completion. **EXIT STATUS 0 IS NOT SUCCESS.**
#   4. The supervisor — not a trap inside the possibly-damaged body — detects source change.
#   5. Arguments are preserved and temporary state is cleaned up.
#   6. Operator cancellation still works.
#
# WHAT THIS DOES NOT ESTABLISH (residual). It exercises the bootstrap on SYNTHETIC bodies. It
# does not prove the gate's stages are correct, and it defends only `scripts/test.sh`. A
# reviewer editing `verifier/verify.py` mid-run is out of scope and is covered by the frozen
# review worktree. It also cannot rule out a same-user actor that can READ the body's
# environment forging the completion token; that is stated rather than defended against.
set -uo pipefail

# --- Sentinel repository identity (D-060(2)) ---------------------------------
# Derived from THIS FILE's own location, never the caller's working directory, so a
# run from an unrelated directory or a foreign repository still inspects Sentinel.
# Every step is checked: `cd ""` returns 0 and does not abort even under `set -e`.
_sentinel_self="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)" || _sentinel_self=""
if [ -z "$_sentinel_self" ]; then
    echo "  FAIL  cannot resolve this script's own location; refusing." >&2; exit 2
fi
ROOT="$(cd -- "$_sentinel_self" 2>/dev/null && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR git rev-parse --show-toplevel 2>/dev/null)" || ROOT=""
if [ -z "$ROOT" ] || [ ! -e "$ROOT/scripts/test.sh" ] || [ ! -e "$ROOT/.githooks/pre-commit" ]; then
    echo "  FAIL  this script is not inside the Sentinel repository; refusing." >&2; exit 2
fi
cd "$ROOT" || { echo "  FAIL  cannot enter the Sentinel repository root; refusing." >&2; exit 2; }
# CALLER GIT OVERRIDES ARE REMOVED ONCE, HERE, BEFORE ANY BODY-LEVEL GIT CALL (12-F2).
# Scrubbing only the identity probe left every later `git` inheriting the caller's
# environment: GIT_DIR alone made this guard report clean over a live credential, and made
# install-hooks write into a victim repository. GIT_PREFIX is included although inert on
# git 2.50.1 — an inert variable today is not a guarantee tomorrow.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
GATE="$ROOT/scripts/test.sh"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/gate-immutability.XXXXXXXX")"
trap 'rm -rf "$WORK"' EXIT

fail=0
note() { printf '  %s\n' "$1"; }
bad() { printf '  FAIL  %s\n' "$1"; fail=1; }

BOOTSTRAP="$WORK/bootstrap.sh"
awk '/^# >>> GATE BOOTSTRAP/{f=1} f{print} /^# <<< GATE BOOTSTRAP/{f=0}' "$GATE" > "$BOOTSTRAP"
if [ ! -s "$BOOTSTRAP" ] || ! grep -q "SENTINEL_GATE_TOKEN" "$BOOTSTRAP"; then
    echo "gate immutability: COULD NOT EXTRACT the bootstrap from scripts/test.sh."
    echo "  Refusing to report a pass on an empty probe — that is the dead-probe failure mode."
    exit 1
fi
note "extracted $(grep -c '' "$BOOTSTRAP") lines of bootstrap verbatim from scripts/test.sh"

# A subject that completes properly, and one that does not.
make_subject() {
    { echo '#!/usr/bin/env bash'; echo 'set -euo pipefail'; cat "$BOOTSTRAP"
      echo 'echo "ARGS:[$*]"'; echo 'sleep "${SUBJ_SLEEP:-0}"'
      echo 'echo "BODY COMPLETED"'; echo '_gate_complete'; } > "$1"
    chmod +x "$1"
}
make_unprotected() {
    { echo '#!/usr/bin/env bash'; echo 'set -euo pipefail'; echo 'echo "ARGS:[$*]"'
      echo 'sleep "${SUBJ_SLEEP:-0}"'; echo 'echo "BODY COMPLETED"'; } > "$1"
    chmod +x "$1"
}
edit_in_place() {
    python3 -c '
import sys
target, pristine = sys.argv[1], sys.argv[2]
body = open(pristine).read()
with open(target, "w") as fh:
    fh.write("".join("# shifting line %d\n" % i for i in range(40)) + body)
' "$1" "$2"
}

# --- 1. unchanged source and body ------------------------------------------------------
printf '\n1. unchanged source and body\n'
S1="$WORK/s1.sh"; make_subject "$S1"
out1="$("$S1" 2>&1)"; rc1=$?
[ "$rc1" -eq 0 ] && printf '%s' "$out1" | grep -q "BODY COMPLETED" \
    && note "exit 0, body ran, completion token accepted" \
    || bad "an untouched subject must succeed; rc=$rc1 out=[$out1]"

# --- 2. the ORIGINAL source edited during execution -------------------------------------
printf '\n2a. CONTROL: an unprotected script must be corrupted by this probe\n'
C="$WORK/ctrl.sh"; make_unprotected "$C"; cp "$C" "$WORK/ctrl.pristine"
SUBJ_SLEEP=3 "$C" >"$WORK/outc.txt" 2>&1 & cp_pid=$!
sleep 1; edit_in_place "$C" "$WORK/ctrl.pristine"; wait $cp_pid; rcc=$?
if [ "$rcc" -ne 0 ] && ! grep -q "BODY COMPLETED" "$WORK/outc.txt"; then
    note "unprotected control corrupted (exit $rcc) — the probe is dangerous"
else
    bad "THE PROBE IS NOT DANGEROUS (control rc=$rcc); everything below would pass falsely"
fi

printf '\n2b. the protected subject under the same edit\n'
S2="$WORK/s2.sh"; make_subject "$S2"; cp "$S2" "$WORK/s2.pristine"
SUBJ_SLEEP=3 "$S2" >"$WORK/out2.txt" 2>&1 & s2_pid=$!
sleep 1; edit_in_place "$S2" "$WORK/s2.pristine"; wait $s2_pid; rc2=$?
grep -q "BODY COMPLETED" "$WORK/out2.txt" \
    && note "body ran to completion — the edit could not reach it" \
    || bad "the running body was disturbed: $(cat "$WORK/out2.txt")"
grep -qiE "syntax error|unexpected token|command not found" "$WORK/out2.txt" \
    && bad "shell-level corruption appeared" || note "no shifted-offset damage"
[ "$rc2" -ne 0 ] && note "exit $rc2 — a changed source is refused a zero exit" \
    || bad "a run whose source changed exited 0"

# --- 3. a CHILD trying to recover and rewrite the body via inherited environment ---------
printf '\n3. child attacks the body through inherited environment\n'
S3="$WORK/s3.sh"
{ echo '#!/usr/bin/env bash'; echo 'set -euo pipefail'; cat "$BOOTSTRAP"
  echo 'bash -c '"'"'
    hit=0
    for v in $(env | grep -oE "^SENTINEL_[A-Z_]*"); do
      p="$(printenv "$v")"
      [ -f "$p" ] && { echo "CHILD-FOUND-PATH:$v"; hit=1; }
    done
    for fd in 9 10 11; do
      if [ -e /dev/fd/$fd ] && : > /dev/fd/$fd 2>/dev/null; then echo "CHILD-WROTE-FD:$fd"; hit=1; fi
    done
    python3 - <<PY 2>/dev/null || true
import os
for fd in (9,10,11):
    try:
        os.ftruncate(fd,0); print(f"CHILD-TRUNCATED:{fd}")
    except OSError: pass
PY
    [ "$hit" = 0 ] && echo "CHILD-FOUND-NOTHING"
  '"'"''
  echo 'echo "BODY COMPLETED"'; echo '_gate_complete'; } > "$S3"
chmod +x "$S3"
out3="$("$S3" 2>&1)"; rc3=$?
printf '%s' "$out3" | grep -qE "CHILD-FOUND-PATH|CHILD-WROTE-FD|CHILD-TRUNCATED" \
    && bad "a child reached a writable handle on the body: $(printf '%s' "$out3" | grep -E 'CHILD-' | tr '\n' ' ')" \
    || note "child found no writable path and no writable descriptor"
[ "$rc3" -eq 0 ] && note "and the run still completed normally" || bad "child probe broke the run (rc=$rc3)"

# --- 4. a SIBLING trying to recover the body from ps -------------------------------------
printf '\n4. sibling attacks the body through ps\n'
S4="$WORK/s4.sh"; make_subject "$S4"
SUBJ_SLEEP=3 "$S4" >"$WORK/out4.txt" 2>&1 & s4_pid=$!
sleep 1
sib_paths="$(ps -o command= | grep -oE '/[^ ]*sentinel-gate\.[A-Za-z0-9]+' | sort -u)"
wrote=0
for p in $sib_paths; do [ -f "$p" ] && { : > "$p" 2>/dev/null && wrote=1; }; done
wait $s4_pid; rc4=$?
if [ -n "$sib_paths" ]; then
    bad "a sibling recovered a snapshot path from ps: $sib_paths"
elif [ "$wrote" -ne 0 ]; then
    bad "a sibling wrote to a recovered path"
else
    note "ps exposes no writable backing path (body appears only as /dev/fd/N)"
fi
grep -q "BODY COMPLETED" "$WORK/out4.txt" && [ "$rc4" -eq 0 ] \
    && note "and the run completed normally under sibling inspection" \
    || bad "sibling probe disturbed the run (rc=$rc4)"

# --- 5. a body that exits 0 WITHOUT reaching completion ----------------------------------
printf '\n5. body exits 0 without completing — EXIT 0 IS NOT SUCCESS\n'
S5="$WORK/s5.sh"
{ echo '#!/usr/bin/env bash'; echo 'set -euo pipefail'; cat "$BOOTSTRAP"
  echo 'echo "silently skipping the completion protocol"'; echo 'exit 0'; } > "$S5"
chmod +x "$S5"
out5="$("$S5" 2>&1)"; rc5=$?
[ "$rc5" -ne 0 ] && note "refused with exit $rc5" || bad "a body that exited 0 without completing was ACCEPTED"
printf '%s' "$out5" | grep -q "DID NOT REACH COMPLETION" \
    && note "and says so, rather than failing for an unrelated reason" \
    || bad "no completion diagnostic: [$out5]"

# --- 6. arguments preserved --------------------------------------------------------------
printf '\n6. arguments preserved across the supervisor boundary\n'
S6="$WORK/s6.sh"; make_subject "$S6"
out6="$("$S6" --gate second "third arg" 2>&1)" || true
printf '%s' "$out6" | grep -q 'ARGS:\[--gate second third arg\]' \
    && note "all three arguments arrived, including the one with a space" \
    || bad "arguments altered: [$out6]"

# --- 7. temporary state cleaned up -------------------------------------------------------
printf '\n7. cleanup on success and on failure\n'
before="$(find "${TMPDIR:-/tmp}" -maxdepth 1 -name 'sentinel-gate.*' 2>/dev/null | wc -l | tr -d ' ')"
S7="$WORK/s7.sh"; make_subject "$S7"; "$S7" >/dev/null 2>&1 || true
S8="$WORK/s8.sh"
{ echo '#!/usr/bin/env bash'; echo 'set -euo pipefail'; cat "$BOOTSTRAP"; echo 'exit 9'; } > "$S8"
chmod +x "$S8"; "$S8" >/dev/null 2>&1; rc8=$?
after="$(find "${TMPDIR:-/tmp}" -maxdepth 1 -name 'sentinel-gate.*' 2>/dev/null | wc -l | tr -d ' ')"
[ "$before" = "$after" ] && note "no temp file left behind ($before before, $after after)" \
    || bad "temp state leaked: $before -> $after"
[ "$rc8" -ne 0 ] && note "a failing body is refused (exit $rc8), not silently accepted" \
    || bad "a body exiting 9 was accepted"

# --- 8. operator cancellation -------------------------------------------------------------
printf '\n8. operator cancellation\n'
S9="$WORK/cancelme.sh"; make_subject "$S9"
SUBJ_SLEEP=10 "$S9" >/dev/null 2>&1 & c_pid=$!
sleep 1
if pgrep -f "cancelme.sh" >/dev/null 2>&1; then
    note "the supervisor is findable by its own script name (pkill -f <script> works again)"
else
    bad "no process matches the script name — operator cancellation by name is broken"
fi
kill "$c_pid" 2>/dev/null
sleep 0.5
pgrep -f "cancelme.sh" >/dev/null 2>&1 \
    && bad "supervisor survived SIGTERM" || note "SIGTERM stopped the run"
wait "$c_pid" 2>/dev/null

# --- 9. concurrent gates ------------------------------------------------------------------
printf '\n9. two gates concurrently\n'
SA="$WORK/sa.sh"; SB="$WORK/sb.sh"; make_subject "$SA"; make_subject "$SB"
SUBJ_SLEEP=2 "$SA" >"$WORK/outa.txt" 2>&1 & pa=$!
SUBJ_SLEEP=2 "$SB" >"$WORK/outb.txt" 2>&1 & pb=$!
wait $pa; ra=$?; wait $pb; rb=$?
if [ "$ra" -eq 0 ] && [ "$rb" -eq 0 ] \
   && grep -q "BODY COMPLETED" "$WORK/outa.txt" && grep -q "BODY COMPLETED" "$WORK/outb.txt"; then
    note "both completed independently — no shared process state"
else
    bad "concurrent gates interfered (rc $ra/$rb)"
fi

# --- 10. A SUBJECT INVOKED BY A RUNNING GATE (the inheritance route, twice now) ----------
#
#     `SENTINEL_GATE_TOKEN` is exported. A gate STAGE carrying this same bootstrap would see it
#     already set, conclude it was itself the body, and run UNPROTECTED from its own mutable
#     file. That is exactly the defect A-076 shipped with `SENTINEL_GATE_SNAPSHOT`, which
#     R1-F1 confirmed at CRITICAL — and it was reintroduced here with the new variable name.
#     It was caught only because this harness runs AS a gate stage and failed there while
#     passing standalone. This case makes that catch deliberate instead of lucky.
printf '\n10. subject invoked with a parent gate token in the environment\n'
S10="$WORK/s10.sh"; make_subject "$S10"; cp "$S10" "$WORK/s10.pristine"
SENTINEL_GATE_TOKEN="a-parent-gates-token" SUBJ_SLEEP=3 "$S10" >"$WORK/out10.txt" 2>&1 & s10_pid=$!
sleep 1
edit_in_place "$S10" "$WORK/s10.pristine"
wait $s10_pid; rc10=$?
if grep -q "BODY COMPLETED" "$WORK/out10.txt"; then
    note "protected itself despite the inherited token — the edit could not reach it"
else
    bad "a subject invoked by a running gate ran UNPROTECTED: $(cat "$WORK/out10.txt")"
fi
[ "$rc10" -ne 0 ] && note "and still refused a zero exit (exit $rc10)" \
    || bad "a child whose own source changed exited 0"

printf '\n'
if [ "$fail" -ne 0 ]; then
    echo "gate immutability: FAILED — the supervisor design does not hold its ten properties."
    exit 1
fi
echo "gate immutability: 10/10 — unchanged run · mid-run source edit cannot reach the body"
echo "  · child finds no writable path or descriptor · ps exposes no backing path"
echo "  · EXIT 0 WITHOUT COMPLETION IS REFUSED · arguments preserved · cleanup on both paths"
echo "  · operator cancellation works · concurrent gates independent"
echo "  · a subject invoked by a running gate still protects itself"
