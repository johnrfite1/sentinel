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

ROOT="$(git rev-parse --show-toplevel)"
TS="$ROOT/ts"
FILTER="${1:-}"
export PATH="$HOME/.foundry/bin:$PATH"

# Refuse to run against a dirty tree. Results are meaningless if a mutation cannot be
# distinguished from work in progress, and a clean tree is what makes `git checkout --` a
# reliable fallback if this script is killed at the worst possible moment.
if [ -n "$(cd "$ROOT" && git status --porcelain -- ts/src contracts/src)" ]; then
    echo "REFUSING: ts/src or contracts/src has uncommitted changes. Commit or stash first."
    exit 1
fi

CURRENT_FILE=""
CURRENT_BACKUP=""

# CURRENT_FILE holds an ABSOLUTE path. It used to be relative to ts/, which quietly made
# the harness TypeScript-only: restoring a Solidity file would have written it under ts/.
restore_current() {
    if [ -n "$CURRENT_FILE" ] && [ -f "$CURRENT_BACKUP" ]; then
        cp "$CURRENT_BACKUP" "$CURRENT_FILE"
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

_mutate() {
    local name="$1" path="$2" from="$3" to="$4" kind="$5"

    if [ -n "$FILTER" ] && [[ "$name" != $FILTER* ]]; then
        skipped=$((skipped + 1))
        return
    fi

    restore_current
    # BACK UP FIRST, ARM THE TRAP SECOND, and the order is the whole point.
    #
    # The previous version set CURRENT_FILE, then created an EMPTY file with mktemp, then
    # copied into it. A TERM in that window left the trap armed with a zero-byte backup and
    # `[ -f ]` true, so restore wrote zero bytes over the source. An independent review
    # reproduced it deterministically: 43 bytes to 0. The absolute-path change made it worse
    # rather than introducing it — the old relative form produced a bogus path and failed
    # harmlessly, while the new one lands on the real contract.
    #
    # This is the v2 lesson stated in the header, in a smaller window: a repair tool must
    # never have an instant in which the thing it repairs does not exist.
    local backup
    backup="$(mktemp)"
    cp "$path" "$backup.tmp" && mv "$backup.tmp" "$backup" || {
        printf '  %-58s ERROR (could not back up)\n' "$name"
        errored=$((errored + 1))
        rm -f "$backup" "$backup.tmp"
        return
    }
    CURRENT_BACKUP="$backup"
    CURRENT_FILE="$path"

    # A mutation that silently fails to apply is indistinguishable, in the results, from one
    # the suite failed to catch — so applying it is verified, not assumed.
    if ! apply_mutation "$path" "$from" "$to" 2>/dev/null; then
        printf '  %-58s ERROR (anchor not unique)\n' "$name"
        errored=$((errored + 1))
        restore_current
        return
    fi

    local green=1
    if [ "$kind" = "sol" ]; then
        # BUILD FIRST, AND REPORT A BUILD FAILURE AS AN ERROR RATHER THAN A CATCH.
        #
        # `deny = "warnings"` means a mutation that leaves an unused variable does not
        # compile, and `forge test` then exits non-zero — which this script would otherwise
        # record as "caught". That would credit the test suite for work the compiler did,
        # and inflate exactly the number the gate evidence cites. A mutant that does not
        # build is not a measurement.
        # Compilation and linting are reported SEPARATELY, because they mean different
        # things. A mutant that does not compile is not a measurement. A mutant that
        # compiles and fails forge-lint IS a measurement the harness cannot take — and
        # an independent review found a real one: replacing `(bool ok, …)` with `(, …)`
        # to drop the CallFailed check trips the unchecked-call lint, so a
        # security-relevant mutation class was being bucketed as "does not compile" and
        # written off as a defective mutant rather than as an unmeasurable one.
        local build_out
        build_out="$(cd "$ROOT/contracts" && forge build 2>&1)"
        if [ $? -ne 0 ]; then
            if printf '%s' "$build_out" | grep -q "Lint failed"; then
                printf '  %-58s ERROR (compiles; forge-lint refuses it — UNMEASURED)\n' "$name"
            else
                printf '  %-58s ERROR (mutant does not compile)\n' "$name"
            fi
            errored=$((errored + 1))
            restore_current
            return
        fi
        (cd "$ROOT/contracts" && forge test >/dev/null 2>&1) || green=0
    else
        (cd "$TS" && npm test >/dev/null 2>&1) || green=0
    fi

    if [ "$green" -eq 1 ]; then
        printf '  %-58s *** SURVIVED ***\n' "$name"
        survived=$((survived + 1))
    else
        printf '  %-58s caught\n' "$name"
        caught=$((caught + 1))
    fi
    restore_current
}

# TypeScript mutation. `file` is relative to ts/.
run_mutation() {
    _mutate "$1" "$TS/$2" "$3" "$4" ts
}

# Solidity mutation. `file` is relative to the repository root, and the runner is `forge
# test` rather than `npm test` — which is the entire reason this harness reported nothing
# about the vault until now (A-028: "scripts/mutate.sh is TypeScript-only, and that gap is
# where most of this class lives").
run_sol_mutation() {
    _mutate "$1" "$ROOT/$2" "$3" "$4" sol
}

echo "=== Sentinel mutation testing${FILTER:+ (filter: $FILTER*)} ==="

# The baseline must be green, or every "caught" below is meaningless.
#
# BOTH baselines are checked, and both are checked even when a filter selects only one
# language. A green TypeScript run says nothing about whether `forge test` compiles, and a
# Solidity batch measured against a suite that does not build would report every mutation
# "caught" — the instrument reading as maximally effective at the exact moment it is broken,
# which is the failure mode v1 of this script had.
if (cd "$TS" && npm test >/dev/null 2>&1); then
    echo "  baseline typescript: green"
else
    echo "  baseline typescript: RED — aborting, results would be meaningless"
    exit 1
fi

if (cd "$ROOT/contracts" && forge test >/dev/null 2>&1); then
    echo "  baseline solidity:   green"
else
    echo "  baseline solidity:   RED — aborting, results would be meaningless"
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

run_mutation "V1 D-017 fix: restore the two-predicate comparison" \
    "src/signer/attest.ts" \
    "    if (claimed.decoded === \"false\") {" \
    "    if (claimed.decoded !== (mine.ok ? \"true\" : \"false\")) return [\"SIGNER_EVIDENCE_DECODING_MISMATCH\"];
    if (claimed.decoded === \"false\") {"

# V2 was NAMED for the target-binding escape hatch and mutated a different branch — the
# non-target one — so it reported "caught" throughout while the hatch it is named for sat
# open (A-028 F1). Renamed to what it actually tests, and V2b added for the real hole.
run_mutation "V2 D-017 fix: non-target decline stops being adjudicated" \
    "src/signer/attest.ts" \
    "        return mine.ok ? [\"SIGNER_EVIDENCE_DECODING_MISMATCH\"] : [];" \
    "        return [];"

run_mutation "V2b A-028 F1: restore the unconditional target-binding escape hatch" \
    "src/signer/attest.ts" \
    "            return requestedVerdict === \"ALLOW\" ? [\"SIGNER_EVIDENCE_DECODING_MISMATCH\"] : [];" \
    "            return [];"

run_mutation "V2c A-028 F1: refuse truthful target-mismatch bundles again (re-break D-017)" \
    "src/signer/attest.ts" \
    "            return requestedVerdict === \"ALLOW\" ? [\"SIGNER_EVIDENCE_DECODING_MISMATCH\"] : [];" \
    "            return [\"SIGNER_EVIDENCE_DECODING_MISMATCH\"];"

run_mutation "V3 D-017 fix: drop simulation serialisation" \
    "src/simulate/index.ts" \
    "    return serialise(() => runSimulation(args));" \
    "    return runSimulation(args);"

run_mutation "V4 D-017 fix: un-normalise decoded addresses" \
    "src/decode/abi.ts" \
    "        return \`0x\${w.slice(24).toLowerCase()}\` as Hex;" \
    "        return \`0x\${w.slice(24)}\` as Hex;"

run_mutation "V5 D-017 fix: emit unpaired surrogates verbatim again" \
    "src/evaluate/jcs.ts" \
    "                } else if (code >= 0xd800 && code <= 0xdfff) {" \
    "                } else if (false) {"

run_mutation "V6 D-017 fix: silence an unobserved allowance effect" \
    "src/evaluate/checks.ts" \
    "            allowance === undefined &&" \
    "            false &&"

# --- P: the agent-proposal transcriber (§9 step 7, D-019) -------------------
#
# The transcriber is TRUSTED under D-019 (§3.1 "canonical schema encoders"), which raises
# the stakes on this batch: there is no second encoding to disagree with it, so a defect
# here silently changes what Sentinel evaluates relative to what the agent proposed.

run_mutation "P1 encode: bytesN right-aligned instead of left-aligned" \
    "src/propose/encode.ts" \
    '    return text.slice(2).toLowerCase().padEnd(WORD_HEX, "0");' \
    '    return text.slice(2).toLowerCase().padStart(WORD_HEX, "0");'

run_mutation "P2 encode: trim whitespace in a signature instead of refusing" \
    "src/propose/encode.ts" \
    '    if (/\s/.test(signature)) {
        throw new ProposalError("PROPOSAL_MALFORMED_SIGNATURE", "contains whitespace");
    }' \
    '    signature = signature.replace(/\s/g, "");'

run_mutation "P3 encode: accept non-canonical decimals (leading zeros)" \
    "src/propose/encode.ts" \
    'const DECIMAL_RE = /^(0|[1-9][0-9]*)$/;' \
    'const DECIMAL_RE = /^[0-9]+$/;'

run_mutation "P4 encode: drop the uint width check" \
    "src/propose/encode.ts" \
    '    if (value > (bits === 256 ? MAX_UINT256 : (1n << BigInt(bits)) - 1n)) {' \
    '    if (false) {'

run_mutation "P5 encode: any non-false spelling becomes true" \
    "src/propose/encode.ts" \
    '        if (text === "true") return "1".padStart(WORD_HEX, "0");' \
    '        if (text !== "false") return "1".padStart(WORD_HEX, "0");'

run_mutation "P6 encode: address word keeps its source spelling" \
    "src/propose/encode.ts" \
    '        return text.slice(2).toLowerCase().padStart(WORD_HEX, "0");' \
    '        return text.slice(2).padStart(WORD_HEX, "0");'

run_mutation "P7 encode: skip the arity check" \
    "src/propose/encode.ts" \
    '    if (args.length !== types.length) {' \
    '    if (false) {'

run_mutation "P8 encode: unsupported argument types pass through" \
    "src/propose/encode.ts" \
    '    for (const type of types) assertSupportedType(type);' \
    '    for (const type of types) void type;'

run_mutation "P9 encode: selector takes 3 bytes, not 4" \
    "src/propose/encode.ts" \
    '    return keccak256(stringToBytes(signature)).slice(0, 10) as Hex;' \
    '    return keccak256(stringToBytes(signature)).slice(0, 8) as Hex;'

run_mutation "P10 propose: bind a constant nonce instead of the vault's" \
    "src/propose/index.ts" \
    '        actionNonce: args.vaultState.actionNonce,' \
    '        actionNonce: 0n,'

run_mutation "P11 propose: bind the mandate the agent's action names, not the active one" \
    "src/propose/index.ts" \
    '        mandateHash: args.vaultState.activeMandateHash,' \
    '        mandateHash: args.vaultState.activePolicyHash,'

run_mutation "P12 propose: dataHash over the signature instead of the calldata" \
    "src/propose/index.ts" \
    '        dataHash: keccak256(toBytes(args.proposal.callData)),' \
    '        dataHash: keccak256(toBytes(args.proposal.signature)),'

run_mutation "P13 propose: skip target validation, pass the raw claim through" \
    "src/propose/index.ts" \
    '        const target = parseTarget(proposal.target);' \
    '        const target = proposal.target as Hex;'

run_mutation "P14 schema: coerce a non-string value_wei instead of refusing" \
    "src/propose/schema.ts" \
    '    if (typeof r.value_wei !== "string") return null;' \
    '    if (false) return null;'

run_mutation "P15 fixtures: drop malformed tool calls instead of recording them" \
    "src/propose/fixtures.ts" \
    '                out.push(readProposal(b.input));' \
    '                const parsed = readProposal(b.input); if (parsed) out.push(parsed);'

# P16-P20 target paths that LINE COVERAGE found untested after P1-P15 all passed.
# Recorded that way deliberately: 15/15 caught looked like strong evidence, and it was
# evidence only about the branches the mutation author had already thought of.

run_mutation "P16 encode: any signature shape parses" \
    "src/propose/encode.ts" \
    'const SIGNATURE_RE = /^([A-Za-z_$][A-Za-z0-9_$]*)\((.*)\)$/;' \
    'const SIGNATURE_RE = /^(.*?)\(?(.*?)\)?$/;'

run_mutation "P17 encode: accept any uint width" \
    "src/propose/encode.ts" \
    '        if (bits >= 8 && bits <= 256 && bits % 8 === 0 && String(bits) === uint[1]) return;' \
    '        return;'

run_mutation "P18 encode: accept any bytesN width" \
    "src/propose/encode.ts" \
    '        if (size >= 1 && size <= 32 && String(size) === bytes[1]) return;' \
    '        return;'

run_mutation "P19 encode: skip the bytesN argument length check" \
    "src/propose/encode.ts" \
    '    const re = new RegExp(`^0x[0-9a-fA-F]{${size * 2}}$`);' \
    '    const re = /^0x[0-9a-fA-F]*$/;'

run_mutation "P20 fixtures: fall back to any fixture when the name does not match" \
    "src/propose/fixtures.ts" \
    '    const file = exact ?? byModel;' \
    '    const file = exact ?? byModel ?? files[0];'

# --- B: the §7.2 baseline and §7.3 layer partition -------------------------
#
# These mutations matter more than their size suggests. The ablation's headline claim is a
# COMPARISON, so a defect in the weaker arm does not produce a wrong number in one cell — it
# produces a wrong story about which layer does the work.

run_mutation "B1 baseline: stop enforcing the native-value ceiling" \
    "src/ablation/baseline.ts" \
    "        action.valueWei <= config.maxNativeValueWei" \
    "        true"

run_mutation "B2 baseline: stop blocking unlimited approvals" \
    "src/ablation/baseline.ts" \
    "    if (config.blockUnlimitedApproval && decode.decoded.schema === \"DemoERC20.approve\") {" \
    "    if (false) {"

run_mutation "B3 baseline: ignore the target allowlist" \
    "src/ablation/baseline.ts" \
    "        config.allowedTargets.some((t) => t.toLowerCase() === target)" \
    "        true"

run_mutation "B4 baseline: undecodable calldata becomes a block, not an abstention" \
    "src/ablation/baseline.ts" \
    '            unresolved("BASE_CALLDATA_UNDECODABLE", `${decode.code}: the baseline cannot read this call`),' \
    '            violation("BASE_CALLDATA_UNDECODABLE", `${decode.code}: the baseline cannot read this call`),'

run_mutation "B5 baseline: an unresolved check starts blocking (verdict fold)" \
    "src/ablation/baseline.ts" \
    '    return results.some((r) => r.outcome === "VIOLATION") ? "BLOCK" : "ALLOW";' \
    '    return results.some((r) => r.outcome !== "PASS") ? "BLOCK" : "ALLOW";'

run_mutation "B6 layers: L2 keeps the wrong-resource check (partition leak)" \
    "src/ablation/layers.ts" \
    '    "EVAL_PURCHASE_RESOURCE",' \
    '    "EVAL_PURCHASE_RESOURCE_TYPO",'

# B7 originally removed the `simulation: null` guard on L1. It SURVIVED, and it was a
# defective mutation rather than a coverage gap: runBaseline reads no simulation field, so
# the change has no observable behaviour today. The guard is defence in depth for a
# post-state check added later, and its untestability is now stated in ablation.test.ts.
# Replaced with a mutation that is observable.
run_mutation "B7 layers: L1 verdict fold swapped for the engine's" \
    "src/ablation/layers.ts" \
    "        verdict = baselineVerdict(checks);" \
    "        verdict = verdictOf(checks, input.policy);"

run_mutation "B8 layers: L3 silently becomes L2" \
    "src/ablation/layers.ts" \
    "        checks = runChecks(input);
        verdict = verdictOf(checks, input.policy);
    }" \
    "        checks = runChecks(input).filter((c) => !MANDATE_CONFORMANCE_CODES.has(c.code));
        verdict = verdictOf(checks, input.policy);
    }"

