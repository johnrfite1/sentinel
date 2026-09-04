# Archive index

A map of the Sentinel record for a reader who did not live through it. Written 2026-09-03 under
D-093(c). It links; it does not restate — nothing here is a claim about the mechanism that the
linked documents do not make themselves, and it carries no number that a script derives.

## 1. What the record is, and why it is kept

Sentinel's product is as much its record as its code: every ruling, finding, review arc and
correction was written down as it happened, because the property under evaluation is honesty —
a claim never stronger than its evidence — and the history is part of what is evaluated
(README, "Where the record lives"; D-093). The record grew by stacking, each session's status
written above the last with superseded passages struck rather than deleted, until the Quench's
cold reader named its cost as dense, repetitive governance history (MSG-041). This index is the
map: nothing was deleted to make it, `docs/decisions.md` did not change, and every passage moved
out of a live file is preserved verbatim under `docs/archive/`.

## 2. Start here — the current state, in five files, in order

1. `docs/session-state.md` — the live status. It declares itself authoritative over anything an
   agent or a reader remembers; its top block is the state as of 2026-09-03.
2. `README.md` — what the artifact is, what it establishes and does not, and the runnable path
   through `release/`.
3. `docs/decisions.md` — the canonical decision log, D-001…D-096, and it wins. For the rulings in
   force since the enforcement release read D-082, D-083 and D-088…D-096.
4. `HANDOFF.md` — the standing fence: the Verification partition (what is autonomy *none*) and
   the House rules.
5. `docs/publication-policy.state` — the machine-read publication state, judged by
   `scripts/check-rename-gate.sh`.

## 3. The eight stories

Decision ranges are by number; the log's physical order is not monotonic. A–E are complete arcs,
F is halted, G is closed by the Quench, H is open.

**A. Intake and the build gates — D-001…D-018 (2026-07-27/28).** Settled the §14 ladder, two
mid-build gates signed by John alone and non-delegably, the kill criteria, the four delegated
forks, signer refusal semantics and the naming block; Gate S1 signed 2026-07-28. Carried by
`docs/archive/handoff-history.md` (the 2026-07-27 brief), `docs/gate-s1-evidence.md`,
`Sentinel_Lab_Proposal_v0_2.md` §14.8–14.9.

**B. Specification clarifications, labelling, Gate 5 and Gate S2 — D-019…D-042 (2026-08-15/16).**
Settled the published type strings and enumerations, split §7.5 into S2 and pre-publication
conditions, measured the labelling contamination channel, certified Gate 5 and signed S2 on §11's
limits. Carried by `docs/gate-s2-evidence.md`, `docs/gate-5-vendor-audit.md`,
`docs/ablation-report.md`.

**C. The post-S2 review loop and its terminating condition — D-043…D-057 (2026-08-16→19).**
Settled the stopping rules, rounds five and six, the atomic-drain boundary, the exit criterion
D-055 and John's rulings on the bounded D-055(e) review's 23 findings. Carried by
`docs/repair-protocol.md`, `docs/review-2026-08-18-d055e/`, `docs/exit-criterion-packet.md`.

**D. The convergence reset, batch cards and Batch A1 — D-058…D-066 (2026-08-19→21).** Settled
test-first remediation by batch card in place of the repository-wide contract, A1 closed through
the one `GIT_INDEX_FILE` containment exception and not on the merits, and the withdrawal of
standing force authorisation. Carried by `docs/review-2026-08-19-d057-targeted/` (README,
`batch-cards/`, `VERDICT-LEDGER.tsv`), `docs/archive/session-state-history.md` (the 2026-08-20
and 2026-08-25 blocks).

**E. D-055 met, the name, and Gate 8 — D-067…D-080 (2026-08-23→25).** Settled D-055(a) MET and
unlocking nothing, the name "Sentinel" and its domain string, the Gate 8 packet assembled and
corrected, and Gate 8 PASSED with three limits against the v0.2 packet. Carried by
`docs/review-2026-08-19-d057-targeted/d055-condition-status.md` and `critical-high-census.md`,
`reviewer-packet/` (frozen), README "Historical" section.

**F. The enforcement release, its casting halted at the Anvil, and the publication posture —
D-081…D-084 (2026-08-29/30).** Settled the Cycle 2 enforcement checkpoint, the four A-018
Criticals sustained and that line HALTED, the deferred licence and state-aware publication guard,
and the fresh casting for the lab. Carried by `docs/a018-remediation-register.md`,
`docs/enforcement-release-v0.3.md`, `docs/publication-policy.state`.

