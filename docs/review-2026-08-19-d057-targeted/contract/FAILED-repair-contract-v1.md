> # FAILED / SUPERSEDED — NOT OPERATIVE
> **This is preserved PROCESS EVIDENCE, not an instruction to anyone.**
> Repair Contract v1 was independently audited and returned **FAIL**.
> **D-060(1) abandons the global-contract method entirely.** There is no active
> repository-wide prose contract. Remediation proceeds through small, independently
> test-authored BATCH CARDS instead — see `../README.md`.
> **Do not implement anything from this document.**

---

# REPAIR CONTRACT — D-058 remediation, four bounded batches

**Authority:** D-058 (John, 2026-08-19). **Base SHA for all test authorship:**
`a18e6e61598a996d962798ad0353a166232d4490`.

**This contract is precommitted. The implementation agent implements against it and MAY NOT
WEAKEN IT.** Per D-058(1), for each batch an independent test author writes the observing
tests first, demonstrates each observes the pre-repair defect with a discriminating control,
and that patch is preserved BEFORE any implementation begins.

**Bounded stopping rule (D-058(9)):** at most **two** implementation attempts per batch after
its contract is fixed. Second failure of the same contract or sibling class → **STOP and return
to John.** No third iteration. A failure in one batch does not authorize widening another.

**Sibling lists below were enumerated MECHANICALLY at the base SHA**, not from the findings.
Commands are recorded in `ENUMERATION.md` beside this file. Items marked **[PENDING ADJ]** enter
the batch only if independently adjudicated CONFIRMED.

---

## SINGLE OWNERSHIP (D-059(5)) — every file and factual repair has exactly ONE owning batch

Other batches may name an item only as a **dependency**. A second implementation is a contract
violation, not a redundancy.

| Item | **OWNER** | Named as a dependency by |
|---|---|---|
| `scripts/check-review-scope.sh` (all sites) | **A** (A-P1) | — |
| `scripts/check-secrets.sh:198` | **A** (A-P1) | — |
| `scripts/check-findings-ledger.sh`, `install-hooks.sh`, `test.sh:161` `cd` sites | **A** (A-P1) | — |
| `scripts/check-type-strings.sh` (both operands) | **A** (A-P2a/A-P2b) | — |
| `scripts/check-eval-codes.sh` | **A** (A-P2a) | — |
| `scripts/check-vendor-honesty.sh` (`V3-N2`) | **A** (A-P2a) | — |
| `scripts/check-suite-floors.sh` | **A** (A-P2b + A-F1) | — |
| **All six floor constants; every live floor occurrence; `session-state.md` §3 passages; `scripts/test.sh` stale output** | **A** (A-F1) | **D** (control only) |
| **The targeted mechanical guard and its gate wiring** | **A** (A-G1) | **D** (D-F5 consumes it) |
| `contracts/src/SentinelVault.sol` events + NatSpec | **B** | — |
| `ts/src/signer/vault.ts` branch matrix | **C** | — |
| `exit-criterion-packet.md` §7 (`R2-F4`) | **D** (D-F1) | — |
| The accepted-limit derivation | **D** (D-F2) | supplies a canonical fact to A-G1 |
| `ts/src/decode/index.ts`, `ts/test/evaluate.checks.test.ts` | **D** (D-F4) | — |

## GATE 5 — D-059(1), and what it forbids the repairer from doing

**The certification STANDS (option A).** `V3-N2` did not falsify D-008(1)–(4), and the guarded
§7.2 property was measured true at this commit — independently of the broken guard, by two
parties.

**But: `check-vendor-honesty.sh` is NOT ADMISSIBLE as evidence for its supplementary §7.2
condition until repaired and independently reverified.** A guard may be broken while the property
it guards is true; the property's truth does **not** restore the guard's standing as evidence.

**THE REPAIRER MUST NOT** revoke, reaffirm, or recertify Gate 5 as any part of this work. **None
of the three.**

**The signed-text half is separate and is NOT repaired in any batch.** The phrase *"extracted from
§7.2 itself"* is a false statement about an enforcement mechanism, inside `docs/gate-s2-evidence.md`
— **a SIGNED pack**. D-059(1b): *"Do not silently edit signed text. Prepare the exact proposed
correction and its provenance for my ratification before applying it."* **It is prepared as
OFFERED / NOT-CERTIFIED and returned to John. It is not in Batch A, B, C or D.**

---

## BATCH A — gate and guard instrumentation

**D-058(8)A: "Prefer one fail-closed helper or shared extraction primitive over patching
successive call sites."** Batch A is therefore specified as TWO primitives plus their consumers,
not as six separate patches.

### A-P1 — a fail-closed command primitive

**Guarantee:** *A guard must never convert a failed or empty result from an external command
into a statement about what it measured.*

**Authoritative source:** the behaviour of `git`/shell exit codes; `scripts/check-review-scope.sh`
lines 96–105 already state this argument in prose as the `R1-F2` lesson.

**Mechanically enumerated call sites — `scripts/check-review-scope.sh`:**

