# V3 — targeted independent reverification of `R2-F6` and `R4-F3`

**Commit evaluated:** `c8d15a76425544148d7da2f8fa0c003feb6ad2b7`, confirmed by
`git rev-parse HEAD` in the V3 worktree before any other work and again after every probe
(both printed the SHA above).

**Authority:** D-057(9), COMMON-BRIEF + BRIEF-V3. Not a new review; scope is exactly the two
findings named. Anything outside that is filed under §RESIDUALS AND NEW, separately from the
verdicts.

| Finding | Verdict |
|---|---|
| `R2-F6` — `SIGNER_CHAIN_UNSTABLE` names one of two conditions | **FAIL** |
| `R4-F3` — two guards certify a NAMED section they never locate | **FAIL** |

**Both verdicts are FAIL for the same reason, and it is not the reason the brief expected.**
The narrow obligation each brief item set out — the collapse/swap mutation must fail a named
test; the intra-section duplicate must be detected in both orders — **is met, decisively, in
both cases.** Each repair nevertheless fails because the property it establishes stops one
branch short of where it must hold, and in both cases a maintained document asserts that it
does not stop short.

---

## R2-F6 — VERDICT: `FAIL`

### The general property, stated before looking at the fix

*A refusal record must not assert a fact the run did not produce.* `SIGNER_CHAIN_UNSTABLE` is
raised on more than one distinct chain condition; whatever the signer says about which one
occurred must be true of the run that produced it, and two different conditions must not be
reported in the same words.

### Where that property must hold — enumerated mechanically, not from the finding text

`/usr/bin/grep -rn "CHAIN_UNSTABLE\|ChainUnstableError\|pendingOnly" ts/src ts/test scripts
verifier contracts` (search tooling validated first — see PROBES §0) returns every site. The
`continue` statements inside `readVaultState` are the complete set of ways the loop can fail
to return, and there are **THREE**, not two:

| # | Site | Condition | Reads issued |
|---|---|---|---|
| (a) | `ts/src/signer/vault.ts:230` | head MOVED / same-height reorg | yes |
| (b) | `ts/src/signer/vault.ts:179` | head is PENDING (hashless) — no reads issued | no |
| (c) | `ts/src/signer/vault.ts:223` | head was finalised, reads were issued, the **CONFIRMATION** was pending | **yes** |

(c) is the branch the D-057(5) verifier caused to be added. **The published account of this
error covers (a) and (b) and describes (c) as if it were (b).**

### What HOLDS

1. **(a) and (b) drive separately and each produces the behaviour and message claimed.**
   Probe `PO`: every head hashless → `pendingOnly=true`, **0 pinned reads issued**, message
   *"…every observation returned a pending block with no hash, so there was nothing to anchor
   to"*. Probe `MV`: a different finalised head every lookup → `pendingOnly=false`, 55 pinned
   reads, message *"…the head moved or was replaced under each pinned read"*.
2. **The tests pin the messages, against four mutations including two routes the previous
   verifier did not use.** Every one turns the suite red on the SAME named test,
   `names the CONDITION it failed on, not a generic one (R2-F6)` at
   `ts/test/vault.anchor.test.ts:304`:
   - collapse both messages into one string → **FAIL** (526/527)
   - swap the two messages → **FAIL** (526/527)
   - delete `pendingOnly = false` from the movement branch → **FAIL** (526/527)
   - hard-wire the throw to `new ChainUnstableError(SNAPSHOT_ATTEMPTS)` → **FAIL** (526/527)

   **BRIEF-V3 item 3's stated FAIL trigger did not fire.** The suite does not stay green under
   collapse or swap. That obligation is met and I record it as met.
3. **The controls behave the opposite way.** A stable head returns a normal snapshot with 11
   pinned reads (probe `OK`), so the signer has not simply started refusing everything. And
   `SIGNER_CHAIN_UNSTABLE` is still separable from `SIGNER_VAULT_UNREACHABLE` in **both**
   directions — `ts/test/reasoncodes.test.ts:240`, asserting each code present and the other
   absent.
4. **The project's STATUS record for this item is honest.** `docs/session-state.md` states in
   its header and in the §1 state table that the `8990255` corrections *"are NOT independently
   reverified"* and names this reverification as outstanding.
   `docs/review-2026-08-18-d055e/FINDINGS-LEDGER.tsv:14` carries `CONFIRMED … REPAIR`, where
   `CONFIRMED` is the adjudication of the FINDING, not a claim about the repair. No maintained
   document records `R2-F6` as closed, accepted or reverified.
   `docs/v1-1-register.md`, `docs/exit-criterion-packet.md`, `docs/gate-s2-evidence.md`,
   `HANDOFF.md` and `README.md` do not mention it at all.

