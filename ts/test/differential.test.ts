import {after, before, describe, it} from "node:test";
import assert from "node:assert/strict";
import {createPublicClient, createWalletClient, http, keccak256, stringToBytes} from "viem";
import type {Abi, Hex as ViemHex} from "viem";
import {anvil} from "viem/chains";
import {
    domainSeparator,
    hashAction,
    hashMandate,
    hashOverride,
    hashPolicy,
    hashReceipt,
} from "../src/signer/eip712.ts";
import type {
    ActionPayload,
    DecisionReceiptPayload,
    Hex,
    MandatePayload,
    OverrideAuthorizationPayload,
    PolicyPayload,
} from "../src/signer/protocol.ts";
import {OWNER, artifact, startAnvil, type AnvilHandle} from "./harness.ts";

/**
 * Cross-language differential: `ts/src/signer/eip712.ts` against `SentinelTypes.sol`,
 * over a real EVM, on all five §5 payloads plus the domain separator.
 *
 * WHY THIS IS SEPARATE FROM THE END-TO-END SUITE. Every passing end-to-end test already
 * checks `hashAction` and `hashReceipt` against Solidity, because the vault recomputes both
 * and recovers the signature over them. The other three get no such check for free:
 * SentinelVault stores the mandate and policy as hashes and never recomputes them from
 * their fields, so a TypeScript encoder that disagreed with Solidity on `hashMandate` would
 * simply activate its own wrong hash and match it. Every onchain test would stay green
 * while the two implementations quietly described different schemas.
 *
 * That is a real defect class, not a hypothetical one — the repository's own traces record
 * that "golden typehash constants pinned beside independently re-transcribed type strings
 * catch schema drift that either check alone would miss." This is the same idea carried
 * across the language boundary, and it is the check D-010's Python verifier will need to
 * have passed before it can be a meaningful third opinion rather than a third guess.
 *
 * The payloads below are generated from a seeded PRNG rather than hand-written constants.
 * Fixed vectors test the encoder on the values whoever wrote them happened to think of;
 * an all-zero or small-integer payload in particular would pass under several encoding
 * bugs at once — a wrong pad direction is invisible when the value is zero.
 */

let node: AnvilHandle;
let harness: Hex;
let harnessAbi: Abi;
let publicClient: ReturnType<typeof createPublicClient>;

before(async () => {
    node = await startAnvil();
    publicClient = createPublicClient({chain: anvil, transport: http(node.rpcUrl)});
    const walletClient = createWalletClient({chain: anvil, account: OWNER, transport: http(node.rpcUrl)});

    const art = artifact("TypesHarness.sol", "TypesHarness");
    harnessAbi = art.abi;
    const hash = await walletClient.deployContract({
        abi: art.abi,
        bytecode: art.bytecode,
        account: OWNER,
        chain: anvil,
        args: [],
    });
    const receipt = await publicClient.waitForTransactionReceipt({hash});
    harness = receipt.contractAddress!.toLowerCase() as Hex;
});

after(() => {
    node?.stop();
});

async function solidity(functionName: string, args: unknown[]): Promise<Hex> {
    const result = (await publicClient.readContract({
        address: harness as ViemHex,
        abi: harnessAbi,
        functionName,
        args: args as never,
    })) as string;
    return result.toLowerCase() as Hex;
}

// ---------------------------------------------------------------------------
// Seeded payload generation
// ---------------------------------------------------------------------------

/**
 * A deterministic 32-bit LCG. Deterministic on purpose: a differential failure has to be
 * reproducible from the test name alone, and `Math.random()` would make a red run something
 * you cannot ask a colleague to reproduce.
 */
function prng(seed: number): () => number {
    let state = seed >>> 0;
    return () => {
        state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
        return state;
    };
}

