import * as S from "../src/signer/eip712.ts";
import * as E from "../src/evaluate/hashes.ts";
const M=(1n<<256n)-1n;
let seed=0x243F6A8885A308D3n;
function rnd(bits){ // xorshift
  let acc=0n;
  for(let i=0;i<4;i++){ seed^=seed<<13n; seed&=M; seed^=seed>>7n; seed^=seed<<17n; seed&=M; acc=(acc<<64n)|(seed&((1n<<64n)-1n)); }
  return acc & ((1n<<BigInt(bits))-1n);
}
const hexN=(n,bytes)=>"0x"+n.toString(16).padStart(bytes*2,"0").slice(-bytes*2);
const out=[];
const edge=[0n,1n,2n];
for(let i=0;i<120;i++){
  const pick=(bits)=> i<6 ? [0n,1n,(1n<<BigInt(bits))-1n,(1n<<BigInt(bits))-2n,2n,7n][i%6] & ((1n<<BigInt(bits))-1n) : rnd(bits);
  const m={schemaVersion:pick(16),mandateId:hexN(rnd(256),32),principal:hexN(rnd(160),20),
    vault:hexN(rnd(160),20),chainId:pick(256),target:hexN(rnd(160),20),
    targetCodeHash:hexN(rnd(256),32),selector:hexN(rnd(32),4),maxNativeValueWei:pick(256),
    purposeKind:hexN(rnd(256),32),resourceId:hexN(rnd(256),32),beneficiary:hexN(rnd(160),20),
    durationSeconds:pick(64),recurringAllowed:(rnd(1)===1n),validAfter:pick(64),validUntil:pick(64),
    policyHash:hexN(rnd(256),32)};
  const p={schemaVersion:pick(16),policyVersion:pick(32),vault:hexN(rnd(160),20),chainId:pick(256),
    allowedOperation:pick(8),allowedTargetsHash:hexN(rnd(256),32),allowedSelectorsHash:hexN(rnd(256),32),
    maxNativeValueWei:pick(256),maxAllowanceIncreaseBaseUnits:pick(256),
    allowedCallGraphHash:hexN(rnd(256),32),validAfter:pick(64),validUntil:pick(64),failureMode:pick(8)};
  const a={schemaVersion:pick(16),chainId:pick(256),vault:hexN(rnd(160),20),actionNonce:pick(256),
    target:hexN(rnd(160),20),valueWei:pick(256),dataHash:hexN(rnd(256),32),operation:pick(8),
    mandateHash:hexN(rnd(256),32),policyHash:hexN(rnd(256),32),deadline:pick(64)};
  const r={schemaVersion:pick(16),decisionId:hexN(rnd(256),32),actionHash:hexN(rnd(256),32),
    mandateHash:hexN(rnd(256),32),policyHash:hexN(rnd(256),32),verdict:pick(8),
    reasonCodesHash:hexN(rnd(256),32),evidenceHash:hexN(rnd(256),32),simulationBlockNumber:pick(256),
    simulationBlockHash:hexN(rnd(256),32),issuedAt:pick(64),expiresAt:pick(64),signer:hexN(rnd(160),20)};
  const o={schemaVersion:pick(16),reviewReceiptHash:hexN(rnd(256),32),actionHash:hexN(rnd(256),32),
    mandateHash:hexN(rnd(256),32),policyHash:hexN(rnd(256),32),actionNonce:pick(256),
    reasonHash:hexN(rnd(256),32),issuedAt:pick(64),expiresAt:pick(64)};
  const chainId=pick(256), vault=hexN(rnd(160),20);
  out.push({m,p,a,r,o,chainId,vault,
    h:{mandate:S.hashMandate(m),policy:S.hashPolicy(p),action:S.hashAction(a),
       receipt:S.hashReceipt(r),override:S.hashOverride(o),domain:S.domainSeparator(chainId,vault)},
    e:{mandate:E.hashMandate(m),policy:E.hashPolicy(p),action:E.hashAction(a),
       domain:E.domainSeparator(chainId,vault)}});
}
const ser=(x)=>JSON.stringify(x,(k,v)=>typeof v==="bigint"?v.toString():v);
console.log(ser(out));
