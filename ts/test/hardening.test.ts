import {describe, it} from "node:test";
import {connect} from "node:net";
import {mkdtempSync} from "node:fs";
import {tmpdir} from "node:os";
import {join} from "node:path";
import {startSignerServer} from "../src/signer/server.ts";
import assert from "node:assert/strict";
import {keccak256, stringToBytes} from "viem";
import {createAttestor} from "../src/signer/attest.ts";
import {parseEvaluateAndSignRequest} from "../src/signer/protocol.ts";
import type {EvaluateAndSignResult, Hex} from "../src/signer/protocol.ts";
import {CHAIN_ID, NOW, VAULT, buildFixture, fakeKeystore, type FixtureOverrides} from "./fakes.ts";

async function run(overrides: FixtureOverrides): Promise<EvaluateAndSignResult> {
    const {request, chain} = buildFixture(overrides);
    const attestor = createAttestor({
        chainId: CHAIN_ID,
        vault: VAULT,
        keystore: fakeKeystore(),
        chain,
        now: () => NOW,
        randomBytes32: () => keccak256(stringToBytes("decision")),
    });
    return attestor.evaluateAndSign(request);
}

/** The wire form of a fixture request: bigints as decimal strings, as the RPC sees them. */
function wire(overrides: FixtureOverrides = {}): any {
    const {request} = buildFixture(overrides);
    return JSON.parse(
        JSON.stringify(request, (_k, v) => (typeof v === "bigint" ? v.toString() : v)),
    );
}

/**
 * A-044 — regression tests for five signer hardening repairs, four of which had NONE.
 *
 * Every defect below was found by the D-044(b) adversarial review of §9 step 3, and every one
 * of them lived in code that already carried a comment claiming the property it did not have.
 * `docs/decisions.md` had already recorded the class — "essentially every A-016 hardening fix
 * shipped in code and comments without regression tests" — and A-043 then demonstrated what
 * that costs: an untested repair covering one of two branches, exploitable for a year.
 *
 * These tests exist so the next reviewer's finding is a failing test rather than a signed
 * ALLOW. Each states which mutation it kills.
 */
