import {describe, it} from "node:test";
import {decodablePurchaseCallData} from "./harness.ts";
import assert from "node:assert/strict";
import {keccak256, stringToBytes} from "viem";
import {createAttestor} from "../src/signer/attest.ts";
import {domainSeparator} from "../src/signer/eip712.ts";
import {
    REASON_SEVERITY,
    severityOf,
    type EvaluateAndSignResult,
    type Hex,
    type ReasonCode,
} from "../src/signer/protocol.ts";
import {
    CHAIN_ID,
    NOW,
    OTHER_ADDRESS,
    SIM_BLOCK_NUMBER,
    VAULT,
    buildFixture,
    fakeKeystore,
    mutableChain,
    type FixtureOverrides,
} from "./fakes.ts";

/**
 * One test per declared reason code.
 *
 * WHY THIS FILE EXISTS. An adversarial review found that 22 of the signer's 31 checks were
 * exercised by nothing: the whole suite stayed green with `SIGNER_MANDATE_WINDOW` deleted,
 * while an expired mandate signed an ALLOW and executed on the real vault. Mutation testing
 * had not caught it either, because the mutation set was written from the same reading of
 * the code that produced the tests — it probed the checks someone had already thought about.
 *
 * The structural fix is the exhaustiveness test at the bottom: it enumerates
 * `REASON_SEVERITY` and fails if any code lacks a case here. A reason code added later
 * without a test turns this file red rather than joining the 22.
 *
 * COVERAGE BOUNDARY. These prove each check FIRES on its own trigger and that its severity
 * tier is honoured. They do not prove the checks are the RIGHT checks, and they say nothing
 * about verdict correctness — the verdict is an input throughout.
 */

async function run(overrides: FixtureOverrides): Promise<EvaluateAndSignResult> {
    const {request, chain} = buildFixture(overrides);
    const attestor = createAttestor({
        chainId: CHAIN_ID,
        vault: VAULT,
        keystore: fakeKeystore(),
        chain,
        now: () => NOW,
        randomBytes32: () => keccak256(stringToBytes("decision")),
    });
    return attestor.evaluateAndSign(request);
}

/** Findings reported, whether the request was signed or refused. */
function findingsOf(result: EvaluateAndSignResult): string[] {
    return result.signerFindings as string[];
}

/**
 * Every declared code, with the single perturbation that should trigger it.
 *
 * Each case changes ONE dimension. That discipline is inherited from a documented dead end
 * in this repository: randomising several dimensions at once produced an invariant campaign
 * of 16,384 calls with zero executions and all-green results.
 */
