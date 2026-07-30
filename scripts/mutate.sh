#!/usr/bin/env bash
# Non-vacuity check for the Sentinel TypeScript suite: apply a deliberate defect, confirm
# the suite goes red, restore. A suite that cannot fail is not evidence.
#
# TWO PAST BUGS IN THIS SCRIPT, KEPT ON THE RECORD BECAUSE BOTH WERE INSTRUCTIVE.
#
# v1 measured results by grepping the node:test reporter for a "fail N" line, and reported
# all 14 mutations as surviving. The parse was broken, not the suite. An instrument that
# reports "everything passed" when it is itself broken is the worst possible failure mode
# for this check, so results now come from the runner's exit status alone.
#
# v2 backed up the whole source tree and restored it with `rm -rf src; cp -R backup src`.
# When the sweep outgrew its 10-minute budget and was killed mid-restore, that left ts/src
# EMPTY: committed files came back from git, four uncommitted ones had to be rewritten from
# scratch. The lesson is not "raise the timeout". It is that a repair tool must never have a
# window in which the thing it repairs does not exist.
#
# v3 therefore NEVER touches more than one file at a time. Each mutation backs up exactly
# the file it edits and restores exactly that file, so at every instant the tree is complete
# except for at most one modified file — recoverable with `git checkout --` or by rerunning.
#
# Usage:  ./scripts/mutate.sh [filter]      e.g. ./scripts/mutate.sh E   runs only E* mutations
#
# WHY THIS IS IN THE REPOSITORY RATHER THAN A SCRATCH FILE. The gate evidence cites mutation
# results, and an outside reviewer correctly objected that a claim resting on a script nobody
# else has cannot be independently reproduced. Either the harness ships or the numbers stop
# being evidence. It ships.
#
# Not wired into scripts/test.sh: a full sweep runs the whole suite once per mutation and
# takes roughly half an hour. It is a periodic verification tool, not a gate stage.
set -uo pipefail

TS="$(git rev-parse --show-toplevel)/ts"
FILTER="${1:-}"

# Refuse to run against a dirty tree. Results are meaningless if a mutation cannot be
# distinguished from work in progress, and a clean tree is what makes `git checkout --` a
# reliable fallback if this script is killed at the worst possible moment.
if [ -n "$(cd "$TS" && git status --porcelain -- src)" ]; then
    echo "REFUSING: ts/src has uncommitted changes. Commit or stash first."
    exit 1
fi

CURRENT_FILE=""
CURRENT_BACKUP=""

restore_current() {
    if [ -n "$CURRENT_FILE" ] && [ -f "$CURRENT_BACKUP" ]; then
        cp "$CURRENT_BACKUP" "$TS/$CURRENT_FILE"
        rm -f "$CURRENT_BACKUP"
    fi
    CURRENT_FILE=""
    CURRENT_BACKUP=""
}

# EXIT alone is not enough: a timeout kill arrives as TERM, and the v2 incident happened
# during exactly that.
trap restore_current EXIT INT TERM

caught=0
survived=0
errored=0
skipped=0

apply_mutation() {
    MUT_FILE="$1" MUT_FROM="$2" MUT_TO="$3" python3 -c '
import os, sys
path = os.environ["MUT_FILE"]
old, new = os.environ["MUT_FROM"], os.environ["MUT_TO"]
text = open(path).read()
n = text.count(old)
if n != 1:
    sys.stderr.write("anchor appears %d times, expected exactly 1\n" % n)
    sys.exit(1)
open(path, "w").write(text.replace(old, new, 1))
'
}

run_mutation() {
    local name="$1" file="$2" from="$3" to="$4"

    if [ -n "$FILTER" ] && [[ "$name" != $FILTER* ]]; then
        skipped=$((skipped + 1))
        return
    fi

    restore_current
    CURRENT_FILE="$file"
    CURRENT_BACKUP="$(mktemp)"
    cp "$TS/$file" "$CURRENT_BACKUP"

    # A mutation that silently fails to apply is indistinguishable, in the results, from one
    # the suite failed to catch — so applying it is verified, not assumed.
    if ! apply_mutation "$TS/$file" "$from" "$to" 2>/dev/null; then
        printf '  %-58s ERROR (anchor not unique)\n' "$name"
        errored=$((errored + 1))
        restore_current
        return
    fi

    if (cd "$TS" && npm test >/dev/null 2>&1); then
        printf '  %-58s *** SURVIVED ***\n' "$name"
        survived=$((survived + 1))
    else
        printf '  %-58s caught\n' "$name"
        caught=$((caught + 1))
    fi
    restore_current
}

echo "=== Sentinel mutation testing${FILTER:+ (filter: $FILTER*)} ==="

