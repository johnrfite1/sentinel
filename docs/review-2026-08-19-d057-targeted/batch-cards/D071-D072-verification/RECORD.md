# D-071 / D-072 verification card — record

Index only. This file does not score D-055. It does not lift D-067.
It does not sign, reopen, or annotate a gate. D-016 stands.

John commissioned this card 2026-08-23: independent tests against the
repair parents, a different agent to verify the freeze, a different
agent to assign severity for R5 and V-6. Three roles. No production
change.

## Freeze

This commit is the card freeze. Paths and the commits that introduced
them (measured with `git log -4 --format='%H %s'` and
`git rev-parse <commit>^{commit}` at freeze):

| Path | Introduced at |
|---|---|
| `CARD.md` `EXPLOIT-CONTROL.md` `COVERAGE.md` `BASELINE-RESULTS.md` `d071-d072-observe.sh` `logs/` (baseline) | `bdacace71e47c55301100d27341e67fc422fbcde` |
| `VERIFICATION.md` `logs/verifier/` | `f4d124323f0f5a0c62e585e48febcee191de7477` |
| `SEVERITY.md` | `6e6e2220bdd2a95d4f3f112019a120b363761a90` |
| `RECORD.md` | this freeze |

Repairs this card observes (not part of the card; already on the branch):

| Repair | SHA | Parent (baseline) |
|---|---|---|
| D-071 / R5 | `1ae684cec83c7bfdb24a8c18ffdeba87c535874f` | `558d001546b55bd80156bc875cf080fef0e301eb` |
| D-072 / V-6+R2 | `4ad6036d81fa66a35a0c3efb4eab117438e3ca38` | `1ae684cec83c7bfdb24a8c18ffdeba87c535874f` |

A-102 (pre-card HEAD): `d688caa8a15244cb4527ba7eb378c46c9687e56b`.

## Roles

1. **Test author** — contract and FAIL-at-parent demonstration:
   `bdacace71e47c55301100d27341e67fc422fbcde`. See `BASELINE-RESULTS.md`.
2. **Verifier** — scores HEAD against that contract:
   `f4d124323f0f5a0c62e585e48febcee191de7477`. See `VERIFICATION.md`.
3. **Reviewer** — severity of the pre-repair defects:
   `6e6e2220bdd2a95d4f3f112019a120b363761a90`. See `SEVERITY.md`.

None of those three wrote the production repairs.

## What the other two documents already say

- Verifier verdict: **HOLD**. Quoted from `VERIFICATION.md`, not restated
  here.
- Reviewer: R5 **High**, V-6 **High**, R2 **Medium**. Quoted from
  `SEVERITY.md`, not restated here.

## What this freeze does not do

- No D-055 verdict, recommendation, or condition flip.
- D-067 is not rewritten. R2 and V-6 stay named completeness limits
  on D-008(2)/(4) until John rules.
- No gate signed, reopened, or annotated. No public-claim
  certification. No push, publication, or rename.
- No frozen A1 harness rewritten. No A1 reopening.
- Five D-008 comprehension questions unseen.
- No follow-on plan.

## Working tree at freeze (not in this commit)

```
 M README.md
?? .serena/
?? assets/
```

Stash empty. Those paths were present at A-102 and were not discarded.

## Redaction (session four)

John ruled that this card's committed vendor plants broke
`scripts/check-vendor-honesty.sh` at the freeze above, so condition 2
did not hold there. This commit redacts those literals to named tokens
and synthesises vendor plants at run time in `d071-d072-observe.sh`,
the same discipline the card already used for credentials.

- No production change. No guard change. No exclusion list.
- HOLD, R5 High, V-6 High, R2 Medium, and upgrade/downgrade conditions
  are unchanged. Disclosures sit in VERIFICATION.md and SEVERITY.md.
- Frozen harness sha256 at the verification freeze (measured then, still
  the pin in VERIFICATION.md):
  `e24443d1fc365e09a691650e8a69bd68a7b4768fde92f2c7da816e3b7e35d12e`.
  After this redaction the harness hash moved. Measured at this commit:
  `284d8974331fecddc505e88037201e6d572410a5f83d5e65dfad1209ae8b143e`
  (`d071-d072-observe.sh`). The verifier's pin is not overwritten.
- D-055 is not ruled. D-067 is not lifted. No gate is signed.
