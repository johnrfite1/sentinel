# V3 — PROBES

Every probe below was run in the V3 worktree at
`c8d15a76425544148d7da2f8fa0c003feb6ad2b7`. `<WORKTREE>` is that checkout; all repository
paths are repository-relative. Commands are copy-pasteable after `cd <WORKTREE>`.

**Restoration.** Originals were copied to `/tmp/vault.ts.orig`, `/tmp/eip712.orig.ts`,
`/tmp/checks.orig.ts`, `/tmp/spec.orig.md` before the first edit and `diff -q`'d back after the
last. Final state verified: all four CLEAN, `git rev-parse HEAD` unchanged, all three guards
green. The only file left added is `ts/probes/v3-r2f6-probe.ts` (mine, untracked, not part of
the suite).

---

## §0 — Instrument validation, done FIRST

**`grep` on this machine is not `grep`.** `type grep` shows a zsh function that execs
`ugrep -G --ignore-files --hidden -I --exclude-dir=…`. `--ignore-files` honours ignore files,
so a repository path can return zero hits that read exactly like a clean sweep. **Every search
in this report used `/usr/bin/grep` explicitly.**

Validated rather than assumed:

```
echo "// CANARY_V3_STRING_9f3a" >> ts/src/signer/vault.ts
/usr/bin/grep -rn "CANARY_V3_STRING_9f3a" ts/src ts/test scripts docs
  → ts/src/signer/vault.ts:272:// CANARY_V3_STRING_9f3a       (exit 0)
```

Also confirmed: zsh eats an unquoted `--include=*.ts` (`no matches found`), which silently
turns a sweep into an error; and this shell's `IFS` is `space tab newline nul` here, but I
avoided IFS-dependent loops regardless.

**Baselines, before any mutation.**

```
cd <WORKTREE> && git rev-parse HEAD
  → c8d15a76425544148d7da2f8fa0c003feb6ad2b7
cd <WORKTREE>/ts && npm test
  → tests 527  suites 91  pass 527  fail 0
cd <WORKTREE> && ./scripts/check-type-strings.sh   → 6/6 …  exit 0
cd <WORKTREE> && ./scripts/check-eval-codes.sh     → 41/41 … exit 0
cd <WORKTREE> && ./scripts/check-vendor-honesty.sh → exit 0
```

---

## Part A — `R2-F6`

### A.1 Behavioural probe: `<WORKTREE>/ts/probes/v3-r2f6-probe.ts`

A standalone JSON-RPC mock (same shape as `ts/test/vault.anchor.test.ts`'s `mockNode`, written
independently so it can script the CONFIRMATION lookup separately from the PIN lookup). Run:

```
cd <WORKTREE>/ts && node probes/v3-r2f6-probe.ts
```

Scenarios and what each proves it MOVED:

| Scenario | Scripted `latest` responses | Purpose |
|---|---|---|
| `CP` | finalised, pending, finalised, pending, … | pin succeeds, **confirmation** is pending — condition (c) |
| `PO` | every response pending | condition (b) |
| `MV` | a different finalised block every response | condition (a) |
| `OK` | one finalised block | **success control** |
| `MIX` | pending, then a moving finalised head | residual `V3-R2` |

Output at the frozen commit, unmutated:

```
[CP confirm-pending] ChainUnstableError pendingOnly=true
[CP confirm-pending]   message : no finalised head after 5 attempts: every observation returned a pending block with no hash, so there was nothing to anchor to
[CP confirm-pending]   FACTS   : pinned reads issued=55, head/confirm lookups=10
[PO pending-only]    ChainUnstableError pendingOnly=true
[PO pending-only]      message : no finalised head after 5 attempts: every observation returned a pending block with no hash, so there was nothing to anchor to
[PO pending-only]      FACTS   : pinned reads issued=0,  head/confirm lookups=5
[MV moved]           ChainUnstableError pendingOnly=false
[MV moved]             message : no stable block after 5 attempts: the head moved or was replaced under each pinned read
[MV moved]             FACTS   : pinned reads issued=55, head/confirm lookups=10
[OK stable]          RETURNED a snapshot at block 42 hash 0x77290c5c…; pinned reads issued=11
[MIX pending-then-moved] ChainUnstableError pendingOnly=false
[MIX …]                message : no stable block after 5 attempts: the head moved or was replaced under each pinned read
[MIX …]                FACTS   : pinned reads issued=44, head/confirm lookups=9
```

