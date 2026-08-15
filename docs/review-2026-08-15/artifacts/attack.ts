/**
 * Adversarial attacks against the isolated signer, run over the real socket against a real
 * Anvil + compiled SentinelVault. Read-only w.r.t. the repository.
 */
import {keccak256, stringToBytes, encodeFunctionData} from "viem";
import {anvil} from "viem/chains";
import {connectSigner} from "../../../ts/src/signer/client.ts";
import type {Hex, EvaluateAndSignRequest} from "../../../ts/src/signer/protocol.ts";
import {
    OWNER, RESOURCE_ID,
    activate, buildCase1, deployStack, evidenceStub, startAnvil, startSignerProcess,
} from "../../../ts/test/harness.ts";

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

// =====================================================================
line("ATTACK 1: D-014 escape hatch — declare a target-binding decode failure");
// =====================================================================
// Case 3 shape: the calldata buys the WRONG resource. The mandate names weather-basic-24h.
// A truthful bundle would carry the decoded parameters and let D-010 detect the mismatch
// afterwards. Instead the bundle claims it could not decode, for a reason the signer is
// ratified not to opine on.
{
    const wrongResource = keccak256(stringToBytes("premium-monthly"));
    const s = await buildCase1(stack, {callDataArgs: {resourceId: wrongResource}});
    await activate(stack, s.mandateHash, s.policyHash);
    console.log("mandate.resourceId :", s.mandate.resourceId);
    console.log("calldata buys      :", wrongResource);
    console.log("action.target      :", s.action.target, "(the REAL DemoPay)");

    const lyingBundle = JSON.stringify({
        note: "bundle that declines to decode",
        decodedSelectorAndParameters: {
            decoded: "false",
            selector: stack.purchaseSelector,
            failureCode: "DECODE_UNSUPPORTED_TARGET",
        },
    });

    const r = await client.evaluateAndSign(req(s, "ALLOW", lyingBundle, await block()));
    console.log("signer result      :", r.refused ? `REFUSED ${JSON.stringify((r as any).blocking)}` : "SIGNED ALLOW");
    if (!r.refused) {
        console.log("signerFindings     :", JSON.stringify(r.signerFindings));
        console.log("evidenceHash       :", r.evidenceHash, "(commits to a bundle with NO parameters)");
        const hash = await stack.walletClient.writeContract({
            address: stack.vault, abi: stack.vaultAbi, functionName: "executeWithReceipt",
            args: [s.action, s.callData, r.receipt, r.signature], account: OWNER, chain: anvil,
        });
        const rc = await stack.publicClient.waitForTransactionReceipt({hash});
        console.log("vault execution    :", rc.status);
        const exp = await stack.publicClient.readContract({
            address: stack.demoPay, abi: stack.demoPayAbi, functionName: "entitlementExpiry",
            args: [OWNER.address, wrongResource],
        });
        console.log("wrong entitlement  :", exp, exp > 0n ? "<-- LANDED ONCHAIN" : "");
    }
}

// =====================================================================
line("ATTACK 1b: control — same lie with a NON-target failure code");
// =====================================================================
{
    const s = await buildCase1(stack);
    await activate(stack, s.mandateHash, s.policyHash);
    const lying = JSON.stringify({
        decodedSelectorAndParameters: {
            decoded: "false", selector: stack.purchaseSelector, failureCode: "DECODE_UNKNOWN_SELECTOR",
        },
    });
    const r = await client.evaluateAndSign(req(s, "ALLOW", lying, await block()));
    console.log("result:", r.refused ? `REFUSED ${JSON.stringify((r as any).blocking.map((x: any) => x.code))}` : "SIGNED");
}

// =====================================================================
line("ATTACK 1c: escape hatch with an EMPTY bundle otherwise");
// =====================================================================
{
    const s = await buildCase1(stack);
    await activate(stack, s.mandateHash, s.policyHash);
    const minimal = JSON.stringify({
        decodedSelectorAndParameters: {decoded: "false", failureCode: "DECODE_SELECTOR_TARGET_MISMATCH"},
    });
    const r = await client.evaluateAndSign(req(s, "ALLOW", minimal, await block()));
    console.log("bundle:", minimal);
    console.log("result:", r.refused ? `REFUSED ${JSON.stringify((r as any).blocking.map((x: any) => x.code))}` : "SIGNED ALLOW with zero evidence");
}

