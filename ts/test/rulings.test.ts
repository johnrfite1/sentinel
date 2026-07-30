import {describe, it} from "node:test";
import assert from "node:assert/strict";
import {keccak256, recoverAddress, stringToBytes} from "viem";
import {createAttestor} from "../src/signer/attest.ts";
import {digest, domainSeparator, hashReceipt, refusalDigest} from "../src/signer/eip712.ts";
import type {EvaluateAndSignResult, Hex, RefusalRecord} from "../src/signer/protocol.ts";
import {createKeystore} from "../src/signer/keystore.ts";
import {
    CHAIN_ID,
    NOW,
    OTHER_ADDRESS,
    VAULT,
    buildFixture,
    fakeKeystore,
} from "./fakes.ts";
import {SIGNER_KEY, evidenceStub} from "./harness.ts";

/**
 * D-012 and D-014, the two rulings that changed code.
 *
 * Both were ruled by John on 2026-07-28 after two outside reviews. These tests exist because
 * a ruling implemented without a test is a ruling that can be silently un-implemented — and
 * because the rulings' whole purpose is to make certain claims checkable by someone other
 * than the build loop.
 */

/**
 * An attestor reading the SAME fixture the request came from.
 *
 * The first version built its chain from `buildFixture({})` regardless of the request, so any
 * test perturbing the mandate got SIGNER_MANDATE_NOT_ACTIVE instead of the behaviour under
 * test — the vault it read had a different mandate active. Worth a comment: a fixture whose
 * chain and request disagree makes tests fail for the wrong reason, and could equally make
 * them pass for the wrong reason.
 */
function attestorFor(
    fixture: ReturnType<typeof buildFixture>,
    keystore = fakeKeystore(),
) {
    return createAttestor({
        chainId: CHAIN_ID,
        vault: VAULT,
        keystore,
        chain: fixture.chain,
        now: () => NOW,
        randomBytes32: () => keccak256(stringToBytes("decision")),
    });
}

function refusalOf(result: EvaluateAndSignResult) {
    assert.equal(result.refused, true, "expected a refusal");
    return (result as Extract<EvaluateAndSignResult, {refused: true}>).refusalRecord;
}

