import {after, before, describe, it} from "node:test";
import assert from "node:assert/strict";
import {
    createPublicClient,
    createWalletClient,
    encodeFunctionData,
    http,
    keccak256,
    stringToBytes,
    type Abi,
    type PublicClient,
    type WalletClient,
} from "viem";
import {anvil} from "viem/chains";
import {buildRegistry, decodeCall, type TargetRegistry} from "../src/decode/index.ts";
import {simulateAction} from "../src/simulate/index.ts";
import {createAnvilControl, internalCalls} from "../src/simulate/anvil.ts";
import type {Hex} from "../src/signer/protocol.ts";
import {OWNER, SIGNER, artifact, startAnvil, type AnvilHandle} from "./harness.ts";

/**
 * The effect pipeline against a real chain (§9 step 5).
 *
 * Every test here runs on a real Anvil with the real compiled contracts, because the
 * properties under test are properties of the node: that a snapshot really rewinds, that
 * impersonation really makes the vault the sender, that a trace really reports subcalls.
 * A mocked chain would assert my beliefs about Anvil rather than Anvil.
 *
 * The leak test is the important one. Everything else in the evaluation harness — the
 * fixture corpus above all — assumes each simulation leaves the chain exactly as it found
 * it. If that is false, results are not merely wrong, they are wrong in a way that depends
 * on execution order, which is the hardest kind of wrong to notice in a green suite.
 */

let node: AnvilHandle;
let publicClient: PublicClient;
let walletClient: WalletClient;
let demoPay: Hex;
let demoErc20: Hex;
let demoPayAbi: Abi;
let demoErc20Abi: Abi;
let registry: TargetRegistry;

/**
 * The real deployed SentinelVault, and it must be a CONTRACT rather than a convenient EOA.
 *
 * The first version of this file used an Anvil dev account as the vault stand-in. Anvil
 * holds keys for those, so it signed the simulated transaction natively and
 * `anvil_impersonateAccount` was dead code — a mutation replacing the impersonated account
 * entirely left the suite green. In production the vault is a contract, no node holds a key
 * for it, and impersonation is the only thing that makes the simulation execute as the
 * vault at all. Using the real contract is what makes this suite test the mechanism rather
 * than a coincidence of the fixture.
 */
let VAULT: Hex;
const ATTACKER: Hex = "0x00000000000000000000000000000000deadbeef";
const RESOURCE: Hex = keccak256(stringToBytes("weather-basic-24h"));

const PURCHASE_ABI = [
    {
        type: "function",
        name: "purchase",
        stateMutability: "payable",
        inputs: [{type: "bytes32"}, {type: "address"}, {type: "uint64"}, {type: "bool"}],
        outputs: [],
    },
] as const;

function purchaseCalldata(beneficiary: Hex, duration = 86_400n, recurring = false): Hex {
    return encodeFunctionData({
        abi: PURCHASE_ABI,
        functionName: "purchase",
        args: [RESOURCE, beneficiary, duration, recurring],
    }) as Hex;
}

before(async () => {
    node = await startAnvil();
    publicClient = createPublicClient({chain: anvil, transport: http(node.rpcUrl)});
    walletClient = createWalletClient({chain: anvil, account: OWNER, transport: http(node.rpcUrl)});

    const payArtifact = artifact("DemoPay.sol", "DemoPay");
    const ercArtifact = artifact("DemoERC20.sol", "DemoERC20");
    demoPayAbi = payArtifact.abi;
    demoErc20Abi = ercArtifact.abi;

    const deploy = async (
        art: {abi: Abi; bytecode: Hex},
        args: unknown[],
        value = 0n,
    ): Promise<Hex> => {
        const hash = await walletClient.deployContract({
            abi: art.abi,
            bytecode: art.bytecode,
            args: args as never,
            account: OWNER,
            chain: anvil,
            value,
        });
        return (await publicClient.waitForTransactionReceipt({hash})).contractAddress!.toLowerCase() as Hex;
    };

    // Deployed first so the demo contracts can be set up against it. Funded, because the
    // pipeline deliberately never tops the vault up: an unfunded vault must show its revert.
    VAULT = await deploy(
        artifact("SentinelVault.sol", "SentinelVault"),
        [OWNER.address, SIGNER.address, 10n ** 18n, [], []],
        10n ** 18n,
    );

    demoPay = await deploy(payArtifact, []);
    demoErc20 = await deploy(ercArtifact, [VAULT, 10n ** 24n]);
    registry = buildRegistry({[demoPay]: "DemoPay", [demoErc20]: "DemoERC20"});
});