function generators(seed: number) {
    const next = prng(seed);
    const bytes = (n: number): Hex => {
        let out = "";
        for (let i = 0; i < n; i++) out += (next() & 0xff).toString(16).padStart(2, "0");
        return `0x${out}` as Hex;
    };
    return {
        // Values chosen to exercise the high end of each width: an encoder that pads the
        // wrong way, or truncates, is invisible on small numbers.
        uint: (bits: number): bigint => {
            const max = (1n << BigInt(bits)) - 1n;
            const draw = (BigInt(next()) << 32n) | BigInt(next());
            return draw % (max + 1n);
        },
        bytes32: () => bytes(32),
        bytes4: () => bytes(4),
        address: () => bytes(20),
        bool: () => (next() & 1) === 1,
    };
}

function payloads(seed: number): {
    mandate: MandatePayload;
    policy: PolicyPayload;
    action: ActionPayload;
    receipt: DecisionReceiptPayload;
    override: OverrideAuthorizationPayload;
    chainId: bigint;
    vault: Hex;
} {
    const g = generators(seed);
    return {
        mandate: {
            schemaVersion: g.uint(16),
            mandateId: g.bytes32(),
            principal: g.address(),
            vault: g.address(),
            chainId: g.uint(256),
            target: g.address(),
            targetCodeHash: g.bytes32(),
            selector: g.bytes4(),
            maxNativeValueWei: g.uint(256),
            purposeKind: g.bytes32(),
            resourceId: g.bytes32(),
            beneficiary: g.address(),
            durationSeconds: g.uint(64),
            recurringAllowed: g.bool(),
            validAfter: g.uint(64),
            validUntil: g.uint(64),
            policyHash: g.bytes32(),
        },
        policy: {
            schemaVersion: g.uint(16),
            policyVersion: g.uint(32),
            vault: g.address(),
            chainId: g.uint(256),
            allowedOperation: g.uint(8),
            allowedTargetsHash: g.bytes32(),
            allowedSelectorsHash: g.bytes32(),
            maxNativeValueWei: g.uint(256),
            maxAllowanceIncreaseBaseUnits: g.uint(256),
            allowedCallGraphHash: g.bytes32(),
            validAfter: g.uint(64),
            validUntil: g.uint(64),
            failureMode: g.uint(8),
        },
        action: {
            schemaVersion: g.uint(16),
            chainId: g.uint(256),
            vault: g.address(),
            actionNonce: g.uint(256),
            target: g.address(),
            valueWei: g.uint(256),
            dataHash: g.bytes32(),
            operation: g.uint(8),
            mandateHash: g.bytes32(),
            policyHash: g.bytes32(),
            deadline: g.uint(64),
        },
        receipt: {
            schemaVersion: g.uint(16),
            decisionId: g.bytes32(),
            actionHash: g.bytes32(),
            mandateHash: g.bytes32(),
            policyHash: g.bytes32(),
            verdict: g.uint(8),
            reasonCodesHash: g.bytes32(),
            evidenceHash: g.bytes32(),
            simulationBlockNumber: g.uint(256),
            simulationBlockHash: g.bytes32(),
            issuedAt: g.uint(64),
            expiresAt: g.uint(64),
            signer: g.address(),
        },
        override: {
            schemaVersion: g.uint(16),
            reviewReceiptHash: g.bytes32(),
            actionHash: g.bytes32(),
            mandateHash: g.bytes32(),
            policyHash: g.bytes32(),
            actionNonce: g.uint(256),
            reasonHash: g.bytes32(),
            issuedAt: g.uint(64),
            expiresAt: g.uint(64),
        },
        chainId: g.uint(256),
        vault: g.address(),
    };
}

// ---------------------------------------------------------------------------
// The differential
// ---------------------------------------------------------------------------

