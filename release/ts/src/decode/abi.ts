import type {Hex} from "../signer/protocol.ts";

/**
 * Strict ABI word reading for the supported call schemas (§9 step 4).
 *
 * WHY THIS IS HAND-ROLLED AND STRICT, RATHER THAN A CALL TO A LIBRARY DECODER.
 *
 * §4.2 Case 2 is the requirement: "Sentinel derives the selector and parameters from
 * calldata rather than trusting the agent's description." The value of that derivation
 * depends entirely on how it handles calldata that is *almost* well-formed — trailing
 * bytes, an address word with dirty upper bits, a bool encoded as 2. A permissive decoder
 * silently normalises all three, and then the parameters Sentinel reasons about are not the
 * only parameters those bytes could mean.
 *
 * So every deviation from the exact encoding is a named failure rather than a shrug.
 *
 * THIS IS DELIBERATELY STRICTER THAN THE EVM, AND THE DIVERGENCE MATTERS ENOUGH TO STATE.
 * Solidity's own external-call decoder ignores calldata beyond the declared parameters, so
 * a call carrying trailing garbage executes normally onchain while this decoder refuses it.
 * That is the intended direction: §3.3(11) says unsupported top-level operations are
 * "denied or reviewed by default", and §3.3(8) says undecodable calldata never produces an
 * automatic allow. A decoder that refuses something the chain would have accepted produces
 * a review; a decoder that accepts something it should not have produces a wrong allow.
 * Only one of those is recoverable.
 *
 * `decode.chain.test.ts` measures the divergence against the real deployed contracts rather
 * than assuming it, because "Solidity is more lenient here" is exactly the kind of claim
 * this repository's own rules say to verify before relying on.
 */

export const WORD_HEX = 64;

/** Every way a supported schema can fail to decode. Each is a distinct reason code. */
export const DECODE_FAILURES = {
    /** Fewer than 4 bytes: no selector at all. */
    DECODE_NO_SELECTOR: "calldata is shorter than a 4-byte selector",
    /** The selector is not one of the supported schemas (§4: exactly two). */
    DECODE_UNKNOWN_SELECTOR: "selector is not a supported call schema",
    /** A supported selector sent to a contract that does not implement it. */
    DECODE_SELECTOR_TARGET_MISMATCH: "selector is not supported at this target",
    /** The target is not one of the supported demo contracts. */
    DECODE_UNSUPPORTED_TARGET: "target is not a supported contract",
    /** Argument region is not exactly the declared number of 32-byte words. */
    DECODE_LENGTH_MISMATCH: "argument region is not the exact declared length",
    /** An address word carries non-zero bytes above the low 20. */
    DECODE_DIRTY_ADDRESS_BITS: "address word has non-zero high-order bytes",
    /** A bool word is neither 0 nor 1. */
    DECODE_NON_CANONICAL_BOOL: "bool word is neither 0 nor 1",
    /** A uintN word carries non-zero bytes above the declared width. */
    DECODE_UINT_OVERFLOW: "uint word exceeds its declared width",
} as const;

export type DecodeFailureCode = keyof typeof DECODE_FAILURES;

export class DecodeError extends Error {
    readonly code: DecodeFailureCode;

    constructor(code: DecodeFailureCode, detail?: string) {
        super(detail === undefined ? DECODE_FAILURES[code] : `${DECODE_FAILURES[code]}: ${detail}`);
        this.code = code;
    }
}

/**
 * A cursor over the argument region of a call.
 *
 * OUTPUTS ARE LOWERCASED. Two calldata strings differing only in hex spelling are the SAME
 * BYTES and execute identically, so they must decode to identical parameters — otherwise the
 * decoder's headline claim, faithfulness to bytes, is false: its output would be a function
 * of the string. A D-017 adjudicator demonstrated that an uppercase-spelled beneficiary
 * produced a different decoded address and a spurious FATAL refusal downstream. Normalising
 * here rather than at each call site keeps the property where it is stated.
 *
 * Constructed only after the region has been length-checked, so a reader that exists is a
 * reader whose every `word(i)` is in bounds. Bounds are a construction-time property here
 * rather than a per-read check, because a per-read check is one someone later forgets.
 */
export class WordReader {
    private readonly body: string;
    readonly wordCount: number;

    private constructor(body: string) {
        this.body = body;
        this.wordCount = body.length / WORD_HEX;
    }

    /**
     * @param callData full calldata including selector
     * @param expectedWords exact number of 32-byte argument words the schema declares
     */
    static forSchema(callData: Hex, expectedWords: number): WordReader {
        const body = callData.slice(2 + 8);
        if (body.length !== expectedWords * WORD_HEX) {
            throw new DecodeError(
                "DECODE_LENGTH_MISMATCH",
                `expected ${expectedWords} words (${expectedWords * 32} bytes), got ${
                    body.length / 2
                } bytes`,
            );
        }
        return new WordReader(body);
    }

    private word(index: number): string {
        return this.body.slice(index * WORD_HEX, (index + 1) * WORD_HEX);
    }

    /** bytes32: every bit is meaningful, so there is nothing to reject. */
    bytes32(index: number): Hex {
        return `0x${this.word(index).toLowerCase()}` as Hex;
    }

    /**
     * address: the low 20 bytes, with the high 12 required to be zero.
     *
     * Two distinct addresses can otherwise share a word's low bytes while differing above
     * them — and the beneficiary of a purchase is precisely a field a mandate constrains.
     */
    address(index: number): Hex {
        const w = this.word(index);
        const high = w.slice(0, 24);
        if (!/^0+$/.test(high)) {
            throw new DecodeError("DECODE_DIRTY_ADDRESS_BITS", `word ${index} = 0x${w}`);
        }
        return `0x${w.slice(24).toLowerCase()}` as Hex;
    }

    /**
     * boolean: exactly 0 or 1.
     *
     * `recurringAllowed` is a mandate field (§5.1) and a bound, inspectable effect on
     * DemoPay. "Any non-zero is true" would let 2 and 1 be the same proposal to Sentinel
     * while being different bytes on the wire.
     */
    boolean(index: number): boolean {
        const w = this.word(index);
        if (/^0+$/.test(w)) return false;
        if (/^0*1$/.test(w)) return true;
        throw new DecodeError("DECODE_NON_CANONICAL_BOOL", `word ${index} = 0x${w}`);
    }

    /** uintN for N ≤ 256, rejecting anything set above the declared width. */
    uint(index: number, bits: number): bigint {
        const w = this.word(index);
        if (bits < 256) {
            const highNibbles = (256 - bits) / 4;
            if (!/^0+$/.test(w.slice(0, highNibbles))) {
                throw new DecodeError("DECODE_UINT_OVERFLOW", `word ${index} exceeds uint${bits}`);
            }
        }
        return BigInt(`0x${w}`);
    }
}

/** The 4-byte selector, or a failure if there isn't one. */
export function selectorOf(callData: Hex): Hex {
    if (callData.length < 2 + 8) throw new DecodeError("DECODE_NO_SELECTOR");
    return callData.slice(0, 10).toLowerCase() as Hex;
}
