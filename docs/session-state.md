# Sentinel — Session State

Rewritten at the end of each working session. **This file, not the conversation, is the
memory.** If it disagrees with anything an agent remembers, this file wins.

Last updated: **2026-08-18**. Branch `step-3/isolated-signer`, **pushed and verified against
the remote** (`78ac9cb` at the time of writing; the commit that updates this file necessarily
comes after, so expect the pointer to trail by one doc-only commit and check `git log` rather
than treating a mismatch as a finding). Working tree clean. **This pointer names the last commit this file DESCRIBES, and the commit that updates
it necessarily comes after — so expect it to trail by one doc-only commit, and check
`git log` rather than treating a mismatch as a finding.** It read `f3308ea` while HEAD was two
commits further on, which is the same stale-pointer defect A-045 and A-046 spent the session
correcting elsewhere, sitting in the file that opens by declaring itself the memory. The repository is PRIVATE — `check-rename-gate.sh` checks this on every gate run — and
D-016 still blocks all publication. **Pushing to the private remote is backup, not publication;
do not read the push as any relaxation of D-016.**

**READING ORDER FOR A FRESH INSTANCE, AND YOUR JOB IS ROUND SIX.** Read §1 first — it tells you
what to run and hands you the brief. Then §0 for how this project fails, which is what a reviewer
brief has to encode. Then, in `docs/decisions.md`: **D-047 and D-048 FIRST — they bind you and you
may not amend them** — then **D-050 and D-051**, which are John's rulings that define round six
and set what was fixed before it. `A-057` through `A-069` are the round-five arc and its
remediation; you do not need all of them to start, but `A-058` (what round five found) and
`A-068`/`A-069` (what was fixed, and the two forks that were NOT) are the ones that change what
you brief.

**`docs/round-six-brief.md` IS THE BRIEF. It is written and ratified; you are not designing it.**
`docs/v1-1-register.md` is the list of known outstanding work, with each item's blocker stated.
`docs/gate-s2-evidence.md` §11 is what is NOT in evidence — read it before repeating any claim
about what this project has proven.

**The suite counts in §3 are verified as of this commit. Verify them again before quoting them:
that line was wrong for most of 2026-08-16.**

---

## 0. If you read nothing else, read this

**Gate S1 is SIGNED — PASS, John, 2026-07-28. GATE S2 IS SIGNED — PASS, John, 2026-08-16
(D-041).** Both by John alone at facilitated sessions, never by an agent (D-002, non-delegable).
**D-002's two mid-build gates are now both behind the project.**

**What S2 does NOT authorise, stated first because a signed gate is the moment scope creeps.**
D-016 still blocks all publication and the repository is PRIVATE. Gate 8 (five-minute
comprehension) is PRE-PUBLICATION under D-032 — it needs the dashboard D-009 deferred and John's
five held questions, which the build loop must never see. Certification of public claims is
still autonomy NONE. **S2 was signed on the state in `docs/gate-s2-evidence.md` §11 INCLUDING
its limits, not despite them** — 14 of 20 classes exercising the class they name, and no live
agent in CI. D-041 carries an annotation naming what became known after it was signed.

**The steps 1–3 review S2 was signed WITHOUT has since been run (D-044(b)).** It found A-043:
**a CRITICAL, exploitable bypass — a signed ALLOW obtainable for calldata nobody decoded,
reproduced twice onchain.** Fixed, with regression tests. Read A-043 and A-044 before trusting
anything about the signer. **`gate-s2-evidence.md` §11 is NOT empty** — this file once claimed it
was, twenty-two lines after telling a fresh instance to read it (`B-7`). It carries the pack's
stated limits plus, as of D-051(b), **§11.0: ten confirmed findings John has ACCEPTED as limits
rather than fixed.**

**THE PATTERN, now the operating assumption rather than an observation. THIS IS THE PARAGRAPH A
REVIEWER BRIEF HAS TO ENCODE.** The defects are *honesty* defects — a claim stronger than its
evidence — and **the build loop does not find them.** Across 2026-08-15 to 2026-08-18, roughly
one hundred and forty findings came from adversarial reviewers, independent adjudicators,
independent labellers, the mutation harness and an independent reimplementation. The build loop
found essentially none of its own. Specifically and repeatedly:

- **An instrument can exist and point at the wrong thing.** Guards, tests and mutations have
  shipped aimed at something other than what they name — five or more times now.
- **A repair can generalise the DEMONSTRATION rather than the ARGUMENT.** A-028 fixed the branch
  its reviewer exploited and left the identical hole two lines down. A-043 is the cost.
- **A comment can describe a vulnerability and file it as an inconvenience.** A-028's test file
  named the exact bypass state in prose and routed around it.
- **A regression test can pass against the defect it names** (A-044).
- **A published number can be true once.** This file's own headline suite counts were stale for
  most of a day; its guard count has been wrong three times; and a suite figure was counted twice
  across two consecutive decision entries (`B-5`).
- **A FALSIFICATION PROBE CAN BE DEAD, AND ITS SILENCE READS EXACTLY LIKE A PASS.** Five were, on
  2026-08-17/18 alone: a mutation of a value already at the maximum so no percentile moved; a
  Solidity probe that did not compile and printed no PASS/FAIL line; two corpus runs that died on
  a missing build artifact long before reaching the code under test; and a grep pattern that
  matched nothing. **Ask what your probe MOVED before believing what its result implies.**
- **A CHECK CAN BE CAUGHT BY THE WRONG CHECK.** A tamper that fails on the canonical bytes tells
  you nothing about the check you were testing. Make the bundle wholly self-consistent — re-hash,
  re-bind, RE-SIGN — so only the check under test can reject it.

**None of that is a reason to distrust the work; it is the reason to keep pointing independent
eyes at it.** Everything above was found, fixed or recorded — and found by the process working.

