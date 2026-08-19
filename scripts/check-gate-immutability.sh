#!/usr/bin/env bash
# The gate's immutable-snapshot bootstrap, falsified (D-056(b), A-076).
#
# WHAT IS BEING PROTECTED. `scripts/test.sh` was twice corrupted mid-run by an agent editing
# it while bash was still reading it. Bash reads a script incrementally BY BYTE OFFSET, so an
# insertion shifts everything after it and the shell resumes mid-token. The first occurrence
# produced the worst possible artifact: a syntax error, no `GATE PASSED` line, and **exit 0**.
# A run that looks green to anything checking the status and is worthless.
#
# WHY THE OBVIOUS GUARD WAS REJECTED, because it is the thing a reader will propose again.
# "Hash the script at the start and re-check at the end" fails for the reason John gave: **the
# ending check can itself be skipped or corrupted when bash resumes at a shifted offset.** A
# guard that lives in the mutable body is exactly the code the attack can make unreachable.
#
# THE ARGUMENT THIS HARNESS FALSIFIES, and it is deliberately not "an edit is detected":
#
#     **The running gate never reads the mutable file after the bootstrap, so an edit cannot
#     corrupt the running parser AT ALL — and a run whose source changed is refused a
#     zero exit even though the run itself was sound.**
#
# Detection is the weaker second half. The first half — that the corruption is IMPOSSIBLE
# rather than caught — is what makes this different from the design that was rejected.
#
# HOW THIS AVOIDS TESTING A COPY THAT CAN DRIFT. The bootstrap is EXTRACTED VERBATIM from
# `scripts/test.sh` between its two markers and pasted into a synthetic one-line script. This
# harness therefore exercises the shipped bytes, not a paraphrase of them. If the markers stop
# matching, this fails loudly rather than silently testing nothing — which is the dead-probe
# failure mode this repository has recorded five times.
#
# WHY A SYNTHETIC SCRIPT RATHER THAN THE REAL GATE: the real gate takes minutes and would have
# to be mutated mid-run to test property 2. The bootstrap is independent of the body it
# protects, so a body that sleeps and echoes exercises it exactly as well, in under a second.
#
# THE EDIT SHAPE IS LOAD-BEARING, AND THE FIRST VERSION OF THIS FILE GOT IT WRONG.
# Property 2 originally replaced the original with `mv`. **That test passes against a script
# with NO protection whatsoever**, because `mv` renames a NEW inode into place and the running
# shell keeps reading the old one — measured across bodies from 442 bytes to 1.5 MB, every one
# completed cleanly. It was caught by mutating the bootstrap to remove its `exec`: the harness
# still reported 4/4, i.e. it was blind to the one property it exists to establish.
#
# **The hazard is an IN-PLACE rewrite — truncate and write the same inode — which is what
# Python's `open(path,"w")` and most editors do, and is what corrupted two real gate runs.**
# Under that edit the unprotected control dies with a shell error and exit 127 at every size.
# So this file now edits in place, and runs an UNPROTECTED control through the identical probe
# first: if the control is NOT corrupted, the probe has stopped being dangerous and any pass
# it reports afterwards is meaningless.
#
# WHAT THIS DOES NOT ESTABLISH (residual). It proves the bootstrap's four properties on a
# synthetic body. It does NOT prove the real gate's stages are correct, and it does not defend
# any other file — a reviewer editing `verifier/verify.py` mid-run is out of scope here and is
# covered by the frozen review worktree, which is the broader protection.
set -uo pipefail

ROOT="$(git rev-parse --show-toplevel)"
GATE="$ROOT/scripts/test.sh"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/gate-immutability.XXXXXXXX")"
trap 'rm -rf "$WORK"' EXIT

fail=0
note() { printf '  %s\n' "$1"; }
bad() { printf '  FAIL  %s\n' "$1"; fail=1; }

# --- Extract the shipped bootstrap, and refuse to run on a miss -------------------------
BOOTSTRAP="$WORK/bootstrap.sh"
awk '/^# >>> GATE BOOTSTRAP/{f=1} f{print} /^# <<< GATE BOOTSTRAP/{f=0}' "$GATE" > "$BOOTSTRAP"

if [ ! -s "$BOOTSTRAP" ] || ! grep -q "SENTINEL_GATE_SNAPSHOT" "$BOOTSTRAP"; then
    echo "gate immutability: COULD NOT EXTRACT the bootstrap from scripts/test.sh."
    echo "  The markers '# >>> GATE BOOTSTRAP' / '# <<< GATE BOOTSTRAP' did not yield a block."
    echo "  Refusing to report a pass on an empty probe — that is the dead-probe failure mode."
    exit 1
fi
note "extracted $(grep -c '' "$BOOTSTRAP") lines of bootstrap verbatim from scripts/test.sh"

