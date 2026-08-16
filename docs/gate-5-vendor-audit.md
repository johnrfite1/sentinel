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

---

---

# Certification packet — the exact diff — **PREPARED 2026-08-15, NOT APPLIED**

This is step 3 of the session-state ordering: *prepare Gate 5's certification for John; do not
perform it.* Below is every proposed change as literal replacement text, so the certification
session is a sequence of rulings rather than drafting. **Nothing here is applied. §2 still
stands exactly as John wrote it.**

**Why this is appended to the audit rather than filed as its own document.** A new
`docs/gate-5-certification-packet.md` naming nine vendors would fail `check-vendor-honesty.sh`
on D-008(4) the moment it existed — the script scans untracked-but-not-ignored files, and only
this file is on its exclusion list. The alternative was to add the new file to that list, and
the script says in terms that adding a file to the exclusion list is a claim about that file.
Appending here makes no such claim.

## What changed since the source-verification pass above

Three lookups were run today to close forks that pass had left open. **Locating a candidate
source is a lookup; deciding whether a sentence fairly describes a competitor is John's.** The
partition is unchanged.

1. **Row 5 (Safe) is recoverable, and the pass above understated it.** Its four unsupported
   claims are all documented — on Safe pages that §13 does not yet cite. See Row 5 below.
2. **Row 8 (Tenderly) is confirmed unsupported, on a second page as well.** The alert-type
   documentation describes only user-configured conditions; there is no known-threat detection
   to cite. See Row 8.
3. **Row 7 (Hypernative) did NOT resolve, and the honest report is that my instrument was
   unreliable.** Detail under Row 7 — read that one before ruling.

**A counting correction to `docs/session-state.md`.** It says "Five rows hold. Four do not."
That is wrong, and it is wrong in the flattering direction. Row 8 is two products in one
sentence: the Blockaid half holds and the **Tenderly half does not**, which the pass above
records but the summary line collapsed. Of the nine numbered rows, **four hold as written (1,
4, 6, 9), one holds by half (8), and four do not (2, 3, 5, 7)** — five rows need a ruling, not
four. Session-state is corrected.

## The two policy questions, which decide the shape of everything below

**Q1 — the citation marker.** `check-vendor-honesty.sh` counts
`[§13#N read YYYY-MM-DD]`. A row needing two sources carries two markers. Confirm the format
and that **2026-08-15** is the access date of record (it is the date every page was fetched).

**Q2 — how inference gets marked (D-008(3)).** Two forms, and the choice is real:

| | Form | Cost | What it says |
|---|---|---|---|
| **A (recommended)** | One declaration above the table that the whole **"Consequence for Sentinel"** column is Sentinel's inference, plus a `(inference)` suffix on individual **capability** clauses not quoted from the cited page | 1 sentence + 1 suffix today | Accurate: the fourth column is inference *by construction* — no vendor documents what its product implies for Sentinel |
| B | `(inference)` on every cell of the fourth column | 11 suffixes | Same content, repeated eleven times; the repetition reads as hedging rather than precision |

Under A, exactly one capability clause is marked today: Circle's "agent-native execution".

**Proposed declaration sentence, to sit immediately below the table:**

> Every entry in "Existing capability" is quoted or closely paraphrased from the cited source
> as read on the marked date; clauses marked `(inference)` are not. **The "Consequence for
> Sentinel" column is Sentinel's own inference throughout** — no vendor documents what its
> product implies for this project.

## Row-by-row

### Rows that hold — ruling is "add the marker"

| # | Party | Marker to append to the capability cell | Note |
|---|---|---|---|
| 1 | Cobo | `[§13#5 read 2026-08-15] [§13#6 read 2026-08-15]` | **Two markers required.** Four claims are on #5, "parameter matching" and "rolling limits" only on #6. One citation would leave two clauses unsupported |
| 4 | Sigil | `[§13#12 read 2026-08-15]` | Seven of seven documented. The pass above retracted its own "most citation-thin row" flag |
| 6 | MetaMask | `[§13#11 read 2026-08-15]` | Announcement page, but it describes shipped capability ("officially launches today") |
| 9 | ERC-7730 | `[§13#16 read 2026-08-15]` | Binding is explicit and mandatory in the standard. A standard is not a vendor; if John reads the vendor-honesty gate as not reaching it, the marker is still harmless |

### Row 2 — Coinbase; Privy — **split**

One sentence covers two products and holds for neither jointly. Privy documents five of the
six criteria; Coinbase documents two; **"signer" is documented for neither.**

*Current:*

```
| Wallet policy infrastructure | Coinbase Policy Engine; Privy | Rules over value, network, destination, contract, signer, and decoded calldata | Generic policy-as-code is a substitute |
```

*Proposed (recommended — split, and drop "signer" from both):*

