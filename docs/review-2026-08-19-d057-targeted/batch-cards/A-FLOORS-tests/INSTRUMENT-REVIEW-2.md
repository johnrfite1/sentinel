# A-FLOORS — fresh independent corrected-instrument review 2

## Verdict

**FAIL for instrument readiness.** The Review-1 corrections close the two reported omissions,
but the corrected frozen contract still admits a natural false-green sibling: its proposed
source reader recognizes a here-document opener in raw text before deciding whether that text is
executable. An inert quoted or assignment-contained `<<...` token can therefore put the reader
into a false here-document state and hide the next real executable floor assignment. The exact
positive sibling passes every frozen row at **REQUIRED 71/71 and CONTROL 65/65**, yet exits 0 and
prints the planned value after Bash executes a later indented duplicate and leaves the actual
value at `999`.

This is a verdict on the corrected test contract only. It is not an implementation verdict,
gate approval or signature, certification, ratification, publication, rename, D-055 assessment,
D-008 action or push authorization.

## 1. Frozen identity, scope and preservation

I reviewed exact subject `69e4fda92401e29c0cd4c717538fc278a5e59e26`, tree
`fc5c63583be28683b53ced20ccc42f697d1494bc`, whose sole parent is Review-1 FAIL commit
`e3b8a76cff7a002b3211bb8f8a75f2d14b86a37e`.

The parent-to-subject diff is exactly 17 paths, all beneath this `A-FLOORS-tests/` evidence
directory: 12 modifications and 5 additions, 1,087 insertions and 333 deletions. It changes no
production byte, existing test, live gate, floor, maintained claim, decision record, signed
material, or prior review. `git diff --check` passes. In particular:

- Review 1 is byte-preserved at SHA-256
  `d07c6358127caba142b0c95adcba6fc33cb5b8eafdbba5c8680382a32d39c82d`;
- all 20 entries in corrected `CHECKSUMS.sha256` verify;
- `a-floors.py` is SHA-256
  `827a4119f60ac97e20951d3a1b0b43a411b3bd2db48872cde754a700d584fc39`;
- unchanged `a-floors-gate.py` is SHA-256
  `fb389fdd33e981a356436cf37e453158787288c6d64530c28c695fcec83cd8d0`;
- the protected B-EVENTS and C-SNAPSHOT tests remain respectively
  `2a9219cc5138858b012b0bc56069490db3dd7d1963b73ccc19c28a48ce2b029e`
  and `29a673560e89b639b6635661706a368454c9969a04c5d37c4f6c15229df3dd8a`;
- the signed Gate S2 pack remains Git blob
  `baab3e7809a46f22131ef2b609f30af1ed8eeada`, SHA-256
  `833671b8071b0c8786e6fcbd0aaa672478d437e6f6d4ba01c744fb1f816bf589`.

I read the workspace rules, D-058, D-059, D-060 and D-066, the complete corrected evidence,
Review 1, both harnesses, the frozen matrices and raw summaries, the current reader, relevant
gate and maintained-claim surfaces, and the protected B/C tests. I authored neither this
instrument nor a future Batch A implementation.

## 2. Exact deterministic reproduction

I reran the corrected focused harness externally against exact Review-1 parent
`e3b8a76cff7a002b3211bb8f8a75f2d14b86a37e`. Each generated matrix was byte-identical to its
tracked counterpart.

| Variant | Exit | REQUIRED | CONTROL | Raw SHA-256 | Matrix SHA-256 |
|---|---:|---:|---:|---|---|
| pre-repair baseline | 1 | 10/71 | 65/65 | `d90500cd684d245bdc79324f3562a92cabbc935b79595e65976878322ba20931` | `f0ab8dcd63efe98bbacfc353dd0e849b6b9f91bbdccd6288fa90c80a524b63a0` |
| zero-accepting sibling | 1 | 65/71 | 65/65 | `2085505bdcd6db3004b5e82cb424da45cc658bcc47caf78ce3b7a522d6275e2c` | `2094fba903c6ad9ef7f8be4cdba1bc5dfc0bc841b7f34fc70070b6787c6bf46c` |
| exact-positive sibling | 0 | 71/71 | 65/65 | `34980d90b09909c698abf7e8f2c88d02e81755325d03ba61325756fef2de0d11` | `3db1d06abbcec760aa4ce80f68aacaed7ed17df3fc998adf3c74707b86695bdb` |