const CASES: {code: ReasonCode; overrides: FixtureOverrides}[] = [
    // --- FATAL ---
    {code: "SIGNER_DATAHASH_MISMATCH", overrides: {action: {dataHash: keccak256(stringToBytes("lie"))}}},
    {code: "SIGNER_WRONG_VAULT", overrides: {action: {vault: OTHER_ADDRESS}}},
    {code: "SIGNER_WRONG_CHAIN", overrides: {action: {chainId: 999n}}},
    {code: "SIGNER_VAULT_UNREACHABLE", overrides: {vaultUnreachable: true}},
    {code: "SIGNER_CHAIN_UNSTABLE", overrides: {chainUnstable: true}},
    {
        code: "SIGNER_DOMAIN_SEPARATOR_MISMATCH",
        overrides: {state: {domainSeparator: domainSeparator(CHAIN_ID, OTHER_ADDRESS)}},
    },
    {code: "SIGNER_CALLDATA_TOO_SHORT", overrides: {callData: "0xa1b2"}},
    // D-014. The fixture calldata carries an unsupported selector, so the signer's own
    // decoding fails; a bundle claiming it decoded is a bundle misdescribing the action.
    {
        code: "SIGNER_EVIDENCE_DECODING_MISMATCH",
        overrides: {
            evidenceCanonical: JSON.stringify({
                decodedSelectorAndParameters: {decoded: "true", selector: "0xa1b2c3d4"},
            }),
        },
    },
    {
        code: "SIGNER_EVIDENCE_DECODING_ABSENT",
        overrides: {evidenceCanonical: "{}"},
    },

    // --- EXECUTABILITY ---
    {code: "SIGNER_NOT_ACTIVE_SIGNER", overrides: {state: {signer: OTHER_ADDRESS}}},
    {code: "SIGNER_NONCE_MISMATCH", overrides: {action: {actionNonce: 42n}}},
    {code: "SIGNER_VAULT_PAUSED", overrides: {state: {paused: true}}},
    {code: "SIGNER_ACTION_EXPIRED", overrides: {action: {deadline: NOW - 1n}}},

    // --- CONFORMANCE ---
    {code: "SIGNER_SIMULATION_BLOCK_MISMATCH", overrides: {blockMissing: true}},
    // D-055(c). ONE dimension: the anchor names a different HEIGHT. The fake reports the
    // fixture hash at every height, so `blockHashAt` still agrees and
    // SIGNER_SIMULATION_BLOCK_MISMATCH does NOT fire — which is the point. This block is
    // real; it is simply not the one the signer read.
    {code: "SIGNER_ANCHOR_NOT_OBSERVED", overrides: {simulationBlockNumber: SIM_BLOCK_NUMBER - 1n}},
    {
        code: "SIGNER_MANDATE_NOT_ACTIVE",
        overrides: {state: {activeMandateHash: keccak256(stringToBytes("another mandate"))}},
    },
    {
        code: "SIGNER_POLICY_NOT_ACTIVE",
        overrides: {state: {activePolicyHash: keccak256(stringToBytes("another policy"))}},
    },
    {
        code: "SIGNER_ACTION_BINDING_STALE",
        overrides: {action: {mandateHash: keccak256(stringToBytes("stale binding"))}},
    },
    {code: "SIGNER_MANDATE_TARGET_MISMATCH", overrides: {action: {target: OTHER_ADDRESS}}},
    {code: "SIGNER_MANDATE_SELECTOR_MISMATCH", overrides: {mandate: {selector: "0xdeadbeef"}}},
    {code: "SIGNER_MANDATE_VALUE_EXCEEDED", overrides: {mandate: {maxNativeValueWei: 1n}}},
    {code: "SIGNER_MANDATE_WINDOW", overrides: {mandate: {validUntil: NOW - 1n}}},
    {code: "SIGNER_MANDATE_PRINCIPAL_MISMATCH", overrides: {state: {owner: OTHER_ADDRESS}}},
    {
        code: "SIGNER_MANDATE_POLICY_LINK_MISMATCH",
        overrides: {mandate: {policyHash: keccak256(stringToBytes("unlinked policy"))}},
    },
    {code: "SIGNER_MANDATE_SCOPE_MISMATCH", overrides: {mandate: {vault: OTHER_ADDRESS}}},
    {
        code: "SIGNER_TARGET_CODEHASH_MISMATCH",
        overrides: {state: {targetCodeHash: keccak256(stringToBytes("yesterday's bytecode"))}},
    },
    {code: "SIGNER_POLICY_SCOPE_MISMATCH", overrides: {policy: {vault: OTHER_ADDRESS}}},
    {code: "SIGNER_POLICY_OPERATION_MISMATCH", overrides: {policy: {allowedOperation: 1n}}},
    {code: "SIGNER_POLICY_VALUE_EXCEEDED", overrides: {policy: {maxNativeValueWei: 1n}}},
    {code: "SIGNER_POLICY_WINDOW", overrides: {policy: {validUntil: NOW - 1n}}},
    {code: "SIGNER_UNSUPPORTED_OPERATION", overrides: {action: {operation: 1n}}},
    {code: "SIGNER_VAULT_VALUE_CAP_EXCEEDED", overrides: {state: {maxNativeValueWei: 1n}}},
    {code: "SIGNER_VAULT_TARGET_NOT_ALLOWED", overrides: {state: {targetAllowed: false}}},
    {code: "SIGNER_VAULT_SELECTOR_NOT_ALLOWED", overrides: {state: {selectorAllowed: false}}},
];