# --- C: the corpus integrity guards ----------------------------------------
#
# These protect the D-011(b) split and the "no fixture carries its own answer" rule. A defect
# here does not produce a wrong number — it produces a meaningless one that reads as success,
# because the corpus is the only evidence bearing on whether the verdicts are RIGHT.

# C1 AND C3 WERE ROTTEN AND BOTH ERRORED, WHICH IS ITSELF THE FINDING.
#
# Both were written against the pre-A-028 leakage guard, which matched `"key"` inside the
# serialised text. That implementation was replaced by a recursive key walk when A-028 F-3
# showed the old one let every prefixed name through — and nobody re-ran batch C afterwards,
# so two of the five corpus mutations had been reporting "anchor not unique" ever since.
# `run_mutation` counts those separately rather than as caught, so nothing false was
# published; but a mutation that cannot apply measures exactly as much as a test that cannot
# fail, and this batch existed to catch a defect in the guard it had stopped exercising.
# Re-aimed at the current implementation, keeping each one pointed at the historical bug it
# was named for.

run_mutation "C1 leakage: match the key exactly again, so every prefixed name passes" \
    "src/corpus/leakage.ts" \
    "            if (lowered.includes(forbidden.toLowerCase())) {" \
    "            if (lowered === forbidden.toLowerCase()) {"

