# D-CLAIMS — independent first-corrected instrument review 2

## Verdict

**FAIL for instrument readiness.** Review 1's three named attacks are closed in the
spellings that review used: restoring unstruck `this alone blocks exit` fails
`R-D1-blocks`; omitting D-09 fails `R-D2-truth`; leaving the FIVE heading unstruck fails
`R-D2-five`; leaving packet `The ten §11.0` fails `R-D1-ten`; FIVE→FOUR no longer fails a
CONTROL; Review 1's exact `fix-all` then `SIGNER_CHAIN_PENDING_HEAD: "FATAL"` fails
exactly `C-D6-codes`. The first-correction still prints
`D_CLAIMS_FOCUSED_COMPLETE` for a TypeScript-legal public reason-code split the CARD
claims `C-D6-codes` freezes, and for D-F1 / D-F2 / packet-ten claims that remain
human-readable after an interior or split `~~…~~` span. Those are live holes in the
correction, not surviving Review-1 rows.

This is an instrument-readiness verdict only. It is not an implementation verdict, gate
approval or signature, certification, ratification, publication, rename, D-055 assessment
or push authorization. I did not edit CARD.md, `d-claims.py`, production files,
`INSTRUMENT-REVIEW-1.md` or signed packs.

## 1. Exact subject, scope and preservation

I reviewed exact subject `c9a19e44af37d1d3f0ccb5302b6313239ccd6508`, tree
`a31f73beb5979bda206854cd93bf9c9cde88c274`, message `D-CLAIMS: record first-correction
demonstration`. Its sole parent is the harness/CARD correction
`7ffed58a9e8d5b1ec03702fb758e1ceadb94b574`. That correction's parent is Review 1 FAIL
`32718410859183c475c83cab78fbf7f9963e4855`. Behavioral baseline for pre-repair oracles is
A-094 `1e7761be051422ad8091b203df375ddcfb7d1208`. HEAD was exactly the subject. Tracked
`README.md` was dirty and `assets/` / `.serena/` were untracked in the live worktree; I
did not touch, stage or commit any of them. Every focused run used a byte-identical
`/tmp` copy of `d-claims.py` against a disposable `git clone --local --no-hardlinks` of a
clean source. Attack harnesses stayed in `/tmp`. Author `RESULTS.md` was not used as
evidence.

Parent `7ffed58` → subject is exactly `RESULTS.md` (14 insertions, 11 deletions).
`7ffed58` vs Review 1 `3271841` is CARD.md, RUNBOOK.md and `d-claims.py` only (149
insertions, 35 deletions). Baseline `1e7761b` → HEAD adds only this `D-CLAIMS-tests/`
directory (five paths before this review). No production byte, existing product test,
`scripts/test.sh`, `scripts/check-*.sh`, maintained claim, decision record, signed pack
or prior review moves. The five declared surfaces are blob-identical at `1e7761b` and
HEAD. `git diff --check` on the subject is clean. `scripts/test.sh` does not mention
`d-claims`. No `check-claims.sh` / `check-prose.sh` exists.

`INSTRUMENT-REVIEW-1.md` is byte-identical at sha256
`fd48278dc9946342868e73b6e4ca8ad596ae0f34237618d0359ac0047e5cab35` (git blob
`14fff621d454d4b32f25a572822eb535a53faafe`). I did not edit it.

