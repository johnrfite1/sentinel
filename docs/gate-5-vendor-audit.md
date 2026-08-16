# Gate 5 (vendor honesty) — the §2 capability-table audit

Prepared 2026-08-15 for John's certification. **Nothing here is certified.** The verification
partition in `HANDOFF.md` gives public claims — "matrix, README, resume language" — autonomy
**none**: John certifies them. An agent may lay the rows out, say what is missing, and
mechanise what D-008 called mechanical. It may not decide whether a sentence fairly describes
somebody else's product.

`scripts/check-vendor-honesty.sh` enforces the mechanical half on every gate run and prints
the two certification-pending conditions so they cannot be forgotten. It reports them as
**UNCERTIFIED**, never as a pass.

---

## What D-008 requires, and where each part stands

| # | Condition | Status | Who can clear it |
|---|---|---|---|
| 1 | Every cell documentation-only, **dated**, and **linked** to its cited source | **UNCERTIFIED** — 0 of 9 rows carry a per-cell source or access date | John |
| 2 | The "executed" and "faithfully emulated" columns of §10.1 are empty in v1 | **ENFORCED** — no artifact claims either label; the §10.1 definition site must still exist, so the check cannot pass by the scheme being deleted | mechanical |
| 3 | Cells that are inference rather than quoted documentation are marked as inference | **UNCERTIFIED** — no cell is marked either way | John |
| 4 | No claim **or layout** implying empirical superiority over a named vendor in any v1 artifact | **ENFORCED** — no named vendor appears in any measurement artifact | mechanical |
| — | §7.2's own caveat travels with the numbers | **ENFORCED** — extracted from §7.2 and required in the ablation report, whitespace-normalised | mechanical |

**Why (4) is enforced as "no named vendor in a measurement artifact" rather than as a phrase
scan.** D-008 forbids a *layout* that implies superiority, and layout has no vocabulary to
grep for: a vendor's name in the same table as Sentinel's false-allow count implies the
comparison whatever the surrounding prose says. §7.2's baseline is called "representative"
for exactly this reason — no row of the ablation is about a real product. A phrase list would
also be a denylist, and the project's most repeated defect is a denylist whose coverage is
the spellings it happens to declare (A-028 F-3).

**The deliberation records are excluded and the exclusion is listed in the script**: the
proposal, `decisions.md`, `session-state.md`, `HANDOFF.md`, and the preserved review scratch
must be free to name vendors, or the project could not record why D-001 cut executed
comparisons.

---

## The nine rows, as they stand today

Every "Existing capability" sentence below is quoted verbatim from §2 of the proposal. **None
of them currently carries a citation or a date.** §13 lists sources 5–15 covering these
vendors, but no cell references one, and nothing anywhere records when a page was read — so a
reader cannot tell whether a sentence describes the product as documented in July 2026 or as
remembered.

The right-hand column is what certification needs, not a finding about the vendor.

| # | Named party | Capability sentence (verbatim, §2) | Candidate source | What John is certifying |
|---|---|---|---|---|
| 1 | Cobo Agentic Wallet | "Owner-approved task pacts, scoped and revocable credentials, parameter matching, completion conditions, rolling limits, and allow/review/deny enforcement" | §13 #5 (Pact Mechanism), #6 (Policy Engine) | Six named features, each traceable to a documentation page, and the read date |
| 2 | Coinbase Policy Engine; Privy | "Rules over value, network, destination, contract, signer, and decoded calldata" | §13 #7, #9 | That one sentence fairly covers **two** products; if it does not, the row needs splitting |
| 3 | Circle Agent Wallets | "Spend limits, address controls, compliance screening, and agent-native execution" | §13 #8 | "agent-native execution" is a marketing-shaped phrase — quoted or inferred? |
| 4 | Sigil | "ERC-4337 wallet, Guardian co-signing, deterministic rules, simulation, AI risk scoring, policies, and recovery" | §13 #12 | Seven features from a single landing page; the most citation-thin row in the table |
| 5 | Safe | "Guards, allowances, multisignature approval, recovery, and agent spending patterns" | §13 #10 | "agent spending patterns" — documented feature, or characterisation? |
| 6 | MetaMask Agent Wallet | "Protocol policies, simulation, threat scanning, MEV protection, and human escalation" | §13 #11 | A news/announcement page is the cited source; announcements describe intent as well as shipped capability |
| 7 | Hypernative Transaction Guard | "Pre-sign simulation, custom policy, intent verification, approval workflows, and audit records" | §13 #13 | "intent verification" is the closest published language to Sentinel's own claim; the fairness of the wording matters most here |
| 8 | Tenderly; Blockaid | "Decoded effects, execution simulation, and known-threat detection" | §13 #14, #15 | Again two products in one row |
| 9 | ERC-7730 | "Chain/address-bound clear-signing metadata for calldata and typed messages" | §13 #16 | A standard rather than a vendor; arguably outside the vendor-honesty gate entirely |

### The fourth column is a separate certification

"Consequence for Sentinel" holds Sentinel's **own judgements**, not vendor facts — "Generic
policy-as-code is a substitute", "Close overlap with the original stack", "Direct substitute
for an inline transaction guard". D-008 says *every cell* of the matrix, so these are in
scope, and by construction every one of them is **inference**: no vendor documents what its
product implies for Sentinel. If (3) is satisfied by marking, this column is where the marks
mostly go.

Two of these read as the strongest statements in the table and are worth reading twice at the
gate, because they are the ones a hostile reader would quote back:

- Sigil — "Close overlap with the original stack"
- Hypernative — "Direct substitute for an inline transaction guard"

Neither claims superiority *for* Sentinel; both concede overlap, which is the honest
direction. That is worth noting explicitly, because a gate that only looks for overstatement
of one's own product would pass this table without reading it.

---

## The marker the check counts

If the rows are certified, the marker `[§13#N read YYYY-MM-DD]` appended to each capability
cell makes condition (1) mechanical from then on — the script counts rows carrying it and
reports the shortfall. Certification is not an edit an agent makes; the marker records a
decision John took.

Condition (3) has no such marker proposed, because "this clause is inference" is a reading of
a sentence against a source, not a pattern. If John wants it mechanised, the cheapest honest
form is a required `(inference)` suffix on any clause not quoted from the cited page — and
that too is a decision, not an implementation detail.

---

## Explicitly not done

- **No vendor documentation was fetched or re-read in preparing this.** Every observation
  above is about the proposal's own text and citation structure — what is missing, what is
  ambiguous, which rows carry the most weight — and none of it asserts anything about what a
  vendor's product does or does not do. Verifying the sentences against live documentation is
  work that produces a public claim, so it belongs to the certification session rather than
  ahead of it.
- **Nothing in §2 was edited.** The table stands exactly as John wrote it.
