import {createAttestor} from "../src/signer/attest.ts";
import {buildFixture, fakeKeystore, CHAIN_ID, VAULT, NOW, CALLDATA} from "../test/fakes.ts";
import {canonicalize} from "../src/evaluate/jcs.ts";
import {keccak256, stringToBytes} from "viem";
import {decodeBySelector} from "../src/decode/index.ts";

const d = decodeBySelector(CALLDATA);
const dsp = d.ok
  ? {decoded:"true", selector:d.selector, schema:d.decoded.schema,
     parameters: d.decoded.schema==="DemoPay.purchase"
       ? {resourceId:d.decoded.resourceId, beneficiary:d.decoded.beneficiary,
          durationSeconds:d.decoded.durationSeconds.toString(), recurring:d.decoded.recurring}
       : {spender:d.decoded.spender, amount:d.decoded.amount.toString()}}
  : {decoded:"false", selector:d.selector ?? "", failureCode:d.code};

// Deliberately NOT RFC 8785: pretty-printed, keys in the wrong order, trailing newline.
const noncanonical = JSON.stringify({zzz:"last", decodedSelectorAndParameters:dsp, aaa:"first"}, null, 2) + "\n";
const canonical    = canonicalize({zzz:"last", decodedSelectorAndParameters:dsp, aaa:"first"});
console.log("bytes the signer is handed are canonical?", noncanonical === canonical);

const f = buildFixture({evidenceCanonical: noncanonical});
const att = createAttestor({chainId:CHAIN_ID, vault:VAULT, keystore:fakeKeystore(), chain:f.chain, now:()=>NOW});
const res = await att.evaluateAndSign(f.request);
console.log(res.refused ? "signer refused" : "signer SIGNED an ALLOW receipt over non-canonical evidence bytes");
if (!res.refused) {
  console.log("  receipt.evidenceHash =", res.receipt.evidenceHash);
  console.log("  keccak(non-canonical)=", keccak256(stringToBytes(noncanonical)));
  console.log("  keccak(RFC 8785 form)=", keccak256(stringToBytes(canonical)));
  console.log("  -> a D-010 verifier recanonicalizing the bundle computes the third value and reports FAIL");
}
