# A-EXTRACT — gate binding (D-059(7)), measured

> *"A standalone script that nothing invokes repeats the defect this work is trying to close.
> Required: invocation by the applicable fast and deep gate paths; a TOP-LEVEL falsification
> showing THE GATE fails when the targeted fact is wrong; an unchanged control showing the real
> gate passes; and an explicit statement that the guard covers only its enumerated canonical facts
> and is NOT general prose-consistency evidence."* — D-059(7)

**Harness:** `a-extract-gate.sh`, sha256
`9da8d3295fecacf68312524080f77db3c35dcf34e308804d657c46bc1a37827e`.
**Subject:** a private `git clone` of this repository checked out at
`bb664c626d592d86391f644bf014e76f2bbf7db4`, with `ts/node_modules` and both submodule working
trees copied in. **The live gate is never run, never edited, and never written to.** No signed or
certified document is read for change; control `Z-signed` asserts `docs/gate-s2-evidence.md` is
byte-identical to the base commit.

**Environment:** git 2.50.1 (Apple Git-155); bash 3.2.57; node v26.3.0; Python 3.9.6; forge on
PATH. **Fast profile only** — see §5.

## STATUS — D-059(7) IS PARTLY DISCHARGED, AND THIS DOCUMENT PREVIOUSLY OVERSTATED IT

**Corrected on John's review. The earlier wording — including the harness's own closing line
"D-059(7) GATE BINDING ESTABLISHED" — read as though the whole obligation were discharged. It is
not.** D-059(7) requires *"invocation by the applicable fast and deep gate paths"*, and only one
of the two was run.

| | Status |
|---|---|
| **Fast-profile gate binding** | **MEASURED.** Three full `./scripts/test.sh` runs against a private clone: unchanged passes, a targeted failure fails the gate at its named stage, and that failure survives other consumers succeeding both before and after it. |
| **Deep-profile invocation (`--gate`)** | **NOT MEASURED.** Supported only by **STATIC CONTROL-FLOW EVIDENCE**: the three consumer invocations sit at `scripts/test.sh:235`, `:238` and `:252`; between line 210 (where `PROFILE` is assigned) and line 253 there is no `if`, `fi`, `else`, `case`, `esac`, `while`, `for` or `do` at column 0, so nothing encloses them; the first `PROFILE`-dependent statement is at line 308. Strong, and still a reading of the source rather than an observation of a run. |
| **D-059(7) overall** | **NOT YET DISCHARGED.** The deep portion is outstanding. |

**WHAT THE EVENTUAL INDEPENDENT POST-REPAIR VERIFICATION MUST DO TO CLOSE IT.** Run
`./scripts/test.sh --gate` **at the exact candidate SHA** and capture the three stage banners:

```
== published EIP-712 type strings (D-023) ==
== §5.7.1 check coverage (D-031) ==
== vendor honesty (§7.5 Gate 5, D-008) ==
```

**Three deep MUTATION runs are NOT required unless the control flow differs between profiles.**
The fast profile's mutation evidence below already establishes that a failure in any one of the
three fails the gate at its named stage and cannot be masked; what the deep profile adds is that
the three stages are *invoked* there too. **A measured deep invocation plus the existing fast
mutation evidence is sufficient.** If the candidate SHA changes the control flow around lines
210-253 — introduces a conditional, moves an invocation, makes one profile-dependent — that
sufficiency lapses and the deep mutation runs become required.

---

## RE-MEASURED AFTER THE EIGHTH REVIEW — G2 IS NOW CAUSALLY DISCRIMINATING

The eighth review showed that the old G2 `ActionPayload` mutation failed both the named
type-string guard and a later verifier test. A gate that explicitly ignored the named guard's
status still failed later and satisfied every G2 predicate. That G2 could not establish that the
gate carried the named consumer's verdict.

