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

STAGED=0
[ "${1:-}" = "--staged" ] && STAGED=1

RED=$'\033[31m'; YEL=$'\033[33m'; RST=$'\033[0m'
[ -t 1 ] || { RED=""; YEL=""; RST=""; }

failures=0

# SCOPE, WIDENED 2026-08-18 (round six, lens 1) — the same argument as the pattern fix
# below, applied to the file list rather than to the value. `git ls-files` is TRACKED ONLY,
# so a credential in an untracked file passed this guard entirely while
# `check-vendor-honesty.sh` beside it already scanned tracked AND untracked, on the stated
# reasoning that "an untracked file in this tree is one `git add -A` away from being
# published". That reasoning was applied to the vendor guard and not to the CREDENTIAL
# guard, which is the asymmetry being closed.
#
# `--exclude-standard` is what keeps this honest rather than noisy: ignored paths
# (`.env`, `contracts/out`, `ts/node_modules`) stay out, because an ignored file is NOT one
# `git add -A` away. Rule 1 above already blocks tracked `.env*` by name, and the .env
# discipline covers the ignored copy.
# NUL-DELIMITED ENUMERATION IN BOTH MODES, WITH INDEX MODE INFORMATION (C4, D-060).
# The previous form parsed newline-joined output of `git ls-files` / `git diff --cached
# --name-only`. Under the default core.quotePath=true a non-ASCII filename is emitted QUOTED
# and octal-escaped, producing a token nothing can open: `[ -f ]` was false and `git show
# ":$f"` failed, and both were followed by `|| continue`. A byte-identical credential was
# BLOCKED under an ASCII name and reported CLEAN under an accented one (Batch A1 cases 9-11).
# `-z` removes the quoting outright, and $(...) is avoided because command substitution STRIPS
# NUL bytes. bash 3.2 here, so no mapfile and no associative arrays.
_sec_err="$(mktemp "${TMPDIR:-/tmp}/sentinel-sec-err.XXXXXXXX")"
_sec_idx="$(mktemp "${TMPDIR:-/tmp}/sentinel-sec-idx.XXXXXXXX")"
_sec_lst="$(mktemp "${TMPDIR:-/tmp}/sentinel-sec-lst.XXXXXXXX")"
_sec_cleanup() { rm -f "$_sec_err" "$_sec_idx" "$_sec_lst"; }

# The index census. `-s` yields "<mode> <object> <stage>\t<path>"; mode 160000 is a GITLINK,
# which is a submodule pointer and not a regular file to scan.
if ! git ls-files -s -z >"$_sec_idx" 2>"$_sec_err"; then
  echo "${RED}FAIL${RST} git ls-files -s failed; refusing to report a clean scan:"
  printf '    %s\n' "$(cat "$_sec_err")"
  _sec_cleanup; exit 1
fi
# A Sentinel checkout always has tracked files. An enumeration that SUCCEEDS with no output
# is the dangerous case — indistinguishable from "nothing to scan" and it reads as clean.
if [ ! -s "$_sec_idx" ]; then
  echo "${RED}FAIL${RST} git ls-files succeeded but returned NO tracked files."
  echo "    Refusing to report a clean scan measured against nothing."
  _sec_cleanup; exit 1
fi
idx_paths=(); idx_modes=()
while IFS= read -r -d '' _rec; do
  idx_modes+=("${_rec%% *}")
  idx_paths+=("${_rec#*$'\t'}")
done < "$_sec_idx"

sec_files=(); sec_kind=(); sec_hasidx=()
_sec_mode_of() {   # linear lookup; the staged set is small and this runs once per path
  local q="$1" i=0
  while [ "$i" -lt "${#idx_paths[@]}" ]; do
    if [ "${idx_paths[$i]}" = "$q" ]; then printf '%s' "${idx_modes[$i]}"; return 0; fi
    i=$((i + 1))
  done
  return 1
}

