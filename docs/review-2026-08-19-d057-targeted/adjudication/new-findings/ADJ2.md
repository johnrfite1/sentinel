# ADJ2 — adjudication of three new findings: `N-SCOPE-CD`, `N-EVAL-ACTION-TARGET`, `N-DECODE-E4`

**Authority:** D-058(7) — *"Adjudicate each new item first and classify it as confirmed, refuted,
duplicate, historical, or a decision fork."*

**Adjudicator:** independent. I reported none of these findings and authored none of the code or
prose under examination.

**Frozen commit:** `a18e6e61598a996d962798ad0353a166232d4490`, confirmed by `git rev-parse HEAD`
in my worktree before the first probe and again after the last. The worktree is restored:
`git status --porcelain` shows only the untracked `ts/node_modules`, and `git diff --stat` is
empty.

**Instrument hygiene.** Every sweep used `/usr/bin/grep`, never the shell's `ugrep` wrapper. The
wrapper was caught failing on this machine in a prior cycle. Before trusting any zero result I
planted a canary (`ZZQCANARY7788` into `docs/session-state.md`, `ZZQCANARY9911` into
`ts/test/evaluate.checks.test.ts`), confirmed `/usr/bin/grep -rn` found each, and reverted.

**Standing evidence bound.** The Solidity artifacts are not built in this worktree and the
Foundry submodules are not provisioned, so any TypeScript test requiring a deployed rig fails for
that reason and not for a defect. I confined my probes to surfaces that need no Solidity build —
the shell guards, `ts/test/evaluate.checks.test.ts`, `ts/src/**`, and `verifier/verify.py` against
the committed `fixtures/samples/`. Where that bounds a conclusion I say so at the point it bites.
Scratch paths below are written `<SCRATCH>`.

**Summary**

| Finding | Reporter's rating | Classification | My severity |
|---|---|---|---|
| `N-SCOPE-CD` | MEDIUM (V2) | **CONFIRMED** — and **DISTINCT** from `V3-N1`, not a duplicate | **LOW** (down from MEDIUM) |
| `N-EVAL-ACTION-TARGET` | LOW (V4) | **CONFIRMED** — cosmetic; same class as `R3-F4`, a new instance, not a duplicate | **LOW**, at the floor of it |
| `N-DECODE-E4` | unrated (V4) | **CONFIRMED IN PART** — one half of the sentence is false, the other half is true and deliberate | **MEDIUM**, with the risk direction inverted from the usual |

---

# 1. `N-SCOPE-CD` — `scripts/check-review-scope.sh:47`, the unguarded `cd`

## 1.1 The exact claim at issue

That `cd "$(git rev-parse --show-toplevel)"` at line 47 has no guard; that an empty command
substitution makes `cd ""` a silent successful no-op rather than an error; and that the script
therefore proceeds against whatever directory it was started in — which, from `contracts/`,
produces a **false diagnostic naming 13 files as unassigned that are in fact assigned under their
real paths**.

## 1.2 The authoritative source

`scripts/check-review-scope.sh` itself. Code beats prose here, and the question is settled by
three constructs: line 47's unquoted-result `cd`, the `assign()` `case` at lines 59-94 whose arms
are all rooted at the repository top level, and the `git ls-files` guards at lines 106-117 that
`V3-N1` installed.

## 1.3 Reproduction

### Sub-claim A — `cd ""` is a silent no-op

```
$ bash --version | head -1
GNU bash, version 3.2.57(1)-release (arm64-apple-darwin25)
$ bash -c 'set -uo pipefail; cd /etc; cd ""; echo "rc=$?"; echo "pwd=$PWD"'
rc=0
pwd=/etc
$ bash -c 'set -euo pipefail; cd /etc; cd ""; echo "survived set -e, rc=$?, pwd=$PWD"'
survived set -e, rc=0, pwd=/etc
```

**Confirmed, and worse than the script's own `set -uo pipefail` would suggest**: the no-op
survives even `set -e`, so tightening the shell options would not close it.

### Sub-claim B — the wrong-directory diagnostic

A PATH shim at `<SCRATCH>/stub/git` execs the real binary for every call except the one
sabotaged, selected by `GIT_STUB_MODE`. I used a **stricter** sabotage than the reporter did:
`toplevel_empty` returns exit **0** and prints nothing at all, so there is not even a stray
`fatal:` on stderr. This is the worst case, not a representative one.

