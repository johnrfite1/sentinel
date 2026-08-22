# C-SNAPSHOT — twice-corrected top-level fast-gate binding

**Behavioral baseline:** `1655b120a653b60ccb5b3a22583c0001d59ea7a4`.

**Unchanged gate:** `scripts/test.sh`, sha256
`66c272b90a16b037e3fcfc6f0d9184c48f63ac32e62538be7b6cd96a93801b79`, baseline blob
`0c6c38ed746925d52720468865ca61eb31ae7ddd`.

**Twice-corrected frozen test patch:** sha256
`b6fc3c713e97c2fdfc328516eeb42fdb4f3cc25d0648602ea654e6cf1513c9f1`; extracted 603-line test
source sha256 `29a673560e89b639b6635661706a368454c9969a04c5d37c4f6c15229df3dd8a`.

The patch adds `ts/test/vault.snapshot.classification.test.ts`. The existing TypeScript glob in
`package.json` discovers it automatically; neither `scripts/test.sh` nor `package.json` is
edited.

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
`28e15ef7c8de62ec4a517af2940c7a2e721a5485f48a702692a31a24c5afb67a`.

## Corrected pre-repair falsification

The same detached checkout then received only the frozen `TESTS.patch`. No source repair was
applied:

```text
exit=5
foundry: 103 tests (103 passed; floor 92)
typescript: 550 tests · 536 passed · 14 failed
thirteen retained named R2-F6 failures plus one exhaustive aggregate failure
aggregate attempted/observed/route-verified/classification-checked = 486/486 each
four oracle-negative controls pass
ablation report: regenerates byte-for-byte from the committed results
suite 221 (floor 221) · samples 7 (floor 7) · tamper 78/30 (floors 78/30)
GATE FAILED
GATE DID NOT REACH COMPLETION
```

Full raw gate-log sha256:
`b17e2eedf201fb3af688b77b9be987dc8c32fd504a44766b63215ebc53d40931`.

The later consumer results are read from body output, not inferred from the supervisor exit. The
exit-5 refusal is the required top-level falsification: a failed TypeScript stage cannot produce a
completion token. The gate's “discard this run” warning remains a limit: this is evidence that the
gate refuses the broken baseline, not a successful gate result.

Raw logs are not tracked because the pre-existing rename guard and TypeScript stack traces print
machine-specific absolute paths. Exact raw hashes are retained. Tracked summaries remove only
path, stack, ANSI and timing noise while preserving scored counts, new test names and the
exhaustive traversal counters.

## Limit

This binds the **fast profile** only. It does not establish a post-implementation pass,
deep-profile pass, new suite floor or any fact outside the declared two-symbol production
boundary. The live TypeScript floor remains Batch A-owned and unchanged at 527.
