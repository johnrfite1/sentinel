#!/usr/bin/env bash
# usage: realtrial.sh <delay-seconds> <label>
A=<SCRATCH>/scratchpad/adj
W=<REVIEW-ROOT>/worktrees/w3
delay="$1"; label="$2"
cd "$W"
./scripts/test.sh > "$A/real-$label.out" 2>&1 &
gpid=$!
snap=""
for i in $(seq 1 3000); do
    snap=$(ps -Ao args= | grep -o '/[^ ]*sentinel-gate\.[A-Za-z0-9]*' | head -1)
    [ -n "$snap" ] && break
done
[ -z "$snap" ] && { echo "$label PROBE-DEAD no snapshot"; wait $gpid; exit 9; }
sz0=$(wc -c < "$snap"); ino0=$(stat -f '%i' "$snap")
sleep "$delay"
if [ ! -e "$snap" ]; then echo "$label PROBE-DEAD snapshot vanished before edit"; wait $gpid; exit 9; fi
python3 - "$snap" >/dev/null <<'PY'
import sys
p=sys.argv[1]; b=open(p).read()
open(p,"w").write("".join("# shifting line %d\n"%i for i in range(40))+b)
PY
sz1=$(wc -c < "$snap" 2>/dev/null); ino1=$(stat -f '%i' "$snap" 2>/dev/null)
wait $gpid; rc=$?
pass=$(grep -c 'GATE PASSED' "$A/real-$label.out")
corr=$(grep -ciE 'syntax error|unexpected EOF|unexpected token' "$A/real-$label.out")
diag=$(grep -c 'GATE SOURCE CHANGED' "$A/real-$label.out")
echo "$label delay=${delay}s inode ${ino0}->${ino1} size ${sz0}->${sz1} | exit=$rc GATE_PASSED=$pass corruption_lines=$corr src_diag=$diag"
