# Check-inventory diff — A / B / C, 2026-08-31

**This file changes nothing. It records what a single versioned executable predicate is missing.**
Produced under D-085(e) and D-086 at HEAD `8146937`, analysis only, in a scratch copy. Nothing
here is a ruling; the two scope calls it surfaces are named in §6 and left open.

**Method, stated because three hand-derived figures in this project turned out to be artifacts of
the instrument.** A's inventory was extracted by AST-walking `verifier/verify.py` for every `Check(`
construction (97 sites across 17 functions), keyed on **(function, title)** — keying on title alone
gives 91 and is wrong, because six reason-code titles are shared verbatim between two functions.
C's inventory was extracted by a comment-stripping tokenizer over `SentinelVault.sol` (32 error
declarations, 46 `if … revert`, 56 atomic clauses, 0 `require`). B's raise sites were AST-walked
(36 + 20). A field sweep over every `eip712.*_FIELDS` member was run and then **verified by
reading, because it produced two false positives** — it marked `schemaVersion` as checked by B
(false: only the *manifest's*; no implementation validates the payload structs') and
`override.issuedAt` as checked by A (false: A's only `issuedAt` hits are inside a tamper mode).
Classification itself — whether a B raise is equivalent to an A check — was done by reading and
then executed. The scripts are reproducible: `extract_checks.py`, `runtime_inventory.py`,
`sol_extract.py`, `field_sweep.py`, `divergence2.py`, `override_parity.py`.

Suites re-measured at HEAD: `test_verifier.py` 221/221 · `test_publication_verifier.py` 77/81 (4
declared reds) · `test_publication_override.py` 61/61.

---

## 1. A (95 checks) against B

| Disposition | n |
|---|---|
| PRESENT | 38 |
| **ABSENT — DELIBERATE** | **0** |
| **ABSENT — OMISSION** | **54** |
| N/A — corpus-fixture artifact | 3 |

**Zero deliberate.** Not one of A's 95 checks is omitted from B with a recorded reason anywhere in
`docs/decisions.md`, the register, or B's source. B carries four `NOT_ESTABLISHED` disclosures and
a declared-red block, and **all five are about things A does not do either** — live code identity,
nonce freshness, a trusted clock, calldata decoding. Nothing in the record points at the A→B axis.

### The 54, by family

| | Family | n | B does instead |
|---|---|---|---|
| **O1** | **§5.5.1 refusal-record arm** — `_refusal_checks` (10), `_refusal_binding_checks` (7), `_refusal_reason_code_checks` (5), `_refusal_label_check`, `_unauthenticated_receipt_checks` (2), shape/locate, payload hashes and charset (6) | **32** | `grep -c "5\.5\.1\|refusal" verify_publication.py` → 0 functional. A refusal bundle is refused with *"missing required artifact receipt.json"* — the wrong artifact named, the §5.5.1 shape unrecognised, the scope boundary undisclosed |
| **O2** | **§5.6 evidence-bundle projections** — `_evidence_describes_the_bundle` (6), anchor present/matches, verdict present/agrees (4) | **10** | B hashes `evidence.json` and never opens it. `normalizedAction`, `expectedEffects`, `anchor` → **0 occurrences in B** |
| **O3** | **§5.7.1 decoded-parameter conformance** — `_allow_conforms_to_the_mandate` | **6** | `decodedSelector` → 0 occurrences |
| **O4** | **Reason-code arm, receipt path** — `_reason_code_checks` | **6** | `reasonCodes`, `reasonCodesHash`, `signerFindings` → 0 occurrences |

### The 38 PRESENT

Trust-root assertion (B stronger: manifest-rooted); evidence canonicalization + hash + binding (3);
§5.4 digest / recovery / declared signer / domain signer / low-s (6, B stronger: bound to the
manifest signer); `_binding_checks` (7, B makes A-067's absence-is-not-agreement repair structural
via `required()`); receipt-path payload hashes (3); calldata hash (1); mandate↔policy↔receipt
binding (2); verdict decodes to a known member (1, B stronger: also gates executability); **all 13
`_override_checks`** (B adds a window check A lacks); ran-to-completion (1).

---

## 2. C (46 reverts) against B

| Disposition | n |
|---|---|
| PRESENT | 27 clauses |
| **ABSENT — OMISSION** | **4** |
| N/A — unobservable offline, **disclosed** | 2 (`BadNonce`; live code identity) |
| N/A — unobservable offline, **UNDISCLOSED** | 6 (`Paused`; the activation half of `MandateNotActive` / `PolicyNotActive`; `activeMandate*` state) |
| N/A — not an action predicate | 7 |

**PRESENT but implicit:** `InvalidValidityWindow` for the receipt and the mandate. B has the explicit
empty-window check for the override (`vp:416`) and not for the other two; the conjunction
`issuedAt <= now < expiresAt` refuses an empty window but with a currency message, not an
empty-window one. Same discipline, one arm of three.

### The 4

| Vault site | C requires | B does |
|---|---|---|
| `:357` `UnsupportedOperation` | `operation == CALL`, **unconditionally** | compares to `policy["allowedOperation"]` (`vp:505`) |
| `:376` `ValueOverCap` | `valueWei <= maxNativeValueWei` — the immutable §4 backstop | nothing; not in `deployment.FIELDS` |
| `:377` `TargetNotAllowed` | `allowedTarget[target]` — owner-set allowlist | nothing |
| `:381` `SelectorNotAllowed` | `allowedSelector[selector]` — second clause | only the mandate half |

The last three are chain state B cannot reach today — but they are the Vault's three §4 hard
backstops, static after construction, could be carried in the manifest, and **`NOT_ESTABLISHED`
does not mention them.** They are OMISSION and not N/A because the honest disposition is a
disclosure B does not make.

---

## 3. The omission list, severity-ordered, each run

Staged from `case-1-allow` with the whole chain re-sealed **including the §5.6 projections** —
`Bundle.seal` does not resync them, and the first run produced three false positives from that.
**Control: unmutated re-sealed bundle → A PASS, B PASS.**

| # | Scenario | A | B | C |
|---|---|---|---|---|
| 1 | **`evidence.json` replaced wholesale** with `{"note": "this bundle's evidence says nothing at all"}`, re-canonicalized, re-hashed, receipt re-signed | FAIL | **PASS** | — |
| 2 | `evidence.normalizedAction` names a different target | FAIL | **PASS** | — |
| 3 | `evidence.verdict = BLOCK` while `receipt.verdict = ALLOW` | FAIL | **PASS** | — |
| 4 | `evidence.anchor` names block 99999999 / fabricated hash | FAIL | **PASS** | — |
| 5 | signer-attested decoded `beneficiary` ≠ `mandate.beneficiary` | FAIL | **PASS** | — |
| 6 | published `reasonCodes` contradict the committed `reasonCodesHash` | FAIL | **PASS** | — |
| 7 | `evidence.expectedEffects` misprojects the ceiling | FAIL | **PASS** | — |
| 8 | `action.operation = DELEGATECALL`, `policy.allowedOperation = 1` | **PASS** | **PASS** | **REVERT** |

**Severity 1 — O2, the evidence bundle.** Cell #1 is the worst in the diff: the artifact a recipient
actually *reads* — the dashboard's entire content — can be replaced with an empty object and B prints
`PASS (static, offline) … the signer's decision is ALLOW`. B authenticates that `evidence.json` is
*the* bundle the signer signed over and never that it *describes this action*. A-069 found exactly
this; D-052(b) fixed its sibling a second time.

**Severity 2 — O1, the §5.5.1 refusal arm.** Largest by count. A refusal presented to B is refused
for the wrong reason, naming the wrong artifact. §5.5.1's own rule — *a verifier must treat an
absent record as an unestablished refusal* — has no expression in B.

**Severity 3 — the operation omission, extended.** `grep -c operation verifier/verify.py` → **0**. A
does not check it either. A DELEGATECALL bundle certifies on **both** offline verifiers and reverts
on chain. **This is not an A→B instance; it is A-and-B-versus-C, and no round had named it.**

**Severity 4 — O4.** `receipt.reasonCodesHash` commits to a list B never reads; the codes a
recipient is shown can be swapped freely. Bites hardest on the override path, where B certifies.

**Severity 5 — O3, §5.7.1 conformance.** A re-derives it from the signer's *attested decoded record*
and the mandate, **without decoding calldata**. Adjacent to D-083(b) but **not covered by it** —
that ruling is about decoding, which A does not do. **See the D-083(b) correction in
`docs/decisions.md`: the recorded cost, "no independent downstream check", was wrong.** Whether B
should carry this check is a scope call and John's.

**Severity 6 — the three §4 hard backstops.** Undisclosed rather than unreachable.

---

## 4. The override-shape parity matrix

39 cells, **run**: 3 verdicts × 13 credential shapes × 2 B paths, credentials minted
internally-perfect via `Bundle`/`OverrideBundle` and `secp256k1.sign_digest`. C read from the
enumerated reverts and confirmed by the project's own green Foundry tests.

**Every credential-authenticity cell agrees. R-A018-18 is genuinely closed** — `check_owner_override`
fires on both paths and ALLOW+outsider is refused on the automatic path. B's diagnosis is *better*
than A's on four cells (named shape faults vs a bare digest failure).

### Disagreeing cells

**D-I — REVIEW × {expired, not-yet-valid, empty-window}: A = PASS, B = REFUSE, C = REVERT.**
`_override_checks` has no window check at all. A certifies a §5.5 credential the Vault refuses in
three distinct ways. **This is the inverse direction of the class, and the first instance found.**

**D-II — the whole temporal axis: `verify.py` has no clock.** Its only `issuedAt`/`expiresAt`
occurrences are inside a tamper mode. A evaluates no receipt, mandate, policy, deadline or override
window. **Demonstrated at HEAD:** `python3 verifier/verify.py --domain … case-1-allow` → `1/1
sample(s) verified`, exit 0, against a receipt whose window closed **2026-08-28**. B on the same
untouched fixture refuses with the currency message. A's docstring says only *"exit status is 0 only
if every check passes"*; it has no `NOT_ESTABLISHED` and never says currency was not evaluated.
**This is precisely the claim defect D-086 closed in B, standing undisclosed in A — the surface Gate
8's reviewers read as source.**

**D-III — REVIEW × absent: A = PASS, B = REFUSE, C = REVERT.** A certifies a REVIEW receipt as
authentic with no credential present. Defensible as a semantic split — A certifies *authenticity*, B
certifies *executability* — but **the split is stated nowhere**, so `=> PASS` from A and `PASS
(static, offline)` from B are two different claims wearing one word.

**D-IV — BLOCK × absent: A = PASS.** Same split, sharper: *"a BLOCK receipt certifies on neither
entry point"* (D-085(f)) is false of A as written.

---

## 5. What the class actually is

The six instances found one at a time are **a sample, not the whole**, and the framing that
produced them is off by one axis. The class is not *"disciplines lost in the rewrite"* — that
describes the mechanism, and it made the remediation look like six repairs. What the inventory
shows is a **scope truncation**: `a38cff9` rebuilt the verification surface around *"would the
Vault execute this bundle?"* and silently dropped every check answering the question `verify.py`
was built for — *"does this bundle describe what it says it describes?"* All 54 A→B omissions fall
inside that dropped half and nowhere else. Not one is recorded, and **the reason no round caught
the shape is that B's five disclosures are all on the other axis** — every `NOT_ESTABLISHED` entry
names something *C* can do that *B* cannot, and none names anything *A* does that *B* does not. The
record had no instrument pointed at A→B, so instances could only surface by accident, in whatever
order reviewers tripped over them.

Two further consequences the "six faces" framing hid entirely: the truncation runs **in both
directions** — A has no clock, so it certifies expired receipts and expired override credentials
that both B and C refuse, undisclosed — and it runs on an axis nobody was watching, **A-and-B versus
C**, where `operation` is checked by neither offline verifier against the Vault's absolute `== CALL`.

**Retiring the class means three matrices, not a longer list. The honest count of what a single
versioned predicate is missing is 54 + 4 + 4, not 6.**

---

## 6. Two scope calls surfaced and NOT made

1. **Should B carry §5.7.1 conformance (O3)?** A checks the signer's attested decoded record
   against the mandate without decoding calldata. D-083(b) rules out *decoding*; it does not address
   this. The diff measures the gap and records that the D-083(b) cost statement was wrong. **John's.**
2. **Is the A/B semantic split intended?** If A certifies authenticity and B certifies
   executability, that is defensible and must be *stated* on both surfaces. If it is not intended,
   D-III and D-IV are defects. **John's.**

---

## 7. Where a seventh instance would hide

1. **Semantic equivalence is not mechanised.** The 38 PRESENT rows were judged by reading and
   spot-executed. A PRESENT row whose B check is subtly weaker — B's `eq()` string-compare where A
   parses, `hex_to_bytes` strictness differing — would read as PRESENT. **The largest blind spot.**
   The mechanical close is a shared conformance-vector corpus run through all three — the Cycle 2
   handoff's own instruction, not yet executed.
2. **C was read, not fully executed.** Three Vault tests were run, not all 46 reverts through both
   entry points on Anvil. A dead guard would be counted PRESENT-in-C.
3. **`evidence.json`'s own schema is unenumerated** — no `*_FIELDS` declaration. Given O2 is
   severity 1, this is the second-likeliest hiding place.
4. **Coverage-guided branch enumeration was not run.** 36 of A's 95 checks were never emitted by
   the 7 committed fixtures; they were attributed by AST, not execution. A dead failure branch would
   look live — the R-A018-02 defect in reverse.
5. **`ts/` is a fourth implementation** (`ts/src/evaluate/`, `ts/src/signer/eip712.ts`) and was out
   of scope by the ruling's terms. If the goal is one predicate, the matrix is 4×4.
6. **`release/` and `reviewer-packet/` carry verifier copies** that were not re-diffed.
