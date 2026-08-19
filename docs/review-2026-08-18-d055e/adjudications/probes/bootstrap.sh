# >>> GATE BOOTSTRAP (D-056(b)) >>>
# Everything between these markers is extracted VERBATIM by
# scripts/check-gate-immutability.sh and exercised against a synthetic script. Editing it
# without running that guard is editing an unfalsified protection.
#
# THE ARGUMENT (repair-protocol step 1): **a gate result is a statement about a specific
# script body, so the body that produced it must be immutable for the whole run** — otherwise
# the result cannot be attributed to anything and a PASS means nothing.
#
# WHY NOT THE OBVIOUS DESIGN. The first proposal was "hash the script at the start and
# re-check at the end". **John rejected it on its merits and the reason is the whole
# difficulty: the ending check can itself be skipped or corrupted when bash resumes at a
# shifted byte offset.** Bash reads a script incrementally BY OFFSET; inserting lines shifts
# everything after them, so a guard living in the mutable body is exactly the code an edit
# can make unreachable. A check that the attack can delete is not a check.
#
# WHAT THIS DOES INSTEAD. The mutable file's only job is to copy itself to a snapshot and
# `exec` into it. From the `exec` onward bash is reading a private file nobody else has a
# path to, so **an edit to the original cannot corrupt the running parser at all** — the
# failure mode is removed rather than detected. The original is still re-hashed at exit, and
# THAT check lives in the snapshot, where no edit can reach it.
#
# THE COPY ITSELF IS THE ONE RACE LEFT, so it is checked rather than assumed: the source is
# hashed BEFORE and AFTER the copy and the copy is hashed too. A write landing mid-copy moves
# one of the three and the run refuses to start. A torn read that happened to leave the file
# byte-identical is indistinguishable from no write at all, which is the honest bound.
#
# THE RE-EXEC IS KEYED ON THIS SCRIPT'S OWN PATH, NOT ON A BARE ENVIRONMENT FLAG, AND THAT
# CORRECTION CAME FROM A REAL FAILURE. The first version skipped the bootstrap whenever
# `SENTINEL_GATE_SNAPSHOT` was merely SET. But it is EXPORTED to every child process, so the
# moment the gate ran another script carrying this same block, the child saw the parent's
# variable, concluded it was already a snapshot, and **ran unprotected straight from its own
# mutable file** — which the immutability harness then caught by being corrupted. Comparing
# the variable to the path actually executing makes the decision about THIS file rather than
# about whether any gate anywhere is running.
_gate_self="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
if [ "${SENTINEL_GATE_SNAPSHOT:-}" != "$_gate_self" ]; then
    _gate_src="$_gate_self"
    _gate_before="$(shasum -a 256 <"$_gate_src" | cut -d' ' -f1)"
    _gate_snap="$(mktemp "${TMPDIR:-/tmp}/sentinel-gate.XXXXXXXX")"
    # RESOLVED THE SAME WAY `_gate_self` IS, and this is not a nicety. On macOS `$TMPDIR` sits
    # under `/var`, which is a symlink to `/private/var`; `$(cd … && pwd)` resolves it and
    # `mktemp` does not. Comparing the two unresolved put the snapshot's own path permanently
    # unequal to itself, so the snapshot re-exec'd forever — an infinite loop, caught by the
    # harness hanging. Both sides now go through the identical resolution.
    _gate_snap="$(cd "$(dirname "$_gate_snap")" && pwd)/$(basename "$_gate_snap")"
    cat <"$_gate_src" >"$_gate_snap"
    _gate_copy="$(shasum -a 256 <"$_gate_snap" | cut -d' ' -f1)"
    _gate_after="$(shasum -a 256 <"$_gate_src" | cut -d' ' -f1)"
    if [ "$_gate_before" != "$_gate_after" ] || [ "$_gate_copy" != "$_gate_before" ]; then
        rm -f "$_gate_snap"
        echo "GATE SOURCE CHANGED WHILE BEING SNAPSHOTTED — refusing to start." >&2
        echo "  Nothing ran. Re-run once the tree is settled." >&2
        exit 3
    fi
    # `exec` so there is no parent process still holding the mutable file open, and "$@" so
    # every original argument survives — a bootstrap that silently dropped `--gate` would
    # turn every deep run into a fast one while printing the deep banner.
    #
    # ONE OPERATIONAL CONSEQUENCE, recorded because it will surprise somebody mid-incident.
    # After the exec this process is `bash /tmp/sentinel-gate.XXXXXXXX --gate`: the original
    # path is GONE from the command line, so **`pkill -f "scripts/test.sh"` no longer finds a
    # running gate.** Use `pkill -f sentinel-gate`. Found while killing a runaway deep run
    # during A-076; deferred by John as operational documentation rather than a correctness
    # defect. No executable consumer greps for the gate by name — but round five's `D-11` was
    # FOUND with `pgrep -f scripts/test.sh` (see
    # `docs/review-2026-08-17/lens-D-evaluator-and-decoders.json`), so a reviewer reusing that
    # recorded technique would now see a quiet tree and be wrong.
    SENTINEL_GATE_SNAPSHOT="$_gate_snap" \
    SENTINEL_GATE_SOURCE="$_gate_src" \
    SENTINEL_GATE_SOURCE_SHA="$_gate_before" \
        exec bash "$_gate_snap" "$@"
fi

# ---- From here down we ARE the snapshot. This code cannot be edited by anything. ----

_gate_source_unchanged() {
    local now
    now="$(shasum -a 256 <"$SENTINEL_GATE_SOURCE" 2>/dev/null | cut -d' ' -f1 || true)"
    [ -n "$now" ] || now="ABSENT-OR-UNREADABLE"
    [ "$now" = "$SENTINEL_GATE_SOURCE_SHA" ]
}

# ONE trap covers both duties, and it fires on EVERY exit path — success, a failed stage, or
# `set -e` aborting midway. Putting the source check only beside "GATE PASSED" would let an
# edit ride along with an early exit, and putting the cleanup anywhere else would leave a
# snapshot behind on exactly the runs that go wrong.
_gate_exit() {
    local rc=$?
    if ! _gate_source_unchanged; then
        printf '\n\033[31mGATE SOURCE CHANGED DURING EXECUTION\033[0m\n' >&2
        echo "  ${SENTINEL_GATE_SOURCE} is not the file this run started from." >&2
        echo "  The run itself was NOT corrupted — it executed an immutable snapshot — but its" >&2
        echo "  result describes a script that no longer exists. DISCARD IT and re-run." >&2
        rc=4
    fi
    rm -f "$SENTINEL_GATE_SNAPSHOT"
    exit "$rc"
}
# INT and TERM as well as EXIT: a gate that is interrupted — Ctrl-C, a harness timeout, a
# `pkill` — would otherwise leave its snapshot behind, and those are precisely the runs a
# person is not watching the cleanup of. Measured: without this, an interrupted run leaked.
trap _gate_exit EXIT INT TERM
# <<< GATE BOOTSTRAP <<<