describe("TypeScript / Solidity EIP-712 differential", () => {
    const SEEDS = [1, 7, 1_337, 20_260_727, 0x7fffffff];

    for (const seed of SEEDS) {
        it(`agrees on every §5 payload hash (seed ${seed})`, async () => {
            const p = payloads(seed);

            assert.equal(await solidity("hashMandate", [p.mandate]), hashMandate(p.mandate), "mandate");
            assert.equal(await solidity("hashPolicy", [p.policy]), hashPolicy(p.policy), "policy");
            assert.equal(await solidity("hashAction", [p.action]), hashAction(p.action), "action");
            assert.equal(await solidity("hashReceipt", [p.receipt]), hashReceipt(p.receipt), "receipt");
            assert.equal(
                await solidity("hashOverride", [p.override]),
                hashOverride(p.override),
                "override",
            );
            assert.equal(
                await solidity("domainSeparator", [p.chainId, p.vault]),
                domainSeparator(p.chainId, p.vault),
                "domain separator",
            );
        });
    }

    it("agrees on boundary values that hide encoding bugs", async () => {
        // Zero and max in the same payload. Zero hides a wrong pad direction; max catches a
        // truncation that a mid-range value would not. A bytes4 selector at 0xffffffff and a
        // uint256 at 2^256-1 disagree loudly under a left/right padding swap.
        const mandate: MandatePayload = {
            schemaVersion: 0n,
            mandateId: `0x${"00".repeat(32)}`,
            principal: `0x${"00".repeat(20)}`,
            vault: `0x${"ff".repeat(20)}`,
            chainId: (1n << 256n) - 1n,
            target: `0x${"00".repeat(20)}`,
            targetCodeHash: `0x${"ff".repeat(32)}`,
            selector: "0xffffffff",
            maxNativeValueWei: (1n << 256n) - 1n,
            purposeKind: `0x${"00".repeat(32)}`,
            resourceId: `0x${"ff".repeat(32)}`,
            beneficiary: `0x${"ff".repeat(20)}`,
            durationSeconds: (1n << 64n) - 1n,
            recurringAllowed: true,
            validAfter: 0n,
            validUntil: (1n << 64n) - 1n,
            policyHash: `0x${"00".repeat(32)}`,
        };
        assert.equal(await solidity("hashMandate", [mandate]), hashMandate(mandate));

        // A one-byte selector difference must move the hash. If `bytes4` were left-padded
        // instead of left-aligned, both of these would still differ from each other — so the
        // check that matters is the equality against Solidity above, and this is the
        // sensitivity check that the field is bound at all.
        const shifted = {...mandate, selector: "0xfffffffe" as Hex};
        assert.notEqual(hashMandate(shifted), hashMandate(mandate));
        assert.equal(await solidity("hashMandate", [shifted]), hashMandate(shifted));
    });

    it("binds every field of the action payload", async () => {
        // Field-by-field sensitivity, mirroring `SentinelTypes.t.sol`'s mutation test on the
        // Solidity side. A field that could be changed without moving the hash would not be
        // bound by invariant §3.3(4), whatever the type string claims.
        const base = payloads(99).action;
        const mutations: Partial<ActionPayload>[] = [
            {schemaVersion: base.schemaVersion + 1n},
            {chainId: base.chainId + 1n},
            {vault: `0x${"01".repeat(20)}`},
            {actionNonce: base.actionNonce + 1n},
            {target: `0x${"02".repeat(20)}`},
            {valueWei: base.valueWei + 1n},
            {dataHash: keccak256(stringToBytes("different"))},
            {operation: (base.operation + 1n) % 256n},
            {mandateHash: keccak256(stringToBytes("other mandate"))},
            {policyHash: keccak256(stringToBytes("other policy"))},
            {deadline: base.deadline + 1n},
        ];
        assert.equal(mutations.length, 11, "one mutation per ActionPayload field");

        const baseline = hashAction(base);
        for (const [index, mutation] of mutations.entries()) {
            const mutated = {...base, ...mutation};
            assert.notEqual(hashAction(mutated), baseline, `field ${index} is not bound`);
            assert.equal(await solidity("hashAction", [mutated]), hashAction(mutated));
        }
    });
});