| Line | Call | State at base SHA |
|---|---|---|
| 47 | `cd "$(git rev-parse --show-toplevel)"` | **UNGUARDED** — `cd ""` is a silent no-op. **`N-SCOPE-CD`: ADJUDICATED CONFIRMED, LOW (down from MEDIUM), DISTINCT from `V3-N1`.** Fail-CLOSED at 60 of 61 tracked directories and fail-open nowhere, so it never produces `V3-N1`'s "all assigned, exit 0" shape — but the diagnostic it prints is FALSE (names 13 files as unassigned that are assigned) |
| 106 | `tracked="$(git ls-files 2>&1)"` | guarded (108 fail, 114 empty) |
| 131 | `printf '%s\n' "$tracked" \| wc -l` | **DISPOSED — ARGUED EXEMPTION, no observing test required (D-059(2)).** It sits **downstream of BOTH guards** (107 failure, 114 emptiness), so the pathology that would make it count 1 instead of 0 is **unreachable**: line 114 has already exited. Residual risk is cosmetic only — the coverage claim is carried by the `unassigned` array below, not by this figure |
| 161 | `git rev-parse --verify --quiet "${since}^{commit}"` | guarded |
| 168 | `scope_diff="$(git diff --name-only "$since"..HEAD 2>&1)"` | guarded (170) |
| **198** | `git ls-files --error-unmatch "$f" \|\| continue` | **UNGUARDED — `V3-N1`, CONFIRMED.** Every failure mode is reinterpreted as "deleted since; not in scope", and it sits **upstream of the UNASSIGNED check**, so swallowed files are unchecked, not merely uncounted |

**Sibling script found by enumerating the CLASS, not reported by anyone —
`scripts/check-suite-floors.sh`:**

| Line | Call | State — **probed at base SHA** |
|---|---|---|
| 13 | `cd "$(git rev-parse --show-toplevel)"` | **UNGUARDED**, identical shape to scope-checker:47. Probe: run outside a repo → `fatal: not a git repository`, script **continues** and reads a local file |
| 15 | `get() { grep -E "^$1=" "$GATE" \| head -1 \| cut -d= -f2; }` | **`C3`: ADJUDICATED CONFIRMED, DISTINCT from `R4-F4`, MEDIUM — and sharper than first reported.** `head -1` is **FIRST-wins** while bash is **LAST-wins**, so the reader and the enforced floor disagree in **BOTH orders and in OPPOSITE directions** (duplicate after → reader 78 / gate 999; duplicate before → reader 999 / gate 78), and a non-column-0 redefinition is invisible entirely. All three print *"which is the only copy"*, exit 0. **Verified independently with a discriminating control: a single definition AGREES.** Missing-constant control correctly exits 1 |

**COMPLETENESS CHECK (D-058, required before implementation) — THE LIST ABOVE WAS INCOMPLETE.**
Sweeping the CLASS across every script, rather than the sites reporters named, found four more:

| Site | Class | State |
|---|---|---|
| `scripts/check-findings-ledger.sh:22` | unguarded `cd "$(…)"` | **ADDED by the completeness check** |
| `scripts/install-hooks.sh:5` | unguarded `cd "$(…)"` | **ADDED** |
| `scripts/test.sh:161` | unguarded `cd "$(…)"` | **ADDED — and this one is the gate itself** |
| `scripts/test.sh:60` | `_gate_src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/…"` | **ARGUED EXEMPTION, NOT A DEFECT (D-059(2)).** A legitimate `BASH_SOURCE` script-location bootstrap, guarded by `&&`. **It is why the textual occurrence count is six while the defective-script count is FIVE** |
| `scripts/check-secrets.sh:198` | `git show ":$f" >/dev/null 2>&1 \|\| continue` | **`C4`: ADJUDICATED CONFIRMED, DISTINCT from `V3-N1`, MEDIUM, FAIL-OPEN.** **The cause is `core.quotePath`, not a hypothetical git failure:** `git diff --cached --name-only` emits a quoted octal-escaped path for a non-ASCII filename, which `git show ":$f"` cannot resolve. **Demonstrated with two byte-identical files carrying a planted 64-hex key, differing only by ONE NON-ASCII BYTE IN THE FILENAME: the ASCII twin is BLOCKED; the non-ASCII twin is silently skipped and the guard prints `secret guard: clean` exit 0** while `git show` retrieves the key from the index. **Broader than reported — it defeats BOTH modes and ALL THREE rules:** a staged `.env.loc<accented>l` bypasses "env files are never committed" while its ASCII twin is blocked twice |

**FOUR OBSERVING TESTS, NOT ONE (`C6`, adjudicated).** A-P1 covers the mechanism for all four
`cd` sites, but **two fail OPEN and two fail CLOSED, and `install-hooks.sh` needs a SIDE-EFFECT
assertion no other site needs.** Merging them into one disposition item **would repeat the exact
D-057(1) grouping error the findings-ledger checker exists to prevent.**

| Site | Class | Severity | Fail direction | Decisive evidence |
|---|---|---|---|---|
| `check-findings-ledger.sh:22` | CONFIRMED (`C6a`) | INFO | fail-CLOSED | — |
| `check-suite-floors.sh:13` | CONFIRMED (`C6b`) | LOW | **fail-OPEN** | printed floors `1/1/1/1/1/1` **plus "read from scripts/test.sh, which is the only copy"**, exit 0, against a decoy tree |
| `install-hooks.sh:5` | CONFIRMED (`C6c`) | LOW | **fail-OPEN** | printed "hooks installed", exit 0, having set `core.hooksPath` **in a FOREIGN repository** (sandboxed scratch repos only) |
| `test.sh:161` | CONFIRMED (`C6d`) **+ DECISION FORK** | LOW (MEDIUM on an attribution reading) | fail-CLOSED as measured | executed seven guard scripts **from a decoy tree**, but the run failed closed at exit 5 `GATE DID NOT REACH COMPLETION`; control from the correct root: `GATE PASSED`, exit 0 |
| `test.sh:60` | **NOT A DEFECT** | — | fail-CLOSED | exemption confirmed three independent ways |

