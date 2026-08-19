#!/usr/bin/env bash
# Adjudication probe: the REAL gate, corrupted through its own snapshot by a SIBLING that
# knows nothing but what `ps` shows. Nothing in the repository is written by this probe.
A=<SCRATCH>/scratchpad/adj
W=<REVIEW-ROOT>/worktrees/w3
cd "$W"
: > "$A/realgate.out"
./scripts/test.sh > "$A/realgate.out" 2>&1 &
gpid=$!
snap=""
for i in $(seq 1 300); do
    snap=$(ps -Ao args= | grep -o '/[^ ]*sentinel-gate\.[A-Za-z0-9]*' | head -1)
    [ -n "$snap" ] && break
    sleep 0.2
done
if [ -z "$snap" ]; then echo "PROBE-DEAD: ps never revealed a snapshot path"; wait $gpid; exit 9; fi
echo "SIBLING: ps shows the running parser is reading: $snap"
[ -w "$snap" ] && echo "SIBLING: it is writable by me (uid $(id -u))" || echo "SIBLING: NOT writable"
# let the gate get several stages in, so the parser has plenty left to read
sleep 12
python3 - "$snap" <<'PY'
import sys
p = sys.argv[1]
body = open(p).read()
with open(p, "w") as fh:
    fh.write("".join("# shifting line %d\n" % i for i in range(40)) + body)
print("SIBLING: rewrote the running gate's snapshot in place, same inode, +40 lines")
PY
wait $gpid; rc=$?
echo "REAL GATE EXIT CODE: $rc"
