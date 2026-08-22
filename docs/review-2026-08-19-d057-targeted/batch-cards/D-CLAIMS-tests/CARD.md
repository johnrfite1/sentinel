# D-CLAIMS — finite maintained-claim test contract

**Verdict: instrument only. Not a HOLD, not implementation approval, not a gate signature,
certification, ratification, publication, rename, D-055 assessment or push authorization.**

**Behavioral baseline:** `1e7761be051422ad8091b203df375ddcfb7d1208` (A-094; parent is A-FLOORS
implementation HOLD `086b3182affe1fc1198ebc21b19d618f4f2e840e`). Independently re-enumerated
2026-08-22 at that commit. Completeness is claimed only inside the inventory below.

## FIRST INSTRUMENT REVIEW — THREE DEFECTS CLOSED

`INSTRUMENT-REVIEW-1.md` returned **FAIL** on `4b10470`. That review is historical and is not
edited. This correction closes its three findings:

- **F1-1, D-F1 BLOCKER half unobserved.** `fix-all` struck `; it does not.` and printed
  COMPLETE while unstruck `this alone blocks exit` remained under BLOCKERS. REQUIRED now uses
  `live_text` (wrap-norm with `~~…~~` spans removed). `R-D1-blocks` PASSes only when that
  sentence is gone from unstruck BLOCKER 1. `fix-all` strikes it.
- **F1-2, D-F2 inverted into a CONTROL, D-09 omitted.** `C-D2-struck` required the unstruck
  `FIVE OF THESE TEN ARE NO LONGER ACCEPTED LIMITS` heading to remain, so FIVE→FOUR failed a
  CONTROL and leaving it live still COMPLETE. That CONTROL is removed. `R-D2-five` requires
  the heading absent from unstruck §11.0; `R-D2-truth` requires the full frozen `D2_TRUTH`
  including `` `D-09` is in both the fixed and accepted sets ``. `C-D2-packet-ten` locked the
  present-tense §7 NON-BLOCKER `The ten §11.0 accepted limits` while §3 already reads SIX;
  that CONTROL is removed. `R-D1-ten` / `R-D1-six` require ten absent from unstruck packet and
  six present. Dated session-state “ten accepted as documented limits” remains a CONTROL.
- **F1-3, public reason-code split uncontrolled.** `C-D6-codes` freezes the 35
  `REASON_SEVERITY` keys. `break-reason-split` inserts `SIGNER_CHAIN_PENDING_HEAD` and must
  fail exactly that CONTROL. `C-D6-no-detail` still observes a `detail` field.

Unstruck oracles are the scored check for D1/D2 live false headings and for packet “ten”.
Struck copies may remain so drift stays visible. Review 1 stays byte-identical.

## SECOND INSTRUMENT REVIEW — TWO DEFECTS CLOSED

`INSTRUMENT-REVIEW-2.md` returned **FAIL** on `c9a19e4`. That review is historical and is not
edited. This correction closes its two findings:

- **F2-1, `C-D6-codes` missed TypeScript-legal keys.** The scored tokeniser was
  `(?m)^\\s+([A-Z][A-Z0-9_]+):`, so quoted keys, space/comment/newline before `:`, and
  `["IDENT"]` were invisible. `reason_object_keys` is a finite grammar: unquoted IDENT,
  `"IDENT"` / `'IDENT'`, or that IDENT in brackets; whitespace and `//` or `/* */` may sit
  between the key and `:`; scored IDENT is `[A-Z][A-Z0-9_]*`. It is not a TypeScript
  parser. Sibling objects and `ReasonCode` union widen remain outside the freeze (Review 2
  §4). Committed variants: `break-reason-quoted`, `break-reason-space`,
  `break-reason-comment`, `break-reason-newline`, plus existing `break-reason-split`.
- **F2-2, interior/split `~~` still COMPLETE.** Deleting whole `~~…~~` spans made
  `this alone blocks exi~~t~~` and `~~this alone ~~blocks exit` look absent. REQUIRED
  absence now uses `phrase_is_live`: the phrase is live if any occurrence has at least one
  unstruck character, or if a `~~` span is left unclosed. A fully closed span covering
  every character of the phrase may remain for drift. `break-live-strike` applies `fix-all`
  then Review 2's interior D1 / FIVE / packet-ten edits and must fail exactly those three
  REQUIRED rows. Extra tildes, `<del>`, and unclosed `~~` stay fail-closed.

Reviews 1 and 2 stay byte-identical.

## THIRD INSTRUMENT REVIEW — TWO DEFECTS CLOSED

`INSTRUMENT-REVIEW-3.md` returned **FAIL** on `4c201d7`. That review is historical and is not
edited. This correction closes its two findings:

