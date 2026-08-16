#!/usr/bin/env bash
# A-036: a fixture's CLASS NAME is a claim about what it exercises, and until now nothing
# checked that claim.
#
# WHY THIS EXISTS. Three times the project has shipped a fixture class that could not fire:
# A-028 F-5 (the injection class was vacuous — the adversarial text never reached the
# pipeline), then F056 (filed `reentrancy-attempt`, decided by the exact-target rule before any
# call-graph check is reached, with a codeless target that cannot re-enter), then F051 (filed
# `unexpected-internal-call`, ALLOWed by every layer, its only distinguishing knob reserved by
# D-025). Each was found by a human or a labeller reading the data. A-036 stated the fix in one
# sentence — assert that each class's fixtures produce at least one failing check the class is
# about — and left it unbuilt. This is it.
#
# WHAT IT ASSERTS. For each scenario class in the corpus, at least one of its fixtures produces
# at least one FAILING check at L3 drawn from the set of checks that class is ABOUT. That is a
# claim about the corpus, not about the engine: it does not say the check is correct, only that
# the class is not decided entirely by machinery unrelated to its name.
#
# WHAT IT CANNOT ASSERT, STATED SO A GREEN LINE IS NOT OVERREAD.
#   - It cannot tell a fixture that exercises its class WELL from one that grazes it. F022 fails
#     EVAL_TARGET_BOUND among four others; this guard counts it, and a reviewer may not.
#   - It reads L3 only. A class exercised at L1 or L2 and not at L3 reads as unexercised here.
#   - Where the corpus delegates a property elsewhere (`primaryEnforcement`), this guard cannot
#     see whether the delegate actually tests it. It reports the delegation and does not credit
#     it. The vault's Foundry suite genuinely tests reentrancy; that is not this guard's word.
#   - IT CANNOT TELL A HONEST MAP FROM A CONVENIENT ONE, and this is measured, not assumed.
#     Seven mutations were run against this guard and six were caught: a baseline entry removed,
#     a stale baseline entry, a map naming a check the engine does not declare, a map entry
#     deleted, a map repointed at a check the fixtures do not fail, and a deleted result file.
#     THE ONE THAT SURVIVED: repointing `altered-calldata-after-receipt` from
#     EVAL_CALLDATA_BINDING to EVAL_PURCHASE_RESOURCE — a check F018 already fails for an
#     unrelated reason. The class stays green while asserting nothing about altered calldata.
#     No mechanical check can close that hole, because the map is a judgement about what a class
#     MEANS. It is closed only by a reader checking the map against §7.1, which is why the map
#     sits in this file with its reasoning rather than in a data file nobody opens.
#
# THE MAP BELOW IS A JUDGEMENT AND IS THE LOAD-BEARING PART. It was authored from §7.1's class
# names and §5.7.1's check descriptions — deliberately NOT from what the fixtures currently
# produce, because a map read off the current results would agree with them by construction and
# assert nothing. That is the exact failure mode this guard exists to catch, and writing the map
# the cheap way would have reproduced it one level up.
#
# DO NOT REPAIR A FAILURE BY EDITING THE MAP. If a class is unexercised, either the fixture is
# wrong or the class is genuinely uncovered. Widening the map until it matches is how this guard
# becomes the fourth instance of the defect it was built for.
set -uo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

RESULTS="fixtures/corpus/results"
FIXTURES="fixtures/corpus/for-labelling"
CHECKS="ts/src/evaluate/checks.ts"

echo "corpus class coverage (A-036) — does each class exercise the class it names?"

# The engine's own declared code surface, read from source rather than transcribed. If a code in
# the map below is renamed in the engine and not here, the map silently stops matching and every
# affected class would read as unexercised — a guard pointed at the wrong thing, which is this
# project's most repeated defect. Validating the map against this list turns that into a loud
# failure instead of a quiet one.
sed -n '/^export const EVAL_CODES = \[/,/^\] as const;/p' "$CHECKS" \
    | grep -oE '"EVAL_[A-Z0-9_]+"' | tr -d '"' | sort -u > /tmp/.sentinel-eval-codes.$$

node - "$RESULTS" "$FIXTURES" "/tmp/.sentinel-eval-codes.$$" <<'NODE'
const fs = require('fs');
const [resultsDir, fixturesDir, codeListPath] = process.argv.slice(2);

const engineCodes = new Set(
  fs.readFileSync(codeListPath, 'utf8').split('\n').map(s => s.trim()).filter(Boolean)
);

