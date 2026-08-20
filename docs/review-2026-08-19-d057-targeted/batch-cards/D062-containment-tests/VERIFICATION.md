# D-062 CONTAINMENT — INDEPENDENT VERIFICATION

# VERDICT: **HOLD**

**The repair stands.** Every REQUIRED case in `CARD.md` holds at the frozen SHA and seven of the
twelve discriminate against the pre-repair baseline. The two layouts `IMPLEMENTATION.md` conceded
were unmeasured were measured here and both work — and both fail OPEN at the baseline, so those
probes moved something. No probe in this verification produced a fail-open at the frozen SHA.

**Authority for this document:** D-062(4) — one implementation and one independent verification.
The verifier authored neither the tests nor the repair.

**Under-verification SHA:** `492021325255f56ed8d3df8265bbaa43ef0f7efa`
**Discriminating baseline:** `28fa955900c102b680084c138e45c8b49cd12a79` (pre-repair)
**Test-contract SHA:** `c73b17aa6df56fa9dd01685f6ae919b43a71351b`

**Measured on:** `git version 2.50.1 (Apple Git-155)`, `GNU bash, version 3.2.57(1)-release
(arm64-apple-darwin25)`, `darwin` 25.5.0. Every scored run used a private clone under a scratch
directory with `HOME`, `XDG_CONFIG_HOME`, `GIT_CONFIG_GLOBAL` redirected and `GIT_CONFIG_NOSYSTEM=1`
set. No repository the verifier did not create was written to.

**Harness sha256, measured before and after every run in this verification — all three unchanged:**

| harness | sha256 (measured) |
|---|---|
| `A1-tests/a1-repo-identity.sh` | `54535b3b139ef9098753393872e39c932e25e0d861cfa14eb04e6f18c591122d` |
| `A2-tests/a2-env-and-supervisor.sh` | `dd67d69a13faf43e0578c57f9681e1468ca0b721727e7f14e83c1e5859fc84a7` |
| `D062-containment-tests/d062-containment.sh` | `c830d195281c0a2bae2fd62e79ce1d1402f03182bb2fbc446361c91fd89a1756` |

All three are byte-identical at `28fa955`, `c73b17a` and the frozen SHA (`git cat-file` on each
blob at each commit). **No existing harness and no existing evidence file changed.**

---

## 0. METHOD, AND WHICH NUMBERS ARE WHOSE

**The verifier's own probes were written first and run first.** They share no code with
`d062-containment.sh`; they were written from `CARD.md`'s behavioural matrix, not from the
harness. The three frozen harnesses were run **afterwards**, and every result below is labelled
`[V]` for verifier-built or `[H]` for frozen-harness. Where the two agree that is stated as
agreement, not as one measurement.

The verifier's fixture is a single hex character repeated 64 times, assembled at run time and
bound to a key-shaped identifier, so no credential-shaped literal exists in this file or in any
committed fixture. The clean counterpart is ordinary prose.

**Every verdict below was read from the tools' OUTPUT.** Exit status was recorded but never used
as the pass condition: BLOCK requires the guard to print `BLOCKED` and to name the fixture path
and requires the credential to be absent from HEAD; ALLOW requires `secret guard: clean` and
requires the intended content to have reached HEAD; REFUSE requires a non-zero exit **and** the
absence of the `secret guard: clean` line.

---

## 1. THE BOUNDARY CLAIM — VERIFIED INDEPENDENTLY

`git diff 28fa955..492021 --numstat` names eleven files. Exactly two are production:

| file | mode | classification | ±lines |
|---|---|---|---|
| `.githooks/pre-commit` | `100755` | **production** | +83 / −0 |
| `scripts/check-secrets.sh` | `100755` | **production** | +84 / −4 |
| `HANDOFF.md` | `100644` | documentation | +13 |
| `docs/decisions.md` | `100644` | decision record | +4 |
| `docs/session-state.md` | `100644` | documentation | +118 / −195 |
| `docs/…/NEW-FINDINGS.tsv` | `100644` | ledger | +20 / −8 |
| `docs/…/D062-containment-tests/CARD.md` | `100644` | test contract (new) | +105 |
| `docs/…/D062-containment-tests/COVERAGE.md` | `100644` | test contract (new) | +168 |
| `docs/…/D062-containment-tests/RESULTS.md` | `100644` | test evidence (new) | +376 |
| `docs/…/D062-containment-tests/d062-containment.sh` | `100755` | test harness (new) | +603 |
| `docs/…/D062-containment-tests/IMPLEMENTATION.md` | `100644` | implementer's claim (new) | +116 |

**No third production file.** The five new batch-card files entered at `c73b17a`, the test-contract
commit, not at the implementation commit. `git diff c73b17a..492021 --numstat` is exactly four
files: the two production files, `+1` line in `docs/decisions.md` (the D-064 entry), and the new
`IMPLEMENTATION.md`. The implementation commit touched no harness.

