import {encodeAbiParameters, keccak256, stringToBytes, toBytes} from "viem";
import type {
    ActionPayload,
    Hex,
    MandatePayload,
    PolicyPayload,
} from "../signer/protocol.ts";

/**
 * The conformance evaluator's OWN EIP-712 implementation (A-013).
 *
 * It must not import `ts/src/signer/eip712.ts`, and this file goes further than merely not
 * importing it: it uses a **different technique**. The signer hand-rolls 32-byte word
 * padding; this delegates to viem's ABI coder. Two implementations that differ only in
 * which file they live in would agree on every bug they share, which is precisely what
 * D-010 means by "the same library behind a different flag is the same code verifying
 * itself". Two implementations that disagree in method can only agree by being right.
 *
 * That gives three independent implementations of the §5 schema in this repository:
 *
 *   1. Solidity   — `contracts/src/types/SentinelTypes.sol`, the enforcement point
 *   2. TypeScript — `ts/src/signer/eip712.ts`, hand-rolled padding
 *   3. TypeScript — this file, via viem's ABI coder
 *
 * plus the Python verifier D-010 adds at Gate S2. `differential.test.ts` checks all three
 * against each other on generated payloads — and asserts the independence itself, since
 * agreement between an implementation and its own import proves nothing.
 *
 * The type strings are transcribed from §5 of the proposal — again, not copied from either
 * of the other two implementations, because a copy proves nothing about the schema.
 */

const MANDATE_TYPE =
    "MandatePayload(uint16 schemaVersion,bytes32 mandateId,address principal,address vault,uint256 chainId,address target,bytes32 targetCodeHash,bytes4 selector,uint256 maxNativeValueWei,bytes32 purposeKind,bytes32 resourceId,address beneficiary,uint64 durationSeconds,bool recurringAllowed,uint64 validAfter,uint64 validUntil,bytes32 policyHash)";

const POLICY_TYPE =
    "PolicyPayload(uint16 schemaVersion,uint32 policyVersion,address vault,uint256 chainId,uint8 allowedOperation,bytes32 allowedTargetsHash,bytes32 allowedSelectorsHash,uint256 maxNativeValueWei,uint256 maxAllowanceIncreaseBaseUnits,bytes32 allowedCallGraphHash,uint64 validAfter,uint64 validUntil,uint8 failureMode)";

const ACTION_TYPE =
    "ActionPayload(uint16 schemaVersion,uint256 chainId,address vault,uint256 actionNonce,address target,uint256 valueWei,bytes32 dataHash,uint8 operation,bytes32 mandateHash,bytes32 policyHash,uint64 deadline)";

const EIP712_DOMAIN_TYPE =
    "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)";

const typeHash = (s: string): Hex => keccak256(stringToBytes(s));

export const MANDATE_TYPEHASH = typeHash(MANDATE_TYPE);
export const POLICY_TYPEHASH = typeHash(POLICY_TYPE);
export const ACTION_TYPEHASH = typeHash(ACTION_TYPE);
export const EIP712_DOMAIN_TYPEHASH = typeHash(EIP712_DOMAIN_TYPE);

/**
 * The same pinned Solidity golden values the other two implementations check against.
 *
 * Verified at import, so a process that starts is a process whose schema matches the chain's.
 */
const GOLDEN = {
    MandatePayload: "0xc4b5766f52cd5eee3830dfe849c18b2cdc58d3d698d5c59e3a90c6dbe9d86799",
    PolicyPayload: "0xaa588a03b15fff97a72f063b7627ed7a61f2d76c4ca795da0607375d06a7f2a8",
    ActionPayload: "0x47787d5c4effb836c1e32339e527f5d91ae6e221e945eaf5c549614b02a60cff",
    EIP712Domain: "0x8b73c3c69bb8fe3d512ecc4cf759cc79239f7b179b0ffacaa9a75d522b39400f",
} as const;

