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

---

# Source-verification pass — 2026-08-15 — **PROPOSED, NOT CERTIFIED**

Every cited source was fetched and read on **2026-08-15**. Below is what each page does and
does not state, so the certification session is a review rather than research.

**This section certifies nothing.** It reports what a source says. Whether a sentence in §2
fairly describes somebody else's product is John's call under the verification partition, and
no part of this changes that. Where a claim is not on its cited page, the honest options are:
add the source that does support it, mark the clause as inference under D-008(3), or reword
it — and which of those is right is a judgement, not a lookup.

## Rows that HOLD against their cited sources

| # | Party | Finding |
|---|---|---|
| 1 | Cobo | **All six claims documented — but only across BOTH cited sources.** "Owner-approved task pacts", "scoped and revocable credentials", "completion conditions" and allow/review/deny are on §13 #5; "parameter matching" ("conditions like chain, token, destination address, contract address, or operation value") and "rolling limits" ("rolling window spending counters… 1 hour, 24 hours, 7 days, 30 days") are on §13 #6. The cell needs both citations, which is D-008(1) doing its job. |
| 4 | Sigil | **Six of seven verbatim** — ERC-4337, Guardian co-signing ("The Guardian co-signer can only approve transactions"), deterministic rules, simulation, AI risk scoring, policies. "Recovery" appears as "Social Recovery… N-of-M trusted guardians recover your Sigil Wallet". I had flagged this as the most citation-thin row; it is not. |
| 6 | MetaMask | **All five documented, and the page describes SHIPPED capability**, not intent — "officially launches today", "Start using… now". My earlier concern that an announcement page conflates plan with product does not apply. |
| 8 | Blockaid half | All three documented — "Reveal the full onchain impact of a transaction—before it's signed", "Simulate and validate every transaction in real time", "Flag complex attack scenarios". |
| 9 | ERC-7730 | Binding is explicit and **mandatory** for both calldata and typed messages: wallets "MUST verify that the target chain and contract address… match one of these deployment options", and for EIP-712 that the message carries "both `domain.chainId` and `domain.verifyingContract`". |

## Rows where the cited source does NOT support the claim as written

**Row 2 — Coinbase Policy Engine; Privy — "Rules over value, network, destination, contract,
signer, and decoded calldata".** One sentence, two products, and it does not hold jointly.

- **Privy's** cited page documents five of the six: decoded calldata explicitly
  (`'ethereum_calldata'` with "both the function name and, if applicable, function arguments",
  addressable as `function_name.param_name`), value, network ("Allowlists and denylists of
  networks"), destination, and contract ("Allowlists and denylists of smart contracts").
- **Coinbase's** cited page documents **two**: value (`ethValue`) and destination
  (`evmAddress`). Network, contract, signer and decoded calldata are not given as criteria —
  the page's prose mentions "destination address, value, and network" but supplies concrete
  criteria only for the first two.
- **"signer" is documented for neither.**

This is the row I flagged before reading anything as "one sentence covering two products; if
it does not hold, the row needs splitting". It does not hold.

**Row 5 — Safe — "Guards, allowances, multisignature approval, recovery, and agent spending
patterns", cited to Smart Account Guards.** The cited page documents **Guards only**: "checks
before and after a Safe transaction", able to "programmatically check all the parameters of the
respective transaction before execution". Allowances, multisignature approval, recovery and
anything describable as "agent spending patterns" are **not on that page**. Safe plainly has
allowances and multisig — but D-008(1) is about the cell being *linked to its cited source*,
and four of five claims are not.

**Row 7 — Hypernative — "…intent verification…".** The phrase **does not appear on the cited
page**, nor does anything meaning it. The other four claims are documented verbatim
("Pre-transaction simulation shows your team exactly what every transaction will do onchain,
in plain English, before anyone signs"; policy-driven approval; approval workflows;
"Exportable audit trails").

**This is the single most important cell in the table**, and I said so in the audit above
before fetching anything — "intent verification" is the closest published language to
Sentinel's own claim, and Sentinel attributing it to a competitor from a source that does not
say it is the exact shape of error D-008 exists to prevent.

**Row 3 — Circle — "…agent-native execution".** Spend limits, address controls and compliance
screening are documented verbatim ("All transfers are screened against sanctions controls
before submission onchain"). **"Agent-native execution" is a characterisation, not documented
language** — the page says an "AI agent hold funds and transact onchain autonomously". Under
D-008(3) that clause is inference and would be marked as such.

**Row 8 — Tenderly half — "known-threat detection".** Not documented on the cited page. Decoded
effects and execution simulation are. The cited URL is also a marketing landing page with
"substantive product details… sparse" — the technical documentation is behind `docs.tenderly.co`,
so this citation may want to point somewhere else regardless.

## The direction of the errors, which is worth noticing

**Every discrepancy found overstates a competitor's documented capability, not Sentinel's.**
The table claims more for Cobo, Safe, Hypernative, Circle, Coinbase and Tenderly than their
cited pages support. That is the honest direction to err — it makes Sentinel's market look
more crowded than the sources establish, not less — and it is consistent with the audit's
earlier observation that the two strongest cells *concede overlap*. It is still an accuracy
problem under D-008(1) and (3), and it is still John's to resolve.

## What certification would need, per row

Rows 1, 4, 6, 8-Blockaid and 9: a citation marker and today's date. Rows 2, 5, 7, 3 and
8-Tenderly: a decision first — additional source, `(inference)` marking, or rewording — and
then the marker.

## Explicitly not done

- **The section above this line was written BEFORE any vendor documentation was fetched**, and
  is preserved unchanged. It is about the proposal's own text and citation structure. The
  source-verification pass that follows it was added later, on John's direction, and reports
  what the cited pages say. Neither section certifies anything: reporting that a page does not
  contain a phrase is a fact about the page, and deciding what to do about it is the
  certification.
- **Nothing in §2 was edited.** The table stands exactly as John wrote it.