// =====================================================================
line("ATTACK 2: D-014 boundary — selector that does not belong at the target");
// =====================================================================
{
    // approve() calldata aimed at DemoPay. The mandate is edited to name the approve
    // selector so the signer's mandate checks pass; the bundle truthfully describes the
    // bytes given the selector.
    const approveData = encodeFunctionData({
        abi: stack.demoErc20Abi, functionName: "approve",
        args: ["0x000000000000000000000000000000000000dEaD", (1n << 256n) - 1n],
    }) as Hex;
    const s = await buildCase1(stack, {mandate: {selector: stack.approveSelector}});
    // rebuild action/callData by hand for the approve bytes at the DemoPay target
    const s2 = {
        ...s,
        callData: approveData,
        action: {...s.action, dataHash: keccak256(Buffer.from(approveData.slice(2), "hex"))},
    };
    await activate(stack, s.mandateHash, s.policyHash);
    const r = await client.evaluateAndSign(
        req(s2, "ALLOW", evidenceStub("approve at DemoPay", approveData), await block()),
    );
    console.log("target :", s2.action.target, "(DemoPay)");
    console.log("bytes  : DemoERC20.approve(0xdead, MAX_UINT256)");
    console.log("result :", r.refused ? `REFUSED ${JSON.stringify((r as any).blocking.map((x: any) => x.code))}` : "SIGNED ALLOW");
    if (!r.refused) console.log("findings:", JSON.stringify(r.signerFindings));
}

// =====================================================================
line("ATTACK 3: does a live REVIEW reservation block a later different ALLOW?");
// =====================================================================
{
    const a = await buildCase1(stack, {callDataArgs: {duration: 3600n}});
    await activate(stack, a.mandateHash, a.policyHash);
    const ra = await client.evaluateAndSign(req(a, "REVIEW", evidenceStub("r", a.callData), await block()));
    console.log("REVIEW for action A:", ra.refused ? "refused" : "signed");

    const b = await buildCase1(stack, {callDataArgs: {duration: 7200n}});
    await activate(stack, b.mandateHash, b.policyHash);
    const rb = await client.evaluateAndSign(req(b, "ALLOW", evidenceStub("a", b.callData), await block()));
    console.log("ALLOW for action B :", rb.refused
        ? `refused ${JSON.stringify((rb as any).blocking.map((x: any) => x.code))}`
        : "SIGNED — two live executable credentials at one nonce");
}

// =====================================================================
line("ATTACK 4: is a second REVIEW at a held nonce refused?");
// =====================================================================
{
    const a = await buildCase1(stack, {callDataArgs: {duration: 111n}});
    await activate(stack, a.mandateHash, a.policyHash);
    const ra = await client.evaluateAndSign(req(a, "ALLOW", evidenceStub("r", a.callData), await block()));
    console.log("ALLOW for A :", ra.refused ? "refused" : "signed");
    const b = await buildCase1(stack, {callDataArgs: {duration: 222n}});
    await activate(stack, b.mandateHash, b.policyHash);
    const rb = await client.evaluateAndSign(req(b, "REVIEW", evidenceStub("r", b.callData), await block()));
    console.log("REVIEW for B:", rb.refused
        ? `refused ${JSON.stringify((rb as any).blocking.map((x: any) => x.code))}`
        : "SIGNED — REVIEW is overridable, so this is a second live credential");
}

// =====================================================================
line("ATTACK 5: raw __proto__ over the wire (bypassing JS literal semantics)");
// =====================================================================
{
    const {connect} = await import("node:net");
    const sock = connect(signer.socketPath);
    sock.setEncoding("utf8");
    await new Promise<void>((res) => sock.once("connect", () => res()));
    const ask = (raw: string) => new Promise<string>((res) => {
        sock.once("data", (l: string) => res(l.trim()));
        sock.write(raw + "\n");
    });
    const s = await buildCase1(stack);
    const wire = (o: unknown) => JSON.parse(JSON.stringify(o, (_k, v) => typeof v === "bigint" ? v.toString() : v));
    const params: any = {
        action: wire(s.action), callData: s.callData, mandate: wire(s.mandate), policy: wire(s.policy),
        evaluation: {verdict: "ALLOW", reasonCodes: [], evidenceCanonical: evidenceStub("x", s.callData),
            simulationBlockNumber: (await block()).number.toString(), simulationBlockHash: (await block()).hash},
    };
    const withProto = JSON.stringify({id: 1, method: "evaluateAndSign", params})
        .replace('"action":{', '"action":{"__proto__":{"valueWei":"999999999999999999"},');
    console.log("raw __proto__ inside action ->", (await ask(withProto)).slice(0, 200));
    sock.destroy();
}

await client.close().catch(() => {});
signer.stop();
node.stop();
process.exit(0);
