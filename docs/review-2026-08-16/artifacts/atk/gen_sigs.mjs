import {privateKeyToAccount} from "viem/accounts";
import {keccak256, toBytes, recoverAddress} from "viem";
const N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141n;
const out = [];
for (let i=1;i<=25;i++){
  const pk = ("0x"+i.toString(16).padStart(64,"0"));
  const acct = privateKeyToAccount(pk);
  const digest = keccak256(toBytes("0x"+(i*7).toString(16).padStart(64,"0")));
  const sig = await acct.sign({hash: digest});
  const r = sig.slice(2,66), s = BigInt("0x"+sig.slice(66,130)), v = parseInt(sig.slice(130,132),16);
  const sMal = N - s;
  const vMal = v === 27 ? 28 : 27;
  const mal = "0x"+r+sMal.toString(16).padStart(64,"0")+vMal.toString(16).padStart(2,"0");
  let malRecovered = null;
  try { malRecovered = await recoverAddress({hash:digest, signature: mal}); } catch(e){ malRecovered = "VIEM_REJECTS:"+e.name; }
  out.push({addr: acct.address.toLowerCase(), digest, sig, mal, sLow: s <= N/2n,
            malRecoveredByViem: typeof malRecovered==="string"?malRecovered.toLowerCase():malRecovered});
}
console.log(JSON.stringify(out,null,0));
