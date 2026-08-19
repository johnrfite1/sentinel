# R4 — FREE LENS — findings

**Commit reviewed: `7e0ab7f1057de278c09cc803ab4ca266f53399e1`**
**Worktree: `<REVIEW-ROOT>/worktrees/w4`**
Reviewer: R4 (free lens, no assigned surface).

Findings are numbered `R4-Fn`. Severity is mine, assigned independently, not softened.
Anything I could not reproduce is labelled **LEAD**, not a finding.

---

## R4-F1 — MEDIUM — The signed S2 pack says five accepted limits remain. Six do. `G-3` has been dropped from the ledger of accepted limits, and this review's own COMMON-BRIEF inherited the error.

### The claim under test

`docs/gate-s2-evidence.md` §11.0 is a **signed** pack section. It exists, in its own words, to
give "the next review round a declared baseline to measure against". Its heading and its
summary paragraphs state the size of that baseline.

- `docs/gate-s2-evidence.md:492` — heading: *"Ten findings ACCEPTED as limits, not fixed
  (D-051(b), 2026-08-18) — **NOW FIVE**"*
- `docs/gate-s2-evidence.md:494-499` — *"A-076 then FIXED five of them outright — `D-09(c)`,
  `D-10`, `G-5`, `H-5`, `H-8` — so what is accepted today is FIVE: `D-07`, `D-09`(a),(b), `E5`,
  `F-VAULT-4`, `F-VAULT-5`."*
- `docs/gate-s2-evidence.md:519-522` — repeats it: *"**What remains accepted here is five**:
  `D-07`, `D-09`(a),(b), `E5`, `F-VAULT-4` and `F-VAULT-5`."*

### What is actually there

The section enumerates **ten** limits, in both its T1 verification table and its per-finding
bullet list. They are: `D-07`, `D-09`, `D-10`, `E5`, `F-VAULT-4`, `F-VAULT-5`, **`G-3`**,
`G-5`, `H-5`, `H-8`.

Five were fixed by A-076: `D-09(c)`, `D-10`, `G-5`, `H-5`, `H-8`. Of those, four are whole
entries and one (`D-09(c)`) is a part of an entry whose (a) and (b) remain accepted.

**Ten entries minus four wholly-removed entries = six still accepted:**
`D-07`, `D-09`(a),(b), `E5`, `F-VAULT-4`, `F-VAULT-5`, **and `G-3`**.

