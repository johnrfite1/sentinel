# A1 — CASE 4 CORRECTION: MEASURED EVIDENCE, BOTH DIRECTIONS

**Author:** an independent test author. It wrote neither the harness nor the implementation
under it, repaired nothing, committed nothing and pushed nothing.
**Authorization:** John, and it covers **case 4 only**. Everything else in the harness is
byte-identical — see `HASHES.md` for the mechanical confinement check.
**Standing rule applied:** D-058(1) / D-060(5). `INVALIDITY-ADJUDICATION.md` is the
independent confirmation step that authorized a replacement at all; this document is the
replacement's demonstration.

Paths are repository-relative. Two placeholders stand for locations outside the repository:
`<PRE>` = the pre-repair worktree at `edb5f7e`, `<POST>` = the implementation worktree at
`8482477`, `<SCRATCH>` = this session's scratch area.

---

## 0. WHAT WAS WRONG, IN ONE PARAGRAPH

The withdrawn case 4 ran the same command as case 2 — `cd "$PLAIN" &&
"$SUT/scripts/$s.sh"`, the **in-repository** entry points called from a directory outside every
repository — and required a non-zero exit where case 2 requires byte-identical Sentinel output
and exit 0. The only thing that fixture made unresolvable was the **caller's** repository, which
counted as identity solely under the caller-current-directory semantics **D-060(2) abolished**.
Under the ruled semantics the entry point derives identity from its **own** location, resolves
fine, and exit 0 is correct. Rows 2 and 4 of the card's matrix were one fixture read under two
semantics; only row 2 survives.

The corrected case attacks the **script's own** location instead, so it measures a different
command from case 2 and the two can both hold.

## 1. THE PROPERTY THE CORRECTED CASE ASSERTS — John's specification

> An entry point whose own containing Sentinel repository cannot be established must refuse
> before performing project work.

Instantiated as: the entry-point layout is **copied** out of every git repository with the
`scripts/` and `.githooks/` structure preserved; the **copies** are invoked from that isolated
layout with `GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR` and `GIT_PREFIX` cleared; a pass
requires a **non-zero exit AND a dedicated repository-identity refusal AND no work having been
done first**. All **16** entry points are covered, not the 12 of the withdrawn form.

## 2. HOW A DEDICATED IDENTITY REFUSAL IS TOLD FROM AN INCIDENTAL FAILURE

This is the crux, and it is why a non-zero exit is not scored as a pass. At the pre-repair
checkpoint **15 of 16 copies print an incidental error** and 13 of 16 exit non-zero for reasons
that have nothing to do with identity. Scoring those as refusals would make the case vacuous —
the same mislabelling case 12b already forecloses, and the same one the adjudication warned
about in its §1.6 cautions.

The scorer requires **one line carrying both** a refusal verb **and** the repository-identity
condition:

```
is_ident_refusal() {
    printf '%s\n' "$1" \
      | /usr/bin/grep -Ei 'refus(e|ed|es|ing)|declin(e|ed|es|ing)' \
      | /usr/bin/grep -Eiq 'sentinel repositor|repository identit|identity mismatch|repository root|own location|invoking repositor|another repositor|foreign repositor|(is |was )?(not inside|outside) the sentinel|cannot (establish|determine|resolve).*(repositor|identity|location)'
}
```

Two properties matter more than the regex itself, and both are asserted by controls rather than
claimed:

- **It is not a transcription of the implementation.** Control `4c` feeds it three refusal
  wordings this harness invented and none of which appears in any entry point; all three are
  accepted. So the case scores a *behaviour*, and an implementer who words the refusal
  differently still passes.
- **It rejects everything the specification excludes.** Control `4d` feeds it eight synthetic
  lines — a missing-file error, a command-not-found, a failed `cd`, `fatal: not a git
  repository`, a shim report, and **three genuine non-identity refusals the pre-repair scripts
  really print** (`refusing to report a clean scan`, `refusing to report totals from nothing`,
  `Refusing to treat an instrument failure as a deletion`). None is accepted.

