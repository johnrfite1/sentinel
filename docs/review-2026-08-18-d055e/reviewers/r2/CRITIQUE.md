# REVIEWER 2 — CRITIQUE of the brief, the scope and the apparatus

The common brief invites me to report that my own brief is wrong. Five things.

## 1. Rule 5 names two authorities, and the item I nearly re-reported is in neither

**This is the most consequential one, and it produced a finding (`R2-F4`).**

> Rule 5: *The register `docs/v1-1-register.md` §13.4 is the list of what is already known;
> `docs/gate-s2-evidence.md` §11.0 is the five findings John ACCEPTED as limits.*

Neither contains the `decodedSelectorAndParameters.description` gap. It is recorded **only inside
a ~5,000-word `docs/decisions.md` A-074 entry**, as residual (c), which itself says "Recorded in
the register" — and it is not. I wrote the gap up as a fresh finding, in full, and demoted it only
because I happened to read A-074 for other reasons.

**The apparatus problem, not just the record problem:** the brief tells reviewers where the
recorded list is, and the recorded list is incomplete, so the brief's own instruction produces
false positives. `decisions.md` is 240+ entries of dense prose with no index; "check whether this is
recorded" is not a tractable operation against it. Either §13.4/§14 must be swept to completeness
before a round, or rule 5 must name `decisions.md` as a third authority and accept that reviewers
will miss things in it.

## 2. "Prove the work fails" and "do not re-report" pull in opposite directions, and the second wins by default

Re-reporting costs a reviewer nothing but a demotion. **Failing to look at something because it
*might* be recorded costs the round a finding and leaves no trace.** The incentive under time
pressure is to skip anything that smells familiar. I caught myself doing it twice — I nearly did
not probe the D-09(c) ceiling at all, because §13.4 says **FIXED (A-076)** in bold, and the third
route (`R2-F3`) is behind that word.

A cheap fix: the briefs already say "showing a recorded item is WORSE than recorded IS a finding".
Make the *stronger* instruction explicit — **probe recorded items anyway, and report the probe as a
null result if it holds.** That converts the incentive from "avoid the recorded list" to "measure
against it", and it produces null results the next round can use. Four of my nine nulls are of
exactly that shape and I produced them despite the brief, not because of it.

## 3. My surface is nine directories and the brief points at one of them

The directed brief spends its whole body on A-075/E3 and the five "worth attacking" bullets, all of
which sit in `signer/`, `evaluate/` and `simulate/`. **`propose/**` and `tools/**` are named in the
scope sentence and then never mentioned again.** I followed the direction, went deep on E3, and
consequently did not exercise `propose/` at all and `tools/` barely (see `COVERAGE.md`).

I think the direction was correct — the depth on E3 produced my two most substantive findings — but
the brief should say which parts of the assigned surface it is *consciously deprioritising*, rather
than listing nine directories and then steering. As written, a reader of my report would reasonably
assume `propose/` was covered because it was assigned. It was not.

## 4. The provisioning is better than round five's and still has one standing false signal

`git diff HEAD --stat -- .` reports two changed files at baseline — the two symlinked submodules —
**before any reviewer touches anything**. The brief warns that bare `git status` exits 128 and
recommends `git diff HEAD --stat`, but does not warn that the recommended command has a permanent
two-line false positive. A reviewer who adopts it as their revert check has a check that never
reads clean, which after a few hours reads as noise and stops being read at all. **I used `cmp`
against a 361-file pristine copy instead** (the brief does mandate `cmp`; I am noting that its own
suggested git command is not a substitute and should be labelled as such).

Separately, and in the apparatus's favour: **`forge build` from the symlinked worktree now works**,
which is the D-052(b)/A-071 repair holding. The remaining gap is that `npm --prefix ts test` does
not build the Solidity artifacts and fails in a way that could be mistaken for a mutation result
(`DEAD-PROBES.md` DP-1). One line in the brief — "run `forge build` in `contracts/` before your
first `npm test`" — would remove a live foot-gun that costs every reviewer the same ten minutes.

## 5. The severity scale has no place to put the defect this project actually produces

Four of my six findings are **claim** defects: the code does something narrower than a comment,
a residual or a decision entry says it does. Critical/High/Medium/Low/Info is a scale for
*exploitability*, and a false claim in a signed artifact is not exploitable — so the honest
severity is always Low or Info, and the project's own declared defect class is systematically
scored as the least important thing found. `R2-F2` is the clearest case: the mechanism is the
declared architecture and works; what is wrong is that `attest.ts:426-431` and A-075's residual (c)
both describe it as establishing something it does not. I assigned MEDIUM by judgement, and I could
equally have argued LOW, and neither number carries the information that matters.

The register already distinguishes `code-defect` / `false-claim` / `instrument-defect` /
`doc-error` in its **Kind** column. **The briefs should require a Kind alongside the severity**, so
an adjudicator sees "MEDIUM false-claim" rather than having to infer it, and so a round's output can
be read as "how much of this is the honesty class" — which is the question this project exists to
ask.

## 6. A smaller one: "revert every mutation" does not say what to do about build artifacts

I created `contracts/out/` (14 MB of Foundry artifacts) because the TypeScript suite requires it. It
is gitignored, it is not a source mutation, and removing it would make the worktree unusable for the
next reader. I left it and recorded it in `ATTESTATION.md`. The brief should say which of those two
it wants; right now every reviewer decides independently and the worktrees end up in different
states.
