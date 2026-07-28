import type {DecodeResult} from "../decode/index.ts";
import {describe as describeCall} from "../decode/index.ts";
import type {SimulationResult} from "../simulate/index.ts";
import type {Hex} from "../signer/protocol.ts";
import {canonicalize, type CanonicalValue} from "./jcs.ts";
import {hashUtf8} from "./hashes.ts";
import {
    failingCodes,
    runChecks,
    verdictOf,
    type CheckResult,
    type ConformanceInput,
    type Verdict,
} from "./checks.ts";

/**
 * The conformance evaluator and evidence bundle (§9 step 6).
 *
 * Produces the three things the isolated signer needs in order to attest: a verdict, the
 * reason codes behind it, and the canonical evidence bytes whose keccak256 the receipt
 * commits to. It does not sign, does not touch key material, and does not talk to the
 * signer — the caller carries its output across the process boundary.
 *
 * WHY THE BUNDLE RECORDS PASSES AS WELL AS FAILURES. §5.6's `policyChecks` is meant to
 * answer "what did Sentinel actually check?", and a record listing only failures cannot
 * distinguish a check that passed from one that never ran. That distinction is the whole
 * subject of §7.3's ablation, and it is what a sceptical reviewer at the five-minute
 * comprehension gate (D-008) will reach for first.
 *
 * WHY EVERY NUMBER IN THE BUNDLE IS A STRING. See `jcs.ts`: RFC 8785's number
 * serialisation is the one part of the scheme two implementations reliably disagree on, so
 * the schema has no JSON numbers and `canonicalize` throws if one appears. D-010's Python
 * verifier reproduces this hash from the published schema alone, and that is the feedback
 * D-010 was promoted into v1 to obtain while the schemas are still cheap to change.
 *
 * TRUST BOUNDARY, STATED BECAUSE IT IS THE POINT OF THE WHOLE HARNESS. This module decides
 * verdicts, so its own tests are the weakest possible evidence that those verdicts are
 * right — self-written tests encode the same misunderstanding twice. HANDOFF's verification
 * partition puts the bar outside: the independently labelled corpus of §9 step 8, authored
 * under D-011 by an agent with no implementation context, adversarially cross-checked, and
 * sampled by John at the gate. Until that exists, a green evaluator suite means the
 * mechanism runs, not that it is correct.
 */

export interface EvaluationResult {
    verdict: Verdict;
    reasonCodes: string[];
    checks: CheckResult[];
    /** The exact bytes whose keccak256 the receipt's `evidenceHash` commits to. */
    evidenceCanonical: string;
    evidenceHash: Hex;
    bundle: CanonicalValue;
}

export interface EvaluateArgs extends ConformanceInput {
    /** Optional §6 explanation layer. §7.4 permits removing it if it does not earn its cost. */
    aiExplanation?: string | null;
    /** §5.6 `citedContextReferences` — documentation the proposal cited. Context-only (§3.1). */
    citedContextReferences?: string[];
}

export function evaluate(args: EvaluateArgs): EvaluationResult {
    const checks = runChecks(args);
    const verdict = verdictOf(checks, args.policy);
    const bundle = buildEvidenceBundle(args, checks, verdict);
    const evidenceCanonical = canonicalize(bundle);

    return {
        verdict,
        reasonCodes: failingCodes(checks),
        checks,
        evidenceCanonical,
        evidenceHash: hashUtf8(evidenceCanonical),
        bundle,
    };
}

/**
 * §5.6's thirteen fields, all present.
 *
 * Every field is emitted even when empty, because "absent" and "empty" are different claims
 * and a verifier reading the bundle should not have to guess which one it is looking at.
 * `aiExplanation` and `citedContextReferences` are null/empty in v1 by default — §7.4 makes
 * the explanation layer optional and subject to removal if it does not earn its cost.
 */
