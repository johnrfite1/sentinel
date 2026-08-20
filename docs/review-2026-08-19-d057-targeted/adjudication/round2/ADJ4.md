# ADJ4 — independent adjudication of C4, C5, C6

**Adjudicator:** independent. Did not report any of these candidates and did not write any of the
code or the repair contract.

**Frozen commit:** `a18e6e61598a996d962798ad0353a166232d4490`, confirmed with `git rev-parse HEAD`
in the adjudication worktree. All probes were run in that worktree and it was restored afterwards
(`git status --porcelain -uall` clean apart from the pre-existing untracked `ts/node_modules`).

**Authority for adjudicating at all:** D-058(7) — *"Adjudicate each new item first and classify
it… Do not repair or accept an unadjudicated list wholesale."* Nothing here is repaired, signed,
certified or ratified. Nothing was committed or pushed. `scripts/test.sh` was never edited.

## Verdicts

| Item | Classification | Severity (mine) | Fail direction |
|---|---|---|---|
| **C4** `check-secrets.sh:198` skipped `git show` path | **CONFIRMED**, **DISTINCT** from `V3-N1` | **MEDIUM** | **fail-OPEN** — prints `secret guard: clean` over an unscanned planted key |
| **C5** the signer "detail distinguishes them" claim | **CONFIRMED** (the *detail* claim is false; the *code* claim is true) | **LOW** | n/a — record-honesty defect, not behavioural |
| **C6a** `check-findings-ledger.sh:22` | **CONFIRMED** | **INFO** | **fail-CLOSED** in every configuration probed |
| **C6b** `check-suite-floors.sh:13` | **CONFIRMED** | **LOW** | **fail-OPEN** — prints wrong floors and self-certifies them |
| **C6c** `install-hooks.sh:5` | **CONFIRMED** | **LOW** | **fail-OPEN** — reports success having configured a *different* repository |
| **C6d** `test.sh:161` | **CONFIRMED**, **carries a decision fork about its remedy** | **LOW** (attribution reading: MEDIUM) | **fail-CLOSED** as measured; attribution case not excluded |
| `test.sh:60` | **not a defect — argued exemption CONFIRMED** | — | fail-CLOSED (exit 1, nothing runs) |

**C4's discriminator question, answered up front:** a reliable discriminator **DOES exist**, but
**not** in `git show`'s exit code (every failure mode returns 128) and **not** in its stderr text
(human prose, localizable, version-dependent). It exists **upstream, in the file list** — and in
this script the legitimate-deletion control John was protecting is **already excluded before line
198 ever runs**. **This is therefore NOT a decision fork.** Detail in §C4.4.

---

# C4 — `scripts/check-secrets.sh:198`, the skipped `git show` path

## C4.1 The exact claim at issue

That `scripts/check-secrets.sh` is a mechanical guard which, when it prints `secret guard: clean`
and exits 0, has *scanned* every file in its declared scope. Line 198's
`git show ":$f" >/dev/null 2>&1 || continue` converts **any** failure of that retrieval into a
silent skip of that file, and the script's terminal `echo "secret guard: clean"` is reached
regardless.

## C4.2 Authoritative source

Code, not prose:

- `scripts/check-secrets.sh:78` — `files=$(git diff --cached --name-only --diff-filter=ACM)`
  builds the `--staged` scope.
- `scripts/check-secrets.sh:82` — `files=$(printf '%s\n%s\n' "$(git ls-files)" "$(git ls-files
  --others --exclude-standard)")` builds the default (suite/CI) scope.
- `scripts/check-secrets.sh:198` — `git show ":$f" >/dev/null 2>&1 || continue`.
- `scripts/check-secrets.sh:266` — the unconditional `echo "secret guard: clean"`.

