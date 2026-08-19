# Round six — the adjudicated list, for John

**Run:** 2026-08-18, frozen `140c59e`, nine independent reviewers in nine detached worktrees,
each with its own evidence directory, each briefed to prove the work fails.
**Status: NOT ACTED ON.** Per D-051(c) this is brought to you without remediation. Whether the
round is CLEAN under D-047 is your judgement, and D-047 forbids me re-authoring it.

**91 findings across nine lenses.** This document separates what I reproduced myself from what
I am relaying on a reviewer's evidence. That split is the point of the adjudication step.

---

## 0. The headline, in one line

**Round six is not clean on any reading**, and the reason is not marginal: several findings sit
inside text you personally certified or signed, and three sit inside repairs made in the last
48 hours.

---

## 1. Did the round meet its own ratified definition? — NO, and this is a finding about the round

D-050(1) requires nine surfaces each covered by a reviewer that ran its own baseline, plus two
conditions. All nine surfaces were covered and all nine returned coverage statements. **But
condition 1 — at least one reviewer able to run the DEEP profile — was met only by accident.**

`docs/round-six-brief.md` states the deep-profile blocker is **"SOLVED 2026-08-17 (A-066)"**.
A-066 solved the *socket* half. It did not solve, and did not consider, this:

**Reproduced by me, both directions, clean rebuild (decisive):**

| worktree `contracts/lib/*` | forge remappings | DemoPay deployed bytecode |
|---|---|---|
| **symlinks** (what `session-state.md` §1 step 1 prescribes) | **4** | **differs from live tree** |
| **real directories** | **5** | **byte-identical to live tree** |

The missing entry is `@openzeppelin/contracts/=lib/openzeppelin-contracts/contracts/`. It goes
into solc's `settings.remappings` → the CBOR metadata → `targetCodeHash` → all 50 committed view
digests mismatch → deep gate fails. The two builds are byte-identical for the first 617 bytes and
differ only in the trailing metadata digest.

**So the prescribed provisioning makes the ratified condition unmeetable.** Five lenses hit this
independently (1, 3, 7, 8, 9) and my own first attempt hit it before any of them reported.
Lenses 1 and 3 got a green deep gate only after ad-hoc environment repair documented nowhere —
both reported replacing the symlinks with real copies.

> **UNRESOLVED DISCREPANCY — recorded rather than smoothed over.** Lens 5 reports a green deep
> gate (`GATE PASSED`, exit 0, 22m41s, "committed views verified FILE BY FILE") and reports **no**
> environment repair beyond my symlink fix. Yet `w5` carries symlinks and resolves only **4**
> remappings, which by my own reproducible experiment must produce a digest mismatch — while its
> built `DemoPay` artifact carries **5** remappings and is byte-identical to the live tree.
>
> I cannot reconcile these. My first draft of this document asserted lens 5 had done an ad-hoc
> repair; **that was my inference, not its evidence, and I withdraw it.** Plausible explanations
> include a build taken during a window when the libraries were real directories (lens 9 documented
> that `git checkout -- .` removes the symlinks and a subsequent `forge build --force` silently
> auto-initialises real submodules), or a stale build cache. Resolving it needs a fresh deep run in
> a controlled worktree, which would destroy lens 5's state, so I did not do it.
>
> **What this does not change:** the symlink → 4-remapping → mismatch chain is reproducible on
> demand and five lenses hit it. **What it does change:** whether *any* lens satisfied condition 1
> on the prescribed provisioning is genuinely open, and the honest answer is "unknown", not "yes".
> It is also direct evidence for the finding above — the round did not freeze the environment, so
> per-worktree state is not reconstructible after the fact.

**Two consequences you should weigh:**

1. **Register §13.1 is misdiagnosed.** It records that a worktree corpus run inherently differs
   on `targetCodeHash`. It does not — the symlinking does. Round five wrote off a class of
   reviewer coverage on a cause that was never the cause. (Lens 9 refuted it; I confirmed both
   directions.)
2. **D-050(1)'s own reversal condition may have fired**: "a definition that cannot be met is
   worse than none… that comes back to John." It is not an agent's to quietly under-run.