run_mutation "C2 leakage: empty the denylist" \
    "src/corpus/leakage.ts" \
    "export const FORBIDDEN_KEYS = [
    \"verdict\"," \
    "export const FORBIDDEN_KEYS = [
    \"__never__\","

run_mutation "C3 leakage: compare the key case-sensitively again (the first real bug)" \
    "src/corpus/leakage.ts" \
    "        const lowered = key.toLowerCase();" \
    "        const lowered = key;"

run_mutation "C3b leakage: let the allowlist exempt everything" \
    "src/corpus/leakage.ts" \
    "        if (isDeclared(key)) {" \
    "        if (true) {"

run_mutation "C4 corpus: drop the §7.1 size bound" \
    "src/corpus/fixtures.ts" \
    "    if (corpus.length < 30 || corpus.length > 50) {" \
    "    if (corpus.length < 0) {"

run_mutation "C5 corpus: stop checking class coverage" \
    "src/corpus/fixtures.ts" \
    "    const missing = FIXTURE_CLASSES.filter((c) => !covered.has(c));" \
    "    const missing: string[] = [];"

# C6-C10 cover the A-028 F-5 remediation: the injection class carries a real rationale and
# the run measures that it reached nothing. The guard is new, so the question is not whether
# it passes — it does — but whether removing it would be noticed.