The two production files are byte-identical at `28fa955`, `76c466f` and `c73b17a`
(`8a99a47a…6288` and `3dd94dab…5c49`) and differ only at the frozen SHA
(`07563bdf…f704` and `acba49bb…f8a5`). `CARD.md`'s statement that the harness may be run at
either base is therefore true as written.

---

## 2. PER-ITEM RESULTS — ASSIGNMENTS 1 THROUGH 7

| # | assignment | result | discriminated? |
|---|---|---|---|
| 1 | all twelve containment cases, reproduced independently | **HOLD** — 12/12 as required at the frozen SHA; 21 verifier controls all live | 7 of 12 move against the baseline; 5 do not — enumerated in §3 |
| 2 | `GIT_DIR` / `GIT_WORK_TREE` combinations with a valid temporary index | **HOLD** — 13 combinations, no fail-open; every foreign-pointing combination refuses or measures its own repository | yes — the baseline admits the credential in the same combinations |
| 3 | no victim configuration or worktree mutation | **HOLD** — victim byte-identical after every refusal case in three separate probe suites | yes — the fingerprint moves under a deliberate config write and under a deliberate worktree write |
| 4 | D-064's three confirmations | **CONFIRMED** — exactly two A2 assertions moved (`B3-index`, `B4`), no third; standalone `check-secrets.sh` carries **0**; all twelve containment cases hold | yes — full normalized diff of two A2 runs, §6 |
| 5 | the `12-F2` anti-regression, both modes | **HOLD** — a caller-supplied `GIT_INDEX_FILE` redirects nothing on `--staged` or default; the decoy is proven potent | yes — the same decoy honoured through the internal argument yields `clean` |
| 6 | the two layouts `IMPLEMENTATION.md` concedes are unmeasured | **MEASURED — both work.** Linked worktree BLOCKED, separate-`gitdir` BLOCKED; clean commits still allowed in both | yes — **both fail OPEN at the baseline** (credential in HEAD, `secret guard: clean`) |
| 7 | direct attacks on the validation rule | **HOLD** — the 45 probes tabulated in §9; every one either scanned the file it was pointed at or refused. **Nothing failed open.** | yes — the same attack surface does not exist at the baseline, where every value is discarded |

---

## 3. ASSIGNMENT 1 — THE TWELVE CASES, INDEPENDENTLY

Verifier probes (`[V]`) were built as: a private clone of each SHA, `core.hooksPath=.githooks`, a
tracked fixture file seeded clean with `--no-verify` and hooks disabled, then the case command.
`git commit -a` and `git commit -- <path>` only act on **tracked** files, so a probe that plants an
untracked file measures nothing — the first draft of this suite did exactly that and was discarded
before it could be scored.

**Ground-truth control, measured before any case (`[V]`, equivalent to `1-tmp` / `2-tmp`):** a probe
hook recorded what git hands the hook for each form.

| commit form | `GIT_INDEX_FILE` git supplies | temp-index fixture blob | canonical-index fixture blob |
|---|---|---|---|
| `git commit -am` | `<root>/.git/index.lock` (absolute, regular, not a symlink) | `3dd2086…` (the credential) | `0a8ef54…` (clean) |
| `git commit -m … -- <path>` | `<root>/.git/next-index-<pid>.lock` | `3dd2086…` (the credential) | `0a8ef54…` (clean) |
| `git add` + `git commit` | `.git/index` (**relative**) | `3dd2086…` | `3dd2086…` |

The two hand-offs differ from the canonical index, so cases 1 and 2 measure something. The plain
`git commit` hand-off is a **relative** path — a detail the repair must handle and does.

### Results

