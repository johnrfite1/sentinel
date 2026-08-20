# OFFERED CORRECTION — signed Gate S2 text. **NOT APPLIED. AWAITING JOHN'S RATIFICATION.**

**Status: OFFERED / NOT CERTIFIED.** Nothing in this file has been written into
`docs/gate-s2-evidence.md`. Per D-059(1b): *"Do not silently edit signed text. Prepare the exact
proposed correction and its provenance for my ratification before applying it."*

**This correction is NOT part of Batch A, B, C or D**, and applying it is not an agent's act.

## Provenance — and it differs from §11.0's in the way that matters

| Question | §11.0 (corrected at A-080) | **This sentence** |
|---|---|---|
| Present at the D-041 signing commit `9488f27`? | **NO** — zero occurrences | **YES — one occurrence** |
| Introduced at | `c2fc8d2` (A-068, 2026-08-18), two days AFTER signing | **`885b4da` (2026-08-15), BEFORE signing** |
| Consequence | post-signature text, correctable as maintained evidence under D-057(5) | **INSIDE THE SIGNED BOUNDARY. Correctable only by John's ratification** |

**So the A-080 precedent does not apply here.** §11.0 was correctable because John's signature
never covered it. **This sentence his signature does cover.**

## The exact current text — `docs/gate-s2-evidence.md:284-285`

```
- **§7.2's caveat travels with the numbers** — extracted from §7.2 itself and required in the
  ablation report, after A-028 found the report had published its table without it.
```

## What is false, and what is true

**FALSE: "extracted from §7.2 itself."** `scripts/check-vendor-honesty.sh:269` runs
`grep -F '<anchor phrase>' "$PROPOSAL" | head -1` — a scan of the **whole 84KB proposal**, taking
whichever occurrence comes first. It never locates §7.2. This is `V3-N2`, adjudicated **CONFIRMED,
MEDIUM**, with two falsifications and three opposite-behaving controls.

**TRUE, and must be preserved:** the caveat **is** required in the ablation report — that half of
the check is real and enforced — and **A-028 did** find the report had published its table without
it. **The sentence is false in one clause, not as a whole.**

**Also true, and the reason this is a record-honesty issue rather than a Gate 5 issue:** the
guarded property currently **holds** — the anchor phrase occurs exactly once tree-wide, inside
§7.2 (lines 663–686), and the report carries that wording. Measured independently of the guard by
two parties. **Per D-059(1), the Gate 5 certification STANDS and this correction neither revokes,
reaffirms, nor recertifies it.**

## The exact proposed replacement

```
- **§7.2's caveat travels with the numbers** — required in the ablation report, after A-028
  found the report had published its table without it. **[CORRECTED <date> (D-0NN). The
  original read "extracted from §7.2 itself". That was FALSE about the enforcement mechanism:
  `check-vendor-honesty.sh` scanned the whole proposal and took the first match, never locating
  §7.2 (`V3-N2`, D-055(e) cycle, CONFIRMED MEDIUM). The requirement on the report was real and
  is unchanged; only the claim about WHERE the caveat was extracted from was wrong. Section-
  scoped extraction is being built under D-058's Batch A; until it is repaired and independently
  reverified, this check is NOT admissible as evidence for its §7.2 condition (D-059(1)).]**
```

**Deliberately minimal:** it strikes only the false clause, keeps the true one intact, states the
error before its content per A-048's rule, and names the finding so a reader can follow it.

## What John is being asked to decide

1. **Whether to ratify this correction at all**, or to leave the signed text untouched and record
   the falsehood elsewhere.
2. **If ratified, under which decision identifier** — the placeholder above reads `D-0NN` and must
   be filled with his, not an agent's, allocation.
3. **Whether the correction is CERTIFIED or merely RECORDED.** A-080's precedent distinguishes
   these, and certification of public claims remains autonomy NONE.

**No agent may answer any of the three.**
