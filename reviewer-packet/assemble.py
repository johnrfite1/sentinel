#!/usr/bin/env python3
"""Assemble the private reviewer packet from on-disk sample bundles.

Private handoff only. Fixture bytes are copied as they stand. The EIP-712
domain name is a signature preimage in `bundles/domain.json` and is rendered
under Cryptographically bound on every dashboard case screen; this packet is
not name-agnostic. Not a live Anvil walkthrough. Not a public URL.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
SAMPLES = REPO / "fixtures" / "samples"
VERIFIER_SRC = REPO / "verifier"

CASE_IDS = [
    "case-1-allow",
    "case-2-injection-block",
    "case-3-wrong-purpose-block",
    "case-4-review-failmode-review",
    "case-4-blocked-failmode-failclosed",
]

VERIFIER_FILES = [
    "verify.py",
    "eip712.py",
    "jcs.py",
    "keccak.py",
    "secp256k1.py",
    "reasoncodes.py",
    "refusal.py",
]

# D-034: compares the call or its simulated effects to mandate PURPOSE fields.
PURPOSE_CODES = {
    "EVAL_PURCHASE_RESOURCE",
    "EVAL_PURCHASE_BENEFICIARY",
    "EVAL_PURCHASE_DURATION",
    "EVAL_PURCHASE_RECURRENCE",
    "EVAL_ENTITLEMENT_ADVANCED",
    "EVAL_ENTITLEMENT_RECURRENCE",
    "EVAL_ENTITLEMENT_UNOBSERVED",
    "EVAL_APPROVAL_SPENDER",
}

# The mechanically-valid set the sample-check walk prints for Case 3.
MECHANICAL_CODES = [
    "EVAL_CHAIN_BOUND",
    "EVAL_VAULT_BOUND",
    "EVAL_TARGET_BOUND",
    "EVAL_SELECTOR_BOUND",
    "EVAL_VALUE_WITHIN_POLICY",
    "EVAL_VALUE_WITHIN_VAULT_CAP",
    "EVAL_OPERATION_SUPPORTED",
    "EVAL_SIMULATION_SUCCEEDS",
]

EVIDENCE_CODES = ["EVAL_TARGET_CODE_IDENTITY"]

VERDICT_NAMES = {"0": "BLOCK", "1": "REVIEW", "2": "ALLOW"}
FAILURE_MODE_NAMES = {"0": "FAIL_CLOSED", "1": "REVIEW"}


def load_json(path: Path):
    return json.loads(path.read_text())


def short_hex(value: str, head=10, tail=6) -> str:
    if not isinstance(value, str) or not value.startswith("0x") or len(value) < 20:
        return str(value)
    return f"{value[: head + 2]}…{value[-tail:]}"


def check_map(evidence: dict) -> dict:
    return {c["code"]: c for c in evidence.get("policyChecks", [])}


def case_payload(case_id: str) -> dict:
    d = SAMPLES / case_id
    meta = load_json(d / "meta.json")
    mandate = load_json(d / "mandate.json")
    action = load_json(d / "action.json")
    policy = load_json(d / "policy.json")
    evidence = load_json(d / "evidence.json")
    receipt_doc = load_json(d / "receipt.json")
    domain = load_json(SAMPLES / "domain.json")
    override = None
    if (d / "override.json").is_file():
        override = load_json(d / "override.json")

    decoded = evidence.get("decodedSelectorAndParameters") or {}
    params = decoded.get("parameters") or {}
    receipt = receipt_doc.get("receipt") or {}
    checks = check_map(evidence)

    def pack(codes):
        rows = []
        for code in codes:
            row = checks.get(code)
            if not row:
                continue
            rows.append(
                {
                    "code": code,
                    "outcome": row.get("outcome", ""),
                    "detail": row.get("detail") or "",
                }
            )
        return rows

    other = []
    known = set(MECHANICAL_CODES) | PURPOSE_CODES | set(EVIDENCE_CODES)
    for row in evidence.get("policyChecks", []):
        if row["code"] in known:
            continue
        if row.get("outcome") in ("VIOLATION", "UNRESOLVED"):
            other.append(
                {
                    "code": row["code"],
                    "outcome": row["outcome"],
                    "detail": row.get("detail") or "",
                }
            )

    return {
        "id": case_id,
        "title": meta.get("title", case_id),
        "note": meta.get("note", ""),
        "verdict": meta.get("verdict", ""),
        "receiptVerdict": VERDICT_NAMES.get(str(receipt.get("verdict")), str(receipt.get("verdict"))),
        "failureMode": FAILURE_MODE_NAMES.get(str(policy.get("failureMode")), str(policy.get("failureMode"))),
        "reasonCodes": receipt_doc.get("reasonCodes") or meta.get("reasonCodes") or [],
        "signerFindings": receipt_doc.get("signerFindings") or [],
        "signerRefused": bool(receipt_doc.get("refused")),
        "hasOverride": override is not None,
        "decodedDescription": decoded.get("description") or "",
        "decodedSchema": decoded.get("schema") or "",
        "simulationOutcome": (evidence.get("observedPostState") or {}).get("outcome"),
        "bound": {
            "domainName": domain.get("name"),
            "domainVersion": domain.get("version"),
            "chainId": mandate.get("chainId"),
            "vault": mandate.get("vault"),
            "mandateTarget": mandate.get("target"),
            "actionTarget": action.get("target"),
            "mandateSelector": mandate.get("selector"),
            "decodedSelector": decoded.get("selector"),
            "mandateResource": mandate.get("resourceId"),
            "decodedResource": params.get("resourceId"),
            "mandateBeneficiary": mandate.get("beneficiary"),
            "decodedBeneficiary": params.get("beneficiary"),
            "decodedSpender": params.get("spender"),
            "mandateDuration": mandate.get("durationSeconds"),
            "decodedDuration": params.get("durationSeconds"),
            "decodedAmount": params.get("amount"),
            "mandateRecurring": mandate.get("recurringAllowed"),
            "decodedRecurring": params.get("recurring"),
            "maxNativeValueWei": mandate.get("maxNativeValueWei"),
            "actionValueWei": action.get("valueWei"),
            "actionHash": receipt.get("actionHash"),
            "mandateHash": receipt.get("mandateHash"),
            "policyHash": receipt.get("policyHash"),
            "evidenceHash": receipt.get("evidenceHash"),
            "reasonCodesHash": receipt.get("reasonCodesHash"),
            "signer": receipt.get("signer"),
            "simulationBlockNumber": receipt.get("simulationBlockNumber"),
            "simulationBlockHash": receipt.get("simulationBlockHash"),
            "codePinned": (evidence.get("targetCodeIdentity") or {}).get("pinnedByMandate"),
            "codeObserved": (evidence.get("targetCodeIdentity") or {}).get("observedOnChain"),
            "codeMatches": (evidence.get("targetCodeIdentity") or {}).get("matches"),
        },
        "mechanical": pack(MECHANICAL_CODES),
        "purpose": pack(sorted(PURPOSE_CODES)),
        "evidenceChecks": pack(EVIDENCE_CODES),
        "otherAdverse": other,
        "ownerSignedOverride": bool(override and override.get("ownerSignature")),
        "ownerAddress": (override or {}).get("ownerAddress"),
    }


def copy_packet() -> None:
    bundles = ROOT / "bundles"
    if bundles.exists():
        shutil.rmtree(bundles)
    bundles.mkdir()
    shutil.copy2(SAMPLES / "domain.json", bundles / "domain.json")
    for case_id in CASE_IDS:
        dest = bundles / case_id
        shutil.copytree(SAMPLES / case_id, dest)
    verifier = ROOT / "verifier"
    if verifier.exists():
        shutil.rmtree(verifier)
    verifier.mkdir()
    for name in VERIFIER_FILES:
        shutil.copy2(VERIFIER_SRC / name, verifier / name)


SCRIPT = """# Demonstration packet — one-page script