**And a methodology defect I caused and must own:** I provisioned the worktrees with `ln -sfn`
against existing empty submodule directories, which nested the links instead of replacing them,
breaking `forge build` in seven of ten trees. Lens 9's timestamped pre-fix snapshot (five broken,
four correct, one hybrid) is authoritative; my later count was taken after reviewers had begun
self-repairing. Worktrees then flip-flopped between provisioning states mid-round — my repair
overwrote lens 4's real copies with symlinks — so **the round froze the commit but never the
environment.** Lens 9 measured two identical invocations 31 seconds apart returning FAIL then
PASS with HEAD unchanged.

**Also:** nine concurrent reviewers drove load average above 100. Lens 6 lost a probe mid-mutation
to a 120s timeout that left a 0-byte log beside an "exit 0" notification. Lenses 3, 7 and 9 each
recorded probes that flaked to a false CAUGHT and reversed on re-run. Every lens that reported a
single-run RED should be treated as provisional.

---

## 2. CONFIRMED — reproduced by me, from scratch, with my own probe

These I verified personally. Where I say "structural" I read the code path and confirmed the
mechanism but did not execute an end-to-end exploit.

### 2.1 A ratified ruling and a SIGNED gate pack rest on a control that does not exist — HIGH
*Found independently by lens 2 and lens 8, by different routes.*

**D-014** (ratified 2026-07-28) rejected giving the signer conformance checks, on this ground:
> "a wrong-purpose ALLOW is detectable after the fact by the D-010 verifier, **which does the
> conformance comparison**."

**It does not.** Verified structurally:
- `grep -c decodedSelectorAndParameters verifier/verify.py` → **0**
- `_calldata_check` binds calldata → `dataHash` only (a hash binding, no decode)
- `normalizedAction` is compared to the **action**; `expectedEffects` is compared to the
  **mandate**. Nothing compares the signer-attested decoded parameters to the mandate's purpose
  fields.

**The same claim is in `docs/gate-s1-evidence.md` lines 124 and 152 — the Gate S1 pack you signed
on 2026-07-28.** Round five's lens B recorded that file as "not opened at all"; the register has
no entry for it.

Both lenses independently produced a wholly self-consistent wrong-purpose ALLOW — re-canonicalised,
re-hashed, re-bound, **re-signed** — that the vault executed and `verify.py` certified `=> PASS`,
exit 0, each with a signature negative control that fails. *(Their end-to-end runs I am relaying;
the structural absence I confirmed myself.)*

**Why it is not a re-report of E4:** E4 named `normalizedAction` and `expectedEffects`; A-069 built
those. `decodedSelectorAndParameters` is a third field, and it is the one D-014's justification
rests on.

### 2.2 The worktree provisioning / condition-1 defect — HIGH
Section 1 above. Reproduced both directions with a clean rebuild.

### 2.3 `check-secrets.sh` — the fourth hole — HIGH
*Lens 1. Reproduced by me with synthetic hex (`0123456789abcdef`×4) and a control.*

```
CONTROL  const OWNER_KEY = "0x<64hex>"        -> exit 1  (BLOCKED)
PROBE    SENTINEL_SIGNER_KEY=<64hex>          -> exit 0  (PASSES)
PROBE    const KEY_1 = "0x<64hex>"            -> exit 0  (PASSES)
```

Two independent evasion families: **(a)** a 64-hex value with no `0x` prefix, where coverage
depends on whether the variable name happens to contain one of nine hard-coded tokens —
`SENTINEL_SIGNER_KEY`, *this repository's own variable*, does not; **(b)** any digit in the
identifier, because the identifier class is `[A-Za-z_]*`.

Lens 1 additionally reports an array-value evasion and a **scope asymmetry**: `check-secrets.sh`
scans `git ls-files` (tracked only), while `check-vendor-honesty.sh` beside it scans tracked *and*
untracked on the stated reasoning that "an untracked file is one `git add -A` away from being
published." The reasoning was applied to the vendor guard and not the credential guard.

This is the **fourth** time this guard has been holed.

### 2.4 §7.1's containment claim — two uncorrected sites, and A-063's record is false — HIGH
*Lens 4. Confirmed by me.*

