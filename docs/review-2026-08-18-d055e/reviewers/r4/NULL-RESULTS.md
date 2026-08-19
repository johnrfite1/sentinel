# R4 — NULL RESULTS — what I probed and found SOUND

Commit `7e0ab7f`. These are recorded so the next round knows where not to look again.
Each states what I checked and what would have made it a finding.

---

## N1 — The round-six raw archive is intact and every preservation claim about its CONTENT is true

This is the record that round six — and therefore the exit criterion's entire backtest — rests
on, and it was explicitly de-scoped from review. I verified it end to end against the raw
archive at `<HOME>/Projects/_archive/sentinel-round-six-2026-08-18`.

| Claim (`docs/review-2026-08-18-round-six/README.md`) | Verified |
|---|---|
| `round-six-raw.tgz` sha256 `830e7222…` | **matches** |
| Raw manifest sha256 `51894dd4…` | **matches** |
| 971 files | **exactly 971** regular files under `raw/` |
| 1 symlink | **exactly 1** |
| 9,551,737 bytes | **exact** |
| "971/971 identical, 0 mismatches" | **971/971 OK** — re-verified independently |
| `ADJUDICATED-ROUND-SIX.md` byte-identical | **`cmp` identical** |
| `briefs/lens1..9.md` byte-identical | **all nine `cmp` identical** |
| `briefs/COMMON-BRIEF.md` "one line sanitized … nothing else changed" | **exactly one line differs**, and it is the disclosed `<REPO>` substitution |

```
A=<HOME>/Projects/_archive/sentinel-round-six-2026-08-18
shasum -a 256 "$A/round-six-raw.tgz"
cd "$A/raw" && shasum -a 256 -c "$A/MANIFEST-sha256.txt" | awk -F': ' '{print $NF}' | sort | uniq -c
#   971 OK
find "$A/raw" -type f | wc -l              # 971
find "$A/raw" -type l | wc -l              # 1
find "$A/raw" -type f -exec stat -f %z {} + | awk '{s+=$1} END{print s}'   # 9551737
```

**This is a strong positive result and it should be recorded as one.** The one defect I found
on this surface (R4-F2) is a disclosure omission, not an integrity failure.

## N2 — Round six's stated provenance gap is accurate, and is not understated

The README claims seven of nine reviewers left no report, that `round6/reports/` is empty, and
that only lens 1 and lens 4 left a reviewer-authored index. I checked whether the gap was
actually **worse or better** than stated — i.e. whether reviewer reports exist in the archive
that were not carried into the repository.

- `raw/round6/reports/` — **empty**, as claimed.
- Only `lens1/00-INDEX.txt` and `lens4/L4-INDEX.txt` are reviewer-authored summaries, as claimed.
- `lens8/ablation-n5.md` is the only other `.md` under any lens directory and is **generated
  tool output** (`npm --prefix ts run ablation`), not a reviewer account.
- A sweep for report/coverage/attestation/null/findings/critique-shaped filenames across all
  nine lens directories returned only probe logs whose names coincidentally contain those words.

The claim holds exactly. Nothing was preserved into the repo that misrepresents the gap, and
nothing was withheld from it.

## N3 — `assertSchemaAgreement()` really does run at import in both TypeScript EIP-712 implementations

`ts/src/evaluate/hashes.ts:56` claims *"Verified at import, so a process that starts is a
process whose schema matches the chain's."* A comment claiming import-time enforcement that is
in fact only exercised by a test would be exactly this project's defect shape.

```
grep -rn "assertSchemaAgreement" ts/ --include="*.ts" | grep -v node_modules
#   ts/src/signer/eip712.ts:364:assertSchemaAgreement();     <-- top-level call
#   ts/src/evaluate/hashes.ts:81:assertSchemaAgreement();    <-- top-level call
```

Both are unconditional module-scope calls. The claim is true. Four golden typehashes are pinned
in the evaluator and six in the signer.

