#!/usr/bin/env bash
# D-071 / D-072 independent observing harness.
# Subject: the named baseline worktree's scripts/*, never HEAD's.
# Prints TSV rows: case, CONTROL|REQUIRED, PASS|FAIL|NOT_MEASURED, evidence
# Does not change production. Does not score HEAD.
set -euo pipefail

usage() {
  echo "usage: $0 --r5-subject DIR --v6-subject DIR --logdir DIR [--skip-toplevel]" >&2
  exit 3
}

R5_SUBJECT=""
V6_SUBJECT=""
LOGDIR=""
SKIP_TOPLEVEL=0
while [ $# -gt 0 ]; do
  case "$1" in
    --r5-subject) R5_SUBJECT="${2:-}"; shift 2 ;;
    --v6-subject) V6_SUBJECT="${2:-}"; shift 2 ;;
    --logdir) LOGDIR="${2:-}"; shift 2 ;;
    --skip-toplevel) SKIP_TOPLEVEL=1; shift ;;
    *) usage ;;
  esac
done
[ -n "$R5_SUBJECT" ] && [ -n "$V6_SUBJECT" ] && [ -n "$LOGDIR" ] || usage

R5_SUBJECT="$(cd "$R5_SUBJECT" && pwd -P)"
V6_SUBJECT="$(cd "$V6_SUBJECT" && pwd -P)"
mkdir -p "$LOGDIR"
LOGDIR="$(cd "$LOGDIR" && pwd -P)"

R5_SHA="$(git -C "$R5_SUBJECT" rev-parse HEAD)"
V6_SHA="$(git -C "$V6_SUBJECT" rev-parse HEAD)"
R5_BASELINE="558d001546b55bd80156bc875cf080fef0e301eb"
V6_BASELINE="1ae684cec83c7bfdb24a8c18ffdeba87c535874f"
ACK_VAR="SENTINEL_RENAME_GATE_UNVERIFIED_OK"
GH_SLUG="johnrfite1/sentinel"
GH_URL="https://github.com/${GH_SLUG}.git"

req_fail=0
ctl_fail=0
not_measured=0
invalid=0
MATRIX="$LOGDIR/matrix.tsv"
: >"$MATRIX"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/d071d072.XXXXXXXX")"
SECRET_HEX="$(openssl rand -hex 16)"
SECRET_LINE="API_KEY=${SECRET_HEX}"
# D-008(2)/(4) plant assembled at run time so committed bytes never carry live scanner literals.
_vp1='execu'
_vp2='ted dir'
_vp3='ectly'
_vn='Coin'
_vn="${_vn}base"
_alt1='faith'
_alt2='fully emu'
_alt3='lated'
VENDOR_LINE="The comparison was ${_vp1}${_vp2}${_vp3} against ${_vn}."
export SECRET_HEX
export VENDOR_LINE
export VP_LABEL="${_vp1}${_vp2}${_vp3}"
export VP_NAME="${_vn}"
export VP_LABEL_ALT="${_alt1}${_alt2}${_alt3}"

trap 'rm -rf "$WORK"' EXIT

redact() {
  python3 -c 'import os,sys
h=os.environ.get("SECRET_HEX","")
v=os.environ.get("VENDOR_LINE","")
lab=os.environ.get("VP_LABEL","")
name=os.environ.get("VP_NAME","")
alt=os.environ.get("VP_LABEL_ALT","")
t=sys.stdin.read()
if h:
    t=t.replace("API_KEY="+h,"API_KEY=<redacted>")
    t=t.replace(h,"<redacted-hex>")
if v:
    t=t.replace(v,"<vendor-plant>")
if lab:
    t=t.replace(lab,"<D-008-2-label>")
if name:
    t=t.replace(name,"<vendor-name>")
if alt:
    t=t.replace(alt,"<D-008-2-label-alt>")
sys.stdout.write(t)'
}

row() {
  local id="$1" kind="$2" status="$3" evidence="$4"
  printf '%s\t%s\t%s\t%s\n' "$id" "$kind" "$status" "$evidence" | tee -a "$MATRIX"
  printf '  %-28s %-8s %-12s %s\n' "$id" "$kind" "$status" "$evidence" >&2
  case "$status" in
    FAIL)
      if [ "$kind" = "REQUIRED" ]; then req_fail=$((req_fail + 1))
      else ctl_fail=$((ctl_fail + 1)); fi ;;
    NOT_MEASURED) not_measured=$((not_measured + 1)) ;;
  esac
}