**G. The lab casting: Cycles 1–3, the patch and the Quench — D-085…D-096 (2026-08-31→09-03).**
Settled the inventory-diff review method and D-047's retirement, the Cycle 2 and Cycle 3
candidates and their backup pushes, Cycle 3's zero sustained Criticals, the D-092 narrow patch
that became the Quench artifact `8dfaa27`, and the Quench itself — assumptions, acceptance
criteria, the decision note and the Temper trigger. Carried by the six `docs/cycle-*` files, the
four `docs/quench-orchestrator-handoff*.md`, `docs/crucible-session-debrief-2026-09-03.md`.

**H. Licence, venue, audience — the publication posture across arcs (cross-cutting).** Settled,
so far, that naming lifts while publication stays blocked, that clean results are preconditions
and never triggers, that the licence is deferred, that the audience is technical evaluators and
the venue GitHub public with visibility unchanged, that a backup push is not publication, and
what the Temper trigger is and is not. Carried by `docs/publication-policy.state`, README
"Status", `docs/session-state.md` (the current block).

## 4. Every `docs/` file and review directory, classified

LIVE — read for the current state or read by a script. FILED WITH THE CRUCIBLE — handed to the
Crucible session byte-for-byte; does not move or change. HISTORICAL — evidence or instrument of a
closed arc, kept because the history is part of what is evaluated.

| File | Class | One line |
|---|---|---|
| `a018-remediation-register.md` | LIVE | The A-018 remediation register for the halted enforcement line; authorises nothing; §3 closed with dated markers, §4 John's (story F, G) |
| `ablation-report.md` | LIVE (generated; guarded) | §7.3 ablation output; the gate diffs it against a regeneration and checks its §7.2 caveat (B) |
| `ARCHIVE-INDEX.md` | LIVE | This map |
| `check-inventory-diff-2026-08-31.md` | HISTORICAL | The D-085(e) inventory diff at `8146937` (G) |
| `crucible-session-debrief-2026-09-03.md` | FILED WITH THE CRUCIBLE | The Smith's session debrief, MSG-001…MSG-043 (G) |
| `cycle-2-orchestrator-brief.md` | FILED WITH THE CRUCIBLE | Cycle 2 instructions; candidate `cb124fe` (G) |
| `cycle-2-return-package.md` | FILED WITH THE CRUCIBLE | Cycle 2 return package for the council (G) |
| `cycle-3-orchestrator-brief.md` | FILED WITH THE CRUCIBLE | Cycle 3 instructions; candidate `81edee1` (G) |
| `cycle-3-patch-orchestrator-handoff.md` | FILED WITH THE CRUCIBLE | The D-092 patch handoff (G) |
| `cycle-3-patch-return-note.md` | FILED WITH THE CRUCIBLE | Maps Cycle 3's eighteen findings to the patch (G) |
| `cycle-3-return-note.md` | FILED WITH THE CRUCIBLE | Cycle 3 return note on `81edee1` (G) |
| `d055e-scope-manifest.md` | HISTORICAL | Scope of the D-055(e) review, fixed by D-056(d); pairs with `scripts/check-review-scope.sh` (C) |
| `decisions.md` | LIVE — the record itself | D-001…D-096 and the A-entries; canonical, and it wins; read by `check-rename-gate.sh` (all) |
| `enforcement-release-v0.3.md` | LIVE (normative; guarded) | v0.3 type strings and release rulings; source for `check-type-strings.sh` and `check-eval-codes.sh` (F) |
| `exit-criterion-packet.md` | HISTORICAL | The measured packet that preceded D-055; prepared, not decided (C) |
| `gate-5-vendor-audit.md` | HISTORICAL | The Gate 5 §2 audit John certified from at D-038 (B) |
| `gate-s1-evidence.md` | HISTORICAL (signed pack) | Gate S1, signed PASS 2026-07-28 (A) |
| `gate-s2-evidence.md` | HISTORICAL (signed pack; §11 load-bearing) | Gate S2, signed PASS 2026-08-16; §11 and §11.0 are the accepted limits S2 was signed on (B, C) |
| `publication-policy.state` | LIVE (machine-read) | The publication state; judged by `check-rename-gate.sh` (H) |
| `quench-orchestrator-handoff.md` | FILED WITH THE CRUCIBLE | D-093 handoff (G) |
| `quench-orchestrator-handoff-2.md` | FILED WITH THE CRUCIBLE | D-094 handoff (G) |
| `quench-orchestrator-handoff-3.md` | FILED WITH THE CRUCIBLE | D-095 handoff (G) |
| `quench-orchestrator-handoff-4.md` | FILED WITH THE CRUCIBLE | D-096 handoff; the Temper trigger (G) |
| `repair-protocol.md` | LIVE (binding method, D-052(b)) | Required for every repair (C, D) |
| `round-six-brief.md` | HISTORICAL | The round six brief (C) |
| `session-state.md` | LIVE (status) | The live status; read by `check-suite-floors.sh` (all) |
| `v1-1-register.md` | HISTORICAL register (deferred work) | The v1.1 register behind the re-label decision; §8 mutation survivors (B, C) |
| `archive/INVENTORY-2026-09-03.md` | HISTORICAL | The measured contract for this pruning pass: block maps, live facts, guard constraints, forks |
| `archive/session-state-history.md` | HISTORICAL | The dated blocks moved out of `session-state.md`, verbatim (§5 below) |
| `archive/handoff-history.md` | HISTORICAL | The 2026-07-27 brief and the dated blocks moved out of `HANDOFF.md`, verbatim (§5 below) |
| `review-2026-08-15/` | HISTORICAL evidence | Reproduction rigs (promoted into `mutate.sh`) and the superseded §7.5 draft (B) |
| `review-2026-08-16/` | HISTORICAL evidence | Attack probes for A-040 and A-043 (B) |
| `review-2026-08-17/` | HISTORICAL evidence | Round five, eight lens reports at `8234aba` (C) |
| `review-2026-08-18-d055e/` | HISTORICAL evidence (guarded) | D-055(e) at `7e0ab7f`; `FINDINGS-LEDGER.tsv` is read by `check-findings-ledger.sh` (C) |
| `review-2026-08-18-round-six/` | HISTORICAL evidence | Round six at `140c59e` (C) |
| `review-2026-08-19-d057-targeted/` | HISTORICAL evidence; carries the D-055 exit record | Batch cards, `VERDICT-LEDGER.tsv`, `d055-condition-status.md`, `critical-high-census.md` (D, E) |

