# D-055 condition-status — prepared material, not an assessment

**2026-08-23, after A-103 freeze. D-055 remains NOT MET on John's Session Five ruling.
This file is prepared material, not an assessment.** D-068 recorded the earlier session
without a D-055 verdict; Session Five ruled NOT MET on four named grounds. This refresh
describes the A-103 tree. It does not re-rule D-055. The session record lives in
`docs/decisions.md`. A-103.

This file is prepared material awaiting John's ruling. Nothing in it is a finding of record.
It writes into no other file, including not into `docs/exit-criterion-packet.md`. It does not
assess D-055. It does not flip, imply, or pre-compute any condition's status. It does not
write a recommended verdict. John rules D-055 at a facilitated session — he answers, not
an agent.

For each of D-055(a)'s conditions and each of T1–T4: what was measured, when, at what commit,
by whom, and — stated as plainly as the rest — **what is not established.**

---

## D-055(a) as ruled

Exit requires, replacing D-047:

1. one independent, FIXED-SCOPE post-D-052 review using the REPAIRED apparatus;
2. a passing deep gate and workspace guards;
3. ZERO unresolved confirmed Critical/High defects;
4. ZERO known false or unsupported signed/certified claims.

Confirmed Medium/Low findings may remain only when individually adjudicated, accurately
documented as limits, and reflected in affected claims. "Zero findings of any severity" is
expressly not the termination condition.

John's clarification: an unadjudicated Critical/High lead is PENDING, not silently
"unconfirmed". A confirmed High ceases to block only through verified repair, or through
John's explicit acceptance as a documented product boundary. An agent may do neither on its
own.

T1–T4 were adopted with it. They are recorded below as themselves, not as a second exit.

---

## Condition 1 — one independent, fixed-scope post-D-052 review using the repaired apparatus

**What was measured.** D-055(e) (2026-08-18): four reviewers, scope fixed by John in advance
(D-056(d)), each in its own worktree with its own persistent evidence directory, at most two
concurrent, every deliverable written to disk before the reviewer was counted complete.
Returned 23 finding IDs (22 confirmed, 1 refuted) including a CRITICAL in the certification
gate (`R1-F1`). John ruled on all of them (D-057). The evidence directory is
`docs/review-2026-08-18-d055e/` with briefs preserved unaltered.

**What is not established.** Whether that review still counts as "using the REPAIRED
apparatus" after the later A-077 / A-078 / A-081 cycle, the D-058 reset, Batch A1's two
FAILED attempts, and the D-062 containment exception. Whether any later independent review
is owed before condition 1 can be considered. John deferred apparatus-drift on
condition 1 as a disposition, not a new gating item. This file does not answer that.

---

## Condition 2 — a passing deep gate and workspace guards

Two isolated exact-commit deep gates exist after Phase B. They are different measurements.
Neither is a ruling of condition 2.

### Acknowledged run (Phase B)

**What was measured.** After the Phase B freeze (A-101), an isolated clone at that freeze
whose `origin` was the clone's own path ran `./scripts/test.sh --gate` with
`SENTINEL_RENAME_GATE_UNVERIFIED_OK=1`. The scored body printed `GATE PASSED`. The rename
stage printed `UNVERIFIED` and, on its own line, that the run **ACKNOWLEDGES D-016 was not
verified**. That is the D-071 option-C path for an origin that is not a GitHub slug. The
pack is out of tree (`_sentinel-out-of-tree/phase-b-2026-08-23/`); it is not a repository
file. Workspace guards on the freeze tree reported OK on ratcheted machine-state debt (all
baselined, none new).

**What that run does not establish.** Rename-gate privacy was **acknowledged, not verified**.
Condition 2's evidence from that run is qualified on D-016.

### Verified-origin run (this stretch)

