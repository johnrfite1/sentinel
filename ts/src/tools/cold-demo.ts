#!/usr/bin/env node
import {spawn, spawnSync, type SpawnSyncReturns} from "node:child_process";
import {
    existsSync,
    mkdirSync,
    mkdtempSync,
    readFileSync,
    readdirSync,
    rmSync,
    writeFileSync,
} from "node:fs";
import {tmpdir} from "node:os";
import {join, relative} from "node:path";
import {
    BaseError,
    ContractFunctionRevertedError,
    createPublicClient,
    createWalletClient,
    encodeFunctionData,
    http,
    keccak256,
    stringToBytes,
    toBytes,
    type Abi,
} from "viem";
import {generatePrivateKey, privateKeyToAccount} from "viem/accounts";
import {anvil} from "viem/chains";
import {buildRegistry, decodeCall} from "../decode/index.ts";
import {evaluate} from "../evaluate/index.ts";
import {hashMandate, hashPolicy} from "../evaluate/hashes.ts";
import {simulateAction} from "../simulate/index.ts";
import {connectSigner} from "../signer/client.ts";
import {digest, domainSeparator} from "../signer/eip712.ts";
import type {ActionPayload, Hex, MandatePayload, PolicyPayload} from "../signer/protocol.ts";
import {createChainReader} from "../signer/vault.ts";

const REPO = join(import.meta.dirname, "..", "..", "..");
const outArg = process.argv.indexOf("--output");
const requestedOutput = outArg >= 0 ? process.argv[outArg + 1] : undefined;
const output: string = requestedOutput ?? mkdtempSync(join(tmpdir(), "sentinel-cold-demo-"));
mkdirSync(output, {recursive: true});

const ownerKey = generatePrivateKey();
const signerKey = generatePrivateKey();
// LAB AUTHORITY, NOT A TRUST ROOT (R-A018-10). This demo generates the deployment authority
// itself, signs its own deployment manifest with it, and then hands the SAME address back to
// the verifier as `--deployment-authority`. That is a self-consistency loop, and it is only
// honest while it is labelled as one. An out-of-band authority is out-of-band precisely because
// the publisher did not choose it; nothing this process prints can be that. The name carries the
// caveat so that no later reader of this file mistakes `authority` for a production identity.
const labAuthorityKey = generatePrivateKey();
const owner = privateKeyToAccount(ownerKey);
const signerAccount = privateKeyToAccount(signerKey);
const labAuthority = privateKeyToAccount(labAuthorityKey);

const port = 9400 + Math.floor(Number(process.hrtime.bigint() % 400n));
const rpcUrl = `http://127.0.0.1:${port}`;
const anvilBin = join(process.env.HOME ?? "", ".foundry", "bin", "anvil");
const node = spawn(existsSync(anvilBin) ? anvilBin : "anvil", ["--port", String(port), "--silent"], {
    stdio: "ignore",
});
const socketDir = mkdtempSync(join(tmpdir(), "sentinel-cold-signer-"));
const socketPath = join(socketDir, "signer.sock");
let signerProcess: ReturnType<typeof spawn> | undefined;

function json(value: unknown): string {
    return JSON.stringify(value, (_key, item) => typeof item === "bigint" ? item.toString() : item, 2);
}

function canonicalObject(value: Record<string, string>): string {
    return JSON.stringify(Object.fromEntries(
        Object.entries(value).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0),
    ));
}

function artifact(file: string, contract: string): {abi: Abi; bytecode: Hex; rawMetadata: string} {
    const doc = JSON.parse(readFileSync(join(REPO, "contracts", "out", file, `${contract}.json`), "utf8")) as {
        abi: Abi; bytecode: {object: Hex}; rawMetadata: string;
    };
    return {abi: doc.abi, bytecode: doc.bytecode.object, rawMetadata: doc.rawMetadata};
}

function sourceArchiveHash(): Hex {
    const root = join(REPO, "contracts", "src");
    const files: string[] = [];
    const walk = (dir: string) => {
        for (const name of readdirSync(dir, {withFileTypes: true})) {
            const path = join(dir, name.name);
            if (name.isDirectory()) walk(path);
            else if (name.isFile() && name.name.endsWith(".sol")) files.push(path);
        }
    };
    walk(root);
    const transcript = files.sort().map((path) => `${relative(root, path)}\0${readFileSync(path, "utf8")}`).join("\0");
    return keccak256(stringToBytes(transcript));
}

async function waitForNode(client: ReturnType<typeof createPublicClient>): Promise<void> {
    const deadline = Date.now() + 20_000;
    while (Date.now() < deadline) {
        try { await client.getChainId(); return; } catch { await new Promise((r) => setTimeout(r, 50)); }
    }
    throw new Error("Anvil did not start");
}

