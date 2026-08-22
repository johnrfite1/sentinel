# D-CLAIMS — independent final implementation verification

# VERDICT: HOLD

The exact implementation candidate
`491c035c67f4267f7c2fad1ceb74937835515387` holds the third-corrected frozen
D-CLAIMS contract. The candidate has one implementation attempt. No correction attempt was
needed. This is a HOLD for this exact candidate and declared five-surface inventory only; it is
not a gate signature, approval, certification, ratification, publication, rename, D-055
assessment or push authorization.

I authored neither the D-CLAIMS instrument and reviews nor this implementation. I changed no
production source, test, instrument, prior review, gate, floor, maintained claim, decision or
signed material during verification. This standalone record is the only tracked review change.

I tried to fail the candidate on scope, NatSpec/comment/§7/§11.0 fidelity, pre-repair still
failing, candidate `baseline` completeness, per-surface causal revert, signed-pack leak,
`RefusalRecord.detail`, a new public reason code, interior/split and extra-tilde D-F1
spellings on the repaired tree, frozen hashes, and TypeScript executable residue. None of
those attacks held.

## 1. Frozen identity, scope and patch fidelity

| Item | Independently verified identity |
|---|---|
| implementation candidate | `491c035c67f4267f7c2fad1ceb74937835515387` |
| candidate parent / Review-4 instrument HOLD | `c79b1592d2c7e9a750c5a5da5bd985d6b390b6cc` |
| candidate tree | `21be52892078a7c7cddeee772ec3c2eb30433052` |
| candidate subject line | `D-CLAIMS: repair five maintained false claims` |
| held instrument review | Review 4; review-file sha256 `faa57770a206fbe8f5f58ff4da1bfb6a0602c6d2ff16989fc88eafeaf6b8ebd5` |
| focused harness `d-claims.py` | 665 lines; sha256 `9ec0307c3743a34a73b522e4ede0a31b3c50dee438269c1e2ec3827d9f4f741a` |
| behavioral baseline (pre-repair) | `1e7761be051422ad8091b203df375ddcfb7d1208` |
| D-058(9) attempt | one of two; instrument corrections do not consume an attempt |

HEAD, parent and tree were resolved with `git rev-parse` on the live branch and again on a
disposable `git clone --local --no-hardlinks` whose `git status --porcelain --untracked-files=no`
was empty. The live worktree had dirty `README.md` and untracked `assets/` / `.serena/`; I did
not touch, stage or commit any of them. The copied harness refused the dirty live source
(exit 2, `source worktree has tracked changes`). Every focused and attack invocation used that
`/tmp` copy of `d-claims.py` against the clean clone, passing an exact 40-hex subject.
Author `RESULTS.md` was not used as evidence.

The exact parent-to-candidate diff is only those five authorised paths (12 insertions, 19
deletions). Instrument files, Reviews 1–4, `CARD.md`, `RUNBOOK.md`, `RESULTS.md`, signed Gate
S1, S2 prefix, floors checker, B-EVENTS and C-SNAPSHOT tests, `scripts/test.sh`, and every
other tracked path are byte-identical to the Review-4 parent. `git diff --check` on the
candidate is clean. There is no sixth file.

| Surface | Change (measured) |
|---|---|
| `ts/src/signer/protocol.ts` | NatSpec on `SIGNER_CHAIN_UNSTABLE` only: live `so the refusal detail now distinguishes them` replaced by frozen `D6_TRUTH`. `(a)` / `(b)`, `D-057(4)`, and `SIGNER_CHAIN_UNSTABLE: "FATAL"` remain. No `RefusalRecord.detail`, no reason-code split. |
| `ts/test/evaluate.checks.test.ts` | Comment only: `` `EVAL_ACTION_TARGET_MATCHES_MANDATE` must PASS. `` → `` `EVAL_TARGET_BOUND` must PASS. `` The asserted code was already `EVAL_TARGET_BOUND`. |
| `ts/src/decode/index.ts` | NatSpec only. Both `D4B_TRUTH` fragments present. `D-014 deliberately kept conformance out of the signer` remains. |
| `docs/exit-criterion-packet.md` | §7 BLOCKER 1 and NON-BLOCKERS only. `D1_TRUTH` in BLOCKER 1; closed isolated `~~` strike of `it does not.` and `this alone blocks exit`; `The six §11.0 accepted limits`. Remaining item 1 under the BLOCKERS heading is the CARD's `D1_NEW` text, not a new defect. |
| `docs/gate-s2-evidence.md` | §11.0 only (after `## 11. What is NOT in evidence`). Full `D2_TRUTH` including `` `D-09` is in both the fixed and accepted sets ``. Closed isolated strike of the FIVE heading. Prefix bytes unchanged. |

