# V5 — PROBES

Every command below was run inside the V5 worktree (`<WORKTREE>`), checked out at the frozen
commit `c8d15a76425544148d7da2f8fa0c003feb6ad2b7`. The primary tree was never written to except
for this evidence directory. Paths are repository-relative.

```
$ git rev-parse HEAD
c8d15a76425544148d7da2f8fa0c003feb6ad2b7
$ git status --porcelain
?? ts/node_modules          # pre-existing, untracked, not mine
```

---

## P0 — Tooling validation BEFORE any zero result was trusted

The brief warns that three local tooling quirks return zero hits that read like a clean sweep.
All three were confirmed present, and each was neutralised before use.

### P0.1 — `grep` is a ugrep wrapper honouring `--ignore-files`

```
$ type grep
grep is a shell function ... ARGV0=ugrep ... -G --ignore-files --hidden -I --exclude-dir=.git ...
$ grep --version
ugrep 7.5.0 aarch64-apple-macosx
```

**Neutralised by** using `command grep` (real BSD grep) for line-based searches and a Python
walker for wrap-tolerant searches. `git grep` was rejected as a primary tool: it silently misses
untracked files, and its exit status is masked when piped to `head`.

### P0.2 — `xargs` has no `-a`; `IFS` lacks newline

```
$ xargs -a /dev/null echo
xargs: invalid option -- a
$ printf '%q\n' "$IFS"
\ $'\t'$'\n'$'\0'
```

`IFS` here **does** contain newline, but `xargs -a` is absent as warned. No probe below depends
on either, by construction — all iteration is done inside Python.

### P0.3 — CONTROL: plant a string, confirm the search finds it

```
$ echo "CANARY_ZZQQ_PLANT remains accepted here is five" > docs/_canary_probe.md
$ grep -rn "CANARY_ZZQQ_PLANT" .            -> docs/_canary_probe.md:1:  HIT
$ command grep -rn "CANARY_ZZQQ_PLANT" .    -> ./docs/_canary_probe.md:1: HIT
$ git grep -n "CANARY_ZZQQ_PLANT"           -> (no output; untracked file invisible to git grep)
```

**Establishes:** both grep paths see new content in `docs/`; `git grep` would have produced a
false clean sweep. Canary removed afterwards; `git status` re-confirmed clean.

### P0.4 — CONTROL: the hard-wrap trap is real, and the wrap-tolerant searcher defeats it

Helper written to scratch (not to either tree): walks a directory, joins every line of a file
with a single space, then regex-matches across the join, reporting the line number of the match
start.

```
$ printf 'line one has WRAPPED_CANARY_ALPHA\nBETA_END on the next line\n' > docs/_canary_wrap.md
$ command grep -rc "WRAPPED_CANARY_ALPHA BETA_END" docs/_canary_wrap.md
docs/_canary_wrap.md:0                     <-- line-based grep MISSES it (the trap)
$ python3 flowgrep.py "WRAPPED_CANARY_ALPHA BETA_END" docs
_canary_wrap.md:1: ...line one has WRAPPED_CANARY_ALPHA BETA_END on the next line...
```

**Establishes:** line-based regex returns a clean-looking zero on a phrase that straddles a line
break, and the wrap-tolerant searcher finds it. **This trap caught a real defect in this review**
— see P3.4, where the surviving text is `ten accepted\nas documented limits`.

### P0.5 — A DEAD PROBE I RAN, CAUGHT, AND CORRECTED

My first count sweep passed **files** to a searcher that expects a **directory**. `os.walk()` on
a file yields nothing, so it printed zero hits across every reader-facing document — a perfect
false clean sweep.

```
$ python3 flowgrep.py "gate" docs/session-state.md "*"      -> (nothing)
$ python3 flowgrep.py "gate" docs "*"                       -> many hits
```

**Establishes:** the zero was an artifact of the invocation, not of the tree. Every sweep below
was re-run against a directory root and each carries a control proving the regex can hit.

---

## ITEM 1 — the accepted-limit count

### P1.1 — Independent derivation from `docs/v1-1-register.md` §13.4

The brief names §13.4 as the authority. Rather than read the asserted number, the status column
was parsed mechanically.