describe("the fully-conforming baseline", () => {
    it("produces a signed ALLOW with no findings at all", async () => {
        // The control. Without it, every "the check fired" assertion below could be
        // satisfied by a fixture that was broken in some unrelated way.
        const result = await run({});
        assert.equal(result.refused, false, "the baseline fixture must conform");
        assert.deepEqual(findingsOf(result), []);
    });
});

describe("every reason code fires on its own trigger", () => {
    for (const {code, overrides} of CASES) {
        it(`${code} (${severityOf(code)})`, async () => {
            const result = await run({...overrides, verdict: "ALLOW"});

            // Every signer finding blocks ALLOW by construction, so an ALLOW request is the
            // one verdict under which any code must produce a refusal.
            assert.equal(result.refused, true, `${code} did not refuse an ALLOW`);
            assert.ok(
                findingsOf(result).includes(code),
                `expected ${code}, got [${findingsOf(result).join(", ")}]`,
            );
            assert.ok(
                (result as {blocking: {code: string}[]}).blocking.some((b) => b.code === code),
                `${code} fired but was not listed as blocking`,
            );
        });
    }
});

describe("severity tiers are honoured per verdict", () => {
    it("FATAL codes refuse BLOCK and REVIEW as well as ALLOW", async () => {
        const fatal = CASES.filter((c) => severityOf(c.code) === "FATAL");
        assert.ok(fatal.length >= 5, "expected the FATAL tier to be non-trivial");
        for (const {code, overrides} of fatal) {
            for (const verdict of ["BLOCK", "REVIEW"] as const) {
                const result = await run({...overrides, verdict});
                assert.equal(result.refused, true, `${code} should refuse ${verdict}`);
            }
        }
    });

    it("EXECUTABILITY codes refuse REVIEW but permit a signed BLOCK", async () => {
        const exec = CASES.filter((c) => severityOf(c.code) === "EXECUTABILITY");
        assert.ok(exec.length >= 4);
        for (const {code, overrides} of exec) {
            const review = await run({...overrides, verdict: "REVIEW"});
            assert.equal(review.refused, true, `${code} should refuse REVIEW`);

            const blocked = await run({...overrides, verdict: "BLOCK"});
            assert.equal(blocked.refused, false, `${code} should still permit a BLOCK receipt`);
            assert.ok(findingsOf(blocked).includes(code));
        }
    });

    it("CONFORMANCE codes permit a signed REVIEW — this is what keeps Case 4 reachable", async () => {
        // §4.2 Case 4: a changed target code hash, a proxy target, conflicting anchored
        // state, or unavailable simulation must all yield a REVIEW receipt. Asserting it for
        // the whole tier rather than one example is deliberate: the original tiering got
        // SIGNER_TARGET_CODEHASH_MISMATCH right and its sibling
        // SIGNER_SIMULATION_BLOCK_MISMATCH wrong, from the same sentence of the spec.
        const conformance = CASES.filter((c) => severityOf(c.code) === "CONFORMANCE");
        assert.ok(conformance.length >= 15);
        for (const {code, overrides} of conformance) {
            const result = await run({...overrides, verdict: "REVIEW"});
            assert.equal(result.refused, false, `${code} must permit a REVIEW receipt`);
            assert.ok(findingsOf(result).includes(code));
            assert.equal(result.receipt.verdict, 1n);
        }
    });

    it("names both Case 4 anchored-state triggers in the same tier", async () => {
        // The specific regression that motivated the tier-wide assertion above.
        assert.equal(severityOf("SIGNER_TARGET_CODEHASH_MISMATCH"), "CONFORMANCE");
        assert.equal(severityOf("SIGNER_SIMULATION_BLOCK_MISMATCH"), "CONFORMANCE");
    });

    it("compares the anchor's HASH, not only its height (D-055(c))", async () => {
        // The half no end-to-end route can reach. A superseded block differs from the head
        // in both number and hash, so the e2e exploit passes against a signer that compares
        // heights alone — and that signer accepts a same-height reorg, which is precisely
        // the case the pair exists for.
        //
        // ONE dimension: the number still agrees, and `blockHashAt` still reports the
        // fixture hash at every height, so SIGNER_SIMULATION_BLOCK_MISMATCH cannot be what
        // fires. Asserted absent below for that reason.
        const result = await run({
            state: {observedBlockHash: keccak256(stringToBytes("a different block, same height"))},
        });
        assert.equal(result.refused, true);
        const codes = findingsOf(result);
        assert.ok(codes.includes("SIGNER_ANCHOR_NOT_OBSERVED"));
        assert.ok(!codes.includes("SIGNER_SIMULATION_BLOCK_MISMATCH"));
    });

    it("SIGNER_CHAIN_UNSTABLE is not filed as SIGNER_VAULT_UNREACHABLE (D-055(c))", async () => {
        // Both are FATAL and both refuse everything, so the tiering cannot tell them apart.
        // The RECORD is what distinguishes them, and a refusal that reported the wrong one
        // would state something the evidence does not support.
        const unstable = findingsOf(await run({chainUnstable: true}));
        assert.ok(unstable.includes("SIGNER_CHAIN_UNSTABLE"));
        assert.ok(!unstable.includes("SIGNER_VAULT_UNREACHABLE"));

        const unreachable = findingsOf(await run({vaultUnreachable: true}));
        assert.ok(unreachable.includes("SIGNER_VAULT_UNREACHABLE"));
        assert.ok(!unreachable.includes("SIGNER_CHAIN_UNSTABLE"));
    });
});

