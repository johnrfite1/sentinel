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
python3 verifier/verify_publication.py SAMPLE_DIR \
  --deployment-manifest DEPLOYMENT_MANIFEST.json \
  --deployment-authority 0xADDRESS_OBTAINED_OUT_OF_BAND
```

The verifier enforces one fail-closed predicate: authenticated deployment
chain/vault/owner/signer; owner-signed mandate naming that signer; exact action,
calldata, policy, and nonce commitments; and `issuedAt <= now < expiresAt`.

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
