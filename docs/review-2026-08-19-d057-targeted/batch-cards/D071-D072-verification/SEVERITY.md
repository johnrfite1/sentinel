# D-071 / D-072 — independent severity

Reviewer is not the test author, the verifier, or the implementer. This
document scores the **pre-repair defects** at the parents the card
measured. It does not score whether the repairs hold. HOLD/FAIL of the
card is the verifier's job.

**Redaction (John, session four, 2026-08-23).** Live D-008(2)/(4)
scanner literals in the scan-description parentheticals were replaced
with named tokens (`<D-008-2-label>`, `<D-008-2-label-alt>`,
`<vendor-name>`). **Severities (R5 High, V-6 High, R2 Medium),
reasoning, and upgrade/downgrade conditions are unchanged.** This
paragraph is disclosure of the redaction, not a rescoring.

It does not score D-055. It does not lift D-067. Named completeness
limits stay named. D-016 stands. No gate is signed, reopened, or
annotated.

Scale is the same one used for R1's first adjudication (F61ECCA
`INDEPENDENT-REVIEW.md`): **Critical / High / Medium / Low / Info**.
Instrument defects are in scope. R1-F1, the Critical that opened this
arc, was a defect in the certification gate: a child or sibling could
rewrite the running parser, and the "private snapshot" claim was false.

SHAs below were remeasured with `git rev-parse` on this machine, not
copied from the brief.

| Role | SHA |
|---|---|
| R5 parent (baseline) | `558d001546b55bd80156bc875cf080fef0e301eb` |
| V-6 / R2 parent (R5 repair; V-6 baseline) | `1ae684cec83c7bfdb24a8c18ffdeba87c535874f` |
| HEAD at adjudication | `f4d124323f0f5a0c62e585e48febcee191de7477` |

Live script names at those parents, from `git ls-tree`:
`scripts/check-rename-gate.sh`, `scripts/test.sh`,
`scripts/check-secrets.sh`, `scripts/check-vendor-honesty.sh`.

---

## R5 (D-071) — **High**

### The defect (pre-repair)

At `558d001546b55bd80156bc875cf080fef0e301eb`,
`scripts/check-rename-gate.sh` has no `--gate` profile. Every
UNVERIFIED path — no remote, no `gh`, empty visibility from `gh` —
prints `UNVERIFIED` and **exits 0**. An isolated clone whose origin is
a local path is that last case: `gh` cannot read a GitHub slug, so the
script cannot tell PRIVATE from PUBLIC. `scripts/test.sh --gate` at
that parent invokes the rename-gate with no extra flag
(`./scripts/check-rename-gate.sh || fail=1`) and prints `GATE PASSED`
only if `fail` is still 0 at the end. UNVERIFIED therefore never sets
`fail`. The card produced UNVERIFIED by cloning the R5-parent worktree
so origin was `/tmp/sentinel-r5-base` (not a GitHub slug). Fast and
`--gate` on that clone both printed UNVERIFIED. The completing
top-level run (`logs/r5-5-gate.meta`) recorded `precheck_rc=0`,
`gate_rc=0`, UNVERIFIED at line 68 of `logs/r5-5-gate.log`, and
standalone `GATE PASSED` at line 1054.

Measured UNVERIFIED line (R5-1 / R5-2, `logs/r5-1-fast.log`):

```
rename gate: UNVERIFIED — could not read visibility for /private/tmp/sentinel-r5-base (auth? network?).
  D-016 still blocks publication. Verify manually before any public action.
```

R5-5 precheck and `logs/r5-5-gate.log` line 68 are the same sentence with
`/tmp/sentinel-r5-base` (macOS `/tmp` → `/private/tmp`). Same clone class.

Harness `logs/matrix.tsv`: `R5-2-deep-refuse` `deep UNVERIFIED no-ack rc=0`;
`R5-5-toplevel-gate` `test.sh --gate printed GATE PASSED (rc=0) after UNVERIFIED rename-gate`.
`logs/summary.txt`: `r5_5=completed: GATE PASSED, gate_rc=0, real 1269.37s`.

