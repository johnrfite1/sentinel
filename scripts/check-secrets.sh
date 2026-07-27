#!/usr/bin/env bash
# Sentinel — mechanical secret guard (A-007).
#
# AGENTS.md: a durable project rule gets a mechanical guard, not prose. The
# durable rule here is house rule 6 — no secrets, credentials, or
# machine-specific absolute paths in repository files.
#
# Modes:
#   ./scripts/check-secrets.sh          scan tracked files (suite / CI)
#   ./scripts/check-secrets.sh --staged scan staged content (pre-commit hook)
#
# DESIGN NOTE — why this does not grep for bare 64-hex strings.
# A private key and a keccak256 hash are the same shape. This repository is full
# of legitimate bytes32 literals: type hashes, domain separators, mandate and
# policy hashes, fixture digests. A guard that flags `0x` + 64 hex would fire on
# nearly every Solidity and fixture file, and a guard that cries wolf gets
# reverted rather than obeyed. So this scans for secret-shaped *assignments*,
# known credential prefixes, and secret-bearing *files* — all three of which are
# unambiguous — and deliberately accepts that a private key pasted as a bare
# literal with no assignment context would pass. That residual gap is covered by
# the .env discipline and by review, not by this script. Stated here rather than
# left for someone to discover.

set -euo pipefail

STAGED=0
[ "${1:-}" = "--staged" ] && STAGED=1

RED=$'\033[31m'; YEL=$'\033[33m'; RST=$'\033[0m'
[ -t 1 ] || { RED=""; YEL=""; RST=""; }

failures=0

if [ "$STAGED" -eq 1 ]; then
  files=$(git diff --cached --name-only --diff-filter=ACM)
else
  files=$(git ls-files)
fi

# --- 1. Secret-bearing files must never be tracked -------------------------
while IFS= read -r f; do
  [ -z "$f" ] && continue
  case "$(basename "$f")" in
    .env|.env.*)
      if [ "$(basename "$f")" != ".env.example" ]; then
        echo "${RED}BLOCKED${RST} $f — env files are never committed (A-007)."
        failures=$((failures + 1))
      fi
      ;;
    *.pem|*.p12|*.keystore|id_rsa|id_ed25519)
      echo "${RED}BLOCKED${RST} $f — key material is never committed."
      failures=$((failures + 1))
      ;;
  esac
done <<< "$files"

# --- 2. Known credential prefixes ------------------------------------------
# Anthropic, OpenAI, AWS, GitHub, Slack. Unambiguous — these shapes are not
# produced by anything legitimate in this repository.
CRED_RE='(sk-ant-[A-Za-z0-9_-]{16,}|sk-[A-Za-z0-9]{32,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,})'

# --- 3. Secret-shaped assignments with a real value -------------------------
# Matches KEY=value / "key": "value" where the name looks like a credential and
# the value is neither empty nor an obvious placeholder.
ASSIGN_RE='(PRIVATE_KEY|PRIVKEY|SECRET_KEY|API_KEY|DEPLOYER_KEY|MNEMONIC|SEED_PHRASE|PASSWORD|ACCESS_TOKEN)["'"'"']?[[:space:]]*[:=][[:space:]]*["'"'"']?[A-Za-z0-9+/_.-]{12,}'

# Publicly documented Anvil dev keys — deliberately allowed (see .env.example).
ANVIL_ALLOW='ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80|59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d|test test test test test test test test test test test junk'

scan_content() {
  local label="$1" content="$2"
  local hits
  hits=$(printf '%s' "$content" \
    | grep -nE "$CRED_RE|$ASSIGN_RE" 2>/dev/null \
    | grep -vE "$ANVIL_ALLOW" \
    | grep -vE '=[[:space:]]*$|=[[:space:]]*["'"'"']{2}|(YOUR_|REPLACE_|EXAMPLE|PLACEHOLDER|xxx|\.\.\.)' \
    || true)
  if [ -n "$hits" ]; then
    echo "${RED}BLOCKED${RST} $label — credential-shaped content:"
    printf '%s\n' "$hits" | sed 's/^/    /'
    failures=$((failures + 1))
  fi
}

while IFS= read -r f; do
  [ -z "$f" ] && continue
  [ "$(basename "$f")" = "check-secrets.sh" ] && continue   # this file defines the patterns
  if [ "$STAGED" -eq 1 ]; then
    git show ":$f" >/dev/null 2>&1 || continue
    scan_content "$f" "$(git show ":$f" 2>/dev/null || true)"
  else
    [ -f "$f" ] || continue
    scan_content "$f" "$(cat "$f")"
  fi
done <<< "$files"

# --- 4. Machine-specific absolute paths ------------------------------------
# House rule 6 / A-008: scripts resolve $HOME, they do not hardcode /Users/<name>.
while IFS= read -r f; do
  [ -z "$f" ] && continue
  [ "$(basename "$f")" = "check-secrets.sh" ] && continue
  if [ "$STAGED" -eq 1 ]; then
    body=$(git show ":$f" 2>/dev/null || true)
  else
    [ -f "$f" ] || continue
    body=$(cat "$f")
  fi
  hits=$(printf '%s' "$body" | grep -nE '(/Users/[a-z]|/home/[a-z])' 2>/dev/null || true)
  if [ -n "$hits" ]; then
    echo "${YEL}BLOCKED${RST} $f — machine-specific absolute path (use \$HOME):"
    printf '%s\n' "$hits" | sed 's/^/    /'
    failures=$((failures + 1))
  fi
done <<< "$files"

if [ "$failures" -gt 0 ]; then
  echo
  echo "${RED}secret guard: $failures finding(s).${RST} Do not weaken this guard to make a commit pass (AGENTS.md)."
  echo "If this is a false positive, fix or refine the guard and document why."
  exit 1
fi

echo "secret guard: clean"
