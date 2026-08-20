# D-062 CONTAINMENT — THE MEASURED PRE-REPAIR BASELINE

**Harness:** `d062-containment.sh`
**sha256:** `c830d195281c0a2bae2fd62e79ce1d1402f03182bb2fbc446361c91fd89a1756`
**Measured at:** `76c466fe95ef4a69a1ce86f271498e076e5343aa`, working tree clean under
`.githooks/` and `scripts/`.
**Applies to:** `28fa955` as well — `git diff 28fa955 HEAD -- .githooks/pre-commit
scripts/check-secrets.sh` is **0 bytes**, verified in this session and re-verified by the
harness itself at `Z-base` on every run. The intervening commits are documentation only.

**Platform.** `git version 2.50.1 (Apple Git-155)`; `GNU bash, version 3.2.57(1)-release
(arm64-apple-darwin25)`; `darwin`; `core.quotePath` and `diff.renames` at their defaults.

**Production files as measured.**

| file | sha256 |
|---|---|
| `.githooks/pre-commit` | `8a99a47a804d524a1bce1e303432f9a6a13134a822b6b4b48b982ae16ff26288` |
| `scripts/check-secrets.sh` | `3dd94dabf54345d357de8aa47af7cf006129d8028df845d1b83ed5ee51d05c49` |

**Frozen harnesses, re-verified and untouched.**

| file | sha256 | matches declared |
|---|---|---|
| `A1-tests/a1-repo-identity.sh` | `54535b3b139ef9098753393872e39c932e25e0d861cfa14eb04e6f18c591122d` | yes |
| `A2-tests/a2-env-and-supervisor.sh` | `dd67d69a13faf43e0578c57f9681e1468ca0b721727e7f14e83c1e5859fc84a7` | yes |

**Harness exit status: 1** — seven REQUIRED failures, **zero CONTROL failures**. Three runs
(twice with an explicit root, once with the default root resolution) produced identical
verdicts.

---

## 0. THE MECHANISM, RE-MEASURED RATHER THAN QUOTED

Preflight `P6` drives three real commit forms through a probe hook that records its environment
and exits 1, so nothing lands.

```
P6 git commit -a        -> GIT_INDEX_FILE=<scratch>/sut/.git/index.lock
P6 git commit -- <path> -> GIT_INDEX_FILE=<scratch>/sut/.git/next-index-262.lock
P6 git commit           -> GIT_INDEX_FILE=.git/index
P6 hook environment: GIT_DIR=<unset> GIT_WORK_TREE=<unset> GIT_COMMON_DIR=<unset> GIT_PREFIX=[] PWD=<scratch>/sut
```

The `<pid>` in the second line varies per run, as it must. `GIT_DIR`, `GIT_WORK_TREE` and
`GIT_COMMON_DIR` are **unset** by this git when it runs a hook in an ordinary clone; the
emulation used by cases 8-11 reproduces exactly that, and `P6` fails the run rather than
emulating a fiction if a future git changes it.

`P5` proves the planted credential trips `check-secrets.sh` in **both** modes before any case
runs (`default=1 staged=1`). `P1` proves `/usr/bin/grep` finds a planted canary, so every zero
count below is trustworthy.

---

## 1. THE MATRIX

| # | required behaviour | baseline verdict | did the control discriminate? |
|---|---|---|---|
| 1 | `git commit -am` + credential → BLOCKED | **FAIL** | **yes** — `1-tmp` proves the temporary index carried the credential and the canonical index was empty; case 3 proves the credential is detectable |
| 2 | `git commit -m … -- <path>` + credential → BLOCKED | **FAIL** | **yes** — `2-tmp`, same structure |
| 3 | `git add` + `git commit` + credential → BLOCKED | **PASS** | **yes** — this is itself the positive control, and it is the only credential route the baseline blocks |
| 4 | clean `git commit -am` → ALLOWED | **PASS** | **no, not at the baseline** — see §3 |
| 5 | clean path-limited commit → ALLOWED | **PASS** | **no, not at the baseline** — see §3 |
| 6a | pre-staged genuine deletion → ALLOWED | **PASS** | **yes** — `6c` proves the deletion path does not blanket-accept |
| 6b | deletion through the temporary index → ALLOWED | **PASS** | **no, not at the baseline** — see §3 |
| 7 | `--staged` + malicious caller `GIT_INDEX_FILE` → still scans canonical | **PASS** | **yes** — `7-decoy` proves the decoy is potent and clean; `7-nov` and `7-def` prove the fixture is live on both shapes |
| 8 | hook + `GIT_INDEX_FILE` outside the index directory → REFUSE | **FAIL** | **yes** — `8-L1`/`8-L2` prove the emulation both passes and blocks; `8-read` proves the victim index reads clean rather than erroring |
| 9a | hook + symlinked temporary index → REFUSE | **FAIL** | **yes** — `9-sym` proves it is a symlink at scan time |
| 9b | hook + nonexistent temporary index → REFUSE | **FAIL** | **yes** — `9-abs` proves it is absent at scan time |
| 10 | hook + valid `index.lock` → SCAN it | **FAIL** | **yes** — `10-tmp` proves the file is a regular non-symlink carrying the credential while the canonical index is empty |
| 11 | hook + valid next-index temporary → SCAN it | **FAIL** | **yes** — `11-tmp`, same structure |
| 12 | victim config and files unchanged through every refusal | **PASS** | **partly** — `12-live` proves the fingerprint can move, but the baseline never reaches the victim at all; see §3 |

