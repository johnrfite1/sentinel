import {after, before, describe, it} from "node:test";
import assert from "node:assert/strict";
import {keccak256, stringToBytes} from "viem";
import {anvil} from "viem/chains";
import {connectSigner, type SignerClient} from "../src/signer/client.ts";
import {digest, domainSeparator, hashOverride, hashReceipt} from "../src/signer/eip712.ts";
import type {
    DecisionReceiptPayload,
    EvaluateAndSignRequest,
    Hex,
    OverrideAuthorizationPayload,
} from "../src/signer/protocol.ts";
import {
    ATTACKER,
    ATTACKER_KEY,
    OWNER,
    PURCHASE_VALUE_WEI,
    RESOURCE_ID,
    SIGNER,
    activate,
    buildCase1,
    deployStack,
    evidenceStub,
    startAnvil,
    startSignerProcess,
    type AnvilHandle,
    type Case1,
    type SignerHandle,
    type Stack,
} from "./harness.ts";

/**
 * End-to-end tests for the isolated signer (§9 step 3, A-005).
 *
 * WHAT MAKES THESE EVIDENCE RATHER THAN CEREMONY. Every receipt the signer produces here
 * is submitted to the compiled SentinelVault, which independently recomputes `hashAction`
 * and `hashReceipt` in Solidity and recovers the signature. That is a cross-language
 * differential on the whole EIP-712 encoding — field order, integer widths, address and
 * bytesN padding, domain construction — running on every green test rather than on a
 * fixture someone remembered to regenerate. A single mis-padded word anywhere in
 * `eip712.ts` turns the happy path red.
 *
 * COVERAGE BOUNDARY (house rule 4). These prove the signer binds receipts correctly and
 * refuses to attest when its independent checks fail. They prove NOTHING about whether a
 * verdict was CORRECT: the evaluator's verdict is an input here, supplied by the test. A
 * signer that faithfully attests to a wrong ALLOW passes every test in this file. Closing
 * that gap is §7's harness and the independently labelled corpus, not this suite.
 */

const FAR_FUTURE = 4_000_000_000n;

let node: AnvilHandle;

before(async () => {
    node = await startAnvil();
});

after(() => {
    node?.stop();
});

// ---------------------------------------------------------------------------
// Rig
// ---------------------------------------------------------------------------

interface Rig {
    stack: Stack;
    signer: SignerHandle;
    client: SignerClient;
}

/**
 * A fresh vault and a fresh signer process per test.
 *
 * Sharing them would be faster and would also let one test's nonce consumption, pause
 * state, or in-memory attestation guard decide another test's result. Given that several
 * tests here exist specifically to probe nonce and pause behaviour, shared state would not
 * merely be untidy — it would make the suite's passes uninterpretable.
 */
async function withRig(
    fn: (rig: Rig) => Promise<void>,
    options: {signerKey?: Hex} = {},
): Promise<void> {
    const stack = await deployStack(node.rpcUrl);
    const signer = await startSignerProcess({
        rpcUrl: node.rpcUrl,
        vault: stack.vault,
        privateKey: options.signerKey,
    });
    const client = await connectSigner(signer.socketPath);
    try {
        await fn({stack, signer, client});
    } finally {
        await client.close().catch(() => {});
        signer.stop();
    }
}

async function currentBlock(stack: Stack): Promise<{number: bigint; hash: Hex}> {
    const block = await stack.publicClient.getBlock();
    return {number: block.number, hash: block.hash.toLowerCase() as Hex};
}

async function request(
    stack: Stack,
    scenario: Case1,
    verdict: "ALLOW" | "REVIEW" | "BLOCK",
    reasonCodes: string[] = [],
    overrides: Partial<EvaluateAndSignRequest["evaluation"]> = {},
): Promise<EvaluateAndSignRequest> {
    const block = await currentBlock(stack);
    return {
        action: scenario.action,
        callData: scenario.callData,
        mandate: scenario.mandate,
        policy: scenario.policy,
        evaluation: {
            verdict,
            reasonCodes,
            evidenceCanonical: evidenceStub(`${verdict} for case-1-shaped action`),
            simulationBlockNumber: block.number,
            simulationBlockHash: block.hash,
            ...overrides,
        },
    };
}