describe("D-012 — a refusal leaves a recorded artifact", () => {
    it("produces a signed refusal record, so 'refused' differs from 'never asked'", async () => {
        // The gap the ruling closes: before D-012 a refusal produced only an absent receipt,
        // so Gate S2 could not prove the signer had ever seen the request.
        const fixture = buildFixture({action: {actionNonce: 42n}});
        const result = await attestorFor(fixture).evaluateAndSign(fixture.request);

        const refusal = refusalOf(result);
        assert.notEqual(refusal, null, "a refusal must leave an artifact");
        assert.equal(refusal!.record.chainId, CHAIN_ID);
        assert.equal(refusal!.record.vault, VAULT);
        assert.equal(refusal!.record.requestedVerdict, "ALLOW");
        assert.ok(refusal!.reasonCodes.includes("SIGNER_NONCE_MISMATCH"));

        // It binds the action AND the evidence, so it is attributable to a specific request
        // rather than being a bare "something was refused at some point".
        assert.match(refusal!.record.actionHash, /^0x[0-9a-f]{64}$/);
        assert.equal(refusal!.record.evidenceHash, keccak256(stringToBytes(
            fixture.request.evaluation.evidenceCanonical,
        )));
    });

    it("signs the refusal with the signer's own key, verifiably", async () => {
        // An unsigned refusal record would be the caller's word, which is exactly what the
        // architecture declines to take anywhere else.
        const keystore = createKeystore({chainId: CHAIN_ID, vault: VAULT, privateKey: SIGNER_KEY});
        const {request, state} = buildFixture({
            state: {signer: keystore.address},
            action: {actionNonce: 42n},
        });
        const a = createAttestor({
            chainId: CHAIN_ID,
            vault: VAULT,
            keystore,
            chain: {
                async chainId() {
                    return CHAIN_ID;
                },
                async readVaultState() {
                    return state;
                },
                async blockHashAt() {
                    return request.evaluation.simulationBlockHash;
                },
            },
            now: () => NOW,
            randomBytes32: () => keccak256(stringToBytes("decision")),
        });

        const refusal = refusalOf(await a.evaluateAndSign(request));
        assert.notEqual(refusal, null);
        const recovered = await recoverAddress({
            hash: refusalDigest(refusal!.record),
            signature: refusal!.signature,
        });
        assert.equal(recovered.toLowerCase(), keystore.address);
    });

    it("is NOT a receipt, and cannot be confused with one", async () => {
        // D-012: "a refusal is not a decision." The digests live in disjoint preimage spaces —
        // every EIP-712 digest is keccak over a preimage starting 0x1901, a refusal preimage
        // starts with an ASCII tag — so no refusal signature can be replayed as a receipt.
        const keystore = createKeystore({chainId: CHAIN_ID, vault: VAULT, privateKey: SIGNER_KEY});
        const record: RefusalRecord = {
            schemaVersion: 1n,
            chainId: CHAIN_ID,
            vault: VAULT,
            actionHash: keccak256(stringToBytes("action")),
            evidenceHash: keccak256(stringToBytes("{}")),
            requestedVerdict: "ALLOW",
            reasonCodesHash: keccak256(stringToBytes("SIGNER_NONCE_MISMATCH")),
            refusedAt: NOW,
            signer: keystore.address,
        };

        const refusalSig = await keystore.signRefusal(record);

        // The same fields arranged as a receipt produce a different digest, and the refusal
        // signature does not recover to the signer under it.
        const asReceipt = {
            schemaVersion: 1n,
            decisionId: keccak256(stringToBytes("decision")),
            actionHash: record.actionHash,
            mandateHash: keccak256(stringToBytes("mandate")),
            policyHash: keccak256(stringToBytes("policy")),
            verdict: 2n,
            reasonCodesHash: record.reasonCodesHash,
            evidenceHash: record.evidenceHash,
            simulationBlockNumber: 100n,
            simulationBlockHash: keccak256(stringToBytes("block")),
            issuedAt: NOW,
            expiresAt: NOW + 300n,
            signer: keystore.address,
        };
        const receiptDigest = digest(domainSeparator(CHAIN_ID, VAULT), hashReceipt(asReceipt));
        assert.notEqual(refusalDigest(record), receiptDigest);

        const recovered = await recoverAddress({hash: receiptDigest, signature: refusalSig});
        assert.notEqual(
            recovered.toLowerCase(),
            keystore.address,
            "a refusal signature must not validate as a receipt signature",
        );
    });

    it("binds the digest to WHICH action was refused", async () => {
        // Without this, one refusal signature would be valid for every action — the record
        // would prove only that something was refused, not what. Found as a gap when a
        // mutation deleting `actionHash` from the digest preimage survived.
        const base: RefusalRecord = {
            schemaVersion: 1n,
            chainId: CHAIN_ID,
            vault: VAULT,
            actionHash: keccak256(stringToBytes("action A")),
            evidenceHash: keccak256(stringToBytes("{}")),
            requestedVerdict: "ALLOW",
            reasonCodesHash: keccak256(stringToBytes("X")),
            refusedAt: NOW,
            signer: OTHER_ADDRESS,
        };
        const other = {...base, actionHash: keccak256(stringToBytes("action B"))};
        assert.notEqual(refusalDigest(base), refusalDigest(other), "digest must bind the action");

        // And every other field too, so a refusal cannot be reused across evidence, verdicts,
        // chains, or vaults.
        for (const mutated of [
            {...base, evidenceHash: keccak256(stringToBytes("other evidence"))},
            {...base, requestedVerdict: "BLOCK" as const},
            {...base, reasonCodesHash: keccak256(stringToBytes("Y"))},
            {...base, chainId: base.chainId + 1n},
            {...base, vault: "0x1212121212121212121212121212121212121212" as Hex},
            {...base, refusedAt: base.refusedAt + 1n},
        ]) {
            assert.notEqual(refusalDigest(base), refusalDigest(mutated));
        }
    });

    it("omits the artifact only when the request names no attributable action", async () => {
        // A payload contradicting its own calldata describes no action the signer could
        // honestly say it refused, so there is nothing to attribute the refusal to.
        const fixture = buildFixture({action: {dataHash: keccak256(stringToBytes("lie"))}});
        const result = await attestorFor(fixture).evaluateAndSign(fixture.request);
        assert.equal(refusalOf(result), null);
        assert.ok((result as {signerFindings: string[]}).signerFindings.includes(
            "SIGNER_DATAHASH_MISMATCH",
        ));
    });
});