/**
 * THIS DEMO KEEPS CHAIN TIME, NOT WALL TIME (R-A018-15).
 *
 * There are two clocks here and only one of them is authoritative. `SentinelVault` checks the
 * receipt window against `block.timestamp`; the receipt's `issuedAt` is stamped by the ISOLATED
 * SIGNER from its own wall clock, in a separate process, which is correct — that process is the
 * thing under test and takes no clock injection from its caller.
 *
 * MEASURED against anvil 1.7.1 and viem 2.55.10, the versions this demo runs — and NOT what the
 * first report of this defect assumed, so the measurement is recorded rather than the guess:
 *
 *   - Anvil does NOT advance block timestamps per block. Each mined block carries the wall-clock
 *     second at which it was mined, and that value then STANDS STILL until the next block is
 *     mined. No block is mined between activating the mandate and executing.
 *   - The `pending` block tracks the wall clock; the `latest` block does not. Anything evaluated
 *     against `latest` therefore sees the second in which `activateMandate` was mined, however
 *     long ago that was.
 *   - viem builds a transaction for a local account with `eth_fillTransaction`, and anvil
 *     evaluates that against the LATEST block environment. So the receipt's time check is applied
 *     against the frozen timestamp while the transaction is still being built, before anything is
 *     ever sent, and the block the transaction would eventually land in never gets a say.
 *
 * The consequence is a clean predicate rather than a race: if the signer's clock crosses a second
 * boundary between the mandate-activation block and stamping `issuedAt`, then
 * `latest.timestamp < receipt.issuedAt` and `_checkAction` reverts `ReceiptNotYetValid()` — and
 * because `latest` never advances on its own, waiting cannot rescue it. The demo's POSITIVE
 * control then fails for a reason with nothing to do with enforcement. Measured directly, by
 * issuing the same `eth_fillTransaction` the pre-fix demo issued: 8 of 12 serial runs would have
 * reverted, every one of them with `0x118a0502` = `ReceiptNotYetValid()`, at a drift of exactly
 * one second. The same drift landing one step earlier makes the `altered calldata` negative refuse
 * on the wrong check, which R-A018-09's typed controls now catch rather than score as a pass.
 *
 * The fix is not a retry, a sleep, or a widened validity window — each of those leaves the defect
 * in place and hides it, and the third would weaken the very window under test. It is to stop
 * having two clocks:
 *
 *   1. every window this demo authors is read from the chain (`const now`, below), not from
 *      `Date.now()`, so the demo can never author a window the chain is not yet inside; and
 *   2. once the receipt exists, the chain is moved to cover it, explicitly and once.
 *
 * After that alignment `block.timestamp >= receipt.issuedAt` holds by construction — for the
 * transaction build, for the mined execution, and for the negative controls either side of it —
 * however slow the run is. Anvil's clock never runs backwards, so a single alignment is
 * sufficient and no later step can undo it.
 */
async function alignChainClockTo(
    client: ReturnType<typeof createPublicClient>, instant: bigint,
): Promise<{before: bigint; after: bigint; drift: bigint}> {
    const before = (await client.getBlock({blockTag: "latest"})).timestamp;
    // `evm_setNextBlockTimestamp` requires a value strictly greater than the latest block's, so
    // an already-covered instant still costs one block rather than an error.
    const next = instant > before ? instant : before + 1n;
    await client.request({
        method: "evm_setNextBlockTimestamp" as never,
        params: [`0x${next.toString(16)}`] as never,
    });
    await client.request({method: "evm_mine" as never, params: [] as never});
    const after = (await client.getBlock({blockTag: "latest"})).timestamp;
    if (after < instant) {
        throw new Error(
            `chain clock alignment failed: the latest block timestamp is ${after}, still behind ` +
            `the receipt's issuedAt of ${instant}. Executing now would revert ReceiptNotYetValid() ` +
            `for a harness reason rather than an enforcement one, so the demo stops instead.`,
        );
    }
    // Reported, not swallowed. `drift` is exactly how many seconds this run WOULD have executed
    // ahead of the chain, so a reader can see the defect this alignment removes rather than
    // taking the removal on trust; a run printing drift=0 is one that would have passed anyway.
    return {before, after, drift: instant > before ? instant - before : 0n};
}

/**
 * TYPED NEGATIVE CONTROLS (R-A018-09).
 *
 * The previous `mustReject` wrapped each negative in a bare `catch` and printed `PASS negative`
 * for ANY thrown value. A killed Anvil, an RPC hiccup, an ABI-encoding mistake, a missing file,
 * a `python3` that is not on PATH, and a receipt that had simply not become valid yet all scored
 * identically to the refusal the control exists to demonstrate. A negative control that cannot
 * fail for the wrong reason is not evidence, and this one demonstrably could: the demo's own
 * positive execution intermittently reverts `ReceiptNotYetValid()` when Anvil's block clock
 * drifts behind wall time, and under the bare catch that same drift landing one step earlier
 * would have printed `PASS negative: altered calldata`.
 *
 * Every negative below now declares, and asserts, three things:
 *
 *   stage      which component must do the refusing (the Vault, or the publication verifier)
 *   class      how it must fail — an EVM revert with return data, or a verifier exit
 *   identity   the exact refusal: a locally computed 4-byte custom-error selector for the
 *              Vault, or a matched `FAIL:` line plus exit status for the verifier
 *
 * Anything else is re-thrown with the observed classification attached, and the demo fails.
 */

