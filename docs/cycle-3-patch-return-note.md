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
