# V2 — COVERAGE: what I did not reach, and why

Commit: `c8d15a76425544148d7da2f8fa0c003feb6ad2b7`. Scope: `V3-N1` and `R4-F4` only.

---

## 1. Not reached on `V3-N1`

- **No non-shim route into the line-198 defect was demonstrated.** The defect is proved by a PATH
  shim (P3) and by a latent content route (C-quoted paths, 3.6). I could not construct a route
  reachable by ordinary use of *this* repository at *this* commit: there are 0 quote-triggering
  tracked paths, the glob-metacharacter hypothesis was disproved, and submodule gitlinks resolve
  normally. Someone weighing severity should weigh that. It does not change whether the call is
  guarded, which is what BRIEF-V2 item 5 asks.
- **I could not test the quoted-path route end-to-end inside the Sentinel worktree**, because
  demonstrating it requires a *committed* change to a file with such a name and COMMON-BRIEF
  forbids committing. I demonstrated the git mechanism in a throwaway repository instead and said
  so. What that does not show is how `check-review-scope.sh` as a whole behaves with such a file
  present — my reading is that loop 1 would flag it UNASSIGNED and mask the loop-2 drop, but that
  is reasoning, not a probe.
- **Only one bash.** Everything ran under bash 3.2.57, which is what `#!/usr/bin/env bash`
  resolves to here. `cd ""` being a successful no-op (residual R-1) and the `$?`-after-assignment
  idiom are both shell-version-sensitive; I did not test bash 4/5 or a `sh`-mode invocation.
- **I did not audit `assign()`'s partition content.** Whether `contracts/*` really should beat
  `ts/src/*`, whether any file is assigned to the wrong reviewer, and whether the deliberate
  first-match overlaps are the intended ones are all untested. I tested the instrument's honesty,
  not its correctness.
- **The non-git external calls were enumerated but only one was probed.** `wc`/`tr`/`printf` at
  line 131 were assessed by reading, not by making them fail. I judged the blast radius cosmetic;
  that judgement is not backed by a probe.
- **I did not check whether `check-review-scope.sh` is invoked anywhere it should be.** Its header
  says nothing runs it automatically and that this is deliberate (D-057(4)); I took that at face
  value and did not verify the claim, since it is R1's subject and not mine.

## 2. Not reached on `R4-F4`

- **I did not run `scripts/test.sh` or `scripts/test.sh --gate` at all.** So I verified that
  `check-suite-floors.sh` re-reads a mutated floor, but **not** that the gate enforces it — I have
  not observed `FLOOR BREACHED` with `VERIFIER_MIN_TAMPER=80`. The claim "these constants are what
  the gate asserts" is taken from the code and from the script headers, not measured. If someone
  needs the enforcement half confirmed, it is unconfirmed here.
- **I therefore did not measure any actual suite count.** Every number in my report is a *floor*
  read from `scripts/test.sh`. Whether the real Foundry/TypeScript/verifier counts equal
  92/527/209 today is untested by me, and `check-suite-floors.sh`'s own header is explicit that
  floors and counts are different things.
- **The 52 frozen files under `docs/review-2026-08-1*/` were not swept for staleness**, per the
  brief's rule. I did not spot-check whether anything under those paths is in fact a live document
  misfiled into a frozen directory — if such a file exists, my classification missed it by
  construction.
- **My sweep is line-based and is known-incomplete.** Residual R-4: this repository hard-wraps
  prose, and the `30 modes` duplicate straddles lines 351/352 and matched no regex I ran. I found
  it by reading. That means my "no other live duplicate exists" statement rests partly on having
  read the candidate sections, not purely on grep — and I read `docs/session-state.md` section 3,
  `docs/round-six-brief.md`, `README.md` and `HANDOFF.md` in full, but **not**
  `Sentinel_Protocol_Lab_Proposal_v0_2.md` (1080 lines), `docs/v1-1-register.md` (949 lines),
  `docs/gate-s2-evidence.md` (974 lines) or `verifier/REPORT.md` (1265 lines) in full. A
  wrap-split duplicate in any of those four would have escaped me.
- **Non-markdown surfaces were not swept.** I swept tracked `*.md` only. A suite count restated in
  a comment in `ts/`, in a JSON fixture, or in a shell script other than `scripts/test.sh` would
  not appear in my results. `scripts/test.sh` itself contains several hardcoded `50` corpus-fixture
  strings (residual R-5), found incidentally rather than by a systematic non-markdown sweep.
- **I did not adjudicate the classification question I raised.** Whether `docs/decisions.md`'s
  newest entry counts as a live claim (residual R-6) and whether `R4-F4`'s property covers all six
  floor constants or only three (question 1 in REPORT.md section 5) are both put to John
  unanswered, per COMMON-BRIEF. My FAIL verdict states which reading it rests on.

## 3. Out of scope by instruction — not examined at all

- Every other `D-057(5)` finding. I did not read the other reviewers' briefs or reports, did not
  look at `R1-F1`, `R3-F5/F6/F7`, `R2-F5/F6`, `R3-F8`, or any Solidity or TypeScript source.
- The primary tree was read **only** for the three files named in my assignment
  (`briefs/COMMON-BRIEF.md`, `briefs/BRIEF-V2.md`, `docs/repair-protocol.md`) and written **only**
  into `docs/review-2026-08-19-d057-targeted/reviewers/v2/`. No other file in the primary tree was
  opened or modified.

## 4. State left behind

- The V2 worktree is at `c8d15a76425544148d7da2f8fa0c003feb6ad2b7` with `git status --porcelain`
  showing only `?? ts/node_modules` (pre-existing, untracked). The `scripts/test.sh` mutation of
  section 4.5 was reverted and the revert verified by both `git diff --stat` and
  `git status --porcelain`.
- Nothing was committed, pushed, staged, renamed or published. No gate was signed or reopened.
- All probe scaffolding (the `git` shim, `sweep.sh`, `floorsweep.sh`, the throwaway repository)
  lives in a session scratch directory outside both trees.