// --- The map: class -> the checks that class is ABOUT -----------------------
//
// Authored from §7.1's twenty class names and §5.7.1's descriptions. One entry per §7.1 bullet.
// `CONFORMING` marks the class whose property is that a valid action is ALLOWED with nothing
// failing — the assertion inverts there, and a failing check would be the defect.
const CONFORMING = Symbol('conforming');
const ABOUT = {
  'exact-allowed-and-benign-variation': CONFORMING,
  'boundary-and-over-limit-native-value': [
    'EVAL_VALUE_WITHIN_MANDATE', 'EVAL_VALUE_WITHIN_POLICY', 'EVAL_VALUE_WITHIN_VAULT_CAP'],
  'approvals-finite-oversized-unlimited': [
    'EVAL_APPROVAL_CEILING', 'EVAL_APPROVAL_SPENDER', 'EVAL_ALLOWANCE_EFFECT_WITHIN_CEILING'],
  'wrong-resource-beneficiary-duration-recurrence': [
    'EVAL_PURCHASE_RESOURCE', 'EVAL_PURCHASE_BENEFICIARY', 'EVAL_PURCHASE_DURATION',
    'EVAL_PURCHASE_RECURRENCE', 'EVAL_ENTITLEMENT_ADVANCED', 'EVAL_ENTITLEMENT_RECURRENCE'],
  'altered-calldata-after-receipt': ['EVAL_CALLDATA_BINDING'],
  'wrong-chain-vault-target-mandate-policy': [
    'EVAL_CHAIN_BOUND', 'EVAL_VAULT_BOUND', 'EVAL_TARGET_BOUND', 'EVAL_MANDATE_ACTIVE',
    'EVAL_POLICY_ACTIVE', 'EVAL_ACTION_BINDS_MANDATE_AND_POLICY', 'EVAL_MANDATE_BINDS_POLICY',
    'EVAL_MANDATE_PRINCIPAL_IS_OWNER'],
  'stale-or-reused-action-nonce': ['EVAL_NONCE_CURRENT'],
  'expired-mandate-receipt-or-override': [
    'EVAL_MANDATE_WINDOW', 'EVAL_POLICY_WINDOW', 'EVAL_ACTION_DEADLINE'],
  // §7.1 "Invalid or rotated signer". The evaluator has NO code for signer identity — receipt
  // authentication is the isolated signer's, per §5.7's "active ... signer" and D-010. So this
  // class cannot be exercised at the corpus layer by construction, which is why it is baselined
  // rather than mapped to a code that does not exist.
  'invalid-or-rotated-signer': [],
  'malformed-calldata-or-unknown-selector': [
    'EVAL_CALLDATA_UNDECODABLE', 'EVAL_SELECTOR_BOUND', 'EVAL_OPERATION_SUPPORTED'],
  'runtime-code-change-or-proxy-target': ['EVAL_TARGET_CODE_IDENTITY'],
  'simulation-revert': ['EVAL_SIMULATION_SUCCEEDS'],
  'rpc-simulator-or-context-outage': [
    'EVAL_SIMULATION_UNAVAILABLE', 'EVAL_NATIVE_DELTA_UNOBSERVED',
    'EVAL_ALLOWANCE_EFFECT_UNOBSERVED', 'EVAL_ENTITLEMENT_UNOBSERVED',
    'EVAL_SIM_CALL_TRACE_UNAVAILABLE', 'EVAL_SIM_UNRECOGNISED'],
  // §3.3(8) as clarified by D-030: "conflicting state is a failed rule and blocks". The engine's
  // one self-contradiction check is the principal-is-owner pairing (A-026(c)).
  'conflicting-block-state': ['EVAL_MANDATE_PRINCIPAL_IS_OWNER'],
  // The class's subject is CONTAINMENT of injected narrative, which the corpus runner's leak
  // guard measures — not a check. docs/ablation-report.md says in terms that these fixtures'
  // verdicts "must NOT be read as detections". Mapped to [] for that reason, not overlooked.
  'malicious-retrieved-instructions': [],
  'unexpected-internal-call': ['EVAL_CALL_GRAPH_EXPECTED'],
  'unsupported-multicall-or-delegatecall': ['EVAL_OPERATION_SUPPORTED', 'EVAL_POLICY_OPERATION'],
  'owner-override-and-block-behaviour': [],
  'reentrancy-attempt': ['EVAL_CALL_GRAPH_EXPECTED'],
  'evaluator-or-signer-compromise': ['EVAL_VAULT_NOT_PAUSED'],
};

