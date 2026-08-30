import {connect, type Socket} from "node:net";
import {
    toWire,
    type DecisionReceiptPayload,
    type EvaluateAndSignRequest,
    type EvaluateAndSignResult,
    type Hex,
    type StatusResult,
} from "./protocol.ts";

/**
 * Client for the isolated signer's RPC.
 *
 * Lives on the CALLER's side of the process boundary — the conformance evaluator (§9 step
 * 6) will import this, and it is the only thing the evaluator ever gets to hold. It has no
 * access to key material, and there is nothing it could ask the signer for that would
 * yield any: the wire surface is the whole surface.
 *
 * Nothing here mirrors the signer's checks. A client-side pre-check would be a courtesy at
 * best and, at worst, the thing someone later mistakes for the real one. If the caller
 * wants to know whether an action would be attested, it asks.
 */

export class SignerRpcError extends Error {
    // Assigned in the body rather than declared as a constructor parameter property:
    // parameter properties are not erasable syntax, and this repository runs TypeScript
    // through Node's native type stripping.
    readonly code: string;

    constructor(code: string, message: string) {
        super(message);
        this.code = code;
    }
}

export interface SignerClient {
    status(): Promise<StatusResult>;
    evaluateAndSign(request: EvaluateAndSignRequest): Promise<EvaluateAndSignResult>;
    close(): Promise<void>;
}

interface Response {
    id: number;
    ok: boolean;
    result?: unknown;
    error?: {code: string; message: string};
}

export async function connectSigner(socketPath: string): Promise<SignerClient> {
    const socket: Socket = await new Promise((resolve, reject) => {
        const s = connect(socketPath);
        s.once("connect", () => resolve(s));
        s.once("error", reject);
    });
    socket.setEncoding("utf8");

    const pending = new Map<number, {resolve: (v: unknown) => void; reject: (e: Error) => void}>();
    let nextId = 1;
    let buffer = "";

    socket.on("data", (chunk: string) => {
        buffer += chunk;
        let newline: number;
        while ((newline = buffer.indexOf("\n")) !== -1) {
            const line = buffer.slice(0, newline);
            buffer = buffer.slice(newline + 1);
            if (line.trim() === "") continue;
            const response = JSON.parse(line) as Response;
            const waiter = pending.get(response.id);
            if (waiter === undefined) continue;
            pending.delete(response.id);
            if (response.ok) waiter.resolve(response.result);
            else {
                waiter.reject(
                    new SignerRpcError(response.error?.code ?? "UNKNOWN", response.error?.message ?? ""),
                );
            }
        }
    });

    socket.on("close", () => {
        for (const [, waiter] of pending) waiter.reject(new SignerRpcError("CLOSED", "signer closed"));
        pending.clear();
    });

    function call(method: string, params?: unknown): Promise<unknown> {
        const id = nextId++;
        return new Promise((resolve, reject) => {
            pending.set(id, {resolve, reject});
            socket.write(`${JSON.stringify({id, method, params})}\n`);
        });
    }

    return {
        async status(): Promise<StatusResult> {
            return (await call("status")) as StatusResult;
        },

        async evaluateAndSign(request: EvaluateAndSignRequest): Promise<EvaluateAndSignResult> {
            const raw = (await call("evaluateAndSign", toWire(request))) as Record<string, unknown>;
            if (raw.refused === true) return raw as unknown as EvaluateAndSignResult;
            return {
                refused: false,
                receipt: parseReceipt(raw.receipt as Record<string, unknown>),
                signature: raw.signature as Hex,
                reasonCodes: raw.reasonCodes as string[],
                actionHash: raw.actionHash as Hex,
                evidenceHash: raw.evidenceHash as Hex,
                signerFindings: raw.signerFindings as never,
            };
        },

        async close(): Promise<void> {
            await new Promise<void>((resolve) => {
                socket.once("close", () => resolve());
                socket.end();
            });
        },
    };
}

/** Wire decimal strings back to bigint. The mirror of `toWire`. */
function parseReceipt(r: Record<string, unknown>): DecisionReceiptPayload {
    return {
        schemaVersion: BigInt(r.schemaVersion as string),
        decisionId: r.decisionId as Hex,
        actionHash: r.actionHash as Hex,
        mandateHash: r.mandateHash as Hex,
        policyHash: r.policyHash as Hex,
        verdict: BigInt(r.verdict as string),
        reasonCodesHash: r.reasonCodesHash as Hex,
        evidenceHash: r.evidenceHash as Hex,
        simulationBlockNumber: BigInt(r.simulationBlockNumber as string),
        simulationBlockHash: r.simulationBlockHash as Hex,
        issuedAt: BigInt(r.issuedAt as string),
        expiresAt: BigInt(r.expiresAt as string),
        signer: r.signer as Hex,
    };
}
