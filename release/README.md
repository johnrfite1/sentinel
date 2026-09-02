# Sentinel enforcement release v0.3

This publication tree contains the enforcement contract, ABI and bytecode,
compiler metadata, a focused adversarial test, the isolated signer/evaluator
runtime, a cold demo, and the independent publication verifier.

No deployment identity inside this tree is trusted. A certifying verifier run
requires an authority address obtained independently from the publisher and a
manifest signed by that authority. `domain.json` is not accepted as a trust
root.

**No known development key was detected by these checks.** The assembler screens
every file it places in this tree against a fixed denylist of known development
private keys and against a fixed-key-assignment pattern, and refuses to produce
the tree on a hit. That is a check result, not a proof of absence: a denylist
can only establish that the keys it knows about are not present. The earlier
wording here — "No private key or fixed private-key fixture is included" —
asserted the absence itself, which no denylist can support. It is corrected
here rather than quietly dropped.

## What this release does not bound

Stated in the file a reader meets first, because this boundary was previously
disclosed only in a code comment. The full statement is the `@dev` header of
`contracts/src/SentinelVault.sol`, which ships in this tree.

`SentinelVault` is an execution harness, not a production wallet. Its onchain
backstops bound the SHAPE of a single action — target and selector allowlists,
calldata hash, chain and vault binding, nonce ordering, and a native-value
ceiling — and let the owner pause, revoke and recover. They do not bound
cumulative loss, nor the rate at which it happens:

* **The native-value ceiling is PER ACTION only.** `maxNativeValueWei` is
  compared once for each action. No cumulative, rate-limited or velocity bound
  exists anywhere in `contracts/src`.
* **The drain is atomic.** A relayer contract can call `executeWithReceipt`
  repeatedly inside ONE transaction; `nonReentrant` stops nesting, not
  repetition. Measured: ~100 sequential valid ALLOW receipts, each at exactly
  the cap, drain a funded vault to zero in a single transaction at ~75,700 gas
  each, with `block.number` and `block.timestamp` unchanged throughout.
* **`pause` cannot land during that drain.** Pausing protects only BEFORE
  execution begins or BETWEEN transactions. There is no interval inside the
  drain in which an owner transaction could be included, and nothing to notice
  while it runs.

This is an explicitly accepted v1 boundary of a testnet lab, not an open defect,
and no cumulative or rate bound is promised. The demonstration is
`test_LIMIT_nativeCeilingIsPerActionAndBoundsNoAggregate` in
`contracts/test/SentinelVault.backstops.t.sol`, which is **not shipped in this
tree**; the only contract test here is
`contracts/test/PublicationWithdrawal.t.sol`.

### Token authority is not bounded at all, and the signed policy suggests it is

Everything above bounds the NATIVE-VALUE dimension. Token authority is a second
dimension, and it has no onchain bound of any kind.

`PolicyPayload.maxAllowanceIncreaseBaseUnits` is a field of the **signed**
policy. It is in the struct at `contracts/src/types/SentinelTypes.sol`, in the
EIP-712 type string, and inside the `policyHash` that the mandate, the action
and the receipt all commit to. **No contract in this tree reads it.** `grep -n
allowance contracts/src/SentinelVault.sol` returns nothing, and the publication
verifier does not evaluate it either — see the policy limit under "Three limits
of that predicate" below.

**Say plainly why that is worse than an ordinary missing feature: the schema
itself is the misleading surface.** A reader who meets an allowance ceiling
inside a signed policy type can reasonably conclude an allowance ceiling is
enforced. It is not — not by the Vault, not by the verifier, and not by anything
a recipient can check offline.

One valid ALLOW receipt for `approve(spender, type(uint256).max)` on an
allowlisted target passes every onchain check: pause, chain, vault, nonce,
deadline, mandate, policy, operation, `dataHash`, target allowlist and selector
allowlist. The native-value ceiling never engages, because `valueWei` is zero.
The Vault's entire balance of that token is then transferable by the spender,
for one consumed nonce and in one transaction. Unlimited approval is the
flagship prompt-injection case this harness exists to measure, so it is refused
by the CONFORMANCE EVALUATOR with nothing behind it: the evaluator is the only
layer that reads the field.

