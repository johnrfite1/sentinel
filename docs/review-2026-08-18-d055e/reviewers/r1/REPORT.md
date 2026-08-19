# REVIEWER 1 — FINDINGS

**Commit reviewed:** `7e0ab7f1057de278c09cc803ab4ca266f53399e1` (detached worktree `w1`)
**Reviewer:** R1 — certification and instruments
**Status:** in progress; findings appended as reproduced.

---

## R1-F1 — CRITICAL — The gate snapshot is not private. A child or sibling can rewrite the running parser in place, reproducing the original incident exactly, INCLUDING exit 0.

### The claim under attack

`scripts/test.sh` lines 30–34 (the shipped bootstrap):

> The mutable file's only job is to copy itself to a snapshot and `exec` into it. From the
> `exec` onward bash is reading **a private file nobody else has a path to**, so **an edit to
> the original cannot corrupt the running parser at all** — the failure mode is removed rather
> than detected.

`scripts/check-gate-immutability.sh` lines 17–22 states the argument it exists to falsify:

> **The running gate never reads the mutable file after the bootstrap, so an edit cannot
> corrupt the running parser AT ALL** [...] The first half — that the corruption is IMPOSSIBLE
> rather than caught — is what makes this different from the design that was rejected.

`docs/decisions.md` A-076(1), a canonical signed-record entry, states it flatly:

> **From the exec onward bash reads a private file nobody has a path to, so an edit cannot
> corrupt the running parser AT ALL; the failure mode is REMOVED, not detected.**

### The claim is false

The snapshot is reachable by two independent routes, and the repository's own text
advertises both:

1. **`SENTINEL_GATE_SNAPSHOT` is exported** (line 82 of `scripts/test.sh`), so **every
   descendant process of the running gate holds a writable absolute path to the file the
   parent's bash parser is reading**. The real gate spawns ~15 `./scripts/check-*.sh` stages
   plus `node`, `npm`, `python3` and `forge`. A-076(1)(b) *records the discovery that this
   variable is exported* — and repaired only the child's own re-exec decision, leaving the
   parent's snapshot exposed to that same child.
2. **The snapshot path is on the process command line.** After `exec bash "$_gate_snap" "$@"`
   the run is `bash /tmp/sentinel-gate.XXXXXXXX --gate`, visible in plain `ps`. The bootstrap's
   own comment (lines 73–81) and `docs/decisions.md` A-076(e) both state this in order to tell
   operators to use `pkill -f sentinel-gate`. The same sentence that documents the operational
   consequence is the disclosure that defeats "nobody else has a path to".

### Reproduction

```
<REVIEW-ROOT>/evidence/r1/probes/probe-snapshot-reachable.sh
```

Full output: `probe-snapshot-reachable.out`.

The probe extracts the **shipped bootstrap verbatim** using the identical `awk` extraction
`check-gate-immutability.sh` uses (104 lines, `SENTINEL_GATE_SNAPSHOT` present — extraction
verified, not assumed), pastes it into a synthetic gate, and uses the **identical in-place
edit shape** the project's own harness uses (`python3 open(path,"w")`, prepend 40 lines,
same inode). It runs under an isolated `TMPDIR` so it cannot touch a live gate.

**Arm A — a child stage, the shape of every `./scripts/check-*.sh` the gate runs:**

```
STAGE 1 ok
  [child] I inherited SENTINEL_GATE_SNAPSHOT=.../tmp/sentinel-gate.iaTGpjsK
  [child] rewrote the running parser's file in place
.../sentinel-gate.iaTGpjsK: line 126: unexpected EOF while looking for matching `"'
--- exit code: 0 ---
source file unchanged? YES
GATE PASSED printed: NO
source-changed diagnostic: NO
```

**Arm B — a sibling that recovers the path from `ps`, using the technique the file itself
documents:**

```
  [sibling] ps says the running parser is reading: .../tmp/sentinel-gate.vbayr8pG
  [sibling] rewrote it in place
STAGE 1 ok
.../sentinel-gate.vbayr8pG: line 109: unexpected EOF while looking for matching `''
--- exit code: 0 ---
source file unchanged? YES
GATE PASSED printed: NO
source-changed diagnostic: NO
```

### What was observed

Both arms reproduce **the original A-075 incident byte for byte**, as `docs/v1-1-register.md`
§13.6 describes it: *"threw a syntax error, never printed `GATE PASSED`, and EXITED 0 — a run
that looks green to anything checking the status and is worthless."*

Worse than before the repair, in one specific respect: **the `_gate_exit` trap actively
certifies the wrong file.** The trap lives in the snapshot and re-hashes `$SENTINEL_GATE_SOURCE`.
The source genuinely did not change, so `_gate_source_unchanged` returns true, `rc` is left at
0, and no `GATE SOURCE CHANGED DURING EXECUTION` diagnostic is emitted. The instrument built to
refuse a zero exit to a compromised run **affirmatively passes it**, because it is watching the
file that is no longer the one being executed.