run_mutation "C6 rationale: drop the floor, so an unprobeable rationale reports a pass" \
    "src/corpus/rationale.ts" \
    "    if (probes.length < MIN_BIGRAMS) throw new UnprobeableRationaleError(fixtureId, probes.length);" \
    "    if (probes.length < 0) throw new UnprobeableRationaleError(fixtureId, probes.length);"

run_mutation "C7 rationale: never actually report a leak" \
    "src/corpus/rationale.ts" \
    "        if (haystack.includes(phrase)) throw new RationaleLeakError(fixtureId, phrase);" \
    "        if (false && haystack.includes(phrase)) throw new RationaleLeakError(fixtureId, phrase);"

# RE-AIMED 2026-08-15, and the re-aim is the same lesson C1/C3 taught one commit earlier: the
# guard was rewritten (normalisation moved into a shared helper) and these two anchors would
# otherwise have started reporting "anchor not unique" for exactly the code they exist to
# protect. Re-run the batch whose target you just edited.
run_mutation "C8 rationale: stop normalising, so a punctuated leak slips past" \
    "src/corpus/rationale.ts" \
    "    return text.toLowerCase().replace(/[^a-z]+/g, \" \");" \
    "    return text.toLowerCase();"

run_mutation "C9 rationale: let evaluator field names count as narrative" \
    "src/corpus/rationale.ts" \
    "    const usable = (w: string): boolean => w.length >= 4 && !GENERIC.has(w);" \
    "    const usable = (w: string): boolean => w.length >= 4;"