Fast UNVERIFIED exit 0 is later option C (D-071) and is **not** this
finding. The hole is the **evidence profile treating UNVERIFIED as
success**, so the certification token and the warning disagree.

### What it reaches

- **Instrument:** `scripts/check-rename-gate.sh` (the D-016 mechanical
  publication check) and `scripts/test.sh --gate` (the deep evidence
  runner). Aggregation is `|| fail=1`: exit 0 is success.
- **Claim:** that a deep/evidence run which prints `GATE PASSED` has
  not treated "could not read visibility" as verified-private. At the
  parent it had.
- **Path actually taken:** D-071 records that an isolated exact-commit
  deep gate whose origin is a local path prints UNVERIFIED, and that
  this isolated-clone deep gate is the method D-058(10) itself
  mandates. That is not a synthetic attacker; it is this project's
  own evidence method. A pack assembled that way at the parent carries
  `GATE PASSED` at rc=0 after UNVERIFIED.

Readable PRIVATE still clean (R5-4 PASS: `rename gate: clean
(johnrfite1/sentinel is private; D-016 publication block intact)`).
When visibility is read and is not PRIVATE, the parent script exits 1
(source at that SHA). D-016's other verbs (demos, published links,
portfolio or resume) are out of this card's coverage (D-071 / D-059(7)).

### Severity: **High**

Same class as R1: a guard fail-open on a path operators actually take,
with the ordinary success path still working. Here the path is the
mandated isolated-clone deep gate, and the token that fail-opens is
`GATE PASSED`.

Round 6's live certification defects (an unexamined override certified
as PASS) were High, not Critical. This is that shape: the evidence
runner certifies PASS while the D-016 check did not verify. It is not
R1-F1. The parser is not rewritten. UNVERIFIED is printed. PUBLIC still
fails when readable. D-016 is a publication gate, not an S1 soundness
condition.

High is a useful answer. It is not a failed one.

### What would change it

- **Up to Critical** if UNVERIFIED were silent (no print) and `GATE
  PASSED` still issued, or if a readable PUBLIC origin also exited 0,
  or if D-016 were an S1 soundness condition. None of those is
  measured here.
- **Down to Medium** if `scripts/test.sh --gate` did not include this
  step, or did not print `GATE PASSED` on `fail=0`, or if isolated
  local-origin clones were not the mandated evidence method. They are.
- Fast UNVERIFIED exit 0 does not change this finding. D-071 option C
  keeps that behaviour on purpose. The finding is deep/evidence
  treating UNVERIFIED as success.

### What this is not claiming

- That the repository was public, or that a rename, push, or
  publication happened. The hole is unverified treated as success, not
  PUBLIC treated as PRIVATE.
- That demos, published links, or portfolio references were in
  coverage. D-071 says they are not.
- That the repair holds, or that D-016 is lifted. D-016 still blocks
  publication.
- That option C's fast-profile UNVERIFIED exit 0 is a defect.

---

## V-6 (D-072) — **High**

### The defect (pre-repair)

At `1ae684cec83c7bfdb24a8c18ffdeba87c535874f`, default-mode
`scripts/check-secrets.sh` enumerates untracked files with unpinned

```
git ls-files --others --exclude-standard -z
```

and `scripts/check-vendor-honesty.sh` `artifacts()` enumerates with
unpinned, unquoted

```
git ls-files --others --exclude-standard
```

then keeps a line only if `[ -f "$f" ]`. Neither call overrides
`core.excludesFile`. Git's documented config/env inputs therefore
hide untracked plants from both consumers:

| Vector | Secrets observe at parent | Vendor observe at parent |
|---|---|---|
| `GIT_CONFIG_COUNT` / `KEY` / `VALUE` → `core.excludesFile` | FAIL — `secret guard: clean` | FAIL — mechanical conditions pass |
| `GIT_CONFIG_GLOBAL` | FAIL | FAIL |
| `GIT_CONFIG_SYSTEM` | FAIL | FAIL |
| `HOME` (`$HOME/.config/git/ignore`) | FAIL — `secret guard: clean`; ls-after empty | FAIL |
| `XDG_CONFIG_HOME` (`$XDG_CONFIG_HOME/git/ignore`) | FAIL | FAIL |
| `GIT_CONFIG_NOSYSTEM` | **NOT_MEASURED** — exploit control did not hide | **NOT_MEASURED** |

`logs/matrix.tsv` records potency PASS on every counted row (unpinned
listing showed the plant; consumer blocked when the plant was visible)
and exploit PASS (unpinned listing omitted the plant after injection).
COUNT secrets: ls-before `scratch-d072-secret.env`, ls-after empty,
observe `secret guard: clean`, potency `BLOCKED`. HOME secrets observe
is the same clean line. Vendor observe ends
`vendor honesty: mechanical conditions pass; D-008(1) met and (3)
certified by record` with the plant not named.

`GIT_CONFIG_NOSYSTEM` did not hide on this machine (`logs/v6-NOSYSTEM-secrets.ls-after.txt`
still lists the plant). The harness does not write `/etc/gitconfig`.
That vector is **NOT_MEASURED**, not a pass.

### What it reaches

- **Instrument 1:** `scripts/check-secrets.sh` **default mode** (untracked
  credential census). `scripts/test.sh --gate` at the parent runs
  `./scripts/check-secrets.sh || fail=1` with no `--staged`. A hidden
  untracked plant yields `secret guard: clean` and does not set `fail`.
- **Instrument 2:** `scripts/check-vendor-honesty.sh` `artifacts()`,
  which feeds the D-008(2) label scan (`<D-008-2-label>` /
  `<D-008-2-label-alt>`) and the D-008(4) vendor-name scan (roster
  including `<vendor-name>`). Same `--gate` runner:
  `./scripts/check-vendor-honesty.sh || fail=1`.
- **Claim:** that those two censuses see untracked files that are not
  ignored **by the repository**. At the parent they also honoured
  caller/user `core.excludesFile`, including ordinary `HOME` /
  `XDG_CONFIG_HOME` ignore files.
- **Path actually taken:** `HOME/.config/git/ignore` is gitignore(5)'s
  default when `XDG_CONFIG_HOME` is unset. A global ignore of `*.env`
  is ordinary operator configuration, not a hostile
  `GIT_CONFIG_COUNT` trick. COUNT / GLOBAL / SYSTEM are in scope for
  **production** guards (D-065's "caller git env is out of scope"
  ruling is the A-EXTRACT **instrument**, and D-065(6) says so).

`--staged` / commit-time secrets still block. The card's own potency
controls blocked the visible plant. Tracked files are still scanned.
This hole does not land a secret in HEAD.

### Severity: **High**

Same shape as R1: a secrets-related instrument fail-open on a path
people actually take (here: default-mode census inside `--gate`, and
HOME's default ignore file), while another path still holds
(`--staged`). It also fail-opens the D-008(2)/(4) mechanical scans for
untracked artifacts, which is the completeness limit D-067 named — a
disposition, not a severity cap.

It is not Critical. Staged/commit-time still blocks. Tracked files
still scan. An untracked secret hidden by `excludesFile` does not
enter history through this hole. R1-F1's bar (running parser
rewritable; claimed impossibility false) is not met.

Two Highs in one card are still Highs. HOME alone would carry this
rating; COUNT/GLOBAL/SYSTEM are additional demonstrated vectors, not
the reason for High.

### What would change it

- **Up to Critical** if `--staged` / the pre-commit path also honoured
  `core.excludesFile` and admitted a credential to the index. The
  card's potency controls show the opposite when the plant is visible.
  That upgrade is not measured as open.
- **Down to Medium** if default-mode secrets were not a `--gate`
  stage, or if HOME and XDG were inert and only COUNT/GLOBAL/SYSTEM
  worked (hostile env only). HOME and XDG fired. Default-mode secrets
  is a `--gate` stage.
