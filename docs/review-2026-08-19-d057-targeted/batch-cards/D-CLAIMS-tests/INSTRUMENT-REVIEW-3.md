# D-CLAIMS — independent second-corrected instrument review 3

## Verdict

**FAIL for instrument readiness.** Review 2's two named attacks are closed in the
spellings that review used: after `fix-all`, quoted / space / `/*split*/` / newline
`SIGNER_CHAIN_PENDING_HEAD` each fail exactly `C-D6-codes`; interior `exi~~t~~`, split
`~~this alone ~~blocks exit`, `FI~~V~~E`, and `The t~~e~~n` each fail the matching
REQUIRED row; committed `break-reason-quoted|space|comment|newline` and
`break-live-strike` discriminate as labelled. The second-correction still prints
`D_CLAIMS_FOCUSED_COMPLETE` for a TypeScript-legal public `REASON_SEVERITY` key the
CARD's finite grammar claims to freeze — unquoted IDENT with VT, FF, NBSP, LS, PS or
BOM before `:` — and for a watched ASCII D-F1 sentence wrapped in extra tildes
(`~~~…~~` / `~~…~~~`) that the CARD says stay fail-closed. Those are live holes in
the claimed grammars, not surviving Review-2 rows.

This is an instrument-readiness verdict only. It is not an implementation verdict, gate
approval or signature, certification, ratification, publication, rename, D-055 assessment
or push authorization. I did not edit CARD.md, `d-claims.py`, production files,
`INSTRUMENT-REVIEW-1.md`, `INSTRUMENT-REVIEW-2.md` or signed packs.

## 1. Exact subject, scope and preservation

I reviewed exact subject `4c201d7b9443876fab2edd4c6f633db6ec4c6ea6`, tree
`b45a60207041db8c30fde637778d30b8e597aad2`, message `D-CLAIMS: close Review 2 instrument
defects`. Its sole parent is Review 2 FAIL
`20f3d69c2315684820b11bab8c47d6b0b2e864f1`. Behavioral baseline for pre-repair oracles is
A-094 `1e7761be051422ad8091b203df375ddcfb7d1208`. HEAD was exactly the subject. Tracked
`README.md` was dirty and `assets/` / `.serena/` were untracked in the live worktree; I
did not touch, stage or commit any of them. Every focused run used a byte-identical
`/tmp` copy of `d-claims.py` against a disposable `git clone --local --no-hardlinks` of a
clean source. Attack harnesses stayed in `/tmp`. Author `RESULTS.md` was not used as
evidence.

Parent `20f3d69` → subject is CARD.md, RUNBOOK.md, RESULTS.md and `d-claims.py` only
(244 insertions, 47 deletions). Baseline `1e7761b` → HEAD adds only this
`D-CLAIMS-tests/` directory (six paths before this review). No production byte, existing
product test, `scripts/test.sh`, `scripts/check-*.sh`, maintained claim, decision record,
signed pack or prior review moves. The five declared surfaces are blob-identical at
`1e7761b` and HEAD. `git diff --check` on the subject is clean. `scripts/test.sh` does
not mention `d-claims`. No `check-claims.sh` / `check-prose.sh` exists.

`INSTRUMENT-REVIEW-1.md` is byte-identical at sha256
`fd48278dc9946342868e73b6e4ca8ad596ae0f34237618d0359ac0047e5cab35` (git blob
`14fff621d454d4b32f25a572822eb535a53faafe`). `INSTRUMENT-REVIEW-2.md` is byte-identical
at sha256 `766cfc1f338ff769f2e9f5d561285d09e5616bd0d6f7117e66478863629b0aa6` (git blob
`b28dbf8588a8e2209aa55422b3fb7207ff872b75`). I did not edit either.

| Object | Git blob | sha256 |
|---|---|---|
| `d-claims.py` (586 lines) | `809e88f6286aeaa5e693b159bcdfb32b5b21a871` | `cee101a25f3aeb745b83a1a1328605a84962d87ebaa51b3f86e4797c240b1ad5` |
| `CARD.md` | `56911df46aea456e81f969a022599a2cf7230995` | `952edf17d03b8335bf6b9289585a86c755231d36755975a787a900f2338e8210` |
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

I read the workspace rules, D-058(8)D / D-059(5)–(6) / D-060(1), Reviews 1 and 2, the
complete CARD/RUNBOOK/harness, and the five declared surfaces at the baseline. I authored
neither this instrument nor a production repair.

## 2. Independent fourteen-variant reproduction

Dirty live worktree refused (exit 2, `source worktree has tracked changes`). Uppercase and
39-hex subjects refused (`exact lowercase 40-hex`, exit 2). Unknown `D_CLAIMS_VARIANT`
refused (exit 2). Untracked-only source (canary file, porcelain `--untracked-files=no`
empty) ran. Tracked dirt in that clone refused.

