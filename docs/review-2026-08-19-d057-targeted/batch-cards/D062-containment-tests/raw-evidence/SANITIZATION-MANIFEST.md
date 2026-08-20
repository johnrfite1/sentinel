# RAW EVIDENCE FROM THE D-062 INDEPENDENT VERIFICATION — PRESERVATION AND SANITIZATION MANIFEST

These are the **raw probe outputs** produced by the independent verifier whose verdict is
`../VERIFICATION.md`. They were held only in a session scratch area and were **absent from the
repository**; John ruled them primary evidence and directed their preservation.

**What they support.** `a2.base.cases` / `a2.subj.cases` / `a2.base.norm` / `a2.subj.norm` are the
raw basis for **D-064's reversal-condition check** — that exactly two A2 assertions moved and no
third. `layouts-BASE.txt`, `layouts-SUBJ.txt` and `gitdir-SUBJ.txt` are the **linked-worktree and
separate-`gitdir` measurements** that closed the two layouts `IMPLEMENTATION.md` had conceded were
unmeasured. `attacks.txt` is the 45-probe attack sweep on the validation rule.

## PROVENANCE

A **byte-for-byte archive of all nineteen files was taken BEFORE anything was inspected or
changed**, into private storage outside this repository. **Its path is deliberately not recorded
in any tracked file** (D-060(3)). Verify against these instead:

- **archive sha256** — `4cf838ba44c02904fd0300d55680d8662fe48d2ddfc129aef1b6235917ac7c6f`
- **archive size** — 228352 bytes
- the per-file raw hashes in the table below, which are the hashes of the originals

## SANITIZATION — ONE substitution, disclosed in full

**Sixteen of nineteen files are committed BYTE-IDENTICAL to the raw originals.** Three were
altered, by a single substitution applied twelve times:

| | |
|---|---|
| original token | `0x` followed by the character `b` repeated 64 times |
| replacement | `0xPLACEHOLDER-b-repeated-64-times` |
| occurrences | `gitdir-SUBJ.txt` ×7 · `layouts-SUBJ.txt` ×4 · `layouts-BASE.txt` ×1 |

**Why.** The token is a **synthetic fixture credential the harness assembles at run time from one
repeated hex character** — it is not a credential and never was. But it is bound to a key-shaped
identifier in the logs, so `scripts/check-secrets.sh` rule 3b blocks it. **That was measured, not
assumed:** with a raw file present the guard reported `BLOCKED … credential-shaped content`. The
guard is **not weakened and no ignore rule is added** — the evidence is adjusted, never the
instrument.

**Nothing else changed.** No finding, measurement, mechanism, severity, classification, argument
or verdict differs between the raw and tracked copies. **No machine-specific path was found in any
of the nineteen files**, so none was substituted.

Bare 64-hex values remain in four other files unaltered. They are **sha256 hashes the harness
prints**, not key-bound values, and `check-secrets.sh` deliberately does not scan bare 64-hex —
see its own design note on why a private key and a keccak hash are the same shape.

## PER-FILE TABLE

