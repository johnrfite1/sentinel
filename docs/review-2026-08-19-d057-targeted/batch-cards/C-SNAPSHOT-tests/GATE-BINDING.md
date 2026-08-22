# C-SNAPSHOT — top-level fast-gate binding

**Subject:** `1655b120a653b60ccb5b3a22583c0001d59ea7a4`.

**Unchanged gate:** `scripts/test.sh`, sha256
`66c272b90a16b037e3fcfc6f0d9184c48f63ac32e62538be7b6cd96a93801b79`, subject blob
`0c6c38ed746925d52720468865ca61eb31ae7ddd`.

**Frozen test patch:** sha256
`51fba356e71fe648e78e85d551b6092b649d843645dde4338f64ca6b932450df`; extracted test source
sha256 `92267b368fb24c1f466e63d7d8344d6884d00c5e96957d612047c642228652c5`.

The patch adds `ts/test/vault.snapshot.classification.test.ts`. The existing TypeScript glob in
`package.json` discovers it automatically; neither `scripts/test.sh` nor `package.json` is edited.

## Unchanged baseline control

In a private detached clone of the exact subject, with no patch:

```text
exit=0
foundry: 103 tests (103 passed; floor 92)
typescript: 527 tests (527 passed; floor 527)
suite 221 (floor 221) · samples 7 (floor 7) · tamper 78/30 (floors 78/30)
GATE PASSED
```

Full raw gate-log sha256:
`4063b39735e29a7eef3d83b17d9ddad18c19228ec885031bb010f1e6f799d082`.

## Frozen pre-repair falsification

The same clone then received only `TESTS.patch`. No source repair was applied:

```text
exit=5
foundry: 103 tests (103 passed; floor 92)
typescript: 537 tests · 532 passed · 5 failed
the five failures are exactly the named pure-B3 and four mixed C-SNAPSHOT tests
ablation report: regenerates byte-for-byte from the committed results
suite 221 (floor 221) · samples 7 (floor 7) · tamper 78/30 (floors 78/30)
GATE FAILED
GATE DID NOT REACH COMPLETION
```

Full raw gate-log sha256:
`abe31cc453e448ffa608f468e5c6c814476d4a59629998cfec4b627e93573bc8`.

The later consumer results are read from the body output, not inferred from the supervisor exit.
The exit-5 supervisor refusal is the required top-level falsification: a failed TypeScript stage
cannot produce a completion token. The gate's “discard this run” warning is preserved as a limit:
this is evidence that the gate refuses the broken baseline, not a successful gate result.

Raw logs are not tracked because the pre-existing rename guard and TypeScript stack traces print
machine-specific absolute paths. The exact raw hashes are retained; tracked summaries remove only
path and timing noise and preserve the scored stage lines and test names.

## Limit

This binds the **fast profile** only. It does not establish a post-repair pass, deep-profile pass,
new suite floor, or any fact outside the declared two-symbol production boundary.