The zero sibling fails exactly the six new `Z-*` rows and passes all 81 Review-1 rows. The
exact-positive sibling differs only by changing its lexical value predicate from digits
including zero to positive decimal, and passes all 136 frozen rows. This exactly reproduces
the claimed Review-1 corrections: zero is now observed, all-six zero is discriminated, and the
direct standalone indented before/after cases exist for every constant with Bash witnesses.

## 3. Blocking finding — an inert fake opener masks a later executable duplicate

The exact-positive sibling's reader examines each raw line in this order:

```python
marker = None if raw.lstrip().startswith("#") else re.search(
    r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1", raw
)
if marker:
    heredoc = marker.group(2)
code = shell_code(raw)
```

Thus the here-document state transition occurs before quotes, assignments and other inert
contexts are classified. In an isolated exact-parent clone carrying the exact-positive sibling,
I began with all six planned definitions and appended:

```bash
printf '%s\n' "<<'MASK' FOUNDRY_MIN_TESTS=888" >/dev/null
    FOUNDRY_MIN_TESTS=999
```

The sibling returned **0** and printed:

```text
  FOUNDRY_MIN_TESTS          103
  TS_MIN_TESTS               550
  VERIFIER_MIN_TESTS         221
  VERIFIER_MIN_SAMPLES       7
  VERIFIER_MIN_TAMPER        78
  VERIFIER_MIN_TAMPER_MODES  30
suite floors: read from scripts/test.sh, which is the only executable source.
```

But an actual clean Bash source returned 0 and xtrace showed:

```text
++ FOUNDRY_MIN_TESTS=103
++ printf '%s\n' '<<'\''MASK'\'' FOUNDRY_MIN_TESTS=888'
++ FOUNDRY_MIN_TESTS=999
+ printf 'actual=%s\n' 999
actual=999
```

The checker log is SHA-256
`cce1141067f4e96b3c65689646045224206dfddd742fc85cd4c7e5162e0afc43`; the Bash log is
`93204ee24802b3960563934cc89bfb8873b083964b8b3abc991f0286f6a26a1b`.
This is a direct false green for the named requirement that a later executable duplicate must
be refused. It is not a demand for general shell parsing: the missed line is the exact
standalone indented form Review 1 required, hidden only by the immediately preceding parser
state.

### Bounded sibling variants

Cheap variants establish the defect class rather than one spelling:

| Prefix before the real indented `FOUNDRY_MIN_TESTS=999` | Checker | Bash |
|---|---|---|
| `echo '<<"MASK" FOUNDRY_MIN_TESTS=888' >/dev/null` | exit 0, prints 103 | xtrace executes 103 then 999; `actual=999` |
| `note="<<'MASK' FOUNDRY_MIN_TESTS=888"` | exit 0, prints 103 | xtrace executes 103 then 999; `actual=999` |
| `: <<< 'MASK'` | exit 0, prints 103 | xtrace executes 103 then 999; `actual=999` |

The single-quoted `echo` checker and Bash logs hash respectively to
`cce1141067f4e96b3c65689646045224206dfddd742fc85cd4c7e5162e0afc43` and
`cbbf9d9c64aea6a113f96520d52a79be75a4663bb90beafe7b196db82dcf066e`.
The assignment-context logs hash to
`cce1141067f4e96b3c65689646045224206dfddd742fc85cd4c7e5162e0afc43` and
`2c04d622ad10c31e4ff38d8e6da57e699a09aca906e0812f946b8593e77c21e0`.
The here-string logs hash to
`cce1141067f4e96b3c65689646045224206dfddd742fc85cd4c7e5162e0afc43` and
`09b917fc81fa31385c2c6e4e8db2806b22c3e8f6246ec5821f5f590779a8b84a`.

Two controls bound the required distinction:

- a full-line comment containing a fake opener, followed by the executable indented duplicate,
  is correctly refused as a duplicate; Bash executes 103 then 999;
- a real `: <<'MASK'` body containing `FOUNDRY_MIN_TESTS=888` is inert, and a real indented
  `FOUNDRY_MIN_TESTS=999` after the `MASK` terminator is correctly refused as a duplicate;
  Bash likewise executes only 103 then 999.