describe("reason codes reach the receipt", () => {
    it("commits the signer's findings and the evaluator's under one hash", async () => {
        const result = await run({
            verdict: "REVIEW",
            reasonCodes: ["EVALUATOR_TARGET_CODE_IDENTITY_UNVERIFIED"],
            state: {targetCodeHash: keccak256(stringToBytes("changed"))},
        });
        assert.equal(result.refused, false);
        assert.deepEqual(result.reasonCodes, [
            "EVALUATOR_TARGET_CODE_IDENTITY_UNVERIFIED",
            "SIGNER_TARGET_CODEHASH_MISMATCH",
        ]);
    });

    it("rejects a reason code that could forge or hide a finding", async () => {
        // A code containing the "\n" delimiter would make the canonical encoding
        // non-injective: ["A\nB"] and ["A","B"] would hash identically, so a receipt holder
        // could present a list that verifies while containing none of the true codes as
        // elements. Confirmed by adversarial review before it was fixed.
        await assert.rejects(
            () => run({reasonCodes: ["EVALUATOR_OK\nSIGNER_TARGET_CODEHASH_MISMATCH"]}),
            /not \^\[A-Za-z0-9_\.:-\]/,
        );
        await assert.rejects(() => run({reasonCodes: [""]}), /not \^\[A-Za-z0-9_\.:-\]/);
    });
});

describe("the reason-code table is exhaustive", () => {
    it("has a case for every declared code", () => {
        // The structural guard. A new reason code without a test fails here rather than
        // joining the 22 that an adversarial review had to find.
        //
        // The exception list is asserted to be EXACTLY this one code, so it cannot quietly
        // become the place uncovered codes go to be forgotten — which is the failure mode
        // the whole file exists to prevent.
        const TABLE_CANNOT_REACH = ["SIGNER_NONCE_ALREADY_ATTESTED"]; // needs two requests
        assert.deepEqual(TABLE_CANNOT_REACH, ["SIGNER_NONCE_ALREADY_ATTESTED"]);

        const declared = Object.keys(REASON_SEVERITY).sort();
        const tested = [...new Set([...CASES.map((c) => c.code as string), ...TABLE_CANNOT_REACH])]
            .sort();
        assert.deepEqual(
            declared.filter((c) => !tested.includes(c)),
            [],
            "reason codes declared but never triggered by any test",
        );
        assert.deepEqual(
            tested.filter((c) => !declared.includes(c)),
            [],
            "tests reference reason codes that no longer exist",
        );
    });

    it("covers SIGNER_NONCE_ALREADY_ATTESTED, which needs two requests", async () => {
        // The one code a single-request table cannot reach.
        const {request, chain} = buildFixture({});
        const attestor = createAttestor({
            chainId: CHAIN_ID,
            vault: VAULT,
            keystore: fakeKeystore(),
            chain,
            now: () => NOW,
            randomBytes32: () => keccak256(stringToBytes("decision")),
        });
        assert.equal((await attestor.evaluateAndSign(request)).refused, false);

        const other = buildFixture({callData: decodablePurchaseCallData("rc-11")});
        const second = await attestor.evaluateAndSign(other.request);
        assert.equal(second.refused, true);
        assert.ok(findingsOf(second).includes("SIGNER_NONCE_ALREADY_ATTESTED"));
    });
});