Applying the frozen harness `apply_all` to a clone of `1e7761b` produced five files
byte-identical to the candidate (sha256 match on every authorised surface). The product commit
is that recipe, not a second wording.

Candidate production hashes:

| File | blob | sha256 |
|---|---|---|
| `ts/src/signer/protocol.ts` | `23795f2b2a5b76739efdb0cefd36ff926fefb515` | `84b3eb8d5ef05ebfe9e0b593e95b1aa9105a382b1264723cb75d84ea49a2c584` |
| `ts/test/evaluate.checks.test.ts` | `d6c3cf0aead02e818a39273d077a72f6a9d99b39` | `669aa31601f2c51bbacd04c8a050966b696d09ea496b351d1d4305ad726ca1c3` |
| `ts/src/decode/index.ts` | `481b8b0847fcab973eb3f47c051ba9bbfdc9451b` | `1947ee42941e0aa65e38d7d9af6caf1d36067823b8b25d28e3c750586f597add` |
| `docs/exit-criterion-packet.md` | `06bb842c48d9eeeba43b7d58c1d9a0a4a2e75cb3` | `2918b15154e6450198a2ae11f4d49a402c71d076eaec577f5b678657047d0f69` |
| `docs/gate-s2-evidence.md` | `bcd9536826cef8dc7da67cd2380959ef0966cd1d` | `69c586d43b27df6103b4160ace285af1d9eb356838e12f4212be44d1e2c2a1ca` |

Parent hashes remain the Review-4 freeze: protocol `87fc5204c561d986c04cc61eb4ae9e880db113187707f7e92e2df7a334b29b33`,
checks `0180a0677d693afc8e2256c62ebf051842b8dd82bfed5f46bc096dacce7fe4ad`,
decode `da5d92966da22df00eaf347a96d7548c034af059db1385ed4b60177f21733c4d`,
packet `ae8e5a5b42fcdaebd432b93d17a99b8312b261af459eff3f782a2c0c311a81ee`,
gate-s2 whole file `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589`.

## 2. Independent implementation reading

`protocol.ts` still exports one `SIGNER_CHAIN_UNSTABLE` FATAL code. The signed `RefusalRecord`
body still has no `detail` field. Distinguishing text for (a) moved-head versus (b) hashless
head is stated to exist only on `ChainUnstableError`, which `attest.ts` does not put on the
wire. That is comment text; comment-stripped TypeScript residue of `protocol.ts` is identical
to the parent.

`evaluate.checks.test.ts` still calls `outcomeOf(..., "EVAL_TARGET_BOUND")` and expects
`"PASS"`. Only the preceding `//` comment changed. Comment-stripped residue is identical to
the parent.

`decode/index.ts` NatSpec now states that the D-010 verifier compares `normalizedAction` /
`expectedEffects` to the presented action and mandate, and that Register E4 is verifier-half
built / signer-half deliberately not built. The D-014 signer-exclusion sentence is unchanged.
Comment-stripped residue is identical to the parent.

Packet §7 BLOCKER 1 keeps the signed S1 pack as item 1 under the BLOCKERS heading, strikes the
two live false clauses with closed isolated `~~…~~`, and inserts `FALSE SINCE A-074; THE
COMPARISON IS BUILT`. NON-BLOCKERS read `The six §11.0 accepted limits`. Gate S2 §11.0 replaces
`Ten minus the five fixed leaves six` with the full `D2_TRUTH` string and wraps the FIVE
heading in one closed isolated strike. Bytes before `## 11. What is NOT in evidence` are
unchanged.

## 3. Independent focused reproduction

Commands were run against a disposable clean clone of the exact candidate. Variant
`D_CLAIMS_VARIANT=baseline` (no `fix-all`). The focused harness was the frozen Review-4
instrument (hash above).

Candidate `491c035c67f4267f7c2fad1ceb74937835515387` `baseline`:

- exit **0**
- REQUIRED **14/14** (every named row PASS)
- CONTROL **26/26**
- completion token `D_CLAIMS_FOCUSED_COMPLETE`
- zero FAIL rows in the produced matrix
- measured matrix sha256 `28c30a8dcf97f4c440e4e1bbe2de2fd0ec67776eec67f7de62af146cd5dc4cb6`
- measured raw-log sha256 `554a9c85fec4a6da437d5958dc704003476cbaf16627d428a1849c939c217ae7`

