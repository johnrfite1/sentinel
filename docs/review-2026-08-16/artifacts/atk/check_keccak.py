import json, sys, os
sys.path.insert(0, os.path.abspath("verifier"))
from keccak import keccak256
vs = json.load(open("ts/atk/kv.json"))
bad = 0
for v in vs:
    raw = bytes.fromhex(v["hex"][2:])
    got = "0x" + keccak256(raw).hex()
    if got != v["k"]:
        bad += 1
        print("MISMATCH len=%d viem=%s py=%s" % (v["len"], v["k"], got))
print("keccak differential: %d vectors, %d mismatches" % (len(vs), bad))
