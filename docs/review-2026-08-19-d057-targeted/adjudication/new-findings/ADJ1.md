# ADJ1 — independent adjudication of `V3-N2`, `F7-R1`, `N-TESTSH-FLOORS`

**Adjudicator:** ADJ1, independent. I reported none of these findings and authored none of the
code, tests, documents or repairs they concern.

**Frozen commit:** `a18e6e61598a996d962798ad0353a166232d4490`, confirmed with `git rev-parse HEAD`
in my worktree before the first probe and again after the last one.

**Authority:** D-058(7) (adjudicate each new item and classify it), D-058(4) (the Gate 5
follow-through on `V3-N2`), D-058(5) (the remedy shape for `F7-R1`), D-058(2) (`R4-F4`'s property
covers all six gate floor constants).

**What I did not do.** I repaired nothing. I signed, certified, ratified, reaffirmed and revoked
nothing. Every mutation was made in my own worktree and reverted; `git status --porcelain` over
`contracts/src`, `contracts/test`, `scripts`, `docs`, `ts`, `verifier`, `fixtures`, the proposal,
`HANDOFF.md` and `README.md` is empty at the end of this work, and `forge test` gives 92/92 —
equal to `FOUNDRY_MIN_TESTS`. My probe files (`contracts/script/F7Probe.s.sol`,
`contracts/test/ADJ1Probe.t.sol`) are deleted and are **not** proposed repairs.

| Item | Reporter | Filed as | **My classification** |
|---|---|---|---|
| `V3-N2` | V3 | MEDIUM | **CONFIRMED** — and it carries a Gate 5 status fork that is John's |
| `F7-R1` | V1 | unrated | **CONFIRMED** — severity LOW as risk, and it is a false claim in the contract's own audit-log NatSpec |
| `N-TESTSH-FLOORS` | V5 | unrated | **DUPLICATE** — of `R4-F4` under D-058(2), and of register §13 `C-2`/`A-2`/`B-1`. One genuinely new site found while checking, recorded in §3.6 |

---

---

# 1. `V3-N2` — the vendor-honesty caveat check certifies a section it never locates

## 1.1 The exact claim at issue

`scripts/check-vendor-honesty.sh` prints, on every green gate run:

```
  ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it
```

The claim has two parts, and only the first is checked:

1. **`docs/ablation-report.md` contains a particular sentence** — checked, correctly, with
   whitespace normalisation on the report side.
2. **That sentence is the one §7.2 words** — **not checked at all.** The expected text is
   extracted with a whole-document `grep -F … | head -1` over
   `Sentinel_Protocol_Lab_Proposal_v0_2.md`. Nothing in the extraction is scoped to §7.2, and
   nothing anywhere establishes that §7.2 contains the sentence even once.

## 1.2 The authoritative source — code, not prose

`scripts/check-vendor-honesty.sh:269-281`. Line 269 is the whole finding:

```sh
CAVEAT="$(grep -F 'is not evidence that current vendors miss Case 3' "$PROPOSAL" | head -1 | sed 's/^ *//;s/ *$//')"
```

`$PROPOSAL` is the entire 71 KB proposal. Two lines above, at `:263-265`, the script's own comment
declares:

> The expected text is EXTRACTED FROM THE SPECIFICATION, not transcribed here — the same shape as
> `check-type-strings.sh`, and for the same reason: a guard holding its own copy of the thing it
> guards can only ever confirm that copy.

**The sibling it names does scope, and this one does not.** `scripts/check-type-strings.sh:34-36`
materialises the section first —

```sh
SPEC_SECTION="$(mktemp)"
awk '/^### 5\.8 /{f=1;next} f && /^#{1,4} /{exit} f' "$SPEC" > "$SPEC_SECTION"
if [ ! -s "$SPEC_SECTION" ]; then   # refuses if the section is empty
```

— and then greps `$SPEC_SECTION`, not `$SPEC`. So the comment's own comparison is what convicts
line 269: it claims a shape it does not have.

**This is the third instance of one defect inside this single file, and the other two are already
fixed in it.** The D-008(3) certification check at `:352` carries a header reading *"SCOPED TO §2,
AND THE FIRST VERSION WAS NOT"* — it grepped the whole proposal until an independent review planted
a certification line in §14 on 2026-08-16 (A-039). The D-008(1) marker count twenty lines above was
fixed the same day from `$0` to field 4. The caveat block sits between the two repaired blocks and
was not swept.