Read together with the drain, the v1 boundary is one sentence. The Vault's hard
caps bound a native-value dimension and no other, so **zero native value at risk
is not zero economic exposure.**

This too is an explicitly accepted v1 boundary of a testnet lab, ruled rather
than overlooked: correct the claim now, defer an onchain allowance cap to a
later version. It is not an open defect, and a per-action allowance-increase
ceiling is recorded as owed work for that later version rather than delivered
here. The demonstration is
`test_LIMIT_vaultCapsNativeValueOnlyAndNotTokenAuthority` in
`contracts/test/SentinelVault.backstops.t.sol`, **not shipped in this tree**. It
asserts the LIMIT rather than a protection, so if a cap is ever added that test
fails, and the failure is the signal to correct this section rather than to
delete the test.

## Version tags: the evidence and refusal envelopes say v0.2

This is a v0.3 release whose evaluator emits evidence tagged v0.2. That is
deliberate and stable, and it is stated here because a reader has no way to tell
a frozen identifier from an un-migrated one.

The evidence bundle carries `"schema": "sentinel.evidence.v0.2"`
(`ts/src/evaluate/index.ts`), and the refusal record's signing preimage opens
with `sentinel.refusal.v0.2` (`REFUSAL_DOMAIN_TAG` in
`ts/src/signer/eip712.ts`). Both files are in this tree; the publication
profile, the EIP-712 domain version and the verifier are v0.3.

Neither tag is a label on the outside of the envelope. The evidence tag is a
field of the canonical bundle that `evidenceHash` is taken over, and
`evidenceHash` is a field of the signed receipt. The refusal tag is the first
line of the refusal digest's preimage, chosen so that a refusal signature can
never be reinterpreted as an EIP-712 receipt signature. **Renumbering either one
changes what is signed** and invalidates every receipt, refusal and sample
already issued under it, so the tags were frozen for the v0.3 work by an
explicit ruling rather than by inattention. Whether they are renumbered is a
v1.1 question.

Read a tag as naming the ENVELOPE, not the release that ships it. The bundle's
field shape is the v0.2 shape and is unchanged. What the envelope carries is
not frozen with the tag: `policyChecks` lists whatever checks the evaluator ran,
so a v0.3 check appears as a row inside a bundle tagged
`sentinel.evidence.v0.2`. Take the check inventory from the evaluator, not from
the tag. Nothing here is a v0.2 artifact that escaped a rename, and no version
skew is implied.

## Cold demo

From this directory:

```sh
npm --prefix ts ci
forge build --root contracts
npm --prefix ts run cold-demo -- --output "$PWD/demo-out"
```

`--output` is optional; without it the demo writes under the system temporary
directory and prints the path. Name it, as above, if you intend to re-run the
verifier by hand afterwards ("Independent verification", below). Give an
absolute path: `npm --prefix` runs the script from `ts/`, so a relative one
lands there.

The demo creates fresh owner, isolated-signer, and deployment-authority keys in
memory for that run. It deploys to a fresh Anvil, owner-signs and activates a
signer-bound mandate, evaluates and signs in the separate signer process,
verifies the signed deployment manifest and the receipt, executes the exact
call, and runs typed negative controls. Each negative asserts the specific
refusal it expects — a locally computed custom-error selector for the Vault
(`NotAllowVerdict()`, `NotReviewVerdict()`, `CalldataMismatch()`, `BadNonce()`),
and a matched `FAIL:` line plus exit status for the verifier. A negative that
fails for any other reason — a transport error, a crash, a missing file — fails
the demo instead of scoring as a pass. Private keys are never written.

