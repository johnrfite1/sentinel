import {join} from "node:path";
import {createAttestor} from "./attest.ts";
import {createKeystore} from "./keystore.ts";
import {startSignerServer} from "./server.ts";
import {createChainReader} from "./vault.ts";
import type {Hex} from "./protocol.ts";

/**
 * Entry point for the isolated signer process (A-005, §9 step 3).
 *
 * A-005 is explicit that this is "a *separate OS process* with its own key material,
 * reachable only through a narrow local RPC" and that "a same-process module would satisfy
 * the letter and make the public 'isolated signer' claim dishonest." This file is the
 * separateness. It is the only place the key is loaded, and no other component in the
 * repository imports `keystore.ts` — callers import `client.ts` and talk over a socket.
 *
 * Run it:
 *
 *     SENTINEL_VAULT_ADDRESS=0x… npm --prefix ts run signer
 *
 * Configuration, all from this process's own environment:
 *
 *     SENTINEL_VAULT_ADDRESS   required. The vault this signer serves; fixed for the
 *                              process lifetime, because a signer that can be retargeted
 *                              per request is a signer whose domain separation is advisory.
 *     SENTINEL_RPC_URL         default http://127.0.0.1:8545
 *     SENTINEL_SIGNER_SOCKET   default <repo>/.sentinel/signer.sock (gitignored)
 *     SENTINEL_SIGNER_KEY      optional; a fresh key is generated at boot when unset
 */

function required(name: string): string {
    const value = process.env[name];
    if (value === undefined || value === "") {
        throw new Error(`${name} is required. See the header of ts/src/signer/main.ts.`);
    }
    return value;
}

const repoRoot = join(import.meta.dirname, "..", "..", "..");

const vault = required("SENTINEL_VAULT_ADDRESS").toLowerCase() as Hex;
if (!/^0x[0-9a-f]{40}$/.test(vault)) throw new Error("SENTINEL_VAULT_ADDRESS is not an address");

const rpcUrl = process.env.SENTINEL_RPC_URL ?? "http://127.0.0.1:8545";
const socketPath = process.env.SENTINEL_SIGNER_SOCKET ?? join(repoRoot, ".sentinel", "signer.sock");

const chain = createChainReader(rpcUrl);

// The chain id is read once, at boot, and burned into the EIP-712 domain. Re-reading it per
// request would let a node that switched chains underneath the signer silently move which
// system its signatures are valid on.
const chainId = await chain.chainId();

const keystore = createKeystore({chainId, vault});
const attestor = createAttestor({chainId, vault, keystore, chain});

const server = await startSignerServer({socketPath, attestor, keystore, vault, chainId});

// Reported at boot so the operator can activate this address as the vault's signer. The
// address is the only thing about the key that ever leaves this process.
process.stdout.write(
    `sentinel-signer listening\n` +
        `  socket : ${server.socketPath}\n` +
        `  signer : ${keystore.address}  (${keystore.describe().source})\n` +
        `  vault  : ${vault}\n` +
        `  chain  : ${chainId}\n` +
        `  rpc    : ${rpcUrl}\n`,
);

try {
    const state = await attestor.probe();
    if (state.signer !== keystore.address) {
        process.stdout.write(
            `\n  NOT THE ACTIVE SIGNER. The vault currently recognises ${state.signer}.\n` +
                `  Until the owner rotates the signer to ${keystore.address}, this process will\n` +
                `  refuse every ALLOW and REVIEW request (SIGNER_NOT_ACTIVE_SIGNER).\n`,
        );
    }
} catch {
    process.stdout.write(`\n  WARNING: vault not readable at ${rpcUrl}. Requests will fail closed.\n`);
}

// Shutdown must actually shut down. A signer that survives its own SIGTERM while its socket
// disappears looks stopped, so the operator starts another one — and two processes holding
// the same key can each issue an ALLOW receipt for the same nonce. The hard deadline is the
// backstop for anything `close()` cannot drain.
const SHUTDOWN_DEADLINE_MS = 5_000;
let shuttingDown = false;

for (const signal of ["SIGINT", "SIGTERM"] as const) {
    process.on(signal, () => {
        if (shuttingDown) process.exit(1);
        shuttingDown = true;
        process.stdout.write(`\nsentinel-signer stopping (${signal})\n`);

        const deadline = setTimeout(() => {
            process.stderr.write("shutdown did not complete in time; exiting anyway\n");
            process.exit(1);
        }, SHUTDOWN_DEADLINE_MS);
        // Do not let the timer itself hold the process open once close() wins the race.
        deadline.unref();

        void server.close().then(
            () => process.exit(0),
            () => process.exit(1),
        );
    });
}
