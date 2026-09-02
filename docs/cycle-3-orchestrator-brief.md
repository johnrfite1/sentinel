# Cycle 3 — instructions to the orchestrator

**From the Smith. Drafted by the build team for his review; nothing below is issued until he
issues it.** Session `S-20260830-sentinel-conformance-lab-r1`. **Cycle 3, past the cap of 2,
extended by the Smith's written ledger note** — that note is the D-090 entry in
`Sentinel/docs/decisions.md`, and D-091 is its rider.

The candidate is **`81edee1a770648345401ea782b4928c382d3602f`**. It is the second of two commits:
`0bc79a8` closed the sustained Critical's withdrawal condition as written and was independently
verified; `81edee1` adds D-091(a) after the Smith ruled the three forks that verification
surfaced. **Review `81edee1`.** `git diff --stat be6894a 81edee1` is the whole change from the
annotated Cycle 2 candidate. A documentation-only follow-up, `0893e58`, carries the return note,
register §8 and the session-state pointers; it changes no code. The return note is
`Sentinel/docs/cycle-3-return-note.md`.

---

## A. What the runbook requires before any Cycle 3 prompt

Mechanical obligations under §4 (forge cycles), §3.2 and D-2. None is optional and none is the
build team's. Item 1 is new and comes first.

1. **File the Smith's written note as a `SMITH DECISION` message before anything else.** Runbook
   §4 permits a cycle past the cap only on the Smith's written ledger note. D-090(c) says: *"this
   entry is that note, for the orchestrator to file as a SMITH DECISION message."* File the D-090
   entry verbatim, and D-091 with it as the ruling on the forks the first candidate disclosed.
   **No chair prompt precedes that filing.** If the note is not in the ledger, Cycle 3 has not
   begun.
2. **Ask the Smith to state, in that filing, what follows Cycle 3.** The runbook's failure table
   ends at "escalate the items verbatim" once the cap is reached. Cycle 3 is already past it. The
   build team does not know whether a sustained Critical at the end of Cycle 3 means a further
   written extension, an Override-in-Writing under §3.2, or a halt — **and it must not be the
   build team's proposal that fills that gap.** The orchestrator should put the question, and the
   Smith should answer it before the chairs sit, so that no one is deciding it after the report.
3. **Register the return note** as an `ARTIFACT` (`A-###`, `Type: ARTIFACT`, `From: BUILD TEAM`,
   the same non-seat filing as Cycles 1 and 2 — the §5 enum gap is recorded in register §7).
   Consumers: all chairs.
4. **Update the session header.** Ingot / Artifact ID → `Sentinel conformance lab at 81edee1…`.
   Current Step → `5 — The Anvil; Cycle 3 re-strike (extended)`. Forge Cycle → `3 — past cap 2,
   by SMITH DECISION <message id>`. Status → `OPEN — CYCLE 3`.
5. **File the patched Ingot as `ingot-c3.md`** and supersede `ingot-c2.md` in the artifact
   registry. Text unchanged except the SHA; the tree it names is what changed.
6. **Draft the D-2 register re-transcription for the Smith's ratification.** You draft; he
   ratifies; **every Status or Existential change is flagged by name for his explicit
   confirmation.** The build team's proposals are in §B — proposals only.
7. **Fresh chair sessions for every re-entering chair**, per-chair launch attestation (§2.3), the
   per-cycle canary (§3, `canary_per_forge_cycle`) as a checked precondition, not an assumption
   (H-1). The Smith names which chairs re-enter. **The Adversary sustained the Critical and must
   re-enter**; whether the other three do is the Smith's, and a sat-out chair keeps its labelled
   Cycle 2 brief (D-3).
8. **Verify each chair's tree before briefing it.** `git rev-parse HEAD` must print
   `81edee1a770648345401ea782b4928c382d3602f` in every chair's tree before its Step 1 prompt, and
   the attestation row records it. The 2026-08-30 precedent — three of four reviewers handed
   worktrees 291 commits behind the subject — has not been forgotten and has not recurred, and
   the reason it has not recurred is this step. The candidate's own `verifier/verify.py` prints
   `=> AUTHENTIC, NOT EXECUTABLE` on `fixtures/samples/case-2-injection-block`; a chair whose tree
   prints `=> PASS: AUTHENTIC` there is on the wrong commit and should say so before doing
   anything else.