**Reading.** `PO` and `MV` are correct and are the paired opposites of each other. `OK` is the
success control — the signer has not started refusing everything. `CP` and `PO` are
**indistinguishable in the record** (same flag, same message) although one issued 55 pinned
reads against a finalised, hashed head and the other issued none; the `FACTS` line is measured
from the mock's own request log, not asserted.

### A.2 Mutation sweep — four routes, all caught

Each mutation applied to `ts/src/signer/vault.ts`, full suite run, file restored from
`/tmp/vault.ts.orig`.

| # | Mutation | Route | Result |
|---|---|---|---|
| M1 | both message branches replaced by `` `the chain was not stable after ${attempts} attempts` `` | the reviewer's own defeat | **526/527** |
| M2 | the two message branches swapped | the reviewer's own defeat | **526/527** |
| M3 | `pendingOnly = false;` deleted from the movement branch (`:232`) | **classifier, not string** | **526/527** |
| M4 | `throw new ChainUnstableError(SNAPSHOT_ATTEMPTS, pendingOnly)` → `…(SNAPSHOT_ATTEMPTS)` | **throw site** | **526/527** |

All four fail the **same named test**:
`test at test/vault.anchor.test.ts:304:5 — names the CONDITION it failed on, not a generic one (R2-F6)`.
Assertion messages differ per route (`/pending block with no hash/` for M1/M2 and M4's flag
equality; `true !== false` for M3), which is how I know each mutation was observed by a
different assertion and not by one blanket check.

### A.3 Mutation 5 — the one that survives

```
# restore the PRE-REPAIR defect in the pending-CONFIRMATION branch (vault.ts:223)
                const confirm = await client.getBlock();
                if (confirm.hash === null) {
                    pendingOnly = false;   // MUTATION 5
                    continue;
                }
```

```
cd <WORKTREE>/ts && npm test
  → tests 527  suites 91  pass 527  fail 0   ← GREEN
```

**Proof the probe MOVED** (the trap COMMON-BRIEF names second). Same mutation, probe rerun:

```
[CP confirm-pending] ChainUnstableError pendingOnly=false
[CP confirm-pending]   message : no stable block after 5 attempts: the head moved or was replaced under each pinned read
```

i.e. under M5 a chain that never moved is reported as having moved — the exact sentence
`R2-F6` was filed about — and no test anywhere notices. `docs/decisions.md` A-078(4) says this
branch is *"now pinned by a test"*.

### A.4 Reachability of the message — mechanical enumeration

```
/usr/bin/grep -rn "readVaultState\|\.probe()" ts/src verifier scripts
```

Product call sites and what each does with the error:

| Site | Handling |
|---|---|
| `ts/src/signer/attest.ts:381` | `catch (error)` → pushes bare `SIGNER_CHAIN_UNSTABLE`, `error` never read again |
| `ts/src/signer/server.ts:118` (`status`) | bare `catch { }` → `notes.push("vault unreadable")` |
| `ts/src/signer/main.ts:71` (startup) | bare `catch { }` → `"WARNING: vault not readable at …"` |
| `ts/src/tools/sample-check.ts:188`, `ts/src/tools/emit-samples.ts:422`, `ts/src/corpus/run.ts:415/625/669` | dev tooling, not a refusal surface |

Record shape: `RefusalRecord` `ts/src/signer/protocol.ts:499-512` (nine fields, no message);
`Refusal` `:514-526` (`blocking`, `signerFindings` — `ReasonCode` strings only).
`/usr/bin/grep -rn "detail" ts/src` finds no `detail` anywhere in the signer's types.

### A.5 Controls that must behave the opposite way

- `ts/test/reasoncodes.test.ts:240` — `SIGNER_CHAIN_UNSTABLE` present / `SIGNER_VAULT_UNREACHABLE`
  absent, **and the mirror**. Green at baseline and under every mutation above, so the
  distinction is not collateral damage from my edits.
- Probe `OK` — a stable chain still returns a full snapshot with exactly 11 pinned reads.
- Baseline suite 527/527 before and after the sweep.

### A.6 Status-record sweep (BRIEF-V3 item 4, second sense)

```
/usr/bin/grep -rn "R2-F6" docs/ *.md
```

