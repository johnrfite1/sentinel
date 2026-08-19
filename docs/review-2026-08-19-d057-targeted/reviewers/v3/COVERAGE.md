# V3 — COVERAGE

What this reverification touched, what it deliberately did not, and where a reader should NOT
take silence for a pass. Commit `c8d15a76425544148d7da2f8fa0c003feb6ad2b7`.

---

## Assigned scope, obligation by obligation

### `R2-F6` (BRIEF-V3 items 1–5)

| Obligation | Covered | Outcome |
|---|---|---|
| 1. Drive the pending-head path and the head-moved path **separately** | yes — probes `PO`, `MV`, scripted RPC | **HOLDS** — each produces the behaviour and message its docstring claims |
| 2. The pending case must not be reported in language asserting movement / disagreeing reads | yes — probes `PO`, `MV`, **`CP`** | **partial FAIL** — (b) is clean; the pending-**confirmation** state (c) is reported with two clauses the run contradicts (F1) |
| 3. Collapse the messages / swap them; a **named** test must fail | yes — 4 mutations, full suite each | **HOLDS** — all four kill `vault.anchor.test.ts:304`. The brief's stated FAIL trigger did not fire |
| 3′. The same argument on the sibling branch the repair also claims to have fixed | yes — mutation 5 | **FAIL** — 527/527 green; probe proves the mutation moves behaviour |
| 4. Classification — runtime | yes | **partial FAIL** — a pending state is not called movement (good), but is described with positive false assertions (F1) |
| 4′. Classification — project status records | yes — `/usr/bin/grep -rn "R2-F6" docs/ *.md` | **HOLDS** — nothing records it as closed/accepted/reverified; `session-state.md` explicitly flags it outstanding. Two **repair claims** in `decisions.md` are false (`V3-N1`) |
| 5. Controls: stable chain still reads; `SIGNER_VAULT_UNREACHABLE` still distinguishable | yes — probe `OK`, `reasoncodes.test.ts:240` | **HOLDS** — both directions asserted; signer has not started refusing everything |

### `R4-F3` (BRIEF-V3 items 1–4)

