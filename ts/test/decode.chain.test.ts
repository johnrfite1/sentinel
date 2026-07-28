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
import type {Hex} from "../src/signer/protocol.ts";
import {OWNER, artifact, startAnvil, type AnvilHandle} from "./harness.ts";

/**
 * The decoder against the real EVM.
 *
 * Two questions this answers that a unit test cannot, both of them about a claim the
 * decoder makes about itself.
 *
 * 1. IS THE DECODER EVER MORE PERMISSIVE THAN THE CHAIN? If calldata decodes cleanly here
 *    but the EVM refuses it — or worse, executes it as something else — then Sentinel would
 *    reason about parameters that are not what happens. This is the property that must
 *    never break, and it is asserted for every case below.
 *
 * 2. WHERE EXACTLY IS THE DECODER STRICTER, AND IS THAT LIST THE ONE WE THINK IT IS?
 *    `abi.ts` claims it is deliberately stricter than Solidity. Claims like that decay:
 *    someone adds a check, the comment stays, and the documented divergence no longer
 *    matches the real one. So the divergence is MEASURED here against the compiled
 *    contracts and asserted to be exactly one case — trailing bytes past the declared
 *    arguments, which Solidity ignores and Sentinel refuses.
 *
 *    That measurement corrected an assumption. Solidity was expected to be lenient about
 *    dirty address bits, non-canonical bools, and over-wide integers too; it is not — it
 *    reverts on all three. The decoder's strictness on those points is therefore agreement
 *    with the EVM, not an addition to it, and only the trailing-bytes case is a genuine
 *    Sentinel-only rule.
 *
 * The third test closes the loop differently: for well-formed calls it checks the decoded
 * parameters against the state the call actually writes. A decoder that reads the right
 * bytes into the wrong fields would pass every refusal test in the suite.
 */

let node: AnvilHandle;
let publicClient: PublicClient;
let walletClient: WalletClient;
let demoPay: Hex;
let demoErc20: Hex;
let demoPayAbi: Abi;
let demoErc20Abi: Abi;
let registry: TargetRegistry;

const RESOURCE: Hex = keccak256(stringToBytes("weather-basic-24h"));
const SPENDER: Hex = "0x5555555555555555555555555555555555555555";

before(async () => {
    node = await startAnvil();
    publicClient = createPublicClient({chain: anvil, transport: http(node.rpcUrl)});
    walletClient = createWalletClient({chain: anvil, account: OWNER, transport: http(node.rpcUrl)});

    const payArtifact = artifact("DemoPay.sol", "DemoPay");
    const ercArtifact = artifact("DemoERC20.sol", "DemoERC20");
    demoPayAbi = payArtifact.abi;
    demoErc20Abi = ercArtifact.abi;

    const deploy = async (art: {abi: Abi; bytecode: Hex}, args: unknown[]): Promise<Hex> => {
        const hash = await walletClient.deployContract({
            abi: art.abi,
            bytecode: art.bytecode,
            args: args as never,
            account: OWNER,
            chain: anvil,
        });
        const receipt = await publicClient.waitForTransactionReceipt({hash});
        return receipt.contractAddress!.toLowerCase() as Hex;
    };

    demoPay = await deploy(payArtifact, []);
    demoErc20 = await deploy(ercArtifact, [OWNER.address, 10n ** 24n]);
    registry = buildRegistry({[demoPay]: "DemoPay", [demoErc20]: "DemoERC20"});
});

after(() => {
    node?.stop();
});

const PURCHASE_ABI = [
    {
        type: "function",
        name: "purchase",
        stateMutability: "payable",
        inputs: [
            {type: "bytes32"},
            {type: "address"},
            {type: "uint64"},
            {type: "bool"},
        ],
        outputs: [],
    },
] as const;

function purchaseCalldata(
    beneficiary: Hex,
    duration = 86_400n,
    recurring = false,
    resource: Hex = RESOURCE,
): Hex {
    return encodeFunctionData({
        abi: PURCHASE_ABI,
        functionName: "purchase",
        args: [resource, beneficiary, duration, recurring],
    }) as Hex;
}

function withWord(callData: Hex, index: number, word: string): Hex {
    const body = callData.slice(10);
    return `${callData.slice(0, 10)}${body.slice(0, index * 64)}${word}${
        body.slice((index + 1) * 64)
    }` as Hex;
}

/** Does the REAL contract accept these bytes? Uses eth_call, so nothing is committed. */
async function chainAccepts(target: Hex, callData: Hex, value: bigint): Promise<boolean> {
    try {
        await publicClient.call({to: target, data: callData, value, account: OWNER.address});
        return true;
    } catch {
        return false;
    }
}