**Control D — shim transparency, sabotage off, from `contracts/`:**

```
$ PATH="<SCRATCH>/stub:$PATH" GIT_STUB_MODE=passthru ../scripts/check-review-scope.sh
review scope: R1=266  R2=46  R3=151  (assigned 463 of 463 tracked files)
  remediation surface: 73 file(s) changed since A-070's parent, all assigned
  preservation-only:   79 file(s) ...
rc=0
```

The shim is transparent, so any refusal below is caused by the sabotage and not by the shim's
presence.

**Probe B — sabotage on, from `contracts/`:**

```
$ PATH="<SCRATCH>/stub:$PATH" GIT_STUB_MODE=toplevel_empty ../scripts/check-review-scope.sh
review scope: R1=0  R2=0  R3=0  (assigned 0 of 13 tracked files)
  FAIL  13 tracked file(s) assigned to NO reviewer:
    foundry.toml
    lib/forge-std
    lib/openzeppelin-contracts
    src/SentinelVault.sol
    src/demo/DemoERC20.sol
    src/demo/DemoPay.sol
    src/types/SentinelTypes.sol
    test/SentinelTypes.t.sol
    test/SentinelVault.backstops.t.sol
    test/SentinelVault.binding.t.sol
    test/SentinelVault.invariants.t.sol
    test/SentinelVault.t.sol
    test/TypesHarness.sol
  The claims surface is covered by this partition or it is not covered. Assign them.
rc=1
```

**Exactly 13, exactly as reported.** Every one of those files *is* assigned — as
`contracts/foundry.toml`, `contracts/src/SentinelVault.sol`, and so on, by the `contracts/*` arm
at line 84. The mechanism is that `git ls-files` is cwd-scoped and emits cwd-relative paths,
while every `assign()` arm is rooted at the top level. `git diff --name-only` (the script's other
input, line 168) is **not** cwd-scoped, so the second half of the script would have been
unaffected — but it is never reached.

**Control C — same sabotage, from the repository root:**

```
$ PATH="<SCRATCH>/stub:$PATH" GIT_STUB_MODE=toplevel_empty ./scripts/check-review-scope.sh
review scope: R1=266  R2=46  R3=151  (assigned 463 of 463 tracked files)
  remediation surface: 73 file(s) changed since A-070's parent, all assigned
rc=0
```

Correct output, reached by luck: the cwd already **was** the top level, so the no-op cost
nothing. This is the paired control that distinguishes "the `cd` is defective" from "the shim
breaks everything".

## 1.4 The question the reporter left open: fail-closed, or fail-open?

This is the part that decides severity, so I measured it rather than reasoning about it. I
enumerated all 61 directories containing tracked files and ran the sabotaged script from each:

```
$ git ls-files | sed 's#/[^/]*$##' | sort -u   (+ ".")   ->  61 directories
   dirs where the sabotaged run exited 0:  1
   dirs where the sabotaged run exited 1: 60
   the single rc=0 dir is "." — and its output is the CORRECT one
```

**It is fail-closed everywhere, and fail-open nowhere.** There is no starting directory from
which the defeated `cd` yields the prohibited shape — `all assigned`, exit 0 — over a tree that
was not measured. The `assign()` catch-all at line 92 is what saves it: cwd-relative paths from
any subdirectory miss every arm and land in `UNASSIGNED`, and an empty `git ls-files` (an
untracked subdirectory) is caught separately by the line 113 guard.

**This is materially different from `V3-N1`**, which the adjudication records as FAIL precisely
because line 198's swallowed `git ls-files --error-unmatch` *is* fail-open: it prints
`0 file(s) changed since A-070's parent, all assigned`, exit 0.

## 1.5 Reachability without a shim — three negative results

Every natural route I could construct that empties `$(git rev-parse --show-toplevel)` **also**
breaks `git ls-files`, and the `V3-N1` guards catch it:

| Route | `show-toplevel` | Script's behaviour |
|---|---|---|
| cwd outside any repository | `fatal: not a git repository`, empty | `FAIL git ls-files failed:` + git's own stderr, rc=1 |
| `git` absent from `PATH` | `command not found`, empty | `FAIL git ls-files failed:` + the same, rc=1 |
| `GIT_DIR` pointing at a **bare** repository | `fatal: this operation must be run in a work tree`, empty | `git ls-files` returns rc=0 and **empty**; caught by the line 113 emptiness guard, rc=1 |

