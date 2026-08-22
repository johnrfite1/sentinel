# Preserved outputs

The focused, current-suite, frozen-mutant, live-receipt and NatSpec logs are byte-exact command
outputs. `mutation-matrix.tsv` is the byte-exact final matrix.

The two complete top-level gate logs each contained one machine-specific repository path printed
by the pre-existing rename guard. The workspace rule forbids tracking that path. Their full raw
bytes are therefore identified by sha256 in the summary files; the summaries preserve the exact
scored lines, exit status and elapsed time without the path. No gate output was used to expose or
answer any held D-008 question.

The elapsed times are observations only. Both final gate runs overlapped mutation compilation and
are not a normal gate-duration basis.
