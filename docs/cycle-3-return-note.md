# Cycle 3 return note — Sentinel conformance lab

Session `S-20260830-sentinel-conformance-lab-r1`, Cycle 3, extended past the cap of 2 by the
Smith's written note (D-090(c)). Prepared by the build team's coordinating agent, 2026-09-02, for
the orchestrator to file. **Withdraws nothing.** The sustained Critical is the council's.

## 1. The candidate commit

`0bc79a8373ec26398702b47430da48134e7cbfe6` on `step-3/isolated-signer`, parent `be6894a`
(the annotated Cycle 2 candidate `cb124fe` plus its return-package annotation). Eleven files.
Not pushed at the time of writing; the private remote is at `f18d143`. Verify:
`git rev-parse 0bc79a8` and `git diff --stat be6894a 0bc79a8`.

## 2. The withdrawal condition, verbatim, and what closes each clause

> "root README routes only through the publication verifier, and `verify.py` no longer emits
> recipient-facing PASS/exit 0 for BLOCK or un-overridden REVIEW"

**Clause 1 — the root README.** `README.md` is rewritten (D-090(b), (d)). The entry-point
paragraph is at the top. The first runnable command is the release cold demo (`README.md:38-43`);
every fenced command before `## Historical: the v0.2 comprehension packet reviewed at Gate 8`
(`README.md:138`) invokes `verify_publication.py` (`:61-63`, `:79-81`, `:83-86`). The first
fenced `verify.py` command is inside the Historical section (`:232-233`) and names the packet copy
explicitly. `release/README.md` fences `verify_publication.py` only and says `verify.py` is not
in the tree; `ls release/verifier/` has no `verify.py` and `release/MANIFEST.sha256` lists none.

**Clause 2 — `verify.py`'s exit contract.** Route (a), D-090(a), the `gpgv` model. Measured on
this commit with `--domain fixtures/samples/domain.json`:

| Bundle | Headline | Exit |
| --- | --- | --- |
| ALLOW (`case-1-allow`) | `=> PASS: AUTHENTIC -- hashes, signatures and bindings hold …` | 0 |
| BLOCK (`case-2`, `case-3`, `case-4-blocked`, `edge-single-reason-code`) | `=> AUTHENTIC, NOT EXECUTABLE: the signed verdict is BLOCK -- SentinelVault refuses a BLOCK receipt at both entry points …` | 3 |
| REVIEW with valid `override.json` (`case-4-review`) | `=> PASS: AUTHENTIC …` | 0 |
| REVIEW with `override.json` removed (constructed; no such fixture ships) | `=> AUTHENTIC, NOT EXECUTABLE: the signed verdict is REVIEW -- the bundle carries no override.json …` | 3 |
| Tampered signature | `=> FAIL` / `FAILED: …` | 1 |
| `--all fixtures/samples` | `7/7 sample(s) verified as AUTHENTIC.` + four `NOT EXECUTABLE:` lines | 3 |
| `--all` over FAIL + BLOCK | `1/2 sample(s) verified as AUTHENTIC` + `FAILED:` + `NOT EXECUTABLE:` | **1** |

Precedence is `1 > 3 > 0`, single, `--all` and multi-positional. The authenticity claim, the
no-clock disclosure, D-088's `operation == CALL` exemption, `verify_sample()`'s return contract
(every in-process caller still gets authenticity) and the `--tamper` self-test are unchanged. The
classifier reads only the signed `receipt.verdict` and whether `override.json` exists.

**Observing tests, written first (D-058(1)).** `verifier/test_verifier.py::TestExitContractD090`,
18 tests, landed by an independent test author against the frozen 221-test baseline before the
implementer touched `verify.py`. They pin: exit 3 and a first headline line that begins
`=> AUTHENTIC, NOT EXECUTABLE` and contains neither `PASS` nor `FAIL`; no `=> PASS` anywhere in a
BLOCK / un-overridden-REVIEW run; `NOT EXECUTABLE:` after the summary; exit 0 / `=> PASS:
AUTHENTIC` and no `NOT EXECUTABLE` for ALLOW and overridden REVIEW; exit 1 / `=> FAIL` /
`FAILED:` for refusals; four states distinguishable by exit code alone; the `--all` and positional
aggregation rules; the tamper self-test untouched. Two carried tests whose assertion *was* the
defect are rewritten. Suite 221 → 239; `VERIFIER_MIN_TESTS=239`.

**The gate observes it too.** `scripts/test.sh:975-976` runs the D-010 walk and fails the stage
unless `--all fixtures/samples` exits exactly `3` — deliberately not `0|3` — and a failed stage
fails the gate (`:1014`, `:1026-1030`). A regression to exit 0 is a red gate, not a log line.

## 3. Verification on this tree