| case | command (`[V]`) | frozen SHA — observed | baseline — observed | moves? |
|---|---|---|---|---|
| 1 | `git commit -am` with the credential | `BLOCKED <fixture>`, exit 1, HEAD unchanged, credential not in HEAD | `secret guard: clean`, exit 0, **HEAD moved, credential IN HEAD** | **YES** |
| 2 | `git commit -m … -- <path>` | `BLOCKED <fixture>`, exit 1, HEAD unchanged | `secret guard: clean`, exit 0, **credential IN HEAD** | **YES** |
| 3 | `git add` + `git commit` | `BLOCKED <fixture>`, exit 1 | `BLOCKED <fixture>`, exit 1 | no (positive control by design) |
| 4 | clean `git commit -am` | `secret guard: clean`, exit 0, content in HEAD | same | no |
| 5 | clean path-limited commit | `secret guard: clean`, exit 0, content in HEAD | same | no |
| 6a | pre-staged `git rm` then commit | `secret guard: clean`, exit 0, deletion committed | same | no |
| 6b | `rm` then `git commit -am` | `secret guard: clean`, exit 0, deletion committed | same | no |
| 6c *(control)* | deletion **plus** a credential in a second file | `BLOCKED zz-second…`, exit 1 | `secret guard: clean`, exit 0, **credential IN HEAD** | **YES** |
| 7 | `check-secrets.sh --staged` with a malicious caller `GIT_INDEX_FILE` at a clean decoy | `BLOCKED <fixture>` — canonical index scanned | `BLOCKED <fixture>` | no (anti-regression) |
| 8 | hook handed a foreign repository's index | exit 2, `reason: outside this worktree's index directory (…)`, **no clean line** | exit 0, `secret guard: clean` | **YES** |
| 9a | hook handed a symlinked temporary index | exit 2, `reason: is a symlink` | exit 0, `secret guard: clean` | **YES** |
| 9b | hook handed a nonexistent temporary index | exit 2, `reason: is not an existing regular file at scan time` | exit 0, `secret guard: clean` | **YES** |
| 10 | hook handed a valid `.git/index.lock` carrying the credential | `BLOCKED <fixture>`, exit 1 | exit 0, `secret guard: clean` | **YES** |
| 11 | hook handed a valid `.git/next-index-<pid>.lock` carrying the credential | `BLOCKED <fixture>`, exit 1 | exit 0, `secret guard: clean` | **YES** |
| 12 | victim repository across every refusal case | fingerprint byte-identical | byte-identical | no (see §5) |

**Verifier controls, all live at both SHAs:** `1-tmp`, `2-tmp` (above); `6c`; `7-nov` (the fixture
blocks on `--staged` with no variable set); `7-def` (default mode with the same variable also
blocks); `8-L1` (the emulated hook invocation exits 0 and prints `secret guard: clean` with nothing
staged); `8-L2` (the same emulation blocks a credential staged in the canonical index — it is not
inert); `8-read` (the victim index is readable from the subject: 501 entries enumerated, so a
refusal at case 8 cannot be an unreadable-object artifact); `9-sym` and `9-abs` (the planted symlink
really is a symlink and the missing file really is missing at scan time); `10-tmp` and `11-tmp` (the
planted temporary index is a regular non-symlink file, carries the credential, and the canonical
index stages nothing versus HEAD); `12-live` in two flavours.

### Which REQUIRED cases do NOT discriminate, stated plainly

**Cases 3, 4, 5, 6a, 6b, 7 and 12 pass at BOTH SHAs.** They are anti-regression, not evidence of
repair, and this verification does not count them as such. `COVERAGE.md` §3 says the same thing
about 4, 5 and 6b and is correct; the verifier adds 3, 7 and 12 to that list, since 3 is the
declared positive control, 7 is the `12-F2` anti-regression that already held, and 12 held at the
baseline because the baseline discarded the value rather than because it validated it.

**Seven REQUIRED cases move: 1, 2, 8, 9a, 9b, 10, 11.** That is the same seven the frozen harness
reports failing at `28fa955`, arrived at independently.

**Frozen-harness agreement `[H]`:** `d062-containment.sh` against a clone at the frozen SHA —
**0 REQUIRED failures, 0 CONTROL failures**, and **run twice with identical verdicts on all 30
scored cases**; against a clone at `28fa955` — **7 REQUIRED failures, 0 CONTROL failures**, the
failing seven being 1, 2, 8, 9a, 9b, 10, 11. The harness's own controls `Z-frozen` and `Z-cfg`
passed on every run.

---

## 4. ASSIGNMENT 2 — `GIT_DIR` / `GIT_WORK_TREE`, ALONE AND TOGETHER

Not covered by the containment harness. Thirteen configurations, each run twice: once as a **real
`git commit -am`** with the credential planted (so a legitimate temporary index exists), and once
as an **emulated hook invocation with a valid credential-bearing `.git/index.lock` present**.

| environment | real `git commit -am` | emulated hook + valid temp index |
|---|---|---|
| none | `BLOCKED`, nothing in HEAD | `BLOCKED` |
| `GIT_DIR` → victim | exit 2, `outside this worktree's index directory` | `BLOCKED` (own repository measured) |
| `GIT_WORK_TREE` → victim | exit 2, `outside this worktree's index directory` | exit 2, **repository identity mismatch** |
| `GIT_DIR` + `GIT_WORK_TREE` → victim | git operated wholly in the victim; hook reported `clean` for the victim, which had nothing staged; **nothing committed, victim byte-identical** | exit 2, **repository identity mismatch** |
| `GIT_DIR` → self | `BLOCKED`, nothing in HEAD | `BLOCKED` |
| `GIT_DIR` + `GIT_WORK_TREE` → self | `BLOCKED`, nothing in HEAD | `BLOCKED` |