Beyond the message, a pass also requires, per entry point: exit non-zero; **no shimmed child
reached**; the isolated layout unmutated; **no git configuration written anywhere**; and the
Sentinel clone unmutated. Reaching a shim is an **instrument failure**, never a refusal.

Control `4b` closes the last hole: no *normal* in-repository run emits the marker, so the marker
is a dedicated signal and not boilerplate the scorer would find everywhere.

## 3. THE FIXTURE, AND WHY IT CANNOT DO DAMAGE

- Two isolated layouts under the run's own `TMPDIR` scratch, each verified to be **outside every
  git repository** before use (control `4a`, alongside a byte-identity check of all 16 copies).
- `HOME`, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM` and `XDG_CONFIG_HOME` are redirected into
  that scratch, so nothing a copy attempts can reach the operator's configuration. This also
  neutralises `export PATH="$HOME/.foundry/bin:$PATH"`, which `test.sh` and `mutate.sh` run
  before anything else and which would otherwise put the real toolchain ahead of the shims.
- Expensive and network-capable children are shimmed to a recorder that does no work:
  `forge anvil cast chisel npm npx node cargo curl wget gh python3 pip3 yarn pnpm ssh nc`.
- Control `4e` re-fingerprints the Sentinel clone and the whole git-configuration surface after
  the case and requires both unchanged, so cases 5–13 still measure a clean subject.

## 4. RESULT — PRE-REPAIR WORKTREE `edb5f7e`

```
cd <PRE>
A1_MATRIX_OUT=<SCRATCH>/pre-matrix.tsv \
  bash docs/review-2026-08-19-d057-targeted/batch-cards/A1-tests/a1-repo-identity.sh
```

**Harness exit status: 1.** (1 = required failures with every control intact.)

```
== A1 SUMMARY ==
  repository under test : edb5f7e066a5d5ee3a834a62a2035db98904621b
  REQUIRED failed       : 20   (pre-repair defects observed)
  CONTROL  failed       : 0   (must be 0, or nothing above is evidence)

  20 required assertion(s) failed with every control intact — the A1 defects are
  present and observable at this SHA.
```

Case 4's own block:

```
== CASE 4 (REQUIRED) — an entry point whose OWN repository cannot be established must refuse ==
  case 4a  CONTROL  PASS  16 byte-identical entry-point copies, structure preserved, in layouts outside every repository
  case 4b  CONTROL  PASS  no normal in-repository run emits an identity refusal — the marker is dedicated, not boilerplate
  case 4c  CONTROL  PASS  the scorer accepts dedicated identity refusals in three wordings this harness invented, not one implementation's literal
  case 4d  CONTROL  PASS  the scorer rejects missing-file, command-not-found, failed-cd, not-a-repository, shim and non-identity refusals
        NOT a refusal: .githooks/pre-commit (exit 128) — no dedicated identity refusal
        NOT a refusal: scripts/check-class-coverage.sh (exit 1) — no dedicated identity refusal; reached a shimmed child (instrument failure)
        NOT a refusal: scripts/check-eval-codes.sh (exit 1) — no dedicated identity refusal
        NOT a refusal: scripts/check-findings-ledger.sh (exit 1) — no dedicated identity refusal
        NOT a refusal: scripts/check-gate-immutability.sh (exit 1) — no dedicated identity refusal
        NOT a refusal: scripts/check-label-integrity.sh (exit 1) — no dedicated identity refusal
        NOT a refusal: scripts/check-label-prompt.sh (exit 1) — no dedicated identity refusal
        NOT a refusal: scripts/check-rename-gate.sh (exit 0) — exited 0; no dedicated identity refusal
        NOT a refusal: scripts/check-review-scope.sh (exit 1) — no dedicated identity refusal
        NOT a refusal: scripts/check-secrets.sh (exit 0) — exited 0; no dedicated identity refusal
        NOT a refusal: scripts/check-suite-floors.sh (exit 0) — exited 0; no dedicated identity refusal
        NOT a refusal: scripts/check-type-strings.sh (exit 1) — no dedicated identity refusal
        NOT a refusal: scripts/check-vendor-honesty.sh (exit 1) — no dedicated identity refusal
        NOT a refusal: scripts/install-hooks.sh (exit 128) — no dedicated identity refusal
        NOT a refusal: scripts/mutate.sh (exit 1) — no dedicated identity refusal
        NOT a refusal: scripts/test.sh (exit 5) — no dedicated identity refusal; reached a shimmed child (instrument failure)
  case 4   REQUIRED FAIL  all 16 entry points refuse with a dedicated repository-identity refusal before doing any work (0 of 16 refuse, 16 do not)
  case 4i  REQUIRED FAIL  install-hooks.sh refuses on an unestablished repository and writes NO git configuration anywhere (exit 128, config unchanged=yes)
  case 4h  REQUIRED FAIL  the hook refuses before executing the layout's own scripts/check-secrets.sh (exit 128, decoy ran: no)
  case 4e  CONTROL  PASS  case 4 changed neither the Sentinel clone nor any git configuration — later cases still measure a clean subject
  case 4s  OBSERVED ....  instrumentation: 2 of 16 reached a shimmed child, 15 of 16 printed an incidental error (neither can score as a refusal)
  case 4x  OBSERVED ....  case 2 and case 4 differ only in WHERE THE SCRIPT LIVES: originals inside Sentinel, called from elsewhere, must answer; copies outside every repository must refuse
