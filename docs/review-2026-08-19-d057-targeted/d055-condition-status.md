# D-055 condition-status — prepared material, not an assessment

This file is prepared material awaiting John's ruling. Nothing in it is a finding of record.
It writes into no other file, including not into `docs/exit-criterion-packet.md`. It does not
assess D-055. It does not flip, imply, or pre-compute any condition's status. It does not
write a recommended verdict. John rules D-055 at a facilitated session.

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
is owed before condition 1 can be considered. This file does not answer that.

---

## Condition 2 — a passing deep gate and workspace guards

**What was measured, historically.** Each confirmed D-058 batch's independent verifier ran an
isolated exact-commit deep gate and recorded `GATE PASSED` inside that batch's boundary
(A-089, A-091, A-093, A-094, A-095). Workspace guards in those packs were reported as
passing on ratcheted debt (baselined machine-state findings, zero new at those dates).

**What is not established.** D-058(10) is the mechanical closeout that names focused suites,
fast gate, isolated exact-commit deep gate, scope / ledger / secret / workspace guards,
committed views file-by-file, ratcheted debt and coverage exclusions, at the freeze of the
complete record. That run is **Phase 2 of this stretch**, out of tree, after every Phase 1
tracked write. **T4's carried-and-ratcheted statement is the same material and is left
open below.** Filling condition 2 from a stale batch-verifier run would be the defect T4
exists to prevent. This stretch has not run `--gate` at the Phase 1 freeze; the freeze SHA
does not exist until Phase 1 lands.

---

## Condition 3 — zero unresolved confirmed Critical/High

**The one confirmed CRITICAL, and its reverification.**

- `R1-F1` (D-055(e)): the certification gate could be corrupted by a same-user child or
  concurrent process and silently exit 0. John ruled REPAIR, not accept (D-057(3)).
- A-077 (2026-08-19) implemented the third design (anonymous/unlinked read-only body plus
  external completion supervisor). Two prior designs failed and are recorded so neither is
  proposed again.
- A-078 (2026-08-19): an independent verifier who broke the previous two designs could not
  break this one. Real gate, sibling route, child route via a verbatim-bootstrap replica,
  always behind a dangerous control that was corrupted first. Exit 0 was refused when a
  probe stalled the body into an early exit. Recorded as HOLD for `R1-F1`.
- A-081 later failed eight of eleven *other* scope items at `c8d15a7`. That is not a
  reopening of the `R1-F1` HOLD; it is a different verification of later corrections.

**What is not established.** Whether any later High remains unresolved. D-055(e)'s
`FINDINGS-LEDGER.tsv` arithmetic, as re-printed by `check-findings-ledger.sh` in this
stretch's disposable clone of `8d8820c`, still derived **1 confirmed CRITICAL / 0 HIGH**
from that ledger. That is a statement about the D-055(e) ledger, not a live repository-wide
severity census. Batch A1's independently verified FAIL (both ordinary attempts) is not a
row in that ledger. Residuals `R2`, `R3`, `R5`, `V-6`, and the six `f61ecca` repairs with no
standing post-D-062 verification of record (below) have not been severity-adjudicated into
Critical/High by John. This file does not assign them a severity and does not treat their
existence as flipping condition 3.

---

## Condition 4 — zero known false or unsupported signed/certified claims

**Recorded basis for the existing ruling.** D-057(2) ruled this condition **NOT MET**, not
"contested". The reason: `docs/gate-s2-evidence.md` §11's header asserts that its content
was part of what was signed, and that assertion is false for the post-signature text it
carries. A document claiming retrospective signature for text added after signing is a
false signed claim in its own right, independent of whether the count inside it is
correct.

**What was done to the header, and what was not.** The header itself was never changed and
could not be: every byte before `## 11. What is NOT in evidence` is signed-prefix material.
This stretch re-hashed that prefix at `8d8820c`:
sha256 `470ec1de8ee696a2875334a7873e8e02504ea27d10676cb1a0018668097ba02f` (31445 bytes),
identical to the prefix at A-EXTRACT's frozen `PRE_REPAIR_SHA`
`bb664c626d592d86391f644bf014e76f2bbf7db4`. `docs/gate-s1-evidence.md` remains
sha256 `25dcefcade99e9e45be0c482f3dc5141f4d25335a920fabe1012303c7d7caf68`.

**The remedy that was applied.** A disclosure block inside §11.0 (authorised at D-057;
corrected under D-057(5) / A-077 / A-080). It states, in the subsection itself, that
everything in §11.0 post-dates the 2026-08-16 signature, that the header's assertion is
false for that subsection, and that the text is authorised at D-057 rather than
retrospectively signed. D-CLAIMS (A-095, candidate `491c035`) later edited §11.0 only —
two hunks, both after the §11 heading (measured: `@@ -514` and `@@ -549`). Full-file
sha256 moved from `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589`
(pre-repair) to `69c586d43b27df6103b4160ace285af1d9eb356838e12f4212be44d1e2c2a1ca`
(live). That is the Z-signed interaction; it is not a signed-prefix edit.

