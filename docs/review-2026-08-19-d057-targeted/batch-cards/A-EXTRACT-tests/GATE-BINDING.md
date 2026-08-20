# A-EXTRACT — gate binding (D-059(7)), measured

> *"A standalone script that nothing invokes repeats the defect this work is trying to close.
> Required: invocation by the applicable fast and deep gate paths; a TOP-LEVEL falsification
> showing THE GATE fails when the targeted fact is wrong; an unchanged control showing the real
> gate passes; and an explicit statement that the guard covers only its enumerated canonical facts
> and is NOT general prose-consistency evidence."* — D-059(7)

**Harness:** `a-extract-gate.sh`, sha256
`af66a45ebf9dfe0501e4e1743b6662392126e82cd462dcc3f3a11c1009330746`.
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

## RE-MEASURED ON THE CORRECTED REVISION

The earlier `7 of 7` / `9 of 9` figure was produced by the revision of `a-extract-gate.sh`
immediately prior to the subject-selection correction, which checked out `bb664c6` from a
hardcoded constant. **That revision's evidence is superseded here.** The corrected revision,
sha256 `af66a45ebf9dfe0501e4e1743b6662392126e82cd462dcc3f3a11c1009330746`, was re-run end to end
through the new interface:

```
a-extract-gate.sh . bb664c626d592d86391f644bf014e76f2bbf7db4

  REQUIRED : 7 of 7 held
  CONTROL  : 10 of 10 held
  exit 0
```

**`CONTROL` moved 9 → 10 for exactly one reason: the new `P3-subject` control**, which asserts
the requested ref resolved to `SUBJECT_SHA` **and that the clone is actually checked out at it**.
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
| `P3-subject` | CONTROL | PASS | the requested ref resolved to `SUBJECT_SHA` and the clone is checked out at it |

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

## 3. G2 — the FIRST consumer breaks; two LATER consumers cannot mask it

**Mutation:** transpose `bytes32 mandateHash,bytes32 policyHash` in the one `ActionPayload`
publication inside `§5.8`. One line, proven applied by control `G2-mut`.

```
== published EIP-712 type strings (D-023) ==
type strings: DRIFT in ActionPayload
  spec  : ActionPayload(…,uint8 operation,bytes32 policyHash,bytes32 mandateHash,uint64 deadline)
  source: ActionPayload(…,uint8 operation,bytes32 mandateHash,bytes32 policyHash,uint64 deadline)
  A published type string that disagrees with the code is a confident wrong answer:
  a wrong type string and an invalid signature are indistinguishable at the output.

== §5.7.1 check coverage (D-031) ==
eval codes: 41/41 engine checks documented in §5.7.1 (D-031)          ← LATER consumer, GREEN

== vendor honesty (§7.5 Gate 5, D-008) ==
  ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it   ← LATER, GREEN
…
GATE FAILED

GATE DID NOT REACH COMPLETION
  The body exited 1 without emitting its completion token.
```

- **`G2-named`** — the failure is *under the named banner* and names `ActionPayload`. It is not
  merely somewhere in a 2000-line log.
- **`G2-gate`** — the top-level gate prints `GATE FAILED` and never `GATE PASSED`.
- **`G2-unmasked`** — **two later A-EXTRACT consumer stages report success in this same run and
  the gate still refuses.**
- **`G2-scope`** — the mutation is targeted: it moved the §5.8 stage and left the other two green.

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

**Why both directions are run.** "A later stage cannot clear an earlier failure" and "earlier
successes cannot excuse a later failure" are two properties. G2 shows the first, G3 the second. A
single direction would demonstrate only one and leave the other assumed — which is the shape of
assumption this whole cycle exists to remove.

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
  Whether the verdict is sound is what `a-extract.sh` measures — and at `bb664c6` it measures 28
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
- If `forge`, `node`, `ts/node_modules` or either submodule tree is absent, the harness **exits 2
  as a preflight failure** rather than skipping. A check that cannot execute must never read as a
  check that passed.