**`C6d` CARRIES A DECISION FORK THAT IS NOT AN AGENT'S, AND FIXING `cd ""` DOES NOT TOUCH IT.**
`cd "$(git rev-parse --show-toplevel)"` means **the CALLER's repo root, not the SCRIPT's tree** —
and those diverge **even when git works perfectly**. **(A)** keep caller-relative semantics and
document the hazard, or **(B)** move to the `BASH_SOURCE` idiom already exempted at `test.sh:60`.
**This changes what a `GATE PASSED` line asserts, so it is John's.**

**THE ARITHMETIC, STATED SO IT CANNOT DRIFT (D-059(2)): FIVE distinct scripts carry the defective
git-root pattern** — `check-findings-ledger.sh`, `check-review-scope.sh`, `check-suite-floors.sh`,
`install-hooks.sh`, `test.sh`. **The sixth textual `cd "$(…)"` occurrence is `test.sh:60`'s
exempted bootstrap. Five defective scripts, six textual occurrences — different counts, used
separately throughout this contract.**

Two supporting facts established by probe rather than assumed:

- **`cd ""` returns 0 and does NOT abort, even under `set -euo pipefail`.** So every one of the
  six `cd "$(git rev-parse --show-toplevel)"` sites is genuinely unguarded; `set -e` is no
  defence. (Only `check-secrets.sh`, `install-hooks.sh` and `test.sh` set `-e` at all; the other
  twelve scripts use `set -uo pipefail`, under which a failed substitution is not fatal.)
- **`scripts/check-rename-gate.sh` is NOT a defect and is the MODEL for this primitive.** It
  already handles both empty cases explicitly, printing `UNVERIFIED` with *"D-016 still blocks
  publication"*, under a comment reading *"Deliberately not a silent pass. An unverifiable guard
  must say so, or a reader will take its silence for a green light."* **Residual, not a defect,
  and John's to rule on: it exits 0 when UNVERIFIED, so a caller reading only the exit status
  sees a pass.**

**Pre-repair falsification (must be shown to fail before the fix):**
1. `PATH`-shim `git` so `ls-files` exits non-zero → scope checker must REFUSE, not summarise.
2. Shim so `ls-files` returns empty with exit 0 → must REFUSE.
3. Shim so only `ls-files --error-unmatch` fails → must REFUSE (this is the `V3-N1` site; at base
   SHA it prints `0 file(s) changed … all assigned`, exit 0).
4. Run **each of the six** `cd`-bearing scripts from a non-repository directory → must REFUSE.
5. Duplicate a floor constant in the gate file → `check-suite-floors.sh` must REFUSE.
6. Make `git show ":$f"` fail for one staged file → `check-secrets.sh --staged` must REFUSE, not
   skip it and print `clean`. **A blanket refusal is explicitly NOT the accepted repair — see
   below.**

**D-059(3) — THE STAGED-SECRET CONTROL MUST DISCRIMINATE. This is a constraint on the fix, not a
detail.**

| Case | Required behaviour |
|---|---|
| **(a)** an expected staged **deletion**, or a path legitimately absent from the index | **CONTROL — must NOT refuse** |
| **(b)** a `git show` **instrument failure** on a file that should be scanned | **MUST REFUSE** |

**John's warning, which forecloses the lazy fix:** *"a blanket 'git show failure always refuses'
risks converting a legitimate deletion into a false failure."*

**A RELIABLE DISCRIMINATOR EXISTS. THIS IS NOT A DECISION FORK (`C4`, adjudicated)** — and it is
not where it was being looked for:

- **NOT from `git show`.** Every failure mode returns **exit 128** — path-not-in-index,
  path-absent, mangled token, missing object — and the stderr strings that differ are localizable
  prose. **An exit-code discriminator does not exist.**
- **The discriminator is UPSTREAM, in the file list — and John's protected control is ALREADY
  excluded there.** Line 78's `--diff-filter=ACM` drops status `D`, so **a staged deletion cannot
  reach line 198 at all** (verified). The feared false failure is structurally impossible.
- **The mechanism:** `git diff --cached --raw -z` supplies the **status letter plus the post-image
  blob OID**, and `-z` removes path quoting outright — which also removes `C4`'s root cause.
  **Status `D` => skip; any other status => a real blob exists, so retrieval failure is BY
  CONSTRUCTION an instrument failure => refuse.**

**Paired controls (must remain PASSING):** an ordinary run from the repository root assigns every
tracked file and exits 0; a genuinely deleted-since file is still correctly skipped without
refusing the whole run; the unmodified gate file still yields all six floors.

**Exact success condition:** every row above is either routed through the primitive or carries a
recorded, argued exemption; **all SIX numbered falsifications refuse** — the list is six items and
the earlier draft's success condition said five (corrected under D-059(2)); all three controls
pass.

**Outside the evidence:** whether any non-shim route can make `git` fail in practice. A `PATH`
shim is the standard `V3-N1` itself was established on, and no live route was found.

