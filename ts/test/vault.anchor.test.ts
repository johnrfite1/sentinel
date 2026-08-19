import {describe, it, before, after} from "node:test";
import assert from "node:assert/strict";
import {createServer, type Server} from "node:http";
import {
    encodeAbiParameters,
    keccak256,
    parseAbiParameters,
    stringToBytes,
    toFunctionSelector,
    toHex,
} from "viem";
import {
    ChainUnstableError,
    SNAPSHOT_ATTEMPTS,
    createChainReader,
    type VaultState,
} from "../src/signer/vault.ts";
import type {Hex} from "../src/signer/protocol.ts";

/**
 * The E3 repair (D-055(c)), falsified against the ARGUMENT rather than the demonstration.
 *
 * THE ARGUMENT, restated from `vault.ts`: every state and code value the signer reasons
 * about comes from ONE block, that block is named in the snapshot, and `attest.ts` requires
 * the receipt's anchor to be that block.
 *
 * WHY THE TESTS LOOK LIKE THIS. `docs/repair-protocol.md` step 3 requires the regression to
 * fail against a mutation that violates the general property BY A ROUTE THE REVIEWER DID NOT
 * USE. Round five's `E3` was demonstrated one way only: an ALLOW anchored to an old block.
 * A test that only replays that demonstration would pass against a repair that special-cased
 * old anchors while leaving the eleven reads straddling blocks — which is the half of the
 * defect nobody demonstrated, and the half `observedAtBlock` was silently wrong about.
 *
 * So this file attacks the READS, from below, through a recording RPC server: it asserts
 * that every `eth_call` and `eth_getCode` carried the SAME EXPLICIT block number. Deleting
 * `blockNumber: at` from any single read in `vault.ts` turns this file red without touching
 * the anchor comparison at all. The anchor comparison is falsified separately, end to end
 * against a real chain, in `signer.e2e.test.ts`.
 *
 * WHAT THIS FILE DOES NOT REACH: it exercises `createChainReader` against a scripted server,
 * so it proves what the reader ASKS FOR, not what a real node does with the request. That a
 * pinned `eth_call` genuinely returns historical state is the node's contract, not this
 * repository's, and it is not asserted here.
 */

const VAULT: Hex = "0x1111111111111111111111111111111111111111";
const TARGET: Hex = "0x2222222222222222222222222222222222222222";
const SELECTOR: Hex = "0xc188528b";

const ADDRESS_WORD = encodeAbiParameters(parseAbiParameters("address"), [
    "0x3333333333333333333333333333333333333333",
]);
const BYTES32_WORD = encodeAbiParameters(parseAbiParameters("bytes32"), [
    keccak256(stringToBytes("hash")),
]);
const UINT_WORD = encodeAbiParameters(parseAbiParameters("uint256"), [7n]);
const BOOL_WORD = encodeAbiParameters(parseAbiParameters("bool"), [true]);

/** Selector → canned return data, so `eth_call` answers whatever the reader asks for. */
const RETURNS: Record<string, Hex> = {
    [toFunctionSelector("owner() view returns (address)")]: ADDRESS_WORD,
    [toFunctionSelector("signer() view returns (address)")]: ADDRESS_WORD,
    [toFunctionSelector("activeMandateHash() view returns (bytes32)")]: BYTES32_WORD,
    [toFunctionSelector("activePolicyHash() view returns (bytes32)")]: BYTES32_WORD,
    [toFunctionSelector("actionNonce() view returns (uint256)")]: UINT_WORD,
    [toFunctionSelector("paused() view returns (bool)")]: BOOL_WORD,
    [toFunctionSelector("maxNativeValueWei() view returns (uint256)")]: UINT_WORD,
    [toFunctionSelector("allowedTarget(address) view returns (bool)")]: BOOL_WORD,
    [toFunctionSelector("allowedSelector(bytes4) view returns (bool)")]: BOOL_WORD,
    [toFunctionSelector("domainSeparator() view returns (bytes32)")]: BYTES32_WORD,
};

function blockAt(number: bigint, hash: Hex | null): Record<string, unknown> {
    return {
        number: toHex(number),
        hash,
        parentHash: keccak256(stringToBytes(`parent:${number}`)),
        nonce: "0x0000000000000000",
        sha3Uncles: keccak256(stringToBytes("uncles")),
        logsBloom: `0x${"00".repeat(256)}`,
        transactionsRoot: keccak256(stringToBytes("txroot")),
        stateRoot: keccak256(stringToBytes("stateroot")),
        receiptsRoot: keccak256(stringToBytes("receiptsroot")),
        miner: "0x0000000000000000000000000000000000000000",
        difficulty: "0x0",
        totalDifficulty: "0x0",
        extraData: "0x",
        size: "0x0",
        gasLimit: "0x1c9c380",
        gasUsed: "0x0",
        timestamp: toHex(1_800_000_000n),
        transactions: [],
        uncles: [],
        baseFeePerGas: "0x7",
    };
}

