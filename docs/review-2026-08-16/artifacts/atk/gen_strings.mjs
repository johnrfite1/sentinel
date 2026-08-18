import {canonicalize} from "../src/evaluate/jcs.ts";
const out = [];
function push(label, s){
  let r;
  try { const c = canonicalize({a:s}); r = Buffer.from(c,"utf8").toString("hex"); }
  catch(e){ r = "ERR:"+e.constructor.name; }
  out.push([label, Buffer.from(s,"utf16le").toString("hex"), r]);
}
for (let cp=0; cp<=0x2FFF; cp++) push("cp"+cp, String.fromCodePoint(cp));
for (let cp=0xD7F0; cp<=0xE010; cp++) push("cp"+cp, String.fromCharCode(cp)); // includes lone surrogates
for (const cp of [0xFFFD,0xFFFE,0xFFFF,0x10000,0x1F600,0x10FFFF,0x2028,0x2029,0xFEFF])
  push("cp"+cp, String.fromCodePoint(cp));
// combining / mixed
push("mixed", "áb😀c");
push("halfpair", "a\uD83Dc");        // high surrogate alone in the middle
push("halfpair2", "a\uDE00c");       // low surrogate alone
console.log(JSON.stringify(out));