## 1.3 Reproduction

All probes run from my worktree at the frozen commit. `/usr/bin/grep` used throughout for
verification counts; the guard uses its own `grep`.

### CONTROL 0 — the unmutated tree must pass

```
$ ./scripts/check-vendor-honesty.sh
  ok    no artifact claims an executed or emulated vendor comparison (D-001, D-008(2))
  ok    no named vendor appears in any measurement artifact (D-008(4))
  ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it
  ok    §2 capability table: 11 of 11 rows carry a marker resolving to a §13 entry
  ok    §2 capability table: inference marking (D-008(3)) certified by record — …
vendor honesty: mechanical conditions pass; D-008(1) met and (3) certified by record
EXIT=0
```

### MUTANT M1 — the reported falsification, reproduced exactly

Weaken §7.2's caveat to `This baseline makes the demo reproducible.` (proposal line 675) and plant
the original sentence inside §6 (verified inside `## 6. AI and Context Scope`, which physically
precedes §7). Section-scoped count of the caveat inside §7.2 afterwards: **0**.

```
  ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it
EXIT=0
```

**Survived.** §7.2's caveat has been silently weakened, the guard certifies "as §7.2 words it",
and the stage is green.

### MUTANT M2 — sharper, and it isolates the `head -1`

M1 could be read as "the anchor phrase left the document's §7.2, so of course nothing matched
there". M2 removes that reading. §7.2 is left **completely untouched**. A decoy sentence
containing the same anchor phrase —
`This demo baseline is illustrative and is not evidence that current vendors miss Case 3 in any
strict sense.` — is planted in §6 (earlier in the file, so `head -1` selects it), and
`docs/ablation-report.md`'s quoted caveat is replaced with the decoy.

Verified before running the guard: the report contains §7.2's real wording **0** times
(wrap-normalised count).

```
  ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it
EXIT=0
```

**Survived.** This is A-028's original defect — the ablation report publishing its
detection-contribution table without §7.2's caveat — fully reinstated, with the guard built to stop
it printing `ok`. The report now quotes a *softened* caveat under the label "§7.2's own caveat,
verbatim", which is the honesty failure the check exists to catch.

## 1.4 Paired controls — the guard is not merely passing everything

| Control | Mutation | Observed |
|---|---|---|
| **C1** | caveat genuinely removed from `docs/ablation-report.md`, proposal untouched | `FAIL  docs/ablation-report.md no longer carries §7.2's caveat:` **exit 1** |
| **C2** | anchor phrase removed from the proposal entirely | `FAIL  §7.2's caveat is missing from Sentinel_Protocol_Lab_Proposal_v0_2.md, so there is nothing to enforce` **exit 1** |
| **C0** | none | `ok`, exit 0 |

So the block fires on the two failures it was pointed at (which is what A-046's 8/8 falsification
measured — its probe *reworded* §7.2's caveat while leaving the anchor phrase in place, which the
guard does catch) and does not fire on either route that moves the sentence's **location**.

**All mutations reverted; `git diff --stat` over both files is empty.**

## 1.5 Severity

**MEDIUM, as filed — I do not raise it.** No enforcement path is affected and nothing about the
vault, evaluator, or verifier moves. What moves is that a §7.5 Gate 5 condition reported as
`ENFORCED — mechanical` is enforced against the wrong operand. It is not HIGH because the fact the
check asserts is independently true today (§1.6), and exploitation requires an edit to the
proposal by someone with commit access — this is a regression net that does not hold, not an open
door.

## 1.6 What my evidence establishes, and what it does not

**Establishes:** the instrument cannot detect either (a) §7.2's caveat being weakened or removed
while a matching sentence exists elsewhere in the proposal, or (b) the ablation report quoting a
non-§7.2 sentence under the label "§7.2's own caveat, verbatim".

**Does NOT establish that anything is currently wrong with the artifacts.** I measured the
property the guard claims, section-scoped and independently of the guard:

```
occurrences of the caveat substring INSIDE §7.2 : 1
occurrences ANYWHERE in the proposal            : 1
§7.2 wording: 'This baseline makes the demo reproducible but is not evidence that current
               vendors miss Case 3.'
report carries §7.2's wording verbatim (wrap-normalised): True
```

A correct section-scoped check returns the same answer as the broken one at this commit. The
caveat *is* where it should be and the report *does* carry it.

## 1.7 D-058(4) — does independent evidence still support Gate 5?

