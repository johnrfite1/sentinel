# BRIEF V1 — the two vault repairs that failed reverification once already

Scope: **`R3-F6`** and **`R3-F7`**. Both are in the Solidity vault and its tests. Both were
repaired, sent to a verifier, and **returned as FAILED**. They were then corrected again by the
same author. **You are the first independent eyes on those second corrections.**

Your worktree builds: `forge build` succeeds and `forge test` runs. Run from
`<WORKTREE>/contracts`.

---

## Item 1 — `R3-F6`

**Original finding:** *"All three of the vault's timestamp comparisons are unpinned by one
second; the value ceiling is not. `D-06`'s repair was applied to the TypeScript engine and never
to the Solidity vault."*

**Why it came back FAILED the first time, in the author's own words:** *"I pinned two of three
timestamp boundaries and wrote 'every' and 'all three'. `executeWithOverride`'s `auth.expiresAt`
survived in BOTH directions at 89/89 — the second path by which funds move."*

**What you must establish:**

1. **Every relevant timestamp boundary in the vault is pinned — enumerate them mechanically.**
   Do not take "three" or "four" from any document. Grep the contract for every comparison
   against a time-like field and build your own list. **`executeWithOverride`'s
   `auth.expiresAt` must be in it.** So must anything else your enumeration turns up.
2. **Both directions, for each.** Flipping `<=` to `<` and `<` to `<=` must each be caught. A
   boundary pinned in one direction only is half-pinned.
3. **A paired control that should remain ACCEPTED** — a value comfortably inside the window
   must still succeed. Without it, a vault that had simply started refusing everything would
   pass your check.
4. **Confirm the tests can observe the defect.** Apply each mutation to the contract, run the
   suite, and record which named test fails. A mutation that produces no failure is a hole,
   whatever the suite total says.

---

## Item 2 — `R3-F7`

**Original finding:** *"FIVE of the vault's eight events can be made to state something FALSE
with the suite 75/75 green. §3.3(2)'s 'logged' requirement is asserted for the three events
`D-043` touched and for none of the five it did not."*

**Why it came back FAILED the first time, in the author's own words:** *"I asserted the wrong
five events, including `Recovered` which `D-043` already covered, and omitted `MandateRevoked`,
which had zero assertions anywhere and still survived."*

**What you must establish:**

1. **The COMPLETE required event set, derived from the actual guarantee** — not from the
   finding, not from the repair, and not from any prose count. Read what the vault is supposed
   to log, enumerate the events the contract actually declares and emits, and derive the set
   yourself.
2. **`MandateRevoked` must be explicitly covered.** Say so in as many words, with the evidence.
3. **For EACH required event, show the test can detect both OMISSION and SUBSTITUTION.**
   Delete the emit — does a named test fail? Change a field the event carries to a wrong value,
   or swap one event for another — does a named test fail? An assertion that only checks "some
   event was emitted" detects neither.
4. **A control:** a correct emission must still pass.

---

## Deliverables — write these into `<EVIDENCE>/reviewers/v1/`

- `REPORT.md` — per item: the general property in your own words, your mechanical sibling
  enumeration, exact commands, falsifications with their observed results, controls, what the
  evidence does and does not establish, and a verdict of `HOLD` / `FAIL` / `UNVERIFIABLE`.
- `PROBES.md` — every command you ran and its material output, including probes that failed,
  died, or turned out to measure nothing. **A dead probe you noticed is a finding about your own
  instrument and is worth reporting.**
- `COVERAGE.md` — what you did NOT reach, and why. Blind spots stated plainly.

Verdicts are per finding ID. If `R3-F6` holds and `R3-F7` fails, say exactly that.