interface Recorded {
    method: string;
    /** The block tag the request carried, verbatim: a hex height, "latest", or absent. */
    blockTag: string | undefined;
}

interface MockNode {
    url: string;
    calls: Recorded[];
    stop(): Promise<void>;
}

/**
 * A JSON-RPC server that records the block tag of every request.
 *
 * `heads` is consumed one entry per `eth_getBlockByNumber("latest")`, which is how a test
 * scripts a head that moves underneath the reader. Running past the end repeats the last.
 */
async function mockNode(heads: {number: bigint; hash: Hex | null}[]): Promise<MockNode> {
    const calls: Recorded[] = [];
    let headIndex = 0;

    const server: Server = createServer((req, res) => {
        let body = "";
        req.on("data", (chunk) => (body += chunk));
        req.on("end", () => {
            const request = JSON.parse(body) as {
                id: number;
                method: string;
                params?: unknown[];
            };
            const params = request.params ?? [];
            let result: unknown = null;
            let blockTag: string | undefined;

            switch (request.method) {
                case "eth_chainId":
                    result = "0x7a69";
                    break;
                case "eth_getBlockByNumber": {
                    const requested = params[0] as string;
                    blockTag = requested;
                    if (requested === "latest") {
                        const head = heads[Math.min(headIndex, heads.length - 1)]!;
                        headIndex += 1;
                        result = blockAt(head.number, head.hash);
                    } else {
                        const n = BigInt(requested);
                        const known = heads.find((h) => h.number === n);
                        result = known === undefined ? null : blockAt(n, known.hash);
                    }
                    break;
                }
                case "eth_call": {
                    const call = params[0] as {data: Hex};
                    blockTag = params[1] as string;
                    result = RETURNS[call.data.slice(0, 10)] ?? "0x";
                    break;
                }
                case "eth_getCode":
                    blockTag = params[1] as string;
                    result = "0x6080";
                    break;
                default:
                    result = null;
            }

            calls.push({method: request.method, blockTag});
            res.writeHead(200, {"content-type": "application/json"});
            res.end(JSON.stringify({jsonrpc: "2.0", id: request.id, result}));
        });
    });

    await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
    const address = server.address();
    if (address === null || typeof address === "string") throw new Error("no port");

    return {
        url: `http://127.0.0.1:${address.port}`,
        calls,
        async stop() {
            await new Promise<void>((resolve) => server.close(() => resolve()));
        },
    };
}

/** Every read that must carry the pin: ten `eth_call`s plus the target's code. */
const PINNED_READS = 11;

describe("the signer reads one block, not eleven (D-055(c))", () => {
    let node: MockNode;
    let state: VaultState;
    const HEAD = {number: 4_242n, hash: keccak256(stringToBytes("head"))};

    before(async () => {
        node = await mockNode([HEAD]);
        state = await createChainReader(node.url).readVaultState(VAULT, TARGET, SELECTOR);
    });

    after(async () => {
        await node.stop();
    });

    it("pins EVERY state and code read to one explicit block height", () => {
        const pinned = node.calls.filter(
            (c) => c.method === "eth_call" || c.method === "eth_getCode",
        );
        assert.equal(
            pinned.length,
            PINNED_READS,
            "the reader should make exactly the eleven pinned reads",
        );

        const expected = toHex(HEAD.number);
        for (const call of pinned) {
            // The two failures this catches are different and both are the defect: a tag of
            // `undefined` or "latest" means the read floats, and a DIFFERENT height means the
            // snapshot straddles. Asserting equality to one literal height catches both.
            assert.equal(
                call.blockTag,
                expected,
                `${call.method} was sent with block tag ${String(call.blockTag)}, not ${expected}`,
            );
        }
    });

    it("reports the block it pinned to, with the hash from that same response", () => {
        assert.equal(state.observedAtBlock, HEAD.number);
        assert.equal(state.observedBlockHash, HEAD.hash);
    });

    it("re-confirms the head AFTER the reads, so a snapshot is never stale on return", () => {
        // Two "latest" lookups per successful attempt: the pin, then the confirmation. One
        // would mean the reader takes a pin and never checks it survived the reads.
        const latest = node.calls.filter(
            (c) => c.method === "eth_getBlockByNumber" && c.blockTag === "latest",
        );
        assert.equal(latest.length, 2);
    });
});