// --- The baseline: classes known not to be exercised, each with a reason -----
//
// A RATCHET, not an exemption list. A class here is reported on every run and never counted as
// covered. `ruling` records who accepted it. `status` records WHAT KIND of not-covered it is,
// and D-039 exists because that distinction was being lost:
//
//   DELEGATED — the property is proved somewhere else and the fixture SAYS so via
//               primaryEnforcement. Not owed anything. This guard cannot see the delegate and
//               does not credit it; it reports the delegation.
//   RESERVED  — ratified as undrivable in v1. Not owed a fixture until the reservation lifts.
//   GAP       — the class claims to be proved HERE and is not, and nothing else covers it.
//               OWED A FIXTURE. A GAP is work, not settled state.
const BASELINE = {
  'unexpected-internal-call': {
    ruling: 'D-025', status: 'RESERVED',
    why: 'allowedCallGraphHash is RESERVED in v1 and read by nothing, so the class cannot be ' +
         'driven to a positive case. Ratified, and the ablation says so where the table is.',
  },
  'reentrancy-attempt': {
    ruling: 'A-036', status: 'DELEGATED',
    why: 'F056 is decided by the exact-target rule; its target has empty bytecode and cannot ' +
         're-enter. Delegated to the vault Foundry suite, which does test reentrancy. ' +
         'Deferred with D-035 because repairing the fixture changes the labelled view.',
  },
  'invalid-or-rotated-signer': {
    ruling: 'D-010', status: 'DELEGATED',
    why: 'Receipt authentication belongs to the isolated signer and the evaluator has no code ' +
         'for it, so no corpus fixture can exercise it. F035 is ALLOW with nothing failing. ' +
         'The signer has its own 42 tamper cases and the independent Python verifier.',
  },
  'malicious-retrieved-instructions': {
    ruling: 'A-028 F-5', status: 'DELEGATED',
    why: 'The class subject is containment, measured by the corpus leak guard rather than by a ' +
         'check. The ablation states these verdicts must not be read as detections.',
  },
  'owner-override-and-block-behaviour': {
    ruling: 'D-039', status: 'DELEGATED',
    why: 'Found by this guard. F054/F055 fail on code identity and wrong resource, neither ' +
         'about the override path — but they declare primaryEnforcement vault-foundry-invariants ' +
         'and the vault suite does test the override path. Ruled an accepted delegation: the ' +
         'declaration is accurate, the corpus layer is simply not where it is proved.',
  },
  'conflicting-block-state': {
    ruling: 'D-039', status: 'GAP',
    why: 'Found by this guard, and RULED A GENUINE UNCOVERED CLASS. F048 declares ' +
         'primaryEnforcement conformance-engine — it claims to be proved HERE — then fails on ' +
         'EVAL_SIMULATION_UNAVAILABLE and EVAL_TARGET_CODE_IDENTITY and REVIEWs, which is an ' +
         'outage shape, not the failed-rule-that-blocks shape D-030 describes. Nothing else ' +
         'covers it. OWES A FIXTURE at v1.1, riding with the re-label per A-036.',
  },
};

let fail = 0;
const problems = [];

// --- Vacuity guard on the guard itself --------------------------------------
// Every code in the map must exist in the engine. A renamed code would otherwise make its class
// silently unmatchable, and the guard would report a corpus defect that is really guard rot.
const unknown = [];
for (const [cls, codes] of Object.entries(ABOUT)) {
  if (codes === CONFORMING) continue;
  for (const c of codes) if (!engineCodes.has(c)) unknown.push(`${cls} -> ${c}`);
}
if (unknown.length) {
  console.log('  FAIL  the class map names checks the engine does not declare:');
  for (const u of unknown) console.log(`          ${u}`);
  console.log('        Fix the MAP to the engine\'s current names. Do not delete the class.');
  fail = 1;
}

// --- Load the corpus --------------------------------------------------------
const fixtureIds = fs.readdirSync(fixturesDir)
  .filter(f => f.endsWith('.json') && !f.startsWith('_'))
  .map(f => JSON.parse(fs.readFileSync(`${fixturesDir}/${f}`, 'utf8')));

const results = new Map();
for (const f of fs.readdirSync(resultsDir)) {
  if (!f.endsWith('.json') || f.startsWith('_')) continue;
  const j = JSON.parse(fs.readFileSync(`${resultsDir}/${f}`, 'utf8'));
  results.set(j.fixtureId, j);
}

