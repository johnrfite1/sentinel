# Demonstration packet — one-page script

Private handoff. No repository. No live chain. No network.

You have three things: this page, a static case viewer, and a Python verifier
that re-checks pre-baked signed receipts.

## 1. Open the case viewer

Open `dashboard/index.html` in a browser. It is a local file. It does not
call a server and does not drive a signer.

Five screens:

- **Case 1** — the call matches the mandate. ALLOW.
- **Case 2** — the agent proposed a different call (unlimited approval to an
  attacker). BLOCK. Caught from the decoded call, not from the agent's story.
- **Case 3** — the load-bearing case. The call is mechanically valid and the
  simulation succeeds. It still BLOCKs because the **purpose** is wrong
  (a different resource than the mandate authorised). Not because the call
  "looks dangerous."
- **Case 4 · REVIEW** and **Case 4 · FAIL_CLOSED** — identical evidence gap
  (target code hash no longer matches the pin). The policy's `failureMode`
  is the only difference. Unresolved is not "malicious."

On every screen, look for: what is bound; who signs what; the check colours;
what the receipt claims; what it does not claim.

## 2. Verify a receipt offline

Needs Python 3.8+ and nothing else. From this packet's root:

```
python3 verifier/verify.py --domain bundles/domain.json bundles/case-1-allow
python3 verifier/verify.py --domain bundles/domain.json bundles/case-3-wrong-purpose-block
```

`--domain` is the trust root **you** assert (the deployment's signer identity).
A bundle that only carries its own copy of that file cannot certify itself.
Without `--domain` the tool reports diagnostics and does not PASS.

Case 3's receipt should still verify: BLOCK is a signed decision, not a
missing artifact.

Optional self-test (mutates a copy in memory; does not write your files):

```
python3 verifier/verify.py --tamper --domain bundles/domain.json bundles/case-1-allow
```

## 3. What you are not being asked to do

Do not start Anvil, Node, Foundry, or a signer. Do not clone a repository.
Do not treat a verified receipt as proof that the simulation is still true
of a chain, or that the target code is benign.