**Seven REQUIRED failures across the six cases the brief predicted would fail** — cases 1, 2, 8,
9, 10 and 11, with case 9 scored as two lines (9a symlink, 9b missing). **Six pass as controls**
— cases 3, 4, 5, 6, 7 and 12, exactly as predicted. **No case failed for an incidental
reason**, and no control failed.

---

## 2. PER CASE — COMMAND, OUTPUT, VERDICT

Paths are shown relative to the private clone. `<64-hex>` stands for the run-time-assembled
credential value: **the literal cannot be written into this file, because `check-secrets.sh`
would block the commit carrying it** — which is itself a small piece of evidence that the guard
works on the ordinary staged route.

### Case 1 — `git commit -am` with a planted credential → must be BLOCKED. **FAIL**

```
$ printf 'export const signerKey = "0x<64-hex>";\n' >> d062-fixture.txt
$ git commit -am "case 1"
secret guard: clean
[detached HEAD 21d94b6] case 1
 1 file changed, 1 insertion(+)
$ echo $?
0
$ git show HEAD:d062-fixture.txt | grep -c '<64-hex>'
1
```

The guard's entire verdict is one line, `secret guard: clean`, and the commit proceeds on it.
**The credential is in HEAD.** Control `1-tmp` recorded, for this exact command line, that the
temporary index git handed the hook staged `d062-fixture.txt`, that its blob contained the
credential, and that the canonical index staged nothing.

### Case 2 — `git commit -m … -- <path>` with a planted credential → must be BLOCKED. **FAIL**

```
$ git commit -m "case 2" -- d062-fixture.txt
secret guard: clean
[detached HEAD 1b019e4] case 2
 1 file changed, 1 insertion(+)
$ echo $?
0
```

Same shape, same outcome, credential in HEAD. Control `2-tmp` held.

### Case 3 — `git add` then commit → must remain BLOCKED. **PASS**

```
$ git add d062-fixture.txt && git commit -m "case 3"
BLOCKED d062-fixture.txt — credential-shaped content:
    2:signerKey = "0x<64-hex>
secret guard: 1 finding(s). Do not weaken this guard to make a commit pass (AGENTS.md).
If this is a false positive, fix or refine the guard and document why.
$ echo $?
1
```

**This is the positive control on which cases 1 and 2 rest.** Byte-identical fixture, same
guard, same hook, ordinary staged route: named, blocked, out of HEAD. So the failures at 1 and 2
are about which index was read, not about whether the credential is detectable.

### Case 4 — clean `git commit -am` → must remain ALLOWED. **PASS**

```
$ printf 'an edit that carries nothing credential-shaped\n' >> d062-fixture.txt
$ git commit -am "case 4"
secret guard: clean
[detached HEAD 7c773e6] case 4
 1 file changed, 1 insertion(+)
```

Allowed, clean, and the intended content is in the new HEAD. **See §3: this passes without
discriminating at the baseline.**

### Case 5 — clean path-limited commit → must remain ALLOWED. **PASS**

Identical outcome via `git commit -m "case 5" -- d062-fixture.txt`. Same caveat.

### Case 6a — pre-staged genuine deletion → must remain ALLOWED. **PASS**

