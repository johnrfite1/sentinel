#!/usr/bin/env python3
"""Mutation campaign against the isolated signer's own checks.

Each mutation deletes or neuters exactly one signer check. A mutation that leaves the
suite GREEN is a check no test exercises.
"""
import subprocess, sys, os, json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = os.path.join(ROOT, "ts/src/signer/attest.ts")
P = os.path.join(ROOT, "ts/src/signer/protocol.ts")
K = os.path.join(ROOT, "ts/src/signer/keystore.ts")

MUTANTS = [
 ("M1 EXECUTABILITY never refuses", P,
  'case "EXECUTABILITY":\n                return verdict !== "BLOCK";',
  'case "EXECUTABILITY":\n                return false;'),
 ("M2 drop action-deadline check", A,
  'if (at > action.deadline) findings.push("SIGNER_ACTION_EXPIRED");', ''),
 ("M3 drop paused check", A,
  'if (state.paused) findings.push("SIGNER_VAULT_PAUSED");', ''),
 ("M4 drop nonce-mismatch check", A,
  'if (action.actionNonce !== state.actionNonce) findings.push("SIGNER_NONCE_MISMATCH");', ''),
 ("M5 drop active-signer check", A,
  'if (state.signer !== keystore.address) findings.push("SIGNER_NOT_ACTIVE_SIGNER");', ''),
 ("M6 nonce guard never conflicts", A,
  'if (guard.conflicts(chainId, vault, action.actionNonce, actionHash, at, basis)) {\n                findings.push("SIGNER_NONCE_ALREADY_ATTESTED");\n            }', ''),
 ("M7 never reserve the nonce", A,
  'const reserved = evaluation.verdict !== "BLOCK";', 'const reserved = false;'),
 ("M8 drop dataHash recomputation", A,
  'if (hashCallData(callData) !== action.dataHash) findings.push("SIGNER_DATAHASH_MISMATCH");', ''),
 ("M9 drop simulation-block anchor check", A,
  'if (simHash === null || simHash !== evaluation.simulationBlockHash) {\n                findings.push("SIGNER_SIMULATION_BLOCK_MISMATCH");\n            }', ''),
 ("M10 drop target codehash check", A,
  'if (mandate.targetCodeHash !== state.targetCodeHash) {\n                    findings.push("SIGNER_TARGET_CODEHASH_MISMATCH");\n                }', ''),
 ("M11 drop domain-separator differential", A,
  'if (state.domainSeparator !== localDomainSeparator) {\n                findings.push("SIGNER_DOMAIN_SEPARATOR_MISMATCH");\n                return await refuse();\n            }', ''),
 ("M12 accept odd-length hex", P,
  'if (v.length % 2 !== 0) fail(path, "an even number of hex digits (whole bytes)");', ''),
 ("M13 accept unknown request fields", P,
  'if (!allowed.includes(k)) throw new ProtocolError(`${path}: unexpected field ${JSON.stringify(k)}`);',
  'void allowed; void path;'),
 ("M14 keystore stops checking receipt.signer", K,
  'if (receipt.signer.toLowerCase() !== address) {', 'if (false) {'),
 ("M15 reserve AFTER signing (reopen the race)", A,
  '''            const reserved = evaluation.verdict !== "BLOCK";
            if (reserved) {
                guard.record(chainId, vault, action.actionNonce, actionHash, expiresAt, basis);
            }

            let signature: Hex;
            try {
                signature = await keystore.signReceipt(receipt);
            } catch (err) {''',
  '''            const reserved = evaluation.verdict !== "BLOCK";

            let signature: Hex;
            try {
                signature = await keystore.signReceipt(receipt);
                if (reserved) {
                    guard.record(chainId, vault, action.actionNonce, actionHash, expiresAt, basis);
                }
            } catch (err) {'''),
 ("M16 drop mandate-active hash check", A,
  'if (!mandateActive) findings.push("SIGNER_MANDATE_NOT_ACTIVE");', ''),
 ("M17 drop reason-code pattern check at the RPC boundary", P,
  '''        if (!REASON_CODE_PATTERN.test(code)) {
            fail(`params.evaluation.reasonCodes[${i}]`, `to match ${REASON_CODE_PATTERN.source}`);
        }''', ''),
 ("M18 D-014 target-branch: drop the A-028 F1 ALLOW guard", A,
  'return requestedVerdict === "ALLOW" ? ["SIGNER_EVIDENCE_DECODING_MISMATCH"] : [];',
  'return [];'),
 ("M19 D-014 non-target branch: blanket escape hatch", A,
  'return mine.ok ? ["SIGNER_EVIDENCE_DECODING_MISMATCH"] : [];', 'return [];'),
 ("M20 drop the vault-unreachable fail-closed", A,
  'findings.push("SIGNER_VAULT_UNREACHABLE");\n                return await refuse();',
  'return await refuse();'),
]

results = []
for name, path, old, new in MUTANTS:
    src = open(path).read()
    if old not in src:
        results.append((name, "PATCH-MISS"))
        print(f"{name}: PATCH DID NOT APPLY", flush=True)
        continue
    open(path, "w").write(src.replace(old, new, 1))
    try:
        r = subprocess.run(["npm", "--prefix", "ts", "test"], cwd=ROOT,
                           capture_output=True, text=True, timeout=1800,
                           env={**os.environ, "PATH": os.path.expanduser("~/.foundry/bin") + ":" + os.environ["PATH"]})
        status = "CAUGHT" if r.returncode != 0 else "SURVIVED"
        fails = [l for l in r.stdout.splitlines() if l.startswith("ℹ fail")]
        print(f"{name}: {status}  {fails}", flush=True)
        results.append((name, status))
    finally:
        open(path, "w").write(src)

print("\n=== SURVIVORS ===")
for n, s in results:
    if s != "CAUGHT":
        print(" ", s, n)
print(f"\n{sum(1 for _, s in results if s=='CAUGHT')}/{len(results)} caught")
