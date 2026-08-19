# V4 — coverage statement

Commit: `c8d15a76425544148d7da2f8fa0c003feb6ad2b7`. Scope: `R2-F4` and `R3-F4` only, per
`BRIEF-V4.md`. I did not hunt outside that scope; two things I tripped over are recorded as
RESIDUALS in `REPORT.md` §3 rather than folded into a verdict.

---

## 1. Brief requirements, item by item

### `R2-F4`

| Requirement | Done | Where |
|---|---|---|
| Enumerate mechanically every place the claim appears, including its **other spellings** | **yes** | `PROBES.md` P2.1 — 14 spellings, `/usr/bin/grep` + join-sweep |
| Search code comments, Solidity NatSpec, Python docstrings, the proposal, the docs | **yes** | `contracts/src`, `contracts/test`, `ts/src`, `verifier/*.py`, `scripts/`, proposal, `HANDOFF.md`, `README.md`, all `docs/*.md` |
| At each site, verify the statement is removed/struck/superseded **as that site's reader sees it** | **yes** | `REPORT.md` §1.3 table; each site read raw, not inferred from the correction note |
| Distinguish live claims from preserved historical evidence | **yes** | `REPORT.md` §1.7, with the basis stated per site |
| A control: a place the claim is stated CORRECTLY, confirmed not flagged | **yes** | `REPORT.md` §1.6 — four such sites |
| Observing falsification / pre-fix comparison | **yes** | `PROBES.md` P1.2 (pre-fix grep at two commits), P1.3 (mutation: 9 OK to 8 FAIL), P2.2-P2.3 (the repair's own diff and line history) |

### `R3-F4`

| Requirement | Done | Where |
|---|---|---|
| Derive the REAL code names from the CODE, not from any document | **yes** | `PROBES.md` P3.1 — `protocol.ts:248/250`, `attest.ts:523/524`, corroborated by a committed receipt, a pinning test and a mutation site |
| Verify the maintained documentation names those real `SIGNER_*` codes everywhere | **yes** | `REPORT.md` §2.3 — both disclosure sites |
| Confirm no fictitious `EVAL_VAULT_*` survives outside clearly historical quoted evidence | **yes** | `PROBES.md` P3.2 — exactly two occurrences tree-wide, both inside `A-078`'s own confession |
| State which category each hit falls into and why | **yes** | `REPORT.md` §2.4, `PROBES.md` P3.5 |
| Sweep the same CLASS: enumerate codes the code defines, diff against codes the docs name | **yes** | `PROBES.md` P3.3 (Diff A) and P3.5 (Diff B, comment-stripped) |
| A control: method does not flag real codes, and WOULD have caught the original if reintroduced | **yes** | `PROBES.md` P3.4 and P3.6 — reintroduced into a doc AND into the code comment; both caught; 102 real codes unflagged |

---

## 2. Exact material inspected

**Read in full or in the relevant region:**

- `docs/decisions.md` — entries `D-014` (:27), `D-052` (:223), `A-070` (:225), `A-074` (:239),
  `A-077` (:245), `A-078` (:246), `A-080` (:248)
- `docs/v1-1-register.md` — §13.6 tail, §13.7 (:877-903), §14 (:905-945), :613, :777
- `docs/exit-criterion-packet.md` — §3 (:88-98), §3b (:99-107), §6 (:192-204), §7 (:207-218)
- `docs/gate-s1-evidence.md` — :110-175 (the `D-055(b)` annotation region)
- `docs/gate-s2-evidence.md` — :612-650 (the three `D-057(6)` accepted limitations)
- `docs/session-state.md` — :12-30, :215-245
- `verifier/verify.py` — :1286-1300, :1327-1440, :1490-1530, :1610-1640
- `verifier/test_verifier.py` — :1180-1200, :1330-1420
- `ts/src/signer/protocol.ts` — :340-395, :660-690, :755-790
- `ts/src/signer/attest.ts` — :515-530, :620-700
- `ts/src/decode/index.ts` — :178-260
- `scripts/check-eval-codes.sh` — :1-45
- Briefs: `COMMON-BRIEF.md`, `BRIEF-V4.md`, `docs/repair-protocol.md`

**Swept but not read line by line:** every other tracked file in the tree, via the grep and
join-sweep patterns in `PROBES.md` P2.1 and P3.2.

**Commands run:** `git rev-parse`, `git status --porcelain`, `git log --oneline -L`,
`git show` (three commits), `/usr/bin/grep -rnE`, two Python sweep scripts,
`python3 -B -m unittest test_verifier.TestAllowConformsToTheMandate`,
`bash scripts/check-eval-codes.sh`.

---

## 3. Historical hits, quoted so the classification is checkable

- `docs/review-2026-08-17/lens-D-evaluator-and-decoders.json` — `EVAL_ALLOWANCE_EFFECT` appears
  inside *"…EVAL_ALLOWANCE_EFFECT before/after swap…"*, a reviewer naming a mutation family.
  Truncated glob, preserved artifact.
- `docs/review-2026-08-17/lens-G-corpus-labels-figures.json` — *"all eight fail a genuine
  `EVAL_PURCHASE_*` purpose check at L3"*. Explicit glob, preserved artifact.
- `docs/review-2026-08-17/lens-H-d010-verifier.json` — `SIGNER_OWNER_APPROVED_OUT_OF_BAND` is a
  code the reviewer **deliberately forged** to demonstrate that an uncommitted code could ride
  in the array a dashboard reads. A fabricated name is the *point* of that artifact.
- `docs/decisions.md:246` — `EVAL_VAULT_TARGET_NOT_ALLOWED` / `EVAL_VAULT_SELECTOR_NOT_ALLOWED`
  inside *"A FALSE CODE NAME I INVENTED … spellings that exist nowhere in the codebase."*
- `docs/session-state.md:18` — *"a fabricated `EVAL_VAULT_*` code name"*.

None of these is a citation of a code as real. None should be rewritten.

---

## 4. BLIND SPOTS — stated so a green report is not read as full coverage

1. **Meaning coverage is bounded by my enumeration.** I searched 14 spellings of the `R2-F4`
   claim. A fifth site phrased in a meaning I did not anticipate would not appear. This is the
   `A-063` failure mode restated, and I cannot rule it out — only narrow it. I did read
   `docs/exit-criterion-packet.md` and `docs/v1-1-register.md` §14 continuously rather than by
   grep alone, which is how site 3 surfaced.
2. **`node_modules` was excluded** from every sweep as vendored dependencies. Nothing in scope
   should live there, but I did not verify that.
3. **Diff B's comment stripper is regex-based.** A code name inside a string that merely looks
   like a comment (or a comment marker inside a string literal) could be misclassified in either
   direction. I did not build a parser.
4. **Identifier families beyond `EVAL_`, `SIGNER_`, `DECODE_` were not diffed.** `DECODE_*` is
   included but I did not separately audit `REFUSAL_*`, class-name strings such as
   `evaluator-or-signer-compromise`, or corpus label vocabularies.
5. **`R3-F4`'s measurement half is untouched.** I confirmed the *codes named* are real. I did
   NOT reverify that `allowedTargetsHash`, `allowedSelectorsHash`, `purposeKind` and
   `allowedCallGraphHash` are read zero times — that is the other half of `R3-F4` and outside
   this brief.
6. **I did not run the deep gate or the full suites.** Only the nine-test verifier class
   directly covering the mechanism `R2-F4`'s claim is about. Nothing here is a statement about
   overall suite health.
7. **`docs/decisions.md:223` (`D-052(a)`) is a judgement call, not a measurement.** I classified
   it historical; see RESIDUAL R-3. If John classifies it the other way, that is a third
   uncorrected `R2-F4` site rather than two.
8. **Binary, image and non-UTF-8 content was skipped** by both sweep scripts.

---

## 5. Independence

I did not author any code, document or repair examined here, and I read no other reviewer's
output for this cycle. `A-077`'s and `A-078`'s own accounts were read as **claims under test**,
not as findings — every statement they make that I relied on was re-measured against the tree.
The two `R2-F4` sites I report were found by continuous reading of the two documents, after the
grep sweep had already returned what looked like a complete four-site picture.
