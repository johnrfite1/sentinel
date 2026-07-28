import {describe, it} from "node:test";
import assert from "node:assert/strict";
import {encodeFunctionData, keccak256, stringToBytes} from "viem";
import {DECODE_FAILURES} from "../src/decode/abi.ts";
import {
    MAX_UINT256,
    SCHEMAS,
    assertSelectorAgreement,
    buildRegistry,
    decodeCall,
    describe as describeCall,
    isUnlimitedApproval,
} from "../src/decode/index.ts";
import type {Hex} from "../src/signer/protocol.ts";

/**
 * Unit tests for the two supported decoders (§9 step 4).
 *
 * The property under test is FAITHFULNESS TO BYTES: given calldata, the decoder produces
 * the parameters those bytes encode, or a named reason it cannot. No mandate, no policy, no
 * verdict — those belong to the conformance evaluator (§9 step 6), and mixing them in here
 * would make a decoding bug and an evaluation bug indistinguishable in the results.
 *
 * The strictness cases are the ones that matter. §4.2 Case 2 turns on Sentinel deriving
 * parameters from calldata rather than from the agent's description; that derivation is
 * only worth something if calldata which is *almost* well-formed is refused rather than
 * quietly normalised.
 */

const DEMO_PAY: Hex = "0x1111111111111111111111111111111111111111";
const DEMO_ERC20: Hex = "0x2222222222222222222222222222222222222222";
const OUTSIDER: Hex = "0x3333333333333333333333333333333333333333";
const BENEFICIARY: Hex = "0x4444444444444444444444444444444444444444";
const SPENDER: Hex = "0x5555555555555555555555555555555555555555";
const RESOURCE: Hex = keccak256(stringToBytes("weather-basic-24h"));

const REGISTRY = buildRegistry({[DEMO_PAY]: "DemoPay", [DEMO_ERC20]: "DemoERC20"});

const PURCHASE_ABI = [
    {
        type: "function",
        name: "purchase",
        stateMutability: "payable",
        inputs: [
            {type: "bytes32", name: "resourceId"},
            {type: "address", name: "beneficiary"},
            {type: "uint64", name: "durationSeconds"},
            {type: "bool", name: "recurring"},
        ],
        outputs: [],
    },
] as const;

const APPROVE_ABI = [
    {
        type: "function",
        name: "approve",
        stateMutability: "nonpayable",
        inputs: [
            {type: "address", name: "spender"},
            {type: "uint256", name: "amount"},
        ],
        outputs: [{type: "bool"}],
    },
] as const;

function purchaseCalldata(
    args: [Hex, Hex, bigint, boolean] = [RESOURCE, BENEFICIARY, 86_400n, false],
): Hex {
    return encodeFunctionData({abi: PURCHASE_ABI, functionName: "purchase", args}) as Hex;
}

function approveCalldata(args: [Hex, bigint] = [SPENDER, 1_000n]): Hex {
    return encodeFunctionData({abi: APPROVE_ABI, functionName: "approve", args}) as Hex;
}

/** Replace one 32-byte argument word, to build calldata a well-behaved encoder will not. */
function withWord(callData: Hex, index: number, word: string): Hex {
    assert.equal(word.length, 64, "a word is 64 hex digits");
    const head = callData.slice(0, 10);
    const body = callData.slice(10);
    return `${head}${body.slice(0, index * 64)}${word}${body.slice((index + 1) * 64)}` as Hex;
}

describe("selector agreement", () => {
    it("each pinned selector is keccak of its transcribed signature", () => {
        assert.doesNotThrow(assertSelectorAgreement);
        assert.equal(SCHEMAS["DemoPay.purchase"].selector, "0xc188528b");
        assert.equal(SCHEMAS["DemoERC20.approve"].selector, "0x095ea7b3");
    });

    it("declares exactly the two schemas §4 scopes", () => {
        // §4: "Two decoded top-level call schemas". A third arriving without a decision is
        // a scope addition, which house rule 7 routes through John.
        assert.deepEqual(Object.keys(SCHEMAS).sort(), ["DemoERC20.approve", "DemoPay.purchase"]);
    });
});