describe("D-014 — the signer binds its own decoding of the calldata", () => {
    /**
     * The ruling rejected giving the signer conformance checks and adopted this instead:
     * the signer decodes the bytes itself and verifies the evidence bundle's decoded
     * parameters match. Derivation without judgement — the mandate is never consulted — so
     * the bundle's parameters become signer-attested and the D-010 verifier can catch a
     * wrong-purpose ALLOW after the fact.
     */
    const PURCHASE: Hex = (() => {
        const w = (h: string) => h.padStart(64, "0");
        return `0xc188528b${w(keccak256(stringToBytes("weather-basic-24h")).slice(2))}${w(
            OTHER_ADDRESS.slice(2),
        )}${w((86_400n).toString(16))}${w("0")}` as Hex;
    })();

    it("accepts a bundle whose decoded parameters match the bytes", async () => {
        const fixture = buildFixture({callData: PURCHASE, mandate: {selector: "0xc188528b"}});
        const result = await attestorFor(fixture).evaluateAndSign(fixture.request);
        assert.ok(
            !(result as {signerFindings: string[]}).signerFindings.includes(
                "SIGNER_EVIDENCE_DECODING_MISMATCH",
            ),
            "a matching bundle must not be flagged",
        );
    });

    it("refuses a bundle that misstates a decoded parameter", async () => {
        // The lying-evaluator case. The bytes purchase weather-basic-24h; the bundle claims
        // premium-monthly. Nothing about the mandate is consulted — only bytes versus claim.
        const lying = JSON.stringify({
            decodedSelectorAndParameters: {
                decoded: "true",
                selector: "0xc188528b",
                schema: "DemoPay.purchase",
                parameters: {
                    resourceId: keccak256(stringToBytes("premium-monthly")),
                    beneficiary: OTHER_ADDRESS,
                    durationSeconds: "86400",
                    recurring: false,
                },
            },
        });
        const fixture = buildFixture({callData: PURCHASE, evidenceCanonical: lying});
        const result = await attestorFor(fixture).evaluateAndSign(fixture.request);
        assert.equal(result.refused, true);
        assert.ok(
            (result as {signerFindings: string[]}).signerFindings.includes(
                "SIGNER_EVIDENCE_DECODING_MISMATCH",
            ),
        );
    });

    it("refuses every verdict on a mismatch, including BLOCK", async () => {
        // FATAL, not CONFORMANCE. A bundle that misdescribes its own action is a false
        // statement in the record the receipt commits to, whatever the verdict says.
        const lying = JSON.stringify({
            decodedSelectorAndParameters: {decoded: "false", selector: "0xc188528b"},
        });
        for (const verdict of ["ALLOW", "REVIEW", "BLOCK"] as const) {
            const fixture = buildFixture({
                callData: PURCHASE,
                evidenceCanonical: lying,
                verdict,
            });
            const result = await attestorFor(fixture).evaluateAndSign(fixture.request);
            assert.equal(result.refused, true, `${verdict} should be refused on a decoding lie`);
        }
    });

    it("does NOT check the parameters against the mandate — that stays the evaluator's job", async () => {
        // The boundary D-014 states precisely, asserted so it cannot drift into a second
        // conformance evaluator. The bytes buy the WRONG resource relative to the mandate,
        // and the bundle describes them accurately. The signer signs: it verified the
        // description, not the purpose.
        const wrongResource: Hex = (() => {
            const w = (h: string) => h.padStart(64, "0");
            return `0xc188528b${w(keccak256(stringToBytes("premium-monthly")).slice(2))}${w(
                OTHER_ADDRESS.slice(2),
            )}${w((86_400n).toString(16))}${w("0")}` as Hex;
        })();

        const fixture = buildFixture({
            callData: wrongResource,
            mandate: {selector: "0xc188528b", resourceId: keccak256(stringToBytes("weather-basic-24h"))},
        });
        const result = await attestorFor(fixture).evaluateAndSign(fixture.request);
        assert.equal(
            result.refused,
            false,
            "the signer must not have become a conformance evaluator (D-014 rejected that); " +
                `findings: ${JSON.stringify((result as {signerFindings?: string[]}).signerFindings)}`,
        );
    });

    it("refuses when the bundle carries no decoding claim at all", async () => {
        // An optional attestation is worthless: a caller wishing to lie would omit the field.
        const fixture = buildFixture({callData: PURCHASE, evidenceCanonical: "{}"});
        const result = await attestorFor(fixture).evaluateAndSign(fixture.request);
        assert.equal(result.refused, true);
        assert.ok(
            (result as {signerFindings: string[]}).signerFindings.includes(
                "SIGNER_EVIDENCE_DECODING_ABSENT",
            ),
        );
    });
});

