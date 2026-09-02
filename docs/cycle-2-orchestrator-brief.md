# Cycle 2 — instructions to the orchestrator

**From the Smith. Drafted by the build team for his review; nothing below is issued until he
issues it.** Session `S-20260830-sentinel-conformance-lab-r1`. Cycle 2 of cap 2.

The candidate is **`cb124feaad6b925f683b0739de53970e1700e146`**. The return package is
`Sentinel/docs/cycle-2-return-package.md`. A documentation-only follow-up, `b598280`, records
D-088 and the package; it changes no code.

---

## A. What the runbook requires before any Cycle 2 prompt

These are the orchestrator's mechanical obligations under §4 (forge cycles) and D-2. None is
optional and none is the build team's.

1. **Register the return package** as an `ARTIFACT` (`A-###`, `Type: ARTIFACT`, `From: BUILD
   TEAM` — the enum still has no seat for the builder; file it as the two Cycle 1 filings were).
   Consumers: all chairs.
2. **Update the session header.** Ingot / Artifact ID → `Sentinel conformance lab at cb124fe…`.
   Current Step → `5 — The Anvil; Cycle 2 re-strike`. Forge Cycle → `2 of cap 2`. Status →
   `OPEN — CYCLE 2`.
3. **File the patched Ingot as `ingot-c2.md`** and supersede its predecessor in the artifact
   registry (`A-001 → SUPERSEDED`, new row `ACTIVE`). The Ingot's text is unchanged from Cycle 1
   except the candidate SHA; the *tree* it names is what changed.
4. **Draft the D-2 register re-transcription for the Smith's ratification.** You draft; he
   ratifies; **every Status or Existential change is flagged by name for his explicit
   confirmation.** The build team's proposed flags are in §B below — they are proposals, and the
   register is constitutionally his.
5. **Fresh chair sessions for every re-entering chair**, per-chair launch attestation (§2.3), and
   the per-cycle canary (§3, `canary_per_forge_cycle`) — **as a checked precondition, not an
   assumption (H-1).** The Smith names which chairs re-enter; a sat-out chair keeps its labelled
   Cycle 1 brief (D-3).
6. **Verify each chair's tree before briefing it.** In the build team's own 2026-08-30 review
   round, **three of four reviewers were handed worktrees 291 commits behind the subject**, with no
   `verifier/` or `release/` directory at all. Every one caught it from its own provenance
   attestation. A reviewer that had not would have reported "no findings" on a tree where the
   artifact does not exist — a false clean. `git rev-parse HEAD` must equal `cb124fe…` in every
   chair's tree before its Step 1 prompt, and the attestation row should record it.
7. **This is cycle 2 of cap 2.** If sustained Criticals remain at the Anvil, stop cycling and
   escalate the items verbatim; a cycle 3 requires the Smith's written ledger note before any
   prompt (§4, runbook failure table).
8. **The build team's agents will not touch the repository or its worktrees while this cycle is
   live** (D-085(d)), after a reviewer and the Conscience collided in one worktree on
   2026-08-30. If a chair sees the tree move, that is a breach to report, not noise.

---

## B. Proposed register re-transcription — flags for the Smith

Drafted from the Ingot's eight assumptions against the candidate. **Only the Smith changes a
Status or Existential.** The orchestrator should reconcile these against the register as
ratified in the session ledger before presenting them.

| # | Statement (abridged) | Cycle 1 | Proposed | Why — measured |
|---|---|---|---|---|
| 1 | A technical evaluator can tell lab authority from production authority without the source | Untested / Existential | **unchanged** | The unaided audience test has still not been run. The demo now labels its authority `NOT PRODUCTION, NOT A TRUST ROOT`; that is a control, not a test of comprehension. |
| 2 | The offline verifier and SentinelVault answer the same question | Untested — **MEASURED FALSE** / Existential | **Untested → Plausible** (flag) | A signed BLOCK receipt is refused on both paths; overrides examined on every path; `operation == CALL` unconditional; the §5.6, reason-code and §5.7.1 arms ported; the 39-cell override parity matrix agrees on every authenticity cell. **Not Verified:** no shared conformance-vector corpus has been run through all three implementations — the inventory diff names that as its largest blind spot. |
| 3 | A public repository for evaluators is not deployed where value is at risk | Untested / Not existential | **unchanged** | Documented only, per D-083(a). The drain and token-authority boundaries are now disclosed reader-facing. |
| 4 | Technical evaluators will form an accurate impression of the engineering | Untested / Existential | **unchanged** | Untested against the real audience. |
| 5 | The project's own record reads as rigour, not thrash | Untested / Existential | **unchanged — and note** | The concise entry-point paragraph Cycle 1 asked for is **still owed** (return package §9). The record grew by four rulings, a register, a diff, and a return package since Cycle 1. |
| 6 | The mechanism is sound for the supported action class | Plausible / Existential | **unchanged** | 105/105 Foundry; nothing in this candidate touches the Vault. |
| 7 | A recipient can reproduce the demonstrated result from the published repository | Untested / Not existential | **Untested → Plausible** (flag) | The shipped verifier is now *executed* by a guard, not only digested; `npm test` in the release refuses honestly rather than passing on zero tests; the cold demo runs 7/7 with a genuine BLOCK case; vendored LICENSEs ship; the verification section is runnable as written. **Not Verified:** toolchain unpinned; the recipient walkthrough was one machine. |
| 8 | v0.2 corpus and v0.3 semantics can coexist without misrepresenting either | Untested / Not existential | **unchanged** | The A-111 hold stands; the deep profile is red on the §7.1 digest by design; nothing touched. |

