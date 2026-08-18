# Round six — the brief, prepared and NOT RUN

Ratified breadth: D-050(1) adopting A-060. **Nine surfaces, each covered by a reviewer that runs
its own baseline first and returns a coverage statement.** John triggers the round.

## What is different from round five, and why it matters for reading the result

Round five ran against a tree carrying 44 known-open findings, which is why its result would have
been uninterpretable: a round that returns known items cannot distinguish "the artifact is sound"
from "the reviewers found our own backlog". **Twenty of those are now closed and the rest are
adjudicated**, so round six is the first round in this loop whose outcome means something in
either direction.

## The nine lenses

| # | Surface | Brief |
|---|---|---|
| 1 | `scripts/**` — guards and the gate | DIRECTED. Nine guards now, not eight. Two are new and unreviewed: `check-label-integrity.sh` and the corpus-verdict comparison. Break one. |
| 2 | `ts/src/signer/**` + the Solidity type mirror | DIRECTED. Obtain a signed ALLOW the design forbids. `Object.hasOwn` replaced `in` at the verdict boundary — look for the sibling. |
| 3 | `ts/src/evaluate/**`, `ts/src/decode/**` | DIRECTED. Mutation sweep. Both window lower bounds are now exercised; the boundary comparisons (`<=` vs `<`) are reported unpinned and unadjudicated. |
| 4 | `contracts/src/**` + the invariant campaign | DIRECTED. Two limit tests now assert what the vault does NOT bound. Find the third thing it does not bound. |
| 5 | `ts/src/corpus/**`, `ts/src/ablation/**`, `fixtures/**` | DIRECTED. The labels are pinned and the verdicts compared — attack the pins, not the absence of them. |
| 6 | `verifier/**` | DIRECTED. Two live certification defects were found here in two consecutive rounds, both in the PREVIOUS round's repairs. Find the third. |
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