mark_invalid_if_baseline_pass() {
  local id="$1" subject_sha="$2" baseline_sha="$3"
  if [ "$subject_sha" = "$baseline_sha" ]; then
    invalid=1
    echo "INVALID: $id PASSED at baseline $baseline_sha; the contract required FAIL." >&2
  fi
}

clone_of() {
  local src="$1" dest="$2"
  rm -rf "$dest"
  git clone --quiet --local --no-hardlinks "$src" "$dest"
  git -C "$dest" config user.email "d071-d072-card@invalid"
  git -C "$dest" config user.name "D071-D072 card"
  git -C "$dest" config commit.gpgsign false
}

sandbox_home() {
  export HOME="$1"
  mkdir -p "$HOME"
  unset GIT_CONFIG_COUNT GIT_CONFIG_KEY_0 GIT_CONFIG_VALUE_0
  unset GIT_CONFIG_GLOBAL GIT_CONFIG_SYSTEM GIT_CONFIG_NOSYSTEM
  unset XDG_CONFIG_HOME
}

clear_cfg() {
  unset GIT_CONFIG_COUNT GIT_CONFIG_KEY_0 GIT_CONFIG_VALUE_0
  unset GIT_CONFIG_GLOBAL GIT_CONFIG_SYSTEM GIT_CONFIG_NOSYSTEM
}

unpinned_ls() {
  local dir="$1"
  (cd "$dir" && git ls-files --others --exclude-standard)
}

plant_listed() {
  local dir="$1" plant="$2"
  unpinned_ls "$dir" 2>/dev/null | /usr/bin/grep -F -x -- "$plant" >/dev/null
}

capture_cmd() {
  local out="$1"
  shift
  set +e
  "$@" >"$out" 2>&1
  echo $? >"${out}.rc"
  set -e
  redact <"$out" >"${out%.raw.log}.log"
}

run_secrets() { capture_cmd "$2" bash -c 'cd "$1" && ./scripts/check-secrets.sh' _ "$1"; }
run_vendor()  { capture_cmd "$2" bash -c 'cd "$1" && ./scripts/check-vendor-honesty.sh' _ "$1"; }

run_rename() {
  local dir="$1" out="$2"
  shift 2
  set +e
  (
    cd "$dir" || exit 90
    unset "$ACK_VAR" || true
    ./scripts/check-rename-gate.sh "$@"
  ) >"$out" 2>&1
  echo $? >"${out}.rc"
  set -e
  redact <"$out" >"${out%.raw.log}.log"
}

rc_of() { cat "$1.rc"; }

secrets_blocked() {
  local out="$1" plant="$2"
  /usr/bin/grep -E -q 'BLOCKED|secret guard: .*finding' "$out" \
    && /usr/bin/grep -F -q -- "$plant" "$out"
}

vendor_blocked() {
  local out="$1" plant="$2"
  /usr/bin/grep -E -q 'FAIL' "$out" \
    && /usr/bin/grep -F -q -- "$plant" "$out"
}

echo "R5 subject $R5_SHA ($R5_SUBJECT)" >&2
echo "V6 subject $V6_SHA ($V6_SUBJECT)" >&2
echo "git $(git --version)" >&2

# ===================================================================== R5
echo >&2
echo "== R5 UNVERIFIED clone ==" >&2
R5U="$WORK/r5-unverified"
clone_of "$R5_SUBJECT" "$R5U"
ORIGIN_U="$(git -C "$R5U" remote get-url origin)"
{
  echo "origin=$ORIGIN_U"
  echo "head=$(git -C "$R5U" rev-parse HEAD)"
} >"$LOGDIR/r5-unverified-clone.meta"
case "$ORIGIN_U" in
  *github.com*)
    row "R5-C-unverified-origin" CONTROL FAIL "origin is a GitHub URL: $ORIGIN_U"
    ;;
  /*|*/*)
    row "R5-C-unverified-origin" CONTROL PASS "origin is local path: $ORIGIN_U"
    ;;
  *)
    row "R5-C-unverified-origin" CONTROL FAIL "origin not a local path: $ORIGIN_U"
    ;;