### A-P2 — TWO distinct properties, deliberately NOT one primitive (D-059(8))

**John's ruling: "Do not force both through a primitive whose semantics only describe Markdown
sections."** These are different guarantees over different substrates and the contract keeps them
apart:

**A-P2a — EXACTLY ONE NORMATIVE PUBLICATION INSIDE A NAMED MARKDOWN SECTION.**
*A guard that certifies a NAMED section must locate that section with **HEADING-DEPTH-AWARE
extent** — a deeper subheading (`#### 5.8.1`) lies INSIDE `§5.8`, while a same-or-shallower
heading (`###`/`##`) ENDS it — and must refuse when the section publishes a value more than once
rather than silently picking one.*

**A-P2b — EXACTLY ONE AUTHORITATIVE DEFINITION IN A SOURCE FILE.**
*A guard comparing against a source-of-truth constant or literal must establish that the source
defines it exactly once.* This is the `check-type-strings.sh:66` `src_line` half and
`check-suite-floors.sh:15`'s `get()`. **It has no sections and no headings; a Markdown-section
primitive cannot express it.**

**LEGITIMATE PROSE MENTIONS ARE CONTROLS AND MUST NOT COUNT AS NORMATIVE PUBLICATIONS** — a
backticked mention of a type name inside §5.8 is not a second publication. This control already
passes today and must keep passing.

**Authoritative source:** the guards' own printed certification lines, which name §5.7.1, §5.8
and §7.2.

**Mechanically enumerated consumers** (`/usr/bin/grep -nE 'head -1|head -n *1' scripts/*.sh`):

| Site | State at base SHA |
|---|---|
| `check-type-strings.sh:65` **spec** operand | scoped to §5.8 **and** duplicate-refusing — this half HOLDS (V3 confirmed, both orders, with a NODUP pre-fix comparison) |
| `check-type-strings.sh:66` **src** operand | **UNGUARDED — `R4-F3`, CONFIRMED.** Bare `head -1` over the whole `eip712.ts`, no duplicate refusal, no scoping. A decoy quoted string above the real one wins |
| `check-eval-codes.sh` | **`C1`: ADJUDICATED CONFIRMED, DISTINCT from `R4-F3`, MEDIUM — RAISED from V3's LOW, and V3's reason for calling it latent was WRONG.** The trigger is not a second code, it is **a one-character edit**: renaming `EVAL_SIM_STOP_IMPERSONATION_FAILED` → `…_FAILE` consistently across engine and test yields `41/41 exit 0` for a code occurring **zero** times in the proposal, with class-coverage green and TS 121/121. Controls: the non-prefix `…_FAILEX` IS caught, and the same truncation on `EVAL_ACTION_DEADLINE` IS caught by class-coverage — both instruments are live. **Only 2 of 41 codes sit outside class-coverage's map: that is the unprotected set.** ALSO: the §5.7.1 boundary is fail-**OPEN in the WIDENING direction** — demoting the `## 6.` heading extends the extent 35→64 lines and certifies a §6-documented code as "documented in §5.7.1" |
| `check-vendor-honesty.sh:269` | **whole-document grep + `head -1`**, prints *"as §7.2 words it"* — **`V3-N2`: ADJUDICATED CONFIRMED, MEDIUM.** Two falsifications, three opposite-behaving controls. The sharper one leaves §7.2 UNTOUCHED, plants a decoy carrying the anchor phrase earlier in the document, and swaps the report's quote for the decoy: the report then carries §7.2's real wording **zero** times and the guard still prints *"carries §7.2's caveat verbatim, as §7.2 words it"*, exit 0. **A-028's original defect fully reinstated.** The same defect was repaired TWICE in this very file on 2026-08-16; the caveat block sits between the two repairs, unswept |
| `check-vendor-honesty.sh:352` | `head -1` over `$sec2`; already section-scoped — verify duplicate behaviour |
| `check-type-strings.sh` §-scoping via `awk` | **`C2`: ADJUDICATED CONFIRMED, DISTINCT, MEDIUM.** Reproduced at V3's exact figure (extent 21 lines, `6/6`, exit 0). **THE MECHANISM: the extraction is NOT heading-depth-aware — `#{1,4}` is a FIXED depth class independent of the anchor's depth.** That is why the identical `awk` line is CORRECT in `check-eval-codes.sh` (anchor `####`, depth 4) and WRONG in `check-type-strings.sh` (anchor `###`, depth 3 — it over-terminates by one level). **The crux control: the same duplicate under a `### ` heading (genuinely OUTSIDE §5.8) produces BYTE-IDENTICAL output to the `#### ` case (genuinely INSIDE) — the instrument cannot tell a correct pass from a false one.** DISTINCT because `C2` is under-scoping introduced BY `R4-F3`'s repair; fixing `R4-F3`'s named residual leaves `C2` wholly live. The document already carries `####` children under `###` at §4.2 and §5.7 |

**Pre-repair falsification:** for EVERY consumer — (a) plant a duplicate publication inside the
named section, **in both orders**, since `head -1` makes order decisive; (b) plant the value
**outside** the named section only; (c) truncate the section with a deeper subheading; (d) make
the section absent entirely.

**Paired control:** a legitimate single publication in its proper place, plus a legitimate
backticked prose *mention* inside the section, must **not** be flagged. (V3 established this
control passes today for `check-type-strings.sh`.)

