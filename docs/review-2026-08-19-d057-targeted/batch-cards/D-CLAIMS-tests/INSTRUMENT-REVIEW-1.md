# D-CLAIMS — first independent instrument review

## Verdict

**FAIL for instrument readiness.** The focused harness reproduces its own eight-variant
matrix, and several wrap/star/signed-pack attacks it claims to survive do survive. It is
still not a frozen contract a repairer can implement against. `fix-all` and a wrap-aware
CARD-phrase sibling both print `D_CLAIMS_FOCUSED_COMPLETE` at 10/10 REQUIRED and 26/26
CONTROL while declared D-F1 / D-F2 surfaces still carry live false current claims, while
D-F2's second named repair site is inverted into a CONTROL that fails a truthful count
correction, and while a forbidden `SIGNER_CHAIN_UNSTABLE` public-code split lands without
touching any CONTROL.

This is an instrument-readiness verdict only. It is not an implementation verdict, gate
approval or signature, certification, ratification, publication, rename, D-055 assessment
or push authorization. I did not edit CARD.md, `d-claims.py`, production files, historical
reviews or signed packs.

## 1. Exact subject, scope and preservation

I reviewed exact subject `4b104700cfe63aa331381974a640435a99618c74`, tree
`06c77289b9c270175f58dc5cb761faf07097de73`, message `D-CLAIMS: add finite maintained-claim
test instrument`. Its sole parent is A-094 `1e7761be051422ad8091b203df375ddcfb7d1208`.
HEAD was exactly that subject. Tracked `README.md` was dirty and `assets/` / `.serena/`
were untracked in the live worktree; I did not touch, stage or commit any of them. Every
focused run used `/tmp/d-claims.py` (byte-identical copy) against a disposable
`git clone --local --no-hardlinks` of a clean source at `/tmp/d-claims-src.gFE3KZ`.

Parent-to-subject is exactly four added paths, all beneath this `D-CLAIMS-tests/`
directory (517 insertions): `CARD.md`, `d-claims.py`, `RUNBOOK.md`, `RESULTS.md`. No
production byte, existing product test, `scripts/test.sh`, `scripts/check-*.sh`,
maintained claim, decision record, signed pack or prior review moves. `git diff --check`
on the subject is clean. `scripts/test.sh` does not mention `d-claims`. No
`check-claims.sh` / `check-prose.sh` exists.

| Object | Git blob | sha256 |
|---|---|---|
| `d-claims.py` (346 lines) | `50be33e1fa0e3db2bed554b7817ce7a485368960` | `2e409a2e3226899a33994dea8c3c10cf629cf939701902dd2494cae185ab07e0` |
| `CARD.md` | `51cb8f07987070662eef24c7072ca99cf424c0e4` | `d7e5b47202238fbb17a9cde449de2e844b301940e30159858369614187185ca9` |
| `docs/gate-s1-evidence.md` | `66f7b843888cf1eca7d719d0f23c6120969fae30` | `25dcefcade99e9e45be0c482f3dc5141f4d25335a920fabe1012303c7d7caf68` |
| S2 prefix before `## 11. What is NOT in evidence` | — | `470ec1de8ee696a2875334a7873e8e02504ea27d10676cb1a0018668097ba02f` |
| `docs/gate-s2-evidence.md` (whole file) | `baab3e7809a46f22131ef2b609f30af1ed8eeada` | `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589` |
| `scripts/check-suite-floors.sh` | `f8df5ab4db9023b319d872249e10140b635dc152` | `95b65a02bdfc8436e4739b7e5ef90b803964236a86173ed5b8f3c6cc139f7a46` |
| B-EVENTS `SentinelVault.events.t.sol` | `b601b0ad949a6c64b5ab53232fc00a9784e123a0` | `2a9219cc5138858b012b0bc56069490db3dd7d1963b73ccc19c28a48ce2b029e` |
| C-SNAPSHOT `vault.snapshot.classification.test.ts` | `6a00cb9d674a5fe89c0e999149add7e25f7100de` | `29a673560e89b639b6635661706a368454c9969a04c5d37c4f6c15229df3dd8a` |

Independent `git show` at both `4b10470` and `1e7761b` gives the same four frozen hashes
the CARD lists. Live floors at this subject remain `103/550/221/7/78/30`. §11.0 begins
after the S2 prefix mark.