- Fast gate: `GATE PASSED`, exit 0; D-010 stage `suite 239 (floor 239) · verdict clean · samples 7
  (floor 7) · walk exit 3 (want 3) · tamper 78 cases / 30 modes`.
- Suites: `test_verifier` 239 OK; `test_publication_verifier` 105 run, 1 failure (the permanent
  R-A018-17 red, unchanged); `test_publication_override` 61 OK; `test_publication_conformance`
  53 OK.
- `check-release-sync.sh` clean (429 files, byte-identical to a fresh assembly);
  `check-release-executes.sh` clean (shipped import closure stdlib-or-shipped; certifying and
  fixed-instant runs reach the source verifier's exact result).
- **Independent verification** by a fresh agent with no build context, told to prove the
  condition fails: 29 executed commands including a fresh cold demo from a clean `release/`
  (`npm ci`, `forge build`, demo, `verify_publication.py` on the ALLOW bundle inside its window →
  exit 0, on the BLOCK bundle on both execution paths → exit 1). **Both clauses HOLD.** Every
  README claim about either verifier was run and matched; the quoted `CLAIM:` line at
  `README.md:101` is byte-identical to the tool's output.

## 4. Stale text asserting the withdrawn behaviour — found by the verifier, fixed in the candidate

1. `docs/enforcement-release-v0.3.md` consequences table said `verify.py` prints `=> PASS` on a
   BLOCK and on an un-overridden REVIEW, and the root README sends readers there as where the
   split is stated. The two cells are struck in place and amended under D-090(a).
2. `verifier/verify_publication.py`'s module docstring — **which ships byte-identical in the
   release tree and prints under `--help`** — said `verify.py` "correctly passes both of those
   bundles". Rewritten to the landed contract; release re-assembled; guards clean.
3. `reviewer-packet/README.md` routed to the packet's frozen v0.2 `verify.py` with no D-090
   disclosure, so a recipient handed the packet directory alone gets a bare `=> PASS` / exit 0 on
   a BLOCK. A dated, additive note now sits under the packet's verifier section. **Nothing in the
   packet is struck or rewritten**, and its `verify.py` is not regenerated — it is the artifact
   Gate 8 reviewed (D-080). This is the one edit in the candidate to a reviewed historical
   artifact; it is reversible, and the Smith may strike it.

## 5. Disclosed, not changed — for the chairs to weigh

- **The packet's `verify.py` still prints `=> PASS` / exit 0 on BLOCK.** Reachable only from the
  root README's Historical section and from the packet directory itself; disclosed in both.
  Regenerating it would change the Gate 8 artifact, which the build team may not decide.
- **A §5.5.1 refusal record still gets `=> PASS: AUTHENTIC` / exit 0 from `verify.py`**
  (`fixtures/samples/refusal-vault-paused`). It is not a receipt, the Vault has nothing to
  execute, and `verify_publication.py` recognises and refuses it (Cycle 2). It is outside the
  condition's text — BLOCK or un-overridden REVIEW — and the test author did not extend the
  ruling to it. **Put to the Smith as a fork**, not decided here.
- **Per-check `[PASS]` lines are unchanged.** A BLOCK run still prints ~27 `[PASS] …` diagnostic
  lines; only the `=> ` headline and the summary changed. A naive `grep -q PASS` matches. The
  tests pin the headline and forbid `=> PASS`, not the word count. Changing the per-check prefix
  touches 239 tests and was judged out of the narrow scope.
- `--tamper all` on a BLOCK sample prints ten `=> tamper self-test PASS: …` lines and exits 0.
  Self-test mode, pinned as deliberate.
- `README.md:111` carries one unfenced, copy-pasteable `verify.py` command before the Historical
  section, as a measured example; it yields exit 3 / `NOT EXECUTABLE`, not the defect.
- R-A018-27 (the README's own commands leave `release/demo-out/` untracked) is open and
  not in scope.

## 6. What this candidate does not do

It withdraws no Critical. It does not touch the five advisory Criticals except where the
entry-point paragraph discharges AC6/AC8 incidentally (D-090(d)). It authorises no publication,
deployment or visibility change; the licence remains DEFERRED (D-082(c)); a push is backup-only
on John's direction (D-089). The enforcement-publication line's four A-018 Criticals remain OPEN
AT ANVIL.

## 7. Where the build team thinks a strike would land

- The two-verifier surface: a recipient who learns "authentic" from `verify.py` and does not run
  the publication verifier. The candidate's answer is exit 3 and the word `NOT EXECUTABLE`; the
  Adversary's own evidence says words fail on contact with readers, and an exit code is the only
  thing a script reads.
- The refusal-record asymmetry in §5.
- The `[PASS]` diagnostic lines in §5.
- The Historical section: whether a labelled, disclosed route to a stale verifier is still
  "routing".