function buildEvidenceBundle(
    args: EvaluateArgs,
    checks: CheckResult[],
    verdict: Verdict,
): CanonicalValue {
    const {mandate, policy, action, callData, decode, simulation, vaultState} = args;

    return {
        schema: "sentinel.evidence.v0.2",
        verdict,

        normalizedAction: {
            schemaVersion: action.schemaVersion.toString(),
            chainId: action.chainId.toString(),
            vault: action.vault,
            actionNonce: action.actionNonce.toString(),
            target: action.target,
            valueWei: action.valueWei.toString(),
            dataHash: action.dataHash,
            operation: action.operation.toString(),
            mandateHash: action.mandateHash,
            policyHash: action.policyHash,
            deadline: action.deadline.toString(),
            callData,
        },

        decodedSelectorAndParameters: decode.ok
            ? {
                  decoded: "true",
                  selector: decode.selector,
                  schema: decode.decoded.schema,
                  description: describeCall(decode.decoded),
                  parameters: decodedParameters(decode),
              }
            : {
                  decoded: "false",
                  selector: decode.selector ?? "",
                  failureCode: decode.code,
                  detail: decode.detail,
              },

        policyChecks: checks.map((c) => ({
            code: c.code,
            outcome: c.outcome,
            detail: c.detail,
        })),

        // What the mandate authorised, stated separately from what was observed so a reader
        // can compare the two without recomputing the mandate.
        expectedEffects: {
            maxNativeValueWei: minOf(mandate.maxNativeValueWei, policy.maxNativeValueWei).toString(),
            target: mandate.target,
            selector: mandate.selector,
            resourceId: mandate.resourceId,
            beneficiary: mandate.beneficiary,
            durationSeconds: mandate.durationSeconds.toString(),
            recurringAllowed: mandate.recurringAllowed,
            maxAllowanceIncreaseBaseUnits: policy.maxAllowanceIncreaseBaseUnits.toString(),
        },

        observedPreState: simulation === null ? null : preState(simulation),
        observedPostState: simulation === null ? null : postState(simulation),

        nativeBalanceDeltas:
            simulation === null
                ? []
                : simulation.nativeBalanceDeltas.map((d) => ({
                      address: d.address,
                      before: d.before.toString(),
                      after: d.after.toString(),
                      delta: d.delta.toString(),
                  })),

        allowanceDeltas:
            simulation === null
                ? []
                : simulation.allowanceDeltas.map((d) => ({
                      token: d.token,
                      owner: d.owner,
                      spender: d.spender,
                      before: d.before.toString(),
                      after: d.after.toString(),
                      delta: d.delta.toString(),
                  })),

        internalCallTrace:
            simulation === null
                ? []
                : simulation.internalCalls.map((c) => ({
                      from: c.from,
                      to: c.to ?? "",
                      type: c.type,
                  })),

        targetCodeIdentity: {
            target: action.target,
            pinnedByMandate: mandate.targetCodeHash,
            observedOnChain: vaultState.targetCodeHash,
            matches: mandate.targetCodeHash.toLowerCase() === vaultState.targetCodeHash.toLowerCase(),
        },

        // §3.1 classifies documentation as context-only: it may be cited, never relied on.
        citedContextReferences: args.citedContextReferences ?? [],

        unresolvedChecks: checks.filter((c) => c.outcome === "UNRESOLVED").map((c) => c.code),

        aiExplanation: args.aiExplanation ?? null,

        anchor:
            simulation === null
                ? null
                : {
                      blockNumber: simulation.anchor.blockNumber.toString(),
                      blockHash: simulation.anchor.blockHash,
                  },
    };
}

function decodedParameters(decode: Extract<DecodeResult, {ok: true}>): CanonicalValue {
    const d = decode.decoded;
    return d.schema === "DemoPay.purchase"
        ? {
              resourceId: d.resourceId,
              beneficiary: d.beneficiary,
              durationSeconds: d.durationSeconds.toString(),
              recurring: d.recurring,
          }
        : {spender: d.spender, amount: d.amount.toString()};
}

function preState(s: SimulationResult): CanonicalValue {
    return {
        nativeBalances: s.nativeBalanceDeltas.map((d) => ({
            address: d.address,
            wei: d.before.toString(),
        })),
        allowances: s.allowanceDeltas.map((d) => ({
            token: d.token,
            owner: d.owner,
            spender: d.spender,
            amount: d.before.toString(),
        })),
        entitlements: s.entitlements.map((e) => ({
            contract: e.contract,
            beneficiary: e.beneficiary,
            resourceId: e.resourceId,
            expiry: e.expiryBefore.toString(),
            recurring: e.recurringBefore,
        })),
    };
}

function postState(s: SimulationResult): CanonicalValue {
    return {
        outcome: s.outcome.status,
        revertReason: s.outcome.revertReason,
        gasUsed: s.gasUsed.toString(),
        nativeBalances: s.nativeBalanceDeltas.map((d) => ({
            address: d.address,
            wei: d.after.toString(),
        })),
        allowances: s.allowanceDeltas.map((d) => ({
            token: d.token,
            owner: d.owner,
            spender: d.spender,
            amount: d.after.toString(),
        })),
        entitlements: s.entitlements.map((e) => ({
            contract: e.contract,
            beneficiary: e.beneficiary,
            resourceId: e.resourceId,
            expiry: e.expiryAfter.toString(),
            recurring: e.recurringAfter,
        })),
        // §5.7: supporting evidence only — an event is never proof of entitlement.
        events: s.events.map((e) => ({address: e.address, topics: e.topics, data: e.data})),
    };
}

function minOf(a: bigint, b: bigint): bigint {
    return a < b ? a : b;
}

export {canonicalize} from "./jcs.ts";
export type {CanonicalValue} from "./jcs.ts";
export {runChecks, verdictOf, failingCodes, EVAL_CODES} from "./checks.ts";
export type {CheckResult, CheckOutcome, Verdict, ConformanceInput, EvalCode} from "./checks.ts";