### What FAILS

**F1 — condition (c) is reported with a message whose every clause the run contradicts.**

Probe `CP` drives (c) directly: the node serves a finalised head to each pin request and a
pending block to each confirmation. Observed at the frozen commit, unmutated:

```
[CP confirm-pending] ChainUnstableError pendingOnly=true
[CP confirm-pending]   message : no finalised head after 5 attempts: every observation
                                 returned a pending block with no hash, so there was
                                 nothing to anchor to
[CP confirm-pending]   FACTS   : pinned reads issued=55, head/confirm lookups=10
```

Five of the ten observations returned **finalised blocks with hashes**; **fifty-five pinned
reads were issued**; there was an anchor — `headHash` — and every read was pinned to it. The
message asserts the opposite on both counts. The same misdescription is repeated in two
docstrings:

- `ts/src/signer/vault.ts:131-134` — *"Every attempt saw a hashless (pending) head"*. In (c)
  **no attempt saw a hashless head.**
- `ts/src/signer/protocol.ts:110-112` — *"(b) the head had NO HASH — a pending block, which
  cannot be anchored to at all"*. In (c) the head had a hash and was anchored to.

This is `R2-F6`'s own defect — a record committing a claim the evidence does not support —
reproduced inside the repair for `R2-F6`, one branch away from the branch the repair fixed.

**F2 — the (c) classification is pinned by nothing, and `docs/decisions.md` A-078 states that
it is pinned.**

A-078(4) reads: *"It also found the same substitution one level in: a PENDING CONFIRMATION set
`pendingOnly = false` and was reported as movement. **Both fixed and now pinned by a test that
fails against the verifier's exact defeat.**"*

Mutation 5 restores exactly that pre-repair defect — `pendingOnly = false; continue;` in the
pending-confirmation branch. Result: **527/527, suite green, exit 0.**

The mutation is not dead. Under it, probe `CP` flips from
`pendingOnly=true / "no finalised head…"` to `pendingOnly=false / "the head moved or was
replaced under each pinned read"` — a reported movement on a chain that never moved, which is
the sentence `R2-F6` was filed about. The behaviour moved; nothing observed it.

**F3 — there is no "refusal detail", and two maintained records say there is.**

`ts/src/signer/protocol.ts:115` — *"so the refusal detail now distinguishes them"*.
`docs/decisions.md` A-077(2) — *"`R2-F6`: … the detail now distinguishes them, with no public
code split."*

Enumerated mechanically. `RefusalRecord` (`ts/src/signer/protocol.ts:499-512`) has nine
fields: `schemaVersion, chainId, vault, actionHash, evidenceHash, requestedVerdict,
reasonCodesHash, refusedAt, signer`. `Refusal` (`:514-526`) adds `blocking`, `signerFindings`
(both `ReasonCode` strings only) and the signed record. **Neither carries a detail, a message
or the `pendingOnly` flag.** `/usr/bin/grep -rn "detail" ts/src` finds `detail` fields in
`evaluate/checks.ts`, `decode/`, `propose/` — and in the signer, only the two comment lines
quoted above.

Every path that can raise the error discards it:
- `ts/src/signer/attest.ts:381-388` — `catch (error)` pushes the bare code and returns
  `refuse()`; `error` is not read again.
- `ts/src/signer/server.ts:118` and `ts/src/signer/main.ts:71` — `attestor.probe()` inside a
  bare `catch { }`, emitting `"vault unreadable"` / `"vault not readable"`.

So the distinguishing text the repair added **reaches no product output surface at all.** It
is observable only by an in-process caller of `chain.readVaultState` — which is what the test
and my probe do, and nothing else in the product does. The repair's substantive fix is to the
*published meaning of the enum* in `protocol.ts`, which is real and which HOLDS; the claim that
a refusal now carries a distinguishing detail does not.

**F4 — the sentence the finding quoted is still in `protocol.ts`, unstruck.**

`R2-F6` quoted `protocol.ts` as documenting the code as *"the vault was read repeatedly and
the chain moved each time"*. That sentence is still present verbatim at
`ts/src/signer/protocol.ts:121-122`, five lines below the new (a)/(b) enumeration, still
describing what distinguishes this code from `SIGNER_VAULT_UNREACHABLE`. A reader who reaches
it gets condition (a) as the code's meaning. This repository's own convention (A-080) is to
strike superseded text rather than leave it standing beside its correction. **Severity: LOW.**
Listed here rather than under residuals because it is the exact text the finding cited.

### What this evidence does NOT establish