`G-3` is in the T1 table (verified, "HOLDS, and the mechanism is now MEASURED rather than
asserted"), it is in the bullet list (*"Adjudicated CONFIRMED. MEDIUM -> LOW"*), and
`docs/v1-1-register.md:782` independently records it as **`ACCEPTED (D-051(b), §11.0)`**.
It is simply missing from both enumerations of what remains.

### Reproduction

```
cd <REVIEW-ROOT>/worktrees/w4

# 1. The ten entries, from the T1 verification table:
sed -n '492,760p' docs/gate-s2-evidence.md | grep '^| `' | cut -d'|' -f2
#   D-07, D-09 (a),(b), D-10, E5, F-VAULT-4, F-VAULT-5, G-3, G-5, H-5, H-8   (10 rows)

# 2. The five the pack says were fixed:
sed -n '494,499p' docs/gate-s2-evidence.md
#   D-09(c), D-10, G-5, H-5, H-8

# 3. The five the pack says remain:
sed -n '519,522p' docs/gate-s2-evidence.md
#   D-07, D-09(a),(b), E5, F-VAULT-4, F-VAULT-5      <-- G-3 absent

# 4. G-3 is neither fixed nor listed as remaining, yet the register carries it as ACCEPTED:
grep -n 'G-3' docs/v1-1-register.md
#   782: | `G-3` | CONFIRMED | MEDIUM -> LOW | **ACCEPTED (D-051(b), §11.0)** ...
```

### Why this is a finding and not bookkeeping

1. **It is a false claim in signed text.** Exit criterion C1 condition 4 — the criterion John is
   being asked to set in `docs/exit-criterion-packet.md` — is *"zero known false or unsupported
   signed/certified claims."* This is one, and it is now known.
2. **The section reasoned explicitly about this exact hazard and still got it wrong.**
   `gate-s2-evidence.md:496-499` argues the heading must keep its original number *"because 'ten
   accepted limits' is quoted in `docs/exit-criterion-packet.md` §3 and in `docs/session-state.md`,
   and silently restating it as **nine** would leave those citations pointing at a number that no
   longer appears anywhere."* **"Nine" is itself stale** — nine is 10 − 1, the count after A-075
   reopened `D-09(c)` alone, written in a paragraph whose own subject is A-076 having removed five.
   The paragraph that exists to prevent a stale count contains one.
3. **An accepted limit that falls out of the summary stops being measurable.** §11.0's stated
   purpose is to be the declared baseline; COMMON-BRIEF rule 5 tells every reviewer in this round
   that §11.0 "is the five findings John ACCEPTED as limits". A reviewer who re-derives the `G-3`
   mechanism and checks it against the brief's five-item baseline will not find it, and may report
   it as new — or, worse, a future round may treat the `G-3` acceptance as expired because nothing
   in the summary carries it forward.
4. **The error has already propagated out of the pack.** COMMON-BRIEF.md of THIS review round
   says five. `docs/exit-criterion-packet.md:221` says ten. `docs/session-state.md:165,176,205`
   say ten. Three live documents, three different counts, none of them six.

### Confidence

**High.** Purely textual, fully deterministic, verified against three independent locations
(the T1 table, the bullet list, and the register). No mutation required.

### Severity: MEDIUM

Not High: no code behaviour is wrong, and `G-3` itself is a recorded LOW whose mechanism the
register still tracks correctly, so nothing is actually lost from the record as a whole. Not
Low: it is a false count in a **signed** pack, it is the count an exit criterion explicitly
keys on, the pack's own anti-staleness reasoning failed in the same paragraph, and it has
already contaminated the brief governing this round.

### ADDENDUM 1 — the error originates in `decisions.md`, so it is in two canonical records, not one

`docs/decisions.md:243` (A-076) is where the enumeration was first written, under the heading
*"RECORDS UPDATED SO NOTHING FIXED STILL READS AS ACCEPTED"*:

> *"§11.0's heading moves from TEN to FIVE and names what remains (`D-07`, `D-09`(a),(b), `E5`,
> `F-VAULT-4`, `F-VAULT-5`); register §13.4's rows for all five move to FIXED."*

`G-3` is missing there too. The register was updated correctly (`v1-1-register.md:782` still
carries `G-3` as `ACCEPTED`), so the defect is confined to the two prose enumerations — the
decision log and the signed pack — and it propagated from the former to the latter.

### ADDENDUM 2 — `G-3` is not an arbitrary limit to drop. It is the only qualification on a headline exit figure, and I reproduced its mechanism independently.

`docs/exit-criterion-packet.md` §3 lists, among the accepted boundaries that **must not block
exit**:

> | 14 of 20 corpus classes exercise the class they name | ratchet, printed every run |

`G-3` is the recorded finding that qualifies that sentence: two classes are credited only on
`UNRESOLVED` outcomes, so "exercise the class they name" is stronger than what the guard
measures. I reproduced the mechanism from the committed corpus rather than relaying it:

```
python3 - <<'PY'
import json, glob, collections
byclass = collections.defaultdict(list)
for f in sorted(glob.glob("fixtures/corpus/results/F*.json")):
    d = json.load(open(f))
    layer = [L for L in d["layers"] if L["layer"] == "L3_full_conformance"][0]
    outs = set(c["outcome"] for c in layer["checks"] if c["outcome"] != "PASS")
    byclass[d["class"]].append((d["fixtureId"], sorted(outs)))
for cls, rows in sorted(byclass.items()):
    allout = set(o for _, outs in rows for o in outs)
    if allout and allout <= {"UNRESOLVED"}:
        print(cls, "->", [r[0] for r in rows])
PY
#   conflicting-block-state             -> ['F048']
#   runtime-code-change-or-proxy-target -> ['F042', 'F043']
```

50 fixtures, 20 classes. `conflicting-block-state` is already declared a GAP by
`check-class-coverage.sh` and is one of the six carried. **`runtime-code-change-or-proxy-target`
is not carried — it is one of the 14 counted as covered, and its credit comes entirely from
checks that did not resolve.**

So the consequence of dropping `G-3` from §11.0 is specific, not cosmetic: **in the two documents
John reads to set the exit criterion — the packet and the signed pack — the figure "14 of 20
classes exercise the class they name" now appears with no surviving qualification anywhere in
either.** The qualification survives only in the register, which the packet's own §6 lists as a
prerequisite that is **NOT MET**.

I am not re-reporting `G-3`; it is recorded and adjudicated LOW. I am reporting that the record
of its acceptance was dropped from both prose ledgers, and that this is the limit whose loss
costs the most.

---

## R4-F2 — LOW — The round-six preservation README is designated "the authority on which is which" and omits one of its own four sanitizations. `EVIDENCE-MANIFEST.txt` was modified and is not disclosed as modified.

### The claim under test

`docs/d055e-scope-manifest.md` de-scopes the 15 files under `docs/review-2026-08-18-round-six/`
from the remediation surface, on the grounds that they are *"round six's record, faithfully
preserved with disclosed path sanitization"*, and it names the authority and the exhaustive list:

> *"'Verbatim' would overstate it for the set as a whole, and **that directory's README is the
> authority on which is which**. `ADJUDICATED-ROUND-SIX.md` and the nine lens briefs ARE
> byte-identical; **`COMMON-BRIEF.md` and the two reviewer indexes** had machine-specific paths
> replaced, **each disclosed there**."*

That enumerates **three** modified files. The README's own fidelity table lists
`EVIDENCE-MANIFEST.txt` with the description *"relative paths + SHA-256 for all 971 preserved
files"* — no modification disclosed, in a table whose other rows disclose modifications
explicitly ("one line sanitized: an absolute repository path became `<REPO>`. Nothing else
changed").

### What is actually there

`EVIDENCE-MANIFEST.txt` is the fourth sanitized file. Its final line was rewritten with exactly
the same `<REPO>` substitution the README discloses for `COMMON-BRIEF.md`:

```
archive : symlink  ./round6/evidence/lens3/node_modules -> <REPO>/ts/node_modules
repo    : symlink  ./round6/evidence/lens3/node_modules -> <REPO>/ts/node_modules
```

It also gained a 4-line descriptive header. Neither change is disclosed in the fidelity table,
and the row's description "relative paths" is inaccurate for that line in the source manifest.

### Reproduction

```
A=<HOME>/Projects/_archive/sentinel-round-six-2026-08-18
R=<REVIEW-ROOT>/worktrees/w4/docs/review-2026-08-18-round-six

diff "$A/MANIFEST-sha256.txt" "$R/EVIDENCE-MANIFEST.txt"
# 0a1,4   > (4 header lines)
# 972c976 < ... -> <REPO>/ts/node_modules
#         > ... -> <REPO>/ts/node_modules

# and the README does not mention it:
grep -n 'EVIDENCE-MANIFEST' "$R/README.md"
# | `EVIDENCE-MANIFEST.txt` | relative paths + SHA-256 for all 971 preserved files |
```

### Why this is a finding

The integrity is fine — I verified it (see NULL-RESULTS.md: 971/971 hashes match, all
byte-identity claims hold). What is defective is the **disclosure**, in the one document
another document designates as the authority on disclosure, about a directory that was
**de-scoped from review on the strength of that disclosure being complete**. The scope
manifest's argument for excluding these 15 files from scrutiny is that their fidelity is
already stated; the statement is incomplete, so the exclusion rests on slightly more than was
established.

### Confidence

**High.** Deterministic `diff` against the source archive.

### Severity: LOW

Not Medium: no hash changed, no content was lost, the substitution is the project's own
disclosed convention applied consistently, and nothing downstream is misled about the
evidence itself. Not Info: it is a false statement of completeness in a document explicitly
nominated as the authority for that exact question, and it is the basis on which 15 files were
excluded from review.

### Note carried with it, not a separate finding

The README's provenance table gives `Raw manifest | sha256 51894dd4…`. That is the hash of the
**archive's** `MANIFEST-sha256.txt` (verified correct), not of the committed
`EVIDENCE-MANIFEST.txt`, which hashes to `234503ed…`. The row is labelled "Raw manifest" so it
is not wrong, but a reader verifying the committed file against the documented hash will get a
mismatch and has nothing in the directory telling them why.

---

## R4-F3 — MEDIUM — Two gate guards certify a *section* of the proposal while checking the *whole 84KB document*. `check-type-strings.sh` can print "6/6 published in §5.8 match eip712.ts exactly" while §5.8 publishes a transposed type string.

### The claim under test

Two of the nine gate guards assert that something in the code is documented in a **named
section** of `Sentinel_Protocol_Lab_Proposal_v0_2.md`, and both print that section number in
their certification line:

- `scripts/check-eval-codes.sh` — header: *"every check the conformance engine declares must
  appear in **§5.7.1** of the proposal"*; prints `eval codes: 41/41 engine checks documented in
  §5.7.1 (D-031)`.
- `scripts/check-type-strings.sh` — header: *"**§5.8** of the proposal publishes the EIP-712
  type strings verbatim. This checks that what the spec publishes is byte-identical to what the
  signer actually hashes."*; prints `type strings: 6/6 published in §5.8 match eip712.ts exactly
  (D-023)`.

### What they actually do

Neither locates a section. Both grep the entire file.

```
# check-eval-codes.sh
grep -q "$code" "$SPEC" || missing="$missing $code"

# check-type-strings.sh
spec_line="$(grep -oE "^ {4}${name}\([^)]*\)$" "$SPEC" | head -1 | sed 's/^ *//')"
```

`$SPEC` is the whole 1,080-line proposal. The section number appears only in the prose and in
the printed output.

### Reproduction — baseline

```
cd <REVIEW-ROOT>/worktrees/w4
./scripts/check-eval-codes.sh    # eval codes: 41/41 engine checks documented in §5.7.1 (D-031)   exit 0
./scripts/check-type-strings.sh  # type strings: 6/6 published in §5.8 match eip712.ts exactly     exit 0
```

§5.7.1 is lines 571–606 (next heading `## 6. AI and Context Scope` at 607). §5.8 is lines
486–521. All 41 codes and all 6 type strings are genuinely in their sections **today** — the
claims are true, and I verified that separately (NULL-RESULTS N6). What follows is that nothing
keeps them true.

