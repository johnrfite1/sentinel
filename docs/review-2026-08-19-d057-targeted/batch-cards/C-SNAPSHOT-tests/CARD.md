# C-SNAPSHOT — frozen independent test contract

**Verdict: HOLD for test-contract readiness only.** This is not an implementation approval,
gate signature, certification, ratification, publication, or authorization to push.

**Frozen subject:** `1655b120a653b60ccb5b3a22583c0001d59ea7a4` (tree
`b2c8fb1e53d35ea40655dc83faa61f8a76dd4f78`). The subject was clean when authorship began.
The independent test author wrote none of the future Batch C implementation.

**Authority:** D-058(1), (8)C and (9); D-059(5)–(6); D-060(1); D-066(2)–(3).

This directory is the complete test-only deliverable. `TESTS.patch` is preserved but not applied
in this commit. No production source, existing test, `scripts/test.sh`, `protocol.ts`, maintained
claim, floor, prior evidence, or signed material is changed.

## 1. Declared production boundary

Completeness is claimed only for `ChainUnstableError` and
`createChainReader(...).readVaultState` in `ts/src/signer/vault.ts`, at the frozen subject. The
contract covers the three exhaustion causes, their pure and required mixed sequences, stable
success, and ordinary RPC/read failure.

The false `ts/src/signer/protocol.ts` claim that a signed refusal “detail” distinguishes chain
conditions is an explicit **excluded dependency owned by Batch D / D-F6 / C5**. There is no such
wire field. Batch C must not edit it, invent a signed detail, or split
`SIGNER_CHAIN_UNSTABLE` into new public reason codes. Its current FATAL tier and remedy remain.

## 2. Independently derived branch matrix

`SNAPSHOT_ATTEMPTS` is five and each successful pin drives eleven state/code reads.

| State | End condition | Reads in that attempt | Required fact |
|---|---|---:|---|
| B0 | initialization | 0 | no cause has yet been observed |
| B1 | `head.hash === null` before reads | 0 | pending head before reads; no movement/read claim |
| B2a | confirmation height differs | 11 | head moved after pinned reads |
| B2b | height equal, confirmation hash differs | 11 | same-height reorg after pinned reads |
| B3 | hashed head + reads + `confirm.hash === null` | 11 | pending confirmation after pinned reads; not movement |
| B4 | five attempts exhausted | sum of attempts | error truthfully aggregates all and only observed causes |
| B5 | confirmation height/hash match | 11 | return the exact hashed pin and snapshot |

The eight exhaustion scenarios frozen by the patch are pure B1, pure B2 movement, pure B2 reorg,
pure B3, B1+B3, B1+B2, B2+B3, and B1+B2+B3. Stable success and ordinary read failure are the two
additional controls, for ten tests total.

## 3. Smallest admissible classification contract

The frozen tests do not prescribe a counter, set, flags, helper, or constructor rewrite. They
require only these externally observable facts:

1. Preserve the exported `ChainUnstableError` class and compatible existing API.
2. Preserve `pendingOnly`; it is `true` **only** when all exhausted attempts ended at B1. A hashed
   head followed by B3 makes it `false`, even when no B2 movement occurred.
3. Preserve the attempt count in the message.
4. The message semantically names all and only the cause categories observed: pre-read pending
   head, changed/replaced head after reads, and pending confirmation after reads.
5. A mixed run may not inherit pure wording such as “every observation” or “under each pinned
   read” when some attempts contradict that universal.
6. Stable success, eleven-read pinning, same-height reorg detection, and ordinary read-error
   propagation remain unchanged.

The oracle deliberately accepts equivalent truthful wording rather than one exact sentence. It
does not require a new exported classification object or any wire-format change.

## 4. Frozen instruments

| File | Role |
|---|---|
| `TESTS.patch` | Adds one independent 329-line TypeScript test file containing the ten cases above. |
| `mutate.py` | Applies five exact, typecheck-clean baseline oracle mutations: B1, B2 and B3 path substitutions, pure-message swap, and generic-message collapse. |
| `mutation-matrix.tsv` | Exact final case totals, intended named catches, and raw-output hashes. |
| `RUNBOOK.md` | Reproduction commands for isolated clones only. |

The current baseline itself is the live collapse mutant for B3 and all four mixed families. The
exact path/message mutants establish that existing pure controls and new defect tests move for
their named assertions, rather than treating any rejection as a catch.

## 5. Contract the implementer receives

The implementer may:

1. apply `TESTS.patch` unchanged; and
2. make the smallest coherent change inside the two declared `vault.ts` symbols that satisfies
   the semantic classification contract.

The implementer may not edit the frozen test, any existing test, `protocol.ts`, `attest.ts`, the
public reason vocabulary or tiers, `scripts/test.sh`, floors, maintained claims, prior evidence,
or signed material. No post-repair pass is claimed here; it is deliberately deferred to the
implementation attempt.

## 6. Fixed success condition

The Batch C implementation holds only if:

- `TESTS.patch` applies unchanged and all ten new tests pass;
- the full TypeScript suite and typecheck pass without shrinking or weakening tests;
- every B1/B2/B3 pure and required mixed semantic mutant is caught at a named assertion;
- the unchanged top-level fast gate passes with the new tests included;
- protected/excluded files stay unchanged; and
- repository/workspace guards report no new finding.

Per D-058(9), a failure permits one bounded correction under this same contract, not a test edit
or scope expansion.