The decisive mechanical fact is **not** in this file: `git diff --cached --name-only` and
`git ls-files` **quote** any pathname containing a byte outside printable ASCII, or a `"`, `\`,
newline or tab (`core.quotePath`, default true, unset in this repository). The emitted token is
then a C-quoted *literal* — `"ts/src/zzprobe-caf\303\251.ts"` — and `git show ":$f"` on that token
cannot resolve. Verified: `git config --get core.quotePath` returns nothing (exit 1, i.e. default
true); git 2.50.1.

## C4.3 Reproduction — done, with a paired control that behaves oppositely

Two files, **byte-identical content**, one planted 64-hex value bound to `OWNER_KEY`. The only
variable moved is one byte in the *filename*.

**(i) `--staged` mode, both staged together:**

```
=== staged list:
ts/src/zzprobe-cafe.ts
"ts/src/zzprobe-caf\303\251.ts"
=== guard:
BLOCKED ts/src/zzprobe-cafe.ts — credential-shaped content:
    1:OWNER_KEY = "0x4c0883…0718
secret guard: 1 finding(s). …
GUARD-EXIT=1
```

The ASCII twin is **BLOCKED**; the non-ASCII twin is **not mentioned at all**.

**(ii) `--staged`, only the non-ASCII twin staged — the guard reports clean over a live key that
is demonstrably in the index:**

```
=== content actually in index:
export const OWNER_KEY = "0x4c0883…0718";
=== guard:
secret guard: clean
GUARD-EXIT=0
```

**(iii) The default (suite/CI) mode has the same hole via a different construct.** The non-staged
branch uses `[ -f "$f" ] || continue` against the same quoted token. With only the non-ASCII file
present untracked and in scope: `secret guard: clean`, exit 0. The ASCII control is BLOCKED.

**(iv) Rule 4 (machine-specific absolute paths) fails open on the same file.** Appending
a machine-specific home-directory path to the non-ASCII twin still yields `secret guard: clean`
(the literal is not reproduced here — rule 4 would block this file for carrying it); the ASCII twin
raises **both** findings.

**(v) Rule 1 (secret-bearing filenames) also fails, because `basename` of a quoted token does not
match `.env*`.** Staged `.env.local` and `.env.locál`, identical content:

```
BLOCKED .env.local — env files are never committed (A-007).
BLOCKED .env.local — credential-shaped content: …
GUARD-EXIT=1
```
and with only the non-ASCII twin staged: `secret guard: clean`, exit 0 — while
`git show ':.env.locál'` prints the key.

**A probe that MOVED nothing, recorded rather than discarded.** My first rule-1 attempt placed the
two `.env` files *untracked*. Both were skipped — including the ASCII control — because `.env*` is
gitignored and `--exclude-standard` removes it by design. That run proved nothing and is not
evidence; the staged version above is.

## C4.4 The remedy question John reserved — deletion vs instrument failure

**Measured, in a scratch repository, git 2.50.1:**

| Case | stderr | exit |
|---|---|---|
| path on disk, not in index | `fatal: path 'X' exists on disk, but not in the index` | **128** |
| path absent everywhere | `fatal: path 'X' does not exist (neither on disk nor in the index)` | **128** |
| quoted/mangled path token | `fatal: ambiguous argument ':"…"': unknown revision or path not in the working tree.` | **128** |
| staged blob whose object is removed from the odb | `fatal: bad object :X` | **128** |

**Exit code is NOT a discriminator: every mode is 128.** stderr text *does* differ, but it is
git's human-facing prose — gettext-localizable and version-dependent — so it is not a durable
mechanical discriminator and should not be made one.

**However, the discriminator does not have to come from `git show` at all, and case (a) is already
excluded before line 198 runs.** Measured on the frozen tree:

- `git diff --cached --name-only --diff-filter=ACM` **excludes status `D`**. Probe: staging a
  deletion of a tracked file put `D <path>` in `--name-status` and **nothing** in the `ACM` list.
  **A staged deletion cannot reach line 198.** John's stated false-failure risk — *"converting a
  legitimate deletion into a false failure"* — is, at this call site, **not reachable**.
- "A path legitimately absent from the index" is likewise unreachable by construction: the list is
  *built from* the index diff. The only residue is a concurrent index mutation between line 78 and
  line 198, which is a race, and refusing on a race is correct.

**A fully mechanical discriminator, no stderr parsing, verified:** `git diff --cached --raw -z`
emits, per entry, the status letter **and** the post-image blob OID —

```
:000000 100644 0000000 3be9de5 A|ts/src/zzprobe-café.ts|
```

`-z` also **disables path quoting entirely**, which removes the trigger outright. Retrieving by
OID (`git cat-file blob 3be9de5`) returned the planted content. So: status `D` ⇒ legitimate
deletion, skip without refusal; any other status ⇒ a real blob exists and a retrieval failure is
**by construction** an instrument failure ⇒ refuse.

**Conclusion: no decision fork. A reliable discriminator exists.** Stated as a constraint on the
repairer rather than as a repair: it must come from the file-list construction (`-z`, and the
status letter from `--raw`), not from interpreting `git show`'s failure.

**One adjacent scope observation, raised not adjudicated:** `--diff-filter=ACM` also excludes `R`.
A staged rename shows `R100` and appears in neither the `ACM` list nor any scan; a
rename-**with**-modification (`R0xx`) would likewise carry unscanned new content. `ACMR` lists it.
Not in my assignment; flagged so it is not lost.

## C4.5 Severity — MEDIUM

Higher than the reporter's framing implies in scope, lower in immediacy.

- **Upward:** it defeats **both** invocation modes (pre-commit hook *and* the gate's own
  `secret guard (A-007)` stage), and **all three** scanning rules (1, 3/3b, 4) for the affected
  file. The bypass costs one non-ASCII byte in a filename and produces **no** diagnostic — the
  guard's output is indistinguishable from a genuine clean.
- **Downward:** **zero** tracked paths at this commit require quoting (`git ls-files` = 463 paths,
  0 matching `[^ -~]`), so nothing is currently unscanned. The accidental route requires a
  maintainer to create such a filename; the adversarial route requires an actor already committing
  credentials, against whom the file's own DESIGN NOTE already concedes limits.

MEDIUM, not HIGH, because no live exposure exists at this commit. Not LOW, because the failure is
silent and total for the affected file and the guard is the mechanical control for house rule 6.

## C4.6 What this evidence does and does not establish

**Establishes:** the mechanism, reproduced in both modes with a paired ASCII control that behaves
oppositely in every case; that the guard prints `clean` and exits 0 with a planted key present and
retrievable; that the reported site (line 198) is **one of four** skip points sharing a single root
cause (path quoting), the others being the default-mode `[ -f "$f" ] || continue`, rule 4's
`git show`/`[ -f ]` pair at :229, and rule 1's `basename` case match; that exit codes cannot
discriminate; that the file list can.

**Does not establish:** that any such file has ever existed in this repository's history (not
searched beyond the current tree); the frequency of the missing-object failure mode; anything
about `check-secrets.sh`'s pattern coverage, which I did not re-audit.

## C4.7 DUPLICATE-vs-DISTINCT against `V3-N1` — **DISTINCT**

Same **class** as `V3-N1` (`check-review-scope.sh:198`,
`git ls-files --error-unmatch "$f" … || continue`): a failed external command silently converted
into a statement about what was measured — the guarantee `A-P1` names. They share a lesson and
nothing else:

| | `V3-N1` | `C4` |
|---|---|---|
| Script / guard | scope checker | **secret guard** |
| Trigger | path not tracked at HEAD ("deleted since") | path token unresolvable, or blob unretrievable |
| Swallowed check | the UNASSIGNED check downstream | rules 1, 3/3b and 4 for that file |
| Repair | must not treat a git failure as "not in scope" | must build the list with `-z` and key on `--raw` status/OID |

Neither repair fixes the other; a coincidence of line numbers is not identity. The repair contract
already lists them on separate rows under `A-P1`, and that treatment is correct.

---

# C5 — the signer "detail distinguishes them" claim

## C5.1 The exact claim at issue

Two claims that must be judged separately, because they are different assertions:

- **Claim A — about the CODE.** `SIGNER_CHAIN_UNSTABLE` covers **two** conditions, not one, and
  the published docstring now enumerates them.
- **Claim B — about the DETAIL.** `ts/src/signer/protocol.ts:115`: *"…so the refusal detail now
  distinguishes them."* `docs/decisions.md` A-077(2): *"the detail now distinguishes them, with no
  public code split."* This asserts that some accompanying text, carried by a refusal, tells the
  two conditions apart.

## C5.2 Authoritative source

- `ts/src/signer/protocol.ts:99-124` — the docstring, and the claim at :115.
- `ts/src/signer/protocol.ts:499-511` — `RefusalRecord`, **nine** fields: `schemaVersion`,
  `chainId`, `vault`, `actionHash`, `evidenceHash`, `requestedVerdict`, `reasonCodesHash`,
  `refusedAt`, `signer`. **No free-text field.**
- `ts/src/signer/protocol.ts:514-526` — `Refusal`: `refused`, `blocking`
  (`{code: ReasonCode; severity: Severity}[]`), `signerFindings` (`ReasonCode[]`),
  `requestedVerdict`, `refusalRecord`. **No free-text field.**
- `ts/src/signer/vault.ts:129-148` — `ChainUnstableError`, which *does* carry both a `pendingOnly`
  boolean and two distinct `message` strings.
- `ts/src/signer/protocol.ts:804` — `toWire` is a structural re-encoder; the wire result is exactly
  `Refusal`, so nothing is added on serialization.

## C5.3 (a) Does any refusal-carrying structure have a detail field that reaches a consumer? **No.**

`/usr/bin/grep -rn "detail" ts/src/signer` returns **exactly two hits, both comment lines** —
`protocol.ts:115` and `protocol.ts:117`. There is no `detail` field anywhere in the signer.
(Search tooling validated first: a planted `ZZCANARY_ADJ4_MARKER` was found by `/usr/bin/grep`
before any zero result was trusted; the canary was removed.)

## C5.4 (b) Do the call sites discard it? **All three signer paths do.**

- `ts/src/signer/attest.ts:381-388` — `catch (error)` binds the error, reads it **once** for
  `error instanceof ChainUnstableError ? "SIGNER_CHAIN_UNSTABLE" : "SIGNER_VAULT_UNREACHABLE"`,
  then `return await refuse()`. `error` is never read again; `.pendingOnly` and `.message` die here.
- `ts/src/signer/server.ts:118-122` — `attestor.probe()` in a **bare** `catch { }` (no binding at
  all), emitting the fixed string `"vault unreadable"`.
- `ts/src/signer/main.ts:70-80` — the same shape, emitting `"vault not readable"`.

## C5.5 Reproduction, with a paired control

An in-process probe drove `evaluateAndSign` three times against a chain reader differing **only**
in the object thrown, and dumped `toWire(result)`:

```
MOVED-ERR-MSG   : no stable block after 5 attempts: the head moved or was replaced under each pinned read | pendingOnly= false
PENDING-ERR-MSG : no finalised head after 5 attempts: every observation returned a pending block with no hash… | pendingOnly= true

