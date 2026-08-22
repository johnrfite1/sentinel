# D-CLAIMS RESULTS — pre-repair demonstration

Instrument measurement only. Not a HOLD, signature, or implementation.

**Subject:** `1e7761be051422ad8091b203df375ddcfb7d1208`
**Harness sha256:** `2e409a2e3226899a33994dea8c3c10cf629cf939701902dd2494cae185ab07e0`
**Source:** disposable clean clone of the live repository; subject checked out detached.

| Variant | REQUIRED | CONTROL | Exit | Notes |
|---|---|---|---:|---|
| `baseline` | 0/10 | 26/26 | 1 | Every live false claim present; every control holds. Completion withheld. |
| `fix-d6` | 2/10 | 26/26 | 1 | Only `R-D6-absent` and `R-D6-truth` PASS. |
| `fix-all` | 10/10 | 26/26 | 0 | `D_CLAIMS_FOCUSED_COMPLETE`. Oracle completeness, not a product commit. |
| `break-s1` | 0/10 | 25/26 | 1 | Exactly `C-D1-s1` FAIL. |
| `break-s2-prefix` | 0/10 | 25/26 | 1 | Exactly `C-D2-prefix` FAIL. |
| `break-floors` | 0/10 | 25/26 | 1 | Exactly `C-floors` FAIL. |
| `break-bevents` | 0/10 | 25/26 | 1 | Exactly `C-B-EVENTS` FAIL. |
| `break-d014` | 0/10 | 25/26 | 1 | Exactly `C-D4b-d014` FAIL. |

Independent review of this instrument is required before any of the five production surfaces is edited.
