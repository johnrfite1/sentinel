# LENS 4 — `contracts/src/**` and the invariant campaign. DIRECTED.

**Your surface:** the Solidity — `SentinelVault` and its supporting types — plus the
Foundry invariant campaign that claims to bound it.

**Your assignment, worded exactly as the ratified brief words it: TWO LIMIT TESTS NOW
ASSERT WHAT THE VAULT DOES NOT BOUND. FIND THE THIRD THING IT DOES NOT BOUND.**

Context you need, because it is the live history of this exact claim: §7.1's containment
sentence has been **wrong twice**. It first said the vault caps native value; the
correction said it caps native value only per-action; the measured truth is that
`maxNativeValueWei` is compared PER ACTION and **no cumulative or rate-limited bound exists
anywhere in `contracts/src`** — a capped vault was drained to zero by 100 valid ALLOW
receipts each at exactly the cap. That is now corrected, tested, and **certified by John**
(D-051(a)). **You audit that certified claim inside the loop — it is not exempt.** Verify
the test that guards it actually fails if the limit is ever closed.

**So: what ELSE does the vault not bound?** Rate? Frequency? Token value (as opposed to
native)? Gas? Call depth? Number of outstanding receipts? Anything the docstrings imply is
bounded and no code checks.

**On the invariant campaign — this is the other half of your lens.** Recorded and
unconfirmed: `F-VAULT-3` says the repaired campaign **cannot construct a violation of ANY
of the vault's twelve action- and receipt-validation checks — 12/12 mutations survive all
eleven invariants.** If true, the campaign is close to decorative. **Measure it yourself.**
`F-VAULT-4` (a tautological invariant) and `F-VAULT-5` (a docstring resting on owner
authority the automatic path never checks) are ACCEPTED limits in §11.0 — re-reporting them
is not a finding; showing them worse than recorded is.

**A previous review found Gate 6's claim was carried by the deterministic tests, not by the
campaign it names** — 31/31 mutations still caught with the entire stateful campaign
disabled. Check whether that is still true.

`export PATH="$HOME/.foundry/bin:$PATH"`; `forge build --root contracts` first. Use
`--force` after mutations. **Confirm every probe COMPILED** — a Solidity probe that does
not compile prints no PASS/FAIL line and reads exactly like a pass. That happened here.