| Object | Git blob | sha256 |
|---|---|---|
| `d-claims.py` (430 lines) | `32865abe4b7d89875ae50eb0e7b53f2f4e3cc3f2` | `f53121e4c9ab4bc68b536df010d4637cc36d8e702b36be70582317afce8027ed` |
| `CARD.md` | `7362dfa56eea7e2cfbfcdad210a45705828b92c4` | `b2df9cb781cb2803539e001df2be6cf9e476e9875a2ddb2c74d055c0832ab6f4` |
| `docs/gate-s1-evidence.md` | `66f7b843888cf1eca7d719d0f23c6120969fae30` | `25dcefcade99e9e45be0c482f3dc5141f4d25335a920fabe1012303c7d7caf68` |
| S2 prefix before `## 11. What is NOT in evidence` | — | `470ec1de8ee696a2875334a7873e8e02504ea27d10676cb1a0018668097ba02f` |
| `docs/gate-s2-evidence.md` (whole file) | `baab3e7809a46f22131ef2b609f30af1ed8eeada` | `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589` |
| `scripts/check-suite-floors.sh` | `f8df5ab4db9023b319d872249e10140b635dc152` | `95b65a02bdfc8436e4739b7e5ef90b803964236a86173ed5b8f3c6cc139f7a46` |
| B-EVENTS `SentinelVault.events.t.sol` | `b601b0ad949a6c64b5ab53232fc00a9784e123a0` | `2a9219cc5138858b012b0bc56069490db3dd7d1963b73ccc19c28a48ce2b029e` |
| C-SNAPSHOT `vault.snapshot.classification.test.ts` | `6a00cb9d674a5fe89c0e999149add7e25f7100de` | `29a673560e89b639b6635661706a368454c9969a04c5d37c4f6c15229df3dd8a` |

Harness sha256 was hashed from the file bytes, not taken from RESULTS.md. It matches the
author's claimed digest. Independent `git show` at HEAD and at `1e7761b` gives the same
four frozen hashes the CARD lists. `FROZEN_REASON_CODES` is 35 unique keys. Live floors
at this subject remain `103/550/221/7/78/30`. §11.0 begins after the S2 prefix mark.

I read the workspace rules, D-058(8)D / D-059(5)–(6) / D-060(1), Review 1, the complete
CARD/RUNBOOK/harness, and the five declared surfaces at the baseline. I authored neither
this instrument nor a production repair.

## 2. Independent nine-variant reproduction

Dirty live worktree refused (exit 2, `source worktree has tracked changes`). Uppercase and
39-hex subjects refused (`exact lowercase 40-hex`). Unknown `D_CLAIMS_VARIANT` refused.
Untracked-only source (canary file, porcelain `--untracked-files=no` empty) ran. Tracked
dirt in that clone refused.

Against behavioral baseline `1e7761b`, and again against subject `c9a19e4` for
`baseline` / `fix-all` (production bytes identical; matrices identical):

| Variant | Exit | REQUIRED | CONTROL | Completion | Matrix sha256 |
|---|---:|---:|---:|---|---|
| `baseline` (`1e7761b`) | 1 | 0/14 | 26/26 | withheld | `5b6274ad5b46cc9c9efd1c2a8cccdb7d09ee30d9b0993b0e192bec6ad9f89ea9` |
| `baseline` (`c9a19e4`) | 1 | 0/14 | 26/26 | withheld | `5b6274ad5b46cc9c9efd1c2a8cccdb7d09ee30d9b0993b0e192bec6ad9f89ea9` |
| `fix-d6` | 1 | 2/14 | 26/26 | withheld | `e0ef9e2ec25aa18ee7af8961e89ecc43f06c37b15c09e34bfdac91f8c9cf19ed` |
| `fix-all` | 0 | 14/14 | 26/26 | `D_CLAIMS_FOCUSED_COMPLETE` | `398d912a3d90ca4115f006619a771c446113d8a8e4e8804383bce599d9749148` |
| `break-s1` | 1 | 0/14 | 25/26 | withheld | `cb624e18226b316ee8a94f51512767505b2390ce1468936e1891aeb5cc3e42f3` |
| `break-s2-prefix` | 1 | 0/14 | 25/26 | withheld | `c69f6d518f0701835bfee4ca702bf6a09f33504c73820ac1021a983bcfca97ef` |
| `break-floors` | 1 | 0/14 | 25/26 | withheld | `91acb7d669138889df2775ec349b78e93132ea36d48f3c45ad25cefa15a34dc9` |
| `break-bevents` | 1 | 0/14 | 25/26 | withheld | `28303e65d054f52b4fab5c26e8e184a06f1513996770e787a7c0c00fd90e1f76` |
| `break-d014` | 1 | 0/14 | 25/26 | withheld | `03719d56e320a865d810a86e3bba13300a64f75d1e9ec92ccf092d69fce65996` |
| `break-reason-split` | 1 | 0/14 | 25/26 | withheld | `baf3451214e957e07b27a4c5e69eeb83f20f0f6cc01fcfcba648c55d049deb95` |

