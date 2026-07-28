#!/usr/bin/env bash
# Sentinel — project gate. Run this before claiming anything is green.
#
# Usage:
#   ./scripts/test.sh          fast profile (fuzz 1024)
#   ./scripts/test.sh --gate   deep profile for gate evidence (fuzz 20000)
#
# AGENTS.md: "a tool reporting success is not a substitute for checking its output",
# and a runner should fail on error output it does not explicitly expect. This script
# therefore fails on a non-zero exit from ANY stage, not just the last one.

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
export PATH="$HOME/.foundry/bin:$PATH"

PROFILE="default"
[ "${1:-}" = "--gate" ] && PROFILE="gate"

fail=0
step() { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }

step "secret guard (A-007)"
./scripts/check-secrets.sh || fail=1

step "solidity build + tests (profile: $PROFILE)"
if command -v forge >/dev/null 2>&1; then
    (cd contracts && FOUNDRY_PROFILE="$PROFILE" forge test -vv) || fail=1
else
    echo "forge not found. Install with: curl -L https://foundry.paradigm.xyz | bash && foundryup"
    fail=1
fi

# Ordered after the Solidity stage on purpose: the TypeScript suite deploys the compiled
# artifacts from contracts/out and runs the signer against the real vault, so it needs the
# build the previous stage produces. It also spawns Anvil, which the same toolchain supplies.
step "typescript typecheck + isolated signer suite (§9 step 3)"
if [ ! -d ts/node_modules ]; then
    echo "ts/node_modules missing. Run: npm --prefix ts ci"
    fail=1
elif ! command -v anvil >/dev/null 2>&1; then
    echo "anvil not found on PATH; the signer suite needs a local chain."
    fail=1
else
    npm --prefix ts run typecheck || fail=1
    npm --prefix ts test || fail=1
fi

printf '\n'
if [ "$fail" -ne 0 ]; then
    echo -e "\033[31mGATE FAILED\033[0m"
    exit 1
fi

cat <<'COVERAGE'
GATE PASSED

Coverage boundary — what this gate is evidence for right now (house rule 4):
  covered : §5 typed payload schemas and canonical EIP-712 hashes; SentinelVault
            enforcement — exact-action binding, nonce single-use, verdict gating,
            override binding, pause, owner-only controls, signer rotation, reentrancy;
            stateful invariants over those; secret hygiene
            §9 step 3 — the isolated signer as a SEPARATE OS PROCESS reached only over a
            two-method local socket; every one of its 31 declared checks triggered by its
            own case, with each severity tier asserted against all three verdicts; the
            per-nonce attestation guard under real concurrency; and a TypeScript/Solidity
            EIP-712 differential across all five §5 payloads on a live EVM
  NOT yet : the decoders, the Anvil snapshot/execute/inspect pipeline, the conformance
            engine, Case 1 end-to-end from a real agent proposal, and the fixture corpus

Read the vault results narrowly: they prove the vault ENFORCES a receipt, not that the
receipt carried a CORRECT verdict. A vault that faithfully executes a wrong decision
passes every test here. That gap is what §7's evaluation harness exists to close, and it
is why a green gate at this stage is not a claim about Sentinel's mechanism working.

The signer results carry the same shape of limit, one layer up. They prove the signer
refuses to attest to a MIS-BOUND receipt — wrong vault, wrong chain, stale nonce, stale
mandate, calldata that contradicts its own payload, a simulation block that never existed.
They prove nothing about whether a verdict was CORRECT: in these tests the verdict is an
input, supplied by the test rather than computed. A signer that faithfully attests to a
wrong ALLOW passes every one of them. Case 3 — the mechanically valid purchase of the
wrong resource — is not detectable anywhere in this gate yet.

That last sentence is not left to prose. `ts/test/signer.e2e.test.ts` asserts it: a Case 3
action is signed, executed, and writes the wrong entitlement with nothing objecting. When
the decoders (§9 step 4) and the conformance evaluator (§9 step 6) land, that test fails —
and whoever it fails for is holding the sentence above that has to change with it.
COVERAGE
