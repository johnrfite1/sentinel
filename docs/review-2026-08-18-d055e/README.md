# D-055(e) — the bounded post-repair review, curated record

**Frozen commit reviewed: `7e0ab7f1057de278c09cc803ab4ca266f53399e1`.**
Four reviewers, four detached worktrees, four persistent evidence directories, at most two
concurrent. Scope fixed by John at D-056(d) **before** the review ran, which is what D-055's
T3 requires and what an agent may not do for itself.

## The arithmetic is DERIVED, not stated here

**`FINDINGS-LEDGER.tsv` is canonical: one row per finding.** Every count in every document
comes from `scripts/check-findings-ledger.sh`, which reads that ledger and fails if its
derivation disagrees with D-057(1)'s ruling. **Do not hand-count anything from this README.**

**23 finding IDs — 22 confirmed, 1 refuted.** Grouped for decision-making that is **20
disposition items, 19 confirmed**. `R3-F5`–`F8` share one repair pattern and may be decided
as one item, but **they remain four findings and four regression obligations.**

The first exit assessment said "20 findings". That was wrong: it grouped the cluster and then
counted lines. The ledger and its checker exist because of that error.

## Provenance

| | |
|---|---|
| Reviewed commit | `7e0ab7f` (detached worktrees, verified identical to HEAD at dispatch) |
| Reviewers | 4 — R1 certification/instruments, R2 authorization/effect pipeline, R3 onchain/corpus, R4 free lens |
| Adjudication | cross-assigned; **nobody adjudicated their own finding**, and the coordinating agent adjudicated NOTHING (it authored the code behind 11 of the 23) |
| Raw archive | `d055e-raw.tgz`, sha256 `afc4daf59d1d7e190fcc278b342130e1952f1e3191d5badf05de307498ab9ada` |
| Raw contents | 352 files, 6,102,309 bytes; verified round-trip against its manifest, 0 mismatches |

The raw archive is held **outside this repository** in private local storage; its path is
deliberately in no tracked file. `EVIDENCE-MANIFEST.txt` carries every relative path and
digest so a citation resolves against it without the bytes living in git.

## What is here, and how faithful

| Path | Fidelity |
|---|---|
| `briefs/` | the common brief and four lens briefs as issued, **path-sanitized only** |
| `reviewers/rN/` | each reviewer's own REPORT, NULL-RESULTS, DEAD-PROBES, COVERAGE, CRITIQUE, ATTESTATION — **path-sanitized only** |
| `adjudications/` | the four cross-adjudications, **path-sanitized only**, plus `probes/` with the adjudicators' own scripts |
| `ADJUDICATED-D055E.md` | the consolidated list and exit assessment, **path-sanitized only** |
| `REVIEW-STATE.md` | the running state record, **path-sanitized only** |

**Sanitization applied to every file in this package:** absolute paths for the review root, the
repository, the session scratchpad, `$TMPDIR` and the home directory were replaced with
placeholders. **Nothing else was altered.** No reviewer material was reconstructed, reworded,
summarised or improved — including where a reviewer was later shown to be wrong.

## The apparatus, and what it fixes

**Every reviewer wrote all six deliverables to disk before being counted complete**, and this
was a precondition in the brief rather than a request. That is the direct fix for round six,
where **seven of nine reviewers left nothing on disk** and their findings survive only as one
adjudicator's second-hand summary — a permanent, unrecoverable provenance gap.

Worktrees were provisioned with the submodule mount points **removed before linking**, the
hazard that cost round six most of its trees; `forge build` was verified in a worktree before
dispatch, so the deep profile was genuinely reachable. Evidence directories are in persistent
storage, **not a session scratchpad under the system temp directory** — round six's loss
traces directly to that choice.

## Limitations of this round

- **Coverage was traded for depth, and the reviewers said so.** R1 reports roughly 60% of its
  assigned surface unprobed, naming `fixtures/samples/**` — the surface that has produced a
  live certification defect in four consecutive rounds. R2 never exercised `propose/**` and
  barely touched `tools/**`, and read none of the corresponding proposal sections, so three
  of its findings quote the code's paraphrase of the spec. R3 did not run the corpus or the
  deep gate. Each is itemised in that reviewer's `COVERAGE.md`.
- **The corruption in `R1-F1` is NON-DETERMINISTIC** — 2 of 8 real-gate trials completed
  cleanly with the edit demonstrably applied. **One clean trial is not evidence a repair
  worked**, and that constrains how any fix to it must be verified.
- **R4's dead probes share one root cause the brief never mentioned:** the harness shell is
  zsh and every script under review is bash.
- The external raw archive exists in copies **on the same machine only**. It survives a
  scratchpad being cleared, not disk loss. Offsite storage remains owed.

## What this package does not do

It preserves and organises. **No finding, severity, verdict or adjudication was changed to make
the record tidier**, including the four findings against the coordinating agent's own repairs
and the one that refutes a premise it had asserted as measured.