if [ "$STAGED" -eq 1 ]; then
  # RAW RECORDS, NUL-DELIMITED, EXCLUDING ONLY PURE DELETIONS (R1, CONFIRMED; D-061).
  # This was `--name-only --diff-filter=ACM`, an ALLOW-LIST that silently dropped staged
  # RENAMES and TYPECHANGES. A tracked file renamed with a credential appended to the
  # destination scores R099, enumerated as NOTHING, and the guard printed clean, exit 0,
  # while the commit succeeded through this very hook. `d` (lower case) EXCLUDES deletions
  # and admits everything else, so the set can no longer be narrowed by omission.
  # `C` (copy) was always inside ACM and is unchanged; only R and T were being dropped.
  # A GENUINE STAGED DELETION IS STILL NEVER ENUMERATED and cannot become a false failure
  # (D-059(3), D-061(1), Batch A1 case 7).
  if ! git diff --cached --raw -z --diff-filter=d >"$_sec_lst" 2>"$_sec_err"; then
    echo "${RED}FAIL${RST} git diff --cached --raw failed; refusing to report a clean scan:"
    printf '    %s\n' "$(cat "$_sec_err")"
    _sec_cleanup; exit 1
  fi
  # Record shape: ":<srcmode> <dstmode> <srcsha> <dstsha> <status>" NUL "<path>" [NUL "<dst>"].
  # RENAME AND COPY CARRY TWO PATHS and the SECOND is the destination — the one that exists
  # after the commit and therefore the one to scan. Assuming one path per record would
  # mis-pair every field after the first rename.
  _raw=()
  while IFS= read -r -d '' _fld; do _raw+=("$_fld"); done < "$_sec_lst"
  _k=0
  while [ "$_k" -lt "${#_raw[@]}" ]; do
    _meta="${_raw[$_k]}"
    case "$_meta" in
      :*) ;;
      *) echo "${RED}FAIL${RST} malformed raw record from git diff --cached; refusing."
         printf '    unexpected field: %s\n' "$_meta"; _sec_cleanup; exit 1 ;;
    esac
    read -r _m1 _m2 _s1 _s2 _st <<< "${_meta#:}"
    if [ -z "${_st:-}" ]; then
      echo "${RED}FAIL${RST} raw record missing a status field; refusing."; _sec_cleanup; exit 1
    fi
    _k=$((_k + 1))
    if [ "$_k" -ge "${#_raw[@]}" ]; then
      echo "${RED}FAIL${RST} raw record missing its path; refusing."; _sec_cleanup; exit 1
    fi
    _p="${_raw[$_k]}"; _k=$((_k + 1))
    case "$_st" in
      R*|C*)
        if [ "$_k" -ge "${#_raw[@]}" ]; then
          echo "${RED}FAIL${RST} ${_st} record missing its destination path; refusing."
          _sec_cleanup; exit 1
        fi
        _p="${_raw[$_k]}"; _k=$((_k + 1)) ;;   # the DESTINATION
    esac
    sec_files+=("$_p")
    # The NEW mode decides: a destination that is a gitlink is a submodule pointer, but a
    # regular-file destination may never be skipped.
    if [ "$_m2" = "160000" ]; then sec_kind+=("gitlink"); else sec_kind+=("regular"); fi
    sec_hasidx+=("1")
  done
else
  _i=0
  while [ "$_i" -lt "${#idx_paths[@]}" ]; do
    sec_files+=("${idx_paths[$_i]}")
    if [ "${idx_modes[$_i]}" = "160000" ]; then sec_kind+=("gitlink"); else sec_kind+=("regular"); fi
    sec_hasidx+=("1")
    _i=$((_i + 1))
  done
  if ! git ls-files --others --exclude-standard -z >"$_sec_lst" 2>"$_sec_err"; then
    echo "${RED}FAIL${RST} git ls-files --others failed; refusing to report a clean scan:"
    printf '    %s\n' "$(cat "$_sec_err")"
    _sec_cleanup; exit 1
  fi
  while IFS= read -r -d '' _f; do
    sec_files+=("$_f"); sec_kind+=("regular"); sec_hasidx+=("0")
  done < "$_sec_lst"
fi
_sec_cleanup