after(() => {
    node?.stop();
});

function decodeFor(target: Hex, callData: Hex) {
    const result = decodeCall({target, callData, registry});
    assert.equal(result.ok, true);
    return result.decoded;
}

describe("the pipeline leaves no trace", () => {
    it("rewinds every effect it produced", async () => {
        const callData = purchaseCalldata(OWNER.address.toLowerCase() as Hex);

        const expiryBefore = (await publicClient.readContract({
            address: demoPay,
            abi: demoPayAbi,
            functionName: "entitlementExpiry",
            args: [OWNER.address, RESOURCE],
        })) as bigint;
        const balanceBefore = await publicClient.getBalance({address: VAULT});

        const result = await simulateAction({
            client: publicClient,
            vault: VAULT,
            target: demoPay,
            valueWei: 1_000n,
            callData,
            decoded: decodeFor(demoPay, callData),
        });

        // The simulation saw the effect...
        assert.equal(result.outcome.status, "success");
        assert.ok(result.entitlements[0]!.expiryAfter > result.entitlements[0]!.expiryBefore);

        // ...and the chain does not have it.
        const expiryAfter = (await publicClient.readContract({
            address: demoPay,
            abi: demoPayAbi,
            functionName: "entitlementExpiry",
            args: [OWNER.address, RESOURCE],
        })) as bigint;
        assert.equal(expiryAfter, expiryBefore, "the simulation leaked entitlement state");
        assert.equal(
            await publicClient.getBalance({address: VAULT}),
            balanceBefore,
            "the simulation leaked native balance",
        );
    });

    it("rewinds even when the simulated call reverts", async () => {
        // DemoPay reverts ZeroDuration. The revert path must still restore the snapshot —
        // a `finally` that only runs on success is the classic version of this bug.
        const callData = purchaseCalldata(OWNER.address.toLowerCase() as Hex, 0n);
        const before = await publicClient.getBlockNumber();

        const result = await simulateAction({
            client: publicClient,
            vault: VAULT,
            target: demoPay,
            valueWei: 1_000n,
            callData,
            decoded: decodeFor(demoPay, callData),
        });

        assert.equal(result.outcome.status, "revert");
        assert.equal(await publicClient.getBlockNumber(), before, "block height was not rewound");
    });

    it("is repeatable: the same simulation twice gives the same effects", async () => {
        // Only true if the first run left nothing behind. This is the property the fixture
        // corpus depends on, stated as a test rather than as a hope.
        const callData = purchaseCalldata(OWNER.address.toLowerCase() as Hex);
        const args = {
            client: publicClient,
            vault: VAULT,
            target: demoPay,
            valueWei: 1_000n,
            callData,
            decoded: decodeFor(demoPay, callData),
        };

        const first = await simulateAction(args);
        const second = await simulateAction(args);

        // A-072: THIS ASSERTION USED TO COMPARE THE WALL CLOCK AND FAILED ~1 RUN IN 11.
        //
        // It compared `expiryAfter - expiryBefore` across the two runs. Both are snapshot-
        // isolated, so `expiryBefore` is 0 in both and the quantity actually compared was
        // `block.timestamp + duration`. Anvil keeps block timestamps strictly increasing, so
        // the test failed whenever the two simulations straddled a second boundary — measured
        // at 2 failures in 22 runs by one round-six lens and hit again by another. **A test
        // that fails ~9% of the time for a reason unrelated to what it names is worse than no
        // test: its failure is indistinguishable from the leak it exists to detect**, and it
        // was the sole reason one lens's baseline was not green.
        //
        // THE PROPERTY IS ABOUT THE PRE-STATE, NOT THE POST-STATE. "The first run left nothing
        // behind" means the second simulation must OBSERVE the same starting chain as the
        // first. That is `expiryBefore`, and it is clock-independent. A leaked first run makes
        // the second's `expiryBefore` non-zero, which this still catches — falsified by
        // no-op'ing the snapshot revert, which fails this assertion.
        assert.equal(
            first.entitlements[0]!.expiryBefore,
            second.entitlements[0]!.expiryBefore,
            "the second simulation observed a different pre-state: the first run leaked",
        );
        // The granted duration is still pinned, without the absolute clock riding along.
        assert.equal(
            first.entitlements[0]!.expiryAfter - first.entitlements[0]!.expiryBefore > 0n,
            second.entitlements[0]!.expiryAfter - second.entitlements[0]!.expiryBefore > 0n,
        );
        assert.equal(first.anchor.blockNumber, second.anchor.blockNumber);
        assert.equal(first.anchor.blockHash, second.anchor.blockHash);
    });
});

