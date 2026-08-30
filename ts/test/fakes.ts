import {keccak256, stringToBytes, toBytes} from "viem";
import {domainSeparator, hashMandate, hashPolicy} from "../src/signer/eip712.ts";
import {decodablePurchaseCallData, evidenceStub} from "./harness.ts";
import type {Keystore} from "../src/signer/keystore.ts";
import {ChainUnstableError, SNAPSHOT_ATTEMPTS} from "../src/signer/vault.ts";
import type {ChainReader, VaultState} from "../src/signer/vault.ts";
import type {
    ActionPayload,
    EvaluateAndSignRequest,
    Hex,
    MandatePayload,
    PolicyPayload,
    VerdictName,
} from "../src/signer/protocol.ts";

/**
 * A fully-conforming signer request, plus the fake chain it conforms to, with every value
 * derived so a single perturbation stays consistent everywhere else.
 *
 * WHY FAKES HERE WHEN THE OTHER SUITES USE A REAL ANVIL AND A REAL SIGNER PROCESS.
 * The end-to-end suite proves the real stack works and that isolation is real; it cannot
 * cheaply reach every branch. Several of the signer's checks are unreachable over a real
 * chain without contorting it — a vault that is unreadable mid-request, a vault whose
 * reported domain separator disagrees with the library that compiled it, a mandate whose
 * principal is not the owner. An adversarial review found the consequence: 22 of the
 * signer's 31 checks had no test at all, and deleting one of them left the whole suite
 * green while an expired mandate executed on the real vault.
 *
 * THE DERIVATION IS THE POINT. Perturbing one field of a §5 payload changes its hash, which
 * changes what "active" means, which changes which check fires. A fixture with hardcoded
 * hashes would silently trigger SIGNER_MANDATE_NOT_ACTIVE for every mandate-content test
 * and the tests would pass for the wrong reason. So `buildFixture` recomputes the vault's
 * active hashes FROM the (possibly perturbed) payloads, and the test author overrides
 * `state` explicitly when the intent is a mismatch.
 */

export const CHAIN_ID = 31337n;
export const VAULT: Hex = "0x1111111111111111111111111111111111111111";
export const TARGET: Hex = "0x2222222222222222222222222222222222222222";
export const OWNER: Hex = "0x3333333333333333333333333333333333333333";
export const SIGNER_ADDRESS: Hex = "0x4444444444444444444444444444444444444444";
export const OTHER_ADDRESS: Hex = "0x9999999999999999999999999999999999999999";

export const SIM_BLOCK_NUMBER = 100n;
export const SIM_BLOCK_HASH: Hex = keccak256(stringToBytes("pinned simulation block"));
export const TARGET_CODE_HASH: Hex = keccak256(stringToBytes("DemoPay runtime code"));

/** `purchase(bytes32,address,uint64,bool)`-shaped: a 4-byte selector plus four words. */
export const SELECTOR: Hex = "0xc188528b"; // DemoPay.purchase — must match CALLDATA below (A-043)
/**
 * The shared fixture calldata, and it MUST be decodable by the signer's own decoder.
 *
 * A-043. This was `0xa1b2c3d4…`, an unsupported selector, chosen as arbitrary bytes for tests
 * about other things. That made the signer's own decode fail, which made the evidence stub
 * honestly report `decoded:"false"`, which made the signer return NO finding for an ALLOW —
 * so the default fixture for the whole unit suite ran through the exact hole this review
 * found. Tests about undecodable calldata should say so explicitly with their own bytes.
 */
export const CALLDATA: Hex = decodablePurchaseCallData("shared-fixture");

/** A clock the tests control. All windows below are open at this instant. */
export const NOW = 1_800_000_000n;

export interface FixtureOverrides {
    mandate?: Partial<MandatePayload>;
    policy?: Partial<PolicyPayload>;
    action?: Partial<ActionPayload>;
    state?: Partial<VaultState>;
    callData?: Hex;
    verdict?: VerdictName;
    reasonCodes?: string[];
    simulationBlockNumber?: bigint;
    simulationBlockHash?: Hex;
    ttlSeconds?: bigint;
    /** Overrides the evidence bundle, for the D-014 decoding-bind cases. */
    evidenceCanonical?: string;
    /** Makes every vault read throw, for the fail-closed path. */
    vaultUnreachable?: boolean;
    /**
     * Makes every vault read throw `ChainUnstableError`, for the D-055(c) path where the
     * head moved on every attempt. Distinct from `vaultUnreachable` because the two produce
     * different reason codes, and a fixture that could not tell them apart could not prove
     * that the distinction is real.
     */
    chainUnstable?: boolean;
    /** Makes the chain report no block at the requested height. */
    blockMissing?: boolean;
}

export interface Fixture {
    request: EvaluateAndSignRequest;
    state: VaultState;
    chain: ChainReader;
    mandate: MandatePayload;
    policy: PolicyPayload;
}

