/**
 * P9: SIGTERM shutdown with a live connection (the A-016 "two signers, one key" repair,
 * which ships with no regression test).
 * P10: refusal-record attributability for the non-contradictory FATAL structural findings.
 */
import {connect} from "node:net";
import {execFileSync} from "node:child_process";
import {connectSigner} from "../src/signer/client.ts";
import type {Hex} from "../src/signer/protocol.ts";
import {
    activate, buildCase1, deployStack, evidenceStub, startAnvil, startSignerProcess,
} from "../test/harness.ts";

const node = await startAnvil();
const stack = await deployStack(node.rpcUrl);
const line = (t: string) => console.log(`\n──── ${t} ────`);
const wire = (o: unknown) =>
    JSON.parse(JSON.stringify(o, (_k, v) => (typeof v === "bigint" ? v.toString() : v)));

// =====================================================================
line("P9: SIGTERM while an evaluator holds a persistent connection");
{
    const signer = await startSignerProcess({rpcUrl: node.rpcUrl, vault: stack.vault});
    const pid = parseInt(
        execFileSync("pgrep", ["-n", "-f", "src/signer/main.ts"]).toString().trim().split("\n")[0], 10);
    const client = await connectSigner(signer.socketPath);
    console.log("status ok:", (await client.status()).ready, " pid:", pid);
    const alive = () => {
        try { execFileSync("ps", ["-p", String(pid)], {stdio: "ignore"}); return true; } catch { return false; }
    };
    process.kill(pid, "SIGTERM");
    const t0 = Date.now();
    while (alive() && Date.now() - t0 < 12_000) await new Promise((r) => setTimeout(r, 100));
    console.log(`process alive ${Date.now() - t0}ms after SIGTERM:`, alive() ? "YES — still holding the key" : "no, exited");
    if (alive()) process.kill(pid, "SIGKILL");
    await client.close().catch(() => {});
    signer.stop();
}

// =====================================================================
line("P10: which FATAL structural findings leave a signed refusal record?");
{
    const signer = await startSignerProcess({rpcUrl: node.rpcUrl, vault: stack.vault});
    const s = await buildCase1(stack);
    await activate(stack, s.mandateHash, s.policyHash);
    const b = await stack.publicClient.getBlock();

    const sock = connect(signer.socketPath);
    sock.setEncoding("utf8");
    await new Promise<void>((r) => sock.once("connect", () => r()));
    let buf = "";
    const waiters: ((s: string) => void)[] = [];
    sock.on("data", (c: string) => {
        buf += c;
        let i: number;
        while ((i = buf.indexOf("\n")) !== -1) { const l = buf.slice(0, i); buf = buf.slice(i + 1); waiters.shift()?.(l); }
    });
    const ask = (raw: string) => new Promise<string>((res) => { waiters.push(res); sock.write(raw + "\n"); });

    const base = () => ({
        action: wire(s.action), callData: s.callData, mandate: wire(s.mandate), policy: wire(s.policy),
        evaluation: {
            verdict: "BLOCK", reasonCodes: [], evidenceCanonical: evidenceStub("x", s.callData),
            simulationBlockNumber: b.number.toString(), simulationBlockHash: (b.hash as Hex).toLowerCase(),
        },
    });

    const cases: [string, (p: any) => void][] = [
        ["SIGNER_WRONG_VAULT", (p) => { p.action.vault = "0x000000000000000000000000000000000000dead"; }],
        ["SIGNER_WRONG_CHAIN", (p) => { p.action.chainId = "999"; }],
        ["SIGNER_DATAHASH_MISMATCH", (p) => { p.action.dataHash = `0x${"11".repeat(32)}`; }],
        ["SIGNER_MANDATE_WINDOW (control: CONFORMANCE)", (p) => { p.mandate.validUntil = "1"; }],
        ["SIGNER_VAULT_PAUSED-ish (control: nonce)", (p) => { p.action.actionNonce = "4242"; }],
    ];
    for (const [name, mut] of cases) {
        const p = base();
        mut(p);
        const out = JSON.parse(await ask(JSON.stringify({id: 1, method: "evaluateAndSign", params: p})));
        const rec = out.ok ? out.result.refusalRecord : null;
        console.log(`  ${name.padEnd(42)} refused=${out.ok ? out.result.refused : "ERR"}  refusalRecord=${
            out.ok ? (rec === null ? "NULL — not attributable" : "signed") : JSON.stringify(out.error).slice(0, 80)}`);
    }
    sock.destroy();
    signer.stop();
}

node.stop();
process.exit(0);