```
$ T=$(sed -n '/^| | Verdict | Severity after adjudication | Status |/,/^### 13.5/p' \
      docs/v1-1-register.md)

# total data rows
$ echo "$T" | awk -F'|' 'NF>3 && $2 !~ /Verdict/ && $2 ~ /`/' | wc -l
24                                          # matches the section's own claim of 24 leads

# rows whose STATUS cell contains ACCEPTED anywhere
$ echo "$T" | awk -F'|' 'NF>3 && $5 ~ /ACCEPTED/ {print $2}'
 `D-07`
 `D-09`
 `E5`
 `F-VAULT-4`
 `F-VAULT-5`
 `G-3`
-> 6
```

**Result: SIX, derived independently — `D-07`, `D-09`, `E5`, `F-VAULT-4`, `F-VAULT-5`, `G-3`.**
This matches §11.0's asserted six-item list exactly, including `G-3`.

### P1.2 — FALSIFICATION of my own counting method

A count that cannot move is not a measurement.

```
$ python3 - <<'EOF'   # flip G-3's status to FIXED, assert the edit actually applied
s2 = s.replace("| `G-3` | CONFIRMED | MEDIUM -> LOW | **ACCEPTED (D-051(b), §11.0)**",
               "| `G-3` | CONFIRMED | MEDIUM -> LOW | **FIXED (mutation)**", 1)
assert s2 != s, "MUTATION DID NOT APPLY - dead probe"
EOF
mutation applied
$ <recount>   -> 5      # the method MOVED
$ cp /tmp/reg.bak docs/v1-1-register.md
$ <recount>   -> 6      # restored
$ git diff --stat -- docs/v1-1-register.md   -> (empty)
```

**Establishes:** the counting method observes the source, and the worktree was left clean.

### P1.3 — Cross-derivation from §11.0's own roster

```
$ sed -n '655,790p' docs/gate-s2-evidence.md | command grep -c "^- \*\*\`"
10
```

The ten roster entries are `D-07 D-09 D-10 E5 F-VAULT-4 F-VAULT-5 G-3 G-5 H-5 H-8`.
A-076 recorded five FIXES: `D-09(c)`, `D-10`, `G-5`, `H-5`, `H-8`.
Four of those remove a whole entry (`D-10`, `G-5`, `H-5`, `H-8`). The fifth, `D-09(c)`, removes
only a **sub-part** of an entry that stays on the list, because `D-09`(a),(b) remain accepted.

**10 entries − 4 fully-removed entries = 6.** SIX is correct.
**10 − 5 = 5.** The arithmetic *as the documents state it* is wrong. See P1.4.

### P1.4 — The stated derivation does not compute (DEFECT)

```
$ python3 flowgrep.py "Ten minus the five fixed" docs
gate-s2-evidence.md:513: ...WHAT IS ACCEPTED TODAY IS SIX: ... AND `G-3`.**
                          Ten minus the five fixed leaves six, not five. ...
```

Every surface states the derivation in the same non-computing form:

| Surface | Text | Literal result |
|---|---|---|
| `docs/gate-s2-evidence.md` §11.0 (l.513) | "Ten minus the five fixed leaves six, not five." | 5 |
| `docs/gate-s2-evidence.md` §11.0 (l.548, **unstruck, bolded**) | "FIVE OF THESE TEN ARE NO LONGER ACCEPTED LIMITS" | 5 remain |
| `docs/exit-criterion-packet.md` §3 (l.95) | "D-051(b) accepted ten; **A-076 FIXED five**" | 5 |
| `docs/decisions.md` A-080 (l.248) | "ten accepted, five FIXED by A-076, `G-3` never in D-056(a)'s scope, therefore **SIX**" | 5 |

`G-3` was never fixed, so it was already inside the remainder; naming it cannot add the missing
one. **The single fact that makes SIX correct — that `D-09` is simultaneously in the fixed set
and the accepted set — is stated on no surface.**

Line 548's claim is independently false: `D-09` is one of "these ten" and **is** still an
accepted limit, so four of the ten, not five, are no longer accepted limits.

### P1.5 — ROOT CAUSE: §13.4's `D-09` cell is labelled FIXED first

```
$ echo "$T" | awk -F'|' 'NF>3 && $5 ~ /^ *\*\*ACCEPTED/ {print $2}'
 `D-07` `E5` `F-VAULT-4` `F-VAULT-5` `G-3`      -> 5     (rows LABELLED ACCEPTED)
