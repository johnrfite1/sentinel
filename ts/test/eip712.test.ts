import {describe, it} from "node:test";
import assert from "node:assert/strict";
import {
    ACTION_TYPE,
    GOLDEN_TYPEHASHES,
    MANDATE_TYPE,
    OVERRIDE_TYPE,
    POLICY_TYPE,
    RECEIPT_TYPE,
    assertSchemaAgreement,
    domainSeparator,
} from "../src/signer/eip712.ts";
import {
    REASON_SEVERITY,
    canonicalReasonCodes,
    parseAction,
    parseEvaluateAndSignRequest,
    refusesVerdict,
    type ReasonCode,
} from "../src/signer/protocol.ts";

/**
 * Unit tests for the parts of the signer that need no chain.
 *
 * The end-to-end suite proves the signer's output is accepted by the real vault. These
 * prove the things a green end-to-end run would NOT notice: that the schema check can
 * actually fail, that the severity table is complete, and that the RPC's parser rejects
 * what it claims to reject. A passing happy path says nothing about any of those.
 */

describe("EIP-712 schema agreement", () => {
    it("agrees with the pinned Solidity golden typehashes", () => {
        assert.doesNotThrow(assertSchemaAgreement);
    });

    it("has exactly the §5 field order in each type string", () => {
        // Transcribed independently from §5 of the proposal. If a type string above is
        // edited, this fails as well as the golden-hash check — two failures pointing at one
        // cause is the intent, because a single failing assertion invites a repin.
        assert.match(MANDATE_TYPE, /^MandatePayload\(uint16 schemaVersion,bytes32 mandateId,/);
        assert.match(POLICY_TYPE, /^PolicyPayload\(uint16 schemaVersion,uint32 policyVersion,/);
        assert.match(ACTION_TYPE, /^ActionPayload\(uint16 schemaVersion,uint256 chainId,/);
        assert.match(RECEIPT_TYPE, /^DecisionReceiptPayload\(uint16 schemaVersion,bytes32 decisionId,/);
        assert.match(
            OVERRIDE_TYPE,
            /^OverrideAuthorizationPayload\(uint16 schemaVersion,bytes32 reviewReceiptHash,/,
        );
        assert.equal(Object.keys(GOLDEN_TYPEHASHES).length, 6);
    });

    it("binds the domain separator to both chain and vault", () => {
        const a = domainSeparator(31337n, "0x1111111111111111111111111111111111111111");
        const b = domainSeparator(1n, "0x1111111111111111111111111111111111111111");
        const c = domainSeparator(31337n, "0x2222222222222222222222222222222222222222");
        assert.notEqual(a, b, "chainId must change the domain");
        assert.notEqual(a, c, "vault must change the domain");
    });
});

describe("reason-code severity", () => {
    it("classifies every declared reason code", () => {
        for (const [code, severity] of Object.entries(REASON_SEVERITY)) {
            assert.ok(
                ["FATAL", "EXECUTABILITY", "CONFORMANCE"].includes(severity),
                `${code} has an unrecognised severity`,
            );
        }
    });

    it("never lets a finding permit an ALLOW it would otherwise block", () => {
        // The asymmetry the tiers exist to guarantee: whatever a finding does to REVIEW or
        // BLOCK, it must be at least as restrictive for ALLOW. A tier that violated this
        // would be a path by which a failed check made an automatic allow *more* likely.
        for (const code of Object.keys(REASON_SEVERITY) as ReasonCode[]) {
            const blocksAllow = refusesVerdict([code], "ALLOW");
            assert.ok(
                blocksAllow,
                `${code} does not block ALLOW; every signer finding must, by construction`,
            );
        }
    });

    it("permits REVIEW on conformance findings so Case 4 stays reachable", () => {
        // §4.2 Case 4 expects a REVIEW receipt when the target code hash changed. A signer
        // that refused here would make the spec's own demonstration case unreachable.
        assert.equal(refusesVerdict(["SIGNER_TARGET_CODEHASH_MISMATCH"], "REVIEW"), false);
        assert.equal(refusesVerdict(["SIGNER_TARGET_CODEHASH_MISMATCH"], "ALLOW"), true);
    });

    it("refuses every verdict on a fatal finding", () => {
        for (const verdict of ["ALLOW", "REVIEW", "BLOCK"] as const) {
            assert.equal(refusesVerdict(["SIGNER_DATAHASH_MISMATCH"], verdict), true);
        }
    });

    it("permits BLOCK on an executability finding", () => {
        assert.equal(refusesVerdict(["SIGNER_NONCE_MISMATCH"], "BLOCK"), false);
        assert.equal(refusesVerdict(["SIGNER_NONCE_MISMATCH"], "REVIEW"), true);
        assert.equal(refusesVerdict(["SIGNER_NONCE_MISMATCH"], "ALLOW"), true);
    });
});

describe("canonical reason codes", () => {
    it("is order- and multiplicity-independent", () => {
        // The D-010 verifier reimplements this in another language from the written rule.
        // Every degree of freedom left here is a place two implementations disagree while
        // both believe they are right.
        assert.equal(canonicalReasonCodes(["B", "A"]), canonicalReasonCodes(["A", "B"]));
        assert.equal(canonicalReasonCodes(["A", "A", "B"]), canonicalReasonCodes(["A", "B"]));
        assert.equal(canonicalReasonCodes([]), "");
        assert.equal(canonicalReasonCodes(["A", "B"]), "A\nB");
    });
});

describe("RPC input parsing", () => {
    const action = {
        schemaVersion: "1",
        chainId: "31337",
        vault: "0x1111111111111111111111111111111111111111",
        actionNonce: "0",
        target: "0x2222222222222222222222222222222222222222",
        valueWei: "1000",
        dataHash: `0x${"11".repeat(32)}`,
        operation: "0",
        mandateHash: `0x${"22".repeat(32)}`,
        policyHash: `0x${"33".repeat(32)}`,
        deadline: "4000000000",
    };

    it("accepts a well-formed action", () => {
        const parsed = parseAction(action);
        assert.equal(parsed.chainId, 31337n);
        assert.equal(parsed.valueWei, 1000n);
    });

    it("rejects an unknown field rather than ignoring it", () => {
        // A silently dropped field is how one payload comes to mean two things: the caller
        // believes it constrained something the signer never saw.
        assert.throws(() => parseAction({...action, surprise: "1"}), /unexpected field/);
    });

    it("rejects hex where a decimal integer is required", () => {
        assert.throws(() => parseAction({...action, valueWei: "0x10"}), /unsigned decimal/);
    });

    it("rejects a negative value", () => {
        assert.throws(() => parseAction({...action, valueWei: "-1"}), /unsigned decimal/);
    });

    it("rejects a number where a decimal string is required", () => {
        // JSON numbers cannot carry a uint256. Accepting one would silently truncate a
        // value in a security payload.
        assert.throws(() => parseAction({...action, valueWei: 1000}), /unsigned decimal/);
    });

    it("rejects an out-of-range uint64", () => {
        assert.throws(() => parseAction({...action, deadline: (2n ** 64n).toString()}), /uint64/);
    });

    it("rejects a wrong-length bytes32", () => {
        assert.throws(() => parseAction({...action, dataHash: "0x1234"}), /32 bytes/);
    });

    it("rejects an unrecognised verdict", () => {
        assert.throws(
            () =>
                parseEvaluateAndSignRequest({
                    action,
                    callData: "0xdeadbeef",
                    mandate: {},
                    policy: {},
                    evaluation: {
                        verdict: "PROBABLY_FINE",
                        reasonCodes: [],
                        evidenceCanonical: "{}",
                        simulationBlockNumber: "1",
                        simulationBlockHash: `0x${"00".repeat(32)}`,
                    },
                }),
            /ALLOW, REVIEW, BLOCK/,
        );
    });
});
