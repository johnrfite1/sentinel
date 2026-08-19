# Round six — the curated record

**Round six ran 2026-08-18 against frozen `140c59e`: nine independent reviewers, nine detached
worktrees, one evidence directory each, every lens briefed to prove the work fails. It returned
**91 findings** and John ruled it NOT CLEAN (D-052(a)).**

**Why this directory exists.** Until now round six was committed nowhere. `docs/` held review
directories for 2026-08-15, -16 and -17 and none for the round whose findings drove D-052,
D-053, D-055 and every repair from A-070 to A-076 — the round the current exit criterion was
BACKTESTED against. It survived only in one session's temporary scratchpad.

## Provenance

| | |
|---|---|
| Reviewed commit | `140c59e` (frozen, detached worktrees) |
| Reviewers | 9, directed lenses 1–8 plus one free lens |
| Findings | 91 · 0 CRITICAL · 18 HIGH · 44 MEDIUM · 29 LOW/INFO |
| Raw archive | `round-six-raw.tgz`, sha256 `830e7222bb79d43e7c2b1f5e3554633e560ce58db14ca067106092b4378bb3cc` |
| Raw manifest | sha256 `51894dd424c26b03784011f0772ba605dbab346eab6b528856bd003d3e69f87d` |
| Raw contents | 971 files, 9,551,737 bytes, plus 1 symlink |
| Verification | copy compared to source file-by-file, 971/971 identical, 0 mismatches |

The raw archive is held **outside this repository** in private local storage. Its path is
deliberately not recorded in any tracked file; ask John. The 936-plus raw probe artifacts are
**not** committed here — `EVIDENCE-MANIFEST.txt` carries every relative path and SHA-256 so a
citation in the adjudication can be resolved against the archive without the bytes living in git.

## What is here, and how faithful each part is

| Path | Fidelity |
|---|---|
| `ADJUDICATED-ROUND-SIX.md` | **byte-identical to the original.** No sanitization was needed — it contains no machine path and no key-shaped value |
| `briefs/lens1..9.md` | **byte-identical.** The nine directed briefs as issued |
| `briefs/COMMON-BRIEF.md` | one line sanitized: an absolute repository path became `<REPO>`. Nothing else changed |
| `reviewer-indexes/lens1-00-INDEX.txt` | reviewer-authored, worktree paths sanitized |
| `reviewer-indexes/lens4-L4-INDEX.txt` | reviewer-authored, worktree paths sanitized |
| `EVIDENCE-MANIFEST.txt` | relative paths + SHA-256 for all 971 preserved files |

## PROVENANCE GAP — the reviewers' final reports do not exist as files

**Seven of the nine reviewers left no report, coverage statement or provenance attestation on
disk, and none of the nine left a complete one.** `round6/reports/` was created and is empty.
The nine `lensN.md` files are the briefs issued **to** the reviewers, not reports **from** them.

What survives of each reviewer's own account:

| Lens | Surviving reviewer-authored summary |
|---|---|
| 1 | evidence index — findings mapped to files, two baselines, one NULL result |
| 4 | evidence index — findings mapped to files, three baselines |
| 2, 3, 5, 6, 7, 8, 9 | **none.** Only raw probe artifacts |

Their reports existed in the prior session's conversation history and are not recoverable from
disk. **They have not been reconstructed.** A reconstruction presented as an original would be
the exact failure this project exists to study, and `ADJUDICATED-ROUND-SIX.md` — written by the
adjudicating agent, not by the reviewers — is the only synthesis of record.

## Read the adjudication's own split before citing any finding

`ADJUDICATED-ROUND-SIX.md` separates **findings the adjudicator reproduced independently** from
**leads relayed on a reviewer's evidence**. That distinction is the point of the adjudication
step and it is load-bearing: round six's severities are otherwise **reviewer-assigned**, and
round five showed reviewers are accurate often enough to trust and wrong often enough that three
verdicts came back REFUTED, ALREADY-CLOSED and UNPROVEN. Under D-055's T2 severity for exit
purposes is the independent reviewer's or adjudicator's to assign — not the party exit depends on.

## Limitations of the round itself, recorded because they bound what it measured

- **The worktree provisioning was broken, and it cost most of the round its deep profile.**
  `session-state.md` prescribed symlinking `contracts/lib/*`; through a symlink forge's
  remapping auto-detection resolved **four** entries instead of five, omitting
  `@openzeppelin/contracts/`. That flows into solc's `settings.remappings`, the CBOR metadata,
  and therefore `targetCodeHash` — so all 50 committed view digests mismatched and the deep
  gate could not run. Reviewers ran the FAST profile. Fixed since at the argument level by
  `auto_detect_remappings = false` (A-071).
- **Nine-way concurrency degraded the evidence.** Load average above 100; **three probes flaked
  to a false CAUGHT and reversed on re-run**, and one probe was lost mid-mutation to a timeout
  that left a 0-byte log beside an "exit 0" notification. This is why D-056(e) caps the next
  review at four reviewers, run serially or at most two at a time.
- **No live model was called.** Reviewers had no `.env` by design, so the Gate 7 canary and
  every model-dependent arm went unexercised.
- **Round six cannot be the qualifying round for D-055 exit** — D-052(a) already ruled that, and
  it does not have to be re-run.

## What this package does NOT establish

It preserves and organises evidence. It does not re-adjudicate anything: **no finding, severity,
adjudication or historical conclusion has been changed here**, including ones later shown
understated. Where the record was wrong it stays wrong and the correction lives in the decision
log, because a curated package that quietly improves its own history is not evidence.
