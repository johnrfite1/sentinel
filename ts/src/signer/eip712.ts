import {keccak256, stringToBytes, toBytes} from "viem";
import type {
    ActionPayload,
    DecisionReceiptPayload,
    Hex,
    MandatePayload,
    OverrideAuthorizationPayload,
    PolicyPayload,
} from "./protocol.ts";

/**
 * EIP-712 hashing for the isolated signer — a second, independent implementation of the
 * schemas in proposal §5.
 *
 * WHY THIS IS NOT SHARED CODE, AND MUST NOT BECOME SHARED CODE.
 *
 * §3.1 says the signer "independently recomputes the canonical action hash." The weak
 * reading of that is "recomputes from the payload instead of trusting a supplied digest."
 * The strong reading is "recomputes with an implementation that could disagree." D-010
 * already settled which reading this project uses, in the course of ruling on the receipt
 * verifier: *"the same library behind a different flag is the same code verifying itself."*
 * That standard applies here for the same reason it applies there.
 *
 * So this module is deliberately duplicated work. When the conformance evaluator is built
 * (§9 step 6) it gets its own encoder; it does not import this one, and this one does not
 * import it. The duplication is the point. Three independent implementations now exist or
 * are planned — Solidity (`SentinelTypes.sol`), this one, and the D-010 Python verifier —
 * and every signature this signer produces is checked against the Solidity one by the
 * vault itself, at execution time, on every single action.
 *
 * TRANSCRIPTION DISCIPLINE. The type strings below were transcribed from §5 of the
 * proposal, not copied from the Solidity. That is what makes `SentinelTypes.t.sol`'s
 * golden-typehash technique work across languages: two independent transcriptions of the
 * same written schema agreeing is evidence; one copy of another copy is not. The golden
 * constants at the bottom are pinned so a later edit to a type string fails a test rather
 * than silently reassigning every hash in the system.
 *
 * ENCODING. `encodeData` for EIP-712 atomic types is each member padded to 32 bytes, in
 * declared order, after the typehash. Every field of every §5 payload is atomic — no
 * strings, bytes, arrays, or nested structs — so no member needs pre-hashing. The padding
 * is written out by hand below rather than delegated to an ABI coder: it is twenty lines,
 * it is checkable against the EIP by eye, and it keeps the independence claim from resting
 * on a third-party library's interpretation of the same spec.
 */

// ---------------------------------------------------------------------------
// Word encoding
// ---------------------------------------------------------------------------

const ZEROS = "0".repeat(64);

/** Left-pad to a 32-byte word: uintN, address, bool. */
function leftPad(hexDigits: string): string {
    if (hexDigits.length > 64) throw new Error(`value exceeds one word: 0x${hexDigits}`);
    return ZEROS.slice(0, 64 - hexDigits.length) + hexDigits;
}

/** Right-pad to a 32-byte word: bytesN (left-aligned, per the ABI spec). */
function rightPad(hexDigits: string): string {
    if (hexDigits.length > 64) throw new Error(`value exceeds one word: 0x${hexDigits}`);
    return hexDigits + ZEROS.slice(0, 64 - hexDigits.length);
}

function strip(v: Hex): string {
    return v.slice(2).toLowerCase();
}

const word = {
    uint(v: bigint): string {
        if (v < 0n) throw new Error("negative value in an unsigned field");
        return leftPad(v.toString(16));
    },
    bool(v: boolean): string {
        return leftPad(v ? "1" : "0");
    },
    /** address is a uint160 for encoding purposes: left-padded. */
    address(v: Hex): string {
        const d = strip(v);
        if (d.length !== 40) throw new Error(`not a 20-byte address: ${v}`);
        return leftPad(d);
    },
    bytes32(v: Hex): string {
        const d = strip(v);
        if (d.length !== 64) throw new Error(`not a 32-byte value: ${v}`);
        return d;
    },
    /** bytesN is left-aligned, so a 4-byte selector occupies the HIGH-order bytes. */
    bytes4(v: Hex): string {
        const d = strip(v);
        if (d.length !== 8) throw new Error(`not a 4-byte value: ${v}`);
        return rightPad(d);
    },
};

function structHash(typeHash: Hex, words: string[]): Hex {
    return keccak256(`0x${strip(typeHash)}${words.join("")}` as Hex);
}

// ---------------------------------------------------------------------------
// Type strings — transcribed from proposal §5
// ---------------------------------------------------------------------------

export const MANDATE_TYPE =
    "MandatePayload(uint16 schemaVersion,bytes32 mandateId,address principal,address vault,uint256 chainId,address target,bytes32 targetCodeHash,bytes4 selector,uint256 maxNativeValueWei,bytes32 purposeKind,bytes32 resourceId,address beneficiary,uint64 durationSeconds,bool recurringAllowed,uint64 validAfter,uint64 validUntil,bytes32 policyHash)";

export const POLICY_TYPE =
    "PolicyPayload(uint16 schemaVersion,uint32 policyVersion,address vault,uint256 chainId,uint8 allowedOperation,bytes32 allowedTargetsHash,bytes32 allowedSelectorsHash,uint256 maxNativeValueWei,uint256 maxAllowanceIncreaseBaseUnits,bytes32 allowedCallGraphHash,uint64 validAfter,uint64 validUntil,uint8 failureMode)";

