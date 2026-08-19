# CRITIQUE — Reviewer 3 on this brief, this scope, and this apparatus

The common brief invites this explicitly: *"You are invited to report that your own brief is
wrong."* Four items, in descending order of how much they cost.

---

## C-1 — MY BRIEF CARRIES A FIGURE A PREVIOUS ROUND ALREADY MEASURED FALSE, and pointed me at the surface with it in hand

`briefs/r3.md` says:

> **The corpus class-coverage ratchet.** 14 of 20 classes exercise the class they name; **two
> classes are credited only on UNRESOLVED outcomes.** Is the ratchet honest about what it carries?

Round six lens 5 reported, and `docs/review-2026-08-18-round-six/ADJUDICATED-ROUND-SIX.md:378`
records at the frozen commit:

> **`G-3` is worse than recorded** (lens 5) — **three** classes are credited only by UNRESOLVED,
> **not two** … Strict reading: **11 of 20**, not 14 of 20.

I measured it myself before finding either statement, and got three (R3-F1). So the scope
document written *after* round six, by the loop, to fix this review's targets, restates the
number round six refuted — and it restates it as a hint about where to look, which is the worst
place for a wrong number because it sets the reviewer's prior. Had I been less stubborn about
measuring first, "two, as briefed" would have read as a clean confirmation.

**This is the same defect the review exists to find, committed by the review's own instrument.**
D-055's T3 makes the pre-fixed scope the guarantee of the round's independence; nothing checks
the scope document's own claims, and `scripts/check-review-scope.sh` audits only file *coverage*,
never content.

**Cheap fix, offered:** the brief should cite the round-six adjudication for any figure it
repeats, or state figures as questions ("how many classes are credited only on UNRESOLVED?")
rather than as facts. A brief that hands a reviewer a number is handing them an answer.

---

## C-2 — The brief's "two accepted boundaries" framing quietly narrows what I was allowed to attack

`briefs/r3.md` opens with *"Two accepted boundaries you must NOT report as new defects — but MAY
report as understated."* Both are stated as settled with their certifications
(D-053(a)/D-054(a), A-073/D-054(b)). That is correct as a matter of what John ruled, and I
respected it.

But the framing puts the two most heavily-documented items on my surface **behind a presumption
of soundness**, and they are the two a reviewer would naturally start on. I spent a
disproportionate share of the session establishing that both are *not* understated (NULL-RESULTS
N-4) — which is a real result and worth having, but it is the result the framing predicts, and
the same hours spent on the un-briefed parts of `contracts/src` and `ts/src/corpus` produced
three of my four findings.

**The observable pattern:** every one of my findings is on a surface the brief did NOT name.
`WITHHELD` (R3-F2), `leakage.ts`'s allowlist depth (R3-F3), and the three unread payload fields
(R3-F4) are none of them in the brief's "Worth attacking" list. The list is a good list; it is
also, at this point in the loop, a list of places that have been looked at repeatedly.

---

## C-3 — The apparatus makes one class of probe undetectably wrong, and nothing warns about it

Six TypeScript test files read `contracts/out` (`decode.chain`, `cases.e2e`, `differential`,
`harness`, `simulate`, `propose.e2e`). A reviewer with both a Foundry mutation sweep and a
TypeScript sweep to run — which is precisely what this surface demands — will be tempted to
parallelise them, and `npm test` will then measure the TypeScript suite against a MUTATED vault
artifact sitting in `contracts/out`. The result is green or red for reasons attributable to
neither probe, and **it looks exactly like a normal result.**

Nothing in the common brief, `r3.md`, `session-state.md` §1 or the scope manifest mentions it.
The brief does warn about the symlinked toolchain and about `git status` exiting 128 — both
real — so the omission is not an oversight of category, just of this instance.

I serialised (DEAD-PROBES DP-2). A reviewer under time pressure would not have.

**Cheap fix:** the corpus/artifact coupling belongs in the common brief's hazards list, or
`npm test` should assert `contracts/out` is clean of local modification.

---

## C-4 — "Prove the work fails" and "revert every mutation" are in tension on the one surface where the deep gate lives

The corpus stage is the only place where the interesting question — *can an engine verdict move
while both committed artifacts stay byte-identical?* — is answerable, and answering it means
running `npm --prefix ts run corpus`, which **rewrites `fixtures/corpus/for-labelling/` and
`fixtures/corpus/results/` in place** unless `SENTINEL_CORPUS_OUT` is set. The environment
variable is documented only in a comment inside `run.ts:75` and in the gate script; neither brief
mentions it, and the naive command is the one in `package.json`.

A reviewer who runs the documented `npm run corpus` command destroys 100 committed artifacts —
including the labeller views the labels of record attest to, which `run.ts:491-500` says
explicitly must never have a window in which they do not exist. The staging-directory fix
protects against a mid-run crash; it does not protect against a reviewer running the tool as
documented.

**This should be in the brief**, in the same paragraph as the `git checkout -- .` warning, which
is the same species of hazard.

---

## C-5 — A smaller one: the deliverables contract has no slot for a null that IS a finding

`NULL-RESULTS.md` is specified as "what you probed and found SOUND", and `REPORT.md` as
findings. But my strongest single piece of evidence for R3-F2 is a **null match**
(`grep -rn 'WITHHELD' ts/test/` → nothing), and my strongest for R3-F4 is a null match over
`docs/`. Under a literal reading those belong in NULL-RESULTS, where they would read as
reassurance. I put them in DEAD-PROBES DP-4 with a note, and in the findings themselves.
**A grep that matches nothing is either a null result or a finding depending entirely on what
you expected to match, and the contract does not distinguish the two.**
