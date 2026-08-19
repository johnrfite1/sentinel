#!/usr/bin/env bash
# usage: realtrial2.sh <delay> <label>   — robust snapshot selector
A=<SCRATCH>/scratchpad/adj
W=<REVIEW-ROOT>/worktrees/w3
delay="$1"; label="$2"
cd "$W"
./scripts/test.sh > "$A/real-$label.out" 2>&1 &
gpid=$!
snap=""; gp=""
for i in $(seq 1 5000); do
    # only a LIVE process whose argv is exactly `bash <path>` with an 8-char mktemp suffix
    line=$(ps -Ao pid=,args= | grep -E '^[[:space:]]*[0-9]+[[:space:]]+bash[[:space:]]+/.*sentinel-gate\.[A-Za-z0-9]{8}' | head -1)
    if [ -n "$line" ]; then
        gp=$(echo "$line" | awk '{print $1}')
        snap=$(echo "$line" | grep -oE '/[^ ]*sentinel-gate\.[A-Za-z0-9]{8}')
        break
    fi
done
if [ -z "$snap" ] || [ ! -f "$snap" ]; then echo "$label DEAD-PROBE: no live gate snapshot found"; wait $gpid; exit 9; fi
echo "$label target pid=$gp snap=$snap"
sleep "$delay"
if ! kill -0 "$gp" 2>/dev/null; then echo "$label DEAD-PROBE: gate already finished before the edit"; wait $gpid; exit 9; fi
if [ ! -f "$snap" ]; then echo "$label DEAD-PROBE: snapshot gone before the edit"; wait $gpid; exit 9; fi
ino0=$(stat -f '%i' "$snap"); sz0=$(wc -c < "$snap")
python3 - "$snap" >/dev/null <<'PY'
import sys
p=sys.argv[1]; b=open(p).read()
open(p,"w").write("".join("# shifting line %d\n"%i for i in range(40))+b)
PY
ino1=$(stat -f '%i' "$snap"); sz1=$(wc -c < "$snap")
[ "$ino0" = "$ino1" ] || { echo "$label DEAD-PROBE: inode changed, not an in-place edit"; wait $gpid; exit 9; }
[ "$sz1" -gt "$sz0" ] || { echo "$label DEAD-PROBE: file did not grow"; wait $gpid; exit 9; }
wait $gpid; rc=$?
echo "$label delay=${delay}s edit-applied inode=$ino0 ${sz0}->${sz1} | exit=$rc GATE_PASSED=$(grep -c 'GATE PASSED' "$A/real-$label.out") corruption=$(grep -ciE 'syntax error|unexpected EOF|unexpected token|command not found' "$A/real-$label.out") src_diag=$(grep -c 'GATE SOURCE CHANGED' "$A/real-$label.out")"