describe("A-044 — signer hardening", () => {
    /**
     * Kills: deleting the SIGNER_ prefix rejection.
     *
     * `reasonCodesHash` commits to the UNION of the caller's codes and the signer's findings,
     * and `signerFindings` is NOT a field of the signed §5.4 payload — so a third party cannot
     * tell which side contributed a code. A reviewer signed an ALLOW whose committed codes
     * asserted the signer had found the vault paused, the mandate inactive and itself not the
     * active signer, while the signer had found nothing.
     */
    describe("the signer's reason-code namespace is the signer's", () => {
        for (const code of ["SIGNER_VAULT_PAUSED", "SIGNER_", "SIGNER_ANYTHING_AT_ALL"]) {
            it(`rejects a caller-supplied ${JSON.stringify(code)} at the RPC boundary`, () => {
                const p = wire();
                (p.evaluation as Record<string, unknown>).reasonCodes = [code];
                assert.throws(
                    () => parseEvaluateAndSignRequest(p),
                    /SIGNER_ prefix/,
                    "a caller must not be able to write into the signer's namespace",
                );
            });
        }

        it("still accepts an ordinary evaluator code", () => {
            const p = wire();
            (p.evaluation as Record<string, unknown>).reasonCodes = ["EVAL_TARGET_BOUND"];
            assert.doesNotThrow(() => parseEvaluateAndSignRequest(p));
        });
    });

    /**
     * Kills: deleting the well-formed-UTF-16 check on evidenceCanonical.
     *
     * `stringToBytes` replaces every unpaired surrogate with U+FFFD, so distinct bundles hash
     * identically and `evidenceHash` stops being injective. The D-010 verifier independently
     * rejects these under RFC 8785 §3.2.2.2, so accepting them here also meant signing
     * evidence the independent verifier structurally could not reproduce.
     */
    describe("evidenceCanonical must be well-formed UTF-16", () => {
        const withEvidence = (s: string) => {
            const p = wire();
            p.evaluation.evidenceCanonical = s;
            return p;
        };

        for (const [name, s] of [
            ["a lone high surrogate", "{\"a\":\"x\ud800y\"}"],
            ["a lone low surrogate", "{\"a\":\"x\udc00y\"}"],
        ] as const) {
            it(`rejects ${name}`, () => {
                assert.throws(() => parseEvaluateAndSignRequest(withEvidence(s)), /unpaired surrogate/);
            });
        }

        it("accepts a valid astral pair, which must not be collateral", () => {
            assert.doesNotThrow(() => parseEvaluateAndSignRequest(withEvidence("{\"a\":\"x\u{1F600}y\"}")));
        });

        it("the two surrogates that used to collide are now both refused", () => {
            // Before the check these encoded to identical bytes and identical hashes.
            assert.throws(() => parseEvaluateAndSignRequest(withEvidence("x\ud800y")), /unpaired/);
            assert.throws(() => parseEvaluateAndSignRequest(withEvidence("x\udbffy")), /unpaired/);
        });
    });

    /**
     * Kills: reverting bounded(..., 256) to uint() on any of the four fields.
     *
     * A value >= 2^256 parsed fine, then leftPad threw an ordinary Error — classified
     * SIGNER_ERROR rather than BAD_REQUEST, and thrown BEFORE refuse() could sign anything.
     * So the one request that produced NO signed refusal artifact was the one a caller could
     * trigger at will, in the component whose D-012 record exists to make refusals provable.
     */
    describe("integers are bounded to uint256 at the boundary", () => {
        const TOO_BIG = (1n << 256n).toString();

        for (const [path, mutate] of [
            ["action.valueWei", (p: any) => (p.action.valueWei = TOO_BIG)],
            ["action.actionNonce", (p: any) => (p.action.actionNonce = TOO_BIG)],
            ["action.chainId", (p: any) => (p.action.chainId = TOO_BIG)],
            ["mandate.maxNativeValueWei", (p: any) => (p.mandate.maxNativeValueWei = TOO_BIG)],
        ] as const) {
            it(`rejects an out-of-range ${path} as a BAD_REQUEST`, () => {
                const p = wire();
                mutate(p);
                assert.throws(() => parseEvaluateAndSignRequest(p), /uint256/);
            });
        }
    });

    /**
     * Kills: widening the attributable carve-out back to all structural findings.
     *
     * D-012 requires a refusal to leave a signed artifact. The carve-out suppressing it is
     * justified only for a payload that contradicts its own calldata — for a wrong vault or
     * chain, hashAction succeeds and the action is nameable, so the refusal is attributable
     * and must be recorded.
     */
    describe("a nameable refusal leaves a signed record (D-012)", () => {
        it("SIGNER_DATAHASH_MISMATCH stays unattributable — it names no action", async () => {
            // dataHash is pinned to bytes that are NOT the submitted calldata, so the payload
            // contradicts itself and there is genuinely no action to name. (buildFixture
            // derives dataHash FROM callData, so overriding the calldata alone creates no
            // mismatch — an earlier version of this test did exactly that and passed for the
            // wrong reason.)
            const r = (await run({
                action: {dataHash: keccak256(stringToBytes("not the submitted calldata"))},
            })) as any;
            assert.equal(r.refused, true);
            assert.equal(r.refusalRecord, null, "a self-contradicting payload names no action");
        });

        for (const [name, over] of [
            ["a wrong vault", {action: {vault: `0x${"ab".repeat(20)}` as Hex}}],
            ["a wrong chain", {action: {chainId: 999999n}}],
        ] as const) {
            it(`${name} refusal IS recorded`, async () => {
                const r = (await run(over as Record<string, unknown>)) as any;
                assert.equal(r.refused, true, "the request must still be refused");
                assert.ok(
                    r.refusalRecord !== null,
                    "hashAction succeeds here, so the refusal is attributable and D-012 requires a record",
                );
                assert.ok(typeof r.refusalRecord.signature === "string");
            });
        }
    });

    /**
     * A-016 repairs that shipped with no regression coverage at all. Both mutations survived
     * the whole suite when an adversarial reviewer deleted them.
     */
    describe("A-016 repairs that had no tests", () => {
        it("rejects odd-length hex — the selector/dataHash split repair", () => {
            const p = wire();
            p.callData = "0xabc"; // odd number of hex digits
            assert.throws(() => parseEvaluateAndSignRequest(p), /hex/i);
        });

        it("rejects a malformed reason code at the RPC boundary, not just at signing", () => {
            const p = wire();
            p.evaluation.reasonCodes = ["EVAL_HAS A SPACE"];
            assert.throws(
                () => parseEvaluateAndSignRequest(p),
                /reasonCodes/,
                "the boundary check is the one that turns this into a BAD_REQUEST",
            );
        });
    });

    it("the fixture attestor still signs a conforming ALLOW", async () => {
        // The control. Every test above asserts a refusal or a throw; without this, deleting
        // the whole attest path would leave them all green.
        const r = (await run({})) as any;
        assert.equal(r.refused, false, "the baseline must still conform");
    });
});

