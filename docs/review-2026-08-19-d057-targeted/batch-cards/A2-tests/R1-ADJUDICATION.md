# R1 — ADJUDICATION: staged rename and typechange fall out of the staged enumeration

**Adjudicator:** the independent test author for Batch A1 attempt two. No production repair was
made, and none is authorised by this document.

**Authority and its limit.** D-061(2) admits R1 into attempt two **only if** an independent test
author first reproduces and classifies it CONFIRMED inside `scripts/check-secrets.sh`'s existing
staged-enumeration boundary. This file supplies that classification and the evidence under it.
**Whether R1 is then worked is John's call, not this document's** — the classification is the
precondition, not the authorisation.

**Boundary.** The defect sits at `scripts/check-secrets.sh:138`, the `git diff --cached` file
enumeration. That symbol is named explicitly in batch card A1's symbol boundary, so this is
inside A1's declared scope and not a widening of it.

Paths are repository-relative. `<subject>` stands for an isolated clone of the commit under
test, created in this session's scratch area; every fixture below was built there and nothing
was written to the repository under test.

---

## VERDICT: **CONFIRMED**

A staged rename and a staged typechange are both **enumerated by nothing**, so the destination's
content is never read, `--staged` mode prints its clean line, exits 0, and the pre-commit hook
admits the commit. The credential reaches HEAD. Reproduced from scratch, with four controls that
behave oppositely and one control that proves the fixture is the one a prior probe failed to
build.

---

## 1. THE MECHANISM, IN ONE LINE

`check-secrets.sh:138` enumerates staged content with

```
git diff --cached -z --name-only --diff-filter=ACM
```

`--diff-filter=ACM` is an **allow-list of status letters**: Added, Copied, Modified. Rename (`R`)
and typechange (`T`) are outside it, so a record carrying either status contributes no pathname
at all — not the source and **not the destination**. An unrecognised or unlisted status therefore
fails *toward being skipped*, which is the opposite of the fail-closed half of the A1 invariant.

The comment above that line is correct about deletions and silent about the rest: it explains
that `D` is excluded so a genuine staged deletion cannot become a false failure (D-059(3)). `R`
and `T` are excluded by the same construction and for no stated reason.

---

## 2. REPRODUCTION — RENAME

**Fixture.** A 400-line ordinary document committed as a tracked regular file, then renamed with
`git mv`, then one credential-shaped line appended to the **destination**, then staged. The
planted credential is an obviously fake value — one hex character repeated 64 times, assembled at
run time — bound to a key-shaped identifier, which is the shape `check-secrets.sh`'s own rule 3b
is written to catch.

**Sizing is load-bearing and is the reason the earlier probe missed this.** `PROBES.md` D2
reported a negative result — "rename detection is not applied here, so the new path surfaces as
`A`". That does not reproduce. D2's fixture was small enough that appending the credential
dropped similarity below git's rename threshold, so git scored the change as `D`+`A`, the `A` was
enumerated, and the guard blocked it. At a realistic size the pair scores a rename and is
excluded. **The negative result was a fixture artefact, not a property of the guard**, and a
harness that does not assert the record actually scored `R` is measuring the same nothing.

**Measured.**

```
git diff --cached --raw
  :100644 100644 <src-oid> <dst-oid> R099   a2c/doc.md   a2c/doc-renamed.md

git diff --cached --name-only --diff-filter=ACM
  (empty)

./scripts/check-secrets.sh --staged
  secret guard: clean            exit 0

git commit                       exit 0, commit created
  the destination's credential-shaped line is present in HEAD
```

The commit path is the one that matters: `.githooks/pre-commit` execs
`check-secrets.sh --staged`, so the guard's clean line **is** the hook's verdict.

---

## 3. REPRODUCTION — TYPECHANGE

**Fixture.** A tracked symlink, committed, then removed and replaced by a regular file carrying
the same shape of planted credential, then staged.