`fix-d6` PASSes only `R-D6-absent` and `R-D6-truth`. Each `break-*` fails exactly the named
CONTROL (`C-D1-s1`, `C-D2-prefix`, `C-floors`, `C-B-EVENTS`, `C-D4b-d014`, `C-D6-codes`)
with REQUIRED still 0/14. Baseline FAILs all 14 REQUIRED. Those counters are from the
reproduced matrices, not from `RESULTS.md`. Clone HEAD matched the requested 40-hex on
every successful run.

## 3. Defects

### 3.1 FAIL — `C-D6-codes` does not freeze `REASON_SEVERITY` keys (Review 1 F1-3 remains)

CARD §5 claims the CONTROL holds the public `REASON_SEVERITY` key set at the frozen 35
codes. `break-reason-split` inserts the unquoted immediate-colon form Review 1 used and
fails exactly `C-D6-codes`. The scored tokeniser is not the key set:

```text
(?m)^\s+([A-Z][A-Z0-9_]+):
```

It keeps only unquoted names with the colon immediately after the identifier. TypeScript
allows whitespace and comments between a name and `:`, and quoted keys. `ReasonCode` is
`keyof typeof REASON_SEVERITY`. Those forms are public codes.

Measured `/tmp` siblings against the same clean `1e7761b` clone, each after harness
`apply_all` (14/14 REQUIRED already held):

| Sibling | REQUIRED | CONTROL | Completion | `C-D6-codes` |
|---|---:|---:|---|---|
| Review 1 exact: `SIGNER_CHAIN_PENDING_HEAD: "FATAL"` | 14/14 | 25/26 | withheld | FAIL |
| `"SIGNER_CHAIN_PENDING_HEAD": "FATAL"` | 14/14 | 26/26 | `COMPLETE` | PASS |
| `SIGNER_CHAIN_PENDING_HEAD : "FATAL"` (space before `:`) | 14/14 | 26/26 | `COMPLETE` | PASS |
| `SIGNER_CHAIN_PENDING_HEAD /*split*/: "FATAL"` | 14/14 | 26/26 | `COMPLETE` | PASS |
| name, newline, then `:` | 14/14 | 26/26 | `COMPLETE` | PASS |
| unquoted key, single-quoted `'FATAL'` value | 14/14 | 25/26 | withheld | FAIL |

On the quoted-key sibling the scored set is still the frozen 35 and does not contain
`SIGNER_CHAIN_PENDING_HEAD`, while the `REASON_SEVERITY` body contains
`"SIGNER_CHAIN_PENDING_HEAD"` as a 36th key. Space-before-colon is the same: scored
length 35, raw line present. A repairer can ship the forbidden D-F6 product change,
copy the frozen truth phrases, and receive the completion token. Review 1's exact
spelling is now a committed variant. The defect class is not closed.

`/usr/bin/grep` on the clean clone finds `SIGNER_CHAIN_PENDING_HEAD` only in this card
directory (CARD, RESULTS, harness `break-reason-split`, Review 1). Production
`protocol.ts` does not contain it until an attack inserts it.

### 3.2 FAIL — `live_text` unstruck oracles PASS while the watched claim stays readable

