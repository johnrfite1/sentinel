# Cycle 3 patch — handoff to the orchestrator

**From the Smith.** Session `S-20260830-sentinel-conformance-lab-r1`. Cycle 3 closed with zero
sustained Criticals (MSG-034); the candidate returned to the Smith at the Anvil (MSG-035). The
Smith ruled a narrow patch before the Quench (D-092, below) and the patch has landed. This file
carries the three items to be filed, in the order to file them. It is assembled by the build
team's coordinating agent from the repository's own record; nothing in it is new text.

---

## Item 1 — the patch commit

**`8dfaa275a669bd202c3fa45e36dc12cbbe261170`** on `step-3/isolated-signer`, the child of `02458d2`, subject
`D-092 patch: Cycle 3 findings closed before the Quench — host-clock expiry, Historical route, record`.
One commit carrying code and its own status documents. Verify with `git rev-parse HEAD` in a
tree checked out at that commit, and `git log --oneline 02458d2..8dfaa27` (one line).

Register it as the artifact the Quench decision is taken on. It is not a Cycle 4 candidate;
D-092(g) rules no further cycle. The chairs do not re-enter.

---

## Item 2 — the Smith Decision to file (D-092, verbatim from `docs/decisions.md`)

- **D-092 (2026-09-02) — CYCLE 3 RETURNED WITH ZERO SUSTAINED CRITICALS; A NARROW PATCH IS RULED BEFORE THE QUENCH, AND `verify.py` GAINS A HOST-CLOCK EXECUTABILITY CLASSIFICATION. Ruled by John, 2026-09-02, in a facilitated walkthrough with the agent's recommendations stated and taken. The agent RECORDS these and makes none of them.**

**THE CYCLE 3 RESULT.** Reviewed on `81edee1`. The Adversary, owner of the carried Critical, measured both clauses of its withdrawal condition and reported **HOLDS**; it raised no provisional Critical, so Steps 2–3 had no target and the ledger closed with **zero sustained Criticals** (MSG-034). Subtractor, Catalyst and Conscience reported the condition FAILS on one line — `README.md:234`, a fenced command running the frozen v0.2 packet verifier on a BLOCK bundle, `=> PASS` / exit 0 — which the Adversary graded a Major residue. Eighteen findings: three advisory Critical alarms, eight Major, seven Minor. The orchestrator recommends a narrow patch before the Quench. Disposition is the Smith's at the Anvil.

**TWO BUILD-TEAM ERRORS, RECORDED.** (1) Conscience found that at `be6894a` the packet commands carried a placeholder and a packet-relative path and did not run from the root; **the Cycle 3 README lane made the route to PASS/exit 0 on a BLOCK receipt copy-pasteable for the first time.** (2) The candidate's status documents were re-pointed in a commit *after* the candidate, so at `81edee1` `docs/session-state.md` and `HANDOFF.md` named the previous SHA and listed D-091(a) as an open fork — the file the README calls authoritative disagreed with the tool (Adversary Major 3). **Henceforth a candidate's status documents land in the same commit as its code.**

**(a) THE HISTORICAL SECTION.** `README.md:234` is deleted. The surviving packet command is rendered as prose, not a fence, so nothing in the Historical section is copy-pasteable. D-091(c) stands; no packet byte moves. **Rejected — delete :234 only** (leaves a fenced route to the frozen verifier); **remove the section's commands entirely** (more than asked).