**What is owed, and where it lives.** Isolation is the tree and the commit, not which URL
`origin` names. This stretch runs an isolated exact-commit `--gate` **after A-103 lands**,
at that freeze, with `origin` set to the repository's real remote, **without** the
acknowledgement variable. The rename stage is required to read `clean` and name the
repository as private. If it reads `UNVERIFIED`, or if the acknowledgement is reached for,
that is a result — not something to route around.

**Sequencing.** That run cannot be a committed fact inside the freeze that creates the SHA
it measures. A-102 named the same protocol; this stretch's verified-origin run is after
**A-103**, out of tree. This file records the protocol and the acknowledged sibling; it
does not pre-print the verified run.

**What is not established.** Whether condition 2 is MET. An agent filling that blank from
either run would be ruling D-055. T4's carried-and-ratcheted statement still has to be
read from the pack that actually ran, not from a prior batch-verifier.

---

## Condition 3 — zero unresolved confirmed Critical/High

**The F61ECCA class, independently HOLD.**

The bounded card at
`docs/review-2026-08-19-d057-targeted/batch-cards/F61ECCA-verification/` commissioned
independent behavioural verification of `C4`, `C6a`, `C6b`, `C6c`, `C6d`, and `R1`, with a
positive exploit control per item before the observing test. A reviewer who authored
neither the `f61ecca` repairs nor the card returned **HOLD** on all six
(`INDEPENDENT-REVIEW.md`). The harness matrix recorded REQUIRED failures: none, CONTROL
failures: none (`RESULTS.md`). `C6d` completing `GATE PASSED` from a decoy cwd was **not
observed** (wait bound); identity held (no decoy shims; Sentinel stages started). That
limit is recorded on the card. It is not a FAIL of the six.

**`R1` — first severity adjudication: High.** T2 puts severity with the independent
reviewer. A2's own adjudication said *"No claim about severity or priority."* The F61ECCA
reviewer assigned **High**: `.githooks/pre-commit` execs `check-secrets.sh --staged`; ACM
drops `R` and `T`, so a credential on a rename or typechange destination could be admitted.
Not Critical: ordinary `A`/`C`/`M` still block; with `diff.renames` off the same edit
scores `D`+`A` and ACM sees the `A`. Freeze observations: staged rename and typechange
**BLOCKED**, destinations named. Mutants printed `secret guard: clean`.

**How that High stops blocking — which clause, not a verdict.** D-055(a)'s clarification:
a confirmed High ceases to block only through **verified repair**, or through **John's
explicit acceptance as a documented product boundary**. The F61ECCA card is verified
repair at the freeze (exploit control live; freeze blocks; independent HOLD). It is **not**
John's acceptance of `R1` as a product boundary. An agent may take neither clause as
ruling condition 3 MET.

**The earlier CRITICAL (`R1-F1`).** D-055(e): certification-gate corruption, John ruled
REPAIR (D-057(3)). A-077 third design; A-078 independent HOLD. Not reopened by this
stretch.

**Census assembled at this freeze, not ruled.** Prepared material:
`docs/review-2026-08-19-d057-targeted/critical-high-census.md`. Independent residual
scores (not the D-062 verifier, not an implementer):
`docs/review-2026-08-19-d057-targeted/batch-cards/D062-containment-tests/RESIDUAL-SEVERITY.md`.

Returned to John, no retiring clause applied in this stretch:

- `V-1` **High** — unset-before-resolve remains load-bearing; A-098 is a guard, not acceptance.
- `R-C` **High** — `GIT_CONFIG_COUNT` + `core.excludesFile` as recorded; D-072 pin measured
  in scratch is not silent closure of the residual.
- `V-3` **UNSCORED** — validate/scan windows exist twice; scoring without a timing probe
  would be a guess. Pending until scored.

Assembled with a verified-repair clause named, not applied as a D-055 ruling: `R1-F1`
(Critical, A-078 HOLD), `R1` (High, F61ECCA HOLD), `R5` (High, D-071 card HOLD), `V-6`
(High, D-072 card HOLD). D-067 is not lifted.

