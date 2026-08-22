# C-SNAPSHOT — provenance and isolation record

## Frozen identity and correction chain

| Item | Identity |
|---|---|
| behavioral baseline commit | `1655b120a653b60ccb5b3a22583c0001d59ea7a4` |
| behavioral baseline tree | `b2c8fb1e53d35ea40655dc83faa61f8a76dd4f78` |
| behavioral baseline parent | `060af4ee1ff1718edbf7772dc15050ccb88b3d29` |
| baseline timestamp/title | `2026-08-21T23:25:48-07:00`; `A-091: record B-EVENTS implementation HOLD` |
| original instrument | `30d1466cde0e47899740818e574a75e575d75b9d` (tree `09c29b98b17468ba937c8c6a87094a1ea1215b71`) |
| independent FAIL review | `8834d9b868657fbccfe1009bf139e23dc8e06db1` |
| preserved review file | sha256 `ffad26f2c8307aa7fcf9e2c7e18dd971eace47b955132f65222bbb1c335febf0` |
| corrected `TESTS.patch` | sha256 `c2a53a4707d62c3e6632405037d684216c8319dd79fdaad15da2c15de6c69de1` |
| corrected extracted test | 485 lines; sha256 `eea8876c38545db864df36f8d75e7a10e53b47ee730d805dc4ed984f88d6c1f7` |
| corrected mutation driver | 270 lines; sha256 `223e784d3804aad8fb7e9a12424c94d19a60418ad4905c3959bcfc707123b4f8` |
| frozen `vault.ts` sha256 | `dbff956fc2fdf6698e6c94ce4261626dc40cf219b6095ff8afcda8afcadc1185` |
| frozen `protocol.ts` sha256 | `87fc5204c561d986c04cc61eb4ae9e880db113187707f7e92e2df7a334b29b33` |
| pre-existing TypeScript-test tree | `e29397245dadfe8c9250905d99c26c036013aacf` |
| pre-existing `scripts/test.sh` blob | `0c6c38ed746925d52720468865ca61eb31ae7ddd` |
| signed Gate S2 blob | `baab3e7809a46f22131ef2b609f30af1ed8eeada` |

All patch application, source mutation, focused tests and top-level gates ran in a private
detached checkout. The shared repository received only bounded corrections to existing files
under this evidence directory. The first independent review record is byte-untouched. The author
made no production repair and authored none of the future Batch C implementation.

## Governing and source material read

| Material | sha256 |
|---|---|
| `docs/decisions.md` (D-058, D-059, D-060, D-066) | `6afa15bcb9beb68b2c5ade5de3201c1aa1246ff61a2b7a435b139ff21e6725e4` |
| original R2 `REPORT.md` | `a943169109c3ace07309002a22ff6978501c1f4cca8a66d7486d85eda909f6b2` |
| original R2 `COVERAGE.md` | `608cc07c4cf1dfa60c044db3b2e6d86540ecd2078018173679b7e76d545dc3c0` |
| original R2 `NULL-RESULTS.md` | `5bcc7a56959dbed3e00933fe5714cb5311653b700b2a56cd6d2df2b71859f12f` |
| original R2 `ATTESTATION.md` | `deca26b61079eb80500e4ea32ebbd1d1c3b275f62463199d70ad2bb25491bd16` |
| original R2 `DEAD-PROBES.md` | `fbb4044c00daf3b4c7999fc440035b16b482b597c1a0734f2033df53c8c3c499` |
| R4 adjudication of R2 | `b19664ec3e2d448086e2e45888d44ecacbae9265095294a70b0561915fa44bcc` |
| targeted `BRIEF-V3.md` | `98d57f5d37251284ccfc098773366a749fbfd5ffa288695b4ed1ebf1a11cb8a8` |
| V3 `REPORT.md` | `fe397f3cf392b6fd59401a3858b284e76382b013e1079ff2dcd389265d9ee6ad` |
| V3 `PROBES.md` | `ee6a8ba3b4c5cd9b34c030c84ba405be087bef0751b286847c625a80bd2cdafa` |
| V3 `COVERAGE.md` | `340c185575de436fc92362d264669b6fe152b7ee35820f48feb4dc5d9fb12d62` |
| targeted adjudication record | `bf1fdb1946aeafacf5e17faa0cc7adf1fab8229c708106f413c5c81dbdac8297` |
| C5 ownership adjudication `ADJ4.md` | `6eb1175afce5d8611f81a6c215e63b51aa9523951c3144c02178949a617cb9e7` |
| failed historical contract v1 (branch matrix evidence only) | `895cc7a981e748f8c0431cef475d41e761ef0e185aa2604f7f95cbb22e3de7b2` |
| failed historical contract v2 (D-F6 ownership evidence only) | `2f73e6653482b030a431a05e761a1292591ec151487d700adc215eb1370b7baf` |

The failed global contracts are historical evidence, not operative contracts. Their branch and
ownership facts were re-derived against the current source before use.

The complete frozen `vault.ts`, `attest.ts` flow, `protocol.ts` reason/error commentary and wire
types, signer startup/status catches, `vault.anchor.test.ts`, `reasoncodes.test.ts`, `fakes.ts`,
and the TypeScript test glob were read. Relevant hashes:

| File | sha256 |
|---|---|
| `ts/src/signer/attest.ts` | `fb8d90a3788eb4dddead249496e2b3934b6e2a376594bb2841029c560d957e96` |
| `ts/src/signer/server.ts` | `ad4b1c52f8fdddf8de1b3ea18ed8ec0b1b1881c9032f40d5c8165e812617be59` |
| `ts/src/signer/main.ts` | `c1e78a21d554a74e28b18f1b75cba899ea65b1c2c70f93f899a5162ccc96121f` |
| `ts/test/vault.anchor.test.ts` | `8e7200d30f6c4a7ca49b6045196cbff83b24d6b4ad83ff7545dfdfa7779d58cd` |
| `ts/test/reasoncodes.test.ts` | `c14332021350aeccd0afc6eb706040e31c0188537a4d22cbf7657d95306e1f19` |
| `ts/test/fakes.ts` | `e3b2a417a545e2d7bd17cf2e3311a22d1d6cfdf710aa0368a87b6c8a86775881` |
| `ts/package.json` | `a22d252c3bea4e082768fa8eaf6e9aaced076b0e06100fe41a1bddba8578ecf4` |

## Toolchain

- git 2.50.1 (Apple Git-155)
- Node v26.3.0
- npm 11.16.0
- TypeScript 5.7.2 from the frozen dependency tree
- Python 3.9.6
- Forge 1.7.1
- macOS 26.5.2 (25F84), arm64

No secret, credential, concrete temporary path, session identifier, or connector configuration is
recorded in tracked evidence.

## Preserved boundaries

- `TESTS.patch` is not applied in this evidence commit.
- `INSTRUMENT-REVIEW-1.md` remains byte-identical at the preserved sha256 above.
- `ts/src`, existing tests, `ts/package.json`, scripts, floors, claims and prior evidence remain
  byte-untouched.
- `protocol.ts` remains outside Batch C ownership and unchanged at its frozen sha256 above.
- `docs/gate-s2-evidence.md` remains sha256
  `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589`.
- Nothing was signed, approved, certified, ratified, published, renamed or pushed.

## Measurement hygiene

The original contract's one mutation typecheck invoked from the repository root remains excluded
historical measurement; it exited before any test and is not reused. Every corrected final
mutation used the exact corrected test source and `npm --prefix ts run typecheck`, exited 0, and
then ran behaviorally. Raw path-bearing outputs were hashed outside the repository before tracked
summaries were written.
