# R4 — DEAD PROBES — every probe that measured nothing

**I had four.** Three had a common root cause worth naming for the next round, and one of the
three **printed a plausible-looking result that I would have mis-read as a finding** if I had
not cross-checked it. Recorded in the order they happened.

---

## DP-1 — `for c in $codes` under zsh: measured ONE code, printed a result that looked like a measurement

**What I was trying to measure.** Which of the 41 `EVAL_*` codes actually appear inside §5.7.1
(lines 571–606) versus only elsewhere in the proposal.

**What I ran** (via the Bash tool, whose shell is **zsh**, not bash):

```
codes="$(sed -n '/^export const EVAL_CODES = \[/,/^\] as const;/p' "$CHECKS" | grep -oE '"EVAL_[A-Z0-9_]+"' | tr -d '"' | sort -u)"
for c in $codes; do
  if grep -q "$c" /tmp/sec5711.txt; then inside=$((inside+1)); else outside=$((outside+1)); fi
done
```

**What it printed:**

```
total codes: 41
INSIDE 5.7.1 : 1
OUTSIDE ONLY : 0
codes NOT in 5.7.1:
```

**Why it is dead.** zsh does **not** word-split unquoted parameter expansions by default. `$codes`
is one 41-line string, so the loop body executed **once**, with a multi-line needle. `total codes:
41` was computed by `wc -l` and is real; the two numbers under it describe a single iteration.

**Why it is dangerous rather than merely useless.** `OUTSIDE ONLY : 0` with an empty "codes NOT
in 5.7.1" list reads exactly like a clean pass — the same conclusion the correct probe later
reached, arrived at by measuring nothing. It agreed with the truth **by accident**. Had the real
answer been "12 codes are outside §5.7.1", this probe would have reported zero and I would have
recorded a null result.

**Corrected probe.** Re-ran the identical logic inside `bash -c '…'`; it iterated 41 times and
returned `INSIDE 5.7.1 : 41 / OUTSIDE ONLY : 0`. That is the number quoted in NULL-RESULTS N6
and in R4-F3. The guard scripts themselves are `#!/usr/bin/env bash`, so they were never
affected — only my probe was.

## DP-2 — `grep -rn "X" --include=*.ts` under zsh: errored before reaching any file

```
grep -rn "${n}(" --include=*.ts --include=*.sol --include=*.py . 
#   (eval):1: no matches found: --include=*.ts
```

zsh tried to glob `*.ts` in the current directory, found nothing, and aborted the command. **Six
consecutive type-string searches returned nothing and the tool reported no failure** — the
output was six `--- Name ---` headers with nothing under them, which is visually identical to
"this type string appears nowhere in the tree." Re-run inside `bash -c` with the patterns
quoted, which is where the four-implementation map in NULL-RESULTS N6 came from.

**Root cause of DP-1 and DP-2 is the same and it is environmental:** the harness shell is zsh
while every script under review is bash. Any probe written in bash idiom must be run as
`bash -c '…'` or it is not measuring the thing the scripts do.

## DP-3 — `cat -A` on macOS: no such option

```
grep -n -v '^[0-9a-f]\{64\}  ' MANIFEST-sha256.txt | cat -A
#   cat: illegal option -- A
```

BSD `cat` has no `-A`. The command exited non-zero and printed a usage message; nothing about
the manifest was measured. Re-run with `cat -v` plus `od -c`, which found the single non-hash
line (the deliberate, disclosed symlink record).

## DP-4 — first attempt at counting invocations of each guard included the guard's own file

My first `grep -rn "$(basename $g)"` matched each script's own filename inside itself and inside
`docs/`, so every guard looked "invoked" including `check-review-scope.sh`. Filtered out
self-matches and `docs/` before believing it; the corrected run is NULL-RESULTS N4 and it
isolates `check-review-scope.sh` as the only guard with no invocation.

---

## Probes that were live but returned nothing interesting — NOT dead

Distinguished deliberately, because "found nothing" and "measured nothing" are different and
this project has confused them before:

- The `shasum -a 256 -c` run over the round-six archive **did** hash all 971 files (971 OK). It
  measured, and the answer was "sound".
- `cmp` of `ADJUDICATED-ROUND-SIX.md` and the nine lens briefs **did** compare bytes. Identical.
- The reproduction of the `G-3` mechanism over 50 corpus results **did** walk every
  `L3_full_conformance` layer and returned two classes. It measured.
- Both `check-eval-codes.sh` and `check-type-strings.sh` mutations were confirmed to have moved
  the input (`grep -c` on the mutated region, before running the guard) precisely so that the
  guards' silence could be believed.
