import type {PublicClient} from "viem";
import {createAnvilControl, internalCalls, type AnvilControl, type TraceNode} from "./anvil.ts";
import type {DecodedCall} from "../decode/index.ts";
import type {Hex} from "../signer/protocol.ts";

/**
 * The anchored snapshot / execute / inspect / revert pipeline (§9 step 5, §3.2 steps 8–9).
 *
 * §3.2: "A local Anvil fork is anchored to a recorded block hash. Sentinel snapshots,
 * executes, inspects supported pre/post effects and call traces, then reverts the
 * snapshot." This module is that sentence, and its correctness rests on three properties
 * that are easier to state than to keep true through later edits.
 *
 * 1. IT ALWAYS REVERTS. The revert is in a `finally`, and a failed revert is escalated
 *    rather than logged. A simulation that leaks state does not merely produce one wrong
 *    answer — it silently poisons every later simulation on the same chain, including the
 *    ones in the fixture corpus that the whole evaluation harness is supposed to be
 *    evidence from. This is the single most important line in the file.
 *
 * 2. IT EXECUTES AS THE VAULT. The vault performs `target.call{value}(data)`, so `msg.sender`
 *    during the real execution is the vault, and the simulation impersonates it. Not a
 *    detail: `DemoPay.purchase` records `buyer = msg.sender`, and `DemoERC20.approve` sets
 *    `allowance[msg.sender][spender]` — which is precisely why the Case 2 injection is
 *    dangerous. Simulating from any other account would measure an allowance nobody can
 *    spend and report the attack as harmless.
 *
 * 3. IT NEVER TOPS UP THE VAULT. No `anvil_setBalance` on the account under test. If the
 *    vault cannot afford the call, the simulation must show that revert, because that is
 *    what would happen. Funding it to "make the simulation work" would convert a real
 *    failure into a fabricated success.
 *
 * WHAT THIS PRODUCES AND WHAT IT DOES NOT. Effects, not verdicts. Nothing here consults a
 * mandate or a policy; comparing observed effects against the signed mandate is the
 * conformance evaluator (§9 step 6). `unresolvedChecks` is the channel for things this
 * layer could not establish — §5.6 declares that field, and §3.3(8) requires that a
 * critical dependency failure never produce an automatic allow, so an unresolved check has
 * to travel rather than be swallowed.
 *
 * CLAIMS BOUNDARY (§8, as amended by D-001). These are SIMULATED effects at a recorded
 * block, not observed post-execution effects. The recorded anchor is what makes that claim
 * auditable rather than rhetorical, and it is why the receipt carries the block number and
 * hash the signer independently re-checks against the chain.
 */

const ERC20_ALLOWANCE_ABI = [
    {
        type: "function",
        name: "allowance",
        stateMutability: "view",
        inputs: [{type: "address"}, {type: "address"}],
        outputs: [{type: "uint256"}],
    },
] as const;

const DEMOPAY_STATE_ABI = [
    {
        type: "function",
        name: "entitlementExpiry",
        stateMutability: "view",
        inputs: [{type: "address"}, {type: "bytes32"}],
        outputs: [{type: "uint64"}],
    },
    {
        type: "function",
        name: "recurringEnabled",
        stateMutability: "view",
        inputs: [{type: "address"}, {type: "bytes32"}],
        outputs: [{type: "bool"}],
    },
] as const;

export interface Anchor {
    blockNumber: bigint;
    blockHash: Hex;
}

export interface NativeBalanceDelta {
    address: Hex;
    before: bigint;
    after: bigint;
    delta: bigint;
}

export interface AllowanceDelta {
    token: Hex;
    owner: Hex;
    spender: Hex;
    before: bigint;
    after: bigint;
    delta: bigint;
}

export interface EntitlementState {
    contract: Hex;
    beneficiary: Hex;
    resourceId: Hex;
    expiryBefore: bigint;
    expiryAfter: bigint;
    recurringBefore: boolean;
    recurringAfter: boolean;
}

export interface EmittedEvent {
    address: Hex;
    topics: Hex[];
    data: Hex;
}