describe("the anchor", () => {
    it("names a block that still exists and still hashes the same afterwards", async () => {
        // The isolated signer independently re-checks `simulationBlockHash` against the
        // chain (SIGNER_SIMULATION_BLOCK_MISMATCH), so an anchor that does not survive the
        // revert would make every receipt unsignable.
        const callData = purchaseCalldata(OWNER.address.toLowerCase() as Hex);
        const result = await simulateAction({
            client: publicClient,
            vault: VAULT,
            target: demoPay,
            valueWei: 1_000n,
            callData,
            decoded: decodeFor(demoPay, callData),
        });

        const block = await publicClient.getBlock({blockNumber: result.anchor.blockNumber});
        assert.equal(block.hash.toLowerCase(), result.anchor.blockHash);
    });
});

describe("effects observed as the vault", () => {
    it("attributes a purchase to the vault, not to whoever ran the simulation", async () => {
        // DemoPay records `buyer = msg.sender`. If the pipeline simulated from any other
        // account, the Purchased event would name the wrong buyer and native value would
        // leave the wrong balance.
        const beneficiary = OWNER.address.toLowerCase() as Hex;
        const callData = purchaseCalldata(beneficiary, 3_600n, true);

        const result = await simulateAction({
            client: publicClient,
            vault: VAULT,
            target: demoPay,
            valueWei: 5_000n,
            callData,
            decoded: decodeFor(demoPay, callData),
        });

        assert.equal(result.outcome.status, "success");

        const vaultDelta = result.nativeBalanceDeltas.find((d) => d.address === VAULT);
        assert.ok(vaultDelta !== undefined);
        // EXACTLY the value transfer, with no gas mixed in. In production a relayer submits
        // the receipt and pays gas; the vault's balance moves by `valueWei` alone. Asserting
        // equality rather than `< 0n` is what makes that model testable — the looser
        // assertion passed while the simulation was silently charging the vault for gas.
        assert.equal(vaultDelta.delta, -5_000n, "the vault must pay the value and nothing else");

        const targetDelta = result.nativeBalanceDeltas.find((d) => d.address === demoPay);
        assert.equal(targetDelta?.delta, 5_000n);

        const entitlement = result.entitlements[0]!;
        assert.equal(entitlement.beneficiary, beneficiary);
        assert.equal(entitlement.resourceId, RESOURCE);
        assert.equal(entitlement.recurringBefore, false);
        assert.equal(entitlement.recurringAfter, true, "recurrence is a bound, observable effect");

        assert.equal(result.events.length, 1, "Purchased is supporting evidence, not proof");
    });

    it("measures the Case 2 allowance the injection actually creates", async () => {
        // A-009: the injection proposed approve(attacker, max uint256). The dangerous
        // allowance is the VAULT's, so the pipeline must read allowance[vault][attacker].
        // Simulating from any other sender would report an allowance nobody can spend and
        // score the attack as harmless.
        const amount = (1n << 256n) - 1n;
        const callData = encodeFunctionData({
            abi: demoErc20Abi,
            functionName: "approve",
            args: [ATTACKER, amount],
        }) as Hex;

        const result = await simulateAction({
            client: publicClient,
            vault: VAULT,
            target: demoErc20,
            valueWei: 0n,
            callData,
            decoded: decodeFor(demoErc20, callData),
        });

        assert.equal(result.outcome.status, "success");
        const allowance = result.allowanceDeltas[0]!;
        assert.equal(allowance.owner, VAULT);
        assert.equal(allowance.spender, ATTACKER.toLowerCase());
        assert.equal(allowance.before, 0n);
        assert.equal(allowance.after, amount);
    });

    it("reports an empty internal call graph for a conforming purchase", async () => {
        // DemoPay is documented as making no external calls, and §5.7 makes the call graph a
        // supported check. Empty is the conforming shape; §3.3(11) reviews anything else.
        const callData = purchaseCalldata(OWNER.address.toLowerCase() as Hex);
        const result = await simulateAction({
            client: publicClient,
            vault: VAULT,
            target: demoPay,
            valueWei: 1_000n,
            callData,
            decoded: decodeFor(demoPay, callData),
        });

        assert.deepEqual(result.internalCalls, []);
        assert.notEqual(result.callTrace, null);
        assert.deepEqual(result.unresolvedChecks, []);
    });
});