**Exact success condition:** each falsification produces a refusal naming the section and the
reason; each control passes; the primitive is shared rather than duplicated per script.

**Outside the evidence:** whether the proposal's section numbering is itself stable. The
primitive assumes headings are the authority for section extent.

### A-F1 — `R4-F4` across all six floor constants (D-058(2))

**Claim:** *floors and counts are single-sourced; reader-facing prose does not duplicate live
values; where displayed, values are derived mechanically from the canonical constants.*

**Authoritative source:** `scripts/test.sh` — `FOUNDRY_MIN_TESTS`, `TS_MIN_TESTS`,
`VERIFIER_MIN_TESTS`, `VERIFIER_MIN_SAMPLES`, `VERIFIER_MIN_TAMPER`, `VERIFIER_MIN_TAMPER_MODES`.

**Reader-facing occurrences, enumerated with PARAGRAPH NORMALIZATION (D-058(6) disallows line
grep here); the probe was self-tested against a known wrapped string first:**

| Site | Content | Class |
|---|---|---|
| `docs/session-state.md` §3 (~l.365) | *"7 samples · 78 tamper cases over 30 modes"*, present tense, **five lines under** *"The figures are no longer duplicated here"* | **LIVE — repair** |
| `docs/session-state.md:470` (at this SHA) | *"D-010 verifier: 7 samples, 77 tamper cases over 29 modes, 160 tests — and all four are FLOORS the gate asserts"* — **three of four stale**, bold present tense, and contradicts the site above **in the same file** | **LIVE — repair.** Reported by V5 and re-found independently by ADJ1. **It falsifies V2's stated conclusion that "no stale disagreeing live duplicate exists at this commit"** — it sits ~79 lines below the §3 passage V2 did flag |
| `scripts/test.sh` COVERAGE heredoc (`:839-1190`, quoted — every figure is a literal) | Duplicates **FOUR of the six** constants. **FOUR stale figures across two sentences: `180` (`:980-981`; canonical 209) plus `160/77/29` (`:984`; canonical 209/78/30).** `7`, `78`, `30` are currently right but still duplicated. `92`, `527`, `209` appear nowhere in the block | **LIVE — `N-TESTSH-FLOORS` ADJUDICATED *DUPLICATE* of `R4-F4`** under D-058(2), so it is repaired **inside A-F1**, not as a separate item. **This corrects V5's "stale trio" to four.** The `:983-984` sentence is MIXED: `62/24/149 FROM 2026-08-16 UNTIL 2026-08-17` is correctly historical, but *"the floors **this same run** asserts read 160/7/77/29"* is a live self-referential claim (line 797 prints `209 · 7 · 78/30`), and *"They are corrected here"* is FALSE |
| `docs/round-six-brief.md:28` | `75/481/180 · 7 samples · 78 tamper · 30 modes` | **HISTORICAL** — sits under *"Baseline at the time of writing — VERIFY IT YOURSELF"*; a spent document |
| `verifier/REPORT.md` (several) | each figure carries its own *"Results after X (date)"* | **HISTORICAL** |
| `docs/decisions.md` (several) | dated entries | **HISTORICAL — D-058(8)D forbids rewriting** |

**ORDERING CONSTRAINT INSIDE BATCH A — `C3` MUST BE REPAIRED BEFORE A-F1's FALSIFICATION MEANS
ANYTHING.** This is the adjudicator's decisive argument and it changes how this batch is built:
**`C3` breaks A-F1's own falsification method.** A-F1 falsifies by mutating a floor constant and
checking that the surfaces follow. **If a shadowed duplicate exists in the gate file, mutating one
copy moves nothing — and a test author would read that stillness as PROOF the surfaces are
bound.** A-F1's probe would be dead in precisely the way that reads as a pass. **Therefore: repair
`C3` first, then author A-F1's falsification.**

**Pre-repair falsification:** change a floor constant in the gate file; the live surfaces must
either follow it or be absent. At base SHA, mutating `VERIFIER_MIN_TAMPER` to 80 leaves the
documents at 78 with **all twelve guards passing, exit 0**.

**Paired control:** a correctly-framed historical figure (`round-six-brief.md:28`, whose own
heading disclaims it) must **not** be flagged. The distinction is framing, not arithmetic.

**Exact success condition:** no live surface states a floor value that a constant change would
falsify; a targeted canonical-fact check (per D-058(6): **paragraph-normalized, never line grep**)
fails when a live surface disagrees and passes on the historical control.

**Outside the evidence:** the six constants are floors, not measurements. Nothing here says the
suites assert anything, only that the numbers are single-sourced.

---

## BATCH B — vault event evidence

**Guarantee:** *§3.3(2) requires the vault's state-changing and authorization events to be
LOGGED, and a logged event must not be able to state something false on any execution path.*

**Authoritative source:** `contracts/src/SentinelVault.sol` declarations and emit sites — not any
prose count. **A prior repair's own header sentence ("exactly the five D-043 did not touch") is
false at this commit and is itself a Batch D item.**

**Mechanically enumerated: eight declared events, eight emit sites, two execution entry points.**