/** Describe an unknown throw without dumping a viem error's full multi-page body. */
function describe(error: unknown): string {
    if (error instanceof BaseError) return `${error.name}: ${error.shortMessage}`;
    if (error instanceof Error) return `${error.name}: ${error.message.split("\n")[0]}`;
    return `non-Error throw: ${String(error)}`;
}

/**
 * The 4-byte selector of a Solidity custom error, computed here from the signature rather than
 * read back out of the ABI. The ABI is the same artifact the vault under test was built from,
 * so recovering the expected selector from it would let one wrong build satisfy both sides.
 */
function errorSelector(signature: string): Hex {
    return keccak256(stringToBytes(signature)).slice(0, 10) as Hex;
}

class NegativeControlFailure extends Error {
    override name = "NegativeControlFailure";
}

/**
 * Assert that `operation` is refused by the Vault with exactly `signature`.
 * stage = vault-execution, class = evm-revert, identity = the custom-error selector.
 */
async function mustRevertWith(
    label: string, signature: string, operation: () => Promise<unknown>,
): Promise<void> {
    const expected = errorSelector(signature);
    let thrown: unknown;
    let accepted = false;
    try { await operation(); accepted = true; } catch (error) { thrown = error; }

    if (accepted) {
        throw new NegativeControlFailure(
            `negative control was ACCEPTED: ${label} (expected the vault to revert ${signature})`,
        );
    }
    if (!(thrown instanceof BaseError)) {
        throw new NegativeControlFailure(
            `negative control "${label}" failed OUTSIDE the vault. Expected an EVM revert with ` +
            `${signature}; got ${describe(thrown)}. This is a harness or transport failure, ` +
            `not a refusal, and it proves nothing about enforcement.`,
        );
    }
    const reverted = thrown.walk((error) => error instanceof ContractFunctionRevertedError);
    if (!(reverted instanceof ContractFunctionRevertedError)) {
        throw new NegativeControlFailure(
            `negative control "${label}" never reached an EVM revert. Expected ${signature}; ` +
            `got ${describe(thrown)}.`,
        );
    }
    const raw = reverted.raw;
    if (typeof raw !== "string" || !raw.startsWith("0x") || raw.length < 10) {
        throw new NegativeControlFailure(
            `negative control "${label}" reverted with no usable return data (${String(raw)}); ` +
            `expected ${signature} (${expected}).`,
        );
    }
    const actual = raw.slice(0, 10).toLowerCase();
    if (actual !== expected) {
        throw new NegativeControlFailure(
            `negative control "${label}" reverted for the WRONG reason: expected ${signature} ` +
            `(${expected}), observed ${reverted.data?.errorName ?? "<undecodable>"}() (${actual}). ` +
            `A negative that refuses on an unintended check is not the control it claims to be.`,
        );
    }
    console.log(
        `PASS negative: ${label} — stage=vault-execution class=evm-revert ` +
        `error=${signature} selector=${actual}`,
    );
}

/**
 * Assert that a publication-verifier run is refused, with the exit status and the specific
 * `FAIL:` line the refusal is supposed to produce.
 * stage = publication-verifier, class = the named refusal, identity = the matched FAIL line.
 *
 * Exit status alone cannot carry this: an uncaught Python exception, an unreadable bundle and a
 * genuine authentication refusal all leave `python3` with status 1, and `verify_publication.py`
 * catches `OSError` too, so `FAIL: [Errno 2] No such file or directory` is a *caught* failure
 * that looks exactly like a contract refusal from the outside.
 */
