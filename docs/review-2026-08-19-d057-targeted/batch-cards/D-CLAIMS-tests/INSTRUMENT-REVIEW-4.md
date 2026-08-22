# D-CLAIMS — independent third-corrected instrument review 4

## Verdict

**HOLD for instrument readiness.** Review 3's two named attacks are closed in the
spellings that review used and in the broader class those spellings stood for: after
`fix-all`, unquoted `SIGNER_CHAIN_PENDING_HEAD` with VT, FF, NBSP, LS, PS or BOM
before `:` fails exactly `C-D6-codes` (14/14 REQUIRED, 25/26 CONTROL, completion
withheld, scored set length 36 and contains the inserted key). The same holds for
every Unicode Zs Python reports, including Ogham U+1680, em space U+2003 and
ideographic U+3000. After `fix-all`, `~~~…~~` and `~~…~~~` around the watched ASCII
D-F1 sentence fail exactly `R-D1-blocks` (13/14). Committed
`break-extra-tilde-open` / `break-extra-tilde-close` discriminate as labelled.
`fix-all` itself stays 14/14 COMPLETE. Review 2 interior/split `exi~~t~~` /
`FI~~V~~E` / `The t~~e~~n` via `break-live-strike` is still 11/14 on exactly
`R-D1-blocks`, `R-D1-ten`, `R-D2-five`. I could not make a TypeScript-legal public
`REASON_SEVERITY` key the CARD's finite grammar claims to freeze print
`D_CLAIMS_FOCUSED_COMPLETE`, and I could not make extra tildes wrapping that D-F1
sentence look fully struck.

This is an instrument-readiness verdict only. It is not an implementation verdict,
gate approval or signature, certification, ratification, publication, rename, D-055
assessment or push authorization. I did not edit CARD.md, `d-claims.py`, production
files, `INSTRUMENT-REVIEW-1.md`, `INSTRUMENT-REVIEW-2.md`,
`INSTRUMENT-REVIEW-3.md` or signed packs.

## 1. Exact subject, scope and preservation

I reviewed exact subject `618057091e5c4eea3c5ddb30ac6f7cc9c51953a3`, tree
`5ca1c8f971bfd997a1a3065a94bbd9b24c20b6ef`, message `D-CLAIMS: close Review 3 instrument
defects`. Its sole parent is Review 3 FAIL
`0f5ba80fa6fa64317a2d0f28769a7fde6eb88558`. Behavioral baseline for pre-repair oracles is
A-094 `1e7761be051422ad8091b203df375ddcfb7d1208`. HEAD was exactly the subject. Tracked
`README.md` was dirty and `assets/` / `.serena/` were untracked in the live worktree; I
did not touch, stage or commit any of them. Every focused run used a byte-identical
`/tmp` copy of `d-claims.py` against a disposable `git clone --local --no-hardlinks` of a
clean source. Attack harnesses stayed in `/tmp`. Author `RESULTS.md` was not used as
evidence.

Parent `0f5ba80` → subject is CARD.md, RUNBOOK.md, RESULTS.md and `d-claims.py` only
(143 insertions, 26 deletions). Baseline `1e7761b` → HEAD adds only this
`D-CLAIMS-tests/` directory (seven paths before this review). No production byte,
existing product test, `scripts/test.sh`, `scripts/check-*.sh`, maintained claim,
decision record, signed pack or prior review moves. The five declared surfaces are
blob-identical at `1e7761b` and HEAD. `git diff --check` on the subject is clean.
`scripts/test.sh` does not mention `d-claims`. No `check-claims.sh` / `check-prose.sh`
exists.

`INSTRUMENT-REVIEW-1.md` is byte-identical at sha256
`fd48278dc9946342868e73b6e4ca8ad596ae0f34237618d0359ac0047e5cab35` (git blob
`14fff621d454d4b32f25a572822eb535a53faafe`). `INSTRUMENT-REVIEW-2.md` is byte-identical
at sha256 `766cfc1f338ff769f2e9f5d561285d09e5616bd0d6f7117e66478863629b0aa6` (git blob
`b28dbf8588a8e2209aa55422b3fb7207ff872b75`). `INSTRUMENT-REVIEW-3.md` is byte-identical
at sha256 `742b5eba31f2a1cb2c043629566a69cee0b73556da16daebe3e80019b0a8ef98` (git blob
`37670166d907db3543d360fbb6486a391d3f2cdd`). I did not edit any of them.