| Event | Emit | Path | Test refs |
|---|---|---|---|
| `MandateActivated` | L189 | `activateMandate` (owner) | 3 |
| `MandateRevoked` | L195 | `revokeMandate` (owner) | 6 |
| `PolicyActivated` | L200 | `activatePolicy` (owner) | 3 |
| `SignerRotated` | L205 | `rotateSigner` (owner) | 4 |
| `PausedSet` | L211 | `setPaused` (owner) | 5 |
| `Recovered` | L216 | `recover` (owner) | 6 |
| `OverrideAuthorized` | L277 | `executeWithOverride` **only** | **1 — weakest of the eight** |
| `ActionExecuted` | L381 | `_consumeAndCall`, reached from **BOTH** | 3 |

**The branch that matters, stated explicitly (D-058(8)B):** `_consumeAndCall` is reached at
**L238** from `executeWithReceipt` with `viaOverride=false`, and at **L281** from
`executeWithOverride` with `viaOverride=true`. **`ActionExecuted` is the only event with a
path-discriminating field.** At base SHA the automatic value is asserted and **the override value
is asserted by nothing.**

**Pre-repair falsification — COMPILING MUTANTS ONLY (D-058(8)B).** A compile failure, a
`deny = "warnings"` failure, or a log retained only by `vm.recordLogs` is **not** a caught
behavioural mutation.

1. `viaOverride && false` at L381 → log denies every override. **At base SHA: 92/92 green,
   SURVIVES.** (Naive `false` orphans the parameter and is a COMPILE ERROR — not a survivor.)
2. `viaOverride || true` → log claims every action is an override. **At base SHA: caught, 91/92.**
   This asymmetry is what proves the mutation is not inert.
3. For each of the other seven events: delete the emit; substitute a field value; substitute a
   different event. Each must fail a **named** test.

**Paired control:** a correct emission on each path must still pass, and a mid-window ordinary
execution on **both** entry points must succeed.

**Exact success condition:** every one of the eight events fails a named test under omission and
under field substitution, on **every** path that emits it; `ActionExecuted.viaOverride` is pinned
`false` on L238's path and `true` on L281's path.

### B-F1 — `F7-R1` — **ADJUDICATED CONFIRMED** (LOW as risk; a false claim in the contract's own audit-log NatSpec)

**Claim under test:** `SentinelVault.sol` NatSpec (~L274) — the `OverrideAuthorized` log *"records
them even if the external call then reverts the transaction away."*

**Authoritative source:** the EVM. `_consumeAndCall` does `if (!ok) revert CallFailed(ret);`,
which reverts the whole transaction and discards its logs.

**D-058(5) forecloses the remedy in advance: truthful NatSpec, NOT machinery to preserve logs
across a revert.** The repair is a sentence, and it must describe the automatic/override branch
accurately.

**DEMONSTRATED ON LIVE `anvil` via `eth_getTransactionReceipt`**, enumerating transactions from
the chain rather than trusting the broadcast file. **The decisive probe is a transaction mined
with status `0x1`:** a Relay contract swallows the vault's revert, so nobody can argue "the whole
tx reverted" — its complete receipt carries `Attempted(ok=false)` and **no `OverrideAuthorized`**.
**Paired control, same block, same relay, succeeding call:** `OverrideAuthorized, ActionExecuted,
Purchased, Attempted(ok=true)`. Plain top-level revert: status `0x0`, zero logs.

**The trap was demonstrated, not just warned about:** `vm.recordLogs` reports **1**
`OverrideAuthorized` for a frame whose every state write was discarded (`actionNonce == 0`) — the
same answer it gives for a genuine success. A test written that way proves nothing.

**Sibling sweep: exactly ONE live site**, `contracts/src/SentinelVault.sol:275-276`.
`docs/v1-1-register.md:176` already states only the true half.

**WORDING IS NOT YET ACCEPTED (D-059(9)).** John: *"verify that 'if and only if the action
executed' is accurate for every successful and reverted route. Prefer precise EVM language over
'executed' if that word could include a reverted external call."*

**I checked, and the word does not survive the check.** There is a route where the action *did*
execute and no event is durably observable: the vault frame completes, the external call succeeds,
and **an outer frame reverts afterwards** — the transaction is discarded with all its logs. So
*"if and only if the action executed"* is **FALSE in the "if" direction**. The proposed wording is
therefore **rejected as drafted**.

**Candidate wording, to be verified by the Batch B test author against every route rather than
adopted here:** keep *"records only authorizations that passed"*; then — **"An observer sees this
event only when the enclosing transaction SUCCEEDS; a reverted transaction discards it along with
every state change. It records authorizations CONSUMED by a successful execution, not
authorizations GRANTED."**

**Three proven facts the repair must preserve (D-059(9)):** `OverrideAuthorized` records an
override **consumed in a successful transaction**; **a reverted transaction exposes NO durable
vault event**; and **Foundry `vm.recordLogs` output from reverted frames is NOT on-chain
evidence.** **AND A CORRECTION TO THE ORIGINAL FRAMING: the two branches do NOT differ in
revert-survival** — both funnel into `_consumeAndCall`. They differ in that the override path
emits an additional event, sets `viaOverride = true`, orders `OverrideAuthorized` strictly before
`ActionExecuted`, and authenticates strictly more.

---

## BATCH C — signer state machine

**Guarantee:** *A refusal record must name the condition that actually occurred. A
confirmation-pending state must never be reported as an observation that was made and disagreed.*

**Authoritative source:** `ts/src/signer/vault.ts` `readVaultState`, and `ts/src/signer/protocol.ts`
`SIGNER_CHAIN_UNSTABLE`'s published meaning.