**What is not established.** Whether condition 3 is MET. Assembling the census is not
ruling it. Two Highs and one unscored lead are returned. D-055(e)'s ledger arithmetic is
a statement about that ledger, not a live repository-wide severity census.

---

## Condition 4 — zero known false or unsupported signed/certified claims

**D-069 applied.** The signed paragraph at `docs/gate-s2-evidence.md` (the block ending
that §11 is part of what was signed) is preserved byte-exact relative to Phase A. Immediately
after it, as its own blockquote, the ratified annotation sits with identifier **D-069**.
The annotation states that both of the paragraph's claims about §11 are true of §11's own
body, still present at the end of that section and unchanged signed text; they are **false
as read today of subsection §11.0 alone**, which did not exist at signature. **The
2026-08-16 signature does not cover §11.0.** That is the only signed-prefix edit in Phase
B. `docs/gate-s1-evidence.md` is byte-identical to its pre-Phase-B blob (remeasured
`git hash-object` at the working tree before A-102:
`66f7b843888cf1eca7d719d0f23c6120969fae30`; remeasured at the A-103 working tree:
`66f7b843888cf1eca7d719d0f23c6120969fae30`).

**Class-count contradiction, resolved under D-070's rule, not by picking a side in prose.**
D-070: credit iff an ABOUT check ran against the named phenomenon and recorded the outcome
the spec assigns to it, UNRESOLVED included. The guard's credit loop and ratchet were not
changed. Remeasured immediately before A-102, `scripts/check-class-coverage.sh` prints
`14 of 20` **with that rule on the same line**. Present-tense maintained publications
carry the rule beside the figure. Signed-prefix present-tense occurrences of the figure
are historical signed text and were not rewritten.

**The four blind spots that qualify that figure** (D-070 as amended at A-103; the fourth
is the class John personally widened):

1. **malformed-calldata-or-unknown-selector** — no fixture in the class fails
   `EVAL_SELECTOR_BOUND` or `EVAL_OPERATION_SUPPORTED`.
2. **runtime-code-change-or-proxy-target** — no fixture in the class is an actual proxy.
3. **rpc-simulator-or-context-outage** — outage sibling codes on the non-null simulation
   branch never fire.
4. **evaluator-or-signer-compromise** — credited on 1 of 4 mapped codes; F057 is counted
   among the covered, so the 1-of-4 shortfall is not visible in the per-fixture note.
   This supersedes D-040(b)'s visibility sentence; the map widening stands.

**Register `G-3` (A-103).** `docs/v1-1-register.md` now names three UNRESOLVED-only
credited classes, aligned with `docs/gate-s2-evidence.md` §11.0. The prior two-class
wording is corrected, not re-adjudicated.

**`D-09`(a),(b) T1 row (A-103).** Stated basis `*(none recorded)*`; verification **No
basis to verify** — same treatment as `H-5` and `H-8`. The cell that stood there was the
severity verdict "LOW stands", which is not a file, line, count, or command. No basis
was invented. Acceptance of (a),(b) as limits is not re-opened.

**Standing.** D-057(2) ruled condition 4 **NOT MET**. That ruling is not reversed here.
The D-069 annotation and the record corrections above are facts assembled for John's
re-ruling. This file does not reverse NOT MET.

The figure is the right number under the rule and it rests on single-code credits in
several classes. Both halves are written down. Stating that is not ruling condition 4.

**Live prefix vs frozen D-CLAIMS pin, remeasured.** `d-claims.py` `C-D2-prefix` still
compares live bytes before `## 11. What is NOT in evidence` to its frozen pin. Live prefix
sha256 and that pin differ (authorised D-069 text in the prefix). Full-file sha256 differs
from A-EXTRACT `Z-signed`'s `PRE_REPAIR_SHA` blob. A-100 dispositions both as authorised
edits of a pinned file, A-097 shape. Neither frozen harness is rewritten.

