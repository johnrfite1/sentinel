# F61ECCA verification card

Bounded verification card commissioned by John 2026-08-23. It independently
verifies, at the current freeze, that the repairs claimed at `f61ecca` for
**C4, C6a, C6b, C6c, C6d, R1** hold behaviourally. It is not a gate. It is not
an A1 reopening beyond the test-clause lift, which is spent at this card's freeze.

## Authorisation

- Narrow lift of A1's "no further A1 test" bar, this card only, spent at freeze.
- No A1 production change.
- No A1 verdict relabelled.
- Independent reviewer assigns severity to anything that does not hold.
- R1's severity has never been adjudicated (`R1-ADJUDICATION.md`: "No claim
  about severity or priority"). T2 puts severity with the reviewer.

## Method

Exploit control first, observing test second, V-1 shape. See `EXPLOIT-CONTROL.md`.
Harness: `f61ecca-verify.sh`. Coverage map: `COVERAGE.md`. C6d completing probe:
`C6d-PROBE.md`. Independent brief: `REVIEW-BRIEF.md`.

## Out of scope

D-055 verdict. Gate signing. Signed-prefix edit. Publication. Push. Rename.
Frozen-harness rewrite. The five D-008 comprehension questions.