**WHERE THE PROJECT STANDS, 2026-08-18.** Round five (51 findings, 2 CRITICAL) is fully
adjudicated and remediated: three live security defects fixed, nine MEDIUMs fixed, ten accepted
as documented limits, two design forks with John. §7.1's containment claim — wrong twice — is
corrected, measured, asserted by a test, and **certified by John** (D-051(a)). **The next move is
round six, and §1 tells you how to run it.**

**John has delegated design forks to the build loop.** Two things stay outside that
permanently, and were restated to him: **gate signing** (D-002) and **certification of public
claims** — the §2 capability table, README, resume language (HANDOFF verification partition,
autonomy *none*).

---

## 1. What the next instance should do

### YOUR JOB IS ROUND SIX. John triggers it; if he has, run it. Read D-047, D-048, D-050 and D-051 before you do.

**RUN IT FROM `docs/round-six-brief.md`.** That brief is ratified, not a draft: D-050(1) adopted
A-060's definition of "full breadth" as **nine named surfaces**, and a round is full breadth when
every one is covered by a reviewer that ran its own baseline and returned a coverage statement.
**You are not designing the round. You are running the one that is already defined** — and the
reason it is defined in advance is that the last three rounds each had a defective brief, twice
in ways that cost coverage.

**HOW TO RUN IT, mechanically.**