- **NOSYSTEM remaining NOT_MEASURED** does not by itself change High.
  HOME already fired.

### What this is not claiming

- That a secret was committed, or that `--staged` was open. It was
  not, on the card's potency rows.
- That in-repo `.gitignore` (tracked) is this defect.
  `--exclude-standard` honouring *repository* ignore rules is the
  parent script's stated design ("an ignored file is not one
  `git add -A` away"). The defect is **caller/user** `core.excludesFile`
  (COUNT/GLOBAL/SYSTEM/HOME/XDG) hiding plants from a census that
  claims to scan untracked-not-ignored-in-the-repo.
- That NOSYSTEM hides on this machine. It did not. NOT_MEASURED.
- That D-008(1) or (3) were bypassed. Those are John's to certify;
  the script says so. This hole is (2) and (4) completeness plus the
  default-mode secret census.
- That D-067 is lifted. R2 and V-6 remain the named D-008(2)/(4)
  completeness limits until John rules. This is severity of the
  pre-repair behaviour, not a lift.
- That the repair holds.

---

## R2 — **Medium** (sibling completeness hole; same pin)

### The defect (pre-repair)

At the same V-6 parent, `artifacts()` has no `-z`. Unquoted
`git ls-files --others --exclude-standard` octal-escapes a non-ASCII
path. `[ -f "$f" ]` is then false and the file is dropped. The card's
unquoted listing (`logs/r2-unquoted.ls.txt`):

```
cafe-d072.md
"caf\303\251-d072.md"
```

ASCII sibling usable; café token not a usable `[ -f ]` path
(R2-C-unquoted PASS). ASCII-only plant blocked (R2-C-payload PASS).
Café-only plant: vendor-honesty printed mechanical-conditions pass
(R2-vendor REQUIRED FAIL). Secrets `-z` still contains the raw café
bytes (R2-C-z PASS). R2-secrets is NOT_MEASURED and is **not claimed**
against secrets.

### What it reaches

Only `scripts/check-vendor-honesty.sh` `artifacts()`, therefore only
the D-008(2) label scan and the D-008(4) vendor-name scan, and only
for untracked non-ASCII names. Same `--gate` stage as V-6's vendor
half. Secrets default mode already uses `-z` at this parent; R2 is
not a secrets hole here.

### Severity: **Medium**

A demonstrated completeness miss on a production `--gate` scan, by
git's default `core.quotePath` quoting — not a hypothetical. Narrower
than V-6: secrets unaffected; ASCII siblings still scanned; only
non-ASCII untracked names drop. D-067 already named this limit on
D-008(2)/(4). That naming matches Medium as a separate hole. It does
not pull V-6 down.

D-072's pin (`-c core.quotePath=false` at the same call sites) is the
same repair that addresses V-6. This is the sibling hole that pin
closes, scored on its own reach, not as a second High.

### What would change it

- **Up to High** if `-z` also dropped the café path from secrets
  (it did not) or if `artifacts()` were the only D-008(2)/(4) census
  and non-ASCII names were the routine artifact spelling. Neither is
  measured.
- **Down to Low** if `artifacts()` were not a `--gate` stage. It is.

### What this is not claiming

- That secrets missed the café file. `-z` kept the raw path.
- That tracked non-ASCII names drop. The drop is the unquoted
  `--others` listing plus `[ -f "$f" ]`.
- That D-067 is lifted.

---

## Boundary

- **D-055** is not scored. High is the class that criterion names for
  unresolved confirmed defects. Whether that condition is met is
  John's, at a facilitated session.
- **D-067** is not rewritten. R2 and V-6 stay named completeness
  limits on D-008(2)/(4) until John rules.
- **D-016** stands. No publication, rename, or push.
- No follow-on plan. No gate signature, reopen, or annotation.
- Five D-008 comprehension questions unseen.
- Working tree at adjudication, before this file: `M README.md`,
  `?? .serena/`, `?? assets/`. Stash empty. Those paths are not part
  of this commit.