- It does not establish that condition (c) — or (b) — is reachable against a **spec-conforming
  node.** Both `getBlock()` calls use viem's default `blockTag: "latest"`, and a conforming
  node always returns a hash for `latest`. Both probes drive a scripted node, exactly as
  `ts/test/vault.anchor.test.ts` does. (b) and (c) have **identical** reachability; the
  repository already treats (b) as reachable — it built the branch, the message and a test for
  it — so (c) is in scope on the project's own terms. I did not attempt to establish which
  real deployments can produce a hashless `latest`.
- Because there is no detail field (F3), F1's wrong message never reaches a **signed** D-012
  artifact. F1 is a defect in the diagnostic, not in the signed record. That cuts both ways and
  I record both: it lowers F1's severity and it is the evidence for F3.
- I did not run the Foundry or verifier suites; nothing in scope touches them.

---

## R4-F3 — VERDICT: `FAIL`

### The general property, stated before looking at the fix

*A guard that prints a claim about a NAMED SECTION must obtain every element of that claim
from that section, and must refuse rather than silently choose when the material it reads
offers more than one candidate.* Restated for this guard's two-operand comparison: **a `6/6`
must mean "the line §5.8 publishes equals the string the signer hashes" — not "some line
somewhere equals some line somewhere".**

### Where that property must hold — enumerated mechanically

`/usr/bin/grep -ln "Sentinel_Protocol_Lab_Proposal" scripts/*` returns **four** scripts, not
the two the finding named:

| Script | Scoped to its named section? |
|---|---|
| `scripts/check-type-strings.sh` | §5.8 — yes (awk), with the caveats below |
| `scripts/check-eval-codes.sh` | §5.7.1 — yes (awk) |
| `scripts/check-vendor-honesty.sh` | **NO** — see §RESIDUALS AND NEW, `V3-N2` |
| `scripts/check-review-scope.sh` | not a section claim |

Within `check-type-strings.sh` the comparison has **two operands**, and the `head -1`
construction appears on both — `:65` (spec) and `:66` (source), one line apart.

### What HOLDS — the assigned obligation, met decisively

1. **Intra-section duplicate publication IS detected, in BOTH orders.** A second, transposed
   `MandatePayload(...)` placed inside §5.8:
   - **after** the correct line (`T1`) → `type strings: §5.8 publishes 2 different lines for
     MandatePayload. … Refusing to pick one.` exit **1**
   - **before** the correct line (`T2`) → same refusal, exit **1**
2. **The refusal, not a neighbouring check, is what catches the decisive order.** Running the
   identical `T1` document against a copy of the guard with only the duplicate block removed
   (`/tmp/check-type-strings.NODUP.sh`, a pre-fix comparison):
   - `T1` shipped → exit 1 (refused) · `T1` NODUP → **exit 0, `6/6` clean pass**
   - `T2` shipped → exit 1 (refused) · `T2` NODUP → exit 1, but as **`DRIFT`**, i.e. caught by
     the neighbouring byte comparison

   So `T1` is the load-bearing probe and it is caught only by the new code. **`T2` alone would
   have proved nothing** — the trap COMMON-BRIEF names fourth.
3. **Cross-section is fixed too, on both scripts.** `T3`: the correct string planted in §5.9
   (which physically precedes §5.8) with §5.8 transposed → `DRIFT`, exit 1. `E4`: a code moved
   from §5.7.1 into §6 → `1 check(s) declared by the engine and absent from §5.7.1`, exit 1.
4. **The legitimate non-duplicate controls are NOT flagged, and I state them explicitly.**
   - Baseline, unmodified tree: `6/6` and `41/41`, both exit 0.
   - `T4`: a prose sentence added **inside §5.8** containing
     `` `MandatePayload(uint16 schemaVersion,bytes32 mandateId,address principal,...)` `` in
     backticks at the paragraph margin — a repeated substring that is not a publication →
     **`6/6`, exit 0, not flagged.**
   - Already in the baseline document and also not flagged: §5.8's own prose naming
     `MandatePayload`, `PolicyPayload` and `ActionPayload`.
   - `E1-control`: an added code with no prefix relation, `EVAL_ZZZ_UNDOCUMENTED`, **is**
     caught. The eval guard is not merely passing everything.

### What FAILS

**F5 — a decoy defeat printing the identical clean `6/6` still works, with §5.8 publishing a
transposed type string and the entire TypeScript suite green.**

The repair added the duplicate refusal to the **spec** operand at `:57-64`. The **source**
operand one line below is untouched:

```
    spec_line="$(grep -oE "^ {4}${name}\([^)]*\)$" "$SPEC_SECTION" | head -1 | sed 's/^ *//')"
    src_line="$(grep -oE "\"${name}\([^\"]*\)\"" "$SRC" | head -1 | sed 's/^"//; s/"$//')"
```

Probe `T5b` moves the decoy to that side: a comment above `MANDATE_TYPE` in
`ts/src/signer/eip712.ts` carrying a **transposed** string, and §5.8 transposed to match it.
`head -1` on the source picks the comment. Observed:

```
type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)   exit 0
ts suite: tests 527  pass 527  fail 0
```

**§5.8 now publishes a type string with a different typehash, a different digest and a
different recovered address; the guard certifies it; the golden-typehash assertion stays green
because `MANDATE_TYPE` itself was never touched.** This is the outcome the finding described,
and it is the outcome the guard's own header calls *"worse than an absent one"*.

`docs/decisions.md` A-077(2) states *"`R4-F3`'s guards now reading the named proposal sections
— **the decoy defeat no longer works** and the transposition control still fails correctly."*
It still works. It works from the other operand of the same comparison, in the same loop body,
one line away from the line that was repaired.

The paired control that must behave the opposite way: probe `T5`, the same decoy comment but
carrying the **correct** string above a **drifted** constant. Guard: `6/6`, exit 0 — also
defeated — but the eip712 module then dies at import with
`EIP-712 schema drift in MandatePayload`, so the suite catches the underlying drift. **The two
together are the boundary:** when the drift is in the constant the signer hashes, another
instrument catches it; when the drift is in what §5.8 **publishes**, nothing does, and the
guard whose sole job is that comparison prints `6/6`.

**F6 — the guard reads a PREFIX of §5.8, not §5.8, and the truncation is fail-open.**

`awk '/^### 5\.8 /{f=1;next} f && /^#{1,4} /{exit} f'` stops at the first line beginning with
one to four `#` and a space. A legitimate `#### 5.8.1` subsection is, to every reader, part of
§5.8. Probe `T7` adds `#### 5.8.1 Restatement for implementers` after the six published
strings, with a second **transposed** `MandatePayload` below it — still inside §5.8:

```
type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)   exit 0
awk-extracted section length: 21 lines
```

The duplicate is invisible because it lies outside the 21 lines the guard read, while the
printed claim still says "§5.8". **One ordinary editorial act — adding a subsection — silently
narrows the scope of a guard whose claim does not narrow with it.** This is the finding's own
sentence, "certifies a NAMED SECTION while grepping [something that is not it]", with 84 KB
replaced by "§5.8's first 21 lines".

The same boundary in `check-eval-codes.sh` is fail-**closed**: probe `E2` inserts
`#### 5.7.1.1 Grouping notes` mid-section and the guard reports **41 of 41 codes missing**,
exit 1 — loud and safe. The asymmetry is real and is the reason F6 is filed against the type
guard only.

### `check-eval-codes.sh` — was the argument carried across, or only applied to the named file?

**Half of it was, and the half that was is the half the finding demonstrated.**

- **Section scoping: CARRIED, and load-bearing.** `E4` proves it (a code documented only in §6
  is now reported absent from §5.7.1). Both scripts also fail closed on an empty extraction.
- **"Refuse rather than choose": NOT carried — and it does not need to be here.**
  `check-eval-codes.sh` performs a presence test with `grep -q`; it makes no choice among
  candidates, so intra-section duplication is not a defect for it. I checked this rather than
  assuming it.
- **The analogous defect — "any line will do" — is present and demonstrated.** `:52` is
  `grep -q "$code" "$SPEC_SECTION"`, an **unanchored substring** match. Probe `E1` adds
  `EVAL_ACTION_DEAD` to `EVAL_CODES`. It occurs **zero** times in the proposal
  (`/usr/bin/grep -c "EVAL_ACTION_DEAD\b"` → 0). The guard prints
  `eval codes: 42/42 engine checks documented in §5.7.1 (D-031)`, exit 0, because it matched
  inside `EVAL_ACTION_DEADLINE`.
  **NOT CURRENTLY LIVE:** across the 41 codes in `EVAL_CODES` today there are **0** prefix
  pairs (computed, not remembered). Recorded at the same standing the guard's own header gives
  `R4-F3` — an instrument defect, not a live false claim. **Severity: LOW.**

### What this evidence does NOT establish

- `T5b` and `T7` are **instrument defects**: each needs an edit to the repository, exactly as
  the original `R4-F3` defeat needed two. Neither is a false claim about the tree as it stands
  today — `T4` and the untouched baseline both certify correctly, and every type string occurs
  exactly once, inside §5.8, at this commit (verified: six `^    Name(` lines, all between
  lines 496 and 506).
