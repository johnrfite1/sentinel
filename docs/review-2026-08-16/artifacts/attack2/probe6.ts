/**
 * P8 (memory) and P10 (refusal attributability), with the signer spawned locally so the pid
 * is known exactly — no pgrep, so no chance of touching an unrelated process.
 */
import {connect} from "node:net";
import {spawn, execFileSync, type ChildProcess} from "node:child_process";
import {existsSync, mkdtempSync, rmSync} from "node:fs";
import {tmpdir} from "node:os";
import {join} from "node:path";
import type {Hex} from "../src/signer/protocol.ts";
import {
    REPO_ROOT, SIGNER_KEY, activate, buildCase1, deployStack, evidenceStub, startAnvil, sleep,
} from "../test/harness.ts";

const node = await startAnvil();
const stack = await deployStack(node.rpcUrl);
const line = (t: string) => console.log(`\n──── ${t} ────`);
const wire = (o: unknown) =>
    JSON.parse(JSON.stringify(o, (_k, v) => (typeof v === "bigint" ? v.toString() : v)));

const dir = mkdtempSync(join(tmpdir(), "sentinel-probe6-"));
const socketPath = join(dir, "signer.sock");
const child: ChildProcess = spawn(
    process.execPath, [join(REPO_ROOT, "ts", "src", "signer", "main.ts")],
    {
        cwd: join(REPO_ROOT, "ts"),
        stdio: ["ignore", "ignore", "inherit"],
        env: {
            ...process.env,
            SENTINEL_RPC_URL: node.rpcUrl,
            SENTINEL_VAULT_ADDRESS: stack.vault,
            SENTINEL_SIGNER_SOCKET: socketPath,
            SENTINEL_SIGNER_KEY: SIGNER_KEY,
        },
    },
);
const pid = child.pid!;
while (!existsSync(socketPath)) await sleep(25);
const rss = () => {
    try {
        return parseInt(execFileSync("ps", ["-o", "rss=", "-p", String(pid)]).toString().trim(), 10);
    } catch { return -1; }
};
console.log("signer pid (spawned by this script):", pid, " RSS at rest:", rss(), "KiB");

function conn() {
    const s = connect(socketPath);
    s.setEncoding("utf8");
    s.on("error", () => {});
    return s;
}

// =====================================================================
line("P8a: ONE connection, ONE write of many complete request lines");
{
    const s = conn();
    await new Promise<void>((r) => s.once("connect", () => r()));
    let replies = 0;
    s.on("data", (c: string) => { replies += (c.match(/\n/g) ?? []).length; });
    const LINE = '{"id":1,"method":"status","params":{}}\n';
    const COUNT = 25_000;
    console.log(`writing ${COUNT} lines (${((LINE.length * COUNT) / 1048576).toFixed(2)} MiB) in one call; MAX_IN_FLIGHT is 16`);
    s.write(LINE.repeat(COUNT));
    for (let i = 0; i < 5; i++) {
        await sleep(2000);
        console.log(`  t+${(i + 1) * 2}s  RSS ${rss()} KiB  replies ${replies}/${COUNT}`);
    }
    s.destroy();
    await sleep(1000);
    console.log("  after drop, RSS:", rss(), "KiB");
}

// =====================================================================
line("P8b: many connections, each holding an under-cap partial line");
{
    const N = 40;
    const CHUNK = "A".repeat(1024 * 1024);
    const socks = [];
    for (let i = 0; i < N; i++) {
        const s = conn();
        await new Promise<void>((r) => s.once("connect", () => r()));
        socks.push(s);
    }
    console.log(`opened ${N} connections; RSS:`, rss(), "KiB");
    for (let round = 0; round < 3; round++) {
        for (const s of socks) s.write(`{"id":1,"method":"status","params":{"pad":"${CHUNK}`);
        await sleep(1500);
        console.log(`  ${round + 1} MiB pending on each of ${N}; RSS:`, rss(), "KiB");
    }
    for (const s of socks) s.destroy();
}

// =====================================================================
line("P10: which findings leave a signed D-012 refusal record?");
{
    const s = await buildCase1(stack);
    await activate(stack, s.mandateHash, s.policyHash);
    const b = await stack.publicClient.getBlock();
    const sock = conn();
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
            verdict: "ALLOW", reasonCodes: [], evidenceCanonical: evidenceStub("x", s.callData),
            simulationBlockNumber: b.number.toString(),
            simulationBlockHash: (b.hash as Hex).toLowerCase(),
        },
    });
    const cases: [string, (p: any) => void][] = [
        ["FATAL SIGNER_WRONG_VAULT", (p) => { p.action.vault = "0x000000000000000000000000000000000000dead"; }],
        ["FATAL SIGNER_WRONG_CHAIN", (p) => { p.action.chainId = "999"; }],
        ["FATAL SIGNER_DATAHASH_MISMATCH", (p) => { p.action.dataHash = `0x${"11".repeat(32)}`; }],
        ["FATAL SIGNER_CALLDATA_TOO_SHORT", (p) => { p.callData = "0xab"; p.action.dataHash = `0x${"11".repeat(32)}`; }],
        ["CONFORMANCE mandate window", (p) => { p.mandate.validUntil = "1"; }],
        ["EXECUTABILITY nonce", (p) => { p.action.actionNonce = "4242"; }],
        ["out-of-range valueWei (2^256)", (p) => { p.action.valueWei = (1n << 256n).toString(); }],
    ];
    for (const [name, mut] of cases) {
        const p = base();
        mut(p);
        const out = JSON.parse(await ask(JSON.stringify({id: 1, method: "evaluateAndSign", params: p})));
        if (!out.ok) { console.log(`  ${name.padEnd(34)} ERROR ${out.error.code}: no refusal record`); continue; }
        const rec = out.result.refusalRecord;
        console.log(`  ${name.padEnd(34)} refused=${out.result.refused}  refusalRecord=${rec === null ? "NULL (not attributable)" : "signed"}`);
    }
    sock.destroy();
}

child.kill("SIGKILL");
rmSync(dir, {recursive: true, force: true});
node.stop();
process.exit(0);