The third is the interesting one and the reason I looked for it: it is the only natural
configuration I found where `rev-parse --show-toplevel` fails while `git ls-files` **succeeds**.
It is still caught, by the emptiness guard rather than the failure guard — which is `V3-N1`'s
repair earning its keep on a route nobody wrote it for.

I also checked `GIT_DIR` set to a non-bare repository with no `GIT_WORK_TREE`: `show-toplevel`
returns the cwd rather than failing, so the `cd` succeeds and nothing is defeated.

## 1.6 DUPLICATE of `V3-N1`, or DISTINCT? — **DISTINCT**

The reporter filed this under `V3-N1`'s banner, as their residual R-1. I do not accept that
placement, for three reasons:

1. **Different construct.** `V3-N1` as adjudicated is about `git ls-files` call sites — "guarded
   two of three". Line 47 is neither: it is `git rev-parse --show-toplevel` consumed by `cd`. A
   sweep that enumerated every `git ls-files` in the file and guarded all three would leave line
   47 untouched.
2. **Opposite failure direction.** `V3-N1`'s live half is fail-open and reproduces the exact
   prohibited sentence. This is fail-closed at 60 of 61 starting directories and correct at the
   61st. Calling them one finding would let a fail-closed diagnostic defect inherit a fail-open
   defect's severity, which is the wrong way round.
3. **Different remedy.** `V3-N1` needs the `|| continue` at line 198 to stop meaning two things.
   This needs one line: capture, test for empty, refuse.

They do share `R1-F2`'s **argument** — *a coverage instrument must never report coverage it did
not measure* — read at its widest. That is a reason to fix both in one pass. It is not a reason
to call them one finding.

## 1.7 Severity — **LOW**, down from the reported MEDIUM

The reporter rated MEDIUM but themselves excluded it from their verdict and filed it as a
residual, which I read as agreeing that it is not load-bearing. Downward:

- It never reports coverage it did not measure. The instrument's core promise holds.
- The false file list arrives under a header reading `assigned 0 of 13 tracked files` against a
  repository of 463 — a distress signal loud enough that "a maintainer adds wrong arms to the
  partition" requires them to ignore both the count and the exit status.
- Under every natural route (as opposed to my deliberately silent shim) git's own `fatal:`
  message is printed to stderr first.
- Nothing invokes this script automatically — confirmed by sweep; it is a dispatch-time check run
  by hand, so a human is present to read the diagnostic.

Upward, and why it is not INFO: the message names specific files and instructs the reader to
"Assign them", which is a concrete wrong corrective action, and the script's own header makes
much of the partition being executable rather than asserted.

## 1.8 What this evidence does and does not establish

**Establishes:** line 47 is unguarded; `cd ""` no-ops silently even under `set -e`; from
`contracts/` the defeated `cd` produces the reported 13-file false diagnostic verbatim; the
failure is fail-closed at 60 of 61 tracked directories and correct at the 61st; every natural
route to an empty substitution is caught by the `git ls-files` guards.

**Does not establish:** that any live route reaches line 47's defect today without a targeted
PATH shim — I found none. Does not establish anything about a bash other than the 3.2.57 that
`#!/usr/bin/env bash` resolves to here. Does not re-adjudicate `V3-N1`, which I did not re-probe.

## 1.9 Classification — **CONFIRMED** (distinct from `V3-N1`; severity LOW)

---

# 2. `N-EVAL-ACTION-TARGET` — a code name that does not exist

## 2.1 The exact claim at issue

That `ts/test/evaluate.checks.test.ts` cites `EVAL_ACTION_TARGET_MATCHES_MANDATE`, a code that
exists nowhere else in the tree, while the assertion below it uses the real code
`EVAL_TARGET_BOUND`.

## 2.2 The authoritative source

`ts/src/evaluate/checks.ts`'s `EVAL_CODES` array is what *defines* the code set — it is what
`scripts/check-eval-codes.sh` reads and what the test file's own exhaustiveness assertion runs
against. The test file is the surface making the citation.

## 2.3 Deriving the defined set and diffing it

Mechanically, not from the finding:

```
$ sed -n '/^export const EVAL_CODES = \[/,/^\] as const;/p' ts/src/evaluate/checks.ts \
    | /usr/bin/grep -oE '"EVAL_[A-Z0-9_]+"' | tr -d '"' | sort -u        ->  41 codes
$ /usr/bin/grep -oE '\bEVAL_[A-Z0-9_]+\b' ts/test/evaluate.checks.test.ts | sort -u ->  43 names

CITED but NOT DEFINED:
    EVAL_ACTION_TARGET_MATCHES_MANDATE
    EVAL_CODES                            <- the array identifier itself, a regex artefact

DEFINED but not cited in this file:  0
```

**Exactly one orphan.** The zero on the reverse direction is the control that the sweep is
discriminating rather than merely name-hunting: all 41 defined codes are cited here, so the diff
is measuring citation fidelity and not coverage.

Widening to the whole tree with the three frozen review-record directories excluded, the other
apparent orphans all resolve to deliberate constructs and none is a fabricated *check* name:
`EVAL_FABRICATED_EXTRA_CODE` and `EVAL_SUBSTITUTED_CODE` in `verifier/verify.py` are tamper-mode
payloads; `EVAL_SOMETHING_ELSE`, `EVAL_NO_INJECTION_DETECTED`, `EVAL_PURPOSE_CONFORMS`,
`EVAL_OK`, `EVAL_HAS A SPACE` are negative-test inputs; `EVAL_PURCHASE_RESOURCE_TYPO` is a mutant
string in `scripts/mutate.sh`; `EVAL_CODES` and `EVAL_EXECUTABILITY_CODES` are identifiers. The
`R3-F4` pair `EVAL_VAULT_TARGET_NOT_ALLOWED` / `EVAL_VAULT_SELECTOR_NOT_ALLOWED` survives only
inside `docs/decisions.md`'s A-078 entry, which is the marked historical record — consistent with
the standing `R3-F4` HOLD, which I therefore did not disturb.

**`EVAL_ACTION_TARGET_MATCHES_MANDATE` is the sole unexplained fabricated code name in
maintained, non-historical material.**

## 2.4 Comment, test name, or assertion? — **comment**

`ts/test/evaluate.checks.test.ts:500-511`. Line 500 is the test name and contains no code. Line
502 is a `//` comment. The assertion at 504-510 passes the real `"EVAL_TARGET_BOUND"` to
`outcomeOf`. The file runs green:

```
$ node --test --test-concurrency=1 test/evaluate.checks.test.ts
ℹ tests 121   ℹ pass 121   ℹ fail 0
```

**Control — is the code string in the assertion load-bearing?** I substituted the fictitious name
into the assertion at line 507 and re-ran:

```
actual:   'ABSENT'
expected: 'PASS'
code:     'ERR_ASSERTION'
```

So a fictitious code in the **assertion** position fails loudly and immediately. The defect is
confined to the comment, where nothing looks.

**Control — does anything catch a fabricated name in a comment?** I planted
`EVAL_TOTALLY_MADE_UP_ZZQ` at line 502 and ran every guard:

```
check-class-coverage 0   check-eval-codes 0        check-findings-ledger 0
check-gate-immutability 0 check-label-integrity 0  check-label-prompt 0
check-rename-gate 0      check-review-scope 0      check-secrets 0
check-suite-floors 0     check-type-strings 0      check-vendor-honesty 0
```

All twelve pass. `scripts/check-eval-codes.sh` is code-to-spec directional — it asks whether every
*defined* code is documented in §5.7.1 — and is structurally blind to a *cited* name that is not
defined. Both mutations were reverted; the tree is clean.

## 2.5 Same class as `R3-F4`? — yes; DUPLICATE of it? — no

Same class: a maintained text names an enforcement/check code that does not exist. Distinct
instance, and materially weaker:

| | `R3-F4` | this |
|---|---|---|
| Site | the inert-fields **disclosure** — a reader-facing enforcement pointer | a `//` comment inside a test |
| Function of the text | *is* the claim; the pointer is the whole payload | explains an assertion printed correctly two lines below |
| Propagation | reached the **signed S2 pack** | one occurrence, nowhere else |
| Reader's recourse | none — the code cannot be looked up | the real code is on the adjacent line |

`R3-F4`'s repair could not have covered this: different name, different file, and no mechanical
guard exists in this direction, which I proved above rather than inferred.

Provenance: `git log -S` puts its introduction at `3031c34` (A-076), the pre-review stabilization
checkpoint — i.e. it was introduced by the same remediation cycle that produced `R3-F4`, which is
the reporter's point and is correct.

## 2.6 Severity — **LOW**, at the floor of it

