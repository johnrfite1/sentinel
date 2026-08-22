# Tracked log policy

Full raw gate logs are not tracked because the pre-existing rename stage prints a
machine-specific absolute repository path. `RESULTS.md` binds every full raw file by sha256.

The original, first-correction and `v2` second-correction summaries/matrices remain unchanged as
historical evidence. Files carrying `v3` are the third-correction measurements: baseline,
digits-zero sibling, exact Review-2 raw-reader sibling, exact Review-3 non-comment sibling,
separately expanded all-token sibling and corrected exact-positive control. They preserve route
totals, exact causal scopes and external raw hashes. The unchanged gate summary/matrix preserve
historical serial cases. No verdict is reconstructed from summaries alone; reproduction uses the
frozen harnesses.