I read `docs/gate-5-vendor-audit.md` in full (502 lines), the Gate 5 sections of
`docs/gate-s2-evidence.md`, D-008/D-032/D-038/A-039/A-046 in `docs/decisions.md`, and every block
of `scripts/check-vendor-honesty.sh`.

### What rests on the block `V3-N2` breaks — exactly one condition, and it is not a numbered one

| Surface | Text | Rests on the broken block? |
|---|---|---|
| `docs/gate-5-vendor-audit.md`, status table, row "—" | *"§7.2's own caveat travels with the numbers — **ENFORCED** — extracted from §7.2 and required in the ablation report, whitespace-normalised — mechanical"* | **YES** |
| `docs/gate-s2-evidence.md`, Gate 5 bullet 3 | *"**§7.2's caveat travels with the numbers** — extracted from §7.2 itself and required in the ablation report, after A-028 found the report had published its table without it."* | **YES** |
| `scripts/check-vendor-honesty.sh:274` printed line | *"as §7.2 words it"* | **YES** |

That is the complete live inventory. I swept the tree with wrap-normalisation for
`extracted from §7.2`, `from §7.2 itself`, `as §7.2 words it`, `caveat travels with the numbers`
and `EXTRACTED FROM THE SPECIFICATION`; every other hit is a frozen probe log under
`docs/review-2026-08-18-d055e/adjudications/probes/` or this review's own directory.

**The words "extracted from §7.2" are false as written, in both documents.** The extraction is
whole-document. One of those documents is `docs/gate-s2-evidence.md`, which is a signed-gate
evidence pack held immutable by `scripts/check-gate-immutability.sh`.

**This condition is not one of D-008's four.** D-008 enumerates (1) dated and linked cells,
(2) empty §10.1 columns, (3) inference marking, (4) no claim or layout implying superiority. The
caveat requirement is the A-028 remedy, carried in the audit's status table as an unnumbered extra
row. It supports the honesty argument; it is not the mechanism any numbered condition is enforced
by.

### What rests on evidence independent of the broken block

- **D-008(1), mechanical half.** A separate `awk` at `:317-318` anchored on the §2 table header
  row, counting the `[§13#N read YYYY-MM-DD]` marker in **field 4** (the capability cell), with
  every `N` resolved against §13's actual declared entry numbers at `:325-331`. Reports 11 of 11.
  Section-scoped and marker-scoped; untouched by `V3-N2`.
- **D-008(1), substantive half.** `docs/gate-5-vendor-audit.md`'s source-verification pass — every
  cited page fetched and read 2026-08-15, per-row findings recorded including the five rows that
  did **not** hold — plus D-038's seven rulings and two new §13 entries. This is human evidence,
  produced before and independently of any script.
- **D-008(2).** A whole-file literal-label scan for the two §10.1 vendor-comparison labels **[the two literal strings were quoted here; replaced with this reference under D-060(3) because quoting them made this evidence file trip the very guard it describes. AUTHORITATIVE SOURCE: the pattern at `scripts/check-vendor-honesty.sh:203`, and §10.1 of the proposal. No finding, mechanism, severity, classification, argument or verdict is changed; the raw original is preserved.]**
  across tracked *and* untracked-but-unignored artifacts, plus a definition-site existence check at
  `:218-221` so the condition cannot pass by §10.1 being deleted. Correctly unscoped — it is a
  "must not appear anywhere" rule, and section scoping would weaken it. Untouched.
- **D-008(3).** Certified by John at the Gate 5 session (D-038, 2026-08-16). The script's role is
  to confirm a named certification line exists **in §2** — a block explicitly repaired for this
  exact whole-document defect on 2026-08-16 — and that §2 still hashes to
  `CERTIFIED_TABLE_SHA=c9034750…`, with the certification-removed path failing rather than
  reporting "uncertified". Untouched.
- **D-008(4).** The named-vendor scan over measurement artifacts, with the anchored exclusion list.
  Untouched.
- **The caveat's presence in the report.** Emitted by the generator, `ts/src/ablation/report.ts:290-291`,
  as a literal — so the report cannot silently lose it without a code edit, independent of the
  guard.

### The status fork — stated, not resolved

**Nothing in `V3-N2` falsifies Gate 5's substance.** The condition it breaks is a supplementary,
unnumbered one; the fact that condition asserts is independently true at this commit; and all four
numbered D-008 conditions rest on separate, section-scoped or correctly-unscoped machinery plus
John's own 2026-08-16 rulings. **What is falsified is the instrument's soundness going forward, and
two sentences that describe it.**