I read the workspace rules, D-058(8)D / D-059(5)–(6) / D-060(1), the failed Batch D
enumerations under `contract/` (evidence, not operative), ADJ2, A-081's D-F* record, the
complete CARD/RUNBOOK/harness, and the five declared surfaces at the baseline. I authored
neither this instrument nor a production repair. Author `RESULTS.md` was not used as
evidence.

## 2. Independent eight-variant reproduction

Dirty live worktree refused (exit 2, `source worktree has tracked changes`). Uppercase
and 39-hex subjects refused (`exact lowercase 40-hex`). Unknown `D_CLAIMS_VARIANT`
refused. Untracked-only source (canary file, porcelain `--untracked-files=no` empty)
ran. Tracked dirt in that clone refused.

Against subject `4b10470`, and again against parent `1e7761b` for `baseline`:

| Variant | Exit | REQUIRED | CONTROL | Completion | Matrix sha256 |
|---|---:|---:|---:|---|---|
| `baseline` (`4b10470`) | 1 | 0/10 | 26/26 | withheld | `482d5603c428ffdd7428fe62999d3609f4f48db6353fc0d37570bab31d0a631d` |
| `baseline` (`1e7761b`) | 1 | 0/10 | 26/26 | withheld | `482d5603c428ffdd7428fe62999d3609f4f48db6353fc0d37570bab31d0a631d` |
| `fix-d6` | 1 | 2/10 | 26/26 | withheld | `fe3bc171db211e924228b046a67d742c06f7158ebea8b0efec55a742aa7af2ec` |
| `fix-all` | 0 | 10/10 | 26/26 | `D_CLAIMS_FOCUSED_COMPLETE` | `23c7c99f583dbcf104ff8c3a4e8f7a9f593a896b419cf56afdd37d3ff9f3eb9f` |
| `break-s1` | 1 | 0/10 | 25/26 | withheld | `5f096067171d841c0626fa8cb436d789711173367b3ac21d2978f120795a7883` |
| `break-s2-prefix` | 1 | 0/10 | 25/26 | withheld | `9d32fa1c49dd24aa06f911b88864ae3055323c91cc869281791ac9f2f8e078b0` |
| `break-floors` | 1 | 0/10 | 25/26 | withheld | `93d836443c0aa8cf21c82c2cb42d372244cba445649d1f3a798e613a62626322` |
| `break-bevents` | 1 | 0/10 | 25/26 | withheld | `14aa81793a0a6d4b1c2ef5aa8a48781353f6ab26b87cac3ff4513a8fa6700d86` |
| `break-d014` | 1 | 0/10 | 25/26 | withheld | `d50d319777affd467abc28fb02614e3881166560fb7a1dad6d8fcc0ca0aa851a` |

`fix-d6` PASSes only `R-D6-absent` and `R-D6-truth`. Each `break-*` fails exactly the
named CONTROL (`C-D1-s1`, `C-D2-prefix`, `C-floors`, `C-B-EVENTS`, `C-D4b-d014`) with
REQUIRED still 0/10. Those counters are from the reproduced matrices, not from
`RESULTS.md`. Clone HEAD matched the requested 40-hex on every successful run.

## 3. Defects

### 3.1 FAIL — D-F1's load-bearing BLOCKER half is unobserved

A-081 recorded D-F1 as: the packet §7 BLOCKER states the verifier *"does not"* compare
*and* *"under C1 condition 4 this alone blocks exit"*, while the packet's own test
returns 2. *"a false BLOCKER in §7 would corrupt the exit assessment itself."* CARD §5
REQUIRED only `; it does not.` and the frozen `D1_TRUTH` phrase.

After the harness `fix-all` replacement, wrap-normalized BLOCKER 1 still contains both
of:

- `This item is not a current exit blocker.`
- `Under C1 condition 4 this alone blocks exit.`

The item remains under `**BLOCKERS — exit cannot be reached while these stand:**`.
Measured: `fix-all` is 10/10 REQUIRED, 26/26 CONTROL, exit 0, completion token printed.
An `/tmp` sibling that then deletes only the `this alone blocks exit` sentence is still
10/10 and 26/26. A wrap-aware independent CARD-phrase repair (strike + `D1_TRUTH`, no
harness `D1_NEW` surrounding prose) is also 10/10 and 26/26 and still carries
`this alone blocks exit`.

