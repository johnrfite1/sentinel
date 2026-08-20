# BATCH CARD A-EXTRACT — named-scope extraction, exact membership, and uniqueness

**Authority:** D-058(1) (test-first separation), D-058(6) (no generic prose checker; a
line-oriented grep is DISALLOWED for a Markdown paragraph check), D-059(2) (a sibling
enumeration identifies candidates and does not adjudicate them), D-059(8) (section extraction
and source uniqueness are TWO properties, not one primitive), D-060(1) (batch cards;
completeness is asserted only inside a declared boundary).

**Pre-repair base SHA:** `bb664c626d592d86391f644bf014e76f2bbf7db4`, tree clean.
**Demonstrated at:** the same commit. **Harness:** `a-extract.sh` (its own sha256 is printed by
preflight case `P0` and recorded in `RESULTS.md`).

**This card is small on purpose. It claims completeness ONLY inside the boundary below.** It is
**not** a Batch A1 attempt of any kind. **Batch A1 is CLOSED** — both ordinary attempts remain
FAILED, the D-062 containment exception closed one named regression, and **nothing here reopens
any A1 finding, residual, or harness.** The name `A-EXTRACT` is used precisely because `A2`
already identifies frozen attempt-two evidence.

**This is a test-only deliverable.** No production file is modified by this card, by its harness,
or by the commit that carries it. `TESTS.patch` is supplied as a patch file and is **NOT
applied**.

## THE INVARIANT — one

> **A checker naming a section, publication, or identifier must inspect that exact scope and
> require the exact value. It must not pass through a prefix, outside-section decoy, duplicate
> publication, incorrect heading boundary, or first-match tie-break.**

Two things make this a real invariant here rather than a slogan. **The proposal's section order
is not monotonic** — `§5.9` precedes `§5.8`, which precedes `§5.7` — so "the first match" is
routinely not "the real one". And **the same `####` heading depth must mean opposite things at
the two anchors**: inside `§5.8` (a `###` anchor) it is a subsection that stays IN, and at
`§5.7.1` (a `####` anchor) it is a sibling that ENDS the section. A fixed `#{1,4}` terminator
class cannot be right for both, which is why heading depth must be derived from the anchor.

## BOUNDARY — four consumers, and only three kinds of block inside them

| Tag | File | The blocks in scope |
|---|---|---|
| **TS** | `scripts/check-type-strings.sh` | the `§5.8` `awk` extraction; the per-type publication-uniqueness test (`spec_hits`); the `§5.8` publication lookup; the `eip712.ts` source-definition lookup |
| **EC** | `scripts/check-eval-codes.sh` | the `§5.7.1` `awk` extraction; the per-code membership test (`grep -q "$code"`) |
| **VH** | `scripts/check-vendor-honesty.sh` | the `§7.2` caveat extraction (`CAVEAT=…`) and its comparison against `docs/ablation-report.md`, including `norm()` |
| **VP** | `verifier/test_verifier.py` | `TestPublishedTypeStrings` — the `§5.8` consumer only |

**Fixture files the cases mutate** (never in the repository under test; only in private
snapshots): `Sentinel_Protocol_Lab_Proposal_v0_2.md`, `ts/src/signer/eip712.ts`,
`docs/ablation-report.md`.

**Explicitly OUTSIDE this boundary and untouched:** every other block of those four files —
the repository-identity preamble, the git-environment scrubbing, the vendor-name scan, the
`§10.1` label scan, the `§13` marker census, `EVAL_CODES` parsing, and every other test class in
`test_verifier.py`. Every other script. Floors, vault events, signer state, maintained-claim
repairs, signed text, D-055, D-016, publication. **`docs/gate-s2-evidence.md` is not read,
quoted, or proposed for change by this card.**

## TEST MATRIX — fourteen cases, all required

