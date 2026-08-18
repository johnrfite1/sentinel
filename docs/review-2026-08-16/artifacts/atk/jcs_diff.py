import json
ts = json.load(open("ts/atk/jcs_ts.json"))
py = json.load(open("ts/atk/jcs_py.json"))
print("%-20s %-34s %-34s %s" % ("CASE","TS","PY","AGREE?"))
for k in ts:
    t, p = ts[k], py[k]
    tv = t.get("hexbytes") if t["ok"] else "ERR("+t["err"].split(":")[0]+")"
    pv = p.get("hexbytes") if p["ok"] else "ERR("+p["err"].split(":")[0]+")"
    agree = "SAME" if tv == pv else ("BOTH-ERR" if (not t["ok"] and not p["ok"]) else "*** DIVERGE ***")
    tdisp = t.get("canonical") if t["ok"] else tv
    pdisp = p.get("canonical") if p["ok"] else pv
    print("%-20s %-34r %-34r %s" % (k, tdisp, pdisp, agree))