This is the brief's named failure mode: *a repair that generalises the DEMONSTRATION rather
than the ARGUMENT.* The demonstration was "edit `scripts/test.sh`". The argument is "the body
producing a gate result must be immutable for the whole run". The repair made
`scripts/test.sh` a safe thing to edit and moved the identical hole to a path it then
published in two places.

### Why `check-gate-immutability.sh` reports 5/5 while this holds

All five properties concern edits **to the original**. Property 5 is the closest and it still
misses: it sets `SENTINEL_GATE_SNAPSHOT` to *"some other parent's snapshot"* — a path that
**does not exist** (`$WORK/some-other-parents-snapshot` is never created) — and then asserts
that the subject protects *itself*. It never asserts that a child cannot reach the *parent's
real* snapshot. The harness's own property list has no arm in which the snapshot is the
target of the edit.

### Severity: CRITICAL

The gate is the certification instrument the whole project rests on; both signed gate packs
are gate runs. The falsified property is stated without qualification in a canonical record
(`decisions.md` A-076) and in the guard's header, and the failure mode is the silent one —
exit 0, no diagnostic. A-076's stated residuals (a)–(e) do **not** cover this: (a) scopes the
harness to a synthetic body and to files other than `scripts/test.sh`; (b) covers torn reads
of the source. Neither contemplates the snapshot itself being writable.

**Not a re-report.** Register §13.6 records the *original* defect against `scripts/test.sh`.
This finding is that the repair is incomplete and the record asserts completeness — which
Rule 5 of the common brief makes a finding in its own right ("showing a recorded item is
WORSE than recorded IS one").

### Confidence: HIGH — reproduced twice, by two independent access routes, against the verbatim shipped bootstrap, with the probe's danger established by the project's own control shape.

---

## R1-F2 — HIGH — `check-review-scope.sh` reports "all assigned" after measuring nothing when its base ref does not resolve. Absence reads as agreement.

### The claim under attack

`scripts/check-review-scope.sh` header, lines 11–14:

> So the partition is executable. Every tracked file is matched against the reviewer patterns
> below, and **this exits non-zero if any tracked file is assigned to NO reviewer.** A file
> added between now and dispatch turns this red rather than sliding into a gap. That is the
> difference between a manifest and a claim about one.

Lines 104–108 introduce the second, load-bearing half in the script's own words:

> Stated separately because "every tracked file is assigned" is satisfiable by a partition that
> nobody checked against the actual remediation, **and the remediation is what has not been
> independently reviewed at all.**

### The defect

```bash
since="${SENTINEL_SCOPE_BASE:-a89c255~1}"
...
done < <(git diff --name-only "$since"..HEAD 2>/dev/null)
echo "  remediation surface: $touched file(s) changed since A-070, all assigned"
```

`git diff`'s stderr is **explicitly discarded** and its exit status is **unreachable** (process
substitution). The script runs `set -uo pipefail` — not `set -e`. If `$since` does not resolve,
the loop body never executes, `touched` stays 0, and the script prints a completeness claim and
exits 0.

### Reproduction

```
cd <REVIEW-ROOT>/worktrees/w1
./scripts/check-review-scope.sh                                    # baseline
SENTINEL_SCOPE_BASE=deadbeefdeadbeef ./scripts/check-review-scope.sh
```

Baseline (correct):

```
review scope: R1=175  R2=46  R3=150  (assigned 371 of 371 tracked files)
  remediation surface: 37 file(s) changed since A-070, all assigned
  preservation-only:   15 file(s) (...)
rc=0
```

Unresolvable base:

```
review scope: R1=175  R2=46  R3=150  (assigned 371 of 371 tracked files)
  remediation surface: 0 file(s) changed since A-070, all assigned
rc=0
```

### What was observed

The guard prints **"0 file(s) changed since A-070, all assigned"** and **exits 0**. The number
is false — 37 files changed — and the words "all assigned" are a completeness claim
discharged by zero measurement. The `preservation-only` line vanishes, which is the only
visible tell, and it is a line whose absence a reader has no reason to notice.

This is verbatim the class the common brief names: *"Absence can read as agreement. A check
that emits nothing when a field is missing is worse than no check, because the run still
prints clean."*

**The base is an abbreviated SHA (`a89c255`) hardcoded in the script.** Abbreviated SHAs become
ambiguous as a repository grows, and `git rev-parse` then fails; the ref also fails to resolve
in a shallow clone, in a fresh clone that has not fetched that history, or after any history
rewrite. No contrivance is needed and no warning is printed on any of those paths.

### Severity: HIGH

This guard's entire purpose is to make a completeness claim mechanical rather than asserted —
`docs/d055e-scope-manifest.md` line 9 calls it *"the part that matters"* — and it is the
instrument John required at D-056(d) before dispatch, to ensure the claims surface *"is not
covered merely by assertion"*. In its silent-failure mode it is an assertion again, and one
that now prints a green line to support itself.

### Confidence: HIGH — reproduced directly; baseline captured before the probe; the probe demonstrably moved the output.