9. **Scope.** D-090(c) scopes Cycle 3 to *"a narrow candidate closing the sustained Critical's
   withdrawal condition as written, plus (d)"* — (d) being the entry-point paragraph. The chairs
   are not bound to look only there; anything they find is theirs to raise. But the build team
   asks that the Cycle 3 verdict be stated in two parts — **the sustained Critical: withdrawn or
   sustained, against its own withdrawal condition** — and, separately, anything new. A verdict
   that conflates the two is one the Smith cannot act on.
10. **The build team's agents will not touch the repository or its worktrees while this cycle is
    live** (D-085(d)). If a chair sees the tree move, that is a breach to report.

---

## B. Proposed register re-transcription — flags for the Smith

From the Ingot's eight assumptions against `81edee1`. **Only the Smith changes a Status or
Existential.** Reconcile against the ledger's ratified register before presenting.

| # | Statement (abridged) | Cycle 2 | Proposed | Why — measured |
|---|---|---|---|---|
| 1 | A technical evaluator can tell lab authority from production authority without the source | Untested / Existential | **unchanged** | Still not tested against the audience. |
| 2 | The offline verifier and SentinelVault answer the same question | Plausible (if the Smith ratified the Cycle 2 flag) / Existential | **unchanged — note** | The Cycle 2 Critical was precisely that `verify.py`'s *exit status* answered a different question from the Vault while its README route said otherwise. The candidate does not make the two verifiers one predicate (D-087(c) still defers that); it makes `verify.py`'s exit code stop saying "pass" for anything the Vault would not execute — BLOCK, override-less REVIEW, and now a §5.5.1 refusal record. **Not Verified:** no shared conformance corpus across all three implementations, as in Cycle 2. |
| 3 | A public repository for evaluators is not deployed where value is at risk | Untested / Not existential | **unchanged** | Documented only. |
| 4 | Technical evaluators will form an accurate impression of the engineering | Untested / Existential | **unchanged** | Untested against the audience. |
| 5 | The project's own record reads as rigour, not thrash | Untested / Existential | **unchanged — the owed item is delivered** | The concise entry-point paragraph owed since Cycle 1 is now the first thing in `README.md` (D-090(d)): mechanism, limitations, status, archive map. Whether it *reads* as rigour is the audience test, still unrun. The record grew by two rulings, a return note and this brief since Cycle 2. |
| 6 | The mechanism is sound for the supported action class | Plausible / Existential | **unchanged** | Nothing in this candidate touches the Vault or the TypeScript. |
| 7 | A recipient can reproduce the demonstrated result from the published repository | Plausible (if ratified) / Not existential | **unchanged** | Two independent verifiers each ran the cold demo from a clean `release/` and the README's commands as written on this tree. Toolchain still unpinned (R-A018-13). |
| 8 | v0.2 corpus and v0.3 semantics can coexist without misrepresenting either | Untested / Not existential | **unchanged** | A-111 hold stands. The v0.2 packet now carries a dated note saying its `verify.py` is the frozen copy (D-091(c)); nothing in it is regenerated. |

**No flags.** The build team proposes no Status change this cycle. The candidate answers one
sustained Critical; it does not move belief on any assumption the register tracks.

---

## C. Where the build team would strike — offered, not prescribed

**A courtesy the chairs may ignore.** The Adversary struck S6 of the Cycle 2 list — the place the
build team said it thought the work weakest — and sustained it. That is the strongest argument
for reading this section and the strongest argument for ignoring it: the build team's blind spots
are, by definition, not on it.

**1. Reproduce the withdrawal condition yourself, clause by clause.** Clause 1: read `README.md`
top to bottom, list every command before `## Historical:` (line 138), and confirm none invokes
`verify.py`. Clause 2: run `verifier/verify.py --domain fixtures/samples/domain.json` on every
bundle under `fixtures/samples/`, on `--all`, and on a REVIEW bundle with `override.json`
deleted (no such fixture ships — construct it). The return note's tables are the build team's
runs; **do not read them, re-run them.**

**2. Then try to reach exit 0 from a verdict the Vault refuses by any path the candidate did not
think of.** Multi-positional ordering, a symlinked bundle, a BLOCK receipt with a foreign
`override.json` beside it, a refusal record with a receipt spliced in, `verify.py` invoked from
inside `reviewer-packet/`, the `--tamper` mode. The classifier reads the signed verdict and the
presence of `override.json`; if a chair can make it read anything else, the fix is narrower than
the defect.