/**
 * A-044 — the backpressure repair, which bounded nothing and had no tests.
 *
 * Two independent defects, both demonstrated by an adversarial reviewer:
 *
 *   1. `socket.pause()` was called INSIDE the drain loop. Pausing stops future reads; it does
 *      not stop the loop dispatching lines already in the buffer. One sub-MiB write carrying
 *      25,000 request lines dispatched all of them — 803 MB RSS from a single connection.
 *   2. Both caps were per-connection with nothing bounding connections: 40 individually
 *      compliant sockets reached 1.8 GB.
 *
 * The file header asserted "a local caller cannot grow the signer's memory without bound",
 * and A-016 cited that comment as evidence. It was false when written.
 *
 * The first test below is the regression for the FIX rather than the defect: pausing mid-drain
 * leaves lines in the buffer, and a resume that does not re-enter the loop would deadlock them.
 * That is the failure mode this repair could plausibly introduce, so it is the one pinned.
 */
describe("A-044 — server backpressure", () => {
    const socketPath = () =>
        join(mkdtempSync(join(tmpdir(), "sentinel-hardening-")), "s.sock");

    async function withServer(fn: (path: string) => Promise<void>): Promise<void> {
        const {chain} = buildFixture({});
        const attestor = createAttestor({
            chainId: CHAIN_ID,
            vault: VAULT,
            keystore: fakeKeystore(),
            chain,
            now: () => NOW,
            randomBytes32: () => keccak256(stringToBytes("decision")),
        });
        const server = await startSignerServer({
            socketPath: socketPath(),
            attestor,
            keystore: fakeKeystore(),
            vault: VAULT,
            chainId: CHAIN_ID,
            log: () => {},
        });
        try {
            await fn(server.socketPath);
        } finally {
            await server.close();
        }
    }

    it("answers every line of one oversized write — the drain loop must not deadlock", async () => {
        await withServer(async (path) => {
            const N = 200; // >> MAX_IN_FLIGHT (16), so the pause path is exercised repeatedly
            const replies = await new Promise<number>((resolve, reject) => {
                const sock = connect(path);
                let buf = "";
                let seen = 0;
                sock.setEncoding("utf8");
                sock.on("error", reject);
                sock.on("data", (c: string) => {
                    buf += c;
                    let nl: number;
                    while ((nl = buf.indexOf("\n")) !== -1) {
                        buf = buf.slice(nl + 1);
                        seen += 1;
                        if (seen === N) {
                            sock.destroy();
                            resolve(seen);
                        }
                    }
                });
                setTimeout(() => {
                    sock.destroy();
                    resolve(seen);
                }, 15_000);
                // ONE write. This is the shape that defeated the old cap.
                sock.write(
                    Array.from({length: N}, (_, i) =>
                        JSON.stringify({id: i, method: "status"}),
                    ).join("\n") + "\n",
                );
            });
            assert.equal(
                replies,
                N,
                "every queued request must eventually be answered; a stalled drain loop is the " +
                    "regression this repair could introduce",
            );
        });
    });

    it("refuses connections past the cap rather than accepting unboundedly", async () => {
        await withServer(async (path) => {
            const socks: ReturnType<typeof connect>[] = [];
            try {
                // Open the cap, then one more. The extra must be destroyed by the server.
                for (let i = 0; i < 32; i++) {
                    const s = connect(path);
                    s.on("error", () => {});
                    socks.push(s);
                    await new Promise((r) => s.once("connect", r));
                }
                const extra = connect(path);
                extra.on("error", () => {});
                socks.push(extra);
                const closed = await new Promise<boolean>((resolve) => {
                    extra.once("close", () => resolve(true));
                    setTimeout(() => resolve(false), 5_000);
                });
                assert.equal(closed, true, "a connection past MAX_CONNECTIONS must be dropped");
            } finally {
                for (const s of socks) s.destroy();
            }
        });
    });
});

