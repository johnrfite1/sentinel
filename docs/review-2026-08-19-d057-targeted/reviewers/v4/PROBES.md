# V4 — probe transcript

Every probe below ran inside the V4 worktree at `c8d15a76425544148d7da2f8fa0c003feb6ad2b7`.
Paths are repository-relative. Every mutation was reverted with `git checkout --` and the tree
returned to `?? ts/node_modules` only, verified with `git status --porcelain` after each.

Convention used throughout, from the COMMON BRIEF: **a probe reports what it MOVED before what
its result implies.** Where a probe moved nothing it is marked DEAD and discarded.

---

## P0 — INSTRUMENT VALIDATION (run first; nothing below is trusted without it)

### P0.1 — `grep` on this machine is a ugrep wrapper with `--ignore-files`

```
type grep
# -> shell function, execs `claude` as ARGV0=ugrep with:
#      -G --ignore-files --hidden -I --exclude-dir=.git ...
```

### P0.2 — Planted canaries in six file types (tracked paths)

Appended `CANARY_V4_SWEEP_PROOF` to `contracts/src/SentinelVault.sol` (NatSpec position),
`verifier/verify.py`, `ts/src/evaluate/checks.ts`, `docs/v1-1-register.md`,
`Sentinel_Protocol_Lab_Proposal_v0_2.md`, and a new `scripts/*.CANARYCOPY`.

- BSD `/usr/bin/grep -rnE` — **6/6 found**.
- shell `grep` wrapper — **6/6 found**.

Both instruments see tracked files. That alone is not enough.

### P0.3 — THE DIVERGENCE THAT MATTERS (this is the control that decided the method)

Planted `CANARY_V4_SWEEP_PROOF2` in `contracts/out/canary.txt` and `.env.canary` — both
gitignore-matched (`contracts/out/`, `.env.*`).

```
shell grep wrapper : exit 1, NO OUTPUT          <- reads exactly like a clean sweep
/usr/bin/grep      : 2 files, both found
```

**A zero result from the shell `grep` wrapper is not evidence of absence in this repository.**
All sweeps in `REPORT.md` therefore use `/usr/bin/grep -rnE --binary-files=without-match
--exclude-dir=.git --exclude-dir=node_modules`.

### P0.4 — Hard-wrap tolerance

The repository hard-wraps prose, so phrase searches were re-run over a newline-joined copy of
every readable file. Identifier searches use **two** joins:

