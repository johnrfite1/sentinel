# C-SNAPSHOT log policy

Raw Node failure logs contain isolated-checkout absolute paths in stack traces. Both raw fast-gate
logs also contain the pre-existing rename guard's repository path. Workspace rules forbid tracking
those paths.

The corrected raw files were retained outside the repository and are bound by sha256 in
`RESULTS.md`, `GATE-BINDING.md`, and `mutation-matrix.tsv`. The tracked summaries preserve the
exact scored counts, stage outcomes, all 23 focused top-level test names, all four 486/486
exhaustive traversal counters, and corrected patch/source identities while omitting only absolute
paths, stack frames, ANSI color and timings. Both independent review records remain byte-untouched.
None of these files answers a held D-008 question.