---

## R1-F3 — MEDIUM — Nothing invokes `check-review-scope.sh`. Its "turns this red" claim has no mechanism.

### The claim

`scripts/check-review-scope.sh` line 13: *"A file added between now and dispatch **turns this
red** rather than sliding into a gap."*

### Reproduction

```
cd <REVIEW-ROOT>/worktrees/w1
grep -n "check-review-scope" scripts/test.sh .githooks/*      # no match
grep -rn "check-review-scope" . --exclude-dir=lib --exclude-dir=node_modules --exclude-dir=.git
```

Every hit is prose in `docs/d055e-scope-manifest.md`. The script is wired into **no gate stage,
no git hook, and no other script**. `scripts/test.sh` runs `check-gate-immutability.sh`,
`check-secrets.sh`, `check-rename-gate.sh`, `check-label-prompt.sh`, `check-class-coverage.sh`,
`check-vendor-honesty.sh` and others — but not this one.

### What was observed

"Turns this red" describes an automatic behaviour that does not exist. Nothing turns red
because nothing runs. A file added between the manifest's authorship and dispatch slides into
exactly the gap the header says it cannot slide into, unless a human remembers to run the
script by hand.

This is the second time this specific file's header has described a mechanism it lacks; lines
16–21 record the first correction (it had claimed overlap detection). The header was corrected
for the mechanism it *contains*, and the correction did not extend to the mechanism that
*invokes* it.

### Severity: MEDIUM — a completeness guard that is not in the loop is prose with a shebang. Compounds R1-F2: the one instrument standing behind the review's coverage claim both fails silently and is never automatically run.

### Confidence: HIGH — grep is exhaustive over the tracked tree.

---

## R1-F4 — LOW — Register §13.6 still says the gate-corruption protection is "Not built, deliberately", and prescribes the design John rejected.

### Reproduction

```
sed -n '823,838p' docs/v1-1-register.md
grep -n "A-076" docs/v1-1-register.md
```

§13.6 ("A gate run can be silently corrupted by editing the gate script") reads:

> there is a cheap mechanical one: **have the gate hash its own file at start and re-check at
> exit, failing loudly if it changed underneath itself.** Roughly four lines.
>
> **Not built, deliberately:** it is new tooling and outside D-055(d)'s four prerequisites [...]

A-076 built it two days later, and `docs/decisions.md` D-056(b) records that John **rejected on
its merits** precisely the "hash at start, re-check at exit" design §13.6 recommends. The
register's `A-076` FIXED markers were applied to the rows for `D-09`, `D-10`, `G-5`, `H-5` and
`H-8` (lines 773–787) — §13.6 was not updated.

### What was observed

A reader consulting the register — the project's stated list of what is already known — is told
that no protection exists and that the correct remedy is one that was ruled insufficient. Given
R1-F1, the stale text is closer to the truth than the current record is, which is its own kind
of problem.

### Severity: LOW — a stale canonical record, no executable consequence.

### Confidence: HIGH.

---

## R1-F5 — LOW — The deep gate's own coverage boundary tells the reader the run was the default profile and directs them to go run the gate.

### Reproduction

```
cd <REVIEW-ROOT>/worktrees/w1
forge build --root contracts && ./scripts/test.sh --gate     # full output: deep-gate-run.txt
tail -1 deep-gate-run.txt   # (before the harness's own exit-code line)
sed -n '780,795p' scripts/test.sh ; tail -8 scripts/test.sh
```

The `COVERAGE` heredoc (line 790) is guarded only by `if [ "$fail" -ne 0 ]`. It is **not**
guarded on `$PROFILE`. Its closing line is:

> For gate evidence use the deep profile — ./scripts/test.sh --gate — not this default.

### What was observed

My deep run — confirmed as the deep profile by `== solidity build + tests (profile: gate) ==`
at line 134 of `deep-gate-run.txt`, fuzz-weighted Foundry stage, `GATE PASSED` at line 946 —
ends by telling the reader that what they just ran was "this default" and that they should run
`--gate` to obtain gate evidence.

The block is titled "COVERAGE BOUNDARY (house rule 4) — read this, not the pass count", i.e. it
is the part of the output the project instructs people to read instead of the result. Its final
sentence is false on exactly the runs that matter, and it is false in the direction that invites
a reader to discard a valid deep run as a default one.

### Severity: LOW — no executable consequence; a false printed claim in the block the project designates as the authoritative reading of a gate run. R1's brief names printed output and the coverage boundary explicitly ("Every number in it is a claim").

### Confidence: HIGH — observed in my own recorded deep run and confirmed in source.

---

## Severity summary

| id | severity | reproduced |
|---|---|---|
| R1-F1 | **CRITICAL** | yes, two independent access routes |
| R1-F2 | **HIGH** | yes |
| R1-F3 | MEDIUM | yes |
| R1-F4 | LOW | yes |
| R1-F5 | LOW | yes |

No leads. Every item above was reproduced; nothing is reported on suspicion.