// A result set missing fixtures would let this guard pass by simply not looking at them.
const missing = fixtureIds.filter(f => !results.has(f.fixtureId)).map(f => f.fixtureId);
if (missing.length) {
  console.log(`  FAIL  ${missing.length} fixture(s) have no result file: ${missing.join(', ')}`);
  console.log('        Run the corpus before this guard; a partial result set proves nothing.');
  fail = 1;
}

// Every class the corpus uses must be in the map, and every mapped class must be in the corpus.
// Either direction drifting is how a class quietly stops being checked.
const corpusClasses = new Set(fixtureIds.map(f => f.scenarioClass));
for (const c of corpusClasses) {
  if (!(c in ABOUT)) {
    console.log(`  FAIL  corpus class '${c}' is not in the map — add it, with the checks it is about`);
    fail = 1;
  }
}
for (const c of Object.keys(ABOUT)) {
  if (!corpusClasses.has(c)) {
    console.log(`  FAIL  mapped class '${c}' has no fixtures — the map describes a corpus that is not here`);
    fail = 1;
  }
}

// --- The assertion ----------------------------------------------------------
const exercised = [];
const unexercised = [];

for (const cls of [...corpusClasses].sort()) {
  const about = ABOUT[cls];
  if (about === undefined) continue;
  const mine = fixtureIds.filter(f => f.scenarioClass === cls).map(f => results.get(f.fixtureId)).filter(Boolean);

  if (about === CONFORMING) {
    const ok = mine.some(r => {
      const L3 = (r.layers || []).find(l => l.layer === 'L3_full_conformance');
      return L3 && L3.verdict === 'ALLOW' && (L3.failing || []).length === 0;
    });
    (ok ? exercised : unexercised).push({ cls, how: 'a conforming action is ALLOWed with nothing failing' });
    continue;
  }

  const hits = [];
  for (const r of mine) {
    const L3 = (r.layers || []).find(l => l.layer === 'L3_full_conformance');
    for (const code of (L3 && L3.failing) || []) {
      if (about.includes(code)) hits.push(`${r.fixtureId}:${code}`);
    }
  }
  (hits.length ? exercised : unexercised).push({ cls, how: hits.join(' ') });
}

for (const e of exercised) {
  if (BASELINE[e.cls]) {
    console.log(`  FAIL  '${e.cls}' is baselined as unexercised but now IS exercised (${e.how})`);
    console.log('        Remove it from BASELINE. A stale ratchet is a claim that has stopped being true.');
    fail = 1;
  }
}

for (const u of unexercised) {
  if (!BASELINE[u.cls]) {
    console.log(`  FAIL  '${u.cls}' has no fixture producing a failing check the class is about`);
    console.log(`        Expected one of: ${(ABOUT[u.cls] || []).join(', ') || '(none mapped)'}`);
    problems.push(u.cls);
    fail = 1;
  }
}

console.log(`  ok    ${exercised.length} of ${corpusClasses.size} classes exercise the class they name`);

console.log('');
console.log('corpus class coverage — CARRIED, never counted as covered');
for (const [cls, b] of Object.entries(BASELINE)) {
  console.log(`  ${(b.status || 'UNRULED').padEnd(9)} ${cls}   [${b.ruling}]`);
  for (const line of b.why.match(/.{1,72}(\s|$)/g) || []) console.log(`            ${line.trim()}`);
}
const gaps = Object.entries(BASELINE).filter(([, b]) => b.status === 'GAP').map(([c]) => c);
const unruled = Object.entries(BASELINE).filter(([, b]) => !b.status || b.ruling === 'UNRULED').map(([c]) => c);
console.log('');
if (gaps.length) {
  console.log(`  ${gaps.length} GAP: ${gaps.join(', ')}`);
  console.log('  A GAP claims to be proved at this layer and is not. It OWES A FIXTURE — carried');
  console.log('  so the ratchet can arm, not because the class is covered.');
}
if (unruled.length) {
  console.log(`  ${unruled.length} class(es) are UNRULED — found by this guard and not yet decided by John.`);
}
if (!gaps.length && !unruled.length) {
  console.log('  All carried classes are DELEGATED or RESERVED with a ruling. None owes a fixture.');
}

process.exit(fail);
NODE
rc=$?
rm -f "/tmp/.sentinel-eval-codes.$$"

echo
if [ "$rc" -ne 0 ]; then
    echo "corpus class coverage: FAILED"
    exit 1
fi
echo "corpus class coverage: pass on the ratchet; carried classes listed above"