Private handoff. No repository. No live chain. No network.

You have three things: this page, a static case viewer, and a Python verifier
that re-checks pre-baked signed receipts.

## 1. Open the case viewer

Open `dashboard/index.html` in a browser. It is a local file. It does not
call a server and does not drive a signer.

Five screens:

- **Case 1** — the call matches the mandate. ALLOW.
- **Case 2** — the agent proposed a different call (unlimited approval to an
  attacker). BLOCK. Caught from the decoded call, not from the agent's story.
- **Case 3** — the load-bearing case. The call is mechanically valid and the
  simulation succeeds. It still BLOCKs because the **purpose** is wrong
  (a different resource than the mandate authorised). Not because the call
  "looks dangerous."
- **Case 4 · REVIEW** and **Case 4 · FAIL_CLOSED** — identical evidence gap
  (target code hash no longer matches the pin). The policy's `failureMode`
  is the only difference. Unresolved is not "malicious."

On every screen, look for: what is bound; who signs what; the check colours;
what the receipt claims; what it does not claim.

## 2. Verify a receipt offline

Needs Python 3.8+ and nothing else. From this packet's root:

```
python3 verifier/verify.py --domain bundles/domain.json bundles/case-1-allow
python3 verifier/verify.py --domain bundles/domain.json bundles/case-3-wrong-purpose-block
```

