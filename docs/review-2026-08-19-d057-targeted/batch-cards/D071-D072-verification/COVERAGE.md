# D-071 / D-072 coverage

What this card measures, what it does not, and where it is blind.

## In

| Row | Hole | Exploit control | Observing assertion | Baseline (expected) |
|---|---|---|---|---|
| R5-1 | Fast UNVERIFIED did not name the ack variable | Isolated clone origin is a local path; output is UNVERIFIED not "no remote" | Fast UNVERIFIED line names `SENTINEL_RENAME_GATE_UNVERIFIED_OK` | FAIL (exit 0 already; name absent) |
| R5-2 | Deep UNVERIFIED exited 0 | Same UNVERIFIED clone | `--gate` non-zero | FAIL |
| R5-3 | Deep ack did not disclose "acknowledged, not verified" | Same clone with `SENTINEL_RENAME_GATE_UNVERIFIED_OK=1` | Exit 0 **and** disclosure in own output | FAIL (exit 0 without disclosure) |
| R5-4 | (control path) readable PRIVATE still clean | `gh repo view` returns PRIVATE | Exit 0, clean line | PASS if control fires; else NOT_MEASURED |
| R5-5 | `test.sh --gate` printed `GATE PASSED` while rename-gate was UNVERIFIED | Clone still UNVERIFIED immediately before the gate | No `GATE PASSED`, non-zero | FAIL if the gate completes; NOT_MEASURED if it cannot |
| V6-*-secrets | Unpinned `--exclude-standard` hides untracked credentials | Unpinned call omits the plant; potency: consumer blocks when it sees it | `check-secrets.sh` default blocks the plant | FAIL |
| V6-*-vendor | Same hide against `artifacts()` | Same | vendor-honesty blocks the plant | FAIL |
| R2-vendor | No `-z`; octal-escaped path fails `[ -f ]` | Unquoted listing is not a usable path; ASCII sibling is; payload blocks on ASCII | vendor-honesty blocks the café plant | FAIL |
| R2-secrets | Only if `-z` still drops the path | `-z` listing measured | secrets blocks the café plant | NOT_MEASURED unless `-z` drops |

## Out

- `scripts/check-v1-index-ordering.sh` untracked scan (own fixture).
- Staged / `--staged` secret-guard (not this hole).
- `GIT_CONFIG` (git-config command only, per the manual).
- `GIT_DIR` / `GIT_WORK_TREE` / `GIT_INDEX_FILE` / `GIT_COMMON_DIR` /
  `GIT_PREFIX` (12-F2; they redirect the repository, not
  `core.excludesFile`).
- In-tree `.gitignore` (tracked content, not caller env).
- `$GIT_DIR/info/exclude` once `GIT_DIR` is unset (real repo state).
- D-016 verbs other than origin visibility: demos, published links,
  portfolio or resume references.
- Current-freeze scoring. Severity. Production edits. D-055. Gate
  signing. Publication. The five D-008 questions.
- D-067's named limits are not lifted by writing this card.

## Blind spots (named, not closed)

- **One git, one OS.** `git version 2.50.1 (Apple Git-155)` on macOS.
  Another git's quote-path or COUNT handling is unmeasured.
- **NOSYSTEM** is inert unless the machine's real system config already
  excludes the plant. This harness will not write `/etc/gitconfig` to
  make it potent. An inert NOSYSTEM row is NOT_MEASURED, not a pass.
- **R5-4** depends on `gh` being able to read PRIVATE on this machine
  at run time. An invalid token makes the row NOT_MEASURED.
- **R5-5** is a full `--gate` (fuzz 20000, corpus). At this baseline it
  **did complete** after `npm --prefix ts ci` in the isolated clone
  (`ts/node_modules` is gitignored; the first attempt died with
  `GATE DID NOT REACH COMPLETION` and is not the observation). Stages
  after an UNVERIFIED rename-gate still run; that accumulation is why
  the full run is the instrument. A clone without TypeScript deps
  cannot emit `GATE PASSED` and must not be scored as this row.
- **Vendor `artifacts()`** also lists tracked files. The plant is
  untracked; a tracked file that already contains a roster name is a
  different failure and would make potency unreadable. The harness
  uses a fresh clone of a commit that itself passes vendor-honesty.
- **HOME sandboxing** for COUNT/GLOBAL/SYSTEM redirects `HOME` to an
  empty sandbox so the operator's `~/.config/git/ignore` is not a
  second excluder. That isolation is not the HOME vector. The HOME
  vector is a separate row that puts the ignore file in the sandbox.
- **Does not claim** every git config key. The matrix is the
  enumeration's hide-untracked vectors against the two production
  untracked consumers.
- **Does not claim** R2 against secrets unless `-z` is measured to
  drop the path.

A green CONTROL is evidence only for what it exercised. A FAIL at the
baseline is evidence that the REQUIRED assertion observed the hole it
names, provided its CONTROL fired.
