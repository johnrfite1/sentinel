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
| first correction | `69e4fda92401e29c0cd4c717538fc278a5e59e26`; tree `fc5c63583be28683b53ced20ccc42f697d1494bc` |
| independent Review-2 FAIL | `9889289cb730a7ef23b2b9d11c0e84110dce84f6`; tree `f82ec033136c383cfad667497f06bc5b1e588c43` |
| preserved `INSTRUMENT-REVIEW-2.md` | sha256 `978d09f669cb6c5037d0de0e903f678ea7015f394670692698305b2f821ae7ae` |
| second correction | `12a35d2c3f30c77250b3ebde0bf82c25591dce10`; tree `b75b7173793b2ea31305698d43a0d81f147e2540` |
| independent Review-3 FAIL | `cd12ac26fb718a9bd02971db1f09f4fe1189bba7`; tree `6da663764db80488e67e49e8505b4d9bd2106e02` |
| preserved `INSTRUMENT-REVIEW-3.md` | sha256 `27e8e8da48fe34a07c750023296c11b82d937279f65b058fe4c5d2e78523bf86` |
| third correction | `fa92ff7729287b10d6e140a6955b9740248600a6`; tree `e01f89342315611f42edd42ee6400b34ea0da56e` |
| independent Review-4 FAIL | `0bf739b5be645abe6c8171c005a7181aaaadc5c8`; tree `2b7265c78e549ba290f0ec2c138c7bc5718b7fcf` |
| preserved `INSTRUMENT-REVIEW-4.md` | sha256 `cfdf80b4c49a5716565fae5254652174c360226e005720402aaba8fb37d28437` |
| fourth correction | `178347dbf33ab70923a6fd0278ea61c5dec5e6b6`; tree `1b5f028aa217da5e389c28a062d43b5350c60d96` |
| independent Review-5 FAIL of record | `30d6257f806276a24cb6a40319b5bbb858fa9a5d`; tree `80769f8b18ab3b716bb51d40463e153a840c10e6` |
| preserved `INSTRUMENT-REVIEW-5.md` | sha256 `4d742aded60fce42d30ec49dbb4d7a443fe0f0dbfc04ab9cafcc06987c4bd6fa` |
| concurrent independent Review-5 FAIL | `bd0c43321e7bb2e8200513fb4e97666fccdab697`; tree `846c19667cff38edb2a8f8976cc82c50ccedecdd` |
| preserved `INSTRUMENT-REVIEW-5-concurrent.md` | sha256 `10bc8231f5d9e3f309a3bf87190d1340f60176c8fdc1644bb1bf8bd2e585dbb7` |

