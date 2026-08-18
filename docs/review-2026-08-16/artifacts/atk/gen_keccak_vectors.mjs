import {keccak256} from "viem";
const lens = [0,1,2,31,32,33,63,64,65,100,134,135,136,137,138,150,200,271,272,273,400,543,544,545,1000];
const out = [];
let seed = 1n;
function rnd(){ seed = (seed*6364136223846793005n + 1442695040888963407n) & ((1n<<64n)-1n); return Number((seed>>33n)&0xffn); }
for (const L of lens){
  const b = new Uint8Array(L);
  for (let i=0;i<L;i++) b[i]=rnd();
  out.push({len:L, hex:"0x"+Buffer.from(b).toString("hex"), k:keccak256(b)});
}
// also all-zero and all-ff at boundary lengths
for (const L of [135,136,137]){
  for (const fill of [0x00,0xff]){
    const b = new Uint8Array(L).fill(fill);
    out.push({len:L, hex:"0x"+Buffer.from(b).toString("hex"), k:keccak256(b)});
  }
}
console.log(JSON.stringify(out));