**THE BRANCH MATRIX, EXPRESSED EXPLICITLY (D-058(8)C) — five states, not two:**

| # | State | Trigger | Reads issued? | `pendingOnly` | Pinned at base SHA? |
|---|---|---|---|---|---|
| B0 | init | — | — | `true` (L173) | n/a |
| B1 | **before reads** — pending head | `head.hash === null` | **NO** | stays `true` (L182) | **YES** — mutation caught, 526/527 |
| B2 | **during reads** — head moved / same-height reorg | `confirm.number !== at \|\| confirm.hash !== headHash` | yes, discarded | set `false` (L232) | YES |
| B3 | **confirmation-pending** | `confirm.hash === null` | **YES, against a hashed head** | stays `true` (L228) | **NO — `R2-F6`, CONFIRMED. Mutation survives 527/527** |
| B4 | exhaustion | 5 attempts | varies | carried into `ChainUnstableError(…, pendingOnly)` (L256) | message collapses B1 and B3 |
| B5 | success | confirm matches | yes | n/a | returns (L236) |

**The mixed states are part of the matrix and must not be omitted.** Across five attempts any
combination can occur; `pendingOnly` is a single boolean, so **B1+B3 mixed still reports B1's
wording** — *"every observation returned a pending block with no hash, so there was nothing to
anchor to"* — which is false for the B3 attempts, where 55 reads were issued against 5 finalised
hashed heads.

**Pre-repair falsification:** restore `pendingOnly = false` in B3 (**survives 527/527 at base
SHA**); collapse the two messages into one; swap them; drive B1+B3 mixed and B3+B2 mixed and
assert the reported condition matches what occurred.

**Paired control (D-058(8)C, "unchanged-chain controls"):** a stable chain still returns a normal
snapshot; the same mutation applied to **B1** is caught (526/527), which is what proves the B3
probe is live and not inert; `SIGNER_VAULT_UNREACHABLE` remains distinguishable from both.

**Exact success condition:** every state B1–B4 including the mixed combinations is pinned by a
named test that fails when its condition is misreported; no state inherits another's wording.

**Outside the evidence:** V3 reports there is **no refusal detail** — `RefusalRecord` and
`Refusal` carry codes only and all three product call sites swallow the error — so
`protocol.ts:115` and A-077's *"the detail now distinguishes them"* are unsupported. **That is a
Batch D claim item, not a Batch C code change**, unless adjudication rules otherwise.

---

## BATCH D — maintained claims

**D-058(8)D: preserved review reports and dated historical decision entries are EVIDENCE, not
maintained current claims. They are not rewritten.**

### D-F1 — `R2-F4`, every current reader-facing location

**RE-ENUMERATED FROM THE RULE, NOT FROM THE EARLIER DRAFT'S EXPECTATION (D-059(6): "do not force
the answer to remain 'two'"). THE ANSWER IS ONE.**

Searched tree-wide with paragraph normalization across hard wraps — code comments, Solidity
NatSpec, Python docstrings, the proposal, `HANDOFF.md` and the docs, not `docs/*.md` alone.
D-058(3) rules `decisions.md:223` historical; **D-059(6) rules `decisions.md:225` historical too**,
which removes the second of the two sites the earlier draft carried. What remains:

| Site | Content | Class |
|---|---|---|
| `docs/exit-criterion-packet.md` §7 BLOCKER 1 | *"it does not … under C1 condition 4 this alone blocks exit"* — the packet's own stated test now returns **2** | **LIVE — and load-bearing: a false BLOCKER would corrupt the exit assessment** |
| `docs/decisions.md:225`, A-070 residual (b) | the originating sentence the register's struck bullet quotes | **HISTORICAL — D-059(6) REVERSES THE EARLIER DRAFT.** A dated decision entry is evidence, not a maintained current claim. **Preserve as history; if the wording could mislead, add a later correction or supersession entry — do NOT rewrite the record** |
| `docs/decisions.md:223`, D-052(a) | present-tense wording inside a ruling's enumeration | **HISTORICAL — D-058(3)** |
| `docs/exit-criterion-packet.md:101` (§3b) | the same claim | **ALREADY CORRECTED** — struck and superseded at A-078. Not a defect; it is the control showing the sweep distinguishes corrected from live |
| `docs/v1-1-register.md:877`, §13.7 heading and body | *"The human-readable `description` is compared to nothing"* | **TRUE, NOT A DEFECT.** The NARROWED claim about the `description` sub-field genuinely holds. It must not be "corrected" |

**THE ONE LIVE FALSE SITE: `docs/exit-criterion-packet.md:211`, §7 BLOCKER 1.** It states the
verifier *"does not"* perform the comparison and that *"under C1 condition 4 this alone blocks
exit"*, while the packet's own stated test returns **2**. **Load-bearing: a false BLOCKER in §7
would corrupt the exit assessment itself.**

**Controls (three, all of which must remain unflagged):** §3b's corrected-and-struck copy; §13.7's
narrowed-and-TRUE `description` claim; and the dated historical entries. **A sweep that flags any
of these three is over-broad and fails its own control.**

### D-F2 — the accepted-limit derivation

**The one fact that makes SIX correct and which §11.0 states NOWHERE: `D-09` is in BOTH sets** —
(c) FIXED by A-076, (a),(b) still ACCEPTED. **Authoritative source: `docs/v1-1-register.md` §13.4
line 773**, which records exactly that. Wholly-removed entries are `D-10`, `G-5`, `H-5`, `H-8` =
**FOUR**; ten minus four = six. The preserved adjudication derived it correctly at the time.