**Both ways, without a verdict.**

- *That the disclosure satisfies condition 4:* the false claim D-057(2) named is now
  disclosed in the only place an agent was permitted to write; the signed prefix still
  says what it said at signature; D-CLAIMS replaced the remaining live false headings
  inside §11.0 with struck copies plus the frozen truths; no agent has edited signed
  bytes.
- *That it does not:* the header D-057(2) named is still in the signed prefix, still
  asserting that §11 was part of what was signed, and still false for post-signature
  text the same document continues to carry. A disclosure in §11.0 does not edit the
  header. Condition 4 is "zero known false or unsupported signed/certified claims",
  and the header is a signed claim.

Whether that satisfies condition 4 is John's to rule.

**What is not established.** Whether any other signed or certified sentence is presently
false. This stretch did not re-audit the signed packs beyond the two hashes above and
the D-CLAIMS five-surface inventory already independently held at A-095.

---

## The six `NEW-FINDINGS.tsv` rows marked repaired at `f61ecca` — whole class, not `R1` alone

`NEW-FINDINGS.tsv` marks `C4`, `C6a`, `C6b`, `C6c`, `C6d`, and `R1` alike as
*CONFIRMED — repaired at `f61ecca`*. `f61ecca55557b7912cc26fddc87127cb0f6e2ebb` is Batch A1
implementation attempt two. The independent verification of that attempt
(`A2-tests/VERIFICATION-2.md`) is **FAIL overall** (item 2: clearing `GIT_INDEX_FILE`
admitted a credential through `git commit -a` / path-limited commit). D-061(4) permitted
no third ordinary attempt. D-062 later contained that named regression; it reopened no
other A1 finding.

**`R1`'s per-item HOLD is real and narrower than "nothing of record says it holds."**
VERIFICATION-2.md item 5 returned **HOLD** on staged rename-with-modification and
typechange, destination scanned and blocked, **against `f61ecca`'s bytes**. D-062 has
since changed `scripts/check-secrets.sh` and `.githooks/pre-commit`. The standing
verification of record for `R1` is therefore a per-item HOLD against superseded bytes
inside an attempt whose verdict as a whole was FAIL. It is not absent, and it is not a
post-D-062 independent verification.

**This stretch reproduced the class read-only** in a disposable clone of `8d8820c`
(git 2.50.1 Apple Git-155, `core.quotePath` unset / default true, `diff.renames` unset /
default true). Credential-shaped content was synthesised at run time; no such literal
was committed. The clone was deleted afterwards. No A1 test was committed, no A1
production file was touched, no A1 verdict was relabelled, nothing was repaired.

| Id | Original shape (adjudication / A2) | Measured at `8d8820c` | Standing verification of record |
|---|---|---|---|
| `C4` | `git diff --cached --name-only` quotes a non-ASCII path; `git show ":$f"` fails; `\|\| continue` skips; ASCII twin BLOCKED, accented twin absent, `secret guard: clean` over the unscanned key (ADJ4 at `a18e6e6`) | `--name-only` still quotes the non-ASCII twin. `-z` emits both unquoted. `--staged` **BLOCKED both** (two findings, exit 1). | Repair claimed at `f61ecca`. No independent post-D-062 verification of record. This stretch's probe is implementer-run, not a standing HOLD. |
| `C6a` | `check-findings-ledger.sh` `cd "$(git rev-parse …)"`; `cd ""` is a successful no-op. INFO, fail-CLOSED in every ADJ4 configuration | From an unrelated empty directory the live script still printed the real ledger totals and `all totals match D-057(1) as ruled`, exit 0 — because identity is now derived from `BASH_SOURCE` (D-060(2)), not from the caller's cwd. | Same as the class: repaired at `f61ecca`; D-060(2) ruled the identity fork. This stretch did not re-apply ADJ4's failing-`rev-parse` shim. |
| `C6b` | `check-suite-floors.sh` fail-OPEN: decoy tree, wrong floors, self-certifies them | `GIT_DIR` pointed at a decoy whose `scripts/test.sh` set every floor to 1. The live script printed Sentinel's floors (103/550/221/7/78/30) and `read from scripts/test.sh, which is the only copy`, exit 0. It did not print the decoy's 1s. | Same class standing. |
| `C6c` | `install-hooks.sh` fail-OPEN: reported success after writing `core.hooksPath` into a foreign repository | Invoked from a foreign repo: refused before writing, exit 2; foreign `hooksPath` none before and after. | Same class standing. |
| `C6d` | `test.sh:161` fail-CLOSED as measured; carries a decision fork later ruled at D-060(2) | From a decoy with `GIT_DIR` set, `scripts/test.sh` began Sentinel's own gate-immutability stage (extracted 171 bootstrap lines). A decoy marker file was **not** present in the output. The process was stopped after twelve seconds; a completing gate from a decoy was **not** observed. | Same class standing. Limit of this probe: identity/early-gate only. |
| `R1` | `--diff-filter=ACM` dropped staged `R` and `T`; destination unscanned; commit could land | (i) Small-file `git mv` + append scored **A+D**, not `R`; destination still BLOCKED. (ii) Large-file `git mv` + append scored **`R097`**. `--diff-filter=ACM` listed **nothing**; `--diff-filter=d` listed the destination; `--staged` **BLOCKED** the destination. (iii) Symlink→regular typechange scored **`T`**; `--staged` **BLOCKED** the destination. | Per-item HOLD in VERIFICATION-2.md item 5 against `f61ecca`. Attempt-two verdict FAIL. D-062 changed the file afterwards. This stretch agrees with "destination scanned and blocked" on current bytes; that agreement is not a standing verification of record. |