The reporter's LOW is right. I would not go lower than LOW only because this repository has
recorded a fabricated code name propagating into a signed pack once already, and because there is
provably no instrument that would catch the next one.

## 2.7 What this evidence does and does not establish

**Establishes:** the name is defined nowhere; it occurs exactly once in maintained material; it
is in a comment and not in a test name or an assertion; the adjacent assertion uses the real code
and the file passes 121/121; a fictitious code in the assertion position would fail immediately;
no guard in the repository catches this class.

**Does not establish:** anything about whether `EVAL_TARGET_BOUND` is the *right* check for the
case described — I checked citation fidelity, not semantics. Does not re-adjudicate `R3-F4`.

## 2.8 Classification — **CONFIRMED** (cosmetic; new instance of the `R3-F4` class, LOW)

---

# 3. `N-DECODE-E4` — "checked by NEITHER the signer nor the verifier"

## 3.1 The exact claim at issue

`ts/src/decode/index.ts:189-201`, the docstring of `decodeBySelector`, states as current fact:

> the §5.6 bundle "also carries `normalizedAction` and `expectedEffects`, and those are checked by
> **NEITHER the signer nor the verifier** — the receipt's `evidenceHash` commits to them, so they
> are tamper-evident, but **nothing compares them to the action and the mandate they purport to
> describe. A bundle can therefore state expected effects that its own action does not imply and
> still verify.**"

and, four lines further down:

> "Whether the SIGNER should compare them is a D-014 question… Whether the VERIFIER should is
> cheaper and needs no ruling… **Both are open (v1.1 register)**."

Per the brief I treated the signer clause and the verifier clause as separate factual claims, and
I read the code rather than any prose — including the register.

## 3.2 The authoritative sources

`verifier/verify.py` for the verifier clause; `ts/src/signer/attest.ts` and `ts/src/signer/*` for
the signer clause. `docs/v1-1-register.md` is prose and decides nothing here; I checked it only to
see whether the record agrees with the code.

## 3.3 The verifier clause — **FALSE**

`verifier/verify.py:1434` `_evidence_describes_the_bundle(evidence, action, mandate, policy)`
checks both fields:

- `:1462-1479` — `normalizedAction` must be present and an object, and must restate **every**
  `eip712.ACTION_FIELDS` field of the §5.3 action; each mismatch is named.
- `:1481-1492` — `keccak256(normalizedAction.callData) == action.dataHash`, so the field-by-field
  agreement cannot be satisfied while the bytes say something else.
- `:1523-1573` — `expectedEffects` must be present and an object; six fields
  (`target`, `selector`, `resourceId`, `beneficiary`, `durationSeconds`, `recurringAllowed`) must
  equal the mandate's; `maxAllowanceIncreaseBaseUnits` must equal the policy's; and
  `maxNativeValueWei` must equal the **§5.2 intersection**, `min(mandate, policy)`.

It is called from **both** verification paths — `:911` in `_refusal_checks` and `:1629` in
`_chain_checks` — so it does not run only on the path a reviewer probed.

### Reproduction, with a full cross-discrimination control matrix

Against a scratch copy of `fixtures/samples`, invoked the way `scripts/test.sh:785` invokes it
(`--domain fixtures/samples/domain.json`). No Solidity build is required for any of this.

**Control 0 — untouched, all samples:** `7/7 sample(s) verified`, and on `case-1-allow` both
projection checks and the callData-derivation check read `[PASS]`.

| Probe on `case-1-allow` | `normalizedAction` restates the action | `keccak256(callData)==dataHash` | `expectedEffects` projects §5.1/§5.2 |
|---|---|---|---|
| **Control 0** untouched | PASS | PASS | PASS |
| **Control A** `expectedEffects.beneficiary` re-spelled to its EIP-55 checksum — *same value* | PASS | PASS | **PASS** |
| **P1** `expectedEffects.beneficiary` → a different address | PASS | PASS | **FAIL** |
| **P2** `normalizedAction.valueWei` → `123456789` | **FAIL** | PASS | PASS |
| **P3** `normalizedAction.callData` last byte flipped | PASS | **FAIL** | PASS |

Control A is the load-bearing one: a same-value-different-spelling edit breaks the RFC 8785
recanonicalization and the hash chain, and **both projection checks still PASS**. So the FAILs in
P1/P2/P3 are caused by the specific mismatch and are not an echo of "the bundle was touched, so
everything failed". P1 versus P2 versus P3 further shows the three checks are independent of each
other rather than one check reported three times.

