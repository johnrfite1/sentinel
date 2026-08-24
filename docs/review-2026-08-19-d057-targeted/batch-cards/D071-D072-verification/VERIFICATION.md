# D-071 / D-072 — INDEPENDENT VERIFICATION

# VERDICT: **HOLD**

Every REQUIRED row that was actually measured at HEAD passed. Controls fired before observe on those rows. Independent probes `[V]` and the frozen harness `[H]` agree where both ran. No measured REQUIRED failed.

**Redaction (John, session four, 2026-08-23).** Live D-008(2)/(4) scanner literals in this file were replaced with named tokens (`<D-008-2-label>`, `<vendor-name>`). **Verdict HOLD is unchanged. No row score, no reasoning, and no confounder logic is changed.** The tokens stand in for the literals that were in this file (and in the committed card files the R5-5 confounder names) at the freeze this document scored. The frozen-harness sha256 recorded below was measured before this redaction; after vendor plants were synthesised at run time the harness hash moved. That movement is recorded in RECORD.md. This paragraph does not re-pin the hash.

This document does not assign severity. It does not lift D-067. It does not give a D-055 verdict. It does not change production.

**Authority:** D-058(1) third role — independent of the test author and of the implementer. CARD.md is the contract. EXPLOIT-CONTROL.md is the control protocol. BASELINE-RESULTS.md is the author's FAIL-at-parent claim, not this score.

**Verifier identity:** this agent did not write the Phase B / A-101 repairs and did not write `d071-d072-observe.sh` or CARD.md.

## SHAs measured on this machine (not taken from the brief)

| Role | SHA |
|---|---|
| HEAD / freeze scored | `bdacace71e47c55301100d27341e67fc422fbcde` |
| Contract commit (HEAD) | `bdacace71e47c55301100d27341e67fc422fbcde` — files only under `docs/review-2026-08-19-d057-targeted/batch-cards/D071-D072-verification/` |
| R5 repair | `1ae684cec83c7bfdb24a8c18ffdeba87c535874f` |
| R5 parent (baseline) | `558d001546b55bd80156bc875cf080fef0e301eb` |
| V-6/R2 repair | `4ad6036d81fa66a35a0c3efb4eab117438e3ca38` |
| V-6/R2 parent | `1ae684cec83c7bfdb24a8c18ffdeba87c535874f` |

All three of R5 parent, R5 repair, and V-6 repair are ancestors of HEAD.

**Machine:** `git version 2.50.1 (Apple Git-155)`, `GNU bash, version 3.2.57(1)-release (arm64-apple-darwin25)`, Darwin 25.5.0.

**Frozen harness sha256**, measured before `[H]` and after `[H]` — unchanged:

`e24443d1fc365e09a691650e8a69bd68a7b4768fde92f2c7da816e3b7e35d12e`  `d071-d072-observe.sh`

The harness was not patched. CARD.md, EXPLOIT-CONTROL.md, and baseline logs were not modified.

---

## 0. METHOD

1. Captured `git status --porcelain` and `git stash list` before any clone or worktree. Stash empty. Dirty tree: `M README.md`, `?? .serena/`, `?? assets/`. Those paths were not discarded, stashed, or staged.
2. Re-measured SHAs, `git help config` ENVIRONMENT, `git help gitignore`, `git help config` `core.excludesFile` / `core.quotePath`, live script names, the ack variable from `scripts/check-rename-gate.sh`, and how `scripts/test.sh --gate` invokes the rename-gate.
3. Wrote independent probes from CARD.md's matrix. They share no functions with `d071-d072-observe.sh`. Results labelled `[V]`. Plants and credential-shaped values were synthesised at runtime. Logs kept under `logs/verifier/` are redacted.
4. Exploit control before observe, every row. A row whose control did not fire is NOT_MEASURED, not a pass.
5. Then ran the frozen harness against HEAD worktree subjects (`--r5-subject` / `--v6-subject` = detached worktree at HEAD). Results labelled `[H]`. `[H]` used `--skip-toplevel` because `[V]` had already completed `./scripts/test.sh --gate` (~22 minutes). Re-running the same instrument through the harness would not add a second observation of `GATE PASSED`; it would spend another twenty minutes to print the same fail path.
6. Isolated clones: `git worktree add --detach` plus `git clone --local --no-hardlinks`. The main worktree was never checked out to another SHA.
7. Output was read, not just exit status. `GATE PASSED` is a string. `UNVERIFIED` is a string. The ack name was required **on** the UNVERIFIED line for R5-1.