export const ACTION_TYPE =
    "ActionPayload(uint16 schemaVersion,uint256 chainId,address vault,uint256 actionNonce,address target,uint256 valueWei,bytes32 dataHash,uint8 operation,bytes32 mandateHash,bytes32 policyHash,uint64 deadline)";

export const RECEIPT_TYPE =
    "DecisionReceiptPayload(uint16 schemaVersion,bytes32 decisionId,bytes32 actionHash,bytes32 mandateHash,bytes32 policyHash,uint8 verdict,bytes32 reasonCodesHash,bytes32 evidenceHash,uint256 simulationBlockNumber,bytes32 simulationBlockHash,uint64 issuedAt,uint64 expiresAt,address signer)";

export const OVERRIDE_TYPE =
    "OverrideAuthorizationPayload(uint16 schemaVersion,bytes32 reviewReceiptHash,bytes32 actionHash,bytes32 mandateHash,bytes32 policyHash,uint256 actionNonce,bytes32 reasonHash,uint64 issuedAt,uint64 expiresAt)";

export const EIP712_DOMAIN_TYPE =
    "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)";

export const MANDATE_TYPEHASH = keccak256(stringToBytes(MANDATE_TYPE));
export const POLICY_TYPEHASH = keccak256(stringToBytes(POLICY_TYPE));
export const ACTION_TYPEHASH = keccak256(stringToBytes(ACTION_TYPE));
export const RECEIPT_TYPEHASH = keccak256(stringToBytes(RECEIPT_TYPE));
export const OVERRIDE_TYPEHASH = keccak256(stringToBytes(OVERRIDE_TYPE));
export const EIP712_DOMAIN_TYPEHASH = keccak256(stringToBytes(EIP712_DOMAIN_TYPE));

export const DOMAIN_NAME = "Sentinel";
export const DOMAIN_VERSION = "0.2";

// ---------------------------------------------------------------------------
// Domain and digest
// ---------------------------------------------------------------------------

export function domainSeparator(chainId: bigint, vault: Hex): Hex {
    return structHash(EIP712_DOMAIN_TYPEHASH, [
        word.bytes32(keccak256(stringToBytes(DOMAIN_NAME))),
        word.bytes32(keccak256(stringToBytes(DOMAIN_VERSION))),
        word.uint(chainId),
        word.address(vault),
    ]);
}

/** keccak256(0x1901 ‖ domainSeparator ‖ structHash). */
export function digest(domainSep: Hex, hashStruct: Hex): Hex {
    return keccak256(`0x1901${strip(domainSep)}${strip(hashStruct)}` as Hex);
}

// ---------------------------------------------------------------------------
// Struct hashes
// ---------------------------------------------------------------------------

export function hashMandate(m: MandatePayload): Hex {
    return structHash(MANDATE_TYPEHASH, [
        word.uint(m.schemaVersion),
        word.bytes32(m.mandateId),
        word.address(m.principal),
        word.address(m.vault),
        word.uint(m.chainId),
        word.address(m.target),
        word.bytes32(m.targetCodeHash),
        word.bytes4(m.selector),
        word.uint(m.maxNativeValueWei),
        word.bytes32(m.purposeKind),
        word.bytes32(m.resourceId),
        word.address(m.beneficiary),
        word.uint(m.durationSeconds),
        word.bool(m.recurringAllowed),
        word.uint(m.validAfter),
        word.uint(m.validUntil),
        word.bytes32(m.policyHash),
    ]);
}

export function hashPolicy(p: PolicyPayload): Hex {
    return structHash(POLICY_TYPEHASH, [
        word.uint(p.schemaVersion),
        word.uint(p.policyVersion),
        word.address(p.vault),
        word.uint(p.chainId),
        word.uint(p.allowedOperation),
        word.bytes32(p.allowedTargetsHash),
        word.bytes32(p.allowedSelectorsHash),
        word.uint(p.maxNativeValueWei),
        word.uint(p.maxAllowanceIncreaseBaseUnits),
        word.bytes32(p.allowedCallGraphHash),
        word.uint(p.validAfter),
        word.uint(p.validUntil),
        word.uint(p.failureMode),
    ]);
}

export function hashAction(a: ActionPayload): Hex {
    return structHash(ACTION_TYPEHASH, [
        word.uint(a.schemaVersion),
        word.uint(a.chainId),
        word.address(a.vault),
        word.uint(a.actionNonce),
        word.address(a.target),
        word.uint(a.valueWei),
        word.bytes32(a.dataHash),
        word.uint(a.operation),
        word.bytes32(a.mandateHash),
        word.bytes32(a.policyHash),
        word.uint(a.deadline),
    ]);
}

