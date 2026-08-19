# LENS 7 — `ts/src/simulate/**`, `ts/src/propose/**`, `ts/src/tools/**`. DIRECTED.

**Your surface:** the simulation and effect pipeline, the proposal path, and the tools.

**Read this first, because it is the whole reason your lens exists: THESE ARE ~1,400 LINES
THAT NO ROUND HAS EVER ASSIGNED TO ANYONE.** Round five's definition of full breadth
FAILED precisely because nobody was assigned this surface — and the free lens that wandered
into it found a surviving mutation (`C-3`: `internalCalls()`, the entire trace walk behind
`EVAL_CALL_GRAPH_EXPECTED` and the bundle's `internalCallTrace`, could have its body
deleted entirely with the tests still green).

**So your prior should be high.** This is the least-examined substantial code in the
repository, and the one sample anybody has taken from it came back positive.

**What to do:**
- **Mutation-sweep the whole surface.** Delete bodies, flip conditions, empty arrays,
  short-circuit returns. Report every mutation that survives a green suite and gate.
- Start with `internalCalls()` and its neighbours — confirm `C-3` independently (it is
  reviewer-only and was never confirmed), then generalise: **is the surviving-mutation
  property local to that function or true of the whole trace-walking layer?** That
  generalisation is worth more than the individual finding.
- The simulation produces the evidence a receipt commits to. Ask what the simulator can
  report that nothing downstream checks. Recorded `E4`: the receipt's `evidenceHash`
  commits to a §5.6 bundle whose `normalizedAction` and `expectedEffects` are checked by
  neither the signer nor the D-010 verifier. **The verifier half was since BUILT (A-069);
  the signer half is deliberately NOT built and is an open design fork John holds — do not
  re-report the fork, and do not build it.** But the surrounding question — what else in
  that bundle is committed-to and unchecked — is yours.
- `ts/src/tools/**`: anything that writes evidence, results or committed artifacts is a
  laundering route worth probing.

**Confirm each mutation actually took effect and state what it MOVED.** A mutation that
changes nothing observable reads exactly like a caught mutation.

`export PATH="$HOME/.foundry/bin:$PATH"`; `forge build --root contracts` if you touch
anything that runs against the contracts. Baseline first.
