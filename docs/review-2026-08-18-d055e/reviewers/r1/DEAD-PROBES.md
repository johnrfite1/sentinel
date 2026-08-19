# REVIEWER 1 — DEAD PROBES

**Every probe that measured nothing.** Recorded because five such probes in one 48-hour window
in this project looked exactly like passes.

**I had two.** Both are listed. Neither was allowed to stand as a result.

---

## D1 — My leak hypothesis against `check-gate-immutability.sh` measured a real thing and disproved me. NOT dead, but recorded here because it nearly went the other way.

I observed six stale `sentinel-gate.*` files in `$TMPDIR` and property 4 reporting "7 before,
7 after" — a pass sitting on top of six leaked artifacts. The tempting write-up was "property 4
is a delta check and is blind to the leak it caused".

**I nearly reported that without measuring it.** Instead I re-ran the harness under an isolated
`TMPDIR` and counted directly: 0 before, 0 after. The current harness does not leak. The six
files predate the frozen commit and match the infinite-re-exec bug the code records as fixed.

Filed as **N2 (null result)**, not as a finding. Recorded here because the failure mode was
mine, and the thing that caught it was insisting the probe move something.

---

## D2 — `SENTINEL_TEST_REPORTERS` TAP-destination write: DESIGNED, NOT RUN. Measured nothing.

I identified that `SENTINEL_TEST_REPORTERS` is exported into the TypeScript test process and
carries `--test-reporter-destination=$ts_tap`, so a test file can read the private TAP
destination path out of its own environment — the same "the private channel's path is
broadcast" shape as R1-F1.

**I did not execute it.** No test file was written, nothing was run, no count was moved. The
theoretical defeat requires appending a later `# tests N` line after node's own TAP reporter
emits its trailing summary, which `sed … | tail -1` reads — a race I did not attempt to win.

**This probe measured nothing and I am not claiming anything from it.** It is named in N4 as
an unexplored route with a reason for stopping (the floor's stated bound is "a ratchet against
ACCIDENT, not against intent"), and it is named again in COVERAGE.md as unreached. It is
explicitly **not** a lead, because I have no evidence it is exploitable at all.

---

## Probes that were checked for danger BEFORE being believed

Recorded because the brief requires that a probe be shown to move something.

- **The in-place edit in `probe-snapshot-reachable.sh`** uses the identical shape the project's
  own harness uses (`python3 open(path,"w")`, prepend 40 lines, same inode) — the shape the
  repository records as the one that corrupted two real runs, and the one that replaced the
  harness's original `mv` after `mv` was found to pass against no protection at all. Its danger
  is not assumed: **both arms produced a shell syntax error and a dead run**, so the probe
  demonstrably moved the thing it was aimed at. A silent pass would have been the dead-probe
  case and would have proved nothing.
- **The bootstrap extraction** in the same probe was verified before use: 104 lines extracted,
  `SENTINEL_GATE_SNAPSHOT` present, with an explicit `exit 1` on a miss. Testing an empty
  bootstrap is the exact dead-probe failure this repository has recorded five times.
- **`check-review-scope.sh`'s baseline was captured before the probe** and the probe changed the
  output (37 → 0, and the `preservation-only` line disappeared). Had the output been identical
  I would have measured nothing.
- **The deep gate was read, not statused.** `GATE PASSED` was confirmed present by grep and the
  profile confirmed as `gate`; exit 0 alone was treated as no evidence, per the brief's warning
  that a previous run exited 0 without ever printing `GATE PASSED`.