The semicolon-phrase strike itself is not a false positive: wrap-norm of
`; ~~it does not.~~` does **not** contain `; it does not.` `R-D1-absent` PASSes for the
right reason. What it does not observe is the half A-081 called load-bearing.

### 3.2 FAIL — D-F2's second named site is inverted into a CONTROL, and the D-09 fact is not REQUIRED

v1/v2 D-F2 named two repairs in §11.0: the derivation that computes to five, and
`"FIVE OF THESE TEN ARE NO LONGER ACCEPTED LIMITS"` (only four entries were wholly
removed because `D-09` is in both sets). A-081 failed A-080(2) on both, and on the
missing D-09 fact.

Live at this subject, line 552 is unstruck:

```text
**FIVE OF THESE TEN ARE NO LONGER ACCEPTED LIMITS — THEY ARE FIXED (A-076, 2026-08-18, under
```

No `~~` wraps that heading. The later "What remains accepted here is five" *is* struck.
`C-D2-struck` is named "struck five-of-ten sentence remains" but the scored check is only
`"FIVE OF THESE TEN ARE NO LONGER ACCEPTED LIMITS" in s2_n` — it does not test strike
marks (`C-A080` does, for `~~"COMPLETE THROUGH REVERIFICATION"~~`).

Measured `/tmp` siblings against the same clean `4b10470` clone:

| Sibling | REQUIRED | CONTROL | What moved |
|---|---:|---:|---|
| replace FIVE→FOUR wholly-removed wording | 0/10 | 25/26 | exactly `C-D2-struck` FAIL |
| wrap the heading in `~~` without changing words | 0/10 | 26/26 | CONTROL still PASS |
| `fix-all` / independent CARD D2 | 10/10 | 26/26 | heading remains live and unstruck |

A truthful D-F2 repair of the second named site therefore fails a CONTROL. Leaving the
false heading live greets COMPLETE.

Separately, CARD's frozen `D2_TRUTH` includes *"`D-09` is in both the fixed and accepted
sets"*. `R-D2-truth` only searches for `Ten minus four wholly-removed entries is six`.
The wrap-aware independent CARD sibling wrote only that short fragment, omitted D-09,
and still greened 10/10. A-081 called D-09-in-both-sets *"the one fact that makes SIX
right and which §11.0 states NOWHERE."* The oracle does not require it.

`C-D2-packet-ten` locks `The ten §11.0 accepted limits` in the current §7 NON-BLOCKERS
list. Packet §3 of the same file already reads `~~Ten~~ **SIX**`. That NON-BLOCKER is
present-tense exit guidance, not a dated decision entry. Independent CARD repair keeps
it and still COMPLETE.

### 3.3 FAIL — forbidden public reason-code split is not controlled

CARD §2 forbids new public reason codes and splitting `SIGNER_CHAIN_UNSTABLE`
(D-057(4); D-F6). `C-D6-no-detail` does observe a `detail` field on `RefusalRecord`.
`C-D6-fatal` only checks `SIGNER_CHAIN_UNSTABLE: "FATAL"` remains. Nothing observes
enum growth.

`/tmp` sibling: harness `apply_all` plus

```text
SIGNER_CHAIN_PENDING_HEAD: "FATAL",
```

inserted beside `SIGNER_CHAIN_UNSTABLE` in `REASON_SEVERITY`. Measured **10/10 REQUIRED,
26/26 CONTROL, `complete=True`**. `D-057(4)` and `No reason-code split` remain as
comment text, so `C-D6-d057` still PASSes. A repairer can ship the exact forbidden D-F6
product change, copy the frozen truth phrases, and receive the completion token.

Signer-side E4 *comment* erasure is controlled (`break-d014` / `C-D4b-d014`). Adding a
public code is not.

## 4. Attacks that did not fail the instrument

These were run. They are not grounds for this FAIL, and they do not cancel §3.

- **D1 strike false-positive.** `; it does not.` is not a substring of `; ~~it does not.~~`
  after wrap-norm.
