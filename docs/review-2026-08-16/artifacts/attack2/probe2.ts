/** Round-2 probes against the real signer process over its real socket. */
import {keccak256, stringToBytes, toBytes} from "viem";
import {connect} from "node:net";
import {statSync} from "node:fs";
import {dirname} from "node:path";
import {connectSigner} from "../src/signer/client.ts";
import type {Hex, EvaluateAndSignRequest} from "../src/signer/protocol.ts";
import {
    OWNER, activate, buildCase1, deployStack, evidenceStub, startAnvil, startSignerProcess,
} from "../test/harness.ts";

const node = await startAnvil();
const stack = await deployStack(node.rpcUrl);
const signer = await startSignerProcess({rpcUrl: node.rpcUrl, vault: stack.vault});
const client = await connectSigner(signer.socketPath);

async function block() {
    const b = await stack.publicClient.getBlock();
    return {number: b.number, hash: b.hash.toLowerCase() as Hex};
}
const line = (t: string) => console.log(`\n──── ${t} ────`);
const wire = (o: unknown) =>
    JSON.parse(JSON.stringify(o, (_k, v) => (typeof v === "bigint" ? v.toString() : v)));

// raw socket so we can send things the typed client cannot express
const sock = connect(signer.socketPath);
sock.setEncoding("utf8");
await new Promise<void>((r) => sock.once("connect", () => r()));
let buf = "";
const waiters: ((s: string) => void)[] = [];
sock.on("data", (c: string) => {
    buf += c;
    let i: number;
    while ((i = buf.indexOf("\n")) !== -1) {
        const l = buf.slice(0, i);
        buf = buf.slice(i + 1);
        waiters.shift()?.(l);
    }
});
const ask = (raw: string) =>
    new Promise<string>((res) => {
        waiters.push(res);
        sock.write(raw + "\n");
    });

function params(s: any, verdict: string, evidence: string, b: any, extra: any = {}) {
    return {
        action: wire(s.action),
        callData: s.callData,
        mandate: wire(s.mandate),
        policy: wire(s.policy),
        evaluation: {
            verdict,
            reasonCodes: [],
            evidenceCanonical: evidence,
            simulationBlockNumber: b.number.toString(),
            simulationBlockHash: b.hash,
            ...extra.evaluation,
        },
        ...extra.top,
    };
}

// =====================================================================
line("P1: valueWei = 2^256 (parser has no uint256 bound) — is a refusal record emitted?");
{
    const s = await buildCase1(stack);
    await activate(stack, s.mandateHash, s.policyHash);
    const p: any = params(s, "ALLOW", evidenceStub("x", s.callData), await block());
    p.action.valueWei = (1n << 256n).toString();
    const out = await ask(JSON.stringify({id: 1, method: "evaluateAndSign", params: p}));
    console.log("response:", out.slice(0, 300));
    console.log("=> refusalRecord present?", out.includes("refusalRecord") ? "yes" : "NO — no signed refusal artifact");
}

// =====================================================================
line("P1b: same, but mandate.maxNativeValueWei out of range");
{
    const s = await buildCase1(stack);
    const p: any = params(s, "BLOCK", evidenceStub("x", s.callData), await block());
    p.mandate.maxNativeValueWei = (1n << 300n).toString();
    const out = await ask(JSON.stringify({id: 2, method: "evaluateAndSign", params: p}));
    console.log("response:", out.slice(0, 300));
}

// =====================================================================
line("P2: stale simulation anchor — genesis block, real hash, verdict ALLOW");
{
    const s = await buildCase1(stack);
    await activate(stack, s.mandateHash, s.policyHash);
    const g = await stack.publicClient.getBlock({blockNumber: 0n});
    const head = await stack.publicClient.getBlockNumber();
    const r = await client.evaluateAndSign({
        action: s.action, callData: s.callData, mandate: s.mandate, policy: s.policy,
        evaluation: {
            verdict: "ALLOW", reasonCodes: [], evidenceCanonical: evidenceStub("x", s.callData),
            simulationBlockNumber: 0n, simulationBlockHash: g.hash!.toLowerCase() as Hex,
        },
    } as EvaluateAndSignRequest);
    console.log("head block:", head, " anchored at: 0");
    console.log("result:", r.refused ? `REFUSED ${JSON.stringify((r as any).blocking.map((x: any) => x.code))}` : "SIGNED ALLOW");
    if (!r.refused) console.log("receipt.simulationBlockNumber:", r.receipt.simulationBlockNumber.toString());
}