function mustRefuseVerification(
    label: string,
    expected: {classification: string; exitStatus: number; failure: RegExp},
    run: () => SpawnSyncReturns<string>,
): void {
    const result = run();
    const stdout = result.stdout ?? "";
    const stderr = result.stderr ?? "";

    if (result.error) {
        throw new NegativeControlFailure(
            `negative control "${label}" never ran the verifier: ${describe(result.error)}`,
        );
    }
    if (result.signal) {
        throw new NegativeControlFailure(
            `negative control "${label}": the verifier was killed by ${result.signal} rather ` +
            `than refusing.`,
        );
    }
    if (stderr.includes("Traceback (most recent call last)")) {
        throw new NegativeControlFailure(
            `negative control "${label}": the verifier CRASHED instead of refusing.\n${stderr}`,
        );
    }
    if (stdout.includes("PASS:")) {
        throw new NegativeControlFailure(
            `negative control was ACCEPTED: ${label}\n${stdout}`,
        );
    }
    if (result.status !== expected.exitStatus) {
        throw new NegativeControlFailure(
            `negative control "${label}": expected exit ${expected.exitStatus}, got ` +
            `${String(result.status)}.\n${stdout}${stderr}`,
        );
    }
    const matched = expected.failure.exec(stderr);
    if (!matched) {
        throw new NegativeControlFailure(
            `negative control "${label}" exited ${result.status} for an UNEXPECTED reason. ` +
            `Expected a FAIL line matching ${expected.failure}; observed:\n${stderr}`,
        );
    }
    console.log(
        `PASS negative: ${label} — stage=publication-verifier class=${expected.classification} ` +
        `exit=${result.status} reason=${matched[0].trim()}`,
    );
}

const ZERO32 = `0x${"00".repeat(32)}` as Hex;

/** Write one publication bundle in the exact shape `verify_publication.py` reads. */
function writeBundle(
    dir: string,
    bundle: {
        action: ActionPayload; callData: Hex; mandate: MandatePayload; policy: PolicyPayload;
        ownerSignature: Hex;
        evaluation: {bundle: unknown; evidenceCanonical: string; evidenceHash: Hex};
        signed: {receipt: unknown; signature: Hex; reasonCodes: string[]; signerFindings: string[]};
    },
): void {
    mkdirSync(dir, {recursive: true});
    writeFileSync(join(dir, "mandate.json"), json(bundle.mandate));
    writeFileSync(join(dir, "mandate-signature.json"),
        json({ownerAddress: owner.address, ownerSignature: bundle.ownerSignature}));
    writeFileSync(join(dir, "policy.json"), json(bundle.policy));
    writeFileSync(join(dir, "action.json"), json({...bundle.action, callData: bundle.callData}));
    writeFileSync(join(dir, "evidence.json"), json(bundle.evaluation.bundle));
    writeFileSync(join(dir, "evidence.canonical.json"), bundle.evaluation.evidenceCanonical);
    writeFileSync(join(dir, "evidence.hash"), bundle.evaluation.evidenceHash);
    writeFileSync(join(dir, "receipt.json"), json({
        refused: false, receipt: bundle.signed.receipt, signature: bundle.signed.signature,
        reasonCodes: bundle.signed.reasonCodes, signerFindings: bundle.signed.signerFindings,
    }));
}

