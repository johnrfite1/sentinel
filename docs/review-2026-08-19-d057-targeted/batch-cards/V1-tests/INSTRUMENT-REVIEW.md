HOLD

Independent instrument review of V-1. Reviewer authored none of the guard, the gate wiring,
the binding harness, or the evidence pack. No production file was edited. Unrelated dirty
paths (`README.md`, `assets/`, `.serena/`) were left alone. `docs/gate-s1-evidence.md` and
`docs/gate-s2-evidence.md` were not touched.

Subject: working tree at `3018e8846b082278298429602d85061c42fb3fd4`
(`git rev-parse HEAD` matched before any run). Branch `step-3/isolated-signer`.

This is instrument readiness only. It is not a product repair, a gate sign-off, or a
claim that V-1 is closed as a residual.

## What I ran

1. `git rev-parse HEAD` — `3018e8846b082278298429602d85061c42fb3fd4`.
2. Read the instrument's own bar: `REVIEW-BRIEF.md`, the whole of
   `scripts/check-v1-index-ordering.sh`, the V-1 step and `PROFILE` branches in
   `scripts/test.sh`, `COVERAGE.md`, `EXPLOIT-CONTROL.md`, `GATE-BINDING.md`,
   `v1-gate-binding.sh`, and `logs/` (including `SHA256SUMS`).
3. `./scripts/check-v1-index-ordering.sh` against the candidate. Output was read; the
   exit status was recorded only after that.
4. In a disposable clone that was deleted afterwards: moved the body-level
   `unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_PREFIX` to immediately
   after the `git rev-parse --git-path index` assignment in that clone's working-tree
   `scripts/check-secrets.sh`. Ran **that clone's** `scripts/check-v1-index-ordering.sh`.
   Live tree was not used as the overlay source.
5. Three further disposable clones, also deleted: (B) save `GIT_INDEX_FILE` into a local
   and re-supply it on the resolve line while leaving `unset` **before** resolve; (C) the
   same save, with a subshell `export GIT_INDEX_FILE=...` around the resolve; (D) `env -u
   GIT_INDEX_FILE` on the resolve line, property kept. Each ran the guard from that clone.
6. `shasum -a 256 -c SHA256SUMS` in `logs/`.
7. Assignment-literal sweep of every file this commit adds or modifies, plus a 64-hex
   scan of the same set excluding `SHA256SUMS`. Grep of the logs for the operator repo
   path, `signerKey`, and a 64-`b` fixture.
8. Confirmed live `scripts/check-secrets.sh` carried none of the attack patches after
   the clones were deleted. `git status --short` still showed only the unrelated dirty
   paths named above.

I did not re-run `v1-gate-binding.sh` or `./scripts/test.sh --gate`.

## What I observed

**Live guard (candidate, output not exit status):**

```
  CS-live REQUIRED   PASS  live check-secrets.sh refuses --index-file outside the canonical directory
  CS-mutant CONTROL    PASS  reversed check-secrets.sh accepts and prints secret guard: clean (probe is live)
  HOOK-live REQUIRED   PASS  live pre-commit blocks git commit under hostile GIT_INDEX_FILE; HEAD unmoved; hook names its own validation
  HOOK-mutant CONTROL    PASS  reversed pre-commit no longer emits its own index refusal; check-secrets.sh still refuses; HEAD unmoved

V-1 index-path ordering: ok
```

Process exit 0. REQUIRED CS does not inspect production source order. It runs
`check-secrets.sh --staged --index-file <hostile>` under an exported `GIT_INDEX_FILE` and
matches the process output. The CS CONTROL is live on this tree: the reverse-ordering
copy prints `secret guard: clean`.

**Attack A (required reverse-ordering mutant, overlay from the clone, guard run from the
clone):** after the move, resolve sat at line 120 and `unset` at line 121. Guard output:

```
  CS-live REQUIRED   FAIL  live check-secrets.sh did not refuse at validation (hole open, or unexpected output)
  CS-mutant CONTROL    PASS  live check-secrets.sh is already reversed; hole observed on CS-live
```

Headline `V-1 index-path ordering: FAIL — live files do not hold the enumerated behaviour.`
Exit 1. CS-live failed for the reason it names.

**`scripts/test.sh` wiring:** `PROFILE` is assigned at lines 207–208. The V-1 step is

```
step "V-1 index-path ordering"
./scripts/check-v1-index-ordering.sh || fail=1
```

at 227–228. That is the only invocation (`grep -c` = 1). It is not inside an `if` /
`case` / `while` on `PROFILE`. The first `if [ "$PROFILE" = "gate" ]` is at line 496
(corpus). The second is at line 1255 (coverage prose). Shared prefix holds.

**Logs (hashes matched `SHA256SUMS`):**

| Log | V-1 stage | Secret guard | Top-level | `.rc` |
|---|---|---|---|---|
| G1 | `V-1 index-path ordering: ok`; CS-live PASS; CS-mutant PASS (probe live) | `secret guard: clean` | `GATE PASSED` once, no `GATE FAILED` | `0` |
| G2 | `V-1 index-path ordering: FAIL`; CS-live FAIL | `secret guard: clean` | `GATE FAILED` then `GATE DID NOT REACH COMPLETION` (body exited 1 without a completion token) | `5` |
| G2c | same V-1 FAIL / CS-live FAIL lines as G2 | `secret guard: clean` | `GATE PASSED` once, no `GATE FAILED` | `0` |

