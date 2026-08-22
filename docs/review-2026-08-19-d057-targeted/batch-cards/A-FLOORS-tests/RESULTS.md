# A-FLOORS — second-corrected measured pre-repair results

## Verdict

**HOLD for second-corrected test-contract readiness, pending fresh independent Review 3.** No
production repair, post-repair pass, approval or gate replay exists.

## 1. Frozen history and correction identity

Original subject `e8b4d29641c47f0099482c9a9ac5da86c9255197` and first correction
`69e4fda92401e29c0cd4c717538fc278a5e59e26` remain historical evidence. Review 2 reproduced the
first correction and returned FAIL in exact review-only commit
`9889289cb730a7ef23b2b9d11c0e84110dce84f6`. Both `INSTRUMENT-REVIEW-*.md` files and all prior
matrices/log summaries are byte-preserved.

The second-corrected harness is 859 lines, sha256
`fb9577d3182cc881e4c2c4f5bca9c02d1ddf8ed04bd64d9f85e0db4d0985896d`. Every final run below
used that external harness against a disposable clean clone at exact Review-2 commit.

## 2. Second-corrected baseline

```text
REQUIRED 10/131
CONTROL 120/120
PRE-REPAIR DEFECTS OBSERVED
exit=1
```

The ten old passes remain six missing-definition refusals and the current verifier quartet. All
new parser-state requirements fail at the current reader, as intended before repair. Every new
Bash witness passes, `T-route-complete` reports 54/54, and all 251 case names are unique.

Raw sha256: `a18333f67c4405af8b86aa7d6f4cfb9f94df380d31ae4744174cd40701f069e4`.
Matrix sha256: `26039eccc906f3db9a5d8f97c7710e17fe6e007187c5503fcfd54fb16b9eaf35`.

## 3. Finite route execution

For each of six constants the matrix executes nine paired fake-opener routes:

| Form family | Spellings | Routes | Bash witness |
|---|---:|---:|---|
| full-line comment | 1 | 6 | canonical then indented 999; final 999 |
| `printf` quoted argument | 2 | 12 | canonical then indented 999; final 999 |
| `echo` quoted token | 2 | 12 | canonical then indented 999; final 999 |
| quoted assignment value | 2 | 12 | canonical then indented 999; final 999 |
| here-string quoted payload | 2 | 12 | canonical then indented 999; final 999 |
| **total** | **9** | **54/54** | **all pass** |

The actual Bash trace is required to equal `[planned, 999]`, not merely finish at 999. Six
`HR-post-*` routes separately prove a genuine quoted-heredoc body does not execute `NAME=888` and
that a following indented 999 is visible after the terminator. Existing `IH-*` controls preserve
the body-only inert case.

## 4. Exact Review-2 flawed reader

The reconstructed candidate preserves Review 2's exact ordering: raw marker search occurs before
quote/context classification, while full-line comments are excluded. It uses the exact positive
value predicate and returns:

```text
REQUIRED 83/131
CONTROL 120/120
exit=1
```

All 136 prior rows are present and PASS (zero missing, zero non-pass). All six comment pairs and
six genuine-heredoc post rows pass. Its exact 48-row failure set is:

- 12 `TF-printf-*` rows;
- 12 `TF-echo-*` rows;
- 12 `TF-assign-*` rows; and
- 12 `TF-herestring-*` rows.

Each family is single/double quoted × six constants. Raw sha256:
`33a0b2d3b12cdb8f89b2b45b30774baee93f488797573b11033d056c5178fbc4`.
Matrix sha256: `a49891dcfcfc5da17e0003a7ed1148901d7437d123e8e2b6347d4c6575babfc7`.

The here-string stimulus is the review's exact `: <<< 'A_FLOOR_MASK'` shape. A provisional setup
used an enriched quoted payload containing an assignment; the regex backreference then had no
closing quote immediately after the delimiter and did not reproduce the review route. That setup
was not counted. The final exact stimulus reproduces the raw-reader state bug and is the evidence
reported above; no altered mutant was manufactured to force the total.

## 5. Zero and satisfying controls

The corrected finite lexer with digits including zero returns:

```text
REQUIRED 125/131
CONTROL 120/120
exit=1
```

Its only failures are the six `Z-*` rows. Raw/matrix sha256:
`6b11d16b4d56040e78b2305b5bdc95a3be18451ee5fbb3c8899f3ff57d7f3350` /
`93444b6b196518050ef16948743459112f1550ca7008a6a231cf9d42ae26ec08`.

The corrected exact-positive sibling returns:

```text
REQUIRED 131/131
CONTROL 120/120
A_FLOORS_FOCUSED_COMPLETE
exit=0
```

All 136 prior rows pass and all 115 added rows pass. Raw/matrix sha256:
`9044d8e72217b9bc03c023ff109b22663852c12f07d45f38bed70359efa84fd9` /
`5d390a4fe8a1600d3430abb340e28e0f0f22e3389ad2f87e61636fa49a9244c1`.

## 6. Historical serial gate reliance

The gate harness/matrix remain byte-identical at
`fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0` /
`0b4d9c127e7230c7266960fe073f92f9551da9a68005cb936850993d803d1c58`. The parser-state
correction adds only focused source fixtures, so no expensive gate was rerun. Prior serial scores,
raw hashes and timings remain in unchanged `logs/gate-summary.log` as historical design reliance;
this correction does not refresh or independently reinspect them.

## 7. Limits

Full focused raw logs remain external and hash-bound. This evidence establishes only the exact
finite opener grammar in `CARD.md`, not command substitution, escaped/concatenated quoting,
arbitrary redirection, general Bash parsing, generic Markdown consistency, historical truth,
implementation, certification, signing, publication or D-055 closure.

## 8. Guards

With the second correction confined to this directory:

- secret guard, worktree and staged modes: `clean`;
- review scope: worktree pass at 610/610 (R1 411 / R2 47 / R3 152), then staged pass at
  618/618 tracked files (R1 419 / R2 47 / R3 152);
- findings ledger: pass with 23 IDs and D-057(1) totals unchanged;
- live floor reader: exit 0 at `92/527/221/7/78/30`;
- vendor-honesty mechanical guard: pass, leaving D-008 authority exactly as printed; and
- workspace guard: pass with 13 pre-existing machine-state findings baselined and zero new.

Workspace success remains ratcheted: the 13 pre-existing findings are accepted debt, not absent.