| Object | Git blob | sha256 |
|---|---|---|
| `d-claims.py` (665 lines) | `56895a70638503a9974cce92bf153c9cce3684c9` | `9ec0307c3743a34a73b522e4ede0a31b3c50dee438269c1e2ec3827d9f4f741a` |
| `CARD.md` | `236cb2625afcc8d7252e82fcb5d7d6779aef32b1` | `86ad309a2c912ab01580a9e6268d60d4d3bc5a074f8367d98a658a8c795d52e6` |
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

I read the workspace rules, D-058(8)D / D-059(5)–(6) / D-060(1), Reviews 1–3, the
complete CARD/RUNBOOK/harness, and the five declared surfaces at the baseline. I authored
neither this instrument nor a production repair.

## 2. Independent twenty-two-variant reproduction

Dirty live worktree refused (exit 2, `source worktree has tracked changes`). Uppercase and
39-hex subjects refused (`exact lowercase 40-hex`, exit 2). Unknown `D_CLAIMS_VARIANT`
refused (exit 2). Untracked-only source (canary file, porcelain `--untracked-files=no`
empty) ran. Tracked dirt in that clone refused.

Against behavioral baseline `1e7761b`, and again against subject `6180570` for
`baseline` / `fix-all` (production bytes identical; matrices identical):

| Variant | Exit | REQUIRED | CONTROL | Completion | Matrix sha256 |
|---|---:|---:|---:|---|---|
| `baseline` (`1e7761b`) | 1 | 0/14 | 26/26 | withheld | `d62568ff732e532eba2fb81a2d8a562f5fa1b1870b9a37280561b9c947d3ee99` |
| `baseline` (`6180570`) | 1 | 0/14 | 26/26 | withheld | `d62568ff732e532eba2fb81a2d8a562f5fa1b1870b9a37280561b9c947d3ee99` |
| `fix-d6` | 1 | 2/14 | 26/26 | withheld | `debbcb9334cf06877a20d476c50cb90ec719470e0194bd4a11537b79fb8f7d14` |
| `fix-all` (`1e7761b`) | 0 | 14/14 | 26/26 | `D_CLAIMS_FOCUSED_COMPLETE` | `28c30a8dcf97f4c440e4e1bbe2de2fd0ec67776eec67f7de62af146cd5dc4cb6` |
| `fix-all` (`6180570`) | 0 | 14/14 | 26/26 | `D_CLAIMS_FOCUSED_COMPLETE` | `28c30a8dcf97f4c440e4e1bbe2de2fd0ec67776eec67f7de62af146cd5dc4cb6` |
| `break-s1` | 1 | 0/14 | 25/26 | withheld | `5c1cd452a29a4cd35e96b2e9818b3b7d99f5e260158cb3a2d75668af1f9cab86` |
| `break-s2-prefix` | 1 | 0/14 | 25/26 | withheld | `2e8a842bd8e472287ae6bd8b51a4c90722ef19e1a6023d1187c3ff3e7b300ca0` |
| `break-floors` | 1 | 0/14 | 25/26 | withheld | `ec8db925c59d8296e5130ef49a21742fe41e94908bd8bf189469fe7151c0320a` |
| `break-bevents` | 1 | 0/14 | 25/26 | withheld | `7eee618d03ad76160a591faf1917dc60c0900e04e7873ed0f2be36fe4654f529` |
| `break-d014` | 1 | 0/14 | 25/26 | withheld | `577de1402ac1d85287d1b9f2052625510d8726d9e7f680d18ee31b09e4099039` |
| `break-reason-split` | 1 | 0/14 | 25/26 | withheld | `285170101a3428c4de92c9d6d348f882da4c6ded082a8e054599789528c66c1c` |
| `break-reason-quoted` | 1 | 0/14 | 25/26 | withheld | `285170101a3428c4de92c9d6d348f882da4c6ded082a8e054599789528c66c1c` |
| `break-reason-space` | 1 | 0/14 | 25/26 | withheld | `285170101a3428c4de92c9d6d348f882da4c6ded082a8e054599789528c66c1c` |
| `break-reason-comment` | 1 | 0/14 | 25/26 | withheld | `285170101a3428c4de92c9d6d348f882da4c6ded082a8e054599789528c66c1c` |
| `break-reason-newline` | 1 | 0/14 | 25/26 | withheld | `285170101a3428c4de92c9d6d348f882da4c6ded082a8e054599789528c66c1c` |
| `break-reason-vt` | 1 | 0/14 | 25/26 | withheld | `285170101a3428c4de92c9d6d348f882da4c6ded082a8e054599789528c66c1c` |
| `break-reason-ff` | 1 | 0/14 | 25/26 | withheld | `285170101a3428c4de92c9d6d348f882da4c6ded082a8e054599789528c66c1c` |
| `break-reason-nbsp` | 1 | 0/14 | 25/26 | withheld | `285170101a3428c4de92c9d6d348f882da4c6ded082a8e054599789528c66c1c` |
| `break-reason-ls` | 1 | 0/14 | 25/26 | withheld | `285170101a3428c4de92c9d6d348f882da4c6ded082a8e054599789528c66c1c` |
| `break-reason-ps` | 1 | 0/14 | 25/26 | withheld | `285170101a3428c4de92c9d6d348f882da4c6ded082a8e054599789528c66c1c` |
| `break-reason-bom` | 1 | 0/14 | 25/26 | withheld | `285170101a3428c4de92c9d6d348f882da4c6ded082a8e054599789528c66c1c` |
| `break-live-strike` | 1 | 11/14 | 26/26 | withheld | `dad3fa42bb5acdc3bf1b01ed2fe1b4744f5fd959a72e820114e56daa3c683aad` |
| `break-extra-tilde-open` | 1 | 13/14 | 26/26 | withheld | `a91226ca09bcfe50923884c344d074e88f2397e882f024f50cd5f02449d7eb41` |
| `break-extra-tilde-close` | 1 | 13/14 | 26/26 | withheld | `a91226ca09bcfe50923884c344d074e88f2397e882f024f50cd5f02449d7eb41` |

