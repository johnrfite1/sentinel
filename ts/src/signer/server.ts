import {createServer, type Server, type Socket} from "node:net";
import {chmodSync, existsSync, mkdirSync, unlinkSync} from "node:fs";
import {dirname} from "node:path";
import type {Attestor} from "./attest.ts";
import type {Keystore} from "./keystore.ts";
import {
    ProtocolError,
    parseEvaluateAndSignRequest,
    toWire,
    type Hex,
    type StatusResult,
} from "./protocol.ts";

/**
 * The narrow local RPC (A-005, §3.1).
 *
 * TRANSPORT. A Unix domain socket, chmod 0600, not a TCP port. The signer holds key
 * material, so "which processes can reach it" should be answered by filesystem permissions
 * rather than by whichever local process gets there first. A loopback port is reachable by
 * every process on the machine and by anything that can trick a browser into a request to
 * 127.0.0.1; a 0600 socket is reachable by this user. Neither is a security boundary against
 * a compromised account — nothing at this layer is — but one of them is free.
 *
 * SURFACE. Two methods:
 *
 *     status            — the signer's address and whether the vault currently recognises it
 *     evaluateAndSign   — the one operation that produces a signature
 *
 * There is deliberately no `sign`, `signDigest`, `signBytes`, `signTypedData`, or
 * `signMessage`. This is the property §3.1 names explicitly, and it is the property a
 * reviewer should check first. `METHODS` below is the complete list; an unknown method is
 * an error rather than a fall-through, so a new signing path cannot arrive by accident.
 *
 * FRAMING. Newline-delimited JSON. No HTTP: the signer needs neither routing, content
 * negotiation, nor headers, and every one of those is surface that has to be reasoned about.
 * Oversized lines are dropped with the connection rather than buffered, so a local caller
 * cannot grow the signer's memory without bound.
 */

/**
 * One request line cannot exceed this many UTF-16 code units. Evidence bundles travel
 * inline, so it is generous.
 *
 * Measured in string length rather than bytes, because that is what the accumulating buffer
 * actually costs: the socket is read as UTF-8 text, and the memory at risk is the JS string.
 * Named for code units rather than bytes so nobody later reasons about it as a byte budget —
 * for non-ASCII content the two differ.
 */
const MAX_LINE_LENGTH = 8 * 1024 * 1024;

/**
 * Requests dispatched concurrently per connection before the socket is paused.
 *
 * Sized for a signer, not a server: the intended caller is one evaluator issuing one
 * decision at a time. Anything beyond a handful in flight is either a retry storm or an
 * attempt to exhaust the process, and neither deserves to be served faster.
 */
const MAX_IN_FLIGHT = 16;

export interface SignerServerConfig {
    socketPath: string;
    attestor: Attestor;
    keystore: Keystore;
    vault: Hex;
    chainId: bigint;
    /** Structured log sink. Defaults to stderr; tests pass a collector. */
    log?: (event: Record<string, unknown>) => void;
}

export interface SignerServer {
    readonly socketPath: string;
    close(): Promise<void>;
}

interface Envelope {
    id?: unknown;
    method?: unknown;
    params?: unknown;
}

const METHODS = ["status", "evaluateAndSign"] as const;
type Method = (typeof METHODS)[number];

function isMethod(v: unknown): v is Method {
    return typeof v === "string" && (METHODS as readonly string[]).includes(v);
}