async function execute(
    stack: Stack,
    scenario: Case1,
    receipt: DecisionReceiptPayload,
    signature: Hex,
    callDataOverride?: Hex,
): Promise<void> {
    const hash = await stack.walletClient.writeContract({
        address: stack.vault,
        abi: stack.vaultAbi,
        functionName: "executeWithReceipt",
        args: [scenario.action, callDataOverride ?? scenario.callData, receipt, signature],
        account: OWNER,
        chain: anvil,
    });
    const result = await stack.publicClient.waitForTransactionReceipt({hash});
    assert.equal(result.status, "success");
}

async function expectVaultRevert(fn: () => Promise<void>, errorName: string): Promise<void> {
    await assert.rejects(fn, (err: Error) => {
        assert.match(err.message, new RegExp(errorName));
        return true;
    });
}

function assertSigned(
    result: Awaited<ReturnType<SignerClient["evaluateAndSign"]>>,
): asserts result is Extract<typeof result, {refused: false}> {
    assert.equal(
        result.refused,
        false,
        `expected a signature, got refusal: ${JSON.stringify((result as {blocking?: unknown}).blocking)}`,
    );
}

function assertRefused(
    result: Awaited<ReturnType<SignerClient["evaluateAndSign"]>>,
    code: string,
): asserts result is Extract<typeof result, {refused: true}> {
    assert.equal(result.refused, true, "expected a refusal, got a signature");
    const codes = (result as {blocking: {code: string}[]}).blocking.map((b) => b.code);
    assert.ok(codes.includes(code), `expected ${code} among blocking findings, got ${codes.join(", ")}`);
}

// ---------------------------------------------------------------------------
// Case 1 — the allow path
// ---------------------------------------------------------------------------

describe("Case 1 — exact mandate, allow", () => {
    it("signs a receipt the real vault accepts, and the purchase actually lands", async () => {
        await withRig(async ({stack, client}) => {
            const scenario = await buildCase1(stack);
            await activate(stack, scenario.mandateHash, scenario.policyHash);

            const result = await client.evaluateAndSign(await request(stack, scenario, "ALLOW"));
            assertSigned(result);

            // The signer found nothing wrong on a fully conforming action. If this list is
            // ever non-empty on Case 1, one of the independent checks is miscalibrated and
            // would refuse legitimate work.
            assert.deepEqual(result.signerFindings, []);
            assert.equal(result.receipt.verdict, 2n, "ALLOW");
            assert.equal(result.receipt.signer, SIGNER.address.toLowerCase());

            await execute(stack, scenario, result.receipt, result.signature);

            // §5.7: an event alone is not proof of entitlement; conformance checks the
            // resulting contract state. So does this test.
            const expiry = (await stack.publicClient.readContract({
                address: stack.demoPay,
                abi: stack.demoPayAbi,
                functionName: "entitlementExpiry",
                args: [OWNER.address, RESOURCE_ID],
            })) as bigint;
            assert.ok(expiry > 0n, "DemoPay entitlement state did not change");

            const recurring = (await stack.publicClient.readContract({
                address: stack.demoPay,
                abi: stack.demoPayAbi,
                functionName: "recurringEnabled",
                args: [OWNER.address, RESOURCE_ID],
            })) as boolean;
            assert.equal(recurring, false, "the mandate forbade recurrence");
        });
    });

    it("issues a receipt whose actionHash the Solidity library recomputes identically", async () => {
        // Implied by the test above, asserted directly here so a failure says which of the
        // two hashes diverged rather than only that execution reverted.
        await withRig(async ({stack, client}) => {
            const scenario = await buildCase1(stack);
            await activate(stack, scenario.mandateHash, scenario.policyHash);

            const result = await client.evaluateAndSign(await request(stack, scenario, "ALLOW"));
            assertSigned(result);

            const vaultDomain = (await stack.publicClient.readContract({
                address: stack.vault,
                abi: stack.vaultAbi,
                functionName: "domainSeparator",
            })) as Hex;
            assert.equal(
                vaultDomain.toLowerCase(),
                domainSeparator(stack.chainId, stack.vault),
                "TypeScript and Solidity derive different EIP-712 domains",
            );
        });
    });
});

