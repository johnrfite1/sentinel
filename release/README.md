# Sentinel enforcement release v0.3

This publication tree contains the enforcement contract, ABI and bytecode,
compiler metadata, a focused adversarial test, the isolated signer/evaluator
runtime, a cold demo, and the independent publication verifier.

No deployment identity inside this tree is trusted. A certifying verifier run
requires an authority address obtained independently from the publisher and a
manifest signed by that authority. `domain.json` is not accepted as a trust
root. No private key or fixed private-key fixture is included.

## Cold demo

From this directory:

```sh
npm --prefix ts ci
forge build --root contracts
npm --prefix ts run cold-demo
```

The demo creates fresh owner, isolated-signer, and deployment-authority keys in
memory for that run. It deploys to a fresh Anvil, owner-signs and activates a
signer-bound mandate, evaluates and signs in the separate signer process,
verifies the signed deployment manifest and current receipt, rejects an
unauthenticated authority and altered calldata, executes the exact call, and
rejects replay. It prints the temporary evidence path and the authority address
that a real verifier would obtain out of band. Private keys are never written.

## Independent verification

```sh
python3 verifier/verify_publication.py SAMPLE_DIR   --deployment-manifest DEPLOYMENT_MANIFEST.json   --deployment-authority 0xADDRESS_OBTAINED_OUT_OF_BAND
```

The verifier enforces one fail-closed predicate: authenticated deployment
chain/vault/owner/signer; owner-signed mandate naming that signer; exact action,
calldata, policy, and nonce commitments; and `issuedAt <= now < expiresAt`.

`MANIFEST.sha256` covers every released file other than itself. Publication or
deployment is a separate user decision; assembling this tree does not push,
publish, or bless a production authority.