Against behavioral baseline `1e7761b`, and again against subject `4c201d7` for
`baseline` / `fix-all` (production bytes identical; matrices identical):

| Variant | Exit | REQUIRED | CONTROL | Completion | Matrix sha256 |
|---|---:|---:|---:|---|---|
| `baseline` (`1e7761b`) | 1 | 0/14 | 26/26 | withheld | `d62568ff732e532eba2fb81a2d8a562f5fa1b1870b9a37280561b9c947d3ee99` |
| `baseline` (`4c201d7`) | 1 | 0/14 | 26/26 | withheld | `d62568ff732e532eba2fb81a2d8a562f5fa1b1870b9a37280561b9c947d3ee99` |
| `fix-d6` | 1 | 2/14 | 26/26 | withheld | `debbcb9334cf06877a20d476c50cb90ec719470e0194bd4a11537b79fb8f7d14` |
| `fix-all` | 0 | 14/14 | 26/26 | `D_CLAIMS_FOCUSED_COMPLETE` | `28c30a8dcf97f4c440e4e1bbe2de2fd0ec67776eec67f7de62af146cd5dc4cb6` |
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
| `break-live-strike` | 1 | 11/14 | 26/26 | withheld | `dad3fa42bb5acdc3bf1b01ed2fe1b4744f5fd959a72e820114e56daa3c683aad` |

`fix-d6` PASSes only `R-D6-absent` and `R-D6-truth`. Each `break-s1` / `break-s2-prefix` /
`break-floors` / `break-bevents` / `break-d014` / `break-reason-*` fails exactly the named
CONTROL (`C-D1-s1`, `C-D2-prefix`, `C-floors`, `C-B-EVENTS`, `C-D4b-d014`, `C-D6-codes`)
with REQUIRED still 0/14 except `break-live-strike`. `break-live-strike` fails exactly
`R-D1-blocks`, `R-D2-five`, `R-D1-ten`. Baseline FAILs all 14 REQUIRED. Those counters
are from the reproduced matrices, not from `RESULTS.md`. Clone HEAD matched the
requested 40-hex on every successful run. The five `break-reason-*` matrices are
byte-identical to each other because they fail the same 15 rows; the matrix does not
name which spelling was inserted.

## 3. Defects

### 3.1 FAIL — claimed whitespace grammar does not observe TypeScript whitespace (Review 2 F2-1 remains for that class)

CARD §0 / §5 / `reason_object_keys` claim a finite key grammar: unquoted IDENT,
`"IDENT"` / `'IDENT'`, or that IDENT in brackets; **whitespace** and `//` or `/* */`
may sit between the key and `:`; scored IDENT is `[A-Z][A-Z0-9_]*`. Review 2's exact
quoted / ASCII-space / comment / newline spellings, plus single-quoted keys, bracket
forms `[ "IDENT" ]` with comments inside the brackets, tab, and CR, now fail
`C-D6-codes` after `fix-all` (14/14 REQUIRED, 25/26 CONTROL, completion withheld,
scored set length 36 and contains `SIGNER_CHAIN_PENDING_HEAD`). Those Review 2 rows
are closed.

The skipper is not the whitespace the CARD named. `_skip_ws_comments` accepts only
` \t\n\r`. ECMAScript WhiteSpace also includes VT (`U+000B`), FF (`U+000C`), NBSP
(`U+00A0`), BOM (`U+FEFF`) and other Zs; LineTerminator also includes LS (`U+2028`)
and PS (`U+2029`). Node `eval` of
`({ SIGNER_CHAIN_UNSTABLE: "FATAL", SIGNER_CHAIN_PENDING_HEAD\v: "FATAL" })` returns
an own-property `SIGNER_CHAIN_PENDING_HEAD`. The same holds for FF, NBSP, LS, PS and
BOM. Those are TypeScript-legal public `REASON_SEVERITY` keys: `ReasonCode` is
`keyof typeof REASON_SEVERITY`.

Measured `/tmp` siblings against the same clean `1e7761b` clone, each after harness
`apply_all` (14/14 REQUIRED already held):