Plus: **a foreign repository configured to use the subject's hook** (`core.hooksPath` pointing at
the subject's `.githooks`), committing a credential — exit 1, `repository identity mismatch;
refusing before running anything`, nothing in the foreign HEAD, foreign repository byte-identical.
That is D-060(2) still holding with the D-062 block bolted on ahead of it.

**No configuration produced a clean report over content that then reached HEAD.** The one `clean`
line in the table is the both-variables-to-the-victim case, where git itself was pointed entirely
at the victim, nothing was staged there and nothing was committed — the guard measured the
repository that was about to be committed, which is the invariant, not a violation of it.

### The load-bearing question this assignment raises, answered separately

Once a caller-supplied value **passes** validation — a regular non-symlink file named `index`,
`index.lock` or `next-index-<digits>.lock` in the repository's own canonical index directory — the
hook honours it. Is that a hole? Measured directly, with a real `git commit` and a caller-planted
`.git/index.lock`:

| which index holds the credential | frozen SHA | baseline |
|---|---|---|
| the **decoy** git will actually commit from | `BLOCKED`, HEAD unchanged, **credential not in HEAD** | `secret guard: clean`, **HEAD moved, credential IN HEAD** |
| the canonical index, while git commits from a clean decoy | `secret guard: clean` — and **nothing was committed**, so the report is accurate | `BLOCKED` — a right answer for the wrong reason: it blocked a commit that was not carrying the credential |

**Git commits from `GIT_INDEX_FILE`.** So honouring a validated in-directory value is not
deference — it is the only way to read the index that is about to become the commit. The direction
that matters cannot fail open, and it is exactly the direction the baseline fails.

---

## 5. ASSIGNMENT 3 — NO VICTIM MUTATION, AND THE COMPARISON IS LIVE

The fingerprint is a sha256 over the victim's **whole `.git/config` byte-for-byte**, its `HEAD`,
the sha256 of its `.git/index`, the sha256 of **every regular file in the worktree** in sorted
order, and the target of every symlink.

| probe suite | refusal cases covered | victim byte-identical after each |
|---|---|---|
| containment cases 8-11 | foreign index, symlinked temp index, nonexistent temp index | yes |
| `GIT_DIR`/`GIT_WORK_TREE` suite | all 13 configurations | yes |
| dedicated refusal suite | foreign canonical index; foreign via traversal; directory symlink to the victim; symlink into the victim; malformed name; nonexistent directory | yes (6 of 6) |

**The comparison is not inert.** Two deliberate changes were made to the same victim and the
fingerprint moved for both: `git config d062.probe yes` (config half) and appending one line to a
tracked worktree file (worktree half). Had only one been proven, the untested half of the
fingerprint would have been decoration.

---

## 6. ASSIGNMENT 4 — D-064'S THREE CONFIRMATIONS

### (a) The collision is exactly two REQUIRED assertions, and nothing else in A2 moved

`a2-env-and-supervisor.sh` was run against a clone at `28fa955` and against a clone at the frozen
SHA. Both runs scored **81 case ids**, the **same 81** — none added, none removed. Verdicts were
compared mechanically, then the two whole outputs were normalized (ANSI stripped, scratch paths,
40-hex object ids and `next-index-<pid>` masked) and diffed in full.

**Assertions whose verdict moved: 2.**

| case | kind | baseline | frozen SHA |
|---|---|---|---|
| `B3-index` | REQUIRED | PASS (exit 1, blocked=1) | **FAIL** (exit 2, blocked=0, refusal=0, clean-report=0) |
| `B4` | REQUIRED | PASS (0 entry points carry) | **FAIL** (1 entry point carries: `.githooks/pre-commit`) |

**Everything else in the full-text diff is an incidental count, not an assertion:**

- `P5` records the subject has 499 tracked files rather than 494 — the five new batch-card files.
- `check-review-scope.sh` makes 200 git calls rather than 195 — five more tracked files.
- `B4n` (OBSERVED, asserts nothing) records 275 git invocations rather than 268.
- The `.githooks/pre-commit` census row: 7 calls / 0 body-level carriers → 9 calls / 4 body-level
  carriers. That row is `B4`'s cause, already counted.
- The tally lines and exit status.

**No third assertion moved. D-064's reversal condition did not fire.** Two independent A2 runs at
the frozen SHA produced identical verdicts on all 81 cases, both with **0 CONTROL failures**, so
the instrument is sound in both.

On `B3-index`: the observed refusal is exit 2, `blocked=0 refusal=0 clean-report=0`. The verifier
reproduced the underlying behaviour directly — the hook prints
`the index git handed this hook is not acceptable; refusing`, exits 2, and prints no clean line —
which is what containment case 8 REQUIRES and what D-062(7) requires. A2's `is_ident_refusal`
matcher does not recognise it because the refusal is about the **index**, not identity.
`refusal=0` is the matcher not matching, not a missing refusal. **The verifier agrees with D-064
that rewording the refusal to satisfy the matcher would be the wrong repair**, and notes that the
refusal was not reworded: A2 is left failing, as D-064 requires every citation to say.

### (b) Standalone `check-secrets.sh` carries ZERO

Measured independently with a `PATH`-injected `git` wrapper that logs the five git variables
present on every invocation before exec'ing the real git. All five variables were exported by the
caller, pointing at a victim repository.

| invocation | git calls | calls carrying a caller variable |
|---|---|---|
| `check-secrets.sh` (default mode), 5 caller variables set | 3 | 1 — `GIT_PREFIX` on the **pre-scrub identity probe** only |
| `check-secrets.sh --staged`, 5 caller variables set | 3 | 1 — same identity probe |
| `check-secrets.sh` either mode, clean environment | 3 | 0 |
| `.githooks/pre-commit` with a valid temporary index | 9 | 5 — 1 pre-scrub identity probe + **4 index reads carrying the hook's own validated path** |
| `.githooks/pre-commit` with no `GIT_INDEX_FILE` | 5 | 0 |

**Body-level carriers for standalone `check-secrets.sh`: zero, in both modes.** The single carrier
is `GIT_PREFIX` surviving into the `env -u …` identity probe, whose `-u` list omits `GIT_PREFIX` —
**and that is byte-for-byte identical at the baseline** (measured, same table), so it is
pre-existing, outside D-062's boundary, and already recorded as A2 residual `R-E`.

A2's own census agrees and reports `scripts/check-secrets.sh  git calls=3  body-level carriers=0
identity-probe carriers=1` at **both** SHAs, and names exactly one carrying entry point at the
frozen SHA: `.githooks/pre-commit`, with 4 body-level carriers. The verifier's independent count is
also 4. The four are the index census, the staged raw enumeration, and the staged blob read issued
twice — once by the credential scan and once by the machine-path scan, both through `_sec_content`.

### (c) All twelve containment cases hold

§3 above, both independently and by the frozen harness.

---

## 7. ASSIGNMENT 5 — THE `12-F2` ANTI-REGRESSION, WITH A POTENCY PROOF

A caller-supplied `GIT_INDEX_FILE` pointing at a clean decoy index, with the credential staged in
the canonical index:

| invocation | frozen SHA | baseline |
|---|---|---|
| `check-secrets.sh --staged` with the variable exported | `BLOCKED <fixture>` — canonical index scanned | `BLOCKED` |
| `check-secrets.sh` (default) with the variable exported | `BLOCKED <fixture>` | `BLOCKED` |
| `check-secrets.sh --staged`, no variable (liveness) | `BLOCKED` | `BLOCKED` |

**The decoy is potent, proven rather than assumed.** The same clean decoy, placed in the canonical
index directory and offered through the internal `--index-file` argument, produces
`secret guard: clean`, exit 0. So "honouring the decoy" is an observably different outcome from
"ignoring it", and the pass above is a real discrimination rather than an unreadable-object
artifact. Without this the case-7 row would have measured nothing.

`GIT_INDEX_FILE` is `unset` in both files before any body-level git call, and the internal
`--index-file` argument is refused outright unless `--staged` is also present. Attempt one's
failure mode — honouring the caller's environment — is not reopened.

---

## 8. ASSIGNMENT 6 — THE TWO LAYOUTS `IMPLEMENTATION.md` LEFT UNMEASURED

`IMPLEMENTATION.md` states `git rev-parse --git-path index` is *believed* correct for a linked
worktree and a separate-`gitdir` checkout and that neither was exercised. **Both are measured
here.**

### Linked worktree (`git worktree add`)

| fact | measured |
|---|---|
| `.git` in the linked worktree | a **FILE** containing `gitdir: <main>/.git/worktrees/lw` |
| `git rev-parse --git-path index` | `<main>/.git/worktrees/lw/index` — **absolute**, not `<root>/.git/index` |
| what git hands the hook for `commit -a` | `<main>/.git/worktrees/lw/index.lock` |
| hook CWD | the linked worktree root |
| `core.hooksPath` | `.githooks`, resolved inside the linked worktree |

**Frozen SHA:** `git commit -am` with the credential → `BLOCKED <fixture>`, exit 1, HEAD unchanged,
credential not in HEAD. A clean `commit -am` → `secret guard: clean`, exit 0, commit lands.
`git add` + `git commit` → `BLOCKED`.
**Baseline:** `secret guard: clean`, exit 0, **HEAD moved, credential IN HEAD — it fails OPEN.**

### Separate-`gitdir` checkout (`.git` as a file)

| fact | measured |
|---|---|
| `.git` | a **FILE** containing `gitdir: <realgit>` |
| `git rev-parse --git-path index` | `<realgit>/index` — absolute |
| what git hands the hook for `commit -a` | `<realgit>/index.lock` |

**Frozen SHA:** credential → `BLOCKED`, exit 1, nothing in HEAD; clean → `secret guard: clean`,
commit lands. **Baseline:** `secret guard: clean`, **credential IN HEAD — it fails OPEN.**

**Neither layout fails open at the frozen SHA and neither fails closed.** The `--git-path` decision
is not merely defensible, it is what makes both layouts work: hardcoding `<root>/.git/index` would
have made `CANON_DIR` wrong in both, and every temporary index would have been refused — a false
refusal on every commit in a linked worktree.

Also measured, and also correct at the frozen SHA: **`git commit -am` issued from a subdirectory**
(git runs the hook at the worktree top and supplies an absolute index path) → `BLOCKED`.

### Additional commit forms, none named in the card

| form | index git supplies | clean content | credential |
|---|---|---|---|
| `git commit --amend -a --no-edit` | `.git/index.lock` | `clean`, exit 0 | `BLOCKED`, exit 1 |
| `git commit --only <path> -m` | `.git/next-index-<pid>.lock` | `clean`, exit 0 | `BLOCKED`, exit 1 |
| `git commit --include <path> -m` | `.git/index.lock` | `clean`, exit 0 | `BLOCKED`, exit 1 |

No third temporary-index spelling appeared on this git. `git revert` and `git cherry-pick` do not
run `pre-commit` on this git and are therefore not covered by this guard at all — an observation,
not a D-062 finding.

---

## 9. ASSIGNMENT 7 — ATTACKS ON THE VALIDATION RULE

45 probes, tabulated below: **33** path-validation attacks, **6** degenerate temporary indexes and
**6** invocations of the internal argument. Each planted the credential in the candidate it points
at, unless its row says otherwise, so a `clean` report would be a **fail open**. Outcome
vocabulary: **BLOCKED** = the guard scanned what it was pointed at and found the credential;
**REFUSED** = non-zero, no clean line; **CLEAN** = a clean report.

### Nothing failed open

| attack | outcome | note |
|---|---|---|
| traversal INTO the canonical directory (`.git/refs/../../.git/index.lock`) | BLOCKED | resolves to the real file; scanned |
| relative `.git/index.lock` | BLOCKED | |
| relative `./.git/../.git/index.lock` | BLOCKED | |
| double slash `.git//index.lock` | BLOCKED | |
| trailing slash `.git/index.lock/` | BLOCKED | |
| traversal OUT to a foreign index (two spellings, both via existing directories) | REFUSED | `outside this worktree's index directory` |
| symlink to a real credential-bearing index | REFUSED | `is a symlink` — `-L` tested before `-f` |
| dangling symlink | REFUSED | `is a symlink` |
| directory symlink OUT (`.git/dlink/index.lock` → foreign `.git`) | REFUSED | `pwd -P` collapses it before comparison |
| chained directory symlink OUT (two hops) | REFUSED | same |
| directory symlink IN (outside path resolving to the canonical directory) | BLOCKED | correct: it is the real file |
| **hardlink** to a foreign credential-bearing index | BLOCKED | accepted, then **scanned**; see residual `V-2` |
| `next-index-007.lock`, `next-index-0.lock`, `next-index-<20 digits>.lock` | BLOCKED | form accepted, content scanned |
| `next-index-.lock`, `-1a`, `-+1`, `-1.2`, `- 1`, `-1 `, Arabic-Indic digits, `next-index-5.lock.lock` | REFUSED | `malformed next-index temporary name` (8 spellings) |
| basename case variant `INDEX.LOCK` on a case-insensitive filesystem | REFUSED | `unexpected basename` — refused on the name before the file test |
| correct basename in the **wrong** subdirectory (`.git/hooks/index.lock`) | REFUSED | `outside this worktree's index directory` |
| directory where a file is expected | REFUSED | `is not an existing regular file at scan time` |
| FIFO where a file is expected | REFUSED | same |
| nonexistent directory component | REFUSED | `does not resolve to an existing directory` |
| a single space | REFUSED | `outside this worktree's index directory` |
| empty `GIT_INDEX_FILE` | CLEAN | no candidate; the canonical index was clean by construction — **correct**, and the paired probe below proves it is not vacuous |
| `GIT_INDEX_FILE` = the canonical index **with the credential staged in it** (absolute and relative) | BLOCKED | the empty-value row above is therefore not hiding a dead path |