WIRE(moved-head)   : {"refused":true,"blocking":[{"code":"SIGNER_CHAIN_UNSTABLE","severity":"FATAL"}], … "reasonCodesHash":"0xf29da571…"}
WIRE(pending-head) : {"refused":true,"blocking":[{"code":"SIGNER_CHAIN_UNSTABLE","severity":"FATAL"}], … "reasonCodesHash":"0xf29da571…"}
WIRE(generic-outage): {"refused":true,"blocking":[{"code":"SIGNER_VAULT_UNREACHABLE","severity":"FATAL"}], … "reasonCodesHash":"0x8a40f057…"}

IDENTICAL(moved,pending) = true
IDENTICAL(moved,outage)  = false
```

**The two conditions produce byte-identical refusals, signed record included.** The **paired
control** — a generic `Error` instead of a `ChainUnstableError` — moves both the reason code and
the `reasonCodesHash`, proving the probe can detect a difference when one exists. The probe file
was deleted after the run.

## C5.6 (c) Is the claim false, partly false, or true? — **Claim A true, Claim B false**

- **Claim A holds.** `protocol.ts:105-113` enumerates (a) head moved / same-height reorg and (b)
  hashless pending head; `vault.ts:179` and `:232` are the two branches; both are exercised by
  `ts/test/vault.anchor.test.ts:316` and `:336`, which assert `pendingOnly` in each direction. The
  *published meaning of the enum* was genuinely repaired.
- **Claim B is false as written.** There is no refusal detail. Nothing that distinguishes the two
  conditions is carried by `Refusal`, by `RefusalRecord`, by the signed D-012 artifact, or by any
  RPC surface. The distinguishing text exists only on an exception object that all three signer
  paths discard.

**One correction to the reporter, in the reporter's favour and against the strongest wording.**
V3 writes that the text *"reaches no product output surface at all."* That is slightly too strong:
`ChainUnstableError` also propagates from non-signer product call sites —
`ts/src/corpus/run.ts:415`, `:625`, `:669`, `ts/src/tools/sample-check.ts:188`,
`ts/src/tools/emit-samples.ts:422` — where, depending on outer handlers I did not exhaustively
trace, it could surface as an unhandled-rejection message on stderr. **None of those is a refusal
surface**, so the precise and defensible statement is: *the distinguishing text reaches no
**refusal**.* That is the claim `protocol.ts:115` and A-077(2) make, and it is false.

## C5.7 Severity — LOW

A record-honesty defect, not a security or behavioural one, and I grade it below what the
substitution language around it might suggest.

- The absence of a detail field means **no signed artifact can carry a false statement about which
  condition occurred** — there is nowhere to put one. The harm is bounded to two maintained
  records asserting a mechanism that does not exist.
- Against that: the two records are `protocol.ts` (the wire contract, i.e. the document a consumer
  reads to learn what the signer tells them) and `docs/decisions.md` A-077 (the decision log). A
  false claim that a diagnostic exists is exactly the class this project tracks, and it was made
  *inside the repair for a finding about naming one cause for two conditions*.

LOW rather than INFO because it sits in the wire contract and in the decision log, both of which
are relied on as authoritative. Not MEDIUM, because no behaviour, no signature and no gate result
depends on it.

## C5.8 What this evidence does and does not establish

**Establishes:** that `Refusal` and `RefusalRecord` carry no free-text field; that all three signer
call sites discard the error object after a single `instanceof` read; that the two conditions are
observationally identical at every product output surface a refusal reaches; that Claim A is true.

**Does not establish:** anything about V3's `F1` (the third `pendingOnly` branch and its
misdescribing message) or `F2` (the unpinned classification) — those are separate items and were
not assigned to me. It does not establish that the `pendingOnly` flag is *unreachable*, only that
it is *unreported*. It does not establish whether a detail field *should* exist — that is a design
question for whoever repairs it, and the honest minimum repair is to strike the two false
sentences rather than to build a field.

**Classification: CONFIRMED.**

---

# C6 — four further unguarded `cd "$(git rev-parse --show-toplevel)"` sites

## C6.1 The shared mechanical fact, verified independently

```
$ bash -c 'set -euo pipefail; cd ""; echo "rc=$? — CONTINUED"; pwd'
rc=0 — CONTINUED
/…/Sentinel                       ← unchanged cwd