- space-join (`\n[ \t>#*`-]*` to a space) — reassembles wrapped **phrases**;
- empty-join (same pattern to nothing) — reassembles an identifier wrapped **mid-token**.

Proof this mattered: see P3.4 — a deliberately wrapped `EVAL_VAULT_` + newline +
`SELECTOR_MISSPELLED` was **missed** by the space-join and **caught** by the empty-join.

---

## P1 — `R2-F4`: is the claim actually false at this commit?

### P1.1 — The packet's own stated test, verbatim

```
grep -c decodedSelectorAndParameters verifier/verify.py       ->  2
```

`docs/exit-criterion-packet.md` §7 blocker 1 and §3b both state this equals **0**.

### P1.2 — CONTROL: does that measurement move? (guards against a dead grep)

```
git show 9347c9d:verifier/verify.py | grep -c decodedSelectorAndParameters  ->  0
git show caad4c1:verifier/verify.py | grep -c decodedSelectorAndParameters  ->  2
```

`9347c9d` = the commit that wrote §7's blocker. `caad4c1` = `A-074`, which built the
comparison. **The instrument moves, and it moves at exactly the commit the record says it
should.** The claim was true when written and false from `A-074` onward.

### P1.3 — Behavioural falsification: mutate the comparison away

A count is a weak instrument. Mutation applied to `verifier/verify.py:1348`:

```
def _allow_conforms_to_the_mandate(evidence, mandate, policy):
+   return []  # MUTATION: comparison removed (probe)
```

Probe moved: exactly 1 line inserted, asserted before running.

```
BEFORE : python3 -B -m unittest test_verifier.TestAllowConformsToTheMandate  -> Ran 9, OK
AFTER  : same command                                                        -> Ran 9, FAILED (failures=8)
```

The one survivor is `test_a_NONCONFORMING_BLOCK_BUNDLE_STILL_VERIFIES` — the control that is
*supposed* to pass in both states. A control that failed pre-mutation would be the wrong
control. Reverted; re-ran clean: **Ran 9, OK**.

**Establishes:** the conformance comparison exists, is reached on the verification path, and is
what refuses. The `§7` claim is false about a live mechanism, not about a dead one.

### P1.4 — The signer half

`ts/src/signer/attest.ts:638` — `checkEvidenceDecoding` reads
`.decodedSelectorAndParameters` from the canonical evidence and compares it to its own
`decodeBySelector` result. So *"checked by neither the signer nor the verifier"* is false on
both halves.

### P1.5 — The `description` sub-field IS still uncompared (this is the CONTROL claim)

```
grep -nE '\bdescription\b' ts/src/signer/attest.ts   -> no matches
grep -nE '\bdescription\b' verifier/verify.py        -> :2261 only, an argparse keyword
```

So the narrowed claim is TRUE and every site stating it that way is correctly left alone.

---

## P2 — `R2-F4`: the site enumeration

### P2.1 — Spellings searched (meaning, not wording)

Each run through `/usr/bin/grep` and again through the join-sweep:

```
compared to nothing | compared against nothing | compared by nothing
checked by neither  | nothing (checks|compares) | no conformance comparison
does not perform    | is not compared          | uncompared
conformance comparison | grep -c decodedSelectorAndParameters
does the conformance comparison | known false claim | false claim in signed
signed Gate S1 pack contains
```

Also swept, per the `A-063` precedent that a fifth site hid in a contract's own NatSpec:
`contracts/src/`, `contracts/test/`, `scripts/`, `verifier/*.py` docstrings, `ts/src/`,
`HANDOFF.md`, `README.md`, `Sentinel_Protocol_Lab_Proposal_v0_2.md`,
`docs/ablation-report.md`, `docs/gate-5-vendor-audit.md`, `docs/d055e-scope-manifest.md`,
`docs/round-six-brief.md`, `docs/session-state.md`, `docs/gate-s2-evidence.md`.

Result outside `docs/`: `scripts/test.sh:653` (accurate), `ts/src/decode/index.ts` (see R-5),
`contracts/**` (nothing — one unrelated hit on the word "description" in a test NatSpec).

### P2.2 — PRE-FIX COMPARISON: what the repair actually touched

```
git show 8990255 --format="" -U0 -- docs/exit-criterion-packet.md | grep '^@@'
#   @@ -103 +103 @@                      <- ONE line

git show 8990255 --format="" -U0 -- docs/decisions.md | grep '^@@'
#   @@ -245 +245,2 @@                    <- A-077's entry only; A-070 (:225) and A-074 (:239) untouched

git show 8990255 --format="" -U0 -- docs/v1-1-register.md | grep '^@@'
#   @@ -909,5 +909,11 @@                 <- §14's bullet
```

### P2.3 — When were the two uncorrected sites last written?

```
git log --oneline -L 212,212:docs/exit-criterion-packet.md
#   9347c9d  Prepare (not decide) the D-047 replacement packet     <- PREDATES A-074 (caad4c1)

git log --oneline -L 225,225:docs/decisions.md
#   a89c255  A-070: the first remediation under the D-052(b) repair protocol
```

**Neither line has been touched since it was written.** Both predate or coincide with the
statement they carry, and no repair has revisited either.

### P2.4 — DEAD PROBE, recorded

`python3 joinsweep.py 'filed where the reader is not'` and `'falsehood standing'` both returned
**0 matches**. That is not evidence about the repository — the phrases live in `8990255`'s
**commit message**, which is not a tracked file. Recorded so the zero is not mistaken for a
finding. The commit message was read with `git show 8990255` instead.

---

## P3 — `R3-F4`: code names

### P3.1 — Derive the real names from code

```
/usr/bin/grep -rhoE 'SIGNER_[A-Z0-9_]+' ts/src | sort -u    -> 38 codes, incl.
    SIGNER_VAULT_TARGET_NOT_ALLOWED
    SIGNER_VAULT_SELECTOR_NOT_ALLOWED
```

Definition and emission:

```
ts/src/signer/protocol.ts:248  SIGNER_VAULT_TARGET_NOT_ALLOWED:   "CONFORMANCE",
ts/src/signer/protocol.ts:250  SIGNER_VAULT_SELECTOR_NOT_ALLOWED: "CONFORMANCE",
ts/src/signer/attest.ts:523    if (!state.targetAllowed)   findings.push("SIGNER_VAULT_TARGET_NOT_ALLOWED");
ts/src/signer/attest.ts:524    if (!state.selectorAllowed) findings.push("SIGNER_VAULT_SELECTOR_NOT_ALLOWED");
```

Independent corroboration (not the source file): a committed receipt at
`fixtures/samples/case-2-injection-block/receipt.json:30,37`; the pinning test at
`ts/test/reasoncodes.test.ts:141-142`; the mutation site at `scripts/mutate.sh:326-327`.

### P3.2 — Whole-tree sweep for the fabrication

```
/usr/bin/grep -rhoE 'EVAL_VAULT_[A-Z0-9_]+' --exclude-dir=.git --exclude-dir=node_modules . | sort -u
    EVAL_VAULT_BOUND                     <- REAL   (ts/src/evaluate/checks.ts:100,229)
    EVAL_VAULT_NOT_PAUSED                <- REAL   (ts/src/evaluate/checks.ts:101,127,221)
    EVAL_VAULT_SELECTOR_NOT_ALLOWED      <- FICTITIOUS
    EVAL_VAULT_TARGET_NOT_ALLOWED        <- FICTITIOUS
```

Full occurrence list of the two fictitious names, whole tree:

```
docs/decisions.md:246   (A-078's "A FALSE CODE NAME I INVENTED" paragraph)   <- and nowhere else
```

Join-sweep for wrapped variants: no additional hits.

### P3.3 — Diff A: codebase-defined vs. maintained-doc-cited

Script: walk the tree; `CODEBASE` = every file not under `docs/` and not `.md`;
`MAINTAINED DOCS` = top-level `docs/*.md` (excluding `docs/review-*`), `HANDOFF.md`,
`README.md`, the proposal, `verifier/REPORT.md`, `fixtures/corpus/LABELLING_PROMPT.md`.
Doc text is space-joined AND empty-joined before tokenising.

```
CODEBASE defines 105 distinct codes
MAINTAINED DOCS name 55 distinct codes

CITED BUT NOT DEFINED ANYWHERE IN THE CODEBASE: 3
  EVAL_VAULT_                     cited in: docs/session-state.md
  EVAL_VAULT_SELECTOR_NOT_ALLOWED cited in: docs/decisions.md
  EVAL_VAULT_TARGET_NOT_ALLOWED   cited in: docs/decisions.md
```

All three accounted for as historical (see `REPORT.md` §2.4).

### P3.4 — CONTROL: would Diff A have caught the original?

Injected into `docs/exit-criterion-packet.md`:

```
`EVAL_VAULT_TARGET_NOT_ALLOWED`, `EVAL_VAULT_SELECTOR_NOT_ALLOWED`,
a mid-token wrapped `EVAL_VAULT_\nSELECTOR_MISSPELLED`, and a real `SIGNER_VAULT_TARGET_NOT_ALLOWED`.
```

```
Diff A, space-join only : catches both plain fabrications; MISSES the wrapped one
Diff A, + empty-join    : catches all three, incl. EVAL_VAULT_SELECTOR_MISSPELLED
Real code SIGNER_VAULT_TARGET_NOT_ALLOWED : NOT flagged (correct)
```

Reverted with `git checkout --`; clean re-run returns to 3 orphans.

**This is why the empty-join exists.** A wrapped identifier is exactly the shape that produces
a zero result reading like a clean sweep.

### P3.5 — Diff B: closing the self-vouching loophole

Diff A treats the whole non-`docs/` tree as "defined", so a fabricated name invented **in a code
comment** would vouch for itself. Diff B strips comments (`//`, `///`, `/* */`, `#`, `"""`)
from `.ts/.py/.sol/.sh/.mjs/.json` product files before building the defined set.