### Degenerate temporary indexes all fail CLOSED

| candidate | outcome |
|---|---|
| a valid index with **zero entries** | `Refusing to report a clean scan measured against nothing`, exit 1 |
| a truncated (corrupt) index | `git ls-files -s failed; refusing to report a clean scan`, exit 1 |
| a zero-length file | same, exit 1 |
| a regular file that is not an index at all | same, exit 1 |
| an accepted index naming an object this repository does not have | `could not read <path> — refusing to report it clean`, exit 1 |
| a valid index staging nothing versus HEAD | `secret guard: clean`, exit 0 — correct |

### The `--index-file` argument interface, attacked directly

| invocation | outcome |
|---|---|
| `--staged --index-file <canonical-dir temp index>` | scanned → `BLOCKED` |
| `--index-file <path>` without `--staged` | refused: `only meaningful with --staged` |
| `--staged --index-file <path outside the canonical directory>` | refused: `outside the canonical index directory` |
| `--staged --index-file` with no value | refused: `--index-file requires a path` |
| `--index-file --staged` (the flag consumed as the value) | refused: `only meaningful with --staged` |
| `--staged --index-file <path> --staged` | scanned → `BLOCKED` |

### One structural fact that makes the whole rule work, recorded because it is fragile

**`git rev-parse --git-path index` honours `GIT_INDEX_FILE`.** Measured: with the variable set to
`/tmp/elsewhere.idx`, `--git-path index` returns `/tmp/elsewhere.idx` rather than `.git/index`.