| # | Case | Consumers | Required behaviour |
|---|---|---|---|
| 1 | the named section is **ABSENT** | TS, EC, VP | **refuse, naming the section.** No result for a scope that could not be found, and no fallback to the whole document |
| 2 | the exact value is **absent but a prefix-sharing value exists** | EC, TS | **exact membership.** A token of which the required value is a proper prefix is a different token |
| 3 | the value is present **only OUTSIDE** the named section | EC, TS | the value must be reported absent, in **both directions of the file** |
| 4 | an **outside-section decoy BEFORE** the real section | TS, EC | **refuse the ambiguity**; never a first-match tie-break, and never a success report |
| 5 | **duplicate normative publication inside the section, in BOTH orders** | TS | **refuse**, naming the type. There is no correct way to choose |
| 6 | **duplicate authoritative definition in the SOURCE, in BOTH orders** | TS | **refuse**, naming the duplicate definition — not "drift", and not success |
| 7 | a **deeper subsection stays INSIDE** its parent | TS, EC | `#### 5.8.1` does not truncate `§5.8`; `##### 5.7.1.1` does not truncate `§5.7.1` |
| 8 | a **same-depth or shallower heading ENDS** the section | TS, EC | and the depth is **relative to the anchor** — see 7a/8c |
| 9 | a **prose or backticked mention is NOT a publication** | TS | the verdict is unchanged and no duplicate refusal is raised |
| 10 | the **`§7.2` caveat comes from `§7.2` itself** | VH | not from the first tree-wide match, in **both the false-fail and the false-pass direction** |
| 11 | the **generated ablation report carries the exact caveat** | VH | and the comparison is over **logical paragraphs**, on the proposal side as well as the report side |
| 12 | **a ONE-CHARACTER prefix substitution is rejected** | EC | appended or prepended; one character makes a different identifier |
| 13 | the **verifier `§5.8` consumer AGREES with the shell guard** | VP + TS | on section extent and on duplicate handling |
| 14 | **Gate 5's certified `§2` table and its pinned hash are unchanged** | VH | a control that must hold **before and after** any repair |

### What each case asserts, in the harness's own case ids

- **1a / 1b / 1c** — TS and EC refuse by name; VP does not report success.
- **2a** (EC, `EVAL_POLICY_WINDOW` vs `EVAL_POLICY_WINDOW_STRICT`), **2b** (TS,
  `PolicyPayload` vs `PolicyPayloadV2`).
- **3a** (EC, code moved to `§6`, later in the file), **3b** (TS, publication moved to `§5.6`).
- **4a** correct decoy earlier in `§5.9`, real `§5.8` transposed → must report the drift.
  **4c** two complete `§5.8` sections → must refuse. **4d** the FIRST `§5.8` correct, the real
  one transposed → **must not report success**. **4b** the same shape at `§5.7.1`.
- **5before / 5after** — duplicate publication either side of the real line.
- **6before / 6after** — duplicate source definition either side of the real one.
- **7a** `####` inside `§5.8` (must stay in), **7b** `#####` inside `§5.7.1` (must stay in),
  **7c** `#####` inside `§5.8` — a CONTROL, because it already stays in.
- **8a** `###` inside `§5.8`, **8b** `##` inside `§5.8`, **8c** `####` inside `§5.7.1`,
  **8d** `###` inside `§5.7.1`. **8c against 7a is the anchor-derivation evidence**: the same
  `####` depth, opposite required outcomes.
- **9a** inline backticked mention, **9b** indented backticked line, **9c** CONTROL — the same
  text unbackticked IS a publication and is refused.
- **10a** decoy earlier, `§7.2` intact → must report ok. **10b** decoy earlier matching the
  report while `§7.2`'s own wording is absent from it → **must FAIL naming the report**.
- **11a** base commit, **11b** `§7.2`'s caveat hard-wrapped → must still be located,
  **11c/11d** controls, **11e/11f** the generator emits it.