The current G2 inserts a second, transposed `ActionPayload` string literal immediately before the
canonical runtime source definition. It is exported but unused, so the named type-string guard
sees a second source candidate while the runtime typehash and later tests stay unchanged. The
primary arm requires a named drift-or-duplication diagnostic, green eval-code and vendor-honesty
stages, and a top-level refusal. A fourth full run is its causal twin: the same duplicate source
string remains, but the gate changes only `check-type-strings.sh || fail=1` to `|| true`. The named
failure must still print and the otherwise-identical top-level gate must pass. `G2-causal`
combines those predicates and therefore fails if another stage independently keeps the gate red.

Current harness sha256:
`9da8d3295fecacf68312524080f77db3c35dcf34e308804d657c46bc1a37827e`. The full valid-output run
returned:

```
  REQUIRED : 7 of 7 held
  CONTROL  : 11 of 11 held
  exit 0
```

Supervisor outcomes are `0/5/0/5` for G1/G2/G2-causal/G3. All four retained logs contain one TS,
EC and VH banner. G1 and G2-causal contain one pass token and no failure/refusal token; G2/G3 each
contain one failure and one completion-refusal token and no pass token. The matrix contains 7
REQUIRED PASS, 11 CONTROL PASS and 3 OBSERVED rows, and no log contains a fatal Git diagnostic or
`ERR_MODULE_NOT_FOUND`.

This run still does not invoke `--gate`; the STATUS above remains authoritative and the eventual
post-repair verification must capture the three banners from a deep run at the exact candidate
SHA.

---

## RE-MEASURED AFTER THE SEVENTH REVIEW — FAIL-CLOSED EVIDENCE DESTINATION

The seventh review supplied an invalid advertised `A_EXTRACT_GATE_LOGDIR`. The old harness ran
all three gate cases before trying the destination, ignored the failed directory creation and log
copies, failed the matrix redirection, then still printed 7/7 REQUIRED, 10/10 CONTROL, its
completion token and exit 0. Evidence output was therefore best-effort while the interface and
result presented it as part of the run.

The current harness creates, resolves and write-probes the destination and validates all four
named outputs before `P3-provenance`, its first REQUIRED or CONTROL row. The final three copies
and matrix write are checked as well. `/dev/null/aextract-review8-output` now refuses at exit 2,
with zero REQUIRED and zero CONTROL rows and a named preflight diagnosis.

Then-current harness sha256:
`2d00ab31fb61956f2daf4128647203a971f220b7104cdff595987cb484153e61`. The paired valid-output
run wrote `g1.log`, `g2.log`, `g3.log` and `matrix.tsv` and returned:

```
  REQUIRED : 7 of 7 held
  CONTROL  : 10 of 10 held
  exit 0
```

Supervisor outcomes are `0/5/5`; every preserved log contains one TS, EC and VH banner. G1 has
one pass token and no failure/refusal token; G2/G3 each have one failure and one
completion-refusal token and no pass token. The matrix contains 7 REQUIRED PASS, 10 CONTROL PASS
and 3 OBSERVED rows. The same review's separate stale figure is corrected in §5: the current fast
harness measures **31**, not 28, REQUIRED failures (21 of 52 held).

This run still does not invoke `--gate`; the STATUS above remains authoritative and the eventual
post-repair verification must capture the three banners from a deep run at the exact candidate
SHA.

---

## RE-MEASURED AFTER THE SIXTH REVIEW — COMPLETE DEPENDENCY PREFLIGHT AND FAIL-CLOSED CLEANLINESS

The sixth review found that the fifth repair enumerated only two of the gate harness's three
copied dependencies. With valid Forge trees and an empty `ts/node_modules`, package-resolution
errors reached all three gate runs and the harness scored G1. The current preflight requires all
three trees to be non-empty before any REQUIRED or CONTROL verdict. The empty Node branch now
refuses at exit 2 with zero scored rows, matching the independently driven Forge-tree branches.