UNVERIFIED was produced by an isolated clone whose origin is a local path. It was not faked by breaking the script.

---

## 1. LIVE NAMES (re-measured)

From `git help config` ENVIRONMENT on this machine:

- `GIT_CONFIG_COUNT`, `GIT_CONFIG_KEY_<n>`, `GIT_CONFIG_VALUE_<n>` (zero-indexed)
- `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM`
- `GIT_CONFIG_NOSYSTEM`
- `GIT_CONFIG` — git-config command only (out of this card)

From `git help git` ENVIRONMENT: `HOME`, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM`, `GIT_CONFIG_NOSYSTEM`. `XDG_CONFIG_HOME` appears in the GLOBAL stanza (`$XDG_CONFIG_HOME/git/config`).

From `git help gitignore` / `git help config`:

- `core.excludesFile` defaults to `$XDG_CONFIG_HOME/git/ignore`, else `$HOME/.config/git/ignore`
- `core.quotePath` (default true; unusual bytes quoted/octal-escaped)

**Ack variable** from `scripts/check-rename-gate.sh`: `ACK="${SENTINEL_RENAME_GATE_UNVERIFIED_OK:-}"`. That name is printed on the UNVERIFIED line.

**Live scripts:** `scripts/check-rename-gate.sh`, `scripts/check-secrets.sh`, `scripts/check-vendor-honesty.sh`, `scripts/test.sh`.

**How `scripts/test.sh --gate` invokes the rename-gate:** `PROFILE=gate` when `$1` is `--gate`. Then `./scripts/check-rename-gate.sh --gate || fail=1`. A failed step sets `fail=1` and the script **continues**. `GATE PASSED` is printed only if `fail` is still 0 at the end. A failed body does **not** emit the completion token; the supervisor then prints `GATE DID NOT REACH COMPLETION` and exits 5. That is the designed fail path, not an aborted run. `[V]` R5-5 was allowed to finish (~22 minutes: `gate_start=2026-08-23T22:36:46Z`, `gate_end=2026-08-23T22:58:18Z`).

The live pin, where it holds, is command-line `-c core.excludesFile=` and `-c core.quotePath=false` at the enumerating `git ls-files --others --exclude-standard` call. This verification scores **behaviour**, not a source grep of those flags.

---

## 2. PER-ROW RESULTS AT HEAD

`[V]` = independent probe. `[H]` = frozen `d071-d072-observe.sh` against HEAD. Agreement is stated as agreement, not as one measurement.

| Row | Control fired? | `[V]` | `[H]` | Agree? | Evidence |
|---|---|---|---|---|---|
| R5-C-unverified-origin | yes — origin local path | PASS | PASS | yes | `logs/verifier/r5-iso.meta`; harness `r5-unverified-clone.meta` |
| R5-C-unverified-output | yes — `UNVERIFIED`, not "no remote" | PASS | PASS | yes | `r5-1-fast.log` |
| **R5-1-fast-varname** | yes | **PASS** — exit 0, UNVERIFIED line names `SENTINEL_RENAME_GATE_UNVERIFIED_OK` | **PASS** | yes | `r5-1-unverified-line.txt` |
| **R5-2-deep-refuse** | yes | **PASS** — `--gate` rc=1 | **PASS** rc=1 | yes | `r5-2-deep.log` |
| **R5-3-deep-ack-disclose** | yes | **PASS** — rc=0 and own output: "This --gate run ACKNOWLEDGES D-016 was not verified; it was acknowledged, not verified private." | **PASS** | yes | `r5-3-ack.log` |
| R5-C-gh-private | yes — `gh repo view johnrfite1/sentinel` → `PRIVATE` (operator `HOME`) | PASS | PASS | yes | `r5-4-re2-gh.out`; harness `r5-4-gh.out` |
| **R5-4-readable-clean** | yes (second measurement) | **PASS** — fast rc=0, `--gate` rc=0, `rename gate: clean (johnrfite1/sentinel is private; D-016 publication block intact)` | **PASS** | yes | `r5-4-re2-fast.log`, `r5-4-re2-deep.log`, `r5-4-re2-gh.out` |
| R5-C-clone-still-unverified | yes — pre-gate `--gate` still UNVERIFIED | PASS | n/a (`[H]` skipped toplevel) | — | `r5-5-precheck.log` |
| **R5-5-toplevel-gate** | yes | **PASS** — no `GATE PASSED`; body printed `GATE FAILED`; supervisor exit 5 | NOT_MEASURED (`--skip-toplevel`) | n/a | `r5-5-gate.raw`, `r5-5-gate.rc`, `r5-5-gate.meta` |
| V6-COUNT-secrets | yes (potency + exploit) | **PASS** | **PASS** | yes | `V6-COUNT-secrets.*` |
| V6-COUNT-vendor | yes | **PASS** | **PASS** | yes | |
| V6-GLOBAL-secrets | yes | **PASS** | **PASS** | yes | |
| V6-GLOBAL-vendor | yes | **PASS** | **PASS** | yes | |
| V6-SYSTEM-secrets | yes | **PASS** | **PASS** | yes | |
| V6-SYSTEM-vendor | yes | **PASS** | **PASS** | yes | |
| V6-NOSYSTEM-secrets | **no** — `GIT_CONFIG_NOSYSTEM=1` did not hide | NOT_MEASURED | NOT_MEASURED | yes | inert on this machine, as the test author already marked |
| V6-NOSYSTEM-vendor | **no** — same | NOT_MEASURED | NOT_MEASURED | yes | |
| V6-HOME-secrets | yes | **PASS** | **PASS** | yes | `$HOME/.config/git/ignore` |
| V6-HOME-vendor | yes | **PASS** | **PASS** | yes | |
| V6-XDG-secrets | yes | **PASS** | **PASS** | yes | `$XDG_CONFIG_HOME/git/ignore` |
| V6-XDG-vendor | yes | **PASS** | **PASS** | yes | |
| R2-C-unquoted | yes — café octal-quoted; `[ -f ]` false; ASCII sibling usable | PASS | PASS | yes | `r2-unquoted.ls.txt` |
| R2-C-payload | yes — ASCII vendor plant blocked | PASS | PASS | yes | |
| **R2-vendor** | yes | **PASS** — vendor-honesty blocked the café plant | **PASS** | yes | `r2-vendor-observe.log` |
| R2-C-z | yes — `-z` still contains raw café bytes | PASS | PASS | yes | `r2-z-meta.txt` |
| R2-secrets | `-z` did not drop | NOT_MEASURED | NOT_MEASURED | yes | not claimed |

V-6 REQUIRED on every counted row: after the vector, the production consumer still SEES/BLOCKS the plant; unpinned `git ls-files --others --exclude-standard` (no `-c core.excludesFile=`, no `-c core.quotePath=false`) HIDES/DROPS the plant.

---

## 3. NOT_MEASURED (not counted)

- **V6-NOSYSTEM-secrets**, **V6-NOSYSTEM-vendor** — exploit control did not hide. This machine's system config is not the excluder. The harness does not write `/etc/gitconfig`.
- **R2-secrets** — unpinned `ls-files -z` still contains the raw café path, so `-z` is not the drop. Secrets already uses `-z`; R2 is not claimed against secrets.
- **`[H]` R5-5** — skipped by `--skip-toplevel`. **`[V]` R5-5 was measured** (see §2). It is not a hole in the HEAD score.
- **First `[V]` R5-4 attempt** — invalid probe, discarded. The control `gh repo view` ran with operator `HOME` and printed `PRIVATE`, but the script was invoked with `HOME` sandboxed, so `gh` inside the script could not authenticate. CARD requires the *script* to see PRIVATE. Remeasured with operator `HOME`: control still PRIVATE; fast and `--gate` both `rename gate: clean`, rc=0. That remasurement is the `[V]` R5-4 score. `[H]` R5-4 independently PASS.

---

## 4. DID ANY REQUIRED FAIL AT HEAD?

**No.** Every counted REQUIRED passed at HEAD.

R5-1 names the ack variable on the UNVERIFIED line (exit 0 is not the row by itself). R5-2 deep/UNVERIFIED/no-ack refuses. R5-3 discloses acknowledgement, not verification. R5-4 clean when visibility is readable. R5-5 top-level `./scripts/test.sh --gate` on a local-origin clone with ack unset does not print `GATE PASSED` and exits non-zero. V-6 counted vectors: consumer still blocks; unpinned listing hides. R2-vendor: café plant blocked.

---

## 5. R5-5 OUTPUT (read, not guessed)

Pre-gate on the isolated clone (origin `/tmp/sentinel-v-d071/head-wt`, HEAD `bdacace71e47c55301100d27341e67fc422fbcde`):

```
rename gate: UNVERIFIED (deep/--gate refuses unless SENTINEL_RENAME_GATE_UNVERIFIED_OK=1) — could not read visibility for /tmp/sentinel-v-d071/head-wt (auth? network?).
```

`npm --prefix ts ci` was run **in that clone** (`npm_rc=0` in `r5-5-gate.meta`). Then `./scripts/test.sh --gate` was allowed to finish.

- Rename-gate step ran and printed UNVERIFIED (fail=1 set; script continued).
- Later stages ran: foundry, typescript 550, corpus, D-010 verifier.
- Line with standalone `GATE FAILED`.
- **No `GATE PASSED`.**
- Supervisor: `GATE DID NOT REACH COMPLETION` because the body exited 1 **without emitting the completion token**. That is `scripts/test.sh` lines 893–897 and 154–159: a failed gate is designed not to emit `GATE PASSED`. Exit status of the supervisor: **5** (`r5-5-gate.rc`). Non-zero.

This is not a script-only `check-rename-gate.sh` result. It is the top-level instrument completing its fail path.

**Confounder, stated so it is not hidden:** vendor-honesty also failed on this clone because **committed** card files (`EXPLOIT-CONTROL.md`, `d071-d072-observe.sh`, baseline `logs/v6-*-vendor.potency.log`) contain `<D-008-2-label>` and `<vendor-name>`. Those files are in HEAD. So `fail=1` has more than one cause. Rename-gate **did** refuse UNVERIFIED/no-ack. `GATE PASSED` was withheld. The REQUIRED is that pair, not "rename-gate was the only failing step."

---

## 6. WORKING TREE BEFORE / AFTER

**Before any clone/worktree/probe:**

```
 M README.md
