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

# Also reads its own output rather than its exit status. It passes on a RATCHET: six classes are
# carried as not-exercised-at-the-corpus-layer — one RESERVED, four DELEGATED elsewhere, and one
# a GAP that owes a fixture (D-039). A green line here means "no NEW class went vacuous", never
# "every class is covered". The carried list, the GAP count, and the per-fixture vacuity note
# print on every run for that reason.
step "corpus class coverage (A-036)"
./scripts/check-class-coverage.sh || fail=1

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

    # THE CORPUS, EXECUTED — deep profile only.
    #
    # `ts/src/corpus/run.ts` was covered by nothing: the suite never ran the corpus, which is
    # exactly why six deliberate defects in its wiring survived a fully green run. It is
    # executed here rather than left to a human remembering to run it.
    #
    # It writes to a TEMPORARY directory and the committed artifacts are not touched. What is
    # compared is `_digests.json` — each labeller view hashed with the run-varying timestamps
    # normalised out (A-029). So this stage asserts something the project could not assert
    # before: **the committed labeller views are still the semantic output of the current
    # code**, which is the provenance claim the corpus rests on and which git history alone
    # could not establish.
    #
    # Deep profile only. It costs ~90s and would double the inner loop; the fast profile says
    # so out loud rather than silently skipping.
    if [ "$PROFILE" = "gate" ]; then
        step "§7.1 corpus executed, and the committed views verified (A-029)"
        CORPUS_TMP="$(mktemp -d)"
        if SENTINEL_CORPUS_OUT="$CORPUS_TMP" npm --prefix ts run --silent corpus >/dev/null 2>&1; then
            if diff -q "$CORPUS_TMP/for-labelling/_digests.json"                        fixtures/corpus/for-labelling/_digests.json >/dev/null 2>&1; then
                echo "corpus: 50 fixtures executed; committed views semantically current"
            else
                echo "corpus: DIGEST MISMATCH — the committed labeller views are NOT what this"
                echo "  code now produces. Either re-run 'npm --prefix ts run corpus' and commit"
                echo "  the result, or find out what changed. The labels of record were drawn"
                echo "  against the COMMITTED views."
                diff "$CORPUS_TMP/for-labelling/_digests.json"                      fixtures/corpus/for-labelling/_digests.json | head -20
                fail=1
            fi
        else
            echo "corpus: RUN FAILED. Note the recorded trace: the runner picks a random port"
            echo "  and occasionally collides, so re-run once before diagnosing."
            fail=1
        fi
        rm -rf "$CORPUS_TMP"
    else
        step "§7.1 corpus (SKIPPED — fast profile)"
        echo "corpus: not executed. Use --gate; ts/src/corpus/run.ts is covered by nothing else."
    fi
fi

# THE D-010 VERIFIER, EXECUTED.
#
# Added 2026-08-16 (A-045). Until then this stage did not exist: the verifier's own suite was
# invoked by NO profile of this script and by nothing else in `scripts/`, so its 146 tests
# passed only when a human remembered to run them by hand. Its counts were nonetheless quoted
# in `docs/session-state.md` §3 alongside the Foundry and TypeScript ones, as though a green
# gate covered them. It did not. A regression in the verifier could not have failed this gate.
#
# That is this project's most-repeated defect — an instrument that exists and is wired to
# nothing (D-042's invariant arms, A-036's class claims) — sitting in an S2 DELIVERABLE.
#
# Deliberately OUTSIDE the node_modules/anvil block above: D-010 requires the verifier share no
# code and no language with the evaluator, and a stage that inherits the TypeScript stage's
# preconditions would quietly couple them. It needs python3 and nothing else — the suite is
# stdlib `unittest` and the CLI has zero third-party imports, so wiring it in adds no
# dependency the repository did not already have.
#
# BOTH arms run, because they fail differently: the suite proves the verifier's internals,
# and the sample walk proves it still certifies the COMMITTED artifacts. A verifier that
# passes its own tests while rejecting the corpus is the failure this second arm catches.
step "D-010 receipt verifier (independent Python; §14.2, D-010)"
if command -v python3 >/dev/null 2>&1; then
    python3 verifier/test_verifier.py || fail=1
    python3 verifier/verify.py --all fixtures/samples || fail=1