**(b) THE PACKET README.** The dated note ruled at D-091(c) is **moved above** `reviewer-packet/README.md:107-108` so it is read before the commands; nothing is struck or deleted (Conscience Minor 7). **Rejected — also strike the BLOCK command** (a first edit to the Gate 8 artifact's own commands); **leave as is.**

**(c) EXPIRED RECEIPTS — `verify.py` CLASSIFIES BY THE HOST CLOCK.** Measured: the ALLOW and overridden-REVIEW fixtures expired 2026-08-29 and `verify.py` exits 0 on both; the Vault (`SentinelVault.sol:393-397`) and the publication verifier refuse them on the window. `verify.py` now compares the receipt's validity window — and the override's, where one carries a window — to the host clock and reports an authentic bundle outside its window as `=> AUTHENTIC, NOT EXECUTABLE`, exit 3, with the host clock disclosed as unauthenticated. **The authenticity certification is unchanged;** exit 3 is neither a certification nor a refusal, so an unauthenticated clock may inform it where it never could inform a PASS. This **amends the consequence recorded at D-087(c)** ("no clock") — `verify.py` still certifies nothing about execution and still authenticates no clock; it stops exiting 0 for the one remaining offline-checkable case the Vault refuses. It takes **no caller-supplied instant**: the host clock only, so no flag can restore exit 0 on an expired receipt. Built test-first under D-058(1). **Rejected — amend AC2 and kill criterion 1 to authorise the authenticity predicate** (the definitional route, rejected at D-090 for the same reason); **hold as a Quench remainder.**

**(d) THE PER-CHECK `[PASS]` LINES — D-091(b) STANDS**, graded Major by Conscience and Minor by the Adversary and Catalyst. Two wording fixes are taken as text-only changes: the refusal bundle's `[PASS] ALLOW:` line is labelled as the *requested* verdict, and the refusal path's continuation reads "neither a certification nor a rejection". **Rejected — rename the per-check prefix; no wording changes.**

**(e) THE `--tamper` SELF-TEST.** The summary reports applicable modes rejected and inapplicable modes skipped by count, and the headline says *self-test* beside the word PASS. **Exit 0 stays** — it is a self-test contract, stated in `--help`. **Rejected — exit non-zero on a non-executable sample; leave alone.**

**(f) NO DEPLOYMENT MANIFEST SHIPS (Conscience Major 2) — RECORDED AS A KNOWN REMAINDER.** The README states plainly that certifying verification requires running the demo and why (five-minute receipts; lab-generated authority). No fixture manifest is shipped. Carried into the Quench as a stated limitation on Assumption 7. **Rejected — ship a lab-signed fixture manifest and bundle** (design work, not a narrow patch); **defer without a README change.**

**(g) PROCESS.** Patch → independent verification by fresh agents reproducing every chair's failing command on the new SHA → **one commit carrying code and status documents together** → a short return note mapping each finding to its change → **the Smith's Quench decision on that SHA, without a further cycle.** Also in the patch, as routine corrections: the entry paragraph at `README.md:3` broken into readable pieces (Conscience Major 5); the false "first surface through the publication verifier only" sentences in `HANDOFF.md` and `docs/session-state.md` (Conscience Major 3); the over-broad "for anything the Vault would not execute" sentence in `docs/enforcement-release-v0.3.md`. **Rejected — a limited Adversary-only re-strike; a full Cycle 4.**

**WHAT THIS ENTRY DOES NOT DO.** It is not the Quench decision. It authorises no publication, deployment or visibility change; a push of the patched SHA is not authorised by this entry. **The licence remains DEFERRED under D-082(c).** The Existential Untested assumptions are not accepted by it.

---

## Item 3 — the build team's return note (verbatim, `docs/cycle-3-patch-return-note.md`)

Register as an `ARTIFACT`, `From: BUILD TEAM`, consumers: the Smith. It maps each of the
eighteen Cycle 3 findings to a disposition and records what the patch does not do.

# Cycle 3 patch — return note for the Smith's Quench decision

Session `S-20260830-sentinel-conformance-lab-r1`. Prepared by the build team's coordinating
agent, 2026-09-02, under D-092(g): patch → independent verification → one commit carrying code
and status documents → this note → the Smith's Quench decision on that commit, without a further
cycle. **The build team asks for no approval here.** It maps each of Cycle 3's eighteen findings
to what changed, what did not, and why.

## 1. The patch commit

The child of `02458d2` on `step-3/isolated-signer`, subject beginning `D-092 patch`. It is one
commit: `verifier/verify.py`, `verifier/test_verifier.py`, `scripts/test.sh`,
`scripts/assemble-enforcement-release.py`, `README.md`, `reviewer-packet/README.md`,
`docs/enforcement-release-v0.3.md`, `docs/decisions.md` (D-092), `HANDOFF.md`,
`docs/session-state.md`, this note, the register's §9, and the regenerated `release/`.
**Its status documents describe it and name it by parent and subject, not by a SHA written
before the commit existed** — the Cycle 3 candidate's status documents were one commit behind
it (Adversary Major 3), and that is not repeated.

## 2. Finding → change

| # | Chair, severity | Finding | Disposition |
|---|---|---|---|
| 1 | Subtractor, Catalyst, Conscience — Critical alarm; Adversary Major 1 | `README.md:234`, a fenced command running the frozen packet verifier on a BLOCK bundle: `=> PASS`, exit 0 | **Fixed (D-092(a)).** The line is deleted; the surviving ALLOW invocation is prose with no copy-pasteable command; nothing after `## Historical:` is runnable. Conscience's finding that the previous README's commands did *not* run from the root, and that the Cycle 3 lane made them runnable, is recorded verbatim in D-092 as a build-team error. |
| 2 | Subtractor — Critical alarm; Adversary Major 2 | `verify.py` `=> PASS` / exit 0 on expired ALLOW and overridden-REVIEW receipts the Vault refuses on the window | **Fixed (D-092(c)).** `verify.py` compares the receipt's window, and the override's, to the unauthenticated host clock and reports an authentic bundle outside its window as `=> AUTHENTIC, NOT EXECUTABLE`, exit 3, both endpoints and the host instant printed. No caller-supplied instant exists. Authenticity certification unchanged. Amends D-087(c)'s "no clock" consequence, recorded. Every shipped fixture is now exit 3; PASS is reachable only on a live bundle. |
| 3 | Adversary Major 3; Conscience Major 3 | Status documents at `81edee1` named the previous SHA and an already-closed fork; "first surface through the publication verifier only" false | **Fixed.** Status documents land in the same commit (§1). The false sentences are struck in place and corrected: every *fenced* pre-Historical command is `verify_publication.py`; one inline measured `verify.py` example exits 3; the Historical section carries no runnable command. |
| 4 | Conscience Major 5 | `README.md:3` one 2,015-character paragraph | **Fixed.** Four short blocks; no fact, file or limitation dropped. |
| 5 | Conscience Major 2 | No deployment manifest ships; a Python-only recipient can run no `verify_publication.py` command | **Disclosed, not changed (D-092(f)).** The README now says so plainly and why. Carried into the Quench as a stated limitation on Assumption 7. |
| 6 | Conscience Major 4; Adversary Minor 4; Catalyst Minor | Per-check `[PASS]` lines; `grep -q PASS` matches on a BLOCK run | **Ruled to stand (D-091(b), reaffirmed D-092(d)).** Disclosed. |
| 7 | Conscience Minor 6; Adversary Minor 6 | `[PASS] ALLOW:` on a refusal bundle; "refusal" in two senses | **Fixed (D-092(d)).** The line reads `[PASS] requested verdict ALLOW: …`; the refusal path's continuation reads "neither a certification nor a rejection". Text only; `Check.name` on the receipt path untouched. |
| 8 | Catalyst Major 2; Adversary Minor 5; Subtractor Minor | `--tamper all` exits 0 on a BLOCK sample; summary counted N/A modes as successes | **Summary fixed, exit unchanged (D-092(e)).** The summary states applicable and N/A counts (10 / 20 on the BLOCK sample; 14 / 16 on the refusal) and names itself a self-test. Exit 0 is the self-test contract stated in `--help`; ruled to stay. |
| 9 | Conscience Minor 7 | The packet README's dated note sits below the commands it warns about | **Fixed (D-092(b)).** Moved above them, verbatim; nothing deleted. |
| 10 | Adversary Major 1 (residue) | The packet's frozen `verify.py` still prints `=> PASS` / exit 0 on BLOCK from the packet directory | **Disclosed, not changed.** D-091(c) stands; the packet is not regenerated; the note is now read first. |
| 11 | Subtractor Part A | `README.md:112` inline current-`verify.py` example makes "only through the publication verifier" literally false | **Left, disclosed.** It exits 3 and prints `NOT EXECUTABLE`; Conscience and the Adversary both say it may stand. The status sentences now name it. |

## 3. Verification

- Fast gate: `GATE PASSED`; D-010 stage `suite 278 (floor 278) · walk exit 3 (want 3)`.
- Suites: `test_verifier` 278 OK (was 252; `TestExitContractD092` 26 tests, 18 red against the
  pre-patch verifier, 2 rewritten tests red, written by an independent author before the
  implementer touched `verify.py`); `test_publication_verifier` 105 run, 1 permanent red
  (R-A018-17); `test_publication_override` 61 OK; `test_publication_conformance` 53 OK.
- `check-release-sync.sh` and `check-release-executes.sh` clean.
- Two independent verifiers with no build context, one on the `verify.py` contract (every chair's
  failing command re-run), one on the README and record (every un-struck claim about the tool run
  and compared). Their results are in §5.

## 4. What the patch does not do

It does not unify the two verifiers (AC2's "one versioned predicate" remains deferred at
D-087(c)); it does not ship a manifest; it does not regenerate the packet; it does not rename the
per-check prefix; it does not change the self-test's exit. It authorises nothing: no publication,
push, visibility change or licence. The Existential Untested assumptions (1, 4, 5) are untouched
and remain the Smith's to accept with stated risk at the Quench.

## 5. What the two independent verifiers found

**Verifier A — the `verify.py` contract.** Forty-odd commands. Re-ran every chair's failing
command: Subtractor's two expired fixtures → `=> AUTHENTIC, NOT EXECUTABLE`, exit 3, both
endpoints and `now` printed, clock disclosed as unauthenticated; Catalyst's `--tamper all` →
`10 applicable … 20 inapplicable … N/A`, counts matching the lines printed, exit 0;
Conscience's refusal bundle → `[PASS] requested verdict ALLOW: …` and `neither a certification
nor a rejection`; `--all fixtures/samples` → 7/7 authentic, seven `NOT EXECUTABLE:` lines, exit 3.
Minted live bundles from the test helpers: live ALLOW → PASS/0; the same bundle re-windowed to
the past → 3 ("expired"), to the future → 3 ("not yet valid"); live REVIEW + live override → 0;
live REVIEW + closed override → 3 naming the override; expired REVIEW + live override → 3 on the
receipt window. Boundary: `expiresAt == now` is not executable, `issuedAt == now` is live, also
under a frozen in-process clock. Ten instant-flag spellings in three forms → argparse status 2;
argparse abbreviations resolve to `--tamper`/`--all`/`--domain`; fourteen environment variables
leave exit 3; no time-like parameter on `verify_sample`, `run` or `main`; the only clock read is
`time.time()` inside the window helper. Precedence: BLOCK, un-overridden REVIEW and refusal-record
leads win over the window; a tampered signature on an expired bundle → 1. BLOCK output differs
from `02458d2` in exactly three summary sentences, all enumerating the exit-3 set; the lead and
all 45 per-check lines are byte-identical. Vacuity, measured: 18 of the 26 new tests fail against
the `02458d2` verifier; the eight that pass pin unchanged behaviour. **(c), (d), (e) HOLD.**
Its own fast-gate run: `GATE PASSED`, floor 278 met exactly (a first run was discarded by the
gate's immutability supervisor because a docs lane edited `test.sh` mid-run, and showed the
known R-A018-26 e2e clock flake once; it did not recur).

**Verifier B — the README and record.** The Historical section has no fence and no backticked
span starting with `python3`; every backticked `verify.py` span fed to a shell fails to run; the
prose ALLOW invocation is accurate. The packet note moved verbatim, eight lines out and eight in,
nothing deleted. The entry region is twelve blocks, longest 73 words, with all 13 file names and
all 28 fact and limitation phrases of the old paragraph present and nothing new asserted. No
deployment manifest ships anywhere; `verify_publication.py` requires `--deployment-manifest` and
`--deployment-authority`. Every un-struck claim about `verify.py` in the README, the release
document, `release/README.md`, the packet README and the status blocks was run and matched.
**Every chair finding on the README and record is closed on this tree.** Seven Minor residuals
— an over-broad "every fenced command", two un-struck "no clock" / "five" sentences in dated
blocks, a timezone-dependent date, "every run" where `--tamper` runs carry no clock line, the
shipped `verify_publication.py` docstring still carrying the "anything the Vault would not
execute" phrase, and a stale list of review documents — were all fixed before the commit and
the release re-assembled; sync and execution guards clean.

**Fixed after verification, before the commit:** Verifier A found that the PASS path read the
host clock twice, so at the expiry second the headline could print a predicate false as written
while the exit status was decided on the earlier read. `run()` now reads the clock once per run
and threads that instant through classification and every printed line.

---

## What follows the filing

The Quench. It is the Smith's decision, not a review. Under the Ingot's register three
assumptions are Existential and Untested — 1 (an evaluator can tell lab authority from
production authority without the source), 4 (technical evaluators will form an accurate
impression of the engineering), 5 (the record reads as rigour, not thrash) — and the protocol
requires each to be explicitly accepted by the Smith with stated risk, or the artifact does not
ship. The patch changes none of them. A Quench is not publication: the repository remains
PRIVATE, publication is NOT AUTHORISED, and the licence remains DEFERRED (D-082(c)); those are
separate rulings. The enforcement-publication line's four A-018 Criticals remain OPEN AT ANVIL
and are not touched by this session.
