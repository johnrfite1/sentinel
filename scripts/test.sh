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

step "rename gate (D-016)"
./scripts/check-rename-gate.sh || fail=1

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

================================================================================
COVERAGE BOUNDARY (house rule 4) — read this, not the pass count
================================================================================

MAINTENANCE NOTE, because this block previously rotted: it is ONE statement, not a
running log. Two outside reviewers found it simultaneously claiming that the Anvil
pipeline and conformance engine did not exist, that Case 3 was undetectable, and — four
lines later — that Case 3 was detectable. A self-contradicting boundary is worse than
none, because a reader takes whichever half suits them, which is the exact failure the
boundary exists to prevent. When a step lands, REWRITE the affected layer below. Do not
append.

WHAT IS COVERED, by layer, each with the limit that layer cannot exceed:

  §9 s1-2  Vault + typed payloads. Exact-action binding, nonce single-use, verdict
           gating, override binding, pause, owner-only controls, signer rotation,
           reentrancy, and stateful invariants over all of it.
           LIMIT: proves the vault ENFORCES a receipt, never that the receipt carried a
           CORRECT verdict. A vault that faithfully executes a wrong decision passes
           every one of these tests.

  §9 s3    Isolated signer, as a separate OS process behind a two-method 0600 socket.
           All 31 declared checks triggered individually; every severity tier asserted
           against all three verdicts; the per-nonce guard under real concurrency.
           LIMIT: proves the signer refuses a MIS-BOUND receipt. In these tests the
           verdict is an INPUT, so a signer faithfully attesting to a wrong ALLOW passes
           all of them.

  §9 s4    Two decoders. Every declared refusal triggered individually, plus a measured
           comparison against the real EVM: never more permissive than the chain,
           stricter in exactly one place (trailing bytes).
           LIMIT: proves faithfulness to bytes. Renders no verdict.

  §9 s5    Anchored snapshot/execute/inspect/revert pipeline against a real Anvil.
           Leak-freedom on success and revert paths, repeatability, an anchor surviving
           the revert, effects measured with the VAULT as msg.sender.
           LIMIT: effects are SIMULATED at a recorded block, not observed
           post-execution (§8 as amended by D-001).

  §9 s6    Conformance engine + RFC 8785 evidence bundle. The §5.2 verdict fold; all 37
           declared checks triggered individually; all four §4.2 cases end to end, with
           Case 1 continuing through the signer into the vault. Case 3 IS detected here,
           blocked on mandate conformance while every representative-baseline check
           passes. Three independent EIP-712 implementations agree.
           LIMIT: this is the layer whose own tests prove least. Self-written tests
           encode the same misunderstanding twice.

WHAT IS NOT COVERED:

  - Whether the verdicts are RIGHT. §7 states it outright: "Four demo paths alone cannot
    prove that the verdicts are not hard-coded." The bar is the §9 step 8 corpus with
    independent labels (D-011) plus the §7.3 ablation. NEITHER EXISTS YET; both are S2.
  - Case 1 from a REAL agent proposal. The action is constructed by the test. The D-007
    spike showed a proposal flips under injection, but proposal and pipeline are not yet
    wired together (step 7).
  - The D-010 receipt-verifier CLI, the fixture corpus, and the dashboard.
  - Independent adversarial review of steps 4-6. Only step 3 has had one (A-016), and
    most of that review's own verifications were cut short by a spend limit.

A green run means the mechanism runs end to end. It does not mean Sentinel decides
correctly. Those are different claims and only the first is in evidence here.

For gate evidence use the deep profile — ./scripts/test.sh --gate — not this default.
COVERAGE
