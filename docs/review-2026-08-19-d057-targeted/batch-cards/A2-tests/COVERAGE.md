# A1 ATTEMPT TWO — COVERAGE, AND WHAT THIS HARNESS CANNOT SEE

`a2-env-and-supervisor.sh` is a **second** harness, added beside the corrected attempt-one
harness `a1-repo-identity.sh`, which it does not modify. Attempt one's harness was green at the
commit an independent verifier then failed — not because it lied, but because it was
**structurally unable** to see two shapes, and it declared both gaps in advance. This file is the
equivalent declaration for attempt two, written before the repair rather than after it.

**Read the blind spots as seriously as the coverage. Every one of them is somewhere a green line
below means "not measured", not "safe".**

---

## 1. WHAT IS COVERED

| group | obligation | what is asserted |
|---|---|---|
| A | `12-F1` | the gate, invoked by absolute path from inside a foreign repository that satisfies the two-path structural test, executes **zero** caller scripts, reads **Sentinel's** tree, and leaves the foreign repository byte-identical. Controls: the same gate from Sentinel's root; a copy outside every repository refusing before any child; the marker mechanism proven live; the refusal scorer probed both ways |
| B1 | `12-F2` | `check-secrets.sh` blocks a credential planted in Sentinel under each of the six caller-provided git environment configurations, in **both** modes |
| B2 | `12-F2` | `install-hooks.sh` leaves a fresh victim's **whole `.git/config`** byte-identical under each configuration, and either refuses or configures Sentinel only |
| B3 | `12-F2` | the pre-commit hook blocks or refuses under each configuration in the **matching** repository, and still refuses before executing a caller-provided script on a mismatch |
| B4 | `12-F2` | a **measured census** of every git invocation made by all 16 entry points, asserting that no caller-provided git variable is still present when a body-level git call runs |
| B5 | `12-F2` | `mutate.sh`'s dirty-tree refusal cannot be defeated from the caller's environment |
| C | `R1` | staged rename, executable-rename, typechange, copy, add, deletion and gitlink records, with the protected controls that forbid a careless widening |

Every REQUIRED line has a paired CONTROL that behaves oppositely, or a liveness control proving
the fixture, the injected variable or the scorer does anything at all. A control failure exits 2
and voids every REQUIRED line beside it.

---

## 2. THE GATE CANNOT COMPLETE IN THIS WORKTREE, SO ITS EXIT STATUS IS NOT A DISCRIMINATOR

`contracts/lib` is unpopulated and `forge` cannot run; `ts/node_modules` does not exist in an
isolated clone; and populating either is a network state change a test author may not make at a
pinned commit. `scripts/test.sh` therefore reaches all thirteen of its stages and then fails at
the Solidity and TypeScript stages **whichever repository it gated**, so both arms of group A
exit 5 — the supervisor's completion-token refusal.

**Consequence, stated plainly: "the ordinary invocation still completes normally" is asserted as
same-stage-sequence, Sentinel's own children executed, and Sentinel's tree read — not as exit 0.**
A completing gate run is not available here and is not in evidence. If a repair changes the
gate's **outcome** rather than its **identity resolution**, this harness will not see it.

The child processes that would otherwise reach the network or cost minutes (`forge`, `anvil`,
`npm`, `gh`, `curl`, and eleven others) are shimmed to a recorder. Reaching one is recorded as an
instrument fact and never scored as a result.

---

## 3. ONE CONFIGURATION IS INERT ON THIS GIT

`GIT_PREFIX` redirects nothing observable on git 2.50.1: not the toplevel, not the file list, not
config. Its REQUIRED lines are still run — the obligation names it — but the harness marks them
**inert** in its own output, because a required line that passes under a variable with no effect
is not coverage. A future git that honours it would make those lines live without any change
here.

The other five were each measured to redirect something before being trusted: `GIT_DIR` (file
list, config), `GIT_WORK_TREE` (toplevel), `GIT_DIR`+`GIT_WORK_TREE` (all three),
`GIT_INDEX_FILE` (file list), `GIT_COMMON_DIR` (config).

---

## 4. THE CENSUS EXEMPTS `rev-parse --show-toplevel`, AND THAT IS A REAL LIMIT

Reading the **caller's** repository is a legitimate identity input — the hook must know where the
commit is happening, and `install-hooks.sh` uses it as a guard. So the census does not score
`rev-parse --show-toplevel` calls that carry caller-provided variables. It prints what they
carried instead, so the exemption cannot hide anything.

