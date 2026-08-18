# Round five — the full-breadth adversarial review, 2026-08-17

Eight independent reviewers, each on its own detached `git worktree` at frozen commit
**`8234aba`**, each briefed to prove the work fails, each invited to report that its own brief
was wrong, each required to return a provenance attestation and a statement of what it did NOT
cover. Commissioned by **A-057** (which declares the reading BEFORE any result), reported by
**A-058**, remediated in part by **A-059** and **A-061**.

**These are the reports as returned. They are not adjudicated and several are wrong.**
`docs/v1-1-register.md` §13 is the adjudicated list: which findings I reproduced myself, which
are unconfirmed leads, and which have been fixed. **Where a report and the register disagree,
the register is the later word** — but the report is what the reviewer actually said, which is
why it is here unedited.

## The files

| Lens | Brief | Findings |
|---|---|---|
| `lens-A-break-an-instrument` | THIN — no surfaces named. Find something that reports a property and make it pass while that property is violated. | 3 |
| `lens-B-catch-a-false-statement` | THIN — no surfaces named. Find a claim stronger than its evidence and prove it false by execution. | 7 |
| `lens-C-free` | THIN — no target, no method. | 5 |
| `lens-D-evaluator-and-decoders` | DIRECTED — mutation-sweep `ts/src/evaluate/**`, `ts/src/decode/**`. | 12 |
| `lens-E-isolated-signer` | DIRECTED — obtain a signed ALLOW the design forbids. | 6 |
| `lens-F-vault-and-containment` | DIRECTED — what one valid ALLOW receipt actually permits. | 5 |
| `lens-G-corpus-labels-figures` | DIRECTED — do the published figures reproduce; can the apparatus be laundered. | 5 |
| `lens-H-d010-verifier` | DIRECTED — find a LIVE certification defect needing no mutation. | 8 |

## What to read them for

Each report carries four things beyond its findings, and the last three are the ones a summary
would lose:

- **`reproduction`** on every finding — the commands and the observed output, not a description.
- **`brief_critique`** — what the reviewer thought was wrong with the brief it was given. **Twice
  in the two preceding rounds the brief was itself the defect**, so this is a first-class output.
- **`coverage_statement`** — what the lens looked at and what it left untouched. A null from a
  lens that ran out of budget is a different fact from a null from a lens that swept its surface,
  and these keep the two apart.
- **`provenance_attestation`** — what was actually read and run, what entered the reviewer's
  context from outside its brief, and anything claimed without executing. Eight for eight of this
  project's labellers produced a first-order finding through this instrument; it is the reason it
  is required here too.

## What this round could not reach

Recorded in register §13.1, and it bears on how a null in any `coverage_statement` should be
read: **no reviewer could run the deep gate profile** — the corpus runner's unix socket path
exceeds macOS's 104-byte limit from the worktree locations — so all eight baselines were the
fast profile. The deep profile was run only in the live tree, by me, before the round started.
Two further limits: the reviewers shared one scratchpad directory and four of them clobbered
each other's baseline logs, and no live model was called, so the Gate 7 canary and every
model-dependent arm went unexercised.

## Provenance of these files

Mechanically split from the workflow's own returned values — one JSON object per lens, with
nothing removed. **One edit was applied and it is the only one: machine-specific absolute paths
were rewritten** (`<scratchpad>`, `<repo>`, `$HOME`). Not for tidiness — `check-secrets.sh`
blocked all eight files under house rule 6, which is the guard behaving correctly, and the
alternative was an exemption. So these are the reviewers' words with their paths generalised,
not byte-identical returns. **No credential-shaped content was flagged in any report**, so
nothing else was touched. The reviewers' probe artifacts (hostile bundles, mutation
sweeps, a vault drain test) are deliberately NOT committed: they carry key-shaped constants,
and adding a secret-guard exemption to accommodate them is the exact shape of hole
`docs/v1-1-register.md` §8.2 keeps recording.