- **F3-1, claimed whitespace missed TypeScript whitespace.** `_skip_ws_comments` only
  skipped space, tab, CR and LF. VT, FF, NBSP, LS, PS and BOM before `:` are ECMAScript
  WhiteSpace / LineTerminator and Node `eval` own-properties. The skipper now takes
  those code points plus other Unicode Zs. Committed variants: `break-reason-vt`,
  `break-reason-ff`, `break-reason-nbsp`, `break-reason-ls`, `break-reason-ps`,
  `break-reason-bom`.
- **F3-2, extra tildes `~~~` were not fail-closed.** Toggling on every two-character
  `~~` made `~~~…~~` / `~~…~~~` look fully struck. Only an *isolated* `~~` pair
  (not part of `~~~`) now toggles strike, so extra tildes leave the phrase live or the
  span unclosed. A path `~` elsewhere in the file is not extra-tilde fail-closed.
  Committed `break-extra-tilde-open` and `break-extra-tilde-close` must fail
  exactly `R-D1-blocks`. An unclosed span does not resurrect a prior closed span
  in the same region. Four-tilde wrap, `<del>`, and unclosed `~~` stay fail-closed.

Reviews 1–3 stay byte-identical.

**Authority:** D-058(1), (6), (8)D and (9); D-059(5)–(6); D-060(1); D-066(2)–(3). D-F3 is
Batch A (closed at A-094). D-F5 is a dependency on that reader, not a second checker.

**This is a test-only deliverable.** This commit must not modify any production file. There is
no new `scripts/check-*.sh`. `d-claims.py` is an independent instrument and must not be wired
into `scripts/test.sh`. Markdown oracles are wrap-normalized (`\s+` → one space) over a named
file or named region; a line-oriented grep is not the scored check (D-058(6)). A watched
false claim is absent only when `phrase_is_live` is false on that wrap-normalized region:
every occurrence of the phrase has all of its characters inside a closed isolated `~~…~~`
span. An interior or split span, extra tildes (`~~~…~~` / `~~…~~~`), or an unclosed `~~`
that still covers the phrase, leaves the claim live. A later unclosed span does not
resurrect a prior closed span. TypeScript oracles
strip leading `^\s*\*` on each line, then wrap-normalize, so a comment-continuation star
is not a word in the phrase. `REASON_SEVERITY` keys are read with the finite grammar in `reason_object_keys`, not
with a line-anchored `IDENT:` regex. Whitespace between a key and `:` is ECMAScript
WhiteSpace plus LineTerminator (including VT, FF, NBSP, BOM, LS, PS, and other Zs).

Failed global contracts under `docs/review-2026-08-19-d057-targeted/contract/` are not this
spec. Historical reviews, A-077, and dated round-five prose are not rewritten (D-058(8)D).

## 1. Declared future implementation surfaces

Exactly five files, comment or unsigned maintained prose only:

| ID | Surface | Live false current claim (measured) | Frozen replacement |
|---|---|---|---|
| D6 | `ts/src/signer/protocol.ts` NatSpec on `SIGNER_CHAIN_UNSTABLE` | `so the refusal detail now distinguishes them.` | Replace that clause with `D6_TRUTH` below. Keep `(a)`/`(b)`, `D-057(4)`, and the single FATAL code. |
| D4a | `ts/test/evaluate.checks.test.ts` comment | `` `EVAL_ACTION_TARGET_MATCHES_MANDATE` must PASS. `` | `` `EVAL_TARGET_BOUND` must PASS. `` |
| D4b | `ts/src/decode/index.ts` NatSpec | `NEITHER the signer nor the verifier` and `Both are open (v1.1 register)` | `D4B_TRUTH` below. Keep `D-014 deliberately kept conformance out of the signer`. |
| D1 | `docs/exit-criterion-packet.md` §7 BLOCKER 1 and NON-BLOCKERS | live `it does not.` and live `this alone blocks exit`; present-tense `The ten §11.0 accepted limits` | `D1_TRUTH` in BLOCKER 1; closed-span strike of the blocks-exit sentence; `The six §11.0 accepted limits` in NON-BLOCKERS. Interior or split `~~` is not a repair. |
| D2 | `docs/gate-s2-evidence.md` §11.0 | `Ten minus the five fixed leaves six`; unstruck `FIVE OF THESE TEN ARE NO LONGER ACCEPTED LIMITS` | Full `D2_TRUTH` below, including the D-09-in-both-sets clause. Strike the FIVE heading rather than requiring it to remain. §11.0 post-dates the 2026-08-16 S2 signature and is authorised at D-057; it is not retrospectively signed. |

Frozen replacement strings (exact; wrap-normalized search):

