# D-055 exit record (D-073)

**2026-08-24. D-055(a)'s terminating condition is MET (D-073, John, Session Six).**
This file is no longer prepared material. It is the exit record. **A MET D-055
unlocks nothing.** D-048 makes a clean result a PRECONDITION, never a trigger.
D-016 blocks publication and the rename. Gate 8 is pre-publication under D-032
and needs the D-009 dashboard and John's five held questions, which the build
loop never sees. No gate is signed or reopened. The §14.8 ladder is still not
an agent's to start climbing.

The session record lives in `docs/decisions.md` (D-073). A-104 is the agent
entry that froze this record. Session Five's NOT MET (at `dffe6f8`) is history;
its reversal condition fired on the six gating items and the clauses below.

For each of D-055(a)'s conditions and each of T1–T4: what was measured, when, at
what commit, by whom, and — stated as plainly as the rest — **what is not
established.** A met exit criterion is evidence only for what D-055(a) asked.

---

## D-055(a) as ruled

Exit requires, replacing D-047:

1. one independent, FIXED-SCOPE post-D-052 review using the REPAIRED apparatus;
2. a passing deep gate and workspace guards;
3. ZERO unresolved confirmed Critical/High defects;
4. ZERO known false or unsupported signed/certified claims.

Confirmed Medium/Low findings may remain only when individually adjudicated,
accurately documented as limits, and reflected in affected claims. "Zero
findings of any severity" is expressly not the termination condition.

John's clarification: an unadjudicated Critical/High lead is PENDING, not
silently "unconfirmed". A confirmed High ceases to block only through verified
repair, or through John's explicit acceptance as a documented product boundary.

T1–T4 were adopted with it. They are recorded below as themselves, not as a
second exit.

---

## Condition 1 — SATISFIED. The qualifying review still qualifies.

**What was measured.** D-055(e) (2026-08-18): four reviewers, scope fixed by
John in advance (D-056(d)), each in its own worktree with its own persistent
evidence directory, at most two concurrent, every deliverable written to disk
before the reviewer was counted complete. Returned 23 finding IDs (22 confirmed,
1 refuted) including a CRITICAL in the certification gate (`R1-F1`). John ruled
on all of them (D-057). The evidence directory is
`docs/review-2026-08-18-d055e/` with briefs preserved unaltered. Frozen commit
reviewed: `7e0ab7f1057de278c09cc803ab4ca266f53399e1`.

**Drift, ruled rather than left to implication.** Session Five deferred
apparatus-drift as a disposition, not a gating item. Session Six ruled: **the
review still qualifies.** D-055 deliberately replaced D-047's unbounded loop so
that later repairs do not re-trigger the qualifying review; ruling otherwise
would restore that loop under another name. The instrument rewrites since are
**the repairs that review demanded** (A-077, A-078, the batch cards).

**Counts, independently remeasured, not copied from the session note.**

Session Six's note cites 122 commits / 685 new tracked files / 678 under
`docs/` / 571 in the batch-card evidence tree / 7 non-doc. Those figures are
exact at Session Five's freeze `dffe6f8a0048fc3f051e766c453537dd8d883e81`
(`git diff --diff-filter=A --name-only 7e0ab7f dffe6f8`; `git rev-list --count
7e0ab7f..dffe6f8`).

Session Six names freeze `8c74537f9d85f97b1d0133fd6869e3d79115c8ef` (A-103).
Remeasured there against the same D-055(e) base:

| | `dffe6f8` (Session Five) | `8c74537` (Session Six freeze) |
|---|---|---|
| commits since `7e0ab7f` | 122 | 123 |
| new tracked files (`--diff-filter=A`) | 685 | 687 |
| of those under `docs/` | 678 | 680 |
| of those under `…/batch-cards/` | 571 | 572 |
| new non-doc | 7 | 7 |

The two files added at A-103 are
`docs/review-2026-08-19-d057-targeted/batch-cards/D062-containment-tests/RESIDUAL-SEVERITY.md`
and `docs/review-2026-08-19-d057-targeted/critical-high-census.md` — the census
Session Five commissioned. The seven non-doc files are unchanged:

- `contracts/test/SentinelVault.binding.t.sol`
- `contracts/test/SentinelVault.events.t.sol`
- `scripts/check-findings-ledger.sh`
- `scripts/check-suite-floors.sh`
- `scripts/check-v1-index-ordering.sh`
- `scripts/extract-markdown-section.py`
- `ts/test/vault.snapshot.classification.test.ts`