**Both ways, without a verdict.**

- *That D-069 plus the class-credit rule satisfy condition 4:* the false-as-read-today
  claim D-057(2) named now carries a ratified annotation; the signed paragraph is
  untouched; the class-count contradiction is one number under one stated rule, with
  blind spots beside it.
- *That they do not:* the signed header still asserts that §11 was part of what was
  signed, and that assertion is still false for post-signature text the same document
  continues to carry. An annotation after the paragraph is not a rewrite of the
  paragraph. Blind spots on the class figure are still qualifications.

Whether that satisfies condition 4 is John's to rule.

**What is not established.** Whether any other signed or certified sentence is presently
false. This stretch did not re-audit the signed packs beyond the hashes above and the
D-CLAIMS / A-EXTRACT dispositions already recorded.

---

## `R2` and `V-6` — closed at the pin; the D-067 limits are a prepared item

D-072 pinned `core.excludesFile=` and `core.quotePath=false` at enumerating call sites.
Live exploit-then-observe controls: the five injection vectors hid plants from the
unpinned call and did not hide them from the pinned call; production secrets and
vendor-honesty scripts still saw the plants. The same `quotePath=false` recovers the
non-ASCII path the bare call octal-escapes (`R2`).

**D-067 named `R2` and `V-6` as completeness limits on D-008(2) and D-008(4).** If those
defects are closed, those limits would lift. **That is a status change John rules, not
one this file records as done.** D-067 is not rewritten. This paragraph presents the
item. It does not lift the limits.

The §7.2 admissibility ruling in D-067 is a separate sentence: that condition reads two
fixed paths and never calls `artifacts()`. Closing `R2`/`V-6` on the scans does not, by
itself, recertify Gate 5.

---

## What remains carried — every named residual has a disposition

| Item | Standing | Disposition |
|---|---|---|
| `R1-F1` (certification gate) | Independent HOLD (A-078) | Repair held; not reopened |
| F61ECCA `C4`, `C6a`–`C6d`, `R1` | Independent HOLD; `R1` High | Verified repair at freeze; High takes the repair clause, not acceptance |
| `R2` | Closed at enumerating call sites (D-072) | D-067 limit **not lifted** until John rules |
| `R3` | Permanent recorded limit (D-068(6)) | Dispositioned; frozen A1 harness untouched |
| `R5` | Repaired as D-071 option C | Fast UNVERIFIED exit 0; deep refuses unless ack; ack discloses |
| `V-6` | Closed at the pin (D-072) | D-067 limit **not lifted** until John rules |
| `V-1` | Independent residual **High**; carried, unaccepted | Returned to John. A-098 is a guard, not acceptance. **No retiring clause applied.** |
| `V-3` | **UNSCORED** (timing probe required) | Returned to John. Pending until scored. **Not probed.** |
| `R-C` | Independent residual **High** | Returned to John. D-072 pin measured in scratch is not silent closure. **No retiring clause applied.** |
| `V-2`, `V-4` | Independent residual Low | Scored; not repaired in this stretch |
| `V-5`, `V-7`, `V-8`, `V-9` | Independent residual Info | Scored; not repaired in this stretch |
| `V-10` | Independent residual Medium (silence over A2 residuals including High-class R-C) | Scored; not repaired in this stretch |
| `R-A`, `R-B`, `R-D`, `R-E` | Independent residual Info | Scored; not repaired in this stretch |
| `R-F` | Independent residual Medium | Scored; not repaired in this stretch |
| Gate 5 certification | Standing (D-059(1) option A) | Not revoked, reaffirmed, or recertified |
| D-008(2)/(4) completeness limits | Named at D-067 | Prepared item; see `R2`/`V-6` above |
| A1 | Closed through D-062 exception | No reopening; test-clause lifts spent |
| D-016 | Stands | Repository PRIVATE; no push, publication, or rename |