// ---------------------------------------------------------------------------
// Binding — the properties the vault relies on
// ---------------------------------------------------------------------------

describe("receipt binding", () => {
    it("cannot be replayed once the nonce is consumed", async () => {
        await withRig(async ({stack, client}) => {
            const scenario = await buildCase1(stack);
            await activate(stack, scenario.mandateHash, scenario.policyHash);

            const result = await client.evaluateAndSign(await request(stack, scenario, "ALLOW"));
            assertSigned(result);
            await execute(stack, scenario, result.receipt, result.signature);

            await expectVaultRevert(
                () => execute(stack, scenario, result.receipt, result.signature),
                "BadNonce",
            );
        });
    });

    it("is rejected when the calldata is swapped after signing", async () => {
        await withRig(async ({stack, client}) => {
            const scenario = await buildCase1(stack);
            await activate(stack, scenario.mandateHash, scenario.policyHash);

            const result = await client.evaluateAndSign(await request(stack, scenario, "ALLOW"));
            assertSigned(result);

            // Same action payload, different bytes on the wire — the substitution the whole
            // dataHash binding exists to catch (§3.3(5)).
            const tampered = await buildCase1(stack, {
                callDataArgs: {recurring: true},
            });

            await expectVaultRevert(
                () => execute(stack, scenario, result.receipt, result.signature, tampered.callData),
                "CalldataMismatch",
            );
        });
    });

    it("refuses to attest at all when the payload contradicts its own calldata", async () => {
        await withRig(async ({stack, client}) => {
            const scenario = await buildCase1(stack);
            await activate(stack, scenario.mandateHash, scenario.policyHash);

            const lying = {
                ...scenario,
                action: {...scenario.action, dataHash: keccak256(stringToBytes("not the calldata"))},
            };

            // FATAL: refused for every verdict, including BLOCK. The signer will not attest
            // to an action payload that misdescribes the bytes travelling with it, even to
            // say "no" — a block receipt naming an action nobody proposed is not evidence.
            for (const verdict of ["ALLOW", "REVIEW", "BLOCK"] as const) {
                const result = await client.evaluateAndSign(await request(stack, lying, verdict));
                assertRefused(result, "SIGNER_DATAHASH_MISMATCH");
            }
        });
    });
});

// ---------------------------------------------------------------------------
// Refusal tiers
// ---------------------------------------------------------------------------