esac

echo >&2
echo "== R5-1 fast UNVERIFIED no-ack ==" >&2
run_rename "$R5U" "$LOGDIR/r5-1-fast.raw.log"
RC1="$(rc_of "$LOGDIR/r5-1-fast.raw.log")"
if /usr/bin/grep -q 'UNVERIFIED' "$LOGDIR/r5-1-fast.log" \
   && ! /usr/bin/grep -qi 'no remote' "$LOGDIR/r5-1-fast.log"; then
  row "R5-C-unverified-output" CONTROL PASS "fast output contains UNVERIFIED (rc=$RC1)"
else
  row "R5-C-unverified-output" CONTROL FAIL "fast output did not establish UNVERIFIED (rc=$RC1)"
fi
if /usr/bin/grep -E 'UNVERIFIED' "$LOGDIR/r5-1-fast.log" | /usr/bin/grep -F -q "$ACK_VAR"; then
  row "R5-1-fast-varname" REQUIRED PASS "UNVERIFIED line names $ACK_VAR (rc=$RC1)"
  mark_invalid_if_baseline_pass "R5-1-fast-varname" "$R5_SHA" "$R5_BASELINE"
else
  row "R5-1-fast-varname" REQUIRED FAIL "UNVERIFIED line does not name $ACK_VAR (rc=$RC1)"
fi

echo >&2
echo "== R5-2 deep UNVERIFIED no-ack ==" >&2
run_rename "$R5U" "$LOGDIR/r5-2-deep.raw.log" --gate
RC2="$(rc_of "$LOGDIR/r5-2-deep.raw.log")"
if [ "$RC2" != "0" ]; then
  row "R5-2-deep-refuse" REQUIRED PASS "deep UNVERIFIED no-ack rc=$RC2"
  mark_invalid_if_baseline_pass "R5-2-deep-refuse" "$R5_SHA" "$R5_BASELINE"
else
  row "R5-2-deep-refuse" REQUIRED FAIL "deep UNVERIFIED no-ack rc=0"
fi

echo >&2
echo "== R5-3 deep UNVERIFIED with ack ==" >&2
set +e
(
  cd "$R5U" || exit 90
  export "${ACK_VAR}=1"
  ./scripts/check-rename-gate.sh --gate
) >"$LOGDIR/r5-3-ack.raw.log" 2>&1
RC3=$?
set -e
echo "$RC3" >"$LOGDIR/r5-3-ack.raw.log.rc"
redact <"$LOGDIR/r5-3-ack.raw.log" >"$LOGDIR/r5-3-ack.log"
DISCLOSE=0
if /usr/bin/grep -Ei 'acknowledged, not verified|ACKNOWLEDGES D-016|acknowledged, not verified private' "$LOGDIR/r5-3-ack.log" >/dev/null; then
  DISCLOSE=1
fi
if [ "$RC3" = "0" ] && [ "$DISCLOSE" -eq 1 ]; then
  row "R5-3-deep-ack-disclose" REQUIRED PASS "ack deep rc=0 and disclosure present"
  mark_invalid_if_baseline_pass "R5-3-deep-ack-disclose" "$R5_SHA" "$R5_BASELINE"
else
  row "R5-3-deep-ack-disclose" REQUIRED FAIL "ack deep rc=$RC3 disclose=$DISCLOSE (need both)"
fi