The same review showed that `Z-clean` could PASS when `git status` exited 128 because a pipeline
discarded Git's status and counted its empty stdout. The current control requires **status rc 0
and zero output lines**. Its isolated paired drive is clean `0/0 -> PASS`, dirty `0/1 -> FAIL`,
and broken status `128/1 -> FAIL`.

Then-current harness sha256:
`b8290f9931b540eb8a4dd381dfd9aaa43f143792a0cbdaef3d0c73bb24b8ff50`. A full isolated run at
`bb664c626d592d86391f644bf014e76f2bbf7db4` returned:

```
  REQUIRED : 7 of 7 held
  CONTROL  : 10 of 10 held
  exit 0
```

Supervisor outcomes are `0/5/5`. Each retained G1/G2/G3 log contains exactly one TS, EC and VH
banner. G1 contains one pass token and no fail/refusal token; G2 and G3 each contain one fail and
one completion-refusal token with no pass token. `Z-clean` records rc 0 and zero lines, and
`Z-signed` passes. The fast-profile binding result is unchanged.

This run still does not invoke `--gate`; the STATUS above remains authoritative and the eventual
post-repair verification must capture the three banners from a deep run at the exact candidate
SHA.

---

## RE-MEASURED AFTER THE FIFTH REVIEW — D-066

The fifth review found the empty-submodule preflight silently removed at `4f1e6a3`. The restored
loop covers both Forge dependency siblings before the first REQUIRED or CONTROL verdict. Paired
negative probes established each branch independently: empty `forge-std` refuses at exit 2 with
zero scored verdicts; with that sibling populated, empty `openzeppelin-contracts` does the same.

The then-current committed-content harness hash during that working state was
`e4141c166353c941a479fa730dfaaaff2089dbb17df697aeffeb666271189fd3`. Its full isolated run at
`bb664c626d592d86391f644bf014e76f2bbf7db4` returned:

```
  REQUIRED : 7 of 7 held
  CONTROL  : 10 of 10 held
  exit 0
```

The three supervisor outcomes remain rc `0/5/5`. G1 contains exactly one `GATE PASSED` and no
failure token; G2 and G3 each contain exactly one `GATE FAILED` and no pass token. Every one of
the three logs contains exactly one instance of each named TS, EC and VH stage banner. `Z-clean`
and `Z-signed` pass. The fast-profile binding is therefore unchanged by the preflight repair.

This run still does not invoke `--gate`; the STATUS above remains authoritative and the eventual
post-repair verification must capture the three banners from a deep run at the exact candidate
SHA.

---

## RE-MEASURED AGAIN AFTER THE FOURTH REVIEW — `F2-4` AND THE D-065 HARDENING

**Measured on the committed file, which recorded its own sha256 during the run:**

```
a-extract-gate.sh . bb664c626d592d86391f644bf014e76f2bbf7db4
gate harness sha256 b1d8d4d287d67045cb892e048788edcbbb171b07ea4ce36c2ddfdec24680f296

  REQUIRED : 7 of 7 held
  CONTROL  : 10 of 10 held
  exit 0
```

| Case | Kind | Verdict |
|---|:--:|:--:|
| `P3-provenance` | CONTROL | **PASS** — now verifies the clone's **WORKTREE** against the subject's tree, not just `HEAD` |
| `G1` | REQUIRED | **PASS** — unchanged gate prints `GATE PASSED` (rc=0) |
| `G1-stages`, `G1-order`, `G1-green` | CONTROL | PASS |
| `G2-mut`, `G2-scope` | CONTROL | PASS |
| `G2-named`, `G2-gate`, `G2-unmasked` | REQUIRED | **PASS** (rc=5) |
| `G3-mut`, `G3-scope` | CONTROL | PASS |
| `G3-named`, `G3-gate`, `G3-unmasked` | REQUIRED | **PASS** (rc=5) |
| `Z-clean`, `Z-signed` | CONTROL | PASS |

**Subject:** `bb664c626d592d86391f644bf014e76f2bbf7db4`, because `G1` requires the UNCHANGED gate to
pass and HEAD is deliberately red (`cefc135` applied `TESTS.patch` and ratcheted the verifier
floor). The exact-oid interface makes that choice explicit in the run's own identity block.