describe("independent checks", () => {
    it("refuses ALLOW when the action exceeds the mandate's value ceiling", async () => {
        await withRig(async ({stack, client}) => {
            const scenario = await buildCase1(stack, {
                mandate: {maxNativeValueWei: PURCHASE_VALUE_WEI - 1n},
            });
            await activate(stack, scenario.mandateHash, scenario.policyHash);

            const result = await client.evaluateAndSign(await request(stack, scenario, "ALLOW"));
            assertRefused(result, "SIGNER_MANDATE_VALUE_EXCEEDED");
        });
    });

    it("refuses ALLOW when the mandate is not the one the vault activated", async () => {
        await withRig(async ({stack, client}) => {
            const scenario = await buildCase1(stack);
            const other = await buildCase1(stack, {
                mandate: {mandateId: keccak256(stringToBytes("some other mandate"))},
            });
            // The vault activates a DIFFERENT mandate than the one presented.
            await activate(stack, other.mandateHash, scenario.policyHash);

            const result = await client.evaluateAndSign(await request(stack, scenario, "ALLOW"));
            assertRefused(result, "SIGNER_MANDATE_NOT_ACTIVE");
        });
    });

    it("refuses ALLOW when the vault does not recognise this signer", async () => {
        await withRig(
            async ({stack, client}) => {
                const scenario = await buildCase1(stack);
                await activate(stack, scenario.mandateHash, scenario.policyHash);

                const result = await client.evaluateAndSign(await request(stack, scenario, "ALLOW"));
                assertRefused(result, "SIGNER_NOT_ACTIVE_SIGNER");

                const status = await client.status();
                assert.equal(status.ready, false);
                assert.equal(status.signerAddress, ATTACKER.address.toLowerCase());
            },
            {signerKey: ATTACKER_KEY},
        );
    });

    it("refuses ALLOW while the vault is paused", async () => {
        await withRig(async ({stack, client}) => {
            const scenario = await buildCase1(stack);
            await activate(stack, scenario.mandateHash, scenario.policyHash);

            const hash = await stack.walletClient.writeContract({
                address: stack.vault,
                abi: stack.vaultAbi,
                functionName: "setPaused",
                args: [true],
                account: OWNER,
                chain: anvil,
            });
            await stack.publicClient.waitForTransactionReceipt({hash});

            const result = await client.evaluateAndSign(await request(stack, scenario, "ALLOW"));
            assertRefused(result, "SIGNER_VAULT_PAUSED");
        });
    });

    it("refuses ALLOW when the recorded simulation block is not the chain's", async () => {
        await withRig(async ({stack, client}) => {
            const scenario = await buildCase1(stack);
            await activate(stack, scenario.mandateHash, scenario.policyHash);

            // §5.4 records which block a verdict was computed against. Without this check
            // that field is an unverified assertion by the evaluator.
            const result = await client.evaluateAndSign(
                await request(stack, scenario, "ALLOW", [], {
                    simulationBlockHash: keccak256(stringToBytes("a block that never was")),
                }),
            );
            assertRefused(result, "SIGNER_SIMULATION_BLOCK_MISMATCH");
        });
    });

    it("refuses ALLOW on a stale nonce but still signs a BLOCK receipt", async () => {
        await withRig(async ({stack, client}) => {
            const scenario = await buildCase1(stack, {action: {actionNonce: 99n}});
            await activate(stack, scenario.mandateHash, scenario.policyHash);

            assertRefused(
                await client.evaluateAndSign(await request(stack, scenario, "ALLOW")),
                "SIGNER_NONCE_MISMATCH",
            );

            // EXECUTABILITY tier: a block receipt is evidence, never authority, and evidence
            // about an action with a stale nonce is still true evidence.
            const blocked = await client.evaluateAndSign(await request(stack, scenario, "BLOCK"));
            assertSigned(blocked);
            assert.equal(blocked.receipt.verdict, 0n);
            assert.ok(blocked.signerFindings.includes("SIGNER_NONCE_MISMATCH"));
        });
    });
});

// ---------------------------------------------------------------------------
// Case 4 — evidence uncertainty reviews rather than blocks
// ---------------------------------------------------------------------------

