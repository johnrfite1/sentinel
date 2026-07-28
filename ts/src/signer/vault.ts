import {createPublicClient, http, keccak256, toBytes} from "viem";
import type {PublicClient} from "viem";
import type {Hex} from "./protocol.ts";

/**
 * The signer's own view of the chain.
 *
 * §3.1 classifies "Active mandate and policy state stored by the vault" as TRUSTED and
 * "Remote RPC state until anchored and checked" as UNTRUSTED. The signer therefore reads
 * vault state itself rather than accepting the evaluator's account of it. That is the
 * difference between a signer that independently checks the mandate and one that
 * countersigns a claim about the mandate — and it is most of what makes A-005's isolation
 * worth the separate process.
 *
 * A read failure is never softened into a default. There is no `?? 0n`, no cached
 * fallback, no "assume unpaused". `readVaultState` throws, and the caller turns that into
 * SIGNER_VAULT_UNREACHABLE — a FATAL finding that refuses every verdict. §3.3(8) requires
 * that a critical dependency failure never produce an automatic allow; the cheapest way to
 * guarantee that is to have no code path in which unavailable state becomes a value.
 */

const VAULT_ABI = [
    {type: "function", name: "owner", inputs: [], outputs: [{type: "address"}], stateMutability: "view"},
    {type: "function", name: "signer", inputs: [], outputs: [{type: "address"}], stateMutability: "view"},
    {
        type: "function", name: "activeMandateHash", inputs: [], outputs: [{type: "bytes32"}],
        stateMutability: "view",
    },
    {
        type: "function", name: "activePolicyHash", inputs: [], outputs: [{type: "bytes32"}],
        stateMutability: "view",
    },
    {
        type: "function", name: "actionNonce", inputs: [], outputs: [{type: "uint256"}],
        stateMutability: "view",
    },
    {type: "function", name: "paused", inputs: [], outputs: [{type: "bool"}], stateMutability: "view"},
    {
        type: "function", name: "maxNativeValueWei", inputs: [], outputs: [{type: "uint256"}],
        stateMutability: "view",
    },
    {
        type: "function", name: "allowedTarget", inputs: [{type: "address"}], outputs: [{type: "bool"}],
        stateMutability: "view",
    },
    {
        type: "function", name: "allowedSelector", inputs: [{type: "bytes4"}], outputs: [{type: "bool"}],
        stateMutability: "view",
    },
    {
        type: "function", name: "domainSeparator", inputs: [], outputs: [{type: "bytes32"}],
        stateMutability: "view",
    },
] as const;

export interface VaultState {
    owner: Hex;
    signer: Hex;
    activeMandateHash: Hex;
    activePolicyHash: Hex;
    actionNonce: bigint;
    paused: boolean;
    maxNativeValueWei: bigint;
    targetAllowed: boolean;
    selectorAllowed: boolean;
    /** The vault's own EIP-712 domain separator, for the cross-language differential check. */
    domainSeparator: Hex;
    /** keccak256 of the target's runtime code, at the block this read observed. */
    targetCodeHash: Hex;
    observedAtBlock: bigint;
}

export interface ChainReader {
    chainId(): Promise<bigint>;
    readVaultState(vault: Hex, target: Hex, selector: Hex): Promise<VaultState>;
    /** Block hash at a given height, or null when the chain has no such block. */
    blockHashAt(blockNumber: bigint): Promise<Hex | null>;
}

/**
 * keccak256 of empty code.
 *
 * Worth naming because of a genuine asymmetry with Solidity: `address.codehash` is 0 for
 * an account that does not exist, but this constant for an account that exists with no
 * code. An offchain reader cannot distinguish the two, so a mandate pinning a code hash
 * for an EOA or a self-destructed target will mismatch here. That is the safe direction —
 * the mismatch is a CONFORMANCE finding that blocks ALLOW and permits REVIEW, which is
 * precisely Case 4's expected handling of a target whose code is not what was pinned.
 */
export const EMPTY_CODE_HASH: Hex =
    "0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470";

export function createChainReader(rpcUrl: string): ChainReader {
    const client: PublicClient = createPublicClient({transport: http(rpcUrl)});

    return {
        async chainId(): Promise<bigint> {
            return BigInt(await client.getChainId());
        },

        async readVaultState(vault: Hex, target: Hex, selector: Hex): Promise<VaultState> {
            const call = <N extends string>(functionName: N, args: readonly unknown[] = []) =>
                client.readContract({
                    address: vault,
                    abi: VAULT_ABI,
                    functionName: functionName as never,
                    args: args as never,
                });

            // One block number captured alongside the reads so the receipt can say what the
            // signer actually observed. These are separate eth_call requests and could in
            // principle straddle a block boundary; on a local Anvil with no competing
            // producer that is not a live concern, and the vault re-checks every value that
            // matters at execution time regardless. Recorded rather than papered over.
            const [
                blockNumber, owner, signer, activeMandateHash, activePolicyHash, actionNonce,
                paused, maxNativeValueWei, targetAllowed, selectorAllowed, domainSeparator, code,
            ] = await Promise.all([
                client.getBlockNumber(),
                call("owner"),
                call("signer"),
                call("activeMandateHash"),
                call("activePolicyHash"),
                call("actionNonce"),
                call("paused"),
                call("maxNativeValueWei"),
                call("allowedTarget", [target]),
                call("allowedSelector", [selector]),
                call("domainSeparator"),
                client.getCode({address: target}),
            ]);

            return {
                owner: (owner as string).toLowerCase() as Hex,
                signer: (signer as string).toLowerCase() as Hex,
                activeMandateHash: (activeMandateHash as string).toLowerCase() as Hex,
                activePolicyHash: (activePolicyHash as string).toLowerCase() as Hex,
                actionNonce: actionNonce as bigint,
                paused: paused as boolean,
                maxNativeValueWei: maxNativeValueWei as bigint,
                targetAllowed: targetAllowed as boolean,
                selectorAllowed: selectorAllowed as boolean,
                domainSeparator: (domainSeparator as string).toLowerCase() as Hex,
                targetCodeHash:
                    code === undefined || code === "0x"
                        ? EMPTY_CODE_HASH
                        : keccak256(toBytes(code)),
                observedAtBlock: blockNumber,
            };
        },

        async blockHashAt(blockNumber: bigint): Promise<Hex | null> {
            try {
                const block = await client.getBlock({blockNumber});
                return block.hash === null ? null : (block.hash.toLowerCase() as Hex);
            } catch {
                // A height the chain does not have. Distinguishable from an RPC outage by
                // the caller only in that the surrounding vault reads succeeded — an outage
                // fails those first and produces SIGNER_VAULT_UNREACHABLE instead.
                return null;
            }
        },
    };
}