**What changed in this harness since the previous measurement:** seven of its ten git invocations
are pinned with `--no-replace-objects` (it was **0**); the other three cannot be reached by object
replacement. `P3-provenance` widened from a `HEAD` check to a whole-worktree tree comparison;
`GIT_TEMPLATE_DIR` is unset and `PATH` pinned by precedence under D-065(2).

## RE-MEASURED ON THE CURRENT FILE, AT A SUBJECT WHERE THE GATE IS GREEN

**Every figure below this section was carried from an earlier revision and at least one of them
was false. These are measured on the committed file.**

```
a-extract-gate.sh . bb664c626d592d86391f644bf014e76f2bbf7db4

  REQUIRED : 7 of 7 held
  CONTROL  : 10 of 10 held
  exit 0
```

**Subject choice, and why it is not a convenience.** `G1` requires the UNCHANGED gate to pass, and
HEAD is deliberately red — `cefc135` applied `TESTS.patch` and ratcheted the verifier floor, so the
suite and the fast gate fail by design. The measurement is therefore taken at
`bb664c626d592d86391f644bf014e76f2bbf7db4`, where the gate is green, and the exact-oid interface
makes that choice explicit in the run's own identity block rather than implicit in a ref.

| Case | Kind | Verdict |
|---|:--:|:--:|
| `P3-provenance` | CONTROL | **PASS** — the control whose assignment had been deleted; restored and now genuinely evaluated |
| `G1` | REQUIRED | **PASS** — unchanged gate prints `GATE PASSED` (rc=0) |
| `G1-stages`, `G1-order`, `G1-green` | CONTROL | PASS |
| `G2-mut`, `G2-scope` | CONTROL | PASS |
| `G2-named`, `G2-gate`, `G2-unmasked` | REQUIRED | **PASS** (rc=5) |
| `G3-mut`, `G3-scope` | CONTROL | PASS |
| `G3-named`, `G3-gate`, `G3-unmasked` | REQUIRED | **PASS** (rc=5) |
| `Z-clean`, `Z-signed` | CONTROL | PASS |

**`CONTROL` is 10, not 9, because `P3-provenance` is now counted** — under the counting bug a
failing control was not counted at all.

## A FALSE `PASS` IN THIS DOCUMENT, AND THE BUG THAT PRODUCED IT

**An independent review (`INSTRUMENT-REVIEW-3.md`, VERDICT FAIL) found that this file recorded a
`PASS` for a control that had printed `FAIL`.** Reproduced before fixing:

- the `_clone_head` assignment was **deleted** by the `4f1e6a3` edit — zero occurrences, while
  line 240 still read it. Under `set -u` that is an unbound variable;
- the command substitution producing the verdict therefore yielded an **empty string**;
- `check()` did arithmetic on it (`[ "$held" -eq 0 ]`, then `[ "$held" -ne 0 ]`), which errored
  with *integer expression expected* — so the case **printed FAIL and the failure was never
  counted**. The run reported its controls held and exited 0.

**That is a self-masking harness, and it would have swallowed any future control failure, not
just this one.** Three separate fixes, all applied: the assignment is restored; `check()` now
uses string comparison with **anything that is not a literal `0` counted as a failure**, in
**both** harnesses; and the false row in the table below is corrected rather than quietly
overwritten.

**Demonstrated, with a deliberately failing control injected into the gate harness:**

```
case DELIBERATE-EMPTY CONTROL FAIL   a control whose verdict is EMPTY, as an unbound variable produces
case DELIBERATE-FAIL  CONTROL FAIL   a control that plainly fails
ctl_fail=2 req_fail=0   -> would exit 2 (harness untrustworthy)
```

Before the fix the same injection produced `ctl_fail=0` and *"reports CONTROLS HELD and exits 0"*.

