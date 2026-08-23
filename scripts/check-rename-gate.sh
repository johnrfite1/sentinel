#!/usr/bin/env bash
# Sentinel — pre-publication rename gate (D-016).
#
# "Sentinel" is a private working codename that collides with existing projects. John ruled
# on 2026-07-28 that the collision is NOT accepted: repository visibility, public demos,
# published links, and portfolio or resume references are blocked until he approves a
# replacement name following domain and trademark/collision review.
#
# AGENTS.md requires a durable project rule to get a mechanical check rather than prose, and
# "nothing goes public" is exactly the rule that gets violated by one click months from now,
# by someone who never read the decision log. So this fails the gate if the repository has
# become public.
#
# NOT an S1 condition (D-016 is explicit). It is a publication gate, checked continuously so
# that a violation is caught the day it happens rather than at the next review.
set -uo pipefail

# --- Sentinel repository identity (D-060(2)) ---------------------------------
# This guard previously operated on whatever repository the caller stood in, so a
# run from elsewhere reported a clean result for the wrong tree. Identity is now
# derived from THIS FILE's own location, and every step is checked: `cd ""`
# returns 0 and does not abort even under `set -e`.
_sentinel_self="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)" || _sentinel_self=""
if [ -z "$_sentinel_self" ]; then
    echo "  FAIL  cannot resolve this script's own location; refusing." >&2; exit 2
fi
SENTINEL_ROOT="$(cd -- "$_sentinel_self" 2>/dev/null && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR git rev-parse --show-toplevel 2>/dev/null)" || SENTINEL_ROOT=""
if [ -z "$SENTINEL_ROOT" ] || [ ! -e "$SENTINEL_ROOT/scripts/test.sh" ] || [ ! -e "$SENTINEL_ROOT/.githooks/pre-commit" ]; then
    echo "  FAIL  this script is not inside the Sentinel repository; refusing." >&2; exit 2
fi
cd "$SENTINEL_ROOT" || { echo "  FAIL  cannot enter the Sentinel repository root; refusing." >&2; exit 2; }
# CALLER GIT OVERRIDES ARE REMOVED ONCE, HERE, BEFORE ANY BODY-LEVEL GIT CALL (12-F2).
# Scrubbing only the identity probe left every later `git` inheriting the caller's
# environment: GIT_DIR alone made this guard report clean over a live credential, and made
# install-hooks write into a victim repository. GIT_PREFIX is included although inert on
# git 2.50.1 — an inert variable today is not a guarantee tomorrow.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX

# D-071 / D-059(7). Invoked by both gate profiles (scripts/test.sh shared prefix).
# Fast: UNVERIFIED exits 0. Deep/--gate: UNVERIFIED exits 1 unless
# SENTINEL_RENAME_GATE_UNVERIFIED_OK=1. The env var name is printed ON the
# UNVERIFIED line. An acknowledged deep run states that D-016 was acknowledged,
# not verified. Coverage: origin visibility via gh when readable. Not covered:
# demos, published links, portfolio or resume references (D-016's other verbs).
PROFILE="fast"
for _arg in "$@"; do
    case "$_arg" in
        --gate) PROFILE="gate" ;;
    esac
done
ACK="${SENTINEL_RENAME_GATE_UNVERIFIED_OK:-}"

unverified() {
    local reason="$1"
    local cover="Coverage: origin visibility via gh when readable. Not covered: demos, published links, portfolio or resume references (D-016's other verbs)."
    if [ "$PROFILE" = "gate" ]; then
        if [ "$ACK" = "1" ]; then
            echo "${YEL}rename gate: UNVERIFIED${RST} (SENTINEL_RENAME_GATE_UNVERIFIED_OK=1) — ${reason}"
            echo "  This --gate run ACKNOWLEDGES D-016 was not verified; it was acknowledged, not verified private."
            echo "  D-016 still blocks publication. ${cover}"
            exit 0
        fi
        echo "${YEL}rename gate: UNVERIFIED${RST} (deep/--gate refuses unless SENTINEL_RENAME_GATE_UNVERIFIED_OK=1) — ${reason}"
        echo "  D-016 still blocks publication. Deep profile requires acknowledgement or a readable visibility check."
        echo "  ${cover}"
        exit 1
    fi
    echo "${YEL}rename gate: UNVERIFIED${RST} (SENTINEL_RENAME_GATE_UNVERIFIED_OK=1 acknowledges in --gate) — ${reason}"
    echo "  D-016 still blocks publication. Verify by hand before any public action."
    echo "  ${cover}"
    exit 0
}

RED=$'\033[31m'; YEL=$'\033[33m'; RST=$'\033[0m'
[ -t 1 ] || { RED=""; YEL=""; RST=""; }

remote_url="$(git config --get remote.origin.url 2>/dev/null || true)"
if [ -z "$remote_url" ]; then
    echo "rename gate: no remote configured — nothing can be public"
    exit 0
fi

if ! command -v gh >/dev/null 2>&1; then
    unverified "gh CLI not available, cannot check visibility."
fi

slug="$(printf '%s' "$remote_url" | sed -E 's#(git@github.com:|https://github.com/)##; s#\.git$##')"
visibility="$(gh repo view "$slug" --json visibility --jq .visibility 2>/dev/null || true)"

if [ -z "$visibility" ]; then
    unverified "could not read visibility for $slug (auth? network?)."
fi

if [ "$visibility" != "PRIVATE" ]; then
    echo "${RED}RENAME GATE VIOLATED${RST} — $slug is $visibility."
    echo "  D-016: publication is blocked until John approves a replacement name after"
    echo "  domain and trademark/collision review. Make the repository private again."
    exit 1
fi

echo "rename gate: clean ($slug is private; D-016 publication block intact)"
