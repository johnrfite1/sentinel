# LENS 8 — THE CLAIMS. Every document, every comment, every printed line. THIN.

**Your surface is deliberately not a directory. It is every CLAIM this repository makes**
— in `docs/`, in the proposal, in code comments, in the text the gate prints on every run,
in READMEs, in commit messages that a decision entry relies on.

**Your assignment: find a statement that is not true.**

This is a THIN brief on purpose. Round two established that thin briefing does not cost
yield and in fact raised it. **Do not let the leads below narrow you** — they are calibration
for what "not true" has meant here, not a checklist.

**Calibration — what previous claims-lens reviewers actually found:**
- **Four false statements in ONE printed block** (the gate's COVERAGE BOUNDARY), two of
  which no reviewer reported. It published three stale verifier figures while asserting
  "ALL THREE FIGURES ARE FLOORS THIS RUN ASSERTS", 142 lines after the same run printed
  different floors.
- A document telling a fresh instance that a section "is now empty" **22 lines after
  telling it to read that section**, when the section had six live entries.
- A decision entry claiming a suite went 154 → 158 when its commit **added zero test
  methods** — the same four tests counted in two consecutive entries.
- A claimed "committed `.env.example`" that does not exist and is gitignored, cited by a
  guard as the documentation of its own allowlist.
- An annotation to the SIGNED Gate S2 pack that **misdescribed what the pack said**, in a
  way that reached a facilitated ratification.

**The highest-value target class, stated plainly:** a claim in a document John has
CERTIFIED or SIGNED, or one a decision entry rests on. §7.1's containment claim was wrong
twice and is now certified by John (D-051(a)) — **it is not exempt from your audit; verify
it against the code rather than against the correction's own prose.**

**Method that has worked here:** take each stated number and each "verified/tested/covered"
verb, and go find the thing it names. Most defects are a claim whose referent moved.

**Two specific things to check because they are mechanically checkable:**
- Every count printed by `./scripts/test.sh` against what that same run measured.
- Every count in `docs/session-state.md` §3 and `docs/round-six-brief.md` against a real
  run. **Both files warn that they have been wrong repeatedly — including the line that
  says "verified as of this commit".**

**Read `docs/v1-1-register.md` §13 and `docs/gate-s2-evidence.md` §11/§11.0 first** so a
re-report is not mistaken for a finding. Note `A-2`, `B-1`..`B-7`, `C-2`, `E6` and `C-4`
are recorded claims findings — several were fixed, one (`C-2`/the COVERAGE BOUNDARY in
`scripts/test.sh`) was explicitly left as unscoped remediation. **Check its CURRENT state
rather than assuming either way.**

Baseline: run the gate once and read what it prints, since what it prints is your surface.