## THE SUBJECT IS NOW AN EXACT COMMIT OID — SUPERSEDES THE PARAGRAPH BELOW

**John's ruling on the second review closed `R1` structurally.** This harness now takes
`<repository-path> <exact-40-hex-commit>` and nothing else — no abbreviated ids, no branch, tag
or remote names, no `HEAD`, no `refs/…`, no revision expressions, no option-shaped input. Every
rejected shape exits 2 with **zero scored verdicts**. Existence and type come from
`git cat-file --batch-all-objects`, which performs no name resolution at all. Caller
configuration injection — `GIT_CONFIG_COUNT`, every enumerated `GIT_CONFIG_KEY_<n>` /
`GIT_CONFIG_VALUE_<n>`, and `GIT_CONFIG_PARAMETERS` — is scrubbed before the first git call.
**Instrument-local isolation only: this does not reopen Batch A1 and does not address its `R-C`
residual.** `P3-subject` is renamed `P3-provenance` and no longer claims independence between
git commands that share git's object resolver.

**The `7 of 7` / `10 of 10` figures below were measured before this narrowing.** Only the subject
grammar, the config scrub and that control's name and wording changed; no gate demonstration,
mutation or assertion was touched.

## SUBJECT RESOLUTION CORRECTED AGAIN AFTER AN INDEPENDENT REVIEW

This harness carried the same ambiguous-refname fail-open as `a-extract.sh` — `--verify` does not
refuse an ambiguous refname, and `--quiet` plus `2>/dev/null` hid git's warning. It now uses the
same two mechanisms (enumeration, and kept stderr) and refused at preflight with **zero scored
verdicts**. *(Both are superseded by the exact-oid grammar above; `P3-provenance` no longer
claims independence between git commands.)* Every bad-subject shape was re-confirmed to exit 2 with nothing scored.
**The `7 of 7` / `10 of 10` figures below were measured before this second correction; only the
resolution wiring changed, and that is stated rather than glossed.**

## RE-MEASURED ON THE CORRECTED REVISION

The earlier `7 of 7` / `9 of 9` figure was produced by the revision of `a-extract-gate.sh`
immediately prior to the subject-selection correction, which checked out `bb664c6` from a
hardcoded constant. **That revision's evidence is superseded here.** The corrected revision,
sha256 `b1d8d4d287d67045cb892e048788edcbbb171b07ea4ce36c2ddfdec24680f296`, was re-run end to end
through the new interface:

```
a-extract-gate.sh . bb664c626d592d86391f644bf014e76f2bbf7db4

  REQUIRED : 7 of 7 held
  CONTROL  : 10 of 10 held
  exit 0
```

**`CONTROL` moved 9 → 10 for exactly one reason: the new `P3-subject` control**, which asserts
the supplied oid is the commit the clone is checked out at. **It is a consistency control, not an independence proof.**
No case semantics changed and no verdict moved.

**MEASURED RESULT (fast profile, corrected revision `af66a45e…`):**

```
  REQUIRED : 7 of 7 held
  CONTROL  : 10 of 10 held
  exit 0 — FAST-PROFILE gate binding measured: the gate passes unchanged, fails at the named
           stage when a targeted A-EXTRACT fact is wrong, and that failure survives other
           consumers succeeding both before and after it. The DEEP portion of D-059(7) is
           NOT covered by this run.
```

