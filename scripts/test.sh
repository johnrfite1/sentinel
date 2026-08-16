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

step "labelling-prompt freeze (D-011a)"
./scripts/check-label-prompt.sh || fail=1

step "published EIP-712 type strings (D-023)"
./scripts/check-type-strings.sh || fail=1

step "§5.7.1 check coverage (D-031)"
./scripts/check-eval-codes.sh || fail=1

# Reads its own output, not just its exit status: this one passes on the mechanical half
# while printing two conditions only John can clear. A green gate here does NOT mean Gate 5
# is satisfied.
step "vendor honesty (§7.5 Gate 5, D-008)"
./scripts/check-vendor-honesty.sh || fail=1

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

    # OBSERVATION, NOT A STAGE. D-007's canary "never fails CI", so this prints its recorded
    # history and cannot set `fail`. It is here because the other half of that ruling —
    # "an unobserved canary is not evidence" — is only satisfied if the history is put in
    # front of somebody on every gate run. NEVER RUN is a legitimate thing for it to print,
    # and it is louder here than in a file nobody opens.
    step "Gate 7 canary observation (D-007; never fails the gate)"
    npm --prefix ts run --silent canary -- --report || true
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
           reentrancy, and stateful invariants over all of it. The override path is IN
           the stateful campaign as of 2026-08-15 — before that the entire second
           execution path, the one that moves funds on a REVIEW verdict, appeared only
           in deterministic tests. `SentinelVault.backstops.t.sol` adds thirteen tests
           each named for a deliberate defect that SURVIVED a green 43-test run, among
           them §3.3(9)'s "nonce consumed before the external call", which the
           reentrancy guard masks and which nothing had ever verified. A second review then
           found five MORE survivors, three of them properties the contract's own comments
           claim: `nonReentrant` droppable from the OVERRIDE path (a double-spend, on two
           shapes, since the guard is shared), the override's binding to one exact review
           receipt untested, and `CallFailed` asserted by nothing. Covered now.
           LIMIT: proves the vault ENFORCES a receipt, never that the receipt carried a
           CORRECT verdict. A vault that faithfully executes a wrong decision passes
           every one of these tests. The invariant handler's action set also defines
           what "cannot bypass" was tested against: a path it never generates was not
           tested.

  §9 s3    Isolated signer, as a separate OS process behind a two-method 0600 socket.
           All 33 declared checks triggered individually; every severity tier asserted
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

  §9 s6    Conformance engine + RFC 8785 evidence bundle. The §5.2 verdict fold; all 41
           declared checks triggered individually; all four §4.2 cases end to end, with
           Case 1 continuing through the signer into the vault. Case 3 IS detected here,
           blocked on mandate conformance while every representative-baseline check
           passes. Three independent EIP-712 implementations agree.
           LIMIT: this is the layer whose own tests prove least. Self-written tests
           encode the same misunderstanding twice.

  §9 s7    Agent-proposal transcriber, and the pipeline driven from real agent output.
           Both arms of the pinned claude-haiku-4-5 recording (A-009) run through
           decode, simulation, evaluation, isolated signing and the vault: the control
           proposal executes and writes an entitlement onchain, the injected proposal
           blocks with no executable receipt. All 7 declared refusals triggered
           individually, each of their alternate branches too, with a structural
           exhaustiveness assertion over the code table.
           LIMIT: under D-019 Sentinel ENCODES the calldata from the agent's typed
           arguments, so the decoder recovering the agent's claimed parameters is a
           round-trip through Sentinel's own encoder and NOT independent corroboration.
           What is genuinely demonstrated is that the agent's rationale — its account of
           what the call means — reaches no check, no bound field, and no byte of the
           evidence bundle. Two further limits: the transcriber emits only exact-width
           canonical words for the SIGNATURE THE AGENT SUPPLIED — but that is not the
           same as the word count the decoder expects, because the decoder keys off a
           4-byte truncated keccak of that signature. A selector collision inside the
           transcriber's own grammar therefore makes §7.1's malformed-calldata class
           REACHABLE from a proposal; an adversarial review demonstrated one
           (`fUXSEz2ajwh(bytes32)` collides with `purchase(...)`, found in 106 seconds).
           It fails CLOSED — the decode failure is UNRESOLVED, so no wrong ALLOW — but the
           earlier wording here claimed unreachability as an absolute and was false (A-028).
           The malformed classes are still authored as raw calldata in the corpus. And the
           proposals are PINNED transcripts, which fix the agent's output and therefore say
           nothing about whether the injection still reproduces against a live model. That
           gap is now covered OUTSIDE this suite by the D-007 canary (`npm --prefix ts run
           canary`), whose history this script prints; nothing in the suite itself calls a
           model, and the canary is deliberately not a stage here.

  §9 s8    The §7.1 corpus and the §7.3 ablation. 50 fixtures across all 20 declared
           classes, executed against a real chain with per-fixture snapshot isolation, and
           INDEPENDENTLY LABELLED under the D-011a frozen prompt by agents denied the
           implementation, the tests, and each other's work. Measured against those labels:
           false allows 38 (baseline) / 8 (policy+effects) / 1 (full). Detection
           contribution — baseline alone 9, effect extraction adds 29, mandate conformance
           adds 8, and those 8 are exactly the wrong-purpose class (D-034 gave the partition
           a criterion and moved nine non-purpose codes to L2; the figure was 17). Inter-labeller disagreement 0.0% on a freshly drawn sample, with both
           limits on that number stated in the report itself.
           LIMIT: this is the first evidence in the repository that bears on whether the
           verdicts are RIGHT rather than merely produced, and it is bounded by the corpus.
           50 fixtures over two demo contracts and two call schemas is not an accuracy claim
           about EVM transactions (§7.3: "do not claim general transaction-safety accuracy").
           The `malicious-retrieved-instructions` class carries a real rationale as of
           2026-08-15, and the run measures that no derived adjacent word-pair of it — nor a
           base64 or hex carriage of the whole — reaches a bound field, a check, a reason
           code, or the evidence bundle. That is a REGRESSION guard, not a proof of absence:
           a single leaked word, a paraphrase, or an unanticipated encoding passes. NO LAYER
           DETECTS AN INJECTION and none should: nothing reads the narrative, so a layer that
           appeared to would be a defect.
           The single full-configuration false allow is F035, whose enforcement is the
           isolated signer rather than the engine. The labels of record are the THIRD round
           (E/F): round 1 scored a spec since amended, and round 2 was discarded as
           contaminated when a review found the brief had handed the labeller a finding
           derived from reading the evaluator (A-028 F-1). All earlier rounds are retained
           as audit trail.

  D-010    The independent Python receipt verifier, in `verifier/`. Zero third-party
           dependencies; its own RFC 8785, Keccak-f[1600] and secp256k1 recovery, built by
           an agent that never read this repository's TypeScript. 6/6 samples verify, 42/42
           applicable tamper cases behave as specified, 70/70 of its own tests pass. The
           sixth sample commits to exactly ONE reason code — until 2026-08-15 nothing
           pinned that edge, and a producer appending the delimiter after a one-element
           set would have verified here (A-027). Its keccak is pinned to
           published vectors and its JCS to RFC 8785's appendix-B vectors, so green means
           agreement with the STANDARD, not with itself.
           LIMIT: it verifies that a bundle is the one a receipt commits to and that the
           receipt is correctly signed. It CANNOT confirm the bundle's factual content
           against a chain — that needs an archive node at the anchored block. Verifying a
           receipt is not verifying the simulation. The corpus exercises no JSON numbers and
           no non-ASCII, so RFC 8785's number and code-unit-ordering paths — its two most
           error-prone branches — are untested by anything (REPORT.md F-6).