# The baseline must be green, or every "caught" below is meaningless.
if (cd "$TS" && npm test >/dev/null 2>&1); then
    echo "  baseline (no mutation): green"
else
    echo "  baseline (no mutation): RED — aborting, results would be meaningless"
    exit 1
fi

run_mutation "M1  hashAction: swap chainId/vault field order" \
    "src/signer/eip712.ts" \
    "        word.uint(a.chainId),
        word.address(a.vault)," \
    "        word.address(a.vault),
        word.uint(a.chainId),"

run_mutation "M2  bytes4 left-padded instead of left-aligned" \
    "src/signer/eip712.ts" \
    "        return rightPad(d);" \
    "        return leftPad(d);"

run_mutation "M3  attest: drop the dataHash/calldata check" \
    "src/signer/attest.ts" \
    'if (hashCallData(callData) !== action.dataHash) findings.push("SIGNER_DATAHASH_MISMATCH");' \
    'if (false) findings.push("SIGNER_DATAHASH_MISMATCH");'

run_mutation "M4  protocol: CONFORMANCE no longer blocks ALLOW" \
    "src/signer/protocol.ts" \
    '            case "CONFORMANCE":
                return verdict === "ALLOW";' \
    '            case "CONFORMANCE":
                return false;'

run_mutation "M5  attest: drop the per-nonce attestation guard" \
    "src/signer/attest.ts" \
    'if (guard.conflicts(chainId, vault, action.actionNonce, actionHash, at, basis)) {' \
    'if (false && guard.conflicts(chainId, vault, action.actionNonce, actionHash, at, basis)) {'

run_mutation "M6  server: add a generic sign method" \
    "src/signer/server.ts" \
    'const METHODS = ["status", "evaluateAndSign"] as const;' \
    'const METHODS = ["status", "evaluateAndSign", "sign"] as const;'

run_mutation "M7  keystore: sign under the wrong chain domain" \
    "src/signer/keystore.ts" \
    "const domainSep = domainSeparator(config.chainId, config.vault);" \
    "const domainSep = domainSeparator(config.chainId + 1n, config.vault);"

run_mutation "M8  attest: skip the simulation-block check" \
    "src/signer/attest.ts" \
    "if (simHash === null || simHash !== evaluation.simulationBlockHash) {" \
    "if (false) {"

run_mutation "M9  attest: ignore the vault's active-signer identity" \
    "src/signer/attest.ts" \
    'if (state.signer !== keystore.address) findings.push("SIGNER_NOT_ACTIVE_SIGNER");' \
    'if (false) findings.push("SIGNER_NOT_ACTIVE_SIGNER");'

run_mutation "M10 attest: trust the mandate without checking it is active" \
    "src/signer/attest.ts" \
    "const mandateActive = hashMandate(mandate) === state.activeMandateHash;" \
    "const mandateActive = true;"

run_mutation "M11 attest: stop checking the mandate value ceiling" \
    "src/signer/attest.ts" \
    "if (action.valueWei > mandate.maxNativeValueWei) {" \
    "if (false) {"

run_mutation "M12 attest: stop checking the pinned target code hash" \
    "src/signer/attest.ts" \
    "if (mandate.targetCodeHash !== state.targetCodeHash) {" \
    "if (false) {"

run_mutation "M13 protocol: silently ignore unknown request fields" \
    "src/signer/protocol.ts" \
    'if (!allowed.includes(k)) throw new ProtocolError' \
    'if (false) throw new ProtocolError'

run_mutation "M14 attest: let a BLOCK receipt hold the nonce" \
    "src/signer/attest.ts" \
    'const reserved = evaluation.verdict !== "BLOCK";' \
    'const reserved = true;'