$ bash -c 'set -euo pipefail; cd "$(false)"; echo continued'
continued                          ← errexit does NOT fire

$ bash -c 'set -euo pipefail; cd /nonexistent; echo "NOT PRINTED"'
cd: /nonexistent: No such file or directory      (rc=1)
```

**Confirmed: `cd ""` returns 0 and does not abort under `set -euo pipefail`.** `set -u` is no help
either — the substitution yields an *empty* string, not an unset variable. The comparison case
shows `set -e` working normally when `cd` is given a real bad path, so the shell is not simply
ignoring `cd` failures: it is that an empty argument is a **successful no-op**.

## C6.2 Instrument, and why the instrument is not load-bearing

Probes used a `PATH` shim `git` that fails **only** `rev-parse --show-toplevel` (exit 128, empty
stdout) and passes everything else through — so exactly one thing moves: the value the `cd`
receives.

**The shim is not required.** The natural condition reproduces it: from a directory not inside any
git work tree, real git prints `fatal: not a git repository (or any of the parent directories):
.git` and the scripts behave identically. Both forms are shown below. Other realistic triggers,
not exercised: a tree with `.git` absent (tarball export, `COPY` into a container), a bare
repository, `GIT_DIR` set without a work tree.

## C6.3 `scripts/check-findings-ledger.sh:22` — **CONFIRMED, INFO, fail-CLOSED**

`set -uo pipefail`. Three configurations:

| cwd | Result |
|---|---|
| repo root (cd is a no-op, cwd already correct) | correct totals, `all totals match D-057(1) as ruled`, exit 0 |
| unrelated empty dir | `findings ledger: MISSING at docs/…/FINDINGS-LEDGER.tsv — refusing to report totals from nothing.` exit **1** |
| decoy tree carrying a **truncated** ledger | eight `MISMATCH:` lines, `DERIVED TOTALS DISAGREE WITH THE RECORDED RULING.` exit **1** |
| decoy tree carrying a **byte-copy** of the real ledger | identical, true output, exit 0 |

**Paired control:** the same script from the repo root with a working git produces the identical
correct output — so the failure is attributable to the `cd`, not to the script being broken.

I could construct **no** configuration in which this script emits a false or misleading statement.
Its `expect` assertions against D-057(1)'s ruled figures are a second, independent gate that a
decoy must also satisfy — and satisfying them means the decoy ledger *is* the real ledger. Real
defect, no reachable harm: **INFO**, below `N-SCOPE-CD`'s LOW, which does print a false diagnostic.

## C6.4 `scripts/check-suite-floors.sh:13` — **CONFIRMED, LOW, fail-OPEN**

`set -uo pipefail`. This is the one that produces a **false clean result**.

Decoy tree containing a `scripts/test.sh` whose six constants are all `1`, script invoked by
absolute path, `rev-parse --show-toplevel` failing:

```
  FOUNDRY_MIN_TESTS          1
  TS_MIN_TESTS               1
  VERIFIER_MIN_TESTS         1
  VERIFIER_MIN_SAMPLES       1
  VERIFIER_MIN_TAMPER        1
  VERIFIER_MIN_TAMPER_MODES  1