run_mutation "C10 corpus: return the injection class to its vacuous state" \
    "src/corpus/fixtures.ts" \
    "        agentRationale:
            \"This authorization call grants the settlement relayer \" +" \
    "        agentRationaleRemovedByMutation:
            \"This authorization call grants the settlement relayer \" +"

# --- S: the vault (Solidity) ------------------------------------------------
#
# THIS BATCH DID NOT EXIST UNTIL 2026-08-15, AND ITS ABSENCE IS THE POINT. The vault is the
# enforcement substrate — the layer that still holds when the evaluator and the signer are
# both compromised — and it was the only layer with no non-vacuity instrument at all. When
# an outside reviewer built one, 29 of 45 mutations survived a fully green run and the
# §3.3(9) ordering property turned out to be verified by nothing.
#
# The twenty below are that reviewer's set, promoted from `docs/review-2026-08-15/artifacts/`
# into the harness that ships, for the reason stated at the top of this file: a claim resting
# on a script nobody else has cannot be independently reproduced.
#
# CONTROLS are marked. They target checks the suite has always covered, and they exist to
# validate the instrument in the other direction — a batch where everything is caught tells
# you nothing unless you know the harness can report a survivor, and a batch where everything
# survives tells you nothing unless you know it can report a catch.

run_sol_mutation "S1  vault: delete the WrongVault check" \
    "contracts/src/SentinelVault.sol" \
    '        if (action.vault != address(this)) revert WrongVault();