D-051(a) certified the §7.1 correction. **A-063's entry states it corrected FOUR SITES and that
"a grep for the claim's other spellings found no fifth site."** Two more carry it verbatim:

- `Sentinel_Protocol_Lab_Proposal_v0_2.md:238` — "Its hard onchain backstops **cap native
  value** … the lab limits worst-case blast radius to testnet funds and the vault's hard
  constraints."
- `contracts/src/SentinelVault.sol:12-16` — the contract's own NatSpec — "backstops **cap native
  value** … can still authorize a malicious action **within those caps**."

`F-VAULT-1` had named `§4:238` **by line number**. The grep missed it because it says "hard
constraints", not "hard caps". A-063's own sentence names "a repair that reaches the demonstration
and not the argument" as this project's most-repeated defect.

### 2.5 "The nine MEDIUM findings were fixed" — false, in the SIGNED S2 pack — MEDIUM
*Lens 8. Confirmed by me.*

A-068's own headline: **"Seven fixed and falsified; TWO ARE DESIGN FORKS AND ARE NOT AN AGENT'S TO
CLOSE."** Four documents say all nine were fixed, including `docs/gate-s2-evidence.md:458` — §11.0,
the section D-051(b) created and you ruled on — plus `session-state.md` ×2 and
`round-six-brief.md:16`, which then contradicts itself two lines later.

### 2.6 `A-062` and `A-065` have no entries in the canonical decision log — MEDIUM
*Lens 8. Confirmed by me:* every ID A-059…A-069 returns 1 except **A-062 → 0** and **A-065 → 0**,
while `session-state.md` asserts of that table "**Every entry below has a full entry there**."
A-062 is the entry seven round-five closures and a live gate stage are attributed to, and
`scripts/test.sh:358` prints its number on every run.

### 2.7 `HANDOFF.md:93` — "verified — no git remote" — LOW severity, high salience
*Lens 8. Confirmed by me:* `origin → https://github.com/johnrfite1/sentinel.git`, with two remote
branches. A-004 was corrected on 2026-07-30 with the rule "an action that changes a documented
safety property must update that documentation in the same turn", naming "the two files every
future session is told to trust." One was fixed. HANDOFF.md has been rewritten twice since.

This is the sentence a reader relies on to conclude nothing has left the machine. The repository
*is* private and the push *is* backup under D-016 — the defect is the documentation, not the act.

### 2.8 `verify.py` "1681 lines" — MEDIUM
*Confirmed:* the file is **2069** lines. `session-state.md:260` also says it "remains unswept"; it
was swept (A-055), and `scripts/test.sh:701` says so. The gate half of `H-7` was fixed; both
document halves were not, and the true value has moved twice since.

### 2.9 F006 refutes a claim written on this commit's own date — MEDIUM
*Lens 3. Confirmed by me:* A-069 and register §13.5 both state **"all 50 corpus fixtures carry
equal ceilings" / "No corpus fixture has them diverge."**

`F006` diverges by a factor of **500** — `mandate.maxNativeValueWei = 1e18` vs
`policy.maxNativeValueWei = 2e15`. Measured across all 50: **1 diverges, 49 do not.** Its declared
intent says so in words and its result file records `BLOCK` on `EVAL_VALUE_WITHIN_POLICY`.

Two consequences: §11.0's downgrade of `D-09(c)` rests on this false premise, and the prescribed
v1.1 remedy ("add a corpus fixture") would fix the wrong artifact — the claim is true of the seven
**sample bundles**, which is what the verifier reads.

### 2.10 `scripts/mutate.sh` has a dead anchor; "0 failed to apply" is false — MEDIUM
*Lens 3. Confirmed by me:* `C3b`'s anchor is `if (isDeclared(key)) {`; the code reads
`isDeclaredAt(key, depth, inEnvironment)`. `session-state.md:573` claims "**batch C 14/14 caught**
… 0 survived, **0 failed to apply**." Batch C has exactly 14 rows and `C3b` is one of them.