export function buildFixture(o: FixtureOverrides = {}): Fixture {
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
        validUntil: NOW + 100_000n,
        failureMode: 0n,
        ...o.policy,
    };
    const policyHash = hashPolicy(policy);

    const mandate: MandatePayload = {
        schemaVersion: 1n,
        mandateId: keccak256(stringToBytes("mandate:fixture")),
        principal: OWNER,
        signer: SIGNER_ADDRESS,
        vault: VAULT,
        chainId: CHAIN_ID,
        target: TARGET,
        targetCodeHash: TARGET_CODE_HASH,
        selector: SELECTOR,
        maxNativeValueWei: 10n ** 18n,
        purposeKind: keccak256(stringToBytes("purpose")),
        resourceId: keccak256(stringToBytes("resource")),
        beneficiary: OWNER,
        durationSeconds: 86_400n,
        recurringAllowed: false,
        validAfter: 0n,
        validUntil: NOW + 100_000n,
        // Derived, but overridable — SIGNER_MANDATE_POLICY_LINK_MISMATCH needs it broken.
        policyHash,
        ...o.mandate,
    };
    const mandateHash = hashMandate(mandate);

    const callData = o.callData ?? CALLDATA;

    // The vault's view. Defaults agree with the payloads above, so a test that wants a
    // disagreement states it rather than inheriting it.
    const state: VaultState = {
        owner: mandate.principal,
        signer: SIGNER_ADDRESS,
        activeMandateHash: mandateHash,
        activePolicyHash: policyHash,
        actionNonce: 0n,
        paused: false,
        maxNativeValueWei: 10n ** 18n,
        targetAllowed: true,
        selectorAllowed: true,
        domainSeparator: domainSeparator(CHAIN_ID, VAULT),
        targetCodeHash: mandate.targetCodeHash,
        observedAtBlock: SIM_BLOCK_NUMBER,
        // D-055(c): the default fixture is CONSISTENT — the block the signer read is the
        // block the evaluation anchored to. A test wanting a stale anchor states it.
        observedBlockHash: SIM_BLOCK_HASH,
        ...o.state,
    };

    const action: ActionPayload = {
        schemaVersion: 1n,
        chainId: CHAIN_ID,
        vault: VAULT,
        actionNonce: state.actionNonce,
        target: mandate.target,
        valueWei: 1_000n,
        dataHash: keccak256(toBytes(callData)),
        operation: 0n,
        // Bound to what the VAULT reports active, which is what the signer compares against.
        mandateHash: state.activeMandateHash,
        policyHash: state.activePolicyHash,
        deadline: NOW + 10_000n,
        ...o.action,
    };

    const chain: ChainReader = {
        async chainId() {
            return CHAIN_ID;
        },
        async readVaultState() {
            if (o.vaultUnreachable === true) throw new Error("simulated RPC outage");
            if (o.chainUnstable === true) throw new ChainUnstableError(SNAPSHOT_ATTEMPTS);
            return state;
        },
        async blockHashAt() {
            return o.blockMissing === true ? null : SIM_BLOCK_HASH;
        },
    };

    const request: EvaluateAndSignRequest = {
        action,
        callData,
        mandate,
        policy,
        evaluation: {
            verdict: o.verdict ?? "ALLOW",
            reasonCodes: o.reasonCodes ?? [],
            evidenceCanonical: o.evidenceCanonical ?? evidenceStub("fixture", callData),
            simulationBlockNumber: o.simulationBlockNumber ?? SIM_BLOCK_NUMBER,
            simulationBlockHash: o.simulationBlockHash ?? SIM_BLOCK_HASH,
        },
        ...(o.ttlSeconds === undefined ? {} : {ttlSeconds: o.ttlSeconds}),
    };

    return {request, state, chain, mandate, policy};
}

/**
 * A chain whose vault state can be swapped between requests — the owner activating a new
 * mandate or policy (§3.2 steps 3–4).
 *
 * Needed because `buildFixture` closes over one immutable state, so an attestor built from
 * `fixture.chain` keeps reporting the mandate that fixture was built with no matter what a
 * later fixture says. A test for "a new mandate frees the reserved nonce" written against
 * the immutable chain fails for the wrong reason — the signer correctly reports
 * SIGNER_MANDATE_NOT_ACTIVE, because from its point of view nothing was ever activated.
 */
export function mutableChain(initial: Fixture): {
    chain: ChainReader;
    activate: (fixture: Fixture) => void;
} {
    let current = initial;
    return {
        chain: {
            async chainId() {
                return CHAIN_ID;
            },
            async readVaultState() {
                return current.state;
            },
            async blockHashAt() {
                return SIM_BLOCK_HASH;
            },
        },
        activate(fixture: Fixture) {
            current = fixture;
        },
    };
}

/**
 * A keystore that signs instantly and records what it was asked to sign.
 *
 * `signCount` is how a test asserts that a refused request never reached the key — which is
 * a stronger statement than "the response said refused".
 */
export function fakeKeystore(delayMs = 0): Keystore & {signCount: () => number} {
    let count = 0;
    return {
        address: SIGNER_ADDRESS,
        async signReceipt() {
            count += 1;
            if (delayMs > 0) await new Promise((resolve) => setTimeout(resolve, delayMs));
            return `0x${"ab".repeat(65)}` as Hex;
        },
        // D-012. Deliberately NOT counted by signCount: that counter exists to assert a
        // refused request never reached the RECEIPT-signing key, and a refusal signature is
        // exactly what a refusal is supposed to produce.
        async signRefusal() {
            return `0x${"cd".repeat(65)}` as Hex;
        },
        describe() {
            return {address: SIGNER_ADDRESS, source: "injected"};
        },
        signCount: () => count,
    };
}