```
$ git rm -q d062-fixture.txt && git commit -m "case 6a"
secret guard: clean
[detached HEAD 155e05c] case 6a
 1 file changed, 1 deletion(-)
 delete mode 100644 d062-fixture.txt
```

No false failure. This is the D-059(3) / D-061(1) protected control, and it is the **only**
"allowed" case that discriminates at the baseline, because a pre-staged deletion is enumerated
through the canonical index the baseline actually reads.

### Case 6b — deletion through the temporary index → must remain ALLOWED. **PASS**

```
$ rm d062-fixture.txt && git commit -am "case 6b"
secret guard: clean
[detached HEAD fdc7fd5] case 6b
 1 file changed, 1 deletion(-)
 delete mode 100644 d062-fixture.txt
```

**See §3.**

### Control 6c — deletion staged alongside a credential → must still be BLOCKED. **PASS**

```
$ git rm -q d062-second.txt
$ printf 'export const signerKey = "0x<64-hex>";\n' >> d062-fixture.txt && git add d062-fixture.txt
$ git commit -m "case 6c"
BLOCKED d062-fixture.txt — credential-shaped content:
    ...
$ echo $?
1
```

The presence of a deletion does not buy acceptance.

### Case 7 — `--staged` with a malicious caller `GIT_INDEX_FILE` → must still scan Sentinel. **PASS**

The decoy is built inside the subject's **own object store** (`GIT_INDEX_FILE=<decoy> git
read-tree HEAD`), so honouring it would read **clean** rather than fail closed on an unreadable
object. Control `7-decoy` measured exactly that:

```
staged set with the decoy honoured : []
staged set with no caller variable : [d062-fixture.txt]
```

```
$ GIT_INDEX_FILE=<decoy> ./scripts/check-secrets.sh --staged
BLOCKED d062-fixture.txt — credential-shaped content:
    2:signerKey = "0x<64-hex>
secret guard: 1 finding(s). ...
$ echo $?
1
```

**This passes for the right reason** — the `12-F2` scrub doing its job — and it is in the matrix
so a repair cannot buy cases 1 and 2 by re-honouring an inherited `GIT_INDEX_FILE`. Controls
`7-nov` (no variable) and `7-def` (default mode with the same variable) both blocked.

### Cases 8-11 — the emulated hook invocation

Liveness first, because nothing in 8-11 means anything without it:

```
8-L1  hook, GIT_INDEX_FILE=.git/index, nothing staged  -> exit 0, "secret guard: clean"
8-L2  hook, GIT_INDEX_FILE=.git/index, credential staged -> exit 1, "BLOCKED d062-fixture.txt ..."
```

The emulation is therefore neither inert nor inherently broken.

**Case 8 — `GIT_INDEX_FILE` outside the invoking repository's index directory → must REFUSE.
FAIL.**

```
$ cd <subject> && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_COMMON_DIR \
      GIT_PREFIX="" GIT_INDEX_FILE=<victim>/.git/index ./.githooks/pre-commit