Named REQUIRED rows inspected, not inferred from the total: `R-D6-absent`, `R-D6-truth`,
`R-D4a-absent`, `R-D4b-neither`, `R-D4b-open`, `R-D4b-truth`, `R-D1-absent`, `R-D1-blocks`,
`R-D1-truth`, `R-D1-ten`, `R-D1-six`, `R-D2-absent`, `R-D2-five`, `R-D2-truth`.

Pre-repair `1e7761be051422ad8091b203df375ddcfb7d1208` `baseline` against the same harness copy:

- exit **1**
- REQUIRED **0/14** (every named row FAIL)
- CONTROL **26/26**
- completion withheld
- measured matrix sha256 `d62568ff732e532eba2fb81a2d8a562f5fa1b1870b9a37280561b9c947d3ee99`
- measured raw-log sha256 `56f3b950736bf2fc32a706fc26fe4f635526b3bf6c0f74287e4f7fec1f7170b8`

## 4. Causal reverts and candidate-specific attacks

Each attack mutated a private detached clone of the exact candidate, then scored with the
frozen `score()` (or the harness variant, for the three committed breaks). Restored by
discarding the clone.

| Attack | REQUIRED | CONTROL | Discriminating FAIL |
|---|---:|---:|---|
| revert parent `protocol.ts` | 12/14 | 26/26 | exactly `R-D6-absent`, `R-D6-truth` |
| revert parent `evaluate.checks.test.ts` | 13/14 | 26/26 | exactly `R-D4a-absent` |
| revert parent `decode/index.ts` | 11/14 | 26/26 | exactly `R-D4b-neither`, `R-D4b-open`, `R-D4b-truth` |
| revert parent `exit-criterion-packet.md` | 9/14 | 26/26 | exactly `R-D1-absent`, `R-D1-blocks`, `R-D1-truth`, `R-D1-ten`, `R-D1-six` |
| revert parent `gate-s2-evidence.md` | 11/14 | 26/26 | exactly `R-D2-absent`, `R-D2-five`, `R-D2-truth` |
| harness `break-s1` after the candidate | 14/14 | 25/26 | exactly `C-D1-s1` |
| harness `break-s2-prefix` (prefix whitespace) | 14/14 | 25/26 | exactly `C-D2-prefix` |
| harness `break-reason-split` (`SIGNER_CHAIN_PENDING_HEAD`) | 14/14 | 25/26 | exactly `C-D6-codes` |
| insert `detail?: string` on `RefusalRecord` | 14/14 | 25/26 | exactly `C-D6-no-detail` |
| undo D-F1 closed strike (fully unstruck) | 13/14 | 26/26 | exactly `R-D1-blocks` |
| undo D-F1 closed strike → interior `exi~~t~~` | 13/14 | 26/26 | exactly `R-D1-blocks` |
| undo D-F1 closed strike → split `~~this alone ~~blocks exit` | 13/14 | 26/26 | exactly `R-D1-blocks` |
| undo D-F1 closed strike → `~~~…~~` | 13/14 | 26/26 | exactly `R-D1-blocks` |
| undo D-F1 closed strike → `~~…~~~` | 13/14 | 26/26 | exactly `R-D1-blocks` |

Interior/split `~~` and extra tildes around the D-F1 sentence do not count as repaired on a
clone of this candidate. Completion is withheld in every row above.

Measured harness-variant matrices (candidate subject):

- `break-s1` sha256 `05ceb4a9d5999e85cd6becbaa7f4ca795011b087af49890d1f51d013471f54b4`
- `break-s2-prefix` sha256 `adbb62da39bc7eebec35629e661a9b663e972d05ee2258fe6fade82eeb27e693`
- `break-reason-split` sha256 `95da668965bb8d8be0b2445c0a4a257ca6986ed780ac542f7fa1152844c80ddf`

## 5. Protected boundaries and frozen hashes

Reviews 1–4, CARD, RUNBOOK, RESULTS and `d-claims.py` are byte-preserved at the Review-4
parent (parent blob == candidate blob for each):

- Review 1 sha256 `fd48278dc9946342868e73b6e4ca8ad596ae0f34237618d0359ac0047e5cab35`
- Review 2 sha256 `766cfc1f338ff769f2e9f5d561285d09e5616bd0d6f7117e66478863629b0aa6`
- Review 3 sha256 `742b5eba31f2a1cb2c043629566a69cee0b73556da16daebe3e80019b0a8ef98`
- Review 4 sha256 `faa57770a206fbe8f5f58ff4da1bfb6a0602c6d2ff16989fc88eafeaf6b8ebd5`
- CARD sha256 `86ad309a2c912ab01580a9e6268d60d4d3bc5a074f8367d98a658a8c795d52e6`