' \
    ''

run_sol_mutation "S2  vault: delete the CalldataTooShort check" \
    "contracts/src/SentinelVault.sol" \
    '        if (callData.length < 4) revert CalldataTooShort();
' \
    ''

run_sol_mutation "S3  vault: delete the SelectorNotAllowed backstop" \
    "contracts/src/SentinelVault.sol" \
    '        if (!allowedSelector[bytes4(callData[:4])]) revert SelectorNotAllowed();
' \
    ''

run_sol_mutation "S4  CONTROL vault: delete the TargetNotAllowed backstop" \
    "contracts/src/SentinelVault.sol" \
    '        if (!allowedTarget[action.target]) revert TargetNotAllowed();
' \
    ''

run_sol_mutation "S5  vault: delete the ReceiptBindingMismatch check" \
    "contracts/src/SentinelVault.sol" \
    '        if (receipt.mandateHash != action.mandateHash || receipt.policyHash != action.policyHash) {
            revert ReceiptBindingMismatch();
        }
' \
    ''

run_sol_mutation "S6  vault: delete the OverrideExpired check" \
    "contracts/src/SentinelVault.sol" \
    '        // forge-lint: disable-next-line(block-timestamp)
        if (block.timestamp > auth.expiresAt) revert OverrideExpired();
' \
    ''

