// R4-as-adjudicator, independent probe for R2-F1.
// Runs the REAL simulateAction from worktree w4 against a stub chain in which one block
// arrives immediately after the anchor getBlock(). Then asks the question R2 did not:
// what does the E3 anchor check in attest.ts do with the resulting receipt?
import {simulateAction} from "<REVIEW-ROOT>/worktrees/w4/ts/src/simulate/index.ts";

const VAULT = "0x1111111111111111111111111111111111111111";
const TARGET = "0x2222222222222222222222222222222222222222";
const H10 = "0xaaaa000000000000000000000000000000000000000000000000000000000010";
const H11 = "0xbbbb000000000000000000000000000000000000000000000000000000000011";

let head = 10n;
let headHash = H10;
let getBlockCalls = 0;
const trace: string[] = [];

// vault balance differs per block, so a read served at the wrong block is visible
const balanceAt = (blk: bigint) => (blk === 10n ? 5000n : 999000n);

const client: any = {
    async getBlock(args?: {blockNumber?: bigint}) {
        getBlockCalls += 1;
        if (args?.blockNumber !== undefined) {
            return {number: args.blockNumber, hash: args.blockNumber === 10n ? H10 : H11};
        }
        const b = {number: head, hash: headHash};
        trace.push(`  getBlock() -> block ${head}  (LATEST, unpinned)`);
        if (getBlockCalls === 1) {
            head = 11n; headHash = H11;
            trace.push(`  *** an external block arrives: head 10 -> 11 ***`);
        }
        return b;
    },
    async getBalance({address}: {address: string}) {
        trace.push(`  getBalance(${address.slice(0,6)}) served at block ${head}   <-- NO blockNumber pin`);
        return address.toLowerCase() === VAULT ? balanceAt(head) : 0n;
    },
    async waitForTransactionReceipt() {
        return {status: "success", gasUsed: 21000n, logs: []};
    },
};

const control: any = {
    async snapshot() { trace.push(`  evm_snapshot at head ${head}`); return "0x1"; },
    async revert() { trace.push(`  evm_revert -> head back to ${head}`); return true; },
    async impersonate() {}, async stopImpersonating() {}, async setNextBlockBaseFee() {},
    async sendFrom() { trace.push(`  eth_sendTransaction (executes)`); return "0xdead"; },
    async traceTransaction() { return {type: "CALL", from: VAULT, to: TARGET, calls: []}; },
};

const sim = await simulateAction({
    client, vault: VAULT as any, target: TARGET as any,
    valueWei: 1000n, callData: "0x" as any, decoded: null, control,
});

console.log("--- RPC trace as the simulator issued it ---");
for (const t of trace) console.log(t);

const vaultDelta = sim.nativeBalanceDeltas.find((d: any) => d.address === VAULT);
console.log("\n--- what the simulator produced ---");
console.log(`  anchor.blockNumber          = ${sim.anchor.blockNumber}`);
console.log(`  anchor.blockHash            = ${sim.anchor.blockHash.slice(0,10)}...`);
console.log(`  vault balance BEFORE        = ${vaultDelta?.before}   (block 10 value is 5000; block 11 is 999000)`);
console.log(`  head after the simulation   = ${head}`);
const straddle = vaultDelta?.before !== balanceAt(sim.anchor.blockNumber);
console.log(`  STRADDLE PRESENT            = ${straddle}`);

// ---- the step R2 omitted: the signer runs NEXT, on the same chain ----
// vault.ts readVaultState pins to its head-confirmed block, which can only be >= the block
// the simulator's unpinned reads were served at. attest.ts:440 is the E3 comparison.
const signerObservedAtBlock = head;             // signer runs after the simulation
const signerObservedBlockHash = headHash;
const findings: string[] = [];
if (
    sim.anchor.blockNumber !== signerObservedAtBlock ||
    sim.anchor.blockHash !== signerObservedBlockHash
) {
    findings.push("SIGNER_ANCHOR_NOT_OBSERVED");
}
console.log("\n--- attest.ts:440-445, the E3 anchor check, applied to this receipt ---");
console.log(`  evaluation.simulationBlockNumber = ${sim.anchor.blockNumber}`);
console.log(`  state.observedAtBlock            = ${signerObservedAtBlock}`);
console.log(`  findings                         = ${JSON.stringify(findings)}`);
console.log(`\nRESULT: ${findings.length > 0
    ? "the straddled simulation is REFUSED by the signer. No receipt is issued."
    : "the straddled simulation would be SIGNED."}`);
