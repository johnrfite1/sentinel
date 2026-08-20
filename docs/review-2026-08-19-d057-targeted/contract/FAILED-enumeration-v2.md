> # SUPERSEDED — belongs to a FAILED contract (D-060(1))
> Its own commands proved incomplete twice: they were shaped like already-reported sites.
> **Batch cards enumerate by file/shebang and OWNERSHIP, not by searching for a known idiom.**

---

# Enumeration commands — v2, derived from MECHANISM rather than from reported line numbers

Run from the repository root at base SHA `a18e6e6`. **Use `/usr/bin/grep`**: the shell's `grep` is
a `ugrep` wrapper honouring `--ignore-files` and returns a clean-looking zero for ignored files.
**Plant a canary and confirm the search finds it before trusting any zero result.**

## Why v1's commands were insufficient — recorded so the mistake is not repeated

v1 enumerated with patterns shaped like the sites already reported. Each therefore stopped where
its report stopped. **`cd "$(` missed the two-step `ROOT="$(git rev-parse …)"` idiom and with it
EIGHT scripts.** The corrected commands below match the *mechanism*.

## A-R1 — repository-root resolution: BOTH idioms
```
/usr/bin/grep -lE '(cd "\$\(git rev-parse --show-toplevel\)"|[A-Za-z_]+="\$\(git rev-parse --show-toplevel\)")' scripts/*.sh
```
→ **13 scripts.** `test.sh:60`'s `BASH_SOURCE` bootstrap is separate and exempted.
Behaviour probe (not inference): `bash -c 'set -euo pipefail; cd ""; echo $?'` → **0, no abort.**

## A-R2 — every skip point in the secrets guard, and WHICH MODE THE GATE RUNS
```
/usr/bin/grep -nE '\|\| *continue|\[ -f "\$f" \]|\[ -z "\$f" \]' scripts/check-secrets.sh
/usr/bin/grep -n 'check-secrets' scripts/test.sh          # -> :176, NO --staged => DEFAULT mode
```

## A-R3 — section extraction, ALL THREE LANGUAGES AND TIE-BREAK STYLES
```
/usr/bin/grep -nE "awk '/\^#" scripts/*.sh                        # shell/awk consumers
/usr/bin/grep -rnE '\.split\("#{2,5} ' verifier/*.py               # Python consumers
/usr/bin/grep -rnE '(sec[0-9]+|table_sha|declared)=\$\(awk' scripts/*.sh
```
**A shell-only sweep misses `verifier/test_verifier.py:930`, whose tie-break is `---` rather than
a heading.** Anchor depth per consumer must be read, not assumed: the terminator `#{1,4}` is a
FIXED class and is correct only where the anchor happens to be depth 4.

## A-R4 / A-R5 — uniqueness and membership
```
/usr/bin/grep -nE 'head -1|head -n *1' scripts/*.sh
/usr/bin/grep -nE 'grep -q' scripts/*.sh                          # unanchored membership tests
```

## A-R6 — floor occurrences, PARAGRAPH-NORMALIZED (line grep DISALLOWED, D-058(6))
Split on blank lines, collapse whitespace, then match. **Self-test against a known WRAPPED string
before trusting any zero** — two real defects survived a line-based sweep that reported clean.
Probe behaviour rather than inferring it:
```
# reader is FIRST-wins, bash is LAST-wins; with a duplicate they disagree in OPPOSITE directions
# single definition -> they agree (the control proving the probe discriminates)
```

## Batch B / Batch C — unchanged from v1 and independently re-verified
```
/usr/bin/grep -nE '^\s*(event [A-Z]|emit )' contracts/src/SentinelVault.sol
/usr/bin/grep -nE '_consumeAndCall\(' contracts/src/SentinelVault.sol
awk 'NR>=170 && NR<=260 && /continue;|throw new|return \{|pendingOnly/ {print NR": "$0}' ts/src/signer/vault.ts
```
