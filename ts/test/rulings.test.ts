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
    type FixtureOverrides,
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

describe("D-014 against REAL evaluator bundles (the gap the D-017 review found)", () => {
    /**
     * Every earlier D-014 test built its bundle with `evidenceStub`, which derives the
     * decoded claim using the SAME `decodeBySelector` the signer checks against — so the two
     * sides agreed tautologically and could never disagree. The four demonstration cases all
     * use calldata that decodes at its target, so none traversed the mismatch path either.
     *
     * These tests use the REAL `evaluate()` output as the bundle, which is built from
     * `decodeCall` (target-bound) rather than `decodeBySelector` (not). That difference is
     * exactly what the blocking finding was about.
     */
    async function realBundleFixture(args: {callData: Hex; target: Hex; registryHasTarget: boolean}) {
        const {evaluate} = await import("../src/evaluate/index.ts");
        const {buildRegistry, decodeCall} = await import("../src/decode/index.ts");

        const base = buildFixture({callData: args.callData, action: {target: args.target}});
        const registry = args.registryHasTarget
            ? buildRegistry({[args.target]: "DemoPay"})
            : buildRegistry({});
        const decode = decodeCall({target: args.target, callData: args.callData, registry});

        const evaluation = evaluate({
            mandate: base.request.mandate,
            policy: base.request.policy,
            action: base.request.action,
            callData: args.callData,
            decode,
            simulation: null,
            vaultState: base.state,
            now: NOW,
        });

        return {base, decode, evaluation};
    }

    /** A supported selector (DemoPay.purchase) aimed at a target that does not host it. */
    const PURCHASE_AT_WRONG_TARGET: Hex = (() => {
        const w = (h: string) => h.padStart(64, "0");
        return `0xc188528b${w(keccak256(stringToBytes("weather-basic-24h")).slice(2))}${w(
            OTHER_ADDRESS.slice(2),
        )}${w((86_400n).toString(16))}${w("0")}` as Hex;
    })();

    it("does not refuse a TRUTHFUL bundle that declined to decode for a target reason", async () => {
        // THE BLOCKING DEFECT. The evaluator honestly emits decoded:"false" with
        // DECODE_UNSUPPORTED_TARGET; the signer's selector-only decode succeeds. Requiring
        // those to agree made the signer refuse FATALLY — no receipt of any verdict for
        // target-substitution or wrong-operation shapes, which are the natural injection
        // cases — and commit a "the bundle misdescribes the action" code to a hash falsely.
        const {base, decode, evaluation} = await realBundleFixture({
            callData: PURCHASE_AT_WRONG_TARGET,
            target: "0x8888888888888888888888888888888888888888",
            registryHasTarget: false,
        });
        assert.equal(decode.ok, false);
        assert.equal(decode.code, "DECODE_UNSUPPORTED_TARGET");

        const request = {
            ...base.request,
            action: {...base.request.action, target: "0x8888888888888888888888888888888888888888" as Hex},
            evaluation: {
                ...base.request.evaluation,
                verdict: "BLOCK" as const,
                evidenceCanonical: evaluation.evidenceCanonical,
            },
        };
        const result = await attestorFor(base).evaluateAndSign(request);

        assert.ok(
            !(result as {signerFindings?: string[]}).signerFindings?.includes(
                "SIGNER_EVIDENCE_DECODING_MISMATCH",
            ),
            "a truthful bundle must not be accused of misdescribing the action; " +
                `findings: ${JSON.stringify((result as {signerFindings?: string[]}).signerFindings)}`,
        );
    });

    it("still catches a bundle that lies about parameters", async () => {
        // The narrowing must not have disabled the check it exists for.
        const lying = JSON.stringify({
            decodedSelectorAndParameters: {
                decoded: "true",
                selector: "0xc188528b",
                schema: "DemoPay.purchase",
                parameters: {
                    resourceId: keccak256(stringToBytes("SOMETHING ELSE ENTIRELY")),
                    beneficiary: OTHER_ADDRESS,
                    durationSeconds: "86400",
                    recurring: false,
                },
            },
        });
        const fixture = buildFixture({
            callData: PURCHASE_AT_WRONG_TARGET,
            evidenceCanonical: lying,
        });
        const result = await attestorFor(fixture).evaluateAndSign(fixture.request);
        assert.equal(result.refused, true);
        assert.ok((result as {signerFindings: string[]}).signerFindings.includes(
            "SIGNER_EVIDENCE_DECODING_MISMATCH",
        ));
    });

    it("still catches a bundle claiming a decode the bytes cannot support", async () => {
        const lying = JSON.stringify({
            decodedSelectorAndParameters: {decoded: "true", selector: "0xdeadbeef"},
        });
        const fixture = buildFixture({
            callData: `0xdeadbeef${"00".repeat(32)}` as Hex,
            evidenceCanonical: lying,
        });
        const result = await attestorFor(fixture).evaluateAndSign(fixture.request);
        assert.equal(result.refused, true);
        assert.ok((result as {signerFindings: string[]}).signerFindings.includes(
            "SIGNER_EVIDENCE_DECODING_MISMATCH",
        ));
    });

    it("still catches a decline for a reason INSIDE the signer's remit", async () => {
        // decoded:"false" is not a blanket escape hatch. Only target-binding reasons are
        // outside the signer's remit; a parameter-level failure code the signer can itself
        // adjudicate must still agree with its own decode.
        const lying = JSON.stringify({
            decodedSelectorAndParameters: {
                decoded: "false",
                selector: "0xc188528b",
                failureCode: "DECODE_NON_CANONICAL_BOOL",
            },
        });
        const fixture = buildFixture({
            callData: PURCHASE_AT_WRONG_TARGET,
            evidenceCanonical: lying,
        });
        const result = await attestorFor(fixture).evaluateAndSign(fixture.request);
        assert.equal(result.refused, true);
        assert.ok((result as {signerFindings: string[]}).signerFindings.includes(
            "SIGNER_EVIDENCE_DECODING_MISMATCH",
        ));
    });

    it("decodes identically regardless of calldata hex spelling", async () => {
        // Decoded parameters must be a function of the BYTES. Two spellings of one calldata
        // execute identically, so they must decode identically — and must not produce a
        // spurious FATAL refusal. LLM output is routinely EIP-55 mixed-case.
        //
        // THE ADDRESS MUST CONTAIN HEX LETTERS. The first version of this test used
        // 0x9999…9999, so `toUpperCase()` was a no-op and the test passed against the
        // un-normalised decoder — the identical trap a D-017 adjudicator had already flagged
        // in decode.test.ts, reproduced here while fixing it. Caught by a mutation.
        const {decodeBySelector} = await import("../src/decode/index.ts");
        const lettered: Hex = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd";
        const w = (h: string) => h.padStart(64, "0");
        const lower = `0xc188528b${w(keccak256(stringToBytes("res")).slice(2))}${w(
            lettered.slice(2),
        )}${w((86_400n).toString(16))}${w("0")}` as Hex;
        const upper = (`0x` + lower.slice(2).toUpperCase()) as Hex;
        assert.notEqual(lower, upper, "the fixture must actually differ in spelling");

        const a = decodeBySelector(lower);
        const b = decodeBySelector(upper);
        assert.equal(a.ok, true);
        assert.equal(b.ok, true);
        assert.deepEqual(a.decoded, b.decoded, "hex spelling must not change decoded parameters");
        assert.equal((a.decoded as {beneficiary: Hex}).beneficiary, lettered);
    });
});

