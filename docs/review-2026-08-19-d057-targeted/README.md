# D-055(e) → D-060: review, reverification, and a failed remediation method

## THERE IS NO ACTIVE GLOBAL REPAIR CONTRACT

**D-060(1) abandoned it.** Two repository-wide prose contracts were written, each attempting to
enumerate every defect class at once. **Both were independently audited and both FAILED.** They
are preserved under `contract/` as **FAILED / SUPERSEDED process evidence** and **nothing in them
is operative.**

**Why the method failed, in one sentence** — the second auditor's diagnosis, which is the reason
the approach was replaced rather than iterated:

> the contract's enumerations were each run with a command shaped like the site somebody already
> reported, and every one of them therefore stops where that report stopped.

A repository-wide contract implicitly claims completeness across the whole repository. **That
claim could not be made true, and each attempt to make it true produced a new false completeness
claim** — which is the exact defect class this whole cycle exists to close.

## What replaces it

**Small, independently test-authored BATCH CARDS.** Each card carries only:

- **one invariant**
- **an explicit file/symbol boundary**
- **a test matrix**
- **controls**
- **exclusions**

**Completeness is assessed INSIDE the declared boundary** — never by claiming every possible
repository sibling has been found. Entry points are enumerated **by file, shebang and ownership**,
never by searching for one known coding idiom.

## What is in here

| Path | What it is |
|---|---|
| `briefs/` | reviewer and adjudicator briefs as issued |
| `reviewers/v1…v5/` | the five targeted-reverification deliverables, **unaltered** |
| `adjudication/` | the targeted-review adjudication and the six-item new-findings table |
| `adjudication/round2/` | adjudication of candidates surfaced during contract drafting |
| `contract/FAILED-*` | **both failed contracts and both audits — evidence only** |
| `offered/` | a signed-text correction prepared for John; **ratified at D-060(4)** |
| `VERDICT-LEDGER.tsv`, `NEW-FINDINGS.tsv` | one row per item; counts are DERIVED from these |
| `SANITIZATION-MANIFEST.md` | the one disclosed alteration to evidence, with raw hashes |

## What the failed contracts still contribute

**Their findings remain factually valid about the tree** and are carried into the batch cards:
the root-resolution class, the secrets-guard skip points, the section-extraction consumers, the
floor duplications. **What is abandoned is the claim to have found them all at once.**

## The standing rule this directory exists to serve

**A green result is evidence only for what it actually exercised.** Every count here is derived
from a `.tsv`, not typed by hand — because a published number that was true once is one of this
project's recorded defect classes.