**The refusal path, separately, because the comment's claim is unconditional:**

```
CONTROL  refusal-vault-paused untouched          -> expectedEffects projects ... [PASS], => PASS
PROBE    expectedEffects.durationSeconds 86400 -> 999999
         evidence.normalizedAction restates the §5.3 action ......... [PASS]
         keccak256(evidence.normalizedAction.callData) == dataHash ... [PASS]
         evidence.expectedEffects projects the §5.1/§5.2 documents ... [FAIL]
         => FAIL
```

**The verifier compares both fields, on both paths, and discriminates correctly.** The clause "nor
the verifier" is false, and so is "nothing compares them to the action and the mandate they
purport to describe": `normalizedAction` is compared to the action twelve fields wide plus the
calldata digest, and `expectedEffects` is compared to the mandate and the policy.

### When it became false

`git log` puts the docstring's last edit at `c2fc8d2` (A-068) and shows it untouched since.
`_evidence_describes_the_bundle` was introduced at `78ac9cb` (A-069) — **the immediately
following commit**, confirmed by `git merge-base --is-ancestor` — and extended at `caad4c1`
(A-074) and `a89c255` (A-070). The comment has therefore been false for the whole of the interval
in which it has stood, i.e. since the next action after it was written.

### The register agrees with the code, and with neither of the comment's two claims about openness

`docs/v1-1-register.md` §13.4's `E4` row reads **"VERIFIER HALF BUILT (A-069, absence-is-agreement
repaired by A-070) · SIGNER HALF DELIBERATELY NOT BUILT (D-014) — not an open defect"**. So the
docstring's "Both are open (v1.1 register)" is false in **both** directions: the verifier half is
built, and the signer half is not open — it is a ruled-on design choice. This is a second false
sentence in the same docstring, in a paragraph that cites the register as its authority.

## 3.4 The signer clause — **TRUE, and deliberate**

Distinguished carefully per the brief, because D-014 kept conformance out of the signer on
purpose and a "repair" here would be an unauthorized product change.

- A canary-verified `/usr/bin/grep` for `normalizedAction|expectedEffects` across all of `ts/src`
  returns exactly three hits: `ts/src/evaluate/index.ts:97` and `:147`, where the evaluator
  **constructs** them, and `ts/src/decode/index.ts:191`, the comment itself. **Neither name occurs
  anywhere in `ts/src/signer/`.**
- The signer's only structural read of the bundle is `ts/src/signer/attest.ts:637`,
  `(JSON.parse(evidenceCanonical) as Record<string, unknown>).decodedSelectorAndParameters`. Its
  only other uses of `evidenceCanonical` are `hashUtf8(...)` at `:302` and `:554` — commitment,
  which the comment already concedes — the parameter declaration at `:632`, and
  `ts/src/signer/protocol.ts:786`'s well-formedness check on the string. There is no generic
  iteration over the bundle, so there is no path by which the signer could compare a field it
  never names.

`verifier/verify.py:1619` states the same thing from the other side — "Neither the signer (D-014
deliberately keeps conformance out of it) nor this verifier looked" — but there it is written in
the **past** tense as the defect A-069 closed, immediately above the call that closes it. That is
an honest historical frame. The decode docstring's is present tense with no date, beside a live
function, and is not.

**Evidence bound, stated because it bit:** I attempted a behavioural probe of the signer half —
renaming `expectedEffects` in the evaluator's bundle and running `ts/test/signer.e2e.test.ts` — and
it could not run: `Run the Solidity build first`, from `ts/test/harness.ts:82`, because the Foundry
artifacts are absent in this worktree. My conclusion on the signer half therefore rests on the
code reading and the canary-verified name sweep, not on an executed end-to-end probe. I judge that
sufficient — a field that appears nowhere in the signer's source and is never generically iterated
cannot be compared by it — but the distinction is recorded rather than glossed.

## 3.5 Exactly which parts are false

| Clause | Verdict |
|---|---|
| "`normalizedAction` and `expectedEffects` … checked by **NEITHER the signer**" | **TRUE** — and deliberate under D-014 |
| "**nor the verifier**" | **FALSE** since A-069 |
| "the receipt's `evidenceHash` commits to them, so they are tamper-evident" | **TRUE** |
| "**nothing compares them** to the action and the mandate they purport to describe" | **FALSE** — `verify.py:1462-1492` and `:1523-1573` |
| "A bundle can therefore state expected effects that its own action does not imply **and still verify**" | **FALSE** as written |
| "Both are open (v1.1 register)" | **FALSE** in both directions |

