# V5 — REPORT

**Reviewer:** V5, independent verifier. I did not write any of the documentation below and have
no stake in it holding.
**Frozen commit:** `c8d15a76425544148d7da2f8fa0c003feb6ad2b7` — confirmed with `git rev-parse
HEAD` in the V5 worktree before any other command.
**Scope:** the three documentation corrections made in that commit itself (`A-080`).
**Method note:** the commit message's account of what it did was treated as a claim to be
checked, not as evidence.

| # | Item | Verdict |
|---|---|---|
| 1 | The accepted-limit count is consistently SIX | **FAIL** |
| 2 | The rejected hash/recheck design is unmistakably rejected | **HOLD** |
| 3 | `docs/session-state.md` is a truthful current handoff | **FAIL** |

Both failures are **incompleteness of a correction that is right about its headline number**.
Neither is a case of the corrected fact being wrong. That distinction matters for what is owed
next, and I have kept it explicit throughout.

---

# ITEM 1 — the accepted-limit count · **FAIL**

## The general property, stated before I looked at the fix

Every reader-facing surface that says how many findings are currently accepted as documented
limits must say the same number, that number must be derivable from the underlying record, and
the derivation a reader is pointed at must actually produce it.

## What holds

**SIX is the correct number, and I derived it independently two ways without relying on any
document's assertion of it.**

**Derivation A — from `docs/v1-1-register.md` §13.4**, the status table the brief names as
authoritative. Parsing the status column mechanically (P1.1) gives exactly six rows carrying
ACCEPTED: `D-07`, `D-09`, `E5`, `F-VAULT-4`, `F-VAULT-5`, `G-3`. The table has 24 data rows,
matching its own claim of 24 leads. My parser was falsified (P1.2): mutating `G-3`'s status
moved the count to 5, and the worktree was restored clean.

