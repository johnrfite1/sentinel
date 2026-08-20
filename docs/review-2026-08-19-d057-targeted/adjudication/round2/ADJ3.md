# ADJ3 — adjudication of three sibling-enumeration candidates: `C1`, `C2`, `C3`

**Authority:** D-058(7) — *"Adjudicate each new item first and classify it as confirmed, refuted,
duplicate, historical, or a decision fork."* — under John's ruling that *"a sibling enumeration may
identify candidates, but it does not itself adjudicate them."* None of the three below may enter a
repair batch on the strength of the enumeration that surfaced it.

**Adjudicator:** independent. I reported none of these candidates, authored none of the code, prose
or guards under examination, and did not draft the repair contract.

**Frozen commit:** `a18e6e61598a996d962798ad0353a166232d4490`, confirmed by `git rev-parse HEAD`
in my worktree before the first probe and again after the last. **Worktree restored:**
`git diff HEAD --stat` is empty and `git status --porcelain` shows only the untracked
`ts/node_modules`. All three guards re-run green after restoration. `git checkout` was used once,
on a canary line I appended myself, before any probe.

**Instrument hygiene.** Every sweep used `/usr/bin/grep`. Before trusting any zero result I
appended `CANARY_ADJ3_7c4b1e_DO_NOT_KEEP` to `docs/session-state.md`, confirmed `/usr/bin/grep -rn`
found it, and reverted. Every probe that writes a file through Python carries an `assert` on the
line it expects to find and prints `WROTE-OK`; **this caught V3's trap (ii) live** — my first C2
attempt died on a bad index *before writing*, and the guard would otherwise have run against an
unmodified document and printed a meaningless `6/6`. Scratch paths are written `<SCRATCH>`.

**Standing evidence bound.** Foundry submodules are not provisioned in this worktree and the
Solidity artifacts are not built, so I did not run `scripts/test.sh` end to end or `forge test`.
I confined myself to surfaces that need neither: the shell guards, `ts/test/evaluate.checks.test.ts`
under `node --test`, and static reading of `ts/src`. Where that bounds a conclusion I say so at the
point it bites.

## Summary