$ echo "$T" | awk -F'|' 'NF>3 && $5 ~ /ACCEPTED/  {print $2}'
 `D-07` `D-09` `E5` `F-VAULT-4` `F-VAULT-5` `G-3` -> 6   (rows MENTIONING ACCEPTED)

$ echo "$T" | command grep "^| \`D-09\`"
| `D-09` | CONFIRMED | LOW stands for (a) and (b) | **FIXED (A-076)** — (c)'s intersected-ceiling
regression added; ... (a),(b) remain ACCEPTED (D-051(b)) |
```

**Establishes:** the table the brief calls authoritative yields **FIVE** to a reader who counts
rows marked ACCEPTED and **SIX** only to one who reads every cell to its end. This is why every
prose derivation lands on the wrong arithmetic.

### P1.6 — Sweep for surviving live FIVE (wrap-tolerant, whole tree)

```
$ python3 flowgrep.py "(accepted|accept|remains?|remainder|limits?)[^.]{0,70}\bfive\b|\bfive\b[^.]{0,80}(accepted|accepted limits|remain)" . "*"
```

Reader-facing hits triaged: `docs/decisions.md` l.85/183/199/223 are unrelated senses ("round
five", "five lines earlier", "five D-008 questions"); `docs/gate-s2-evidence.md` l.509 and l.551
are **struck** (`~~…~~`); l.548 is the defect at P1.4; `docs/session-state.md` l.106 and
`docs/exit-criterion-packet.md` l.95 describe the error correctly; `docs/v1-1-register.md` l.416
and `verifier/verify.py` l.2309 are unrelated. **23 further hits are under `docs/review-…/` and
are frozen evidence — correctly left unaltered.**

`docs/decisions.md` A-076 (l.243) carries "§11.0's heading moves from TEN to FIVE and names what
remains (…)" **unstruck**, but immediately followed in the same paragraph by a bolded
`[CORRECTED 2026-08-19 (A-080). THE REMAINDER STATED HERE IS WRONG …]`. Annotated in place, as
the commit describes. Recorded as a residual, not a failure.

### P1.7 — Sweep for stale NINE

```
$ python3 flowgrep.py "\bnine\b[^.]{0,70}(accepted|accept|limits?|remain)|(accepted|accept|limits?|remain|restating)[^.]{0,70}\bnine\b" . "*"
```

`docs/gate-s2-evidence.md` l.522 — `silently restating it as ~~nine~~ **six**` — **struck and
replaced.** Every other `nine` is a different set (the nine MEDIUMs fixed by A-068, the nine LOW
findings of D-051(b), nine lens briefs). **No stale nine survives unstruck.**

### P1.8 — CONTROL: legitimately historical TEN is preserved, not flattened

```
$ python3 flowgrep.py "(accepted|documented limits?)[^.]{0,90}(ten|six|five|nine)|\b(ten|six|five)\b[^.]{0,40}(accepted|documented limit)" . "*"
```

Still present and correctly **not** marked as errors:

- `docs/decisions.md` l.217 — D-051(b) itself: "THE NINE LOW AND ONE INFO BECOME DOCUMENTED
  LIMITS" (9 + 1 = the original ten — the origin of the number).
- `docs/decisions.md` l.219, l.237, l.241 — A-075-era entries stating ten, true on their dates.
- `docs/v1-1-register.md` l.749 — "ten that John had ACCEPTED", inside an explicitly labelled
  2026-08-18 snapshot.
- `docs/gate-s2-evidence.md` §11.0 heading — keeps "Ten … — NOW SIX".
- `git show --stat HEAD` touches **6 files, none under `docs/review-…/`** — all reviewer and
  adjudication artifacts preserved byte-identical.

**CONTROL PASSES: history is intact.**

### P1.9 — CONTROL: the sibling sweep regex demonstrably fires

```
$ <same regex as P1.8, over docs/>   -> 12 hits    # regex is live
$ <same regex, filtered to HANDOFF.md / README.md> -> (none)
```

**Establishes:** the zero for `HANDOFF.md`/`README.md` is a real absence, not a dead probe.

---

## ITEM 2 — the rejected hash/recheck design

### P2.1 — COLD READ of `docs/v1-1-register.md` §13.6

```
$ sed -n '823,876p' docs/v1-1-register.md
```

The prescription is struck:
`~~**have the gate hash its own file at start and re-check at exit, failing loudly if it changed
underneath itself.** Roughly four lines.~~`

and is immediately followed by
`**THE STRUCK SENTENCE DIRECTLY ABOVE IS THE REJECTED DESIGN. DO NOT BUILD IT.**`

and, twenty lines later, by an explicit disambiguation:
`**The rejected design is the struck "hash at start, re-check at exit" prescription above — NOT
the struck "not built, deliberately" note beside it, which is merely spent.**`

**Verdict of the cold read: I would come away certain the design is rejected, not buildable.**

### P2.2 — The warning points at the right text

Two struck spans exist in §13.6: the prescription (l.834) and the spent "Not built,
deliberately" note (l.840). The warning names its referent twice — positionally ("DIRECTLY
ABOVE") and by quotation ("hash at start, re-check at exit … NOT the struck 'not built,
deliberately' note"). **Unambiguous.**

### P2.3 — The adopted design is preserved, element by element

All five elements the brief lists are present in §13.6 item 4:

| Element | Present |
|---|---|
| copy | yes — "the body is copied" |
| open read-only | yes — "opened read-only" |
| unlink | yes — "and **unlinked**, so it has no filesystem pathname at all" |
| execute as `/dev/fd/N` | yes — "it executes as `/dev/fd/N`" |
| external supervisor + completion token | yes — "an **external supervisor** refuses success unless the body emits a completion token" |
| exit 0 alone is not success | yes — "**exit 0 alone is not success**" |

### P2.4 — Verified against the CODE, not just the prose

```
$ sed -n '58,135p' scripts/test.sh
_gate_before="$(shasum -a 256 <"$_gate_src" | cut -d' ' -f1)"
exec 9<"$_gate_tmp"; rm -f "$_gate_tmp"                     # read-only fd, then UNLINK
_gate_token="$(head -c 32 /dev/urandom | shasum -a 256 | cut -d' ' -f1)"
SENTINEL_GATE_TOKEN="$_gate_token" bash /dev/fd/9 "$@" 3>"$_gate_fifo" &
...
if [ "$_gate_seen" != "$_gate_token" ]; then ... exit 5 ; fi
```

Every element in P2.3 is implemented as described. The completion token is passed **in the
environment** to the body process, which then removes it:

```
$ sed -n '150,152p' scripts/test.sh
_gate_token_local="$SENTINEL_GATE_TOKEN"
unset SENTINEL_GATE_TOKEN
```

**This is the mechanism the residual is about, and it confirms the residual is accurate.**

### P2.5 — The threat-model residual, checked against A-077's own text

```
$ python3 flowgrep.py "forge the completion token|read the (body|executing body)'?s? environment" . "*"
docs/decisions.md:245  (A-077(b), the source):
  "(b) **A same-user actor able to READ the body's environment could forge the completion
   token**; the nonce defends against corruption, not against an attacker with environment
   access, ..."
