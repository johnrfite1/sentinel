import {readFileSync} from "node:fs";
import {canonicalize} from "../src/evaluate/jcs.ts";
const cases = JSON.parse(readFileSync("ts/atk/jcs_cases.json","utf8"));
const out = {};
for (const [name, text] of Object.entries(cases)){
  let rec;
  try {
    const v = JSON.parse(text);
    const c = canonicalize(v);
    rec = {ok:true, canonical:c, hexbytes: Buffer.from(c,"utf8").toString("hex")};
  } catch(e){ rec = {ok:false, err: `${e.constructor.name}: ${e.message.slice(0,90)}`}; }
  out[name] = rec;
}
console.log(JSON.stringify(out,null,1));
