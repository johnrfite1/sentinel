import {describe, it} from "node:test";
import assert from "node:assert/strict";
import {keccak256, recoverAddress, stringToBytes} from "viem";
import {privateKeyToAccount} from "viem/accounts";
import * as keystoreModule from "../src/signer/keystore.ts";
import {createKeystore} from "../src/signer/keystore.ts";
import {digest, domainSeparator, hashReceipt} from "../src/signer/eip712.ts";
import type {DecisionReceiptPayload, Hex} from "../src/signer/protocol.ts";
import {SIGNER, SIGNER_KEY} from "./harness.ts";

/**
 * Direct tests of the keystore's own guards.
 *
 * WHY THESE ARE NEEDED, AND WHY THEY IMPORT WHAT THE END-TO-END TESTS DELIBERATELY DO NOT.
 * The end-to-end suite reaches the signer only over its socket, because A-005's claim is
 * about process isolation and a claim about process boundaries cannot be tested by
 * importing a module. But that discipline left a real hole: `signReceipt` refuses to sign a
 * receipt naming a different signer, and the attestor always sets `signer` to the
 * keystore's own address — so the guard is unreachable through the socket and no
 * end-to-end test can ever observe it.
 *
 * This was found by mutation testing, not by reading: deleting the check left the whole
 * suite green. An assertion no test can observe is indistinguishable from an absent one,
 * which is precisely what AGENTS.md's test-coverage discipline warns about. These tests
 * exercise the guard directly. They make no claim about isolation and should not be read
 * as one.
 */

const VAULT: Hex = "0x1111111111111111111111111111111111111111";
const CHAIN_ID = 31337n;

function receipt(overrides: Partial<DecisionReceiptPayload> = {}): DecisionReceiptPayload {
    return {
        schemaVersion: 1n,
        decisionId: keccak256(stringToBytes("decision")),
        actionHash: keccak256(stringToBytes("action")),
        mandateHash: keccak256(stringToBytes("mandate")),
        policyHash: keccak256(stringToBytes("policy")),
        verdict: 2n,
        reasonCodesHash: keccak256(stringToBytes("")),
        evidenceHash: keccak256(stringToBytes("{}")),
        simulationBlockNumber: 100n,
        simulationBlockHash: keccak256(stringToBytes("block")),
        issuedAt: 1_000_000n,
        expiresAt: 1_000_300n,
        signer: SIGNER.address.toLowerCase() as Hex,
        ...overrides,
    };
}

describe("keystore", () => {
    it("signs a receipt that recovers to its own address", async () => {
        const keystore = createKeystore({chainId: CHAIN_ID, vault: VAULT, privateKey: SIGNER_KEY});
        const r = receipt();
        const signature = await keystore.signReceipt(r);

        const recovered = await recoverAddress({
            hash: digest(domainSeparator(CHAIN_ID, VAULT), hashReceipt(r)),
            signature,
        });
        assert.equal(recovered.toLowerCase(), keystore.address);
    });

    it("refuses to sign a receipt that names a different signer", async () => {
        // The guard mutation testing found untested. Such a receipt would recover to THIS
        // key while claiming another — dead onchain, because SentinelVault checks both the
        // named signer and the recovered one, but a false statement in an evidence bundle.
        const keystore = createKeystore({chainId: CHAIN_ID, vault: VAULT, privateKey: SIGNER_KEY});
        await assert.rejects(
            () => keystore.signReceipt(receipt({signer: "0x9999999999999999999999999999999999999999"})),
            /names a different signer/,
        );
    });

    it("binds the domain at construction, so one keystore cannot sign for another vault", async () => {
        // A per-call domain would let a caller retarget a signature at a different vault or
        // chain — the exact substitution EIP-712 domain separation exists to prevent.
        const a = createKeystore({chainId: CHAIN_ID, vault: VAULT, privateKey: SIGNER_KEY});
        const b = createKeystore({
            chainId: CHAIN_ID,
            vault: "0x2222222222222222222222222222222222222222",
            privateKey: SIGNER_KEY,
        });
        const r = receipt();
        assert.notEqual(await a.signReceipt(r), await b.signReceipt(r));
    });

    it("exposes no way to sign arbitrary bytes", async () => {
        // §3.1: "The signer exposes no generic sign-bytes method." The RPC surface is
        // checked in the end-to-end suite; this checks the in-process surface, so the
        // narrowness cannot be bypassed by an import rather than a socket.
        const keystore = createKeystore({chainId: CHAIN_ID, vault: VAULT, privateKey: SIGNER_KEY});
        assert.deepEqual(Object.keys(keystore).sort(), ["address", "describe", "signReceipt"]);

        for (const name of ["sign", "signMessage", "signTypedData", "signHash", "signBytes"]) {
            assert.equal(
                (keystore as unknown as Record<string, unknown>)[name],
                undefined,
                `keystore must not expose ${name}`,
            );
        }
        assert.deepEqual(Object.keys(keystoreModule).sort(), ["createKeystore"]);
    });

    it("never reveals the private key, including through describe() or errors", () => {
        const keystore = createKeystore({chainId: CHAIN_ID, vault: VAULT, privateKey: SIGNER_KEY});
        const described = JSON.stringify(keystore.describe());
        assert.ok(!described.includes(SIGNER_KEY.slice(2)), "describe() leaked the key");
        assert.deepEqual(Object.keys(keystore.describe()).sort(), ["address", "source"]);

        // A malformed key is still a secret. Error strings travel further than the code
        // that produced them — into logs, tickets, and issue trackers.
        const malformed = "0xnotakeybutdefinitelysecret";
        try {
            createKeystore({chainId: CHAIN_ID, vault: VAULT, privateKey: malformed as Hex});
            assert.fail("expected a malformed key to be rejected");
        } catch (err) {
            const message = (err as Error).message;
            assert.match(message, /32-byte hex private key/);
            assert.ok(!message.includes("notakeybut"), "the error echoed the key material");
        }
    });

    it("generates an ephemeral key when none is supplied", () => {
        const previous = process.env.SENTINEL_SIGNER_KEY;
        delete process.env.SENTINEL_SIGNER_KEY;
        try {
            const a = createKeystore({chainId: CHAIN_ID, vault: VAULT});
            const b = createKeystore({chainId: CHAIN_ID, vault: VAULT});
            assert.equal(a.describe().source, "ephemeral");
            assert.notEqual(a.address, b.address, "each boot must produce a distinct key");
            assert.match(a.address, /^0x[0-9a-f]{40}$/);
        } finally {
            if (previous !== undefined) process.env.SENTINEL_SIGNER_KEY = previous;
        }
    });

    it("reports the key source honestly", () => {
        const previous = process.env.SENTINEL_SIGNER_KEY;
        process.env.SENTINEL_SIGNER_KEY = SIGNER_KEY;
        try {
            const fromEnv = createKeystore({chainId: CHAIN_ID, vault: VAULT});
            assert.equal(fromEnv.describe().source, "env");
            assert.equal(fromEnv.address, privateKeyToAccount(SIGNER_KEY).address.toLowerCase());

            const injected = createKeystore({chainId: CHAIN_ID, vault: VAULT, privateKey: SIGNER_KEY});
            assert.equal(injected.describe().source, "injected");
        } finally {
            if (previous === undefined) delete process.env.SENTINEL_SIGNER_KEY;
            else process.env.SENTINEL_SIGNER_KEY = previous;
        }
    });
});
