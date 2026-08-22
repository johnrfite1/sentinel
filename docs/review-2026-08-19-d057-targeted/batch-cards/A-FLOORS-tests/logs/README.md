# Tracked log policy

Full raw gate logs are not tracked because the pre-existing rename stage prints a
machine-specific absolute repository path. `RESULTS.md` binds every full raw file by sha256.

The original and first-correction summaries/matrices remain unchanged as historical evidence.
Files carrying `v2` are the second-correction measurements: baseline, zero sibling, exact Review-2
raw-heredoc sibling and corrected exact-positive control. They preserve route totals, causal
failure sets and external raw hashes. The unchanged gate summary/matrix preserve historical serial
cases. No verdict is reconstructed from summaries alone; reproduction uses the frozen harnesses.