echo >&2
echo "== R5-4 readable PRIVATE ==" >&2
R5P="$WORK/r5-private-origin"
clone_of "$R5_SUBJECT" "$R5P"
git -C "$R5P" remote set-url origin "$GH_URL"
set +e
GH_VIS="$(gh repo view "$GH_SLUG" --json visibility --jq .visibility 2>"$LOGDIR/r5-4-gh.err")"
GH_RC=$?
set -e
printf '%s\n' "$GH_VIS" >"$LOGDIR/r5-4-gh.out"
if [ "$GH_RC" -eq 0 ] && [ "$GH_VIS" = "PRIVATE" ]; then
  row "R5-C-gh-private" CONTROL PASS "gh repo view $GH_SLUG visibility=PRIVATE"
  run_rename "$R5P" "$LOGDIR/r5-4-fast.raw.log"
  RC4="$(rc_of "$LOGDIR/r5-4-fast.raw.log")"
  run_rename "$R5P" "$LOGDIR/r5-4-deep.raw.log" --gate
  RC4D="$(rc_of "$LOGDIR/r5-4-deep.raw.log")"
  if [ "$RC4" = "0" ] && [ "$RC4D" = "0" ] \
     && /usr/bin/grep -q 'rename gate: clean' "$LOGDIR/r5-4-fast.log" \
     && /usr/bin/grep -q 'rename gate: clean' "$LOGDIR/r5-4-deep.log"; then
    row "R5-4-readable-clean" REQUIRED PASS "fast rc=$RC4 deep rc=$RC4D clean line present"
  else
    row "R5-4-readable-clean" REQUIRED FAIL "fast rc=$RC4 deep rc=$RC4D; missing clean line or non-zero"
  fi
else
  row "R5-C-gh-private" CONTROL NOT_MEASURED "gh visibility not PRIVATE (rc=$GH_RC vis=${GH_VIS:-empty})"
  row "R5-4-readable-clean" REQUIRED NOT_MEASURED "readable PRIVATE control did not fire"
fi

# ===================================================================== V6
v6_observe() {
  local vec="$1" consumer="$2" clone="$3" plant="$4" raw="$5"
  if [ "$consumer" = "secrets" ]; then
    run_secrets "$clone" "$raw"
    if secrets_blocked "$raw" "$plant"; then
      row "V6-${vec}-${consumer}" REQUIRED PASS "consumer blocked $plant (rc=$(rc_of "$raw"))"
      mark_invalid_if_baseline_pass "V6-${vec}-${consumer}" "$V6_SHA" "$V6_BASELINE"
    else
      row "V6-${vec}-${consumer}" REQUIRED FAIL "consumer missed $plant (rc=$(rc_of "$raw"))"
    fi
  else
    run_vendor "$clone" "$raw"
    if vendor_blocked "$raw" "$plant"; then
      row "V6-${vec}-${consumer}" REQUIRED PASS "consumer blocked $plant (rc=$(rc_of "$raw"))"
      mark_invalid_if_baseline_pass "V6-${vec}-${consumer}" "$V6_SHA" "$V6_BASELINE"
    else
      row "V6-${vec}-${consumer}" REQUIRED FAIL "consumer missed $plant (rc=$(rc_of "$raw"))"
    fi
  fi
}