### Demonstration 1 — a check documented nowhere in §5.7.1, certified as documented in §5.7.1

Applied to `Sentinel_Protocol_Lab_Proposal_v0_2.md`: removed the only §5.7.1 mention of
`EVAL_MANDATE_PRINCIPAL_IS_OWNER` and added a passing mention inside `## 6. AI and Context
Scope`, a section the proposal itself scopes to AI, not to checks.

```
# probe MOVED something — verified before believing the silence:
sed -n '571,606p' Sentinel_Protocol_Lab_Proposal_v0_2.md | grep -c EVAL_MANDATE_PRINCIPAL_IS_OWNER
#   0        (was 1)

./scripts/check-eval-codes.sh
#   eval codes: 41/41 engine checks documented in §5.7.1 (D-031)
#   exit=0
```

**The guard certifies §5.7.1 coverage for a check that §5.7.1 does not mention.**

### Demonstration 2 — the sharp one: §5.8 publishes a WRONG type string and the guard says it matches

`check-type-strings.sh` takes `head -1` of a whole-file grep. Section order in this file is
**not** monotonic — §5.9 is at line 468, *before* §5.8 at line 486 — so an earlier occurrence
anywhere in the document wins over the one §5.8 actually publishes.

Applied: transposed `string name` and `string version` in the `EIP712Domain` line that §5.8
publishes (line 498), and placed a correct copy earlier, inside §5.9 (line 470).