**Derivation B — from §11.0's own roster.** The ten accepted entries are `D-07 D-09 D-10 E5
F-VAULT-4 F-VAULT-5 G-3 G-5 H-5 H-8` (ten bullets, counted mechanically). A-076 recorded five
repairs. Four of them remove a whole entry. The fifth, `D-09(c)`, removes only part of `D-09`,
which stays accepted on (a),(b). **Ten entries minus four fully-removed entries = SIX.**

Both derivations agree with each other and with §11.0's asserted six-item list, `G-3` included.

Also holding:

- **The stale `nine` is struck and replaced** — `silently restating it as ~~nine~~ **six**`
  (§11.0 l.522). No stale nine survives anywhere (P1.7).
- **CONTROL PASSES: history was not flattened** (P1.8). D-051(b)'s own "THE NINE LOW AND ONE INFO
  BECOME DOCUMENTED LIMITS" is intact — and is the origin of the ten. The A-075-era statements of
  ten in `docs/decisions.md`, and the labelled 2026-08-18 snapshot prose in `docs/v1-1-register.md`
  §13.4, are intact and correctly not marked as errors. `git show --stat HEAD` touches six files,
  **none under `docs/review-…/`**; every reviewer and adjudication artifact is byte-identical.
- `docs/exit-criterion-packet.md` §3 corrected to `~~Ten~~ **SIX**` with the six named.
- `HANDOFF.md` and `README.md` carry no copy of the count (controlled zero, P1.9).

## FAILURE 1 — the authoritative derivation does not compute, on any of four surfaces

The brief asked me to check the arithmetic myself. **It does not work as written anywhere.**

| Surface | Text as it stands | What a reader gets |
|---|---|---|
| `docs/gate-s2-evidence.md` §11.0 l.513 | "Ten minus the five fixed leaves six, not five." | **five** |
| `docs/gate-s2-evidence.md` §11.0 l.548 | "**FIVE OF THESE TEN ARE NO LONGER ACCEPTED LIMITS**" (unstruck, bolded) | **five remain** |
| `docs/exit-criterion-packet.md` §3 l.95 | "D-051(b) accepted ten; **A-076 FIXED five**" | **five** |
| `docs/decisions.md` A-080 l.248 | "ten accepted, five FIXED by A-076, `G-3` never in D-056(a)'s scope, therefore **SIX**" | **five** |

`G-3` was never fixed, so it was already inside the remainder — naming it cannot supply the
missing one. **The single fact that makes SIX correct — that `D-09` is simultaneously in the
fixed set and the accepted set, so five repairs removed only four entries — is stated on no
surface.**

Line 548 is independently false, not merely unhelpful: `D-09` is one of "these ten" and **is**
still an accepted limit, so **four** of the ten, not five, are no longer accepted limits. This is
a live, unstruck, bolded false count statement inside the subsection whose entire subject is a
wrong count — the same structural position as the sentence A-080 struck thirty lines above it.

**Root cause, found mechanically (P1.5).** §13.4's `D-09` cell reads `**FIXED (A-076)** — … (a),(b)
remain ACCEPTED`. A reader counting rows *marked* ACCEPTED gets **five**; only a reader who reads
every cell to its end gets **six**. The authoritative table itself yields the wrong number to the
obvious reading, which is why every prose ledger lands on "ten minus five".

## FAILURE 2 — a third, uncorrected present-tense "ten accepted" in `docs/session-state.md`

The commit message claims it corrected "`session-state.md`'s two copies". The diff confirms
exactly two were corrected. **A third survives, untouched (P3.4):**

> `docs/session-state.md` l.151-153
> **WHERE THE PROJECT STANDS, 2026-08-19.** Round five (51 findings, 2 CRITICAL) is fully
> adjudicated and remediated: three live security defects fixed, nine MEDIUMs fixed, **ten accepted
> as documented limits**, two design forks with John.

`git show HEAD -- docs/session-state.md | grep -c "ten accepted as documented limits"` → **0**.
Written 2026-08-18; the heading's date was carried to 2026-08-19, the count was not.

**Why this is a defect and not preserved history:** the near-identical phrase *"Ten findings
accepted as documented limits"* in `docs/exit-criterion-packet.md` §3 **was** struck to
`~~Ten~~ **SIX**` in this very commit. The author's own standard was applied to the sibling and
missed here — under a present-tense heading dated today, in the file that opens by declaring
itself the project's memory.

**Why it survived:** the phrase straddles a line break (`ten accepted` / `as documented limits`),
so a line-based grep for it returns a clean-looking zero. It was found only with the
wrap-tolerant searcher validated at P0.4. **This is the third defect this repository's hard
wrapping has hidden from a reviewer.**

## Verdict — Item 1: **FAIL**

The number is right and the historical control passes. But of the brief's four requirements, two
fail: the one authoritative derivation does not produce its own answer and carries a live
unstruck false statement (l.548), and the sibling surfaces do not agree (`docs/session-state.md`
still states ten as current). This is the project's named failure mode — the exact sentence a
reviewer quoted was struck, and the identical error one file and thirty lines away was not.

---

# ITEM 2 — the rejected hash/recheck design · **HOLD**

## The general property, stated before I looked at the fix

Nowhere in the tree does the hash-at-start/recheck-at-exit design read as something to build, and
the design that replaced it survives with its limits intact.

## Cold read of §13.6 — the brief's central question

I read `docs/v1-1-register.md` §13.6 top to bottom before reading the commit message's account of
it. **I would come away certain that design is rejected and must not be built.** Three things do
that work, and any one would be close to sufficient:

1. The prescription is struck through: `~~**have the gate hash its own file at start and re-check
   at exit…** Roughly four lines.~~`
2. The next line is `**THE STRUCK SENTENCE DIRECTLY ABOVE IS THE REJECTED DESIGN. DO NOT BUILD
   IT.**`, carrying John's reason in his own words and the generalisation that a guard inside the
   mutable body is the code the attack makes unreachable.
3. Twenty lines later the referent is disambiguated by quotation, not just position: the rejected
   design is *"the struck 'hash at start, re-check at exit' prescription above — NOT the struck
   'not built, deliberately' note beside it, which is merely spent."*

**The warning points at the right text.** Two struck spans exist in §13.6; the warning names its
target both positionally and by quotation. There is no ambiguity about which is which.

## The adopted design and its residual

**Preserved and legible (P2.3).** All six elements the brief lists are present in §13.6 item 4:
copy, open read-only, unlink so it has no pathname, execute as `/dev/fd/N`, external supervisor
requiring a completion token, and exit 0 alone not being success.

**Verified against the code, not the prose (P2.4).** `scripts/test.sh` implements each element as
described — `exec 9<"$_gate_tmp"; rm -f "$_gate_tmp"`, `bash /dev/fd/9`, and an explicit
`if [ "$_gate_seen" != "$_gate_token" ]; then … exit 5`.

**The threat-model residual is present and accurate (P2.5).** §13.6 item 5 states that a
same-user actor able to READ the executing body's environment can forge the completion token, and
that the nonce defends against corruption rather than environment access. Checked against **both**
sources the brief names:

- **A-077's own text** (`docs/decisions.md` l.245) says the same thing in the same terms — same
  actor, same capability, same explicit non-defence. It is faithful, not a drifting paraphrase.
- **The code** confirms the mechanism: the token is passed to the body *in the environment*
  (`SENTINEL_GATE_TOKEN="$_gate_token" bash /dev/fd/9 …`), and the body's first act is
  `unset SENTINEL_GATE_TOKEN`. The residual is accurate and, if anything, conservative.

**Falsified with a working control (P2.6).** `scripts/check-gate-immutability.sh` ran 10/10, and
critically **its own unprotected control was corrupted (exit 127)** — so the protected subject's
survival is a measurement, not a vacuous pass. Probe 5 independently demonstrated the
completion-token refusal (exit 5). I read the output, not the status.

**Both script headers are clean (P2.7).** `scripts/test.sh` l.23 and
`scripts/check-gate-immutability.sh` l.10 each list the hash/recheck design under an explicit
"designs that failed / were rejected" heading, with the reason. Neither recommends it. The
immutability guard's header additionally carries the environment-read residual itself.

## Verdict — Item 2: **HOLD**

All five of the brief's requirements are met, and the load-bearing ones were checked against the
code and against a live falsification rather than against the document's own account.

---

# ITEM 3 — `docs/session-state.md` as a truthful handoff · **FAIL**

## The general property, stated before I looked at the fix

A fresh instance reading only this file forms a picture of the project no more finished,
complete, or verified than the tree actually is — **including its numbers.**

## What holds — and the narrative half holds well

**All seven required facts are stated plainly (P3.1)**, all within the first 25 lines, under a
heading ordering the reader to read them before any other line. Verified against `git log` rather
than against the file (P3.2): `497d1ce` (A-077, the repair), `8990255` (A-078, the reverification
that returned three FAILED, and the commit carrying the corrections), `254db64` (A-079), HEAD.

**The blanket claims are gone (P3.3).** "Every repair has been INDEPENDENTLY REVERIFIED" and
"THERE IS NO AGENT WORK OUTSTANDING" survive only as quotations immediately labelled false. l.46
states outright: `"no agent work outstanding" is NOT true`. `HANDOFF.md` strikes "COMPLETE
THROUGH REVERIFICATION". No surviving blanket assertion.

**Push status is dated, accurate, and verified against the ref (P3.5).**
`git rev-parse origin/step-3/isolated-signer` → `254db64`, exactly as the file says, with only
the frozen commit local. Framed as a dated checkpoint fact, with backup-is-not-publication stated
twice.

**No hard-coded ahead/behind count (P3.6)** — and this requirement is met unusually well: the
file replaces the number with the command that derives it.

## CONTROL — the cold read, and it PASSES (P3.9)

A separate instance with no context, no repository access and no knowledge of this review was
given only `docs/session-state.md`. Its conclusions:

- Verification status: **"PARTLY"** — quoting the header, the five-step sequence, and the state
  table. Exactly the true sequence.
- Outstanding agent work: **yes**, correctly noting it is gated behind John's authorisation, and
  quoting `"no agent work outstanding" is NOT true`.
- Push: through `254db64` on 2026-08-19, backup not publication, D-016 unrelaxed. Correct.
- Finished rating: **6/10**, reasoning that "the unverified part is exactly the part that fixes
  repairs which *already failed once*."

**The handoff does NOT overclaim.** The cold reader's picture is if anything *more* cautious than
the true sequence. The brief's stated FAIL trigger for this control did not fire. Credit where
due: the narrative repair is genuine and effective.

## FAILURE — the numbers, which are the half the brief asks about at point 5

The cold reader, unprompted, flagged the file for leaking numbers it told him not to trust — and
found a contradiction I had not. Both check out.

**(a) Two false self-descriptions, six and eight lines apart.** §3 l.346 claims *"**The figures
are no longer duplicated here.** The gate constants are the only copy"*; l.358 claims *"**THE
FLOOR VALUES ARE DELIBERATELY NOT REPRINTED HERE.**"* Between them, l.350-351 reprints
`7 samples · 78 tamper cases over 30 modes`.

I did not assume these were gate constants — I read them off the gate (P3.7):

```
$ ./scripts/check-suite-floors.sh
  VERIFIER_MIN_SAMPLES       7
  VERIFIER_MIN_TAMPER        78
  VERIFIER_MIN_TAMPER_MODES  30