| file | raw sha256 | tracked sha256 | altered |
|---|---|---|---|
| `a1-repo-identity--tpl-baseline.txt` | `0dafae03b4589dd85715276cff60c90afd865101005c3eb86d49606070b5e0d5` | `0dafae03b4589dd85715276cff60c90afd865101005c3eb86d49606070b5e0d5` | no — byte-identical |
| `a1-repo-identity--tpl-subject.txt` | `10cf7353700d4d7a6d278bac78bc15daeef19d7312bfba2bd1f412af04110db5` | `10cf7353700d4d7a6d278bac78bc15daeef19d7312bfba2bd1f412af04110db5` | no — byte-identical |
| `a2-env-and-supervisor--tpl-baseline.txt` | `bcf236fca8afc01cc18ed3b55e5fc4eb894d33a686a1359dc24d56e6d00c164f` | `bcf236fca8afc01cc18ed3b55e5fc4eb894d33a686a1359dc24d56e6d00c164f` | no — byte-identical |
| `a2-env-and-supervisor--tpl-subject.txt` | `56d060b2d0f6de48dccd66d4d70912977296ea7f394c74f6f19d7983529c4355` | `56d060b2d0f6de48dccd66d4d70912977296ea7f394c74f6f19d7983529c4355` | no — byte-identical |
| `a2-run2-subject.txt` | `56d060b2d0f6de48dccd66d4d70912977296ea7f394c74f6f19d7983529c4355` | `56d060b2d0f6de48dccd66d4d70912977296ea7f394c74f6f19d7983529c4355` | no — byte-identical |
| `a2.base.cases` | `cf1a8dd73929af0580919533d580d83a9df75ea1d0cf81ea0bb5dd397c624527` | `cf1a8dd73929af0580919533d580d83a9df75ea1d0cf81ea0bb5dd397c624527` | no — byte-identical |
| `a2.base.norm` | `5bd5971def2812f9215eb3d9a0157ebcda43aba79bf6a1d311faaee38cdd0f9f` | `5bd5971def2812f9215eb3d9a0157ebcda43aba79bf6a1d311faaee38cdd0f9f` | no — byte-identical |
| `a2.subj.cases` | `1b1a47d47734d825dc302b29be24fdf8ab678930875861ddbf3ec2b7fe8bb549` | `1b1a47d47734d825dc302b29be24fdf8ab678930875861ddbf3ec2b7fe8bb549` | no — byte-identical |
| `a2.subj.norm` | `e56d1fce0532950838d39d501a58122a57caf2c054e5ae1c34880d0d22f7ea32` | `e56d1fce0532950838d39d501a58122a57caf2c054e5ae1c34880d0d22f7ea32` | no — byte-identical |
| `attacks.txt` | `7e8195d0dd4595f4fb202cb53389b99b041d893dce3048aaabd1cb226a655cfc` | `7e8195d0dd4595f4fb202cb53389b99b041d893dce3048aaabd1cb226a655cfc` | no — byte-identical |
| `d062-containment--tpl-baseline.txt` | `f3c4a85613a01becb2561af074ab511b1aabb980ced4a593eb271465e3227334` | `f3c4a85613a01becb2561af074ab511b1aabb980ced4a593eb271465e3227334` | no — byte-identical |
| `d062-containment--tpl-subject.txt` | `d47d63b7f6a1ceebefda1709e5c688be4c99cc9ab74fa09e56ffd6bc148ceafb` | `d47d63b7f6a1ceebefda1709e5c688be4c99cc9ab74fa09e56ffd6bc148ceafb` | no — byte-identical |
| `d062-run2-subject.txt` | `e41261273e981895cc2d98441130d13979148e7495ccf4f55dd9ab7e9953648e` | `e41261273e981895cc2d98441130d13979148e7495ccf4f55dd9ab7e9953648e` | no — byte-identical |
| `d062-run2b-subject.txt` | `077d42ace0706aa5f5564c4858082e0d1fee01fc109040373a3872d6a33c2f08` | `077d42ace0706aa5f5564c4858082e0d1fee01fc109040373a3872d6a33c2f08` | no — byte-identical |
| `gitdir-SUBJ.txt` | `07456c1f5c135dad649311784c448b480ff176afc4cd8394f2990e56f46cbd3f` | `b952ab2b10d3c6ddc58fc1911bdf091e4e222ea2b1f5ba314659c9c0fe7cc82e` | **YES — 1 substitution** |
| `harness-driver.txt` | `9f44387406d1439162c5689d6f0ed439c3150e97f0a01cdf6b37066f4835241f` | `9f44387406d1439162c5689d6f0ed439c3150e97f0a01cdf6b37066f4835241f` | no — byte-identical |
| `layouts-BASE.txt` | `9aeb3c79c4ca7053e51a2f1138429fb2b6d3b2b33c004d07e7d884bde5875fcc` | `6388ca243f55d08c7c31f7224830c7b9570e3f35e3b1b598b71e4a8bb7ab2822` | **YES — 1 substitution** |
| `layouts-SUBJ.txt` | `0d6737f4700e1d3eec4b56ff93ed4b0ed1adbca061cf40101e1d82233fde16e4` | `e104ca9fd7705330f83f7c1a0cad767e1ccf2d009dc40468b7818de5379e8a26` | **YES — 1 substitution** |
| `secondruns.flag` | `4ff8bad41b3f53d6a8e1e500254452add98cc96e48ff0844e69997f786d01c65` | `4ff8bad41b3f53d6a8e1e500254452add98cc96e48ff0844e69997f786d01c65` | no — byte-identical |

**Counts are derived from this table, not typed:** nineteen rows, three altered, sixteen
byte-identical.

## STANDING RULE, CARRIED FROM D-060(3)

Another **quotation** of a policed string gets the same disclosed treatment. A **live claim** is a
**STOP CONDITION** and is reported, not sanitized.