| Case | Kind | Verdict | What it asserts |
|---|:--:|:--:|---|
| `G1` | REQUIRED | **PASS** | the unchanged fast gate prints `GATE PASSED`, never `GATE FAILED` (supervisor rc=0) |
| `G1-stages` | CONTROL | PASS | all three consumer stages are invoked by the gate, by name |
| `G1-order` | CONTROL | PASS | type-strings, then eval-codes, then vendor-honesty |
| `G1-green` | CONTROL | PASS | each of the three prints its own success line on the unchanged copy |
| `G2-mut` | CONTROL | PASS | the §5.8 mutation applied and nothing else in the subject changed |
| `G2-named` | REQUIRED | **PASS** | the failure appears **under the named banner** and names the type string |
| `G2-gate` | REQUIRED | **PASS** | `GATE FAILED`, never `GATE PASSED` (supervisor rc=5) |
| `G2-unmasked` | REQUIRED | **PASS** | the two LATER consumer stages report success and the gate still fails |
| `G2-scope` | CONTROL | PASS | targeted — the other two consumers stayed green |
| `G3-mut` | CONTROL | PASS | the §7.2 mutation applied; `docs/ablation-report.md` untouched |
| `G3-named` | REQUIRED | **PASS** | the failure appears under the vendor-honesty banner and names the artifact |
| `G3-gate` | REQUIRED | **PASS** | `GATE FAILED`, never `GATE PASSED` (supervisor rc=5) |
| `G3-unmasked` | REQUIRED | **PASS** | the two EARLIER consumer stages report success and the gate still fails |
| `G3-scope` | CONTROL | PASS | targeted |
| `Z-clean` | CONTROL | PASS | **0 changed paths** in the live repository's production boundary |
| `Z-signed` | CONTROL | PASS | `docs/gate-s2-evidence.md` byte-identical to `PRE_REPAIR_SHA` |
| `P3-provenance` (was `P3-subject`) | **see below** | **THIS ROW WAS FALSE** | at `4f1e6a3` the control's `_clone_head` assignment had been deleted; it printed **FAIL**, the counting bug then swallowed the failure, and this table recorded PASS. Corrected and re-measured — see *Re-measured after the third review*. |

**The gate's own exit status is recorded (`rc=0`, `rc=5`, `rc=5`) and used in no assertion.**
`rc=5` is the completion-token supervisor refusing a run that did not reach completion — a fact
about the supervisor, not a discriminator between findings.

---

## 1. The three stages, by the exact banner the gate prints

`scripts/test.sh` invokes all three A-EXTRACT consumers unconditionally, each under its own named
stage, in this order:

| Banner line / invocation line | Banner | Consumer |
|---|---|---|
| `scripts/test.sh:234` / `:235` | `== published EIP-712 type strings (D-023) ==` | `scripts/check-type-strings.sh` |
| `scripts/test.sh:237` / `:238` | `== §5.7.1 check coverage (D-031) ==` | `scripts/check-eval-codes.sh` |
| `scripts/test.sh:251` / `:252` | `== vendor honesty (§7.5 Gate 5, D-008) ==` | `scripts/check-vendor-honesty.sh` |

Each is invoked as `./scripts/<guard>.sh || fail=1`. **`fail` accumulates and is never reset**,
which is the mechanism G2 and G3 falsify rather than assume.

---

## 2. G1 — the UNCHANGED gate passes

```
$ ./scripts/test.sh            # in the isolated clone at bb664c6

== published EIP-712 type strings (D-023) ==
type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)

== §5.7.1 check coverage (D-031) ==
eval codes: 41/41 engine checks documented in §5.7.1 (D-031)

== vendor honesty (§7.5 Gate 5, D-008) ==
  ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it
…
GATE PASSED
```

**This is the control for everything below.** Without it, G2 and G3 would be satisfiable by a gate
that fails on this machine for an unrelated reason. Controls `G1-stages`, `G1-order` and
`G1-green` additionally assert that all three banners appear, in that order, each followed by its
own success line.

---

## 3. G2 — the FIRST consumer breaks, and its status edge is the cause

**Mutation:** insert an exported-but-unused, transposed `ActionPayload` string immediately before
the canonical `ACTION_TYPE` definition in `ts/src/signer/eip712.ts`. The pre-repair guard reads
the first candidate and reports drift; the repaired source-uniqueness guard must refuse the two
candidates. Runtime hashing still uses the untouched canonical definition. Control `G2-mut`
proves the insertion applied once and the proposal stayed byte-identical.

Primary arm:

```
== published EIP-712 type strings (D-023) ==
type strings: DRIFT in ActionPayload
  spec  : ActionPayload(…,bytes32 mandateHash,bytes32 policyHash,uint64 deadline)
  source: ActionPayload(…,bytes32 policyHash,bytes32 mandateHash,uint64 deadline)

== §5.7.1 check coverage (D-031) ==
eval codes: 41/41 engine checks documented in §5.7.1 (D-031)             ← LATER, GREEN

== vendor honesty (§7.5 Gate 5, D-008) ==
  ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it  ← AFTER, GREEN
…
GATE FAILED

GATE DID NOT REACH COMPLETION
  The body exited 1 without emitting its completion token.
```

- **`G2-named`** — the failure is under the named banner, names `ActionPayload`, and reports
  either pre-repair drift or repaired source duplication.
- **`G2-gate`** — the top-level gate prints `GATE FAILED` and never `GATE PASSED`.
- **`G2-unmasked`** — both later consumers are green in the same run and the gate still refuses.
- **`G2-scope`** — the unused duplicate moved only the type-string/source consumer.

**Causal twin:** copy that exact G2 subject and change only the named gate edge from
`./scripts/check-type-strings.sh || fail=1` to `|| true`. The same diagnostic must still print,
the eval-code and vendor-honesty consumers must remain green, and now the complete top-level gate
must print `GATE PASSED` with no failure or completion-refusal token. That is control
**`G2-causal`**. It rules out the defect found by Review 8: if any later stage independently
failed on this fixture, the causal twin would remain red and the control would invalidate every
verdict at exit 2.

---

## 4. G3 — the LAST consumer breaks; two EARLIER consumers cannot excuse it

**Mutation:** reword `§7.2`'s own caveat so the ablation report no longer carries §7.2's wording.
One line, proven applied by control `G3-mut`. `docs/ablation-report.md` is untouched, so the
A-062 generator stage is unaffected and the failure is attributable to the vendor-honesty guard.

```
== published EIP-712 type strings (D-023) ==
type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)     ← EARLIER, GREEN

== §5.7.1 check coverage (D-031) ==
eval codes: 41/41 engine checks documented in §5.7.1 (D-031)            ← EARLIER, GREEN

== vendor honesty (§7.5 Gate 5, D-008) ==
  ok    no artifact claims an executed or emulated vendor comparison (D-001, D-008(2))
  ok    no named vendor appears in any measurement artifact (D-008(4))
  FAIL  docs/ablation-report.md no longer carries §7.2's caveat:
…
GATE FAILED
```

- **`G3-named`** — the failure is under the vendor-honesty banner and names the artifact.
- **`G3-gate`** — `GATE FAILED`, never `GATE PASSED`.
- **`G3-unmasked`** — **two earlier consumer stages are green and do not excuse the later failure.**
- **`G3-scope`** — targeted; the other two consumers stayed green.

**Why both shapes are run.** G2 puts two successful consumers after its failure and adds the
causal bypass that attributes the refusal to its one status edge. G3 separately puts the failure
last, after two earlier successes. One shape would leave a different ordering assumed — which is
the shape of assumption this cycle exists to remove.

---

## 5. What this does NOT establish, stated rather than left to be assumed

- **FAST profile only.** `./scripts/test.sh --gate` (deep) is not run; it costs several minutes
  more per invocation and executes the corpus. **That the three consumer stages are unconditional
  in both profiles is a READING of `scripts/test.sh`, not a measurement here.** What WAS measured
  mechanically: the three invocations sit at `scripts/test.sh:235`, `:238` and `:252`, and between
  line 210 (where `PROFILE` is assigned) and line 253 there is **no `if`, `fi`, `else`, `case`,
  `esac`, `while`, `for` or `do` at column 0** — so nothing encloses them; the first
  `PROFILE`-dependent statement is at line 308. That is strong evidence and it is still a static
  reading rather than a deep-profile run, and this document declines to convert one into the
  other.
