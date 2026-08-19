# LENS 1 — `scripts/**`: the guards and the gate. DIRECTED.

**Your surface:** every script in `scripts/`, and `scripts/test.sh` itself — the ten
mechanical stages, what each one claims, and the COVERAGE BOUNDARY block it prints.

**Your assignment, in one sentence: BREAK A GUARD.** Not "confirm a guard fires on the
violation it was designed for" — that measures the designer's imagination, not the guard.
A previous round reported "8/8 guards caught, 0 defeated" as a headline; an independent
reviewer told to DEFEAT a guard produced **seven confirmed defeats within hours**, every
one a violation of that guard's own stated purpose. That correction is the reason your
lens is worded this way.

**Three stages are NEW since round five and NONE has been independently reviewed:**
- `check-label-integrity.sh` (the labelling-artifact pinning, A-064)
- the corpus-VERDICT comparison inside the deep stage (A-064)
- the §7.3 ablation-report provenance stage (A-062)

**Break one of those three by preference.** They are the least-examined code in the repo.

**Specific leads, all unconfirmed — confirm or refute, do not assume:**
- For each guard, ask: what is the guard's STATED purpose, and what is the smallest
  violation of that stated purpose it does NOT catch? That framing found all seven defeats.
- The gate's printed COVERAGE BOUNDARY has carried stale verifier figures while labelling
  them "FLOORS THIS RUN ASSERTS". Check every number it prints against what the run
  actually measured, on the same run.
- Guards that pass on a RATCHET rather than on a pass (class coverage, vendor honesty):
  does the ratchet actually arm? Can it be laundered — e.g. through committed `results/`?
- `check-secrets.sh` has been holed three times, most recently by line-scoped suppression.
  Find the fourth hole. **Use only synthetic key-shaped constants you generate; never a
  real key, and do not commit any artifact containing one.**

**Run the gate at least once on the untouched worktree first** (`./scripts/test.sh`; add
`--gate` if you can) and record it. `export PATH="$HOME/.foundry/bin:$PATH"` and
`forge build --root contracts` before anything Solidity-dependent.
