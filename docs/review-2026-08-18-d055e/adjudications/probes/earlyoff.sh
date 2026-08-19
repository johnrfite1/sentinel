#!/usr/bin/env bash
A=<SCRATCH>/scratchpad/adj
W=<REVIEW-ROOT>/worktrees/w3
cd "$W"
./scripts/test.sh > "$A/earlyoff-gate.out" 2>&1 &
gpid=$!
pid=""
for i in $(seq 1 2000); do
    line=$(ps -Ao pid=,args= | grep 'sentinel-gate\.' | grep -v grep | head -1)
    [ -n "$line" ] && { pid=$(echo "$line"|awk '{print $1}'); break; }
done
echo "found gate pid=$pid after $i ps polls"
for n in $(seq 1 40); do
    o=$(lsof -p "$pid" 2>/dev/null | awk '/sentinel-gate/{print $7}')
    kill -0 "$pid" 2>/dev/null || { echo "sample $n: gone"; break; }
    echo "sample $n: offset=$o"
    [ "$o" = "73660" ] && { echo ">>> reached EOF (73660) at sample $n"; break; }
done
kill $gpid 2>/dev/null; wait $gpid 2>/dev/null; echo done