WHAT IS NOT COVERED:

  - A LIVE agent. §9 step 7 connected the proposal to the pipeline, so the D-018 gap is
    closed for the recorded case, but every agent proposal exercised here comes from a
    pinned D-007 transcript. Nothing in this suite calls a model.
  - Gate 5's CERTIFICATION half. The mechanical conditions run above and pass; D-008(1)
    and (3) — every capability cell dated and linked, inference marked — are John's, are
    reported UNCERTIFIED on every run, and no agent may clear them.
  - The evidence dashboard (outside S2 unless John adds it at the gate, D-009).
  - Gate 8 (five-minute comprehension), which D-032 makes PRE-PUBLICATION rather than S2.
  - Reproducible labelling views: re-running the corpus rewrites 32 of 50 view files
    purely because entitlement expiry follows chain time (A-029).
  - Labeller independence from PRIOR FINDINGS about specific fixtures (A-030). The
    independence from the IMPLEMENTATION is real and enforced. The specification the
    protocol grants has carried a walkthrough of F049 since before any labelling round,
    and every labeller of record read it. OPEN FORK for John.
  - An independent review of steps 7-8, which have had NONE, and of steps 1-3 that
    completed. Steps 4-6 HAVE now had a full
    independent adversarial pass under D-017 (see A-022): fixed commit, 12 findings, all 12
    independently adjudicated, 1 S1-blocking defect plus 6 others corrected and reverified.
    Steps 1-3 were reviewed earlier under A-016, whose own verifications were mostly cut
    short by a spend limit — that limit is NOT retired by the later review.

A green run means the mechanism runs end to end. It does not mean Sentinel decides
correctly. Those are different claims and only the first is in evidence here.

For gate evidence use the deep profile — ./scripts/test.sh --gate — not this default.
COVERAGE