No disagreement with the independent reviewer's `R1` reproduction on the `R`/`T` records
that are the defect. The first small-file probe was the wrong shape (git did not score
`R`); the follow-up was the right shape and the destination was scanned.

---

## `V-6` — live fail-open of the hygiene scan, not of the commit gate

Carried by reference as D-062 `VERIFICATION.md` §10 residual `V-6`, which names it
pre-existing A2 residual `R-C`. Recorded, not reopened. Not repaired in this stretch.

**Reproduced in this stretch** on the same disposable clone of `8d8820c`:

- Default mode, untracked credential-shaped file, no injection: **BLOCKED**, exit 1.
- Default mode, `GIT_CONFIG_COUNT=1` and `GIT_CONFIG_KEY_0=core.excludesFile` pointing at
  an excludes file that names the untracked path: **`secret guard: clean`**, exit 0.
- **`--staged` under the same injection**, with that path staged: **BLOCKED**, exit 1.

The injection defeats the hygiene scan (`git ls-files --others --exclude-standard`). The
staged path — the commit-time guard the hook uses — still blocks. This is the boundary
to look at when ruling D-055. Naming it is not carding it, not repairing it, and not
accepting it.

---

## `V-1` through `V-10`

Carried by reference to
`docs/review-2026-08-19-d057-targeted/batch-cards/D062-containment-tests/VERIFICATION.md`
§10. **Not copied.**

`V-1` remains **carried and unaccepted**. This stretch added a behavioural regression
guard and bound it to both gate profiles (see A-098). A regression test is not
acceptance.

`V-6` is additionally named above because this stretch reproduced it with the
hygiene/staged boundary stated. That does not reopen it.

---

## `R2`, `R3`, `R5` — deferred and unresolved

Deferred by D-061(2). D-062 did not reach them. Still deferred, still unresolved. Not
carded, not repaired, not accepted.

- **`R2`:** `check-vendor-honesty.sh` `artifacts()` quotePath skip. Independent A1
  verifier reproduced it with output. This stretch reproduced it (see the Gate 5
  dossier). Same script as `V3-N2`. Never a `NEW-FINDINGS.tsv` row.
- **`R3`:** inert Case 4 scorer residual — `is_ident_refusal` matches a failed-`cd`
  "repository root" line. Weakness in a test, recorded by the A1 verifier.
- **`R5`:** `check-rename-gate.sh` exiting zero while printing `UNVERIFIED`. The
  rename gate's exit status is not evidence; read its output. It is the residual
  that guards the D-016 rename.

---

## Disposition or owner of every `NEW-FINDINGS.tsv` row

Authoritative file: `docs/review-2026-08-19-d057-targeted/NEW-FINDINGS.tsv`.
Adjudication: `adjudication/new-findings/ADJUDICATED-NEW-FINDINGS.md` plus ADJ3/ADJ4
for the contract-drafting cluster. No row below is listed as having neither a
disposition nor an owner.

