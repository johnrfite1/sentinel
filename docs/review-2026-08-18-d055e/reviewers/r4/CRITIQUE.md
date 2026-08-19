# R4 — CRITIQUE of the brief, the scope and the apparatus

The common brief invites this explicitly, and the r4 brief calls its own seat "a recorded weak
mitigation". Taking both at their word.

## 1. COMMON-BRIEF rule 5 states the baseline wrongly, and I found it by tripping over it

> *"`docs/gate-s2-evidence.md` §11.0 is the **five** findings John ACCEPTED as limits."*

It is **six** (R4-F1). The brief inherited a miscount from the signed pack rather than checking
it. This is not a nitpick about the brief: rule 5 is the rule that decides whether a reviewer's
work counts as a finding or as a re-report, so an inaccurate baseline mis-sorts findings in both
directions — it invites a reviewer to re-report `G-3` as new, and it invites an adjudicator to
dismiss a genuine `G-3`-adjacent finding as recorded.

**A brief that hands reviewers a derived number should hand them the command that derives it
instead.** Rule 5 could have said "run this and read the result", exactly as the scope manifest
says of its own partition — *"Do not trust that line — run `./scripts/check-review-scope.sh`."*
The manifest got this right about itself and the brief did not get it right about §11.0.

## 2. "Prove the work fails" is the right instruction and it is in tension with the deliverables

`NULL-RESULTS.md` is required, and correctly so. But a reviewer told to prove failure, and
measured by findings, has no incentive to spend an hour establishing that something is **sound**
— which is what I did for the round-six archive, and it is arguably the most useful hour of my
review, because that archive is the evidentiary base of the exit backtest and nobody had checked
it since the session that wrote it. The brief should say that **a hard null on a load-bearing
claim is a deliverable of equal standing**, not a residue. As written, N1 reads as what I failed
to find rather than as what I established.

## 3. The free lens is briefed as a mitigation for scope-ceiling risk, and is not resourced as one

R4 is told it is the answer to "this project's defects have repeatedly been where nobody was
looking", and is then given the same budget as a reviewer with a 46-file surface. Ranging over
371 files means sampling, and sampling means my null results are much weaker than R1–R3's: when
R2 says a surface is sound it has read it, and when I say a surface is sound I have probed it.
**My COVERAGE.md "not run" list is longer than my "ran" list and that is structural, not lazy.**
If the free lens is genuinely the mitigation for the ceiling, it needs either more budget or an
explicit instruction to go deep on two or three self-chosen targets and say so — which is what I
did, unprompted, and which the brief should make the stated method rather than leaving each free
lens to invent it.

## 4. The apparatus is materially better than round six's and one hazard is under-stated

Working correctly: separate worktrees, separate persistent evidence directories, the pre-declared
deliverables contract, the pristine-copy-and-`cmp` revert rule, and the `pgrep -f sentinel-gate`
correction. The revert warning about `git checkout -- .` destroying symlinks is precise and I
followed it; the `git status` exit-128 warning is accurate.

**Under-stated: the harness shell is `zsh`, and every script under review is `bash`.** Three of
my four dead probes came from this single mismatch, and one of them — `for c in $codes` — printed
`OUTSIDE ONLY : 0`, which is a clean-looking pass produced by a loop that executed once. It
happened to agree with the truth. **That is the brief's own "five such probes looked exactly like
passes" hazard, sitting in the review harness rather than in the repository**, and it is not
mentioned in the brief. It should be, with the mitigation: *run any bash-idiom probe as
`bash -c '…'`.*

## 5. "Revert every mutation and verify with `cmp` against a pristine copy" needs a scope

The rule does not say **what** to copy. A worktree-wide copy is impractical (`ts/node_modules` and
`contracts/lib` are symlinks that must not be duplicated, and `contracts/out` is build output). I
made my own decision — snapshot the eight source directories plus six top-level files, 364 files
— and stated it in ATTESTATION.md. Two reviewers making different decisions here produce
non-comparable revert evidence. The brief should specify the set.

## 6. The scope manifest's strongest argument is one this round does not apply to its own record

The manifest is right that "a table in a document IS an assertion: it claims completeness and
nothing checks it", and it mechanised the file partition for exactly that reason. **Three of my
four findings are that same defect in tables the manifest did not mechanise** — §11.0's ledger
(F1), the preservation fidelity table (F2), and session-state §3 (F4). The lesson generalises
further than it was applied. Both a count of accepted limits and a suite-count line are derivable
in one command; neither is derived.

## 7. On the exit criterion itself, offered as an observation and not a recommendation

Three of my four findings are false or incomplete claims in documents, none of them in code, and
all four are of the class C1 condition 4 names ("zero known false or unsupported signed/certified
claims"). Two sit in text that is **signed** (`gate-s2-evidence.md` §11.0) or **canonical**
(`decisions.md` A-076, `session-state.md` §3). If C1 is adopted as written, a bounded review that
finds only defects of this class still blocks exit — which I read as the rule working, not
failing, but it does mean the packet's own §4 attack 5 ("unknown false claims are the residual")
is doing more work than its phrasing suggests. **This is John's call and nothing here is a
recommendation about it.**
