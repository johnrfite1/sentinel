/**
 * F1-C: the same escape hatch, aimed at the attack D-042(b) says has NOTHING behind the
 * evaluator — an unlimited ERC-20 approval out of the vault.
 *
 * D-042(b): "the vault caps native value only ... So that attack is refused by the
 * CONFORMANCE EVALUATOR with nothing behind it." D-014's decoded-parameter attestation is the
 * one thing that would leave a trace of it in the signed record. This turns that off.
 */
import {encodeFunctionData, keccak256, toBytes} from "viem";
import {anvil} from "viem/chains";
import {connectSigner} from "../src/signer/client.ts";
import type {Hex, EvaluateAndSignRequest} from "../src/signer/protocol.ts";
import {decodeBySelector} from "../src/decode/index.ts";
import {
    OWNER, activate, buildCase1, deployStack, startAnvil, startSignerProcess,
} from "../test/harness.ts";

const node = await startAnvil();
const stack = await deployStack(node.rpcUrl);
const signer = await startSignerProcess({rpcUrl: node.rpcUrl, vault: stack.vault});
const client = await connectSigner(signer.socketPath);

// Give the vault a token balance to steal.
await stack.publicClient.waitForTransactionReceipt({
    hash: await stack.walletClient.writeContract({
        address: stack.demoErc20, abi: stack.demoErc20Abi, functionName: "transfer",
        args: [stack.vault, 10n ** 21n], account: OWNER, chain: anvil,
    }),
});

const SPENDER: Hex = "0x000000000000000000000000000000000000dead";
const MAX = (1n << 256n) - 1n;
const approveData = encodeFunctionData({
    abi: stack.demoErc20Abi, functionName: "approve", args: [SPENDER, MAX],
}) as Hex;
const padded = `${approveData}${"00".repeat(32)}` as Hex;

const erc20Code = await stack.publicClient.getCode({address: stack.demoErc20});
const s0 = await buildCase1(stack, {
    mandate: {
        target: stack.demoErc20,
        selector: stack.approveSelector,
        targetCodeHash: keccak256(toBytes(erc20Code ?? "0x")),
    },
});
const s = {
    ...s0,
    callData: padded,
    action: {
        ...s0.action,
        target: stack.demoErc20,
        valueWei: 0n,
        dataHash: keccak256(toBytes(padded)),
    },
};
await activate(stack, s.mandateHash, s.policyHash);

console.log("calldata                :", "DemoERC20.approve(0xdead, MAX_UINT256) + 32 trailing bytes");
console.log("signer's own decode     :", JSON.stringify(decodeBySelector(padded)));
console.log("policy.maxAllowanceIncreaseBaseUnits:", s.policy.maxAllowanceIncreaseBaseUnits.toString());
console.log("vault token balance     :", await stack.publicClient.readContract({
    address: stack.demoErc20, abi: stack.demoErc20Abi, functionName: "balanceOf", args: [stack.vault],
}));

const lie = JSON.stringify({
    note: "unable to decode",
    decodedSelectorAndParameters: {
        decoded: "false", selector: stack.approveSelector, failureCode: "DECODE_LENGTH_MISMATCH",
    },
});
const b = await stack.publicClient.getBlock();
const r = await client.evaluateAndSign({
    action: s.action, callData: s.callData, mandate: s.mandate, policy: s.policy,
    evaluation: {
        verdict: "ALLOW", reasonCodes: [], evidenceCanonical: lie,
        simulationBlockNumber: b.number, simulationBlockHash: b.hash!.toLowerCase() as Hex,
    },
} as EvaluateAndSignRequest);

console.log("signer result           :", r.refused
    ? `REFUSED ${JSON.stringify((r as any).blocking.map((x: any) => x.code))}`
    : "SIGNED ALLOW");

if (!r.refused) {
    console.log("signerFindings          :", JSON.stringify(r.signerFindings));
    const hash = await stack.walletClient.writeContract({
        address: stack.vault, abi: stack.vaultAbi, functionName: "executeWithReceipt",
        args: [s.action, s.callData, r.receipt, r.signature], account: OWNER, chain: anvil,
    });
    const rc = await stack.publicClient.waitForTransactionReceipt({hash});
    console.log("vault execution         :", rc.status);
    const allowance = await stack.publicClient.readContract({
        address: stack.demoErc20, abi: stack.demoErc20Abi, functionName: "allowance",
        args: [stack.vault, SPENDER],
    });
    console.log("allowance(vault→0xdead) :", allowance, allowance === MAX ? "<-- UNLIMITED, ONCHAIN" : "");
}

await client.close().catch(() => {});
signer.stop();
node.stop();
process.exit(0);