**Two defects to repair:** the surviving derivation *"Ten minus the five fixed leaves six"*
computes to five; and l.548's **"FIVE OF THESE TEN ARE NO LONGER ACCEPTED LIMITS"** is false —
only four are. **Third uncorrected copy:** `docs/session-state.md` (~l.152), which survived
because the phrase straddles a line break.

**Control:** legitimately historical statements of "ten" must remain intact and unflagged.

### D-F3 — **REMOVED. Batch A owns it (D-059(5)).**

The earlier draft had Batch D repairing `docs/session-state.md` §3's count passages, which
**Batch A already owns under A-F1**. D-059(5): *"Every file and factual repair must have exactly
one owning batch. Other batches may name it only as a dependency."*

**Owner: Batch A (A-F1)** — every live floor occurrence, including both `session-state.md`
passages and `scripts/test.sh`'s stale output. **Batch D names them as a DEPENDENCY only and
implements nothing there.** V5's context-free control on the handoff's narrative half **passed**
and is not reopened.

### D-F4 — fictitious names and false E4 statements — **BOTH ADJUDICATED CONFIRMED**

**`N-EVAL-ACTION-TARGET` — CONFIRMED, LOW, cosmetic.** `ts/test/evaluate.checks.test.ts:502`
cites `EVAL_ACTION_TARGET_MATCHES_MANDATE` in a `//` COMMENT — not a test name, not an assertion;
the assertion below uses the real `EVAL_TARGET_BOUND` and the file runs 121/121. Mechanically
derived: exactly **one** orphan cited-but-never-defined and **zero** defined-but-uncited, which is
the control proving the sweep discriminates. **Independently re-derived by the adjudicator and by
me, agreeing on the orphan set.** Same CLASS as `R3-F4` but a distinct new instance; `R3-F4`'s own
repair is intact. **No guard exists in this direction** — a planted fictitious name passed all
twelve `check-*.sh`.

**`N-DECODE-E4` — CONFIRMED IN PART, MEDIUM. The split is the whole finding and a repairer must
not get it wrong.** In `ts/src/decode/index.ts:190-195`:

| Clause | Verdict |
|---|---|
| *"nor the verifier"* | **FALSE.** `verifier/verify.py:1434` `_evidence_describes_the_bundle` compares `normalizedAction` to all twelve §5.3 action fields plus `keccak256(callData)==dataHash`, and `expectedEffects` to six mandate fields, one policy field and the §5.2-intersected ceiling — reached from **BOTH** paths (`:911` refusal, `:1629` receipt). Verified independently. False for its entire standing life: the comment's last edit is `c2fc8d2` (A-068); the check landed at `78ac9cb` (A-069), the very next commit |
| *"NEITHER the signer"* | **TRUE, AND DELIBERATE (D-014).** `normalizedAction`/`expectedEffects` appear nowhere in `ts/src/signer/`. **A repairer MUST NOT read the signer half as a defect to close** |
| *"Both are open (v1.1 register)"* | **FALSE.** The register's E4 row reads "VERIFIER HALF BUILT · SIGNER HALF DELIBERATELY NOT BUILT — not an open defect" |

**Narrow residue of truth to preserve:** `expectedEffects` is bound to mandate/policy, and to the
action only transitively via the ALLOW-gated `_allow_conforms_to_the_mandate` — deliberately
absent on BLOCK/REVIEW. **No decision fork.** The repair is a truthful comment, nothing more.

### D-F5 — CLAIM-SIDE USE of the Batch A guard (D-059(5)) — **not a second checker**

**Batch D does NOT build a checker.** D-059(5): *"D-F5 should specify claim-side use of the Batch
A primitive, not another checker."* Batch D supplies the **canonical facts** to be asserted and
**consumes** the Batch A guard. **Batch A owns the implementation; Batch D names it as a
dependency only.**

Canonical facts Batch D contributes: **the accepted-limit count (six)**. The six floor constants
are Batch A's own (A-F1).

**D-058(6) constraints carried:** no generic prose-consistency checker; and **any Markdown check
MUST normalize logical paragraphs across hard line wraps — a line-oriented grep is DISALLOWED**,
because that is exactly how both A-080 misses survived a sweep that reported clean.

### A-G1 — WHERE THE TARGETED GUARD RUNS (D-059(7)) — owned by Batch A

**"A standalone script that nothing invokes repeats the defect this work is trying to close."**
`check-suite-floors.sh` is that defect today: it is referenced in prose and **invoked by no
script**. The guard therefore has a binding placement requirement:

1. **Invoked by the applicable fast AND deep gate paths** — named in `scripts/test.sh`, not merely
   present in `scripts/`.
2. **A TOP-LEVEL falsification: make a targeted canonical fact wrong and show THE GATE fails** —
   not that the standalone script fails. The gate's own output must carry the failure and the run
   must not print its completion token.
3. **An unchanged control: the real gate still passes** on an unmutated tree, emitting
   `GATE PASSED` and its completion token.
4. **An explicit scope statement in the guard's own output and header: it covers ONLY its
   enumerated canonical facts and is NOT general prose-consistency evidence.** A guard that
   implies broader assurance than it measures is the defect class this whole cycle exists to
   close.
