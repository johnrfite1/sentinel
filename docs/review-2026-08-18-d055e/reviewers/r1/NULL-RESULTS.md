# REVIEWER 1 — NULL RESULTS

Things I attacked and found SOUND. Recorded so the next round knows where not to look again.
Each entry states what I actually ran, not what I read.

**Commit:** `7e0ab7f1057de278c09cc803ab4ca266f53399e1`.

---

## N1 — The deep gate profile genuinely runs from a symlinked frozen worktree, and genuinely passes.

Round six could not run it at all (four remappings resolved instead of five). R1's brief said
"verify the deep gate actually runs here — do not assume."

Ran: `forge build --root contracts && ./scripts/test.sh --gate`, ~50 minutes wall clock,
full output in `deep-gate-run.txt` (1298 lines).

Verified by reading the output, not the status:
- `== solidity build + tests (profile: gate) ==` — the deep profile engaged (line 134).
- `GATE PASSED` present at line 946 — the failure mode the brief warned about (exit 0 with no
  `GATE PASSED`) did **not** occur.
- `GATE EXIT CODE: 0`, `forge build exit: 0`.
- No `GATE FAILED`, no `FLOOR BREACHED`, no `GATE SOURCE CHANGED`, no `SUITE NOT CLEAN`.
- Counts printed: foundry 75 (floor 75), 75 passed / 0 failed / 0 skipped; typescript 513
  (floor 513); verifier suite 209 (floor 209), samples 7 (floor 7), tamper 78 cases / 30 modes
  (floors 78/30).
- `50 committed view files match the current code`; `51 result files identical to the committed
  set`; ablation report `regenerates byte-for-byte`.

**Sound.** `auto_detect_remappings = false` fixed what round six could not run. This is the
one condition of the round and it is discharged.

---

## N2 — `check-gate-immutability.sh` does not leak snapshots. My hypothesis was wrong.

I found **six** stale `sentinel-gate.*` files in `$TMPDIR` (dated Aug 18 17:40–17:41) and
confirmed by content that they are the harness's **own synthetic subjects** — they carry the
bootstrap and end in `echo "BODY COMPLETED"`. The harness's property 4 reported "7 before,
7 after" during my deep run, i.e. it passed while six of its own leaked artifacts sat on disk.

I hypothesised the current harness leaks and that property 4's delta comparison hides it.
**It does not.** Measured directly under an isolated `TMPDIR`:

```
T=$(mktemp -d .../probes/tmpiso.XXXXXX)
find "$T" -maxdepth 1 -name 'sentinel-gate.*' | wc -l      # 0
TMPDIR="$T" ./scripts/check-gate-immutability.sh            # rc=0
find "$T" -maxdepth 1 -name 'sentinel-gate.*' | wc -l      # 0
```

Output in `probe-harness-leak.out`. Zero before, zero after, across all six subjects — not just
the two property 4 counts around. The six stale files predate the frozen commit and are
consistent with the infinite-re-exec bug the bootstrap's own comments record as fixed
(each re-exec created a fresh snapshot).

**Sound.** Recorded because a null here is worth as much as a finding: this is the only one of
the harness's five properties I could not break, and I attacked it directly.

*Bounded limit, not a defect:* property 4 is a delta over a shared directory, so it isolates the
subjects under test from ambient state — which is the right design — and correspondingly says
nothing about snapshots leaked by anything else.

---

## N3 — Absence genuinely fails rather than skips on both suite-count stages.

The brief's named class ("a check that emits nothing when a field is missing"). Read
`scripts/test.sh` lines 255–360 and confirmed both stages close it explicitly:

- Foundry: `if [ -z "${f_total:-}" ]` → `FOUNDRY SUITE PRODUCED NO REPORT — treating as failure,
  not as clean.` + `fail=1`.
- TypeScript: `if [ -z "${ts_tests:-}" ]` → `TYPESCRIPT SUITE PRODUCED NO TAP REPORT — treating
  as failure, not as clean.` + `fail=1`.

Both also assert `skipped`/`todo` separately from the floor, because those are counted in the
total — closing the `vm.skip(true)` and `Ran 146 / OK (skipped=146)` defeats the file records.

**Sound.** This is the pattern `check-review-scope.sh` (R1-F2) fails to apply to itself; the
same author closed it correctly here two hundred lines earlier, which is why R1-F2 is a defect
rather than an unknown standard.

---