export function hashReceipt(r: DecisionReceiptPayload): Hex {
    return structHash(RECEIPT_TYPEHASH, [
        word.uint(r.schemaVersion),
        word.bytes32(r.decisionId),
        word.bytes32(r.actionHash),
        word.bytes32(r.mandateHash),
        word.bytes32(r.policyHash),
        word.uint(r.verdict),
        word.bytes32(r.reasonCodesHash),
        word.bytes32(r.evidenceHash),
        word.uint(r.simulationBlockNumber),
        word.bytes32(r.simulationBlockHash),
        word.uint(r.issuedAt),
        word.uint(r.expiresAt),
        word.address(r.signer),
    ]);
}

/**
 * §5.5. Present for schema completeness and for the review path's end-to-end test.
 *
 * The signer never calls this. An OverrideAuthorization is signed by the human owner, and
 * §3.3(7) is exactly that the review path requires a credential the isolated signer cannot
 * mint — if this process could produce one, the owner's separate authorisation would be
 * decorative.
 */
export function hashOverride(o: OverrideAuthorizationPayload): Hex {
    return structHash(OVERRIDE_TYPEHASH, [
        word.uint(o.schemaVersion),
        word.bytes32(o.reviewReceiptHash),
        word.bytes32(o.actionHash),
        word.bytes32(o.mandateHash),
        word.bytes32(o.policyHash),
        word.uint(o.actionNonce),
        word.bytes32(o.reasonHash),
        word.uint(o.issuedAt),
        word.uint(o.expiresAt),
    ]);
}

// ---------------------------------------------------------------------------
// Content hashing helpers
// ---------------------------------------------------------------------------

/** keccak256 over raw calldata bytes — what the vault recomputes in `_checkAction`. */
export function hashCallData(callData: Hex): Hex {
    return keccak256(toBytes(callData));
}

/** keccak256 over UTF-8 text — used for the canonical evidence bundle and reason codes. */
export function hashUtf8(text: string): Hex {
    return keccak256(stringToBytes(text));
}

// ---------------------------------------------------------------------------
// Golden typehashes
// ---------------------------------------------------------------------------

/**
 * Pinned expected values, verified at import time.
 *
 * These literals are the same constants `SentinelTypes.t.sol` pins on the Solidity side
 * (`GOLD_MANDATE` and friends). They are NOT derived from the type strings above — that
 * is the entire point. The type strings are an independent transcription of §5; these
 * numbers come from the other implementation. Agreement between the two is cross-language
 * evidence that both transcriptions describe the same schema.
 *
 * Either check alone misses what the other catches. Recomputing a hash from a type string
 * proves only that keccak is deterministic. Pinning a hash without an independently
 * written type string beside it proves only that nobody edited the number. Together they
 * fail loudly on a field reorder, a renamed member, or a widened integer type — each of
 * which silently invalidates every signature already in the system.
 *
 * This throws at process start rather than at first signature: a signer that boots is a
 * signer whose schema agrees with the chain's.
 */
export const GOLDEN_TYPEHASHES = {
    MandatePayload: "0xc4b5766f52cd5eee3830dfe849c18b2cdc58d3d698d5c59e3a90c6dbe9d86799",
    PolicyPayload: "0xaa588a03b15fff97a72f063b7627ed7a61f2d76c4ca795da0607375d06a7f2a8",
    ActionPayload: "0x47787d5c4effb836c1e32339e527f5d91ae6e221e945eaf5c549614b02a60cff",
    DecisionReceiptPayload: "0xbbdf70ecc28b4e3c3e229f3b2bfdebbd4a9960d1302f588d52b09717ef5db797",
    OverrideAuthorizationPayload: "0x2257b6461a2c5c9477706f5afea11a1e3df3dbe16cb5c9a2b2150311e3cc4fea",
    EIP712Domain: "0x8b73c3c69bb8fe3d512ecc4cf759cc79239f7b179b0ffacaa9a75d522b39400f",
} as const satisfies Record<string, Hex>;

const COMPUTED_TYPEHASHES: Record<keyof typeof GOLDEN_TYPEHASHES, Hex> = {
    MandatePayload: MANDATE_TYPEHASH,
    PolicyPayload: POLICY_TYPEHASH,
    ActionPayload: ACTION_TYPEHASH,
    DecisionReceiptPayload: RECEIPT_TYPEHASH,
    OverrideAuthorizationPayload: OVERRIDE_TYPEHASH,
    EIP712Domain: EIP712_DOMAIN_TYPEHASH,
};

/**
 * Throws unless every transcribed type string hashes to its pinned Solidity counterpart.
 *
 * Exported so tests can assert the check exists and bites, rather than only observing
 * that importing this module happened not to throw.
 */
export function assertSchemaAgreement(): void {
    for (const [name, expected] of Object.entries(GOLDEN_TYPEHASHES)) {
        const actual = COMPUTED_TYPEHASHES[name as keyof typeof GOLDEN_TYPEHASHES];
        if (actual !== expected) {
            throw new Error(
                `EIP-712 schema drift in ${name}: this implementation computes ${actual}, ` +
                    `the pinned Solidity golden value is ${expected}. One of the two type ` +
                    `definitions changed. Every signature already issued under the old schema ` +
                    `is invalidated by this change — resolve it deliberately, do not repin.`,
            );
        }
    }
}

assertSchemaAgreement();
