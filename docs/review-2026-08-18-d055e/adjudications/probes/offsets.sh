#!/usr/bin/env bash
A=<SCRATCH>/scratchpad/adj
W=<REVIEW-ROOT>/worktrees/w3
cd "$W"
./scripts/test.sh > "$A/offsets-gate.out" 2>&1 &
gpid=$!
snap=""; pid=""
for i in $(seq 1 300); do
    line=$(ps -Ao pid=,args= | grep 'sentinel-gate\.' | grep -v grep | head -1)
    if [ -n "$line" ]; then
        pid=$(echo "$line" | awk '{print $1}')
        snap=$(echo "$line" | grep -o '/[^ ]*sentinel-gate\.[A-Za-z0-9]*')
        break
    fi
    sleep 0.1
done
echo "gate bash pid=$pid  snapshot=$snap  size=$(wc -c < "$snap" 2>/dev/null)"
for t in 0 1 2 4 8 12 20 30 45 60; do
    sleep_to=$t
    now=$SECONDS
    while [ $SECONDS -lt $sleep_to ]; do sleep 0.2; done
    off=$(lsof -p "$pid" -a -d 255 -Fo 2>/dev/null | grep '^o' | head -1)
    alive=$(kill -0 "$pid" 2>/dev/null && echo yes || echo no)
    echo "t=${t}s alive=$alive fd255_offset=$off"
    [ "$alive" = no ] && break
done
kill $gpid 2>/dev/null; wait $gpid 2>/dev/null
echo done