Hits: `docs/session-state.md` ×2 (both stating the corrections are NOT reverified);
`docs/review-2026-08-18-d055e/` reviewer + adjudication artifacts (historical, preserved by
A-080 on purpose); `docs/review-2026-08-18-d055e/FINDINGS-LEDGER.tsv:14`
(`CONFIRMED … REPAIR` — the finding's adjudication, not a repair status);
`docs/decisions.md` A-077 and A-078. **Zero** hits in `docs/v1-1-register.md`,
`docs/exit-criterion-packet.md`, `docs/gate-s2-evidence.md`, `HANDOFF.md`, `README.md`.
Nothing records it as closed, accepted or reverified. See `V3-N1` for the two A-07x claims.

---

## Part B — `R4-F3`

All spec edits applied by `/tmp/spec_probe.py`, which re-copies `/tmp/spec.orig.md` first, so
no probe can inherit a previous probe's document. (It did once, before that guard was added —
see `T6` below.)

### B.1 Intra-section duplication — the assigned obligation

The wrong copy is `MandatePayload(…)` with `bytes32 mandateId,address principal` transposed to
`address principal,bytes32 mandateId` — a different typehash, a different digest.

| Probe | Document | Guard output | Exit |
|---|---|---|---|
| `T1` | correct line, then WRONG copy, both inside §5.8 | `§5.8 publishes 2 different lines for MandatePayload. … Refusing to pick one.` | **1** |
| `T2` | WRONG copy, then correct line, both inside §5.8 | same refusal | **1** |

### B.2 Which check caught it — the "caught by the wrong check" test

`/tmp/check-type-strings.NODUP.sh` is `scripts/check-type-strings.sh` with **only** the
`spec_hits > 1` block deleted; a pre-fix comparison.

```
T1 shipped   -> exit=1  :: type strings: §5.8 publishes 2 different lines for MandatePayload.
T1 NODUP     -> exit=0  :: type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)
T2 shipped   -> exit=1  :: type strings: §5.8 publishes 2 different lines for MandatePayload.
T2 NODUP     -> exit=1  :: type strings: DRIFT in MandatePayload
baseline shipped -> exit=0 :: 6/6 …
baseline NODUP   -> exit=0 :: 6/6 …
```

**`T1` is the load-bearing case** — without the new block it is a silent clean pass. **`T2`
would have proved nothing**: the neighbouring byte comparison catches it either way. Exit
codes captured with `out=$(...); rc=$?` rather than through a pipe, after an earlier run
mistakenly read `head -3`'s status (EXIT STATUS 0 IS NOT SUCCESS).

### B.3 Cross-section, and the legitimate controls

| Probe | Document | Result |
|---|---|---|
| `T3` | correct string planted in §5.9 (physically **before** §5.8), §5.8 transposed | `DRIFT in MandatePayload`, exit **1** |
| `T4` **(control)** | a prose sentence inside §5.8 mentioning `` `MandatePayload(uint16 schemaVersion,bytes32 mandateId,address principal,...)` `` in backticks | `6/6`, exit **0**, **not flagged** |
| baseline **(control)** | untouched tree | `6/6`, exit **0** |

Also unflagged in the baseline: §5.8's own prose naming `MandatePayload`, `PolicyPayload` and
`ActionPayload`. Every type string occurs exactly once at this commit —
`/usr/bin/grep -n "^    Name("` returns six lines, 496–506, all inside §5.8.

### B.4 `T5` / `T5b` — the source operand

`T5`: a comment above `MANDATE_TYPE` in `ts/src/signer/eip712.ts` carrying the **correct**
string; the constant itself transposed.

```
./scripts/check-type-strings.sh  → 6/6 …   exit 0        ← guard defeated
node --test test/eip712.test.ts  → Error: EIP-712 schema drift in MandatePayload: …
```

`T5b` (**the dangerous direction**): the comment carries the **transposed** string, the
constant is left **correct**, and §5.8 is transposed to match the comment.

```
./scripts/check-type-strings.sh  → type strings: 6/6 published in §5.8 match eip712.ts exactly (D-023)   exit 0
cd ts && npm test                → tests 527  pass 527  fail 0
```

**§5.8 publishes an unusable type string; every instrument is green.** `T5` is `T5b`'s paired
control and behaves the opposite way — the drift is caught, by a different instrument, which
is exactly the boundary that makes `T5b` the finding.

### B.5 `T6` / `T7` — the section boundary

