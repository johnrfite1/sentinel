# REVIEWER 2 — DEAD PROBES

Every probe that measured nothing: did not compile, matched no lines, errored before reaching the
code under test, or mutated a value already at its limit. **I had five.** Recorded because in this
project five dead probes in one 48-hour window looked exactly like five passes.

---

## DP-1 — my first baseline run measured nothing, and it exited 1

**What happened.** `npm --prefix ts test` from a fresh worktree failed 4 tests in
`simulate.test.ts` with `missing Foundry artifact .../contracts/out/DemoPay.sol/DemoPay.json`, and
two more were reported as `'test did not finish before its parent and was cancelled'`.

**Why it was dead.** The TypeScript suite requires the Solidity build; `scripts/test.sh` does it
before the TS stage and `npm test` alone does not. The provisioned worktree ships no
`contracts/out/`.

**Why it matters that this is recorded.** The failure mode is asymmetric and dangerous in the other
direction. Here it exited 1, so it was unmissable. **Had I mutated something in `simulate/index.ts`
first and then run the suite, I would have seen these same four failures and could have credited
them to my mutation** — a mutation "caught" by an artifact that was never built. Every mutation
result in `NULL-RESULTS.md` was taken after `forge build` succeeded, against a recorded 513/513
baseline, and each names the *specific* test that failed rather than counting failures.

**Fix:** ran `forge build` in `contracts/` (exit 0, 34 files, Solc 0.8.28) and re-took the
baseline: 513 pass / 0 fail.

---

## DP-2 — the mutation runner ran `node --test` from the wrong directory

**What happened.** `mutate.sh` mutated `ts/src/simulate/anvil.ts` (correctly — the diff against
pristine is in the transcript), then printed `Could not find 'test/simulate.test.ts'` and restored.

**Why it was dead.** The runner `cd`ed to the worktree root; the test glob is relative to `ts/`.

**Why it matters.** `node --test` printed a diagnostic and did **not** exit non-zero in a way my
pipeline distinguished from a pass. A less careful runner would have read "no failures" and
recorded the mutation as SURVIVING — an instrument reporting a defect that does not exist, which is
the mirror image of the class this review is looking for. **The guard that caught it was requiring
each mutation to name the test it killed, not counting failures.** No result in
`NULL-RESULTS.md` comes from a run that did not print a test total.

**Fix:** `cd "$W/ts"` in the runner; re-ran and the mutation was caught with a concrete assertion
diff.

---

## DP-3 — the first ceiling probe could not resolve `viem`

**What happened.** `p2-ceiling-third-route.ts` threw `ERR_MODULE_NOT_FOUND: Cannot find package
'viem'` before executing a line of the code under test.

**Why it was dead.** The probe lives in the evidence directory, outside the worktree, so Node's
resolver never reached `ts/node_modules`. `p1-sim-anchor-straddle.ts` had run fine from the same
place because `simulate/index.ts` imports `viem` **type-only**, and type imports are erased — so
the first probe's success was not evidence the second would work.

**Fix:** symlinked `node_modules` into `probes/`. Not a mutation of the worktree; the worktree's own
symlinks were never touched.

---

## DP-4 — a sed-built probe that did not parse

**What happened.** My first attempt at `p3-callgraph-absence.ts` was produced by a chain of `sed`
substitutions over `p2-ceiling-third-route.ts` and threw
`ERR_INVALID_TYPESCRIPT_SYNTAX: Expected ';', '}' or <eof>`.

**Why it was dead.** It never ran. Loud and self-announcing, so no risk of misreading it — recorded
for completeness and because the *rebuilt* probe (written explicitly rather than patched) is the one
whose output backs `R2-F5`, and the provenance of that file should be visible.

---

## DP-5 — `git status` in the worktree, exactly as the brief warns

**What happened.** I did not run bare `git status`; the brief told me it exits 128 and truncates
`&&` chains. I record it here as a probe I deliberately did **not** run, and note that
`git diff HEAD --stat -- .` reports two "changed" files (`contracts/lib/forge-std`,
`contracts/lib/openzeppelin-contracts`) **at baseline, before I touched anything** — they are the
provisioned symlinks standing in for submodules.

**Why it belongs here.** That output is a standing false positive. A reviewer who took it as the
revert check would either chase a phantom change or, worse, conclude that a *real* change had been
reverted because the diff "looked the same as before". **My revert verification is `cmp` against a
pristine copy of 361 files, not git** — see `ATTESTATION.md`.

---

## Probes that were alive but produced a NULL, not a dead probe

Recorded separately so the two are not conflated: the eight mutations in `NULL-RESULTS.md` each
**moved something** — `mutate.sh` `cmp`s the mutated file against pristine and aborts with
`DEAD PROBE: mutation changed nothing` if the edit did not apply. That guard never fired, and every
one of the eight produced a named failing test. None of them is a dead probe; they are live probes
with a sound result.
