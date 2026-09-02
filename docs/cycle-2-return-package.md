# Cycle 2 return package — Sentinel conformance lab

| | |
|---|---|
| **Message ID** | `MSG-TBD` |
| **Reply To** | Cycle 1 handoff, `S-20260830-sentinel-conformance-lab-r1` |
| **From** | BUILD TEAM — no seat in the §5 `From` enum |
| **To** | Smith, Staff, all chairs |
| **Type** | `ARTIFACT` |
| **Action Required** | `DECIDE` — Cycle 2 review of the candidate against both withdrawal conditions |
| **Status** | `OPEN` |

**Summary:** Both Binding Criticals are addressed at one implementation SHA — one demonstrated as already closed, one fixed by the non-certifying-static route the council permitted. Each is observed by a named test that fails when its fix is reverted. Neither Critical is withdrawn by this package; that is the council's.

Every figure below was produced by running the tool on the candidate on 2026-09-01/02. Commands are given so they can be re-run rather than believed.

---

## 1. The implementation commit

```
cb124feaad6b925f683b0739de53970e1700e146
```

Branch `step-3/isolated-signer`, on top of `2115c4f`. A documentation-only follow-up commit records D-088 and this package; it changes no code and the candidate is `cb124fe`.

**Built under D-086 and D-087 with test-first separation (D-058(1)).** Two independent test authors extended and created the frozen contracts against the untouched implementation — 21 and 38 red — before any implementer touched a module. One implementer worked to those contracts. An independent verifier then tried to break the result. No implementer edited a contract; the one staging defect the port exposed in the frozen suites went back through a test author.

---

## 2. Mapping: each sustained Critical → changed files → observing tests

### Binding Critical 1 — an unexamined override credential inside a PASS

**Status: closed at `5d93850` (2026-08-30) under D-083(c), before Cycle 1 reported. Demonstrated here, not fixed here.** The council reviewed `8d47a0b`, four commits earlier.

| Changed | What |
|---|---|
| `verifier/verify_publication.py` | `check_owner_override` is called whenever `override.json` is present, on every execution path, not only when the override path is selected. A §5.5 pairing check refuses any override beside a non-REVIEW receipt, first, before authenticity — so the refusal names the shape rather than sending a recipient after a signature that was fine. |

| Observing test | What it stages |
|---|---|
| `test_publication_override.py::TestAnUnexaminedOverrideCredentialIsNotCertifiable.test_an_allow_bundle_carrying_an_outsider_override_is_refused` | A genuine secp256k1 §5.5 credential, correctly bound to this bundle's receipt/action/mandate/policy/nonce, minted by an outsider key, beside an ALLOW receipt, on the automatic path. Must refuse naming `override`. |
| `…test_the_owner_signed_case_is_refused_too_or_examined` | Same, owner-signed. |

**Reverting the hoist** (`if execution_path == OVERRIDE_PATH:` back in front of the call) fails exactly those two tests and nothing else. Measured by the independent verifier as mutation M1.

**Withdrawal condition as written — every clause:** ALLOW + override refused ✓ (above); malformed / outsider-signed / misbound / expired / non-canonical overrides refused ✓ (`TestOverrideRefusalsAreDiagnosed`, `TestOverrideBindsToOneExactAction`, `TestOverrideWindow*`, `TestOverrideSignatureForm*` — 61/61); positive REVIEW + authenticated override ✓ (`TestTheCertifyingRunSaysWhichPathItCertified`); the deliberately-red R-A018-18 cases removed ✓ (both green; floors guard declares zero reds for that file); no success message implies an ignored credential was validated ✓ (the override headline names the override; `TestTheCertifyingRunSaysWhichPathItCertified` asserts on it). **The parity matrix is §4.**

### Binding Critical 2 — certification over unauthenticated state and optional time

**Status: fixed at `cb124fe` by the non-certifying-static route** — *"Live RPC is not mandatory if the bounded lab chooses the honest non-certifying path. What is mandatory is that the result stop claiming properties it did not authenticate."* Ruled D-086(e). No RPC was added.

| Changed | What |
|---|---|
| `verifier/deployment.py` | `verify()` with no `evaluation_time` **refuses** by raising `DeploymentManifestError` — a `ValueError` subclass, deliberately not a Python-required parameter, because a `TypeError` would sail past every `except ValueError` in callers (D-086(b)). `check_lifetime` is unconditional. |
| `verifier/verify_publication.py` | One instant is pinned at process start and threaded to the single `deployment.verify` call. A supplied `runtimeCodeHash` and `deploymentBlockNumber` travel **only** under `unverifiedAuthorityAssertions`, never as a bare top-level fact, and appear in no headline. `NOT ESTABLISHED` names deployment identity, nonce freshness, currentness and executability, plus the three §4 Vault backstops, and is printed beside every certifying result. `--evaluation-time` produces `MODE_DIAGNOSTIC`, exit 3, never a certification. A `CLAIM:` line states that this tool certifies executability and that `verify.py` certifies authenticity (D-087(c)). |

