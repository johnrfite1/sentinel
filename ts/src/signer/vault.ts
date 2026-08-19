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
 *
 * ONE BLOCK, NOT ELEVEN (D-055(c), the E3 repair).
 *
 * THE ARGUMENT this establishes, stated before the code as `docs/repair-protocol.md` step 1
 * requires: **every state and code value the signer reasons about comes from ONE block, and
 * that block is named in the returned snapshot** — so the signer can never attest to a
 * combination of values that never simultaneously existed, and `attest.ts` can require the
 * receipt's anchor to name the block the signer actually read.
 *
 * That is deliberately not a recency rule. D-055(c) rejected inventing a timeout: a number
 * of blocks or seconds is a policy parameter nobody had reasoned about, and the answer that
 * needs no parameter is CONSISTENCY — the signer attests against the state it read, and a
 * verdict computed against any other block is refused because it disagrees, not because it
 * is old. Recency falls out of that rather than being asserted.
 *
 * WHAT THE PREVIOUS VERSION DID, because it is the defect: ten `eth_call`s, a `getCode` and
 * a `getBlockNumber`, all at "latest", each its own request, with a comment conceding they "could
 * in principle straddle a block boundary" and arguing it away on the grounds that a local
 * Anvil has no competing producer. Two things were wrong with that. The straddle made
 * `observedAtBlock` a number no field was guaranteed to have been read at — and nothing
 * consumed it, so the inconsistency was invisible. And the environment argument is exactly
 * the kind this project has repeatedly paid for: it justifies a property from the deployment
 * rather than from the code.
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
    /**
     * The single block EVERY field above was read at (D-055(c)). Not "the block number
     * around the time of the reads" — the pin passed to each one.
     */
    observedAtBlock: bigint;
    /**
     * The hash of that block, taken from the same `getBlock` that supplied the number and
     * re-confirmed after the reads completed. Named separately from the number because the
     * number alone does not identify a block across a reorg, and the anchor check in
     * `attest.ts` compares both.
     */
    observedBlockHash: Hex;
}

export interface ChainReader {
    chainId(): Promise<bigint>;
    /**
     * A consistent snapshot of the vault at one block, or a throw. Never a partial read and
     * never a straddle: see the file header for why that distinction is the whole point.
     */
    readVaultState(vault: Hex, target: Hex, selector: Hex): Promise<VaultState>;
    /** Block hash at a given height, or null when the chain has no such block. */
    blockHashAt(blockNumber: bigint): Promise<Hex | null>;
}

/**
 * How many times to re-take the snapshot when the head moves underneath it.
 *
 * There is no timeout here and that is deliberate — this bounds WORK, not RECENCY. Each
 * attempt is a fresh pin at the then-current head; exhausting them means the chain is
 * producing blocks faster than the signer can observe one, which is a condition the signer
 * reports (SIGNER_CHAIN_UNSTABLE) rather than one it papers over by accepting a stale pin.
 */
export const SNAPSHOT_ATTEMPTS = 5;

/** Thrown when no attempt produced a snapshot whose block was still the head afterwards. */
export class ChainUnstableError extends Error {
    /**
     * `pendingOnly` distinguishes the two conditions this error covers (R2-F6). Every attempt
     * saw a hashless (pending) head, versus the head actually moving under the reads. Same
     * tier and same remedy, different fact — and reporting one as the other is the substitution
     * this project exists to study.
     */
    constructor(attempts: number, pendingOnly = false) {
        super(
            pendingOnly
                ? `no finalised head after ${attempts} attempts: every observation returned a ` +
                      "pending block with no hash, so there was nothing to anchor to"
                : `no stable block after ${attempts} attempts: the head moved or was replaced ` +
                      "under each pinned read",
        );
        this.name = "ChainUnstableError";
        this.pendingOnly = pendingOnly;
    }
    readonly pendingOnly: boolean = false;
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
            // Tracks whether EVERY attempt failed for the pending-head reason (R2-F6).
            let pendingOnly = true;
            for (let attempt = 0; attempt < SNAPSHOT_ATTEMPTS; attempt += 1) {
                // Number and hash from ONE response. Deriving the hash from a second request
                // would reintroduce, in the identifier of the pin itself, exactly the
                // straddle this function exists to remove.
                const head = await client.getBlock();
                if (head.hash === null) {
                    // A pending block. It has no hash to anchor to and its contents are not
                    // final; there is nothing here to attest against. `pendingOnly` stays true.
                    continue;
                }
                const at = head.number;
                const headHash = head.hash.toLowerCase() as Hex;

                // EVERY read below carries `blockNumber: at`. That is the repair. A read
                // added here without the pin is the defect returning, which is why the
                // pin lives in this one helper rather than at each call site.
                const call = <N extends string>(functionName: N, args: readonly unknown[] = []) =>
                    client.readContract({
                        address: vault,
                        abi: VAULT_ABI,
                        functionName: functionName as never,
                        args: args as never,
                        blockNumber: at,
                    });

                const [
                    owner, signer, activeMandateHash, activePolicyHash, actionNonce,
                    paused, maxNativeValueWei, targetAllowed, selectorAllowed, domainSeparator,
                    code,
                ] = await Promise.all([
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
                    client.getCode({address: target, blockNumber: at}),
                ]);

                // The pin makes the snapshot internally consistent; this makes it CURRENT.
                // One request covers both ways the pin can go stale: the head advancing past
                // it, and a same-height reorg replacing it. A snapshot that fails either is
                // discarded rather than returned with a caveat — the signer has no way to
                // attest "this was true a moment ago".
                const confirm = await client.getBlock();
                if (confirm.hash === null) {
                    // A PENDING CONFIRMATION. Nothing moved — the node simply had no finalised
                    // head to confirm against, which is condition (b), not (a). Attributing it
                    // to movement is the same substitution R2-F6 was raised about, one level
                    // in; found by the D-057(5) verifier after the first repair.
                    continue;
                }
                if (confirm.number !== at || confirm.hash.toLowerCase() !== headHash) {
                    // The head genuinely moved or was replaced: condition (a).
                    pendingOnly = false;
                    continue;
                }

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
                    observedAtBlock: at,
                    observedBlockHash: headHash,
                };
            }

            throw new ChainUnstableError(SNAPSHOT_ATTEMPTS, pendingOnly);
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
