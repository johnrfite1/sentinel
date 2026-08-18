# Attack probes from the 2026-08-16 reviews

The working artifacts of the adversarial reviews that produced **A-040** and **A-043** — the
latter being this project's only CRITICAL: a signed ALLOW obtainable for calldata nobody decoded,
reproduced twice onchain.

**These are probes, not evidence, and nothing depends on them.** Every finding they produced is
recorded in `docs/decisions.md`, fixed, and covered by regression tests in the suite. They are
preserved because they document how the CRITICAL was actually found, and because the alternative
was that they vanished with a scratchpad. Recovered from two frozen worktrees at
`9488f27` and `db46db1` before those were removed (D-051(d)).

| Artifact | From | What it is |
|---|---|---|
| `Adversarial.t.sol` | `9488f27` | Solidity probes against the vault at the S2-signing commit |
| `atk/` | `9488f27` | The JCS / keccak / signature differential corpus — generators plus the vectors they produced |
| `attack2/` | `db46db1` | The second attack set, against the signer |
| `attest.ts.reviewer-diff` | `db46db1` | The reviewer's uncommitted change to `ts/src/signer/attest.ts`, kept as a diff rather than applied |

**Do not run anything here against the live tree**, and do not treat the diff as a patch to
apply — it is a record of what a reviewer did to make a failure happen, at a commit the tree has
since moved a long way past.
