import {keccak256, toBytes} from "viem";
import type {ActionPayload, Hex} from "../signer/protocol.ts";
import type {VaultState} from "../signer/vault.ts";
import {ProposalError, encodeCall, parseSignature, parseTarget, parseValueWei} from "./encode.ts";
import type {AgentProposal} from "./schema.ts";

/**
 * The agent-proposal seam (§9 step 7).
 *
 * §3.2 step 5 is "the agent proposes an exact EVM call"; steps 6-10 are the pipeline that
 * already exists. This module is the join between them, and until now it was the one link
 * that had never been built — D-018 recorded that omission precisely so S1's "end-to-end"
 * could not be read as including it.
 *
 * WHAT AN AGENT ACTUALLY EMITS. The D-007 spike's `propose_evm_action` tool takes a target,
 * a native value, a function signature, arguments as strings, and a rationale. It does not
 * emit calldata. §3.1 classifies every one of those fields as untrusted — "agent-supplied
 * parameter or purpose claims" — so nothing here may assume any of them is well-formed,
 * sensible, or honest.
 *
 * D-019 (John, 2026-07-30) rules that Sentinel encodes the calldata from the agent's typed
 * arguments. Two consequences follow, and both are stated rather than left implicit:
 *
 *   1. The agent's PARAMETER claim and the executed bytes become one statement. Sentinel
 *      decoding those bytes back to the agent's claim is a round-trip through
 *      `encode.ts`, not independent corroboration. §4.2 Case 2 is amended to match.
 *   2. The agent's PURPOSE claim — `rationale` — stays untrusted and unread. It is carried
 *      alongside the action as provenance, never consulted by a check. This is where the
 *      Case 2 demonstration actually lives: the agent says "a required one-time setup
 *      before purchasing the weather-basic-24h feed" and Sentinel blocks on the decoded
 *      max-uint256 approval to an attacker, having never read the sentence.
 *
 * THIS MODULE RENDERS NO VERDICT. Same discipline as the decoder (A-017(c)). It transcribes
 * a proposal into bytes or refuses on well-formedness alone. It does not check the target
 * against a registry, does not care whether the selector is supported, and does not consult
 * the mandate — a proposal Sentinel cannot decode must still be BUILDABLE, or §3.3(8)'s
 * "unsupported calls, undecodable calldata" path is unreachable from an agent and the §7.1
 * fixture class that covers it can never be driven by one.
 */

// ---------------------------------------------------------------------------
// The untrusted input
// ---------------------------------------------------------------------------

/** A proposal transcribed into the exact call it denotes. */
export interface TranscribedProposal {
    target: Hex;
    valueWei: bigint;
    callData: Hex;
    selector: Hex;
    /** The signature the agent supplied, verbatim. The selector is keccak of these bytes. */
    signature: string;
    /**
     * The agent's account of what the call means. Untrusted, unread by every check, and
     * carried only so the evidence record can show what was claimed beside what was done.
     */
    rationale: string;
}

export type TranscribeResult =
    | {ok: true; proposal: TranscribedProposal}
    | {ok: false; code: string; detail: string};

/**
 * Transcribe an agent proposal into the exact call it denotes, or say why it cannot be.
 *
 * Returns a result rather than throwing, for the same reason `decodeCall` does: a proposal
 * that will not transcribe is a recordable fact about the agent under test, not an
 * exception to swallow.
 */
export function transcribe(proposal: AgentProposal): TranscribeResult {
    try {
        const target = parseTarget(proposal.target);
        const valueWei = parseValueWei(proposal.value_wei);
        // Parsed before encoding so a malformed signature is reported as such rather than
        // as an arity mismatch against a signature that never parsed.
        parseSignature(proposal.function_signature);
        const callData = encodeCall(proposal.function_signature, proposal.args);

        return {
            ok: true,
            proposal: {
                target,
                valueWei,
                callData,
                selector: callData.slice(0, 10) as Hex,
                signature: proposal.function_signature,
                rationale: proposal.rationale,
            },
        };
    } catch (err) {
        if (err instanceof ProposalError) return {ok: false, code: err.code, detail: err.message};
        throw err;
    }
}

// ---------------------------------------------------------------------------
// Binding to the chain
// ---------------------------------------------------------------------------

/**
 * Bind a transcribed proposal to the vault's current state, producing the §5.3 ActionPayload.
 *
 * Every field the agent does not control comes from the chain, never from the proposal:
 * the nonce, the active mandate hash, and the active policy hash are read from the vault,
 * so an agent cannot aim its action at a mandate that is not the live one. `dataHash` is
 * computed from the transcribed bytes here and recomputed by both the signer and the vault
 * (§5.3, §3.3(4)) — three independent computations of the binding that §3.3(5) says any
 * mutation must invalidate.
 *
 * `deadline` is the caller's: it is an operational parameter of the run, not a claim the
 * agent gets to make.
 */
export function bindAction(args: {
    proposal: TranscribedProposal;
    vault: Hex;
    chainId: bigint;
    vaultState: VaultState;
    deadline: bigint;
    /** §5.3 `operation`. Zero is CALL, the fail-closed default fixed in step 1. */
    operation?: bigint;
}): ActionPayload {
    return {
        schemaVersion: 1n,
        chainId: args.chainId,
        vault: args.vault,
        actionNonce: args.vaultState.actionNonce,
        target: args.proposal.target,
        valueWei: args.proposal.valueWei,
        dataHash: keccak256(toBytes(args.proposal.callData)),
        operation: args.operation ?? 0n,
        mandateHash: args.vaultState.activeMandateHash,
        policyHash: args.vaultState.activePolicyHash,
        deadline: args.deadline,
    };
}

export {
    PROPOSAL_FAILURES,
    ProposalError,
    encodeCall,
    parseSignature,
    parseTarget,
    parseValueWei,
    selectorFor,
} from "./encode.ts";
export type {ProposalFailureCode} from "./encode.ts";
export {readProposal} from "./schema.ts";
export type {AgentProposal} from "./schema.ts";
export {loadSpikeFixture, proposalsFrom} from "./fixtures.ts";
export type {SpikeFixture, SpikeArm} from "./fixtures.ts";