- **D6_TRUTH:** `The signed RefusalRecord has no detail field; SIGNER_CHAIN_UNSTABLE remains one public code for both (a) and (b). Distinguishing text exists only on ChainUnstableError, which attest.ts does not put on the wire.`
- **D4B_TRUTH:** `The D-010 verifier compares those fields to the presented action and mandate` and `Register E4 is VERIFIER HALF BUILT · SIGNER HALF DELIBERATELY NOT BUILT, not an open defect.`
- **D1_TRUTH:** inside the BLOCKER 1 region (from `1. **The signed Gate S1 pack` through `2. **\`E3\` is an open fork`): `FALSE SINCE A-074; THE COMPARISON IS BUILT`
- **D2_TRUTH:** `Four entries were wholly removed (`D-10`, `G-5`, `H-5`, `H-8`); `D-09` is in both the fixed and accepted sets. Ten minus four wholly-removed entries is six, not five.`

BLOCKER 1 region is the only D1 scored region. Whole-file `FALSE SINCE A-074` already exists in
§3b and is a control, not D1_TRUTH.

## 2. Forbidden surfaces

- `docs/gate-s1-evidence.md` (signed). Byte-identical at the frozen hash.
- `docs/gate-s2-evidence.md` bytes before `## 11. What is NOT in evidence` (S2 prefix).
- `RefusalRecord` / `Refusal` fields, `attest.ts` wire, new public reason codes, a signed
  `detail` field, or splitting `SIGNER_CHAIN_UNSTABLE` (D-057(4); C-SNAPSHOT CARD exclusion).
- Signer-side E4 conformance (D-014). Register E4 signer half stays deliberately unbuilt.
- `scripts/test.sh`, `scripts/check-suite-floors.sh`, a second floor or claim checker.
- B-EVENTS and C-SNAPSHOT frozen tests.
- Rewriting A-077, Reviews, or dated round-five “ten accepted as documented limits”.
- “Fixing” `docs/v1-1-register.md` §13.7’s true `description` sub-field claim.

A later `docs/decisions.md` HOLD record may *supersede* A-077; it must not rewrite A-077.

## 3. Outside this card (named residuals, not silent expansions)

- `HANDOFF.md` “NO SUBSEQUENT BATCH HAS BEGUN” (A-086 dated). D-058(8)D named A-080 sites;
  the A-080 strike of `COMPLETE THROUGH REVERIFICATION` already holds and is a control.
- Full `docs/session-state.md` rewrite. A-FLOORS already removed live floor copies.
- D-055, publication, rename, push, gate signatures.

## 4. Frozen hashes at the baseline

| Object | sha256 |
|---|---|
| `docs/gate-s1-evidence.md` | `25dcefcade99e9e45be0c482f3dc5141f4d25335a920fabe1012303c7d7caf68` |
| S2 prefix before `## 11. What is NOT in evidence` | `470ec1de8ee696a2875334a7873e8e02504ea27d10676cb1a0018668097ba02f` |
| `scripts/check-suite-floors.sh` | `95b65a02bdfc8436e4739b7e5ef90b803964236a86173ed5b8f3c6cc139f7a46` |
| B-EVENTS `contracts/test/SentinelVault.events.t.sol` | `2a9219cc5138858b012b0bc56069490db3dd7d1963b73ccc19c28a48ce2b029e` |
| C-SNAPSHOT `ts/test/vault.snapshot.classification.test.ts` | `29a673560e89b639b6635661706a368454c9969a04c5d37c4f6c15229df3dd8a` |

Live floors remain 103/550/221/7/78/30.

## 5. Focused oracle

`d-claims.py <source-repository> [exact-commit]` clones the exact 40-hex subject and mutates
only that clone. The source worktree must have no tracked changes. Variant
`D_CLAIMS_VARIANT` (default `baseline`).

**14 REQUIRED** (PASS only when the named live false claim is gone per `phrase_is_live`
where noted, *and* the frozen truth is present, each scoped to its surface/region):

| Row | PASS when |
|---|---|
| `R-D6-absent` | `protocol.ts` has no live `so the refusal detail now distinguishes them` |
| `R-D6-truth` | `protocol.ts` wrap-norm contains `D6_TRUTH` |
| `R-D4a-absent` | `evaluate.checks.test.ts` lacks `EVAL_ACTION_TARGET_MATCHES_MANDATE` |
| `R-D4b-neither` | `decode/index.ts` has no live `NEITHER the signer nor the verifier` |
| `R-D4b-open` | `decode/index.ts` has no live `Both are open (v1.1 register)` |
| `R-D4b-truth` | `decode/index.ts` wrap-norm contains both `D4B_TRUTH` fragments |
| `R-D1-absent` | BLOCKER 1 has no live `it does not.` (`phrase_is_live`) |
| `R-D1-blocks` | BLOCKER 1 has no live `this alone blocks exit` |
| `R-D1-truth` | BLOCKER 1 wrap-norm contains `D1_TRUTH` |
| `R-D1-ten` | packet has no live `The ten §11.0 accepted limits` |
| `R-D1-six` | packet wrap-norm contains `The six §11.0 accepted limits` |
| `R-D2-absent` | `gate-s2-evidence.md` has no live `Ten minus the five fixed leaves six` |
| `R-D2-five` | `gate-s2-evidence.md` has no live `FIVE OF THESE TEN ARE NO LONGER ACCEPTED LIMITS` |
| `R-D2-truth` | wrap-norm contains the full `D2_TRUTH` string, including the D-09-in-both-sets clause |

