# Tracked log policy

Full raw gate logs are not tracked because the pre-existing rename stage prints a
machine-specific absolute repository path. `RESULTS.md` binds every full raw file by sha256.

The original focused summary/matrix are preserved with `review1` in their names. The current
baseline, zero-sibling and exact-positive summaries/matrices preserve exact totals, causal failure
sets and raw sha256. The unchanged gate summary/matrix preserve the historical serial cases.
No verdict is reconstructed from summaries alone; reproduction uses the frozen harnesses.
