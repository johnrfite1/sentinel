# LENS 3 — `ts/src/evaluate/**`, `ts/src/decode/**`. DIRECTED. Mutation sweep.

**Your surface:** the conformance engine and the calldata decoders — the code that turns a
proposed action into a verdict.

**Why this surface matters more than its test count suggests:** the HANDOFF's verification
partition says this engine is *cheap to run and expensive to trust* — "its bar is the
independently labeled corpus, never its own suite, because self-written tests encode the
same misunderstanding twice." You are the outside eye that partition calls for.

**Your method is a MUTATION SWEEP.** Mutate the engine; run the full suite AND the gate;
report every mutation that SURVIVES a green gate. A survivor is an unasserted behaviour.

**The specific lead you are handed:** both window lower bounds are now exercised (that was
`D-01`/`D-02`, fixed), **but the boundary comparisons themselves — `<=` vs `<` — are
reported UNPINNED and UNADJUDICATED.** `D-06` claims every ceiling and deadline comparison
boundary in the engine can be flipped with nothing failing. **That is a reviewer-only lead
that was never independently confirmed. Confirm it or refute it, with a control.**

**Other recorded-but-unconfirmed leads on your surface** (`D-04`, `D-05`, `D-07`, `D-08`,
`D-09`, `D-10`, `C-3`, `E5`) — several were fixed in A-067/A-068 and some were ACCEPTED as
limits in §11.0. **Read `docs/v1-1-register.md` §13 and `docs/gate-s2-evidence.md` §11.0
FIRST** so you can tell a re-report from a new finding. Showing an accepted limit is worse
than recorded IS a new finding.

**Mutation hygiene is where this goes wrong:** confirm each mutation actually took effect
(TypeScript may be cached or the file may not be the one executed). **State what each
mutation MOVED.** A mutation of a value already at its bound moves nothing and reads
exactly like a caught mutation.

Baseline first. `export PATH="$HOME/.foundry/bin:$PATH"`.