```

**The reason for the failure is the one intended, and it is stated per line: the dedicated
identity refusal is ABSENT — 0 of 16.** Every `NOT a refusal` line names `no dedicated identity
refusal`; three additionally fail open at exit 0; two additionally reached a shim. Note
`4i` and `4h` fail on the message alone: at this checkpoint `install-hooks.sh` already writes no
git configuration (its `git config` dies with `fatal: not in a git directory`, exit 128) and the
hook already fails to run the decoy — so those two sub-conditions are *necessary but not
sufficient*, and the discriminator remains the refusal.

**Every control holds: 20 of 20 CONTROL lines PASS, 0 fail.**

### 4.1 Internal consistency of the required-failure count

The harness writes a machine-readable matrix. Counted from it rather than from the prose:

```
awk -F'\t' '$2=="REQUIRED" && $3=="FAIL"' <SCRATCH>/pre-matrix.tsv | /usr/bin/grep -c ''
20
awk -F'\t' '$2=="CONTROL"  && $3=="FAIL"' <SCRATCH>/pre-matrix.tsv | /usr/bin/grep -c ''
0
awk -F'\t' '{print $2,$3}' <SCRATCH>/pre-matrix.tsv | sort | uniq -c
  20 CONTROL PASS
   3 OBSERVED ....
  20 REQUIRED FAIL
```

The 20 failing REQUIRED ids are `2 3 3a 3b 3c 4 4i 4h 5a 5b 5c 6 9 10 11 12 12b 13a-r 13 13b`
— three of them (`4`, `4i`, `4h`) are the corrected case, and the summary's `REQUIRED failed :
20` equals the number of `REQUIRED FAIL` rows exactly.

## 5. RESULT — IMPLEMENTATION WORKTREE `8482477`

```
cd <POST>
A1_MATRIX_OUT=<SCRATCH>/post-matrix.tsv \
  bash docs/review-2026-08-19-d057-targeted/batch-cards/A1-tests/a1-repo-identity.sh
```

**Harness exit status: 0.**

```
== A1 SUMMARY ==
  repository under test : 848247797929b8c4ce35f57815143394fc6cc9ad
  REQUIRED failed       : 0   (pre-repair defects observed)
  CONTROL  failed       : 0   (must be 0, or nothing above is evidence)

  every required assertion and every control held.
```

```
awk -F'\t' '{print $2,$3}' <SCRATCH>/post-matrix.tsv | sort | uniq -c
  20 CONTROL PASS
   3 OBSERVED ....
  20 REQUIRED PASS