/**
 * The test that detects the ORIGINAL defect rather than the fix's failure mode.
 *
 * The other two are worth having — one pins the deadlock this repair could introduce, the
 * other pins the connection cap — but neither distinguishes the old drain loop from the new
 * one, because both eventually answer every request. The difference is CONCURRENCY, so that
 * is what this measures: how many requests are in flight at once when a single write carries
 * far more than the cap.
 *
 * Recorded because the first version of this suite shipped without it and I checked: the
 * drain-loop test passed against the unfixed server. A regression test that cannot fail on
 * the defect it names is the shape this project keeps finding.
 */
describe("A-044 — the in-flight cap actually bounds concurrency", () => {
    it("never exceeds MAX_IN_FLIGHT from one oversized write", async () => {
        const {chain} = buildFixture({});
        let live = 0;
        let peak = 0;
        const counting = new Proxy(chain as unknown as Record<string, unknown>, {
            get(target, prop) {
                const v = Reflect.get(target, prop);
                if (typeof v !== "function") return v;
                return async (...args: unknown[]) => {
                    live += 1;
                    peak = Math.max(peak, live);
                    try {
                        await new Promise((r) => setTimeout(r, 5));
                        return await (v as (...a: unknown[]) => unknown).apply(target, args);
                    } finally {
                        live -= 1;
                    }
                };
            },
        });

        const attestor = createAttestor({
            chainId: CHAIN_ID,
            vault: VAULT,
            keystore: fakeKeystore(),
            chain: counting as never,
            now: () => NOW,
            randomBytes32: () => keccak256(stringToBytes("decision")),
        });
        const server = await startSignerServer({
            socketPath: join(mkdtempSync(join(tmpdir(), "sentinel-flight-")), "s.sock"),
            attestor,
            keystore: fakeKeystore(),
            vault: VAULT,
            chainId: CHAIN_ID,
            log: () => {},
        });

        try {
            const N = 200;
            await new Promise<void>((resolve) => {
                const sock = connect(server.socketPath);
                let buf = "";
                let seen = 0;
                sock.setEncoding("utf8");
                sock.on("error", () => resolve());
                sock.on("data", (c: string) => {
                    buf += c;
                    let nl: number;
                    while ((nl = buf.indexOf("\n")) !== -1) {
                        buf = buf.slice(nl + 1);
                        if (++seen === N) {
                            sock.destroy();
                            resolve();
                        }
                    }
                });
                setTimeout(() => {
                    sock.destroy();
                    resolve();
                }, 20_000);
                sock.write(
                    Array.from({length: N}, (_, i) =>
                        JSON.stringify({id: i, method: "status"}),
                    ).join("\n") + "\n",
                );
            });

            assert.ok(
                peak > 0,
                "the probe never ran — this test would pass vacuously, which is the failure " +
                    "mode it exists to prevent elsewhere",
            );
            assert.ok(
                peak <= 16,
                `peak concurrency ${peak} exceeded MAX_IN_FLIGHT; the drain loop is dispatching ` +
                    "past the cap, which is the defect this repair closed",
            );
        } finally {
            await server.close();
        }
    });
});
