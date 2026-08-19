#!/usr/bin/env bash
tgt="${SENTINEL_GATE_SNAPSHOT:-}"
if [ -z "$tgt" ]; then echo "  [child] no SENTINEL_GATE_SNAPSHOT in my environment"; exit 0; fi
echo "  [child] inherited SENTINEL_GATE_SNAPSHOT=$tgt"
[ -w "$tgt" ] && echo "  [child] and it is WRITABLE by me" || { echo "  [child] not writable"; exit 0; }
python3 - "$tgt" <<'PY'
import sys
p = sys.argv[1]
body = open(p).read()
with open(p, "w") as fh:                      # same inode: truncate + write
    fh.write("".join("# shifting line %d\n" % i for i in range(40)) + body)
PY
echo "  [child] rewrote the running parser's file in place (40 lines prepended)"