```
grep -n '^    EIP712Domain(' Sentinel_Protocol_Lab_Proposal_v0_2.md
#   470:    EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)   <- §5.9, correct
#   498:    EIP712Domain(string version,string name,uint256 chainId,address verifyingContract)   <- §5.8, WRONG

./scripts/check-type-strings.sh
#   type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)
#   exit=0
```

**This is the exact scenario the guard's own header says is worse than having no guard:**

> *"A PUBLISHED type string that has drifted from the code is worse than an absent one: it is a
> confident, wrong answer that an implementer has no way to detect, because a wrong type string
> and an invalid signature are indistinguishable at the output."*

A transposed `EIP712Domain` yields a different typehash, so every signature an independent
implementer produces from §5.8 would fail to recover — and §5.8 exists precisely because an
independent reimplementation established §5 was not buildable without it. That is the D-010
premise. The guard is the only mechanical thing standing behind it, and it passes.

### Revert

Restored from a pristine copy taken before any mutation and verified with `cmp`, not with git:

```
cmp Sentinel_Protocol_Lab_Proposal_v0_2.md "$PRIS/Sentinel_Protocol_Lab_Proposal_v0_2.md"   # clean
git diff HEAD --stat -- .    # only the two provisioned submodule symlink entries
```

### Confidence

