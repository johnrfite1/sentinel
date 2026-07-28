import type {PublicClient} from "viem";
import type {Hex} from "../signer/protocol.ts";

/**
 * The Anvil control surface the effect pipeline needs (§3.2 steps 8–9).
 *
 * Kept as a thin, named layer over the raw RPC for one reason: every method here mutates
 * or inspects chain state that the rest of the system assumes is untouched, and a
 * misspelled `evm_revert` fails silently as an unknown-method error that a `catch` might
 * swallow. Naming them makes the failure a type error instead.
 *
 * Verified against Anvil v1.7.1 rather than assumed — snapshot/revert, account
 * impersonation, and `debug_traceTransaction` with `callTracer` were all probed on the
 * real binary before this module was written, including the two properties the pipeline
 * depends on: a revert rewinds contract state, and contracts deployed *before* the
 * snapshot survive it.
 */

/** Opaque snapshot handle. Anvil returns a quantity; it is never interpreted here. */
export type SnapshotId = string;

/** One node of a `callTracer` trace. */
export interface TraceNode {
    type: string;
    from: Hex;
    to?: Hex;
    value?: Hex;
    gasUsed?: Hex;
    input?: Hex;
    output?: Hex;
    error?: string;
    revertReason?: string;
    calls?: TraceNode[];
}

type Rpc = (method: string, params?: unknown[]) => Promise<unknown>;

function rpcOf(client: PublicClient): Rpc {
    return (method, params = []) =>
        (client as unknown as {request: (a: {method: string; params: unknown[]}) => Promise<unknown>})
            .request({method, params});
}

export interface AnvilControl {
    snapshot(): Promise<SnapshotId>;
    /** @returns true if Anvil accepted the revert. */
    revert(id: SnapshotId): Promise<boolean>;
    impersonate(address: Hex): Promise<void>;
    stopImpersonating(address: Hex): Promise<void>;
    /** Sends a transaction from an impersonated account at zero gas price. Returns the tx hash. */
    sendFrom(args: {from: Hex; to: Hex; value: bigint; data: Hex}): Promise<Hex>;
    /** Sets the next block's base fee. Used to make simulated gas free — see `sendFrom`. */
    setNextBlockBaseFee(wei: bigint): Promise<void>;
    traceTransaction(hash: Hex): Promise<TraceNode>;
}

export function createAnvilControl(client: PublicClient): AnvilControl {
    const rpc = rpcOf(client);
    return {
        async snapshot() {
            return (await rpc("evm_snapshot")) as SnapshotId;
        },
        async revert(id) {
            return (await rpc("evm_revert", [id])) as boolean;
        },
        async impersonate(address) {
            await rpc("anvil_impersonateAccount", [address]);
        },
        async stopImpersonating(address) {
            await rpc("anvil_stopImpersonatingAccount", [address]);
        },
        /**
         * Zero gas price, deliberately.
         *
         * In production the vault does not send its own transaction — a relayer submits the
         * receipt to `executeWithReceipt`, and the RELAYER pays gas. The vault's balance
         * changes by exactly the native value forwarded to the target. Simulating the vault
         * as the transaction sender at a normal gas price would charge it gas as well, so
         * the measured native-balance delta would not be the value transfer, and every
         * comparison against the mandate's `maxNativeValueWei` would be off by an amount
         * that depends on gas prices.
         *
         * Measured, not assumed: at the default base fee an impersonated sender's delta came
         * back as -42000000001000 for a 1000 wei transfer; with the base fee zeroed it is
         * exactly -1000. `setNextBlockBaseFee(0n)` is therefore called before every send.
         */
        async sendFrom({from, to, value, data}) {
            return (await rpc("eth_sendTransaction", [
                {from, to, value: `0x${value.toString(16)}`, data, gasPrice: "0x0"},
            ])) as Hex;
        },
        async setNextBlockBaseFee(wei) {
            await rpc("anvil_setNextBlockBaseFeePerGas", [`0x${wei.toString(16)}`]);
        },
        async traceTransaction(hash) {
            return (await rpc("debug_traceTransaction", [hash, {tracer: "callTracer"}])) as TraceNode;
        },
    };
}

/**
 * Every call in a trace, depth-first, excluding the top-level one.
 *
 * §5.7 makes "allowed top-level and internal call graph" a supported check and §3.3(11)
 * says unexpected internal calls are denied or reviewed by default. Both need the subcall
 * set, and DemoPay is documented as making no external calls at all — so for a conforming
 * purchase this returns an empty array, and anything else is a finding.
 */
export function internalCalls(root: TraceNode): TraceNode[] {
    const out: TraceNode[] = [];
    const walk = (node: TraceNode): void => {
        for (const child of node.calls ?? []) {
            out.push(child);
            walk(child);
        }
    };
    walk(root);
    return out;
}