**FORK — for John, not for me:**

- **(A)** Gate 5's certification (D-038) stands as ruled. `V3-N2` is an instrument defect on the
  A-028 caveat condition; the remedy is to scope the extraction to §7.2 the way
  `check-type-strings.sh` scopes to §5.8 (including its empty-section refusal), and to correct the
  phrase "extracted from §7.2" in the two documents that assert it. Precedent points this way:
  A-039 found the *identical* defect in the *same file* — the certification grep — and it was
  repaired in place without any gate being reopened.
- **(B)** The phrase "extracted from §7.2 itself" is a false statement about an enforcement
  mechanism inside `docs/gate-s2-evidence.md`, a **signed** pack held immutable by a guard. Whatever
  rule governs a false claim discovered inside a signed pack applies here, and that rule is not
  mine to apply. A-047's annotation to the signed S2 pack reached a facilitated ratification
  (D-045) — so this repository already has a procedure for it, and it is a facilitated one.

**The forks are not exclusive.** (A) is about the guard; (B) is about a sentence in a signed pack.
Both can be true. **I have not revoked, reaffirmed, or changed any certification, and I state no
preference between them.**

One thing (A)'s remedy must not lose: `docs/ablation-report.md` is **hard-wrapped**, and the guard
normalises it before comparing for exactly that reason. A §7.2-scoped extraction must keep the
report-side normalisation, or the repair ships dead — this is the trap the brief names second and
that V3 recorded hitting.

## 1.8 Classification

**CONFIRMED.** Reproduced twice with three controls. Carries the Gate 5 status fork in §1.7, which
is John's.

---

---

# 2. `F7-R1` — the vault's NatSpec claims a log survives a revert

## 2.1 The exact claim at issue

`contracts/src/SentinelVault.sol:274-276`:

```solidity
// §3.3(2)'s "logged", emitted AFTER authentication and BEFORE the call — so the log
// records only authorizations that actually passed, and records them even if the
// external call then reverts the transaction away. (D-043)
```

Two claims. **The first is true.** The emit at `:277-279` sits after every override check —
`_checkAction`, `_checkReceipt`, the REVIEW-verdict gate, the five-field override binding,
`OverrideExpired`, and `digest.recover(ownerSig) != owner`. **The second is false.**
`_consumeAndCall` ends `if (!ok) revert CallFailed(ret);`, and the EVM discards a reverted frame's
logs.

## 2.2 The authoritative source

The chain, not the test harness — which is the whole difficulty. `contracts/src/SentinelVault.sol:281`
(`return _consumeAndCall(action, callData, receipt.decisionId, true);`) and `:383-384`:

```solidity
(bool ok, bytes memory ret) = action.target.call{value: action.valueWei}(callData);
if (!ok) revert CallFailed(ret);
```

## 2.3 Reproduction — on a live chain, because the harness lies here

Foundry's `vm.recordLogs` retains logs emitted inside a reverted frame, so an in-VM test written
that way falsely confirms the claim. I therefore ran the decisive probes against **`anvil`
(chain id 31337)** and read `eth_getTransactionReceipt` — what an offchain observer actually sees —
enumerating every transaction from the chain rather than trusting the broadcast file's ordering.

Rig: a probe script deployed `DemoPay`, `SentinelVault` (funded 1 ether, ceiling 0.01 ether) and a
`Relay` contract that makes a low-level call and **swallows** the revert, emitting
`Attempted(vault, ok)`. `DemoPay.purchase` reverts `NoPayment()` when `msg.value == 0`, so an
override carrying `valueWei = 0` is a well-authenticated override whose external call fails.

| # | Transaction | Top-level status | Logs in the receipt |
|---|---|---|---|
| **1 — CONTROL** | direct `executeWithOverride`, call succeeds | `0x1` | `OverrideAuthorized`, `ActionExecuted`, `Purchased` |
| **2 — PROBE** | direct `executeWithOverride`, call reverts | **`0x0`** | **none (0 logs)** |
| **3 — PROBE** | `Relay.relay(vault, …)`, inner call reverts | **`0x1` — mined successfully** | **`Attempted` only; `Attempted.ok == false`** |
| **4 — CONTROL** | `Relay.relay(vault, …)`, inner call succeeds | `0x1` | `OverrideAuthorized`, `ActionExecuted`, `Purchased`, `Attempted` (`ok == true`) |