| Candidate | Reporter's rating | Classification | My severity |
|---|---|---|---|
| `C1` — `check-eval-codes.sh` unanchored membership test | LOW, "latent" (V3) | **CONFIRMED** — instrument defect, **DISTINCT** from `R4-F3` | **MEDIUM** (up from LOW) |
| `C2` — §5.8 deeper-subheading truncation (V3's `T7`) | filed, unrated (V3 `F6`) | **CONFIRMED** — **DISTINCT** from `R4-F3` | **MEDIUM** |
| `C3` — `check-suite-floors.sh` duplicate handling | probe, unrated | **CONFIRMED** — **DISTINCT** from `R4-F4` | **MEDIUM** |

All three are **instrument defects**: each needs an edit to the repository to produce a false
statement, and none of them is a false claim about the tree as it stands. That is the same standing
the project already gives `R4-F3`, whose ledger row reads `CONFIRMED` while its own guard header
says *"NOT CURRENTLY LIVE"*. I have not lowered any of them on that ground, and I say for each one
exactly what the edit is and how ordinary it is.

---

# C1 — `scripts/check-eval-codes.sh:52`, the unanchored membership test

## 1.1 The exact claim at issue

That the guard prints *"eval codes: 41/41 engine checks documented in §5.7.1 (D-031)"* on the
strength of `grep -q "$code" "$SPEC_SECTION"` — an **unanchored substring** test — so a code that
is a strict prefix of some other token already present in §5.7.1 is certified as documented when
§5.7.1 does not document it. V3 filed this as latent, on the ground that there are **0 prefix
pairs** among the 41 codes.

## 1.2 The authoritative source

`scripts/check-eval-codes.sh` itself, line 52, and the string it prints at line 63. The set of
codes is settled by `ts/src/evaluate/checks.ts`'s own `EVAL_CODES` array — the guard reads it at
lines 40-41 and nothing else declares the engine's surface. Code beats prose; the array beats §5.7.1
and beats the guard's printed claim.

## 1.3 The current code set, derived rather than read

```
sed -n '/^export const EVAL_CODES = \[/,/^\] as const;/p' ts/src/evaluate/checks.ts \
  | /usr/bin/grep -oE '"EVAL_[A-Z0-9_]+"' | tr -d '"' | sort -u          ->  41 codes, 41 unique
```

Computed over that set in Python:

- **strict-prefix pairs: 0**
- **substring pairs (a proper substring of b, not merely a prefix): 0**

**V3's count is correct and I strengthen it:** the guard is not merely free of prefix collisions
today, it is free of substring collisions of any kind.

I also verified that the guard's present output is **true**, which the prefix count alone does not
establish. For each of the 41 codes, in the awk-extracted §5.7.1 (35 lines):

```
/usr/bin/grep -cE "\bCODE\b"        -> >= 1 for all 41
/usr/bin/grep -cE "CODE[A-Z0-9_]"   ->    0 for all 41
```

So every code appears with a word boundary and none appears *only* as a fragment of a longer token.
**The `41/41` printed at this commit is a true sentence.**

## 1.4 Reproduction — and the reporter's framing of the latency is wrong

V3's probe added a fictitious 42nd code. That is the weaker version. The exposure is **not** a
property of the code set; it is a property of a single edit. I reproduced four ways.

### C1-a — the shape V3 described (add a 42nd code that is a prefix)

Inserting `"EVAL_ACTION_DEAD"` into `EVAL_CODES` beside the existing `"EVAL_ACTION_DEADLINE"`:

```
eval codes: 42/42 engine checks documented in §5.7.1 (D-031)      exit 0
```

`EVAL_ACTION_DEAD` occurs **0** times, word-bounded, in the whole 84 KB proposal.

### C1-a2 — the decisive probe: a **one-character truncating rename of an existing code**

No code is added. `EVAL_SIM_STOP_IMPERSONATION_FAILED` is renamed consistently to
`EVAL_SIM_STOP_IMPERSONATION_FAILE` — one trailing character dropped — across all three of its
occurrences (`ts/src/evaluate/checks.ts:91`, `:152`, `ts/test/evaluate.checks.test.ts:341`), which
is what an actual rename would touch. §5.7.1 is left documenting the old name. This is a typo or a
half-finished rename, not a plant.

```
occurrences of EVAL_SIM_STOP_IMPERSONATION_FAILE in the proposal, word-bounded : 0

scripts/check-eval-codes.sh    -> eval codes: 41/41 engine checks documented in §5.7.1   exit 0
scripts/check-class-coverage.sh-> corpus class coverage: pass on the ratchet             exit 0
ts/test/evaluate.checks.test.ts-> tests 121  pass 121  fail 0
```

**Nothing catches it.** The engine declares a check that appears nowhere in the specification, and
the guard whose entire purpose is that comparison prints `41/41`. This is precisely the drift class
D-031 was built for, and the guard's own header states *"this is the third time a
spec-versus-implementation drift has been found by someone outside the build loop, and a guard is
the only thing that stops a fourth."*

## 1.5 Paired controls — three, each behaving oppositely

| Control | Edit | `check-eval-codes.sh` | `check-class-coverage.sh` |
|---|---|---|---|
| **C1-b** | rename the array entry to `EVAL_ACTION_ZQDEAD` (non-prefix) | **FAIL**, names the code, exit 1 | — |
| **C1-b2** | rename `…_FAILED` → `…_FAILEX` — same file, same length, **one character different, not a prefix** | **FAIL**, names the code, exit 1 | pass, exit 0 |
| **C1-c2** | the same truncating rename applied to `EVAL_ACTION_DEADLINE`, a code that **is** in the class map | `41/41` **PASS**, exit 0 | **FAIL**, exit 1 |

`C1-b2` is the load-bearing control: it differs from `C1-a2` in exactly one character and in nothing
else, and it is caught. The guard is not simply passing everything; **only the prefix relation
defeats it.**

`C1-c2` fixes the boundary of the exposure honestly. `scripts/check-class-coverage.sh` carries its
own hard-coded class map and independently catches a rename of any code in it. Enumerated:
**39 of the 41 codes are in that map; two are not** — `EVAL_NATIVE_DELTA_MATCHES_VALUE` and
`EVAL_SIM_STOP_IMPERSONATION_FAILED`. `C1-a2` sits at that intersection deliberately. So the
unprotected set today is two codes wide, and `C1-c2` proves the second instrument is live rather
than inert.

## 1.6 The two questions the brief asks about `R4-F3`, verified independently

**(i) Is the section scoping carried across? YES, and it is load-bearing.** I re-derived V3's `E4`
from scratch: removing `` `EVAL_ACTION_DEADLINE` `` from §5.7.1's "Windows and deadlines" line and
describing it under `## 6.` instead →

```
eval codes: 1 check(s) declared by the engine and absent from §5.7.1:
    EVAL_ACTION_DEADLINE                                          exit 1
```

**`R4-F3`'s obligation is discharged in this file.** C1 survives that discharge untouched, which is
the first half of why it is not a duplicate.

**(ii) Does truncation fail CLOSED here? YES — and the reason is structural, not lucky, but V3's
framing covers only one direction of the boundary.**

- Truncation fails closed **because a presence test can only lose matches when the extract
  shrinks.** Inserting `#### 5.7.1.1 Grouping notes` mid-section cut the extent 35 → 18 lines and
  produced `14 check(s) declared by the engine and absent from §5.7.1`, exit 1. The explicit
  `[ ! -s "$SPEC_SECTION" ]` guard at `:32` covers the degenerate case. There is no arrangement of
  *less* text that yields a false pass.
- **The boundary is fail-OPEN in the widening direction, and that is not covered by "truncation
  fails closed".** Demoting the `## 6. AI and Context Scope` heading to bold prose extends §5.7.1's
  awk extent from **35 to 64 lines**, and a code documented only under §6 is then certified as
  *"documented in §5.7.1"* — `41/41`, exit 0. That is `R4-F3`'s original over-scoping defect,
  reachable in this file by one heading edit. **I record this inside C1 rather than as a fourth
  candidate, because the brief asked me to verify V3's claim and this is the precise limit of what
  that claim establishes.** It belongs in A-P2's obligation set.

## 1.7 DUPLICATE of `R4-F3`? No — DISTINCT

`R4-F3` as confirmed is two properties: *locate the named section*, and *refuse rather than
silently choose among candidates*. C1 is neither.

1. **Different operator on a correctly-scoped input.** C1's input is already §5.7.1 and only
   §5.7.1 — I proved the scoping is live in §1.6(i). The defect is in `grep -q`'s **anchoring**, not
   in what it reads.
2. **"Refuse rather than choose" does not apply and is not the gap.** A presence test makes no
   choice among candidates; V3 checked this and I agree. Adding duplicate refusal to this guard
   would not touch C1.
3. **Discharging `R4-F3` completely leaves C1 live.** Demonstrated, not argued: at this commit the
   scoping is in place and `C1-a2` still passes.

## 1.8 Severity: **MEDIUM** — raised from V3's LOW

**Why not LOW.** V3 rated it LOW on the 0-prefix-pairs count. That measures the wrong quantity. The
exposure is not "how many collisions exist among 41 names" but "how small an edit creates one", and
the answer is **one character in one identifier**. `scripts/test.sh:195` runs this guard as one of
the nine in the product gate, so its verdict is load-bearing rather than advisory, and at the
two-code intersection with `check-class-coverage.sh` nothing else in the repository observes the
drift — demonstrated across three instruments, not assumed.

**Why not HIGH.** The guard's present output is true; there is no live false claim at this commit.
The guard asserts coverage, not correctness, and says so in its own header. And 39 of 41 renames
are independently caught by `check-class-coverage.sh`, so this is a hole in a layered defence rather
than the removal of the only layer.

## 1.9 What this evidence does and does not establish

- **Establishes:** the mechanism, by four edits with two discriminating controls; that the current
  41-code set contains zero prefix and zero substring collisions; that all 41 codes really are
  word-bounded present in §5.7.1 today; that the trigger is a one-character edit, not a new code;
  and that at the two-code intersection three instruments pass simultaneously.
- **Does not establish:** any live false claim at this commit. It does not establish that a
  truncating rename is *likely* — I measured its cost, not its probability. It does not establish
  anything about §5.7.1's *descriptions* being correct; the guard disclaims that and I did not
  disturb the disclaimer. I did not run the full gate or the whole TypeScript suite (evidence bound
  above); I ran the one test file that binds `EVAL_CODES`, which is the file that could have caught
  it.

## 1.10 Classification: **CONFIRMED**

Real, reproduced at the frozen commit, DISTINCT from `R4-F3`. Latent as to the guard's *output*,
not as to the defect. **No decision fork** — the remedy is an anchored membership test and there is
no product guarantee to choose between.

---

# C2 — `scripts/check-type-strings.sh:36`, fixed-depth section extraction (V3's `T7`)

## 2.1 The exact claim at issue

That `awk '/^### 5\.8 /{f=1;next} f && /^#{1,4} /{exit} f'` terminates §5.8's extent at the first
heading of depth 1-4, so a `#### 5.8.1` subsection — which every reader takes to be **inside**
§5.8 — silently narrows the guard's scope to §5.8's first 21 lines while the printed claim still
says *"published in §5.8"*, hiding an intra-section duplicate below the cut.

## 2.2 The authoritative source

`scripts/check-type-strings.sh:36`, and the section structure of
`Sentinel_Protocol_Lab_Proposal_v0_2.md` — the headings, which the repair contract correctly names
as the authority for section extent. Confirmed on this machine that `awk version 20200816` supports
ERE interval expressions, so `#{1,4}` is a genuine depth class and not a literal (checked, because
an awk that treated it literally would never terminate and the defect would be a different one).

## 2.3 Reproduction

Baseline: §5.8 spans lines 487-521, **35 lines**; the six type strings are published at lines 496,
498, 500, 502, 504, 506; guard prints `6/6`, exit 0.

**C2 (`T7` reproduced).** Insert `#### 5.8.1 Restatement for implementers` after line 506, and
below it a second `MandatePayload(…)` with `address principal,address vault` transposed:

```
extent(§5.8) = 21 lines
type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)     exit 0
```

**V3's 21 lines reproduced exactly.** §5.8 now publishes two different `MandatePayload` strings —
with different typehashes, digests and recovered addresses — and the guard certifies it.

## 2.4 Paired controls — three, and the second one is the crux

**C2-ctl — the same duplicate with NO subheading.** The D-057(5) duplicate refusal fires:

```
extent(§5.8) = 37 lines
type strings: §5.8 publishes 2 different lines for MandatePayload.
  … Refusing to pick one. Remove the duplicate.                          exit 1
```

So the mitigation works, and C2 is specifically the act that **disarms** it.

**C2-b — the subheading placed ABOVE the six publications (the fail-closed direction):**

```
extent(§5.8) = 9 lines
type strings: §5.8 does not publish EIP712Domain
… (all six) …                                                            exit 1
```

Truncation is loud when it cuts the strings out. The fail-open surface is *only* the duplicate
refusal.

**C2-c — THE CRUX CONTROL. The same duplicate, same position, under a `### ` heading instead of a
`#### ` one — i.e. genuinely OUTSIDE §5.8:**

```
extent(§5.8) = 21 lines
type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)      exit 0
```

**C2 and C2-c produce byte-identical output — same extent, same claim, same exit code — while in
one case the duplicate is inside §5.8 and in the other it is outside.** The instrument cannot
distinguish a correct pass from a false one. C2-c is the *right* answer; C2 is the *same* answer
given for the wrong reason.

## 2.5 Is the extraction heading-DEPTH-aware? **No — and this is the crux John named**

The terminator `#{1,4} ` is a **fixed depth class independent of the anchor heading's depth**. The
depth-aware rule is *"end at the first heading of depth ≤ the anchor's depth"*. The two coincide
only when the anchor sits at depth 4. Demonstrated in both directions:

| Guard | Anchor | Anchor depth | Terminator | Deeper subheading | Same/shallower heading |
|---|---|---|---|---|---|
| `check-eval-codes.sh` | `#### 5.7.1` | **4** | `#{1,4}` | `##### 5.7.1.1` → **not terminated, extent 37 lines, `41/41`, exit 0 — CORRECT** | `#### 5.7.1.1` → terminated, 18 lines, exit 1 |
| `check-type-strings.sh` | `### 5.8` | **3** | `#{1,4}` | `#### 5.8.1` → **terminated, 21 lines — WRONG** | `### …` → terminated, 21 lines — correct |

`check-eval-codes.sh` is depth-correct **by coincidence**: its anchor sits at 4, the ceiling of the
fixed class. `check-type-strings.sh` over-terminates by exactly one level. **The same literal awk
expression is right in one guard and wrong in the other, and nothing in either script records
that the correctness depends on the anchor's depth.** That is the argument for a shared primitive
that takes the anchor's depth as a parameter rather than a sixth copy of the same expression.

**One residual for the implementer, flagged not resolved.** Under a depth-aware rule, a *numbered*
subsection written at *sibling* markdown depth — a `#### 5.7.1.1` under `#### 5.7.1` — correctly
ends the parent even though its number says otherwise. A depth-aware primitive therefore also
requires the document not to write subsections at sibling depth. This is an authoring constraint
the primitive imports; it is not a fork about what the product guarantees.

**The triggering edit is ordinary, not adversarial.** The document **already** uses `####` children
under `###` sections in two places: `### 4.2 Four Demonstration Cases` carries four `#### Case N`
headings, and `### 5.7 Supported Checks and Effects` carries `#### 5.7.1`. Adding `#### 5.8.1`
follows the document's own established convention. `R4-F3`'s original defeat required a deliberate
two-edit decoy plant; C2's trigger is one well-formed editorial act that no reviewer would flag.

## 2.6 DISTINCT from `R4-F3`, or a facet of it? **DISTINCT**

1. **Opposite direction of the same class.** `R4-F3` was **over**-scoping — the guard read 84 KB
   and claimed §5.8. C2 is **under**-scoping — it reads §5.8's first 21 lines and claims §5.8. They
   share a genus and not a mechanism.
2. **C2 did not exist when `R4-F3` was filed.** There was no section extraction at all then. C2 is a
   defect **in `R4-F3`'s repair**, introduced by it. A defect a repair introduces is not the defect
   the repair addressed.
3. **Discharging `R4-F3`'s named residual does not fix C2.** That residual is the **source**
   operand at `:66` — a bare `head -1` over `ts/src/signer/eip712.ts` with neither scoping nor
   duplicate refusal. Scope and duplicate-refuse both operands perfectly and C2 is untouched,
   because C2 is not about which operand is read but about **which lines constitute §5.8**.
4. **It targets a different mitigation.** `R4-F3`'s residual defeats the byte comparison. C2
   defeats the **duplicate refusal**, the separate mechanism added at D-057(5), and *only* that one
   — every other comparison in the guard fails closed under truncation (C2-b).

**Same remedy vehicle, different obligation.** A-P2's falsification list already anticipates it
— *"(c) truncate the section with a deeper subheading"* — but the contract lists it as an
unadjudicated enumerated row, which is exactly what D-058(7) forbids relying on. It is now
adjudicated and may enter A-P2 on its own footing.

## 2.7 Severity: **MEDIUM**

**Why not LOW.** The triggering act is legitimate, conventional and invisible to review; it disarms
a mitigation installed two days earlier; and `check-type-strings.sh` runs in the product gate at
`scripts/test.sh:192`. The guard's own header calls a published-but-drifted type string *"worse
than an absent one"*.

**Why not HIGH.** The false certification needs **two** conditions, not one: the subheading *and* a
second differing publication below it. The subheading alone is inert today because all six strings
sit above the cut, and a subheading above them fails closed with six explicit refusals (C2-b). No
live false claim at this commit.

## 2.8 What this evidence does and does not establish

- **Establishes:** the mechanism, at V3's exact figure of 21 lines; that the extraction is not
  depth-aware, by a control pair whose outputs are byte-identical for opposite ground truths; that
  truncation is fail-open **only** through the duplicate refusal and fail-closed everywhere else in
  this guard; and that the triggering edit follows the document's own conventions.
- **Does not establish:** any false claim about the tree as it stands — every type string occurs
  exactly once, inside §5.8, and the baseline `6/6` is true. It does not establish that a drifted
  string could reach a signature without a duplicate: with only one publication, truncation yields
  `does not publish`, exit 1. It says nothing about `check-vendor-honesty.sh`, which uses a
  **different** extraction idiom (a literal next-heading terminator, `/^## 3\./{exit}`) with a
  different failure mode, and which is `V3-N2`'s territory, not mine.

## 2.9 Classification: **CONFIRMED**

Real, reproduced, DISTINCT from `R4-F3`. Instrument defect, not a live false claim. **No decision
fork** — John has already ruled the design must be heading-depth-aware, and my evidence supports
that ruling rather than reopening it.

---

# C3 — `scripts/check-suite-floors.sh:15`, duplicate handling

## 3.1 The exact claim at issue

That `get() { grep -E "^$1=" "$GATE" | head -1 | cut -d= -f2; }` silently returns the **first** of
several definitions, exits 0, and prints *"suite floors: read from `scripts/test.sh`, which is the
only copy"* — a **universal claim the instrument never tests**, from the instrument installed to
certify single-sourcing. A **missing** constant is correctly caught.

## 3.2 The authoritative source

`scripts/check-suite-floors.sh:15` and `:24`, against `scripts/test.sh`'s six assignments
(`:234`, `:235`, `:658`, `:659`, `:660`, `:673`) and their use site at `scripts/test.sh:797`. The
question of *what value the gate actually enforces* is settled by bash's assignment semantics —
last assignment before use wins — not by any prose.

## 3.3 Reproduction — and the defect is sharper than "returns the first value"

Baseline: all six printed, `92 · 527 · 209 · 7 · 78 · 30`, exit 0.

**C3-a — duplicate placed AFTER the original (`VERIFIER_MIN_TAMPER=999` at line 674):**

```
reader (check-suite-floors.sh)  ->  VERIFIER_MIN_TAMPER   78
                                    suite floors: … which is the only copy.     exit 0
bash, same assignment lines in file order  ->  999
```

**C3-b — duplicate placed BEFORE the original:**

```
reader  ->  VERIFIER_MIN_TAMPER  999
            suite floors: … which is the only copy.                             exit 0
bash    ->  78
```

**The reader is `head -1` (first wins); bash is last-wins. They disagree in *both* orders, in
opposite directions.** The instrument does not merely fail to notice a second copy — it reports a
floor **the gate does not enforce**, while asserting there is only one. Under C3-a it under-reports
(the gate is stricter than the reader says); under C3-b it over-reports (the gate is *looser* than
the reader says), which is the direction that matters, because a maintainer reconciling documents
against the reader would be reading a floor no run asserts.

**C3-c — a redefinition the reader cannot see at all.** `^$1=` anchors at column 0, so an indented
or compound-command assignment is invisible. With
`if [ -n "${CI:-}" ]; then VERIFIER_MIN_TAMPER=1; fi` inserted at line 674:

```
reader  ->  VERIFIER_MIN_TAMPER   78    …which is the only copy.                exit 0
bash with CI set                  ->  1
```

**C3-d — CONTROL, the opposite behaviour. A MISSING constant is caught:**

```
  MISSING: VERIFIER_MIN_TAMPER is not defined in scripts/test.sh
suite floors: a floor the gate asserts could not be read.                       exit 1
```

**C3-e — a second control, checking C1's class here.** `VERIFIER_MIN_TAMPER` is a strict prefix of
`VERIFIER_MIN_TAMPER_MODES`, so this guard could have carried C1's defect. It does not: the `=` in
`^$1=` anchors the match, and `/usr/bin/grep -cE '^VERIFIER_MIN_TAMPER='` returns 1, not 2. **The
two candidates are independent and I am not reporting one defect twice.**

**Modelling bound, stated plainly.** I could not run `scripts/test.sh` to observe the enforced value
directly (Foundry unprovisioned). The "what bash holds" column is bash executing **the same
assignment lines from the same file in file order**, plus the minimal demonstrations
`bash -c 'V=78; V=999; echo $V'` → `999` and the conditional form → `1`. That is bash's documented
semantics applied to the real lines, not an observed gate run, and I mark it as such.

## 3.4 Where the false sentence lands

`check-suite-floors.sh` is **not** in the gate — `scripts/test.sh` runs nine checkers
(`:173`-`:209`) and this is not among them; `docs/session-state.md:774` records it as *"a reporting
aid"*. It cannot make a gate pass falsely. **But it is the designated substitute for exactly the
surface `R4-F4` was filed about**, and `docs/session-state.md` directs readers to it **four** times
in place of a number:

- `:87` *"DO NOT QUOTE THE SUITE COUNTS IN §3. Run `./scripts/check-suite-floors.sh`"*
- `:232` the §1 state table — *"the numbers are deliberately not printed here"*
- `:239`, `:354` the reading order and §3
- `:378` *"Run `./scripts/check-suite-floors.sh`, which reads them from `scripts/test.sh`, the only
  copy."*

And the unverified claim is echoed in maintained prose twice more, at `docs/session-state.md:361`
(*"The gate constants are the only copy"*) and `:774`. **Three statements of a single-sourcing
property, and the one instrument that appears to verify it does not.**

I also checked whether anything else would catch a duplicated constant.
`scripts/check-gate-immutability.sh` reads `scripts/test.sh` but extracts and defends only the
`GATE BOOTSTRAP` block (`:53`); it does not pin the floor lines. Nothing else does.

## 3.5 DUPLICATE of `R4-F4`, or DISTINCT? **DISTINCT** — the argument, not the assertion

`R4-F4` as adjudicated is: *`session-state.md` §3 publishes stale figures that disagree with the
gate constants*. A-F1 restates the obligation as *"floors and counts are single-sourced;
reader-facing prose does not duplicate live values; where displayed, values are derived mechanically
from the canonical constants."* The question is whether that entails *"the reader refuses
double-sourcing"*. **It does not**, for four reasons, in ascending order of force.

1. **The obligation runs in the opposite direction.** `R4-F4` constrains what may exist
   **outside** `scripts/test.sh`: no reader-facing surface may state a live floor. C3 is a condition
   **inside** the designated single source. A-F1 is silent on the internal structure of the
   canonical file, and it can be discharged to the letter — zero prose duplicates, every display
   derived — with `scripts/test.sh` still defining a constant twice. "Single-sourced" is a claim
   about copies *elsewhere*; C3 is about the source containing two.

2. **A-F1's stated success condition cannot see it.** A-F1 succeeds when *"no live surface states a
   floor value that a constant change would falsify."* Under C3-a, mutating the *shadowed* copy
   falsifies nothing anywhere, because it is not the value bash resolves. The check passes and the
   duplicate persists.

3. **C3 defeats A-F1's own falsification method, which is the decisive point.** A-F1's pre-repair
   falsification is *"change a floor constant in the gate file; the live surfaces must either follow
   it or be absent."* With a duplicate present, changing the shadowed copy moves **nothing** — not
   the gate's behaviour, not the derived surfaces — and a test author would read that stillness as
   *"the surfaces are correctly bound"* when in fact the constant they moved is dead. **C3 is a
   defect in the instrument A-F1's evidence depends on**, which is a strictly stronger relation than
   "covered by A-F1".

4. **The number and the claim are separate assertions.** `R4-F4`'s defect was a *value* being
   stale. C3's defect is a *universal claim* — "the only copy" — being unwarranted. Make every
   value correct and the claim remains exactly as unverified as before. They have different truth
   conditions and need different obligations.

**Steelman for DUPLICATE, and why it fails.** D-058(2) directs `R4-F4` to be repaired across all six
constants under the single obligation A-F1, and the repair contract already lists
`check-suite-floors.sh:15` with falsification #5 *"Duplicate a floor constant in the gate file →
`check-suite-floors.sh` must REFUSE."* So the obligation is written down. **But the contract lists
it under A-P1 — the fail-closed command primitive — not under A-F1**, i.e. the drafters themselves
already placed it with the guard instrumentation and not with the floors obligation. That placement
is right, and it is an argument *for* DISTINCT, not against it. It is in the contract because a
sibling enumeration put it there, which under John's ruling is precisely not an adjudication.

**Timing seals it:** C3 is a defect in the mechanism built **as** `R4-F4`'s repair. `R4-F4` said
*"remove the duplication or mechanically bind it."* The binding was built. The binding does not
verify the premise it prints.

## 3.6 Severity: **MEDIUM**

**Why not LOW.** It is the one surface the project's entry-point document instructs every reader to
consult **instead of** a number, four times over — the exact position `R4-F4`'s stale line occupied,
and `R4-F4` was rated MEDIUM by its adjudicator for exactly that reason. It prints an unconditional
universal claim it never tests, and the value it prints can differ from the enforced floor in either
direction. And per §3.5(3) it silently degrades the evidence for A-F1 itself.

**Why not HIGH.** No gate can pass falsely: the script is not in the gate, and the gate enforces
whatever value bash resolves regardless of what the reader prints, so suite protection is intact and
only the description is wrong. Requires an edit to `scripts/test.sh`. **This is the same "why not
HIGH" the `R4-F4` adjudicator gave, and I apply it consistently.**

## 3.7 What this evidence does and does not establish

- **Establishes:** that a duplicate is not detected, in **both** orders, with the reported value
  diverging from the enforced value in opposite directions; that a non-column-0 redefinition is
  invisible entirely; that a missing constant IS caught, so the instrument is not simply passing
  everything; that nothing else in the repository observes a duplicated floor constant; and that the
  "only copy" claim is restated twice more in maintained prose.
- **Does not establish:** any live double-definition at this commit — all six constants are defined
  exactly once, at column 0. The "what the gate enforces" half is bash semantics applied to the real
  lines, **not an observed gate run** (evidence bound in §3.3). I did not measure how likely a
  duplicate is; `scripts/test.sh` is long and heavily edited, which is a reason to guard it, not
  evidence that it will happen.

## 3.8 Classification: **CONFIRMED**

Real, reproduced at the frozen commit, DISTINCT from `R4-F4`. Instrument defect, not a live false
claim. **No decision fork** — refusing on a second definition is the only coherent behaviour for an
instrument whose printed sentence is "which is the only copy."

---

# Adjudicator's provenance

**Files I mutated, all in my own worktree, all restored:**
`Sentinel_Protocol_Lab_Proposal_v0_2.md` (six edits), `ts/src/evaluate/checks.ts` (five),
`ts/test/evaluate.checks.test.ts` (three), `scripts/test.sh` (four),
`docs/session-state.md` (one canary line). Each restored from a pre-probe copy taken before the
first edit of that file.

**Restore verified:** `git diff HEAD --stat` empty; `git status --porcelain` shows only untracked
`ts/node_modules`; `git rev-parse HEAD` = `a18e6e61598a996d962798ad0353a166232d4490`; and
`check-eval-codes.sh` (`41/41`), `check-type-strings.sh` (`6/6`) and `check-suite-floors.sh` (all
six floors) each re-run green afterwards.

**Nothing was repaired, signed, certified, ratified or reaffirmed. No commit, no push. No file
outside this evidence directory was left changed.**

**What I did not do.** I did not run `scripts/test.sh`, `forge test`, the verifier suite, or the
full TypeScript suite — the Foundry submodules are not provisioned here and the Solidity artifacts
are not built. I ran `ts/test/evaluate.checks.test.ts` alone (121/121 baseline), because it is the
one file that binds `EVAL_CODES`. I did not read V1, V2, V4 or V5's reports; I read V3's, the
repair contract, `ENUMERATION.md` and the round-one adjudications, so that my verification of each
candidate started from the tree rather than from another reviewer's account of it. I did not
adjudicate `V3-N2` (`check-vendor-honesty.sh`), which is not mine and uses a different extraction
idiom, and I did not reopen `R4-F3` or `R4-F4`.
