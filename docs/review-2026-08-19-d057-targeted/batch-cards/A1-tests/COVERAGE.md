# A1 — COVERAGE

**What these tests do NOT reach, and why.** Stated in the §11 "what is NOT in evidence" discipline
the repair protocol requires. A green harness is evidence only for what it actually exercised.

---

## 1. Two of the sixteen entry points are NOT exercised at runtime

`scripts/test.sh` and `scripts/mutate.sh` are asserted **statically only** — tracked,
`#!/usr/bin/env bash`, executable, and resolving a root via `git rev-parse --show-toplevel`
(case 1c). **Their runtime behaviour under cases 1–6 is not in evidence.**

Both drive Foundry, and `contracts/lib` is deliberately unpopulated in the review worktree. Foundry
does not refuse on a missing dependency: `forge build` **self-installs the submodules over the
network**, which I discovered by doing it (PROBES.md D1) and then reverted. Populating a pinned
review worktree, and pulling code from the network into it, is not a change a test author may make.

**Consequence for the card's control**, stated rather than papered over: "case 1 passes unchanged at
base SHA for all 16 entry points" is verified at runtime for **12 of 16**, statically for 4, and
`.githooks/pre-commit` and `scripts/install-hooks.sh` *are* exercised at runtime elsewhere (cases 7,
12c, 13c, 13d) — so the honest count is **14 of 16 exercised in some form, 2 (`test.sh`,
`mutate.sh`) not run at all.**

`scripts/test.sh:176` — the invocation the card singles out — is covered *by proxy*: the harness
invokes `check-secrets.sh` in **default** mode directly, which is what that line does. It does not
prove `test.sh` reaches line 176, nor what `test.sh` does with a non-zero result from it.

**No Solidity is involved in A1**, so the unpopulated Foundry submodules bound nothing else. The
card's boundary is `scripts/*` and `.githooks/*` only.

---

## 2. Case 2 and case 3 are asserted as "same answer", not as "correct answer"

The sweep asserts that all 12 executable entry points produce **byte-identical output and exit
status** from an unrelated directory and from inside a foreign repository as they do from the
repository root. That is exactly the card's invariant and it discriminates today (12 differ, 11
differ).

It has one blind spot the harness itself prints: **an identical answer is not automatically
agreement.** On a clean tree `check-secrets.sh` says `secret guard: clean` about any repository, so
its case-3 comparison matches by coincidence. Case 3a closes that by planting content only the
Sentinel tree holds. **No equivalent planted-content probe was written for the other eleven** —
their case-2/3 verdicts rest on output comparison alone. A repair that made them merely *print the
same thing* from elsewhere without actually reading Sentinel would satisfy this test. I judged the
eleven low-risk because each reads Sentinel-specific files by path, but that is a judgement, not a
measurement.

---

## 3. `check-rename-gate.sh`'s no-remote path is a fail-open shape that is NOT one of the 13 cases

From a directory with no repository, it prints `rename gate: no remote configured — nothing can be
public` and exits 0. That is case 4 territory and is counted there. But the same sentence would be
printed for a **Sentinel checkout that genuinely has no origin configured**, and whether *that*
should be a pass is a D-016 question, not an A1 question. Not tested, deliberately. Raised, not
absorbed.

---

## 4. The default-mode discriminator: established, but the POLICY is not mine

A default-mode discriminator **does exist** (RESULTS.md carries the evidence): `git ls-files -z` for
quoting, `git ls-files -s -z` mode bits to tell a gitlink from a regular file, `git ls-files
--deleted -z` to tell a legitimate worktree deletion from an unreadable one. So the card's "if none
exists that is a DECISION FORK" branch is **not** triggered.

**A narrower fork is still open and is John's**: when default mode enumerates a regular-file path
whose working-tree copy is absent but whose index blob is present, should the guard

- **(a)** read the index blob (`git show ":$f"`, the same mechanism staged mode uses) and scan it,
  which makes default mode scan content the working tree no longer shows; or
- **(b)** treat it as a legitimate deletion and skip it, consistent with case 7's protection, and
  refuse only when neither the working tree nor the index can produce content?

They differ in what the guard is *for*, not in how it is written. I did not choose, and the test for
case 10 asserts only the property both satisfy — **refuse rather than print clean when an
enumerated path could not be read** — so it does not pre-decide the fork.

**A related trap for whoever repairs this, recorded because a naive fix hits it immediately:** two
tracked paths (`contracts/lib/forge-std`, `contracts/lib/openzeppelin-contracts`) are gitlinks,
mode `160000`, and are correctly *not* regular files. A repair that refuses on "enumerated but not
a regular file" refuses on both and breaks case 1.

---

## 5. Not tested at all, and named so the silence is not read as coverage

- **`git worktree` / `GIT_DIR` / `GIT_WORK_TREE` identity confusion.** Case 3 uses a foreign
  repository reached by CWD. Environment-variable and linked-worktree routes to the same identity
  failure are not probed.
- **Concurrent invocation**, and the index moving underneath a run.
- **Symlinked tracked paths.** This index has none (`160000`, `100644`, `100755` only), so
  `[ -f "$f" ]` on a symlink to a missing target is untested.
- **`core.quotePath=false` repositories.** Case 9's defect is `core.quotePath` at its default; a
  repository configured otherwise would not reproduce it. That is a *reason the defect is real*,
  not a reason it is bounded — but the test asserts the defect under the default configuration
  only.
- **Staged renames** with rename detection enabled (`diff.renames`, `-M`). D2 shows a rename
  surfaces as `A` in this invocation and IS scanned; whether that holds under every `diff.renames`
  configuration is **not** established. Recorded as configuration-sensitive, not proven safe.
- **`check-secrets.sh`'s pattern coverage.** Out of scope for A1 entirely. Every fixture here is a
  64-hex value bound to a key-shaped name, chosen because it is known to be caught (control 8/89).
  Nothing here says anything about the guard's declared bare-literal residual.
- **The other twelve entry points' internal correctness.** A1 tests identity and fail-closed
  enumeration. That `check-eval-codes.sh` exits 0 says nothing about whether it counts correctly;
  the card excludes `C1` and `C3` explicitly.

---

## 6. Landing note for the repairer — NOT a blocker, and NOT resolved here

The harness is placed at
`docs/review-2026-08-19-d057-targeted/batch-cards/A1-tests/a1-repo-identity.sh`, which
`check-review-scope.sh`'s `assign()` already covers via its `docs/review-*` → R1 arm.

**Do not move it to `tests/` without adding an `assign()` arm first.** There is no `tests/*` arm, so
a tracked file there is `UNASSIGNED` and turns the partition red — which would make the A1 tests
break the A1 control. **Do not move it to `scripts/` at all**: that would make it a seventeenth
member of the exact set the card enumerates as sixteen by file, shebang and ownership. Either move
is a production change, so both are recorded for John and the repairer rather than made.

---

## 7. Blockers

**None.** All 13 cases were testable at this SHA without a production change. Nothing in the matrix
is recorded as UNTESTABLE.

The one thing I could not do without a state change I am not permitted to make is exercise
`test.sh` and `mutate.sh` at runtime (§1), and that is recorded as a coverage limit rather than a
blocker because the card's symbol boundary — file enumeration in `check-review-scope.sh` and
`check-secrets.sh`, and blob reading in `check-secrets.sh` in both modes — is fully exercised
without them.