```

**Zero REQUIRED failures. Zero CONTROL failures.** Case 4's block:

```
== CASE 4 (REQUIRED) — an entry point whose OWN repository cannot be established must refuse ==
  case 4a  CONTROL  PASS  16 byte-identical entry-point copies, structure preserved, in layouts outside every repository
  case 4b  CONTROL  PASS  no normal in-repository run emits an identity refusal — the marker is dedicated, not boilerplate
  case 4c  CONTROL  PASS  the scorer accepts dedicated identity refusals in three wordings this harness invented, not one implementation's literal
  case 4d  CONTROL  PASS  the scorer rejects missing-file, command-not-found, failed-cd, not-a-repository, shim and non-identity refusals
  case 4   REQUIRED PASS  all 16 entry points refuse with a dedicated repository-identity refusal before doing any work (16 of 16 refuse, 0 do not)
  case 4i  REQUIRED PASS  install-hooks.sh refuses on an unestablished repository and writes NO git configuration anywhere (exit 2, config unchanged=yes)
  case 4h  REQUIRED PASS  the hook refuses before executing the layout's own scripts/check-secrets.sh (exit 2, decoy ran: no)
  case 4e  CONTROL  PASS  case 4 changed neither the Sentinel clone nor any git configuration — later cases still measure a clean subject
  case 4s  OBSERVED ....  instrumentation: 0 of 16 reached a shimmed child, 0 of 16 printed an incidental error (neither can score as a refusal)
  case 4x  OBSERVED ....  case 2 and case 4 differ only in WHERE THE SCRIPT LIVES: originals inside Sentinel, called from elsewhere, must answer; copies outside every repository must refuse
```

`4s` is worth reading twice: **0 of 16 reached a shim and 0 of 16 printed an incidental error.**
Every one of the sixteen refused on its own, before any child ran.

### 5.1 Case 2 and case 4 pass for opposite, observable reasons

Same run, same subject, adjacent blocks:

```
  case 2   REQUIRED PASS  all 12 give the Sentinel answer from an unrelated directory (0 differ, of which 0 exit 0)
  case 3   REQUIRED PASS  all 12 give the Sentinel answer from inside a foreign repository (0 differ, of which 0 exit 0)
  case 4   REQUIRED PASS  all 16 entry points refuse ... (16 of 16 refuse, 0 do not)
```

- **Case 2** runs the **originals**, which live inside an intact Sentinel clone, from a
  directory outside every repository. Identity **resolves**, so they must and do produce
  Sentinel's byte-identical answer at exit 0.
- **Case 4** runs **copies of the same 16 files** from a layout that is inside no repository.
  Identity **cannot be established**, so they must and do refuse.

The two fixtures differ in exactly one thing — **where the script itself lives** — which is the
variable D-060(2) makes decisive. The withdrawn case 4 varied the caller's directory instead,
which is the variable D-060(2) made irrelevant, and that is why it collided with case 2.

### 5.2 Determinism — run twice, compared byte-for-byte

```
cd <POST>
A1_MATRIX_OUT=<SCRATCH>/post-matrix.tsv bash …/a1-repo-identity.sh > <SCRATCH>/post-A.log; echo $?   # 0
A1_MATRIX_OUT=<SCRATCH>/post-matrix.tsv bash …/a1-repo-identity.sh > <SCRATCH>/post-B.log; echo $?   # 0

diff <SCRATCH>/post-A.summary <SCRATCH>/post-B.summary   ->  BYTE-IDENTICAL
diff <SCRATCH>/post-A.tsv     <SCRATCH>/post-B.tsv       ->  MATRIX BYTE-IDENTICAL
diff <SCRATCH>/post-A.log     <SCRATCH>/post-B.log       ->  (no output — the WHOLE log matches)

shasum -a 256 post-A.summary post-B.summary
764fa6f4d1363137f78e02c6c07af0fba038d0d16efd87946d6cdf400bf206eb
764fa6f4d1363137f78e02c6c07af0fba038d0d16efd87946d6cdf400bf206eb

