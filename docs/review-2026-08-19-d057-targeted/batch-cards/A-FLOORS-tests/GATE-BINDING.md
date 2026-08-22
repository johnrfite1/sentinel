# A-FLOORS — fast and deep top-level gate binding

## Correction status and reliance limit

Review-1 F1/F2, Review-2's parser-state finding, Review-3's missing opposite-side reader
oracle and Review-4's uncorrelated diagnostic matcher change only focused source/assignment
or diagnostic-correlation stimuli.
The 328-line gate harness is
byte-unchanged at sha256 `fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0`,
and `gate-matrix.tsv` is byte-unchanged at
`0b4d9c127e7230c7266960fe073f92f9551da9a68005cb936850993d803d1c58`.

The seven expensive gate cases were therefore not rerun for any of the four bounded corrections. Everything
below is retained historical author evidence from the original subject: it remains relevant to
the unchanged gate design, but the fourth correction neither refreshes its timings/raw logs nor
claims independent reinspection of the external logs. Fourth-corrected focused evidence is in
`RESULTS.md`.

**Baseline:** `1a133301533e9d959dbafbbcc7ffe05e7eb78df3`.

**Frozen gate:** `scripts/test.sh`, sha256
`66c272b90a16b037e3fcfc6f0d9184c48f63ac32e62538be7b6cd96a93801b79`, blob
`0c6c38ed746925d52720468865ca61eb31ae7ddd`.

**Frozen reader:** `scripts/check-suite-floors.sh`, sha256
`c9a334dca2ce06e78a126e15dd33ef19bd0df3b43569eb0de76ea0b1c3ac13b6`, blob
`d69cc9a403719908139fdd660a126e254014d45b`.

The frozen serial harness creates a separate exact-commit clone for each case and invokes cases
synchronously. The final evidence contains no overlapping gate or timing measurement.

## Baseline controls

Unchanged fast:

```text
exit=0
foundry: 103 tests (floor 92)
typescript: 550 tests (floor 527)
suite 221 (floor 221) · verdict clean · samples 7 (floor 7) · tamper 78 cases / 30 modes (floors 78/30)
GATE PASSED
```

Unchanged isolated deep adds:

```text
corpus: 50 fixtures executed; committed views verified FILE BY FILE
This IS the deep profile (--gate)
exit=0
GATE PASSED
```

Only raising the two stale floors also passes:

```text
foundry: 103 tests (floor 103)
typescript: 550 tests (floor 550)
verifier quartet unchanged and green
exit=0
GATE PASSED
```

## Current missing wiring, falsified on both profiles

In G1 and G3 only the enumerated §3 stable paragraph is replaced by an incorrect wrapped live
publication. At baseline both gates still emit the same successful counts and `GATE PASSED`.
The deep case also executes all 50 corpus fixtures and verifies committed views. Thus
`scripts/check-suite-floors.sh` is not currently load-bearing on either profile.

The repaired contract reverses those exact outcomes. The checker must print a line naming
`session-state`, the current/live/maintained class and the duplicate/publication/derivation reason;
the gate must accumulate that failure, continue through the later successful consumers, omit
`GATE PASSED`, and let the supervisor exit 5 with `GATE DID NOT REACH COMPLETION`. A later green
Foundry, TypeScript, verifier or deep corpus stage cannot mask the earlier named failure.

## Floor preservation falsification

With floors 103/550, deleting the B file produces:

```text
foundry: 92 tests (floor 103)
FLOOR BREACHED — foundry tests: 92, floor 103.
typescript: 550 tests (floor 550)
verifier 221/7/78/30 green
GATE FAILED
GATE DID NOT REACH COMPLETION
exit=5
```

Deleting the C file produces:

```text
foundry: 103 tests (floor 103)
typescript: 527 tests (floor 550)
FLOOR BREACHED — typescript tests: 527, floor 550.
verifier 221/7/78/30 green
GATE FAILED
GATE DID NOT REACH COMPLETION
exit=5
```

The later successes are read from body output, not inferred from the supervisor status. The
missing-completion message is not success evidence; it is the required failed-closed top-level
falsification.

## Limit

This binds only the enumerated floor/source/publication guard on the real fast and deep paths and
the two B/C count deltas. It is not generic prose-consistency evidence, a deep timing budget, a
post-repair pass or a gate signature.
