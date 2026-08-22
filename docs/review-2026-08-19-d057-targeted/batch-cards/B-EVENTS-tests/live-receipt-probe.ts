import {
    decodeEventLog,
    encodeFunctionData,
    keccak256,
    stringToBytes,
    toEventSelector,
    type Hex,
    type TransactionReceipt,
} from "viem";
import {anvil} from "viem/chains";
import {digest, domainSeparator, hashAction, hashOverride, hashReceipt} from "../src/signer/eip712.ts";
import type {DecisionReceiptPayload, OverrideAuthorizationPayload} from "../src/signer/protocol.ts";
import {
    OWNER,
    SIGNER,
    activate,
    artifact,
    buildCase1,
    deployStack,
    startAnvil,
    type Stack,
} from "./harness.ts";

const TOPICS = new Map([
    [toEventSelector("OverrideAuthorized(bytes32,bytes32,bytes32,bytes32,uint64)"), "OverrideAuthorized"],
    [toEventSelector("ActionExecuted(bytes32,uint256,bytes32,bool)"), "ActionExecuted"],
    [toEventSelector("Purchased(address,address,bytes32,uint64,bool,uint256,uint64)"), "Purchased"],
    [toEventSelector("Attempted(address,bool)"), "Attempted"],
]);

const json = (value: unknown) => JSON.stringify(value, (_key, item) => typeof item === "bigint" ? item.toString() : item);

interface Bundle {
    stack: Stack;
    payload: Hex;
}
async function bundle(rpcUrl: string, failing: boolean): Promise<Bundle> {
    const stack = await deployStack(rpcUrl);
    const scenario = await buildCase1(stack, failing ? {callDataArgs: {duration: 0n}} : {});
    await activate(stack, scenario.mandateHash, scenario.policyHash);

    const block = await stack.publicClient.getBlock();
    const actionHash = hashAction(scenario.action);
    const receipt: DecisionReceiptPayload = {
        schemaVersion: 1n,
        decisionId: keccak256(stringToBytes(failing ? "events-failing" : "events-success")),
        actionHash,
        mandateHash: scenario.action.mandateHash,
        policyHash: scenario.action.policyHash,
        verdict: 1n,
        reasonCodesHash: keccak256(stringToBytes("events-review-reasons")),
        evidenceHash: keccak256(stringToBytes("events-review-evidence")),
        simulationBlockNumber: block.number,
        simulationBlockHash: block.hash,
        issuedAt: block.timestamp,
        expiresAt: block.timestamp + 3600n,
        signer: SIGNER.address.toLowerCase() as Hex,
    };
    const receiptSig = await SIGNER.sign({
        hash: digest(domainSeparator(stack.chainId, stack.vault), hashReceipt(receipt)),
    });
    const auth: OverrideAuthorizationPayload = {
        schemaVersion: 1n,
        reviewReceiptHash: hashReceipt(receipt),
        actionHash,
        mandateHash: scenario.action.mandateHash,
        policyHash: scenario.action.policyHash,
        actionNonce: scenario.action.actionNonce,
        reasonHash: keccak256(stringToBytes("events-owner-reason")),
        issuedAt: block.timestamp,
        expiresAt: block.timestamp + 1800n,
    };
    const ownerSig = await OWNER.sign({
        hash: digest(domainSeparator(stack.chainId, stack.vault), hashOverride(auth)),
    });
    const payload = encodeFunctionData({
        abi: stack.vaultAbi,
        functionName: "executeWithOverride",
        args: [scenario.action, scenario.callData, receipt, receiptSig, auth, ownerSig],
    });
    return {stack, payload};
}

async function deployRelay(stack: Stack): Promise<{address: Hex; abi: ReturnType<typeof artifact>["abi"]}> {
    const relay = artifact("SentinelVault.events.t.sol", "BEventsRelay");
    const hash = await stack.walletClient.deployContract({
        abi: relay.abi,
        bytecode: relay.bytecode,
        account: OWNER,
        chain: anvil,
    });
    const receipt = await stack.publicClient.waitForTransactionReceipt({hash});
    if (receipt.contractAddress === null) throw new Error("relay deployment returned no address");
    return {address: receipt.contractAddress, abi: relay.abi};
}