shasum -a 256 post-A.tsv post-B.tsv
8efac6c0c3a73d737f3ff61df74c0f17396fed9c973df6501c2918f456598890
8efac6c0c3a73d737f3ff61df74c0f17396fed9c973df6501c2918f456598890
```

The two summaries are byte-identical; so, in fact, is every line of both runs.

## 6. SUPPLEMENTARY PROBE — the per-entry-point view

`probe4.sh` (scratch only, never written into the repository) reproduces case 4's fixture and
prints one line per entry point, so the aggregate above can be read file by file. `MARKER` means
the scorer found a dedicated identity refusal.

**`8482477` — 16 of 16 refuse, 0 shims reached, no git configuration written:**

```
.githooks/pre-commit               rc=2    MARKER |   FAIL  pre-commit: this hook is not inside the Sentinel repository; refusing.
scripts/check-class-coverage.sh    rc=2    MARKER |   FAIL  this script is not inside the Sentinel repository; refusing.
scripts/check-eval-codes.sh        rc=2    MARKER |   FAIL  this script is not inside the Sentinel repository; refusing.
scripts/check-findings-ledger.sh   rc=2    MARKER |   FAIL  this script is not inside the Sentinel repository; refusing.
scripts/check-gate-immutability.sh rc=2    MARKER |   FAIL  this script is not inside the Sentinel repository; refusing.
scripts/check-label-integrity.sh   rc=2    MARKER |   FAIL  this script is not inside the Sentinel repository; refusing.
scripts/check-label-prompt.sh      rc=2    MARKER |   FAIL  this script is not inside the Sentinel repository; refusing.
scripts/check-rename-gate.sh       rc=2    MARKER |   FAIL  this script is not inside the Sentinel repository; refusing.
scripts/check-review-scope.sh      rc=2    MARKER |   FAIL  this script is not inside the Sentinel repository; refusing.
scripts/check-secrets.sh           rc=2    MARKER |   FAIL  this script is not inside the Sentinel repository; refusing.
scripts/check-suite-floors.sh      rc=2    MARKER |   FAIL  this script is not inside the Sentinel repository; refusing.
scripts/check-type-strings.sh      rc=2    MARKER |   FAIL  this script is not inside the Sentinel repository; refusing.
scripts/check-vendor-honesty.sh    rc=2    MARKER |   FAIL  this script is not inside the Sentinel repository; refusing.
scripts/install-hooks.sh           rc=2    MARKER |   FAIL  this script is not inside the Sentinel repository; refusing.
scripts/mutate.sh                  rc=2    MARKER |   FAIL  this script is not inside the Sentinel repository; refusing.
scripts/test.sh                    rc=5    MARKER |   FAIL  the gate was invoked outside the Sentinel repository; refusing.
```

`test.sh` is the interesting one and it is *correctly* scored. Its body refuses with the
dedicated message; because the body exits before emitting its completion token, the D-057(3)
supervisor outside it fails closed on its own terms and the process exits **5**, not 2. The
scorer keys on the message, so a defensible two-layer refusal is not mistaken for a defect —
and, equally, the supervisor's own generic failure could not have produced a pass on its own.

**`edb5f7e` — 0 of 16 refuse. First refusal-shaped line of each output, where there was one:**

```
.githooks/pre-commit               rc=128  ------ |
scripts/check-class-coverage.sh    rc=1    ------ | a1-case4 shim: 'node' was reached — INSTRUMENT FAILURE, not a refusal
scripts/check-eval-codes.sh        rc=1    ------ |   Refusing to report coverage against a section this guard could not find.
scripts/check-findings-ledger.sh   rc=1    ------ | findings ledger: MISSING at … — refusing to report totals from nothing.
scripts/check-gate-immutability.sh rc=1    ------ |   Refusing to report a pass on an empty probe — that is the dead-probe failure mode.
scripts/check-label-integrity.sh   rc=1    ------ |
scripts/check-label-prompt.sh      rc=1    ------ |
scripts/check-rename-gate.sh       rc=0    ------ |
scripts/check-review-scope.sh      rc=1    ------ |     Refusing to report a partition measured against nothing.
scripts/check-secrets.sh           rc=0    ------ |
scripts/check-suite-floors.sh      rc=0    ------ |
scripts/check-type-strings.sh      rc=1    ------ |   Refusing to certify a section this guard could not find — an empty scope would
scripts/check-vendor-honesty.sh    rc=1    ------ |
scripts/install-hooks.sh           rc=128  ------ |
scripts/mutate.sh                  rc=1    ------ |
scripts/test.sh                    rc=5    ------ |   Refusing to report a pass on an empty probe — that is the dead-probe failure mode.
```

**This table is the whole argument for the scorer.** Six of these entry points print a refusal
verb and still score `------`, because what they are refusing is a missing section, an empty
probe, an absent ledger or a partition measured against nothing — a downstream fail-closed, not
an identity refusal. Measured, not estimated:

```
entry points at edb5f7e whose case-4 output carries a refusal verb: 6
  scripts/check-eval-codes.sh  scripts/check-findings-ledger.sh  scripts/check-gate-immutability.sh
  scripts/check-review-scope.sh  scripts/check-type-strings.sh   scripts/test.sh