| Sibling | REQUIRED | CONTROL | Completion | `C-D6-codes` | scored |
|---|---:|---:|---|---|---:|
| Review 2 `"SIGNER_CHAIN_PENDING_HEAD": "FATAL"` | 14/14 | 25/26 | withheld | FAIL | 36 |
| Review 2 `SIGNER_CHAIN_PENDING_HEAD : "FATAL"` (space) | 14/14 | 25/26 | withheld | FAIL | 36 |
| Review 2 `SIGNER_CHAIN_PENDING_HEAD /*split*/: "FATAL"` | 14/14 | 25/26 | withheld | FAIL | 36 |
| Review 2 name, newline, then `:` | 14/14 | 25/26 | withheld | FAIL | 36 |
| `SIGNER_CHAIN_PENDING_HEAD\v: "FATAL"` (VT) | 14/14 | 26/26 | `COMPLETE` | PASS | 35 |
| `SIGNER_CHAIN_PENDING_HEAD\f: "FATAL"` (FF) | 14/14 | 26/26 | `COMPLETE` | PASS | 35 |
| `SIGNER_CHAIN_PENDING_HEAD` then NBSP then `:` | 14/14 | 26/26 | `COMPLETE` | PASS | 35 |
| LS / PS / BOM before `:` | 14/14 | 26/26 | `COMPLETE` | PASS | 35 |

On the VT sibling the scored set is still the frozen 35 and does not contain
`SIGNER_CHAIN_PENDING_HEAD`, while the `REASON_SEVERITY` body contains
`SIGNER_CHAIN_PENDING_HEAD\x0b: "FATAL"` as a 36th public key. A repairer can ship the
forbidden D-F6 product change, copy the frozen truth phrases, and receive the
completion token. Review 2's exact ASCII-space spelling is now a committed variant.
The defect class — whitespace between IDENT and `:` that TypeScript accepts and the
CARD claims to freeze — is not closed.

`/usr/bin/grep` on the clean clone finds `SIGNER_CHAIN_PENDING_HEAD` only in this card
directory (CARD, harness `break-reason-*`, Reviews 1–2). Production `protocol.ts` does
not contain it until an attack inserts it.

### 3.2 FAIL — extra tildes `~~~` do not stay fail-closed (Review 2 F2-2 remainder inside the claimed `~~` grammar)

CARD §0 says extra tildes, `<del>`, and unclosed `~~` stay fail-closed, and that a
watched claim is absent only when every occurrence has all of its characters inside a
closed `~~…~~` span. `phrase_is_live` toggles on each two-character `~~` and treats a
third `~` as an ordinary character. Review 2's interior `exi~~t~~`, split
`~~this alone ~~blocks exit`, `FI~~V~~E`, and `The t~~e~~n` now fail the matching
REQUIRED row after `fix-all` (13/14, completion withheld). Four-tilde wrap
`~~~~…blocks exit.~~~~` is still fail-closed. Committed `break-live-strike` is 11/14
and fails exactly those three REQUIRED rows. Those Review 2 rows are closed.

Three tildes are extra tildes. The watched ASCII phrase is still present. The oracle
reports it not live:

| Sibling (after `fix-all`) | Live remainder | REQUIRED | CONTROL | Completion |
|---|---|---:|---:|---|
| restore `this alone blocks exit` fully unstruck | phrase present | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| `this alone blocks exi~~t~~.` | interior letter struck | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| `~~this alone ~~blocks exit` | trailing words unstruck | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| `~~~~…blocks exit.~~~~` (four tildes) | phrase unstruck after double toggle | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| `<del>…blocks exit.</del>` | phrase still in the char stream | 13/14 | 26/26 | withheld (`R-D1-blocks`) |
| unclosed `~~…exit.` | global unclosed flag | 12/14 | 26/26 | withheld (`R-D1-absent`, `R-D1-blocks`) |
| `~~~Under C1 condition 4 this alone blocks exit.~~` | every phrase character inside a closed span; leftover `~` is a character | 14/14 | 26/26 | `COMPLETE` |
| `~~Under C1 condition 4 this alone blocks exit.~~~` | same | 14/14 | 26/26 | `COMPLETE` |