1. **Freeze a commit.** `git worktree add <scratch>/w<N> <HEAD> --detach` per reviewer, then
   symlink `ts/node_modules` and both `contracts/lib/*` submodule directories into each. Nine
   worktrees, nine reviewers.
   - **`ln -sfn <target> <dir>` NESTS the link inside an existing directory instead of replacing
     it**, and `git worktree add` creates the submodule mount points, so the naive command
     silently produces `contracts/lib/forge-std/forge-std` and `forge build` fails with
     `Source "lib/forge-std/src/Test.sol" not found`. This broke most of round six's trees.
     **Remove the directory first, then link.** Verify with `ls -l contracts/lib` — you want two
     symlinks, not two directories.
   - **The remapping hazard behind that one is FIXED and no longer a reason to avoid symlinks**
     (A-070): `contracts/foundry.toml` pins all five remappings with
     `auto_detect_remappings = false`, so the compiled bytecode no longer depends on how the
     libraries are mounted. Before that, symlinked libs resolved four remappings instead of five
     and every one of the 50 committed view digests mismatched — which is why round six could not
     run the deep profile it was required to run.
   - **`git status` with no pathspec EXITS 128 in a symlinked worktree** ("expected submodule path
     … not to be a symbolic link"), which silently truncates `&&` chains and `set -e` scripts. Use
     `git diff HEAD --stat` plus recorded hashes to verify a revert.
   - **`git checkout -- .` DESTROYS the symlinks** and then reports a clean tree, and a cached
     `forge build` still exits 0 — a revert that verifies clean while the toolchain is gone. Tell
     reviewers to revert from a pre-mutation copy and `cmp`, not with git.
2. **Give each reviewer its own evidence directory.** This is one of A-060's two conditions and
   it exists because four of round five's eight lenses independently chose the same baseline
   filename and clobbered each other.
3. **At least one reviewer must run the DEEP profile.** The other condition. It is now possible —
   A-066 made the corpus socket path fall back to a private `mkdtemp` dir when the repo path
   would exceed macOS's 104-byte `sun_path` — but **verify it in a worktree before you claim the
   condition is met**, because it was ratified while unmeetable and nobody noticed for a day.
   A worktree also needs `forge build --root contracts` before the corpus will run at all.
4. **Brief each lens to prove the work fails**, invite it to report that its own brief is wrong,
   and require a provenance attestation and a coverage statement. Carry forward round five's
   warnings — they are in the brief.
5. **Tell reviewers that re-reporting a recorded item is not a new finding — but showing a
   recorded item is WORSE than recorded IS one.** `docs/v1-1-register.md` §13 is the list, and
   §11.0 of the S2 pack is the ten findings John ACCEPTED as limits.

**THEN STOP AT ADJUDICATION. D-051(c) is explicit: verify the findings, reproduce them yourself,
and bring John the adjudicated list WITHOUT acting on it.** Whether the round is clean is the
judgement D-047 reserves, and it must not be made by the hands that were editing the tree.

### What round six is measuring, and why its result finally means something

Round five ran against a tree with 44 known-open findings, so its result could not distinguish
"the artifact is sound" from "the reviewers found our own backlog". **That is no longer true.**
Of round five's 51 findings: **the three live security defects are fixed, the nine MEDIUMs are
fixed, ten are ACCEPTED as documented limits by John, and two are open design forks he holds.**
Twenty-one of twenty-four leads were confirmed by independent adjudicators before any of that
was decided, so the list was verified rather than assumed.

**So round six is the first round in this loop whose outcome means something in either
direction** — and that, not tidiness, is why the repairs came first.

### The one thing still open that is JOHN'S, not yours

**`E3` — anchor recency.** The signer will attest an ALLOW anchored to ANY historical block,
including one at which the vault had no code, and the vault executes it. Nothing bounds recency
here or downstream. **The fork is whether the receipt should bind to the signer's own
observation, and it changes what the product guarantees, so it is not an agent's to close.** The
comment at `attest.ts` states the limit rather than implying it away; do not "fix" it.

`E4`'s verifier half is built (A-069). Its signer half is deliberately NOT built — D-014 keeps
conformance out of the signer, and building it would weaken the independence that makes the
D-010 artifact worth having.

### What is NOT authorised, and none of it has changed

- **Pre-publication has not started** and D-048 makes a clean round a PRECONDITION, never a
  trigger — the programme still needs John's separate authorisation.
- **D-016 blocks all publication**; the repository is PRIVATE and the rename gate verifies it on
  every run. Pushing to the private remote is backup, not publication.
- **Never sign a gate** (D-002) and **never certify a public claim** — John certified §7.1
  himself at a walkthrough (D-051(a)); an agent may not, and no overnight authorisation changes
  that.
- **The five D-008 comprehension questions stay unseen.** Do not ask for them, guess them, or
  write substitutes.
- §14.8 ladder rung 2, the 14.3 attestation stretch, and the evidence dashboard remain declined
  (D-043, D-044).

### If you arrived with no instruction from John

Say so and stop. Round six is his to trigger, and `docs/v1-1-register.md` exists so that "there
is nothing to do" is checkable rather than a guess.

### The operating rules that bind whatever you do

1. **One agent session at a time on this tree** (D-037). Sub-agents inside one session are fine
   and are how every review here is run; two sessions with write authority are not.
2. **Adversarial review is the technique that works**, and its yield does not decay when the
   scope widens — round five went wider than any round before it and returned 51 findings, two
   CRITICAL.
3. **Verify before you rely on any number or status in these docs, including this file.** It has
   been wrong repeatedly — its own headline counts, its guard count three times, and a suite
   figure counted twice across two consecutive decision entries.
4. **Run every new regression test against the PRE-FIX code and confirm it fails**, and **check
   that your probe MOVED SOMETHING before believing what its silence implies.** Five probes
   across 2026-08-17/18 were dead on the first attempt — a mutation of a value already at the
   maximum, a Solidity probe that did not compile, two corpus runs that died before reaching the
   code under test, and a grep pattern that matched nothing. **Every one of them looked exactly
   like a passing check.**
5. **A fix must generalise the ARGUMENT, not the demonstration.** The trust-root repair's first
   draft closed the single-bundle path and left `--all` certifying the identical hostile tree;
   it was caught only by re-running the exploit through both invocation shapes.
6. **Never sign a gate; never certify a public claim.**

## 2. Authority

**Agents propose; John decides.** Routine engineering judgment is yours; John has delegated
design forks. Never sign a gate, never certify a public claim.

- **The five D-008 comprehension questions are held by John and must stay unseen.** Do not ask
  for them, guess them, or write substitutes. Gate 8 is PRE-PUBLICATION under D-032, not S2.
- **A worked pattern for decision sessions**, used for D-033…D-036: present ONE fork at a time
  with verified facts, real options, costs, and a recommendation; record the ruling immediately
  with the counter-argument and the condition that would reverse it. **When a reversal condition
  later fires, say so and hand the decision back** — A-034 did exactly that.

## 3. Where the build is

**75/75 Foundry · 481/481 TypeScript · 180/180 verifier · 78 tamper cases over 30 modes ·
50 corpus fixtures · 7 samples · gate green at the deep profile · workspace guards OK.**
*(A-059 moved 160→170 / 77→78 / 29→30; A-061 moved 405→407 TypeScript and 170→173 verifier;
A-063 moved 73→74 Foundry; A-064 moved 74→75 Foundry and 407→409 TypeScript;
A-067 moved 409→426 TypeScript and 173→176 verifier.
Every gate FLOOR was ratcheted in the SAME edit as the suite it bounds, which is the rule this
line exists to enforce and the rule it has broken three times.)*
*(Read `149/149` and omitted the tamper figures entirely until 2026-08-17 — stale for the third
time, in the file that opens by declaring itself the memory. The verifier moved 146 → 149 → 154 →
158 → 160 in two days and this line tracked none of it.)* *(This line read 66/66 and 70/70 for
most of 2026-08-16 while all three numbers moved underneath it — in the file that opens by
declaring itself the memory. Update it in the same edit that changes a suite, not later.)*

Run `./scripts/test.sh`; use `--gate` for evidence. Read the coverage boundary it prints — it is
ONE statement, not a log; rewrite the affected layer when a step lands, never append.

**All four counts above were re-measured 2026-08-16 (late session) and all four held.** The
verifier's 146 was measured by running it — which until that moment was the ONLY way it could be
measured, because **no profile of the gate ran the verifier and nothing in `scripts/` invoked
it** (A-045). Its numbers were quoted on this line beside Foundry's and TypeScript's as though a
green gate covered them; it did not, and a verifier regression could not have failed the gate.
It is now a stage in `scripts/test.sh`, in both profiles, and both of its arms were falsified
against the real script before that was claimed.

**A-046 falsified all eight guards and reported "8/8 caught, 0 defeated". THAT HEADLINE WAS
WORTHLESS AND A-047 IS THE CORRECTION.** An independent reviewer, told to defeat a guard rather
than to confirm one, produced **seven confirmed defeats within hours** — every one a violation of
a guard's own stated purpose that the guard does not catch. A-046 stated the bound ("each guard
fires on the violation it was pointed at; it says nothing about violations nobody imagined") and
that bound turned out to be the entire story, not a footnote. **Falsifying an instrument against
the violation you designed it for measures your imagination, not the instrument.** The technique
is still worth running — it is cheap and it caught real things — but its output is a floor, and
reporting a floor as a headline is the honesty defect this project exists to study.
**Fixed under A-047 (John scoped it):** the corpus stage never hashed the committed view files at
all, so tampering one passed while the gate printed "committed views semantically current" — the
provenance claim the corpus rests on; and the vendor scan was case-sensitive while the label scan
beside it was not, so `| coinbase |` passed and `| Coinbase |` failed. **Recorded, not fixed:** the
unscoped spec greps, three secrets-guard holes, the rename gate's second-remote and trailing-slash
gaps, the class-coverage laundering route through committed `results/`, and — **omitted from this
list until 2026-08-17, though A-047's own entry calls it "A GENUINE HOLE THAT REMAINS" — that A
GREEN SUITE IS NOT A CORRECT VERIFIER:** neutering the `evidenceHash` check by hand left all
146 tests passing and all 7 samples verifying, because no tamper mode corrupted `evidence.hash`.
**CLOSED 2026-08-17 (A-049): the `evidence-hash` mode mutates the PUBLISHED hash rather than the
canonical bytes, so it isolates that one check, and the same neutering now produces 12 failures.**
The generalisation is NOT closed — **A DIRECTED SWEEP HAS NOW RUN (A-051)** over the SIX other modules — the count in this
sentence read *five* and omitted `jcs.py`, an error that reached three documents and the sweep's
own brief. 142 mutations applied, **41 survived a green gate**; three verdict-flippers are closed
and the rest are in the register. `verify.py` — 1681 lines, the file that decides the verdict —
remains unswept, and that is now the largest MEASURED gap rather than an assumed one.
See `docs/v1-1-register.md` §8.

**A-048 (2026-08-17) then broke A-047's own headline.** A second review round — thinner briefs,
three reviewers — found the verifier floor counted tests that never ran (`@unittest.skip`,
`@unittest.expectedFailure` over a real RFC 8785 violation, and a `setUp` monkeypatch giving
`OK (skipped=146)`: every assertion disabled, floor satisfied), and that the new committed-view
check exempted `expiryAfter`/`expiryBefore` — a CONFORMANCE INPUT feeding
`EVAL_ENTITLEMENT_ADVANCED` in 36 of 50 views, not the "timestamp fields" three documents called
them. **Both fixed and falsified against clean baselines.** Worst item: A-047's annotation to the
signed S2 pack claimed §11 had made the overclaim, when §11 said the opposite and was RIGHT
("git history, not re-execution"); that misdescription reached a facilitated ratification
(D-045). Corrected in place under John's ruling that repairing a false statement inside an
annotation is not itself a new annotation.

**TEN mechanical stages guard the gate** *(eight until A-064 added labelling-artifact pinning — the labels of record were guarded by nothing while the prompt that produced them was hash-frozen — and A-062 then added the §7.3 ablation-report provenance stage; COUNT THEM IN `scripts/test.sh` before quoting this number, because this line has been wrong three times)***:** secrets (A-007), rename (D-016), labelling-prompt
freeze (D-011a), EIP-712 type strings (D-023), §5.7.1 check coverage (D-031), **corpus class
coverage (A-036, new 2026-08-16)**, vendor honesty (§7.5 Gate 5, D-008), and — deep profile
only — **the §7.1 corpus executed with its committed views verified**. The Gate 7 canary history
prints and deliberately cannot fail the gate.

**Two of the eight pass on something weaker than a pass, and both say so on every run.** Vendor
honesty now reports D-008(1) as MET and (3) as **certified by record** (D-038) — it checks that a
named certification exists in §2 and that §2 still hashes to the table John certified, and states
that it cannot check the certification is *right*. Class coverage passes on a RATCHET: **14 of 20
classes exercise the class they name**, six are carried, one of them a GAP, and a green line
means only that no NEW class went vacuous. Read their output, not their exit status.

- **§9 steps 1–9 done.** Steps 4–6 reviewed under A-022; steps 1–3 under A-016 (whose
  verifications were mostly cut short by a spend limit — that limit is NOT retired); **steps
  7–8 reviewed for the first time this session**, ten findings, all remediated.
- **Ablation:** false allows **38 / 8 / 1**; contribution — baseline alone 9, effect extraction
  29, **mandate conformance 8**; exact match 12 / 41 / 49. **D-034 gave the partition a
  criterion** (L3-only = compares the call or its effects to the mandate's PURPOSE fields) and
  the figure fell from 17 to 8. The 8 are exactly the wrong-purpose class. The report emits the
  split as a CHECK — its second row must be empty.
- **D-010 verifier: 7 samples, 77 tamper cases over 29 modes, 160 tests — and all four are FLOORS
  the gate asserts.** *(CORRECTED 2026-08-17, round five `B-4`/`B-1`: this line read `7/7, 62/62,
  24 modes, 149/149` — a fourth staleness in this file, seventy-nine lines below a §3 headline
  that already said 160 and 77/29. **The identical stale trio is STILL PRINTED BY THE GATE
  ITSELF** in `scripts/test.sh`'s COVERAGE BOUNDARY, where it is labelled "ALL THREE FIGURES ARE
  FLOORS THIS RUN ASSERTS" beside floors of 160/7/77/29 — five of eight round-five lenses found
  it independently. That one is CODE and is NOT fixed: it is unscoped remediation awaiting John,
  register §13.)* *This line read `6/6, 42/42, 70/70` until
  2026-08-16, forty-six lines below the headline in §3 that already said 146/146 and 7 samples —
  i.e. this file contradicted itself, in the file that opens by declaring itself the memory. It
  was **not** fixed by A-045, whose decision entry and commit message both claim "both layers are
  corrected"; exactly one was. Found by an independent reviewer, not by the author who edited this
  file twice in the same session.*
- **Gate 7 canary:** built, run live once, agrees with the pinned recording. D-036 sets the
  cadence at **monthly**; a DRIFT row is a finding about the model, never a build failure.
- **Labellers:** E and F are the labels of record. G, H, J, K, **L and M** are targeted
  measurement arms and are audit trail only. **A-033 as first written was wrong and is corrected
  in place** — the contamination channel moved one label (F051), measured by K. **L and M are
  the same D-035 control arm run twice by two concurrent sessions (A-037); M is the duplicate,
  re-designated, and its provenance says so. They agree with E and with each other on all five
  labels and on confidence.** Next arm is N.

## 4. Decisions and findings — 2026-08-15 and 2026-08-16

**The canonical record is `docs/decisions.md`, and it is the one that wins.** This table is an
index, ordered roughly as things happened. Every entry below has a full entry there with its
reasoning, its rejected options, and where stated the condition that would reverse it.

| | Subject |
|---|---|
| D-033 | Measure A-030's contamination channel; add model diversity |
| D-034 | The §7.3 partition gets a criterion; mandate conformance 17 → 8 |
| D-035 | **Resolves A-034** — measure five fixtures, then treat the PASSAGES as the v1.1 defect. Escalation threshold declared: 2+ movements → full re-freeze |
| D-036 | Canary monthly; D-009 order confirmed; A-029 accepted as bounded |
| A-029 | Views not byte-reproducible — now bounded by normalised digests |
| A-030 | The specification is a contamination channel for labellers |
| A-031 | The five owed items built; three agent-made calls, one flagged reversible |
| A-032 | Three adversarial reviews: two blockers, fourteen others |
| A-033 | D-033 executed — **corrected**: the channel moved one label |
| A-034 | Agent call not to re-freeze — **TRIGGERED, superseded by D-035** |
| A-036 | Two fixtures do not exercise the class they name; no check asserts they do |
| A-037 | **Two sessions ran the same measurement and one overwrote the other's committed evidence.** Caught by luck, not by any guard |
| A-038 | A-036's check **built** and in the gate: 14/20 classes exercise the class they name; two new vacuous classes found |
| D-037 | **One agent session at a time on this tree.** Resolves A-037 |
| D-038 | **GATE 5 CERTIFIED.** Seven rulings; §2 rewritten; 11/11 cited; stale on any §2 edit |
| D-039 | The two A-038 classes ruled apart: override is an accepted **delegation**, conflicting-block-state is a **GAP owing a fixture** |
| A-039 | **Two adversarial reviews, 25 findings.** Both new guards were defeatable; several claims exceeded their evidence. 11 of 12 exploits now caught, 1 documented residual |
| D-040 | Closes A-039: **F002 stays** (it earns its place by blocking), the class map widens to §7.1's four hard caps, condition (2)'s residual accepted as documented |
| D-041 | **GATE S2 SIGNED — PASS, John, 2026-08-16.** Signed on §11's limits, not despite them. Steps 1–3's limit recorded not retired; dashboard stays outside S2; 14/20 does not flip a gate |
| A-040 | The steps 1–3 review S2 was signed WITHOUT. **The encoding held; the two layers built on it did not.** Vault caps native value only; the invariant campaign killed nothing the fast tests did; the D-010 verifier certified a forged refusal |
| D-042 | **S2 stands, annotated.** §7.1's containment claim corrected (cap → v1.1); the campaign gets its two missing arms; the verifier is repaired by an agent that has not read the implementation |
| A-041 | Verifier repaired, 70 → 101 tests, both exploits now fail closed. **Its best output is a spec finding: §5 defined no refusal record at all**, so D-012's requirement was unbuildable from the published document |
| D-043 | **CONSOLIDATE — no new front, no ladder rung.** Re-label bound to pre-publication with a named trigger; §5.5.1 RefusalRecord published; override event added; Anvil keys re-baselined |
| A-044 | The six remaining step-3 findings, ruled and fixed: backpressure bounded nothing, the signer's namespace was caller-writable, `evidenceHash` non-injective, two refusal paths left no artifact. Anchor recency **recorded as a limit** |
| A-043 | **CRITICAL, fixed.** A signed ALLOW was obtainable for calldata nobody decoded, and executed onchain twice in reproduction. A-028's repair covered one of two branches; **11 tests were passing through the hole** |
| D-044 | **Session close.** Pushed; one last review of §9 step 3 (A-016's 6 unadjudicated skeptics); both capability deferrals CONFIRMED; **pre-publication NOT started** |
| D-045 | S2 pack annotated for A-042 and A-047, **with a stopping rule** |
| D-046 | Round two authorised; reading declared before results |
| D-047 | **The review loop terminates on a CLEAN ROUND — and an agent may not amend that** |
| D-048 | **Pre-publication sequences AFTER the loop.** A clean round is a precondition, not a trigger |
| A-045 | The D-010 verifier was an S2 deliverable **no gate ran** |
| A-046 | All eight guards falsified — headline later shown worthless (see A-047) |
| A-047 | **Three reviewers: 7 guard defeats.** A-046's "8/8" refuted; corpus provenance never checked |
| A-048 | **Round two broke A-047's fixes**, incl. one John had ratified. Floor counted tests that never ran |
| A-049 | `evidence-hash` mode; vendor roster de-duplicated; casing residual narrowed |
| A-050 | Round three launched; reading declared first; **taxonomy later proved incomplete** |
| A-051 | **41 surviving mutations** across six verifier modules. My brief omitted `jcs.py` |
| A-052 | **The secret guard let a real private key through** — `...` and `EXAMPLE` suppressed the line |
| A-053 | The `verify.py` sweep commissioned; reviewer invited to criticise the brief |
| A-054 | Charsets pinned by COMPLEMENT rather than by bad list |
| A-055 | **`verify.py`: 14 survivors + TWO LIVE certification defects.** Presenter chose the trust root |
| A-056 | Override cluster, the anchor, and **the corpus-vs-verifier category error** |
| A-057 | Round five commissioned; the reading declared before results; eight lenses, whole tree |
| A-058 | **ROUND FIVE: NOT CLEAN. 51 findings, 2 CRITICAL, the same repair defect three times. D-048(b) fired** |
| D-049 | John: **the loop continues and "full breadth" gets defined**; remediation scoped to the three LIVE defects |
| A-059 | The three live defects fixed. **The first draft of the first fix shipped the very defect it was fixing** |
| A-060 | ~~DRAFT~~ **RATIFIED by D-050(1)** — the nine-surface definition of "full breadth" |
| D-050 | John's six walkthrough rulings: **A-060 ratified**, cluster C only, leads → round six, reports committed, push, kill the leaks |
| A-061 | Cluster C built: the signer's prototype-chain verdict check and the verifier's array-precedence hole |
| A-062 | The coverage boundary audited WHOLE — four false statements, two reported by nobody; G-2 closed with a provenance gate stage |
| A-063 | **F-VAULT-1: D-042's correction was itself false.** Four sites repaired, a limit test added, **claim UNCERTIFIED — awaits John** |
| A-064 | **Cluster B closed:** labels pinned (9th guard), corpus VERDICTS compared, both window lower bounds exercised, the invariant arm's registration asserted |
| A-065 | Two verified leads: the env template that never shipped, and a suite figure counted twice |
| A-066 | **The deep profile can now be run from a worktree** — D-050(1)'s condition was unmeetable when it was ratified |
| A-067 | **21 of 24 leads CONFIRMED** by four independent adjudicators. `D-08` raised to HIGH and fixed; `H-4` fixed; 19 recorded |
| D-051 | John's four walkthrough rulings: **§7.1 CERTIFIED**, fix MEDIUM / accept LOW, round six after the fixes, probes preserved |
| A-068 | Seven MEDIUMs fixed; **`E3` and `E4` returned to John as design forks** |
| A-069 | E4's verifier half built — and the fixture gap it found matters more than the check |
| A-042 | **The D-010 experiment run properly:** a schema-only build met a real signed refusal it had never seen. Everything §5.5.1 STATED matched first time; the envelope it omitted diverged, plus three defects in the section — all mine, all corrected. 101 → 146 tests |

## 5. Traces — what worked, and what was a dead end

**Dead ends and traps — do not repeat:**

- **A CHECK THAT ALWAYS FIRES LOOKS EXACTLY LIKE ONE THAT CATCHES EVERYTHING.** A-051: the first
  verdict check used BSD `sed` with `\|` alternation, which basic regex does not support, so it
  matched nothing and failed on EVERY run including a clean tree. All three defeat probes duly
  came back "caught, exit 1" — which is what a working fix looks like. **Caught only by running
  the BASELINE first on an untouched tree.** This is the twin of the vacuous probe and it is the
  more seductive one, because every falsification appears to succeed.
- **A TEST THAT ASSERTS A PROPERTY OF THE CORPUS CANNOT CATCH A VERIFIER THAT ACCEPTS WHAT THE
  CORPUS HAPPENS NOT TO CONTAIN.** A-056: `test_only_review_receipts_carry_an_override` asserts
  no fixture overrides a BLOCK receipt — true, worth knowing, and completely silent on whether
  the verifier would accept one. §5.5's check was changed to `verdict in ("REVIEW","BLOCK")` and
  every test passed. Three checks survived on this confusion. **A fixture property says what the
  repository CONTAINS; a verifier property says what the code ACCEPTS.**
- **RE-SIGNING IS WHAT MAKES A BINDING THE WITNESS.** A-056: `override-nonce` bumps a SIGNED
  field and leaves the old signature, so the signature check fires first and §3.3(9)'s nonce
  binding never bites. `override-wrongkey` leaves `ownerAddress` declaring the owner, so §3.3(7)
  never bites. A tamper mode that is caught by a *different* check than the one it targets is
  worth nothing, and the tamper matrix will score that check as covered.
- **THE TAMPER MATRIX IS NOT A COVERAGE MEASURE; MUTATION IS.** A-055 measured both directions
  and refuted "a check no mode targets is a check nothing asserts" — an inference that had been
  load-bearing across three entries. Of 33 checks no mode makes fail, 18 probed → **10 CAUGHT**.
  Of checks that DO fail under some mode, 10 neutered → **5 SURVIVED**.
- **`__pycache__` MASKS SAME-SIZE MUTATIONS.** A same-length edit landing in the same
  filesystem-mtime second makes CPython reuse stale bytecode, so the mutated run executes clean
  code and reads as a no-op — **and same-size mutations are the interesting ones.** Run `python3
  -B` and clear `__pycache__` between variants.
- **A REVIEW BRIEF IS AN INSTRUMENT AND NOTHING CHECKS IT.** Twice in two rounds the brief was
  the defect: A-051's named five modules when there were six, omitting the one holding two of
  that round's best findings; A-055's was scoped to `Check(...)` mutations and would have missed
  the one live defect that needs no mutation. **Invite the reviewer to report that the brief is
  wrong** — that is what surfaced the second one.

- **A FALSIFICATION PROBE CAN ITSELF BE THE DEAD INSTRUMENT, AND ITS SILENCE READS AS A PASS.**
  A-045: to prove the new verifier stage could turn the gate red, I appended a deliberately
  failing test to `verifier/test_verifier.py` and ran the gate. **It printed GATE PASSED.** The
  correct reading was not "the wiring is broken" — it was that `unittest.main(verbosity=2)` is
  the last statement in that file, so a class appended *after* it is defined only after
  `sys.exit()` has already fired and **never runs at all**. The probe tested nothing; the test
  count stayed at 146 and I had not looked. Had I injected the probe and seen GATE FAILED for
  some unrelated reason, or skipped the probe entirely on the grounds that `|| fail=1` is
  obvious, the stage would have shipped with its wiring unproven either way. **Check that the
  probe MOVED SOMETHING — the count, the output — before you believe what its result implies.**
  Injected before the `__main__` block it ran (147 tests) and the gate went red correctly.
  **A-046 then measured the rate: FOUR of about twelve probes across the eight-guard
  falsification were vacuous, and every single time the GUARD was right and the PROBE was
  wrong** — a `sed` anchor absent from the file, a code injected outside the array the guard
  actually reads, prose where the guard searches for two literal labels, and a caveat probed
  against text the guard normalises for line-wrapping before comparing. **Each one produced a
  green guard that reads exactly like "this guard does not fire."** Assert that the edit
  applied and read the diff, every time; in this technique the probe is the unreliable half.
- **A REGRESSION TEST CAN PASS AGAINST THE DEFECT IT NAMES.** A-044: the first backpressure
  test I wrote pinned the deadlock my own repair could introduce, not the unbounded dispatch it
  was written for — it passed against the unfixed server. **Always run a new regression test
  against the PRE-FIX code and confirm it fails.** If it does not, it is testing your fix, not
  the defect.
- **A REPAIR CAN GENERALISE THE DEMONSTRATION INSTEAD OF THE ARGUMENT.** A-028 F1 fixed the
  branch its reviewer exploited and left the identical hole in the sibling branch two lines
  down, though the justification it wrote covered both. A second reviewer walked through the
  other half a year of commits later (A-043). **When you fix a defect, ask what the ARGUMENT
  covers, not what the reproduction touched.**
- **A COMMENT THAT DESCRIBES A VULNERABILITY AND CALLS IT A FIXTURE HAZARD.** A-028's test file
  says an unsupported selector means "the signer's own decode fails too, so bundle and signer
  honestly agree and nothing fires" — and routes around it to avoid a test passing for the
  wrong reason. That sentence IS the bypass, written down and filed as an inconvenience.
- **Fixtures chosen as "arbitrary bytes" are never arbitrary.** Eleven tests used an undecodable
  selector because they needed *some* calldata for tests about other things, and every one was
  passing through A-043's hole. They went red the moment it closed, which is the only reason
  the blast radius was visible. Use `decodablePurchaseCallData()`; say so explicitly when a
  test is genuinely about undecodable bytes.
- **A guard, a test or a mutation can exist and point at the wrong thing.** Three times this
  session: mutation anchors rotted when the code they targeted was rewritten (twice in one
  day); a leak guard built probes by pairing FILTERED words, so 10 of 17 could never match and
  the injection payload could pass; a canary matched `ATTACKER.slice(2,10)` — the address's HIGH
  bytes, all zeros — so every approval to `address(0)` was logged as an approval to the
  attacker. **Re-run the batch whose target you just edited.**
- **A negative test case can be the one input that cannot expose the bug.** The canary's
  negative was `0x1111…1111`, the only address containing no run of eight zeros.
- **Unit-testing a guard does not test that anything CALLS it.** Six of ten mutations against
  the injection wiring survived because every test drove the pure function and none drove the
  pipeline. Where behaviour cannot be reached, assert the STRUCTURE that produces it — read the
  caller's source, require the call site — and say in the test why.
- **A fall-through is a claim.** `verdictOf` had no treatment-arm validity check, so an arm that
  proposed *nothing* fell through to "RESISTED — the model still proposed the purchase".
- **A description a ruling rests on must describe the code.** D-034 quoted L2's doc comment as
  what decided the criterion, and L2 was carrying two checks from a different implementation.
- **Do not generalise a bound from a sample without sweeping the whole set for
  counterexamples.** A-033 claimed the channel "moved no label" from nine fixtures; the
  counterexample (F051) was already on disk, in a label's own note.
- **Measure the claim you just wrote.** The seeded gate profile is *nearly* reproducible, not
  reproducible — outcomes and call counts match, revert tallies differ by one on two of ten
  invariants. Caught before it reached a document.
- **A denylist matched by substring only catches the spellings it declares**; a name-based guard
  cannot catch a semantic leak; an allowlist exemption must be scoped to the DEPTH it was
  decided at.
- **Do not summarise ratified decisions for a labeller**, and do not reuse a sample across
  rounds.
- **A HANDLER ACTION MUST BE REGISTERED AS WELL AS WRITTEN, and forgetting it is silent.**
  D-042's two invariant arms were written, their non-vacuity test passed — it calls them
  directly — and the whole suite went green, while the mutation they were written for still
  survived, because `targetSelector` had not been told the new selectors existed. **The
  invariants existed and pointed at nothing.** Caught only by re-running the mutation instead of
  trusting the green suite. This is the project's most-repeated defect appearing *inside the fix
  for a finding about the same defect*.
- **A stateful campaign's coverage is bounded by what its handler can BUILD, not by its call
  count.** 262,144 calls that never construct a future nonce prove nothing about future nonces.
  Before D-042 the campaign killed nothing the 56 deterministic tests did not.
- **A clean `git status` is a statement about one instant, not a lock.** A-037: a second session
  committed between this session's check and its write, and the write silently clobbered it.
  The collision was caught only because both sessions picked the same letter. **Nothing in the
  repository can detect a second writer** — every guard here validates content, and content
  cannot tell you who produced it.
- **The corpus runner picks a random port and occasionally collides.** Re-run before diagnosing.
  Concurrent runs also contend — nine spurious failures came from a mutation sweep running
  beside the suite.

**What worked:**

- **Building an independent implementation from the SPEC ALONE and measuring it against a real
  artifact it had never seen** (A-042). Keep the two halves apart, and **declare what each
  outcome means before either finishes** — agreement means the spec is precise enough to build
  from, divergence is a spec gap. It resolved as divergence and named the exact clause. **The
  spec text was four days old and mine; the independent side found what I could not, because I
  could not un-know the implementation.** This is the only technique here that tests a
  DOCUMENT rather than code.
- **Writing a fixture's own falsification guard into the tool that emits it.** The refusal
  sample's spec carried "if the signer did not refuse, fail the run" — and it fired on the first
  attempt, catching that pausing before evaluation produces a BLOCK the signer will happily
  attest. A sample that exists to demonstrate X and silently does not is worse than no sample.
- **Adversarial review at a fixed commit, told to prove the work fails.** Four reviews, ~24
  material findings, several missed by the suite, the mutation harness and prior reviews. Give
  each a FROZEN tree — `git worktree add <scratch> <commit>` with `node_modules` symlinked
  works and lets you keep editing.
- **Requiring a provenance attestation from every labeller.** **Eight for eight** produced a
  first-order finding this way, unprompted: the harness-injected memory file (repeatedly), the
  specification-as-contamination-channel, the published reason codes, `failureMode`'s undefined
  encoding, the F026/F051 call-graph-hash contradiction, F056 not exercising reentrancy, and a
  labeller declining an injected instruction that would have breached the protocol.
- **Adversarial review of a GUARD, not just of code.** Two reviewers at a frozen commit produced
  twenty-five findings against two guards and the documents citing them — including that the
  certification check grepped the whole proposal while the comment beside it congratulated the
  author for having just fixed that exact defect in the function above. **Knowing about a defect
  class is not protection from it.**
- **Measuring a fork instead of arguing it.** D-033's control arm settled in one run what would
  otherwise have been unfalsifiable — then produced the counterexample that corrected A-033.
- **Single-variable experiment design.** H varied only the spec text; J varied only the model.
- **Declaring the escalation threshold BEFORE seeing the result** (D-035: two movements).
- **Making a guard state what it cannot check.** `check-vendor-honesty.sh` fails on the
  mechanical conditions and reports the other two as UNCERTIFIED, never as a pass.

## 6. Environment facts

- **MORE THAN ONE AGENT SESSION CAN BE OPEN ON THIS TREE, AND NOTHING STOPS THEM COLLIDING.**
  It happened (A-037): two sessions ran D-035's control arm minutes apart and one overwrote a
  file the other had just committed. **`git status` clean and a directory listing are only true
  for the instant they run** — re-check immediately before writing, and prefer creating a file
  under a name nobody else could pick. Every guard in this repository checks the CONTENT of the
  tree and none can see a second writer.
- Foundry v1.7.1 at `$HOME/.foundry/bin` — **not on the agent's non-interactive PATH**.
  `scripts/mutate.sh` and `scripts/test.sh` export it themselves.
- Node v26.3.0, viem 2.55.10. The signer runs under Node's native type stripping: erasable
  syntax only, and relative imports need the `.ts` extension.
- `.env` is gitignored and holds `ANTHROPIC_API_KEY`. The pre-commit hook blocks it.
- **Claude Opus 5 rejects `temperature`/`top_p`/`top_k` (400).**
- **After ANY Solidity mutation — `scripts/mutate.sh` or a hand-rolled `sed` — `contracts/out`
  holds the LAST mutant's bytecode.** Run `forge build --force` before emitting samples, or the
  artifacts are signed against a deliberately broken vault. **THE SYMPTOM IS MISLEADING AND COST
  A DETOUR ON 2026-08-16: the gate reports `corpus: DIGEST MISMATCH — the committed labeller
  views are NOT what this code now produces`,** which reads as "your change moved the labelling
  views" — the re-label trigger — when the source is clean and only the build artifacts are
  stale. Check `git diff contracts/src` FIRST; if it is empty, force-rebuild before believing
  the mismatch.
- **The harness injects the workspace `CLAUDE.md` and John's `MEMORY.md` into every subagent.**
  Five labellers reported it; one declined an instruction inside it that would have breached the
  labelling protocol. This cannot be fixed from the repository — assume every labeller starts
  partly oriented, and keep asking for the attestation that surfaces it.

## 7. Verification tooling

`scripts/mutate.sh` — batches across signer, decoders, pipeline, evaluator, the D-012/D-014
rulings, the D-017 corrections, the step-7 transcriber (`P`), the ablation layers (`B`), the
corpus guards (`C`), and the vault (`S`, Solidity). Run `./scripts/mutate.sh C` for one batch or
`./scripts/mutate.sh C12` for one mutation. **Get counts by running it, not by grepping.**

Latest measured: **batch C 14/14 caught**, **batch S 31/31 caught**, 0 survived, 0 failed to
apply. Three qualifications belong with that number: it is **not** comparable to A-028's "29 of
45 survived", because these tests were written for these mutants; **four anchors had to be
re-aimed** after the code they target was rewritten, twice in one day; and **C12 survived its
first run**, catching a test that passed for a reason other than the one it named — which three
independent reviews and a green suite had missed.

**There is no `spike` batch.** `ts/src/spike/**` is excluded from `tsconfig`, and its two live
defects this session were found by reading, not by tooling. `canary.test.ts` now covers the
verdict logic; the arms themselves need a model and are untested.

---

*Entries below predate 2026-08-15 and are unchanged.*

## 8. Pre-existing traces

- **Do not make non-vacuity an `afterInvariant` hook.** Foundry shrinks to a minimal sequence,
  and any one-call sequence has zero executions by construction.
- **Do not randomize every dimension inside one invariant handler action.** 16,384 calls, zero
  executions, all invariants PASS.
- **`forge` caches invariant failures in `contracts/cache/invariant/`.**
- **A `// forge-lint: disable-next-line(...)` directive must be the line immediately before the
  code.**
- **`Promise.all([f(await g()), f(await h())])` is NOT concurrent.**
- **A socket-level test cannot observe the signer's reserve-versus-sign ordering.**
- **Do not measure mutation results by parsing the `node:test` reporter.** Use exit status.
- **`check-secrets.sh` scans TRACKED files** (`--staged` after `git add`);
  `check-vendor-honesty.sh` scans tracked AND untracked-but-not-ignored.
- **Do not run an adversarial review while still editing the tree.** Freeze, then review.
- **A mutation set written by the implementer probes only the checks the implementer already
  thought about** — and inherits its author's blind spots even when the author is a reviewer.