docs/v1-1-register.md:869  (§13.6 item 5, the new text):
  "**A same-user actor able to READ the executing body's environment can forge the completion
   token.** The nonce defends against CORRUPTION of the body, not against an attacker who
   already has environment access, and A-077 states that rather than defending against it."
```

**Establishes:** §13.6 item 5 is faithful to A-077(b) — same actor, same capability, same
mechanism, same explicit non-defence. Not a paraphrase that drifts.

`scripts/check-gate-immutability.sh` l.37-40 carries the same residual in its own header
("cannot rule out a same-user actor that can READ the body's environment forging the completion
token; that is stated rather than defended against").

### P2.6 — FALSIFICATION with the guard's own unprotected control

```
$ ./scripts/check-gate-immutability.sh
  extracted 146 lines of bootstrap verbatim from scripts/test.sh
2a. CONTROL: an unprotected script must be corrupted by this probe
  unprotected control corrupted (exit 127) — the probe is dangerous
2b. the protected subject under the same edit
  body ran to completion — the edit could not reach it
  exit 4 — a changed source is refused a zero exit
5. body exits 0 without completing — EXIT 0 IS NOT SUCCESS
  refused with exit 5
  and says so, rather than failing for an unrelated reason
gate immutability: 10/10 ...
---- RAW EXIT STATUS: 0 (status is NOT the evidence; output above is) ----
```

**Establishes:** the adopted design that §13.6 describes is real and behaves as described. The
**paired control fired** — the unprotected subject WAS corrupted (exit 127), so probe 2b is not
passing vacuously. Probe 5 independently confirms "exit 0 alone is not success" is implemented,
not merely asserted.
**Does NOT establish:** anything about the environment-read residual, which the guard's own
header declares out of scope. Consistent with the register.

### P2.7 — Sibling sweep: does the rejected design read as live ANYWHERE?

```
$ python3 flowgrep.py "hash (its own file|at start|the (gate|script))[^.]{0,120}|re-?check at (exit|end)" . "*"
```

CONTROL first — a planted copy of the sentence in a scratch directory was found by the same
regex, so the sweep is live.

| Surface | Reads as |
|---|---|
| `scripts/test.sh` l.23 | REJECTED — "TWO DESIGNS WERE TRIED AND BOTH FAILED … 1. Hash at start, re-check at end (rejected by John before it was built)" |
| `scripts/check-gate-immutability.sh` l.10 | REJECTED — "TWO PREVIOUS DESIGNS FAILED … rejected by John before it was built" |
| `docs/v1-1-register.md` l.834/847/858 | REJECTED — struck, labelled, reason carried |
| `docs/decisions.md` l.242/243/248 | REJECTED — John's ruling quoted |
| `docs/review-2026-08-18-d055e/…` | frozen evidence, correctly unaltered |
| **`docs/decisions.md` l.241 (A-075)** | **reads affirmatively — see below** |

**The one imperfect surface.** `docs/decisions.md` A-075 still says, unstruck and unannotated in
that paragraph:

> **A mechanical guard is possible and is NOT built:** the gate could stamp its own file's hash
> at start and re-check it at the end, failing loudly if the script changed underneath itself.

It is a dated historical ledger entry, the rejection is recorded in the two entries immediately
following it, and the sentence itself points the reader to `docs/v1-1-register.md` — where the
design is now struck. Recorded as a **residual**, not a failure: the pointer leads to the
rejection, and `docs/decisions.md` is append-only by house rule.

### P2.8 — Residual ambiguity in §13.6's lead-in

The clause introducing the struck prescription is **not** struck:
`"…and there is a cheap mechanical one: ~~have the gate hash…~~"`. The surviving lead-in asserts
a cheap mechanical defence exists while the only thing it introduces is rejected. The bolded
`DO NOT BUILD IT` on the next line resolves it, and the adopted design *is* a mechanical
defence, so the sentence is not false. **Minor residual; does not create buildable ambiguity.**

---

## ITEM 3 — `docs/session-state.md` as a truthful handoff

### P3.1 — The seven required facts, each located

| # | Required fact | Where | Plain? |
|---|---|---|---|
| 1 | bounded review completed | l.15 §hdr step 1; l.208 | yes |
| 2 | CRITICAL reverified at `497d1ce` | l.16 step 2; l.220; l.259 | yes |
| 3 | `R3-F6`/`R3-F7`/`R4-F4` FAILED | l.17 step 3; l.220; l.276-281 | yes |
| 4 | `V3-N1` + residuals found | l.18 step 3; l.220 | yes |
| 5 | corrections in `8990255`, **after** verifiers | l.19 step 4; l.220 | yes |
| 6 | those corrections NOT reverified | l.20 step 5 (caps); l.220; l.259 | yes |
| 7 | targeted reverification outstanding | l.22; l.208; l.248 | yes |

All seven are stated in the first 25 lines, under a heading that orders the reader to read them
before any other line in the file.

### P3.2 — Verified against `git log`, not against the file

```
$ git log --oneline -5 --date=short --format="%h %ad %s"
c8d15a7 2026-08-19 A-080: a narrow correction checkpoint ...
254db64 2026-08-19 A-079: handoff documents rewritten for a fresh instance
8990255 2026-08-19 A-078: the D-057(5) reverification — three of my repairs returned as failed
497d1ce 2026-08-19 A-077: the D-057 remediation — R1-F1 repaired at the argument level
fc11142 2026-08-19 D-057 + the D-055(e) review record ...
```

The sequence in the file matches the tree. A-078 (`8990255`) is both the reverification and the
commit carrying the corrections — consistent with "corrections were made AFTER the verifiers had
finished".

### P3.3 — Blanket claims are GONE

```
$ python3 flowgrep.py "every repair[^.]{0,60}reverified|no agent work[^.]{0,30}outstanding|INDEPENDENTLY REVERIFIED\b|COMPLETE THROUGH REVERIFICATION" . "*"
```

Every occurrence in `docs/session-state.md` and `HANDOFF.md` is either (a) the phrase **quoted
and immediately labelled false** (l.10-12: "All three were false when written"), (b) struck
(`HANDOFF.md` l.11: `~~"COMPLETE THROUGH REVERIFICATION"~~`), or (c) a correctly-scoped claim
about `R1-F1` alone. l.46 states outright: `"no agent work outstanding" is NOT true`.
**No surviving blanket assertion.**

### P3.4 — DEFECT: a THIRD, uncorrected present-tense "ten accepted"

The commit message claims it corrected "`session-state.md`'s two copies". The diff confirms
exactly two:

```
$ git show HEAD -U2 -- docs/session-state.md | command grep "^[-+].*accepted"
-stated limits plus, as of D-051(b), **§11.0: ten confirmed findings John has ACCEPTED ...
+stated limits plus **§11.0: findings John has ACCEPTED as limits rather than fixed — ten when
+D-051(b) accepted them, and SIX today** ...
-**22 of its 24 rows were wrong**, ... The ten accepted limits were T1-verified:
+**22 of its 24 rows were wrong**, ... The ten limits accepted at that time
+were T1-verified (**six remain accepted today** — see §11.0):
```

A third copy survives, untouched:

```
$ command grep -n "ten accepted" docs/session-state.md
152:adjudicated and remediated: three live security defects fixed, nine MEDIUMs fixed, ten accepted