Both files clear `GIT_INDEX_FILE` **before** they ask git for the canonical path — the hook at line
39, the resolution at line 86; the guard at line 76, the resolution at line 121. Had either order
been reversed, the candidate would have defined the canonical directory it is compared against and
the containing-directory test would have been vacuous while still passing every case in the card.

The order is correct as built, and it is proven by measurement rather than by reading: in every
out-of-directory refusal the diagnostic names the **subject's** `.git` as the canonical directory
while the candidate was elsewhere. A reordering would make that message name the candidate's
directory instead. Recorded as residual `V-1` so a future edit does not silently undo it.

---

## 10. RESIDUALS — SEPARATE FROM FAILURES

**None of these is a failure of the D-062 contract.** They are recorded so silence is not read as
coverage.

**`V-1` — the unset-before-resolve ordering is load-bearing and nothing guards it.**
`git rev-parse --git-path index` honours `GIT_INDEX_FILE` (measured, §9). The directory comparison
is only meaningful because both files clear the variable first. No test in any harness would fail
if that ordering were reversed: every card case would still pass, because in every card case the
candidate either is in the canonical directory or is refused for another reason first. A future
edit that hoists the resolution — or that adds a third caller which resolves before scrubbing —
reopens the hole silently.

**`V-2` — a hardlink into the canonical index directory is accepted.** `-L` is false for a
hardlink, so a hardlink to a foreign index passes validation. It fails **safe** here — the guard
scanned the linked bytes and blocked the credential they carried — and creating it requires write
access to `.git`, which is the same-user boundary the implementation explicitly disclaims. Not
probed further.