describe("a head that moves is retried, never accepted (D-055(c))", () => {
    it("discards the attempt and re-pins when the head advances mid-read", async () => {
        const first = {number: 10n, hash: keccak256(stringToBytes("ten"))};
        const second = {number: 11n, hash: keccak256(stringToBytes("eleven"))};
        // pin=10, confirm=11 (moved, discard), pin=11, confirm=11 (stable).
        const node = await mockNode([first, second, second, second]);
        try {
            const state = await createChainReader(node.url).readVaultState(
                VAULT,
                TARGET,
                SELECTOR,
            );
            assert.equal(state.observedAtBlock, 11n);
            assert.equal(state.observedBlockHash, second.hash);
            // Two attempts' worth of pinned reads, not one — the discarded attempt was
            // genuinely discarded rather than patched up.
            const pinned = node.calls.filter(
                (c) => c.method === "eth_call" || c.method === "eth_getCode",
            );
            assert.equal(pinned.length, PINNED_READS * 2);
        } finally {
            await node.stop();
        }
    });

    it("detects a SAME-HEIGHT reorg, which a height comparison alone would not", async () => {
        // The height never changes; only the hash does. A reader that compared numbers and
        // not hashes would return a snapshot taken on an orphaned block and call it current.
        const original = {number: 20n, hash: keccak256(stringToBytes("original"))};
        const reorged = {number: 20n, hash: keccak256(stringToBytes("reorged"))};
        const node = await mockNode([original, reorged, reorged, reorged]);
        try {
            const state = await createChainReader(node.url).readVaultState(
                VAULT,
                TARGET,
                SELECTOR,
            );
            assert.equal(state.observedBlockHash, reorged.hash);
        } finally {
            await node.stop();
        }
    });

    it("gives up rather than returning a stale pin when the head never settles", async () => {
        // A different head on every single lookup: no attempt can ever confirm.
        const heads = Array.from({length: SNAPSHOT_ATTEMPTS * 4}, (_, i) => ({
            number: BigInt(100 + i),
            hash: keccak256(stringToBytes(`moving:${i}`)),
        }));
        const node = await mockNode(heads);
        try {
            await assert.rejects(
                () => createChainReader(node.url).readVaultState(VAULT, TARGET, SELECTOR),
                (error: unknown) => error instanceof ChainUnstableError,
                "an unsettleable head must throw, not return the last pin taken",
            );
            const pinned = node.calls.filter(
                (c) => c.method === "eth_call" || c.method === "eth_getCode",
            );
            assert.equal(pinned.length, PINNED_READS * SNAPSHOT_ATTEMPTS);
        } finally {
            await node.stop();
        }
    });

    it("names the CONDITION it failed on, not a generic one (R2-F6)", async () => {
        // R2-F6, D-055(e), and the follow-up the D-057(5) verifier found: the error covers TWO
        // conditions and must say which. It was ALSO pinned by nothing — the verifier collapsed
        // both messages into one visibly-broken string and 526/526 stayed green, which is the
        // `F-VAULT-2` shape: correct today, protected tomorrow by nothing.
        //
        // (b) every observation was a PENDING head — nothing moved, there was simply never a
        // finalised head to anchor to.
        const pending = await mockNode(
            Array.from({length: SNAPSHOT_ATTEMPTS * 4}, () => ({number: 30n, hash: null})),
        );
        try {
            await createChainReader(pending.url).readVaultState(VAULT, TARGET, SELECTOR);
            assert.fail("expected ChainUnstableError");
        } catch (error) {
            assert.ok(error instanceof ChainUnstableError);
            assert.equal(error.pendingOnly, true);
            assert.match(error.message, /pending block with no hash/);
            assert.doesNotMatch(error.message, /head moved/,
                "a never-finalised head must NOT be reported as movement");
        } finally {
            await pending.stop();
        }

        // (a) the head genuinely MOVED under every pinned read.
        const moving = await mockNode(
            Array.from({length: SNAPSHOT_ATTEMPTS * 4}, (_, i) => ({
                number: BigInt(100 + i),
                hash: keccak256(stringToBytes(`moving:${i}`)),
            })),
        );
        try {
            await createChainReader(moving.url).readVaultState(VAULT, TARGET, SELECTOR);
            assert.fail("expected ChainUnstableError");
        } catch (error) {
            assert.ok(error instanceof ChainUnstableError);
            assert.equal(error.pendingOnly, false);
            assert.match(error.message, /head moved or was replaced/);
            assert.doesNotMatch(error.message, /pending block/,
                "a moving head must NOT be reported as a never-finalised one");
        } finally {
            await moving.stop();
        }
    });

    it("ABSENCE IS NOT AGREEMENT: a head with no hash produces no snapshot", async () => {
        // `docs/repair-protocol.md` step 4. A pending block has `hash: null`. The failure to
        // avoid is a snapshot returned with a null or undefined `observedBlockHash`, because
        // `attest.ts` compares the anchor to that field — and an anchor comparison against a
        // missing value is the "check that emits nothing" shape A-069 shipped.
        const node = await mockNode(
            Array.from({length: SNAPSHOT_ATTEMPTS * 4}, () => ({number: 30n, hash: null})),
        );
        try {
            await assert.rejects(
                () => createChainReader(node.url).readVaultState(VAULT, TARGET, SELECTOR),
                (error: unknown) => error instanceof ChainUnstableError,
            );
            // And it never even issued the reads: there is nothing to pin them to.
            assert.equal(
                node.calls.filter((c) => c.method === "eth_call").length,
                0,
                "a hashless head must be rejected BEFORE the state is read, not after",
            );
        } finally {
            await node.stop();
        }
    });
});