describe("decoding a well-formed call", () => {
    it("recovers DemoPay.purchase parameters exactly", () => {
        const result = decodeCall({
            target: DEMO_PAY,
            callData: purchaseCalldata([RESOURCE, BENEFICIARY, 86_400n, true]),
            registry: REGISTRY,
        });
        assert.equal(result.ok, true);
        assert.deepEqual(result.decoded, {
            schema: "DemoPay.purchase",
            resourceId: RESOURCE,
            beneficiary: BENEFICIARY.toLowerCase(),
            durationSeconds: 86_400n,
            recurring: true,
        });
    });

    it("recovers DemoERC20.approve parameters exactly, including max uint256", () => {
        // The Case 2 injection produced precisely this: the attacker as spender, unlimited
        // allowance (A-009).
        const result = decodeCall({
            target: DEMO_ERC20,
            callData: approveCalldata([SPENDER, MAX_UINT256]),
            registry: REGISTRY,
        });
        assert.equal(result.ok, true);
        assert.deepEqual(result.decoded, {
            schema: "DemoERC20.approve",
            spender: SPENDER.toLowerCase(),
            amount: MAX_UINT256,
        });
        assert.equal(isUnlimitedApproval((result.decoded as {amount: bigint}).amount), true);
        assert.equal(isUnlimitedApproval(MAX_UINT256 - 1n), false);
    });

    it("is case-insensitive about the target address", () => {
        const result = decodeCall({
            target: DEMO_PAY.toUpperCase().replace("0X", "0x") as Hex,
            callData: purchaseCalldata(),
            registry: REGISTRY,
        });
        assert.equal(result.ok, true);
    });

    it("renders a description for the evidence bundle without using it for comparison", () => {
        const result = decodeCall({target: DEMO_PAY, callData: purchaseCalldata(), registry: REGISTRY});
        assert.equal(result.ok, true);
        const text = describeCall(result.decoded);
        assert.match(text, /^DemoPay\.purchase\(resource=0x/);
        assert.match(text, /recurring=false\)$/);
    });
});

const cases: {name: string; code: string; target: Hex; callData: Hex}[] = [
    {
        name: "no selector at all",
        code: "DECODE_NO_SELECTOR",
        target: DEMO_PAY,
        callData: "0x12",
    },
    {
        name: "a selector nobody supports",
        code: "DECODE_UNKNOWN_SELECTOR",
        target: DEMO_PAY,
        callData: `0xdeadbeef${"00".repeat(32)}` as Hex,
    },
    {
        name: "a supported selector at an unregistered target",
        code: "DECODE_UNSUPPORTED_TARGET",
        target: OUTSIDER,
        callData: purchaseCalldata(),
    },
    {
        // Not a purchase: it is a call to whatever DemoERC20 has at that selector, which
        // is nothing. Decoding parameters here would describe a call that cannot happen.
        name: "purchase aimed at DemoERC20",
        code: "DECODE_SELECTOR_TARGET_MISMATCH",
        target: DEMO_ERC20,
        callData: purchaseCalldata(),
    },
    {
        name: "approve aimed at DemoPay",
        code: "DECODE_SELECTOR_TARGET_MISMATCH",
        target: DEMO_PAY,
        callData: approveCalldata(),
    },
    {
        // The EVM ignores these bytes. Sentinel must not: they are part of what was
        // proposed, and dataHash binds them.
        name: "trailing bytes past the declared arguments",
        code: "DECODE_LENGTH_MISMATCH",
        target: DEMO_PAY,
        callData: `${purchaseCalldata()}${"ff".repeat(32)}` as Hex,
    },
    {
        name: "an argument word short",
        code: "DECODE_LENGTH_MISMATCH",
        target: DEMO_PAY,
        callData: purchaseCalldata().slice(0, -64) as Hex,
    },
    {
        // Two addresses sharing low bytes and differing above them would otherwise be one
        // beneficiary to Sentinel — and beneficiary is a mandate-constrained field.
        name: "beneficiary word with dirty high bytes",
        code: "DECODE_DIRTY_ADDRESS_BITS",
        target: DEMO_PAY,
        callData: withWord(purchaseCalldata(), 1, `ff${"00".repeat(11)}${BENEFICIARY.slice(2)}`),
    },
    {
        name: "spender word with dirty high bytes",
        code: "DECODE_DIRTY_ADDRESS_BITS",
        target: DEMO_ERC20,
        callData: withWord(approveCalldata(), 0, `01${"00".repeat(11)}${SPENDER.slice(2)}`),
    },
    {
        // recurringAllowed is a mandate field and a bound effect. "Any non-zero is true"
        // would make 2 and 1 the same proposal while being different bytes on the wire.
        name: "recurring encoded as 2",
        code: "DECODE_NON_CANONICAL_BOOL",
        target: DEMO_PAY,
        callData: withWord(purchaseCalldata(), 3, `${"00".repeat(31)}02`),
    },
    {
        name: "duration overflowing uint64",
        code: "DECODE_UINT_OVERFLOW",
        target: DEMO_PAY,
        callData: withWord(purchaseCalldata(), 2, `${"00".repeat(23)}${"ff".repeat(9)}`),
    },
];