suite floors: read from scripts/test.sh, which is the only copy.
EXIT=0
```

**Paired control**, same invocation from the repo root: `92 / 527 / 209 / 7 / 78 / 30`,
`suite floors: read from scripts/test.sh, which is the only copy.`, exit 0. **Second control**,
empty cwd: six `MISSING:` lines and exit **1** — so the script is not simply printing whatever it
is handed; it refuses when there is nothing there.

The output is not merely wrong, it is **self-certifying**: the closing sentence asserts
single-sourcing, from an instrument that has just read a different tree's copy. That is precisely
the failure this script's header says it exists to prevent — *"drifted from the gate's constants
five times — most recently publishing 507/198 while the floors were 513/209, which would have led
a maintainer to LOWER a floor."*

**LOW, not MEDIUM.** The harm shape is serious (a maintainer lowering a floor on false
information) but reachability needs **both** a git-root resolution failure **and** a co-located
`scripts/test.sh` from another tree. It should not be dispositioned as cosmetic: it is the only
one of the four that fails open into a false *statement*.

The repair contract has separately flagged this script's line 15 (`get()` returns the first match,
no duplicate refusal, same `"only copy"` sentence). **Two independent routes to the same false
sentence.** They need separate observing tests.

## C6.5 `scripts/install-hooks.sh:5` — **CONFIRMED, LOW, fail-OPEN**

`set -euo pipefail`. Probed in **sandboxed scratch repositories only** — never against the project
repository, because a worktree shares `.git/config` with its main checkout and `git config
core.hooksPath` would have mutated it.

| cwd | Result |
|---|---|
| its own repo root (control, no shim) | `hooks installed: core.hooksPath=.githooks`, exit 0, config correct |
| a **different** git repo that also has `.githooks/` and `scripts/` | `hooks installed: core.hooksPath=.githooks`, **exit 0** — and `git config --get core.hooksPath` in that **foreign** repo now returns `.githooks` |
| empty dir | `fatal: not in a git directory`, exit **128** |

The middle row is the defect: the script reports success, the operator believes the pre-commit
secret guard is installed, **the intended repository was never touched**, and a foreign repository
was silently reconfigured. **This composes with C4**: the guard that C4 shows can be bypassed is
also the guard this script can fail to install while saying it did.

**LOW** — narrow trigger, no false claim about *measured* content, and the wrong-repo mutation is
recoverable. Named for the composition rather than for its own weight.

## C6.6 `scripts/test.sh:161` — **CONFIRMED, LOW, fail-CLOSED as measured; carries a decision fork**

`set -euo pipefail`; line 161 is the first statement of the gate **body**, which runs as
`bash /dev/fd/9` and inherits the supervisor's cwd.

**Probe.** A decoy tree containing seven stub guard scripts that each print their cwd and exit 0,
with `rev-parse --show-toplevel` failing:

```
== gate immutability (D-056(b)) ==
DECOY-TREE-STUB: check-gate-immutability ran from …/gateprobe
== secret guard (A-007) ==
DECOY-TREE-STUB: check-secrets ran from …/gateprobe
…seven stages, all from the decoy tree, none reporting a failure…
== corpus class coverage (A-036) ==
/dev/fd/9: line 203: ./scripts/check-class-coverage.sh: No such file or directory
…
GATE DID NOT REACH COMPLETION
  The body exited 1 without emitting its completion token.