- **Nothing about whether the guards are RIGHT.** This shows the gate carries their verdict.
  Whether the verdict is sound is what `a-extract.sh` measures — and at `bb664c6` it measures 31
  REQUIRED failures.
- **These guards cover only their enumerated canonical facts** — six `§5.8` type strings,
  forty-one `§5.7.1` identifiers, one `§7.2` sentence, one `§2` table hash. **They are NOT general
  prose-consistency evidence** (D-058(6), D-059(7)).
- **The environment is this workstation's.** `forge`, `node` and an installed `ts/node_modules`
  are copied into the clone from the live tree. The gate under test is the committed one; the
  toolchain it runs against is local, and that is a disclosed dependency rather than a claim about
  CI.
- **THREE ATTEMPTS WERE DISCARDED BEFORE THE ONE REPORTED HERE, and all three are recorded rather
  than quietly re-run.** *(3)* The third was killed because **a CONTROL caught a bug in this
  harness itself**: `has()` was `printf '%s' "$big" | grep -qF …`, and `grep -q` exits at the
  first match, closing the pipe — `printf` then takes `EPIPE` and, under `set -o pipefail`, the
  pipeline returns non-zero **although the needle was found**. Against a 60 KB gate log,
  `G1-stages` reported FAIL beside a visible `printf: write error: Broken pipe` on a run whose
  gate had plainly printed all three banners. **The control did exactly what a control is for: it
  exited 2 and refused to let any verdict beside it be believed.** `has`/`has_re` now use
  `grep -c`, which consumes all of its input, in both this harness and `a-extract.sh`. *(1)* The first was started while `a-extract.sh` was still running — see the
  concurrency note below. *(2)* The second was killed because the harness file was EDITED WHILE IT
  WAS EXECUTING. `bash` reads a script incrementally, so an in-place edit can truncate a running
  body — the precise hazard `session-state.md` §0 records against `scripts/test.sh`, where the
  truncated body exited 0 with no diagnostic. The edit also invalidated the sha256 the run had
  already printed. **A run whose script changed under it is not evidence, whatever it printed**,
  so it was discarded rather than reported.
- **RUN IT ALONE. One attempt hung and is recorded rather than discarded.** The first attempt at
  this harness was started while `a-extract.sh` was still running. `scripts/test.sh`'s TypeScript
  suite starts a real signer process over a real socket, and under that concurrent load the test
  `reports status without revealing anything but the address` FAILED and the suite then hung with
  the signer process still alive; the run was killed and re-run with nothing else executing, and
  it passed. **That attempt is an environment artifact, not evidence about the gate** — but a
  falsification harness whose baseline can fail for an unrelated reason is exactly the thing this
  project's §0 warns about, so it is written down instead of quietly re-run. **Do not run this
  harness concurrently with anything that loads the machine.**
- **Gate exit status is used in no assertion.** `scripts/test.sh` runs under a completion-token
  supervisor with its own codes; the observed code is recorded in each case description as a fact.
  Every assertion is on the gate's OUTPUT.

---

## 6. Isolation and cost

- One `git clone --no-hardlinks --local` plus two `cp -R` from the live tree, all read-only with
  respect to the repository under test. `HOME`, `XDG_CONFIG_HOME` and the global/system git
  configuration are redirected into the scratch area; the scratch area is removed on exit.
- Control **`Z-clean`** asserts zero changed paths in the production boundary of the live
  repository when the run ends. Control **`Z-signed`** asserts `docs/gate-s2-evidence.md` is
  byte-identical to `bb664c6`.
- **Three full fast-gate runs.** Budget ten to twenty minutes and roughly 180 MB of scratch per
  subject. This is why gate binding is a separate harness: `a-extract.sh` runs in about two
  minutes and this does not.
- If `forge` or `node` is absent, or `ts/node_modules` or either submodule tree is absent or empty,
  the harness **exits 2
  as a preflight failure** rather than skipping. A check that cannot execute must never read as a
  check that passed.
