import {createAttestor} from "../src/signer/attest.ts";
import {buildFixture, fakeKeystore, CHAIN_ID, VAULT, NOW} from "../test/fakes.ts";
import {canonicalize} from "../src/evaluate/jcs.ts";
import {parseEvaluateAndSignRequest} from "../src/signer/protocol.ts";
import {decodeBySelector} from "../src/decode/index.ts";
import {CALLDATA} from "../test/fakes.ts";

const d = decodeBySelector(CALLDATA);
const emoji = "purchase approved \u{1F600}";
const truncated = emoji.slice(0, emoji.length - 1);   // lone HIGH surrogate

const bundle = {
    schema: "sentinel.evidence.v0.2",
    aiExplanation: truncated,
    decodedSelectorAndParameters: d.ok
        ? {decoded:"true", selector:d.selector, schema:d.decoded.schema,
           parameters: d.decoded.schema==="DemoPay.purchase"
             ? {resourceId:d.decoded.resourceId, beneficiary:d.decoded.beneficiary,
                durationSeconds:d.decoded.durationSeconds.toString(), recurring:d.decoded.recurring}
             : {spender:d.decoded.spender, amount:d.decoded.amount.toString()}}
        : {decoded:"false", selector:d.selector ?? "", failureCode:d.code},
};
const evidenceCanonical = canonicalize(bundle);
console.log("evidenceCanonical contains a lone surrogate escape:", evidenceCanonical.includes("\\ud83d"));

const f = buildFixture({evidenceCanonical});
// prove the RPC boundary parser accepts it too
const wire = JSON.parse(JSON.stringify(f.request, (k,v)=> typeof v==="bigint"? v.toString(): v));
try { parseEvaluateAndSignRequest(wire); console.log("RPC parser (protocol.ts): ACCEPTED"); }
catch(e){ console.log("RPC parser REJECTED:", e.message); }

const att = createAttestor({chainId: CHAIN_ID, vault: VAULT, keystore: fakeKeystore(),
                            chain: f.chain, now: ()=>NOW});
const res = await att.evaluateAndSign(f.request);
if (res.refused) { console.log("SIGNER REFUSED:", JSON.stringify(res.blocking)); }
else {
  console.log("SIGNER SIGNED an ALLOW receipt.");
  console.log("  verdict       =", res.receipt.verdict);
  console.log("  evidenceHash  =", res.receipt.evidenceHash);
  console.log("  signature     =", res.signature.slice(0,20)+"...");
}