The drift is evidence accretion. The load-bearing figure — seven new non-doc
files — is the same at both freezes.

**What is not established.** Whether any later independent review is owed for
any purpose other than D-055(a) condition 1. Condition 1 does not re-open
because instruments were repaired.

---

## Condition 2 — SATISFIED at the Session Six freeze.

**Verified-origin isolated exact-commit deep gate** at
`8c74537f9d85f97b1d0133fd6869e3d79115c8ef`, out of tree
(`_sentinel-out-of-tree/a103-verified-gate-2026-08-23/`). Clone porcelain empty
before and after `--gate`. `origin` =
`https://github.com/johnrfite1/sentinel.git`. Acknowledgement variable
`SENTINEL_RENAME_GATE_UNVERIFIED_OK` unset. Quoted from `gate.log`, not from
exit status:

```
rename gate: clean (johnrfite1/sentinel is private; D-016 publication block intact)
```

```
vendor honesty: mechanical conditions pass; D-008(1) met and (3) certified by record
```

```
GATE PASSED
```

Wrapper exit `0` (`gate-exit.txt`). Coverage of the rename line: origin
visibility via `gh` only. D-071's "Not covered: demos, published links,
portfolio or resume references" is not printed on the pass branch.

An earlier acknowledged run (Phase B, A-101) printed UNVERIFIED and disclosed
acknowledgement. That run is not this condition's evidence.

**A-104's isolated exact-commit `--gate` is after the freeze that creates its
SHA**, same sequencing as A-102/A-103, reported out of tree. It is not a
committed fact inside this file.

**What is not established.** Whether any later freeze still passes. Condition 2
at D-073 is the 8c74537 run.

---

## Condition 3 — SATISFIED. Each Critical/High retired by a named clause.

The census of record is
`docs/review-2026-08-19-d057-targeted/critical-high-census.md`.

| ID | Severity | Clause applied |
|---|---|---|
| `R1-F1` | Critical | Verified repair — A-078 independent HOLD |
| `R1` | High | Verified repair — F61ECCA independent HOLD |
| `R5` | High | Verified repair — D-071, card HOLD |
| `V-6` | High | Verified repair — D-072, card HOLD |
| `V-1` | High | Verified repair — A-098's behavioural guard, independent HOLD |
| `R-C` | High | Verified repair — D-072's pin (coverage explicit; see census) |
| `V-3` | UNSCORED | John's explicit acceptance as a documented product boundary |

**V-1.** The defect was that nothing observed the unset-before-resolve
ordering. A-098 observes it. Independent HOLD at review-only
`8d8820c03043844b3281d35d81578890eee1ecdf`. The facilitator confirmed it FAILS
against an order-preserving refactor that a source-text lint would pass.
Reversing the ordering still reopens the hole; the guard is required to fail.

**R-C.** The D-072 card HOLD is scoped to V-6 **and** to default-mode
`check-secrets.sh` (REQUIRED rows `V6-*-secrets`). R-C is that secrets path.
Independently remeasured at `8c74537` on all five live vectors (COUNT, GLOBAL,
SYSTEM, HOME, XDG): unpinned listing hid the plant; the pin restored it;
production `check-secrets.sh` BLOCKED and never printed `secret guard: clean`
over it. See the census. Not assumed.

**V-3.** Unprobed TOCTOU on the validate/scan windows. The adjudicator declined
to score it without a timing probe rather than guess. Accepted because
`scripts/check-secrets.sh` lines 148–152 already declare the same-user
limitation: *"NOT a defence against a hostile process running as this same
user, which can replace git's temporary index between validation and scan, and
can equally well edit this file."* The hook states the same bound. John accepts
a boundary the product already states. Reflected here and in the census per
D-055(a). Not repaired. Not probed.

The F61ECCA class HOLDs on all six (`INDEPENDENT-REVIEW.md`). `R3` remains
dispositioned (D-068(6)). Medium/Low residuals stay scored and unrepaired in
this stretch; they are not condition-3 blockers.

**What is not established.** Whether every Medium/Low residual would stay below
High if rescored. Condition 3 asked for unresolved confirmed Critical/High.
Those are retired.

---

## Condition 4 — SATISFIED.

**D-069 applied.** The signed paragraph at `docs/gate-s2-evidence.md` (the block
ending that §11 is part of what was signed) is preserved byte-exact relative to
Phase A. Immediately after it, as its own blockquote, the ratified annotation
sits with identifier **D-069**. Both of the paragraph's claims about §11 are
true of §11's own body; they are **false as read today of subsection §11.0
alone**. **The 2026-08-16 signature does not cover §11.0.**

