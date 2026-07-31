import {keccak256, stringToBytes} from "viem";
import type {Hex} from "../signer/protocol.ts";

/**
 * Strict transcription of an agent's typed parameter claim into ABI calldata (§9 step 7).
 *
 * This is `decode/abi.ts` run backwards, and it is strict for the same reason: every
 * deviation from the exact canonical form is a named refusal rather than a normalisation.
 * A transcriber that "helpfully" reads `uint` as `uint256`, ` 86400 ` as `86400`, or
 * `0x0DeaDBeef…` padded however it likes is a transcriber whose output is not the only
 * bytes its input could have meant — and the whole point of the step is that the bytes
 * Sentinel evaluates are the ones the agent proposed.
 *
 * WHAT D-019 MAKES THIS LAYER, AND WHAT IT DOES NOT.
 *
 * Under D-019 Sentinel encodes calldata from the agent's `function_signature` and `args`.
 * That makes this module part of the TRUSTED path (§3.1, "canonical schema encoders and
 * hashes"), and it makes the agent's parameter claim and the executed bytes the same
 * statement by construction. The honest consequence, stated here because a future reader
 * will otherwise re-derive it from the code: for an agent-sourced action, the decoder
 * recovering the agent's claimed parameters is NOT independent evidence — it is a
 * round-trip through this file. What remains genuinely untrusted on the agent path is the
 * agent's `rationale`: its account of what the call MEANS. Sentinel never reads it.
 *
 * `propose.roundtrip.test.ts` measures the transcription against the real decoder rather
 * than assuming it. That test is not decoration: it is the only thing standing between
 * "the agent proposed X" and "Sentinel evaluated X", now that no separate encoding exists
 * to disagree with.
 */

/** Every way a proposal can fail to transcribe. Each is a distinct reason code. */
export const PROPOSAL_FAILURES = {
    /** `target` is not a 20-byte hex address. */
    PROPOSAL_MALFORMED_TARGET: "target is not a 20-byte hex address",
    /** `value_wei` is not a canonical decimal integer, or does not fit uint256. */
    PROPOSAL_MALFORMED_VALUE: "value_wei is not a canonical uint256 decimal string",
    /** `function_signature` is not exactly `name(type,type,...)` with no whitespace. */
    PROPOSAL_MALFORMED_SIGNATURE: "function_signature is not a canonical solidity signature",
    /** A declared type is outside the statically-encodable set this module supports. */
    PROPOSAL_UNSUPPORTED_ARG_TYPE: "argument type is not a supported static type",
    /** The number of arguments does not match the number of declared types. */
    PROPOSAL_ARITY_MISMATCH: "argument count does not match the signature's declared types",
    /** An argument is not in the canonical textual form for its declared type. */
    PROPOSAL_MALFORMED_ARG: "argument is not canonical for its declared type",
    /** A numeric argument does not fit the declared width. */
    PROPOSAL_ARG_OUT_OF_RANGE: "argument does not fit its declared width",
} as const;

export type ProposalFailureCode = keyof typeof PROPOSAL_FAILURES;

export class ProposalError extends Error {
    readonly code: ProposalFailureCode;

    constructor(code: ProposalFailureCode, detail?: string) {
        super(detail === undefined ? PROPOSAL_FAILURES[code] : `${PROPOSAL_FAILURES[code]}: ${detail}`);
        this.code = code;
    }
}

const WORD_HEX = 64;
const MAX_UINT256 = (1n << 256n) - 1n;

/**
 * Canonical decimal only: no sign, no leading zeros, no underscores, no whitespace.
 *
 * Leading zeros are refused rather than trimmed because `value_wei` is a bound field
 * (§3.3(4)) and two spellings of one number arriving from an untrusted source is a
 * distinction worth preserving rather than erasing.
 */
const DECIMAL_RE = /^(0|[1-9][0-9]*)$/;
const ADDRESS_RE = /^0x[0-9a-fA-F]{40}$/;
const SIGNATURE_RE = /^([A-Za-z_$][A-Za-z0-9_$]*)\((.*)\)$/;
const UINT_RE = /^uint([0-9]+)$/;
const BYTES_RE = /^bytes([0-9]+)$/;

/** Parse a canonical decimal string into a bigint bounded by `bits`. */
function parseUint(text: string, bits: number, what: string): bigint {
    if (!DECIMAL_RE.test(text)) {
        throw new ProposalError(
            what === "value_wei" ? "PROPOSAL_MALFORMED_VALUE" : "PROPOSAL_MALFORMED_ARG",
            `${what} = ${JSON.stringify(text)}`,
        );
    }
    const value = BigInt(text);
    if (value > (bits === 256 ? MAX_UINT256 : (1n << BigInt(bits)) - 1n)) {
        throw new ProposalError(
            what === "value_wei" ? "PROPOSAL_MALFORMED_VALUE" : "PROPOSAL_ARG_OUT_OF_RANGE",
            `${what} = ${text} exceeds uint${bits}`,
        );
    }
    return value;
}

export function parseValueWei(text: string): bigint {
    return parseUint(text, 256, "value_wei");
}

