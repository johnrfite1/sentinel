#!/usr/bin/env bash
A=<SCRATCH>/scratchpad/adj
W=<REVIEW-ROOT>/worktrees/w3
cd "$W"
./scripts/test.sh > "$A/offsets-gate2.out" 2>&1 &
gpid=$!
snap=""; pid=""
for i in $(seq 1 300); do
    line=$(ps -Ao pid=,args= | grep 'sentinel-gate\.' | grep -v grep | head -1)
    if [ -n "$line" ]; then pid=$(echo "$line"|awk '{print $1}'); snap=$(echo "$line"|grep -o '/[^ ]*sentinel-gate\.[A-Za-z0-9]*'); break; fi
    sleep 0.1
done
echo "gate pid=$pid snapshot=$snap size=$(wc -c < "$snap")"
for t in 1 3 6 10 15 25 40; do
    while [ $SECONDS -lt $t ]; do sleep 0.2; done
    kill -0 "$pid" 2>/dev/null || { echo "t=${t}s gate gone"; break; }
    echo "t=${t}s  $(lsof -p "$pid" 2>/dev/null | grep 'sentinel-gate' | awk '{print "fd="$4" offset="$7" name="$NF}')"
done
kill $gpid 2>/dev/null; wait $gpid 2>/dev/null; echo done