`fix-d6` PASSes only `R-D6-absent` and `R-D6-truth`. Each `break-s1` / `break-s2-prefix` /
`break-floors` / `break-bevents` / `break-d014` / `break-reason-*` fails exactly the named
CONTROL (`C-D1-s1`, `C-D2-prefix`, `C-floors`, `C-B-EVENTS`, `C-D4b-d014`, `C-D6-codes`)
with REQUIRED still 0/14 except `break-live-strike` and the two extra-tilde variants.
`break-live-strike` fails exactly `R-D1-blocks`, `R-D2-five`, `R-D1-ten`.
`break-extra-tilde-open` and `break-extra-tilde-close` fail exactly `R-D1-blocks`.
Baseline FAILs all 14 REQUIRED. Those counters are from the reproduced matrices, not from
`RESULTS.md`. Clone HEAD matched the requested 40-hex on every successful run. The
`break-reason-*` matrices are byte-identical to each other because they fail the same 15
rows; the matrix does not name which spelling was inserted. The two extra-tilde matrices
are likewise byte-identical to each other.

## 3. Review 3 named defects

### 3.1 F3-1 closed — claimed whitespace now observes ECMAScript WhiteSpace / LineTerminator and other Zs

CARD §0 / §5 / `reason_object_keys` claim a finite key grammar: unquoted IDENT,
`"IDENT"` / `'IDENT'`, or that IDENT in brackets; **ECMAScript WhiteSpace plus
LineTerminator** (including VT, FF, NBSP, BOM, LS, PS, and other Unicode Zs) and `//`
or `/* */` may sit between the key and `:`; scored IDENT is `[A-Z][A-Z0-9_]*`. Review 3
measured VT / FF / NBSP / LS / PS / BOM after `fix-all` as 14/14 REQUIRED, 26/26
CONTROL, `COMPLETE`, scored set still 35. Those six committed variants now fail
exactly `C-D6-codes` on the unrepaired tree (0/14 REQUIRED, 25/26 CONTROL). `/tmp`
siblings against the same clean `1e7761b` clone, each after harness `apply_all` (14/14
REQUIRED already held):