// =====================================================================
line("P3: caller injects SIGNER_-namespaced reason codes into the signed reasonCodesHash");
{
    const s = await buildCase1(stack);
    await activate(stack, s.mandateHash, s.policyHash);
    const r = await client.evaluateAndSign({
        action: s.action, callData: s.callData, mandate: s.mandate, policy: s.policy,
        evaluation: {
            verdict: "ALLOW",
            reasonCodes: ["SIGNER_VAULT_PAUSED", "SIGNER_MANDATE_NOT_ACTIVE", "SIGNER_NOT_ACTIVE_SIGNER"],
            evidenceCanonical: evidenceStub("x", s.callData),
            simulationBlockNumber: (await block()).number,
            simulationBlockHash: (await block()).hash,
        },
    } as EvaluateAndSignRequest);
    console.log("result:", r.refused ? "REFUSED" : "SIGNED ALLOW");
    if (!r.refused) {
        console.log("receipt.verdict      :", r.receipt.verdict.toString(), "(2 = ALLOW)");
        console.log("committed reasonCodes:", JSON.stringify(r.reasonCodes));
        console.log("signerFindings (NOT in the signed payload):", JSON.stringify(r.signerFindings));
    }
}

// =====================================================================
line("P4: evidenceCanonical carrying a lone surrogate — signer hashes it anyway");
{
    const s = await buildCase1(stack);
    await activate(stack, s.mandateHash, s.policyHash);
    const stub = JSON.parse(evidenceStub("x", s.callData));
    const b = await block();
    // evidenceCanonical text carries a marker; after JSON.stringify of the whole envelope the
    // marker is replaced by the RAW six characters \ u d 8 0 0, so the signer's JSON.parse
    // yields a JS string holding a genuine unpaired surrogate.
    const send = async (escape: string, id: number) => {
        const p: any = params(s, "ALLOW", JSON.stringify({...stub, note: "paid Alice MARKER"}), b);
        const raw = JSON.stringify({id, method: "evaluateAndSign", params: p})
            .replace("MARKER", escape);
        return JSON.parse(await ask(raw));
    };
    const out1 = await send("\\ud800", 11);
    const out2 = await send("\\udbff", 12);
    console.log("bundle A (note: paid Alice \\ud800) ->", out1.ok ? out1.result.evidenceHash : JSON.stringify(out1));
    console.log("bundle B (note: paid Alice \\udbff) ->", out2.ok ? out2.result.evidenceHash : JSON.stringify(out2));
    console.log("two DIFFERENT bundles, one evidenceHash?",
        out1.ok && out2.ok && out1.result.evidenceHash === out2.result.evidenceHash);
}

// =====================================================================
line("P5: method enumeration + permissions (re-verifying A-016)");
{
    for (const m of ["sign", "signBytes", "signDigest", "signMessage", "signTypedData", "eth_sign",
        "personal_sign", "exportKey", "getPrivateKey", "describe", "probe", "keystore",
        "constructor", "__proto__", "toString", "evaluateandsign", "STATUS"]) {
        const out = await ask(JSON.stringify({id: 99, method: m, params: {}}));
        const j = JSON.parse(out);
        console.log(`  ${m.padEnd(18)} -> ${j.ok ? "OK!!!" : j.error.code}`);
    }
    console.log("socket mode :", (statSync(signer.socketPath).mode & 0o777).toString(8));
    console.log("dir mode    :", (statSync(dirname(signer.socketPath)).mode & 0o777).toString(8));
}

// =====================================================================
line("P6: does SENTINEL_SIGNER_KEY survive in the signer process environment?");
{
    console.log("(signer was started without an explicit key; see harness) source reported by status:");
    const st = await client.status();
    console.log("  status ->", JSON.stringify(st));
}

sock.destroy();
await client.close().catch(() => {});
signer.stop();
node.stop();
process.exit(0);