```
DEFINED-FOR-REAL (non-comment, product tree): 102
NAMED ANYWHERE (docs, comments, NatSpec, docstrings): 109

NAMED BUT NEVER DEFINED IN NON-COMMENT PRODUCT CODE: 7
  EVAL_ACTION_TARGET_MATCHES_MANDATE   ts/test/evaluate.checks.test.ts        <- NEW, see R-4
  EVAL_ALLOWANCE_EFFECT                docs/review-2026-08-17/lens-D...json   <- historical, truncated glob
  EVAL_PURCHASE_                       docs/review-2026-08-17/lens-G...json   <- historical, truncated glob
  EVAL_VAULT_                          docs/session-state.md                  <- labelled "fabricated"
  EVAL_VAULT_SELECTOR_NOT_ALLOWED      docs/decisions.md                      <- A-078's confession
  EVAL_VAULT_TARGET_NOT_ALLOWED        docs/decisions.md                      <- A-078's confession
  SIGNER_OWNER_APPROVED_OUT_OF_BAND    docs/review-2026-08-17/lens-H...json   <- historical: a reviewer's
                                                                                 DELIBERATELY forged payload
```

Each historical hit was read in context before classifying; the contexts are quoted in
`COVERAGE.md`.

### P3.6 — CONTROL: would Diff B have caught the original in the CODE COMMENT?