| Obligation | Covered | Outcome |
|---|---|---|
| 1. Intra-section duplicate, **both orders**, must not print a clean 6/6 | yes — `T1`, `T2`, plus the NODUP pre-fix comparison | **HOLDS** — and `T1` is caught **only** by the new refusal, `T2` by a neighbour |
| 2. Cross-section case too | yes — `T3` (type strings), `E4` (eval codes) | **HOLDS** on both scripts |
| 3. A legitimate non-duplicate control that must NOT be flagged | yes — `T4`, the untouched baseline, `E1-control` | **HOLDS** — stated explicitly and passed |
| 4. Carry the reasoning to `check-eval-codes.sh` | yes — `E1`, `E2`, `E4` and a computed prefix-pair scan | **section scoping carried; "any line will do" NOT** — `E1` defeats it, latent today (0 prefix pairs) |
| — the underlying ARGUMENT (COMMON-BRIEF's governing rule) | yes — sibling sweep over all four spec-reading scripts, and over both operands of the comparison | **FAIL** — `T5b` reproduces the original defeat from the source operand; `T7` shows the scope is §5.8's prefix, not §5.8 |

---

## Sibling enumeration — mechanical, recorded even where empty

**`R2-F6`.** `/usr/bin/grep -rn "CHAIN_UNSTABLE\|ChainUnstableError\|pendingOnly" ts/src ts/test
scripts verifier contracts`. Every `continue` in `readVaultState` enumerated by reading the
function end to end: **three** exit-without-return branches (`:179`, `:223`, `:230`). Every
consumer of the error enumerated: `attest.ts:381`, `server.ts:118`, `main.ts:71`, plus five
dev-tool call sites. Record shape read field by field from
`ts/src/signer/protocol.ts:499-526`. **No further siblings found.**

**`R4-F3`.** `/usr/bin/grep -ln "Sentinel_Protocol_Lab_Proposal" scripts/*` → four scripts.
Two are the finding's, one (`check-review-scope.sh`) makes no section claim, one
(`check-vendor-honesty.sh`) does and is unscoped — `V3-N2`. Within `check-type-strings.sh`,
both operands of the comparison enumerated: `head -1` at `:65` **and** `:66`; only `:65` is
guarded.

---

## What I did NOT cover — read this before treating anything here as a clean sweep

1. **Foundry (89/92 tests) and the Python verifier (209) were not run.** Nothing in either
   finding's blast radius touches Solidity or `verifier/`, and I did not verify that claim by
   running them — I verified it by reading the call graph. If a reader needs Solidity evidence,
   this report has none.
2. **The deep gate (`scripts/test.sh`) was not run.** I invoked the three guards directly. A
   guard that behaves differently under the gate's environment would not be visible to me.
   COMMON-BRIEF forbids editing `test.sh` during a gate run; I did neither.
3. **Reachability of a hashless `latest` against a real node is unestablished.** Both the (b)
   and (c) branches are driven through a scripted mock. They have identical reachability, and
   the repository already treats (b) as real, but "a production RPC provider can do this" is
   not something I measured.
4. **`T5b`, `T7`, `T6`, `E1` and `V1` are instrument defects, not live false claims.** Each
   requires a repository edit. At this commit the guards certify correctly: six type strings,
   each exactly once, all inside §5.8; 41 eval codes, all present in §5.7.1; §7.2's caveat
   genuinely in §7.2. I state this because the guard's own header draws the same distinction
   for `R4-F3` and blurring it would overstate my result.
5. **I did not check whether §5.7.1's descriptions are correct**, only that the codes appear.
   The guard declares that limit itself.
6. **I did not read the other reviewers' work** (v1, v2, v4, v5 directories) and my results are
   independent of theirs. If two of us reach the same conclusion, that is agreement, not
   corroboration by a second method.
7. **No mutation-testing run over the whole suite.** My mutations were five hand-placed edits
   chosen from the enumerated branches, not `scripts/mutate.sh`. A branch I did not enumerate
   is a branch I did not test.
8. **`V3-N2` is filed, not investigated to completion.** I ran one falsification and one
   control on `check-vendor-honesty.sh` and stopped, because it is outside D-057(9)'s scope for
   this reviewer. Its other whole-document greps (`:218` and the §2/§13 awk blocks) were read
   but not probed. **Do not read this report as clearing them.**

---

## Instrument hazards encountered, and what they would have looked like if missed

| Hazard | How it would have read | How it was caught |
|---|---|---|
| `grep` is a `ugrep --ignore-files` wrapper | a clean sweep | planted `CANARY_V3_STRING_9f3a`, confirmed the hit, used `/usr/bin/grep` throughout |
| zsh glob on `--include=*.ts` | `no matches found`, easily skimmed past | quoted the pattern; re-ran |
| `EXIT=$?` after a pipe reads `head`'s status | every probe "exit 0" | re-ran with `out=$(cmd); rc=$?` |
| `T6`'s Python died before writing the file | a `6/6` pass that was really the previous probe's document | traceback printed above the guard line; probe harness changed to re-copy the original first |
| hard-wrapped prose | `docs/ablation-report.md` grep → **0** hits for a caveat that is there | wrap-normalised (`tr '\n' ' ' \| tr -s ' '`) and got **1** |
| a mutation that changes nothing | mutation 5's green suite would have meant "correctly unaffected" | re-ran the behavioural probe under mutation 5 and showed `CP` flips `pendingOnly` and its message |

---

## Verdict summary

| Finding | Verdict | Single most load-bearing piece of evidence |
|---|---|---|
| `R2-F6` | **FAIL** | Mutation 5 restores the pre-repair pending-confirmation defect; suite **527/527 green**, while the probe shows the same mutation flips a never-moving chain into "the head moved" |
| `R4-F3` | **FAIL** | `T5b`: `type strings: 6/6 published in §5.8 match eip712.ts exactly` + suite 527/527, with §5.8 publishing a **transposed** type string |

Residuals (`V3-R1`–`V3-R4`) and new items (`V3-N1`, `V3-N2`) are in REPORT.md, kept separate
from the failures. Nothing here is signed, certified, ratified or committed; the three design
questions raised are John's.