export function parseTarget(text: string): Hex {
    if (!ADDRESS_RE.test(text)) {
        throw new ProposalError("PROPOSAL_MALFORMED_TARGET", JSON.stringify(text));
    }
    return text.toLowerCase() as Hex;
}

/**
 * Split a signature into its name and declared types.
 *
 * Whitespace is refused outright rather than stripped. The selector is
 * `keccak256(signature)[0..4]`, so `approve(address, uint256)` and `approve(address,uint256)`
 * are DIFFERENT four bytes — one of which routes to no function at all. Trimming would
 * silently repair an agent's mistake into a call it did not propose.
 */
export function parseSignature(signature: string): {name: string; types: string[]} {
    if (/\s/.test(signature)) {
        throw new ProposalError("PROPOSAL_MALFORMED_SIGNATURE", "contains whitespace");
    }
    const m = SIGNATURE_RE.exec(signature);
    if (m === null) {
        throw new ProposalError("PROPOSAL_MALFORMED_SIGNATURE", JSON.stringify(signature));
    }
    const name = m[1]!;
    const params = m[2]!;
    const types = params === "" ? [] : params.split(",");
    for (const type of types) assertSupportedType(type);
    return {name, types};
}

/**
 * The statically-encodable types this module transcribes.
 *
 * Deliberately narrow, and deliberately WIDER than the two schemas Sentinel decodes. An
 * agent must be able to propose a call Sentinel cannot decode — §3.3(8) requires
 * "unsupported calls, undecodable calldata" never to produce an automatic allow, and that
 * path is unreachable from a proposal if the transcriber refuses to build anything but the
 * two supported schemas. The transcriber is not a gate.
 *
 * Dynamic types (`bytes`, `string`, arrays, tuples) are refused rather than encoded,
 * because their head/tail layout is a second encoding scheme with its own edge cases and
 * neither demo schema uses one. That is a stated limit, not an oversight.
 */
function assertSupportedType(type: string): void {
    if (type === "address" || type === "bool") return;

    const uint = UINT_RE.exec(type);
    if (uint !== null) {
        const bits = Number(uint[1]);
        if (bits >= 8 && bits <= 256 && bits % 8 === 0 && String(bits) === uint[1]) return;
        throw new ProposalError("PROPOSAL_UNSUPPORTED_ARG_TYPE", type);
    }

    const bytes = BYTES_RE.exec(type);
    if (bytes !== null) {
        const size = Number(bytes[1]);
        if (size >= 1 && size <= 32 && String(size) === bytes[1]) return;
        throw new ProposalError("PROPOSAL_UNSUPPORTED_ARG_TYPE", type);
    }

    throw new ProposalError("PROPOSAL_UNSUPPORTED_ARG_TYPE", type);
}

/** Encode one argument into its 32-byte word, as 64 lowercase hex characters. */
function encodeArg(type: string, text: string, index: number): string {
    const where = `arg ${index} (${type})`;

    if (type === "address") {
        if (!ADDRESS_RE.test(text)) {
            throw new ProposalError("PROPOSAL_MALFORMED_ARG", `${where} = ${JSON.stringify(text)}`);
        }
        return text.slice(2).toLowerCase().padStart(WORD_HEX, "0");
    }

    if (type === "bool") {
        // Exactly the two canonical spellings. "1"/"0"/"True"/"yes" are refused, matching
        // the decoder's refusal of any bool word that is neither 0 nor 1.
        if (text === "true") return "1".padStart(WORD_HEX, "0");
        if (text === "false") return "0".padStart(WORD_HEX, "0");
        throw new ProposalError("PROPOSAL_MALFORMED_ARG", `${where} = ${JSON.stringify(text)}`);
    }

    const uint = UINT_RE.exec(type);
    if (uint !== null) {
        const value = parseUint(text, Number(uint[1]), where);
        return value.toString(16).padStart(WORD_HEX, "0");
    }

    const bytes = BYTES_RE.exec(type)!;
    const size = Number(bytes[1]);
    const re = new RegExp(`^0x[0-9a-fA-F]{${size * 2}}$`);
    if (!re.test(text)) {
        throw new ProposalError("PROPOSAL_MALFORMED_ARG", `${where} = ${JSON.stringify(text)}`);
    }
    // bytesN is LEFT-aligned: bytes32 fills the word, bytes4 occupies its top four bytes.
    return text.slice(2).toLowerCase().padEnd(WORD_HEX, "0");
}

/** `keccak256(signature)[0..4]`, computed from the agent's exact bytes. */
export function selectorFor(signature: string): Hex {
    return keccak256(stringToBytes(signature)).slice(0, 10) as Hex;
}

/**
 * Transcribe a signature and its textual arguments into calldata.
 *
 * Throws `ProposalError` on any deviation. The caller turns that into a recorded refusal —
 * an unbuildable proposal is evidence about the agent, not an error to swallow.
 */
export function encodeCall(signature: string, args: readonly string[]): Hex {
    const {types} = parseSignature(signature);
    if (args.length !== types.length) {
        throw new ProposalError(
            "PROPOSAL_ARITY_MISMATCH",
            `signature declares ${types.length}, proposal supplied ${args.length}`,
        );
    }
    const words = types.map((type, i) => encodeArg(type, args[i]!, i));
    return (selectorFor(signature) + words.join("")) as Hex;
}