| Id | Classification in the TSV | Owner / disposition |
|---|---|---|
| `V3-N2` | CONFIRMED | Batch A (A-P2). Gate 5 status fork is John's (D-059(1)). A-EXTRACT repaired the named extraction defect; the guard's evidentiary standing is the other dossier. `R2` in the same script is deferred, not this row. |
| `F7-R1` | CONFIRMED | Batch B (B-F1). Truthful NatSpec at A-091. |
| `N-TESTSH-FLOORS` | DUPLICATE of `R4-F4` | Absorbed into A-F1 / A-FLOORS. Not a separate item. |
| `N-SCOPE-CD` | CONFIRMED, distinct from `V3-N1` | Batch A (A-P1). Live `check-review-scope.sh` uses D-060(2) identity. |
| `N-EVAL-ACTION-TARGET` | CONFIRMED, cosmetic | Batch D (D-F4). D-CLAIMS surface `ts/test/evaluate.checks.test.ts`. |
| `N-DECODE-E4` | CONFIRMED IN PART | Batch D (D-F4). D-CLAIMS surface `ts/src/decode/index.ts`. Signer half true and deliberate (D-014). |
| `C1` | CONFIRMED, distinct | A-EXTRACT (`check-eval-codes.sh` unanchored membership). |
| `C2` | CONFIRMED, distinct | A-EXTRACT (`check-type-strings.sh` section extent). |
| `C3` | CONFIRMED, distinct | A-FLOORS (`check-suite-floors.sh` duplicate handling). |
| `C4` | CONFIRMED — repaired at `f61ecca` | Batch A1 attempt two. See the class table above. |
| `C5` | CONFIRMED (code claim true, detail claim false) | D-CLAIMS (`protocol.ts` NatSpec). A-077(2)'s present-tense "the detail now distinguishes them" is superseded by A-096, not rewritten. |
| `C6a` | CONFIRMED — repaired at `f61ecca` | Batch A1 attempt two. See the class table. |
| `C6b` | CONFIRMED — repaired at `f61ecca` | Batch A1 attempt two. See the class table. |
| `C6c` | CONFIRMED — repaired at `f61ecca` | Batch A1 attempt two. See the class table. |
| `C6d` | CONFIRMED — repaired at `f61ecca`; fork RULED at D-060(2) | Batch A1 attempt two; identity fork is John's (D-060(2)). See the class table. |
| `R1` | CONFIRMED — repaired at `f61ecca` | Batch A1 attempt two. Per-item HOLD against those bytes; attempt FAIL overall. See the class table. |

---

## T1 — a limit's basis must be verified, not just its wording

**Remaining accepted limits**, as derived in §11.0 and register §13.4, not re-counted by
hand here: `D-07`, `D-09`(a),(b), `E5`, `F-VAULT-4`, `F-VAULT-5`, `G-3`.
(`D-09`(c) was reopened and then FIXED at A-076; `D-09` therefore sits in both the
fixed and accepted sets.)

**What the register currently prints** (status column, not re-verified in this stretch):
each of those six carries "T1 basis VERIFIED 2026-08-18" or a dated equivalent
(`F-VAULT-4` additionally "now stronger than when accepted (D-054(b))"; `F-VAULT-5`
cites the vault docstring; `G-3` cites a measured class-credit statement).

**A-075** (2026-08-18) is the T1-retroactive pass: independently verify all then-ten
accepted-limit factual bases; `D-09(c)`'s basis was refuted (F006). **A-078** returned
three LIMIT-BASIS-CONFIRMED among its four independent verifiers.

**What is not established.** This stretch did not re-run those basis probes. Register
§13.4 is a maintained table this project has already caught stale. `G-3`'s credited-class
count is one side of a recorded divergence (see T4); treating the register's present-tense
figure as T1-complete for `G-3` would pick a side A-080(4) left open.

---

## T2 — severity is assigned by the independent reviewer/adjudicator

D-057(4) countersigned three downgrades (`R1-F2` HIGH→MEDIUM, `R1-F3` MEDIUM→LOW,
`R2-F1` HIGH→LOW) and stated the countersignature does not dispose of the underlying
finding. D-056(a) re-classified `D-10`(c) MEDIUM rather than leaving an undocumented
downgrade.

**What is not established.** Whether every later residual (`R2`, `R3`, `R5`, `V-6`,
the `f61ecca` class) has an independent severity that John has countersigned. They do
not, which is why they are named rather than slotted into condition 3.

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

**Left open.** This is the material Phase 2's out-of-tree D-058(10) pack must carry:
what the gate passes *on the ratchet* (baselined workspace findings, carried corpus
classes, anything else), in those terms. "Passes on ratcheted debt" is not "clean".

**The corpus-class coverage figure is DISPUTED — recorded rather than picked.**
A-077(2) `R3-F1` re-measured the same set under a stricter crediting rule than the
class-coverage guard's ratchet and got a lower count. A-077's residual (e) is still
open at A-080(4): the divergence is *recorded rather than reconciled* because
reconciling it is a scope decision. Documents on the ordinary reading path print
the higher figure in present tense. T4 exists for exactly this. Filling T4 from a
stale run, or picking a side here, is not authorised.

Phase 2 will regenerate the artifacts at the Phase 1 freeze. Until that pack exists,
T4 is not complete in this dossier.

---

## What this dossier is not

It is not an assessment of D-055. It is not a recommended verdict. It is not a
reopening of Batch A1, Gate 5, or any residual named above. `R2`, `R3`, `R5`, and
`V-6` stay named, not carded, not repaired, not accepted.