export interface SimulationResult {
    anchor: Anchor;
    outcome: {status: "success" | "revert"; revertReason: string | null};
    gasUsed: bigint;
    nativeBalanceDeltas: NativeBalanceDelta[];
    allowanceDeltas: AllowanceDelta[];
    entitlements: EntitlementState[];
    /** §5.7: "emitted events as supporting evidence" — never proof of entitlement on their own. */
    events: EmittedEvent[];
    callTrace: TraceNode | null;
    /** Subcalls beneath the top-level call. Empty is the conforming shape for DemoPay. */
    internalCalls: {from: Hex; to: Hex | null; type: string}[];
    /** §5.6. Anything this layer could not establish. Never silently dropped. */
    unresolvedChecks: string[];
}

export interface SimulateArgs {
    client: PublicClient;
    vault: Hex;
    target: Hex;
    valueWei: bigint;
    callData: Hex;
    /** Decoded parameters, when the call decoded. Drives which typed effects are inspected. */
    decoded: DecodedCall | null;
    /** Extra addresses to watch for native balance movement. */
    watchAddresses?: Hex[];
    control?: AnvilControl;
}

export class SimulationLeakError extends Error {}

/**
 * Serialises simulations on this process.
 *
 * WHY THE HEADLINE INVARIANT NEEDED THIS. "It always reverts" is only true one snapshot at a
 * time. Anvil's `evm_revert` DISCARDS snapshots taken after the one being reverted, so two
 * overlapping snapshot/revert windows cannot both be isolated. A D-017 adjudicator reproduced
 * both consequences on a real node: an `approve` simulation whose own `valueWei` was 0
 * reported the vault at -1000 wei — the other simulation's value, captured because its
 * post-state read straddled the other transaction — and `SimulationLeakError` fired on a
 * demonstrably clean chain, 11 times out of 11 in one sweep. A false leak alarm is
 * particularly corrosive here, because the alarm exists to make a real leak unmissable.
 *
 * Nothing in the API or the tests previously enforced serial use; it was true only by
 * convention, and conventions do not survive a caller who reads the type signature. This
 * queue makes the documented invariant a property of the code.
 *
 * HONEST LIMIT: per-process, like the signer's nonce guard (D-013). Two processes simulating
 * against one node still collide, and no lock here can prevent that — the node is the shared
 * resource. Run one simulator per chain.
 */
let simulationQueue: Promise<unknown> = Promise.resolve();

function serialise<T>(work: () => Promise<T>): Promise<T> {
    const run = simulationQueue.then(work, work);
    // Swallow rejection on the CHAIN only, so one failed simulation does not reject the next
    // caller's turn. The original promise still rejects to its own caller.
    simulationQueue = run.then(
        () => undefined,
        () => undefined,
    );
    return run;
}

/**
 * Run one action against a snapshot and return its effects, leaving the chain as found.
 */
export async function simulateAction(args: SimulateArgs): Promise<SimulationResult> {
    return serialise(() => runSimulation(args));
}

