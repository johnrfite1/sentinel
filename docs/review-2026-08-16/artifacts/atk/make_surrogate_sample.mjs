import {readFileSync, writeFileSync} from "node:fs";
import {canonicalize} from "../src/evaluate/jcs.ts";
import {keccak256, stringToBytes} from "viem";
const dir = "/tmp/sur/case-1-surrogate";
const ev = JSON.parse(readFileSync(dir+"/evidence.json","utf8"));

// The §6 explanation layer carries free text. A truncated emoji — the single most
// common way a lone surrogate enters a JS string — splits a UTF-16 pair.
const emoji = "purchase approved \u{1F600}";
ev.aiExplanation = emoji.slice(0, emoji.length - 1);   // drops the LOW surrogate
console.log("aiExplanation code units:", [...ev.aiExplanation].map(c=>c.codePointAt(0).toString(16)).join(" "));

// Sentinel's OWN canonicalizer + its own evidenceHash. No tampering: this is the
// evaluator's normal output path for this bundle.
const canon = canonicalize(ev);
const hash  = keccak256(stringToBytes(canon));
writeFileSync(dir+"/evidence.json", JSON.stringify(ev));
writeFileSync(dir+"/evidence.canonical.json", canon);
writeFileSync(dir+"/evidence.hash", hash);
console.log("TS canonicalize(): OK,", Buffer.byteLength(canon,"utf8"), "bytes");
console.log("TS evidenceHash  :", hash);
console.log("canonical tail   :", JSON.stringify(canon.slice(canon.indexOf('"aiExplanation"'), canon.indexOf('"aiExplanation"')+45)));
