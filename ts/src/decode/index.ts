import {keccak256, stringToBytes} from "viem";
import type {Hex} from "../signer/protocol.ts";
import {DecodeError, WordReader, selectorOf, type DecodeFailureCode} from "./abi.ts";

/**
 * The two supported call decoders (§9 step 4, §4).
 *
 * §4 fixes the scope at "two decoded top-level call schemas: DemoPay purchase and
 * DemoERC20 approve", and §5.7 names what the decoded parameters are for: "DemoPay
 * resource, beneficiary, duration, and recurrence" and "DemoERC20 approval parameters and
 * allowance ceiling". Everything else is `DECODE_UNKNOWN_SELECTOR` — not a best guess, not
 * a generic ABI walk. A lab that claims to check two schemas should be unable to pretend it
 * checked a third.
 *
 * WHAT THIS LAYER DOES AND DOES NOT DECIDE. It turns bytes into typed parameters, or it
 * fails with a named reason. It renders no verdict, consults no mandate, and knows nothing
 * about policy — comparing decoded parameters against the signed mandate is the conformance
 * evaluator's job (§9 step 6). Keeping the split means the decoder can be tested for
 * FAITHFULNESS TO BYTES alone, which is the one property it must never get wrong, and the
 * evaluator can be tested against the labelled corpus without a decoding bug polluting it.
 *
 * TARGET BINDING IS PART OF DECODING. A `purchase` selector aimed at DemoERC20 is not a
 * purchase; it is a call to whatever DemoERC20 happens to have at that selector, which is
 * nothing. §3.3(11) makes unsupported top-level operations deny-or-review by default, so
 * the decoder is told which contract lives at which address and refuses the mismatch rather
 * than decoding parameters that describe a call that cannot happen.
 */

// ---------------------------------------------------------------------------
// Schemas
// ---------------------------------------------------------------------------

/**
 * Signatures beside their selectors, and the pair checked at import time.
 *
 * The same technique as the EIP-712 golden typehashes, for the same reason: a signature
 * string transcribed from the contract, and a selector taken from `cast sig`, agreeing is
 * evidence. Either alone proves only that nobody edited one number. A selector is four
 * bytes, and getting one wrong routes a call to the wrong decoder — which is a
 * conformance failure that looks like a parameter bug.
 */
export const SCHEMAS = {
    "DemoPay.purchase": {
        contract: "DemoPay",
        signature: "purchase(bytes32,address,uint64,bool)",
        selector: "0xc188528b",
        words: 4,
    },
    "DemoERC20.approve": {
        contract: "DemoERC20",
        signature: "approve(address,uint256)",
        selector: "0x095ea7b3",
        words: 2,
    },
} as const;

export type SchemaName = keyof typeof SCHEMAS;
export type SupportedContract = (typeof SCHEMAS)[SchemaName]["contract"];

export function assertSelectorAgreement(): void {
    for (const [name, schema] of Object.entries(SCHEMAS)) {
        const computed = keccak256(stringToBytes(schema.signature)).slice(0, 10);
        if (computed !== schema.selector) {
            throw new Error(
                `selector drift in ${name}: keccak256("${schema.signature}")[0..4] is ${computed}, ` +
                    `the pinned value is ${schema.selector}. A wrong selector routes calls to the ` +
                    `wrong decoder — resolve it deliberately, do not repin.`,
            );
        }
    }
}

assertSelectorAgreement();

// ---------------------------------------------------------------------------
// Decoded shapes
// ---------------------------------------------------------------------------

/** §4.1 / §5.7: resource, beneficiary, duration, recurrence — the mandate-constrained set. */
export interface DemoPayPurchase {
    schema: "DemoPay.purchase";
    resourceId: Hex;
    beneficiary: Hex;
    durationSeconds: bigint;
    recurring: boolean;
}

/** §5.7: approval parameters, against which an allowance ceiling is checked. */
export interface DemoErc20Approve {
    schema: "DemoERC20.approve";
    spender: Hex;
    amount: bigint;
}

export type DecodedCall = DemoPayPurchase | DemoErc20Approve;

export type DecodeResult =
    | {ok: true; selector: Hex; decoded: DecodedCall}
    | {ok: false; selector: Hex | null; code: DecodeFailureCode; detail: string};

/** address → which supported contract is deployed there. Built once per environment. */
export type TargetRegistry = ReadonlyMap<Hex, SupportedContract>;

export function buildRegistry(entries: Record<string, SupportedContract>): TargetRegistry {
    return new Map(
        Object.entries(entries).map(([address, contract]) => [address.toLowerCase() as Hex, contract]),
    );
}

// ---------------------------------------------------------------------------
// Decoding
// ---------------------------------------------------------------------------

/**
 * Decode one top-level call, or say precisely why it cannot be decoded.
 *
 * Returns a result rather than throwing. The caller is a conformance evaluator that must
 * record *why* a call was undecodable — "malformed calldata or unknown selector" is a
 * fixture class in §7.1 with its own expected verdict, so the reason is evidence, not an
 * error to swallow.
 */
