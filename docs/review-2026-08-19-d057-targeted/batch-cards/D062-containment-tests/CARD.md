# BATCH CARD D-062 — the `GIT_INDEX_FILE` containment exception

**Authority:** D-062. **Base SHA:** `28fa955` — and the two production files are byte-identical
at `28fa955` and at `76c466f`, so the harness may be run at either. **Demonstrated at:**
`76c466fe95ef4a69a1ce86f271498e076e5343aa`.

**This card is small on purpose. It claims completeness ONLY inside the boundary below.** It is
**not** a third general Batch A1 attempt. Batch A1 stays recorded as FAILED under D-061(4);
neither of its attempts is relabelled successful, and no other A1 finding or residual is
reopened by this card.

## THE INVARIANT — one

> **The pre-commit guard scans THE INDEX THAT IS ABOUT TO BECOME THE COMMIT, and refuses rather
> than reporting a result it did not establish — while an arbitrary caller-supplied
> `GIT_INDEX_FILE` still redirects nothing.**

Both halves are load-bearing, and the two failed A1 attempts are one on each side of them.
Attempt one honoured the caller's git environment and let a foreign repository be measured.
Attempt two scrubbed it, including the variable git itself uses to hand a hook the temporary
index, and let a credential reach HEAD through `git commit -am`. **Too much deference, then too
little; both fail open.**

## BOUNDARY — explicit, and narrower than any previous card

**Two production files, and no others may change under this card:**

- `.githooks/pre-commit`
- `scripts/check-secrets.sh`

**Symbol boundary — the paths under test:**

- the pre-commit hook's handling of the git environment it is handed, from capture through to
  whatever it passes to the guard
- `check-secrets.sh` `--staged` mode: the staged enumeration (`git diff --cached --raw`) and the
  staged blob read (`git show ":<path>"`)
- `check-secrets.sh` default mode, **only** to the extent that a caller-supplied
  `GIT_INDEX_FILE` must not redirect it (control `7-def`)

**Explicitly outside the boundary and unchanged by this card:** raw NUL-delimited status
parsing, rename and copy destination handling, mode and gitlink handling, index-blob behaviour
in default mode, the staged-deletion control, repository identity resolution, `scripts/test.sh`
and its supervisor, `install-hooks.sh`, and the other twelve check scripts.

## TEST MATRIX — twelve cases, all required

| # | Case | Required behaviour |
|---|---|---|
| 1 | `git commit -am` with a planted credential | **BLOCKED**, guard names the file, nothing in HEAD |
| 2 | `git commit -m … -- <path>` with a planted credential | **BLOCKED**, guard names the file, nothing in HEAD |
| 3 | `git add` then `git commit`, planted credential | **remains BLOCKED** — the positive control |
| 4 | clean `git commit -am` | **ALLOWED**, reports clean, content reaches HEAD |
| 5 | clean path-limited commit | **ALLOWED**, reports clean, content reaches HEAD |
| 6 | genuine staged deletion — **6a** pre-staged, **6b** through the temporary index | **ALLOWED**, never a false failure |
| 7 | `check-secrets.sh --staged` with a malicious caller `GIT_INDEX_FILE` at a clean decoy index | **still scans the canonical index** (12-F2 anti-regression) |
| 8 | hook handed a `GIT_INDEX_FILE` outside the invoking repository's index directory | **REFUSE** |
| 9 | hook handed a **9a** symlinked / **9b** nonexistent temporary index | **REFUSE** |
| 10 | hook handed a valid `.git/index.lock` carrying a credential | **SCAN it** — blocked, named |
| 11 | hook handed a valid `.git/next-index-<pid>.lock` carrying a credential | **SCAN it** — blocked, named |
| 12 | the victim repository across every refusal case | **byte-identical** config, index, HEAD and files |

## CONTROLS — each must behave OPPOSITELY, or the matching case proves nothing

- **`1-tmp`, `2-tmp`** — a probe hook records what git actually hands the hook for each commit
  form and proves the temporary index **carries the candidate credential** while the canonical
  index is empty. Without this, cases 1 and 2 would be measuring nothing.
- **Case 3 is the positive control for 1 and 2** — the same credential, the same guard, the
  ordinary staged route. It is blocked at the pre-repair baseline, so the credential is
  demonstrably detectable and the failures at 1 and 2 are about the index, not the pattern.
- **Cases 1 and 2 are the opposite control for 4 and 5**, and vice versa: a repair that refuses
  every `-a` commit fails 4 and 5; a repair that accepts every `-a` commit fails 1 and 2.
- **`6c`** — a deletion staged alongside a credential is still blocked, so the deletion path
  cannot be satisfied by blanket acceptance.
- **`7-decoy`** — the decoy index is potent and clean: honouring it yields an empty staged set
  while the canonical set holds the fixture. So a clean report at case 7 would be a real failure
  rather than an unreadable-object artifact. **`7-nov`** and **`7-def`** prove the fixture is
  live on both invocation shapes.
- **`8-L1` / `8-L2`** — the emulated hook invocation used by cases 8-11 exits 0 and reports
  clean on an empty canonical index, and blocks a credential staged in it. Without both, a
  refusal at case 8 could be an artifact of the emulation.
- **`8-read`** — the victim index is readable from the subject and reads clean.
- **`9-sym` / `9-abs`** — the planted symlink really is a symlink, and the missing file really
  is missing, at scan time.
- **`10-tmp` / `11-tmp`** — the planted temporary index is a regular non-symlink file, carries
  the credential, and the canonical index is empty.
- **`12-live`** — the victim fingerprint moves under a deliberate change, so case 12 is not
  vacuous.
- **`Z-frozen` / `Z-cfg`** — the two frozen harnesses are byte-identical to their declared
  sha256 values, and the redirected git configuration is unchanged by the run.

## EXCLUSIONS

- **No implementation is proposed here.** Every assertion is on behaviour: what is blocked, what
  is allowed, what is refused, what reaches HEAD. Nothing asserts how the hook and the guard
  communicate.
- **Residuals `R-A` through `R-F`** recorded in `A2-tests/VERIFICATION-2.md` are **not probed**
  and are not reopened.
- **Interactive commit forms** (`git commit -p`, `git commit --interactive`) are not driven.
- **One platform, one git.** See `COVERAGE.md` §2.

## STOPPING RULE

D-062(4): one implementation and one independent verification. The implementer may not modify,
weaken, relocate or delete this harness (D-058(1)). If a case here is believed invalid, the
implementation **stops** and has the invalidity independently confirmed before anything changes.