No named residual above is left without a disposition. A disposition is not a D-055
verdict.

---

## T1 — a limit's basis must be verified, not just its wording

**Remaining accepted limits**, as derived in §11.0 and register §13.4, not re-counted by
hand here: `D-07`, `D-09`(a),(b), `E5`, `F-VAULT-4`, `F-VAULT-5`, `G-3`.
(`D-09`(c) was reopened and then FIXED at A-076; `D-09` therefore sits in both the
fixed and accepted sets.)

**What is not established.** This stretch did not re-run those basis probes. Register
§13.4 is a maintained table this project has already caught stale. `G-3`'s credited-class
count now sits under D-070's stated rule with the four blind spots above; treating the
register as T1-complete for `G-3` without re-verifying the basis is still John's.

---

## T2 — severity is assigned by the independent reviewer/adjudicator

D-057(4) countersigned three downgrades (`R1-F2` HIGH→MEDIUM, `R1-F3` MEDIUM→LOW,
`R2-F1` HIGH→LOW) and stated the countersignature does not dispose of the underlying
finding. D-056(a) re-classified `D-10`(c) MEDIUM rather than leaving an undocumented
downgrade.

The F61ECCA reviewer assigned `R1` **High**. That is the first adjudication of that
item's severity. It is not a countersignature by John of condition 3.

**This stretch (T2).** An independent adjudicator — not the D-062 verifier, not an
implementer, not a party this exit depends on — scored V-1–V-5, V-7–V-10 and R-A–R-F.
V-3 was left UNSCORED rather than guessed. Anything High was returned, not repaired.

**What is not established.** Whether every other residual has an independent severity
John has countersigned. Whether V-3's score, once probed, is below High.

---

## T3 — scope is fixed by John before the review

D-056(d) fixed the D-055(e) scope. D-058 abandoned the repository-wide contract method
after two independent audits failed. Subsequent work has been batch cards whose
completeness is inside a declared boundary.

**What is not established.** Whether T3 requires a new John-fixed scope before any
further review that would feed D-055, or whether D-055(e) remains the one bounded
review the criterion named. That is his.

---

## T4 — the exit record states the gate's carried and ratcheted items explicitly

**The class-coverage figure is no longer a live contradiction in maintained prose.**
D-070 stated the crediting rule; the guard prints the figure with the rule; the four
blind spots are recorded. That is not T4 complete.

T4 still requires the exit record to state, in those terms, what the **deep gate that
is offered as condition 2** passed *on the ratchet* (baselined workspace findings,
carried corpus classes, rename-gate **verified** with coverage = origin visibility only,
anything else). "Passes on ratcheted debt" is not "clean". The acknowledged pack and the
verified-origin pack (out of tree, **after A-103**) are the places that statement can be
read. Filling T4 from a stale batch-verifier run is the defect T4 exists to prevent.
`scripts/check-findings-ledger.sh` and `scripts/check-review-scope.sh` are not gate
stages.

**What is not established.** Whether T4 is complete. This file does not complete it.

---

## Deferrals, recorded as dispositions

John named these deferred. Deferral is a disposition, not an open inventory item, and
not a new precondition:

- apparatus drift on condition 1 (John will rule at the next session)
- `docs/exit-criterion-packet.md` §7 reconciliation
- `NEW-FINDINGS.tsv` repair annotations
- sanitization-manifest rows for the session-four redacted files
- harness-pin disposition (`VERIFICATION.md` pin vs post-redaction hash; the verifier's
  pin is not overwritten)

## What this dossier is not

It is not an assessment of D-055. It is not a recommended verdict. It is not a
follow-on plan. It does not lift the D-067 limits. It does not sign, reopen, or
annotate a gate. It does not certify or alter a public claim. It does not rewrite a
frozen harness. D-055 remains NOT MET until John re-rules.
