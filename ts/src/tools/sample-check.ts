import {spawn} from "node:child_process";
import {existsSync, readFileSync} from "node:fs";
import {join} from "node:path";
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
import {privateKeyToAccount} from "viem/accounts";
import {anvil} from "viem/chains";
import {buildRegistry, decodeCall} from "../decode/index.ts";
import {evaluate} from "../evaluate/index.ts";
import {hashMandate, hashPolicy} from "../evaluate/hashes.ts";
import {simulateAction} from "../simulate/index.ts";
import {createChainReader} from "../signer/vault.ts";
import {connectSigner} from "../signer/client.ts";
import type {ActionPayload, Hex, MandatePayload, PolicyPayload} from "../signer/protocol.ts";

/**
 * Gate sample-check walker (D-006).
 *
 * D-006 gives John adversarial sampling at gates, and D-017 established that reviewing a
 * SUMMARY grades the summary. This runs the real pipeline and prints the real artifacts —
 * the action it built, what the decoder derived from the bytes, what the simulation actually
 * observed on a real chain, every conformance check with its outcome, the verdict, the
 * receipt the isolated signer produced in its own process, and the resulting onchain state.
 *
 * It imports the SAME modules the suite and the production entry point use. It is a viewer,
 * not a second implementation: if it disagreed with the tests, one of them would be lying.
 *
 * Run:  npm --prefix ts run sample-check
 */

const REPO = join(import.meta.dirname, "..", "..", "..");
const OWNER = privateKeyToAccount("0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80");
const SIGNER = privateKeyToAccount("0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d");

const RESOURCE = keccak256(stringToBytes("weather-basic-24h"));
const WRONG_RESOURCE = keccak256(stringToBytes("premium-monthly"));
const DURATION = 86_400n;
const VALUE = 10n ** 15n;
const FAR_FUTURE = 4_000_000_000n;

const bold = (s: string) => `\x1b[1m${s}\x1b[0m`;
const dim = (s: string) => `\x1b[2m${s}\x1b[0m`;
const green = (s: string) => `\x1b[32m${s}\x1b[0m`;
const red = (s: string) => `\x1b[31m${s}\x1b[0m`;
const yellow = (s: string) => `\x1b[33m${s}\x1b[0m`;

function artifact(file: string, contract: string): {abi: Abi; bytecode: Hex} {
    const path = join(REPO, "contracts", "out", file, `${contract}.json`);
    if (!existsSync(path)) throw new Error(`missing ${path}; run ./scripts/test.sh first`);
    const j = JSON.parse(readFileSync(path, "utf8")) as {abi: Abi; bytecode: {object: Hex}};
    return {abi: j.abi, bytecode: j.bytecode.object};
}

const anvilBin = join(process.env.HOME ?? "", ".foundry", "bin", "anvil");
const port = 8700 + Math.floor(Number(process.hrtime.bigint() % 200n));
const rpcUrl = `http://127.0.0.1:${port}`;
const node = spawn(existsSync(anvilBin) ? anvilBin : "anvil", ["--port", String(port), "--silent"], {
    stdio: "ignore",
});

const publicClient = createPublicClient({chain: anvil, transport: http(rpcUrl)});
const walletClient = createWalletClient({chain: anvil, account: OWNER, transport: http(rpcUrl)});

for (;;) {
    try {
        await publicClient.getChainId();
        break;
    } catch {
        await new Promise((r) => setTimeout(r, 50));
    }
}
const chainId = BigInt(await publicClient.getChainId());

async function deploy(art: {abi: Abi; bytecode: Hex}, args: unknown[], value = 0n): Promise<Hex> {
    const hash = await walletClient.deployContract({
        abi: art.abi,
        bytecode: art.bytecode,
        args: args as never,
        account: OWNER,
        chain: anvil,
        value,
    });
    const r = await publicClient.waitForTransactionReceipt({hash});
    return r.contractAddress!.toLowerCase() as Hex;
}

const payArt = artifact("DemoPay.sol", "DemoPay");
const ercArt = artifact("DemoERC20.sol", "DemoERC20");
const vaultArt = artifact("SentinelVault.sol", "SentinelVault");

