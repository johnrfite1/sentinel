# D-071 / D-072 verification card — frozen observing contract

Independent test-author card. Commissioned by John 2026-08-23 after the
repairs already existed. **This card does not score the current freeze.
It does not assign severity. It does not change production.**

## Authorisation

- **D-058(1)** test-first separation, applied **retrospectively**: the
  observing tests are written against the **parents of the repair
  commits**, which are the pre-repair baselines. That is the authorised
  method for this card, not a licence to change production.
- **D-071** (R5 option C). **D-072** (V-6 pin at the enumerating call).
- **D-067** named completeness limits (`R2`, `V-6` on D-008(2)/(4)) stay
  named. This card does not lift them.
- John's 2026-08-23 card instruction: write observing tests, demonstrate
  they FAIL at those baselines with exploit-control-before-observe,
  freeze the contract, **stop**.

A different agent verifies the current freeze. A different agent
adjudicates severity.

## THE INVARIANT — two, one per ruling

**D-071 / R5.** Deep/`--gate` UNVERIFIED refuses unless the named
acknowledgement is set; fast UNVERIFIED still exits 0; the
acknowledgement variable is named **on** the UNVERIFIED line; an
acknowledged deep run states in its own output that D-016 was
acknowledged, not verified. Coverage: origin visibility via `gh` when
readable.

**D-072 / V-6 and R2.** Production untracked censuses used as a secret
census or as a D-008(2)/(4) artifact census must still see a planted
untracked file when git's documented config/env inputs would hide that
file from an unpinned `git ls-files --others --exclude-standard`.
Non-ASCII untracked paths must not be dropped by quote-path octal
escape at the vendor-honesty `artifacts()` site.

## BOUNDARY

**In, R5:** `scripts/check-rename-gate.sh` fast and `--gate` profiles,
and `scripts/test.sh --gate` as the top-level instrument that must not
print `GATE PASSED` when the rename-gate is deep/UNVERIFIED/no-ack.

**In, V-6/R2:** `scripts/check-secrets.sh` default mode (untracked
credential census) and `scripts/check-vendor-honesty.sh` `artifacts()`
(D-008(2) label scan and D-008(4) vendor-name scan).

**Out:** `scripts/check-v1-index-ordering.sh` (its untracked scan is its
own fixture, not a production census). Frozen harnesses. Production
repairs. D-055 verdict. Gate signing. Publication. Push. Rename.
D-016's other verbs (demos, published links, portfolio or resume
references). The five D-008 comprehension questions.

## BASELINES (measured; not taken from the brief)

| Role | SHA |
|---|---|
| R5 repair | `1ae684cec83c7bfdb24a8c18ffdeba87c535874f` |
| **R5 baseline (parent)** | `558d001546b55bd80156bc875cf080fef0e301eb` |
| V-6/R2 repair | `4ad6036d81fa66a35a0c3efb4eab117438e3ca38` |
| **V-6/R2 baseline (parent = R5 repair)** | `1ae684cec83c7bfdb24a8c18ffdeba87c535874f` |

Subject under test at a baseline is **that worktree's** `scripts/*`.

## TEST MATRIX

See `EXPLOIT-CONTROL.md` for the control that must fire **before** each
REQUIRED assertion. A row whose control does not fire is NOT_MEASURED
and is not counted.

### R5 (D-071) — subject: R5 baseline SHA

| Case | Kind | Required behaviour |
|---|---|---|
| R5-1-fast-varname | REQUIRED | Fast profile, UNVERIFIED, no-ack: exit 0 **and** `SENTINEL_RENAME_GATE_UNVERIFIED_OK` appears on the UNVERIFIED line. Exit 0 alone is not this row. |
| R5-2-deep-refuse | REQUIRED | Deep/`--gate`, UNVERIFIED, no-ack: non-zero exit. |
| R5-3-deep-ack-disclose | REQUIRED | Deep/`--gate`, UNVERIFIED, ack set: exit 0 **and** own output states D-016 was acknowledged, not verified. |
| R5-4-readable-clean | REQUIRED | When `gh` can read PRIVATE: exit 0 and the clean line. If that visibility cannot be produced, NOT_MEASURED. |
| R5-5-toplevel-gate | REQUIRED | `./scripts/test.sh --gate` on an UNVERIFIED/no-ack isolated clone: no `GATE PASSED`, non-zero exit. Script-only failure of `check-rename-gate.sh` is not this row. The run must be allowed to complete far enough to observe `GATE PASSED` if the hole is live. |