else
    echo "python3 not found; the D-010 verifier is the independent check on every receipt."
    fail=1
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

  §9 s8    The §7.1 corpus and the §7.3 ablation. 50 fixtures spread over all 20 declared
           classes — but SPREAD OVER IS NOT COVERAGE, and as of 2026-08-16 the difference is
           measured rather than assumed: check-class-coverage.sh (A-036) finds 14 of the 20
           produce a failing check the class is actually about. Six do not. Four of those are
           known and reasoned — the call-graph class D-025 reserved, the signer class the
           evaluator has no code for, the injection class whose subject is containment rather
           than a check, and the override class the vault suite proves instead. THE SIXTH IS A
           GAP (D-039): `conflicting-block-state` declares it is proved by the conformance
           engine, is not, and nothing else covers it. It owes a fixture at v1.1.
           A DELEGATION IS NOT A CREDIT. Where a class points elsewhere, this guard reports the
           pointer; it cannot see the delegate and does not check that the delegate tests
           anything. One of the four points at a REGRESSION guard that is explicitly not a
           proof of absence. Read the carried list the guard prints; a green line there means
           no NEW class went vacuous.
           The class number also hides per-fixture vacuity, which the guard now prints
           separately: 39 of 43 scoped fixtures individually fail a check their OWN class is
           about. A class stays green while a member of it exercises nothing — F051 was caught
           only because it was the sole fixture of its class.
           The fixtures are executed against a real chain with per-fixture snapshot isolation, and
           INDEPENDENTLY LABELLED under the D-011a frozen prompt by agents denied the
           implementation, the tests, and each other's work. Measured against those labels:
           false allows 38 (baseline) / 8 (policy+effects) / 1 (full). Detection
           contribution — baseline alone 9, effect extraction adds 29, mandate conformance
           adds 8, and those 8 are exactly the wrong-purpose class (D-034 gave the partition
           a criterion and moved nine non-purpose codes to L2; the figure was 17). Inter-labeller disagreement 0.0% on a freshly drawn sample, with FOUR
           limits on that number stated in the report — two written with it, two supplied by
           an independent review.
           LIMIT ON THE EXACT-MATCH COLUMN: 12/50, 41/50, 49/50 are scored against labeller E,
           and the one label the contamination channel moved (F051) is one of the 50. Scored
           without it the figures read 11/49, 40/49, 48/49. Both columns are real; only the
           first is published anywhere but the decision log (A-033).
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
           an agent that never read this repository's TypeScript. 7/7 samples verify, 55/55
           applicable tamper cases behave as specified, 146/146 of its own tests pass.
           It verifies REFUSALS as well as decisions as of 2026-08-16: §5.5.1's
           RefusalRecord was implemented by a schema-only agent and met a real signed
           refusal it had never seen, which is where the envelope gap and three further
           defects in that section came from (A-042). One sample commits to exactly ONE
           reason code — until 2026-08-15 nothing pinned that edge, and a producer
           appending the delimiter after a one-element set would have verified here
           (A-027). Its keccak is pinned to published vectors and its JCS to RFC 8785's
           appendix-B vectors, so green means agreement with the STANDARD, not with itself.
           THESE FIGURES ARE NOW PRODUCED BY THIS SCRIPT RATHER THAN QUOTED IN IT. Until
           2026-08-16 no profile of this gate ran the verifier at all: the three numbers
           above read 6/6, 42/42 and 70/70 — true when written, stale through A-041
           (70 → 101) and A-042 (101 → 146, and the seventh sample), in the block whose own
           maintenance note exists because it had rotted once before. A regression in an S2
           deliverable could not have failed this gate. Wired in as a stage under A-045,
           both arms falsified against the real script before the claim was made.
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
  - THAT THE VAULT CONSTRAINS TOKEN AUTHORITY. It does not, and §7.1 said otherwise until
    2026-08-16 (D-042). The hard caps bound the NATIVE-VALUE dimension only: pause, nonce,
    deadline and the wei ceiling. One valid ALLOW receipt for approve(spender, max) passes
    every onchain check — the wei ceiling never engages, valueWei being zero — and the
    vault's whole token balance becomes transferable. The flagship Case 2 attack is
    refused by the EVALUATOR with nothing behind it. A per-action allowance ceiling is
    v1.1; test_LIMIT_vaultCapsNativeValueOnlyAndNotTokenAuthority asserts the limit so it
    cannot regress into an assumption.
  - WHAT THE STATEFUL CAMPAIGN ADDS OVER THE DETERMINISTIC TESTS. Measured 2026-08-16 and
    the answer was NOTHING: 31 mutations, 31/31 caught by the 56 deterministic tests, and
    31/31 still caught with the whole campaign disabled. Five survived all invariants,
    including a vault accepting arbitrary FUTURE nonces. Two arms were added (D-042) and
    both of those mutations are now killed — but the honest reading of Gate 6's line is
    that the deterministic tests carry it and the campaign corroborates. A campaign's
    coverage is bounded by what its handler can BUILD, not by its call count.
  - THAT GATE 5's CITATIONS POINT ANYWHERE. Certified by John 2026-08-16 (D-038), and
    the check now reports 11 of 11 rows and "certified by record" rather than
    UNCERTIFIED. What it verifies is the SHAPE of a marker in the capability cell:
    [§13#N read YYYY-MM-DD]. It does not resolve N against §13, so a citation to a
    source number that does not exist passes. "Dated" is checked; "linked" is not.
    Nor does anything detect an edit to the §2 table, which D-038 declares makes the
    certification stale — that expiry is a convention, not an instrument.
  - The evidence dashboard (outside S2 unless John adds it at the gate, D-009).
  - Gate 8 (five-minute comprehension), which D-032 makes PRE-PUBLICATION rather than S2.
  - BYTE-reproducible labelling views: a corpus re-run rewrites 32 of 50 view files
    purely because entitlement expiry follows chain time (A-029). What IS covered, at
    the deep profile, is that the committed views are SEMANTICALLY current — the corpus
    runs to a temp directory and its normalised digests are compared to the committed
    ones. "These are the views the labellers saw" is now checkable modulo two declared
    timestamp fields, rather than resting on git history alone.
  - Labeller independence from PRIOR FINDINGS about specific fixtures (A-030) is no
    longer an open fork — it was MEASURED (D-033, D-035) and the channel moved exactly
    ONE label, F051, the one labeller E had flagged itself. What is NOT covered is the
    residue: the specification still carries fixture walkthroughs and still publishes
    41 of the evaluator's reason-code identifiers, a contamination surface four times
    what the decision log recorded before it was counted. v1.1 work, not measured away.
  - Model-INDEPENDENT labelling. One arm used a different Claude model and agreed. The
    build loop cannot obtain a labeller from another vendor, so "model diversity" here
    means a second model from one family, not an independent implementation of judgement.
  - An independent review of steps 1-3, whose earlier pass (A-016) had most of its
    verifications cut short by a spend limit that is NOT retired. Steps 4-6 had a full
    independent adversarial pass under D-017 (see A-022): fixed commit, 12 findings, all 12
    independently adjudicated, 1 S1-blocking defect plus 6 others corrected and reverified.
    Steps 7-8 were reviewed 2026-08-15: ten findings, all remediated.
    Steps 1-3 were reviewed earlier under A-016, whose own verifications were mostly cut
    short by a spend limit — that limit is NOT retired by the later review.

A green run means the mechanism runs end to end. It does not mean Sentinel decides
correctly. Those are different claims and only the first is in evidence here.

For gate evidence use the deep profile — ./scripts/test.sh --gate — not this default.
COVERAGE