## N4 — The count floors are not defeatable by *accidental* shrinkage, and the intentional defeat is a recorded limit.

Attacked the brief's question "can you shrink a suite and stay green?".

- The Foundry count comes from `forge test --json`, parsed per-test out of a structured object;
  a Solidity test's `console.log` is captured *into* the object as `decoded_logs` rather than
  interleaved with it. The three recorded "count the tests" defeats all relied on the suite
  writing the line the gate read. That route is closed.
- The TypeScript count comes from a **second** TAP reporter writing to a private `mktemp` file
  while `spec` output goes to stdout. A test writing `# tests 9999` to stdout does not reach it.
- Deleting tests lowers the count and breaches the floor; disabling assertions is caught by the
  separate `skipped`/`todo` assertions.

*One residual I checked and am NOT reporting as a finding:* `SENTINEL_TEST_REPORTERS` is
exported into the test process and contains the TAP destination path, so a test file could in
principle read `process.env.SENTINEL_TEST_REPORTERS` and write into the reporter's destination.
I did not reproduce this — `sed | tail -1` takes the reporter's own trailing `# tests N`, and
beating it requires winning a race after the reporter closes. More importantly, the floor's
header states its own bound in terms that cover this: *"this is a ratchet against ACCIDENT, not
against intent."* Defeating it from inside a malicious test is intent, and re-reporting a
recorded limit is not a finding. **Named here so the next round does not spend the same hours,
and flagged as the one place I stopped short of a reproduction.**

---

## N5 — A-074's conformance comparison does bind only to ALLOW, and does run on every verification path.

The brief asked both questions directly.

- `_allow_conforms_to_the_mandate` (verify.py:1348) returns early on
  `evidence.get("verdict") != "ALLOW"` — BLOCK and REVIEW bundles stay verifiable, which is
  correct and is what `case-3-wrong-purpose-block` requires.
- It is called from exactly one site (verify.py:1521) inside `_evidence_describes_the_bundle`,
  which is itself called from **two** places: `_refusal_checks` (verify.py:911, the §5.5.1 path)
  and `_chain_checks` (verify.py:1629, the receipt path). Verified by exhaustive grep — those
  are the only two call sites in the file.
- Absence fails rather than skips at every gate inside it: a non-dict
  `decodedSelectorAndParameters`, a non-dict `parameters`, an absent mandate, `decoded` not
  true, and an unrecognised `schema` each append a **failing** `Check` and return. There is no
  `skipped=True` anywhere in the function.
- The escape I looked for — set `evidence.verdict` to something other than `"ALLOW"` (including
  a case variant like `"Allow"`) so conformance is skipped while the receipt still decodes to
  ALLOW — is closed by the sibling check at verify.py:1667–1679, which fails both when
  `verdict` is absent (`if not (isinstance(evidence, dict) and "verdict" in evidence)`) and when
  it disagrees with `VERDICT_NAMES[receipt["verdict"]]`.

**Sound as far as I probed it.** See COVERAGE.md — I did **not** build a wrong-purpose ALLOW
sample and run it through, so this is a reading-plus-grep result, not an executed defeat.

---

## N6 — `check-review-scope.sh`'s partition arm is correct, and its header's self-correction is honest.

The first arm (every tracked file assigned to exactly one reviewer) works: 371 of 371 assigned,
`R1=175 R2=46 R3=150`. I confirmed the header's own disclaimer is accurate rather than
face-saving — `assign()` is a `case`, `case` returns on first match, so overlap is genuinely
resolved-not-reported, and the header says exactly that after having been corrected once for
claiming otherwise. The ordering-is-the-specification argument holds.

**Sound.** The defect is in the *second* arm (R1-F2) and in the fact that nothing runs it
(R1-F3), not in the partition.

---

## N7 — The bootstrap's stated race on the copy is genuinely checked, and its stated residual is honest.

`scripts/test.sh` hashes the source before the copy, hashes the copy, and re-hashes the source
after, refusing to start (exit 3) if any of the three disagree. The stated residual — "a torn
read that happened to leave the file byte-identical is indistinguishable from no write at all"
— is the correct bound for a hash comparison and is stated rather than glossed.

The `_gate_self` / `_gate_snap` path resolution through the same `cd … && pwd` on both sides is
correct and the `/var` → `/private/var` hazard it exists for is real on this machine.

**Sound.** My R1-F1 is not about this; the copy is fine. The problem is what happens to the
snapshot *after* the exec.