try {
    const publicClient = createPublicClient({chain: anvil, transport: http(rpcUrl)});
    await waitForNode(publicClient);
    const chainId = BigInt(await publicClient.getChainId());
    await publicClient.request({
        method: "anvil_setBalance" as never,
        params: [owner.address, "0x3635c9adc5dea00000"] as never,
    });
    const wallet = createWalletClient({chain: anvil, account: owner, transport: http(rpcUrl)});
    const payArtifact = artifact("DemoPay.sol", "DemoPay");
    const vaultArtifact = artifact("SentinelVault.sol", "SentinelVault");

    const payTx = await wallet.deployContract({abi: payArtifact.abi, bytecode: payArtifact.bytecode, account: owner});
    const payReceipt = await publicClient.waitForTransactionReceipt({hash: payTx});
    const demoPay = payReceipt.contractAddress!.toLowerCase() as Hex;
    const selector = keccak256(stringToBytes("purchase(bytes32,address,uint64,bool)")).slice(0, 10) as Hex;
    const vaultTx = await wallet.deployContract({
        abi: vaultArtifact.abi,
        bytecode: vaultArtifact.bytecode,
        args: [owner.address, signerAccount.address, 10n ** 16n, [demoPay], [selector]],
        value: 10n ** 18n,
        account: owner,
    });
    const vaultReceipt = await publicClient.waitForTransactionReceipt({hash: vaultTx});
    const vault = vaultReceipt.contractAddress!.toLowerCase() as Hex;
    const code = await publicClient.getCode({address: demoPay});
    const vaultCode = await publicClient.getCode({address: vault});
    const block = await publicClient.getBlock({blockNumber: vaultReceipt.blockNumber});
    // R-A018-15. CHAIN TIME, read from the chain, not `Date.now()`. Every window below — the
    // policy's, the mandate's, the action deadline, and the deployment manifest's `issuedAt` — is
    // derived from this one instant, so none of them can be authored ahead of the block clock
    // that will judge them. Read explicitly at `latest` rather than reused from the deployment
    // block above: that block happens to be the newest one right now, and an edit inserting any
    // further transaction would quietly make it stale.
    const now = (await publicClient.getBlock({blockTag: "latest"})).timestamp;
    const validUntil = now + 3600n;

    const policy: PolicyPayload = {
        schemaVersion: 1n, policyVersion: 1n, vault, chainId, allowedOperation: 0n,
        allowedTargetsHash: keccak256(stringToBytes(demoPay)),
        allowedSelectorsHash: keccak256(stringToBytes(selector)), maxNativeValueWei: 10n ** 16n,
        maxAllowanceIncreaseBaseUnits: 0n,
        allowedCallGraphHash: keccak256(stringToBytes("DemoPay.purchase:no-internal-calls")),
        validAfter: now - 1n, validUntil, failureMode: 0n,
    };
    const resource = keccak256(stringToBytes("cold-demo-resource"));
    const mandate: MandatePayload = {
        schemaVersion: 1n, mandateId: keccak256(stringToBytes(`cold-demo:${now}`)),
        principal: owner.address.toLowerCase() as Hex,
        signer: signerAccount.address.toLowerCase() as Hex,
        vault, chainId, target: demoPay, targetCodeHash: keccak256(toBytes(code ?? "0x")), selector,
        maxNativeValueWei: 10n ** 16n, purposeKind: keccak256(stringToBytes("purchase")),
        resourceId: resource, beneficiary: owner.address.toLowerCase() as Hex,
        durationSeconds: 3600n, recurringAllowed: false, validAfter: now - 1n, validUntil,
        policyHash: hashPolicy(policy),
    };
    const ownerSignature = await owner.sign({
        hash: digest(domainSeparator(chainId, vault), hashMandate(mandate)),
    });
    const policyActivation = await wallet.writeContract({
        address: vault, abi: vaultArtifact.abi, functionName: "activatePolicy",
        args: [hashPolicy(policy)], account: owner,
    });
    await publicClient.waitForTransactionReceipt({hash: policyActivation});
    const mandateActivation = await wallet.writeContract({
        address: vault, abi: vaultArtifact.abi, functionName: "activateMandate",
        args: [mandate, ownerSignature], account: owner,
    });
    await publicClient.waitForTransactionReceipt({hash: mandateActivation});

    signerProcess = spawn(process.execPath, [join(REPO, "ts", "src", "signer", "main.ts")], {
        cwd: join(REPO, "ts"), stdio: ["ignore", "ignore", "pipe"],
        env: {...process.env, SENTINEL_RPC_URL: rpcUrl, SENTINEL_VAULT_ADDRESS: vault,
            SENTINEL_SIGNER_SOCKET: socketPath, SENTINEL_SIGNER_KEY: signerKey},
    });
    for (let i = 0; i < 400 && !existsSync(socketPath); i++) await new Promise((r) => setTimeout(r, 25));
    if (!existsSync(socketPath)) throw new Error("isolated signer did not start");
    const client = await connectSigner(socketPath);
    const callData = encodeFunctionData({
        abi: payArtifact.abi, functionName: "purchase", args: [resource, owner.address, 3600n, false],
    }) as Hex;
    const reader = createChainReader(rpcUrl);
    const vaultState = await reader.readVaultState(vault, demoPay, selector);
    const action: ActionPayload = {
        schemaVersion: 1n, chainId, vault, actionNonce: vaultState.actionNonce, target: demoPay,
        valueWei: 10n ** 15n, dataHash: keccak256(toBytes(callData)), operation: 0n,
        mandateHash: hashMandate(mandate), policyHash: hashPolicy(policy), deadline: validUntil,
    };
    const registry = buildRegistry({[demoPay]: "DemoPay"});
    const decoded = decodeCall({target: demoPay, callData, registry});
    const simulation = await simulateAction({
        client: publicClient, vault, target: demoPay, valueWei: action.valueWei,
        callData, decoded: decoded.ok ? decoded.decoded : null,
    });
    const evaluation = evaluate({mandate, policy, action, callData, decode: decoded, simulation, vaultState, now});
    if (evaluation.verdict !== "ALLOW") throw new Error(`cold demo did not evaluate ALLOW: ${evaluation.reasonCodes}`);

    // -----------------------------------------------------------------------------------
    // THE BLOCK CASE, GENERATED HERE WITH THIS RUN'S KEYS (D-085(f), 2026-09-01).
    //
    // "A BLOCK receipt certifies on neither entry point" is the flagship property, and until
    // this block it had no runnable evidence in the release: no BLOCK fixture ships, and none
    // should -- a fixture signed by a fixed key that also appears in a repository is the
    // trust-root confusion A-018 Critical 2 was about. So the BLOCK receipt is minted at
    // runtime by the same isolated signer, over an action that differs from the ALLOW one in
    // exactly one word: the beneficiary inside `callData`. Target, selector, value,
    // operation, nonce, mandate and policy are all as mandated. That matters twice over:
    //
    //   * it is the one shape the publication verifier says, in its own NOT ESTABLISHED
    //     line, that it cannot see for itself (it never decodes calldata; D-083(b)), so the
    //     demo shows it caught where it can be caught -- the evaluator decodes the
    //     arguments and returns BLOCK (`EVAL_PURCHASE_BENEFICIARY`);
    //   * and because every field `_checkAction` / `_checkReceipt` compare is conforming,
    //     the ONLY check that can refuse it on-chain is the verdict check. So
    //     `NotAllowVerdict()` / `NotReviewVerdict()` below assert that the refusal happened
    //     on the verdict and not on some incidental mismatch.
    //
    // Signed BEFORE the ALLOW receipt, deliberately. A BLOCK receipt reserves no nonce in
    // the signer, so the ALLOW signing after it is unaffected; and its `issuedAt` is then
    // never later than the ALLOW receipt's, so the single chain-clock alignment below
    // covers both and the Vault cannot refuse it `ReceiptNotYetValid()` for a harness
    // reason (R-A018-15). The alignment target is the later of the two anyway.
    // -----------------------------------------------------------------------------------
    const redirected = privateKeyToAccount(generatePrivateKey()).address;
    const blockCallData = encodeFunctionData({
        abi: payArtifact.abi, functionName: "purchase", args: [resource, redirected, 3600n, false],
    }) as Hex;
    const blockAction: ActionPayload = {...action, dataHash: keccak256(toBytes(blockCallData))};
    const blockDecoded = decodeCall({target: demoPay, callData: blockCallData, registry});
    const blockSimulation = await simulateAction({
        client: publicClient, vault, target: demoPay, valueWei: blockAction.valueWei,
        callData: blockCallData, decoded: blockDecoded.ok ? blockDecoded.decoded : null,
    });
    const blockEvaluation = evaluate({
        mandate, policy, action: blockAction, callData: blockCallData, decode: blockDecoded,
        simulation: blockSimulation, vaultState, now,
    });
    if (blockEvaluation.verdict !== "BLOCK") {
        throw new Error(
            `the redirected-beneficiary action did not evaluate BLOCK (got ` +
            `${blockEvaluation.verdict}: ${blockEvaluation.reasonCodes.join(",")}); the BLOCK ` +
            `case cannot be demonstrated, so the demo stops rather than skipping it`,
        );
    }
    const signedBlock = await client.evaluateAndSign({
        action: blockAction, callData: blockCallData, mandate, policy,
        evaluation: {verdict: blockEvaluation.verdict, reasonCodes: blockEvaluation.reasonCodes,
            evidenceCanonical: blockEvaluation.evidenceCanonical,
            simulationBlockNumber: blockSimulation.anchor.blockNumber,
            simulationBlockHash: blockSimulation.anchor.blockHash},
    });
    if (signedBlock.refused) {
        throw new Error(
            "the isolated signer REFUSED to attest the BLOCK verdict. A signed BLOCK receipt is " +
            "what this demo has to present, and a refusal record is a different artifact; the " +
            `demo stops. blocking=${signedBlock.blocking.map((b) => `${b.code}:${b.severity}`).join(",")}`,
        );
    }
    if (signedBlock.receipt.verdict !== 0n) {
        throw new Error(`signed receipt verdict is ${signedBlock.receipt.verdict}, expected 0 (BLOCK)`);
    }
    console.log(
        `BLOCK receipt signed by the isolated signer over the redirected-beneficiary action ` +
        `(reasonCodes=${blockEvaluation.reasonCodes.join(",")}). It is presented four times below ` +
        `and must be refused four times.`,
    );

    const signed = await client.evaluateAndSign({
        action, callData, mandate, policy,
        evaluation: {verdict: evaluation.verdict, reasonCodes: evaluation.reasonCodes,
            evidenceCanonical: evaluation.evidenceCanonical,
            simulationBlockNumber: simulation.anchor.blockNumber,
            simulationBlockHash: simulation.anchor.blockHash},
    });
    if (signed.refused) throw new Error("isolated signer refused the conforming cold-demo action");

    // R-A018-15. The receipt now exists and carries the signer process's own `issuedAt`; move the
    // chain to cover it before ANY vault call reads it. Placed here rather than immediately before
    // the positive execution so that the `altered calldata` negative in between is also judged
    // inside the receipt window and can only refuse on the binding it was written to exercise.
    const latestIssuedAt = signed.receipt.issuedAt > signedBlock.receipt.issuedAt
        ? signed.receipt.issuedAt : signedBlock.receipt.issuedAt;
    const clock = await alignChainClockTo(publicClient, latestIssuedAt);
    console.log(
        `Chain clock aligned to the receipts: latest block was ${clock.before}, ALLOW receipt ` +
        `issuedAt ${signed.receipt.issuedAt}, BLOCK receipt issuedAt ` +
        `${signedBlock.receipt.issuedAt}, drift ${clock.drift}s, latest block now ${clock.after} ` +
        `(ALLOW receipt expiresAt ${signed.receipt.expiresAt}).`,
    );

    const sample = join(output, "sample");
    writeBundle(sample, {action, callData, mandate, policy, ownerSignature, evaluation, signed});
    // The BLOCK bundle is written beside the ALLOW one so a reader can re-run the verifier
    // against it by hand (release README, "Independent verification"). Its refusal does not
    // go stale: the verifier checks the verdict before any validity window.
    const sampleBlock = join(output, "sample-block");
    writeBundle(sampleBlock, {
        action: blockAction, callData: blockCallData, mandate, policy, ownerSignature,
        evaluation: blockEvaluation, signed: signedBlock,
    });

    const manifestPayload = {
        schemaVersion: "1", chainId: chainId.toString(), vault,
        owner: owner.address.toLowerCase(), signer: signerAccount.address.toLowerCase(),
        deploymentBlockNumber: vaultReceipt.blockNumber.toString(), deploymentBlockHash: block.hash,
        runtimeCodeHash: keccak256(toBytes(vaultCode ?? "0x")),
        compilerMetadataHash: keccak256(stringToBytes(vaultArtifact.rawMetadata)),
        sourceArchiveHash: sourceArchiveHash(), issuedAt: now.toString(),
    };
    const manifestDigest = keccak256(stringToBytes(`sentinel.deployment-manifest.v1\n${canonicalObject(manifestPayload)}`));
    const manifest = {schema: "sentinel.deployment-manifest.v1", payload: manifestPayload,
        authoritySignature: await labAuthority.sign({hash: manifestDigest})};
    const manifestPath = join(output, "deployment-manifest.json");
    writeFileSync(manifestPath, json(manifest));

    // R-A018-10: say what the next run is before it prints PASS, so nobody reads the verifier's
    // output as an out-of-band authentication. The demo signed this manifest with a key it made
    // itself, seconds ago, and is about to hand the verifier that same address.
    console.log(
        "NOTE: this demo generated the deployment authority itself and signed its own manifest " +
        "with it,\n      so the verification below is a SELF-CONSISTENCY loop, not an " +
        "independent authentication.",
    );
    const verifier = spawnSync("python3", [join(REPO, "verifier", "verify_publication.py"), sample,
        "--deployment-manifest", manifestPath, "--deployment-authority", labAuthority.address],
        {encoding: "utf8"});
    if (verifier.status !== 0) throw new Error(`publication verifier failed:\n${verifier.stdout}${verifier.stderr}`);
    process.stdout.write(verifier.stdout);

    const wrongAuthority = privateKeyToAccount(generatePrivateKey()).address.toLowerCase();
    mustRefuseVerification("unauthenticated deployment identity", {
        classification: "authority-signature-refusal",
        exitStatus: 1,
        // The FAIL line must name BOTH addresses. That is what separates an authentication
        // refusal from a crash, a missing bundle, or a malformed manifest: the verifier has to
        // have recovered the lab authority from the signature and rejected it against the
        // out-of-band address it was handed, rather than failing before it ever got there.
        failure: new RegExp(
            `^FAIL: deployment manifest recovered ${labAuthority.address.toLowerCase()}, ` +
            `expected out-of-band authority ${wrongAuthority}$`,
            "m",
        ),
    }, () => spawnSync("python3", [join(REPO, "verifier", "verify_publication.py"), sample,
        "--deployment-manifest", manifestPath, "--deployment-authority", wrongAuthority],
        {encoding: "utf8"}));

    // --- BLOCK x both verifier paths. The FAIL line must name the verdict AND the Vault
    // entry point that refuses it; anything else (a window, a binding, a crash) is not the
    // control this claims to be. The verifier checks the verdict before the windows, which
    // is why these two refusals are the ones a reader can reproduce after the demo's
    // 300-second receipt window has closed.
    const verifierPath = join(REPO, "verifier", "verify_publication.py");
    mustRefuseVerification("BLOCK receipt presented on the automatic path (verifier)", {
        classification: "verdict-refusal",
        exitStatus: 1,
        failure: /^FAIL: receipt\.verdict is BLOCK \(0\), not ALLOW: the Vault's automatic path executeWithReceipt reverts NotAllowVerdict on this receipt\./m,
    }, () => spawnSync("python3", [verifierPath, sampleBlock,
        "--deployment-manifest", manifestPath, "--deployment-authority", labAuthority.address],
        {encoding: "utf8"}));
    mustRefuseVerification("BLOCK receipt presented on the owner-override path (verifier)", {
        classification: "verdict-refusal",
        exitStatus: 1,
        failure: /^FAIL: receipt\.verdict is BLOCK \(0\), not REVIEW: the Vault's override path executeWithOverride reverts NotReviewVerdict, so no owner override can make this receipt executable/m,
    }, () => spawnSync("python3", [verifierPath, sampleBlock,
        "--deployment-manifest", manifestPath, "--deployment-authority", labAuthority.address,
        "--execution-path", "owner-override"],
        {encoding: "utf8"}));

    // --- BLOCK x both Vault entry points, while the nonce is still current. Every field
    // `_checkAction` and `_checkReceipt` compare is as mandated and the receipt is genuinely
    // signed by the active signer, so the verdict check is the first thing that CAN refuse
    // this receipt -- and the selector assertion proves it is the thing that did.
    await mustRevertWith("BLOCK receipt at executeWithReceipt", "NotAllowVerdict()", () =>
        wallet.writeContract({
            address: vault, abi: vaultArtifact.abi, functionName: "executeWithReceipt",
            args: [blockAction, blockCallData, signedBlock.receipt, signedBlock.signature],
            account: owner,
        }));
    // The override struct is all zeros and the owner signature is empty ON PURPOSE. The
    // Vault's verdict check precedes every override check, so `NotReviewVerdict()` asserts
    // that a BLOCK receipt is refused before the Vault so much as reads the credential. If
    // this ever reverted OverrideMismatch or NotOwnerOverride instead, the typed control
    // fails, and rightly: it would mean the Vault examined an override on a BLOCK receipt.
    const zeroOverride = {
        schemaVersion: 0, reviewReceiptHash: ZERO32, actionHash: ZERO32, mandateHash: ZERO32,
        policyHash: ZERO32, actionNonce: 0n, reasonHash: ZERO32, issuedAt: 0n, expiresAt: 0n,
    };
    await mustRevertWith("BLOCK receipt at executeWithOverride", "NotReviewVerdict()", () =>
        wallet.writeContract({
            address: vault, abi: vaultArtifact.abi, functionName: "executeWithOverride",
            args: [blockAction, blockCallData, signedBlock.receipt, signedBlock.signature,
                zeroOverride, "0x"],
            account: owner,
        }));

    const altered = `${callData.slice(0, -2)}${callData.endsWith("00") ? "01" : "00"}` as Hex;
    // The vault recomputes keccak256(callData) and compares it to the signed action's dataHash.
    // Nothing earlier in `_checkAction` can fire here: same nonce, same active mandate and
    // policy, same target, same value. If anything but CalldataMismatch comes back, the control
    // did not exercise the exact-call binding.
    await mustRevertWith("altered calldata", "CalldataMismatch()", () => wallet.writeContract({
        address: vault, abi: vaultArtifact.abi, functionName: "executeWithReceipt",
        args: [action, altered, signed.receipt, signed.signature], account: owner,
    }));
    const execution = await wallet.writeContract({
        address: vault, abi: vaultArtifact.abi, functionName: "executeWithReceipt",
        args: [action, callData, signed.receipt, signed.signature], account: owner,
    });
    const executionReceipt = await publicClient.waitForTransactionReceipt({hash: execution});
    if (executionReceipt.status !== "success") throw new Error("exact execution failed");
    console.log("PASS positive: exact authenticated call executed");
    // The execution above consumed the nonce, so the replay is refused by the nonce check --
    // the FIRST state comparison in `_checkAction`. `BadNonce()` is the assertion that replay
    // died on nonce currency and not on some later, incidental check.
    await mustRevertWith("receipt replay", "BadNonce()", () => wallet.writeContract({
        address: vault, abi: vaultArtifact.abi, functionName: "executeWithReceipt",
        args: [action, callData, signed.receipt, signed.signature], account: owner,
    }));
    await client.close();
    console.log(`Cold demo artifacts: ${output}`);
    console.log(`  sample/        ALLOW bundle -- certifies for 300s after signing, then expires`);
    console.log(`  sample-block/  BLOCK bundle -- refused on both --execution-path values, indefinitely`);
    // R-A018-10. This address was `Deployment authority (obtain out of band)`, which presented a
    // key the demo had generated 20 seconds earlier as the recipient's independent trust root --
    // the exact confusion the out-of-band requirement exists to prevent.
    console.log("");
    console.log("LAB-GENERATED DEPLOYMENT AUTHORITY -- NOT PRODUCTION, NOT A TRUST ROOT");
    console.log(`  address: ${labAuthority.address}`);
    console.log("  This process generated that key in memory at start-up, signed its own");
    console.log("  deployment manifest with it, and discards it on exit. Nothing independent of");
    console.log("  this process attests to it, so it is NOT an out-of-band authority and the");
    console.log("  verification above was a self-consistency check, not an authentication.");
    console.log("  A real recipient's --deployment-authority arrives over a channel the");
    console.log("  publisher does not control. Do not reuse, publish, or trust this address.");
} finally {
    signerProcess?.kill("SIGKILL");
    node.kill("SIGKILL");
    rmSync(socketDir, {recursive: true, force: true});
}