CARD §0 / §5 say unstruck oracles delete `~~…~~` spans from wrap-normalized text, then
search. `R-D1-blocks`, `R-D2-five` and `R-D1-ten` are contiguous substring absence after
that delete. A `~~…~~` span that splits the watched phrase, or that strikes one interior
letter, makes the contiguous string absent while the live false claim remains
human-readable. `fix-all` then that one edit greets COMPLETE.

Measured after harness `apply_all` on the same clean `1e7761b` clone:

| Sibling | Live remainder | REQUIRED | CONTROL | Completion |
|---|---|---:|---:|---|
| restore `this alone blocks exit` fully unstruck | phrase present in blocker live | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| `this alone blocks exi~~t~~.` | `this alone blocks exi .` | 14/14 | 26/26 | `COMPLETE` |
| `~~this alone ~~blocks exit.` | `blocks exit` remains | 14/14 | 26/26 | `COMPLETE` |
| `~~~~…blocks exit.~~~~` (extra tildes) | phrase still in live_text | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| `<del>…blocks exit.</del>` | phrase still in live_text | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| `FI~~V~~E OF THESE TEN…` instead of wrapping the heading | `FIE OF THESE TEN` in live | 14/14 | 26/26 | `COMPLETE` |
| packet `The t~~e~~n §11.0` plus a live six | `The t n §11.0` in live | 14/14 | 26/26 | `COMPLETE` |

Review 1 F1-1's exact restore is closed. The new unstruck mechanism is not: D-F1's
load-bearing BLOCKER sentence, D-F2's FIVE heading, and packet “ten” can all remain
current readable claims behind a one-letter or split strike and still print the
completion token. Extra tildes, HTML `<del>`, single tildes and an unclosed `~~` are
fail-closed (phrase stays in `live_text`, REQUIRED FAILs). Those outside-grammar marks
do not cancel the hole inside the claimed `~~…~~` grammar.

## 4. Attacks that did not fail the instrument

These were run. They are not grounds for this FAIL, and they do not cancel §3.

- **Review 1 F1-1 exact.** `fix-all` wrap-norm of BLOCKER 1 still contains struck
  `this alone blocks exit`; `live_text` does not. Restoring only that sentence unstruck
  is 13/14 REQUIRED, exactly `R-D1-blocks`. Independent wrap-aware CARD-phrase repair
  (strike `; it does not.`, insert `D1_TRUTH`, strike the blocks-exit sentence, no
  harness `D1_NEW` surrounding prose) is 14/14 and 26/26.
- **Review 1 F1-2 exact.** Independent CARD repair that writes only
  `Ten minus four wholly-removed entries is six, not five.` and omits D-09 is 13/14,
  exactly `R-D2-truth`. Leaving the FIVE heading unstruck is 13/14, exactly `R-D2-five`.
  Leaving packet `The ten §11.0 accepted limits` (and therefore not writing six) is
  12/14, `R-D1-ten` and `R-D1-six`. FIVE→FOUR on the heading, with full `D2_TRUTH` and
  the other CARD phrases, is 14/14 and 26/26: the truthful wholly-removed count no
  longer fails a CONTROL. `C-D2-struck` and `C-D2-packet-ten` are gone. Dated
  session-state `ten accepted as documented limits` remains `C-session-ten`.
- **BLOCKER 1 still under the BLOCKERS heading.** After `fix-all` and after the
  independent CARD-complete sibling, item 1 remains under `**BLOCKERS — exit cannot be
  reached while these stand:**` while its body says it is not a current exit blocker.
  CARD §1 / `D1_NEW` keep that item as the scored BLOCKER 1 region and require the
  disclaimer plus the struck blocks-exit sentence, not relocation to NON-BLOCKERS. I do
  not add list membership as a numbered defect.
- **Sibling object / union widen.** `EXTRA_REASON = { SIGNER_CHAIN_PENDING_HEAD: … }`
  beside `REASON_SEVERITY`, and `| "SIGNER_CHAIN_PENDING_HEAD"` on the `ReasonCode`
  alias, both COMPLETE. CARD freezes `REASON_SEVERITY` keys, not every identifier in
  the file. Those are outside that freeze. §3.1 is the freeze not actually covering
  keys *in* that object.