?? .serena/
?? assets/
```

Stash: empty.

**After probes, harness, and this file:**

```
 M README.md
?? .serena/
?? assets/
?? docs/review-2026-08-19-d057-targeted/batch-cards/D071-D072-verification/VERIFICATION.md
?? docs/review-2026-08-19-d057-targeted/batch-cards/D071-D072-verification/logs/verifier/
```

Stash: still empty. `README.md`, `assets/`, `.serena/` were not staged, discarded, or restored. No `git checkout` of the main worktree. No `git add -A`. Production trees (`scripts/`, `.githooks/`, `ts/`, `contracts/`) were not modified. The frozen harness hash is unchanged.

---

## 7. BLIND SPOTS

- **One git, one OS.** `git version 2.50.1 (Apple Git-155)` on macOS. Another git's quote-path or COUNT handling is unmeasured.
- **NOSYSTEM** is inert unless the real system config already excludes the plant. Not forced.
- **R2-secrets** not claimed; `-z` keeps the café path.
- **R5-5 confounder:** committed test-contract text trips vendor-honesty on a HEAD clone of this card. `GATE PASSED` withhold has more than one `fail=1` contributor. Rename-gate refusal was observed in the same log.
- **`[H]` R5-5 not re-run.** `[V]` completed the top-level instrument. The harness treats `GATE DID NOT REACH COMPLETION` as NOT_MEASURED; at HEAD that string is the supervisor's designed response to `GATE FAILED`. Scoring `[H]` R5-5 through the harness would likely mark NOT_MEASURED even on a complete fail path. `[V]` scores CARD: no `GATE PASSED`, non-zero.
- **HOME sandbox vs gh.** A verifier probe that sandboxes `HOME` for git isolation will make `gh` fail auth. R5-4 must be run with the operator `HOME` that the control used. The discarded first attempt is not a product FAIL.
- **XDG/HOME observe latency.** Some `check-secrets.sh` runs under injection took tens of seconds to minutes; they completed and blocked. Not scored as a separate hole.
- **Does not claim** every git config key. Matrix is CARD's hide-untracked vectors against the two production untracked consumers.
- Source greps of `-c core.excludesFile=` were not used as a substitute for the hole.

---

## 8. WHAT THIS DOCUMENT DID NOT SCORE

- Severity. No SEVERITY.md.
- D-055. No verdict, recommendation, or follow-on plan on that criterion.
- D-067. Named completeness limits stay named. This HOLD does not lift them.
- Gate signing. Publication. Push. Rename. D-016's other verbs.
- The five D-008 comprehension questions (not seen, not guessed).
- Parents were not re-run as a full matrix; BASELINE-RESULTS.md is the author's FAIL-at-parent claim. SCORE is of HEAD.
- `scripts/check-v1-index-ordering.sh` (out of CARD).

---

## 9. CONTRACT VALIDITY

The frozen harness ran against HEAD subjects without being patched. Controls fired on the rows that were counted. UNVERIFIED was a local-path origin, not a broken script. The contract is valid. HEAD is scored HOLD. The harness is not invalid; this is not a STOP.