EXIT=5
```

**Two things are established at once.** The body **did** execute a foreign tree's guards — seven
stages ran the decoy's scripts and printed the decoy's path, so the `cd` no-op is real and it
reaches the gate. And the run **failed closed**: later stages needing `contracts/`, `ts/`, the
ablation generator and the verifier could not run, `fail=1` propagated to `exit 1` at :832-836, the
completion token at :1210 was never emitted, and the A-077 supervisor refused with exit **5**.

**Paired control:** the same script from the correct repo root, working git, fast profile —
`GATE PASSED` at line 991 of the log, exit **0**. So the decoy run's refusal is attributable to the
wrong tree, not to a broken gate at this commit.

**Severity LOW on the evidence I have.** But state the limit honestly: **I did not establish that
this site cannot fail open.** The only decoy capable of reaching `GATE PASSED` is a *complete and
passing second Sentinel checkout* — in which case the gate genuinely passes, **about a different
tree than the script came from**. That is an **attribution** fail-open, and it is this project's
own recorded lesson: *"an exit status is not evidence that the thing you meant to run is the thing
that ran."* I did not run that scenario, because the only such tree available is the project
checkout and running a gate there would have written into it. On that reading the severity is
MEDIUM. I record both rather than picking the convenient one.

**THE DECISION FORK, attached to the CONFIRMED classification (brief §"A finding can be CONFIRMED
*and* carry a decision fork about its remedy").**

`cd "$(git rev-parse --show-toplevel)"` means *"the repository root of the current directory"* —
**not** *"the root of the tree this script lives in"*. Those diverge whenever a script is invoked
by path from outside its own tree, **and they diverge even when git works perfectly**: invoking
`<treeA>/scripts/test.sh` with cwd inside `treeB` cds to **treeB** and gates treeB. Repairing the
`cd ""` half does not touch this; it only removes the last case where the chdir silently does
nothing.

**The fork, which is John's:**

- **(A) Keep caller-relative semantics** — the script gates whatever repository you are standing
  in. Then the repair is only "refuse when the substitution is empty or the command fails", and the
  wrong-tree hazard is accepted and documented.
- **(B) Move to script-relative semantics** — the script gates the tree it belongs to, using the
  `BASH_SOURCE` bootstrap idiom **already present and already exempted at `test.sh:60`**. Then a
  gate result is a statement about the tree the script came from, which is what a reader assumes a
  `GATE PASSED` line means.

This changes what a gate result *asserts*, so it is not an engineering detail. **Not resolved
here.**

## C6.7 `scripts/test.sh:60` — exemption **CONFIRMED**, not a defect

`_gate_src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"`.

