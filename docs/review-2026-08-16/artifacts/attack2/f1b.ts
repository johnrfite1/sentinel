/**
 * F1-B: the A-028 F1 escape hatch, through the branch the fix did not cover.
 *
 * checkEvidenceDecoding (ts/src/signer/attest.ts) has TWO returns under `decoded === "false"`.
 * A-028 F1 hardened the TARGET_BINDING_FAILURES one to refuse ALLOW. The sibling
 *     return mine.ok ? ["SIGNER_EVIDENCE_DECODING_MISMATCH"] : [];
 * still returns NO finding for ALLOW whenever the signer's own decode fails — and
 * ts/src/decode/abi.ts documents in its own header that trailing calldata bytes make this
 * decoder fail while the same bytes "execute normally onchain".
 */
import {keccak256, stringToBytes, toBytes} from "viem";
import {anvil} from "viem/chains";
import {connectSigner} from "../src/signer/client.ts";
import type {Hex, EvaluateAndSignRequest} from "../src/signer/protocol.ts";
import {decodeBySelector} from "../src/decode/index.ts";
import {
    OWNER, RESOURCE_ID,
    activate, buildCase1, deployStack, evidenceStub, startAnvil, startSignerProcess,
} from "../test/harness.ts";

const node = await startAnvil();
const stack = await deployStack(node.rpcUrl);
const signer = await startSignerProcess({rpcUrl: node.rpcUrl, vault: stack.vault});
const client = await connectSigner(signer.socketPath);

async function block() {
    const b = await stack.publicClient.getBlock();
    return {number: b.number, hash: b.hash.toLowerCase() as Hex};
}

function req(s: any, verdict: "ALLOW" | "REVIEW" | "BLOCK", evidence: string, b: any): EvaluateAndSignRequest {
    return {
        action: s.action, callData: s.callData, mandate: s.mandate, policy: s.policy,
        evaluation: {
            verdict, reasonCodes: [], evidenceCanonical: evidence,
            simulationBlockNumber: b.number, simulationBlockHash: b.hash,
        },
    };
}

const line = (t: string) => console.log(`\n──── ${t} ────`);

line("F1-B: non-target failureCode + calldata the signer cannot decode");

const WRONG = keccak256(stringToBytes("premium-monthly"));
const s0 = await buildCase1(stack, {callDataArgs: {resourceId: WRONG}});

// Same purchase, plus 32 bytes of trailing garbage. Solidity's external decoder ignores it;
// this repo's WordReader.forSchema throws DECODE_LENGTH_MISMATCH.
const padded = `${s0.callData}${"00".repeat(31)}2a` as Hex;
const s = {
    ...s0,
    callData: padded,
    action: {...s0.action, dataHash: keccak256(toBytes(padded))},
};

console.log("mandate.resourceId       :", s.mandate.resourceId);
console.log("calldata buys            :", WRONG);
console.log("callData length (bytes)  :", (padded.length - 2) / 2, "(4 + 4*32 + 32)");
console.log("signer's own decode      :", JSON.stringify(decodeBySelector(padded)));

await activate(stack, s.mandateHash, s.policyHash);

const lie = JSON.stringify({
    note: "bundle that declines to decode, for a reason INSIDE the signer's remit",
    decodedSelectorAndParameters: {
        decoded: "false",
        selector: stack.purchaseSelector,
        failureCode: "DECODE_LENGTH_MISMATCH",
    },
});
console.log("evidence bundle          :", lie);

const r = await client.evaluateAndSign(req(s, "ALLOW", lie, await block()));
console.log("signer result            :", r.refused
    ? `REFUSED ${JSON.stringify((r as any).blocking.map((x: any) => x.code))}`
    : "SIGNED ALLOW");

if (!r.refused) {
    console.log("signerFindings           :", JSON.stringify(r.signerFindings));
    console.log("receipt.evidenceHash     :", r.evidenceHash, "(commits to a bundle with NO parameters)");
    console.log("receipt.verdict          :", r.receipt.verdict.toString(), "(2 = ALLOW)");
    const hash = await stack.walletClient.writeContract({
        address: stack.vault, abi: stack.vaultAbi, functionName: "executeWithReceipt",
        args: [s.action, s.callData, r.receipt, r.signature], account: OWNER, chain: anvil,
    });
    const rc = await stack.publicClient.waitForTransactionReceipt({hash});
    console.log("vault execution          :", rc.status);
    const wrongExp = await stack.publicClient.readContract({
        address: stack.demoPay, abi: stack.demoPayAbi, functionName: "entitlementExpiry",
        args: [OWNER.address, WRONG],
    });
    const rightExp = await stack.publicClient.readContract({
        address: stack.demoPay, abi: stack.demoPayAbi, functionName: "entitlementExpiry",
        args: [OWNER.address, RESOURCE_ID],
    });
    console.log("entitlement(premium)     :", wrongExp, wrongExp > 0n ? "<-- WRONG RESOURCE LANDED ONCHAIN" : "");
    console.log("entitlement(mandated)    :", rightExp);
}

// -------------------------------------------------------------------------
line("CONTROL: identical request, verdict REVIEW->ALLOW with the TARGET failureCode (A-028 F1 path)");
const s2 = await buildCase1(stack, {callDataArgs: {resourceId: WRONG}});
const padded2 = `${s2.callData}${"00".repeat(31)}2a` as Hex;
const s2p = {...s2, callData: padded2, action: {...s2.action, dataHash: keccak256(toBytes(padded2))}};
await activate(stack, s2.mandateHash, s2.policyHash);
const lie2 = JSON.stringify({
    decodedSelectorAndParameters: {
        decoded: "false", selector: stack.purchaseSelector, failureCode: "DECODE_UNSUPPORTED_TARGET",
    },
});
const r2 = await client.evaluateAndSign(req(s2p, "ALLOW", lie2, await block()));
console.log("target-code result       :", r2.refused
    ? `REFUSED ${JSON.stringify((r2 as any).blocking.map((x: any) => x.code))}`
    : "SIGNED ALLOW");

// -------------------------------------------------------------------------
line("CONTROL: truthful bundle for the same padded calldata");
const s3 = await buildCase1(stack, {callDataArgs: {resourceId: WRONG}});
const padded3 = `${s3.callData}${"00".repeat(31)}2a` as Hex;
const s3p = {...s3, callData: padded3, action: {...s3.action, dataHash: keccak256(toBytes(padded3))}};
await activate(stack, s3.mandateHash, s3.policyHash);
const r3 = await client.evaluateAndSign(req(s3p, "ALLOW", evidenceStub("honest", padded3), await block()));
console.log("honest-stub result       :", r3.refused
    ? `REFUSED ${JSON.stringify((r3 as any).blocking.map((x: any) => x.code))}`
    : `SIGNED ALLOW findings=${JSON.stringify((r3 as any).signerFindings)}`);

await client.close().catch(() => {});
signer.stop();
node.stop();
process.exit(0);