**Transaction 3 is the decisive one.** The transaction was mined with status `0x1` — nobody can say
"the whole transaction reverted, so of course there are no logs". Its receipt is complete, it
proves the vault really was called and really did fail (`Attempted.ok == false`), and
`OverrideAuthorized` **is absent from it**. Transaction 4 is the same shape with the same relay in
the same block, and the event is present. The only variable moved is whether the external call
reverted.

## 2.4 The trap, demonstrated rather than described

Three Foundry probes against the same code, starving the vault with `vm.deal(address(vault), 0)`:

- `test_probe_TRAP_recordLogsKeepsTheRevertedFramesEvent` — `vm.expectRevert()`, then
  `vm.getRecordedLogs()`: **`OverrideAuthorized` entries kept: 1**, while `vault.actionNonce() == 0`
  proves every state write of that frame was discarded.
- `test_probe_swallowedRevertDiscardsStateButNotTheRecorder` — the same call through a low-level
  `call` that swallows the revert: `ok == false`, `actionNonce == 0`, and the recorder **still
  reports 1**.
- `test_probe_CONTROL_successfulOverrideEmitsAndRetains` — a genuine successful override: 1 entry,
  `actionNonce == 1`.

All three PASS. **The recorder gives the same answer, 1, for the case the chain answers 0 and for
the case the chain answers 1.** A test built on it cannot distinguish them, which is almost
certainly how the sentence came to be written. My probe files are deleted.

## 2.5 Severity

**LOW as risk; the reason it matters is the project's own false-claim standard.** §3.3(2) requires
override be *"separately authenticated, unavailable to the agent, and logged"* (proposal line 195).
It says nothing about surviving a revert, so the false clause is a gratuitous over-claim and
deleting it costs no conformance. No enforcement path, no fund movement, and no gate figure
depends on it. It matters because it is a false statement, in the contract's own NatSpec, about
what the onchain audit log guarantees — the same family as A-063 — and because an auditor who
believed it would look for a record of *attempted-but-failed* overrides that does not exist.

**Sibling sweep, mechanical.** Wrap-normalised sweep of the whole tree for
`reverts the transaction away`, `even if the external call`, `records only authorizations`: **the
false clause exists at exactly one live site**, `contracts/src/SentinelVault.sol:275-276`. Its
nearest sibling, `docs/v1-1-register.md:176`, states only the true half — *"after authentication and
before the call, so the log records only authorizations that passed"* — and needs no change. This is
the rare case where the repair really is one site.

## 2.6 What the NatSpec can truthfully say (D-058(5) — wording, not architecture)

John has ruled the remedy is truthful NatSpec, not machinery to preserve logs across a revert. I
propose no architecture. The following are the facts a truthful comment may assert, each verified
above:

1. **Emission point.** `OverrideAuthorized` is emitted after every override authentication check
   has passed and before `_consumeAndCall`, so **the log never records an authorization that
   failed authentication**. *(True — keep this half verbatim.)*
2. **What replaces the false clause.** The event does **not** survive a failed execution.
   `_consumeAndCall` reverts the call frame when the external call fails, and the EVM discards a
   reverted frame's logs — including when an outer caller swallows the revert and the transaction
   itself is mined successfully. **An observer sees `OverrideAuthorized` if and only if the action
   executed.** The event is therefore a record of authorizations that were **consumed**, not of
   authorizations that were **granted**; §3.3(2) requires the former and this satisfies it.
3. **How the two branches actually differ — they do not differ in revert-survival.**
   `executeWithReceipt` and `executeWithOverride` funnel into the same `_consumeAndCall`, so
   neither path's logs survive a failed external call. The real differences are:
   - the override path emits an **additional** event, `OverrideAuthorized`, which the automatic
     path never emits;
   - `ActionExecuted.viaOverride` is `true` on the override path and `false` on the automatic one;
   - `OverrideAuthorized` is emitted in `executeWithOverride` itself, before `_consumeAndCall`, so
     it is strictly ordered **before** `ActionExecuted` — observed on chain as
     `OverrideAuthorized, ActionExecuted, Purchased` — whereas on the automatic path
     `ActionExecuted` is the vault's first event;
   - the override path's authentication set is strictly larger: a REVIEW receipt, an owner-signed
     override bound to that receipt, action, mandate, policy and nonce, and the override's own
     expiry.
