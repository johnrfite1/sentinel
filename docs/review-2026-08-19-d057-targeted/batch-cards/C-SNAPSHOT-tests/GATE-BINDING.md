# C-SNAPSHOT — corrected top-level fast-gate binding

**Behavioral baseline:** `1655b120a653b60ccb5b3a22583c0001d59ea7a4`.

**Unchanged gate:** `scripts/test.sh`, sha256
`66c272b90a16b037e3fcfc6f0d9184c48f63ac32e62538be7b6cd96a93801b79`, baseline blob
`0c6c38ed746925d52720468865ca61eb31ae7ddd`.

**Corrected frozen test patch:** sha256
`c2a53a4707d62c3e6632405037d684216c8319dd79fdaad15da2c15de6c69de1`; extracted 485-line test
source sha256 `eea8876c38545db864df36f8d75e7a10e53b47ee730d805dc4ed984f88d6c1f7`.

The patch adds `ts/test/vault.snapshot.classification.test.ts`. The existing TypeScript glob in
`package.json` discovers it automatically; neither `scripts/test.sh` nor `package.json` is edited.

## Unchanged baseline control

In a private detached checkout of the exact baseline, with no patch:

```text
exit=0
foundry: 103 tests (103 passed; floor 92)
typescript: 527 tests (527 passed; floor 527)
suite 221 (floor 221) · samples 7 (floor 7) · tamper 78/30 (floors 78/30)
GATE PASSED
```

Full raw gate-log sha256:
`01c623750c70a15a9e900ce11f7bf813597e896c4f23ae160a97628a06f45dd9`.

## Corrected pre-repair falsification

The same checkout then received only the corrected `TESTS.patch`. No source repair was applied:

```text
exit=5
foundry: 103 tests (103 passed; floor 92)
typescript: 549 tests · 536 passed · 13 failed
the thirteen failures are exactly pure B3, six ordered pairs and six triple-order C-SNAPSHOT tests
the four oracle-negative controls pass
ablation report: regenerates byte-for-byte from the committed results
suite 221 (floor 221) · samples 7 (floor 7) · tamper 78/30 (floors 78/30)
GATE FAILED
GATE DID NOT REACH COMPLETION
```

Full raw gate-log sha256:
`67af49c9a81b3e0a6f4fc8d4803742063d856d5ec6fdc7e147760324c9518a9d`.

The later consumer results are read from body output, not inferred from the supervisor exit. The
exit-5 refusal is the required top-level falsification: a failed TypeScript stage cannot produce a
completion token. The gate's “discard this run” warning remains a limit: this is evidence that the
gate refuses the broken baseline, not a successful gate result.

Raw logs are not tracked because the pre-existing rename guard and TypeScript stack traces print
machine-specific absolute paths. Exact raw hashes are retained; tracked summaries remove only
path, stack, ANSI and timing noise and preserve every scored count and new test name.

## Limit

This binds the **fast profile** only. It does not establish a post-implementation pass,
deep-profile pass, new suite floor or any fact outside the declared two-symbol production
boundary. The live TypeScript floor remains Batch A-owned and unchanged at 527.
