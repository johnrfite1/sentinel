# The D-055(e) review — scope manifest

**Scope fixed by John, D-056(d), BEFORE the review runs.** That ordering is the whole of
D-055's T3: *"scope is fixed by JOHN BEFORE the review"*, because D-047's anti-gaming clause
exists precisely because a round scoped narrowly enough comes back clean. **Nothing in this
file is an agent's choice about what gets looked at.** What an agent did was mechanise the
partition and check it for holes.

**The mechanical half is `scripts/check-review-scope.sh`, and it is the part that matters.**
John's requirement was that the remaining tracked documents be partitioned *"explicitly so the
claims surface is not covered merely by assertion"*. A table in a document IS an assertion:
it claims completeness and nothing checks it. This repository has now recorded three separate
hand-maintained status tables going stale while being cited as authority — register §13.4
(22 of 24 rows wrong), the gate's own coverage boundary, and `session-state.md` §3. So the
partition executes: **every tracked file is assigned to exactly one of R1–R3, and the script
exits non-zero if any is assigned to none.** Adding a file turns it red rather than letting it
slide into a gap. Verified against a probe: a new tracked file in an uncovered directory fails
it.

**What "exactly one" means here, stated precisely because the script's own header once
overstated it.** `assign()` is a shell `case`, and a `case` returns on its FIRST match. So each
file gets exactly one reviewer **by construction**, not by a check — **the script does NOT
detect overlapping patterns**, it resolves them by order. That is deliberate: first-match
precedence is what lets `ts/src/corpus/*` beat `ts/src/*` and it is how the seams below are
expressed. **The ordering is part of the specification.** Reordering the arms silently
reassigns files, and nothing but review catches that.

Current state at the provenance checkpoint, from the script's actual output:
**R1=175 · R2=46 · R3=150 — 371 of 371 tracked files assigned · 37 remediation files changed
since A-070 · 15 preservation-only files**, all assigned. **Do not trust that line — run
`./scripts/check-review-scope.sh`.**

**Preservation is counted apart from remediation deliberately.** The 15 files under
`docs/review-2026-08-18-round-six/` are round six's record, **faithfully preserved with
disclosed path sanitization**: they change no behaviour and repair nothing. Folding them into
"the remediation surface" would inflate the number needing scrutiny with documents nobody is
being asked to review as work.

**"Verbatim" would overstate it for the set as a whole, and that directory's README is the
authority on which is which.** `ADJUDICATED-ROUND-SIX.md` and the nine lens briefs ARE
byte-identical; `COMMON-BRIEF.md` and the two reviewer indexes had machine-specific paths
replaced, each disclosed there. They are still assigned — R1's, and R1 should read them — just
counted separately. It is a count in a document, which is the
species of claim this file exists to stop relying on, and it went stale once already while
being written: adding this manifest itself made it 355 of 356 until the script failed and the
gap was assigned.

---

## The four reviewers

| | Surface | D-050(1) surfaces covered |
|---|---|---|
| **R1** | certification and instruments | guards and gate · the D-010 verifier · the claims |
| **R2** | authorization and effect pipeline | signer · evaluator and decoders · simulation and effect pipeline |
| **R3** | onchain and corpus | vault · corpus, labels and ablation |
| **R4** | **wholly free lens** | the ninth surface, by being given none of the others |

All nine D-050(1) surfaces are covered. R1 additionally carries the cross-cutting canonical
records — both signed gate packs, `decisions.md`, `session-state.md`, `HANDOFF.md`, `README.md`
— and **must run the DEEP profile from the repaired isolated-worktree apparatus.**

**R4 is absent from `check-review-scope.sh`'s patterns deliberately.** Its brief is "no assigned
target, no preferred direction, no surface hints", so assigning it files would defeat it.
Coverage means R1–R3 partition the tree; R4 ranges over all of it.

## The remediation surface — 37 files changed since A-070

Thirty-five at A-076, plus `scripts/check-review-scope.sh` and this manifest from the
administrative commit. **Excludes the 15 preservation-only files.**

This is the half a whole-tree partition does not by itself establish, and it is the half that
matters most: **four of the five repairs *preceding* A-070 were defeated within 48 hours, and
A-070 through A-076 have had no independent review at all.**