export function decodeCall(args: {
    target: Hex;
    callData: Hex;
    registry: TargetRegistry;
}): DecodeResult {
    const target = args.target.toLowerCase() as Hex;
    let selector: Hex | null = null;

    try {
        selector = selectorOf(args.callData);

        const contract = args.registry.get(target);
        if (contract === undefined) {
            throw new DecodeError("DECODE_UNSUPPORTED_TARGET", target);
        }

        const entry = Object.entries(SCHEMAS).find(([, s]) => s.selector === selector);
        if (entry === undefined) {
            throw new DecodeError("DECODE_UNKNOWN_SELECTOR", selector);
        }
        const [name, schema] = entry as [SchemaName, (typeof SCHEMAS)[SchemaName]];

        if (schema.contract !== contract) {
            throw new DecodeError(
                "DECODE_SELECTOR_TARGET_MISMATCH",
                `${schema.signature} is ${schema.contract}'s, but ${target} is ${contract}`,
            );
        }

        const reader = WordReader.forSchema(args.callData, schema.words);

        // Field order is the schema. Read positionally against the signature above; the
        // selector already committed to that ordering, so a mismatch here would be a decoder
        // that disagrees with the four bytes it just matched.
        const decoded: DecodedCall =
            name === "DemoPay.purchase"
                ? {
                      schema: "DemoPay.purchase",
                      resourceId: reader.bytes32(0),
                      beneficiary: reader.address(1),
                      durationSeconds: reader.uint(2, 64),
                      recurring: reader.boolean(3),
                  }
                : {
                      schema: "DemoERC20.approve",
                      spender: reader.address(0),
                      amount: reader.uint(1, 256),
                  };

        return {ok: true, selector, decoded};
    } catch (err) {
        if (err instanceof DecodeError) {
            return {ok: false, selector, code: err.code, detail: err.message};
        }
        throw err;
    }
}

/**
 * Decode parameters from calldata using the SELECTOR ALONE, with no target binding.
 *
 * Exists for D-014: the isolated signer independently decodes the calldata and verifies that
 * the parameters recorded in the evidence bundle match what the bytes actually say. That is
 * *derivation without judgement* — the signer never consults the mandate — and it makes the
 * bundle's decoded parameters signer-attested rather than evaluator-asserted, so a
 * wrong-purpose ALLOW becomes detectable after the fact by the D-010 verifier.
 *
 * "DETECTABLE BY THE D-010 VERIFIER" IS NOT YET TRUE OF THE WHOLE BUNDLE (A-068, from round
 * five's E4, adjudicated and confirmed). What the signer binds is the PARAMETERS. The §5.6
 * bundle also carries `normalizedAction` and `expectedEffects`. The D-010 verifier compares
 * those fields to the presented action and mandate (`_evidence_describes_the_bundle`). The
 * signer still does not.
 *
 * Whether the SIGNER should compare them is a D-014 question and not an agent's to answer:
 * D-014 deliberately kept conformance out of the signer. Register E4 is VERIFIER HALF BUILT
 * · SIGNER HALF DELIBERATELY NOT BUILT, not an open defect.
 *
 * BOUNDARY, STATED PRECISELY BECAUSE D-014 STATES IT PRECISELY: this checks that the
 * parameters match the bytes *given the selector*. It does NOT check that the selector
 * belongs at that target — that is `decodeCall`, and it remains the evaluator's job. A signer
 * using this function must not be described as validating the call, only its parameters.
 *
 * Deliberately a separate entry point rather than an option on `decodeCall`: a boolean flag
 * that silently disables target binding is exactly the kind of thing a later caller sets
 * without reading why.
 */
export function decodeBySelector(callData: Hex): DecodeResult {
    let selector: Hex | null = null;
    try {
        selector = selectorOf(callData);
        const entry = Object.entries(SCHEMAS).find(([, s]) => s.selector === selector);
        if (entry === undefined) throw new DecodeError("DECODE_UNKNOWN_SELECTOR", selector);
        const [name, schema] = entry as [SchemaName, (typeof SCHEMAS)[SchemaName]];
        const reader = WordReader.forSchema(callData, schema.words);

        const decoded: DecodedCall =
            name === "DemoPay.purchase"
                ? {
                      schema: "DemoPay.purchase",
                      resourceId: reader.bytes32(0),
                      beneficiary: reader.address(1),
                      durationSeconds: reader.uint(2, 64),
                      recurring: reader.boolean(3),
                  }
                : {
                      schema: "DemoERC20.approve",
                      spender: reader.address(0),
                      amount: reader.uint(1, 256),
                  };

        return {ok: true, selector, decoded};
    } catch (err) {
        if (err instanceof DecodeError) {
            return {ok: false, selector, code: err.code, detail: err.message};
        }
        throw err;
    }
}

/**
 * A one-line, human-readable rendering of a decoded call.
 *
 * Exists for the evidence bundle and the §7.5 five-minute comprehension gate, where a
 * reviewer has to see what the agent actually proposed without reading hex. Deliberately
 * not parseable and never used for comparison — the typed fields are the truth.
 */
export function describe(decoded: DecodedCall): string {
    switch (decoded.schema) {
        case "DemoPay.purchase":
            return (
                `DemoPay.purchase(resource=${decoded.resourceId}, beneficiary=${decoded.beneficiary}, ` +
                `duration=${decoded.durationSeconds}s, recurring=${decoded.recurring})`
            );
        case "DemoERC20.approve":
            return `DemoERC20.approve(spender=${decoded.spender}, amount=${decoded.amount})`;
    }
}

/**
 * Whether an approval amount is the unlimited sentinel.
 *
 * Named rather than inlined because §7.1 lists "finite, oversized, and unlimited approvals"
 * as three distinct fixture classes, and because max-uint256 is what the Case 2 injection
 * actually produced (A-009). The evaluator applies the ceiling; this only recognises the
 * value that makes a ceiling meaningless.
 */
export const MAX_UINT256 = (1n << 256n) - 1n;

export function isUnlimitedApproval(amount: bigint): boolean {
    return amount === MAX_UINT256;
}

export {DecodeError} from "./abi.ts";
export type {DecodeFailureCode} from "./abi.ts";
