/** P7: per-connection caps with no cap on connections. */
import {connect, type Socket} from "node:net";
import {execFileSync} from "node:child_process";
import {deployStack, startAnvil, startSignerProcess} from "../test/harness.ts";

const node = await startAnvil();
const stack = await deployStack(node.rpcUrl);
const signer = await startSignerProcess({rpcUrl: node.rpcUrl, vault: stack.vault});

const pid = parseInt(
    execFileSync("pgrep", ["-n", "-f", "src/signer/main.ts"]).toString().trim().split("\n")[0], 10);
const rss = () => {
    try {
        return parseInt(execFileSync("ps", ["-o", "rss=", "-p", String(pid)]).toString().trim(), 10);
    } catch {
        return -1;
    }
};

console.log("signer pid:", pid, " RSS at rest:", rss(), "KiB");

// Each connection may buffer up to MAX_LINE_LENGTH (8 MiB of UTF-16 code units) before the
// server notices. Nothing caps the number of connections.
const N = 40;
const CHUNK = "A".repeat(1024 * 1024); // 1 MiB, no newline -> stays in the per-connection buffer
const socks: Socket[] = [];
for (let i = 0; i < N; i++) {
    const s = connect(signer.socketPath);
    await new Promise<void>((r) => s.once("connect", () => r()));
    s.on("error", () => {});
    socks.push(s);
}
console.log(`opened ${N} concurrent connections; RSS:`, rss(), "KiB");

for (let round = 0; round < 3; round++) {
    for (const s of socks) s.write(`{"id":1,"method":"status","params":{"pad":"${CHUNK}`);
    await new Promise((r) => setTimeout(r, 1500));
    console.log(`after ${(round + 1)} MiB pending on each of ${N} connections; RSS:`, rss(), "KiB");
}

for (const s of socks) s.destroy();
await new Promise((r) => setTimeout(r, 500));
console.log("after dropping all connections; RSS:", rss(), "KiB");

signer.stop();
node.stop();
process.exit(0);