No operator-home absolute path remains in the logs. The disclosed substitution `<sentinel-root>`
appears on the rename-gate UNVERIFIED line, not in the V-1 stage. No credential-shaped
fixture string is in any log.

**Coverage statement:** `COVERAGE.md`, the guard header, `EXPLOIT-CONTROL.md`, and
`GATE-BINDING.md` all state that a hook-path commit-accepted outcome was not constructed
and is not a required fail. HOOK-mutant is a CONTROL that the refusal moves from the
hook's wording to `check-secrets.sh`'s `--index-file` refusal, with HEAD unmoved. The
instrument does not claim a commit is accepted under a hook mutant.

**Credential-shaped assignment literals:** none in the files this commit adds
(`scripts/check-v1-index-ordering.sh`, the V1-tests card, the logs) or in `scripts/test.sh`.
The only 64-hex strings in the card are checksums in `logs/SHA256SUMS`, not assignments.
The fixture is assembled at run time (`fake_hex64`).

## Attacks — landed or missed

The instrument's bar: observe guard **behaviour** under a hostile exported
`GIT_INDEX_FILE`. A grep of line order, byte offsets, or scrub-vs-resolution text order
is a FAIL of this instrument.

1. **CS mutant still refuses (dead probe).** Missed. On the candidate, CS-mutant accepts
   and prints `secret guard: clean`. On Attack A, CS-live itself fails because the overlay
   is already reversed.

2. **Independent reverse-ordering mutant does not move CS-live.** Missed. Applied by this
   reviewer, not by trusting the guard's Python in isolation. CS-live FAIL, exit 1.

3. **Failure signal is line order (the named fatal).** Missed. Attacks B and C keep
   `unset` **before** `--git-path index` in the file and still reopen the hole:

   - B: `_v1_saved_gif="${GIT_INDEX_FILE-}"` then the original `unset`, then
     `_cs_canon="$(GIT_INDEX_FILE="${_v1_saved_gif}" git rev-parse --git-path index …)"`.
     Measured: unset line 77, resolve line 122, `unset_before_resolve=True`.
   - C: same save, resolve inside `export GIT_INDEX_FILE=...; git rev-parse --git-path index`.

   Both: CS-live REQUIRED FAIL, same headline as Attack A, exit 1. A source-order grep
   would have passed those files. The guard did not.

4. **`env -u` at the resolve site, property kept (Attack D).** This is not a hole. CS-live
   still PASS. CS-mutant CONTROL FAIL: `reversed check-secrets.sh did not accept — the
   probe did not move`. Guard exit 2, `a CONTROL failed; the instrument is untrustworthy.`
   The line-move mutant is how the CONTROL is *constructed*, not how REQUIRED is scored.
   When that construction stops opening a hole, the instrument refuse-closes rather than
   emitting a false REQUIRED pass. Recorded as a limit, not as a false green.

5. **Credential literal in a tracked file this work adds.** Missed.

6. **V-1 step inside a `PROFILE` branch.** Missed. Shared prefix, one invocation.

7. **G1/G2/G2c logs do not show the claimed gate behaviour.** Missed. Unchanged gate
   passes; mutant fails at V-1 with the default secret-guard step still `clean`; causal
   twin still prints V-1 FAIL and `GATE PASSED`.

8. **Coverage claims a hook commit was accepted.** Missed. The gap is named as not
   constructed.

## Limits of this review

- Fast-profile G1/G2/G2c were not re-executed. Contents were read and hashes checked
  against the committed `SHA256SUMS`. Matching SUMS cannot prove the logs were produced
  by `v1-gate-binding.sh` on this machine; it only proves the files were not altered
  after they were summed. The live guard and the four clone attacks are the
  independently executed part.
- `./scripts/test.sh --gate` was not run. Deep-profile *invocation* is inferred from
  shared-prefix control flow, the same split `GATE-BINDING.md` records and does not
  claim to have measured. A later `--gate` run that lacked the V-1 banner would reopen
  this, as would any edit that wraps the step in a `PROFILE` branch.
- Attack D shows the CONTROL mutant is one transform. A production-preserving resolve-site
  scrub makes that transform stop moving; the gate then goes red at V-1 for an
  untrustworthy probe, not because CS-live saw a hole. REQUIRED scoring on B and C was
  still the hostile-export output.
- CS-live matches the phrase `canonical index directory`. HOOK-live matches the hook's
  own refusal wording plus HEAD unmoved. A refusal that held the behaviour under
  different text would fail those cases. That is output coupling, not a source-order
  check of scrub versus resolve.
- The hook analog of B/C (re-export `HOOK_INDEX` into `--git-path index` while leaving
  `unset` first) was not applied. The CS fail-open is the path that prints
  `secret guard: clean`; that is what B and C targeted.
- `v1-gate-binding.sh`'s G2 predicate does not itself require `secret guard: clean`. The
  committed G2 log does. The causal twin is what shows G2's red is the V-1 step.
- No hook-path commit-accepted outcome was constructed here either. The instrument
  excludes it; this review does not fill it.
- Residual V-1 as a production fact is not accepted by this HOLD. The HOLD is that the
  instrument observes the behaviour it enumerates.