async function runSimulation(args: SimulateArgs): Promise<SimulationResult> {
    const {client, vault, target, valueWei, callData, decoded} = args;
    const control = args.control ?? createAnvilControl(client);
    const unresolvedChecks: string[] = [];

    // The anchor is recorded BEFORE anything mutates (§3.2 step 8). Executing mines a block;
    // reverting returns here, so this block and its hash still exist afterwards — which is
    // what lets the isolated signer independently re-check `simulationBlockHash`.
    //
    // WHAT THIS DOES **NOT** ESTABLISH, corrected 2026-08-19 (R2-F1, D-055(e), CONFIRMED;
    // accepted as a bounded limitation at D-057(6)). The earlier wording said the anchor
    // "names the state the verdict is computed against". **It does not, locally.** This
    // `getBlock()` is unpinned and every state read below carries no `blockNumber`, so if the
    // head advances mid-simulation the anchor names one block and the effects were measured at
    // another. **This module cannot establish the property on its own.**
    //
    // WHAT MAKES THIS SOUND LIVES IN ANOTHER COMPONENT, and that dependency is now recorded rather
    // than left implicit: the anchor is taken before every read and the signer runs after the
    // revert, so anchor <= effects <= signer, and the signer's E3 check requires its own
    // observed block to EQUAL this anchor. A straddled simulation therefore fails that equality
    // and is REFUSED — `SIGNER_ANCHOR_NOT_OBSERVED`, no receipt issued.
    //
    // So the residual is a LIVENESS one, not an authorization one: a caller whose simulation
    // crossed a block boundary must re-simulate. Nothing can attest to straddled effects.
    const anchorBlock = await client.getBlock();
    const anchor: Anchor = {
        blockNumber: anchorBlock.number,
        blockHash: anchorBlock.hash.toLowerCase() as Hex,
    };

    const watched = [
        ...new Set(
            [vault, target, ...(args.watchAddresses ?? []), beneficiaryOf(decoded)]
                .filter((a): a is Hex => a !== null)
                .map((a) => a.toLowerCase() as Hex),
        ),
    ];

    const snapshotId = await control.snapshot();
    let reverted = false;

    try {
        const before = await readState(client, watched, vault, target, decoded);

        await control.impersonate(vault);

        let txHash: Hex | null = null;
        let status: "success" | "revert" = "revert";
        let revertReason: string | null = null;
        let gasUsed = 0n;
        let events: EmittedEvent[] = [];
        let revertedTxHash: Hex | null = null;

        try {
            // Gas is made free before sending so the measured native delta is the value
            // transfer alone. In production a relayer pays gas, not the vault; see
            // `sendFrom` for the measurement behind this. Inside the snapshot, so the revert
            // restores the real fee market along with everything else.
            await control.setNextBlockBaseFee(0n);
            txHash = await control.sendFrom({from: vault, to: target, value: valueWei, data: callData});
            const receipt = await client.waitForTransactionReceipt({hash: txHash});
            status = receipt.status === "success" ? "success" : "revert";
            // The mined-and-reverted path is the DEFAULT for a contract revert, and it
            // previously left `revertReason` null while the datum sat in the trace. §7.1
            // makes "simulation revert" its own fixture class, so the reason is evidence.
            // The raw 4-byte custom-error selector is recorded as-is; mapping selectors to
            // error names needs a per-contract table and is S2 work.
            revertedTxHash = status === "revert" ? txHash : null;
            gasUsed = receipt.gasUsed;
            events = receipt.logs.map((l) => ({
                address: l.address.toLowerCase() as Hex,
                topics: l.topics as Hex[],
                data: l.data as Hex,
            }));
        } catch (err) {
            // A rejected send is a legitimate simulation outcome — an over-value call, a
            // revert at estimation, an unfunded vault. Recorded as the revert it is rather
            // than thrown, because §7.1 lists "simulation revert" as its own fixture class
            // with an expected verdict.
            status = "revert";
            revertReason = err instanceof Error ? err.message.split("\n")[0] ?? null : String(err);
        } finally {
            await control.stopImpersonating(vault).catch(() => {
                unresolvedChecks.push("SIM_STOP_IMPERSONATION_FAILED");
            });
        }

        let callTrace: TraceNode | null = null;
        let subcalls: {from: Hex; to: Hex | null; type: string}[] = [];
        if (txHash !== null) {
            try {
                callTrace = await control.traceTransaction(txHash);
                if (revertedTxHash !== null && revertReason === null) {
                    const raw = callTrace.revertReason ?? callTrace.output ?? null;
                    revertReason = raw === null || raw === "0x" ? null : `revert data ${raw}`;
                }
                subcalls = internalCalls(callTrace).map((c) => ({
                    from: c.from.toLowerCase() as Hex,
                    to: c.to === undefined ? null : (c.to.toLowerCase() as Hex),
                    type: c.type,
                }));
            } catch {
                // §3.3(8): a missing trace is missing evidence, and missing evidence must
                // reach the evaluator rather than be inferred as "no internal calls".
                unresolvedChecks.push("SIM_CALL_TRACE_UNAVAILABLE");
            }
        } else {
            unresolvedChecks.push("SIM_CALL_TRACE_UNAVAILABLE");
        }

        const after = await readState(client, watched, vault, target, decoded);

        return {
            anchor,
            outcome: {status, revertReason},
            gasUsed,
            nativeBalanceDeltas: watched.map((address, i) => {
                const b = before.balances[i] ?? 0n;
                const a = after.balances[i] ?? 0n;
                return {address, before: b, after: a, delta: a - b};
            }),
            allowanceDeltas:
                before.allowance === null || after.allowance === null
                    ? []
                    : [
                          {
                              ...before.allowance.key,
                              before: before.allowance.value,
                              after: after.allowance.value,
                              delta: after.allowance.value - before.allowance.value,
                          },
                      ],
            entitlements:
                before.entitlement === null || after.entitlement === null
                    ? []
                    : [
                          {
                              ...before.entitlement.key,
                              expiryBefore: before.entitlement.expiry,
                              expiryAfter: after.entitlement.expiry,
                              recurringBefore: before.entitlement.recurring,
                              recurringAfter: after.entitlement.recurring,
                          },
                      ],
            events,
            callTrace,
            internalCalls: subcalls,
            unresolvedChecks,
        };
    } finally {
        // THE LINE THAT MATTERS. A leaked simulation does not produce one wrong answer, it
        // corrupts every later one on this chain.
        reverted = await control.revert(snapshotId).catch(() => false);
        if (!reverted) {
            throw new SimulationLeakError(
                `evm_revert of snapshot ${snapshotId} failed. The chain may still carry this ` +
                    `simulation's effects, so every subsequent result on it is untrustworthy. ` +
                    `Restart the node rather than continuing.`,
            );
        }
    }
}