**The BLOCK case is generated at runtime, with that run's keys.** Before the
ALLOW receipt is signed, the demo asks the same isolated signer to evaluate a
second action: target, selector and value exactly as mandated, and the
beneficiary word inside the calldata rewritten to an address the mandate does
not authorise. That is the one shape this tree's verifier says, in its own
`NOT ESTABLISHED` line, that it cannot see for itself — it never decodes
calldata — so it is caught where it can be caught: the evaluator decodes the
arguments, returns BLOCK, and the signer signs a genuine BLOCK receipt over
that evidence. The demo then presents that receipt four times and requires four
refusals: to the Vault at `executeWithReceipt` (`NotAllowVerdict()`) and at
`executeWithOverride` (`NotReviewVerdict()`), and to the verifier on
`--execution-path automatic` and on `--execution-path owner-override`, each
with the `FAIL:` line naming the verdict. That is the runnable form of the
sentence under "Independent verification" that a BLOCK receipt certifies on
neither entry point. The BLOCK bundle is written beside the ALLOW one as
`sample-block/`. No fixed-key BLOCK fixture is shipped, deliberately: a fixture
signed by a key that also appears in a repository is exactly the trust-root
confusion this tree exists to avoid, and a per-run key cannot be confused with
anything.

The remaining negatives are an unauthenticated deployment authority, altered
calldata, and receipt replay.

**The demo generates its own deployment authority.** It signs its own manifest
with that key and then hands the verifier the same address, so that run is a
self-consistency loop and not an independent authentication. The demo labels the
address it prints as lab-generated and non-production. A real recipient's
`--deployment-authority` arrives over a channel the publisher does not control;
nothing this tree prints can be that channel.

## Independent verification

The demo above leaves everything this needs under its `--output` directory:
`sample/` (the ALLOW bundle), `sample-block/` (the BLOCK bundle),
`deployment-manifest.json`, and — printed at the end of the run under the
heading `LAB-GENERATED DEPLOYMENT AUTHORITY` — the address to pass as the
authority. Substitute that address below. An earlier version of this section
named a `SAMPLE_DIR` and a `DEPLOYMENT_MANIFEST.json` that the tree does not
contain; it was written by someone who still had the repository open.

```sh
python3 verifier/verify_publication.py demo-out/sample \
  --deployment-manifest demo-out/deployment-manifest.json \
  --deployment-authority 0xADDRESS_THE_DEMO_PRINTED
```

**The ALLOW bundle expires 300 seconds after the demo signed it.** The isolated
signer issues receipts with a five-minute lifetime, and the verifier evaluates
that window against the host clock. Run within five minutes: exit `0`, `PASS
(static, offline)`. Run later: exit `1`, `FAIL: receipt requires issuedAt <=
evaluationTime < expiresAt; got …`. The second is expiry, not rejection — the
bytes are the same, and a verifier with a window is doing what it should.
Re-run the demo for a fresh bundle.

The BLOCK bundle does not go stale the same way. The verdict is checked before
the windows, so `sample-block/` is refused for its verdict however long you
wait, on either path:

```sh
python3 verifier/verify_publication.py demo-out/sample-block \
  --deployment-manifest demo-out/deployment-manifest.json \
  --deployment-authority 0xADDRESS_THE_DEMO_PRINTED
# exit 1 — FAIL: receipt.verdict is BLOCK (0), not ALLOW: …
python3 verifier/verify_publication.py demo-out/sample-block \
  --deployment-manifest demo-out/deployment-manifest.json \
  --deployment-authority 0xADDRESS_THE_DEMO_PRINTED \
  --execution-path owner-override
# exit 1 — FAIL: receipt.verdict is BLOCK (0), not REVIEW: …
```

A recipient with real material substitutes their own bundle, the publisher's
signed manifest, and an authority address that reached them over a channel the
publisher does not control.

### Two verifiers, two claims

This tree ships ONE verifier, `verifier/verify_publication.py`, and its claim
is **executability**: would `SentinelVault` execute this bundle at the entry
point it is presented for. It refuses a BLOCK receipt, and a REVIEW receipt
without an authenticated owner override, because the Vault would refuse them.