describe("Case 4 — evidence uncertainty", () => {
    it("refuses ALLOW on a code-hash mismatch, signs REVIEW, and the override path executes", async () => {
        await withRig(async ({stack, client}) => {
            // The mandate pins a code hash the target does not have — §4.2 Case 4's first
            // trigger. The expected result is REVIEW, not block, and emphatically not a
            // signer refusal: a signer that refused here would make Case 4 unreachable while
            // appearing stricter.
            const scenario = await buildCase1(stack, {
                mandate: {targetCodeHash: keccak256(stringToBytes("yesterday's bytecode"))},
            });
            await activate(stack, scenario.mandateHash, scenario.policyHash);

            assertRefused(
                await client.evaluateAndSign(await request(stack, scenario, "ALLOW")),
                "SIGNER_TARGET_CODEHASH_MISMATCH",
            );

            const reviewed = await client.evaluateAndSign(
                await request(stack, scenario, "REVIEW", ["EVALUATOR_TARGET_CODE_IDENTITY_UNVERIFIED"]),
            );
            assertSigned(reviewed);
            assert.equal(reviewed.receipt.verdict, 1n, "REVIEW");
            assert.ok(reviewed.signerFindings.includes("SIGNER_TARGET_CODEHASH_MISMATCH"));

            // The evaluator's code and the signer's finding both appear under the hash, so a
            // verifier reading the receipt learns what each component concluded.
            assert.ok(reviewed.reasonCodes.includes("EVALUATOR_TARGET_CODE_IDENTITY_UNVERIFIED"));
            assert.ok(reviewed.reasonCodes.includes("SIGNER_TARGET_CODEHASH_MISMATCH"));

            // A REVIEW receipt alone must not execute (§3.3(7)).
            await expectVaultRevert(
                () => execute(stack, scenario, reviewed.receipt, reviewed.signature),
                "NotAllowVerdict",
            );

            // With the owner's separate exact-action override, it does. Note who signs this:
            // the OWNER, not the signer. §3.3(7) requires a credential the isolated signer
            // cannot mint, and it cannot — `keystore.ts` signs receipts and nothing else.
            const auth: OverrideAuthorizationPayload = {
                schemaVersion: 1n,
                reviewReceiptHash: hashReceipt(reviewed.receipt),
                actionHash: reviewed.actionHash,
                mandateHash: scenario.action.mandateHash,
                policyHash: scenario.action.policyHash,
                actionNonce: scenario.action.actionNonce,
                reasonHash: keccak256(stringToBytes("owner accepts the code-identity risk")),
                issuedAt: 0n,
                expiresAt: FAR_FUTURE,
            };
            const ownerSig = await OWNER.sign({
                hash: digest(domainSeparator(stack.chainId, stack.vault), hashOverride(auth)),
            });

            const hash = await stack.walletClient.writeContract({
                address: stack.vault,
                abi: stack.vaultAbi,
                functionName: "executeWithOverride",
                args: [
                    scenario.action,
                    scenario.callData,
                    reviewed.receipt,
                    reviewed.signature,
                    auth,
                    ownerSig,
                ],
                account: OWNER,
                chain: anvil,
            });
            const result = await stack.publicClient.waitForTransactionReceipt({hash});
            assert.equal(result.status, "success");
        });
    });
});

// ---------------------------------------------------------------------------
// The boundary this layer does NOT close
// ---------------------------------------------------------------------------

describe("Case 3 — mechanically valid, wrong purpose", () => {
    it("IS SIGNED by the signer: this layer cannot see it, and that is the gap", async () => {
        // A test that asserts a LIMIT rather than a capability.
        //
        // §4.2 Case 3: poisoned context makes the agent buy the wrong resource. Target,
        // selector, and native value all satisfy the mandate; only the decoded PARAMETER is
        // wrong. The signer checks the selector, never the arguments — decoding is §9 step 4
        // and conformance is step 6 — so it signs an ALLOW here, and the vault executes it.
        //
        // This is written as a passing test on purpose. The coverage boundary printed by
        // scripts/test.sh claims "Case 3 is not detectable anywhere in this gate yet"; prose
        // like that rots the moment someone adds a check and forgets the sentence. Asserted
        // here, the claim is mechanical: when the decoders and the conformance evaluator
        // land, THIS TEST WILL FAIL, and whoever it fails for will be holding the exact
        // sentence in scripts/test.sh that has to change with it.
        await withRig(async ({stack, client}) => {
            const wrongResource = keccak256(stringToBytes("premium-monthly"));
            const scenario = await buildCase1(stack, {
                callDataArgs: {resourceId: wrongResource},
            });
            // The mandate still names weather-basic-24h; only the calldata differs.
            assert.equal(scenario.mandate.resourceId, RESOURCE_ID);
            await activate(stack, scenario.mandateHash, scenario.policyHash);

            const result = await client.evaluateAndSign(await request(stack, scenario, "ALLOW"));
            assertSigned(result);
            assert.deepEqual(
                result.signerFindings,
                [],
                "the signer has no parameter-level check to fail — that is the point",
            );

            await execute(stack, scenario, result.receipt, result.signature);

            // The wrong entitlement is now real onchain state. Nothing in this gate objected.
            const wrongExpiry = (await stack.publicClient.readContract({
                address: stack.demoPay,
                abi: stack.demoPayAbi,
                functionName: "entitlementExpiry",
                args: [OWNER.address, wrongResource],
            })) as bigint;
            assert.ok(wrongExpiry > 0n, "the wrong resource was purchased, unopposed");
        });
    });
});

