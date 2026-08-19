#!/usr/bin/env bash
# usage: mkbody.sh <outfile> <with-bootstrap:yes|no> <bootstrap-file> <child-script>
out="$1"; withboot="$2"; boot="$3"; child="$4"
{
  echo '#!/usr/bin/env bash'
  echo 'set -euo pipefail'
  [ "$withboot" = yes ] && cat "$boot"
  echo 'echo "STAGE 1 ok"'
  echo "\"$child\""
  echo 'sleep 2'
  echo 'echo "STAGE 2 ok"'
  # 4000 padding lines (~120 KB) so the parser certainly has unread bytes left
  awk 'BEGIN{for(i=0;i<4000;i++) print ": padding line " i}'
  echo 'echo "BODY COMPLETED"'
} > "$out"
chmod +x "$out"
