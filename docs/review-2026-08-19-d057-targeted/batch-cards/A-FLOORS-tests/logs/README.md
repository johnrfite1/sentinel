# Tracked log policy

Full raw gate logs are not tracked because the pre-existing rename stage prints a
machine-specific absolute repository path. `RESULTS.md` binds every full raw file by sha256.

The two tracked summaries preserve only exact scored output lines, case result, elapsed time and
raw sha256. `focused-matrix.tsv` and `gate-matrix.tsv` preserve every scored row. No verdict is
reconstructed from these summaries alone; reproduction uses the frozen harnesses.