- **D2 wrap.** Live sentence is `Ten minus the five` / `fixed leaves six` across a newline.
  Line grep for the joined phrase is false; wrap-norm is true. `R-D2-absent` FAILs at
  baseline, so the scored check is wrap-norm, not a line grep.
- **comment-star wrap.** `Both are open (v1.1 register)` is absent from raw wrap-norm of
  `decode/index.ts` and present after `^\s*\*` strip. After `fix-all`, both `D4B_TRUTH`
  fragments are absent from wrap-only and present after strip. Baseline `R-D4b-open` FAIL
  proves the strip is load-bearing, not fake.
- **Signed-pack leak.** `D2_FALSE` is not in the S2 prefix. `fix-all` and independent CARD
  D2 leave S1 sha256 `25dcefcade…` and the prefix hash `470ec1de8e…`. `break-s1` /
  `break-s2-prefix` fail only those CONTROLS.
- **Historical quotes.** After `fix-all`, v3 still contains `so the refusal detail now
  distinguishes them` and ADJ2 still contains `Both are open (v1.1 register)`. REQUIRED
  D4a/D6/D4b are surface-scoped. A-077 still contains `the detail now distinguishes them`;
  `C-A077` only requires the heading, which is the D-059(6) historical treatment.
- **Second checker / gate wiring.** The subject adds none. Planting `scripts/check-claims.sh`
  fails `C-no-second-checker`. Appending `d-claims` to `test.sh` fails `C-no-gate-wire`.
- **`RefusalRecord.detail`.** Adding `detail?: string` fails exactly `C-D6-no-detail`.
- **CONTROL over-reach on a CARD-phrase repair.** Wrap-aware independent replacements of
  the five CARD false strings with the frozen truth fragments (keeping `(a)`/`(b)`,
  `D-057(4)`, `EVAL_TARGET_BOUND`, the D-014 sentence, §3b, S1/S2 prefix, B/C hashes)
  scored 10/10 and 26/26. No CONTROL failed. A truthful *paraphrase* that does not copy
  the frozen phrases scored 5/10 REQUIRED and 26/26 CONTROL (the five `*-truth` rows plus
  `R-D4b-open`, as intended).
- **Preflight / identity / completion.** Exact 40-hex, clone HEAD match, dirty source
  refused, completion withheld on baseline 0/10.
- **HANDOFF / session-state "NO SUBSEQUENT BATCH HAS BEGUN".** CARD names the HANDOFF
  phrase as a residual and puts a full `session-state.md` rewrite outside the card.
  HANDOFF has the phrase only wrap-split; `docs/session-state.md:209` has it contiguous
  in §1. That is a stale current instruction, but it is not a silent drop of a declared
  D-F1/F2/F4/F6 theme, and D-060(1) assesses completeness inside the declared five-file
  boundary. I do not add it as a numbered defect.
- **session-state "ten accepted as documented limits".** Present under a dated 2026-08-19
  heading, with "six remain accepted today" later in the same section. CARD gives the
  D-058(8)D historical disposition v2 F12 required. I do not FAIL that inversion.

D-F3 as Batch A / D-F5 as no second checker match D-059(5). No gate harness is present,
so D-059(7) is N/A as claimed.

## 5. What I did not run

I did not launch Foundry, the TypeScript suite, the verifier, `scripts/test.sh` as a
gate, `a-floors-gate.py`, or `scripts/check-suite-floors.sh` as a process. Floor
constants were read from `scripts/test.sh` at the subject (`FOUNDRY_MIN_TESTS=103`,
`TS_MIN_TESTS=550`) and `C-floors` PASSed in every non-`break-floors` variant. Attack
harnesses, clones and matrices stayed in `/tmp`.

## 6. Limits

This review establishes that the eight committed variants discriminate as labelled, that
wrap-norm and comment-star stripping are the scored Markdown/TypeScript checks, and that
three instrument defects remain: an unobserved load-bearing D-F1 BLOCKER sentence, a
D-F2 site inverted into a CONTROL that punishes a truthful count correction while
`R-D2-truth` omits the D-09 fact, and an uncontrolled public reason-code split that still
prints the completion token. It does not establish general prose consistency,
implementation correctness, a gate outcome, historical factual truth, certification,
signing, publication or D-055 closure.

**FAIL.** Do not hold this instrument. Do not start a product repair against it.