**3. `verify_sample()` and `run()` are unchanged in what they return.** An in-process caller
still gets `ok=True` for an authentic BLOCK receipt; only the CLI's headline and exit changed.
The withdrawal condition says *recipient-facing*, and the build team read that as the CLI. **A
chair may read it as any surface a recipient can call**, in which case the Python API still says
"ok" for a BLOCK. The build team did not extend the ruling there and says so.

**4. The per-check `[PASS]` lines — D-091(b), ruled to stand, disclosed.** A BLOCK run still
prints ~27 `[PASS] …` diagnostic lines; a refusal run prints `[PASS] ALLOW: the signer-attested
decoded parameters conform to the mandate (§5.7.1)`, where `ALLOW` is the *requested* verdict,
not a signed one. `grep -q PASS` matches on every one of them. The Adversary's Cycle 2 evidence
was that readers do not parse disclaimers; the build team's answer is that scripts parse exit
codes. **This is the same argument the Adversary already won once.**

**5. The word "refusal" in the refusal-record headline.** The continuation line reads `Exit status
3: neither a certification nor a refusal.` one sentence before `the signer's refusal to issue a
receipt`. The verifier judged it clear in context. A chair who reads it cold may not.

**6. Is a labelled, disclosed route to a stale verifier still "routing"?** The reviewer-packet
section is retained under `## Historical:` and its `verify.py` still prints a bare `=> PASS` /
exit 0 on a BLOCK; the packet's own README now carries a dated note saying so (D-091(c)). Clause 1
says *only through the publication verifier*. The build team reads "routes" as the path a reader
is sent down and says the Historical section is not that path. The Adversary wrote the clause.

**7. Vacuity — check it empirically, not by reading.** `TestExitContractD090` (18 tests) and
`TestExitContractD091` (13) must fail against the verifier that had the defect. Check out
`be6894a:verifier/verify.py` into a scratch tree and run both classes against it; the build team's
verifier measured 10 of 14 D-091 tests red and every D-090 observation red. If a chair measures
otherwise, the tests are not observing what they claim.

**8. The gate as a control.** `scripts/test.sh:975-980` fails the D-010 stage unless
`--all fixtures/samples` exits exactly 3. Change the `3` to `0|3` and confirm the gate goes
green on a tree with the defect restored — i.e. confirm the guard is load-bearing. Then confirm
`VERIFIER_MIN_TESTS=252` refuses a suite of 251.

**9. AC6 and AC8 — claimed discharged incidentally.** D-090(d) says the entry-point paragraph *is*
the mechanism/limitations/status/archive-map paragraph the two advisories asked for. The build
team wrote it; whether it discharges them is the chairs'. Read it against the release's own
`NOT ESTABLISHED` output and against `docs/enforcement-release-v0.3.md`: every claim in that
paragraph should map to a shipped control or a stated limitation, and any that does not is AC6
still open.

**10. Three surfaces the first verifier found stale after the contract landed** — the
enforcement-release document's consequences table, the *shipped* `verify_publication.py`
docstring, and the packet README — were on no one's list until a fresh agent walked every
`verify.py` mention. The build team fixed them and then a second verifier found a fourth (the
generated `release/README.md`). **Walk every mention yourself**: `grep -rn "verify.py"` across
`README.md`, `release/`, `docs/`, `reviewer-packet/`, `verifier/`. Any sentence describing exit 0
or `=> PASS` for BLOCK, override-less REVIEW or a refusal record, other than one explicitly about
the packet's frozen copy, is a Critical the build team missed twice.

**11. The build team's error rate, carried forward.** Cycle 2's list recorded four wrong measured
claims. This cycle added one class, not one instance: **a contract change declared landed while
four surfaces still described the old contract**, caught only by fresh agents walking the
mentions. Weigh that against every "unchanged" and every "byte-identical" in the return note and
re-measure.

---

## D. What the build team is not asking for

No publication, push, deployment, release, or visibility change; no licence selection (DEFERRED,
D-082(c)); no conversion to a production product; no unification of the two verifiers (deferred at
D-087(c) and not attempted here); no change to the five advisory Criticals beyond what §C.9
describes; no history rewrite; nothing in the enforcement-publication line, whose four A-018
Criticals remain OPEN AT ANVIL. **The build team asks the council to withdraw the sustained
Critical only if its own withdrawal condition is met on `81edee1` as measured by the chairs**, and
to say in the report which clause failed if it is not.