`docs/gate-s1-evidence.md` remeasured `git hash-object` at this working tree:
`66f7b843888cf1eca7d719d0f23c6120969fae30` (matches the A-103 working-tree
measurement). This stretch does not edit it.

**Class-count contradiction, resolved under D-070.** Credit iff an ABOUT check
ran against the named phenomenon and recorded the outcome the spec assigns to
it, UNRESOLVED included. Guard credit loop and ratchet unchanged. The four
blind spots remain recorded beside the figure. Register `G-3` names three
UNRESOLVED-only credited classes. `D-09`(a),(b) T1 row: stated basis
`*(none recorded)*`; verification **No basis to verify**.

A-096 superseded A-077's detail sentence. The register/pack contradiction was
fixed at A-103.

Live prefix vs frozen D-CLAIMS pin: authorised D-069 text in the prefix.
A-100 dispositions both frozen-harness control failures. Neither frozen
harness is rewritten.

**What is not established.** Whether any other signed or certified sentence is
presently false. This record did not re-audit the signed packs beyond the
hashes above and the D-CLAIMS / A-EXTRACT dispositions already recorded. A MET
D-055 certifies no public claim.

---

## `R2` and `V-6` — D-067 limits HISTORICAL as of D-073

D-072 pinned `core.excludesFile=` and `core.quotePath=false` at enumerating
call sites. Independent HOLD in the D-058(1) shape (D-071/D-072 card). V-6
measured effective on five vectors; R2 at the vendor consumer, the only place
it applied.

**D-067 named `R2` and `V-6` as completeness limits on D-008(2) and D-008(4).**
Those limits **stood from D-067 until D-073** and now lift. They are recorded
as HISTORICAL on D-067 rather than deleted. **D-067's §7.2 admissibility
sentence is untouched and stays exactly as scoped.** This lift does not
recertify Gate 5 and does not touch D-059(1)'s three verbs (not revoked,
reaffirmed, or recertified).

---

## What remains carried — every named residual has a disposition

| Item | Standing | Disposition |
|---|---|---|
| `R1-F1` (certification gate) | Independent HOLD (A-078) | Verified repair; not reopened |
| F61ECCA `C4`, `C6a`–`C6d`, `R1` | Independent HOLD; `R1` High | Verified repair; High takes the repair clause |
| `R2` | Closed at enumerating call sites (D-072) | D-008(2)/(4) limit **HISTORICAL** as of D-073 |
| `R3` | Permanent recorded limit (D-068(6)) | Dispositioned; frozen A1 harness untouched |
| `R5` | Repaired as D-071 option C | Fast UNVERIFIED exit 0; deep refuses unless ack; ack discloses |
| `V-6` | Closed at the pin (D-072) | D-008(2)/(4) limit **HISTORICAL** as of D-073 |
| `V-1` | High, verified repair (A-098) | Retired under D-073; guard remains load-bearing |
| `V-3` | UNSCORED; accepted boundary (D-073) | Source declaration in `scripts/check-secrets.sh` 148–152 |
| `R-C` | High, verified repair (D-072 pin) | Coverage explicit in the census; same call site as V6-*-secrets |
| `V-2`, `V-4` | Independent residual Low | Scored; not repaired in this stretch |
| `V-5`, `V-7`, `V-8`, `V-9` | Independent residual Info | Scored; not repaired in this stretch |
| `V-10` | Independent residual Medium | Scored; not repaired in this stretch |
| `R-A`, `R-B`, `R-D`, `R-E` | Independent residual Info | Scored; not repaired in this stretch |
| `R-F` | Independent residual Medium | Scored; not repaired in this stretch |
| Gate 5 certification | Standing (D-059(1) option A) | Not revoked, reaffirmed, or recertified |
| D-008(2)/(4) completeness limits | Named at D-067 | **HISTORICAL** as of D-073 |
| A1 | Closed through D-062 exception | No reopening; test-clause lifts spent |
| D-016 | Stands | Repository PRIVATE; no push, publication, or rename |

Batch cards' completeness claims remain bounded to their declared boundaries
and do not become repository-wide. D-060(1)'s abandonment of repository-wide
enumeration guarantees is unchanged.

---

## T1 — a limit's basis must be verified, not just its wording