$ sed -n '151,153p' docs/session-state.md
**WHERE THE PROJECT STANDS, 2026-08-19.** Round five (51 findings, 2 CRITICAL) is fully
adjudicated and remediated: three live security defects fixed, nine MEDIUMs fixed, ten accepted
as documented limits, two design forks with John.

$ git show HEAD -- docs/session-state.md | command grep -c "ten accepted as documented limits"
0                                        # untouched by A-080
$ git log --format="%h %ad" --date=short -S "nine MEDIUMs fixed, ten accepted" -- docs/session-state.md
140c59e 2026-08-18                       # written 2026-08-18, date in the heading bumped to 08-19
```

**Why it survived:** the phrase straddles a line break (`ten accepted` / `as documented
limits`), so a line-based grep for it returns zero. It was found only by the wrap-tolerant
searcher validated at P0.4.

**Why it matters:** the near-identical phrase `"Ten findings accepted as documented limits"` in
`docs/exit-criterion-packet.md` §3 **was** struck to `~~Ten~~ **SIX**` in this same commit. The
author's own standard was applied to the sibling and missed here, under a present-tense heading
dated **2026-08-19**.

### P3.5 — Push status: accurate, dated, and verified against the ref

```
$ git rev-parse origin/step-3/isolated-signer
254db64cbc3e4305ec54de32cec9576fca36c144
$ git log --oneline origin/step-3/isolated-signer..HEAD
c8d15a7 A-080: ...
```

The file says (l.34, l.217): "On 2026-08-19 John pushed the branch to the private remote through
`254db64`", "Everything committed after `254db64` is LOCAL". **Both confirmed against the actual
remote-tracking ref.** Framed as a dated checkpoint fact, and the D-016 distinction
(backup ≠ publication) is stated twice.

### P3.6 — CONTROL: no hard-coded ahead/behind count

```
$ python3 flowgrep.py "\b(ahead|behind)\b[^.]{0,60}|\b\d+ commits?\b" . "*" | grep "^docs/session-state"
l.38  "Never quote an ahead/behind number from this file — it is stale the moment the next
       commit lands; run `git log --oneline origin/step-3/isolated-signer..HEAD`"