suite floors: read from scripts/test.sh, which is the only copy.
```

Three of the six gate floor constants, reprinted verbatim between two statements that they are
not. **Both statements are false as written.** The file's own header (l.77) says `DO NOT QUOTE
THE SUITE COUNTS IN §3` — an instruction presupposing §3 contains them, contradicting both.

**(b) A fourth statement, and this one is STALE, not merely duplicated.** `docs/session-state.md`
l.456, live, bolded, unstruck, present tense:

> **D-010 verifier: 7 samples, 77 tamper cases over 29 modes, 160 tests — and all four are FLOORS
> the gate asserts.**

Against the actual constants: samples 7 correct; tamper **77 vs 78** wrong; modes **29 vs 30**
wrong; tests **160 vs 209** wrong. **Three of the four asserted floors are wrong**, and the line
contradicts l.351 in the same file and the same section. Its own parenthetical records that it
was corrected in round five as "a fourth staleness in this file" — the correction has since gone
stale again.

This is precisely the `R4-F4` defect class — *one copy removed, another left in the same section,
below the sentence claiming they were no longer duplicated* — recurring in the same section of
the same file that describes `R4-F4` at l.280.

**Control (P3.8):** not everything in that sentence is wrong. "50 corpus fixtures" is **correct**
(50 `F0xx` fixtures + one digest index = the 51 files on disk), and `FOUNDRY_MIN_TESTS` /
`TS_MIN_TESTS` are correctly *not* reprinted. The defect is specific and bounded, not a general
sloppiness — which is what makes it a real finding rather than an impression.

**In fairness to A-080:** its hunks end at line 259 and **it never touched §3** (P3.7). It did
not introduce these and did not claim to fix them. But the brief asks whether the file *is* a
truthful current handoff, and a file asserting four gate floors of which three are wrong, under
two claims that it asserts none, is not one.

## Verdict — Item 3: **FAIL**

Requirements 1, 2, 3, 4 and the control (6) all hold, and the narrative repair is genuinely good.
Requirement 5 fails: counts are duplicated rather than pointed at the canonical source, under two
explicit false claims that they are not, and one of the duplicates is materially stale.

---

# RESIDUALS — real limits I am recording, NOT failures

1. **`docs/decisions.md` A-075 (l.241) still describes the rejected design affirmatively** —
   *"A mechanical guard is possible and is NOT built: the gate could stamp its own file's hash at
   start and re-check it at the end…"* — unstruck and unannotated in its own paragraph. Mitigated:
   it is a dated append-only ledger entry, the rejection is recorded in the two entries
   immediately following, and the sentence points the reader at `docs/v1-1-register.md`, where the
   design is now struck. Not a failure; the pointer leads to the rejection.
2. **§13.6's lead-in clause is unstruck** — *"there is a cheap mechanical one:"* introduces only
   the struck, rejected prescription. The bolded `DO NOT BUILD IT` on the next line resolves it,
   and the adopted design genuinely *is* a mechanical defence, so the sentence is not false.
3. **`docs/decisions.md` A-076 (l.243) carries its "TEN to FIVE" statement unstruck**, corrected
   by an adjacent bracketed bold annotation rather than by strikethrough. Consistent with the
   commit's stated approach ("annotated in place"), and unambiguous in context.
4. **Nothing mechanical asserts the accepted-limit count.** It is hand-maintained across five
   surfaces with no guard, no script, and no test. §13.4's own text warns "nothing mechanical
   asserts it". Given this count has now been wrong four distinct ways, a check that derives it
   from §13.4 would convert a recurring defect into an impossible one. **This is a suggestion for
   John, not a decision I am making or implying.**
5. **The A-077(b) environment-read residual remains open**, correctly declared in §13.6, in
   `docs/decisions.md` A-077, and in the immutability guard's own header. This review did not
   close it and could not.

---

# NEW CONCERN — outside my three items, raised because the COMMON BRIEF asks for it

`docs/session-state.md` l.456-461 states that the **same stale trio is still printed by
`scripts/test.sh` itself**, in a COVERAGE BOUNDARY block labelled "ALL THREE FIGURES ARE FLOORS
THIS RUN ASSERTS", beside floors of 160/7/77/29 — and says *"That one is CODE and is NOT fixed:
it is unscoped remediation awaiting John, register §13."* I did not verify the code block myself;
it is outside my scope and belongs to whoever holds the gate-script surface. **Flagging it because
the same three stale numbers now appear in at least two places, one of them executable, and my
Item 3 evidence establishes the documentation half independently.**

---

# QUESTIONS FOR JOHN — recorded, not answered

1. Should the §11.0 derivation state explicitly that `D-09` is partially fixed and partially
   accepted, so that "ten minus five leaves six" becomes arithmetic a reader can follow? An agent
   should not rewrite a signed-adjacent evidence subsection on its own initiative.
2. Is `docs/session-state.md` l.152's "ten accepted as documented limits" to be struck to SIX
   like its sibling in `docs/exit-criterion-packet.md`, or preserved as round-five history?
3. Do the §3 floor figures come out of `docs/session-state.md` entirely, or does the file drop
   its claim that they are not reprinted? Both are defensible; choosing is not mine.