**`V-3` — the validate/scan window exists twice and was not probed.** The hook validates then
`exec`s; the guard re-validates then reads. A same-user process can replace the file in either
window. This is the bound `IMPLEMENTATION.md` states in both files' comments; the verifier did not
manufacture a timing probe for it and draws no conclusion either way.

**`V-4` — `--index-file` is now a reachable interface on `check-secrets.sh`.** Re-validation
confines it to the repository's own canonical index directory, and it is refused without
`--staged`, but a caller who can write into `.git` can now direct the guard at an index of their
own authorship. Outside the hook that changes only what the guard **reports**, never what git
commits. Same-user boundary again.

**`V-5` — `GIT_PREFIX` still reaches `check-secrets.sh`'s identity probe.** One carrier, on the
`env -u …` probe whose `-u` list omits it. **Identical at the baseline** (measured), pre-existing,
inert on this git, and already recorded as A2 residual `R-E`.

**`V-6` — configuration injection still hides untracked content in default mode.** Reproduced:
`GIT_CONFIG_COUNT` + `GIT_CONFIG_KEY_0=core.excludesFile` turns a `BLOCKED` untracked credential
into `secret guard: clean`, exit 0. The code path (`git ls-files --others --exclude-standard`) is
**not touched by this diff** and is not one of the three calls that gained `_cs_git`. This is A2
residual `R-C` verbatim, pre-existing, outside D-062's boundary. Recorded, not reopened.

**`V-7` — the argument parser's semantics changed slightly.** `--staged` was previously recognised
only as `$1`; it is now recognised anywhere in the argument list, and unknown arguments are still
ignored. The only invocation of `check-secrets.sh` anywhere in the repository outside the hook is
`scripts/test.sh:219`, which passes no arguments, so no live caller changes behaviour. Recorded
because it is a behaviour change the diff makes and `IMPLEMENTATION.md` does not mention.