**Remaining accepted limits**, as derived in §11.0 and register §13.4, not
re-counted by hand here: `D-07`, `D-09`(a),(b), `E5`, `F-VAULT-4`,
`F-VAULT-5`, `G-3`. (`D-09`(c) was reopened and then FIXED at A-076; `D-09`
therefore sits in both the fixed and accepted sets.) **V-3 is now among
accepted limits**, with its basis the source declaration cited above.

**What is not established.** This stretch did not re-run those basis probes.
Register §13.4 is a maintained table this project has already caught stale.

---

## T2 — severity is assigned by the independent reviewer/adjudicator

D-057(4) countersigned three downgrades. The F61ECCA reviewer assigned `R1`
High. An independent adjudicator scored V-1–V-5, V-7–V-10 and R-A–R-F. V-3
was left UNSCORED rather than guessed, then accepted by John as a documented
boundary. R5 and V-6 were scored High on the D-071/D-072 card at their
pre-repair parents.

**What is not established.** Whether every other residual has an independent
severity John has countersigned.

---

## T3 — scope is fixed by John before the review

D-056(d) fixed the D-055(e) scope. D-058 abandoned the repository-wide
contract method after two independent audits failed. Subsequent work has been
batch cards whose completeness is inside a declared boundary.

---

## T4 — carried and ratcheted, from the run that happened

Written from the verified-origin isolated `--gate` at `8c74537`, out of tree
(`a103-verified-gate-2026-08-23`), not copied from an earlier pack. "Passes on
ratcheted debt" is not "clean".

### Workspace machine-state

Load-bearing measurement is against the project path whose basename is
`Sentinel` (the guard keys its baseline on `basename`).
`guards-sentinel-path.log`:

```
[machine-state] Sentinel — 13 finding(s), 13 baselined, 0 new
[machine-state] PASS
== guards: Sentinel — OK ==
```

Aspect and contrast guards **do not apply to this project and did not
execute**. They are not a pass. They are absent from that log.

A first probe against the pack's directory named `clone` printed
`13 finding(s), 0 baselined, 13 new` and FAIL (`guards.log`). That is the
basename missing the Sentinel baseline, not thirteen new findings in the tree.

### Corpus classes, as that gate enumerated them

`ok 14 of 20` with D-070's rule on the same line (`gate.log`). Carried, never
counted as covered:

- RESERVED `unexpected-internal-call` [D-025]
- DELEGATED `reentrancy-attempt` [A-036]
- DELEGATED `invalid-or-rotated-signer` [D-010]
- DELEGATED `malicious-retrieved-instructions` [A-028 F-5]
- DELEGATED `owner-override-and-block-behaviour` [D-039]
- GAP `conflicting-block-state` [D-039] — **OWES A FIXTURE at v1.1**

Three of the fourteen credited classes are credited by UNRESOLVED only, under
D-070's rule. The four D-070 blind spots remain.

### Six suite floors (that run)

Printed in `gate.log`: foundry 103 (floor 103); typescript 550 (floor 550);
suite 221 (floor 221); samples 7 (floor 7); tamper 78 cases / 30 modes
(floors 78/30). Headroom on each printed floor was 0.

### Vendor honesty

- D-008(1) and (3): certified by record. The script states it did not and
  cannot check the certification is right.
- D-008(2) and (4): re-measured each run. The D-067 completeness limits on
  those two scans are HISTORICAL as of D-073.

### Rename gate

**Verified** (acknowledgement unset; no `UNVERIFIED` line). Coverage = origin
visibility only.

### Not gate stages

`scripts/check-findings-ledger.sh` and `scripts/check-review-scope.sh` are not
invoked from `scripts/test.sh` or `.githooks/pre-commit`.

---

## Deferrals, recorded as dispositions

John named these deferred. Deferral is a disposition (D-059(2)), not an open
inventory item, and not a new precondition:

- `docs/exit-criterion-packet.md` §7 reconciliation
- `NEW-FINDINGS.tsv` repair annotations
- sanitization-manifest rows for the session-four redacted files
- harness-pin disposition (`VERIFICATION.md` pin vs post-redaction hash; the
  verifier's pin is not overwritten)
- the three items volunteered and not done: the class-coverage visibility
  sentence, the "eight bases hold" headline, the rename-gate pass line

**Do not work them.**

---

## What this dossier is not

It is not a publication path, a rename plan, a Gate 8 packet, a v1.1 plan, or
any follow-on stretch. It does not sign, reopen, or annotate a gate. It does
not recertify Gate 5. It does not certify or alter a public claim. It does not
rewrite a frozen harness. **A MET D-055 certifies nothing and unlocks
nothing.**
