# R5 — rename-gate design, for John's ruling. Not built.

`scripts/check-rename-gate.sh` is D-016's mechanical publication block. When it cannot read visibility it prints `UNVERIFIED` and **exits 0**. `scripts/test.sh` aggregates with `|| fail=1`, so UNVERIFIED is indistinguishable from verified-private.

## Remeasured, this machine

From the live worktree, `gh` is present and authenticated:

```
rename gate: clean (johnrfite1/sentinel is private; D-016 publication block intact)
```

exit 0.

From the C6d freeze clone — origin was a local path, `gh` could not read visibility — the same script printed `UNVERIFIED` and the suite continued. That is the hole. The Phase 2 isolated deep gate disclosed this (`Rename-gate exit status: not evidence (R5)`) and still printed `GATE PASSED`. Nothing was concealed. The defect is in the guard.

## Why "fail UNVERIFIED everywhere" is not free

Making UNVERIFIED a hard failure in every profile blocks:

- clones with no `gh`
- clones with `gh` and no auth
- clones whose origin is not a GitHub slug (local `--local` clones used by this project's own cards)
- offline / air-gapped gate runs

Those are legitimate. The isolated clones this project verifies in are one of them.

## Options

**A. Fail closed in the deep / `--gate` profile only.**
Fast `./scripts/test.sh` may still print UNVERIFIED and exit 0. `./scripts/test.sh --gate` treats UNVERIFIED as failure.
- Cost: two profiles mean two meanings. A contributor who only runs fast never learns the gate will refuse. The deep gate becomes unrunnable offline unless they also get A-or-C's acknowledgement.
- Benefit: the profile that is evidence for D-055 condition 2 can no longer pass while seeing nothing.

**B. Explicit acknowledgement to proceed when UNVERIFIED.**
A named env var or flag, for example `SENTINEL_RENAME_GATE_UNVERIFIED_OK=1`, required whenever the script would otherwise print UNVERIFIED. Absent: fail. Present: print UNVERIFIED and continue, and print that acknowledgement was given.
- Cost: every offline clone, including card harnesses, must set the var. Forgetting it looks like a product failure. The var can be exported in a wrapper and forgotten.
- Benefit: one meaning in both profiles. UNVERIFIED is never silent.

**C. Hybrid: deep fails closed unless acknowledged; fast stays UNVERIFIED exit 0.**
- Cost: three states to document. Easy to describe wrong.
- Benefit: daily fast runs stay possible; the evidence profile cannot pass on nothing without someone saying so.

**D. Fail closed everywhere, no acknowledgement.**
- Cost: blocks every offline / unauthenticated / non-GitHub-origin gate run, including this project's isolated clones. The reversal condition in the ruling is aimed at this shape.
- Benefit: simplest mechanical rule.

**E. Procedural rule only** (pack already discloses "exit status: not evidence").
John rejected this: substituting a procedural guard for a mechanical one is a failure shape this project has already paid for.

## Reversal

If no shape of the repair can avoid blocking legitimate offline gate runs, R5 returns as a documented limit with the procedural rule attached.

## Recommendation, not a ruling

C, if the acknowledgement string is a single env var named in the UNVERIFIED line so a log reader can see it was given. A if John wants zero new interface. D is the option the ruling already said would block the clones. Not built.