- **D1 strike false-positive.** `; it does not.` is not a substring of
  `; ~~it does not.~~` after wrap-norm or after `live_text`.
- **D2 wrap.** Live sentence is `Ten minus the five` / `fixed leaves six` across a
  newline. Joined phrase is absent from raw file bytes and present after wrap-norm.
  Baseline `R-D2-absent` FAILs, so the scored check is wrap-norm, not a line grep.
- **comment-star wrap.** `Both are open (v1.1 register)` is absent from raw wrap-norm of
  `decode/index.ts` and present after `^\s*\*` strip. `NEITHER the signer nor the verifier`
  is present in both. After `fix-all`, both `D4B_TRUTH` fragments are absent from
  wrap-only and present after strip. Baseline `R-D4b-open` FAIL proves the strip is
  load-bearing, not fake.
- **Signed-pack leak.** `fix-all` leaves S1 sha256 `25dcefcade…` and the prefix hash
  `470ec1de8e…`. Appending a byte to S1 after `fix-all` fails exactly `C-D1-s1`.
  Prefix whitespace before `## 11. What is NOT in evidence` fails exactly `C-D2-prefix`.
- **Historical quotes.** After `fix-all`, ADJ2 still contains `Both are open (v1.1
  register)` and v3 still contains `so the refusal detail now distinguishes them`.
  Erasing those quotes after `fix-all` fails exactly `C-hist-adj2` / `C-hist-v3`.
- **Second checker / gate wiring.** Planting `scripts/check-claims.sh` or
  `scripts/check-prose.sh` after `fix-all` fails exactly `C-no-second-checker`.
  Appending `d-claims` to `test.sh` fails exactly `C-no-gate-wire`.
- **`RefusalRecord.detail`.** Adding `detail?: string` to the `RefusalRecord` body after
  `fix-all` fails exactly `C-D6-no-detail`.
- **Paraphrase without frozen truth strings.** Wrap-aware strikes of the false phrases
  plus non-frozen replacements scored 10/14 REQUIRED and 26/26 CONTROL (exactly the
  four `*-truth` rows: `R-D6-truth`, `R-D4b-truth`, `R-D1-truth`, `R-D2-truth`).
- **Preflight / identity / completion.** Exact 40-hex, clone HEAD match, dirty source
  refused, completion withheld on baseline 0/14.

D-F3 as Batch A / D-F5 as no second checker match D-059(5). No gate harness is present,
so D-059(7) is N/A as claimed.

## 5. What I did not run

I did not launch Foundry, the TypeScript suite, the verifier, `scripts/test.sh` as a
gate, `a-floors-gate.py`, or `scripts/check-suite-floors.sh` as a process. Floor
constants were read from `scripts/test.sh` at the subject (`FOUNDRY_MIN_TESTS=103`,
`TS_MIN_TESTS=550`) and `C-floors` PASSed in every non-`break-floors` variant. Attack
harnesses, clones and matrices stayed in `/tmp`. `/usr/bin/grep` tree sweeps were on the
clean clone, not the dirty live worktree.

## 6. Limits

This review establishes that the nine committed variants discriminate as labelled, that
Review 1's three exact attacks are closed in those spellings, that wrap-norm and
comment-star stripping remain the scored Markdown/TypeScript checks, and that two
instrument defects remain: a `REASON_SEVERITY` freeze that does not observe
TypeScript-legal keys, and unstruck oracles that treat an interior or split `~~…~~` span
as removal of a still-readable live claim. It does not establish general prose
consistency, implementation correctness, a gate outcome, historical factual truth,
certification, signing, publication or D-055 closure.

**FAIL.** Do not hold this instrument. Do not start a product repair against it.