const demoPay = await deploy(payArt, []);
const vault = await deploy(
    vaultArt,
    [OWNER.address, SIGNER.address, 10n ** 16n, [demoPay], ["0xc188528b"]],
    10n ** 18n,
);
const demoErc20 = await deploy(ercArt, [vault, 10n ** 24n]);
const registry = buildRegistry({[demoPay]: "DemoPay", [demoErc20]: "DemoERC20"});

const policy: PolicyPayload = {
    schemaVersion: 1n,
    policyVersion: 1n,
    vault,
    chainId,
    allowedOperation: 0n,
    allowedTargetsHash: keccak256(stringToBytes("targets")),
    allowedSelectorsHash: keccak256(stringToBytes("selectors")),
    maxNativeValueWei: 10n ** 16n,
    maxAllowanceIncreaseBaseUnits: 0n,
    allowedCallGraphHash: keccak256(stringToBytes("DemoPay.purchase:no-internal-calls")),
    validAfter: 0n,
    validUntil: FAR_FUTURE,
    failureMode: 1n,
};
const code = await publicClient.getCode({address: demoPay});
const mandate: MandatePayload = {
    schemaVersion: 1n,
    mandateId: keccak256(stringToBytes("mandate:case-1")),
    principal: OWNER.address.toLowerCase() as Hex,
    vault,
    chainId,
    target: demoPay,
    targetCodeHash: keccak256(toBytes(code ?? "0x")),
    selector: "0xc188528b",
    maxNativeValueWei: 10n ** 16n,
    purposeKind: keccak256(stringToBytes("data-service-purchase")),
    resourceId: RESOURCE,
    beneficiary: OWNER.address.toLowerCase() as Hex,
    durationSeconds: DURATION,
    recurringAllowed: false,
    validAfter: 0n,
    validUntil: FAR_FUTURE,
    policyHash: hashPolicy(policy),
};

for (const [fn, arg] of [
    ["activateMandate", hashMandate(mandate)],
    ["activatePolicy", hashPolicy(policy)],
] as const) {
    const h = await walletClient.writeContract({
        address: vault,
        abi: vaultArt.abi,
        functionName: fn,
        args: [arg],
        account: OWNER,
        chain: anvil,
    });
    await publicClient.waitForTransactionReceipt({hash: h});
}

const signerProc = spawn(process.execPath, [join(REPO, "ts", "src", "signer", "main.ts")], {
    cwd: join(REPO, "ts"),
    stdio: ["ignore", "ignore", "ignore"],
    env: {
        ...process.env,
        SENTINEL_RPC_URL: rpcUrl,
        SENTINEL_VAULT_ADDRESS: vault,
        SENTINEL_SIGNER_SOCKET: join(REPO, ".sentinel", `sample-${port}.sock`),
        SENTINEL_SIGNER_KEY: "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
    },
});
const socketPath = join(REPO, ".sentinel", `sample-${port}.sock`);
for (let i = 0; i < 200 && !existsSync(socketPath); i++) await new Promise((r) => setTimeout(r, 25));
const signer = await connectSigner(socketPath);

function purchaseCalldata(resource: Hex): Hex {
    return encodeFunctionData({
        abi: payArt.abi,
        functionName: "purchase",
        args: [resource, OWNER.address, DURATION, false],
    }) as Hex;
}

