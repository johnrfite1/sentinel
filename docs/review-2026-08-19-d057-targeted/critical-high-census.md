# Critical / High census — D-055 exit record (D-073)

**This file is the census of record for D-073, not prepared material.** John ruled
D-055(a) MET on 2026-08-24 at freeze `8c74537f9d85f97b1d0133fd6869e3d79115c8ef`.
Assembling a clause is no longer pending: each row carries the clause he applied.

Independent residual scores for V-1–V-5, V-7–V-10 and R-A–R-F live in
`docs/review-2026-08-19-d057-targeted/batch-cards/D062-containment-tests/RESIDUAL-SEVERITY.md`.
That adjudicator was not the D-062 verifier and did not implement a repair. V-6, R5,
and R2 were scored on the D-071/D-072 card (`SEVERITY.md`), not rescored there.

D-055(a): a confirmed High ceases to block only through **verified repair**, or
through **John's explicit acceptance as a documented product boundary**.

| ID | Severity | Clause applied (D-073) | Record |
|---|---|---|---|
| `R1-F1` | Critical | Verified repair — A-078 independent HOLD | Certification-gate corruption. John ruled REPAIR (D-057(3)). A-077 third design. A-078: the verifier who had broken the two prior designs could not break this one. Not reopened. |
| `R1` | High | Verified repair — F61ECCA independent HOLD | First severity High (`INDEPENDENT-REVIEW.md`). Exploit control live; freeze blocked rename and typechange destinations. Not acceptance as a product boundary. |
| `R5` | High | Verified repair — D-071, card HOLD | Pre-repair High (`SEVERITY.md`). Option C. Independent HOLD on the D-071/D-072 card (`VERIFICATION.md`). |
| `V-6` | High | Verified repair — D-072, card HOLD | Pre-repair High (`SEVERITY.md`). Pin at enumerating call sites. Independent HOLD on the card. The D-008(2)/(4) completeness limit named at D-067 is HISTORICAL as of D-073. |
| `V-1` | High | Verified repair — A-098's behavioural guard, independent HOLD | The defect was that nothing observed the unset-before-resolve ordering. A-098 observes it (`scripts/check-v1-index-ordering.sh`); independent HOLD in review-only commit `8d8820c03043844b3281d35d81578890eee1ecdf`. Reversing the ordering still reopens the hole; the guard is required to fail. |
| `R-C` | High | Verified repair — D-072's pin, coverage made explicit | See **R-C coverage** below. Not assumed from V-6. |
| `V-3` | UNSCORED | John's **explicit acceptance** as a documented product boundary | See **V-3** below. Not probed. Not repaired. Not scored. |

No other item from the Session-Five 3a set scored Critical or High.

## R-C coverage — measured, not assumed

R-C as recorded (A2 `VERIFICATION-2.md`): `GIT_CONFIG_COUNT` + `core.excludesFile`
hides an untracked credential from **default-mode** `scripts/check-secrets.sh`,
which then prints `secret guard: clean`. `--staged` / commit-time is a different
path.

**The D-072 HOLD was not scoped only to V-6's vendor consumer.** The frozen card
boundary names `scripts/check-secrets.sh` default mode (untracked credential
census) as **in**. REQUIRED row `V6-COUNT-secrets` is that exact residual: COUNT
triple setting `core.excludesFile`, consumer `check-secrets.sh` default.
`V6-GLOBAL-secrets`, `V6-SYSTEM-secrets`, `V6-HOME-secrets`, and `V6-XDG-secrets`
are the same consumer under the other four live vectors. Independent verification
scored those rows **PASS** at `bdacace71e47c55301100d27341e67fc422fbcde`
(`VERIFICATION.md` §2). `V6-NOSYSTEM-secrets` was **NOT_MEASURED** (control did
not hide). `R2-secrets` was **NOT_MEASURED** (secrets already uses `-z`).

That is the same pin at the same call site R-C names. The live enumerating call
is `scripts/check-secrets.sh` line 281:

```
git -c core.excludesFile= -c core.quotePath=false ls-files --others --exclude-standard -z
```

**Independently remeasured** in a detached worktree at `8c74537` (synthesised
`API_KEY=` plant; worktree removed; main-tree porcelain unchanged):

| Vector | Unpinned `ls-files --others --exclude-standard` | Pinned `-c core.excludesFile= -c core.quotePath=false` | Production `check-secrets.sh` default |
|---|---|---|---|
| none (baseline) | plant listed | plant listed | BLOCKED |
| COUNT | hides | sees | BLOCKED |
| GLOBAL | hides | sees | BLOCKED |
| SYSTEM | hides | sees | BLOCKED |
| HOME | hides | sees | BLOCKED |
| XDG | hides | sees | BLOCKED |

All five injection vectors were live (unpinned hid). The pin restored listing.
The production script blocked the plant under every vector and never printed
`secret guard: clean` over it. R-C is therefore closed by the D-072 HOLD's own
secrets rows, confirmed at this freeze on the identical call site, not by
treating V-6 as a synonym.

## V-3 — accepted as a documented boundary, pointing at the source declaration

The adjudicator left V-3 **UNSCORED**: validate/scan windows exist twice; scoring
without a timing probe would be a guess (`RESIDUAL-SEVERITY.md`). John accepted
that as a documented product boundary **because the product already states it**,
not because nobody assessed it.

Source declaration, `scripts/check-secrets.sh` lines 148–152:

> WHAT THIS PROTECTS AGAINST, AND WHAT IT DOES NOT: accidental and environmental
> redirection — an inherited or mistaken GIT_INDEX_FILE, a stale value, a path
> pointing at another repository. It is NOT a defence against a hostile process
> running as this same user, which can replace git's temporary index between
> validation and scan, and can equally well edit this file. Stated here rather
> than left for a reviewer to infer.

The hook states the same bound (`.githooks/pre-commit` lines 61–64). Accepting
V-3 is accepting that sentence. It is not a shrug, not a probe, and not a
repair. D-055(a) requires accepted limits reflected where the claims they bound
are made; this census and the D-055 exit record so reflect it.

## What this file does not do

It does not unlock publication, rename, a gate signature, or a follow-on plan.
A MET D-055 is a precondition under D-048, never a trigger. D-016 still blocks
publication and the rename. Gate 5 is not recertified. Deferred items named at
D-073 stay deferred.