| Reviewer | Files changed since A-070 |
|---|---|
| **R1** | `scripts/test.sh` · `scripts/check-secrets.sh` · `scripts/check-gate-immutability.sh` · `scripts/check-review-scope.sh` · `docs/d055e-scope-manifest.md` · `verifier/verify.py` · `verifier/test_verifier.py` · `docs/decisions.md` · `docs/session-state.md` · `docs/gate-s1-evidence.md` · `docs/gate-s2-evidence.md` · `docs/v1-1-register.md` · `docs/repair-protocol.md` · `docs/exit-criterion-packet.md` |
| **R2** | `ts/src/signer/{attest,protocol,vault,socket-path}.ts` · `ts/test/{vault.anchor,signer.e2e,reasoncodes,evaluate.checks,fakes,attestor.concurrency,propose,simulate}.ts` · `ts/src/tools/{sample-check,emit-samples}.ts` · `ts/package.json` · `Sentinel_Protocol_Lab_Proposal_v0_2.md` |
| **R3** | `contracts/foundry.toml` · `contracts/src/SentinelVault.sol` · `contracts/test/SentinelVault.backstops.t.sol` · `ts/src/corpus/run.ts` · `ts/src/ablation/report.ts` · `ts/test/ablation.test.ts` · `docs/ablation-report.md` |

Named repairs by reviewer, from D-056(d): **R1** — A-070, A-071, A-074, and the gate
stabilization. **R2** — A-072, D-053(b), A-074, A-075/`E3`. **R3** — atomic drain, the
invariant-campaign boundary, `D-09(c)`, `G-5`, `D-10`.

## Comments and printed claims travel with their source file

Assigned by file, not as a separate "claims" pile, because a claim in a comment is only
checkable against the code beside it. The exception is the cross-cutting records above, which
belong to R1 — they make claims *about* every surface, and R1 is the reviewer whose subject is
whether a claim matches its evidence.

## Seams, named rather than hidden

A partition draws lines through things that are actually connected. These are the places where
a reviewer will find the other side of its subject in someone else's scope, and both sides are
told:

- **`fixtures/injection/**` and `ts/src/spike/**` → R1** (Gate 7 is a gate, and D-007's "an
  unobserved canary is not evidence" is an instrument rule). But `ts/src/propose/fixtures.ts`
  and `ts/src/corpus/fixtures.ts` also read those fixtures, and they are **R2** and **R3**.
- **`docs/ablation-report.md` → R3** with its generator, but the report is also a published
  claim, which is R1's subject.
- **`ts/test/evaluate.checks.test.ts` → R2**, and it now carries `D-09(c)` and `D-10`
  regressions whose *subject* — corpus single-casedness, divergent ceilings — is **R3's**.
- **`verifier/**` → R1**, but what it verifies is R2's receipts over R3's fixtures.

## One operational note every reviewer needs

**To check whether another gate run is in flight, use `pgrep -f sentinel-gate`, not
`pgrep -f scripts/test.sh`.** Since A-076 the gate executes an immutable snapshot, so after its
bootstrap the process is `bash /tmp/sentinel-gate.XXXXXXXX --gate` and the old pattern matches
nothing.

This is called out because **round five's `D-11` — four reviewers clobbering one shared
baseline log — was FOUND with `pgrep -f scripts/test.sh`**, and that technique is recorded in
`docs/review-2026-08-17/lens-D-evaluator-and-decoders.json`. A reviewer reusing it now would
see a quiet tree and be wrong. Each reviewer has its own worktree and evidence directory this
round, which is the actual fix for `D-11`; this is the diagnostic that goes with it.

## What this manifest does NOT establish

It assigns files. It does not make a surface *reviewed* — that is the coverage statement each
reviewer returns, and a reviewer that ran nothing on an assigned surface must say so. It also
does not cover **untracked** material: notably, **round six's evidence and adjudication are not
committed anywhere in this repository** (`docs/` holds review directories for 2026-08-15, -16
and -17 and none for round six) and live only in a prior session's temporary scratchpad. That
is raised, not resolved.