describe("the attestation guard is scoped to the authorisation basis", () => {
    it("releases the nonce when the owner activates a new mandate (§4.2 Case 4)", async () => {
        // Case 4's second remedy: "Execution requires a separately signed exact-action owner
        // override OR A NEW MANDATE." A reservation taken under the old mandate must not
        // refuse the corrected action taken under the new one. Reviewed and confirmed as a
        // real liveness limit before this scoping was added.
        const first = buildFixture({
            verdict: "REVIEW",
            state: {targetCodeHash: keccak256(stringToBytes("stale code"))},
        });
        const {chain, activate} = mutableChain(first);
        const attestor = createAttestor({
            chainId: CHAIN_ID,
            vault: VAULT,
            keystore: fakeKeystore(),
            chain,
            now: () => NOW,
            randomBytes32: () => keccak256(stringToBytes("decision")),
        });
        assert.equal((await attestor.evaluateAndSign(first.request)).refused, false);

        // The owner activates a corrected mandate; the action changes with it. Activating it
        // on the chain the signer READS is the whole point — the signer's view of "active"
        // comes from the vault, never from the request.
        const corrected = buildFixture({
            mandate: {mandateId: keccak256(stringToBytes("mandate:corrected"))},
            callData: decodablePurchaseCallData("rc-22"),
        });
        activate(corrected);

        const result = await attestor.evaluateAndSign(corrected.request);
        assert.equal(
            result.refused,
            false,
            `a new mandate must free the nonce the old decision reserved; got ` +
                `${JSON.stringify((result as {blocking?: unknown}).blocking)}`,
        );
    });

    it("still refuses a different action under the SAME mandate", async () => {
        // The complement: the scoping must not have quietly disabled the guard.
        const {request, chain} = buildFixture({});
        const attestor = createAttestor({
            chainId: CHAIN_ID,
            vault: VAULT,
            keystore: fakeKeystore(),
            chain,
            now: () => NOW,
            randomBytes32: () => keccak256(stringToBytes("decision")),
        });
        assert.equal((await attestor.evaluateAndSign(request)).refused, false);

        const sameMandate = buildFixture({callData: decodablePurchaseCallData("rc-33")});
        const second = await attestor.evaluateAndSign(sameMandate.request);
        assert.equal(second.refused, true);
        assert.ok(findingsOf(second).includes("SIGNER_NONCE_ALREADY_ATTESTED"));
    });

    // ---- D-053(b): THE BASIS CYCLE, AND THE ARGUMENT AROUND IT --------------------------
    //
    // The guard used to key reservations by nonce alone, so a basis change OVERWROTE the
    // earlier reservation instead of superseding it. Round six showed the consequence: rotate
    // M1 -> M2 -> M1 and the nonce is free again, leaving two live credentials under the SAME
    // active mandate — where A-012(a)'s "the vault reverts MandateNotActive on the stale one"
    // escape cannot engage, because neither is stale.
    //
    // John's ruling was explicit that the repair must cover the ARGUMENT, not M1 -> M2 -> M1.
    // Each case below is one of the seven he enumerated.

    const cycleAttestor = (chain: Parameters<typeof createAttestor>[0]["chain"]) =>
        createAttestor({
            chainId: CHAIN_ID, vault: VAULT, keystore: fakeKeystore(), chain,
            now: () => NOW, randomBytes32: () => keccak256(stringToBytes("decision")),
        });

    it("a MANDATE cycle does not free a nonce the first action still holds", async () => {
        const f1 = buildFixture({});
        const {chain, activate} = mutableChain(f1);
        const attestor = cycleAttestor(chain);
        assert.equal((await attestor.evaluateAndSign(f1.request)).refused, false);

        const f2 = buildFixture({
            mandate: {mandateId: keccak256(stringToBytes("mandate:M2"))},
            callData: decodablePurchaseCallData("cycle-m2"),
        });
        activate(f2);
        // The new mandate is IMMEDIATELY usable — Case 4's remedy must survive the repair.
        assert.equal((await attestor.evaluateAndSign(f2.request)).refused, false);

        activate(f1); // back to M1
        const f3 = buildFixture({callData: decodablePurchaseCallData("cycle-m1-again")});
        const third = await attestor.evaluateAndSign(f3.request);
        assert.equal(third.refused, true, "the cycle freed a nonce the first action still holds");
        assert.ok(findingsOf(third).includes("SIGNER_NONCE_ALREADY_ATTESTED"));
    });

    it("a POLICY cycle behaves the same as a mandate cycle", async () => {
        // The basis is (mandate, policy). Pinning only the mandate half would be the same
        // partial repair this project keeps making.
        const f1 = buildFixture({});
        const {chain, activate} = mutableChain(f1);
        const attestor = cycleAttestor(chain);
        assert.equal((await attestor.evaluateAndSign(f1.request)).refused, false);

        const f2 = buildFixture({
            policy: {policyVersion: 99n},
            callData: decodablePurchaseCallData("cycle-p2"),
        });
        activate(f2);
        assert.equal((await attestor.evaluateAndSign(f2.request)).refused, false);

        activate(f1);
        const f3 = buildFixture({callData: decodablePurchaseCallData("cycle-p1-again")});
        const third = await attestor.evaluateAndSign(f3.request);
        assert.equal(third.refused, true, "a policy cycle freed the nonce");
        assert.ok(findingsOf(third).includes("SIGNER_NONCE_ALREADY_ATTESTED"));
    });

    it("an idempotent re-sign of the SAME action still succeeds after a cycle", async () => {
        // Preserving reservations must not deadlock the retry path a lost response needs.
        const f1 = buildFixture({});
        const {chain, activate} = mutableChain(f1);
        const attestor = cycleAttestor(chain);
        assert.equal((await attestor.evaluateAndSign(f1.request)).refused, false);

        const f2 = buildFixture({
            mandate: {mandateId: keccak256(stringToBytes("mandate:M2"))},
            callData: decodablePurchaseCallData("cycle-idem-m2"),
        });
        activate(f2);
        assert.equal((await attestor.evaluateAndSign(f2.request)).refused, false);

        activate(f1);
        const again = await attestor.evaluateAndSign(f1.request); // the SAME action as before
        assert.equal(again.refused, false, "an idempotent re-sign must not be refused");
    });

    it("an EXPIRED superseded reservation no longer holds the nonce after a cycle", async () => {
        // Expiry, not overwriting, is what releases a reservation now. If that stopped working
        // a cycle would wedge the nonce for the rest of the TTL.
        const f1 = buildFixture({});
        const {chain, activate} = mutableChain(f1);
        let clock = NOW;
        const attestor = createAttestor({
            chainId: CHAIN_ID, vault: VAULT, keystore: fakeKeystore(), chain,
            now: () => clock, randomBytes32: () => keccak256(stringToBytes("decision")),
        });
        assert.equal((await attestor.evaluateAndSign(f1.request)).refused, false);

        const f2 = buildFixture({
            mandate: {mandateId: keccak256(stringToBytes("mandate:M2"))},
            callData: decodablePurchaseCallData("cycle-exp-m2"),
        });
        activate(f2);
        assert.equal((await attestor.evaluateAndSign(f2.request)).refused, false);

        clock = NOW + 7200n; // past any TTL the signer will grant
        activate(f1);
        const f3 = buildFixture({callData: decodablePurchaseCallData("cycle-exp-m1")});
        assert.equal((await attestor.evaluateAndSign(f3.request)).refused, false,
            "an expired reservation must not keep holding the nonce");
    });

    it("a REVIEW reservation survives a cycle, not just an ALLOW one", async () => {
        // REVIEW reserves because an owner override makes it executable. If only ALLOW
        // reservations were preserved, the human-in-the-loop path would carry the hole.
        const f1 = buildFixture({
            verdict: "REVIEW",
            state: {targetCodeHash: keccak256(stringToBytes("stale code"))},
        });
        const {chain, activate} = mutableChain(f1);
        const attestor = cycleAttestor(chain);
        assert.equal((await attestor.evaluateAndSign(f1.request)).refused, false);

        const f2 = buildFixture({
            mandate: {mandateId: keccak256(stringToBytes("mandate:M2"))},
            callData: decodablePurchaseCallData("cycle-review-m2"),
        });
        activate(f2);
        assert.equal((await attestor.evaluateAndSign(f2.request)).refused, false);

        activate(f1);
        const f3 = buildFixture({
            verdict: "REVIEW",
            state: {targetCodeHash: keccak256(stringToBytes("stale code"))},
            callData: decodablePurchaseCallData("cycle-review-m1"),
        });
        const third = await attestor.evaluateAndSign(f3.request);
        assert.equal(third.refused, true, "a REVIEW reservation was lost across the cycle");
        assert.ok(findingsOf(third).includes("SIGNER_NONCE_ALREADY_ATTESTED"));
    });

    it("never shortens a live reservation via a smaller caller-supplied TTL", async () => {
        // `ttlSeconds` is a caller field. An idempotent re-sign with a tiny TTL must not move
        // the reservation's expiry earlier than the receipt already issued, or a different
        // action could be signed alongside a still-valid ALLOW. Found by adversarial review.
        const chain = buildFixture({}).chain;
        let clock = NOW;
        const attestor = createAttestor({
            chainId: CHAIN_ID,
            vault: VAULT,
            keystore: fakeKeystore(),
            chain,
            now: () => clock,
            randomBytes32: () => keccak256(stringToBytes("decision")),
        });

        const long = buildFixture({ttlSeconds: 3600n});
        assert.equal((await attestor.evaluateAndSign(long.request)).refused, false);

        // Same action, one-second TTL. Legal, idempotent, and must not shorten the hold.
        const shortRetry = buildFixture({ttlSeconds: 1n});
        assert.equal((await attestor.evaluateAndSign(shortRetry.request)).refused, false);

        clock = NOW + 10n; // past the 1s TTL, far inside the 3600s one
        const rival = buildFixture({callData: decodablePurchaseCallData("rc-44")});
        const result = await attestor.evaluateAndSign(rival.request);
        assert.equal(result.refused, true, "the long reservation must still hold the nonce");
        assert.ok(findingsOf(result).includes("SIGNER_NONCE_ALREADY_ATTESTED"));
    });
});