# Content for entry $1. Prints it on stdout. Returns 0 read, 2 legitimately skip, 1 REFUSE.
# D-060: in DEFAULT mode a regular tracked path whose working-tree copy is absent but whose
# INDEX BLOB EXISTS is read from the index — until the deletion is staged the index still
# carries the content, and default mode may not report clean while known repository content
# went unread. The previous `[ -f "$f" ] || continue` skipped exactly that case.
_sec_content() {
  # bash 3.2: split, because a later expansion in the SAME `local` cannot rely on an
  # earlier name in it under `set -u`.
  local i="$1"
  local pth="${sec_files[$i]}"
  local knd="${sec_kind[$i]}"
  local hix="${sec_hasidx[$i]}"
  [ "$knd" = "gitlink" ] && return 2
  if [ "$STAGED" -eq 1 ]; then
    git show ":$pth" 2>/dev/null && return 0
    return 1
  fi
  if [ -f "$pth" ]; then cat -- "$pth" 2>/dev/null && return 0; return 1; fi
  # D-061's ruling: absent working-tree copy, index blob present -> scan the INDEX BLOB.
  # (Ruled after D-060 was recorded; D-060's entry does not contain it. Citation corrected.)
  # Until the deletion is staged the index still carries the content, and default mode may
  # not report clean while known repository content went unread.
  if [ "$hix" = "1" ]; then git show ":$pth" 2>/dev/null && return 0; return 1; fi
  # Exists but is not a regular file — a symlink to a directory, a device. Never scannable,
  # and NOT the C4 defect, which is a REGULAR file made unreadable by path quoting. Skipping
  # here is legitimate; skipping a regular file is what the repair forbids.
  if [ -e "$pth" ] || [ -L "$pth" ]; then return 2; fi
  return 1
}
_sec_refuse() {
  echo "${RED}FAIL${RST} could not read $1 — refusing to report it clean."
  echo "    An unreadable file is not a scanned file (C4, D-060)."
  failures=$((failures + 1))
}

# --- 1. Secret-bearing files must never be tracked -------------------------
_i=0
while [ "$_i" -lt "${#sec_files[@]}" ]; do
  f="${sec_files[$_i]}"; _i=$((_i + 1))
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
done

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
#
# WIDENED 2026-08-18 (round six, lens 1) UNDER THE D-052(b) REPAIR PROTOCOL. Three separate
# evasions, all with assignment context AND a key-shaped name, so none was the residual the
# design note above declares. THE ARGUMENT, stated so the next repair can be checked against it
# rather than against the probes: a 64-hex value bound to a key-shaped identifier is a
# credential HOWEVER IT IS SPELLED. The previous pattern encoded three accidental spellings.
#
#   (a) NO `0x`. The pattern required the prefix. `SENTINEL_SIGNER_KEY=<64hex>` — THIS
#       REPOSITORY'S OWN VARIABLE (ts/src/corpus/run.ts) — passed clean, and coverage of the
#       no-prefix form depended entirely on whether the name happened to contain one of
#       ASSIGN_RE's nine hard-coded tokens. `SIGNER_KEY` is not one of them.
#   (b) A DIGIT IN THE NAME. The identifier class was `[A-Za-z_]*`, so `KEY_1`, `deployerKey2`
#       and `signer_key_2` all fell out of the pattern.
#   (c) A COLLECTION VALUE. `{"signerKeys": ["0x<64hex>"]}` — the `[` sat between the assignment
#       operator and the value.
#
# The bare-64-hex residual in the design note is UNCHANGED and still deliberate: this widening
# only ever fires when a KEY/SECRET/MNEMONIC-shaped name is bound to the value, which no
# legitimate bytes32 constant here is. Typehashes, domain separators and mandate hashes are
# named for what they are.
#
# WHAT THIS REPAIR DOES NOT REACH — required by the D-052(b) protocol step 6, because a repair
# with no stated residual is asserting completeness and that assertion has been wrong four times
# running. **A key-shaped name is matched only where it binds the value DIRECTLY.** Falsified and
# still passing: `const k = {apiKey3: {"v": "<64hex>"}}` — the 64-hex is bound to `v`, which is
# not key-shaped, inside a container that is. One level of `[`/`(`/`{` between the operator and
# the value IS covered; arbitrary nesting is not, and chasing it with a regex would trade a real
# false-negative for a worse false-positive rate on a repository full of bytes32 literals. Under
# the argument above this case sits with the DESIGN NOTE's declared bare-literal residual — the
# value has no key-shaped binding of its own — and it is recorded here rather than left for a
# reviewer to find. Register §8.2.
#
# FALSIFIED BEFORE BEING BELIEVED, in both directions, on the live tree (round six adjudication):
# the three evasions above now BLOCK; two routes the reviewer never demonstrated — a no-`0x`
# lowercase TypeScript type annotation with a digit, and a MNEMONIC-family name holding a
# collection — also BLOCK; the untracked-file scope gap now BLOCKS and did not before; the
# `--staged` invocation shape blocks the same content; and all four negative controls still pass
# clean (both Anvil allowlist spellings, a genuine placeholder, and a legitimate non-key bytes32).
KEY_NAME='([Kk][Ee][Yy]|[Ss][Ee][Cc][Rr][Ee][Tt]|[Mm][Nn][Ee][Mm][Oo][Nn][Ii][Cc])'
KEYLIT_RE='[A-Za-z0-9_]*'"$KEY_NAME"'[A-Za-z0-9_]*["'"'"']?[[:space:]]*(:[[:space:]]*[A-Za-z_.]+)?[[:space:]]*[:=][[:space:]]*[[({]?[[:space:]]*["'"'"']?(0x)?[0-9a-fA-F]{64}'

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

