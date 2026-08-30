import {describe, it} from "node:test";
import assert from "node:assert/strict";
import {keccak256, stringToBytes} from "viem";
import {createAttestor} from "../src/signer/attest.ts";
import {decodablePurchaseCallData, evidenceStub} from "./harness.ts";
import {domainSeparator, hashMandate, hashPolicy} from "../src/signer/eip712.ts";
import type {Keystore} from "../src/signer/keystore.ts";
import type {ChainReader, VaultState} from "../src/signer/vault.ts";
import type {
    ActionPayload,
    EvaluateAndSignRequest,
    Hex,
    MandatePayload,
    PolicyPayload,
} from "../src/signer/protocol.ts";

/**
 * The per-nonce attestation guard under genuine concurrency.
 *
 * WHY THIS TEST IS IN-PROCESS, WHEN EVERY OTHER SIGNER TEST DELIBERATELY IS NOT.
 * The end-to-end suite spawns the real signer process because A-005's claim is about
 * isolation, and a claim about process boundaries cannot be tested by importing a module.
 * This test makes a different claim — that check-and-reserve is atomic with respect to
 * other in-flight requests — and that one is about the ordering of operations inside the
 * attestor. Testing it over a socket is not merely indirect, it is *unreliable*: the race
 * window is bounded by how long signing takes, signing resolves on a microtask, and a
 * competing request is meanwhile blocked on network I/O measured in milliseconds. The
 * socket-level test therefore passes against BOTH the correct and the incorrect ordering,
 * which was verified by re-breaking the attestor and watching it stay green.
 *
 * That is worth stating plainly, because it is the exact failure mode house rule 4 exists
 * to catch: a test that names a property it cannot actually observe is worse than no test.
 * The socket-level concurrency test is retained — it proves the invariant holds end-to-end
 * — but THIS is the test that proves the invariant is structural rather than a timing
 * accident, by making signing slow enough that the window is unmissable.
 *
 * Under the ordering this replaced — reserve AFTER `await signReceipt` — this test fails:
 * both requests observe an unreserved nonce and both are signed.
 */

const VAULT: Hex = "0x1111111111111111111111111111111111111111";
const TARGET: Hex = "0x2222222222222222222222222222222222222222";
const OWNER: Hex = "0x3333333333333333333333333333333333333333";
const SIGNER_ADDRESS: Hex = "0x4444444444444444444444444444444444444444";
const CHAIN_ID = 31337n;
const BLOCK_HASH: Hex = keccak256(stringToBytes("pinned block"));

const CALLDATA: Hex = decodablePurchaseCallData("concurrency-a");
const SELECTOR: Hex = "0xc188528b";

const policy: PolicyPayload = {
    schemaVersion: 1n,
    policyVersion: 1n,
    vault: VAULT,
    chainId: CHAIN_ID,
    allowedOperation: 0n,
    allowedTargetsHash: keccak256(stringToBytes("targets")),
    allowedSelectorsHash: keccak256(stringToBytes("selectors")),
    maxNativeValueWei: 10n ** 18n,
    maxAllowanceIncreaseBaseUnits: 0n,
    allowedCallGraphHash: keccak256(stringToBytes("graph")),
    validAfter: 0n,
    validUntil: 4_000_000_000n,
    failureMode: 0n,
};

const mandate: MandatePayload = {
    schemaVersion: 1n,
    mandateId: keccak256(stringToBytes("mandate")),
    principal: OWNER,
    signer: SIGNER_ADDRESS,
    vault: VAULT,
    chainId: CHAIN_ID,
    target: TARGET,
    targetCodeHash: keccak256(stringToBytes("target code")),
    selector: SELECTOR,
    maxNativeValueWei: 10n ** 18n,
    purposeKind: keccak256(stringToBytes("purpose")),
    resourceId: keccak256(stringToBytes("resource")),
    beneficiary: OWNER,
    durationSeconds: 86_400n,
    recurringAllowed: false,
    validAfter: 0n,
    validUntil: 4_000_000_000n,
    policyHash: hashPolicy(policy),
};

const state: VaultState = {
    owner: OWNER,
    signer: SIGNER_ADDRESS,
    activeMandateHash: hashMandate(mandate),
    activePolicyHash: hashPolicy(policy),
    actionNonce: 0n,
    paused: false,
    maxNativeValueWei: 10n ** 18n,
    targetAllowed: true,
    selectorAllowed: true,
    domainSeparator: domainSeparator(CHAIN_ID, VAULT),
    targetCodeHash: mandate.targetCodeHash,
    observedAtBlock: 100n,
    observedBlockHash: BLOCK_HASH,
};

const chain: ChainReader = {
    async chainId() {
        return CHAIN_ID;
    },
    async readVaultState() {
        return state;
    },
    async blockHashAt() {
        return BLOCK_HASH;
    },
};

/**
 * A keystore whose signing takes real wall-clock time.
 *
 * This is the whole point of the fixture: it widens the reserve-versus-sign window from
 * microtask-scale to 50ms, so an incorrect ordering fails deterministically instead of
 * failing once in a thousand runs on a loaded machine. It also models the plausible future
 * in which signing is not free — an HSM, a smartcard, a remote signer — where the ordering
 * bug would stop being a theoretical window and start being the common case.
 */