function beneficiaryOf(decoded: DecodedCall | null): Hex | null {
    if (decoded === null) return null;
    return decoded.schema === "DemoPay.purchase" ? decoded.beneficiary : decoded.spender;
}

interface StateSnapshot {
    balances: bigint[];
    allowance: {key: {token: Hex; owner: Hex; spender: Hex}; value: bigint} | null;
    entitlement: {
        key: {contract: Hex; beneficiary: Hex; resourceId: Hex};
        expiry: bigint;
        recurring: boolean;
    } | null;
}

/**
 * Read every supported pre/post quantity in one pass (§5.7 "supported effects").
 *
 * Called identically before and after, so a field that is unreadable is unreadable on both
 * sides and produces no delta rather than a fabricated one.
 */
async function readState(
    client: PublicClient,
    watched: Hex[],
    vault: Hex,
    target: Hex,
    decoded: DecodedCall | null,
): Promise<StateSnapshot> {
    const balances = await Promise.all(watched.map((address) => client.getBalance({address})));

    let allowance: StateSnapshot["allowance"] = null;
    let entitlement: StateSnapshot["entitlement"] = null;

    if (decoded?.schema === "DemoERC20.approve") {
        // owner is the VAULT, because the vault is what calls approve. An allowance granted
        // by anyone else is not the one the Case 2 attack creates.
        const key = {token: target, owner: vault, spender: decoded.spender};
        const value = (await client.readContract({
            address: target,
            abi: ERC20_ALLOWANCE_ABI,
            functionName: "allowance",
            args: [vault, decoded.spender],
        })) as bigint;
        allowance = {key, value};
    }

    if (decoded?.schema === "DemoPay.purchase") {
        const key = {
            contract: target,
            beneficiary: decoded.beneficiary,
            resourceId: decoded.resourceId,
        };
        const [expiry, recurring] = await Promise.all([
            client.readContract({
                address: target,
                abi: DEMOPAY_STATE_ABI,
                functionName: "entitlementExpiry",
                args: [decoded.beneficiary, decoded.resourceId],
            }) as Promise<bigint>,
            client.readContract({
                address: target,
                abi: DEMOPAY_STATE_ABI,
                functionName: "recurringEnabled",
                args: [decoded.beneficiary, decoded.resourceId],
            }) as Promise<boolean>,
        ]);
        entitlement = {key, expiry, recurring};
    }

    return {balances, allowance, entitlement};
}

export {createAnvilControl, internalCalls} from "./anvil.ts";
export type {AnvilControl, TraceNode} from "./anvil.ts";