# The one A-028 called its sharpest coverage finding: the reentrancy guard masks the
# ordering, so the two defences §3.3(9) presents as independent were tested by one test.
run_sol_mutation "S7  vault: consume the nonce AFTER the external call (breaks §3.3(9))" \
    "contracts/src/SentinelVault.sol" \
    '        bytes32 actionHash = T.hashAction(action);
        actionNonce += 1;

        emit ActionExecuted(actionHash, action.actionNonce, decisionId, viaOverride);

        (bool ok, bytes memory ret) = action.target.call{value: action.valueWei}(callData);
        if (!ok) revert CallFailed(ret);' \
    '        bytes32 actionHash = T.hashAction(action);

        emit ActionExecuted(actionHash, action.actionNonce, decisionId, viaOverride);

        (bool ok, bytes memory ret) = action.target.call{value: action.valueWei}(callData);
        actionNonce += 1;
        if (!ok) revert CallFailed(ret);'

run_sol_mutation "S8  CONTROL vault: drop nonReentrant from executeWithReceipt" \
    "contracts/src/SentinelVault.sol" \
    '        bytes calldata receiptSig
    ) external nonReentrant returns (bytes memory) {
        _checkAction(action, callData);
        _checkReceipt(action, receipt, receiptSig);' \
    '        bytes calldata receiptSig
    ) external returns (bytes memory) {
        _checkAction(action, callData);
        _checkReceipt(action, receipt, receiptSig);'

run_sol_mutation "S9  CONTROL vault: delete the named-signer half of the receipt check" \
    "contracts/src/SentinelVault.sol" \
    '        if (receipt.signer != signer) revert WrongSigner();
' \
    ''

run_sol_mutation "S10 vault: delete the constructor zero-address check" \
    "contracts/src/SentinelVault.sol" \
    '        if (_owner == address(0) || _signer == address(0)) revert ZeroAddress();
' \
    ''

run_sol_mutation "S11 vault: delete the rotateSigner zero-address check" \
    "contracts/src/SentinelVault.sol" \
    '        if (newSigner == address(0)) revert ZeroAddress();
' \
    ''

run_sol_mutation "S12 vault: delete the recover zero-address check" \
    "contracts/src/SentinelVault.sol" \
    '        if (to == address(0)) revert ZeroAddress();
' \
    ''

run_sol_mutation "S13 CONTROL vault: delete the ReceiptExpired check" \
    "contracts/src/SentinelVault.sol" \
    '        // forge-lint: disable-next-line(block-timestamp)
        if (block.timestamp > receipt.expiresAt) revert ReceiptExpired();
' \
    ''

run_sol_mutation "S14 vault: drop actionNonce from the override binding" \
    "contracts/src/SentinelVault.sol" \
    '                || auth.actionNonce != action.actionNonce
        ) revert OverrideMismatch();' \
    '        ) revert OverrideMismatch();'

run_sol_mutation "S15 vault: drop mandate/policy from the override binding" \
    "contracts/src/SentinelVault.sol" \
    '                || auth.mandateHash != action.mandateHash || auth.policyHash != action.policyHash
' \
    ''

run_sol_mutation "S16 vault: drop the zero-hash guard on activeMandateHash" \
    "contracts/src/SentinelVault.sol" \
    '        if (activeMandateHash == bytes32(0) || action.mandateHash != activeMandateHash) {' \
    '        if (action.mandateHash != activeMandateHash) {'

run_sol_mutation "S17 vault: drop the zero-hash guard on activePolicyHash" \
    "contracts/src/SentinelVault.sol" \
    '        if (activePolicyHash == bytes32(0) || action.policyHash != activePolicyHash) {' \
    '        if (action.policyHash != activePolicyHash) {'

run_sol_mutation "S18 vault: trust the supplied dataHash instead of recomputing it" \
    "contracts/src/SentinelVault.sol" \
    '        if (keccak256(callData) != action.dataHash) revert CalldataMismatch();
' \
    ''