| Sibling | REQUIRED | CONTROL | Completion | `C-D6-codes` | scored |
|---|---:|---:|---|---|---:|
| Review 3 `SIGNER_CHAIN_PENDING_HEAD\v: "FATAL"` (VT) | 14/14 | 25/26 | withheld | FAIL | 36 |
| Review 3 FF / NBSP / LS / PS / BOM before `:` | 14/14 | 25/26 | withheld | FAIL | 36 |
| Ogham U+1680 / em space U+2003 / ideographic U+3000 | 14/14 | 25/26 | withheld | FAIL | 36 |
| Remaining Zs (U+2000..U+2002, U+2004..U+2006, U+2008, U+2009, U+202F, U+205F) | 14/14 | 25/26 | withheld | FAIL | 36 |
| Mix em space + Ogham + ideographic | 14/14 | 25/26 | withheld | FAIL | 36 |
| Quoted key + Ogham; `[ em "IDENT" em ] em :`; `/*x*/` + em space; `//` ended by LS; CRLF; tab; empty `/**/` | 14/14 | 25/26 | withheld | FAIL | 36 |

On the VT sibling the scored set is 36 and contains `SIGNER_CHAIN_PENDING_HEAD`. Node
`eval` of `({ SIGNER_CHAIN_UNSTABLE: "FATAL", SIGNER_CHAIN_PENDING_HEAD` + ch +
`: "FATAL" })` returns an own-property `SIGNER_CHAIN_PENDING_HEAD` for VT, FF, NBSP,
LS, PS, BOM, every measured Zs, the mix, quoted+Ogham, and `//` ended by LS. NEL
U+0085, ZWSP U+200B and Mongolian vowel separator U+180E are SyntaxError in Node;
those siblings COMPLETE with scored set 35, which is not a TypeScript-legal key.

`/usr/bin/grep` on the clean clone finds `SIGNER_CHAIN_PENDING_HEAD` only in this card
directory (CARD, harness `break-reason-*`, Reviews 1–3). Production `protocol.ts` does
not contain it until an attack inserts it.

### 3.2 F3-2 closed — extra tildes `~~~` stay fail-closed; isolated `~~` is the toggle

CARD §0 says only an isolated `~~` pair (not part of `~~~`) toggles strike, so extra
tildes leave the phrase live or the span unclosed. A path `~` elsewhere is not
extra-tilde fail-closed. An unclosed span does not resurrect a prior closed span.
Review 3 measured `~~~…~~` / `~~…~~~` after `fix-all` as 14/14 COMPLETE. Those two
committed variants now fail exactly `R-D1-blocks` (13/14). `/tmp` siblings after
`apply_all`:

| Sibling (after `fix-all`) | REQUIRED | CONTROL | Completion |
|---|---:|---:|---|
| Review 3 `~~~Under C1 condition 4 this alone blocks exit.~~` | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| Review 3 `~~Under C1 condition 4 this alone blocks exit.~~~` | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| `~~~~…blocks exit.~~~~` (four-tilde wrap) | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| `~~~~~…~~` (five-tilde open) | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| leftover `~` glued to an isolated wrap (`~`+`~~…~~` or `~~…~~`+`~`) | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| nested isolated pairs that unstrike the phrase | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| `~~ ~~phrase~~ ~~` (spaced double wrap) | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| unclosed `~~…exit.` | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| `<del>…exit.</del>` | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| restore the sentence fully unstruck | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| interior `exi~~t~~` / split `~~this alone ~~blocks exit` | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| isolated letterwise / wordwise wraps (spaces in the phrase stay unstruck) | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| `~~~` not adjacent (`~~~ note. ~~…~~`) | 14/14 | 26/26 | `COMPLETE` |
| leftover `~` with a space, not glued | 14/14 | 26/26 | `COMPLETE` |
| unclosed `~~` after a prior closed span | 14/14 | 26/26 | `COMPLETE` |
| path `~/` left intact | 14/14 | 26/26 | `COMPLETE` |
| FIVE heading wrapped `~~~…~~` after `fix-all` | 13/14 | 26/26 | withheld (`R-D2-five`) |
| Review 2 triple interior/split | 11/14 | 26/26 | withheld (`R-D1-blocks`, `R-D1-ten`, `R-D2-five`) |