**High.** Both demonstrations run in seconds, are deterministic, and each was confirmed to have
moved the input before its result was believed.

### Severity: MEDIUM

Not High: the defect is in the instrument, not in the artifact — §5.7.1 and §5.8 are correct at
`7e0ab7f`, so nothing is currently mis-published, and the type strings additionally agree across
all four implementations that carry them (N6). Not Low: this is a guard that **passes while the
property it names is violated**, in a repository whose recorded history contains "the secret
guard passed a real private key" as a HIGH; it protects the published schema that D-010's whole
independent-implementer argument depends on; and both guards' printed lines are certifications
that a reader — and `docs/gate-s2-evidence.md` — takes as section-scoped evidence.

**If an adjudicator wants to move this, the argument for High is that the guard's failure mode
is silent and the artifact it protects is load-bearing for a signed gate; the argument for Low
is that no current artifact is wrong. I judged the midpoint correct.**

### Two smaller observations from the same reading, recorded here rather than as findings

- `check-eval-codes.sh` prints `${total}/${total}` — numerator and denominator are the same
  variable, so the ratio is an identity and can never print anything but `N/N`. It reads as a
  measurement of coverage and is a count of the loop.
- `check-type-strings.sh`'s `[^)]*` and `[^\"]*` character classes would silently fail to match
  any future type string containing `)` or `"`. Not reachable with the current six.

---

## R4-F4 — MEDIUM — `session-state.md` §3, the line every session is told to start from, is stale for the FIFTH time. It publishes 507/198 where the tree measures 513/209, and it misquotes a gate floor constant in the direction the repository forbids.

### The claim under test

`docs/session-state.md:353` — §3 "Where the build is", the headline status line:

> **75/75 Foundry · 507/507 TypeScript · 198/198 verifier · 78 tamper cases over 30 modes ·
> 50 corpus fixtures · 7 samples · gate green …**

and `:359`:

> **AND AS OF A-075 THE FOUNDRY AND TYPESCRIPT FIGURES ARE FLOORS THIS GATE ASSERTS** —
> `FOUNDRY_MIN_TESTS=75`, **`TS_MIN_TESTS=507`**

The same section carries its own warning in bold: ***"VERIFY BEFORE QUOTING — this line has been
wrong four times."*** It is now wrong a fifth time.

### Measured at `7e0ab7f`

