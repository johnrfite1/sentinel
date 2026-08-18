/**
 * P8: the A-016 backpressure repair does not bound in-flight work.
 *
 * server.ts pauses the socket once `inFlight >= MAX_IN_FLIGHT`, but the pause happens INSIDE
 * the `while ((newline = buffer.indexOf("\n")) !== -1)` loop. `socket.pause()` only stops
 * FUTURE reads; it does not stop the loop from draining the lines already in `buffer`. So a
 * single write carrying many complete lines is dispatched in full — which is verbatim the
 * scenario the fix's own comment says it closes ("one ~1 MiB write ... queue tens of
 * thousands of requests at once and drive the process into gigabytes of RSS").
 *
 * ONE connection, ONE write.
 */
import {connect} from "node:net";
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
    } catch { return -1; }
};

const s = connect(signer.socketPath);
s.setEncoding("utf8");
s.on("error", (e) => console.log("socket error:", e.message));
let replies = 0;
s.on("data", (c: string) => { replies += (c.match(/\n/g) ?? []).length; });
await new Promise<void>((r) => s.once("connect", () => r()));

console.log("RSS at rest:", rss(), "KiB");

const LINE = '{"id":1,"method":"status","params":{}}\n';
const COUNT = 30_000;               // ~1.1 MiB, comfortably under MAX_LINE_LENGTH (8 MiB)
const payload = LINE.repeat(COUNT);
console.log(`single write: ${COUNT} complete request lines, ${(payload.length / 1048576).toFixed(2)} MiB`);
s.write(payload);

for (let i = 0; i < 8; i++) {
    await new Promise((r) => setTimeout(r, 2000));
    console.log(`  t+${(i + 1) * 2}s  RSS ${rss()} KiB   replies received: ${replies}`);
}

s.destroy();
signer.stop();
node.stop();
process.exit(0);