// ---------------------------------------------------------------------------
// The nonce attestation guard
// ---------------------------------------------------------------------------

describe("one live executable attestation per nonce", () => {
    it("refuses a second, different ALLOW at the same nonce but re-signs the same action", async () => {
        await withRig(async ({stack, client}) => {
            const first = await buildCase1(stack);
            await activate(stack, first.mandateHash, first.policyHash);

            const a = await client.evaluateAndSign(await request(stack, first, "ALLOW"));
            assertSigned(a);

            // Idempotent: a retried request for the SAME action must not wedge the nonce.
            const again = await client.evaluateAndSign(await request(stack, first, "ALLOW"));
            assertSigned(again);
            assert.equal(again.actionHash, a.actionHash);

            // A different action at the same nonce is the hazard the vault structurally
            // cannot see: both receipts are valid credentials for the current nonce, and
            // whichever is relayed first wins.
            const second = await buildCase1(stack, {
                callDataArgs: {duration: 3600n},
            });
            // Re-activate so only the action differs, not the mandate binding.
            await activate(stack, second.mandateHash, second.policyHash);
            const b = await client.evaluateAndSign(await request(stack, second, "ALLOW"));
            assertRefused(b, "SIGNER_NONCE_ALREADY_ATTESTED");
        });
    });

    it("holds under two CONCURRENT requests for different actions at one nonce", async () => {
        await withRig(async ({stack, client}) => {
            const a = await buildCase1(stack, {callDataArgs: {duration: 3600n}});
            const b = await buildCase1(stack, {callDataArgs: {duration: 7200n}});
            await activate(stack, a.mandateHash, a.policyHash);

            assert.equal(a.action.actionNonce, b.action.actionNonce, "both must target one nonce");
            assert.notEqual(a.callData, b.callData, "and must be genuinely different actions");

            // BUILD BOTH REQUESTS FIRST. Writing this as
            //     Promise.all([client.evaluateAndSign(await request(a)), ...])
            // looks concurrent and is not: the `await` inside the array literal suspends
            // evaluation of the second element, so the first request completes end-to-end
            // before the second is ever sent. Both payloads are prepared up front so the
            // two calls genuinely overlap on the socket.
            //
            // WHAT THIS TEST DOES AND DOES NOT PROVE. It proves the invariant holds through
            // the whole real stack — client, socket, server, attestor, chain. It does NOT
            // prove the reserve-before-sign ORDERING is what makes it hold: signing resolves
            // on a microtask while the competing request is still blocked on chain I/O, so
            // the race window here is far too narrow to hit reliably. Verified rather than
            // assumed — re-breaking the ordering leaves this test green.
            // `attestor.concurrency.test.ts` is the test that observes the ordering, using a
            // deliberately slow signer to widen the window; it fails when the ordering is
            // wrong. Naming that split here so nobody reads this test as covering it.
            const requestA = await request(stack, a, "ALLOW");
            const requestB = await request(stack, b, "ALLOW");

            const [ra, rb] = await Promise.all([
                client.evaluateAndSign(requestA),
                client.evaluateAndSign(requestB),
            ]);

            const signed = [ra, rb].filter((r) => !r.refused);
            assert.equal(
                signed.length,
                1,
                "exactly one of two concurrent different actions may hold the nonce",
            );
            const loser = [ra, rb].find((r) => r.refused);
            assert.ok(loser !== undefined);
            assertRefused(loser, "SIGNER_NONCE_ALREADY_ATTESTED");
        });
    });

    it("does not let a BLOCK receipt hold the nonce", async () => {
        await withRig(async ({stack, client}) => {
            const scenario = await buildCase1(stack);
            await activate(stack, scenario.mandateHash, scenario.policyHash);

            const blocked = await client.evaluateAndSign(await request(stack, scenario, "BLOCK"));
            assertSigned(blocked);

            const other = await buildCase1(stack, {callDataArgs: {duration: 7200n}});
            await activate(stack, other.mandateHash, other.policyHash);
            const allowed = await client.evaluateAndSign(await request(stack, other, "ALLOW"));
            assertSigned(allowed);
        });
    });
});