- **12suffix / 12prefix** — `EVAL_NONCE_CURRENTX` and `XEVAL_NONCE_CURRENT`.
- **13a** deeper subsection, **13b-before / 13b-after** duplicate publication, **13d** a
  horizontal rule inside `§5.8`. `TESTS.patch` carries the verifier-side half.
- **14a–14c** controls on the snapshot, **14d** the live repository is unchanged.

## CONTROLS — each case has an opposite outcome, or it proves nothing

- **Every mutation proves it applied.** Each `*-mut` control counts the fixture before and
  after — anchors present/absent, exact-token vs substring hits, decoy line number against the
  real one, publications above and below an interposed heading. A probe whose mutation silently
  failed reads exactly like a pass, and this harness has already caught that in itself: an
  `awk -v` carrying a newline errored to stderr, the mutation did not apply, and case `11b`
  reported PASS against an unmutated fixture until the `*-mut` control was added.
- **`1-ctl`, `5-ctl`, `6-ctl`, `8-ctl`, `10-ctl`, `13-ctl`** — the unmutated snapshot, where
  every consumer reports success. Nothing here is satisfiable by a checker that always fails.
- **`2-ctl`, `12-ctl`** — the identifier removed outright, where EC *does* name it missing. So
  the reporting path is live and `2a`/`12*` are about the matching rule, not about plumbing.
- **`7c` against `7a`** — the SAME insertion at a deeper heading level already passes, so `7a`
  is about depth and not about headings in general.
- **`9c` against `9a`/`9b`** — the identical text as an unbackticked literal IS refused, so
  `9a`/`9b` do not pass because the fixture is inert.
- **`11c`, `11d`** — the report's copy altered by one word FAILS, and a pure re-wrap of the
  report does not. `11b` is therefore about the **proposal** side of the comparison.
- **`14c`** — a `§2` edit makes the pinned hash report STALE, so case 14 is not vacuous.
- **`Z-*`** — the four consumers are byte-identical to the base SHA at run time, and the
  repository under test is unmodified when the run ends.

**A failing CONTROL exits 2 and invalidates every verdict beside it.** A failing REQUIRED with
all controls holding exits 1. **Exit status alone is never a per-case discriminator:** three of
the four consumers exit 1 for every finding they have, so every assertion here is on OUTPUT —
the success line absent, and the finding NAMED.

**Refusal wording is matched as a set of alternatives, never as one dictated sentence.** The
repair chooses its words; it may not choose silence, success, or a message about something else.

## EXCLUSIONS

- **No implementation is proposed.** Every assertion is on behaviour: what is reported, what is
  refused, what is named. Nothing asserts how a consumer extracts a section.
- **No generic prose-consistency checker is proposed or tested** (D-058(6)). Every probe is
  aimed at a named canonical fact: six type strings, forty-one identifiers, one `§7.2` sentence,
  one `§2` table hash.
- **Batch A1 is not reopened.** No A1 test, no A1 production change, no relabelling of either
  attempt.
- **Gate 5 is neither revoked, reaffirmed nor recertified** (D-059(1)). Case 14 asserts only
  that this batch leaves the certified table and its pin exactly where they were.
- **`R2` (quotePath), `R3`, `R5`** and every other deferred item stay deferred.
- One platform, one git, one python. See `COVERAGE.md` §2.

## STOPPING RULE

**This batch STOPS at the independent test checkpoint.** The tests are demonstrated failing for
their intended pre-repair reasons with every control discriminating; the harness, this card,
`COVERAGE.md`, `RESULTS.md` and `TESTS.patch` are committed; **John reviews before any
implementation begins.**

Thereafter D-058(9): **at most two implementation attempts** against this fixed contract. **The
implementer may not modify, weaken, relocate or delete this harness or `TESTS.patch`**
(D-058(1)). If a case here is believed invalid, the implementation **STOPS** and has the
invalidity independently confirmed before anything changes. A failure in this batch does not
authorize widening another.
