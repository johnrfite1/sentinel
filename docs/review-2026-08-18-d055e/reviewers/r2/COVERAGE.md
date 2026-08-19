# REVIEWER 2 — COVERAGE

Commit `7e0ab7f1057de278c09cc803ab4ca266f53399e1`, worktree
`_archive/sentinel-d055e-review/worktrees/w2`. Nothing outside that worktree was touched.

## What I actually ran

| command | where | result |
|---|---|---|
| `forge build` | `contracts/` | exit 0, 34 files, Solc 0.8.28 — **required before the TS suite; see DEAD-PROBES DP-1** |
| `npm --prefix ts test` (fast profile) | worktree root | **513 pass / 0 fail / 0 skipped**, 90 suites, 55.7s — `baseline-test.txt` |
| `npm --prefix ts run typecheck` | worktree root | exit 0, no diagnostics — `baseline-typecheck.txt` |
| 8 source mutations, each reverted and `cmp`-verified | `ts/src/{signer,simulate}/**` | all 8 caught; see `NULL-RESULTS.md` |
| 4 read-only probes against the worktree source | `probes/` | see `REPORT.md` |
| `npm --prefix ts test` + typecheck, post-revert | worktree root | **513 pass / 0 fail**, typecheck exit 0 — `post-revert-test.txt` |

The E3 e2e tests ran for real against Anvil (`baseline-test.txt:637-638`, `skipped 0`), so my
baseline is not a silently-degraded one.

## Assigned surface, file by file

| surface | reached | how |
|---|---|---|
| `ts/src/signer/attest.ts` | **yes, in depth** | read in full; 4 mutations; `checkEvidenceDecoding` absence traced by hand across 9 malformed shapes |
| `ts/src/signer/vault.ts` | **yes, in depth** | read in full; retry loop traced for termination; E3 argument checked against the code |
| `ts/src/signer/protocol.ts` | **yes** | read in full; tier table checked line by line against `refusesVerdict`; 1 mutation; the four recorded parser fixes re-verified |
| `ts/src/simulate/index.ts` | **yes, in depth** | read in full; 1 mutation; the anchor straddle reproduced (`R2-F1`) |
| `ts/src/simulate/anvil.ts` | **yes** | read in full; 2 mutations |
| `ts/src/evaluate/checks.ts` | **yes** | read in full; absence handling of every effect class enumerated (`R2-F5`) |
| `ts/src/evaluate/index.ts` | **yes** | read in full; intersected ceiling probed (`R2-F3`) |
| `ts/src/decode/index.ts` | **yes** | read in full; the D-014 boundary checked against `decodeBySelector`'s signature |
| Solidity type mirror (`contracts/src/types/SentinelTypes.sol`) | **partial** | typehash string and `DecisionReceiptPayload` field order read and compared against `verifier/eip712.py` and `ts/src/signer/eip712.ts`; **the hashStruct encoding itself was not independently recomputed** |
| A-072 | **yes** | all three claimed pins mutation-tested |
| D-053(b) | **yes** | 4 attack shapes constructed; 1 mutation |
| A-074 | **yes, on my half** | residual (b) and (c) checked against the tree; (c) produced `R2-F4` |
| A-075 / `E3` | **yes, in depth** | the primary target; produced `R2-F1`, `R2-F2`, `R2-F6` |

## What I did NOT reach, and why

Named here so a null is not read as coverage.

- **`ts/src/decode/abi.ts`** — the `WordReader` strictness predicates. `D-08` (raise MEDIUM →
  HIGH, **FIXED A-067**) lives here and I did not re-verify the fix. **Not exercised.** I chose
  depth on E3 over breadth, and this file has had a recent independent adjudication.
- **`ts/src/propose/**` (encode.ts, index.ts, schema.ts, fixtures.ts)** — **assigned and not
  exercised.** I read no line of it beyond `grep`. This is the largest gap in my coverage. It is
  the LLM-facing proposal surface and nothing in my findings touches it.
- **`ts/src/tools/**` (sample-check.ts 343 lines, emit-samples.ts 649 lines)** — **assigned and
  only partially exercised.** I read the pipeline-ordering call sites (`R2-F2`) and nothing else.
  `emit-samples.ts` writes the seven committed sample bundles the D-010 verifier reads; I did not
  check that what it writes matches what it claims to write.
- **`ts/src/signer/server.ts`, `client.ts`, `keystore.ts`, `main.ts`, `socket-path.ts`,
  `eip712.ts`** — assigned, read only where the E3 path crosses them. The RPC framing, the socket
  permissions and the keystore were not attacked. `eip712.ts`'s golden typehashes were not
  independently recomputed.
- **The deep gate profile** — Reviewer 1 owns it, per my brief; a gate run (`pgrep -f
  sentinel-gate` → pid 69845) was already in flight when I started and I did not start another.
  **Every result here is from the FAST profile.** Anything visible only under the deep profile —
  the corpus stage, the committed-view comparison, the ablation regeneration — is outside my
  evidence.
- **A live-Anvil reproduction of `R2-F1`.** The straddle is proved at the code level and its
  consequence with a stub; forcing a block to land inside a millisecond-wide window on a real node
  needs an interleaving harness I did not build. Stated in the finding.
- **`verifier/**` and `fixtures/samples/**`** — Reviewer 1's surface. I read `verify.py:1659-1660`
  and `:255-265` only to establish whether the bundle-anchor route was already closed (it is —
  `NULL-RESULTS.md` N7). I made no finding there and did not run the verifier suite.
- **`contracts/src/SentinelVault.sol`** — Reviewer 3's surface. I read the four execution-path
  checks (`:311-315`, `:337`) only to answer whether a policy-rotation cycle defeats the nonce
  guard (it does not). No Foundry test was run beyond `forge build`.
- **The corpus and ablation** — Reviewer 3's. Not touched.
- **No live model was called.** No `.env` in the worktree, by design, so the Gate 7 canary and every
  model-dependent arm went unexercised — the same limit round five recorded at register §13.1.

## Coverage of the CLAIMS on my surface

My brief assigns "all claims and comments owned by those surfaces and the corresponding proposal
sections". I covered the comments in the eight source files listed above and the `decisions.md`
entries for A-072, D-053(b), A-074 and A-075. **I did not read
`Sentinel_Protocol_Lab_Proposal_v0_2.md`'s corresponding sections at all** (§3.1, §3.2, §5.6, §5.7,
§9). Three of my findings quote the code's *paraphrase* of the proposal rather than the proposal
itself, and if a paraphrase diverges from the source I would not have seen it. **That is a real
gap in an assigned area.**
