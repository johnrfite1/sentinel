#!/usr/bin/env python3
"""Targeted mutation driver for the Sentinel review. Operates ONLY on the scratch copy."""
import json, os, subprocess, sys, shutil

ROOT = "/private/tmp/claude-501/-Users-johnfite-Projects/f4a114ae-7fd0-4704-8971-a83564ca72ef/scratchpad/mut"
ENV = dict(os.environ, PATH=os.path.expanduser("~/.foundry/bin") + ":" + os.environ["PATH"])

MUTANTS = json.load(open(sys.argv[1]))
only = sys.argv[2] if len(sys.argv) > 2 else None

def run(kind):
    if kind == "sol":
        p = subprocess.run(["forge", "test"], cwd=ROOT + "/contracts", env=ENV,
                           capture_output=True, text=True, timeout=1800)
    else:
        p = subprocess.run(["npm", "--prefix", "ts", "test"], cwd=ROOT, env=ENV,
                           capture_output=True, text=True, timeout=2400)
    return p.returncode, (p.stdout + p.stderr)

results = []
for m in MUTANTS:
    if only and m["id"] != only:
        continue
    path = os.path.join(ROOT, m["file"])
    orig = open(path).read()
    old, new = m["old"], m["new"]
    if orig.count(old) != 1:
        print(f"{m['id']}: PATTERN NOT UNIQUE ({orig.count(old)} matches) -- SKIPPED", flush=True)
        results.append((m["id"], "SKIP", m["desc"]))
        continue
    open(path, "w").write(orig.replace(old, new))
    try:
        rc, out = run(m["kind"])
    finally:
        open(path, "w").write(orig)
    verdict = "SURVIVED" if rc == 0 else "killed"
    tail = ""
    if rc != 0:
        fails = [l for l in out.splitlines() if ("[FAIL" in l or l.strip().startswith("✖") or "not ok" in l)]
        tail = " | ".join(fails[:4])[:400]
    print(f"{m['id']}: {verdict}  -- {m['desc']}\n    {tail}", flush=True)
    results.append((m["id"], verdict, m["desc"]))

print("\n==== SUMMARY ====")
for i, v, d in results:
    print(f"{v:9} {i}  {d}")