l.88  "D-002's two mid-build gates are now both behind the project."   (unrelated sense)
l.747 "a claim ... stronger than the check behind it"                  (unrelated sense)
```

**No numeric ahead/behind anywhere. This requirement is met, and met well** — the file replaces
the number with the command that derives it.

### P3.7 — DEFECT: gate floor constants ARE duplicated, under two claims that they are not

`docs/session-state.md` §3 l.346:

> **The figures are no longer duplicated here.** The gate constants are the only copy, and
> `scripts/check-suite-floors.sh` prints them from the script itself, so this file cannot drift
> from them again.

Six lines later, l.350-351:

> **What is stable and worth stating: 50 corpus fixtures · 7 samples · 78 tamper cases over 30
> modes · workspace guards 0 NEW findings with 13 pre-existing baselined**

Eight lines after **that**, l.358:

> **THE FLOOR VALUES ARE DELIBERATELY NOT REPRINTED HERE.**

Are those three figures gate floor constants? Checked against the scripts, not assumed:

```
$ command grep -n "MIN_" scripts/test.sh
234:FOUNDRY_MIN_TESTS=92
235:TS_MIN_TESTS=527
658:VERIFIER_MIN_TESTS=209
659:VERIFIER_MIN_SAMPLES=7
660:VERIFIER_MIN_TAMPER=78
673:VERIFIER_MIN_TAMPER_MODES=30