/** In-process attestor run, mirroring reasoncodes.test.ts's harness. */
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

function findingsOf(result: EvaluateAndSignResult): string[] {
    return result.signerFindings as string[];
}

describe("D-014: the target-binding escape hatch cannot switch off the attestation (A-028 F1)", () => {
    /**
     * THE DEFECT, and why a green suite said nothing about it.
     *
     * `checkEvidenceDecoding` accepts a bundle that declines to decode for a TARGET reason,
     * because D-014 places target binding outside the signer's remit and D-017's blocking
     * defect was caused by refusing exactly those truthful bundles. But the acceptance was
     * UNCONDITIONAL. Any composer of an `evaluateAndSign` request could therefore switch the
     * whole D-014 attestation off with a two-field lie — claim `decoded:"false"` with a
     * target failureCode — and the signer recorded nothing.
     *
     * An adversarial reviewer ran it end to end against a real Anvil, vault and signer
     * process: an ALLOW was signed for a wrong-resource purchase, it executed, and the wrong
     * entitlement landed onchain under a receipt whose `evidenceHash` committed to a bundle
     * carrying no decoded parameters at all. The party able to do it is exactly the
     * compromised evaluator D-014 names as the threat, which is the ruling's whole subject.
     *
     * The project's own mutation harness has a mutation NAMED for this hole (V2, "treat
     * decoded:false as a blanket escape hatch") that mutates a different branch and reported
     * caught throughout. Reproduction preserved at docs/review-2026-08-15/artifacts/attack.ts.
     */
    const targetFailureBundle = (failureCode: string) =>
        JSON.stringify({
            decodedSelectorAndParameters: {decoded: "false", selector: "0xc188528b", failureCode},
        });

    /**
     * Calldata the signer CAN decode. This is the whole attack: well-formed bytes paired with
     * a bundle that lies about being unable to read them.
     *
     * The fixture default is `0xa1b2c3d4…`, an unsupported selector — against which the
     * signer's own decode fails too, so bundle and signer honestly agree and nothing fires.
     * Using it here would have made these tests pass for the wrong reason, which is the
     * failure mode this whole review round was about.
     */
    const w = (h: string) => h.padStart(64, "0");
    const decodableCallData = `0xc188528b${w(keccak256(stringToBytes("res")).slice(2))}${w(
        "f39fd6e51aad88f6f4ce6ab8827279cfffb92266",
    )}${w((86_400n).toString(16))}${w("0")}` as Hex;

    for (const failureCode of ["DECODE_UNSUPPORTED_TARGET", "DECODE_SELECTOR_TARGET_MISMATCH"]) {
        it(`refuses an ALLOW whose bundle declines to decode (${failureCode})`, async () => {
            const result = await run({
                verdict: "ALLOW",
                callData: decodableCallData,
                evidenceCanonical: targetFailureBundle(failureCode),
            });
            assert.equal(result.refused, true, "the attack must not yield a signed ALLOW");
            assert.ok(
                findingsOf(result).includes("SIGNER_EVIDENCE_DECODING_MISMATCH"),
                `expected the decoding mismatch finding, got ${findingsOf(result).join(",")}`,
            );
        });

        /**
         * The other half, and the one that keeps D-017 fixed. A TRUTHFUL target-mismatch
         * bundle asks for BLOCK or REVIEW — never ALLOW, because `decode.ok === false` makes
         * EVAL_CALLDATA_UNDECODABLE unresolved and `verdictOf` only returns ALLOW when nothing
         * is unresolved (§3.3(8)). Those must still get their receipt: refusing them was
         * precisely the D-017 blocking defect, which left no receipt of any verdict for
         * target-substitution shapes — the natural injection cases.
         */
        for (const verdict of ["BLOCK", "REVIEW"] as const) {
            it(`still issues a ${verdict} receipt for a truthful ${failureCode} bundle`, async () => {
                const result = await run({
                    verdict,
                    callData: decodableCallData,
                    evidenceCanonical: targetFailureBundle(failureCode),
                });
                assert.equal(
                    findingsOf(result).includes("SIGNER_EVIDENCE_DECODING_MISMATCH"),
                    false,
                    "a truthful target-mismatch bundle must not be accused of misdescribing",
                );
            });
        }
    }

    it("still refuses a non-target decline the signer CAN adjudicate", async () => {
        // The control: the hole was specific to the two target codes. A bundle declining for
        // a reason inside the signer's remit, on calldata the signer decodes fine, was always
        // caught — and must stay caught.
        const result = await run({
            verdict: "ALLOW",
            callData: decodableCallData,
            evidenceCanonical: targetFailureBundle("DECODE_UNKNOWN_SELECTOR"),
        });
        assert.equal(result.refused, true);
        assert.ok(findingsOf(result).includes("SIGNER_EVIDENCE_DECODING_MISMATCH"));
    });
});
