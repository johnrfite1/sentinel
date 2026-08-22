# A-EXTRACT — ELEVENTH INDEPENDENT INSTRUMENT REVIEW

# VERDICT: FAIL

The tenth-review correction establishes a measured current timing basis and aligns the main
operator-facing cost passages: the fast run is 103 seconds with an approximately two-minute
budget, and the four-arm gate captures are 8m50s, 8m51s and 9m57s with a 10–15-minute budget.
The preserved artifacts were available and support those figures. The gate harness changed only
its `COST` comment; every executable line is byte-identical to Review 9's fully measured
executable subject.

The required search of every operative current record found one remaining conflict:

- **`F11-1` — `COVERAGE.md` still publishes a roughly 55-second whole-run duration.** Its
  current “Known weaknesses” section says the vendor-honesty cases take about four seconds each
  and *“A whole run is roughly 55 s.”* That is an unqualified statement about the current fast
  harness, beside the newly published **103-second** measurement in `CARD.md`,
  `GATE-BINDING.md` and `a-extract-gate.sh`. It is not inside a dated or superseded historical
  section. The current timing artifact also records 17 vendor-honesty executions, making the
  adjacent roughly-four-seconds-each estimate incompatible with a 55-second total even before
  consulting the 103-second measurement. This is the exact current one-minute-versus-two-minute
  conflict Review 10 required the correction to eliminate.

`F11-1` is sufficient for FAIL under D-065(3)'s published-figure bar. The bounded correction is
to align or explicitly historicise that one current whole-run statement from the preserved timing
basis, without rewriting historical review records. This review makes no repair.

---

## 0. Review identity and bar

| | |
|---|---|
| Branch | `step-3/isolated-signer` |
| Exact frozen subject | `31e768e6f2684ca6900e245a70c2cee41815a8f2` |
| Subject message | `A-EXTRACT: tenth-review duration figures measured and aligned. INSTRUMENT ONLY.` |
| Parent | `e7cf2e75da228237374e81bad73b495a1f508e76` — tenth independent review, VERDICT FAIL |
| Review 9 executable subject | `e22b81bfccbb466e46f1dd604c0f8b6ae6c840af` |
| Fast harness | sha256 `9e489ee6f4adab00535d036619738cf1faa97ec8ab070d22cbf29dd3e769bc1a` |
| Gate harness | sha256 `da8c15794f4a597bb0ab766f73e50dac87fd4edea62b22d533e4eef313acc4b1` |
| Frozen test patch | sha256 `3780e63a68ba013a085937c5019a837eb02fc4dda0238c21b2bd2074a908442b` |
| Threat model | D-065: faithful measurement in a non-adversarial environment; no hostile caller-variable finding is offered |
| Repository state at start | clean; HEAD and the supplied exact subject were the same commit object |
| Repository writes before this record | none |

I read the workspace instructions; D-058, D-059, D-065 and D-066; all four operative A-EXTRACT
records; both complete harnesses; `TESTS.patch`; `INSTRUMENT-REVIEW-9.md` and
`INSTRUMENT-REVIEW-10.md`; and the exact parent-to-subject diff. This is an
instrument-readiness review only. It does not approve a product repair, sign or reopen a gate,
certify or alter a claim, ratify a decision, publish, rename, or push.

## 1. The preserved timing evidence

The four preserved captures were still available in external temporary storage at review time.
Only basenames and hashes are recorded here so no machine-specific path enters the repository.

### 1.1 Four-arm gate captures

| Artifact basename | Birth | Modified | Delta | sha256 | Content check |
|---|---:|---:|---:|---|---|
| `aextract-r8-exact.yKWIpH/stdout.log` | 1787364215 | 1787364745 | 530 s = 8m50s | `12186c8a…b9d` | G1, G2, G2-causal and G3 each present; 7/7 REQUIRED, 11/11 CONTROL |
| `aextract-r8-final.aRzD50/stdout.log` | 1787364985 | 1787365516 | 531 s = 8m51s | `ee54b2ee…a31` | same four-arm and summary shape |
| `aextract-r8-repair.AlMvly/stdout.log` | 1787363398 | 1787363995 | 597 s = 9m57s | `bcb820d9…cc0` | same four-arm and summary shape |

Each is a 64-line complete stdout capture. Each has one passing G1 row, one passing G2 named
row, one passing G2-causal control and one passing G3 named row, plus the 7/7 and 11/11 summary.
The measurements therefore support the published range and a 10–15-minute operator budget.

### 1.2 Fast capture

The supplied timing record reports start `1787367484`, process completion `1787367587`, a
103-second elapsed run. The preserved directory birth time is `1787367484`; the last writes to
stdout, matrix and consumer transcript are `1787367582`, five seconds before the reported
process completion. The files themselves establish 98 seconds from creation through final output;
the supplied completion timestamp establishes the remaining process-exit interval. This split is
recorded rather than presenting a file mtime as the process end.

The captured contents support the run identity and outcome:

- stdout sha256 `36fdeda0…524`: one 21/52 REQUIRED summary, one 70/70 CONTROL summary and the
  required-failures completion line;
- matrix sha256 `af11a950…34a`: 136 rows — 52 REQUIRED (21 PASS, 31 FAIL), 70 CONTROL PASS and
  14 OBSERVED;
- stderr sha256 `e3b0c442…b855`: empty;
- consumer transcript sha256 `00838695…a3c`: the captured per-consumer output, including 17
  vendor-honesty executions.

