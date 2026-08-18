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
# THE PLACEHOLDER SUPPRESSOR WAS AN EVASION PATH UNTIL 2026-08-17 (A-052), AND THE FIX IS THE
# LINE BELOW BEGINNING `| grep -vE`. It suppressed any line matching
# `(YOUR_|REPLACE_|EXAMPLE|PLACEHOLDER|xxx|\.\.\.)` ANYWHERE ON THE LINE. Two of those are
# catastrophic in this repository: `\.\.\.` matches `...`, the TypeScript spread operator, in a
# codebase written in TypeScript; and `EXAMPLE` matches a trailing comment. So a REAL 64-hex
# private key bound to `privateKey:` passed the guard — and the pre-commit hook with it — if the
# line happened to contain a spread or the word EXAMPLE. Reproduced with a control: the identical
# key without the spread is BLOCKED.
#
# The markers are now anchored to the VALUE (`[:=][[:space:]]*["']?(0x)?MARKER`) rather than
# matched anywhere on the line, and `\.\.\.` is gone entirely — spread is syntax, never a
# placeholder. Verified both ways: four real-key spellings blocked, four genuine placeholders
# (`YOUR_…`, `PLACEHOLDER`, `xxx`, empty) still suppressed, clean tree still green.
#
# THAT FIX WAS INCOMPLETE AND THE GUARD WAS HOLED A THIRD TIME (A-058, round five, found by two
# independent reviewers and reproduced with a control). A-052 anchored the MARKER to an
# assignment operator, which is necessary and not sufficient: the suppressor still ran with
# `grep -v` against the WHOLE LINE, and a line can hold more than one assignment. So a real
# 64-hex key passed clean whenever ORDINARY sibling syntax appeared beside it —
# `{ deployKey: "0x…", API_KEY: "YOUR_API_KEY" }`, or a trailing `// see: EXAMPLE bundle`.
# A-052 had generalised its DEMONSTRATION (marker adjacent to the operator) and not its
# ARGUMENT (a suppressor must discard an OCCURRENCE, never a line). It is now `grep -o`: every
# suppressor sees one match at a time and cannot reach past it. **This also closes the
# line-wise `ANVIL_ALLOW` hole recorded separately in register §8.2 — one real key beside one
# allowlisted Anvil key was the same defect wearing a different filter, and fixing the argument
# rather than the demonstration necessarily takes both.**
#
# The report now names the MATCH rather than the whole line. That is deliberate: it is the
# thing being judged, and printing less surrounding context around a live credential is not a
# loss.
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

# --- 3b. Key-shaped literals bound to a key-shaped NAME ---------------------
# Added when the signer suite introduced `export const OWNER_KEY: Hex = "0x…"` — a real
# private key in exactly that form would have passed every rule above. The design note
# explains why bare 64-hex is not scanned; that reasoning does not extend to 64-hex
# assigned to an identifier containing KEY, SECRET, or MNEMONIC, which no legitimate
# bytes32 constant in this repository is. Typehashes, domain separators, and mandate
# hashes are named for what they are.
#
# The optional `: Type` group is what makes this fire on TypeScript as well as on env
# and JSON files.
#
# The name part is CASE-INSENSITIVE, written out as character classes rather than by making
# the whole scan case-insensitive — `CRED_RE`'s prefixes (sk-ant-, AKIA, ghp_) are
# case-bearing and would lose precision. The first version matched only uppercase, so
# `const privateKey = "0x…"` and `{signerKey: "0x…"}` — the idiomatic TypeScript and JSON
# forms, and the ones this repository actually writes — passed clean while the comment
# claimed they were caught. Found by adversarial review.
KEY_NAME='([Kk][Ee][Yy]|[Ss][Ee][Cc][Rr][Ee][Tt]|[Mm][Nn][Ee][Mm][Oo][Nn][Ii][Cc])'
KEYLIT_RE='[A-Za-z_]*'"$KEY_NAME"'[A-Za-z_]*["'"'"']?[[:space:]]*(:[[:space:]]*[A-Za-z_.]+)?[[:space:]]*[:=][[:space:]]*["'"'"']?0x[0-9a-fA-F]{64}'

# Publicly documented Anvil dev accounts 0, 1 and 2 — deliberately allowed. These ship in
# Anvil itself and appear in its startup banner; they are test fixtures, not credentials
# (see .env.example). Any OTHER 64-hex value bound to a key-shaped name is a finding.
ANVIL_ALLOW='ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80|59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d|5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a|test test test test test test test test test test test junk'

scan_content() {
  local label="$1" content="$2"
  local hits
  # `-o` IS THE WHOLE FIX FOR A-058's A-1/C-1 AND IT IS LOAD-BEARING: DO NOT REMOVE IT.
  # Every filter below this line is a SUPPRESSOR, and with `-n` alone each one deleted the
  # entire LINE. A line can carry more than one assignment, so suppressing it because ONE of
  # its assignments is a placeholder — or an allowlisted Anvil key — threw the others away
  # unexamined. With `-o` each record is `LINENO:MATCH`, so a suppressor can only ever discard
  # the occurrence it actually matched.
  hits=$(printf '%s' "$content" \
    | grep -onE "$CRED_RE|$ASSIGN_RE|$KEYLIT_RE" 2>/dev/null \
    | grep -vE "$ANVIL_ALLOW" \
    | grep -vE '=[[:space:]]*$|=[[:space:]]*["'"'"']{2}|[:=][[:space:]]*["'"'"']?(0x)?(YOUR_|REPLACE_|EXAMPLE|PLACEHOLDER|xxx)' \
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
  # HTTP(S) URLs are stripped before matching, and only those. A remote URL's path can
  # legitimately contain the segment `/home/` — a documentation citation gathered for the Gate 5
  # source-verification pass had exactly that shape and blocked a commit. (The vendor is not
  # named here on purpose: this file is not on check-vendor-honesty.sh's exclusion list, and
  # naming one would fail D-008(4). That guard caught this comment's first draft.)
  # This is house rule 6 doing what the project keeps catching elsewhere: an instrument pointed
  # at the wrong thing. The rule is that SCRIPTS must resolve $HOME rather than hardcode a local
  # path; a segment inside a remote URL is not a local path and no script can resolve it.
  #
  # Scoped deliberately to http/https. `file:///Users/<name>/...` IS a machine-specific path
  # wearing a URL scheme and must still fail, so `file://` is not stripped. The residual hole is
  # that a real path could be hidden behind an `https://` prefix — it would then also not be a
  # usable path, which is the whole reason the rule exists.
  #
  # sed runs line-by-line, so grep -n's line numbers still refer to the original file.
  hits=$(printf '%s' "$body" \
    | sed -E 's#https?://[^[:space:])"'"'"']*##g' \
    | grep -nE '(/Users/[a-z]|/home/[a-z])' 2>/dev/null || true)
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