4. **A note worth leaving for whoever writes the test.** `vm.recordLogs` retains a reverted frame's
   logs, so a Foundry test using it will appear to show the opposite of (2). Any test pinning this
   must observe the receipt of a transaction, not the recorder.

**I have not applied any of this.**

## 2.7 What my evidence establishes, and what it does not

**Establishes:** on a live EVM chain, `OverrideAuthorized` is absent from the receipt whenever the
override's external call reverts — both when the transaction reverts at top level and when a
swallowing caller lets the transaction succeed — and present whenever it does not. Paired controls
in the same block rule out "everything is empty".

**Does not establish** anything about whether the override mechanism is *correct*; this is a
documentation defect only. It also does not establish that no other NatSpec claim in the file is
false — I swept only for this claim's phrasing.

## 2.8 Classification

**CONFIRMED.** The wording remedy in §2.6 is stated as required and is not applied.

---

---

# 3. `N-TESTSH-FLOORS` — the gate's own coverage boundary duplicates the floors it asserts

## 3.1 The exact claim at issue

`scripts/test.sh` prints a COVERAGE BOUNDARY block on every **passing** gate run — `cat <<'COVERAGE'`
at `:839`, terminator at `:1190`, and the heredoc is **quoted**, so every figure inside it is a
literal that no variable can move. Two of its sentences restate the gate's own floor constants.

## 3.2 The authoritative source

The six constants, and the instrument that derives from them:

```
scripts/test.sh:234  FOUNDRY_MIN_TESTS=92          scripts/test.sh:659  VERIFIER_MIN_SAMPLES=7
scripts/test.sh:235  TS_MIN_TESTS=527              scripts/test.sh:660  VERIFIER_MIN_TAMPER=78
scripts/test.sh:658  VERIFIER_MIN_TESTS=209        scripts/test.sh:673  VERIFIER_MIN_TAMPER_MODES=30

$ ./scripts/check-suite-floors.sh
  FOUNDRY_MIN_TESTS 92 · TS_MIN_TESTS 527 · VERIFIER_MIN_TESTS 209 ·
  VERIFIER_MIN_SAMPLES 7 · VERIFIER_MIN_TAMPER 78 · VERIFIER_MIN_TAMPER_MODES 30
suite floors: read from scripts/test.sh, which is the only copy.
```

`scripts/test.sh:797` is where the run actually prints them, in the order
suite · samples · tamper cases / modes — i.e. `209 · 7 · 78/30`. That order is exactly the order of
the quartet in the prose below, which is how I fix its field mapping.

## 3.3 Which printed figures are stale — mechanical enumeration of the whole block

I extracted lines 840-1189 and matched every count-shaped figure (`N/N`, `N tests|tamper|modes|samples|fixtures`,
`floors … N`). Full result, nothing omitted:

| Line | Printed text | Verdict |
|---|---|---|
| 929, 956, 958, 962 | `50 fixtures`, `12/50, 41/50, 49/50`, `11/49, 40/49, 48/49` | corpus/labelling figures — **not** among the six constants; out of scope |
| **980-981** | `7/7 samples verify, 78/78 applicable tamper cases across 30 distinct modes behave as specified, and 180/180 of its own tests pass.` | **7 ✓ · 78 ✓ · 30 ✓ · 180 ✗ (VERIFIER_MIN_TESTS = 209)** — present tense, live |
| **983-984** | `THIS PARAGRAPH'S THREE FIGURES READ 62/24/149 FROM 2026-08-16 UNTIL 2026-08-17, while the floors this same run asserts read 160/7/77/29 and printed 142 lines above` | first clause **historical, correctly framed**; second clause **live: 160 ✗ (209) · 7 ✓ · 77 ✗ (78) · 29 ✗ (30)** |
| 1002 | `ALL THREE FIGURES ARE FLOORS THIS RUN ASSERTS (A-047)` | present-tense framing of 980-981; carries no figure of its own |
| 1005 | `these numbers read 6/6, 42/42, 70/70` **until 2026-08-16** | historical, correctly framed |
| 1009, 1015 | `"Ran 145 tests"`, `"146/146 …"`, `all 146 tests passing and all 7 samples verifying` | narration of a past adversarial demonstration — historical |
| 1041-1042, 1102-1103 | `17/17`, `23/33`, `31 mutations, 31/31`, `56 deterministic tests` | mutation-campaign figures, not the six constants |