export function assertSchemaAgreement(): void {
    const computed: Record<keyof typeof GOLDEN, Hex> = {
        MandatePayload: MANDATE_TYPEHASH,
        PolicyPayload: POLICY_TYPEHASH,
        ActionPayload: ACTION_TYPEHASH,
        EIP712Domain: EIP712_DOMAIN_TYPEHASH,
    };
    for (const [name, expected] of Object.entries(GOLDEN)) {
        const actual = computed[name as keyof typeof GOLDEN];
        if (actual !== expected) {
            throw new Error(
                `evaluator EIP-712 schema drift in ${name}: computed ${actual}, pinned ${expected}`,
            );
        }
    }
}

assertSchemaAgreement();

function structHash(typehash: Hex, types: readonly {type: string}[], values: readonly unknown[]): Hex {
    return keccak256(
        encodeAbiParameters(
            [{type: "bytes32"}, ...types] as never,
            [typehash, ...values] as never,
        ),
    );
}

export function hashMandate(m: MandatePayload): Hex {
    return structHash(
        MANDATE_TYPEHASH,
        [
            {type: "uint16"}, {type: "bytes32"}, {type: "address"}, {type: "address"},
            {type: "uint256"}, {type: "address"}, {type: "bytes32"}, {type: "bytes4"},
            {type: "uint256"}, {type: "bytes32"}, {type: "bytes32"}, {type: "address"},
            {type: "uint64"}, {type: "bool"}, {type: "uint64"}, {type: "uint64"},
            {type: "bytes32"},
        ],
        [
            m.schemaVersion, m.mandateId, m.principal, m.vault, m.chainId, m.target,
            m.targetCodeHash, m.selector, m.maxNativeValueWei, m.purposeKind, m.resourceId,
            m.beneficiary, m.durationSeconds, m.recurringAllowed, m.validAfter, m.validUntil,
            m.policyHash,
        ],
    );
}

export function hashPolicy(p: PolicyPayload): Hex {
    return structHash(
        POLICY_TYPEHASH,
        [
            {type: "uint16"}, {type: "uint32"}, {type: "address"}, {type: "uint256"},
            {type: "uint8"}, {type: "bytes32"}, {type: "bytes32"}, {type: "uint256"},
            {type: "uint256"}, {type: "bytes32"}, {type: "uint64"}, {type: "uint64"},
            {type: "uint8"},
        ],
        [
            p.schemaVersion, p.policyVersion, p.vault, p.chainId, p.allowedOperation,
            p.allowedTargetsHash, p.allowedSelectorsHash, p.maxNativeValueWei,
            p.maxAllowanceIncreaseBaseUnits, p.allowedCallGraphHash, p.validAfter,
            p.validUntil, p.failureMode,
        ],
    );
}

export function hashAction(a: ActionPayload): Hex {
    return structHash(
        ACTION_TYPEHASH,
        [
            {type: "uint16"}, {type: "uint256"}, {type: "address"}, {type: "uint256"},
            {type: "address"}, {type: "uint256"}, {type: "bytes32"}, {type: "uint8"},
            {type: "bytes32"}, {type: "bytes32"}, {type: "uint64"},
        ],
        [
            a.schemaVersion, a.chainId, a.vault, a.actionNonce, a.target, a.valueWei,
            a.dataHash, a.operation, a.mandateHash, a.policyHash, a.deadline,
        ],
    );
}

export function domainSeparator(chainId: bigint, vault: Hex): Hex {
    return structHash(
        EIP712_DOMAIN_TYPEHASH,
        [{type: "bytes32"}, {type: "bytes32"}, {type: "uint256"}, {type: "address"}],
        [keccak256(stringToBytes("Sentinel")), keccak256(stringToBytes("0.2")), chainId, vault],
    );
}

export function hashCallData(callData: Hex): Hex {
    return keccak256(toBytes(callData));
}

export function hashUtf8(text: string): Hex {
    return keccak256(stringToBytes(text));
}
