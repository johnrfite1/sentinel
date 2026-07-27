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
  NOT yet : the decoders, the Anvil snapshot/execute/inspect pipeline, the conformance
            engine, Case 1 end-to-end, and the fixture corpus

Read the vault results narrowly: they prove the vault ENFORCES a receipt, not that the
receipt carried a CORRECT verdict. A vault that faithfully executes a wrong decision
passes every test here. That gap is what §7's evaluation harness exists to close, and it
is why a green gate at this stage is not a claim about Sentinel's mechanism working.
COVERAGE