| Condition | Observing test(s) — each fails when its fix is reverted |
|---|---|
| (1) Certifying instant non-omissible | `test_publication_verifier.py::TestTheCertifyingInstantIsNotOmissible` — `test_omitting_the_evaluation_time_is_refused_not_skipped`, `test_an_explicit_none_is_refused_the_same_way`, `test_omitting_the_instant_cannot_revive_a_stale_manifest`, `…_post_dated_manifest`; plus `test_the_publication_verifier_supplies_one_instant_on_both_paths`, which spies the single `deployment.verify` call and matches its instant to `result["evaluationTime"]`. Mutation M2 (restore `if evaluation_time is not None:`) fails the four. |
| (2) Injected time only in a non-certifying mode | `test_injected_time_is_only_available_in_the_non_certifying_mode`; `TestClockIsNotTheCallers` (CLI: exit 3, no `NOT ESTABLISHED` line printed, `notEstablished` carried in JSON). |
| (3) Explicit declaration that identity, nonce freshness, executability are not established | `TestTheStaticResultDisclaimsWhatItDidNotAuthenticate.test_the_certifying_result_disclaims_all_four` and `test_the_disclaimer_is_printed_beside_the_result_not_only_inside_it` — the single printed `NOT ESTABLISHED` line must match all four words. Mutation M6 (strip two entries) fails both. `TestTheVaultBackstopsAreDisclosed` — `maxNativeValueWei`, `allowedTarget`, `allowedSelector` named as Vault state. |
| (4) A supplied `runtimeCodeHash` is never reported as authenticated | `TestDeploymentIdentityIsNotBound.test_a_fabricated_runtime_code_hash_is_echoed_as_authenticated` — name kept for the council's reference, body **redefined under D-086(e)**: the invented value may appear only under a key labelled `assert|unverified|unauthenticated|claim|said|disclaim|not.?established`, never top-level; the headline must not say "authenticated deployment". Checks the certifying JSON, the headline, and the diagnostic JSON. Mutation M3 (echo top-level) fails three tests. |

**The three R-A018-04 tests were redefined, not closed by chain binding.** `…_two_contradictory_manifests_cannot_both_certify` became `…_both_authenticate_statically_and_neither_claims_deployment_identity` — both certify (a positive control: a run refusing one would mean someone built the RPC D-086(e) rules out), neither presents its hash as fact. `…_the_result_names_the_block_its_claims_are_true_at` became `…_anchors_no_claim_to_a_block_and_says_executability_is_not_established`. **No chain binding exists.** `runtimeCodeHash` is compared to nothing, and the `KNOWN RED TESTS` block in `verify_publication.py` records that a future chain binding needs new tests — these three no longer test for one.

---

## 3. Test commands and captured results

All run from the repository root on the candidate.

```
forge test --root contracts                                   105 passed, 0 failed
npm --prefix ts test                                          557 pass, 0 fail
python3 -m unittest verifier.test_verifier                    Ran 221 · OK
python3 -m unittest verifier.test_publication_verifier        Ran 105 · FAILED (failures=1)   ← the one ruled red, §7
python3 -m unittest verifier.test_publication_override        Ran 61  · OK
python3 -m unittest verifier.test_publication_conformance     Ran 53  · OK   (new this candidate)
bash scripts/test.sh                                          GATE PASSED, exit 0
bash scripts/check-release-sync.sh                            clean — 429 files, byte-identical to the assembler's output
bash scripts/check-release-executes.sh                        clean — the SHIPPED verifier runs; import closure 8 files; two arms match source byte-for-byte
bash scripts/check-publication-suite-floors.sh                clean — 104/105 (floor 104, 1 red declared) · 61/61 · 53/53
bash scripts/check-test-vacuity.sh                            clean — 4 modules traced; 2 carried in test_verifier.py (§7)
bash scripts/check-gate-abort-safety.sh                       clean — 10 sites, 0 unguarded, 0 carried
bash scripts/check-gate-immutability.sh                       10/10
bash scripts/check-rename-gate.sh                             held — HELD_PRIVATE / UNDECIDED / NONE
tools/guards/run_guards.sh Sentinel                           OK — 13 baselined, 0 new
```

