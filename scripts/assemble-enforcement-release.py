#!/usr/bin/env python3
"""Assemble the key-free Sentinel enforcement publication tree.

The release is generated from maintained source and Foundry artifacts.  It
deliberately excludes reviewer fixtures, corpus material, legacy domain.json,
and every source file containing fixed development private keys.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "release"

VERIFIER_FILES = (
    "verify_publication.py", "deployment.py", "eip712.py", "jcs.py",
    "keccak.py", "secp256k1.py",
)
TS_DIRS = ("decode", "evaluate", "simulate", "signer")
KNOWN_DEV_KEYS = (
    "ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
    "59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
    "5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",
)

README = """# Sentinel enforcement release v0.3

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
npm --prefix ts run cold-demo
```

The demo creates fresh owner, isolated-signer, and deployment-authority keys in
memory for that run. It deploys to a fresh Anvil, owner-signs and activates a
signer-bound mandate, evaluates and signs in the separate signer process,
verifies the signed deployment manifest and the receipt, executes the exact
call, and runs three typed negative controls: an unauthenticated deployment
authority, altered calldata, and receipt replay. Each negative asserts the
specific refusal it expects — a locally computed custom-error selector for the
Vault (`CalldataMismatch()`, `BadNonce()`), and a matched `FAIL:` line plus exit
status for the verifier. A negative that fails for any other reason — a
transport error, a crash, a missing file — now fails the demo instead of scoring
as a pass. The demo prints the temporary evidence path. Private keys are never
written.

**The demo generates its own deployment authority.** It signs its own manifest
with that key and then hands the verifier the same address, so that run is a
self-consistency loop and not an independent authentication. The demo labels the
address it prints as lab-generated and non-production. A real recipient's
`--deployment-authority` arrives over a channel the publisher does not control;
nothing this tree prints can be that channel.

## Independent verification

```sh
python3 verifier/verify_publication.py SAMPLE_DIR \\
  --deployment-manifest DEPLOYMENT_MANIFEST.json \\
  --deployment-authority 0xADDRESS_OBTAINED_OUT_OF_BAND
```

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

* **`0`** — certifying. Static, offline authenticity, with everything in the
  run's own `NOT ESTABLISHED` line still outstanding.
* **`1`** — refused. The reason is printed to stderr as a `FAIL:` line.
* **`3`** — **not certified, and not a refusal either.** Emitted only under
  `--evaluation-time`, which moves the evaluation instant from the machine
  running the check to whoever wrote the command line. Such a run prints its
  findings as diagnostics and certifies nothing. A script that treats any
  non-zero status as a failure, or any non-`1` status as a pass, misreads it.

### Three limits of that predicate

Stated because an earlier version of this file claimed "exact action, calldata,
policy, and nonce commitments", and no part of that last clause held.

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
* **The calldata's arguments are never decoded.** `dataHash` binds `callData` to
  the bytes presented, and the leading four bytes are compared to the mandated
  selector — but nothing after that selector is decoded. A beneficiary,
  recipient or amount encoded inside the calldata is therefore compared to no
  mandated value, and a bundle in which only that word was rewritten is
  internally consistent and authenticates. The Vault binds the same bytes and
  likewise never decodes them; only the isolated signer's evaluator reads the
  decoded arguments. Whether the verifier should decode them is an open scope
  question rather than a settled no, and it is disclosed here either way.
* **There is no nonce check, and an offline verifier cannot have one.** Nonce
  freshness is not observable offline at all: the Vault consumes the action
  nonce atomically at execution, and nothing here reads chain state. What this
  verifier does with `actionNonce` is confirm it is a canonical `uint256`, and —
  on the override path — that the owner's override names the same one.

Two of these three — the undecoded calldata arguments and nonce freshness — are
printed by the tool itself, in a `NOT ESTABLISHED` line beside every result,
together with the absence of any chain read and the absence of any authenticated
clock. A recipient who reads only the tool's output still meets them. The
policy's hash-bound fields are the one limit stated only here.

`MANIFEST.sha256` covers every released file other than itself. Publication or
deployment is a separate user decision; assembling this tree does not push,
publish, or bless a production authority.
"""


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def assemble() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / "README.md").write_text(README)

    shutil.copytree(REPO / "contracts" / "src", OUT / "contracts" / "src")
    copy_file(REPO / "contracts" / "foundry.toml", OUT / "contracts" / "foundry.toml")
    copy_file(
        REPO / "contracts" / "test" / "PublicationWithdrawal.t.sol",
        OUT / "contracts" / "test" / "PublicationWithdrawal.t.sol",
    )
    shutil.copytree(
        REPO / "contracts" / "lib" / "forge-std" / "src",
        OUT / "contracts" / "lib" / "forge-std" / "src",
    )
    shutil.copytree(
        REPO / "contracts" / "lib" / "openzeppelin-contracts" / "contracts",
        OUT / "contracts" / "lib" / "openzeppelin-contracts" / "contracts",
    )

    artifact = json.loads(
        (REPO / "contracts" / "out" / "SentinelVault.sol" / "SentinelVault.json").read_text()
    )
    write_json(OUT / "contracts" / "artifact" / "SentinelVault.abi.json", artifact["abi"])
    write_json(
        OUT / "contracts" / "artifact" / "SentinelVault.bytecode.json",
        {"bytecode": artifact["bytecode"], "deployedBytecode": artifact["deployedBytecode"]},
    )
    (OUT / "contracts" / "artifact" / "SentinelVault.metadata.json").write_text(
        artifact["rawMetadata"] + "\n"
    )

    for name in VERIFIER_FILES:
        copy_file(REPO / "verifier" / name, OUT / "verifier" / name)

    for name in ("package.json", "package-lock.json", "tsconfig.json"):
        copy_file(REPO / "ts" / name, OUT / "ts" / name)
    for name in TS_DIRS:
        shutil.copytree(REPO / "ts" / "src" / name, OUT / "ts" / "src" / name)
    copy_file(
        REPO / "ts" / "src" / "tools" / "cold-demo.ts",
        OUT / "ts" / "src" / "tools" / "cold-demo.ts",
    )

    assert_key_free()
    write_manifest()


def assert_key_free() -> None:
    failures = []
    fixed_key_assignment = re.compile(
        r"(?:privateKeyToAccount|SENTINEL_SIGNER_KEY|OWNER_KEY|SIGNER_KEY|PRIVATE_KEY).{0,40}0x[0-9a-fA-F]{64}"
    )
    for path in sorted(p for p in OUT.rglob("*") if p.is_file()):
        data = path.read_bytes()
        text = data.decode("utf-8", errors="ignore")
        lower = text.lower()
        if any(key in lower for key in KNOWN_DEV_KEYS):
            failures.append(f"{path.relative_to(OUT)} contains a known development key")
        if fixed_key_assignment.search(text):
            failures.append(f"{path.relative_to(OUT)} contains a fixed private-key assignment")
        if "/Users/" in text or "-----BEGIN PRIVATE KEY-----" in text:
            failures.append(f"{path.relative_to(OUT)} contains machine state or a private key")
        if path.name == "domain.json":
            failures.append(f"{path.relative_to(OUT)} is a presenter-selected trust root")
    if failures:
        raise SystemExit("release refused:\n" + "\n".join(failures))


def write_manifest() -> None:
    rows = []
    for path in sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "MANIFEST.sha256"):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(f"{digest}  {path.relative_to(OUT).as_posix()}")
    (OUT / "MANIFEST.sha256").write_text("\n".join(rows) + "\n")


if __name__ == "__main__":
    assemble()
    print(f"assembled {OUT}")