```

A case-4 that accepted any non-zero exit would have counted **13 of 16** as passes at the
pre-repair checkpoint and proved nothing; a case-4 that accepted any refusal verb would have
counted **6**. It counts **zero**.

The shim recorder at `edb5f7e`, with temporary paths elided, showing the work that did **not**
happen:

```
--- shim touches ---
   1 node - fixtures/corpus/results fixtures/corpus/for-labelling /tmp/.sentinel-eval-codes.…
   1 node - fixtures/corpus/results fixtures/corpus/for-labelling /tmp/.sentinel-eval-codes.…
   1 node --input-type=module -e  … import('<TMP>/iso/ts/src/ablation/report.ts') …
   1 python3 - <TMP> <TMP>
   1 python3 - <TMP>
```

## 7. WHAT THIS EVIDENCE DOES AND DOES NOT ESTABLISH

**Establishes.**

- The correction is confined to case 4: one hunk, the removed lines are exactly case 4's body,
  its REQUIRED line and its CONTROL line, and the rest of the file is byte-identical
  (`HASHES.md`). **Case 2 is untouched.** No other test line needed to change, so the
  authorization's stop condition was never reached.
- At `edb5f7e` the corrected case fails for the intended reason — the dedicated identity
  refusal is absent, 0 of 16 — with every control intact and harness exit 1.
- At `8482477` it passes, 16 of 16, with 0 shims reached and 0 incidental errors, alongside
  case 2 passing for the opposite reason, and harness exit 0 with zero REQUIRED and zero
  CONTROL failures.
- The scorer discriminates in both directions against synthetic probes, including against three
  genuine non-identity refusals the pre-repair scripts really emit.
- The run is deterministic: two consecutive runs at `8482477` are byte-identical end to end.

**Does not establish.**

- Neither worktree is the card's base SHA `f68d4d80…`; the harness prints that warning itself.
  These outcomes are evidence about `edb5f7e` and `8482477` and nothing else. In particular the
  pre-repair fail-open set here is `check-rename-gate.sh`, `check-secrets.sh` and
  `check-suite-floors.sh`, which is not necessarily the base-SHA set the adjudication quotes.
- Nothing here adjudicates any other REQUIRED line. Cases 1, 2, 3, 5–13 were observed only as
  they fell out of these runs, and the 17 non-case-4 REQUIRED failures at `edb5f7e` are recorded
  above without being analysed.
- The case asserts that no work happened *before* the refusal, by exit status, message,
  shim-reach, layout fingerprint, git-configuration fingerprint and clone fingerprint. It does
  not prove the absence of every conceivable side effect — a side effect outside all six
  observation surfaces would not be seen.
- `test.sh` and `mutate.sh` are exercised here **only** to the point of their identity check,
  with their expensive children shimmed. Nothing above is evidence about their gate behaviour;
  `COVERAGE.md` §1 still governs that.
- The scorer's wording list is broad by design and could, in principle, accept a future refusal
  that names the repository for an unrelated reason. Control `4b` bounds that risk — no normal
  run emits it today — but it is a bound, not a proof.

## 8. RESTORATION

No production file was edited in any tree. Nothing was committed, staged or pushed. The
committed harness in the primary tree is untouched at
`7be56445cc0510c03753011e21d2cea949e766a42545603289f889579145b82d`; the corrected file exists in
the two worktrees as an unstaged working-tree modification for the demonstration, and as
`CASE4.patch` here. Every search in this work used `/usr/bin/grep`, with the harness's own
planted-canary preflight (`P1`) proving it finds a string that is definitely there before any
zero result was believed.