**A guard that did not exist at Cycle 1, and why.** The port added `import reasoncodes` and `import refusal`; the assembler did not ship them; **the shipped verifier died on import** — while `check-release-sync.sh` reported clean (the tree *was* byte-identical to the assembler's output) and the gate reported PASSED (it ran the source). Nothing executed the release copy. This is the third instance in three days of the reviewed thing and the shipped thing diverging. `scripts/check-release-executes.sh` now assembles into a temporary directory and **runs** the shipped `verify_publication.py` — static import closure, `--help`, a re-staged certifying arm and a fixed-instant diagnostic arm, each byte-compared against the source verifier. It fails on the exact defect that produced it (removing `reasoncodes.py` from `VERIFIER_FILES` → four named findings) and is wired in both gate profiles. Its printed limits: it does not run the release's Anvil demo, cannot see dynamic imports, and runs one ALLOW fixture on two arms.

---

## 4. The override-shape parity matrix

**Full matrix:** `docs/check-inventory-diff-2026-08-31.md` §4 — 39 cells, **run** not reasoned: 3 verdicts × 13 credential shapes × 2 execution paths, credentials minted internally-perfect via the suites' `Bundle`/`OverrideBundle` helpers and `secp256k1.sign_digest`; SentinelVault read from its enumerated reverts and confirmed by its green Foundry tests.

**Result on the credential-authenticity axis: every cell agrees** across `verify.py`, the publication verifier on both paths, and SentinelVault. The publication verifier's diagnosis is *better* than `verify.py`'s on four cells (a named shape fault where `verify.py` gives a bare digest failure).

**Cells that disagree, and their disposition:**

| Shape | `verify.py` | Publication verifier | Vault | Disposition |
|---|---|---|---|---|
| REVIEW × override expired / not-yet-valid / empty-window | PASS | REFUSE | REVERT | `verify.py::_override_checks` has no window check; `verify.py` has **no clock at all**. **Ruled intended under D-087(c):** `verify.py` certifies *authenticity*, and an expired credential is still an authentic one. Its docstring and output now say so, and disclose that it evaluates no validity window. |
| REVIEW × no override | PASS | REFUSE | REVERT | Same ruling: authentic, not executable. The split is now stated on both surfaces (`CLAIM:` line; `verify.py` success output). |
| BLOCK × any | PASS | REFUSE | REVERT | Same. |
| DELEGATECALL / CREATE with a permissive policy | PASS | **REFUSE** (`UnsupportedOperation`, unconditional) | REVERT | Publication verifier fixed this candidate (D-087(a)). `verify.py` **exempt under D-088** — an executability condition, not an authenticity one. |

**No override-bearing shape certifies on the publication verifier that the Vault would refuse.**

---

## 5. Evidence that certifying time is non-omissible

- `deployment.verify(document, authority)` with the instant omitted → `DeploymentManifestError: evaluation_time was omitted: the certifying instant at which this manifest's lifetime is judged is not omissible (D-086(e))`. Same for an explicit `None`. Measured.
- The publication verifier captures `int(time.time())` once at process start and passes it to its single `deployment.verify` call; `test_the_publication_verifier_supplies_one_instant_on_both_paths` spies that call and asserts one instant per run, equal to `result["evaluationTime"]`.
- `--evaluation-time` → `MODE_DIAGNOSTIC`, exit 3, no certifying headline, no `NOT ESTABLISHED` line printed (the list rides in JSON only). It cannot reach exit 0.
- The four omission tests fail when the old `if evaluation_time is not None:` guard is restored — mutation M2, measured by the independent verifier.

---

## 6. Evidence that unauthenticated state cannot produce authenticated / current / executable claims

- A fabricated `runtimeCodeHash` (`0xb2…b2`) in a signed manifest: the certifying run's stdout contains the value **once**, inside `unverifiedAuthorityAssertions`; **zero** occurrences in the headline, the `CLAIM:` line, or the `NOT ESTABLISHED` line. Measured by the independent verifier, who also scanned the two lines the test does not.
- The certifying headline reads `PASS (static, offline) …` and the printed `NOT ESTABLISHED` line names: deployment identity, nonce freshness, currentness, executability, `maxNativeValueWei`, `allowedTarget`, `allowedSelector`, and the seventh entry — conformance of calldata *arguments*. The word "current" does not appear in any certifying claim; "authenticated deployment" appears nowhere.
- Two contradictory manifests for the same bundle **both** certify statically and **neither** presents its hash as a fact — the positive control that no chain binding was built.
- The `CLAIM:` line: this tool certifies **executability** as far as it can be established offline; `verify.py` certifies **authenticity**. Both surfaces state it.

---

## 7. The complete remaining-red list

**One red, permanent by ruling.**

`test_publication_verifier.py::TestExactActionIsEnforced.test_calldata_redirecting_the_mandated_beneficiary_is_refused` — **R-A018-17, D-083(b).** The verifier does not decode calldata; the signer's evaluator does, and the Vault binds bytes. Rebuilt this candidate so that it fails on the ruled defect itself — a bundle whose calldata redirects the beneficiary, with an internally perfect chain and an attested record still naming the mandated party, certifies ALLOW (`'ALLOW' == 'ALLOW'`) — and nothing else can move it: a green means calldata was decoded against ruling; an error means an unrelated arm intercepted the staging. Disclosed to the recipient as the seventh `NOT ESTABLISHED` entry. The council endorsed this disposition at Cycle 1 ("define exact action as exact signer-attested bytes and disclose the signer-only semantic boundary").

**Zero reds in `test_publication_override.py` and `test_publication_conformance.py`.** The floors guard declares zero for both; a red in either is a regression.

**Carried, not red — two dead assertions in `test_verifier.py`,** found by the vacuity guard on its first run and carried on its ratchet: `TestUnassertedValidation.test_pair_aligned_whitespace_cannot_collide_an_encoded_word` (an unreachable `assertNotEqual` after a `continue`; the test's own comment records its first version had the same defect) and `TestJCSStructure.test_key_sorting_is_utf16_code_units` (`assertGreater` over two literals). Owed to a test author; outside this candidate's ruled scope.

**Intermittent, outside scope — R-A018-26.** `ts/test/cases.e2e.test.ts:260` stamps `now` from `Date.now()`; the R-A018-15 clock mechanism the cold demo was cured of. One fast-gate run failed on it; the file ran 3/3 and the suite 557/557 on re-run; the candidate touches neither `ts/test/` nor the signer. Recorded, not fixed.

---

## 8. Confirmation

Measured at commit time, 2026-09-02:

- `gh repo view johnrfite1/sentinel --json visibility` → **`PRIVATE`**
- `git rev-parse origin/step-3/isolated-signer` → `70f4b4d`; **nothing pushed**; 11 commits local
- No `LICENSE*` at the repository root; rights mode `UNDECIDED`; **licence DEFERRED under D-082(c)**
- No deployment, no release, no visibility action. `docs/publication-policy.state` is `HELD_PRIVATE`.

---

## 9. Cycle 1's non-blocking findings — disposition at this candidate

| Finding | Done |
|---|---|
| "Exact action" language | Defined as exact signer-attested bytes; the signer-only semantic boundary disclosed as `NOT ESTABLISHED` #7 and in `release/README.md`. §5.7.1 conformance added on the signer's *attested record*, named "signer-attested record conforms to mandate" and never "beneficiary verified", with the output stating it does not catch a lying signer (D-087(b)). No calldata decoding. |
| Headline and success claims | `CLAIM:` line; `NOT ESTABLISHED` beside every certifying result; `release/README.md` exit-code table and predicate list rewritten; the "open scope question" contradiction of D-083(b) struck in place. |
| Guard integration | `check-release-sync.sh` and `check-publication-suite-floors.sh` wired at `5d93850`; `check-release-executes.sh` added and wired here. |
| Vacuous tests | `check-test-vacuity.sh` wired under `--gate` at `5d93850`; now traces four modules. |
| Record navigation | Not done. Assumption 5 of the Ingot; the entry-point paragraph the council asked for is still owed. |
| Historical corpus | Untouched; the A-111 hold stands; the deep profile remains red on the §7.1 digest by design. |
| Key-absence claims | `release/README.md` states a check result, never an absence; the machine-state ratchet's 13 baselined findings are disclosed by class in `AGENTS.md`'s successor note. |
| Commit subject | History not rewritten; `8d47a0b`'s subject is annotated in the register. |
| "Independent" terminology | Not addressed reader-facing. Open. |
| Reproducibility | Vendored LICENSEs ship; `npm test` in the release refuses honestly rather than passing on zero tests; Node/Python/Foundry/Anvil remain unpinned (R-A018-13). |
| Naming collision | Unchanged; the README's disambiguation is not yet at the first surface. Open. |
| Overall presentation | The `CLAIM:` line and `release/README.md`'s "Two verifiers, two claims" section are the concise statement; the one-paragraph entry point is still owed. |

---

## 10. Corrections to the build team's own record, made this candidate

Recorded here because the council's method is that a claim must be measured, and four of the agent's were not:

- D-083(d)'s "17 call sites" was **20**, and its `TypeError` obstacle was avoidable (D-086(b)).
- D-083(b)'s recorded cost — "no independent downstream check" — was **false**; `verify.py` re-checks the attested record (`docs/decisions.md`, D-083(b) correction).
- D-084(a)'s "exactly two instances" was a property of an anchored regex; a third existed (`docs/decisions.md`, D-084 correction).
- A claim was written into `HANDOFF.md` before its work existed and an outage left it standing (register §0.3).

**Nothing in this package withdraws a Critical, signs a gate, or authorises publication, deployment, push, or visibility change. Both Criticals remain the council's to withdraw at Cycle 2, against tests that directly observe the original defects — which is what §2 names.**