describe("D-013 — the nonce guard's CLAIM is narrowed, not its mechanism", () => {
    it("still refuses a second different ALLOW at one nonce", async () => {
        // The ruling changed wording, not behaviour. Asserted so a future reader does not
        // mistake "not a durable guarantee" for "removed".
        const first = buildFixture({});
        const a = attestorFor(first);
        assert.equal((await a.evaluateAndSign(first.request)).refused, false);

        const second = buildFixture({callData: `0xa1b2c3d4${"77".repeat(128)}` as Hex});
        const result = await a.evaluateAndSign(second.request);
        assert.equal(result.refused, true);
        assert.ok((result as {signerFindings: string[]}).signerFindings.includes(
            "SIGNER_NONCE_ALREADY_ATTESTED",
        ));
    });

    it("documents itself as per-process rather than durable", async () => {
        // D-013 is a claim-scoping ruling, so the claim itself is what needs a guard. A fresh
        // attestor shares no state with the previous one — which is exactly why the guarantee
        // may not be described as durable.
        const first = buildFixture({});
        assert.equal((await attestorFor(first).evaluateAndSign(first.request)).refused, false);

        const other = buildFixture({callData: `0xa1b2c3d4${"88".repeat(128)}` as Hex});
        assert.equal(
            (await attestorFor(other).evaluateAndSign(other.request)).refused,
            false,
            "a separate process sees no prior reservation — the honest limit D-013 records",
        );
    });
});

describe("D-015 — the proposal no longer contradicts failureMode", () => {
    it("§5.2 states the failureMode-governed rule", async () => {
        const {readFileSync} = await import("node:fs");
        const {join} = await import("node:path");
        const {REPO_ROOT} = await import("./harness.ts");
        const spec = readFileSync(
            join(REPO_ROOT, "Sentinel_Protocol_Lab_Proposal_v0_2.md"),
            "utf8",
        );
        // The amendment ruled in D-015(a). Asserted mechanically because a spec contradiction
        // guarantees a future reader re-derives the fork from scratch.
        assert.match(spec, /Any unknown required check is governed by `failureMode`/);
        assert.equal(
            /Any failed rule blocks\. Any unknown required check reviews\./.test(spec),
            false,
            "the contradicting sentence must be gone",
        );
    });
});