Frozen hashes at the candidate, independently hashed from clone bytes (not from RESULTS.md):

| Object | sha256 |
|---|---|
| `docs/gate-s1-evidence.md` | `25dcefcade99e9e45be0c482f3dc5141f4d25335a920fabe1012303c7d7caf68` |
| S2 prefix before `## 11. What is NOT in evidence` | `470ec1de8ee696a2875334a7873e8e02504ea27d10676cb1a0018668097ba02f` |
| `scripts/check-suite-floors.sh` | `95b65a02bdfc8436e4739b7e5ef90b803964236a86173ed5b8f3c6cc139f7a46` |
| B-EVENTS `contracts/test/SentinelVault.events.t.sol` | `2a9219cc5138858b012b0bc56069490db3dd7d1963b73ccc19c28a48ce2b029e` |
| C-SNAPSHOT `ts/test/vault.snapshot.classification.test.ts` | `29a673560e89b639b6635661706a368454c9969a04c5d37c4f6c15229df3dd8a` |

`scripts/test.sh` still assigns `FOUNDRY_MIN_TESTS=103` and `TS_MIN_TESTS=550` (verifier floors
remain 221/7/78/30). `C-floors`, `C-checker`, `C-B-EVENTS` and `C-C-SNAPSHOT` PASSed on the
candidate `baseline`. `scripts/test.sh` does not mention `d-claims`. No `check-claims.sh` /
`check-prose.sh` exists.

`/usr/bin/grep` on the clean clone: `SIGNER_CHAIN_PENDING_HEAD` occurs only under this card
directory. `EVAL_ACTION_TARGET_MATCHES_MANDATE` is absent from `evaluate.checks.test.ts`.
`so the refusal detail now distinguishes them` is absent from `protocol.ts`. Live
`NEITHER the signer nor the verifier` / `Both are open (v1.1 register)` are absent from
`decode/index.ts` (historical ADJ2 / v3 quotes remain; those CONTROLs PASSed).

TypeScript executable residue (comment-stripped, whitespace-collapsed) is identical to the
parent for all three `.ts` surfaces. Spot-check: the mixed-case TARGET test still passes
`"EVAL_TARGET_BOUND"` into `outcomeOf`.

Repository checks from Sentinel root, output-read:

- secret guards: worktree `clean` (worktree emitted two `sed: RE error: illegal byte sequence`
  lines from untracked binary assets and still reported clean);
- review scope: R1 525 / R2 47 / R3 152 and **724/724** before staging this record;
  R1 526 / R2 47 / R3 152 and **725/725** after staging;
- vendor-honesty mechanical guard: pass without exercising agent authority over public claims;
- workspace guard: pass with **13 machine-state findings baselined and 0 new**;
- `git diff --check` on the candidate: clean.

Workspace success remains ratcheted; it does not erase the 13 pre-existing findings.

## 6. Limits carried with this HOLD

- Coverage is finite to the 14 REQUIRED / 26 CONTROL focused rows, the five causal reverts,
  and the named candidate attacks in §4. It is not general prose-consistency evidence or
  repository-wide claim completeness.
- Named residuals outside the card, not FAILs: `HANDOFF.md` still carries dated
  `NO SUBSEQUENT BATCH HAS BEGUN`; full `docs/session-state.md` rewrite was not in scope;
  D-055 / publish / push were not assessed. BLOCKER 1 remaining under the BLOCKERS heading
  is CARD-specified (`D1_NEW`).
- I did not launch Foundry, the TypeScript suite, the verifier, `scripts/test.sh` as a gate,
  `a-floors-gate.py`, or `scripts/check-suite-floors.sh` as a process. Floor constants were
  read from `scripts/test.sh` and hashed; `C-floors` PASSed. I did not re-run the full
  twenty-two committed instrument variants; pre-repair `baseline` and candidate `baseline`
  plus the §4 attacks are the implementation observations.
- This HOLD does not assess D-055, D-008 public-claim certification, publication, rename, or
  push. Gate S1/S2 signatures are untouched. It is not a second product attempt.

**HOLD** for exact candidate `491c035c67f4267f7c2fad1ceb74937835515387` within the frozen
D-CLAIMS boundary.