function slowKeystore(delayMs: number): Keystore & {signCount: () => number} {
    let count = 0;
    return {
        address: SIGNER_ADDRESS,
        async signReceipt() {
            count += 1;
            await new Promise((resolve) => setTimeout(resolve, delayMs));
            return `0x${"ab".repeat(65)}` as Hex;
        },
        async signRefusal() {
            return `0x${"cd".repeat(65)}` as Hex;
        },
        describe() {
            return {address: SIGNER_ADDRESS, source: "injected"};
        },
        signCount: () => count,
    };
}

function action(overrides: Partial<ActionPayload> = {}): ActionPayload {
    return {
        schemaVersion: 1n,
        chainId: CHAIN_ID,
        vault: VAULT,
        actionNonce: 0n,
        target: TARGET,
        valueWei: 1_000n,
        dataHash: keccak256(stringToBytes("placeholder")),
        operation: 0n,
        mandateHash: hashMandate(mandate),
        policyHash: hashPolicy(policy),
        deadline: 4_000_000_000n,
        ...overrides,
    };
}

function requestFor(a: ActionPayload, callData: Hex): EvaluateAndSignRequest {
    return {
        action: a,
        callData,
        mandate,
        policy,
        evaluation: {
            verdict: "ALLOW",
            reasonCodes: [],
            evidenceCanonical: evidenceStub("concurrency fixture", callData),
            simulationBlockNumber: 100n,
            simulationBlockHash: BLOCK_HASH,
        },
    };
}

describe("attestation guard atomicity", () => {
    it("signs exactly one of two overlapping ALLOWs at the same nonce", async () => {
        const keystore = slowKeystore(50);
        const attestor = createAttestor({
            chainId: CHAIN_ID,
            vault: VAULT,
            keystore,
            chain,
            now: () => 1_000_000n,
            randomBytes32: () => keccak256(stringToBytes("decision")),
        });

        // Two genuinely different actions competing for nonce 0. Only the calldata differs,
        // so both are otherwise fully conforming — the guard is the only thing that can
        // separate them.
        const callDataA: Hex = CALLDATA;
        const callDataB: Hex = decodablePurchaseCallData("concurrency-b");
        const a = action({dataHash: keccak256(hexToBytes(callDataA))});
        const b = action({dataHash: keccak256(hexToBytes(callDataB))});

        const [ra, rb] = await Promise.all([
            attestor.evaluateAndSign(requestFor(a, callDataA)),
            attestor.evaluateAndSign(requestFor(b, callDataB)),
        ]);

        const signed = [ra, rb].filter((r) => !r.refused);
        const refused = [ra, rb].filter((r) => r.refused);

        assert.equal(signed.length, 1, "exactly one overlapping request may hold the nonce");
        assert.equal(refused.length, 1);
        assert.equal(keystore.signCount(), 1, "the loser must never reach the signing key");

        const blocking = (refused[0] as {blocking: {code: string}[]}).blocking.map((x) => x.code);
        assert.ok(
            blocking.includes("SIGNER_NONCE_ALREADY_ATTESTED"),
            `expected SIGNER_NONCE_ALREADY_ATTESTED, got ${blocking.join(", ")}`,
        );
    });

    it("still permits an overlapping re-sign of the SAME action", async () => {
        // Idempotence must survive concurrency too: a retried request that raced its own
        // original must not be refused, or a dropped response would wedge the nonce.
        const keystore = slowKeystore(50);
        const attestor = createAttestor({
            chainId: CHAIN_ID,
            vault: VAULT,
            keystore,
            chain,
            now: () => 1_000_000n,
            randomBytes32: () => keccak256(stringToBytes("decision")),
        });

        const a = action({dataHash: keccak256(hexToBytes(CALLDATA))});
        const results = await Promise.all([
            attestor.evaluateAndSign(requestFor(a, CALLDATA)),
            attestor.evaluateAndSign(requestFor(a, CALLDATA)),
        ]);

        assert.deepEqual(
            results.map((r) => r.refused),
            [false, false],
        );
    });

    it("does not let an overlapping BLOCK consume the nonce", async () => {
        const keystore = slowKeystore(50);
        const attestor = createAttestor({
            chainId: CHAIN_ID,
            vault: VAULT,
            keystore,
            chain,
            now: () => 1_000_000n,
            randomBytes32: () => keccak256(stringToBytes("decision")),
        });

        const a = action({dataHash: keccak256(hexToBytes(CALLDATA))});
        const callDataB: Hex = decodablePurchaseCallData("concurrency-c");
        const b = action({dataHash: keccak256(hexToBytes(callDataB))});

        const blockRequest = {...requestFor(a, CALLDATA)};
        blockRequest.evaluation = {...blockRequest.evaluation, verdict: "BLOCK"};

        const [blocked, allowed] = await Promise.all([
            attestor.evaluateAndSign(blockRequest),
            attestor.evaluateAndSign(requestFor(b, callDataB)),
        ]);

        assert.equal(blocked.refused, false, "a BLOCK receipt is evidence and is always issued");
        assert.equal(allowed.refused, false, "and it must not have reserved the nonce");
    });
});

/** Local hex→bytes so this file shares no helper with the code under test. */
function hexToBytes(hex: Hex): Uint8Array {
    const digits = hex.slice(2);
    const out = new Uint8Array(digits.length / 2);
    for (let i = 0; i < out.length; i++) out[i] = parseInt(digits.slice(i * 2, i * 2 + 2), 16);
    return out;
}