// ---------------------------------------------------------------------------
// The narrow RPC surface — §3.1's explicit prohibition
// ---------------------------------------------------------------------------

describe("RPC surface", () => {
    it("exposes no generic signing method", async () => {
        await withRig(async ({signer}) => {
            // Reaching past the typed client on purpose: the client cannot express these
            // calls, and the claim under test is about the SERVER's surface, not the
            // client's. §3.1: "The signer exposes no generic sign-bytes method."
            const {connect} = await import("node:net");
            const socket = connect(signer.socketPath);
            socket.setEncoding("utf8");
            await new Promise<void>((resolve) => socket.once("connect", () => resolve()));

            const ask = (method: string): Promise<{ok: boolean; error?: {message: string}}> =>
                new Promise((resolve) => {
                    socket.once("data", (line: string) => resolve(JSON.parse(line)));
                    socket.write(`${JSON.stringify({id: 1, method, params: {}})}\n`);
                });

            for (const method of [
                "sign",
                "signBytes",
                "signDigest",
                "signMessage",
                "signTypedData",
                "signHash",
                "eth_sign",
                "personal_sign",
                "exportKey",
                "getPrivateKey",
            ]) {
                const response = await ask(method);
                assert.equal(response.ok, false, `method ${method} must not exist`);
                assert.match(response.error?.message ?? "", /unknown method/);
            }

            socket.destroy();
        });
    });

    it("reports status without revealing anything but the address", async () => {
        await withRig(async ({stack, client}) => {
            const status = await client.status();
            assert.equal(status.signerAddress, SIGNER.address.toLowerCase());
            assert.equal(status.vault, stack.vault);
            assert.equal(status.chainId, stack.chainId.toString());
            assert.equal(status.ready, true);
            assert.deepEqual(Object.keys(status).sort(), [
                "chainId",
                "notes",
                "ready",
                "signerAddress",
                "vault",
            ]);
        });
    });

    it("rejects a malformed request rather than partially applying it", async () => {
        await withRig(async ({stack, client, signer}) => {
            const scenario = await buildCase1(stack);
            await activate(stack, scenario.mandateHash, scenario.policyHash);

            const {connect} = await import("node:net");
            const socket = connect(signer.socketPath);
            socket.setEncoding("utf8");
            await new Promise<void>((resolve) => socket.once("connect", () => resolve()));

            const response = await new Promise<{ok: boolean; error?: {code: string}}>((resolve) => {
                socket.once("data", (line: string) => resolve(JSON.parse(line)));
                socket.write(
                    `${JSON.stringify({
                        id: 1,
                        method: "evaluateAndSign",
                        params: {action: {schemaVersion: "1"}, callData: "0xdeadbeef"},
                    })}\n`,
                );
            });
            assert.equal(response.ok, false);
            assert.equal(response.error?.code, "BAD_REQUEST");
            socket.destroy();

            // Still healthy afterwards: a bad request must not take the signer down.
            const status = await client.status();
            assert.equal(status.ready, true);
        });
    });
});
