# D-CLAIMS RESULTS — second-correction demonstration

Instrument measurement only. Not a HOLD, signature, or implementation.
Reviews 1 and 2 are preserved byte-identical:

- `INSTRUMENT-REVIEW-1.md` sha256 `fd48278dc9946342868e73b6e4ca8ad596ae0f34237618d0359ac0047e5cab35`
- `INSTRUMENT-REVIEW-2.md` sha256 `766cfc1f338ff769f2e9f5d561285d09e5616bd0d6f7117e66478863629b0aa6`

**Subject:** `1e7761be051422ad8091b203df375ddcfb7d1208`
**Harness sha256:** `cee101a25f3aeb745b83a1a1328605a84962d87ebaa51b3f86e4797c240b1ad5`
**Source:** disposable clean clone of the live repository; subject checked out detached.

| Variant | REQUIRED | CONTROL | Exit | Notes |
|---|---|---|---:|---|
| `baseline` | 0/14 | 26/26 | 1 | Completion withheld. |
| `fix-d6` | 2/14 | 26/26 | 1 | Only the D6 pair PASS. |
| `fix-all` | 14/14 | 26/26 | 0 | `D_CLAIMS_FOCUSED_COMPLETE`. Closed-span strikes; not a product commit. |
| `break-reason-split` | 0/14 | 25/26 | 1 | Exactly `C-D6-codes` FAIL. |
| `break-reason-quoted` | 0/14 | 25/26 | 1 | Exactly `C-D6-codes` FAIL. |
| `break-reason-space` | 0/14 | 25/26 | 1 | Exactly `C-D6-codes` FAIL. |
| `break-reason-comment` | 0/14 | 25/26 | 1 | Exactly `C-D6-codes` FAIL. |
| `break-reason-newline` | 0/14 | 25/26 | 1 | Exactly `C-D6-codes` FAIL. |
| `break-live-strike` | 11/14 | 26/26 | 1 | Exactly `R-D1-blocks`, `R-D1-ten`, `R-D2-five` FAIL. |
| `break-s1` | 0/14 | 25/26 | 1 | Exactly `C-D1-s1` FAIL. |
| `break-s2-prefix` | 0/14 | 25/26 | 1 | Exactly `C-D2-prefix` FAIL. |
| `break-floors` | 0/14 | 25/26 | 1 | Exactly `C-floors` FAIL. |
| `break-bevents` | 0/14 | 25/26 | 1 | Exactly `C-B-EVENTS` FAIL. |
| `break-d014` | 0/14 | 25/26 | 1 | Exactly `C-D4b-d014` FAIL. |

Independent review of this correction is required before any of the five production surfaces is edited.