secret guard: clean
$ echo $?
0
```

Control `8-read` first established that the victim index is readable from the subject and reads
clean — `:000000 100644 0000000 db06832 A  VICTIM-ONLY.md` — so a refusal here could not have
been an unreadable-object artifact. The hook neither refuses nor reports anything about the
foreign path; it clears the variable and reports clean over the canonical index.

**Case 9a — symlinked temporary index → must REFUSE. FAIL.**

```
$ ln -sf <scratch>/outside.idx <subject>/.git/index.lock
$ ... GIT_INDEX_FILE=<subject>/.git/index.lock ./.githooks/pre-commit
secret guard: clean
$ echo $?
0
```

Control `9-sym` confirmed the planted path is a symlink at scan time.

**Case 9b — nonexistent temporary index → must REFUSE. FAIL.**

```
$ ... GIT_INDEX_FILE=<subject>/.git/next-index-99999.lock ./.githooks/pre-commit
secret guard: clean
$ echo $?
0
```

Control `9-abs` confirmed the path does not exist at scan time.

**Case 10 — valid `.git/index.lock` carrying a credential → must be SCANNED. FAIL.**

The temporary index is built the way git builds one:

```
$ GIT_INDEX_FILE=.git/index.lock git read-tree HEAD
$ GIT_INDEX_FILE=.git/index.lock git add d062-fixture.txt
```

Control `10-tmp` then measured, before the hook ran:

```
temp-index staged set        : [d062-fixture.txt]
temp-index blob has credential: 1
canonical index staged set   : []
regular non-symlink file     : yes
```

```
$ ... GIT_INDEX_FILE=<subject>/.git/index.lock ./.githooks/pre-commit
secret guard: clean
$ echo $?
0
```

**A credential that is provably in the index about to become the commit is reported clean.**

**Case 11 — valid `.git/next-index-<pid>.lock` carrying a credential → must be SCANNED. FAIL.**

Identical construction and identical outcome with `next-index-24680.lock`; control `11-tmp`
held on all four sub-measurements.

### Case 12 — the victim repository is unchanged. **PASS**

```
victim fingerprint before = 48821767f9b41d745e731ee2d196827bed2fd2a55ec714e82102e30198d771f9
victim fingerprint after  = 48821767f9b41d745e731ee2d196827bed2fd2a55ec714e82102e30198d771f9
```

The fingerprint covers `HEAD`, the whole `.git/config`, `git ls-files -s`, `git status
--porcelain` and a sha256 of every worktree file. Control `12-live` then deliberately edited a
victim file and confirmed the fingerprint moves, so "unchanged" is a measurement. **See §3 for
why this is weaker at the baseline than it will be after a repair.**

---

## 3. WHERE THE BASELINE RESULT IS WEAKER THAN IT LOOKS — SAID PLAINLY

**Cases 4, 5 and 6b pass for the wrong reason at the baseline.** The guard reads the canonical
index, which for those commit forms is empty, and prints clean. The commit is allowed because
nothing was examined, not because the right thing was examined and found clean. Nothing
observable from outside separates *"read the right index, found nothing"* from *"read the wrong
index, found nothing"* when the correct answer is also nothing. Their value is as the **opposite
control** that stops a repair satisfying cases 1 and 2 by refusing every `-a` commit — and that
value is only realised once cases 1 and 2 pass.

**Case 12 passes trivially at the baseline**, because the baseline clears `GIT_INDEX_FILE`
before anything runs and so never reaches the victim by any route. It becomes a real assertion
only once a repair starts resolving the handed path.

**Case 6a and case 3 are the two "should already pass" cases that genuinely discriminate at the
baseline.** Everything else in the PASS column is anti-regression, not evidence.

**Every FAIL is attributable.** Each of the seven failing lines has a control proving the
fixture, the temporary index or the invocation shape was live, and each asserts on the guard's
own output rather than on exit status alone. None of the seven failed because a command was
missing, a fixture was broken or a commit failed generically: in all seven the guard **ran, and
printed `secret guard: clean`.**

---

## 4. THE CONTRACT WAS CHECKED FOR SELF-CONTRADICTION

§0 of `docs/session-state.md` records, dated the day before this work: *"A TEST CAN BE INVALID,
AND TWO FAILING TESTS HIDE IT. A1's original case 4 demanded a non-zero exit from the same
command line case 2 demanded exit 0 from. Both failed at the pre-repair baseline, so the
contradiction was invisible until an implementation made one pass."*

That failure mode is not detectable by reasoning alone, so it was measured. A **throwaway
sketch** was applied to a private scratch clone purely to establish that the twelve REQUIRED
cases are **simultaneously satisfiable**, and the harness was run against it:

```
REQUIRED failures : 0
CONTROL  failures : 0
ALL REQUIRED CASES AND ALL CONTROLS HELD.   (exit 0)
```

**No two REQUIRED assertions in this matrix contradict each other, and every one of them is
reachable.** The sketch was then discarded. It is deliberately **not** part of this deliverable,
is not reproduced anywhere in it, and is not a proposed design: its only purpose was to prove
this contract is satisfiable rather than merely unfalsifiable. The implementer receives the
contract, not a solution.

---

## 5. HYGIENE

- Every scored run used a private clone under `TMPDIR` and repositories the harness created.
  **The primary repository was read only** and ends this session with zero modified paths under
  `.githooks/` and `scripts/` (`Z-tree`).
- `HOME` and the global, system and XDG git configuration were redirected into the scratch area
  for every scored run, and their fingerprint is asserted unchanged at `Z-cfg`.
- Git configuration was never written into a repository this work did not create.
- Both frozen harnesses were hashed at the start and at the end of every run and match their
  declared values (`Z-frozen`).
- **No production file was modified.** The commit carrying this directory contains no change to
  `.githooks/`, `scripts/`, `ts/`, `contracts/`, `verifier/` or `fixtures/`.