`--domain` is the trust root **you** assert (the deployment's signer identity).
A bundle that only carries its own copy of that file cannot certify itself.
Without `--domain` the tool reports diagnostics and does not PASS.

Case 3's receipt should still verify: BLOCK is a signed decision, not a
missing artifact.

Optional self-test (mutates a copy in memory; does not write your files):

```
python3 verifier/verify.py --tamper --domain bundles/domain.json bundles/case-1-allow
```

## 3. What you are not being asked to do

Do not start Anvil, Node, Foundry, or a signer. Do not clone a repository.
Do not treat a verified receipt as proof that the simulation is still true
of a chain, or that the target code is benign.
"""


def html_escape(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def write_dashboard(cases: list) -> None:
    dash = ROOT / "dashboard"
    dash.mkdir(exist_ok=True)
    data = json.dumps(cases, indent=None)
    page = DASHBOARD_HTML.replace("/*__CASES__*/", data)
    (dash / "index.html").write_text(page)


DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Demonstration cases</title>
<style>
:root {
  --paper: #f3eee4;
  --ink: #161410;
  --muted: #5c564c;
  --rule: #cfc6b6;
  --teal: #0c4a4e;
  --pass: #1a5c38;
  --pass-bg: #dceee3;
  --fail: #8f1d1d;
  --fail-bg: #f4d9d6;
  --warn: #7a4b00;
  --warn-bg: #f3e4c4;
  --allow: #1a5c38;
  --block: #8f1d1d;
  --review: #7a4b00;
}
* { box-sizing: border-box; }
html, body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: "Iowan Old Style", Palatino, "Palatino Linotype", "Book Antiqua", Georgia, serif;
  line-height: 1.35;
}
code, .mono, .hex {
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  font-size: 0.82rem;
}
header.top {
  position: sticky;
  top: 0;
  z-index: 2;
  background: var(--paper);
  border-bottom: 1px solid var(--ink);
  padding: 0.7rem 1.25rem 0.55rem;
}
header.top h1 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
header.top p.kicker {
  margin: 0.15rem 0 0.55rem;
  color: var(--muted);
  font-size: 0.85rem;
}
nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}
nav a {
  color: var(--ink);
  text-decoration: none;
  border: 1px solid var(--ink);
  padding: 0.2rem 0.55rem;
  font-size: 0.82rem;
}
nav a[aria-current="page"] {
  background: var(--ink);
  color: var(--paper);
}
main {
  max-width: 78rem;
  margin: 0 auto;
  padding: 1rem 1.25rem 3rem;
}
.screen { display: none; }
.screen.active { display: block; }
.case-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.75rem 1.25rem;
  border-bottom: 1px solid var(--rule);
  padding-bottom: 0.7rem;
  margin-bottom: 0.9rem;
}
.case-head h2 {
  margin: 0;
  font-size: 1.45rem;
  font-weight: 600;
}
.badge {
  display: inline-block;
  padding: 0.12rem 0.5rem;
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  border: 1px solid currentColor;
  font-family: ui-monospace, Menlo, Consolas, monospace;
}
.badge.ALLOW { color: var(--allow); background: var(--pass-bg); }
.badge.BLOCK { color: var(--block); background: var(--fail-bg); }
.badge.REVIEW { color: var(--review); background: var(--warn-bg); }
.note { color: var(--muted); margin: 0; max-width: 46rem; }
.roles {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.55rem;
  margin: 0.9rem 0 1.1rem;
}
.roles div {
  border-top: 2px solid var(--ink);
  padding-top: 0.35rem;
}
.roles strong { display: block; font-size: 0.92rem; }
.roles span { color: var(--muted); font-size: 0.82rem; }
.grid {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 1.25rem;
}
section h3 {
  margin: 0 0 0.45rem;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  border-bottom: 1px solid var(--ink);
  padding-bottom: 0.2rem;
}
.pair {
  display: grid;
  grid-template-columns: 8.5rem 1fr;
  gap: 0.2rem 0.6rem;
  font-size: 0.9rem;
  margin: 0.15rem 0;
}
.pair .k { color: var(--muted); }
.match { color: var(--pass); }
.mismatch { color: var(--fail); font-weight: 600; }
.hex { word-break: break-all; color: var(--teal); }
.check {
  display: grid;
  grid-template-columns: 5.6rem 1fr;
  gap: 0.25rem 0.5rem;
  margin: 0.22rem 0;
  font-size: 0.86rem;
}
.out {
  font-family: ui-monospace, Menlo, Consolas, monospace;
  font-size: 0.72rem;
  letter-spacing: 0.04em;
  padding: 0.05rem 0.3rem;
  text-align: center;
  align-self: start;
}
.out.PASS { color: var(--pass); background: var(--pass-bg); }
.out.VIOLATION { color: var(--fail); background: var(--fail-bg); }
.out.UNRESOLVED { color: var(--warn); background: var(--warn-bg); }
.detail { color: var(--muted); font-size: 0.8rem; }
.split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.7rem;
  margin-top: 0.35rem;
}
.split .col {
  padding: 0.45rem 0.55rem 0.55rem;
}
.split .col.ok { background: var(--pass-bg); }
.split .col.bad { background: var(--fail-bg); }
.split .col.mid { background: var(--warn-bg); }
.split h4 {
  margin: 0 0 0.35rem;
  font-size: 0.82rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.claims {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 1.15rem;
  border-top: 1px solid var(--ink);
  padding-top: 0.8rem;
}
.claims ul { margin: 0.3rem 0 0; padding-left: 1.1rem; }
.claims li { margin: 0.25rem 0; }
@media (max-width: 900px) {
  .roles, .grid, .split, .claims { grid-template-columns: 1fr; }
}
</style>
</head>
<body>
<header class="top">
  <h1>Demonstration cases</h1>
  <p class="kicker">Exact-action binding · fixture receipts · no live chain</p>
  <nav id="nav"></nav>
</header>
<main id="main"></main>
<script>
const CASES = /*__CASES__*/;

const NAV = [
  ["case-1-allow", "Case 1"],
  ["case-2-injection-block", "Case 2"],
  ["case-3-wrong-purpose-block", "Case 3"],
  ["case-4-review-failmode-review", "Case 4 · REVIEW"],
  ["case-4-blocked-failmode-failclosed", "Case 4 · FAIL_CLOSED"],
];

function esc(s) {
  return String(s ?? "").replace(/[&<>"]/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"
  }[c]));
}
function hx(v) {
  if (v === undefined || v === null || v === "") return "—";
  const s = String(v);
  if (!s.startsWith("0x") || s.length < 22) return esc(s);
  return `<span class="hex" title="${esc(s)}">${esc(s.slice(0,12))}…${esc(s.slice(-6))}</span>`;
}
function same(a, b) {
  if (a === undefined || b === undefined || a === null || b === null) return null;
  return String(a).toLowerCase() === String(b).toLowerCase();
}
function pair(label, left, right) {
  const eq = same(left, right);
  const cls = eq === null ? "" : eq ? "match" : "mismatch";
  const mark = eq === null ? "" : eq ? " match" : " differ";
  return `<div class="pair"><span class="k">${esc(label)}</span><span class="${cls}">${hx(left)} → ${hx(right)}<span class="detail">${mark}</span></span></div>`;
}
function checks(rows) {
  if (!rows.length) return "<p class='detail'>None on this receipt.</p>";
  return rows.map(r => `
    <div class="check">
      <span class="out ${esc(r.outcome)}">${esc(r.outcome)}</span>
      <div><code>${esc(r.code)}</code>${r.detail ? `<div class="detail">${esc(r.detail)}</div>` : ""}</div>
    </div>`).join("");
}

function screen(c) {
  const b = c.bound;
  const purposeFail = c.purpose.some(r => r.outcome === "VIOLATION");
  const mechPass = c.mechanical.every(r => r.outcome === "PASS");
  const ident = c.evidenceChecks[0];
  const identCls = ident && ident.outcome === "UNRESOLVED" ? "mid" : (ident && ident.outcome === "PASS" ? "ok" : "bad");
  const override = c.hasOverride
    ? `<div class="pair"><span class="k">Owner override</span><span>present · owner ${hx(c.ownerAddress)}</span></div>`
    : `<div class="pair"><span class="k">Owner override</span><span>none on this bundle</span></div>`;

  const purposeCol = c.id === "case-3-wrong-purpose-block"
    ? "bad" : (purposeFail ? "bad" : "ok");

  return `
  <article class="screen" id="${esc(c.id)}">
    <div class="case-head">
      <h2>${esc(c.title)}</h2>
      <span class="badge ${esc(c.verdict)}">${esc(c.verdict)}</span>
      <p class="note">${esc(c.note)}</p>
    </div>
    <div class="roles">
      <div><strong>Agent</strong><span>Proposes the call. Does not sign.</span></div>
      <div><strong>Evaluator</strong><span>Compares call and simulated effects to the mandate. Does not sign.</span></div>
      <div><strong>Isolated signer</strong><span>Attests the receipt. Signs.</span></div>
      <div><strong>Vault</strong><span>Enforces the exact action at execution. Does not sign the receipt.</span></div>
    </div>
    <div class="grid">
      <section>
        <h3>Cryptographically bound</h3>
        <div class="pair"><span class="k">EIP-712 domain</span><span>${esc(b.domainName)} v${esc(b.domainVersion)} · chain ${esc(b.chainId)}</span></div>
        <div class="pair"><span class="k">Vault</span><span>${hx(b.vault)}</span></div>
        ${pair("Target", b.mandateTarget, b.actionTarget)}
        ${pair("Selector", b.mandateSelector, b.decodedSelector)}
        ${b.decodedResource != null ? pair("Resource", b.mandateResource, b.decodedResource) : ""}
        ${b.decodedBeneficiary != null ? pair("Beneficiary", b.mandateBeneficiary, b.decodedBeneficiary) : ""}
        ${b.decodedSpender != null ? pair("Spender vs mandate beneficiary", b.mandateBeneficiary, b.decodedSpender) : ""}
        ${b.decodedDuration != null ? pair("Duration (seconds)", b.mandateDuration, b.decodedDuration) : ""}
        ${b.decodedAmount != null ? `<div class="pair"><span class="k">Approval amount</span><span>${hx(b.decodedAmount)}</span></div>` : ""}
        ${b.decodedRecurring != null ? pair("Recurring", b.mandateRecurring, b.decodedRecurring) : ""}
        <div class="pair"><span class="k">Value (wei)</span><span>mandate max ${esc(b.maxNativeValueWei)} · action ${esc(b.actionValueWei)}</span></div>
        <div class="pair"><span class="k">Decoded call</span><span>${esc(c.decodedDescription)}</span></div>
        <div class="pair"><span class="k">actionHash</span><span>${hx(b.actionHash)}</span></div>
        <div class="pair"><span class="k">mandateHash</span><span>${hx(b.mandateHash)}</span></div>
        <div class="pair"><span class="k">policyHash</span><span>${hx(b.policyHash)}</span></div>
        <div class="pair"><span class="k">evidenceHash</span><span>${hx(b.evidenceHash)}</span></div>
        <div class="pair"><span class="k">Receipt signer</span><span>${hx(b.signer)}</span></div>
        <div class="pair"><span class="k">Sim block</span><span>#${esc(b.simulationBlockNumber)} ${hx(b.simulationBlockHash)}</span></div>
        ${override}
        <div class="pair"><span class="k">failureMode</span><span>${esc(c.failureMode)}</span></div>
        <div class="pair"><span class="k">Reason codes</span><span>${c.reasonCodes.length ? esc(c.reasonCodes.join(", ")) : "none"}</span></div>
      </section>
      <section>
        <h3>Checks on this evidence</h3>
        <div class="split">
          <div class="col ${mechPass ? "ok" : "bad"}">
            <h4>Mechanically valid</h4>
            <p class="detail">Chain, vault, target, selector, value, operation, simulation. A call can pass all of these and still be the wrong purchase.</p>
            ${checks(c.mechanical)}
          </div>
          <div class="col ${purposeCol}">
            <h4>Purpose</h4>
            <p class="detail">Resource, beneficiary, duration, recurrence, and the entitlement those imply. Case 3 lives here.</p>
            ${checks(c.purpose)}
          </div>
        </div>
        <div class="col ${identCls}" style="margin-top:0.7rem;padding:0.45rem 0.55rem;">
          <h4 style="margin:0 0 0.35rem;font-size:0.82rem;letter-spacing:0.04em;text-transform:uppercase;">Code identity (evidence, not malice)</h4>
          <p class="detail">Pinned ${ident && b.codePinned ? "" : ""} vs observed. A mismatch is unresolved, not a finding that the target is malicious.</p>
          ${checks(c.evidenceChecks)}
          ${c.otherAdverse.length ? "<p class='detail' style='margin-top:0.6rem'>Other adverse checks</p>" + checks(c.otherAdverse) : ""}
        </div>
      </section>
    </div>
    <div class="claims">
      <section>
        <h3>A verified receipt proves</h3>
        <ul>
          <li>The deployment’s signer attested this verdict over these hashes: action, mandate, policy, evidence, reason codes.</li>
          <li>The signature recovers to the signer named in the trust root you asserted, not a signer the bundle nominated for itself.</li>
          <li>The receipt names the simulation block it was anchored to.</li>
          <li>Anyone with the bundle and that trust root can re-check this offline.</li>
        </ul>
      </section>
      <section>
        <h3>It does not prove</h3>
        <ul>
          <li>That the simulation is still true of any later chain state. Effects were judged at the recorded block. The vault will bind the exact call at execution; it will not re-prove the effects.</li>
          <li>That the target code is benign. A code-hash mismatch is insufficient evidence, not a malice label.</li>
          <li>That the agent was honest, or that a prompt was or was not injected. The agent’s story never enters the bound fields.</li>
          <li>Anything about any other product.</li>
        </ul>
      </section>
    </div>
  </article>`;
}

const main = document.getElementById("main");
const nav = document.getElementById("nav");
main.innerHTML = CASES.map(screen).join("");
nav.innerHTML = NAV.map(([id, label]) => `<a href="#${id}" data-id="${id}">${label}</a>`).join("");

function show(id) {
  const fallback = CASES[0].id;
  const target = CASES.some(c => c.id === id) ? id : fallback;
  document.querySelectorAll(".screen").forEach(el => el.classList.toggle("active", el.id === target));
  document.querySelectorAll("nav a").forEach(a => {
    if (a.getAttribute("data-id") === target) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  });
}
window.addEventListener("hashchange", () => show(location.hash.slice(1)));
show(location.hash.slice(1));
</script>
</body>
</html>
"""


def main() -> int:
    if not SAMPLES.is_dir():
        print("samples missing", file=sys.stderr)
        return 2
    copy_packet()
    cases = [case_payload(cid) for cid in CASE_IDS]
    write_dashboard(cases)
    (ROOT / "SCRIPT.md").write_text(SCRIPT)
    print(f"assembled {ROOT}")
    print("cases:", ", ".join(CASE_IDS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