The repository this tree was assembled from carries a second, older verifier,
`verifier/verify.py`, which is **not in this tree**. Its claim is
**authenticity**: is this bundle genuinely what the signer produced. It passes
a BLOCK receipt and an override-less REVIEW receipt, correctly, because both
are authentic; and it evaluates no validity window at all, so an expired
receipt is still an authentic one there. Its `=> PASS` and this tool's `PASS
(static, offline)` are two different claims that once shared one word. The
split is deliberate, was ruled at D-087(c), and each tool now says in its own
output which claim it makes. It is stated here so a reader who meets both does
not take one's PASS for the other's.

The verifier enforces one fail-closed predicate:

* the deployment manifest's chain, vault, owner and signer, authenticated under
  the out-of-band authority, with the manifest refused if it is post-dated or
  older than the maximum age the module records;
* an owner-signed mandate naming that signer, and a receipt signed by that
  signer, with every signature held to EIP-2 low-s form and `v` in `{27, 28}`;
* **the signer's verdict, checked against the Vault entry point the bundle is
  presented for.** `SentinelTypes.Verdict` is `{0=BLOCK, 1=REVIEW, 2=ALLOW}`.
  The automatic path certifies an ALLOW receipt only; the owner-override path
  certifies a REVIEW receipt only, and then only alongside a separate
  owner-signed override that names this exact receipt, action, mandate, policy
  and nonce, is inside its own validity window, and recovers to the owner rather
  than to the isolated signer. A BLOCK receipt — including the corpus's real
  prompt-injection case — is executable through neither entry point and
  certifies on neither. A verdict value outside the enum fails closed instead of
  falling through to an ALLOW comparison;
* the action's target and selector against the **mandate**, which names both
  directly; its `valueWei` against both the mandate and the policy native-value
  ceilings; and its `operation` against the policy's `allowedOperation`;
* `dataHash` recomputed from the calldata bytes supplied;
* the policy document matching the `policyHash` that the mandate and action
  commit to, and current at the evaluation instant;
* `issuedAt/validAfter <= evaluationTime < expiresAt/validUntil` for the
  receipt, the mandate, the policy and the override.

### Which Vault entry point a bundle is presented for

`SentinelVault` has exactly two entry points and deliberately no third, so the
verifier is told which one rather than guessing:

```sh
--execution-path automatic        # default. executeWithReceipt; ALLOW only.
--execution-path owner-override   # executeWithOverride; REVIEW plus an
                                  # authenticated override.json.