**`V-8` — a relative `GIT_INDEX_FILE` is resolved against `INVOKING_ROOT`, not the process CWD.**
Git resolves a relative `GIT_INDEX_FILE` against the CWD. Under git's real invocation the two are
the same, because git runs hooks at the worktree top (measured, including for a commit issued from
a subdirectory). They diverge only for a hand-invocation of the hook from a subdirectory, where the
hook resolves to a file git would not have used — measured, and it resolves toward scanning **more**,
not less. Unreachable through git; recorded for completeness.

**`V-9` — a wording imprecision in `IMPLEMENTATION.md`, not a behaviour defect.** It says
`GIT_INDEX_FILE` is set "as a per-command prefix on exactly three calls". There are exactly three
**call sites**; the staged blob read executes twice per scanned path, because `_sec_content` is
invoked once by the credential scan and once by the machine-path scan. The measured count on a
one-file run is four invocations, which is also what A2's `B4` census reports. Both scans reading
the same index is correct and is what stops rule 3 and rule 4 from disagreeing about which bytes
they judged.

**`V-10` — `A2-tests/VERIFICATION-2.md` residuals `R-A` through `R-F` were not probed** beyond the
two incidental reproductions noted at `V-5` and `V-6`. D-062 reopens none of them and neither does
this verification. Read no coverage into the silence.

---

## 11. WHAT THIS VERIFICATION DOES NOT ESTABLISH

- **One platform, one git, one shell.** `git 2.50.1 (Apple Git-155)`, `bash 3.2.57(1)`, `darwin`
  25.5.0, `core.quotePath` and `diff.renames` at defaults, on a **case-insensitive** filesystem
  (`core.ignorecase=true`). The temporary-index spellings `.git/index.lock` and
  `.git/next-index-<pid>.lock` are what this git produces; a git that produced a third spelling
  would be refused by the basename rule, which is fail-closed but would be a false refusal. Not
  tested under bash 4 or 5, and not tested on a case-sensitive filesystem.
- **No completing gate run.** `contracts/lib` is unpopulated and `ts/node_modules` is absent in an
  isolated clone, so no run of `scripts/test.sh` here reaches completion. Nothing is concluded
  about the gate, about Solidity, or about the TypeScript suites. Both frozen harnesses clone
  `ROOT` at HEAD and never read the working tree, which is why every measurement above was taken
  against clones pinned to an explicit SHA rather than against a working directory.
- **Concurrency and the validate/scan race were not probed** (`V-3`). Nothing here runs two commits
  at once, and no timing attack was attempted.
- **Interactive commit forms were not driven** — `git commit -p`, `git commit --interactive`. The
  card excludes them and this verification did not add them.
- **The credential pattern set was not re-verified.** One fixture shape was used: 64 repetitions of
  one hex character bound to a key-shaped identifier. Whether `check-secrets.sh` catches other
  credential shapes is A-052/A-058 territory and was not re-measured here.
- **Everything the card places outside its boundary was not probed**: raw NUL-delimited status
  parsing, rename and copy destination handling, mode and gitlink handling, default-mode index-blob
  behaviour (D-061(1)), repository identity resolution beyond the two identity refusals observed in
  passing, `scripts/test.sh` and its supervisor, `install-hooks.sh`, and the other twelve check
  scripts.
- **Whether the repair is minimal is not established.** It is a judgement, and this verification
  measured behaviour, not economy. What it does establish is that the repair does not exceed its
  two permitted files.
- **This verification says nothing about Batch A1.** A1 remains recorded FAILED under D-061(4);
  neither attempt is relabelled successful, and no A1 finding or residual is reopened. It says
  nothing about D-055's exit condition, signs nothing, certifies nothing, and ratifies nothing.

---

## 12. INTEGRITY OF THE ARTEFACTS

| claim | measured |
|---|---|
| production files changed | exactly two: `.githooks/pre-commit`, `scripts/check-secrets.sh` |
| existing harnesses changed | none — all three byte-identical at `28fa955`, `c73b17a` and the frozen SHA |
| existing evidence files changed by the implementation commit | none — `c73b17a..492021` is four files: the two production files, `+1` line in `docs/decisions.md`, and the new `IMPLEMENTATION.md` |
| harness sha256 after every run in this verification | unchanged (values in the header) |
| the primary repository during this verification | untouched; every probe ran against private clones, and the only write is this file |
| `HEAD` of the primary repository while measuring | `492021325255f56ed8d3df8265bbaa43ef0f7efa`, working tree clean |

---

**VERDICT: HOLD.** The repair closes the seven demonstrated failures, holds the five anti-regression
cases, survives 45 direct probes of its validation rule without a single fail-open, works in both
repository layouts its own author left unmeasured, and collides with A2 in exactly the two places
D-064 rules superseded and nowhere else.