run_v6_vector() {
  local vec="$1" consumer="$2" plant="$3" payload="$4"
  local clone="$WORK/v6-${vec}-${consumer}"
  local ignore="$WORK/ignore-${vec}-${consumer}"
  local cfg="$WORK/cfg-${vec}-${consumer}"
  local sand="$WORK/home-${vec}-${consumer}"
  local xdg="$WORK/xdg-${vec}-${consumer}"
  local raw="$LOGDIR/v6-${vec}-${consumer}.raw.log"

  clone_of "$V6_SUBJECT" "$clone"
  mkdir -p "$sand" "$xdg/git"
  sandbox_home "$sand"
  printf '%s\n' "$payload" >"$clone/$plant"
  printf '%s\n' "$plant" >"$ignore"
  printf '[core]\n\texcludesFile = %s\n' "$ignore" >"$cfg"

  clear_cfg
  unset XDG_CONFIG_HOME
  unpinned_ls "$clone" >"$LOGDIR/v6-${vec}-${consumer}.ls-before.txt" 2>&1 || true
  if ! plant_listed "$clone" "$plant"; then
    row "V6-${vec}-${consumer}-C-potency-ls" CONTROL FAIL "unpinned ls-files did not list $plant before injection"
    row "V6-${vec}-${consumer}" REQUIRED NOT_MEASURED "potency listing control did not fire"
    return 0
  fi
  row "V6-${vec}-${consumer}-C-potency-ls" CONTROL PASS "unpinned ls-files listed $plant before injection"

  local pot="$LOGDIR/v6-${vec}-${consumer}.potency.raw.log"
  if [ "$consumer" = "secrets" ]; then
    run_secrets "$clone" "$pot"
    if ! secrets_blocked "$pot" "$plant"; then
      row "V6-${vec}-${consumer}-C-potency-scan" CONTROL FAIL "consumer did not block visible $plant"
      row "V6-${vec}-${consumer}" REQUIRED NOT_MEASURED "payload potency control did not fire"
      return 0
    fi
  else
    run_vendor "$clone" "$pot"
    if ! vendor_blocked "$pot" "$plant"; then
      row "V6-${vec}-${consumer}-C-potency-scan" CONTROL FAIL "consumer did not block visible $plant"
      row "V6-${vec}-${consumer}" REQUIRED NOT_MEASURED "payload potency control did not fire"
      return 0
    fi
  fi
  row "V6-${vec}-${consumer}-C-potency-scan" CONTROL PASS "consumer blocked visible $plant"

  sandbox_home "$sand"
  case "$vec" in
    COUNT)
      export GIT_CONFIG_COUNT=1
      export GIT_CONFIG_KEY_0=core.excludesFile
      export GIT_CONFIG_VALUE_0="$ignore"
      unset GIT_CONFIG_GLOBAL GIT_CONFIG_SYSTEM GIT_CONFIG_NOSYSTEM
      ;;
    GLOBAL)
      clear_cfg
      export GIT_CONFIG_GLOBAL="$cfg"
      ;;
    SYSTEM)
      clear_cfg
      export GIT_CONFIG_SYSTEM="$cfg"
      ;;
    NOSYSTEM)
      clear_cfg
      export GIT_CONFIG_NOSYSTEM=1
      ;;
    HOME)
      clear_cfg
      unset XDG_CONFIG_HOME
      mkdir -p "$sand/.config/git"
      cp "$ignore" "$sand/.config/git/ignore"
      export HOME="$sand"
      ;;
    XDG)
      clear_cfg
      mkdir -p "$xdg/git"
      cp "$ignore" "$xdg/git/ignore"
      export XDG_CONFIG_HOME="$xdg"
      export HOME="$sand"
      ;;
    *) echo "unknown vector $vec" >&2; exit 3 ;;
  esac

  unpinned_ls "$clone" >"$LOGDIR/v6-${vec}-${consumer}.ls-after.txt" 2>&1 || true
  if plant_listed "$clone" "$plant"; then
    if [ "$vec" = "NOSYSTEM" ]; then
      row "V6-${vec}-${consumer}-C-exploit" CONTROL NOT_MEASURED "GIT_CONFIG_NOSYSTEM did not hide $plant on this machine"
      row "V6-${vec}-${consumer}" REQUIRED NOT_MEASURED "NOSYSTEM exploit control did not hide the plant"
      clear_cfg
      unset GIT_CONFIG_NOSYSTEM XDG_CONFIG_HOME
      return 0
    fi
    row "V6-${vec}-${consumer}-C-exploit" CONTROL FAIL "unpinned ls-files still listed $plant after $vec"
    row "V6-${vec}-${consumer}" REQUIRED NOT_MEASURED "exploit control did not hide the plant"
    clear_cfg
    unset GIT_CONFIG_NOSYSTEM XDG_CONFIG_HOME
    return 0
  fi
  row "V6-${vec}-${consumer}-C-exploit" CONTROL PASS "unpinned ls-files omitted $plant after $vec"

  v6_observe "$vec" "$consumer" "$clone" "$plant" "$raw"
  clear_cfg
  unset GIT_CONFIG_NOSYSTEM XDG_CONFIG_HOME
}

echo >&2
echo "== V6 hide-untracked vectors ==" >&2
for vec in COUNT GLOBAL SYSTEM NOSYSTEM HOME XDG; do
  run_v6_vector "$vec" secrets "scratch-d072-secret.env" "$SECRET_LINE"
  run_v6_vector "$vec" vendor "scratch-d072-vendor.md" "$VENDOR_LINE"
done

# ===================================================================== R2
echo >&2
echo "== R2 non-ASCII filename ==" >&2
R2="$WORK/r2"
clone_of "$V6_SUBJECT" "$R2"
sandbox_home "$WORK/r2-home"
CAFE_NAME="$(python3 -c 'print("caf\u00e9-d072.md")')"
ASCII_NAME="cafe-d072.md"
printf '%s\n' "$VENDOR_LINE" >"$R2/$ASCII_NAME"
python3 -c 'import os,sys
open(os.path.join(sys.argv[1], sys.argv[2]), "w", encoding="utf-8").write(sys.argv[3]+"\n")
' "$R2" "$CAFE_NAME" "$VENDOR_LINE"