```

A run that certifies on the override path says so in its headline. The two
outcomes a recipient most needs to tell apart — *the machine approved this* and
*a human was asked and signed an exception* — must not differ by one word in the
middle of a sentence.

### Exit codes

* **`0`** — certifying. Static, offline EXECUTABILITY — the manifest
  authenticates under the out-of-band authority, the bundle is bound and signed
  by the parties it names, the verdict is the one the presented entry point
  accepts, and the compared action fields conform to the mandate and policy at
  the evaluation instant — with everything in the run's own `NOT ESTABLISHED`
  line still outstanding, which is where executability *on chain* is
  disclaimed. An earlier version of this line said "authenticity", which is the
  other verifier's word ("Two verifiers, two claims", above).
* **`1`** — refused. The reason is printed to stderr as a `FAIL:` line.
* **`3`** — **not certified, and not a refusal either.** Emitted only under
  `--evaluation-time`, which moves the evaluation instant from the machine
  running the check to whoever wrote the command line. Such a run prints its
  findings as diagnostics and certifies nothing. A script that treats any
  non-zero status as a failure, or any non-`1` status as a pass, misreads it.

### Limits of that predicate

Stated because an earlier version of this file claimed "exact action, calldata,
policy, and nonce commitments", and no part of that last clause held. There
were three of these; a 2026-08-30 claim-honesty review found two more that the
tool's own output does not carry, and they are added rather than folded in.

* **The policy is partly enforced and partly hash-bound.** Enforced against the
  action: `maxNativeValueWei`, `allowedOperation`, and the policy's own
  `validAfter`/`validUntil` window. Hash-bound only: `allowedTargetsHash`,
  `allowedSelectorsHash` and `allowedCallGraphHash` commit to lists whose
  contents this tree does not ship, so there is nothing here for an action to be
  compared against; `maxAllowanceIncreaseBaseUnits` is likewise not evaluated by
  this verifier — nor, as "Token authority is not bounded at all" above records,
  by the Vault. For those four fields the verifier establishes only that the
  policy document supplied is the one the mandate and the action committed to.
  The earlier wording here — "It does not evaluate the policy's target,
  selector, value, or call-graph constraints" — became false for value and for
  operation when those checks were added, and is corrected rather than quietly
  dropped.
* **The calldata's arguments are never decoded, by ruling.** `dataHash` binds
  `callData` to the bytes presented, and the leading four bytes are compared to
  the mandated selector — but nothing after that selector is decoded. A
  beneficiary, recipient or amount encoded inside the calldata is therefore
  compared to no mandated value by this verifier, and a bundle in which only
  that word was rewritten is internally consistent and authenticates. The Vault
  binds the same bytes and likewise never decodes them; only the isolated
  signer's evaluator reads the decoded arguments. An earlier version of this
  file called that "an open scope question rather than a settled no". It is
  settled: John ruled on 2026-08-30 (D-083(b)) that this verifier stays
  disclosed-only and does not decode calldata, permanently, and the ruling
  recorded its own cost rather than arguing it away. What a verifier can do
  without decoding is compare the signer's ATTESTED decoded record against the
  mandate, which catches a misconfigured-but-honest evaluator and not a lying
  signer; the tool's own output is the authority on whether this tree's copy
  carries that check. The cold demo's BLOCK case is this exact shape, caught
  where it can be caught — by the evaluator, before anything is signed.
* **There is no nonce check, and an offline verifier cannot have one.** Nonce
  freshness is not observable offline at all: the Vault consumes the action
  nonce atomically at execution, and nothing here reads chain state. What this
  verifier does with `actionNonce` is confirm it is a canonical `uint256`, and —
  on the override path — that the owner's override names the same one.

* **There is no authenticated revocation source, so the manifest lifetime is a
  bound and not a revocation check.** `deployment.py` refuses a manifest older
  than ninety days (`MAX_MANIFEST_AGE_SECONDS`, ratified at D-083(e)) and one
  post-dated past the evaluation instant. That is the whole of what stands in
  for revocation: no list, no on-chain registry, no state proof. A manifest the
  publisher has since repudiated, or one naming a signer rotated away
  yesterday, keeps authenticating until it ages out. `check_lifetime` is named
  for what it is; nothing in this tree can be named "revocation".
* **The `NOT ESTABLISHED` line is printed beside every CERTIFYING result, not
  every result.** A refused run prints its `FAIL:` line and nothing else; a
  non-certifying `--evaluation-time` run carries the list only inside its JSON.
  So a reader who sees the line is reading a PASS, and a reader of a refusal
  never sees it — which is fine for a refusal, and is stated so that "beside
  every result", which this file used to say, is not read as a property of the
  refusals too.

Two of the first three — the undecoded calldata arguments and nonce freshness —
are printed by the tool itself in that `NOT ESTABLISHED` line, together with
the absence of any chain read and the absence of any authenticated clock. A
recipient who reads only the tool's certifying output still meets them. The
policy's hash-bound fields and the two limits added above are stated only here.

## Tests: what runs in this tree and what does not

`npm --prefix ts test` in this tree REFUSES, with exit 1 and a message, on
purpose. The repository's TypeScript suite (`ts/test/**`) does not ship: it
depends on the corpus, the fixture generators and fixed-key test harnesses that
this tree deliberately excludes, and shipping those would reintroduce the fixed
development keys the assembler refuses to place here. Before this was fixed the
shipped script was the repository's own `node --test "test/**/*.test.ts"`,
which against an empty glob exits 0 having run zero tests — a green light on an
empty suite, which is this project's own named failure mode. The repository's
Python suite for its authenticity verifier does not ship either, and neither
does that verifier (see "Two verifiers, two claims").

What does run: `forge test --root contracts` (one adversarial test file,
`contracts/test/PublicationWithdrawal.t.sol`), the cold demo with its typed
negative controls, the verifier invocations above, and `npm --prefix ts run
typecheck` against the shipped sources. The npm scripts for tools that are not
in this tree are removed from the shipped `package.json` rather than left to
fail on a missing file. A green result from any of these is evidence for what
it exercised and nothing wider.

Vendored dependencies ship with their notices: `contracts/lib/forge-std/`
carries `LICENSE-APACHE` and `LICENSE-MIT`, and
`contracts/lib/openzeppelin-contracts/` carries `LICENSE` (MIT). Those notices
are the vendors' terms for their code. This tree's own code carries no licence
grant; that choice is deliberately held and is not made here.

`MANIFEST.sha256` covers every released file other than itself. Publication or
deployment is a separate user decision; assembling this tree does not push,
publish, or bless a production authority.