**What the exemption forecloses:** an implementation that derived its working root from a
caller-carried `--show-toplevel` answer would not be caught by the census. It would be caught by
groups A, B1, B2 and B3, which assert outcomes rather than call hygiene. The census is a
supplement to those, never a substitute.

**What the census also revealed and does not score:** the entry points' identity probes scrub
`GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE` and `GIT_COMMON_DIR` and do **not** scrub
`GIT_PREFIX`. That is harmless on this git and is recorded rather than asserted.

---

## 5. THE CENSUS ONLY SEES CALLS THAT WERE MADE

An entry point that made no git call under the census fixture is named in the output, and the
census says nothing about it. The census fixture injects the **subject's own** paths precisely so
that every entry point runs normally and makes all of its calls, rather than failing early and
under-reporting — but an entry point whose git usage is conditional on state the fixture does not
create is still under-measured. The 16 entry points are executed once each, from Sentinel's root,
in their cheapest configuration.

---

## 6. SOME REQUIRED LINES PASS TODAY FOR AN INCIDENTAL REASON

In **default** mode, several configurations block the planted credential not because the tracked
enumeration was correct but because the redirected enumeration pushed Sentinel's own files into
`git ls-files --others`, where the untracked sweep added in round six read them from the working
tree. The tracked enumeration still read the wrong repository.

The harness records the clean-report flag on every line and raises a separate OBSERVED line
wherever a clean report was printed over unread Sentinel content, so this is visible — but
**a repair must not be credited for these rows**, and a reviewer reading only PASS/FAIL would
credit it.

---

## 7. NOT EXERCISED, AND NAMED SO THE SILENCE IS NOT READ AS COVERAGE

- **No Solidity, and no gate outcome.** See §2. What `test.sh` and `mutate.sh` do *after* a
  successful identity resolution is not in evidence.
- **`mutate.sh`'s mutation behaviour.** Only its dirty-tree refusal is exercised, with a filter
  that matches nothing.
- **Concurrency.** Nothing here probes two entry points running at once, or a hook racing a
  working-tree change.
- **The twelve check scripts' internal correctness.** Excluded by the A1 card and untouched here.
- **One platform, one git.** git 2.50.1, bash 3.2, `core.quotePath` and `diff.renames` at their
  defaults. Both `R1` and `12-F2` are configuration-sensitive and both were measured at the
  defaults.
- **`git worktree` proper.** The subject is a clone, not a linked worktree. `GIT_COMMON_DIR` is
  exercised as an injected variable, not as a real linked-worktree layout.
- **Non-ASCII paths.** Attempt one's `C4` group covers them and is unchanged; nothing here
  re-derives it.
- **The deferred residuals.** `R2` (`check-vendor-honesty.sh` quoting), `R3` (the inert Case 4
  scorer residual) and `R5` (`check-rename-gate.sh` exiting zero while UNVERIFIED) are DEFERRED
  by D-061(2) and are not probed.

---

## 8. WHAT THIS HARNESS DELIBERATELY DOES NOT ASSERT

It does not assert an implementation. D-061(3) constrains *how* `12-F1` must be repaired — the
root resolved in the supervisor from its real `_gate_src` and passed across the snapshot exec,
with any caller-supplied value cleared, and the read-only snapshot, unlink-before-execution and
completion-token mechanism preserved. **This harness asserts none of that directly**: it asserts
that the gate uses Sentinel's repository, that no caller script executes, and that a copy outside
every repository refuses before any child. Whether the bootstrap's preserved properties survive
the change is a separate obligation on the implementer and its verifier, and this harness does
not carry it.

Likewise it prescribes no scrubbing idiom. It asserts outcomes, plus a census of what actually
reached the children.

---

## 9. THE TWO HARNESSES, AND WHY BOTH ARE RUN

`a1-repo-identity.sh` is unmodified and still exits 0 with zero REQUIRED and zero CONTROL
failures at this branch tip. **That is expected and is not a contradiction**: it is blind to both
confirmed obligations by construction — its runnable set is the twelve check scripts, `test.sh`
is static-only, and its Case 4 fixture places the copy outside every repository rather than
inside a shape-compatible one. Both harnesses must be run, and a repair must leave the first one
green while turning the second one green.
