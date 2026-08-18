import json, sys, os, traceback
sys.path.insert(0, os.path.abspath("verifier"))
import jcs
cases = json.load(open("ts/atk/jcs_cases.json"))
out = {}
for name, text in cases.items():
    try:
        v = jcs.parse(text)
        c = jcs.canonicalize(v)
        out[name] = {"ok": True, "canonical": c.decode("utf-8","replace"), "hexbytes": c.hex()}
    except Exception as e:
        out[name] = {"ok": False, "err": "%s: %s" % (type(e).__name__, str(e)[:90])}
print(json.dumps(out, indent=1))