Three independent reasons it is not the same construct, each verified:

1. **The argument can never be empty.** `dirname` returns `.` for a bare name and `/dev/fd` for
   `/dev/fd/9` — probed across four spellings, never empty. `cd ""` cannot arise.
2. **Failure is guarded by `&&`.** With a nonexistent directory the substitution yields an empty
   string, `_gate_src` becomes `/foo.sh`, and the very next line `shasum -a 256 <"$_gate_src"`
   fails the redirect — under `set -euo pipefail` the script **aborts, exit 1, nothing runs**:
   ```
   cd: /nonexistent-xyz: No such file or directory
   src=[/foo.sh]
   /foo.sh: No such file or directory
   outer-rc=1
   ```
3. **It is inside a command substitution**, so it does not chdir the script at all — it is a
   location bootstrap, not a working-directory change.

**John's ruling that this is an argued exemption is correct, and it is stronger than an exemption:
it is the model for fork option (B) above.**

## C6.8 Siblings of `N-SCOPE-CD`? — **one obligation, four separate observing tests**

**One obligation.** All four are consumers of a single guarantee, correctly stated by `A-P1`: *a
guard must never convert a failed or empty result from an external command into a statement about
what it measured.* One primitive fixes the mechanism in all four, and the contract's decision to
specify Batch A as primitives-plus-consumers rather than six patches is right.