_i=0
while [ "$_i" -lt "${#sec_files[@]}" ]; do
  f="${sec_files[$_i]}"; _idx=$_i; _i=$((_i + 1))
  [ -z "$f" ] && continue
  [ "$(basename "$f")" = "check-secrets.sh" ] && continue   # this file defines the patterns
  if _body="$(_sec_content "$_idx")"; then _rc=0; else _rc=$?; fi
  if [ "$_rc" -eq 2 ]; then continue; fi            # gitlink: not a regular file
  if [ "$_rc" -ne 0 ]; then _sec_refuse "$f"; continue; fi
  scan_content "$f" "$_body"
done

# --- 4. Machine-specific absolute paths ------------------------------------
# House rule 6 / A-008: scripts resolve $HOME, they do not hardcode /Users/<name>.
#
# CASE-SENSITIVITY FIXED 2026-08-18 (D-052(b); recorded in register §8.2 since round five and
# not fixed until now). The scan was `(/Users/[a-z]|/home/[a-z])`, so a capitalised home
# directory passed — and macOS derives exactly that shape from a full name. The workspace
# machine-state guard, which uses `[A-Za-z0-9._-]`, caught a path this guard did not.
#
# THE ARGUMENT: a guard must not depend on the CASE of the thing it is scanning. That is the
# identical defect A-047 fixed one file over — `check-vendor-honesty.sh`'s vendor scan was
# case-sensitive while the label scan beside it was not, so a lowercase spelling of the scanned
# token passed while its capitalised form failed — and the argument was not carried across to
# this file at the time.
# Falsified in both directions: a capitalised path now fails and the lowercase form still does.
#
# The first draft of THIS comment illustrated that defect with the literal token, and
# `check-vendor-honesty.sh` blocked the commit for naming a vendor in a measurement artifact
# (D-008(4)) — the same way it caught the first draft of the rule-4 comment below. Recorded
# because a guard catching its own documentation is the cheapest possible evidence that it works.
_i=0
while [ "$_i" -lt "${#sec_files[@]}" ]; do
  f="${sec_files[$_i]}"; _idx=$_i; _i=$((_i + 1))
  [ -z "$f" ] && continue
  [ "$(basename "$f")" = "check-secrets.sh" ] && continue
  if body="$(_sec_content "$_idx")"; then _rc=0; else _rc=$?; fi
  if [ "$_rc" -eq 2 ]; then continue; fi
  if [ "$_rc" -ne 0 ]; then _sec_refuse "$f"; continue; fi
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
    | grep -nE '(/Users/[A-Za-z]|/home/[A-Za-z])' 2>/dev/null || true)
  if [ -n "$hits" ]; then
    echo "${YEL}BLOCKED${RST} $f — machine-specific absolute path (use \$HOME):"
    printf '%s\n' "$hits" | sed 's/^/    /'
    failures=$((failures + 1))
  fi
done

if [ "$failures" -gt 0 ]; then
  echo
  echo "${RED}secret guard: $failures finding(s).${RST} Do not weaken this guard to make a commit pass (AGENTS.md)."
  echo "If this is a false positive, fix or refine the guard and document why."
  exit 1
fi

echo "secret guard: clean"