Two flags, both upward, both stopping short of Verified. If the Smith declines either, the
candidate is unchanged — the register describes belief, not the tree.

---

## C. Where the build team would strike — offered, not prescribed

**This section is a courtesy and the chairs may ignore it.** It is the builder saying where it
thinks the work is weakest, on the theory that a council which finds nothing here should look
elsewhere, because the builder has blind spots. It is not a checklist, and a chair that treats it
as one has been steered. The Cycle 1 handoff's own rule governs: *passing tests alone will not
withdraw the findings unless the tests directly observe the original defects.*

**1. Do not trust the package's mutation evidence — reproduce it.** The package says reverting
the override hoist fails exactly two named tests, and restoring the `evaluation_time` guard fails
exactly four. Revert them yourself. If a different set fails, the package is wrong about what
observes what.

**2. The three R-A018-04 tests kept their names and changed their bodies.** The defence is
D-086(e) and the council's own words — *the result must stop claiming properties it did not
authenticate* — but a chair is entitled to call this moving the goalposts. Mutation-test the
redefined bodies. If `test_a_fabricated_runtime_code_hash_is_echoed_as_authenticated` still passes
when the hash is printed bare in the headline, the redefinition is vacuous.

**3. The one permanent red.** `test_calldata_redirecting_the_mandated_beneficiary_is_refused` is
red by ruling and rebuilt to fail on the ruled defect itself. A methodological challenge is
available: is a test that documents a disclosed, ruled-open defect a *test*, or a comment wearing a
test's clothes? The build team thinks it is a test because a green there is an alarm (calldata was
decoded against D-083(b)) and an error there is a staging fault. The council may disagree.

**4. §5.7.1 conformance is named "signer-attested record conforms to mandate".** Stage a lying
signer — record honest to the mandate, calldata redirected — and confirm it **certifies**, as
disclosed. Stage a misconfigured-honest one — record confessing the redirect — and confirm it
**refuses** by that name. If the check catches the liar, its name is wrong; if it misses the
confessor, the check is wrong.

**5. The execution guard states what it does not run: the release's Anvil demo.** From a clean
checkout of `cb124fe`: `npm ci`, `forge build`, `npm run cold-demo -- --output "$PWD/demo-out"`.
That is the only thing that exercises the shipped TypeScript, the shipped contracts, and the
demo's own verifier calls. The guard's honesty about its limit is the map to its blind spot.

**6. The A/B split against acceptance criterion 2.** The Ingot says *one versioned executable
predicate*. The candidate has two verifiers with different, now-stated, claims — `verify.py`
certifies authenticity and has no clock; the publication verifier certifies executability. D-087(c)
ruled the split intended and deferred unification to *a later batch*. **Does the Ingot permit that
deferral?** The build team recorded the question and did not answer it.

**7. D-088 exempts `verify.py` from `operation == CALL`** on the reasoning that it is an
executability condition and `verify.py` certifies authenticity. `verify.py` is the surface Gate 8's
reviewers read as source. A DELEGATECALL receipt gets `PASS: AUTHENTIC` there. A chair may find the
exemption a rationalisation; the build team recommended it and says so.

**8. §5.5.1 recognition — recognise and refuse, do not verify (D-087(d)).** Confirm a refusal
bundle is refused *because it is recognised* — the message names `refusal record` /
`SignedRefusalRecord` / `5.5.1` and says this verifier does not certify refusals — and not for some
other reason whose message happens to contain the word. Then confirm no refusal check ran.

**9. What Cycle 1 asked for and is not done.** The package's §9 says so plainly: the concise
entry-point paragraph (acceptance criterion 8), "independent" terminology, and naming
disambiguation at the first surface are **open**. The build team is not claiming them. If the
council sustains any as a Critical, the build team will not contest it.

**10. The Existential Untested assumptions — 1, 4, 5.** None has been tested against the named
audience. The Quench requires each to be explicitly accepted by the Smith with stated risk, or the
artifact does not ship. That is not the build team's to answer and it is not answered.

**11. The build team's own error rate.** Four measured claims it supplied at moments of decision
were wrong — "17 call sites" (20), "exactly two instances" (an anchored regex), "no independent
downstream check" (false), "branch pushed" (false). All are in the ledger. **A chair should weigh
that against every number in the return package and re-measure rather than read.** The inventory
diff — mechanical extraction instead of hand-grepping — was the structural response, and it is
where a chair should look for whether the method actually changed.

---

## D. What the build team is not asking for

Per the Cycle 1 handoff's own out-of-scope list: no publication, push, deployment, release, or
visibility change; no licence selection; no conversion to a production product; no aggregate
token cap; no live RPC; no calldata decoding; no history rewrite. **The build team asks the
council to withdraw neither Critical on the strength of this package.** It asks the council to
test whether the named tests observe the original defects, and to rule on what it finds.