The temporary artifacts are not durable repository evidence and may disappear after this review.
They were present and inspected here. Their hashes and timing/content facts above are the limit of
this review's reliance.

## 2. The executable did not change

The complete `a-extract-gate.sh` diff from Review 9's executable subject
`e22b81bfccbb466e46f1dd604c0f8b6ae6c840af` to the frozen subject changes only the `COST`
comment: four comment lines become five. Removing blank lines and lines whose first nonblank
character is `#` gives byte-identical streams, both sha256 `d1fc4a06…ebe`.

Both harnesses pass `bash -n`. The fast harness remains byte-identical to Review 9 at sha256
`9e489ee6…bc1a`; the gate harness's full-file hash changes from the fully measured
`9da8d329…827e` to the correctly published `da8c1579…c4b1` solely because of the comment.

I therefore did not repeat either expensive harness. Review 9's full behavioural evidence remains
applicable to the executable lines: fast, two byte-identical runs at 21/52 REQUIRED and 70/70
CONTROL; gate, 7/7 REQUIRED and 11/11 CONTROL, supervisor `0/5/0/5`, four logs, three banners per
log and the causal twin holding. That reliance does **not** make the remaining 55-second current
publication true and does not extend to the still-unmeasured deep profile.

## 3. Exact correction scope and current record consistency

The exact parent-to-subject correction is five files and only five:

| File | Insertions | Deletions | Correction |
|---|---:|---:|---|
| `CARD.md` | 2 | 2 | publishes 103 seconds / ~2 minutes and 8m50s–9m57s / 10–15 minutes |
| `COVERAGE.md` | 3 | 2 | publishes the three gate measurements and 10–15-minute budget |
| `GATE-BINDING.md` | 8 | 6 | updates current hash, executable-reliance limit and both duration publications |
| `RESULTS.md` | 4 | 2 | updates current hash and states the comment-only reliance |
| `a-extract-gate.sh` | 4 | 3 | changes only the `COST` comment |

No prior review record changed. Explicitly historical three-arm results and then-current hashes
remain intact.

Apart from `F11-1`, the operative current counts agree: fast 52 REQUIRED, 70 CONTROL,
14 OBSERVED, 136 rows, with 21 held and 31 failed at the pre-repair subject; gate 7 REQUIRED,
11 CONTROL, 3 OBSERVED, supervisor `0/5/0/5`, four logs plus the matrix. Searches found no
remaining unqualified current 15–20- or 15–25-minute gate budget, and no other current “about one
minute” phrase. The surviving old ranges are in `INSTRUMENT-REVIEW-10.md`, where they are the
explicit historical statement of its finding.

The missed `COVERAGE.md` sentence is different: it sits in the current “Known weaknesses” section,
has no historical qualifier and describes “A whole run”. It conflicts directly with the 103-second
current measurement. The correction is therefore internally incomplete even though its main cost
table and gate-binding passages agree.

## 4. Protected material, pinning and repository checks

- The parent-to-subject production/protected diff is empty across `scripts`, `ts`, `contracts`,
  `verifier`, `fixtures`, `.githooks`, the proposal, ablation report, signed pack and
  `TESTS.patch`.
- `TESTS.patch` remains sha256
  `3780e63a68ba013a085937c5019a837eb02fc4dda0238c21b2bd2074a908442b`.
- `docs/gate-s2-evidence.md` remains sha256
  `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589`.
- The live Gate 5 pin, live §2 table and pre-repair §2 table all remain
  `c9034750e56b8801be7cd31cce33c42caad209013a61ed7082155db33903959c`.
- Parent-to-subject and worktree `git diff --check`: PASS.
- `check-secrets.sh`: clean.
- `check-review-scope.sh`: 540/540 then-tracked files assigned; 158 remediation-surface and
  79 preservation-only files reported.
- `check-suite-floors.sh`: 92 Foundry, 527 TypeScript, 221 verifier tests, 7 samples,
  78 tamper cases and 30 modes, single-sourced from `scripts/test.sh`.
- `check-findings-ledger.sh`: all ruled totals match.
- `check-rename-gate.sh`: private repository; D-016 publication block intact.
- Workspace guards: 13 machine-state findings, all baselined, 0 new; PASS by ratchet.

These checks support scope and preservation. They do not reconcile the live 55-second and
103-second whole-run publications.

## 5. Limits and disposition

1. No full fast or gate harness was rerun because every executable line is byte-identical to
   Review 9's fully measured subject. The exact reliance and its limit are stated in §2.
2. File mtimes directly establish 98 seconds through the fast capture's last write; the supplied
   timing record establishes the 103-second process completion. That distinction is explicit in
   §1.2.
3. The deep `./scripts/test.sh --gate` profile remains unmeasured, as the operative records say.
   The eventual exact-candidate verifier still owns that invocation and its three banners.
4. The duration defect is documentary. It does not reverse an executable verdict, but it prevents
   a HOLD because the operative current fast cost is still stated two incompatible ways.
5. This verdict evaluates instrument readiness only. It does not approve implementation,
   discharge the deep-profile portion of D-059(7), or exercise any authority reserved to John.

**FAIL.** The measured timing correction is sound where applied, but one current operative
55-second whole-run statement remains. A FAIL consumes no implementation attempt. Nothing is
signed, ratified, certified, reaffirmed, published, renamed, pushed, repaired, or implemented by
this review.
