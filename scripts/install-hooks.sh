#!/usr/bin/env bash
# Point git at the tracked hooks directory so the secret guard travels with the
# repository instead of living in one machine's .git (A-007).
#
# D-060(2): this configures SENTINEL ONLY. It previously ran `git config` against
# whatever repository the caller stood in, and was demonstrated writing
# core.hooksPath=.githooks into a foreign repository (Batch A1 case 12) — its
# non-zero exit came from a later chmod, not from any refusal, so the write had
# already landed. It now REFUSES BEFORE WRITING ANYTHING on a mismatch.
set -euo pipefail

# Sentinel identity, derived from THIS FILE, never the caller's directory.
_sentinel_self="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)" || _sentinel_self=""
if [ -z "$_sentinel_self" ]; then
    echo "  FAIL  cannot resolve this script's own location; refusing." >&2; exit 2
fi
SENTINEL_ROOT="$(cd -- "$_sentinel_self" 2>/dev/null && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u GIT_COMMON_DIR git rev-parse --show-toplevel 2>/dev/null)" || SENTINEL_ROOT=""
if [ -z "$SENTINEL_ROOT" ] || [ ! -e "$SENTINEL_ROOT/scripts/test.sh" ] || [ ! -e "$SENTINEL_ROOT/.githooks/pre-commit" ]; then
    echo "  FAIL  this script is not inside the Sentinel repository; refusing." >&2; exit 2
fi

# The repository the caller is standing in. Absent is fine; DIFFERENT is not.
CALLER_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || CALLER_ROOT=""
if [ -n "$CALLER_ROOT" ] && [ "$CALLER_ROOT" != "$SENTINEL_ROOT" ]; then
    echo "  FAIL  refusing to install Sentinel hooks into another repository." >&2
    echo "        invoked from : $CALLER_ROOT" >&2
    echo "        this script's: $SENTINEL_ROOT" >&2
    echo "        Nothing was written. Run it from Sentinel if that is what you meant." >&2
    exit 2
fi

cd "$SENTINEL_ROOT" || { echo "  FAIL  cannot enter the Sentinel repository root; refusing." >&2; exit 2; }
# CALLER GIT OVERRIDES ARE REMOVED ONCE, HERE, BEFORE ANY BODY-LEVEL GIT CALL (12-F2).
# Scrubbing only the identity probe left every later `git` inheriting the caller's
# environment: GIT_DIR alone made this guard report clean over a live credential, and made
# install-hooks write into a victim repository. GIT_PREFIX is included although inert on
# git 2.50.1 — an inert variable today is not a guarantee tomorrow.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX
git -C "$SENTINEL_ROOT" config core.hooksPath .githooks
chmod +x .githooks/* scripts/*.sh
echo "hooks installed: core.hooksPath=.githooks"