export async function startSignerServer(config: SignerServerConfig): Promise<SignerServer> {
    const {socketPath, attestor, keystore, vault, chainId} = config;
    const log = config.log ?? ((e) => process.stderr.write(`${JSON.stringify(e)}\n`));

    async function handle(method: Method, params: unknown): Promise<unknown> {
        if (method === "status") {
            const notes: string[] = [];
            let ready = false;
            try {
                const state = await attestor.probe();
                ready = state.signer === keystore.address && !state.paused;
                if (state.signer !== keystore.address) {
                    notes.push("vault does not recognise this signer; rotate the signer to " +
                        keystore.address);
                }
                if (state.paused) notes.push("vault is paused");
            } catch {
                notes.push("vault unreadable");
            }
            const result: StatusResult = {
                signerAddress: keystore.address,
                vault,
                chainId: chainId.toString(),
                ready,
                notes,
            };
            return result;
        }

        // `evaluateAndSign`. Parsing is strict and happens before anything else touches the
        // request, so a malformed payload never reaches the check engine.
        const request = parseEvaluateAndSignRequest(params);
        const result = await attestor.evaluateAndSign(request);

        log({
            event: "evaluateAndSign",
            requested: request.evaluation.verdict,
            nonce: request.action.actionNonce.toString(),
            outcome: result.refused ? "refused" : "signed",
            // Findings are logged; the receipt and signature are not. A log is a copy, and
            // the fewer copies of a credential exist the better.
            signerFindings: result.signerFindings,
        });

        return result;
    }

    // Tracked so shutdown can actually close them. `server.close()` alone waits for every
    // connection to drain, which for a long-lived client means forever.
    const connections = new Set<Socket>();

    const server: Server = createServer((socket: Socket) => {
        connections.add(socket);
        socket.setEncoding("utf8");
        let buffer = "";

        // BACKPRESSURE. Each request fans out to a dozen concurrent chain reads, so
        // dispatching every line the moment it arrives lets one ~1 MiB write — comfortably
        // under the per-line cap — queue tens of thousands of requests at once and drive the
        // process into gigabytes of RSS. The per-line cap bounds the receive buffer; it does
        // not bound the work queued behind it. Pausing the socket at the cap is what makes
        // the file header's "cannot grow the signer's memory without bound" true rather than
        // aspirational — an adversarial review demonstrated it was not.
        let inFlight = 0;
        const settle = () => {
            inFlight -= 1;
            if (inFlight < MAX_IN_FLIGHT && socket.isPaused()) socket.resume();
        };

        socket.on("data", (chunk: string) => {
            buffer += chunk;
            if (buffer.length > MAX_LINE_LENGTH) {
                log({event: "oversizedRequest", length: buffer.length});
                socket.destroy();
                return;
            }

            let newline: number;
            while ((newline = buffer.indexOf("\n")) !== -1) {
                const line = buffer.slice(0, newline);
                buffer = buffer.slice(newline + 1);
                if (line.trim() === "") continue;

                inFlight += 1;
                void respond(socket, line).finally(settle);

                if (inFlight >= MAX_IN_FLIGHT && !socket.isPaused()) socket.pause();
            }
        });

        socket.on("close", () => connections.delete(socket));
        socket.on("error", (err) => log({event: "socketError", message: err.message}));
    });

    async function respond(socket: Socket, line: string): Promise<void> {
        let id: unknown = null;
        try {
            const envelope = JSON.parse(line) as Envelope;
            id = envelope.id ?? null;

            if (!isMethod(envelope.method)) {
                // The refusal a reviewer should look for. There is no default branch that
                // could quietly grow into a generic signing method.
                throw new ProtocolError(
                    `unknown method ${JSON.stringify(envelope.method)}; this signer exposes ` +
                        `only ${METHODS.join(", ")} and has no generic signing method by design`,
                );
            }

            const result = await handle(envelope.method, envelope.params);
            write(socket, {id, ok: true, result: toWire(result)});
        } catch (err) {
            const message = err instanceof Error ? err.message : String(err);
            const code = err instanceof ProtocolError ? "BAD_REQUEST" : "SIGNER_ERROR";
            log({event: "requestFailed", code, message});
            write(socket, {id, ok: false, error: {code, message}});
        }
    }

    function write(socket: Socket, payload: unknown): void {
        if (!socket.destroyed) socket.write(`${JSON.stringify(payload)}\n`);
    }

    // A socket left behind by a killed process would make `listen` fail with EADDRINUSE.
    // Removing it is safe only because a live server holds no lock on the path either way;
    // two signers on one path is a configuration error, not something to defend against here.
    //
    // The DIRECTORY is created 0700, and that is the real access control. `listen()` creates
    // the socket at the process umask and only the `chmodSync` below narrows it to 0600 —
    // leaving a window in which another local user could connect and hold the connection,
    // since Unix-socket permissions are checked at connect time and not per write. A
    // 0700 parent directory closes that window regardless of how the socket itself is
    // created, because no other user can traverse into it. Found by adversarial review;
    // `mode` on mkdir is masked by the umask, so it is set explicitly afterwards.
    const socketDir = dirname(socketPath);
    mkdirSync(socketDir, {recursive: true, mode: 0o700});
    chmodSync(socketDir, 0o700);
    if (existsSync(socketPath)) unlinkSync(socketPath);

    await new Promise<void>((resolve, reject) => {
        server.once("error", reject);
        server.listen(socketPath, () => {
            server.removeListener("error", reject);
            resolve();
        });
    });

    // Owner-only. Done after listen because the socket does not exist until then; the
    // window between the two is why the containing directory should also be user-owned.
    chmodSync(socketPath, 0o600);

    log({
        event: "listening",
        socketPath,
        signerAddress: keystore.address,
        keySource: keystore.describe().source,
        vault,
        chainId: chainId.toString(),
        methods: METHODS,
    });

    return {
        socketPath,
        /**
         * Stop listening AND drop existing connections.
         *
         * `server.close()` on its own only stops accepting; it waits for every open
         * connection to end before its callback fires. The evaluator holds one persistent
         * connection, so on its own this never resolves — while Node unlinks the socket file
         * immediately. The result was a signer that ignored SIGTERM, kept its key, kept
         * serving the connected caller, and *looked* stopped because its socket was gone.
         * Restarting then gave two live processes sharing one key, each able to issue an
         * ALLOW receipt for the same nonce — precisely the double-authorisation the
         * attestation guard exists to prevent, reintroduced by a shutdown path. Found by
         * adversarial review, which is a good argument for reviewing shutdown code at all.
         */
        async close(): Promise<void> {
            const closed = new Promise<void>((resolve) => server.close(() => resolve()));
            for (const socket of connections) socket.destroy();
            connections.clear();
            await closed;
            if (existsSync(socketPath)) unlinkSync(socketPath);
        },
    };
}