describe("failure is reported, never inferred away", () => {
    it("records a revert as an outcome rather than throwing", async () => {
        // §7.1 lists "simulation revert" as its own fixture class with an expected verdict,
        // so it has to be a value the evaluator can read.
        const callData = purchaseCalldata(`0x${"00".repeat(20)}` as Hex);
        const result = await simulateAction({
            client: publicClient,
            vault: VAULT,
            target: demoPay,
            valueWei: 1_000n,
            callData,
            decoded: decodeFor(demoPay, callData),
        });
        assert.equal(result.outcome.status, "revert");
        assert.deepEqual(result.entitlements[0]!.expiryBefore, result.entitlements[0]!.expiryAfter);
    });

    it("surfaces a missing call trace as an unresolved check, not as 'no internal calls'", async () => {
        // §3.3(8): a critical dependency failure never produces an automatic allow. The
        // distinction matters — "the trace says there were no subcalls" and "there is no
        // trace" must not reach the evaluator as the same fact.
        const callData = purchaseCalldata(OWNER.address.toLowerCase() as Hex);
        const control = {
            ...(await import("../src/simulate/anvil.ts")).createAnvilControl(publicClient),
            async traceTransaction(): Promise<never> {
                throw new Error("tracer unavailable");
            },
        };

        const result = await simulateAction({
            client: publicClient,
            vault: VAULT,
            target: demoPay,
            valueWei: 1_000n,
            callData,
            decoded: decodeFor(demoPay, callData),
            control,
        });

        assert.equal(result.callTrace, null);
        assert.deepEqual(result.internalCalls, []);
        assert.ok(
            result.unresolvedChecks.includes("SIM_CALL_TRACE_UNAVAILABLE"),
            "a missing trace must travel to the evaluator",
        );
    });

    it("escalates a failed revert instead of returning a result", async () => {
        // The worst case: the simulation ran and the chain kept it. Returning normally here
        // would hand the evaluator a clean-looking result from a now-dirty chain.
        const callData = purchaseCalldata(OWNER.address.toLowerCase() as Hex);
        const real = (await import("../src/simulate/anvil.ts")).createAnvilControl(publicClient);
        let snapshotToRestore: string | null = null;

        const control = {
            ...real,
            async snapshot() {
                snapshotToRestore = await real.snapshot();
                return snapshotToRestore;
            },
            async revert(): Promise<boolean> {
                return false; // Anvil refused
            },
        };

        await assert.rejects(
            () =>
                simulateAction({
                    client: publicClient,
                    vault: VAULT,
                    target: demoPay,
                    valueWei: 1_000n,
                    callData,
                    decoded: decodeFor(demoPay, callData),
                    control,
                }),
            /every subsequent result on it is untrustworthy/,
        );

        // Put the chain back so the rest of the suite runs on clean state.
        assert.notEqual(snapshotToRestore, null);
        assert.equal(await real.revert(snapshotToRestore!), true);
    });
});

