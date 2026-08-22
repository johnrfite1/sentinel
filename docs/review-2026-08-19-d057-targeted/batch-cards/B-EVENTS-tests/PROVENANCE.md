# B-EVENTS — provenance and isolation record

## Frozen identity

| Item | Identity |
|---|---|
| subject commit | `46b62bea748b0dcdf6c02288659a3be1bbb945ba` |
| subject tree | `e5d6044d048b2ba56c6c4db8d9e08ad1bc5d2788` |
| parent | `a8921a118480fc1f492400858e1cbcd6c34a212c` |
| subject timestamp | `2026-08-21T20:59:31-07:00` |
| subject title | `A-089: record A-EXTRACT implementation HOLD` |
| frozen vault sha256 | `ea20f7ea110ab8da4c42e54255ca73268d12ec06471b88e502328683d0cc18a5` |
| pre-existing Solidity-test tree | `bc32ccf4c993853dfb0950a45ed5754c6ad77294` |
| pre-existing `scripts/test.sh` blob | `0c6c38ed746925d52720468865ca61eb31ae7ddd` |
| signed Gate S2 blob | `baab3e7809a46f22131ef2b609f30af1ed8eeada` |

The shared subject was clean at start. All source/test mutation, patch application, Anvil probes,
and top-level gate runs occurred in private detached clones. The shared repository received only
new files under this evidence directory. The author made no production repair and authored none
of the forthcoming implementation.

## Governing and source material read

| Material | sha256 |
|---|---|
| `docs/decisions.md` (D-058, D-059, D-060, D-066) | `c1863bed688359a55bed66faa505f05117bad9283718bbcbcd5f1254bf927fd9` |
| `Sentinel_Protocol_Lab_Proposal_v0_2.md` (§3.3(2)) | `322cd96fa7daf9840c34f6bf6cc0abd9b1d31a83ccfd5e9babb0f575e20c4124` |
| `docs/repair-protocol.md` | `9ffedf6c72553d032e88d4f0df840b67c8670a66bd2bb81e8f5b7c940b4ff9ea` |
| `docs/session-state.md` | `2a2d0a4ce78cd06a8af38d80aa90f5c3eabb32968905ca18250f61e5fe54de2c` |
| R3-F7/F7-R1 `reviewers/v1/REPORT.md` | `013e3d9db9bf3dcb61aca30a578ffdea9b60cc11034098dea8140bb8b08e2777` |
| R3-F7/F7-R1 `reviewers/v1/PROBES.md` | `79562d4a046f795a1308af601da4b91dfeea306b9859dfad72a73cd666b39abf` |
| R3-F7/F7-R1 `reviewers/v1/COVERAGE.md` | `3bc64b71f9e76c88f7e0591e0657fdfc6f1b2373762092b983f3dc07c10d2710` |
| F7-R1 adjudication `ADJ1.md` | `5abc3bfc21503ee71c5588d42c2bd76833270ec45bd0b85dc48700bd187656a1` |
| adjudicated-new-findings record | `5d581507b4eb74b2a1df216c2b8d0a8bdfc129e7b7c12af78e5b18ba19166988` |
| signed `docs/gate-s2-evidence.md` | `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589` |

The complete current `SentinelVault.sol`, all six current Solidity test/harness files, and
`contracts/foundry.toml` were read. The vault sha256 and the tree that binds all six test/harness
files are listed above; the frozen `foundry.toml` blob is
`45136cc2343dc49c3511e666491e7cd4d0b44458`.

## Toolchain

- git 2.50.1 (Apple Git-155)
- Forge 1.7.1, commit `4072e48705af9d93e3c0f6e29e93b5e9a40caed8`
- solc 0.8.28 via the pinned Foundry configuration
- Node v26.3.0
- Python 3.9.6
- GNU bash 3.2.57
- macOS 26.5.2 (25F84), arm64

No secret, credential, concrete temporary path, session identifier, or connector configuration is
recorded in tracked evidence.

## Preserved boundaries

- `TESTS.patch` is not applied in the evidence commit.
- `NATSPEC.patch` is not applied in the evidence commit.
- Existing product tests, scripts, claims, signed material and prior evidence are byte-untouched.
- `docs/gate-s2-evidence.md` remains sha256
  `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589`.
- No gate was signed, approved, reopened or ratified; no claim was certified; nothing was pushed,
  published or renamed.

## Measurement hygiene

One early development sweep invoked Forge from the super-repository directory. All rows failed
dependency resolution before compilation. That run is excluded completely: zero behavioral
catches were credited. Two later development sweeps were superseded when self-review strengthened
the frozen oracle first with an explicit recorder limitation, then with exact extra-event and
indexed/data-layout discrimination. Only the final bytes identified in `CHECKSUMS.sha256` and the
final matrix in `mutation-matrix.tsv` support the verdict.