describe("fail-closed on dependency failure (§3.3(8))", () => {
    it("refuses every verdict when the vault cannot be read", async () => {
        for (const verdict of ["ALLOW", "REVIEW", "BLOCK"] as const) {
            const result = await run({vaultUnreachable: true, verdict});
            assert.equal(result.refused, true, `an unreadable vault must refuse ${verdict}`);
            assert.ok(findingsOf(result).includes("SIGNER_VAULT_UNREACHABLE"));
        }
    });

    it("never reaches the signing key on a refusal", async () => {
        // Stronger than "the response said refused": the key is not touched at all.
        const {request, chain} = buildFixture({action: {actionNonce: 42n}});
        const keystore = fakeKeystore();
        const attestor = createAttestor({
            chainId: CHAIN_ID,
            vault: VAULT,
            keystore,
            chain,
            now: () => NOW,
            randomBytes32: () => keccak256(stringToBytes("decision")),
        });
        assert.equal((await attestor.evaluateAndSign(request)).refused, true);
        assert.equal(keystore.signCount(), 0);
    });

    it("records the block it observed, and refuses a height the chain lacks", async () => {
        const ok = await run({});
        assert.equal(ok.refused, false);
        assert.equal(ok.receipt.simulationBlockNumber, SIM_BLOCK_NUMBER);

        const bad = await run({blockMissing: true});
        assert.equal(bad.refused, true);
    });
});
