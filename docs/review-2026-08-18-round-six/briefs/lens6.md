# LENS 6 — `verifier/**`, the D-010 independent receipt verifier. DIRECTED.

**Your surface:** the standalone Python verifier — `verify.py` (the file that decides the
verdict), plus `eip712.py`, `jcs.py`, `keccak.py`, `reasoncodes.py`, `refusal.py`,
`secp256k1.py`, and the test suite.

**Your assignment, worded exactly as the ratified brief words it: LIVE CERTIFICATION
DEFECTS HAVE BEEN FOUND HERE IN THREE CONSECUTIVE ROUNDS, EVERY TIME IN THE PREVIOUS
ROUND'S REPAIRS. FIND THE FOURTH.**

Read that literally. It is not encouragement; it is a base rate. The pattern is that the
repair from round N becomes the defect of round N+1.

**Since round five this file has gained, and NONE of it has been independently reviewed:**
- an asserted trust root (the repair for: *the presenter of a bundle chose the trust root*)
- an override bound to `mandate.principal` (the repair for: *the override stage had no
  deployment-anchored owner identity check; an outsider-minted override verified PASS*)
- both-arrays-must-agree, and absence-is-not-agreement (the repair for: *a precedence-based
  `signerFindings` check that one added key re-opened*)
- A-069's evidence projections

**Attack those four repairs specifically.** For each, ask the question that broke the last
three: *did this generalise the ARGUMENT or only the DEMONSTRATION?* Check `--all` as well
as single-bundle invocation — a previous trust-root repair closed the single-bundle path
and left `--all` certifying the identical hostile tree.

**How to falsify here, and this is the part that goes wrong:** make the bundle **wholly
self-consistent** — re-canonicalise, re-hash, re-bind and **RE-SIGN** — so that only the
check under test can reject it. Modes that mutate a signed field and leave the old
signature are worthless: the signature check fires first and the check you meant to test
never bites. Two shipped tamper modes had exactly that defect.

**Also worth your time:**
- **A green suite is not a correct verifier.** Neutering a check by hand and finding the
  suite still green is the strongest evidence class on this surface. `verify.py` was swept
  once; 14 latent verdict-flippers were recorded, some fixed.
- `H-5` and `H-8` are ACCEPTED limits in §11.0 (misleading "no meta.json" message; `--all`
  over an empty directory printing `0/0 verified` and exiting 0). **Worse-than-recorded
  only.**
- The suite has had tests that never ran: `@unittest.skip`, `@unittest.expectedFailure`
  over a real RFC 8785 violation, and a `setUp` monkeypatch producing `OK (skipped=146)`
  with every assertion disabled while the floor was satisfied. **Check the floor is
  counting tests that actually execute.**

**Python hygiene is mandatory:** `rm -rf` the `__pycache__` and run `python3 -B`. A
same-size mutation in the same mtime second executes stale bytecode and reads as a no-op.
This has bitten this project.

Baseline first: run the verifier suite on the untouched worktree and record the count.