describe("concurrent simulations do not contaminate each other", () => {
    it("keeps overlapping simulations isolated, with no false leak alarm", async () => {
        // THE DEFECT THIS PROVES FIXED. Anvil's evm_revert DISCARDS snapshots taken after the
        // one being reverted, so two overlapping snapshot/revert windows cannot both be
        // isolated. A D-017 adjudicator reproduced both consequences on a real node: an
        // `approve` simulation whose own valueWei was 0 reported the vault at -1000 wei — the
        // OTHER simulation's value, captured because its post-state read straddled that
        // transaction — and SimulationLeakError fired on a demonstrably clean chain, 11 times
        // out of 11 in one sweep.
        //
        // "It always reverts" was therefore true only under serial use, which nothing
        // enforced. simulateAction now serialises. This test fires overlapping calls and
        // asserts each result reflects only its OWN action; without the queue it fails.
        const purchase = purchaseCalldata(OWNER.address.toLowerCase() as Hex);
        const approve = encodeFunctionData({
            abi: demoErc20Abi,
            functionName: "approve",
            args: [ATTACKER, (1n << 256n) - 1n],
        }) as Hex;

        const purchaseArgs = {
            client: publicClient,
            vault: VAULT,
            target: demoPay,
            valueWei: 1_000n,
            callData: purchase,
            decoded: decodeFor(demoPay, purchase),
        };
        const approveArgs = {
            client: publicClient,
            vault: VAULT,
            target: demoErc20,
            valueWei: 0n,
            callData: approve,
            decoded: decodeFor(demoErc20, approve),
        };

        // Four overlapping pairs. Launched without awaiting between them, so they genuinely
        // contend — the mistake of writing `await` inside the array literal is recorded as a
        // dead end in docs/session-state.md and is deliberately avoided here.
        const pending = [
            simulateAction(purchaseArgs),
            simulateAction(approveArgs),
            simulateAction(purchaseArgs),
            simulateAction(approveArgs),
        ];
        const results = await Promise.all(pending);

        for (const [i, r] of results.entries()) {
            const isPurchase = i % 2 === 0;
            const vaultDelta = r.nativeBalanceDeltas.find((d) => d.address === VAULT);
            assert.ok(vaultDelta !== undefined);
            assert.equal(
                vaultDelta.delta,
                isPurchase ? -1_000n : 0n,
                `simulation ${i} saw the other simulation's native movement`,
            );
            assert.equal(r.outcome.status, "success");
        }

        // And the chain is exactly as it was — no leak, and no false alarm either, since a
        // thrown SimulationLeakError would have rejected one of the promises above.
        const expiry = (await publicClient.readContract({
            address: demoPay,
            abi: demoPayAbi,
            functionName: "entitlementExpiry",
            args: [OWNER.address, RESOURCE],
        })) as bigint;
        assert.equal(expiry, 0n, "concurrent simulations leaked entitlement state");
    });
});

describe("internalCalls walks the whole trace, not just the top level (A-068)", () => {
    /**
     * Replacing this function's entire body with `return []` left ALL 426 tests green.
     *
     * Not an accident of coverage: every real trace in the suite is a vault→DemoPay call with
     * no subcalls, so the real walk and `return []` produce the same `[]`; the one non-empty
     * case in the suite is a hand-written override that never reaches the walker; and the
     * end-to-end assertion checks only that the key `internalCallTrace` is PRESENT in the
     * bundle, never its value. So `EVAL_CALL_GRAPH_EXPECTED` and §3.3(11)'s
     * unexpected-internal-call defence rested on a function nothing measured.
     *
     * These need no chain: `internalCalls` is a pure walk over a TraceNode, and the reason it
     * was untested is precisely that every test that could reach it needs anvil.
     */
    const node = (to: string, calls: any[] = []): any =>
        ({type: "CALL", from: "0x" + "11".repeat(20), to, input: "0x", calls});

    it("returns every descendant depth-first, excluding the root", () => {
        const root = node("0xaaa", [node("0xbbb", [node("0xccc")]), node("0xddd")]);
        const out = internalCalls(root);
        assert.deepEqual(out.map((c) => c.to), ["0xbbb", "0xccc", "0xddd"],
            "depth-first order, root excluded — `return []` and any non-recursive rewrite " +
            "both fail here");
    });

    it("recurses past the first level, which a one-level walk would not", () => {
        // Pinned separately: a rewrite that pushed `node.calls` without recursing would pass a
        // single-level assertion and miss exactly the nested call an attacker would use.
        const root = node("0xaaa", [node("0xbbb", [node("0xccc", [node("0xeee")])])]);
        assert.deepEqual(internalCalls(root).map((c) => c.to), ["0xbbb", "0xccc", "0xeee"]);
    });

    it("returns [] for a genuinely leaf call, which is the conforming case", () => {
        // The paired positive. Without it, a function that always returned a non-empty array
        // would satisfy both assertions above while breaking every conforming purchase.
        assert.deepEqual(internalCalls(node("0xaaa")), []);
    });
});