unpinned_ls "$R2" >"$LOGDIR/r2-unquoted.ls.txt" 2>&1 || true
USABLE_CAFE=0
USABLE_ASCII=0
ESCAPED_CAFE=0
while IFS= read -r line || [ -n "$line" ]; do
  [ -z "$line" ] && continue
  if [ -f "$R2/$line" ]; then
    [ "$line" = "$ASCII_NAME" ] && USABLE_ASCII=1
    [ "$line" = "$CAFE_NAME" ] && USABLE_CAFE=1
  else
    case "$line" in
      *\\3*|*caf\\*) ESCAPED_CAFE=1 ;;
    esac
  fi
done <"$LOGDIR/r2-unquoted.ls.txt"

R2_DROP_OK=0
if [ "$USABLE_ASCII" -eq 1 ] && [ "$USABLE_CAFE" -eq 0 ]; then
  row "R2-C-unquoted" CONTROL PASS "ASCII sibling usable; café path not a usable [ -f ] token (escaped=$ESCAPED_CAFE)"
  R2_DROP_OK=1
else
  row "R2-C-unquoted" CONTROL FAIL "ASCII usable=$USABLE_ASCII café usable=$USABLE_CAFE escaped=$ESCAPED_CAFE"
  row "R2-vendor" REQUIRED NOT_MEASURED "unquoted drop control did not fire"
  row "R2-secrets" REQUIRED NOT_MEASURED "unquoted drop control did not fire"
fi

R2_PAYLOAD_OK=0
if [ "$USABLE_ASCII" -eq 1 ]; then
  R2A="$WORK/r2-ascii-only"
  clone_of "$V6_SUBJECT" "$R2A"
  sandbox_home "$WORK/r2-ascii-home"
  printf '%s\n' "$VENDOR_LINE" >"$R2A/$ASCII_NAME"
  run_vendor "$R2A" "$LOGDIR/r2-ascii-potency.raw.log"
  if vendor_blocked "$LOGDIR/r2-ascii-potency.raw.log" "$ASCII_NAME"; then
    row "R2-C-payload" CONTROL PASS "vendor-honesty blocked ASCII sibling $ASCII_NAME"
    R2_PAYLOAD_OK=1
  else
    row "R2-C-payload" CONTROL FAIL "vendor-honesty did not block ASCII sibling"
    row "R2-vendor" REQUIRED NOT_MEASURED "payload potency control did not fire"
  fi
fi

if [ "$R2_DROP_OK" -eq 1 ] && [ "$R2_PAYLOAD_OK" -eq 1 ]; then
  R2C="$WORK/r2-cafe-only"
  clone_of "$V6_SUBJECT" "$R2C"
  sandbox_home "$WORK/r2-cafe-home"
  python3 -c 'import os,sys
open(os.path.join(sys.argv[1], sys.argv[2]), "w", encoding="utf-8").write(sys.argv[3]+"\n")
' "$R2C" "$CAFE_NAME" "$VENDOR_LINE"
  run_vendor "$R2C" "$LOGDIR/r2-vendor.raw.log"
  if vendor_blocked "$LOGDIR/r2-vendor.raw.log" "$CAFE_NAME"; then
    row "R2-vendor" REQUIRED PASS "vendor-honesty blocked café plant"
    mark_invalid_if_baseline_pass "R2-vendor" "$V6_SHA" "$V6_BASELINE"
  else
    row "R2-vendor" REQUIRED FAIL "vendor-honesty missed café plant"
  fi
fi

(cd "$R2" && git ls-files --others --exclude-standard -z) >"$LOGDIR/r2-z.ls.bin" 2>/dev/null || true
Z_HAS_CAFE="$(python3 -c 'import sys
name=sys.argv[1].encode("utf-8")
data=open(sys.argv[2],"rb").read().split(b"\0")
print("1" if name in data else "0")
' "$CAFE_NAME" "$LOGDIR/r2-z.ls.bin")"
if [ "$Z_HAS_CAFE" = "1" ]; then
  row "R2-C-z" CONTROL PASS "-z listing still contains raw café path; R2 is not a secrets hole here"
  row "R2-secrets" REQUIRED NOT_MEASURED "-z did not drop the café path; R2 not claimed against secrets"