run_sol_mutation "S19 CONTROL vault: drop the ValueOverCap backstop" \
    "contracts/src/SentinelVault.sol" \
    '        if (action.valueWei > maxNativeValueWei) revert ValueOverCap();
' \
    ''

run_sol_mutation "S20 vault: delete the ActionExpired deadline check" \
    "contracts/src/SentinelVault.sol" \
    '        // forge-lint: disable-next-line(block-timestamp)
        if (block.timestamp > action.deadline) revert ActionExpired();
' \
    ''

# S21-S25 come from an independent adversarial review of the twenty above (2026-08-15).
# All five SURVIVED the 60-test suite the original twenty were all caught by, and the
# reviewer's diagnosis is the useful part: every one of the first twenty targets a check
# inside `_checkAction`, `_checkReceipt`, or the override binding. None targeted
# `_consumeAndCall`'s failure handling, the reentrancy guard on the OVERRIDE path, or any
# emitted event. A mutation set inherits the blind spots of whoever enumerated it, which is
# the same lesson recorded for the TypeScript batches — and this time the set was inherited
# from a reviewer rather than the implementer, and STILL had a shape to it.

run_sol_mutation "S21 vault: drop nonReentrant from executeWithOverride" \
    "contracts/src/SentinelVault.sol" \
    '        bytes calldata ownerSig
    ) external nonReentrant returns (bytes memory) {' \
    '        bytes calldata ownerSig
    ) external returns (bytes memory) {'

# The anchor spans both lines on purpose. Dropping only the comparison leaves `receiptHash`
# unused, which `deny = "warnings"` turns into a build failure — so the first version of this
# mutation reported ERROR and measured nothing. A mutation must be a change the compiler
# accepts, or it is a statement about the compiler.
run_sol_mutation "S22 vault: drop the review-receipt term from the override binding" \
    "contracts/src/SentinelVault.sol" \
    '        bytes32 receiptHash = _checkReceipt(action, receipt, receiptSig);' \
    '        _checkReceipt(action, receipt, receiptSig);
        bytes32 receiptHash = auth.reviewReceiptHash;'

run_sol_mutation "S23 vault: report a failed external call as success" \
    "contracts/src/SentinelVault.sol" \
    '        if (!ok) revert CallFailed(ret);
        return ret;' \
    '        ok;
        return ret;'

run_sol_mutation "S24 vault: log the post-increment nonce in ActionExecuted" \
    "contracts/src/SentinelVault.sol" \
    '        emit ActionExecuted(actionHash, action.actionNonce, decisionId, viaOverride);' \
    '        emit ActionExecuted(actionHash, actionNonce, decisionId, viaOverride);'

run_sol_mutation "S25 vault: recover moves the whole balance while the event says amount" \
    "contracts/src/SentinelVault.sol" \
    '        (bool ok, bytes memory ret) = to.call{value: amount}("");' \
    '        (bool ok, bytes memory ret) = to.call{value: address(this).balance}("");'

# C11-C13 target the WIRING, which had none. Six of ten mutations against it survived a green
# suite because every test drove the fixture data or the pure guard and nothing drove the
# pipeline. `run.ts` is not covered by the suite at all, so C13 is caught by a STRUCTURAL
# assertion over its source rather than by behaviour — which is the honest way to pin a call
# site the tests cannot reach, and is stated as such in the test.

run_mutation "C11 rationale: skip the transcription equality check" \
    "src/corpus/rationale.ts" \
    "    if (
        transcribed.callData !== input.encodedCallData ||" \
    "    if (
        false ||"

run_mutation "C12 rationale: accept a proposal that did not transcribe" \
    "src/corpus/rationale.ts" \
    "    if (!transcribed.ok) {" \
    "    if (false) {"

run_mutation "C13 corpus: delete the one call site in the runner" \
    "src/corpus/run.ts" \
    "            verifyRationaleFixture({" \
    "            const _unused = ({"

echo "=== ${caught} caught, ${survived} survived, ${errored} did not apply, ${skipped} skipped ==="