**Outside the heredoc**, every `echo`/`printf` in the file that carries a floor prints it from the
variable (`:331`, `:390`, `:797`, `:805`). The only hardcoded count outside the block is
`:528  echo "corpus: 50 fixtures executed; …"`, which is the corpus size — not one of the six, and
recorded here only so the enumeration is complete.

**Neither `92` nor `527` nor `209` appears anywhere in the block.** So of the six constants, the
block duplicates **four** — samples, tamper, modes, and the verifier-suite slot — and **four
printed figures are stale**: `180`, `160`, `77`, `29`.

**V5's report needs one correction, which sharpens rather than weakens it.** It described "the same
stale trio" beside "floors of 160/7/77/29". It is not a trio and not one sentence: it is `180` in
the measurement sentence at 980-981 **plus** `160/77/29` in the floors sentence at 984, with `7`,
`78` and `30` currently correct but still duplicated. Four wrong figures across two sentences.

## 3.4 Current claim or dated historical narration? — both, in one sentence

The sentence at 983-984 is **mixed**, and the mixture is why it survived:

- `THIS PARAGRAPH'S THREE FIGURES READ 62/24/149 FROM 2026-08-16 UNTIL 2026-08-17` — a dated record
  of what the paragraph used to say. **Correctly historical. Not a defect.**
- `while the floors this same run asserts read 160/7/77/29 and printed 142 lines above` — the
  subject is **"this same run"**, the run whose output the reader is holding, and "printed 142 lines
  above" points at that run's own line 797. **A live, self-referential, checkable claim, and three
  of its four figures are wrong.**
- `They are corrected here …` — a present-tense assertion that the paragraph now agrees with the
  floors. It does not: 180 ≠ 209.

The measurement sentence at 980-981 needs no such parsing. `verify`, `behave as specified` and
`pass` are present tense, and line 1002 then declares them *"FLOORS THIS RUN ASSERTS"* — floors
presented as measurements, which is the error `check-suite-floors.sh`'s own header warns against, in
the block a passing gate tells the reader to read instead of the pass count.

## 3.5 Reproduction and control

**CONTROL (unmutated).** `check-suite-floors.sh` reports `VERIFIER_MIN_TAMPER 78`; the prose at
980-984 reads `78/78 … 30 … 180/180` and `160/7/77/29`. The derived instrument and the prose already
disagree on four figures, with no mutation applied.

**MUTANT.** `VERIFIER_MIN_TAMPER=78` → `79` in my worktree:

| | before | after |
|---|---|---|
| `check-suite-floors.sh` (derived) | `78` | **`79`** — moved |
| `scripts/test.sh:980` printed prose | `78/78` | `78/78` — **unmoved** |
| `scripts/test.sh:984` printed prose | `…/77/29` | `…/77/29` — **unmoved** |

Reverted; `git diff --stat -- scripts/test.sh` empty, constant back at 78.

**This is the paired control the classification turns on:** it distinguishes "the figures happen to
be wrong" from "the figures are a second, unlinked copy". They are a second copy, in the very file
`check-suite-floors.sh` calls *"the only copy"* — which makes that printed sentence false at this
commit too.

## 3.6 A site nobody has reported, found while checking this one

`docs/session-state.md:470`, in bold and in the present tense:

> **D-010 verifier: 7 samples, 77 tamper cases over 29 modes, 160 tests — and all four are FLOORS
> the gate asserts.**