else
  row "R2-C-z" CONTROL PASS "-z listing omitted raw café path"
  R2S="$WORK/r2-secrets-cafe"
  clone_of "$V6_SUBJECT" "$R2S"
  sandbox_home "$WORK/r2-sec-home"
  python3 -c 'import os,sys
open(os.path.join(sys.argv[1], sys.argv[2]), "w", encoding="utf-8").write(sys.argv[3]+"\n")
' "$R2S" "$CAFE_NAME" "$SECRET_LINE"
  run_secrets "$R2S" "$LOGDIR/r2-secrets.raw.log"
  if secrets_blocked "$LOGDIR/r2-secrets.raw.log" "$CAFE_NAME"; then
    row "R2-secrets" REQUIRED PASS "secrets blocked café plant"
  else
    row "R2-secrets" REQUIRED FAIL "secrets missed café plant"
  fi
fi

# ===================================================================== R5-5
echo >&2
echo "== R5-5 top-level test.sh --gate ==" >&2
if [ "$SKIP_TOPLEVEL" -eq 1 ]; then
  row "R5-5-toplevel-gate" REQUIRED NOT_MEASURED "skipped by --skip-toplevel"
else
  run_rename "$R5U" "$LOGDIR/r5-5-precheck.raw.log" --gate
  if ! /usr/bin/grep -q 'UNVERIFIED' "$LOGDIR/r5-5-precheck.log"; then
    row "R5-C-clone-still-unverified" CONTROL FAIL "clone was not UNVERIFIED immediately before test.sh --gate"
    row "R5-5-toplevel-gate" REQUIRED NOT_MEASURED "pre-gate UNVERIFIED control did not fire"
  else
    row "R5-C-clone-still-unverified" CONTROL PASS "clone still UNVERIFIED before test.sh --gate"
    echo "starting ./scripts/test.sh --gate in $R5U (long)" >&2
    set +e
    (
      cd "$R5U" || exit 90
      unset "$ACK_VAR" || true
      ./scripts/test.sh --gate
    ) >"$LOGDIR/r5-5-gate.raw.log" 2>&1
    RC5=$?
    set -e
    echo "$RC5" >"$LOGDIR/r5-5-gate.raw.log.rc"
    redact <"$LOGDIR/r5-5-gate.raw.log" >"$LOGDIR/r5-5-gate.log"
    if /usr/bin/grep -q 'GATE PASSED' "$LOGDIR/r5-5-gate.log"; then
      row "R5-5-toplevel-gate" REQUIRED FAIL "test.sh --gate printed GATE PASSED (rc=$RC5)"
    elif /usr/bin/grep -q 'GATE DID NOT REACH COMPLETION' "$LOGDIR/r5-5-gate.log"; then
      row "R5-5-toplevel-gate" REQUIRED NOT_MEASURED "gate did not reach completion token (rc=$RC5)"
    elif [ "$RC5" != "0" ]; then
      row "R5-5-toplevel-gate" REQUIRED PASS "no GATE PASSED, rc=$RC5"
      mark_invalid_if_baseline_pass "R5-5-toplevel-gate" "$R5_SHA" "$R5_BASELINE"
    else
      row "R5-5-toplevel-gate" REQUIRED NOT_MEASURED "rc=0 without GATE PASSED; not counted as the top-level row"
    fi
  fi
fi

{
  echo "r5_sha=$R5_SHA"
  echo "v6_sha=$V6_SHA"
  echo "req_fail=$req_fail"
  echo "ctl_fail=$ctl_fail"
  echo "not_measured=$not_measured"
  echo "invalid=$invalid"
  echo "git=$(git --version)"
} >"$LOGDIR/summary.txt"

echo >&2
echo "== summary req_fail=$req_fail ctl_fail=$ctl_fail not_measured=$not_measured invalid=$invalid ==" >&2
if [ "$invalid" -ne 0 ] || [ "$ctl_fail" -ne 0 ]; then
  exit 2
fi
if [ "$req_fail" -ne 0 ]; then
  exit 1
fi
exit 0
