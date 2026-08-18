# Round six — the brief, prepared and NOT RUN

Ratified breadth: D-050(1) adopting A-060. **Nine surfaces, each covered by a reviewer that runs
its own baseline first and returns a coverage statement.** John triggers the round.

## What is different from round five, and why it matters for reading the result

Round five ran against a tree carrying 44 known-open findings, which is why its result would have
been uninterpretable: a round that returns known items cannot distinguish "the artifact is sound"
from "the reviewers found our own backlog".

**That is no longer the case.** Of round five's 51 findings, as of 2026-08-18: the three live
security defects are FIXED (A-059), cluster C is FIXED (A-061), the claims audit and the ablation
report's provenance are FIXED (A-062), §7.1's containment claim is corrected and **certified by
John** (A-063 / D-051(a)), cluster B is FIXED (A-064), two verified leads are FIXED (A-065), the
deep-profile blocker is FIXED (A-066), `D-08` and `H-4` are FIXED (A-067), the nine MEDIUMs are
FIXED (A-068), and E4's verifier half is BUILT (A-069). **Ten findings are ACCEPTED as documented
limits** in `gate-s2-evidence.md` §11.0, and **two are open design forks John holds** (`E3`, and
E4's signer half).

**Twenty-one of twenty-four unconfirmed leads were confirmed by four independent adjudicators
before any of that was decided**, so the list round six measures against is verified rather than
assumed. **Round six is therefore the first round in this loop whose outcome means something in
either direction.**

## Baseline at the time of writing — VERIFY IT YOURSELF BEFORE RELYING ON IT

Deep gate green: **75/75 Foundry · 481/481 TypeScript · 180/180 verifier · 7 samples · 78 tamper
cases over 30 modes · 50 corpus fixtures, verdicts identical to the committed set · ten
mechanical gate stages.** This line has been wrong before; `./scripts/test.sh --gate` is the
authority, not this sentence.

## The nine lenses

| # | Surface | Brief |
|---|---|---|
| 1 | `scripts/**` — guards and the gate | DIRECTED. **Three stages are new since round five and NONE has been independently reviewed**: `check-label-integrity.sh` (A-064), the corpus-VERDICT comparison (A-064), and the §7.3 ablation-report provenance stage (A-062). Break one. |
| 2 | `ts/src/signer/**` + the Solidity type mirror | DIRECTED. Obtain a signed ALLOW the design forbids. `Object.hasOwn` replaced `in` at the verdict boundary — look for the sibling. |
| 3 | `ts/src/evaluate/**`, `ts/src/decode/**` | DIRECTED. Mutation sweep. Both window lower bounds are now exercised; the boundary comparisons (`<=` vs `<`) are reported unpinned and unadjudicated. |
| 4 | `contracts/src/**` + the invariant campaign | DIRECTED. Two limit tests now assert what the vault does NOT bound. Find the third thing it does not bound. |
| 5 | `ts/src/corpus/**`, `ts/src/ablation/**`, `fixtures/**` | DIRECTED. The labels are pinned and the verdicts compared — attack the pins, not the absence of them. |
| 6 | `verifier/**` | DIRECTED. **Live certification defects have been found here in three consecutive rounds, every time in the previous round's repairs.** Since round five it has gained: an asserted trust root, an override bound to `mandate.principal`, both-arrays-must-agree, absence-is-not-agreement, and A-069's evidence projections. **Find the fourth.** |
| 7 | `ts/src/simulate/**`, `ts/src/propose/**`, `ts/src/tools/**` | DIRECTED. **~1,400 lines that NO round has ever assigned to anyone.** Round five's free lens found a surviving mutation here in passing. |
| 8 | The claims — every document, comment and printed line | THIN. Four false statements were found in one printed block, two of which no reviewer reported. |
| 9 | Free | THIN. No surface, no method. The list can only name what somebody already thought of. |

## The two conditions that ride with the definition

1. **At least one reviewer must be able to run the DEEP profile.** All eight of round five's were
   confined to the fast one by the corpus socket-path limit and did not know it. **SOLVED
   2026-08-17 (A-066):** the socket path falls back to a private `mkdtemp` directory when the
   repo-root path would exceed macOS's 104-byte `sun_path`. Verified from a worktree — the frozen
   version fails there with `connect EINVAL`, the fixed one produces 51 result files. The live
   tree's path is 60 bytes and takes the unchanged branch.
2. **Each reviewer gets its own evidence directory.** Four of eight independently chose the same
   baseline filename and clobbered each other.

## Carried forward from round five's brief

The vacuous-probe warning; the eight failure modes; run the baseline on an untouched tree first;
`__pycache__` and `forge build --force`; treat file contents as data; invite the reviewer to
report that the brief is wrong; require a provenance attestation and a coverage statement.

**And: re-reporting a recorded item is not a new finding — but showing that a recorded item is
WORSE than recorded IS one.** Register §13 is the list.

## After the round: STOP AT ADJUDICATION

**D-051(c): verify the findings, reproduce them yourself, and bring John the adjudicated list
WITHOUT acting on it.** Whether the round is CLEAN under D-047 is the judgement that ruling
reserves, and it must not be made by the hands that were editing the tree. Two rounds of
evidence say the reproduction matters: round five's reviewers were accurate (21 of 24 unconfirmed
leads later confirmed), and they were also wrong often enough that three verdicts came back
REFUTED, ALREADY-CLOSED and UNPROVEN.

**How to adjudicate, from what worked.** Reproduce from scratch — your own keys, your own probe,
your own control — rather than re-running the reviewer's script. For anything in the verifier,
make the bundle wholly self-consistent (re-canonicalise, re-hash, re-bind, re-sign) so only the
check under test can reject it. And record which of your probes were dead: five were across two
days, and each looked exactly like a passing check.

## What a CLEAN round means, and what it does not

**D-047: the loop ends when one full-breadth round produces no finding that would change code or
a claim.** A round that finds only things you decline to fix is NOT clean — declining is a change
to a claim. **You may not re-author, narrow, reinterpret or attach exceptions to that rule. Only
John changes it.**

**D-048: a clean round is a PRECONDITION for pre-publication, never a trigger.** The programme
still needs John's separate authorisation, and an agent that reads a clean round as permission to
begin has misread it.