$ ./scripts/check-suite-floors.sh
  FOUNDRY_MIN_TESTS          92
  TS_MIN_TESTS               527
  VERIFIER_MIN_TESTS         209
  VERIFIER_MIN_SAMPLES       7
  VERIFIER_MIN_TAMPER        78
  VERIFIER_MIN_TAMPER_MODES  30
suite floors: read from scripts/test.sh, which is the only copy.
```

**`7`, `78` and `30` are three of the six gate floor constants, reprinted verbatim in the file
between two explicit statements that they are not reprinted.** Both statements are false as
written. The file's own header (l.77) says `**DO NOT QUOTE THE SUITE COUNTS IN §3.**` — an
instruction that presupposes §3 contains them, contradicting both.

This is the `R4-F4` defect shape — *one copy removed, another left in the same section, below
the sentence claiming they were no longer duplicated* — recurring in the same section of the
same file that describes it (l.280).

### P3.8 — CONTROL for P3.7: not every restated figure is wrong

The values are currently **accurate** — this is duplication risk, not present staleness. And
the other figures in the same sentence check out:

```
$ ls fixtures/corpus/for-labelling/*.json | wc -l
51
$ ls fixtures/corpus/for-labelling/ | command grep -v "^F[0-9]"
_digests.json                      # 51 files = 50 F-fixtures + 1 digest index
```

**"50 corpus fixtures" is CORRECT.** The control matters: it distinguishes "this sentence is
sloppy" from "these specific three numbers are gate constants the file promised not to
duplicate". Only the latter is the defect. `FOUNDRY_MIN_TESTS` and `TS_MIN_TESTS` are correctly
**not** reprinted — so the repair was partial, exactly as at P3.4.

### P3.9 — CONTROL (the brief's own): a genuinely cold read

A fresh sub-agent with no context, no repository access, and no knowledge of this review was
given **only** `docs/session-state.md` and asked what state the project is in, how verified the
work is, whether agent work remains, what was pushed and when, and to rate how finished the
project feels on a 1-10 scale.

Its conclusions are recorded and compared against the brief's true sequence in `REPORT.md`
under **Item 3 — the control**.