Lens 3 audited all 131 anchors: **126 OK, 5 unusable**, four of which died inside the very repairs
they exist to protect — including `R3`, the mutation that would falsify the D-014 evidence-decoding
bind that A-068 and A-069 both lean on.

### 2.11 The D-010 verifier skips the override stage entirely on the refusal path — HIGH
*Lens 6. Structural mechanism confirmed by me:* `_refusal_checks` is called at `verify.py:399` and
the function **returns at :401**; `_override_checks` is at **:474**, unreachable on that path.
`override.json` is never opened.

Lens 6's corroboration is the sharpest single artifact in the round: `verify.py <bundle> --tamper
all` on such a bundle prints **six consecutive `=> tamper self-test FAIL: WRONGLY ACCEPTED`** lines
for the override modes — the verifier's own tamper arm declaring six §5.5/§3.3(7) invariants
unenforced on a bundle the certifying arm passes.

### 2.12 A "paired positive" test that never invokes the verifier — MEDIUM
*Lens 6. Confirmed by me:* `test_the_genuine_owner_is_the_mandate_principal` reads `override.json`
and `mandate.json` and compares them to each other. It never calls `verify`. Its comment:
> "The paired positive. Without it the check above could be satisfied by a rule that rejects every
> override, and the sample walk would be the only thing noticing."

Self-refuting — it cannot notice, because it does not run the verifier. It is also near-identical
to `test_owner_is_the_mandate_principal` 80 lines above, which is `H-6`'s recorded instance,
adjudicated ALREADY-CLOSED and now duplicated as the new repair's evidence. This is A-056's
corpus-property/verifier-property category error, the fourth instance.

### 2.13 The call graph can be neutered end-to-end and no profile can see it — HIGH
*Lens 7. Artifact blindness confirmed by me:*

- `internalCallCount` across the 50 committed views: **0 in 46, null in 4 — never non-zero**
- `internalCallTrace` across all 7 sample bundles: **`[]` in all seven**

So no committed artifact carries a non-empty call graph, and `EVAL_CALL_GRAPH_EXPECTED`
(`checks.ts:413`) is a hard `require_(simulation.internalCalls.length === 0, …)` — it passes
unconditionally once the producer is neutered. Lens 7 showed two live mutations surviving 481/481:
`subcalls = []`, and switching the tracer to `prestateTracer` (which returns no `calls` key at any
depth **and does not error**, so `SIM_CALL_TRACE_UNAVAILABLE` never fires).

A-068 closed `C-3` with three unit tests on the pure walk; the walk's **input and output are both
still unpinned**. §3.3(11)'s unexpected-internal-call defence is off under either mutation.

### 2.14 The §7.3 latency columns are unpinned; the gate passes on fabricated figures — HIGH/MEDIUM
*Lens 1. Mechanism confirmed by me:*

- `scripts/test.sh:243` drops `micros` from the corpus-verdict comparison
- `ts/src/ablation/report.ts:141,162-163` — `micros` is the **sole** input to `p50Micros`/`p95Micros`
- A-062's stage asserts only that the report is its generator's output on the committed inputs

Each stage does exactly what it says; the **composition** leaves the two published latency columns
outside all provenance. Lens 1 rewrote 100 `micros` values across the 50 result files, regenerated,
and got **`GATE PASSED`, exit 0** with the published table reading `L1 5000/5000, L3 3/3`. Control:
flipping a verdict in the same files is caught (`1 result file(s) MOVED`).

Worse than recorded `G-2`, which is marked CLOSED. Note the proposal carries a résumé template
reading "Y millisecond p95 deterministic decision latency" — a public-claim surface.

---

## 3. HIGH-SEVERITY LEADS — reviewer evidence, NOT independently reproduced by me

I am flagging these as leads rather than confirmed, because I did not run them myself. Each carries
a reviewer's controls and evidence directory. **They are the first things a follow-up should
reproduce.**

### 3.1 Two live ALLOW credentials at one nonce — lens 2 — HIGH
A-012(a) and `attest.ts:110-112` both claim: "Two credentials can never be live under two different
active mandate hashes … so this is **strictly safe rather than a trade**."

The reservation is **overwritten**, not suspended, on a basis change. So M1 → M2 → **M1** leaves the
first credential live and both bound to the *same* active mandate, where the escape clause never
applies. Lens 2 executed both onchain via snapshot/revert. The existing test covers M1→M2 and
M1→M1, never the cycle. **Needs neither a restart nor a second process — so it is outside D-013's
stated honest limit.**

*(I confirmed the claim text and the overwrite mechanism by reading; I did not run the exploit.)*

### 3.2 The vault does not bound RATE, and the drain is ATOMIC — lens 4 — HIGH
100 valid ALLOW receipts drain a capped vault to zero **inside a single transaction** — 7.5M gas,
~75k per action, with `block.number` and `block.timestamp` asserted constant. `nonReentrant` stops
nesting, not repetition. Three controls in the same file (cap+1 reverts; re-entry refused; pause
before the batch reverts).

This bears on the **certified** §7.1 sentence: "only PAUSE bounds a compromised signer — it bounds
damage **after somebody notices**." There is nothing to notice; no owner transaction can interleave.
And the shipped limit test spreads its 100 actions with `vm.warp(+365 days)` between each, so a
reader takes away "over a century" rather than "in one block."

Lens 4 also reports five assertion messages in the shipped suite naming a *per-transaction* bound
that does not exist, and that pause **and** recover are both inert against the recorded token gap
(`transferFrom` never touches the vault; `recover` is native-only).

### 3.3 The invariant campaign's marginal killing power is ZERO — lens 4 — MEDIUM
25 mutations, two arms: campaign alone 9 caught / 16 survived; deterministic alone **25 caught / 0
survived**. **Every mutation the campaign caught was also caught without it.** 8/8 two-sided controls
confirm the instrument is live. §7's "twelve unreachable checks" measured at **at least fourteen**.
And `Z1`: inverting the chainId check so *nothing can ever execute* leaves **11 invariants passing**
— all ten live invariants are `assertFalse(ghost)`, which zero executions satisfies.

### 3.4 A-069's evidence projections are absence-is-agreement — lenses 6 and 2 — HIGH
Both checks are gated on `isinstance(..., dict)`, so an **absent** or non-dict `normalizedAction` /
`expectedEffects` emits **no Check object at all** — not even a SKIP. Wrapping the identical
contradicting object in a one-element list passes. Lens 6 also reports the projections are never
called on the refusal path. Contrast A-067's own comment one day earlier: "ABSENCE IS NOT
AGREEMENT… With no document there is nothing to certify, so this FAILS."

### 3.5 Thirteen self-contradicting evidence bundles all certified PASS — lens 7 — HIGH
Re-canonicalised, re-hashed, re-bound, re-signed, with two passing controls and one demonstrated
rejection. Includes: every `policyChecks` row flipped to VIOLATION under an ALLOW receipt; every row
flipped to PASS under a BLOCK; the single failing check **deleted**; `targetCodeIdentity.matches =
true` beside two hashes that visibly differ; max-uint256 allowance to `0x…deadbeef` inside an ALLOW.
Four of these are pure derivations of material the verifier already holds.

### 3.6 A-061's "both arrays must agree" reads two of three envelope levels — lens 6 — HIGH
`_extract_refusal` descends up to two envelope levels; `_both()` resolves from only the innermost
and `receipt_doc`. Moving the decoy one level out re-opens `H-3` verbatim, with the verifier printing
"the bundle carries no `signerFindings` array … checked both" about a bundle that carries one.

### 3.7 A-059's trust-root check asserts an invariant it does not test — lens 6 — HIGH
Passed a presenter-supplied `domain.json` via `--domain`, it prints "the trust root was **ASSERTED by
the verifying party**" with no containment test, and a hostile re-signed bundle verifies `=> PASS`,
exit 0 — including under `--all`. `scripts/test.sh:452` uses exactly that invocation shape.

### 3.8 `D-06` is recorded FIXED and is not — lenses 3 and 9, same source line — HIGH
Both lenses independently landed on `EVAL_APPROVAL_CEILING` (`ts/src/evaluate/checks.ts:382`) as a
surviving `<=` → `<` mutation, with controls proving the four *pinned* boundaries do fail. A-068's
repair calls itself "that generalisation" and enumerates four sites; `D-06` named five. Lens 3 found
**five further unpinned boundaries** outside D-06's set (both mandate window bounds, both policy
window bounds, the allowance-effect ceiling) — A-064 pinned direction, not edge. No corpus fixture
sits on any of these boundaries, measured.

### 3.9 `scripts/test.sh` aborts mid-run and never prints `GATE FAILED` — lens 3 — MEDIUM
Under `set -euo pipefail`, three unguarded diagnostic commands kill the run — including the corpus
digest-mismatch `diff | head`. **Observed:** lens 3's first baseline ended at a truncated diff with
exit 1, `grep -c "GATE PASSED\|GATE FAILED"` = **0**, and the entire D-010 verifier stage skipped.
The header claims "This script therefore fails on a non-zero exit from ANY stage."

### 3.10 A-066's socket repair has two unfixed siblings — lens 7 — MEDIUM
The identical construction is in `tools/sample-check.ts` and `tools/emit-samples.ts`, neither with
the fallback; both die `connect EINVAL` from a worktree. `sample-check` is **your D-006 adversarial
sampling instrument and a signed Gate S1 condition** ("Run it yourself with: `npm --prefix ts run
sample-check`"); `emit-samples` generates the D-010 verifier's entire fixture corpus.

---

## 4. Notable MEDIUM/LOW leads, compressed

- **`v1-1-register.md` §13 is stale by ~17 of 24 rows** (lenses 4, 8) — still says "the other 47 are
  not fixed", "remediation scoping has not happened", and marks every A-068 fix and every §11.0
  acceptance as `open`. **This is the file every reviewer is told to read so a re-report is not
  mistaken for a finding.** Lens 8 also found §13.3 headlined "CLOSED — 20 of the 51" enumerating 24.
- **§11.0's adjudicator reasoning is truncated mid-word** in five of ten entries, two carry none, and
  **no adjudicator report is committed anywhere** — the cited `docs/review-2026-08-17/` holds the
  *reviewer* reports and its own README says they are "not adjudicated and several are wrong." The
  worst truncation cuts off exactly where the adjudicator argues a LOW **up** to MEDIUM (lens 8).
- **`B-3`'s exact false sentence survives in the signed S2 pack** (lens 8) — A-062 fixed the
  `scripts/test.sh` copy and never touched `gate-s2-evidence.md:440`, which still says two RFC 8785
  paths "are untested by anything," citing a REPORT.md line that says the opposite. Both paths are
  tested in the suite this gate runs.
- **A fifth false statement in the COVERAGE BOUNDARY** (lens 8) — "FOUR limits … two supplied by an
  independent review"; the report states two, both from the second labeller. `git log -S'Four limits'`
  → 0 commits. A-062 claimed it "audited every claim in the block."
- **`check-label-integrity.sh` defeated by a `.` in a filename** (lens 1) — the guard uses the
  filename as a `grep` *pattern* without `-F`, so `labeller-H.control.json` matches a different pin
  entry and reports "none unpinned" with 21 files on disk.
- **The D-011(c) sample composition is pinned by nothing** (lens 5) — a steered ten-fixture sample
  regenerates a **byte-identical** `ablation-report.md`, because with zero disagreements the report
  never prints which fixtures were sampled, while stating "the selection is a deterministic hash
  precisely so it cannot be steered." Lens 5 verified the real draw *is* correct today.
- **The D-011(d) S2 halt condition can halt nothing** (lens 5) — `THRESHOLD BREACHED` is a sentence in
  a markdown file no gate profile reads. A-068 recorded this as fixed ("a floor now says so loudly").
  *Whether D-011(d) should become a gate condition is a fork for you, not an agent.*
- **`G-3` is worse than recorded** (lens 5) — three classes are credited only by UNRESOLVED, not two,
  and the recorded finding's universal claim ("every other credited class is carried by at least one
  VIOLATION") is false. Strict reading: **11 of 20**, not 14 of 20.
- **The class-coverage GAP can be erased by one word** (lens 1) — `status: 'GAP'` → `'DELEGATED'` and
  the guard prints "None owes a fixture", exit 0. `ruling: 'D-997'` is printed as authority; nothing
  resolves ruling ids.
- **Vendor-honesty condition (2) is a two-entry phrase denylist** defeated by a double space, a
  hyphen, or ordinary markdown line-wrapping; condition (4) excludes three files that carry 42/34/24
  measured figures, against the guard's own stated criterion (lens 1).
- **`ts/src/tools/**` (990 lines) is executed by no test and no gate stage**, hand-rolls the §5.3
  binding three times, and its comment denies being a second implementation (lens 7).
- **The nine-surface definition leaves ~12,250 lines unassigned** (lens 9), including `ts/test/**` at
  8,498 lines — the test oracle every headline count rests on. Lens 9's one code finding came from
  there.
- **`simulate.test.ts:185` compares wall-clock** (lenses 3, 7) — asserts a property A-029 documents
  as false; measured to fail ~2 in 22 runs; caused false CAUGHT verdicts in two lenses' sweeps.
- **`SimulationLeakError` does not latch** (lens 7) — the corpus runner's bare `catch {}` turns a
  declared-poisoned chain into `simulation = null` and fixtures N+1…50 run on it silently.
- **The vault permits `signer == owner`**, validates no `schemaVersion`, never compares `issuedAt` to
  `expiresAt`, and accepts an override with `reasonHash == 0` — logged as `OverrideAuthorized` with no
  reason, which the D-043 comment calls "exactly the event a hostile reader would ask about first"
  (lens 4).
- **All three usage examples in `verify.py --help` fail** on this repository's own corpus (lens 6).

---

## 5. What the lenses said about their own briefs — worth carrying into round seven

Convergent, from reviewers who could not see each other:

1. **"Name the repair, not the finding."** Lenses 2, 3 and 7 all report that their directed lead
   pointed at a *closed* item, and that the productive question was "what did the repair not reach?"
   Lens 2's exact words: a lead pinned to one idiom nearly cost the round its two best findings.
2. **"For every finding the register marks CLOSED, grep the corrected sentence's other spellings."**
   Lens 8 produced five findings that way; A-063's missed fifth site is the same shape.
3. **"For each repair, enumerate the paths it does not run on"** (lens 6) — different from "did it
   generalise", and the question that found the refusal-path holes.
4. **Several lenses flagged that `§13` is currently bad advice** to read as authoritative, because its
   status column is stale in the direction of "more outstanding than there is."
5. **The brief needs a third branch for a non-green baseline.** "If your baseline is not green, STOP"
   nearly cost the round several surfaces when the cause was environmental.

---

## 6. What I did NOT do

- **I did not fix anything.** No code, comment, document or claim was changed. The live tree is clean
  at `140c59e`, verified.
- **I did not reproduce §3's leads myself.** They carry reviewer controls and evidence, and I say so
  rather than presenting them as confirmed.
- **I did not run a full re-verification of every one of the 91 findings** — I prioritised by severity
  and by whether a cheap decisive check existed. That is budget, named as budget.
- **I did not judge whether the round is CLEAN.** D-047 reserves that to you and forbids me
  re-authoring, narrowing or attaching exceptions to it.
- **I did not touch the D-008 comprehension questions**, sign anything, or certify any public claim.
- **Cleanup I did do:** killed two orphaned processes from this round (a w5 signer, an `anvil` on port
  9156), both PPID 1, both spawned by my own reviewers.

---

## 7. The two things I think need your ruling first

1. **The signed/certified text.** Findings 2.1, 2.4, 2.5 and 3.2 all sit inside documents you signed
   or certified — Gate S1, the §11.0 section you ruled on, and the §7.1 row you certified at a
   walkthrough five days ago. That is a different class from a stale count, and certification of
   public claims is autonomy NONE.
2. **Whether D-050(1)'s reversal condition has fired.** The ratified definition of full breadth
   specifies a provisioning method that makes its own condition 1 unmeetable, and the brief records
   the blocker as SOLVED. D-050(1) says explicitly that this comes back to you rather than being
   quietly under-run.

D-048 is untouched: a clean round is a precondition for pre-publication, never a trigger, and this
round is not clean.