Outside `docs/`: `reviewer-packet/` is the frozen Gate 8 artefact (D-091(c), D-092(b): no packet
byte moves); `release/` is generated and guarded by `check-release-sync.sh`.

## 5. Where the archived history of the two status files lives

- `docs/archive/session-state-history.md` — every dated block moved out of `docs/session-state.md`
  on 2026-09-03: the struck Last-updated lines, the "READ THIS BEFORE ANYTHING ELSE" blockquote's
  dated instructions and Crucible blocks, the reading order, the 2026-08-19 and 2026-08-29 status
  tables, the Batch A1 record, the open/waiting/not-authorised lists, the §3 staleness chronicle,
  the §4 index table, the 2026-08-16 mutation counts and the 2026-08-19 §7.1 table.
- `docs/archive/handoff-history.md` — every dated block moved out of `HANDOFF.md` (2026-08-16
  through 2026-09-02) and, oldest, the 2026-07-27 build brief whole.

Both are organised the same way: by date, newest first (ties in original line order), each block
under a heading giving its date and its original line range at `e73789d`, each block's own date
line and text verbatim, struck passages still struck, and a bracketed note wherever a block was
cut from surrounding text. One block did not move: the 2026-08-16/17 A-046…A-051 block stays at
the tail of `docs/session-state.md` because `scripts/check-vendor-honesty.sh` exempts that file by
name and would scan a new one. The inventory that governed the pass, with the live facts a
reviewer checks, is `docs/archive/INVENTORY-2026-09-03.md`.

## Appendix — README passages replaced on 2026-09-03, verbatim

The README has no archive file of its own; the two passages this pass replaced are kept here.
Lines 27–29 at `e73789d`:

Status at this revision (2026-09-02): a pre-publication candidate under external adversarial
review, held private, publication not authorised, licence deferred. `docs/session-state.md` is
the live status and wins over anything written here.

Lines 185–187 at `e73789d`:

(D-082(c)) and no agent may select one. The Crucible review record is in `docs/cycle-2-orchestrator-brief.md`, `docs/cycle-2-return-package.md`,
`docs/cycle-3-orchestrator-brief.md`, `docs/cycle-3-return-note.md` and `docs/cycle-3-patch-return-note.md`;
the rulings that followed are D-088 through D-092 in `docs/decisions.md`.