run_mutation "M17 attest: reserve the nonce AFTER signing (reopens the race)" \
    "src/signer/attest.ts" \
    '            if (reserved) {
                guard.record(chainId, vault, action.actionNonce, actionHash, expiresAt, basis);
            }

            let signature: Hex;
            try {
                signature = await keystore.signReceipt(receipt);
            } catch (err) {' \
    '            let signature: Hex;
            try {
                signature = await keystore.signReceipt(receipt);
                if (reserved) {
                    guard.record(chainId, vault, action.actionNonce, actionHash, expiresAt, basis);
                }
            } catch (err) {'

run_mutation "M18 keystore: allow signing a receipt naming another signer" \
    "src/signer/keystore.ts" \
    "if (receipt.signer.toLowerCase() !== address) {" \
    "if (false) {"

run_mutation "M15 attest: stop checking vault pause state" \
    "src/signer/attest.ts" \
    'if (state.paused) findings.push("SIGNER_VAULT_PAUSED");' \
    'if (false) findings.push("SIGNER_VAULT_PAUSED");'

run_mutation "M16 attest: stop checking the action nonce" \
    "src/signer/attest.ts" \
    'if (action.actionNonce !== state.actionNonce) findings.push("SIGNER_NONCE_MISMATCH");' \
    'if (false) findings.push("SIGNER_NONCE_MISMATCH");'

run_mutation "M19 attest: delete the mandate validity-window check" \
    "src/signer/attest.ts" \
    'if (at < mandate.validAfter || at > mandate.validUntil) {' \
    'if (false) {'

run_mutation "M20 attest: delete the mandate principal/owner check" \
    "src/signer/attest.ts" \
    'if (mandate.principal !== state.owner) {' \
    'if (false) {'

run_mutation "M21 attest: delete the policy window check" \
    "src/signer/attest.ts" \
    'if (at < policy.validAfter || at > policy.validUntil) {' \
    'if (false) {'

run_mutation "M22 attest: drop the vault target allowlist check" \
    "src/signer/attest.ts" \
    'if (!state.targetAllowed) findings.push("SIGNER_VAULT_TARGET_NOT_ALLOWED");' \
    'if (false) findings.push("SIGNER_VAULT_TARGET_NOT_ALLOWED");'

run_mutation "M23 protocol: SIMULATION_BLOCK back to EXECUTABILITY (breaks Case 4)" \
    "src/signer/protocol.ts" \
    'SIGNER_SIMULATION_BLOCK_MISMATCH: "CONFORMANCE",' \
    'SIGNER_SIMULATION_BLOCK_MISMATCH: "EXECUTABILITY",'

run_mutation "M24 attest: reservation ignores the mandate/policy basis" \
    "src/signer/attest.ts" \
    'if (held.mandateHash !== basis.mandateHash || held.policyHash !== basis.policyHash) {' \
    'if (false) {'

run_mutation "M25 protocol: allow newline inside a reason code" \
    "src/signer/protocol.ts" \
    'export const REASON_CODE_PATTERN = /^[A-Za-z0-9_.:-]{1,64}$/;' \
    'export const REASON_CODE_PATTERN = /^[\\s\\S]{0,64}$/;'

run_mutation "D1 decode: accept trailing bytes (chain-lenient drift)" \
    "src/decode/abi.ts" \
    "if (body.length !== expectedWords * WORD_HEX) {" \
    "if (body.length < expectedWords * WORD_HEX) {"

run_mutation "D2 decode: stop checking dirty address high bits" \
    "src/decode/abi.ts" \
    "if (!/^0+$/.test(high)) {" \
    "if (false) {"

run_mutation "D3 decode: treat any non-zero word as bool true" \
    "src/decode/abi.ts" \
    "if (/^0*1$/.test(w)) return true;" \
    "return true;"

run_mutation "D4 decode: stop checking uintN width" \
    "src/decode/abi.ts" \
    "if (!/^0+$/.test(w.slice(0, highNibbles))) {" \
    "if (false) {"

run_mutation "D5 decode: ignore selector/target mismatch" \
    "src/decode/index.ts" \
    "if (schema.contract !== contract) {" \
    "if (false) {"

run_mutation "D6 decode: swap beneficiary and resourceId positions" \
    "src/decode/index.ts" \
    "                      resourceId: reader.bytes32(0),
                      beneficiary: reader.address(1)," \
    "                      resourceId: reader.bytes32(1),
                      beneficiary: reader.address(0),"

run_mutation "D7 decode: wrong pinned selector for purchase" \
    "src/decode/index.ts" \
    'selector: "0xc188528b",' \
    'selector: "0xc188528c",'

run_mutation "D8 decode: allow unregistered targets" \
    "src/decode/index.ts" \
    "if (contract === undefined) {" \
    "if (false) {"

run_mutation "S1 simulate: swallow a failed revert instead of escalating" \
    "src/simulate/index.ts" \
    "if (!reverted) {" \
    "if (false) {"

run_mutation "S2 simulate: execute as the caller, not as the vault" \
    "src/simulate/index.ts" \
    "await control.impersonate(vault);" \
    "await control.impersonate(target);"

run_mutation "S3 simulate: treat a missing trace as 'no internal calls'" \
    "src/simulate/index.ts" \
    'unresolvedChecks.push("SIM_CALL_TRACE_UNAVAILABLE");
            }
        } else {' \
    '/* swallowed */;
            }
        } else {'

run_mutation "S4 simulate: read the allowance of the wrong owner" \
    "src/simulate/index.ts" \
    "args: [vault, decoded.spender]," \
    "args: [decoded.spender, vault],"

run_mutation "S6 simulate: charge the vault for gas (non-zero base fee)" \
    "src/simulate/index.ts" \
    "await control.setNextBlockBaseFee(0n);" \
    "await control.setNextBlockBaseFee(1000000000n);"

run_mutation "S5 simulate: record the anchor AFTER the snapshot is taken" \
    "src/simulate/index.ts" \
    "expiryBefore: before.entitlement.expiry," \
    "expiryBefore: after.entitlement.expiry,"

run_mutation "E1 evaluate: drop the Case 3 resource check" \
    "src/evaluate/checks.ts" \
    "decoded.resourceId.toLowerCase() === mandate.resourceId.toLowerCase()," \
    "true,"

run_mutation "E2 evaluate: drop the recurrence check" \
    "src/evaluate/checks.ts" \
    "!decoded.recurring || mandate.recurringAllowed," \
    "true,"

run_mutation "E3 evaluate: UNRESOLVED no longer affects the verdict" \
    "src/evaluate/checks.ts" \
    'if (results.some((r) => r.outcome === "UNRESOLVED")) {' \
    "if (false) {"

run_mutation "E4 evaluate: VIOLATION no longer blocks" \
    "src/evaluate/checks.ts" \
    'if (results.some((r) => r.outcome === "VIOLATION")) return "BLOCK";' \
    'if (false) return "BLOCK";'

run_mutation "E5 evaluate: code identity becomes a VIOLATION (breaks Case 4)" \
    "src/evaluate/checks.ts" \
    '            : unresolved(
                  "EVAL_TARGET_CODE_IDENTITY",' \
    '            : violation(
                  "EVAL_TARGET_CODE_IDENTITY",'

run_mutation "E6 evaluate: ignore the approval ceiling" \
    "src/evaluate/checks.ts" \
    "decoded.amount <= policy.maxAllowanceIncreaseBaseUnits," \
    "true,"

run_mutation "E7 evaluate: drop the beneficiary check" \
    "src/evaluate/checks.ts" \
    "decoded.beneficiary.toLowerCase() === mandate.beneficiary.toLowerCase()," \
    "true,"

run_mutation "E8 evaluate: failureMode ignored, always review" \
    "src/evaluate/checks.ts" \
    'return policy.failureMode === FAILURE_MODE_REVIEW ? "REVIEW" : "BLOCK";' \
    'return "REVIEW";'

run_mutation "E9 jcs: stop sorting object keys" \
    "src/evaluate/jcs.ts" \
    "const sorted = [...keys].sort();" \
    "const sorted = [...keys];"

run_mutation "E10 jcs: silently serialise numbers" \
    "src/evaluate/jcs.ts" \
    'if (typeof value === "number" || typeof value === "bigint") {' \
    "if (false) {"

run_mutation "E11 evaluate: bundle omits passing checks" \
    "src/evaluate/index.ts" \
    "policyChecks: checks.map((c) => ({" \
    'policyChecks: checks.filter((c) => c.outcome !== "PASS").map((c) => ({'

run_mutation "R1 D-012: refusal produces no recorded artifact" \
    "src/signer/attest.ts" \
    "                if (attributable) {" \
    "                if (false) {"

run_mutation "R2 D-012: refusal digest ignores which action was refused" \
    "src/signer/eip712.ts" \
    "        r.actionHash," \
    "        \"\"," \

run_mutation "R3 D-014: skip the evidence-decoding bind entirely" \
    "src/signer/attest.ts" \
    "findings.push(...checkEvidenceDecoding(callData, evaluation.evidenceCanonical));" \
    "findings.push();"

run_mutation "R4 D-014: accept a bundle with no decoding claim" \
    "src/signer/attest.ts" \
    'if (typeof claim !== "object" || claim === null) return ["SIGNER_EVIDENCE_DECODING_ABSENT"];' \
    'if (typeof claim !== "object" || claim === null) return [];'

run_mutation "R5 D-014: ignore mismatched parameter values" \
    "src/signer/attest.ts" \
    "        if (!match) return [\"SIGNER_EVIDENCE_DECODING_MISMATCH\"];" \
    "        if (false) return [\"SIGNER_EVIDENCE_DECODING_MISMATCH\"];"

run_mutation "R6 D-014: signer starts checking resource against the mandate (rejected branch)" \
    "src/signer/attest.ts" \
    "                if (mandate.targetCodeHash !== state.targetCodeHash) {" \
    "                const mine = decodeBySelector(callData);
                if (mine.ok && mine.decoded.schema === \"DemoPay.purchase\" &&
                    mine.decoded.resourceId !== mandate.resourceId) {
                    findings.push(\"SIGNER_MANDATE_SELECTOR_MISMATCH\");
                }
                if (mandate.targetCodeHash !== state.targetCodeHash) {"

echo "=== ${caught} caught, ${survived} survived, ${errored} did not apply, ${skipped} skipped ==="
