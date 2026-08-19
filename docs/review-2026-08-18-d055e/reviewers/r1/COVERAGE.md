# REVIEWER 1 — COVERAGE

**Commit:** `7e0ab7f1057de278c09cc803ab4ca266f53399e1`. Worktree `w1`, detached, symlinked libs.

## What I actually ran

| Thing | Command | Result |
|---|---|---|
| **DEEP GATE (the condition of the round)** | `forge build --root contracts && ./scripts/test.sh --gate` | Completed. `GATE PASSED`, profile confirmed `gate`, exit 0. Full 1298-line output in `deep-gate-run.txt`. |
| Baseline tree state | `git diff HEAD --stat -- .` | Only the two expected submodule-symlink entries. Captured before any probe. |
| In-flight gate check | `pgrep -f sentinel-gate` | None. |
| Scope guard baseline | `./scripts/check-review-scope.sh` | 371/371 assigned, 37 remediation files. |
| Scope guard probe | `SENTINEL_SCOPE_BASE=deadbeefdeadbeef ./scripts/check-review-scope.sh` | **R1-F2.** Prints "0 file(s) … all assigned", exit 0. |
| Scope guard invocation sweep | `grep -rn check-review-scope` over the tracked tree | **R1-F3.** Prose only. |
| Snapshot reachability | `probes/probe-snapshot-reachable.sh` (isolated `TMPDIR`) | **R1-F1.** Two arms, both reproduce syntax error + no `GATE PASSED` + **exit 0**. |
| Immutability harness, isolated | `TMPDIR=<iso> ./scripts/check-gate-immutability.sh` | 5/5, 0 snapshots leaked. `probe-harness-leak.out`. **N2.** |
| Leaked-snapshot forensics | `find $TMPDIR -name 'sentinel-gate.*'`, content inspection | Six, identified as the harness's own subjects, predating the commit. |

## Source read closely

`scripts/test.sh` (all 1142 lines: bootstrap, both new count floors, verifier floors, the
`COVERAGE` heredoc), `scripts/check-gate-immutability.sh` (all 256), `scripts/check-review-scope.sh`
(all 144), `verifier/verify.py` targeted (the A-074 conformance function and both its call
paths, the verdict cross-check, the refusal verdict handling), `docs/decisions.md` D-056/A-076,
`docs/v1-1-register.md` §13.4/§13.6/§14, `docs/d055e-scope-manifest.md`, `.githooks/`.

## What I did NOT reach, and why

Named explicitly, because a surface I was assigned and did not exercise must appear here.

1. **`fixtures/samples/**` — not exercised directly.** I read the verifier's logic over samples
   and observed the gate's aggregate result (7 samples, 78 tamper cases, 30 modes, all floors
   met), but I did **not** construct a sample, tamper one by hand, or run
   `verify.py` against a bundle I built. **The wrong-purpose-ALLOW defeat that A-074 exists to
   close was therefore not re-attempted.** N5 is a reading-and-grep result, not an executed
   one. Given the brief's statement that `verifier/**` has produced a live certification defect
   in four consecutive rounds *inside the previous round's repairs*, this is the most important
   gap in my coverage and I am naming it as such rather than letting the gate's green
   verifier line stand in for it.
2. **`ts/src/spike/**` and the Gate 7 injection fixtures — not reached at all.** Assigned to me
   ("Gate 7 IS a gate"). I spent my depth budget on the gate bootstrap and the scope guard. The
   gate run exercised `ts/test/canary.test.ts` as part of the 513, and the canary history line
   printed, but I did not read the spike, the injection fixtures, or `fixtures/d019-revisit/*`.
   **No conclusion of mine covers Gate 7.**
3. **A-070 and A-071 — not independently reviewed.** My brief named A-070, A-071 and A-074.
   I attacked A-074 (N5) and the new gate-stabilization work (R1-F1). A-070's credential-guard
   nesting residual and A-071's apparatus repair were read in the register only.
4. **`check-secrets.sh`, `check-class-coverage.sh`, `check-vendor-honesty.sh`,
   `check-label-integrity.sh`, `check-type-strings.sh`, `check-eval-codes.sh`,
   `check-rename-gate.sh`, `mutate.sh` — observed passing in the gate, not attacked.** ~1900
   lines of guard logic in my scope that I did not probe. `check-vendor-honesty.sh` (407 lines)
   and `check-class-coverage.sh` (447 lines) are the largest unexamined instruments in my scope.
5. **H-5 and H-8 — not reproduced.** Named in my brief as this week's work. I read A-076's
   account of both but ran neither the three-state label diagnostic nor `--all` over zero
   bundles. The register's `FIXED (A-076)` markers for both are **unverified by me.**
6. **Both signed gate packs, `session-state.md`, `HANDOFF.md`, `README.md` — grepped, not
   read through.** My brief calls the claims surface "the largest single source of findings in
   every round" and says it has produced HIGHs inside text John personally signed. I searched
   these for specific claims (snapshot, immutability, the coverage-boundary text) and found
   R1-F4, but I did not read `gate-s1-evidence.md` or `gate-s2-evidence.md` end to end. **On
   the brief's own account of where findings come from, this is where the next reviewer should
   start.**
7. **`docs/gate-s2-evidence.md` §11.0's five accepted limits — read only via grep.** I checked
   my findings against the register §13.4 and against A-076's stated residuals (a)–(e) to
   confirm R1-F1 is not a re-report, but I did not audit §11.0 row by row.

## Honest summary of depth vs breadth

I traded breadth for one Critical. Roughly 60% of my assigned surface by line count was not
probed. Items 1, 2 and 5 above are the ones I would hand to a follow-up reviewer first.
