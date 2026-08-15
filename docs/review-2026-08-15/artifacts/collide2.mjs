import {keccak_256} from "../../../ts/node_modules/@noble/hashes/sha3.js";
import {appendFileSync} from "node:fs";

// Find a signature in the transcriber's OWN supported grammar whose 4-byte selector equals
// a Sentinel schema selector but whose declared word count differs.
//   approve(address,uint256)              0x095ea7b3  -> 2 words
//   purchase(bytes32,address,uint64,bool) 0xc188528b  -> 4 words
// Search form: <name>(bytes32)  -> 1 word.  bytes32 is a supported static type.
const TARGETS = new Map([
    [0x095ea7b3 >>> 0, "approve(address,uint256)"],
    
]);

const seed = Number(process.argv[2] ?? 0);
const OUT = "/private/tmp/claude-501/-Users-johnfite-Projects/f4a114ae-7fd0-4704-8971-a83564ca72ef/scratchpad/HIT2.txt";

// name = "f" + 10 chars from ALPHABET, then "(uint256,uint256)"
const ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_$";
const NAMELEN = 10;
const enc = new TextEncoder();
const prefix = "f";
const suffix = "(uint256,uint256)";
const total = prefix.length + NAMELEN + suffix.length;
const buf = new Uint8Array(total);
buf.set(enc.encode(prefix), 0);
buf.set(enc.encode(suffix), prefix.length + NAMELEN);

// deterministic per-worker stream via a 64-bit LCG on BigInt-free split state
let s0 = (seed * 0x9e3779b1) >>> 0 || 1;
let s1 = (seed * 0x85ebca6b + 0x165667b1) >>> 0 || 2;
function nextU32() {
    // xorshift128
    let t = s0 ^ (s0 << 11);
    t ^= t >>> 8;
    s0 = s1;
    s1 = (s1 ^ (s1 >>> 19) ^ t) >>> 0;
    return s1;
}

let tried = 0;
const t0 = Date.now();
for (;;) {
    // fill the name with random alphabet chars
    for (let k = 0; k < NAMELEN; k += 5) {
        let r = nextU32();
        for (let j = 0; j < 5 && k + j < NAMELEN; j++) {
            buf[prefix.length + k + j] = ALPHABET.charCodeAt(r % 63);
            r = (r / 63) | 0;
        }
    }
    const h = keccak_256(buf);
    const sel = ((h[0] << 24) | (h[1] << 16) | (h[2] << 8) | h[3]) >>> 0;
    if (TARGETS.has(sel)) {
        const sig = new TextDecoder().decode(buf);
        const line = `HIT sig=${sig} selector=0x${sel.toString(16).padStart(8, "0")} collides_with=${TARGETS.get(sel)} seed=${seed} tried=${tried}\n`;
        appendFileSync(OUT, line);
        console.log(line);
        process.exit(0);
    }
    tried++;
    if ((tried & 0xffffff) === 0) {
        const rate = tried / ((Date.now() - t0) / 1000) / 1e6;
        console.error(`w${seed}: ${(tried / 1e6).toFixed(0)}M tried, ${rate.toFixed(2)} M/s`);
    }
}