```
| Wallet policy infrastructure | Privy | Rules over value, network, destination, contract, and decoded calldata [§13#9 read 2026-08-15] | Generic policy-as-code is a substitute |
| Wallet policy infrastructure | Coinbase Policy Engine | Rules over value and destination [§13#7 read 2026-08-15] | Generic policy-as-code is a substitute |
```

*Alternative:* keep one row narrowed to the intersection ("Rules over value and destination").
Cheaper, but it understates Privy — which is the direction that flatters Sentinel, and this
table's whole purpose is to not do that.

### Row 3 — Circle — **mark one clause**

*Current:*

```
| Agent payment wallets | Circle Agent Wallets | Spend limits, address controls, compliance screening, and agent-native execution | Spend governance is increasingly bundled |
```

*Proposed:*

```
| Agent payment wallets | Circle Agent Wallets | Spend limits, address controls, compliance screening, and agent-native execution (inference) [§13#8 read 2026-08-15] | Spend governance is increasingly bundled |
```

Three clauses are verbatim. The page says an "AI agent hold funds and transact onchain
autonomously"; "agent-native execution" is Sentinel's compression of that, so it is inference,
not misquotation.

### Row 5 — Safe — **re-cite; the claims are real, the citation was wrong**

The pass above found four of five claims absent from the cited Guards page and proposed
narrowing the row to Guards. **That proposal is withdrawn.** Both missing pieces are documented
on Safe pages §13 does not yet list, verified today:

- **"How do Safe Smart Accounts work?"** — multisignature: *"Safe's multi-signature
  functionality allows you to define a list of owner accounts and a threshold number of
  accounts required to confirm a transaction."* Allowances: *"allowance modules that allow
  owners of a Safe to grant limited execution permission, such as a daily limit to external
  accounts."* Recovery: *"defining a module that can only be used to recover access to a Safe
  under specific circumstances is possible."*
- **"AI agent with a spending limit for a treasury"** — a documentation page whose subject is
  exactly the clause I could not source: *"you can set an allowance per token for a spender…
  It can be a one-time allowance, or an allowance that resets after a certain time interval."*

*Current:*

```
| Smart-account controls | Safe | Guards, allowances, multisignature approval, recovery, and agent spending patterns | Do not invent production custody |
```

*Proposed:*

```
| Smart-account controls | Safe | Guards, allowance modules, multisignature approval, recovery modules, and agent spending patterns [§13#10 read 2026-08-15] [§13#25 read 2026-08-15] [§13#26 read 2026-08-15] | Do not invent production custody |
```

**One wording judgement is flagged rather than taken.** The source documents recovery and
allowances as *things a module can be built to do*, not as shipped named features — hence
"allowance modules" and "recovery modules" above. If John reads Safe's spending-limit
documentation as making allowances a shipped feature, the bare words are defensible. **Narrowing
the row to Guards would have made a competitor look weaker on a citation error of ours** — worth
recording, because that was the cheap option and it was available.

### Row 7 — Hypernative — **unresolved; read the method note before ruling**