`FI~~V~~E` and packet `The t~~e~~n` remain REQUIRED FAIL as committed. Extra tildes
were the CARD's own fail-closed claim for this grammar. `~~~` prints the completion
token while the D-F1 BLOCKER sentence is still the watched ASCII phrase in source.
A leading `\` before `~~` is unspecified; `\~~this alone blocks exit.\~~` also
COMPLETE because the toggle still treats `~~` as delimiters. F3-2 is named from
`~~~` alone.

## 4. Attacks that did not fail the instrument

These were run. They are not grounds for this FAIL, and they do not cancel §3.

- **Review 2 F2-1 exact.** Quoted, ASCII space, `/*split*/`, and newline before `:`
  after `fix-all` are 14/14 REQUIRED and 25/26 CONTROL, exactly `C-D6-codes`.
  Unquoted immediate colon and single-quoted `'FATAL'` value remain FAIL on that
  CONTROL. Single-quoted keys, `["IDENT"]`, `['IDENT']`, `[ "IDENT" ]` with comments
  inside the brackets, quoted key with `/*split*/` before `:`, and tab before `:`
  all fail `C-D6-codes`.
- **Review 2 F2-2 exact.** Interior D1 / FIVE / packet-ten after `fix-all` are 13/14
  on the matching REQUIRED row. Nested `~~this ~~alone~~ blocks exit~~` is fail-closed
  (`R-D1-blocks`). Letterwise `~~t~~~~h~~…` is fail-closed because the spaces in the
  phrase stay unstruck. ZWSP between the tildes of a delimiter (`~\u200b~…~\u200b~`)
  is fail-closed.
- **Review 1 F1-1 / F1-2 exact.** Restoring only the blocks-exit sentence unstruck is
  13/14, exactly `R-D1-blocks`. Omitting D-09 is 13/14, exactly `R-D2-truth`. Leaving
  the FIVE heading unstruck is 13/14, exactly `R-D2-five`. FIVE→FOUR on the heading,
  with full `D2_TRUTH` and the other CARD phrases, is 14/14 and 26/26.
- **Forms the CARD excludes from the finite key grammar.** Backtick template
  `` [`SIGNER_CHAIN_PENDING_HEAD`] ``, unquoted computed `[IDENT]`, `["IDENT" as const]`,
  unicode-escape quoted `"SIGNER_CHAIN_PENDING_\u0048EAD"`, shorthand without `:`,
  concatenation `["SIGNER_" + "HEAD"]`, ZWSP inside the name (not a JS identifier),
  sibling `EXTRA_REASON = { SIGNER_CHAIN_PENDING_HEAD: … }`, and `| "SIGNER_CHAIN_PENDING_HEAD"`
  on the `ReasonCode` alias all COMPLETE. CARD freezes `REASON_SEVERITY` keys under
  the listed grammar, not every TypeScript production. Inline `...{SIGNER_CHAIN_PENDING_HEAD: "FATAL"}`
  is fail-closed (inner IDENT is scored; 25/26). `#SIGNER_CHAIN_PENDING_HEAD: "FATAL"`
  is fail-closed because `#` is skipped and the IDENT is then scored; it is also not
  a public object-literal field.
- **ZWSP / homoglyph / single `~` that break the watched ASCII phrase.**
  `e\u200bxit`, dotless-i `exıt`, and `exi~t` make `phrase_is_live` false because the
  contiguous ASCII phrase is gone. CARD absence is defined on that ASCII phrase.
  `<s>` and HTML comments leave the phrase in the stream and FAIL `R-D1-blocks`.
  Inline-code `` `~~…~~` `` COMPLETE; CARD does not claim to parse Markdown code spans.
- **BLOCKER 1 still under the BLOCKERS heading.** After `fix-all`, item 1 remains under
  `**BLOCKERS — exit cannot be reached while these stand:**` while its body says it is
  not a current exit blocker. CARD §1 / `D1_NEW` keep that item as the scored BLOCKER 1
  region. I do not add list membership as a numbered defect.
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
  Erasing the v3 quote after `fix-all` fails exactly `C-hist-v3`. ADJ2 carries several
  copies; a one-occurrence replace left the CONTROL holding.
- **Second checker / gate wiring.** Planting `scripts/check-claims.sh` after `fix-all`
  fails exactly `C-no-second-checker`. Appending `d-claims` to `test.sh` fails exactly
  `C-no-gate-wire`.
- **`RefusalRecord.detail`.** Adding `detail?: string` to the `RefusalRecord` body after
  `fix-all` fails exactly `C-D6-no-detail`.
- **Paraphrase without frozen truth strings.** Replacing the three contiguous frozen
  truths (D6, D1, D2) with non-frozen paraphrases after `fix-all` scored 11/14 REQUIRED
  and 26/26 CONTROL (exactly `R-D6-truth`, `R-D1-truth`, `R-D2-truth`). D4B_TRUTH is
  wrap-split behind comment stars; I did not land a substitute for that row.
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
every non-`break-floors` variant. VT/FF/NBSP/LS/PS/BOM key legality was checked with
Node `eval` of object-literal source, not with `tsc`. Attack harnesses, clones and
matrices stayed in `/tmp`. `/usr/bin/grep` tree sweeps were on the clean clone, not
the dirty live worktree.

## 6. Limits

This review establishes that the fourteen committed variants discriminate as labelled,
that Review 2's two exact attacks are closed in those spellings, that wrap-norm and
comment-star stripping remain the scored Markdown/TypeScript checks, and that two
instrument defects remain: a `REASON_SEVERITY` whitespace grammar that does not
observe TypeScript whitespace between IDENT and `:`, and extra-tilde `~~~` wraps that
the CARD said would stay fail-closed. It does not establish general prose
consistency, implementation correctness, a gate outcome, historical factual truth,
certification, signing, publication or D-055 closure.

**FAIL.** Do not hold this instrument. Do not start a product repair against it.
