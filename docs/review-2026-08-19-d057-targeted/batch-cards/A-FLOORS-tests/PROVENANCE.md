# A-FLOORS — provenance and isolation record

## Frozen identity

| Item | Identity |
|---|---|
| behavioral baseline | `1a133301533e9d959dbafbbcc7ffe05e7eb78df3` |
| tree | `07cdc103133525f42b95018fabb802caa7cd8af3` |
| parent | `a0952264521f0f0755cb34b567877d496d8c1ec1` |
| timestamp/title | `2026-08-22T02:26:50-07:00`; `A-093: record C-SNAPSHOT implementation HOLD` |
| `scripts/test.sh` | blob `0c6c38ed746925d52720468865ca61eb31ae7ddd`; sha256 `66c272b90a16b037e3fcfc6f0d9184c48f63ac32e62538be7b6cd96a93801b79` |
| `scripts/check-suite-floors.sh` | blob `d69cc9a403719908139fdd660a126e254014d45b`; sha256 `c9a334dca2ce06e78a126e15dd33ef19bd0df3b43569eb0de76ea0b1c3ac13b6` |
| `docs/session-state.md` | blob `b91f548389a52b75b9796d3aaa975fc6e542dedc`; sha256 `2a2d0a4ce78cd06a8af38d80aa90f5c3eabb32968905ca18250f61e5fe54de2c` |
| frozen B-EVENTS test | blob `b601b0ad949a6c64b5ab53232fc00a9784e123a0`; sha256 `2a9219cc5138858b012b0bc56069490db3dd7d1963b73ccc19c28a48ce2b029e` |
| frozen C-SNAPSHOT test | blob `6a00cb9d674a5fe89c0e999149add7e25f7100de`; sha256 `29a673560e89b639b6635661706a368454c9969a04c5d37c4f6c15229df3dd8a` |
| signed Gate S2 pack | blob `baab3e7809a46f22131ef2b609f30af1ed8eeada`; sha256 `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589` |
| original evidence subject | `e8b4d29641c47f0099482c9a9ac5da86c9255197`; tree `3debee282acb37a23e0a5ba8eb38368ad5736d08` |
| independent Review-1 FAIL | `e3b8a76cff7a002b3211bb8f8a75f2d14b86a37e`; tree `bd3357e60d5f9b6cc5942a0f75eff38102349286` |
| preserved `INSTRUMENT-REVIEW-1.md` | sha256 `d07c6358127caba142b0c95adcba6fc33cb5b8eafdbba5c8680382a32d39c82d` |

The shared worktree was clean at the Review-1 parent. Corrected focused probes cloned the exact
review commit into private temporary roots; every source mutation remained there. The shared
repository correction changes only files under this evidence directory and preserves the review
record byte-for-byte.

## Governing and source material read

The workspace `AGENTS.md` and the complete operative D-058, D-059, D-060 and D-066 decision
entries were read before authorship. Relevant tracked materials:

| Material | sha256 |
|---|---|
| `docs/decisions.md` | `869f2d61e54a3dc70d13f6486d31c8b4d67a07131c2652cf267db04c26327e80` |
| R4-F4 `briefs/BRIEF-V2.md` | `b41521fae14e319d3bb6233639f4fdc37f54142447bfc71892a6fa25be250a89` |
| R4-F4 reviewer `REPORT.md` | `75397744e3087ec0396a5d7c8d81d7c67a2633053cdd0580125e236d8ff483af` |
| R4-F4 reviewer `PROBES.md` | `d27f0cc2629f5d35e6c95454ab8755518c21775f041eb3aa8a3301d7bc92d95a` |
| targeted adjudication | `bf1fdb1946aeafacf5e17faa0cc7adf1fab8229c708106f413c5c81dbdac8297` |
| `N-TESTSH-FLOORS` adjudication `ADJ1.md` | `5abc3bfc21503ee71c5588d42c2bd76833270ec45bd0b85dc48700bd187656a1` |
| new-finding disposition table | `5d581507b4eb74b2a1df216c2b8d0a8bdfc129e7b7c12af78e5b18ba19166988` |
| round-two `C3` adjudication | `3f131fe2b87809592c26a42016ae7a7f5288af8371ae8f66ea3e04c02e6068ef` |
| failed global contract audit, historical only | `7bf3e3d257053a3cd948cdbe77da0bccdfbffa9f42881c40337d34b31160eb4e` |