UNVERIFIED is produced by an isolated clone whose `origin` is a local
path, not a GitHub slug (D-071's own decisive fact). It is not faked by
breaking the script.

At the R5 baseline, R5-1, R5-2, R5-3, and R5-5 **must FAIL**. R5-4 is a
control path that should still PASS if visibility is readable (the clean
path was not the defect).

### V-6 and R2 (D-072) — subject: V-6 baseline SHA

Every enumeration vector, each against both consumers, with a live
control that the vector defeats the **unpinned** call:

| Case | Vector | Consumer |
|---|---|---|
| V6-COUNT-secrets | `GIT_CONFIG_COUNT` + `GIT_CONFIG_KEY_n` + `GIT_CONFIG_VALUE_n` setting `core.excludesFile` | `check-secrets.sh` default |
| V6-COUNT-vendor | same | `check-vendor-honesty.sh` `artifacts()` |
| V6-GLOBAL-secrets | `GIT_CONFIG_GLOBAL` → config setting `core.excludesFile` | secrets |
| V6-GLOBAL-vendor | same | vendor |
| V6-SYSTEM-secrets | `GIT_CONFIG_SYSTEM` → config setting `core.excludesFile` | secrets |
| V6-SYSTEM-vendor | same | vendor |
| V6-NOSYSTEM-secrets | `GIT_CONFIG_NOSYSTEM` (weaker sibling; only hides if the system file was the excluder) | secrets |
| V6-NOSYSTEM-vendor | same | vendor |
| V6-HOME-secrets | `HOME` with no `GIT_CONFIG_*`; default `$HOME/.config/git/ignore` | secrets |
| V6-HOME-vendor | same | vendor |
| V6-XDG-secrets | `XDG_CONFIG_HOME` with no `GIT_CONFIG_*`; default `$XDG_CONFIG_HOME/git/ignore` | secrets |
| V6-XDG-vendor | same | vendor |
| R2-vendor | non-ASCII filename; unquoted `ls-files --others --exclude-standard` octal-escapes; `[ -f "$f" ]` drops it | vendor `artifacts()` (the no-`-z` site) |
| R2-secrets | same, **only if** measured that `-z` still drops the path | secrets |

REQUIRED assertion on each V-6/R2 observing row: the production consumer
**sees / blocks the plant**. At the V-6 baseline the consumer misses the
plant, so those REQUIRED rows **FAIL**.

Env-var names are taken from `git help config` ENVIRONMENT and
`git help git` ENVIRONMENT on this machine, not from memory. Default
ignore path is taken from `git help gitignore`.

## CONTROLS

Written in `EXPLOIT-CONTROL.md` **before** the observing assertions.
Harness: `d071-d072-observe.sh`. A CONTROL failure or an inert vector
makes the paired REQUIRED row NOT_MEASURED.

## EXCLUSIONS

- No implementation is proposed. No production file is changed.
- No VERIFICATION.md, no SEVERITY.md, no IMPLEMENTATION.md.
- No source-text greps (`grep -c core.excludesFile`) as a substitute
  for the hole.
- Credential-shaped values are synthesised at run time and never
  committed. Logs are redacted.
- `check-v1-index-ordering.sh` is not a required hide-untracked consumer.

## STOPPING RULE

If a test PASSES at the baseline it was supposed to fail, or its control
does not fire, it is **invalid**. Do not replace it in this card. Report
the invalidity with evidence. Invalidity must be independently confirmed
before replacement — that confirmation is not this author's job.

## How to read the harness

Every scored line is `case<TAB>CONTROL|REQUIRED<TAB>PASS|FAIL|NOT_MEASURED<TAB>evidence`.

Exit status (never a substitute for reading the TSV and the logs):

- `0` every REQUIRED and every CONTROL held (not expected at these baselines)
- `1` REQUIRED failures, all counted CONTROLs held (the baseline demonstration)
- `2` a CONTROL failed, or a REQUIRED passed at a baseline where FAIL was required (invalid / untrustworthy)
- `3` usage / preflight