describe("decoder versus the real EVM", () => {
    it("is never more permissive than the chain, and is stricter in exactly one place", async () => {
        const owner = OWNER.address.toLowerCase() as Hex;
        const wellFormed = purchaseCalldata(owner);

        const cases: {name: string; callData: Hex}[] = [
            {name: "well-formed purchase", callData: wellFormed},
            {name: "trailing 32 bytes", callData: `${wellFormed}${"ff".repeat(32)}` as Hex},
            {name: "one argument word short", callData: wellFormed.slice(0, -64) as Hex},
            {
                name: "dirty address high bits",
                callData: withWord(wellFormed, 1, `ff${"00".repeat(11)}${owner.slice(2)}`),
            },
            {name: "bool encoded as 2", callData: withWord(wellFormed, 3, `${"00".repeat(31)}02`)},
            {
                name: "uint64 overflow",
                callData: withWord(wellFormed, 2, `${"00".repeat(23)}${"ff".repeat(9)}`),
            },
        ];

        const strictlySentinel: string[] = [];

        for (const c of cases) {
            const onChain = await chainAccepts(demoPay, c.callData, 1_000n);
            const decoded = decodeCall({target: demoPay, callData: c.callData, registry});

            // THE PROPERTY THAT MUST NEVER BREAK. If Sentinel decodes it, the EVM must
            // accept it — otherwise Sentinel is reasoning about a call that cannot happen.
            if (decoded.ok) {
                assert.equal(
                    onChain,
                    true,
                    `${c.name}: the decoder accepted calldata the chain rejects`,
                );
            }

            if (onChain && !decoded.ok) strictlySentinel.push(c.name);
        }

        // The measured divergence, asserted rather than described. Solidity ignores calldata
        // beyond the declared parameters; Sentinel refuses it, because those bytes are part
        // of what was proposed and `dataHash` binds them.
        assert.deepEqual(
            strictlySentinel,
            ["trailing 32 bytes"],
            "the set of cases where Sentinel is stricter than the EVM has changed — " +
                "update abi.ts's documented divergence, or reconsider the check that changed it",
        );
    });

    it("decodes parameters that predict the state the call actually writes", async () => {
        // A decoder that read the right bytes into the wrong fields would pass every refusal
        // test in this suite. This is the test that would catch it: decode first, execute
        // second, compare against contract state (§5.7 — "an event alone is not proof of
        // entitlement; conformance checks the resulting contract state").
        const beneficiary = OWNER.address.toLowerCase() as Hex;
        const duration = 3_600n;
        const resource = keccak256(stringToBytes("premium-monthly"));
        const callData = purchaseCalldata(beneficiary, duration, true, resource);

        const decoded = decodeCall({target: demoPay, callData, registry});
        assert.equal(decoded.ok, true);
        assert.deepEqual(decoded.decoded, {
            schema: "DemoPay.purchase",
            resourceId: resource,
            beneficiary,
            durationSeconds: duration,
            recurring: true,
        });

        const before = await publicClient.getBlock();
        const hash = await walletClient.sendTransaction({
            to: demoPay,
            data: callData,
            value: 1_000n,
            account: OWNER,
            chain: anvil,
        });
        await publicClient.waitForTransactionReceipt({hash});

        const expiry = (await publicClient.readContract({
            address: demoPay,
            abi: demoPayAbi,
            functionName: "entitlementExpiry",
            args: [beneficiary, resource],
        })) as bigint;
        const recurring = (await publicClient.readContract({
            address: demoPay,
            abi: demoPayAbi,
            functionName: "recurringEnabled",
            args: [beneficiary, resource],
        })) as boolean;

        // Every decoded field is observable in the resulting state: the resource and
        // beneficiary select the slot, the duration sets its expiry, the flag sets recurrence.
        assert.ok(expiry >= before.timestamp + duration, "duration did not land as decoded");
        assert.equal(recurring, true, "recurrence did not land as decoded");
    });

    it("decodes an approval whose spender and amount match the resulting allowance", async () => {
        // The Case 2 shape (A-009): attacker as spender, unlimited allowance.
        const amount = (1n << 256n) - 1n;
        const callData = encodeFunctionData({
            abi: demoErc20Abi,
            functionName: "approve",
            args: [SPENDER, amount],
        }) as Hex;

        const decoded = decodeCall({target: demoErc20, callData, registry});
        assert.equal(decoded.ok, true);
        assert.deepEqual(decoded.decoded, {
            schema: "DemoERC20.approve",
            spender: SPENDER.toLowerCase(),
            amount,
        });

        const hash = await walletClient.sendTransaction({
            to: demoErc20,
            data: callData,
            account: OWNER,
            chain: anvil,
        });
        await publicClient.waitForTransactionReceipt({hash});

        const allowance = (await publicClient.readContract({
            address: demoErc20,
            abi: demoErc20Abi,
            functionName: "allowance",
            args: [OWNER.address, SPENDER],
        })) as bigint;
        assert.equal(allowance, amount, "decoded approval did not match the allowance written");
    });
});