Three of the four disagree with the constants (77 ≠ 78, 29 ≠ 30, 160 ≠ 209). The italic
parenthetical that follows it *is* correctly dated; the bolded lead is not — it was corrected on
2026-08-17 and the floors moved past it afterwards, a move this same file records at `:388`
(*"A-059 moved 160→170 / 77→78 / 29→30"*) and at `:381` (*"A-070 moved 180→188 verifier … A-074
189→198"*).

**This matters to the record**, because `docs/session-state.md` was squarely inside V2's briefed
sweep for `R4-F4`, and V2's report concludes: *"No stale disagreeing live duplicate exists at this
commit."* One does, seventy-nine lines below the §3 passage V2 did flag. V2 split §3 correctly and
classified `docs/v1-1-register.md` and the round-six brief correctly; the sweep simply did not reach
line 470. I record it because `R4-F4` has now failed three times and a fourth uncorrected copy on
its own briefed surface belongs in front of whoever scopes the next repair. **I have not repaired
it.**

## 3.7 Is this the same defect as `R4-F4`? — yes

D-058(2) binds me: *`R4-F4`'s property covers ALL SIX gate floor constants, and any claim that
floors or counts are single-sourced must be true for all six.* The property, as V2 stated it, is
**"a number a reader can act on must exist in exactly one place, and that place must be the one the
gate asserts."** `scripts/test.sh`'s coverage boundary is a reader-facing surface — printed on every
green gate, under a heading telling the reader to read it *instead of* the pass count — and it
carries a second copy of four of the six constants, four figures of which are stale. That is
`R4-F4`'s property, violated, on the strongest possible surface: the gate script itself.

Three further reasons it is the same item and not a new one:

1. **`R4-F4`'s own FAIL record already names it.** `docs/decisions.md` A-081 records the failure as
   *"…the third iteration of one defect, plus a second site contradicting it in the same section
   **and stale floors printed by `scripts/test.sh` itself**."*
2. **The register already carries it, three times.** `docs/v1-1-register.md` §13 rows `C-2` (HIGH),
   `A-2` (MEDIUM) and `B-1` (MEDIUM) are round-five findings against this exact block — *"prints
   verifier figures 62/24/149 on a run that measured 77/29/160 — and calls them 'FLOORS THIS RUN
   ASSERTS'"*, *"142 lines after the same run printed floors of 160/7/77/29"*. All three are marked
   **re-verified**, all three are among the 47 §13 explicitly records as **not fixed**, and
   remediation scoping is recorded as John's.
3. **The project already routed it there.** `docs/session-state.md:475-477` says of this very block:
   *"That one is CODE and is NOT fixed: it is unscoped remediation awaiting John, register §13."*

**What is new is only the figures, and only because a partial correction moved them.** The
2026-08-17 correction that closed `C-2`/`B-1`'s demonstration updated the paragraph to `7/78/30/180`
and wrote a fresh copy of the floors — `160/7/77/29` — into the sentence beside it. Both have since
gone stale. That is the project's recorded pattern (the repair generalised the demonstration, not
the argument) recurring inside a finding already on the ledger; it is not a second finding.

## 3.8 Severity

**MEDIUM.** Higher than a documentation typo because the surface is the gate's own output, read by
whoever just passed the gate, under a heading that instructs them to trust it over the pass count —
and because it states floors as measurements, which is the specific inversion
`check-suite-floors.sh` was built to prevent. Not HIGH: no gate outcome, threshold or enforcement
depends on it, the floors the run actually asserts are printed correctly 142-odd lines above from
the variables, and `check-suite-floors.sh` gives any reader a correct answer on demand.

## 3.9 What my evidence establishes, and what it does not

**Establishes:** four printed figures in the block are stale duplicates of gate floor constants
defined in the same file; the block cannot track the constants (quoted heredoc, proved by mutation);
and `check-suite-floors.sh`'s printed *"which is the only copy"* is false at this commit.

**Does not establish** that the gate mis-asserts anything — line 797 prints the live values from the
variables and the floor comparisons at `:799-805` use the variables. I did **not** verify the
positional claim *"printed 142 lines above"*; it would need a full gate run and it is not
load-bearing for the classification.

## 3.10 Classification

**DUPLICATE** — of `R4-F4` as adjudicated (whose recorded failure explicitly names the
`scripts/test.sh` floors) read under D-058(2), and of `docs/v1-1-register.md` §13 rows `C-2`, `A-2`
and `B-1`, recorded and unfixed. **Named, as the brief requires.** The uncorrected
`docs/session-state.md:470` site in §3.6 is likewise inside `R4-F4`'s scope and is recorded rather
than repaired.

---

---

# 4. Attestations

- I reported none of these findings, and I authored none of the code, tests, documents or repairs
  under adjudication.
- Every probe ran in my own worktree at `a18e6e61598a996d962798ad0353a166232d4490`. Every mutation
  was reverted and verified reverted. The primary tree was read only, and written only at this file.
- I used `/usr/bin/grep` for every verification sweep, and wrap-normalised before searching for any
  phrase that could straddle a line break. Both traps are live in this repository and both were
  relevant here: `docs/ablation-report.md`'s caveat returns 0 for a line-based grep and 1 after
  normalisation, and `scripts/test.sh` hard-wraps the sentence carrying `160/7/77/29`.
- For `F7-R1` I did not trust `vm.recordLogs`, and I demonstrated why rather than asserting it.
- I have signed nothing, certified nothing, revoked nothing, repaired nothing, and resolved no fork.
  The Gate 5 fork in §1.7 is stated for John and left open.