| Figure | §3 says | I measured | |
|---|---|---|---|
| Foundry | 75/75 | **75**, 75 passed | ✅ |
| TypeScript | 507/507 | **513**, 513 passed, 0 skipped, 0 todo | ❌ |
| verifier | 198/198 | **209** | ❌ |
| tamper | 78 cases / 30 modes | **78** cases | ✅ |
| corpus fixtures | 50 | **50** | ✅ |
| samples | 7 | **7/7 verified** | ✅ |
| `TS_MIN_TESTS` | `507` | `scripts/test.sh:188` = **`513`** | ❌ |
| `VERIFIER_MIN_TESTS` | (198 implied) | `scripts/test.sh:611` = **`209`** | ❌ |

### Reproduction

```
cd <REVIEW-ROOT>/worktrees/w4

# TypeScript
cd ts && SENTINEL_TEST_REPORTERS="--test-reporter=tap --test-reporter-destination=/tmp/r4-ts.tap" npm test
grep -E '^# (tests|pass|fail|skipped|todo)' /tmp/r4-ts.tap
#   # tests 513 / # pass 513 / # fail 0 / # skipped 0 / # todo 0

# Foundry
cd contracts && forge test --json > /tmp/r4-forge.json      # 75 tests, 75 passed

# Verifier
cd verifier && python3 test_verifier.py                      # Ran 209 tests ... OK
python3 verifier/verify.py --domain fixtures/samples/domain.json --all fixtures/samples
#   7/7 sample(s) verified

# The gate's own constants
grep -n '^TS_MIN_TESTS=\|^VERIFIER_MIN_TESTS=' scripts/test.sh
#   188:TS_MIN_TESTS=513
#   611:VERIFIER_MIN_TESTS=209

# What §3 publishes
sed -n '353,360p' docs/session-state.md
```

### It is not recorded, and the correct numbers exist one file away

`docs/decisions.md:243` (A-076) records the true figures: *"Suite 75 Foundry / **513** TypeScript
/ **209** verifier; every floor ratcheted in the same edit as its suite."* A-076 also enumerates
which records it updated — §11.0's heading and register §13.4 — and **`session-state.md` §3 is
not among them.** The drift is exactly the A-076 delta (+6 TypeScript, +11 verifier) and nothing
carried it across.

Nor is the staleness disclosed as a known limit. `docs/exit-criterion-packet.md` §3b lists
*"Register §13 status column stale for ~17 of 24 rows"* as an unresolved item and **does not list
`session-state.md` §3**; §6's prerequisite table lists *"Register §13 status column accurate —
NOT MET"* and again does not mention §3. `docs/d055e-scope-manifest.md` names §3 only in the past
tense, as one of three tables that *have* gone stale historically. **This instance is new and
undisclosed.**

### Why it is MEDIUM and not LOW

1. **It misquotes a gate floor in the forbidden direction.** `scripts/test.sh` carries, in three
   separate places, the rule *"RAISE A FLOOR IN THE SAME EDIT AS THE SUITE IT BOUNDS. **NEVER
   LOWER ONE TO MAKE A RUN PASS.**"* §3 publishes `TS_MIN_TESTS=507` as the current constant. A
   maintainer reconciling `test.sh` against the document this project designates as its memory
   would lower the floor by six and silently open exactly the six-test hole A-076 closed.
2. **It is the designated entry point.** The standing instruction for this project is to start
   every session at `docs/session-state.md` §1; §3 is the status any new agent or reviewer reads
   first, and the exit-criterion packet's whole method is comparing measured state to recorded
   state.
3. **Its own text nominates it as the risk.** The line says it has been wrong four times, is
   labelled *"in the file that opens by declaring itself the memory"*, and asserts *"All four
   counts above were re-measured 2026-08-16 (late session) and all four held"* — a re-measurement
   claim that is true of 2026-08-16 and false of the reviewed commit. **This is verbatim the
   project's own named defect: a published number that was true once.**

Not High: no code behaviour is affected, the gate itself carries the correct floors and would
still catch a shrinking suite, and the accurate figures are recorded in `decisions.md`.

### Confidence

**High.** Every figure independently measured by running the suites at `7e0ab7f`, not by reading
another document.