describe("refusals — the cases that make derivation worth doing", () => {
    for (const c of cases) {
        it(`refuses ${c.name} with ${c.code}`, () => {
            const result = decodeCall({target: c.target, callData: c.callData, registry: REGISTRY});
            assert.equal(result.ok, false, `${c.name} should not decode`);
            assert.equal(result.code, c.code);
        });
    }

    it("never returns partial parameters alongside a failure", () => {
        // A caller must not be able to read "half a decode". §3.3(8): undecodable calldata
        // never produces an automatic allow, and the cheapest way to guarantee that is for
        // there to be no decoded value in existence to be misread.
        const result = decodeCall({
            target: DEMO_PAY,
            callData: withWord(purchaseCalldata(), 3, `${"00".repeat(31)}02`),
            registry: REGISTRY,
        });
        assert.equal(result.ok, false);
        assert.equal("decoded" in result, false);
    });
});

describe("the refusal table is exhaustive", () => {
    it("has a case for every declared decode-failure code", () => {
        // The structural guard, added here from the outset rather than after the fact.
        // In step 3 the equivalent check was missing and 22 of 31 reason codes turned out to
        // be exercised by nothing — a hole mutation testing could not reveal, because the
        // mutations were written from the same reading of the code as the tests. A new
        // failure code without a case fails this test rather than joining them.
        const declared = Object.keys(DECODE_FAILURES).sort();
        const tested = [...new Set(cases.map((c) => c.code))].sort();
        assert.deepEqual(
            declared.filter((c) => !tested.includes(c)),
            [],
            "decode-failure codes declared but never triggered by any test",
        );
        assert.deepEqual(
            tested.filter((c) => !declared.includes(c)),
            [],
            "tests reference decode-failure codes that no longer exist",
        );
    });
});

describe("boundary values decode rather than being rejected", () => {
    // Strictness must not shade into refusing legitimate extremes — a decoder that rejects
    // valid maxima manufactures reviews and teaches its operators to ignore them.
    it("accepts a zero-valued but well-formed purchase", () => {
        const result = decodeCall({
            target: DEMO_PAY,
            callData: purchaseCalldata([`0x${"00".repeat(32)}`, `0x${"00".repeat(20)}`, 0n, false]),
            registry: REGISTRY,
        });
        assert.equal(result.ok, true);
        assert.equal((result.decoded as {durationSeconds: bigint}).durationSeconds, 0n);
    });

    it("accepts uint64 at its maximum", () => {
        const max = (1n << 64n) - 1n;
        const result = decodeCall({
            target: DEMO_PAY,
            callData: purchaseCalldata([RESOURCE, BENEFICIARY, max, true]),
            registry: REGISTRY,
        });
        assert.equal(result.ok, true);
        assert.equal((result.decoded as {durationSeconds: bigint}).durationSeconds, max);
    });
});