async function walk(title: string, resource: Hex, expect: string): Promise<void> {
    console.log(`\n${"=".repeat(78)}\n${bold(title)}\n${"=".repeat(78)}`);

    const callData = purchaseCalldata(resource);
    const reader = createChainReader(rpcUrl);
    const vaultState = await reader.readVaultState(vault, demoPay, "0xc188528b");

    const action: ActionPayload = {
        schemaVersion: 1n,
        chainId,
        vault,
        actionNonce: vaultState.actionNonce,
        target: demoPay,
        valueWei: VALUE,
        dataHash: keccak256(toBytes(callData)),
        operation: 0n,
        mandateHash: vaultState.activeMandateHash,
        policyHash: vaultState.activePolicyHash,
        deadline: FAR_FUTURE,
    };

    console.log(`\n${bold("1. THE MANDATE authorises")}`);
    console.log(`   resource    ${mandate.resourceId}`);
    console.log(`   beneficiary ${mandate.beneficiary}`);
    console.log(`   duration    ${mandate.durationSeconds}s   recurring: ${mandate.recurringAllowed}`);
    console.log(`   value cap   ${mandate.maxNativeValueWei} wei`);

    console.log(`\n${bold("2. THE ACTION proposed")}   ${dim("(constructed — D-018 scope)")}`);
    console.log(`   target ${action.target}  value ${action.valueWei} wei  nonce ${action.actionNonce}`);
    console.log(`   calldata ${callData.slice(0, 42)}…`);

    const decode = decodeCall({target: demoPay, callData, registry});
    console.log(`\n${bold("3. DECODED FROM THE BYTES")}   ${dim("(not from any description)")}`);
    if (decode.ok && decode.decoded.schema === "DemoPay.purchase") {
        const d = decode.decoded;
        const mark = (ok: boolean) => (ok ? green("matches mandate") : red("DIFFERS from mandate"));
        console.log(`   resource    ${d.resourceId}  ${mark(d.resourceId === mandate.resourceId)}`);
        console.log(`   beneficiary ${d.beneficiary}  ${mark(d.beneficiary === mandate.beneficiary)}`);
        console.log(`   duration    ${d.durationSeconds}s  ${mark(d.durationSeconds === mandate.durationSeconds)}`);
        console.log(`   recurring   ${d.recurring}`);
    }

    const simulation = await simulateAction({
        client: publicClient,
        vault,
        target: demoPay,
        valueWei: VALUE,
        callData,
        decoded: decode.ok ? decode.decoded : null,
    });
    const ent = simulation.entitlements[0];
    console.log(`\n${bold("4. SIMULATED ON A REAL CHAIN")}   ${dim(`anchor block ${simulation.anchor.blockNumber}`)}`);
    console.log(`   outcome  ${simulation.outcome.status === "success" ? green("success") : red("revert")}`);
    console.log(`   vault Δ  ${simulation.nativeBalanceDeltas.find((d) => d.address === vault)?.delta} wei`);
    if (ent !== undefined) {
        console.log(`   entitlement[${ent.resourceId.slice(0, 10)}…] expiry ${ent.expiryBefore} → ${ent.expiryAfter}`);
    }
    console.log(`   internal calls ${simulation.internalCalls.length}   unresolved ${simulation.unresolvedChecks.length}`);

    const evaluation = evaluate({
        mandate,
        policy,
        action,
        callData,
        decode,
        simulation,
        vaultState,
        now: BigInt(Math.floor(Date.now() / 1000)),
    });

    const violations = evaluation.checks.filter((c) => c.outcome === "VIOLATION");
    const unresolved = evaluation.checks.filter((c) => c.outcome === "UNRESOLVED");
    const passes = evaluation.checks.filter((c) => c.outcome === "PASS");

    console.log(`\n${bold("5. CONFORMANCE CHECKS")}   ${dim(`${passes.length} pass, ${violations.length} violation, ${unresolved.length} unresolved`)}`);
    console.log(dim(`   ${passes.length} passing checks incl. the representative-baseline set:`));
    for (const c of ["EVAL_CHAIN_BOUND","EVAL_VAULT_BOUND","EVAL_TARGET_BOUND","EVAL_SELECTOR_BOUND",
                     "EVAL_VALUE_WITHIN_POLICY","EVAL_VALUE_WITHIN_VAULT_CAP","EVAL_OPERATION_SUPPORTED",
                     "EVAL_SIMULATION_SUCCEEDS"]) {
        const r = evaluation.checks.find((x) => x.code === c);
        console.log(`     ${r?.outcome === "PASS" ? green("PASS") : red(String(r?.outcome))}  ${c}`);
    }
    for (const v of violations) console.log(`   ${red("VIOLATION")}  ${v.code}\n              ${dim(v.detail)}`);
    for (const u of unresolved) console.log(`   ${yellow("UNRESOLVED")} ${u.code}`);

    console.log(`\n${bold("6. VERDICT")}  ${evaluation.verdict === "ALLOW" ? green(evaluation.verdict) : red(evaluation.verdict)}   ${dim(`expected ${expect}`)}`);
    console.log(`   evidenceHash ${evaluation.evidenceHash}`);

    const signed = await signer.evaluateAndSign({
        action,
        callData,
        mandate,
        policy,
        evaluation: {
            verdict: evaluation.verdict,
            reasonCodes: evaluation.reasonCodes,
            evidenceCanonical: evaluation.evidenceCanonical,
            simulationBlockNumber: simulation.anchor.blockNumber,
            simulationBlockHash: simulation.anchor.blockHash,
        },
    });

    console.log(`\n${bold("7. ISOLATED SIGNER")}   ${dim("(separate OS process, over its socket)")}`);
    if (signed.refused) {
        console.log(`   ${red("REFUSED")}  ${JSON.stringify(signed.blocking.map((b) => b.code))}`);
        return;
    }
    console.log(`   ${green("signed")}  verdict=${signed.receipt.verdict} signer=${signed.receipt.signer}`);
    console.log(`   receipt.evidenceHash ${signed.receipt.evidenceHash} ${
        signed.receipt.evidenceHash === evaluation.evidenceHash ? green("= evaluator's") : red("MISMATCH")}`);
    console.log(`   signature ${signed.signature.slice(0, 34)}…`);

    console.log(`\n${bold("8. VAULT ENFORCEMENT")}`);
    try {
        const h = await walletClient.writeContract({
            address: vault,
            abi: vaultArt.abi,
            functionName: "executeWithReceipt",
            args: [action, callData, signed.receipt, signed.signature],
            account: OWNER,
            chain: anvil,
        });
        const r = await publicClient.waitForTransactionReceipt({hash: h});
        console.log(`   executeWithReceipt → ${r.status === "success" ? green("EXECUTED") : red(r.status)}`);
    } catch (err) {
        const m = (err instanceof Error ? err.message : String(err)).split("\n")[0] ?? "";
        console.log(`   executeWithReceipt → ${red("REVERTED")} ${dim(m.slice(0, 90))}`);
    }

    console.log(`\n${bold("9. RESULTING ONCHAIN STATE")}   ${dim("(§5.7: state, not the event, is the truth)")}`);
    for (const [label, res] of [["authorised weather-basic-24h", RESOURCE], ["wrong premium-monthly", WRONG_RESOURCE]] as const) {
        const expiry = (await publicClient.readContract({
            address: demoPay,
            abi: payArt.abi,
            functionName: "entitlementExpiry",
            args: [OWNER.address, res],
        })) as bigint;
        console.log(`   ${label.padEnd(30)} expiry = ${expiry === 0n ? dim("0 (never purchased)") : green(String(expiry))}`);
    }
}

await walk("SAMPLE CHECK — CASE 1: exact mandate, expect ALLOW and execution", RESOURCE, "ALLOW");
await walk("SAMPLE CHECK — CASE 3: mechanically valid, WRONG RESOURCE, expect BLOCK", WRONG_RESOURCE, "BLOCK");

console.log(`\n${"=".repeat(78)}`);
console.log(bold("WHAT THIS SAMPLE SHOWS, AND WHAT IT DOES NOT"));
console.log(`${"=".repeat(78)}
Case 3 is the one that carries the differentiation claim. Read its section 5: every
representative-baseline check PASSES and the simulated execution SUCCEEDS. The block comes
from one place only — the mandate's purpose constraint. If that violation list ever contains
more than the resource check, the case has stopped demonstrating mandate conformance and
started demonstrating an ordinary policy engine.

This is two paths. §7 is explicit that four demo paths cannot prove the verdicts are not
hard-coded; the bar for that is the §9 step 8 corpus with independent labels plus the §7.3
ablation, both Gate S2. Per D-018, "end-to-end" here begins at a CONSTRUCTED action —
agent proposal generation is §9 step 7.`);

await signer.close().catch(() => {});
signerProc.kill("SIGKILL");
node.kill("SIGKILL");