Reintroduced the fabrication into `ts/src/signer/protocol.ts:370`, the exact comment it was
removed from:

```
Diff B ->  EVAL_VAULT_SELECTOR_NOT_ALLOWED  named in: docs/decisions.md, ts/src/signer/protocol.ts
```

Caught. Reverted.

---

## P4 — Is this class mechanically guarded? (probe + control)

### P4.1 — The repository's own guard, clean

```
bash scripts/check-eval-codes.sh
#   eval codes: 41/41 engine checks documented in §5.7.1 (D-031)
#   EXIT=0
```

### P4.2 — PROBE: inject a fictitious code into the S2 evidence pack

Appended to `docs/gate-s2-evidence.md`:
``Enforcement surfaces as `EVAL_VAULT_TARGET_NOT_ALLOWED` (fabricated probe).``

```
bash scripts/check-eval-codes.sh   ->  41/41 ... EXIT=0     <- BLIND
python3 codediff.py                ->  flags it against docs/gate-s2-evidence.md
```

Same result with the fabrication reintroduced into `ts/src/signer/protocol.ts` (P3.6).

### P4.3 — CONTROL: is `check-eval-codes.sh` alive, or is P4.2 a dead probe?

Renamed one REAL code inside proposal §5.7.1
(`EVAL_VAULT_NOT_PAUSED` -> `EVAL_ZZZ_MUTATED_CONTROL`, 1 replacement, asserted applied):

```
bash scripts/check-eval-codes.sh
#   eval codes: 1 check(s) declared by the engine and absent from §5.7.1:
#       EVAL_VAULT_NOT_PAUSED
#   EXIT=1
```

**The guard is alive.** Its exit 0 in P4.2 is a genuine blind spot in the doc-to-code
direction, not a dead probe. Reverted.

---

## P5 — Tree hygiene

After every probe: `git checkout -- <file>` then `git status --porcelain`, which returned
`?? ts/node_modules` and nothing else. Final state verified the same way. `scripts/test.sh` was
never edited. No gate run was in flight at any point. The primary tree was read for the briefs
and never written outside this reviewer directory.
