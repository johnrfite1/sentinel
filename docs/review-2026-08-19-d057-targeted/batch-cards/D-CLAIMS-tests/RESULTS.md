# D-CLAIMS RESULTS — first-correction demonstration

Instrument measurement only. Not a HOLD, signature, or implementation.
`INSTRUMENT-REVIEW-1.md` is preserved byte-identical at sha256
`fd48278dc9946342868e73b6e4ca8ad596ae0f34237618d0359ac0047e5cab35`.

**Subject:** `1e7761be051422ad8091b203df375ddcfb7d1208`
**Harness sha256:** `f53121e4c9ab4bc68b536df010d4637cc36d8e702b36be70582317afce8027ed`
**Source:** disposable clean clone of the live repository; subject checked out detached.

| Variant | REQUIRED | CONTROL | Exit | Notes |
|---|---|---|---:|---|
| `baseline` | 0/14 | 26/26 | 1 | Every live false claim present; every control holds. Completion withheld. |
| `fix-d6` | 2/14 | 26/26 | 1 | Only `R-D6-absent` and `R-D6-truth` PASS. |
| `fix-all` | 14/14 | 26/26 | 0 | `D_CLAIMS_FOCUSED_COMPLETE`. Strikes BLOCKER exit sentence and FIVE heading; writes full D2_TRUTH including D-09; packet NON-BLOCKER ten→six. Oracle completeness, not a product commit. |
| `break-s1` | 0/14 | 25/26 | 1 | Exactly `C-D1-s1` FAIL. |
| `break-s2-prefix` | 0/14 | 25/26 | 1 | Exactly `C-D2-prefix` FAIL. |
| `break-floors` | 0/14 | 25/26 | 1 | Exactly `C-floors` FAIL. |
| `break-bevents` | 0/14 | 25/26 | 1 | Exactly `C-B-EVENTS` FAIL. |
| `break-d014` | 0/14 | 25/26 | 1 | Exactly `C-D4b-d014` FAIL. |
| `break-reason-split` | 0/14 | 25/26 | 1 | Exactly `C-D6-codes` FAIL (`SIGNER_CHAIN_PENDING_HEAD`). |

Independent review of this correction is required before any of the five production surfaces is edited.