# --- Build a synthetic gate carrying that exact bootstrap -------------------------------
# The body sleeps so property 2 has a window to edit the original in, and echoes its args so
# property 3 is observable. `git rev-parse` is not used: the synthetic script must not depend
# on being inside the repository.
make_subject() {
    local path="$1"
    {
        echo '#!/usr/bin/env bash'
        echo 'set -euo pipefail'
        cat "$BOOTSTRAP"
        echo 'echo "ARGS:[$*]"'
        echo 'sleep "${SUBJECT_SLEEP:-0}"'
        echo 'echo "BODY COMPLETED"'
    } > "$path"
    chmod +x "$path"
}

# ---------------------------------------------------------------------------------------
# 1. Unchanged source succeeds.
# ---------------------------------------------------------------------------------------
printf '\n1. unchanged source\n'
SUBJ="$WORK/subject1.sh"; make_subject "$SUBJ"
out1="$("$SUBJ" 2>&1)"; rc1=$?
if [ "$rc1" -eq 0 ] && printf '%s' "$out1" | grep -q "BODY COMPLETED"; then
    note "exit 0 and the body ran"
else
    bad "an untouched script must succeed; got rc=$rc1 out=[$out1]"
fi

# ---------------------------------------------------------------------------------------
# 2. Editing the original DURING execution: the parser must not be corrupted, and the run
#    must not be allowed a zero exit.
#
#    THE INSERTION IS AT THE TOP ON PURPOSE. Appending to the end is the easy case; the
#    corruption this exists to stop comes from INSERTING lines ABOVE the execution point,
#    which is what shifts every later byte offset. This reproduces the real incident.
# ---------------------------------------------------------------------------------------
# Rewrite `$1` IN PLACE, prepending 40 lines so every later byte offset shifts. Same inode,
# which is the whole point: a rename would leave the running shell on the old inode and prove
# nothing. This is byte-for-byte the operation that corrupted the two real runs.
edit_in_place() {
    python3 -c '
import sys
target, pristine = sys.argv[1], sys.argv[2]
body = open(pristine).read()
with open(target, "w") as fh:
    fh.write("".join("# shifting line %d\n" % i for i in range(40)) + body)
' "$1" "$2"
}

printf '\n2a. CONTROL: the probe must actually be dangerous to an unprotected script\n'
CTRL="$WORK/control.sh"
{ echo '#!/usr/bin/env bash'; echo 'set -euo pipefail'; echo 'echo "ARGS:[$*]"'
  echo 'sleep "${SUBJECT_SLEEP:-0}"'; echo 'echo "BODY COMPLETED"'; } > "$CTRL"
chmod +x "$CTRL"
cp "$CTRL" "$WORK/control.pristine"
SUBJECT_SLEEP=3 "$CTRL" > "$WORK/outc.txt" 2>&1 &
ctrl_pid=$!
sleep 1
edit_in_place "$CTRL" "$WORK/control.pristine"
wait "$ctrl_pid"; rcc=$?
outc="$(cat "$WORK/outc.txt")"
if [ "$rcc" -ne 0 ] && ! printf '%s' "$outc" | grep -q "BODY COMPLETED"; then
    note "an unprotected script IS corrupted by this edit (exit $rcc, body never completed)"
else
    bad "THE PROBE IS NOT DANGEROUS — an unprotected script survived it (rc=$rcc). Everything"
    bad "  below would pass for the wrong reason. Fix the probe before trusting property 2."
fi

printf '\n2b. the protected script under the SAME edit\n'
SUBJ2="$WORK/subject2.sh"; make_subject "$SUBJ2"
cp "$SUBJ2" "$WORK/subject2.pristine"
SUBJECT_SLEEP=3 "$SUBJ2" > "$WORK/out2.txt" 2>&1 &
subj_pid=$!
sleep 1
edit_in_place "$SUBJ2" "$WORK/subject2.pristine"
wait "$subj_pid"; rc2=$?
out2="$(cat "$WORK/out2.txt")"

if printf '%s' "$out2" | grep -q "BODY COMPLETED"; then
    note "the body ran to completion — the mid-run edit did NOT corrupt the parser"
else
    bad "the running parser was disturbed by an edit to the original: [$out2]"
fi
if printf '%s' "$out2" | grep -qiE "syntax error|unexpected token|command not found"; then
    bad "shell-level corruption appeared in the output: [$out2]"
else
    note "no syntax error or shifted-offset damage in the output"
fi
if [ "$rc2" -ne 0 ]; then
    note "exit $rc2 — a changed source is refused a zero exit"
else
    bad "a run whose source changed exited 0; this is the exact defect (rc=$rc2)"
fi
if printf '%s' "$out2" | grep -q "GATE SOURCE CHANGED DURING EXECUTION"; then
    note "and it says so, rather than failing for an unrelated reason"
