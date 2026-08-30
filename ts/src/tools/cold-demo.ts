#!/usr/bin/env node
import {spawn, spawnSync} from "node:child_process";
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
const authorityKey = generatePrivateKey();
const owner = privateKeyToAccount(ownerKey);
const signerAccount = privateKeyToAccount(signerKey);
const authority = privateKeyToAccount(authorityKey);

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

async function mustReject(label: string, operation: () => Promise<unknown>): Promise<void> {
    try { await operation(); } catch { console.log(`PASS negative: ${label}`); return; }
    throw new Error(`negative control was accepted: ${label}`);
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
    const now = BigInt(Math.floor(Date.now() / 1000));
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
    const signed = await client.evaluateAndSign({
        action, callData, mandate, policy,
        evaluation: {verdict: evaluation.verdict, reasonCodes: evaluation.reasonCodes,
            evidenceCanonical: evaluation.evidenceCanonical,
            simulationBlockNumber: simulation.anchor.blockNumber,
            simulationBlockHash: simulation.anchor.blockHash},
    });
    if (signed.refused) throw new Error("isolated signer refused the conforming cold-demo action");

    const sample = join(output, "sample");
    mkdirSync(sample, {recursive: true});
    writeFileSync(join(sample, "mandate.json"), json(mandate));
    writeFileSync(join(sample, "mandate-signature.json"), json({ownerAddress: owner.address, ownerSignature}));
    writeFileSync(join(sample, "policy.json"), json(policy));
    writeFileSync(join(sample, "action.json"), json({...action, callData}));
    writeFileSync(join(sample, "evidence.json"), json(evaluation.bundle));
    writeFileSync(join(sample, "evidence.canonical.json"), evaluation.evidenceCanonical);
    writeFileSync(join(sample, "evidence.hash"), evaluation.evidenceHash);
    writeFileSync(join(sample, "receipt.json"), json({
        refused: false, receipt: signed.receipt, signature: signed.signature,
        reasonCodes: signed.reasonCodes, signerFindings: signed.signerFindings,
    }));

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
        authoritySignature: await authority.sign({hash: manifestDigest})};
    const manifestPath = join(output, "deployment-manifest.json");
    writeFileSync(manifestPath, json(manifest));

    const verifier = spawnSync("python3", [join(REPO, "verifier", "verify_publication.py"), sample,
        "--deployment-manifest", manifestPath, "--deployment-authority", authority.address], {encoding: "utf8"});
    if (verifier.status !== 0) throw new Error(`publication verifier failed:\n${verifier.stdout}${verifier.stderr}`);
    process.stdout.write(verifier.stdout);
    const wrongAuthority = privateKeyToAccount(generatePrivateKey()).address;
    const wrongVerifier = spawnSync("python3", [join(REPO, "verifier", "verify_publication.py"), sample,
        "--deployment-manifest", manifestPath, "--deployment-authority", wrongAuthority], {encoding: "utf8"});
    if (wrongVerifier.status === 0) throw new Error("unauthenticated deployment authority was accepted");
    console.log("PASS negative: unauthenticated deployment identity");

    const altered = `${callData.slice(0, -2)}${callData.endsWith("00") ? "01" : "00"}` as Hex;
    await mustReject("altered calldata", () => wallet.writeContract({
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
    await mustReject("receipt replay", () => wallet.writeContract({
        address: vault, abi: vaultArtifact.abi, functionName: "executeWithReceipt",
        args: [action, callData, signed.receipt, signed.signature], account: owner,
    }));
    await client.close();
    console.log(`Cold demo artifacts: ${output}`);
    console.log(`Deployment authority (obtain out of band): ${authority.address}`);
} finally {
    signerProcess?.kill("SIGKILL");
    node.kill("SIGKILL");
    rmSync(socketDir, {recursive: true, force: true});
}