`T6` (first attempt) inserted a bare `# a stray level-1 line inside §5.8`. **The first run of
`T6` was a DEAD PROBE**: the Python died on an off-by-one assertion *before writing the file*,
so the guard ran against `T4`'s document and printed `6/6` — a result that meant nothing. It
is recorded because it is precisely the class COMMON-BRIEF warns about, and it was visible
only because the traceback printed above the guard output. Re-run after the fix, `T6` defeats
the guard.

`T7` is the realistic form:

```
#### 5.8.1 Restatement for implementers

For convenience the mandate type string is repeated here:

    MandatePayload(uint16 schemaVersion,address principal,bytes32 mandateId,…)   ← TRANSPOSED
```

inserted after the six published strings, still inside §5.8 by any reader's reading.

```
./scripts/check-type-strings.sh → 6/6 published in §5.8 match eip712.ts exactly   exit 0
awk '/^### 5\.8 /{f=1;next} f && /^#{1,4} /{exit} f' … | wc -l   → 21
```

The guard read 21 lines and called them §5.8.

**Paired opposite on the sibling script.** `E2` inserts `#### 5.7.1.1 Grouping notes` into
§5.7.1: `eval codes: 41 check(s) declared by the engine and absent from §5.7.1`, exit **1** —
fail-CLOSED. Same construction, opposite failure direction, which is why F6 names only the
type guard.

### B.6 `check-eval-codes.sh`

| Probe | Change | Result |
|---|---|---|
| baseline **(control)** | none | `41/41 … documented in §5.7.1`, exit 0 |
| `E4` | `EVAL_ACTION_DEADLINE`'s only mention moved from §5.7.1 into §6 | `1 check(s) … absent from §5.7.1`, exit **1** — section scoping is load-bearing |
| `E2` | `#### 5.7.1.1` subsection mid-section | 41 of 41 reported missing, exit **1** — fail-closed |
| `E1` | `"EVAL_ACTION_DEAD"` added to `EVAL_CODES`; occurs **0** times in the proposal | `42/42 … documented in §5.7.1`, **exit 0** — defeated by unanchored `grep -q` matching inside `EVAL_ACTION_DEADLINE` |
| `E1-control` | `"EVAL_ZZZ_UNDOCUMENTED"` added (no prefix relation) | `1 check(s) … absent`, exit **1** — correctly caught |

Prefix relations among today's 41 codes, computed not remembered:

```
sed -n '/^export const EVAL_CODES = \[/,/^\] as const;/p' ts/src/evaluate/checks.ts \
  | /usr/bin/grep -oE '"EVAL_[A-Z0-9_]+"' | tr -d '"' | sort -u
  → 41 codes; 0 prefix pairs
```

So `E1` is latent, not live.

### B.7 `V1` — the third sibling (`scripts/check-vendor-honesty.sh`), out of scope, filed

```
# 7.2's caveat weakened in place; the original sentence planted in 6.
awk '/^### 7\.2 /{f=1;next} f && /^#{1,4} /{exit} f' Sentinel_Protocol_Lab_Proposal_v0_2.md \
  | /usr/bin/grep -c "is not evidence that current vendors miss Case 3"   → 0

./scripts/check-vendor-honesty.sh | /usr/bin/grep "7.2"
  → "  ok    the ablation report carries §7.2's caveat verbatim, as §7.2 words it"
./scripts/check-vendor-honesty.sh >/dev/null 2>&1; echo $?   → 0
```

Control: untouched tree gives the same `ok` line with the caveat genuinely present in §7.2.

**Hard-wrap trap, live.** `/usr/bin/grep -c` for that caveat in `docs/ablation-report.md`
returns **0**; `tr '\n' ' ' | tr -s ' '` then grep returns **1**. A line-based search on that
file reads exactly like an absence. The guard's own `norm()` handles this correctly; my first
check did not, and I only found out by normalising.

---

## Restoration verified

```
diff -q ts/src/signer/vault.ts     /tmp/vault.ts.orig     → CLEAN
diff -q ts/src/signer/eip712.ts    /tmp/eip712.orig.ts    → CLEAN
diff -q ts/src/evaluate/checks.ts  /tmp/checks.orig.ts    → CLEAN
diff -q Sentinel_Protocol_Lab_Proposal_v0_2.md /tmp/spec.orig.md → CLEAN
git rev-parse HEAD → c8d15a76425544148d7da2f8fa0c003feb6ad2b7
./scripts/check-type-strings.sh → 6/6, ./scripts/check-eval-codes.sh → 41/41,
./scripts/check-vendor-honesty.sh → exit 0
```