```
git diff --cached --raw
  :120000 100644 <src-oid> <dst-oid> T     a2c/link.md

git diff --cached --name-only --diff-filter=ACM
  (empty)

./scripts/check-secrets.sh --staged
  secret guard: clean            exit 0
```

Identical shape, different status letter. This is why the requirement below is written against
**the raw status and the new mode** rather than against a longer allow-list of letters: a list of
letters is satisfiable by the next letter nobody listed.

---

## 4. THE CONTROLS — each behaves oppositely, or the reproduction proves nothing

| control | result | what it forecloses |
|---|---|---|
| ordinary staged **ADD** carrying the identical bytes | **BLOCKED**, exit 1 | the credential pattern is not the variable; the **status letter** is |
| genuine staged **DELETION** | accepted, exit 0 | D-059(3)'s protected control is intact and is not what is being reported here |
| staged deletion of a file that **did** carry a credential | accepted, exit 0 | removing content is not a finding, and R1 is not an argument for making it one |
| newly staged **GITLINK** (new mode `160000`) | accepted, exit 0 | a submodule pointer is not a regular file; skipping it is legitimate |
| staged **COPY** (status `C`) | **BLOCKED**, exit 1 | `C` is *inside* `ACM`; copies are already scanned |
| the rename in **default** mode | **BLOCKED**, exit 1 | the working-tree copy is present, so default mode reads it — the exposure is the `--staged` path and therefore the hook |
| the rename record actually scores **R** | asserted in the harness | the exact failure that produced the earlier false negative |

**One correction to the framing this adjudication was handed.** The brief names
"copy/rename/modify/add/typechange" as the records to parse. Only **`R` and `T`** are excluded
today. `A`, `C` and `M` are all inside `ACM` and are scanned — the staged copy control above
demonstrates it. Copy is therefore a **regression risk for the repair**, not a live defect, and
the harness carries it as a control rather than as a required failure.

---

## 5. WHAT A REPAIR WOULD HAVE TO SATISFY

These are the assertions `a2-env-and-supervisor.sh` group C carries. They are stated as
behaviour, not as an implementation:

1. The rename **destination** is scanned; a credential there is blocked and named.
2. A rename destination whose **new mode** is `100755` is scanned. Mode is read from the record,
   not guessed from the path.
3. A staged typechange whose destination is a regular file is scanned.
4. Pure staged **deletions** remain accepted — no false failure (D-059(3)).
5. A newly staged **gitlink** may be treated as a gitlink; a regular-file destination may **not**
   be skipped.
6. Copy, rename, modify, add and typechange records are enumerated **by their raw status and new
   mode**, from `git diff --cached --raw -z`.
7. The parse does **not** assume one pathname per record: rename and copy records carry a
   **source and a destination**, so one staged rename yields three NUL-delimited fields, not two.

The suggested direction the verifier recorded — enumerate with `--diff-filter=d` (exclude
deletions only) so an unrecognised status fails *toward being scanned* — satisfies (1)–(5) but
not (6)–(7) on its own, because `--name-only` still hands back a single pathname per record and
gives the parser no mode. Which route to take is an engineering choice inside the repair; **the
scope decision to take it at all is John's** under D-061(2).

---

## 6. WHAT THIS ADJUDICATION DOES NOT ESTABLISH

- **One platform, one git.** git 2.50.1, bash 3.2, `core.quotePath` and `diff.renames` at their
  defaults on this workstation. Rename detection is configuration-sensitive: a repository
  configured with rename detection off surfaces the same change as `D`+`A`, and the `A` is
  scanned. The default is what the project runs under and what the hook runs under.
- **No claim about severity or priority.** This says the defect exists and reproduces. Whether it
  is worth attempt two's budget is not a test author's call.
- **Nothing about the other residuals.** `R2`, `R3` and `R5` are DEFERRED by D-061(2) and were
  not probed here.
- **No production change was made or proposed in code.** The reproduction ran against an isolated
  clone; the repository under test was read and never written.
