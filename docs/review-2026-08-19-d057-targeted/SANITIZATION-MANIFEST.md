# Sanitization manifest — D-060(3)

**Authorized by John, D-060(3):** *minimal, disclosed sanitization of adjudicator-authored
evidence solely to prevent literal quotations of guarded labels from being interpreted as live
product labels.*

## What was altered

**One file. One substitution. Nothing else in this directory was touched.**

| File | Raw SHA-256 | Tracked SHA-256 |
|---|---|---|
| `adjudication/new-findings/ADJ1.md` | `3397d943403b68aaa8ddcfc0c71843fdd83378fa51f2da90dd12f229a8370924` | `5abc3bfc21503ee71c5588d42c2bd76833270ec45bd0b85dc48700bd187656a1` |

**What changed:** at `ADJ1.md:219`, a sentence describing `check-vendor-honesty.sh`'s own scan
quoted the two §10.1 vendor-comparison label strings verbatim, in backticks. The literal strings
were replaced with a reference to their authoritative source. **The replacement is disclosed
inline in the file itself**, so a reader encounters the change where the change is.

**What did NOT change:** no finding, mechanism, severity, classification, argument, verdict,
probe, control, command or coverage statement. The substitution is confined to one clause of one
descriptive sentence.

## Why it was necessary

`scripts/check-vendor-honesty.sh:203` scans **untracked** files as well as tracked ones — by
design, because *"an untracked file in this repository is one `git add -A` from being published"*.
Its own header records `docs/gate-s2-evidence.md` tripping this same way, which is why untracked
scanning was added.

**The guard was correct and the evidence file was correct.** A document that quotes a policed
label while describing the policing is indistinguishable, to a literal scan, from one that applies
the label. **The guard was not weakened, no ignore rule was added, and its scope is unchanged.**

## Raw originals are preserved

The complete evidence directory was archived **byte-for-byte outside this repository** before any
alteration, with an archive hash and a 37-entry per-file manifest.

- archive SHA-256: `b5648c1cb554f67a66d6ccfa0824d550a3184795059124c1e44011f28303b635`
- per-file manifest SHA-256: `a93fb3d82fec922685662c59ead114dcfb8f362b8c31cb1862167f264d574a8f`

**The archive's location is deliberately not recorded in any tracked file** (D-060(3): no
machine-specific paths). John holds it.

## Standing rule

If the guard later identifies another **quotation**, the same disclosed treatment applies and this
manifest gains a row. **If it identifies a LIVE CLAIM rather than quoted evidence, that is a stop
condition and is reported, not sanitized.**