describe("the call graph PIPELINE is asserted end to end, not just its pure walk (A-072)", () => {
    /**
     * A-068 closed round five's `C-3` by pinning `internalCalls` — the pure walk — with three
     * unit tests. Round six then deleted the walk's INPUT and its OUTPUT with the whole suite
     * still green, because the walk was the only part anybody had pinned:
     *
     *   * `subcalls = internalCalls(callTrace).map(...)` -> `subcalls = []`   survived 481/481
     *   * `{tracer: "callTracer"}` -> `{tracer: "prestateTracer"}`            survived 481/481
     *
     * The second is the worse of the two. `prestateTracer` returns an account map with no
     * `calls` key at any depth AND DOES NOT ERROR, so `internalCalls` returns `[]` for every
     * transaction there can ever be and `SIM_CALL_TRACE_UNAVAILABLE` never fires. Silence
     * reads exactly like "this call made no internal calls" — failure mode 6, in the product
     * rather than in a probe.
     *
     * Neither is caught by any profile of the gate: `internalCallCount` is 0 in 46 of the 50
     * committed views and null in the other 4, and `internalCallTrace` is `[]` in all seven
     * sample bundles, so NO committed artifact carries a non-empty call graph to compare
     * against. `EVAL_CALL_GRAPH_EXPECTED` is a hard `require_(internalCalls.length === 0, ...)`,
     * so a producer that is always empty makes §3.3(11)'s defence pass unconditionally.
     *
     * These two tests pin the two ends. Both fail against the mutations above.
     */

    it("maps every descendant of the fetched trace into the result, not just the top level", async () => {
        // The control delegates everything to the real Anvil control except the trace, which is
        // replaced by a synthetic nested one. That isolates the MAPPING: the chain still runs
        // the transaction, and only the trace's shape is ours.
        const callData = purchaseCalldata(OWNER.address.toLowerCase() as Hex);
        const real = createAnvilControl(publicClient);
        const nested = {
            type: "CALL", from: "0x1111111111111111111111111111111111111111",
            to: "0x2222222222222222222222222222222222222222",
            calls: [
                {type: "STATICCALL", from: "0x2222222222222222222222222222222222222222",
                 to: "0x3333333333333333333333333333333333333333",
                 calls: [{type: "DELEGATECALL",
                          from: "0x3333333333333333333333333333333333333333",
                          to: "0x4444444444444444444444444444444444444444"}]},
            ],
        };
        const result = await simulateAction({
            client: publicClient,
            vault: VAULT,
            target: demoPay,
            valueWei: 1_000n,
            callData,
            decoded: decodeFor(demoPay, callData),
            control: {...real, traceTransaction: async () => nested as never},
        });

        // Depth-first, excluding the root, lower-cased, `to` preserved.
        assert.deepEqual(result.internalCalls, [
            {from: "0x2222222222222222222222222222222222222222",
             to: "0x3333333333333333333333333333333333333333", type: "STATICCALL"},
            {from: "0x3333333333333333333333333333333333333333",
             to: "0x4444444444444444444444444444444444444444", type: "DELEGATECALL"},
        ]);
        assert.deepEqual(result.unresolvedChecks, []);
    });

    it("asks the node for a callTracer trace, which is the only tracer that reports calls", async () => {
        // Pins the walk's INPUT. A tracer that returns no `calls` key produces an empty graph
        // for every transaction without erroring, so this cannot be left to the trace's shape.
        const seen: {method: string; params: unknown[]}[] = [];
        const stub = {
            request: async (a: {method: string; params: unknown[]}) => {
                seen.push(a);
                return {type: "CALL", from: "0x00", to: "0x00"};
            },
        } as unknown as PublicClient;

        await createAnvilControl(stub).traceTransaction("0xdeadbeef" as Hex);

        assert.equal(seen.length, 1);
        const call = seen[0]!;
        assert.equal(call.method, "debug_traceTransaction");
        assert.deepEqual(call.params[1], {tracer: "callTracer"});
    });
});