function names(receipt: TransactionReceipt): string[] {
    return receipt.logs.map((log) => TOPICS.get(log.topics[0] ?? "0x") ?? "OTHER");
}

function vaultLogCount(receipt: TransactionReceipt, vault: Hex): number {
    return receipt.logs.filter((log) => log.address.toLowerCase() === vault.toLowerCase()).length;
}

async function nonce(stack: Stack): Promise<bigint> {
    return await stack.publicClient.readContract({
        address: stack.vault,
        abi: stack.vaultAbi,
        functionName: "actionNonce",
    }) as bigint;
}

async function direct(rpcUrl: string, failing: boolean) {
    const {stack, payload} = await bundle(rpcUrl, failing);
    const hash = await stack.walletClient.sendTransaction({
        to: stack.vault,
        data: payload,
        gas: 2_000_000n,
        account: OWNER,
        chain: anvil,
    });
    const receipt = await stack.publicClient.waitForTransactionReceipt({hash});
    return {
        status: receipt.status,
        logs: names(receipt),
        vaultLogCount: vaultLogCount(receipt, stack.vault),
        nonce: await nonce(stack),
    };
}

async function relayed(rpcUrl: string, failing: boolean, outerRevert: boolean) {
    const {stack, payload} = await bundle(rpcUrl, failing);
    const relay = await deployRelay(stack);
    const functionName = outerRevert ? "relayThenRevert" : "relay";
    const hash = await stack.walletClient.writeContract({
        address: relay.address,
        abi: relay.abi,
        functionName,
        args: [stack.vault, payload],
        gas: 2_500_000n,
        account: OWNER,
        chain: anvil,
    });
    const receipt = await stack.publicClient.waitForTransactionReceipt({hash});
    const attempted = receipt.logs.find((log) => log.address.toLowerCase() === relay.address.toLowerCase());
    let attemptedOk: boolean | null = null;
    if (attempted !== undefined && !outerRevert) {
        const decoded = decodeEventLog({abi: relay.abi, data: attempted.data, topics: attempted.topics});
        attemptedOk = (decoded.args as {ok: boolean}).ok;
    }
    return {
        status: receipt.status,
        logs: names(receipt),
        vaultLogCount: vaultLogCount(receipt, stack.vault),
        attemptedOk,
        nonce: await nonce(stack),
    };
}

const node = await startAnvil();
try {
    const results = {
        directSuccess: await direct(node.rpcUrl, false),
        directFailure: await direct(node.rpcUrl, true),
        relaySwallowsFailure: await relayed(node.rpcUrl, true, false),
        relaySuccess: await relayed(node.rpcUrl, false, false),
        ancestorRevertsAfterSuccess: await relayed(node.rpcUrl, false, true),
    };
    console.log(json(results));

    const ok =
        results.directSuccess.status === "success"
        && json(results.directSuccess.logs) === json(["OverrideAuthorized", "ActionExecuted", "Purchased"])
        && results.directSuccess.vaultLogCount === 2
        && results.directSuccess.nonce === 1n
        && results.directFailure.status === "reverted"
        && results.directFailure.logs.length === 0
        && results.directFailure.vaultLogCount === 0
        && results.directFailure.nonce === 0n
        && results.relaySwallowsFailure.status === "success"
        && json(results.relaySwallowsFailure.logs) === json(["Attempted"])
        && results.relaySwallowsFailure.vaultLogCount === 0
        && results.relaySwallowsFailure.attemptedOk === false
        && results.relaySwallowsFailure.nonce === 0n
        && results.relaySuccess.status === "success"
        && json(results.relaySuccess.logs) === json(["OverrideAuthorized", "ActionExecuted", "Purchased", "Attempted"])
        && results.relaySuccess.vaultLogCount === 2
        && results.relaySuccess.attemptedOk === true
        && results.relaySuccess.nonce === 1n
        && results.ancestorRevertsAfterSuccess.status === "reverted"
        && results.ancestorRevertsAfterSuccess.logs.length === 0
        && results.ancestorRevertsAfterSuccess.vaultLogCount === 0
        && results.ancestorRevertsAfterSuccess.nonce === 0n;
    if (!ok) throw new Error("durable-receipt matrix did not match the frozen boundary");
} finally {
    node.stop();
}
