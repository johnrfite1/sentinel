# A-FLOORS — seventh-corrected measured pre-repair results

## Verdict

**HOLD for seventh-corrected test-contract readiness, pending fresh independent Review 8.** No
production repair, post-repair pass, approval or gate replay exists.

## 1. Identity

Review 7 FAIL `0e90836057174052c13327fa5410f58a92550ad0`. Reviews 1–7 and earlier matrices/logs
are byte-preserved. Harness 1140 lines, sha256
`47cb61ccef462f75131259c7af2b22c12911c86347c898653d50062bf8b717b4`. Runs used that external
harness against a clean clone of `0e90836`.

## 2. Baseline

REQUIRED 4/131, CONTROL 218/218, exit 1. Raw/matrix:
`ec0d66e240d7ad2382d8ddb1375e32e4d173364c0464dc0b694244e8aeb1d23e` /
`82e0e80e849190807576ddb079795dfeb86595eb517c035ed28a848023c23684`.

## 3. Uncorrelated siblings

Six live siblings (two-line, oneline, compact JSON, pretty JSON, commented pretty JSON,
same-record inventory) each return REQUIRED 41/131, CONTROL 218/218, exit 1, failing exactly the
90 named-duplicate rows. Shared matrix
`b83e49acb5a483d9507b4ae4e31edfc0f53ffd767cf3d40b0dabfca81fd30308`.

| Sibling | Raw SHA-256 |
|---|---|
| two-line | `c066b05fb53d6e2520d6daaea170319bbfa37300321b7232d315ad9f137f903a` |
| oneline | `71e7218bb77b0a67970f6a253482de30fa09d6b6d9f25ffa3c56345db1a1aa7c` |
| compact JSON | `f5e77cc46111b38b20ae0e753a1c8c8c701e88656e3d91e7fb596760e1229348` |
| pretty JSON | `25ede00dcb2d10640cb0117e6a9cdba9f00c2411b5113e94ebae1d2b71420e96` |
| commented pretty JSON | `23079c36c5d1f56d442b19fdc2f3569fc12e2377f7861ff313e8d050ff8878c6` |
| same-record inventory | `3f530e8d6166436f5b779f1a7abac83fdc4e7cc977d8d1390c16fcede7a92387` |

Forty-four `DR-*` controls pass, including `DR-prettycomment-*`.

## 4. Other variants

| Variant | REQUIRED | CONTROL | Exit | Raw | Matrix |
|---|---|---|---:|---|---|
| digits-zero | 125/131 | 218/218 | 1 | `11b251c00193907c38b3f62fb89d66b553165761b1937fc95f9961fc9bd5e6c4` | `fec03d43fe4cc392fe8765119d651d971e06db853ebbc676b89d4290f518ae47` |
| Review-2 raw | 83/131 | 178/218 | 2 | `4033c3c34958760041368fd0921e38fc2c36365e92a5b2501d83d12771eaee5b` | `0696db2d63fc9779e7038d0e4615ad92e748ff9845e6cd2e84a539999364c7c9` |
| Review-3 | 131/131 | 170/218 | 2 | `bdc01cf527aa788ed588f3bb4174169942fb3e1903b70a7c88c6ec47ee8750bc` | `57584faa5b4a2aeb8d03db41e354ba236e11082d31d5d062daceefd3be7aa2b2` |
| all-token | 131/131 | 164/218 | 2 | `eef8d7c7b90e62a1f3872216f91339319ac4394492c5f78dc502f88427fce65d` | `eb398f4b816e395c277346d4ad104f295fd62ff982da81786bc011372111407b` |
| exact-positive | 131/131 | 218/218 | 0 | `622544caaff1acdb75d07a81cd05a6527ba56efec532955514a847657e4899a0` | `69825cc0e41a11cc359c66968f5920160f215d2a0c2f2b62e6c06a4dd99aeed0` |

349 unique names. Gate harness/matrix unchanged; not rerun.

## 5. Limits

This establishes only the exact finite grammar in `CARD.md`, including Review 7's commented
JSON-wrapper hole. It is not implementation, certification, signing, publication or D-055
closure.

## 6. Guards

Before staging, repository guards all exited 0: worktree secret scan, review scope
(`R1=491`, `R2=47`, `R3=152`; 690/690 then-tracked files assigned), findings ledger (23 IDs;
totals match D-057), live suite-floor reader (`92/527/221/7/78/30`) and vendor-honesty mechanical
conditions. With the new v7 matrix/summary files staged, the staged secret scan was clean and
review scope again exited 0 (`R1=515`, `R2=47`, `R3=152`; 714/714 tracked files assigned). The
workspace guard exited 0 with 13 machine-state findings, all 13 baselined and zero new.
Workspace success remains ratcheted: pre-existing findings are not absent.