**Four separate observing tests, because their post-fix behaviours differ and three of the four
are not interchangeable with `N-SCOPE-CD`:**

| Site | Fail direction | What its own falsification must show |
|---|---|---|
| `check-findings-ledger.sh:22` | CLOSED | must refuse *before* reading a ledger, not merely mismatch afterwards — today's refusal comes from `expect`, not from the `cd` |
| `check-suite-floors.sh:13` | **OPEN** | must refuse rather than print six values and `"which is the only copy"` — and this test must be distinct from line 15's duplicate-refusal test |
| `install-hooks.sh:5` | **OPEN** | must refuse **before** `git config` runs; the assertion is a **side-effect** one (no foreign repository's `core.hooksPath` was written), which no other site in this batch needs |
| `test.sh:161` | CLOSED (attribution case open) | must refuse; and the fork in §C6.6 must be answered first, because option (B) changes what the assertion is |

**Merging them into one disposition item would repeat the D-057(1) error the ledger checker exists
to prevent** — grouping is a convenience for deciding, never a reduction in what must be verified.
One primitive, four obligations.

## C6.9 What this evidence does and does not establish

**Establishes:** `cd ""` is a silent success under `set -euo pipefail`; the natural (unshimmed)
condition reproduces every result; two of the four fail open into a false or misleading success,
two fail closed; the gate body genuinely executes a foreign tree's guard scripts; the gate is green
at this commit on the fast profile from the correct root; `test.sh:60` is a different and safe
construct.

**Does not establish:** that `test.sh:161` cannot fail open — see §C6.6. It does not exercise the
deep (`--gate`) profile. It does not sweep for further sites beyond the five scripts named (the
contract's completeness check did that and I did not re-run it). It says nothing about whether
these scripts' *other* checks are correct.

---

## Restoration and hygiene

- All probe files were removed; the adjudication worktree is clean at `a18e6e6`
  (`git diff --cached` empty, no probe paths in `git ls-files --others --exclude-standard`).
- `./scripts/check-secrets.sh` re-run afterwards: `secret guard: clean`, exit 0.
- The project repository was written to **only** at this deliverable's path. `install-hooks.sh` was
  never executed anywhere that could reach the project's shared `.git/config`.
- `scripts/test.sh` was never edited. The one gate run was a read-only fast-profile control from
  the adjudication worktree.
- Trap check: `/usr/bin/grep` was used throughout, and a planted `ZZCANARY_ADJ4_MARKER` was
  confirmed found before any zero result was trusted. One probe (the untracked `.env` pair) is
  recorded in §C4.3 as having **moved nothing**, and is not counted as evidence.
