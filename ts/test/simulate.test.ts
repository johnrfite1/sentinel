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

        assert.deepEqual(
            first.entitlements[0]!.expiryAfter - first.entitlements[0]!.expiryBefore,
            second.entitlements[0]!.expiryAfter - second.entitlements[0]!.expiryBefore,
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