- I did not test the guards under `scripts/test.sh`; I ran them directly, as the gate does.
- I did not audit §5.7.1's *descriptions* for correctness. The guard declares that limit
  itself ("Coverage, not correctness") and I did not disturb it.

---

## RESIDUALS AND NEW — kept out of the two verdicts above

**`V3-R1` (residual, R2-F6).** `ts/test/fakes.ts:185` constructs
`new ChainUnstableError(SNAPSHOT_ATTEMPTS)` — always `pendingOnly=false`. Every attest-layer
test therefore exercises only condition (a). Harmless **today** precisely because F3 holds (no
detail leaves the attestor); it becomes a gap the moment a detail field is added.

**`V3-R2` (residual, R2-F6).** The mixed case: one pending head, then a moving head. Probe
`MIX` reports `pendingOnly=false` with *"the head moved or was replaced under **each** pinned
read"* after an attempt that pinned no read at all (44 reads over 4 attempts, 9 lookups).
Milder than F1 — the quantifier ranges only over attempts that pinned something — but it is
the same class.

**`V3-N1` (new, MEDIUM — a question of scope, not mine to rule on).** BRIEF-V3 item 4 asked
whether the item's status is recorded as confirmed where it is pending. The status records are
clean (see HOLD-4). **Two substantive repair claims in `docs/decisions.md` are not:**
- A-078(4): *"Both fixed and now pinned by a test"* — mutation 5 falsifies "pinned" for the
  pending-confirmation half (527/527 green).
- A-077(2): *"the detail now distinguishes them"* and *"the decoy defeat no longer works"* —
  the first has no detail field to refer to (F3), the second is falsified by `T5b`.

`docs/session-state.md` already warns that the `8990255` corrections are unreverified, so the
reader is not left unguarded — but the sentences themselves state as fact things this
reverification measured to be false. **How they are corrected is John's call. I did not touch
them; I am recording that they need his ruling.**

**`V3-N2` (new, MEDIUM — the third sibling the R4-F3 repair did not reach).**
`scripts/check-vendor-honesty.sh:269`:

```
CAVEAT="$(grep -F 'is not evidence that current vendors miss Case 3' "$PROPOSAL" | head -1 …)"
```

A **whole-document grep with `head -1`** feeding a printed claim about a named section:
`"ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it"`. The script's
own comment two lines above declares itself *"the same shape as `check-type-strings.sh`, and
for the same reason."* It self-identifies as the sibling and was not swept.

Falsified (probe `V1`): weaken §7.2's caveat to `"This baseline makes the demo reproducible."`
and plant the original sentence in §6. §7.2 then contains the caveat **zero** times
(section-scoped count), and the guard prints
`ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it`, **stage exit 0.**
Control: the untouched tree gives the same `ok` line with the caveat genuinely in §7.2.

This is `R4-F3` verbatim in a third file, on a §7.5 Gate-5 vendor-honesty condition. **Out of
my assigned scope — filed, not adjudicated.**

**`V3-R3` (residual, LOW).** `scripts/check-type-strings.sh:94` prints `${checked}/6`. If a
name were dropped from the loop list at `:48-49`, the script would print `5/6` and **exit 0**.
Visible in the output, so not silent, but a partial certification with a success status.

**`V3-R4` (method note, recorded because it cost the last verifier time and nearly cost me
some).** On this machine `grep` is a zsh function wrapping `ugrep --ignore-files`; I used
`/usr/bin/grep` throughout and validated it by planting `CANARY_V3_STRING_9f3a` and confirming
a hit before trusting any zero result. Two live instances of the traps COMMON-BRIEF names:
(i) probe `T6`'s first run died in Python **before writing the file** and the guard then ran
against the *previous* probe's document, printing a `6/6` that meant nothing — caught only
because the traceback was visible above it; (ii) `docs/ablation-report.md` returns **0** for a
line-based grep of §7.2's caveat and **1** after wrap normalisation, which is the hard-wrap
trap exactly.

---

## Questions for John — not answered here

1. `docs/decisions.md` A-077(2) and A-078(4) carry three claims this reverification measured
   to be false (`V3-N1`). Historical entries in this file are normally left standing as
   history and annotated in place. Whether these are annotated, struck, or left is his call.
2. Whether `V3-N2` (`check-vendor-honesty.sh`) is folded into `R4-F3`'s remediation or raised
   as its own item is a scope decision (house rule 7).
3. Whether condition (c) warrants its own message and its own test, or whether the honest move
   is to say the error covers **three** conditions, is a design fork. I have not chosen one.