else
    bad "no 'gate source changed' diagnostic; a bare nonzero could be anything: [$out2]"
fi

# ---------------------------------------------------------------------------------------
# 3. Arguments survive the exec.
#    A bootstrap that dropped `--gate` would turn every deep run into a fast one while the
#    banner still said "profile: gate" — a silent downgrade of the evidence.
# ---------------------------------------------------------------------------------------
printf '\n3. arguments preserved across the exec\n'
SUBJ3="$WORK/subject3.sh"; make_subject "$SUBJ3"
out3="$("$SUBJ3" --gate second "third arg" 2>&1)" || true
if printf '%s' "$out3" | grep -q 'ARGS:\[--gate second third arg\]'; then
    note "all three arguments arrived, including the one containing a space"
else
    bad "arguments were altered by the bootstrap: [$out3]"
fi

# ---------------------------------------------------------------------------------------
# 4. Temporary state is removed — on the success path AND on the failure path.
#    Checking only the success path would miss the case that actually leaks: a run that
#    aborts is exactly when a stale snapshot would be left behind.
# ---------------------------------------------------------------------------------------
printf '\n4. snapshot cleanup\n'
before="$(find "${TMPDIR:-/tmp}" -maxdepth 1 -name 'sentinel-gate.*' 2>/dev/null | wc -l | tr -d ' ')"
SUBJ4="$WORK/subject4.sh"; make_subject "$SUBJ4"
"$SUBJ4" >/dev/null 2>&1 || true
SUBJ5="$WORK/subject5.sh"
{ echo '#!/usr/bin/env bash'; echo 'set -euo pipefail'; cat "$BOOTSTRAP"; echo 'exit 9'; } > "$SUBJ5"
chmod +x "$SUBJ5"
"$SUBJ5" >/dev/null 2>&1; rc5=$?
after="$(find "${TMPDIR:-/tmp}" -maxdepth 1 -name 'sentinel-gate.*' 2>/dev/null | wc -l | tr -d ' ')"
if [ "$before" = "$after" ]; then
    note "no snapshot left behind by either the passing or the failing run ($before before, $after after)"
else
    bad "snapshot files leaked: $before before, $after after"
fi
if [ "$rc5" -eq 9 ]; then
    note "and the body's own exit code survives the trap (9 preserved, not overwritten)"
else
    bad "the exit trap changed a failing body's exit code: expected 9, got $rc5"
fi

# ---------------------------------------------------------------------------------------
# 5. A SIBLING INVOCATION SHAPE, and it is here because it caught a live defect.
#
#    `SENTINEL_GATE_SNAPSHOT` is EXPORTED, so every child of a running gate inherits it. The
#    first bootstrap skipped its work whenever that variable was merely SET, which meant any
#    script carrying this block and invoked BY the gate decided it was already a snapshot and
#    ran unprotected from its own mutable file. Found by wiring this harness in as a gate
#    stage and watching it get corrupted.
#
#    The fix compares the variable to the path actually executing. This asserts that: with the
#    variable set to somebody else's snapshot, the subject must STILL protect itself.
# ---------------------------------------------------------------------------------------
printf '\n5. inherited SENTINEL_GATE_SNAPSHOT from a parent (sibling invocation shape)\n'
SUBJ6="$WORK/subject6.sh"; make_subject "$SUBJ6"
cp "$SUBJ6" "$WORK/subject6.pristine"
SENTINEL_GATE_SNAPSHOT="$WORK/some-other-parents-snapshot" \
SENTINEL_GATE_SOURCE="$WORK/some-other-parents-source" \
SENTINEL_GATE_SOURCE_SHA="0000000000000000000000000000000000000000000000000000000000000000" \
SUBJECT_SLEEP=3 "$SUBJ6" > "$WORK/out6.txt" 2>&1 &
subj6_pid=$!
sleep 1
edit_in_place "$SUBJ6" "$WORK/subject6.pristine"
wait "$subj6_pid"; rc6=$?
out6="$(cat "$WORK/out6.txt")"
if printf '%s' "$out6" | grep -q "BODY COMPLETED"; then
    note "protected itself despite the inherited variable — the body survived the edit"
else
    bad "a child of a running gate ran UNPROTECTED and was corrupted: [$out6]"
fi
if [ "$rc6" -ne 0 ]; then
    note "and still refused a zero exit (exit $rc6)"
else
    bad "a child whose own source changed exited 0 (rc=$rc6)"
fi

printf '\n'
if [ "$fail" -ne 0 ]; then
    echo "gate immutability: FAILED — the bootstrap does not hold its five properties."
    exit 1
fi
echo "gate immutability: 5/5 — unchanged run passes · mid-run edit cannot corrupt the parser"
echo "  and is refused a zero exit · arguments preserved · snapshot cleaned up on both paths"
echo "  · a child inheriting a parent gate's snapshot variable still protects itself"