**CONTROL** rows (must PASS at baseline and after a conforming repair): `(a)`/`(b)` remain;
`RefusalRecord` body has no `detail` field; `SIGNER_CHAIN_UNSTABLE` stays FATAL; the
`REASON_SEVERITY` key set stays the frozen 35 codes under the finite key grammar (quoted,
unquoted, bracket-quoted, with ECMAScript whitespace or comments before `:`); `D-057(4)` remains; `EVAL_TARGET_BOUND`
remains; `D-014 deliberately kept conformance out of the signer` remains; register E4 signer
half remains deliberately unbuilt; packet §3b `FALSE SINCE A-074; CORRECTED 2026-08-19`
remains; signed S1 bytes and S2 prefix hash remain; `WHAT IS ACCEPTED TODAY IS SIX` and `G-3`
remain in §11.0; `THAT SENTENCE IS FALSE AND IS SUPERSEDED` remains; session-state dated
`ten accepted as documented limits` remains; A-077 heading remains; HANDOFF A-080 strike
remains; §13.7 description claim remains; floors 103/550; A-FLOORS checker hash; B/C hashes;
no `check-claims.sh` / `check-prose.sh`; `test.sh` does not mention `d-claims`; historical
review quotes of the live false strings remain in `ADJ2.md` and `reviewers/v3/REPORT.md`.

Pre-repair `baseline` must FAIL every REQUIRED and PASS every CONTROL. Completion token
`D_CLAIMS_FOCUSED_COMPLETE` is printed only on 14/14 REQUIRED, all CONTROL, exit 0.

## 6. Causal siblings (clone-only)

| Variant | Discriminating observation |
|---|---|
| `baseline` | 0/14 REQUIRED, all CONTROL, exit 1. |
| `fix-d6` | only the D6 pair PASS; other REQUIRED FAIL; CONTROL PASS. |
| `fix-all` | 14/14 REQUIRED and all CONTROL (oracle completeness, not the product commit). |
| `break-s1` | S1-bytes CONTROL FAIL; REQUIRED unchanged. |
| `break-s2-prefix` | S2-prefix CONTROL FAIL; REQUIRED unchanged. |
| `break-floors` | floors CONTROL FAIL. |
| `break-bevents` | B-EVENTS hash CONTROL FAIL. |
| `break-d014` | D-014 CONTROL FAIL. |
| `break-reason-split` | `C-D6-codes` FAIL; REQUIRED unchanged. |
| `break-reason-quoted` | `C-D6-codes` FAIL (`"SIGNER_CHAIN_PENDING_HEAD"`). |
| `break-reason-space` | `C-D6-codes` FAIL (space before `:`). |
| `break-reason-comment` | `C-D6-codes` FAIL (`/*split*/` before `:`). |
| `break-reason-newline` | `C-D6-codes` FAIL (newline before `:`). |
| `break-live-strike` | after `fix-all`, Review 2 interior/split `~~` on D1 / FIVE / packet-ten: exactly `R-D1-blocks`, `R-D2-five`, `R-D1-ten` FAIL (11/14 REQUIRED), CONTROL PASS. |
| `break-reason-vt` / `ff` / `nbsp` / `ls` / `ps` / `bom` | `C-D6-codes` FAIL (ECMAScript whitespace before `:`). |
| `break-extra-tilde-open` | after `fix-all`, `~~~…~~` around the D-F1 sentence: exactly `R-D1-blocks` FAIL (13/14 REQUIRED). |
| `break-extra-tilde-close` | after `fix-all`, `~~…~~~` around the D-F1 sentence: exactly `R-D1-blocks` FAIL (13/14 REQUIRED). |

No gate harness: this card adds no targeted guard, so D-059(7) does not apply. D-059(5)
forbids a second floor/claim checker.

## 7. D-058(9)

Two implementation attempts against a frozen HOLD instrument. Instrument corrections do not
consume an attempt. Independent review of this instrument is required before any product edit.