The shared worktree was clean at the Review-5 parent. Fifth-corrected focused probes used the
external dirty harness against a disposable clean clone at that exact commit; every source
mutation remained there. The shared repository correction changes only files under this evidence
directory and preserves all five review records, the concurrent Review-5 blob, and every earlier
matrix/summary byte-for-byte. Two reviewers committed `INSTRUMENT-REVIEW-5.md` in succession
(D-037); both FAILs name the same hole, and both blobs are retained.

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
| first-corrected focused harness, 712 lines, historical | `827a4119f60ac97e20951d3a1b0b43a411b3bd2db48872cde754a700d584fc39` |
| corrected baseline matrix/raw | `f0ab8dcd63efe98bbacfc353dd0e849b6b9f91bbdccd6288fa90c80a524b63a0` / `d90500cd684d245bdc79324f3562a92cabbc935b79595e65976878322ba20931` |
| digits-zero sibling matrix/raw | `2094fba903c6ad9ef7f8be4cdba1bc5dfc0bc841b7f34fc70070b6787c6bf46c` / `2085505bdcd6db3004b5e82cb424da45cc658bcc47caf78ce3b7a522d6275e2c` |
| exact-positive control matrix/raw | `3db1d06abbcec760aa4ce80f68aacaed7ed17df3fc998adf3c74707b86695bdb` / `34980d90b09909c698abf7e8f2c88d02e81755325d03ba61325756fef2de0d11` |
| second-corrected focused harness, 859 lines | `fb9577d3182cc881e4c2c4f5bca9c02d1ddf8ed04bd64d9f85e0db4d0985896d` |
| v2 baseline matrix/raw | `26039eccc906f3db9a5d8f97c7710e17fe6e007187c5503fcfd54fb16b9eaf35` / `a18333f67c4405af8b86aa7d6f4cfb9f94df380d31ae4744174cd40701f069e4` |
| v2 digits-zero matrix/raw | `93444b6b196518050ef16948743459112f1550ca7008a6a231cf9d42ae26ec08` / `6b11d16b4d56040e78b2305b5bdc95a3be18451ee5fbb3c8899f3ff57d7f3350` |
| v2 Review-2 raw-reader matrix/raw | `a49891dcfcfc5da17e0003a7ed1148901d7437d123e8e2b6347d4c6575babfc7` / `33a0b2d3b12cdb8f89b2b45b30774baee93f488797573b11033d056c5178fbc4` |
| v2 exact-positive matrix/raw | `5d390a4fe8a1600d3430abb340e28e0f0f22e3389ad2f87e61636fa49a9244c1` / `9044d8e72217b9bc03c023ff109b22663852c12f07d45f38bed70359efa84fd9` |
| third-corrected focused harness, 926 lines | `4bc09b9c4f835f28fcfc114a6f9b78c6bb3e102d3513eae545bdb1ad5996bb80` |
| v3 baseline matrix/raw | `98a3f66489827f8632be5b32395d2e02841fc456099f5f179e213eeda71f95ca` / `cb2e9e89edc3d032483a5241df06d7d0fcae499de49c85acd3f40d763061d7f4` |
| v3 digits-zero matrix/raw | `bbeaaf8a18d4ee08e9990b339ea3e5f426d19c3198adcfb9ae6ca9c27761c3e1` / `d9f08c88bed66e38b6789114fd4a20d7da104d5c2d138097e7ec6d935c67f47e` |
| v3 Review-2 raw-reader matrix/raw | `9456409625b1f49570c34580adbe1c0b7fc45d834965cfdeb3710d80aae97ecf` / `65e1cf30e3c123a5485741e8544d3da6e45a6225d8ee73827046628bb85a778d` |
| v3 exact Review-3 non-comment matrix/raw | `feb1ede79e3cff8ca38d34e1a747116daeac73589c982fa12be1781c2347f2f4` / `b7950c4b1e4ca075ca6a32e525f5e1ea108f6c205cd6f862c378871e3eea101e` |
| v3 expanded all-token matrix/raw | `c9f40f79b8acac473701a1c17d2d928a93905369bbe3c41734c29afbaa4f5101` / `6e9daec8628d84707d1f7b1485fd85d1f6ca4eb29e7bb26071329f83e020ef2f` |
| v3 exact-positive matrix/raw | `15e53549138fb45d19c8b89d8f2dd676abdeb576aa735b195c20218e858bfe2d` / `a3a1c390ab03a53d19596d473fcbdfc3b38852d5775a3f7a1edc6ee45685bf16` |
| fourth-corrected focused harness, 975 lines | `b751b0b643c6dc28f484ca80845bd4d453e31bb85fd61a70ded68b898016df33` |
| v4 baseline matrix/raw | `81049470ca4a7d36385bf82a231395f85b039d7b682bc89ae4108602b84396f1` / `33a241ca6c9dffec52b9f0a8d9fe2a741ac6c02675ba01444f6f1b2ce6524192` |
| v4 digits-zero matrix/raw | `9e7982aea1c4930ba4df535cf6d136c322c1d03eb1f3792217efb712d87956e3` / `351350c6583f2101e34ce822c1a922a477676080dcf3d1d489293af204ef548e` |
| v4 Review-2 raw-reader matrix/raw | `3842c0d9e28880859b66b27d662912be190be0e9fc9b26882aa6db752399627f` / `2314126ce6cc5ffae241f76825ea377a327c99dfa51f6cf5c4b38ed67378973e` |
| v4 exact Review-3 non-comment matrix/raw | `a258ba787faad740bf7ac98813701f261ddac73a89fcea0f6a7cf05ff77d1618` / `634c0b999268a453923f1868ba46cd3e1a3a79064dc01af3653bf8f0711f9f68` |
| v4 expanded all-token matrix/raw | `1ff40412804a481264dd01cb0bf74164e5104e66291403ae5f06ac299128e600` / `b4dd45521ede35165a532725a4c4a1573905898dac516c200f96fdb63ff0be1a` |
| v4 uncorrelated-diagnostic matrix/raw | `15c540c565050b427d4e97486ba34a2d7d020aede82d2aa6e61e2086820f3be9` / `6c6bc07ca9b59bb9214dcaa865cc6c9926e4addd54bad906bc0ad9691a1c908b` |
| v4 exact-positive matrix/raw | `63dbb5577a5a9d40c5f4df06367f77901305d26e858e6d16386c4118451e1ff5` / `d8d3a9b9f5c1c63c16bca04131b1c17d755a72da2a99794aafd980d0bbe7c809` |
| fifth-corrected focused harness, 1035 lines | `3f347ecf482b7f249275dec87b70c6f94f9a3b3a329a4dd02e4db4a68742a42a` |
| v5 baseline matrix/raw | `b7dabf0e3ea0ede2c0fdf6bca70feeafa2d911b77e55c06e8db625078f1283e0` / `242d0098cbf8045ce52e80c12f376581d2c3e01ac1ae11b1316ba093aa80f217` |
| v5 digits-zero matrix/raw | `3eac8a9e4657f518870ce53110c23ad4f97b229e689629184dfe712d40aab62b` / `7748cc056b7adcfff77a24a1ad0aa9abd1008a7edf759d2df1c7845b334fc84b` |
| v5 Review-2 raw-reader matrix/raw | `16766991f633d81c8753cc2502475b90a9ca81b5f533aefbd90615ee7013d7c2` / `c388f7404f15c515289f1c25c1c6c2e47f2f3198e48ee999ad7c987f9f64e798` |
| v5 exact Review-3 non-comment matrix/raw | `325b2323d55acbca4da494f11c82e617317c97fbfeb8fb96fab9745f9b9cce6d` / `49ff71ac22da4683fc90d77366749078b2d4c9f19a03733749e557f413c5c17f` |
| v5 expanded all-token matrix/raw | `1b7d8c79585314734ee48f0ad932541fb15255e63c1eed673fd6d8c671f462d5` / `104e3b732562ce4acf9f5a326ef69c60cc86f3b3cdb9598e392f89912a0fc21a` |
| v5 two-line uncorrelated matrix/raw | `b464ae62dcff31da51f5bd6391b7bc8c35c17e39fb540aa03a6c39162b522e2d` / `8b24e85949063a041aced443937329d1bfca8d9a7499a4191f0d4b8a5152f36b` |
| v5 oneline uncorrelated matrix/raw | `b464ae62dcff31da51f5bd6391b7bc8c35c17e39fb540aa03a6c39162b522e2d` / `99edf1dc6d2789cd30c57ad16460fa391f70c86b5d2c58fc6560c86ef2f2de5a` |
| v5 JSON uncorrelated matrix/raw | `b464ae62dcff31da51f5bd6391b7bc8c35c17e39fb540aa03a6c39162b522e2d` / `1598e55137f9a5a49e2b5ffde0339d74d5aa84f0295384cc8006fe8ebb5942e6` |
| v5 exact-positive matrix/raw | `ea972bff0f769c8acb177134d1ce5ddbcc03fcc18d89d704af2579f10d5e212a` / `c362678e42aa26d67ad1206cff5b5077cae6969c375f751417c02dc374278adc` |
| serial gate harness, 328 lines | `fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0` |
| gate matrix | `0b4d9c127e7230c7266960fe073f92f9551da9a68005cb936850993d803d1c58` |
| gate wrapper raw output, external | `c4a41ddc58b73c7c23932556a37c7c955968298553fcbbd94314c550c01a6cb2` |

The seven full gate-log hashes remain in unchanged tracked `logs/gate-summary.log`; gate design
and reliance limits remain in `GATE-BINDING.md`. They were not rerun for any focused-only
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
- `INSTRUMENT-REVIEW-1.md`, `INSTRUMENT-REVIEW-2.md`, `INSTRUMENT-REVIEW-3.md`,
  `INSTRUMENT-REVIEW-4.md` and `INSTRUMENT-REVIEW-5.md` remain byte-identical at the hashes above.
  `INSTRUMENT-REVIEW-5-concurrent.md` is the exact `bd0c433` review blob.
- Both frozen B/C test files remain byte-identical at the hashes above.
- Signed Gate S2 material remains byte-identical.
- No test patch was applied, no floor lowered, and no historical record rewritten.
- No gate was signed/reopened; no claim was certified/ratified/published; no rename, push or
  D-055 assessment occurred; held D-008 questions remained unseen.
- No secret, concrete temporary path, session identifier or connector configuration is recorded
  in tracked evidence.