`fix-all` remains 14/14 COMPLETE with `cd ~/Projects/Sentinel` present in
`gate-s2-evidence.md`. Wrap-norm of that file contains one single-tilde run (that
path) and 22 isolated `~~` pairs; there is no `~~~`. A later unclosed span does not
make the already-closed D-F1 sentence live.

## 4. Attacks that did not fail the instrument

These were run. They are not grounds to withhold HOLD, and they do not reopen §3.

- **Review 2 F2-1 exact.** Quoted, ASCII space, `/*split*/`, and newline before `:`
  after `fix-all` are 14/14 REQUIRED and 25/26 CONTROL, exactly `C-D6-codes`.
  Single-quoted keys, `["IDENT"]`, `['IDENT']`, `[ /*k*/ "IDENT" /*k*/ ]`, and tab
  before `:` all fail `C-D6-codes`.
- **Review 2 F2-2 exact.** Interior D1 / FIVE / packet-ten after `fix-all` are 11/14
  on exactly those three REQUIRED rows as committed. Nested isolated pairs that leave
  any phrase character unstruck are fail-closed. Four-tilde wrap is fail-closed.
- **Review 1 F1-1 / F1-2 exact.** Restoring only the blocks-exit sentence unstruck is
  13/14, exactly `R-D1-blocks`. Omitting D-09 is 13/14, exactly `R-D2-truth`. Leaving
  the FIVE heading unstruck is 13/14, exactly `R-D2-five`.
- **Forms the CARD excludes from the finite key grammar.** Backtick template
  `` [`SIGNER_CHAIN_PENDING_HEAD`] ``, unquoted computed `[IDENT]`, `["IDENT" as const]`,
  unicode-escape quoted `"SIGNER_CHAIN_PENDING_\u0048EAD"`, unquoted `\u0053IGNER…`,
  shorthand without `:`, concatenation `["SIGNER_" + "HEAD"]`, sibling
  `EXTRA_REASON = { SIGNER_CHAIN_PENDING_HEAD: … }`, and `| "SIGNER_CHAIN_PENDING_HEAD"`
  on the `ReasonCode` alias all COMPLETE. CARD freezes `REASON_SEVERITY` keys under
  the listed grammar, not every TypeScript production. Inline
  `...{SIGNER_CHAIN_PENDING_HEAD: "FATAL"}` is fail-closed (inner `}` ends the finite
  walk; `C-D6-codes` FAIL). `#SIGNER_CHAIN_PENDING_HEAD: "FATAL"` is fail-closed
  because `#` is skipped and the IDENT is then scored; it is also not a public
  object-literal field.
- **Annex B HTML-like comments.** Node `eval` of
  `({ SIGNER_CHAIN_UNSTABLE: "FATAL", SIGNER_CHAIN_PENDING_HEAD<!--split\n: "FATAL" })`
  returns own-property `SIGNER_CHAIN_PENDING_HEAD`. The skipper does not treat `<!--`
  as `//` or `/* */`; after `fix-all` that sibling is 14/14 and 26/26 COMPLETE with
  scored set 35. The listed grammar names those two comment forms, not HTML comments.
  Same class as template/computed keys: Node-legal, not a freeze the CARD claimed.