The failed global contract is not operative under D-060(1). It was read only for its independently
confirmed surface/ownership cautions and does not define this card.

The current `scripts/test.sh`, `scripts/check-suite-floors.sh`, full §3 and relevant live
D-010/COVERAGE paragraphs, B/C test files, prior B/C contracts and A-090–A-093 records were read.
A tracked search for all six names, the checker name, current count-shaped publications and Batch
D ownership produced the finite owned/excluded inventory in `CARD.md`. Historical reviews,
decision entries, signed packs and dated narration were classified as controls, not rewritten.

## Measurement identities

| Item | sha256 |
|---|---|
| Review-1 focused harness/matrix, historical | `4782ff0211ce64c5a6fb1c82b7faf6ea3b4118eea4fe218c38648386e235200f` / `a704290d198f14ab85db1a66149b5dd03ff3d7096ad04646f05f5c6980247ca5` |
| corrected focused harness, 712 lines | `827a4119f60ac97e20951d3a1b0b43a411b3bd2db48872cde754a700d584fc39` |
| corrected baseline matrix/raw | `f0ab8dcd63efe98bbacfc353dd0e849b6b9f91bbdccd6288fa90c80a524b63a0` / `d90500cd684d245bdc79324f3562a92cabbc935b79595e65976878322ba20931` |
| digits-zero sibling matrix/raw | `2094fba903c6ad9ef7f8be4cdba1bc5dfc0bc841b7f34fc70070b6787c6bf46c` / `2085505bdcd6db3004b5e82cb424da45cc658bcc47caf78ce3b7a522d6275e2c` |
| exact-positive control matrix/raw | `3db1d06abbcec760aa4ce80f68aacaed7ed17df3fc998adf3c74707b86695bdb` / `34980d90b09909c698abf7e8f2c88d02e81755325d03ba61325756fef2de0d11` |
| serial gate harness, 328 lines | `fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0` |
| gate matrix | `0b4d9c127e7230c7266960fe073f92f9551da9a68005cb936850993d803d1c58` |
| gate wrapper raw output, external | `c4a41ddc58b73c7c23932556a37c7c955968298553fcbbd94314c550c01a6cb2` |

The seven full gate-log hashes remain in unchanged tracked `logs/gate-summary.log`; gate design
and reliance limits remain in `GATE-BINDING.md`. They were not rerun for the focused-only
correction. Full logs remain external because the
pre-existing rename stage prints a machine-specific absolute repository path. Tracked summaries
and matrices contain no such path.

## Toolchain

- git 2.50.1 (Apple Git-155)
- Node v26.3.0
- npm 11.16.0
- Python 3.9.6
- Forge 1.7.1
- macOS 26.5.2 (25F84), arm64

## Preserved boundaries

- No production, existing test, script, gate, floor, maintained claim, prior evidence or decision
  file changed.
- `INSTRUMENT-REVIEW-1.md` remains byte-identical at the hash above.
- Both frozen B/C test files remain byte-identical at the hashes above.
- Signed Gate S2 material remains byte-identical.
- No test patch was applied, no floor lowered, and no historical record rewritten.
- No gate was signed/reopened; no claim was certified/ratified/published; no rename, push or
  D-055 assessment occurred; held D-008 questions remained unseen.
- No secret, concrete temporary path, session identifier or connector configuration is recorded
  in tracked evidence.