**The one narrow residue of truth in the "still verify" sentence**, stated so the correction does
not overshoot: `expectedEffects` is compared to the **mandate and policy**, not directly to the
action. On an **ALLOW** bundle the action-to-mandate link is closed separately by
`_allow_conforms_to_the_mandate` (`verify.py:1521`, gated `verdict != "ALLOW" -> return` at
`:1364`), so the binding is transitively complete there. On a BLOCK or REVIEW bundle that link is
deliberately absent — `verify.py:1365`, *"BLOCK and REVIEW bundles are legitimately nonconforming
and MUST stay verifiable"* — so on those paths `expectedEffects` is bound to the mandate but not
to the action. That is by design and is not what the sentence claims; the sentence claims nothing
compares them at all.

## 3.6 Not HISTORICAL

I considered `HISTORICAL` and reject it. The passage is undated, present tense, sits in the
docstring of a live exported function, and its third paragraph makes a claim about *current*
register state ("Both are open"). Contrast `verifier/verify.py:1615-1621`, which says the same
thing in the past tense as a record of what A-069 fixed — that one is properly historical and I
would not flag it.

## 3.7 Severity — **MEDIUM**, with the risk direction inverted

Higher than the LOW I would give a stale comment, because:

- It stands on the surface that carries D-014's justification chain. `verify.py:1501-1509` records
  that D-014's stated ground — carried into the **signed Gate S1 pack** at
  `docs/gate-s1-evidence.md:124` and `:152` — is that a wrong-purpose ALLOW is detectable after the
  fact by the D-010 verifier. A comment asserting the verifier does not look attacks the premise
  of a signed gate's reasoning while the code satisfies it.
- It is the `R2-F4` / `A-063` shape: the correction filed in the register, the falsehood left
  standing at the site a reader actually reaches. This repository has now recorded that shape
  repeatedly.

Lower than HIGH, and the direction is worth naming because it is unusual here: this comment
**understates** the product's guarantees. It does not induce false confidence in a protection that
is absent; it induces false alarm about a protection that is present. The realistic harm is
wasted or duplicated work — someone rebuilding `_evidence_describes_the_bundle`, or reopening a
fork the register records as decided — and a reader's loss of trust in the codebase's own
comments. No verification outcome is wrong because of it.

## 3.8 What this evidence does and does not establish

**Establishes:** the verifier compares both fields, on both verification paths, with a control
matrix distinguishing each check from the others and from generic bundle breakage; the comment has
been false since the commit immediately after it was written; the register records the same thing
the code does; the signer genuinely does not check either field and never names them; the
"Both are open" sentence is independently false.

**Does not establish:** anything about whether the verifier's projection checks are *sufficient* —
I probed that they fire on mismatches, not that their field lists are complete against §5.6. Does
not establish the signer half by execution (Solidity build absent; see 3.4). Does not establish
that a fully self-consistent tampered bundle — re-canonicalised, re-hashed and **re-signed** —
fails; my probes broke the hash chain as a side effect, which the Control A row is designed to
neutralise but does not wholly replace. Nothing here bears on whether Sentinel *decides*
correctly.

## 3.9 Classification — **CONFIRMED IN PART**

Confirmed as to the verifier clause, "nothing compares them", "still verify", and "Both are open".
**Refuted as to the signer clause**, which is true and is a ruled design position under D-014 and
must not be "repaired" into a signer-side conformance check.

**No decision fork attaches.** Repairing this is a factual correction of a comment to match code
that already exists and a register entry that already records it. Nothing about what the product
guarantees changes. The one thing a repairer must not do is read "the signer does not check them"
as a defect to close: D-014 decided that, and the correct comment says so.

---

# 4. Scope note

Adjudication only. I repaired nothing, signed nothing, and resolved no fork. My worktree is
restored to `a18e6e6` with an empty `git diff --stat`; the only untracked path is
`ts/node_modules`. `scripts/check-review-scope.sh` runs clean on the restored tree
(`463 of 463`, exit 0) and `ts/test/evaluate.checks.test.ts` runs 121/121, which is my closing
evidence that every probe mutation was reverted.