- **ZWSP / homoglyph / single `~` that break the watched ASCII phrase.**
  `e\u200bxit`, dotless-i `exıt`, and `exi~t` make `phrase_is_live` false because the
  contiguous ASCII phrase is gone. CARD absence is defined on that ASCII phrase.
  `<s>` and HTML comments around the sentence leave the phrase in the stream and FAIL
  `R-D1-blocks`. Inline-code `` `~~…~~` `` COMPLETE; CARD does not claim to parse
  Markdown code spans. A leading `\` before `~~` is unspecified; `\~~…\~~` COMPLETE
  because the isolated pair still toggles.
- **Path `~/` versus `~~/`.** Existing `~/` does not make `fix-all` fail `R-D2-five`.
  Replacing it with `~~/` after `fix-all` fails `C-D2-prefix` (that line sits in the
  signed prefix) and `R-D2-five` (an extra isolated `~~` flips whole-file strike
  parity). That is whole-file coupling, not the path-`~` exception the CARD named. I
  do not add it as a numbered defect.
- **D2 wrap.** Live sentence is `Ten minus the five` / `fixed leaves six` across a
  newline. Joined phrase is absent from raw file bytes and present after wrap-norm.
  Baseline `R-D2-absent` FAILs, so the scored check is wrap-norm, not a line grep.
- **comment-star wrap.** `Both are open (v1.1 register)` is absent from raw wrap-norm of
  `decode/index.ts` and present after `^\s*\*` strip. `NEITHER the signer nor the verifier`
  is present in both. Baseline `R-D4b-open` FAIL proves the strip is load-bearing.
- **Signed-pack leak.** `fix-all` leaves S1 sha256 `25dcefcade…` and the prefix hash
  `470ec1de8e…`. Appending a byte to S1 after `fix-all` fails exactly `C-D1-s1`.
  Prefix whitespace before `## 11. What is NOT in evidence` fails exactly `C-D2-prefix`.
- **Historical quotes.** After `fix-all`, erasing the v3 quote of the detail claim
  fails exactly `C-hist-v3`.
- **Second checker / gate wiring.** Planting `scripts/check-claims.sh` after `fix-all`
  fails exactly `C-no-second-checker`. Appending `d-claims` to `test.sh` fails exactly
  `C-no-gate-wire`.
- **`RefusalRecord.detail`.** Adding `detail?: string` to the `RefusalRecord` body after
  `fix-all` fails exactly `C-D6-no-detail`.
- **Preflight / identity / completion.** Exact 40-hex, clone HEAD match, dirty source
  refused, completion withheld on baseline 0/14.

D-F3 as Batch A / D-F5 as no second checker match D-059(5). No gate harness is present,
so D-059(7) is N/A as claimed.

## 5. What I did not run

I did not launch Foundry, the TypeScript suite, the verifier, `scripts/test.sh` as a
gate, `a-floors-gate.py`, or `scripts/check-suite-floors.sh` as a process. Floor
constants were read from `scripts/test.sh` at the subject (`FOUNDRY_MIN_TESTS=103`,
`TS_MIN_TESTS=550`, `VERIFIER_MIN_TESTS=221`, `VERIFIER_MIN_SAMPLES=7`,
`VERIFIER_MIN_TAMPER=78`, `VERIFIER_MIN_TAMPER_MODES=30`) and `C-floors` PASSed in
every non-`break-floors` variant. Key legality was checked with Node `eval` of
object-literal source, not with `tsc`. Attack harnesses, clones and matrices stayed in
`/tmp`. `/usr/bin/grep` tree sweeps were on the clean clone, not the dirty live
worktree. I did not start a product repair.

## 6. Limits

This review establishes that the twenty-two committed variants discriminate as
labelled, that Review 3's two named attacks are closed in those spellings and in the
Zs / extra-tilde classes they named, that wrap-norm and comment-star stripping remain
the scored Markdown/TypeScript checks, and that I could not print the completion token
for a public `REASON_SEVERITY` key the finite grammar claims to freeze or for extra
tildes wrapping the watched D-F1 sentence. It does not establish general prose
consistency, implementation correctness, a gate outcome, historical factual truth,
certification, signing, publication or D-055 closure.

**HOLD for instrument readiness only.** This is not implementation approval, a gate
signature, certification, ratification, publication, rename, D-055 assessment or push
authorization.