Both refusal logs contain exactly `FOUNDRY_MIN_TESTS: duplicate executable assignment` and hash
to `2d5fc18357191f989e580636199ba0d28e5c21095baf89aae60e7c2d62f4ac74`.

### Why the frozen rows do not observe it

No current row combines an inert parser-state token with a subsequent executable assignment:

- `IC-*` supplies an inert full-line comment, but no following duplicate;
- `IQ-*` supplies an ordinary quoted assignment-shaped string, but no `<<` token and no
  following duplicate;
- `IH-*` supplies assignment-shaped text inside a genuine here-document body, but no executable
  duplicate after the terminator;
- `IA-*` and `IB-*` supply the required standalone executable duplicate, but no preceding inert
  fake opener.

All these rows can therefore pass while their combination fails. The corrected instrument needs
state-machine combination probes that prevent an inert fake opener from masking the next
executable assignment, calibrated against controls proving genuine here-document bodies stay
inert and parsing resumes at the terminator. A conforming sibling must pass all existing rows and
the new combinations. This states the observable contract; it does not prescribe an
implementation.

## 4. Other correction and oracle checks

The remaining independently attacked properties did not create another blocker:

- all six zero values are rejected by the exact-positive sibling and accepted by the deliberate
  zero sibling; all ordinary exact positive values are accepted;
- all six standalone indented duplicates before and after the canonical definitions are real
  Bash assignments, their before/after traces are exact, and the reader refuses them by name;
- full-line comment exclusion does not by itself mask a following executable duplicate;
- quoted assignment strings and true here-document bodies remain inert in their isolated rows;
- the six definition, malformed/empty/nondecimal, duplicate-order, conditional, diagnostic and
  wrap-normalized current-prose classifications reproduce as recorded;
- the finite current surfaces remain the six executable definitions in `scripts/test.sh`, the
  reader, and the enumerated current maintained paragraphs. Historical decisions, prior reviews
  and signed evidence remain controls; Batch D ownership is not expanded;
- `W-common` passes at exactly one proposed real-gate invocation and `W-positive` passes. A
  scratch subject producing two invocations makes only `W-common` fail (`observed 2`), with
  REQUIRED 70/71 and CONTROL 65/65;
- `P-reader-restore` compares both the reader hash and restored live output. Injecting a
  byte-only comment change immediately before that comparison makes only this control fail:
  REQUIRED 10/71, CONTROL 64/65, exit 2. It is therefore a live restoration control, not a
  vacuous label.

## 5. Full gate not replayed

I did **not** launch the seven-case `a-floors-gate.py` replay after establishing the decisive
focused false green. Its bytes and recorded evidence remain checksum-valid, but those historical
results are not represented here as a fresh run. End-to-end gate results cannot restore a source
oracle that a passing natural sibling has just falsified; Review 2 stops at instrument FAIL and
requires a corrected frozen contract before another costly replay.

Accordingly, this review makes no fresh claim about the recorded 3/3 CONTROL, 2/4 REQUIRED,
fast/deep wrong-reader trials, or planned 103/550 and B/C deletion trials. Those remain evidence
to rerun after the combination gap is corrected.

## 6. Limits

This review establishes a specific missing discrimination property in the frozen focused source
oracle. It does not establish general Bash parsing, implementation correctness, fast/deep gate
success, measured suite counts, the truth of historical prose, or closure of any Batch A or
D-055 obligation. It neither alters nor adjudicates Gate S2, signed material, Batch D surfaces,
or held D-008 questions.

## 7. Review-child guards

The only repository change made by this reviewer is this standalone record. Before committing:

- worktree and staged secret guards: `clean`;
- review scope before staging: R1 410 / R2 47 / R3 152, 609/609 tracked; after staging this
  record: R1 411 / R2 47 / R3 152, 610/610 tracked;
- findings ledger: pass, 23 IDs and all D-057(1) totals unchanged;
- unchanged floor reader: exit 0 at `92/527/221/7/78/30`;
- vendor-honesty mechanical guard: pass, while explicitly leaving D-008(1) and D-008(3)
  authority with John;
- workspace guards: pass with 13 pre-existing machine-state findings baselined and zero new;
- staged diff: exactly this added record, with `git diff --cached --check` passing; and
- protected B/C test and signed-pack hashes: unchanged as listed in section 1.

The workspace pass is ratcheted: it does not erase the 13 pre-existing baselined findings.