## N4 — Every guard except `check-review-scope.sh` is invoked by the gate

I checked whether R1's recorded orphan is one of several. It is not.

```
for g in scripts/check-*.sh; do grep -rn "$(basename $g)" --include="*.sh" . ; done
```

`check-class-coverage` (test.sh:161), `check-eval-codes` (:153), `check-gate-immutability`
(:131), `check-label-integrity` (:147), `check-label-prompt` (:140), `check-rename-gate` (:137),
`check-secrets` (:134), `check-type-strings` (:150), `check-vendor-honesty` (:167) are all
invoked. **`check-review-scope.sh` is the only one with no invocation** — which is already
recorded this round and is not mine to re-report.

## N5 — No tracked file contains an absolute `<HOME>` path

I expected to find one, because the round-six symlink line carries one in the source archive and
because `fixtures/corpus/labels/labeller-M.provenance.json` records a past commit being refused
for exactly this. The sanitization was in fact applied everywhere.

```
git ls-files | while read -r f; do grep -qs "<HOME>" "$f" && echo "$f"; done
#   (no output)
```

## N6 — The six EIP-712 type strings agree across all four implementations that carry them

`check-type-strings.sh` only compares two of them (spec ↔ `ts/src/signer/eip712.ts`), so I
checked the rest by hand rather than trusting the guard's scope.

- spec §5.8 (lines 496–506), `ts/src/signer/eip712.ts` (all 6),
  `contracts/src/types/SentinelTypes.sol` (all 6), `ts/src/evaluate/hashes.ts` (the 4 it needs),
  `contracts/test/SentinelTypes.t.sol` (independently transcribed goldens).
- Each of the six appears exactly **once** as a published literal in the proposal, all inside
  §5.8, so the guard's whole-file grep (see R4-F3) currently lands on the right lines.

No drift found.

## N7 — Every gate count floor is exactly met, and every floor constant matches a measured suite

I expected headroom — a floor set below the real count lets a suite shrink silently up to the
gap, which is the defect the floors exist to close, half-closed. There is none. Measured at
`7e0ab7f`:

| Suite | Floor in `scripts/test.sh` | Measured | Headroom |
|---|---|---|---|
| Foundry | `FOUNDRY_MIN_TESTS=75` (:187) | **75** passed | 0 |
| TypeScript | `TS_MIN_TESTS=513` (:188) | **513** passed, 0 skipped, 0 todo | 0 |
| verifier suite | `VERIFIER_MIN_TESTS=209` (:611) | **209**, OK | 0 |
| verifier samples | `VERIFIER_MIN_SAMPLES=7` (:612) | **7/7 verified** | 0 |
| verifier tamper cases | `VERIFIER_MIN_TAMPER=78` (:613) | **78** `tamper self-test PASS` | 0 |

Every floor is a true ratchet at the current value. The `skipped`/`todo` branch that catches a
suite kept nominally large by disabled tests is present and separate from the floor, for both
Foundry and TypeScript, as its comments claim.

**This is the null that makes R4-F4 a finding rather than a rounding complaint:** the gate's
constants are right and current; it is only `docs/session-state.md` §3 that publishes the
superseded pair.

## N8 — The `G-3` mechanism is exactly as recorded — not worse

I reproduced it independently from the 50 committed corpus results rather than relaying §11.0's
verification, specifically to test whether a recorded item was worse than recorded. It is not.

Exactly **two** of 20 classes are credited only on `UNRESOLVED` outcomes at the
`L3_full_conformance` layer — `conflicting-block-state` (F048) and
`runtime-code-change-or-proxy-target` (F042, F043). That is precisely what §11.0's T1
verification states. `check-class-coverage.sh` independently reports 6 carried classes
(1 RESERVED, 4 DELEGATED, 1 GAP), consistent with the published 14 of 20.

The mechanism is sound as recorded. **What is defective is the bookkeeping around its
acceptance, not the finding itself — see R4-F1 Addendum 2.**