"Intent verification" appears nowhere on the cited page (§13 #13). The other four clauses are
verbatim. This is the cell the audit above singled out before any page was fetched, because
"intent verification" is the closest published language to Sentinel's own claim.

**I attempted the same re-cite lookup that rescued Row 5, and it did not produce evidence I am
willing to put behind a citation.** A fetch of Hypernative's security-solutions page returned a
sentence containing *"ensuring every signed transaction matches authorized intent"* — but the
same fetch also stated that the word "intent" does not appear on the page, and separately that
the sentence came from navigation rather than body content. **Those statements cannot all be
true.** A self-contradicting read is not a source, and treating the fragment I liked as the
reliable half is precisely the defect class this project keeps finding. So Row 7 goes to John
with the lookup **attempted and failed**, not with a citation.

Three options, no recommendation between the first two:

| | Ruling | Effect |
|---|---|---|
| a | Strike "intent verification" | Removes an unsourced claim. Makes a competitor look less like Sentinel — the direction that flatters us, so it deserves the harder look |
| b | Mark `(inference)` | Keeps the concession that a competitor may already do Sentinel's differentiating thing, and says the inference is ours |
| c | Re-cite, after a **verified** read of a Hypernative page that carries the language | Correct if the language exists; **blocked on a clean fetch, which I did not get** |

If John wants (c), the check is one page-read confirming the sentence in body content, and it
should be done by someone who can see the rendered page — my tooling gave an unreliable answer
once already.

### Row 8 — Tenderly; Blockaid — **split; the Tenderly clause is unsupported on two pages**

Blockaid documents all three claims. Tenderly documents decoded effects and execution
simulation but **not known-threat detection** — confirmed today against the alert-type
documentation as well as the cited landing page: the alert types are user-configured conditions
(a "Blocklisted Callers" alert requires the user to supply the addresses), with no automatic
detection of known threats or attack patterns.

*Current:*

```
| Simulation and threat APIs | Tenderly; Blockaid | Decoded effects, execution simulation, and known-threat detection | Integrate or compare against these primitives |
```

*Proposed:*

```
| Simulation and threat APIs | Blockaid | Decoded effects, execution simulation, and known-threat detection [§13#14 read 2026-08-15] | Integrate or compare against these primitives |
| Simulation APIs | Tenderly | Decoded effects and execution simulation [§13#15 read 2026-08-15] | Integrate or compare against these primitives |
```

The category label changes for the Tenderly row because "threat APIs" would carry the struck
claim in the layout after the words were removed — D-008(4) is about layout as well as text.
The cited Tenderly source stays #15 (it does document the two surviving clauses) even though
the pass above noted it is a thin marketing page; **re-citing to `docs.tenderly.co` is a
separate improvement and would need its own verified read, which has not been done.**

## New §13 entries this requires

Two, and they are **appended as 25 and 26 rather than inserted into the wallet-alternatives
block (5–15)**. Inserting would renumber 16–24 and silently invalidate every `§13 #N` reference
already written in this audit — a renumbering that breaks existing citations is a worse
citation defect than the one being fixed.

```
Additional vendor sources (added at Gate 5 certification, 2026-08-15):

25. [Safe — How do Safe Smart Accounts work?](https://docs.safe.global/advanced/smart-account-overview)
26. [Safe — AI agent with a spending limit for a treasury](https://docs.safe.global/home/ai-agent-quickstarts/agent-with-spending-limit)
```

## The table as it would read, under the recommended rulings

Row 7 is left **exactly as it stands today**, because it is unresolved — so this block is not
yet appliable in full, by design.

```
| Category | Examples | Existing capability | Consequence for Sentinel |
|---|---|---|---|
| Pact-first agent authorization | Cobo Agentic Wallet | Owner-approved task pacts, scoped and revocable credentials, parameter matching, completion conditions, rolling limits, and allow/review/deny enforcement [§13#5 read 2026-08-15] [§13#6 read 2026-08-15] | Intent-aware authorization is not an empty category |
| Wallet policy infrastructure | Privy | Rules over value, network, destination, contract, and decoded calldata [§13#9 read 2026-08-15] | Generic policy-as-code is a substitute |
| Wallet policy infrastructure | Coinbase Policy Engine | Rules over value and destination [§13#7 read 2026-08-15] | Generic policy-as-code is a substitute |
| Agent payment wallets | Circle Agent Wallets | Spend limits, address controls, compliance screening, and agent-native execution (inference) [§13#8 read 2026-08-15] | Spend governance is increasingly bundled |
| Direct agent-wallet security | Sigil | ERC-4337 wallet, Guardian co-signing, deterministic rules, simulation, AI risk scoring, policies, and recovery [§13#12 read 2026-08-15] | Close overlap with the original stack |
| Smart-account controls | Safe | Guards, allowance modules, multisignature approval, recovery modules, and agent spending patterns [§13#10 read 2026-08-15] [§13#25 read 2026-08-15] [§13#26 read 2026-08-15] | Do not invent production custody |
| Wallet-native controls | MetaMask Agent Wallet | Protocol policies, simulation, threat scanning, MEV protection, and human escalation [§13#11 read 2026-08-15] | Policy plus simulation is moving into wallet UX |
| Institutional transaction guard | Hypernative Transaction Guard | Pre-sign simulation, custom policy, intent verification, approval workflows, and audit records | Direct substitute for an inline transaction guard |
| Simulation and threat APIs | Blockaid | Decoded effects, execution simulation, and known-threat detection [§13#14 read 2026-08-15] | Integrate or compare against these primitives |
| Simulation APIs | Tenderly | Decoded effects and execution simulation [§13#15 read 2026-08-15] | Integrate or compare against these primitives |
| Signing metadata | ERC-7730 | Chain/address-bound clear-signing metadata for calldata and typed messages [§13#16 read 2026-08-15] | Consume the standard; do not invent a parallel manifest without evidence of a gap |
```

**After application the guard would read `10 of 11` rows cited, not `11 of 11`** — Row 7 is the
uncited one, and the shortfall is the gate correctly refusing to go green on an open question.
Gate 5 is **NOT MET** until Row 7 is ruled.

## A defect in the guard that counts these markers

`check-vendor-honesty.sh` tells the reader the marker is *"appended to the capability cell"*,
but its awk tests `$0` — **the whole row line**. A marker in any cell, including "Consequence
for Sentinel", would be counted. Nothing exploits this today (0 of 9 rows carry a marker, and
the markers will be written to John's ruling), but it is the project's most-repeated defect
shape: an instrument that exists and points at something other than what it says it does.

**Not fixed yet, deliberately** — the tightened awk must match the cell layout John actually
rules for, and the row split changes that layout. Sequencing: rule, apply, then tighten the
guard and re-run. Recorded here so it is not lost between the two.
